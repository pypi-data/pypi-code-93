import time
import numpy as np
from numba import njit
from spins2cpu import functions

def iteration3(latt, X_s, Y_s, Z_s, Ja, Jb, Jc, val, nequilibrium, nworks):
    Nw = np.zeros((nworks, 8))
    Ew = np.zeros(nworks)
    t0 = time.time()
    for i in range(nequilibrium):
        randvals = np.random.rand(2, 2, 2, Z_s, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Z_s, Ja, Jb, Jc, val)
    for i in range(nworks):
        randvals = np.random.rand(2, 2, 2, Z_s, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Z_s, Ja, Jb, Jc, val)
        Ew[i] = E0 / 2
        Nw[i] = functions.Average(latt[0,0,0]), functions.Average(latt[1,1,0]), functions.Average(latt[0,1,1]), functions.Average(latt[1,0,1]),\
                functions.Average(latt[0,1,0]), functions.Average(latt[1,0,0]), functions.Average(latt[0,0,1]), functions.Average(latt[1,1,1])
    t = time.time() - t0
    return t, Nw, Ew

@njit(cache=True)
def update3(latt, randvals, X_s, Y_s, Z_s, Ja, Jb, Jc, val):
    nn_sum = 0
    for n in range(2):
        for m in range(2):
            for l in range(2):
                for k in range(Z_s):
                    for j in range(Y_s):
                        for i in range(X_s):
                            no  = 1 - n
                            mo  = 1 - m
                            lo  = 1 - l
                            ipp = (i + 1) if (i + 1) < X_s else 0
                            inn = (i - 1) if (i - 1) > -1  else (X_s - 1)
                            jpp = (j + 1) if (j + 1) < Y_s else 0
                            jnn = (j - 1) if (j - 1) > -1  else (Y_s - 1)
                            kpp = (k + 1) if (k + 1) < Z_s else 0
                            knn = (k - 1) if (k - 1) > -1  else (Z_s - 1)
                            if l == 0:
                                x_inn = inn
                                x_ipp = i
                                mn_x1 = inn
                            else:
                                x_inn = i
                                x_ipp = ipp
                                mn_x1 = ipp

                            if m == 0:
                                y_jnn = jnn
                                y_jpp = j
                                ln_y1 = jnn
                            else:
                                y_jnn = j
                                y_jpp = jpp
                                ln_y1 = jpp

                            if n == 0:
                                z_knn = knn
                                z_kpp = k
                                lm_z1 = knn
                            else:
                                z_knn = k
                                z_kpp = kpp
                                lm_z1 = kpp

                            energy = latt[n,m,l,k,j,i] * ( -Ja * ( latt[no,m ,l ,z_knn,j    ,i    ] + latt[no,m ,l ,z_kpp,j    ,i    ] +
                                                                   latt[n ,mo,l ,k    ,y_jnn,i    ] + latt[n ,mo,l ,k    ,y_jpp,i    ] +
                                                                   latt[n ,m ,lo,k    ,j    ,x_inn] + latt[n ,m ,lo,k    ,j    ,x_ipp] ) -
                                                            Jb * ( latt[n ,mo,lo,k    ,y_jnn,x_inn] + latt[n ,mo,lo,k    ,y_jpp,x_inn] + latt[n ,mo,lo,k    ,y_jnn,x_ipp] + latt[n ,mo,lo,k    ,y_jpp,x_ipp] +
                                                                   latt[no,m ,lo,z_knn,j    ,x_inn] + latt[no,m ,lo,z_kpp,j    ,x_inn] + latt[no,m ,lo,z_knn,j    ,x_ipp] + latt[no,m ,lo,z_kpp,j    ,x_ipp] +
                                                                   latt[no,mo,l ,z_knn,y_jnn,i    ] + latt[no,mo,l ,z_kpp,y_jnn,i    ] + latt[no,mo,l ,z_knn,y_jpp,i    ] + latt[no,mo,l ,z_kpp,y_jpp,i    ] ) -
                                                            Jc * ( latt[no,mo,lo,k    ,j    ,i    ] + latt[no,mo,lo,lm_z1,j    ,i    ] +
                                                                   latt[no,mo,lo,k    ,ln_y1,i    ] + latt[no,mo,lo,lm_z1,ln_y1,i    ] +
                                                                   latt[no,mo,lo,k    ,j    ,mn_x1] + latt[no,mo,lo,lm_z1,j    ,mn_x1] +
                                                                   latt[no,mo,lo,k    ,ln_y1,mn_x1] + latt[no,mo,lo,lm_z1,ln_y1,mn_x1] ) )

                            if val == 0:
                                if energy < 0:
                                    pass
                                else:
                                    latt[n,m,l,k,j,i] *= -1
                            else:
                                if energy < 0:
                                    if randvals[n,m,l,k,j,i] < np.exp( 2.0 * val * energy ):
                                        latt[n,m,l,k,j,i] *= -1
                                else:
                                    latt[n,m,l,k,j,i] *= -1

                            nn_sum += energy
    return nn_sum
