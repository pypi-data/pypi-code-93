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

from anna import PhysicalQuantity, SubstitutionGroup, Duplet, parametrize
import injector
import numpy as np

from virtual_ipm.components import Model
import virtual_ipm.di as di


class DeviceModel(Model):
    """
    (Abstract) Base class for device models.

    A device model is responsible for

    * defining the boundaries of the simulation region. This information is for example used by
      bunch electric field models in order to confine the volume in which the field must be
      precomputed.
    * deciding when particles are detected or invalidated (invalidated means a particle stopped
      tracking but was not detected; e.g. it hit the boundary of the chamber).

    The task of identifying which particles are detected is a very general one and extends
    for example to the use case of studying BIF monitors. The device would compute
    the decay probabilities per particle and use this information in order to determine when
    the particle is considered detected.

    Status updates must not be performed manually via assignment but using the dedicated methods
    provided by this base class instead:

    * :method:`Device.invalidate`
    * :method:`Device.detect`

    This is because for each status update a corresponding status update notification will be
    generated and published on the :method:`ParticleSupervisor.status_updates` stream.
    When using manual assignment those notifications are not created.
    """

    CONFIG_PATH_TO_IMPLEMENTATION = 'Device/Model'
    CONFIG_PATH = 'Device/Parameters'

    @injector.inject(
        particle_supervisor=di.components.particle_supervisor,
        configuration=di.components.configuration
    )
    def __init__(self, particle_supervisor, configuration):
        """
        Initialize the device model.

        Parameters
        ----------
        particle_supervisor : :class:`ParticleSupervisor`
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super().__init__(configuration)
        self._particle_supervisor = particle_supervisor

    def invalidate(self, particles, progress):
        """
        Set the status of the given particles to "invalid".

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress at which the status change happens.
        """
        self.log.debug('Particles invalidated: %s', particles)
        if particles:
            self._particle_supervisor.invalidate(particles, progress)

    def detect(self, particles, progress):
        """
        Set the status of the given particles to "detected".

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress at which the status change happens.
        """
        self.log.debug('Particles detected: %s', particles)
        if particles:
            self._particle_supervisor.detect(particles, progress)

    @abc.abstractmethod
    def scan_particles(self, particles, progress):
        """
        Check the given particles and change their statuses if appropriate.
        This method must be implemented by all Device subclasses.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress at which this method is invoked.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def x_boundaries(self):
        """
        The x-boundaries of the device.

        Returns
        -------
        x_boundaries : :class:`~np.ndarray`, shape (2,)
            In units of [m]. The first item denotes the lower and the second item the upper
            boundary: ``x_boundaries[0] < x_boundaries[1]``.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def y_boundaries(self):
        """
        The y-boundaries of the device.

        Returns
        -------
        y_boundaries : :class:`~np.ndarray`, shape (2,)
            In units of [m]. The first item denotes the lower and the second item the upper
            boundary: ``y_boundaries[0] < y_boundaries[1]``.
        """
        raise NotImplementedError

    @property
    def z_boundaries(self):
        """
        The z-boundaries of the device.

        Returns
        -------
        z_boundaries : :class:`~np.ndarray`, shape (2,)
            In units of [m]. The first item denotes the lower and the second item the upper
            boundary: ``z_boundaries[0] < z_boundaries[1]``. Returns ``array([-inf,  inf])``.
        """
        return np.array((-np.inf, np.inf))

Interface = DeviceModel


class FreeSpace(DeviceModel):
    """
    A no-op device model. This model won't change particle statuses and lets them propagate freely.
    """

    def __init__(self):
        super().__init__()
        self._xyz_boundaries = np.array((-np.inf, np.inf))

    @property
    def x_boundaries(self):
        return self._xyz_boundaries

    @property
    def y_boundaries(self):
        return self._xyz_boundaries

    def scan_particles(self, particles, progress):
        pass


@parametrize(
    Duplet[PhysicalQuantity](
        'XBoundaries',
        unit='m',
        info='The x-boundaries of the beam pipe at the BIF location.'
    ).use_container(np.array),
    Duplet[PhysicalQuantity](
        'YBoundaries',
        unit='m',
        info='The y-boundaries of the beam pipe at the BIF location.'
    ).use_container(np.array),
    SubstitutionGroup(
        PhysicalQuantity('Lifetime', unit='s')
    ).add_option(
        PhysicalQuantity('DecayRate', unit='Hz'),
        lambda x: 1./x
    )
)
class BIF(DeviceModel):
    @injector.inject(
        setup=di.components.setup
    )
    def __init__(self, setup):
        super().__init__()
        self._decay_probability = 1. - np.exp(-setup.time_delta / self._lifetime)

    @property
    def x_boundaries(self):
        return self._x_boundaries

    @property
    def y_boundaries(self):
        return self._y_boundaries

    def scan_particles(self, particles, progress):
        decays = np.random.uniform(size=len(particles)) < self._decay_probability
        self.detect(particles[decays], progress)


@parametrize(
    Duplet[PhysicalQuantity](
        'XBoundaries',
        unit='m'
    ).use_container(np.array),
    Duplet[PhysicalQuantity](
        'YBoundaries',
        unit='m'
    ).use_container(np.array)
)
class BasicIPM(DeviceModel):
    """
    Allows for specification of upper and lower boundaries with respect to x- and y-direction.
    The detector is located at the lower y-boundary. When particles reach this level they are
    considered detected.
    """

    def __init__(self):
        super().__init__()
        self._lower_transverse_boundaries = np.array([
            self.x_boundaries[0], self.y_boundaries[0]
        ])
        self._upper_transverse_boundaries = np.array([
            self.x_boundaries[1], self.y_boundaries[1]
        ])

    @property
    def x_boundaries(self):
        return self._x_boundaries

    @property
    def y_boundaries(self):
        return self._y_boundaries

    def scan_particles(self, particles, progress):
        # Detector is located at the lower y-boundary.
        invalid = (
            np.any(
                particles.position[:-1].T >= self._upper_transverse_boundaries,
                axis=1
            )
            |
            (particles.x <= self.x_boundaries[0])
        )
        self.invalidate(particles[invalid], progress)
        # `particles` is a view which corresponds to all "tracked" particles so we don't need to
        # check for `~invalid` here because the above call to `invalidate` already changed the
        # statuses appropriately (from "tracked" to "invalid").
        self.detect(particles[particles.y <= self.y_boundaries[0]], progress)


class InterpolatingIPM(BasicIPM):
    __doc__ = BasicIPM.__doc__.rstrip() + """
    This device model uses the current and the previous position of particles in order to
    interpolate their final positions at the detector level.
    """

    @injector.inject(
        setup=di.components.setup
    )
    def __init__(self, setup):
        super().__init__()
        self._dt = setup.time_delta

    def detect_particle(self, particles, progress):
        # Interpolate final positions at detector level.
        inverse_y_slope = self._dt / (particles.y - particles.previous_y)
        delta_time_to_detector = (
            inverse_y_slope
            * (self.y_boundaries[0] - particles.previous_y)
        )
        slopes = (particles.position - particles.previous_position) / self._dt
        particles.position = particles.previous_position + slopes * delta_time_to_detector
        super().detect_particle(particles, progress)
