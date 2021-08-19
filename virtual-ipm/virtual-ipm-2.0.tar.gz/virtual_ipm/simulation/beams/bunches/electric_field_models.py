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

from anna import Choice, Duplet, Triplet, Integer, Number, PhysicalQuantity, String, parametrize
from anna.utils import use_docs_from
try:
    # noinspection PyPackageRequirements
    import dolfin
except ImportError:
    dolfin = None
import numpy as np
import scipy.constants as constants
import scipy.linalg
from scipy.special import erfcx as scaled_complementary_complex_error_function
import scipy.stats

from virtual_ipm.components import Model
from virtual_ipm.simulation.errors import ConfigurationError, IncompatibleModelsError, MissingOptionalDependencyError
from . import shapes as bunch_shapes


class BunchElectricFieldModel(Model, metaclass=abc.ABCMeta):
    """
    (Abstract) Base class for bunch electric field models.

    A bunch electric field model must provide the electric field in the rest frame of the bunch.
    The electric field must correspond to a total bunch charge equals the elementary charge.
    The appropriate rescaling is performed in :method:`Bunch.electric_and_magnetic_field_at`.

    .. note::
       The bunch magnetic field is computed via Lorentz transformation from the bunch
       electric field.
    """

    CONFIG_PATH_TO_IMPLEMENTATION = 'BunchElectricField/Model'
    CONFIG_PATH = 'BunchElectricField/Parameters'

    # noinspection PyUnusedLocal
    def __init__(self, bunch_shape, device, configuration=None):
        """
        Parameters
        ----------
        bunch_shape : :class:`BunchShape`
        device : :class:`DeviceManager`
        configuration : :class:`ConfigurationAdaptor` derived instance, optional
        """
        super().__init__(configuration)

    def __call__(self, positions):
        """
        Evaluate the electric field at the given positions.

        See Also
        --------
        :method:`~BunchElectricFieldModel.eval` : For arguments and return values.
        """
        return self.eval(positions)

    @abc.abstractmethod
    def eval(self, positions):
        """
        Retrieve the bunch electric field in the bunch frame at the given positions.

        Parameters
        ----------
        positions : :class:`~np.ndarray`, shape (3, N)
            Positions are stored as column vectors and are given in the bunch frame,
            in units of [m].

        Returns
        -------
        electric_field : :class:`~np.ndarray`, shape (3, N)
            The electric field vectors at the given positions; the electric field vectors are
            stored as column vectors and are given in the bunch frame,
            in units of [V/m].
        """
        raise NotImplementedError


Interface = BunchElectricFieldModel


class ForUniform(BunchElectricFieldModel):
    """
    Electric field model corresponding to the `Uniform` bunch shape.
    """

    def __init__(self, bunch_shape, device, configuration=None):
        """
        Parameters
        ----------
        bunch_shape : :class:`BunchShape`
        device : :class:`DeviceManager`
        configuration : :class:`ConfigurationAdaptor` derived instance, optional
        """
        super().__init__(bunch_shape, device, configuration)
        self._shape = bunch_shape

    @use_docs_from(BunchElectricFieldModel)
    def eval(self, positions):
        r = scipy.linalg.norm(positions[:2], axis=0)
        phi = np.arctan2(positions[1], positions[0])
        E_r = (
            constants.elementary_charge
            / (2 * constants.pi * constants.epsilon_0 * self._shape._radius**2)
            * scipy.stats.norm.pdf(positions[2], scale=self._shape._longitudinal_sigma)
            * np.minimum(r, self._shape._radius)**2 / r
        )
        return np.stack([
            E_r * np.cos(phi),
            E_r * np.sin(phi),
            np.zeros_like(E_r)
        ])


class _SymmetricGaussian2D(BunchElectricFieldModel):
    SIGMA_DIFFERENCE_THRESHOLD = 1.0e-6

    __doc__ = """
    Electrical field for a 2D circular (that is radially symmetric) Gaussian bunch
    (``sigma_x == sigma_y`` within a tolerance of ``%.1e``).
    """ % SIGMA_DIFFERENCE_THRESHOLD

    def __init__(self, bunch_shape, device, configuration=None):
        """
        Parameters
        ----------
        bunch_shape : :class:`BunchShape`
        device : :class:`DeviceManager`
        configuration : :class:`ConfigurationAdaptor` derived instance, optional
        """
        super().__init__(bunch_shape, device, configuration)

        if abs(bunch_shape.sigma[0] - bunch_shape.sigma[1]) > self.SIGMA_DIFFERENCE_THRESHOLD:
            raise ConfigurationError(
                'Difference in sigma_x and sigma_y must not be greater than %e'
                % self.SIGMA_DIFFERENCE_THRESHOLD
            ) from None
        self._sigma = bunch_shape.sigma[0]
        self._inv_2_pi_eps0 = 1 / (2. * constants.pi * constants.epsilon_0)

    @use_docs_from(BunchElectricFieldModel)
    def eval(self, position):
        r = scipy.linalg.norm(position[:2], axis=0)
        z = position[2]
        r_not_equals_zero = (r != 0.)
        # Electric field for r == 0 is zero.
        electric_field_abs_val = np.zeros(r.size, dtype=float)
        electric_field_abs_val[r_not_equals_zero] = (
            self._inv_2_pi_eps0
            * constants.elementary_charge
            / r[r_not_equals_zero]
            * (1.0 - np.exp(- r[r_not_equals_zero]**2 / (2. * self._sigma**2)))
        )
        phi = np.arctan2(position[1], position[0])
        return np.stack((
            electric_field_abs_val * np.cos(phi),
            electric_field_abs_val * np.sin(phi),
            0. * z  # Multiply with z in order to get the dimensions right.
        ))


