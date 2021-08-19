#!/usr/bin/env python
#
# hierarchy.py - Functions and data structures for working with hierarchical
#                variables.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains functions and data structures for working with
hierarchical variables.


The :func:`loadHierarchyFile` function will read hierarchy information for
one variable from a text file, and return a :class:`Hierarchy` object.


The :class:`Hierarchy` class allows the hierarchy information about a variable
to be queried.


The hierarchy information for all hierarchical variables in the UKBiobank is
stored in ``funpack/data/hierarchy/`` - these files are available from the
UKBiobank showcase at https://biobank.ctsu.ox.ac.uk/crystal/schema.cgi.
"""


import os.path   as op
import functools as ft

import pandas    as pd
import numpy     as np


HIERARCHY_DATA_NAMES = {
    'icd10' : 19,
    'icd9'  : 87,
    'opcs4' : 240,
    'opcs3' : 259,
}
"""This dictionary contains some UK Biobank hierarchical data codings which
can be looked up by name with the :func:`getHierarchyFilePath` function.
"""


class CircularError(Exception):
    """Error raised by the :meth:`Hierarchy.parents` method in the event
    that a circular relationship is detected in a hierarchy.
    """
    pass


def getHierarchyFilePath(dtable=None,
                         vid=None,
                         name=None,
                         coding=None):
    """Return a path to the file containing hierarchy information for the
    specified variable/name. Pass the path to the :func:`loadHierarchyFile`
    function to load it.

    Hierarchy files can be looked up with one of the following methods, in
    order of precedence:

     1. By specifying a data coding (``coding``). This takes precedence.
     2. By specifying a ``name`` which is present in the
        :attr:`HIERARCHY_DATA_NAMES`.
     3. By passing a :class:`.DataTable` (``dtable``) and variable ID (``vid``)

    Te recognised data type names for use with the second method are listed in
    the :attr:`HIERARCHY_DATA_NAMES` dictionary.

    A :exc:`ValueError` is raised if the variable is unknown, or does not
    have a listed data coding.

    The returned path is not guaranteed to exist.

    :arg dtable: The :class:`.DataTable`
    :arg vid:    Variable ID
    :arg name:   Data coding name
    :arg coding: Data coding ID
    :returns:    A path to the relevant hierarchical coding file.
    """

    if coding is None:
        if name is not None:
            coding = HIERARCHY_DATA_NAMES[name.lower()]
        elif (dtable is not None) and (vid is not None):
            try:
                coding = int(dtable.vartable.loc[vid, 'DataCoding'])
            except Exception:
                raise ValueError('Variable {} is unknown or does not '
                                 'have a data coding'.format(vid))
    if coding is None:
        raise ValueError('A coding, name, or dtable+vid must be specified')

    hierdir = op.join(op.dirname(__file__), 'data', 'hierarchy')
    return op.join(hierdir, 'coding{}.tsv'.format(int(coding)))


@ft.lru_cache()
def loadHierarchyFile(fname):
    """Reads the hierarchy information for a variable from the given file.

    ``fname`` is assumed to refer to a tab-separated file containing
    the following columns:

      - ``coding``:    A variable value
      - ``meaning``:   Description
      - ``node_id``:   Index in the hierarchy
      - ``parent_id``: Index of this node's parent

    It is assumed that all codings have a sequential ``node_id`` starting from
    1, and that the parent node(s) have a ``parent_id`` of 0.
    The codes are not assumed to be ordered by their ID.

    :arg fname: File containing hierarchy information for one variable
    :returns:   A :class:`Hierarchy` object.
    """

    data      = pd.read_csv(fname, delimiter='\t', index_col=False)
    codings   = data['coding']   .values
    meanings  = data['meaning']  .values
    nodeIds   = data['node_id']  .values
    parentIds = data['parent_id'].values

    order = np.argsort(nodeIds)

    codings   = codings[  order]
    meanings  = meanings[ order]
    nodeIds   = nodeIds[  order] - 1
    parentIds = parentIds[order] - 1

    return Hierarchy(nodeIds, parentIds, codings, meanings)


def codeToNumeric(code,
                  name=None,
                  dtable=None,
                  vid=None,
                  coding=None,
                  hier=None):
    """Converts a hierarchical code into a numeric version. See the
    :func:`getHierarchyFilePath` for information on the arguments.

    :arg code:   Code to convert
    :arg name:   Data coding name
    :arg dtable: The :class:`.DataTable`
    :arg vid:    Variable ID
    :arg coding: Data coding ID
    :arg hier:   A :class:`Hierarchy` instance which, if provided, will
                 be used instead of loading one from file using the other
                 arguments.
    """
    # We use the node IDs defined in
    # the hierarchy file as the
    # numeric version of each coding.
    if hier is None:
        hier = getHierarchyFilePath(dtable, vid, name, coding)
        hier = loadHierarchyFile(hier)

    try:
        # hierarchy uses 0-indexing,
        # whereas the hierarchy files
        # use 1-indexing
        return int(hier.index(code) + 1)
    except KeyError:
        return np.nan


def numericToCode(code, name=None, dtable=None, vid=None, coding=None):
    """Converts a numeric hierarchical code into its original version

    :arg code:   Code to convert
    :arg name:   Data coding name
    :arg dtable: The :class:`.DataTable`
    :arg vid:    Variable ID
    :arg coding: Data coding ID
    """
    hier = getHierarchyFilePath(dtable, vid, name, coding)
    hier = loadHierarchyFile(hier)

    try:
        return hier.coding(int(code - 1))
    except KeyError:
        return 'NaN'


class Hierarchy(object):
    """The ``Hierarchy`` class allows information in a hierarchical variable to be
    queried. The :meth:`parents` method will return all parents in the
    hierarchy for a given value (a.k.a. *coding*), and the :meth:`description`
    method will return the description for a value.

    Additional metadata can be added and retrieved for codings via the
    :meth:`set` and :meth:`get` methods.
    """

    def __init__(self, nodes, parents, codings, descs):
        """Create a ``Hierarchy`` object.

        :arg nodes:   Node IDs. Currently assumed to be equivalent to
                      ``np.arange(len(nodes))``
        :arg parents: Parent IDs for each node.
        :arg codings: Value/coding for each node.
        :arg descs:   Description for each node
        """

        self.__nodes    = nodes
        self.__parents  = parents
        self.__codings  = codings
        self.__attrs    = {}
        self.__codeidxs = {}

        self.__attrs['description'] = descs

        for i, c in enumerate(self.__codings):
            self.__codeidxs[c] = i


    @property
    def codings(self):
        """Return a list of all codings in the hierarchy. """
        return list(self.__codings)


    def index(self, coding):
        """Return the node ID for the given ``coding``. """
        return self.__codeidxs[coding]


    def coding(self, nodeID):
        """Return the coding for the given ``nodeID``. """
        return self.__codings[nodeID]


    def parents(self, coding):
        """Return all parents of the given coding. """

        parents = []
        cidx    = self.index(coding)
        pidx    = self.__parents[cidx]
        seen    = set()

        while pidx >= 0:
            if pidx in seen:
                raise CircularError(pidx + 1, str(self.coding(pidx)))
            seen.add(pidx)
            parents.append(self.coding(pidx))
            pidx = self.__parents[pidx]

        return parents


    def description(self, coding):
        """Return the description for the given coding. """
        return self.get(coding, 'description')


    def get(self, coding, attr):
        """Get the given attribue for the given coding. """
        idx = self.index(coding)
        return self.__attrs[attr][idx]


    def set(self, coding, attr, value):
        """Set an attribute for the given coding. """

        if attr not in self.__attrs:
            self.__attrs[attr] = [None] * len(self.__nodes)

        idx = self.index(coding)
        self.__attrs[attr][idx] = value
