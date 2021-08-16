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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "19/07/2018"

from silx.gui import qt
from Orange.widgets import gui
from orangecontrib.tomwer.orange.managedprocess import SuperviseOW
from Orange.widgets.widget import Input, Output
from tomwer.web.client import OWClient
from tomwer.gui.conditions.filter import FileNameFilterWidget
from tomwer.core.scan.scanbase import TomwerScanBase
from processview.core.manager import DatasetState
from tomwer.utils import docstring
import logging

logger = logging.getLogger(__name__)


class NameFilterOW(SuperviseOW, OWClient):
    name = "scan filter"
    id = "orange.widgets.tomwer.filterow"
    description = (
        "Simple widget which filter some data directory if the name"
        "doesn't match with the pattern defined."
    )
    icon = "icons/namefilter.svg"
    priority = 106
    category = "esrfWidgets"
    keywords = ["tomography", "selection", "tomwer", "folder", "filter"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    class Inputs:
        data_in = Input(name="data", type=TomwerScanBase)

    class Outputs:
        data_out = Output(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        """ """
        SuperviseOW.__init__(self, parent)
        OWClient.__init__(self)

        self.widget = FileNameFilterWidget(parent=self)
        self.widget.setContentsMargins(0, 0, 0, 0)

        layout = gui.vBox(self.mainArea, self.name).layout()
        layout.addWidget(self.widget)
        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        layout.addWidget(spacer)

        # expose API
        self.setPattern = self.widget.setPattern

    @Inputs.data_in
    def applyfilter(self, scan):
        if scan is None:
            return
        assert isinstance(scan, TomwerScanBase)
        if not self.widget.isFiltered(scan.path):
            self.set_dataset_state(dataset=scan, state=DatasetState.SUCCEED)
            logger.processSucceed("{} pass through filter".format(str(scan)))
            self._signalScanReady(scan)
        else:
            self.set_dataset_state(dataset=scan, state=DatasetState.FAILED)
            logger.processFailed("{} NOT pass through filter".format(str(scan)))

    @docstring(SuperviseOW)
    def reprocess(self, dataset):
        self.applyfilter(dataset)

    def _signalScanReady(self, scan):
        self.Outputs.data_out.send(scan)
