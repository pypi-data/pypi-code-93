# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.base_rule import BaseRule
from contrast.api.settings_pb2 import ProtectionRule


class MalformedHeader(BaseRule):
    """
    Malformed Header Protection rule
    """

    NAME = "malformed-header"

    def __init__(self, settings):
        BaseRule.__init__(self, settings)

    @property
    def mode(self):
        """
        Always block at perimeter
        """
        return ProtectionRule.BLOCK_AT_PERIMETER
