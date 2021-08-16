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


import unittest
import tempfile
import shutil
import os
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.process.control.datatransfert import FolderTransfert
from tomwer.test.utils import UtilsTest
from nxtomomill import converter as nxtomomill_converter
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.synctools.rsyncmanager import RSyncManager
import pytest


class TestDataTransferIO(unittest.TestCase):
    """Test inputs and outputs types of the handler functions"""

    def setUp(self):
        self.origin_folder = tempfile.mkdtemp()
        self.scan_folder = os.path.join(self.origin_folder, "scan_toto")
        os.makedirs(self.scan_folder)
        self.output_folder = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.output_folder, "scan_toto"))

        self.scan = MockEDF.mockScan(
            scanID=self.scan_folder, nRadio=10, nRecons=1, nPagRecons=4, dim=10
        )
        self.transfert_process = FolderTransfert()
        self.transfert_process.setDestDir(self.output_folder)

        self.scan = MockEDF.mockScan(
            scanID=self.scan_folder,
            nRadio=10,
            nRecons=1,
            nPagRecons=4,
            dim=10,
        )

    def tearDown(self):
        shutil.rmtree(self.origin_folder)
        shutil.rmtree(self.output_folder)

    def testInputOutput(self):
        """Test that io using TomoBase instance work"""
        for input_type in (dict, TomwerScanBase):
            for _input in FolderTransfert.inputs:
                for return_dict in (True, False):
                    with self.subTest(
                        handler=_input.handler,
                        return_dict=return_dict,
                        input_type=input_type,
                    ):
                        if os.path.exists(self.output_folder):
                            shutil.rmtree(self.output_folder)
                            os.makedirs(self.output_folder)

                        self.scan = MockEDF.mockScan(
                            scanID=self.scan_folder,
                            nRadio=10,
                            nRecons=1,
                            nPagRecons=4,
                            dim=10,
                        )

                        assert os.path.exists(self.output_folder)
                        input_obj = self.scan
                        if input_obj is dict:
                            input_obj = input_obj.to_dict()
                        self.transfert_process._set_return_dict(return_dict)
                        out = getattr(self.transfert_process, _input.handler)(input_obj)
                        if return_dict:
                            self.assertTrue(isinstance(out, dict))
                        else:
                            self.assertTrue(isinstance(out, TomwerScanBase))


@pytest.mark.skipif(not RSyncManager().has_rsync(), reason="requires rsync")
class TestBlissDataTransfer(unittest.TestCase):
    """Make sure we can transfer data from bliss acquisition"""

    def setUp(self):
        self.input_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        shutil.copytree(
            UtilsTest.getBlissDataset(folderID="sample"),
            os.path.join(self.input_dir, "sample"),
        )

        self._proposal_file = os.path.join(
            self.input_dir, "sample", "ihpayno_sample.h5"
        )
        self._sample_file = os.path.join(
            self.input_dir, "sample", "sample_29042021", "sample_29042021.h5"
        )
        self._sample_file_entry = "1.1"

        self.process = FolderTransfert()
        self.process.setDestDir(self.output_dir)

        # convert it to nx
        output_file_path = os.path.join(
            self.input_dir, "sample", "sample_29042021", "test_nx.h5"
        )
        entries = ("/1.1",)
        assert os.path.exists(self._sample_file)
        conv = nxtomomill_converter.h5_to_nx(
            input_file_path=self._sample_file,
            output_file=output_file_path,
            entries=entries,
            single_file=False,
            ask_before_overwrite=False,
            request_input=False,
            file_extension=".nx",
        )
        self.assertEqual(len(conv), 1)
        conv_file, conv_entry = conv[0]
        self.scan = HDF5TomoScan(scan=conv_file, entry=conv_entry)

        # mock data listener: the processing of the Data transfer requires
        # knowledge of bliss files origin.
        from tomwer.core.process.control.datalistener import DataListener

        data_listener = DataListener()
        data_listener.process_sample_file(
            sample_file=self._sample_file,
            entry=self._sample_file_entry,
            proposal_file=self._proposal_file,
            master_sample_file=None,
        )

    def tearDown(self):
        shutil.rmtree(self.input_dir)
        shutil.rmtree(self.output_dir)

    def testDataTransfer(self):
        """Make sure the data transfer is able to retrieve the scan,
        proposal file and scan file to transfer.
        Check that only the specific scan folders will be copy and removed
        and the other won't be affected.
        """
        out_nx = os.path.join(self.output_dir, "sample_29042021", "test_nx.h5")
        self.assertFalse(os.path.exists(out_nx))
        out_proposal = os.path.join(self.output_dir, "ihpayno_sample.h5")
        self.assertFalse(os.path.exists(out_proposal))
        out_sample_file = os.path.join(
            self.output_dir, "sample_29042021", "sample_29042021.h5"
        )
        self.assertFalse(os.path.exists(out_sample_file))
        out_included_scans = [
            os.path.join(self.output_dir, "sample_29042021", "scan0002")
        ]
        for scan_path in out_included_scans:
            self.assertFalse(os.path.exists(scan_path))
        out_not_included_scans = [
            os.path.join(self.output_dir, "sample_29042021", "scan0004"),
            os.path.join(self.output_dir, "sample_29042021", "scan0006"),
            os.path.join(self.output_dir, "sample_29042021", "scan0008"),
        ]
        for scan_path in out_not_included_scans:
            self.assertFalse(os.path.exists(scan_path))

        self.process.setForceSync(True)
        self.process.process(scan=self.scan)
        import time

        time.sleep(2)
        self.assertTrue(os.path.exists(out_nx))
        self.assertTrue(os.path.exists(out_proposal))
        self.assertTrue(os.path.exists(out_sample_file))
        for scan_path in out_included_scans:
            self.assertTrue(os.path.exists(scan_path))
        for scan_path in out_not_included_scans:
            self.assertFalse(os.path.exists(scan_path))


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestDataTransferIO, TestBlissDataTransfer):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
    return test_suite
