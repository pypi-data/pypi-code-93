import time
import numpy as np
from numba import njit
from spins2cpu import functions

def iteration3(latt, X_s, Y_s, Ja, J0, J1, val, nequilibrium, nworks):
    Nw = np.zeros((nworks, 8))
    Ew = np.zeros(nworks)
    t0 = time.time()
    for i in range(nequilibrium):
        randvals = np.random.rand(2, 4, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Ja, J0, J1, val)
    for i in range(nworks):
        randvals = np.random.rand(2, 4, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Ja, J0, J1, val)
        Ew[i] = E0 / 2
        Nw[i] = functions.Average(latt[0,0]), functions.Average(latt[0,1]), functions.Average(latt[0,2]), functions.Average(latt[0,3]),\
                functions.Average(latt[1,0]), functions.Average(latt[1,1]), functions.Average(latt[1,2]), functions.Average(latt[1,3])
    t = time.time() - t0
    return t, Nw, Ew

@njit(cache=True)
def update3(latt, randvals, X_s, Y_s, Ja, J0, J1, val):
    nn_sum = 0
    for l in range(2):
        for k in range(4):
            for j in range(Y_s):
                for i in range(X_s):
                    lo  = 1 - l
                    k1  = 3 - k
                    k2  = (5 - k) if k > 1 else (1 - k)
                    k3  = (2 - k) if k%2 == 0 else (4 - k)
                    ipp = (i + 1) if (i + 1) < X_s else 0
                    inn = (i - 1) if (i - 1) > -1  else (X_s - 1)
                    jpp = (j + 1) if (j + 1) < Y_s else 0
                    jnn = (j - 1) if (j - 1) > -1  else (Y_s - 1)
                    if k == 0:
                        x_inn = i
                        x_ipp = ipp
                        y_jnn = j
                        y_jpp = jpp
                    elif k == 1:
                        x_inn = i
                        x_ipp = ipp
                        y_jnn = jnn
                        y_jpp = j
                    elif k == 2:
                        x_inn = inn
                        x_ipp = i
                        y_jnn = jnn
                        y_jpp = j
                    else:
                        x_inn = inn
                        x_ipp = i
                        y_jnn = j
                        y_jpp = jpp

                    if l == 0:
                        if k == 0:
                            i_1 = i
                            j_2 = jpp
                            x_0 = i
                            x_1 = i
                            x_2 = ipp
                            y_0 = j
                            y_1 = jpp
                            y_2 = jpp
                        elif k == 1:
                            i_1 = i
                            j_2 = j
                            x_0 = i
                            x_1 = i
                            x_2 = ipp
                            y_0 = jnn
                            y_1 = j
                            y_2 = j
                        elif k == 2:
                            i_1 = inn
                            j_2 = j
                            x_0 = inn
                            x_1 = inn
                            x_2 = i
                            y_0 = jnn
                            y_1 = j
                            y_2 = j
                        else:
                            i_1 = inn
                            j_2 = jpp
                            x_0 = inn
                            x_1 = inn
                            x_2 = i
                            y_0 = j
                            y_1 = jpp
                            y_2 = jpp
                    else:
                        if k == 0:
                            i_1 = ipp
                            j_2 = j
                            x_0 = ipp
                            x_1 = ipp
                            x_2 = i
                            y_0 = jpp
                            y_1 = j
                            y_2 = j
                        elif k == 1:
                            i_1 = ipp
                            j_2 = jnn
                            x_0 = ipp
                            x_1 = ipp
                            x_2 = i
                            y_0 = j
                            y_1 = jnn
                            y_2 = jnn
                        elif k == 2:
                            i_1 = i
                            j_2 = jnn
                            x_0 = i
                            x_1 = i
                            x_2 = inn
                            y_0 = j
                            y_1 = jnn
                            y_2 = jnn
                        else:
                            i_1 = i
                            j_2 = j
                            x_0 = i
                            x_1 = i
                            x_2 = inn
                            y_0 = jpp
                            y_1 = j
                            y_2 = j

                    energy = ( latt[l,k,j,i] * ( -Ja * ( latt[l ,k1,j    ,x_ipp] + latt[l ,k1,j    ,x_inn] +
                                                         latt[l ,k2,y_jpp,i    ] + latt[l ,k2,y_jnn,i    ] +
                                                         latt[l ,k3,y_jnn,x_inn] + latt[l ,k3,y_jpp,x_ipp] ) -
                                                  J0 * ( latt[lo,k ,j    ,i    ] + latt[lo,k1,j    ,i_1  ] + latt[lo,k2,j_2,i  ] ) -
                                                  J1 * ( latt[lo,k3,y_0  ,x_0  ] + latt[lo,k3,y_1  ,x_1  ] + latt[lo,k3,y_2,x_2] ) ) )

                    if val == 0:
                        if energy < 0:
                            pass
                        else:
                            latt[l,k,j,i] *= -1
                    else:
                        if energy < 0:
                            if randvals[l,k,j,i] < np.exp( 2.0 * val * energy ):
                                latt[l,k,j,i] *= -1
                        else:
                            latt[l,k,j,i] *= -1

                    nn_sum += energy
    return nn_sum
