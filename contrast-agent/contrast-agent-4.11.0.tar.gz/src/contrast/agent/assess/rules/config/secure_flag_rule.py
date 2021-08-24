# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.


class SecureFlagRuleMixin(object):
    @property
    def name(self):
        return "secure-flag-missing"

    def is_violated_properties(*args, **kwargs):
        """Override for safety. In theory, this should never be called."""
        return False

    def is_violated(self, value):
        """Rule is violated if config value is missing (None) or set to False"""
        return not value
