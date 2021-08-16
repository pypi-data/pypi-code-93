# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
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
__date__ = "09/06/2017"

import os
import shutil
import tempfile
import time
import unittest
import pytest
from silx.gui.utils.testutils import TestCaseQt
from silx.gui import qt

from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.gui.control.datawatcher import DataWatcherWidget
from tomwer.gui.control.datawatcher.datawatcherobserver import _QDataWatcherFixObserver
from tomwer.gui.control.datawatcher.datawatcherobserver import _QDataWatcherObserver
from tomwer.gui.control.datawatcher.datawatcherobserver import _QOngoingObservation
from tomwer.core.process.control.datawatcher import status as datawatcherstatus
from tomwer.synctools.rsyncmanager import RSyncManager
from tomwer.test.utils import UtilsTest
from tomwer.test.utils import skip_gui_test


@unittest.skip("Fail on CI...")
@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestDataWatcherDirObserver(TestCaseQt):
    """
    Simple test to make sure the timeout of data watcher is working properly
    """

    FOLDER_WITH_DATA = 4

    FOLDER_WITHOUT_DATA = 3

    def setUp(self):
        TestCaseQt.setUp(self)
        self.observeFolder = tempfile.mkdtemp()

        self.dataSetID = "test10"
        dataDir = UtilsTest.getEDFDataset(self.dataSetID)
        for iFolder in range(self.FOLDER_WITH_DATA):
            shutil.copytree(
                dataDir,
                os.path.join(self.observeFolder, "f" + str(iFolder), self.dataSetID),
            )

        for iFolder in range(self.FOLDER_WITHOUT_DATA):
            os.makedirs(os.path.join(self.observeFolder, "empty" + str(iFolder)))

        # observer
        self.observer = _QDataWatcherObserver(
            headDir=self.observeFolder,
            startByOldest=False,
            obsMethod=datawatcherstatus.DET_END_XML,
            srcPattern=None,
            destPattern=None,
            observationClass=_QOngoingObservation,
        )

    def tearDown(self):
        self.observer.wait()
        self.observer = None
        if os.path.isdir(self.observeFolder):
            shutil.rmtree(self.observeFolder)
        TestCaseQt.tearDown(self)

    def testRun(self):
        self.observer.run()
        self.assertTrue(len(self.observer.observations) is self.FOLDER_WITH_DATA)
        self.observer.waitForObservationFinished(4)


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestDataWatcherFixObserver(TestCaseQt):
    def setUp(self):
        TestCaseQt.setUp(self)

        self.observeFolder = tempfile.mkdtemp()
        self.dataSetID = "test10"
        dataDir = UtilsTest.getEDFDataset(self.dataSetID)
        shutil.copytree(dataDir, os.path.join(self.observeFolder, self.dataSetID))

        self.thread = _QDataWatcherFixObserver(
            scanID=os.path.join(self.observeFolder, self.dataSetID),
            obsMethod=datawatcherstatus.DET_END_XML,
            srcPattern=None,
            destPattern=None,
            patternObs=None,
            observationRegistry=None,
        )

    def tearDown(self):
        self.thread.wait()
        self.thread = None
        shutil.rmtree(self.observeFolder)
        TestCaseQt.tearDown(self)

    def testRunOk(self):
        self.thread.start()
        self.thread.wait(5)

    def testFolderNotExisting(self):
        self.thread.setDirToObserve("toto/pluto")
        self.thread.start()
        self.thread.wait(5)
        self.assertEqual(
            self.thread.status, "failure", msg="status is %s" % self.thread.status
        )

    def testRunWaitingXML(self):
        fileXML = os.path.join(
            self.thread.dataWatcherProcess.RootDir, self.dataSetID + ".xml"
        )
        assert os.path.isfile(fileXML)
        os.remove(fileXML)
        self.thread.start()
        self.thread.wait(5)


class _ObservationCounter(qt.QObject):
    """Basically simulate the next box which has to receive some signal to
    process"""

    def __init__(self):
        qt.QObject.__init__(self)
        self.scansCounted = 0
        self.scansID = []

    def add(self, scanID):
        self.scansCounted = self.scansCounted + 1
        if scanID.path not in self.scansID:
            self.scansID.append(scanID.path)

    def getReceivedScan(self):
        return self.scansCounted

    def getDifferentScanReceived(self):
        return len(self.scansID)

    def clear(self):
        self.scansID = []
        self.scansCounted = 0


