import math
import numpy as np


class Polynomial:

    def __init__(self, coefficients: np.array):

        self.c = coefficients
        self.n = len(coefficients) - 1

    def value(self, x):
        return self.c.dot(np.array([x ** i for i in range(self.n + 1)]))

    def derivative(self):
        return Polynomial(np.delete(np.array([i for i in range(self.n + 1)]) * self.c, 0))

    def indefinite_integral(self):
        return Polynomial(np.insert(self.c / np.array([i + 1 for i in range(self.n + 1)]), 0, 0))

    def definite_integral(self, a, b):
        return self.indefinite_integral().value(b) - self.indefinite_integral().value(a)

    def graph(self, a, b, step):
        return [[x, self.value(x)] for x in np.arange(a, b + step, step)]

    @classmethod
    def product(cls, *input_polynomials):

        p = [polynomial.c for polynomial in input_polynomials]

        while len(p) > 1:

            n1 = len(p[-2]) - 1
            n2 = len(p[-1]) - 1

            p_temp = [0] * (n1 + n2 + 1)

            for i in range(n1 + 1):
                for j in range(n2 + 1):
                    p_temp[i + j] += p[-2][i] * p[-1][j]

            del p[-2:]

            p.append(p_temp)

        return cls(p[0])

    @classmethod
    def legendre(cls, n):

        c = np.array([0.] * (n + 1))

        for m in range(n // 2 + 1):
            c[n - 2 * m] = (-1) ** m * math.factorial(2 * n - 2 * m) / \
                           (2 ** n * math.factorial(m) * math.factorial(n - m) * math.factorial(n - 2 * m))
        return cls(c)

    @classmethod
    def lagrange(cls, x):

        n = x.size
        lagrange_polynomial = []

        for i in range(n):
            monomials = []
            for j in range(n):
                if j != i:
                    denominator = x[i] - x[j]
                    monomials.append(cls(np.array([-x[j] / denominator, 1 / denominator])))

            lagrange_polynomial.append(cls.product(*monomials))

        return lagrange_polynomial
