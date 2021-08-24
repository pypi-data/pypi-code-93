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

"""Gestion du fichier de configuration de Pyromaths"""

import codecs
import os

from lxml import etree

from pyromaths.directories import HOME, CONFIGDIR
from .version import VERSION

def create_config_file():
    """Crée le fichier de configuration au format xml"""
    root = etree.Element("pyromaths")

    child = etree.SubElement(root, "options")
    etree.SubElement(child, "nom_fichier").text = _("exercices")
    etree.SubElement(child, "chemin_fichier").text = "%s" % HOME
    etree.SubElement(child, "titre_fiche").text = _(u"Fiche de révisions")
    etree.SubElement(child, "corrige").text = "True"
    etree.SubElement(child, "pdf").text = "True"
    etree.SubElement(child, "unpdf").text = "False"
    etree.SubElement(child, "modele").text = "pyromaths.tex"

    child = etree.SubElement(root, "informations")
    etree.SubElement(child, "version").text = VERSION
    etree.SubElement(child, "description").text = _(u"Pyromaths est un programme qui permet de générer des fiches d’exercices de mathématiques de collège ainsi que leur corrigé. Il crée des fichiers au format pdf qui peuvent ensuite être imprimés ou lus sur écran.")
    etree.SubElement(child, "icone").text = "pyromaths.ico"

    subchild = etree.SubElement(child, "auteur")
    etree.SubElement(subchild, "nom").text = u"Jérôme Ortais"
    etree.SubElement(subchild, "email").text = u"jerome.ortais@pyromaths.org"
    etree.SubElement(subchild, "site").text = "http://www.pyromaths.org"

    return etree.tostring(root, encoding="unicode", pretty_print=True)

def indent(elem, level=0):
    """Indente correctement les fichiers xml.
    By Filip Salomonsson; published on February 06, 2007.
    http://infix.se/2007/02/06/gentlemen-indent-your-xml"""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    return elem

def modify_config_file(fichier):
    """Modifie le fichier de configuration si besoin, excepté les options utilisateur déjà configurées"""
    modifie = False
    oldtree = etree.parse(fichier)
    oldroot = oldtree.getroot()
    newroot = etree.XML(create_config_file())
    for element in newroot.iter(tag=etree.Element):
        if not len(element):
            parents = [element]
            e = element.getparent()
            while e is not None:
                parents.insert(0, e)
                e = e.getparent()
            oldtag = oldroot
            for i in range(1, len(parents)):
                if oldtag.find(parents[i].tag) is None and i < len(parents) - 1 :
                    if i > 1:
                        etree.SubElement(oldroot.find(parents[i - 1].tag), parents[i].tag)
                    else:
                        etree.SubElement(oldroot, parents[i].tag)
                    oldtag = oldtag.find(parents[i].tag)
                else:
                    oldtag = oldtag.find(parents[i].tag)
                if i == len(parents) - 2: oldparent = oldtag
            if oldtag is None:
                # Ajoute un nouvel item dans le fichier xml
                modifie = True
                etree.SubElement(oldparent, element.tag).text = element.text
            elif oldtag.text != element.text and parents[1].tag != "options":
                # Modifie un item existant s'il ne s'agit pas des options
                modifie = True
                oldtag.text = element.text
    if modifie:
        f = codecs.open(os.path.join(CONFIGDIR, "pyromaths.xml"), encoding='utf-8', mode='w')
        f.write(etree.tostring(indent(oldroot), pretty_print=True, encoding=str))
        f.close()

