# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os
from typing import Dict, List, Any, Tuple, Callable, cast

import dask
import dask.dataframe as dd
import dask.delayed as ddelayed
import pandas as pd
from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.utilities import _get_ts_params_dict
from azureml.data import TabularDataset
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from joblib import Parallel, delayed, parallel_backend

from azureml.automl.runtime import _ml_engine as ml_engine, data_context
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.featurizer.transformer import TimeSeriesPipelineType, TimeSeriesTransformer
from azureml.automl.runtime.shared import memory_utilities
from azureml.automl.runtime.shared.lazy_azure_blob_cache_store import LazyAzureBlobCacheStore

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class DistributedFeaturizationPhase:
    """AutoML job phase that featurizes the data."""

    @staticmethod
    def run(workspace_getter: Callable[..., Any],
            experiment_name: str,
            parent_run_id: str,
            automl_settings: AzureAutoMLSettings,
            training_dataset: TabularDataset,
            validation_dataset: TabularDataset,
            parallel_backend_name: str = 'dask') -> None:

        _log_with_memory("Beginning distributed featurization")

        with logging_utilities.log_activity(logger=logger, activity_name='FindingUniqueCategories'):
            categories_by_grain_cols, categories_by_non_grain_cols = _get_categories_by_columns(
                training_dataset,
                automl_settings.grain_column_names)

        with logging_utilities.log_activity(logger=logger, activity_name='BuildTransformer'):
            ts_transformer = _build_transformer(training_dataset,
                                                automl_settings,
                                                categories_by_grain_cols,
                                                categories_by_non_grain_cols)

        featurized_data_dir = '{}_{}_featurized'.format(experiment_name, parent_run_id)
        with logging_utilities.log_activity(logger=logger, activity_name='DistributedTransformation'):
            with parallel_backend(parallel_backend_name):
                Parallel(n_jobs=-1)(delayed(_transform_one_grain)(
                    workspace_getter,
                    featurized_data_dir,
                    parent_run_id,
                    _get_dataset_for_grain(grain_key_value, training_dataset),
                    _get_dataset_for_grain(grain_key_value, validation_dataset),
                    grain_key_value,
                    ts_transformer,
                    automl_settings.label_column_name,
                    automl_settings.grain_column_names
                ) for grain_key_value in training_dataset.get_partition_key_values())

        expr_store = ExperimentStore.get_instance()
        expr_store.data.partitioned.save_train_dataset(
            workspace_getter(),
            featurized_data_dir + "_train",
            training_dataset.partition_keys
        )
        expr_store.data.partitioned.save_valid_dataset(
            workspace_getter(),
            featurized_data_dir + "_validation",
            training_dataset.partition_keys
        )
        _log_with_memory("Ending distributed featurization")


def _get_dataset_for_grain(grain_keys_values: Dict[str, Any],
                           partitioned_dataset: TabularDataset) -> TabularDataset:
    filter_condition = None
    for key, value in grain_keys_values.items():
        new_condition = partitioned_dataset[key] == value
        filter_condition = new_condition if filter_condition is None else filter_condition & new_condition
    return partitioned_dataset.filter(filter_condition)


# these are worker process global variables tp be used in _transform_one_grain function only
default_datastore_for_worker = None
workspace_for_worker = None
expr_store = None


def _transform_one_grain(workspace_getter: Callable[..., Any],
                         featurized_data_dir: str,
                         parent_run_id: str,
                         training_dataset_for_grain: TabularDataset,
                         validation_dataset_for_grain: TabularDataset,
                         grain_keys_values: Dict[str, Any],
                         ts_transformer: TimeSeriesTransformer,
                         label_column_name: str,
                         grain_column_names: List[Any]) -> None:
    global default_datastore_for_worker
    global workspace_for_worker
    global expr_store

    if default_datastore_for_worker is None:
        # Use one for lifetime of worker process instead of one per grain
        logger.info("creating workspace for the worker process")
        workspace_for_worker = workspace_getter()
        default_datastore_for_worker = workspace_for_worker.get_default_datastore()
        cache_store = LazyAzureBlobCacheStore(default_datastore_for_worker, parent_run_id)
        expr_store = ExperimentStore(cache_store, read_only=False)

    os.makedirs(featurized_data_dir, exist_ok=True)

    # load pandas dataframe for one grain
    train_X_grain = training_dataset_for_grain.to_pandas_dataframe()
    train_y_grain = train_X_grain.pop(label_column_name).values
    validation_X_grain = validation_dataset_for_grain.to_pandas_dataframe()
    validation_y_grain = validation_X_grain.pop(label_column_name).values

    # transform one grain
    train_transformed_data = ts_transformer.fit_transform(train_X_grain, train_y_grain)
    validation_transformed_data = ts_transformer.transform(validation_X_grain, validation_y_grain)

    for transformed_data, split in \
            zip([train_transformed_data, validation_transformed_data], ['train', 'validation']):
        # write one grain to local file
        # drop the grain columns since they will be part of the path and hence
        # they will be reconstructed as part of reading partitioned dataset
        transformed_data.reset_index(inplace=True)
        transformed_data.drop(columns=grain_column_names, inplace=True)
        grain_keys_values_str = '-'.join([str(v) for v in grain_keys_values.values()])
        featurized_file_name = '{}-{}.parquet'.format(split, grain_keys_values_str)
        featurized_file_path = '{}/{}'.format(featurized_data_dir, featurized_file_name)
        transformed_data.to_parquet(featurized_file_path)

        # construct the path to which data will be written to on the default blob store
        target_path_array = ['_'.join([featurized_data_dir, split])]
        for val in grain_keys_values.values():
            target_path_array.append(str(val))
        target_path = '/'.join(target_path_array)

        # upload data to default store
        expr_store.data.partitioned.write_file(featurized_file_path, target_path)
        logger.info("transformed one grain and uploaded data")

    # upload fitted pipeline to default datastore
    expr_store.transformers.set_by_grain(grain_keys_values, ts_transformer)


