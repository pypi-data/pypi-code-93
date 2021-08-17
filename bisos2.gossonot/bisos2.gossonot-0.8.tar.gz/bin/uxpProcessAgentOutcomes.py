#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""\
*    *[Summary]* :: An =ICM=: Bxp (ByStar Platform) Tpa (Target Parameters and Actions) Monitor. 
*  Loads Target-Lists and Params and invokes these ICM Actions and Agent-Actions.
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/de/bx/nne/dev-py/pypi/pkgs/bisos/gossonot/dev/bin/uxpProcessAgentOutcomes.py :: [[elisp:(org-cycle)][| ]]
 is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
 *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
 A Python Interactively Command Module (PyICM). Part Of ByStar.
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 Warning: All edits wityhin Dynamic Blocks may be lost.
"""
####+END:

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:icm:python:name :style "fileName"
__icmName__ = "uxpProcessAgentOutcomes"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201809192527"
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
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ContentsList*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || =Imports=      :: *IMPORTS*  [[elisp:(org-cycle)][| ]]
"""
####+END:

import sys
import os

import shlex
import subprocess

import collections

from unisos import ucf
from unisos import icm

from blee.icmPlayer import bleep

from unisos.common import icmsPkgLib
from bisos.gossonot import gossonotPkgThis

from bisos.things import toIcm

g_importedCmnds = {        # Enumerate modules from which CMNDs become invokable
    'bleep': bleep.__file__,    
}


####+BEGIN: bx:icm:python:section :title "= =Framework::= ICM  Description (Overview) ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM  Description (Overview) =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "new" :cmndName "icmOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || ICM-Cmnd       :: /icmOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
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

**  [[elisp:(org-cycle)][| ]]	Model and Terminology 					   :Overview:
*** bxpRootXxFile   -- /etc/bystarRoot, ~/.bystarRoot, /bystar
*** bxpRoot         -- Base For This Module
*** bpb             -- ByStar Platform Base, Location Of Relevant Parts (Bisos, blee, bsip
*** bpd             -- ByStar Platform Directory (Object), An instance of Class BxpBaseDir
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
        icm.unusedSuppressForEval(moduleUsage, moduleStatus)
        actions = self.cmndArgsGet("0&2", cmndArgsSpecDict, effectiveArgsList)
        if actions[0] == "all":
            cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&2")
            argChoices = cmndArgsSpec.argChoicesGet()
            argChoices.pop(0)
            actions = argChoices
        for each in actions:
            print each
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
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM Hooks =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:func :funcName "g_icmChars" :comment "ICM Characteristics Spec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || Func-FrameWrk  :: /g_icmChars/ =ICM Characteristics Spec= retType=Void argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def g_icmChars():
####+END:
    icmInfo['panel'] = "{}-Panel.org".format(__icmName__)
    icmInfo['groupingType'] = "IcmGroupingType-pkged"
    icmInfo['cmndParts'] = "IcmCmndParts[common] IcmCmndParts[param]"
    
g_icmChars()


####+BEGIN: bx:icm:python:func :funcName "g_icmPreCmnds" :funcType "FrameWrk" :retType "Void" :deco "default" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || Func-FrameWrk  :: /g_icmPreCmnds/ retType=Void argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def g_icmPreCmnds():
####+END:
    """ PreHook """
    pass


####+BEGIN: bx:icm:python:func :funcName "g_icmPostCmnds" :funcType "FrameWrk" :retType "Void" :deco "default" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || Func-FrameWrk  :: /g_icmPostCmnds/ retType=Void argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def g_icmPostCmnds():
####+END:
    """ PostHook """
    pass


####+BEGIN: bx:icm:python:section :title "= =Framework::= Options, Arguments and Examples Specifications ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= Options, Arguments and Examples Specifications =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:func :funcName "g_argsExtraSpecify" :comment "FrameWrk: ArgsSpec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList "parser"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || Func-FrameWrk  :: /g_argsExtraSpecify/ =FrameWrk: ArgsSpec= retType=Void argsList=(parser)  [[elisp:(org-cycle)][| ]]
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
        parName='pkgSrc',
        parDescription="Package Source",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--pkgSrc',
    )
    
    bleep.commonParamsSpecify(icmParams)    
    
    toIcm.targetParamListCommonArgs(parser)    
       
    icm.argsparseBasedOnIcmParams(parser, icmParams)

    # So that it can be processed later as well.
    G.icmParamDictSet(icmParams)
    
    return


