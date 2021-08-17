# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Runs all enabled features sweepers."""
from typing import Any, cast, Dict, List, Optional, Tuple
from functools import reduce
import logging

import numpy as np
import os
import pickle
import scipy
import tempfile

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ConflictingValueForArguments
from sklearn.base import BaseEstimator
from sklearn.pipeline import make_pipeline, Pipeline

from azureml.automl.core.shared import activity_logger, logging_utilities
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.runtime.shared import resource_limits
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType
from azureml.automl.core.constants import TextNeuralNetworks, SweepingMode, TextDNNLanguages
from azureml.automl.core.configuration import FeatureConfig, SweeperConfig, ConfigKeys
from azureml.automl.core.configuration.sampler_config import SamplerConfig
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.runtime.estimation import Estimators
from ..featurization import Featurizers
from ..sampling import Samplers, AbstractSampler, \
    DataProvider, DiskBasedDataProvider, InMemoryDataProvider
from ..scoring import Scorers, AbstractScorer
from ..sweeping.abstract_sweeper import AbstractSweeper
from ..sweeping.sweepers import Sweepers
from ..stats_computation import RawFeatureStats
from ..featurizer.transformer import WordEmbeddingsInfo


logger = logging.getLogger(__name__)


class MetaSweeper:
    """Runs all enabled features sweepers."""

    DEFAULT_SWEEPER_TIMEOUT_SEC = 3600  # 1 hour

    def __init__(self,
                 task: str,
                 timeout_sec: int = DEFAULT_SWEEPER_TIMEOUT_SEC,
                 featurization_config: Optional[FeaturizationConfig] = None,
                 is_cross_validation: bool = False,
                 enable_dnn: bool = False,
                 force_text_dnn: bool = False,
                 feature_sweeping_config: Dict[str, Any] = {}) -> None:
        """Load configuration and create sweeper configurations.

        :param task: Task type- Classification, Regression or Forecasting.
        :param timeout_sec: Timeout in seconds for feature sweeping.
        :param is_cross_validation: Whether to do the cross validation.
        :param feature_sweeping_config: Feature sweeping config.
        :param enable_dnn: Flag to enable sweeping over text DNNs such as BERT, BiLSTM.
        :param force_text_dnn: Flag to force add text DNNs such as BERT, BiLSTM after sweeping.
        """
        self._task = task
        self._cfg = feature_sweeping_config  # type: Dict[str,Any]

        self._enabled = self._cfg.get(ConfigKeys.SWEEPING_ENABLED, False)
        self._sweepers = []  # type: List[AbstractSweeper]
        self._enabled_sweeper_configs = []  # type: List[SweeperConfig]
        self._is_cross_validation = is_cross_validation
        self._enable_dnn = enable_dnn and not self._is_cross_validation  # DNNs do not support cross-validation
        self._featurization_config = featurization_config
        self._class_balancing = self._cfg.get(ConfigKeys.ENABLE_CLASS_BALANCING, False)
        self._enabled_balancer_configs = []  # type: List[SweeperConfig]
        self._force_text_dnn = force_text_dnn

        # Select default language for text dnns or use langauge specified in featurization config
        if self._featurization_config is None or self._featurization_config.dataset_language is None:
            self._dataset_language = TextDNNLanguages.default
        else:
            self._dataset_language = self._featurization_config.dataset_language

        # Set sweeping configs with user specified params like enable_dnn and featurization_config
        self._set_feature_sweeping_configs()
        self._set_class_balancing_sweeper_configs()

        self._timeout_sec = timeout_sec
        self._temp_files_to_cleanup = []  # type: List[str]
        self._page_sampled_data_to_disk = self._cfg.get(ConfigKeys.PAGE_SAMPLED_DATA_TO_DISK, True)
        self._run_sweeping_in_isolation = self._cfg.get(ConfigKeys.RUN_SWEEPING_IN_ISOLATION, True)

    def _set_feature_sweeping_configs(self):
        """ Create and set feature sweeper configs objects and join with user settings to decide what sweepers
            are enabled, and in some cases what parameters they have such as
            enable_dnn or force_text_dnn."""

        # Text dnn logic based on enable_dnn, force_text_dnn, and dataset_language.
        if self._enabled:
            sweeper_configs = [{}] if self._cfg is None \
                else self._cfg.get(ConfigKeys.ENABLED_SWEEPERS, [])  # type: List[Dict[str, Any]]
            self._sweeper_name_list = []  # type: List[str]
            for sweeper_config in sweeper_configs:
                sweeper_name = sweeper_config["name"]
                honor_enable_dnn_flag = sweeper_name not in TextNeuralNetworks.ALL or self._enable_dnn
                if honor_enable_dnn_flag:
                    honor_force_dnn_flag = sweeper_name in TextNeuralNetworks.ALL and self._force_text_dnn
                    if honor_force_dnn_flag:
                        # Force text dnn's to be added in the sweeper.
                        sweeper_config["experiment_result_override"] = True
                    enabled_sweeper_config = SweeperConfig.from_dict(sweeper_config)
                    if sweeper_name == TextNeuralNetworks.BERT:
                        # Change the BERT model according to the given language
                        for featurizer in enabled_sweeper_config._experiment["featurizers"]:
                            if featurizer["id"] == "pretrained_text_dnn":
                                featurizer["kwargs"]["dataset_language"] = self._dataset_language
                    self._enabled_sweeper_configs.append(enabled_sweeper_config)

                    self._sweeper_name_list.append(sweeper_name)

            # Non-unique sweeper._name's can break how we loop over sweepers in _sweep_internal()
            duplicate_sweepers = set([x for x in self._sweeper_name_list if self._sweeper_name_list.count(x) > 1])
            if duplicate_sweepers:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ConflictingValueForArguments, target="_sweeper_name_list",
                        arguments='_sweeper_name_list ({})'.format(", ".join(duplicate_sweepers))
                    )
                )

    def _set_class_balancing_sweeper_configs(self):
        """ Create and set class balancing sweeper config objects"""

        # Class balancing logic
        if self._class_balancing:
            balancer_configs = [{}] if self._cfg is None \
                else self._cfg.get(ConfigKeys.ENABLED_BALANCERS, [])  # type: List[Dict[str, Any]]
            self._balancer_name_list = []  # type: List[str]
            for balancer_config in balancer_configs:
                balancer_name = balancer_config["name"]
                if balancer_name not in self._balancer_name_list:  # dedupe balancer
                    self._enabled_balancer_configs.append(SweeperConfig.from_dict(balancer_config))
                    self._balancer_name_list.append(balancer_name)

    # TODO: Balancing sweeping and the normal sweeping return completely different data structures. Refactor!
    def sweep(self,
              working_dir: str,
              X: DataInputType,
              y: DataSingleColumnInputType,
              stats_and_column_purposes: Optional[List[Tuple[RawFeatureStats, str, str]]] = None,
              sweeping_mode: str = SweepingMode.Feature) -> List[Any]:
        """Feature sweeping and / or class balancing sweeping"""

        if sweeping_mode == SweepingMode.Feature:
            return self._sweep_feature(working_dir, X, y, stats_and_column_purposes)

        if sweeping_mode == SweepingMode.Balancing:
            return self._sweep_balancing(working_dir, X, y)

        return []

    def _sweep_balancing(self, working_dir: str, X: DataInputType, y: DataSingleColumnInputType) -> List[Any]:
        """Sweep through all class balancers in the configuration."""

        if self._class_balancing is False:
            logger.info("Class balancing sweeping disabled")

        sweepers = self._build_sweepers(working_dir, X, y, sweeper_configs=self._enabled_balancer_configs,
                                        sweeping_mode=SweepingMode.Balancing)
        is_valid, msg = self._validate(X, y)
        if not is_valid:
            logger.info(msg)
            return []

        kwargs = {"sweepers": sweepers}  # type: Dict[str, Any]

        exit_status = None
        result = None  # type: Optional[List[Any]]
        try:
            if self._run_sweeping_in_isolation is False:
                return MetaSweeper._sweep_balancing_internal(**kwargs)

            constraints = resource_limits.DEFAULT_RESOURCE_LIMITS
            constraints[resource_limits.TIME_CONSTRAINT] = self._timeout_sec
            limiter = resource_limits.SafeEnforceLimits(enable_limiting=True, **constraints)
            result, exit_status, _ = limiter.execute(working_dir,
                                                     MetaSweeper._sweep_balancing_internal,
                                                     sweepers)

        except Exception:
            logger.warning("Balancing sweeping sub-process failed")

        return cast(List[Any], result)

    def _sweep_feature(self,
                       working_dir: str,
                       X: DataInputType,
                       y: DataSingleColumnInputType,
                       stats_and_column_purposes: Optional[List[Tuple[RawFeatureStats, str, str]]]) \
            -> List[Tuple[str, Pipeline]]:
        """Sweep through all the sweepers in the configurations."""

        if self._enabled is False:
            logger.debug("Feature sweeping disabled.")
            return []

        sweepers = self._build_sweepers(working_dir, X, y, sweeper_configs=self._enabled_sweeper_configs,
                                        sweeping_mode=SweepingMode.Feature)
        column_groups = {}  # type: Dict[str, List[str]]
        is_valid, msg = self._validate(X, y)
        if not is_valid:
            logger.info(msg)
            return []

        if stats_and_column_purposes is not None:
            for _, column_purpose, column in stats_and_column_purposes:
                column_groups.setdefault(column_purpose.lower(), []).append(column)

        file_handle, checkpoint_file = tempfile.mkstemp(suffix=".ck", prefix="feature_sweep_", dir=working_dir)
        self._temp_files_to_cleanup.append(checkpoint_file)
        # after creating the file, mkstemp holds a lock on it, preventing us from removing it after we're done
        # so we'll close that handle right after creation
        os.close(file_handle)

        exit_status = None
        result = None  # type: Optional[List[Tuple[Any, Pipeline]]]
        try:
            # TODO: Can we use enable_limiting=False for this case?
            if self._run_sweeping_in_isolation is False:
                return MetaSweeper._sweep_internal(sweepers,
                                                   self._enabled_sweeper_configs,
                                                   checkpoint_file,
                                                   X,
                                                   y,
                                                   column_groups)

            constraints = resource_limits.DEFAULT_RESOURCE_LIMITS
            constraints[resource_limits.TIME_CONSTRAINT] = self._timeout_sec
            limiter = resource_limits.SafeEnforceLimits(enable_limiting=True, **constraints)
            result, exit_status, _ = limiter.execute(working_dir,
                                                     MetaSweeper._sweep_internal,
                                                     sweepers,
                                                     self._enabled_sweeper_configs,
                                                     checkpoint_file,
                                                     X,
                                                     y,
                                                     column_groups)

            # the subprocess can silently fail, in which case fallback to recovering from checkpoint file
            if result is None:
                # This will always be a BaseException. Cast is required since combining Union and Tuple doesn't work
                exit_status = cast(BaseException, exit_status)
                logger.warning("Feature sweeping silently failed. ExitStatus: {}".format(exit_status))
                logging_utilities.log_traceback(exit_status, logger, is_critical=False)
                result = self._recover_sweeping_from_checkpointfile(checkpoint_file)
        except Exception as ex:
            logger.warning("Feature sweeping sub-process failed.")
            logging_utilities.log_traceback(ex, logger, is_critical=False)
            result = self._recover_sweeping_from_checkpointfile(checkpoint_file)
        finally:
            self._remove_temporary_files()

        return cast(List[Tuple[str, Any]], result)

    def _recover_sweeping_from_checkpointfile(self, checkpoint_file: str) -> List[Tuple[Any, Pipeline]]:
        # let's try to open the checkpoint file and recover as much as possible from there.
        result = []
        logger.info("Recovering sweeping metadata from checkpoint file")
        try:
            with open(checkpoint_file, 'rb') as ck_file:
                for row in ck_file:
                    sweeper_idx, columns = pickle.loads(row)
                    sweeper_config = self._enabled_sweeper_configs[int(sweeper_idx)]

                    result.append((columns,  # Handle group of columns case.
                                   self._build_featurizers(sweeper_config._experiment)))
            recovered_sweeps_count = len(result)
            if recovered_sweeps_count > 0:
                logger.debug(
                    "Recovered {} sweeping metadata items from checkpoint file.".format(recovered_sweeps_count))
        except Exception:
            pass

        return result

    @staticmethod
    def _sweep_balancing_internal(sweepers: List[AbstractSweeper]) -> List[Any]:
        return_strategies = []  # type: List[Any]

        logger.info("Begin Balancing Sweeping...")

        for sweeper_idx, sweeper in enumerate(sweepers):

            if sweeper.sweep():
                logger.debug("Sweep returned true for: {sweeper}".format(sweeper=sweeper))
                return_strategies.append(sweeper._name)
            else:
                logger.debug(
                    "Sweep returned false for: {sweeper} ".format(sweeper=sweeper))

        logger.info("Finished sweeping with all balancing sweepers.")
        return return_strategies

    @staticmethod
    def _sweep_internal(sweepers: List[AbstractSweeper],
                        enabled_sweeper_configs: List[SweeperConfig],
                        checkpoint_file: str,
                        X: DataInputType,
                        y: DataSingleColumnInputType,
                        column_groups: Dict[str, List[str]]) -> List[Tuple[str, Pipeline]]:
        return_transforms = []  # type: List[Tuple[Any, Any]]

        logger.info("Begin Feature Sweeping...")

        with open(checkpoint_file, mode='wb', buffering=1) as ck_file:
            for sweeper_idx, sweeper in enumerate(sweepers):
                # Get sweeper config by name in case of misalignment between sweeper_configs and sweepers
                sweeper_config = next((x for x in enabled_sweeper_configs if x._name == sweeper._name), None)
                if sweeper_config is None:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            ArgumentBlankOrEmpty, target="sweeper_config",
                            argument_name="sweeper_config ({})".format(sweeper._name)
                        )
                    )
                cols = []  # type: List[str]
                for purpose in sweeper_config._column_purposes:
                    group = purpose.get("group", False)
                    for t in purpose.get("types", []):
                        cols.extend(column_groups.get(t.lower(), []))

                if len(cols) == 0:
                    logger.info("No columns eligible for sweeping, continuing with next sweeper.")
                    continue

                if not group:
                    for col_id, column in enumerate(cols):
                        if sweeper.sweep(column):
                            logger.debug("Sweep returned true for: {sweeper} on column index: {col}".format(
                                sweeper=sweeper, col=col_id))

                            # persist our progress so far in case this child process dies out of a sudden
                            ck_file.write(pickle.dumps((sweeper_idx, column)))
                            return_transforms.append((column, sweeper._experiment))
                        else:
                            logger.debug(
                                "Sweep returned false for: {sweeper} "
                                "on col id: {col}".format(sweeper=sweeper, col=col_id))
                else:
                    featurize_separately = False
                    if group == 'score':
                        featurize_separately = True
                    col_string = reduce(lambda a, b: str(a) + "," + str(b), cols)
                    if sweeper.sweep(cols, featurize_separately=featurize_separately):
                        logger.debug("Sweep returned true for: {sweeper} on column index: {col}".format(
                            sweeper=sweeper, col=col_string))
                        ck_file.write(pickle.dumps((sweeper_idx, col_string)))
                        if featurize_separately:
                            return_transforms.extend((col, sweeper._experiment) for col in cols)
                        else:
                            return_transforms.append((cols, sweeper._experiment))
                    else:
                        logger.debug(
                            "Sweep returned false for: {sweeper} "
                            "for col ids: {col}".format(sweeper=sweeper, col=col_string))

        logger.info("Finished sweeping with all feature sweepers.")
        return return_transforms

    def _build_sweepers(self, working_dir: str, X: DataInputType, y: DataSingleColumnInputType,
                        sweeper_configs: Optional[List[SweeperConfig]] = None,
                        sweeping_mode: str = SweepingMode.Feature) -> List[AbstractSweeper]:
        """Sweep over all enabled sweepers."""
        if not sweeper_configs:
            return []

        logger.debug("Sweeper configuration: {c}".format(c=sweeper_configs))
        sweepers = []
        enabled_sweeper_configs = [cfg for cfg in sweeper_configs if cfg._enabled]
        for enabled_sweeper_config in enabled_sweeper_configs:
            # Build sampler
            sampler = self._build_sampler(
                SamplerConfig.from_dict(enabled_sweeper_config._sampler), task=self._task)
            # Build estimator
            estimator = Estimators.get(enabled_sweeper_config._estimator)  # type: Optional[BaseEstimator]
            # build scorer
            scorer = Scorers.get(
                enabled_sweeper_config._scorer,
                experiment_result_override=enabled_sweeper_config._experiment_result_override,
                task=self._task)  # type: Optional[AbstractScorer]

            # Build data provider
            data_provider = self._build_data_provider(X, y, sampler, working_dir)

            # Build baseline and experiment featurizers only for feature sweeping mode
            if sweeping_mode == SweepingMode.Feature:
                baseline_featurizer = self._build_featurizers(
                    enabled_sweeper_config._baseline,
                )  # type: FeatureConfig
                experiment_featurizer = self._build_featurizers(
                    enabled_sweeper_config._experiment,
                )  # type: FeatureConfig

                if baseline_featurizer is None or experiment_featurizer is None:
                    logger.debug("Excluding blocked transformer from sweeper")
                    continue

                include_baseline_features = True
                if enabled_sweeper_config._experiment:
                    include_baseline_features = enabled_sweeper_config._experiment. \
                        get(ConfigKeys.INCLUDE_BASELINE_FEATURES, True)

                kwargs = {"name": enabled_sweeper_config._name, "data_provider": data_provider, "estimator": estimator,
                          "scorer": scorer,
                          "baseline": baseline_featurizer, "experiment": experiment_featurizer,
                          "epsilon": enabled_sweeper_config._epsilon, "task": self._task,
                          "include_baseline_features_in_experiment": include_baseline_features}  # type: Dict[str, Any]
            else:
                kwargs = {"name": enabled_sweeper_config._name, "data_provider": data_provider, "estimator": estimator,
                          "scorer": scorer,
                          "epsilon": enabled_sweeper_config._epsilon, "task": self._task}

            sweeper = Sweepers.get(enabled_sweeper_config._type, **kwargs)  # type: Optional[AbstractSweeper]
            if sweeper:
                sweepers.append(sweeper)

        return sweepers

    def _remove_temporary_files(self) -> None:
        for file_name in self._temp_files_to_cleanup:
            try:
                os.remove(file_name)
            except IOError:
                pass

    @classmethod
    def _validate(cls, X: DataInputType, y: DataSingleColumnInputType) -> Tuple[bool, str]:
        if X is None or y is None:
            return False, "X or y cannot be None"

        if scipy.sparse.issparse(X):
            if X.shape[0] != len(y):
                return False, "Number of rows in X must be equal to the number of rows in y."
        elif len(X) != len(y):
            return False, "Number of rows in X must be equal to the number of rows in y."

        if len(np.unique(y)) == 1:
            return False, "Number of classes in y must be more than 1."

        return True, ''

    @classmethod
    def _build_sampler(cls, sampler_config: SamplerConfig, task: str) -> AbstractSampler:
        """
        Build sampler from the given sampler configuration.

        :param sampler_config: Sampler configuration.
        :param task: Task type.
        :return: Created sampler.
        """
        sampler_id = sampler_config.id
        sampler_args = sampler_config.sampler_args
        sampler_kwargs = sampler_config.sampler_kwargs
        sampler_kwargs["task"] = task

        sampler = Samplers.get(sampler_id, *sampler_args, **sampler_kwargs)
        return cast(AbstractSampler, sampler)

    def _build_featurizers(self, feature_config: Dict[str, Any]) -> Pipeline:
        feature_steps = feature_config.get(ConfigKeys.FEATURIZERS)
        if not isinstance(feature_steps, list):
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="feature_config",
                    argument_name="feature_config ({})".format(ConfigKeys.FEATURIZERS)
                )
            )
        steps = []

        for c in feature_steps:
            f_config = FeatureConfig.from_dict(c)
            featurizer = Featurizers.get(f_config, self._featurization_config)
            if featurizer is None:
                logger.debug("Excluding featurizer step with transformer: {0}.".format(f_config.id))
                return
            steps.append(featurizer)

        return make_pipeline(*steps)

    def _build_data_provider(self, X: DataInputType, y: DataSingleColumnInputType,
                             sampler: AbstractSampler, working_dir: str) -> DataProvider:
        # sample the data before creating the sweeper
        X_sampled, y_sampled, splitting_config = sampler.sample(X, y)
        data_provider = None  # type: Optional[DataProvider]
        if self._page_sampled_data_to_disk:
            file_handle, dataset_file = tempfile.mkstemp(suffix=".ds", prefix="sampled_dataset_", dir=working_dir)
            self._temp_files_to_cleanup.append(dataset_file)

            with os.fdopen(file_handle, "wb") as f:
                pickle.dump((X_sampled, y_sampled), f)

            data_provider = DiskBasedDataProvider(dataset_file, splitting_config)
        else:
            data_provider = InMemoryDataProvider(X_sampled, y_sampled, splitting_config)

        return data_provider
