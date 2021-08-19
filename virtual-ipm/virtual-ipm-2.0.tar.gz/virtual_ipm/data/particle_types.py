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

from scipy.constants import physical_constants

from virtual_ipm.components import Mutable
from virtual_ipm.utils import to_json_string


class ParticleType(Mutable):
    """
    This class represents a particle type.
    """
    def __init__(self, charge_number, rest_energy):
        """
        Parameters
        ----------
        charge_number : int
            Electric charge in units of [elementary charge].
        rest_energy : float
            Rest energy in units of [eV].
        """
        super().__init__()
        self.charge_number = charge_number
        self.rest_energy = rest_energy
        self.charge = charge_number * physical_constants['elementary charge'][0]
        self.mass = (
            rest_energy * physical_constants['elementary charge'][0]
            / physical_constants['speed of light in vacuum'][0]**2
        )

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        return {
            'charge': self.charge,
            'charge_number': self.charge_number,
            'mass': self.mass,
            'rest_energy': self.rest_energy,
        }
