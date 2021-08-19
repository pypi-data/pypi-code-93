""" Exceptions for encoded data. """

from diffusion.internal.exceptions import DiffusionError


class DataError(DiffusionError):
    """ General error with data encoding. """


class DataValidationError(DataError):
    """ Validation error. """


class DataWriteError(DataError):
    """ Error when writing data. """


class DataReadError(DataError):
    """ Error when reading data. """


class StreamExhausted(DataReadError):
    """ Error for unexpectedly reaching the end of a stream. """
