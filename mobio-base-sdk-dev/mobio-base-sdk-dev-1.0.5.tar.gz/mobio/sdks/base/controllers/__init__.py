#!/usr/bin/python
# -*- coding: utf8 -*-

from mobio.libs.validator import HttpValidator, VALIDATION_RESULT

from src.common import LANG
from src.common.mobio_exception import ParamInvalidError


class BaseController(object):
    PARAM_INVALID_VALUE = 412

    @staticmethod
    def abort_if_validate_error(rules, data):
        valid = HttpValidator(rules)
        val_result = valid.validate_object(data)
        if not val_result[VALIDATION_RESULT.VALID]:
            errors = val_result[VALIDATION_RESULT.ERRORS]
            raise ParamInvalidError(LANG.VALIDATE_ERROR, errors)

    @staticmethod
    def validate_optional_err(rules, data):
        valid = HttpValidator(rules)
        val_result = valid.validate_optional(data)
        if not val_result[VALIDATION_RESULT.VALID]:
            errors = val_result[VALIDATION_RESULT.ERRORS]
            raise ParamInvalidError(LANG.VALIDATE_ERROR, errors)

    @staticmethod
    def abort_if_param_empty_error(param, param_name):
        if param is None or param is '':
            raise ParamInvalidError(LANG.MUST_NOT_EMPTY, param_name)

    def __init__(self):
        pass