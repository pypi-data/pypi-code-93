# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""A decorator which builds a :class:`azure.ml.component.Component`."""

from .component import _component, ComponentExecutor
from ._annotations import InputPath, InputFile, OutputPath, OutputFile, \
    StringParameter, EnumParameter, IntParameter, FloatParameter, BoolParameter
from ._exceptions import RequiredParamParsingError, TooManyDSLComponentsError

__all__ = [
    '_component',
    'ComponentExecutor',
    'TooManyDSLComponentsError',
    'InputPath',
    'InputFile',
    'OutputPath',
    'OutputFile',
    'StringParameter',
    'EnumParameter',
    'IntParameter',
    'FloatParameter',
    'BoolParameter',
    'RequiredParamParsingError',
]
