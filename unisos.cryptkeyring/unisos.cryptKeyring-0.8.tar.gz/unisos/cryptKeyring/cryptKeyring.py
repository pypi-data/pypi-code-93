# -*- coding: utf-8 -*-
"""\
* TODO *[Summary]* ::  A /library/ for policy based encryption and decryption.
"""

####+BEGIN: bx:icm:python:top-of-file :control "NOTYET" :partof "none" :copyleft "none"
"""
*  This file:/bisos/git/auth/bxRepos/unisos/bin/py/cryptKeyring.py :: [[elisp:(org-cycle)][| ]]

 A Python Interactively Command Module (PyICM).
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 *WARNING*: All edits wityhin Dynamic Blocks may be lost.
"""
####+END:


"""
*  [[elisp:(org-cycle)][| *Lib-Module-INFO:* |]] :: Author, Copyleft and Version Information
"""

####+BEGIN: bx:global:lib:name-py :style "fileName"
__libName__ = "cryptoKeyring"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201908274150"
####+END:

####+BEGIN: bx:global:icm:status-py :status "Initial"
__status__ = "Initial"
####+END:

__credits__ = [""]

####+BEGINNOT: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/icmInfo-mbNedaGpl.py"
icmInfo = {
    'authors':         ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"],
    'licenses':        ["[[https://www.gnu.org/licenses/agpl-3.0.en.html][Affero GPL]]", "Libre-Halaal Services License", "Neda Commercial License"],
    'maintainers':     ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]",],
    'contacts':        ["[[http://mohsen.1.banan.byname.net/contact]]",],
}
####+END:

####+BEGIN: bx:icm:python:topControls 
"""
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
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
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ContentsList*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:dblock:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  =Imports=      :: *IMPORTS*  [[elisp:(org-cycle)][| ]]
"""
####+END:

import os
import collections
import enum

####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/importUcfIcmG.py"
from unisos import ucf
from unisos import icm

icm.unusedSuppressForEval(ucf.__file__)  # in case icm and ucf are not used

G = icm.IcmGlobalContext()
G.icmLibsAppend = __file__
G.icmCmndsLibsAppend = __file__

####+END:

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import binascii
import base64

import json
import keyring
import getpass

#from cryptography.hazmat.primitives.ciphers.aead import AESGCM
#import binascii
import os
import errno

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

import pickle

from unisos.symCrypt import symCrypt

####+BEGIN: bx:dblock:python:section :title "Library Description (Overview)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Library Description (Overview)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "icmBegin_libOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /icmBegin_libOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class icmBegin_libOverview(icm.Cmnd):
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
 
####+BEGIN: bx:dblock:python:section :title "Start Your Sections Here"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Start Your Sections Here*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:dblock:python:section :title "Common Command Parameter Specification"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Command Parameter Specification*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:func :funcName "commonParamsSpecify" :funcType "void" :retType "bool" :deco "" :argsList "icmParams"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-void      :: /commonParamsSpecify/ retType=bool argsList=(icmParams)  [[elisp:(org-cycle)][| ]]
"""
def commonParamsSpecify(
    icmParams,
):
####+END:

    icmParams.parDictAdd(
        parName='rsrc',
        parDescription="Resource",
        parDataType=None,
        parDefault=None,
        parChoices=["someResource", "UserInput"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--rsrc',
        )
    

    icmParams.parDictAdd(
        parName='cryptoPolicy',
        parDescription="Encryption Policy",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--cryptoPolicy',
        )

    icmParams.parDictAdd(
        parName='passwdPolicy',
        parDescription="Policy For Setting Passwd In Keyring",
        parDataType=None,
        parDefault=None,
        parChoices=['prompt', 'default',],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--passwdPolicy',
        )

    icmParams.parDictAdd(
        parName='system',
        parDescription="System Name",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--system',
        )
    
    icmParams.parDictAdd(
        parName='user',
        parDescription="User Name",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--user',
        )

    icmParams.parDictAdd(
        parName='passwd',
        parDescription="Pass Word",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--passwd',
        )
     


####+BEGIN: bx:dblock:python:section :title "Common Command Examples Sections"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Command Examples Sections*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:func :funcName "examples_libModuleCmnds" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "keyring=None system=None user=None"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-anyOrNone :: /examples_libModuleCmnds/ retType=bool argsList=(keyring=None system=None user=None)  [[elisp:(org-cycle)][| ]]
"""
def examples_libModuleCmnds(
    keyring=None,
    system=None,
    user=None,
):
####+END:
    """
** Auxiliary examples to be commonly used.x2
"""
    def cpsInit(): return collections.OrderedDict()
    def menuItemVerbose(): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    def menuItemTerse(): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='none')            
    def menuItem(verbosity): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity)            
    def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

    if not keyring:
        keyring="keyring"

    if not system:
        system="sysEx1"
        
    if not user:
        user="userEx1"
        
    rsrcPath = """{keyring}/{system}/{user}""".format(keyring=keyring, system=system, user=user)        

