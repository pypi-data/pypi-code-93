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
__date__ = "12/12/2018"


from tomwer.core.process.baseprocess import SingleProcess, _input_desc, _output_desc
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
import time
import logging

_logger = logging.getLogger(__name__)


class Timer(SingleProcess):
    """
    Simple timer / time out - function"""

    inputs = [
        _input_desc(
            name="data", type=TomwerScanBase, handler="process", doc="scan object"
        )
    ]

    outputs = [_output_desc(name="data", type=TomwerScanBase, doc="scan object")]

    def __init__(self, wait):
        SingleProcess.__init__(self)
        self.waiting_time = wait or 1

    @property
    def waiting_time(self):
        return self._waiting_time

    @waiting_time.setter
    def waiting_time(self, wait):
        self._waiting_time = wait

    def process(self, scan):
        if type(scan) is dict:
            _scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            _scan = scan
        assert isinstance(scan, TomwerScanBase)
        time.sleep(self.waiting_time)
        if self._return_dict:
            return _scan.to_dict()
        else:
            return _scan
