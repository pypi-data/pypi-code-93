# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This file is used for backward compatibility of dsl._component to enable defining component with functions."""

import argparse
import sys
import pathlib
from typing import List, Union

from azure.ml.component.dsl.types import Input, _Path, Output, String, Float, Integer, Enum, Boolean, _Param
from azure.ml.component.dsl.types import _DATA_TYPE_NAME_MAPPING
from ._exceptions import RequiredParamParsingError, DSLComponentDefiningError


class CommandLineGenerator:
    """This class is used to generate command line arguments for an input/output in a component."""

    def __init__(self, param: Union[Input, Output, _Param], arg_name=None, arg_string=None):
        self._param = param
        self._arg_name = arg_name
        self._arg_string = arg_string

    @property
    def param(self) -> Union[Input, Output, String, Float, Integer, Enum, Boolean]:
        """Return the bind input/output/parameter"""
        return self._param

    @property
    def arg_string(self):
        """Return the argument string of the parameter."""
        return self._arg_string

    @property
    def arg_name(self):
        """Return the argument name of the parameter."""
        return self._arg_name

    @arg_name.setter
    def arg_name(self, value):
        self._arg_name = value

    def to_cli_option_str(self, style=None):
        """Return the cli option str with style, by default return underscore style --a_b."""
        return self.arg_string.replace('_', '-') if style == 'hyphen' else self.arg_string

    def arg_group_str(self):
        """Return the argument group string of the input/output/parameter."""
        s = '%s %s' % (self.arg_string, self._arg_placeholder())
        return '[%s]' % s if isinstance(self.param, (Input, _Param)) and self.param.optional else s

    def _arg_group(self):
        """Return the argument group item. This is used for legacy module yaml."""
        return [self.arg_string, self._arg_dict()]

    def _arg_placeholder(self) -> str:
        raise NotImplementedError()

    def _arg_dict(self) -> dict:
        raise NotImplementedError()


class DSLCommandLineGenerator(CommandLineGenerator):
    """This class is used to generate command line arguments for an input/output in a dsl.component."""

    @property
    def arg_string(self):
        """Compute the cli option str according to its name, used in argparser."""
        return '--' + self.param.name

    def add_to_arg_parser(self, parser: argparse.ArgumentParser, default=None):
        """Add this parameter to ArgumentParser, both command line styles are added."""
        cli_str_underscore = self.to_cli_option_str(style='underscore')
        cli_str_hyphen = self.to_cli_option_str(style='hyphen')
        if default is not None:
            return parser.add_argument(cli_str_underscore, cli_str_hyphen, default=default)
        else:
            return parser.add_argument(cli_str_underscore, cli_str_hyphen,)

    def _update_name(self, name: str):
        """Update the name of the port/param.

        Initially the names of inputs should be None, then we use variable names of python function to update it.
        """
        if self.param._name is not None:
            raise AttributeError("Cannot set name to %s since it is not None, the value is %s." % (name, self._name))
        if not name.isidentifier():
            raise DSLComponentDefiningError("The name must be a valid variable name, got '%s'." % name)
        self.param._name = name

    def _arg_placeholder(self) -> str:
        io_tag = 'outputs' if isinstance(self.param, Output) else 'inputs'
        return "{%s.%s}" % (io_tag, self.param.name)


class OutputPath(Output):
    pass


class IntParameter(Integer):
    pass


class FloatParameter(Float):
    pass


class StringParameter(String):
    pass


class EnumParameter(Enum):
    pass


class BoolParameter(Boolean):
    pass


class InputPath(_Path):
    """InputFile indicates an input which is a file."""

    def __init__(self, type='path', description=None, name=None, optional=None):
        """Initialize an input file port Declare type to use your customized port type."""
        super().__init__(description=description, optional=optional)
        self._name = name
        self._type = type


class InputFile(InputPath):
    """InputFile indicates an input which is a file."""

    def __init__(self, description=None, name=None, optional=None):
        """Initialize an input file port Declare type to use your customized port type."""
        super().__init__(description=description, name=name, optional=optional)
        self._type = 'AnyFile'


# TODO: Refine this class if we need to enable parallel component with dsl._component
class _InputFileList:

    def __init__(self, inputs: List[InputPath]):
        self.validate_inputs(inputs)
        self._inputs = inputs
        for i in inputs:
            if i.arg_name is None:
                i.arg_name = i.name

    @classmethod
    def validate_inputs(cls, inputs):
        for i, port in enumerate(inputs):
            if not isinstance(port, (InputFile, InputPath)):
                msg = "You could only use InputPath in an input list, got '%s'." % type(port)
                raise DSLComponentDefiningError(msg)
            if port.name is None:
                raise DSLComponentDefiningError("You must specify the name of the %dth input." % i)
        if all(port.optional for port in inputs):
            raise DSLComponentDefiningError("You must specify at least 1 required port in the input list, got 0.")

    def add_to_arg_parser(self, parser: argparse.ArgumentParser):
        for port in self._inputs:
            port.add_to_arg_parser(parser)

    def load_from_args(self, args):
        """Load the input files from parsed args from ArgumentParser."""
        files = []
        for port in self._inputs:
            str_val = getattr(args, port.name, None)
            if str_val is None:
                if not port.optional:
                    raise RequiredParamParsingError(name=port.name, arg_string=port.arg_string)
                continue
            files += [str(f) for f in pathlib.Path(str_val).glob('**/*') if f.is_file()]
        return files

    def load_from_argv(self, argv=None):
        if argv is None:
            argv = sys.argv
        parser = argparse.ArgumentParser()
        self.add_to_arg_parser(parser)
        args, _ = parser.parse_known_args(argv)
        return self.load_from_args(args)

    @property
    def inputs(self):
        return self._inputs


class OutputFile(OutputPath):
    """OutputFile indicates an output which is a file."""

    def __init__(self, description=None):
        """Initialize an output file port Declare type to use your custmized port type."""
        super().__init__(type='AnyFile', description=description)


_DATA_TYPE_NAME_MAPPING_EXTENDED = {
    **_DATA_TYPE_NAME_MAPPING,
    **{
        v.__name__: v
        for v in globals().values() if isinstance(v, type) and issubclass(v, _Param) and v.DATA_TYPE
    }
}


def _get_annotation_by_type_name(t: str):
    return _DATA_TYPE_NAME_MAPPING_EXTENDED.get(t)
