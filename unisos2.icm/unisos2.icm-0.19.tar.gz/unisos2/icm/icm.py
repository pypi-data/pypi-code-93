# -*- coding: utf-8 -*-

"""\
*    *[Summary]* :: A =Library=: Interactive Command Modules (ICM) -- Cmnd methods of ICM classes are auto invokable at command line.
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/de/bx/nne/dev-py/pypi/pkgs/unisos/icm/dev/unisos/icm/icm.py :: [[elisp:(org-cycle)][| ]]
** is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
** *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
** A Python Interactively Command Module (PyICM). Part Of ByStar.
** Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
** Warning: All edits wityhin Dynamic Blocks may be lost.
"""
####+END:

"""
*  [[elisp:(org-cycle)][| *Lib-Module-INFO:* |]] :: Author, Copyleft and Version Information
"""

####+BEGIN: bx:icm:python:libName :style "fileName"
__libName__ = "icm"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201712260430"
####+END:

####+BEGIN: bx:global:icm:status-py :status "Production"
__status__ = "Production"
####+END:

__credits__ = [""]

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/icmInfo-mbNedaGpl.py"
icmInfo = {
    'authors':         ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"],
    'copyright':       "Copyright 2017, [[http://www.neda.com][Neda Communications, Inc.]]",
    'licenses':        ["[[https://www.gnu.org/licenses/agpl-3.0.en.html][Affero GPL]]", "Libre-Halaal Services License", "Neda Commercial License"],
    'maintainers':     ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]",],
    'contacts':        ["[[http://mohsen.1.banan.byname.net/contact]]",],
    'partOf':          ["[[http://www.by-star.net][Libre-Halaal ByStar Digital Ecosystem]]",]
}
####+END:

####+BEGIN: bx:icm:python:topControls 
"""
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]] [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
"""
####+END:

"""
* 
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/pythonWb.org"
*  /Python Workbench/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(python-check (format "pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "pep8 %s" (bx:buf-fname))))][pep8]] | [[elisp:(python-check (format "flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
####+END:
"""


####+BEGIN: bx:icm:python:section :title "ContentsList"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ContentsList*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:python:class :className "Cmnd" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /Cmnd/ object  [[elisp:(org-cycle)][| ]]
"""
class Cmnd(object):
####+END:
    """
** Root class of an ICM's Cmnd.
"""
    cmndParamsMandatory = list()  # ['inFile']
    cmndParamsOptional = list()   # ['perhaps']
    cmndArgsLen = {'Min': 0, 'Max':0,}
    cmndArgsSpecObsoltedByMethod = dict()  # {1: []}

    cmndVisibility = ["all"]  # users, developers, internal
    cmndUsers = []            # lsipusr
    cmndGroups = []           # bystar
    cmndImpact = []           # read, modify

    def __init__(self,
                 cmndLineInputOverRide=None,
                 cmndOutcome = None,  
    ):
        self.cmndLineInputOverRide = cmndLineInputOverRide
        self.cmndOutcome = cmndOutcome       

    def docStrClass(self,):
        return self.__class__.__doc__

    def docStrCmndMethod(self,):
        return self.cmnd.__doc__

    def docStrCmndDesc(self,):
        return self.cmnd.cmndDesc.__doc__

    
    def paramsMandatory(self,):
        return self.__class__.cmndParamsMandatory

    def paramsOptional(self,):
        return self.__class__.cmndParamsOptional

    def argsLen(self,):
        return self.__class__.cmndArgsLen

    def argsDesc(self,):
        return self.__class__.cmndArgsSpecObsoltedByMethod
    
    def users(self,):
        return self.__class__.cmndUsers

    def groups(self,):
        return self.__class__.cmndGroups

    def impact(self,):
        return self.__class__.cmndImpact

    def visibility(self,):
        return self.__class__.cmndVisibility

    def getOpOutcome(self):
        if self.cmndOutcome:
            return self.cmndOutcome
        return OpOutcome(invokerName=self.myName())

    def cmndLineValidate(
            self,
            outcome,
    ):
        if self.cmndLineInputOverRide:
            return True
            
        errorStr = self.cmndArgsLenValidate()
        if errorStr:
            outcome.error = OpError.CmndLineUsageError
            outcome.errInfo = errorStr
            return False
        errorStr = self.cmndParamsMandatoryValidate()
        if errorStr:
            outcome.error = OpError.CmndLineUsageError
            outcome.errInfo = errorStr
            return False
        errorStr = self.cmndParamsOptionalValidate()
        if errorStr:
            outcome.error = OpError.CmndLineUsageError
            outcome.errInfo = errorStr
            return False
        return True

    def cmndArgsLenValidate(self,
    ):
        """ If not as expected, return an error string, otherwise, None.

    expectedCmndArgsLen is a dcitionary with 'Min' and 'Max' range.
    """
        cmndArgsLen = len(IcmGlobalContext().icmRunArgsGet().cmndArgs)
        expectedCmndArgsLen = self.__class__.cmndArgsLen

        def errStr():
            errorStr = "Bad Number Of cmndArgs: cmndArgs={cmndArgs} --".format(cmndArgs=cmndArgsLen)
            if expectedCmndArgsLen['Min'] == expectedCmndArgsLen['Max']:
                errorStr = errorStr + "Expected {nu}".format(nu=expectedCmndArgsLen['Min'])
            else:
                errorStr = errorStr + "Expected between {min} and {max}".format(
                    min=expectedCmndArgsLen['Min'],
                    max=expectedCmndArgsLen['Max']
                )
            return errorStr

        if cmndArgsLen < expectedCmndArgsLen['Min']:
            retVal = errStr()
        elif cmndArgsLen > expectedCmndArgsLen['Max']:
            retVal = errStr()
        else:
            retVal = None

        #parser=argparse.ArgumentParser()
        #parser.print_help()

        return(retVal)

    def cmndParamsMandatoryValidate(self,
    ):
        """If not as expected, return an error string, otherwise, None.

    expectedCmndArgsLen is a dcitionary with 'Min' and 'Max' range.
    """
        G = IcmGlobalContext()
        icmRunArgs = G.icmRunArgsGet()
        icmRunArgsDict = vars(icmRunArgs)

        cmndParamsMandatory = self.__class__.cmndParamsMandatory

        for each in cmndParamsMandatory:
            if each in icmRunArgsDict.keys():
                continue
            else:
                return "Unexpected Mandatory Param: param={param} --".format(param=each)

        for each in cmndParamsMandatory:
            if icmRunArgsDict[each] == None:
                return "Missing Mandatory Param: param={param} --".format(param=each)                
            else:
                continue
        
        for each in cmndParamsMandatory:
            exec(
                "G.usageParams.{paramName} = icmRunArgs.{paramName}"
                .format(paramName=each)
            )
        return None

    def cmndParamsOptionalValidate(self,
    ):
        """If not as expected, return an error string, otherwise, None.

    expectedCmndArgsLen is a dcitionary with 'Min' and 'Max' range.
    """
        G = IcmGlobalContext()
        icmRunArgs = G.icmRunArgsGet()
        icmRunArgsDict = vars(icmRunArgs)

        cmndParamsOptional = self.__class__.cmndParamsOptional

        for each in cmndParamsOptional:
            if each in icmRunArgsDict.keys():
                continue
            else:
                return "Unexpected Optional Param: param={param} --".format(param=each)
        
        for each in cmndParamsOptional:
            #if icmRunArgsDict[each] != None:
            exec(
                "G.usageParams.{paramName} = icmRunArgs.{paramName}"
                .format(paramName=each)
            )
        return None
    
    def cmndMyName(self):
        return self.__class__.__name__
    
    def myName(self):
        return self.cmndMyName()
            
    def cmnd(self, interactive=False):
        print "This is default Cmnd Class Definition -- It is expected to be overwritten. You should never see this."

    def cmndArgsSpec(self):
        # This is default Cmnd Class Definition -- It is expected to be overwritten. You should never see this."
        return None

    def cmndArgsGet(
            self,
            argPosition,
            cmndArgsSpecDict,
            effectiveArgsList,
    ):
        def argDefaultGet(
                cmndArgsSpecDict,
                argPosition, 
        ):
            if cmndArgsSpecDict:
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind(argPosition)
                return cmndArgsSpec.argDefaultGet()
            else:
                return ""

        min, max = cmndArgPositionToMinAndMax(argPosition)

        if min == None:
            return None

        if min == max:
            # We are returning a string as value
            if len(effectiveArgsList) >= (min + 1):
                return effectiveArgsList[min]
            else:
                return argDefaultGet(cmndArgsSpecDict, argPosition)
            
        elif max == -1:
            argsList = list()
            if len(effectiveArgsList) >= (min + 1):
                for count in range(0, min):
                    effectiveArgsList.pop(count)
                return effectiveArgsList
            else:
                defaultArg = argDefaultGet(cmndArgsSpecDict, argPosition)
                if defaultArg:
                    argsList.append(
                        argDefaultGet(cmndArgsSpecDict, argPosition)
                    )
                return argsList

        else:
            argsList = list()
            if len(effectiveArgsList) >= (min + 1):
                for count in range(min, max):
                    if len(effectiveArgsList) > count:
                        argsList.append(effectiveArgsList[count])
            else:
                defaultArg = argDefaultGet(cmndArgsSpecDict, argPosition)
                if defaultArg:
                    argsList.append(
                        argDefaultGet(cmndArgsSpecDict, argPosition)
                    )
            return argsList


    def cmndArgsValidate(
            self,
            effectiveArgsList,
            cmndArgsSpecDict,
            outcome=None,
    ):
        """
** TODO Place Holder -- Should validate argsList to confirm that it is consistent with cmndArgsSpec
"""
        if not cmndArgsSpecDict:
            return True

        retVal = True

        def reportInvalidCmndLineArgValue(
            cmndLineArgValue,
            argChoices,
        ):
            print "cmndLineArgValue={cmndLineArgValue} is not in {argChoices}".format(
                cmndLineArgValue=cmndLineArgValue, argChoices=argChoices,
            )
            return False

        cmndArgsSpecDictDict = cmndArgsSpecDict.argDictGet()
        for argPosition, cmndArgSpec in cmndArgsSpecDictDict.iteritems():
            argChoices = cmndArgSpec.argChoicesGet()

            if not argChoices:
                continue

            if argChoices == "any":
                continue
            
            min, max = cmndArgPositionToMinAndMax(argPosition)
            
            if min == None:
                # EH_problem()
                return None

            if min == max:
                # There is just one value
                if len(effectiveArgsList) >= (min + 1):
                    cmndLineArgValue =  effectiveArgsList[min]

                    if not cmndLineArgValue in argChoices:
                        retVal = reportInvalidCmndLineArgValue(
                            cmndLineArgValue,
                            argChoices,
                        )

            elif max == -1:
                if len(effectiveArgsList) >= (min + 1):
                    for count in range(0, min):
                        effectiveArgsList.pop(count)
                        for cmndLineArgValue in effectiveArgsList:
                            if not cmndLineArgValue in argChoices:
                                retVal = reportInvalidCmndLineArgValue(
                                    cmndLineArgValue,
                                    argChoices,
                                )

            else:
                for count in range(min, max):            
                    if len(effectiveArgsList) >= (count + 1):
                        cmndLineArgValue = effectiveArgsList[count]
                        if not cmndLineArgValue in argChoices:
                            retVal = reportInvalidCmndLineArgValue(
                                cmndLineArgValue,
                                argChoices,
                            )
                        
        return retVal

        

####+BEGIN: bx:icm:python:func :funcName "cmndArgPositionToMinAndMax" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "argPosStr"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-anyOrNone :: /cmndArgPositionToMinAndMax/ retType=bool argsList=(argPosStr)  [[elisp:(org-cycle)][| ]]
"""
def cmndArgPositionToMinAndMax(
    argPosStr,
):
####+END:
    """
** Expecting argPosStr to be either an integer or two intgers delimited by an ampersand
*** returning two integers specifying the range
"""
    rangeList = argPosStr.split("&")
    rangeListLen = len(rangeList)

    def errVal():
        return None, None

    if rangeListLen == 0:
        return int(rangeList), int(rangeList)
    else:
        min=int(rangeList[0])

    if rangeListLen == 1:
        return min, min
    elif rangeListLen == 2:
        max=int(rangeList[1])
        return min, max
    else:
        print 'rangeListLen not 1 or 2'
        return errVal()
        
####+BEGINNOT: bx:icm:python:cmnd:classHead :modPrefix "lib" :cmndName "model" :comment "" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /model/ parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class model(Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    #@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:
	def cmndDesc(): """
** Description of ICM Model.
"""
        
        description = """
** Python-ICM Overview: file:/libre/ByStar/InitialTemplates/activeDocs/bxRefModel/iim/fullUsagePanel-en.org
        """
        if interactive: print description
        return description

    def cmndDocStr(self): return """
** Description of ICM Model.
"""

        

####+BEGINNOT: bx:icm:python:cmnd:classHead :modPrefix "lib" :cmndName "icmHelp" :comment "" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /icmHelp/ parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class icmHelp(Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    #@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        G = IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:
	def cmndDesc(): """
** Desription of ICM Command line options.
"""
        description = """

** Python-Icm-ICM Common UI Features:

Command Line (User Interface based on options, arguments and sub-commands)
ICM is based on [[http:docs.python.org/dev/library/argparse.html][argsparse]] with a set of well defined pre-specified options.
The "-"/"--invoke" in particular permits rapid module development.

***  --help
***  -i icm.model
***  -i describe  (Applies to the G_ ICM)
***  -i examples
***  --customOpt -i cmnd arg1 arg2

** Logging Control
***  -v 1 or --verbosity 1  (logging level 1 to 50 -- 1 means most verbose)
***  --logFile /var/log/somefile    (Specifies destination LogFile for this run)

** Callable Monitor Logging Control
***  --callTrackings monitor+  (or: --callTrackings monitor-)

** Callable Invokation Logging Control
***  --callTrackings invoke+  (or: --callTrackings invoke-)

** Run Mode (dryRun vs fullRun)
*** --runMode dryRun (or: --runMode fullRun runDebug)

** Load Python code in Global Context from icm module
*** --load file1.py --load file2.py

** Extract (display) an CMND's docstring
*** --docstring -i cmnd
        """
        if interactive: print description
        return description

####+BEGIN: bx:icm:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || =Imports=      :: *IMPORTS*  [[elisp:(org-cycle)][| ]]
"""
####+END:

import __main__

import sys
import os
import argparse
import inspect
from datetime import datetime
import time
import logging
#import pexpect
# Not using import pxssh -- because we need to custom manipulate the prompt
#import re

#import ast

import shlex
import subprocess

#from unisos.ucf import ucf
from unisos import ucf

import getpass



####+BEGINNOT: bx:dblock:python:icm:cmnd:classHead :modPrefix "lib" :cmndName "icmLibOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /icmLibOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class icmLibOverview(Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 3,}

    #@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {}
        if not cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        moduleDescription="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]	Model and Terminology 			                   :Overview:

Command line parameters and arguments are passed to Icm.cmnd. ICMs are capable of communicating 
their full command line parameters and arguments syntax and expectations to ICM Players. 
				
This module's primary documentation is in  http://www.by-star.net/PLPC/180047
**      [End-Of-Description]
"""
        
        moduleUsage="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]

**      How-Tos:
**      [End-Of-Usage]
"""
        
        moduleStatus="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO [[elisp:(org-cycle)][| ]]  Current         :: Just getting started [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""
        cmndArgsSpec = {"0&-1": ['moduleDescription', 'moduleUsage', 'moduleStatus']}
        cmndArgsValid = cmndArgsSpec["0&-1"]
        for each in effectiveArgsList:
            if each in cmndArgsValid:
                print each
                if interactive:
                    #print( str( __doc__ ) )  # This is the Summary: from the top doc-string
                    #version(interactive=True)
                    exec("""print({})""".format(each))
                
        return(format(str(__doc__)+moduleDescription))


"""
*  [[elisp:(org-cycle)][| ]]  /General/            :: *Common Utilities -- Constants, Variables* [[elisp:(org-cycle)][| ]]
"""

####+BEGINNOT: bx:icm:python:func :funcName "unusedSuppressForEval" :funcType "void" :retType "bool" :deco "" :argsList "*v **k"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-void      :: /unusedSuppressForEval/ retType=bool argsList=(*v **k)  [[elisp:(org-cycle)][| ]]
"""
def unusedSuppressForEval(
    *v,
    **k
):
####+END:
    pass

