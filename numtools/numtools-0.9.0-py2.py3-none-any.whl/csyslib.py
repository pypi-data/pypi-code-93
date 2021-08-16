"""

.. testsetup:: *

   from numtools.csyslib import *

.. autoclass::numtools.csyslib.RCSys
   :members:

.. autoclass::numtools.csyslib.Register
   :members:

"""
from collections import UserDict
import numpy as np
from numpy import dot
from numpy.linalg import inv
import pprint as pp
import vg
import logging

try:
    from pyquaternion import Quaternion

    ISQUATERNION = True
except:
    ISQUATERNION = False

# ============================================================================
# ⚠ NOTE ⚠
# ----------------------------------------------------------------------------
# Some usefull functions are missing in vg module as downloaded from pypi
# ----------------------------------------------------------------------------
# nic@alcazar -- mardi 19 novembre 2019, 08:25:12 (UTC+0100)
# ========================================================================
def check_value(a, shape, **kwargs):
    """
    copied from `vg` master branch
    """

    def is_wildcard(dim):
        return dim == -1

    if any(not isinstance(dim, int) and not is_wildcard(dim) for dim in shape):
        raise ValueError("Expected shape dimensions to be int")

    if "name" in kwargs:
        preamble = "{} must be an array".format(kwargs["name"])
    else:
        preamble = "Expected an array"

    if a is None:
        raise ValueError("{} with shape {}; got None".format(preamble, shape))
    try:
        len(a.shape)
    except (AttributeError, TypeError):
        raise ValueError(
            "{} with shape {}; got {}".format(preamble, shape, a.__class__.__name__)
        )

    # Check non-wildcard dimensions.
    if len(a.shape) != len(shape) or any(
        actual != expected
        for actual, expected in zip(a.shape, shape)
        if not is_wildcard(expected)
    ):
        raise ValueError("{} with shape {}; got {}".format(preamble, shape, a.shape))

    wildcard_dims = [
        actual for actual, expected in zip(a.shape, shape) if is_wildcard(expected)
    ]
    if len(wildcard_dims) == 0:
        return None
    elif len(wildcard_dims) == 1:
        return wildcard_dims[0]
    else:
        return tuple(wildcard_dims)


def check(locals_namespace, name, shape):
    """
    copied from `vg` master branch
    """
    return check_value(locals_namespace[name], shape, name=name)


def convert_33_to_44(matrix):
    """
    Transform from:
        array([[1., 2., 3.],
               [2., 3., 4.],
               [5., 6., 7.]])
    to:
        array([[1., 2., 3., 0.],
               [2., 3., 4., 0.],
               [5., 6., 7., 0.],
               [0., 0., 0., 1.]])
    """
    check(locals(), "matrix", (3, 3))
    result = np.zeros((4, 4), dtype=matrix.dtype)
    result[:3, :3] = matrix
    result[3, 3] = 1
    return result


def find_third(vectors, keep=None, check=True):
    """
    return a tuple of three vectors (tuples)

    if one of the three vectors is null, calculate it as per cross product
    (right-hand rule). If all the vectors are provided and vectors are not
    orthogonal, raises a ``ValueError`` exception otherwise, returns vectors
    provided vectors.

    >>> find_third( ((1,0,0),(),(0,0,1)) )
    [array([1., 0., 0.]), array([0., 1., 0.]), array([0., 0., 1.])]
    >>> find_third( ((1,0,0),(),(0,0,1)), keep=0)
    [array([1., 0., 0.]), array([0., 1., 0.]), array([0., 0., 1.])]

    """
    vectors = [np.array(v, dtype=np.float64) for v in vectors]
    # find null vector's index in the list
    na = [ix for ix, v in enumerate(vectors) if v.size == 0]
    if na:
        na = na[0]
    else:
        check_trihedron(vectors)
        na = 0  # pick a random vector

    axis = (0, 1, 2, 0, 1, 2)
    vectors[na] = np.cross(vectors[axis[na + 1]], vectors[axis[na + 2]])
    if keep:
        recalc_vec = set(range(3)) ^ set((na, keep))
        recalc_vec = recalc_vec.pop()
        # recalculate false vector
        vectors[recalc_vec] = np.cross(
            vectors[axis[recalc_vec + 1]], vectors[axis[recalc_vec + 2]]
        )
    if check:
        check_trihedron(vectors)

    return vectors


