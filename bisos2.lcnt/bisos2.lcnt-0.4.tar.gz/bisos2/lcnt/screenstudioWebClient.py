# -*- coding: utf-8 -*-
"""\
* TODO *[Summary]* ::  A /library/ Beginning point for development of new ICM oriented libraries.
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/de/bx/nne/dev-py/pypi/pkgs/bisos/examples/dev/bisos/examples/icmLibBegin.py :: [[elisp:(org-cycle)][| ]]
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

####+BEGIN: bx:global:lib:name-py :style "fileName"
__libName__ = "icmLibBegin"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201712312856"
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

####+BEGIN: bx:dblock:python:func :funcName "insertPathForImports" :funcType "FrameWrk" :retType "none" :deco "" :argsList "path"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-FrameWrk  :: /insertPathForImports/ retType=none argsList=(path)  [[elisp:(org-cycle)][| ]]
"""
def insertPathForImports(
    path,
):
####+END:
    """
** Extends Python imports path with  ../lib/python
"""
    import os
    import sys
    absolutePath = os.path.abspath(path)    
    if os.path.isdir(absolutePath):
        sys.path.insert(1, absolutePath)

insertPathForImports("../lib/python/")



####+BEGIN: bx:dblock:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || =Imports=      :: *IMPORTS*  [[elisp:(org-cycle)][| ]]
"""
####+END:

import os
import collections
import enum

import requests

import pexpect
# Not using import pxssh -- because we need to custom manipulate the prompt

# NOTYET, should become a dblock with its own subItem
from unisos import ucf
from unisos import icm

G = icm.IcmGlobalContext()
G.icmLibsAppend = __file__
G.icmCmndsLibsAppend = __file__
# NOTYET DBLOCK Ends -- Rest of bisos libs follow;


####+BEGIN: bx:dblock:python:section :title "Library Description (Overview)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Library Description (Overview)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:python:icm:cmnd:classHead :cmndName "icmBegin_LibOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /icmBegin_LibOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class icmBegin_LibOverview(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 3,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        argsList=None,         # or Args-Input
    ):
        G = icm.IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        moduleDescription="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]	Model and Terminology 					   :Overview:
This module is part of BISOS and its primary documentation is in  http://www.by-star.net/PLPC/180047
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

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/moduleOverview.py"
        cmndArgsSpec = {"0&-1": ['moduleDescription', 'moduleUsage', 'moduleStatus']}
        cmndArgsValid = cmndArgsSpec["0&-1"]
        icm.unusedSuppressForEval(moduleDescription, moduleUsage, moduleStatus)
        for each in effectiveArgsList:
            if each in cmndArgsValid:
                if interactive:
                    exec("""print({})""".format(each))
                
        return(format(str(__doc__)+moduleDescription))
####+END:


####+BEGIN: bx:icm:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:func :funcName "serviceUrlDefault" :funcType "defaultVerify" :retType "echo" :deco "" :argsList "serviceUrl"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-defaultVerify :: /serviceUrlDefault/ retType=echo argsList=(serviceUrl)  [[elisp:(org-cycle)][| ]]
"""
def serviceUrlDefault(
    serviceUrl,
):
####+END:
    if not serviceUrl:
        return "http://localhost:8080"
    else:
        return serviceUrl



####+BEGIN: bx:dblock:python:class :className "ScreenstudioWebClient" :superClass "" :comment "" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /ScreenstudioWebClient/ object  [[elisp:(org-cycle)][| ]]
"""
class ScreenstudioWebClient(object):
####+END:
    """
** This is just a placeholder for now. It needs to use the filesystem for persistence.
"""
        
    def __init__(self,
                 serviceUrl=None,
    ):
        self.serviceUrl = serviceUrl

    def recordingStart(self,):
        try:
            response = requests.get(self.serviceUrl)
        except Exception as e:
            print e
            return False

        icm.ANN_here(response)
        icm.ANN_here(response.status_code)

        startRecordingUrl = "{serviceUrl}/?action=record".format(serviceUrl=self.serviceUrl)
        print startRecordingUrl
        try:
	    resp = requests.get(startRecordingUrl)

	except Exception as e:
	    print e
            return False

        print resp

    def recordingStop(self,):
        self.recordingStart()
      
    def recordingStatus(self,):
        icm.ANN_here("NOTYET")

####+BEGIN: bx:dblock:python:section :title "ICM Examples"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Examples*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:func :funcName "commonParamsSpecify" :funcType "void" :retType "bool" :deco "" :argsList "icmParams"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-void      :: /commonParamsSpecify/ retType=bool argsList=(icmParams)  [[elisp:(org-cycle)][| ]]
"""
def commonParamsSpecify(
    icmParams,
):
####+END:

    icmParams.parDictAdd(
        parName='sessionType',
        parDescription="One of: liveSession or narratedSession",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--sessionType',
    )

    icmParams.parDictAdd(
        parName='nuOfDisplays',
        parDescription="One of: 1 or 3",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--nuOfDisplays',
    )
    


