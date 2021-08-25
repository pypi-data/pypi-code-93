#! /usr/bin/env python3

import numpy as np


def krodelta(arg1, arg2):
    """
    Kronecker delta function

    Positional arguments:
        arg1 (float/int) :: First variable
        arg2 (float/int) :: Second variable

    Keyword arguments:
        None

    Returns:
        val (int) :: 1 if arg1 = arg, else 0
    """

    if arg1 == arg2:
        val = 1
    else:
        val = 0

    return val


def stevens_to_wybourne(CFPs, k_max):
    """
    Transforms Crystal Field parameters from Wybourne notation to
    Stevens notation

    Assumes only even Ranks (k) are present


    Positional arguments:
        CFPs (np.array)  : CFPs in Stevens notation ordered
                           k=2 q=-2, ... k=2 q=2, k=4 q=-4, ...
        k_max (integer)  : maximum value of k

    Returns:
        w_CFPs (np.array) : CFPs in Wybourne notation
    """

    n_CFPs = {2: 5, 4: 14, 6: 27}

    # Taken from Mulak and Gajek
    lmbda = [
             np.sqrt(6.)/3.,
             -np.sqrt(6.)/6.,
             2.,
             -np.sqrt(6.)/6.,
             np.sqrt(6.)/3.,
             4.*np.sqrt(70.)/35.,
             -2.*np.sqrt(35.)/35.,
             2.*np.sqrt(10.)/5.,
             -2*np.sqrt(5.)/5.,
             8.,
             -2.*np.sqrt(5.)/5.,
             2.*np.sqrt(10.)/5.,
             -2.*np.sqrt(35.)/35.,
             4.*np.sqrt(70.)/35.,
             16.*np.sqrt(231.)/231.,
             -8.*np.sqrt(77.)/231.,
             8.*np.sqrt(14.)/21.,
             -8.*np.sqrt(105.)/105.,
             16.*np.sqrt(105.)/105.,
             -4.*np.sqrt(42.)/21.,
             16.,
             -4.*np.sqrt(42.)/21.,
             16.*np.sqrt(105.)/105.,
             -8.*np.sqrt(105.)/105.,
             8.*np.sqrt(14.)/21.,
             -8.*np.sqrt(77.)/231.,
             16.*np.sqrt(231.)/231.
            ]

    w_CFPs = np.zeros(n_CFPs[k_max], dtype=np.complex128)

    for k in range(2, k_max + 2, 2):
        for q in range(-k, k + 1):
            ind = _even_kq_to_num(k, q)
            neg_ind = _even_kq_to_num(k, -q)
            if q == 0:
                w_CFPs[ind] = lmbda[ind] * CFPs[ind]
            elif q > 0:
                w_CFPs[ind] = lmbda[ind]*(CFPs[ind] + 1j*CFPs[neg_ind])
            elif q < 0:
                w_CFPs[ind] = lmbda[ind]*(-1)**q*(CFPs[neg_ind] - 1j*CFPs[ind])

    return w_CFPs


def _even_kq_to_num(k, q):
    """
    Converts Rank (k) and order (q) to array index
    Assuming that only even ranks are present

    Positional arguments:
        k (int) : Rank
        q (int) : Order

    Keyword arguments:
        None

    Returns:
        index (int) : Array index
    """

    index = k + q
    for kn in range(1, int(k/2)):
        index += 2*(k-2*kn) + 1

    return index


def GCD(a, b):
    """
    Calculates greatest common divisor of two numbers
    by recursion

    Positional arguments:
        a (float/int) :: first number
        b (float/int) :: second number

    Keyword arguments:
        None

    Returns:
        divisor (float) : greatest common divisor of a and b

    """
    if b == 0:
        divisor = a
    else:
        divisor = GCD(b, a % b)

    return divisor


def binomial(n, r):
    """
    Calculates binomial coefficient nCr (n r)

    Positional arguments:
        n (float/int) :: first number
        r (float/int) :: second number

    Keyword arguments:
        None

    Returns:
        bcoeff (float) : Binomial coefficient

    """
    bcoeff = 0.

    if r == n or r == 0:
        bcoeff = 1.
    elif r < 0:
        bcoeff = 0.
    elif r == 1:
        bcoeff = n
    else:
        #https://en.wikipedia.org/wiki/Binomial_coefficient#Multiplicative_formula # noqa
        bcoeff = n
        for i in range(2, r+1):
            bcoeff *= (n + 1 - i) / i

    return bcoeff


def hex_to_rgb(value):
    """
    Convert hex code to rgb list

    Positional arguments:
        value (str)             :: Hex code

    Keyword arguments:
        None

    Returns:
        rgb (list)    :: [red,green,blue]
    """

    value = value.lstrip('# ')
    lv = len(value)
    rgb = [int(value[i:i + lv // 3], 16)/255. for i in range(0, lv, lv // 3)]

    return rgb


def factorial(n):
    if n == 1:
        return n
    else:
        return n*factorial(n-1)
