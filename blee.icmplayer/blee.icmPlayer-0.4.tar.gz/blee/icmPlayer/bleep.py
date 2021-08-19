# -*- coding: utf-8 -*-
"""\
* TODO *[Summary]* ::  A /library/ for BleeIcmPlayer implementation.
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/de/bx/nne/dev-py/pypi/pkgs/blee/icmPlayer/dev/blee/icmPlayer/bleep.py :: [[elisp:(org-cycle)][| ]]
 is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
 *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
 A Python Interactively Command Module (PyICM). Part Of ByStar.
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 Warning: All edits wityhin Dynamic Blocks may be lost.
"""
####+END:


"""
*  [[elisp:(org-cycle)][| *Lib-Module-INFO:* |]] :: Author, Copyleft and Version Information
"""

####+BEGIN: bx:global:lib:name-py :style "fileName"
__libName__ = "bleep"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201712315400"
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
import sys
import collections
import shutil

# NOTYET, should become a dblock with its own subItem
#from unisos import ucf
from unisos import icm

G = icm.IcmGlobalContext()
G.icmLibsAppend = __file__
G.icmCmndsLibsAppend = __file__
# NOTYET DBLOCK Ends -- Rest of bisos libs follow;

from bisos.common import bxpBaseDir

####+BEGIN: bx:dblock:python:section :title "Library Description (Overview)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Library Description (Overview)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:python:icm:cmnd:classHead :cmndName "bleep_LibOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /bleep_LibOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class bleep_LibOverview(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 3,}

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
 
####+BEGIN: bx:dblock:python:section :title "Importable ICM Examples And Menus"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Importable ICM Examples And Menus*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:python:func :funcName "commonParamsSpecify" :funcType "ParSpec" :retType "" :deco "" :argsList "icmParams"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-ParSpec   :: /commonParamsSpecify/ retType= argsList=(icmParams)  [[elisp:(org-cycle)][| ]]
"""
def commonParamsSpecify(
    icmParams,
):
####+END:

    icmParams.parDictAdd(
        parName='panelBase',
        parDescription="Either an Abs path or one of here/pkg/group",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--panelBase',
    )



####+BEGIN: bx:icm:python:func :funcName "examples_icmBasic" :funcType "void" :retType "bool" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-void      :: /examples_icmBasic/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def examples_icmBasic():
####+END:
    def cpsInit(): return collections.OrderedDict()
    def menuItem(): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    #def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

    icm.cmndExampleMenuChapter('*Blee ICM Player (Update, Start, StartUpdated)*')

    cmndName = "bleepUpdate"
    cps = cpsInit(); cmndArgs = ""; menuItem()

    cmndName = "bleepPlay"
    cps = cpsInit(); cmndArgs = ""; menuItem()
        
    cmndName = "bleepPlayUpdated"
    cps = cpsInit(); cmndArgs = ""; menuItem()


 
####+BEGIN: bx:dblock:python:section :title "ICM Cmnds and Supporing Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Cmnds and Supporing Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:



####+BEGIN: bx:icm:python:func :funcName "panelBasePathObtain" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "panelBase"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-anyOrNone :: /panelBasePathObtain/ retType=bool argsList=(panelBase)  [[elisp:(org-cycle)][| ]]
"""
def panelBasePathObtain(
    panelBase,
):
####+END:
    """
** TODO NOTYET not fully implemented yet
"""

    print(panelBase)
    
    if not panelBase:
        #return "/bisos/var/core/bleePlayer"
        return ( os.path.join(
            bxpBaseDir.bpbBisos_baseObtain_var(None),
            "main/bleePlayer"
        ))
    
    if os.path.isabs(panelBase):
        return panelBase

    if panelBase == "here":
        return os.path.abspath(".")
    elif panelBase == "grouped":
        return os.path.abspath(".")
    elif panelBase == "pkged":
        return os.path.abspath(".")
    else:
        return icm.EH_problem_usageError(panelBase)

    
