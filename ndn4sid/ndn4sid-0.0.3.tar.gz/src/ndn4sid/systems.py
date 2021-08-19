import numpy as np
from constants import *
from linearalgebra import *

def print_system(SS):
    """
    Print the system matrices of a state space model.
    Parameters:
        SS: A state space model
    Returns:

    """
    print(f"A = \n {SS['A']}")
    print(f"B = \n {SS['B']}")
    print(f"C = \n {SS['C']}")
    print(f"x0 = \n {SS['x0']}")


def get_obs_2D(SS):
    """
    Get the observability matrix [C^T (CA)^T (CA^2)^T ... (CA^{n-1})^T]^T
    Parameters:
        SS: A state space model
    Returns:
        O: A 2D numpy array, which is the observability matrix of SS
    """
    n = SS['n']
    A = SS['A']
    B = SS['B']
    C = SS['C']
    x = SS['x0']
    m = n * (n + 1) // 2
    O = np.zeros((m, n))
    row = 0
    for block_index in range(n):
        powerA = block_index
        powerB = block_index - powerA
        for row_in_block in range(block_index + 1):
            O[row, :] = C @ np.linalg.matrix_power(A, powerA) @ np.linalg.matrix_power(B, powerB)
            row += 1
            powerA -= 1
            powerB += 1
    return O


def get_con_2D(SS):
    """
    Get the state sequence matrix [x Ax A^2x ... A^{n-1}x]
    Parameters:
        SS: A state space model
    Returns:
        X: A 2D numpy array, which is the controlability matrix of SS
    """
    n = SS['n']
    A = SS['A']
    B = SS['B']
    C = SS['C']
    x = SS['x0']
    m = n * (n + 1) // 2
    X = np.zeros((n, m))
    col = 0
    for block_index in range(n):
        powerA = block_index
        powerB = block_index - powerA
        for _ in range(block_index + 1):
            X[:, col] = np.linalg.matrix_power(A, powerA) @ np.linalg.matrix_power(B, powerB) @ x
            col += 1
            powerA -= 1
            powerB += 1
    return X


def transformSS(SS, T, Tinv, model_name=None):
    """
    Function to apply a similarity transformation to a state space model.
    Parameters:
        SS: A state space model
        T: Transformation matrix
        Tinv: The inverse of the transformation matrix.
    Returns:
       SS_trans: A transformed state space model. 
    """
    SS_trans = SS.copy()
    SS_trans['A'] = Tinv @ SS['A'] @ T
    SS_trans['B'] = Tinv @ SS['B'] @ T
    SS_trans['C'] = SS['C'] @ T
    SS_trans['x0'] = Tinv @ SS['x0']
    if model_name:
        SS_trans['model_name'] = model_name
    return SS_trans


def simulate_SS(SS, n=10, m=10):
    """Function to simulate the output of an autonomous state space model.
    Parameters:
        SS: A state space model
        n(int): The time horizon.
        m(int): The spatial horizon
    Returns:
        y: The simulated response on length n times m.
    """
    y = np.array([[SS['C'] @ np.linalg.matrix_power(SS['A'], k) @ np.linalg.matrix_power(SS['B'], l) @ SS['x0'] for k in
                   range(n)] for l in range(m)])
    return y


def check_system_is_well_posed(SS):
    """
    Checks if the system is well posed. The well-posedness conditions states that the system matrices must commute.
    Parameters:
        SS: A 2D commuting state space model
    Returns:
        is_well_posed(Boolean): True iff the system is matrices commute 
    """
    commutator = lie(SS['A'], SS['B'])
    is_well_posed = check_norm_is_zero(commutator)
    return is_well_posed


def get_kalman_decomposition(SS):
    """
    Calculate the kalman decomposition of a state space model.
    Calculations follow: https://en.wikipedia.org/wiki/Kalman_decomposition
    Parameters:
        SS: A state space model
    Returns:
        SS_kalman: The Kalman decomposition of SS. 
    """
    # Get the observability matrix [C^T (CA)^T (CA^2)^T ... (CA^{n-1})^T]^T
    O = get_obs_2D(SS)
    # Get the state sequence matrix [x Ax A^2x ... A^{n-1}x]
    X = get_con_2D(SS)

    # Basis for the reachable subspace, optionally provide the rank=2.
    basis_reach = get_column_space(X, 2)
    # Basis for unobservable space.
    basis_not_obs = get_right_null_space(O.T, 2)

    not_obs_con = np.array(get_intersection(basis_reach, basis_not_obs))
    not_obs_not_con = get_difference_column_space(basis_not_obs, not_obs_con)
    obs_con = get_difference_column_space(basis_reach, not_obs_con)
    obs_not_con = get_right_null_space(np.concatenate((not_obs_con, not_obs_not_con, obs_con), axis=1))

    Tinv_est = np.concatenate((not_obs_con, obs_con, not_obs_not_con, obs_not_con), axis=1)
    T_est = np.linalg.inv(Tinv_est)
    SS_kalman = transformSS(SS, Tinv_est, T_est, 'Kalman form of ' + SS['model_name'])
    return SS_kalman
