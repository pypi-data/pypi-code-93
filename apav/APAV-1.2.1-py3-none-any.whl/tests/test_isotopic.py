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

from apav import Isotope, IsotopeSeries, Ion
from apav.core.isotopic import str2composition, Ion, UnknownElement
from periodictable import elements as el
# import apav

from pytest import raises, fixture
import numpy as n


@fixture()
def O_isotope_series():
    ion = Ion("O", 1)
    isos = [
        Isotope(ion, 16, 15.995, 0.99757),
        Isotope(ion, 17, 16.999, 0.00038),
        Isotope(ion, 18, 17.999, 0.00205),
    ]
    return IsotopeSeries(ion, isos)


def test_str2composition():
    assert str2composition("Ba") == {el.Ba: 1}
    assert str2composition("BaCl1") == {el.Ba: 1, el.Cl: 1}
    assert str2composition("BaCl2") == {el.Ba: 1, el.Cl: 2}
    assert str2composition("Ba2ClCB34") == {el.Ba: 2, el.Cl: 1, el.C: 1, el.B: 34}
    assert str2composition("BaBa") == {el.Ba: 2}
    comp = str2composition("Gd7IGd2ReO")
    assert comp == {el.Gd: 9, el.I: 1, el.Re: 1, el.O: 1}
    assert len(comp.keys()) == 4

    with raises(ValueError):
        str2composition("2Ba3")
    with raises(ValueError):
        str2composition("")
    with raises(TypeError):
        str2composition(12)
    with raises(ValueError):
        str2composition("Ba1.2")
    with raises(ValueError):
        str2composition("ba2")
    with raises(ValueError):
        str2composition("u")
    with raises(ValueError):
        str2composition("(CuO)2")
    with raises(ValueError):
        str2composition("Ba0")
    with raises(ValueError):
        str2composition("Ba-1")

class TestUnknownElement:
    def test_name(self):
        elem = UnknownElement("At")
        assert elem.name == "At"

    def test_symbol(self):
        elem = UnknownElement("At")
        assert elem.symbol == "At"

    def test_mass(self):
        elem = UnknownElement("At")
        assert elem.mass == 0

    def test_number(self):
        elem = UnknownElement("At")
        assert elem.number == 0

    def test_isotopes(self):
        elem = UnknownElement("At")
        with raises(ValueError):
            print(elem.isotopes)

    def test_add_isotopes(self):
        elem = UnknownElement("At")
        with raises(ValueError):
            elem.add_isotope(3)

    def test_eq_(self):
        elem1 = UnknownElement("At")
        elem2 = UnknownElement("At")
        elem3 = UnknownElement("Bx")

        assert elem1 == elem2
        assert elem1 != elem3

    def test_repr_(self):
        elem = UnknownElement("Bc").__repr__()


class TestIon:
    def test_formula(self):
        ion = Ion("BaO")
        assert ion.formula == "BaO"

        ion = Ion("Ba2ClICO3")
        assert ion.formula == "Ba2ClICO3"

        # Placeholder element
        ion = Ion("Cu2A10")
        assert ion.formula == "Cu2A10"

        with raises(Exception):
            Ion(13)
        with raises(ValueError):
            Ion("CuO2I0")

    def test_charge(self):
        ion = Ion("Ba", 2)
        assert ion.charge == 2

        ion = Ion("Ba", -2)
        assert ion.charge == -2

        with raises(Exception):
            Ion("Ba", "g")

    def test_elements(self):
        ion = Ion("GdO2Gd3")
        assert el.Gd in ion.elements
        assert el.O in ion.elements
        assert len(ion.elements) == 2

    def test_comp_dict(self):
        ion = Ion("Ba2ClIC")
        assert ion.comp_dict == {el.Ba: 2, el.Cl: 1, el.I: 1, el.C: 1}

    def test_comp_str_dict(self):
        ion = Ion("Ba2ClIC")
        assert ion.comp_str_dict == {"Ba": 2, "Cl": 1, "I": 1, "C": 1}

    def test_number(self):
        ion = Ion("Ba2ClIC")
        assert ion.number == el.Ba.number*2 + el.Cl.number + el.I.number + el.C.number

    def test_mass(self):
        ion = Ion("Ba2ClIC")
        assert ion.mass == el.Ba.mass*2 + el.Cl.mass + el.I.mass + el.C.mass

    def test_num_atoms(self):
        assert Ion("Gd").num_atoms == 1
        assert Ion("Gd2C3Gd1").num_atoms == 6

    def test_items(self):
        ion = Ion("H3CCu2")
        assert ion.items() == ion.comp_dict.items()

    def test_hill_formula(self):
        ion = Ion("Gd")
        assert ion.hill_formula == "Gd"

        ion = Ion("GdO")
        assert ion.hill_formula == "GdO"

        ion = Ion("OGd")
        assert ion.hill_formula == "GdO"

        ion = Ion("H3C")
        assert ion.hill_formula == "CH3"

        ion = Ion("Y2C6H2C12Og")
        assert ion.hill_formula == "C18H2OgY2"

    def test_equal(self):
        ion1 = Ion("BaO2", 2)
        ion2 = Ion("BaO2", 2)
        ion3 = Ion("CuO2", 2)
        assert ion1 == ion2
        assert ion1 != ion3
        assert ion1 != 4

    def test_str_(self):
        ion = Ion("BaO2")
        str(ion)


