import importlib
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Text, Optional, Any, List, Dict, Tuple, NamedTuple, Union

import convo.core
import convo.core.training.training
from convo.shared.exceptions import ConvoExceptions 
import convo.shared.utils.common
import convo.shared.utils.io
import convo.utils.io
from convo.constants import MIN_COMPATIBLE_VER
from convo.shared.constants import (
    RULES_DOCUMENTS_URL,
    POLICIES_DOCUMENTS_URL ,
    MIGRATION_GUIDE_DOCUMENTS_URL,
    DEFAULT_CONFIGURATION_PATH,
)
from convo.shared.core.constants import (
    BACK_USER_INTENT  ,
    RESTART_USER_INTENT  ,
    LISTEN_ACTION_NAME  ,
    RESTART_ACTION_NAME  ,
    BACK_ACTION_NAME   ,
)
from convo.shared.core.domain import InvalidDomain, Domain
from convo.shared.core.events import ActExecutionRejected
from convo.core.exceptions import UnsupportedCommunicationModelError
from convo.core.featurizers.tracker_featurizers import MaxHistoryTrackerFeaturizer
from convo.shared.nlu.interpreter import NaturalLangInterpreter, RegexInterpreter
from convo.core.policies.policy import Policy, SupportedDataSet
from convo.core.policies.fallback import PolicyFallback
from convo.core.policies.memoization import MemoizationPolicy, AugmentedMemoizationPolicy
from convo.core.policies.rule_policy import RulePolicy
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.core.generator import TrackerInCachedStates
from convo.core import registry

log = logging.getLogger(__name__)


