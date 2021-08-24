from math import factorial

import matplotlib.pyplot as plt
import numpy as np

from numerical_analysis.dependencies import GeometricalPlace
from numerical_analysis.dependencies import Polynomial
from numerical_analysis.root_finding import newton_raphson


class Bezier(GeometricalPlace):

    def __init__(self, control_points: np.array, datatype=np.float):
        super().__init__()
        self.datatype = datatype
        self.cp = control_points
        self.n = len(self.cp) - 1
        self.m = self.matrix(self.n, self.datatype)
        self.c = self.polynomial_coefficients()
        self.polynomials = {"x": Polynomial(self.c[0]),
                            "y": Polynomial(self.c[1]),
                            "dx/dt": Polynomial(self.c[0]).derivative(),
                            "dy/dt": Polynomial(self.c[1]).derivative(),
                            "p": [Polynomial(self.m[i]) for i in range(self.n + 1)]}

    def polynomial_coefficients(self):
        c = np.empty([2, self.n + 1], dtype=self.datatype)
        for k in range(2):
            c[k] = np.matmul(np.transpose(self.m), self.cp[:, k])
        return c

    def y_x(self, x, error=1e-14):
        t0 = newton_raphson(lambda t: self.x_t(t) - x, self.dx_dt, 0.5, error)
        return self.y_t(t0)

    def x_t(self, t):
        return self.polynomials["x"].value(t)

    def y_t(self, t):
        return self.polynomials["y"].value(t)

    def dx_dt(self, t):
        return self.polynomials["dx/dt"].value(t)

    def dy_dt(self, t):
        return self.polynomials["dy/dt"].value(t)

    def p_i(self, i, t):
        return self.polynomials["p"][i].value(t)

    def graph_cp(self):
        return [[self.cp[j, i] for j in range(len(self.cp))] for i in range(len(self.cp[0]))]

    def plot(self, dt):
        graph = self.graph(dt)
        # noinspection PyUnresolvedReferences
        plt.plot(graph[0], graph[1], self.graph_cp()[0], self.graph_cp()[1])
        plt.show()

    def update(self):
        self.c = self.polynomial_coefficients()
        self.polynomials = {"x": Polynomial(self.c[0]),
                            "y": Polynomial(self.c[1]),
                            "dx/dt": Polynomial(self.c[0]).derivative(),
                            "dy/dt": Polynomial(self.c[1]).derivative(),
                            "p": [Polynomial(self.m[i]) for i in range(self.n + 1)]}

    def modify_control_point(self, i, new_control_point):
        self.cp[i][0] = new_control_point[0]
        self.cp[i][1] = new_control_point[1]
        self.update()

    def modify_control_point_coordinate(self, i, k, new_control_point_coordinate):
        self.cp[i, k] = new_control_point_coordinate
        self.update()

    def refresh_control_points(self, control_points):
        self.cp = control_points
        self.update()

    def append_control_point(self, new_control_point):
        self.cp = np.append(self.cp, [new_control_point], axis=0)
        self.update()

    def change_datatype(self, datatype):
        self.datatype = datatype
        self.cp = self.cp.astype(datatype)
        self.m = self.m.astype(datatype)
        self.c = self.c.astype(datatype)

    @classmethod
    def matrix(cls, n, datatype=np.int):
        return np.array([[((-1) ** (j - i) * factorial(n)) /
                          (factorial(i) * factorial(j - i) * factorial(n - j))
                          if j >= i else 0. for j in range(n + 1)] for i in range(n + 1)], dtype=datatype)
