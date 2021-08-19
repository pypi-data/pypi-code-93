# copyright 2011-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-counters specific hooks and operations"""

from datetime import datetime

from cubicweb.predicates import is_instance
from cubicweb.server import hook


class InitCounter(hook.Hook):
    __regid__ = "counters.init"
    __select__ = is_instance("PeriodicallyResetCounter")
    events = ("before_add_entity",)

    def __call__(self):
        if self.entity.initial_value is None:
            value = self.entity.e_schema.default("initial_value")
        else:
            value = self.entity.initial_value
        self.entity.cw_edited["value"] = value
        self.entity.cw_edited["reset_on"] = datetime.now()
