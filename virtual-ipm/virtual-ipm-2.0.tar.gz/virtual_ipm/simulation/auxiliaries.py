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

from argparse import Namespace
import logging

import injector
import numpy as np
from rx.subjects import Subject
import scipy.constants as constants

import virtual_ipm.di as di
from virtual_ipm.utils import to_json_string


class Particle:
    # noinspection PyUnresolvedReferences
    """
    This class represents a particle that is tracked throughout the simulation. Particle data is
    stored in one common pool and a ``Particle`` instance is a view onto one such element,
    uniquely identified by its id.

    Particles can have different statuses depending on their situation during the simulation:

      * IDLE: The particle's data has been allocated but not initialized yet.
      * QUEUED: The particle's data has been initialized and it is queued for tracking.
      * TRACKED: The particle is currently being tracked.
      * DETECTED: The particle has stopped tracking by reaching a detecting element.
      * INVALID: The particle has stopped tracking without being detected (e.g. hit the chamber).
      
    Attributes
    ----------
    charge
    mass
    particle_type
    time
    x
    y
    z
    px
    py
    pz
    previous_x
    previous_y
    previous_z
    previous_px
    previous_py
    previous_pz
    position
    position_four_vector
    momentum
    previous_position
    previous_momentum
    status
    status_as_string
    is_detected
    is_idle
    is_invalid
    is_queued
    is_tracked
    uuid
    relativistic_gamma
    """

    _statuses = [
        'IDLE',
        'QUEUED',
        'TRACKED',
        'DETECTED',
        'INVALID',
    ]
    Status = Namespace(**{s: i for i, s in enumerate(_statuses)})

    def __init__(self, pool, uuid):
        """
        Parameters
        ----------
        pool : :class:`ParticlePool`
        uuid : int
        """
        super().__init__()
        self._charge = pool.particle_type.charge
        self._mass = pool.particle_type.mass
        self._particle_type = pool.particle_type
        self._pool = pool
        self._uuid = uuid

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        """
        Retrieve a JSON serializable representation of this component.

        Returns
        -------
        json : dict
        """
        return {
            'position': self.position.tolist(),
            'momentum': self.momentum.tolist(),
            'previous position': self.previous_position.tolist(),
            'previous momentum': self.previous_momentum.tolist(),
            'status': str(self.status),
            'uuid': str(self.uuid),
            'relativistic gamma': self.relativistic_gamma,
        }

    @property
    def charge(self):
        """
        Returns
        -------
        charge : float
            In units of [C].
        """
        return self._charge

    @property
    def mass(self):
        """
        Returns
        -------
        mass : float
            In units of [kg].
        """
        return self._mass

    @property
    def particle_type(self):
        """
        Returns
        -------
        particle_type : :class:`ParticleType`
        """
        return self._particle_type

    @property
    def time(self):
        """
        Returns
        -------
        time : float
            The particle's current simulation time multiplied by the speed of light,
            in units of [m].
        """
        return self._pool.position_four_vectors[0, self._uuid]

    @time.setter
    def time(self, value):
        self._pool.position_four_vectors[0, self._uuid] = value

    @property
    def x(self):
        """
        The x-component of the particle's position.

        Returns
        -------
        x : float
            In units of [m].
        """
        return self._pool.position_four_vectors[1, self._uuid]

    @property
    def y(self):
        """
        The y-component of the particle's position.

        Returns
        -------
        y : float
            In units of [m].
        """
        return self._pool.position_four_vectors[2, self._uuid]

    @property
    def z(self):
        """
        The z-component of the particle's position.

        Returns
        -------
        z : float
            In units of [m].
        """
        return self._pool.position_four_vectors[3, self._uuid]

    @property
    def px(self):
        """
        The x-component of the particle's momentum.

        Returns
        -------
        px : float
            In units of [kg*m/s].
        """
        return self._pool.momenta[0, self._uuid]

    @property
    def py(self):
        """
        The y-component of the particle's momentum.

        Returns
        -------
        py : float
            In units of [kg*m/s].
        """
        return self._pool.momenta[1, self._uuid]

    @property
    def pz(self):
        """
        The z-component of the particle's momentum.

        Returns
        -------
        pz : float
            In units of [kg*m/s].
        """
        return self._pool.momenta[2, self._uuid]

    @property
    def previous_x(self):
        """
        The x-component of the particle's previous position (that is the position one time step
        prior to the one obtained via :method:`~Particle.position`).

        Returns
        -------
        previous_x : float
            In units of [m].
        """
        return self._pool.previous_positions[0, self._uuid]

    @property
    def previous_y(self):
        """
        The y-component of the particle's previous position (that is the position one time step
        prior to the one obtained via :method:`~Particle.position`).

        Returns
        -------
        previous_y : float
            In units of [m].
        """
        return self._pool.previous_positions[1, self._uuid]

    @property
    def previous_z(self):
        """
        The z-component of the particle's previous position (that is the position one time step
        prior to the one obtained via :method:`~Particle.position`).

        Returns
        -------
        previous_z : float
            In units of [m].
        """
        return self._pool.previous_positions[2, self._uuid]

    @property
    def previous_px(self):
        """
        The x-component of the particle's previous momentum (that is the momentum one time step
        prior to the one obtained via :method:`~Particle.momentum`).

        Returns
        -------
        previous_px : float
            In units of [kg*m/s].
        """
        return self._pool.previous_momenta[0, self._uuid]

    @property
    def previous_py(self):
        """
        The y-component of the particle's previous momentum (that is the momentum one time step
        prior to the one obtained via :method:`~Particle.momentum`).

        Returns
        -------
        previous_py : float
            In units of [kg*m/s].
        """
        return self._pool.previous_momenta[1, self._uuid]

    @property
    def previous_pz(self):
        """
        The z-component of the particle's previous momentum (that is the momentum one time step
        prior to the one obtained via :method:`~Particle.momentum`).

        Returns
        -------
        previous_pz : float
            In units of [kg*m/s].
        """
        return self._pool.previous_momenta[2, self._uuid]

    @property
    def position(self):
        """
        Returns
        -------
        position : :class:`~np.ndarray`, shape (3,)
            In units of [m].
        """
        return self._pool.position_four_vectors[1:, self._uuid]

    @position.setter
    def position(self, value):
        self._pool.previous_positions[:, self._uuid] = \
            self._pool.position_four_vectors[1:, self._uuid]
        self._pool.position_four_vectors[1:, self._uuid] = value

    @property
    def position_four_vector(self):
        """
        The first component refers to the (simulation) time component multiplied by the speed
        of light and the last three components refer to the particle's spatial position.

        Returns
        -------
        position_four_vector : :class:`~np.ndarray`, shape (4,)
            In units of [m].
        """
        return self._pool.position_four_vectors[:, self._uuid]

    @property
    def momentum(self):
        """
        Returns
        -------
        momentum : :class:`~np.ndarray`, shape (3,)
            In units of [kg*m/s].
        """
        return self._pool.momenta[:, self._uuid]

    @momentum.setter
    def momentum(self, value):
        self._pool.previous_momenta[:, self._uuid] = self._pool.momenta[:, self._uuid]
        self._pool.momenta[:, self._uuid] = value

    @property
    def previous_position(self):
        """
        The position one time step prior to the one obtained via :method:`~Particle.position`.

        Returns
        -------
        previous_position : :class:`~np.ndarray`, shape (3,)
            In units of [m].
        """
        return self._pool.previous_positions[:, self._uuid]

    @property
    def previous_momentum(self):
        """
        The momentum one time step prior to the one obtained via :method:`~Particle.momentum`.

        Returns
        -------
        previous_momentum : :class:`~np.ndarray`, shape (3,)
            In units of [kg*m/s].
        """
        return self._pool.previous_momenta[:, self._uuid]

    @property
    def status(self):
        """
        The particle's current status.

        Returns
        -------
        status : Particle.Status
        """
        # ParticlePool returns only attributes for particles that have been created already (for
        # reasons of optimization). So when using Particle instances for access by UUID it might
        # be the case that it tries to access a region which is not provided by the particle pool.
        # This is only relevant for the status because before trying to obtain other attributes
        # such as position or momentum one should always check the particle's status first (and
        # verify it's not IDLE).
        try:
            return self._pool.statuses[self._uuid]
        except IndexError:
            return self.Status.IDLE

    @status.setter
    def status(self, value):
        self._pool.statuses[self._uuid] = value

    @property
    def status_as_string(self):
        """
        The particle's current status as string.

        Returns
        -------
        status : unicode
        """
        return self._statuses[self._pool.statuses[self._uuid]]

    @property
    def is_detected(self):
        """
        Returns
        -------
        is_detected : bool
            True if the particle has status ``DETECTED``, False otherwise
        """
        return self.status == Particle.Status.DETECTED

    @property
    def is_idle(self):
        """
        Returns
        -------
        is_idle : bool
            True if the particle has status ``IDLE``, False otherwise
        """
        return self.status == Particle.Status.IDLE

    @property
    def is_invalid(self):
        """
        Returns
        -------
        is_invalid : bool
            True if the particle has status ``INVALID``, False otherwise
        """
        return self.status == Particle.Status.INVALID

    @property
    def is_queued(self):
        """
        Returns
        -------
        is_queued : bool
            True if the particle has status ``QUEUED``, False otherwise
        """
        return self.status == Particle.Status.QUEUED

    @property
    def is_tracked(self):
        """
        Returns
        -------
        is_tracked : bool
            True if the particle has status ``TRACKED``, False otherwise
        """
        return self.status == Particle.Status.TRACKED

    @property
    def uuid(self):
        """
        The unique identifier of the particle which is the index pointing to the particle's
        data in the pool.

        Returns
        -------
        uuid : int
        """
        return self._uuid

    @property
    def relativistic_gamma(self):
        """
        The particle's current relativistic gamma factor.

        Returns
        -------
        relativistic_gamma : float
        """
        return np.sqrt(
            1. + np.dot(self.momentum, self.momentum) / (self.mass * constants.c) ** 2
        )


