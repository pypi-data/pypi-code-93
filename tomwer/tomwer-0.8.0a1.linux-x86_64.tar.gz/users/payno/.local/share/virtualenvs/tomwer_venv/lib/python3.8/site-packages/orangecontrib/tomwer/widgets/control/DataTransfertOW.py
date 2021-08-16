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
__date__ = "07/12/2016"

import logging
from Orange.widgets import widget, gui
from Orange.widgets import settings
from Orange.widgets.widget import Output, Input
from silx.gui import qt
from orangecontrib.tomwer.orange.settings import CallbackSettingsHandler
from tomwer.core.process.control.datatransfert import FolderTransfert
from tomwer.web.client import OWClient
from tomwer.gui.control.datatransfert import DataTransfertSelector
from tomwer.core.scan.scanbase import TomwerScanBase
from processview.core.manager import ProcessManager, DatasetState
from orangecontrib.tomwer.orange.managedprocess import SuperviseOW
from tomwer.utils import docstring

logger = logging.getLogger(__name__)


class DataTransfertOW(SuperviseOW, FolderTransfert, OWClient):
    """
    A simple widget managing the copy of an incoming folder to an other one

    :param parent: the parent widget
    """

    name = "data transfert"
    id = "orange.widgets.tomwer.foldertransfert"
    description = "This widget insure data transfert of the received data "
    description += "to the given directory"
    icon = "icons/folder-transfert.svg"
    priority = 30
    category = "esrfWidgets"
    keywords = [
        "tomography",
        "transfert",
        "cp",
        "copy",
        "move",
        "file",
        "tomwer",
        "folder",
    ]

    settingsHandler = CallbackSettingsHandler()

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    dest_dir = settings.Setting(str())
    """Parameters directly editabled from the TOFU interface"""

    scanready = qt.Signal(TomwerScanBase)

    assert len(FolderTransfert.inputs) == 1

    class Inputs:
        data_in = Input(
            name=FolderTransfert.inputs[0].name,
            type=FolderTransfert.inputs[0].type,
            doc=FolderTransfert.inputs[0].doc,
        )

    assert len(FolderTransfert.outputs) == 1

    class Outputs:
        data_out = Output(
            name=FolderTransfert.outputs[0].name,
            type=FolderTransfert.outputs[0].type,
            doc=FolderTransfert.outputs[0].doc,
        )

    def __init__(self, parent=None):
        FolderTransfert.__init__(self)
        SuperviseOW.__init__(self, parent)
        OWClient.__init__(self)

        # define GUI
        self._widget = DataTransfertSelector(
            parent=self,
            rnice_option=True,
            default_root_folder=self._getDefaultOutputDir(),
        )
        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self._layout.addWidget(self._widget)

        # signal / SLOT connection
        self.settingsHandler.addCallback(self._updateSettingsVals)
        self._widget.sigSelectionChanged.connect(self._updateDestDir)

        # setting configuration
        if self.dest_dir != "":
            self._widget.setFolder(self.dest_dir)

    def _requestFolder(self):
        """Launch a QFileDialog to ask the user the output directory"""
        dialog = qt.QFileDialog(self)
        dialog.setWindowTitle("Destination folder")
        dialog.setModal(1)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_():
            dialog.close()
            return None

        return dialog.selectedFiles()[0]

    def signalTransfertOk(self, input_scan, output_scan):
        if output_scan is None:
            return
        ProcessManager().notify_dataset_state(
            dataset=input_scan, process=self, state=DatasetState.SUCCEED
        )
        ProcessManager().notify_dataset_state(
            dataset=output_scan, process=self, state=DatasetState.SUCCEED
        )
        # assert isinstance(output_scan, TomwerScanBase)
        self.Outputs.data_out.send(output_scan)
        self.scanready.emit(output_scan)

    def _updateDestDir(self):
        self._destDir = self._widget.getFolder()

    def _updateSettingsVals(self):
        """function used to update the settings values"""
        self.dest_dir = self._destDir

    @Inputs.data_in
    def process(self, scan, move=False, force=True, noRsync=False):
        if scan is None:
            return
        try:
            FolderTransfert.process(
                self, scan=scan, move=move, force=force, noRsync=noRsync
            )
        except Exception as e:
            logger.error("data transfer failed. Reason is {}".format(e))
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=self,
                state=DatasetState.FAILED,
                details=str(e),
            )

    @docstring(SuperviseOW)
    def reprocess(self, dataset):
        self.process(dataset)
