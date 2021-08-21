#!/usr/bin/env python3

# Pyromaths
# Un programme en Python qui permet de créer des fiches d'exercices types de
# mathématiques niveau collège ainsi que leur corrigé en LaTeX.
# Copyright (C) 2006 -- Jérôme Ortais (jerome.ortais@pyromaths.org)
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
#

from math import copysign

from pyromaths.classes.PolynomesCollege import Polynome
from pyromaths.classes.Fractions import Fraction
import random

from pyromaths.ex import Jinja2Exercise
from pyromaths.outils.jinja2utils import facteur


class LimitesSuites(Jinja2Exercise):
    """
    Exercice de terminale : Établir la convergence d’une suite, ou sa divergence vers + ∞ ou – ∞.
    """

    tags = ["Term Spé math"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = []
        polynome = [[random.choice([-1, 1]) * random.randint(1, 9), i] for i in range(4)]
        polynome[random.randint(1, 3)][0] = 0
        if polynome[3][0]:
            polynome[2][0] = copysign(polynome[2][0], polynome[3][0])
            polynome[1][0] = copysign(polynome[1][0], polynome[3][0])
        else:
            polynome[1][0] = copysign(polynome[1][0], polynome[2][0])
        random.shuffle(polynome)
        polynome = Polynome(polynome, "n")
        polynome_ord = polynome.ordonne()
        l1 = r"-\infty" if polynome_ord[0][0] < 0 else r"+\infty"
        questions.append({"cas": 1, "polynome": polynome, "polynome_ord": polynome_ord, "l1": l1})

        polynome = [[random.choice([-1, 1]) * random.randint(1, 9), i] for i in range(4)]
        polynome[random.randint(1, 3)][0] = 0
        if polynome[3][0]:
            polynome[2][0] = -copysign(polynome[2][0], polynome[3][0])
            polynome[1][0] = -copysign(polynome[1][0], polynome[3][0])
        else:
            polynome[1][0] = -copysign(polynome[1][0], polynome[2][0])
        random.shuffle(polynome)
        polynome = Polynome(polynome, "n")
        polynome_ord = polynome.ordonne()
        l1 = r"-\infty" if polynome_ord[0][0] < 0 else r"+\infty"
        l2 = r"-\infty" if polynome_ord[1][0] < 0 else r"+\infty"
        degre = polynome.degre()
        questions.append(
            {"cas": 2, "polynome": polynome, "polynome_ord": polynome_ord, "l1": l1, "l2": l2, "degre": degre})

        # Quotient qui diverge vers l'infini
        polynome1 = [[random.choice([-1, 1]) * random.randint(1, 9), i] for i in range(4)]
        polynome1[random.randint(1, 2)][0] = 0
        random.shuffle(polynome1)
        polynome1 = Polynome(polynome1, "n")
        polynome1_ord = polynome1.ordonne()
        l1 = r"-\infty" if polynome1_ord[0][0] < 0 else r"+\infty"
        degre1 = polynome1.degre()
        polynome2 = [[random.choice([-1, 1]) * random.randint(1, 9), i] for i in range(4)]
        polynome2[3][0] = 0
        random.shuffle(polynome2)
        polynome2 = Polynome(polynome2, "n")
        polynome2_ord = polynome2.ordonne()
        l2 = r"-\infty" if polynome2_ord[0][0] < 0 else r"+\infty"
        lim = Fraction(polynome1_ord[0][0], polynome2_ord[0][0]).simplifie()
        degre2 = polynome2.degre()
        questions.append(
            {"cas": 3, "polynome1": polynome1, "polynome1_ord": polynome1_ord, "l1": l1, "degre1": degre1,
             "polynome2": polynome2, "polynome2_ord": polynome2_ord, "l2": l2, "degre2": degre2, "lim": lim})

        # Quotient qui converge vers zéro
        polynome1 = [[random.choice([-1, 1]) * random.randint(1, 9), i] for i in range(4)]
        polynome1[3][0] = 0
        random.shuffle(polynome1)
        polynome1 = Polynome(polynome1, "n")
        polynome1_ord = polynome1.ordonne()
        l1 = r"-\infty" if polynome1_ord[0][0] < 0 else r"+\infty"
        degre1 = polynome1.degre()
        polynome2 = [[random.choice([-1, 1]) * random.randint(1, 9), i] for i in range(4)]
        polynome2[random.randint(1, 2)][0] = 0
        random.shuffle(polynome2)
        polynome2 = Polynome(polynome2, "n")
        polynome2_ord = polynome2.ordonne()
        l2 = r"-\infty" if polynome2_ord[0][0] < 0 else r"+\infty"
        lim = Fraction(polynome1_ord[0][0], polynome2_ord[0][0]).simplifie()
        degre2 = polynome2.degre()
        questions.append(
            {"cas": 4, "polynome1": polynome1, "polynome1_ord": polynome1_ord, "l1": l1, "degre1": degre1,
             "polynome2": polynome2, "polynome2_ord": polynome2_ord, "l2": l2, "degre2": degre2, "lim": lim})

        # Quotient qui converge
        i = random.randint(1, 3)
        polynome1 = [[random.choice([-1, 1]) * random.randint(1, 9), i] for i in range(4)]
        polynome1[i][0] = 0
        random.shuffle(polynome1)
        polynome1 = Polynome(polynome1, "n")
        polynome1_ord = polynome1.ordonne()
        l1 = r"-\infty" if polynome1_ord[0][0] < 0 else r"+\infty"
        degre1 = polynome1.degre()
        polynome2 = [[random.choice([-1, 1]) * random.randint(1, 9), i] for i in range(4)]
        polynome2[i][0] = 0
        random.shuffle(polynome2)
        polynome2 = Polynome(polynome2, "n")
        polynome2_ord = polynome2.ordonne()
        l2 = r"-\infty" if polynome2_ord[0][0] < 0 else r"+\infty"
        lim = Fraction(polynome1_ord[0][0], polynome2_ord[0][0]).simplifie()
        degre2 = polynome2.degre()
        questions.append(
            {"cas": 5, "polynome1": polynome1, "polynome1_ord": polynome1_ord, "l1": l1, "degre1": degre1,
             "polynome2": polynome2, "polynome2_ord": polynome2_ord, "l2": l2, "degre2": degre2, "lim": lim})

        random.shuffle(questions)
        suites = ["u_n", "v_n", "w_n", "s_n", "t_n"]
        for i, q in enumerate(questions):
            q["suite"] = suites[i]
        self.context = {
            "questions": questions,
        }

    @property
    def environment(self):
        environment = super().environment
        environment.filters.update({
            'facteur': facteur,
            'Polynome': Polynome,
        })
        return environment
