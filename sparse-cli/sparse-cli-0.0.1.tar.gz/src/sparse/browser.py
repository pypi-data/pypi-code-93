"""Utility function for opening a webbrowser."""

import click
import webbrowser

from . import config

def open(url):
    result = do_open(url)
    if result:
        msg = 'Opened {0}'.format(url)
        click.secho(msg, fg='green')
    else:
        msg = 'Failed to open {0}'.format(url)
        click.secho(msg, fg='red')
    return result

def do_open(url):
    if config.is_testing() and not config.should_open_browser():
        return True
    return webbrowser.open_new_tab(url)
