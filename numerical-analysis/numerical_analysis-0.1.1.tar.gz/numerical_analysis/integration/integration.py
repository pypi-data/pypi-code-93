import numpy as np
from numerical_analysis.dependencies import Polynomial
from numerical_analysis.root_finding import newton_raphson_multiple_roots


def trapezoid(f, xs, xn, n):

    def dI():
        nonlocal xa, xb
        return (xb - xa) * (f(xa) + f(xb)) / 2

    I = 0
    dx = (xn - xs) / n

    for i in range(n):

        xa = xs + i * dx
        xb = xs + (i + 1) * dx

        I += dI()

    return I


def simpson1_3(f, xs, xn, n):

    def dI():
        nonlocal xa, xb

        x0 = xa
        x1 = (xa + xb) / 2
        x2 = xb

        return (xb - xa) * (f(x0) + 4 * f(x1) + f(x2)) / 6

    I = 0
    dx = (xn - xs) / n

    for i in range(n):

        xa = xs + i * dx
        xb = xs + (i + 1) * dx

        I += dI()

    return I


def simpson3_8(f, xs, xn, n):

    def dI():
        nonlocal xa, xb

        h = (xb - xa) / 3

        x0 = xa
        x1 = xa + h
        x2 = xb - h
        x3 = xb

        return (xb - xa) * (f(x0) + 3 * f(x1) + 3 * f(x2) + f(x3)) / 8

    I = 0
    dx = (xn - xs) / n

    for i in range(n):

        xa = xs + i * dx
        xb = xs + (i + 1) * dx

        I += dI()

    return I


def romberg(f, x0, xn, level):

    dx = (xn-x0)/2**(level-1)
    Irom = []
    xs = [x0 for i in range(level)]

    for i in range(level):
        Irom.append([])
        for j in range(level - i):
            Irom[i].append(0)

    for i in range(1, 2**(level-1) + 1):
        xi = x0 + i*dx
        for j in range(level):
            if i % 2**(level - (j+1)) == 0:
                Irom[j][0] += trapezoid(f, xs[j], xi, 1)
                xs[j] = xi

    for j in range(1, level):
        for i in range(level - j):
            Irom[i][j] = (4 ** j * Irom[i + 1][j - 1] - Irom[i][j - 1]) / (4 ** j - 1)

    return Irom[0][-1]


def gauss_legendre(f, x0, xn, n):

    p = Polynomial.legendre(n+1)

    x = newton_raphson_multiple_roots(p.value, p.derivative().value, p.n, 1e-14)
    L = Polynomial.lagrange(np.array(x))
    w = []

    for i in range(n+1):
        w.append(L[i].definite_integral(-1, 1))

    I = 0.
    for i in range(n+1):
        I += w[i]*f((x[i] * (xn - x0) + xn + x0) / 2)

    I *= 0.5 * (xn - x0)

    return I
