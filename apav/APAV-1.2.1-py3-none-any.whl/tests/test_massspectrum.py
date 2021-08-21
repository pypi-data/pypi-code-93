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


class TestRangedMassSpectrum:
    def test_upper(self, triples_roi, triples_range, si_range, si_roi):
        rms = ms.RangedMassSpectrum(triples_roi, triples_range, upper=6)
        assert rms.histogram[1].sum() == 11

        rms = ms.RangedMassSpectrum(triples_roi, triples_range, upper=100)
        assert rms.histogram[1].sum() == 13

        with raises(Exception):
            ms.RangedMassSpectrum(si_roi, si_range, upper=-2)
        with raises(Exception):
            ms.RangedMassSpectrum(si_roi, si_range, upper=0)

    def test_percent(self, triples_roi, triples_range):
        rms = ms.RangedMassSpectrum(triples_roi, triples_range, percent=False)
        assert rms.quant_dict["A"] == (2/11, 2)
        assert rms.quant_dict["A2"] == (4/11, 4)
        assert rms.quant_dict["B"] == (5/11, 5)
        assert rms.quant_dict["C"] == (0, 0)

        rms = ms.RangedMassSpectrum(triples_roi, triples_range, percent=True)
        assert rms.quant_dict["A"] == (100*2/11, 2)
        assert rms.quant_dict["A2"] == (100*4/11, 4)
        assert rms.quant_dict["B"] == (100*5/11, 5)
        assert rms.quant_dict["C"] == (100*0, 0)

        with raises(Exception):
            ms.RangedMassSpectrum(triples_roi, triples_range, percent=12)

    def test_decompose(self, triples_roi, triples_range):
        rms = ms.RangedMassSpectrum(triples_roi, triples_range, decompose=False)
        assert rms.quant_dict["A"] == (2/11, 2)
        assert rms.quant_dict["A2"] == (4/11, 4)
        assert rms.quant_dict["B"] == (5/11, 5)
        assert rms.quant_dict["C"] == (0, 0)

        rms = ms.RangedMassSpectrum(triples_roi, triples_range, decompose=True)
        assert rms.quant_dict["A"] == (10/15, 10)
        assert rms.quant_dict["B"] == (5/15, 5)
        assert rms.quant_dict["C"] == (0, 0)

    def test_print(self, triples_range, triples_roi):
        rms = ms.RangedMassSpectrum(triples_roi, triples_range)
        rms.print()

    def test_ranges(self, triples_roi, triples_range):
        ms.RangedMassSpectrum(triples_roi, triples_range)

        rms = ms.RangedMassSpectrum(triples_roi, ap.RangeCollection())
        assert sum(rms.quant_dict.values()) == 0

        with raises(Exception):
            ms.RangedMassSpectrum(triples_roi, 12)

    def test_bin_width(self, triples_roi, triples_range):
        rms = ms.RangedMassSpectrum(triples_roi, triples_range, bin_width=1)
        assert rms.bin_width == 1
        assert rms.histogram[0][1] - rms.histogram[0][0] == 1

        with raises(Exception):
            ms.RangedMassSpectrum(triples_roi, triples_range, bin_width=0)
        with raises(Exception):
            ms.RangedMassSpectrum(triples_roi, triples_range, bin_width=-2)
        with raises(Exception):
            ms.RangedMassSpectrum(triples_roi, triples_range, bin_width="3")

    def test_multiplicity(self, si_roi, si_range, triples_roi, triples_range):
        # Singles
        rms = ms.RangedMassSpectrum(triples_roi, triples_range, multiplicity=1)
        assert rms.quant_dict["A"] == (0, 0)
        assert rms.quant_dict["A2"] == (0, 0)
        assert rms.quant_dict["B"] == (1, 1)
        assert rms.quant_dict["C"] == (0, 0)

        # Doubles
        rms = ms.RangedMassSpectrum(triples_roi, triples_range, multiplicity=2)
        assert rms.quant_dict["A"] == (1/5, 1)
        assert rms.quant_dict["A2"] == (2/5, 2)
        assert rms.quant_dict["B"] == (2/5, 2)
        assert rms.quant_dict["C"] == (0, 0)

        # Triples
        rms = ms.RangedMassSpectrum(triples_roi, triples_range, multiplicity=3)
        assert rms.quant_dict["A"] == (1/5, 1)
        assert rms.quant_dict["A2"] == (2/5, 2)
        assert rms.quant_dict["B"] == (2/5, 2)
        assert rms.quant_dict["C"] == (0, 0)

        # Multiples
        rms = ms.RangedMassSpectrum(triples_roi, triples_range, multiplicity="multiples")
        assert rms.quant_dict["A"] == (2/10, 2)
        assert rms.quant_dict["A2"] == (4/10, 4)
        assert rms.quant_dict["B"] == (4/10, 4)
        assert rms.quant_dict["C"] == (0, 0)

        # All counts
        rms = ms.RangedMassSpectrum(triples_roi, triples_range, multiplicity="all")
        assert rms.quant_dict["A"] == (2/11, 2)
        assert rms.quant_dict["A2"] == (4/11, 4)
        assert rms.quant_dict["B"] == (5/11, 5)
        assert rms.quant_dict["C"] == (0, 0)

        # Real data
        for i in si_roi.multiplicities:
            ms.RangedMassSpectrum(si_roi, si_range, multiplicity=int(i))

        ms.RangedMassSpectrum(si_roi, si_range, multiplicity="all")
        ms.RangedMassSpectrum(si_roi, si_range, multiplicity="multiples")

    def test_counts_in_range(self, triples_roi, triples_range):
        rms = ms.RangedMassSpectrum(triples_roi, triples_range)
        assert rms.counts_in_range(triples_range.find_by_mass(1)) == 4
        assert rms.counts_in_range(triples_range.find_by_mass(4)) == 5
        assert rms.counts_in_range(triples_range.find_by_mass(7)) == 2
        assert rms.counts_in_range(triples_range.find_by_mass(40)) == 0

        with raises(Exception):
            rms.counts_in_range("12")

    def test_plot(self, si_ranged_ms_plot, qtbot):
        si_ranged_ms_plot.show()
        qtbot.addWidget(si_ranged_ms_plot)
        # qtbot.stopForInteraction()


