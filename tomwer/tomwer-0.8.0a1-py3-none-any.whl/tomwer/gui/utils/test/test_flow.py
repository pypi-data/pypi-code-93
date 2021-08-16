# coding: utf-8
# /*##########################################################################
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
#############################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "05/02/2020"

from tomwer.test.utils import skip_gui_test
from tomwer.gui.utils.flow import FlowCanvas
from silx.gui.utils.testutils import TestCaseQt
from silx.gui import qt
import unittest


class ProcessClass:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


#
# @pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
# class TestFlowCanvas(TestCaseQt):
#     def setUp(self) -> None:
#         TestCaseQt.setUp(self)
#         self.widget = FlowCanvas(parent=None, direction="vertical")
#
#     def testFlow1(self):
#         self.widget.addProcess(process="preprocessing - step 1", icon=None, draggable=False)
#         self.widget.addProcess(process="preprocessing - step 2", icon=None, draggable=False)
#
#         for name in "process lambda", "process zeta", "process test":
#             self.widget.addProcess(process=name, icon=None)
#
#         style = qt.QApplication.style()
#
#         icon_1 = style.standardIcon(qt.QStyle.SP_DialogApplyButton)
#         icon_2 = style.standardIcon(qt.QStyle.SP_FileLinkIcon)
#
#         for name, icon in zip(("process_ico1", "process_ico2"), (icon_1, icon_2)):
#             self.widget.addProcess(process=name, icon=icon)
#
#         id_process_rm = self.widget.addProcess(process="process to remove")
#         self.widget.removeProcess(id_process_rm)
#
#         for proc_with_class in ("proc_class_1", "proc class b"):
#             self.widget.addProcess(process=ProcessClass(name=proc_with_class))
#
#         self.widget.addProcess(process="postprocessing - step 1", icon=None, draggable=False)
#
#         self.widget.show()
#         # TODO: test the getFlow function result
#
#
# def suite():
#     test_suite = unittest.TestSuite()
#     for ui in (TestFlowCanvas,):
#         test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
#     return test_suite
