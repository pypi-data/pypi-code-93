import time
import numpy as np
from numba import njit
from spins2cpu import functions

def iteration3(latt, X_s, Y_s, Ja, Jb, Jc, val, nequilibrium, nworks):
    Nw = np.zeros((nworks, 16))
    Ew = np.zeros(nworks)
    t0 = time.time()
    for i in range(nequilibrium):
        randvals = np.random.rand(4, 4, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Ja, Jb, Jc, val)
    for i in range(nworks):
        randvals = np.random.rand(4, 4, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Ja, Jb, Jc, val)
        Ew[i] = E0 / 2
        Nw[i] = functions.Average(latt[0,0]), functions.Average(latt[0,1]), functions.Average(latt[0,2]), functions.Average(latt[0,3]),\
                functions.Average(latt[1,0]), functions.Average(latt[1,1]), functions.Average(latt[1,2]), functions.Average(latt[1,3]),\
                functions.Average(latt[2,0]), functions.Average(latt[2,1]), functions.Average(latt[2,2]), functions.Average(latt[2,3]),\
                functions.Average(latt[3,0]), functions.Average(latt[3,1]), functions.Average(latt[3,2]), functions.Average(latt[3,3])
    t = time.time() - t0
    return t, Nw, Ew

@njit(cache=True)
def update3(latt, randvals, X_s, Y_s, Ja, Jb, Jc, val):
    nn_sum = 0
    for l in range(4):
        for k in range(4):
            for j in range(Y_s):
                for i in range(X_s):
                    ipp = (i + 1) if (i + 1) < X_s else 0
                    inn = (i - 1) if (i - 1) > -1  else (X_s - 1)
                    jpp = (j + 1) if (j + 1) < Y_s else 0
                    jnn = (j - 1) if (j - 1) > -1  else (Y_s - 1)
                    lx  = 3 - l
                    ly  = (5 - l) if l > 1 else (1 - l)
                    lz  = (2 - l) if l%2 == 0 else (4 - l)
                    if l == 0:
                        ix0 = ipp
                        ix1 = ipp
                        ix2 = i
                        ix3 = i
                        jy0 = jpp
                        jy1 = j
                        jy2 = j
                        jy3 = jpp
                    elif l == 1:
                        ix0 = ipp
                        ix1 = ipp
                        ix2 = i
                        ix3 = i
                        jy0 = j
                        jy1 = jnn
                        jy2 = jnn
                        jy3 = j
                    elif l == 2:
                        ix0 = i
                        ix1 = i
                        ix2 = inn
                        ix3 = inn
                        jy0 = j
                        jy1 = jnn
                        jy2 = jnn
                        jy3 = j
                    else:
                        ix0 = i
                        ix1 = i
                        ix2 = inn
                        ix3 = inn
                        jy0 = jpp
                        jy1 = j
                        jy2 = j
                        jy3 = jpp

                    if k == 0:
                        if l == 0:
                            i_0 = i
                            i_1 = i
                            j_3 = j
                            j_0 = j
                        elif l == 1:
                            i_0 = i
                            i_1 = i
                            j_3 = jnn
                            j_0 = jnn
                        elif l == 2:
                            i_0 = inn
                            i_1 = inn
                            j_3 = jnn
                            j_0 = jnn
                        else:
                            i_0 = inn
                            i_1 = inn
                            j_3 = j
                            j_0 = j

                        E = -Jc * ( latt[l,0,j,i] * ( latt[lx,3,j,ix0] + latt[ly,1,jy0,i] ) +
                                    latt[l,1,j,i] * ( latt[lx,2,j,ix1] + latt[ly,0,jy1,i] ) +
                                    latt[l,2,j,i] * ( latt[lx,1,j,ix2] + latt[ly,3,jy2,i] ) +
                                    latt[l,3,j,i] * ( latt[lx,0,j,ix3] + latt[ly,2,jy3,i] ) )

                        F = ( latt[l ,2,j  ,i  ] * ( -Ja * ( latt[l ,1,j  ,i  ] + latt[l ,3,j  ,i  ] ) - Jb * latt[l ,0,j  ,i  ] ) +
                              latt[ly,3,j_3,i  ] * ( -Ja * ( latt[ly,0,j_3,i  ] + latt[ly,2,j_3,i  ] ) ) +
                              latt[lz,0,j_0,i_0] * ( -Ja * ( latt[lz,3,j_0,i_0] + latt[lz,1,j_0,i_0] ) - Jb * latt[lz,2,j_0,i_0] ) +
                              latt[lx,1,j  ,i_1] * ( -Ja * ( latt[lx,2,j  ,i_1] + latt[lx,0,j  ,i_1] ) ) )

                        if val == 0:
                            if E < F:
                                if F < 0:
                                    pass
                                else:
                                    latt[l ,2,j  ,i  ] *= -1
                                    latt[ly,3,j_3,i  ] *= -1
                                    latt[lz,0,j_0,i_0] *= -1
                                    latt[lx,1,j  ,i_1] *= -1
                            else:
                                if E < 0:
                                    pass
                                else:
                                    latt[l,:,j,i] *= -1
                        else:
                            if E < F:
                                if F < 0:
                                    if randvals[l,0,j,i] < np.exp( 2.0 * val * F ):
                                        latt[l,2,j,i] *= -1
                                        if Jc > 0:
                                            acceptance = np.exp( 2.0 * val * -Jc )
                                            if randvals[l,1,j,i] < acceptance:
                                                latt[ly,3,j_3,i] = -latt[l,2,j,i]
                                            else:
                                                latt[ly,3,j_3,i] = latt[l,2,j,i]
                                            if randvals[l,2,j,i] < acceptance:
                                                latt[lx,1,j,i_1] = -latt[l,2,j,i]
                                            else:
                                                latt[lx,1,j,i_1] = latt[l,2,j,i]
                                            if randvals[l,0,j,i] < 0.5:
                                                if randvals[l,3,j,i] < acceptance:
                                                    latt[lz,0,j_0,i_0] = -latt[ly,3,j_3,i]
                                                else:
                                                    latt[lz,0,j_0,i_0] = latt[ly,3,j_3,i]
                                            else:
                                                if randvals[l,3,j,i] < acceptance:
                                                    latt[lz,0,j_0,i_0] = -latt[lx,1,j,i_1]
                                                else:
                                                    latt[lz,0,j_0,i_0] = latt[lx,1,j,i_1]
                                        else:
                                            acceptance = np.exp( 2.0 * val * Jc )
                                            if randvals[l,1,j,i] < acceptance:
                                                latt[ly,3,j_3,i] = latt[l,2,j,i]
                                            else:
                                                latt[ly,3,j_3,i] = -latt[l,2,j,i]
                                            if randvals[l,2,j,i] < acceptance:
                                                latt[lx,1,j,i_1] = latt[l,2,j,i]
                                            else:
                                                latt[lx,1,j,i_1] = -latt[l,2,j,i]
                                            if randvals[l,0,j,i] < 0.5:
                                                if randvals[l,3,j,i] < acceptance:
                                                    latt[lz,0,j_0,i_0] = latt[ly,3,j_3,i]
                                                else:
                                                    latt[lz,0,j_0,i_0] = -latt[ly,3,j_3,i]
                                            else:
                                                if randvals[l,3,j,i] < acceptance:
                                                    latt[lz,0,j_0,i_0] = latt[lx,1,j,i_1]
                                                else:
                                                    latt[lz,0,j_0,i_0] = -latt[lx,1,j,i_1]
                                else:
                                    latt[l ,2,j  ,i  ] *= -1
                                    latt[ly,3,j_3,i  ] *= -1
                                    latt[lz,0,j_0,i_0] *= -1
                                    latt[lx,1,j  ,i_1] *= -1
                            else:
                                if E < 0:
                                    if randvals[l,0,j,i] < np.exp( 2.0 * val * E ):
                                        latt[l,0,j,i] *= -1
                                        if Ja > 0:
                                            acceptance = np.exp( 2.0 * val * -Ja )
                                            if randvals[l,1,j,i] < acceptance:
                                                latt[l,1,j,i] = -latt[l,0,j,i]
                                            else:
                                                latt[l,1,j,i] = latt[l,0,j,i]
                                            if randvals[l,2,j,i] < acceptance:
                                                latt[l,3,j,i] = -latt[l,0,j,i]
                                            else:
                                                latt[l,3,j,i] = latt[l,0,j,i]
                                            if Jb > Ja * 0.5:
                                                acceptance = np.exp( 2.0 * val * -Jb )
                                                if randvals[l,3,j,i] < acceptance:
                                                    latt[l,2,j,i] = -latt[l,0,j,i]
                                                else:
                                                    latt[l,2,j,i] = latt[l,0,j,i]
                                            elif Jb < -Ja * 0.5:
                                                acceptance = np.exp( 2.0 * val * Jb )
                                                if randvals[l,3,j,i] < acceptance:
                                                    latt[l,2,j,i] = latt[l,0,j,i]
                                                else:
                                                    latt[l,2,j,i] = -latt[l,0,j,i]
                                            else:
                                                if randvals[l,0,j,i] < 0.5:
                                                    if randvals[l,3,j,i] < acceptance:
                                                        latt[l,2,j,i] = -latt[l,1,j,i]
                                                    else:
                                                        latt[l,2,j,i] = latt[l,1,j,i]
                                                else:
                                                    if randvals[l,3,j,i] < acceptance:
                                                        latt[l,2,j,i] = -latt[l,3,j,i]
                                                    else:
                                                        latt[l,2,j,i] = latt[l,3,j,i]
                                        else:
                                            acceptance = np.exp( 2.0 * val * Ja )
                                            if randvals[l,1,j,i] < acceptance:
                                                latt[l,1,j,i] = latt[l,0,j,i]
                                            else:
                                                latt[l,1,j,i] = -latt[l,0,j,i]
                                            if randvals[l,2,j,i] < acceptance:
                                                latt[l,3,j,i] = latt[l,0,j,i]
                                            else:
                                                latt[l,3,j,i] = -latt[l,0,j,i]
                                            if Jb > -Ja * 0.5:
                                                acceptance = np.exp( 2.0 * val * -Jb )
                                                if randvals[l,3,j,i] < acceptance:
                                                    latt[l,2,j,i] = -latt[l,0,j,i]
                                                else:
                                                    latt[l,2,j,i] = latt[l,0,j,i]
                                            elif Jb < Ja * 0.5:
                                                acceptance = np.exp( 2.0 * val * Jb )
                                                if randvals[l,3,j,i] < acceptance:
                                                    latt[l,2,j,i] = latt[l,0,j,i]
                                                else:
                                                    latt[l,2,j,i] = -latt[l,0,j,i]
                                            else:
                                                if randvals[l,0,j,i] < 0.5:
                                                    if randvals[l,3,j,i] < acceptance:
                                                        latt[l,2,j,i] = latt[l,1,j,i]
                                                    else:
                                                        latt[l,2,j,i] = -latt[l,1,j,i]
                                                else:
                                                    if randvals[l,3,j,i] < acceptance:
                                                        latt[l,2,j,i] = latt[l,3,j,i]
                                                    else:
                                                        latt[l,2,j,i] = -latt[l,3,j,i]
                                else:
                                    latt[l,:,j,i] *= -1

                    if k == 0:
                        energy = latt[l,0,j,i] * ( -Ja * ( latt[l ,3,j,i  ] + latt[l ,1,j  ,i]   ) - Jb * latt[l,2,j,i] -
                                                    Jc * ( latt[lx,3,j,ix0] + latt[ly,1,jy0,i] ) )
                    elif k == 1:
                        energy = latt[l,1,j,i] * ( -Ja * ( latt[l ,2,j,i  ] + latt[l ,0,j  ,i]   ) -
                                                    Jc * ( latt[lx,2,j,ix1] + latt[ly,0,jy1,i] ) )
                    elif k == 2:
                        energy = latt[l,2,j,i] * ( -Ja * ( latt[l ,1,j,i  ] + latt[l ,3,j  ,i]   ) - Jb * latt[l,0,j,i] -
                                                    Jc * ( latt[lx,1,j,ix2] + latt[ly,3,jy2,i] ) )
                    else:
                        energy = latt[l,3,j,i] * ( -Ja * ( latt[l ,0,j,i  ] + latt[l ,2,j  ,i]   ) -
                                                    Jc * ( latt[lx,0,j,ix3] + latt[ly,2,jy3,i] ) )

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
