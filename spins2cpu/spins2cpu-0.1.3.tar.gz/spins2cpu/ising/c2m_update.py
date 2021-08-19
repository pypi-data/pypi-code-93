import time
import numpy as np
from numba import njit
from spins2cpu import functions

def iteration3(latt, X_s, Y_s, Ja, Jb, J0, J1, val, nequilibrium, nworks):
    Nw = np.zeros((nworks, 8))
    Ew = np.zeros(nworks)
    t0 = time.time()
    for i in range(nequilibrium):
        randvals = np.random.rand(2, 4, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Ja, Jb, J0, J1, val)
    for i in range(nworks):
        randvals = np.random.rand(2, 4, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Ja, Jb, J0, J1, val)
        Ew[i] = E0 / 2
        Nw[i] = functions.Average(latt[0,0]), functions.Average(latt[0,1]), functions.Average(latt[0,2]), functions.Average(latt[0,3]),\
                functions.Average(latt[1,0]), functions.Average(latt[1,1]), functions.Average(latt[1,2]), functions.Average(latt[1,3])
    t = time.time() - t0
    return t, Nw, Ew

@njit(cache=True)
def update3(latt, randvals, X_s, Y_s, Ja, Jb, J0, J1, val):
    nn_sum = 0
    for l in range(2):
        for k in range(4):
            for j in range(Y_s):
                for i in range(X_s):
                    lo  = 1 - l
                    k1  = (k + 1) % 4
                    k2  = (k + 2) % 4
                    k3  = (k + 3) % 4
                    ipp = (i + 1) if (i + 1) < X_s else 0
                    inn = (i - 1) if (i - 1) > -1  else (X_s - 1)
                    jpp = (j + 1) if (j + 1) < Y_s else 0
                    jnn = (j - 1) if (j - 1) > -1  else (Y_s - 1)
                    if k == 0:
                        y_u  = jnn
                        y_d  = j
                        y_u2 = jnn
                        y_d2 = j
                    elif k == 1:
                        y_u  = j
                        y_d  = j
                        y_u2 = jnn
                        y_d2 = j
                    elif k == 2:
                        y_u  = j
                        y_d  = j
                        y_u2 = j
                        y_d2 = jpp
                    else:
                        y_u  = j
                        y_d  = jpp
                        y_u2 = j
                        y_d2 = jpp

                    if l == 0:
                        if k == 0 or k == 2:
                            x_p = i
                            x_o = inn
                            x_q = inn
                        else:
                            x_p = ipp
                            x_o = ipp
                            x_q = i
                    else:
                        if k == 0 or k == 2:
                            x_p = i
                            x_o = ipp
                            x_q = ipp
                        else:
                            x_p = inn
                            x_o = inn
                            x_q = i

                    energy = ( latt[l,k,j,i] * ( -Ja * ( latt[l ,k2,y_d2,i  ] + latt[l ,k2,y_u2,i  ] +
                                                         latt[l ,k1,y_d ,i  ] + latt[l ,k3,y_u ,i  ] +
                                                         latt[l ,k1,y_d ,x_o] + latt[l ,k3,y_u ,x_o] ) -
                                                  Jb * ( latt[l ,k ,jnn ,i  ] + latt[l ,k ,jpp ,i  ] +
                                                         latt[l ,k2,y_d2,inn] + latt[l ,k2,y_d2,ipp] +
                                                         latt[l ,k2,y_u2,inn] + latt[l ,k2,y_u2,ipp] ) -
                                                  J0 * ( latt[lo,k1,y_d ,i  ] + latt[lo,k3,y_u ,i  ] + latt[lo,k ,j   ,x_p] ) -
                                                  J1 * ( latt[lo,k2,y_d2,x_p] + latt[lo,k2,y_u2,x_p] + latt[lo,k ,j   ,x_q] ) ) )

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