class _BassettiErskine2D(BunchElectricFieldModel):
    """
    Electrical field for a 2D elliptical Gaussian bunch (that is ``sigma_x != sigma_y``). The
    longitudinal charge distribution is taken into account by rescaling the field according to the
    longitudinal position.

    References
    ----------
    .. [1] M.Bassetti & G.A.Erskine: "Closed Expression for the Electrical Field of
       a Two-Dimensional Gaussian Charge", CERN-ISR-TH/80-06, Geneva (CERN), 1980
    """

    def __init__(self, bunch_shape, device, configuration=None):
        """
        Parameters
        ----------
        bunch_shape : :class:`BunchShape`
        device : :class:`DeviceManager`
        configuration : :class:`ConfigurationAdaptor` derived instance, optional
        """
        super().__init__(bunch_shape, device, configuration)

        self._sigma_x, self._sigma_y, self._sigma_z = bunch_shape.sigma
        self.Ez_placeholder = np.zeros(shape=(1,), dtype=float)
        self.sqrt_2pi = np.sqrt(2. * np.pi)

    def prepare(self):
        super().prepare()
        if self._sigma_x**2 - self._sigma_y**2 == 0:
            raise ConfigurationError('sigma_x and sigma_y must not be equal (or too close within floating point limits)')

    # noinspection PyPep8Naming
    @use_docs_from(BunchElectricFieldModel)
    def eval(self, position):
        x, y, z = position
        Ex, Ey = self.compute_field_at(x, y, self._sigma_x, self._sigma_y)
        field_vector = np.stack((Ex, Ey, np.zeros_like(z)))
        return field_vector * constants.elementary_charge

    # noinspection PyPep8Naming,PyUnresolvedReferences
    @staticmethod
    def compute_field_at(x_signed, y_signed, sigma_x, sigma_y):
        """
        Compute the field at the given position for the given beam size using
        the formula of Bassetti & Erskine.

        The result is the 2D field in the 2D transverse plane per elementary charge.
        In order to obtain the actual field in the 3D space it needs to be rescaled
        with the (corresponding) longitudinal density and the elementary charge.

        Parameters
        ----------
        x_signed : float or 1d-:class:`~np.ndarray`
            The x-position(s) in the bunch frame, in units of [m].
        y_signed : float or 1d-:class:`~np.ndarray`
            The y-position(s) in the bunch frame, in units of [m].
        sigma_x : float
            Beam size with respect to x-direction, in units of [m].
        sigma_y : float
            Beam size with respect to y-direction, in units of [m].

        Returns
        -------
        electric_field : tuple
            The first element is (are) the x-component(s) of the electric field vector(s),
            the second component is (are) the y-component(s) of the electric field vector(s),
            given in the bunch frame, in units of [V/(m*e)], where `e` is the elementary charge.
        """
        exp, pi, sign, sqrt = np.exp, np.pi, np.sign, np.sqrt

        def w_function(z):
            """
            Evaluate the complementary complex error function.

            Parameters
            ----------
            z : complex or :class:`~np.ndarray`[complex], shape (N,)

            Returns
            -------
            result : complex or :class:`~np.ndarray`[complex], shape (N,)

            See Also
            --------
            :func:`scipy.special.erfcx` : This implementation is used.

            References
            ----------
            .. [1] Abramowitz, Stegun: Handbook of Mathematical Functions, National Bureau of
               Standards, Applied Mathematics Series 55, 1972 [Equation 7.1.3]
            """
            return scaled_complementary_complex_error_function(-1j * z)

        x_abs = np.abs(x_signed)
        y_abs = np.abs(y_signed)

        if sigma_x > sigma_y:

            s = sqrt(2. * (sigma_x * sigma_x - sigma_y * sigma_y))
            fact_be = 1. / (2. * constants.epsilon_0 * sqrt(pi) * s)

            # Use complex numbers to pass the values to the (complex) error function.
            eta_be = sigma_y / sigma_x * x_abs + 1j * sigma_x / sigma_y * y_abs
            zeta_be = x_abs + 1j * y_abs

            val = (
                fact_be * (w_function(zeta_be / s)
                           - exp(- x_abs ** 2 / (2. * sigma_x ** 2)
                                 - y_abs ** 2 / (2. * sigma_y ** 2))
                           * w_function(eta_be / s))
            )

            Ex = np.abs(val.imag) * sign(x_signed)
            Ey = np.abs(val.real) * sign(y_signed)

        else:

            s = sqrt(2. * (sigma_y * sigma_y - sigma_x * sigma_x))
            fact_be = 1. / (2. * constants.epsilon_0 * sqrt(pi) * s)

            # Use complex numbers to pass the values to the (complex) error function.
            eta_be = sigma_x / sigma_y * y_abs + 1j * sigma_y / sigma_x * x_abs
            yeta_be = y_abs + 1j * x_abs

            val = (
                fact_be * (w_function(yeta_be / s)
                           - exp(- y_abs ** 2 / (2. * sigma_y ** 2)
                                 - x_abs ** 2 / (2. * sigma_x ** 2))
                           * w_function(eta_be / s))
            )

            Ey = np.abs(val.imag) * sign(y_signed)
            Ex = np.abs(val.real) * sign(x_signed)

        return Ex, Ey


class _GaussianBase(BunchElectricFieldModel):
    """
    Auxiliary class which automatically selects between the `_SymmetricGaussian2D` and `_BassettiErskine2D` models
    based on the similarity of values specified by `TransverseSigma`.
    """

    SIGMA_DIFFERENCE_THRESHOLD = 1.0e-6

    def __init__(self, bunch_shape, device, configuration=None):
        """
        Parameters
        ----------
        bunch_shape : :class:`BunchShape`
        device : :class:`DeviceManager`
        configuration : :class:`ConfigurationAdaptor` derived instance, optional
        """
        super().__init__(bunch_shape, device, configuration)
        if abs(bunch_shape.sigma[0] - bunch_shape.sigma[1]) > self.SIGMA_DIFFERENCE_THRESHOLD:
            self.model = _BassettiErskine2D(bunch_shape, device, configuration)
        else:
            self.model = _SymmetricGaussian2D(bunch_shape, device, configuration)

    def eval(self, positions):
        raise NotImplementedError


class Gaussian(_GaussianBase):
    """
    Electric field model for a beam where bunches have a Gaussian charge distribution in all three dimensions.
    """

    def __init__(self, bunch_shape, device, configuration=None):
        super().__init__(bunch_shape, device, configuration)
        self._sigma_z = bunch_shape.sigma[2]

    @use_docs_from(BunchElectricFieldModel)
    def eval(self, position):
        z = position[2]
        z_factor = 1 / (np.sqrt(2 * constants.pi) * self._sigma_z) * np.exp(- z ** 2 / (2. * self._sigma_z ** 2))
        return self.model.eval(position) * z_factor


class GaussianDC(_GaussianBase):
    """
    Electric field model for emulating a DC beam which has a Gaussian charge distribution in the transverse plane.
    """

    def __init__(self, bunch_shape, device, configuration=None):
        super().__init__(bunch_shape, device, configuration)
        self.lin_density_div_elem_charge = bunch_shape.linear_density / constants.elementary_charge

    @use_docs_from(BunchElectricFieldModel)
    def eval(self, positions):
        # The underlying `self.model` already multiplies with the elementary charge.
        return self.model.eval(positions) * self.lin_density_div_elem_charge


class SymmetricGaussian(Gaussian):
    def __init__(self, bunch_shape, device, configuration=None):
        super().__init__(bunch_shape, device, configuration)
        self.log.warning('[Deprecation Warning] The SymmetricGaussian electric field model has been superseded by the '
                         'Gaussian electric field model; please change your configuration files to use the new '
                         'Gaussian model as the SymmetricGaussian model will be removed in the next release.')


class BassettiErskine(Gaussian):
    def __init__(self, bunch_shape, device, configuration=None):
        super().__init__(bunch_shape, device, configuration)
        self.log.warning('[Deprecation Warning] The BassettiErskine electric field model has been superseded by the '
                         'Gaussian electric field model; please change your configuration files to use the new '
                         'Gaussian model as the BassettiErskine model will be removed in the next release.')


class HollowDCBeam(BunchElectricFieldModel):
    __doc__ = """
    Analytical solution for the electric field of a hollow DC beam.
    
    .. note::
       This electric field model must be used together with the {0} bunch shape model.
       
    .. note::
       This field model yields the electric field as generated by the DC beam current, normalized
       by the elementary charge.
    """.format(bunch_shapes.HollowDCBeam.__name__)

    def __init__(self, bunch_shape, device, configuration=None):
        super().__init__(bunch_shape, device, configuration)

        if not isinstance(bunch_shape, bunch_shapes.HollowDCBeam):
            raise IncompatibleModelsError(
                'This field model requires an instance of %s as bunch shape'
                % bunch_shapes.HollowDCBeam.__name__
            ) from None

        self._pre_factor = bunch_shape._charge_density / (2 * constants.epsilon_0)
        self._inner_radius = bunch_shape.inner_radius
        self._outer_radius = bunch_shape.outer_radius

    def eval(self, positions):
        radius = np.sqrt(positions[0]**2 + positions[1]**2)
        phi = np.arctan2(positions[1], positions[0])
        case_1 = radius <= self._inner_radius
        case_2 = np.logical_and(
            self._inner_radius < radius,
            radius < self._outer_radius
        )
        case_3 = self._outer_radius <= radius
        absolute_value_case_2 = self._pre_factor / radius[case_2] * (
            radius[case_2]**2 - self._inner_radius**2
        )
        absolute_value_case_3 = self._pre_factor / radius[case_3] * (
            self._outer_radius**2 - self._inner_radius**2
        )
        phi_case_2 = phi[case_2]
        phi_case_3 = phi[case_3]

        electric_field = np.empty(positions.shape, dtype=float)
        # Electric field in z-direction is zero for all cases.
        electric_field[2, :] = 0.

        electric_field[:2, case_1] = 0.

        electric_field[0, case_2] = absolute_value_case_2 * np.cos(phi_case_2)
        electric_field[1, case_2] = absolute_value_case_2 * np.sin(phi_case_2)

        electric_field[0, case_3] = absolute_value_case_3 * np.cos(phi_case_3)
        electric_field[1, case_3] = absolute_value_case_3 * np.sin(phi_case_3)

        return electric_field


