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

from anna import Action, Duplet, Number, PhysicalQuantity, SubstitutionGroup, Triplet, parametrize
from anna.utils import use_docs_from
import injector
import numpy as np
from scipy.constants import physical_constants
from scipy.special import gamma as gamma_function
from scipy.stats import gennorm

from virtual_ipm.components import Mutable
import virtual_ipm.di as di
from virtual_ipm.simulation.errors import ConfigurationError
from virtual_ipm.simulation.beams.utils import convert_lab_frame_bunch_length_to_bunch_frame, \
    compute_beta_and_gamma_from_energy
from virtual_ipm.utils.mathematics.random_sampling import RejectionSampling2D
from . import bunch_parameters


_SPEED_OF_LIGHT = physical_constants['speed of light in vacuum'][0]


class BunchShape(Mutable, metaclass=abc.ABCMeta):
    """
    (Abstract) Base class for bunch shape classes.
    """
    
    CONFIG_PATH_TO_IMPLEMENTATION = 'BunchShape/Model'
    CONFIG_PATH = 'BunchShape/Parameters'

    def __init__(self, configuration=None):
        """
        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor` derived class, optional
        """
        super().__init__(configuration)

    def as_json(self):
        return dict(
            super().as_json(),
            length=self.length
        )

    @property
    def density_as_string(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def length(self):
        """
        The bunch length in the bunch frame. There is no fixed definition of the bunch length but
        it should be reasonably chosen for each implementation (e.g. 2*3sigma for
        a Gaussian bunch).

        .. note::
        This is the full length, not the half length of the bunch.

        Returns
        -------
        bunch_length : float
            The bunch length in the bunch frame, given in units of [m].
        """
        raise NotImplementedError

    @abc.abstractmethod
    def normalized_density_at(self, positions):
        """
        Retrieve the particle density at the given positions. The density is normalized to a bunch
        population of 1.

        Parameters
        ----------
        positions : :class:`~np.ndarray`, shape (3, N)
            Positions are stored as column vectors and are given in the bunch frame,
            in units of [m].

        Returns
        -------
        particle_densities : :class:`~np.ndarray`, shape (N,)
            The particle densities at the given positions, in units of [1/m^3].
        """
        raise NotImplementedError

    @abc.abstractmethod
    def normalized_linear_density_at(self, z_positions):
        """
        Retrieve the linear particle density at the given z-positions. The density is normalized to
        a bunch population of 1.

        Parameters
        ----------
        z_positions : :class:`~np.ndarray`, shape (N,)
            Given in the bunch frame, in units of [m].

        Returns
        -------
        linear_particle_densities : :class:`~np.ndarray`, shape (N,)
            The linear particle densities at the given z-positions, in units of [1/m].
        """
        raise NotImplementedError

    @abc.abstractmethod
    def generate_positions_in_transverse_plane(self, count, z):
        """
        Generate positions in the transverse plane specified by the `z`-coordinate according to
        the bunch shape's particle density.

        Parameters
        ----------
        count : int
            The number of transverse positions to be generated.
        z : float
            The longitudinal position specifying the transverse plane,
            given in the bunch frame, in units of [m].

        Returns
        -------
        transverse_positions : :class:`~np.ndarray`, shape (2, `count`)
            Positions are stored as column vectors and are given in the bunch frame,
            in units of [m].
        """
        raise NotImplementedError

Interface = BunchShape


@parametrize(
    PhysicalQuantity('Radius', unit='m'),
    _longitudinal_sigma=SubstitutionGroup(
        PhysicalQuantity(
            'LongitudinalSigmaBunchFrame',
            unit='m'
        )
    ).add_option(
        Action(
            PhysicalQuantity(
                'LongitudinalSigmaLabFrame',
                unit='s'
            ),
            convert_lab_frame_bunch_length_to_bunch_frame,
            depends_on=(bunch_parameters.aware_energy, bunch_parameters.aware_particle_type)
        ),
        # Do nothing because the conversion is already handled by the ActionParameter.
        lambda x: x
    )
)
class Uniform(BunchShape):
    """
    Represents a charge distribution that is uniform in transverse dimensions (x, y) and Gaussian
    in the longitudinal dimension (z).
    """

    @injector.inject(configuration=di.components.configuration)
    def __init__(self, configuration):
        """
        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super().__init__(configuration)

    def density_as_string(self):
        raise NotImplementedError

    @property
    @use_docs_from(BunchShape)
    def length(self):
        return 8 * self._longitudinal_sigma

    @use_docs_from(BunchShape)
    def normalized_density_at(self, positions):
        inside = np.sqrt(positions[0]**2 + positions[1]**2) <= self._radius
        result = np.zeros_like(positions[0])
        result[inside] = (
            1. / (np.pi * self._radius**2)
            / np.sqrt(2 * np.pi * self._longitudinal_sigma**2)
            * np.exp(-0.5 * positions[2, inside]**2 / self._longitudinal_sigma**2)
        )
        return result

    @use_docs_from(BunchShape)
    def normalized_linear_density_at(self, z_positions):
        return (
            1. / np.sqrt(2 * np.pi * self._longitudinal_sigma ** 2)
            * np.exp(-0.5 * z_positions ** 2 / self._longitudinal_sigma ** 2)
        )

    @use_docs_from(BunchShape)
    def generate_positions_in_transverse_plane(self, count, z):
        rs = self._radius * np.sqrt(np.random.uniform(size=count))
        phis = np.random.uniform(high=2*np.pi, size=count)
        xs = rs * np.cos(phis)
        ys = rs * np.sin(phis)
        return np.vstack((xs, ys))


@parametrize(
    Duplet[PhysicalQuantity]('TransverseSigma', unit='m'),
    _longitudinal_sigma=SubstitutionGroup(
        PhysicalQuantity(
            'LongitudinalSigmaBunchFrame',
            unit='m'
        )
    ).add_option(
        Action(
            PhysicalQuantity(
                'LongitudinalSigmaLabFrame',
                unit='s'
            ),
            convert_lab_frame_bunch_length_to_bunch_frame,
            depends_on=(bunch_parameters.aware_energy, bunch_parameters.aware_particle_type)
        ),
        # Do nothing because the conversion is already handled by the ActionParameter.
        lambda x: x
    )
)
class Gaussian(BunchShape):
    """
    This component represents a bunch with Gaussian charge distribution in all dimensions.
    
    The half-length (head to center) of this bunch shape is ``4*sigma_z``.
    """

    @injector.inject(configuration=di.components.configuration)
    def __init__(self, configuration):
        """
        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super().__init__(configuration)
        self._sigma = np.array(
            self._transverse_sigma + (self._longitudinal_sigma,)
        )

    def as_json(self):
        return dict(
            super().as_json(),
            sigma=self.sigma.tolist(),
        )

    @property
    def density_as_string(self):
        from string import Template

        density_template = Template(
            '1. / ($sqrt_two_pi * $sigma) '
            '* exp(- pow(x[$index] / $sigma, 2) / 2.0)'
        )
        density_template = Template(
            density_template.safe_substitute(
                {'sqrt_two_pi': np.sqrt(2. * np.pi)}
            )
        )
        x_density = density_template.substitute({'index': 0, 'sigma': self.sigma[0]})
        y_density = density_template.substitute({'index': 1, 'sigma': self.sigma[1]})
        z_density = density_template.substitute({'index': 2, 'sigma': self.sigma[2]})
        overall_density = ' * '.join((x_density, y_density, z_density))

        self.log.debug('density: %s', density_template.template)
        self.log.debug('x-density: %s', x_density)
        self.log.debug('y-density: %s', y_density)
        self.log.debug('z-density: %s', z_density)
        self.log.debug('overall density: %s', overall_density)

        return overall_density

    @property
    def sigma(self):
        """
        The standard deviation of the Gaussian charge distribution.

        Returns
        -------
        sigma : :class:`~np.ndarray`, shape (3,)
            In the bunch frame, in units of [m].
        """
        return self._sigma

    @property
    @use_docs_from(BunchShape)
    def length(self):
        return 8.0 * self.sigma[2]

    # noinspection PyTypeChecker
    @use_docs_from(BunchShape)
    def normalized_density_at(self, positions):
        two_pi_sqrt = np.sqrt(2 * np.pi)
        a = 1. / (two_pi_sqrt**3 * self._sigma[0] * self._sigma[1] * self._sigma[2])
        g = a * np.exp(
            -0.5 * np.dot(1. / self.sigma**2, positions**2)
        )
        return g

    @use_docs_from(BunchShape)
    def normalized_linear_density_at(self, z_positions):
        sigma_z = self.sigma[2]
        return 1. / (np.sqrt(2 * np.pi) * sigma_z) * np.exp(
            -0.5 * z_positions**2 / sigma_z**2
        )

    @use_docs_from(BunchShape)
    def generate_positions_in_transverse_plane(self, count, z):
        xs = np.random.normal(scale=self._sigma[0], size=count)
        ys = np.random.normal(scale=self._sigma[1], size=count)
        return np.vstack((xs, ys))


def compute_linear_density_in_bunch_frame_from_beam_current(beam_current, energy, particle_type):
    beta, gamma = compute_beta_and_gamma_from_energy(energy, particle_type.rest_energy)
    velocity = _SPEED_OF_LIGHT * beta
    return beam_current / velocity / gamma


@parametrize(
    Duplet[PhysicalQuantity]('TransverseSigma', unit='m'),
    linear_density=Action(
        PhysicalQuantity('BeamCurrent', unit='A'),
        compute_linear_density_in_bunch_frame_from_beam_current,
        depends_on=(
                bunch_parameters.aware_energy,
                bunch_parameters.aware_particle_type
        )
    )
)
class GaussianDC(BunchShape):
    """
    This component represents a bunch with Gaussian charge distribution in the
    transverse plane and constant along the longitudinal axis (z).

    .. note::
       This model requires ``BunchPopulation`` to be set to 1.
    """

    @injector.inject(configuration=di.components.configuration)
    def __init__(self, configuration):
        """
        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super().__init__(configuration)
        self._sigma = np.array(self._transverse_sigma)

    def as_json(self):
        return dict(super().as_json(), sigma=self.sigma.tolist())

    @property
    def density_as_string(self):
        raise NotImplementedError

    @property
    def sigma(self):
        """
        The standard deviation of the Gaussian charge distribution.

        Returns
        -------
        sigma : :class:`~np.ndarray`, shape (2,)
            In the bunch frame, in units of [m].
        """
        return self._sigma

    @property
    @use_docs_from(BunchShape)
    def length(self):
        return np.inf

    # noinspection PyTypeChecker
    @use_docs_from(BunchShape)
    def normalized_density_at(self, positions):
        a = 1. / (np.sqrt(2*np.pi)**2 * self._sigma[0] * self._sigma[1])
        return a * np.exp(-0.5 * np.dot(1. / self._sigma**2, positions[:2]**2))

    @use_docs_from(BunchShape)
    def normalized_linear_density_at(self, z_positions):
        return np.full_like(z_positions, self.linear_density)

    @use_docs_from(BunchShape)
    def generate_positions_in_transverse_plane(self, count, z):
        xs = np.random.normal(scale=self._sigma[0], size=count)
        ys = np.random.normal(scale=self._sigma[1], size=count)
        return np.vstack((xs, ys))


@parametrize(
    Duplet[PhysicalQuantity]('TransverseScale', unit='m', info='These are the alpha parameters '
                                                               'for transverse dimensions.'),
    Duplet[Number]('TransverseShape', info='These are the beta parameters for transverse '
                                           'dimensions.'),
    Number('LongitudinalShape', info='This is the beta parameter for longitudinal dimension.'),
    _longitudinal_scale=SubstitutionGroup(
        PhysicalQuantity(
            'LongitudinalScaleBunchFrame',
            unit='m',
            info='This is the alpha parameter for longitudinal dimension.'
        ),
    ).add_option(
        Action(
            PhysicalQuantity(
                'LongitudinalScaleLabFrame',
                unit='s'
            ),
            convert_lab_frame_bunch_length_to_bunch_frame,
            depends_on=(bunch_parameters.aware_energy, bunch_parameters.aware_particle_type)
        ),
        # Do nothing because the conversion is already handled by the ActionParameter.
        lambda x: x
    )
)
class GeneralizedGaussian(BunchShape):
    """
    This component represents a bunch that has a generalized Gaussian charge distribution in all
    dimensions.
    
    The :math:`\\alpha` parameter is denoted with "scale" while the :math:`\\beta` parameter is
    denoted with "shape".
    The length (head to tail) of this bunch shape is the length of the 0.9999366 percentile of its
    longitudinal charge density. This corresponds to 4*sigma_z for beta = 2 (which corresponds
    to a "normal" Gaussian distribution).
    """

    @injector.inject(configuration=di.components.configuration)
    def __init__(self, configuration):
        """
        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super().__init__(configuration)
        self._scale = np.asarray(
            self._transverse_scale + (self._longitudinal_scale,)
        )
        self._shape = np.asarray(
            self._transverse_shape + (self._longitudinal_shape,)
        )

    def as_json(self):
        return dict(
            super().as_json(),
            sigma=self.sigma.tolist(),
            shape=self._shape.tolist()
        )

    @property
    def density_as_string(self):
        raise NotImplementedError

    @property
    @use_docs_from(BunchShape)
    def length(self):
        # Corresponds to 8 sigma for beta = 2 (-> Gaussian distribution).
        return 2 * gennorm.interval(0.9999366, self._shape[2], scale=self._scale[2])[1]

    # noinspection PyTypeChecker
    @use_docs_from(BunchShape)
    def normalized_density_at(self, positions):
        return (
            gennorm.pdf(positions[0, :], self._shape[0], scale=self._scale[0])
            * gennorm.pdf(positions[1, :], self._shape[1], scale=self._scale[1])
            * gennorm.pdf(positions[2, :], self._shape[2], scale=self._scale[2])
        )

    @use_docs_from(BunchShape)
    def normalized_linear_density_at(self, z_positions):
        return gennorm.pdf(z_positions, self._shape[2], scale=self._scale[2])

    @use_docs_from(BunchShape)
    def generate_positions_in_transverse_plane(self, count, z):
        return np.transpose(gennorm.rvs(self._shape[:2], scale=self._scale[:2], size=(count, 2)))


@parametrize(
    _q=Triplet[Number]('Q'),
    _beta=Triplet[PhysicalQuantity]('Beta', unit='m^2'),
    _scale=Triplet[PhysicalQuantity]('Scale', unit='m', info='Symmetric left and right margin for '
                                                             'the distribution in each dimension.')
)
class QGaussian(BunchShape):
    """
    This component represents a bunch whose charge density follows a q-Gaussian distribution in all
    dimensions.
    
    The half-length (head to center) of this bunch shape is the longitudinal (3rd) value of the
    specified "Scale" parameter.
    """
    def __init__(self, configuration):
        super().__init__(configuration)

        self._q = np.asarray(self._q)
        self._beta = np.asarray(self._beta)

        print('_q:', self._q)
        print('_beta:', self._beta)

        if np.any(self._q >= 3.):
            raise ConfigurationError('Q parameter must be < 3 for all dimensions') from None
        if np.any(self._beta <= 0.):
            raise ConfigurationError('Beta parameter must be > 0 for all dimensions') from None

        self._beta = np.asarray(self._beta)
        self._scale = np.asarray(self._scale)
        q = self._q = np.asarray(self._q)
        pi = np.pi
        sqrt_pi = np.sqrt(pi)
        sqrt_q1 = np.sqrt(np.abs(q - 1.))

        q_mask_lt = q < 1.
        q_mask_eq = q == 1.
        q_mask_gt = q > 1.

        q_lt = q[q_mask_lt]
        q_gt = q[q_mask_gt]

        self._C = np.empty((3,), dtype=float)
        self._C[q_mask_lt] = (
            (2 * sqrt_pi * gamma_function(1. / (1. - q_lt)))
            / ((3. - q_lt) * sqrt_q1[q_mask_lt] * gamma_function((3. - q_lt) / (2. - 2.*q_lt)))
        )
        self._C[q_mask_eq] = sqrt_pi
        self._C[q_mask_gt] = (
            sqrt_pi * gamma_function((3. - q_gt) / (2.*q_gt - 2.))
            / (sqrt_q1[q_mask_gt] * gamma_function(1. / (q_gt - 1.)))
        )
        self._sqrt_beta = np.sqrt(self._beta)

        if q[0] == 1.:
            self.q_exponential_x = np.exp
        if q[1] == 1.:
            self.q_exponential_y = np.exp
        if q[2] == 1.:
            self.q_exponential_z = np.exp

    @property
    def length(self):
        return 2. * self._scale[2]

    @property
    def density_as_string(self):
        raise NotImplementedError

    @staticmethod
    def q_exponential(x, q):
        result = np.zeros_like(x)
        mask = (1. + (1. - q) * x) > 0.
        result[mask] = (1. + (1. - q) * x[mask]) ** (1. / (1. - q))
        return result

    def q_exponential_x(self, x):
        return self.q_exponential(x, self._q[0])

    def q_exponential_y(self, x):
        return self.q_exponential(x, self._q[1])

    def q_exponential_z(self, x):
        return self.q_exponential(x, self._q[2])

    def eval_x(self, x):
        return self._sqrt_beta[0] / self._C[0] * self.q_exponential_x(-self._beta[0] * x ** 2)

    def eval_y(self, x):
        return self._sqrt_beta[1] / self._C[1] * self.q_exponential_y(-self._beta[1] * x ** 2)

    def eval_z(self, x):
        return self._sqrt_beta[2] / self._C[2] * self.q_exponential_z(-self._beta[2] * x ** 2)

    def normalized_density_at(self, positions):
        return self.eval_x(positions[0, :]) * self.eval_y(positions[1, :]) * self.eval_z(positions[2, :])

    def normalized_linear_density_at(self, z_positions):
        return self.eval_z(z_positions)

    def generate_positions_in_transverse_plane(self, count, z):
        x_samples = RejectionSampling2D(self.eval_x, -self._scale[0], self._scale[0],
                                        self.eval_x(0)).create_samples(count)
        y_samples = RejectionSampling2D(self.eval_y, -self._scale[1], self._scale[1],
                                        self.eval_y(0)).create_samples(count)
        return np.stack((x_samples, y_samples))


def convert_beam_current_to_charge_density(
        beam_current, inner_radius, outer_radius, energy, particle_type):
    beta, gamma = compute_beta_and_gamma_from_energy(energy, particle_type.rest_energy)
    velocity = _SPEED_OF_LIGHT * beta
    return (
        beam_current
        / (np.pi * (outer_radius**2 - inner_radius**2) * velocity * gamma)
    )


@parametrize(
    PhysicalQuantity('InnerRadius', unit='m'),
    PhysicalQuantity('OuterRadius', unit='m'),
    _charge_density=Action(
        PhysicalQuantity('BeamCurrent', unit='A'),
        convert_beam_current_to_charge_density,
        depends_on=(
                'InnerRadius', 'OuterRadius', bunch_parameters.aware_energy,
                bunch_parameters.aware_particle_type
        )
    )
)
class HollowDCBeam(BunchShape):
    """
    This component represents a hollow DC beam with uniform charge density between the two radii.
    
    The longitudinal charge density of this bunch shape is constant and its length is infinite in
    order to mimic a DC beam.
    """

    def __init__(self, configuration):
        super().__init__(configuration)
        self._particle_density = self._charge_density / physical_constants['elementary charge'][0]

    @property
    def inner_radius(self):
        return self._inner_radius

    @property
    def outer_radius(self):
        return self._outer_radius

    @property
    def length(self):
        return np.inf

    def as_json(self):
        return dict(
            super().as_json(),
            inner_radius=self._inner_radius,
            outer_radius=self._outer_radius,
            charge_density=self._charge_density
        )

    def density_as_string(self):
        raise NotImplementedError

    def normalized_density_at(self, positions):
        density = np.zeros(positions.shape[1], dtype=float)
        radius = np.sqrt(positions[0, :]**2 + positions[1, :]**2)
        between_inner_and_outer_radius = np.logical_and(
            self._inner_radius <= radius,
            radius <= self._outer_radius
        )
        density[between_inner_and_outer_radius] = self._particle_density
        return density

    def normalized_linear_density_at(self, z_positions):
        return np.full(
            z_positions.shape,
            self._particle_density * np.pi * (self._outer_radius**2 - self._inner_radius**2)
        )

    def generate_positions_in_transverse_plane(self, count, z):
        radius = np.sqrt(
            np.random.uniform(
                self._inner_radius ** 2,
                self._outer_radius ** 2,
                size=count
            )
        )
        phi = np.random.uniform(0, 2*np.pi, size=count)
        return np.stack((
            radius * np.cos(phi),
            radius * np.sin(phi)
        ))


@parametrize(
    PhysicalQuantity('SemiMinorAxis', unit='m'),
    _semi_major_axis=SubstitutionGroup(
        PhysicalQuantity('SemiMajorAxis', unit='m', info='In the bunch frame.'),
    ).add_option(
        Action(
            PhysicalQuantity(
                'SemiMajorAxisLabFrame',
                unit='s',
                info='In the lab frame.'
            ),
            convert_lab_frame_bunch_length_to_bunch_frame,
            depends_on=(bunch_parameters.aware_energy, bunch_parameters.aware_particle_type)
        ),
        # Do nothing because the conversion is already handled by the ActionParameter.
        lambda x: x
    )
)
class ParabolicEllipsoid(BunchShape):
    """
    This bunch shape models a parabolically charged ellipsoid. This is a rotational symmetric
    spheriod (with respect to the z-axis) whose charge decreases parabolically when going from
    the center outwards.
    
    The half-length (head to center) of this bunch shape is the specified semi major axis.
    
    References
    ----------
    M.Dolinska (INR-Kiev), R.W.Mueller (GSI-Darmstadt), P.Strehl (GSI-Darmstadt):
    "The Electric Field of Bunches", July 5th 2000
    """

    def __init__(self, configuration):
        super().__init__(configuration)
        a = self.semi_major_axis
        b = self.semi_minor_axis
        self._xi0 = a / np.sqrt(a**2 - b**2)

    def as_json(self):
        return dict(
            super().as_json(),
            semi_major_axis=self.semi_major_axis,
            semi_minor_axis=self.semi_minor_axis
        )

    @property
    def semi_major_axis(self):
        return self._semi_major_axis

    @property
    def semi_minor_axis(self):
        return self._semi_minor_axis

    @property
    def density_as_string(self):
        """
        .. warning::
        The density string is only valid inside the ellipsoid. Outside of the ellipsoid it yields
        negative values however the density is to be considered zero outside.
        
        Returns
        -------
        density_as_string : unicode
        """
        pi = np.pi
        a = self.semi_major_axis
        b = self.semi_minor_axis
        return (
            '%(factor)e * (1. - pow(x[0] / %(b)e, 2)'
            '                 - pow(x[1] / %(b)e, 2)'
            '                 - pow(x[2] / %(a)e, 2))'
        ) % {
            'factor': 15. / (8. * pi * a * b**2),
            'a': a,
            'b': b
        }

    @property
    def length(self):
        return 2. * self.semi_major_axis

    @use_docs_from(BunchShape)
    def normalized_density_at(self, positions):
        result = np.empty(positions.shape[1], dtype=float)
        inside = self.inside_from_3d_cartesian_coordinates(positions)
        outside = ~inside
        pi = np.pi
        a = self.semi_major_axis
        b = self.semi_minor_axis
        r_square_inside = positions[0, inside]**2 + positions[1, inside]**2
        z_square_inside = positions[2, inside]**2
        result[inside] = 15. / (8. * pi * a * b**2) * (
            1. - r_square_inside/b**2 - z_square_inside/a**2
        )
        result[outside] = 0.
        return result

    @use_docs_from(BunchShape)
    def normalized_linear_density_at(self, z_positions):
        result = np.empty(z_positions.size, dtype=float)
        inside = np.logical_and(
            -self.semi_major_axis < z_positions,
            z_positions < self.semi_major_axis
        )
        outside = ~inside
        a = self.semi_major_axis
        z_square_inside = z_positions[inside] ** 2
        result[inside] = 15. / (16. * a) * (1. - z_square_inside / a**2) ** 2
        result[outside] = 0.
        return result

    @use_docs_from(BunchShape)
    def generate_positions_in_transverse_plane(self, count, z):
        if np.abs(z) >= self.semi_major_axis:
            raise ValueError('z-position outside of the ellipsoid')

        a = self.semi_major_axis
        b = self.semi_minor_axis

        def distribution(position):
            return (
                1. - (position[0]**2 + position[1]**2) / b**2 - z**2 / a**2
            )

        # Transverse plane of the rotational symmetric ellipsoid is a circle.
        # Note that this will generate a fair number of positions outside of the circle which
        # will are certainly rejected. However generating one dimension after another and confining
        # the second dimension to the circle's area would bias the probability of positions lying
        # closer towards the boundaries of the circle.
        # However we can confine the area with respect to the z-coordinate.
        max_xy = np.sqrt(1. - z**2 / a**2) * b
        samples = np.random.uniform(-1.0 * max_xy, max_xy, size=(2, count))
        rejected = np.argwhere(
            np.random.uniform(0., 1., count)
            <=
            1. - distribution(samples)
        ).flatten()
        while rejected.size > 0:
            samples[:, rejected] = \
                np.random.uniform(-1.0 * max_xy, max_xy, size=(2, len(rejected)))
            rejected = rejected[
                np.random.uniform(0., 1., len(rejected))
                <=
                1. - distribution(samples[:, rejected])
            ]
        return samples

    def inside_from_3d_cartesian_coordinates(self, positions):
        """
        Semi-major axis is along `z` (``positions[2]``), semi-minor axes are along `x`, `y`.

        Parameters
        ----------
        positions : :class:`np.ndarray`, shape (3, N)
            Cartesian coordinates (x, y, z).

        Returns
        -------
        inside : :class:`np.ndarray`, shape (N,), dtype=bool
            True for those who are inside.
        """
        a = self.semi_major_axis
        b = self.semi_minor_axis
        return (
                   positions[0] ** 2 / b ** 2
                   + positions[1] ** 2 / b ** 2
                   + positions[2] ** 2 / a ** 2
               ) <= 1.

    def inside_from_2d_elliptical_coordinates(self, positions):
        """
        Parameters
        ----------
        positions : :class:`np.ndarray`, shape (2, N)
            Elliptical coordinates (xi, eta); ``1 <= xi``, ``-1 <= eta <= 1``.

        Returns
        -------
        inside : :class:`np.ndarray`, shape (N,), dtype=bool
            True for those who are inside.
        """
        return positions[0] <= self._xi0
