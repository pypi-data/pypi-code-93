#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

import numpy as np
from scipy.optimize import minimize


class InverseTransformSampling2D:
    """
    Uses inverse transform sampling on a discrete, pre-computed grid. Advantage: The sampling
    process is equally fast, independent of the underlying distribution. Disadvantage: Linearity
    assumption between the different grid points.
    """

    def __init__(self, distribution, boundaries):
        """
        Initialize the sampler by pre-computing the distribution on the specified grid.

        Parameters
        ----------
        distribution : callable
            distribution(x, y) should return the distribution's value at (x, y).
        boundaries : list or tuple
            (Lower) boundaries of grid cells with respect to x (as returned from np.linspace).
        """
        super().__init__()

        boundaries = np.asarray(boundaries)
        dxs = boundaries[1:] - boundaries[:-1]
        xs = boundaries[:-1] + dxs / 2.

        prob = distribution(xs) * dxs
        prob /= np.sum(prob)

        # Cumulative distribution function with 0 prepended.
        self.cdf = np.insert(np.cumsum(prob), 0, [0.])
        self.edges = boundaries

    def create_samples(self, count):
        """
        Generate samples from the underlying distribution.

        Parameters
        ----------
        count : int
            Number of samples.

        Returns
        -------
        samples : list[tuple]
            Samples in the form (x, y).
        """
        index = np.searchsorted(self.cdf, np.random.random(count), side=str('right')) - 1
        return np.random.uniform(self.edges[index], self.edges[index + 1])


class RejectionSampling2D:
    """
    Uses rejection sampling on a continuous distribution. Advantage: Continuous values are
    returned. Disadvantage: For "wavy" distributions (or rather distributions which are very
    different from being uniform) the sampling process can take a significant amount of time
    as many attempts will be rejected.
    """

    def __init__(self, distribution, x_min, x_max, p_max=None):
        """
        Parameters
        ----------
        distribution : callable
            distribution(x, y) should return the distribution's value at (x, y).
        x_min : float
        x_max : float
        p_max: float
        """
        log = logging.getLogger('{0}.{1}'.format(__name__, RejectionSampling2D))

        if p_max is None:
            # Invert function in order to find the maximum via `minimize`.
            # noinspection PyTypeChecker
            result = minimize(
                lambda x: -1. * distribution(x),
                1.0,
                method='SLSQP',
                bounds=(x_min, x_max),
                options={'disp': True}
            )
            if not result.success:
                raise StopIteration('Function could not be minimized.')
            log.debug('Found maximum at x = %e' % result.x[0])
            p_max = distribution(result.x[0])

        self.dist = distribution
        self.x_min = x_min
        self.x_max = x_max
        self.p_max = p_max

    def create_samples(self, count):
        """
        Generate samples from the underlying distribution.

        Parameters
        ----------
        count : int
            Number of samples.

        Returns
        -------
        samples : list[tuple]
            Samples in the form (x, y).
        """
        x = np.random.uniform(self.x_min, self.x_max, count)
        repeat = np.argwhere((np.random.random(count) * self.p_max) >= self.dist(x)).ravel()
        while repeat.size > 0:
            x[repeat] = np.random.uniform(self.x_min, self.x_max, repeat.size)
            repeat = repeat[(np.random.random(repeat.size) * self.p_max) >= self.dist(x[repeat])]
        return x
