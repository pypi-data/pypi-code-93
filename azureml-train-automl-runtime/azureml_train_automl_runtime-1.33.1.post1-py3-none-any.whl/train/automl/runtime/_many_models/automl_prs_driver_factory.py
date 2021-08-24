# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, cast, Dict, Optional
from logging import Logger

from azureml.core import Run
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.train.automl.runtime._many_models.train_helper import Arguments
from azureml.train.automl.runtime._many_models.automl_prs_driver_base import AutoMLPRSDriverBase
from azureml.train.automl.runtime._many_models.many_models_automl_train_driver import ManyModelsAutoMLTrainDriver
from azureml.train.automl.runtime._many_models.many_models_inference_driver import ManyModelsInferenceDriver
from azureml.train.automl.runtime._hts.hts_automl_train_driver import HTSAutoMLTrainDriver
from azureml.train.automl.runtime._hts.hts_data_aggregation_driver import HTSDataAggregationDriver
from azureml.train.automl.runtime._hts.hts_forecast_parallel_driver import HTSForecastParallelDriver


class AutoMLPRSDriverFactory:
    HTS_AUTOML_TRAIN = "HTSAutoMLTrain"
    HTS_DATA_AGGREGATION = "HTSDataAggregation"
    HTS_FORECAST_PARALLEL = "ForecastParallel"
    MANY_MODELS_AUTOML_TRAIN = "ManyModelsAutoMLTrain"
    MANY_MODELS_INFERENCE = "ManyModelsInference"

    @staticmethod
    def get_automl_prs_driver(
            scenario: str,
            current_step_run: Run,
            logger: Logger,
            args: Arguments,
            automl_settings: Optional[Dict[str, Any]] = None,
    ) -> AutoMLPRSDriverBase:
        """
        Get AutoML PRS driver code based on scenario.

        :param scenario: The PRS run scenario.
        :param current_step_run: The current PRS run.
        :param logger: The logger.
        :param args: The args used in the PRS run.
        :param automl_settings: The automl settings dict.
        :return: An AutoMLPRSDriverBase that used in PRS step.
        """
        driver = None  # type: Optional[AutoMLPRSDriverBase]
        if scenario == AutoMLPRSDriverFactory.MANY_MODELS_AUTOML_TRAIN:
            driver = ManyModelsAutoMLTrainDriver(
                current_step_run, cast(Dict[str, Any], automl_settings), args
            )
        elif scenario == AutoMLPRSDriverFactory.MANY_MODELS_INFERENCE:
            driver = ManyModelsInferenceDriver(
                current_step_run, args
            )
        elif scenario == AutoMLPRSDriverFactory.HTS_DATA_AGGREGATION:
            driver = HTSDataAggregationDriver(
                current_step_run, args, cast(Dict[str, Any], automl_settings)
            )
        elif scenario == AutoMLPRSDriverFactory.HTS_FORECAST_PARALLEL:
            driver = HTSForecastParallelDriver(
                current_step_run, args
            )
        elif scenario == AutoMLPRSDriverFactory.HTS_AUTOML_TRAIN:
            driver = HTSAutoMLTrainDriver(
                current_step_run, cast(Dict[str, Any], automl_settings), args
            )

        Contract.assert_type(
            driver, "AutoMLPRSDriver",
            expected_types=(
                ManyModelsAutoMLTrainDriver, ManyModelsInferenceDriver, HTSDataAggregationDriver,
                HTSForecastParallelDriver, HTSAutoMLTrainDriver
            ),
            reference_code=ReferenceCodes._MANY_MODELS_WRONG_DRIVER_TYPE
        )
        driver = cast(AutoMLPRSDriverBase, driver)

        return driver
