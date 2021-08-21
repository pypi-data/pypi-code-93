# coding: utf-8
from kwhelp.rules import RuleAttrExist
from typing import Optional
from abc import ABC, abstractmethod
# region class HelperBase

class HelperBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        '''Class Constructor'''

    # region private methods

    def _get_type_error_method_msg(self, method_name: str, arg: object, arg_name: str, expected_type: str) -> str:
        result = f"{self.__class__.__name__}.{method_name}() arg '{arg_name}' is expecting type of '{expected_type}'. Got type of '{type(arg).__name__}'"
        return result

    def _get_value_error_msg(self, method_name: str, arg: object, arg_name: str, msg: str) -> str:
        result = f"{self.__class__.__name__}.{method_name}() arg '{arg_name}' {msg}"
        return result

    # region Property Helpers
    def _get_type_error_prop_msg(self, prop_name: str, value: object, expected_type: str) -> str:
        result = f"{self.__class__.__name__}.{prop_name} is expecting type of '{expected_type}'. Got type of '{type(value).__name__}'"
        return result

    def _isinstance_prop(self, value: object, prop_name: str, prop_type: object, raise_error: Optional[bool] = False):
        result = isinstance(value, prop_type)
        if result == False and raise_error == True:
            self._prop_error(prop_name=prop_name,
                             value=value, expected_type=self._get_name_type_obj(prop_type))
        return result

    def _prop_error(self, prop_name: str, value: object, expected_type: str):
        raise TypeError(self._get_type_error_prop_msg(
            prop_name=prop_name, value=value, expected_type=expected_type
        ))

    def _is_prop_str(self, value: object, prop_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_prop(
            value=value, prop_name=prop_name, prop_type=str, raise_error=raise_error)
        return result

    def _is_prop_bool(self, value: object, prop_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_prop(
            value=value, prop_name=prop_name, prop_type=bool, raise_error=raise_error)
        return result

    def _is_prop_int(self, value: object, prop_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_prop(
            value=value, prop_name=prop_name, prop_type=int, raise_error=raise_error)
        return result
    # endregion Property Helpers

    # region method Arg Helpers
    def _isinstance_method(self, method_name: str, arg: object, arg_name: str, arg_type: object, raise_error: Optional[bool] = False) -> bool:
        result = isinstance(arg, arg_type)
        if result == False and raise_error == True:
            self._arg_type_error(self._get_type_error_method_msg(
                method_name=method_name, arg=arg, arg_name=arg_name,
                expected_type=self._get_name_type_obj(
                    arg_type)
            ))
        return result

    def _is_arg_str(self, method_name: str, arg: object, arg_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_method(
            method_name=method_name, arg=arg, arg_name=arg_name, arg_type=str, raise_error=raise_error)
        return result
    
    def _is_arg_str_empty_null(self, method_name: str, arg: object, arg_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._is_arg_str(
            method_name=method_name, arg=arg, arg_name=arg_name, raise_error=raise_error)
        if result == False:
            return result
        _arg = str(arg).strip()
        if len(_arg) == 0:
            if raise_error:
                raise ValueError(self._get_value_error_msg(
                    method_name=method_name, arg=arg, arg_name=arg_name,
                    msg='empty or whitespace string is not allowed'
                ))
            result = False
        return result

    def _is_arg_bool(self, method_name: str, arg: object, arg_name: str, raise_error: Optional[bool] = False) -> bool:
        result = self._isinstance_method(
            method_name=method_name, arg=arg, arg_name=arg_name, arg_type=bool, raise_error=raise_error)
        return result
    # endregion method Arg Helpers

    def _arg_type_error(self, method_name: str, arg: object, arg_name: str, expected_type: str):
        raise TypeError(self._get_type_error_method_msg(
            method_name=method_name, arg=arg, arg_name=arg_name, expected_type=expected_type
        ))

    def _get_name_type_obj(self, obj: object) -> str:
        '''
        Gets the name of an object instance name or type name
        '''
        if isinstance(obj, type):
            return str(obj.__name__)
        return str(obj.__class__.__name__)
    # endregion private methods
# endregion class HelperBase
