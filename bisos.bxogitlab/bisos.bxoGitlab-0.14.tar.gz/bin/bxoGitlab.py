#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""\
* TODO *[Summary]* :: An =ICM=: sets up /bisos /bxo /de directory bases.
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/bisos/git/bxRepos/bisos-pip/bxoGitlab/py2/bin/bxoGitlab.py :: [[elisp:(org-cycle)][| ]]
 is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
 *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
 A Python Interactively Command Module (PyICM).
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 *WARNING*: All edits wityhin Dynamic Blocks may be lost.
"""
####+END:

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:icm:python:name :style "fileName"
__icmName__ = "bxoGitlab"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "202104095902"
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

####+BEGIN: bx:icm:python:topControls :partof "bystar" :copyleft "halaal+minimal"
"""
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
"""
####+END:

####+BEGIN: bx:icm:python:section :title "ContentsList"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ContentsList*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  =Imports=      :: *IMPORTS*  [[elisp:(org-cycle)][| ]]
"""
####+END:

import sys
import os

import collections
import enum

import gitlab

####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/importUcfIcmBleepG.py"
from unisos import ucf
from unisos import icm

icm.unusedSuppressForEval(ucf.__file__)  # in case icm and ucf are not used

G = icm.IcmGlobalContext()
G.icmLibsAppend = __file__
G.icmCmndsLibsAppend = __file__

from blee.icmPlayer import bleep

####+END:

from bisos.common import serviceObject

g_importedCmnds = {        # Enumerate modules from which CMNDs become invokable
    'bleep': bleep.__file__,    
    'serviceObject': serviceObject.__file__,
}


####+BEGIN: bx:icm:python:section :title "= =Framework::= ICM  Description (Overview) ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM  Description (Overview) =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "new" :cmndName "icmOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /icmOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class icmOverview(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 3,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        argsList=[],         # or Args-Input
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

        cmndArgsSpecDict = self.cmndArgsSpec()
        if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        moduleDescription="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]   Model and Terminology                                      :Overview:
*** See BISOS Documentation for ICM's model and terminology
**      [End-Of-Description]
"""
        
        moduleUsage="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]

**      How-Tos:
*** TODO Edit icmInfo to identify author, etc
*** TODO Select ICM type in g_icmChars
*** TODO Enhance g_argsExtraSpecify for your parameters
*** TODO Add your Commands
*** TODO Enhance Examples Cmnd
**      [End-Of-Usage]
"""
        
        moduleStatus="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO [[elisp:(org-cycle)][| ]]  Current         :: Just getting started [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/moduleOverview.py"
        icm.unusedSuppressForEval(moduleUsage, moduleStatus)
        actions = self.cmndArgsGet("0&2", cmndArgsSpecDict, effectiveArgsList)
        if actions[0] == "all":
            cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&2")
            argChoices = cmndArgsSpec.argChoicesGet()
            argChoices.pop(0)
            actions = argChoices
        for each in actions:
            print(each)
            if interactive:
                #print( str( __doc__ ) )  # This is the Summary: from the top doc-string
                #version(interactive=True)
                exec("""print({})""".format(each))
                
        return(format(str(__doc__)+moduleDescription))

    """
**  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Method-anyOrNone :: /cmndArgsSpec/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self):
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = icm.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&2",
            argName="actions",
            argDefault='all',
            argChoices=['all', 'moduleDescription', 'moduleUsage', 'moduleStatus'],
            argDescription="Output relevant information",
        )

        return cmndArgsSpecDict
####+END:
    

####+BEGIN: bx:icm:python:section :title "= =Framework::= ICM Hooks ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM Hooks =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:func :funcName "g_icmChars" :comment "ICM Characteristics Spec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-FrameWrk  :: /g_icmChars/ =ICM Characteristics Spec= retType=Void argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def g_icmChars():
####+END:
    icmInfo['panel'] = "{}-Panel.org".format(__icmName__)
    icmInfo['groupingType'] = "IcmGroupingType-pkged"
    icmInfo['cmndParts'] = "IcmCmndParts[common] IcmCmndParts[param]"
    
g_icmChars()


####+BEGIN: bx:icm:python:func :funcName "g_icmPreCmnds" :funcType "FrameWrk" :retType "Void" :deco "default" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-FrameWrk  :: /g_icmPreCmnds/ retType=Void argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def g_icmPreCmnds():
####+END:
    """ PreHook """
    pass


####+BEGIN: bx:icm:python:func :funcName "g_icmPostCmnds" :funcType "FrameWrk" :retType "Void" :deco "default" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-FrameWrk  :: /g_icmPostCmnds/ retType=Void argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def g_icmPostCmnds():
####+END:
    """ PostHook """
    pass


####+BEGIN: bx:icm:python:section :title "= =Framework::= Options, Arguments and Examples Specifications ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= Options, Arguments and Examples Specifications =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:func :funcName "g_argsExtraSpecify" :comment "FrameWrk: ArgsSpec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList "parser"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-FrameWrk  :: /g_argsExtraSpecify/ =FrameWrk: ArgsSpec= retType=Void argsList=(parser)  [[elisp:(org-cycle)][| ]]
"""
def g_argsExtraSpecify(
    parser,
):
####+END:
    """Module Specific Command Line Parameters.
    g_argsExtraSpecify is passed to G_main and is executed before argsSetup (can not be decorated)
    """
    G = icm.IcmGlobalContext()
    icmParams = icm.ICM_ParamDict()

    icmParams.parDictAdd(
        parName='moduleVersion',
        parDescription="Module Version",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--version',
    )

    icmParams.parDictAdd(
        parName='outFile',
        parDescription="Output File Name",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--outFile',
    )

    icmParams.parDictAdd(
        parName='keyName',
        parDescription="Name Of The SSH Key",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--keyName',
    )
    
    bleep.commonParamsSpecify(icmParams)    
    
    serviceObject.commonParamsSpecify(icmParams)
       
    icm.argsparseBasedOnIcmParams(parser, icmParams)

    # So that it can be processed later as well.
    G.icmParamDictSet(icmParams)
    
    return


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "examples" :cmndType "ICM-Cmnd-FWrk"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd-FWrk  :: /examples/ =FrameWrk: ICM Examples= parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class examples(icm.Cmnd):
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

        logControler = icm.LOG_Control()
        logControler.loggerSetLevel(20)

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity,
                                 comment='none', icmWrapper=None, icmName=None) # verbosity: 'little' 'basic' 'none'
        def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)
        
        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())
        
        icm.G_commonBriefExamples()    

        bleep.examples_icmBasic()


