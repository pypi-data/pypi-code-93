# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import abc

import collections


###############################################################
#
#   REFINITIV IMPORTS
#

###############################################################
#
#   LOCAL IMPORTS
#

###############################################################
#
#   CLASSES
#


class InvalidChainRecordException(Exception):
    pass


class ChainRecord(abc.ABC):
    """this class is designed for represent the chain record templates.
    there are 3 types of chain record template.
        the common fields of all templates including
    number of elements in chain record field
        'REF_COUNT'
    display purpose fields
        'RDNDISPLAY',  'PREF_DISP'
    other fields
        'RECORD_TYPE',

    NOTE that in this scope we defined chain record name aka RIC or instrument name
    """

    #   name of number of link elements field
    RefCountFieldName = "REF_COUNT"

    #   name of record type field
    RecordTypeFieldName = "RECORDTYPE"

    ###########################################
    #   display purpose fields

    #   name of RNRECORD field
    RdnDisplayFieldName = "RDNDISPLAY"

    #   name of prefer display field
    PerfDisplayFieldName = "PREF_DISP"

    #   name of previous display field
    PrevDisplayFieldName = "PREV_DISP"

    #   name of prefer link field
    PrefLinkFieldName = "PREF_LINK"

    #   name of display name field
    DisplayNameFieldName = "DSPLY_NAME"

    #   define the invalid display template values
    #       note that include the empty string
    InvalidDisplayTemplateValues = ["@@@", 0]

    def __init__(self):
        #   store the number of link elements
        self._numLinkElements = None
        #   store link fields - mapping between element index to link field value
        self._linkFieldDict = None
        #   store previous/next chain records
        self.prevChainRecordName = None
        self.nextChainRecordName = None

        #   store record type
        self._recordType = None

        #   store display purpose fields
        self._rdnDisplay = None
        self._perfDisplay = None
        self._prevDisplay = None
        self._prefLink = None

        #   store the DSPLY_NAME field
        self._displayName = None

    def __repr__(self):
        return """ChainRecord(displayName = {}, numLinkElements = {}, linkFields = {}, prevChainRecordName = {}, nextChainRecordName = {},
                recordType = {}, rdnDisplay = {}, perfDisplay = {}, prevDisplay = {}, perfLink = {},
                displayTemplate = {})\n""".format(
            self._displayName,
            self._numLinkElements,
            self._linkFieldDict,
            self.prevChainRecordName,
            self.nextChainRecordName,
            self._recordType,
            self._rdnDisplay,
            self._perfDisplay,
            self._prevDisplay,
            self._prefLink,
            self.displayTemplate,
        )

    @property
    def numConsituents(self):
        """ number of constituents in this chain record """
        return self._numLinkElements

    @property
    def constituentList(self):
        """ list all constituent of this chain record """
        return [
            constituent for index, constituent in sorted(self._linkFieldDict.items())
        ]

    @property
    #   display template of this chain record
    def displayTemplate(self):
        """ determine display template of this chain record """
        #   order to determine which is display template
        #       perfDisplay -> prevDisplay -> rdnDisplay

        #   determine display template value
        if ChainRecord._isValidDisplayTemplate(self._perfDisplay):
            #   this is a valid display template, so use it as display template
            return self._perfDisplay
        elif ChainRecord._isValidDisplayTemplate(self._prevDisplay):
            #   this is a valid display template, so use it as display template
            return self._prevDisplay
        else:
            #   use the rdn display as display template
            return self._rdnDisplay

    @property
    def displayName(self):
        return self._displayName

    @property
    @abc.abstractmethod
    def StartNoLinkFieldName(self):
        pass

    @property
    @abc.abstractmethod
    def LinkFieldNameTemplate(self):
        pass

    @property
    @abc.abstractmethod
    def PrevFieldName(self):
        pass

    @property
    @abc.abstractmethod
    def NextFieldName(self):
        pass

    def update(self, fields):
        """ do an update on this chain record by given some of the fields """

        #   call an internal update (this is update for general chain record field.)
        oldAndNewNumLinkElementsTuple = self._update_internal(fields)

        #   determine number of link elements to be update
        if oldAndNewNumLinkElementsTuple:
            #   number of link elements changed
            (oldNumLinkElements, newNumLinkElements) = oldAndNewNumLinkElementsTuple
            numLinkElements = (
                oldNumLinkElements
                if oldNumLinkElements > newNumLinkElements
                else newNumLinkElements
            )
        else:
            #   number of link elements hasn't changed
            numLinkElements = self._numLinkElements

        #   do an update on specific on each chain record template

        #   LINK fields
        indexToOldAndNewConstituentTupleDict = {}
        for index in range(self.StartNoLinkFieldName, numLinkElements + 1):
            #   extract each LINK field index
            #   construct link field name from template
            thisLinkFieldName = self.LinkFieldNameTemplate.format(index)

            #   check this link field is update or not?
            if thisLinkFieldName in fields:
                #   this link field exists, so update it
                #   store the old constituent for this link field
                try:
                    oldConstituent = self._linkFieldDict[index]
                except KeyError:
                    #   no old link element, so set it to be None
                    assert oldAndNewNumLinkElementsTuple
                    assert oldNumLinkElements < newNumLinkElements
                    oldConstituent = None

                #   update the link field constituent
                self._linkFieldDict[index] = fields[thisLinkFieldName]

                #   store updated link field
                indexToOldAndNewConstituentTupleDict[
                    index - self.StartNoLinkFieldName
                ] = (oldConstituent, self._linkFieldDict[index])

        #   previous/next fields
        #       previous
        oldAndNewPrevChainRecordNameTuple = None
        if self.PrevFieldName in fields:
            #   this previous link field exists, so update it
            #   store the old previous chain record name
            oldPrevChainRecordName = self.prevChainRecordName

            #   update the new previous chain record name
            self.prevChainRecordName = fields[self.PrevFieldName]

            #   store the old and new previous chain record name
            oldAndNewPrevChainRecordNameTuple = (
                oldPrevChainRecordName,
                self.prevChainRecordName,
            )

        #       next
        oldAndNewNextChainRecordNameTuple = None
        if self.NextFieldName in fields:
            #   this next link field exists, so update it
            #   store the old next chain record name
            oldNextChainRecordName = self.nextChainRecordName

            #   update the new next chain record name
            self.nextChainRecordName = fields[self.NextFieldName]

            #   store the old and new previous chain record name
            oldAndNewNextChainRecordNameTuple = (
                oldNextChainRecordName,
                self.nextChainRecordName,
            )

        #   construct and initialize the object for storing things that has been updated
        ChainRecordUpdateInfo = collections.namedtuple(
            "ChainRecordUpdateInfo",
            [
                "oldAndNewNumLinkElementsTuple",
                "indexToOldAndNewConstituentTupleDict",
                "oldAndNewPrevChainRecordNameTuple",
                "oldAndNewNextChainRecordNameTuple",
            ],
        )
        chainRecordUpdateInfo = ChainRecordUpdateInfo(
            oldAndNewNumLinkElementsTuple=oldAndNewNumLinkElementsTuple,
            indexToOldAndNewConstituentTupleDict=indexToOldAndNewConstituentTupleDict,
            oldAndNewPrevChainRecordNameTuple=oldAndNewPrevChainRecordNameTuple,
            oldAndNewNextChainRecordNameTuple=oldAndNewNextChainRecordNameTuple,
        )
        #   return updated chain record information
        return chainRecordUpdateInfo

    def _update_internal(self, fields):
        """do an internal update on this ChainRecord class
        RETURNS if number link elements is updated, so return a tuple of old and new number of link elements,
                    otherwise return None
        """

        #   update some fields might doesn't exists

        #   extract REF_COUNT field
        oldAndNewNumLinkElementsTuple = None
        if self.RefCountFieldName in fields:
            #   REF_COUNT is updated, so store the old and new ref_count
            #   store the old number of link elements
            oldNumLinkElements = self._numLinkElements

            #   update the number of element
            self._numLinkElements = fields[self.RefCountFieldName]

            #   store the tuple of old and new number of link elements
            oldAndNewNumLinkElementsTuple = (oldNumLinkElements, self._numLinkElements)

        #   extract the record type field
        if self.RecordTypeFieldName in fields:
            #   record type field exists, so update it
            self._recordType = fields[self.RecordTypeFieldName]

        #   extract display fields
        #       rdn display field
        if self.RdnDisplayFieldName in fields:
            #   extract rdn display and update in chain record object
            self._rdnDisplay = fields[self.RdnDisplayFieldName]

        #       prefer display field
        if self.PerfDisplayFieldName in fields:
            #   extract prefer display and update in chain record object
            self._perfDisplay = fields[self.PerfDisplayFieldName]

        #       previous display field
        if self.PrevDisplayFieldName in fields:
            #   extract previous display field and update in chain record object
            self._prevDisplay = fields[self.PrevDisplayFieldName]

        #       prefer link field
        if self.PrefLinkFieldName in fields:
            #   extract prefer line field and update in chain record object
            self._prefLink = fields[self.PrefLinkFieldName]

        #       display field
        if self.DisplayNameFieldName in fields:
            #   extract display name field and update th chain recored object
            self._displayName = fields[self.DisplayNameFieldName]

        #   done
        return oldAndNewNumLinkElementsTuple

    @classmethod
    def isValidChainRecord(cls, fields):
        """return True if given fields matched with this chain record
        otherwise False
        """
        #   REF_COUNT field
        if cls.RefCountFieldName not in fields:
            #   no ref_count field found, this is not a chains
            return False

        #   LINK fields
        for index in range(cls.StartNoLinkFieldName, cls.EndNoLinkFieldName + 1):
            #   check each LINK field index
            if cls.LinkFieldNameTemplate.format(index) not in fields:
                #   no this field index in fields, this is not a 10 char chain record
                return False

        #   previous/next fields
        if cls.PrevFieldName not in fields and cls.NextFieldName not in fields:
            #   no previous or next field found, this is not a chains
            return False

        #   otherwise, all field name matched 10 char chain record
        return True

    @classmethod
    def parseChainRecord(cls, fields):
        """parse the given chain record into object
            return chain record object

        raise InvalidChainRecordException if given fields are doesn't match with chain record template.
        """

        #   construct this ChainRecord object
        obj = cls()

        #   parse the general information and display information
        ChainRecord._parseChainRecord_displayFields(obj, fields)

        #   extract data from the fields
        #       raise exception when field doesn't found
        try:
            #   REF_COUNt field
            obj._numLinkElements = fields[obj.RefCountFieldName]

            #   LINK fields
            obj._linkFieldDict = {}
            if obj._numLinkElements:
                #   valid number of link elements
                for index in range(obj.StartNoLinkFieldName, obj._numLinkElements + 1):
                    #   extract each LINK field index
                    #   construct link field name from template
                    thisLinkFieldName = obj.LinkFieldNameTemplate.format(index)
                    # #   skip None fields
                    # if fields[thisLinkFieldName]:
                    # #   link field data is not None, so update link field data
                    obj._linkFieldDict[index] = fields[thisLinkFieldName]

        except KeyError:
            #   invalid chain record
            raise InvalidChainRecordException(
                "ERROR!!! invalid chain record template of {}".format(cls.__name__)
            )

        # warning CHECK_ME :: IS IT POSSIBLE? NO PREV AND NEXT LINK
        #   previous/next fields
        if obj.PrevFieldName in fields:
            #   exist previous field, so extract it
            obj.prevChainRecordName = fields[obj.PrevFieldName]
        if obj.NextFieldName in fields:
            #   exist previous field, so extract it
            obj.nextChainRecordName = fields[obj.NextFieldName]

        #   return extracted chain record
        return obj

    @staticmethod
    def _parseChainRecord_displayFields(chainRecord, fields):
        """parse the display purpose fields and store in the given chain record.
        NOTE that this legacy will modify chain record display data.
        """

        chainRecord._recordType = fields.get(
            ChainRecord.RecordTypeFieldName, chainRecord._recordType
        )
        chainRecord._rdnDisplay = fields.get(
            ChainRecord.RdnDisplayFieldName, chainRecord._rdnDisplay
        )
        chainRecord._perfDisplay = fields.get(
            ChainRecord.PerfDisplayFieldName, chainRecord._perfDisplay
        )
        chainRecord._prevDisplay = fields.get(
            ChainRecord.PrevDisplayFieldName, chainRecord._prevDisplay
        )
        chainRecord._prefLink = fields.get(
            ChainRecord.PrefLinkFieldName, chainRecord._prefLink
        )
        chainRecord._displayName = fields.get(
            ChainRecord.DisplayNameFieldName, chainRecord._displayName
        )

    @staticmethod
    def _isValidDisplayTemplate(displayTemplate):
        """ check whether is given display template is valid or not? """
        return (
            True
            if (
                (displayTemplate)
                and (displayTemplate not in ChainRecord.InvalidDisplayTemplateValues)
                ^ (isinstance(displayTemplate, str) and displayTemplate.strip() == "")
            )
            else False
        )


