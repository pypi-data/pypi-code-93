"""曲线拟合"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def func(x, a, b, c):
    return a * x ** 2 + b * x + c


def poly_fit(x_values: list,
             y_values: list
             ):
    x_values_arr = np.array(x_values)
    y_values_arr = np.array(y_values)

    popt, pcov = curve_fit(func, x_values_arr, y_values_arr)
    # 获取popt里面是拟合系数
    print(popt)
    a = popt[0]
    b = popt[1]
    c = popt[2]
    yvals = func(x_values_arr, a, b, c)  # 拟合y值
    print('popt:', popt)
    print('系数a:', a)
    print('系数b:', b)
    print('系数c:', c)
    print('系数p cov:', pcov)
    print('系数y vals:', yvals)
    # 绘图
    plot1 = plt.plot(x_values_arr, y_values_arr, 's', label='original values')
    plot2 = plt.plot(x_values_arr, yvals, 'r', label='poly fit values')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend(loc=4)  # 指定legend的位置右下角
    plt.title('curve_fit')
    plt.show()
