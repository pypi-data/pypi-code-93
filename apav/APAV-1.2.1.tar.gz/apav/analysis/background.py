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

from copy import deepcopy

from apav.utils import validate
from apav.core.range import Range
from apav.utils.hinting import *
from apav.utils.helpers import intervals_intersect
from apav.analysis import models

import numpy as n
from lmfit.minimizer import MinimizerResult
from lmfit.models import PowerLawModel

settings = {
    "method": "least_squares",
    "nan_policy": "raise",
    "xtol": 1e-7,
    "ftol": 1e-7
}


class Background:
    """
    Defines a background model through a specified range of a mass spectrum.
    """
    def __init__(self,
                 fit_interval: Union[Tuple[float, float], Sequence[Tuple[float, float]]],
                 include_interval: Union[Tuple[float, float], Sequence[Tuple[float, float]]] = (),
                 model: Type[Model] = models.PowerLawShiftModel()):
        """
        A background is fit on the provided fit_interval(s). Intervals provided to `include_interval` define
        ranges where mass spectrum ranges will use the background model for background subtraction. For example:

        >>> bkg = Background((10, 12), (13, 20), models.PowerLawShiftModel())

        Fits a shifted power law  on the interval from 10 -> 12 Da. The background will be subtracted and applied to
        any mass ranges that begin in the interval from 13 -> 20 Da.

        >>> bkg = Background([(10, 12), (15, 16)], [(13, 20), (22, 24)], models.PowerLawShiftModel())

        Will fit the same power law model on 2 intervals from 10 -> 12 and 15 -> 16 Da. This background will be
        subtracted and applied to any mass ranges that begin in either of the intervals 13 ->20 Da or 22 -> 24 Da. This
        allows simple control over which background applies to which mass ranges, without being too explicit.

        :param fit_interval: single or multiple intervals on the x to fit the background model
        :param include_interval: mass ranges to apply the background subtraction to
        :param model: the background model to be used
        """
        if not isinstance(model, Model):
            raise TypeError(f"Background model must be and lmfit Model not {type(model)}.")

        self.model = model
        self._include_intervals = []
        self._fit_intervals = []
        self._area = None

        if len(fit_interval) == 0:
            raise ValueError("Background must be initialized with valid fit range")

        if hasattr(fit_interval[0], "__iter__"):
            for i in fit_interval:
                validate.positive_interval(i)
                self.add_fit_interval(i)
        else:
            self.add_fit_interval(validate.positive_interval(fit_interval))

        if len(include_interval) > 0:
            if hasattr(include_interval[0], "__iter__"):
                for intv in include_interval:
                    validate.positive_interval(intv)
                    self.add_include_interval(intv)
            else:
                self.add_include_interval(validate.positive_interval(include_interval))

        self._fit_results = None

    @property
    def fit_intervals(self) -> List[Tuple[Real, Real]]:
        """
        Get the fit intervals assigned to this background
        """
        return self._fit_intervals

    @property
    def lower(self) -> Real:
        """
        Get the lower value of the fit interval
        """
        return min(i[0] for i in self.fit_intervals)

    @property
    def upper(self) -> Real:
        """
        Get the upper value of the fit interval
        """
        return max(i[1] for i in self.fit_intervals)

    @property
    def area(self) -> Real:
        """
        Get the area of the fit
        """
        if self._area is None:
            raise Exception("Background that has not been fit has no area")

        return self._area

    @property
    def fit_results(self) -> MinimizerResult:
        """
        Get the fit results of the background
        """
        return self._fit_results

    def eval(self, x: ndarray) -> ndarray:
        """
        Compute the background curve on the given interval x
        :return: the background estimate on the given range
        """
        if self.fit_results is None:
            raise AttributeError("Background must be fit before it can be evaluated.")

        return self.fit_results.eval(x=x)

    def contains_mass(self, value) -> bool:
        """
        Determine if this background contains the mass/charge ratio in any include range interval [min-max)
        """
        for imin, imax in self._include_intervals:
            if imin <= value < imax:
                return True
        return False

    @property
    def include_intervals(self) -> List[Tuple[Real, Real]]:
        """
        Get the list of intervals that assign ranges (:class:`Range`) to the background
        """
        return self._include_intervals

    def fit(self, spec_x: ndarray, spec_y: ndarray):
        """
        Fit the background to the spectrum (spec_x, spec_y)
        :param spec_x: array of x axis
        :param spec_y: array of y axis
        """
        x = n.array([])
        y = n.array([])
        for i in self.fit_intervals:
            idx = n.argwhere((i[0] <= spec_x) & (i[1] > spec_x)).ravel()
            x = n.concatenate((x, spec_x[idx]))
            y = n.concatenate((y, spec_y[idx]))

        params = self.model.guess(y, x=x)

        try:
            self._fit_results = self.model.fit(y,
                                               params=params,
                                               x=x,
                                               method=settings["method"],
                                               nan_policy=settings["nan_policy"],
                                               fit_kws={"xtol": settings["xtol"],
                                                        "ftol": settings["ftol"]}
                                               )
        except Exception as e:
            raise RuntimeError(f"Fit failed on background with fit interval(s) {self.fit_intervals}, with error:\n\t{e}")

        self._area = n.sum(self.fit_results.best_fit)

    def add_fit_interval(self, minmax: Tuple[Real, Real]):
        """
        Add fit interval to the background
        :param minmax: the new fit interval
        """
        validate.positive_interval(minmax)

        if any(intervals_intersect(minmax, i) for i in self.fit_intervals):
            raise validate.IntervalIntersectionError(f"Cannot have intersecting fit ranges ({minmax[0]}-{minmax[1]})")

        self._fit_intervals.append(minmax)

    def add_include_interval(self, minmax: Tuple[float, float]):
        """
        Add a specified interval through which any containing mass ranges will be matched. This will occur
        if the lower bound of a given mass range is contained within rng. Overlapping ranges are allowed.
        """
        validate.positive_interval(minmax)
        self._include_intervals.append(minmax)

    def reset(self):
        """
        Clear the current background fit and data
        """
        # self.fit_coef = None
        # self.fit_curve = None
        self._fit_results = None
        self._area = None


