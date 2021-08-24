import logging
from typing import TYPE_CHECKING, Any, AnyStr, Dict, List, Optional

from jsonpath_ng import parse

from ruleau.adapter import ApiAdapter
from ruleau.exceptions import (
    CaseIdRequiredException,
    DuplicateRuleIdException,
    DuplicateRuleNameException,
)
from ruleau.process import Process
from ruleau.rule import Rule

if TYPE_CHECKING:
    from ruleau.structures import ExecutionResult

logger = logging.getLogger(__name__)


def validate_no_duplicate_rule_names(rules: List[Rule]) -> None:
    """Returns True if there are no duplicate Rule Names are used
    A name can only be re-used if the same rule is included multiple times
    """
    rules_dict = {}
    for rule in rules:
        if rule.name not in rules_dict:
            rules_dict[rule.name] = rule
        else:
            if rule != rules_dict[rule.name]:
                raise DuplicateRuleNameException()


def validate_no_duplicate_rule_ids(rules: List[Rule]) -> None:
    """Returns True if there are no duplicate Rule IDs used
    An ID can only be re-used if the same rule is included multiple times
    """
    rules_dict = {}
    for rule in rules:
        if rule.id not in rules_dict:
            rules_dict[rule.id] = rule
        else:
            if rule != rules_dict[rule.id]:
                raise DuplicateRuleIdException()


def get_case_id_from_json_path(
    payload: Dict[AnyStr, Any],
    case_id_jsonpath: AnyStr,
) -> Optional[str]:
    """
    Return case_id value from json payload

    :param payload Dict[AnyStr, Any]: Raise
    :param case_id_jsonpath AnyStr: The json path to the case_id in the payload
    :rtype Optional[str]: The case_id from the payload (or None if no path provided)
    :raises ValueError: If provided JSON path not found
    :raises ValueError: If the case_id at the path is blank (empty string)
    """
    # If jsonpath is None, then there is no case_id
    if case_id_jsonpath is None:
        return None

    # Otherwise find the case id in the json
    case_id_results = parse(case_id_jsonpath).find(payload)
    if not case_id_results:
        raise ValueError("Case ID not found in payload")

    case_id = str(case_id_results[0].value)
    if not case_id:
        raise ValueError("Case ID not found")

    return case_id


def execute(
    executable_rule: Rule,
    payload: Dict[AnyStr, Any],
    case_id_jsonpath: AnyStr = None,
    case_id: Optional[AnyStr] = None,
    api_adapter: Optional[ApiAdapter] = None,
) -> "ExecutionResult":
    """
    Executes the provided rule, following dependencies and
    passing in results accordingly
    """

    if api_adapter:
        case_id = (
            case_id
            if case_id is not None
            else get_case_id_from_json_path(payload, case_id_jsonpath)
        )
        if not case_id:
            raise CaseIdRequiredException()

    # Validate unique rule name
    flattened_rules_as_objects = executable_rule.flatten_rule_objects()
    validate_no_duplicate_rule_names(flattened_rules_as_objects)

    # Validate unique rule ids
    validate_no_duplicate_rule_ids(flattened_rules_as_objects)

    # If API adapter was was passed sync the case
    executable_rule.calculate_order_values()
    process = Process(
        executable_rule.id,
        executable_rule.name,
        executable_rule.description,
        executable_rule,
    )

    if api_adapter:

        # Sync the process rules
        api_adapter.sync_process(process)

        # Sync the case
        api_adapter.sync_case(case_id, process.id, payload)

    # Trigger the rule execution, from the top level rule
    return process.execute(case_id, payload, api_adapter)
