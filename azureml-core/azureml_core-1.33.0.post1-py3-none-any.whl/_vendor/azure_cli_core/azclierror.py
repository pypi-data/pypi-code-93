# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import logging

logger = logging.getLogger(__name__)
# pylint: disable=unnecessary-pass

_COMMAND_METADATA_LOGGER = 'az_command_data_logger'


class CommandLoggerContext:
    def __init__(self, module_logger):
        self.logger = module_logger
        self.hdlr = logging.getLogger(_COMMAND_METADATA_LOGGER)  # pylint: disable=protected-access

    def __enter__(self):
        if self.hdlr:
            self.logger.addHandler(self.hdlr)  # add command metadata handler
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.hdlr:
            self.logger.removeHandler(self.hdlr)


# Base class for all the AzureCLI defined error classes.
class AzCLIError(Exception):
    """ Base class for all the AzureCLI defined error classes.
    DO NOT raise this error class in your codes. """

    def __init__(self, error_msg, recommendation=None):
        # error message
        self.error_msg = error_msg

        # set recommendations to fix the error if the message is not actionable,
        # they will be printed to users after the error message, one recommendation per line
        self.recommendations = []
        self.set_recommendation(recommendation)

        # exception trace for the error
        self.exception_trace = None
        super().__init__(error_msg)

    def set_recommendation(self, recommendation):
        if isinstance(recommendation, str):
            self.recommendations.append(recommendation)
        elif isinstance(recommendation, list):
            self.recommendations.extend(recommendation)

    def set_exception_trace(self, exception_trace):
        self.exception_trace = exception_trace

    def print_error(self):
        with CommandLoggerContext(logger):
            # print error type and error message
            message = '{}: {}'.format(self.__class__.__name__, self.error_msg)
            logger.error(message)
            # print exception trace if there is
            if self.exception_trace:
                logger.exception(self.exception_trace)
            # print recommendations to action
            if self.recommendations:
                for recommendation in self.recommendations:
                    print(recommendation, file=sys.stderr)

    def send_telemetry(self):
        # telemetry.set_error_type(self.__class__.__name__)
        pass


class ClientError(AzCLIError):
    """ AzureCLI should be responsible for the errors.
    DO NOT raise this error class in your codes. """
    def send_telemetry(self):
        # super().send_telemetry()
        # telemetry.set_failure(self.error_msg)
        # if self.exception_trace:
        #     telemetry.set_exception(self.exception_trace, '')
        pass


# CLI internal error type
class CLIInternalError(ClientError):
    """ AzureCLI internal error """
    pass
