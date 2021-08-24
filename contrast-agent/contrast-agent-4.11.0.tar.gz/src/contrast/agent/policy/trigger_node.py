# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re
from contrast.extern.six import integer_types

from contrast.agent.policy import constants
from contrast.agent.assess.assess_exceptions import ContrastAssessException
from contrast.agent.assess.policy.trigger_actions.default_action import DefaultAction
from contrast.agent.assess.policy.trigger_actions import redos_action
from contrast.agent.assess.policy.trigger_actions import ssrf_action
from contrast.agent.policy.policy_node import PolicyNode


class TriggerNode(PolicyNode):

    TRIGGER_ACTIONS = {
        constants.TRIGGER_ACTION_DEFAULT: DefaultAction(),
        constants.TRIGGER_ACTION_REDOS: redos_action.RedosAction(),
        constants.TRIGGER_ACTION_SSRF: ssrf_action.SsrfAction(),
    }

    def __init__(
        self,
        module,
        class_name,
        instance_method,
        method_name,
        source,
        dataflow=True,
        good_value=None,
        bad_value=None,
        action=None,
        policy_patch=True,
        rule=None,
        python2_only=False,
        python3_only=False,
        protect_mode=False,
    ):
        super(TriggerNode, self).__init__(
            module,
            class_name,
            instance_method,
            method_name,
            source,
            None,
            policy_patch=policy_patch,
            python2_only=python2_only,
            python3_only=python3_only,
        )

        self.dataflow = dataflow

        self.good_value = (
            re.compile(good_value, flags=re.IGNORECASE) if good_value else None
        )
        self.bad_value = (
            re.compile(bad_value, flags=re.IGNORECASE) if bad_value else None
        )
        self.action = action or constants.TRIGGER_ACTION_DEFAULT

        self.rule = rule

        self.protect_mode = protect_mode

        self.validate()

    @property
    def node_type(self):
        return "TYPE_METHOD"

    @property
    def dataflow_rule(self):
        return self.dataflow

    def validate(self):
        super(TriggerNode, self).validate()

        if not self.dataflow_rule:
            return

        if not (self.sources and len(self.sources) != 0):
            raise ContrastAssessException(
                "Trigger {} did not have a proper source. Unable to create.".format(
                    self.name
                )
            )

    def get_matching_sources(self, self_obj, ret, args, kwargs):
        sources = []

        for source in self.sources:
            if source == constants.OBJECT:
                sources.append(self_obj)
            elif source == constants.ALL_ARGS:
                sources.append(args)
            elif source == constants.ALL_KWARGS:
                sources.append(kwargs)
            elif source == constants.RETURN:
                sources.append(ret)
            elif isinstance(source, integer_types) and len(args) > source:
                sources.append(args[source])
            elif kwargs and source in kwargs:
                sources.append(kwargs[source])

        return sources

    def get_protect_sources(self, args, kwargs):
        self_obj = args[0] if self.instance_method else None
        args = args[1:] if self.instance_method else args
        return self.get_matching_sources(self_obj, None, args, kwargs)

    @property
    def trigger_action(self):
        return self.TRIGGER_ACTIONS.get(self.action)

    @classmethod
    def from_dict(cls, obj, dataflow=True, rule=None):
        return cls(
            obj[constants.JSON_MODULE],
            obj.get(constants.JSON_CLASS_NAME, ""),
            obj.get(constants.JSON_INSTANCE_METHOD, True),
            obj[constants.JSON_METHOD_NAME],
            obj.get(constants.JSON_SOURCE, None),
            dataflow,
            obj.get(constants.JSON_GOOD_VALUE, None),
            obj.get(constants.JSON_BAD_VALUE, None),
            obj.get(constants.JSON_ACTION, None),
            policy_patch=obj.get(constants.JSON_POLICY_PATCH, True),
            rule=rule,
            python2_only=obj.get(constants.JSON_PY2_ONLY, False),
            python3_only=obj.get(constants.JSON_PY3_ONLY, False),
            protect_mode=obj.get(constants.JSON_PROTECT_MODE, False),
        )
