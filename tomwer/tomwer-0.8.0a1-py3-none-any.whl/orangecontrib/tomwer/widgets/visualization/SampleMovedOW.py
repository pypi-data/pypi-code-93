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

__authors__ = ["C. Nemoz", "H. Payno"]
__license__ = "MIT"
__date__ = "19/03/2018"

from silx.gui import qt
from Orange.widgets import widget, gui
from Orange.widgets.widget import Input
from tomwer.web.client import OWClient
from tomwer.gui.samplemoved import SampleMovedWidget
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.edfscan import EDFTomoScan
import os
import logging

logger = logging.getLogger(__name__)


class SampleMovedOW(widget.OWWidget, OWClient):
    """
    Simple widget exposing two images side by side to see if a sample moved
    during the acquisition.

    :param parent: the parent widget
    """

    name = "sample moved"
    id = "orange.widgets.tomwer.samplemoved"
    description = (
        "This widget is used to display two scan side by side "
        "to know if a sample moved during the acquisition by "
        "simple observation."
    )
    icon = "icons/sampleMoved.svg"
    priority = 85
    category = "esrfWidgets"
    keywords = ["tomography", "sample", "moved", "visualization"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    class Inputs:
        data_in = Input(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        widget.OWWidget.__init__(self, parent)
        OWClient.__init__(self)

        layout = gui.vBox(self.mainArea, self.name).layout()

        self._widgetScanPath = qt.QWidget(parent=self)
        self._widgetScanPath.setLayout(qt.QHBoxLayout())
        self._widgetScanPath.layout().addWidget(
            qt.QLabel("scan: ", parent=self._widgetScanPath)
        )
        self._scanNameQLabel = qt.QLabel("", parent=self._widgetScanPath)
        self._widgetScanPath.layout().addWidget(self._scanNameQLabel)
        spacer = qt.QWidget(parent=self._widgetScanPath)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self._widgetScanPath.layout().addWidget(spacer)
        layout.addWidget(self._widgetScanPath)

        self._mainWidget = SampleMovedWidget(parent=self)
        layout.addWidget(self._mainWidget)

    def sizeHint(self):
        return qt.QSize(400, 200)

    @Inputs.data_in
    def updateScan(self, scan):
        if scan is None:
            return

        assert isinstance(scan, TomwerScanBase)
        if os.path.isdir(scan.path):
            self._scanNameQLabel.setText(os.path.basename(scan.path))
            rawSlices = scan.get_proj_angle_url()

            self._mainWidget.clearOnLoadActions()
            self._mainWidget.setImages(rawSlices)
            self._mainWidget.setOnLoadAction(scan.flat_field_correction)

    def clear(self):
        self._scanNameQLabel.setText("")
        self._mainWidget.clear()