####+BEGINNOT: bx:icm:python:func :funcName "unusedSuppress" :funcType "void" :retType "bool" :deco "" :argsList "*v **k"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-void      :: /unusedSuppress/ retType=bool argsList=(*v **k)  [[elisp:(org-cycle)][| ]]
"""
def unusedSuppress(
    *v,
    **k
):
####+END:
    pass


####+BEGIN: bx:icm:python:func :funcName "cmndArgsValidate" :funcType "succFail" :retType "bool" :deco "" :argsList "argsList cmndArgsSpec"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-succFail  :: /cmndArgsValidate/ retType=bool argsList=(argsList cmndArgsSpec)  [[elisp:(org-cycle)][| ]]
"""
def cmndArgsValidate(
    argsList,
    cmndArgsSpec,
    outcome=None,
):
####+END:
    """
** TODO Place Holder -- Converted to a method, This Function will be obsolted. Should validate argsList to confirm that it is consistent with cmndArgsSpec
"""
    print "cmndArgsValidate Function OBSOLTED -- Deprecated"
    return True



"""
*  [[elisp:(org-cycle)][| ]]  /Enumerations/       :: *Common Global Enumerations* [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:dblock:python:class :className "ReturnCode" :superClass "" :comment "" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /ReturnCode/ object  [[elisp:(org-cycle)][| ]]
"""
class ReturnCode(object):
####+END:
    """ """
    Success = 0
    Failure  = 1
    ExtractionSuccess = 11                                  
    UsageError = 201

    def __init__(self):
        pass


"""
*  [[elisp:(org-cycle)][| ]]  /Operations/       :: *Operation Results* [[elisp:(org-cycle)][| ]]
"""
    

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Constants        ::  OpError    [[elisp:(org-cycle)][| ]]
"""
    
OpError = ucf.Constants()
opErrorDesc = {}

OpError.Success = 0
opErrorDesc[OpError.Success] = "Successful Operation -- No Errors"
OpError.Failure = 1
opErrorDesc[OpError.Failure] = "Catchall for general errors",
OpError.ShellBuiltinMisuse = 2    
opErrorDesc[OpError.ShellBuiltinMisuse]= "Bash Problem"
OpError.ExtractionSuccess = 11
opErrorDesc[OpError.ExtractionSuccess] = "NOTYET"
OpError.PermissionProblem = 126
opErrorDesc[OpError.PermissionProblem] = "Command invoked cannot execute"
OpError.CommandNotFound = 127
OpError.ExitError = 128
OpError.Signal1 = 128+1
OpError.ControlC = 130
OpError.Signal9 = 128+9
# ByStar Base Error Starts at 155
OpError.UsageError = 201
OpError.CmndLineUsageError = 202
OpError.ExitStatusOutOfRange = 255


####+BEGIN: bx:dblock:python:func :funcName "notAsFailure" :funcType "succFail" :retType "bool" :deco "" :argsList "obj"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-succFail  :: /notAsFailure/ retType=bool argsList=(obj)  [[elisp:(org-cycle)][| ]]
"""
def notAsFailure(
    obj,
):
####+END:
    if not obj:
        return  OpError.Failure
    else:
        return  OpError.Success



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  opErrorDescGet -- return opErrorDesc[opError]   [[elisp:(org-cycle)][| ]]
"""
def opErrorDescGet(opError):
    """ OpError is defined as Constants. A basic textual description is provided with opErrorDescGet().

Usage:  opOutcome.error = None  -- opOutcome.error = OpError.UsageError
OpError, eventually maps to Unix sys.exit(error). Therefore, the range is 0-255.
64-to-78 Should be made consistent with /usr/include/sysexits.h.
There are also qmail errors starting at 100.
"""
    # NOTYET, catch exceptions
    return opErrorDesc[opError]



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  OpOutcome -- .log() .isProblematic()   [[elisp:(org-cycle)][| ]]
"""
class OpOutcome(object):
    """ Operation Outcome. Consisting Of Error and/or Result -- Operation Can Be Local Or Remote

** TODO Add exception and exceptionInfo For situations where try: is handled
** TODO Add opType as one of PyCallable -- SubProc, RemoteOp
** TODO Add a printer (repr) for OpOutcome

OpOutcome is a combination of OpError(SuccessOrError) and OpResults.
                                                         
Typical Usage is like this:

On Definition of f():
thisOutcome = OpOutcome()
thisOutcome.results = itemOrList
)
return(thisOutcome.set(
    opError=None,
    ))

Then on invocation:
thisOutcome = OpOutcome()
opOutcome = f()
if opOutcome.error: return(thisOutcome.set(opError=opOutcome.error))
opResults = opOutcome.results
"""
    def __init__(self,
                 invokerName=None,
                 opError=None,
                 opErrInfo=None,
                 opResults=None,
                 opStdout=None,
                 opStderr=None,
                 opStdcmnd=None,                                  
    ):
        '''Constructor'''
        self.invokerName = invokerName
        self.error = opError
        self.errInfo  = opErrInfo
        self.results = opResults
        self.stdout = opStdout
        self.stderr = opStderr
        self.stdcmnd = opStdcmnd      

    def set(self,
            invokerName=None,
            opError=None,
            opErrInfo=None,
            opResults=None,
            opStdout=None,
            opStderr=None,
            opStdcmnd=None,                        
    ):
        if invokerName != None:
            self.name = invokerName
        if opError != None:
            self.error = opError
        if opErrInfo != None:
            self.errInfo = opErrInfo
        if opResults != None:
            self.results = opResults
        if opStdout != None:
            self.stdout = opStdout
        if opStderr != None:
            self.stderr = opStderr
        if opStdcmnd != None:
            self.stdcmnd = opStdcmnd
            
        return self
    
    def isProblematic(self):
        if self.error:
            IcmGlobalContext().__class__.lastOpOutcome = self
            return True
        else:
            return False


    def log(self):
        G = IcmGlobalContext()
        LOG_here(G.icmMyFullName() + ':' + str(self.invokerName) + ':' + ucf.stackFrameInfoGet(2))
        if self.stdcmnd: LOG_here("Stdcmnd: " +  self.stdcmnd)
        if self.stdout: LOG_here("Stdout: " +  self.stdout)        
        if self.stderr: LOG_here("Stderr: " +  self.stderr)
        return self


    def out(self):
        G = IcmGlobalContext()
        ANN_here(G.icmMyFullName() + ':' + str(self.invokerName) + ':' + ucf.stackFrameInfoGet(2))
        if self.stdcmnd: ANN_write("Stdcmnd: \n" +  self.stdcmnd)
        if self.stdout: ANN_write("Stdout: ")
        if self.stdout: OUT_write(self.stdout)                
        if self.stderr: ANN_write("Stderr: \n" +  self.stderr)
        return self
    

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  opSuccess    [[elisp:(org-cycle)][| ]]
"""    
def opSuccess():
    """."""
    return (
        OpOutcome()
    )


class OpRemoteCmnd(object):
    """ Remote operation specification and invocation of an CMND through ICM command line.

Returns OpOutcome.

** TODO Developement Status: in-progress.
                                                         
Typical Usage:
performerCmnd = OpRemoteCmnd()
performerCmnd.performerInfo(
    remoteOpMethod="ssh",
    remoteOpSap=21,
    performerHost=ipAddrOrName,
    performerUser=lsipusr,
    performerCredentials=pubKey,
)
performerCmnd.cmndElems(
    icmName="prog",
    cmndName="cmndName",
    cmndMandatoryParams=listOfPars,
    cmndOptionalParams=listOfOpts,
    cmndArgs=listOfArgs,
    icmParams=listOfCmndParams,
)
Or 
performerCmnd.cmndLine=cmndString

