import time
import numpy as np
from numba import njit
from spins2cpu import functions

def looping3(latt, X_s, Y_s, Ja, Jb, Jc, val, nequilibrium):
    t0 = time.time()
    for i in range(nequilibrium):
        cluster3(latt, X_s, Y_s, Ja, Jb, Jc, val)
    t = time.time() - t0
    return t, functions.Average(latt[0]), functions.Average(latt[1])

@njit(cache=True)
def cluster3(latt, X_s, Y_s, Ja, Jb, Jc, val):
    l = np.random.randint(0, 2)
    k = np.random.randint(0, 4)
    j = np.random.randint(0, Y_s)
    i = np.random.randint(0, X_s)
    P_adda = 1 - np.exp( 2 * val * -abs(Ja) )
    P_addb = 1 - np.exp( 2 * val * -abs(Jb) )
    P_addc = 1 - np.exp( 2 * val * -abs(Jc) )
    lable = np.ones((2, 4, Y_s, X_s)).astype(np.int8)
    stack = [(l,k,j,i)]
    lable[l,k,j,i] = 0
    while len(stack) > 0:
        current = stack.pop()
        sign = latt[current]
        l, k, j, i = current
        lo = 1 - l
        k1 = 3 - k
        k2 = (5 - k) if k > 1 else (1 - k)
        k3 = (2 - k) if k%2 == 0 else (4 - k)
        jpp = (j + 1) if (j + 1) < Y_s else 0
        jnn = (j - 1) if (j - 1) > -1  else (Y_s - 1)
        ipp = (i + 1) if (i + 1) < X_s else 0
        inn = (i - 1) if (i - 1) > -1  else (X_s - 1)
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

        neighbor_0 = (lo, k, j, i)
        neighbor_1 = (lo, k1, j, i_1)
        neighbor_2 = (lo, k2, j_2, i)

        latt[current] *= -1
        if Ja > 0:
            if latt[neighbor_0] == sign and lable[neighbor_0] and np.random.rand() < P_adda:
                stack.append(neighbor_0)
                lable[neighbor_0] = 0
            if latt[neighbor_1] == sign and lable[neighbor_1] and np.random.rand() < P_adda:
                stack.append(neighbor_1)
                lable[neighbor_1] = 0
            if latt[neighbor_2] == sign and lable[neighbor_2] and np.random.rand() < P_adda:
                stack.append(neighbor_2)
                lable[neighbor_2] = 0
        else:
            if latt[neighbor_0] == -sign and lable[neighbor_0] and np.random.rand() < P_adda:
                stack.append(neighbor_0)
                lable[neighbor_0] = 0
            if latt[neighbor_1] == -sign and lable[neighbor_1] and np.random.rand() < P_adda:
                stack.append(neighbor_1)
                lable[neighbor_1] = 0
            if latt[neighbor_2] == -sign and lable[neighbor_2] and np.random.rand() < P_adda:
                stack.append(neighbor_2)
                lable[neighbor_2] = 0

        if abs(Jb) > abs(Ja * 0.5):
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

            neighbor_lef = (l, k1, j, x_inn)
            neighbor_rig = (l, k1, j, x_ipp)
            neighbor_up1 = (l, k2, y_jnn, i)
            neighbor_do1 = (l, k2, y_jpp, i)
            neighbor_up2 = (l, k3, y_jnn, x_inn)
            neighbor_do2 = (l, k3, y_jpp, x_ipp)
            if Jb > 0:
                if latt[neighbor_lef] == sign and lable[neighbor_lef] and np.random.rand() < P_addb:
                    stack.append(neighbor_lef)
                    lable[neighbor_lef] = 0
                if latt[neighbor_rig] == sign and lable[neighbor_rig] and np.random.rand() < P_addb:
                    stack.append(neighbor_rig)
                    lable[neighbor_rig] = 0
                if latt[neighbor_up1] == sign and lable[neighbor_up1] and np.random.rand() < P_addb:
                    stack.append(neighbor_up1)
                    lable[neighbor_up1] = 0
                if latt[neighbor_up2] == sign and lable[neighbor_up2] and np.random.rand() < P_addb:
                    stack.append(neighbor_up2)
                    lable[neighbor_up2] = 0
                if latt[neighbor_do1] == sign and lable[neighbor_do1] and np.random.rand() < P_addb:
                    stack.append(neighbor_do1)
                    lable[neighbor_do1] = 0
                if latt[neighbor_do2] == sign and lable[neighbor_do2] and np.random.rand() < P_addb:
                    stack.append(neighbor_do2)
                    lable[neighbor_do2] = 0
            else:
                if latt[neighbor_lef] == -sign and lable[neighbor_lef] and np.random.rand() < P_addb:
                    stack.append(neighbor_lef)
                    lable[neighbor_lef] = 0
                if latt[neighbor_rig] == -sign and lable[neighbor_rig] and np.random.rand() < P_addb:
                    stack.append(neighbor_rig)
                    lable[neighbor_rig] = 0
                if latt[neighbor_up1] == -sign and lable[neighbor_up1] and np.random.rand() < P_addb:
                    stack.append(neighbor_up1)
                    lable[neighbor_up1] = 0
                if latt[neighbor_up2] == -sign and lable[neighbor_up2] and np.random.rand() < P_addb:
                    stack.append(neighbor_up2)
                    lable[neighbor_up2] = 0
                if latt[neighbor_do1] == -sign and lable[neighbor_do1] and np.random.rand() < P_addb:
                    stack.append(neighbor_do1)
                    lable[neighbor_do1] = 0
                if latt[neighbor_do2] == -sign and lable[neighbor_do2] and np.random.rand() < P_addb:
                    stack.append(neighbor_do2)
                    lable[neighbor_do2] = 0

        if abs(Jc) > abs(Ja * 0.5):
            neighbor_a = (lo, k3, y_0, x_0)
            neighbor_b = (lo, k3, y_1, x_1)
            neighbor_c = (lo, k3, y_2, x_2)
            if Jc > 0:
                if latt[neighbor_a] == sign and lable[neighbor_a] and np.random.rand() < P_addc:
                    stack.append(neighbor_a)
                    lable[neighbor_a] = 0
                if latt[neighbor_b] == sign and lable[neighbor_b] and np.random.rand() < P_addc:
                    stack.append(neighbor_b)
                    lable[neighbor_b] = 0
                if latt[neighbor_c] == sign and lable[neighbor_c] and np.random.rand() < P_addc:
                    stack.append(neighbor_c)
                    lable[neighbor_c] = 0
            else:
                if latt[neighbor_a] == -sign and lable[neighbor_a] and np.random.rand() < P_addc:
                    stack.append(neighbor_a)
                    lable[neighbor_a] = 0
                if latt[neighbor_b] == -sign and lable[neighbor_b] and np.random.rand() < P_addc:
                    stack.append(neighbor_b)
                    lable[neighbor_b] = 0
                if latt[neighbor_c] == -sign and lable[neighbor_c] and np.random.rand() < P_addc:
                    stack.append(neighbor_c)
                    lable[neighbor_c] = 0

