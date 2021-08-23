import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 10:
    raise SystemExit('This module need Python 3.10 or more later')

from math import *
import cmath as c

def run(mode='+', a=0, b=0):
    if a == 'pi':
        a = pi
    if b == 'pi':
        b = pi
    # pi
    if a == 'e':
        a = e
    if b == 'e':
        b = e
    # e
    if a == 'tau':
        a = tau
    if b == 'tau':
        b = tau
    # tau
    if a == 'inf':
        a = float('inf')
    if b == 'inf':
        b = float('inf')
    # inf
    if a == '-inf':
        a = float('-inf')
    if b == '-inf':
        b = float('-inf')
    # -inf
    if a == 'nan' or a == 'NaN':
        a = nan
    if b == 'nan' or b == 'NaN':
        b = nan
    # nan
    match mode:
        case '+':
            result = a + b
        case '-':
            result = a - b
        case '*':
            result = a * b
        case '/':
            result = a / b
        case '//':
            result = a // b
        case '...':
            result = a % b
        case '%':
            result = a % b
        # Operations
        case '>':
            if a > b:
                result = True
            else:
                result = False
        case '<':
            if a < b:
                result = True
            else:
                result = False
        case '==':
            if a == b:
                result = True
            else:
                result = False
        case '!=':
            if a != b:
                result = True
            else:
                result = False
        case '>=':
            if a >= b:
                result = True
            else:
                result = False
        case '<=':
            if a <= b:
                result = True
            else:
                result = False
        # Compare
        case '!':
            x = 1
            for y in range(1, a + 1):
                x = x * y
            result = x
        case '^':
            result = a ** b
        case 'square root':
            result = sqrt(a)
        case 'sqrt()':
            result = sqrt(a)
        # Power
        case 'exp()':
            result = exp(a)
        case 'exp1()':
            result = exp1(a)
        # Power And Logarithmic Functions
        case 'cos()':
            result = cos(a)
        case 'tan()':
            result = tan(a)
        case 'sin()':
            result = sin(a)
        case 'acos()':
            result = acos(a)
        case 'atan()':
            result = atan(a)
        case 'asin()':
            result = asin(a)
        case 'dist()':
            result = dist(a)
        case 'hypot()':
            result = hypot(a)
        # Trigonometric Function
        case 'cosh()':
            result = cosh(a)
        case 'tanh()':
            result = tanh(a)
        case 'sinh()':
            result = sinh(a)
        case 'acosh()':
            result = acosh(a)
        case 'atanh()':
            result = atanh(a)
        case 'asinh()':
            result = asinh(a)
        # Hyperbolic Functions
        case 'Degrees()':
            result = degrees(a)
        case 'degrees()':
            result = degrees(a)
        case 'Radians()':
            result = radians(a)
        case 'radians()':
            result = radians(a)
        # Angular Conversion
        case 'abs()':
            result = abs(a)
        # Else
        case 'Int / Float':
            if type(a) == type(1):
                result = float(a)
            elif type(a) == type(1.5):
                result = int(a)
            else:
                raise TypeError(''' 'Int / Float' object's argument must be int or float ''')
        case 'int / float':
            if type(a) == type(1):
                result = float(a)
            elif type(a) == type(1.5):
                result = int(a)
            else:
                raise TypeError(''' 'Int / Float' object's argument must be int or float ''')
        case 'Type':
            result = type(a)
        case 'type':
            result = type(a)
        # Type
        case _:
            raise AttributeError(''' 'run' object has no attribute '%s' ''' % mode)
    return result

def crun(mode, a, b):
    if a == 'pi':
        a = c.pi
    if b == 'pi':
        b = c.pi
    # pi
    if a == 'e':
        a = c.e
    if b == 'e':
        b = c.e
    # e
    if a == 'tau':
        a = c.tau
    if b == 'tau':
        b = c.tau
    # tau
    if a == 'inf':
        a = float('inf')
    if b == 'inf':
        b = float('inf')
    # inf
    if a == '-inf':
        a = float('-inf')
    if b == '-inf':
        b = float('-inf')
    # -inf
    if a == 'nan' or a == 'NaN':
        a = c.nan
    if b == 'nan' or b == 'NaN':
        b = c.nan
    # nan
    match mode:
        case 'cos()':
            return c.cos(a)
        case 'tan()':
            return c.tan(a)
        case 'sin()':
            return c.sin(a)
        case 'acos()':
            return c.cos(a)
        case 'atan()':
            return c.tan(a)
        case 'asin()':
            return c.sin(a)
        # Trigonometric Function
        case 'cosh()':
            return c.cos(a)
        case 'tanh()':
            return c.tan(a)
        case 'sinh()':
            return c.sin(a)
        case 'acosh()':
            return c.cos(a)
        case 'atanh()':
            return c.tan(a)
        case 'asinh()':
            return c.sin(a)
        # Hyperbolic Functions
        case _:
            raise AttributeError(''' 'crun' object has no attribute '%s' ''' % mode)

