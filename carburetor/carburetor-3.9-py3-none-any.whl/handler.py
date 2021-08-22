#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi<dani.behzi@ubuntu.com>, 2020-2021.

"""
handlers for ui events
"""

from subprocess import PIPE, Popen

from gi.repository import Gio, Gtk

from . import actions
from . import config
from . import functions


class Handler:
    '''
    main handler class
    '''
    def on_MainPage_realize(self, page):
        functions.set_run_status(None)

    def on_SetProxyItem_realize(self, item):
        functions.set_checkbox()

    def on_ActionExitNode_realize(self, combo):
        _ = config._
        nodes = {
            _("Austria"): "au",
            _("Bulgaria"): "bg",
            _("Canada"): "ca",
            _("Czech"): "cz",
            _("Finland"): "fi",
            _("France"): "fr",
            _("Germany"): "de",
            _("Ireland"): "ie",
            _("Moldova"): "md",
            _("Netherlands"): "nl",
            _("Norway"): "no",
            _("Poland"): "pl",
            _("Romania"): "ro",
            _("Russia"): "su",
            _("Seychelles"): "sc",
            _("Singapore"): "sg",
            _("Spain"): "es",
            _("Sweden"): "se",
            _("Switzerland"): "ch",
            _("Ukraine"): "ua",
            _("United Kingdom"): "uk",
            _("United States"): "us"}
        combo.append("ww", _("Auto (Best)"))
        for node in sorted(nodes.keys()):
            combo.append(nodes[node], node)
        config.dconf.bind(
            "exit-node", combo, "active-id",
            Gio.SettingsBindFlags.DEFAULT)

    def on_ActionAcceptConnection_realize(self, switch):
        config.dconf.bind(
            "accept-connection", switch, "active",
            Gio.SettingsBindFlags.DEFAULT)

    def on_ActionSocksPort_realize(self, spin):
        port = config.dconf.get_int("socks-port")
        adjustment = Gtk.Adjustment(
            value=port, lower=1, upper=65535,
            step_increment=1, page_increment=1, page_size=0)
        spin.set_adjustment(adjustment)
        spin.set_text(str(port))
        config.dconf.bind(
            "socks-port", spin, "value",
            Gio.SettingsBindFlags.DEFAULT)

    def on_ActionDNSPort_realize(self, spin):
        port = config.dconf.get_int("dns-port")
        adjustment = Gtk.Adjustment(
            value=port, lower=1, upper=65535,
            step_increment=1, page_increment=1, page_size=0)
        spin.set_adjustment(adjustment)
        spin.set_text(str(port))
        config.dconf.bind(
            "dns-port", spin, "value",
            Gio.SettingsBindFlags.DEFAULT)

    def on_ActionHTTPPort_realize(self, spin):
        port = config.dconf.get_int("http-port")
        adjustment = Gtk.Adjustment(
            value=port, lower=1, upper=65535,
            step_increment=1, page_increment=1, page_size=0)
        spin.set_adjustment(adjustment)
        spin.set_text(str(port))
        config.dconf.bind(
            "http-port", spin, "value",
            Gio.SettingsBindFlags.DEFAULT)

    def on_ActionBridgeType_realize(self, switch):
        config.dconf.bind(
            "use-bridges", switch, "active",
            Gio.SettingsBindFlags.DEFAULT)

    def on_TextO4Bridge_realize(self, view):
        buff = view.get_buffer()
        get_bridges = Popen(
            config.COMMAND + "bridgesfile", stdout=PIPE,
            shell=True)
        bridges = get_bridges.stdout.read()
        bridges_file = bridges.decode("utf-8").strip('\n')
        with open(bridges_file) as file:
            text = file.read()
            buff.set_text(str(text))

    def on_ButtonO4Bridge_clicked(self, button):  # TODO: Move this to actions
        actions.on_save(button, None, self)

    def on_ActionBridgePlugin_realize(self, chooser):
        dconf = config.dconf

        def on_file_set(chooser):
            filename = chooser.get_filename()
            dconf.set_string("obfs4-path", filename)

        current_file = Gio.File.new_for_path(dconf.get_string("obfs4-path"))
        chooser.set_file(current_file)
        chooser.connect("file-set", on_file_set)

    def on_AboutDialog_realize(self, dialog):
        dialog.set_translator_credits(config._("translator-credits"))

    def on_AboutDialog_destroy(self, dialog):
        dialog.hide()
