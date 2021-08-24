from collections import OrderedDict
from typing import TYPE_CHECKING, Any, AnyStr, Dict, Optional

from ruleau.exceptions import RuleErrorException
from ruleau.rule import Rule

if TYPE_CHECKING:
    from ruleau.adapter import ApiAdapter


class Process:
    """Class holding rule process"""

    def __init__(
        self,
        process_id: str,
        name: str,
        description: str,
        root_rule: Rule,
    ):
        self.id = process_id
        self.name = name
        self.description = description
        self.root_rule = root_rule

    @property
    def rules(self):
        return list(OrderedDict.fromkeys(self.root_rule.flatten_rule_objects()))

    def parse(self):
        self.root_rule.calculate_order_values()

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "root_rule": self.root_rule.id,
            "rules": [rule.parse() for rule in self.rules],
        }

    def execute(
        self,
        case_id: AnyStr,
        payload: Dict[AnyStr, Any],
        api_adapter: Optional["ApiAdapter"] = None,
    ):
        try:
            result = self.root_rule.execute(case_id, payload, self, api_adapter)
            return result
        # If any exception is hit during the process execution
        except RuleErrorException as e:
            raise e.rule_exception
        finally:
            # Always sync the rules current state
            if api_adapter:
                api_adapter.sync_results(self, case_id)
