##
# File: PdbxChemCompDictIndex.py
# Date: 21-Feb-2012  John Westbrook
#
# Update:
#
#  21-Apr-2013  jdw  Add indices of parent/child relationships for modified residues
#  17-Mar-2016  jdw  Update and move to chem_ref_data module -
#   1-Feb-2017  jdw  Move search functions to ChemCompIndexSearchUtils.py
#   1-Feb-2017  jdw  Unified with chem_ref_data -
#   1-Feb-2017  jdw  Expand index content
#   1-May-2017  jdw  Index all SMILES -
#
##
"""
A collection of classes for building simplified indices of the
serialized content in the chemical component dictionary.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
import traceback

try:
    import cPickle as pickle
except ImportError:
    import pickle

from mmcif_utils.persist.PdbxPersist import PdbxPersist
from wwpdb.utils.cc_dict_util.persist.PdbxChemCompPersist import PdbxChemCompIt, PdbxChemCompAtomIt, PdbxChemCompDescriptorIt, PdbxChemCompIdentifierIt


class PdbxChemCompDictIndex(object):
    """Builds simplified indices of the serialized content in the chemical component dictionary."""

    def __init__(self, verbose=True, log=sys.stderr):
        self.__verbose = verbose
        self.__debug = False
        self.__lfh = log

    def makeIndex(self, storePath="chemcomp.db", indexPath="chemcomp-index.pic"):
        """Create a search index from the contents of a persistent store of
        a chemical dictionary.  Store the index in indexPath.
        """
        return self.__makeIndex(storePath=storePath, indexPath=indexPath)

    def makeParentComponentIndex(self, storePath="chemcomp.db", indexPath="chemcomp-parent-index.pic"):
        """Create a search index for parent components from the contents of a persistent store of
        a chemical dictionary.  Store the index in indexPath.
        """
        return self.__makeParentIndex(storePath=storePath, indexPath=indexPath)

    def readIndex(self, indexPath="chemcomp-index.pic"):
        """Read and return search index."""
        return self.__readIndex(indexPath=indexPath)

    def readParentComponentIndex(self, indexPath="chemcomp-parent-index.pic"):
        """Read and return the parent component search index."""
        return self.__readParentIndex(indexPath=indexPath)

    def __makeIndex(self, storePath, indexPath):
        """Read serialized component dictionary and build a search index.

        Index is a dictionary of selected items such as name, synonyns, formula, status and
        descriptors.  Index is stored as a pickled dictionary.
        """
        ccIdx = {}
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            myPersist.open(dbFileName=storePath)
            containerList = myPersist.getStoreContainerIndex()
            #
            for ccId in containerList:
                #
                d = {}
                d["ccId"] = ccId
                d["nameList"] = []
                d["typeCounts"] = {}
                d["InChI"] = None
                d["InChIKey"] = None
                d["InChIKey14"] = None
                d["smiles"] = None
                d["smilesList"] = []
                d["smilesStereo"] = None
                d["releaseStatus"] = None
                d["subcomponentList"] = None
                #
                d["name"] = None
                d["type"] = None
                d["formula"] = None
                d["formulaWeight"] = None
                #
                nameList = []
                dC = myPersist.fetchObject(containerName=ccId, objectName="chem_comp")
                if dC is not None:
                    rowIt = PdbxChemCompIt(dC, self.__verbose, self.__lfh)
                    for row in rowIt:
                        name = row.getName()
                        synonyms = row.getSynonyms()
                        d["releaseStatus"] = row.getReleaseStatus()
                        d["subcomponentList"] = row.getSubComponentList()
                        d["name"] = name
                        d["synonyms"] = synonyms
                        d["type"] = row.getType()
                        d["formula"] = row.getFormula()
                        d["formulaWeight"] = row.getFormulaWeight()
                        d["ambiguousFlag"] = row.getAmbiguousFlag()

                    nameList.append(name)
                    if synonyms is not None:
                        if ";" in synonyms:
                            sList = synonyms.split(";")
                            nameList.extend(sList)
                        else:
                            nameList.append(synonyms)

                # Compute element/type counts directly from the definition atom list
                typeCounts = {}
                dC = myPersist.fetchObject(containerName=ccId, objectName="chem_comp_atom")
                if dC is not None:
                    rowIt = PdbxChemCompAtomIt(dC, self.__verbose, self.__lfh)
                    for row in rowIt:
                        aType = row.getType()
                        if row.getType() not in typeCounts:
                            typeCounts[aType] = 1
                        else:
                            typeCounts[aType] += 1
                    d["typeCounts"] = typeCounts

                #
                dC = myPersist.fetchObject(containerName=ccId, objectName="pdbx_chem_comp_descriptor")
                if dC is not None:
                    rowIt = PdbxChemCompDescriptorIt(dC, self.__verbose, self.__lfh)
                    for row in rowIt:
                        des = row.getDescriptor()
                        desType = row.getType()
                        desProgram = row.getProgram()
                        if desType.startswith("SMILES"):
                            d["smilesList"].append(des)
                        if "OpenEye" in desProgram:
                            if desType == "SMILES_CANNONICAL":
                                d["smilesStereo"] = des
                            elif desType == "SMILES":
                                d["smiles"] = des
                        elif "InChI" in desProgram:
                            if desType == "InChI":
                                d["InChI"] = des
                            elif desType == "InChIKey":
                                d["InChIKey"] = des
                                d["InChIKey14"] = des[:14]
                #

                dC = myPersist.fetchObject(containerName=ccId, objectName="pdbx_chem_comp_identifier")
                if dC is not None:
                    rowIt = PdbxChemCompIdentifierIt(dC, self.__verbose, self.__lfh)
                    for row in rowIt:
                        iden = row.getIdentifier()
                        idenType = row.getType()
                        # idenProgram = row.getProgram()
                        if "SYSTEMATIC" in idenType:
                            nameList.append(iden)

                d["nameList"] = nameList
                ccIdx[ccId] = d

            myPersist.close()
            with open(indexPath, "wb") as fout:
                # Maintain backwards compatibility with python 2
                pickle.dump(ccIdx, fout, 2)

        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("PdbxChemCompDictIndex(__makeIndex) index creation failed for %s index %s\n" % (storePath, indexPath))
            if self.__debug:
                traceback.print_exc(file=self.__lfh)

        return ccIdx

    def __makeParentIndex(self, storePath, indexPath):
        """Read serialized component dictionary and indices of parent/child relationships for modified residues.

        Index is stored as a pickled dictionary in indexPath.
        """
        pD = {}
        cD = {}
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            myPersist.open(dbFileName=storePath)
            containerList = myPersist.getStoreContainerIndex()
            #

            for ccId in containerList:
                #
                dC = myPersist.fetchObject(containerName=ccId, objectName="chem_comp")
                if dC is not None:
                    rowIt = PdbxChemCompIt(dC, self.__verbose, self.__lfh)
                    for row in rowIt:
                        pCompId = row.getNstdParentId()
                        compId = row.getId()
                        #
                        if (pCompId is not None) and (len(pCompId) > 0) and (pCompId not in ["?", "."]):

                            if "," in pCompId:
                                pList = pCompId.split(",")
                                cD[compId] = pList
                            else:
                                if len(pCompId) > 3:
                                    self.__lfh.write("PdbxChemCompDictIndex(__makeParentIndex) compId %s parent compId %s\n" % (compId, pCompId))
                                else:
                                    pList = [pCompId]
                                    if pCompId not in pD:
                                        pD[pCompId] = []
                                    pD[pCompId].append(compId)
                                    #
                                    cD[compId] = pList

            myPersist.close()
            #
            ofh = open(indexPath, "wb")
            # Compatbility with python 2 and not pickle.HIGHEST_PROTOCOL
            pickle.dump(pD, ofh, 2)
            pickle.dump(cD, ofh, 2)
            ofh.close()

        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("PdbxChemCompDictIndex(__makeParentIndex) parent index creation failed for %s index %s\n" % (storePath, indexPath))
            if self.__debug:
                traceback.print_exc(file=self.__lfh)

        return pD, cD

    def __readParentIndex(self, indexPath):
        """Internal method to recover the pickled index file."""
        pD = {}
        cD = {}
        try:
            ifh = open(indexPath, "rb")
            pD = pickle.load(ifh)
            cD = pickle.load(ifh)
            ifh.close()
            return pD, cD
        except:  # noqa: E722 pylint: disable=bare-except
            pass
        return pD, cD

    def __readIndex(self, indexPath):
        """Internal method to recover the pickled index file."""
        try:
            with open(indexPath, "rb") as fin:
                return pickle.load(fin)
        except:  # noqa: E722 pylint: disable=bare-except
            return {}
