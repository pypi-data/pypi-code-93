from __future__ import annotations

from collections import defaultdict, namedtuple
from dataclasses import dataclass
from functools import partial
import inspect
import math
from pathlib import Path
from typing import Any, Callable, List, Sequence, Type, Union

try:
    from PyQt5.QtWidgets import (
        QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox, QFileDialog, QDialog,
        QMessageBox, QDialogButtonBox, QScrollArea, QFrame,
    )
    from PyQt5.QtGui import QDoubleValidator, QIntValidator, QIcon, QFontMetrics
    from PyQt5.QtCore import QLocale, Qt, pyqtSignal
except ImportError:
    raise RuntimeError('Parameter sweeps only work with PyQt5')

from anna.adaptors import ConfigurationAdaptor
from anna.parameters import Parameter, IntegerParameter, NumberParameter, FilepathParameter, PhysicalQuantityParameter
from anna.sweeps import (
    FilepathRange, NumberRange, CombinationMethod, ProductCombination, ZipCombination, Generator, Distribution,
    Combinator, VectorRange, Sweep, IntegerRange, Linear, Log10,
)
from .widgets import Folder


class ParameterRangeForm(QWidget):
    PEER: Type[Parameter] = Parameter

    content_changed = pyqtSignal()
    count_changed = pyqtSignal()

    @property
    def count(self) -> int:
        raise NotImplementedError

    @property
    def why_incomplete_hint(self) -> Union[str, None]:
        raise NotImplementedError

    @property
    def is_complete(self) -> bool:
        return self.why_incomplete_hint is None

    def convert(self) -> Generator:
        raise NotImplementedError


class NumberRangeForm(ParameterRangeForm):
    PEER = NumberParameter
    RANGE = NumberRange

    DOUBLE_VALIDATOR = QDoubleValidator()
    _locale = QLocale(QLocale.Language.English)
    _locale.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
    DOUBLE_VALIDATOR.setLocale(_locale)
    del _locale

    def __init__(self):
        super().__init__()

        self.input_distribution = QComboBox()
        self.input_distribution.addItem('evenly spaced', Distribution.GRID)
        self.input_distribution.addItem('randomly', Distribution.RANDOM)

        self.input_lower_bound = QLineEdit()
        self.input_lower_bound.setValidator(self.DOUBLE_VALIDATOR)
        self.input_lower_bound.setPlaceholderText('lower bound')

        self.input_upper_bound = QLineEdit()
        self.input_upper_bound.setValidator(self.DOUBLE_VALIDATOR)
        self.input_upper_bound.setPlaceholderText('upper bound')

        self.input_count = QLineEdit()
        self.input_count.setValidator(QIntValidator())
        self.input_count.setPlaceholderText('count')

        self.input_transformation = QComboBox()
        self.input_transformation.addItem('linear', Linear)
        self.input_transformation.addItem('log-linear', Log10)
        self.input_transformation.setToolTip(
            'linear: distribute data points directly between the specified boundaries\n'
            'log-linear: take the log10 of the boundaries, then distribute data points and finally convert them back '
            'via 10^x'
        )

        layout = QHBoxLayout()
        layout.addWidget(QLabel('Distribute'))
        layout.addWidget(self.input_distribution)
        layout.addWidget(QLabel('from'))
        layout.addWidget(self.input_lower_bound)
        layout.addWidget(QLabel('to'))
        layout.addWidget(self.input_upper_bound)
        layout.addWidget(QLabel('using'))
        layout.addWidget(self.input_count)
        layout.addWidget(QLabel('points'))
        layout.addWidget(QLabel('(scale:'))
        layout.addWidget(self.input_transformation)
        layout.addWidget(QLabel(')'))
        layout.addStretch(1)
        self.setLayout(layout)

        self.input_lower_bound.textEdited.connect(lambda text: self.content_changed.emit())
        self.input_upper_bound.textEdited.connect(lambda text: self.content_changed.emit())
        self.input_count.textEdited.connect(lambda text: self.content_changed.emit())
        self.input_count.textEdited.connect(lambda text: self.count_changed.emit())

    @property
    def count(self) -> int:
        try:
            return int(self.input_count.text())
        except ValueError:
            return _NO_COUNT

    @property
    def why_incomplete_hint(self) -> Union[str, None]:
        if not self.input_lower_bound.text():
            return 'Lower boundary missing'
        elif not self.input_upper_bound.text():
            return 'Upper boundary missing'
        elif self.count is _NO_COUNT:
            return 'Count missing'
        else:
            return None

    def convert(self) -> Generator:
        return self.RANGE(
            float(self.input_lower_bound.text()),
            float(self.input_upper_bound.text()),
            int(self.input_count.text()),
            self.input_distribution.currentData(),
            self.input_transformation.currentData(),
        )


