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


from collections import defaultdict
import logging
import re
import sys

from anna.frontends.qt.views import ParametrizedComponentView
import matplotlib.pyplot as plt
# noinspection PyUnresolvedReferences
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.backends.backend_qt5agg
import numpy as np
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as Widgets
from rx.concurrency import current_thread_scheduler

from virtual_ipm.control.commands import issue_stop_command
from virtual_ipm.control.threading import SimulationThread
from virtual_ipm.log import add_handler, remove_handler, SubjectHandler
from virtual_ipm.simulation.auxiliaries import Particle
from virtual_ipm.simulation.errors import SetupError
import virtual_ipm.simulation.output as simulation_output

FigureCanvas = matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg


class LogView(Widgets.QWidget):
    new_message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.text_view = Widgets.QTextEdit()
        self.text_view.setReadOnly(True)

        layout = Widgets.QVBoxLayout()
        layout.addWidget(self.text_view)
        self.setLayout(layout)

        self._handler = SubjectHandler(level=logging.INFO)

        self._subscription = self._handler.records.observe_on(current_thread_scheduler)\
            .filter(lambda msg: re.match(r'^\[[A-Z]+\] Completed step \d+$', msg) is None)\
            .subscribe(on_next=self.new_message.emit)
        self.new_message.connect(self.update_view)

        add_handler(self._handler)

    def clean_up(self):
        remove_handler(self._handler)
        self._subscription.dispose()
        self.new_message.disconnect()

    def update_view(self, message):
        self.text_view.setText('\n'.join([str(self.text_view.toPlainText()), str(message)]))


class ProgressView(Widgets.QWidget):
    next_step = QtCore.pyqtSignal(int)

    def __init__(self, progress, parent=None):
        super().__init__(parent)
        self._progress = Widgets.QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)

        layout = Widgets.QVBoxLayout()
        layout.addWidget(self._progress)
        self.setLayout(layout)

        self._subscription = progress.observe_on(current_thread_scheduler) \
            .map(lambda x: ((x.step + 1) * 100) / x.max_steps) \
            .filter(lambda x: x > self._progress.value()) \
            .subscribe(on_next=self.next_step.emit)

        self.next_step.connect(self.update_view)

    def clean_up(self):
        self._subscription.dispose()
        self.next_step.disconnect()

    def update_view(self, percentage):
        self._progress.setValue(percentage)


class ParticlesView(Widgets.QWidget):
    row_number_per_status = {
        Particle.Status.TRACKED: 0,
        Particle.Status.DETECTED: 1,
        Particle.Status.INVALID: 2,
    }
    update_interval = 200  # milliseconds

    def __init__(self, status_updates, parent=None):
        super().__init__(parent)
        self._statistics = Widgets.QTableWidget()
        self._statistics.setColumnCount(2)
        self._statistics.setRowCount(3)

        def set_label_for_status(status):
            self._statistics.setItem(
                self.row_number_per_status[status],
                0,
                Widgets.QTableWidgetItem(Particle._statuses[status].capitalize())
            )
            self._statistics.setItem(
                self.row_number_per_status[status],
                1,
                Widgets.QTableWidgetItem('0')
            )

        set_label_for_status(Particle.Status.TRACKED)
        set_label_for_status(Particle.Status.DETECTED)
        set_label_for_status(Particle.Status.INVALID)

        layout = Widgets.QVBoxLayout()
        layout.addWidget(self._statistics)
        self.setLayout(layout)

        self._counts_per_status = defaultdict(int)

        def on_status_update(update):
            self._counts_per_status[update.old_status] -= 1
            self._counts_per_status[update.particle.status] += 1

        self._subscription = status_updates.observe_on(current_thread_scheduler).\
            subscribe(on_next=on_status_update)

        self._update_timer = QtCore.QTimer()
        self._update_timer.setInterval(self.update_interval)
        # noinspection PyUnresolvedReferences
        self._update_timer.timeout.connect(self.update_statistics)
        self._update_timer.start()

    def clean_up(self):
        self._subscription.dispose()
        self._update_timer.stop()
        # noinspection PyUnresolvedReferences
        self._update_timer.timeout.disconnect()

    def update_statistics(self):
        for status, row_number in iter(self.row_number_per_status.items()):
            self._statistics.item(row_number, 1).setText('%d' % self._counts_per_status[status])


