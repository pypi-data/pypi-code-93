## All specific to this example routines

def get_system():
    """
    Get an example system, which has 4 eigenmodes, of which 2 observable modes and 1 controllable mode.
    The state space model is placed in the modal canonical form.
    Parameters:

    Returns:

    """
    n = 4
    A = np.diag([k + 1 for k in range(n)])
    B = np.diag([n + k + 1 for k in range(n)])
    assert check_norm_is_zero(lie(A, B))
    C = np.array([k < n // 2 for k in range(n)], dtype=int)
    x0 = np.array([(k + 1) % 2 for k in range(n)])
    return {
        'A': A,
        'B': B,
        'C': C,
        'x0': x0,
        'n': n,
        'model_name': 'Example System'
    }