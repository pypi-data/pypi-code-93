#!/usr/bin/env python
#
# processing_functions.py - Processing functions
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains definitions of processing functions - functions which
may be specifeid in the processing table.


A processing function may perform any sort of processing on one or more
variables. A processing function may add, remove, or manipulate the columns of
the :class:`DataTable`.


All processing functions must accept the following as their first two
positional arguments:


 - The :class:`.DataTable` object, containing references to the data, variable,
   and processing table.
 - A list of integer ID of the variables to process.


Furthermore, all processing functions must return one of the following:

 - ``None``, indicating that no columns are to be added or removed.

 - A ``list`` (must be a ``list``) of :class:`.Column` objects describing the
   columns that should be removed from the data.

 - A ``tuple`` (must be a ``tuple``) of length 2, containing:

    - A list of ``pandas.Series`` that should be added to the data.

    - A list of variable IDs to use for each new ``Series``. This list must
      have the same length as the list of new ``Series``, but if they are not
      associated with any specific variable, ``None`` may be used.

 - A ``tuple`` of length 3, containing:

    - List of columns to be removed
    - List of ``Series`` to be added
    - List of variable IDs for each new ``Series``.

 - A ``tuple`` of length 4, containing the above, and:

    - List of dicts associated with each of the new ``Series``. These will be
      passed as keyword arguments to the :class:`.Column` objects that
      represent each of the new ``Series``.

The following processing functions are defined:

 .. autosummary::
   :nosignatures:

   removeIfSparse
   removeIfRedundant
   binariseCategorical
   expandCompound
