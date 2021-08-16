"""
Geometric calculations on top of vg (https://github.com/lace/vg) and numpy
(https://numpy.org)
"""

import numpy as np
import vg


def fit_plane(points, auto_orient=True):
    """
    Returns the normal of a cloud of points and the max distance to this plane.
    SVD method from:
    http://stackoverflow.com/questions/15959411/best-fit-plane-algorithms-why-different-results-solved

    :param points: stack of coordinates
    :type points: numpy array
    :param auto_orient: flip normal vector to get positive value along X, Y and/or Z
    :type auto_orient: bool

    :returns: a tuple (normal <numpy array>, max distance <float>)

    >>> pnts = np.array([[0,0,0], [1,0,0], [0,1,0], [1,1,0.2]])
    >>> normal, max_dist = fit_plane(pnts)
    >>> print ( normal.round(2) )
    [ 0.1   0.1  -0.99]
    >>> print ( round(max_dist,2) )
    0.05
    >>>
    >>> normal, max_dist = fit_plane(pnts, auto_orient=False)
    >>> print ( normal.round(2) )
    [-0.1  -0.1   0.99]
    """
    rows = points.shape[0]
    # Set up constraint equations of the form  AB = 0,
    # where B is a column vector of the plane coefficients
    # in the form b(1)*X + b(2)*Y +b(3)*Z + b(4) = 0.
    p = np.ones((rows, 1))
    AB = np.hstack([points, p])
    [u, d, v] = np.linalg.svd(AB, 0)
    B = v[3, :]  # Solution is last column of v.
    nn = np.linalg.norm(B[0:3])
    B = B / nn
    normal = B[0:3]
    if auto_orient:
        for axis in (0, 1, 2):
            if normal[axis] < 0:
                normal = normal * -1
                break
            elif normal[axis] > 0:
                break
    # recenter the points cloud:
    centroid = np.mean(points, axis=0)
    points -= centroid
    distances = np.abs(points.dot(normal))
    # plot(normal, centroid, points)
    return normal, max(distances)


def loc_array(x, y):
    """
    return indices of y (data) in x (reference). In other words,
    the function returns an array "how to find y's data in x"

    :param x: where to find the values' index
    :type x: numpy array
    :param y: data to find index in ``x``
    :type y: numpy array

    :returns: numpy array with the length of ``y`` filled with index of ``y`` in ``x``

    >>> x = np.array([2, 1, 5, 3, 100, 6])  # ref
    >>> y = np.array([3, 5, 5, 1, 3, 5, 6, 6, 6, 100])  # data
    >>> loc_array(x, y)
    array([3, 2, 2, 1, 3, 2, 5, 5, 5, 4])
    """
    index = np.argsort(x)
    sorted_x = x[index]
    sorted_index = np.searchsorted(sorted_x, y)

    yindex = np.take(index, sorted_index, mode="raise")
    mask = x[yindex] != y

    result = np.ma.array(yindex, mask=mask)
    return result.data


def angle(v1, v2, look=None, assume_normalized=False, units="deg", range_0_pi=False):
    """
    Small mod if initial `vg.angle`

    Compute the unsigned angle between two vectors. For stacked inputs, the
    angle is computed pairwise.

    When `look` is provided, the angle is computed in that viewing plane
    (`look` is the normal). Otherwise the angle is computed in 3-space.

    :param v1: A `3x1` vector or a `kx3` stack of vectors.
    :type v1: np.arraylike
    :param v2: A vector or stack of vectors with the same shape as `v1`.
    :type v2: np.arraylike
    :param look: A `3x1` vector specifying the normal of a viewing
                  plane, or `None` to compute the angle in 3-space.
    :type look: np.arraylike
    :param assume_normalized: When `True`, assume the input vectors
               are unit length. This improves performance, however when the inputs
               are not normalized, setting this will cause an incorrect results.
    :type assume_normalized: bool
    :param units: `'deg'` to return degrees or `'rad'` to return radians.
    :type units: str

    :returns: For `3x1` inputs, a `float` with the angle. For `kx1` inputs,
            a `kx1` array.
    """
    if units not in ["deg", "rad"]:
        raise ValueError("Unrecognized units {}; expected deg or rad".format(units))

    if look is not None:
        # This is a simple approach. Since this is working in two dimensions,
        # a smarter approach could reduce the amount of computation needed.
        v1, v2 = [vg.reject(v, from_v=look) for v in (v1, v2)]

    dot_products = np.einsum("ij,ij->i", v1.reshape(-1, 3), v2.reshape(-1, 3))
    if range_0_pi:
        dot_products = np.abs(dot_products)

    if assume_normalized:
        cosines = dot_products
    else:
        cosines = dot_products / vg.magnitude(v1) / vg.magnitude(v2)

    # Clip, because the dot product can slip past 1 or -1 due to rounding and
    # we can't compute arccos(-1.00001).
    angles = np.arccos(np.clip(cosines, -1.0, 1.0))
    if units == "deg":
        angles = np.degrees(angles)

    return angles[0] if v1.ndim == 1 and v2.ndim == 1 else angles


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS)
