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

import numpy as n
from numpy.polynomial import Polynomial
from lmfit.models import Model, update_param_vals
from lmfit.models import ExponentialGaussianModel as _EXPGauss

from apav.utils.hinting import *


class ExponentialGaussianModel(_EXPGauss):
    """
    Exponential gaussian model
    """
    def __init__(self, *args, **kwargs):
        """
        This model defines an exponentially modified gaussian with refined parameter min/max/initial values
        for APAV
        """
        super().__init__(*args, **kwargs)

    def guess(self, *args, **kwargs):
        vals = super().guess(*args, **kwargs)
        x = kwargs["x"]
        vals["center"].set(max=x.min(), min=0)
        vals["amplitude"].set(min=0)
        return vals


class PowerLawShiftModel(Model):
    """
    Shifted power law model
    """
    def __init__(self, *args, **kwargs):
        """
        This model defines a shifted power law with refined parameter min/max/initial values
        for APAV
        """
        def power_law(x, amplitude, center, exponent):
            # Cannot take fractional power of negative numbers
            xx = x - center
            xx[xx<0] = 1
            return amplitude * xx ** exponent
        super().__init__(power_law, *args, **kwargs)

    def guess(self, data, x: ndarray = None, **kwargs):
        """
        Estimate initial model parameter values from data.
        """
        try:
            cen = x.min() - x.min() * 0.1
            idx = n.argwhere(data > 0).ravel()
            xx, yy = n.log((x[idx]-cen)+1.e-14), n.log(data[idx]+1.e-14)
            amp, expon = Polynomial.fit(xx, yy, 1)
        except TypeError:
            cen = 0
            expon, amp = 1, n.log(abs(max(data)+1.e-9))

        pars = self.make_params(amplitude=n.exp(amp), exponent=expon, center=cen)
        update_param_vals(pars, self.prefix, **kwargs)
        pars["amplitude"].set(min=1)
        pars["exponent"].set(min=-1e3, max=-1)
        pars["center"].set(min=0, max=x.min())
        return pars
