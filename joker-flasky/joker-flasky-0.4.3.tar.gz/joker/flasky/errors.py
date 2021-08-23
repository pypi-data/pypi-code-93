#!/usr/bin/env python3
# coding: utf-8

import volkanic.introspect


class KnownError(volkanic.introspect.ErrorBase):
    # TODO: remove this
    def __str__(self):
        if not self.args:
            return ''
        if len(self.args):
            return str(self.args[0])


class OperationalError(KnownError):
    extra = {'code': 1}



C1Error = OperationalError


class TechnicalError(KnownError):
    extra = {'code': 2}

    def __str__(self):
        s = super().__str__()
        return f'{s} <{self.error_key}>'


C2Error = TechnicalError


class ErrorInfo(volkanic.introspect.ErrorInfo):
    def to_dict(self, code=3):
        if isinstance(self.exc, volkanic.introspect.ErrorBase):
            return self.exc.to_dict()
        return {
            'code': code,
            'error_key': self.error_key,
            'message': f'出错了ಥ_ಥ <{self.error_key}>',
        }
