#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""\
*    *[Summary]* :: An =ICM=: a beginning template for development of new ICMs.
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/de/bx/nne/dev-py/pypi/pkgs/bisos/lcnt/dev/bin/beamerExternalExtensions.py :: [[elisp:(org-cycle)][| ]]
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
__icmName__ = "beamerExternalExtensions"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201801175435"
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
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || =Imports=      :: *IMPORTS*  [[elisp:(org-cycle)][| ]]
"""
####+END:

import sys
import os
import io

import collections

from pyPdf import PdfFileReader
import re

from unisos import ucf
from unisos import icm

from blee.icmPlayer import bleep
from bisos.lcnt import latexSup

g_importedCmnds = {        # Enumerate modules from which CMNDs become invokable
    'bleep': bleep.__file__,
    'latexSup': latexSup.__file__,    
}


        

####+BEGIN: bx:icm:python:section :title "= =Framework::= ICM  Description (Overview) ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM  Description (Overview) =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "icmOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /icmOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class icmOverview(icm.Cmnd):
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
**      ====[[elisp:(org-cycle)][Fold]]==== Description:
Given the base directory of a beamer produced pdf file, process all disposition aspects.
This script provides full integration between Impressive and Beamer based on the following:

***      ==[[elisp:(org-cycle)][Fold]]== Model
****   =[[elisp:(org-cycle)][Fold]]= Content Structure Vs Content Dispositions
       A given document (content) has a specific structure and can have many resulting formats (Article, Presentaton, VoiceOver, ScreenCast (Video)).
       A given content can be presented/exposed in a variety of ways. Content disposition parameters play a role at that time.
****   =[[elisp:(org-cycle)][Fold]]= SlideNumber vs FrameName
       frameName is an attribute of  Content Structure. It is specified in the latex source and corresponding disposition parameters
       slideNumber (page of presentation format) maps to a frameName. [NOTYET, needs better description.]
***      ==[[elisp:(org-cycle)][Fold]]== Beamer Input Disposition Tagging
****   =[[elisp:(org-cycle)][Fold]]= Each frame that requires special disposition is tagged with [label=frameName]
***      ==[[elisp:(org-cycle)][Fold]]== ./disposition.gened   Directory Structure
****   =[[elisp:(org-cycle)][Fold]]= For each slide, there is a sequential slideNumber fileParam.
****   =[[elisp:(org-cycle)][Fold]]= Value of each slideNumber is *frameName*
****   =[[elisp:(org-cycle)][Fold]]= frameName is specified in BeamerInut with [label=frameName] or if not it becomes defaultDispParams
****   =[[elisp:(org-cycle)][Fold]]= There is a baseDir  with the name frameName in ./disposition.gened
****   =[[elisp:(org-cycle)][Fold]]= That baseDir includes disposition parameters for the slide such as:
       - transitionType -- These are all autogenerated from LaTeX source
***      ==[[elisp:(org-cycle)][Fold]]== ./audio         Directory Structure
****   =[[elisp:(org-cycle)][Fold]]= For each frameName that has voiceOver, there is a frameName.wav file.
****   =[[elisp:(org-cycle)][Fold]]= With audioProc.sh -- Based on frameName.wav, frameName.mp3 and frameName.length
***      ==[[elisp:(org-cycle)][Fold]]== ./impressive    Directory Structure
****   =[[elisp:(org-cycle)][Fold]]= For each of the well-known usages, an impressive input file with the name use.info will be created
****   =[[elisp:(org-cycle)][Fold]]= voiceOver.info  is gernerated by -i xxx of this script

**      ====[[elisp:(org-cycle)][Fold]]==== Background and Assumptions:
***      ==[[elisp:(org-cycle)][Fold]]== Components:  Debian/Ubuntu + Emacs + Beamer + Impressive
***      ==[[elisp:(org-cycle)][Fold]]== Background: Beamer + (Impressive + Pdfpc) gets us almost there. This is about getting all the way there.
***      ==[[elisp:(org-cycle)][Fold]]== Goals/Requirements:
****   =[[elisp:(org-cycle)][Fold]]=  BeamerInput should be the primary source for EVERYTHING.
****   =[[elisp:(org-cycle)][Fold]]=  Audio files should correlate to BeamerInput.
****   =[[elisp:(org-cycle)][Fold]]=  Presenter Console should be emacs based and provide for controlling Impressive.
****   =[[elisp:(org-cycle)][Fold]]=  Emacs should permit editing BeamerInput in the context of current slide.
***      ==[[elisp:(org-cycle)][Fold]]== Contours Of Languages And Tools
****   =[[elisp:(org-cycle)][Fold]]= Bash -- To glue things together
****   =[[elisp:(org-cycle)][Fold]]= Python -- To control Impressive and communicate with Emacs
****   =[[elisp:(org-cycle)][Fold]]= Elisp -- To control Emacs and Communicate with Impressive
****   =[[elisp:(org-cycle)][Fold]]= Tex/LaTeX -- To generate stuff out of BeamerInput.
****   =[[elisp:(org-cycle)][Fold]]= Choosing NOT to use: JavaScript, Perl
**      ====[[elisp:(org-cycle)][Fold]]==== Design:
***      ==[[elisp:(org-cycle)][Fold]]== Presenter-Console
	 Two Options exist, Both are usable, neither of them is ultimate
****   =[[elisp:(org-cycle)][Fold]]= pdfpc Presenter Notes.
       Ubuntu's apt-get pdf-presenter-console will be used for now.
       With pdfpcnotes.sty \pnotes{} produces pres.pdfpc which can then be used by pdfpc
****   =[[elisp:(org-cycle)][Fold]]= Javascript based presenter-for-impressive -- http://flobosg.com/en/2013/02/impressive-presenter -- https://github.com/flobosg/impressive-presenter
       I have packaged this and it does work. It does not have a feature to get notes from BeamerInput.
       Its model is flexible and the same model can be adopted for Emacs-Impressive-Presenter-Console.

****   =[[elisp:(org-cycle)][Fold]]= Emacs-Impressive-Presenter-Console 
       Mimic the javascript model of presenter-for-impressive with elisp.
       Extract notes from Beamer-input similar to pdfpc Presenter Notes.
       Send a particular slideNumber Selection to impressive -- May need updates to impressive to listen on a socket (similar to vlc's remote control).
       Emacs will display Current+Previous slides. Will have a running clock.
       Will permit BeamerInput notes editing of the current slide.

***      ==[[elisp:(org-cycle)][Fold]]== Correlation Of PDF File to BeamerInput
****   =[[elisp:(org-cycle)][Fold]]= Relevant Info is in pdfOut.nav and pdfOut.aux  and pdf.snm -- most convenient is .snm -- (for [label=frameName])
**** TODO =[[elisp:(org-cycle)][Fold]]= Start From Beamer-With-Impressive http://code.google.com/p/makebeamerinfo/  -- Takes latex.nav, generates impressive.info
       Convert perl to python and integrate with above.

***      ==[[elisp:(org-cycle)][Fold]]== Beamer Input Tagging
****   =[[elisp:(org-cycle)][Fold]]=  Impressive features are tagged with comments correlated to frameNames
****   =[[elisp:(org-cycle)][Fold]]=  The action parts are python callables in the context of this script.
****   =[[elisp:(org-cycle)][Fold]]=  Those functions, act within the ./disposition.gened directory, by creating/modifying
       file parameters.
****   =[[elisp:(org-cycle)][Fold]]=  The tags are identified in beamer source, and then acted upon with this script.

**      [End-Of-Description]
"""
        
        moduleUsage="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]
