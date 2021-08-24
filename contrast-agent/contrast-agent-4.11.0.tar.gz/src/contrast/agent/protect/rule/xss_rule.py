# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.base_rule import BaseRule
from contrast.api.settings_pb2 import ProtectionRule


class Xss(BaseRule):
    """
    Cross Site Scripting Protection rule
    Currently only a prefilter / block at perimeter rule
    """

    NAME = "reflected-xss"

    def __init__(self, settings):
        BaseRule.__init__(self, settings)

    @property
    def mode(self):
        """
        Always block at perimeter
        """
        mode = self.mode_from_settings()

        return (
            mode
            if mode in [ProtectionRule.NO_ACTION, ProtectionRule.MONITOR]
            else ProtectionRule.BLOCK_AT_PERIMETER
        )
