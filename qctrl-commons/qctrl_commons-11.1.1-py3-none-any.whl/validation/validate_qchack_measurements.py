"""
Validator for core__calculateQchackMeasurements mutation.
"""

import numpy as np

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.validation.base import BaseMutationInputValidator
from qctrlcommons.validation.utils import read_numpy_array


class CalculateQchackMeasurementsValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateQchackMeasurements mutation.
    """

    properties = {"shotCount": {"type": "integer", "minimum": 1, "maximum": 10000}}

    def check_controls(self, input_):  # pylint:disable=no-self-use
        """
        Expects that the control has between 1 and 256 segments, and that
        each value has norm at most 1.

        Parameters
        ----------
        input_: dict
            the GraphQL input.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        controls = input_["controls"]
        if len(controls) < 1 or len(controls) > 100:
            raise QctrlFieldError(
                message="The number of controls must be between 1 and 100 (inclusive).",
                fields=["controls"],
            )
        for control in controls:
            duration = control["duration"]
            values = read_numpy_array(**control["values"])
            repetition_count = control["repetitionCount"]

            if duration <= 0 or duration > 300:
                raise QctrlFieldError(
                    message="The control duration must be greater than 0 and at most 300.",
                    fields=["duration"],
                )
            if len(values.shape) != 1:
                raise QctrlFieldError(
                    message="The control values must be a 1D array.", fields=["values"]
                )
            if len(values) < 1 or len(values) > 256:
                raise QctrlFieldError(
                    message="The control must have between 1 and 256 values (inclusive).",
                    fields=["values"],
                )
            if np.any(np.abs(values) > 1 + 1e-8):
                raise QctrlFieldError(
                    message="The control values must have norm at most 1.",
                    fields=["values"],
                )
            if repetition_count < 1 or repetition_count > 64:
                raise QctrlFieldError(
                    message="The control repetition count must be between 1 and 64 (inclusive).",
                    fields=["repetitionCount"],
                )
