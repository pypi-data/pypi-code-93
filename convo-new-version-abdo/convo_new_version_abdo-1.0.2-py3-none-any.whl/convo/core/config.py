import copy
import os
from typing import Optional, Text, List, Dict, Union, Tuple, Any, TYPE_CHECKING

import convo.shared.utils.io
import convo.shared.utils.cli
from convo.core.constants import (
    BY_DEFAULT_NLU_FALL_BACK_THRESHOLD,
    BY_DEFAULT_CORE_FALL_BACK_THRESHOLD,
    BY_DEFAULT_NLU_FALL_BACK_AMBIGUITY_THRESHOLD,
)
from convo.shared.core.constants import (
    ACTION_DEFAULT_FALLBACK_NAME,
    TWO_STAGE_FALLBACK_ACTION_NAME   ,
)
import convo.utils.io
from convo.shared.constants import (
    DEFAULT_NLU_FALLBACK_INTENTS_NAME,
    TRAINING_DATA_LATEST_FORMAT_VERSION ,
)
from convo.shared.core.training_data.story_reader.yaml_story_reader import (
    YAMLStoryReviewer,
)

import convo.shared.utils.io
import convo.utils.io
from convo.core.policies.mapping_policy import MappingPolicy
from convo.core.policies.rule_policy import RulePolicy
from convo.core.policies.fallback import PolicyFallback
from convo.core.policies.two_stage_fallback import TwoStageFallbackPolicy
from convo.nlu.classifiers.fallback_classifier import FallbackClassifier

if TYPE_CHECKING:
    from convo.core.policies.policy import Policy
    from convo.shared.core.domain import Domain
    from convo.shared.core.training_data.structures import StoryStage


def load(config_file: Optional[Union[Text, Dict]]) -> List["Policy"]:
    """Load policy data stored in the specified file."""
    from convo.core.policies.ensemble import EnsemblePolicy

    if not config_file:
        raise ValueError(
            "You have to provide a valid path to a config file. "
            "The file '{}' could not be found."
            "".format(os.path.abspath(config_file))
        )

    configuration_data_set = {}
    if isinstance(config_file, str) and os.path.isfile(config_file):
        configuration_data_set = convo.shared.utils.io.read_configuration_file(config_file)
    elif isinstance(config_file, Dict):
        configuration_data_set = config_file

    return EnsemblePolicy.from_dict(configuration_data_set)


def migrate_fall_back_policies(config: Dict) -> Tuple[Dict, Optional["StoryStage"]]:
    """Migrate the deprecated fallback policies to their `RulePolicy` counterpart.

    Args:
        config: The model configuration containing deprecated policies.

    Returns:
        The updated configuration and the required fallback rules.
    """
    new_configuration = copy.deepcopy(config)
    policy = new_configuration.get("policies", [])

    fall_back_configuration = _fetch_configuration_for_name(
        PolicyFallback.__name__, policy
    ) or _fetch_configuration_for_name(TwoStageFallbackPolicy.__name__, policy)

    if not fall_back_configuration:
        return config, None

    convo.shared.utils.cli.printing_information(f"Migrating the '{fall_back_configuration.get('name')}'.")

    _update_rule_policy_configuration_for_fallback(policy, fall_back_configuration)
    _update_fallback_configuration(new_configuration, fall_back_configuration)
    new_configuration["policies"] = _fetch_drop_policy(fall_back_configuration.get("name"), policy)

    # The triggered action is hardcoded for the Two-Stage Fallback`
    fall_back_act_name = TWO_STAGE_FALLBACK_ACTION_NAME   
    if fall_back_configuration.get("name") == PolicyFallback.__name__:
        fall_back_act_name = fall_back_configuration.get(
            "fallback_action_name", ACTION_DEFAULT_FALLBACK_NAME
        )

    fall_back_rule = _fetch_faq_rule(
        f"Rule to handle messages with low NLU confidence "
        f"(automated conversion from '{fall_back_configuration.get('name')}')",
        DEFAULT_NLU_FALLBACK_INTENTS_NAME,
        fall_back_act_name,
    )

    return new_configuration, fall_back_rule


def _fetch_configuration_for_name(component_name: Text, config_part: List[Dict]) -> Dict:
    return next(
        (config for config in config_part if config.get("name") == component_name), {}
    )