class IntegerRangeForm(NumberRangeForm):
    PEER = IntegerParameter
    RANGE = IntegerRange


class FilepathRangeForm(ParameterRangeForm):
    PEER = FilepathParameter

    def __init__(self):
        super().__init__()

        self.input_directory = SelectExistingDirectoryWidget()

        self.input_filter_pattern = QLineEdit()
        self.input_filter_pattern.setPlaceholderText('glob pattern (optional)')

        self.label_how_many_files = QLabel('')

        layout = QHBoxLayout()
        layout.addWidget(QLabel('Scan'))
        layout.addWidget(self.input_directory)
        layout.addWidget(QLabel('using filter'))
        layout.addWidget(self.input_filter_pattern)
        layout.addWidget(self.label_how_many_files)
        layout.addStretch(1)

        self.setLayout(layout)

        self.input_directory.textChanged.connect(lambda text: self.content_changed.emit())
        self.input_directory.textChanged.connect(lambda text: self.count_changed.emit())

        self.input_filter_pattern.textChanged.connect(lambda text: self.count_changed.emit())

        self.count_changed.connect(self._update_how_many_files)

    @property
    def count(self) -> int:
        if self.why_incomplete_hint is None:
            return self.convert().count
        else:
            return _NO_COUNT

    @property
    def why_incomplete_hint(self) -> Union[str, None]:
        if not self.input_directory.text():
            return 'Directory missing'
        elif not Path(self.input_directory.text()).is_dir():
            return f'{self.input_directory.text()!s} does not point to an existing directory'
        else:
            return None

    def get_filter_pattern(self) -> str:
        return self.input_filter_pattern.text() or '*'

    def _update_how_many_files(self):
        if (count := self.count) is not _NO_COUNT:
            self.label_how_many_files.setText(f'({count} files)')
        else:
            self.label_how_many_files.setText('')

    def convert(self) -> Generator:
        return FilepathRange(self.input_directory.text(), self.get_filter_pattern())


def find_form_by_type(t: Type[Parameter]):
    candidates = (c for c in globals().values() if inspect.isclass(c) and issubclass(c, ParameterRangeForm))
    if issubclass(t, PhysicalQuantityParameter):
        t = NumberParameter
    for cls in candidates:
        if cls.PEER == t:
            return cls
    raise LookupError(f'No form for parameter type {t}')


class ParameterRangeWidget(QWidget):

    content_changed = pyqtSignal()
    count_changed = pyqtSignal()

    FORMATTER: dict[Type, Callable[[Any], str]] = {
        float: lambda x: str(x) if x == 0 or 1e-3 <= abs(x) < 1e4 else f'{x:.3e}',
    }

    def __init__(self, name: str, value: Any, form: ParameterRangeForm, *, path: str = None):
        super().__init__()
        self.name = name
        self.form = form
        self.path = path
        layout = QHBoxLayout()
        layout.addWidget(QLabel(f'<b>{name}</b> (value: {self.value_to_string(value)})'))
        layout.addWidget(form)
        self.setLayout(layout)
        self.form.content_changed.connect(lambda: self.content_changed.emit())
        self.form.count_changed.connect(lambda: self.count_changed.emit())

    @property
    def count(self) -> int:
        return self.form.count

    @property
    def is_complete(self) -> bool:
        return self.form.is_complete

    @property
    def why_incomplete_hint(self) -> Union[str, None]:
        if (hint := self.form.why_incomplete_hint) is not None:
            return f'{self.name}: {hint}'
        return None

    def convert(self) -> Generator:
        return self.form.convert()

    @classmethod
    def value_to_string(cls, value):
        for tp, formatter in cls.FORMATTER.items():
            if isinstance(value, tp):
                return formatter(value)
        return str(value)


