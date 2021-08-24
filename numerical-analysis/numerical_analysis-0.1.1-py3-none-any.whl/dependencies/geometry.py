import math

import matplotlib.pyplot as plt
import numpy as np

from numerical_analysis.dependencies import Polynomial


class GeometricalPlace:

    def __init__(self):
        pass

    def x_t(self, t):
        return

    def y_t(self, t):
        return

    def point_t(self, t):
        return [self.x_t(t), self.y_t(t)]

    def graph(self, dt):
        graph = [[], []]
        for t in np.arange(0., 1. + dt, dt):
            for k in range(2):
                graph[k].append(self.point_t(t)[k])
        return graph

    def plot(self, dt):
        graph = self.graph(dt)
        plt.plot(graph[0], graph[1])
        plt.show()


class StraightLine(GeometricalPlace):

    def __init__(self, points):
        # points given in following format: [[t0, [x0, y0]], [t1, [x1, y1]]]
        self.points = points
        self.c = self.coefficients()
        super().__init__()

    def coefficients(self):
        t0 = self.points[0][0]
        t1 = self.points[1][0]

        x0 = self.points[0][1][0]
        x1 = self.points[1][1][0]

        y0 = self.points[0][1][1]
        y1 = self.points[1][1][1]

        a = (x1 - x0) / (t1 - t0)
        b = (x0 * t1 - x1 * t0) / (t1 - t0)
        c = (y1 - y0) / (t1 - t0)
        d = (y0 * t1 - y1 * t0) / (t1 - t0)

        return np.array([[b, a], [d, c]])

    def x_t(self, t):
        return Polynomial(self.c[0]).value(t)

    def y_t(self, t):
        return Polynomial(self.c[1]).value(t)

    def slope_rad(self):
        if self.x_t(1.) != self.x_t(0.):
            phi = math.atan((self.y_t(1.) - self.y_t(0.)) / (self.x_t(1.) - self.x_t(0.)))
            if self.x_t(1.) > self.x_t(0.):
                return phi
            else:
                return phi + math.pi
        elif self.y_t(1.) > self.y_t(0.):
            return math.pi / 2
        else:
            return 3 * math.pi / 2

    # noinspection PyMethodOverriding
    def graph(self, ta, tb):
        def invert_table(table):
            return [[table[j][i] for j in range(len(table))] for i in range(len(table[0]))]
        return invert_table([self.point_t(ta), self.point_t(tb)])

    def modify_points(self, points):
        self.points = points
        self.c = self.coefficients()


class Circle(GeometricalPlace):

    def __init__(self, center, radius):
        self.C = center
        self.R = radius
        super().__init__()

    def x_t(self, angle_rad):
        return self.R * math.cos(angle_rad) + self.C[0]

    def y_t(self, angle_rad):
        return self.R * math.sin(angle_rad) + self.C[1]