####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "new" :cmndName "examples" :cmndType "ICM-Cmnd-FWrk"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || ICM-Cmnd-FWrk  :: /examples/ =FrameWrk: ICM Examples= parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
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
        def cpsInit(): return collections.OrderedDict()
        def menuItem(): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
        def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        icmsPkgInfoBaseDir = gossonotPkgThis.pkgBase_baseDir()

        #print icmsPkgInfoBaseDir

        logControler = icm.LOG_Control()
        logControler.loggerSetLevel(20)

        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())
        
        icm.G_commonBriefExamples()    

        bleep.examples_icmBasic()

        
####+BEGIN: bx:icm:python:cmnd:subSection :title "Dev And Testing"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Dev And Testing*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

        icm.cmndExampleMenuChapter('*General Dev and Testing CMNDs*')

        cmndName = "unitTest" ; cmndArgs = "" ;
        cps = collections.OrderedDict() ; # cps['icmsPkgName'] = icmsPkgName 
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='full')

        
####+BEGIN: bx:icm:python:cmnd:subSection :title "Simplified Targets Selection"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Simplified Targets Selection*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        
        icm.cmndExampleMenuChapter('*Simplified Targets Selection*')

        # execLineEx("""ln -s /de/bx/current/district/librecenter/tiimi/targets/bxp/tList/ts-librecenter-localhostIcm.py liTargets.py""")
        # execLineEx("""ln -s /de/bx/current/district/librecenter/tiimi/targets/bxp/paramList/bxpUsageParamsIcm.py liParams.py""")

        execLineEx("""ln -s {pkgBaseDir}/ts-librecenter-localhostIcm.py liTargets.py""".format(pkgBaseDir=icmsPkgInfoBaseDir))
        execLineEx("""ln -s {pkgBaseDir}/bxpUsageParamsIcm.py liParams.py""".format(pkgBaseDir=icmsPkgInfoBaseDir))
        
        execLineEx("""stress --cpu 2 --io 1 --vm 1 --vm-bytes 128M --timeout 10s --verbose""")

        loadTargetArgs=""" --load ./liTargets.py"""
        loadParamsArgs=""" --load ./liParams.py """    
        #ticmoFullInfo=format(commonArgs + loadTargetArgs)

        toIcm.targetParamSelectCommonExamples()

        toIcm.targetParamListCommonExamples(loadTargetArgs=loadTargetArgs,
                                       loadParamsArgs=loadParamsArgs)
    
        #fileParamPath1 = "/de/bx/coll/libreCenter/platforms/bue/0015/params/access/cur/"
        #fileParamPath2 = "/de/bx/coll/libreCenter/platforms/bue/0015/params/access/cur/"

####+BEGIN: bx:icm:python:cmnd:subSection :title "Run With Targets"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Run With Targets*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        
        icm.cmndExampleMenuChapter('/TOICM: Monitor/ *targetsParamsToIcmMonitor*')   

        thisCmndAction= " -i linuxUsageKpisRetrieve"
    
        # accessParams = " --targetFqdn " + thisTargetFqdn + " --userName " + thisUser + " --password " + thisPassword
        # icm.cmndExampleMenuItem(format(toIcmMonitorArgs + accessParams  +  thisCmndAction),
        #                         verbosity='none')                            

        icm.cmndExampleMenuItem(format(loadTargetArgs + loadParamsArgs +  thisCmndAction),
                               verbosity='none')                            
        icm.cmndExampleMenuItem(format(loadTargetArgs + loadParamsArgs + thisCmndAction),
                               verbosity='full')                            

        #
        # ICMs PKG Information
        #


        # icmsPkgLib.examples_pkgInfoParsFull(
        #     icmsPkgNameSpecification(),
        #     icmsPkgInfoBaseDir=icmsPkgInfoBaseDir,
        #     icmsPkgControlBaseDir=icmsPkgControlBaseDirDefault(),
        #     icmsPkgRunBaseDir=icmsPkgRunBaseDirDefault(),
        # )
        


