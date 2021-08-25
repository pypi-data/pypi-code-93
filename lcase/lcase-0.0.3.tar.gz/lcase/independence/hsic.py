
import numpy as np
import numpy.matlib
import scipy
import scipy.linalg
import scipy.io
from sklearn.cluster import KMeans
from scipy.stats import gamma
from statsmodels.nonparametric import bandwidths

__all__ = ['get_kernel_width', 'get_gram_matrix', 'hsic_teststat', 'hsic_test_gamma']


def get_kernel_width(X):
    """Calculate the bandwidth to median distance between points.
    Use at most 100 points (since median is only a heuristic,
    and 100 points is sufficient for a robust estimate).
    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        Training data, where ``n_samples`` is the number of samples
        and ``n_features`` is the number of features.
    Returns
    -------
    float
        The bandwidth parameter.
    """
    n_samples = X.shape[0]
    if n_samples > 100:
        X_med = X[:100, :]
        n_samples = 100
    else:
        X_med = X

    G = np.sum(X_med * X_med, 1).reshape(n_samples, 1)
    Q = np.tile(G, (1, n_samples))
    R = np.tile(G.T, (n_samples, 1))

    dists = Q + R - 2 * np.dot(X_med, X_med.T)
    dists = dists - np.tril(dists)
    dists = dists.reshape(n_samples ** 2, 1)

    return np.sqrt(0.5 * np.median(dists[dists > 0]))

def _rbf_dot(X, Y, width):
    """Compute the inner product of radial basis functions."""
    n_samples_X = X.shape[0]
    n_samples_Y = Y.shape[0]

    G = np.sum(X * X, 1).reshape(n_samples_X, 1)
    H = np.sum(Y * Y, 1).reshape(n_samples_Y, 1)
    Q = np.tile(G, (1, n_samples_Y))
    R = np.tile(H.T, (n_samples_X, 1))
    H = Q + R - 2 * np.dot(X, Y.T)

    return np.exp(-H / 2 / (width ** 2))

def get_gram_matrix(X, width):
    """Get the centered gram matrices.
    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        Training data, where ``n_samples`` is the number of samples
        and ``n_features`` is the number of features.
    width : float
        The bandwidth parameter.
    Returns
    -------
    K, Kc : array
        the centered gram matrices.
    """
    n = X.shape[0]
    H = np.eye(n) - 1 / n * np.ones((n, n))

    K = _rbf_dot(X, X, width)
    Kc = np.dot(np.dot(H, K), H)

    return K, Kc

def hsic_teststat(Kc, Lc, n):
    """get the HSIC statistic.
    Parameters
    ----------
    K, Kc : array
        the centered gram matrices.
    n : float
        the number of samples.
    Returns
    -------
    float
        the HSIC statistic.
    """
    # test statistic m*HSICb under H1
    return 1 / n * np.sum(np.sum(Kc.T * Lc))

def hsic_test_gamma(X, Y, bw_method='mdbs'):
    """get the HSIC statistic.
    Parameters
    ----------
    X, Y : array-like, shape (n_samples, n_features)
        Training data, where ``n_samples`` is the number of samples
        and ``n_features`` is the number of features.
    bw_method : str, optional (default=``mdbs``)
        The method used to calculate the bandwidth of the HSIC.
        * ``mdbs`` : Median distance between samples.
        * ``scott`` : Scott's Rule of Thumb.
        * ``silverman`` : Silverman's Rule of Thumb.
    Returns
    -------
    test_stat : float
        the HSIC statistic.
    p : float
        the HSIC p-value.
    """
    X = X.reshape(-1, 1) if X.ndim == 1 else X
    Y = Y.reshape(-1, 1) if Y.ndim == 1 else Y

    if bw_method == 'scott':
        width_x = bandwidths.bw_scott(X)
        width_y = bandwidths.bw_scott(Y)
    elif bw_method == 'silverman':
        width_x = bandwidths.bw_silverman(X)
        width_y = bandwidths.bw_silverman(Y)
    # Get kernel width to median distance between points
    else:
        width_x = get_kernel_width(X)
        width_y = get_kernel_width(Y)

    # these are slightly biased estimates of centered gram matrices
    K, Kc = get_gram_matrix(X, width_x)
    L, Lc = get_gram_matrix(Y, width_y)

    # test statistic m*HSICb under H1
    n = X.shape[0]
    bone = np.ones((n, 1))
    test_stat = hsic_teststat(Kc, Lc, n)

    var = (1 / 6 * Kc * Lc) ** 2
    # second subtracted term is bias correction
    var = 1 / n / (n - 1) * (np.sum(np.sum(var)) - np.sum(np.diag(var)))
    # variance under H0
    var = 72 * (n - 4) * (n - 5) / n / (n - 1) / (n - 2) / (n - 3) * var

    K = K - np.diag(np.diag(K))
    L = L - np.diag(np.diag(L))
    mu_X = 1 / n / (n - 1) * np.dot(bone.T, np.dot(K, bone))
    mu_Y = 1 / n / (n - 1) * np.dot(bone.T, np.dot(L, bone))
    # mean under H0
    mean = 1 / n * (1 + mu_X * mu_Y - mu_X - mu_Y)

    alpha = mean ** 2 / var
    # threshold for hsicArr*m
    beta = np.dot(var, n) / mean
    p = 1 - gamma.cdf(test_stat, alpha, scale=beta)[0][0]

    return test_stat, p


