# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.


class HttpOnlyRuleMixin(object):
    @property
    def name(self):
        return "httponly"

    def is_violated(self, value):
        """
        The rule is violated if the value is False or if it is not set at all (None)
        """
        return not value
