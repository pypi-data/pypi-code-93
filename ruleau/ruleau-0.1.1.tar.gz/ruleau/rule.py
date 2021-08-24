import functools
import inspect
from typing import TYPE_CHECKING, Any, AnyStr, Dict, List, Optional

import regex as re

from ruleau.constants import OverrideLevel
from ruleau.context_manager import Context
from ruleau.docs import clean_source, comments, description, doctests, parameters
from ruleau.exceptions import (
    CannotOverrideException,
    ConditionalDependencyReusedException,
    RuleErrorException,
    RuleFunctionNameAttributeCollisionException,
    RuleIdIllegalCharacterException,
    RuleRequiresIdException,
    RuleRequiresNameException,
    RunIfRuleHasRunIfException,
)
from ruleau.structures import ExecutionResult, RuleauDict

if TYPE_CHECKING:
    from ruleau.adapter import ApiAdapter
    from ruleau.process import Process
    from ruleau.types import Function


class Rule:
    def __init__(
        self,
        func: "Function",
        id_: AnyStr,
        name: AnyStr,
        depends_on: List["Rule"],
        override_level: OverrideLevel = OverrideLevel.ANY_OVERRIDE,
        run_if: Optional["Rule"] = None,
    ):
        """
        :param func: User defined rule
        :param name: User defined human readable name of the rule
        :param depends_on: Rule dependencies
        :param override_level: Override level
        :param run_if: Optional, Conditional rule
        """
        self.id = id_
        self.name = name
        # Set the user defined function
        self.func = func
        # Validate the rule, make sure the name is always set for a rule
        self._validate()

        # Set the override level for rule
        self.override_level = override_level
        # Set rule function name
        self.__name__ = func.__name__

        # Setup the rule dependencies
        self.depends_on = depends_on
        self.run_if = run_if
        # Validate dependencies
        self._validate_duplicate_dependencies()
        self._validate_run_if()

        # Set default values for order & result
        self.order = None
        self.execution_result = None

        # This preserves the original Docstring on the decorated function
        # which allows DocTest to detect the function
        functools.update_wrapper(self, func)

    @property
    def dependencies(self):
        if self.run_if:
            return self.depends_on + [self.run_if]
        return self.depends_on

    def __str__(self) -> str:
        return f"{str(self.id)} - {str(self.name)} ({str(self.__name__)})"

    def __repr__(self):
        return str(self)

    def __call__(self, *args, **kwargs) -> bool:
        return self.func(*args, **kwargs)

    def _validate(self):
        """
        Validator to check if top level rule has a human readable name and
        and id
        :raises: TopLevelRuleRequiresNameException
        :raises: RuleRequiresIdException
        """
        # Validate if Rule name is present
        if not self.name or not isinstance(self.name, str):
            raise RuleRequiresNameException()

        # Validate if Rule ID is present
        if not self.id or not isinstance(self.id, str):
            raise RuleRequiresIdException()

        # Validate the Rule ID
        if not re.match(r"^([a-zA-Z0-9-_~]+)+$", self.id):
            raise RuleIdIllegalCharacterException()

        # If an attribute with the same name as the function name
        try:
            getattr(self, self.func.__name__)
            raise RuleFunctionNameAttributeCollisionException()
        except AttributeError:
            pass

    def _validate_duplicate_dependencies(self):
        """
        Validator to check if rule has duplicate dependencies
        in run_if and depends_on
        :raises: ConditionalDependencyReusedException
        """
        # Validate if there are no duplicate dependencies
        if self.run_if in self.depends_on:
            raise ConditionalDependencyReusedException(
                f"{self.run_if} has been reused in `run_if` "
                f"and `depends_on` in {str(self)}"
            )

    def _validate_run_if(self):
        if self.run_if and self.run_if.run_if:
            raise RunIfRuleHasRunIfException

    def _get_source(self) -> AnyStr:
        """Get the cleaned source code of the rule"""
        return clean_source(inspect.getsource(self.func))

    @property
    def description(self) -> AnyStr:
        """Parse the description of rule"""
        return description(self.func.__doc__)

    def calculate_order_values(self, index=None):
        """
        This sets the `order` value for this rule
        and all of the dependencies below it.

        :param index: Used internally, do not set
        """
        if index is None:
            self.order = 0
        else:
            if self.order is not None:
                self.order = max(self.order, index + 1)
            else:
                self.order = index + 1
        for dependency in self.dependencies:
            dependency.calculate_order_values(self.order)

    def flatten_rule_objects(self, flat_rules=None) -> List["Rule"]:
        """Method to flatten rule objects, usually used for root rule"""
        if flat_rules is None:
            flat_rules = []
        flat_rules.append(self)
        for dependency in self.dependencies:
            dependency.flatten_rule_objects(flat_rules)
        return flat_rules

    def parse(self):
        """Collects and returns parsed rule data for documentation
        :return: Dictionary of rule data
        """
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "override_level_name": self.override_level.name,
            "override_level": self.override_level.value,
            "source": self._get_source(),
            "comments": comments(self._get_source()),
            "docstring": self.func.__doc__,
            "description": self.description,
            "parameters": parameters(self.func.__doc__),
            "dependencies": [
                {
                    "id": dependent.id,
                    "run_if": dependent == self.run_if,
                }
                for dependent in self.dependencies
            ],
            "doctests": doctests(self.func),
        }

    def execute(
        self,
        case_id: AnyStr,
        payload: Dict[AnyStr, Any],
        process: "Process",
        api_adapter: Optional["ApiAdapter"] = None,
    ) -> ExecutionResult:
        """
        Execute the rule and apply overrides
        :param case_id: Case ID
        :param payload: Case payload
        :param process: Process instance
        :param api_adapter: ApiAdapter instance
        :param is_parent_skipped: Override if the parent rule is skipped
        :return: ExecutionResult of the rule
        """

        # If there is a run_if dependency
        if self.run_if:
            # run the run if rule
            run_if_result = self.run_if.execute(case_id, payload, process, api_adapter)
            # if it fails then skip the execution of this rule
            if not run_if_result.result:
                self.skip_execution()
                return self.execution_result

        # If the rule is already executed return the previous result
        # unless that result was skipped
        if self.execution_result and not self.execution_result.skipped:
            return self.execution_result

        # Prep the rule payload
        rule_payload = RuleauDict(payload)

        # Run this rule dependencies
        dependency_results = {
            dependency.__name__: dependency.execute(
                case_id, payload, process, api_adapter
            )
            for dependency in self.depends_on
        }
        context = Context(dependency_results)

        self.execution_result = ExecutionResult(
            self,
            rule_payload,
            None,
            dependency_results,
        )

        # Run this rule
        try:
            rule_result = self.__call__(context, rule_payload)
            self.execution_result.result = rule_result
        # If it fails mark it as failed
        except Exception as e:
            self.execution_result.failed = True
            raise RuleErrorException(self, e)

        if api_adapter:
            # Apply overrides on the rule result
            self.execution_result = self.apply_override(
                case_id, process, self.execution_result, api_adapter
            )

        # Assign to internal object & return the rule result
        return self.execution_result

    def apply_override(
        self,
        case_id,
        process,
        execution_result: ExecutionResult,
        api_adapter: "ApiAdapter",
    ) -> ExecutionResult:
        """
        Check if there are any overrides to apply to this case. If so apply the
        override.
        :param case_id: Case ID
        :param execution_result: ExecutionResult of a rule
        :param api_adapter: ApiAdapter instance
        :return: ExecutionResult of the rule
        """
        # Get overrides for the rule in a case
        override = api_adapter.fetch_override(case_id, process.id, self.id)

        # Apply override to the executed rule result, if any
        # Overrides should only be applied to allowed rule and if they're present
        if override:
            # Throw an exception if the backend is trying to override a NO_OVERRIDE rule
            if self.override_level == OverrideLevel.NO_OVERRIDE:
                raise CannotOverrideException(f"Cannot override {self.name}")
            else:
                # Override the rule result and set the overridden flag
                execution_result.override = override["id"]
                execution_result.original_result = execution_result.result
                execution_result.result = override["applied"]
        return execution_result

    def skip_execution(self):
        """
        Recursively skip a rule and all its children. If a rule is skipped when
        it already has a result, that result is kept.
        """
        if self.execution_result is None:
            self.execution_result = ExecutionResult.skipped_result(self)
        for dependency in self.depends_on:
            dependency.skip_execution()
