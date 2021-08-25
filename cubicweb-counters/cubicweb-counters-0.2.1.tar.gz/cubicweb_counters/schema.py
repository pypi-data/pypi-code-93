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
"""cubicweb-counters schema"""

from yams.buildobjs import EntityType, String, Int, Datetime

from cubicweb import _


class PeriodicallyResetCounter(EntityType):
    name = String(maxsize=256, indexed=True)
    #
    initial_value = Int(required=True, default=0)
    increment = Int(required=True, default=1)
    reset_every = String(
        vocabulary=[_(""), _("year"), _("month"), _("day")], default=u"year"
    )
    # internally handled attributes
    value = Int(__permissions__={"read": ("managers",), "update": ()})
    reset_on = Datetime(__permissions__={"read": ("managers",), "update": ()})
