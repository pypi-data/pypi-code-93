#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi<dani.behzi@ubuntu.com>, 2019-2021.

"""
Main module for carburetor
"""

from sys import argv

import gi
gi.require_versions({'Gtk': '3.0'})
from gi.repository import Gtk

from . import actions
from . import ui


class Application(Gtk.Application):
    '''
    main window of carburetor
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, application_id='org.tractor.carburetor',
            **kwargs)
        self.window = None
        self.prefs = None
        self.about = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        actions.do_startup(self)

    def do_activate(self):
        if not self.window:
            ui.css()
            window = ui.get('MainWindow')
            self.add_window(window)
            self.window = window
        self.window.present()


def main():
    '''
    main entrance of app
    '''
    ui.initialize_builder()
    app = Application()
    app.run(argv)


if __name__ == '__main__':
    main()
