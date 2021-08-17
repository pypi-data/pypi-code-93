import os
import json
import traceback
import gi
from pypulseprofilestray.config import THEMES, config_file, load_config
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3
from pypulseprofiles import pulse_apply, pulse_create, pulse_delete, list_configs

CURRPATH = os.path.dirname(os.path.realpath(__file__))
""" for locating the icon for the indicator. """

indicator = None
""" the tray icon indicator instance. """

""" the name of the application. """


class ConfirmationDialog(Gtk.Dialog):
    """
    Simple confirmation dialog. Based on code from here:
    https://python-gtk-3-tutorial.readthedocs.io/en/latest/dialogs.html#messagedialog
    """

    def __init__(self, parent, msg):
        Gtk.Dialog.__init__(
            self,
            "Confirmation",
            parent,
            0,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK,
                Gtk.ResponseType.OK,
            ),
        )

        self.set_default_size(150, 100)
        label = Gtk.Label(label=msg)
        box = self.get_content_area()
        box.add(label)
        self.show_all()


class InputDialog(Gtk.Dialog):
    """
    Simple input dialog. Based on code from here:
    https://python-gtk-3-tutorial.readthedocs.io/en/latest/dialogs.html#messagedialog
    """

    def __init__(self, parent, msg):
        Gtk.Dialog.__init__(
            self,
            "Input",
            parent,
            0,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK,
                Gtk.ResponseType.OK,
            ),
        )

        self.set_default_size(150, 100)
        label = Gtk.Label(label=msg)
        box = self.get_content_area()
        box.add(label)
        self.entry = Gtk.Entry()
        box.add(self.entry)
        self.show_all()


def current_theme():
    """
    Returns the currently configured theme.

    :return: the current theme
    :rtype: str
    """
    result = "Dark"
    config = load_config()
    if ("theme" in config) and (config["theme"] in THEMES):
        result = config["theme"]
    return result


def store_theme(theme):
    """
    Stores the theme as the default one.

    :param theme: the theme to use
    :type theme: str
    """
    print("Applying theme: %s" % theme)
    config = load_config()
    config["theme"] = theme
    with open(config_file(), "w") as cf:
        json.dump(config, cf, indent=2)


def main():
    """
    The main method for starting up the tray icon
    """

    global indicator
    indicator = AppIndicator3.Indicator.new(
        "customtray",
        CURRPATH + "/" + THEMES[current_theme()],
        AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    indicator.set_menu(menu())
    Gtk.main()


def menu():
    """
    Generates the menu and returns it.

    :return: the menu
    :rtype: Gtk.Menu
    """

    result = Gtk.Menu()

    profiles = list_configs()

    # create
    menuitem_create = Gtk.MenuItem(label='Create...')
    menuitem_create.connect('activate', create_profile)
    result.append(menuitem_create)

    # apply
    if len(profiles) > 0:
        menu_apply = Gtk.Menu()
        menuitem_apply = Gtk.MenuItem(label='Apply')
        menuitem_apply.set_submenu(menu_apply)
        result.append(menuitem_apply)
        for profile in profiles:
            menuitem = Gtk.MenuItem(label=profile)
            menuitem.connect('activate', apply_profile)
            menu_apply.append(menuitem)
    else:
        menuitem_apply = Gtk.MenuItem(label='Apply')
        menuitem_apply.set_sensitive(False)
        result.append(menuitem_apply)

    # delete
    if len(profiles) > 0:
        menu_delete = Gtk.Menu()
        menuitem_delete = Gtk.MenuItem(label='Delete')
        menuitem_delete.set_submenu(menu_delete)
        result.append(menuitem_delete)
        for profile in profiles:
            menuitem = Gtk.MenuItem(label=profile)
            menuitem.connect('activate', delete_profile)
            menu_delete.append(menuitem)
    else:
        menuitem_delete = Gtk.MenuItem(label='Delete')
        menuitem_delete.set_sensitive(False)
        result.append(menuitem_delete)

    result.append(Gtk.SeparatorMenuItem())

    # refresh
    menuitem_refresh = Gtk.MenuItem(label='Refresh')
    menuitem_refresh.connect('activate', refresh_profiles)
    result.append(menuitem_refresh)

    result.append(Gtk.SeparatorMenuItem())

    # themes
    menu_theme = Gtk.Menu()
    menuitem_theme = Gtk.MenuItem(label='Theme')
    menuitem_theme.set_submenu(menu_theme)
    result.append(menuitem_theme)
    for k in THEMES:
        menuitem = Gtk.MenuItem(label=k)
        menuitem.connect('activate', select_theme)
        menu_theme.append(menuitem)

    result.append(Gtk.SeparatorMenuItem())

    # exit
    menuitem_exit = Gtk.MenuItem(label='Exit')
    menuitem_exit.connect('activate', exit_tray)
    result.append(menuitem_exit)

    result.show_all()
    return result


def update_menu():
    """
    Updates the menu.
    """

    global indicator
    indicator.set_menu(menu())


def create_profile(_):
    """
    Creates a new profile, using the current settings, prompting the user for a name.
    """

    dialog = InputDialog(None, "Please enter profile name:")
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        profile = dialog.entry.get_text()
        print("Creating profile: %s" % profile)
        pulse_create(profile)
        update_menu()

    dialog.destroy()


def apply_profile(e):
    """
    Applies the profile with the name stored in the label.

    :param e: the menu item that triggered the event
    :type e: Gtk.MenuItem
    """

    profile = e.get_label()
    print("Applying profile: %s" % profile)
    pulse_apply(profile)


def delete_profile(e):
    """
    Deletes the profile with the name stored in the label.

    :param e: the menu item that triggered the event
    :type e: Gtk.MenuItem
    """

    profile = e.get_label()

    dialog = ConfirmationDialog(None, "Do you want to delete profile '%s'?" % profile)
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        print("Deleting profile: %s" % profile)
        pulse_delete(profile)
        update_menu()

    dialog.destroy()


def refresh_profiles(_):
    """
    Re-creates the menu.
    """

    print("Refreshing profiles")
    update_menu()


def select_theme(e):
    """
    Applies the theme with the name stored in the label.

    :param e: the menu item that triggered the event
    :type e: Gtk.MenuItem
    """
    global indicator
    theme = e.get_label()
    store_theme(theme)
    icon = THEMES[theme]
    indicator.set_icon(CURRPATH + "/" + icon)


def exit_tray(_):
    """
    Exits the tray icon menu.
    """

    Gtk.main_quit()


def sys_main():
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    :rtype: int
    """

    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
