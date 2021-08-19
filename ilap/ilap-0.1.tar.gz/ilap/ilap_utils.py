'''
ilap_utils.py

Implements the Fixed Talbot Laplace inversion scheme of Abate and Valko in two ways:
1) Using pure numpy functions, limited to machine precision but working with
    transforms defined using any library
2) Using the mpmath multi-precision library. Solution is to aritrary precision, but
    the transform must be defined exclusively with mpmath (not numpy/scipy) functions.
'''
import mpmath as mpm
import numpy as np

def invert(lt, t):
    M = 15
    theta = np.arange(1,M)*np.pi/M
    sigma = theta + (theta/np.tan(theta)-1)/np.tan(theta)
    B = (1 + 1j*sigma)
    r = 2*M/(5*t)
    s = r*theta*(1/np.tan(theta) + 1j)

    A = np.exp(t*s)*np.fromiter(map(lt,s), dtype=np.complex128)
    return (r/M)*(np.real(np.dot(A,B)) + np.real(lt(r))*np.exp(r*t)/2)

def invert_mp(lt, t):
    '''multiprecision (slow) Fixed Talbot inversion. Transform must be defined with mpm functions'''
    def mat_map(func, mat):
        res = mpm.matrix(len(mat),1)
        for idx, val in enumerate(mat):
            res[idx] = func(val)
        return res

    def mat_div(a1, a2):
        if not isinstance(a2, mpm.matrix): #second value is scalar
            return a1/a2
        elif isinstance(a1, mpm.matrix): #both matrices
            assert(len(a1)==len(a2))
            res = mpm.matrix(len(a2),1)
            for idx, val in enumerate(a2):
                res[idx] = a1[idx]/val
            return res
        else: #only seccond is matrix
            res = mpm.matrix(len(a2),1)
            for idx, val in enumerate(a2):
                res[idx] = a1/val
            return res

    def mat_mult(m1, m2):
        assert(len(m1) == len(m2))
        res = mpm.matrix(len(m2),1)
        for idx, val in enumerate(m1):
            res[idx] = val*m2[idx]
        return res

    M = mpm.mp.dps
    theta = mpm.matrix(np.arange(1,M))*mpm.pi/M
    tan_theta = mat_map(mpm.tan, theta)
    
    sigma = theta + mat_div(mat_div(theta, tan_theta)-1, tan_theta)
    B = (1 + 1j*sigma)
    r = mpm.mpf(2*M/(5*t))
    s = r*mat_mult(theta, mat_div(1, tan_theta) + 1j)
    A = mat_mult(mat_map(mpm.exp, t*s), mat_map(lt, s))

    return mpm.re((r/M)*((A.T*B)[0]+ lt(r)*mpm.exp(r*t)/2))