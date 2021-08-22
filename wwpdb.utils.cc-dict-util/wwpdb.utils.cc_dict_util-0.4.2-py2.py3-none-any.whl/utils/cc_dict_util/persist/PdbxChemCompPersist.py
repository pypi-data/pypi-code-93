##
# File: PdbxChemCompPersist.py
# Date: 20-Feb-2012  John Westbrook
#
# Update:
#  21-Feb-2012 jdw adapted for chemcomputil repository
#  23-Feb-2012 jdw adapted for cc_dict_util repository
#   1-Feb-2017 jdw update imports to pdbx_v2
##
"""
A collection of access and iterator classes supporting chemical component dictionary data
extracted from persistent store.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys

# import traceback

from wwpdb.utils.cc_dict_util.persist.PdbxChemCompConstants import PdbxChemCompConstants


class PdbxCategoryItBase(object):
    """Base category iterator class."""

    def __init__(self, dataCategory, func, verbose=True, log=sys.stderr):  # pylint: disable=unused-argument
        self.__rL = dataCategory.getRowList()
        self.__func = func

    def get(self, index=0):
        try:
            return self.__rL[index]
        except:  # noqa: E722 pylint: disable=bare-except
            return []

    def __iter__(self):
        return self.forward()

    def forward(self):
        # Forward generator
        current_row = 0
        while current_row < len(self.__rL):
            row = self.__rL[current_row]
            current_row += 1
            yield self.__func(row)

    def reverse(self):
        # The reverse generator
        current_row = len(self.__rL)
        while current_row > 0:
            current_row -= 1
            yield self.__func(self.__rL[current_row])


class PdbxChemCompIt(PdbxCategoryItBase):
    def __init__(self, dataCategory, verbose=True, log=sys.stderr):
        o = PdbxChemCompPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompAtomIt(PdbxCategoryItBase):
    def __init__(self, dataCategory, verbose=True, log=sys.stderr):
        o = PdbxChemCompAtomPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompAtomIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompBondIt(PdbxCategoryItBase):
    def __init__(self, dataCategory, verbose=True, log=sys.stderr):
        o = PdbxChemCompBondPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompBondIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompDescriptorIt(PdbxCategoryItBase):
    def __init__(self, dataCategory, verbose=True, log=sys.stderr):
        o = PdbxChemCompDescriptorPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompDescriptorIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompIdentifierIt(PdbxCategoryItBase):
    def __init__(self, dataCategory, verbose=True, log=sys.stderr):
        o = PdbxChemCompIdentifierPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompIdentifierIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompAuditIt(PdbxCategoryItBase):
    def __init__(self, dataCategory, verbose=True, log=sys.stderr):
        o = PdbxChemCompAuditPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompAuditIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompPersist(object):
    """Accessor methods chemical component attributes."""

    def __init__(self, rowData, attributeNameList, verbose=True, log=sys.stderr):  # pylint: disable=unused-argument
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def set(self, rowData=None):
        self.__rowData = rowData
        return self

    def __getAttribute(self, name):
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getId(self):
        return self.__getAttribute("id")

    def getName(self):
        return self.__getAttribute("name")

    def getType(self):
        return self.__getAttribute("type")

    def getPdbxType(self):
        return self.__getAttribute("pdbx_type")

    def getFormula(self):
        return self.__getAttribute("formula")

    def getSynonyms(self):
        return self.__getAttribute("pdbx_synonyms")

    def getFormalCharge(self):
        return self.__getAttribute("pdbx_formal_charge")

    def getModificationDate(self):
        return self.__getAttribute("pdbx_modified_date")

    def getInitialDate(self):
        return self.__getAttribute("pdbx_initial_date")

    def getReleaseStatus(self):
        return self.__getAttribute("pdbx_release_status")

    def getFormulaWeight(self):
        return self.__getAttribute("formula_weight")

    def getSubComponentList(self):
        return self.__getAttribute("pdbx_subcomponent_list")

    def getAmbiguousFlag(self):
        return self.__getAttribute("pdbx_ambiguous_flag")

    def getProcessingSite(self):
        return self.__getAttribute("pdbx_processing_site")

    def getReplacesId(self):
        return self.__getAttribute("pdbx_replaces")

    def getReplacesById(self):
        return self.__getAttribute("pdbx_replaced_by")

    def getNstdParentId(self):
        return self.__getAttribute("mon_nstd_parent_comp_id")

    def getOneLetterCode(self):
        return self.__getAttribute("one_letter_code")

    def getThreeLetterCode(self):
        return self.__getAttribute("three_letter_code")

    def getModelCoordinatesPdbCode(self):
        return self.__getAttribute("pdbx_model_coordinates_db_code")

    def getMissingModelCoordinates(self):
        return self.__getAttribute("pdbx_model_coordinates_missing_flag")

    def getMissingIdealCoordinates(self):
        return self.__getAttribute("pdbx_ideal_coordinates_missing_flag")


class PdbxChemCompAtomPersist(PdbxChemCompConstants):
    """Accessor methods chemical component atom attributes."""

    def __init__(self, rowData, attributeNameList, verbose=True, log=sys.stderr):  # pylint: disable=unused-argument
        super(PdbxChemCompAtomPersist, self).__init__()
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name):
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData=None):
        self.__rowData = rowData
        return self

    def getName(self):
        return self.__getAttribute("atom_id")

    def isChiral(self):
        return self.__getAttribute("pdbx_stereo_config") != "N"

    def getType(self):
        return self.__getAttribute("type_symbol")

    def getLeavingAtomFlag(self):
        return self.__getAttribute("pdbx_leaving_atom_flag")

    def getAtNo(self):
        try:
            tyU = str(self.getType()).upper()
            if (tyU == "D") or (tyU == "T"):
                tyU = "H"
            return self._periodicTable.index(tyU) + 1
        except:  # noqa: E722 pylint: disable=bare-except
            # traceback.print_exc(file=self.__lfh)
            return 0

    def getIsotope(self):
        ty = self.getType()
        if ty == "D":
            return 2
        elif ty == "T":
            return 3
        else:
            return 0

    def isAromatic(self):
        return self.__getAttribute("pdbx_aromatic_flag") != "N"

    def getCIPStereo(self):
        return self.__getAttribute("pdbx_stereo_config")

    def getFormalCharge(self):
        try:
            return int(self.__getAttribute("charge"))
        except:  # noqa: E722 pylint: disable=bare-except
            return 0

    def hasModelCoordinates(self):
        x, y, z = self.getModelCoordinates()
        # x=self.__getAttribute('model_Cartn_x')
        # y=self.__getAttribute('model_Cartn_y')
        # z=self.__getAttribute('model_Cartn_z')
        #
        return (x is not None) and (y is not None) and (z is not None)

    def hasIdealCoordinates(self):
        x, y, z = self.getIdealCoordinates()
        # x=self.__getAttribute('pdbx_model_Cartn_x_ideal')
        # y=self.__getAttribute('pdbx_model_Cartn_y_ideal')
        # z=self.__getAttribute('pdbx_model_Cartn_z_ideal')
        #
        return (x is not None) and (y is not None) and (z is not None)

    def getModelCoordinates(self):
        """Returns (x,y,z)"""
        try:
            x = float(self.__getAttribute("model_Cartn_x"))
            y = float(self.__getAttribute("model_Cartn_y"))
            z = float(self.__getAttribute("model_Cartn_z"))
            return (x, y, z)
        except:  # noqa: E722 pylint: disable=bare-except
            return (None, None, None)

    def getIdealCoordinates(self):
        """Returns (x,y,z)"""
        try:
            x = float(self.__getAttribute("pdbx_model_Cartn_x_ideal"))
            y = float(self.__getAttribute("pdbx_model_Cartn_y_ideal"))
            z = float(self.__getAttribute("pdbx_model_Cartn_z_ideal"))
            return (x, y, z)
        except:  # noqa: E722 pylint: disable=bare-except
            return (None, None, None)

    def dump(self, ofh):
        ofh.write("PdbxChemCompAtomPersist(dump) %r\n" % self.__rowData)


class PdbxChemCompBondPersist(object):
    """Accessor methods chemical component bond attributes."""

    def __init__(self, rowData, attributeNameList, verbose=True, log=sys.stderr):  # pylint: disable=unused-argument
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name):
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData=None):
        self.__rowData = rowData
        return self

    def getBond(self):
        """Returns (atomI,atomJ) atom ids from the atom list."""
        return (self.__getAttribute("atom_id_1"), self.__getAttribute("atom_id_2"))

    def getType(self):
        return self.__getAttribute("value_order")

    def getIntegerType(self):
        bT = self.__getAttribute("value_order")
        if bT == "SING":
            return 1
        elif bT == "DOUB":
            return 2
        elif bT == "TRIP":
            return 3
        elif bT == "QUAD":
            return 4
        else:
            return 0

    def isAromatic(self):
        return self.__getAttribute("pdbx_aromatic_flag") == "Y"

    def getStereo(self):
        return self.__getAttribute("pdbx_stereo_config")

    def hasStereo(self):
        return self.__getAttribute("pdbx_stereo_config") != "N"

    def dump(self, ofh):
        ofh.write("PdbxChemCompBondPersist(dump) %r\n" % self.__rowData)


class PdbxChemCompIdentifierPersist(object):
    """Accessor methods chemical component identifier attributes."""

    def __init__(self, rowData, attributeNameList, verbose=True, log=sys.stderr):  # pylint: disable=unused-argument
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name):
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData=None):
        self.__rowData = rowData
        return self

    def getIdentifier(self):
        """Returns the value of the identifier."""
        return self.__getAttribute("identifier")

    def getType(self):
        return self.__getAttribute("type")

    def getProgram(self):
        return self.__getAttribute("program")

    def getProgramVersion(self):
        return self.__getAttribute("program_version")

    def dump(self, ofh):
        ofh.write("PdbxChemCompIdentifierPersist(dump) %r\n" % self.__rowData)


class PdbxChemCompDescriptorPersist(object):
    """Accessor methods chemical component descriptor  attributes."""

    def __init__(self, rowData, attributeNameList, verbose=True, log=sys.stderr):  # pylint: disable=unused-argument
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name):
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData=None):
        self.__rowData = rowData
        return self

    def getDescriptor(self):
        """Returns the value of the descriptor."""
        return self.__getAttribute("descriptor")

    def getType(self):
        return self.__getAttribute("type")

    def getProgram(self):
        return self.__getAttribute("program")

    def getProgramVersion(self):
        return self.__getAttribute("program_version")

    def dump(self, ofh):
        ofh.write("PdbxChemCompDescriptorPersist(dump) %r\n" % self.__rowData)


class PdbxChemCompAuditPersist(object):
    """Accessor methods chemical component audit details."""

    def __init__(self, rowData, attributeNameList, verbose=True, log=sys.stderr):  # pylint: disable=unused-argument
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name):
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData=None):
        self.__rowData = rowData
        return self

    def getActionType(self):
        """Returns the value of the action type."""
        return self.__getAttribute("action_type")

    def getDate(self):
        """Returns the value of audit date."""
        return self.__getAttribute("date")

    def getProcessingSite(self):
        """Returns the value of processing site."""
        return self.__getAttribute("processing_site")

    def getAnnotator(self):
        """Returns the value of audit annotator."""
        return self.__getAttribute("annotator")

    def getDetails(self):
        """Returns the value of audit details."""
        return self.__getAttribute("details")
