from __future__ import annotations

from collections import defaultdict
import inspect
import os
from pathlib import Path
from typing import Type

from anna.adaptors import XMLAdaptor
from anna.configuration import Configurable
from anna.exceptions import IncompleteConfigurationError, InvalidPathError
from anna.frontends.qt.sweeps import SweepWidget, SelectExistingDirectoryWidget
from anna.parameters import AwareParameter, ActionParameter, SubstitutionParameterGroup, Parameter, PhysicalQuantityParameter
from anna.sweeps import Sweep, Generate
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QShortcut,
    QPushButton, QVBoxLayout, QWidget,
)

from virtual_ipm.simulation.beams.bunches.bunch import Bunch
import virtual_ipm.simulation.beams.bunches.shapes as bunch_shapes
import virtual_ipm.simulation.beams.bunch_trains as bunch_trains
import virtual_ipm.simulation.particle_tracking.em_fields.guiding_fields.models.electric as electric_guiding_field_models
import virtual_ipm.simulation.particle_tracking.em_fields.guiding_fields.models.magnetic as magnetic_guiding_field_models
from virtual_ipm.simulation.setup import SimulationParameters
from virtual_ipm.simulation.output import OutputRecorder

from ..about import add_help_menu
from ..utils import pad_hv


class _Bunch(Bunch):
    CONFIG_PATH_TO_IMPLEMENTATION = None


class _SimulationParameters(SimulationParameters):
    CONFIG_PATH_TO_IMPLEMENTATION = None


# noinspection PyProtectedMember
PARAMETERS: dict[Type[Configurable], dict[str|None, list[AwareParameter]]] = {
    _Bunch: {
        None: [
            Bunch._energy,
            Bunch._bunch_population,
        ],
    },
}
AUTO = object()
for interface, module in (
    (AUTO, bunch_shapes),
    (bunch_trains.BunchTrain, bunch_trains),
    (AUTO, electric_guiding_field_models),
    (AUTO, magnetic_guiding_field_models),
):
    if interface is AUTO:
        interface = module.Interface
    models = [x for x in vars(module).values() if inspect.isclass(x) and issubclass(x, interface)]
    PARAMETERS[interface] = {model.__name__: model.get_parameters() for model in models}
del interface, module, models

# noinspection PyProtectedMember
PARAMETERS[_SimulationParameters] = {
    None: [
        SimulationParameters._number_of_particles,
    ],
}


class SweepWindow(QMainWindow):
    DEFAULT_SIZE_WITHOUT_CONTENT = 400, 400
    DEFAULT_SIZE_WITH_CONTENT = 1400, 800
    SWEEP_FILE_NAME = 'sweep.json'
    WINDOW_TITLE = '[Virtual-IPM] Parameter Scan'

    def __init__(self):
        super().__init__()

        self.seed_file_path = None
        self.meta = {}
        self.default_values = {}

        open_file_icon = QIcon(os.path.join(os.path.split(__file__)[0], '..', 'icons/open_xml.png'))
        open_file_action = QAction(open_file_icon, 'Load seed configuration', self)
        open_file_action.triggered.connect(self.load_seed_configuration)
        self._open_file_shortcut = QShortcut(QKeySequence('Ctrl+O'), self)
        self._open_file_shortcut.activated.connect(self.load_seed_configuration)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        file_menu.addAction(open_file_action)
        add_help_menu(menubar, widget=self, parent=self)

        button_open_file = QPushButton(open_file_icon, 'Load seed configuration')
        button_open_file.clicked.connect(self.load_seed_configuration)
        _button_widget = QWidget()
        _button_widget.setLayout(pad_hv(button_open_file))
        self.setCentralWidget(_button_widget)
        self.resize(*self.DEFAULT_SIZE_WITHOUT_CONTENT)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowIcon(QIcon(os.path.join(os.path.split(__file__)[0], '..', 'icons/parameter_sweep.png')))

    def generate(self, sweep: Sweep):
        dialog = SaveSweepDialog(parent=self)
        dialog.accepted.connect(lambda: self.save(sweep=sweep, directory=dialog.directory, results=dialog.directory_results))
        dialog.open()

    def save(self, sweep: Sweep, directory: Path, results: Path):
        if results.parent == directory:
            results.mkdir(exist_ok=True)
        with open(directory / self.SWEEP_FILE_NAME, 'w') as fh:
            fh.write(sweep.to_json())
        names = sweep.dataframe.columns
        n_digits = len(str(len(sweep) - 1))
        sweep.dataframe = sweep.dataframe.assign(**{
            f'{OutputRecorder.CONFIG_PATH}/Filename': [
                f'{results.joinpath(str(i).zfill(n_digits) + ".csv")!s}'
                for i in range(len(sweep))
            ]
        })
        Generate(
            sweep,
            seed_path=self.seed_file_path.resolve(),
            folder_path=directory.resolve(),
            config_prefix='',
            meta=self.meta,
            constants={k: v for k, v in self.default_values.items() if k not in names},
        ).all()
        QMessageBox.information(self, 'Success', f'All files have been saved to {directory.resolve()!s}')

    def load_seed_configuration(self):
        path, __ = QFileDialog.getOpenFileName(caption='Choose a seed configuration', filter='*.xml')
        if path:
            self.seed_file_path = Path(str(path))
            seed_config = XMLAdaptor(str(path))
            parameters = defaultdict(list)
            self.meta.clear()
            for base_model, models in PARAMETERS.items():
                if base_model in (_Bunch, bunch_shapes.BunchShape, bunch_trains.BunchTrain):
                    configurations = {f'Beams/Beam[{i}]/{base_model.CONFIG_PATH}': config
                                      for i, config in enumerate(seed_config.get_sub_configurations('Beams'))}
                else:
                    configurations = {base_model.CONFIG_PATH: seed_config}
                for full_config_path, config in configurations.items():
                    if base_model.CONFIG_PATH_TO_IMPLEMENTATION is not None:
                        model_name = config.get_text(base_model.CONFIG_PATH_TO_IMPLEMENTATION).strip()
                    else:
                        model_name = None
                    try:
                        model_params = models[model_name]
                    except KeyError:
                        pass
                    else:
                        for aware_param in model_params:
                            param = _unwrap_parameter(aware_param.parameter)
                            if isinstance(param, SubstitutionParameterGroup):
                                # noinspection PyProtectedMember
                                for option in param._options:
                                    option = _unwrap_parameter(option)
                                    try:
                                        option.load_from_configuration(config, base_model.CONFIG_PATH)
                                    except IncompleteConfigurationError:
                                        pass
                                    else:
                                        param = option
                                        break
                                else:
                                    # None of the options is specified by the configuration file.
                                    QMessageBox.critical(
                                        self,
                                        'Invalid configuration file',
                                        f'Could not find parameter {aware_param} in the configuration file',
                                    )
                                    return

                            param_meta = _extract_meta_data(param)
                            self.meta[f'{full_config_path}/{param.name}'] = param_meta
                            if 'unit' in param_meta:
                                try:
                                    seed_unit = seed_config.get_meta(f'{full_config_path}/{param.name}')['unit']
                                except InvalidPathError:
                                    pass
                                else:
                                    _update_unit(parameter=param, unit=seed_unit)
                            parameters[full_config_path].append(param)
                            self.default_values[f'{full_config_path}/{param.name}'] = param.load_from_configuration(seed_config, full_config_path)
            sweep_widget = SweepWidget.from_configuration(seed_config, parameters)
            sweep_widget.generate_callbacks.append(self.generate)
            self.setCentralWidget(sweep_widget)
            self.resize(*self.DEFAULT_SIZE_WITH_CONTENT)