def check_trihedron(vectors, auto_correct=False):
    v1 = vg.normalize(np.cross(vectors[0], vectors[1]))
    v2 = vg.normalize(vectors[2])
    try:
        np.testing.assert_array_almost_equal(v1, v2)
    except AssertionError:
        # --------------------------------------------------------------------
        # autocorrect
        if auto_correct:
            vectors[2] = v1
        else:
            raise ValueError("provided vectors are not orthogonal!")
    return vectors


# ============================================================================
# Register
# ============================================================================


class Register(UserDict):
    """
    Dict-like class for storing and managing a collection of Coordinate Systems.

    >>> reg = Register(minid=1)
    >>> reg.nextid()
    1
    >>> csys1 = reg.new(points=((1, -1, 0), (1, -1, 3), (5, -1, -2)))
    >>> csys2 = reg.new(points=((1, -1, 0), (1, -1, 3), (5, -1, -2)), reference_id=1)
    >>> reg.deps(csys2.id)
    [1]

    >>> import pickle
    >>> reg.minid
    1
    >>> pickle.loads(pickle.dumps(reg))
    {1: RCSys #1 x:[1.0, 0.0, -0.0] ...

    """

    def __init__(self, minid=1, *args, **kwargs):
        self.minid = minid
        UserDict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        if not isinstance(key, int) or key < self.minid:
            raise ValueError("CSys ID key shall be an integer >= %d" % self.minid)
        if key in self:
            raise ValueError("CSys ID%d already stored" % key)
        if not isinstance(value, RCSys):
            raise ValueError("Can only register Coordinates systems")
        UserDict.__setitem__(self, key, value)

    def nextid(self):
        return max(self.data.keys(), default=self.minid - 1) + 1

    def new(self, id=None, reference_id=None, *args, **kwargs):
        """create and store a coordinate CSys"""
        if "reference" in kwargs:
            reference = kwargs.pop("reference")
        else:
            reference = None
        if not id:
            id = self.nextid()
        if reference_id:
            reference = self[reference_id]
        csys = RCSys(id=id, reference=reference, *args, **kwargs)
        csys.reg = self
        self[id] = csys
        return self[id]

    def deps(self, csys_id):
        """return the list of dependancies"""
        deps = []
        csys = self[csys_id]
        csys_id = csys.reference_id
        while csys_id != 0:
            deps.append(csys_id)
            csys = self[csys_id]
            csys_id = csys.reference_id
        return deps


##############################################################################
# Class RCSys
##############################################################################
class _DummyRef:
    _matrix = np.eye(4)
    reference = None
    reference_id = None
    id = 0
    title = "Global Rectangular"

    def __str__(self):
        return "Absolute Ref."


