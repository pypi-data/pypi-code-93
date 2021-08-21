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

from pytest import raises
import numpy as n

import apav.analysis.massspectrum as ms
import apav as ap
from apav.analysis.spatial import RangedGrid, DensityHistogram
# import matplotlib.pyplot as plt
import pyqtgraph as pg


class TestRangedGrid:

    def test(self):
        xyz = n.random.randn(1000000, 3)*5
        mass = n.ones(1000000)
        mass[:500000] = 32
        mass[500000:] = 63

        rc = ap.RangeCollection()
        rc.add(ap.Range(ap.Ion("O2"), (31, 33)))
        rc.add(ap.Range(ap.Ion("Cu"), (62, 64)))

        roi = ap.Roi(xyz, mass)

        grid = RangedGrid(roi, rc, delocalization=(3, 3, 1.5), bin_width=1)
        o = grid.ion_grids[ap.Ion("O2")]
        half = o.shape[-1]//2
        # oproc = o.sum(axis=-1)
        # nonzero = n.argwhere(grid.composition_counts > 0.1)
        # filt = n.argwhere(grid.composition_counts > 1)
        # plt.imshow(o[:, :, half])
        # plt.show()
        # x = pg.image(grid.composition_grid("O")[:, :, half])
        # plt.show()
        #
        # dens = DensityHistogram(roi, bin_width=0.5)
        # print("Sum: ", dens.histogram.sum())
        # plt.imshow(dens.histogram)
        # plt.show()

