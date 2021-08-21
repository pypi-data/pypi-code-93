import numpy as np
import warnings
from typing import List
import functools
import itertools
from dataclasses import dataclass
from .constants import *
from .linearalgebra import *
from .misc import *

@dataclass()
class SS:
    '''
    A class to represent nD autonomous commuting state space models.
    Parameters:
        A(List[np.array]): List of system matrices, can also be a single matrix for 1D systems.
        C(np.array): Output matrix, throws a warning if dimension of array is 1.
        x0(np.array): Initial state, throws a warning if dimension of array is 1.
        name(str): Name of the model. (optional)
        suppress_warnings(bool): Boolean to suppress warnings, default is False (optional).
    '''
    A: List[np.array]
    C: np.array
    x0: np.array
    name: str = "State space model"
    suppress_warnings: bool = False
    def __post_init__(self):
        '''
        Function that is run after the initialization.
        The well-posedness of the model is checked, and the dimensions of the model are stored.
        '''
        self.check_if_model_is_well_posed()
        self.nb_dim = len(self.A)
        self.nb_output = self.C.shape[0]
        self.nb_state = self.x0.shape[0]
        
    def check_if_model_is_well_posed(self):
        '''
        The well-posedness of the model is checked, the dimensions of the output matrix and 
        initial states are expanded if needed. The parameter dimensions are checked.
        '''
        do_all_commute = check_commuting_set(self.A)
        # Check if the model is well posed
        if not(do_all_commute):
            raise ValueError("The provided system matrices must pairwise commute.")
        # Check if all the dimensions are ok.
        if np.ndim(self.C)==1:
            self.C = np.expand_dims(self.C,axis=0)
            self.warning("The provided C matrix has been expanded to have two dimensions.")
        if np.ndim(self.x0)==1:
            self.x0 = np.expand_dims(self.x0,axis=1)
            self.warning("The provided initial state has been expanded to have two dimensions.")
        
        if not(self.C.shape[1] == self.A[0].shape[0]):
            raise ValueError("The provided output matrix has a wrong shape.")
        if not(self.x0.shape[0] == self.A[0].shape[1]):
            raise ValueError("The initial state has a wrong shape.")
            
    def warning(self, message):
        '''
        A function to handle class warnings. The warnings are not displayed in the suppress_warnings boolean is True.
        Note that repeated warnings are suppressed.
        Parameters:
            self(SS): self
            message(str): The waring text.
        '''
        if not(self.suppress_warnings):
            warnings.warn(message)


def get_observability_matrix(SS):
    """
    Get the observability matrix of a commuting state space model.
    Parameters:
        SS: A state space model
    Returns:
        O(np.array): A 2D numpy array, which is the observability matrix of SS
    """
    nb_state = SS.nb_state
    # The first block row of the observability matrix is just the output matrix.
    all_blocks = [SS.C]
    for block_index in range(1,nb_state):
        block = []
        for combination in itertools.combinations_with_replacement(SS.A,block_index):
            # Calculate the matrix power
            matrix_power = functools.reduce(lambda A,B : A@B, combination)
            # Multiply the output marix and the matrix power and append to the current block
            block.append(SS.C@matrix_power)
        # Convert the list of matrices to a single matrix
        array_block = np.concatenate(block)
        # Append the array to the list of all blocks
        all_blocks.append(array_block)
    # Concatenate all blocks into the final observability matrix.
    O = np.concatenate(all_blocks,axis=0)
    return O


def get_state_sequence_matrix(SS):
    """
    Get the state sequence matrix of a commuting state space model.
    Parameters:
        SS: A state space model
    Returns:
        X(np.array): A 2D numpy array, which is the state sequnce matrix of SS
    """
    nb_state = SS.nb_state
    # The first block row of the observability matrix is just the output matrix.
    all_blocks = [SS.x0]
    for block_index in range(1,nb_state):
        block = []
        for combination in itertools.combinations_with_replacement(SS.A,block_index):
            # Calculate the matrix power
            matrix_power = functools.reduce(lambda A,B : A@B, combination)
            # Multiply the matrix power and the initial state and append to the current block
            block.append(matrix_power@SS.x0)
        # Convert the list of matrices to a single matrix
        array_block = np.concatenate(block,axis=1)
        # Append the array to the list of all blocks
        all_blocks.append(array_block)
    # Concatenate all blocks into the final state sequence matrix.
    X = np.concatenate(all_blocks,axis=1)
    return X


