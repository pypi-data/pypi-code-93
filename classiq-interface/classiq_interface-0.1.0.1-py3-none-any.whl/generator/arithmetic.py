import ast
import enum
import keyword
import math
import random
import re
from enum import Enum
from typing import Union, Optional, Generic, TypeVar, Dict, List

import pydantic
from classiq_interface.generator.function_params import FunctionParams
from pydantic.generics import GenericModel

_MAX_FRACTION_PLACES = 5
DEFAULT_ARG_NAME = "arg"
DEFAULT_RIGHT_ARG_NAME = "right_arg"
DEFAULT_LEFT_ARG_NAME = "left_arg"
DEFAULT_OUT_NAME = "out"
LeftDataT = TypeVar("LeftDataT")
RightDataT = TypeVar("RightDataT")
Numeric = (float, int)


class FixPointNumber(pydantic.BaseModel):
    float_value: float
    max_fraction_places: pydantic.conint(ge=0) = _MAX_FRACTION_PLACES
    is_signed: Optional[bool] = None
    _fraction_places: Optional[int] = pydantic.PrivateAttr(default=None)
    _int_val: Optional[int] = pydantic.PrivateAttr(default=None)
    _size: Optional[int] = pydantic.PrivateAttr(default=None)
    _integer_part_size: Optional[int] = pydantic.PrivateAttr(default=None)

    def set_int_representation(self):
        int_val = math.floor(self.float_value * 2 ** self.max_fraction_places)
        int_val = self.signed_int_to_unsigned(int_val)

        if int_val == 0:
            fraction_places = 0
        else:
            bin_val = bin(int_val)[2:]
            fraction_places = self.max_fraction_places
            for b in reversed(bin_val):
                if b == "1" or fraction_places == 0:
                    break
                fraction_places -= 1
            int_val = int_val >> (self.max_fraction_places - fraction_places)

        self._fraction_places = fraction_places
        self._int_val = int_val

    @staticmethod
    def signed_int_to_unsigned(number: int):
        """Return the integer value of a signed int if it would we read as un-signed in binary representation"""
        if number >= 0:
            return number

        not_power2 = abs(number) & (abs(number) - 1) != 0
        return number + 2 ** (number.bit_length() + 1 * not_power2)

    @staticmethod
    def binary_to_float(bin_rep: str, fraction_part_size: int, is_signed: bool = False):
        negative_offset = -(2 ** len(bin_rep)) * (bin_rep[0] == "1") * is_signed
        value = int(bin_rep, 2) + negative_offset
        if (
            fraction_part_size > 0
        ):  # this separated to make sure that the value remains int if no there is no fraction part
            value = value / 2 ** fraction_part_size
        return value

    @pydantic.validator("is_signed", always=True)
    def validate_is_signed(cls, is_signed: bool, values: dict):
        float_value = values.get("float_value")
        if is_signed is False and float_value < 0:
            raise ValueError("Not possible to define a negative number as not signed")
        elif is_signed is None:
            is_signed = float_value < 0

        return is_signed

    @property
    def fraction_places(self):
        if self._fraction_places is None:
            self.set_int_representation()
        return self._fraction_places

    def set_fraction_places(self, value: int):
        if value > self.max_fraction_places:
            self.max_fraction_places = value
            self.set_int_representation()

        self._int_val = math.floor(self.int_val * 2 ** (value - self.fraction_places))
        self._fraction_places = value
        self._size = self._integer_part_size + self._fraction_places

    @property
    def int_val(self):
        if self._int_val is None:
            self.set_int_representation()
        return self._int_val

    @property
    def integer_part_size(self):
        if self._integer_part_size is None:
            self._integer_part_size = self.int_val.bit_length() - self.fraction_places
        return self._integer_part_size

    def set_integer_part_size(self, value: int):
        if value < self.integer_part_size:
            raise ValueError("size cannot be lower than minimum number bits required")
        self._integer_part_size = value
        self._size = self._integer_part_size + self._fraction_places
        self._int_val = int(self.bin_val, 2)

    def bit_length(self):
        return 1 if self.int_val == 0 else self.int_val.bit_length()

    @property
    def size(self):
        if self._size is None:
            self._size = self.bit_length()
        return self._size

    @property
    def bin_val(self):
        if self._int_val is None:
            self.set_int_representation()

        bin_rep = bin(self._int_val)[2:]
        size_diff = self.size - len(bin_rep)
        if self.float_value >= 0:
            return "0" * size_diff + bin_rep
        else:
            return "1" * size_diff + bin_rep

    @property
    def actual_float_value(self):
        return self.binary_to_float(self.bin_val, self.fraction_places, self.is_signed)

    def __getitem__(self, item):
        return [v for v in self.bin_val[::-1]][
            item
        ]  # follow qiskit convention that LSB is the top wire, bigendian

    class Config:
        extra = "forbid"


