# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class ConfigurationError(Exception):
    pass


class IncompleteConfigurationError(ConfigurationError):
    def __init__(self, parameter, path):
        super(IncompleteConfigurationError, self).__init__(
            'Configuration does not specify parameter "%s" which should be located at "%s"'
            % (parameter.name, path)
        )


class InvalidPathError(ConfigurationError):
    def __init__(self, path):
        super(InvalidPathError, self).__init__('Path "%s" is unreachable' % path)


class ParameterError(ConfigurationError):
    def __init__(self, msg, parameter=None):
        if parameter is not None:
            super(ParameterError, self).__init__('%s: %s' % (parameter, msg))
        else:
            super(ParameterError, self).__init__(msg)
        self.reason = msg
        self.parameter = parameter


class DeclarationError(ParameterError):
    def __init__(self, msg, parameter=None):
        super(DeclarationError, self).__init__(msg, parameter)


class UnknownUnitError(DeclarationError):
    def __init__(self, msg, parameter=None):
        super(UnknownUnitError, self).__init__(msg, parameter)


class SpecificationError(ParameterError):
    def __init__(self, msg, parameter=None):
        super(SpecificationError, self).__init__(msg, parameter)


class RepresentationError(SpecificationError):
    def __init__(self, msg, parameter=None):
        super(RepresentationError, self).__init__(msg, parameter)


class InvalidUnitError(RepresentationError):
    def __init__(self, msg, parameter=None):
        super(InvalidUnitError, self).__init__(msg, parameter)


# noinspection PyPep8Naming
class ValueError_(SpecificationError):
    def __init__(self, msg, parameter=None):
        super(ValueError_, self).__init__(msg, parameter)
