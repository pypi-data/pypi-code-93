# Pyromaths
#
# Un programme en Python qui permet de créer des fiches d'exercices types de
# mathématiques niveau collège ainsi que leur corrigé en LaTeX.
#
# Copyright (C) 2018 -- Louis Paternault (spalax@gresille.org)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""Classes et fonctions de jinja2 adaptées pour LaTeX."""

from jinja2 import *

class LatexEnvironment(Environment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.block_start_string = '(*'
        self.block_end_string = '*)'
        self.variable_start_string = '(('
        self.variable_end_string = '))'
        self.comment_start_string = '(% '
        self.comment_end_string = ' %)'
        self.trim_blocks = True
        self.lstrip_blocks = True
