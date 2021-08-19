"""
v_stat module: Methods to develop a test of exchangeability

@author: Alan Aw and Jeffrey Spence
"""
import sys
import warnings
import logging
import numpy as np
from gmpy2 import hamdist, pack
from scipy.spatial.distance import pdist, squareform
from scipy.stats import chi2, norm
from numba import njit, prange
sys.path.insert(0, '.')


def _hamming_distance_gmpy(X):
    '''
    Bit-Computation of Pairwise Hamming Distances

    Uses bit operations to quickly compute pairwise Hamming
    distances for a two dimensional array :math:`\\mathbf{X}`. Incurs
    some overhead in packing the bits, so performance
    gains are only for sufficiently large arrays.

    Depends on: ``gmpy2.pack``, ``gmpy2.hamdist``

    Parameters
    ----------
    X : int64 numpy array
        An :math:`N\\times P` array recording :math:`P` features
        in :math:`N` individuals

    Returns
    -------
    float64 numpy array
        A length :math:`{N \\choose 2}` array containing the
        pairwise Hamming distances in order
        :math:`((1, 1), (1, 2), ..., (1, N), (2, 3),\\ldots)`.

    '''
    to_return = []
    n = X.shape[0]

    # Pack numpy int arrays into gmpy2 format bits
    x_pack = []
    for vec in X:
        x_pack.append(pack(vec.tolist(), 1))

    # For each pair compute the hamming distance
    for i in range(n-1):
        for j in range(i+1, n):
            to_return.append(hamdist(x_pack[i], x_pack[j]))

    return np.array(to_return).astype(np.float64)


def _hamming_distances(X):
    '''
    A Hamming Distance Vector Calculator

    Uses a heuristic to decide whether to use bit operations or
    operate directly on a two-dimensional array :math:`\\mathbf{X}`
    to compute the pairwise Hamming distances.

    Depends on: ``_hamming_distance_gmpy``, ``scipy.spatial.distance.pdist``

    Parameters
    ----------
    X : int64 numpy array
        An :math:`N \\times P` array recording :math:`P` features
        in :math:`N` individuals

    Returns
    -------
    float64 numpy array
        A length :math:`{N \\choose 2}` array containing the
        pairwise Hamming distances in order
        :math:`((1, 1), (1, 2), ..., (1, N), (2, 3),\\ldots)`.

    '''
    # If X is a single column, broadcast to N by 1 array
    if len(X.shape) == 1:
        X = X[:, None]

    # If X is sufficientily large, use bit operations to
    # compute hamming distances.
    if X.shape[0] > 100 and X.shape[1] > 64:
        return _hamming_distance_gmpy(X)

    # Otherwise, use scipy.spatial.distance to operate directly on the
    # numpy arrays
    return pdist(X, 'cityblock')


def _calculate_bin_v_stat(X):
    '''
    V Statistic for Binary Arrays

    Computes :math:`V(\\mathbf{X})` for a binary matrix :math:`\\mathbf{X}`.

    Depends on: ``_hamming_distances``

    Parameters
    ----------
    X : int64 numpy array
        An :math:`N \\times P` array recording :math:`P` features in
        :math:`N` individuals

    Returns
    -------
    float
        The :math:`V` statistic, a scalar computing the
        variance of the pairwise Hamming distance between individuals.

    '''
    return np.var(_hamming_distances(X))/X.shape[1]


def _calculate_real_v_stat(X, p):
    '''
    V Statistic for Real Arrays

    Computes :math:`V(\\mathbf{X})` for a real matrix :math:`\\mathbf{X}`,
    where :math:`V(\\mathbf{X})` is the scaled
    variance of :math:`l_p^p` distances
    between the rows of :math:`\\mathbf{X}`.

    Depends on: ``scipy.spatial.distance.pdist``

    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features in
        :math:`N` individuals

    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    float
        The :math:`V` statistic, a scalar computing the variance of the
        pairwise :math:`l_p^p` distance between individuals.

    '''
    return np.var(pdist(X=X, metric='minkowski', p=p)**p)/X.shape[1]


@njit('int64[:, :](int64[:, :], int64[:])', parallel=True)
def _numba_permute(X, block_labels):
    '''
    Resampling Arrays

    Generates a new array :math:`\\mathbf{X}'` under the permutation null.

    Depends on: ``numba.njit``

    Parameters
    ----------
    X : numpy array
        An :math:`N \\times P` array recording :math:`P` features in
        :math:`N` individuals
    block_labels : int64 numpy array
        A length :math:`P` array, with entry :math:`i` containing the
        label of the block that contains feature :math:`i`. Blocks are
        assumed to be labeled 0 to number of blocks - 1.

    Returns
    -------
    numpy array
        An :math:`N \\times P` matrix :math:`\\mathbf{X}'`, which is a
        permuted version of :math:`\\mathbf{X}`.

    '''
    to_return = np.empty_like(X)

    # The number of blocks is the largest label + 1
    num_blocks = np.max(block_labels) + 1

    # Generate the permutations for each block
    perms = [np.random.permutation(X.shape[0]) for i in range(num_blocks)]

    # For each feature apply the permutation from that feature's block
    for i in prange(X.shape[1]):
        to_return[:, i] = X[perms[block_labels[i]], i]

    return to_return


