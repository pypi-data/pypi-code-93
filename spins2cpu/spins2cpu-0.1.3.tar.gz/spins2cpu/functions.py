import numpy as np
from numba import njit

def Average(arr):
    return np.sum(arr) / arr.size

def Average2(arr):
    return np.sum(arr**2) / arr.size

def Normalrand(Y, X):
    arr = np.random.randn(3, X, Y)
    arr = arr / np.sqrt(arr[0]**2 + arr[1]**2 + arr[2]**2)
    return arr.T

@njit(cache=True)
def NormalrandN(n, Y, X):
    arr = np.zeros((n, Y, X, 3))
    for i in range(n):
        arr_t = np.random.randn(3, X, Y)
        arr_t = arr_t / np.sqrt(arr_t[0]**2 + arr_t[1]**2 + arr_t[2]**2)
        arr[i] = arr_t.T
    return arr

@njit(cache=True)
def NormalrandNN(n, m, Y, X):
    arr = np.zeros((n, m, Y, X, 3))
    for i in range(n):
        for j in range(m):
            arr_t = np.random.randn(3, X, Y)
            arr_t = arr_t / np.sqrt(arr_t[0]**2 + arr_t[1]**2 + arr_t[2]**2)
            arr[i,j] = arr_t.T
    return arr

def Onesint(Y, X):
    return np.ones((Y, X)).astype(np.int8)

def Onesint3(Z, Y, X):
    return np.ones((Z, Y, X)).astype(np.int8)

def Onesint4(n, Z, Y, X):
    return np.ones((n, Z, Y, X)).astype(np.int8)

def Onesint5(n, m, Z, Y, X):
    return np.ones((n, m, Z, Y, X)).astype(np.int8)

def Onesint6(o, n, m, Z, Y, X):
    return np.ones((o, n, m, Z, Y, X)).astype(np.int8)

def OnesZ(Y, X):
    arr = np.zeros((Y, X, 3))
    arr[:,:,2] = 1
    return arr

def OnesZN(n, Y, X):
    arr = np.zeros((n, Y, X, 3))
    arr[:,:,:,2] = 1
    return arr

def OnesZNN(n, m, Y, X):
    arr = np.zeros((n, m, Y, X, 3))
    arr[:,:,:,:,2] = 1
    return arr

def Uniformint(Y, X):
    return (2 * (np.random.randint(0, 2, (Y, X)) - 0.5)).astype(np.int8)

def Uniformint3(Z, Y, X):
    return (2 * (np.random.randint(0, 2, (Z, Y, X)) - 0.5)).astype(np.int8)

def Uniformint4(n, Z, Y, X):
    return (2 * (np.random.randint(0, 2, (n, Z, Y, X)) - 0.5)).astype(np.int8)

def Uniformint5(n, m, Z, Y, X):
    return (2 * (np.random.randint(0, 2, (n, m, Z, Y, X)) - 0.5)).astype(np.int8)

def Uniformint6(o, n, m, Z, Y, X):
    return (2 * (np.random.randint(0, 2, (o, n, m, Z, Y, X)) - 0.5)).astype(np.int8)