def iteration3(latt, X_s, Y_s, Ja, Jb, Jc, val, nequilibrium, nworks):
    Nw = np.zeros((nworks, 8))
    Ew = np.zeros(nworks)
    t0 = time.time()
    for i in range(nequilibrium):
        randvals = np.random.rand(2, 4, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Ja, Jb, Jc, val)
    for i in range(nworks):
        randvals = np.random.rand(2, 4, Y_s, X_s)
        E0 = update3(latt, randvals, X_s, Y_s, Ja, Jb, Jc, val)
        Ew[i] = E0 / 2
        Nw[i] = functions.Average(latt[0,0]), functions.Average(latt[0,1]), functions.Average(latt[0,2]), functions.Average(latt[0,3]),\
                functions.Average(latt[1,0]), functions.Average(latt[1,1]), functions.Average(latt[1,2]), functions.Average(latt[1,3])
    t = time.time() - t0
    return t, Nw, Ew

@njit(cache=True)
def update3(latt, randvals, X_s, Y_s, Ja, Jb, Jc, val):
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

                    energy = ( latt[l,k,j,i] * ( -Ja * ( latt[lo,k ,j    ,i    ] + latt[lo,k1,j    ,i_1  ] + latt[lo,k2,j_2  ,i    ] ) -
                                                  Jb * ( latt[l ,k1,j    ,x_ipp] + latt[l ,k1,j    ,x_inn] +
                                                         latt[l ,k2,y_jpp,i    ] + latt[l ,k2,y_jnn,i    ] +
                                                         latt[l ,k3,y_jnn,x_inn] + latt[l ,k3,y_jpp,x_ipp] ) -
                                                  Jc * ( latt[lo,k3,y_0  ,x_0  ] + latt[lo,k3,y_1  ,x_1  ] + latt[lo,k3,y_2  ,x_2  ] ) ) )

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