####+BEGIN: bx:icm:python:cmnd:subSection :title "Imported: bxPlatformBaseDirs"
        """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Imported: bxPlatformBaseDirs*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

        oneBxoId='prs_bisos'
        oneBxoRoot = bxoRootDir_obtain(bxoId=oneBxoId) 
        oneKeyPath = os.path.join(oneBxoRoot, 'credentials/priv/ssh/id_rsa.pub')
        oneKeyTypeName = '_priv-pubkey'
        oneKeyName = oneKeyTypeName
        oneSnapshotOutFile = '/tmp/git-' + oneBxoId + '-iso.tar'
        
        #serviceObject.examples_bxoSrBaseDir()

        icm.cmndExampleMenuChapter('*Gitlab BxE Realization -- Create Account*')

        cmndName = "acctCreate" ; cmndArgs = ""
        cps=cpsInit() ; cps['bxoId'] = oneBxoId
        menuItem(verbosity='little')

        cmndName = "acctVerify" ; cmndArgs = ""
        cps=cpsInit() ; cps['bxoId'] = oneBxoId
        menuItem(verbosity='little')

        cmndName = "acctList" ; cmndArgs = ""
        cps=cpsInit(); menuItem(verbosity='little')

        cmndName = "acctDelete" ; cmndArgs = ""
        cps=cpsInit() ; cps['bxoId'] = oneBxoId
        menuItem(verbosity='little')
        
        icm.cmndExampleMenuChapter('*Gitlab BxE Realization -- Key Upload*')

        cmndName = "pubkeysList" ; cmndArgs = ""
        cps=cpsInit() ; cps['bxoId'] = oneBxoId
        menuItem(verbosity='little')
        
        cmndName = "pubkeyObtain" ; cmndArgs = ""
        cps=cpsInit() ; cps['bxoId'] = oneBxoId ; cps['keyName'] = oneKeyName
        menuItem(verbosity='little')
        
        cmndName = "pubkeyUpload" ; cmndArgs = oneKeyPath
        cps=cpsInit() ; cps['bxoId'] = oneBxoId ; cps['keyName'] = oneKeyName
        menuItem(verbosity='little')

        cmndName = "pubkeyDelete" ; cmndArgs = ""
        cps=cpsInit() ; cps['bxoId'] = oneBxoId ; cps['keyName'] = oneKeyName
        menuItem(verbosity='little')
        
        icm.cmndExampleMenuChapter('*Gitlab Repos -- List, Create and Delete Repos*')        
        
        cmndName = "reposList" ; cmndArgs = ""
        cps=cpsInit() ; cps['bxoId'] = oneBxoId
        menuItem(verbosity='little')

        cmndName = "reposCreate" ; cmndArgs = "iso"
        cps=cpsInit() ; cps['bxoId'] = oneBxoId
        menuItem(verbosity='little')

        cmndName = "reposDelete" ; cmndArgs = "iso"
        cps=cpsInit() ; cps['bxoId'] = oneBxoId
        menuItem(verbosity='little')

        icm.cmndExampleMenuChapter('*Gitlab BxE Construction -- Take A Snapshot Of Repo*')        
        
        cmndName = "repoSnapshot" ; cmndArgs = "iso"
        cps=cpsInit() ; cps['bxoId'] = oneBxoId ; cps['outFile'] = oneSnapshotOutFile
        menuItem(verbosity='little')
        
        return(cmndOutcome)

    def cmndDocStr(self): return """
** ICM Examples -- List of commonly used lines for this ICM [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:icm:python:section :title "ICM Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "acctCreate" :comment "" :parsMand "bxoId" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /acctCreate/ parsMand=bxoId parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class acctCreate(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'bxoId': bxoId, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']

####+END:

        bxoRoot = bxoRootDir_obtain(bxoId=bxoId) 

        bxeDescRoot = bxo_bxeDescRootDir_obtain(bxoRoot)

        selectedSiteRoot = usgSitesSelectedDir_obtain(usgAcct=None)
        gitServerInfo = os.path.join(selectedSiteRoot, "gitServerInfo")

        gitServerUrl = icm.FILE_ParamValueReadFrom(parRoot=gitServerInfo, parName="gitServerUrl")
        gitServerPrivToken = icm.FILE_ParamValueReadFrom(parRoot=gitServerInfo, parName="gitServerPrivToken")        
        
        # gl = gitlab.Gitlab.from_config('bisosAdmin', ['/bxo/usg/bystar/.python-gitlab.cfg'])            
        # private token or personal token authentication
        # gl = gitlab.Gitlab('http://192.168.0.56', private_token='qji9-_YqoqzZ4Rymk_qG')
        
        gl = gitlab.Gitlab(gitServerUrl, private_token=gitServerPrivToken)        

        user = getUserForBxo(gl, bxoId)
        if user:
            icm.ANN_write("Acct Already Exists -- user={}".format(user.username))
            return cmndOutcome.set(
                opError=icm.OpError.Success,
                opResults=None,
            )

        bxeOid = icm.FILE_ParamValueReadFrom(parRoot=bxeDescRoot, parName="bxeOid")
        if not bxeOid:
            icm.EH_problem_usageError("Missing Path {}".format(bxeDescRoot))
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)
        
        # AdminContactEmail = icm.FILE_ParamValueReadFrom(bxeDescRoot, parName='AdminContactEmail')
        AdminContactEmail = "git-" + bxoId + "@mohsen.1.banan.byname.net"
        passwd = 'somePassword'
        # acctName = "oid-" + bxeOid
        acctName = bxoId  + "-bxe-" + bxeOid          
        
        user = gl.users.create({
            'username': bxoId,
            'name': acctName,
            'email': AdminContactEmail,
            'password': passwd,
            'skip_confirmation': True                
        })

        # BASH equivalent:
        # gitlab user create  --email test2@example.com --username test2 --name "Test User2" --password "secret01" --skip-confirmation true

        print("Activating User")
        user.activate()

        if interactive:
            #icm.ANN_write("{}".format(bxoRoot))
            print((user.username))
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=user.username,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  NOTYET AdminContactEmail should be fixed.
***** TODO Passwd should be auto generated -- not something specific as it is never used.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "acctVerify" :comment "" :parsMand "bxoId" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /acctVerify/ parsMand=bxoId parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class acctVerify(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'bxoId': bxoId, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']

####+END:

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bxoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=user.username,
        )


