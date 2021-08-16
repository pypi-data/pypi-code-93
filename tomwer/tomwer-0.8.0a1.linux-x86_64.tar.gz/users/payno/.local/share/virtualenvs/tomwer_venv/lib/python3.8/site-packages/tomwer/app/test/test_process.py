# # coding: utf-8
# # /*##########################################################################
# #
# # Copyright (c) 2017 European Synchrotron Radiation Facility
# #
# # Permission is hereby granted, free of charge, to any person obtaining a copy
# # of this software and associated documentation files (the "Software"), to deal
# # in the Software without restriction, including without limitation the rights
# # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # copies of the Software, and to permit persons to whom the Software is
# # furnished to do so, subject to the following conditions:
# #
# # The above copyright notice and this permission notice shall be included in
# # all copies or substantial portions of the Software.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# # THE SOFTWARE.
# #
# # ###########################################################################*/
#
# __authors__ = ["H. Payno"]
# __license__ = "MIT"
# __date__ = "31/07/2020"
#
#
# import unittest
# from tomwer.test.utils import UtilsTest
# import h5py
# import shutil
# import tempfile
# from tomwer.core.utils.scanutils import MockBlissAcquisition
# from tomwer.core.scan.blissscan import BlissScan
# from tomwer.core.scan.hdf5scan import HDF5TomoScan
# from pypushflow.representation.scheme.ows_parser import OwsParser
# from tomwer.core.process.reconstruction.nabu import settings as nabu_settings
# from silx.io.utils import h5py_read_dataset
# from ..process import _exec
# from glob import glob
# import os
#
#
# class TestNxTomoDarkRef(unittest.TestCase):
#     """
#     Test the execution of the following workflow:
#     nxtomomill -> dark and flat field
#     uses:
#
#     - 'nxtomomill_darkref.ows': where dark is not computed and ref is average
#     - 'nxtomomill_darkref_2.ows': where dark is average and ref is median
#     """
#
#     TIMEOUT = 120
#
#     def setUp(self) -> None:
#         unittest.TestCase.setUp(self)
#         self._data_dir = tempfile.mkdtemp()
#         self._bliss_mock = MockBlissAcquisition(
#             n_sample=1,
#             n_sequence=1,
#             n_darks=10,
#             n_flats=10,
#             n_scan_per_sequence=2,
#             output_dir=self._data_dir,
#         )
#         self.master_file = self._bliss_mock.samples[0].sample_file
#         assert os.path.exists(self.master_file)
#         self.bliss_scan = BlissScan(
#             master_file=self.master_file, entry="/1.1", proposal_file=None
#         )
#         self.tomwer_file = os.path.join(
#             self._bliss_mock.samples[0].path, "tomwer_processes.h5"
#         )
#
#     @staticmethod
#     def get_scheme(file_path):
#         return OwsParser.scheme_load(file_path, load_handlers=True)
#
#     def tearDown(self) -> None:
#         if os.path.isdir(self._data_dir):
#             shutil.rmtree(self._data_dir)
#
#     def testProcessing_1(self):
#         self.assertFalse(os.path.exists(self.tomwer_file))
#         scheme_file = UtilsTest.getOrangeExecTestFile("nxtomomill_darkref.ows")
#         self.scheme = self.get_scheme(scheme_file)
#         _exec(scheme=self.scheme, scan=self.bliss_scan, timeout=self.TIMEOUT)
#         self.assertTrue(os.path.exists(self.tomwer_file))
#         with h5py.File(self.tomwer_file, "r") as h5s:
#             self.assertTrue("entry0000" in h5s)
#             self.assertTrue("entry0000/tomwer_process_0/results/flats" in h5s)
#             self.assertTrue(
#                 h5s["entry0000/tomwer_process_0/results/flats/100"].shape, (2560, 2160)
#             )
#             self.assertFalse("entry0000/tomwer_process_0/results/darks" in h5s)
#
#     def testProcessing_2(self):
#         self.assertFalse(os.path.exists(self.tomwer_file))
#         scheme_file = UtilsTest.getOrangeExecTestFile("nxtomomill_darkref_2.ows")
#         self.scheme = self.get_scheme(scheme_file)
#         _exec(scheme=self.scheme, scan=self.bliss_scan, timeout=self.TIMEOUT)
#         self.assertTrue(os.path.exists(self.tomwer_file))
#         with h5py.File(self.tomwer_file, "r") as h5s:
#             self.assertTrue("entry0000" in h5s)
#             self.assertTrue("entry0000/tomwer_process_0/results/flats" in h5s)
#             self.assertTrue(
#                 h5s["entry0000/tomwer_process_0/results/flats/100"].shape, (2560, 2160)
#             )
#             self.assertTrue("entry0000/tomwer_process_0/results/darks" in h5s)
#             self.assertTrue(
#                 h5s["entry0000/tomwer_process_0/results/darks/0"].shape, (2560, 2160)
#             )
#
#
# class TestDarkRefAxisNabu(unittest.TestCase):
#     """
#     Test the execution of the following workflow:
#     dark and flat field -> center of rotation -> nabu reconstruction
#     uses:
#
#     - 'darkref_axis_nabu.ows'
#         - dark: average, ref: median
#         - cor: manual at 70
#         - nabu: reconstruct slice 20
#     - 'darkref_axis_nabu_2.ows'
#         - dark: average, ref: median
#         - cor: use centered (value should be ~79)
#         - nabu: reconstruct middle slice (1080)
#     """
#
#     TIMEOUT = 120
#
#     def setUp(self) -> None:
#         unittest.TestCase.setUp(self)
#         self._data_dir = tempfile.mkdtemp()
#         self.master_file = os.path.join(self._data_dir, "frm_edftomomill_twoentries.nx")
#         self.tomwer_file = os.path.join(
#             self._data_dir, "frm_edftomomill_twoentries_tomwer_processes.h5"
#         )
#
#         shutil.copyfile(
#             UtilsTest.getH5Dataset(folderID="frm_edftomomill_twoentries.nx"),
#             self.master_file,
#         )
#         self.scan = HDF5TomoScan(scan=self.master_file, entry="entry0000")
#         self._nabu_cfg_folder = os.path.join(
#             self.scan.path, nabu_settings.NABU_CFG_FILE_FOLDER
#         )
#
#     @staticmethod
#     def get_scheme(file_path):
#         return OwsParser.scheme_load(file_path, load_handlers=True)
#
#     def tearDown(self) -> None:
#         if os.path.isdir(self._data_dir):
#             shutil.rmtree(self._data_dir)
#
#     def testProcessing_1(self):
#         self.assertFalse(os.path.exists(self.tomwer_file))
#         self.assertEqual(len(glob(self._nabu_cfg_folder + os.sep + "*.cfg")), 0)
#         scheme_file = UtilsTest.getOrangeExecTestFile("darkref_axis_nabu.ows")
#         self.scheme = self.get_scheme(scheme_file)
#         # monkey patch parameters to use nabu in dry tun mode
#         self.scheme.nodes[2].properties["_rpSetting"]["dry_run"] = True
#         _exec(scheme=self.scheme, scan=self.scan, timeout=self.TIMEOUT)
#         self.assertTrue(os.path.exists(self.tomwer_file))
#         with h5py.File(self.tomwer_file, "r") as h5s:
#             # check darks
#             self.assertTrue("entry0000" in h5s)
#             self.assertTrue("entry0000/tomwer_process_0/results/flats" in h5s)
#             self.assertTrue(
#                 h5s["entry0000/tomwer_process_0/results/flats/1"].shape, (2560, 2160)
#             )
#             self.assertTrue("entry0000/tomwer_process_0/results/darks" in h5s)
#             self.assertTrue(
#                 h5s["entry0000/tomwer_process_0/results/darks/0"].shape, (2560, 2160)
#             )
#             # check axis
#             self.assertEqual(
#                 h5py_read_dataset(h5s["entry0000/tomwer_process_1/program"]),
#                 "tomwer_axis",
#             )
#             self.assertAlmostEqual(
#                 h5py_read_dataset(
#                     h5s["entry0000/tomwer_process_1/results/center_of_rotation"]
#                 ),
#                 70.0,
#                 places=4,
#             )
#
#             # check nabu
#             self.assertEqual(
#                 h5py_read_dataset(h5s["entry0000/tomwer_process_2/program"]),
#                 "nabu-slices",
#             )
#             axp = h5py_read_dataset(
#                 h5s[
#                     "entry0000/tomwer_process_2/configuration/reconstruction/rotation_axis_position"
#                 ]
#             )
#             self.assertAlmostEqual(float(axp), (10.0 + 70.0), places=4)
#             # +10: moved to nabu system (half width
#         # check nabu files
#         self.assertEqual(len(glob(self._nabu_cfg_folder + os.sep + "*.cfg")), 2)
#
#     def testProcessing_2(self):
#         self.assertFalse(os.path.exists(self.tomwer_file))
#         self.assertEqual(len(glob(self._nabu_cfg_folder + os.sep + "*.cfg")), 0)
#
#         scheme_file = UtilsTest.getOrangeExecTestFile("darkref_axis_nabu_2.ows")
#         self.scheme = self.get_scheme(scheme_file)
#         # monkey patch parameters to use nabu in dry tun mode
#         self.scheme.nodes[2].properties["_rpSetting"]["dry_run"] = True
#
#         _exec(scheme=self.scheme, scan=self.scan, timeout=self.TIMEOUT)
#         self.assertTrue(os.path.exists(self.tomwer_file))
#         with h5py.File(self.tomwer_file, "r") as h5s:
#             # check darks
#             self.assertTrue("entry0000" in h5s)
#             self.assertTrue("entry0000/tomwer_process_0/results/flats" in h5s)
#             self.assertTrue(
#                 h5s["entry0000/tomwer_process_0/results/flats/1"].shape, (2560, 2160)
#             )
#             self.assertTrue("entry0000/tomwer_process_0/results/darks" in h5s)
#             self.assertTrue(
#                 h5s["entry0000/tomwer_process_0/results/darks/0"].shape, (2560, 2160)
#             )
#             # check axis
#             self.assertEqual(
#                 h5py_read_dataset(h5s["entry0000/tomwer_process_1/program"]),
#                 "tomwer_axis",
#             )
#             axis_cor = h5py_read_dataset(
#                 h5s["entry0000/tomwer_process_1/results/center_of_rotation"]
#             )
#
#             # check nabu
#             self.assertEqual(
#                 h5py_read_dataset(h5s["entry0000/tomwer_process_2/program"]),
#                 "nabu-slices",
#             )
#             axp = h5py_read_dataset(
#                 h5s[
#                     "entry0000/tomwer_process_2/configuration/reconstruction/rotation_axis_position"
#                 ]
#             )
#             self.assertAlmostEqual(float(axp), (10.0 + axis_cor), places=4)
#             # +10: moved to nabu system (half width
#         # check nabu files
#         self.assertEqual(len(glob(self._nabu_cfg_folder + os.sep + "*.cfg")), 2)
#
#
# class TestPythonScript(unittest.TestCase):
#     """
#     Test the execution of the following workflow:
#     Data list -> Python script test -> Python script test 2
#
#     Data list will be ignored
#     The first scripts create a 'test.txt' file at the root level
#     The second scripts create a 'test2.txt' file at the root level
#
#     Make sure the code is correctly executed and that it.
#     """
#
#     TIMEOUT = 120
#
#     def setUp(self) -> None:
#         unittest.TestCase.setUp(self)
#         self._data_dir = tempfile.mkdtemp()
#         self.master_file = os.path.join(self._data_dir, "frm_edftomomill_twoentries.nx")
#         self.tomwer_file = os.path.join(self._data_dir, "tomwer_processes.h5")
#
#         shutil.copyfile(
#             UtilsTest.getH5Dataset(folderID="frm_edftomomill_twoentries.nx"),
#             self.master_file,
#         )
#         self.scan = HDF5TomoScan(scan=self.master_file, entry="entry0000")
#
#     @staticmethod
#     def get_scheme(file_path):
#         return OwsParser.scheme_load(file_path, load_handlers=True)
#
#     def tearDown(self) -> None:
#         if os.path.isdir(self._data_dir):
#             shutil.rmtree(self._data_dir)
#
#     def testProcessing(self):
#         self.assertEqual(len(glob(self.scan.path + os.sep + "test*.txt")), 0)
#         scheme_file = UtilsTest.getOrangeExecTestFile("test_tomwer_python_scripts.ows")
#         self.scheme = self.get_scheme(scheme_file)
#         _exec(scheme=self.scheme, scan=self.scan, timeout=self.TIMEOUT)
#         self.assertEqual(len(glob(self.scan.path + os.sep + "test*.txt")), 2)
#
#
# def suite():
#     test_suite = unittest.TestSuite()
#     for ui in (TestNxTomoDarkRef, TestDarkRefAxisNabu, TestPythonScript):
#         test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
#     return test_suite
#
#
# if __name__ == "__main__":
#     unittest.main(defaultTest="suite")
