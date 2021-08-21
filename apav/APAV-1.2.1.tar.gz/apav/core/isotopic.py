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

import periodictable as pt
from periodictable import elements as el
from periodictable.core import Element
import tabulate as tab
import numpy as n

from itertools import product
from operator import attrgetter
import math
from collections import defaultdict
import re
from copy import deepcopy

from apav.utils.hinting import *
from apav.utils import validate


_syms = ['Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'B', 'Ba', 'Be', 'Bh', 'Bi', 'Bk', 'Br', 'C', 'Ca', 'Cd', 'Ce',
         'Cf', 'Cl', 'Cm',
         'Cn', 'Co', 'Cr', 'Cs', 'Cu', 'Db', 'Ds', 'Dy', 'Er', 'Es', 'Eu', 'F', 'Fe', 'Fl', 'Fm', 'Fr', 'Ga', 'Gd',
         'Ge', 'H', 'He', 'Hf', 'Hg', 'Ho',
         'Hs', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lr', 'Lu', 'Lv', 'Mc', 'Md', 'Mg', 'Mn', 'Mo', 'Mt', 'N', 'Na',
         'Nb', 'Nd', 'Ne',
         'Nh', 'Ni', 'No', 'Np', 'O', 'Og', 'Os', 'P', 'Pa', 'Pb', 'Pd', 'Pm', 'Po', 'Pr', 'Pt', 'Pu', 'Ra', 'Rb', 'Re',
         'Rf', 'Rg', 'Rh',
         'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Se', 'Sg', 'Si', 'Sm', 'Sn', 'Sr', 'Ta', 'Tb', 'Tc', 'Te', 'Th', 'Ti', 'Tl',
         'Tm', 'Ts', 'U', 'V',
         'W', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']

_comp_re = re.compile(r"([A-Z][a-z]?)([0-9]*)")


class UnknownElement:
    def __init__(self, symbol):
        self._symbol = symbol

    def __repr__(self):
        return self.symbol

    def __eq__(self, other):
        if not isinstance(other, (UnknownElement, Element)):
            return NotImplemented
        elif other.symbol == self.symbol:
            return True
        else:
            return False

    def __hash__(self):
        return hash((self.symbol))

    @property
    def name(self):
        return self._symbol

    @property
    def symbol(self):
        return self._symbol

    @property
    def mass(self):
        return 0

    @property
    def number(self):
        return 0

    @property
    def isotopes(self):
        raise ValueError(f"Placeholder element {self.symbol} does not have isotopes")

    def add_isotope(self, number):
        raise ValueError(f"Placeholder element {self.symbol} does not have isotopes")


def str2composition(formula: str) -> Dict[Element, int]:
    """
    Convert a chemical formula string to a dict
    :param formula: the chemical string
    """
    if not isinstance(formula, str):
        raise TypeError(f"Chemical formula must be string not {type(formula)}")
    if not formula:
        raise ValueError("Formula cannot be null")

    matches = re.findall(_comp_re, formula)
    if len(matches) == 0:
        raise ValueError("Formula cannot be null")

    all_matches = "".join([i[0]+i[1] for i in matches])

    # If the original formula is not the same length as the regex matches then the formula is invalid
    if len(all_matches) != len(formula):
        raise ValueError(f"Unable to interpret chemical formula string: {formula}")

    comp = defaultdict(lambda: 0)

    # Convert the matches to a dict
    for elem, count in matches:
        if elem in _syms:
            element = el.symbol(elem)
        else:
            element = UnknownElement(elem)

        if count:
            if count == "0":
                raise ValueError(f"Element {elem} cannot have 0 atoms")
            num = int(count)
            comp[element] += num
        else:
            comp[element] += 1

    return dict(comp)


class Ion:
    def __init__(self, formula: str, charge: int = 0):
        self._charge = int(charge)
        self._comp_dict = str2composition(formula)
        self._formula = formula

    def __eq__(self, other):
        if not isinstance(other, Ion):
            return NotImplemented
        if self.comp_dict != other.comp_dict:
            return False
        elif self.charge != other.charge:
            return False
        else:
            return True

    def __str__(self):
        return self.formula + " " + str(self.charge) + "+"

    def __hash__(self):
        return hash((self.hill_formula, self.charge))

    def items(self):
        return self.comp_dict.items()

    @property
    def formula(self) -> str:
        """
        Get the ion's formula
        """
        return self._formula

    @property
    def charge(self) -> int:
        """
        Get the ion charge
        """
        return self._charge

    @property
    def comp_str_dict(self) -> Dict[str, int]:
        """
        Get the composition as a dictionary of (element str: num) key/value pairs
        """
        retn = {}
        for elem, num in self.comp_dict.items():
            retn[elem.symbol] = num

        return retn

    @property
    def comp_dict(self) -> Dict[Element, int]:
        """
        Get the composition as a dictionary of (element: num) key/value pairs
        """
        return deepcopy(self._comp_dict)

    @property
    def elements(self) -> List[Element]:
        """
        Get a list of all unique elements in the ion
        """
        return [i for i in self.comp_dict.keys()]

    @property
    def number(self) -> Real:
        """
        Get the cumulative atomic number of the ion
        """
        retn = 0
        for elem, count in self._comp_dict.items():
            retn += elem.number*count

        return retn

    @property
    def mass(self) -> Real:
        """
        Get the cumulative atomic mass of the ion
        """
        retn = 0
        for elem, count in self._comp_dict.items():
            retn += elem.mass*count

        return retn

    @property
    def num_atoms(self) -> int:
        """
        Get the total number of atoms in the ion
        """
        return sum(i for i in self.comp_dict.values())

    @property
    def hill_formula(self) -> str:
        """
        Get the formula as a hill formula
        """
        comp = self.comp_dict
        carbon = ""
        hydrogen = ""
        if el.C in comp.keys():
            count = comp.pop(el.C)
            carbon = "C" + str(count) if count > 1 else "C"
        if el.H in comp.keys():
            count = comp.pop(el.H)
            hydrogen = "H" + str(count) if count > 1 else "H"

        rest = [(elem.symbol, count) for elem, count in comp.items()]
        rest.sort(key=lambda x: x[0])
        retn = carbon + hydrogen
        for elem_str, count in rest:
            retn += elem_str + str(count) if count > 1 else elem_str

        return retn

    def all_real_elements(self) -> bool:
        """
        Determine if any elements in the composition are not real (place holder or unknown elements)
        """
        return all(not isinstance(i, UnknownElement) for i in self.elements)


class Isotope:
    """
    A single isotope
    """
    def __init__(self,
                 ion: Ion,
                 number: int,
                 mass: float,
                 abundance: float):
        """
        This class defines a single isotopic species, defined by composition, charge, mass, and absolute abundance.
        These values must be provided manually, see `IsotopeSeries` for calculating isotope distributions (which uses
        this class in its calculations). This class may be used for defining custom/modified isotopes for
        `IsotopeSeries`.

        >>> carbon_12 = Isotope(Ion("C", 1), 12, 6, 98.93)

        :param ion: Ion composition
        :param number: atomic number
        :param mass: atomic mass
        :param abundance: absolute isotopic abundance
        """
        if not isinstance(ion, Ion):
            raise validate.IonTypeError(ion)
        self._ion = ion
        self._number = validate.positive_nonzero_int(number)
        self._mass = validate.positive_nonzero_number(mass)
        self._abundance = validate.number_in_interval(abundance, 0, 1, lower_open=True, upper_open=False)

    def __repr__(self):
        return f"Isotope: {self.ion.hill_formula} +{self.charge} {self.number} @ {n.round(self.mass, 3)} Da {n.round(self.abundance*100, 2)} %"

    def __eq__(self, other):
        if self.ion == other.ion and \
                self.number == other.number and \
                self.mass == other.mass and \
                self.abundance == other.abundance:
            return True
        else:
            return False

    @property
    def ion(self) -> Ion:
        """
        Get the :class:`Ion` (Composition and charge)
        """
        return self._ion

    @property
    def number(self) -> int:
        """
        Get the atomic number of the isotope
        """
        return self._number

    @property
    def mass(self) -> float:
        """
        Get the atomic mass of the isotope
        """
        return self._mass

    @property
    def abundance(self) -> float:
        """
        Get the absolute abundance of the isotope
        """
        return self._abundance

    @property
    def charge(self) -> int:
        """
        Get the cumulative charge of the isotope
        """
        return self._ion.charge


class IsotopeSeries:
    """
    Compute isotopic distributions
    """
    def __init__(self,
                 *args,
                 isotopes: Optional[List[Isotope]] = None,
                 threshold: Real = 0.01):
        """
        This class computes isotopic distributions of arbitrary elemental or molecular compositions. The only physical
        requirement is that the charge is not 0.

        This computation can be constructed by providing either the Ion instance directly, or by providing a string of
        the composition and an integer of the charge. i.e.:

        >>> ion1 = IsotopeSeries(Ion("GdCuO2", 3))
        >>> ion2 = IsotopeSeries("GdCuO2", 3)
        >>> ion1 == ion2

        These are equivalent. Complex compositions can sometimes produce very large number of isotopologues with very
        small abundances that are quite below the detectability of most atom probe experiments. As a result the
        computation is thresholded to only display isotopologues above this threshold. As a result, the sum of the
        absolute abundances from

        >>> IsotopeSeries.isotopes

        is not guaranteed to be unity. If this is important, the threshold can be set to 0 to get all isotopologues, or
        consider working with relative abundances instead.

        This computation works for both elemental ions as well as molecular ions, i.e.

        >>> IsotopeSeries("CuO2", 2)
        >>> IsotopeSeries("Cu", 3)

        Are both valid signatures.

        The calculation used is derived from the following work:
            Margrave, J. L., & Polansky, R. B. (1962). Relative abundance calculations for isotopic molecular species.
            Journal of Chemical Education, 39(7), 335–337. https://doi.org/10.1021/ed039p335

        :param *args: Either Ion type, or composition (str) and charge (int)
        :param isotopes: "None" to calculate, otherwise must be provided explicitly
        """
        if isinstance(args[0], Ion) and len(args) == 1:
            ion = args[0]
        elif isinstance(args[0], str) and len(args) == 1:
            ion = Ion(args[0], 1)
        elif len(args) == 2:
            if isinstance(args[0], str) and isinstance(args[1], int):
                ion = Ion(args[0], args[1])
            else:
                raise ValueError("Expected string as first argument and charge int as second")
        else:
            raise ValueError("Could not decipher arguments")

        if not isinstance(ion, Ion):
            raise validate.IonTypeError(ion)
        self._ion = ion

        if self.ion.charge == 0:
            raise ValueError("Can only calculate isotopes of non-neutral ions (charge != 0)")

        # Set the isotopes
        self._all_isotopes = []
        self._isotopes = []
        if isotopes is not None:
            self._init_isotopes_as_manual(isotopes)
        else:
            if ion.num_atoms == 1:
                self._init_isotopes_as_element()
            else:
                self._init_isotopes_as_molecular()

        self.__index = 0

        self._threshold = None
        self.threshold = threshold

    def __repr__(self):
        thresh_str = f", threshold: {self.threshold*100}%" if self.threshold else ", all isotopes"
        retn = f"IsotopeSeries: {self.ion.hill_formula} +{self.ion.charge}{thresh_str}\n"
        max_val = max(i.abundance for i in self.isotopes)
        data = [[i+1, iso.ion.hill_formula, iso.number, iso.mass, iso.abundance*100, iso.abundance/max_val*100] for i, iso in enumerate(self.isotopes)]
        table = tab.tabulate(data, ("", "Ion", "Isotope", "Mass", "Abs. abundance %", "Rel. abundance %"))
        retn += table
        return retn

    def __len__(self) -> int:
        return len(self._isotopes)

    def __iter__(self):
        self.__index = 0
        return self

    def __next__(self) -> Isotope:
        if len(self._isotopes) == 0:
            raise StopIteration
        elif self.__index == len(self._isotopes):
            self.__index = 0
            raise StopIteration
        else:
            self.__index += 1
            return self._isotopes[self.__index - 1]

    def __getitem__(self, index: int) -> Isotope:
        return self._isotopes[index]

    @property
    def charge(self) -> int:
        """
        Get the cumulative charge of the ion
        """
        return self._ion.charge

    @property
    def ion(self) -> Ion:
        """
        Get the :class:`Ion` (Composition and charge)
        """
        return self._ion

    @property
    def abundances(self) -> ndarray:
        """
        Get an array of the abundances of each isotope
        """
        return n.array([i.abundance for i in self])

    @property
    def masses(self) -> ndarray:
        """
        Get an array of the mass/charge ratios of each isotope
        """
        return n.array([i.mass for i in self])

    @property
    def isotopes(self) -> List[Isotope]:
        """
        Get an array of all isotopes
        """
        return self._isotopes

    @property
    def threshold(self) -> Real:
        """
        Get the threshold used for computing the isotopes
        """
        return self._threshold

    @threshold.setter
    def threshold(self, new: Real):
        """
        Set the threshold. This represents the absolute abundance limit for the computed isotopes
        :param new: the new absolute abundance limit/threshold
        """
        self._threshold = validate.number_in_interval(new, 0, 1, lower_open=False, upper_open=False)
        if self.threshold == 0:
            self._isotopes = self._all_isotopes
        else:
            self._isotopes = [iso for iso in self._all_isotopes if iso.abundance >= self.threshold]

    def _init_isotopes_as_manual(self, isotopes):
        if not all(iso.ion == self.ion for iso in isotopes):
            raise ValueError("All isotopes must be of the same ion")
        if len(set(iso.mass for iso in isotopes)) != len(isotopes):
            raise ValueError("Cannot have duplicate isotopes")
        if not all(iso.charge == self.charge for iso in isotopes):
            raise ValueError("All isotopes must have the same charge")
        self._all_isotopes = sorted(isotopes, key=lambda iso: iso.mass)

    def _init_isotopes_as_element(self):
        """
        Initialize the isotopes from an elemental ion (1 element 1 atom)
        """
        pt_elem = pt.elements.symbol(self.ion.elements[0].symbol)
        isos = [Isotope(self.ion, pt_elem[i].isotope, pt_elem[i].mass / self.ion.charge, pt_elem[i].abundance / 100) for
                i in pt_elem.isotopes if pt_elem[i].abundance > 0]
        self._init_isotopes_as_manual(isos)
        assert self._is_unity

    def _init_isotopes_as_molecular(self):
        """
        Initialize the isotopes from a molecular ion (multiple elements/atoms)

        Calculation is derived from the following work:
            Margrave, J. L., & Polansky, R. B. (1962). Relative abundance calculations for isotopic molecular species.
            Journal of Chemical Education, 39(7), 335–337. https://doi.org/10.1021/ed039p335
        """

        def elem2ion(elem: Element, charge: int):
            return Ion(elem.symbol, charge)

        # Get the isotopes for each element (we ignore the scaling of charge until later)
        elem_isos_series = dict((i.symbol, IsotopeSeries(elem2ion(i, 1), threshold=0)) for i in self.ion.elements)
        inputs = []

        for elem_str, elem_num in self.ion.comp_str_dict.items():
            for i in range(int(elem_num)):
                inputs.append(elem_isos_series[elem_str].isotopes)

        # Create all possible combinations of isotopes
        combinations = list(product(*inputs))

        # Sort each isotopic combination by element first then isotope
        for i, item in enumerate(combinations):
            combinations[i] = sorted(item, key=attrgetter("ion.hill_formula", "number"))

        # Extract each unique isotopic combination
        unique_isos = []
        for i in combinations:
            if i not in unique_isos:
                unique_isos.append(i)

        # Calculate the isotopic abundances of the unique isotope combinations
        rslts = []
        for u_iso in unique_isos:
            iso_dict: Dict[str, List[Tuple[Isotope, int]]] = defaultdict(lambda: [])
            for iso in u_iso:
                if iso in (i[0] for i in iso_dict[iso.ion.hill_formula]):
                    continue
                else:
                    count = u_iso.count(iso)
                    iso_dict[iso.ion.hill_formula].append((iso, count))

            elem_parts = []
            for elem, isos in iso_dict.items():
                elem_amount = math.factorial(self.ion.comp_str_dict[elem])
                isotope_amounts = n.prod([math.factorial(i[1]) for i in isos])
                isotope_abundances = n.prod([i[0].abundance**(i[1]) for i in isos])
                elem_parts.append(elem_amount*isotope_abundances/isotope_amounts)
            rslts.append(n.prod(elem_parts))

        # Make the Isotope objects
        new_isos = []
        for isos, abundance in zip(unique_isos, rslts):
            number = sum(i.number for i in isos)
            mass = sum(i.mass for i in isos)/n.abs(self.ion.charge)
            newiso = Isotope(self.ion, number, mass, abundance)
            new_isos.append(newiso)

        self._init_isotopes_as_manual(new_isos)
        assert self._is_unity

    def _is_unity(self):
        """
        For internal checking when all isotopic abundances equal unity
        """
        return n.isclose(sum(i.abundance for i in self._all_isotopes), 1, 1e-10)