####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "bleepUpdate" :comment "" :parsMand "" :parsOpt "panelBase" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /bleepUpdate/ parsMand= parsOpt=panelBase argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class bleepUpdate(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'panelBase', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        panelBase=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'panelBase': panelBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        panelBase = callParamsDict['panelBase']
####+END:
        panelBasePath = panelBasePathObtain(panelBase)

        icmName = G.icmMyName()
        icmPrefix, icmExtension = os.path.splitext(icmName)

        panelFileName = "{}-Panel.org".format(icmPrefix)
        panelFileFullPath = os.path.join(
            panelBasePath,
            panelFileName,
        )

        icmPlayerInfoBaseDir =  os.path.join(
            panelBasePath,
            "var",
            icmName,
            "icmIn"
        )
        icm.unusedSuppress(icmPlayerInfoBaseDir)

        icmInputsExpose().cmnd(
            interactive=False,
            argsList=[
                os.path.join(
                    panelBasePath,
                    "./var",
                )
            ]
        )

        outcome = beginPanelStdout().cmnd(
            interactive=False,
        )
        if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))

        beginPanelStr = outcome.results

        
        if os.path.isfile(panelFileFullPath):
            shutil.copyfile(panelFileFullPath, "{}-keep".format(panelFileFullPath))
        else:
            with open(panelFileFullPath, "w") as thisFile:
                thisFile.write(beginPanelStr + '\n')

        icm.ANN_note("ls -l {}".format(panelFileFullPath))

        outcome = icm.subProc_bash("""\
bx-dblock -i dblockUpdateFiles {panelFileFullPath}"""
                                   .format(panelFileFullPath=panelFileFullPath)
        ).log()
        if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )

    def cmndDocStr(self): return """
** Update this ICM's Blee Player Panel -- But do not visit it. [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "bleepPlay" :comment "" :parsMand "" :parsOpt "panelBase" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /bleepPlay/ parsMand= parsOpt=panelBase argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class bleepPlay(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'panelBase', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        panelBase=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'panelBase': panelBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        panelBase = callParamsDict['panelBase']
####+END:
        panelBasePath = panelBasePathObtain(panelBase)

        icmName = G.icmMyName()
        icmPrefix, icmExtension = os.path.splitext(icmName)

        panelFileName = "{}-Panel.org".format(icmPrefix)
        panelFileFullPath = os.path.join(
            panelBasePath,
            panelFileName,
        )

        if os.path.isfile(panelFileFullPath):
            outcome = icm.subProc_bash("""\
emacsclient -n --eval '(find-file \"{panelFileFullPath}\")' """
                                       .format(panelFileFullPath=panelFileFullPath)
            ).log()
            if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))
            
        else:
            icm.EH_problem("Missing File -- Run Update First")
            
        icm.ANN_note("ls -l {}".format(panelFileFullPath))
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )

    def cmndDocStr(self): return """
** Visit this ICM's Blee Player Panel -- But do not update. [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "bleepPlayUpdated" :comment "" :parsMand "" :parsOpt "panelBase" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /bleepPlayUpdated/ parsMand= parsOpt=panelBase argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class bleepPlayUpdated(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'panelBase', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        panelBase=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'panelBase': panelBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        panelBase = callParamsDict['panelBase']
####+END:

        bleepUpdate().cmnd(
            interactive=False,
            panelBase=panelBase,
        )

        bleepPlay().cmnd(
            interactive=False,
            panelBase=panelBase,
        )
        

    def cmndDocStr(self): return """
** Update this ICM's Blee Player Panel and then visit it. [[elisp:(org-cycle)][| ]]
"""

 
####+BEGIN: bx:dblock:python:section :title "Subject ICM Information Exposition"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Cmnds and Supporing Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "icmInputsExpose" :comment "" :parsMand "" :parsOpt "" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /icmInputsExpose/ parsMand= parsOpt= argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class icmInputsExpose(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

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
        icmsBase = effectiveArgsList[0]

        G_myFullName = sys.argv[0]
        G_myName = os.path.basename(G_myFullName)

        icmInBase = icmsBase + "/" + G_myName + "/icmIn"
        
        print("{icmInBase}".format(icmInBase=icmInBase))
            
        icm.icmParamsToFileParamsUpdate(
            parRoot="{icmInBase}/paramsFp".format(icmInBase=icmInBase),
            icmParams=G.icmParamDictGet(),
        )

        icm.icmParamsToFileParamsUpdate(
            parRoot="{icmInBase}/commonParamsFp".format(icmInBase=icmInBase),
            icmParams=icm.commonIcmParamsPrep(),
        )

        icm.cmndMainsMethodsToFileParamsUpdate(
            parRoot="{icmInBase}/cmndMainsFp".format(icmInBase=icmInBase),
        )

        icm.cmndLibsMethodsToFileParamsUpdate(
            parRoot="{icmInBase}/cmndLibsFp".format(icmInBase=icmInBase),
        )
        
        return



####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "beginPanelStdout" :comment "" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /beginPanelStdout/ parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class beginPanelStdout(icm.Cmnd):
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

        iicmName = G.icmMyName()

        resStr = beginPanelTemplate().format(
            iicmName=iicmName,
        )

        if interactive:
            print(resStr)
        
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=resStr
        )
    

