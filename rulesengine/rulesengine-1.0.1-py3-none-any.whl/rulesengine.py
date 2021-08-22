# -*- coding: utf-8 -*-
"""
Rules engine definition and the decorator to wrap it
"""

import types
from functools import wraps

from .common import LOGGER
from .common import RulesCourse
from .common import RulesData
from .common import RulesEngineException
from .rule import Rule


class RulesEngine:
    """
    Rules engine to manage and execute rules
    """

    def __init__(self, input_data: dict = {}, rules_course: RulesCourse = RulesCourse.non_blocking):
        self.rules = {}
        self.sorted_rules = []
        self.input = RulesData(input_data)
        self.rules_course = rules_course

    def add(self, NewRule: Rule, previous_rule: str = None, forced_order: int = None,  # pylint: disable=C0103
            converter: types.FunctionType = None) -> None:
        """
        Add a new rule to the pipeline
        """
        used_order = forced_order \
            if forced_order is not None \
            else NewRule.RULE_ORDER
        if used_order not in self.rules.keys():
            self.rules[used_order] = []
        self.rules[used_order].append((NewRule, previous_rule, converter))

    def _sort_rules(self) -> None:
        """
        Sort the rules for the pipeline execution
        """
        rules_keys = list(self.rules.keys())
        rules_keys.sort()
        if len(rules_keys) > 1 and rules_keys[0] < 0:
            inf_key = rules_keys[0]
            del rules_keys[0]
            rules_keys.append(inf_key)
            if rules_keys[0] < 0:
                exc_message = "A rule order has to be an integer equals to -1 or bigger : %s" % str(rules_keys)
                LOGGER.error(exc_message)
                raise RulesEngineException(exc_message)
        for rules_key in rules_keys:
            self.sorted_rules += self.rules[rules_key]

    def run(self) -> dict:
        """
        Execute the pipeline
        """
        self._sort_rules()
        for NewRule, expected_previous, converter in self.sorted_rules:  # pylint: disable=C0103
            # Run the rule with the potential extra arguments
            rule_filter = NewRule().run(
                self.input,
                expected_previous=expected_previous,
                converter=converter)

            # Use the rule filter result to define the pipeline behaviour
            if (self.rules_course == RulesCourse.non_blocking) or \
               (self.rules_course == RulesCourse.block_on_false and rule_filter) or \
               (self.rules_course == RulesCourse.block_on_true and not rule_filter):
                pass
            elif (self.rules_course == RulesCourse.block_on_false and not rule_filter) or \
                 (self.rules_course == RulesCourse.block_on_true and rule_filter):
                break
            elif self.rules_course == RulesCourse.error_on_false and not rule_filter:
                exc_message = "The rule filter of '%s' returned false and the rule course forbid it" % NewRule.__class__.RULE_NAME
                LOGGER.error(exc_message)
                raise RulesEngineException(exc_message, rule_name=NewRule.__class__.RULE_NAME)
            else:
                exc_message = "The rule engine course isn't defined with a correct value '%s'" % str(self.rules_course)
                LOGGER.error(exc_message)
                raise RulesEngineException(exc_message)
        return self.input

    def set(self, key, value):
        self.input.set(key, value)


class RuleEngineDec:
    """
    RulesEngine usable as decorators

    WARNING The signature of the function/method as to match the final rule output
    """
    @staticmethod
    def rule_engine(input_data: dict = None,
                    rules_course=RulesCourse.non_blocking) -> types.FunctionType:
        """
        Decorator to create the rule engine
        """
        def wrapper(func):
            @wraps(func)
            def arg_wrapper(*args, **kwargs):
                rule_engine = RulesEngine(kwargs if input_data is None else input_data, rules_course=rules_course)
                kwargs["_rule_engine"] = rule_engine
                return func(*args, **kwargs)
            return arg_wrapper
        return wrapper

    @staticmethod
    def add(NewRule: Rule, previous_rule: str = None, forced_order: int = None,  # pylint: disable=C0103
            converter: types.FunctionType = None) -> types.FunctionType:
        """
        Decorator to add a new rule the rule engine
        """
        def wrapper(func):
            @wraps(func)
            def arg_wrapper(*args, **kwargs):
                kwargs["_rule_engine"].add(
                    NewRule=NewRule,
                    previous_rule=previous_rule,
                    forced_order=forced_order,
                    converter=converter)
                return func(*args, **kwargs)
            return arg_wrapper
        return wrapper

    @staticmethod
    def run(func) -> types.FunctionType:
        """
        Decorator to run the rule engine's pipeline
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs = kwargs["_rule_engine"].run()
            if "_rule_engine" in kwargs.keys():
                del kwargs["_rule_engine"]
            if '_previous_rule' in kwargs.keys():
                del kwargs["_previous_rule"]
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def m_rule_engine(input_data: dict = None,
                      rules_course=RulesCourse.non_blocking) -> types.FunctionType:
        """
        Class method decorator to create the rule engine
        """
        def wrapper(method):
            @wraps(method)
            def arg_wrapper(self, *args, **kwargs):
                rule_engine = RulesEngine(
                    kwargs if input_data is None else input_data,
                    rules_course=rules_course)
                kwargs["_rule_engine"] = rule_engine
                return method(self, *args, **kwargs)
            return arg_wrapper
        return wrapper

    @staticmethod
    def m_add(NewRule: Rule, previous_rule: str = None, forced_order: int = None,  # pylint: disable=C0103
              converter: types.FunctionType = None) -> types.FunctionType:
        """
        Class method decorator to add a new rule the rule engine
        """
        def wrapper(method):
            @wraps(method)
            def arg_wrapper(self, *args, **kwargs):
                kwargs["_rule_engine"].add(
                    NewRule=NewRule,
                    previous_rule=previous_rule,
                    forced_order=forced_order,
                    converter=converter)
                return method(self, *args, **kwargs)
            return arg_wrapper
        return wrapper

    @staticmethod
    def m_run(method) -> types.FunctionType:
        """
        Class method decorator to run the rule engine's pipeline
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            kwargs = kwargs["_rule_engine"].run()
            if "_rule_engine" in kwargs.keys():
                del kwargs["_rule_engine"]
            if '_previous_rule' in kwargs.keys():
                del kwargs["_previous_rule"]
            return method(self, *args, **kwargs)
        return wrapper
