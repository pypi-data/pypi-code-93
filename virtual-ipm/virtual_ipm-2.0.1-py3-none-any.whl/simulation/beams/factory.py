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
from types import MethodType

from anna import adopt, parametrize, Bool
import injector
import numpy as np

import virtual_ipm.di as di
from .bunches import Bunch
from .bunches import electric_field_models as bunch_fields
from .bunches import shapes as bunch_shapes
from . import bunch_trains
from virtual_ipm.components import Component
from virtual_ipm.simulation.errors import ConfigurationError
from .bunch_trains import DCBeam


@adopt(Bunch)
@parametrize(
    _electric_field_off=Bool(
        'ElectricFieldOFF',
        default=False,
        info='Setting this parameter causes the beam to have zero electric field.'
    ),
    _magnetic_field_off=Bool(
        'MagneticFieldOFF',
        default=False,
        info='Setting this parameter causes the beam to have zero magnetic field.'
    )
)
class Beam(Component):
    """
    A beam has exactly one bunch shape and one bunch electric field model which is the same for
    all bunches in its bunch train. Thus the only difference between bunches in the bunch train is
    their longitudinal (hence time-like) offset to the chamber center.
    """

    CONFIG_PATH = 'Parameters'

    def __init__(self, bunch_shape, bunch_electric_field_model, bunch_train, configuration):
        super().__init__(configuration)
        self._bunch_shape = bunch_shape
        self._bunch_electric_field_model = bunch_electric_field_model
        self._bunch_train = bunch_train
        if isinstance(self._bunch_train, DCBeam) and self.bunch_population != 1:
            raise ConfigurationError('BunchPopulation must be set to 1 for DCBeam to work correctly')

    def as_json(self):
        attributes = super().as_json()
        attributes.update({
            'bunch shape': self._bunch_shape.as_json(),
            'bunch electric field model': self._bunch_electric_field_model.as_json(),
            'bunch train': self._bunch_train.as_json(),
            'bunch population': '%e' % self.bunch_population,
            'energy': '%e' % self.energy,
            'particle type': self.particle_type.as_json(),
        })
        return attributes

    @property
    def bunch_population(self):
        return self._bunch_population

    @property
    def energy(self):
        return self._energy

    @property
    def particle_type(self):
        return self._particle_type

    def prepare(self):
        super().prepare()
        self._bunch_shape.prepare()
        self._bunch_electric_field_model.prepare()

    def charge_density_at(self, position_four_vector, progress):
        """
        Get the beam's charge density at the specified positions and time.
        
        .. note::
        This method requires a single four vector position and does not allow multiple positions
        in form of 2d arrays because for each position it needs to search the corresponding bunch
        and this operation can't be done natively in numpy anyway. However the positions must be
        given as a column vector in order to preserve consistency with the other interfaces
        accepting positions.
        
        Parameters
        ----------
        position_four_vector : :class:`np.ndarray`, shape (4, 1)
        progress : :class:`Progress`
        
        Returns
        -------
        charge_density : :class:`np.ndarray`, shape (1,)
        """
        bunch = self._bunch_train.get_bunch_at(progress, position_four_vector[3, 0])
        if bunch is not None:
            return bunch.charge_density_at(position_four_vector, progress)
        return np.zeros(1, dtype=float)

    def linear_charge_density_at(self, position_four_vector, progress):
        """
        Get the beam's linear charge density at the specified position and time.

        .. note::
        This method requires a single four vector position and does not allow multiple positions
        in form of 2d arrays because for each position it needs to search the corresponding bunch
        and this operation can't be done natively in numpy anyway. However the positions must be
        given as a column vector in order to preserve consistency with the other interfaces
        accepting positions.

        Parameters
        ----------
        position_four_vector : :class:`np.ndarray`, shape (4, 1)
            The x- and y-positions are ignored.
        progress : :class:`Progress`

        Returns
        -------
        linear_charge_density : :class:`np.ndarray`, shape (1,)
            In units of [C/m].
        """
        bunch = self._bunch_train.get_bunch_at(progress, position_four_vector[3, 0])
        if bunch is not None:
            return bunch.linear_charge_density_at(position_four_vector, progress)
        return np.zeros(1, dtype=float)

    def generate_positions_in_transverse_plane(self, progress, count, z):
        """
        Choose the correct bunch and invoke its corresponding method.
        
        Parameters
        ----------
        progress : :class:`Progress`
        count : int
            Number of positions to be generated.
        z : float
            Specifies the transverse plane, given in the lab frame in units of [m].
        """
        bunch = self._bunch_train.get_bunch_at(progress, z)
        if bunch is None:
            raise ValueError(
                'There is no bunch at the specified position and time '
                '(long. position: %e, time step: %e)'
                % (z, progress.step)
            )
        return bunch.generate_positions_in_transverse_plane(progress, count, z)

    def electric_field_at(self, position_four_vectors, progress):
        """
        See Also
        --------
        :method:`EMFieldsCollector.electric_field_at` : For explanations, parameters and return
                                                        values.
        """
        return sum(map(
            lambda bunch: bunch.electric_field_at(position_four_vectors, progress),
            self._bunch_train.relevant_bunches(progress)
        ))

    def magnetic_field_at(self, position_four_vectors, progress):
        """
        See Also
        --------
        :method:`EMFieldsCollector.magnetic_field_at` : For explanations, parameters and return
                                                        values. 
        """
        return sum(map(
            lambda bunch: bunch.magnetic_field_at(position_four_vectors, progress),
            self._bunch_train.relevant_bunches(progress)
        ))