def _update_rule_policy_configuration_for_fallback(
    policies: List[Dict], fallback_config: Dict
) -> None:
    """Update the `RulePolicy` configuration with the parameters for the fallback.

    Args:
        policies: The current list of configured policies.
        fallback_config: The configuration of the deprecated fallback configuration.
    """
    rule_policy_configuration = _fetch_configuration_for_name(RulePolicy.__name__, policies)

    if not rule_policy_configuration:
        rule_policy_configuration = {"name": RulePolicy.__name__}
        policies.append(rule_policy_configuration)

    minimum_core = fallback_config.get(
        "core_threshold", BY_DEFAULT_CORE_FALL_BACK_THRESHOLD
    )
    fall_back_act_name = fallback_config.get(
        "fallback_core_action_name"
    ) or fallback_config.get("fallback_action_name", ACTION_DEFAULT_FALLBACK_NAME)

    rule_policy_configuration.setdefault("core_fallback_threshold", minimum_core)
    rule_policy_configuration.setdefault("core_fallback_action_name", fall_back_act_name)


def _update_fallback_configuration(config: Dict, fallback_config: Dict) -> None:
    fallback_classifier_configuration = _fetch_configuration_for_name(
        FallbackClassifier.__name__, config.get("pipeline", [])
    )

    if not fallback_classifier_configuration:
        fallback_classifier_configuration = {"name": FallbackClassifier.__name__}
        config["pipeline"].append(fallback_classifier_configuration)

    nlu_threshold = fallback_config.get("nlu_threshold", BY_DEFAULT_NLU_FALL_BACK_THRESHOLD)
    ambiguity_threshold = fallback_config.get(
        "ambiguity_threshold", BY_DEFAULT_NLU_FALL_BACK_AMBIGUITY_THRESHOLD
    )

    fallback_classifier_configuration.setdefault("threshold", nlu_threshold)
    fallback_classifier_configuration.setdefault("ambiguity_threshold", ambiguity_threshold)


def _fetch_faq_rule(rule_name: Text, intent: Text, action_name: Text) -> "StoryStage":
    faq_rule = f"""
       version: "{TRAINING_DATA_LATEST_FORMAT_VERSION }"

       rules:
       - rule: {rule_name}
         steps:
         - intent: {intent}
         - action: {action_name}
    """

    story_reviewer = YAMLStoryReviewer()
    return story_reviewer.reading_from_string(faq_rule)[0]


def _fetch_drop_policy(policy_to_drop: Text, policies: List[Dict]) -> List[Dict]:
    return [policy for policy in policies if policy.get("name") != policy_to_drop]


def migrate_mapping_policy_to_rules(
    config: Dict[Text, Any], domain: "Domain"
) -> Tuple[Dict[Text, Any], "Domain", List["StoryStage"]]:
    """Migrate `MappingPolicy` to its `RulePolicy` counterparts.

    This migration will update the config, domain and generate the required rules.

    Args:
        config: The model configuration containing deprecated policies.
        domain: The domain which potentially includes convo_intents with the `triggers`
            property.

    Returns:
        The updated model configuration, the domain without trigger convo_intents, and the
        generated rules.
    """
    policy = config.get("policies", [])
    had_mapping_policy = False
    had_rule_policy = False

    for policy in policy:
        if policy.get("name") == MappingPolicy.__name__:
            had_mapping_policy = True
        if policy.get("name") == RulePolicy.__name__:
            had_rule_policy = True

    if not had_mapping_policy:
        return config, domain, []

    convo.shared.utils.cli.printing_information(f"Migrating the '{MappingPolicy.__name__}'.")
    new_configuration = copy.deepcopy(config)
    new_domain_name = copy.deepcopy(domain)

    new_rules_determined = []
    for intent, properties in new_domain_name.intent_props.items():
        # remove triggers from convo_intents, if any
        activate_act = properties.pop("triggers", None)
        if activate_act:
            activate_rule = _fetch_faq_rule(
                f"Rule to map `{intent}` intent to "
                f"`{activate_act}` (automatic conversion)",
                intent,
                activate_act,
            )
            new_rules_determined.append(activate_rule)

    # finally update the policies
    policy = _fetch_drop_policy(MappingPolicy.__name__, policy)

    if new_rules_determined and not had_rule_policy:
        policy.append({"name": RulePolicy.__name__})
    new_configuration["policies"] = policy

    return new_configuration, new_domain_name, new_rules_determined
