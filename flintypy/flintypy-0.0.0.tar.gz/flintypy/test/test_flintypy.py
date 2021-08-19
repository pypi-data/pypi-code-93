"""
Unit tests for flintypy.v_stat

@author: Alan Aw and Jeffrey Spence
"""
from flintypy.v_stat import _hamming_distances
from flintypy.v_stat import _calculate_bin_v_stat
from flintypy.v_stat import _calculate_real_v_stat
from flintypy.v_stat import _numba_permute
from flintypy.v_stat import _build_forward
from flintypy.v_stat import _build_reverse
from flintypy.v_stat import _numba_permute_dists
from flintypy.v_stat import _naive_block_permute
from flintypy.v_stat import _cache_block_permute
from flintypy.v_stat import _convolution_of_chi2
from flintypy.v_stat import _ind_cov
from flintypy.v_stat import _chi2_weights
from flintypy.v_stat import _ind_large_p
from flintypy.v_stat import _block_permute
from flintypy.v_stat import _block_cov
from flintypy.v_stat import _block_large_p
from flintypy.v_stat import _ind_large_p_large_n
from flintypy.v_stat import _block_large_p_large_n
import numpy as np
from scipy.stats import chi2
from scipy.spatial.distance import pdist


def test_hamming_distances():
    X = np.random.randint(2, size=(50, 100))
    h_dists = _hamming_distances(X)
    h_dist_mat = np.zeros((50, 50))
    h_dist_mat[np.triu_indices(50, 1)] = h_dists
    calc = []
    for n1 in range(49):
        for n2 in range(n1+1, 50):
            calc.append(((X[n1, :] - X[n2, :])**2).sum())
            assert np.isclose(h_dist_mat[n1, n2], calc[-1])
    assert np.allclose(h_dists, calc),  '_hamming_distances failed test'


def test_calculate_bin_v_stat():
    X = np.random.randint(2, size=(50, 100))
    v_stat = _calculate_bin_v_stat(X)
    calc = 0
    h_dists = _hamming_distances(X)
    for h in h_dists:
        calc += (h - np.mean(h_dists))**2
    calc /= h_dists.shape[0]
    calc /= X.shape[1]
    assert np.isclose(calc, v_stat), '_calculate_bin_v_stat failed test'


def test_calculate_real_v_stat():
    X = np.random.randn(50, 100)
    v_stat = _calculate_real_v_stat(X, p=2)
    calc = 0
    dists = pdist(X=X, metric='minkowski', p=2)**2
    for d in dists:
        calc += (d - np.mean(dists))**2
    calc /= dists.shape[0]
    calc /= X.shape[1]
    assert np.isclose(calc, v_stat), '_calculate_real_v_stat failed test'


def test_numba_permute():
    X = np.random.randint(2, size=(50, 100))
    blocks = np.zeros(100, dtype=np.int64)
    X_perm = _numba_permute(X, blocks)
    assert np.allclose(X.sum(axis=0), X_perm.sum(axis=0))
    for i in range(50):
        check = False
        for j in range(50):
            if np.all(X[i] == X_perm[j]):
                check = True
                break
        assert check
    X = np.zeros((50, 100), dtype=np.int64)
    X[0:25, :] = 1
    blocks = np.arange(100, dtype=np.int64)
    X_perm = _numba_permute(X, blocks)
    r2s = []
    for i in range(99):
        for j in range(i+1, 100):
            r2s.append(np.corrcoef(X_perm[:, i], X_perm[:, j])[0, 1]**2)
    assert np.isclose(np.mean(r2s), 0.02, atol=0.02)
    blocks[0:50] = 0
    blocks[50:] = 1
    X_perm = _numba_permute(X, blocks)
    assert np.isclose(np.corrcoef(X_perm[:, 0], X_perm[:, 1])[0, 1], 1)


def test_numba_permute_dists():
    X = np.random.randint(2, size=(10, 100))
    blocks = np.arange(100, dtype=np.int64)
    forward = _build_forward(10)
    reverse = _build_reverse(10)
    calcs = []
    fancy = []
    h_dists = np.array([_hamming_distances(X[:, i, None]) for i in range(100)])
    for i in range(1000):
        calcs.append(np.var(_hamming_distances(_numba_permute(X, blocks))))
        fancy.append(np.var(_numba_permute_dists(h_dists,
                                                 forward,
                                                 reverse).sum(axis=0)))
    assert np.isclose(np.mean(calcs), np.mean(fancy), rtol=1e-1)
    assert np.isclose(np.var(calcs), np.var(fancy), rtol=5e-1)


def test_cache_block_permute():
    X = np.random.randint(2, size=(50, 1000))
    blocks = [np.arange(250), np.arange(250, 500), np.arange(500, 750),
              np.arange(750, 1000)]
    numba_blocks = np.zeros(1000, dtype=np.int64)
    numba_blocks[250:500] = 1
    numba_blocks[500:750] = 2
    numba_blocks[750:] = 3
    naive = [_naive_block_permute(X, numba_blocks, p=2) for i in range(1000)]
    cache = _cache_block_permute(X, blocks, 1000, p=2)
    assert np.isclose(np.mean(naive), np.mean(cache), rtol=1e-1)
    assert np.isclose(np.var(naive), np.var(cache), rtol=5e-1)


