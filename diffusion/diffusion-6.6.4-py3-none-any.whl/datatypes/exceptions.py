""" Data types exceptions. """
from diffusion.internal.exceptions import DiffusionError


class DataTypeError(DiffusionError):
    """ General data type error. """


class UnknownDataTypeError(DataTypeError):
    """ Raised if the data type identifier does not exist in the system. """


class IncompatibleDatatypeError(DataTypeError):
    """ Raised if the provided data type was different from expected. """


class InvalidDataError(DataTypeError):
    """ Error with conversion of data. """