**      How-Tos: Typical Usage involves
***     -i updateDispositionBase ./presentationEnFa.pdf   ## Creates ./disposistion.gened
***     -i dispositionToImpressivePurposed  voiceOver     ## No Video Recording -- Creates ./tmp/impressive.info and suggests cmndLineTo 
***     -i -p slidesRange 1 dispositionToImpressivePurposed voiceOver recorderEach  ## Record ONLY specified slide and its transition to next
***     -i dispositionToImpressivePurposed voiceOver recorderEach  ## Record ALL displayed one after another
***     -i dispositionToImpressivePurposed voiceOver recorderOnce  ## Record the FIRST displayed slide (runOnce -- IS NOT WORKING)
**      [End-Of-Usage]
"""
        
        moduleStatus="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO [[elisp:(org-cycle)][| ]]  Current         :: Just getting started [[elisp:(org-cycle)][| ]]
** TODO ==[[elisp:(org-cycle)][Fold]]== Add Tagging Extraction
** TODO ==[[elisp:(org-cycle)][Fold]]== Look Into makebeamerinfo
** TODO ==[[elisp:(org-cycle)][Fold]]== Extract and Cross Link this against BxScreenCast Panel
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


####+BEGIN: bx:icm:python:section :title "= =Framework::= ICM Hooks ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM Hooks =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:func :funcName "g_icmChars" :comment "ICM Characteristics Spec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-FrameWrk  :: /g_icmChars/ =ICM Characteristics Spec= retType=Void argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def g_icmChars():
####+END:
    icmInfo['panel'] = "{}-Panel.org".format(__icmName__)
    icmInfo['groupingType'] = "IcmGroupingType-pkged"
    icmInfo['cmndParts'] = "IcmCmndParts[common] IcmCmndParts[param]"
    
g_icmChars()


####+BEGIN: bx:icm:python:func :funcName "g_icmPreCmnds" :funcType "FrameWrk" :retType "Void" :deco "default" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-FrameWrk  :: /g_icmPreCmnds/ retType=Void argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def g_icmPreCmnds():
####+END:
    """ PreHook """
    pass


####+BEGIN: bx:icm:python:func :funcName "g_icmPostCmnds" :funcType "FrameWrk" :retType "Void" :deco "default" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-FrameWrk  :: /g_icmPostCmnds/ retType=Void argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
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
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-FrameWrk  :: /g_argsExtraSpecify/ =FrameWrk: ArgsSpec= retType=Void argsList=(parser)  [[elisp:(org-cycle)][| ]]
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
        parName='dispositionBase',
        parDescription="Disposition Base Directory",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--dispositionBase',
        )

    icmParams.parDictAdd(
        parName='inPdf',
        parDescription="Input Pdf file with ttytex etc implied",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--inPdf',
    )

    icmParams.parDictAdd(
        parName='framesRange',
        parDescription="Frames Range -- For Now Just Initial Number",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--framesRange',
    )
    
    bleep.commonParamsSpecify(icmParams)    
       
    icm.argsparseBasedOnIcmParams(parser, icmParams)

    # So that it can be processed later as well.
    G.icmParamDictSet(icmParams)
    
    return

####+BEGIN: bx:icm:python:func :funcName "dispositionBaseDefault" :funcType "defaultVerify" :retType "echo" :deco "" :argsList "dispositionBase"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-defaultVerify :: /dispositionBaseDefault/ retType=echo argsList=(dispositionBase)  [[elisp:(org-cycle)][| ]]
"""
def dispositionBaseDefault(
    dispositionBase,
):
####+END:
    if not dispositionBase:
        return './disposition.gened'
    else:
        return dispositionBase


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "examples" :cmndType "ICM-Cmnd-FWrk" :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd-FWrk  :: /examples/ =FrameWrk: ICM Examples= parsMand= parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
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
        comment='none'
        def cpsInit(): global comment; comment='none'; return collections.OrderedDict()
        def menuItem(): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, comment=comment, verbosity='little')
        def menuItemUnverbose(): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, comment=comment, verbosity='none')        
        def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        logControler = icm.LOG_Control()
        logControler.loggerSetLevel(20)
        
        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())
        
        icm.G_commonBriefExamples()

        bleep.examples_icmBasic()

        mainPdfFile="""./presentationEnFa.pdf"""
        mainTtytexFile="""./presentationEnFa.ttytex"""
        mainSnmFile="""./presentationEnFa.snm"""

        selectedFramesRange = "1"
        
####+BEGIN: bx:icm:python:cmnd:subSection :title "Dev And Testing"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Dev And Testing*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

        icm.cmndExampleMenuChapter('*General Dev and Testing IIFs*')

        cmndName = "unitTest"
        cmndArgs = ""; cps = cpsInit(); # cps['icmsPkgName'] = icmsPkgName 
        menuItem()
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='full')


####+BEGIN: bx:icm:python:cmnd:subSection :title "Disposition Setup/Set/Update -- ./disposition.gened"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Disposition Setup/Set/Update -- ./disposition.gened*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        icm.cmndExampleMenuChapter('*Disposition Setup/Set/Update  -- ./disposition.gened*')

        cmndName = "dispositionBaseSetup";  comment="""# Just creates dispositionBaseDir."""
        menuItem()
        cmndArgs = ""; cps = cpsInit(); cps['dispositionBase'] = '/tmp/t3/DISP'
        menuItem()

        cmndName = "dispositionParamSet"
        cmndArgs = "globalTimeout 2000"; cps = cpsInit(); # cps['dispositionBase'] = '/tmp/t3/DISP'
        menuItem()

        cmndName = "frameParSet"
        cmndArgs = "frameName transition up"; cps = cpsInit();   cps['dispositionBase'] = '/tmp/t3/DISP'
        menuItem()

####+BEGIN: bx:icm:python:cmnd:subSection :title "Extract Frames Parameters From Pdf/snm files -- into DispositionBase"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          **Extract into DispositionBase Frames Parameters Info From Pdf/snm/tex files**  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        icm.cmndExampleMenuChapter('*Extract Frames Parameters From Pdf/snm files -- into DispositionBase*')

        cmndName = "latexSrcToDispositionUpdate" ; comment = """# Sets up dispositionBase based on pdf and snm info."""
        cmndArgs = mainPdfFile; cps = cpsInit(); 
        menuItem()
        cmndArgs = mainPdfFile; cps = cpsInit();  cps['dispositionBase'] = "./disposition.gened"
        menuItem()
        
        cmndName = "frameNamesList"; comment="""# Gets frame names from pdf file."""
        cmndArgs = mainPdfFile; cps = cpsInit(); # cps['icmsPkgName'] = icmsPkgName 
        menuItemUnverbose()
        
        #cmndName = "frameNamesGet" ; comment="""# Gets from latex snm file."""
        #cmndArgs = mainSnmFile + " 25"; cps = cpsInit(); # cps['icmsPkgName'] = icmsPkgName 
        #menuItem()

        
####+BEGIN: bx:icm:python:cmnd:subSection :title "Extract Frames Parameters From Pdf/snm files -- into DispositionBase"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *pdfToDisposition*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        icm.cmndExampleMenuSection('Extract Frames Parameters From TeX files -- into DispositionBase')
        
        cmndName = "beamerExternalTagsUpdateAsFPs"  ; comment = ""
        cmndArgs = mainTtytexFile;  cps = cpsInit(); #  cps['load'] = ''
        menuItem()

        
####+BEGIN: bx:icm:python:cmnd:subSection :title "DispositionBase Full Update"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *DispositionBase Full Update*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        icm.cmndExampleMenuSection('DispositionBase Full Update')
        
        cmndName = "updateDispositionBase"  ; comment = "# Primary Preparations"
        cmndArgs = mainPdfFile;  cps = cpsInit();  cps['dispositionBase'] = "./disposition.gened"
        menuItem()

        cps = cpsInit();  menuItemUnverbose()

        cmndName = "dispositionFrameNamesList"  ; comment = "# List FrameNames from dispositionBase"
        cmndArgs = "";
        cps = cpsInit();  menuItemUnverbose()
        

        
