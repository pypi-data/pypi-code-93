# -*- coding: utf-8 -*-
"""
Commont tools to manage the rules engine
"""

import logging
from dataclasses import dataclass
from dataclasses import field
from enum import Enum

LOGGER = logging.getLogger('rulesengine')
LOGGER.addHandler(logging.NullHandler())


class RulesEngineException(ValueError):
    """
    The rules engine pipeline has been created with unconsistant data/parameters
    """

    def __init__(self, *args, **kwargs):
        self.rule_context = {}
        if "rule_name" in kwargs.keys():
            self.rule_context["rule_name"] = kwargs["rule_name"]
            del kwargs["rule_name"]
        super(RulesEngineException, self).__init__(*args, **kwargs)

    def __str__(self):
        return "%s;rule_context=%s" % (
            super(RulesEngineException, self).__str__(),
            str(self.rule_context))


class RulesCourse(Enum):
    """
    Enum defining possible RuleEngine execution course
    """
    non_blocking = 0
    block_on_false = 1
    block_on_true = 2
    error_on_false = 3


@dataclass(frozen=True)
class RulesData:
    """
    Object countaining the data transfered between rules
    """
    dataset: dict = field(default_factory=dict)
    history: dict = field(default_factory=dict)

    def __post_init__(self, dataset={}):
        self.history["previous"] = None
        self.history["expected_next"] = None
        for key, item in dataset.items():
            self.history[key] = item

    def get(self, key):
        """
        Get a value using the key
        """
        return self.dataset[key] if key in self.dataset.keys() else None

    def set(self, key, value):
        """
        Set a value using a key
        """
        self.dataset[key] = value
        return key

    def delete(self, key):
        """
        Deleting a value at a specific key
        """
        value = self.dataset[key]
        del self.dataset[key]
        return value

    def get_previous(self) -> str:
        """
        Return the name of the previously executed rule
        """
        return self.history["previous"]

    def set_previous(self, rule_name: str) -> str:
        """
        Change the name stored as the previously executed rule
        """
        self.history["previous"] = rule_name
        return rule_name

    def get_expected_next(self) -> str:
        """
        Return the name of the next allowed rule or None if every rules are allowed
        """
        return self.history["expected_next"]

    def set_expected_next(self, rule_name: str) -> str:
        """
        Change the name stored of the next allowed rule
        """
        self.history["expected_next"] = rule_name
        return rule_name