"""


import functools       as ft
import itertools       as it
import                    logging
import                    collections

import numpy            as np
import pandas           as pd
import pandas.api.types as pdtypes

from typing import List, Optional, Any

from . import processing_functions_core as core
from . import                              util
from . import                              custom
from . import                              datatable
from . import                              loadtables


log = logging.getLogger(__name__)


@custom.processor()
def removeIfSparse(
        dtable     : datatable.DataTable,
        vids       : List[int],
        minpres    : Optional[float] = None,
        minstd     : Optional[float] = None,
        mincat     : Optional[float] = None,
        maxcat     : Optional[float] = None,
        abspres    : bool            = True,
        abscat     : bool            = True,
        naval      : Optional[Any]   = None,
        ignoreType : bool            = False
) -> List[datatable.Column]:
    """removeIfSparse([minpres], [minstd], [mincat], [maxcat], [abspres], [abscat], [naval])
    Removes columns deemed to be sparse.

    Removes columns for the variables in ``vids`` if they are sparse.

    :arg ignoreType: Defaults to ``False``. If ``True``, all specified tests are
                     run regardless of the types of the ``vids``. Only used for
                     testing.

    See the :func:`.isSparse` function for details on the other arguments.
    """  # noqa

    cols   = []
    series = []
    vtypes = []

    for vid in vids:

        if ignoreType: vtype = None
        else:          vtype = dtable.vartable.loc[vid, 'Type']

        vcols = dtable.columns(vid)

        cols  .extend(vcols)
        series.extend([dtable[:, c.name] for c in vcols])
        vtypes.extend([vtype] * len(vcols))

    log.debug('Checking %u columns for sparsity %s ...', len(series), vids[:5])

    func = ft.partial(core.isSparse,
                      minpres=minpres,
                      minstd=minstd,
                      mincat=mincat,
                      maxcat=maxcat,
                      abspres=abspres,
                      abscat=abscat,
                      naval=naval)

    with dtable.pool() as pool:
        results = pool.starmap(func, zip(series, vtypes))

    remove = []

    for col, (isSparse, reason, value) in zip(cols, results):
        if isSparse:
            log.debug('Dropping sparse column %s (%s: %f)',
                      col.name, reason, value)
            remove.append(col)

    if len(remove) > 0:
        log.debug('Dropping %u sparse columns: %s ...',
                  len(remove), [r.name for r in remove[:5]])

    return remove


@custom.processor()
def removeIfRedundant(dtable       : datatable.DataTable,
                      vids         : List[int],
                      corrthres    : float,
                      nathres      : Optional[float] = None,
                      pairwise     : Optional[bool]  = False,
                      skipUnknowns : Optional[bool]  = False):
    """removeIfRedundant(corrthres, [nathres], [pairwise])
    Removes columns deemed to be redundant.

    Removes columns from the variables in ``vids`` if they are redundant.

    Redundancy is determined by calculating the correlation between pairs
    of columns using `corrthres` and `nathres` - see the :func:`.isRedundant`
    function.

    If ``pairwise`` is ``True``, an alternative implementation is used which
    may be faster on data sets with high missingness correlation.

    :arg pairwise:     Use alternative pairwise implementation.

    :arg skipUnknowns: If ``True``, columns which are deemed to be redundant
                       with respect to an unknown or uncategorised column
                       are *not* dropped.
    """

    # Ignore non-numeric columns
    cols     = list(it.chain(*[dtable.columns(v) for v in vids]))
    cols     = [c for c in cols if pdtypes.is_numeric_dtype(dtable[:, c.name])]
    colnames = [c.name for c in cols]
    data     = dtable[:, colnames]

    with np.errstate(divide='ignore'):
        if pairwise:
            redundant = _pairwiseRemoveIfRedundant(
                dtable, data, corrthres, nathres)
        else:
            redundant = _removeIfRedundant(
                dtable, data, corrthres, nathres)

    redundant = util.dedup(sorted(redundant))

    if skipUnknowns:
        copy = []
        for idxa, idxb in redundant:
            colb = cols[idxa]
            bvid = colb.vid
            cats = loadtables.variableCategories(dtable.cattable, [bvid])[bvid]

            if 'unknown' in cats or 'uncategorised' in cats:
                namea = colnames[idxa]
                nameb = colnames[idxb]
                log.debug('Column %s is redundant with %s, but %s is '
                          'unknown / uncategorised, so %s will not be '
                          'dropped', namea, nameb, nameb, namea)
            else:
                copy.append((idxa, idxb))
        redundant = copy

    if len(redundant) > 0:
        log.debug('Dropping %u redundant columns', len(redundant))

    return [cols[r[0]] for r in redundant]


def _removeIfRedundant(dtable, data, corrthres, nathres=None):
    """Default fast implementation of redundancy check. Used when the
    ``pairwise`` option to :func:`removeIfRedundant` is ``False``.

    :arg dtable:    The :class:`.DataTable` containing all data
    :arg data:      ``pandas.DataFrame`` containing the data to check
    :arg corrthres: Correlation threshold - see :func:`.redundantColumns`.
    :arg nathres:   Missingness correlation threshold - see
                    :func:`.redundantColumns`.
    :returns:       Sequence of tuples of column indices, where each tuple
                    ``(a, b)`` indicates that column ``a`` is redundant with
                    respect to column ``b``.
    """

    return core.matrixRedundantColumns(data, corrthres, nathres)


def _pairwiseRemoveIfRedundant(dtable, data, corrthres, nathres=None):
    """Alternative implementation of redundancy check. Used when the
    ``pairwise`` option to :func:`removeIfRedundant` is ``True``.

    :arg dtable:    The :class:`.DataTable` containing all data
    :arg data:      ``pandas.DataFrame`` containing the data to check
    :arg corrthres: Correlation threshold - see :func:`.redundantColumns`.
    :arg nathres:   Missingness correlation threshold - see
                    :func:`.redundantColumns`.
    :returns:       Sequence of tuples of column indices, where each tuple
                    ``(a, b)`` indicates that column ``a`` is redundant with
                    respect to column ``b``.
    """

    ncols = len(data.columns)

    # If we are correlating missingness,
    # we use the naCorrelation function
    # to identify all of the column pairs
    # which are na-correlated - the pairs
    # which fail this test do not need to
    # be subjected to the correlation test
    # (and therefore pass the redundancy
    # check)
    if nathres is not None:
        nacorr = core.naCorrelation(pd.isna(data), nathres)

        # As the matrix is symmetric, we can
        # drop column pairs where x >= y.
        nacorr   = np.triu(nacorr, k=1)
        colpairs = np.where(nacorr)
        colpairs = np.vstack(colpairs).T

    # Otherwise we generate an array
    # containing indices of all column
    # pairs.
    else:
        xs, ys   = np.triu_indices(ncols, k=1)
        colpairs = np.vstack((xs, ys)).T

    # we need at least
    # one pair of columns
    if len(colpairs) == 0:
        return []

    # evaluate all pairs at once
    if not dtable.parallel:
        log.debug('Checking %u columns for redundancy', ncols)
        redundant = core.pairwiseRedundantColumns(
            data, colpairs, corrthres=corrthres)

    # evaluate in parallel
    else:
        # Split the column pairs
        # into njobs chunks, and
        # run in parallel
        chunksize  = int(np.ceil(len(colpairs) / dtable.njobs))
        pairchunks = [colpairs[i:i + chunksize]
                      for i in range(0, len(colpairs), chunksize)]

        log.debug('Checking %u columns for redundancy (%u tasks)',
                  ncols, len(pairchunks))

        with dtable.pool() as pool:
            results = []
            for i, chunk in enumerate(pairchunks):

                # We can pass the full dataframe
                # to each task, as it should be
                # read-accessible via shared memory.
                token  = 'task {} / {}'.format(i + 1, len(pairchunks))
                result = pool.apply_async(
                    core.pairwiseRedundantColumns,
                    kwds=dict(data=data,
                              colpairs=chunk,
                              corrthres=corrthres,
                              token=token))
                results.append(result)

            # wait for the tasks to complete,
            # and gather the results (indices
            # of redundant columns) into a list
            redundant = []
            for result in results:
                redundant.extend(result.get())

    return redundant


# auxvids tells the processing runner the
# "take" argument refers to other variables
# which are not processed, but are needed
# to perform the processing.
#
# "filterMissing" tells the processing
# runner *not* to remove variables which
# are not present in the data from the list
# of vids that are passed in - we do our
# own check here.
#
# Both of the above are ridiculous hacks
# which are in place because this function,
# and FUNPACK, used to parallelise things
# differently, and to preserve backwards
# compatibility.
@custom.processor(auxvids=['take'], filterMissing=False)
def binariseCategorical(dtable,
                        vids,
                        acrossVisits=False,
                        acrossInstances=True,
                        minpres=None,
                        nameFormat=None,
                        replace=True,
                        take=None,
                        fillval=None,
                        replaceTake=True):
    """binariseCategorical([acrossVisits], [acrossInstances], [minpres], [nameFormat], [replace])
    Replace a categorical column with one binary column per category.

    Binarises categorical variables - replaces their columns with
    one new column for each value, containing ``1`` for subjects
    with that value, and ``0`` otherwise.

    The :func:`.processing_functions_core.binariseCategorical` function is called
    for each variable in ``vids`` - it internally parallelises generation of the
    new columns using multiprocessing.

    :arg dtable:          The :class:`.DataTable`

    :arg vids:            Sequence of variable IDs to (independently) apply the
                          binarisation to.

    :arg acrossVisits:    If ``True``, the binarisation is applied across
                          visits for each variable.

    :arg acrossInstances: If ``True``, the binarisation is applied across
                          instances for each variable.

    :arg minpres:         Optional threshold - categorical values with less
                          than this many occurrences will not be added as
                          columns.

    :arg nameFormat:      Format string defining how the new columns should
                          be named - see below.

    :arg replace:         If ``True`` (the default), the original columns are
                          returned for removal.

    :arg take:            Optional variable ID, or sequence of variable IDs
                          (one for each of the main ``vids``) to take values
                          from. If provided, the generated columns will have
                          values from the column(s) of this variable, instead
                          of containinng binary 0/1 values. A ``take``
                          variable must have columns that match the columns of
                          the corresponding ``vid`` (by visits and instances).

    :arg fillval:         If ``take`` is provided, the value to use for
                          ``False`` rows. Defaults to ``np.nan``

    :arg replaceTake:     If ``True`` (the default), and ``takeFrom`` variables
                          were specified, the columns associated with the
                          ``take`` variables are returned for removal.

    The ``nameFormat`` argument controls how the new data columns should be
    named - it must be a format string using named replacement fields
    ``'vid'``, ``'visit'``, ``'instance'``, and ``'value'``. The ``'visit'``
    and ``'instance'`` fields may or may not be necessary, depending on the
    value of the ``acrossVisits`` and ``acrossInstances`` arguments.

    The default value for the ``nameFormat`` string is as follows:

    ================ =================== ======================================
    ``acrossVisits`` ``acrossInstances`` ``nameFormat``
    ================ =================== ======================================
    ``False``        ``False``           ``'{vid}-{visit}.{instance}_{value}'``
    ``False``        ``True``            ``'{vid}-{visit}.{value}'``
    ``True``         ``False``           ``'{vid}-{value}.{instance}'``
    ``True``         ``True``            ``'{vid}-0.{value}'``
    ================ =================== ======================================
    """  # noqa

    # get groups of columns for vid, grouped
    # according to acrossVisits/acrossInstances
    def gatherColumnGroups(vid):
        colgroups = []
        visits    = dtable.visits(   vid)
        instances = dtable.instances(vid)
        if not (acrossVisits or acrossInstances):
            for visit, instance in it.product(visits, instances):
                colgroups.append(dtable.columns(vid, visit, instance))
        elif acrossInstances and (not acrossVisits):
            for visit in visits:
                colgroups.append(dtable.columns(vid, visit))
        elif (not acrossInstances) and acrossVisits:
            for instance in instances:
                colgroups.append(dtable.columns(vid, instance=instance))
        else:
            colgroups = [dtable.columns(vid)]
        return colgroups

    defaultNameFormat = {
        (False, False) : '{vid}-{visit}.{instance}_{value}',
        (False, True)  : '{vid}-{visit}.{value}',
        (True,  False) : '{vid}-{value}.{instance}',
        (True,  True)  : '{vid}-0.{value}',
    }

    if nameFormat is None:
        nameFormat = defaultNameFormat[acrossVisits, acrossInstances]

    # if take is a single vid or None,
    # we turn it into [take] * len(vids)
    if not isinstance(take, collections.abc.Sequence):
        take = [take] * len(vids)

    if len(take) != len(vids):
        raise ValueError('take must be either None, a single variable ID, '
                         'or a list of variable IDs, one for each of the '
                         'main vids.')

    remove     = []
    newseries  = []
    newvids    = []
    newcolargs = []

    for vid, takevid in zip(vids, take):

        if (not dtable.present(vid)) or \
           (takevid is not None and not dtable.present(takevid)):
            log.warning('Variable %u (or take: %s) is not present in the '
                        'data set - skipping the binariseCategorical step',
                        vid, takevid)
            continue

        colgrps = gatherColumnGroups(vid)

        if takevid is None: takegrps = [None] * len(colgrps)
        else:               takegrps = gatherColumnGroups(takevid)

        for cols, takecols in zip(colgrps, takegrps):

            log.debug('Calling binariseCategorical (vid: %i, '
                      '%u columns)', vid, len(cols))

            if takecols is None: tkdata = None
            else:                tkdata = dtable[:, [c.name for c in takecols]]

            data              = dtable[:, [c.name for c in cols]]
            binarised, values = core.binariseCategorical(data,
                                                         minpres=minpres,
                                                         take=tkdata,
                                                         token=vid,
                                                         njobs=dtable.njobs)

            if replace:                                remove.extend(cols)
            if replaceTake and (takecols is not None): remove.extend(takecols)

            for col, val in zip(binarised.T, values):

                # make sure no periods appear
                # in the resulting column name.
                # We're assuming here that all
                # categoricals are integers,
                # which has not been verified.
                try:               val = int(val)
                except ValueError: pass

                fmtargs = {
                    'vid'      : str(int(cols[0].vid)),
                    'visit'    : str(int(cols[0].visit)),
                    'instance' : str(int(cols[0].instance)),
                    'value'    : str(val)
                }

                series = pd.Series(
                    col,
                    index=dtable.index,
                    name=nameFormat.format(**fmtargs))

                colargs = {
                    'metadata' : val,
                    'basevid'  : takevid,
                    'fillval'  : fillval
                }

                newvids   .append(vid)
                newcolargs.append(colargs)
                newseries .append(series)

    return remove, newseries, newvids, newcolargs


@custom.processor()
def expandCompound(dtable, vids, nameFormat=None, replace=True):
    """expandCompound([nameFormat], [replace])
    Expand a compound column into a set of columns, one for each value.

    Expands compound variables into a set of columns, one for each value.
    Rows with different number of values are padded with ``np.nan``.

    :arg dtable:     The :class:`.DataTable`

    :arg vids:       Sequence of variable IDs to (independently) apply the
                     expansion to.

    :arg nameFormat: Format string defining how the new columns should be named
                     - see below.

    :arg replace:    If ``True`` (the default), the original columns are
                     flagged for removal.
    """

    if nameFormat is None:
        nameFormat = '{vid}-{visit}.{instance}_{index}'

    columns   = list(it.chain(*[dtable.columns(v) for v in vids]))
    newseries = []
    newvids   = []

    for column in columns:

        data    = dtable[:, column.name]
        newdata = core.expandCompound(data)

        for i in range(newdata.shape[1]):

            coldata = newdata[:, i]
            name    = nameFormat.format(vid=column.vid,
                                        visit=column.visit,
                                        instance=column.instance,
                                        index=i)

            newvids  .append(column.vid)
            newseries.append(pd.Series(coldata,
                                       index=dtable.index,
                                       name=name))

    if replace: return columns, newseries, newvids
    else:       return          newseries, newvids
