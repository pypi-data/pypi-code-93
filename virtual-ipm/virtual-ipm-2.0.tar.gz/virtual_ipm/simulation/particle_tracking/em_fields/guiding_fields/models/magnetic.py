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

from anna import PhysicalQuantity, Triplet, parametrize
from anna.utils import use_docs_from
import injector
import numpy as np

import virtual_ipm.di as di

from .mixin import GuidingFieldModel, CSVAdaptor2D, CSVAdaptor3D, UniformGuidingField


# noinspection PyAbstractClass,PyOldStyleClasses
class MagneticGuidingFieldModel(GuidingFieldModel):
    """
    (Abstract) Base class for magnetic guiding field models.
    """

    CONFIG_PATH_TO_IMPLEMENTATION = 'GuidingFields/Magnetic/Model'
    CONFIG_PATH = 'GuidingFields/Magnetic/Parameters'

    def __init__(self, configuration=None):
        super().__init__(configuration)

Interface = MagneticGuidingFieldModel


@parametrize(
    _field_vector=Triplet[PhysicalQuantity](
        'MagneticField', 'T'
    ).use_container(np.array)
)
class UniformMagneticField(UniformGuidingField, MagneticGuidingFieldModel):
    """
    Constant, uniform magnetic field.
    """

    CONFIG_PATH = MagneticGuidingFieldModel.CONFIG_PATH

    @injector.inject(
        configuration=di.components.configuration
    )
    def __init__(self, configuration):
        super().__init__(configuration)


class NoMagneticField(UniformMagneticField):
    """
    Use this model if no magnetic field is present (zero magnetic field).
    """
    _field_vector = np.zeros(3, dtype=float)

    @injector.inject(
        configuration=di.components.configuration
    )
    def __init__(self, configuration=None):
        super().__init__(configuration=configuration)


class MagneticCSVAdaptor2D(CSVAdaptor2D, MagneticGuidingFieldModel):
    """
    Magnetic field in two dimensions whose values are read from a CST file.
    """

    CONFIG_PATH = MagneticGuidingFieldModel.CONFIG_PATH

    @injector.inject(
        configuration=di.components.configuration
    )
    def __init__(self, configuration):
        super().__init__(configuration)

    @use_docs_from(MagneticGuidingFieldModel)
    def eval(self, position_four_vector, progress):
        return super().eval(position_four_vector, progress)


class MagneticCSVAdaptor3D(CSVAdaptor3D, MagneticGuidingFieldModel):
    """
    Magnetic field in three dimensions whose values are read from a CST file.
    """

    CONFIG_PATH = MagneticGuidingFieldModel.CONFIG_PATH

    @injector.inject(
        configuration=di.components.configuration
    )
    def __init__(self, configuration):
        super().__init__(configuration)

    @use_docs_from(MagneticGuidingFieldModel)
    def eval(self, position_four_vector, progress):
        return super().eval(position_four_vector, progress)
