import ctypes as c
import os

_lib = c.CDLL(os.path.join(os.path.dirname(__file__), "lib.dylib"))

_lib.fcos.argtypes = (c.c_double, c.c_char)
_lib.fcos.restype = c.c_double

_lib.fsin.argtypes = (c.c_double, c.c_char)
_lib.fsin.restype = c.c_double

_lib.ftan.argtypes = (c.c_double, c.c_char)
_lib.ftan.restype = c.c_double

_lib.fatan.argtypes = (c.c_double)
_lib.fatan.restype = c.c_double

_lib.facos.argtypes = (c.c_double)
_lib.facos.restype = c.c_double

_lib.fasin.argtypes = (c.c_double)
_lib.fasin.restype = c.c_double

_lib.fcosh.argtypes = (c.c_double, c.c_char)
_lib.fcosh.restype = c.c_double

_lib.fsinh.argtypes = (c.c_double, c.c_char)
_lib.fsinh.restype = c.c_double

_lib.ftanh.argtypes = (c.c_double, c.c_char)
_lib.ftanh.restype = c.c_double

_lib.fpow.argtypes = (c.c_double, c.c_char)
_lib.fpow.restype = c.c_double

_lib.flog10.argtypes = (c.c_double,)
_lib.flog10.restype = c.c_double

_lib.flog.argtypes = (c.c_double,)
_lib.flog.restype = c.c_double

_lib.fexp.argtypes = (c.c_double,)
_lib.fexp.restype = c.c_double

_lib.fceil.argtypes = (c.c_double,)
_lib.fceil.restype = c.c_double

_lib.ffabs.argtypes = (c.c_double,)
_lib.ffabs.restype = c.c_double

_lib.fsqrt.argtypes = (c.c_double,)
_lib.fsqrt.restype = c.c_double

_lib.floor.argtypes = (c.c_double,)
_lib.floor.restype = c.c_double

_lib.ffmod.argtypes = (c.c_double,)
_lib.ffmod.restype = c.c_double


def cos(angle: float, radian: bool = True) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(angle, (float, int)) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float or an int, radian has to be an boolean")

    return _lib.fcos(angle, radian)


def sin(angle: float, radian: bool = True) -> float:
    '''Returns the sine of the angle'''

    if not (isinstance(angle, (float, int)) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float or an int, radian has to be an boolean")

    return _lib.fsin(angle, radian)


def tan(angle: float, radian: bool = True) -> float:
    '''Returns the tangent of the angle'''

    if not (isinstance(angle, (float, int)) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float or an int, radian has to be an boolean")

    return _lib.ftan(angle, radian)


def acos(value: float) -> float:
    '''Returns the arccosine of the value'''

    if not isinstance(value, (float, int)):
        raise ValueError(
            "Value has to be a float or an int")

    return _lib.facos(value)


def asin(value: float) -> float:
    '''Returns the arcsine of the value'''

    if not (isinstance(value, float)):
        raise ValueError(
            "Value has to be a float or an int")

    return _lib.fasin(value)


def atan(value: float) -> float:
    '''Returns the arctangent of the value'''

    if not (isinstance(value, float)):
        raise ValueError(
            "Value has to be a float or an int")

    return _lib.fatan(value)


def cosh(angle: float, radian: bool = True) -> float:
    '''Returns the hyperbolic cosine of the angle'''

    if not (isinstance(angle, (float, int)) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fcosh(angle, radian)


def sinh(angle: float, radian: bool = True) -> float:
    '''Returns the hyperbolic sine of the angle'''

    if not (isinstance(angle, (float, int)) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fsinh(angle, radian)


def tanh(angle: float, radian: bool = True) -> float:
    '''Returns the hyperbolic tangent of the angle'''

    if not (isinstance(angle, (float, int)) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.ftan(angle, radian)


def pow(base: float, exponent: float) -> float:
    '''Returns base^exponent'''

    if not (isinstance(base, (float, int)) and isinstance(exponent, (float, int))):
        raise ValueError(
            "base and exponent has to be a float or an int")

    return _lib.fpow(base, exponent)


def log10(number: float) -> float:
    '''Returns the base 10 log of the number'''

    if not (isinstance(number, (float, int)) and number > 0):
        raise ValueError(
            "number has to be a float or an int")

    return _lib.flog10(number)


def ceil(number: float) -> float:
    '''Rounds the number up and returns the rounded value'''

    if not (isinstance(number, (float,int))):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fceil(number)


def ln(number: float) -> float:
    '''Returns the natural logarithm of the number'''

    if not (isinstance(number, (float,int)) and number > 0):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.flog(number)


def exp(number: float) -> float:
    '''Returns the cosine of the angle'''

    if not isinstance(number, (float,int)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fexp(number)


def floor(number: float) -> float:
    '''Returns the cosine of the angle'''

    if not isinstance(number, (float,int)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.ffloor(number)


def abs(number: float) -> float:
    '''Returns the absolute value of the number'''

    if not isinstance(number, (float,int)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.ffabs(number)


def sqrt(number: float) -> float:
    '''Returns the square root of the number'''

    if not (isinstance(number, float) and number > 0):
        raise ValueError(
            "number has to be a float or an int")

    return _lib.fsqrt(number)


def mod(num1: float, num2: float) -> float:
    '''Returns num1 modulo num2'''

    if not (isinstance(num1, float) and isinstance(num2, float)):
        raise ValueError(
            "num1 and num2 have to be floats or ints")

    return _lib.fmod(num1, num2)


if __name__ == "__main__":
    pass