class EnsemblePolicy:
    versioning_pack = ["convo", "tensorflow", "sklearn"]

    def __init__(
        self,
        policies: List[Policy],
        action_fingerprints: Optional[Dict[Any, Dict[Text, List]]] = None,
    ) -> None:
        self.policies = policies
        self.date_trained = None

        self.action_fingerprints = action_fingerprints

        self._inspect_priority()
        self._inspect_for_important_policy()

    def _inspect_for_important_policy(self) -> None:
        from convo.core.policies.mapping_policy import MappingPolicy

        if not any(
            isinstance(policy, (MappingPolicy, RulePolicy)) for policy in self.policies
        ):
            log.info(
                f"MappingPolicy not included in policy ensemble. Default convo_intents "
                f"'{RESTART_USER_INTENT  } and {BACK_USER_INTENT  } will not trigger "
                f"actions '{RESTART_ACTION_NAME  }' and '{BACK_ACTION_NAME   }'."
            )

    @staticmethod
    def inspect_domain_combination_compatibility(
        ensemble: Optional["EnsemblePolicy"], domain: Optional[Domain]
    ) -> None:
        """Check for elements that only work with certain policy/domain combinations."""

        from convo.core.policies.mapping_policy import MappingPolicy
        from convo.core.policies.two_stage_fallback import TwoStageFallbackPolicy

        policy_needing_validation = [
            MappingPolicy,
            TwoStageFallbackPolicy,
            RulePolicy,
        ]
        for policy in policy_needing_validation:
            policy.validate_against_domain(ensemble, domain)

        _validate_policy_for_forms_available(domain, ensemble)

    def _inspect_priority(self) -> None:
        """Checks for duplicate policy priorities within EnsemblePolicy."""

        priority_dictionary = defaultdict(list)
        for p in self.policies:
            priority_dictionary[p.priority].append(type(p).__name__)

        for k, v in priority_dictionary.items():
            if len(v) > 1:
                convo.shared.utils.io.raising_warning(
                    f"Found policies {v} with same priority {k} "
                    f"in EnsemblePolicy. When personalizing "
                    f"priorities, be sure to give all policies "
                    f"different priorities.",
                    docs=POLICIES_DOCUMENTS_URL ,
                )

    def _policy_combinaion_include_policy_with_rules_support(self) -> bool:
        """Determine whether the policy ensemble contains at least one policy
        supporting rule-based data.

        Returns:
            Whether or not the policy ensemble contains at least one policy that
            supports rule-based data.
        """
        return any(
            policy.supported_data()
            in [SupportedDataSet.RULE_DATA_SET, SupportedDataSet.ML_AND_RULE_DATA]
            for policy in self.policies
        )

    @staticmethod
    def _training_trackers_include_rule_trackers(
        training_trackers: List[DialogueStateTracer],
    ) -> bool:
        """Determine whether there are rule-based training trackers.

        Args:
            training_trackers: Trackers to inspect.

        Returns:
            Whether or not any of the supplied training trackers contain rule-based
            data.
        """
        return any(tracker.is_rule_tracker for tracker in training_trackers)

    def _release_rule_policy_warning(
        self, training_trackers: List[DialogueStateTracer]
    ) -> None:
        """Emit `UserWarning`s about missing rule-based data."""
        check_rules_consuming_policy_available = (
            self._policy_combinaion_include_policy_with_rules_support()
        )
        training_trackers_hold_rule_trackers = self._training_trackers_include_rule_trackers(
            training_trackers
        )

        if (
            check_rules_consuming_policy_available
            and not training_trackers_hold_rule_trackers
        ):
            convo.shared.utils.io.raising_warning(
                f"Found a rule-based policy in your pipeline but "
                f"no rule-based training data. Please add rule-based "
                f"stories to your training data or "
                f"remove the rule-based policy (`{RulePolicy.__name__}`) from your "
                f"your pipeline.",
                docs=RULES_DOCUMENTS_URL,
            )
        elif (
            not check_rules_consuming_policy_available
            and training_trackers_hold_rule_trackers
        ):
            convo.shared.utils.io.raising_warning(
                f"Found rule-based training data but no policy supporting rule-based "
                f"data. Please add `{RulePolicy.__name__}` or another rule-supporting "
                f"policy to the `policies` section in `{DEFAULT_CONFIGURATION_PATH}`.",
                docs=RULES_DOCUMENTS_URL,
            )

    def train(
        self,
        training_trackers: List[TrackerInCachedStates],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> None:
        if training_trackers:
            self._release_rule_policy_warning(training_trackers)

            for policy in self.policies:
                trackers_to_train = SupportedDataSet.trackers_for_policy(
                    policy, training_trackers
                )
                policy.train(
                    trackers_to_train, domain, interpreter=interpreter, **kwargs
                )

            self.action_fingerprints = convo.core.training.training.generate_act_finger_prints(
                training_trackers, domain
            )
        else:
            log.info("Skipped training, because there are no training samples.")

        self.date_trained = datetime.now().strftime("%Y%m%d-%H%M%S")

    def probability_using_finest_policy(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> Tuple[List[float], Optional[Text]]:
        raise NotImplementedError

    def _maximum_histories(self) -> List[Optional[int]]:
        """Return max history."""

        maximum_histories = []
        for p in self.policies:
            if isinstance(p.featurizer, MaxHistoryTrackerFeaturizer):
                maximum_histories.append(p.featurizer.max_history)
            else:
                maximum_histories.append(None)
        return maximum_histories

    def _append_package_version_information(self, metadata: Dict[Text, Any]) -> None:
        """Adds version info for self.versioned_packages to metadata."""

        for package_name in self.versioning_pack:
            try:
                q = importlib.import_module(package_name)
                w = q.__version__  # pytype: disable=attribute-error
                metadata[package_name] = w
            except ImportError:
                pass

    def _persist_meta_data(self, path: Text) -> None:
        """Persists the domain specification to storage."""

        # make sure the directory we persist exists
        domain_specification_path = os.path.join(path, "metadata.json")
        convo.shared.utils.io.create_dir_from_file(domain_specification_path)

        fetch_policy_names = [
            convo.shared.utils.common.from_instance_module_path_flow(p) for p in self.policies
        ]

        meta_flow = {
            "action_fingerprints": self.action_fingerprints,
            "python": ".".join([str(s) for s in sys.version_info[:3]]),
            "max_histories": self._maximum_histories(),
            "ensemble_name": self.__module__ + "." + self.__class__.__name__,
            "policy_names": fetch_policy_names,
            "trained_at": self.date_trained,
        }

        self._append_package_version_information(meta_flow)

        convo.shared.utils.io.dump_object_as_json_to_file(domain_specification_path, meta_flow)

    def persist(self, path: Union[Text, Path]) -> None:
        """Persists the policy to storage."""

        self._persist_meta_data(path)

        for i, policy in enumerate(self.policies):
            dir_name = "policy_{}_{}".format(i, type(policy).__name__)
            policy_path = Path(path) / dir_name
            policy.persist(policy_path)

    @classmethod
    def load_meta_data(cls, path) -> Any:
        meta_data_path_flow = os.path.join(path, "metadata.json")
        metadata = json.loads(
            convo.shared.utils.io.read_file(os.path.abspath(meta_data_path_flow))
        )
        return metadata

    @staticmethod
    def makesure_model_compatibility(metadata, version_to_check=None) -> None:
        from packaging import version

        if version_to_check is None:
            version_to_check = MIN_COMPATIBLE_VER

        model_ver = metadata.get("convo", "0.0.0")
        if version.parse(model_ver) < version.parse(version_to_check):
            raise UnsupportedCommunicationModelError(
                "The model version is too old to be "
                "loaded by this Convo Core instance. "
                "Either retrain the model, or run with "
                "an older version. "
                "Model version: {} Instance version: {} "
                "Minimal compatible version: {}"
                "".format(model_ver, convo.__version__, version_to_check),
                model_ver,
            )

    @classmethod
    def _makesure_loaded_policy(cls, policy, policy_cls, policy_name: Text):
        if policy is None:
            raise Exception(f"Failed to load policy {policy_name}: load returned None")
        elif not isinstance(policy, policy_cls):
            raise Exception(
                "Failed to load policy {}: "
                "load returned object that is not instance of its own class"
                "".format(policy_name)
            )

    @classmethod
    def load(cls, path: Union[Text, Path]) -> "EnsemblePolicy":
        """Loads policy and domain specification from storage"""

        meta_data = cls.load_meta_data(path)
        cls.makesure_model_compatibility(meta_data)
        _policy = []
        for i, policy_name in enumerate(meta_data["policy_names"]):
            policy_class = registry.policy_from_module_path_flow(policy_name)
            directory_name = f"policy_{i}_{policy_class.__name__}"
            policy_path_flow = os.path.join(path, directory_name)
            policy_name = policy_class.load(policy_path_flow)
            cls._makesure_loaded_policy(policy_name, policy_class, policy_name)
            _policy.append(policy_name)
        ensemble_cls = convo.shared.utils.common.class_name_from_module_path(
            meta_data["ensemble_name"]
        )
        finger_prints = meta_data.get("action_fingerprints", {})
        combine = ensemble_cls(_policy, finger_prints)
        return combine

    @classmethod
    def from_dict(cls, policy_configuration: Dict[Text, Any]) -> List[Policy]:
        import copy

        _policy = policy_configuration.get("policies") or policy_configuration.get(
            "policy"
        )
        if _policy is None:
            raise InvalidPolicyConfiguration(
                "You didn't define any policies. "
                "Please define them under 'policies:' "
                "in your policy configuration file."
            )
        if len(_policy) == 0:
            raise InvalidPolicyConfiguration(
                "The policy configuration file has to include at least one policy."
            )

        _policy = copy.deepcopy(_policy)  # don't manipulate passed `Dict`
        all_policies_parsed = []

        for policy in _policy:
            if policy.get("featurizer"):
                featurizer_func, featurizer_config = cls.fetch_featurizer_from_dictionary(
                    policy
                )

                if featurizer_config.get("state_featurizer"):
                    (
                        state_featurizer_func,
                        state_featurizer_config,
                    ) = cls.fetch_state_featurizer_from_dictionary(featurizer_config)

                    # override featurizer's state_featurizer
                    # with real state_featurizer class
                    featurizer_config["state_featurizer"] = state_featurizer_func(
                        **state_featurizer_config
                    )

                # override policy's featurizer with real featurizer class
                policy["featurizer"] = featurizer_func(**featurizer_config)

            get_policy_names = policy.pop("name")
            try:
                construct_function = registry.policy_from_module_path_flow(get_policy_names)
                try:
                    policy_obj = construct_function(**policy)
                except TypeError as e:
                    raise Exception(f"Could not initialize {get_policy_names}. {e}")
                all_policies_parsed.append(policy_obj)
            except (ImportError, AttributeError):
                raise InvalidPolicyConfiguration(
                    f"Module for policy '{get_policy_names}' could not "
                    f"be loaded. Please make sure the "
                    f"name is a valid policy."
                )

        cls._check_if_rule_policy_used_with_rule_like_policy(all_policies_parsed)

        return all_policies_parsed

    @classmethod
    def fetch_featurizer_from_dictionary(cls, policy) -> Tuple[Any, Any]:
        # policy can have only 1 featurizer
        if len(policy["featurizer"]) > 1:
            raise InvalidPolicyConfiguration(
                f"Every policy can only have 1 featurizer "
                f"but '{policy.get('name')}' "
                f"uses {len(policy['featurizer'])} featurizers."
            )
        featurizer_configuration = policy["featurizer"][0]
        fetch_featurizer_name = featurizer_configuration.pop("name")
        featurizer_function = registry.featurizer_from_module_path_flow(fetch_featurizer_name)

        return featurizer_function, featurizer_configuration

    @classmethod
    def fetch_state_featurizer_from_dictionary(cls, featurizer_config) -> Tuple[Any, Any]:
        # featurizer can have only 1 state featurizer
        if len(featurizer_config["state_featurizer"]) > 1:
            raise InvalidPolicyConfiguration(
                f"Every featurizer can only have 1 state "
                f"featurizer but one of the featurizers uses "
                f"{len(featurizer_config['state_featurizer'])}."
            )
        state_featurizer_configuration = featurizer_config["state_featurizer"][0]
        state_featurizer_names = state_featurizer_configuration.pop("name")
        state_featurizer_function = registry.state_featurizer_from_module_path_flow(
            state_featurizer_names
        )

        return state_featurizer_function, state_featurizer_configuration

    @staticmethod
    def _check_if_rule_policy_used_with_rule_like_policy(
        policies: List[Policy],
    ) -> None:
        if not any(isinstance(policy, RulePolicy) for policy in policies):
            return

        from convo.core.policies.mapping_policy import MappingPolicy
        from convo.core.policies.form_policy import FormPolicy
        from convo.core.policies.two_stage_fallback import TwoStageFallbackPolicy

        policies_not_be_used_with_rule_policy = (
            MappingPolicy,
            FormPolicy,
            PolicyFallback,
            TwoStageFallbackPolicy,
        )

        if any(
            isinstance(policy, policies_not_be_used_with_rule_policy)
            for policy in policies
        ):
            convo.shared.utils.io.raising_warning(
                f"It is not recommended to use the '{RulePolicy.__name__}' with "
                f"others policies which implement rule-like "
                f"behavior. It is highly recommended to migrate all deprecated "
                f"policies to use the '{RulePolicy.__name__}'. Note that the "
                f"'{RulePolicy.__name__}' will supersede the predictions of the "
                f"deprecated policies if the confidence levels of the predictions are "
                f"equal.",
                docs=MIGRATION_GUIDE_DOCUMENTS_URL,
            )


class Forecast(NamedTuple):
    """Stores the chances and the priority of the prediction."""

    chances: List[float]
    priority: int


class SimplePolicyEnsemble(EnsemblePolicy):
    @staticmethod
    def is_not_memo_policy(
        policy_name: Text, max_confidence: Optional[float] = None
    ) -> bool:
        is_memo_true = policy_name.endswith("_" + MemoizationPolicy.__name__)
        is_increase = policy_name.endswith("_" + AugmentedMemoizationPolicy.__name__)
        # also check if confidence is 0, than it cannot be count as prediction
        return not (is_memo_true or is_increase) or max_confidence == 0.0

    @staticmethod
    def _is_not_mapped_policies(
        policy_name: Text, max_confidence: Optional[float] = None
    ) -> bool:
        from convo.core.policies.mapping_policy import MappingPolicy

        is_maped = policy_name.endswith("_" + MappingPolicy.__name__)
        # also check if confidence is 0, than it cannot be count as prediction
        return not is_maped or max_confidence == 0.0

    @staticmethod
    def _is_policy_form(policy_name: Text) -> bool:
        from convo.core.policies.form_policy import FormPolicy

        return policy_name.endswith("_" + FormPolicy.__name__)

    def _collect_best_policy(
        self, predictions: Dict[Text, Forecast]
    ) -> Tuple[List[float], Optional[Text]]:
        """Picks the best policy prediction based on chances and policy priority.

        Args:
            predictions: the dictionary containing policy name as keys
                         and predictions as values

        Returns:
            best_probabilities: the list of chances for the next actions
            best_policy_name: the name of the picked policy
        """

        fetch_best_belief = (-1, -1)
        fetch_best_policy_name = None

        # form and mapping policies are special:
        # form should be above fallback
        # mapping should be below fallback
        # mapping is above form if it wins over fallback
        # therefore form predictions are stored separately

        fetch_form_belief = None
        fetch_form_policies_name = None

        for policy_name, prediction in predictions.items():
            belief = (max(prediction.chances), prediction.priority)
            if self._is_policy_form(policy_name):
                # store form prediction separately
                fetch_form_belief = belief
                fetch_form_policies_name = policy_name
            elif belief > fetch_best_belief:
                # pick the best policy
                fetch_best_belief = belief
                fetch_best_policy_name = policy_name

        if fetch_form_belief is not None and self._is_not_mapped_policies(
            fetch_best_policy_name, fetch_best_belief[0]
        ):
            # if mapping didn't win, check form policy predictions
            if fetch_form_belief > fetch_best_belief:
                fetch_best_policy_name = fetch_form_policies_name

        return predictions[fetch_best_policy_name].chances, fetch_best_policy_name

    def _best_policy_forecast(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
    ) -> Tuple[List[float], Optional[Text]]:
        """Finds the best policy prediction.

        Args:
            tracker: the :class:`convo.core.trackers.DialogueStateTracer`
            domain: the :class:`convo.shared.core.domain.Domain`
            interpreter: Interpreter which may be used by the policies to create
                additional features.

        Returns:
            chances: the list of chances for the next actions
            policy_name: the name of the picked policy
        """

        # find rejected action before running the policies
        # because some of them might add events
        rejected_act_name = None
        if len(tracker.events) > 0 and isinstance(
            tracker.events[-1], ActExecutionRejected
        ):
            rejected_act_name = tracker.events[-1].action_name

        forecast = {
            f"policy_{i}_{type(p).__name__}": self._fetch_forecast(
                p, tracker, domain, interpreter
            )
            for i, p in enumerate(self.policies)
        }

        if rejected_act_name:
            log.debug(
                f"Execution of '{rejected_act_name}' was rejected. "
                f"Setting its confidence to 0.0 in all predictions."
            )
            for prediction in forecast.values():
                prediction.chances[
                    domain.actions_index(rejected_act_name)
                ] = 0.0

        return self._collect_best_policy(forecast)

    @staticmethod
    def _fetch_forecast(
        policy: Policy,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
    ) -> Forecast:
        no_of_args_1_0 = 2
        args = convo.shared.utils.common.args_of(
            policy.predict_action_probabilities
        )
        if (
            len(args) > no_of_args_1_0
            and "interpreter" in args
        ):
            chances = policy.predict_action_probabilities(
                tracker, domain, interpreter
            )
        else:
            convo.shared.utils.io.raising_warning(
                "The function `predict_action_probabilities` of "
                "the `Policy` interface was changed to support "
                "additional parameters. Please make sure to "
                "adapt your custom `Policy` implementation.",
                category=DeprecationWarning,
            )
            chances = policy.predict_action_probabilities(
                tracker, domain, RegexInterpreter()
            )

        return Forecast(chances, policy.priority)

    def _fall_back_after_listen(
        self, domain: Domain, chances: List[float], policy_name: Text
    ) -> Tuple[List[float], Text]:
        """Triggers fallback if `action_listen` is predicted after a user utterance.

        This is done on the condition that:
        - a fallback policy is present,
        - there was just a user message and the predicted
          action is action_listen by a policy
          others than the MemoizationPolicy

        Args:
            domain: the :class:`convo.shared.core.domain.Domain`
            chances: the list of chances for the next actions
            policy_name: the name of the picked policy

        Returns:
            chances: the list of chances for the next actions
            policy_name: the name of the picked policy
        """

        fall_back_idx_policies = [
            (i, p) for i, p in enumerate(self.policies) if isinstance(p, PolicyFallback)
        ]

        if fall_back_idx_policies:
            fall_back_idx, fallback_policy = fall_back_idx_policies[0]

            log.debug(
                f"Action 'action_listen' was predicted after "
                f"a user message using {policy_name}. Predicting "
                f"fallback action: {fallback_policy.fallback_action_name}"
            )

            chances = fallback_policy.fallback_scores(domain)
            policy_name = f"policy_{fall_back_idx}_{type(fallback_policy).__name__}"

        return chances, policy_name

    def probability_using_finest_policy(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> Tuple[List[float], Optional[Text]]:
        """Predicts the next action the bot should take after seeing the tracker.

        Picks the best policy prediction based on chances and policy priority.
        Triggers fallback if `action_listen` is predicted after a user utterance.

        Args:
            tracker: the :class:`convo.core.trackers.DialogueStateTracer`
            domain: the :class:`convo.shared.core.domain.Domain`
            interpreter: Interpreter which may be used by the policies to create
                additional features.

        Returns:
            best_probabilities: the list of chances for the next actions
            best_policy_name: the name of the picked policy
        """

        chances, policy_name = self._best_policy_forecast(
            tracker, domain, interpreter
        )

        if (
            tracker.latestActionName == LISTEN_ACTION_NAME
            and chances is not None
            and chances.index(max(chances))
            == domain.actions_index(LISTEN_ACTION_NAME  )
            and self.is_not_memo_policy(policy_name, max(chances))
        ):
            chances, policy_name = self._fall_back_after_listen(
                domain, chances, policy_name
            )

        log.debug(f"Predicted next action using {policy_name}")
        return chances, policy_name


def _validate_policy_for_forms_available(
    domain: Domain, ensemble: Optional["EnsemblePolicy"]
) -> None:
    if not ensemble:
        return

    from convo.core.policies.form_policy import FormPolicy

    right_policies_for_forms = (FormPolicy, RulePolicy)

    have_policy_for_forms = ensemble is not None and any(
        isinstance(policy, right_policies_for_forms) for policy in ensemble.policies
    )

    if domain.form_names and not have_policy_for_forms:
        raise InvalidDomain(
            "You have defined a form action, but haven't added the "
            "FormPolicy to your policy ensemble. Either remove all "
            "forms from your domain or exclude the FormPolicy from your "
            "policy configuration."
        )


class InvalidPolicyConfiguration(ConvoExceptions ):
    """Exception that can be raised when policy config is not valid."""

    pass
