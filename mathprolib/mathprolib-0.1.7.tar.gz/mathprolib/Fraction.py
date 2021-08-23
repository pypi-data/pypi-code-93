from functools import total_ordering
from logging import warning as warn
from math import floor


class CalculateError(Exception):
    pass


class Fraction(object):
    @staticmethod
    def log(*args):
        if len(args) == 0:
            return
        line1 = ''
        line2 = ''
        line3 = ''
        for msg in args:
            if isinstance(msg, Fraction):
                temp = (len(str(max(msg._numerator, msg.denominator)))) // 2 + 1
                line1 += ' ' * temp
                line1 += str(msg._numerator) + ' ' * temp
                line3 += ' ' * temp
                line3 += str(msg.denominator) + ' ' * temp
                line2 += ' ' * temp + '—' * temp + ' '
            else:
                line1 += ' ' * len(str(msg))
                line3 += ' ' * len(str(msg))
                line2 += str(msg)
        if line1.strip() != '':
            print(line1)
        print(line2)
        if line3.strip() != '':
            print(line3)

    def __gongyue(self, a, b):
        a, aa, b, bb = abs(a), a / abs(a), abs(b), b / abs(b)
        while b != 0:
            temp = a % b
            a = b
            b = temp
        return a * aa * bb

    def __init__(self, _numerator, denominator):
        if denominator == 0: 
            raise CalculateError("fatal error:Denominator = 0")
        self._numerator = _numerator
        self.denominator = denominator

    # 只有满足交换律的才能使用self.__r..__ = self.__..__

    def __float__(self):
        temp = self._numerator / self.denominator
        if not isinstance(temp, float):
            temp = float(temp)
        return temp

    def __int__(self):
        return int(float(self))

    def general(self, factor):
        self._numerator *= factor
        self.denominator *= factor

    def isSimple(self):
        return self.__gongyue(self.numerator, self.denominator) == 1

    def all(self):
        return self._numerator, self.denominator

    def reduction(self, factor=None):
        if factor is None:
            factor = self.__gongyue(self._numerator, self.denominator)
        if self._numerator / factor != floor(self._numerator / factor) or self.denominator / factor != floor(
                self.denominator / factor):
            warn(f"Reduction failed.Cannot reduction by {factor}")
            return
        self._numerator //= factor
        self.denominator //= factor

    def common(self, other):
        if type(other) != int and (not isinstance(other, Fraction)) and type(other) != float:
            raise TypeError(
                f"can only concatenate Fraction (not {type(other)}) to Fraction")
        else:
            if isinstance(other, float):
                ofra = VulgarFraction(
                    self.denominator * other, self.denominator)
            elif isinstance(other, float):
                l = 10 ** len(str(other).split(".")[1])
                ofra = VulgarFraction(int(other * l), l)
                ofra.reduction()
                p = ofra.denominator * \
                    self.denominator // self.__gongyue(
                    ofra.denominator, self.denominator)
                self._numerator *= p // self.denominator
                ofra._numerator *= p // ofra.denominator
                self.denominator, ofra.denominator = p, p
            else:
                if isinstance(other, MixedFraction):
                    ofra = other.toVulgar()
                else:
                    ofra = VulgarFraction(other._numerator, other.denominator)
                p = ofra.denominator * \
                    self.denominator // self.__gongyue(
                    ofra.denominator, self.denominator)
                self._numerator *= p // self.denominator
                ofra._numerator *= p // ofra.denominator
                self.denominator, ofra.denominator = p, p
            return ofra


