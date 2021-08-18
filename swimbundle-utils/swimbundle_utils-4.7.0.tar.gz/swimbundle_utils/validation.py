from validators import ValidationFailure
from pendulum.exceptions import ParserError
import validators
import pendulum
import re


class StopValidation(object):
    """Value to indicate that validation should stop if the value is this class"""
    def __init__(self):
        raise TypeError("Don't instantiate StopValidation!")


class ValidValue(object):
    """Container class for a valid value"""
    def __init__(self, value):
        self.value = value


class InvalidValue(object):
    """Container class for an invalid value"""
    def __init__(self, value):
        self.value = value


class ValueRange(object):
    """Range of values"""

    def __init__(self, value_type):
        self.value_type = value_type

    def _in_range(self, value):
        raise NotImplementedError("Must override in_range()!")

    def __contains__(self, value):
        """Check if the range contains a value.
        Will return false if the value isn't the correct type, unless it is a SpecialValue Instance

        Args:
            value: value to check if it contains
        """
        if not isinstance(value, self.value_type) and not isinstance(value, SpecialValue):
            return False
        return self._in_range(value)


class SpecialValue(object):
    """Class to represent a value that shouldn't be type checked in ValueRange __contains__
    """
    pass


class InfinityVal(SpecialValue):
    """Infinity exists for float but not int, so this class represents infinity for all numerical types
    """
    def __init__(self, pos=True):
        """
        Args:
            pos: If this infinity is positive or negative

        """
        self.pos = pos

    def __sub__(self, other):
        return self

    def __add__(self, other):
        return self

    def __ge__(self, other):
        return self.pos

    def __le__(self, other):
        return not self.pos

    def __gt__(self, other):
        return self.pos

    def __lt__(self, other):
        return not self.pos

    def __str__(self):
        return ("+" if self.pos else "-") + "inf"


class IntRange(ValueRange):
    """Class to have an integer range
    """
    def __init__(self, start, end):
        super(IntRange, self).__init__(int)
        self.start = start
        self.end = end

    def _in_range(self, value):
        return self.start <= value < self.end

    def __str__(self):
        return "IntRange[{}, {})".format(self.start, self.end)


class PositiveIntRange(IntRange):
    """Positive Integer Range"""
    def __init__(self, include_zero=True):
        if include_zero:
            start = 0
        else:
            start = 1
        super(PositiveIntRange, self).__init__(start, InfinityVal())


class NegativeIntRange(IntRange):
    """Negative Integer Range"""
    def __init__(self, include_zero=True):
        if include_zero:
            end = 1  # Off by one since range(0, 10) is actually [0, 9]
        else:
            end = 0
        super(NegativeIntRange, self).__init__(InfinityVal(pos=False), end)


class FloatRange(IntRange):
    """Float Range"""
    def __init__(self, start, end):
        super(FloatRange, self).__init__(start, end)
        self.value_type = float

    def __str__(self):
        return "FloatRange[{}, {})".format(self.start, self.end)


class Validator(object):
    """Validator class instance.
    Can wrap a function with Validators().add_type_validator()
    Or directly created
    """
    def __init__(self, name):
        self.name = name

    def __call__(self, value):
        raise NotImplementedError("Must override __call__!")


class RegexValidator(Validator):
    """Validate a regex statement
    """
    def __init__(self, regex, name="regex"):
        super(RegexValidator, self).__init__(name)
        self.regex = regex

    def __call__(self, value):
        if bool(re.match(self.regex, value)):
            return ValidValue(value)
        else:
            return InvalidValue(value)


class Validators(object):
    """
    Singleton validator class for keeping track of the validators used in validation
    """
    instance = None

    # Singleton class to contain the validation methods

    class __Validators(object):
        def __init__(self):
            self.type_vmap = {  # Validator map
                "ipv4": self._make_validator(validators.ipv4, "ipv4"),
                "url": self._make_validator(validators.url, "url"),
                "domain": self._make_validator(validators.domain, "domain"),
            }

            self.add_type_validator("int", self.is_int)  # Add custom validators this same way
            self.add_type_validator("bool", self.is_boolean)  # Add a function
            self.add_type_validator("datetime", self.is_datetime)  # Add a Validator instance

        @staticmethod
        def _make_validator(func, name):
            class ValidatorInst(Validator):
                def __call__(self, val):
                    if val == StopValidation:
                        return val

                    res = func(val)
                    if res and isinstance(res, bool):  # Handle validators bool response
                        return val
                    elif isinstance(res, ValidValue):  # Custom funcs return valid value
                        return res.value
                    elif isinstance(res, InvalidValue):  # Raise on invalid value
                        raise ValidationFailure(func, {"value": val})
                    if isinstance(res, ValidationFailure):  # Raise validation failure
                        raise res

                    raise Exception("Invalid response from validator function!")

            return ValidatorInst(name)

        def add_type_validator_inst(self, inst, override=False):
            """Add a type validator instance directly

            Args:
                inst: Validator class instance
                override: Override any previous entry with the same name

            """
            assert isinstance(inst, Validator)
            if inst.name in self.type_vmap and not override:
                raise TypeError("Attempted to set type validation function without being set to override!")
            self.type_vmap[inst.name] = inst

        def add_type_validator(self, type_name, func, override=False):
            """Add a type validator from a function given a type_name

            Args:
                type_name: Name of the validator
                func: Function with signature func(val) -> return ValidValue(val) or InvalidValue(val)
                override: If this validator already exists, replace it in the mapping

            """
            self.add_type_validator_inst(self._make_validator(func, type_name), override=override)

        def get_type_validators(self):
            """
            Get the map of validators for types

            Returns:
                validator dict

            """
            return self.type_vmap

        def is_boolean(self, value):
            """
            Basic boolean validator func
            Args:
                value: value to validate

            Returns:
                ValidValue or InvalidValue
            """
            if isinstance(value, bool):
                return ValidValue(value)
            else:
                return InvalidValue(value)

        def is_datetime(self, value):
            """
            Basic datetime validator func

            Args:
                value: value to validate

            Returns:
                ValidValue or InvalidValue
            """
            try:
                return ValidValue(pendulum.parse(value, strict=False).to_iso8601_string())
            except ParserError:
                return InvalidValue(value)

        def is_int(self, value):
            """Basic int validator func

            Args:
                value: value to validate

            Returns:
                ValidValue or InvalidValue
            """

            try:
                return ValidValue(int(value))
            except ValueError:
                return InvalidValue(value)

    def __new__(cls):  # Code needed to make Validator a singleton
        if not Validators.instance:
            Validators.instance = Validators.__Validators()
        return Validators.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)
