# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""
contains gui relative to axis calculation using sinogram
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "14/10/2019"


from silx.gui import qt
from tomwer.core.process.reconstruction.axis.params import AxisCalculationInput
from tomwer.core.process.reconstruction.axis.mode import AxisMode
from tomwer.gui.utils.buttons import PadlockButton
from tomwer.synctools.axis import QAxisRP
from tomwer.core.scan.scanbase import TomwerScanBase
from silx.gui.plot import Plot2D
import logging

_logger = logging.getLogger(__file__)


class SinogramAxisWindow(qt.QMainWindow):
    """
    Main window for axis calculation from sinogram
    """

    sigReadyForComputation = qt.Signal()
    """signal emitted when a computation is requested"""

    sigApply = qt.Signal()
    """signal emitted when the axis reconstruction parameters are validated"""

    sigAxisEditionLocked = qt.Signal(bool)
    """Signal emitted when the status of the reconstruction parameters edition
    change"""

    sigSinoLoadStarted = qt.Signal()
    """Signal emitted when some computation is started. For this widget
    some computation can be time consuming when creating the sinogram"""
    sigSinoLoadEnded = qt.Signal()
    """Signal emitted when a computation is ended"""

    sigLockModeChanged = qt.Signal(bool)
    """signal emitted when the lock on the mode change"""

    _MARKER_NAME = "cor"
    _MARKER_COLOR = "#ebc634"

    def __init__(self, axis, parent=None):
        qt.QMainWindow.__init__(self, parent)
        self._scan = None
        if isinstance(axis, QAxisRP):
            self._axis_params = axis
        else:
            raise TypeError("axis should be an instance of QAxisRP")

        self._plot = Plot2D(parent=self)
        self._plot.getDefaultColormap().setVRange(None, None)
        self._plot.setAxesDisplayed(False)
        self._dockOpt = qt.QDockWidget(parent=self)
        self._options = _SinogramOpts(parent=self, axis_params=axis)
        self._dockOpt.setWidget(self._options)

        self.setCentralWidget(self._plot)
        self._dockOpt.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._dockOpt)

        # prepare processing
        self._loadingThread = _LoadSinoThread()

        # expose API
        self.isModeLock = self._options.isModeLock
        self._lockModeChanged = self._options._lockModeChanged

        # connect signal / slot
        self._options.sigComputationRequested.connect(self._computationRequested)
        self._options.sigAxisEditionLocked.connect(self._editionLocked)
        self._options.sigApply.connect(self._applyRequested)
        self._options.sigLockModeChanged.connect(self._expandSigLockModeChanged)
        # self._options.sigPositionChanged.connect(self._updateCORMarker)
        self._loadingThread.finished.connect(self._sinogram_loaded)

    def _expandSigLockModeChanged(self, lock):
        self.sigLockModeChanged.emit(lock)

    def setReconsParams(self, axis):
        self._axis_params = axis
        # TODO: update according to axis paramters

    def setScan(self, scan):
        self._scan = scan
        self._options.setScan(self._scan)

    def getPlot(self):
        return self._plot

    def getSettingsWidget(self):
        return self._options

    def _updatePlot(self, sinogram):
        self._plot.addImage(data=sinogram)
        self._plot.replot()

    def _computationRequested(self):
        # first load the sinogram to display it
        if self._loadingThread.isRunning():
            _logger.warning(
                "a center of rotation is already into processing,"
                "please wait until it ends"
            )
            return

        if self._scan is None:
            return

        # update scan
        self._scan.axis_params.use_sinogram = True
        self._axis_params.sinogram_line = self._options.getRadioLine()
        self._axis_params.sinogram_subsampling = self._options.getSubsampling()
        self._axis_params.calculation_input_type = (
            self._options.getCalulationInputType()
        )
        self._scan.axis_params.sinogram_line = self._axis_params.sinogram_line
        self._scan.axis_params.sinogram_subsampling = (
            self._axis_params.sinogram_subsampling
        )
        self._scan.axis_params.calculation_input_type = (
            self._axis_params.calculation_input_type
        )
        self._options.setEnabled(False)
        self.sigSinoLoadStarted.emit()
        self._loadingThread.init(
            scan=self._scan,
            line=self._options.getRadioLine(),
            subsampling=int(self._options.getSubsampling()),
        )
        self._loadingThread.start()

    def _editionLocked(self, locked):
        self.sigAxisEditionLocked.emit(locked)

    def _applyRequested(self):
        self.sigApply.emit()

    def _sinogram_loaded(self):
        """callback when the sinogram is loaded"""
        # note: cache avoid reading data twice here.
        sinogram = self._scan.get_sinogram(
            line=self._scan.axis_params.sinogram_line,
            subsampling=self._scan.axis_params.sinogram_subsampling,
        )
        self._updatePlot(sinogram=sinogram)
        self.sigSinoLoadEnded.emit()
        self.sigReadyForComputation.emit()
        self._options.setEnabled(True)

    def setLocked(self, locked):
        if self._axis_params.mode not in (AxisMode.manual, AxisMode.read):
            self._axis_params.mode = AxisMode.manual
        self._options.setLocked(locked)

    def _setModeLockFrmSettings(self, lock):
        self._options.setLocked(lock)

    def _validated(self):
        """callback when the validate button is activated"""
        self.sigApply.emit()

    def _updateCORMarker(self, value):
        if value is None:
            try:
                self._plot.removeMarker(self._MARKER_NAME)
            except:
                pass
        else:
            # change reference:
            img = self._plot.getActiveImage(just_legend=False)
            if img:
                value = value + img.getData().shape[1] // 2
            self._plot.addXMarker(
                value, legend=self._MARKER_NAME, color=self._MARKER_COLOR, text="center"
            )


