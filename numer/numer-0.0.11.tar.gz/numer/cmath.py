import ctypes as c

_lib = c.CDLL("lib.so")

_lib.fcos.argtypes = (c.c_double, c.c_char)
_lib.fcos.restype = c.c_double

_lib.fsin.argtypes = (c.c_double, c.c_char)
_lib.fsin.restype = c.c_double

_lib.ftan.argtypes = (c.c_double, c.c_char)
_lib.ftan.restype = c.c_double

_lib.fatan.argtypes = (c.c_double, c.c_char)
_lib.fatan.restype = c.c_double

_lib.facos.argtypes = (c.c_double, c.c_char)
_lib.facos.restype = c.c_double

_lib.fasin.argtypes = (c.c_double, c.c_char)
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

    if not ((isinstance(angle, float) or isinstance(angle, int)) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fcos(angle, radian)


def sin(angle: float, radian: bool = True) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(angle, float) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fsin(angle, radian)


def tan(angle: float, radian: bool = True) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(angle, float) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.ftan(angle, radian)


def acos(angle: float, radian: bool = True) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(angle, float) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.facos(angle, radian)


def asin(angle: float, radian: bool = True) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(angle, float) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fasin(angle, radian)


def atan(angle: float, radian: bool = True) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(angle, float) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fatan(angle, radian)


def cosh(angle: float, radian: bool = True) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(angle, float) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fcosh(angle, radian)


def sinh(angle: float, radian: bool = True) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(angle, float) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fsinh(angle, radian)


def tanh(angle: float, radian: bool = True) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(angle, float) and isinstance(radian, bool)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.ftan(angle, radian)

def pow(base: float, exponent: float) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(base, float) and isinstance(exponent, float)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.pow(base, exponent)

def log10(number: float) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(number, float) and number > 0):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.log10(number)

def ceil(number: float) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(number, float)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fceil(number)

def ln(number: float) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(number, float) and number > 0):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.log(number)

def exp(number: float) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(number, float)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fexp(number)

def floor(number: float) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(number, float)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.ffloor(number)

def abs(number: float) -> float:
    '''Returns the cosine of the angle'''

    if not isinstance(number, float):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.ffabs(number)

def sqrt(number: float) -> float:
    '''Returns the cosine of the angle'''

    if not (isinstance(number, float) and number > 0):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.sqrt(number)

def mod(num1: float, num2: float) -> float:
    '''Returns the cosine of the angle'''
    print('fdfds')
    if not (isinstance(num1, float) and isinstance(num2, float)):
        raise ValueError(
            "Angle has to be a float, radian has to be an boolean")

    return _lib.fmod(num1, num2)



if __name__ == "__main__":
    pass
