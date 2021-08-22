# -*- coding: utf-8 -*-
"""
Rules engine
"""

import types
from functools import wraps

from .common import RulesData
from .common import LOGGER


class RuleLogger:
    """
    Decorators to manage rules data
    """

    @staticmethod
    def logging_filter(func):
        """
        Decorator for the filter
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            LOGGER.debug("Rule filtering for %s" % self.__class__.RULE_NAME)
            success = func(self, *args, **kwargs)
            LOGGER.debug("Rule filtering ended for %s with result %s" % (self.__class__.RULE_NAME, success))
            return success
        return wrapper

    @staticmethod
    def logging_action(func):
        """
        Decorator for the action
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            LOGGER.debug("Rule action for %s" % self.__class__.RULE_NAME)
            success = func(self, *args, **kwargs)
            LOGGER.debug("Rule action ended for %s" % self.__class__.RULE_NAME)
            return success
        return wrapper

    @staticmethod
    def to_implement(func):
        """
        Decorator for the action
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):  # pylint: disable=W0613 W0612
            exc_message = "The method %s needs to be implemented in the inherited Rule class" % func.__name__
            LOGGER.error(exc_message)
            raise NotImplementedError(exc_message)


class Rule:
    """
    The default *abstract* Rule class from which rules have to inherit.

    Minimal implementation example :
    ``` python
    class MyRule(Rule):
        RULE_NAME = "MY_RULE"

        def filter(self, input_data: dict) -> bool:
            return True

        def action(self, input_data: dict) -> dict:
            input_data["my_value"] += 1
            return input_data
    ```
    """
    RULE_NAME = "RULE_ASBTRACT"  # rule name to display in logs and compare in execution
    RULE_ORDER = -1  # RuleEngine execution order: the default -1 is lastly executed, 0 is the first and biggers are next

    def run(self, input_data: RulesData, expected_previous: str = None, converter: types.FunctionType = None) -> bool:
        """
        Run the rule pipeline composed of the filter and possibly the action.
        Return a tuple composed of the filter result and the action result data
        if the filter returned true or the input_data if the filter returned false.

        WARNING in the case of the *_next_rule* item was defined in the input_data
        and if the rule isn't the expected next_rule the filter and action are skipped
        and the rule return True and the input_data

        WARNING in the case of the *expected_previous* was defined as run argument and
        *_previous_rule* wasn't defined in the input_data or wasn't equals to *expected_previous*,
        the rule isn't the expected rule the filter and action are skipped
        and the rule return True and the input_data
        """
        expected_rule = input_data.get_expected_next()
        is_expected_rule = expected_rule == self.__class__.RULE_NAME
        rule_filter = True

        # Managing the expected previously executed rule or the expected currently executed rule
        # if one of those case has to be cheked and doesn't match, the rule still return True and
        # the input data as output
        if (expected_previous is None or expected_previous == input_data.get_previous()) and \
           (expected_rule is None or is_expected_rule):
            if is_expected_rule:
                input_data.set_expected_next(None)
            if converter is not None:
                converter(input_data)
            rule_filter = self._filter(input_data)

            if rule_filter:
                self._action(input_data)
                input_data.set_previous(self.__class__.RULE_NAME)
            elif is_expected_rule:
                LOGGER.warning("The rule %s was expected but the filter doesn't allow the action" % self.__class__.RULE_NAME)
        elif expected_rule is not None:
            LOGGER.debug("The rule %s is skipped, the next expected rule is %s" % (
                self.__class__.RULE_NAME, expected_rule))
        return rule_filter

    @RuleLogger.logging_filter
    def _filter(self, rules_data: RulesData) -> bool:
        return self.filter(rules_data)

    @RuleLogger.logging_action
    def _action(self, rules_data: RulesData) -> None:
        return self.action(rules_data)

    @RuleLogger.to_implement
    def filter(self, rules_data: RulesData) -> bool:  # pylint: disable=R0201 W0613
        """
        The filter analyse input_data content and return True if the rule's action
        has to be run.

        Arguments:
        ----------
        rules_data: RulesData
            An object transmitted between every rules of the pipeline to store, share
            and manipulate the rules data

        Returns:
        --------
        bool
            A boolean defining the result of the filter. If `True`, the action will be
            performed

        """
        return False

    @RuleLogger.to_implement
    def action(self, rules_data: RulesData) -> None:  # pylint: disable=R0201
        """
        The action perform a treatment and can update the rules_data object

        Arguments:
        ----------
        rules_data: RulesData
            An object transmitted between every rules of the pipeline to store, share
            and manipulate the rules data

        Returns:
        --------
        None
        """
