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
__date__ = "09/02/2018"


import logging
import os
import shutil
import tempfile
import unittest
from xml.etree import ElementTree
import fabio
import numpy
import h5py
from silx.gui.utils.testutils import TestCaseQt
from tomwer.core.process.reconstruction.darkref.darkrefs import DarkRefs
from tomwer.core.process.reconstruction.darkref.settings import (
    DARKHST_PREFIX,
    REFHST_PREFIX,
)
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core import utils
from tomwer.core.process.reconstruction.darkref.darkrefscopy import DarkRefsCopy
from tomwer.test.utils import UtilsTest, rebaseAcquisition
from tomwer.core.utils.scanutils import MockHDF5
from silx.io.utils import h5py_read_dataset

logging.disable(logging.INFO)


class TestRefCopyEDF(TestCaseQt):
    """
    Test that RefCopy process is correct for acquisition using EDF
    """

    def setUp(self):
        TestCaseQt.setUp(self)
        self.top_dir = tempfile.mkdtemp()
        dataset_with_ref = "test10"
        data_test_dir = UtilsTest.getEDFDataset(dataset_with_ref)
        self.folder_with_ref = os.path.join(self.top_dir, dataset_with_ref)
        shutil.copytree(data_test_dir, self.folder_with_ref)

        dataset_with_no_ref = "test101"
        self.folder_without_ref = os.path.join(self.top_dir, dataset_with_no_ref)
        rebaseAcquisition(src=self.folder_with_ref, dst=self.folder_without_ref)
        [
            os.remove(f)
            for f in DarkRefs.getRefHSTFiles(
                self.folder_without_ref, prefix=REFHST_PREFIX
            )
        ]
        [
            os.remove(f)
            for f in DarkRefs.getDarkHSTFiles(
                self.folder_without_ref, prefix=DARKHST_PREFIX
            )
        ]

        for acqui in (self.folder_with_ref, self.folder_without_ref):
            for _file in os.listdir(acqui):
                if _file.startswith(("refHST", "dark.edf", "darkHST")):
                    os.remove(os.path.join(acqui, _file))
                if acqui == self.folder_without_ref and _file.startswith("ref"):
                    os.remove(os.path.join(acqui, _file))
        # remove darkend file to avoid creation of dark.edf from it
        os.remove(os.path.join(self.folder_without_ref, "darkend0000.edf"))

        # create back the dark.edf
        darkProcess = DarkRefs()
        darkProcess.setForceSync(True)
        darkProcess.process(self.folder_with_ref)
        del darkProcess
        assert "dark.edf" in os.listdir(self.folder_with_ref)
        assert "refHST0000.edf" in os.listdir(self.folder_with_ref)
        assert "refHST0020.edf" in os.listdir(self.folder_with_ref)
        self.ref_copy_process = DarkRefsCopy(reconsparams=None)
        self.ref_copy_process.setForceSync(True)

    def tearDown(self):
        shutil.rmtree(self.top_dir)
        self.ref_copy_process = None
        TestCaseQt.tearDown(self)

    def testAutoMode(self):
        """Check behavior of the auto mode"""
        self.ref_copy_process.set_mode_auto(True)
        self.ref_copy_process.process(self.folder_with_ref)
        # make sure the refCopy is correctly initialized
        self.assertTrue(self.ref_copy_process.has_flat_stored() is True)
        self.assertTrue(self.ref_copy_process.has_dark_stored() is True)
        # check process is doing the job
        self.ref_copy_process.process(self.folder_without_ref)
        self.assertTrue(
            len(DarkRefs.getRefHSTFiles(self.folder_without_ref, prefix=REFHST_PREFIX))
            > 0
        )
        self.assertTrue(
            len(
                DarkRefs.getDarkHSTFiles(self.folder_without_ref, prefix=DARKHST_PREFIX)
            )
            > 0
        )

    def testManualMode(self):
        """Check behavior of the manual mode"""
        self.ref_copy_process.set_mode_auto(False)
        self.ref_copy_process.set_refs_from_scan(EDFTomoScan(self.folder_with_ref))
        # make sure the refCopy is correctly initialized
        self.assertTrue(self.ref_copy_process.has_dark_stored() is True)
        with h5py.File(self.ref_copy_process.get_dark_save_file(), "r") as h5f:
            assert "dark_basename" in h5f
            self.assertEqual("dark.edf", h5py_read_dataset(h5f["dark_basename"]))
        self.assertTrue(self.ref_copy_process.has_flat_stored())
        # check process is doing the job
        self.ref_copy_process.process(self.folder_without_ref)
        self.assertTrue(
            len(DarkRefs.getRefHSTFiles(self.folder_without_ref, prefix=REFHST_PREFIX))
            > 0
        )
        self.assertTrue(
            len(
                DarkRefs.getDarkHSTFiles(self.folder_without_ref, prefix=DARKHST_PREFIX)
            )
            > 0
        )

    def testNormalizationSRCurrent(self):
        """Make sure the srCurrent is taking into account"""
        self.ref_copy_process.set_mode_auto(False)
        self.ref_copy_process.set_refs_from_scan(EDFTomoScan(self.folder_with_ref))

        self.assertTrue(os.path.isfile(os.path.join(self.folder_with_ref, "dark.edf")))
        original_ref_data = fabio.open(
            os.path.join(self.folder_with_ref, "refHST0000.edf")
        ).data
        assert utils.getSRCurrent(scan_dir=self.folder_with_ref, when="start") == 101.3
        assert utils.getSRCurrent(scan_dir=self.folder_with_ref, when="end") == 93.6
        with h5py.File(
            self.ref_copy_process.get_ref_save_file(), "r", swmr=True
        ) as h5f:
            os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"
            norm_ref_data = h5py_read_dataset(h5f["data_start"])
        self.assertFalse(numpy.array_equal(original_ref_data, norm_ref_data))

        # change SRCurrent on the .xml
        infoXml = os.path.join(self.folder_without_ref, "test101.xml")
        assert os.path.exists(infoXml)
        xmlTree = ElementTree.parse(infoXml)
        xmlTree.getroot()[0][6].text = "200.36"
        xmlTree.getroot()[0][7].text = "199.63"
        xmlTree.write(infoXml)
        self.ref_copy_process.process(self.folder_without_ref)
        self.assertTrue(
            os.path.isfile(os.path.join(self.folder_without_ref, "dark.edf"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(self.folder_without_ref, "refHST0000.edf"))
        )
        copyRefData = fabio.open(
            os.path.join(self.folder_without_ref, "refHST0000.edf")
        ).data
        assert (
            utils.getSRCurrent(scan_dir=self.folder_without_ref, when="start") == 200.36
        )
        assert (
            utils.getSRCurrent(scan_dir=self.folder_without_ref, when="end") == 199.63
        )
        self.assertFalse(numpy.array_equal(original_ref_data, copyRefData))
        self.assertFalse(numpy.array_equal(norm_ref_data, copyRefData))

    def testInverseOperation(self):
        """Make sure we will found back the original flat field reference
        if the process is forced to take the default value for SRCurrent
        two time"""
        self.ref_copy_process.set_mode_auto(False)
        self.ref_copy_process.set_refs_from_scan(EDFTomoScan(self.folder_with_ref))
        originalRefData = fabio.open(
            os.path.join(self.folder_with_ref, "refHST0000.edf")
        ).data
        self.ref_copy_process.process(self.folder_without_ref)
        copyRefData = fabio.open(
            os.path.join(self.folder_without_ref, "refHST0000.edf")
        ).data
        self.assertTrue(originalRefData.shape == copyRefData.shape)
        self.assertTrue(numpy.allclose(originalRefData, copyRefData))


class TestRefCopyHDF5(unittest.TestCase):
    """
    Test that RefCopy process is correct for acquisition using HDF5
    """

    def setUp(self) -> None:
        self._folder = tempfile.mkdtemp()
        mock_with_refs = MockHDF5(
            scan_path=os.path.join(self._folder, "with_refs"),
            n_proj=10,
            n_ini_proj=10,
            create_ini_ref=True,
            create_ini_dark=True,
        )
        self._acquisition_with_refs = mock_with_refs.scan

        mock_without_refs = MockHDF5(
            scan_path=os.path.join(self._folder, "without_refs"),
            n_proj=10,
            n_ini_proj=10,
            create_ini_ref=False,
            create_ini_dark=False,
        )

        self._acquisition_without_refs = mock_without_refs.scan
        self.ref_copy_process = DarkRefsCopy(reconsparams=None)
        self.ref_copy_process.setForceSync(True)
        # process dark ref to create dark and ref
        tomwer_processes_file = os.path.join(
            self._acquisition_with_refs.path,
            os.path.basename(self._acquisition_with_refs.path) + "_tomwer_processes.h5",
        )
        assert not os.path.exists(tomwer_processes_file)
        dkref_process = DarkRefs()
        dkref_process.process(self._acquisition_with_refs)
        assert os.path.exists(tomwer_processes_file)
        self.darks = DarkRefs.get_darks_frm_process_file(tomwer_processes_file)
        self.flats = DarkRefs.get_flats_frm_process_file(tomwer_processes_file)
        assert len(self.darks) == 1
        assert 0 in self.darks
        assert len(self.flats) == 1
        assert 1 in self.flats.keys()

    def tearDown(self) -> None:
        shutil.rmtree(self._folder)
        self.ref_copy_process = None

    def testCopy(self):
        """Check behavior of the copy, if mode is manual or automatic"""
        for auto_mode in (True, False):
            with self.subTest(auto_mode=auto_mode):
                if os.path.exists(self._acquisition_without_refs.process_file):
                    os.remove(self._acquisition_without_refs.process_file)
                self.ref_copy_process.set_mode_auto(auto_mode)
                self.ref_copy_process.set_refs_from_scan(self._acquisition_with_refs)
                # make sure the refCopy is correctly initialized
                self.assertTrue(self.ref_copy_process.has_dark_stored() is True)
                self.assertTrue(self.ref_copy_process.has_flat_stored())
                # check process is doing the job
                self.assertFalse(
                    os.path.exists(self._acquisition_without_refs.process_file)
                )
                self.ref_copy_process.process(self._acquisition_without_refs)
                self.assertTrue(
                    os.path.exists(self._acquisition_without_refs.process_file)
                )
                # compare dark and refs
                copied_darks = DarkRefs.get_darks_frm_process_file(
                    self._acquisition_without_refs.process_file,
                    entry=self._acquisition_without_refs.entry,
                )
                self.assertTrue(0 in copied_darks)
                copied_flats = DarkRefs.get_flats_frm_process_file(
                    self._acquisition_without_refs.process_file,
                    entry=self._acquisition_without_refs.entry,
                )
                # when copy dark and flats copy two refs, one at the beginning
                # (index 0) and one at the en (index n_proj)
                self.assertTrue(0 in copied_flats)
                self.assertTrue(9 in copied_flats)

                numpy.testing.assert_allclose(self.darks[0], copied_darks[0])
                numpy.testing.assert_allclose(self.flats[1], copied_flats[0])
                numpy.testing.assert_allclose(self.flats[1], copied_flats[0])


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestRefCopyEDF, TestRefCopyHDF5):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
    return test_suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