class RCSys(object):
    r"""
    Rectangular Coordinate System object handling both rotations and translations.

    Two ways to construct a new instance are provided:

        * giving `axis` and `origin`
        * giving three points (A, B, C) in the NASTRAN's philosphy:
            A: origin
            B: point **on** Z axis (so AB is the Z axis)
            C: point **on** Axz plane (so C basically indicates x axis)

    Three Points definition::

                                 [Z]
                                  ┃
                                  ⊕ B
                                  ┃
                                 ╱┃
                                ╱ ┃ A
                             C ⊕  ⊕ ━━━━━━━━━━━ [Y]
                               | ╱
                               |╱
                               ╱
                             [X]


    Note:

    To use this 3-points way from FEMAP, one need to use "ZX Locate" option.


    :param axis: X, Y, Z axis definition given in `reference` system.
    :type axis: sequence of three-numbers-sequences.
    :param origin: origin location given in `reference` system.
    :type origin: sequence of three numbers.
    :param points: NASTRAN-like 3 points definition
    :type points: sequence of 3-nb sequences.
    :param keep: index of the axis to keep exact.
    :type keep: int or None.
    :param reference: RCSys object taken as reference. If `None` is provided,
        takes absolute reference
    :type reference: RCSys object or None
    :param labels: names of the three axis. Default is ('x','y','z').
    :type labels: sequence of three strings.

    In case both options are given, the method of "points" superseeds the
    one with `axis` and `origin`.

    `RCSys` instances can be created using two ways: the "three-points" one and the
    "origin and axis" one.

    basic example using NASTRAN's three points philosophy:

    >>> # create a coordinate system using NASTRAN's 3-points philosophy
    >>> csys2 = RCSys(points=((1, -1, 0), (1, -1, 3), (5, -1, -2)))
    >>> pnt2 = (1,0,1) # vertex in csys2
    >>> csys2.export_vertices(pnt2) # pnt2 in ref axis
    array([ 2., -1.,  1.])

    basic example using origin and axes (providing two axis is enough):

    >>> csys3 = RCSys(origin=(1, -1, 0),
    ...               axis= [[1, 0, 0],
    ...                      [0, 1, 0],
    ...                      []])
    >>> pnt2 = (1,0,1) # vertex in csys2
    >>> csys3.export_vertices(pnt2) # pnt2 in ref axis
    array([ 2., -1.,  1.])

    Some properties such as origin and axis are available:

    >>> csys2.axis
    array([[ 1.,  0., -0.],
           [-0.,  1.,  0.],
           [ 0.,  0.,  1.]])
    >>> csys2.origin
    array([ 1., -1.,  0.])


    """

    def __init__(
        self,
        axis=((1, 0, 0), (0, 1, 0), ()),
        origin=(0, 0, 0),
        points=None,
        keep=None,
        reference=None,
        labels=("xyz"),
        title="Rectangular Coordinates System",
        id=None,
    ):

        if not reference:
            # by default, refers to Ground
            reference = _DummyRef()
        self.reference = reference
        self.reference_id = reference.id
        self.title = title
        self.reg = None  # overriden in case of use of registry

        if points:
            # NASTRAN-like CSYS definition
            # first provided point (A) is the origin
            # second provided point (B) **is located on Z axis**
            # third provided point (C) **is located on the XZ plane**
            A, B, C = (
                np.array(points[0], dtype=np.float64),
                np.array(points[1], dtype=np.float64),
                np.array(points[2], dtype=np.float64),
            )
            self.origin = A
            axis = find_third(((C - A), (), (B - A)), keep=2)
        else:
            self.origin = np.array(origin)
            # if one of the axis is not provided, calculate it
            axis = find_third(axis, keep=keep)
            axis = [np.array(v) for v in axis]
        self.axis = np.array([v / np.linalg.norm(v) for v in axis])
        self.labels = labels
        self._build_matrices()
        # also store an `id` in case RCSys instances are handled by a
        # register
        self.id = id

    def __repr__(self):
        """
        >>> csys = RCSys(labels=('T','L','S'))
        >>> print(csys)
        RCSys T:[1.0, 0.0, 0.0] L:[0.0, 1.0, 0.0] S:[0.0, 0.0, 1.0]
        """
        raxis = tuple(list(map(lambda x: round(x, 2), a)) for a in self.axis)
        naxis = self.labels
        axis = "RCSys"
        if self.id is not None:
            axis += " #%d" % self.id
        axis += " %s:%s %s:%s %s:%s" % (
            naxis[0],
            raxis[0],
            naxis[1],
            raxis[1],
            naxis[2],
            raxis[2],
        )
        return axis

    def info(self):
        """ return a string defining the RCsyss"""
        if self.id:
            msg = "Coordinate System {csys.id} - {csys.title}"
        else:
            msg = "Coordinate System - {csys.title}"
        if self.reference.id:
            msg += "\nDef CSys: {csys.reference.id}"
        else:
            msg += "\nDef CSys: {csys.reference}"
        msg += "\nOrigin: {csys.origin}"
        msg += "\nAxis (Direction Cosines):\n{csys.axis}"
        return msg.format(csys=self)

    def get_axis(self):
        """return a dictionnay of np arrays showing axis

        :returns:  dictionnary -- given axis.

        >>> RCSys(labels=('T','L','S')).get_axis()
        {'T': array([1., 0., 0.]), 'L': array([0., 1., 0.]), 'S': array([0., 0., 1.])}
        """
        return dict(zip(self.labels, self.axis))

    def _build_matrices(self):
        """
        build:

            * _matrix is the rotation matrix FROM reference TO self
            * _M is the transformation matrix FROM self TO ground
            * _MI is the transformation matrix FROM ground TO self

        """
        # ==============================================================================
        #         build the matrix from ref to self
        # ==============================================================================
        M = np.array(self.axis, dtype=np.float64).transpose()  # rotation
        v = np.array(self.origin).reshape((3, 1))  # translation
        M = np.hstack((M, v))
        M = np.vstack((M, [0, 0, 0, 1]))
        self._matrix = M
        # ==============================================================================
        # build the _M absolute matrix to ground
        # http://en.wikipedia.org/wiki/Transformation_matrix#Composing_and_inverting_transformations
        # ==============================================================================
        # recursively parsing all the CSYS chain
        botcsys = self.reference
        matrices = [self._matrix]
        while botcsys:
            matrices.append(botcsys._matrix)
            botcsys = botcsys.reference
        matrices.reverse()
        M = matrices.pop(0)
        for m in matrices:
            M = dot(M, m)
        self._M = M
        self._MI = inv(M)

    def get_rot_matrix(self):
        """ return rotational part of self._M """
        return self._M[:-1, :-1]

    def get_inv_rot_matrix(self):
        """ return rotational part of self._MI """
        return self._MI[:-1, :-1]

    def export_vertices(self, vertices, to_csys=None, rot_only=False):
        """
        Convert a 3D vertices stack (or single vertex)
        from current RCSys to ground (reference CSYS).

        :param vertices: vertex or stack of vertices
        :type vertices: any iterable, including ``numpy.ndarray``
        :param to_csys: Coordinate system (``RCSys`` obj.) or ``None`` for ground
            (default is ``None``). Can also be a CSys ID if a registry has been bound

        >>> csys = RCSys(axis=((0 , 1, 0),(),(0,0,1)), keep=0,
        ...                origin=(-1, -1, 0) )
        >>> csys.export_vertices((2, -2, 1) )
        array([1., 1., 1.])

        If ``vertices`` are vectors, only the rotational part of the transformation
        is to be applied. In this case, set ``rot_only`` to ``True``

        >>> csys = RCSys(axis=((0 , 1, 0),(),(0,0,1)), keep=0,
        ...                origin=(-1, -1, 0) )
        >>> csys.export_vertices((2, -2, 1), rot_only=True )
        array([2., 2., 1.])

        To export vertice(s) to another RCSys, provide `to_csys` argument:

        """
        matrix = self._M[:]
        if rot_only:
            # apply only rotational transformation
            matrix = convert_33_to_44(matrix[:3, :3])
        grounded = vg.matrix.transform(np.array(vertices), matrix)
        if not to_csys:
            return grounded
        if isinstance(to_csys, int):
            to_csys = self.reg[to_csys]
        return to_csys.import_vertices(grounded, rot_only=rot_only)

    def import_vertices(self, vertices, from_csys=None, rot_only=False):
        """
        Convert a vertex or a stack (nx3) of vertices to current CSYS

        :param vertices: (nx3) iterable of vertex (n=1) or vertices (n>=1) to export
        :type vertices: any iterable, including ``numpy.ndarray``
        :param from_csys: Coordinate system (``RCSys`` obj.) or ``None`` for ground
            (default is ``None``)
        :type rot_only: bool
        :param rot_only: Apply only rotational transformation and skip translational
            transformation. default is ``False``. Set it to ``True`` to export vectors.

        >>> csys1 = RCSys( axis=((0 ,1, 0),(),(0,0,1)),
        ...                origin=(-1, -1, 0) )
        >>> csys1.import_vertices((1, 1, 1))
        array([ 2., -2.,  1.])

        A stack of vertices can also be passed:

        >>> vertices = [[0, 0, 0],
        ...            [1, 1, 1]]
        >>> csys1.import_vertices(vertices)
        array([[ 1., -1.,  0.],
               [ 2., -2.,  1.]])

        If we assume ``vertices`` to be *vectors*, only the rotational
        transformation should be applied. Passing ``rot_only=True``:

        >>> csys1.import_vertices(vertices, rot_only=True)
        array([[ 0.,  0.,  0.],
               [ 1., -1.,  1.]])

        """
        matrix = self._MI
        if rot_only:
            # apply only rotational transformation
            matrix = convert_33_to_44(matrix[:3, :3])
        if not from_csys:
            # import vertices from ground
            return vg.matrix.transform(np.array(vertices), matrix)
        if isinstance(from_csys, int):
            from_csys = self.reg[from_csys]
        grounded = from_csys.export_vertices(vertices)
        return vg.matrix.transform(np.array(grounded), self._MI)

    def quaternion(self):
        if not ISQUATERNION:
            raise ValueError("Need `pyquaternion` to be installed")
        return Quaternion(matrix=self._M)


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
