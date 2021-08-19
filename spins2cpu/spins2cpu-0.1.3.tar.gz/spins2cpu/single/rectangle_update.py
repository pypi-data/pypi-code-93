import time
import numpy as np
from numba import njit
from spins2cpu import functions

def iteration5(latt, X_s, Y_s, Ja, Jb, Jc, Jd, Je, Aa, val, nequilibrium, nworks):
    t0 = time.time()
    ju = abs(Ja) * val
    if ju > 6:
        nequilibrium = nequilibrium * 3
        nworks = nworks * 3
    elif ju > 3:
        nequilibrium = nequilibrium * 2
        nworks = nworks * 2
    Nw = np.zeros((nworks, 16))
    Ew = np.zeros(nworks)
    for i in range(nequilibrium):
        laRn = functions.NormalrandNN(4, 4, Y_s, X_s)
        randvals = np.random.rand(4, 4, Y_s, X_s)
        latZ = energy_A(latt, Aa)
        laRZ = energy_A(laRn, Aa)
        Etot = update5(latt, latZ, laRn, laRZ, randvals, X_s, Y_s, Ja, Jb, Jc, Jd, Je, val)
    for i in range(nworks):
        laRn = functions.NormalrandNN(4, 4, Y_s, X_s)
        randvals = np.random.rand(4, 4, Y_s, X_s)
        latZ = energy_A(latt, Aa)
        laRZ = energy_A(laRn, Aa)
        Etot = update5(latt, latZ, laRn, laRZ, randvals, X_s, Y_s, Ja, Jb, Jc, Jd, Je, val)
        Ew[i] = Etot
        Nw[i] = functions.Average(latt[0,0,:,:,2]), functions.Average(latt[0,1,:,:,2]), functions.Average(latt[0,2,:,:,2]), functions.Average(latt[0,3,:,:,2]),\
                functions.Average(latt[1,0,:,:,2]), functions.Average(latt[1,1,:,:,2]), functions.Average(latt[1,2,:,:,2]), functions.Average(latt[1,3,:,:,2]),\
                functions.Average(latt[2,0,:,:,2]), functions.Average(latt[2,1,:,:,2]), functions.Average(latt[2,2,:,:,2]), functions.Average(latt[2,3,:,:,2]),\
                functions.Average(latt[3,0,:,:,2]), functions.Average(latt[3,1,:,:,2]), functions.Average(latt[3,2,:,:,2]), functions.Average(latt[3,3,:,:,2])
    t = time.time() - t0
    return t, Nw, Ew

def energy_A(latt, Aa):
    latt_2 = latt ** 2
    if Aa > 0:
        L_z_2 = latt_2[:,:,:,:,2]
        return ( -Aa * L_z_2 )
    else:
        L_y_2 = latt_2[:,:,:,:,1]
        return ( -Aa * L_y_2 )

