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

from anna import Action, Bool, Integer, PhysicalQuantity, String, \
    Group, ComplementaryGroup, Configurable, parametrize, SubstitutionGroup
import injector
import numpy as np
from scipy.constants import speed_of_light, elementary_charge

from virtual_ipm.data.particle_types import ParticleType
import virtual_ipm.di as di


log = logging.getLogger(__name__)


# noinspection PyTypeChecker
@parametrize(
    Integer(
        'NumberOfParticles',
        info='The number of particles to be simulated. The actual number can deviate slightly if '
             'particle generation involves random number generation.'
    ),
    ComplementaryGroup(
        'TimeRange',
        (
            PhysicalQuantity(
                'SimulationTime',
                unit='s',
                info='The simulation time defines the time range which is covered by a simulation '
                     'run. After this time has elapsed the simulation run is complete. Choosing '
                     'the simulation time large enough is important so that the desired bunch(es) '
                     'can move through the chamber and in addition all generated particles are '
                     'detected (extracted). For a common IPM setup the extraction time is roughly '
                     '400 ns for ions and 20 ns for electrons.'
            ) > 0.,
            lambda time_delta, n_steps: time_delta * n_steps
        ),
        (
            PhysicalQuantity(
                'TimeDelta',
                unit='s',
                info='The time delta defines how much time elapses during one simulation step; '
                     'that is it defines the size of a time step. Choosing the time step small '
                     'enough is important in order to obtain an accurate particle tracking.'
            ) > 0.,
            lambda simulation_time, n_steps: simulation_time / n_steps
        ),
        (
            Integer(
                'NumberOfTimeSteps',
                info='The number of time steps defines how fine or coarse a given time range is '
                     'divided or what simulation time a given time delta will add up to. Together '
                     'with one of the time parameters it defines the time extent of a simulation '
                     'run.'
            ) > 0,
            lambda simulation_time, time_delta: int(round(simulation_time / time_delta))
        ),
        info='The time range of a simulation defines\n'
             '    a) How much time elapses during a simulation run and\n'
             '    b) How much time elapses during a single simulation step.\n\n'
             'The former ensures that all physical processes (including the detection of '
             'particles) have enough time to take place while the latter defines the accuracy of '
             'the particle tracking (smaller time steps means more accurate tracking results).\n '
             'By specifying two of the three possible parameters the third one will be computed '
             'automatically. In the end the simulation time and the time delta are the ones which '
             'are deciding.'
    ),
    Action(
        Group(
            'ParticleType',
            Integer('ChargeNumber'),
            SubstitutionGroup(
                PhysicalQuantity('RestEnergy', unit='eV')
            ).add_option(
                PhysicalQuantity('RestMass', unit='kg'),
                lambda x: x * speed_of_light**2 / elementary_charge
            )
        ),
        lambda x: ParticleType(x['ChargeNumber'], x['RestEnergy'])
    ),
    Bool(
        'NumpyRaiseOnFloatingPointError',
        default=True,
        info='This flat controls if an exception should be raised when a floating point error is '
             'encountered during the simulation. This applies to all FPN errors but underflow '
             'errors which are controlled by a separate flag. In general raising is a good idea '
             'because it means that invalid numbers are used (infinity, not a number) which will '
             'lead to invalid results. One should rather fix those errors than silence them.'
    ),
    String(
        'NumpyHandleUnderflow',
        default='ignore',
        info='Underflow errors are those where the floating point precision is not sufficient in '
             'order to distinguish a certain number from zero. As a default zero is assumed '
             'instead. This is a reasonable behaviour as all computations are still valid within '
             'the range of floating point precision which is available.'
    ),
    Bool(
        'OnlyGenerateParticles',
        default=False,
        info='If selected then the simulation will only perform particle generation at each time '
             'step (i.e. omit particle tracking and particle detection). This is useful for '
             'speeding up the generation of initial parameters. If you want to save these '
             'values make sure that you deselect the corresponding `SkipTrackedParticles` '
             'parameter of the OutputRecorder.'
    ),
    _rng_seed=Integer(
        'RNGSeed',
        optional=True,
        info='The Random Number Generator seed can be used to ensure consistency between many '
             'runs of a similar setup.'
    )
)
class SimulationParameters(Configurable):
    """
    General (basic) parameters that are common to each simulation run. 
    """

    CONFIG_PATH = 'Simulation'

    @injector.inject(
        configuration=di.components.configuration
    )
    def __init__(self, configuration):
        super().__init__(configuration)

        self._simulation_time = self._time_range[0]
        self._time_delta = self._time_range[1]
        self._number_of_time_steps = self._time_range[2]

        if self._numpy_raise_on_floating_point_error:
            np.seterr(divide=str('raise'), over=str('raise'), invalid=str('raise'))
        np.seterr(under=self._numpy_handle_underflow)

        if self._rng_seed is not None:
            np.random.seed(self._rng_seed)

        log.debug('%s', self)

    @property
    def number_of_particles(self):
        """
        Returns
        -------
        number_of_particles : int
            The number of particles to be simulated.
        """
        return self._number_of_particles

    @property
    def number_of_time_steps(self):
        """
        Returns
        -------
        number_of_time_steps : int
            The total number of simulation (time) steps to be performed during a simulation run.
        """
        return self._number_of_time_steps

    @property
    def simulation_time(self):
        """
        Returns
        -------
        simulation_time : float
            The total time that that elapses during a simulation run,
            in units of [s].
        """
        return self._simulation_time

    @property
    def time_delta(self):
        """
        Returns
        -------
        time_delta : float
            The time which elapses between two simulation steps,
            in units of [s].
        """
        return self._time_delta

    @property
    def particle_type(self):
        """
        Returns
        -------
        particle_type : :class:`ParticleType`
        """
        return self._particle_type

    @property
    def only_generate_particles(self):
        """
        Returns
        -------
        only_generate_particles : bool
            Flag indicating whether the simulation should perform only particle generation.
        """
        return self._only_generate_particles

Setup = SimulationParameters
