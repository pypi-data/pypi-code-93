# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.exceptions._azureml_exception import UserErrorException


class TooManyDSLComponentsError(UserErrorException):
    """Exception when multiple dsl.components are found in single component entry."""

    def __init__(self, count, file):
        """Error message inits here."""
        super().__init__("Only one dsl.component is allowed per file, {} found in {}".format(count, file))


class RequiredParamParsingError(UserErrorException):
    """This error indicates that a parameter is required but not exists in the command line."""

    def __init__(self, name, arg_string):
        """Init the error with the parameter name and its arg string."""
        msg = "'%s' cannot be None since it is not optional. " % name + \
              "Please make sure command option '%s' exists." % arg_string
        super().__init__(msg)


class DSLComponentDefiningError(UserErrorException):
    """This error indicates that the user define a dsl.component in an incorrect way."""

    def __init__(self, cause):
        """Init the error with the cause which causes the wrong dsl.component."""
        super().__init__("Defining the component failed due to '%s'." % cause)
