'''
    This file is part of SerialBox.

    SerialBox is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SerialBox is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with SerialBox.  If not, see <http://www.gnu.org/licenses/>.
'''

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PoolsConfig(AppConfig):
    name = 'serialbox'
    verbose_name = _("SerialBox")

    def __init__(self, app_name, app_module):
        AppConfig.__init__(self, app_name, app_module)
        self.name = app_name

    def ready(self):
        pass
