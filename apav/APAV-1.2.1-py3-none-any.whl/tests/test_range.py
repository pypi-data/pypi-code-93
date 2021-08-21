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
from periodictable import elements as el
from apav.core.isotopic import UnknownElement

import apav
from apav.utils.helpers import data_path
import apav.core.range as rng
from apav import Ion


class TestRange:
    @classmethod
    def setup_class(cls):
        cls.data = rng.Range("BCl3", (12, 13.5), vol=19, color=(0.25, 0.5, 0.75))

    def test_constructor(self):
        rng.Range("SiO2", (0, 1))
        rng.Range(apav.Ion("SiO2"), (0, 1))

        rng.Range("SiO2", (2, 100))
        rng.Range("SiO2", (2, 100), vol=2)
        rng.Range("SiO2", (2, 100), vol=0)
        rng.Range("SiO2", (2, 100), color=(1, 1, 1))

        with raises(ValueError):
            rng.Range("SiO2", (2, 1))
        with raises(ValueError):
            rng.Range("SiO2", (-2, -1))
        with raises(ValueError):
            rng.Range("SiO2", (-2, 0))
        with raises(ValueError):
            rng.Range("SiO2", (1, 2), color=(2, 0, 0))
        with raises(ValueError):
            rng.Range("SiO2", (1, 2), vol=-2)

        with raises(TypeError):
            rng.Range(12, (1, 2))

    def test_contains(self):
        assert 12 in self.data
        assert 12.5 in self.data

        assert 13.5 not in self.data
        assert 14 not in self.data
        assert 10 not in self.data

    def test_contains_mass(self):
        assert self.data.contains_mass(12)
        assert self.data.contains_mass(12.5)

        assert not self.data.contains_mass(13.5)
        assert not self.data.contains_mass(14)
        assert not self.data.contains_mass(10)

    def test_lower(self):
        self.data.upper = 14
        self.data.lower = 0
        self.data.lower = 12
        assert self.data.lower == 12
        self.data.lower = 13
        assert self.data.lower == 13

        with raises(ValueError):
            self.data.lower = 14
        with raises(ValueError):
            self.data.lower = 15

    def test_upper(self):
        self.data.lower = 12
        self.data.upper = 14

        assert self.data.upper == 14
        self.data.upper = 14.5
        assert self.data.upper == 14.5

        with raises(ValueError):
            self.data.upper = 2

    def test_color(self):
        self.data.color = (0, 0, 0)
        assert self.data.color == (0, 0, 0)
        self.data.color = (1, 1, 1)
        assert self.data.color == (1, 1, 1)
        self.data.color = "FFFFFF"

        with raises(ValueError):
            self.data.color = (2, 0, 0)
        with raises(Exception):
            self.data.color = "ASDFQW"

    def test_interval(self):
        self.data.lower = 12
        self.data.upper = 14
        assert self.data.interval == (12, 14)

    def test_vol(self):
        self.data.vol = 5
        assert self.data.vol == 5

        with raises(ValueError):
            self.data.vol = 0
        with raises(ValueError):
            self.data.vol = -2

    def test_num_elems(self):
        assert self.data.num_elems() == 2

    def test_composition(self):
        self.data.ion = "GdO2Cl10"
        self.data.ion = apav.Ion("GdO2Cl10")

        with raises(TypeError):
            self.data.ion = 12

    def test_intersects(self):
        rng_test = rng.Range("O", (3, 4))

        assert rng_test.intersects(rng.Range("O", (3.5, 5))) is True
        assert rng_test.intersects(rng.Range("O", (2.5, 3.5))) is True
        assert rng_test.intersects(rng.Range("O", (3, 4))) is True

        assert rng_test.intersects(rng.Range("O", (2, 3))) is False
        assert rng_test.intersects(rng.Range("O", (4, 5))) is False
        assert rng_test.intersects(rng.Range("O", (1, 2))) is False
        assert rng_test.intersects(rng.Range("O", (5, 6))) is False

    def test_reduced_formula(self):
        self.data.ion = "GdO2Cl10"
        assert self.data.ion.hill_formula == self.data.hill_formula


class TestRangeCollection:
    @classmethod
    def setup_class(cls):
        cls.ranges = [
            rng.Range("SiO2", (1, 2)),
            rng.Range("Cl", (13, 14.5)),
            rng.Range("A3W2", (20, 21))
        ]
        cls.data = rng.RangeCollection(cls.ranges)

    def test_constructor(self):
        rng.RangeCollection([rng.Range("SiO2", (1, 2)), rng.Range("SiO3", (12, 13))])
        rng.RangeCollection((rng.Range("SiO2", (1, 2)), rng.Range("SiO3", (12, 13))))
        rng.RangeCollection()

        with raises(TypeError):
            rng.RangeCollection(["GdO2"])

        assert self.data.filepath == ""

    def test_ranges(self):
        for i in self.ranges:
            assert i in self.data.ranges

    def test_iter(self):
        for i, item in enumerate(self.data):
            assert item.ion == self.ranges[i].ion
        for i, item in enumerate(self.data):
            assert item.ion == self.ranges[i].ion

    def test_len(self):
        assert len(self.data) == len(self.ranges)

    def test_from_rrng(self):
        rrng = rng.RangeCollection.from_rrng(data_path("Si.RRNG"))
        assert len(rrng) == 25
        assert rrng.ranges[0].ion == apav.Ion("Si")
        assert rrng.ranges[24].ion == apav.Ion("Cr2O")
        assert rrng.filepath == data_path("Si.RRNG")

    def test_load_rrng(self):
        path = data_path("Si.RRNG")
        apav.load_rrng(path)

    def test_add_range(self):
        temp = rng.RangeCollection()
        item = rng.Range("CeO2", (1, 2))
        temp.add(item)

        assert len(temp) == 1
        assert temp.ranges[0] == item

        temp.add(rng.Range("CeO2", (0, 1)))
        temp.add(rng.Range("CeO2", (2, 3)))
        temp.add(rng.Range("CeO2", (3, 4)))

        with raises(ValueError):
            temp.add(rng.Range("CeO2", (1.5, 2.5)))
        with raises(ValueError):
            temp.add(rng.Range("CeO2", (1, 2)))

        with raises(TypeError):
            temp.add("CeO2")

    def test_remove_by_mass(self):
        temp = rng.RangeCollection(self.ranges)

        temp.remove_by_mass(0)
        assert len(temp) == 3

        temp.remove_by_mass(1)
        assert self.ranges[0] not in temp

        temp.remove_by_mass(14)
        assert self.ranges[1] not in temp

        temp.remove_by_mass(20.5)
        assert self.ranges[2] not in temp

        assert len(temp) == 0

    def test_ions(self):
        assert all(Ion(i) in self.data.ions() for i in ("A3W2", "Cl", "SiO2"))

    def test_elements(self):
        assert all(i in self.data.elements() for i in (UnknownElement("A"), el.W, el.Cl, el.Si, el.O))

    def test_sorted_ranges(self):
        temp = rng.RangeCollection(self.ranges[::-1])
        assert temp.sorted_ranges() == self.ranges

    def test_find_by_mass(self):
        assert self.data.find_by_mass(1) == self.ranges[0]
        assert self.data.find_by_mass(1.5) == self.ranges[0]
        assert self.data.find_by_mass(14) == self.ranges[1]
        assert self.data.find_by_mass(20.5) == self.ranges[2]

        with raises(ValueError):
            self.data.find_by_mass(2)
        with raises(ValueError):
            self.data.find_by_mass(14.5)
        with raises(ValueError):
            self.data.find_by_mass(100)

