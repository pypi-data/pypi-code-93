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

from anna.configuration import Configurable
from anna.configuration import _ConfigMeta
import logging

from virtual_ipm.utils import to_json_string


class _ComponentType(_ConfigMeta):
    # noinspection PyMethodParameters
    def __new__(mcs, name, bases, attributes):
        attributes['log'] = logging.getLogger('{0}.{1}'.format(__name__, name))
        return super().__new__(mcs, name, bases, attributes)


class _MutableType(_ComponentType):
    # noinspection PyMethodParameters
    def __new__(mcs, name, bases, attributes):
        config_path_to_implementation = attributes.get('CONFIG_PATH_TO_IMPLEMENTATION', None)
        if config_path_to_implementation is None:
            inherited_by = map(
                lambda base: getattr(base, str('CONFIG_PATH_TO_IMPLEMENTATION'), None) is not None,
                bases
            )
            if not any(inherited_by):
                attributes['CONFIG_PATH_TO_IMPLEMENTATION'] = name
        return super().__new__(mcs, name, bases, attributes)


class Component(Configurable, metaclass=_ComponentType):
    log = logging.getLogger('{0}.{1}'.format(__name__, 'Component'))

    def __init__(self, configuration=None):
        super().__init__(configuration)

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        return dict(
            super().as_json(),
            __class__=self.__class__.__name__
        )

    def prepare(self):
        self.log.debug('Preparing %s', self)


class Mutable(Component, metaclass=_MutableType):
    CONFIG_PATH_TO_IMPLEMENTATION = None

    def __init__(self, configuration=None):
        super().__init__(configuration)


class Model(Mutable):
    def __init__(self, configuration=None):
        super().__init__(configuration)

    def foo(self):
        self.log.debug('test')


class Manager(Component):
    def __init__(self):
        super().__init__()
