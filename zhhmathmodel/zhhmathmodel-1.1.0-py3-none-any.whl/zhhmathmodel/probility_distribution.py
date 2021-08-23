import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import os


def fit_gaussian_distribution(ls: list, file_name: str, path: str):
    """
    拟合一个数字列表的高斯分布图像，保存文件
    :param ls: 数字列表
    :param file_name: 要保存的文件名
    :param path: 保存路径
    :return: None
    """
    x = np.array(ls)

    # n, bins, patches = plt.hist(x, 20, density=1, facecolor='blue', alpha=0.75)  #第二个参数是直方图柱子的数量
    mu = np.mean(x)  # 计算均值
    sigma = np.std(x)
    num_bins = 30  # 直方图柱子的数量
    n, bins, patches = plt.hist(x, num_bins, density=1, alpha=0.75)
    # 直方图函数，x为x轴的值，normed=1表示为概率密度，即和为一，绿色方块，色深参数0.5.返回n个概率，直方块左边线的x值，及各个方块对象
    y = norm.pdf(bins, mu, sigma)  # 拟合一条最佳正态分布曲线y

    plt.grid(True)
    plt.plot(bins, y, 'r--')  # 绘制y的曲线
    plt.xlabel('values')  # 绘制x轴
    plt.ylabel('Probability')  # 绘制y轴
    plt.title('Histogram : $\mu$=' + str(round(mu, 2)) + ' $\sigma=$' + str(round(sigma, 2)))  # 中文标题 u'xxx'
    # plt.subplots_adjust(left=0.15)#左边距
    create_dir_not_exist(path)
    plt.savefig(path + "/" + file_name + ".png", bbox_inches="tight")


def create_dir_not_exist(path: str):
    """create dir if not exist"""
    if not os.path.exists(path):
        os.mkdir(path)