@total_ordering
class VulgarFraction(Fraction):
    def __init__(self, numerator, denominator):
        super().__init__(numerator, denominator)
        self.numerator = numerator
        self.denominator = denominator
        self.__radd__ = self.__add__
        self.__rmul__ = self.__mul__

    def toMixed(self):
        temp = MixedFraction(0, 0, self.denominator)
        temp.numerator = self.numerator
        return temp

    @property
    def numerator(self):
        return self._numerator

    @numerator.setter
    def numerator(self, value):
        self._numerator = value

    def __repr__(self):
        if self.numerator == self.denominator:
            return '1'
        if self.numerator == 0:
            return '0'
        if self.denominator == 1:
            return str(self.numerator)
        return f" {self.numerator}\n{('—' * (len(str(max(self.numerator, self.denominator))) + 2))}\n {self.denominator}"

    def __pos__(self):
        return self

    def __neg__(self):
        return VulgarFraction(-self.numerator, self.denominator)

    def __add__(self, other):
        if type(other) == MixedFraction:
            other = MixedFraction(
                other.integer, other.numerator, other.denominator).toVulgar()
        fra = VulgarFraction(self.numerator, self.denominator)
        if type(other) == int:
            fra.numerator += other * fra.denominator
        elif type(other) == float or isinstance(other, Fraction):
            temp = fra.common(other).numerator
            fra.numerator += temp
        else:
            raise TypeError(
                f"can only concatenate Fraction (not {type(other)}) to Fraction")
        fra.reduction()
        return fra

    def __sub__(self, other):
        if type(other) == MixedFraction:
            other = MixedFraction(
                other.integer, other.numerator, other.denominator).toVulgar()
        fra = VulgarFraction(self.numerator, self.denominator)
        if type(other) == int:
            fra.numerator -= other * fra.denominator
        elif type(other) == float or isinstance(other, Fraction):
            temp = fra.common(other).numerator
            fra.numerator -= temp
        else:
            raise TypeError(
                f"can only concatenate Fraction (not {type(other)}) to Fraction")
        fra.reduction()
        return fra

    def __rsub__(self, other):
        return -(self - other)

    def __rtruediv__(self, other):
        return (self / other).rec()

    def __mul__(self, other):
        if type(other) == MixedFraction:
            other = MixedFraction(
                other.integer, other.numerator, other.denominator).toVulgar()
        fra = VulgarFraction(self.numerator, self.denominator)
        if type(other) == int:
            fra.numerator *= other
        elif type(other) == float or isinstance(other, Fraction):
            temp = fra.common(other)
            fra.numerator *= temp.numerator
            fra.denominator *= temp.denominator
        else:
            raise TypeError(
                f"can only concatenate Fraction (not {type(other)}) to Fraction")
        fra.reduction()
        return fra

    def __truediv__(self, other):
        if type(other) == MixedFraction:
            other = MixedFraction(
                other.integer, other.numerator, other.denominator).toVulgar()
        fra = VulgarFraction(self.numerator, self.denominator)
        if type(other) == int:
            fra.denominator *= other
        elif type(other) == float or isinstance(other, Fraction):
            temp = fra.common(other)
            fra.numerator *= temp.denominator
            fra.denominator *= temp.numerator
        else:
            raise TypeError(
                f"can only concatenate Fraction (not {type(other)}) to Fraction")
        fra.reduction()
        return fra

    def __eq__(self, other):
        fra = VulgarFraction(self.numerator, self.denominator)
        if type(other) == MixedFraction:
            otr = other.toVulgar()
            otr = fra.common(otr)
        else:
            otr = fra.common(other)
        return fra.numerator == otr.numerator

    def __lt__(self, other):
        fra = VulgarFraction(self.numerator, self.denominator)
        if type(other) == MixedFraction:
            otr = other.toVulgar()
            otr = fra.common(otr)
        else:
            otr = fra.common(other)
        return fra.numerator < otr.numerator

    def irec(self):  # 你这个是直接赋值，return的是None啊
        self.numerator, self.denominator = self.denominator, self.numerator

    def rec(self):  # 有返回值的倒数
        return VulgarFraction(self.denominator, self.numerator)

    def __pow__(self, other):
        if isinstance(other, (VulgarFraction, int, float)):
            return VulgarFraction(self.numerator ** float(other), self.denominator ** float(other))
        elif isinstance(other, MixedFraction):
            return self ** other.toVulgar()
        else:
            raise CalculateError

    def __mod__(self, other):
        otr = self.common(other)
        return VulgarFraction((self.numerator % otr.numerator), otr.denominator)

    def __floordiv__(self, other):
        return (self / other).__int__()

    def __abs__(self):
        return VulgarFraction(abs(self.numerator), abs(self.denominator))

    def __call__(self, numerator, denominator, *args):
        if args:
            raise CalculateError("only 2 arguments")
        self.denominator = denominator
        self.numerator = numerator

    def __complex__(self):
        return eval(f"{self.numerator}+{self.denominator}i")

    def __format__(self, format_spec):
        format_spec = int(format_spec)
        if format_spec == 0:
            return str(self)
        elif format_spec == 1:
            return f"{self.numerator}/{self.denominator}"
        elif format_spec == 2:
            return f"{self.numerator}÷{self.denominator}"


