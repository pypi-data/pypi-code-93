"""Pentaquark exceptions
"""


class PentaQuarkWarning(Warning):
    pass


class PentaQuarkException(Exception):
    pass


class PentaQuarkValidationError(PentaQuarkException, ValueError):
    """Raised on value validation error"""
    pass


class PentaQuarkConfigurationError(PentaQuarkException):
    """Raised on wrong configuration (settings or models)"""
    pass


class PentaQuarkInvalidLabelError(PentaQuarkException):
    """Invalid label name"""
    pass


class PentaQuarkObjectDoesNotExistError(PentaQuarkException):
    pass


class PentaQuarkCardinalityError(PentaQuarkException):
    pass


class PentaquarkInvalidOperationError(PentaQuarkException):
    pass


class PentaQuarkInvalidMatchOperationException(PentaquarkInvalidOperationError):
    pass


class PentaQuarkInvalidQueryException(PentaQuarkException):
    pass