@unittest.skip("Fail on CI...")
@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestDataWatcher(TestCaseQt):
    """
    Make sur the DataWatcher process is valid
    """

    WAIT_BTW_LOOP = 0.1

    def setUp(self):
        TestCaseQt.setUp(self)
        # create a folder with an unfinished acquisition
        self.observeFolder = tempfile.mkdtemp()

        self.dataSetIDs = "test10", "test01"
        for scanID in self.dataSetIDs:
            dataDir = UtilsTest.getEDFDataset(scanID)
            shutil.copytree(dataDir, os.path.join(self.observeFolder, scanID))

        self.observationCounter = _ObservationCounter()

        # data watcher
        self.dataWatcher = DataWatcherWidget()
        self.dataWatcher.setFolderObserved(self.observeFolder)
        self.dataWatcher.obsMethod = datawatcherstatus.DET_END_XML
        self.dataWatcher.setSrcAndDestPattern(srcPattern=None, destPattern=None)
        self.dataWatcher.setWaitTimeBtwLoop(self.WAIT_BTW_LOOP)
        self.dataWatcher.sigScanReady.connect(self.observationCounter.add)

    def tearDown(self):
        self.dataWatcher.stop()
        self.dataWatcher = None
        if os.path.isdir(self.observeFolder):
            shutil.rmtree(self.observeFolder)
        TestCaseQt.tearDown(self)

    def testInfinity(self):
        """
        Test that if we ar ein the infinity mode and two acquisitions are
        existing we will found only those two observations once and that the
        datawatcher object is still observing
        """
        self.observationCounter.clear()

        self.dataWatcher.start()
        self.qapp.processEvents()
        time.sleep(self.WAIT_BTW_LOOP * 2.0)  # make sure no multiple signal are emitted
        self.qapp.processEvents()
        time.sleep(0.4)
        self.qapp.processEvents()
        self.dataWatcher.waitForObservationFinished()
        self.assertTrue(self.dataWatcher.observationThread is not None)
        self.assertTrue(len(self.dataWatcher.lastFoundScans) == 2)
        self.assertTrue(self.observationCounter.getReceivedScan() == 2)
        self.assertTrue(self.observationCounter.getDifferentScanReceived() == 2)
        self.dataWatcher.stop()

    def testPatternFileObsMethod(self):
        """
        Test the DET_END_USER_ENTRY observation method.
        Will look for a file pattern given by the user in the scan directory
        """

        def tryPattern(pattern, filePrefix, fileSuffix):
            self.dataWatcher.stop()
            self.observationCounter.clear()

            self.dataWatcher.setObsMethod(
                (datawatcherstatus.DET_END_USER_ENTRY, {"pattern": pattern})
            )

            tempfile.mkdtemp(
                prefix=filePrefix,
                suffix=fileSuffix,
                dir=os.path.join(self.observeFolder, "test10"),
            )

            self.assertEqual(self.observationCounter.getDifferentScanReceived(), 0)

            self.dataWatcher.start()
            self.dataWatcher.waitForObservationFinished()
            self.qapp.processEvents()
            time.sleep(0.4)
            self.qapp.processEvents()

            return self.observationCounter.getDifferentScanReceived() == 1

        self.assertTrue(
            tryPattern(
                pattern="*tatayoyo*.cfg", filePrefix="tatayoyo", fileSuffix=".cfg"
            )
        )

        self.assertFalse(
            tryPattern(pattern="*tatayoyo*.cfg", filePrefix="tatayoyo", fileSuffix="")
        )

        self.assertFalse(
            tryPattern(pattern="tatayoyo.cfg", filePrefix="tatayoyo", fileSuffix=".cfg")
        )


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestDataWatcherAborted(TestCaseQt):
    """Test behavior of the DataWatcher when some acquisition are aborted"""

    def setUp(self):
        TestCaseQt.setUp(self)
        # create a folder with an unfinished acquisition
        self.observeFolder = tempfile.mkdtemp()

        # data watcher
        self.dataWatcher = DataWatcherWidget()
        self.dataWatcher.setFolderObserved(self.observeFolder)
        self.dataWatcher.obsMethod = datawatcherstatus.DET_END_XML
        self.dataWatcher.setSrcAndDestPattern(srcPattern=None, destPattern=None)

        self.dataDir01 = UtilsTest.getEDFDataset("test01")
        self.dataDir10 = UtilsTest.getEDFDataset("test10")

        RSyncManager().force_sync = False

    def tearDown(self):
        self.dataWatcher.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.dataWatcher.stop()
        self.dataWatcher = None
        if os.path.exists(self.observeFolder):
            shutil.rmtree(self.observeFolder)
        TestCaseQt.tearDown(self)

    def testAbortedFindNext(self):
        """Make sure if an acquisition is aborted then we will skip it
        and that the NEXT acquisition will be found"""
        self.dataWatcher.setWaitTimeBtwLoop(0.1)
        self.assertEqual(len(self.dataWatcher.getIgnoredFolders()), 0)

        dirTest01 = os.path.join(self.observeFolder, "test01")
        shutil.copytree(self.dataDir01, dirTest01)
        # add the `abort file`
        open(os.path.join(dirTest01, "test01" + EDFTomoScan.ABORT_FILE), "a")
        self.dataWatcher.start()
        self.dataWatcher.observationThread.wait()
        self.qapp.processEvents()
        self.assertEqual(len(self.dataWatcher.getIgnoredFolders()), 0)
        self.assertTrue(self.dataWatcher.isObserving is True)
        dirTest10 = os.path.join(self.observeFolder, "test10")
        shutil.copytree(self.dataDir10, dirTest10)

        for i in range(6):
            self.qapp.processEvents()
            time.sleep(0.1)
        self.assertEqual(len(self.dataWatcher.lastFoundScans), 1)
        self.assertTrue(dirTest10 in self.dataWatcher.lastFoundScans)

    def testAbortedFindPrevious(self):
        """Make sure if an acquisition is aborted then we will skip it
        and that the PREVIOUS acquisition will be found"""
        self.dataWatcher.setWaitTimeBtwLoop(0.1)
        self.assertEqual(len(self.dataWatcher.getIgnoredFolders()), 0)

        dirTest10 = os.path.join(self.observeFolder, "test10")
        shutil.copytree(self.dataDir10, dirTest10)
        dirTest01 = os.path.join(self.observeFolder, "test01")
        shutil.copytree(self.dataDir01, dirTest01)
        # add the `abort file`
        open(os.path.join(dirTest01, "test01" + EDFTomoScan.ABORT_FILE), "a")
        self.dataWatcher.start()
        self.dataWatcher.observationThread.wait()
        self.qapp.processEvents()
        self.assertTrue(self.dataWatcher.isObserving is True)
        time.sleep(0.2)
        self.qapp.processEvents()
        time.sleep(0.2)
        self.qapp.processEvents()
        self.assertEqual(len(self.dataWatcher.lastFoundScans), 1)
        self.assertTrue(dirTest10 in self.dataWatcher.lastFoundScans)

    def testAbortedWhenWaitingFor(self):
        """
        Make sure will skip the scan if aborted even if observation started
        """
        self.dataWatcher.setWaitTimeBtwLoop(0.1)
        self.assertEqual(len(self.dataWatcher.getIgnoredFolders()), 0)

        dirTest01 = os.path.join(self.observeFolder, "test01")
        shutil.copytree(self.dataDir01, dirTest01)
        self.dataWatcher.start()
        # add the `abort file`
        open(os.path.join(dirTest01, "test01" + EDFTomoScan.ABORT_FILE), "a")
        self.dataWatcher.observationThread.wait()
        self.qapp.processEvents()
        self.assertEqual(len(self.dataWatcher.getIgnoredFolders()), 0)
        self.assertTrue(self.dataWatcher.isObserving)
        dirTest10 = os.path.join(self.observeFolder, "test10")
        shutil.copytree(self.dataDir10, dirTest10)
        self.qapp.processEvents()
        time.sleep(0.2)
        self.qapp.processEvents()
        self.assertEqual(len(self.dataWatcher.lastFoundScans), 1)
        self.assertTrue(dirTest10 in self.dataWatcher.lastFoundScans)

    def testAbortedRemovingFolder(self):
        """Make sure the aborted folder is removed after found by datawatcher"""
        RSyncManager().force_sync = True
        self.dataWatcher.setWaitTimeBtwLoop(0.1)
        dirTest01 = os.path.join(self.observeFolder, "test01")
        shutil.copytree(self.dataDir01, dirTest01)
        # add the `abort file`
        open(os.path.join(dirTest01, "test01" + EDFTomoScan.ABORT_FILE), "a")
        self.dataWatcher.start()
        self.dataWatcher.observationThread.wait()
        assert dirTest01 in self.dataWatcher.observationThread.observations.dict
        obs = self.dataWatcher.observationThread.observations.dict[dirTest01]
        obs.wait()
        self.assertFalse(os.path.exists(dirTest01))
