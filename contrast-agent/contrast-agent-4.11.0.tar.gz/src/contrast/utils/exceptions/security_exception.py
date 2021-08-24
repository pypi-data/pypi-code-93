# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
class SecurityException(Exception):

    STATUS_CODE = 403
    REASON_PHRASE = "Forbidden"
    STATUS = "{} {}".format(STATUS_CODE, REASON_PHRASE)

    def __init__(self, rule, message=None):
        message = (
            message
            if message
            else "Rule {} threw a security exception".format(rule.name)
        )
        super(SecurityException, self).__init__(message)