class BeamFactory:
    """
    This class can be used to create beams from corresponding configuration objects.
    """

    log = logging.getLogger(str('{0}.{1}'.format(__name__, 'BeamFactory')))

    @injector.inject(device=di.components.device)
    def __init__(self, device):
        """
        Parameters
        ----------
        device : :class:`DeviceManager`
        """
        super().__init__()
        self._device = device

    def create(self, configuration):
        """
        Create a :class:`Beam` instance from the given configuration.
        
        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor`
        """
        self.log.debug('Creating new beam ...')

        bunch_shape_class = getattr(
            bunch_shapes,
            configuration.get_text(bunch_shapes.Interface.CONFIG_PATH_TO_IMPLEMENTATION)
        )
        bunch_electric_field_model_class = getattr(
            bunch_fields,
            configuration.get_text(bunch_fields.Interface.CONFIG_PATH_TO_IMPLEMENTATION)
        )

        bunch_shape = bunch_shape_class(configuration)
        bunch_electric_field_model = bunch_electric_field_model_class(
            bunch_shape,
            self._device,
            configuration
        )
        self.log.debug('BunchShape: %s', bunch_shape)
        self.log.debug('BunchElectricFieldModel: %s', bunch_electric_field_model)

        bunch_train_type_str = configuration.get_text(bunch_trains.BunchTrain.TYPE_INDICATOR_PATH)
        try:
            bunch_train_type = getattr(bunch_trains, bunch_train_type_str)
        except AttributeError:
            raise ConfigurationError('Unknown bunch train type: %s' % bunch_train_type_str) from None
        bunch_train = bunch_train_type(
            bunch_shape,
            bunch_electric_field_model,
            configuration
        )

        self.log.debug('BunchTrain: %s', bunch_train)

        beam = Beam(
            bunch_shape,
            bunch_electric_field_model,
            bunch_train,
            configuration
        )

        if beam._electric_field_off:
            self.log.debug('Electric field is switched OFF')

            # noinspection PyUnusedLocal
            def electric_field_at(*args, **kwargs):
                return np.zeros(shape=(3, 1), dtype=float)

            setattr(
                beam,
                beam.electric_field_at.__name__,
                MethodType(electric_field_at, beam)
            )

        if beam._magnetic_field_off:
            self.log.debug('Magnetic field is switched OFF')

            # noinspection PyUnusedLocal
            def magnetic_field_at(*args, **kwargs):
                return np.zeros(shape=(3, 1), dtype=float)

            setattr(
                beam,
                beam.magnetic_field_at.__name__,
                MethodType(magnetic_field_at, beam)
            )

        if beam._electric_field_off and beam._magnetic_field_off:
            self.log.debug(
                'Monkey patch prepare method of bunch electric field model with a no-op method'
            )

            # noinspection PyShadowingNames
            def prepare(self):
                self.log.debug('Skip preparation because beam fields are switched off')

            setattr(
                bunch_electric_field_model,
                bunch_electric_field_model.prepare.__name__,
                MethodType(prepare, bunch_electric_field_model)
            )

        self.log.debug('... done.')

        return beam
