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

import logging

from rx.subjects import Subject


format_string = '[%(levelname)s] %(name)s ( %(funcName)s ): %(message)s'

root_logger = logging.getLogger(str('virtual_ipm'))
root_logger.setLevel(logging.DEBUG)
null_handler = logging.NullHandler()
root_logger.addHandler(null_handler)


def add_handler(handler):
    root_logger.addHandler(handler)


def remove_handler(handler):
    root_logger.removeHandler(handler)


def to_console(level=logging.DEBUG):
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format_string))
    handler.setLevel(level)

    root_logger.addHandler(handler)


def to_file(filename, level=logging.DEBUG):
    handler = logging.FileHandler(filename, mode='w')
    handler.setFormatter(logging.Formatter(format_string))
    handler.setLevel(level)

    root_logger.addHandler(handler)


class SubjectHandler(logging.Handler):
    def __init__(self, format_string_='[%(levelname)s] %(message)s', level=logging.INFO):
        super().__init__(level)
        self.setFormatter(logging.Formatter(format_string_))
        self._records = Subject()

    def emit(self, record):
        self._records.on_next(self.format(record))

    @property
    def records(self):
        return self._records