# conditional hsic
def hsiccondTestIC(X,Y,Z,alpha,shuffles):
    # Statistical test for kernel conditional independence of X and Y given Z with
    # incomplete Cholesky factorization for low rank approximation of Gram matrices
    #
    # Arguments:
    # X          n x p vector of data points
    # Y          n x m vector of data points
    # Z          n x r vector of data points
    # alpha      significance level
    # shuffles   number of shuffles for the permutation test
    #
    # Output:
    # sig        boolean indicator of whether the test was significant for the given alpha
    # p          resulting p-value
    X = X.reshape(-1, 1) if X.ndim == 1 else X
    Y = Y.reshape(-1, 1) if Y.ndim == 1 else Y
    Z = Z.reshape(-1, 1) if Z.ndim == 1 else Z
    X = np.asmatrix(X)
    Y = np.asmatrix(Y)
    Z = np.asmatrix(Z)

    n = X.shape[0]
    if (n != Y.shape[0] or n != Z.shape[0]):
        raise Exception('X, Y, and Z must have the same number of data points')

    if (alpha < 0 or alpha > 1):
        raise Exception('alpha must be between 0 and 1')

    if (shuffles <= 0):
        raise Exception('number of shuffles must be a positive integer');

    # smoothing constant for conditional cross covariance operator
    epsilon = 1e-4
    # threshold for eigenvalues to consider in low rank Gram matrix approximations
    tol = 1e-4

    # augment X and Y for conditional test
    X = np.concatenate([X, Z], axis=1)
    Y = np.concatenate([Y, Z], axis=1)

    # set kernel size to median distance between points
    maxpoints = 1000
    sigx = medbw(X, maxpoints)
    sigy = medbw(Y, maxpoints)
    sigz = medbw(Z, maxpoints)

    # low rank approximation of Gram matrices using incomplete Cholesky factorization
    K, Pk = inchol(X, sigx, tol)
    L, Pl = inchol(Y, sigy, tol)
    M, Pm = inchol(Z, sigz, tol)

    # center Gram matrices factoring in permutations made during low rank approximation
    Kc = K[Pk,:] - np.tile((np.sum(K, axis=0) / n), (n, 1))
    Lc = L[Pl,:] - np.tile((np.sum(L, axis=0) / n), (n, 1))
    Mc = M[Pm,:] - np.tile((np.sum(M, axis=0) / n), (n, 1))

    # compute HSIC dependence value
    testStat = hsiccondIC(Kc, Lc, Mc, epsilon)

    # first cluster Z;
    nc = pickK(Z)
    clf = KMeans(n_clusters=nc, max_iter=1000)
    clf.fit(Z)
    clusters = clf.labels_

    # simulate null distribution and permutation test
    nullapprox = np.matlib.zeros((shuffles, 1))
    for i in range(shuffles):
        # permute within clusters
        Plnew = np.arange(n)
        for j in range(nc):
            indj = np.where(clusters == j)
            Plnew[indj] = np.random.permutation(Plnew[indj])
        # centered Gram matrix for new sample
        newLc = Lc[Plnew, :]
        # compute HSIC dependence value for new sample
        nullapprox[i] = hsiccondIC(Kc, newLc, Mc, epsilon)

    # get p-value from empirical cdf
    p = len(np.where(nullapprox >= testStat)[0]) / shuffles

    # determine significance
    sig = (p <= alpha)
    return sig,p,testStat