remoteOpOutcome = performerCmnd.perform()
"""
    def __init__(self,
                 remoteOpMethod=None,
                 remoteOpSap=None,
                 performerHost=None,
                 cmndLine=None,                 
    ):
        '''Constructor'''
        self.remoteOpMethod = remoteOpMethod
        self.cmndLine = cmndLine

    def performerInfo(self,
    ):
        return self

    def cmndElems(self,
    ):
        return self

    def perform(self,
    ):
        return self
    

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  ArgReq -- Obsoleted   [[elisp:(org-cycle)][| ]]
"""
#ArgReq = enum('Mandatory', 'Optional')   # Argument Requirements -- Mandatory Keyword Arguments
class ArgReq():
    """ Argument Requirements: For Specification Of Required Keyword Arguments.

    Example: ArgReq.Conditional -- to be used at declaration time.
    """
    Mandatory = "___Mandatory___"
    Optional = "___Optional___"
    Conditional = "___Conditional___"

    def __init__(self):
        pass

    def isMandatory(self, arg):
        """Predicate."""
        if arg == self.Mandatory:
            return True
        else:
            return False

    def mandatoryValidate(self, arg):
        """Predicate."""        
        if self.isMandatory(arg):
            EH_problem_info("Missing Mandatory Argument")
            # It is the caller's frame that is of significance
            raise ValueError("Missing Mandatory Argument: " + ucf.stackFrameInfoGet(2))
        return arg


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  Interactivity -- Obsoleted   [[elisp:(org-cycle)][| ]]
"""

class Interactivity():
    """ The interactive= keyword argument is specified as below and invoked as True or False."""
    Only = "___Only___"          # Should Only Be Invoked Interactively
    Both = "___Both___"          # Can Be Invoked Interactive Or Non-Interactively
    Not = "___Not___"            # Should Not Be Invoked Interactively

    def __init__(self):
        pass

    def interactiveInvokation(self, interactive):
        if interactive:
            return True
        else:
            return False



"""
*  [[elisp:(org-cycle)][| ]]  /General/            :: *Call Tracking (decorators)* [[elisp:(org-cycle)][| ]]
"""


"""
**  [[elisp:(org-cycle)][| ]]  Decorator     ::  Callable Tracking subjectToTracking()   [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  subjectToTracking    [[elisp:(org-cycle)][| ]]
"""

def subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True):
    """[DECORATOR-WITH-ARGS:]  Passes parameters to subSubjectToTracking. See subSubjectToTracking.
    """

    def subSubjectToTracking(fn):
        """[DECORATOR:] tracks calls to a function.

        Returns a decorated version of the input function which "tracks" calls
        made to it by writing out the function's name and the arguments it was
        called with.
        Do so subject to icmRunArgs_isCallTrackingMonitorOn and
        fnLoc, fnEntry, fnExit parameters.
        """

        import functools
        # Unpack function's arg count, arg names, arg defaults
        code = fn.func_code
        argcount = code.co_argcount
        argnames = code.co_varnames[:argcount]
        fn_defaults = fn.func_defaults or list()
        argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

        @functools.wraps(fn)
        def wrapped(*v, **k):
            if (fnLoc == False) and (fnEntry == False) and (fnExit == False):
                return fn(*v, **k)

            #if icmRunArgs_isCallTrackingMonitorOff():   # normally on, turns-off with monitor-
                #return fn(*v, **k)

            if not icmRunArgs_isCallTrackingMonitorOn(): # normally off, turns-on with monitor+
                return fn(*v, **k)

            # Collect function arguments by chaining together positional,
            # defaulted, extra positional and keyword arguments.
            positional = map(ucf.format_arg_value, zip(argnames, v))
            defaulted = [ucf.format_arg_value((a, argdefs[a]))
                         for a in argnames[len(v):] if a not in k]
            nameless = map(repr, v[argcount:])
            keyword = map(ucf.format_arg_value, k.items())
            args = positional + defaulted + nameless + keyword

            logControler = LOG_Control()
            logger = logControler.loggerGet()

            depth = ucf.stackFrameDepth(2)
            indentation = ucf.STR_indentMultiples(multiple=depth)
            
            # if fnLoc:
            #     logger.debug(format('%s Monitoring(M-Call-%s): ' % (indentation, depth)) + ucf.stackFrameInfoGet(2))

            if fnEntry:
                logger.debug( "%s M-Enter-%s: %s(%s) AT %s" % (indentation, depth, fn.__name__, ", ".join(args), ucf.stackFrameInfoGet(2)))

            retVal = fn(*v, **k)

            if fnExit:
                logger.debug( "%s M-Return-%s(%s):  %s AT %s" % (indentation, depth, fn.__name__, retVal, ucf.stackFrameInfoGet(2)))
            
            return retVal
        return wrapped
    return subSubjectToTracking


# def subjectToDryRun(fn):
#     """[DECORATOR] Subject the function to DryRun predicate.
#     """
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  callableEntryEnhancer    [[elisp:(org-cycle)][| ]]
"""

def callableEntryEnhancer(type='generic'):
    """\
    For now this is somewhat Complex,
    The Real parts are:
       - When requested, the callable's docstring is extracted.
         The request is either:
         --docString
         or type=describe
    The Imaginary parts are:
       - Callables are assigned --type (eg, cmnd)--, then
         list of all of a given type can be produced
         The cmnd type mimics Emacs' (interactive)
    """
    if icmRunArgs_isDocStringRequested():
        print( ucf.stackFrameInfoGet(2) )
        #print( stackFrameArgsGet(2) )
        print( ucf.stackFrameDocString(2) )

        raise StopIteration()

    if type == 'cmnd':
        # Tag it as Interactive
        pass
    elif type == 'describe':
        #print( stackFrameArgsGet(2) )
        print( ucf.stackFrameDocString(2) )
    elif type == 'icmUiSupport':
        pass
    elif type == 'generic':
        pass
    else:
        TM_here()
        raise StopIteration()


"""
**  [[elisp:(org-cycle)][| ]]  Func          ::  loadFile (based on execfile)   [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  loadFile    [[elisp:(org-cycle)][| ]]
"""
#@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def loadFile(file):
    """Load the specified python file."""

    global globdict
    globdict= globals()

    TM_here('ICM-Loading: ' + file)
    execfile(file, globdict)


"""
**  [[elisp:(org-cycle)][| ]]  Func          ::  Invokation Tracking do() and doLog()  [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  do    [[elisp:(org-cycle)][| ]]
"""
subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def do(fn, *v, **k):
    """Invokes fn with args (*v, **k) and logs the invocation and return based on invoke+/-.

    If invoke+ is set, invokation is logged. Otherwise it just invokes the function.
    Example Usage:
    instead of thisFunc(thatArg) in order to track thisFunc we:
    do(thisFunc, thatArg)
    """

    if icmRunArgs_isCallTrackingInvokeOff():
        return fn(*v, **k)

    #
    # Even though the call is identical because of stackFrameInfoGet(2)
    # in there, we are not going to --  return doLog(fn, *v, **k)
    # And instead we are duplicating the code.
    # Consider this an instance for why python should have macros.
    #

    # Unpack function's arg count, arg names, arg defaults
    code = fn.func_code
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.func_defaults or list()
    argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

    # Collect function arguments by chaining together positional,
    # defaulted, extra positional and keyword arguments.
    positional = map(ucf.format_arg_value, zip(argnames, v))
    defaulted = [ucf.format_arg_value((a, argdefs[a]))
                 for a in argnames[len(v):] if a not in k]
    nameless = map(repr, v[argcount:])
    keyword = map(ucf.format_arg_value, k.items())
    args = positional + defaulted + nameless + keyword

    logControler = LOG_Control()
    logger = logControler.loggerGet()
    depth = ucf.stackFrameDepth(2)
    indentation = ucf.STR_indentMultiples(multiple=depth)

    logger.debug(format('%s Invoking(I-Call-%s): ' % (indentation, depth)) + ucf.stackFrameInfoGet(2))
    logger.debug( "%s I-Enter-%s: %s(%s)" % (indentation, depth, fn.__name__, ", ".join(args)) )
    retVal = fn(*v, **k)
    logger.debug( "%s I-Return-%s(%s):  %s" % (indentation, depth, fn.__name__, retVal) )
    return retVal


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  doLog    [[elisp:(org-cycle)][| ]]
"""
subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def doLog(fn, *v, **k):
    """Invokes fn with args (*v, **k) and logs the invocation and return.
    """

    # Unpack function's arg count, arg names, arg defaults
    code = fn.func_code
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.func_defaults or list()
    argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

    # Collect function arguments by chaining together positional,
    # defaulted, extra positional and keyword arguments.
    positional = map(ucf.format_arg_value, zip(argnames, v))
    defaulted = [ucf.format_arg_value((a, argdefs[a]))
                 for a in argnames[len(v):] if a not in k]
    nameless = map(repr, v[argcount:])
    keyword = map(ucf.format_arg_value, k.items())
    args = positional + defaulted + nameless + keyword

    logControler = LOG_Control()
    logger = logControler.loggerGet()
    depth = ucf.stackFrameDepth(2)
    indentation = ucf.STR_indentMultiples(multiple=depth)

    logger.debug(format('Invoking(I-Call-%s): ' % (depth)) + ucf.stackFrameInfoGet(2))
    logger.debug( "%s I-Enter-%s: %s(%s)" % (indentation, depth, fn.__name__, ", ".join(args)) )
    retVal = fn(*v, **k)
    logger.debug( "%s I-Return-%s(%s):  %s" % (indentation, depth, fn.__name__, retVal) )
    return retVal


"""
*  [[elisp:(org-cycle)][| ]]  /subProc/            :: *SubProcess -- Bash or Command Syncronous invokations* [[elisp:(org-cycle)][| ]]
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  subProc_bash  -- subprocess.Popen()  [[elisp:(org-cycle)][| ]]
"""
subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def subProc_bash(
        cmndStr,
        stdin=None,
        outcome=None,
):
    """subprocess.Popen() -- shell=True, runs cmndStr in bash."""
    
    #
    if not outcome:
        outcome = OpOutcome()

    if not stdin:
        stdin = ""

    outcome.stdcmnd = cmndStr    
    try:
        process = subprocess.Popen(
            cmndStr,
            shell=True,
            executable="/bin/bash",            
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError:
        outcome.error = OSError
    else: 
        outcome.stdout, outcome.stderr = process.communicate(input=format(stdin.encode()))
        process.stdin.close()

    process.wait()

    outcome.error = process.returncode
    
    return outcome



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  subProc_cmnd    [[elisp:(org-cycle)][| ]]
"""
subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def subProc_cmnd(
        cmndStr,
        stdin=None,
        outcome=None,
):
    """subprocess.Popen()
    """
    #
    if not outcome:
        outcome = OpOutcome()

    if not stdin:
        stdin = ""

    commandArgs=shlex.split(cmndStr)

    outcome.stdcmnd = cmndStr    
    try:
        process = subprocess.Popen(
            commandArgs,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError:
        outcome.errInfo = OSError
    else: 
        outcome.stdout, outcome.stderr = process.communicate(input=format(stdin.encode()))
        process.stdin.close()

    process.wait()

    outcome.error = process.returncode
    
    return outcome


"""
*  [[elisp:(org-cycle)][| ]]  /General/            :: *Frame Marking and Tracking -- stackFrameInfoGet(frameNu)* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  /Outputs Control/    :: *LOG_: ICM Logging Control -- On top of Standard of Python Logging* [[elisp:(org-cycle)][| ]]
"""

#LOGGER = 'Icm.Python.Logger'
LOGGER = 'Icm'
CONSL_LEVEL_RANGE = range(0, 51)
#FORMAT_STR = '%(asctime)s %(levelname)s %(message)s'
FORMAT_STR = '%(levelname)s %(message)s -- %(asctime)s'


####+BEGIN: bx:icm:python:func :funcName "logFileName" :funcType "anyOrNone" :retType "str" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-anyOrNone :: /logFileName/ retType=str argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def logFileName():
####+END:
    return (
        "/tmp/{userName}-ICM.log".format(
            userName=getpass.getuser()
        )
    )
    

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  getConsoleLevel    [[elisp:(org-cycle)][| ]]
"""

def getConsoleLevel(args):
    level = args.verbosityLevel
    if level is None: return
    try: level = int(level)
    except: pass
    if level not in CONSL_LEVEL_RANGE:
        args.verbosityLevel = None
        print 'warning: console log level ', level, ' not in range 1..50.'
        return
    return level

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  LOG_Control  -- logging: debug(TM_), info(LOG_), warning(EH_), error(EH_), critical(EH_)   [[elisp:(org-cycle)][| ]]
"""

class LOG_Control():
    """ICM Logging on top of basic Logging.
    """

    args = None
    logger = None
    fh = None
    level = None

    def __init__(self):
        pass

    def loggerSet(self, args):
        """
        """

        #print( args )    #TEMP

        self.__class__.args = args

        logger = logging.getLogger(LOGGER)

        self.__class__.logger = logger

        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(FORMAT_STR)
        ## Add FileHandler
        fh = logging.FileHandler(logFileName())
        fh.name = 'File Logger'
        fh.level = logging.WARNING
        fh.formatter = formatter
        logger.addHandler(fh)

        self.__class__.fh = fh

        ## Add (optionally) ConsoleHandler
        level = getConsoleLevel(args)

        self.__class__.level = level

        #print( 'level= ' + str(level) )  # TEMP

        if level is not None:
            #print( stackFrameInfoGet(1) )  # TEMP
            ch = logging.StreamHandler()
            ch.name = 'Console Logger'
            ch.level = level
            ch.formatter = formatter
            logger.addHandler(ch)
            #print( stackFrameInfoGet(1) )  # TEMP
        return logger

    def loggerSetLevel(self, level):
        """
        """

        #print( args )    #TEMP

        #self.__class__.args = args

        logger = logging.getLogger(LOGGER)

        self.__class__.logger = logger

        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(FORMAT_STR)
        ## Add FileHandler
        fh = logging.FileHandler(logFileName())
        fh.name = 'File Logger'
        fh.level = logging.WARNING
        fh.formatter = formatter
        logger.addHandler(fh)

        self.__class__.fh = fh

        ## Add (optionally) ConsoleHandler
        #level = getConsoleLevel(args)

        self.__class__.level = level

        #print( 'level= ' + str(level) )  # TEMP

        if level is not None:
            #print( stackFrameInfoGet(1) )  # TEMP
            ch = logging.StreamHandler()
            ch.name = 'Console Logger'
            ch.level = level
            ch.formatter = formatter
            logger.addHandler(ch)
            #print( stackFrameInfoGet(1) )  # TEMP
        return logger

    def loggerGetLevel(self, ):
        """
        """
        return(self.__class__.level)

    
    def loggerReset(self):
        logger = self.__class__.logger
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(FORMAT_STR)
        fh = self.__class__.fh
        fh.formatter = formatter

    def loggerGet(self):
        return self.__class__.logger

"""
*  [[elisp:(org-cycle)][| ]]  /TM_/                :: *TM_: Trackings Module (TM_)/Class -- Instrumented Tracing On Top Of ICM-Logging* [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  TM_note  -- logging.debug (10) -- bxf.tm.note() [[elisp:(org-cycle)][| ]]
"""

def TM_note(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.debug( 'TM_: ' + outString )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  TM_here  -- logging.debug (10) -- bxf.tm.here() [[elisp:(org-cycle)][| ]]
"""

def TM_here(*v, **k):
    """Mark file and line -- do the equivalent of a print statement.
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.debug('TM_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )



"""
*  [[elisp:(org-cycle)][| ]]  /LOG_/               :: *LOG_: Significant Event Which Is Not An Error* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  LOG_note  -- logging.info (20) -- bxf.info.note() -- bxf.info.op.note(outcome,).log()  [[elisp:(org-cycle)][| ]]
"""

def LOG_note(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.info( 'LOG_: ' + outString )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  LOG_here  -- logging.info (20) -- bxf.info.here() -- bxf.info.op.here(outcome,)  [[elisp:(org-cycle)][| ]]
"""

def LOG_here(*v, **k):
    """Mark file and line -- do the equivalent of a print statement.
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.info('LOG_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )

    


"""
*  [[elisp:(org-cycle)][| ]]  /EH_/                :: *EH_: ICM Error Handling On Top Of Python Exceptions (EH_ Module)* [[elisp:(org-cycle)][| ]]
"""
"""
**  [[elisp:(org-cycle)][| ]]  Subject      ::== CmndArgs Exceptions (EH_ Module) [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_critical_cmndArgsPositional  --   [[elisp:(org-cycle)][| ]]
"""

def EH_critical_cmndArgsPositional(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.critical('EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )
    #raise RuntimeError()
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_critical_cmndArgsOptional    [[elisp:(org-cycle)][| ]]
"""

def EH_critical_cmndArgsOptional(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.critical('EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )
    #raise RuntimeError()
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_critical_usageError    [[elisp:(org-cycle)][| ]]
"""

def EH_critical_usageError(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.critical('EH_usageError: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )
    return(ReturnCode.UsageError)
    #raise RuntimeError()
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_problem_notyet    [[elisp:(org-cycle)][| ]]
"""

def EH_problem_notyet(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.critical('EH_NotYet: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )
    #raise RuntimeError()

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_problem_info    [[elisp:(org-cycle)][| ]]
"""

def EH_problem_info(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.critical('EH_Info: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_problem_usageError -- logger.error (40)  [[elisp:(org-cycle)][| ]]
"""

def EH_problem_usageError(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.critical('EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )

    return (
        eh_problem_usageError(OpOutcome(), *v, **k)
    )
    
    #raise RuntimeError()

    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  eh_problem_usageError -- Captured in Outcome  [[elisp:(org-cycle)][| ]]
"""
    

def eh_problem_usageError(outcome, *v, **k):
    """
    """
    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    errStr='EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2)
    return(outcome.set(
        opError=OpError.UsageError,
        opErrInfo=errStr,
    ))

    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_critical_unassigedError    [[elisp:(org-cycle)][| ]]
"""

def EH_critical_unassigedError(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.critical('EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )
    #raise RuntimeError()
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_problem_unassignedError    [[elisp:(org-cycle)][| ]]
"""

def EH_problem_unassignedError(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.critical('EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )
    #raise RuntimeError()

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_critical_oops    [[elisp:(org-cycle)][| ]]
"""

def EH_critical_oops(*v, **k):
    """A Software Error has Occured.
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    print('EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )
    logger.critical('EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )

    #raise RuntimeError()

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_critical_exception    [[elisp:(org-cycle)][| ]]
"""

def EH_critical_exception(e):
    """ Usage Example:
    try: m=2/0
    except Exception as e: icm.EH_critical_exception(e)
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    #fn = FUNC_currentGet()

    outString = format(e)
    
    logger.critical('EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logger.critical(
        "EH_: {exc_type} {fname} {lineno}"
        .format(
            exc_type=exc_type,
            fname=fname,
            lineno=exc_tb.tb_lineno
        )
    )

    logging.exception(e)

    # Or any of the 
    #logger.error("EH_critical_exception", exc_info=True)
    #print(traceback.format_exc())


    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_badOutcome    [[elisp:(org-cycle)][| ]]
"""
def EH_badOutcome(outcome):
    print(
        "EH_badOutcome: InvokedBy {invokerName}, Operation Failed: Stdcmnd={stdcmnd} Error={status} -- {errInfo}".
        format(invokerName=outcome.invokerName,
               stdcmnd=outcome.stdcmnd,
               status=outcome.error,
               errInfo=outcome.errInfo,
        ))
    print('EH_: ' + ' -- ' + ucf.stackFrameInfoGet(2) ) 

    return outcome

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || CMND              ::  EH_badLastOutcome    [[elisp:(org-cycle)][| ]]
"""
def EH_badLastOutcome():
    return (
        EH_badOutcome(
            IcmGlobalContext().lastOpOutcome
        ))

def eh_badLastOutcome():
    return (
            IcmGlobalContext().lastOpOutcome
    )

    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  EH_runTime    [[elisp:(org-cycle)][| ]]
"""

def EH_runTime(*v, **k):
    """
    """
    logControler = LOG_Control()
    logger = logControler.loggerGet()

    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.error('EH_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )
    raise RuntimeError()


"""
*  [[elisp:(org-cycle)][| ]]  /ANN_/               :: *ANN_: Announcing Module (ANN_)/Class* [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ANN_write  -- Same As print to stderr [[elisp:(org-cycle)][| ]]
"""

def ANN_write(*v, **k):
    """
    """
    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    print( outString )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ANN_note -- Prepends ANN_:     [[elisp:(org-cycle)][| ]]
"""

def ANN_note(*v, **k):
    """
    """
    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    print( 'ANN_: ' + outString )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ANN_here -- Prepends ANN_ and adds stackFrameInfoGet(2)   [[elisp:(org-cycle)][| ]]
"""

def ANN_here(*v, **k):
    """Mark file and line -- do the equivalent of a print statement.
    """
    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    print('ANN_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )


"""
*  [[elisp:(org-cycle)][| ]]  /OUT_/               :: *OUT_: Output Module (OUT_)/Class* [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  OUT_write  -- Same As print to stderr [[elisp:(org-cycle)][| ]]
"""

def OUT_write(*v, **k):
    """
    """
    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    print( outString )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  OUT_note -- Prepends OUT_:     [[elisp:(org-cycle)][| ]]
"""

def OUT_note(*v, **k):
    """
    """
    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    print( outString )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  OUT_here -- Prepends OUT_ and adds stackFrameInfoGet(2)   [[elisp:(org-cycle)][| ]]
"""

def OUT_here(*v, **k):
    """Mark file and line -- do the equivalent of a print statement.
    """
    fn = ucf.FUNC_currentGet()
    argsLength =  ucf.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    print('OUT_: ' + outString + ' -- ' + ucf.stackFrameInfoGet(2) )

    

    
"""
*  [[elisp:(org-cycle)][| ]]  /FV_/                :: *File Variables (FV_)* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FV_writeToFilePath    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FV_writeToFilePath(
        filePath,
        varValue,
):
    """
    """
    baseDir = os.path.dirname(filePath)
    if not os.path.isdir(baseDir):
        return None
    varName = os.path.basename(filePath)
    return(
        FV_writeToBaseDir(
            baseDir,
            varName,
            varValue,
        )
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FV_writeToFilePathAndCreate    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FV_writeToFilePathAndCreate(
        filePath,
        varValue,
):
    """
    """
    baseDir = os.path.dirname(filePath)
    varName = os.path.basename(filePath)
    return(
        FV_writeToBaseDirAndCreate(
            baseDir,
            varName,
            varValue,
        )
    )
 
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FV_writeToBaseDirAndCreate    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FV_writeToBaseDirAndCreate(
        baseDir,
        varName,
        varValue,
):
    """
    """
    if not os.path.isdir(baseDir):
        try: os.makedirs(baseDir, 0775)
        except OSError: pass

    return(
        FV_writeToBaseDir(
            baseDir,
            varName,
            varValue,
        )
    )


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FV_writeToBaseDir    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FV_writeToBaseDir(
        baseDir,
        varName,
        varValue,
):
    """
    """
    if not os.path.isdir(baseDir):
        return None

    varValueFullPath = os.path.join(
        baseDir,
        varName
    )

    with open(varValueFullPath, "w") as valueFile:
        valueFile.write(str(varValue) +'\n')
        LOG_here("FILE_Param.writeTo path={path} value={value}".
                format(path=varValueFullPath, value=varValue))



"""
*  [[elisp:(org-cycle)][| ]]  /FILE_TreeObject/    :: *FILE_TreeObject: A Tree of Nodes and Leaves on Top Of file system* [[elisp:(org-cycle)][| ]]
**  [[elisp:(org-cycle)][| ]]  Subject      :: Facilitates building Tree hierarchies on the file system. [[elisp:(org-cycle)][| ]]
**  [[elisp:(org-cycle)][| ]]  Subject      :: Super Class for FILE_Param and ICM_Param [[elisp:(org-cycle)][| ]]
"""

FILE_TreeItemEnum = ucf.enum(
    'node',
    'leaf',
    'ignore',
    'ignoreLeaf',
    'ignoreNode'
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  FILE_TreeObject    [[elisp:(org-cycle)][| ]]
"""

class FILE_TreeObject(object):
    """Representation of a FILE_TreeObject in a file system directory (either a leaf or a node).

    This class is paralleled by /opt/public/osmt/bin/lcnObjectTree.libSh
    And is expected to be compatible with lcnObjectTree.libSh.

    A FILE_TreeObject is either a
       - FILE_TreeNode
       - FILE_TreeLeaf

    A FILE_TreeObject consists of:
       1) FileSysDir
       2) _tree_
       3) _treeProc_
       4) _objectType_

    _tree_  in bash  typeset -A treeItemEnum=(
    [node]=node                   # this dir is a node
    [leaf]=leaf                   # this dir is a leaf
    [ignore]=ignore               # ignore this and everything below it
    [ignoreLeaf]=ignoreLeaf       # ignore this leaf
    [ignoreNode]=ignoreNode       # ignore this node but continue traversing
)

    _objectTypes_  Known objectTypes are FILE_Param


    """

    def __init__(self,
                 fileSysPath,
                 ):
        '''Constructor'''
        self.__fileSysPath = fileSysPath

    def __str__(self):
        return  format(
            'value: ' + str(self.parValueGet()) +
            'read: ' + str(self.attrReadGet())
            )

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def nodeCreate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a node.
        """
        absFileSysPath = os.path.abspath(self.__fileSysPath)

        if not os.path.isdir(absFileSysPath):
            try: os.makedirs( absFileSysPath, 0777 )
            except OSError: pass

        thisFilePath= format(absFileSysPath + '/_tree_')
        with open(thisFilePath, "w") as thisFile:
             thisFile.write('node' +'\n')

    def leafCreate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """
        absFileSysPath = os.path.abspath(self.__fileSysPath)

        if not os.path.isdir(absFileSysPath):
            try: os.makedirs( absFileSysPath, 0777 )
            except OSError: pass

        thisFilePath= format(absFileSysPath + '/_tree_')
        with open(thisFilePath, "w") as thisFile:
             thisFile.write('leaf' +'\n')

    def validityPredicate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a verify that _tree_ is in place.
        """
        absFileSysPath = os.path.abspath(self.__fileSysPath)

        if not os.path.isdir(absFileSysPath):
            return 'NonExistent'

        filePathOf_tree_= format(absFileSysPath + '/_tree_')
        if not os.path.isfile(filePathOf_tree_):
            return 'NonExistent'

        lineString = open(filePathOf_tree_, 'r').read().strip()    # Making sure we get rid of \n on read()

        if lineString == 'node':
            return 'InPlace'
        else:
            EH_critical_usageError('lineString=' + lineString)
            return 'BadlyFormed'

    def nodePredicate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """
        print(self.__fileSysPath)

    def leafPredicate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """
        print(self.__fileSysPath)

    def nodeUpdate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """
        print(self.__fileSysPath)


    def leafUpdate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def nodesEffectiveList(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def leavesEffectiveList(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def nodesList(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def leavesList(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def treeObjectInfo(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def treeRecurse(self, command):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """



"""
*  [[elisp:(org-cycle)][| ]]  /FILE_Param/         :: *FILE_Param: File Parameter (FILE_ParamBase, FILE_Param, FILE_ParamDict)* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  FILE_ParamBase    [[elisp:(org-cycle)][| ]]
"""
class FILE_ParamBase(FILE_TreeObject):
    """Representation of a FILE_TreeObject when _objectType_ is FILE_ParamBase (a node).
    """
    def baseCreate(self):
        """  """
        return self.nodeCreate()

    def baseValidityPredicate(self):
        """  """
        return self.validityPredicate()


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  FILE_Param    [[elisp:(org-cycle)][| ]]
"""

class FILE_Param(object):
    """Representation of One FILE_Parameter.

    A FILE_Param consists of 3 parts
       1) ParameterName
       2) ParameterValue
       3) ParameterAttributes

    On the file system:
      1- name of directory is ParameterName
      2- content of ParameterName/value is ParameterValue
      3- rest of the files in ParameterName/ are ParameterAttributes.

    The concept of a FILE_Param dates back to [[http://www.qmailwiki.org/Qmail-control-files][Qmail Control Files]] (at least).
    A FILE_Param is broader than that concept in two respects.
     1) A FILE_Param is represented as a directory on the file system. This FILE_Param
        permits the parameter to have attributes beyond just a value. Other attributes
        are themselves in the form of a traditional filename/value.
     2) The scope of usage of a FILE_Param is any parameter not just a control parameter.


    We are deliberately not using a python dictionary to represent a FILE_Param
    instead it is a full fledged python-object.
    """

    def __init__(self,
                 parName=None,
                 parValue=None,
                 storeBase=None,
                 storeRoot=None,
                 storeRel=None,
                 attrRead=None,
                 ):
        '''Constructor'''
        self.__parName = parName
        self.__parValue = parValue
        self.__storeBase = storeBase   # storeBase = storeRoot + storeRel
        self.__storeRoot = storeRoot
        self.__storeRel = storeRel
        self.__attrRead = attrRead


    def __str__(self):
        return  format(
            str(self.parNameGet()) + ": " + str(self.parValueGet())
            )

    def parNameGet(self):
        """  """
        return self.__parName

    def parValueGet(self):
        """        """
        return self.__parValue

    def parValueGetLines(self):
        """        """
        if self.__parValue == None:
            return None
        return self.__parValue.splitlines()

    def parValueSet(self, value):
        """        """
        self.__parValue = value

    def attrReadGet(self):
        """        """
        return self.__attrRead

    def attrReadSet(self, attrRead):
        """        """
        self.__attrRead = attrRead

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def readFrom(self, storeBase=None, parName=None):
        """Read into a FILE_param content of parBase/parName.

        Returns a FILE_param which was contailed in parBase/parName.
        """
        if self.__storeBase == None and storeBase == None:
            return EH_problem_usageError("storeBase")

        if self.__parName == None and parName == None:
            return EH_problem_usageError("parName")

        if storeBase:
            self.__storeBase = storeBase

        if parName:
            self.__parName = parName

        self.__parName = parName

        parNameFullPath = os.path.join(self.__storeBase, parName)

        return self.readFromPath(parNameFullPath)

    # Undecorated because called before initialization
    #@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def readFromPath(self, parNameFullPath):
        """Read into a FILE_param content of parBase/parName.

        Returns a FILE_param which was contailed in parBase/parName.
        """

        if not os.path.isdir(parNameFullPath):
            #return EH_problem_usageError("parName: " + parNameFullPath)
            return None

        fileParam = self

        fileParam.__parName = os.path.basename(parNameFullPath)

        #
        # Now we will fill fileParam based on the directory content
        #
        for item in os.listdir(parNameFullPath):
            if item == "CVS":
                continue
            fileFullPath = os.path.join(parNameFullPath, item)
            if os.path.isfile(fileFullPath):
                if item == 'value':
                    lineString = open(fileFullPath, 'r').read().strip()    # Making sure we get rid of \n on read()
                    self.parValueSet(lineString)
                    continue

                # Rest of the files are expected to be attributes

                #lineString = open(fileFullPath, 'r').read()
                # NOTYET, check for exceptions
                #eval('self.attr' + str(item).title() + 'Set(lineString)')
            #else:
                #EH_problem_usageError("Unexpected Non-File: " + fileFullPath)

        return fileParam


    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def writeTo(self, storeBase=None, parName=None, parValue=None):
        """Write this FILE_Param to storeBase.

        """
        if self.__storeBase == None and storeBase == None:
            return EH_problem_usageError("storeBase")

        if self.__parName == None and parName == None:
            return EH_problem_usageError("parName")

        if self.__parValue == None and parValue == None:
            return EH_problem_usageError("parValue")

        if storeBase:
            self.__storeBase = storeBase

        if parName:
            self.__parName = parName
        else:
            parName = self.__parName

        if parValue:
            self.__parValue = parValue
        else:
            parValue = self.__parValue

        parNameFullPath = os.path.join(self.__storeBase, parName)
        try: os.makedirs( parNameFullPath, 0777 )
        except OSError: pass

        fileTreeObject = FILE_TreeObject(parNameFullPath)

        fileTreeObject.leafCreate()

        parValueFullPath = os.path.join(parNameFullPath, 'value')
        with open(parValueFullPath, "w") as valueFile:
             valueFile.write(str(parValue) +'\n')
             LOG_here("FILE_Param.writeTo path={path} value={value}".
                      format(path=parValueFullPath, value=parValue))

        return parNameFullPath


    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def writeToPath(self, parNameFullPath=None, parValue=None):
        """Write this FILE_Param to storeBase.
        """

        return self.writeTo(storeBase=os.path.dirname(parNameFullPath),
                            parName=os.path.basename(parNameFullPath),
                            parValue=parValue)                 

        
    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def writeToFromFile(self, storeBase=None, parName=None, parValueFile=None):
        """Write this FILE_Param to storeBase.

        """
        if self.__storeBase == None and storeBase == None:
            return EH_problem_usageError("storeBase")

        if self.__parName == None and parName == None:
            return EH_problem_usageError("parName")

        if parValueFile == None:
             return EH_problem_usageError("parValueFile")

        if storeBase:
            self.__storeBase = storeBase

        if parName:
            self.__parName = parName
        else:
            parName = self.__parName

        # if parValue:
        #     self.__parValue = parValue
        # else:
        #     parValue = self.__parValue

        parNameFullPath = os.path.join(self.__storeBase, parName)
        try: os.makedirs( parNameFullPath, 0777 )
        except OSError: pass

        fileTreeObject = FILE_TreeObject(parNameFullPath)

        fileTreeObject.leafCreate()

        parValueFullPath = os.path.join(parNameFullPath, 'value')
        with open(parValueFullPath, "w") as valueFile:
            with open(parValueFile, "r") as inFile:
                for line in inFile:
                    valueFile.write(line)

        return parNameFullPath


    def reCreationString(self):
        """Provide the string needed to recreate this object.

        """
        return

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_ParamWriteTo    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_ParamWriteTo(parRoot=None,
                      parName=None,
                      parValue=None,
                      ):
    """
    """

    thisFileParam = FILE_Param(parName=parName, parValue=parValue,)

    if thisFileParam == None:
        return EH_critical_usageError('')

    return thisFileParam.writeTo(storeBase=parRoot)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_ParamWriteToPath    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_ParamWriteToPath(parNameFullPath=None,
                          parValue=None,
                          ):
    """
    """

    thisFileParam = FILE_Param()

    if thisFileParam == None:
        return EH_critical_usageError('')

    return thisFileParam.writeToPath(parNameFullPath=parNameFullPath,
                                     parValue=parValue)

    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_ParamWriteToFromFile    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_ParamWriteToFromFile(parRoot=None,
                      parName=None,
                      parValueFile=None,
                      ):
    """
    """

    thisFileParam = FILE_Param(parName=parName)

    if thisFileParam == None:
        return EH_critical_usageError('')

    return thisFileParam.writeToFromFile(storeBase=parRoot, parValueFile=parValueFile)


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_ParamReadFrom    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_ParamReadFrom(parRoot=None,
                      parName=None,
                      parVerTag=None,
                      ):
    blank = FILE_Param()

    if blank == None:
        return EH_critical_usageError('blank')

    filePar = blank.readFrom(storeBase=parRoot, parName=parName)

    if filePar == None:
        #print('Missing: ' + parRoot + parName)
        raise IOError
        #return EH_critical_usageError('blank')
        return None

    return filePar

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_ParamValueReadFrom    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_ParamValueReadFrom(parRoot=None,
                      parName=None,
                      parVerTag=None,
                      ):
    blank = FILE_Param()

    if blank == None:
        return EH_critical_usageError('blank')

    filePar = blank.readFrom(storeBase=parRoot, parName=parName)

    if filePar == None:
        print('Missing: ' + parRoot + parName)
        #raise IOError        
        #return EH_critical_usageError('blank')
        return None        

    return(filePar.parValueGet())


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_ParamReadFromPath    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_ParamReadFromPath(parRoot=None,
                      parVerTag=None,
                      ):
    blank = FILE_Param()

    if blank == None:
        return EH_critical_usageError('blank')

    filePar = blank.readFromPath(parRoot)

    if filePar == None:
        #print('Missing: ' + parRoot + parName)
        raise IOError
        #return EH_critical_usageError('blank')        

    return filePar


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_ParamValueReadFromPath    [[elisp:(org-cycle)][| ]]
"""
#@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_ParamValueReadFromPath(parRoot=None,
                      parVerTag=None,
                      ):
    blank = FILE_Param()

    if blank == None:
        return EH_critical_usageError('blank')

    filePar = blank.readFromPath(parRoot)

    if filePar == None:
        print('Missing: ' + parRoot)
        return EH_critical_usageError('blank')

    return(filePar.parValueGet())


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_ParamVerWriteTo    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_ParamVerWriteTo(parRoot=None,
                      parName=None,
                      parVerTag=None,
                      parValue=None,
                      ):
    """ Given ticmoBase, Create parName, then assign parValue to parVerTag
    """

    parFullPath = os.path.join(parRoot, parName)
    try: os.makedirs( parFullPath, 0777 )
    except OSError: pass

    thisFileParam = FILE_Param(parName=parVerTag,
                                    parValue=parValue,
                                    )

    if thisFileParam == None:
        return EH_critical_usageError('')

    return thisFileParam.writeTo(storeBase=parFullPath)


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_ParamVerReadFrom    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_ParamVerReadFrom(parRoot=None,
                      parName=None,
                      parVerTag=None,
                      ):
    blank = FILE_Param()

    if blank == None:
        try:  EH_critical_usageError('blank')
        except RuntimeError:  return

    parFullPath = os.path.join(parRoot, parName)
    try: os.makedirs( parFullPath, 0777 )
    except OSError: pass


    filePar = blank.readFrom(storeBase=parFullPath, parName=parVerTag)

    if filePar == None:
        #print('Missing: ' + parRoot + parName)
        return EH_critical_usageError('blank')

    #print(filePar.parValueGet())
    return filePar



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  FILE_ParamDict    [[elisp:(org-cycle)][| ]]
"""

class FILE_ParamDict(object):
    """Maintain a list of FILE_Params.

    NOTYET, nesting of dictionaries.
    """

    def __init__(self):
        self.__fileParamDict = dict()

    def parDictAdd(self, fileParam=None):
        """        """
        self.__fileParamDict.update({fileParam.parNameGet():fileParam})

    def parDictGet(self):
        """        """
        return self.__fileParamDict

    def parNameFind(self, parName=None):
        """        """
        return self.__fileParamDict[parName]

    def readFrom(self, path=None):
        """Read each file's content into a FLAT dictionary item with the filename as key.

        Returns a Dictionary of paramName:FILE_Param.
        """

        absolutePath = os.path.abspath(path)

        if not os.path.isdir(absolutePath):
            return None

        for item in os.listdir(absolutePath):
            fileFullPath = os.path.join(absolutePath, item)
            if os.path.isdir(fileFullPath):

                blank = FILE_Param()

                itemParam = blank.readFrom(storeBase=absolutePath, parName=item)

                self.parDictAdd(itemParam)

        return self.__fileParamDict

 
    
"""
*  [[elisp:(org-cycle)][| ]]  /FILE_paramDictRead/ :: *FILE_paramDictRead:* (CMND) [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_paramDictRead    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_paramDictRead(interactive=Interactivity.Both,
                      inPathList=None):
    """ Old Style CMND
    """
    try: callableEntryEnhancer(type='cmnd')
    except StopIteration:  return(ReturnCode.ExtractionSuccess)

    G = IcmGlobalContext()
    G.curFuncNameSet(ucf.FUNC_currentGet().__name__)

    if Interactivity().interactiveInvokation(interactive):
        icmRunArgs = G.icmRunArgsGet()
        if cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=int__gt):
            return(ReturnCode.UsageError)
    
        inPathList = []
        for thisPath in icmRunArgs.cmndArgs:
            inPathList.append(thisPath)
    else:
        if inPathList == None:
            return EH_critical_usageError('inPathList is None and is Non-Interactive')                    

    for thisPath in inPathList:
        blankDict = FILE_ParamDict()
        thisParamDict = blankDict.readFrom(path=thisPath)
        TM_here('path=' + thisPath)

        if thisParamDict == None:
            continue

        for parName, filePar  in thisParamDict.iteritems():
            print('parName=' + parName)
            if filePar == None:
                continue
            thisValue=filePar.parValueGetLines()
            if thisValue == None:
                TM_here("Skipping: " + filePar.parNameGet())
                continue
            print(
                filePar.parNameGet() +
                '=' +
                thisValue[0])
    return

subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FP_readTreeAtBaseDir_fNOT(
        interactive=False,
        outcome=None,
        FPsDir=None,
):
    """Is also be exposed as an CMND."""
    if not outcome:
        outcome = OpOutcome()
    
    blankParDictObj  = FILE_ParamDict()
    thisParamDict = blankParDictObj.readFrom(path=FPsDir)
    TM_here('path=' + FPsDir)

    if thisParamDict == None:
        return eh_problem_usageError(
            outcome,
            "thisParamDict == None",
        )

    if interactive:
        ANN_write(FPsDir)
        FILE_paramDictPrint(thisParamDict)

    return outcome.set(
        opError=OpError.Success,
        opResults=thisParamDict,
    )

####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "lib" :cmndName "FP_readTreeAtBaseDir" :comment "" :parsMand "FPsDir" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /FP_readTreeAtBaseDir/ parsMand=FPsDir parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class FP_readTreeAtBaseDir(Cmnd):
    cmndParamsMandatory = [ 'FPsDir', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        FPsDir=None,         # or Cmnd-Input
    ):
        G = IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'FPsDir': FPsDir, }
        if not cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        FPsDir = callParamsDict['FPsDir']
####+END:
        #G = IcmGlobalContext()        

        # return FP_readTreeAtBaseDir_f(
        #     interactive=interactive,
        #     outcome = cmndOutcome,          
        #     FPsDir=FPsDir,
        # )

        blankParDictObj  = FILE_ParamDict()
        thisParamDict = blankParDictObj.readFrom(path=FPsDir)
        TM_here('path=' + FPsDir)

        if thisParamDict == None:
            return eh_problem_usageError(
                cmndOutcome,
                "thisParamDict == None",
            )

        if interactive:
            ANN_write(FPsDir)
            FILE_paramDictPrint(thisParamDict)

        return cmndOutcome.set(
            opError=OpError.Success,
            opResults=thisParamDict,
        )

    def cmndDocStr(self): return """
** Reads and recurses through all FPs.  [[elisp:(org-cycle)][| ]]
*** When interactive, also prints out parValues as read.
"""
    

def cmndCallParamsValidate(
        callParamDict,
        interactive,
        outcome=None,
        
):
    """Expected to be used in all CMNDs.

Usage Pattern:

    if not icm.cmndCallParamValidate(FPsDir, interactive, outcome=cmndOutcome):
       return cmndOutcome
"""
    #G = IcmGlobalContext()
    #if type(callParamOrList) is not list: callParamOrList = [ callParamOrList ]

    if not outcome:
        outcome = OpOutcome()

    for key  in callParamDict:
        #print key
        if not callParamDict[key]:
            if not interactive:
                return eh_problem_usageError(
                    outcome,
                    "Missing Non-Interactive Arg {}".format(key),
                )
            exec("callParamDict[key] = IcmGlobalContext().usageParams." + key)
            
    return True

         

def FILE_paramDictPrint(fileParamDict):
    """ Returns a Dictionary of paramName:FILE_Param.        """
    for parName, filePar  in fileParamDict.iteritems():
        #print('parName=' + parName)
        if filePar == None:
            continue
        thisValue=filePar.parValueGetLines()
        if thisValue == None:
            TM_here("Skipping: " + filePar.parNameGet())
            continue
        if thisValue:
            print(
                filePar.parNameGet() +
                '=' +
                thisValue[0])
        else: # Empty list
            print(
                filePar.parNameGet() +
                '=')



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_paramDictReadDeep    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_paramDictReadDeep(interactive=Interactivity.Both,
                      inPathList=None):
    """
    """
    try: callableEntryEnhancer(type='cmnd')
    except StopIteration:  return(ReturnCode.ExtractionSuccess)

    G = IcmGlobalContext()
    G.curFuncNameSet(ucf.FUNC_currentGet().__name__)

    if Interactivity().interactiveInvokation(interactive):
        icmRunArgs = G.icmRunArgsGet()
        if cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=int__gt):
            return(ReturnCode.UsageError)
    
        inPathList = []
        for thisPath in icmRunArgs.cmndArgs:
            inPathList.append(thisPath)
    else:
        if inPathList == None:
            return EH_critical_usageError('inPathList is None and is Non-Interactive')                    

    for thisPath in inPathList:
        #absolutePath = os.path.abspath(thisPath)

        if not os.path.isdir(thisPath):
            return EH_critical_usageError('Missing Directory: {thisPath}'.format(thisPath=thisPath))

        for root, dirs, files in os.walk(thisPath):
            #print("root={root}".format(root=root))
            #print ("dirs={dirs}".format(dirs=dirs))
            #print ("files={files}".format(files=files))

            thisFileParamValueFile = os.path.join(root, "value")
            if os.path.isfile(thisFileParamValueFile):
                try:
                    fileParam = FILE_ParamReadFromPath(parRoot=root)
                except IOError:
                    EH_problem_info("Missing " + root)
                    continue

                print(root + "=" + fileParam.parValueGet())

    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FILE_parametersReadDeep_PlaceHolder    [[elisp:(org-cycle)][| ]]
"""

def FILE_parametersReadDeep_PlaceHolder(path=None):
    """Read each file's content into a DEEP dictionary item with the filename as key.

    Not Fully Implemeted YET.
    """
    retVal = None

    absolutePath = os.path.abspath(path)

    if not os.path.isdir(absolutePath):
        return retVal

    fileParamsDict = dict()

    for root, dirs, files in os.walk(absolutePath):
        # Each time that we see a dir we will create a new subDict
        print root
        print dirs
        print files

    return fileParamsDict


####+BEGIN: bx:icm:python:section :title "ICM_Param: ICM Parameter (ICM_Param, ICM_ParamDict)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM_Param: ICM Parameter (ICM_Param, ICM_ParamDict)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

ICM_ParamScope = ucf.enum('TargetParam', 'IcmGeneralParam', 'CmndSpecificParam')

####+BEGIN: bx:dblock:python:class :className "ICM_Param" :superClass "" :comment "" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /ICM_Param/ object  [[elisp:(org-cycle)][| ]]
"""
class ICM_Param(object):
####+END:
     """Representation of an Interactively Invokable Module Parameter (ICM_Param).

     An ICM Parameter is a superset of an argsparse parameter which also includes:
        - CMND relevance (Mandatory and Optional)
        - Maping onto FILE_Params


     ICM_Param is initially used to setup ArgParse and other user-interface parameter aspects.
     """

     def __init__(self,
                  parName=None,
                  parDescription=None,
                  parDataType=None,
                  parDefault=None,
                  parChoices=None,
                  parScope=None,
                  parMetavar=None,                  
                  parAction='store',                    # Same as argparse's action
                  parNargs=None,                        # Same as argparse's nargs
                  parCmndApplicability=None,             # List of CMNDs to which this ICM is applicable
                  argparseShortOpt=None,
                  argparseLongOpt=None,
                 ):
         '''Constructor'''
         self.__parName = parName
         self.__parValue = None
         self.__parCmndApplicability = parCmndApplicability
         self.__parDescription = parDescription
         self.__parDataType = parDataType
         self.__parDefault = parDefault
         self.__parChoices = parChoices
         self.__parMetavar = parMetavar         
         self.parActionSet(parAction)
         self.parNargsSet(parNargs)
         self.__argparseShortOpt =  argparseShortOpt
         self.__argparseLongOpt =  argparseLongOpt

     def __str__(self):
         return  format(
             'value: ' + str(self.parValueGet())
             )

     def parNameGet(self):
         """  """
         return self.__parName

     def parNameSet(self, parName):
         """        """
         self.__parName = parName

     def parValueGet(self):
         """        """
         return self.__parValue

     def parValueSet(self, value):
         """        """
         self.__parValue = value

     def parDescriptionGet(self):
         """        """
         return self.__parDescription

     def parDescriptionSet(self, parDescription):
         """        """
         self.__parDescription = parDescription

     def parDataTypeGet(self):
         """        """
         return self.__parDataType

     def parDataTypeSet(self, parDataType):
         """        """
         self.__parDataType = parDataType

     def parDefaultGet(self):
         """        """
         return self.__parDefault

     def parDefaultSet(self, parDefault):
         """        """
         self.__parDefault = parDefault

     def parChoicesGet(self):
         """        """
         return self.__parChoices

     def parChoicesSet(self, parChoices):
         """        """
         self.__parChoices = parChoices

     def parActionGet(self):
         """        """
         return self.__parAction

     def parActionSet(self, parAction):
         """        """
         self.__parAction = parAction

     def parNargsGet(self):
         """        """
         return self.__parNargs

     def parNargsSet(self, parNargs):
         """        """
         self.__parNargs = parNargs

     def argsparseShortOptGet(self):
         """        """
         return self.__argparseShortOpt

     def argsparseShortOptSet(self, argsparseShortOpt):
         """        """
         self.__argparseShortOpt = argsparseShortOpt

     def argsparseLongOptGet(self):
         """        """
         return self.__argparseLongOpt

     def argsparseLongOptSet(self, argsparseLongOpt):
         """        """
         self.__argparseLongOpt = argsparseLongOpt

     def readFrom(self, parRoot=None, parName=None):
         """Read into a FILE_param content of parBase/parName.

         Returns a FILE_param which was contailed in parBase/parName.
         """

         absoluteParRoot = os.path.abspath(parRoot)

         if not os.path.isdir(absoluteParRoot):
             return None

         absoluteParBase = os.path.join(absoluteParRoot, parName)

         if not os.path.isdir(absoluteParBase):
             return None

         fileParam = self

         self.__parName = parName

         #
         # Now we will fill fileParam based on the directory content
         #
         for item in os.listdir(absoluteParBase):
             fileFullPath = os.path.join(absoluteParBase, item)
             if os.path.isfile(fileFullPath):

                 if item == 'value':
                     lineString = open(fileFullPath, 'r').read()
                     self.parValueSet(lineString)
                     continue

                 # Rest of the files are expected to be attributes

                 lineString = open(fileFullPath, 'r').read()
                 # NOTYET, check for exceptions
                 eval('self.attr' + str(item).title() + 'Set(lineString)')

         return fileParam

     @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)     
     def writeAsFileParam(
             self,
             parRoot=None,
     ):
         """Writing a FILE_param content of self.

         Returns a FILE_param which was contailed in parBase/parName.
         """

         absoluteParRoot = os.path.abspath(parRoot)

         if not os.path.isdir(absoluteParRoot):
            try: os.makedirs( absoluteParRoot, 0775 )
            except OSError: pass
 
         #print absoluteParRoot

         #print 
         #print self.parValueGet()

         parValue = self.parValueGet()
         if not parValue:
             parValue = "unSet"
     
         FILE_ParamWriteTo(
             parRoot=absoluteParRoot,
             parName=self.parNameGet(),
             parValue=parValue,
         )

         varValueFullPath = os.path.join(
             absoluteParRoot,
             self.parNameGet(),
             'description'
         )

         FV_writeToFilePathAndCreate(
             filePath=varValueFullPath,
             varValue=self.parDescriptionGet(),
         )

         varValueBaseDir = os.path.join(
             absoluteParRoot,
             self.parNameGet(),
             'enums'
         )

         for thisChoice in self.parChoicesGet():
             FV_writeToBaseDirAndCreate(
                 baseDir=varValueBaseDir,
                 varName=thisChoice,
                 varValue="",
             )         
         
####+BEGIN: bx:dblock:python:class :className "ICM_ParamDict" :superClass "" :comment "" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /ICM_ParamDict/ object  [[elisp:(org-cycle)][| ]]
"""
class ICM_ParamDict(object):
####+END:
     """ICM Parameters Dictionary -- Collection of ICM_Param s can be placed in ICM_ParamDict

     From icmParamDict
     """

     def __init__(self):
         self.__icmParamDict = dict()

     def parDictAdd(self,
                    parName=None,
                    parDescription=None,
                    parDataType=None,
                    parMetavar=None,                                      
                    parDefault=None,
                    parChoices=None,
                    parScope=None,
                    parAction='store',
                    parNargs=None,
                    argparseShortOpt=None,
                    argparseLongOpt=None,
                   ):
         """        """
         thisParam = ICM_Param(parName=parName,
                               parDescription=parDescription,
                               parDataType=parDataType,
                               parMetavar=parMetavar,
                               parDefault=parDefault,
                               parChoices=parChoices,
                               parScope=parScope,
                               parAction=parAction,
                               parNargs=parNargs,
                               argparseShortOpt=argparseShortOpt,
                               argparseLongOpt=argparseLongOpt,
                               )

         self.parDictAppend(thisParam)

     def parDictAppend(self, icmParam=None):
         """        """
         self.__icmParamDict.update({icmParam.parNameGet():icmParam})


     def parDictGet(self):
         """        """
         return self.__icmParamDict

     def parNameFind(self, parName=None):
         """        """
         return self.__icmParamDict[parName]


     def cmndApplicabilityUpdate(self,
                                cmnd=None,
                                mandatoryParams=None,
                                optionalParams=None,
                                ):
         """NOTYET -- Verify That Mandatory and Optional Params for this cmnd have been specified At Runtime."""

         # if icmRunArgs.perfSap:
         #     print(icmRunArgs.perfSap)

         # if icmRunArgs.wsdlUrl:
         #     print(icmRunArgs.wsdlUrl)

         return


####+BEGIN: bx:icm:python:section :title "CmndArgs: Per Command Argument"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *CmndArgs: Per Command Argument*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:python:class :className "CmndArgSpec" :superClass "" :comment "" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /CmndArgSpec/ object  [[elisp:(org-cycle)][| ]]
"""
class CmndArgSpec(object):
####+END:
     """\
** Representation of an Interactively Command Module (ICM) Command Argument Sepecification(CmndArgSpec).
     """

     def __init__(
             self,
             argName=None,
             argDefault=None,
             argChoices=[],
             argDataType=None,
             argDescription=None,
     ):
         '''Constructor'''
         self.__argName = argName
         self.__argDefault = argDefault         
         self.__argValue = None
         self.__argDescription = argDescription
         self.__argDataType = argDataType
         self.__argChoices = argChoices

     def __str__(self):
         return  format(
             'value: ' + str(self.argValueGet())
             )

     def argNameGet(self):
         """  """
         return self.__argName

     def argNameSet(self, argName):
         """        """
         self.__argName = argName

     def argValueGet(self):
         """        """
         return self.__argValue

     def argValueSet(self, value):
         """        """
         self.__argValue = value

     def argDescriptionGet(self):
         """        """
         return self.__argDescription

     def argDescriptionSet(self, argDescription):
         """        """
         self.__argDescription = argDescription

     def argDataTypeGet(self):
         """        """
         return self.__argDataType

     def argDataTypeSet(self, argDataType):
         """        """
         self.__argDataType = argDataType

     def argDefaultGet(self):
         """        """
         return self.__argDefault

     def argDefaultSet(self, argDefault):
         """        """
         self.__argDefault = argDefault

     def argChoicesGet(self):
         """        """
         return self.__argChoices

     def argChoicesSet(self, argChoices):
         """        """
         self.__argChoices = argChoices
         

####+BEGIN: bx:dblock:python:class :className "CmndArgsSpecDict" :superClass "" :comment "" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /CmndArgsSpecDict/ object  [[elisp:(org-cycle)][| ]]
"""
class CmndArgsSpecDict(object):
####+END:
     """ICM Argameters Dictionary -- Collection of ICM_Argam s can be placed in ICM_ArgamDict

     From icmArgamDict
     """

     def __init__(self):
         self.__cmndArgsSpecDict = dict()

     def argsDictAdd(
             self,
             argPosition=None,
             argName=None,
             argDefault=None,
             argDescription=None,             
             argDataType=None,
             argChoices=None,
     ):
         """        """
         thisArgSpec = CmndArgSpec(
             argName=argName,
             argDefault=argDefault,
             argDescription=argDescription,
             argDataType=argDataType,
             argChoices=argChoices,
         )

         self.argDictAppend(argPosition, thisArgSpec)

     def argDictAppend(
             self,
             argPosition,
             cmndArgSpec,
     ):
         """        """
         self.__cmndArgsSpecDict.update({argPosition:cmndArgSpec})

     def argDictGet(self):
         """        """
         return self.__cmndArgsSpecDict

     def argPositionFind(self, argPosition=None):
         """        """
         return self.__cmndArgsSpecDict[argPosition]


     
"""
*  [[elisp:(org-cycle)][| ]]  /ICM Output/         :: *icmOutputBaseGet -- icmOutputXlsGetPath(fileBaseName)* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmOutputBaseGet    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def icmOutputBaseGet():
    return "./"

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmOutputXlsGetPath    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def icmOutputXlsGetPath(fileBaseName):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%y%m%d%H%M%S')
    fileName = fileBaseName + st + ".xlsx"
    return os.path.join(icmOutputBaseGet(), fileName)

"""
*  [[elisp:(org-cycle)][| ]]  /ICM Lib/            :: *percentage, runOnceOnly, setAdjust*  [[elisp:(org-cycle)][| ]]
"""


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  /G_/                 :: *IcmGlobalContext (G_) -- Class, ICM Singleton, provides global context* [[elisp:(org-cycle)][| ]]
"""


ICM_GroupingType = ucf.enum(
    'Pkged',
    'Grouped',
    'Scattered',
    'Unitary',
    'Standalone',
    'Other',
    'UnSet',    
)

ICM_PkgedModel = ucf.enum(
    'BasicPkg',
    'ToicmPkg',
    'EmpnaPkg',
    'UnSet',    
)

ICM_CmndParts = ucf.enum(
    'Common',
    'Param',
    'Target',
    'Bxo',
    'Bxsrf',        
    'UnSet',    
)

AuxInvokationContext = ucf.enum(
    'UnSet',        
    'IcmRole',
    'CmndParamsAndArgs',
    'DocString',
)
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  IcmGlobalContext    [[elisp:(org-cycle)][| ]]
"""

class IcmGlobalContext():
     """ Singleton: Interactively Invokable Module Global Context.
     """

     icmArgsParser = None
     
     #icmRunArgsThis = None
     icmRunArgsThis = []     
     icmParamDict = None       # ICM Specified Parameters in g_argsExtraSpecify()
     thisFuncName = None
     logger = None
     astModuleFunctionsList = None
     
     usageParams = ucf.Variables
     usageArgs = ucf.Variables

     # ICM-Profile Specifications
     icmGroupingType = ICM_GroupingType.UnSet
     icmPkgedModel = ICM_PkgedModel.UnSet
     icmCmndPartsList = [ICM_CmndParts.UnSet]

     _auxInvokationContext = AuxInvokationContext.UnSet
     _auxInvokationResults = None
     _cmndNames = None # All 3 of the above have been obsoleted
     
     _cmndFuncsDict = None
     _cmndMethodsDict = None

     lastOpOutcome = None

     def __init__(self):
         pass

     def globalContextSet(self,
                          icmRunArgs=None,
                          icmParamDict=None
                          ):
         """
         """
         #if not icmRunArgs == None:
         self.__class__.icmRunArgsThis = icmRunArgs

         # NOTYET, 2017 -- Review This
         if icmParamDict == None:
             pass
             #self.__class__.icmParamDict = ICM_ParamDict()

         logger = logging.getLogger(LOGGER)
         self.__class__.logger = logger

         self.__class__.astModuleFunctionsList = ucf.ast_topLevelFunctionsInFile(
             self.icmMyFullName()
         )

     def icmRunArgsGet(self):
         return self.__class__.icmRunArgsThis

     def icmParamDictSet(self, icmParamDict):
         self.__class__.icmParamDict = icmParamDict

     def icmParamDictGet(self):
         return self.__class__.icmParamDict

     def icmMyFullName(self):
          return os.path.abspath(sys.argv[0])

     def icmMyName(self):
         return os.path.basename(sys.argv[0])

     def icmModuleFunctionsList(self):
         return self.__class__.astModuleFunctionsList
     
     def curFuncNameSet(self, curFuncName):
         self.__class__.thisFuncName = curFuncName

     def curFuncName(self):
         return self.__class__.thisFuncName

     def auxInvokationContextSet(self, auxInvokationEnum):
         self.__class__._auxInvokationContext = auxInvokationEnum

     def auxInvokationContext(self):
         return self.__class__._auxInvokationContext

     def auxInvokationResultsSet(self, auxInvokationRes):
         self.__class__._auxInvokationResults = auxInvokationRes

     def auxInvokationResults(self):
         return self.__class__._auxInvokationResults

     def cmndNamesSet(self, cmnds):
         self.__class__._cmndNames = cmnds

     def cmndNames(self):
         return self.__class__._cmndNames

     def cmndMethodsDictSet(self, cmnds):
         self.__class__._cmndMethodsDict = cmnds

     def cmndMethodsDict(self):
         return self.__class__._cmndMethodsDict

     def cmndFuncsDictSet(self, cmnds):
         self.__class__._cmndFuncsDict = cmnds

     def cmndFuncsDict(self):
         return self.__class__._cmndFuncsDict

G = IcmGlobalContext()     
G.icmLibsAppend = __file__
G.icmCmndsLibsAppend = __file__

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  commonIcmParamsParser    [[elisp:(org-cycle)][| ]]
"""     
def commonIcmParamsParser(parser):
    """Module Common Command Line Parameters.

    NOTYET -- Needs To Be Called
    """
    icmParams = commonIcmParamsPrep()

    argsparseBasedOnIcmParams(parser, icmParams)

    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  commonIcmParamsPrep    [[elisp:(org-cycle)][| ]]
"""
def commonIcmParamsPrep():
    """Module Common Command Line Parameters.
    """
    icmParams = ICM_ParamDict()

    icmParams.parDictAdd(
        parAction='append',
        parName='callTrackings',
        parDescription="Set monitoring of calls and selected invokes.",
        parDataType=None,
        parDefault=[],
        parChoices=['invoke+', 'invoke-', 'monitor+', 'monitor-'],
        parScope=ICM_ParamScope.TargetParam,
        argparseShortOpt='-t',
        argparseLongOpt='--callTrackings',
        )
       
    icmParams.parDictAdd(
        parAction='store',
        parName='runMode',
        parDescription="Run Mode as fullRun or dryRun",
        parDataType=None,
        parDefault='fullRun',
        parChoices=['dryRun', 'fullRun', 'runDebug'],
        parScope=ICM_ParamScope.TargetParam,
        #argparseShortOpt='-r',
        argparseLongOpt='--runMode',
        )
       
    icmParams.parDictAdd(
        parAction='store',
        parName='verbosity',
        parDescription='Adds a Console Logger for the level specified in the range 1..50',
        parDataType=None,
        parDefault='30',
        parMetavar='ARG',
        parChoices=['1', '10', '20', '30', '40', '50',],
        parScope=ICM_ParamScope.TargetParam,
        argparseShortOpt='-v',        
        argparseLongOpt='--verbosity',
        )
       
    icmParams.parDictAdd(
        parAction='store',
        parName='logFile',
        parDescription='Specifies destination LogFile for this run',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=ICM_ParamScope.TargetParam,
        #argparseShortOpt='-v',        
        argparseLongOpt='--logFile',
        )

    icmParams.parDictAdd(
        parAction='store',
        parName='logFileLevel',
        parDescription='Specifies destination LogFile for this run',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=ICM_ParamScope.TargetParam,
        #argparseShortOpt='-v',        
        argparseLongOpt='--logFileLevel',
        )

    icmParams.parDictAdd(
        parAction='store_true',
        parName='docstring',
        parDescription='Docstring',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=ICM_ParamScope.TargetParam,
        #argparseShortOpt='-v',        
        argparseLongOpt='--logFileLevel',
        )
    
    # icmParams.parDictAdd(
    #     parAction='store',
    #     parName='cmndArgs',
    #     parDescription='Docstring',
    #     parDataType=None,
    #     parDefault=None,
    #     parMetavar='ARG',
    #     parChoices=None,
    #     parScope=ICM_ParamScope.TargetParam,
    #     #argparseShortOpt='-v',        
    #     argparseLongOpt='--logFileLevel',
    #     )
    

    icmParams.parDictAdd(
        parAction='append',
        parName='loadfiles',
        parDescription='Load Files',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=ICM_ParamScope.TargetParam,
        #argparseShortOpt='-l',        
        argparseLongOpt='--load',
        )
    
    return icmParams

     
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  argsCommonProc -- Obsoleted By commonIcmParamsPrep??   [[elisp:(org-cycle)][| ]]
"""
#@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def argsCommonProc(parser):

     parser.add_argument(
         '-i',
         '--invokes',
         dest='invokes',
         action='append'
         )

     parser.add_argument(
         '-t',
         '--callTrackings',
         dest='callTrackings',
         action='append',
         choices=['invoke+', 'invoke-', 'monitor+', 'monitor-'],
         default=[]
         )

     parser.add_argument(
         '--runMode',
         dest='runMode',
         action='store',
         choices=['dryRun', 'fullRun', 'runDebug'],
         default='fullRun'
         )

     parser.add_argument(
         '-v',
         '--verbosity',
         dest='verbosityLevel',
         metavar='ARG',
         action='store',
         default=None,
         help='Adds a Console Logger for the level specified in the range 1..50'
         )

     parser.add_argument(
         '--logFile',
         dest='logFile',
         metavar='ARG',
         action='store',
         default=None,
         help='Specifies destination LogFile for this run'
         )

     parser.add_argument(
         '--logFileLevel',
         dest='logFileLevel',
         metavar='ARG',
         action='store',
         default=None,
         help=''
         )

     parser.add_argument(
         '--docstring',
         action='store_true',
         dest="docstring"
         )

     parser.add_argument(
         'cmndArgs',
     #dest='cmndArgs',   #
         metavar='CMND',
         nargs='*',
         action='store',
         help='Interactively Invokable Function Arguments'
         )

     parser.add_argument(
         '--load',
         dest='loadFiles',
         action='append',
         default=[]
         )

     return

"""
*  [[elisp:(org-cycle)][| ]]  getopt.args   :: Arguments Parsing -- G_argsProc based on argparse [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  G_argsProc    [[elisp:(org-cycle)][| ]]
"""
#@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def G_argsProc(arguments, extraArgs):
     """ICM-ICM Argument Parser.

     extraArgs resides in the G_ module.
     """

     parser = argparse.ArgumentParser(
         description=__doc__
         )

     argsCommonProc(parser)
     #commonIcmParamsPrep()

     if extraArgs:
        extraArgs(parser)

     #
     # The logic below breaks multiple --invokes.
     # Perhaps a distinction between --invoke and --invokes is an answer.
     #
     # We are inserting "--" after -i cmnd
     # to get things like -i run pip install --verbose
     #
     #
     index = 0
     for each in arguments:
         if each == "-i":
             arguments.insert(index+2, "--")
             break
         if each == "--invokes":            
             arguments.insert(index+2, "--")
             break
         index = index + 1

     args = parser.parse_args(arguments)

     return args, parser


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  argsparseBasedOnIcmParams    [[elisp:(org-cycle)][| ]]
"""
#subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def argsparseBasedOnIcmParams(parser, icmParams):
     """Convert icmParams to parser
**  [[elisp:(org-cycle)][| ]]  Subject      :: type= is missing -- [[elisp:(org-cycle)][| ]]
     """


     for key, icmParam in icmParams.parDictGet().iteritems():
         if ( icmParam.argsparseShortOptGet() == None )  and ( icmParam.argsparseLongOptGet() == None ):
             break

         if not icmParam.argsparseShortOptGet() == None:
             parser.add_argument(
                 icmParam.argsparseShortOptGet(),
                 icmParam.argsparseLongOptGet(),
                 dest = icmParam.parNameGet(),
                 nargs = icmParam.parNargsGet(),
                 action=icmParam.parActionGet(),
                 default = icmParam.parDefaultGet(),
                 help=icmParam.parDescriptionGet()
                 )
         else:
             parser.add_argument(
                icmParam.argsparseLongOptGet(),
                dest = icmParam.parNameGet(),
                nargs = icmParam.parNargsGet(),
                metavar = 'ARG',
                action=icmParam.parActionGet(),
                default = icmParam.parDefaultGet(),
                help=icmParam.parDescriptionGet()
                )

     return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmParamsToFileParamsUpdate    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def icmParamsToFileParamsUpdate(
        parRoot,
        icmParams,
):
     """Convert icmParams to parser
**  [[elisp:(org-cycle)][| ]]  Subject      :: type= is missing -- [[elisp:(org-cycle)][| ]]
     """

     LOG_here("Updating icmParams at: {parRoot}".format(parRoot=parRoot))
     
     for key, icmParam in icmParams.parDictGet().iteritems():
         if ( icmParam.argsparseShortOptGet() == None )  and ( icmParam.argsparseLongOptGet() == None ):
             break
         
         icmParam.writeAsFileParam(
             parRoot=parRoot,
         )
         
     return
 
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndParamsMandatoryAssert    [[elisp:(org-cycle)][| ]]
"""

def cmndParamsMandatoryAssert(paramsList):
        for key, value in paramsList.iteritems():
            if value == None: return(EH_critical_usageError(key))
            

"""
*  [[elisp:(org-cycle)][| ]]  /G_ examples/        :: *G_commonExamples -- Common features included in G_examples() + devExamples(), etc* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  commonExamples    [[elisp:(org-cycle)][| ]]
"""
class commonExamples(Cmnd):
    """Print common ICM examples."""

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)    
    def cmnd(self,
            interactive=True,
    ):
        """Provide a menu of common icm examples.
"""
        G_myFullName = sys.argv[0]
        G_myName = os.path.basename(G_myFullName)

        cmndExampleMenuChapter('/Intercatively Invokable Module (ICM) General Usage Model/')

        print( G_myName + " --help" )
        print( G_myName + " -i model" )
        print( G_myName + " -i icmHelp" )
        print( G_myName + " -i icmOptionsExamples" )
        print( G_myName + " -i icmInfo" )
        print( G_myName + " -i icmInUpdate ./var" )        
        print( G_myName + " -i cmndInfo cmndName" )
        print( G_myName + " -i cmndInfo cmndInfo" )                
        print( G_myName + " -i devExamples" )
        print( G_myName + " -i describe" )
        print( G_myName + " -i describe" + " |" + " emlVisit")
        print( G_myName + " -i examples" )
        print( G_myName + " -i examples" + " |" + " icmToEmlVisit")

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  G_commonBriefExamples    [[elisp:(org-cycle)][| ]]
"""
#@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def G_commonBriefExamples(interactive=False):

     G_myFullName = sys.argv[0]
     G_myName = os.path.basename(G_myFullName)

     cmndExampleMenuChapter('/Intercatively Invokable Module (ICM) Brief Usage Model/')

     print( G_myName + " -i commonExamples" + "    # Help, Model, icmOptionsExample")
     print( G_myName + " -i describe" + " |" + " emlVisit")
     print( G_myName + " -i examples" + " |" + " icmToEmlVisit")
     print( G_myName + " -i visit")     
     print( """emlVisit -v -n showRun -i gotoPanel """ + G_myFullName)

     cmndExampleMenuChapter('*ICM Blee Player Invokations*')
     ANN_write("icmPlayer.sh -h -v -n showRun -i grouped {G_myName}".format(G_myName=G_myName))     

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  devExamples    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def devExamples(interactive=False):

     G_myName = sys.argv[0]

     print("======== Development =========")

     print("python -m trace -l " + G_myName + " | egrep -v " + '\'/python2.7/|\<string\>\'')
     print("python -m trace -l " + G_myName)
     print("python -m trace -t " + G_myName)


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmOptionsExamples    [[elisp:(org-cycle)][| ]]
"""

class icmOptionsExamples(Cmnd):
    """Print a summary of the ICM Model."""

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)    
    def cmnd(self,
            interactive=True,
    ):
 
        G_myFullName = sys.argv[0]
        G_myName = os.path.basename(G_myFullName)

        print("==== cmndEx Built-In Feature Examples =====")

        print( G_myName + " -i icm.cmndExample arg1 arg2" )
        print( G_myName + " -v 20" + " -i icm.cmndExample arg1 arg2" )
        print( G_myName + " -v 1" + " -i icm.cmndExample arg1 arg2" )
        print( G_myName + " --runMode dryRun" + " -i icm.cmndExample arg1 arg2" )
        print( G_myName + " -v 1" + " --callTrackings monitor-" + " -i icm.cmndExample arg1 arg2" )
        print( G_myName + " -v 1" + " --callTrackings monitor+" + " --callTrackings invoke+" + " -i icm.cmndExample arg1 arg2" )
        print( G_myName + " -v 1" + " --callTrackings monitor-" + " --callTrackings invoke-" + " -i icm.cmndExample arg1 arg2" )
        print( G_myName + " --docstring" + " -i describe" )



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmExampleMyName    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def icmExampleMyName(myName, myFullName):
    """
    """
    print("#######  " + '  *' + myName + '*  ' + "  ##########")
    print("=======  " + myFullName + "  ===========")

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || CMND       ::  ex_gCommon    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def ex_gCommon():
    """."""
    G = IcmGlobalContext()
    icmExampleMyName(G.icmMyName(), G.icmMyFullName())
    G_commonBriefExamples()    
    #G_commonExamples()

"""
*  [[elisp:(org-cycle)][| ]]  /example Seps/       :: *cmndExample -- Simple Usage Example -- Seperators* [[elisp:(org-cycle)][| ]]
"""



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndExampleMenuChapter    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def cmndExampleMenuChapter(title):
    """
    """
    print("#######  " + title + "  ##########")


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndExampleMenuSection    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def cmndExampleMenuSection(title):
     """
     """
     print("=======  " + title + "  ==========")


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndExampleMenuSubSection    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def cmndExampleMenuSubSection(title):
     """  """
     print("%%%%%%%  " + title + "  %%%%%%%%%%%")


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndExampleMenuItem    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def cmndExampleMenuItem(
        commandLine,
        icmName=None,          # Defaults to G_myName
        verbosity='basic',
        comment='none',
        icmWrapper=None,
):
    """ vebosity is one of: 'none', 'little', 'some',  'full'
    """
    G_myFullName = sys.argv[0]
    G_myName = os.path.basename(G_myFullName)

    if comment == 'none':
        fullCommandLine = commandLine
    else:
        fullCommandLine = commandLine + '         ' + comment

    if icmName:
        G_myName = icmName
        
    if icmWrapper:
        G_myName = icmWrapper + " " + G_myName

    if verbosity == 'none':
        #print( G_myName + " -v 30" + " " + fullCommandLine)
        print( G_myName + " " + fullCommandLine)        
    elif verbosity == 'basic':
        print( G_myName + " -v 1"  + " " + fullCommandLine )
    elif verbosity == 'little':
        print( G_myName + " -v 20" + " " + fullCommandLine )
    elif verbosity == 'some':
        print( G_myName + " -v 1"  + " --callTrackings monitor-" + " --callTrackings invoke-" + " " + fullCommandLine )
    elif verbosity == 'full':
        print( G_myName + " -v 1"  + " --callTrackings monitor+" + " --callTrackings invoke+" + " " + fullCommandLine )
    else:
        return EH_critical_oops('')

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ex_gCmndMenuItem    [[elisp:(org-cycle)][| ]]
"""    
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def ex_gCmndMenuItem(
        cmndName,    # String
        cmndPars,    # Dictionary
        cmndArgs,    # String
        verbosity='basic',
        comment='none',
        icmWrapper=None,
        icmName=None,
):
    """ vebosity is one of: 'none', 'little', 'some',  'full'
    """

    cmndParsStr = ""
    for key in cmndPars:
        cmndParsStr += """--{parName}="{parValue}" """.format(parName=key, parValue=cmndPars[key])
    
    cmndLine = """{cmndParsStr} -i {cmndName} {cmndArgs}""".format(
        cmndName=cmndName, cmndParsStr=cmndParsStr, cmndArgs=cmndArgs
    )

    cmndExampleMenuItem(
        commandLine=cmndLine,
        verbosity=verbosity,
        comment=comment,
        icmWrapper=icmWrapper,
        icmName=icmName,
    )    

####+BEGIN: bx:dblock:python:func :funcName "ex_gExecMenuItem" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "execLine wrapper=None comment='none'"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-anyOrNone :: /ex_gExecMenuItem/ retType=bool argsList=(execLine wrapper=None comment='none')  [[elisp:(org-cycle)][| ]]
"""
def ex_gExecMenuItem(
    execLine,
    wrapper=None,
    comment='none',
):
####+END:
    """
** Output an Non-ICM menu line.
"""
    if comment == 'none':
        fullCommandLine = execLine
    else:
        fullCommandLine = execLine + '         ' + comment
        
    if wrapper:
        fullCommandLine = wrapper + fullCommandLine

    print fullCommandLine
    

    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndExampleExternalCmndItem    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def cmndExampleExternalCmndItem(commandLine,
                               verbosity='basic',
                               comment='none'
                               ):
    """ vebosity is one of: 'none', 'little', 'some',  'full'
                               """
    #G_myFullName = sys.argv[0]
    #G_myName = os.path.basename(G_myFullName)

    if comment == 'none':
        fullCommandLine = commandLine
    else:
        fullCommandLine = commandLine + '         ' + comment

    print( fullCommandLine )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndArgsLengthIsNotValid    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def cmndArgsLengthIsNotValid(cmndArgs=ArgReq.Mandatory,
                        expected=ArgReq.Mandatory,
                        comparison=ArgReq.Mandatory,
                       ):
    cmndArgsLen=len(cmndArgs)
    if comparison(cmndArgsLen, expected):
        EH_critical_usageError("Bad Number Of cmndArgs: cmndArgs={cmndArgs}"
                                 .format(cmndArgs=cmndArgs))
        return(True)
    return(False)
    

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndArgsLengthValidate    [[elisp:(org-cycle)][| ]]
"""
@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def cmndArgsLengthValidate(cmndArgs=ArgReq.Mandatory,
                        expected=ArgReq.Mandatory,
                        comparison=ArgReq.Mandatory,
                       ):
    cmndArgsLen=len(cmndArgs)
    if comparison(cmndArgsLen, expected):
        EH_critical_usageError("Bad Number Of cmndArgs: cmndArgs={cmndArgs}"
                                 .format(cmndArgs=cmndArgs))
        return(1)
    return(0)
        
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  int__gt    [[elisp:(org-cycle)][| ]]
"""

def int__gt(nuOfArgs,  expected):
    if nuOfArgs > expected:
        return True
    else:
        return False


"""
*  [[elisp:(org-cycle)][| ]]  /icmRunArgs/         :: *IcmRunArgs_ -- In support of Run Time ICM Options --  icmRunArgs_isOptionXxSet()* [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmRunArgs_isCallTrackingMonitorOff    [[elisp:(org-cycle)][| ]]
"""

def icmRunArgs_isCallTrackingMonitorOff():
    """Activated with --callTrackings monitor-.
    """

    G = IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()
    retVal = False

    for this in icmRunArgs.callTrackings:
        if this == 'monitor-':
            retVal = True

    return retVal
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmRunArgs_isCallTrackingMonitorOn    [[elisp:(org-cycle)][| ]]
"""

def icmRunArgs_isCallTrackingMonitorOn():
    """Activated with --callTrackings monitor-.
    """

    G = IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()
    retVal = False

    try:
        callTrackings = icmRunArgs.callTrackings
    except AttributeError:
        callTrackings = []
        

    for this in callTrackings:
        if this == 'monitor+':
            retVal = True

    return retVal
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmRunArgs_isCallTrackingInvokeOff    [[elisp:(org-cycle)][| ]]
"""

def icmRunArgs_isCallTrackingInvokeOff():
    """Activated with --callTrackings monitor-.
    """
    G = IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()

    retVal = False

    for this in icmRunArgs.callTrackings:
        if this == 'invoke-':
            retVal = True

    return retVal

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmRunArgs_isRunModeDryRun    [[elisp:(org-cycle)][| ]]
"""

def icmRunArgs_isRunModeDryRun():
    """Activated with --runMode dryRun.
    """
    G = IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()

    retVal = False

    if icmRunArgs.runMode == 'dryRun':
        retVal = True

    return retVal

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmRunArgs_isRunModeDryRun    [[elisp:(org-cycle)][| ]]
"""

def icmRunArgs_verbosityLevel():
    """
    """
    G = IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()

    level = icmRunArgs.verbosityLevel
    if level is None:
        return 30

    try: level = int(level)
    except: pass

    return level



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmRunArgs_isDocStringRequested    [[elisp:(org-cycle)][| ]]
"""

def icmRunArgs_isDocStringRequested():
    """Activated with -i docString.
    """
    G = IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()

    retVal = False

    if icmRunArgs.docstring:
        retVal = True

    return retVal

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmRunArgs_loadFiles    [[elisp:(org-cycle)][| ]]
"""

def icmRunArgs_loadFiles():
    """Load the python files specified with --load."""
    G = IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()

    for this in icmRunArgs.loadFiles:
        loadFile(this)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  icmRunArgs_evalFiles    [[elisp:(org-cycle)][| ]]
"""

def icmRunArgs_evalFiles():
    """Eval Files -- Unused But Perhaps Usefull."""
    G = IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()

    for this in icmRunArgs.loadFiles:
        TM_here('Loading: ' + this)
        f = open(this)
        eval(f.read()) # Caution: you must be sure of what's in that file
        f.close()

####+BEGIN: bx:icm:python:func :funcName "libUserInit" :funcType "void" :retType "void" :deco "" :argsList "icmLineOpts"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-void      :: /libUserInit/ retType=void argsList=(icmLineOpts)  [[elisp:(org-cycle)][| ]]
"""
def libUserInit(
    icmLineOpts,
):
####+END:
    """ For situations when icm lib is being used outside of an ICM -- in the context of any app.
"""
    parser = argparse.ArgumentParser(
         description=__doc__
    )
    argsCommonProc(parser)
    
    args = parser.parse_args(icmLineOpts)
    logControler = LOG_Control()
    logControler.loggerSet(args)
    

"""
*  [[elisp:(org-cycle)][| ]]  /G_main/             :: *G_main -- Invoked from ICM, calls invokesProc* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  G_main    [[elisp:(org-cycle)][| ]]
"""
# DO NOT DECORATE THIS FUNCTION
#@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)   # Log module has not been setup, we can't track this
def G_main(inArgv,
           G_examples,
           extraArgs,
           invokesProc,
           mainEntry=None,
):
    """This is the main entry point for Python.Icm.Icm (InteractiveInvokationModules)
    """

    #
    # The order is important here,
    # 1) Parse The Command Line -- 2) LOG_ usese the command line -- 3) G. setup
    #
    icmRunArgs, icmArgsParser = G_argsProc(inArgv, extraArgs)

    logControler = LOG_Control()
    logControler.loggerSet(icmRunArgs)

    logger = logControler.loggerGet()

    logger.info('Main Started: ' + ucf.stackFrameInfoGet(1) )

    G = IcmGlobalContext()
    G.globalContextSet( icmRunArgs=icmRunArgs )
    G.icmArgsParser = icmArgsParser

    icmRunArgs_loadFiles()

    if len( inArgv ) == 0:
        if G_examples:
            G_examples()
            return

    if icmRunArgs.invokes:
        invokesProc()
    else:
        if mainEntry:
            mainEntry()

    return 0


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  G_mainWithClass    [[elisp:(org-cycle)][| ]]
"""
# DO NOT DECORATE THIS FUNCTION
#@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)   # Log module has not been setup, we can't track this
def G_mainWithClass(
        inArgv,
        G_examples,
        extraArgs,
        classedCmndsDict,
        #funcedCmndsDict,
        mainEntry=None,
        g_icmPreCmnds=None,
        g_icmPostCmnds=None,
):
    """This is the main entry point for Python.Icm
    """

    icmRunArgs, icmArgsParser = G_argsProc(inArgv, extraArgs)    

    logControler = LOG_Control()
    logControler.loggerSet(icmRunArgs)

    logger = logControler.loggerGet()

    logger.info('Main Started: ' + ucf.stackFrameInfoGet(1) )

    G = IcmGlobalContext()
    G.globalContextSet( icmRunArgs=icmRunArgs )
    G.icmArgsParser = icmArgsParser    
    G.cmndMethodsDictSet(classedCmndsDict)
    #G.cmndFuncsDictSet(funcedCmndsDict)

    icmRunArgs_loadFiles()

    if len( inArgv ) == 0:
        if G_examples:
            G_examples().cmnd()
            return

    if icmRunArgs.invokes:
        thisCmndName=icmRunArgs.invokes[0]

        if g_icmPreCmnds:
            g_icmPreCmnds()
            
        outcome = invokesProcAllClassed(
            classedCmndsDict,
        )

        if g_icmPostCmnds:
            g_icmPostCmnds()
        

        if not outcome:
            return

        try:
            outcomeError = outcome.error
        except AttributeError:
            ANN_here("Consider returning an outcome. cmnd={cmnd}".format(cmnd=thisCmndName))
            return
        
        if outcomeError: 
            if outcome.error != OpError.Success:
                if outcome.error == OpError.CmndLineUsageError:
                    sys.stderr.write(
                        "{myName}.{cmndName} Command Line Failed: Error={status} -- {errInfo}\n".
                        format(myName=G.icmMyName(),
                               cmndName=thisCmndName,
                               status=outcome.error,
                               errInfo=outcome.errInfo,
                    ))
                    print "------------------"
                    G.icmArgsParser.print_help()
                    print "------------------"
                    print "Run -i usage for more details."
                else:
                    sys.stderr.write(
                        "{myName}.{cmndName} Failed: Error={status} -- {errInfo}\n".
                        format(myName=G.icmMyName(),
                               cmndName=thisCmndName,
                               status=outcome.error,
                               errInfo=outcome.errInfo,
                    ))
            else:
                #sys.stderr.write("{myName}.{cmndName} Completed Successfully: status={status}\n"
                logger.info(
                    "{myName}.{cmndName} Completed Successfully: status={status}".
                    format(myName=G.icmMyName(),
                           cmndName=thisCmndName,
                           status=outcome.error
                ))
        else:
            #sys.stderr.write("{myName}.{cmndName} Completed Successfully: status={status}\n"
            logger.info(                
                "{myName}.{cmndName} Completed Successfully: status={status}".                
                format(myName=G.icmMyName(),
                       cmndName=thisCmndName,
                       status=outcome.error
            ))
        return outcome.error
    else:
        if mainEntry:
            mainEntry()

    return 0

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  invokesProcWithClass    [[elisp:(org-cycle)][| ]]
"""
def invokesProcAllClassed(
        classedCmndsDict,
):
    """Process all invokations applicable to all (classed+funced of mains+libs) CMNDs."""
    G = IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()

    for invoke in icmRunArgs.invokes:
        #
        # First we try cmndList_mainsMethods()
        #
        try:
            classedCmnd = classedCmndsDict[invoke]
        except  KeyError:
            #print "TM_"
            pass
        else:
            outcome = classedCmnd().cmnd(
                interactive=True, 
            )
            continue

        #
        # Next we try cmndList_libsMethods()
        #
        callDict = dict()
        for eachCmnd in cmndList_libsMethods().cmnd(interactive=False):
            try:
                callDict[eachCmnd] = eval("{eachCmnd}".format(eachCmnd=eachCmnd))
            except NameError:
                print("EH_problem -- Skipping eval({eachCmnd})".format(eachCmnd=eachCmnd))
                continue

        try:
            classedCmnd = callDict[invoke]
        except  KeyError:
            pass
        else:
            outcome =  classedCmnd().cmnd(
                interactive=True, 
            )
            continue

        #
        # We tried everything and could not find any
        #

        # BUG, NOTYET, EH_problem goes to -v 20
        EH_problem_info("Invalid Action: {invoke}"
                        .format(invoke=invoke))            

        print("Invalid Action: {invoke}"
                        .format(invoke=invoke))

        outcome = OpOutcome()
        outcome.error = OpError.CmndLineUsageError
        outcome.errInfo = "Invalid Action: {invoke}".format(invoke=invoke)

    return(outcome)


"""
*  [[elisp:(org-cycle)][| ]]  /Player Support/      :: *Framework cmnds That are expected by the ICM-Player* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  icmLanguage    [[elisp:(org-cycle)][| ]]
"""
class icmLanguage(Cmnd):
    """Returns python"""

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)     
    def cmnd(self,
            interactive=False,
    ):
        """Part of icm framework."""
        thisOutcome = OpOutcome()
        if interactive:
            print "python"

        return thisOutcome.set(
            opError=OpError.Success,
            opResults="python"
        )

    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  icmCmndPartIncludes    [[elisp:(org-cycle)][| ]]
"""
class icmCmndPartIncludes(Cmnd):
    """NOTYET Returns True"""

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)     
    def cmnd(self,
            interactive=False,
    ):
        """Part of icm framework."""

        #if interactive:
            #print "python"

        return True
    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  icmInUpdate -- Update    [[elisp:(org-cycle)][| ]]
"""    
class icmInUpdate(Cmnd):
    """Given a baseDir, update icmIn"""
    cmndParamsMandatory = None
    cmndParamsOptional = None
    cmndArgsLen = ["1"]

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)     
    def cmnd(self,
            interactive=False,
            icmsBase=None,  # cmndArgs[0]
    ):
        """Part of icm framework."""

        if interactive:
            G = IcmGlobalContext()
            icmRunArgs = G.icmRunArgsGet()
            icmsBase = icmRunArgs.cmndArgs[0]
        else:
            if not icmsBase:
                EH_problem_usageError("")
                return

        G_myFullName = sys.argv[0]
        G_myName = os.path.basename(G_myFullName)

        icmInBase = icmsBase + "/" + G_myName + "/icmIn"
        
        print "{icmInBase}".format(icmInBase=icmInBase)
            
        icmParamsToFileParamsUpdate(
            parRoot="{icmInBase}/paramsFp".format(icmInBase=icmInBase),
            icmParams=G.icmParamDictGet(),
        )

        icmParamsToFileParamsUpdate(
            parRoot="{icmInBase}/commonParamsFp".format(icmInBase=icmInBase),
            icmParams=commonIcmParamsPrep(),
        )

        cmndMainsMethodsToFileParamsUpdate(
            parRoot="{icmInBase}/cmndMainsFp".format(icmInBase=icmInBase),
        )

        cmndLibsMethodsToFileParamsUpdate(
            parRoot="{icmInBase}/cmndLibsFp".format(icmInBase=icmInBase),
        )
        
        return 


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  icmInfo    [[elisp:(org-cycle)][| ]]
"""    
class icmInfo(Cmnd):
    """Given a baseDir, update icmIn"""
    cmndParamsMandatory = None
    cmndParamsOptional = None
    cmndArgsLen = ["1"]

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)     
    def cmnd(self,
            interactive=False,
    ):
        """Part of icm framework."""

        # if interactive:
        G = IcmGlobalContext()
        #     icmRunArgs = G.icmRunArgsGet()
        #     icmInBase = icmRunArgs.cmndArgs[0]
        # else:
        #     if not icmInBase:
        #         EH_problem_usageError("")
        #         return

        print("* ICM Specified Parameters")

        icmParams = G.icmParamDictGet()

        for key, icmParam in icmParams.parDictGet().iteritems():
            if ( icmParam.argsparseShortOptGet() == None )  and ( icmParam.argsparseLongOptGet() == None ):
                break

            print "** " + key
            print "*** " + str(icmParam)

        print("* ICM Common Parameters")            

        icmParams = commonIcmParamsPrep()

        for key, icmParam in icmParams.parDictGet().iteritems():
            if ( icmParam.argsparseShortOptGet() == None )  and ( icmParam.argsparseLongOptGet() == None ):
                break

            print "** " + key
            print "*** " + str(icmParam)
            
        print("* ICM Mains Methods")
            
        mainsMethods = cmndList_mainsMethods().cmnd(interactive=False)         
        for each in mainsMethods:
            cmndInfo().cmnd(
                interactive=True,
                orgLevel=2,
                cmndName=each,
            )

        print("* ICM Libs Methods")
            
        libsMethods = cmndList_libsMethods().cmnd(interactive=False)
        for each in libsMethods:
            cmndInfo().cmnd(
                interactive=True,
                orgLevel=2,
                cmndName=each,
            )
       
        return 
 


"""
####+BEGINNOT: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/topControls.org"
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || FrmWrk-CMND       ::  version    [[elisp:(org-cycle)][| ]]
*       [[elisp:(org-cycle)][| *Version:* | ]]
####+END:
"""
class version(Cmnd):
    """ICM version number."""

    cmndArgsLen={'Min': 0, 'Max':0,}
    
    #@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)    
    def cmnd(self,
            interactive=False,        # Can also be called non-interactively
    ):
        """Version number is obtained from."""
        if interactive:
            print("* ICM-Version: {ver}".format(ver=str( __version__ )))
            return
        else:
            return(format(str(__version__)))


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  visit    [[elisp:(org-cycle)][| ]]
"""
class visit(Cmnd):
    """Visit The ICM Module."""

    cmndArgsLen = {'Min': 0, 'Max':0,}
    
    subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)    
    def cmnd(self,
            interactive=False,        # Can also be called non-interactively
    ):
        """Use emacs client to visit the ICM module."""
        
        myName=self.myName()
        G = IcmGlobalContext()
        thisOutcome = OpOutcome(invokerName=myName)
        
        thisOutcome = subProc_bash(
            """emlVisit -v -n showRun -i gotoPanel {myFullName}"""
            .format(myFullName=G.icmMyFullName()),
            stdin=None, outcome=thisOutcome,
        ).out()
        
        if thisOutcome.isProblematic():
            return(EH_badOutcome(thisOutcome))
        
        return thisOutcome
        

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  cmndInfo    [[elisp:(org-cycle)][| ]]
"""    
class cmndInfo(Cmnd):
    """Returns a human oriented string for the specified cmndName's expected pars/args usage."""

    cmndArgsLen={'Min': 1, 'Max':1,}    
    cmndArgsSpec = {1: ["cmndName"]}
    
    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)     
    def cmnd(self,
            interactive=False,
            cmndName=None,  # cmndArgs[0]             
            orgLevel=2,
    ):
        """Used by ICM Players to inform user of a given cmndName capabilities."""

        myName=self.myName()
        G = IcmGlobalContext()
        thisOutcome = OpOutcome(invokerName=myName)

        if not cmndName:
            if not interactive:
                EH_problem_usageError("")
                return
            cmndName = G.icmRunArgsGet().cmndArgs[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return

        outString = list()

        def orgIndentStr(subLevel): return "*" * (orgLevel + subLevel)

        outString.append("{baseOrgStr} {cmndName}\n".format(
            baseOrgStr=orgIndentStr(0),
            cmndName=cmndName,
        ))
        outString.append("{baseOrgStr} cmndShortDocStr={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndDocStrShort().cmnd(
                interactive=False,
                cmndName=cmndName,
        )))
        outString.append("{baseOrgStr} cmndFullDocStr={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndDocStrFull().cmnd(
                interactive=False,
                cmndName=cmndName,
        )))
        outString.append("{baseOrgStr} cmndParamsMandatory={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().paramsMandatory(),           
        ))
        outString.append("{baseOrgStr} cmndParamsOptional={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().paramsOptional(),           
        ))
        outString.append("{baseOrgStr} cmndArgsLen={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().argsLen(),           
        ))
        outString.append("{baseOrgStr} cmndArgsSpec={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().argsDesc(),           
        ))
        outString.append("{baseOrgStr} cmndUsers={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().users(),           
        ))
        outString.append("{baseOrgStr} cmndGroups={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().groups(),           
        ))
        outString.append("{baseOrgStr} cmndImapct={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().impact(),           
        ))
        outString.append("{baseOrgStr} cmndVisibility={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().visibility(),           
        ))

        if interactive:
            # print adds an extra line at the end in Python 2.X
            sys.stdout.write("".join(outString))

        return thisOutcome.set(
            opError=OpError.Success,
            opResults="".join(outString)
        )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  cmndInfoEssential    [[elisp:(org-cycle)][| ]]
"""    
class cmndInfoEssential(Cmnd):
    """Returns a human oriented string for the specified cmndName's expected pars/args usage."""
    cmndParamsMandatory = None
    cmndParamsOptional = None
    cmndArgsLen = ["1"]
    cmndArgsSpec = ["cmndName"]
    
    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)     
    def cmnd(self,
            interactive=False,
            cmndName=None,  # cmndArgs[0]            
            orgLevel=2,
    ):
        """Used by ICM Players to inform user of a given cmndName capabilities."""

        myName=self.myName()
        G = IcmGlobalContext()
        thisOutcome = OpOutcome(invokerName=myName)

        if not cmndName:
            if not interactive:
                EH_problem_usageError("")
                return
            cmndName = G.icmRunArgsGet().cmndArgs[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return

        outString = list()

        def orgIndentStr(subLevel): return "*" * (orgLevel + subLevel)

        outString.append("{baseOrgStr} cmndFullDocStr={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndDocStrFull().cmnd(
                interactive=False,
                cmndName=cmndName,
        )))
        outString.append("{baseOrgStr} cmndParamsMandatory={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().paramsMandatory(),           
        ))
        outString.append("{baseOrgStr} cmndParamsOptional={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().paramsOptional(),           
        ))
        outString.append("{baseOrgStr} cmndArgsLen={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().argsLen(),           
        ))
        outString.append("{baseOrgStr} cmndArgsSpec={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().argsDesc(),           
        ))
        outString.append("{baseOrgStr} cmndUsers={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().users(),           
        ))
        outString.append("{baseOrgStr} cmndGroups={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().groups(),           
        ))
        outString.append("{baseOrgStr} cmndImapct={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().impact(),           
        ))
        outString.append("{baseOrgStr} cmndVisibility={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().visibility(),           
        ))

        if interactive:
            # print adds an extra line at the end in Python 2.X
            sys.stdout.write("".join(outString))

        return thisOutcome.set(
            opError=OpError.Success,
            opResults="".join(outString)
        )
    
    
    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndNameToClass    [[elisp:(org-cycle)][| ]]
