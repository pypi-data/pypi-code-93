#!/usr/bin/env python3

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

"""Création d'un modèle d'exercice."""

import logging
import os
import shutil
import textwrap

from pyromaths.ex import TexExercise
from pyromaths.outils.System import Fiche

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    )

class DummyExercise(TexExercise):
    """Faux exercice, servant de modèle pour les nouveaux exercices."""

    tags = []

    def tex_statement(self):
        return textwrap.dedent(r"""
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            % DÉBUT DE L'ÉNONCÉ
            \exercice

            ÉNONCÉ DE L'EXERCICE

            % FIN DE L'ÉNONCÉ
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        """)

    def tex_answer(self):
        return textwrap.dedent(r"""
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            % DÉBUT DU CORRIGÉ
            \exercice*

            CORRIGÉ DE L'EXERCICE

            % FIN DU CORRIGÉ
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        """)

PARAMETRES = {
    'enonce': True,
    'corrige': True,
    'exercices': [DummyExercise()],
    }
TEXFILE = "dummy.tex"
PDFFILE = "dummy.pdf"

def main():
    """Fonction principale."""
    with Fiche(PARAMETRES) as fiche:
        fiche.write_tex()
        shutil.copy(fiche.texname, TEXFILE)
        fiche.write_pdf()
        shutil.copy(fiche.pdfname, PDFFILE)
        fiche.show_pdf(PDFFILE)
    logging.info("Le modèle de document est disponible dans le fichier '%s'.", TEXFILE)

if __name__ == "__main__":
    main()
