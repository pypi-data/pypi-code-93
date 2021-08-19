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

"""
This module provides components that model the propagation of particles
throughout the simulation.
"""

import abc

from anna import depends_on, PhysicalQuantity, parametrize
from anna.utils import use_docs_from
import injector
import numpy as np

from virtual_ipm.components import Model
import virtual_ipm.di as di
from virtual_ipm.utils.mathematics import sincc, cosincc, cubsincc


class ParticleTrackingModel(Model):
    """
    (Abstract) Base class for particle tracking models.

    A particle tracking model is responsible for propagating particles throughout
    the simulation. It must provide a method for updating particle positions and
    momenta via :method:`~ParticleTrackingModel.propagate`.
    """

    CONFIG_PATH_TO_IMPLEMENTATION = 'ParticleTracking/Model'
    CONFIG_PATH = 'ParticleTracking/Parameters'

    def __init__(self, em_fields, configuration=None):
        """
        Initialize the particle tracking model.

        Parameters
        ----------
        em_fields : :class:`EMFieldsCollector`
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super().__init__(configuration)
        self._em_fields = em_fields

    def prepare(self):
        """
        Prepare the particle tracking model.
        """
        super().prepare()

    def electric_field_for(self, particles, progress):
        """
        Retrieve the electric field vectors for the given particles in the lab frame.
        The electric field is evaluated at each particle's position and for
        the current simulation time.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`

        Returns
        -------
        electric_field : :class:`~np.ndarray`, shape (3, N)
            The electric field vectors as column vectors; that is the shape of the returned array
            is `(3, N)` for `N` given particles and ``electric_field[0]`` returns the x-component
            of the electric field for each particle; the electric field is given
            in units of [V/m] in the lab frame.
        """
        return self._em_fields.electric_field_at(particles.position_four_vector, progress)

    def magnetic_field_for(self, particles, progress):
        """
        Retrieve the magnetic field vectors for the given particles in the lab frame.
        The magnetic field is evaluated at each particle's position and for
        the current simulation time.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`

        Returns
        -------
        magnetic_field : :class:`~np.ndarray`, shape (3, N)
            The magnetic field vectors as column vectors; that is the shape of the returned array
            is `(3, N)` for `N` given particles and ``magnetic_field[0]`` returns the x-component
            of the magnetic field for each particle; the magnetic field is given
            in units of [T] in the lab frame.
        """
        return self._em_fields.magnetic_field_at(particles.position_four_vector, progress)

    def initialize(self, particles, progress):
        """
        Initialize the positions and momenta of the given particles. After initialization
        the particles must be in state in which they can be propagated.
        By default this method is a no-op.

        ..note::
        Particles are generated with an initial position and momentum which both refer to
        the same simulation step. If that's what your model needs then you don't need to override
        this method.
        Some tracking models however require the position being shifted by half a time step versus
        the momentum for example. Such an initial shift should be performed during this method.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
        """
        pass

    @abc.abstractmethod
    def propagate(self, particles, progress):
        """
        Update the positions and momenta of the given particles at the current simulation step.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
        """
        raise NotImplementedError

Interface = ParticleTrackingModel


class RungeKutta4(ParticleTrackingModel):
    """
    Particle tracking using the Runge-Kutta method of 4th order for solving
    the equations of motion.

    .. note::
       The simulation time step should be significantly shorter than the cyclotron period of
       particles.
       
    .. note::
       Only non-relativistic velocities are valid.
    """

    @injector.inject(
        em_fields=di.components.em_fields,
        setup=di.components.setup
    )
    def __init__(self, em_fields, setup):
        """
        Initialize the Runge-Kutta model.

        Parameters
        ----------
        em_fields : :class:`EMFieldsCollector`
        setup : :class:`Setup`
        """
        super().__init__(em_fields)
        self.dt = setup.time_delta

    # noinspection PyPep8Naming
    @use_docs_from(ParticleTrackingModel)
    def propagate(self, particles, progress):
        dt = self.dt

        posi = particles.position
        velo = particles.momentum / particles.mass
        qm = particles.charge / particles.mass

        E = self.electric_field_for(particles, progress)
        B = self.magnetic_field_for(particles, progress)

        # Shouldn't we request separate field values for each updated position posi + k_i?
        # Or is this left out for performance reasons?

        k_0 = dt * velo
        m_0 = dt * qm * (E + np.cross(velo, B, axis=0))
        velo_2 = velo + m_0 / 2.

        k_1 = dt * velo_2
        m_1 = dt * qm * (E + np.cross(velo_2, B, axis=0))
        velo_2 = velo + m_1 / 2.

        k_2 = dt * velo_2
        m_2 = dt * qm * (E + np.cross(velo_2, B, axis=0))
        velo_2 = velo + m_2

        k_3 = dt * velo_2
        m_3 = dt * qm * (E + np.cross(velo_2, B, axis=0))

        posi += (k_0 + 2.0 * k_1 + 2.0 * k_2 + k_3) / 6.0
        velo += (m_0 + 2.0 * m_1 + 2.0 * m_2 + m_3) / 6.0

        particles.position = posi
        particles.momentum = velo * particles.mass


@depends_on(
    RungeKutta4
)
class Boris(ParticleTrackingModel):
    """
    Implementation of the particle-in-cell algorithm after Boris.
    
    The :class:`RungeKutta4` model is used to initialize particles' positions and momenta;
    the Boris algorithm requires position and velocity of particles being shifted by half
    a time step. This is achieved by bootstrapping with the Runge-Kutta model.
    
    .. note::
       Only non-relativistic velocities are valid.

    References
    ----------
    .. [1] J.P.Boris, "Relativistic plasma simulation-optimization of a hybrid code",
       Proceedings of the 4th Conference on Numerical Simulation of Plasmas, 1970 [pp. 3-67]
    """

    @injector.inject(
        em_fields=di.components.em_fields,
        setup=di.components.setup
    )
    def __init__(self, em_fields, setup):
        """
        Initialize the Boris model. This involves the creating a Runge-Kutta model which is used to
        initialize particles later on.

        Parameters
        ----------
        em_fields : :class:`EMFieldsCollector`
        setup : :class:`Setup`
        """
        super().__init__(em_fields)
        self.dt = setup.time_delta

        class RK4Setup:
            def __getattr__(self, item):
                return getattr(setup, item)

            @property
            def time_delta(self):
                # Need to propagate momentum backwards in time by half a time step.
                return -1.0 * setup.time_delta / 2.

        self.runge_kutta = RungeKutta4(em_fields, RK4Setup())

    def prepare(self):
        """
        Prepare the Runge-Kutta model which is used to initialize particles later on.
        """
        super().prepare()
        self.runge_kutta.prepare()

    def initialize(self, particles, progress):
        """
        Use the Runge-Kutta model to shift position and momentum of particles by half a time step
        (momentum is shifted half a time step backwards).

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
        """
        position = particles.position.copy()
        self.runge_kutta.propagate(particles, progress)
        particles.position = position

    # noinspection PyPep8Naming
    @use_docs_from(ParticleTrackingModel)
    def propagate(self, particles, progress):
        position, momentum = particles.position, particles.momentum
        charge, mass = particles.charge, particles.mass

        electric_field = self.electric_field_for(particles, progress)
        magnetic_field = self.magnetic_field_for(particles, progress)

        x, v = position, momentum / mass
        E, B = electric_field, magnetic_field

        q_prime = self.dt * charge / (2 * mass)
        h = q_prime * B
        # Perform the dot product for each magnetic field vector in h.
        # This is the diagonal of the matrix product.
        # Works only for 2d-arrays.
        # s = 2 * h / (1 + np.einsum('ij, ji -> i', h.T, h))
        # Is slower than einsum.
        # s = 2 * h / (1 + np.linalg.norm(h, axis=0)**2)
        # This is the fastest solution; works for 1d- and 2d-arrays thanks to the ellipsis `...`.
        # noinspection PyTypeChecker
        s = 2 * h / (1 + np.einsum('i...,i... ->...', h, h))
        u = v + q_prime * E
        # noinspection PyTypeChecker
        u_prime = u + np.cross(u + np.cross(u, h, axis=0), s, axis=0)

        new_velocity = u_prime + q_prime * E
        new_position = x + self.dt * new_velocity

        particles.position = new_position
        particles.momentum = new_velocity * mass


class RadialFields(ParticleTrackingModel):
    """
    This particle tracking model is for the specific case ``Ez = Bz = 0``. It is based on
    an analytical solution of the equations of motion and thus is faster compared to other models
    which solve the e.q.m. numerically "live". Also the time step can be of the order of magnitude
    of the cyclotron period of tracked particles.
    
    .. note::
       Only non-relativistic velocities are valid.

    References
    ----------
    .. [1] G.Iadarola: "Electron Cloud Studies For CERN Particle Accelerators and
       Simulation Code Development", CERN-THESIS-2014-047, chapter 2.8 (pp.34-38)
    """

    @injector.inject(
        em_fields=di.components.em_fields,
        setup=di.components.setup,
        configuration=di.components.configuration
    )
    def __init__(self, em_fields, setup, configuration=None):
        super().__init__(em_fields, configuration)
        self.dt = setup.time_delta

    # noinspection PyPep8Naming
    @use_docs_from(ParticleTrackingModel)
    def propagate(self, particles, progress):
        dt = self.dt

        posi = particles.position
        velo = particles.momentum / particles.mass

        E = self.electric_field_for(particles, progress)
        B = self.magnetic_field_for(particles, progress)
        qm = abs(particles.charge) / particles.mass

        Btot = np.sqrt(B[0] ** 2 + B[1] ** 2)
        # Cyclotron frequency
        omegac = abs(particles.charge) * Btot / particles.mass

        # Eq.(2.62)
        veloz = (
            velo[2] * np.cos(omegac * dt)
            - ((B[1] * velo[0] - B[0] * velo[1]) * np.sin(omegac * dt) / Btot)
            + (B[1] * E[0] - B[0] * E[1]) * (1.0 - np.cos(omegac * dt) / Btot**2)
        )

        # Eq.(2.63)
        posiz = (
            posi[2]
            + (velo[2] * np.sin(omegac * dt) / omegac)
            + (
                (B[1] * velo[0] - B[1] * velo[0])
                * (np.cos(omegac * dt) - 1.0)
                / (Btot * omegac))
            + ((B[1] * E[0] - B[0] * E[1]) * (dt - (np.sin(omegac * dt) / omegac)) / Btot**2)
        )

        # Eq.(2.64a+b)
        velox = (
            velo[0]
            - qm * (E[0] * dt - B[1] * (posiz - posi[2]))
        )
        veloy = (
            velo[1]
            - qm * (E[1] * dt - B[0] * (posiz - posi[2]))
        )

        # Eq.(2.65); zp is an auxiliary quantity.
        zp = (
            velo[2] * (1.0 - np.cos(omegac * dt)) / omegac**2
            + (
                ((B[1] * velo[0] - B[0] * velo[1]) / (Btot * omegac))
                * (np.sin(omegac * dt) / omegac - dt)
            )
            + (
                ((B[1] * E[0] - B[0] * E[1]) / Btot**2)
                * (0.5 * dt ** 2 + ((np.cos(omegac * dt) - 1.0) / omegac**2))
            )
        )

        # Eq.(2.66a+b)
        posix = (
            posi[0]
            + velo[0] * dt
            - qm * (0.5 * E[0] * dt ** 2 - B[1] * zp)
        )
        posiy = (
            posi[1]
            + velo[1] * dt
            - qm * (0.5 * E[1] * dt ** 2 - B[0] * zp)
        )

        particles.position = np.array([posix, posiy, posiz])
        particles.momentum = np.array([velox, veloy, veloz]) * particles.mass

# Delete the model because it contains a known bug (see #174). When the bug has been resolved the
# model can be enabled again.
del RadialFields


@parametrize(
    PhysicalQuantity(
        'MagneticFieldStrengthInY',
        unit='T',
        info='This tracking model is only valid for a constant, uniform magnetic field pointing '
             'in y-direction. The corresponding field strength is used to pre-compute the '
             'particles gyro-frequency and several other related quantities in order to increase '
             'efficiency.'
    )
)
class RadialFieldsBx0(ParticleTrackingModel):
    """
    This particle tracking model is for the specific case ``Ez = Bz = Bx = 0``  (while ``By`` must
    point in negative y-direction).
    It is based on an analytical solution of the equations of motion and thus is faster compared to
    other models which solve the e.q.m. numerically "live". Also the time step can be of the order
    of magnitude of the cyclotron period of tracked particles.
    
    .. note::
       Only non-relativistic velocities are valid.

    References
    ----------
    .. [1] PyECLOUD-BGI: ``dynamics.dyn_stp_vect2`` (G.Iadarola)
    """

    @injector.inject(
        em_fields=di.components.em_fields,
        setup=di.components.setup,
        configuration=di.components.configuration
    )
    def __init__(self, em_fields, setup, configuration):
        super().__init__(em_fields, configuration)
        self._setup = setup

        self.omegac = None
        self.qm = None
        self.dt = None

        self.sincc_v = None
        self.cosincc_v = None
        self.cubsincc_v = None
        self.sin_v = None
        self.cos_v = None

    # noinspection PyPep8Naming
    def prepare(self):
        """
        Pre-compute several quantities that are reused during propagation.
        """
        super().prepare()
        B = self._magnetic_field_strength_in_y
        charge, mass = self._setup.particle_type.charge, self._setup.particle_type.mass

        self.omegac = abs(charge) * B / mass
        self.qm = abs(charge) / mass
        self.dt = self._setup.time_delta

        self.sincc_v = sincc(self.omegac * self.dt)
        self.cosincc_v = cosincc(self.omegac * self.dt)
        self.cubsincc_v = cubsincc(self.omegac * self.dt)
        self.sin_v = np.sin(self.omegac * self.dt)
        self.cos_v = np.cos(self.omegac * self.dt)

    # noinspection PyPep8Naming
    @use_docs_from(ParticleTrackingModel)
    def propagate(self, particle, progress):
        qm = self.qm
        omegac = self.omegac
        dt = self.dt
        sin_v, cos_v = self.sin_v, self.cos_v
        sincc_v, cosincc_v, cubsincc_v = self.sincc_v, self.cosincc_v, self.cubsincc_v

        Ex, Ey, _ = self.electric_field_for(particle, progress)
        x, y, z = particle.position
        vx, vy, vz = particle.momentum / particle.mass

        xn1 = (
            x
            + vx * sincc_v * dt
            + vz * cosincc_v * omegac * dt**2
            - qm * Ex * cosincc_v * dt**2
        )
        yn1 = (
            y
            + vy * dt
            - 0.5 * qm * Ey * dt**2
        )
        zn1 = (
            z
            + vz * sincc_v * dt
            - vx * cosincc_v * omegac * dt**2
            + qm * Ex * cubsincc_v * omegac * dt**3
        )

        vxn1 = (
            vx * cos_v
            + vz * sin_v
            - qm * Ex * sincc_v * dt
        )
        vyn1 = (
            vy
            - qm * Ey * dt
        )
        vzn1 = (
            vz * cos_v
            - vx * sin_v
            + qm * Ex * cosincc_v * omegac * dt**2
        )

        particle.position = np.array([xn1, yn1, zn1])
        particle.momentum = np.array([vxn1, vyn1, vzn1]) * particle.mass