"""
def cmndNameToClass(
        cmndName,
):
    """Given cmndName, return cmndClass."""

    G = IcmGlobalContext()
    classedCmndsDict = G.cmndMethodsDict()

    try:
        classedCmnd = classedCmndsDict[cmndName]
    except  KeyError:
        #print "TM_"
        pass
    else:
        return classedCmnd
    
    try:
        cmndClass = eval("{cmndName}".format(cmndName=cmndName))
    except NameError:
        return None

    if cmndName in cmndSubclassesNames():
        return cmndClass
    else:
        return None
    

"""
*  [[elisp:(org-cycle)][| ]]  /cmndsList_/          :: *cmndsList_ -- List C-CMNDs and F-CMNDs in a given file and in icm library* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  cmndList_allMethods    [[elisp:(org-cycle)][| ]]
"""
class cmndList_allMethods(Cmnd):
    """List All Classed-CMNDs."""

    #Do Not Decorate with  @subjectToTracking    
    def cmnd(self,
            interactive=True,
    ):
        """Is based on subclasses of Cmnd and which are in the main module.
When interactive is false, return the list and when true print it and return the list.
"""
        allClassedCmndNames = cmndSubclassesNames()

        if interactive:
            ucf.listPrintItems(allClassedCmndNames)

        return allClassedCmndNames


####+BEGIN: bx:icm:python:icmItem :itemType "Global" :itemTitle "mainsClassedCmndsGlobal = None"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Global         :: mainsClassedCmndsGlobal = None  [[elisp:(org-cycle)][| ]]
"""
####+END:
    
