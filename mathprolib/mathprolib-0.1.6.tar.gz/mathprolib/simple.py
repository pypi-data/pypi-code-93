# Version: Test
# Author:LAI-1048576,Toby-LAI
# -*- coding:utf-8 -*-

import math
from functools import total_ordering,reduce
from operator import and_,mul
from Inf_digits_float import InfDigitsFloat
REAL = float
Ф = (math.sqrt(5) - 1) / 2
γ = 0.5772156649015328
true_pi_1000 = "3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461284756482337867831652712019091456485669234603486104543266482133936072602491412737245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094330572703657595919530921861173819326117931051185480744623799627495673518857527248912279381830119491298336733624406566430860213949463952247371907021798609437027705392171762931767523846748184676694051320005681271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235420199561121290219608640344181598136297747713099605187072113499999983729780499510597317328160963185950244594553469083026425223082533446850352619311881710100031378387528865875332083814206171776691473035982534904287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989"
def getPi(numbers = 1000):
    return InfDigitsFloat(true_pi_1000[:number+3])
def deg(num):
    return num*180/math.pi
def rad(num):
    return num/180*math.pi
def sin(x):
    return math.sin(rad(n))

def cos(x):
    return math.cos(rad(n))
# 因为我突然想到了tan90,所以做了这个更新

def tan(n):
    if n % 180 == 90:
        raise ValueError("tan90?")
    return math.tan(rad(n))
sinr,cosr,tanr = math.sin,math.cos,math.tan
asin,acos,atan = math.asin,math.acos,math.atan
ln,log,log2 = math.log,math.log10,math.log2
π,e = math.pi,math.e
def fact(num):
    assert num >= 0 ,"Cannot get factorail to negative number"
    assert num == int(num),"the number should be int(or int-like float) not other"
    result = 1
    for i in range(int(num)):
        result *= i
    return result  # python3.9不支持math.factorail
def gcd(x, y):
    smaller = x if x < y else y
    g = [i for i in range(1,smaller+1) if x % i == 0 and y % i == 0][-1]
    return g

def lcm(x, y):
    return x*y//gcd(x,y)
@total_ordering
class INF:
    def __lt__(self, other):
        return False

    def __eq__(self, other):
        return isinstance(other, INF)

    def __str__(self):
        return "∞"

    def __neg__(self):
        return NEGINF()


@total_ordering
class NEGINF:
    def __lt__(self, other):
        return True

    def __eq__(self, other):
        return isinstance(other, NEGINF)

    def __str__(self):
        return "∞"


Infinity = INF()


def root(num: REAL, exp: REAL):
    """

    :rtype: REAL
    :param num: 开方底数
    :param exp: 开方指数
    :return: 结果

    """
    result = num ** (1 / exp)
    if not isinstance(result, complex):
        return num ** (1 / exp)
    else:
        return math.nan


def sqrt(num: REAL):
    """

    :param num:要开方的数
    :return: 结果
    """
    return root(num, 2)


def calculate(equation:str):
    return eval(equation.replace("÷","/").replace("^","**"))


def fibonacci(num:int):
    b = 0
    temp = 1
    for _ in range(num):
        yield temp
        a = b
        b = temp
        temp = a+b


def isOdd(num:int) -> bool:
    return num % 2 == 1


def isEven(num:int) -> bool:
    return num % 2 == 0


def isPrime(num:int) -> bool:
    return not reduce(and_,[num % i == 0 for i in range(2,int(sqrt(num))+1)])


def product(iterable):
    return reduce(mul,iterable)