####+BEGIN: bx:icm:python:func :funcName "recordingIcmExamples" :funcType "void" :retType "bool" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-void      :: /recordingIcmExamples/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def recordingIcmExamples():
####+END:
        def cpsInit(): return collections.OrderedDict()
        def menuItem(): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
        def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        nuOfDisplays = nuOfDisplaysGet().cmnd().results

        icm.cmndExampleMenuChapter('*Recorder Preparations*')

        cmndName = "screenstudioRcUpdate"
        cmndArgs = ""; cps = cpsInit(); cps['sessionType'] = "liveSession"
        menuItem()

        cmndArgs = ""; cps = cpsInit(); cps['sessionType'] = "narratedSession"
        menuItem()

        cmndName = "screenstudioRcStdout"
        cmndArgs = ""; cps = cpsInit(); cps['sessionType'] = "liveSession" ; cps['nuOfDisplays'] = nuOfDisplays
        menuItem()

        cmndArgs = ""; cps = cpsInit(); cps['sessionType'] = "narratedSession" ; cps['nuOfDisplays'] = nuOfDisplays
        menuItem()

        cmndName = "screenstudioRun"
        cmndArgs = ""; cps = cpsInit(); # cps['sessionType'] = "liveSession" ; cps['nuOfDisplays'] = nuOfDisplays
        menuItem()

        cmndName = "recorderIsUp"
        cmndArgs = serviceUrlDefault(None); cps = cpsInit(); # cps['icmsPkgName'] = icmsPkgName 
        menuItem()
        #icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='full')

        icm.cmndExampleMenuChapter('*Recordings Start/Stop*')
        
        cmndName = "recordingStart"
        cmndArgs = serviceUrlDefault(None); cps = cpsInit(); # cps['icmsPkgName'] = icmsPkgName 
        menuItem()
        
        cmndName = "recordingStop"
        cmndArgs = serviceUrlDefault(None); cps = cpsInit(); # cps['icmsPkgName'] = icmsPkgName 
        menuItem()


        
 
####+BEGIN: bx:dblock:python:section :title "Recording ICMs -- Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICMs -- Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:



####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "recordingStart" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /recordingStart/ parsMand= parsOpt= argsMin=0 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class recordingStart(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
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
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:
        serviceUrl = serviceUrlDefault(effectiveArgsList[0])

        myName=self.myName()
        thisOutcome = icm.OpOutcome(invokerName=myName)

        screenstudioClient = ScreenstudioWebClient(serviceUrl=serviceUrl)

        screenstudioClient.recordingStart()
        
        return thisOutcome
    
    def cmndDocStr(self): return """
** Place holder for ICM's experimental or test code.  [[elisp:(org-cycle)][| ]]
 You can use this Cmnd for rapid prototyping and testing of newly developed functions.
"""
    

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "recordingStop" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /recordingStop/ parsMand= parsOpt= argsMin=0 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class recordingStop(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
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
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:
        serviceUrl = serviceUrlDefault(effectiveArgsList[0])

        myName=self.myName()
        thisOutcome = icm.OpOutcome(invokerName=myName)

        screenstudioClient = ScreenstudioWebClient(serviceUrl=serviceUrl)

        screenstudioClient.recordingStop()
        
        return thisOutcome
    
    def cmndDocStr(self): return """
** Place holder for ICM's experimental or test code.  [[elisp:(org-cycle)][| ]]
 You can use this Cmnd for rapid prototyping and testing of newly developed functions.
"""

        
 
####+BEGIN: bx:dblock:python:section :title "Recorder Configuration And Run ICMs -- Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICMs -- Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "nuOfDisplaysGet" :comment "" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /nuOfDisplaysGet/ parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class nuOfDisplaysGet(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        outcome = icm.subProc_bash(
            """\
xrandr -q | grep ' connected' | wc -l\
"""
        ).log()
        if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))

        nuOfScreens = outcome.stdout.strip('\n')

        if interactive:
            icm.ANN_write("{}".format(nuOfScreens))
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=nuOfScreens,
        )


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "screenstudioRun" :comment "" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /screenstudioRun/ parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class screenstudioRun(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:
        """
** TODO UnUsed.
        """
        
        #offlineimaprcPath = withInMailDomGetOfflineimaprcPath(controlProfile, inMailAcct)            

        outcome = icm.subProc_bash(
            """screenstudio"""
        ).log()
        if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "screenstudioRcUpdate" :comment "" :parsMand "sessionType" :parsOpt "nuOfDisplays" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /screenstudioRcUpdate/ parsMand=sessionType parsOpt=nuOfDisplays argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class screenstudioRcUpdate(icm.Cmnd):
    cmndParamsMandatory = [ 'sessionType', ]
    cmndParamsOptional = [ 'nuOfDisplays', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        sessionType=None,         # or Cmnd-Input
        nuOfDisplays=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'sessionType': sessionType, 'nuOfDisplays': nuOfDisplays, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        sessionType = callParamsDict['sessionType']
        nuOfDisplays = callParamsDict['nuOfDisplays']
####+END:

        if not nuOfDisplays:
            outcome = nuOfDisplaysGet().cmnd()
            if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))
            
            nuOfDisplays = outcome.results

        outcome = screenstudioRcStdout().cmnd(
            interactive=False,
            sessionType=sessionType,
            nuOfDisplays=nuOfDisplays,
        )
        if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))

        screenstudioRcStr = outcome.results

        screenstudioRcPath = screenstudioRcFileNameGet(sessionType, nuOfDisplays)

        with open(screenstudioRcPath, "w") as thisFile:
            thisFile.write(screenstudioRcStr + '\n')

        if interactive:
            icm.ANN_here("screenstudioRcPath={val}".format(val=screenstudioRcPath))
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=screenstudioRcPath,
        )

