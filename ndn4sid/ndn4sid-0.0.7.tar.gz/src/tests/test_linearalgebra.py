import pytest
import numpy as np
from ndn4sid.linearalgebra import *

@pytest.mark.parametrize("n",[1,2,3,4,5,6,7,8,9,10])
@pytest.mark.parametrize("r",[1,2,3,4,5,6,7,8,9,10])
def test_get_random_matrix_with_rank_r(n,r):
    A = get_random_matrix_with_rank_r(n,r)
    assert np.linalg.matrix_rank(A) == min(n,r)

def test_get_random_permutation():
    for n in range(2,10):
        for _ in range(100):
            M,M_inv = get_random_permutation(n)
            assert check_norm_is_zero(M@M_inv - np.eye(n))
            assert np.sum(M) == (n+1)
            assert np.sum(M_inv) == (n-1)


@pytest.mark.parametrize("n",[1,2,3,4,5,6,7,8,9,10])
@pytest.mark.parametrize("r",[1,2,3,4,5,6,7,8,9,10])
def test_get_right_null_space(n,r):
    A = get_random_matrix_with_rank_r(n,r)
    x = get_right_null_space(A,r)
    assert check_norm_is_zero(A@x)
    x = get_right_null_space(A)
    assert check_norm_is_zero(A@x)


@pytest.mark.parametrize("n",[1,2,3,4,5,6,7,8,9,10])
@pytest.mark.parametrize("r",[1,2,3,4,5,6,7,8,9,10])
def test_get_column_space(n,r):
    A = get_random_matrix_with_rank_r(n,r)
    x = get_column_space(A,r)
    assert np.linalg.matrix_rank(concat(A,x,axis=1)) == np.linalg.matrix_rank(A)
    x = get_column_space(A)
    assert np.linalg.matrix_rank(concat(A,x,axis=1)) == np.linalg.matrix_rank(A)


@pytest.mark.parametrize("n",[1,2,3,4,5,6,7,8,9,10])
@pytest.mark.parametrize("r",[1,2,3,4,5,6,7,8,9,10])
def test_get_complement_columns(n,r):
    A = get_random_matrix_with_rank_r(n,r)
    x = get_complement_columns(A,r)
    assert x.shape == (n,max(0,n-r))
    Ax = concat(A,x,axis=1)
    assert np.linalg.matrix_rank(Ax) == n
    x = get_column_space(A)
    assert np.linalg.matrix_rank(Ax) == n


# TODO: implement the commutation test.
def test_check_commuting_set():
    pass

@pytest.mark.parametrize("n",[10])
@pytest.mark.parametrize("r0",[1,2,3])
@pytest.mark.parametrize("r1",[1,2,3])
def test_get_difference_column_space(n,r0,r1):
    T0 = np.random.randn(n,r0)
    T1 = np.random.randn(n,r1)
    T = concat(T0,T1,axis=1)

    change_of_basis_T = np.random.randn(r1+r0,r1+r0)
    change_of_basis_T1 = np.random.randn(r1,r1)

    T1_changed = T1@change_of_basis_T1
    T_changed = T@change_of_basis_T

    T1_est = get_difference_column_space(T,T0)
    T0_T1_est = concat(T0,T1_est,axis=1)
    assert np.linalg.matrix_rank(T0) == min(n,r0)
    assert np.linalg.matrix_rank(T1_est) == min(n,r1)
    assert np.linalg.matrix_rank(T0_T1_est) == min(n,r1+r0)
    # assert np.linalg.matrix_rank(T0_T0_est) == min(n,r0)
    

@pytest.mark.parametrize("n",[1,2,3,4])
@pytest.mark.parametrize("m1",[1,2,3])
@pytest.mark.parametrize("m2",[1,2,3])
@pytest.mark.parametrize("axis",[0,1])
def test_concat(n,m1,m2,axis):
    A = np.empty((n,m1))
    B = np.empty((n,m2))
    if axis==0:
        A = A.T
        B = B.T
    AB = concat(A,B,axis)
    assert AB.shape == (n,m1+m2) if axis==1 else (m1+m2,n)


@pytest.mark.parametrize("n",[100])
@pytest.mark.parametrize("r0",[1,2,3])
@pytest.mark.parametrize("r1",[1,2,3])
@pytest.mark.parametrize("r2",[1,2,3])
def test_get_intersection(n,r0,r1,r2):
    T0 = np.random.randn(n,r0)
    T1 = np.random.randn(n,r1)
    T2 = np.random.randn(n,r2)
    # Concatenate and apply a random row operation
    T01 = concat(T0,T1,axis=1)@np.random.randn(r0+r1,r0+r1)
    # Concatenate and apply a random row operation
    T12 = concat(T1,T2,axis=1)@np.random.randn(r1+r2,r1+r2)
    T_int = get_intersection(T01,T12,r1)
    s = T_int.shape
    s_est = (n,r1)
    assert T_int.shape == (n,r1)
    T01_T_int = concat(T01,T_int,axis=1)
    T12_T_int = concat(T12,T_int,axis=1)
    assert np.linalg.matrix_rank(T01_T_int) == r0 + r1
    assert np.linalg.matrix_rank(T12_T_int) == r1 + r2



@pytest.mark.parametrize("n",[1,2,3,4,5,6,7,8,9,10])
@pytest.mark.parametrize("r",[1,2,3,4,5,6,7,8,9,10])
def test_get_projector(n,r):
    A = get_random_matrix_with_rank_r(n,r)
    P = get_projector(A,r=r)
    assert check_norm_is_zero(P@P-P)
    assert check_norm_is_zero(P@A-A)

    A = np.random.randn(n,min(r,n))
    P = get_projector(A,r=min(r,n))
    assert check_norm_is_zero(P@P-P)
    assert check_norm_is_zero(P@A-A)

@pytest.mark.parametrize("n",[1,2,3,4,5,6,7,8,9,10])
@pytest.mark.parametrize("r",[1,2,3,4,5,6,7,8,9,10])
def test_project_A_on_B(n,r):
    A = np.random.randn(n,n)
    B = get_random_matrix_with_rank_r(n,min(n,r))
    P_A_2_B = project_A_on_B(A,B)
    P_A_2_B_2_B = project_A_on_B(P_A_2_B,B)
    assert check_norm_is_zero(P_A_2_B-P_A_2_B_2_B)
    A_P = concat(B,P_A_2_B,axis=1)
    assert np.linalg.matrix_rank(A_P) == min(n,r)



@pytest.mark.parametrize("n",[0,1,2,3,4,5,6,7,8,9,10])
def test_check_norm_is_zero(n):
    Z = np.zeros((n,n))
    assert check_norm_is_zero(Z)
    O = np.ones((n,n))
    assert not( check_norm_is_zero(O)) or n==0
    E = np.eye(n)
    assert not(check_norm_is_zero(E)) or n==0
    A = np.random.randn(n)
    assert check_norm_is_zero(A-A)
    B = np.random.randn(n,n)
    assert check_norm_is_zero(B-B)

@pytest.mark.parametrize("n",[0,1,2,3,4,5,6,7,8,9,10])
def test_lie(n):
    A = np.random.randn(n,n)
    B = np.random.randn(n,n)
    assert check_norm_is_zero(A@B-B@A-lie(A,B))