import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize


def f(x, k, b):
    """线性函数"""
    return k * x + b


def draw_scatter(x_values, y_values):
    """
    绘制离散点集
    :param x_values: List
    :param y_values: List
    :return: None
    """
    plt.scatter(x_values[:], y_values[:], 3, "red")


def fit_and_draw_line(x_values, y_values, step: int):
    """
    直线拟合与绘制
    :param x_values:
    :param y_values:
    :param step: 步长
    :return: dict
    """
    k, b = optimize.curve_fit(f, x_values, y_values)[0]
    x1 = np.arange(int(min(x_values)), int(max(x_values)) + 1, step)  # 要对应x的两个端点，1为步长
    y1 = k * x1 + b
    plt.plot(x1, y1, "blue")
    plt.title("title")
    plt.xlabel('x_value')
    plt.ylabel('y_value')
    plt.show()
    return {"系数k": k, "常数b": b}
