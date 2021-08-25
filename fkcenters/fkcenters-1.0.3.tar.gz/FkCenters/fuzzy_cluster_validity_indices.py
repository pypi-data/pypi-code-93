#toanstt ported to python 
#Origina source: https://github.com/fernandase/fuzzy-cluster-validity-indices
# FUZZY SILHOUETTE

# FUZZY.SIL is a implementation of the Fuzzy Silhouette of CAMPELLO, R.; HRUSCHKA, E. A fuzzy extension of the silhouette width criterion
# for cluster analysis. Fuzzy Sets and Systems, v. 157, n. 21, p. 2858

# This function returns the silhouette of each object (obj.sil) and the fuzzy silhouette of the given fuzzy partition
import numpy as np
import math
import copy
def overlap_distance(a, b):
    return np.sum(a != b)
def MyFuzzySil(X,U,labels,distance=overlap_distance, alpha=1):
    n = len(X)
    k = len(U[0])
    D = np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            D[i][j] = distance(X[i],X[j])
    #Compute crisp silhouette for each object
    numerator=0
    denominator=0
    for i in range(n):
        count_a = 0
        a_sum=0
        #b_sum=0
        label = labels[i]
        d=np.zeros((k))
        count=np.zeros((k))
        for i2 in range(n):
            label2 = labels[i2]
            d[label2] += D[i][i2]
            count[label2] += 1
                
        a = d[label]/count[label]
        d[label] = float('inf')
        d[count==0]=float('inf')

        ii = np.argmin(d)
        b = d[ii]/count[ii]
        #print(b)
        maxab = max(a,b)
        if maxab ==0: continue
        s = (b-a)/maxab
        #Compute Fuzzy sil
        sorted_array = np.sort(U[i])
        dif = (sorted_array[k-1]-sorted_array[k-2])**alpha
        numerator+= dif*s
        denominator+=dif
    if denominator ==0: return 0
    return numerator/denominator





def FuzzySil(X,U,distance=overlap_distance, alpha=1):
    n = len(X)
    k = len(U[0])
    D = np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            D[i][j] = distance(X[i],X[j])
    obj = np.array([np.argmax(i) for i in U])
    degrees = np.zeros(n)
    a = np.zeros(n)
    b = np.zeros(n)
    sil = np.zeros(n)
    for i in range(n):
        degrees[i] = (np.max(U[i])- np.min(U[i]))**alpha
        B = np.zeros(k)
        i2 = np.argwhere(obj != obj[i]) 
        c2 = np.unique(obj[i2])  # all remaining clusters that object i does not belong
        for c in c2:
            i3 = np.argwhere (obj == c) # objects in the cth cluster
            for object_index in i3:
                B[c] += distance(X[i],X[object_index])
            B[c]/= len(i3)
            asd=123
        asd=123
        B[obj[i]] = float('inf')
        b[i] = np.min(B)
        m = np.argwhere(obj == obj[i]) # # objects in the same cluster of i
        for object_index in m:
            a[i] += distance(X[i],X[object_index])
        a[i]/= len(m)
        if (len(obj[i] == obj)) > 1 and (a[i] >0 or b[i]>0):
            sil[i] = (b[i] - a[i])/max(a[i], b[i])
        else: sil[i] = a[i]
    sil2 = sum(degrees * sil)/sum(degrees)
    if(sil2==-1):
        asd=123
    return sil2


def MPO(U):
    n = len(U)
    k = len(U[0])
    mpo =[]
    oijk =[]
    for c1 in range(k-1):
        for c2 in range(c1+1,k):
            o = abs(U[c1]-U[c2])
            threshold = round(1.0/k,4)
            i = np.where(o >= threshold)[0]
            o[i] = 1 - o[i]
            for ii in range(len(o)):
                if ii not in i: o[ii]=0
            oijk.append(o)
    am = min(np.sum(U**2,axis=1))
    comp = ((k+1)/(k-1))**(1/2) * np.sum(U**2)/am;
    sep = np.sum(oijk)/n;
    result = comp - sep; 
    return comp,sep,result
def NPE(U, base_log=2):
    U2 = copy.deepcopy(U)
    nrow = len(U)
    ncol = len(U[0])
    for i in range(nrow):
        for j in range(ncol):
            if U[i][j]==0: U2[i][j]=-100
            else: U2[i][j] = math.log(U[i][j], base_log)

    return (nrow * (-np.sum(U *U2 )/nrow)/(nrow-ncol))

def PE(U, base_log=2):
    U2 = copy.deepcopy(U)
    nrow = len(U)
    ncol = len(U[0])
    for i in range(nrow):
        for j in range(ncol):
            if U[i][j]==0: U2[i][j]=-100
            else: U2[i][j] = math.log(U[i][j], base_log)
    return -np.sum(U * U2)/nrow
def PEB(U, base_log=2):
    U2 = copy.deepcopy(U)
    nrow = len(U)
    ncol = len(U[0])
    for i in range(nrow):
        for j in range(ncol):
            if U[i][j]==0: U2[i][j]=-100
            else: U2[i][j] = math.log(U[i][j], base_log)
    return((-np.sum(U * U2)/nrow)/math.log(ncol, base_log))
if __name__ == "__main__":
    X = np.genfromtxt('X.csv',delimiter=',')
    U = np.genfromtxt('U.csv',delimiter=',')
    sil = FuzzySil(X,U,overlap_distance)
    print(sil)
    comp,sep,mpo = MPO(U)
    print(comp,sep,mpo)
    npe = NPE(U)
    print(npe)
    pe = PE(U)
    print(pe)
    peb = PEB(U)
    print(peb)