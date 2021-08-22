#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi<dani.behzi@ubuntu.com>, 2020-2021.

'''
actions for carburetor
'''

import os
import re
import signal
from subprocess import PIPE, Popen

import gi
gi.require_versions({'Notify': '0.7'})
from gi.repository import Gio, GLib, Notify

from . import config
from . import functions
from . import ui


def add(name, function, app):
    '''
    adds functions to app as actions
    '''
    action = Gio.SimpleAction.new(name, None)
    action.connect('activate', function, app)
    app.add_action(action)


def do_startup(app):
    '''
    actions to do when starting the app up
    '''
    add('preferences', on_preferences, app)
    add('about', on_about, app)
    add('quit', on_quit, app)
    add('connect', on_connect, app)
    add('new_id', on_new_id, app)
    add('set_proxy', on_set_proxy, app)
    add('cancel', on_cancel, app)
    add('save', on_save, app)


def on_preferences(action, params, app):
    '''
    show the preferences window
    '''
    if not app.prefs:
        prefs_window = ui.get('PreferencesWindow')
        prefs_window.set_transient_for(app.window)
        app.prefs = prefs_window
        app.prefs.connect('delete-event', functions.hide_window)
    app.prefs.show()


def on_about(action, param, app):
    '''
    show the about window
    '''
    if not app.about:
        about_dialog = ui.get('AboutDialog')
        about_dialog.set_transient_for(app.window)
        app.about = about_dialog
    response = app.about.run()
    if -6 < response < -3:
        app.about.hide()


def on_quit(action, param, app):
    '''
    exit the app
    '''
    app.quit()


def on_connect(action, param, app):
    '''
    clicking on connect button
    '''
    button = ui.get('ConnectButton')
    button.set_sensitive(False)
    menu_button = ui.get('ActionMenuButton')
    menu_button.set_sensitive(False)
    cancel_button = ui.get('CancelButton')
    cancel_button.set_visible(True)
    page = ui.get('MainPage')
    page.set_icon_name('image-loading-symbolic')
    if functions.is_running():
        text_stopping = config._("Disconnecting…")
        page.set_title(text_stopping)
        action = 'stop'
    else:
        text_starting = config._("Connecting…")
        page.set_title(text_starting)
        action = 'start'
    app.task = Popen(
        config.COMMAND + action,
        stdout=PIPE, shell=True,
        start_new_session=True)
    if action == 'start':
        config.dconf.set_int('pid', app.task.pid)
    app.io_id = GLib.io_add_watch(
        app.task.stdout, GLib.IO_IN,
        functions.set_progress)
    GLib.io_add_watch(
        app.task.stdout, GLib.IO_HUP,
        functions.thread_finished, button, app)


def on_new_id(action, param, app):
    '''
    clicking on new id button
    '''
    if functions.is_running():
        newid = Popen(config.COMMAND + 'newid', stdout=PIPE, shell=True)
        newid.wait()
        notif = Notify.Notification.new(
            config.app_name,
            config._("You have a new identity!"))
    else:
        notif = Notify.Notification.new(
            config.app_name,
            config._("Tractor is not running!"))
    notif.set_timeout(Notify.EXPIRES_DEFAULT)
    notif.show()


def on_set_proxy(action, param, app):
    '''
    clicking on proxy button
    '''
    checkbox = ui.get('SetProxyItem')
    if checkbox.get_active():
        action = 'set'
    else:
        action = 'unset'
    task = Popen(config.COMMAND + action, stdout=PIPE, shell=True)
    task.wait()


def on_cancel(action, param, app):
    dconf = config.dconf
    pid = dconf.get_int('pid')
    os.killpg(os.getpgid(pid), signal.SIGTERM)
    dconf.reset('pid')


def on_save(action, param, app):
    '''
    clicking on save button in bridges
    '''
    textview = ui.get('TextO4Bridge')
    buff = textview.get_buffer()
    text = buff.get_text(buff.get_start_iter(), buff.get_end_iter(), 0)
    regex = re.compile(r'^( )*([Bb][Rr][Ii][Dd][Gg][Ee])?( )*', re.MULTILINE)
    get_bridges = Popen(
        config.COMMAND + "bridgesfile",
        stdout=PIPE, shell=True)
    bridges = get_bridges.stdout.read()
    bridges_file = bridges.decode("utf-8").strip('\n')
    if text == regex.sub('Bridge ', text):
        with open(bridges_file, 'w') as file:
            file.write(text)
    else:
        dialog = ui.get('O4ErrorDialog')
        response = dialog.run()
        if -6 < response < -3:
            dialog.hide()
