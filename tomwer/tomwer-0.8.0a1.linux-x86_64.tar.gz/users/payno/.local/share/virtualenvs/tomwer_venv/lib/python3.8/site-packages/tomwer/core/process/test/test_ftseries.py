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
__date__ = "05/04/2019"


import shutil
import tempfile
import unittest
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.utils import getParametersFromParOrInfo
from ..reconstruction.ftseries import Ftseries
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.process.reconstruction.ftseries.params import ReconsParams
from tomwer.test.utils import UtilsTest
import os


class TestFtseriesIO(unittest.TestCase):
    """Test inputs and outputs types of the handler functions"""

    def setUp(self) -> None:
        self.scan_folder = tempfile.mkdtemp()

        self.scan = MockEDF.mockScan(
            scanID=self.scan_folder, nRadio=10, nRecons=1, nPagRecons=4, dim=10
        )
        self.recons_params = ReconsParams()
        self.ftseries_process = Ftseries(self.recons_params)
        self.ftseries_process.setMockMode(True)

    def tearDown(self) -> None:
        shutil.rmtree(self.scan_folder)

    def testInputOutput(self) -> None:
        """Test that io using TomoBase instance work"""
        for input_type in (dict, TomwerScanBase):
            for _input in Ftseries.inputs:
                for return_dict in (True, False):
                    with self.subTest(
                        handler=_input.handler,
                        return_dict=return_dict,
                        input_type=input_type,
                    ):
                        input_obj = self.scan
                        if input_obj is dict:
                            input_obj = input_obj.to_dict()
                        self.ftseries_process._set_return_dict(return_dict)
                        out = getattr(self.ftseries_process, _input.handler)(input_obj)
                        if return_dict:
                            self.assertTrue(isinstance(out, dict))
                        else:
                            self.assertTrue(isinstance(out, TomwerScanBase))


class TestFtseriesAxis(unittest.TestCase):
    """Test the behavior of ftseries depending on the axis parameter"""

    def setUp(self) -> None:
        self.outputDir = tempfile.mkdtemp()
        self.dataSetID = "scan_3_"
        self.dataDir = UtilsTest.getEDFDataset(self.dataSetID)
        self.datasetDir = os.path.join(self.outputDir, self.dataSetID)
        shutil.copytree(src=os.path.join(self.dataDir), dst=self.datasetDir)
        self.recons_params = ReconsParams()
        self.ftseries = Ftseries(recons_params=self.recons_params)
        self.parFile = os.path.join(self.datasetDir, self.dataSetID + ".par")
        if os.path.exists(self.parFile):
            os.remove(self.parFile)
        self.scan = EDFTomoScan(self.datasetDir)
        self.axis_frm_tomwer_file = os.path.join(self.datasetDir, "correct.txt")

    def tearDown(self) -> None:
        shutil.rmtree(self.outputDir)

    def testAxisCorrectionOption(self) -> None:
        """Test that the pyhst parameter 'DO_AXIS_CORRECTION' is correctly set"""
        self.recons_params.axis.do_axis_correction = False
        self.ftseries.process(self.scan)
        self.assertTrue(os.path.exists(self.parFile))
        par_info = getParametersFromParOrInfo(self.parFile)
        self.assertTrue("DO_AXIS_CORRECTION".lower() in par_info)
        self.assertTrue(par_info["DO_AXIS_CORRECTION".lower()] in ("NO", 0))

        self.recons_params.axis.do_axis_correction = True
        self.ftseries.process(self.scan)
        self.assertTrue(os.path.exists(self.parFile))
        par_info = getParametersFromParOrInfo(self.parFile)
        self.assertTrue("DO_AXIS_CORRECTION".lower() in par_info)
        self.assertTrue(par_info["DO_AXIS_CORRECTION".lower()] in ("YES", 1))
        self.assertFalse(os.path.exists(self.axis_frm_tomwer_file))
        self.assertEqual(par_info["AXIS_CORRECTION_FILE".lower()], "")

    # no time to look into it. Now focus on nabu
    # def testLinkWithAxis(self) -> None:
    #     """Test ftseries process behavior with AxisProcess"""
    #     from tomwer.core.process.reconstruction.axis import AxisRP, AxisProcess
    #
    #     axis_params = AxisRP()
    #     axis_params.mode = "manual"
    #     axis_params.set_relative_value(2.5)
    #     axis_process = AxisProcess(axis_params=axis_params)
    #
    #     # part 1: test scan with an axis computation history
    #     self.recons_params.axis.do_axis_correction = True
    #     self.recons_params.axis.use_tomwer_axis = True
    #     self.recons_params.axis.use_old_tomwer_axis = False
    #     self.ftseries.process(scan=self.scan)
    #     self.assertFalse(os.path.exists(self.axis_frm_tomwer_file))
    #     par_info = getParametersFromParOrInfo(self.parFile)
    #     self.assertTrue("AXIS_CORRECTION_FILE".lower() in par_info)
    #     self.assertEqual(par_info["AXIS_CORRECTION_FILE".lower()], "")
    #
    #     # then process axis then ftseries
    #     axis_process.process(scan=self.scan)
    #     self.ftseries.process(scan=self.scan)
    #     self.assertTrue(os.path.exists(self.axis_frm_tomwer_file))
    #     par_info = getParametersFromParOrInfo(self.parFile)
    #     self.assertEqual(
    #         par_info["AXIS_CORRECTION_FILE".lower()], self.axis_frm_tomwer_file
    #     )
    #     with open(file=self.axis_frm_tomwer_file, mode="r") as f_:
    #         l = f_.readline()
    #         self.assertEqual(l, "2.5")
    #
    #     # part 2: test from a new scan without any axis process history
    #     scan2 = EDFTomoScan(scan=self.datasetDir)
    #     os.remove(self.parFile)
    #     self.ftseries.process(scan=scan2)
    #     self.assertTrue(os.path.exists(self.parFile))
    #     self.recons_params.axis.use_old_tomwer_axis = True
    #     self.ftseries.process(scan=scan2)
    #     self.assertTrue(os.path.exists(self.parFile))
    #     self.assertTrue(os.path.exists(self.axis_frm_tomwer_file))
    #     with open(file=self.axis_frm_tomwer_file, mode="r") as f_:
    #         l = f_.readline()
    #         self.assertEqual(l, "2.5")
    #
    #     # then process axis on scan 2 with a different value
    #     axis_params.set_relative_value(-1.3)
    #     axis_process.process(scan=scan2)
    #     self.ftseries.process(scan=scan2)
    #     with open(file=self.axis_frm_tomwer_file, mode="r") as f_:
    #         l = f_.readline()
    #         self.assertEqual(l, "-1.3")


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestFtseriesIO,):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
    return test_suite