class RegisterUserInput(pydantic.BaseModel):
    size: pydantic.PositiveInt
    name: Optional[str] = None
    is_signed: bool = False
    fraction_places: pydantic.conint(ge=0) = 0

    class Config:
        extra = "forbid"


class UnaryOpParams(FunctionParams):
    arg: RegisterUserInput
    output_size: Optional[pydantic.PositiveInt]
    output_name: Optional[str]

    @pydantic.root_validator()
    def validate_output_size(cls, values):
        output_size = values.get("output_size")
        arg = values.get("arg")
        if output_size is None:
            values["output_size"] = arg.size
        return values

    def create_io_enums(self):
        output_name = self.output_name if self.output_name else DEFAULT_OUT_NAME
        self._output_names = Enum("BinaryOpOutputs", {output_name: output_name})

        arg_name = self.arg.name if self.arg.name else DEFAULT_ARG_NAME

        self._input_names = Enum(
            "UnaryOpInputs",
            {arg_name: arg_name},
        )

    class Config:
        arbitrary_types_allowed = True


class LogicalAnd(FunctionParams):
    args: List[Union[RegisterUserInput, FixPointNumber, int, float]]
    output_name: Optional[str] = DEFAULT_OUT_NAME

    @pydantic.validator("args")
    def validate_inputs_sizes(cls, args):
        for arg in args:
            if (
                isinstance(arg, RegisterUserInput)
                and arg.size != 1
                and arg.fraction_places != 0
            ):
                raise ValueError(
                    f"All inputs to logical and must be of size 1 | {arg.name}"
                )

        return args

    @pydantic.validator("args")
    def set_inputs_names(cls, args):
        for i, arg in enumerate(args):
            if isinstance(arg, RegisterUserInput):
                arg.name = arg.name if arg.name else DEFAULT_ARG_NAME + str(i)

        return args

    def create_io_enums(self):
        output_name = self.output_name
        self._output_names = Enum("BinaryOpOutputs", {output_name: output_name})

        arg_names = [
            arg.name for arg in self.args if isinstance(arg, RegisterUserInput)
        ]

        self._input_names = Enum(
            "LogicalAndInputs",
            {arg_name: arg_name for arg_name in arg_names},
        )

    class Config:
        arbitrary_types_allowed = True


class BitwiseInvert(UnaryOpParams):
    inplace: bool = False

    @pydantic.validator("arg")
    def validate_arg_is_integer(cls, arg):
        if arg.fraction_places > 0:
            raise ValueError("Invert is defined only for integers")
        return arg


class BinaryOpParams(GenericModel, FunctionParams, Generic[LeftDataT, RightDataT]):
    left_arg: Union[LeftDataT, RegisterUserInput]
    right_arg: Union[RightDataT, RegisterUserInput]
    output_size: Optional[pydantic.PositiveInt]
    output_name: Optional[str]

    @pydantic.root_validator()
    def validate_one_is_register(cls, values):
        if isinstance(values.get("left_arg"), Numeric) and isinstance(
            values.get("right_arg"), Numeric
        ):
            raise ValueError("One argument must be a register")
        return values

    def create_io_enums(self):
        output_name = self.output_name if self.output_name else DEFAULT_OUT_NAME
        self._output_names = Enum("BinaryOpOutputs", {output_name: output_name})

        if isinstance(self.left_arg, RegisterUserInput) and isinstance(
            self.right_arg, RegisterUserInput
        ):
            left_arg_name = (
                self.left_arg.name if self.left_arg.name else DEFAULT_LEFT_ARG_NAME
            )
            right_arg_name = (
                self.right_arg.name if self.right_arg.name else DEFAULT_RIGHT_ARG_NAME
            )
            self._input_names = Enum(
                "BinaryOpInputs",
                {left_arg_name: left_arg_name, right_arg_name: right_arg_name},
            )
            return

        if isinstance(self.left_arg, RegisterUserInput):
            arg_name = (
                self.left_arg.name if self.left_arg.name else DEFAULT_LEFT_ARG_NAME
            )
        else:
            assert isinstance(
                self.right_arg, RegisterUserInput
            ), "At least one argument should be a register"
            arg_name = (
                self.right_arg.name if self.right_arg.name else DEFAULT_RIGHT_ARG_NAME
            )

        self._input_names = Enum("BinaryOpInputs", {arg_name: arg_name})

    class Config:
        arbitrary_types_allowed = True


