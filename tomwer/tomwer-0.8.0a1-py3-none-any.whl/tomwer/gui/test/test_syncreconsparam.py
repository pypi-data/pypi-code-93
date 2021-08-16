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
__date__ = "16/06/2021"


import unittest
import pytest
from silx.gui import qt
from tomwer.core.process.reconstruction.darkref.params import Method as DkrfMethod
from tomwer.gui.reconstruction.ftserie import FtserieWidget
from tomwer.gui.reconstruction.darkref.darkrefcopywidget import DarkRefAndCopyWidget
from tomwer.synctools.ftseries import QReconsParams
from tomwer.test.utils import skip_gui_test


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestReconsParamFtSerieDarkRef(unittest.TestCase):
    """Test that the FtSerie and Dark Ref instances are synchronized
    both with the ReconsParam instance"""

    def setUp(self):
        self.recons_params = QReconsParams()
        self._ftserie = FtserieWidget(parent=None, recons_params=self.recons_params)
        self._darkRefCopy = DarkRefAndCopyWidget(
            parent=None, reconsparams=self.recons_params
        )
        self.qapp = qt.QApplication.instance() or qt.QApplication([])

    def tearDown(self):
        self._ftserie.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._darkRefCopy.setAttribute(qt.Qt.WA_DeleteOnClose)

    def testSync(self):
        """Make sure that connection between dkrf and ftserie are made.
        Some individual test (ftserie and ReconsParams) are also existing"""
        self._ftserie.show()
        self._darkRefCopy.show()
        ftserieEditor = self._ftserie.getReconsParamSetEditor()
        ftserieDKRf = ftserieEditor._dkRefWidget
        dkrfSkip = self._darkRefCopy.mainWidget.tabGeneral._skipOptionCB

        # test skipping option
        skipping = ftserieDKRf._qcbSkipRef.isChecked()
        self.assertTrue(dkrfSkip.isChecked() is skipping)
        self.assertTrue(self._ftserie.recons_params.dkrf["REFSOVE"] is not skipping)
        self.assertTrue(self._ftserie.recons_params.dkrf["DARKOVE"] is not skipping)
        ftserieDKRf._qcbSkipRef.setChecked(not skipping)
        self.qapp.processEvents()
        self.assertTrue(dkrfSkip.isChecked() is not skipping)
        self.assertTrue(self._ftserie.recons_params.dkrf["REFSOVE"] is skipping)
        self.assertTrue(self._ftserie.recons_params.dkrf["DARKOVE"] is skipping)

        # test dark pattern
        ftserieRef = ftserieEditor._dkRefWidget._qleDKPattern
        dkrfRef = self._darkRefCopy.mainWidget.tabExpert._darkLE
        self.assertTrue(dkrfRef.text() == ftserieRef.text())
        self.assertTrue(dkrfRef.text() == self._ftserie.recons_params.dkrf["DKFILE"])
        txt = dkrfRef.text()
        dkrfRef.setText(txt + "toto")
        dkrfRef.editingFinished.emit()
        self.qapp.processEvents()
        self.assertTrue(self.recons_params.dkrf["DKFILE"] == txt + "toto")
        self.assertTrue(dkrfRef.text() == ftserieRef.text())
        self.assertTrue(dkrfRef.text() == self._ftserie.recons_params.dkrf["DKFILE"])
        ftserieRef.setText(txt + "tata")
        ftserieRef.editingFinished.emit()
        self.assertTrue(dkrfRef.text() == ftserieRef.text())
        self.assertTrue(dkrfRef.text() == self._ftserie.recons_params.dkrf["DKFILE"])

        # test what ref
        ftserieWhatDark = ftserieEditor._dkRefWidget._qcbDKMode
        dkrfWhatDark = self._darkRefCopy.mainWidget.tabGeneral._darkWCB
        self.assertTrue(ftserieWhatDark.getMode() == dkrfWhatDark.getMode())
        for mode in DkrfMethod:
            ftserieWhatDark.setMode(mode)
            self.assertTrue(dkrfWhatDark.getMode() == mode)
            self.assertTrue(self._ftserie.recons_params.dkrf["DARKCAL"] == mode)
        for mode in DkrfMethod:
            dkrfWhatDark.setMode(mode)
            self.assertTrue(ftserieWhatDark.getMode() == mode)
            self.assertTrue(self._ftserie.recons_params.dkrf["DARKCAL"] == mode)