class SaveSweepDialog(QDialog):
    DIRECTORY_NOT_EMPTY_TITLE = 'Directory not empty'
    DIRECTORY_NOT_EMPTY_MESSAGE = (
        'The chosen directory is not empty; in order to prevent data loss, please empty the directory manually or '
        'choose a different directory.'
    )
    TOOL_TIP_DIRECTORY = 'Configuration files and other auxiliary files will be saved to this directory'
    TOOL_TIP_RESULTS = 'The <Filename> parameter of OutputRecorder will point to this directory'

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.input_directory = SelectExistingDirectoryWidget()
        self.input_directory.setToolTip(self.TOOL_TIP_DIRECTORY)
        self.input_directory_results = SelectExistingDirectoryWidget()
        self.input_directory_results.setToolTip(self.TOOL_TIP_RESULTS)
        self.input_directory_results_customized = False
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout()

        directory_layout = QHBoxLayout()
        _label = QLabel('Save sweep files here:')
        _label.setToolTip(self.TOOL_TIP_DIRECTORY)
        directory_layout.addWidget(_label)
        directory_layout.addWidget(self.input_directory)
        directory_layout.addStretch(1)
        layout.addLayout(directory_layout)

        directory_results_layout = QHBoxLayout()
        _label = QLabel('File path for simulation output files:')
        _label.setToolTip(self.TOOL_TIP_RESULTS)
        directory_results_layout.addWidget(_label)
        directory_results_layout.addWidget(self.input_directory_results)
        directory_results_layout.addStretch(1)
        layout.addLayout(directory_results_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.button_box)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.input_directory.input.textChanged.connect(self._new_directory_selected)
        self.input_directory_results.input.textEdited.connect(self._new_custom_results_directory)
        self.button_box.accepted.connect(self.confirm)
        self.button_box.rejected.connect(self.reject)

    @property
    def directory(self) -> Path:
        return Path(self.input_directory.text())

    @property
    def directory_results(self) -> Path:
        return Path(self.input_directory_results.text())

    def _new_directory_selected(self, directory):
        if not self.input_directory_results_customized:
            self.input_directory_results.input.setText(str(Path(str(directory)).joinpath('results')))

    def _new_custom_results_directory(self, _):
        self.input_directory_results_customized = True

    def confirm(self):
        if not self.input_directory.text():
            QMessageBox.critical(self, 'No directory specified', 'Please choose an existing directory')
            return
        directory = Path(self.input_directory.text())
        if not directory.is_dir():
            QMessageBox.critical(self, 'Directory does not exist', 'Please choose an existing directory')
            return
        if directory.joinpath('configurations').exists():
            QMessageBox.critical(self, self.DIRECTORY_NOT_EMPTY_TITLE, self.DIRECTORY_NOT_EMPTY_MESSAGE)
            return
        self.accept()


def _unwrap_parameter(parameter: Parameter | ActionParameter):
    if isinstance(parameter, ActionParameter):
        # noinspection PyProtectedMember
        return _unwrap_parameter(parameter._parameter)
    return parameter


# noinspection PyProtectedMember
def _extract_meta_data(parameter: Parameter):
    if type(parameter).__name__.endswith(('Duplet', 'Triplet', 'Vector')):
        parameter = parameter._parameter
    if isinstance(parameter, PhysicalQuantityParameter):
        return dict(unit=parameter.unit)
    return {}


# noinspection PyProtectedMember
def _update_unit(parameter: Parameter, unit: str):
    if type(parameter).__name__.endswith(('Duplet', 'Triplet', 'Vector')):
        parameter = parameter._parameter
    parameter.unit = unit
