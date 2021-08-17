# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The set of helper functions for data frames."""
from typing import Any, List, Optional, cast

import gc

import numpy as np
import pandas as pd

from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime._data_definition.raw_experiment_data import RawExperimentData
from azureml.automl.runtime._ml_engine.validation import common_data_validations
from azureml.automl.runtime.column_purpose_detection._time_series_column_helper import convert_check_grain_value_types
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime import short_grain_padding
from azureml.automl.runtime.featurizer.transformer.timeseries._validation import (
    TimeseriesAutoParamValidationWorker,
    TimeseriesColumnNameValidationWorker,
    TimeseriesCVValidationWorker,
    TimeseriesDataFrameValidationWorker,
    TimeseriesFrequencyValidationWorker,
    TimeseriesInputValidationWorker,
    TimeseriesParametersValidationWorker,
    TimeseriesValidationParameter,
    TimeseriesValidationParamName,
    TimeseriesValidationWorkerBase,
    TimeseriesValidator,
)
from azureml.automl.runtime.featurizer.transformer.timeseries._validation._timeseries_validation_common \
    import check_memory_limit
from azureml.automl.runtime.frequency_fixer import fix_data_set_regularity_may_be
from azureml.automl.runtime.shared.types import DataInputType


def validate_timeseries_training_data(
    automl_settings: AutoMLBaseSettings,
    X: DataInputType,
    y: DataInputType,
    X_valid: Optional[DataInputType] = None,
    y_valid: Optional[DataInputType] = None,
    sample_weight: Optional[np.ndarray] = None,
    sample_weight_valid: Optional[np.ndarray] = None,
    cv_splits_indices: Optional[List[List[Any]]] = None,
    x_raw_column_names: Optional[np.ndarray] = None,
) -> None:
    """
    Quick check of the timeseries input values, no tsdf is required here.

    :param automl_settings: automl settings
    :param X: Training data.
    :param y: target/label data.
    :param X_valid: Validation data.
    :param y_valid: Validation target/label data.
    :param sample_weight: Sample weights for the training set.
    :param sample_weight_valid: Sample weights for the validation set.
    :param cv_splits_indices: Indices for the cross validation.
    :param x_raw_column_names: The column names for the features in train and valid set.
    """
    ts_val_param = TimeseriesValidationParameter(
        automl_settings=automl_settings,
        X=X,
        y=y,
        X_valid=X_valid,
        y_valid=y_valid,
        sample_weight=sample_weight,
        sample_weight_valid=sample_weight_valid,
        cv_splits_indices=cv_splits_indices,
        x_raw_column_names=x_raw_column_names,
    )
    validation_workers = [
        TimeseriesParametersValidationWorker(),
        TimeseriesFrequencyValidationWorker(),
        TimeseriesColumnNameValidationWorker(),
        TimeseriesCVValidationWorker(),
        TimeseriesInputValidationWorker(
            x_param_name=TimeseriesValidationParamName.X, y_param_name=TimeseriesValidationParamName.Y
        ),
        TimeseriesInputValidationWorker(
            x_param_name=TimeseriesValidationParamName.X_VALID, y_param_name=TimeseriesValidationParamName.Y_VALID
        ),
        TimeseriesAutoParamValidationWorker(),
        TimeseriesDataFrameValidationWorker(),
    ]  # type: List[TimeseriesValidationWorkerBase]

    ts_validator = TimeseriesValidator(validation_workers=validation_workers)
    ts_validator.validate(param=ts_val_param)


def _add_freq_fixer_guard_rails(verifier: Optional[VerifierManager],
                                failed: bool, corrected: bool,
                                automl_settings: AutoMLBaseSettings) -> None:
    """
    Add the correct guard rail to the verifier.

    :param verifier: The verifier to be used to write guard rails to.
    :param failed: True if frequency fixer has failed.
    :param corrected: True if the dimensions of the data frame was corrected.
    :param automl_settings: The automl_settings used to run frequency fixer.
    :param effective_freq_str: The forecasting frequency used.
    """
    if verifier is None:
        return
    if automl_settings.target_aggregation_function is None or automl_settings.freq is None:
        verifier.update_data_verifier_frequency_inference(failed, corrected)
    elif not failed:
        # Aggregation does not fail, so in this case we ignore this value.
        verifier.update_data_verifier_aggregation(
            corrected,
            automl_settings.target_aggregation_function,
            automl_settings.freq)


