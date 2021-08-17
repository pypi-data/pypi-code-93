# -*- coding: utf-8 -*-
import logging


class LoggerFieldType:
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, logging.Logger):
            raise TypeError('must be logging.Logger object')
        return v
