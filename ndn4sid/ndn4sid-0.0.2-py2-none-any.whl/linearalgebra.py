import nupmy as np
from constants import *

## All Linear algebra routines


def random_permutation(n):
    """
    A function that returns a random permutation matrix and the inverse permutation of size n times n.
    Parameters:
        n(int): size of the permutation matrix
    Returns:
        M: 2D numpyarray a random permutation
        Minv: 2D numpy array the inverse permutation of specified by M
    """
    i = np.random.randint(n)
    j = np.mod(i+np.random.randint(1,n),n)
    M = np.eye(n)
    Minv = np.eye(n)
    M[i,j] = 1
    Minv[i,j] = -1
    return M,Minv


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
    U, _, _ = np.linalg.svd(M, full_matrices=True)
    right_null_space = U[:, r:]
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
    T_1 = get_intersection(T, get_right_null_space(T_0))
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


def get_intersection(A, B):
    """
    Calculates the intersection of of two column spaces. This space is V = {x | ∃v,∃w, Av = x = Bw}
    Parameters:
        A: A 2D numpy array
        B: A 2D numpy array
    Returns:
        intersection: The intersection of the column spaces of A and B.
    """
    complement_A = get_complement_columns(A)
    complement_B = get_complement_columns(B)
    concat_comp_A_comp_B = concat(complement_A, complement_B, axis=1)
    intersection = get_complement_columns(concat_comp_A_comp_B)
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
    Projectes the columns of A on to the column space of B. 
    The rank of B can be be provided. If no rank is provided, the rank is estimated. 
    Parameters:
        A: A 2D numpy array
        B: A 2D numpy array
    Returns:
        projection: the projeced space from the columns of A onto the columns of B.
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
        commutator: 2D numpy array representing the comutator of A and B.
    """
    commutator = A @ B - B @ A
    return commutator