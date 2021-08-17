"""Low-level functions to calculate the principal components."""
import warnings

import numpy as np


def norm(x, keepdims=True):
    """Calculate norm of vectors in array."""
    return np.linalg.norm(x, ord=2, axis=-1, keepdims=keepdims)


def normalize(x):
    """Normalize vectors in array to length 1."""
    return x / norm(x, True)


def frechet_similarity_distance(x, points):
    """Calculate the frechet similarity distance between x and points."""
    x = normalize(x)
    points = normalize(points)
    return np.sum(np.inner(x, points) ** 2, axis=-1)


def pspca(points):
    """Run PSPCA on points."""
    points = normalize(points)
    matrix_a = np.matmul(points.T, points)
    w, v = np.linalg.eigh(matrix_a)

    inds = np.argsort(w)[::-1]
    w = w[inds]
    v = v[:, inds]

    if np.all(v[:, 0] < 0):
        v[:, 0] *= -1
    if not np.all(v[:, 0] > 0):
        warnings.warn("The first component is not strictly positive!")

    test = test_surroundings(v[:, 0], points)
    if not test[0] and test[1]:
        warnings.warn("The first component is not a maximum!")  # pragma: no cover
    test = test_surroundings(v[:, -1], points)
    if test[0] and not test[1]:
        warnings.warn("The last component is not a minimum!")  # pragma: no cover

    for i in range(1, v.shape[0] - 1):
        test = test_surroundings(v[:, -1], points)
        if not test[0] and not test[1]:
            warnings.warn(f"Component {i} is not a saddle point!")

    for i in range(v.shape[0]):
        v_ = v[:, i]
        mi = v_.min()
        ma = v_.max()
        if np.abs(mi) > ma:
            v[:, i] *= -1

    return w, v, matrix_a


def transform(points, v):
    """Transform points according to their PSPCA eigenvectors v."""
    inv_v = np.linalg.inv(v)
    return np.matmul(inv_v, points[:, :, np.newaxis]).squeeze()


def reduce_dimensions(points, v, num):
    """Reduce dimension of points to num dimensions based on eigenvectors v."""
    return normalize(transform(points, v)[:, :num])


def mean(points):
    """Calculate the Frechet mean of points."""
    _, v, _ = pspca(points)
    return v[:, 0]


def other_points(v, num=10000):
    """Create several nearby points around given points v."""
    return normalize(v + np.random.rand(num, v.shape[0]) / 1000)


def test_surroundings(v, points):
    """Test wether eigenvectors v are maximum, minimum or saddle points."""
    o_points = other_points(v)
    diff_loss = frechet_similarity_distance(v, points) - frechet_similarity_distance(
        o_points, points
    )
    return (np.all(diff_loss >= 0), np.all(diff_loss <= 0))
