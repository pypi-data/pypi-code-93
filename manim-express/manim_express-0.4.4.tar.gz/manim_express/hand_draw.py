import numpy as np
import random
import math


def random_trigonometric(x, n=5, w_min=1, w_max=20, intensity=0.003):
    # theta = np.linspace(0, np.pi * 2, N)
    N = len(x)
    delta_w = w_max - w_min
    wave = np.array([0.] * N)
    for i in range(n):
        w = w_min + random.random() * delta_w
        phi = np.random.rand() * 2 * np.pi * w
        pth_pwave = np.sin(w * x + phi) * intensity
        wave += pth_pwave
    return wave


def rand_func(point, n=5, w_min=1, w_max=20, intensity=0.003):
    delta_w = w_max - w_min
    wave = 0
    for i in range(n):
        w = w_min + random.random() * delta_w
        phi = np.random.rand() * 2 * np.pi * w
        pth_pwave = math.sin(w * point + phi) * intensity
        wave += pth_pwave
    return wave
