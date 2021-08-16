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
__date__ = "10/01/2018"


import logging
from ..utils import WidgetLongProcessing
from silx.gui import qt
from Orange.widgets import gui
from orangecontrib.tomwer.orange.managedprocess import SuperviseOW
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, Output
from tomwer.core.process.reconstruction.darkref.darkrefs import DarkRefs
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui.reconstruction.darkref.darkrefcopywidget import DarkRefAndCopyWidget
from tomwer.synctools.ftseries import QReconsParams
from tomwer.web.client import OWClient
from processview.core.manager import DatasetState
from processview.core.manager import ProcessManager
from tomwer.utils import docstring
import copy

logger = logging.getLogger(__name__)


class DarkRefAndCopyOW(SuperviseOW, OWClient, WidgetLongProcessing):
    """
    A simple widget managing the copy of an incoming folder to an other one

    :param parent: the parent widget
    """

    # note of this widget should be the one registred on the documentation
    name = "dark and flat field construction"
    id = "orange.widgets.tomwer.darkrefs"
    description = "This widget will generate dark refs for a received scan "
    icon = "icons/darkref.svg"
    priority = 15
    category = "esrfWidgets"
    keywords = ["tomography", "dark", "darks", "ref", "refs"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    _rpSetting = Setting(dict())
    """Setting to load and save DarkRefAndCopyWidget settings"""

    sigScanReady = qt.Signal(TomwerScanBase)
    """Signal emitted when a scan is ready"""

    assert len(DarkRefs.inputs) == 1

    class Inputs:
        data_in = Input(
            name=DarkRefs.inputs[0].name,
            type=DarkRefs.inputs[0].type,
            doc=DarkRefs.inputs[0].doc,
        )

    assert len(DarkRefs.outputs) == 1

    class Outputs:
        data_out = Output(
            name=DarkRefs.outputs[0].name,
            type=DarkRefs.outputs[0].type,
            doc=DarkRefs.outputs[0].doc,
        )

    def __init__(self, parent=None, reconsparams=None):
        """

        :param QReconsParams reconsparams: reconstruction parameters
        """
        SuperviseOW.__init__(self, parent)
        OWClient.__init__(self)
        recons_params = reconsparams or QReconsParams()
        if self._rpSetting != dict():
            try:
                recons_params.dkrf.load_from_dict(self._rpSetting)
            except:
                logger.warning("fail to load reconstruction settings")

        self.widget = DarkRefAndCopyWidget(
            parent=self, reconsparams=recons_params, process_id=self.process_id
        )
        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self._layout.addWidget(self.widget)
        self.setForceSync = self.widget.setForceSync

        # expose API
        self.hasRefStored = self.widget.hasFlatStored
        self.setModeAuto = self.widget.set_mode_auto
        self.setRefsFromScan = self.widget.setRefsFromScan
        self.setCopyActive = self.widget.setCopyActive
        self.hasDarkStored = self.widget.hasDarkStored
        self.hasFlatStored = self.widget.hasFlatStored

        # connect signal / slot
        self.widget.sigProcessingStart.connect(self._startProcessing)
        self.widget.sigProcessingEnd.connect(self._endProcessing)
        self.widget.sigScanReady.connect(self.signalReady)
        self.widget.recons_params.sigChanged.connect(self._updateSettingsVals)
        self.widget.sigModeAutoChanged.connect(self._updateSettingsVals)
        self.widget.sigCopyActivationChanged.connect(self._updateSettingsVals)

        # load some other copy parameters
        if self._rpSetting != dict():
            try:
                if "activate" in self._rpSetting:
                    self.widget.setCopyActive(self._rpSetting["activate"])
                    del self._rpSetting["activate"]
                if "auto" in self._rpSetting:
                    self.widget.setModeAuto(self._rpSetting["auto"])
                    del self._rpSetting["auto"]
            except:
                logger.warning("fail to load reconstruction settings")

        self.setCaption(self.windowTitle())

    @Inputs.data_in
    def process(self, scanID):
        if scanID is None:
            return
        assert isinstance(scanID, TomwerScanBase)
        ProcessManager().notify_dataset_state(
            dataset=scanID, process=self, state=DatasetState.PENDING
        )
        return self.widget.process(copy.copy(scanID))

    @docstring(SuperviseOW)
    def reprocess(self, dataset):
        self.process(dataset)

    def signalReady(self, scanID):
        assert isinstance(scanID, TomwerScanBase)
        self.Outputs.data_out.send(scanID)
        self.sigScanReady.emit(scanID)

    def _updateSettingsVals(self):
        self._rpSetting = self.widget.recons_params.to_dict()
        self._rpSetting["auto"] = self.widget.isOnModeAuto()
        self._rpSetting["activate"] = self.widget.isCopyActive()

    @property
    def recons_params(self):
        return self.widget.recons_params

    def close(self):
        self.widget.close()
        super(DarkRefAndCopyOW, self).close()