mainsClassedCmndsGlobal = None    
    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  cmndList_mainsMethods    [[elisp:(org-cycle)][| ]]
"""
class cmndList_mainsMethods(Cmnd):
    """List All C-CMNDs of the Module."""

    #Do Not Decorate with  @subjectToTracking    
    def cmnd(self,
            interactive=False,
            importedCmnds={},
            mainFileName=None,
    ):
        """Is based on subclasses of Cmnd and which are in the main module.
When interactive is false, return the list and when true print it and return the list.
"""

        global mainsClassedCmndsGlobal

        allClassedCmndNames = cmndSubclassesNames()

        if not mainFileName:
            mainFileName = sys.argv[0]

        mainClasses = ucf.ast_topLevelClassNamesInFile(
            mainFileName,
        )

        #print mainClasses

        relevantClasses = mainClasses
        for key, modPath in importedCmnds.iteritems():
            if modPath.endswith('.pyc') and os.path.exists(modPath[:-1]):
                modPath = modPath[:-1]
            relevantClasses += ucf.ast_topLevelClassNamesInFile(modPath)

        mainsClassedCmnds = set.intersection(
            set(allClassedCmndNames),
            set(relevantClasses),
        )
        
        if interactive:
            ucf.listPrintItems(mainsClassedCmnds)

        mainsClassedCmndsGlobal = mainsClassedCmnds

        return mainsClassedCmnds

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  cmndList_libsMethods    [[elisp:(org-cycle)][| ]]
"""         
class cmndList_libsMethods(Cmnd):
    """List All NAMES of C-CMNDs of the Libs Module."""

    #@subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)    
    def cmnd(self,
            interactive=False,
    ):
        """Is based on subclasses of Cmnd and which are in the main module.
When interactive is false, return the list and when true print it.
"""

        global mainsClassedCmndsGlobal
        
        allClassedCmndNames = cmndSubclassesNames()

        #mainClasses = ucf.ast_topLevelClassNamesInFile(
        #    sys.argv[0]
        #)

        #ANN_here(allClassedCmndNames)
        #print mainClasses
        #libsClassedCmnds = set(allClassedCmndNames) - set(mainClasses)
        libsClassedCmnds = set(allClassedCmndNames) - set(mainsClassedCmndsGlobal)

        if interactive:
            ucf.listPrintItems(libsClassedCmnds)

        return libsClassedCmnds

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  cmndClassDocStr    [[elisp:(org-cycle)][| ]]
"""
class cmndClassDocStr(Cmnd):
    """Given a list of cmnds as Args, for each return the the class docStr."""
    cmndParamsMandatory = None
    cmndParamsOptional = None
    cmndArgsLen = ["1"]
    
    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)    
    def cmnd(self,
            interactive=False,
            cmndName=None,
    ):
        """The Cmnd class from which this is drived, includes docStr extractors.\
