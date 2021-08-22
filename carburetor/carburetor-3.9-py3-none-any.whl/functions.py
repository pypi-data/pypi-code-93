#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi<dani.behzi@ubuntu.com>, 2020-2021.

"""
ui actions
"""

import re
from distutils.util import strtobool
from subprocess import PIPE, Popen

import gi
gi.require_versions({'Notify': '0.7'})
from gi.repository import Gio, GLib, Notify

from . import config
from . import ui


def is_running():
    '''
    check if tractor is running or not
    '''
    check = Popen(config.COMMAND + 'isrunning', stdout=PIPE, shell=True)
    output = strtobool(check.stdout.read().decode('utf-8').strip('\n'))
    return output


def set_progress(stdout, condition):
    '''
    set progress output on page desription
    '''
    try:
        line = stdout.readline().decode('utf-8')
        page = ui.get('MainPage')
        valid = re.compile(r'.*\[notice\] ')
        if 'notice' in line:
            notice = valid.sub('', line)[:-5]
            page.set_description(notice)
    except ValueError:
        pass
    return True


def thread_finished(stdout, condition, button, app):
    '''
    things to do after process finished
    '''
    GLib.source_remove(app.io_id)
    stdout.close()
    set_run_status(app)
    button.set_sensitive(True)
    notify(app)
    return False


def notify(app):
    '''
    show notification
    '''
    notif = Notify.Notification.new(config.app_name, app.notification)
    notif.set_timeout(Notify.EXPIRES_DEFAULT)
    notif.show()


def set_to_stopped(app):
    '''
    set status to stopped
    '''
    page = ui.get('MainPage')
    page.set_icon_name('process-stop-symbolic')
    page.set_title(config._("Stopped"))
    page.set_description("")
    button = ui.get('ConnectButton')
    text_start = config._("_Connect")
    style = button.get_style_context()
    style.remove_class('red')
    style.add_class('green')
    button.set_label(text_start)
    button = ui.get('ActionMenuButton')
    button.set_sensitive(False)
    button = ui.get('CancelButton')
    button.set_visible(False)
    dconf = config.dconf
    dconf.reset('pid')
    if app:
        app.notification = config._("Tractor is stopped")


def set_to_running(app):
    '''
    set status to connected
    '''
    page = ui.get('MainPage')
    page.set_icon_name('security-high')
    page.set_title(config._("Running"))
    page.set_description("")
    button = ui.get('ConnectButton')
    text_stop = config._("_Disconnect")
    style = button.get_style_context()
    style.remove_class('green')
    style.add_class('red')
    button.set_label(text_stop)
    button = ui.get('ActionMenuButton')
    button.set_sensitive(True)
    button = ui.get('CancelButton')
    button.set_visible(False)
    if app:
        app.notification = config._("Tractor is running")


def set_run_status(app):
    '''
    set status of conection
    '''
    if is_running():
        set_to_running(app)
    else:
        set_to_stopped(app)


def hide_window(window, data):
    '''
    hide the window
    '''
    window.hide()
    return True


def is_proxy_set():
    '''
    checks if proxy was already set
    '''
    proxy = Gio.Settings.new('org.gnome.system.proxy')
    socks = Gio.Settings.new('org.gnome.system.proxy.socks')
    if config.dconf.get_boolean('accept-connection'):
        myip = '0.0.0.0'
    else:
        myip = '127.0.0.1'
    proxy_mode = proxy.get_string('mode')
    current_port = socks.get_int('port')
    tractor_port = config.dconf.get_int('socks-port')
    current_ip = socks.get_string('host')
    if (proxy_mode == 'manual' and
            current_port == tractor_port and
            current_ip == myip):
        return True
    return False


def set_checkbox():
    '''
    set status of proxy checkbox
    '''
    checkbox = ui.get('SetProxyItem')
    if is_proxy_set():
        checkbox.props.active = True
    checkbox.props.active = False