class ParticleIndexView:
    # noinspection PyUnresolvedReferences
    """
    This class represents a group of particles. It is similarly a view onto the common data pool
    but using an index array instead of a single (scalar) index. This class exhibits similar
    properties as :class:`Particle` with the difference that the return values are 1d-arrays
    where the corresponding property of `Particle` returns a scalar and 2d-arrays where the
    corresponding property of `Particle` returns a 1d-array. Numpy's broadcasting rules apply,
    meaning that if a value is the same for all particles a scalar can equally be returned.
    2d-arrays represent vector properties of multiple particles and are arranged such that
    the attributes (per particle) are stored as column vectors. That is ``vector_property[0]``
    gives the first element of the property for all particles.

    This class provides the following additional functionality:

      * Test whether a particle is part of the view, see :method:`~ParticleIndexView.__contains__`.
      * Iterate over the view yielding a :class:`Particle` instance for each element of the view,
        see :method:`~ParticleIndexView.__iter__`.
      * Retrieve a subset of the view, see :method:`~ParticleIndexView.__getitem__`.
      * Retrieve the number of elements in the view, see :method:`~ParticleIndexView.__len__`.
      
    Attributes
    ----------
    charge
    mass
    particle_type
    time
    x
    y
    z
    px
    py
    pz
    previous_x
    previous_y
    previous_z
    previous_px
    previous_py
    previous_pz
    position
    position_four_vector
    momentum
    previous_position
    previous_momentum
    status
    status_as_string
    is_detected
    is_idle
    is_invalid
    is_queued
    is_tracked
    uuid
    relativistic_gamma

    Examples
    --------
    Retrieving the positions of all particles:

    >>> index_view.position
    [[ x_1  x_2  ...  x_n ],
     [ y_1  y_2  ...  y_n ],
     [ z_1  z_2  ...  z_n ]]
    """
    def __init__(self, pool, index_mask):
        """
        Parameters
        ----------
        pool : :class:`ParticlePool`
        index_mask : :class:`np.ndarray`
            Containing the indices of elements of `pool` which are part of this view. 
        """
        super().__init__()
        self._charge = pool.particle_type.charge
        self._mass = pool.particle_type.mass
        self._particle_type = pool.particle_type
        self._pool = pool
        self._index_mask = index_mask

    def __contains__(self, particle):
        """
        Test whether the given particle is part of the view.

        Parameters
        ----------
        particle : :class:`Particle`

        Returns
        -------
        bool
            True if the particle is part of the view, False otherwise.
        """
        return particle.uuid in self._mask

    def __iter__(self):
        """
        Iterate over the view yielding a :class:`Particle` instance for each element. In a sense
        the group view is collapsed into an iterable of single element views.

        Returns
        -------
        iterator[:class:`Particle`]
            Providing the single element views.
        """
        for index in self._mask:
            yield Particle(self._pool, index)

    def __getitem__(self, mask):
        # noinspection PyUnresolvedReferences
        """
        Retrieve a subset of this view. This is achieved by providing an index array as a mask.

        .. note::
        Usually such an index array should not be created manually but rather by subjecting
        this view to some condition (see examples).

        Parameters
        ----------
        mask : :class:`~np.ndarray`
            Contains the indices of particles to be selected from this view.

        Returns
        -------
        subset : :class:`ParticleIndexView`
            Contains the specified subset of particles.

        Examples
        --------
        Retrieve all particles of the view whose x-component of position is greater than zero:

        >>> x_gt_0_view = view[view.x > 0.]

        Retrieve all particles of the view that have positions greater than zero:

        >>> pos_gt_0_view = view[view.position > 0.]
        """
        return ParticleIndexView(self._pool, self._mask[mask])

    def __len__(self):
        """
        Returns
        -------
        int
            The number of particles that are part of this view.
        """
        return len(self._mask)

    def __nonzero__(self):
        """
        Returns
        -------
        bool
            True if the view contains at least one particle, False otherwise.
        """
        return len(self._mask) > 0

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        """
        Retrieve a JSON serializable representation of this component.

        Returns
        -------
        json : dict
        """
        return {
            '__class__': self.__class__.__name__,
            'index_mask': self._mask.tolist(),
        }

    @property
    def _mask(self):
        return self._index_mask

    @property
    def charge(self):
        return self._charge

    @property
    def mass(self):
        return self._mass

    @property
    def particle_type(self):
        return self._particle_type

    @property
    def time(self):
        return self._pool.position_four_vectors[0, self._mask]

    @time.setter
    def time(self, value):
        self._pool.position_four_vectors[0, self._mask] = value

    @property
    def x(self):
        return self._pool.position_four_vectors[1, self._mask]

    @property
    def y(self):
        return self._pool.position_four_vectors[2, self._mask]

    @property
    def z(self):
        return self._pool.position_four_vectors[3, self._mask]

    @property
    def px(self):
        return self._pool.momenta[0, self._mask]

    @property
    def py(self):
        return self._pool.momenta[1, self._mask]

    @property
    def pz(self):
        return self._pool.momenta[2, self._mask]

    @property
    def previous_x(self):
        return self._pool.previous_positions[0, self._mask]

    @property
    def previous_y(self):
        return self._pool.previous_positions[1, self._mask]

    @property
    def previous_z(self):
        return self._pool.previous_positions[2, self._mask]

    @property
    def previous_px(self):
        return self._pool.previous_momenta[0, self._mask]

    @property
    def previous_py(self):
        return self._pool.previous_momenta[1, self._mask]

    @property
    def previous_pz(self):
        return self._pool.previous_momenta[2, self._mask]

    @property
    def position(self):
        return self._pool.position_four_vectors[1:, self._mask]

    @position.setter
    def position(self, values):
        self._pool.previous_positions[:, self._mask] = \
            self._pool.position_four_vectors[1:, self._mask]
        self._pool.position_four_vectors[1:, self._mask] = values

    @property
    def position_four_vector(self):
        return self._pool.position_four_vectors[:, self._mask]

    @property
    def momentum(self):
        return self._pool.momenta[:, self._mask]

    @momentum.setter
    def momentum(self, values):
        self._pool.previous_momenta[:, self._mask] = self._pool.momenta[:, self._mask]
        self._pool.momenta[:, self._mask] = values

    @property
    def previous_position(self):
        return self._pool.previous_positions[:, self._mask]

    @property
    def previous_momentum(self):
        return self._pool.previous_momenta[:, self._mask]

    @property
    def status(self):
        return self._pool.statuses[self._mask]

    @status.setter
    def status(self, values):
        self._pool.statuses[self._mask] = values

    @property
    def is_detected(self):
        return self._pool.statuses[self._mask] == Particle.Status.DETECTED

    @property
    def is_idle(self):
        return self._pool.statuses[self._mask] == Particle.Status.IDLE

    @property
    def is_invalid(self):
        return self._pool.statuses[self._mask] == Particle.Status.INVALID

    @property
    def is_queued(self):
        return self._pool.statuses[self._mask] == Particle.Status.QUEUED

    @property
    def is_tracked(self):
        return self._pool.statuses[self._mask] == Particle.Status.TRACKED

    @property
    def uuid(self):
        return self._mask

    @property
    def relativistic_gamma(self):
        return np.sqrt(
            1. + np.einsum(
                'ij, ji -> i', self.momentum.T, self.momentum
            ) / (self.mass * constants.c) ** 2
        )