@parametrize(
    Duplet[Integer](
        'GridPoints',
        info='The number of grid points in x- and y-direction.'
    ),
    Duplet[PhysicalQuantity](
        'XRange',
        unit='m',
        optional=True,
        info='Controls the grid extent in x-direction. If not given then the device boundaries '
             'are used as grid boundaries. However if the field is (almost) constant (or even '
             'negligible) at the device boundaries it might be more efficient to choose a smaller '
             'grid in order to get more precision in this region. The field value outside of the '
             'grid can be set via the `FieldValueOutside` parameter.'
    ),
    Duplet[PhysicalQuantity](
        'YRange',
        unit='m',
        optional=True,
        info='Controls the grid extent in y-direction. If not given then the device boundaries '
             'are used as grid boundaries. However if the field is (almost) constant (or even '
             'negligible) at the device boundaries it might be more efficient to choose a smaller '
             'grid in order to get more precision in this region. The field value outside of the '
             'grid can be set via the `FieldValueOutside` parameter.'
    ),
    PhysicalQuantity(
        'FieldValueOutside',
        unit='V/m',
        default=0.,
        info='This parameter controls the field value that is assumed for positions outside of '
             'the specified grid. Defaults to zero. Note that this value must be given in the '
             'rest frame of the bunch and it must correspond to a bunch population of 1. The '
             'resulting field vector will always point towards the origin (in the bunch frame) '
             'so depending on the charge distribution this might be a rather rough approximation.'
    ),
    # Default parameters are from original IPMSim3D code.
    Number(
        'ConvergenceLimit',
        default=1.0e-6
    ),
    Number(
        'RelaxationFactor',
        default=1.9,
        info='www.physics.buffalo.edu/phy410-505/2011/topic3/app1/index.html gives a hint for '
             'an optimal relaxation factor, namely: 2.0 / (1.0 + (pi / nx)); where `nx` is '
             'the number of grid points in x-direction.'
    )
)
class Poisson2DSor(BunchElectricFieldModel):
    """
    Successive over-relaxation method for solving Poisson's equation in two dimensions.

    To incorporate the longitudinal charge density distribution the field is scaled according
    to the longitudinal position.
    """

    def __init__(self, bunch_shape, device, configuration):
        super().__init__(bunch_shape, device, configuration)

        self._bunch_shape = bunch_shape

        self._nx, self._ny = self._grid_points

        if self._x_range is not None:
            self._xmin = min(self._x_range)
            self._xmax = max(self._x_range)
        else:
            self._xmin = device.x_min
            self._xmax = device.x_max
        self.log.debug('Using x-range: (%e, %e)', self._xmin, self._xmax)

        if self._y_range is not None:
            self._ymin = min(self._y_range)
            self._ymax = max(self._y_range)
        else:
            self._ymin = device.y_min
            self._ymax = device.y_max
        self.log.debug('Using y-range: (%e, %e)', self._ymin, self._ymax)

        self._xs = np.linspace(self._xmin, self._xmax, self._nx)
        self._ys = np.linspace(self._ymin, self._ymax, self._ny)

        self.Ex = np.zeros(shape=(self._nx, self._ny), dtype=float)
        self.Ey = np.zeros(shape=(self._nx, self._ny), dtype=float)
        self.Ez = np.zeros(shape=(1,), dtype=float)

    def as_json(self):
        attributes = super().as_json()
        attributes.update({
            '__class__': self.__class__.__name__,
            'number of grid points along x': self._nx,
            'number of grid points along y': self._ny,
            'boundaries along x': ('%e' % self._xmin, '%e' % self._xmax),
            'boundaries along y': ('%e' % self._ymin, '%e' % self._ymax),
            'minimum / maximum field in x': ('%e' % np.min(self.Ex), '%e' % np.max(self.Ex)),
            'minimum / maximum field in y': ('%e' % np.min(self.Ey), '%e' % np.max(self.Ey)),
        })
        return attributes

    def prepare(self):
        """
        Solve Poisson's equation in two-dimension on the specified grid. 3 sigma are used as
        grid region in each dimension (from the center, i.e. total length is 6 sigma).
        """
        super().prepare()

        self.log.info(
            "Solving Poisson's equation in order to obtain the beam fields. This may take some "
            "time ..."
        )

        # Obtain the particle density at z=0 because the resulting electric field will be rescaled
        # according to the current charge density at a given `z` position.
        self._reference_particle_density = self._bunch_shape.normalized_density_at(
            np.zeros((3, 1), dtype=float)
        )[0]

        delta_x = (self._xmax - self._xmin) / self._nx
        delta_y = (self._ymax - self._ymin) / self._ny

        delta_x_sq = delta_x ** 2
        delta_y_sq = delta_y ** 2
        delta_xy_sq = delta_x_sq + delta_y_sq

        # Let y be the "fast" index.
        ys_grid, xs_grid = np.meshgrid(self._ys, self._xs)
        zs_grid = np.zeros(shape=xs_grid.shape, dtype=float)

        # Grid positions is a 2d array of all positions in the grid:
        # [[x1, x2, ...],
        #  [y1, y2, ...],
        #  [z1, z2, ...]]
        grid_positions = np.dstack((xs_grid, ys_grid, zs_grid)).flatten().reshape((-1, 3)).T

        rho = self._bunch_shape.normalized_density_at(grid_positions).reshape(xs_grid.shape)
        phi = np.zeros(shape=(self._nx, self._ny), dtype=float)

        # Successive over-relaxation (SOR) method.
        # Iterate until convergence is reached.
        # max_phi is the maximal (absolute) value that is reached during a sweep; init to a small
        # number so it is overridden during the first sweep.
        # Initialize max_err such that while condition is fulfilled.
        n_iterations = 0
        max_phi = 1.e-10
        max_err = self._convergence_limit + 1.
        while max_err >= self._convergence_limit:
            max_err = 0.
            for i in range(1, self._nx - 1):
                for j in range(1, self._ny - 1):
                    previous_phi = phi[i, j]
                    phi[i, j] += self._relaxation_factor * (
                        0.5 / delta_xy_sq * (
                            rho[i, j] * delta_x_sq * delta_y_sq / constants.epsilon_0
                            + delta_y_sq * (phi[i+1, j] + phi[i-1, j])
                            + delta_x_sq * (phi[i, j+1] + phi[i, j-1])
                        ) - previous_phi
                    )
                    if max_phi < abs(phi[i, j]):
                        max_phi = phi[i, j]
                    current_error = abs(phi[i, j] - previous_phi) / max_phi
                    if max_err < current_error:
                        max_err = current_error
            n_iterations += 1
            self.log.debug(
                'Completed iteration #%d; error: %e, convergence limit: %e'
                % (n_iterations, max_err, self._convergence_limit)
            )

        # Inner region.
        self.Ex[1:-1, 1:-1] = -(phi[2:, 1:-1] - phi[:-2, 1:-1]) / (2.0 * delta_x)
        self.Ey[1:-1, 1:-1] = -(phi[1:-1, 2:] - phi[1:-1, :-2]) / (2.0 * delta_y)

        # Alternatively using an explicit for-loop.
        # for i in range(1, self._nx - 1):
        #     for j in range(1, self._ny - 1):
        #         self.Ex[i, j] = -(phi[i + 1, j] - phi[i - 1, j]) / (2.0 * delta_x)
        #         self.Ey[i, j] = -(phi[i, j + 1] - phi[i, j - 1]) / (2.0 * delta_y)

        #
        # Edges.
        self.Ex[:, 0] = self.Ex[:, 1]
        self.Ey[:, 0] = self.Ey[:, 1]
        self.Ex[:, -1] = self.Ex[:, -2]
        self.Ey[:, -1] = self.Ey[:, -2]

        self.Ex[0, :] = self.Ex[1, :]
        self.Ey[0, :] = self.Ey[1, :]
        self.Ex[-1, :] = self.Ex[-2, :]
        self.Ey[-1, :] = self.Ey[-2, :]

        # Alternatively using an explicit for-loop.
        # for i in range(0, self._nx):
        #     self.Ex[i, 0] = self.Ex[i, 1]
        #     self.Ey[i, 0] = self.Ey[i, 1]
        #     self.Ex[i, -1] = self.Ex[i, -2]
        #     self.Ey[i, -1] = self.Ey[i, -2]
        #
        # for i in range(0, self._ny):
        #     self.Ex[0, i] = self.Ex[1, i]
        #     self.Ey[0, i] = self.Ey[1, i]
        #     self.Ex[-1, i] = self.Ex[-2, i]
        #     self.Ey[-1, i] = self.Ey[-2, i]

        self.log.info('... done.')

    # noinspection PyPep8Naming
    def eval(self, positions):
        """
        Retrieve the bunch electric field in the bunch frame at the given positions.

        .. note::
        For positions outside the grid region (see :method:`~PoissonSOR2DGauss.prepare`) a field
        strength of zero is returned.

        Parameters
        ----------
        positions : :class:`~np.ndarray`, shape (3, N)
            Positions are stored as column vectors and are given in the bunch frame,
            in units of [m].

        Returns
        -------
        electric_field : :class:`~np.ndarray`, shape (3, N)
            The electric field vectors at the given positions; the electric field vectors are
            stored as column vectors and are given in the bunch frame,
            in units of [V/m].
        """
        # Could use scipy.interpolate.RegularGridInterpolator instead of manual interpolation.

        # The max. boundary is considered outside because below `searchsorted` is told to yield
        # the rightmost index so in case of an upper boundary this would be the last grid point
        # already (i.e. no interpolation possible, missing grid point "to the right").
        outside = (
            (positions[0] < self._xmin)
            | (positions[0] >= self._xmax)
            | (positions[1] < self._ymin)
            | (positions[1] >= self._ymax)
        )
        inside = ~outside

        ix = np.searchsorted(self._xs, positions[0, inside], side=str('right')) - 1
        remainder_x = (positions[0, inside] - self._xs[ix]) / (self._xs[ix+1] - self._xs[ix])

        iy = np.searchsorted(self._ys, positions[1, inside], side=str('right')) - 1
        remainder_y = (positions[1, inside] - self._ys[iy]) / (self._ys[iy+1] - self._ys[iy])

        def interpolate(field):
            return (
                field[ix, iy] * (1. - remainder_x) * (1. - remainder_y)
                + field[ix+1, iy] * remainder_x * (1. - remainder_y)
                + field[ix, iy+1] * (1. - remainder_x) * remainder_y
                + field[ix+1, iy+1] * remainder_x * remainder_y
            )

        # `positions.shape` happens to be the same shape that is required for Ex, Ey.
        Ex = np.empty(shape=positions.shape[1], dtype=float)
        Ey = np.empty(shape=positions.shape[1], dtype=float)

        phi_outside = np.arctan2(positions[1, outside], positions[0, outside])
        Ex[outside] = self._field_value_outside * np.cos(phi_outside)
        Ey[outside] = self._field_value_outside * np.sin(phi_outside)

        Ex[inside] = interpolate(self.Ex)
        Ey[inside] = interpolate(self.Ey)

        # Use self.Ez itself for searchsorted as it only contains a single item (namely zero).
        # Ez will be all zero, however depending on z it will be either a scalar or a numpy array.
        # So the indexing for self.Ez is done in order to automatically get the dimensions right.
        Ez = self.Ez[np.searchsorted(self.Ez, positions[2], side=str('right')) - 1]

        field_vector = np.stack((Ex, Ey, Ez))

        # Rescale with the ratio of current charge density to the z=0 reference density.
        particle_density_ratios = self._bunch_shape.normalized_density_at(
            np.vstack((
                np.zeros((2, positions.shape[1]), dtype=float),
                positions[2]
            ))
        ) / self._reference_particle_density

        return field_vector * particle_density_ratios * constants.elementary_charge