class ParticleMonitor(Widgets.QWidget):
    update_interval = 100  # milliseconds

    def __init__(self, position_updates, parent=None):
        super().__init__(parent=parent, flags=QtCore.Qt.WindowType.Widget)
        self._figure_xyz = plt.figure()
        self._axes_xyz = self._figure_xyz.add_subplot(111, projection='3d')
        self._canvas_xyz = FigureCanvas(self._figure_xyz)

        self._figure_xy = plt.figure()
        self._axes_xy = self._figure_xy.add_subplot(111)
        self._canvas_xy = FigureCanvas(self._figure_xy)

        self._figure_xz = plt.figure()
        self._axes_xz = self._figure_xz.add_subplot(111)
        self._canvas_xz = FigureCanvas(self._figure_xz)

        self._figure_yz = plt.figure()
        self._axes_yz = self._figure_yz.add_subplot(111)
        self._canvas_yz = FigureCanvas(self._figure_yz)

        self._plot_selector = Widgets.QComboBox()
        self._plot_stack = Widgets.QStackedWidget()

        self._plot_selector.addItem('3d')
        self._plot_stack.addWidget(self._canvas_xyz)
        self._plot_selector.addItem('xy-plane')
        self._plot_stack.addWidget(self._canvas_xy)
        self._plot_selector.addItem('xz-plane')
        self._plot_stack.addWidget(self._canvas_xz)
        self._plot_selector.addItem('yz-plane')
        self._plot_stack.addWidget(self._canvas_yz)

        self._plot_selector.currentIndexChanged.connect(self._plot_stack.setCurrentIndex)

        v_layout = Widgets.QVBoxLayout()
        h_layout = Widgets.QHBoxLayout()
        h_layout.addWidget(self._plot_selector)
        h_layout.addStretch(1)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self._plot_stack)
        self.setLayout(v_layout)

        self._trajectories = defaultdict(list)

        self._subscription = position_updates.subscribe(on_next=self.new_position)

        self._plot_timer = QtCore.QTimer()
        self._plot_timer.setInterval(self.update_interval)
        # noinspection PyUnresolvedReferences
        self._plot_timer.timeout.connect(self.plot_positions)
        self._plot_timer.start()

    def clean_up(self):
        self._subscription.dispose()
        self._plot_timer.stop()
        # noinspection PyUnresolvedReferences
        self._plot_timer.timeout.disconnect()

    def new_position(self, update):
        uuid, position = update
        self._trajectories[uuid].append(position)

    def plot_positions(self):
        {
            0: ParticleMonitor.plot_xyz,
            1: ParticleMonitor.plot_xy,
            2: ParticleMonitor.plot_xz,
            3: ParticleMonitor.plot_yz,
        }[self._plot_selector.currentIndex()](self)

    def plot_xyz(self):
        self._axes_xyz.clear()
        self._axes_xyz.set_xlabel('x [mm]')
        self._axes_xyz.set_ylabel('y [mm]')
        self._axes_xyz.set_zlabel('z [mm]')
        for positions in self._trajectories.values():
            positions = np.array(positions) * 1.0e3  # [m] -> [mm]
            xs, ys, zs = positions[:, 0], positions[:, 1], positions[:, 2]
            self._axes_xyz.plot(xs, ys, zs)
        self._canvas_xyz.draw()

    def plot_xy(self):
        self._axes_xy.clear()
        self._axes_xy.set_xlabel('x [mm]')
        self._axes_xy.set_ylabel('y [mm]')
        for positions in self._trajectories.values():
            positions = np.array(positions) * 1.0e3  # [m] -> [mm]
            xs, ys = positions[:, 0], positions[:, 1]
            self._axes_xy.plot(xs, ys)
        self._canvas_xy.draw()

    def plot_xz(self):
        self._axes_xz.clear()
        self._axes_xz.set_xlabel('x [mm]')
        self._axes_xz.set_ylabel('z [mm]')
        for positions in self._trajectories.values():
            positions = np.array(positions) * 1.0e3  # [m] -> [mm]
            xs, zs = positions[:, 0], positions[:, 2]
            self._axes_xz.plot(xs, zs)
        self._canvas_xz.draw()

    def plot_yz(self):
        self._axes_yz.clear()
        self._axes_yz.set_xlabel('y [mm]')
        self._axes_yz.set_ylabel('z [mm]')
        for positions in self._trajectories.values():
            positions = np.array(positions) * 1.0e3  # [m] -> [mm]
            ys, zs = positions[:, 1], positions[:, 2]
            self._axes_yz.plot(ys, zs)
        self._canvas_yz.draw()


