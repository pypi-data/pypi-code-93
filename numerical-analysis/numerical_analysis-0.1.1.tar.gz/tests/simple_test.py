import numpy as np
import numerical_analysis as na

import datetime


def f(x):
    return (x - 1) ** 2 - 3 * x


def df_dx(x):
    return 2 * x - 5


cp = np.array([[1., 3.],
               [2., 4.],
               [3., 5.],
               [4., 1.],
               [5., 1.]])

bezier = na.splines.Bezier(cp)
bezier.plot(0.01)

comp_bezier = na.splines.CompositeQuadraticBezier(cp)
comp_bezier.plot(0.01)

xa = 0.
xb = 10.
n = 10000
level = 10

a = datetime.datetime.now()

print(na.integration.trapezoid(f, xa, xb, n))
print(na.integration.simpson1_3(f, xa, xb, n))
print(na.integration.simpson3_8(f, xa, xb, n))
print(na.integration.romberg(f, xa, xb, level))
print(na.integration.gauss_legendre(f, xa, xb, 8))


b = datetime.datetime.now()
c = b - a
print("Time taken by function: {} milliseconds".format(1e3 * c.total_seconds()))

print(na.root_finding.secant(f, 0, 1))
print(na.root_finding.newton_raphson(f, df_dx, 0))