class ParticleStatusView(ParticleIndexView):
    """
    This class represents a group of particles that all have the same status. This is
    a :method:`ParticleIndexView`` with the index mask emerging from the condition
    "those particles whose status is equal to the specified status of the view".
    """

    def __init__(self, pool, status):
        """
        Parameters
        ----------
        pool : ParticlePool
        status : Particle.Status
            All particles that have this status are part of this view. 
        """
        super().__init__(pool, None)
        self._status = status

    def __contains__(self, particle):
        return particle.status == self._status

    def as_json(self):
        """
        Retrieve a JSON serializable representation of this component.

        Returns
        -------
        json : dict
        """
        return dict(
            super().as_json(),
            status=self._status
        )

    # Override _mask in order to provide a mask that can dynamically change with the statuses of
    # particles.
    @property
    def _mask(self):
        return np.where(self._pool.statuses == self._status)[0]

    @property
    def is_detected(self):
        return self._status == Particle.Status.DETECTED

    @property
    def is_idle(self):
        return self._status == Particle.Status.IDLE

    @property
    def is_invalid(self):
        return self._status == Particle.Status.INVALID

    @property
    def is_queued(self):
        return self._status == Particle.Status.QUEUED

    @property
    def is_tracked(self):
        return self._status == Particle.Status.TRACKED


