#!/usr/bin/env python

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
import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as Widgets

import virtual_ipm.log as log
from virtual_ipm.frontends.gui import MainWindow


def main():
    log.to_console(level=logging.INFO)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = Widgets.QApplication(sys.argv)

    view = MainWindow()
    view.show()

    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