def medbw(X, maxpoints):
    # Median distance heuristic for setting RBF kernel bandwidth
    #
    # Description:
    # Uses the median distance between points for setting the bandwidth for RBF kernels.
    #
    # Arguments:
    # X             n x p matrix of n datapoints with dimensionality p
    # maxpoints     maximum number of points to use when setting the bandwidth
    #
    # Output:
    # sigma         value for bandwidth
    if (maxpoints < 1):
        raise Exception('maxpoints must be a positive integer')

    # truncates data if more points than maxpoints
    n = X.shape[0]
    if (n > maxpoints):
        med = X[0:maxpoints, :]
        n = maxpoints
    else:
        med = X

    # finds median distance between points
    G = np.sum(np.multiply(med, med), axis=1)
    Q = np.tile(G, (1, n))
    R = np.tile(G.T, (n, 1))
    dists = Q + R - 2 * med * med.T
    dists = dists - np.tril(dists)
    dists = dists.reshape(n ** 2, 1)
    sigma = np.sqrt(0.5 * np.median(np.asarray(dists[np.where(dists > 0)])))
    return sigma

def inchol(X,sigma,tol):
    # Incomplete Cholesky factorization with RBF kernel
    #
    # Description:
    # Finds low rank approximation of RBF kernel Gram matrix K = PGG'P for the
    # n x p data matrix X. Here, K is an n x n Gram matrix, G is n x m with m << n,
    # and P is a permutation matrix.
    #
    # Arguments:
    # X       n x p data matrix
    # sigma   bandwidth for RBF kernel
    # tol     threshold for remaining eigenvalues to consider
    #
    # Output:
    # G       n x m matrix (m << n)
    # P       n vector of permutation indices
    #
    #
    # Adapted from Francis Bach's Cholesky with side information implementation
    if (sigma <= 0):
        raise Exception('sigma must be > 0')

    if (tol <= 0):
        raise Exception('tol must be > 0')
    n = X.shape[0]
    # begin with full matrix
    G = np.matlib.zeros((n, n))
    # using RBF kernel so diagonal entries are ones
    diagK = np.matlib.ones((n, 1))
    # permutation indices;
    P = np.matlib.arange(n)
    # updated diagonal elements
    D = diagK

    # construct columns of K until threshold is met
    for k in range(n):

        # select next most informative pivot
        best = D[k]
        bestInd = k
        for j in range(k, n):
            if (D[j] > best / .99):
                best = D[j]
                bestInd = j

        # threshold met so remove columns to the right and break
        if best < tol:
            G = G[:, 0:k]
            break

        # move pivot to the front
        pk = P[k]
        P[k] = P[bestInd]
        P[bestInd] = pk
        dk = D[k].copy()
        D[k] = D[bestInd]
        D[bestInd] = dk

        # update existing columns
        for j in range(0, k):
            gk = G[k, j]
            G[k, j] = G[bestInd, j]
            G[bestInd, j] = gk

        # compute new Cholesky column
        G[k, k] = np.sqrt(D[k])
        G[k + 1: n, k] = 1 / G[k, k] * (rbf(X[P[k + 1:n], :], np.tile(X[P[k], :], ((n - k - 1), 1)), sigma) - G[k + 1: n, 0:k]*(G[k, 0:k]).T)

        # update diagonal
        D[k + 1: n] = D[k + 1: n] - np.power(G[k + 1: n, k], 2)
        D[k] = 0
    return G, P

