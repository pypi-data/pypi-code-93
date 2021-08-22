import gi
import locale
import sys
import warnings

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from .Window import Window


def main():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    locale.setlocale(locale.LC_ALL, locale='en_US')

    win = Window()
    win.show_all()

    if len(sys.argv) > 1:
        win.set_tournament_by_path(sys.argv[1])
    else:
        win.set_tournament_to_new_tournament()

    Gtk.main()


if __name__ == '__main__':
    main()