####+BEGIN: bx:icm:python:cmnd:subSection :context "func-1" :title "Prepare Crypto Keyring"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Prepare Crypto Keyring*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    icm.cmndExampleMenuChapter('*Prepare Crypto Keyring*')

    cmndName = "prepare"

    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = 'keyring'
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='none', comment="# One time initialization")
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='full')                        
    thisBlock()


####+BEGIN: bx:icm:python:cmnd:subSection :context "func-1" :title "Set Password In Crypto Keyring"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Set Password In Crypto Keyring*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    icm.cmndExampleMenuChapter('*Set Password In Crypto Keyring*')

    cmndName = "cryptPasswdSet"
    
    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = rsrcPath;  cps['passwdPolicy'] = 'prompt'
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='none')
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='full')                        
    thisBlock()
    

    def thisBlock():
        cmndArgs = "somePasswd";
        cps = cpsInit();  cps['rsrc'] = rsrcPath; 
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock()

    

####+BEGIN: bx:icm:python:cmnd:subSection :context "func-1" :context "func-1" :title "Get Password From Crypto Keyring (Decrypted)"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Get Password From Crypto Keyring*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    icm.cmndExampleMenuChapter('*Get Password From Crypto Keyring (Decrypted)*')

    cmndName = "clearPasswdGet"
    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = rsrcPath
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock()

    
####+BEGIN: bx:icm:python:cmnd:subSection :context "func-1" :context "func-1" :title "Get Password From Keyring (Encrypted)"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Get Password From Crypto Keyring*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    icm.cmndExampleMenuChapter('*Get Password From Keyring (Encrypted)*')

    cmndName = "keyringPasswdGet"
    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = rsrcPath
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock()



####+BEGIN: bx:icm:python:cmnd:subSection :context "func-1" :context "func-1" :title "Delete Password From Crypto Keyring"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Delete Password From Crypto Keyring*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    icm.cmndExampleMenuChapter('*Delete Password From Crypto Keyring*')

    cmndName = "passwdDelete"

    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = rsrcPath
        icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock()
    
        
####+BEGIN: bx:icm:python:cmnd:subSection :context "func-1" :title "Remain In Sycn With Template"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Remain In Sycn With Template*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
        
    def thisBlock():
        icm.cmndExampleMenuChapter('*Remain In Sycn With Template*')

        templateFile = "/bisos/git/bxRepos/bisos-pip/examples/dev/bisos/examples/icmLibPkgBegin.py"
        thisFile = __file__

        execLineEx("""diff {thisFile} {templateFile}""".format(thisFile=thisFile, templateFile=templateFile))
        execLineEx("""cp {thisFile} {templateFile}""".format(thisFile=thisFile, templateFile=templateFile))
        execLineEx("""cp {templateFile} {thisFile}""".format(thisFile=thisFile, templateFile=templateFile))                
    #thisBlock()

    return


####+BEGIN: bx:dblock:python:section :title "Lib Module Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Lib Module Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:



####+BEGIN: bx:icm:python:section :title "ICM-Commands: CryptPasswd Prepare"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: CryptPasswd Prepare*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "prepare" :comment "" :parsMand "rsrc" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /prepare/ parsMand=rsrc parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class prepare(icm.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        rsrc=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'rsrc': rsrc, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        rsrc = callParamsDict['rsrc']