def mean(mode=''):
    match mode:
        case '+':
            message = 'Find the sum of A and B, indicating A plus B'
        case '-':
            message = 'Find the difference between A and B, which means A minus B'
        case '*':
            message = 'Find the product of A and B, representing A times B'
        case '/':
            message = 'The quotient of A and B, which means A divided by B'
        case '//':
            message = 'Find the integer part of a divided by B'
        case '...':
            message = 'Find the remainder of a divided by B'
        case '%':
            message = 'Find the remainder of a divided by B'
        # Operations
        case '>':
            message = 'Find whether A is greater than B. If yes, return True; If not, False is returned'
        case '<':
            message = 'Find whether A is less than B. If yes, return true; If not, false is returned'
        case '==':
            message = 'Find whether A is equal to B. If yes, return true; If not, false is returned'
        case '>=':
            message = 'Find whether A is greater than or equal to B. If yes, return true; If not, false is returned'
        case '<=':
            message = 'Find whether A is less than or equal to B. If yes, return true; If not, false is returned'
        case '!=':
            message = 'Find whether A is not equal to B. If yes, return true; If not, false is returned'
        # Compare
        case '!':
            message = 'Find the factorial of A'
        case '^':
            message = 'Seeking the b-th of a'
        case 'sqrt()':
            message = 'Find the square root of A'
        # Power
        case 'cos()':
            message = 'Return the cosine of x radians'
        case 'sin()':
            message = 'Return the sine of x radians'
        case 'tan()':
            message = 'Return the tangent of x radians'
        case 'acos()':
            message = 'Return the arc cosine of A, in radians'
        case 'asin()':
            message = 'Return the arc sine of A, in radians'
        case 'atan()':
            message = 'Return the arc tangent of A, in radians'
        case 'dist()':
            message = 'Return the Euclidean distance between two points A and B, \n each given as a sequence (or iterable) of coordinates. \n The two points must have the same dimension'
        case 'hypot()':
            message = '''Return the Euclidean norm,
sqrt(sum(A**2 for A in coordinates)).
This is the length of the vector from the origin to the point given by the coordinates.
For a two dimensional point (A, B),
this is equivalent to computing the hypotenuse of a right triangle using the Pythagorean theorem, sqrt(A*A + B*B)'''
        # Trigonometric Function
        case 'acosh()':
            message = 'Return the inverse hyperbolic cosine of A'
        case 'asinh()':
            message = 'Return the inverse hyperbolic sine of A'
        case 'atanh()':
            message = 'Return the inverse hyperbolic tangent of A'
        case 'cosh()':
            message = 'Return the hyperbolic cosine of A'
        case 'sinh()':
            message = 'Return the hyperbolic sine of A'
        case 'tanh()':
            message = 'Return the hyperbolic tangent of A'
        # Hyperbolic Functions
        case 'exp()':
            message = 'Return e raised to the power A, where e = 2.718281… is the base of natural logarithms. \n This is usually more accurate than math.e ** A or pow(math.e, A)'
        case 'expm1()':
            message = '''Return e raised to the power A, minus 1.
Here e is the base of natural logarithms.
For small floats A, the subtraction in exp(A) - 1 can result in a significant loss of precision;
the expm1() function provides a way to compute this quantity to full precision:

>>> from math import exp, expm1
>>> exp(1e-5) - 1  # gives result accurate to 11 places
1.0000050000069649e-05
>>> expm1(1e-5)    # result accurate to full precision
1.0000050000166668e-05'''
        # Power And Logarithmic Functions
        case 'Degrees()':
            message = 'Convert angle A from radians to degrees'
        case 'degrees()':
            message = 'Convert angle A from radians to degrees'
        case 'Radians()':
            message = 'Convert angle A from degrees to radians'
        case 'radians()':
            message = 'Convert angle A from degrees to radians'
        # Angular Conversion
        case 'abs()':
            message = 'Return the absolute value of a'
        # Else
        case 'Int / Float':
            message = 'Force integer A to be converted to decimal, or convert decimal A to integer ( Note: if the decimal part of A is 0, A will be converted to decimal x.0 )'
        case 'int / float':
            message = 'Force integer A to be converted to decimal, or convert decimal A to integer ( Note: if the decimal part of A is 0, A will be converted to decimal x.0 )'
        case 'Type':
            message = 'Returns the type of A, integer returns Int, decimal returns Float \n ( Note: if decimal part is 0, Int is returned )'
        case 'type':
            message = 'Returns the type of A, integer returns Int, decimal returns Float \n ( Note: if decimal part is 0, Int is returned )'
        # Type
        case _:
            raise AttributeError(''' 'mean' object has no attribute '%s' ''' % mode)

def list():
    a = '''
+, -, *, /, //, ..., %,
^, sqrt(), sqare root,
exp(), exp1(),
cos(), tan(), sin(),
acos(), atan(), asin(),
cosh(), tanh(), sinh(),
acosh(), atanh(), asinh(),
abs(),
Int / Float, Type
'''
    print(a)