def _naive_block_permute(X, block_labels, p):
    '''
    Resampling V Statistic

    Generates a new array :math:`\\mathbf{X}'` under the permutation null,
    and then returns the :math:`V` statistic computed for :math:`\\mathbf{X}'`.

    Depends on: ``_calculate_bin_v_stat``, ``_calculate_real_v_stat``,
                ``_numba_permute``

    Parameters
    ----------
    X : numpy array
        An :math:`N \\times P` array recording :math:`P` features
        in :math:`N` individuals
    block_labels : int64 numpy array
        A length :math:`P` array, with entry :math:`i` containing the
        label of the block that contains feature :math:`i`. Blocks are
        assumed to be labeled 0 to number of blocks - 1.
    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    float
        :math:`V(\\mathbf{X}')`, where :math:`\\mathbf{X}'` is a
                 resampled version of :math:`\\mathbf{X}`.

    '''
    new_X = _numba_permute(X, block_labels)

    if ((X == 0) | (X == 1)).all():
        return _calculate_bin_v_stat(new_X)
    # else
    return _calculate_real_v_stat(new_X, p)


@njit('float64[:, :](float64[:, :], int64[:, :], int64[:, :])', parallel=True)
def _numba_permute_dists(dists, forward, reverse):
    '''
    Permutation by Caching Distances

    What do you do when you have to compute pairwise
    distances many times, and those damn distances take a long time
    to compute? Answer: You cache the distances and permute the underlying
    sample labels!

    Permutes pairwise distances (Hamming, :math:`l_p^p`, etc.) within blocks.
    Permutations respect the fact that we are actually permuting the
    underlying labels. Arguments `forward` and `reverse` should be precomputed
    using ``_build_forward`` and ``_build_reverse``.

    Depends on: ``numba.njit``

    Parameters
    ----------
    dists : float64 numpy array
        A :math:`B \\times {N \\choose 2}` array, where each column
        records the pairwise distances across all blocks,
        ordered as :math:`((1, 1), (1, 2), ..., (1, N), (2, 3),\\ldots)`
    forward : numpy 2D array
        A :math:`N \\times N` mapping from labels :math:`i, j` to their
        corresponding index in `dists`. Should be
        precomputed using ``_build_forward``
    reverse : numpy 2D array
        A :math:`{N \\choose 2}\\times 2` mapping from an index in `dists` to
        the corresponding labels `i` and `j`. Should be
        precomputed using ``_build_reverse``.

    Returns
    -------
    float64 2D array
        A :math:`B \\times {N \\choose 2}` array containing the
        block-permuted pairwise distances

    '''
    to_return = np.empty_like(dists)

    # iterate over blocks
    for i in prange(dists.shape[0]):

        # generate a permutation of the N labels
        raw_perm = np.random.permutation(forward.shape[0])
        for j in range(dists.shape[1]):
            n1, n2 = reverse[j]     # labels for this index
            n1, n2 = raw_perm[n1], raw_perm[n2]     # permuted labels
            k = forward[n1, n2]     # index for permuted pair
            to_return[i, j] = dists[i, k]
    return to_return


@njit('int64[:, :](int64)')
def _build_forward(n):
    '''
    Map from Indices to Label Pairs

    Builds a map from indexes to pairs of labels.
    This is for caching distances, to avoid recomputing
    distances especially when dealing with high-dimensional (large :math:`P`)
    arrays.

    Depends on: ``numba.njit``

    Parameters
    ----------
    n : int
        Sample size (i.e., :math:`\\mathbf{X}`.shape[0])

    Returns
    -------
    forward : int64 2D array
        An :math:`N\\times N` array, whose entries record the index
        corresponding to the pair of labels (indexed by the matrix dimensions)

    '''
    forward = np.zeros((n, n), dtype=np.int64)
    idx = 0
    for i in range(n-1):
        for j in range(i+1, n):
            forward[i, j] = idx
            forward[j, i] = idx
            idx += 1
    return forward


