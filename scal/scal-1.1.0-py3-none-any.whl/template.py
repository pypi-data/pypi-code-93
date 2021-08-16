#!/usr/bin/env python3

# Copyright Louis Paternault 2011-2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Calendar generation"""

import os

import jinja2

from scal import VERSION, __DATE__
import scal


def generate_tex(calendar, template=None, weeks=None):
    """Generate TeX code producing calendar represented in argument.

    :arg Calendar calendar: A :class:`Calendar` object.
    :arg str template: The name of a template to use. Use ``None`` for default
        template.
    """
    if template is None:
        loader = jinja2.PackageLoader("scal.data")
        template = "template.tex"
    else:
        loader = jinja2.FileSystemLoader("/")
        template = os.path.abspath(template)
    if weeks is None:
        weeks = scal.calendar.parse_weeks("none")

    environment = jinja2.Environment(loader=loader)
    environment.block_start_string = "(*"
    environment.block_end_string = "*)"
    environment.variable_start_string = "(("
    environment.variable_end_string = "))"
    environment.comment_start_string = "(% comment %)"
    environment.comment_end_string = "(% endcomment %)"
    environment.line_comment_prefix = "%!"
    # environment.filters['escape_tex'] = _escape_tex
    environment.trim_blocks = True
    environment.lstrip_blocks = True
    return environment.get_template(template).render(
        {  # pylint: disable=maybe-no-member
            "start": calendar.start,
            "end": calendar.end,
            "nb_months": calendar.months_count(),
            "holidays": calendar.holidays,
            "config": calendar.config,
            "years": calendar.year_boundaries(),
            "weeks": calendar.weeks(weeks["work"], weeks["iso"]),
            "version": "`scal` version {}".format(VERSION),
            "copyrightdate": __DATE__,
        }
    )