####+BEGIN: bx:icm:python:section :title "ICM Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "new" :cmndName "unitTest" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || ICM-Cmnd       :: /unitTest/ parsMand= parsOpt= argsMin=0 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class unitTest(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

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

        myName=self.myName()
        thisOutcome = icm.OpOutcome(invokerName=myName)

        print G.icmInfo

        for eachArg in effectiveArgsList:
            icm.ANN_here("{}".format(eachArg))

        print (icm.__file__)
        print sys.path

        import imp
        print(imp.find_module('unisos/icm'))

        @ucf.runOnceOnly
        def echo(str):
            print str
            
        echo("first")
        echo("second")  # Should not run
    
        return thisOutcome
    
    def cmndDocStr(self): return """
** Place holder for ICM's experimental or test code.  [[elisp:(org-cycle)][| ]]
*** You can use this Cmnd for rapid prototyping and testing of newly developed functions.
"""


    

####+BEGIN: bx:icm:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *General Interactively Invokable Functions (CMND)*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Common-CMND   ::  commonParamsDefaultsSet    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def commonParamsDefaultsSet(interactive=icm.Interactivity.Both,):
    """ Set Monitor FILE_Params to their defaults."""
####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/icmFuncHead.py"

####+END:

    if icm.Interactivity().interactiveInvokation(interactive):
        icmRunArgs = G.icmRunArgsGet()
        if icm.cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=icm.int__gt):
            return(icm.ReturnCode.UsageError)

    icm.FILE_ParamWriteToPath(
        parNameFullPath="./icmsIn/control/targetsChunkSize",
        parValue=200
    )
    icm.FILE_ParamWriteToPath(
        parNameFullPath="./icmsIn/control/paramWriterBufferSize",
        parValue=500
    )
    icm.FILE_ParamWriteToPath(
        parNameFullPath="./icmsIn/control/paramReaderBufferSize",
        parValue=100
    )
    icm.FILE_ParamWriteToPath(
        parNameFullPath="./icmsIn/control/exclusionListsControl",
        parValue="fullyIgnore"
    )
    icm.FILE_ParamWriteToPath(
        parNameFullPath="./icmsIn/control/execResultsControl",
        parValue="complete"
    )
    icm.FILE_ParamWriteToPath(
        parNameFullPath="./icmsIn/control/cmParamsVerificationControl",
        parValue="none"
    )

    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Common-CMND   ::  commonParamsGet    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def commonParamsGet(interactive=icm.Interactivity.Both,):
    """ Lists The ParameterNames that were loaded. """
####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/icmFuncHead.py"

####+END:

    if icm.Interactivity().interactiveInvokation(interactive):
        icmRunArgs = G.icmRunArgsGet()
        if icm.cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=icm.int__gt):
            return(icm.ReturnCode.UsageError)

    icm.FILE_paramDictReadDeep(interactive=False, 
                      inPathList=["./icmsIn"])
    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Common-CMND   ::  usageParams    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def usageParams(interactive=icm.Interactivity.Both,):
    """ Lists The ParameterNames that were loaded. """
####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/icmFuncHead.py"

####+END:

    if icm.Interactivity().interactiveInvokation(interactive):
        icmRunArgs = G.icmRunArgsGet()
        if icm.cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=icm.int__gt):
            return(icm.ReturnCode.UsageError)

    inPrep_usageParams(interactive=True,
                       cmndName="usageParams",
    ) 
    
    return


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *ICM Specific Interactively Invokable Functions (ICM-CMND)*
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-CMND      ::  inPrep_usageParams    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=False, fnExit=False)
def inPrep_usageParams(interactive, cmndName):
    """ Get relevant input parameters
    """
####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/icmFuncHead.py"

