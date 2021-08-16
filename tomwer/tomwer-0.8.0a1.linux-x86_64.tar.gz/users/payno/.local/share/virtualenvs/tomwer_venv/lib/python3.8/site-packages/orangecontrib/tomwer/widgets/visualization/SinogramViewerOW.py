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
__date__ = "01/08/2018"

from Orange.widgets import widget, gui
from Orange.widgets.widget import Input
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui.visualization.sinogramviewer import SinogramViewer
from ..utils import WidgetLongProcessing
import logging

logger = logging.getLogger(__name__)


class SinogramViewerOW(WidgetLongProcessing, widget.OWWidget):
    """
    This widget can be used to compute and display a specific sinogram from an
    acquisition.
    """

    name = "sinogram viewer"
    id = "orange.widgets.tomwer.visualization.sinogramviewer"
    description = (
        "This widget can be used to compute and display a "
        "specific sinogram from an acquisition."
    )

    icon = "icons/sinogramviewer.png"
    priority = 5
    category = "tomwer"
    keywords = ["tomography", "sinogram", "radio"]

    allows_cycle = True
    compress_signal = False

    want_main_area = True
    resizing_enabled = True

    class Inputs:
        data_in = Input(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        widget.OWWidget.__init__(self, parent)
        WidgetLongProcessing.__init__(self)
        self._box = gui.vBox(self.mainArea, self.name)
        self._viewer = SinogramViewer(parent=self)
        self._box.layout().addWidget(self._viewer)

        # connect signal / slot
        self._viewer.sigSinoLoadStarted.connect(self._startProcessing)
        self._viewer.sigSinoLoadEnded.connect(self._endProcessing)
        self.destroyed.connect(self._viewer._stopAnimationThread)

    @Inputs.data_in
    def addLeafScan(self, scanID):
        if scanID is None:
            return
        self._viewer.setScan(scanID)