####+BEGIN: bx:icm:python:cmnd:subSection :title "Common Capabilities"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Common Capabilities*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        icm.cmndExampleMenuSection('Common Capabilities')

        cmndName = "latexInputFilesList"  ; comment = ""
        cmndArgs =  mainTtytexFile; cps = cpsInit(); #  cps['load'] = './presentationEnFa-itags.py'
        menuItem()
        
        cmndArgs =  mainTtytexFile + " ./articleEnFa.ttytex" ; menuItem()

####+BEGIN: bx:icm:python:cmnd:subSection :title "Construct Configuration Files From Disposition Base For Impressive -- stdout"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Construct Configuration Files From Disposition Base For Impressive -- stdout*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        icm.cmndExampleMenuChapter('*Construct Configuration Files From Disposition Base For Impressive -- stdout*')

        cmndName = "frameParSet"  ; comment = ""
        cmndArgs = "frameName transition up"; cps = cpsInit();  cps['dispositionBase'] = '/tmp/t3/DISP'
        menuItem()

        cmndName = "dispositionToImpressiveInfoPurposedStdout" ; comment="""# Args specify purpose"""
        cmndArgs = "voiceOver presenter"; cps = cpsInit();
        menuItem()

        cmndArgs = "voiceOver";  menuItem()
        cmndArgs = "voiceOver recorderEach"; cps = cpsInit(); cps['framesRange'] = selectedFramesRange ;  menuItem()                 

####+BEGIN: bx:icm:python:cmnd:subSection :title "Update DispositionBase and Construct Configuration Files"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Update DispositionBase and Construct Configuration Files*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        icm.cmndExampleMenuChapter('*Construct Configuration Files From Disposition Base*')

        cmndName = "updateThenImpressiveInfoStdout" ; comment="""# Args specify purpose"""
        cps = cpsInit(); cps['inPdf'] = "./presentationEnFa.pdf"

        cmndArgs = "voiceOver";  menuItem()
        cmndArgs = "voiceOver recorderEach";  cps['framesRange'] = selectedFramesRange ;  menuItem()                         
        

####+BEGIN: bx:icm:python:cmnd:subSection :title "Construct Configuration Files And Run Impressive"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Construct Configuration Files And Run Impressive*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        icm.cmndExampleMenuChapter('*Construct Configuration Files And Run Impressive*')

        cmndName = "updateDispositionBase"  ; comment = "# Primary Preparations"
        cmndArgs = mainPdfFile; cps = cpsInit();  menuItemUnverbose()

        cmndName = "frameNamesList"; comment="""# Gets frame names from pdf file."""
        cmndArgs = mainPdfFile; cps = cpsInit();  menuItemUnverbose()
     

        cmndName = "dispositionToImpressivePurposed" ; comment="""# Applies To ALL -- Args specify purpose"""
        cps = cpsInit(); cps['inPdf'] = "./presentationEnFa.pdf"
        cmndArgs = "voiceOver";  menuItemUnverbose()
        cmndArgs = "voiceOver recorderEach" ; menuItemUnverbose()

        cmndName = "dispositionToImpressivePurposed" ; comment="""# Applies To framesRange -- Args specify purpose"""
        cps = cpsInit(); cps['inPdf'] = "./presentationEnFa.pdf"
        cmndArgs = "voiceOver";  menuItemUnverbose()
        cmndArgs = "voiceOver recorderEach"; cps['framesRange'] = selectedFramesRange ; menuItemUnverbose()
        
        cmndName = "dispositionToImpressivePurposed" ; comment="""# Applies To Any -- Args specify purpose"""
        cps = cpsInit(); cps['inPdf'] = "./presentationEnFa.pdf"
        cmndArgs = "voiceOver";  menuItemUnverbose()
        cmndArgs = "voiceOver recorderOnce" ; menuItemUnverbose()
        
        
####+BEGIN: bx:icm:python:cmnd:subSection :title "Direct Invoke Commands"
        """
**  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Direct Invoke Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        
        icm.cmndExampleMenuChapter('*Direct Invoke Commands*')

        execLineEx("""impressive""".format())

        return(cmndOutcome)

    def cmndDocStr(self): return """
** ICM Examples -- List of commonly used lines for this ICM [[elisp:(org-cycle)][| ]]
"""
    
####+BEGIN: bx:icm:python:section :title "ICM Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "unitTest" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /unitTest/ parsMand= parsOpt= argsMin=0 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class unitTest(icm.Cmnd):
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

        myName=self.myName()
        thisOutcome = icm.OpOutcome(invokerName=myName)

        print(G.icmInfo)

        for eachArg in effectiveArgsList:
            icm.ANN_here("{}".format(eachArg))

        print((icm.__file__))
        print(sys.path)

        import imp
        print((imp.find_module('unisos/icm')))

        @ucf.runOnceOnly
        def echo(str):
            print(str)
            
        echo("first")
        echo("second")  # Should not run
    
        return thisOutcome
    
    def cmndDocStr(self): return """
** Place holder for ICM's experimental or test code.  [[elisp:(org-cycle)][| ]]
 You can use this Cmnd for rapid prototyping and testing of newly developed functions.
"""

    
####+BEGIN: bx:icm:python:section :title "Disposition Base Setup"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Disposition Base Setup*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
    


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "dispositionBaseSetup" :comment "Creates dispositionBase" :parsMand "" :parsOpt "dispositionBase" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /dispositionBaseSetup/ =Creates dispositionBase= parsMand= parsOpt=dispositionBase argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class dispositionBaseSetup(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        dispositionParamBaseSetup().cmnd(
            interactive=False,
            dispositionBase=dispositionBase,
            dispositionParBase='.',
        )



	def cmndDesc(): """
