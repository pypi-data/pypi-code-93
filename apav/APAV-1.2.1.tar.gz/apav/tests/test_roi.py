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

from apav import Roi, RangeCollection
from apav.utils.helpers import data_path
from apav.utils import validate
import apav as ap

import numpy as n
from pytest import raises


class TestRoi:
    def test_constructor(self):
        xyz = n.array([[0,   0,  0],
                           [1,   1,  1],
                           [-1,  1,  1],
                           [1,  -1,  1],
                           [1,   1, -1],
                           [-1, -1,  1],
                           [-1,  1, -1],
                           [1,  -1, -1],
                           [-1, -1, -1]])

        mass = n.array([1, 2, 2, 3, 3, 3, 5, 5, 4])
        ipp = n.array([1, 2, 0, 4, 0, 0, 0, 2, 0])
        det_x = n.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        det_y = n.array([10, 20, 30, 40, 50, 60, 70, 80, 90])
        tof = n.array([1.5, 1.5, 2.5, 5.5, 2.5, 3.5, 3.5, 3.5, 3.5])
        roi = Roi(xyz,
                  mass,
                  misc={"ipp": ipp, "det_x": det_x, "det_y": det_y, "tof": tof})

    with raises(TypeError):
        Roi((1, 0, 0), n.array([1]))
    with raises(TypeError):
        Roi(n.array([[1, 0, 0]]), [1])
    with raises(ValueError):
        Roi(n.array([[1, 0, 0], [0, 2, 0]]), n.array([1]))
    with raises(ValueError):
        Roi(n.array([[1, 0, 0], [0, 2, 0]]), n.array([[1, 2]]))
    with raises(ValueError):
        Roi(n.array([[[1, 0, 0], [0, 2, 0]]]), n.array([[1, 2]]))

    def test_xyz(self, triples_roi):
        xyz = n.array([[1, 0, 0],
                   [1, 1, 0],
                   [4, 2, 1],
                   [4, 7, 1],
                   [8, 2, 4],
                   [4, 7, 9],
                   [4, 2, 1],
                   [8, 2, 4],
                   [4, 7, 1],
                   [8, 2, 4],
                   [1, 1, 0],
                   [4, 2, 1],
                   [9, 4, 3]])
        assert n.allclose(triples_roi.xyz, xyz)

    def test_mass(self, triples_roi):
        mass = n.array([1, 1.1, 3, 1, 2, 3, 5.6, 12, 3.4, 3.5, 4, 5, 6])
        assert n.allclose(triples_roi.mass, mass)

    def test_misc(self, triples_roi):
        ipp = n.array([2, 0, 1, 3, 0, 0, 2, 0, 2, 0, 3, 0, 0])
        assert n.allclose(triples_roi.misc["ipp"], ipp)

    def test_nhits(self, triples_roi):
        assert triples_roi.counts == 13

    def test_dimensions(self, triples_roi):
        assert n.allclose(triples_roi.dimensions, (8, 7, 9))

    def test_mass_extents(self, triples_roi):
        assert n.allclose(triples_roi.mass_extents, (1, 12))

    def test_xyz_extents(self, triples_roi):
        assert n.allclose(triples_roi.xyz_extents, ((1, 9), (0, 7), (0, 9)))

    def test_detector_extents(self, triples_roi):
        assert n.allclose(triples_roi.detector_extents, ((1, 13), (10, 130)))

    def test_multiplicity_info(self, triples_roi, singles_roi):
        assert triples_roi.has_multiplicity_info() is True
        assert Roi(n.array([[0, 0, 0]]), n.array([7])).has_multiplicity_info() is False

    def test_tof_info(self, triples_roi, singles_roi):
        assert triples_roi.has_tof_info() is True
        assert singles_roi.has_tof_info() is False

    def test_multiplicities(self, singles_roi, triples_roi):
        assert n.allclose(triples_roi.multiplicities, [1, 2, 3])
        assert n.allclose(singles_roi.multiplicities, [1])

        with raises(validate.NoMultiEventError):
            roi = Roi(n.array([[0, 0, 0]]), n.array([2]))
            m = roi.multiplicities

    def test_xyz_center(self, singles_roi):
        cen = singles_roi.xyz_center
        assert n.isclose(cen[0], 4.42857)
        assert n.isclose(cen[1], 3.285714)
        assert n.isclose(cen[2], 2.57142)

    def test_from_pos(self):
        fpos = data_path("Si.pos")
        posrun = Roi.from_pos(fpos)
        assert not posrun.has_multiplicity_info()
        assert not posrun.has_detailed_info()
        assert not posrun.has_tof_info()

        with raises(validate.NoMultiEventError):
            posrun.multiplicity_counts()
        with raises(validate.NoMultiEventError):
            posrun.multiplicity_fraction()
        with raises(validate.NoMultiEventError):
            posrun.multiplicity_percentage()

        with raises(validate.NoDetectorInfoError):
            posrun.detector_extents()

        with raises(validate.NoTOFError):
            posrun.tof_histogram()

    def test_load_pos(self):
        fpos = data_path("Si.pos")
        ap.load_pos(fpos)

    def test_load_epos(self):
        fepos = data_path("Si.epos")
        ap.load_epos(fepos)

    # def test_load_ato(self):
    #     fato = data_path("Si.ato")
    #     ap.load_ato(fato)

    def test_load_apt(self):
        fapt = data_path("Si.apt")
        ap.load_apt(fapt)

    def test_from_epos(self):
        fepos = data_path("Si.epos")
        eposrun = Roi.from_epos(fepos)
        assert eposrun.has_multiplicity_info()
        assert eposrun.has_detailed_info()
        assert eposrun.has_tof_info()

        eposrun.multiplicity_counts()
        eposrun.multiplicity_percentage()
        eposrun.multiplicity_fraction()

    def test_from_apt(self, si_roi):
        path = data_path("Si.apt")
        apt_roi = Roi.from_apt(path, verbose=True)

        assert n.allclose(si_roi.mass, apt_roi.mass)
        assert n.allclose(si_roi.xyz, apt_roi.xyz)
        assert n.allclose(si_roi.misc["ipp"], apt_roi.misc["ipp"])
        assert n.allclose(si_roi.misc["det_x"], apt_roi.misc["det_x"])
        assert n.allclose(si_roi.misc["det_y"], apt_roi.misc["det_y"])

    def test_multiplicity_counts(self, triples_roi):
        assert n.allclose(triples_roi.multiplicity_counts(),
                          (n.array([1, 2, 3]), n.array([1, 6, 6])))

    def test_multiplicity_fraction(self, triples_roi):
        counts = triples_roi.counts
        assert n.allclose(triples_roi.multiplicity_fraction(),
                          (n.array([1, 2, 3]), n.array([1/counts, 6/counts, 6/counts])))

    def test_multiplicity_percentage(self, triples_roi):
        counts = triples_roi.counts
        assert n.allclose(triples_roi.multiplicity_percentage(),
                          (n.array([1, 2, 3]), n.array([100*1/counts, 100*6/counts, 100*6/counts])))

    def test_tof_histogram(self, triples_roi):
        hist = triples_roi.tof_histogram(10, "all", norm=False, cutoff=100)
        assert n.allclose(hist[1], n.array([2, 2, 2, 2, 0, 1, 0, 1, 1, 0]))

        hist = triples_roi.tof_histogram(10, "multiples", norm=False, cutoff=100)
        assert n.allclose(hist[1], n.array([2, 2, 2, 2, 0, 1, 0, 1, 1, 0]))

        hist = triples_roi.tof_histogram(10, 2, norm=False, cutoff=100)
        assert n.allclose(hist[1], n.array([1, 1, 2, 0, 0, 1, 0, 0, 0, 0]))

        hist = triples_roi.tof_histogram(10, 2, norm=True, cutoff=100)
        assert n.allclose(hist[1], n.array([1, 1, 2, 0, 0, 1, 0, 0, 0, 0])/2)

    def test_mass_histogram(self, triples_roi):
        hist = triples_roi.mass_histogram(2, 1, 7, multiplicity="all", norm=False)
        assert n.allclose(hist[1], n.array([4, 5, 3]))

        hist = triples_roi.mass_histogram(2, 1, 7, multiplicity="multiples", norm=False)
        assert n.allclose(hist[1], n.array([4, 4, 3]))

        hist = triples_roi.mass_histogram(2, 1, 7, multiplicity=2, norm=False)
        assert n.allclose(hist[1], n.array([2, 2, 1]))

        hist = triples_roi.mass_histogram(2, 1, 7, multiplicity=2, norm=True)
        assert n.allclose(hist[1], n.array([2, 2, 1])/2)

    def test_plotting(self, triples_roi, qtbot):
        # very basic plot testing
        plot = triples_roi.plot_mass_spectrum()
        plot.show()
        qtbot.addWidget(plot)

        # bin
        plot.bin_width.setValue(0)
        plot.bin_width.editingFinished.emit()
        assert plot.bin_width.value() != 0

        # min
        plot.lower.setValue(2.5)
        plot.lower.editingFinished.emit()

        # max
        plot.upper.setValue(3.5)
        plot.upper.editingFinished.emit()

        # norm
        plot.lower.setValue(0)
        plot.upper.setValue(200)
        plot.upper.editingFinished.emit()
