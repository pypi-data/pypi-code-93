import numpy as np


def geomsurr(W, D, nmean=3, nstd=2, rs=None):
    '''
    Produces a random graph that preserves low-order distance effects
    and node strength distribution.

    Directly adapted from Roberts et al. (2016) NeuroImage 123:379-393,
    available as Matlab code at http://www.sng.org.au/Downloads.

    Parameters
    __________
    W : ndarray
        Weighted connectivity matrix
    D : ndarray
        Physical distance between nodes
    nmean : int
        Polynomial order to preserve mean. Default is 3.
    nstd : int
        Polynomial order to preserve standard deviation. Default is 2.
    rs : int
        Use to set random state. Default to none.

    Returns
    _______
    Wsp : ndarray
        Geometric surrogate connectivity matrix that preserves low-order
        distance effects and node strength distribution
    '''

    if rs is not None:
        np.random.seed(rs)

    # Check if directed
    drct = 0 if np.max(W - W.T) == 0 else 1

    # Initialize weight-preserving matrix
    Wwp = np.zeros_like(W)

    # Check to ensure no self-connectivity
    np.fill_diagonal(W, 0)

    if drct == 0:
        W = np.triu(W)

    # Filter out missing connections
    nz = (W != 0) & (~np.isnan(D))
    w = W[nz]
    d = D[nz]
    logw = np.log(w)

    # Remove mean
    p1 = np.polyfit(d, logw, nmean)
    mnlogw = logw - np.polyval(p1, d)

    # Scale variance
    p2 = np.polyfit(d, abs(mnlogw), nstd)
    stdlogw = mnlogw / np.polyval(p2, d)

    # Shuffle weights
    shuff = np.random.permutation(stdlogw.size)
    surr = stdlogw[shuff]

    # Reapply geometric transforms
    stdsurr = surr * np.polyval(p2, d)
    mnsurr = stdsurr + np.polyval(p1, d)

    # Use surrogate weights as a scaffold to reorder the original weights
    surrlogw = _rank_reorder(logw, mnsurr)
    Wwp[nz] = np.exp(surrlogw)

    if drct == 0:
        Wwp = Wwp + Wwp.T
        W = W + W.T

    # Adjust node strengths
    str_W = W.sum(0)
    str_Wwp = Wwp.sum(0)
    str_Wsp = _rank_reorder(str_W, str_Wwp)
    Wsp = _strength_correct(Wwp, str_Wsp)

    return Wsp


def randomsurr(W, rs=None):
    '''
    Produces a random graph that preserves node strength sequence.

    Parameters
    __________
    W : ndarray
        Weighted connectivity matrix
    rs : int
        Use to set random state. Default to none.

    Returns
    _______
    Wrs : ndarray
        Random surrogate connectivity matrix that preserves node strength
        sequence
    '''

    if rs is not None:
        np.random.seed(rs)

    # Check if directed
    drct = 0 if np.max(W - W.T) == 0 else 1

    # Initialize random surrogate matrix
    Wrs = np.zeros_like(W)

    # Check to ensure no self-connectivity
    np.fill_diagonal(W, 0)

    if drct == 0:
        W = np.triu(W)

    # Filter out self-connectivity
    nz = W != 0
    w = W[nz]
    logw = np.log(w)

    # Shuffle weights
    shuff = np.random.permutation(logw.size)
    surr = logw[shuff]
    Wrs[nz] = np.exp(surr)

    if drct == 0:
        Wrs = Wrs + Wrs.T
        W = W + W.T

    # Adjust node strength sequence
    str_W = W.sum(0)
    Wrs = _strength_correct(Wrs, str_W)
    return Wrs


def _strength_correct(W, ss, nreps=9):
    '''
    Rescales weights in W to make strength sequence converge to ss

    Directly adapted from Roberts et al. (2016) NeuroImage 123:379-393,
    available as Matlab code at http://www.sng.org.au/Downloads.

    Scott Trinkle,
    University of Chicago
    2021

    Parameters
    __________
    W : ndarray
        Weighted connectivity matrix
    ss : ndarray
        Desired strength sequence
    nreps : int
        Number of repetitions for iterative procedure. Default is 9.

    Returns
    _______
    sW : ndarray
        Network with desired strength sequence ss
    '''

    discnodes = W.sum(0) == 0
    sW = W * ss/W.sum(0)[None, :]
    sW[:, discnodes] = 0
    for i in range(nreps):
        sW *= ss/sW.sum(0)[None, :]
        sW[:, discnodes] = 0
        sW = (sW + sW.T) / 2
    return sW


def _rank_reorder(x, scaffold):
    '''
    Reorders the values in x according to the values in scaffold

    Directly adapted from Roberts et al. (2016) NeuroImage 123:379-393,
    available as Matlab code at http://www.sng.org.au/Downloads.

    Scott Trinkle,
    University of Chicago
    2021

    Parameters
    __________
    x : ndarray
        Desired weights
    scaffold : ndarray
        Scaffold weights

    Returns
    _______
    out : ndarray
        Values in x sorted according to the values in scaffold
    '''

    n = np.arange(x.size)
    inds = scaffold.argsort()
    out = np.sort(x)[n[inds].argsort()]
    return out