def rbf(x1,x2,sigma):
    # RBF kernel evaluation
    #
    # Description:
    # Evaluates RBF kernel for n points
    #
    # Input:
    # x1      n x p matrix (n points with dimensionality p)
    # x2      n x p matrix (n points with dimensionality p)
    # sigma   kernel bandwidth
    #
    # Output:
    # k       n x 1 matrix of k(x1,x2) evaluations
    if (x1.shape[0] != x2.shape[0]):
        raise Exception('x1 and x2 must contain the same number of data points')
    if (x1.shape[1] != x2.shape[1]):
        raise Exception('x1 and x2 must be of the same dimensionality')
    if (sigma <= 0):
        raise Exception('sig must be > 0')

    k = np.exp(-.5 * np.sum(np.power((x1 - x2), 2), axis=1) / (sigma ** 2))
    return k

def hsiccondIC(Gx,Gy,Gz,epsilon):
    # Conditional dependence operator empirical estimator with incomplete Choleksy
    # factorization for low rank approximation of Gram matrices
    #
    # Arguments:
    # Gx        low rank approximation for centered Gram matrix for X
    # Gy        low rank approximation for centered Gram matrix for Y
    # Gz        low rank approximation for centered Gram matrix for Z
    # epsilon   the smoothing constant
    #
    # Output:
    # emphsic   the test statistic
    n = Gx.shape[0]
    if (n != Gy.shape[0] or n != Gz.shape[0]):
        raise Exception('Gx, Gy, and Gz must have the same number of rows')
    if (epsilon <= 0):
        raise Exception('epsilon must > 0')

    mx = Gx.shape[1]
    my = Gy.shape[1]
    mz = Gz.shape[1]

    Ux, Sx, Vx = scipy.linalg.svd(Gx, full_matrices=False)
    Uy, Sy, Vy = scipy.linalg.svd(Gy, full_matrices=False)
    Uz, Sz, Vz = scipy.linalg.svd(Gz, full_matrices=False)
    Ux = np.asmatrix(Ux)
    Uy = np.asmatrix(Uy)
    Uz = np.asmatrix(Uz)

    Sxsq = np.power(Sx, 2)
    Sysq = np.power(Sy, 2)
    Szsq = np.power(Sz, 2)
    Szsqe = Szsq + epsilon
    Szsqt = Szsq / Szsqe

    # first term  - GxGx'GyGy'
    first = np.sum(np.multiply((Ux * (np.diag(Sxsq) * (Ux.T * Uy) * np.diag(Sysq))), Uy))

    # second term - 2GyGy'GzGz'(GzGz' - epsilonI)^(-2)GzGz'GxGx'
    second1 = Ux * (np.diag(Sxsq) * (Ux.T * Uz) * np.diag(Szsqt) * (Uz.T * Uy) * np.diag(Sysq))
    second = -2 * np.sum(np.multiply(second1, Uy))

    # third term  - 2GyGy'GzGz'(GzGz' - epsilonI)^(-2)GzGz'GxGx'GzGz'(GzGz' - epsilonI)^(-2)GzGz'
    third = np.sum(np.multiply((second1 * (Uy.T * Uz) * np.diag(Szsqt)), Uz))

    # compute test statistic using first, second, and third terms above with
    # the U-statistic
    emphsic = (first + second + third) / ((n - 1) ** 2)
    return emphsic

def pickK(X):
    # picks number of clusters for k-means clustering
    a = 1
    n = X.shape[0]
    b = n
    step = 2

    v = np.sum(np.var(X, axis=0))

    while (step > 1 and b <= n):
        step = max(round((b - a + 1) / 10), 1)
        for k in range(a, b, step):
            clf = KMeans(n_clusters=k, max_iter=1000)
            clf.fit(X)
            c = clf.cluster_centers_  # 两组数据点的中心点
            idx = clf.labels_  # 每个数据点所属分组
            sumd = 0
            for cluster_id in range(k):
                sumd += np.sum(np.power(X[np.where(idx == cluster_id)] - c[cluster_id], 2))
            c = sumd / n

            if (k != a):
                if ((lastc - c) / v < .05):
                    k = k - step
                    break

            lastc = c

        a = k
        b = k + step
    return k

if __name__ == '__main__':
    data_dict = scipy.io.loadmat('data.mat')
    aa, pval, stat = hsiccondTestIC(data_dict['X'], data_dict['Z'], data_dict['Y'], 0.8, 500)
    print(1)