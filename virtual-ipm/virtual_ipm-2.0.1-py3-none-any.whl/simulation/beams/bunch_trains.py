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

import copy

from anna import parametrize, Duplet, Integer, PhysicalQuantity, SubstitutionGroup
import numpy as np

from virtual_ipm.components import Mutable
from .bunches import Bunch
from virtual_ipm.simulation.errors import IncompatibleModelsError
from virtual_ipm.utils import to_json_string
from .utils import compute_bunch_length_as_time


class Window:
    """
    Base class for windows on bunch trains. A window provides the part of the bunch train which
    is currently visible (relevant) from (for) the processes taking place in the simulation region
    (usually the IPM chamber).
    """

    def __str__(self):
        return to_json_string(self.as_json())

    def apply(self, progress):
        """
        Return those bunches which are within the window region for the given simulation progress.

        Parameters
        ----------
        progress : :class:`Progress`

        Returns
        -------
        bunches : list[:class:`Bunch`]
        """
        raise NotImplementedError

    def as_json(self):
        return {
            '__class__': self.__class__.__name__
        }


class LinearWindow(Window):
    """
    A linear window with a fixed width. The width is counter from z=0 in positive and negative
    z-direction (i.e. the full width is 2*`width`). All bunches whose centers are within
    +/-`width` are taken into account.
    """

    def __init__(self, elements, width):
        super().__init__()
        self._elements = elements
        self._width = width

    def apply(self, progress):
        if self._width is None:
            return self._elements
        return list(filter(
            lambda bunch: np.abs(bunch.longitudinal_offset + progress.time) <= self._width,
            self._elements
        ))

    def as_json(self):
        return dict(
            super().as_json(),
            width=self._width,
            elements=[e.as_json() for e in self._elements]
        )


class CyclicWindow(Window):
    """
    A cyclic window with a fixed width. Bunches are cycled from the right boundary (+`width`) to
    the left boundary (-`width`). All bunches are taken into account and their longitudinal offset
    is adjusted so they are always within the window region (by wrapping the bunches around the
    boundaries).
    """

    def __init__(self, elements, width):
        super().__init__()
        self._elements = elements
        self._width = width

    def apply(self, progress):
        def cycle_bunch(bunch):
            if bunch.longitudinal_offset + progress.time >= self._width:
                # `width is measured from the center of the chamber.
                total_overlap = bunch.longitudinal_offset + progress.time - self._width
                fractional_overlap = total_overlap / (2. * self._width)
                cyclic_overlap = (fractional_overlap - int(fractional_overlap)) * 2. * self._width
                longitudinal_offset = -1.0 * self._width + cyclic_overlap - progress.time
                cycled_bunch = copy.copy(bunch)
                cycled_bunch.longitudinal_offset = longitudinal_offset
                return cycled_bunch
            return bunch

        return list(map(
            cycle_bunch,
            self._elements
        ))

    def as_json(self):
        return dict(
            super().as_json(),
            width=self._width,
            elements=[e.as_json() for e in self._elements]
        )


class BunchTrain(Mutable):
    """
    Base class for bunch trains. A bunch train contains a number of bunches which all share
    the same shape and electric field models and which are identified by their longitudinal offset.
    """

    CONFIG_PATH = 'BunchTrain'
    TYPE_INDICATOR_PATH = '{0}/Type'.format(CONFIG_PATH)
    CONFIG_PATH_TO_IMPLEMENTATION = TYPE_INDICATOR_PATH

    def __init__(self, configuration):
        super().__init__(configuration)

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        return {
            '__class__': self.__class__.__name__
        }

    def get_bunch_at(self, progress, z):
        """
        Get the bunch which is at the specified longitudinal position at the specified time.

        Parameters
        ----------
        progress : :class:`Progress`
        z : float
            Longitudinal position in the lab frame in units of [m].

        Returns
        -------
        bunch : :class:`Bunch` or None
            If there is no bunch at the specified time and position then ``None`` is returned.
        """
        bunches = self.relevant_bunches(progress)
        for bunch in bunches:
            center_position = bunch.longitudinal_position(progress)
            head_position = center_position + bunch.length / 2.
            tail_position = center_position - bunch.length / 2.
            # noinspection PyTypeChecker
            if tail_position < z < head_position:
                return bunch
        return None

    def relevant_bunches(self, progress):
        """
        Get all relevant bunches for the given simulation progress. This is evaluated by the window
        which is used by the bunch train instance.

        Parameters
        ----------
        progress : :class:`Progress`

        Returns
        -------
        bunches : list[:class:`Bunch`]
        """
        raise NotImplementedError