####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "acctDelete" :comment "" :parsMand "bxoId" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /acctDelete/ parsMand=bxoId parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class acctDelete(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'bxoId': bxoId, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']

####+END:

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bxoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        userName=user.username

        user.delete()
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=user.name,
        )


####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "acctList" :comment "" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /acctList/ parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class acctList(icm.Cmnd):
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

        gl = bxoGitlab_connect()

        users = gl.users.list(all=True)

        for eachUser in users:
            print((eachUser.username))

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "pubkeysList" :comment "" :parsMand "bxoId" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /pubkeysList/ parsMand=bxoId parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pubkeysList(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'bxoId': bxoId, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']

####+END:

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bxoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        keys = user.keys.list(all=True)
    
        for eachKey in keys:
            print((eachKey.title))

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  List repos for bxoId.
"""
    
    

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "pubkeyObtain" :comment "" :parsMand "bxoId keyName" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /pubkeyObtain/ parsMand=bxoId keyName parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pubkeyObtain(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', 'keyName', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
        keyName=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'bxoId': bxoId, 'keyName': keyName, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']
        keyName = callParamsDict['keyName']

####+END:

        gitlab = bxoGitlab_connect()

        key = bxoKeyGet(gitlab, bxoId, keyName)
        if not key:
            return cmndOutcome.set(opError=icm.OpError.Success, opResults=None,)

        if interactive:
            print((key.key))

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=key.key,
        )


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "pubkeyUpload" :comment "" :parsMand "bxoId keyName" :parsOpt "" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /pubkeyUpload/ parsMand=bxoId keyName parsOpt= argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pubkeyUpload(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', 'keyName', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
        keyName=None,         # or Cmnd-Input
        argsList=[],         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'bxoId': bxoId, 'keyName': keyName, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']
        keyName = callParamsDict['keyName']

        cmndArgsSpecDict = self.cmndArgsSpec()
        if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, effectiveArgsList)

        keyPath=cmndArgs[0]

        gitlab = bxoGitlab_connect()

        key = keyUploadForBxo(gitlab, bxoId, keyName, keyPath)
        if not key:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)
  
        if interactive:
            #icm.ANN_write("{}".format(bxoRoot))
            print(key)
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=key.title,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "pubkeyDelete" :comment "" :parsMand "bxoId keyName" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /pubkeyDelete/ parsMand=bxoId keyName parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pubkeyDelete(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', 'keyName', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
        keyName=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'bxoId': bxoId, 'keyName': keyName, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']
        keyName = callParamsDict['keyName']

####+END:

        gitlab = bxoGitlab_connect()

        key = bxoKeyGet(gitlab, bxoId, keyName)
        if not key:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        keyTitle = key.title
        
        if interactive:
            #icm.ANN_write("Deleting keyTitle={}".format(keyTitle))
            print(key)

        key.delete()
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=keyTitle,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "reposList" :comment "" :parsMand "bxoId" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /reposList/ parsMand=bxoId parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class reposList(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'bxoId': bxoId, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']

####+END:

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bxoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        # list all the projects
        projects = gl.projects.list(sudo=bxoId, all=True)
        for project in projects:
            if project.name != "Monitoring":
                print((project.name))
                #print(project.attributes)

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  List repos for bxoId.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "reposCreate" :comment "" :parsMand "bxoId" :parsOpt "" :argsMin "1" :argsMax "9999" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /reposCreate/ parsMand=bxoId parsOpt= argsMin=1 argsMax=9999 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class reposCreate(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
        argsList=[],         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'bxoId': bxoId, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']

        cmndArgsSpecDict = self.cmndArgsSpec()
        if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, effectiveArgsList)

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bxoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        # example code fragment:
        
        # bxeType = icm.FILE_ParamValueReadFrom(
        #     parRoot=os.path.abspath(bxeDescRoot),
        #     parName="bxeType"
        # )

        def processEachArg(eachArg,):

            project = getRepoOfBxo(gl, bxoId, eachArg)
            if project:
                icm.ANN_write("Repo Already Exists -- repoName={}".format(project.name))
                return None
                    
            # If you have the administrator status, you can use sudo to act as another user.
            project = gl.projects.create(
                {
                'name': eachArg,
                },
                sudo=bxoId,
            )
            icm.ANN_write("Created Repo -- repoName={}".format(project.name))            
            print((project.name))
            return project

        for eachArg in cmndArgs:
            project = processEachArg(eachArg)                        

        if project:
            return cmndOutcome.set(
                opError=icm.OpError.Success,
                opResults=project.name,
            )
        else:
            return cmndOutcome.set(
                opError=icm.OpError.Failure,
                opResults="AlreadyExists",
            )
  

####+BEGIN: bx:icm:python:method :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndArgsSpec/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self):
####+END:        
        """
***** Cmnd Args Specification  -- Each As Any.
"""
        cmndArgsSpecDict = icm.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict

    

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "reposDelete" :comment "" :parsMand "bxoId" :parsOpt "" :argsMin "1" :argsMax "9999" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /reposDelete/ parsMand=bxoId parsOpt= argsMin=1 argsMax=9999 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class reposDelete(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
        argsList=[],         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'bxoId': bxoId, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']

        cmndArgsSpecDict = self.cmndArgsSpec()
        if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, effectiveArgsList)

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bxoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        # example code fragment:
        
        # bxeType = icm.FILE_ParamValueReadFrom(
        #     parRoot=os.path.abspath(bxeDescRoot),
        #     parName="bxeType"
        # )

        def processEachArg(eachArg,):

            project = getRepoOfBxo(gl, bxoId, eachArg)
            if not project:
                icm.ANN_write("Missing Repo -- repoName={}".format(eachArg))
                return project
                    
            project.delete()
            
        for eachArg in cmndArgs:
            project = processEachArg(eachArg)                        

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndArgsSpec/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self):
####+END:        
        """
***** Cmnd Args Specification  -- Each As Any.
"""
        cmndArgsSpecDict = icm.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict

    
####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""
    

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "repoSnapshot" :comment "" :parsMand "bxoId outFile" :parsOpt "" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /repoSnapshot/ parsMand=bxoId outFile parsOpt= argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class repoSnapshot(icm.Cmnd):
    cmndParamsMandatory = [ 'bxoId', 'outFile', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bxoId=None,         # or Cmnd-Input
        outFile=None,         # or Cmnd-Input
        argsList=[],         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'bxoId': bxoId, 'outFile': outFile, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        bxoId = callParamsDict['bxoId']
        outFile = callParamsDict['outFile']

        cmndArgsSpecDict = self.cmndArgsSpec()
        if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, effectiveArgsList)

        repoName = cmndArgs[0]
        
        gitlab = bxoGitlab_connect()

        thisRepo = getRepoOfBxo(gitlab, bxoId, repoName)
        if not thisRepo:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        tarFile = thisRepo.snapshot()

        f = open(outFile, 'bw+')  # b added for py3.
        f.write(tarFile)
        f.close()            
            
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndArgsSpec/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self):
####+END:        
        """
***** Cmnd Args Specification  -- Each As Any.
"""
        cmndArgsSpecDict = icm.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict


####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:        
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""

####+BEGIN: bx:icm:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:dblock:python:func :funcName "bxoKeyGet" :funcType "Obtain" :retType "str" :deco "" :argsList "gitlab bxoId keyName"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-Obtain    :: /bxoKeyGet/ retType=str argsList=(gitlab bxoId keyName)  [[elisp:(org-cycle)][| ]]
"""
def bxoKeyGet(
    gitlab,
    bxoId,
    keyName,
):
####+END:
    """
** Get the specified key for bxo.
"""

    user = getUserForBxo(gitlab, bxoId)
    if not user:
        icm.EH_problem_usageError("Missing user={} for bxoId={}".format(user, bxoId))
        return None

    key = None
    keys = user.keys.list(all=True)
    
    for eachKey in keys:
        if eachKey.title == keyName:
            icm.LOG_here("Key Already Exists -- keys={}".format(keys))            
            key = eachKey
            break

    if not key:
        icm.LOG_here("No Keys Found -- keyName={} for bxoId={}".format(keyName, bxoId))        
        
    return key
                                  

####+BEGIN: bx:dblock:python:func :funcName "keyUploadForBxo" :funcType "Obtain" :retType "str" :deco "" :argsList "gitlab bxoId keyName keyPath"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-Obtain    :: /keyUploadForBxo/ retType=str argsList=(gitlab bxoId keyName keyPath)  [[elisp:(org-cycle)][| ]]
"""
def keyUploadForBxo(
    gitlab,
    bxoId,
    keyName,
    keyPath,
):
####+END:
    """
** Upload the specified key for bxo.
"""

    bxoRoot = bxoRootDir_obtain(bxoId=bxoId,) 

    user = getUserForBxo(gitlab, bxoId)
    if not user:
        icm.EH_problem_usageError("Missing user={} for bxoId={}".format(user, bxoId))
        return None

    key = None
    keys = user.keys.list(all=True)
    
    for eachKey in keys:
        if eachKey.title == keyName:
            icm.LOG_here("Key Already Exists -- keys={}".format(keys))            
            key = eachKey
            break

    if not key:
        key = user.keys.create({
            'title': keyName,
            'key': open(keyPath).read()
        })

    return key
                                  



####+BEGIN: bx:dblock:python:func :funcName "getRepoOfBxo" :funcType "Obtain" :retType "str" :deco "" :argsList "gitlab bxoId repoName"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-Obtain    :: /getRepoOfBxo/ retType=str argsList=(gitlab bxoId repoName)  [[elisp:(org-cycle)][| ]]
"""
def getRepoOfBxo(
    gitlab,
    bxoId,
    repoName,
):
####+END:
    """
** Get the gitlab repo (project) based on specified repoName of bxoId.
"""
    project = None
    projects = gitlab.projects.list(search=repoName, sudo=bxoId, all=True)
    for eachProject in projects:
        if eachProject.name == repoName:
            project = eachProject
            break

    if not project:
        icm.LOG_here("Missing repoName={} for bxoId={}".format(repoName, bxoId))
        
    return project
    

####+BEGIN: bx:dblock:python:func :funcName "getUserForBxo" :funcType "Obtain" :retType "str" :deco "" :argsList "gitlab bxoId"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-Obtain    :: /getUserForBxo/ retType=str argsList=(gitlab bxoId)  [[elisp:(org-cycle)][| ]]
"""
def getUserForBxo(
    gitlab,
    bxoId,
):
####+END:
    """
** Get the gitlab user associated with the specified bxoId.
"""

    user = None
    users = gitlab.users.list(search=bxoId, all=True)

    for eachUser in users:
        if eachUser.username == bxoId:
            user = eachUser
            break

    if not user:
        icm.LOG_here("Missing user bxoId={}".format(bxoId))
        
    return user


####+BEGIN: bx:dblock:python:func :funcName "bxoGitlab_connect" :funcType "Obtain" :retType "str" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-Obtain    :: /bxoGitlab_connect/ retType=str argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def bxoGitlab_connect():
####+END:
    """
** Obtain a handle for the gitlab class.
"""

    selectedSiteRoot = usgSitesSelectedDir_obtain(usgAcct=None)
    gitServerInfo = os.path.join(selectedSiteRoot, "gitServerInfo")

    gitServerUrl = icm.FILE_ParamValueReadFrom(
        parRoot=gitServerInfo,
        parName="gitServerUrl"
    )
    gitServerPrivToken = icm.FILE_ParamValueReadFrom(
        parRoot=gitServerInfo,
        parName="gitServerPrivToken"
    )        
    gl = gitlab.Gitlab(gitServerUrl, private_token=gitServerPrivToken)        

    return gl


####+BEGIN: bx:dblock:python:section :title "Directory Base Locations"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Directory Base Locations*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:python:subSection :title "Bxo Roots And InfoBases"

####+END:

####+BEGINNOT: bx:dblock:python:enum :enumName "bxo_IdType" :comment ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Enum           :: /bxo_IdType/  [[elisp:(org-cycle)][| ]]
"""
#@enum.unique
class bxo_IdType(enum.Enum):
####+END:
    foreignBxO = 'foreignBxO'
    nativeBxO = 'nativeBxO'
    bystarId = 'bystarId'


####+BEGIN: bx:dblock:python:func :funcName "bxoIdType_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList "bxoId"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-Obtain    :: /bxoIdType_obtain/ retType=str argsList=(bxoId)  [[elisp:(org-cycle)][| ]]
"""
def bxoIdType_obtain(
    bxoId,
):
####+END:
    """
** ea-NUM means old ByStarUid, A pure number means nativeSO. nonNumber means foreignBxO
"""
    # return bxo_IdType.foreignBxO
    return bxo_IdType.nativeBxO


####+BEGIN: bx:dblock:python:func :funcName "bxoRootDir_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList "bxoId"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-Obtain    :: /bxoRootDir_obtain/ retType=str argsList=(bxoId)  [[elisp:(org-cycle)][| ]]
"""
def bxoRootDir_obtain(
    bxoId,
):
####+END:
    """
** 
"""
    bxoBaseDir = None
    idType = bxoIdType_obtain(bxoId)

    if idType == bxo_IdType.foreignBxO:
        bxoBaseDir = os.path.join(
            bxPlatformConfig.rootDir_foreignBxo_fpObtain(configBaseDir=None,),
            bxoId,
        )
    elif idType == bxo_IdType.nativeBxO:
        bxoBaseDir = os.path.expanduser("~" +  bxoId)

    elif idType == bxo_IdType.bystarId:
        pass
    else:
        icm.EH_problem_usageError("")

    return bxoBaseDir


####+BEGIN: bx:dblock:python:subSection :title "Bxo+Sr Roots and InfoBases (Control/Input)"

####+END:


####+BEGIN: bx:dblock:python:func :funcName "bxo_bxeDescRootDir_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList "bxoBaseDir"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-Obtain    :: /bxo_bxeDescRootDir_obtain/ retType=str argsList=(bxoBaseDir)  [[elisp:(org-cycle)][| ]]
"""
def bxo_bxeDescRootDir_obtain(
    bxoBaseDir,
):
####+END:
    """
** 
"""
    return (
        os.path.join(
            bxoBaseDir,
            "rbxe/bxeDesc",
        )
    )


####+BEGIN: bx:dblock:python:func :funcName "usgSitesSelectedDir_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList "usgAcct=None"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-Obtain    :: /usgSitesSelectedDir_obtain/ retType=str argsList=(usgAcct=None)  [[elisp:(org-cycle)][| ]]
"""
def usgSitesSelectedDir_obtain(
    usgAcct=None,
):
####+END:
    """
** 
"""
    if usgAcct:
        usgAcctBase=os.path.expanduser("~" + usgAcct)
    else:
        usgAcctBase=os.path.expanduser("~")
        
    usgSitesSelectedDir = os.path.join(
        usgAcctBase,
        "bisos/sites/selected"
    )

    if not os.path.exists(usgSitesSelectedDir):
        usgSitesSelectedDir = "/bisos/var/sites/selected"

    return usgSitesSelectedDir


####+BEGIN: bx:icm:python:section :title "Common/Generic Facilities -- Library Candidates"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common/Generic Facilities -- Library Candidates*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
"""
*       /Empty/  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(org-cycle)][| ]]
"""
    
####+BEGIN: bx:icm:python:section :title "= =Framework::=   G_main -- Instead Of ICM Dispatcher ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::=   G_main -- Instead Of ICM Dispatcher =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:func :funcName "G_main" :funcType "FrameWrk" :retType "Void" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-FrameWrk  :: /G_main/ retType=Void argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def G_main():
####+END:
    """ 
** Replaces ICM dispatcher for other command line args parsings.
"""
    pass

####+BEGIN: bx:icm:python:icmItem :itemType "Configuration" :itemTitle "= =Framework::= g_ Settings -- ICMs Imports ="
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Configuration  :: = =Framework::= g_ Settings -- ICMs Imports =  [[elisp:(org-cycle)][| ]]
"""
####+END:


g_examples = examples  # or None 
g_mainEntry = None  # or G_main

####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/icm2.G_main.py"
"""
*  [[elisp:(beginning-of-buffer)][Top]] # /Dblk-Begin/ # [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM main() =*
"""

def classedCmndsDict():
    """
** Should be done here, can not be done in icm library because of the evals.
"""
    callDict = dict()
    for eachCmnd in icm.cmndList_mainsMethods().cmnd(
            interactive=False,
            importedCmnds=g_importedCmnds,
            mainFileName=__file__,
    ):
        try:
            callDict[eachCmnd] = eval("{}".format(eachCmnd))
            continue
        except NameError:
            pass

        for mod in g_importedCmnds:
            try:
                eval("{mod}.{cmnd}".format(mod=mod, cmnd=eachCmnd))
            except AttributeError:
                continue
            try:                
                callDict[eachCmnd] = eval("{mod}.{cmnd}".format(mod=mod, cmnd=eachCmnd))
                break
            except NameError:
                pass
    return callDict

icmInfo['icmName'] = __icmName__
icmInfo['version'] = __version__
icmInfo['status'] = __status__
icmInfo['credits'] = __credits__

G = icm.IcmGlobalContext()
G.icmInfo = icmInfo

def g_icmMain():
    """This ICM's specific information is passed to G_mainWithClass"""
    sys.exit(
        icm.G_mainWithClass(
            inArgv=sys.argv[1:],                 # Mandatory
            extraArgs=g_argsExtraSpecify,        # Mandatory
            G_examples=g_examples,               # Mandatory            
            classedCmndsDict=classedCmndsDict(),   # Mandatory
            mainEntry=g_mainEntry,
            g_icmPreCmnds=g_icmPreCmnds,
            g_icmPostCmnds=g_icmPostCmnds,
        )
    )

g_icmMain()

"""
*  [[elisp:(beginning-of-buffer)][Top]] ## /Dblk-End/ ## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM main() =*
"""

####+END:

####+BEGIN: bx:icm:python:section :title "Unused Facilities -- Temporary Junk Yard"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Unused Facilities -- Temporary Junk Yard*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:icm:python:section :title "End Of Editable Text"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
