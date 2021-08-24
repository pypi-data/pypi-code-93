from typing import AnyStr, Optional

from ruleau.constants import OverrideLevel
from ruleau.rule import Rule
from ruleau.structures import ExecutionResult


class Any(Rule):
    """Aggregator to implement OR operation
    Returns truthy, if any one of the rule result is truthy
    """

    def __init__(
        self,
        rule_id: AnyStr,
        name: AnyStr,
        *rules: "Rule",
        description: AnyStr = None,
        override_level: OverrideLevel = OverrideLevel.ANY_OVERRIDE,
        run_if: Optional[Rule] = None
    ):
        def all_aggregator(context: ExecutionResult, _):
            return any(result.result for result in context.dependent_results)

        all_aggregator.__doc__ = description if description else All.__doc__
        super().__init__(
            all_aggregator, rule_id, name, list(rules), override_level, run_if
        )


class All(Rule):
    """Aggregator to implement AND operation
    Returns truthy, if all of the rule results are truthy
    """

    def __init__(
        self,
        rule_id: AnyStr,
        name: AnyStr,
        *rules: "Rule",
        description: AnyStr = None,
        override_level: OverrideLevel = OverrideLevel.ANY_OVERRIDE,
        run_if: Optional[Rule] = None
    ):
        def all_aggregator(context: ExecutionResult, _):
            return all(
                result.result
                for result in context.dependent_results
                if not result.skipped
            )

        all_aggregator.__doc__ = description if description else All.__doc__
        super().__init__(
            all_aggregator, rule_id, name, list(rules), override_level, run_if
        )
