# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for storing experiment data, metadata, and transformers. See ExperimentStore for details."""
from typing import cast, Any, Dict, List, MutableMapping, Optional, Union
from abc import abstractmethod, ABC
import logging
import pickle

from azureml._common._error_definition import AzureMLError
from azureml.core import Dataset, Workspace

from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternalLogSafe
)
from azureml.automl.runtime.shared._cv_splits import FeaturizedCVSplit
from azureml.automl.runtime.featurizer.transformer import TimeSeriesTransformer


_READ_ONLY_ERROR_MESSAGE = "Unable to set attributes on read only store."
_CV_NOT_FOUND_MESSAGE = "CV split '{}' not found."

logger = logging.getLogger(__name__)


class _CacheableStoreABC(ABC):
    """The abstract object for a cacheable object in an ExperimentStore."""
    @abstractmethod
    def _load(self):
        ...

    @abstractmethod
    def _unload(self):
        ...


class _CacheableStoreBase(_CacheableStoreABC):
    """The base object for any part of an ExperimentStore."""

    def __init__(self, cache, read_only):
        self._cache = cache
        self._read_only = read_only

    def __getstate__(self):
        state = self.__dict__.copy()
        # These entries should always be set on the ExperimentStore.
        del state["_cache"]
        del state["_read_only"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class _CVSplitsCollection(MutableMapping[Union[str, int], FeaturizedCVSplit]):
    """
    Object for storing featurized CV splits.

    This object is only be used by ExperimentData.

    This object handles custom read/writes to a mutable mapping allowing
    for caching without need to load/unload by users. All key/value pairs
    are stored in the Cache. A read from the collection results in a two
    cache look ups - 1 to check if the key is in the dictionary, 1 to
    retrieve the value. A write to the collection results in 1 read and
    2 writes - the first read is required to update the keys in the dictionary,
    while the 2 writes handle the added key and value.
    """
    split_keys = "split_keys"

    def __init__(self, cache, read_only):
        self._cache = cache
        self._read_only = read_only

    def __getitem__(self, key):
        if key in self._cache.get([self.split_keys])[self.split_keys]:
            return self._cache.get([key])[key]
        else:
            raise ClientException._with_error(AzureMLError.create(
                AutoMLInternalLogSafe, target="get_cv_split",
                error_message=_CV_NOT_FOUND_MESSAGE.format(key),
                error_details=_CV_NOT_FOUND_MESSAGE.format(key))
            )

    def __setitem__(self, key, value):
        if self._read_only:
            raise ClientException._with_error(AzureMLError.create(
                AutoMLInternalLogSafe, target="set_cv_split",
                error_message=_READ_ONLY_ERROR_MESSAGE,
                error_details=_READ_ONLY_ERROR_MESSAGE)
            )
        else:
            # Only check split keys from cache if we know the split_keys are
            # in the cache. If the split_keys key is not yet cached, we know we
            # are on the first item in the list.
            if self.split_keys in self._cache.cache_items:
                splits = self._cache.get([self.split_keys])[self.split_keys]
            else:
                splits = []
            if key not in splits:
                splits.append(key)
                self._cache.set(self.split_keys, splits)
            self._cache.set(key, value)

    def __iter__(self):
        keys = self._cache.get([self.split_keys])[self.split_keys]
        self._cur_key = 0
        self._keys = keys
        return self

    def __next__(self):
        if self._keys and self._cur_key < len(self._keys):
            res = self._cache.get([self._keys[self._cur_key]])[self._keys[self._cur_key]]
            self._cur_key += 1
            return res
        else:
            raise StopIteration

    def __len__(self):
        keys = self._cache.get([self.split_keys])[self.split_keys]
        return len(keys) if keys else 0

    def __delitem__(self, item: Union[str, int]) -> None:
        if self._read_only:
            raise ClientException._with_error(AzureMLError.create(
                AutoMLInternalLogSafe, target="del_cv_split",
                error_message=_READ_ONLY_ERROR_MESSAGE,
                error_details=_READ_ONLY_ERROR_MESSAGE)
            )
        else:
            keys = self._cache.get([self.split_keys])[self.split_keys]
            if item in keys:
                keys.remove(item)
                self._cache.remove(item)
                self._cache.set(self.split_keys, keys)
            else:
                raise ClientException._with_error(AzureMLError.create(
                    AutoMLInternalLogSafe, target="del_cv_split",
                    error_message=_CV_NOT_FOUND_MESSAGE.format(item),
                    error_details=_CV_NOT_FOUND_MESSAGE.format(item))
                )


class ExperimentData(_CacheableStoreBase):
    """
    The object containing data for a given Experiment.

    This object should only be used by the ExperimentStore.

    Information stored in this object can be memory- or cache-backed.

    ExperimentData represents any data which may be used throughout a job. There are two types of
    data formats which can be accessed - materialized and lazy. Materialized data represents data
    which can be materialized entirely in memory. Materialized data is typically stored as a pandas
    dataframe. Lazy data represents data which is too large to fit into memory and must be streamed
    as it is used. Lazy data is typically stored as a TabularDataset. Materialized data will always
    be cache-backed data.
    """

    class MaterializedData(_CacheableStoreBase):
        """
        Object containing materialized data within the ExperimentStore.

        materialized data is any data which can be stored in memory
        (typically pandas dataframes or numpy arrays). As this data is
        always stored in memory, all attributes are cache-backed. If
        the ExperimentStore is loaded as read-only, writes to these attributes
        will raise an exception.

        Data stored here is stored in the form X, y, sample_weight.
        Available data groups are - train, valid, test, raw, cv_splits.

        CV splits are implemented through the _CVSplitsCollection object
        which is a cache-backed mutable mapping.
        """

        def __init__(self, cache, read_only):
            super().__init__(cache, read_only)
            self.cv_splits = _CVSplitsCollection(cache, read_only)

        def get_test(self):
            keys = ["X_test", "y_test", "sample_weight_test"]
            ret = self._cache.get(keys)
            return ret[keys[0]], ret[keys[1]], ret[keys[2]]

        def set_test(self, X, y, sample_weight):
            if self._read_only:
                raise ClientException._with_error(AzureMLError.create(
                    AutoMLInternalLogSafe, target="set_test",
                    error_message=_READ_ONLY_ERROR_MESSAGE,
                    error_details=_READ_ONLY_ERROR_MESSAGE)
                )
            else:
                self._cache.set("X_test", X)
                self._cache.set("y_test", y)
                self._cache.set("sample_weight_test", sample_weight)

        def get_train(self):
            keys = ["X", "y", "sample_weight"]
            ret = self._cache.get(keys)
            return ret[keys[0]], ret[keys[1]], ret[keys[2]]

        def set_train(self, X, y, sample_weight):
            if self._read_only:
                raise ClientException._with_error(AzureMLError.create(
                    AutoMLInternalLogSafe, target="set_train",
                    error_message=_READ_ONLY_ERROR_MESSAGE,
                    error_details=_READ_ONLY_ERROR_MESSAGE)
                )
            else:
                self._cache.set("X", X)
                self._cache.set("y", y)
                self._cache.set("sample_weight", sample_weight)

        def get_raw(self):
            keys = ["X_raw", "y_raw", "X_raw_valid", "y_raw_valid"]
            ret = self._cache.get(keys)
            return ret[keys[0]], ret[keys[1]], ret[keys[2]], ret[keys[3]]

        def set_raw(self, X, y, X_valid, y_valid):
            if self._read_only:
                raise ClientException._with_error(AzureMLError.create(
                    AutoMLInternalLogSafe, target="set_raw",
                    error_message=_READ_ONLY_ERROR_MESSAGE,
                    error_details=_READ_ONLY_ERROR_MESSAGE)
                )
            else:
                self._cache.set("X_raw", X)
                self._cache.set("y_raw", y)
                self._cache.set("X_raw_valid", X_valid)
                self._cache.set("y_raw_valid", y_valid)

        def get_valid(self):
            keys = ["X_valid", "y_valid", "sample_weight_valid"]
            ret = self._cache.get(keys)
            return ret[keys[0]], ret[keys[1]], ret[keys[2]]

        def set_valid(self, X, y, sample_weight):
            if self._read_only:
                raise ClientException._with_error(AzureMLError.create(
                    AutoMLInternalLogSafe, target="set_valid",
                    error_message=_READ_ONLY_ERROR_MESSAGE,
                    error_details=_READ_ONLY_ERROR_MESSAGE)
                )
            else:
                self._cache.set("X_valid", X)
                self._cache.set("y_valid", y)
                self._cache.set("sample_weight_valid", sample_weight)

        def get_CV_splits(self):
            for split in self.cv_splits:
                yield(split)

        def _load(self):
            pass

        def _unload(self):
            pass

    class LazyData(_CacheableStoreBase):
        """
        Object containing lazy data within the ExperimentStore.

        Lazy data is any data which need be loaded into memory prior to
        use (typically dataset objects). As this data is only materialized
        on demand, these attributes are all memory-backed.

        Data stored here is stored in the form Data, label_column_name,
        sample_weight_column_name. This object supports retrieval of data
        in the form X, y, sw and data, label_name, sw_name.
        """

        def __init__(self, cache, read_only):
            super().__init__(cache, read_only)
            self._training_dataset = None
            self._validation_dataset = None
            self._label_column_name = ""
            self._weight_column_name = None

        def get_training_dataset(self):
            """
            Get the training dataset.

            Returns the data in the from dataset, label column name, sample weight column name.
            """
            return self._training_dataset, self._label_column_name, self._weight_column_name

        def set_training_dataset(self, dataset, label_column_name, weight_column_name):
            """
            Set the training data.

            Sets the values for training dataset, label column name, and optionally weight column name.
            :param dataset: The TabularDataset to be stored.
            :param label_column_name: The label column name from the dataset.
            :param weight_column_name: If present, the name of the sample weight column from the dataset.
            """
            if self._read_only:
                raise ClientException._with_error(AzureMLError.create(
                    AutoMLInternalLogSafe, target="set_training_dataset",
                    error_message=_READ_ONLY_ERROR_MESSAGE,
                    error_details=_READ_ONLY_ERROR_MESSAGE)
                )
            else:
                self._training_dataset = dataset
                self._label_column_name = label_column_name
                if weight_column_name:
                    self._weight_column_name = weight_column_name

        def _get_X_train(self):
            columns_to_drop = []
            if self._label_column_name is not None:
                columns_to_drop.append(self._label_column_name)
            if self._weight_column_name is not None:
                columns_to_drop.append(self._weight_column_name)

            if self._training_dataset is not None:
                return self._training_dataset.drop_columns(columns_to_drop)
            else:
                return None

        def _get_y_train(self):
            if self._label_column_name and self._training_dataset is not None:
                return self._training_dataset.keep_columns([self._label_column_name])
            else:
                return None

        def _get_sw_train(self):
            if self._weight_column_name and self._training_dataset is not None:
                return self._training_dataset.keep_columns([self._weight_column_name])
            else:
                return None

        def _get_X_valid(self):
            columns_to_drop = []
            if self._label_column_name is not None:
                columns_to_drop.append(self._label_column_name)
            if self._weight_column_name is not None:
                columns_to_drop.append(self._weight_column_name)

            if self._validation_dataset is not None:
                return self._validation_dataset.drop_columns(columns_to_drop)
            else:
                return None

        def _get_y_valid(self):
            if self._label_column_name and self._validation_dataset is not None:
                return self._validation_dataset.keep_columns([self._label_column_name])
            else:
                return None

        def _get_sw_valid(self):
            if self._weight_column_name and self._validation_dataset is not None:
                return self._validation_dataset.keep_columns([self._weight_column_name])
            else:
                return None

        def get_train(self):
            """
            Get the training data.

            Returns the training data in the form X, y, sw.
            """
            return self._get_X_train(), self._get_y_train(), self._get_sw_train()

        def get_valid(self):
            """
            Get the validation data.

            Returns the validation data in the for X_valid, y_valid, sw_valid.
            """
            return self._get_X_valid(), self._get_y_valid(), self._get_sw_valid()

        def get_raw(self):
            """
            Get the raw data.

            Returns the raw data for training and validation (if applicable, else returns None).
            """
            return self._get_X_train(), self._get_y_train(), self._get_X_valid(), self._get_y_valid()

        def get_validation_dataset(self):
            """
            Get the validation dataset.

            Returns the validation dataset along with the label and sample weight column names
            """
            return self._training_dataset, self._label_column_name, self._weight_column_name

        def set_validation_dataset(self, dataset):
            """
            Set the validation dataset.

            Assumes the same label column name and sample weight column name from training
            set also also present in validation dataset.
            """
            if self._read_only:
                raise ClientException._with_error(AzureMLError.create(
                    AutoMLInternalLogSafe, target="set_validation_dataset",
                    error_message=_READ_ONLY_ERROR_MESSAGE,
                    error_details=_READ_ONLY_ERROR_MESSAGE)
                )
            else:
                self._validation_dataset = dataset

        def _load(self):
            cache = self._cache
            read_only = self._read_only
            self.__dict__ = pickle.loads(self._cache.get(["ExperimentData_lazy"])["ExperimentData_lazy"]).__dict__
            self._cache = cache
            self._read_only = read_only

        def _unload(self):
            self._cache.set("ExperimentData_lazy", pickle.dumps(self))

    class FeaturizedPartitionData(_CacheableStoreBase):

        def __init__(self, cache, read_only):
            super().__init__(cache, read_only)
            self._train_dataset_id = None
            self._valid_dataset_id = None

        def write_file(self, src, dest):
            dest = "data/" + dest
            self._cache.upload_file(src, dest)

        def save_train_dataset(self, workspace, path_to_dataset, partition_keys):
            self._train_dataset_id = self._save_dataset(workspace, path_to_dataset, partition_keys)

        def save_valid_dataset(self, workspace, path_to_dataset, partition_keys):
            self._valid_dataset_id = self._save_dataset(workspace, path_to_dataset, partition_keys)

        def _save_dataset(self, workspace: Workspace, path_to_dataset: str, partition_keys: List[str]) -> str:
            partition_string = ""
            for key in partition_keys:
                partition_string += "{"
                partition_string += str(key)
                partition_string += "}/"

            partition_string += "*.parquet"

            path_to_dataset = "data/" + path_to_dataset
            dataset = Dataset.Tabular.from_parquet_files(
                path=(self._cache._data_store, path_to_dataset),
                partition_format=partition_string
            )
            return cast(str, dataset._ensure_saved(workspace))

        @property
        def train_dataset_id(self) -> Optional[str]:
            return self._train_dataset_id

        @property
        def valid_dataset_id(self) -> Optional[str]:
            return self._valid_dataset_id

        def _load(self):
            cache = self._cache
            read_only = self._read_only
            self.__dict__ = pickle.loads(
                self._cache.get(["ExperimentData_partitioned"])["ExperimentData_partitioned"]
            ).__dict__
            self._cache = cache
            self._read_only = read_only

        def _unload(self):
            self._cache.set("ExperimentData_partitioned", pickle.dumps(self))

    def __init__(self, cache, read_only):
        super().__init__(cache, read_only)
        self.materialized = self.MaterializedData(cache, read_only)
        self.lazy = self.LazyData(cache, read_only)
        self.cv_splits = _CVSplitsCollection(cache, read_only)
        self.partitioned = self.FeaturizedPartitionData(cache, read_only)

    def _load(self):
        # Materialized data is loaded on access
        self.lazy._load()
        self.partitioned._load()

    def _unload(self):
        # Materialized data is unloaded on access
        self.lazy._unload()
        self.partitioned._unload()


class ExperimentMetadata(_CacheableStoreBase):
    """
    The object containing metadata for a given Experiment.

    This object should only be used by the ExperimentStore.

    Any information stored in this object will be memory-backed and should
    be unloaded (saved) to the CacheStore prior to usage in subsequent runs
    or subprocesses.

    ExperimentMetadata represents any metadata used throughout a job. ExperimentMetadata is split between
    common metadata attributes used across jobs - things like task, is_sparse, data_snapshot, etc. - and
    things specific to a given job. Specific attributes are stored under their prospective tasks:
    Classification, Regression, and Timeseries. If something is not a generic piece of metadata used across
    tasks it should be put in the correct task's metadata.
    """

    class _ClassificationMetadata():
        """Metadata related to classification tasks."""

        def __init__(self):
            self.num_classes = None
            self.class_labels = None

    class _RegressionMetadata():
        """Metadata related to regression tasks."""

        def __init__(self):
            self.bin_info = {}
            self.y_min = None
            self.y_max = None
            self.y_std = None

        def get_y_range(self):
            return self.y_min, self.y_max

    class _TimeseriesMetadata():
        """Metadata related to timeseries tasks."""

        def __init__(self):
            self.timeseries_param_dict = {}

    def __init__(self, cache, read_only):
        super().__init__(cache, read_only)
        self.is_sparse = False
        self.nimbus = None
        self.num_samples = None
        self.problem_info = None
        self.raw_data_snapshot_str = ""
        self.output_snapshot_str = ""
        self.raw_data_type = None
        self.task = ""
        self.training_type = ""
        self.X_raw_column_names = None
        self._timeseries = self._TimeseriesMetadata()
        self._regression = self._RegressionMetadata()
        self._classification = self._ClassificationMetadata()

    @property
    def is_timeseries(self) -> bool:
        """
        Get the older version of automl timeseries.

        Previously AutoML only supported classification/regression tasks. When
        forecasting was added, the task was converted to regression and is_timeseries
        was set to `True`. This property is added to support the old workflows where
        task is expected to be only Classification/Regression and is_timeseries is needed.
        In new workflows, task_type should be used.
        """
        return self.task == constants.Tasks.FORECASTING

    @property
    def task_type(self) -> str:
        """
        Get the older version of automl tasks.

        Previously AutoML only supported classification/regression tasks. When
        forecasting was added, the task was converted to regression and is_timeseries
        was set to `True`. This property is added to support the old workflows where
        task is expected to be only Classification/Regression. In new workflows,
        task_type should be used.
        """
        if self.task == constants.Tasks.FORECASTING:
            return constants.Tasks.REGRESSION
        else:
            return self.task

    @property
    def classification(self) -> _ClassificationMetadata:
        return self._classification

    @property
    def regression(self) -> _RegressionMetadata:
        return self._regression

    @property
    def timeseries(self) -> _TimeseriesMetadata:
        return self._timeseries

    def _load(self):
        cache = self._cache
        read_only = self._read_only
        self.__dict__ = pickle.loads(self._cache.get(["ExperimentMetadata"])["ExperimentMetadata"]).__dict__
        self._cache = cache
        self._read_only = read_only

    def _unload(self):
        self._cache.set("ExperimentMetadata", pickle.dumps(self))


class ExperimentTansformers(_CacheableStoreBase):
    """
    The object containing transformers for a given Experiment.

    This object should only be used by the ExperimentStore.

    Any information stored in this object will be memory-backed and should
    be unloaded (saved) to the CacheStore prior to usage in subsequent runs
    or subprocesses.
    """

    def __init__(self, cache, read_only):
        super().__init__(cache, read_only)
        self._transformers = {}  # type: Dict[str, Any]
        self._nimbus_preprocessor = None

    def set_nimbus_preprocessor(self, pipeline):
        if self._read_only:
            raise ClientException._with_error(AzureMLError.create(
                AutoMLInternalLogSafe, target="set_nimbus_preprocessor",
                error_message=_READ_ONLY_ERROR_MESSAGE,
                error_details=_READ_ONLY_ERROR_MESSAGE)
            )
        else:
            self._nimbus_preprocessor = pipeline

    def get_nimbus_preprocessor(self):
        """Return the preprocessor for this dataset, if any."""
        return self._nimbus_preprocessor

    def get_nimbus_preprocessor_pipeline_step(self):
        # The input dataset (X and y) are already transformed in this class
        if self._nimbus_preprocessor is None:
            return None

        # This is Nimbus specific, and kinda weird to have in this file. This should be refactored out
        # to a more Nimbus specific place. Long term, DatasetTransformer shouldn't be used, once Dataflow's
        # map_partition() function is usable, this class should just be out of the business for handling
        # preprocessed pipelines

        # The training data in case of NimbusML will *not* be a featurized Dataflow, instead, we use the
        # pre-fitted transformation pipeline computed in the setup phase and tack that onto the learner.
        # DatasetTransformer is the glue that takes in a fitted transformation pipeline and passes the
        # transformed dataflow to the (NimbusML) learner
        from nimbusml.preprocessing import DatasetTransformer
        return ('DatasetTransformer',
                DatasetTransformer(transform_model=self._nimbus_preprocessor.pipeline.model))

    def set_transformers(self, transformers):
        if self._read_only:
            raise ClientException._with_error(AzureMLError.create(
                AutoMLInternalLogSafe, target="set_transformers",
                error_message=_READ_ONLY_ERROR_MESSAGE,
                error_details=_READ_ONLY_ERROR_MESSAGE)
            )
        else:
            self._transformers = transformers

    def get_transformers(self):
        return self._transformers

    def get_by_grain(self, grain_dict: Dict[Any, Any]) -> TimeSeriesTransformer:
        """Get the timeseries transformer by grain."""
        grain_str = self._convert_grain_dict_to_str(grain_dict)
        transformer = self._cache.get([grain_str])[grain_str]
        return cast(TimeSeriesTransformer, transformer)

    def set_by_grain(self, grain_dict: Dict[Any, Any], pipeline: TimeSeriesTransformer) -> None:
        """
        Set the transformer for a given grain.

        This method stores the given pipeline into the cache store, ensuring it is
        available for subsequent jobs via cache backed access.
        """
        grain_str = self._convert_grain_dict_to_str(grain_dict)
        self._cache.set(grain_str, pipeline)

    def _convert_grain_dict_to_str(self, grain_dict: Dict[Any, Any]) -> str:
        """
        Convert dictionary of grains to string.

        Dictionary of the form {key1: value1, key2: value2} will be converted to string
        key1_value1_key2_value2. Additionally string will always be returns in sorted order.
        """
        return "_".join("{}_{}".format(k, v) for k, v in sorted(grain_dict.items(), key=lambda x: str(x[0])))

    def get_timeseries_transformer(self):
        return self._transformers.get(constants.Transformers.TIMESERIES_TRANSFORMER)

    def get_y_transformer(self):
        return self._transformers.get(constants.Transformers.Y_TRANSFORMER)

    def _load(self):
        cache = self._cache
        read_only = self._read_only
        self.__dict__ = pickle.loads(self._cache.get(["ExperimentTransformers"])["ExperimentTransformers"]).__dict__
        self._cache = cache
        self._read_only = read_only

    def _unload(self):
        self._cache.set("ExperimentTransformers", pickle.dumps(self))


class ExperimentStore:
    """
    The place to store data, metadata, transformers, and other information necessary
    complete a task within AutoML.

    This object replaces the ClientDatasets object. The purpose of this object is to
    store any information which is necessary across the set of tasks within AutoML.
    Example jobs currently supported include: AutoML Featurize, Train, Explain, & Test.
    This object should never do any work related to creating, modifying, or splitting
    data/metadata, it acts simply as a place to store and marshall information between
    runs.

    This object is represented as a singleton object instantiated once at the entrypoint of
    of a run and retrieved at use time. Attempts to recreate the singleton, or to retrieve the
    singleton prior to initial creation will both result in exceptions. The data is marshalled
    across runs or processes via the CacheStore. The ExperimentStore can unload (write) data
    to the underlying cache or load (read) data from the cache depending on the requirements
    of the run. Additionally, a read-only flag is included to ensure the ExperimentStore is
    only written to when the entrypoint expects such writes.

    Attributes within the ExperimentStore have two modes of storage - memory-backed and cached-backed.
    Attributes which are typically large, things like training data or cv-splits, are stored as
    cache-backed attributes. All other attributes, like transformers and metadata, are memory-backed.
    Reading from or writing to cache-backed attributes will result in a read or write to the underlying
    cache store. Reading from or writing to memory-backed attributes results in a read or write to the
    in memory object. The only way to ensure memory-backed attributes are persisted accross runs or processes
    is to unload (write) and load (read) the ExperimentStore to the cache. Once a run is finished, it should
    always reset its ExperimentStore state to ensure no undesired elements of a previous job persist within
    a future job in the same environment. This reset is done via ExperimentStore.reset().

    .. code-block:: python

        # Create a read/write ExperimentStore
        expr_store = ExperimentStore(cache, read_only=False)

        # Retreive an ExperimentStore
        expr_store = ExperimentStore.get_instance()

        # Write the ExperimentStore to the cache
        expr_store.unload()

        # Create a read-only ExperimentStore and load the information from the cache
        exp = ExperimentStore(cache, read_only=True)
        expr_store.load()

        # Retrieve and ExperimentStore
        expr_store = ExperimentStore.get_instance()

    The ExperimentStore has three major components for compartmentalizing data - ExperimentData,
    ExperimentMetadata, and ExperimentTransformers. These attributes provide access to their
    respective data components: data, metadata, transformers.

    ExperimentData represents any data which may be used throughout a job. There are two types of
    data formats which can be accessed - materialized and lazy. Materialized data represents data
    which can be materialized entirely in memory. Materialized data is typically stored as a pandas
    dataframe. Lazy data represents data which is too large to fit into memory and must be streamed
    as it is used. Lazy data is typically stored as a TabularDataset. Materialized data will always
    be cache-backed data.

    ExperimentMetadata represents any metadata used throughout a job. ExperimentMetadata is split between
    common metadata attributes used across jobs - things like task, is_sparse, data_snapshot, etc. - and
    things specific to a given job. Specific attributes are stored under their prospective tasks:
    Classification, Regression, and Timeseries. If something is not a generic piece of metadata used across
    tasks it should be put in the correct task's metadata. All ExperimentMetadata is memory-backed.

    ExperimentTransformers represents any transformers used to featurize data during an AutoML job.
    ExperimentTransformers is memory-backed.
    """

    __instance = None

    def __init__(self, cache, read_only):
        logger.info("Requested a new ExperimentStore instance.")
        if ExperimentStore.__instance:
            raise ClientException._with_error(AzureMLError.create(
                AutoMLInternalLogSafe, target="ExperimentStore.__init__",
                error_message="ExperimentStore singleton has already been created.",
                error_details="ExperimentStore singleton has already been created.")
            )
        else:
            self._data = ExperimentData(cache, read_only)
            self._metadata = ExperimentMetadata(cache, read_only)
            self._transformers = ExperimentTansformers(cache, read_only)
            self._read_only = read_only
            ExperimentStore.__instance = self
        logger.info("Created ExperimentStore with ID: {}.".format(id(self)))

    @staticmethod
    def get_instance() -> "ExperimentStore":
        if not ExperimentStore.__instance:
            raise ClientException._with_error(AzureMLError.create(
                AutoMLInternalLogSafe, target="ExperimentStore.get_instance",
                error_message="ExperimentStore singleton has not been created.",
                error_details="ExperimentStore singleton has not been created.")
            )
        return ExperimentStore.__instance

    @classmethod
    def reset(cls) -> None:
        logger.info("Resetting ExpeirmentStore ID: {}".format(id(cls.__instance)))
        cls.__instance = None

    @property
    def data(self) -> ExperimentData:
        return self._data

    @data.setter
    def data(self, data):
        raise ClientException._with_error(AzureMLError.create(
            AutoMLInternalLogSafe, target="ExperimentStore.set_data",
            error_message="Setting data is not supported.",
            error_details="Setting data is not supported.")
        )

    @property
    def metadata(self) -> ExperimentMetadata:
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        raise ClientException._with_error(AzureMLError.create(
            AutoMLInternalLogSafe, target="ExperimentStore.set_metadata",
            error_message="Setting metadata is not supported.",
            error_details="Setting metadata is not supported.")
        )

    @property
    def transformers(self) -> ExperimentTansformers:
        return self._transformers

    @transformers.setter
    def transformers(self, transformers):
        raise ClientException._with_error(AzureMLError.create(
            AutoMLInternalLogSafe, target="ExperimentStore.set_transformers",
            error_message="Setting transformers is not supported.",
            error_details="Setting transformers is not supported.")
        )

    def load(self) -> None:
        """Load the ExperimentStore state from cache."""
        self._data._cache.load()
        self._data._load()
        self._metadata._load()
        self._transformers._load()

    def unload(self) -> None:
        """Unload the ExperimentStore state to cache."""
        if self._read_only:
            raise ClientException._with_error(AzureMLError.create(
                AutoMLInternalLogSafe, target="ExperimentStore.unload",
                error_message=_READ_ONLY_ERROR_MESSAGE,
                error_details=_READ_ONLY_ERROR_MESSAGE)
            )
        else:
            self._data._unload()
            self._metadata._unload()
            self._transformers._unload()

    def clear(self) -> bool:
        """
        Clear experiment data from cache store.

        This method will delete any underlying cached data. Once deleted,
        it cannot be recovered.

        If call was successful returns True, otherwise False.
        """
        try:
            self._data._cache.unload()
            return True
        except IOError:
            return False
