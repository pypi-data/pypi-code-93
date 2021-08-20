#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi<dani.behzi@ubuntu.com>, 2020-2021.

"""
handle ui related stuff
"""

import gi
gi.require_versions({'Gtk': '3.0'})
from gi.repository import Gdk, Gtk

from . import config
from . import handler

builder = Gtk.Builder()


def initialize_builder():
    '''
    connect builder to files and handlers
    '''
    ui_dir = config.s_data_dir+'/ui'
    builder.add_from_file(ui_dir+'/about.ui')
    builder.add_from_file(ui_dir+'/main.ui')
    builder.add_from_file(ui_dir+'/preferences.ui')
    builder.connect_signals(handler.Handler())


def get(obj):
    '''
    get object from ui
    '''
    return builder.get_object(obj)


def css():
    '''
    apply css to ui
    '''
    css_provider = Gtk.CssProvider()
    ui_dir = config.s_data_dir+'/ui'
    css_provider.load_from_path(ui_dir+'/style.css')
    screen = Gdk.Screen.get_default()
    context = Gtk.StyleContext()
    context.add_provider_for_screen(
        screen, css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_USER)
