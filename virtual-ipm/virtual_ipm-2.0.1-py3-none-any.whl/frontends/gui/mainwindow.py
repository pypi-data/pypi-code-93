#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
from xml.etree.ElementTree import ParseError

from anna import load_from_file, JSONAdaptor, XMLAdaptor
from anna.exceptions import ConfigurationError, InvalidPathError
from anna.frontends.qt import parameters
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as Widgets

import virtual_ipm
from .about import add_help_menu
from .utils import getOpenFileName, getSaveFileName
from . import views
from .simulation.views import MainView as SimulationView
from .analysis.views import InitialFinalMapAnalyzer
from .sweeps.main import SweepWindow


class MainWidget(Widgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._load_views()

    def _load_views(self):
        self.views = [
            views.Beams(self),
            views.Device(self),
            views.ParticleGeneration(self),
            views.ParticleTracking(self),
            views.ElectricGuidingField(self),
            views.MagneticGuidingField(self),
            views.Simulation(self),
            views.Output(self),
        ]
        self._layout_views()

    def _layout_views(self):
        self._tab_widget = tab_widget = Widgets.QTabWidget()
        for view in self.views:
            tab_widget.addTab(view, view.__class__.__name__)
        layout = Widgets.QVBoxLayout()
        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def get_json_config(self):
        config = JSONAdaptor()
        for view in self.views:
            try:
                config.insert_config('', view.dump_as_json())
            except parameters.InvalidInputError as err:
                Widgets.QMessageBox.critical(
                    self,
                    type(err).__name__,
                    str(err),
                )
                if err.origin is not None:
                    self.set_focus_on_input(err.origin)
                return None
        return config

    def get_xml_config(self):
        config = XMLAdaptor(root='Virtual-IPM')
        config._root.attrib['version'] = virtual_ipm.__version__
        for view in self.views:
            try:
                config.insert_config('', view.dump_as_xml())
            except parameters.InvalidInputError as err:
                Widgets.QMessageBox.critical(
                    self,
                    type(err).__name__,
                    str(err),
                )
                if err.origin is not None:
                    self.set_focus_on_input(err.origin)
                return None
        return config

    def open_file(self):
        filename = str(
            getOpenFileName(
                caption='Open configuration file',
                filter='XML Files (*.xml);;All Files (*.*)'
            )
        )
        if not filename:
            return
        try:
            configuration = XMLAdaptor(filepath=filename)
            for view in self.views:
                view.load_from_source(configuration)
        except (ConfigurationError, parameters.InvalidInputError) as err:
            Widgets.QMessageBox.critical(
                self,
                'Invalid configuration file',
                f'The content of the specified configuration file seems not to be valid.\n'
                f'I encountered the following error: {err}.'
            )
        except ParseError as err:
            Widgets.QMessageBox.critical(
                self,
                'Invalid format',
                f"The specified file doesn't seem to be a valid XML file.\n"
                f"I encountered the following error: {err}."
            )

    def save_as_json(self):
        config = self.get_json_config()
        if config is None:
            return
        print(config)
        filename = str(
            getSaveFileName(
                caption='Save as JSON',
                filter='JSON Files (*.json);;All Files (*.*)'
            )
        )
        if not filename:
            return
        config.dump_to_file(filename)

    def save_as_xml(self):
        config = self.get_xml_config()
        if config is None:
            return
        print(config)
        filename = str(
            getSaveFileName(
                caption='Save as XML',
                filter='XML Files (*.xml);;All Files (*.*)'
            )
        )
        if not filename:
            return
        config.dump_to_file(filename)

    def set_focus_on_input(self, origin):
        parent_chain = []

        def add_parent(widget):
            if widget.parent() is not None:
                parent_chain.append(widget.parent())
                add_parent(widget.parent())

        add_parent(origin)
        corresponding_view = list(filter(
            lambda view: view in parent_chain,
            self.views
        ))
        if corresponding_view:
            self._tab_widget.setCurrentWidget(corresponding_view[0])
            corresponding_view[0].set_focus_on_input(origin)


class MainWindow(Widgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('[IPMSim] Virtual-IPM')
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.split(__file__)[0], 'icons/vipm.png')))

        self.main_widget = MainWidget(self)
        scroll_area = Widgets.QScrollArea()
        scroll_area.setWidget(self.main_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        self._results_analyzer = []
        self._simulation_views = []

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        file_save_as_menu = file_menu.addMenu('Save as')
        simulation_menu = menubar.addMenu('Simulation')

        # save_as_json_action = Widgets.QAction('JSON', self.main_widget)
        # save_as_json_action.triggered.connect(self.main_widget.save_as_json)
        # file_save_as_menu.addAction(save_as_json_action)

        save_as_xml_action = Widgets.QAction(
            QtGui.QIcon(os.path.join(os.path.split(__file__)[0], 'icons/save_xml.png')),
            'XML',
            self.main_widget
        )
        save_as_xml_action.triggered.connect(self.main_widget.save_as_xml)
        file_save_as_menu.addAction(save_as_xml_action)

        open_file_action = Widgets.QAction(
            QtGui.QIcon(os.path.join(os.path.split(__file__)[0], 'icons/open_xml.png')),
            'Load configuration',
            self.main_widget
        )
        open_file_action.triggered.connect(self.main_widget.open_file)
        open_file_action.setShortcut(QtGui.QKeySequence.Open)
        file_menu.addAction(open_file_action)

        run_simulation_action = Widgets.QAction(
            QtGui.QIcon(os.path.join(os.path.split(__file__)[0], 'icons/run.png')),
            'Run current configuration',
            self
        )
        run_simulation_action.triggered.connect(self.run_simulation)
        run_simulation_action.setShortcut(QtGui.QKeySequence('Ctrl+R'))
        simulation_menu.addAction(run_simulation_action)

        run_simulation_from_file_action = Widgets.QAction(
            QtGui.QIcon(os.path.join(os.path.split(__file__)[0], 'icons/run_from_file.png')),
            'Run configuration from file',
            self
        )
        run_simulation_from_file_action.triggered.connect(self.run_simulation_from_file)
        run_simulation_from_file_action.setShortcut(QtGui.QKeySequence('Ctrl+F'))
        simulation_menu.addAction(run_simulation_from_file_action)

        analyze_results_action = Widgets.QAction(
            QtGui.QIcon(os.path.join(os.path.split(__file__)[0], 'icons/data-analysis.png')),
            'Analyze results',
            self
        )
        analyze_results_action.triggered.connect(self.analyze_results)
        analyze_results_action.setShortcut(QtGui.QKeySequence('Ctrl+A'))
        simulation_menu.addAction(analyze_results_action)

        parameter_sweep_action = Widgets.QAction(
            QtGui.QIcon(os.path.join(os.path.split(__file__)[0], 'icons/parameter_sweep.png')),
            'Parameter sweep',
            self,
        )
        parameter_sweep_action.triggered.connect(lambda: SweepWindow().show())
        simulation_menu.addAction(parameter_sweep_action)

        add_help_menu(menubar, widget=self.main_widget, parent=self)

        toolbar = Widgets.QToolBar()
        toolbar.addAction(open_file_action)
        save_as_xml_toolbar_action = Widgets.QAction(
            QtGui.QIcon(os.path.join(os.path.split(__file__)[0], 'icons/save_xml.png')),
            'Save configuration as XML',
            self.main_widget
        )
        save_as_xml_toolbar_action.triggered.connect(self.main_widget.save_as_xml)
        toolbar.addAction(save_as_xml_toolbar_action)
        toolbar.addAction(run_simulation_from_file_action)
        toolbar.addAction(run_simulation_action)
        toolbar.addAction(analyze_results_action)
        toolbar.addAction(parameter_sweep_action)
        self.addToolBar(toolbar)

        self.resize(QtCore.QSize(750, 1000))

    def run_simulation(self):
        config = self.main_widget.get_xml_config()
        if config is None:
            return
        from virtual_ipm.simulation.output import OutputRecorder
        try:
            output_filepath = config.get_text(
                config.join_paths(
                    OutputRecorder.CONFIG_PATH,
                    'Filename'
                )
            )
        except InvalidPathError:
            Widgets.QMessageBox.information(
                self,
                'Configuration needs to be saved',
                "I couldn't determine a suitable file path for saving your current "
                "configuration. Please choose one manually."
            )
            filename = str(
                getSaveFileName(
                    caption='Choose a file for saving the configuration',
                    filter='XML Files (*.xml);;All Files (*.*)'
                )
            )
        else:
            base_path = os.path.splitext(output_filepath)[0]
            filename = base_path + '.config.xml'
            if os.path.exists(filename):
                Widgets.QMessageBox.information(
                    self,
                    'File already exists',
                    "I tried to save the current configuration as %s however the file already "
                    "exists. Please choose a different one." % filename
                )
                base_dir = os.path.split(base_path)[0]
                filename = str(
                    getSaveFileName(
                        caption='Choose a file for saving the configuration',
                        directory=base_dir,
                        filter='XML Files (*.xml);;All Files (*.*)'
                    )
                )
            else:
                Widgets.QMessageBox.information(
                    self,
                    'Saving configuration',
                    'I will save the current configuration as %s' % filename
                )
        if not filename:
            return
        config.dump_to_file(filename)
        self._simulation_views.append(
            SimulationView(
                load_from_file(str(filename))
            )
        )
        self._simulation_views[-1].show()

    def run_simulation_from_file(self):
        configuration_file_name = getOpenFileName(
            self,
            'Choose a configuration file',
            filter='XML Files (*.xml);;All Files (*.*)'
        )
        if not configuration_file_name:
            return
        self._simulation_views.append(
            SimulationView(
                load_from_file(str(configuration_file_name))
            )
        )
        self._simulation_views[-1].show()

    def analyze_results(self):
        self._results_analyzer.append(InitialFinalMapAnalyzer(parent=self))
        self._results_analyzer[-1].show()