####+END:

    G.usageParams.enforceScope=None

            
    return



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-CMND      ::  enetLibsUpdate    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def enetLibsUpdate(
        interactive=False,
        targetFqdn=None,     # Optional
        accessMethod=None,   # Optional
        userName=None,       # Optional
        password=None,       # Optional
):
    """ Given An ToIcmTag, dateVer in TICMO
    """
    try: icm.callableEntryEnhancer(type='cmnd')
    except StopIteration:  return

    cmndThis = icm.FUNC_currentGet().__name__

    if interactive == True:
        G = icm.IcmGlobalContext()
        icmRunArgs = G.icmRunArgsGet()

        if not len(icmRunArgs.cmndArgs) == 0:
            try:  icm.EH_runTime(format(cmndThis + 'Bad Number Of cmndArgs'))
            except RuntimeError:  return


    targetsAccessList=toIcm.targetsAccessListGet(interactive=interactive,
                                                 targetFqdn=targetFqdn,
                                                 accessMethod=accessMethod,
                                                 userName=userName,
                                                 password=password)

    targetParamsList = toIcm.targetParamsListGet(interactive=interactive)

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def targetsListProc(pathTargetsList):
        """Process List of Ephemera and Persistent Targets"""
        @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
        def targetProc(thisPathTarget):
            """Process One Target"""
            @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)            
            def paramsListProc(paramsList):
                """Process List of Parameters"""
                @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)            
                def paramProc(thisParam):
                    """At this point, we have the target and the parameter, ready for processing.
                    - From thisParam's fileParams, get the agent and parName, 
                    - Then remoteExec the agent on target and get the results.
                    - Record the obtained results with local invokation of the agent.
                    """
                    
                    icm.TM_here('targetPath=' + thisPathTarget)  # Target Access Information
                    icm.TM_here(format('ticmoBase=' + thisTicmoBase))  # TICMO Base

                    paramBase = thisParam.base()
                    icm.TM_here('paramBase=' + paramBase)

                    agent = icm.FILE_ParamValueReadFrom(parRoot=paramBase, parName='agent')
                    if not agent: return(icm.EH_problem_unassignedError())
                        
                    parName = icm.FILE_ParamValueReadFrom(parRoot=paramBase, parName='parName')
                    if not parName: return(icm.EH_problem_unassignedError())

                    commandLine=format(agent + ' -p mode=agent -i ' + parName)
                    icm.LOG_here('RemoteExec: ' + commandLine)                    
                                                
                    resultLines = linuxTarget.runCommand(connection, commandLine)

                    pipeableResultLines = ""
                    for thisResultLine in resultLines:
                        pipeableResultLines =  pipeableResultLines + thisResultLine + '\n'
                    
                    icm.LOG_here('ResultLines: ' + str(resultLines)) 

                    # We can now dateVer and empnaPkg write the resultLines for parName in TICMO
                    #fileParWriteBase = os.path.join(thisTicmoBase, empnaPkg, dateVer)

                    # updated =  icm.FILE_ParamWriteTo(parRoot=fileParWriteBase,
                    #                               parName=parName,
                    #                               parValue=resultLines[0])

                    #
                    # We ask the agent to capture the resultLines in ticmo
                    #
                    commandLine=format(agent  + ' ' + '-n showRun -p mode=capture -p ticmoBase=' +  ' -i ' + parName)
                    commandArgs=shlex.split(commandLine)

                    icm.LOG_here('SubProc: ' + commandLine)                                        
                    p = subprocess.Popen(commandArgs,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)

                    out, err = p.communicate(input=format(pipeableResultLines.encode()))

                    if out: icm.ANN_note("Stdout: " +  out)
                    if err: icm.ANN_note("Stderr: " +  err)

                    return
                                    
                for thisParam in paramsList:
                    paramProc(thisParam)
                return    

            linuxTarget = toIcm.TARGET_Proxy_Linux(basePath=thisPathTarget)

            accessParams = linuxTarget.accessParamsGet()
            targetId = accessParams.targetFqdnValue

            thisTicmoBase = toIcm.targetBaseGet(targetId=targetId)

            connection = linuxTarget.connect()

            paramsListProc(targetParamsList)
            
            return            

        for thisPathTarget in pathTargetsList:
            targetProc(thisPathTarget)

        return

    targetsListProc(targetsAccessList)

    #empna.dateVerRecordForNext(dateVer=dateVer)

    return

####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "new" :cmndName "linuxUsageKpisRetrieve" :comment "" :parsMand "" :parsOpt "targetFqdn accessMethod userName password" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || ICM-Cmnd       :: /linuxUsageKpisRetrieve/ parsMand= parsOpt=targetFqdn accessMethod userName password argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class linuxUsageKpisRetrieve(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'targetFqdn', 'accessMethod', 'userName', 'password', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        targetFqdn=None,         # or Cmnd-Input
        accessMethod=None,         # or Cmnd-Input
        userName=None,         # or Cmnd-Input
        password=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'targetFqdn': targetFqdn, 'accessMethod': accessMethod, 'userName': userName, 'password': password, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        targetFqdn = callParamsDict['targetFqdn']
        accessMethod = callParamsDict['accessMethod']
        userName = callParamsDict['userName']
        password = callParamsDict['password']