####+BEGIN: bx:icm:python:func :funcName "screenstudioRcFileNameGet" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "sessionType nuOfDisplays"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-anyOrNone :: /screenstudioRcFileNameGet/ retType=bool argsList=(sessionType nuOfDisplays)  [[elisp:(org-cycle)][| ]]
"""
def screenstudioRcFileNameGet(
    sessionType,
    nuOfDisplays,
):
####+END:
    fileName = "./screenstudio-{sessionType}-{nuOfDisplays}disps.xml".format(
        sessionType=sessionType,
        nuOfDisplays=nuOfDisplays,
    )
    return os.path.abspath(fileName)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "screenstudioRcStdout" :comment "" :parsMand "sessionType" :parsOpt "nuOfDisplays" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /screenstudioRcStdout/ parsMand=sessionType parsOpt=nuOfDisplays argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class screenstudioRcStdout(icm.Cmnd):
    cmndParamsMandatory = [ 'sessionType', ]
    cmndParamsOptional = [ 'nuOfDisplays', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        sessionType=None,         # or Cmnd-Input
        nuOfDisplays=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'sessionType': sessionType, 'nuOfDisplays': nuOfDisplays, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        sessionType = callParamsDict['sessionType']
        nuOfDisplays = callParamsDict['nuOfDisplays']
####+END:

        if not nuOfDisplays:
            outcome = nuOfDisplaysGet().cmnd()
            if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))
            
            nuOfDisplays = outcome.result

        cwd = os.getcwd()

        if sessionType == "narratedSession":
            audiosystemStr="""Monitor of Built-in Audio Analog Stereo"""
            microphoneStr="""None"""

        elif sessionType == "liveSession":
            audiosystemStr="""None"""
            microphoneStr="""Yeti Stereo Microphone Analog Stereo"""
            
        else:
            icm.EH_usageError("Bad sessionType -- {}".format(sessionType))

        resStr = screenstudioRcTemplate(
            nuOfDisplays,
        ).format(
            audiosystemStr=audiosystemStr,
            microphoneStr=microphoneStr,
            outputvideofolderStr=cwd,
        )

        if interactive:
            print resStr
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=resStr
        )

####+BEGIN: bx:icm:python:func :funcName "screenstudioRcTemplate" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "nuOfDisplays"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-anyOrNone :: /screenstudioRcTemplate/ retType=bool argsList=(nuOfDisplays)  [[elisp:(org-cycle)][| ]]
"""
def screenstudioRcTemplate(
    nuOfDisplays,
):
####+END:

    screens_1_templateStr = """ 
<?xml version="1.0" encoding="UTF-8" standalone="no"?><screenstudio><audios audiobitrate="Audio44K" audiosystem="{audiosystemStr}" microphone="{microphoneStr}"/><output outputframerate="10" outputheight="1080" outputpreset="ultrafast" outputtarget="MP4" outputvideofolder="{outputvideofolderStr}" outputwidth="1920" rtmpkey="" rtmpserver="" videobitrate="1000"/><settings backgroundmusic=""/><desktop bg="0" bgAreaColor="0" capturex="0" capturey="0" effect="None" end="0" fg="0" font="" fontsize="0" id="Screen 1" start="0" transstart="None" transstop="None" type=""><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/></desktop></screenstudio>
"""

    screens_3_templateStr = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?><screenstudio><audios audiobitrate="Audio44K" audiosystem="{audiosystemStr}" microphone="{microphoneStr}"/><output outputframerate="10" outputheight="1080" outputpreset="ultrafast" outputtarget="MP4" outputvideofolder="{outputvideofolderStr}" outputwidth="1920" rtmpkey="" rtmpserver="" videobitrate="1000"/><settings backgroundmusic=""/><desktop bg="0" bgAreaColor="0" capturex="0" capturey="0" effect="None" end="0" fg="0" font="" fontsize="0" id="Screen 3" start="0" transstart="None" transstop="None" type=""><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="5760" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="5760" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="5760" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="5760" x="0" y="0"/></desktop></screenstudio>
"""

    templateStr = None          

    icm.unusedSuppressForEval(
        screens_1_templateStr,
        screens_3_templateStr,
    )

    exec(
        "templateStr = screens_{}_templateStr".format(str(nuOfDisplays))
    )

    return templateStr

    
    

####+BEGIN: bx:icm:python:section :title "End Of Editable Text"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
