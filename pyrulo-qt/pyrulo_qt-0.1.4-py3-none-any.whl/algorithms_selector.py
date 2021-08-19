import os
from pathlib import Path

from PySide2 import QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from typing import Dict, Tuple, List, Any

from pyrulo_qt.ui_configurable_selector import ConfigurableSelector


class AlgorithmsSelector(QtWidgets.QDialog):

    def __init__(self, algorithm_types: List[Tuple[str, Any]], parent=None):
        super(AlgorithmsSelector, self).__init__(parent=parent)

        self._algorithm_types = algorithm_types
        self._selectors: Dict[str, ConfigurableSelector] = {}

        ui_file_path = os.path.join(Path(__file__).parent, 'algorithms_selector_ui.py')
        self._widget = self.setup_widget_from_ui(ui_file_path, self)

        self._container: QtWidgets.QWidget = self._widget.container
        self._layout = self._container.layout()

        self._buttons_box: QtWidgets.QDialogButtonBox = self._widget.buttons_box
        self._buttons_box.accepted.connect(self.accept)
        self._buttons_box.rejected.connect(self.reject)

        self._populate_algorithm_selectors()

    def setup_widget_from_ui(self, ui_file_path: str, parent: QtWidgets.QWidget):
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        widget = loader.load(ui_file)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        parent.setLayout(layout)
        layout.addWidget(widget)

        return widget

    @staticmethod
    def create_dialog(algorithm_types: List[Tuple[str, Any]]):
        dialog = AlgorithmsSelector(algorithm_types)
        result = dialog.exec_()
        succeeded = result == QtWidgets.QDialog.DialogCode.Accepted

        selected = dialog.get_selected() if succeeded else None

        return succeeded, selected

    def get_selected(self):
        return {name: selector.current_object() for name, selector in self._selectors.items()}

    def _populate_algorithm_selectors(self):
        for algorithm_type_name, algorithm_key in self._algorithm_types:
            label = QtWidgets.QLabel(algorithm_type_name)
            combobox = ConfigurableSelector(dir_key=algorithm_key)
            self._layout.addRow(label, combobox)
            self._selectors[algorithm_type_name] = combobox