class _LoadSinoThread(qt.QThread):
    def init(self, scan, line, subsampling):
        self._scan = scan
        self._line = line
        self._subsampling = subsampling

    def run(self):
        self._scan.axis_params.use_sinogram = True
        self._scan.axis_params.sinogram_line = self._line
        self._scan.axis_params.sinogram_subsampling = self._subsampling

        try:
            self._scan.get_sinogram(line=self._line, subsampling=self._subsampling)
        except ValueError as e:
            _logger.error(e)


class _SinogramOpts(qt.QWidget):
    """
    Add axis calculation options for sinogram
    """

    sigComputationRequested = qt.Signal()
    """signal emitted when a computation is requested"""

    sigApply = qt.Signal()
    """signal emitted when the axis reconstruction parameters are validated"""

    sigAxisEditionLocked = qt.Signal(bool)
    """Signal emitted when the status of the reconstruction parameters edition
    change"""

    sigPositionChanged = qt.Signal(object)
    """Signal emitted when the cor value changed"""

    sigLockModeChanged = qt.Signal(bool)
    """Signal emitted when the lock mode change"""

    def __init__(self, parent, axis_params):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self._axis = axis_params
        self._scan = None

        self._dataModeWidget = qt.QWidget(parent=self)
        self._dataModeWidget.setLayout(qt.QHBoxLayout())
        self._dataModeWidget.layout().addWidget(
            qt.QLabel("Data mode", parent=self._dataModeWidget)
        )
        self._qcbDataMode = qt.QComboBox(parent=self)
        for input_type in AxisCalculationInput:
            # paganin is not managed for sinogram
            if input_type == AxisCalculationInput.transmission_pag:
                continue
            else:
                self._qcbDataMode.addItem(input_type.name(), input_type)
        self._dataModeWidget.layout().addWidget(self._qcbDataMode)
        self._lockMethodPB = PadlockButton(parent=self._dataModeWidget)
        self._lockMethodPB.setToolTip(
            "Lock the method to compute the cor. \n"
            "This will automatically call the "
            "defined algorithm each time a scan is received."
        )
        self._dataModeWidget.layout().addWidget(self._lockMethodPB)

        self.layout().addWidget(self._dataModeWidget)

        # add line
        self._lineSelWidget = qt.QWidget(parent=self)
        self._lineSelWidget.setLayout(qt.QHBoxLayout())
        self._lineSelWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._lineSB = qt.QSpinBox(parent=self)
        self._lineSelWidget.layout().addWidget(qt.QLabel("radio line", self))
        self._lineSelWidget.layout().addWidget(self._lineSB)
        self.layout().addWidget(self._lineSelWidget)
        # TODO: add an option to show the radios from here ???

        # add subsampling option
        self._subsamplingWidget = qt.QWidget(parent=self)
        self._subsamplingWidget.setLayout(qt.QHBoxLayout())
        self._subsamplingWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._subsamplingSB = qt.QSpinBox(parent=self)
        self._subsamplingSB.setMinimum(1)
        self._subsamplingSB.setValue(4)
        self._subsamplingSB.setMaximum(100)
        self._subsamplingWidget.layout().addWidget(qt.QLabel("subsampling", self))
        self._subsamplingWidget.setToolTip(
            "if you like you can only take a "
            "subsample of the sinogram to speed up process"
        )
        self._subsamplingWidget.layout().addWidget(self._subsamplingSB)
        self.layout().addWidget(self._subsamplingWidget)

        # add spacer
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        # set up
        if self._axis.sinogram_line is None:
            self._axis.sinogram_line = 0
        else:
            self._lineSB.setValue(self._axis.sinogram_line)
        self._subsamplingSB.setValue(self._axis.sinogram_subsampling)

        # make connection
        self._qcbDataMode.currentIndexChanged.connect(self._updateInputType)

    def _needComputation(self, *arg, **kwargs):
        """callback when the radio line changed"""
        if self._scan is not None:
            self.sigComputationRequested.emit()

    def _lockModeChanged(self, lock, disable_other_mode_lock=False):
        self._lockLabel.setEnabled(not lock)
        self._lockBut.setEnabled(not lock)
        self._qcbDataMode.setEnabled(not lock)
        if disable_other_mode_lock is True:
            self.setEnabled(not lock)
        self.sigLockModeChanged.emit(lock)

    def getRadioLine(self):
        return self._lineSB.value()

    def getSubsampling(self):
        return self._subsamplingSB.value()

    def setScan(self, scan):
        """
        set the gui for this scan

        :param TomwerScanBase scan:
        """
        if scan is None:
            return
        assert isinstance(scan, TomwerScanBase)
        self.blockSignals(True)
        # update line max and value
        n_line = scan.dim_2
        if n_line is None:
            n_line = 0
        self._lineSB.setMaximum(n_line)
        if scan.axis_params.sinogram_line is not None:
            self._lineSB.setValue(scan.axis_params.sinogram_line)
        elif self._lineSB.value() == 0:
            self._lineSB.setValue(n_line // 2)

        self._scan = scan
        self.blockSignals(False)

    def _updateInputType(self):
        self._axis.calculation_input_type = self.getCalulationInputType()

    def getCalulationInputType(self, *arg, **kwargs):
        return AxisCalculationInput.from_value(self._qcbDataMode.currentText())

    def setLocked(self, locked):
        self._dataModeWidget.setEnabled(not locked)
        self._qcbDataMode.setEnabled(not locked)
        self._dataModeWidget.setEnabled(not locked)
        self._lineSelWidget.setEnabled(not locked)
        self._lineSB.setEnabled(not locked)
        self._subsamplingWidget.setEnabled(not locked)
        self.sigAxisEditionLocked.emit(locked)

    def isModeLock(self):
        return self._lockMethodPB.isChecked()
