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

import random
from pyromaths.outils import Arithmetique, Affichage
from pyromaths.ex import LegacyExercise
from pyromaths.ex import Jinja2Exercise
from pyromaths.outils.jinja2utils import facteur

#===============================================================================
# Poser des opérations
#===============================================================================
class PoserDesOperations(Jinja2Exercise):
    """Poser des opérations (sauf divisions)"""

    tags = ['Sixième', 'Nombres et calculs', 'Calcul posé', 'Cycle 3']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        SommeValues = self.valeurs_sommes()
        DiffValues = self.valeurs_diff()
        ProdValues = self.valeurs_prod()
        ordre = ["somme", "diff", "produit"]
        random.shuffle(ordre)
        self.context = {
            "ordre": ordre,
            "Sna": SommeValues[0],
            "Sta": SommeValues[1],
            "Snb": SommeValues[2],
            "Stb": SommeValues[3],
            "Str": SommeValues[4],
            "Stt": SommeValues[5],
            "Dna": DiffValues[0],
            "Dta": DiffValues[1],
            "Dnb": DiffValues[2],
            "Dtb": DiffValues[3],
            "Dtrh": DiffValues[4],
            "Dtrb": DiffValues[5],
            "Dtt": DiffValues[6],
            "Pna": ProdValues[0],
            "Pnb": ProdValues[1],
            "Ppa": ProdValues[2],
            "Ppb": ProdValues[3],
            "alignement": ProdValues[4],
        }


    @property
    def environment(self):
        environment = super().environment
        environment.filters.update({
            'facteur': facteur,
            })
        return environment

    def splitDecimal(self, nb):
        """
        Retourne une liste contenant la partie entière puis la partie décimale d'un nombre
        :param nb: int or Decimal
        :return: list
        """
        s =format(nb, ".14g") # Convertit un float en un décimal
        try:
            p = s.index('.')
            l = [s[:p], s[p+1:]]
        except ValueError:
            "Il s'agit d'un entier"
            l=[s, '']
        return l

    def valeurs_sommes(self):
        """
        Sélectionne un nombre entier et un nombre décimal non entier pour poser une somme
        :return:
            Sna, Snb: int or float
            Sta, Stb, Stt, Str: justified strings
        """
        Sna = random.randrange(111, 100000) # Nombre entier
        Snb = (random.randrange(11, 10000)*10+random.randrange(1,10)) / 10**random.randrange(1,3) # Nombre décimal non entier
        la = self.splitDecimal(Sna)
        lb = self.splitDecimal(Snb)
        lt = self.splitDecimal(Sna + Snb)
        "Justifie les nombres sous forme de texte pour que les virgules soient alignées"
        alignement = '{:>' + str(len(lt[0])) + '}.{:0>' +str(max(len(la[1]), len(lb[1]))) + '}'
        Sta = alignement.format(la[0], la[1])
        Stb = alignement.format(lb[0], lb[1])
        Stt = alignement.format(lt[0], lt[1])
        Str = self.retenues_somme(Sta, Stb)
        "Mélange l'ordre des deux valeurs"
        if random.randrange(2):
            return Sna, Sta, Snb, Stb, Str, Stt
        else:
            return Snb, Stb, Sna, Sta, Str, Stt

    def valeurs_diff(self):
        """
        Sélectionne un nombre entier et un nombre décimal non entier pour poser une différence
        :return:
            Sna, Snb: int or float
            Sta, Stb, Stt, Strb, Strh: justified strings
        """
        Dna = random.randrange(111, 100000) # Nombre entier
        Dnb = (random.randrange(11, 10000)*10+random.randrange(1,10)) / 10**random.randrange(1,3) # Nombre décimal non entier
        if Dna<Dnb: Dna, Dnb = Dnb, Dna
        la = self.splitDecimal(Dna)
        lb = self.splitDecimal(Dnb)
        lt = self.splitDecimal(Dna - Dnb)
        "Justifie les nombres sous forme de texte pour que les virgules soient alignées"
        alignement = '{:>' + str(len(la[0])) + '}.{:0>' +str(max(len(la[1]), len(lb[1]))) + '}'
        Dta = alignement.format(la[0], la[1])
        Dtb = alignement.format(lb[0], lb[1])
        Dtt = alignement.format(lt[0], lt[1])
        Dtrh, Dtrb = self.retenues_diff(Dta, Dtb)
        return Dna, Dta, Dnb, Dtb, Dtrh, Dtrb, Dtt

    def valeurs_prod(self):
        Pna = random.randrange(10, 1000)*10+random.randrange(1,10)
        Pnb = random.randrange(10, 100)*10+random.randrange(1,10)
        Pnt = format(Pna * Pnb, ".14g")
        alignement = '{:>' + str(len(Pnt)) + '}'
        Ppa = random.randrange(-3,0) # Position de la virgule
        Ppb = random.randrange(-3,0)
        if random.randrange(2):
            return Pna, Pnb, Ppa, Ppb, alignement
        else:
            return Pnb, Pna, Ppb, Ppa, alignement

    def spaceToZeros(self, t):
        "Convertit un caracatère en entier, renvoie 0 si ce n'est pas un chiffre"
        try:
            return int(t)
        except ValueError:
            return 0

    def retenues_somme(self, ta, tb):
        tr=' ' # liste des retenues
        ra, rb=ta[::-1], tb[::-1] # retourne le nombre : '123.45' -> '54.321'
        for i in range(len(ta)-1):
            tr+=str((self.spaceToZeros(tr[i]) + self.spaceToZeros(ra[i]) + self.spaceToZeros(rb[i]))//10).replace('0', ' ')
        return tr[::-1]

    def retenues_diff(self, ta, tb):
        trh='' # liste des retenues hautes
        trb=' ' # liste des retenues basses
        ra, rb=ta[::-1], tb[::-1] # retourne le nombre : '123.45' -> '54.321'
        for i in range(len(ta)-1):
            if self.spaceToZeros(ra[i])<self.spaceToZeros(rb[i])+self.spaceToZeros(trb[i]):
                trh+='1'
                trb+='1'
            else:
                trh+=' '
                trb+=' '
        trh+=' '
        return trh[::-1], trb[::-1]



#===============================================================================
# Calcul mental
#===============================================================================


def tex_calcul_mental(exo, cor):
    modules = (plus, moins, plus, div)
    calculs = [i for i in range(20)]
    for i in range(20):
        j = random.randrange(0, len(calculs))
        (a, b) = modules[calculs[j] // 5](10)
        if calculs[j] // 5 == 0:
            choix_trou(a, b, a + b, '+', exo, cor)
        if calculs[j] // 5 == 1:
            choix_trou(a, b, a - b, '-', exo, cor)
        if calculs[j] // 5 == 2:
            choix_trou(a, b, a * b, '\\times', exo, cor)
        if calculs[j] // 5 == 3:
            choix_trou(a, b, a // b, '\\div', exo, cor)
        calculs.pop(j)


def choix_trou(nb1, nb2, tot, operateur, exo, cor):
    nbaleatoire = random.randrange(4)
    if nbaleatoire > 1:
        exo.append('\\item $%s %s %s = \\ldots\\ldots$' % (nb1,
                 operateur, nb2))
        cor.append('\\item $%s %s %s = \\mathbf{%s}$' % (nb1,
                 operateur, nb2, tot))
    elif nbaleatoire > 0:
        exo.append('\\item $%s %s \\ldots\\ldots = %s$' % (nb1,
                 operateur, tot))
        cor.append('\\item $%s %s \\mathbf{%s} = %s$' % (nb1,
                 operateur, nb2, tot))
    else:
        exo.append('\\item $\\ldots\\ldots %s %s = %s$' % (operateur,
                 nb2, tot))
        cor.append('\\item $\\mathbf{%s} %s %s = %s$' % (nb1,
                 operateur, nb2, tot))


def plus(valeurmax):
    (a, b) = (Arithmetique.valeur_alea(1, valeurmax), Arithmetique.valeur_alea(1,
              valeurmax))
    return (a, b)


def moins(valeurmax):
    (a, b) = (Arithmetique.valeur_alea(1, valeurmax), Arithmetique.valeur_alea(1,
              valeurmax))
    return (a + b, a)


def div(valeurmax):
    (a, b) = (Arithmetique.valeur_alea(1, valeurmax), Arithmetique.valeur_alea(1,
              valeurmax))
    return (a * b, a)




def _CalculMental():
    exo = ["\\exercice", 'Effectuer sans calculatrice :', '\\begin{multicols}{4}\\noindent', '\\begin{enumerate}']
    cor = ["\\exercice*", 'Effectuer sans calculatrice :', '\\begin{multicols}{4}\\noindent', '\\begin{enumerate}']

    tex_calcul_mental(exo, cor)

    exo.append('\\end{enumerate}')
    exo.append('\\end{multicols}')
    cor.append('\\end{enumerate}')
    cor.append('\\end{multicols}')
    return (exo, cor)

class CalculMental(LegacyExercise):
    """Calcul mental"""

    tags = ["Sixième"]
    function = _CalculMental


#===============================================================================
# PRODUITS ET QUOTIENTS PAR 10, 100, 1000
#===============================================================================


def tex_dix(exo, cor):
    nb = 4  # nb de calculs de chaque type
    l = valeurs10(nb)
    for dummy in range(len(l)):
        j = random.randrange(0, len(l))
        tex_formule_dix(l.pop(j), exo, cor)


def tex_formule_dix(l, exo, cor):
    if l[2] == '*':
        alea = random.randrange(0, 5)
        if alea > 1:
            exo.append('\\item $%s \\quad\\times\\quad %s \\quad = \\quad \\dotfill$' %
                       (Affichage.decimaux(l[0], 1), Affichage.decimaux(l[1], 1)))
            cor.append('\\item $%s \\times %s = \\mathbf{%s}$' %
                       (Affichage.decimaux(l[0], 1), Affichage.decimaux(l[1], 1), Affichage.decimaux(l[0] * l[1], 1)))
        elif alea > 0:
            exo.append('\\item $%s \\quad\\times\\quad \\dotfill \\quad = \\quad %s$' %
                       (Affichage.decimaux(l[0], 1), Affichage.decimaux(l[0] * l[1], 1)))
            cor.append('\\item $%s \\times \\mathbf{%s} = %s$' %
                       (Affichage.decimaux(l[0], 1), Affichage.decimaux(l[1], 1), Affichage.decimaux(l[0] * l[1], 1)))
        else:
            exo.append('\\item $\\dotfill \\quad\\times\\quad %s \\quad = \\quad %s$' %
                       (Affichage.decimaux(l[1], 1), Affichage.decimaux(l[0] * l[1], 1)))
            cor.append('\\item $\\mathbf{%s} \\times %s = %s$' %
                       (Affichage.decimaux(l[0], 1), Affichage.decimaux(l[1], 1), Affichage.decimaux(l[0] * l[1], 1)))
    else:
        alea = random.randrange(0, 5)
        if alea > 1:
            exo.append('\\item $%s \\quad\\div\\quad %s \\quad = \\quad \\dotfill$' %
                       (Affichage.decimaux(l[0], 1), Affichage.decimaux(l[1], 1)))
            cor.append('\\item $%s \\div %s = \\mathbf{%s}$' % (Affichage.decimaux(l[0],1), Affichage.decimaux(l[1], 1),
                                                                Affichage.decimaux(l[0] / l[1], 1)))
        elif alea > 0:
            exo.append('\\item $%s \\quad\\div\\quad \\dotfill \\quad = \\quad %s$' %
                       (Affichage.decimaux(l[0], 1), Affichage.decimaux(l[0] / l[1], 1)))
            cor.append('\\item $%s \\div \\mathbf{%s} = %s$' % (Affichage.decimaux(l[0], 1),
                                                                Affichage.decimaux(l[1], 1),
                                                                Affichage.decimaux(l[0] / l[1], 1)))
        else:
            exo.append('\\item $\\dotfill \\quad\\div\\quad %s \\quad = \\quad %s$' %
                       (Affichage.decimaux(l[1], 1), Affichage.decimaux(l[0] / l[1], 1)))
            cor.append('\\item $\\mathbf{%s} \\div %s = %s$' % (Affichage.decimaux(l[0], 1),
                                                                Affichage.decimaux(l[1], 1),
                                                                Affichage.decimaux(l[0] / l[1], 1)))


def valeurs10(nb):  # renvoie nb valeur de chaque type : *10, /10, *0.1
    l = []
    for i in range(nb):
        if random.randrange(0, 1):
            l.append((Arithmetique.valeur_alea(111, 999) * 10 ** random.randrange(-3, 0), 10 ** (i + 1), '*'))
        else:
            l.append((10 ** (i + 1), Arithmetique.valeur_alea(111, 999) * 10 **random.randrange(-3, 0), '*'))
    for i in range(nb):
        l.append((Arithmetique.valeur_alea(111, 999) * 10 ** random.randrange(-3, 0), 10 ** (i + 1), '/'))
    for i in range(nb):
        if random.randrange(0, 1):
            l.append((Arithmetique.valeur_alea(111, 999) * 10 ** random.randrange(-3, 0), 10 ** (-i - 1), '*'))
        else:
            l.append((10 ** (-i - 1), Arithmetique.valeur_alea(111, 999) * 10 **random.randrange(-3, 0), '*'))
    return l



def _ProduitPuissanceDix():
    exo = ["\\exercice", u'Compléter sans calculatrice :', '\\begin{multicols}{2}\\noindent', '\\begin{enumerate}']
    cor = ["\\exercice*", u'Compléter sans calculatrice :', '\\begin{multicols}{2}\\noindent', '\\begin{enumerate}']

    tex_dix(exo, cor)

    exo.append('\\end{enumerate}')
    exo.append('\\end{multicols}')
    cor.append('\\end{enumerate}')
    cor.append('\\end{multicols}')
    return (exo, cor)

class ProduitPuissanceDix(LegacyExercise):
    """Produits, quotients par 10, 100, 1000"""

    tags = ["Sixième"]
    function = _ProduitPuissanceDix