class BinaryOpWithIntInputs(BinaryOpParams[int, int]):
    @pydantic.root_validator()
    def validate_int_registers(cls, values):
        left_arg = values.get("left_arg")
        is_left_arg_float_register = (
            isinstance(left_arg, RegisterUserInput) and left_arg.fraction_places > 0
        )
        right_arg = values.get("right_arg")
        is_right_arg_float_register = (
            isinstance(right_arg, RegisterUserInput) and right_arg.fraction_places > 0
        )
        if is_left_arg_float_register or is_right_arg_float_register:
            raise ValueError("Boolean operation are defined only for integer")

        return values


class BinaryOpWithFloatInputs(
    BinaryOpParams[Union[float, FixPointNumber], Union[float, FixPointNumber]]
):
    @pydantic.validator("left_arg", "right_arg")
    def convert_numeric_to_fix_point_number(cls, val):
        if isinstance(val, Numeric):
            val = FixPointNumber(float_value=val)
        return val


class BitwiseAnd(BinaryOpWithIntInputs):
    pass


class BitwiseOr(BinaryOpWithIntInputs):
    pass


class BitwiseXor(BinaryOpWithIntInputs):
    pass


class Adder(BinaryOpWithFloatInputs):
    inplace: bool = True


class Equal(BinaryOpWithFloatInputs):
    @pydantic.validator("output_size")
    def validate_output_size(cls, val):
        if val and val != 1:
            raise ValueError("Equal function has only one output qubits")
        return val


class MappingMethods(str, enum.Enum):
    topological = "topological"
    pebble = "pebble"


class Arithmetic(FunctionParams):
    max_fraction_places: pydantic.conint(ge=0) = _MAX_FRACTION_PLACES
    expression: str
    definitions: Dict[
        str,
        Union[
            pydantic.StrictInt, pydantic.StrictFloat, FixPointNumber, RegisterUserInput
        ],
    ]
    method: MappingMethods = MappingMethods.pebble
    qubit_count: Optional[pydantic.conint(ge=0)] = None
    output_name: Optional[str]
    random_seed: Optional[int] = None

    @pydantic.validator("expression")
    def check_expression_is_legal(cls, expression):
        ast.parse(expression, "", "eval")
        return expression

    @pydantic.root_validator()
    def check_all_variable_are_defined(cls, values):
        expression, definitions = values.get("expression"), values.get("definitions")

        literals = re.findall("[A-Za-z][A-Za-z0-9]*", expression)
        undefined_literals = {
            literal for literal in literals if literal not in definitions
        }.difference(set(keyword.kwlist))

        if undefined_literals:
            raise ValueError(f"{undefined_literals} need to be defined in definitions")
        return values

    @pydantic.root_validator()
    def substitute_expression(cls, values):
        # TODO there isn't a secure way to simplify the expression which does not involve using eval.
        #  Can be done with sdk on client side
        expression, definitions = values.get("expression"), values.get("definitions")
        new_definition = dict()
        for var_name, value in definitions.items():
            if isinstance(value, RegisterUserInput):
                new_definition[var_name] = value
                continue
            elif isinstance(value, int):
                pass
            elif isinstance(value, float):
                value = FixPointNumber(float_value=value).actual_float_value
            elif isinstance(value, FixPointNumber):
                value = value.actual_float_value
            else:
                raise ValueError(f"{type(value)} type is illegal")

            expression = re.sub(r"\b" + var_name + r"\b", str(value), expression)
        values["expression"] = expression
        values["definitions"] = new_definition
        return values

    @pydantic.validator("definitions")
    def set_register_names(cls, definitions):
        for k, v in definitions.items():
            if isinstance(v, RegisterUserInput):
                v.name = k
        return definitions

    @pydantic.validator("random_seed", always=True)
    def validate_random_seed(cls, random_seed):
        return random.randint(0, 1000) if not random_seed else random_seed

    def create_io_enums(self):
        literals = re.findall("[A-Za-z][A-Za-z0-9]*", self.expression)
        output_name = self.output_name if self.output_name else DEFAULT_OUT_NAME
        self._input_names = Enum(
            "ArithmeticInputs",
            {literal: literal for literal in literals if literal not in keyword.kwlist},
        )
        self._output_names = Enum("ArithmeticOutputs", {output_name: output_name})

    class Config:
        extra = "forbid"


class ArithmeticOracle(Arithmetic):
    @pydantic.validator("expression")
    def validate_compare_expression(cls, value):
        ast_obj = ast.parse(value, "", "eval")
        if not isinstance(ast_obj.body, (ast.Compare, ast.BoolOp)):
            raise ValueError("Must a comparison expression")

        return value