AParam = namedtuple('AParam', 'active widget')


class CombinationWidget(QWidget):

    content_changed = pyqtSignal()
    count_changed = pyqtSignal()

    def __init__(
        self,
        widgets: Union[list[ParameterRangeWidget | CombinationWidget], dict[str, Sequence[ParameterRangeWidget | CombinationWidget]]],
        *,
        title: str,
        path: str = None,
    ):
        super().__init__()
        self.name = title
        self.path = path

        self.parameters: List[AParam] = []

        self.input_combination_method = QComboBox()
        self.input_combination_method.addItem('product', ProductCombination)
        self.input_combination_method.addItem('zip', ZipCombination)
        self.input_combination_method.currentIndexChanged.connect(lambda index: self.count_changed.emit())
        self.input_combination_method.setToolTip(
            'product: for each data point of a parameter, consider all possible combinations of all other parameters '
            '(n = n1*n2*n3*...)'
            '\n'
            'zip: combine the values of all parameters by building pairs that correspond to the first value of each '
            'parameter, the second value, ... (n = min(n1, n2, n3, ...))'
        )

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel(f'<b>{title}</b>'))
        title_layout.addWidget(QLabel('combine as'))
        title_layout.addWidget(self.input_combination_method)
        title_layout.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(title_layout)
        if isinstance(widgets, list):
            layout.addLayout(self._create_flat_layout(widgets))
        elif isinstance(widgets, dict):
            layout.addLayout(self._create_nested_layout(widgets))
        else:
            raise TypeError(f'Invalid container type for widgets: {type(widgets)}')
        layout.addStretch(1)
        self.setLayout(layout)

        self.setStyleSheet('CombinationWidget { border: 1px solid black; border-radius: 5px; }')
        self.setAttribute(Qt.WA_StyledBackground, True)

    def _create_flat_layout(self, widgets: list[ParameterRangeWidget | CombinationWidget]):
        class NonFolder(QWidget):
            def __init__(self, *, title):
                super().__init__()
                self._title = title

            def notify_parameter_activated(self, param, active):
                pass

            def setContentLayout(self, layout):
                self.setLayout(layout)

        # The dict key is not important, it will be ignored by NonFolder.
        return self._create_layout(dict(_=widgets), NonFolder)

    def _create_nested_layout(self, widgets: dict[str, Sequence[ParameterRangeWidget | CombinationWidget]]):
        class ColorFolder(Folder):
            COLOR_INACTIVE = '000000'
            COLOR_ACTIVE = '009925'

            def __init__(self, *, title):
                super().__init__(title=title)
                self._activate_count = 0

            # noinspection PyUnusedLocal
            def notify_parameter_activated(self, param, active):
                self._activate_count += (2*active - 1)
                if self._activate_count > 0:
                    style_sheet = f'QToolButton {{ border: none; color: #{self.COLOR_ACTIVE}}}'
                elif self._activate_count == 0:
                    style_sheet = f'QToolButton {{ border: none; color: #{self.COLOR_INACTIVE}}}'
                else:
                    assert False
                self.toggleButton.setStyleSheet(style_sheet)

        return self._create_layout(widgets, ColorFolder)

    def _create_layout(
        self,
        widget_groups: dict[str, Sequence[ParameterRangeWidget | CombinationWidget]],
        group_container_cls,
    ):
        def _generate_checkbox_slot(param: QWidget, group_):
            def _slot(state):
                active = state == Qt.CheckState.Checked
                param.setEnabled(active)
                group_.notify_parameter_activated(param, active)
            return _slot

        layout = QVBoxLayout()
        for group_title, widgets in widget_groups.items():
            group = group_container_cls(title=group_title)
            group_layout = QVBoxLayout()
            for parameter in widgets:
                parameter.setEnabled(False)
                parameter.content_changed.connect(lambda: self.content_changed.emit())
                parameter.count_changed.connect(lambda: self.count_changed.emit())
                check_box = QCheckBox()
                check_box.stateChanged.connect(_generate_checkbox_slot(parameter, group))
                check_box.stateChanged.connect(lambda: self.content_changed.emit())
                check_box.stateChanged.connect(lambda: self.count_changed.emit())
                parameter_layout = QHBoxLayout()
                parameter_layout.addWidget(check_box)
                parameter_layout.addWidget(parameter)
                group_layout.addLayout(parameter_layout)
                self.parameters.append(AParam(check_box, parameter))
            group.setContentLayout(group_layout)
            layout.addWidget(group)
        return layout

    @property
    def active_widgets(self) -> List[ParameterRangeWidget|CombinationWidget]:
        return [p.widget for p in self.parameters if p.active.checkState() == Qt.CheckState.Checked]

    @property
    def count(self) -> int:
        if self.active_widgets:
            combination_method = self.input_combination_method.currentData()
            return combination_method(self.active_widgets).count
        else:
            return _NO_COUNT

    @property
    def is_complete(self) -> bool:
        return all(w.is_complete for w in self.active_widgets)

    @property
    def why_incomplete_hint(self) -> Union[str, None]:
        if (hint := next((w.why_incomplete_hint for w in self.active_widgets if not w.is_complete), None)) is not None:
            return f'{self.name}/{hint}'
        return None

    def convert(self) -> Combinator:
        method = self.input_combination_method.currentData()
        if method is ZipCombination and len({w.count for w in self.active_widgets}) > 1:
            QMessageBox.warning(
                self,
                f'{self.path}/{self.name}' if self.path else self.name,
                'ZIP combination will discard excess data points if not all parameters have the same count.',
            )
        return Combinator([w.convert() for w in self.active_widgets], method=method)


