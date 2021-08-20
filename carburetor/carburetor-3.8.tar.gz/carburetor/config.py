#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi<dani.behzi@ubuntu.com>, 2020-2021.


"""
main configurations for carburetor
"""

import gettext
import locale
import os

import gi
gi.require_versions({'Notify': '0.7', 'Handy': '1'})
from gi.repository import Gio, GLib, Notify, Handy

dconf = Gio.Settings.new("org.tractor")
s_data_dir = os.path.dirname(os.path.abspath(__file__))
locale_dir = s_data_dir+"/locales"
locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain('messages', locale_dir)
gettext.bindtextdomain('messages', locale_dir)
gettext.textdomain('messages')
_ = gettext.gettext
COMMAND = "tractor "
app_name = _("Carburetor")

GLib.set_application_name(app_name)
Notify.init(app_name)
Handy.init()