@total_ordering
class MixedFraction(Fraction):
    def __init__(self, integer, numerator, denominator):
        if int(integer) != integer:
            raise CalculateError("integer should be int(or int-like float)")
        if numerator >= denominator:
            raise CalculateError(
                "Numerator should be smaller than denominator")
        if integer < 0:
            raise CalculateError(
                "fatal error:Calculate failed.Cause integer < 0")
        super().__init__(numerator, denominator)
        self.integer = integer
        self.__radd__ = self.__add__
        self.__rmul__ = self.__mul__

    def __eq__(self, other):
        fra = MixedFraction(self.integer, self.numerator,
                            self.denominator).toVulgar()
        otr = fra.common(other)
        return fra == otr

    def __lt__(self, other):
        fra = MixedFraction(self.integer, self.numerator,
                            self.denominator).toVulgar()
        otr = fra.common(other)
        return fra < otr

    def toVulgar(self):
        num = self.integer * self.denominator + self.numerator
        f = VulgarFraction(num, self.denominator)
        return f

    def all(self):
        return (self.integer, self.numerator, self.denominator)

    def irec(self):
        fra = MixedFraction(self.integer, self.numerator,
                            self.denominator).toVulgar()
        fra.irec()
        self.integer = 0
        self.denominator = fra.denominator
        self.numerator = fra.numerator

    def rec(self):
        temp = self
        temp.irec()
        return temp

    @property
    def numerator(self):
        return self._numerator

    def __mod__(self, other):
        return float(self) % float(other)

    @numerator.setter
    def numerator(self, value):
        nm = value

        def itg():
            nonlocal self
            nonlocal nm
            temp = nm // self.denominator
            if temp > 0:
                nm -= self.denominator * temp
                self.integer += temp

        if nm >= self.denominator:
            itg()
        elif nm < 0:
            nm += self.integer * self.denominator
            self.integer = 0
            itg()
        else:
            pass
        self._numerator = nm
        self.reduction()

    def __str__(self):
        if self.numerator == 0:
            return str(self.integer)
        return f"{' ' * len(str(self.integer)) if self.integer != 0 else ''}{self.numerator}\n{self.integer if self.integer != 0 else ''}{'—' * len(str(max(self.numerator, self.denominator)))}\n{' ' * len(str(self.integer)) if self.integer != 0 else ''}{self.denominator}"

    def __add__(self, other):
        fra = MixedFraction(self.integer, self.numerator,
                            self.denominator).toVulgar()
        return (fra + other).toMixed()

    def __sub__(self, other):
        fra = MixedFraction(self.integer, self.numerator,
                            self.denominator).toVulgar()
        return (fra - other).toMixed()

    def __mul__(self, other):
        fra = MixedFraction(self.integer, self.numerator,
                            self.denominator).toVulgar()
        return (fra * other).toMixed()

    def __truediv__(self, other):
        fra = MixedFraction(self.integer, self.numerator,
                            self.denominator).toVulgar()
        return (fra / other).toMixed()

    def __rsub__(self, other):

        return -(self - other)

    def __rtruediv__(self, other):
        return (self / other).rec()

    def __call__(self, integer, numerator, denominator, *args):
        if args:
            raise CalculateError('only 3 arguments')
        self.integer = integer
        self.denominator = denominator
        self.numerator = numerator


class ComplexFraction(Fraction):
    def __init__(self, numerator: complex, denominator: complex):
        super().__init__(numerator, denominator)
        self.numerator = numerator
        self.denominator = denominator

    def common(self, other):
        def is_int(number):
            return abs(number-round(number)) == 0
        
        def complex_to_complex_fraction(number):
            pass  # 没做完
        
        def is_complex_int(number:complex):
            return is_int(number.imag) and is_int(number.real)


if __name__ == "__main__":
    a = VulgarFraction(10, 20)
    print(
        format(a, "1")
    )
