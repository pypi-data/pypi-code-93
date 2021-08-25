import os
import platform
import sys


from PyQt5 import QtWidgets, QtGui, QtCore

import xappt

import xappt_qt.config
from xappt_qt.gui.ui.browser import Ui_Browser
from xappt_qt.gui.utilities import center_widget
from xappt_qt.gui.utilities.dark_palette import apply_palette
from xappt_qt.gui.utilities.tray_icon import TrayIcon
from xappt_qt.constants import *
from xappt_qt.gui.tab_pages import ToolsTabPage, OptionsTabPage, AboutTabPage

# noinspection PyUnresolvedReferences
from xappt_qt.gui.resources import icons

from xappt_qt.utilities import singleton

DISABLE_TRAY_ICON = platform.system() == "Darwin"


class XapptBrowser(xappt.ConfigMixin, QtWidgets.QMainWindow, Ui_Browser):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(":appicon"))
        self.setWindowTitle(APP_TITLE)

        self.tray_icon = TrayIcon(self, QtGui.QIcon(":appicon"))

        self.tools = ToolsTabPage(on_info=self.tray_icon.info, on_warn=self.tray_icon.warn,
                                  on_error=self.tray_icon.critical)
        self.options = OptionsTabPage()
        self.about = AboutTabPage()

        self.tabWidget.addTab(self.tools, self.tools.windowTitle())
        self.tabWidget.addTab(self.options, self.options.windowTitle())
        self.tabWidget.addTab(self.about, self.about.windowTitle())
        self.tabWidget.setCurrentIndex(0)

        self.config_path = APP_CONFIG_PATH.joinpath("browser.cfg")
        self.init_config()
        self.load_config()

        self.init_tray_icon()

    def init_config(self):
        self.add_config_item('launch-new-process',
                             saver=lambda: xappt_qt.config.launch_new_process,
                             loader=lambda x: setattr(xappt_qt.config, "launch_new_process", x),
                             default=True)
        self.add_config_item('window-size',
                             saver=lambda: (self.width(), self.height()),
                             loader=lambda x: self.setGeometry(0, 0, *x),
                             default=(350, 600))
        self.add_config_item('window-position',
                             saver=lambda: (self.geometry().x(), self.geometry().y()),
                             loader=lambda x: self.set_window_position(*x),
                             default=(-1, -1))
        self.add_config_item('start-minimized',
                             saver=lambda: xappt_qt.config.start_minimized,
                             loader=lambda x: setattr(xappt_qt.config, "start_minimized", x),
                             default=False)
        if DISABLE_TRAY_ICON:
            self.options.chkMinimizeToTray.setChecked(False)
            self.options.chkMinimizeToTray.setEnabled(False)
            xappt_qt.config.minimize_to_tray = False
        else:
            self.add_config_item('minimize-to-tray',
                                 saver=lambda: xappt_qt.config.minimize_to_tray,
                                 loader=lambda x: setattr(xappt_qt.config, "minimize_to_tray", x),
                                 default=True)

    def init_tray_icon(self):
        if DISABLE_TRAY_ICON:
            return

        for category, plugin_list in self.tools.loaded_plugins.items():
            for plugin in plugin_list:
                self.tray_icon.add_menu_item(plugin.name(), on_activate=self.run_tool, data=plugin, group=category)

        self.tray_icon.add_menu_item(None)
        self.tray_icon.add_menu_item("Show", on_activate=self.show, is_visible=self.isHidden)
        self.tray_icon.add_menu_item("Hide", on_activate=self.hide, is_visible=self.isVisible)
        self.tray_icon.add_menu_item(None)
        self.tray_icon.add_menu_item("Quit", on_activate=self.on_quit)
        self.tray_icon.on_trigger = self.on_activate
        self.tray_icon.show()

    def set_window_position(self, x: int, y: int):
        if x < 0 or y < 0:
            center_widget(self)
        else:
            self.move(x, y)

    def changeEvent(self, event: QtCore.QEvent):
        if not DISABLE_TRAY_ICON:
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.windowState() == QtCore.Qt.WindowMinimized:
                    if xappt_qt.config.minimize_to_tray and self.tray_icon.tray_available:
                        self.hide()
        super().changeEvent(event)

    def closeEvent(self, event: QtGui.QCloseEvent):
        if xappt_qt.config.minimize_to_tray and self.tray_icon.tray_available:
            event.ignore()
            self.hide()
        else:
            self.on_quit()

    def on_activate(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def on_quit(self):
        self.tray_icon.destroy()
        self.save_config()
        QtWidgets.QApplication.instance().quit()

    def run_tool(self, **kwargs):
        plugin = kwargs.get('data')
        if plugin is None:
            return
        assert issubclass(plugin, xappt.BaseTool)
        self.tools.launch_tool(plugin)


def main(args) -> int:
    try:
        _ = singleton.SingleInstance(flavor_id='browser')
    except singleton.SingleInstanceException:
        return 1

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(args)
    apply_palette(app)

    browser = XapptBrowser()
    if xappt_qt.config.start_minimized:
        if not xappt_qt.config.minimize_to_tray:
            browser.setWindowState(QtCore.Qt.WindowMinimized)
            browser.show()
    else:
        browser.show()

    app.setProperty(APP_PROPERTY_RUNNING, True)
    app.setProperty(APP_PROPERTY_LAUNCHER, False)
    return app.exec_()


def entry_point() -> int:
    os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME
    return main(sys.argv)


if __name__ == '__main__':
    sys.exit(entry_point())
