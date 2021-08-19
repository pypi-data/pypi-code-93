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

import abc

from anna import Action, Duplet, Choice, Integer, PhysicalQuantity, String, parametrize
import anna.input
from ionics.ddcs.random_sampling import InverseTransformSampling
from ionics.ddcs.voitkiv import VoitkivDDCS as Voitkiv
import numpy as np
from numpy.random import random_sample
import scipy.constants as constants

import virtual_ipm.data.gas_types as gas_types
from virtual_ipm.components import Model
from virtual_ipm.utils import arrange_input_as


class IonizationCrossSectionModel(Model):
    CONFIG_PATH = 'Ionization/Parameters'
    CONFIG_PATH_TO_IMPLEMENTATION = 'Ionization/Model'

    def __init__(self, configuration=None):
        super().__init__(configuration)

    @abc.abstractmethod
    def generate_momenta(self, count):
        raise NotImplementedError


class ZeroVelocities(IonizationCrossSectionModel):
    """
    This model creates all particles at rest.
    """

    def __init__(self):
        super().__init__()

    def generate_momenta(self, count):
        return np.zeros(shape=(count, 3), dtype=float)

Interface = IonizationCrossSectionModel


specific_gas_types = filter(
    lambda x: isinstance(getattr(gas_types, x), gas_types.GasType),
    dir(gas_types)
)
gas_type_choices = Choice(String('GasType'))
for specific_gas_type in specific_gas_types:
    gas_type_choices.add_option(specific_gas_type)
# noinspection PyTypeChecker
gas_type_parameter = Action(
    gas_type_choices,
    lambda x: getattr(gas_types, x)
)


@parametrize(
    gas_type_parameter,
    Duplet[PhysicalQuantity](
        'EnergyBoundaries',
        unit='eV',
        for_example=(0.01, 100.),
        info='The energies of generated electrons are sampled within this interval.'
    ),
    Integer(
        'EnergyBins',
        for_example=200,
        info='This parameter determines how fine or coarse the given energy range is sampled. '
             'For N energy bins there are exactly N different possible values for electron '
             'energies.'
    ),
    Duplet[PhysicalQuantity](
        'ScatteringAngleBoundaries',
        unit='rad',
        for_example=(0., '%(pi)'),
        info='The polar scattering angles (the angle between an electron velocity and the '
             'z-axis) is sampled within this interval.'
    ),
    Integer(
        'ScatteringAngleBins',
        for_example=200,
        info='This parameter determines how fine or coarse the given scattering angle range is '
             'sampled. For N scattering angle bins there are exactly N different possible values '
             'for scattering angles that generated electrons can have.'
    )
)
class VoitkivModel(IonizationCrossSectionModel):
    """
    This ionization model uses the Voitkiv double differential cross section.
    
    References
    ----------
    A.B. Voitkiv, N. Gruen, W. Scheid: "Hydrogen and helium ionization by relativistic projectiles
    in collisions with small momentum transfer", J.Phys.B: At.Mol.Opt.Phys 32, 1999
    """

    def __init__(self, beam, setup, configuration):
        super().__init__(configuration)
        self._beam = beam
        self._particle_mass = setup.particle_type.mass
        self.sampler = None

    def prepare(self):
        energy_min, energy_max = self._energy_boundaries
        energy_count = self._energy_bins
        angle_min, angle_max = self._scattering_angle_boundaries
        angle_count = self._scattering_angle_bins

        energies = arrange_input_as(energy_min, energy_max, energy_count, func='log10')
        scattering_angles = arrange_input_as(angle_min, angle_max, angle_count)

        ddcs = Voitkiv(
            self._beam.energy,
            self._beam.particle_type.charge_number,
            self._gas_type.composition
        )

        self.sampler = InverseTransformSampling(ddcs, energies, scattering_angles)
        # sampler = RejectionSampling(ddcs, energy_min, energy_max, angle_min, angle_max)

    def generate_momenta(self, count):
        if count == 0:
            return np.empty((0,))
        energies, angles = zip(*self.sampler.create_samples(count))
        energies, angles = np.array(energies), np.array(angles)
        # Conversion to SI units ([eV] -> [J]).
        energies *= constants.elementary_charge
        # Non-relativistic energies.
        momenta = np.sqrt(2. * self._particle_mass * energies)
        # Azimuthal angle:
        phis = 2. * constants.pi * random_sample(energies.shape[0])

        px = momenta * np.sin(angles) * np.cos(phis)
        py = momenta * np.sin(angles) * np.sin(phis)
        pz = momenta * np.cos(angles)

        return np.stack((px, py, pz))


# SimpleDDCS shall offer also cm^2 as a unit for ionization cross sections.
anna.input.Unit.register_unit('area', 'cm^2', 1e-4)