####+BEGIN: bx:icm:python:func :funcName "beginPanelTemplate" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-anyOrNone :: /beginPanelTemplate/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def beginPanelTemplate():
####+END:
     templateStr = """ 
* 
####+BEGIN: bx:dblock:bnsm:top-of-menu "basic"
####+END:

####+BEGIN: bx:dblock:bnsm:this-node "basic"
####+END:

####+BEGIN: bx:dblock:bnsm:iim-see-related
####+END:
* 
####+BEGIN: iim:panel:iimsListPanels :iimsList "./_iimsList"
####+END:
* 
* /=======================================================================================================/
* 
####+BEGIN: iicm:py:panel:set:iicmName :mode "default" :iicm "{iicmName}" 
####+END:

####+BEGIN: iicm:py:panel:module-title :mode "default"
####+END:
* 
* /=======================================================================================================/
* 
*  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(org-top-overview)][(O)]]   /=====/   [[elisp:(org-cycle)][| *IICM Module Information* | ]]            /======/  [[elisp:(progn (org-shifttab) (org-content))][Content]]  /========/

####+BEGIN: iicm:py:panel:iimPkgInfo :mode "default"
####+END:
* 
*  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(org-top-overview)][(O)]]   /=====/   [[elisp:(org-cycle)][| *IICM Pkg & Framework Preparations* | ]]  /======/  [[elisp:(progn (org-shifttab) (org-content))][Content]]  /========/
####+BEGIN: iicm:py:panel:frameworkFeatures :mode "default"
####+END: 
* 
*  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(org-top-overview)][(O)]]   /=====/   [[elisp:(org-cycle)][| *IICMs Development Workbench* | ]]        /======/  [[elisp:(progn (org-shifttab) (org-content))][Content]]  /========/
####+BEGIN: iicm:py:panel:devWorkbench :mode "default"
####+END:          
* 
####+BEGIN: iicm:py:panel:execControlShow :mode "default" :orgLevel "1"
####+END:    
* 
*  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(org-top-overview)][(O)]] /===/      [[elisp:(org-cycle)][| =Select IICM IIF (Method)= | ]]                        /====/ [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (org-shifttab) (org-content))][(C)]] /====/
** 
####+BEGIN: iicm:py:panel:execControlShow  :mode "default" :orgLevel "2"
####+END:

####+BEGIN: iicm:py:iifBox:common:selector :mode "default"  :baseDir "./var/{iicmName}/iicmIn/iifMainsFp"
####+END:
**   [[elisp:(org-show-subtree)][=|=]]  [[elisp:(org-top-overview)][(O)]] /===/          =Select IICM Libs (Common) IIF (Method)=         /====/ [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (org-shifttab) (org-content))][(C)]] /====/
** 
####+BEGIN: iicm:py:panel:execControlShow  :mode "default" :iim "mboxRetrieve.sh"
####+END:
####+BEGIN: iicm:py:iifBox:common:selector :mode "default" :iim "{iicmName}" :baseDir "./var/{iicmName}/iicmIn/iifLibsFp"
####+END:

    
####+BEGIN: iicm:py:panel:execControlShow :mode "default" :iim "mboxRetrieve.sh"
####+END:    
* 
*  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(org-top-overview)][(O)]] /===/      [[elisp:(org-cycle)][| =Select IIF's FP Parameters And Args= | ]]             /====/ [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (org-shifttab) (org-content))][(C)]] /====/
** 
####+BEGIN: iicm:py:panel:execControlShow :mode "default" :iim "mboxRetrieve.sh"
####+END:    
** 
####+BEGIN: iicm:py:menuBox:params:selectValues :mode "default" :iim "{iicmName}" :scope "param" :title "IIM=moduleName Shorter" :baseDir "./var/{iicmName}/iicmIn/paramsFp"
####+END:
**                               =IIF Args=
**     
** 
####+BEGIN: iicm:py:panel:execControlShow :mode "default" :iim "mboxRetrieve.sh"
####+END:
** 
** IIF Args Table Comes Here
**  
    
####+BEGIN: iicm:py:menuBox:selectBxSrf :mode "DISABLED" :scope "bxsrf"
####+END:    

####+BEGINNOT: iicm:py:menuBox:selectTargets  :mode "default" :iim "{iicmName}" :scope "target"
* 
*  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(org-top-overview)][(O)]] /===/      [[elisp:(org-cycle)][| =Select Targets For Chosen Method (IIF)= | ]]          /====/ [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (org-shifttab) (org-content))][(C)]] /====/
** 
####+END:    

####+BEGIN: iicm:py:panel:execControlShow :mode "default" :iim "mboxRetrieve.sh"
####+END:    
* 
*  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(org-top-overview)][(O)]] /===/      [[elisp:(org-cycle)][| =Select IICM Common Controls And Scheduling= | ]]      /====/ [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (org-shifttab) (org-content))][(C)]] /====/
** 
####+BEGIN: iicm:py:panel:execControlShow :mode "default" :iim "mboxRetrieve.sh"
####+END:    
####+BEGIN: iicm:py:menuBox:params:selectValues :mode "default" :iim "{iicmName}" :scope "param" :title "IIM=moduleName Shorter" :baseDir "./var/{iicmName}/iicmIn/commonParamsFp"
####+END:
** 
**                             =Scheduling And Wrapper=
** 
####+BEGIN: iicm:py:panel:execControlShow :mode "default" :iim "mboxRetrieve.sh"
####+END: 
** 
**  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(org-cycle)][| ]]  [[elisp:(delete-other-windows)][(1)]] || [[elisp:(blee:menu-box:cmndLineResultsRefresh)][Refresh Command Line]] || [[elisp:(blee:menu-box:paramsPropListClear)][Clear Params Settings]] 
####+BEGINNOT: iim:bash:menuBox:commonControls:selectValues  :mode "default" :iim "mboxRetrieve.sh" :baseDir "./var/mboxRetrieve.sh/iimsIn/commonControlFp"

**  ======================================================================================================|
**  |                 *IIM Bash Editor For: [[file:./var/mboxRetrieve.sh/iimsIn/commonControlFp][./var/mboxRetrieve.sh/iimsIn/commonControlFp]]*                 |
**  +-----------------------------------------------------------------------------------------------------|
**  |  /Par Name/        |    /Parameter Value/      |          /Parameter Description/              |info|
**  +-----------------------------------------------------------------------------------------------------|
**  | [[elisp:(fp:node:menuBox:popupMenu:iimBash:trigger "./var/mboxRetrieve.sh/iimsIn/commonControlFp/wrapper" 'iim:bash:cmnd:commonControl/dict/bufLoc)][:wrapper]]          *| None                      |* Command Wrapping IIM Exec (e.g. echo, time)  |[[info]]|
**  +-----------------------------------------------------------------------------------------------------|
**  | [[elisp:(fp:node:menuBox:popupMenu:iimBash:trigger "./var/mboxRetrieve.sh/iimsIn/commonControlFp/iimName" 'iim:bash:cmnd:commonControl/dict/bufLoc)][:iimName]]          *| mboxRetrieve.sh           |* Interactively Invokable Module (IIM)         |[[info]]|
**  +-----------------------------------------------------------------------------------------------------|
**  ======================================================================================================|
** 
####+END:
* 
####+BEGIN: iicm:py:menuBox:iimExamples :mode "default" :iim "{iicmName}"
####+END:
* 
*  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(org-top-overview)][(O)]]   /=====/   [[elisp:(org-cycle)][| *Monitor IIM Execution* | ]]          /========/  [[elisp:(progn (org-shifttab) (org-content))][Content]]  /==========/
* 
*  [[elisp:(org-show-subtree)][=|=]]  [[elisp:(beginning-of-buffer)][Top]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(org-top-overview)][(O)]]   /=====/   [[elisp:(org-cycle)][| *IIM Execution Results* | ]]          /========/  [[elisp:(progn (org-shifttab) (org-content))][Content]]  /==========/
* 
* /=======================================================================================================/
* 
*  [[elisp:(beginning-of-buffer)][Top]] #####################  [[elisp:(delete-other-windows)][(1)]]      *Common Footer Controls*
####+BEGIN: bx:dblock:org:parameters :types "agenda"
####+END:


####+BEGIN: bx:dblock:bnsm:end-of-menu "basic"
####+END:
*  [[elisp:(org-cycle)][| ]]  Local Vars  ::                  *Org-Mode And Emacs Specific Configurations*   [[elisp:(org-cycle)][| ]]
#+CATEGORY: iimPanel
#+STARTUP: overview

## Local Variables:
## eval: (setq bx:iimp:iimModeArgs "")
## eval: (bx:iimp:cmndLineSpecs :name "bxpManage.py")
## eval: (bx:iimBash:cmndLineSpecs :name "lcntProc.sh")
## eval: (setq bx:curUnit "lcntProc")
## End:
"""
     return templateStr




####+BEGIN: bx:icm:python:section :title "End Of Editable Text"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
