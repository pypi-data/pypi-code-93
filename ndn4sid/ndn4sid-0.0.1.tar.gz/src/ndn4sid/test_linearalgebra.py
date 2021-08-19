import numpy as np
from ndn4sid.constants import *
from ndn4sid.linearalgebra import *

def test_get_random_permutation():
    for n in range(2,10):
        for _ in range(100):
            T,Tinv = get_random_permutation(n)
            assert check_norm_is_zero(T@Tinv - np.eye(n))
            assert np.sum(T) == (n+1)
            assert np.sum(Tinv) == (n-1)
    