class VectorCombinationWidget(CombinationWidget):
    def __init__(
        self,
        names: Sequence[str],
        values: Sequence[Any],
        forms: Sequence[ParameterRangeForm],
        *,
        default_values: Sequence[Any],
        title: str,
        path: str = None,
    ):
        assert len(names) == len(values) == len(forms)
        widgets = [ParameterRangeWidget(name, value, form) for name, value, form in zip(names, values, forms)]
        super().__init__(widgets, title=title, path=path)
        self.default_values = default_values
        assert len(self.parameters) == len(self.default_values)

    def convert(self) -> Combinator:
        super().convert()  # Display warnings, if applicable.
        method = self.input_combination_method.currentData()
        if method is ProductCombination:
            default_generator = partial(SequenceGenerator.from_value, count=1)
        elif method is ZipCombination:
            default_generator = partial(SequenceGenerator.from_value, count=self.count)
        else:
            assert False
        active_widgets = self.active_widgets
        return Combinator(
            [p.widget.convert() if p.widget in active_widgets else default_generator(v)
             for p, v in zip(self.parameters, self.default_values)],
            method=method,
        )


def find_widget_for_parameter(parameter: Parameter, value: Any, *, path: str = None):
    p_type = type(parameter)
    is_vector_parameter = p_type.__name__.endswith(('Duplet', 'Triplet', 'Vector'))
    if is_vector_parameter:
        # noinspection PyProtectedMember
        p_type = parameter._element_type
    if issubclass(p_type, PhysicalQuantityParameter):
        value_formatter = lambda v: f'{ParameterRangeWidget.value_to_string(v)} {parameter.unit!s}'
    else:
        value_formatter = ParameterRangeWidget.value_to_string
    if is_vector_parameter:
        f_type = find_form_by_type(p_type)
        widget = VectorCombinationWidget(
            names=[f'[{i}]' for i in range(len(value))],
            values=[value_formatter(v) for v in value],
            forms=[f_type() for _ in value],
            default_values=value,
            title=parameter.name,
            path=path,
        )
    else:
        f_type = find_form_by_type(p_type)
        widget = ParameterRangeWidget(
            name=parameter.name,
            value=value_formatter(value),
            form=f_type(),
            path=path,
        )
    return widget


