import time
import numpy as np
from numba import njit
from spins2cpu import functions


def looping(latt, X, Y, Ja, val, nequilibrium):
    t0 = time.time()
    for i in range(nequilibrium):
        cluster(latt, X, Y, Ja, val)
    t = time.time() - t0
    return t, functions.Average(latt)

@njit(cache=True)
def cluster(latt, X, Y, Ja, val):
    k = np.random.randint(0, 3)
    j = np.random.randint(0, Y)
    i = np.random.randint(0, X)
    P_add = 1 - np.exp( 2 * val * -abs(Ja) )
    lable = np.ones((3, Y, X)).astype(np.int8)
    stack = [(k,j,i)]
    lable[k,j,i] = 0
    while len(stack) > 0:
        current = stack.pop()
        sign = latt[current]
        k, j, i = current
        jpp = (j + 1) if (j + 1) < Y  else 0
        jnn = (j - 1) if (j - 1) > -1 else (Y - 1)
        ipp = (i + 1) if (i + 1) < X  else 0
        inn = (i - 1) if (i - 1) > -1 else (X - 1)
        if k == 0:
            neighbor_0 = (1, j, i)
            neighbor_1 = (2, j, i)
            neighbor_2 = (1, jpp, inn)
            neighbor_3 = (2, jpp, i)
        elif k == 1:
            neighbor_0 = (0, j, i)
            neighbor_1 = (2, j, i)
            neighbor_2 = (0, jnn, ipp)
            neighbor_3 = (2, j, ipp)
        else:
            neighbor_0 = (0, j, i)
            neighbor_1 = (1, j, i)
            neighbor_2 = (0, jnn, i)
            neighbor_3 = (1, j, inn)

        latt[current] *= -1
        if Ja > 0:
            if latt[neighbor_0] == sign and lable[neighbor_0] and np.random.rand() < P_add:
                stack.append(neighbor_0)
                lable[neighbor_0] = 0
            if latt[neighbor_1] == sign and lable[neighbor_1] and np.random.rand() < P_add:
                stack.append(neighbor_1)
                lable[neighbor_1] = 0
            if latt[neighbor_2] == sign and lable[neighbor_2] and np.random.rand() < P_add:
                stack.append(neighbor_2)
                lable[neighbor_2] = 0
            if latt[neighbor_3] == sign and lable[neighbor_3] and np.random.rand() < P_add:
                stack.append(neighbor_3)
                lable[neighbor_3] = 0
        else:
            if latt[neighbor_0] == -sign and lable[neighbor_0] and np.random.rand() < P_add:
                stack.append(neighbor_0)
                lable[neighbor_0] = 0
            if latt[neighbor_1] == -sign and lable[neighbor_1] and np.random.rand() < P_add:
                stack.append(neighbor_1)
                lable[neighbor_1] = 0
            if latt[neighbor_2] == -sign and lable[neighbor_2] and np.random.rand() < P_add:
                stack.append(neighbor_2)
                lable[neighbor_2] = 0
            if latt[neighbor_3] == -sign and lable[neighbor_3] and np.random.rand() < P_add:
                stack.append(neighbor_3)
                lable[neighbor_3] = 0

def iteration(latt, X, Y, Ja, val, nequilibrium, nworks):
    Nw = np.zeros((nworks, 3))
    Ew = np.zeros(nworks)
    t0 = time.time()
    for i in range(nequilibrium):
        randvals = np.random.rand(3, Y, X)
        E0 = update(latt, randvals, X, Y, Ja, val)
    for i in range(nworks):
        randvals = np.random.rand(3, Y, X)
        E0 = update(latt, randvals, X, Y, Ja, val)
        Ew[i] = E0 / 2
        Nw[i] = functions.Average(latt[0]), functions.Average(latt[1]), functions.Average(latt[2])
    t = time.time() - t0
    return t, Nw, Ew

@njit(cache=True)
def update(latt, randvals, X, Y, Ja, val):
    nn_sum = 0
    for k in range(3):
        for j in range(Y):
            for i in range(X):
                ipp = (i + 1) if (i + 1) < X  else 0
                inn = (i - 1) if (i - 1) > -1 else (X - 1)
                jpp = (j + 1) if (j + 1) < Y  else 0
                jnn = (j - 1) if (j - 1) > -1 else (Y - 1)
                if k == 0:
                    energy = latt[0,j,i] * ( -Ja * ( latt[1,j,i] + latt[2,j,i] +
                                                     latt[1,jpp,inn] + latt[2,jpp,i] ) )
                elif k == 1:
                    energy = latt[1,j,i] * ( -Ja * ( latt[0,j,i] + latt[2,j,i] +
                                                     latt[0,jnn,ipp] + latt[2,j,ipp] ) )
                else:
                    energy = latt[2,j,i] * ( -Ja * ( latt[0,j,i] + latt[1,j,i] +
                                                     latt[0,jnn,i] + latt[1,j,inn] ) )

                if val == 0:
                    if energy < 0:
                        pass
                    else:
                        latt[k,j,i] *= -1
                else:
                    if energy < 0:
                        if randvals[k,j,i] < np.exp( 2.0 * val * energy ):
                            latt[k,j,i] *= -1
                    else:
                        latt[k,j,i] *= -1

                nn_sum += energy
    return nn_sum
