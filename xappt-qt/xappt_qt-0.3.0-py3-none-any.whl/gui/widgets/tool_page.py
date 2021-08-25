from typing import Any, Callable, Dict, Generator, List, Optional, Type

from PyQt5 import QtWidgets, QtCore

import xappt

from xappt_qt.gui.widgets import *
from xappt_qt.gui.delegates import SimpleItemDelegate


class ToolPage(QtWidgets.QWidget):
    def __init__(self, tool: xappt.BaseTool, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self.convert_dispatch: Dict[Type, Callable] = {
            int: self._convert_int,
            bool: self._convert_bool,
            float: self._convert_float,
            str: self._convert_str,
            list: self._convert_list,
        }

        self.tool = tool
        self.build_ui()

    # noinspection PyAttributeOutsideInit
    def build_ui(self):
        self.grid = QtWidgets.QGridLayout()
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(0, 0)
        self.grid.setHorizontalSpacing(16)
        self.grid.setVerticalSpacing(8)

        self.setLayout(self.grid)
        self._load_tool_parameters()

    @staticmethod
    def get_caption(param: xappt.Parameter) -> str:
        caption_default = param.name.replace("_", " ").title()
        caption = param.options.get("caption", caption_default)
        return caption

    def update_tool_choices(self, param: xappt.Parameter):
        """ Given that multiple parameter types can be updated at runtime,
        it's easier just to remove and recreate the widget rather than
        reimplementing a lot of the same functionality to update existing
        widgets. """
        widget = param.metadata.get('widget')
        if widget is None:
            return

        # find and remove existing widget
        index = self.grid.indexOf(widget)
        row, column, *_ = self.grid.getItemPosition(index)
        self.grid.takeAt(index)
        widget.deleteLater()
        param.on_choices_changed.clear()

        # create a new widget to replace it
        new_widget = self.convert_parameter(param)
        self.grid.addWidget(new_widget, row, column)
        param.metadata['widget'] = new_widget
        param.on_choices_changed.add(self.update_tool_choices)

    def _load_tool_parameters(self):
        for i, param in enumerate(self.tool.parameters()):
            label = QtWidgets.QLabel(self.get_caption(param))
            label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            label.setToolTip(param.description)
            param.metadata['label'] = label
            self.grid.addWidget(label, i, 0)

            error = ErrorLabel()
            param.metadata['error'] = error
            self.grid.addWidget(error, i, 2)

            widget = self.convert_parameter(param)
            widget.setToolTip(param.description)
            param.metadata['widget'] = widget  # this lets us avoid lambdas
            self.grid.addWidget(widget, i, 1)

            self.widget_options_updated(param)

            param.on_choices_changed.add(self.update_tool_choices)
            param.on_value_changed.add(self.widget_value_updated)
            param.on_options_changed.add(self.widget_options_updated)

    def convert_parameter(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        convert_fn = self.convert_dispatch.get(param.data_type)
        if convert_fn is not None:
            return convert_fn(param)
        return QtWidgets.QWidget()

    def _convert_int(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.choices is not None:
            return self._convert_int_choice(param)
        else:
            return self._convert_int_spin(param)

    def _convert_int_choice(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QComboBox()
        w.addItems(param.choices)
        for v in (param.value, param.default):
            if v is not None:
                if isinstance(v, str):
                    if v in param.choices:
                        index = w.findText(v)
                        w.setCurrentIndex(index)
                elif isinstance(v, int):
                    if 0 <= v < w.count():
                        w.setCurrentIndex(v)
                break
        else:
            param.value = w.currentIndex()

        if param.options.get("searchable"):
            self.setup_combo_completer(w)

        w.currentIndexChanged[str].connect(lambda x: self.update_tool_param(param.name, x))
        param.metadata['ui-setter'] = w.setCurrentIndex
        return w

    def _convert_int_spin(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QSpinBox(parent=self)
        minimum = param.options.get("minimum", -999999999)
        maximum = param.options.get("maximum", 999999999)
        w.setMinimum(minimum)
        w.setMaximum(maximum)
        for v in (param.value, param.default):
            if v is not None:
                w.setValue(v)
                break
        else:
            param.value = w.value()
        w.valueChanged[int].connect(lambda x: self.update_tool_param(param.name, x))
        param.metadata['ui-setter'] = w.setValue
        return w

    def _convert_bool(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.options.get("ui") == "button":
            w = QtWidgets.QPushButton()
            w.setText(self.get_caption(param))
            w.clicked.connect(lambda x: self.update_tool_param(param.name, param.value))
            param.metadata['label'].setText("")
        else:
            w = QtWidgets.QCheckBox()
            for v in (param.value, param.default):
                if v is not None:
                    w.setChecked(v)
                    break
            else:
                param.value = w.isChecked()
            w.stateChanged.connect(lambda x: self.update_tool_param(param.name, x == QtCore.Qt.Checked))
            param.metadata['ui-setter'] = w.setChecked
        return w

    def _convert_str(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.choices is not None:
            return self._convert_str_choice(param)
        else:
            return self._convert_str_edit(param)

    def _convert_str_choice(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QComboBox()
        w.addItems(param.choices)
        for v in (param.value, param.default):
            if v is not None and v in param.choices:
                index = w.findText(v)
                w.setCurrentIndex(index)
                break
        else:
            param.value = w.currentText()

        if param.options.get("searchable"):
            self.setup_combo_completer(w)

        w.currentIndexChanged[str].connect(lambda x: self.update_tool_param(param.name, x))
        param.metadata['ui-setter'] = lambda s, widget=w: widget.setCurrentIndex(widget.findText(s))
        return w

    def _convert_str_edit(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        ui = param.options.get("ui")
        if ui == "folder-select":
            w = FileEdit(mode=FileEdit.MODE_CHOOSE_DIR)
            w.onSetFile.connect(lambda x: self.update_tool_param(param.name, x))
        elif ui == "file-open":
            w = FileEdit(accept=param.options.get("accept"), mode=FileEdit.MODE_OPEN_FILE)
            w.onSetFile.connect(lambda x: self.update_tool_param(param.name, x))
        elif ui == "file-save":
            w = FileEdit(accept=param.options.get("accept"), mode=FileEdit.MODE_SAVE_FILE)
            w.onSetFile.connect(lambda x: self.update_tool_param(param.name, x))
        elif ui == "multi-line":
            w = TextEdit()
            w.editingFinished.connect(lambda widget=w: self.update_tool_param(param.name, widget.text()))
        else:
            w = QtWidgets.QLineEdit()
            w.editingFinished.connect(lambda widget=w: self.update_tool_param(param.name, widget.text()))

        for v in (param.value, param.default):
            if v is not None:
                w.setText(v)
                break
        else:
            w.setText("")
        param.metadata['ui-setter'] = w.setText
        return w

    # noinspection DuplicatedCode
    def _convert_float(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QDoubleSpinBox(parent=self)
        minimum = param.options.get("minimum", -999999999.0)
        maximum = param.options.get("maximum", 999999999.0)
        w.setMinimum(minimum)
        w.setMaximum(maximum)
        if param.default is not None:
            w.setValue(param.default)
        param.value = w.value()
        w.valueChanged[float].connect(lambda x: self.update_tool_param(param.name, x))
        param.metadata['ui-setter'] = w.setValue
        return w

    def _convert_list(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = CheckList(searchable=param.options.get('searchable', False))
        if param.choices is not None:
            w.add_items(param.choices)
        for v in (param.value, param.default):
            if v is not None:
                w.check_items(v)
                break
        param.value = list(w.checked_items())
        w.item_changed.connect(lambda: self.update_list_param(param.name))
        param.metadata['ui-setter'] = lambda value, widget=w: self.set_list_value(value, widget)
        return w

    def update_list_param(self, name: str):
        param: xappt.Parameter = getattr(self.tool, name)
        error: ErrorLabel = param.metadata['error']
        widget: CheckList = param.metadata.get('widget')
        if widget is None:
            return
        checked_items = list(widget.checked_items())
        param.on_value_changed.paused = True
        try:
            param.value = param.validate(checked_items)
        except xappt.ParameterValidationError as e:
            error.set_error(str(e))
        else:
            error.reset()
        param.on_value_changed.paused = False

    def update_tool_param(self, name: str, value: Any):
        param: xappt.Parameter = getattr(self.tool, name)
        error: ErrorLabel = param.metadata['error']
        try:
            param.value = param.validate(value)
        except xappt.ParameterValidationError as e:
            error.set_error(str(e))
        else:
            error.reset()

    @staticmethod
    def set_list_value(items: List[str], widget: CheckList):
        widget.uncheck_all()
        widget.check_items(items)

    @staticmethod
    def widget_value_updated(param: xappt.Parameter):
        setter = param.metadata.get('ui-setter')
        if setter is None:
            return
        setter(param.value)

    @staticmethod
    def widget_options_updated(param: xappt.Parameter):
        label: Optional[QtWidgets.QLabel] = param.metadata.get('label')
        widget: Optional[QtWidgets.QWidget] = param.metadata.get('widget')
        error: Optional[ErrorLabel] = param.metadata.get('error')

        visible = param.option("visible", True)
        if label is not None:
            label.setVisible(visible)
        if widget is not None:
            widget.setVisible(visible)
        if error is not None:
            error.setVisible(visible)

        enabled = param.option("enabled", True)
        if widget is not None:
            widget.setEnabled(enabled)

    def disconnect(self):
        for param in self.tool.parameters():
            param.on_value_changed.clear()
            param.on_options_changed.clear()
            param.on_choices_changed.clear()

    @staticmethod
    def setup_combo_completer(combo_widget: QtWidgets.QComboBox):
        combo_widget.setEditable(True)
        combo_widget.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        combo_widget.lineEdit().editingFinished.connect(
            lambda: combo_widget.setCurrentIndex(combo_widget.findText(combo_widget.currentText())))
        completer = combo_widget.completer()
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        completer.popup().setAlternatingRowColors(True)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setFilterMode(QtCore.Qt.MatchContains)