class ChainRecord10Chars(ChainRecord):
    """this class represent chain record template #80 (supports 10 chars in link fields).
       the following are link field name
    link field represent the links to the element of the chain
        'LINK_1', 'LINK_2', 'LINK_3', 'LINK_4', 'LINK_5', 'LINK_6', 'LINK_7',
        'LINK_8', 'LINK_9', 'LINK_10', 'LINK_11', 'LINK_12', 'LINK_13', 'LINK_14'
    previous field represent the previous chain record (can be empty)
        'PREV_LR'
    next field represent the next chain record (can be empty)
        'NEXT_LR'
    other fields
        'PREF_LINK'
    """

    #   template represent link field name
    LinkFieldNameTemplate = "LINK_{:d}"
    #   start number of link field
    StartNoLinkFieldName = 1
    EndNoLinkFieldName = 14

    #   name of previous/next field
    PrevFieldName = "PREV_LR"
    NextFieldName = "NEXT_LR"


class ChainRecord17Chars(ChainRecord):
    """this class represent chain record template #85 (supports 17 chars in link fields).
       the following are link field name
    link field represent the links to the element of the chain
        'LONGLINK1', 'LONGLINK2', 'LONGLINK3', 'LONGLINK4', 'LONGLINK5', 'LONGLINK6', 'LONGLINK7',
        'LONGLINK8', 'LONGLINK9', 'LONGLINK10', 'LONGLINK11', 'LONGLINK12', 'LONGLINK13', 'LONGLINK14'
    previous field represent the previous chain record (can be empty)
        'LONGPREVLR'
    next field represent the next chain record (can be empty)
        'LONGNEXTLR'
    other fields
        'PREF_LINK', 'PREV_DISP'
    """

    #   template represent link field name
    LinkFieldNameTemplate = "LONGLINK{:d}"
    #   start number of link field
    StartNoLinkFieldName = 1
    EndNoLinkFieldName = 14

    #   name of previous/next field
    PrevFieldName = "LONGPREVLR"
    NextFieldName = "LONGNEXTLR"


class ChainRecord32Chars(ChainRecord):
    """this class represent chain record template #32766 (supports 32 chars in link fields).
       the following are link field name
    link field represent the links to the element of the chain
        'BR_LINK1', 'BR_LINK2', 'BR_LINK3', 'BR_LINK4', 'BR_LINK5', 'BR_LINK6', 'BR_LINK7',
        'BR_LINK8', 'BR_LINK9', 'BR_LINK10', 'BR_LINK11', 'BR_LINK12', 'BR_LINK13', 'BR_LINK14'
    previous field represent the previous chain record (can be empty)
        'BR_PREVLR'
    next field represent the next chain record (can be empty)
        'BR_NEXTLR'
    other fields
        'PREF_LINK', 'PREV_DISP'
    """

    #   template represent link field name
    LinkFieldNameTemplate = "BR_LINK{:d}"
    #   start number of link field
    StartNoLinkFieldName = 1
    EndNoLinkFieldName = 14

    #   name of previous/next field
    PrevFieldName = "BR_PREVLR"
    NextFieldName = "BR_NEXTLR"