def unique_by_partition_columns(partitioned_dataset: TabularDataset,
                                grain_col: str) -> List[Any]:
    categories_for_grain_col = set()
    for key_val in partitioned_dataset.get_partition_key_values():
        categories_for_grain_col.add(key_val[grain_col])
    unique_vals = list(categories_for_grain_col)
    logger.info("Calculated uniques for one grain column")
    return unique_vals


def _get_categories_by_columns(partitioned_dataset: TabularDataset,
                               grain_column_names: List[str]) -> Tuple[Dict[str, List[Any]], Dict[str, List[Any]]]:

    categories_by_grain_cols = {col: pd.Categorical(unique_by_partition_columns(partitioned_dataset,
                                                                                col)).categories
                                for col in grain_column_names}
    _log_with_memory("Calculated uniques for all grain columns")

    ddf = _to_partitioned_dask_dataframe(partitioned_dataset)
    ddf = ddf.drop(grain_column_names, axis=1)
    categorical_cols = ddf.select_dtypes(['object', 'category', 'bool']).columns

    uniques_delayed = [ddf[col].unique() for col in categorical_cols]
    uniques = dask.compute(*uniques_delayed)
    categories_by_non_grain_cols = {col: pd.Categorical(uniques).categories for col, uniques
                                    in zip(categorical_cols, uniques)}
    _log_with_memory("Calculated uniques for all non grain columns")

    return categories_by_grain_cols, categories_by_non_grain_cols


def _build_transformer(training_dataset: TabularDataset,
                       automl_settings: AzureAutoMLSettings,
                       categories_by_grain_cols: Dict[str, List[Any]],
                       categories_by_non_grain_cols: Dict[str, List[Any]]) -> TimeSeriesTransformer:
    dataset_for_grain = _get_dataset_for_grain(training_dataset.get_partition_key_values()[0], training_dataset)
    subsampled_X = dataset_for_grain.to_pandas_dataframe()
    subsampled_Y = subsampled_X.pop(automl_settings.label_column_name).values

    data_context_params = data_context.DataContextParams(automl_settings)

    pipeline_type = TimeSeriesPipelineType.FULL
    ts_params = cast(Dict[str, Any], data_context_params.control_params.timeseries_param_dict)
    featurization_config = data_context_params.control_params.featurization
    # Timeseries currently doesn't reject "off" as input and currently converts "auto"/"off" to the object
    # during the featurize_data_timeseries method. Since we bypass that call and call suggest directly, we
    # need to convert from string to object here.
    if isinstance(featurization_config, str):
        featurization_config = FeaturizationConfig()

    (
        forecasting_pipeline,
        timeseries_param_dict,
        lookback_removed,
        time_index_non_holiday_features
    ) = ml_engine.suggest_featurizers_timeseries(
        subsampled_X,
        subsampled_Y,
        featurization_config,
        ts_params,
        pipeline_type,
        categories_by_grain_cols,
        categories_by_non_grain_cols
    )

    ts_transformer = TimeSeriesTransformer(
        forecasting_pipeline,
        pipeline_type,
        featurization_config,
        time_index_non_holiday_features,
        lookback_removed,
        **timeseries_param_dict
    )

    _log_with_memory("Suggest featurization invoked and transformer pipeline is ready to be fit")
    return ts_transformer


def _to_partitioned_dask_dataframe(partitioned_dataset: TabularDataset) -> dd:
    datasets_for_all_grains = [_get_dataset_for_grain(kv, partitioned_dataset)
                               for kv in partitioned_dataset.get_partition_key_values()]
    delayed_functions = [ddelayed(dataset_for_grain.to_pandas_dataframe)()
                         for dataset_for_grain in datasets_for_all_grains]
    ddf = dd.from_delayed(delayed_functions)
    return ddf


def _log_with_memory(info: str) -> None:
    logger.info(info)
    avail_memory = memory_utilities.get_available_physical_memory() / (1024 * 1024 * 1024)
    all_memory = memory_utilities.get_all_ram() / (1024 * 1024 * 1024)
    percentage_available = avail_memory * 100 / all_memory
    logger.info("Memory usage info:  "
                "   RAM = {}GB  "
                "   Available RAM = {}GB    "
                "   Percentage RAM Available = {}".format(all_memory, avail_memory, percentage_available))