@njit(cache=True)
def update5(latt, latZ, laRn, laRZ, randvals, X_s, Y_s, Ja, Jb, Jc, Jd, Je, val):
    nn_sum = 0
    nn_p = 0
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

                    energy = ( latt[l,k,j,i,0] * ( -Ja * ( latt[l ,k3,j   ,x_l ,0] + latt[l ,k1,j   ,x_r ,0] ) -
                                                    Jb * ( latt[l3,k ,y_u ,i   ,0] + latt[l1,k ,y_d ,i   ,0] ) -
                                                    Jc * ( latt[l3,k3,y_u ,x_l ,0] + latt[l3,k1,y_u ,x_r ,0] + latt[l1,k3,y_d ,x_l ,0] + latt[l1,k1,y_d ,x_r ,0] ) -
                                                    Jd * ( latt[l ,k2,j   ,x_l2,0] + latt[l ,k2,j   ,x_r2,0] ) -
                                                    Je * ( latt[l2,k ,y_u2,i   ,0] + latt[l2,k ,y_d2,i   ,0] ) ) +
                               latt[l,k,j,i,1] * ( -Ja * ( latt[l ,k3,j   ,x_l ,1] + latt[l ,k1,j   ,x_r ,1] ) -
                                                    Jb * ( latt[l3,k ,y_u ,i   ,1] + latt[l1,k ,y_d ,i   ,1] ) -
                                                    Jc * ( latt[l3,k3,y_u ,x_l ,1] + latt[l3,k1,y_u ,x_r ,1] + latt[l1,k3,y_d ,x_l ,1] + latt[l1,k1,y_d ,x_r ,1] ) -
                                                    Jd * ( latt[l ,k2,j   ,x_l2,1] + latt[l ,k2,j   ,x_r2,1] ) -
                                                    Je * ( latt[l2,k ,y_u2,i   ,1] + latt[l2,k ,y_d2,i   ,1] ) ) +
                               latt[l,k,j,i,2] * ( -Ja * ( latt[l ,k3,j   ,x_l ,2] + latt[l ,k1,j   ,x_r ,2] ) -
                                                    Jb * ( latt[l3,k ,y_u ,i   ,2] + latt[l1,k ,y_d ,i   ,2] ) -
                                                    Jc * ( latt[l3,k3,y_u ,x_l ,2] + latt[l3,k1,y_u ,x_r ,2] + latt[l1,k3,y_d ,x_l ,0] + latt[l1,k1,y_d ,x_r ,0] ) -
                                                    Jd * ( latt[l ,k2,j   ,x_l2,2] + latt[l ,k2,j   ,x_r2,2] ) -
                                                    Je * ( latt[l2,k ,y_u2,i   ,2] + latt[l2,k ,y_d2,i   ,2] ) ) )
                    Erandn = ( laRn[l,k,j,i,0] * ( -Ja * ( latt[l ,k3,j   ,x_l ,0] + latt[l ,k1,j   ,x_r ,0] ) -
                                                    Jb * ( latt[l3,k ,y_u ,i   ,0] + latt[l1,k ,y_d ,i   ,0] ) -
                                                    Jc * ( latt[l3,k3,y_u ,x_l ,0] + latt[l3,k1,y_u ,x_r ,0] + latt[l1,k3,y_d ,x_l ,0] + latt[l1,k1,y_d ,x_r ,0] ) -
                                                    Jd * ( latt[l ,k2,j   ,x_l2,0] + latt[l ,k2,j   ,x_r2,0] ) -
                                                    Je * ( latt[l2,k ,y_u2,i   ,0] + latt[l2,k ,y_d2,i   ,0] ) ) +
                               laRn[l,k,j,i,1] * ( -Ja * ( latt[l ,k3,j   ,x_l ,1] + latt[l ,k1,j   ,x_r ,1] ) -
                                                    Jb * ( latt[l3,k ,y_u ,i   ,1] + latt[l1,k ,y_d ,i   ,1] ) -
                                                    Jc * ( latt[l3,k3,y_u ,x_l ,1] + latt[l3,k1,y_u ,x_r ,1] + latt[l1,k3,y_d ,x_l ,1] + latt[l1,k1,y_d ,x_r ,1] ) -
                                                    Jd * ( latt[l ,k2,j   ,x_l2,1] + latt[l ,k2,j   ,x_r2,1] ) -
                                                    Je * ( latt[l2,k ,y_u2,i   ,1] + latt[l2,k ,y_d2,i   ,1] ) ) +
                               laRn[l,k,j,i,2] * ( -Ja * ( latt[l ,k3,j   ,x_l ,2] + latt[l ,k1,j   ,x_r ,2] ) -
                                                    Jb * ( latt[l3,k ,y_u ,i   ,2] + latt[l1,k ,y_d ,i   ,2] ) -
                                                    Jc * ( latt[l3,k3,y_u ,x_l ,2] + latt[l3,k1,y_u ,x_r ,2] + latt[l1,k3,y_d ,x_l ,0] + latt[l1,k1,y_d ,x_r ,0] ) -
                                                    Jd * ( latt[l ,k2,j   ,x_l2,2] + latt[l ,k2,j   ,x_r2,2] ) -
                                                    Je * ( latt[l2,k ,y_u2,i   ,2] + latt[l2,k ,y_d2,i   ,2] ) ) )
                    ez = latZ[l,k,j,i]
                    Ez = laRZ[l,k,j,i]
                    if val == 0:
                        if energy < 0:
                            pass
                            DeltaE = ez + energy - Ez - Erandn
                        else:
                            latt[l,k,j,i] *= -1
                            DeltaE = ez - energy - Ez - Erandn
                        if DeltaE < 0:
                            pass
                        else:
                            latt[l,k,j,i] = laRn[l,k,j,i]
                    else:
                        if energy < 0:
                            if randvals[l,k,j,i] < np.exp( 2.0 * val * energy ):
                                latt[l,k,j,i] *= -1
                                DeltaE = ez - energy - Ez - Erandn
                            else:
                                DeltaE = ez + energy - Ez - Erandn
                        else:
                            latt[l,k,j,i] *= -1
                            DeltaE = ez - energy - Ez - Erandn
                        if DeltaE < 0:
                            if randvals[l,k,j,i] < np.exp( val * DeltaE ):
                                latt[l,k,j,i] = laRn[l,k,j,i]
                        else:
                            latt[l,k,j,i] = laRn[l,k,j,i]

                    nn_sum += energy
                    nn_p += ez
    return ( nn_p + nn_sum / 2.0 )