class TestIsotope:
    def test_constructor(self):
        Isotope(Ion("Cl"), 1, 1, 1)
        Isotope(Ion("BCl3"), 1, 1, 1)

        Isotope(Ion("BCl3", 3), 1, 1, 1)
        Isotope(Ion("BCl3", 0), 1, 1, 1)
        Isotope(Ion("BCl3", -3), 1, 1, 1)

    with raises(ValueError):
        Isotope(Ion("BCl3", 3), 0, 1, 1)
    with raises(ValueError):
        Isotope(Ion("BCl3", 3), 1, 0, 1)
    with raises(ValueError):
        Isotope(Ion("BCl3", 3), 1, 1, 0)
    with raises(TypeError):
        Isotope(Ion((2), 3), 1, 1, 0)

    def test_eq(self):
        ion1 = Isotope(Ion("BCl"), 1, 2, 1)
        ion2 = Isotope(Ion("BCl"), 1, 2, 1)
        ion3 = Isotope(Ion("BCl2"), 1, 2, 1)
        assert ion1 == ion2
        assert ion1 != ion3

    def test_repr(self):
        print(Isotope(Ion("BCl3", 0), 1, 1, 1))

    def test_ion(self):
        iso = Isotope(Ion("BCl3", 3), 1, 2, 0.5)
        assert iso.ion == Ion("BCl3", 3)

    def test_number(self):
        iso = Isotope(Ion("BCl3", 3), 1, 2, 0.5)
        assert iso.number == 1

    def test_mass(self):
        iso = Isotope(Ion("BCl3", 3), 1, 2, 0.5)
        assert iso.mass == 2

    def test_abundance(self):
        iso = Isotope(Ion("BCl3", 3), 1, 2, 0.5)
        assert iso.abundance == 0.5

    def test_all_real_elements(self):
        ion = Ion("Cu2O")
        assert ion.all_real_elements() == True

        ion = Ion("BaTy6")
        assert ion.all_real_elements() == False

        ion = Ion("BaT6")
        assert ion.all_real_elements() == False


