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

import gettext
from sys import argv, exit
import sys
from os import access, R_OK, makedirs
from os.path import join, isdir, dirname, realpath, split
from codecs import open

from pyromaths.directories import CONFIGDIR, LOCALEDIR

def main():
#===============================================================================
# Imports spécifiques à Pyromaths
#===============================================================================

    gettext.install('pyromaths', localedir=LOCALEDIR)


    from .config import create_config_file, modify_config_file
    from .testenv import testenvironment

    from . import Ui_MainWindow
    from PyQt5 import QtGui, QtWidgets
    class StartQT5(QtWidgets.QMainWindow, Ui_MainWindow):
        def __init__(self, parent=None):
            QtWidgets.QWidget.__init__(self, parent)
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

    #===========================================================================
    # Création du fichier de configuration si inexistant
    #===========================================================================
    if not access(join(CONFIGDIR, "pyromaths.xml"), R_OK):
        if not isdir(CONFIGDIR): makedirs(CONFIGDIR)
        f = open(join(CONFIGDIR, "pyromaths.xml"), encoding='utf-8', mode='w')
        f.write(create_config_file())
        f.close()
    modify_config_file(join(CONFIGDIR, "pyromaths.xml"))
    templatesdir = join(CONFIGDIR, "templates")
    if not isdir(templatesdir): makedirs(templatesdir)
    packagesdir = join(CONFIGDIR, "packages")
    if not isdir(packagesdir): makedirs(packagesdir)

    app = QtWidgets.QApplication(argv)
    pyromaths = StartQT5()

    # Intégration de QTranslator
    from PyQt5.QtCore import QTranslator
    translator = QTranslator()
    translator.load("qtbase_fr", "data")
    app.installTranslator(translator)

    pyromaths.show()
    testenvironment(pyromaths)

    exit(app.exec_())

if __name__ == "__main__":
    main()
