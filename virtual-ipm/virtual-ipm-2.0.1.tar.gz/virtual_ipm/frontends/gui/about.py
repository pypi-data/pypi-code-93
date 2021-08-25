from functools import partial
import os.path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QMenuBar, QWidget, QAction

import virtual_ipm


def add_help_menu(menubar: QMenuBar, *, widget: QWidget, parent: QWidget):
    help_menu = menubar.addMenu('Help')
    about_action = QAction(
        QIcon(os.path.join(os.path.split(__file__)[0], 'icons/about.png')),
        'About',
        widget,
    )
    about_action.triggered.connect(partial(show_about_note, parent=parent))
    help_menu.addAction(about_action)

    license_note_action = QAction('License note', widget)
    license_note_action.triggered.connect(partial(show_license_note, parent=parent))
    help_menu.addAction(license_note_action)
    return help_menu


def show_about_note(parent=None):
    QMessageBox.information(
        parent,
        'About',
        'Virtual-IPM\n{0}'.format(virtual_ipm.__version__)
    )


def show_license_note(parent=None):
    QMessageBox.information(
        parent,
        'License note',
        'Virtual-IPM is a software for simulating IPMs and other related devices.\n'
        'Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>\n'
        '\n'
        'This program is free software: you can redistribute it and/or modify\n'
        'it under the terms of the GNU Affero General Public License as\n'
        'published by the Free Software Foundation, either version 3 of the\n'
        'License, or (at your option) any later version.\n'
        '\n'
        'This program is distributed in the hope that it will be useful,\n'
        'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
        'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
        'GNU Affero General Public License for more details.\n'
        '\n'
        'You should have received a copy of the GNU Affero General Public License\n'
        'along with this program.  If not, see <http://www.gnu.org/licenses/>.'
    )