@parametrize(
    Triplet[Integer](
        'GridPoints',
        info='The number of grid points in x-, y- and z-direction.'
    ),
    Duplet[PhysicalQuantity](
        'XRange',
        unit='m',
        optional=True,
        info='Controls the grid extent in x-direction. If not given then the device boundaries '
             'are used as grid boundaries. However if the field is (almost) constant (or even '
             'negligible) at the device boundaries it might be more efficient to choose a smaller '
             'grid in order to get more precision in this region. The field value outside of the '
             'grid can be set via the `FieldValueOutside` parameter.'
    ),
    Duplet[PhysicalQuantity](
        'YRange',
        unit='m',
        optional=True,
        info='Controls the grid extent in y-direction. If not given then the device boundaries '
             'are used as grid boundaries. However if the field is (almost) constant (or even '
             'negligible) at the device boundaries it might be more efficient to choose a smaller '
             'grid in order to get more precision in this region. The field value outside of the '
             'grid can be set via the `FieldValueOutside` parameter.'
    ),
    Duplet[PhysicalQuantity](
        'ZRange',
        unit='m',
        optional=True,
        info='Controls the grid extent in z-direction. If not given then the bunch length '
             'is used to confine the grid. However if the field is (almost) constant (or even '
             'negligible) at the bunch tails it might be more efficient to choose a smaller '
             'grid in order to get more precision in this region. The field value outside of the '
             'grid can be set via the `FieldValueOutside` parameter.'
    ),
    PhysicalQuantity(
        'FieldValueOutside',
        unit='V/m',
        default=0.,
        info='This parameter controls the field value that is assumed for positions outside of '
             'the specified grid. Defaults to zero. Note that this value is not a boundary input '
             'for solving the Poisson equation. The Poisson equation is solved with Dirichlet '
             'boundary condition and the boundary value can be controlled via the parameter '
             '`DirichletBoundaryValue`. Also note that the resulting field vector will point '
             'towards the origin (in the bunch frame) which might be an invalid assumption '
             'depending on the underlying charge distribution (the more it is spherically '
             'symmetric the better this assumption is).'
    ),
    PhysicalQuantity(
        'DirichletBoundaryValue',
        unit='V',
        default=0.,
        info='The potential value at the grid boundaries which is used as an input for the '
             'Dirichlet boundary condition for solving the Poisson equation. Defaults to zero.'
    ),
    Choice(
        String(
            'PolynomialType',
            default='Lagrange',
            info='The type of polynomial to be used for the FEM solver.'
        )
    ).add_option(
        'Lagrange'
    ),
    Integer(
        'PolynomialDegree',
        default=1,
        info='The polynomial degree to be used for the FEM solver. Note that by increasing the '
             'degree of the polynomial the algorithm will also use more memory as it needs to '
             'store one coefficient per additional degree.'
    )
)
class Poisson3D(BunchElectricFieldModel):
    """
    Solve Poisson's equation in three dimension using the dolfin package from the FEniCS project.
    
    .. note::
       The solver must be used together with a :class:`BunchShape` class which provides its
       particle density as a string formula via :method:`~BunchShape.density_as_string`.
    """

    _fenics_download_link = 'https://fenicsproject.org/download/'

    def __init__(self, bunch_shape, device, configuration):
        super().__init__(bunch_shape, device, configuration)

        if dolfin is None:
            raise MissingOptionalDependencyError(
                '%s needs the dolfin package from the FEniCS project however this seems to be '
                'unavailable on your machine. Please visit %s for installation instructions.'
                % (self.__class__.__name__, self._fenics_download_link)
            ) from None
        try:
            bunch_shape.density_as_string
        except NotImplementedError:
            raise IncompatibleModelsError(
                'Bunch shape %s does not support `density_as_string` which is required by this '
                'solver'
                % bunch_shape.__class__.__name__
            ) from None
        self._bunch_shape = bunch_shape
        self._device = device
        self._e_over_eps0 = constants.elementary_charge / constants.epsilon_0

    # noinspection PyAttributeOutsideInit,PyPackageRequirements,PyUnresolvedReferences
    def prepare(self):
        """
        Solve Poisson's equation in order to obtain the electric potential and then compute the
        derivatives in order to obtain the electric field vectors (as (polynomial) functions).
        """
        super().prepare()

        self.log.info(
            "Solving Poisson's equation in order to obtain the beam fields. This may take some "
            "time ..."
        )

        from dolfin.common.constants import DOLFIN_EPS
        from dolfin.cpp.mesh import BoxMesh, Point
        from dolfin.fem.bcs import DirichletBC
        from dolfin.fem.solving import solve
        from dolfin.functions.constant import Constant
        from dolfin.functions.expression import Expression
        from dolfin.functions.function import Function, TestFunction, TrialFunction
        from dolfin.functions.functionspace import FunctionSpace
        from dolfin import dx, grad, inner, project

        if self._x_range is not None:
            x_min, x_max = self._x_range
        else:
            x_min, x_max = self._device.x_min, self._device.x_max

        if self._y_range is not None:
            y_min, y_max = self._y_range
        else:
            y_min, y_max = self._device.y_min, self._device.y_max

        if self._z_range is not None:
            z_min, z_max = self._z_range
        else:
            z_min, z_max = -1.0 * self._bunch_shape.length / 2., self._bunch_shape.length / 2.

        min_corner = Point(x_min, y_min, z_min)
        max_corner = Point(x_max, y_max, z_max)

        mesh = BoxMesh(min_corner, max_corner, *self._grid_points)
        function_space = FunctionSpace(mesh, str(self._polynomial_type), self._polynomial_degree)

        def boundary_domain(x):
            return (
                x[0] < x_min + DOLFIN_EPS or x[0] > x_max - DOLFIN_EPS
                or x[1] < y_min + DOLFIN_EPS or x[1] > y_max - DOLFIN_EPS
                # There is not device boundary in z-direction so we don't apply the boundary
                # condition there.
                # or x[2] < z_min + DOLFIN_EPS or x[2] > z_max - DOLFIN_EPS
            )

        boundary_value = Constant(self._dirichlet_boundary_value)
        boundary_condition = DirichletBC(function_space, boundary_value, boundary_domain)

        trial_function = TrialFunction(function_space)
        test_function = TestFunction(function_space)

        density_as_string = self._bunch_shape.density_as_string
        self.log.debug('Using source term: %s', density_as_string)
        source_term = Expression(str(density_as_string), degree=3)
        bilinear_form = inner(grad(trial_function), grad(test_function)) * dx
        linear_form = source_term * test_function * dx
        phi = Function(function_space)

        solve(
            bilinear_form == linear_form,
            phi,
            boundary_condition,
            solver_parameters={
                str('linear_solver'): str('mumps'),
            }
        )
        self._Ex = project(
            phi.dx(0), function_space,
            solver_type=str('cg'),
            preconditioner_type=str('amg')
        )
        self._Ey = project(
            phi.dx(1), function_space,
            solver_type=str('cg'),
            preconditioner_type=str('amg')
        )
        self._Ez = project(
            phi.dx(2), function_space,
            solver_type=str('cg'),
            preconditioner_type=str('amg')
        )

        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max
        self._z_min = z_min
        self._z_max = z_max

        self.log.info('... done.')

    # noinspection PyPep8Naming
    @use_docs_from(BunchElectricFieldModel)
    def eval(self, positions):
        outside = (
            (positions[0] < self._x_min)
            | (positions[0] > self._x_max)
            | (positions[1] < self._y_min)
            | (positions[1] > self._y_max)
            | (positions[2] < self._z_min)
            | (positions[2] > self._z_max)
        )
        inside = ~outside

        Ex = np.empty(shape=(positions.shape[1],), dtype=float)
        Ey = np.empty(shape=(positions.shape[1],), dtype=float)
        Ez = np.empty(shape=(positions.shape[1],), dtype=float)

        theta_outside = np.arccos(
            positions[2, outside]
            / np.sqrt(
                positions[0, outside] ** 2
                + positions[1, outside] ** 2
                + positions[2, outside] ** 2
            )
        )
        phi_outside = np.arctan2(
            positions[1, outside],
            positions[0, outside]
        )
        Ex[outside] = self._field_value_outside * np.sin(theta_outside) * np.cos(phi_outside)
        Ey[outside] = self._field_value_outside * np.sin(theta_outside) * np.sin(phi_outside)
        Ez[outside] = self._field_value_outside * np.cos(theta_outside)

        inside_indices = np.argwhere(inside).flatten()
        positions_transposed = np.transpose(positions[:, inside])
        for index, position in zip(inside_indices, positions_transposed):
            # Multiply by -1.0 because the field should be positive for positive positions but
            # because the potential (usually) is decreasing for positions farther from the origin
            # its derivative - the electric field - is negative.
            Ex[index] = -1.0 * self._Ex(position)
            Ey[index] = -1.0 * self._Ey(position)
            Ez[index] = -1.0 * self._Ez(position)
        return np.r_[str('0,2'), Ex, Ey, Ez] * self._e_over_eps0