class ParticlePool:
    # noinspection PyUnresolvedReferences
    """
    Common storage for all particle data.

    .. warning::
    A pool has a maximum number particles which it can represent; this number is specified upon
    initialization. If the maximum number is exceeded by creating more particles the pool will
    resize its resources in order to fit additional particles. This is a costly operation and
    thus should be avoided. Choosing the pool large enough from the beginning is more efficient.
    
    Attributes
    ----------
    particle_type
    statuses
    position_four_vectors
    momenta
    previous_positions
    previous_momenta
    """

    log = logging.getLogger('{0}.{1}'.format(__name__, 'ParticlePool'))

    def __init__(self, particle_type, count):
        """
        Parameters
        ----------
        particle_type : :class:`ParticleType`
            All particles within this pool have this type.
        count : int
            The number of particles for which data is allocated.
        """
        super().__init__()
        self._particle_type = particle_type
        self._number_of_particles = 0
        self._count = count
        self._statuses = np.array([Particle.Status.IDLE] * count)
        self._position_four_vectors = np.zeros((4, count), dtype=float)
        self._momenta = np.zeros((3, count), dtype=float)
        self._previous_positions = np.zeros((3, count), dtype=float)
        self._previous_momenta = np.zeros((3, count), dtype=float)

        self.log.debug('Initialized particle pool with %d particles', count)

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        """
        Retrieve a JSON serializable representation of this component.

        Returns
        -------
        json : dict
        """
        return {
            'particle type': self._particle_type.as_json(),
            'pool size': self._count,
            'occupied': self._number_of_particles,
        }

    @property
    def particle_type(self):
        """
        Returns
        -------
        particle_type : :class:`ParticleType`
        """
        return self._particle_type

    @property
    def statuses(self):
        """
        Returns
        -------
        statuses : :class:`~np.ndarray`, shape (N,)
            Contains the status of each particle.
        """
        return self._statuses[:self._number_of_particles]

    @property
    def position_four_vectors(self):
        """
        Returns
        -------
        position_four_vectors : :class:`~np.ndarray`, shape (4, N)
            Positions are column vectors of shape (4,), one column vector per particle.
        """
        return self._position_four_vectors[:, :self._number_of_particles]

    @property
    def momenta(self):
        """
        Returns
        -------
        momenta : :class:`~np.ndarray`, shape (3, N)
            Momenta are column vectors of shape (3,), one column vector per particle.
        """
        return self._momenta[:, :self._number_of_particles]

    @property
    def previous_positions(self):
        """
        Returns
        -------
        previous_positions : :class:`~np.ndarray`, shape (3, N)
            Previous positions are column vectors of shape (3,), one column vector per particle.
        """
        return self._previous_positions[:, :self._number_of_particles]

    @property
    def previous_momenta(self):
        """
        Returns
        -------
        momenta : :class:`~np.ndarray`, shape (3, N)
            Previous momenta are column vectors of shape (3,), one column vector per particle.
        """
        return self._previous_momenta[:, :self._number_of_particles]

    def create_particle(self, position=None, momentum=None):
        """
        Initializes the position and momentum of the next unused particle in the pool and
        returns a view onto it. If the pool doesn't contain any free particles it will resize
        it's resources through increasing storage by 10%.

        Parameters
        ----------
        position : :class:`~np.ndarray` or list or tuple, optional
            Must provide 3 elements which are used to initialize the spatial position;
            if omitted then the position is initialized with zeros.
        momentum : :class:`~np.ndarray` or list or tuple, optional
            Must provide 3 elements which are used to initialize the momentum;
            if omitted then the momentum is initialized with zeros.

        Returns
        -------
        particle : :class:`Particle`
            A view onto the created element.
        """
        # Check if resizing is necessary.
        if self._number_of_particles == self._count:
            self.log.warning(
                'Exceeding size of particle pool; additional storage will be allocated'
            )
            self._resize()
        if position is not None:
            self._position_four_vectors[1:, self._number_of_particles] = position
        if momentum is not None:
            self._momenta[:, self._number_of_particles] = momentum
        self._number_of_particles += 1
        return Particle(self, self._number_of_particles-1)

    def _resize(self):
        """
        Resize the pool's storage by 10%.
        """
        # Increase by 10%.
        count_increment = int(0.1 * self._count)
        self._count += count_increment
        self._statuses = np.r_[
            self._statuses,
            np.array([Particle.Status.IDLE] * count_increment)
        ]
        self._position_four_vectors = np.c_[
            self._position_four_vectors,
            np.zeros((4, count_increment), dtype=float)
        ]
        self._momenta = np.c_[
            self._momenta,
            np.zeros((3, count_increment), dtype=float)
        ]
        self._previous_positions = np.c_[
            self._previous_positions,
            np.zeros((3, count_increment), dtype=float)
        ]
        self._previous_momenta = np.c_[
            self._previous_momenta,
            np.zeros((3, count_increment), dtype=float)
        ]


