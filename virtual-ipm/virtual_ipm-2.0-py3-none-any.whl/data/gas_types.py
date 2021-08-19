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

from ionics.material_data import H, He

from virtual_ipm.components import Mutable
from virtual_ipm.utils import to_json_string


class GasType(Mutable):
    """
    Base class for components representing gas types.
    """
    def __init__(self, composition, effective_charge):
        """
        Parameters
        ----------
        composition : unicode
            IUPAC specifier for the element or composite string of elements.
        effective_charge : float
            The effective core charge seen by the outermost shell electrons.
        """
        super().__init__()
        self.composition = composition
        self.effective_charge = effective_charge

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        return {
            'composition': self.composition,
            'effective_charge': self.effective_charge
        }


Hydrogen = GasType('H', H.effective_charge)
Helium = GasType('He', He.effective_charge)
