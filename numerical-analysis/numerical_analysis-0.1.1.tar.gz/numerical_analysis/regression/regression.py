import numpy as np
from numerical_analysis.root_finding.root_finding import newton_raphson_2x2


def least_squares(points, method, n=2):

    def linear():
        nonlocal points, n
        n = 1
        return polynomial()

    def polynomial():
        nonlocal points, n

        A = np.zeros((n + 1, n + 1))

        for i in range(n + 1):
            for j in range(i, n + 1):
                for point in points:
                    A[i][j] += point[0] ** (i + j)

        for i in range(n + 1):
            for j in range(i):
                A[i][j] = A[j][i]

        B = np.zeros(n + 1)

        for i in range(n + 1):
            for point in points:
                B[i] += point[1] * point[0] ** i

        return np.linalg.solve(A, B)

    def exponential():
        nonlocal points

        def sigma(fun, a, b):
            nonlocal points
            return sum([fun(a, b, point[0], point[1]) for point in points])

        def f(a, b):
            def function(a, b, x, y):
                return x * a ** (2 * x - 1) + x * b * a ** (x - 1) - x * y * a ** (x - 1)
            return sigma(function, a, b)

        def g(a, b):
            def function(a, b, x, y):
                return a ** x + b - y
            return sigma(function, a, b)

        def fa(a, b):
            def function(a, b, x, y):
                return x * (2 * x - 1) * a ** (2 * x - 2) + x * (x - 1) * b * a ** (x - 2) - x * (x - 1) * y * a ** (
                            x - 2)
            return sigma(function, a, b)

        def fb(a, b):
            def function(a, b, x, y):
                return x * a ** (x - 1)
            return sigma(function, a, b)

        def ga(a, b):
            def function(a, b, x, y):
                return x * a ** (x - 1)
            return sigma(function, a, b)

        def gb(a, b):
            def function(a, b, x, y):
                return 1
            return sigma(function, a, b)

        return newton_raphson_2x2(f, g, fa, fb, ga, gb, 1., 1.)

    def logarithmic():
        nonlocal points
        # Swap axes of points set, and solve the inverted problem
        for item in points:
            item[0], item[1] = item[1], item[0]
        coefficients = exponential()
        # Retrieve original points table
        for item in points:
            item[0], item[1] = item[1], item[0]
        return coefficients

    if method == "linear":  # Returns b and a coefficients of the equation {y = a * x + b}
        return linear()
    elif method == "polynomial":  # Returns polynomial's coefficients
        return polynomial()
    elif method == "exponential":  # Returns a and b of the exponential equation {y = a^x+b}
        return exponential()
    elif method == "logarithmic":  # Returns base a and b of the logarithmic equation {y = loga(x-b)}
        return logarithmic()


def linear_regression(points):
    return least_squares(points, "linear")