@parametrize(
    PhysicalQuantity('PlateauValue', unit='cm^2', info='The value of the ionization cross section '
                                                       'at the plateau.'),
    PhysicalQuantity('SlopeValue', unit='cm^2', info='The value of the ionization cross section '
                                                     'at the *end* of the slope.'),
    PhysicalQuantity('PlateauEnergy', unit='eV', info='The energy where the plateau *ends*.'),
    PhysicalQuantity('SlopeEnergy', unit='eV', info='The energy where the slope *ends*.'),
    PhysicalQuantity('ScatteringAngleStdDev', unit='rad', info='Scattering angles are sampled '
                                                               'from a Gaussian distribution.'),
)
class SimpleDDCS(IonizationCrossSectionModel):
    """
    This ionization cross section models features two independent, simple parametrizations for
    the energy distribution and the scattering angle distribution.
    The energy distribution has two distinct regions - a plateau region and a slope region - and 
    is characterized by four parameters:

    * `PlateauEnergy`: All energies <= `PlateauEnergy` have an equal probability; the probability
      for energies > `PlateauEnergy` decreases linearly in a log-log scale until it reaches 
      `SlopeValue` at `SlopeEnergy`.
    * `SlopeEnergy`: This parameter defines the maximum energy that a generated particle can have.
      The probability for energies ``PlateauEnergy < Energy <= SlopeEnergy`` decreases linearly
      (in a log-log scale) until it reaches `SlopeValue` at `SlopeEnergy`.
    * `PlateauValue`: The value of the ionization cross section at the plateau region. Together
      with the `SlopeValue` parameter this controls the steepness of the slope.
    * `SlopeValue`: The value of the ionization cross section at the end of the slope region.
      Together with the `PlateauValue` parameter this controls the steepness of the slope.

    This is a visualization of the energy distribution (in log-log scale)::

          Probability
          ^
          |
          |
          |---------------      <--- PlateauValue
          |               \\
          |                \\
          |                 \\
          |                  \\
          |                   \\
          |                    \\     <--- SlopeValue
        --|---------------|-----|----------> Energy
          |
                          ^     ^
                          |     |
                          |     |
              PlateauEnergy     SlopeEnergy

    The (polar) scattering angle is computed from a Gaussian distribution which is characterized by
    one parameter, namely its standard deviation. The distribution is centred around `pi/2` which
    corresponds to transverse scattering.
    The azimuthal angle is chosen randomly from a uniform distribution.
    """

    def __init__(self, setup, configuration):
        """
        Parameters
        ----------
        setup : :class:`Setup`
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super().__init__(configuration)
        self._particle_mass = setup.particle_type.mass

        # Compute some useful factors.
        E_p, E_s = self._plateau_energy, self._slope_energy
        V_p, V_s = self._plateau_value, self._slope_value

        self._a_plus_1 = a1 = (np.log10(V_s / V_p) / np.log10(E_s / E_p)) + 1.
        self._one_over_a_plus_1 = 1. / a1
        self._cn_times_sigmap = a1 / (E_s**a1 - E_p**a1)
        self._Ep_power_aplus1 = E_p ** a1

        # Compute the integrals of the two different regions. The probability with which an energy
        # is to be found in a particular region is proportional to the integral of that region.
        # (Integral = Number of particles for that region).
        p1 = V_p * E_p
        p2 = V_p / (E_p**(a1-1) * a1) * (E_s**a1 - E_p**a1)

        # Normalize probabilities to 1.
        self._p_plateau = p1 / (p1 + p2)
        self._p_slope = p2 / (p1 + p2)

    def as_json(self):
        return dict(
            super().as_json(),
            _a_plus_1=self._a_plus_1,
            _cn_times_sigmap=self._cn_times_sigmap,
            _p_plateau=self._p_plateau,
            _p_slope=self._p_slope
        )

    def generate_momenta(self, count):
        energies = self._sample_energies(count) * constants.elementary_charge  # [eV] -> SI units
        polar_angles = self._sample_scattering_angles(count)
        azimuthal_angles = 2.*np.pi * np.random.uniform(size=count)

        momenta = np.sqrt(2. * self._particle_mass * energies)

        px = momenta * np.sin(polar_angles) * np.cos(azimuthal_angles)
        py = momenta * np.sin(polar_angles) * np.sin(azimuthal_angles)
        pz = momenta * np.cos(polar_angles)

        return np.stack((px, py, pz))

    def _sample_energies(self, count):
        samples = np.empty(shape=count, dtype=float)
        p_region = np.random.uniform(size=count) <= self._p_plateau
        s_region = ~p_region
        samples[p_region] = np.random.uniform(0, self._plateau_energy, size=np.sum(p_region))
        # Using inverse transform sampling for the slope region.
        samples[s_region] = (
            self._a_plus_1 / self._cn_times_sigmap * np.random.uniform(size=np.sum(s_region))
            + self._Ep_power_aplus1
        ) ** self._one_over_a_plus_1
        return samples

    def _sample_scattering_angles(self, count):
        return np.random.normal(
            loc=np.pi/2.,
            scale=self._scattering_angle_std_dev,
            size=count
        )