class BackgroundCollection:
    """
    Handles operate on a collection of Backgrounds
    """
    def __init__(self):
        """
        This class is used to contain all backgrounds that operate on a spectrum/ROI.

        >>> bkgs = BackgroundCollection()
        >>> bkg1 = Background((10, 12), (13, 14))
        >>> bkgs.add(bkg1)

        or

        >>> bkgs = BackgroundCollection()
        >>> bkgs.add(Background((10, 12), (13, 14)), models.ExponentialModel)
        >>> bkgs.add(Background((48, 52), (60, 65)), models.PowerLawShiftModel)

        This will fit the first background model on the interval 10 -> 12 Da and apply to mass ranges begining from
        13 -> 14 Da using an exponential decay model. The second background is fit from 48 -> 52 Da and is applied to
        mass ranges beginning between 60 -> 65 Da, using a Power Law model.

        """
        self._bkgs = []
        self.__index = 0

    def __iter__(self):
        self.__index__ = 0
        return self

    def __next__(self):
        if len(self.backgrounds) == 0 or self.__index == len(self.backgrounds):
            raise StopIteration
        else:
            self.__index += 1
            return self.backgrounds[self.__index - 1]

    def __len__(self):
        return len(self.backgrounds)

    def __str__(self):
        bkgs = self.sorted()
        retn = "Background collection\n"
        retn += f"Number of backgrounds: {len(self)}\n"
        for i, bkg in enumerate(bkgs):
            retn += f"Background {i+1}:\n"
            retn += f"\tFit interval: {bkg.lower}-{bkg.upper} Da\n"
            retn += f"\tModel: {bkg.eval_func.descr}\n"

            for j, incl_rng in enumerate(bkg.include_intervals):
                retn += f"\tInclude mass range {j+1}: {incl_rng[0]}-{incl_rng[1]} Da\n"

            retn += f"Fit coef: {bkg.fit_coef}\n"
        return retn

    def __getitem__(self, item) -> Background:
        return self._bkgs[item]

    @property
    def backgrounds(self) -> List[Background]:
        """
        Get a list of backgrounds (:class:`Background`) in the collection
        :return:
        """
        return self._bkgs

    def sort(self):
        """
        Sort the BackgroundCollection in-place
        """
        self._bkgs = sorted(self._bkgs, key=lambda x: x.lower)

    def sorted(self) -> BackgroundCollection:
        """
        Get a sorted copy of the BackgroundCollection
        """
        retn = deepcopy(self)
        retn.sort()
        return retn

    def add(self, newbkg: Background):
        """
        Add a new :class:`Background` to the collection
        :param newbkg: the new background
        """
        if not isinstance(newbkg, Background):
            raise TypeError("Expected a Background object, not {}".format(type(newbkg)))

        for bkg in self._bkgs:
            if _background_includes_overlap(newbkg, bkg):
                raise RuntimeError(f"Cannot have overlapping include ranges between backgrounds.")
        self._bkgs.append(newbkg)
        return newbkg

    @classmethod
    def from_bkg(cls, fpath: str):
        """
        Load background information from file (see BackgroundCollection.export)
        """
        validate.file_exists(fpath)
        raise NotImplementedError()

    def export(self, fpath: str):
        """
        Save background information to file for reuse
        """
        validate.file_exists(fpath)
        raise NotImplementedError()

    def find_background(self, rng: Range):
        """
        Find a background whos included mass ranges intersects a Range's mass range.
        If no background is found return None
        """
        for bkg in self._bkgs:
            if bkg.contains_mass(rng.lower):
                return bkg
        return None

    def reset(self):
        """
        Clear the calculated data for each background
        """
        for bkg in self._bkgs:
            bkg.reset()

    def fit(self, spec_x: ndarray, spec_y: ndarray):
        """
        Do the calculation of each background with respect the provided mass spectrum
        :param spec_x: array of x axis
        :param spec_y: array of y axis
        """
        self.reset()
        for bkg in self.backgrounds:
            bkg.fit(spec_x, spec_y)


def _background_includes_overlap(bkg1: Background, bkg2: Background) -> bool:
    """
    Determine if two backgrounds' included ranges overlap
    """
    for rng1 in bkg1.include_intervals:
        for rng2 in bkg2.include_intervals:
            if intervals_intersect(rng1, rng2) is True:
                return True
    return False