def test_convolution_of_chi2():
    for i in range(10):
        w1 = np.random.random()
        w2 = np.random.random()
        d1 = np.random.randint(1, 1000)
        d2 = np.random.randint(1, 1000)
        val = w1*chi2.rvs(df=d1, size=1) + w2*chi2.rvs(df=d2, size=1)
        val = float(val)
        sims = w1*chi2.rvs(df=d1, size=10000) + w2*chi2.rvs(df=d2, size=10000)
        p_val = np.mean(sims > val)
        error = 3 * np.sqrt(p_val * (1-p_val) / 10000)
        error = np.max([error, 3/10000])
        theory = _convolution_of_chi2(val, w1, w2, d1, d2)
        assert np.abs(theory - p_val) < error


def test_ind_cov():
    for k in range(1, 50):
        X = np.zeros((50, 10))
        X[0:k] = 1
        true_alpha = 2 * k * (50-k) / 50 / 49 * (1 - 2 * k * (50-k) / 50 / 49)
        true_beta = k * (50-k) / 50 / 49 * (1 - 4 * k * (50-k) / 50 / 49)
        true_gamma = 2 * k * (50-k) / 50 / 49 * (2*(k-1)*(50-k-1)/48/47
                                                 - 2*k*(50-k)/50/49)
        alpha, beta, gamma = _ind_cov(X, p=2)
        assert np.isclose(alpha, true_alpha)
        assert np.isclose(beta, true_beta)
        assert np.isclose(gamma, true_gamma)


def test_block_cov():
    for k in range(1, 50):
        X = np.zeros((50, 10))
        X[0:k] = 1
        blocks = [np.array([i]) for i in range(10)]
        true_alpha, true_beta, true_gamma = _ind_cov(X, p=2)
        alpha, beta, gamma = _block_cov(X, blocks, p=2)
        assert np.isclose(alpha, true_alpha)
        assert np.isclose(beta, true_beta)
        assert np.isclose(gamma, true_gamma)
        blocks = [np.arange(10)]
        alpha, beta, gamma = _block_cov(X, blocks, p=2)
        assert np.isclose(alpha, true_alpha*10)
        assert np.isclose(beta, true_beta*10)
        assert np.isclose(gamma, true_gamma*10)


def test_chi2_weights():
    for k in range(1, 50):
        X = np.zeros((50, 10))
        X[0:k] = 1
        w1, w2 = _chi2_weights(*_ind_cov(X, p=2), 50)
        if k == 25:
            assert np.isclose(w1, 0)
        assert w1 > -1e-16
        assert w2 > -1e-16


def test_ind_large_p():
    for i in range(10):
        X = np.random.randint(2, size=(5, 1000))
        blocks = [np.array([i]) for i in range(1000)]
        perm_p_val = _block_permute(X, blocks, 1000, p=2)
        error = 3 * np.sqrt(perm_p_val * (1-perm_p_val) / 1000)
        error = np.max([error, 3/1000])
        asy_p_val = _ind_large_p(X, p=2)
        assert np.abs(perm_p_val - asy_p_val) < error


def random_blocks(size, num_blocks):
    breaks = np.random.choice(size, size=num_blocks, replace=False)
    breaks = np.sort(breaks)
    if breaks[0] != 0:
        breaks = np.array([0] + breaks.tolist())
    if breaks[-1] != size:
        breaks = np.array(breaks.tolist() + [size])
    blocks = []
    for start, end in zip(breaks[:-1], breaks[1:]):
        blocks.append(np.arange(start, end))
    return blocks


def test_block_large_p():
    for i in range(10):
        X = np.random.randint(2, size=(10, 10000))
        blocks = random_blocks(10000, 1000)
        perm_p_val = _block_permute(X, blocks, 1000, p=2)
        error = 3 * np.sqrt(perm_p_val * (1-perm_p_val) / 1000)
        error = np.max([error, 3/1000])
        asy_p_val = _block_large_p(X, blocks, p=2)
        assert np.abs(perm_p_val - asy_p_val) < error


def test_ind_large_p_uniform():
    p_vals = []
    for i in range(3000):
        X = np.random.randint(2, size=(10, 10000))
        p_vals.append(_ind_large_p(X, p=2))
    assert np.isclose(np.mean(p_vals), 0.5, atol=0.01)
    assert np.isclose(np.var(p_vals), 1/12, atol=0.03)


def test_in_large_p_large_n_uniform():
    p_vals = []
    for i in range(3000):
        X = np.random.randint(2, size=(100, 10000))
        p_vals.append(_ind_large_p_large_n(X, p=2))
    assert np.isclose(np.mean(p_vals), 0.5, atol=0.1)
    assert np.isclose(np.var(p_vals), 1/12, atol=0.03)


def test_ind_large_p_large_n():
    for i in range(10):
        X = np.random.randint(2, size=(500, 10000))
        large_p_val = _ind_large_p(X, p=2)
        large_n_val = _ind_large_p_large_n(X, p=2)
        assert np.isclose(large_p_val, large_n_val, rtol=0.1)


def test_block_large_p_large_n():
    for i in range(10):
        X = np.random.randint(2, size=(500, 10000))
        blocks = random_blocks(10000, 1000)
        large_p_val = _block_large_p(X, blocks, p=2)
        large_n_val = _block_large_p_large_n(X, blocks, p=2)
        assert np.isclose(large_p_val, large_n_val, rtol=0.1)