class TestCorrelationHistogram:
    def test_constructor(self,
                         singles_roi,
                         doubles_roi,
                         triples_roi,
                         si_roi):
        # Synthetic roi with only singles
        singles = ms.CorrelationHistogram(singles_roi)
        assert n.sum(singles.histogram) == 0

        # Synthetic roi with only doubles
        doubles = ms.CorrelationHistogram(doubles_roi)

        # Synthetic roi with only triples
        triples = ms.CorrelationHistogram(triples_roi)

        # Real data
        ms.CorrelationHistogram(si_roi)

    def test_bin_width(self, triples_roi):
        corr = ms.CorrelationHistogram(triples_roi, bin_width=0.1)
        assert corr.bin_width == 0.1

        with raises(Exception):
            ms.CorrelationHistogram(triples_roi, bin_width=0)
        with raises(Exception):
            ms.CorrelationHistogram(triples_roi, bin_width=-1)

    def test_extents(self, triples_roi):
        corr = ms.CorrelationHistogram(triples_roi, extents=((3, 6), (3, 13)))
        assert corr.histogram.sum() == 2
        assert corr.extents == ((3, 6), (3, 13))

        corr = ms.CorrelationHistogram(triples_roi, extents=((3, 5.6), (3, 13)))
        assert corr.histogram.sum() == 1

        corr = ms.CorrelationHistogram(triples_roi, extents=((40, 50), (100, 120)))
        assert corr.histogram.sum() == 0

        with raises(Exception):
            ms.CorrelationHistogram(triples_roi, extents=((6, 5), (3, 13)))
        with raises(Exception):
            ms.CorrelationHistogram(triples_roi, extents=((5, 6), (-3, 13)))

    def test_multiplicity(self, singles_roi, doubles_roi, triples_roi, si_roi):
        # Singles not allowed
        with raises(Exception):
            ms.CorrelationHistogram(singles_roi, multiplicity=1)

        # Doubles
        corr = ms.CorrelationHistogram(singles_roi, multiplicity=2)
        assert corr.histogram.sum() == 0
        assert corr.multiplicity == 2

        corr = ms.CorrelationHistogram(doubles_roi, multiplicity=2)
        assert corr.histogram.sum() == 3

        corr = ms.CorrelationHistogram(triples_roi, multiplicity=2)
        assert corr.histogram.sum() == 3

        corr = ms.CorrelationHistogram(si_roi, multiplicity=2)

        # Triples
        corr = ms.CorrelationHistogram(singles_roi, multiplicity=3)
        assert corr.histogram.sum() == 0

        corr = ms.CorrelationHistogram(doubles_roi, multiplicity=3)
        assert corr.histogram.sum() == 0

        corr = ms.CorrelationHistogram(triples_roi, multiplicity=3)
        assert corr.histogram.sum() == 6

        corr = ms.CorrelationHistogram(si_roi, multiplicity=3)

        # All multiples
        corr = ms.CorrelationHistogram(singles_roi, multiplicity="multiples")
        assert corr.histogram.sum() == 0

        corr = ms.CorrelationHistogram(doubles_roi, multiplicity="multiples")
        assert corr.histogram.sum() == 3

        corr = ms.CorrelationHistogram(triples_roi, multiplicity="multiples")
        assert corr.histogram.sum() == 9

        # Test some real data
        corr = ms.CorrelationHistogram(si_roi, multiplicity="multiples")

    def test_symmetric(self, triples_roi):
        corr = ms.CorrelationHistogram(triples_roi, symmetric=False)
        assert corr.symmetric is False

        corr_sym = ms.CorrelationHistogram(triples_roi, symmetric=True)
        assert corr_sym.symmetric is True

        assert n.allclose(corr.histogram + corr.histogram.T, corr_sym.histogram)

    def test_flip(self, triples_roi):
        corr = ms.CorrelationHistogram(triples_roi, flip=False)
        assert corr.flip is False

        corr_flip = ms.CorrelationHistogram(triples_roi, flip=True)
        assert corr_flip.flip is True

        assert n.allclose(corr.histogram.T, corr_flip.histogram)

    def test_plot(self, si_roi, qtbot):
        corr1 = ms.CorrelationHistogram(si_roi)
        plot1 = corr1.plot()
        plot1.show()
        qtbot.addWidget(plot1)

        corr2 = ms.CorrelationHistogram(si_roi)
        plot2 = corr2.plot()
        plot2.show()
        qtbot.addWidget(plot2)







