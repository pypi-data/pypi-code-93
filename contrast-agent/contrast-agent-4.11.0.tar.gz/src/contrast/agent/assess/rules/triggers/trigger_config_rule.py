# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os

from contrast.extern import six

from contrast.agent.settings_state import SettingsState
from contrast.agent.assess.rules.dataflow_rule import DataflowRule
from contrast.api import Finding


class TriggerConfigRule(DataflowRule):
    """
    Base class for config rules that are actually implemented as triggers

    We have several rules that are technically config rules in TS, but are implemented
    as triggers for some of the frameworks we support. In these cases, the rule itself
    is fired like a trigger/dataflow rule. However, we need to structure the data we
    send to TS in a way that looks like a config rule.
    """

    SESSION_ID = "sessionId"
    PATH = "path"
    SNIPPET = "snippet"

    def _find_first_app_frame(self, node, stack):
        """
        Look for the first stack frame that doesn't belong to the framework

        This is a heuristic and may not work in all cases.
        """
        for frame in stack:
            if not frame.declaring_class.startswith(node.module):
                return frame

        # Fallback case
        return stack[0]

    def _create_filename(self, frame):
        filename = frame.file_name.rstrip(".py").replace(".", os.sep) + ".py"
        return "{}:{}".format(filename, frame.line_number)

    def _create_snippet(self, node, target, event):
        source = node.sources[0]
        params = (
            "{}={}".format(source, target)
            if isinstance(source, six.string_types)
            else repr(target)
        )

        method_name = (
            "{}.{}".format(
                event.stack[0].declaring_class.rstrip(".py"), event.stack[0].method_name
            )
            if event.stack[0].declaring_class.startswith(node.module)
            else node.name
        )

        return "{}({})".format(method_name, params)

    def create_finding(self, orig_properties, node, target, events, **kwargs):
        """
        Create a finding that makes the trigger rule look like a config rule in TS
        """
        settings = SettingsState()

        properties = {}
        properties[self.SESSION_ID] = settings.config.get_session_id()

        reported_frame = self._find_first_app_frame(node, events[-1].stack)
        properties[self.PATH] = self._create_filename(reported_frame)
        properties[self.SNIPPET] = self._create_snippet(node, target, events[-1])

        return Finding(self, properties, **kwargs)
