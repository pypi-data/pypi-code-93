"""
This file is part of APAV.

APAV is a python package for performing analysis and visualization on
atom probe tomography data sets.

Copyright (C) 2018 Jesse Smith

APAV is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

APAV is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with APAV.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import os

import numpy as n
import pyqtgraph as pg
from copy import copy

from apav.vtkall import *
from apav.qt import *
from apav.visualization.base import BaseVisualization#, VTKVisualization
from apav.qtwidgets.massrangewidget import QMassRangeWidget
from apav.core import histogram
from apav.visualization.vtkhelpers import point_cloud, point_dataset
from apav.utils.helpers import modifying
import apav.qtwidgets.controls as controls

pg.setConfigOption("foreground", "k")
pg.setConfigOption("background", "w")
pg.setConfigOption("antialias", True)


class Plotter1D(pg.PlotWidget):
    """
    Base 1D plotter settings
    """
    def __init__(self, parent: QWidget, xlabel: str, ylabel: str, xunits: str = "", yunits: str = ""):
        super().__init__(parent)
        self.getPlotItem().showAxis("right")
        self.getPlotItem().showAxis("top")
        self.setLabel("left", ylabel, units=yunits)
        self.setLabel("bottom", xlabel, units=xunits)
        right = self.getPlotItem().getAxis("right")
        top = self.getPlotItem().getAxis("top")
        self.getPlotItem().showAxis("top")
        right.setStyle(showValues=False)
        top.setStyle(showValues=False)


class MassSpectrumPlot(BaseVisualization):
    def __init__(self, roi):
        super().__init__(roi)
        self.resize(900, 600)
        self.setWindowTitle("Mass histogram - {}".format(os.path.basename(self.ref_data.filepath)))

        self.widget = QWidget(self)
        self.toplayout = QVBoxLayout()
        self.widget.setLayout(self.toplayout)
        self.setCentralWidget(self.widget)
        self.status = self.statusBar()

        self.plot_layout = QHBoxLayout()
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_layout.setSpacing(0)
        self.toplayout.addLayout(self.plot_layout)
        self.plotter = Plotter1D(self, "Mass/charge ratio", "Counts", xunits="Da")

        self.plot_layout.addWidget(self.plotter)

        self.prox = pg.SignalProxy(self.plotter.getPlotItem().scene().sigMouseMoved, rateLimit=30,
                                   slot=self.slotOnMouseMoved)

        self.data = None
        self.makeToolBar()
        self._recalculateHistogram()

    def setupToolBarActions(self):
        super().setupToolBarActions()
        tb = self.toolbar_actions

        # Bin value
        tb.append(QLabel("Bin width: "))
        self.bin_width = QDoubleSpinBox(self)
        self.bin_width.setDecimals(3)
        self.bin_width.setMinimum(0.001)
        self.bin_width.setMaximum(100)
        self.bin_width.setSingleStep(0.01)
        self.bin_width.setValue(0.05)
        self.bin_width.setSuffix(" Da")
        self.bin_width.editingFinished.connect(self._recalculateHistogram)
        tb.append(self.bin_width)
        tb.append(None)

        # lower value
        tb.append(QLabel("Lower: "))
        self.lower = QDoubleSpinBox(self)
        self.lower.setMinimum(0)
        self.lower.setMaximum(10000)
        self.lower.setValue(0)
        self.lower.setSuffix(" Da")
        # self.lower.editingFinished.connect(self._recalculateHistogram)
        self.lower.editingFinished.connect(self._recalculateHistogram)
        tb.append(self.lower)
        tb.append(None)

        # upper value
        tb.append(QLabel("Upper: "))
        self.upper = QDoubleSpinBox(self)
        self.upper.setMinimum(0)
        self.upper.setMaximum(10000)
        self.upper.setValue(200)
        self.upper.setSuffix(" Da")
        self.upper.editingFinished.connect(self._recalculateHistogram)
        tb.append(self.upper)
        tb.append(None)

        # Multiplicity
        tb.append(QLabel("Multiplicity: "))
        self.multiplicity = controls.QAnyMultiplicityComboBox(self, self.ref_data)
        self.multiplicity.currentIndexChanged.connect(self._recalculateHistogram)
        tb.append(self.multiplicity)
        tb.append(None)

        # Normalize
        self.norm = QCheckBox(self)
        self.norm.setText("Normalize:")
        self.norm.setLayoutDirection(Qt.RightToLeft)
        self.norm.setChecked(False)
        self.norm.stateChanged.connect(self._recalculateHistogram)
        tb.append(self.norm)

    def _recalculateHistogram(self):
        line = pg.mkPen(color=(0, 0, 0), width=1)
        bin_width = self.bin_width.value()

        mult = self.multiplicity.formattedValue()

        low = self.lower.value()
        up = self.upper.value()

        if low >= up:
            self.plotter.getPlotItem().clear()
            return

        self.data = self.ref_data.mass_histogram(bin_width=bin_width,
                                                 multiplicity=mult,
                                                 norm=self.norm.isChecked(),
                                                 lower=self.lower.value(),
                                                 upper=self.upper.value())

        # x = self.data[0] - bin_width/2
        # x = n.hstack((x, x[-1] + bin_width))
        self.plotter.getPlotItem().plot(self.data[0], self.data[1], stepMode="left", clear=True, pen=line)

    def slotOnMouseMoved(self, event):
        pos = self.plotter.getPlotItem().getViewBox().mapSceneToView(event[0])

        x, y = pos.x(), pos.y()
        idx = int((x - self.lower.value())/self.bin_width.value())
        try:
            y = self.data[1][idx]
        except IndexError:
            y = 0
        finally:
            if idx < 0:
                y = 0
        self.statusBar().showMessage("x = {}, y = {:d}".format(round(x, 4), int(y)))

    def exportRawData(self):
        path, filter = QFileDialog.getSaveFileName(self, "Export to raw data", "~/", filter="*.csv")
        if not path:
            return

        dat = self.data[0][None].T
        dat = n.hstack((dat, self.data[1][None].T))
        n.savetxt(path, dat, delimiter=",")


class MassSpectrumPlotRanged(BaseVisualization):
    def __init__(self, ranged_mass_spec):
        self.rmass = ranged_mass_spec
        super().__init__(ranged_mass_spec.roi)
        self.resize(1200, 600)
        self.setWindowTitle("Ranged mass histogram - {}".format(os.path.basename(self.ref_data.filepath)))

        self.widget = QWidget(self)
        self.toplayout = QVBoxLayout()
        self.widget.setLayout(self.toplayout)
        self.setCentralWidget(self.widget)
        self.status = self.statusBar()

        self.plot_layout = QHBoxLayout()
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_layout.setSpacing(0)
        self.toplayout.addLayout(self.plot_layout)
        self.plotter = Plotter1D(self, "Mass/charge ratio", "Counts", xunits="Da")

        self.plot_layout.addWidget(self.plotter)

        self.prox = pg.SignalProxy(self.plotter.getPlotItem().scene().sigMouseMoved, rateLimit=30,
                                   slot=self.slotOnMouseMoved)

        self.makeToolBar()

        self.data = self.rmass.histogram

        # Draw colored ranges
        for rng in self.rmass.ranges:
            idx = n.argwhere((self.data[0] >= rng.lower) & (self.data[0] <= rng.upper))[:, 0]
            rngx = histogram.centers2edges(self.data[0][idx], self.rmass.bin_width)
            fill = QBrush(QColor.fromRgbF(*rng.color))
            self.plotter.getPlotItem().plot(rngx, self.data[1][idx], stepMode="center", brush=fill, fillLevel=0, pen=None)

        # Draw line spectrum
        self.centers = histogram.centers2edges(self.data[0], self.rmass.bin_width)
        line = pg.mkPen(color=(0, 0, 0), width=1)
        self.mass_spectrum_item = self.plotter.getPlotItem().plot(self.centers, self.data[1], stepMode="center", pen=line)

        # Range viewer
        range_dock = QDockWidget("Mass ranges", self)
        range_dock.setContentsMargins(0, 0, 0, 0)
        range_dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        range_widget = QMassRangeWidget(self, self.rmass.ranges)
        range_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        range_dock.setWidget(range_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, range_dock)

        range_widget.sigRangeDoubleClicked.connect(self.onRangeSelected)

    def onRangeSelected(self, rng):
        xmin = rng.lower
        xmax = rng.upper
        xstride = xmax - xmin
        idx = n.argwhere((self.data[0] >= xmin) & (self.data[0] <= xmax))
        ymax = self.data[1][idx].upper()
        ymin = self.data[1][idx].lower()
        ystride = ymax - ymin

        # Pad the x, y extents
        xmin -= 0.1*xstride
        xmax += 0.1*xstride
        ymin -= 0.1*ystride
        ymax += 0.1*ystride

        # Don't let ymin be zero in case the plot is int log scale
        if ymin < 1:
            ymin = 1

        self.plotter.setXRange(xmin, xmax)
        self.plotter.setYRange(ymin, ymax)

    def setupToolBarActions(self):
        super().setupToolBarActions()
        tb = self.toolbar_actions

        # Cutoff value
        tb.append(QLabel("Bin width: "))
        self.bin_width = QLineEdit(self)
        self.bin_width.setText(str(self.rmass.bin_width) + " Da")
        self.bin_width.setReadOnly(True)
        self.bin_width.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        tb.append(self.bin_width)
        tb.append(None)

        # upper value
        tb.append(QLabel("Upper: "))
        self.upper = QLineEdit(self)
        self.upper.setText(str(self.rmass.upper) + " Da")
        self.upper.setReadOnly(True)
        self.upper.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        tb.append(self.upper)
        tb.append(None)

        # Multiplicity
        tb.append(QLabel("Multiplicity: "))
        self.multiplicity = QLineEdit(self)
        mult = self.rmass.multiplicity
        if mult == "all":
            text = "All"
        elif mult == "multiples":
            text = "All multiples"
        elif isinstance(mult, int):
            text = str(mult)
        else:
            raise ValueError("Unknown multiplicity value")
        self.multiplicity.setText(text)
        self.multiplicity.setReadOnly(True)
        self.multiplicity.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        tb.append(self.multiplicity)
        tb.append(None)

    def slotOnMouseMoved(self, event):
        pos = self.plotter.getPlotItem().getViewBox().mapSceneToView(event[0])

        x, y = pos.x(), pos.y()
        idx = int(x/self.rmass.bin_width)
        try:
            counts = self.data[1][idx]
        except IndexError:
            counts = 0
        finally:
            if idx < 0:
                counts = 0

        comp = ""
        if x > 0:
            for rng in self.rmass.ranges:
                if x in rng:
                    if 0 <= y <= counts:
                        comp = rng.hill_formula

        txt = "x = {}, y = {}".format(round(x, 2), round(counts, 2))
        if comp != "":
            txt += f" - {comp}"
        self.statusBar().showMessage(txt)

    def exportRawData(self):
        path, filter = QFileDialog.getSaveFileName(self, "Export to raw data", "~/", filter="*.csv")
        if not path:
            return

        dat = self.data[0][None].T
        dat = n.hstack((dat, self.data[1][None].T))
        n.savetxt(path, dat, delimiter=",")


class MassSpectrumPlotNoiseCorrected(MassSpectrumPlotRanged):
    def __init__(self, noise_corr_mass):
        super().__init__(noise_corr_mass)
        self.nmass = noise_corr_mass

        self.setWindowTitle("Noise corrected mass histogram - {}".format(os.path.basename(self.ref_data.filepath)))

        line = pg.mkPen(color=(255, 0, 255), width=1)
        bkg_min = self.nmass.noise_background.lower
        x = self.nmass.noise_fit_data[0]
        idx = n.argmin(n.abs(x-bkg_min))
        # print(bkg_min, idx)
        self.noise_fit_item = self.plotter.getPlotItem().plot(self.nmass.noise_fit_data[0][idx:],
                                                              self.nmass.noise_fit_data[1][idx:],
                                                              pen=line)

        self.legend = pg.LegendItem(offset=(-20, 10))
        self.legend.setParentItem(self.plotter.getPlotItem())
        self.legend.addItem(self.mass_spectrum_item, "Uncorrected mass spectrum")
        self.legend.addItem(self.noise_fit_item, f"Background noise fit")# ({self.nmass.noise_background.eval_func.descr})")


class MassSpectrumPlotLocalBkgCorrected(MassSpectrumPlotNoiseCorrected):
    def __init__(self, local_bkg_mass):
        super().__init__(local_bkg_mass)
        self.lmass = local_bkg_mass
        self.setWindowTitle("Local background corrected mass histogram - {}".format(os.path.basename(self.ref_data.filepath)))

        for bkg in self.lmass.background_collection:
            lower_idx = int(min(i[0] for i in bkg.fit_intervals)/self.lmass.bin_width)
            # upper_idx = int(max(i[1] for i in bkg.include_intervals)/self.lmass.bin_width)
            x = self.lmass.histogram[0][lower_idx:]
            noise_y = self.lmass.noise_background.eval(x)
            sig_y = bkg.eval(x)
            self.plotter.getPlotItem().plot(x, sig_y + noise_y, pen=(0, 0, 0))


class InteractiveCorrelationHistogramPlot(BaseVisualization):
    def __init__(self, corr_hist):
        super().__init__(copy(corr_hist))
        self.resize(700, 500)
        self.setWindowTitle("Correlation Histogram - {}".format(os.path.basename(corr_hist.roi.filepath)))
        self.setMouseTracking(True)

        self.status = self.statusBar()

        self.widget = QWidget(self)
        self.toplayout = QVBoxLayout()
        self.widget.setLayout(self.toplayout)
        self.setCentralWidget(self.widget)
        self.dock = QDockWidget("Options", self)
        self.dock.setMinimumWidth(250)
        self.dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.makeDock()

        # Setup data
        self.img = None
        self.colorbar = None
        self.plotter = None
        self.data = None
        self.proxy = None

        self.plot_layout = QHBoxLayout()
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_layout.setSpacing(0)
        self.toplayout.addLayout(self.plot_layout)

        self._recalculateHistogram(self.ref_data)

        self.makeToolBar()

    def slotOnMouseMoved(self, event):
        pos = self.plotter.getPlotItem().getViewBox().mapSceneToView(event[0])
        bin = self.ref_data.bin_width
        xrng, yrng = self.ref_data.extents
        ysize = self.data.shape[1]

        x, y = pos.x(), pos.y()
        idx = int((x - xrng[0])/bin)
        idy = int((y - yrng[0])/bin)
        try:
            z = self.data[idx, idy]
        except:
            z = 0
        self.statusBar().showMessage("x = {}, y = {}, z = {}".format(round(x, 2), round(y, 2), int(z)))

    def makeDock(self):
        dockwidget = QWidget(self)
        layout = QVBoxLayout(self.dock)
        dockwidget.setLayout(layout)
        self.dock.setWidget(dockwidget)
        extents = self.ref_data.extents

        bin_group = QGroupBox(self)
        bin_group.setTitle("Bins")
        bin_layout = QFormLayout(self)
        bin_group.setLayout(bin_layout)

        # Bin value
        self.binwidth = controls.QDecimalSpinBox(self)
        self.binwidth.setMinimum(0.001)
        self.binwidth.setMaximum(10)
        self.binwidth.setSingleStep(0.01)
        self.binwidth.setDecimals(3)
        self.binwidth.setValue(self.ref_data.bin_width)
        self.binwidth.setSuffix(" Da")
        self.binwidth.editingFinishedAndChanged.connect(self._recalculateHistogram)
        bin_layout.addRow(QLabel("Width: "), self.binwidth)
        layout.addWidget(bin_group)

        ext_group = QGroupBox(self)
        ext_group.setTitle("Histogram boundaries")
        ext_layout = QFormLayout(self)
        ext_group.setLayout(ext_layout)

        # Ion 1 lower value
        self.lower1 = controls.QDecimalSpinBox(self)
        self.lower1.setMinimum(0)
        self.lower1.setMaximum(1000)
        self.lower1.setValue(extents[0][0])
        self.lower1.setSuffix(" Da")
        self.lower1.editingFinishedAndChanged.connect(self._recalculateHistogram)
        ext_layout.addRow(QLabel("Ion1 lower:"), self.lower1)

        # Ion 1 upper value
        self.upper1 = controls.QDecimalSpinBox(self)
        self.upper1.setMinimum(1)
        self.upper1.setMaximum(1000)
        self.upper1.setValue(extents[0][1])
        self.upper1.setSuffix(" Da")
        self.upper1.editingFinishedAndChanged.connect(self._recalculateHistogram)
        ext_layout.addRow(QLabel("Ion1 upper:"), self.upper1)

        # Ion 2 lower value
        self.lower2 = controls.QDecimalSpinBox(self)
        self.lower2.setMinimum(0)
        self.lower2.setMaximum(1000)
        self.lower2.setValue(extents[1][0])
        self.lower2.setSuffix(" Da")
        self.lower2.editingFinishedAndChanged.connect(self._recalculateHistogram)
        ext_layout.addRow(QLabel("Ion2 lower:"), self.lower2)

        # Ion 2 upper value
        self.upper2 = controls.QDecimalSpinBox(self)
        self.upper2.setMinimum(1)
        self.upper2.setMaximum(1000)
        self.upper2.setValue(extents[1][1])
        self.upper2.setSuffix(" Da")
        self.upper2.editingFinishedAndChanged.connect(self._recalculateHistogram)
        ext_layout.addRow(QLabel("Ion2 upper:"), self.upper2)
        layout.addWidget(ext_group)

        # Multiplicity
        mult_group = QGroupBox(self)
        mult_group.setTitle("Multiple events")
        mult_layout = QFormLayout(self)
        mult_group.setLayout(mult_layout)

        self.multiplicity = controls.QMultiplesMultiplicityComboBox(self, self.ref_data.roi)
        idx = self.multiplicity.findText(str(self.ref_data.multiplicity))
        self.multiplicity.setCurrentIndex(idx)
        self.multiplicity.currentIndexChanged.connect(self._recalculateHistogram)
        mult_layout.addRow("Multiplicity:", self.multiplicity)
        layout.addWidget(mult_group)

        view_group = QGroupBox(self)
        view_group.setTitle("Appearance")
        view_layout = QFormLayout(self)
        view_group.setLayout(view_layout)

        # log
        self.log_edit = QCheckBox(self)
        self.log_edit.setLayoutDirection(Qt.RightToLeft)
        self.log_edit.setChecked(False)
        self.log_edit.stateChanged.connect(self._recalculateHistogram)
        view_layout.addRow("Log:", self.log_edit)

        # Symmetric
        self.symmetric = QCheckBox(self)
        self.symmetric.setLayoutDirection(Qt.RightToLeft)
        self.symmetric.setChecked(self.ref_data.symmetric)
        self.symmetric.stateChanged.connect(self._recalculateHistogram)
        view_layout.addRow("Symmetric:", self.symmetric)

        # flip
        self.flip = QCheckBox(self)
        self.flip.setLayoutDirection(Qt.RightToLeft)
        self.flip.setChecked(self.ref_data.symmetric)
        self.flip.stateChanged.connect(self._recalculateHistogram)
        view_layout.addRow("Flipped:", self.flip)
        layout.addWidget(view_group)
        layout.addStretch()

    def exportRawData(self):
        xrng, yrng = self.ref_data.extents
        head = f"ion1({xrng[0]}-{xrng[1]}) ion2({yrng[0]}-{yrng[1]}) bin({self.ref_data.bin_width})"
        path, filter = QFileDialog.getSaveFileName(self, "Export to raw data", f"~/{head}.csv", filter="*.csv")
        if not path:
            return
        self.ref_data.export(path)

    def _recalculateHistogram(self, corr_hist=None):
        """
        Recalculate the histogram. This should not modify the original CorrelationHistogram as it is copied in
        the constructor

        :param corr_hist: an existing CorrelationHistogram, used for initial plot
        """
        if self.lower1.value() >= self.upper1.value():
            return
        elif self.lower2.value() >= self.upper2.value():
            return

        if corr_hist is not None:
            with modifying(self.ref_data) as ref_data:
                multiplicity = self.multiplicity.formattedValue()

                ref_data.multiplicity = multiplicity
                ref_data.extents = ((self.lower1.value(), self.upper1.value()),
                                    (self.lower2.value(), self.upper2.value()))
                ref_data.flip = self.flip.isChecked()
                ref_data.symmetric = self.symmetric.isChecked()
                ref_data.bin_width = self.binwidth.value()

        if self.colorbar:
            self.plot_layout.removeWidget(self.colorbar)
        if self.plotter:
            self.plot_layout.removeWidget(self.plotter)

        self.plotter = pg.PlotWidget(self)
        self.plotter.getPlotItem().showAxis("right")
        self.plotter.getPlotItem().showAxis("top")

        self.data = ref_data.histogram.copy()
        xrng, yrng = ref_data.extents
        non_zero = n.where(self.data > 0)
        binw = ref_data.bin_width
        plot_data = self.data

        if self.log_edit.isChecked():
            data_log = self.data.copy()
            data_log[non_zero] = n.log(self.data[non_zero])
            plot_data = data_log

        if self.ref_data.flip is False:
            xlabel = "Ion 1 mass/charge"
            ylabel = "Ion 2 mass/charge"
        else:
            xlabel = "Ion 2 mass/charge"
            ylabel = "Ion 1 mass/charge"

        self.plotter.setLabel("left", ylabel, units="Da")
        self.plotter.setLabel("bottom", xlabel, units="Da")
        right = self.plotter.getPlotItem().getAxis("right")
        top = self.plotter.getPlotItem().getAxis("top")
        self.plotter.getPlotItem().showAxis("top")
        right.setStyle(showValues=False)
        top.setStyle(showValues=False)
        self.plotter.plotItem.getViewBox().setAspectLocked(True)
        self.img = pg.ImageItem()

        self.plotter.addItem(self.img)

        self.img.setImage(plot_data)
        self.img.translate(xrng[0], yrng[0])
        self.img.scale(binw, binw)
        if self.colorbar is None:
            self.colorbar = pg.HistogramLUTWidget(self, self.img)
        else:
            self.colorbar.setImageItem(self.img)
        self.plot_layout.insertWidget(0, self.plotter)
        self.plot_layout.addWidget(self.colorbar)

        self.prox = pg.SignalProxy(self.plotter.getPlotItem().scene().sigMouseMoved,
                                   rateLimit=30,
                                   slot=self.slotOnMouseMoved)


# class DetectorDeadZonePlot(VTKVisualization):
#     def __init__(self, dead_zone):
#         super().__init__()
#         self.dead_zone = dead_zone
#
#         # roi = self.dead_zone.roi
#         # idx = self.dead_zone.idx
#         # detx = roi.misc["det_x"][idx]
#         # dety = roi.misc["det_y"][idx]
#         # dx = detx[1::2] - detx[::2]
#         # dy = dety[1::2] - dety[::2]
#         # dt = dead_zone.tof_diff*0.1
#         dx = dead_zone.dx
#         dy = dead_zone.dy
#         dt = dead_zone.tof_diff
#         poly = point_cloud(n.array([dx, dy, dt]).T)
#         points = point_dataset(poly, 4)
#         self.viewport.register_actors(points)
#         # points.SetScale(1, 1, 0.25)
#
#         cube = vtkCubeAxesActor()
#         cube.SetXAxisRange(dx.lower(), dx.upper())
#         cube.SetYAxisRange(dy.lower(), dy.upper())
#         cube.SetZAxisRange(dt.lower(), dt.upper())
#         cube.SetBounds(dx.lower(), dx.upper(), dy.lower(), dy.upper(), dt.lower(), dt.upper())
#
#         cube.GetXAxesLinesProperty().SetColor(0, 0, 0)
#         cube.GetXAxesGridlinesProperty().SetColor(0, 0, 0)
#         cube.GetYAxesLinesProperty().SetColor(0, 0, 0)
#         cube.GetZAxesLinesProperty().SetColor(0, 0, 0)
#         cube.GetTitleTextProperty(0).SetColor(0,0,0)
#         cube.GetLabelTextProperty(0).SetColor(0,0,0)
#         cube.GetTitleTextProperty(1).SetColor(0,0,0)
#         cube.GetLabelTextProperty(1).SetColor(0,0,0)
#         cube.GetTitleTextProperty(2).SetColor(0,0,0)
#         cube.GetLabelTextProperty(2).SetColor(0,0,0)
#
#         self.viewport.register_actors(cube)
#
#
#         # view = vtkContextView()
#
#
#         # chart = vtkChartXYZ()
#         # view.GetScene().AddItem(chart)
#         # plot = vtkPlotPoints3D()
#         # table = vtkTable()
#         # xary, yary, tofary = vtkFloatArray(), vtkFloatArray(), vtkFloatArray()
#         # xary.SetName("Delta x (mm)")
#         # yary.SetName("Delta y (mm)")
#         # tofary.SetName("Delta TOF (ns)")
#         # table.AddColumn(xary)
#         # table.AddColumn(yary)
#         # table.AddColumn(tofary)
#         # table.SetNumberOfRows(dx.size)
#         # for i, item in enumerate(zip(dx, dy, dead_zone.tof_diff)):
#         #     x, y, z = item
#         #     table.SetValue(i, 0, vtkVariant(float(x)))
#         #     table.SetValue(i, 1, vtkVariant(float(y)))
#         #     table.SetValue(i, 2, vtkVariant(float(z)))
#         #
#         # plot.SetInputData(table)
#         # chart.AddPlot(plot)
#         # self.viewport._ren
#         # view.SetRenderWindow(self.viewport._renwin)
#         # b = vtkMapper()
#         # b.SetInputConnection(chart)
#         # a = vtkOpenGLContextActor()
#         # self.viewport.register_actors(chart)




