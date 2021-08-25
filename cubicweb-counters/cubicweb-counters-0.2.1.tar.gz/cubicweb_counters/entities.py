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
"""cubicweb-counters entity's classes"""

from datetime import datetime

from cubicweb.entities import AnyEntity

# XXX why lock + separate connection on eid_creation_cnx


def _need_reset_year(now, last_update):
    return now.year != last_update.year


def _need_reset_month(now, last_update):
    return now.month != last_update.month or now.year != last_update.year


def _need_reset_day(now, last_update):
    return (
        now.day != last_update.day
        or now.month != last_update.month
        or now.year != last_update.year
    )


RESET_MODES = {
    "year": _need_reset_year,
    "month": _need_reset_month,
    "day": _need_reset_day,
}


def need_reset(last_update, reset_mode):
    if not reset_mode:
        return False
    return RESET_MODES[reset_mode](datetime.now(), last_update)


class PeriodicallyResetCounter(AnyEntity):
    __regid__ = "PeriodicallyResetCounter"

    def dc_title(self):
        if self.name:
            return self.name
        return "{} #{}".format(self.dc_type(), self.eid)

    def next_value(self):
        """repository only method to use to retrieve next counter value"""
        # update to lock the row
        self._cw.system_sql(
            "UPDATE cw_%s SET cw_value=cw_value+%s WHERE cw_eid=%s"
            % (self.__regid__, self.increment, self.eid)
        )
        cu = self._cw.system_sql(
            """SELECT cw_value, cw_reset_on, cw_reset_every FROM cw_%s
            WHERE cw_eid=%s"""
            % (self.__regid__, self.eid)
        )
        value, reset_on, reset_mode = cu.fetchone()
        # check if we've to reset the counter
        if need_reset(reset_on, reset_mode):
            value = self.initial_value + self.increment
            self._cw.system_sql(
                """UPDATE cw_%s SET cw_value=%%(value)s,
                cw_reset_on=%%(now)s WHERE cw_eid=%s"""
                % (self.__regid__, self.eid),
                {"value": value, "now": datetime.now()},
            )
        return value


# XXX creation hook to initialise cw_value
