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

from collections import defaultdict, OrderedDict
from warnings import warn
from copy import deepcopy

import numpy as n
from tabulate import tabulate
from lmfit.models import PowerLawModel

from apav.core.multipleevent import MultipleEventExtractor, get_mass_indices
from apav.core.histogram import histogram2d_binwidth
from apav import RangeCollection, Range
from apav.core.roi import DummyRoiHistogram, Roi
from apav.visualization.factory import vfactory
from apav.analysis.base import AnalysisBase
from apav.utils import validate
from apav.utils.hinting import *
from apav.analysis.background import BackgroundCollection, Background
from apav.analysis import models


class CorrelationHistogram(AnalysisBase):
    """
    Statistical analysis of the correlation evaporation by ion pair histograms
    """
    def __init__(self,
                 roi: Roi,
                 extents: Tuple[Tuple, Tuple] = ((0, 200), (0, 200)),
                 bin_width: float = 0.1,
                 multiplicity: Union[int, str] = 2,
                 symmetric: bool = False,
                 flip: bool = False):
        """
        Correlation histograms are computed by forming all ion pairs in given multiple-events. The correlation histogram
        may be computed using any multiplicity "order", for example creating histograms from the 2nd and 5th order
        multiple events:

        >>> roi = Roi.from_epos("path_to_epos_file.epos")
        >>> corr_2 = CorrelationHistogram(roi, multiplicity=2)
        >>> corr_5 = CorrelationHistogram(roi, multiplicity=5)

        The ions from higher order multiplicities are separated into ion pair combinations. For example a 5th order
        multiple event composed of 5 ions, ABCDE is separated in the 10 ion pairs: AB AC AD AE BC BD BE CD CE DE. See
        the MultipleEventExtractor class for more detail.

        The histogram may also be formed from the ion pairs for of all multiple events combined together. This is
         achieved by passing the value "multiples" to the multiplicity keyword, indicating all ion pairs should be used:

        >>> roi = Roi.from_epos("path_to_epos_file.epos")
        >>> corr_2 = CorrelationHistogram(roi, multiplicity="multiples")

        :param roi: region of interest
        :param extents: x and y extents for the mass_histogram to be calculated
        :param bin_width: bin width in daltons
        :param multiplicity: the multiplicity to compute the histogram with
        :param symmetric: make the mass_histogram symmetric across the diagonal
        :param flip: flip the histogram along its diagonal (i.e. swap the ion1/ion2 axes)
        """
        super().__init__(roi)
        self.roi.require_multihit_info()
        self._update_suppress = True

        # Parameters
        self.extents = extents
        self.multiplicity = validate.multiplicity_non_singles(multiplicity)
        self.bin_width = bin_width
        self.symmetric = symmetric
        self.flip = flip

        self._histogram = None
        self._pairs = None
        self._pair_idx = None
        self._mevent_extractor = None

        self._update_suppress = False
        self._process()

    @property
    def histogram(self) -> ndarray:
        """
        Get the raw histogram
        """
        return self._histogram

    @property
    def symmetric(self) -> bool:
        """
        Whether or not the histogram is symmetrized
        Returns:

        """
        return self._symmetric

    @symmetric.setter
    def symmetric(self, new: bool):
        """
        Set the histogram symmetry
        """
        self._symmetric = validate.boolean(new)
        self._process()

    @property
    def bin_width(self) -> float:
        """
        Get the bin width in Da
        """
        return self._bin_width

    @bin_width.setter
    def bin_width(self, new: float):
        """
        Set the bin width
        """
        self._bin_width = validate.positive_nonzero_number(new)
        self._process()

    @property
    def extents(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get the histogram boundaries as ((ion1_min, ion1_max), (ion2_min, ion2_max))
        """
        return self._extents

    @extents.setter
    def extents(self, new: Tuple[Tuple, Tuple]):
        """
        Set the boundaries of the histogram
        """
        self._extents = validate.positive_interval_2d(new)
        self._process()

    @property
    def multiplicity(self) -> Union[int, str]:
        """
        Get the ion pair multiplicity
        """
        return self._multiplicity

    @multiplicity.setter
    def multiplicity(self, new: Union[str, int]):
        """
        Set the multiplicity of the histogram
        """
        self._multiplicity = validate.multiplicity_non_singles(new)
        self._process()

    @property
    def flip(self) -> bool:
        """
        Whether or not the histogram was flipped (transposed)
        """
        return self._flip

    @flip.setter
    def flip(self, new: bool):
        """
        Set flip, whether or not the histogram has ion 1 on the y and ion 2 on the x
        """
        self._flip = validate.boolean(new)
        self._process()

    @property
    def event_extractor(self) -> MultipleEventExtractor:
        """
        Get the MultipleEventExtractor used to filter the ion pairs
        """
        return self._mevent_extractor

    @property
    def pairs(self) -> ndarray:
        """
        Get all pairs in correlation histogram
        """
        return self._pairs

    def _process(self):
        """
        Calculate the correlation mass_histogram
        """
        # Dont calculate until the constructor is finished
        if self._update_suppress is True:
            return

        self._mevent_extractor = MultipleEventExtractor(self.roi, self.multiplicity, self.extents)
        if len(self._mevent_extractor.pairs) == 0:
            self._histogram = n.array([])
            return
        self._pairs = self.event_extractor.pairs
        mults = self._pairs

        if self.symmetric is True:
            mults = n.vstack((mults, mults[:, ::-1]))

        rng_h, rng_v = self.extents
        self._histogram = histogram2d_binwidth(mults[:, 0], mults[:, 1], (rng_h, rng_v), self.bin_width)

        if self.flip is True:
            self._histogram = self._histogram.T

    def plot(self):
        """
        Interactively view the histogram. This function is for exploring the dataset interactively, while maintaining
        performance. Publication quality plots should be created in other software intended for plotting. See the
        `export` function for saving the histogram in a format suitable for conventional plotting.

        """
        widget = vfactory.make("interactive_correlation_histogram_plot", self)
        return widget

    def export(self, path: str):
        """
        Export the histogram as a text image, which should processable in most other applications.
        :param path: Filepath for the image
        """
        n.savetxt(path, self.histogram, delimiter=",")


class RangedMassSpectrum(AnalysisBase):
    """
    Uncorrected ranged mass spectrum analysis
    """
    def __init__(self,
                 roi: Roi,
                 ranges: RangeCollection,
                 bin_width: float = 0.01,
                 decompose: bool = False,
                 percent: bool = False,
                 upper: float = 200,
                 multiplicity: Union[int, str] = "all"):
        """
        This class is used for performing mass spectrum quantification on uncorrected mass histograms. No background
        subtractions are performed, see :class:`NoiseCorrectedMassSpectrum` and :class:`LocalBkgCorrectedMassSpectrum` for
        different levels of background correction.

        This computation does not use any histogram to perform its computation (the composition), however, the histogram
        is computed for the sake of plotting the ranged mass spectrum in :meth:`RangedMassSpectrum.plot` and can be accessed from
        :attr:`RangedMassSpectrum.histogram`

        The mass ranges are provided as a :class:`RangeCollection` instance to the `ranges` argument.

        :param roi: Region of interest
        :param ranges: RangeCollection defining mass ranges
        :param decompose: Decompose polyatomic ions into their elemental components or not
        :param percent: Return composition as percentage instead of fraction
        :param upper: The upper value for the mass spectrum
        :param multiplicity: Option to quantify specific multiple-hit events, either "all"
            for the all hits, int=1 for singles, int > 1 for specific multi-hits, or "multiples" for all multiples
        """
        super().__init__(roi)
        if not isinstance(ranges, RangeCollection):
            raise TypeError(f"Expected type RangeCollection not {type(ranges)}")

        self._ranges = ranges
        self._percent = validate.boolean(percent)
        self._decompose = decompose
        self._bin_width = validate.positive_nonzero_number(bin_width)
        self._multiplicity = validate.multiplicity_any(multiplicity)
        self._upper = validate.positive_nonzero_number(upper)

        if multiplicity != "all":
            self.roi.require_multihit_info()

        # The mass_histogram is not strictly necessary in the quantification scheme for this class, but we use it
        # for plotting the ranges and for derived classes
        self._histogram = self.roi.mass_histogram(self.bin_width,
                                                  multiplicity=multiplicity,
                                                  norm=False,
                                                  upper=upper)
        self._results_dict = None
        self._preprocess()
        self._process()

    @property
    def upper(self) -> float:
        """
        Get the upper limit of the calculated histogram
        """
        return self._upper

    @property
    def histogram(self) -> ndarray:
        """
        Get the binned computed histogram
        """
        return self._histogram

    @property
    def ranges(self) -> RangeCollection:
        """
        Get the RangeCollection defining all mass ranges
        """
        return self._ranges

    @property
    def percent(self) -> bool:
        """
        Whether the quantification is in percentage or not (fraction)
        """
        return self._percent

    @property
    def decompose(self) -> bool:
        """
        Whether or not molecular species are broken down into elemental forms
        """
        return self._decompose

    @property
    def multiplicity(self) -> Union[str, int]:
        """
        Get the ion multiplicity user for quantification
        Returns:

        """
        return self._multiplicity

    @property
    def bin_width(self) -> float:
        """
        Get the bin width in Da
        """
        return self._bin_width

    @property
    def quant_dict(self) -> Dict[str, Tuple[float, float]]:
        """
        Get a dictionary of the quantification results

        The keys are a string of the range composition and the values are a tuple of composition % or
        fraction (depending on the percent kwarg) and the total counts in that range
        """
        return deepcopy(self._results_dict)

    def print(self):
        """
        Convenience to print the quantification results
        """
        quant = self.quant_dict
        data = [(i[0], i[1][0], i[1][1]) for i in quant.items()]
        print(tabulate(data, headers=("Ion", "Composition", "Counts")))

    def counts_in_range(self, rng: Range) -> int:
        """
        Calculate the number of counts within a specified mass/charge range. This method should be overridden
        in subclasses since the calculated counts in a range is implementation-specific (i.e. background subtraction).
        """
        if self.multiplicity != "all":
            self.roi.require_multihit_info()

        if not isinstance(rng, Range):
            raise TypeError("Expected a Range object")
        if self.multiplicity == "all":
            idx = n.argwhere((self.roi.mass >= rng.lower) & (self.roi.mass < rng.upper))
        elif isinstance(self.multiplicity, int) or self.multiplicity == "multiples":
            idxs = get_mass_indices(self.roi.misc["ipp"], multiplicity=self.multiplicity)
            idx = n.argwhere((self.roi.mass[idxs] >= rng.lower) & (self.roi.mass[idxs] < rng.upper))
        else:
            raise ValueError("Bad input")
        return idx.size

    def _preprocess(self):
        """
        Any pre-processing that should be done prior to quantification. This method should be overridden
        in subclasses (if) any data needs to be available prior to calls to self.counts_in_range
        """

    def _process(self):
        """
        Perform the quantification. This method should NOT be overridden and works for all
        variation in mass spectrum quantification scheme. Instead, self.counts_in_range() should be re-implemented
        for any subclassed quantification method, which is called here to do the computation
        """
        # Normalization factor if percentage flag is enabled
        norm = 100 if self.percent else 1

        ion_counts = defaultdict(lambda: 0)
        atomic_counts = defaultdict(lambda: 0)
        for rng in self.ranges:
            a = rng.ion.hill_formula
            ranged_counts = self.counts_in_range(rng)
            ion_counts[rng.formula] += ranged_counts

            for element, number in rng.ion.comp_dict.items():
                atomic_counts[element.symbol] += number*ranged_counts

        # Ionic quantification
        ion_total = sum(ion_counts.values())
        ionic_quant = {}
        for ion, count in ion_counts.items():
            ionic_quant[ion] = norm*count/ion_total

        # Atomic quantification
        atomic_total = sum(atomic_counts.values())
        atomic_quant = {}
        for element, count in atomic_counts.items():
            atomic_quant[element] = norm*count/atomic_total

        quant = OrderedDict()
        if self.decompose is False:
            for i in ionic_quant.keys():
                quant[i] = (ionic_quant[i], ion_counts[i])
        elif self.decompose is True:
            for i in atomic_quant.keys():
                quant[i] = (atomic_quant[i], atomic_counts[i])

        self._results_dict = dict(quant)

    def plot(self):
        """
        Get a plot to visualize the mass spectrum
        """
        plt = vfactory.make("mass_spectrum_plot_ranged", self)
        return plt


class NoiseCorrectedMassSpectrum(RangedMassSpectrum):
    """
    Ranged mass spectrum analysis with correction for random noise background
    """
    def __init__(self,
                 roi: Roi,
                 ranges: RangeCollection,
                 noise_background: Background = Background((0.1, 0.75), model=PowerLawModel()),
                 **kwargs):
        """
        This class performs mass spectrum quantification on mass histograms after removing background from random
        noise. I.e. this noise is corrected by fitting a background model to the initial portion of the mass spectrum,
        usual before 1 Dalton. The default model for the fit can be modified using the ``noise_background`` keyword
        argument.

        Additional keyword arguments are passed to :class:`RangedMassSpectrum`.

        The quantification can be done on manually provided mass spectra instead of an Roi by using the alternate
        constructor :meth:`NoiseCorrectedMassSpectrum.from_array`.

        :param roi: Region of interest
        :param ranges: RangeCollection defining mass ranges
        :param noise_background: Background defining the random noise background

        :param **kwargs: Keyword arguments passed to NoiseCorrectedMassSpectrum constructor
        """
        self._noise_bkg = noise_background
        self.__corrected_hist = None
        self._noise_fit_data = None
        super().__init__(roi, ranges, **kwargs)

    @classmethod
    def from_array(cls,
                   x: ndarray,
                   y: ndarray,
                   ranges: RangeCollection,
                   decompose: bool = False,
                   percent: bool = False):
        """
        Create the :class:`NoiseCorrectedMassSpectrum` from a numpy array (of a mass spectrum) instead of a :class:`Roi`
        """
        binwidth = x[1] - x[0]
        retn = cls(DummyRoiHistogram(x, y),
                   ranges,
                   decompose=decompose,
                   percent=percent,
                   bin_width=binwidth)

        return retn

    @property
    def noise_corrected_histogram(self) -> ndarray:
        """
        Get the noise corrected mass histogram as a numpy array
        """
        return self.__corrected_hist

    @property
    def noise_background(self) -> Background:
        """
        Get the :class:`Background` instance defining the noise background
        :return:
        """
        return self._noise_bkg

    @property
    def noise_fit_data(self) -> ndarray:
        """
        The fit to the random noise background
        """
        return self._noise_fit_data

    @property
    def noise_counts(self) -> float:
        """
        Get the area of the noise fit
        """
        return self.noise_background.area

    def counts_in_range(self, rng: Range) -> int:
        """
        Calculate the corrected counts in a range on the mass spectrum. Overwritten from
        :meth:`RangedMassSpectrum.counts_in_range`.

        :param rng: Range instance for the computation
        """
        if not isinstance(rng, Range):
            raise TypeError(f"Expected a Range object not type {type(rng)}")

        x, y = self.noise_corrected_histogram

        idx = n.argwhere((x >= rng.lower) & (x < rng.upper))
        counts = int(n.sum(y[idx]))
        return counts

    def _preprocess(self):
        # Construct the corrected mass_histogram prior to quantification
        x, y = self.histogram
        self.noise_background.fit(x, y)
        fit_y = self.noise_background.eval(x)
        self._noise_fit_data = x, fit_y
        self.__corrected_hist = x, y - fit_y

    def plot(self):
        """
        Get a interactive plot of the noise corrected mass spectrum.
        """
        plt = vfactory.make("mass_spectrum_plot_noise_corrected", self)
        return plt


class LocalBkgCorrectedMassSpectrum(NoiseCorrectedMassSpectrum):
    """
    Ranged mass spectrum analysis with correction for random noise and local background subtraction
    """
    def __init__(self,
                 roi: Roi,
                 ranges: RangeCollection,
                 local_background: BackgroundCollection,
                 show_warnings: bool = False,
                 **kwargs):
        """
        This class performs mass spectrum quantification correcting for random noise background, as well as local
        background subtraction for isotopic peaks.

        The random noise background subtraction is performed by :class:`NoiseCorrectedMassSpectrum` and can be adjusted
        by the keyword arguments passed  to it.

        The local background subtractions are defined by the `local_background` parameter which is a
        :class:`BackgroundCollection` instance. See the :class:`BackgroundCollection` for detail. Generally, backgrounds are defined
        on a fit interval(s), and each background defines an interval(s) which determines the mass ranges it will
        apply to. For example:

        >>> roi = Roi.from_pos("path_to_pos_ file.pos")
        >>> ranges = RangeCollection.from_rng("path_to_range_file.rng")
        >>> bkgs = BackgroundCollection()
        >>> bkgs.add(Background((10, 12), [(14, 15), (20, 22)]))
        >>> bkgs.add(Background([(32, 40), (42, 45)], (47, 50)))
        >>> quant = LocalBkgCorrectedMassSpectrum(roi, ranges, bkgs)
        >>> quant.print()

        Does a local background subtracted quantification using 2 backgrounds fits and prints the result.

        :param roi: Region of interest
        :param ranges: RangeCollection defining mass ranges
        :param local_background: BackgroundCollection defining background model
        :param noise_background: Background defining the random noise background
        :param disable_warnings: Disable warnings (such as when a range does has not been assigned a background)
        :param **kwargs: Keyword arguments passed to :class:`NoiseCorrectedMassSpectrum` constructor
        """
        self._local_bkg = local_background
        self._show_warnings = show_warnings
        self.__local_bkg_hist = None
        self.__corrected_hist = None
        super().__init__(roi, ranges, **kwargs)

    @classmethod
    def from_array(cls,
                   x: ndarray,
                   y: ndarray,
                   ranges: RangeCollection,
                   background: BackgroundCollection,
                   decompose: bool = False,
                   percent: bool = False):
        """
        Mass spectrum analysis from an array
        """
        # Call constructor with a dummy roi
        binwidth = x[1] - x[0]
        retn = cls(DummyRoiHistogram(x, y),
                   ranges,
                   background,
                   decompose=decompose,
                   percent=percent,
                   bin_width=binwidth,
                   cutoff=x[-1])

        return retn

    @property
    def show_warnings(self):
        """
        Whether or not to show warnings when there are ranges that are not background subtracted
        """
        return self._show_warnings

    @property
    def background_collection(self) -> BackgroundCollection:
        """
        Get the :class:`BackgroundCollection` applied to the computation
        """
        return self._local_bkg

    @property
    def local_bkg_fit(self) -> ndarray:
        return self.__local_bkg_hist

    @property
    def local_bkg_corrected_histogram(self) -> ndarray:
        return self.__corrected_hist

    def counts_in_range(self, rng: Range) -> int:
        """
        Calculate the number of counts within a specified mass/charge range.
        Overwritten from :meth:`NoiseCorrectedMassSpectrum.counts_in_range`
        """
        if not isinstance(rng, Range):
            raise TypeError(f"Expected a Range object not type {type(rng)}")

        x, y = self.local_bkg_corrected_histogram

        idx = n.argwhere((x >= rng.lower) & (x < rng.upper))
        counts = int(n.sum(y[idx]))
        return counts

    def _preprocess(self):
        super()._preprocess()
        x, y = self.noise_corrected_histogram
        self.background_collection.fit(x, y)

        sig_y = n.zeros_like(x)
        bkg_y = n.zeros_like(x)

        for rng in self.ranges:
            bkg = self.background_collection.find_background(rng)
            xmin = rng.lower
            xmax = rng.upper
            idx = n.argwhere((x >= xmin) & (x < xmax)).ravel()
            if bkg is not None:
                # self._background_map[rng.id] = bkg
                rng_bkg = bkg.eval(x[idx])
                rng_signal = y[idx] - rng_bkg
                sig_y[idx] = rng_signal
                bkg_y[idx] = rng_bkg
            else:
                sig_y[idx] = y[idx]
                if self.show_warnings:
                    warn(f"No background could be matched to {rng.ion.hill_formula} from {rng.lower}-{rng.upper} Da."
                         f" This range will not be background corrected.")

        self.__local_bkg_hist = (x, bkg_y)
        self.__corrected_hist = (x, sig_y)

    def plot(self):
        """
        Get an interactive plot showing the background fits
        """
        plt = vfactory.make("mass_spectrum_plot_local_bkg_corrected", self)
        return plt
