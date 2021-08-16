# coding: utf-8
# /*##########################################################################
# Copyright (C) 2017 European Synchrotron Radiation Facility
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
#############################################################################*/

"""
This module is used to define a set of folders to be emitted to the next box.
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "05/07/2017"


from tomwer.core.signal import Signal
from tomwer.core.process.baseprocess import BaseProcess, _output_desc
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
import logging
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.edfscan import EDFTomoScan

logger = logging.getLogger(__name__)


class _ScanList(BaseProcess):
    """Process to list a set of scan"""

    scanReady = Signal(TomwerScanBase)

    outputs = [_output_desc(name="data", type=TomwerScanBase, doc="scan path")]

    endless_process = True

    def __init__(self):
        BaseProcess.__init__(self)
        self._scanIDs = {}
        """associate path (key) to TomoBase object"""

    def process(self):
        """function to launch if is the first box to be executed"""
        self._sendList()
        res = []
        for scanID, scan in self._scanIDs.items():
            if self._return_dict:
                res.append(scan.to_dict())
            else:
                res.append(scan)
        return res

    def set_properties(self, properties):
        if "_scanIDs" in properties:
            self.setScanIDs(properties["_scanIDs"])
        else:
            raise ValueError("scansID no included in the widget properties")

    def setScanIDs(self, list_of_scan):
        for folder in list_of_scan:
            self.add(folder)

    def add(self, folder):
        """Add a folder to the list

        :param folder: the path to the folder for the scan to add
        :type folder: Union[str, :class:`.TomoBase`]
        """
        if isinstance(folder, TomwerScanBase):
            _scan_obj = folder
        else:
            try:
                _scan_obj = ScanFactory.create_scan_object(folder)
            except ValueError as e:
                logger.warning(e)
                return
        self._scanIDs[str(_scan_obj)] = _scan_obj
        return _scan_obj

    def remove(self, folder):
        """Remove a folder to the list

        :param str folder: the path to the folder for the scan to add
        """
        if folder in self._scanIDs:
            del self._scanIDs[folder]

    def clear(self):
        """clear the list"""
        self._scanIDs.clear()

    def _sendList(self):
        for scanID, scan in self._scanIDs.items():
            self.scanReady.emit(scan)

    def length(self):
        return len(self._scanIDs)


class ScanList(_ScanList):
    """For now to avoid multiple inheritance from QObject with the process widgets
    we have to define two classes. One only for the QObject inheritance
    """

    data = _ScanList.scanReady
