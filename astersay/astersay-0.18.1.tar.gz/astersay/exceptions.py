#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#


class AstersayError(Exception):
    pass


class AgiError(AstersayError):
    pass


class AgiUnknownError(AgiError):
    pass


class AgiAppError(AgiError):
    pass


class AgiHangupError(AgiAppError):
    pass


class AgiSighupError(AgiHangupError):
    pass


class AgiSigpipeError(AgiHangupError):
    pass


class AgiUsageError(AgiError):
    pass


class AgiInvalidCommand(AgiError):
    pass


class AppError(AstersayError):
    pass


class ImproperlyConfigured(AstersayError):
    pass


class TokenError(AstersayError):
    pass