def get_hankel_matrix(system):
    '''
    A Function to calculate the generalized Hankel matrix for nD commuting state space models.
    The calculation is done by taking the outer product of the theoretical factorization of the matrix.
    Parameters:
        system(SS): A state space model
    Returns:
        H(np.array): The Hankel matrix
    '''
    O = get_observability_matrix(system)
    X = get_state_sequence_matrix(system)
    H = O@X
    return H


def transformSS(system, T, T_inv, model_name=None):
    """
    Function to apply a similarity transformation in place to a state space model.
    Parameters:
        system: A state space model
        T: Transformation matrix
        T_inv: The inverse of the transformation matrix.
    Returns:
        transformed_system(system): The transformed system
    """
    A = [T_inv @ A @ T for A in system.A]
    C = system.C @ T 
    x0 = T_inv @ system.x0

    transformed_system = SS(A, C, x0, model_name)
    return transformed_system

def print_state_space_model(SS):
    """
    Print the name and system matrices of a state space model.
    Parameters:
        SS: A state space model
    Returns:

    """
    print(SS.name)
    for k,A in enumerate(SS.A):
        A_k = A
        print(f"A_{k} = \n {A}")
    print(f"x0 = \n {SS.x0}")
    print(f"C = \n {SS.C}")


def simulate_SS(SS, size):
    """Function to simulate the output of an autonomous state space model.
    Parameters:
        SS: A state space model
        n(int): The time horizon.
        m(int): The spatial horizon
    Returns:
        y: The simulated response on length n times m.
    """
    # make sure the size is a list
    assert len(size)==SS.nb_dim
    y = np.empty((SS.nb_output,*size))
    for index in itertools.product(*[range(s) for s in size]):
        matrix_powers = [np.linalg.matrix_power(A,p) for A,p in zip(SS.A,index)]
        matrix_product = functools.reduce(lambda A,B:A@B, matrix_powers)
        y[(slice(0,SS.nb_output),*index)] = np.squeeze(SS.C@matrix_product@SS.x0)
    return y


def get_kalman_decomposition(SS):
    """
    Calculate the Kalman decomposition of a state space model.
    Calculations follow: https://en.wikipedia.org/wiki/Kalman_decomposition
    Parameters:
        SS: A state space model
    Returns:
        SS_kalman: The Kalman decomposition of SS. 
    """
    # Get the observability matrix [C^T (CA)^T (CA^2)^T ... (CA^{n-1})^T]^T
    O = get_observability_matrix(SS)
    # Get the state sequence matrix [x Ax A^2x ... A^{n-1}x]
    X = get_state_sequence_matrix(SS)

    basis_reach = get_column_space(X)
    # Basis for unobservable space.
    basis_not_obs = get_right_null_space(O)

    not_obs_con = np.array(get_intersection(basis_reach, basis_not_obs))

    not_obs_not_con = get_difference_column_space(basis_not_obs, not_obs_con)
    obs_con = get_difference_column_space(basis_reach, not_obs_con)
    obs_not_con = get_complement_columns(np.concatenate((not_obs_con, not_obs_not_con, obs_con), axis=1))

    T_inv_est = np.concatenate((not_obs_con, obs_con, not_obs_not_con, obs_not_con), axis=1)
    T_est = np.linalg.inv(T_inv_est)
    return T_inv_est, T_est


def get_hankel_tensor(y,order):
    """
    A method to calculate the Hankel tensor of a nD array.
    The Hankel tensor is constructed as
    H[i,k_1,l_1,k_2,l_2,\dots, k_n,l_n] = y[i,k_1+l_1,k_2+l_2,\dots,k_n+l_n]
    Parameters:
        y(np.array): 1 + n dimensional dataset. The first dimension is for multiple outputs.
        order(list(int)): Order of the Hankelization. The length is equal to n.
    Returns:
        H(np.array): A recursive Hankel tensor.
    """
    # The first dimension is reserved for multivariate signals. 
    n_dim = np.ndim(y) - 1
    size_y = y.shape[1:]
    nb_output = y.shape[0]
    
    # Check if the dimension of the dataset is the same as the size of the order.
    assert len(order) == n_dim
    # Calculate the shape of the Hankel tensor.
    H_shape = [sub for k,l in zip(size_y,order) for sub in (k-l+1,l)]
    # Check if the size is positive
    assert all([h>0 for h in H_shape])
    
    # Initialize the Hankel tensor, the first dimension is add and is equal to the number of outputs.
    H = np.empty([nb_output] + H_shape)
    # Create the index range, which is a list of ranges. 
    for tenson_index in shape_to_iterator(H_shape):
        data_index = tensor_index_to_data_index(tenson_index)
        H[(slice(0,nb_output),*tenson_index)] = y[(slice(0,nb_output),*data_index)]
    return H