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

import os
import re

import matplotlib.pyplot as plt
# noinspection PyUnresolvedReferences
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.backends.backend_qt5agg
import numpy as np
import pandas
from pandas.errors import ParserError
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as Widgets

from virtual_ipm.simulation.output import BasicRecorder

from ..utils import getOpenFileName

FigureCanvas = matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg


class InitialFinalMapAnalyzer(Widgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent, flags=QtCore.Qt.WindowType.Window)

        self._profile_plot = ProfilePlot()
        self._initial_scatter = ScatterPlot('initial')
        self._final_scatter = ScatterPlot('final')

        v_splitter = Widgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        v_splitter.addWidget(self._profile_plot)
        h_splitter = Widgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        h_splitter.addWidget(self._initial_scatter)
        h_splitter.addWidget(self._final_scatter)
        v_splitter.addWidget(h_splitter)

        self.setCentralWidget(v_splitter)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        open_file_action = Widgets.QAction(
            QtGui.QIcon(os.path.join(os.path.split(__file__)[0], '../icons/open_xml.png')),
            'Open output file',
            self
        )
        open_file_action.triggered.connect(self.open_file)
        open_file_action.setShortcut(QtGui.QKeySequence.Open)
        file_menu.addAction(open_file_action)

        toolbar = Widgets.QToolBar()
        toolbar.addAction(open_file_action)
        self.addToolBar(toolbar)

        self.setWindowTitle('[IPMSim] Virtual-IPM')
        self.resize(QtCore.QSize(1500, 1000))

    def open_file(self):
        filename = getOpenFileName(
            self,
            caption='Choose an output file',
            filter='CSV Files (*.csv);;All Files (*.*)'
        )
        if not filename:
            return
        try:
            df = pandas.read_csv(filename)
        except ParserError as err:
            Widgets.QMessageBox.critical(
                self,
                type(err).__name__,
                str(err)
            )
        else:
            if 'status' in df:
                statuses, counts = np.unique(df['status'], return_counts=True)
                if 'DETECTED' not in statuses or statuses.size > 1:
                    Widgets.QMessageBox.information(
                        self,
                        'File contains undetected particles',
                        'The selected data file contains particles which are marked as not '
                        'detected. The following statuses were encountered:\n\n'
                        + '\n'.join('{}: {}'.format(s.capitalize(), c)
                                    for s, c in zip(statuses, counts))
                        + '\n\nOnly detected particles will be included in the plots.'
                    )
                    df = df.loc[df['status'] == 'DETECTED']
            self._profile_plot.data_frame = df
            self._initial_scatter.data_frame = df
            self._final_scatter.data_frame = df