@njit('int64[:, :](int64)')
def _build_reverse(n):
    '''
    Map from Label Pairs to Indices

    Builds a map from pairs of labels to indexes.
    This is for caching distances, to avoid recomputing
    distances especially when dealing with high-dimensional (large :math:`P`)
    arrays.

    Depends on: ``numba.njit``

    Parameters
    ----------
    n : int
        Sample size (i.e., :math:`\\mathbf{X}`.shape[0])

    Returns
    -------
    reverse : int64 2D array
        An :math:`{N \\choose 2} \\times 2` array, whose entries at
        row :math:`k`, :math:`(k,0)` and :math:`(k,1)`,
        are the indices that make up the :math:`k` th pair in
        the list :math:`((1,1), (1,2), ..., (1,N), (2,3),\\ldots)`

    '''
    reverse = np.zeros(((n*(n-1))//2, 2), dtype=np.int64)
    idx = 0
    for i in range(n-1):
        for j in range(i+1, n):
            reverse[idx, 0] = i
            reverse[idx, 1] = j
            idx += 1
    return reverse


def _cache_block_permute(X,
                         blocks,
                         nruns,
                         p):
    '''
    Resampling Many V Statistics

    Generates a block permutation distribution of :math:`V`.
    Precomputes distances and some indexing arrays to quickly
    generate samples from the block permutation distribution.

    Depends on: ``_hamming_distances``, ``scipy.spatial.distance.pdist``,
    ``_build_forward``, ``_build_reverse``, ``_numba_permute_dists``

    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features
        in :math:`N` individuals
    blocks : List of int64 numpy arrays
        List of arrays, with the :math:`k` th array containing the indices of
        features in block :math:`k`.
    nruns : int
        The number of permutations to perform / resampling number.
    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    array
        Array of floats storing the permutation distribution of the :math:`V`
        statistic

    '''
    # Cache pairwise distances
    if ((X == 0) | (X == 1)).all():
        # Hamming if matrix is binary
        dists = np.array([_hamming_distances(X[:, b]) for b in blocks])
    else:
        # l_p^p distance if matrix is non-binary
        dists = np.array([pdist(X=X[:, b], metric='minkowski', p=p)**p for b in blocks])

    # Cache indexing arrays
    forward = _build_forward(X.shape[0])
    reverse = _build_reverse(X.shape[0])

    to_return = []
    for _ in range(nruns):
        # permute hamming distances for each block
        partials = _numba_permute_dists(dists, forward, reverse)

        # combine hamming distances to total distance, then compute
        # V stat.
        to_return.append(np.var(np.sum(partials, axis=0))/X.shape[1])

    return to_return


def _block_permute(X, blocks, nruns, p):
    '''
    p-value Computation for Test of Exchangeability with Block Dependencies

    Generates a block permutation p-value. Uses a heuristic to decide
    whether to use distance caching or simple block permutations.

    Depends on: ``_calculate_bin_v_stat``, ``_calculate_real_v_stat``,
    ``_naive_block_permute``, ``_cache_block_permute``

    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features
        in :math:`N` individuals
    blocks : List of int64 numpy arrays
        List of arrays, with the :math:`k` th array containing the indices of
        features in block :math:`k`.
    nruns : int
        The number of permutations to perform / resampling number.
    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    float
        The block permutation p-value

    '''
    if ((X == 0) | (X == 1)).all():
        v_stat = _calculate_bin_v_stat(X)
    else:
        v_stat = _calculate_real_v_stat(X, p)

    # Estimated speed up from caching
    speed_ratio = len(blocks) / X.shape[1]

    # If the speedup is minimal, the overhead is not worth it
    if speed_ratio > 0.2:
        # Convert blocks into block labels
        block_labels = np.zeros(X.shape[1], dtype=np.int64)
        for i, b in enumerate(blocks):
            block_labels[b] = i

        # Generate block permutations of V stat
        perms = [_naive_block_permute(X, block_labels, p)
                 for i in range(nruns)]

    # If the speedup is substantial, use caching
    else:
        perms = _cache_block_permute(X, blocks, nruns, p)

    # Proportion of permutation V stats that are at least as
    # large as the observed V stat
    # # Use strictly greater than for conservativeness (should be >= in theory)
    return np.mean(np.array(perms) > v_stat)


def _convolution_of_chi2(val, w1, w2, d1, d2):
    '''
    Tail Probability for Chi Square Convolution Random Variable

    Computes :math:`P(X > val)` where :math:`X = w_1 Y + w_2 Z`, where
    :math:`Y` is chi square distributed with :math:`d_1` degrees of freedom,
    and :math:`Z` is chi square distributed with :math:`d_2` degrees of
    freedom. The probabiity is computed using numerical
    integration of the densities of the two chi square
    distributions. (Method: trapezoidal rule)

    Depends on: ``scipy.stats.chi2``

    Parameters
    ----------
    val : float
        The point at which to evaluate the anti-CDF (aka, observed statistic).
    w1 : float
        The weight of the first chi square rv
    w2 : float
        The weight of the second chi square rv
    d1 : int
        The degrees of freedom of first chi square rv
    d2 : int
        The degrees of freedom of second chi square rv

    Returns
    -------
    float
        :math:`1 - CDF = P(X > val)`, the probability that the rv
        is at least val

    '''
    # Obtain grid points where distribution 1 is changing fast
    min1 = np.max([1e-10, val - w1*(d1 + 10*np.sqrt(2*d1))])
    max1 = np.max([1., val - w1*(d1 - 10*np.sqrt(2*d1))])
    grid1 = np.linspace(min1, max1, num=1000)

    # Obtain grid points where distribution 2 is changing fast
    min2 = np.max([1e-10, w2*(d2 - 10*np.sqrt(2*d2))])
    max2 = w2*(d2 + 10*np.sqrt(2*d2))
    grid2 = np.linspace(min2, max2, num=1000)

    # Obtain grid points up to and around val
    grid_val = np.linspace(1e-10, 6*val, num=1000)

    # Combine grids
    grid = np.sort(
        np.unique(grid1.tolist() + grid2.tolist() + grid_val.tolist())
    )

    # Riemann summands (in logspace):
    # delta_grid * (P(w1*Y > val-x) * P(w2*Z = x))
    delta = np.diff(grid)
    probs = (chi2.logsf(val-grid, df=d1, scale=w1)
             + chi2.logpdf(grid, df=d2, scale=w2))
    riemann = probs[1:] + np.log(delta)

    # Compute integral via Riemann summation and sumexp trick
    maxval = np.max(riemann)
    return np.sum(np.exp(riemann-maxval)) * np.exp(maxval)


def _ind_cov(X, p):
    '''
    Covariance Computation Between Pairs of Distances (Independent Case)

    Computes covariance matrix entries and associated :math:`\\alpha`,
    :math:`\\beta` and :math:`\\gamma` quantities defined
    in Aw, Spence and Song (2021),
    assuming the :math:`P` features of dataset
    :math:`\\mathbf{X}` are independent.

    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features
        in :math:`N` individuals
    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    float 1D array
        The three distinct entries of covariance matrix
        :math:`(\\alpha,\\beta,\\gamma)`, all floats.

    '''
    # Sample size
    n = X.shape[0]
    B = X.shape[1]

    # Compute for binary matrix
    if ((X == 0) | (X == 1)).all():
        # Count columnn sums
        col_p = X.sum(axis=0)

        # Count number of pairs
        n_choose = (n*(n-1))//2
        # Compute alpha, beta and gamma analytically
        alpha = np.mean(
            col_p*(n-col_p) / n_choose
            * (1 - col_p*(n-col_p) / n_choose)
        )
        beta = np.mean(
            0.5 * col_p*(n-col_p) / n_choose
            - (col_p * (n-col_p) / n_choose) ** 2
        )
        gamma = np.mean(
            4 * col_p * (n - col_p) * (col_p - 1) * (n - col_p - 1)
            / n / (n-1) / (n-2) / (n-3)
            - (col_p * (n - col_p) / n_choose) ** 2
        )
    # Compute for non-binary matrix
    else:
        # Calculate l_p^p distances for each feature
        blocks = [np.array([i]) for i in range(B)]
        dists = np.array([pdist(X=X[:, b], metric='minkowski', p=p)**p for b in blocks])

        # Compute average distance for each feature
        mu = np.mean(dists, axis=1)

        # Compute variance of d(X_1,X_2), aka alpha
        alpha = np.sum(dists**2, axis=1) / n / (n-1) * 2 - mu**2
        alpha = np.mean(alpha)

        # Create an array for easy computation of other covariances
        dist_mat = np.zeros((B, n, n))
        dist_mat.T[np.triu_indices(n, 1)] = dists.T
        dist_mat += np.transpose(dist_mat, axes=[0, 2, 1])
        nu_i = np.sum(dist_mat, axis=2)

        # Compute nu = \sum_i \sum_j d(X_i, X_j)
        nu = n * (n-1) * mu

        # Compute E[d(X_1,X_2) * d(X_1,X_3)] and beta
        beta = (dist_mat * (nu_i[:, :, None] - dist_mat)).sum(axis=(1, 2))
        beta /= (n * (n-1) * (n-2))
        beta -= mu**2
        beta = np.mean(beta)

        # Compute E[d(X_1,X_2) * d(X_3,X_4)] and gamma
        gamma = (dist_mat * (nu[:, None, None]
                             - 2*nu_i[:, :, None]
                             - 2*nu_i[:, None, :]
                             + 2*dist_mat)).sum(axis=(1, 2))
        gamma /= (n * (n-1) * (n-2) * (n-3))
        gamma -= mu**2
        gamma = np.mean(gamma)

    return alpha, beta, gamma


def _chi2_weights(alpha, beta, gamma, n):
    '''
    Get Chi Square Weights

    Computes convolution weights for the asymptotic random variable
    from the covariance entries :math:`\\alpha`, :math:`\\beta`
    and :math:`\\gamma` obtained from :math:`\\mathbf{X}`.

    Parameters
    ----------
    alpha : float
        The variance of :math:`d(X_1, X_2)`
    beta : float
        The covariance of :math:`d(X_1,X_2)` and :math:`d(X_1,X_3)`
    gamma : float
        The covariance of :math:`d(X_1,X_2)` and :math:`d(X_3,X_4)`
    n : int
        Sample size (i.e., :math:`\\mathbf{X}`.shape[0])

    Returns
    -------
    1D floats
        Two floats, :math:`w_1` and :math:`w_2`, where :math:`w_1` is the
        weight for the chi square distribution with :math:`n-1` degrees of
        freedom and :math:`w_2` is the weight for the chi square distribution
        with :math:`{n-1 \\choose 2} - 1` degrees of freedom.

    '''
    n_choose = (n*(n-1))//2
    w1 = (alpha + (n-4)*beta - (n-3)*gamma) / n_choose
    w2 = (alpha - 2*beta + gamma) / n_choose
    return w1, w2


def _ind_large_p(X, p):
    '''
    Approximate Test of Exchangeability (Large P)

    Computes the large :math:`P` asymptotic p-value for dataset
    :math:`\\mathbf{X}`, assuming its :math:`P` features are independent.

    Depends on: ``scipy.stats.chi2``, ``_calculate_bin_v_stat``,
                ``_convolution_of_chi2``

    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features in
        :math:`N` individuals
    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    float
        The approximate p-value for :math:`\\mathbf{X}`, a float.

    '''
    n = X.shape[0]
    w1, w2 = _chi2_weights(*_ind_cov(X, p), n)
    d1 = n - 1
    d2 = ((n-1)*(n-2))//2 - 1
    if ((X == 0) | (X == 1)).all():
        v_stat = _calculate_bin_v_stat(X)
    else:
        v_stat = _calculate_real_v_stat(X, p)
    return _convolution_of_chi2(v_stat, w1, w2, d1, d2)


def _ind_large_p_large_n(X, p):
    '''
    Approximate Test of Exchangeability (Large N, Large P)

    Computes the large :math:`N`, large :math:`P` asymptotic p-value
    for :math:`\\mathbf{X}` assuming its :math:`P` features are independent.

    Depends on: ``_calculate_bin_v_stat``, ``_calculate_real_v_stat``,
    ``_ind_cov``, ``_chi2_weights, scipy.stats.norm``

    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features in
        :math:`N` individuals
    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    float
        The approximate p-value for :math:`\\mathbf{X}`, a float.

    '''
    if ((X == 0) | (X == 1)).all():
        v_stat = _calculate_bin_v_stat(X)
    else:
        v_stat = _calculate_real_v_stat(X, p)

    n = X.shape[0]
    d1 = n-1
    d2 = ((n-1)*(n-2))//2 - 1   # (n-1 choose 2) - 1

    alpha, beta, gamma = _ind_cov(X, p)
    w1, w2 = _chi2_weights(alpha, beta, gamma, n)

    mean = w1*d1 + w2*d2
    variance = w1**2 * 2 * d1 + w2**2 * 2 * d2

    # anti-CDF of Gaussian
    return norm.sf(v_stat, loc=mean, scale=np.sqrt(variance))


def _block_cov(X, blocks, p):
    '''
    Covariance Computations between Pairs of Distances (Block Dependency Case)

    Computes covariance matrix entries and associated
    :math:`\\alpha`, :math:`\\beta` and :math:`\\gamma`
    quantities, for partitionable
    features that are grouped into blocks. Computes the unique entries of the
    asymptotic covariance matrix of the pairwise
    distances in :math:`O(N^2)` time.

    This is used in the large :math:`B` asymptotics of the permutation test.

    Depends on: ``_hamming_distances``, ``scipy.spatial.distance.pdist``

    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features in
        :math:`N` individuals
    blocks : List of int64 numpy arrays
        List of arrays, with the :math:`k` th array containing the indices of
        features in block :math:`k`.
    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    float 1D array
        The three distinct entries of covariance matrix
        :math:`(\\alpha,\\beta,\\gamma)`, all floats.

    '''

    # Dimensions
    n = X.shape[0]
    P = X.shape[1]
    B = len(blocks)

    # Calculate distances for each block
    if ((X == 0) | (X == 1)).all():
        dists = np.array([_hamming_distances(X[:, b]) for b in blocks])
    else:
        dists = np.array([pdist(X=X[:, b], metric='minkowski', p=p)**p for b in blocks])

    # Compute the average distance
    mu = np.mean(dists, axis=1)

    # Compute variance of d(X_1, X_2)
    alpha = np.sum(dists**2, axis=1) / n / (n-1) * 2 - mu**2
    alpha = np.mean(alpha)

    # Compute nu = \sum_i \sum_j d(X_i, X_j)
    nu = n * (n-1) * mu

    # Reshape distances into a matrix to
    # easily compute nu_i = \sum_j d(X_i, X_j)
    dist_mat = np.zeros((B, n, n))
    dist_mat.T[np.triu_indices(n, 1)] = dists.T
    dist_mat += np.transpose(dist_mat, axes=[0, 2, 1])
    nu_i = np.sum(dist_mat, axis=2)

    # Compute the covariance of d(X_1, X_2) and d(X_1, X_3)
    beta = (dist_mat * (nu_i[:, :, None] - dist_mat)).sum(axis=(1, 2))
    beta /= (n * (n-1) * (n-2))
    beta -= mu**2
    beta = np.mean(beta)

    # Compute the covariance of d(X_1, X_2) and d(X_3, X_4)
    gamma = (dist_mat * (nu[:, None, None]
                         - 2*nu_i[:, :, None]
                         - 2*nu_i[:, None, :]
                         + 2*dist_mat)).sum(axis=(1, 2))
    gamma /= (n * (n-1) * (n-2) * (n-3))
    gamma -= mu**2
    gamma = np.mean(gamma)

    # V-stat is scaled by 1/P, but covariances above are
    # scaled by 1/B
    return alpha*B/P, beta*B/P, gamma*B/P


def _block_large_p(X, blocks, p):
    '''
    Approximate for Exchangeability Test (Large P, Block Dependency)

    Computes the large :math:`P` asymptotic p-value for :math:`\\mathbf{X}`,
    assuming its :math:`P` features are independent within specified blocks.

    Depends on: `_chi2_weights`, `_block_cov`, `_calculate_bin_v_stat`,
    `_calculate_real_v_stat`, `_convolution_of_chi2`

    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features in
        :math:`N` individuals
    blocks : List of int64 numpy arrays
        List of arrays, with the :math:`k` th array containing the indices of
        features in block :math:`k`.
    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    float
        The approximate p-value for :math:`\\mathbf{X}`.

    '''
    n = X.shape[0]
    w1, w2 = _chi2_weights(*_block_cov(X, blocks, p), n)
    d1 = n - 1
    d2 = ((n-1)*(n-2))//2 - 1
    if ((X == 0) | (X == 1)).all():
        v_stat = _calculate_bin_v_stat(X)
    else:
        v_stat = _calculate_real_v_stat(X, p)
    return _convolution_of_chi2(v_stat, w1, w2, d1, d2)


def _block_large_p_large_n(X, blocks, p):
    '''
    Approximate Exchangeability Test (Large P, Large N, Block Dependency)

    Computes the large :math:`P`, large :math:`N` asymptotic p-value
    for :math:`\\mathbf{X}`,
    assuming its :math:`P` features are are
    independent within specified blocks.

    Depends on: ``_chi2_weights``, ``_block_cov``, ``_calculate_bin_v_stat``,
    ``_calculate_real_v_stat``, ``scipy.stats.norm``

    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features
        in :math:`N` individuals
    blocks : List of int64 numpy arrays
        List of arrays, with the :math:`k` th array containing the indices of
        features in block :math:`k`.
    p : float
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`

    Returns
    -------
    float
        The approximate p-value for :math:`\\mathbf{X}`.

    '''
    if ((X == 0) | (X == 1)).all():
        v_stat = _calculate_bin_v_stat(X)
    else:
        v_stat = _calculate_real_v_stat(X, p)

    n = X.shape[0]
    d1 = n-1
    d2 = ((n-1)*(n-2))//2 - 1   # (n-1 choose 2) - 1

    w1, w2 = _chi2_weights(*_block_cov(X, blocks, p), n)

    mean = w1*d1 + w2*d2
    variance = w1**2 * 2 * d1 + w2**2 * 2 * d2

    # anti-CDF of Gaussian
    return norm.sf(v_stat, loc=mean, scale=np.sqrt(variance))


def _dist_data_permute(dist_list, nruns):
    '''
    p-value Computation for Test of Exchangeability using Distance Data

    Generates a permutation null distribution of :math:`V`
    by storing the provided list of distance data as
    a :math:`B \\times {N \\choose 2}` array, and then permuting
    the underlying indices of each individual to generate
    resampled arrays. The observed :math:`V` statistic
    is also computed from the distance data. The p-value is
    computed from the null distribution and the observed
    :math:`V` statistic.

    Each element of `dist_list` should be the same type.
    They can either all be distance matrices (shape :math:`(N,N)`),
    or all be distance vectors (shape :math:`({N \\choose 2},)`).

    Depends on: ``scipy.spatial.distance.squareform``, ``_build_forward``,
    ``_build_reverse``, ``_numba_permute_dists``

    Parameters
    ----------
    dist_list : List of numpy arrays (matrix / vector)
        The list of pairwise distances
    nruns : int
        The number of permutations to perform / resampling number.

    Returns
    -------
    float
        The block permutation p-value.

    '''
    # Get number of independent blocks
    B = len(dist_list)

    # Check if dist_list is in vector form
    if len(dist_list[0].shape) == 1:
        logging.info('Distances are in vector form')
        # Get sample size
        n = squareform(dist_list[0]).shape[0]
        # Convert to nd.array
        dists = np.array(dist_list)
    else:
        logging.info('Distances are in matrix form')
        n = dist_list[0].shape[0]
        # Flatten and convert to nd.array
        dists = np.array([squareform(dist_list[b]) for b in range(B)])

    # Get observed V
    v_stat = np.var(np.sum(dists, axis=0))/B

    # Cache indexing arrays
    forward = _build_forward(n)
    reverse = _build_reverse(n)

    perms = []
    for _ in range(nruns):
        # Permute distances for each block
        partials = _numba_permute_dists(dists, forward, reverse)

        # Combine distances to total distance, then compute
        # V stat.
        perms.append(np.var(np.sum(partials, axis=0))/B)

    # Proportion of permutation V stats that are at least as
    # large as the observed V stat
    # # Use strictly greater than for conservativeness (should be >= in theory)
    return np.mean(np.array(perms) > v_stat)


def _dist_data_large_p(dist_list):
    '''
    Asymptotic Test of Exchangeability Using Distance Data

    Generates an asymptotic distribution of :math:`V`, by
    storing the provided list of distance data as
    a :math:`B\\times {N \\choose 2}` array,
    and then using large-:math:`P` theory to
    generate the asymptotic null distribution. The observed :math:`V`
    statistic is also computed from the distance data.

    Each element of `dist_list` should be the same type.
    They can either all be distance matrices (shape :math:`(N,N)`),
    or all be distance vectors (shape :math:`({N \\choose 2},)`).

    Depends on: ``scipy.spatial.distance.squareform``, ``_build_forward``,
    ``_build_reverse``, ``_numba_permute_dists``

    Parameters
    ----------
    dist_list : List of numpy arrays (matrix / vector)
        The list of pairwise distance

    Returns
    -------
    float
        The block permutation p-value.

    '''
    # Get number of independent blocks
    B = len(dist_list)

    # Check if dist_list is in vector form
    if len(dist_list[0].shape) == 1:
        logging.info('Distances are in vector form')
        # Get sample size
        n = squareform(dist_list[0]).shape[0]
        # Convert to nd.array
        dists = np.array(dist_list)
    else:
        logging.info('Distances are in matrix form')
        n = dist_list[0].shape[0]
        # Flatten and convert to nd.array
        dists = np.array([squareform(dist_list[b]) for b in range(B)])

    # Get observed V
    v_stat = np.var(np.sum(dists, axis=0))/B

    # Compute the average distance
    mu = np.mean(dists, axis=1)

    # Compute variance of d(X_1, X_2)
    alpha = np.sum(dists**2, axis=1) / n / (n-1) * 2 - mu**2
    alpha = np.mean(alpha)

    # Compute nu = \sum_i \sum_j d(X_i, X_j)
    nu = n * (n-1) * mu

    # Reshape distances into a matrix to
    # easily compute nu_i = \sum_j d(X_i, X_j)
    dist_mat = np.zeros((B, n, n))
    dist_mat.T[np.triu_indices(n, 1)] = dists.T
    dist_mat += np.transpose(dist_mat, axes=[0, 2, 1])
    nu_i = np.sum(dist_mat, axis=2)

    # Compute the covariance of d(X_1, X_2) and d(X_1, X_3)
    beta = (dist_mat * (nu_i[:, :, None] - dist_mat)).sum(axis=(1, 2))
    beta /= (n * (n-1) * (n-2))
    beta -= mu**2
    beta = np.mean(beta)

    # Compute the covariance of d(X_1, X_2) and d(X_3, X_4)
    gamma = (dist_mat * (nu[:, None, None]
                         - 2*nu_i[:, :, None]
                         - 2*nu_i[:, None, :]
                         + 2*dist_mat)).sum(axis=(1, 2))
    gamma /= (n * (n-1) * (n-2) * (n-3))
    gamma -= mu**2
    gamma = np.mean(gamma)

    # Get weights for chi-square distribution
    w1, w2 = _chi2_weights(alpha, beta, gamma, n)

    # Compute degrees of freedom
    d1 = n - 1
    d2 = ((n-1)*(n-2))//2 - 1

    # Return
    return _convolution_of_chi2(v_stat, w1, w2, d1, d2)


def get_p_value(X, blocks=None,
                large_p=False,
                large_n=False,
                num_perms=1000,
                p=2):
    '''
    **A Non-parametric Test of Exchangeability and Homogeneity**

    Computes the p-value of a multivariate dataset :math:`\\mathbf{X}`, which
    informs the user if the sample is
    exchangeable at a given significance level,
    while simultaneously accounting for feature dependencies.
    See Aw, Spence, and Song (2021) for details.

    Automatically detects if dataset is binary, and runs the Hamming distance
    version of test if so. Otherwise, computes the squared Euclidean distance
    between individuals and evaluates whether
    the variance of Euclidean distances,
    :math:`V`, is atypically large under
    the null hypothesis of exchangeability.

    Note the user may tweak the choice of
    power :math:`p` if they prefer an :math:`l_p^p`
    distance other than Euclidean (:math:`p=2`).

    Under the hood, the variance statistic :math:`V` is computed efficiently.
    Moreover, the user can specify their
    choice of block permutations, large :math:`P`
    asymptotics, or large :math:`P` and
    large :math:`N` asymptotics. The latter two
    return reasonbly accurate p-values for moderately large dimensionalities.

    User recommendations: When the number of independent blocks :math:`B` or
    number of independent features :math:`P` is at least :math:`50`, it is safe
    to use large :math:`P` asymptotics.
    If :math:`P` or :math:`B` is small, stick
    with permutations.

    Depends on: ``_ind_large_p``, ``_ind_large_p_large_n``,
    ``_block_large_p``, ``_block_large_p_large_n``, ``_block_permute``


    Parameters
    ----------
    X : float numpy array
        An :math:`N \\times P` array recording :math:`P` features
        in :math:`N` individuals
    blocks : List of int64 numpy arrays, optional
        List of arrays, with the :math:`k` th array containing the indices of
        features in block :math:`k`. The default is None.
    large_p : boolean, optional
        Indicates whether large :math:`P` asymptotics
        are used to determine the approximate
        null distribution. The default is False.
    large_n : boolean, optional
        Indicates whether large :math:`P`, large :math:`N` asymptotics
        are used to determine the approximate
        null distribution. The default is False.
    num_perms : int, optional
        Determines the number of
        permutations to perform if not using an
        asymptotic test.  If either `large_p` or `large_n`
        is true, `num_perms` is ignored. The default is 1000.
    p : float, optional
        The Minkowski power, :math:`l_p^p = (x_1^p+\\ldots+x_n^p)`.
        The default is 2.

    Raises
    ------
    IOError
        These are errors associated with assertions and unit tests.
    NotImplementedError
        This error corresponds to the large :math:`N`, small :math:`P`
        asymptotics, which is currently not implemented.

    Returns
    -------
    float
        The p-value computed for the :math:`V`
        statistic of :math:`\\mathbf{X}`.

    '''
    # Check that arguments are correct

    # Check data matrix, X
    if not isinstance(X, np.ndarray):
        raise IOError('X must be a 2D numpy array')
    if len(X.shape) != 2:
        raise IOError('X must be a 2D numpy array')
    if ((X == 0) | (X == 1)).all():
        col_sums = X.sum(axis=0)
        if np.any(col_sums == 0) or np.any(col_sums == X.shape[0]):
            warnings.warn('There exist columns with all '
                          'ones or all zeros for binary X.')

    # Check blocks
    if blocks is not None:
        for b in blocks:
            if not isinstance(b, np.ndarray):
                raise IOError('Each block in blocks must be a 1D int64 '
                              'numpy array')
            if b.dtype != np.int64:
                raise IOError('Each block in blocks must be a 1D int64 '
                              'numpy array')
            if len(b.shape) != 1:
                raise IOError('Each block in blocks must be a 1D int64 '
                              'numpy array')
        combined = np.concatenate(blocks)
        if combined.shape[0] != X.shape[1]:
            raise IOError('Each feature must be in exactly one block')
        if len(np.unique(combined)) != X.shape[1]:
            raise IOError('Each feature must be in exactly one block')

    # Check large_p and large_n
    if not isinstance(large_p, bool):
        raise IOError('large_p must be a boolean')
    if not isinstance(large_n, bool):
        raise IOError('large_n must be a boolean')

    # Check num_perms
    if not isinstance(num_perms, int):
        raise IOError('num_perms must be an int')

    # Determine which test to perform
    if large_p and large_n and blocks is None:
        return _ind_large_p_large_n(X, p)

    if large_p and large_n and blocks is not None:
        return _block_large_p_large_n(X, blocks, p)

    if not large_p and large_n:
        raise NotImplementedError('Large N but small P asymptotics '
                                  'have not been implemented.')

    if large_p and not large_n and blocks is None:
        return _ind_large_p(X, p)

    if large_p and not large_n and blocks is not None:
        return _block_large_p(X, blocks, p)

    # Block permute
    if not large_p and not large_n and blocks is None:
        blocks = [np.array([i]) for i in range(X.shape[1])]
    return _block_permute(X, blocks, num_perms, p)


def dist_data_p_value(dist_list, large_p=False, num_perms=1000):
    '''
    **A Non-parametric Test for Exchangeability (Distance List Version)**

    Computes the p-value of a multivariate dataset, which
    informs the user if the sample is exchangeable at a given
    significance level, while simultaneously accounting for
    feature dependencies.

    This version takes in a list of distances recording pairwise distances
    between individuals across either :math:`P` independent features or
    :math:`B` independent blocks of features.

    Each element of `dist_list` should be the same type.
    They can either all be distance matrices (shape :math:`(N,N)`),
    or all be distance vectors (shape :math:`({N \\choose 2},)`).

    Depends on: ``_dist_data_large_p``, ``_dist_data_permute``

    Parameters
    ----------
    dist_list : List of numpy arrays (matrix / vector)
        The list of pairwise distances
    large_p : boolean, optional
        Indicates whether large P asymptotics
        are used to determine the approximate
        null distribution. The default is False.
    num_perms : int
        The number of permutations to perform / resampling number.
        The default is 1000.

    Returns
    -------
    float
        The p-value.

    '''
    # Check that dist_list is a list
    if not isinstance(dist_list, list):
        raise IOError('dist_list must be a list')

    # Check all distance matrices have the same dimension
    data_dims = [dist_list[b].shape for b in range(len(dist_list))]
    if not all(element == data_dims[0] for element in data_dims):
        raise IOError('Not all dist_list elements have the same dimension')

    # Check that large_p and no. independent features are consistent
    if (len(dist_list) < 50 and large_p):
        raise IOError('Too few independent distances for '
                      'approximation to be valid')

    # Get p-value
    if large_p:
        return _dist_data_large_p(dist_list)
    # else
    return _dist_data_permute(dist_list, num_perms)