@parametrize(
    Duplet[PhysicalQuantity](
        'TransverseOffset',
        unit='m',
        default=np.zeros((2,), dtype=float),
        info='Transverse offset of the beam center from the chamber center.'
    ).use_container(np.array)
)
class DCBeam(BunchTrain):
    """
    Use this bunch train class for emulating a DC beam.
    
    .. note::
       This bunch train class must be used together with a bunch shape model of infinite length.
    """

    def __init__(self, bunch_shape, bunch_electric_field_model, configuration):
        super().__init__(configuration)

        # The bunch shape must have infinite length in order to emulate a DC beam.
        if np.isfinite(bunch_shape.length):
            raise IncompatibleModelsError(
                'Invalid bunch shape model: {0}. Only bunch shapes of infinite length can be used '
                'to emulate a DC beam.'.format(
                    type(bunch_shape).__name__
                )
            ) from None

        self._bunch = Bunch(
            bunch_shape,
            bunch_electric_field_model,
            0.,
            self._transverse_offset,
            configuration
        )

    def as_json(self):
        return dict(
            super().as_json(),
            bunch=self._bunch.as_json()
        )

    def get_bunch_at(self, progress, z):
        return self._bunch

    def relevant_bunches(self, progress):
        return [self._bunch]


@parametrize(
    Integer('NumberOfBunches') >= 1,
    PhysicalQuantity(
        'LongitudinalOffset',
        unit='s',
        optional=True,
        info='Longitudinal offset of the first bunch\'s center with respect to z = 0 in the lab '
             'frame. Negative offsets correspond to z < 0. If not specified then negative '
             'half the bunch length is used (i.e. bunch head at z = 0). This influences the time '
             'at which particles will be generated at a specific z-position as well as whether '
             'these particles will see the whole bunch or only part of it. For example if '
             'particles are generated at z = 0 and the longitudinal offset is set to zero then '
             'the bunch center starts at z = 0 and only particles from the center to the tail '
             'will be generated (omitting the head to center part).'
    ),
    Duplet[PhysicalQuantity](
        'TransverseOffset',
        unit='m',
        default=np.zeros((2,), dtype=float),
        info='Transverse offset of the beam center from the chamber center.'
    ).use_container(np.array),
    PhysicalQuantity(
        'WindowWidth',
        unit='s',
        optional=True,
        info='The window is placed with respect to the center of the chamber (z = 0). Only '
             'bunches inside the window are taken into account. If not specified then all bunches '
             'are taken into account. If many bunches take part in the simulation it is more '
             'efficient to choose a limited window width because otherwise the electric and '
             'magnetic fields of all bunches will be taken into account while they are negligible '
             'for bunches that are far away form the simulation region. The window width provides '
             'an option for assisting which bunch fields should be considered zero before an '
             'attempt to compute them is made.'
    ),
    _bunch_spacing=SubstitutionGroup(
        PhysicalQuantity(
            'BunchSpacing',
            unit='s',
            info='The bunch spacing is the distance of bunch centers of two subsequent bunches.'
        ) >= 0
    ).add_option(
        PhysicalQuantity(
            'BunchFrequency',
            unit='Hz',
            info='The repetition frequency with which bunches appear.'
        ) >= 0,
        lambda x: 1./x
    )
)
class LinearBunchTrain(BunchTrain):
    """
    All bunches are placed behind one another and their offsets to the chamber are computed from
    the previous bunch's offset + the bunch spacing. The first bunch's offset can be controlled with
    the `LongitudinalOffset` parameter.
    """

    def __init__(self, bunch_shape, bunch_electric_field_model, configuration):
        super().__init__(configuration)

        energy = Bunch._energy.load_from_configuration(configuration)
        particle_type = Bunch._particle_type.load_from_configuration(configuration)
        rest_energy = particle_type.rest_energy

        bunch_length_as_time = \
            compute_bunch_length_as_time(bunch_shape.length, energy, rest_energy)

        if self._number_of_bunches > 1 and bunch_length_as_time > self._bunch_spacing:
            self.log.warning('Bunches interleave (bunch length > bunch spacing)')

        longitudinal_offset = (
            self._longitudinal_offset
            if self._longitudinal_offset is not None
            else -1.0 * bunch_length_as_time / 2.
        )
        offsets = (
            longitudinal_offset
            - np.arange(self._number_of_bunches) * self._bunch_spacing
        )
        # noinspection PyUnresolvedReferences
        self.log.debug('Offsets: %s', offsets.tolist())
        # noinspection PyTypeChecker
        elements = list(map(
            lambda offset: Bunch(
                bunch_shape,
                bunch_electric_field_model,
                offset,
                self._transverse_offset,
                configuration
            ),
            offsets
        ))
        self._window = LinearWindow(elements, self._window_width)

    def as_json(self):
        return dict(
            super().as_json(),
            number_of_bunches=self._number_of_bunches,
            bunch_spacing=self._bunch_spacing,
            window=self._window.as_json()
        )

    def relevant_bunches(self, progress):
        return self._window.apply(progress)