class ProfilePlot(Widgets.QWidget):
    bin_size_slider_multiplier = 5

    def __init__(self, df=None, parent=None):
        super().__init__(parent=parent, flags=QtCore.Qt.WindowType.Widget)

        self._df = df

        self._bin_size_slider = Widgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        # Range and bin size in [um].
        self._bin_size_slider.setRange(1, 20)
        self._bin_size_line_edit = Widgets.QLineEdit()

        self._replot_timer = QtCore.QTimer()
        # Wait 500 milliseconds until replotting in order to avoid plotting for fast changes of
        # the slider.
        self._replot_timer.setInterval(500)

        self._bin_size_slider.valueChanged.connect(
            lambda x: self._bin_size_line_edit.setText(
                '%d um' % (x * self.bin_size_slider_multiplier)
            )
        )
        self._bin_size_slider.valueChanged.connect(lambda x: self._replot_timer.start())
        self._bin_size_slider.setEnabled(False)
        self._bin_size_line_edit.setText(
            '%d um' % (self._bin_size_slider.value() * self.bin_size_slider_multiplier)
        )

        self._replot_timer.timeout.connect(self.replot)

        self._figure = plt.figure()
        self._axes = self._figure.add_subplot(111)
        self._canvas = FigureCanvas(self._figure)

        layout = Widgets.QVBoxLayout()
        h_layout = Widgets.QHBoxLayout()
        h_layout.addWidget(Widgets.QLabel('<b>Profiles</b>'))
        h_layout.addStretch(1)
        layout.addLayout(h_layout)
        h_layout = Widgets.QHBoxLayout()
        h_layout.addWidget(Widgets.QLabel('Bin size:'))
        h_layout.addWidget(self._bin_size_line_edit)
        h_layout.addWidget(self._bin_size_slider, stretch=1)
        layout.addLayout(h_layout)
        layout.addWidget(self._canvas, stretch=1)
        self.setLayout(layout)

    @property
    def data_frame(self):
        return self._df

    @data_frame.setter
    def data_frame(self, df):
        self._df = df
        self._bin_size_slider.setEnabled(True)
        self.replot(self._bin_size_slider.value())

    def replot(self, *args):
        self._reset_figure()
        self._plot_profile(BasicRecorder.possible_column_names['initial x'])
        self._plot_profile(BasicRecorder.possible_column_names['final x'])
        self._axes.set_xlabel('x [mm]')
        self._axes.set_ylabel('[a.u.]')
        self._axes.legend()
        self._canvas.draw()

    def _plot_profile(self, column_name):
        try:
            centers, bins = self._generate_histogram(self._df[column_name])
        except KeyError:
            pass
        else:
            self._axes.plot(centers, bins, label=column_name.split()[0])

    def _generate_histogram(self, samples):
        samples = np.array(samples) * 1.0e3  # [m] -> [mm]
        bin_size = (
            self._bin_size_slider.value() * self.bin_size_slider_multiplier
            * 1.0e-3  # [um] -> [mm]
        )
        n_bins = int((np.max(samples) - np.min(samples)) / bin_size)
        bins, edges = np.histogram(samples, bins=n_bins)
        centers = edges[:-1] + (edges[1] - edges[0]) / 2.
        return centers, bins

    def _reset_figure(self):
        self._figure.clear()
        self._axes = self._figure.add_subplot(111)
        self._canvas.draw()