class SelectExistingDirectoryWidget(QWidget):
    PEER = FilepathParameter
    INPUT_FIELD_PADDING = 30

    def __init__(self):
        super().__init__()
        self.input = QLineEdit()
        self.input.setPlaceholderText('directory')
        self.input.textChanged.connect(self._resize_line_edit)
        self._input_min_width = self.input.width()
        self.input.setFixedWidth(self._input_min_width)
        button = QPushButton(QIcon.fromTheme('folder-open'), '')
        button.clicked.connect(lambda: self.input.setText(
            QFileDialog.getExistingDirectory(caption='Choose an existing directory')))
        layout = QHBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(button)
        self.setLayout(layout)

    @property
    def textChanged(self):
        return self.input.textChanged

    def text(self):
        return self.input.text()

    def _resize_line_edit(self, text):
        font_metric = QFontMetrics(self.input.font())
        self.input.setFixedWidth(max(font_metric.width(text) + self.INPUT_FIELD_PADDING, self._input_min_width))
        self.adjustSize()


class SequenceGenerator(Generator):
    def __init__(self, sequence: Sequence):
        self.sequence = sequence

    @property
    def count(self) -> int:
        return len(self.sequence)

    def generate(self) -> Sequence:
        return self.sequence

    @classmethod
    def from_value(cls, value: Any, *, count: int):
        return cls([value] * count)


class _NAInt(int):
    def _op(self, other):
        if isinstance(other, int):
            return self
        return NotImplemented

    __add__ = __radd__ = __mul__ = __rmul__ = _op


_NO_COUNT = _NAInt()


class SweepWidget(QWidget):

    WIDGET_TITLE = 'Parameter sweep'

    generate_callbacks: List[Callable[[Sweep], None]]

    def __init__(
        self,
        widget_groups: dict[str, Sequence[ParameterRangeWidget | CombinationWidget]],
    ):
        super().__init__()

        self.combination_widget = CombinationWidget(widget_groups, title=self.WIDGET_TITLE)
        self.generate_callbacks = []

        self.button_generate = QPushButton('Generate')
        self.button_generate.setEnabled(False)
        self.button_generate.clicked.connect(self.generate)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.button_generate)
        button_layout.addStretch(1)

        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.combination_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.combination_widget.content_changed.connect(self._content_changed_slot)
        self.combination_widget.count_changed.connect(self._count_changed_slot)

    @property
    def is_complete(self) -> bool:
        return self.combination_widget.count is not _NO_COUNT and self.combination_widget.is_complete

    @property
    def why_incomplete_hint(self) -> Union[str, None]:
        return self.combination_widget.why_incomplete_hint

    def _count_changed_slot(self):
        if (count := self.combination_widget.count) is not _NO_COUNT:
            self.button_generate.setText(f'Generate (n = {count})')
        else:
            self.button_generate.setText('Generate')

    def _content_changed_slot(self):
        self.button_generate.setEnabled(self.is_complete)
        self.button_generate.setToolTip(self.why_incomplete_hint or '')

    def generate(self):
        names = [(f'{w.path}/{w.name}' if w.path else w.name) for w in self.combination_widget.active_widgets]
        sweep = Sweep(names, self.combination_widget.convert())
        for callback in self.generate_callbacks:
            callback(sweep)

    @classmethod
    def from_configuration(cls, adaptor: ConfigurationAdaptor, parameters: dict[str, list[Parameter]]) -> SweepWidget:
        widgets = defaultdict(list)
        for config_path, params in parameters.items():
            for param in params:
                widgets[config_path].append(find_widget_for_parameter(
                    param,
                    param.load_from_configuration(adaptor, config_path),
                    path=config_path,
                ))
        return cls(widgets)