def preprocess_timeseries_data(
        raw_experiment_data: RawExperimentData,
        automl_settings_obj: AutoMLBaseSettings,
        is_remote: bool,
        verifier: Optional[VerifierManager] = None) -> RawExperimentData:
    """
    Preprocess timeseries data and apply rule based validation.

    :param raw_experiment_data: The data to be analyzed and preprocessed.
    :param automl_settings_obj: The AutoML settings.
    :param is_remote: True if it is a remote run.
    :param verifier: The VerifierManager object used to output the guard rails.
    :return: The same RawExperimentData with modified data.
    """
    # We should not check dimensions on remote and non
    # forecasting runs because of streaming scenario.
    if not is_remote or automl_settings_obj.is_timeseries:
        common_data_validations.check_dimensions(
            X=raw_experiment_data.X,
            y=raw_experiment_data.y,
            X_valid=raw_experiment_data.X_valid,
            y_valid=raw_experiment_data.y_valid,
            sample_weight=raw_experiment_data.weights,
            sample_weight_valid=raw_experiment_data.weights_valid
        )
    if automl_settings_obj.is_timeseries:
        # Reconstruct the pandas data frames if possible.
        if not isinstance(raw_experiment_data.X, pd.DataFrame) and \
                raw_experiment_data.feature_column_names is not None:
            raw_experiment_data.X = pd.DataFrame(
                raw_experiment_data.X, columns=raw_experiment_data.feature_column_names
            )
        if raw_experiment_data.X_valid is not None and not isinstance(raw_experiment_data.X_valid, pd.DataFrame) \
                and raw_experiment_data.feature_column_names is not None:
            raw_experiment_data.X_valid = pd.DataFrame(
                raw_experiment_data.X_valid, columns=raw_experiment_data.feature_column_names
            )
        # Check that each grain column contains exactly one data type.
        raw_experiment_data.X, raw_experiment_data.X_valid = convert_check_grain_value_types(
            raw_experiment_data.X, raw_experiment_data.X_valid, automl_settings_obj.grain_column_names,
            automl_settings_obj.featurization,
            ReferenceCodes._TS_VALIDATION_GRAIN_TYPE_REMOTE if
            is_remote else ReferenceCodes._TS_VALIDATION_GRAIN_TYPE_LOCAL)

        # When data were read try to fix the frequency.
        if raw_experiment_data.X_valid is None:
            X = raw_experiment_data.X
            if isinstance(X, np.ndarray) and raw_experiment_data.feature_column_names is not None:
                X = pd.DataFrame(X, columns=raw_experiment_data.feature_column_names)
            y = raw_experiment_data.y
            fixed_freq_obj = fix_data_set_regularity_may_be(
                X,
                y,
                automl_settings_obj,
                ReferenceCodes._REMOTE_SCRIPT_WRONG_FREQ
                if is_remote else ReferenceCodes._TRAINING_UTILITIES_CHECK_FREQ_FIX)
            X = fixed_freq_obj.data_x
            raw_experiment_data.y = cast(np.ndarray, fixed_freq_obj.data_y)
            failed = fixed_freq_obj.is_failed
            corrected = fixed_freq_obj.is_modified
            freq = fixed_freq_obj.freq
            # Do our best to clean up memory.
            raw_experiment_data.X = None
            gc.collect()
            # If we do not have enough memory, raise the exception.
            check_memory_limit(X, raw_experiment_data.y)
            # Pad the short grains if needed (the short_series_handing_config_value is
            # checked by pad_short_grains_or_raise).
            X, raw_experiment_data.y = short_grain_padding.pad_short_grains_or_raise(
                X, raw_experiment_data.y, freq, automl_settings_obj,
                ReferenceCodes._TS_ONE_VALUE_PER_GRAIN_RSCRIPT if
                is_remote else ReferenceCodes._TS_ONE_VALUE_PER_GRAIN_TSUTIL,
                verifier)
            # We may have reordered data frame X remember the new column order.
            raw_experiment_data.feature_column_names = X.columns.values
            # and then copy the data to new location.
            raw_experiment_data.X = X
            if verifier:
                _add_freq_fixer_guard_rails(
                    verifier, failed, corrected,
                    automl_settings_obj)
    return raw_experiment_data