class TestIsotopeSeries:
    @classmethod
    def setup_class(cls):
        cls.o_ion = Ion("O", 1)
        cls.o_isos = [
            Isotope(cls.o_ion, 16, 15.995, 0.99757),
            Isotope(cls.o_ion, 17, 16.999, 0.00038),
            Isotope(cls.o_ion, 18, 17.999, 0.00205),
        ]
        cls.o_iso_series = IsotopeSeries(cls.o_ion,
                                         isotopes=cls.o_isos,
                                         threshold=0)



    def test_constructor(self):
        a = IsotopeSeries(Ion("Cu2O", 2))
        b = IsotopeSeries("Cu2O", 2)

        assert a.ion == b.ion
        assert a.charge == b.charge
        assert a.isotopes == b.isotopes
        with raises(ValueError):
            IsotopeSeries(["Cu"])
        with raises(ValueError):
            IsotopeSeries(["Cu"], "^")

    def test_explicit_isotopes(self):
        ion = Ion("O", 1)
        isos = [
            Isotope(ion, 16, 15.995, 0.99757),
            Isotope(ion, 17, 16.999, 0.00038),
            Isotope(ion, 18, 17.999, 0.00205),
        ]

        IsotopeSeries(ion, isotopes=isos)

        IsotopeSeries(ion, isotopes=[Isotope(Ion("O", 1), 1, 1, 0.5)])

        with raises(ValueError):
            IsotopeSeries(Ion("O", 0), isotopes=isos)
        with raises(ValueError):
            IsotopeSeries(Ion("O", 1), isotopes=isos+[Isotope(Ion("H", 1), 1, 1, 1)])
        with raises(ValueError):
            IsotopeSeries(Ion("O", 1), isotopes=isos+[isos[1]])
        with raises(ValueError):
            isos2 = [
                Isotope(ion, 16, 15.995, 0.99757),
                Isotope(ion, 17, 16.999, 0.00038),
                Isotope(ion, 18, 17.999, 1.00205),
            ]

            IsotopeSeries(ion, isotopes=isos2)
        with raises(ValueError):
            isos2 = [
                Isotope(ion, 16, 15.995, 0.99757),
                Isotope(ion, 17, 16.999, 0.00038),
                Isotope(Ion("O", 2), 18, 17.999, 0.00205),
            ]

            IsotopeSeries(ion, isotopes=isos2)

    def test_molecular_isotopes(self):
        ion1 = Ion("BCl3", 1)
        isos1 = IsotopeSeries(ion1, threshold=0)
        assert len(isos1) == 8
        assert n.isclose(isos1[0].abundance, 0.0865998)
        assert n.isclose(isos1[0].mass, 114.919)
        assert n.isclose(isos1[-1].abundance, 0.0113803)
        assert n.isclose(isos1[-1].mass, 121.907)
        assert isos1._is_unity()

        with raises(ValueError):
            IsotopeSeries(Ion("BCl3", 0))

        ion2 = Ion("GdCuO2", 1)
        isos2 = IsotopeSeries(ion2, threshold=0)
        assert isos2._is_unity()
        isos2_filt = IsotopeSeries(ion2, threshold=0.01)
        assert len(isos2_filt) == 11
        assert n.isclose(isos2_filt[0].abundance, 0.0150059)
        assert n.isclose(isos2_filt[0].mass, 248.84)
        assert n.isclose(isos2_filt[-1].abundance, 0.0670672)
        assert n.isclose(isos2_filt[-1].mass, 256.845)

        isos2_filt2 = IsotopeSeries(ion2, threshold=0.01)
        assert len(isos2_filt2) == 11

        ion3 = Ion("O2", 1)
        isos3 = IsotopeSeries(ion3, threshold=0)
        assert isos3._is_unity()
        assert len(isos3) == 6
        assert isos3[0].charge == 1
        assert n.isclose(isos3[0].abundance, 0.995146)
        assert n.isclose(isos3[0].mass, 31.9898)
        assert isos3[0].number == 32

        assert isos3[-1].charge == 1
        assert n.isclose(isos3[-1].abundance, 0.0000042025)
        assert n.isclose(isos3[-1].mass, 35.9983)
        assert isos3[-1].number == 36

        ion4 = Ion("O2", 2)
        isos4 = IsotopeSeries(ion4, threshold=0)
        assert isos4._is_unity()
        assert len(isos4) == 6
        assert isos4[0].charge == 2
        assert n.isclose(isos4[0].abundance, 0.995146)
        assert n.isclose(isos4[0].mass, 31.9898/2)
        assert isos4[0].number == 32

    def test_threshold(self):
        ion = Ion("BCl3", 1)
        isos = IsotopeSeries(ion,
                             isotopes=[Isotope(ion, 1, 1, 0.75), Isotope(ion, 1, 2, 0.125), Isotope(ion, 1, 1.5, 0.125)],
                             threshold=0)
        isos_filt = IsotopeSeries(ion,
                                  isotopes=[Isotope(ion, 1, 1, 0.75), Isotope(ion, 1, 2, 0.125), Isotope(ion, 1, 1.5, 0.125)],
                                  threshold=0.5)
        assert len(isos_filt) == 1
        assert isos_filt[0] == Isotope(ion, 1, 1, 0.75)

    def test_iter(self):
        for iso1, iso2 in zip(self.o_isos, self.o_iso_series):
            assert iso1 == iso2

    def test_getitem(self):
        for i in range(len(self.o_iso_series)):
            assert self.o_isos[i] == self.o_iso_series[i]

        with raises(IndexError):
            self.o_iso_series[12]

    def test_len(self):
        assert len(self.o_iso_series) == 3

    def test_elemental_isotopes(self):
        for ind, i in enumerate(self.o_iso_series):
            assert i.ion == self.o_ion
            assert n.isclose(i.number, self.o_isos[ind].number)
            assert n.isclose(i.mass, self.o_isos[ind].mass)
            assert n.isclose(i.abundance, self.o_isos[ind].abundance)

    def test_repr(self):
        ion = Ion("BCl3", 2)
        isos = IsotopeSeries(ion)
        print(isos)
        filt = IsotopeSeries(ion, threshold=0.05)
        print(filt)

    def test_abundances(self):
        assert n.allclose(self.o_iso_series.abundances, [i.abundance for i in self.o_isos])




