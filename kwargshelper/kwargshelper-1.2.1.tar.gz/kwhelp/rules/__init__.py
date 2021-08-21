# coding: utf-8
from abc import ABC, abstractmethod
import numbers

# region Interface


class IRule(ABC):
    def __init__(self, key: str, name: str, value: object, raise_errors: bool, originator: object) -> None:
        self._name: str = name
        self._value: object = value
        self._key: str = key
        self._raise_errors = raise_errors
        self._originator = originator

    # region Abstract Methods
    @abstractmethod
    def validate(self) -> bool:
        '''Gets attrib field and value are valid'''
    # endregion Abstract Methods

    def _get_type_error_msg(self, arg: object, arg_name: str, expected_type: str) -> str:
        result = f"Argument Error: '{arg_name}' is expecting type of '{expected_type}'. Got type of '{type(arg).__name__}'"
        return result
    # region Properties

    @property
    def field_name(self) -> str:
        '''The name of the field that value was assigned'''
        return self._name

    @property
    def field_value(self) -> object:
        '''The value that is assigned to `field_name`'''
        return self._value

    @property
    def key(self) -> str:
        '''Gets the key currently being read'''
        return self._key

    @property
    def raise_errors(self) -> bool:
        '''Gets if a rule could raise an error when validation fails'''
        return self._raise_errors

    @property
    def originator(self) -> object:
        '''Gets object that attributes validated for '''
        return self._originator
    # endregion Properties
# endregion Interface

# region Attrib rules


class RuleAttrNotExist(IRule):
    '''
    Rule to ensure an attribute does not exist before it is added to class.

    If `raise_errors` is `True` the following errors may be raised:
    * AttributeError
    '''

    def validate(self) -> bool:
        result = not hasattr(self.originator, self.field_name)
        if result == False and self.raise_errors == True:
            raise AttributeError(
                f"'{self.field_name}' attribute already exist in current instance of '{type(self.originator).__name__}'")
        return result


class RuleAttrExist(IRule):
    '''
    Rule to ensure an attribute does exist before its value is set.

    If `raise_errors` is `True` the following errors may be raised:
    * AttributeError
    '''

    def validate(self) -> bool:
        result = hasattr(self.originator, self.field_name)
        if result == False and self.raise_errors == True:
            raise AttributeError(
                f"'{self.field_name}' attribute does not exist in current instance of '{type(self.originator).__name__}'")
        return result
# endregion Attrib rules

# region None


class RuleNotNone(IRule):
    '''
    Rule to ensure the value of `None` is not assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * ValueError
    '''

    def validate(self) -> bool:
        if self.field_value is None:
            if self.raise_errors:
                raise ValueError(
                    f"Arg error: {self.key} must be assigned a value")
            return False
        return True

# endregion None

# region Number


class RuleNumber(IRule):
    '''
    Rule to ensure a number is assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * TypeError
    '''

    def validate(self) -> bool:
        # isinstance(False, int) is True
        # print(int(True)) 1
        # print(int(False)) 0
        if not isinstance(self.field_value, numbers.Number) or isinstance(self.field_value, bool):
            if self.raise_errors:
                raise TypeError(self._get_type_error_msg(
                    self.field_value, self.key, 'Number'))
            return False
        return True

# region Integer


class RuleInt(IRule):
    '''
    Rule to ensure a positive integer is assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * TypeError
    '''

    def validate(self) -> bool:
        # isinstance(False, int) is True
        # print(int(True)) 1
        # print(int(False)) 0
        if not isinstance(self.field_value, int) or isinstance(self.field_value, bool):
            if self.raise_errors:
                raise TypeError(self._get_type_error_msg(
                    self.field_value, self.key, 'int'))
            return False
        return True


class RuleIntPositive(IRule):
    '''
    Rule to ensure a positive integer is assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * ValueError
    '''

    def validate(self) -> bool:
        if not isinstance(self.field_value, int):
            return False
        if self.field_value < 0:
            if self.raise_errors:
                raise ValueError(
                    f"Arg error: '{self.key}' must be a positive int value")
            return False
        return True


class RuleIntNegative(IRule):
    '''
    Rule to ensure a negative integer is assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * ValueError
    '''

    def validate(self) -> bool:
        if not isinstance(self.field_value, int):
            return False
        if self.field_value >= 0:
            if self.raise_errors:
                raise ValueError(
                    f"Arg error: '{self.key}' must be a negative int value")
            return False
        return True

# endregion Integer

# region Float Rules


class RuleFloat(IRule):
    '''
    Rule to ensure a float is assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * TypeError
    '''

    def validate(self) -> bool:
        if not isinstance(self.field_value, float):
            if self.raise_errors:
                raise TypeError(self._get_type_error_msg(
                    self.field_value, self.key, 'float'))
            return False


class RuleFloatPositive(IRule):
    '''
    Rule to ensure a positive float is assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * ValueError
    '''

    def validate(self) -> bool:
        if self.field_value < 0.0:
            if self.raise_errors:
                raise ValueError(
                    f"Arg error: '{self.key}' must be a positive float value")
            return False
        return True


class RuleFloatNegative(IRule):
    '''
    Rule to ensure a negative float is assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * TypeError
    * ValueError
    '''

    def validate(self) -> bool:
        if self.field_value >= 0.0:
            if self.raise_errors:
                raise ValueError(
                    f"Arg error: '{self.key}' must be a negative float value")
            return False
        return True

# endregion Float Rules

# endregion Number

# region String


class RuleStr(IRule):
    '''
    Rule to ensure a str is assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * TypeError
    '''

    def validate(self) -> bool:
        '''
        Validates rule
        @eturns: `True` if validation is a success.
        If validaton fails adn `raise_errors` is `True` and error will be raised;
        Otherwise `False`
        '''
        if not isinstance(self.field_value, str):
            if self.raise_errors:
                raise TypeError(self._get_type_error_msg(
                    self.field_value, self.key, 'str'))
            return False
        return True


class RuleStrNotNullOrEmpty(IRule):
    '''
    Rule to ensure a string that is not empty or whitespace is assigned to attribute.

    If `raise_errors` is `True` the following errors may be raised:
    * ValueError
    '''

    def validate(self) -> bool:
        '''
        Validates rule
        @eturns: `True` if validation is a success.
        If validaton fails adn `raise_errors` is `True` and error will be raised;
        Otherwise `False`
        '''
        if not isinstance(self.field_value, str):
            return False
        value = self.field_value.strip()
        if len(value) == 0:
            if self.raise_errors:
                raise ValueError(
                    f"Arg error: {self.key} must not be empty or whitespace")
            return False
        return True
# endregion String

# region boolean


class RuleBool(IRule):
    def validate(self) -> bool:
        if not isinstance(self.field_value, bool):
            if self.raise_errors:
                raise TypeError(self._get_type_error_msg(
                    self.field_value, self.key, 'bool'))
            return False
        return True
# endregion boolean
