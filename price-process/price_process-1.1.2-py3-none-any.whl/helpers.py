import numpy as np
from scipy.stats import levy_stable, norm
from scipy.signal import convolve2d
import matplotlib.pyplot as plt


def moving_average(x, w):
    if len(x.shape) == 1:
        return np.convolve(x, np.ones(w), 'valid') / w
    elif len(x.shape) == 2:
        return convolve2d(x,np.ones([w, len(x[0, :])]))/w


def dist(i, j):
    return np.sqrt(i ** 2 + j ** 2)


def normalize(vec):
    return vec/np.max(np.abs(vec))


def integer_difference(vec, t, n=1):
    if len(vec) != len(t):
        raise IndexError("lengths of vector and index must match")
    dvec = vec
    for i in range(0, n):
        dvec = np.diff(np.append([dvec[0]], dvec))/abs(t[1]-t[0])
    return dvec

def shift(arr, num, fill_value=0):
    # https://www.delftstack.com/howto/numpy/python-numpy-shift-array/
    result = np.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result[:] = arr
    return result



def autocorr(x, lag):
    lag = int(lag)
    return np.corrcoef(np.array([x[:-lag], x[lag:]]))
