import json
from typing import TYPE_CHECKING, AnyStr, Dict

from ruleau.structures import ExecutionResult

if TYPE_CHECKING:
    from ruleau.rule import Rule


class Context:
    """
    The context is passed in to the execution of a rule. It stores the results
    of the dependencies of the rule.
    """

    class DependentResults:
        def __init__(self, execution_results: Dict[AnyStr, "ExecutionResult"]):
            self.dependencies = execution_results

        def __getattr__(self, name):
            # Gets the attribute
            dependency = self.dependencies.get(name, None)
            attribute = getattr(super(), name, None)

            # If neither are found raise an exception
            if not (dependency or attribute):
                raise AttributeError(
                    f"Result for rule '{name}' not available, as it was not "
                    f"declared as a dependency'. "
                    f"depends_on={json.dumps(list(self.dependencies.keys()))}"
                )

            # Return the found attribute/dependency
            return attribute or dependency

        def __iter__(self):
            # Iterate through the dependencies
            for dep in self.dependencies:
                yield getattr(self, dep)

        def parse(self):
            return {
                dep_name: execution_result.result
                for dep_name, execution_result in self.dependencies.items()
            }

    def __init__(self, execution_results: Dict[AnyStr, "ExecutionResult"]):
        self.dependent_results = self.DependentResults(execution_results)

    def parse(self):
        return {"dependent_results": self.dependent_results.parse()}


def mock_context(rule_results: Dict[str, bool]):
    """
    Given an dictionary containing the rule function name
    as the key and the mocked result as the value, creates
    an ExecutionResult.

    :param rule_results: A dictionary containing the mock
    results for the depedent rules

    :return: ExecutionResult containing mocked results
    """
    return Context(
        {
            key: ExecutionResult(None, {}, value, {})
            for key, value in rule_results.items()
        }
    )
