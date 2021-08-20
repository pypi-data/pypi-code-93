import numpy as np
from .constants import *

import itertools



def check_commuting_set(list_of_array):
    '''
    Function to check if all matrices in the argument list pairwise commute.
    Parameters:
        list_of_array: A list of arrays to be checked
    Returns:
        do_all_commute(boolean): True iff all matrices pairwise commute.
    '''
    do_all_commute = True
    for pair in itertools.combinations(list_of_array,2):
        commutator = lie(pair[0],pair[1])
        if not(check_norm_is_zero(commutator)):
            do_all_commute = False
            return do_all_commute
    return do_all_commute


def get_random_matrix_with_rank_r(n,r=0):
    """
    A function to generate random matrices with a predefined rank r.
    The rank must be smaller than the provided size of the matrix.
    Parameters:
        n(int): The size of the returned matrix
        r(int): The rank 
    Returns:
        A: A 2D numpy array of size n times n, with rank r.    
    """
    A_full_rank = np.random.randn(n,n)
    U,s,V = np.linalg.svd(A_full_rank)
    s[r:] = 0
    A = U@np.diag(s)@V
    return A
    


def get_random_permutation(n):
    """
    A function that returns a random permutation matrix and the inverse permutation of size n times n.
    Parameters:
        n(int): size of the permutation matrix
    Returns:
        M: 2D numpy array a random permutation
        M_inv: 2D numpy array the inverse permutation of specified by M
    """
    i = np.random.randint(n)
    j = np.mod(i+np.random.randint(1,n),n)
    M = np.eye(n,dtype=np.int)
    M_inv = np.eye(n,dtype=np.int)
    M[i,j] = 1
    M_inv[i,j] = -1
    return M,M_inv


def get_right_null_space(M, r=0):
    """
    Calculate the right null space of a matrix. This space is V = {x | Ax = 0}.
    Parameters:
        M: A 2D numpy array
        r: Optional rank estimation of M
    Returns:
        right_null_space: A 2D numpy array, which is the right null space of M.
    """
    r = np.linalg.matrix_rank(M) if r == 0 else r
    _, _, V = np.linalg.svd(M, full_matrices=True)
    right_null_space = V[r:, :].T
    return right_null_space


def get_column_space(M, r=0):
    """
    Calculate the column space of a matrix. This space is V = {x | ∃v, Av = x}
    Parameters:
        M: A 2D numpy array
        r: Optional rank estimation of M
    Returns:
        column_space: A 2D numpy array, which is the column space of M.
    """
    r = np.linalg.matrix_rank(M) if r == 0 else r
    U, _, _ = np.linalg.svd(M, full_matrices=True)
    column_space = U[:, :r]
    return column_space


def get_complement_columns(M, r=0):
    """
    Calculate the complement of the column space. This space is V = {x | ∄v, Av = x}
    Parameters:
        M: A 2D numpy array
        r(int): Optional rank estimation of M
    Returns:
        complement: A 2D numpy array, which is the complement of the column space of M.
    """
    r = np.linalg.matrix_rank(M) if r == 0 else r
    U, _, _ = np.linalg.svd(M, full_matrices=True)
    complement = U[:, r:]
    return complement


def get_difference_column_space(T, T_0):
    """
    Function to calculate the difference between T = [T_0 T_1] and T_0. 
    This function returns T_1.
    Using set notation we return T_1 = T-T_0
    Parameters:
        T: A 2D numpy array
        T_0: A 2D numpy array
    Returns:
        T_1: A 2D numpy array, which is the difference between T and T_0
    """
    T_1 = get_intersection(T, get_complement_columns(T_0))
    return T_1


def concat(A, B, axis=0):
    """
    Shorthand wrapper for numpy.concatenate
    Parameters:
        A: A 2D numpy array
        B: A 2D numpy array
        axis: The concatenation axis.
    Returns:
        AB: The concatenation of A and B via the specified axis.
    """
    AB = np.concatenate((A, B), axis=axis)
    return AB


def get_intersection(A, B, dim_intersection=None):
    """
    Calculates the intersection of of two column spaces. This space is V = {x | ∃v,∃w, Av = x = Bw}
    Parameters:
        A: A 2D numpy array
        B: A 2D numpy array
        dim_intersection: An optional estimation of the dimension of the intersection.
    Returns:
        intersection: The intersection of the column spaces of A and B.
    """
    complement_A = get_complement_columns(A)
    complement_B = get_complement_columns(B)
    concat_comp_A_comp_B = concat(complement_A, complement_B, axis=1)
    if dim_intersection == None:
        intersection = get_complement_columns(concat_comp_A_comp_B)
    else:
        intersection = get_complement_columns(concat_comp_A_comp_B,A.shape[0]-dim_intersection)
    return intersection


def get_projector(A, r=0):
    """
    Calculates the projector of the column space of the matrix A.
    If no rank is provided via r, the rank is estimated.
    Parameters:
        A: A 2D numpy array
        r(int): Optional rank estimation of A
    Returns:
        projector: The projector onto the columns of A.
    """
    r = np.linalg.matrix_rank(A) if r == 0 else r
    U, _, _ = np.linalg.svd(A)
    U = U[:, 0:r]
    projector = U @ np.linalg.inv(U.T @ U) @ U.T
    return projector


def project_A_on_B(A, B, r=0):
    """
    Projects the columns of A on to the column space of B. 
    The rank of B can be be provided. If no rank is provided, the rank is estimated. 
    Parameters:
        A: A 2D numpy array
        B: A 2D numpy array
    Returns:
        projection: the projected space from the columns of A onto the columns of B.
    """
    projection = get_projector(B, r) @ A
    return projection


def check_norm_is_zero(P, tol=tol):
    """
    A function to check if a matrix has norm zero, up to the specified numerical precission.
    Parameters:
        P: A numpy array
        tol: The numerical tolerance.
    Returns:
        is_zero: Boolean value which is True when the norm of P is zero, False otherwise. 
    """
    is_zero = np.linalg.norm(P) < tol
    return is_zero


def lie(A, B):
    """
    Computes the commutator of two matrices A@B-B@A
    Parameters:
        A: 2D numpy array
        B: 2D numpy array
    Returns:
        commutator: 2D numpy array representing the commutator of A and B.
    """
    commutator = A @ B - B @ A
    return commutator