# noinspection PyPep8Naming
class ParabolicEllipsoid(BunchElectricFieldModel):
    """
    The electric field of a parabolically charged ellipsoid. This is a rotational symmetric
    spheroid (with respect to the z-axis) whose charge decreases parabolically when going from
    the center outwards.
    
    .. note::
       This electric field model must be used together with the :class:`ParabolicEllipsoid` bunch
       shape.
    
    References
    ----------
    .. [1] P.Strehl: "Beam Instrumentation and Diagnostics" (Chapter 8: The electromagnetic fields
       of bunches), Springer, 2016
    .. [2] M.Dolinska (INR-Kiev), R.W.Mueller (GSI-Darmstadt), P.Strehl (GSI-Darmstadt):
       "The Electric Field of Bunches", July 5th 2000
    """

    def __init__(self, bunch_shape, device, configuration):
        super().__init__(bunch_shape, device, configuration)

        if not isinstance(bunch_shape, bunch_shapes.ParabolicEllipsoid):
            raise IncompatibleModelsError(
                'This field models requires an instance of %s as bunch shape'
                % bunch_shapes.ParabolicEllipsoid.__name__
            ) from None

        self._bunch_shape = bunch_shape

        P4 = ParabolicEllipsoid.P4
        P4_prime = ParabolicEllipsoid.P4_prime
        Q4 = ParabolicEllipsoid.Q4
        Q4_prime = ParabolicEllipsoid.Q4_prime

        P2 = ParabolicEllipsoid.P2
        P2_prime = ParabolicEllipsoid.P2_prime
        Q2 = ParabolicEllipsoid.Q2
        Q2_prime = ParabolicEllipsoid.Q2_prime

        Q0 = ParabolicEllipsoid.Q0
        Q0_prime = ParabolicEllipsoid.Q0_prime

        a = bunch_shape.semi_major_axis
        b = bunch_shape.semi_minor_axis
        c = np.sqrt(a**2 - b**2)

        # After Eq.(9).
        xi0 = a / c

        # After Eq.(5).
        # The ``N * zeta`` factor is accounted for in the Bunch class. The bunch electric field
        # models should return the field for a single charge (distributed as necessary).
        rho_0ep = (
            (15. * constants.elementary_charge)
            / (8. * constants.pi * a * b**2)
        )

        # Eq.(12) - (14).
        s1 = rho_0ep * a**2 / b**2
        s2 = -rho_0ep * c**2 / b**2
        s3 = rho_0ep * c**4 / (a**2 * b**2)

        # Eq.(30) - (32).
        A = -c**2 / constants.epsilon_0 * (s1 / 6. + s2 / 10.)
        B = -c**2 / constants.epsilon_0 * s2 / 20.
        C = -c**2 / constants.epsilon_0 * s3 / 12.

        # Eq.(37) - (39).
        PQ4 = Q4(xi0) * P4_prime(xi0) - Q4_prime(xi0) * P4(xi0)
        A4 = (
            8. / (35. * PQ4) * (
                P4_prime(xi0) * (B + C * xi0**4)
                - 4. * C * xi0**3 * P4(xi0)
            )
        )
        C4 = (
            1. / P4_prime(xi0) * (
                A4 * Q4_prime(xi0)
                - 32. / 35. * C * xi0**3
            )
        )

        # Eq.(40) - (44).
        PQ2 = Q2(xi0) * P2_prime(xi0) - Q2_prime(xi0) * P2(xi0)
        A_C4 = A4 * Q4(xi0) - C4 * P4(xi0)
        A_C4S = A4 * Q4_prime(xi0) - C4 * P4_prime(xi0)
        A2 = (
            2. / (3. * PQ2) * (
                P2_prime(xi0) * (A + 15./4. * A_C4)
                - P2(xi0) * 15./4. * A_C4S
            )
        )
        C2 = (
            1. / P2_prime(xi0) * (
                A2 * Q2_prime(xi0)
                - 5./2. * A_C4S
            )
        )

        # Eq.(45) - (48).
        A_C2 = A2 * Q2(xi0) - C2 * P2(xi0)
        A_C2S = A2 * Q2_prime(xi0) - C2 * P2_prime(xi0)
        A0 = 1. / Q0_prime(xi0) * (
            2. * A * xi0
            + 4. * B * xi0**3
            + 0.5 * A_C2S
            - 0.375 * A_C4S
        )
        C0 = (
            A0 * Q0(xi0)
            - A * xi0**2
            - B * xi0**4
            - 0.5 * A_C2
            + 0.375 * A_C4
        )

        self._coefficients = {
            'c': c,
            'A': A,
            'B': B,
            'C': C,
            'A4': A4,
            'C4': C4,
            'A2': A2,
            'C2': C2,
            'A0': A0,
            'C0': C0,
            'semi-major axis': self._bunch_shape.semi_major_axis,
            'semi-minor axis': self._bunch_shape.semi_minor_axis,
            'xi0': xi0,
        }

    @use_docs_from(BunchElectricFieldModel)
    def eval(self, positions):
        inside = self._bunch_shape.inside_from_3d_cartesian_coordinates(positions)
        outside = ~inside
        polar_coordinates_3d = self.transform_cartesian_coordinates_to_polar_coordinates(positions)
        elliptical_coordinates_2d = \
            self.transform_3d_polar_coordinates_to_2d_elliptical_coordinates(
                polar_coordinates_3d,
                self._coefficients
            )
        xi = elliptical_coordinates_2d[0]
        eta = elliptical_coordinates_2d[1]

        E_inside = self.E_field_vector_inside_in_polar_basis_from_elliptical_coordinates_safeguard
        E_outside = self.E_field_vector_outside_in_polar_basis_from_elliptical_coordinates
        electric_field_vectors_2d_polar = np.empty((2, len(xi)), dtype=float)
        electric_field_vectors_2d_polar[:, inside] = E_inside(
            xi[inside],
            eta[inside],
            self._coefficients
        )
        electric_field_vectors_2d_polar[:, outside] = E_outside(
            xi[outside],
            eta[outside],
            self._coefficients
        )

        # Electric field should point away from positive charges. The field here was computed for
        # a single positive charge.
        electric_field_vectors_2d_polar *= -1.0
        return np.stack((
            electric_field_vectors_2d_polar[0] * np.cos(polar_coordinates_3d[1]),
            electric_field_vectors_2d_polar[0] * np.sin(polar_coordinates_3d[1]),
            electric_field_vectors_2d_polar[1]
        ))

    @staticmethod
    def transform_cartesian_coordinates_to_polar_coordinates(positions):
        """
        Parameters
        ----------
        positions : :class:`np.ndarray`, shape (3, N)
            Cartesian coordinates (x, y, z).

        Returns
        -------
        polar_positions : :class:`np.ndarray`, shape (3, N)
            Polar coordinates (r, phi, z).
        """
        r = np.sqrt(positions[0]**2 + positions[1]**2)
        phi = np.arctan2(positions[1], positions[0])
        return np.stack((r, phi, positions[2]))

    # See Eq.(7)-(8).
    # noinspection PyUnresolvedReferences
    @staticmethod
    def transform_3d_polar_coordinates_to_2d_elliptical_coordinates(positions, coefficients):
        """
        Considering the upper half of a flat ellipse (independent of phi,
        r >= 0 corresponds to the y-coordinate, z corresponds to the x-coordinate of the 2D (flat)
        cartesian coordinate system). Starting from a 3D rotational invariant ellipsoid (with
        respect to the z-axis in a 3D polar coordinate system) we can make the transition to the
        upper half of a flat ellipse because the electric field is independent of phi (that
        includes mirroring at the z-axis). Starting from the polar coordinate system the
        z-coordinate is considered along the semi-major axis of the 2D ellipse and the r-coordinate
        is considered along the semi-minor axis.

        Parameters
        ----------
        positions : :class:`np.ndarray`, shape (3, N)
            Polar coordinates (r, phi, z). `r` is considered along the semi-minor axis of the
            ellipse and `z` is considered along the semi-major axis.
        coefficients : dict

        Returns
        -------
        elliptical_coordinates : :class:`np.ndarray`, shape (2, N)
            Elliptical coordinates (xi, eta); ``1 <= xi``, ``-1 <= eta <= 1``.
        """
        from numpy import sqrt

        z = positions[2]
        r = positions[0]
        c = coefficients['c']
        Q = c**2 + z**2 + r**2
        xi = 1. / sqrt(2. * c**2) * sqrt(Q + sqrt(Q**2 - 4. * z**2 * c**2))
        eta = z / (c * xi)

        # Because of floating point math it might happen that xi and/or eta are slightly out of
        # bounds (in the order of magnitude ~ 1e-15).
        assert np.all(
            (1. - xi[xi < 1.])
            < 1e-13
        ), 'xi out of bounds (> 1e-13)'
        xi[xi < 1.] = 1.
        assert np.all(
            (
                np.abs(eta[(eta < -1.) | (eta > 1.)])
                - 1.
            )
            < 1e-13
        ), 'eta out of bounds (> 1e-13)'
        eta[eta < -1.] = -1.
        eta[eta > 1.] = 1.

        return np.stack((xi, eta))

    # See Eq.(63) - (65).
    @staticmethod
    def E_field_vector_inside_in_polar_basis_from_elliptical_coordinates_safeguard(
            xi, eta, coefficients):
        """
        Proxy for
        :method:`~ElectricFieldOfParabolicEllipsoid.E_field_vector_inside_in_polar_basis_from_elliptical_coordinates`
        that checks if ``xi == abs(eta)``. For that special case the formulation derived from
        the corresponding limit is used instead because the normal formulation would contain
        a division by zero.
        
        .. note::
        The constraints ``1 <= xi`` & ``-1 <= eta <= 1`` imply that ``xi == abs(eta) == 1``.
        This is the case for the two focal points of the ellipse.
        
        Parameters
        ----------
        xi : :class:`np.ndarray`, shape (N,)
        eta : :class:`np.ndarray`, shape (N,)
        coefficients : dict
        
        Returns
        -------
        e_field : :class:`np.ndarray`, shape (2, N)
            The electric field in the basis of polar coordinates. Only the r- and z-component is
            given (in that order) because E_phi is zero.
        """
        E_xi_equals_eta = ParabolicEllipsoid\
            .E_field_vector_inside_in_polar_basis_from_elliptical_coordinates_xi_equals_eta
        E_xi_noneq_eta = ParabolicEllipsoid\
            .E_field_vector_inside_in_polar_basis_from_elliptical_coordinates

        xi_equals_eta = (xi == np.abs(eta))
        xi_noneq_eta = ~xi_equals_eta
        result = np.empty((2, len(xi)))
        result[:, xi_equals_eta] = E_xi_equals_eta(
            xi[xi_equals_eta],
            eta[xi_equals_eta],
            coefficients
        )
        result[:, xi_noneq_eta] = E_xi_noneq_eta(
            xi[xi_noneq_eta],
            eta[xi_noneq_eta],
            coefficients
        )
        return result

    # See Eq.(63) - (65).
    @staticmethod
    def E_field_vector_inside_in_polar_basis_from_elliptical_coordinates_xi_equals_eta(
            xi, eta, coefficients):
        """
        Computes the electric field vector in polar basis for positions inside the ellipsoid for
        the special case ``xi == abs(eta)``.
        
        .. note::
        The constraints ``1 <= xi`` & ``-1 <= eta <= 1`` imply that ``xi == abs(eta) == 1``.
        This is the case for the two focal points of the ellipse.
        
        Parameters
        ----------
        xi : :class:`np.ndarray`, shape (N,)
        eta : :class:`np.ndarray`, shape (N,)
        coefficients : dict
        
        Returns
        -------
        e_field : :class:`np.ndarray`, shape (2, N)
            The electric field in the basis of polar coordinates. Only the r- and z-component is
            given (in that order) because E_phi is zero.
        """
        Di_eta = ParabolicEllipsoid.Di_eta
        c = coefficients['c']
        return np.stack((
            np.zeros(len(xi), dtype=float),
            # Because eta is proportional to z and in this special case `eta = +/-1` we can just
            # multiply by eta in order to get the sign right.
            eta / c * Di_eta(xi, eta, coefficients)
        ))

    # See Eq.(63) - (65).
    @staticmethod
    def E_field_vector_inside_in_polar_basis_from_elliptical_coordinates(xi, eta, coefficients):
        """
        Computes the electric field vector in polar basis for positions inside the ellipsoid.
        
        Parameters
        ----------
        xi : :class:`np.ndarray`, shape (N,)
        eta : :class:`np.ndarray`, shape (N,)
        coefficients : dict
        
        Returns
        -------
        e_field : :class:`np.ndarray`, shape (2, N)
            The electric field in the basis of polar coordinates. Only the r- and z-component is
            given (in that order) because E_phi is zero.
        """
        from numpy import sqrt

        Di_eta = ParabolicEllipsoid.Di_eta
        Di_xi = ParabolicEllipsoid.Di_xi
        c = coefficients['c']
        E_r = sqrt(xi**2 - 1.) * sqrt(1. - eta**2) / (c * (xi**2 - eta**2)) * (
            xi * Di_xi(xi, eta, coefficients)
            - eta * Di_eta(xi, eta, coefficients)
        )
        E_z = 1. / (c * (xi**2 - eta**2)) * (
            eta * (xi**2 - 1.) * Di_xi(xi, eta, coefficients)
            + xi * (1. - eta**2) * Di_eta(xi, eta, coefficients)
        )
        return np.stack((E_r, E_z))

    # See Eq.(63) - (65).
    @staticmethod
    def E_field_vector_outside_in_polar_basis_from_elliptical_coordinates(xi, eta, coefficients):
        """
        Computes the electric field vector in polar basis for positions inside the ellipsoid.
        
        Parameters
        ----------
        xi : :class:`np.ndarray`, shape (N,)
        eta : :class:`np.ndarray`, shape (N,)
        coefficients : dict
        
        Returns
        -------
        e_field : :class:`np.ndarray`, shape (2, N)
            The electric field in the basis of polar coordinates. Only the r- and z-component is
            given (in that order) because E_phi is zero. 
        """
        from numpy import sqrt

        Do_eta = ParabolicEllipsoid.Do_eta
        Do_xi = ParabolicEllipsoid.Do_xi
        c = coefficients['c']
        E_r = sqrt(xi ** 2 - 1.) * sqrt(1. - eta ** 2) / (c * (xi ** 2 - eta ** 2)) * (
            xi * Do_xi(xi, eta, coefficients)
            - eta * Do_eta(xi, eta, coefficients)
        )
        E_z = 1. / (c * (xi ** 2 - eta ** 2)) * (
            eta * (xi ** 2 - 1.) * Do_xi(xi, eta, coefficients)
            + xi * (1. - eta ** 2) * Do_eta(xi, eta, coefficients)
        )
        return np.stack((E_r, E_z))

    @staticmethod
    def E_ipe_safeguard(xi, eta, coefficients):
        """
        Proxy for :method:`~ElectricFieldOfParabolicEllipsoid.E_ipe` that checks if
        ``xi == abs(eta)``. For that special case the formulation derived from the corresponding
        limit is used instead because the normal formulation would contain a division by zero.
        
        .. note::
        The constraints ``1 <= xi`` & ``-1 <= eta <= 1`` imply that ``xi == abs(eta) == 1``.
        This is the case for the two focal points of the ellipse.
        """
        result = np.empty(len(xi))
        xi_equals_eta = (xi == np.abs(eta))
        result[xi_equals_eta] = ParabolicEllipsoid.E_ipe_xi_equals_eta(xi, eta, coefficients)
        result[~xi_equals_eta] = ParabolicEllipsoid.E_ipe(xi, eta, coefficients)
        return result

    # See Eq.(55).
    @staticmethod
    def E_ipe(xi, eta, coefficients):
        c = coefficients['c']
        Di_xi = ParabolicEllipsoid.Di_xi
        Di_eta = ParabolicEllipsoid.Di_eta
        return 1. / (c * np.sqrt(xi**2 - eta**2)) * np.sqrt(
            (xi**2 - 1.) * Di_xi(xi, eta, coefficients)**2
            + (1. - eta**2) * Di_eta(xi, eta, coefficients)**2
        )

    # See Eq.(55).
    @staticmethod
    def E_ipe_xi_equals_eta(xi, eta, coefficients):
        c = coefficients['c']
        Di_xi = ParabolicEllipsoid.Di_xi
        Di_eta = ParabolicEllipsoid.Di_eta
        return 1. / c * np.sqrt(
            Di_xi(xi, eta, coefficients) ** 2
            + Di_eta(xi, eta, coefficients)**2
        )

    # See Eq.(58).
    @staticmethod
    def E_ope(xi, eta, coefficients):
        c = coefficients['c']
        Do_xi = ParabolicEllipsoid.Do_xi
        Do_eta = ParabolicEllipsoid.Do_eta
        return 1. / (c * np.sqrt(xi**2 - eta**2)) * np.sqrt(
            (xi**2 - 1.) * Do_xi(xi, eta, coefficients)**2
            + (1. - eta**2) * Do_eta(xi, eta, coefficients)**2
        )

    # See Eq.(56).
    @staticmethod
    def Di_xi(xi, eta, coefficients):
        A = coefficients['A']
        B = coefficients['B']
        C = coefficients['C']
        C2 = coefficients['C2']
        C4 = coefficients['C4']
        P2 = ParabolicEllipsoid.P2
        P2_prime = ParabolicEllipsoid.P2_prime
        P4 = ParabolicEllipsoid.P4
        P4_prime = ParabolicEllipsoid.P4_prime
        return (
            2. * A * xi
            + 4. * B * xi**3
            + 4. * C * xi**3 * eta**4
            + C2 * P2_prime(xi) * P2(eta)
            + C4 * P4_prime(xi) * P4(eta)
        )

    # See Eq.(57).
    @staticmethod
    def Di_eta(xi, eta, coefficients):
        A = coefficients['A']
        B = coefficients['B']
        C = coefficients['C']
        C2 = coefficients['C2']
        C4 = coefficients['C4']
        P2 = ParabolicEllipsoid.P2
        P2_prime = ParabolicEllipsoid.P2_prime
        P4 = ParabolicEllipsoid.P4
        P4_prime = ParabolicEllipsoid.P4_prime
        return (
            2. * A * eta
            + 4. * B * eta ** 3
            + 4. * C * eta ** 3 * xi ** 4
            + C2 * P2_prime(eta) * P2(xi)
            + C4 * P4_prime(eta) * P4(xi)
        )

    # See Eq.(59).
    @staticmethod
    def Do_xi(xi, eta, coefficients):
        A0 = coefficients['A0']
        A2 = coefficients['A2']
        A4 = coefficients['A4']
        P2 = ParabolicEllipsoid.P2
        P4 = ParabolicEllipsoid.P4
        Q0_prime = ParabolicEllipsoid.Q0_prime
        Q2_prime = ParabolicEllipsoid.Q2_prime
        Q4_prime = ParabolicEllipsoid.Q4_prime
        return (
            A0 * Q0_prime(xi)
            + A2 * Q2_prime(xi) * P2(eta)
            + A4 * Q4_prime(xi) * P4(eta)
        )

    # See Eq.(60).
    @staticmethod
    def Do_eta(xi, eta, coefficients):
        A2 = coefficients['A2']
        A4 = coefficients['A4']
        Q2 = ParabolicEllipsoid.Q2
        Q4 = ParabolicEllipsoid.Q4
        P2_prime = ParabolicEllipsoid.P2_prime
        P4_prime = ParabolicEllipsoid.P4_prime
        return (
            A2 * Q2(xi) * P2_prime(eta)
            + A4 * Q4(xi) * P4_prime(eta)
        )

    # noinspection PyUnusedLocal
    @staticmethod
    def P0(x):
        return 1.0

    # noinspection PyUnusedLocal
    @staticmethod
    def P0_prime(x):
        return 0.

    @staticmethod
    def P1(x):
        return x

    # noinspection PyUnusedLocal
    @staticmethod
    def P1_prime(x):
        return 1.0

    @staticmethod
    def P2(x):
        return 1.5 * x**2 - 0.5

    @staticmethod
    def P2_prime(x):
        return 3. * x

    @staticmethod
    def P3(x):
        return 2.5 * x**3 - 1.5 * x

    @staticmethod
    def P3_prime(x):
        return 7.5 * x**2 - 1.5

    @staticmethod
    def P4(x):
        return 0.125 * (35.0 * x**4 - 30.0 * x**2 + 3.0)

    @staticmethod
    def P4_prime(x):
        return 17.5 * x**3 - 7.5 * x

    # See Eq.(21) - (23) for definition of the Q-polynoms.
    @staticmethod
    def Q0(x):
        return 0.5 * np.log((x + 1.) / (x - 1.))

    @staticmethod
    def Q0_prime(x):
        return 1. / (1. - x**2)

    @staticmethod
    def Q1(x):
        Q0 = ParabolicEllipsoid.Q0
        return x * Q0(x) - 1.0

    @staticmethod
    def Q1_prime(x):
        Q0 = ParabolicEllipsoid.Q0
        Q0_prime = ParabolicEllipsoid.Q0_prime
        return Q0(x) + x * Q0_prime(x)

    @staticmethod
    def Q2(x):
        Q0 = ParabolicEllipsoid.Q0
        return (
            0.5 * (3. * x**2 - 1.) * Q0(x)
            - 1.5*x
        )

    @staticmethod
    def Q2_prime(x):
        Q0 = ParabolicEllipsoid.Q0
        Q0_prime = ParabolicEllipsoid.Q0_prime
        return (
            3. * x * Q0(x)
            + 0.5 * (3. * x**2 - 1.) * Q0_prime(x)
            - 1.5
        )

    @staticmethod
    def Q3(x):
        Q0 = ParabolicEllipsoid.Q0
        return (
            0.5 * (5. * x**3 - 3. * x) * Q0(x)
            + (-2.5 * x**2 + 2./3.)
        )

    @staticmethod
    def Q3_prime(x):
        Q0 = ParabolicEllipsoid.Q0
        Q0_prime = ParabolicEllipsoid.Q0_prime
        return (
            0.5 * (15. * x**2 - 3.) * Q0(x)
            + 0.5 * (5. * x**3 - 3. * x) * Q0_prime(x)
            - 5. * x
        )

    @staticmethod
    def Q4(x):
        Q0 = ParabolicEllipsoid.Q0
        return (
            0.125 * (
                35. * x**4
                - 30. * x**2
                + 3.
            ) * Q0(x)
            + (-105. * x**3 + 55. * x) / 24.
        )

    @staticmethod
    def Q4_prime(x):
        Q0 = ParabolicEllipsoid.Q0
        Q0_prime = ParabolicEllipsoid.Q0_prime
        return (
            0.5 * (35. * x**3 - 15. * x) * Q0(x)
            + 0.125 * (
                35. * x ** 4
                - 30. * x ** 2
                + 3.
            ) * Q0_prime(x)
            + (-315. * x**2 + 55.) / 24.
        )
