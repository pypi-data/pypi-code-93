import os
import sys

from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore

import xappt
from xappt import BaseTool

from xappt_qt.gui.utilities import center_widget
from xappt_qt.gui.utilities.dark_palette import apply_palette

from xappt_qt.gui.dialogs import RunDialog

from xappt_qt.constants import *

# noinspection PyUnresolvedReferences
from xappt_qt.gui.resources import icons

os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME


@xappt.register_plugin
class QtInterface(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication.instance()
        self.runner = RunDialog()
        self.__runner_close_event = self.runner.closeEvent
        self.runner.closeEvent = self.close_event
        self.runner.btnOk.clicked.connect(self._on_run)
        self.runner.btnClose.clicked.connect(self.close)
        self.progress_dialog = None
        self.headless = False
        self.on_write_stdout.add(self.write_console_stdout)
        self.on_write_stderr.add(self.write_console_stderr)

    @classmethod
    def name(cls) -> str:
        return APP_INTERFACE_NAME

    def load_window_geo(self):
        assert self.runner.tool_plugin is not None
        tool_key = f"{self.runner.tool_plugin.collection()}::{self.runner.tool_plugin.name()}"
        geo = self.data(f"{tool_key}.geo")
        if geo is not None:
            self.runner.setGeometry(0, 0, *geo)
        pos = self.data(f"{tool_key}.pos")
        if pos is not None:
            self.runner.move(*pos)

    def save_window_geo(self):
        assert self.runner.tool_plugin is not None
        tool_key = f"{self.runner.tool_plugin.collection()}::{self.runner.tool_plugin.name()}"
        self.set_data(f"{tool_key}.geo", (self.runner.width(), self.runner.height()))
        self.set_data(f"{tool_key}.pos", (self.runner.geometry().x(), self.runner.geometry().y()))

    def invoke(self, plugin: BaseTool, **kwargs):
        self.headless = kwargs.get('headless')
        if self.headless:
            center_widget(self.runner)
            result = plugin.execute()
            if self.app.property(APP_PROPERTY_LAUNCHER):
                self.app.quit()
                sys.exit(result)
            return
        self.runner.clear()
        self.runner.set_current_tool(plugin)
        self.runner.show()
        self.load_window_geo()
        for parameter in self.runner.tool_plugin.parameters():
            self.runner.tool_widget.widget_value_updated(param=parameter)
        if kwargs.get('auto_run', False):
            self.runner.tool_plugin.execute()

    def message(self, message: str):
        xappt.log.info(message)
        QtWidgets.QMessageBox.information(self.runner, APP_TITLE, message)

    def warning(self, message: str):
        xappt.log.warning(message)
        QtWidgets.QMessageBox.warning(self.runner, APP_TITLE, message)

    def error(self, message: str, *, details: Optional[str] = None):
        xappt.log.error(message, )
        QtWidgets.QMessageBox.critical(self.runner, APP_TITLE, message)
        if details is not None and len(details):
            self.write_console_err(f"\n{details}\n")
            if not self.is_console_visible():
                self.show_console()

    def ask(self, message: str) -> bool:
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ask_result = QtWidgets.QMessageBox.question(self.runner, APP_TITLE, message, buttons=buttons,
                                                    defaultButton=QtWidgets.QMessageBox.No)
        return ask_result == QtWidgets.QMessageBox.Yes

    def progress_start(self):
        if self.headless:
            if self.progress_dialog is None:
                self.progress_dialog = QtWidgets.QProgressDialog(self.runner)
            self.progress_dialog.setRange(0, 100)
            self.progress_dialog.setLabelText("")
            self.progress_dialog.setCancelButton(None)
            self.progress_dialog.show()
        else:
            self.runner.progressBar.setRange(0, 100)
            self.runner.progressBar.setFormat("")
        self.app.processEvents()

    def progress_update(self, message: str, percent_complete: float):
        progress_value = int(100.0 * percent_complete)
        if self.headless:
            self.progress_dialog.setValue(progress_value)
            self.progress_dialog.setLabelText(message)
        else:
            self.runner.progressBar.setValue(progress_value)
            self.runner.progressBar.setFormat(message)
        self.app.processEvents()

    def progress_end(self):
        if self.headless:
            self.progress_dialog.setValue(0)
            self.progress_dialog.setLabelText("")
            self.progress_dialog.close()
        else:
            self.runner.progressBar.setValue(0)
            self.runner.progressBar.setFormat("")
        self.app.processEvents()

    def write_console_stdout(self, text: str):
        self.show_console()
        for line in text.splitlines():
            self.runner.add_output_line(line, error=False)

    def write_console_stderr(self, text: str):
        self.show_console()
        for line in text.splitlines():
            self.runner.add_output_line(line, error=True)

    def _on_run(self):
        try:
            self.runner.tool_plugin.validate()
        except xappt.ParameterValidationError as e:
            self.message(str(e))
            return

        self.enable_ui(False)
        self.runner.tool_plugin.execute(interface=self)
        try:
            self.enable_ui(True)
        except AttributeError:
            # this can happen if the tool asks the interface to close during execute
            pass

    def enable_ui(self, enabled: bool):
        self.runner.btnOk.setEnabled(enabled)
        self.runner.tool_widget.setEnabled(enabled)

    def close(self):
        if self.command_runner.running:
            self.command_runner.abort()
            self.warning("Process has been terminated.")
            return
        self.runner.close()

    def clear_console(self):
        self.runner.clear_console()

    def show_console(self):
        self.runner.show_console()

    def hide_console(self):
        self.runner.hide_console()

    def is_console_visible(self) -> bool:
        return self.runner.is_console_visible()

    def close_event(self, event: QtGui.QCloseEvent):
        tool_plugin = self.runner.tool_plugin
        if tool_plugin is not None:
            if hasattr(tool_plugin, "can_close"):
                if not tool_plugin.can_close():
                    return event.ignore()
        self.save_window_geo()
        return self.__runner_close_event(event)