class SingleBunch(LinearBunchTrain):
    """
    Use this bunch train class for single bunch simulations.
    
    This class is a special case of the `LinearBunchTrain` with `NumberOfBunches = 1` and
    `BunchSpacing = 0`.
    """
    _number_of_bunches = 1
    _bunch_spacing = 0
    _window_width = None


@parametrize(
    Integer('NumberOfBunches') >= 1,
    Duplet[PhysicalQuantity](
        'TransverseOffset',
        unit='m',
        default=np.zeros((2,), dtype=float),
        info='Transverse offset of the beam center from the chamber center.'
    ).use_container(np.array),
    PhysicalQuantity(
        'LongitudinalOffset',
        unit='s',
        default=0,
        info='Longitudinal offset for all bunch centers with respect to z = 0 in the lab '
             'frame. Negative offsets correspond to z < 0. The whole bunch train is centered '
             'around z = 0 and then cycled within its spatial range during the simulation. A '
             'longitudinal offset will adjust this centering. Bunches that cross either the left '
             'or right margin are wrapped around accordingly in order to preserve their spatial '
             'and temporal appearance (with respect to an observer positioned at z = 0).'
    ),
    _bunch_spacing=SubstitutionGroup(
        PhysicalQuantity(
            'BunchSpacing',
            unit='s',
            info='The bunch spacing is the distance of bunch centers of two subsequent bunches.'
        ) >= 0
    ).add_option(
        PhysicalQuantity(
            'BunchFrequency',
            unit='Hz',
            info='The repetition frequency with which bunches appear.'
        ) >= 0,
        lambda x: 1./x
    )
)
class CircularBunchTrain(BunchTrain):
    """
    All bunches are placed in a symmetric fashion around the chamber (with respect to the
    longitudinal direction). While bunches move during the simulation they are cycled from the
    "right" side (z > 0) to the left side (z < 0) and hence can pass the simulation region multiple
    times.
    """

    def __init__(self, bunch_shape, bunch_electric_field_model, configuration):
        super().__init__(configuration)

        energy = Bunch._energy.load_from_configuration(configuration)
        particle_type = Bunch._particle_type.load_from_configuration(configuration)
        rest_energy = particle_type.rest_energy

        bunch_length_as_time = \
            compute_bunch_length_as_time(bunch_shape.length, energy, rest_energy)

        if bunch_length_as_time > self._bunch_spacing:
            self.log.warning('Bunches interleave (bunch length > bunch spacing)')

        # Include an extra spacing that separates last and first bunch (wrap-around).
        window_width = self._number_of_bunches * self._bunch_spacing / 2.

        max_longitudinal_offset = window_width - self._bunch_spacing / 2.
        offsets = (
            max_longitudinal_offset
            - np.arange(self._number_of_bunches) * self._bunch_spacing
        )
        if self._longitudinal_offset != 0:
            sign = np.sign(self._longitudinal_offset)
            offsets = (
                (offsets + sign*window_width + self._longitudinal_offset)
                % (sign * 2 * window_width)
                - sign*window_width
            )
            offsets[offsets == window_width] = -window_width
        # noinspection PyUnresolvedReferences
        self.log.debug('Offsets: %s', offsets.tolist())
        # noinspection PyTypeChecker
        elements = list(map(
            lambda offset: Bunch(
                bunch_shape,
                bunch_electric_field_model,
                offset,
                self._transverse_offset,
                configuration
            ),
            offsets
        ))
        self._window = CyclicWindow(elements, window_width)

    def as_json(self):
        return dict(
            super().as_json(),
            number_of_bunches=self._number_of_bunches,
            bunch_spacing=self._bunch_spacing,
            window=self._window.as_json()
        )

    def relevant_bunches(self, progress):
        return self._window.apply(progress)
