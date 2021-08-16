# coding: utf-8
###########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
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
#############################################################################

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "09/01/2018"

from silx.gui import qt
from tomwer.core.process.reconstruction.darkref.darkrefs import DarkRefsWorker

from tomwer.core.process.reconstruction.darkref.darkrefscopy import DarkRefsCopyWorker


class DarkRefsWorkerThread(DarkRefsWorker, qt.QThread):
    """Implementation of the DarkRefsWorker on a qt.QThread for gui"""

    sigProcessingStart = qt.Signal()
    """signal emitted when run start"""

    def __init__(self, process_id):
        DarkRefsWorker.__init__(self, process_id=process_id)
        qt.QThread.__init__(self)

    def run(self):
        self.sigProcessingStart.emit()
        DarkRefsWorker.run()


class DarkRefsCopyWorkerThread(DarkRefsCopyWorker, qt.QThread):
    """Implementation of the DarkRefsCopyWorker on a qt.QThread for gui"""

    sigProcessingStart = qt.Signal()
    """signal emitted when run start"""

    def __init__(self, process, process_id):
        DarkRefsCopyWorker.__init__(self, process=process, process_id=process_id)
        qt.QThread.__init__(self)

    def run(self):
        self.sigProcessingStart.emit()
        DarkRefsCopyWorker.run(self)