####+END:

        targetsAccessList=toIcm.targetsAccessListGet(interactive=interactive,
                                                     targetFqdn=targetFqdn,
                                                     accessMethod=accessMethod,
                                                     userName=userName,
                                                     password=password)

        targetParamsList = toIcm.targetParamsListGet(interactive=interactive)

        @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
        def targetsListProc(pathTargetsList):
            """Process List of Ephemera and Persistent Targets"""
            @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
            def targetProc(thisPathTarget):
                """Process One Target"""
                @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)            
                def paramsListProc(paramsList):
                    """Process List of Parameters"""
                    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)            
                    def paramProc(thisParam):
                        """At this point, we have the target and the parameter, ready for processing.
                        - From thisParam's fileParams, get the agent and parName, 
                        - Then remoteExec the agent on target and get the results.
                        - Record the obtained results with local invokation of the agent.
                        """

                        icm.TM_here('targetPath=' + thisPathTarget)  # Target Access Information
                        icm.TM_here(format('ticmoBase=' + thisTicmoBase))  # TICMO Base

                        paramBase = thisParam.base()
                        icm.TM_here('paramBase=' + paramBase)

                        agent = icm.FILE_ParamValueReadFrom(parRoot=paramBase, parName='agent')
                        if not agent: return(icm.EH_problem_unassignedError())

                        parName = icm.FILE_ParamValueReadFrom(parRoot=paramBase, parName='parName')
                        if not parName: return(icm.EH_problem_unassignedError())

                        commandLine=format(agent + ' -p mode=agent -i ' + parName)
                        icm.LOG_here('RemoteExec: ' + commandLine)                    

                        resultLines = linuxTarget.runCommand(connection, commandLine)

                        pipeableResultLines = ""
                        for thisResultLine in resultLines:
                            pipeableResultLines =  pipeableResultLines + thisResultLine + '\n'

                        icm.LOG_here('ResultLines: ' + str(resultLines)) 

                        # We can now dateVer and empnaPkg write the resultLines for parName in TICMO
                        #fileParWriteBase = os.path.join(thisTicmoBase, empnaPkg, dateVer)

                        # updated =  icm.FILE_ParamWriteTo(parRoot=fileParWriteBase,
                        #                               parName=parName,
                        #                               parValue=resultLines[0])

                        #
                        # We ask the agent to capture the resultLines in ticmo
                        #
                        commandLine=format(agent  + ' ' + '-n showRun -p mode=capture -p ticmoBase=' +  ' -i ' + parName)
                        commandArgs=shlex.split(commandLine)

                        icm.LOG_here('SubProc: ' + commandLine)                                        
                        p = subprocess.Popen(commandArgs,
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)

                        out, err = p.communicate(input=format(pipeableResultLines.encode()))

                        if out: icm.ANN_note("Stdout: " +  out)
                        if err: icm.ANN_note("Stderr: " +  err)

                        return

                    for thisParam in paramsList:
                        paramProc(thisParam)
                    return    

                linuxTarget = toIcm.TARGET_Proxy_Linux(basePath=thisPathTarget)

                accessParams = linuxTarget.accessParamsGet()
                targetId = accessParams.targetFqdnValue

                thisTicmoBase = toIcm.targetBaseGet(targetId=targetId)

                connection = linuxTarget.connect()

                paramsListProc(targetParamsList)

                return            

            for thisPathTarget in pathTargetsList:
                targetProc(thisPathTarget)

            return

        targetsListProc(targetsAccessList)

        #empna.dateVerRecordForNext(dateVer=dateVer)

        return


####+BEGIN: bx:icm:python:section :title "Common/Generic Facilities -- Library Candidates"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common/Generic Facilities -- Library Candidates*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

    
####+BEGIN: bx:icm:python:section :title "= =Framework::=   G_main -- Instead Of ICM Dispatcher ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::=   G_main -- Instead Of ICM Dispatcher =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:func :funcName "G_main" :funcType "FrameWrk" :retType "Void" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || Func-FrameWrk  :: /G_main/ retType=Void argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def G_main():
####+END:
    """ 
** Replaces ICM dispatcher for other command line args parsings.
"""
    pass

####+BEGIN: bx:icm:python:icmItem :itemType "Configuration" :itemTitle "= =Framework::= g_ Settings -- ICMs Imports ="
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]] || Configuration  :: = =Framework::= g_ Settings -- ICMs Imports =  [[elisp:(org-cycle)][| ]]
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
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Unused Facilities -- Temporary Junk Yard*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:icm:python:section :title "End Of Editable Text"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
