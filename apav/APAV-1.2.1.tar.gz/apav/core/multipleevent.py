"""
This file is part of APAV.

APAV is a python package for performing analysis and visualization on
atom probe tomography data sets.

Copyright (C) 2018 Jesse Smith

APAV is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

APAV is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with APAV.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import annotations
import numpy as n

from apav.utils import validate
from apav.utils.validate import NoMultiEventError
from apav.utils.hinting import *
import apav as ap


class MultipleEventExtractor:
    """
    Handle extraction and access of multiple-event related data from an Roi
    """
    def __init__(self, roi, multiplicity: Union[int, str], extents: Tuple[Tuple, Tuple] = ((0, 200), (0, 200))):
        """
        This class is responsible for extracting arbitrary multiple event data from Rois. The output is formatted
        in as pairs, i.e. a 6th order multiple event of the composition ABCDEF is formatted into the 15 ion pairs:

        AB
        AC
        AD
        AE
        AF
        BC
        BD
        BE
        BF
        CD
        CE
        CF
        DE
        DF
        EF

        The number of ion pairs generated from any nth order multiplicity can be calculated using
        :func:`pairs_per_multiplicity`.

        This class supports any multiplicity > 1, and also supports extracting the combined pairs all multiple events.
        For example, all of these are valid:

        >>> roi = Roi.from_epos("path_to_epos_file.epos")
        >>> mevents = MultipleEventExtractor(roi, multiplicity=2)  # Ion pairs from 2nd or multiple events
        >>> mevents = MultipleEventExtractor(roi, multiplicity=11)  # Ion pairs from 11th or multiple events
        >>> mevents = MultipleEventExtractor(roi, multiplicity="multiples")  # Ion pairs from all multiple events

        The pairs can be access from

        >>> mevents.pairs

        More broadly, the indices of the pairs are accessed via

        >>> mevents.pair_indices

        Which allows for performing arbitrary analysis of multiple events on any data set attached to the Roi. For
        example, to form a plot of the difference in mass/charge ratio to distance between the ion pair in detector
        coordinates (to look at orientational properties of molecular dissociation):

        >>> roi = Roi.from_epos("path_to_epos_file.epos")
        >>> mevents = MultipleEventExtractor(roi, multiplicity="multiples")  # Use all multiple events
        >>> mass = roi.mass[mevents.pair_indices]
        >>> det_x = roi.misc["det_x"][mevents.pair_indices]
        >>> det_y = roi.misc["det_y"][mevents.pair_indices]
        >>> dx = np.diff(det_x)
        >>> dy = np.diff(det_y)
        >>> diff_det = np.linalg.norm([dx, dy], axis=0)
        >>> diff_mass = np.diff(mass)
        >>> plt.hist2d(diff_det, diff_mass, bins=100)
        >>> plt.plot()

        :param roi: region of interest
        :param multiplicity: multiplicity order (int > 1 or "multiples")
        :param extents: two dimensional range to extract events from (think correlation histograms)
        """
        self._roi = roi
        self._multiplicity = validate.multiplicity_non_singles(multiplicity)
        self._pair_indices = ndarray([])
        self._pairs = ndarray([])
        self._extents = validate.positive_interval_2d(extents)
        self._process()

    @property
    def roi(self) -> ap.Roi:
        """
        Get the :class:`Roi` used in the :class:`MultipleEventExtractor`
        """
        return self._roi

    @property
    def multiplicity(self) -> Union[int, str]:
        """
        Get the multiplicity of multiple events in the :class:`MultipleEventExtractor`. Either: int>1 or "multiples
        """
        return self._multiplicity

    @property
    def pairs(self) -> ndarray:
        """
        Get the array of all ion pairs. These are ion pairs regardless of the multiplicity so the arrays is Mx2
        """
        return self._pairs

    @property
    def n_pairs(self) -> int:
        """
        Get the number of pairs extracted
        """
        return self.pairs.shape[0]

    @property
    def pair_indices(self) -> ndarray:
        """
        Get the array of indices for the pairs. This is the same shape as :meth:`MultipleEventExtractor.pairs`
        but this is used to index map ion pairs to other positional data in the :class:`Roi`.
        """
        return self._pair_indices

    @property
    def extents(self) -> Tuple[Tuple[Real, Real], Tuple[Real, Real]]:
        """
        Get the 2-dimensional boundary that was used to extract the ion pairs
        """
        return self._extents

    def _process(self):
        pairs, idx = _multievents2pairs(self.roi, self.multiplicity, self.extents)
        self._pairs = pairs
        self._pair_indices = n.array(idx, dtype=int)


def pairs_per_multiplicity(multiplicity: int):
    """
    The number of unique ion pairs produced from a single multiple event of given multiplicity.

    A 6th-order multiple event composed of ions ABCDEF produces the 15 ion pairs:

    AB
    AC
    AD
    AE
    AF
    BC
    BD
    BE
    BF
    CD
    CE
    CF
    DE
    DF
    EF

    >>> pairs_per_multiplicity(6)
    15

    :param multiplicity: integer multiplicity order
    """
    validate.multiplicity_singular_two_or_greater(multiplicity)
    return int(((multiplicity-1)**2 + (multiplicity-1))/2)


def _multievents2pairs(roi: ap.Roi,
                       multiplicity: Union[int, str],
                       extents: Tuple[Tuple, Tuple]) -> Tuple[ndarray, ndarray]:
    """
    Generate ion pairs from an roi with any multiplicity, or all multiples
    :param roi: Roi object
    :param multiplicity: Any multiplicity value >= 2 or "multiples" for all
    :param extents: 2-dimensional boundary to extract pars from
    """
    multiplicity = validate.multiplicity_non_singles(multiplicity)
    roi.require_multihit_info()

    if isinstance(multiplicity, int):
        data, idx_ary = _aggregate_multiples_with_idx(roi, multiplicity)

        # For multiplicity 2 the result from aggregate_multiples is already formatted in pairs
        if multiplicity == 2:
            pairs = data
            pairs_idx = idx_ary
        else:
            tri = n.array(n.triu_indices(multiplicity, 1)).T
            idx = tri.ravel() + multiplicity*n.arange(data.shape[0])[None].T
            pairs = data.ravel()[idx.reshape((-1, 2))]
            pairs_idx = idx_ary.ravel()[idx.reshape((-1, 2))]

            # Filter out pairs outside the supplied extents
        filt = n.where((pairs[:, 0] >= extents[0][0]) &
                       (pairs[:, 0] <= extents[0][1]) &
                       (pairs[:, 1] >= extents[1][0]) &
                       (pairs[:, 1] <= extents[1][1]))[0]

        return pairs[filt], pairs_idx[filt]

    elif multiplicity == "multiples":
        mults, counts = roi.multiplicity_counts()
        total_pairs = sum(int(counts[i] * pairs_per_multiplicity(mults[i])) for i in range(mults.shape[0]) if mults[i] > 1)
        pairs = n.zeros([total_pairs, 2])
        pairs_idx = n.zeros_like(pairs)

        last_idx = 0
        dat = []
        idxs = []
        for i, mult in enumerate(mults):
            if mult < 2:
                continue
            new_pairs, new_idx = _multievents2pairs(roi, mult, extents)
            dat.append(new_pairs)
            idxs.append(new_idx)
            pairs[last_idx: last_idx+new_pairs.shape[0]] = new_pairs
            pairs_idx[last_idx: last_idx+new_pairs.shape[0]] = new_idx
            last_idx += new_pairs.shape[0]
        if len(dat) == 0:
            return n.array([]), n.array([])
        else:
            return n.concatenate([i for i in dat]), n.concatenate([i for i in idxs])


def _aggregate_multiples_with_idx(roi, multiplicity: int = 2) -> Tuple[ndarray, ndarray]:
    """
    Find the hits belonging to multi-hits of a specified multiplicity
    :param roi: Roi
    :param multiplicity: The event multiplicity, int > 0
    :return: a MxN matrix of mass/charge values, M=number of multiple hits N=multiplicity
    """
    if not roi.has_multiplicity_info():
        raise NoMultiEventError()
    validate.multiplicity_singular_one_or_greater(multiplicity)

    init_idx = n.where(roi.misc["ipp"] == multiplicity)[0]
    retn = n.zeros([init_idx.size, multiplicity])
    indices = n.zeros_like(retn)
    for i in range(multiplicity):
        retn[:, i] = roi.mass[init_idx + i]
        indices[:, i] = init_idx + i
    return retn, indices


def get_mass_indices(ipp: ndarray, multiplicity: Union[int, str]) -> ndarray:
    """
    Get the array indices corresponding to multi-event events of a specific multiplicity

    :param ipp: array of ions per pulse
    :param multiplicity: vent multiplicity
    :return: array of indices into ipp
    """
    validate.multiplicity_any_singular_or_all_multiples(multiplicity)

    if isinstance(multiplicity, (int, n.int64, n.int32, n.int16, n.int8)):
        if multiplicity == 1:
            return n.where(ipp == 1)[0]
        else:
            nhits = n.count_nonzero(ipp == multiplicity)
            retn = n.zeros(multiplicity * nhits)
            first = n.where(ipp == multiplicity)[0]
            retn[0::multiplicity] = first

            for i in range(1, multiplicity):
                retn[i::multiplicity] = first+i

            return retn.astype(int)
    elif multiplicity == "multiples":
        # All multiple hits
        return n.where(ipp != 1)[0]
    else:
        raise ValueError("Bad input")