class ParticleSupervisor:
    # noinspection PyUnresolvedReferences
    """
    This class manages all particles that take place in the simulation. It provides a method for
    creating new particles as well as methods for retrieving particles of a particular status and
    for modifying the status of particles.
    
    Attributes
    ----------
    detected_particles
    idle_particles
    invalid_particles
    queued_particles
    tracked_particles
    status_updates
    """

    log = logging.getLogger('{0}.{1}'.format(__name__, 'ParticleSupervisor'))

    class StatusUpdate:
        """
        Information about a particle having changed its status.

        Attributes
        ----------
        particle : :class:`Particle`
        old_status : Particle.Status
        progress : :class:`Progress`
        """
        def __init__(self, particle, old_status, progress):
            """
            Parameters
            ----------
            particle : :class:`Particle`
            old_status : Particle.Status
            progress : :class:`Progress`
            """
            self.particle = particle
            self.old_status = old_status
            self.progress = progress

    @injector.inject(setup=di.components.setup)
    def __init__(self, setup):
        """
        Parameters
        ----------
        setup : :class:`Setup`
        """
        super().__init__()

        # Choose the maximum number of particles 1% larger than the actual number of particles to
        # be simulated but not less than 100 larger. This number is used to allocate resources in
        # the particle pool and if the number of simulated particles exceed this limit during the
        # simulation it will lead to resource reallocation which slows down the simulation.
        # Therefore we choose the number to be large enough in the beginning.
        maximum_number_of_particles = (
            setup.number_of_particles
            + int(max(100., 0.01*setup.number_of_particles))
        )
        self._pool = ParticlePool(setup.particle_type, maximum_number_of_particles)
        self._status_updates = Subject()
        self._groups = {
            getattr(Particle.Status, status):
                ParticleStatusView(
                    self._pool,
                    getattr(Particle.Status, status)
                )
            for status in Particle._statuses
            }
        self.log.debug(
            'Supervising max. %d particles of type %s',
            maximum_number_of_particles,
            setup.particle_type
        )

    def __str__(self):
        return to_json_string(self.as_json())

    @property
    def detected_particles(self):
        """
        Retrieve all particles that have status ``DETECTED``.

        Returns
        -------
        detected_particles : :class:`ParticleStatusView`
        """
        return self._groups[Particle.Status.DETECTED]

    @property
    def idle_particles(self):
        """
        Retrieve all particles that have status ``IDLE``.

        Returns
        -------
        idle_particles : :class:`ParticleStatusView`
        """
        return self._groups[Particle.Status.IDLE]

    @property
    def invalid_particles(self):
        """
        Retrieve all particles that have status ``INVALID``.

        Returns
        -------
        invalid_particles : :class:`ParticleStatusView`
        """
        return self._groups[Particle.Status.INVALID]

    @property
    def queued_particles(self):
        """
        Retrieve all particles that have status ``QUEUED``.

        Returns
        -------
        queued_particles : :class:`ParticleStatusView`
        """
        return self._groups[Particle.Status.QUEUED]

    @property
    def tracked_particles(self):
        """
        Retrieve all particles that have status ``TRACKED``.

        Returns
        -------
        tracked_particles : :class:`ParticleStatusView`
        """
        return self._groups[Particle.Status.TRACKED]

    @property
    def status_updates(self):
        """
        A stream on which all status changes of particles are published.

        Returns
        -------
        status_updates : :class:`rx.subject.Subject`
        """
        return self._status_updates

    def as_json(self):
        """
        Retrieve a JSON serializable representation of this component.

        Returns
        -------
        json : dict
        """
        return {
            'particle pool': self._pool,
        }

    def create_particle(self, progress, position=None, momentum=None,
                        status=Particle.Status.QUEUED):
        """
        Create a new particle by initializing its position and momentum as well as
        generating a corresponding status update notification.

        Parameters
        ----------
        progress : :class:`Progress`
            The current simulation progress (used for generating the status update notification).
        position : :class:`~np.ndarray` or list or tuple, optional
            Must provide 3 elements which are used to initialize the spatial position;
            if omitted then the position is initialized with zeros.
        momentum : :class:`~np.ndarray` or list or tuple, optional
            Must provide 3 elements which are used to initialize the momentum;
            if omitted then the momentum is initialized with zeros.
        status : Particle.Status, optional
            The new particle's status is changed to this value; the default is ``QUEUED``.
        """
        particle = self._pool.create_particle(position, momentum)
        self._update_single_status(particle, status, progress)
        return particle

    def get_particle_by_uuid(self, uuid):
        """
        Retrieve the particle corresponding to the given uuid.

        Parameters
        ----------
        uuid : int

        Returns
        -------
        particle : :class:`Particle`
        """
        return Particle(self._pool, uuid)

    def detect(self, particles, progress):
        """
        Change the given particles' statuses to ``DETECTED``.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress.
        """
        self._update_status(particles, Particle.Status.DETECTED, progress)

    def invalidate(self, particles, progress):
        """
        Change the given particles' statuses to ``INVALID``.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress.
        """
        self._update_status(particles, Particle.Status.INVALID, progress)

    def queue(self, particles, progress):
        """
        Change the given particles' statuses to ``QUEUED``.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress.
        """
        self._update_status(particles, Particle.Status.QUEUED, progress)

    def track(self, particles, progress):
        """
        Change the given particles' statuses to ``TRACKED``.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress.
        """
        self._update_status(particles, Particle.Status.TRACKED, progress)

    def _update_status(self, particles, status, progress):
        """
        Update the status of multiple particles and generate the corresponding
        status update notifications.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        status : Particle.Status
            The new status received by all particles.
        progress : :class:`Progress`
            The current simulation progress.
        """
        # Can't use assignment particles.status = status because after doing so iterating over
        # the particles isn't possible anymore because the indices will be reevaluated based on
        # their old status however the particles already have a new status.
        for particle in particles:
            self._update_single_status(particle, status, progress)

    def _update_single_status(self, particle, status, progress):
        """
        Update the status of a single particle and generate the corresponding
        status update notification.

        Parameters
        ----------
        particle : :class:`Particle`
        status : Particle.Status
            The new status received by the particle.
        progress : :class:`Progress`
            The current simulation progress.
        """
        old_status = particle.status
        particle.status = status
        self._status_updates.on_next(self.StatusUpdate(particle, old_status, progress))