class MainWidget(Widgets.QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self._config = config
        self._thread = SimulationThread()
        self._thread.errors.subscribe(on_next=self.handle_simulation_error)

        self._progress_view = progress_view = ProgressView(self._thread.progress)
        self._particles_view = particles_view = ParticlesView(self._thread.status_updates)
        self._log_view = log_view = LogView()

        self._start_simulation_button = start_button = Widgets.QPushButton('Start simulation')
        start_button.clicked.connect(self.start_simulation)

        def stop_simulation():
            issue_stop_command()
            stop_button.setEnabled(False)

        self._stop_simulation_button = stop_button = Widgets.QPushButton('Stop simulation')
        stop_button.clicked.connect(stop_simulation)
        stop_button.setEnabled(False)

        monitor_particles_button = Widgets.QPushButton('Monitor particles')
        monitor_particles_button.clicked.connect(self.configure_particle_monitor)

        self._publishing_recorder_configuration_widget = ParametrizedComponentView(
            simulation_output.PublishingRecorder
        )
        configuration_container = Widgets.QWidget()
        ok_button = Widgets.QPushButton('Ok')
        ok_button.clicked.connect(self.add_particle_monitor)
        v_layout = Widgets.QVBoxLayout()
        v_layout.addWidget(self._publishing_recorder_configuration_widget)
        h_layout = Widgets.QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(ok_button)
        v_layout.addLayout(h_layout)
        configuration_container.setLayout(v_layout)

        self._particle_monitor = particle_monitor = ParticleMonitor(self._thread.position_updates)

        self._particle_monitor_stack = Widgets.QStackedWidget()
        self._particle_monitor_stack.addWidget(monitor_particles_button)
        self._particle_monitor_stack.addWidget(configuration_container)
        self._particle_monitor_stack.addWidget(particle_monitor)

        layout = Widgets.QVBoxLayout()

        button_layout = Widgets.QHBoxLayout()
        button_layout.addWidget(start_button)
        button_layout.addStretch(1)
        button_layout.addWidget(stop_button)

        layout.addLayout(button_layout)
        layout.addWidget(progress_view)

        v_splitter = Widgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        h_splitter = Widgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        h_splitter.addWidget(particles_view)
        h_splitter.addWidget(log_view)

        v_splitter.addWidget(h_splitter)
        v_splitter.addWidget(self._particle_monitor_stack)

        layout.addWidget(v_splitter)
        self.setLayout(layout)

        self.setWindowTitle('[IPMSim] Virtual-IPM')

    def clean_up(self):
        self._progress_view.clean_up()
        self._particles_view.clean_up()
        self._log_view.clean_up()
        self._particle_monitor.clean_up()

    def handle_simulation_error(self, exc_info):
        Widgets.QMessageBox.critical(
            self,
            exc_info[0].__name__,
            str(exc_info[1])
        )

    def start_simulation(self):
        # noinspection PyBroadException
        try:
            self._thread.setup(self._config)
            self._thread.prepare()
        except SetupError as err:
            Widgets.QMessageBox.critical(self, f'{type(err).__name__} ({type(err.instance).__name__})', str(err))
        except Exception:
            self.handle_simulation_error(sys.exc_info())
        else:
            self._thread.start()
            self._start_simulation_button.setEnabled(False)
            self._stop_simulation_button.setEnabled(True)

    def add_particle_monitor(self):
        output_recorder = self._config.get_text(
            simulation_output.OutputRecorder.CONFIG_PATH_TO_IMPLEMENTATION
        )
        output_recorder += ', ' + simulation_output.PublishingRecorder.__name__
        config = self._publishing_recorder_configuration_widget.dump_as_xml()
        self._config.insert_config('', config)
        self._config.insert_element(
            simulation_output.OutputRecorder.CONFIG_PATH_TO_IMPLEMENTATION,
            output_recorder,
            replace=True
        )
        print(self._config)
        self._particle_monitor_stack.setCurrentIndex(2)

    def configure_particle_monitor(self):
        self._particle_monitor_stack.setCurrentIndex(1)


class MainView(Widgets.QMainWindow):
    def __init__(self, config, parent=None):
        super().__init__(parent)

        self._main_widget = MainWidget(config)
        self.setCentralWidget(self._main_widget)

        self.setWindowTitle('[IPMSim] Virtual-IPM')

    def closeEvent(self, event):
        self._main_widget.clean_up()
        super().closeEvent(event)
