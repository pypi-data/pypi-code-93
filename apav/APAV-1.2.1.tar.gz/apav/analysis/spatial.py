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

from apav.analysis.base import AnalysisBase
from apav.utils import validate
from apav.utils.hinting import *
from apav import Roi, RangeCollection, Ion
from apav.core.histogram import histogram2d_binwidth
from apav.core.multipleevent import get_mass_indices
from scipy.ndimage import gaussian_filter
import numpy as n


class RangedGrid(AnalysisBase):
    def __init__(self,
                 roi: Roi,
                 ranges: RangeCollection,
                 bin_width: Union[Real, Sequence[Real]] = n.array([1, 1, 1]),
                 # decompose: bool = False,
                 delocalization: Union[Real, Sequence[Real]] = n.array([3, 3, 1.5]),
                 gauss_trunc: Real = 4
                 ):
        super().__init__(roi)
        self._ranges = validate.is_type(ranges, RangeCollection)

        self._voxel = bin_width
        self._delocalization = delocalization

        if hasattr(delocalization, "__iter__") and not isinstance(delocalization, ndarray):
            self._delocalization = n.array(delocalization)

        self._gauss_trunc = validate.positive_nonzero_number(gauss_trunc)
        # self._decompose = validate.boolean(decompose)

        self._edges = None
        self._ion_grids = {}
        self._quant_grids = {}
        self._quant_cum_counts = None

        self._calculate()

    @property
    def ranges(self) -> RangeCollection:
        return self._ranges

    @property
    def bin_width(self) -> Union[Real, Sequence[Real]]:
        return self._voxel

    @property
    def delocalization(self) -> Union[Real, Sequence[Real]]:
        return self._delocalization

    @property
    def gauss_trunc(self) -> Real:
        return self._gauss_trunc

    # @property
    # def decompose(self) -> bool:
    #     return self._decompose

    @property
    def edges(self) -> ndarray:
        return self._edges

    @property
    def ion_grids(self) -> Dict[Ion, ndarray]:
        return self._ion_grids

    @property
    def composition_grids(self) -> Dict[Element, ndarray]:
        return self._quant_grids

    @property
    def composition_str_grids(self) -> Dict[Ion, ndarray]:
        return {i.symbol: j for i, j in self._quant_grids.items()}

    @property
    def composition_counts(self) -> ndarray:
        return self._quant_cum_counts

    def ion_grid(self, ion: Ion) -> ndarray:
        if ion not in self.ion_grids.keys():
            raise ValueError("Ion {} does not exist in the RangedGrid".format(ion.hill_formula))
        return self.ion_grids[ion]

    def composition_grid(self, element: Union[str, Element]) -> ndarray:
        if isinstance(element, str):
            el = None
            for i, j in self.composition_grids.items():
                if i.symbol == element:
                    el = i
                    break
            return self.composition_grids[el]
        elif isinstance(element, Element):
            return self.composition_grids[element]
        else:
            raise TypeError("Expected elemental symbol string or Element type, got {} instead".format(type(element)))

    def _calculate(self):
        dims = self.roi.dimensions
        n_voxels = (dims // self.bin_width).ravel().astype(int)

        range_elems = self.ranges.elements()

        self._ion_grids = {i.ion: n.zeros(n_voxels) for i in self.ranges.ranges}

        for i, rng in enumerate(self.ranges):
            ion = rng.ion
            low, up = rng.interval
            idx = n.argwhere((self.roi.mass >= low) & (self.roi.mass < up)).ravel()
            counts, edges = n.histogramdd(self.roi.xyz[idx], bins=n_voxels)
            if self.edges is None:
                self._edges = edges
            self._ion_grids[ion] += gaussian_filter(counts,
                                                    sigma=self.delocalization/3,
                                                    mode="constant",
                                                    truncate=self.gauss_trunc)

        self._quant_grids = {i: 0 for i in range_elems}
        elem_grids = self._quant_grids

        for ion, counts in self._ion_grids.items():
            for elem, mult in ion.comp_dict.items():
                elem_grids[elem] += mult * counts

        norm = sum(i for i in elem_grids.values())
        self._quant_cum_counts = norm
        for key in elem_grids.keys():
            ary = elem_grids[key]
            elem_grids[key] = n.divide(ary, norm, where=ary > 0)


class DensityHistogram(AnalysisBase):
    """
    Compute density histograms on an Roi
    """
    def __init__(self,
                 roi: Roi,
                 bin_width=0.3,
                 axis="z",
                 multiplicity="all"):
        """
        :param roi: region of interest
        :param bin_width: width of the bin size in Daltons
        :param axis: which axis the histogram should be computed on ("x", "y", or "z")
        :param multiplicity: the multiplicity order to compute histogram with
        """
        super().__init__(roi)
        self.bin_width = validate.positive_nonzero_number(bin_width)
        self._multiplicity = validate.multiplicity_any(multiplicity)
        if multiplicity != "all":
            roi.require_multihit_info()

        self._histogram = None
        self._histogram_extents = None
        self._axis = validate.choice(axis, ("x", "y", "z"))
        self._bin_vol = None
        self._calculate_histogram()

    @property
    def multiplicity(self):
        return self._multiplicity

    @property
    def bin_vol(self):
        return self._bin_vol

    @property
    def axis(self):
        return self._axis

    @property
    def histogram(self):
        return self._histogram

    @property
    def histogram_extents(self):
        return self._histogram_extents

    def _calculate_histogram(self):
        orient_map = {"x": 0, "y": 1, "z": 2}
        ax1, ax2 = (self.roi.xyz[:, val] for key, val in orient_map.items() if key != self.axis)
        ext_ax1, ext_ax2 = (self.roi.xyz_extents[val] for key, val in orient_map.items() if key != self.axis)
        ext = (ext_ax1, ext_ax2)

        if self.multiplicity == "all":
            self._histogram = histogram2d_binwidth(ax1, ax2, ext, self.bin_width)
        else:
            idx = get_mass_indices(self.roi.misc["ipp"], self.multiplicity)
            self._histogram = histogram2d_binwidth(ax1[idx], ax2[idx], ext, self.bin_width)

        self._histogram_extents = ext