class ScatterPlot(Widgets.QWidget):
    distribution_options_spatial_3d = {
        'x_scaling_factor': 1.0e3,
        'y_scaling_factor': 1.0e3,
        'z_scaling_factor': 1.0e3,
        'x_label': 'x [mm]',
        'y_label': 'y [mm]',
        'z_label': 'z [mm]',
    }
    distribution_options_spatial_2d = {
        'x_scaling_factor': 1.0e3,
        'y_scaling_factor': 1.0e3,
        'x_label': '{0} [mm]',
        'y_label': '{0} [mm]',
    }
    distribution_options_time_and_spatial_2d = {
        'x_scaling_factor': 1,
        'y_scaling_factor': 1.0e3,
        'x_label': 'simulation step',
        'y_label': '{0} [mm]',
    }

    distributions = {
        '3d': {
            'column-names': ['{0} x', '{0} y', '{0} z'],
            'options': distribution_options_spatial_3d
        },
        'xy-plane': {
            'column-names': ['{0} x', '{0} y'],
            'options': distribution_options_spatial_2d
        },
        'xz-plane': {
            'column-names': ['{0} x', '{0} z'],
            'options': distribution_options_spatial_2d
        },
        'yz-plane': {
            'column-names': ['{0} y', '{0} z'],
            'options': distribution_options_spatial_2d
        },
        'tx-distribution': {
            'column-names': ['{0} sim. step', '{0} x'],
            'options': distribution_options_time_and_spatial_2d
        },
        'ty-distribution': {
            'column-names': ['{0} sim. step', '{0} y'],
            'options': distribution_options_time_and_spatial_2d
        },
    }

    scatter_plot_marker_size = 1

    def __init__(self, stage, df=None, parent=None):
        super().__init__(parent=parent, flags=QtCore.Qt.WindowType.Widget)

        self._df = df
        if stage not in ('initial', 'final'):
            raise ValueError('Invalid value for stage: %s' % stage)
        self._stage = stage

        self._figure_3d = plt.figure()
        self._axes_3d = self._figure_3d.add_subplot(111, projection='3d')
        self._canvas_3d = FigureCanvas(self._figure_3d)

        self._figure_2d = plt.figure()
        self._axes_2d = self._figure_2d.add_subplot(111)
        self._canvas_2d = FigureCanvas(self._figure_2d)

        self._plot_selector = Widgets.QComboBox()

        self._plot_stack = Widgets.QStackedWidget()
        self._plot_stack.addWidget(self._canvas_3d)
        self._plot_stack.addWidget(self._canvas_2d)

        for distribution in sorted(self.distributions, reverse=True):
            self._plot_selector.addItem(distribution)

        self._plot_selector.currentIndexChanged.connect(self.plot)
        self._plot_selector.setEnabled(False)

        v_layout = Widgets.QVBoxLayout()
        h_layout = Widgets.QHBoxLayout()
        h_layout.addWidget(self._plot_selector)
        h_layout.addWidget(Widgets.QLabel(
            '<b>{0} particle distribution</b>'.format(self._stage.capitalize())
        ))
        h_layout.addStretch(1)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self._plot_stack)
        self.setLayout(v_layout)

    @property
    def data_frame(self):
        return self._df

    @data_frame.setter
    def data_frame(self, df):
        self._df = df
        self._plot_selector.setEnabled(True)
        self.plot(self._plot_selector.currentIndex())

    def plot(self, index):
        if self._df is None:
            return
        distribution = self._plot_selector.itemText(index)
        column_names = list(map(
            lambda x: BasicRecorder.possible_column_names[x.format(self._stage)],
            self.distributions[distribution]['column-names']
        ))
        options = self.distributions[distribution]['options'].copy()
        if len(column_names) == 3:
            self.plot_3d(*column_names, **options)
        else:
            plane = re.match(r'([a-z]{2})-(plane|distribution)', distribution).groups()[0]
            options['x_label'] = options['x_label'].format(plane[0])
            options['y_label'] = options['y_label'].format(plane[1])
            self.plot_2d(*column_names, **options)

    def plot_3d(self, x_name, y_name, z_name, x_label=None, y_label=None, z_label=None,
                x_scaling_factor=1.0, y_scaling_factor=1.0, z_scaling_factor=1.0):
        self._reset_3d_figure()
        self._plot_stack.setCurrentWidget(self._canvas_3d)
        try:
            xs = self._df[x_name.format(self._stage)] * x_scaling_factor
            ys = self._df[y_name.format(self._stage)] * y_scaling_factor
            zs = self._df[z_name.format(self._stage)] * z_scaling_factor
        except KeyError as err:
            Widgets.QMessageBox.information(
                self,
                'Incomplete data',
                'The plot could not be created because column "%s" is missing in the data file.'
                % str(err)
            )
            return
        self._axes_3d.scatter(xs, ys, zs, s=self.scatter_plot_marker_size)
        self._axes_3d.set_xlabel(x_label or x_name)
        self._axes_3d.set_ylabel(y_label or y_name)
        self._axes_3d.set_zlabel(z_label or z_name)
        self._canvas_3d.draw()

    def plot_2d(self, x_name, y_name, x_label=None, y_label=None, x_scaling_factor=1.0,
                y_scaling_factor=1.0):
        self._reset_2d_figure()
        self._plot_stack.setCurrentWidget(self._canvas_2d)
        try:
            xs = self._df[x_name.format(self._stage)] * x_scaling_factor
            ys = self._df[y_name.format(self._stage)] * y_scaling_factor
        except KeyError as err:
            Widgets.QMessageBox.information(
                self,
                'Incomplete data',
                'The plot could not be created because column "%s" is missing in the data file.'
                % str(err)
            )
            return
        self._axes_2d.scatter(xs, ys, s=self.scatter_plot_marker_size)
        self._axes_2d.set_xlabel(x_label or x_name)
        self._axes_2d.set_ylabel(y_label or y_name)
        self._canvas_2d.draw()

    def _reset_3d_figure(self):
        self._figure_3d.clear()
        self._axes_3d = self._figure_3d.add_subplot(111, projection='3d')
        self._canvas_3d.draw()

    def _reset_2d_figure(self):
        self._figure_2d.clear()
        self._axes_2d = self._figure_2d.add_subplot(111)
        self._canvas_2d.draw()