** Sets up the base ./disposition.gened FILE_Param directory. Calls dispositionParamBaseSetup with dispositionParBase='.'
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "dispositionParamBaseSetup" :comment "Creates the given FP base" :parsMand "" :parsOpt "dispositionBase dispositionParBase" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /dispositionParamBaseSetup/ =Creates the given FP base= parsMand= parsOpt=dispositionBase dispositionParBase argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class dispositionParamBaseSetup(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', 'dispositionParBase', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
        dispositionParBase=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'dispositionBase': dispositionBase, 'dispositionParBase': dispositionParBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
        dispositionParBase = callParamsDict['dispositionParBase']
####+END:
        
        dispositionBase = dispositionBaseDefault(dispositionBase)

        parRoot = os.path.join(dispositionBase, dispositionParBase)    

        thisParamBase = icm.FILE_ParamBase(fileSysPath=parRoot)

        thisParamBaseState = thisParamBase.baseValidityPredicate()
    
        if  thisParamBaseState == 'BadlyFormed':
            return icm.EH_critical_usageError('')
        elif thisParamBaseState == 'NonExistent':
            thisParamBase.baseCreate()
        elif thisParamBaseState == 'InPlace':
            icm.TM_here('InPlace')
        else:
            return icm.EH_critical_oops('thisParamBaseState=' + thisParamBaseState)

        return


	def cmndDesc(): """
** Sets up ParBase -- For example for slideNumber and frameName.
"""

####+BEGIN: bx:icm:python:cmnd:classHead  :cmndName "dispositionParamSet" :comment "For Global disposition FPs" :parsMand "" :parsOpt "dispositionBase dispositionParBase" :argsMin "2" :argsMax "2" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /dispositionParamSet/ =For Global disposition FPs= parsMand= parsOpt=dispositionBase dispositionParBase argsMin=2 argsMax=2 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class dispositionParamSet(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', 'dispositionParBase', ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
        dispositionParBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'dispositionBase': dispositionBase, 'dispositionParBase': dispositionParBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
        dispositionParBase = callParamsDict['dispositionParBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        dispositionParName = effectiveArgsList[0]
        dispositionParValue = effectiveArgsList[1]

        dispositionBaseSetup().cmnd(interactive=False,
                                  dispositionBase=dispositionBase)

        parRoot = os.path.join(dispositionBase, dispositionParBase)

        thisFileParam = icm.FILE_Param()
        return  thisFileParam.writeTo(storeBase=parRoot,
                                      parName=dispositionParName,
                                      parValue=dispositionParValue)


	def cmndDesc(): """
** Thin layer on top of icm.FILE_Param()
"""

    

####+BEGIN: bx:icm:python:func :funcName "impressiveFrameParSet" :comment "Func to set FPs based on ^%BxPy" :funcType "void" :retType "none" :deco "default" :argsList "frameName parName parValue"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-void      :: /impressiveFrameParSet/ =Func to set FPs based on ^%BxPy= retType=none argsList=(frameName parName parValue) deco=default  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def impressiveFrameParSet(
    frameName,
    parName,
    parValue,
):
####+END:
    """ Typically executed at load time.
        Specified in .tex file. Meant to be terse. 
    """

    frameParSet().cmnd(
        interactive=False,
        argsList=[frameName, parName, parValue,],
    )

    
####+BEGIN: bx:icm:python:cmnd:classHead  :cmndName "frameParSet" :comment "Sets FP in dispositionBase" :parsMand "" :parsOpt "dispositionBase" :argsMin "3" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /frameParSet/ =Sets FP in dispositionBase= parsMand= parsOpt=dispositionBase argsMin=3 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class frameParSet(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', ]
    cmndArgsLen = {'Min': 3, 'Max': 3,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        frameName = effectiveArgsList[0]
        parName = effectiveArgsList[1]
        parValue = effectiveArgsList[2]

        dispositionBaseSetup().cmnd(interactive=False,
                                  dispositionBase=dispositionBase)

        dispositionParBase = frameName
        parRoot = os.path.join(dispositionBase, dispositionParBase)
        
        thisFileParam = icm.FILE_Param()

        if parName == 'sound':
            dispositionParName = 'audio'     
        else:
            dispositionParName = parName
    
        dispositionParValue = parValue
    
        icm.TM_here("frameName={frameName} parName={parName} parValue={parValue}"
                     .format(frameName=frameName, parName=dispositionParName, parValue=dispositionParValue))
    
        return  thisFileParam.writeTo(storeBase=parRoot,
                                      parName=dispositionParName,
                                      parValue=dispositionParValue)
    
        
	def cmndDesc(): """
** Thin layer on top of icm.FILE_Param()
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "latexSrcToDispositionUpdate" :comment "$1=pdfFile" :parsMand "" :parsOpt "dispositionBase" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /latexSrcToDispositionUpdate/ =$1=pdfFile= parsMand= parsOpt=dispositionBase argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class latexSrcToDispositionUpdate(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        pdfFileName = effectiveArgsList[0]
    
        document = PdfFileReader(file(pdfFileName, "rb"))
        pages = document.getNumPages()    

        dispositionBaseSetup().cmnd(
            interactive=False,
            dispositionBase=dispositionBase,
        )

        fileName, fileExtension = os.path.splitext(pdfFileName)

        #navFileName = fileName + ".nav"
        snmFileName = fileName + ".snm"

        slideNumbersNames = frameNamesGet().cmnd(
            interactive=False,
            argsList=[snmFileName, pages,],
        )
    
        for i in range(len(slideNumbersNames)):
            # impressive's first slide, usually titlePage is slide Nu 1

            slideNu=i+1
            slideNumberName=format("slide" + str(slideNu))                
            frameName = slideNumbersNames[i]
        
            dispositionParamSet().cmnd(
                interactive=False,
                dispositionBase=dispositionBase,
                dispositionParBase='.',
                argsList=[slideNumberName, frameName,],
            )

            dispositionParamBaseSetup().cmnd(
                interactive=False,
                dispositionBase=dispositionBase,
                dispositionParBase=frameName,
            )


            if os.path.isdir("./audio"):
                if frameName ==  'defaultParams':
                    pass
                else:
                    audioAbsFilePath = os.path.abspath(format("./audio" + "/" + frameName + '.wav'))
                    dispositionParamSet().cmnd(
                        interactive=False,
                        dispositionBase=dispositionBase,
                        dispositionParBase=frameName,
                        argsList=['audio', audioAbsFilePath,],
                    )
                    # NOTYET, Compute duration and add that here.
            else:
                icm.TM_here("Missing ./audio -- Skipped")

            # The first two slides (0 and 1)
            if i < 2:
                dispositionParamSet().cmnd(
                    interactive=False,
                    dispositionBase=dispositionBase,
                    dispositionParBase=frameName,
                    argsList=['transition', 'PagePeel'],
                )
        
	def cmndDesc(): """
** Given the pdfFileName,  determine total number of slides, then for each slide determine frameName.

    For each slideNumber associate frameName. For each frameName create baseParam directory.
    If ./audio create the 'sound': attribute.
    Makes sure basePdf.snm and basePdf.nav are available.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "frameNamesList" :comment "$1 is pdfFile (interactiveOnly)" :parsMand "" :parsOpt "dispositionBase" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /frameNamesList/ =$1 is pdfFile (interactiveOnly)= parsMand= parsOpt=dispositionBase argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class frameNamesList(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        pdfFileName = effectiveArgsList[0]

        thisFile=file(pdfFileName, "rb")

        document = PdfFileReader(thisFile)
        pages = document.getNumPages()    

        # dispositionBaseSetup(interactive=False, dispositionBase=dispositionBase)

        fileName, fileExtension = os.path.splitext(pdfFileName)

        #navFileName = fileName + ".nav"
        snmFileName = fileName + ".snm"

        slideNumbersNames = frameNamesGet().cmnd(
            interactive=False,
            argsList=[snmFileName, pages,],
        )

        for i in range(len(slideNumbersNames)):

            #slideNumberName=format("slide" + str(i))                
            frameName = slideNumbersNames[i]

            if interactive:
                icm.ANN_write("{slideNumber} {frameName}".format(
                    slideNumber=i+1, frameName=frameName,)
                )

        if not interactive:
            icm.EH_critical_usageErro("Not expected to be used non-interactivly. Use frameNamesGet directly.")
            
        
    def cmndDesc(): """
**  Given the pdfFileName,  determine total number of slides, then for each slide determine frameName.

    For each slideNumber associate frameName. For each frameName create baseParam directory.
    If ./audio create the 'sound': attribute.
    Makes sure basePdf.snm and basePdf.nav are available.
    """

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "frameNameQuote" :comment "$1 is frameName" :parsMand "" :parsOpt "" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /frameNameQuote/ =$1 is frameName= parsMand= parsOpt= argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class frameNameQuote(icm.Cmnd):
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

        frameName = effectiveArgsList[0]
        frameNameQuoted=""

        thisOutcome = icm.OpOutcome(invokerName=G.icmMyFullName())

        #
        thisOutcome = icm.subProc_bash(
            """uri@Encode.sh {frameName}"""
            .format(frameName=frameName),
            stdin=None, outcome=thisOutcome,
        )#.out()
        
        if thisOutcome.isProblematic():
            return(icm.EH_badOutcome(thisOutcome))

        frameNameQuoted = thisOutcome.stdout.splitlines()[0]

        if interactive:
            icm.ANN_note(frameNameQuoted)

        return frameNameQuoted

    def cmndDesc(): """
** Given frameName return frameNameQuoted.
"""
    

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "frameNamesGet" :comment "$1 is tex's snm file - $2=nuOfPages" :parsMand "" :parsOpt "" :argsMin "2" :argsMax "2" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /frameNamesGet/ =$1 is tex's snm file - $2=nuOfPages= parsMand= parsOpt= argsMin=2 argsMax=2 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class frameNamesGet(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

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

        snmFileName = effectiveArgsList[0]
        numberOfPages = int(effectiveArgsList[1])

        slideNumbersNames = []
        for i in range(0,numberOfPages):
            slideNumbersNames.append('defaultParams')
    

        # Open FileName and walkthrough it.
        with open(snmFileName, 'r') as fp:
            for line in fp:
                icm.TM_here(line)
                #\beamer@slide {summary.problem<1>}{2}
                #matchObj = re.search( r'(.beamer.slide .) (.*) (}) ({) (.*) (})', line, re.M|re.I)
                matchObj = re.search( r'(\\beamer@slide {)(.*)(<.>)(}{)(.*)(})', line, re.M|re.I)            
                if matchObj:
                    # print "matchObj.group() : ", matchObj.group()
                    # print "matchObj.group(1) : ", matchObj.group(1)
                    # print "matchObj.group(2) : ", matchObj.group(2)
                    # print "matchObj.group(3) : ", matchObj.group(3)
                    # print "matchObj.group(4) : ", matchObj.group(4)
                    # print "matchObj.group(5) : ", matchObj.group(5)
                    # print "matchObj.group(6) : ", matchObj.group(6)

                    slideNumbersNames[int(matchObj.group(5))-1] = frameNameQuote().cmnd(
                        interactive=False,
                        argsList=[matchObj.group(2)]
                    )
                else:
                    icm.TM_here("No match!!")

        if interactive:
            icm.ANN_note(slideNumbersNames)

        return slideNumbersNames

    def cmndDesc(): """
** Given the pdfFileName,  determine total number of slides, then for each slide determine frameName.

    Returns slideNumbersNames -- where index of slideNumber points to frameName.
    Make sure basePdf.snm and basePdf.nav are available.
"""

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "beamerExternalTagsUpdateAsFPs" :comment "$1 is .ttytex -- extractes from tex and uses impressiveFrameParSet()" :parsMand "" :parsOpt "dispositionBase" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /beamerExternalTagsUpdateAsFPs/ =$1 is .ttytex -- extractes from tex and uses impressiveFrameParSet()= parsMand= parsOpt=dispositionBase argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class beamerExternalTagsUpdateAsFPs(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        opOutcome = latexSup.latexInputFilesList().cmnd(
            interactive=False,
            argsList=effectiveArgsList,
        )

        if opOutcome.isProblematic():
            return(icm.EH_badOutcome(opOutcome))

        filesList = opOutcome.results

        thisOutcome = icm.OpOutcome(invokerName=G.icmMyFullName())

        #
        # Example Lines:
        # %BxPy: impressiveFrameParSet('JoiningByStar--IndividuallyAndEn-Mass', 'always', 'True')
        # %BxPy: impressiveFrameParSet('JoiningByStar--IndividuallyAndEn-Mass', 'transition', 'UnSpecified')
        #
        thisOutcome = icm.subProc_bash(
            """egrep '^%BxPy:' {filesList} | cut -d ':' -f 3 | sed -e 's/^[ ]*//'"""
            .format(filesList=" ".join(filesList)),
            stdin=None, outcome=thisOutcome,
        )#.out()
        
        if thisOutcome.isProblematic():
            return(icm.EH_badOutcome(thisOutcome))

        for each in thisOutcome.stdout.splitlines():
            # Evals lines like this, resulting into ./disposition.gened/xx updates
            # impressiveFrameParSet('titlePage', 'always', 'True')
            #
            icm.evalStringInMain(each)

        return thisOutcome

    def cmndDocStr(self): return """
** Look in input files for ExternalTags as '^%BxPy:' and update them in the disposition.gened  [[elisp:(org-cycle)][| ]]
"""

    
####+BEGIN: bx:icm:python:section :title "Disposition Base Setup -- Main Usage Cmnds"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Disposition Base Setup -- Main Usage Cmnds*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
    

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "updateDispositionBase" :comment "Full update dispositionBase" :parsMand "" :parsOpt "dispositionBase" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /updateDispositionBase/ =Full update dispositionBase= parsMand= parsOpt=dispositionBase argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class updateDispositionBase(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        inPdf = effectiveArgsList[0]

        latexSrcToDispositionUpdate().cmnd(
            interactive=False,
            dispositionBase=dispositionBase,
            argsList=[inPdf,],
        )

        fileName, fileExtension = os.path.splitext(inPdf)
        ttytexFileName = fileName + ".ttytex"

        beamerExternalTagsUpdateAsFPs().cmnd(
            interactive=False,
            dispositionBase=dispositionBase,
            argsList=[ttytexFileName,],
        )

        return

    def cmndDesc(): """
** Given a purpose (voiceOver, presentation, etc) create an info file based on purposesList.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "dispositionFrameNamesList" :comment "" :parsMand "" :parsOpt "framesRange dispositionBase" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /dispositionFrameNamesList/ parsMand= parsOpt=framesRange dispositionBase argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class dispositionFrameNamesList(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'framesRange', 'dispositionBase', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        framesRange=None,         # or Cmnd-Input
        dispositionBase=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'framesRange': framesRange, 'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        framesRange = callParamsDict['framesRange']
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        thisParamBase = icm.FILE_ParamBase(fileSysPath=dispositionBase)

        thisParamBaseState = thisParamBase.baseValidityPredicate()

        if thisParamBaseState != 'InPlace':
            return icm.EH_critical_oops('thisParamBaseState=' + thisParamBaseState)


        filesList = os.listdir(dispositionBase)  # This is instead of sorting

        #print(filesList)

        if framesRange:
            selectedFrameNu = int(framesRange)

        i = 0
        while True:
            i = i + 1
            this = format("slide" + str(i))       
            if this not in filesList:
                icm.TM_here('Missing' + this)
                break           

            frameFileParam = icm.FILE_Param()
            frameFileParam = frameFileParam.readFrom(storeBase=dispositionBase, parName=this)

            if frameFileParam == None:
                return icm.EH_critical_usageError('frameFileParam')

            thisLabeled = frameFileParam.parValueGet()
            # thisLabeledBase = os.path.join(dispositionBase, thisLabeled)
            
            if interactive:
                #icm.ANN_write("{slideNumber} {frameName}".format(
                #    slideNumber=i, frameName=thisLabeled,)
                #)
                icm.ANN_write("{frameName}".format(
                    frameName=thisLabeled,)
                )

            if not interactive:
                icm.EH_critical_usageErro("Not expected to be used non-interactivly. Use frameNamesGet directly.")

        return

    def cmndDesc(): """
**  [[elisp:(org-cycle)][| ]] Given a purpose (voiceOver, presentation, recorderEach) or a combination, create an info file based on purposesList.

For each slide impressiveInfoItemXX(purposesList), is called.
In each, based on puposesList and content of dispositionBase corresponing to that slide,
translate  dispositionBase info into impressive parameters and write them to stdout.

"""
    
    
    
####+BEGIN: bx:icm:python:section :title "Impressive Configurations Based On DispositionBase"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Impressive Configurations Based On DispositionBase*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
    
    

####+BEGIN: bx:icm:python:func :funcName "impressiveTransitionValue" :comment "map disposition to impressive" :funcType "filter" :retType "str" :deco "" :argsList "transitionValue"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-filter    :: /impressiveTransitionValue/ =map disposition to impressive= retType=str argsList=(transitionValue)  [[elisp:(org-cycle)][| ]]
"""
def impressiveTransitionValue(
    transitionValue,
):
####+END:
    """Map dispositionBase transitionValue into impressiveTransitionValue.

You can get a listof impressiveTransitions from 'impressive -l'
"""
    if transitionValue == "default":
        return 'PagePeel'
    elif transitionValue == "UnSpecified":
        return 'SlideUp'
    else:
        return transitionValue

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "dispositionToImpressiveInfoPurposedStdout" :comment "args are purposes (voiceOver, etc)" :parsMand "" :parsOpt "framesRange dispositionBase" :argsMin "1" :argsMax "1000" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /dispositionToImpressiveInfoPurposedStdout/ =args are purposes (voiceOver, etc)= parsMand= parsOpt=framesRange dispositionBase argsMin=1 argsMax=1000 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class dispositionToImpressiveInfoPurposedStdout(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'framesRange', 'dispositionBase', ]
    cmndArgsLen = {'Min': 1, 'Max': 1000,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        framesRange=None,         # or Cmnd-Input
        dispositionBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'framesRange': framesRange, 'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        framesRange = callParamsDict['framesRange']
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        purposesList = []
        for thisArg in effectiveArgsList:
            purposesList.append(thisArg)

        thisParamBase = icm.FILE_ParamBase(fileSysPath=dispositionBase)

        thisParamBaseState = thisParamBase.baseValidityPredicate()

        if thisParamBaseState != 'InPlace':
            return icm.EH_critical_oops('thisParamBaseState=' + thisParamBaseState)

        def impressiveInfoHeadStdout(purposesList):
            """ Considering  purposesList, output the head part of impressiveInfo """
            if 'presenter' in purposesList:
                path = os.path.dirname(dispositionBase)
                if path == None:
                    path = path + '/'

                sys.stdout.write(
                    dispositionToPresenterStdout().impressiveInfoHeadStr(path)
                )

            if 'voiceOver' in purposesList:
                pass

            if 'recorderEach' in purposesList:
                sys.stdout.write(
                    dispositionToImpressiveStdout_recorderEach().impressiveInfoHeadStr()
                )

            if 'recorderOnce' in purposesList:
                sys.stdout.write(
                    dispositionToImpressiveStdout_recorderEach().impressiveInfoHeadStr()
                )
                
        def impressivePagePropsBeginStdout():
            """ Just write out the beginning of PageProps."""

            sys.stdout.write("""

PageProps = {
            """)
            
        impressiveInfoHeadStdout(purposesList)

        impressivePagePropsBeginStdout()        

        filesList = os.listdir(dispositionBase)  # This is instead of sorting

        #print(filesList)

        if framesRange:
            selectedFrameNu = int(framesRange)

        i = 0
        while True:
            i = i + 1
            this = format("slide" + str(i))       
            if this not in filesList:
                icm.TM_here('Missing' + this)
                break           

            frameFileParam = icm.FILE_Param()
            frameFileParam = frameFileParam.readFrom(storeBase=dispositionBase, parName=this)

            if frameFileParam == None:
                return icm.EH_critical_usageError('frameFileParam')

            thisLabeled = frameFileParam.parValueGet()
            thisLabeledBase = os.path.join(dispositionBase, thisLabeled)

            def impressiveInfoItemAudio(purposesList):
                if not 'voiceOver' in purposesList:
                    return

                if framesRange:
                    if i == selectedFrameNu:
                        filePar = icm.FILE_Param()
                        filePar = filePar.readFrom(storeBase=thisLabeledBase, parName='audio')
                        if filePar == None:
                            return #icm.EH_critical_usageError('')

                        else:
                            audioValue = filePar.parValueGet()
                            sys.stdout.write("""
              'sound': """+'"'+audioValue+'"'+""",""")

                        return
                    
                    elif i == (selectedFrameNu + 1):
                        sys.stdout.write("""
              'sound': """+'"/libre/ByStar/InitialTemplates/audio/common/silence1Sec.wav"'+""",""")
                        return

                    else:
                        return

                if thisLabeled == 'recorderStopResume':
                    sys.stdout.write("""
              'sound': """+'"/libre/ByStar/InitialTemplates/audio/common/silence1Sec.wav"'+""",""")
                    return

                if thisLabeled == 'recorderFinishStart':
                    sys.stdout.write("""
              'sound': """+'"/libre/ByStar/InitialTemplates/audio/common/silence1Sec.wav"'+""",""")
                    return

                filePar = icm.FILE_Param()
                filePar = filePar.readFrom(storeBase=thisLabeledBase, parName='audio')
                if filePar == None:
                    return #icm.EH_critical_usageError('')

                else:
                    audioValue = filePar.parValueGet()
                    sys.stdout.write("""
              'sound': """+'"'+audioValue+'"'+""",""")

            def impressiveInfoItemTimeout(purposesList):
                if not 'voiceOver' in purposesList:
                    return

                if framesRange:
                    if i == selectedFrameNu:
                        pass
                    
                    elif i == (selectedFrameNu + 1):
                        sys.stdout.write("""
              'timeout': """+'1000'+""",""")
                        return

                    else:
                        return
                    

                if thisLabeled == 'recorderStopResume':
                    sys.stdout.write("""
              'timeout': """+'99999000'+""",""")
                    return

                if thisLabeled == 'recorderFinishStart':
                    sys.stdout.write("""
              'timeout': """+'99999000'+""",""")
                    return


                filePar = icm.FILE_Param()
                filePar = filePar.readFrom(storeBase=thisLabeledBase, parName='audio')
                if filePar == None:
                    return #icm.EH_critical_usageError('')
                audioValue = filePar.parValueGet()

                audioSansSuffix = os.path.splitext(audioValue)[0]

                audioLengthFP=audioSansSuffix+".length"

                try:
                    fileParam = icm.FILE_ParamReadFromPath(parRoot=audioLengthFP)
                except IOError:
                    icm.TM_here("Missing:  " + audioLengthFP)
                    return(None)

                audioLen=fileParam.parValueGet()
                sys.stdout.write("""
              'timeout': """ + audioLen + """,""")

            def impressiveInfoItemAlways(purposesList):

                filePar = icm.FILE_Param()
                filePar = filePar.readFrom(storeBase=thisLabeledBase, parName='always')
                if filePar == None:
                    return #icm.EH_critical_usageError('')
                thisValue = filePar.parValueGet()
                sys.stdout.write("""
              'always': """ + thisValue + """,""")

            def impressiveInfoItemTransition(purposesList):
                filePar = icm.FILE_Param()
                filePar = filePar.readFrom(storeBase=thisLabeledBase, parName='transition')
                if filePar == None:
                    return #icm.EH_critical_usageError('')
                transitionValue = filePar.parValueGet()
                transitionValue = impressiveTransitionValue(transitionValue)
                sys.stdout.write("""
              'transition': """+transitionValue+""",""")

            def impressiveInfoItemOverview(purposesList):
                filePar = icm.FILE_Param()
                filePar = filePar.readFrom(storeBase=thisLabeledBase, parName='overview')
                if filePar == None:
                    return icm.EH_critical_usageError('')
                overviewValue = filePar.parValueGet()
                sys.stdout.write("""
              'overview': """+overviewValue+""",""")

            def impressiveInfoItemNotes(purposesList):
                filePar = icm.FILE_Param()
                filePar = filePar.readFrom(storeBase=thisLabeledBase, parName='notes')
                if filePar == None:
                    return icm.EH_critical_usageError('')
                notesValue = filePar.parValueGet()
                sys.stdout.write("""
              'notes': """+notesValue+""",""")

            def impressiveInfoItemExtra(purposesList):
                if 'presenter' in purposesList:
                    sys.stdout.write("""
              'OnEnter': UpdateInfo,""")

            def impressiveInfoItemOnEnter(purposesList):

                if framesRange:
                    if i == selectedFrameNu:
                        if 'recorderEach' in purposesList:
                            sys.stdout.write("""
              'OnEnter': bxVideoRecorderStart,""")
                            return
                        
                    elif i == (selectedFrameNu + 1):
                        if 'recorderEach' in purposesList:
                            sys.stdout.write("""
              'OnEnter': bxVideoRecorderStop,""")
                            return
                    else:
                        return

                if 'recorderEach' in purposesList:
                            sys.stdout.write("""
              'OnEnter': bxVideoRecorderStart,""")
                            return

                if 'recorderOnce' in purposesList:
                            sys.stdout.write("""
              'OnEnter': bxVideoRecorderOnceStart,""")
                            return
                    
                if 'recorderStopResume' == thisLabeled:
                    sys.stdout.write("""
              'OnEnter': vlcRecordStop,""")
                    return
                if 'recorderFinishStart' == thisLabeled:
                    sys.stdout.write("""
              'OnEnter': vlcRecordFinish,""")
                    return

            def impressiveInfoItemOnLeave(purposesList):

                if framesRange:
                    return
                    
                if 'recorderEach' in purposesList:
                    sys.stdout.write("""
              'OnLeave': bxVideoRecorderStop,""")
                    return

                if 'recorderOnce' in purposesList:
                    sys.stdout.write("""
              'OnLeave': bxVideoRecorderOnceStop,""")
                    return
                
                if 'recorderStopResume' == thisLabeled:
                    sys.stdout.write("""
              'OnLeave': vlcRecordResume,""")
                    return
                if 'recorderFinishStart' == thisLabeled:
                    sys.stdout.write("""
              'OnLeave': vlcRecordStart,""")
                    return
                filePar = icm.FILE_Param()
                filePar = filePar.readFrom(storeBase=thisLabeledBase, parName='OnLeave')
                if filePar == None:
                    return #icm.EH_critical_usageError('')
                thisValue = filePar.parValueGet()
                sys.stdout.write("""
              'OnLeave': """ + thisValue + """,""")

            def impressiveInfoItemHead(purposesList):            
                #if 'presenter' in purposesList:
        #         sys.stdout.write("""
        # """+str(i)+""": {""")

                  sys.stdout.write("""
        # frameName={frameName}
        {frameNumber}: {{""".format(frameName=thisLabeled, frameNumber=i))

            def impressiveInfoItemTail(purposesList):            
                #if 'presenter' in purposesList:
                sys.stdout.write("""
        },""")

            impressiveInfoItemHead(purposesList)
            impressiveInfoItemAudio(purposesList)
            impressiveInfoItemTimeout(purposesList)
            impressiveInfoItemAlways(purposesList)                
            impressiveInfoItemTransition(purposesList)
            #impressiveInfoItemOverview(purposesList)
            #impressiveInfoItemNotes(purposesList)                                
            impressiveInfoItemExtra(purposesList)
            impressiveInfoItemOnEnter(purposesList)
            impressiveInfoItemOnLeave(purposesList)               
            impressiveInfoItemTail(purposesList)


        # End Of The While True Statement
        # Output the Tail now.

        def impressiveInfoTailStdout(purposesList):
            #if 'presenter' in purposesList:
            sys.stdout.write("""
}\n\n"""
            )
        impressiveInfoTailStdout(purposesList)

        return

    def cmndDesc(): """
**  [[elisp:(org-cycle)][| ]] Given a purpose (voiceOver, presentation, recorderEach) or a combination, create an info file based on purposesList.

For each slide impressiveInfoItemXX(purposesList), is called.
In each, based on puposesList and content of dispositionBase corresponing to that slide,
translate  dispositionBase info into impressive parameters and write them to stdout.

"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "dispositionToPresenterStdout" :comment "No longer used" :parsMand "" :parsOpt "dispositionBase" :argsMin "1" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /dispositionToPresenterStdout/ =No longer used= parsMand= parsOpt=dispositionBase argsMin=1 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class dispositionToPresenterStdout(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        filename = effectiveArgsList[0]

        document = PdfFileReader(file(filename, "rb"))
        pages = document.getNumPages()
        icm.TM_here()

        with open(filename+".info", 'w') as out:
            path = os.path.dirname(filename)
            icm.TM_here(str(path))

            if path == None:
                return icm.EH_critical_usageError('')

            icm.TM_here()
            path = path + '/'

            out.write(
                self.impressiveInfoHeadStr(path)
            )
            
            out.write("""
                PageProps = {
                """)

            for i in range(1,pages + 1):
                if i < pages:
                    out.write("    "+str(i)+": {\n        'transition': None,\n        'overview': True,\n        'notes': '',\n        'OnEnter': UpdateInfo\n    },\n")
                else:
                    out.write("    "+str(i)+": {\n        'transition': None,\n        'overview': True,\n        'notes': '',\n        'OnEnter': UpdateInfo\n    }\n}")

    def impressiveInfoHeadStr(self,
                             path,
    ):
        return """\
import json


    def UpdateInfo():
        global FileName, FileList, PageCount
        global DocumentTitle
        global Pcurrent, Pnext, Tcurrent, Tnext, InitialPage
        global RTrunning, RTrestart, StartTime, PageEnterTime, CurrentTime

        with open('"""+path+"""json.txt', 'w') as io:
            json.dump(({"page_count": PageCount, "current_page": Pcurrent, "previous_page": Pnext, "start_time": StartTime, "pageenter_time": PageEnterTime, "current_time": CurrentTime, "notes": PageProps[Pcurrent]['notes']}), io)

"""
                    
    def cmndDesc(): """
** No longer used -- Creates  meta info for Presenter -- To be tested or deleted.
"""

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "dispositionToImpressiveStdout_voiceOver_Obsoleted" :comment "" :parsMand "" :parsOpt "dispositionBase" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /dispositionToImpressiveStdout_voiceOver_Obsoleted/ parsMand= parsOpt=dispositionBase argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class dispositionToImpressiveStdout_voiceOver_Obsoleted(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        if not dispositionBase:
           dispositionBase = './disposition.gened'

        thisParamBase = icm.FILE_ParamBase(fileSysPath=dispositionBase)

        thisParamBaseState = thisParamBase.baseValidityPredicate()

        if thisParamBaseState != 'InPlace':
            return icm.EH_critical_oops('thisParamBaseState=' + thisParamBaseState)

        sys.stdout.write(
            self.impressiveInfoHeadStr()
        )

                    
    def cmndDesc(): """
** Map dispositionBase into ImpressiveInfo for voiceOver purposes.
"""

    def impressiveInfoHeadStr(self,
    ):
        """
** Returns a string for impressive.info header for recording purposes.
"""
        return """\

    import shlex
    import subprocess

    def vlcRecordStop():
        commandLine="/opt/public/osmt/bin/bx-vlcRecScreen -i rcRecordStop"
        commandArgs=shlex.split(commandLine)

        print("executing {commandLine}".format(commandLine=commandLine))

        p = subprocess.Popen(commandArgs,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

        out, err = p.communicate()

        if out: print("Stdout:" +  out)
        if err: print("Stderr:" +  err)

    def vlcRecordResume():
        commandLine="/opt/public/osmt/bin/bx-vlcRecScreen -i rcRecordResume"
        commandArgs=shlex.split(commandLine)

        print("executing {commandLine}".format(commandLine=commandLine))

        p = subprocess.Popen(commandArgs,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

        out, err = p.communicate()

        if out: print("Stdout:" +  out)
        if err: print("Stderr:" +  err)


    def vlcRecordFinish():
        commandLine="/opt/public/osmt/bin/bx-vlcRecScreen -i rcRecordShutdown"
        commandArgs=shlex.split(commandLine)

        print("executing {commandLine}".format(commandLine=commandLine))

        p = subprocess.Popen(commandArgs,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

        out, err = p.communicate()

        if out: print("Stdout:" +  out)
        if err: print("Stderr:" +  err)

    def vlcRecordStart():
        commandLine="/opt/public/osmt/bin/bx-vlcRecScreen -h -v -n showRun -p locSize=topLeft720 -i  recordStart"
        commandArgs=shlex.split(commandLine)

        print("executing {commandLine}".format(commandLine=commandLine))

        p = subprocess.Popen(commandArgs,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

        #out, err = p.communicate()

        #if out: print("Stdout:" +  out)
        #if err: print("Stderr:" +  err)
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "dispositionToImpressiveStdout_recorderEach" :comment "" :parsMand "" :parsOpt "dispositionBase" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /dispositionToImpressiveStdout_recorderEach/ parsMand= parsOpt=dispositionBase argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class dispositionToImpressiveStdout_recorderEach(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dispositionBase', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        dispositionBase=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        if not dispositionBase:
           dispositionBase = './disposition.gened'

        thisParamBase = icm.FILE_ParamBase(fileSysPath=dispositionBase)

        thisParamBaseState = thisParamBase.baseValidityPredicate()

        if thisParamBaseState != 'InPlace':
            return icm.EH_critical_oops('thisParamBaseState=' + thisParamBaseState)

        sys.stdout.write(
            self.impressiveInfoHeadStr()
        )
                    
    def cmndDesc(): """
** Map dispositionBase into ImpressiveInfo for voiceOver purposes.
"""
        

    def impressiveInfoHeadStr(self,
    ):
        """
** Returns a string for impressive.info header for recording purposes.
"""
        return """\

from unisos import icm
from bisos.lcnt import impressiveSup

icm.libUserInit("-v 20")

def bxVideoRecorderStart():
    global FileName, FileList, PageCount
    global DocumentTitle
    global Pcurrent, Pnext, Tcurrent, Tnext, InitialPage
    global RTrunning, RTrestart, StartTime, PageEnterTime, CurrentTime

    impressiveSup.bxVideoRecorderStart(
        curPage=Pcurrent,
    )

def bxVideoRecorderStop():
    global FileName, FileList, PageCount
    global DocumentTitle
    global Pcurrent, Pnext, Tcurrent, Tnext, InitialPage
    global RTrunning, RTrestart, StartTime, PageEnterTime, CurrentTime

    impressiveSup.bxVideoRecorderStop(
        curPage=Pcurrent,
    )

def bxVideoRecorderOnceStart():
    global Pcurrent

    impressiveSup.bxVideoRecorderOnceStart(
        curPage=Pcurrent,
    )

def bxVideoRecorderOnceStop():
    global Pcurrent

    impressiveSup.bxVideoRecorderOnceStop(
        curPage=Pcurrent,
    )

"""
    

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "updateThenImpressiveInfoStdout" :comment "Full update then ImpressiveInfoStdout" :parsMand "inPdf" :parsOpt "framesRange dispositionBase" :argsMin "1" :argsMax "1000" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /updateThenImpressiveInfoStdout/ =Full update then ImpressiveInfoStdout= parsMand=inPdf parsOpt=framesRange dispositionBase argsMin=1 argsMax=1000 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class updateThenImpressiveInfoStdout(icm.Cmnd):
    cmndParamsMandatory = [ 'inPdf', ]
    cmndParamsOptional = [ 'framesRange', 'dispositionBase', ]
    cmndArgsLen = {'Min': 1, 'Max': 1000,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        inPdf=None,         # or Cmnd-Input
        framesRange=None,         # or Cmnd-Input
        dispositionBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'inPdf': inPdf, 'framesRange': framesRange, 'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        inPdf = callParamsDict['inPdf']
        framesRange = callParamsDict['framesRange']
        dispositionBase = callParamsDict['dispositionBase']
####+END:

        dispositionBase = dispositionBaseDefault(dispositionBase)

        updateDispositionBase().cmnd(
            interactive=False,
            dispositionBase=dispositionBase,
            argsList=[inPdf,],
        )

        dispositionToImpressiveInfoPurposedStdout().cmnd(
            interactive=False,
            dispositionBase=dispositionBase,
            framesRange=framesRange,
            argsList=effectiveArgsList,
        )

        return

    def cmndDesc(): """
** Given a purpose (voiceOver, presentation, etc) create an info file based on purposesList.
"""

    
####+BEGIN: bx:icm:python:section :title "Impressive Purposed Preparations And Executions -- Main Usage Cmnds"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Impressive Purposed Preparations And Executions -- Main Usage Cmnds*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "dispositionToImpressivePurposed" :comment "Create Info and run impressive for each" :parsMand "inPdf" :parsOpt "framesRange dispositionBase" :argsMin "1" :argsMax "1000" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /dispositionToImpressivePurposed/ =Create Info and run impressive for each= parsMand=inPdf parsOpt=framesRange dispositionBase argsMin=1 argsMax=1000 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class dispositionToImpressivePurposed(icm.Cmnd):
    cmndParamsMandatory = [ 'inPdf', ]
    cmndParamsOptional = [ 'framesRange', 'dispositionBase', ]
    cmndArgsLen = {'Min': 1, 'Max': 1000,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        inPdf=None,         # or Cmnd-Input
        framesRange=None,         # or Cmnd-Input
        dispositionBase=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'inPdf': inPdf, 'framesRange': framesRange, 'dispositionBase': dispositionBase, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        inPdf = callParamsDict['inPdf']
        framesRange = callParamsDict['framesRange']
        dispositionBase = callParamsDict['dispositionBase']
####+END:
        dispositionBase = dispositionBaseDefault(dispositionBase)

        purposesStr="-".join(effectiveArgsList)
        impressiveInfoPath=os.path.abspath("./tmp/impressive.{}".format(purposesStr))

        ucf.DIR_ensure(impressiveInfoPath)

        purposesList = effectiveArgsList
        
        with open(impressiveInfoPath, 'w') as f:
            with ucf.stdout_redirector(f):
                dispositionToImpressiveInfoPurposedStdout().cmnd(
                    interactive=False,
                    framesRange=framesRange,
                    dispositionBase=dispositionBase,
                    argsList=purposesList,
                )

        if framesRange:
            icm.ANN_write("impressive -i {framesRange} --nologo -Q -k -I {impressiveInfoPath} {inPdf}".
                          format(framesRange=framesRange, impressiveInfoPath=impressiveInfoPath, inPdf=inPdf))
        else:
            if 'recorderOnce' in purposesList:
                icm.ANN_write("impressive -i 1 --nologo -Q -k -I {impressiveInfoPath} {inPdf}".
                          format(impressiveInfoPath=impressiveInfoPath, inPdf=inPdf))
            else:
                icm.ANN_write("impressive --nologo -Q -k -I {impressiveInfoPath} {inPdf}".
                          format(impressiveInfoPath=impressiveInfoPath, inPdf=inPdf))
                
            

    def cmndDesc(): """
** Given a purpose (voiceOver, presentation, etc) create an info file based on purposesList.
"""



####+BEGIN: bx:icm:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""
    
####+BEGIN: bx:icm:python:section :title "Common/Generic Facilities -- Library Candidates"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common/Generic Facilities -- Library Candidates*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    
####+BEGIN: bx:icm:python:section :title "= =Framework::=   G_main -- Instead Of ICM Dispatcher ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::=   G_main -- Instead Of ICM Dispatcher =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:func :funcName "G_main" :funcType "FrameWrk" :retType "Void" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-FrameWrk  :: /G_main/ retType=Void argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def G_main():
####+END:
    """ 
** Replaces ICM dispatcher for other command line args parsings.
"""
    pass

####+BEGIN: bx:icm:python:icmItem :itemType "Configuration" :itemTitle "= =Framework::= g_ Settings -- ICMs Imports ="
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Configuration  :: = =Framework::= g_ Settings -- ICMs Imports =  [[elisp:(org-cycle)][| ]]
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
