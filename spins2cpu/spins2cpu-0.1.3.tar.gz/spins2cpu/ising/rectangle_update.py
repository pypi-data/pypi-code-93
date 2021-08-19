import time
import numpy as np
from numba import njit
from spins2cpu import functions

def iteration5(latt, X_s, Y_s, Ja, Jb, Jc, Jd, Je, val, nequilibrium, nworks):
    Nw = np.zeros((nworks, 16))
    Ew = np.zeros(nworks)
    t0 = time.time()
    for i in range(nequilibrium):
        randvals = np.random.rand(4, 4, Y_s, X_s)
        E0 = update5(latt, randvals, X_s, Y_s, Ja, Jb, Jc, Jd, Je, val)
    for i in range(nworks):
        randvals = np.random.rand(4, 4, Y_s, X_s)
        E0 = update5(latt, randvals, X_s, Y_s, Ja, Jb, Jc, Jd, Je, val)
        Ew[i] = E0 / 2
        Nw[i] = functions.Average(latt[0,0]), functions.Average(latt[0,1]), functions.Average(latt[0,2]), functions.Average(latt[0,3]),\
                functions.Average(latt[1,0]), functions.Average(latt[1,1]), functions.Average(latt[1,2]), functions.Average(latt[1,3]),\
                functions.Average(latt[2,0]), functions.Average(latt[2,1]), functions.Average(latt[2,2]), functions.Average(latt[2,3]),\
                functions.Average(latt[3,0]), functions.Average(latt[3,1]), functions.Average(latt[3,2]), functions.Average(latt[3,3])
    t = time.time() - t0
    return t, Nw, Ew

@njit(cache=True)
def update5(latt, randvals, X_s, Y_s, Ja, Jb, Jc, Jd, Je, val):
    nn_sum = 0
    for l in range(4):
        for k in range(4):
            for j in range(Y_s):
                for i in range(X_s):
                    l1  = (l + 1) % 4
                    l2  = (l + 2) % 4
                    l3  = (l + 3) % 4
                    k1  = (k + 1) % 4
                    k2  = (k + 2) % 4
                    k3  = (k + 3) % 4
                    ipp = (i + 1) if (i + 1) < X_s else 0
                    inn = (i - 1) if (i - 1) > -1  else (X_s - 1)
                    jpp = (j + 1) if (j + 1) < Y_s else 0
                    jnn = (j - 1) if (j - 1) > -1  else (Y_s - 1)
                    if l == 0:
                        y_u  = jnn
                        y_d  = j
                        y_u2 = jnn
                        y_d2 = j
                    elif l == 1:
                        y_u  = j
                        y_d  = j
                        y_u2 = jnn
                        y_d2 = j
                    elif l == 2:
                        y_u  = j
                        y_d  = j
                        y_u2 = j
                        y_d2 = jpp
                    else:
                        y_u  = j
                        y_d  = jpp
                        y_u2 = j
                        y_d2 = jpp

                    if k == 0:
                        x_l  = inn
                        x_r  = i
                        x_l2 = inn
                        x_r2 = i
                    elif k == 1:
                        x_l  = i
                        x_r  = i
                        x_l2 = inn
                        x_r2 = i
                    elif k == 2:
                        x_l  = i
                        x_r  = i
                        x_l2 = i
                        x_r2 = ipp
                    else:
                        x_l  = i
                        x_r  = ipp
                        x_l2 = i
                        x_r2 = ipp

                    energy = latt[l,k,j,i] * ( -Ja * ( latt[l ,k3,j   ,x_l ] + latt[l ,k1,j   ,x_r ] ) -
                                                Jb * ( latt[l3,k ,y_u ,i   ] + latt[l1,k ,y_d ,i   ] ) -
                                                Jc * ( latt[l3,k3,y_u ,x_l ] + latt[l3,k1,y_u ,x_r ] + latt[l1,k3,y_d ,x_l] + latt[l1,k1,y_d ,x_r] ) -
                                                Jd * ( latt[l ,k2,j   ,x_l2] + latt[l ,k2,j   ,x_r2] ) -
                                                Je * ( latt[l2,k ,y_u2,i   ] + latt[l2,k ,y_d2,i   ] ) )

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