####+END:
        opError=icm.OpError.Success

        rsrcPath = os.path.normpath(rsrc)
        rsrcParts = rsrcPath.split(os.sep)

        rsrcBase = rsrcParts[0]
        
        cryptoKeyring = CryptoKeyring()

        opError = cryptoKeyring.prepare()

        return cmndOutcome.set(
            opError=opError,
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

####+BEGIN: bx:icm:python:section :title "ICM-Commands: CryptPasswd Set"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: CryptPasswd Set*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "cryptPasswdSet" :comment "" :parsMand "rsrc" :parsOpt "passwdPolicy" :argsMin "0" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /cryptPasswdSet/ parsMand=rsrc parsOpt=passwdPolicy argsMin=0 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class cryptPasswdSet(icm.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ 'passwdPolicy', ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        rsrc=None,         # or Cmnd-Input
        passwdPolicy=None,         # or Cmnd-Input
        argsList=[],         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'rsrc': rsrc, 'passwdPolicy': passwdPolicy, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        rsrc = callParamsDict['rsrc']
        passwdPolicy = callParamsDict['passwdPolicy']

        cmndArgsSpecDict = self.cmndArgsSpec()
        if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
            return cmndOutcome
####+END:
        opError=icm.OpError.Success

        rsrcPath = os.path.normpath(rsrc)
        rsrcParts = rsrcPath.split(os.sep)

        rsrcBase = rsrcParts[0]
        system = rsrcParts[1]
        user = rsrcParts[2]                

        
        passwd=None
        
        cmndArgs = self.cmndArgsGet("0&1", cmndArgsSpecDict, effectiveArgsList)
        for each in cmndArgs:
            passwd = each                      

        if not passwd:
            
            if not passwdPolicy:
                passwd = "clear"
            elif passwdPolicy == "prompt":
                # Prompt for password
                passwd = getpass.getpass()
            else:
                return (
                    icm.EH_problem_usageError("Bad passwdPolicy={}".passwdPolicy)
                )

            
        
        cryptoKeyring = CryptoKeyring(
            system=system,
            user=user,
        )

        cryptedPasswd = cryptoKeyring.passwdSet(passwd)

        if interactive:
            print(("cryptedPasswd={}".format(cryptedPasswd)))

        return cmndOutcome.set(
            opError=opError,
            opResults=cryptedPasswd,
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
            argPosition="0&1",
            argName="passwd",
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


####+BEGIN: bx:icm:python:section :title "ICM-Commands: CryptPasswd Get"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: CryptPasswd Get*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "clearPasswdGet" :comment "" :parsMand "rsrc" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /clearPasswdGet/ parsMand=rsrc parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class clearPasswdGet(icm.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        rsrc=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'rsrc': rsrc, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        rsrc = callParamsDict['rsrc']

####+END:
        opError=icm.OpError.Success

        rsrcPath = os.path.normpath(rsrc)
        rsrcParts = rsrcPath.split(os.sep)
        
        rsrcBase = rsrcParts[0]
        system = rsrcParts[1]
        user = rsrcParts[2]                

        cryptoKeyring = CryptoKeyring(
            system=system,
            user=user,
        )

        clearPasswd = cryptoKeyring.passwdGet()

        if interactive:        
            print(clearPasswd)

        return cmndOutcome.set(
            opError=opError,
            opResults=clearPasswd,
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



####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "keyringPasswdGet" :comment "" :parsMand "rsrc" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /keyringPasswdGet/ parsMand=rsrc parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class keyringPasswdGet(icm.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        rsrc=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'rsrc': rsrc, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        rsrc = callParamsDict['rsrc']

####+END:
        opError=icm.OpError.Success

        rsrcPath = os.path.normpath(rsrc)
        rsrcParts = rsrcPath.split(os.sep)

        rsrcBase = rsrcParts[0]
        system = rsrcParts[1]
        user = rsrcParts[2]                

        keyringPasswd = keyring.get_password(system, user)

        if interactive:
            if keyringPasswd:
                print(keyringPasswd)
            else:
                print(("No Passwd Found For: system={system} user={user}".format(system=system, user=user)))

        return cmndOutcome.set(
            opError=opError,
            opResults=keyringPasswd,
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



####+BEGIN: bx:icm:python:section :title "ICM-Commands: CryptPasswd Delete"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: CryptPasswd Get*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "passwdDelete" :comment "" :parsMand "rsrc system user" :parsOpt "passwdPolicy cryptoPolicy" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  ICM-Cmnd       :: /passwdDelete/ parsMand=rsrc system user parsOpt=passwdPolicy cryptoPolicy argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class passwdDelete(icm.Cmnd):
    cmndParamsMandatory = [ 'rsrc', 'system', 'user', ]
    cmndParamsOptional = [ 'passwdPolicy', 'cryptoPolicy', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        rsrc=None,         # or Cmnd-Input
        system=None,         # or Cmnd-Input
        user=None,         # or Cmnd-Input
        passwdPolicy=None,         # or Cmnd-Input
        cryptoPolicy=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'rsrc': rsrc, 'system': system, 'user': user, 'passwdPolicy': passwdPolicy, 'cryptoPolicy': cryptoPolicy, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        rsrc = callParamsDict['rsrc']
        system = callParamsDict['system']
        user = callParamsDict['user']
        passwdPolicy = callParamsDict['passwdPolicy']
        cryptoPolicy = callParamsDict['cryptoPolicy']

####+END:
        opError=icm.OpError.Success

        
        cryptoKeyring = CryptoKeyring(
            system=system,
            user=user,
        )

        opError = cryptoKeyring.passwdSet()

        #cryptoKeyring.save()        

        return cmndOutcome.set(
            opError=opError,
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


####+BEGIN: bx:icm:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:dblock:python:class :className "CryptoKeyring" :superClass "" :comment "" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Class-basic    :: /CryptoKeyring/ object  [[elisp:(org-cycle)][| ]]
"""
class CryptoKeyring(object):
####+END:
    """ 
    """

    ucryptKeyringBackend = "placeholder"
    ucryptKeyringSystem = "ucrypt"    
    ucryptPolicy = "cryptoKeyring"
    ucryptKeyPasswdPolicy = "prompt"

####+BEGIN: bx:icm:python:method :methodName "__init__" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "system=None user=None"
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /__init__/ retType=bool argsList=(system=None user=None) deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
        self,
        system=None,
        user=None,
    ):
####+END:
        """ 
        system = (string) 
        user = (string)
        """
        
        self.system = system
        self.user = user
        

####+BEGIN: bx:icm:python:method :methodName "load" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /load/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def load(self):
####+END:        
        f = open(self.pickleFile, 'rb')
        tmp_dict = pickle.load(f)
        f.close()          

        self.__dict__.update(tmp_dict) 

####+BEGIN: bx:icm:python:method :methodName "save" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /save/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def save(self):
####+END:        
        f = open(self.pickleFile, 'wb')
        pickle.dump(self.__dict__, f, 2)
        f.close()        


####+BEGIN: bx:icm:python:method :methodName "prepare" :methodType "anyOrNone" :retType "passwd string" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /prepare/ retType=passwd string argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def prepare(self):
####+END:        
        """ create ucrypt policy. 
"""
        outcome = symCrypt.createEncryptionPolicy().cmnd(
            interactive=False,
            rsrc="policy",
            policy=self.__class__.ucryptPolicy,
            keyringPolicy=self.__class__.ucryptKeyPasswdPolicy,
            #argsList=[],
        ).log()
        if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))

        print((outcome.results))



####+BEGIN: bx:icm:python:method :methodName "passwdSet" :methodType "anyOrNone" :retType "passwd string" :deco "default" :argsList "passwd"
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /passwdSet/ retType=passwd string argsList=(passwd) deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def passwdSet(
        self,
        passwd,
    ):
####+END:        
        """ Return passwd string from keyring.
"""

        outcome = symCrypt.encrypt().cmnd(        
            interactive=False,
            rsrc="policy/{}".format(self.__class__.ucryptPolicy),            
            clearText=passwd,
        ).log()
        if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))

        cipheredPasswd = outcome.results

        keyring.set_password(self.system, self.user, cipheredPasswd)        
            
        keyringPasswd = keyring.get_password(self.system, self.user)

        icm.LOG_here(keyringPasswd)
        
        return keyringPasswd

    
####+BEGIN: bx:icm:python:method :methodName "passwdGet" :methodType "anyOrNone" :retType "binary" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /passwdGet/ retType=binary argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def passwdGet(self):
####+END:        
        """ Return passwd."""

        keyringPasswd = keyring.get_password(self.system, self.user)

        if not keyringPasswd:
            return None
        
        outcome = symCrypt.decrypt().cmnd(        
            interactive=False,
            rsrc="policy/{}".format(self.__class__.ucryptPolicy),            
            cipherText=keyringPasswd,
        ).log()
        if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))

        clearPasswd = outcome.results

        icm.LOG_here(clearPasswd)
        
        return clearPasswd


    
####+BEGIN: bx:icm:python:method :methodName "passwdDelete" :methodType "anyOrNone" :retType "binary" :deco "default" :argsList ""
    """
**  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Method-anyOrNone :: /passwdDelete/ retType=binary argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def passwdDelete(self):
####+END:        
        """ Return passwd."""
        return 
    



####+BEGIN: bx:icm:python:section :title "End Of Editable Text"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
