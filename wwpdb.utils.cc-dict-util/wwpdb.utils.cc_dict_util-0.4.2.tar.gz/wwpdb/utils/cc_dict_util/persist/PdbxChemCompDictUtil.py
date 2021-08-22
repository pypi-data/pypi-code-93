##
# File: PdbxChemCompDictUtil.py
# Date: 21-Feb-2012  John Westbrook
#
# Update:
#    1-Feb-2017 jdw unified with chem_ref_data -
##
"""
A collection of classes supporting maintenance methods on chemical
dictionaries and  persistent stores.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
import os
import traceback

from mmcif_utils.persist.PdbxPersist import PdbxPersist
from mmcif_utils.persist.PdbxCoreIoAdapter import PdbxCoreIoAdapter as PdbxIoAdapter


class PdbxChemCompDictUtil(object):
    """Maintenance methods for creating and updating persistent stores of chemical dictionaries."""

    def __init__(self, verbose=True, log=sys.stderr):
        self.__verbose = verbose
        self.__debug = False
        self.__lfh = log

    def makeStoreFromFile(self, dictPath, storePath="chemcomp.db", minSize=10):
        """Create a new persistent store from input chemical dictionary file."""
        return self.__makeStoreFromFile(dictPath=dictPath, storePath=storePath, minSize=minSize)

    def makeStoreFromPathList(self, pathList, storePath="chemcomp.db"):
        """Create a new persistent store from a path list of chemical component definitions."""
        return self.__makeStoreFromPathList(pathList=pathList, storePath=storePath)

    def updateStoreByFile(self, pathList, storePath="chemcomp.db"):
        """Update the persistant store with the contents of the input path list"""
        return self.__updateStoreByFile(pathList, storePath=storePath)

    def updateStoreByObject(self, inpObject, containerName=None, containerType="data", storePath="chemcomp.db"):
        """Update the persistant store with the contents of the input object in the input named container."""
        return self.__updateStoreByObject(inpObject, containerName=containerName, containerType=containerType, storePath=storePath)

    def updateStoreByContainer(self, containerList, storePath="chemcomp.db"):
        """Update the persistant store with the contents of the input container list."""
        return self.__updateStoreByContainer(containerList=containerList, storePath=storePath)

    ##

    def __getFileSize(self, fPath):
        try:
            st = os.stat(fPath)
            return st.st_size
        except:  # noqa: E722 pylint: disable=bare-except
            return 0

    def __makeStoreFromFile(self, dictPath, storePath="chemcomp.db", minSize=10):
        """Internal method to create a new persistent store from input chemical dictionary file."""
        try:
            ok = False
            tmpPath = storePath + "-tmpstore"
            myReader = PdbxIoAdapter(self.__verbose, self.__lfh)
            ok = myReader.read(pdbxFilePath=dictPath)

            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            myPersist.setContainerList(myReader.getContainerList())
            myPersist.store(dbFileName=tmpPath)
            if self.__getFileSize(tmpPath) > minSize:
                myPersist.moveStore(tmpPath, storePath)
                ok = True
                # if (self.__debug):
                #   indexD = myPersist.getIndex(dbFileName=storePath)
                #   self.__lfh.write("Persistent index dictionary %r\n" % indexD.items())
            else:
                ok = False
            return ok
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__debug:
                traceback.print_exc(file=self.__lfh)
            return False

    def __makeStoreFromPathList(self, pathList, storePath="chemcomp.db", minSize=10):
        """Internal method to create a new persistent store from a path list
        of chemical component definitions.
        """
        try:
            ok = False
            # build the full container list from the input path list
            myReader = PdbxIoAdapter(self.__verbose, self.__lfh)
            for pth in pathList:
                ok = myReader.read(pdbxFilePath=pth)

            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            myPersist.setContainerList(myReader.getContainerList())

            if self.__verbose:
                self.__lfh.write("Read completed for %d definitions\n" % len(pathList))

            tmpPath = storePath + "-tmpstore"
            myPersist.store(dbFileName=tmpPath)
            if self.__getFileSize(tmpPath) > minSize:
                ok = True
                myPersist.moveStore(tmpPath, storePath)
                #
                # if (self.__debug):
                #   indexD = myPersist.getIndex(dbFileName=storePath)
            else:
                ok = False
            return ok
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__debug:
                traceback.print_exc(file=self.__lfh)
            return False

    def __updateStoreByFile(self, pathList, storePath="chemcomp.db"):
        """Internal method to update the persistant store with the contents of the input list of
        chemical component definition files.
        """
        try:
            myReader = PdbxIoAdapter(self.__verbose, self.__lfh)
            for rPath in pathList:
                _ok = myReader.read(pdbxFilePath=rPath)  # noqa: F841

                myPersist = PdbxPersist(self.__verbose, self.__lfh)
                myPersist.updateContainerList(dbFileName=storePath, containerList=myReader.getContainerList())
            #
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__debug:
                traceback.print_exc(file=self.__lfh)
            return False

    def __updateStoreByObject(self, inpObject, containerName=None, containerType="data", storePath="chemcomp.db"):
        """Internal method to update the persistant store with the contents of the input object in the input named container."""
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            myPersist.updateOneObject(inpObject, dbFileName=storePath, containerName=containerName, containerType=containerType)
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__debug:
                traceback.print_exc(file=self.__lfh)
            return False

    def __updateStoreByContainer(self, containerList, storePath="chemcomp.db"):
        """Internal method to update the persistant store with the contents of the input container list."""
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            myPersist.updateContainerList(dbFileName=storePath, containerList=containerList)
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__debug:
                traceback.print_exc(file=self.__lfh)
            return False