"""
        G = IcmGlobalContext()
        if not cmndName:
            if not interactive:
                EH_problem_usageError("")
                return None
            cmndName = G.icmRunArgsGet().cmndArgs[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return None
            
        docStr = cmndClass().docStrClass()

        if interactive: print docStr

        return docStr

####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "lib" :cmndName "cmndHelp" :comment "" :parsMand "" :parsOpt "" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /cmndHelp/ parsMand= parsOpt= argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class cmndHelp(Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        argsList=None,         # or Args-Input
    ):
        G = IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {}
        if not cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:
        cmndName = effectiveArgsList[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return None

        docStr = cmndClass().cmndDocStr()

        if interactive: print docStr
        return docStr


####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "lib" :cmndName "null" :comment "" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /null/ parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class null(Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):

        G = IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:
        return cmndOutcome
      
    def cmndDesc(): """
** A command that does nothing. The null Command. -- Can be combined with --load.
    When used with --load it can result in execution of loaded extensions.
"""
    

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  cmndFuncDocStr    [[elisp:(org-cycle)][| ]]
"""
class cmndMethodDocStr(Cmnd):
    """Given a list of cmnds as Args, for each return the cmnd() funcs docStr."""
    cmndParamsMandatory = None
    cmndParamsOptional = None
    cmndArgsLen = ["1"]
    
    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)    
    def cmnd(self,
            interactive=False,
            cmndName=None,            
    ):
        """The Cmnd class from which this is drived, includes docStr extractors.\
"""
        G = IcmGlobalContext()
        if not cmndName:
            if not interactive:
                EH_problem_usageError("")
                return
            cmndName = G.icmRunArgsGet().cmndArgs[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return 
            
        docStr = cmndClass().docStrCmndMethod()

        if interactive:
            print docStr

        return docStr


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  cmndDocStrShort    [[elisp:(org-cycle)][| ]]
"""
class cmndDocStrShort(Cmnd):
    """Given a list of cmnds as Args, for each return the the class docStr."""
    cmndParamsMandatory = None
    cmndParamsOptional = None
    cmndArgsLen = ["1"]
    
    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)    
    def cmnd(self,
            interactive=False,
            cmndName=None,
    ):
        """The Cmnd class from which this is drived, includes docStr extractors.\
"""
        classDocStr = cmndClassDocStr().cmnd(
                interactive=False,
                cmndName=cmndName,
        )
        if not classDocStr: return None

        shortDocStr = ucf.STR_getFirstLine(classDocStr)
        
        if interactive: print shortDocStr
        return shortDocStr

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-CMND        ::  cmndDocStrLong    [[elisp:(org-cycle)][| ]]
"""
class cmndDocStrFull(Cmnd):
    """Given a list of cmnds as Args, for each return the cmnd() funcs docStr."""
    cmndParamsMandatory = None
    cmndParamsOptional = None
    cmndArgsLen = ["1"]
    
    @subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)    
    def cmnd(self,
            interactive=False,
            cmndName=None,            
    ):
        """The Cmnd class from which this is drived, includes docStr extractors.\
"""
        classDocStr = cmndClassDocStr().cmnd(
                interactive=False,
                cmndName=cmndName,
        )
        if not classDocStr: return None

        methodDocStr = cmndMethodDocStr().cmnd(
                interactive=False,
                cmndName=cmndName,
        )
        if not methodDocStr: return None

        longDocStr = classDocStr + "\n" + methodDocStr
        
        if interactive: print longDocStr
        return longDocStr


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndSubclassesNames    [[elisp:(org-cycle)][| ]]
"""
def cmndSubclassesNames():
    """Not using generators by choice."""
    # return [each.__name__ for each in Cmnd.__subclasses__()]
    cmndsNames = list()
    for eachClass in Cmnd.__subclasses__():
        cmndsNames.append(eachClass.__name__)
    return cmndsNames

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndMainsMethodsToFileParamsUpdate    [[elisp:(org-cycle)][| ]]
"""
def cmndMainsMethodsToFileParamsUpdate(
        parRoot,
):
    """ """
    mainsCmndMethods = cmndList_mainsMethods().cmnd()
    for each in mainsCmndMethods:
        cmndToFileParamsUpdate(
            cmndName=each,
            parRoot=parRoot,
        )
    return

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndLibsMethodsToFileParamsUpdate    [[elisp:(org-cycle)][| ]]
"""
def cmndLibsMethodsToFileParamsUpdate(
        parRoot,
):
    """ """
    libsCmndMethods = cmndList_libsMethods().cmnd()
    for each in libsCmndMethods:
        cmndToFileParamsUpdate(
            cmndName=each,
            parRoot=parRoot,
        )
    return

####+BEGIN: bx:icm:python:func :funcName "evalStringInMain" :funcType "succFail" :retType "bool" :deco "" :argsList "inStr"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-succFail  :: /evalStringInMain/ retType=bool argsList=(inStr)  [[elisp:(org-cycle)][| ]]
"""
def evalStringInMain(
    inStr,
):
####+END:
    """
** Given inStr eval that string in __main__.
"""
    LOG_here("Eval-ing: __main__.{}".format(inStr))
    # try
    eval("__main__.{}".format(inStr))


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  cmndToFileParamsUpdate    [[elisp:(org-cycle)][| ]]
"""
def cmndToFileParamsUpdate(
        cmndName,
        parRoot,
):
    "Write cmnd as fileParam"
    
    absoluteParRoot = os.path.abspath(parRoot)

    if not os.path.isdir(absoluteParRoot):
        try: os.makedirs( absoluteParRoot, 0775 )
        except OSError: pass

    parValue = "unSet"

    FILE_ParamWriteTo(
        parRoot=absoluteParRoot,
        parName=cmndName,
        parValue=parValue,
    )
    
    def writeCmndAttrFV(
            cmndName,
            attrName,
            attrValue,
    ):
        varValueFullPath = os.path.join(
            absoluteParRoot,
            cmndName,
            attrName,
        )
        FV_writeToFilePathAndCreate(
            filePath=varValueFullPath,
            varValue=attrValue,
        )

        
    docStr = cmndDocStrShort().cmnd(
        cmndName=cmndName,
    )
    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='description',
        attrValue=docStr,
    )
        
    docStr = cmndDocStrFull().cmnd(
        cmndName=cmndName,
    )
    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='fullDesc',
        attrValue=docStr,
    )

    cmndClass = cmndNameToClass(cmndName)
    if not cmndClass: return 
    
    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='paramsMandatory',
        attrValue=cmndClass().paramsMandatory(),
    )
    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='paramsOptional',
        attrValue=cmndClass().paramsOptional(),
    )
    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='cmndInfo',
        attrValue=cmndInfoEssential().cmnd(
            interactive=False,
            orgLevel=2,
            cmndName=cmndName,
        )
    )
    
    return


        
"""
*  [[elisp:(org-cycle)][| ]]  /General-Misc/       :: *Common-Misc Utilities -- FUNC_* [[elisp:(org-cycle)][| ]]
"""


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *End Of Editable Text*
"""

"""
*  [[elisp:(org-cycle)][| ]]  COMMON        :: /[dblock] -- End-Of-File Controls/ [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
