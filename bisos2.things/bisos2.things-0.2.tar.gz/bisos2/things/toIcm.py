# -*- coding: utf-8 -*-
"""\
* TODO *[Summary]* ::  A /library/ of TOICM: Things Oriented Interactive Commands Module.
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/de/bx/nne/dev-py/pypi/pkgs/bisos/things/dev/bisos/things/new-toIcm.py :: [[elisp:(org-cycle)][| ]]
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
__libName__ = "new-toIcm"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201712262308"
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

####+BEGIN: bx:dblock:python:icm:cmnd:classHead :modPrefix "new" :cmndName "bxpBaseDir_LibOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /bxpBaseDir_LibOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class toIcm_LibOverview(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 3,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
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

####+BEGIN: bx:dblock:python:section :title "Topic Section"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Things Abstractions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


"""
*      ======[[elisp:(org-cycle)][Fold]]====== /TARGET_Elem:/ and TARGET_List
"""

class TARGET_Elem(object):
     """Representation of One TARGET_Element.

     A TARGET_Elem is the general representation of a TARGET_Proxy_.

     """
     def __init__(self, targetType=None, base=None, dnType=None, dnQualifier=None):
         '''Constructor'''
         self.__targetType = targetType
         self.__base = base
         self.__dnType = dnType                  
         self.__dnQualifier = dnQualifier
         self.__config = dnQualifier

     def targetType(self):
         """
         """
         return self.__targetType

     def base(self):
         """
         """
         return self.__base

     def dnQualifier(self):
         """
         """
         return self.__dnQualifier

     def dnType(self):
         """
         """
         return self.__dnType
         
     def fileParamsBase(self):
         """
         """
         return format(self.__base + '/' + self.__dnQualifier)

     def fileParamsGet(self):
         """
         """
         fileParamsBase = self.fileParamsBase()
         #params = FILE_parametersRead(fileParamsBase)
         #return params

class TARGET_List(object):
     """Maintain a list of Targets.
     """

     targetList = []

     def __init__(self):
         pass

     def targetAppend(self, target=None):
         """
         """
         self.__class__.targetList.append(target)

     def targetAdd(self, targetType=None, base=None, dnType=None, dnQualifier=None):
         """
         """
         newTarget = TARGET_Elem(targetType=targetType, base=base, dnType=dnType, dnQualifier=dnQualifier)

         self.__class__.targetList.append(newTarget)

     def targetListGet(self):
         """
         """
         return self.__class__.targetList

     def targetFind(self, dnQualifier=None):
         """
         """
         for target in self.__class__.targetList:
             if target.dnQualifier() == dnQualifier:
                 return target


def TARGET_paramsAdd(targetType=None, base=None, dnQualifier=None, param=None):
     """
     If base is ephemera, create a TARGET_Elem, and write it to disk.
     """
     pass

"""
*      ======[[elisp:(org-cycle)][Fold]]====== /Target_Proxy_Linux:/ -- TARGET_Proxy
"""

#
# Some constants.
#
#COMMAND_PROMPT = '[#$] ' ### This is way too simple for industrial use -- we will change is ASAP.
#COMMAND_PROMPT = '^.*[>#]'
COMMAND_PROMPT = '[>#]'
TERMINAL_PROMPT = '(?i)terminal type\?'
TERMINAL_TYPE = 'vt100'
# This is the prompt we get if SSH does not have the remote host's public key stored in the cache.
SSH_NEWKEY = '(?i)are you sure you want to continue connecting'


@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def doSendline(connection, *v, **k):
    """Returns connection.sendline(*v, **k)"""
    return connection.sendline(*v, **k)

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def doExpect(connection, *v, **k):
     return connection.expect(*v, **k)


class TARGET_Proxy_Linux(object):
     """Abstraction Of SSH accessable Linux hosts.
     """

     def __init__(self, basePath=None):
         '''Constructor'''
         self.__basePath = basePath

     def base(self):
         """
         """
         return self.__basePath

     def readFileParDictFrom(self, fileParDictRelPath):
         """
         """
         fullPath = format(self.__basePath + '/' + fileParDictRelPath)
         blankDict = icm.FILE_ParamDict()
         thisParamDict = blankDict.readFrom(path=fullPath)
         return thisParamDict

     def accessParamsGet(self):
         """
         """
         class AccessParams(object):
             """
             """
             def __init__(self, accessParams=None):
                 '''Constructor'''

                 self.accessMethod = accessParams.get('accessMethod')
                 self.targetFqdn = accessParams.get('targetFqdn')
                 self.userName = accessParams.get('userName')
                 self.password = accessParams.get('password')

                 self.accessMethodValue = self.accessMethod.parValueGetLines()[0]
                 self.targetFqdnValue = self.targetFqdn.parValueGetLines()[0]
                 self.userNameValue = self.userName.parValueGetLines()[0]
                 self.passwordValue = self.password.parValueGetLines()[0]

         accessParamsDict = self.readFileParDictFrom("params/access/cur")
         accessParams = AccessParams(accessParamsDict)
         return accessParams

     def accessParamsSet(
             self,
             accessMethod='ssh',
             targetFqdn='UnSpecified',
             userName='UnSpecified',
             password='UnSpecified',
             ):
         """
         """

         fullPath = format(self.__basePath + '/' + "params/access/cur")

         try: os.makedirs( fullPath, 0777 )
         except OSError: pass

         parFullPath= format(fullPath + '/accessMethod')
         try: os.makedirs( parFullPath, 0777 )
         except OSError: pass
         parValueFullPath= format(parFullPath + '/value')
         with open(parValueFullPath, "w") as valueFile:
             valueFile.write(accessMethod +'\n')

         parFullPath= format(fullPath + '/targetFqdn')
         try: os.makedirs( parFullPath, 0777 )
         except OSError: pass
         parValueFullPath= format(parFullPath + '/value')
         with open(parValueFullPath, "w") as valueFile:
             valueFile.write(targetFqdn +'\n')

         parFullPath= format(fullPath + '/userName')
         try: os.makedirs( parFullPath, 0777 )
         except OSError: pass
         parValueFullPath= format(parFullPath + '/value')
         with open(parValueFullPath, "w") as valueFile:
             valueFile.write(userName +'\n')

         parFullPath= format(fullPath + '/password')
         try: os.makedirs( parFullPath, 0777 )
         except OSError: pass
         parValueFullPath= format(parFullPath + '/value')
         with open(parValueFullPath, "w") as valueFile:
             valueFile.write(password +'\n')


     def configParamsGet(self):
         """Unused and incomplete -- mirrors accessParamsGet
         """
         class ConfigParams(object):
             """
             """
             def __init__(self, paramsDict=None):
                 '''Constructor'''

                 self.accessMethod = paramsDict.get('accessMethod')
                 self.accessMethodValue = self.accessMethod.parValueGetLines()[0]

                 self.targetFqdn = paramsDict.get('targetFqdn')
                 self.targetFqdnValue = self.targetFqdn.parValueGetLines()[0]

         paramsDict = self.readFileParDictFrom("params/config/cur")
         icm.TM_here(paramsDict)
         theseParams = ConfigParams(paramsDict=paramsDict)
         return theseParams


     def configParamsSet(
             self,
             interface='UnSpecified',
             interfaceIpAddr='UnSpecified',
             ):
         """Unused and incomplete -- mirrors accessParamsSet
         """

         fullPath = format(self.__basePath + '/' + "params/config/cur")

         try: os.makedirs( fullPath, 0777 )
         except OSError: pass

         parFullPath= format(fullPath + '/interface')
         try: os.makedirs( parFullPath, 0777 )
         except OSError: pass
         parValueFullPath= format(parFullPath + '/value')
         with open(parValueFullPath, "w") as valueFile:
             valueFile.write(interface +'\n')

         parFullPath= format(fullPath + '/interfaceIpAddr')
         try: os.makedirs( parFullPath, 0777 )
         except OSError: pass
         parValueFullPath= format(parFullPath + '/value')
         with open(parValueFullPath, "w") as valueFile:
             valueFile.write(interfaceIpAddr +'\n')

     def connect(self):
         """
         """
         accessParams = self.accessParamsGet()


         if not accessParams.accessMethodValue == 'ssh':
             # EH_problem()
             pass


         try:
             icm.TM_here(format('ssh -l %s %s' %(
                 accessParams.userNameValue,
                 accessParams.targetFqdnValue)))
             connection = pexpect.spawn('ssh -l %s %s'%(
                 accessParams.userNameValue,
                 accessParams.targetFqdnValue))
         except Exception as e:
             icm.TM_here('EXCEPTION: ' + str(e) )
             raise

         try:
             icm.TM_here('pexpect -- waiting for COMMAND_PROMPT=' + COMMAND_PROMPT)
             i = connection.expect([pexpect.TIMEOUT, SSH_NEWKEY, COMMAND_PROMPT, '(?i)password'])
         except Exception as e:
             icm.TM_here('EXCEPTION: ' + str(e) )
             raise


         #icm.TM_here()

         if i == 0: # Timeout
             icm.TM_here()
             print 'ERROR! could not login with SSH. Here is what SSH said:'
             print connection.before, connection.after
             print str(connection)
             sys.exit (1)
         if i == 1: # In this case SSH does not have the public key cached.
             icm.TM_here()
             connection.sendline ('yes')
             connection.expect ('(?i)password')
         if i == 2:
             icm.TM_here("Auto Login -- Public Key")             
             # This may happen if a public key was setup to automatically login.
             # But beware, the COMMAND_PROMPT at this point is very trivial and
             # could be fooled by some output in the MOTD or login message.
             #pass
             # 20170428 -- Mohsen Fix
             connection.sendline (' ')           
             return connection             
         if i == 3:
             icm.TM_here(format('Received: ' + connection.before + connection.after))
             icm.TM_here('Sending: Passwd')             
             #icm.TM_here('Sending: ' + accessParams.passwordValue )
             connection.sendline(accessParams.passwordValue)
             # Now we are either at the command prompt or
             # the login process is asking for our terminal type.
             icm.LOG_here("Connected ....")
             return connection

     def connectInteractive(self):
         """
         """
         icm.TM_here('NOTYET')

     def runCommand(self, connection, cmndLine):
         """Execute the line and return the result (stdout) as a list of lines
         """
         doExpect (connection, COMMAND_PROMPT)
         # 
         doSendline (connection, cmndLine)
         doExpect (connection, COMMAND_PROMPT)
         resultStr = connection.before
         doSendline (connection, '')    # Prepares things for the next command_prompt       
         lines = resultStr.split('\n')
         resultLines=[]
         for thisLine in range(1, len(lines)-1):
            resultLines.append(lines[thisLine])
         return(resultLines)

     def staticsSet(self):
         """
         """
         icm.TM_here('NOTYET')

     def staticsPush(self):
         """
         """
         icm.TM_here('NOTYET')

     def staticsPull(self):
         """
         """
         icm.TM_here('NOTYET')

     def staticsVerify(self):
         """
         """
         icm.TM_here('NOTYET')


"""
*      ################          *Target Parameters -- (T_Param_Elem, T_Param_List)*
"""

"""
*      ======[[elisp:(org-cycle)][Fold]]====== /T_Param_Elem:/  Target Parameter Element
"""

class Target_Param_Elem(object):
     """Representation of One Parameter_Element.

     """
     def __init__(self, parameterType=None, base=None, dnType=None, dnQualifier=None):
         '''Constructor'''
         self.__parameterType = parameterType
         self.__base = base
         self.__dnType = dnType                  
         self.__dnQualifier = dnQualifier
         self.__config = dnQualifier

     def parameterType(self):
         """
         """
         return self.__parameterType

     def base(self):
         """
         """
         return self.__base

     def dnQualifier(self):
         """
         """
         return self.__dnQualifier

     def dnType(self):
         """
         """
         return self.__dnType
         
     def fileParamsBase(self):
         """
         """
         return format(self.__base + '/' + self.__dnQualifier)

     def fileParamsGet(self):
         """
         """
         fileParamsBase = self.fileParamsBase()
         #params = FILE_parametersRead(fileParamsBase)
         #return params

"""
*      ======[[elisp:(org-cycle)][Fold]]====== /T_Param_List:/  Target Parameter List (of TParam_List)
"""
         

class Target_Param_List(object):
     """Maintain a list of Parameters
     """

     parameterList = []

     def __init__(self):
         pass

     def parameterAppend(self, parameter=None):
         """
         """
         self.__class__.parameterList.append(parameter)

     def parameterAdd(self, parameterType=None, base=None, dnType=None, dnQualifier=None):
         """
         """
         newParameter = Target_Param_Elem(parameterType=parameterType, base=base, dnType=dnType, dnQualifier=dnQualifier)

         self.__class__.parameterList.append(newParameter)

     def parameterListGet(self):
         """
         """
         return self.__class__.parameterList

     def parameterFind(self, dnQualifier=None):
         """
         """
         for parameter in self.__class__.parameterList:
             if parameter.dnQualifier() == dnQualifier:
                 return parameter


                          

"""
*      ################          *TICMO OUTPUTS -- (Target-oriented Interactively Invokable Output Facilities)*
"""


#@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def targetParamListCommonArgs(parser):
    """Module Specific Extra Arguments.
    """

    icmParams = icm.ICM_ParamDict()

    icmParams.parDictAdd(
        parName='empnaPkg',
        parDescription="Empna Detection And Notification Label",
        parDataType=None,
        parDefault=None,
        parChoices=None,
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--empnaPkg',
        )

    icmParams.parDictAdd(
        parName='dateVer',
        parDescription="",
        parDataType=None,
        parDefault=None,
        parChoices=None,
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--dateVer',
        )

    icmParams.parDictAdd(
        parName='collective',
        parDescription='Collective. Eg, int, ir, us, fr',
        parDataType=None,
        parDefault=None,
        parChoices=None,
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--collective',
        )

    icmParams.parDictAdd(
        parName='district',
        parDescription="District. Eg, libreCenter",
        parDataType=None,
        parDefault=None,
        parChoices=None,
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--district',
        )

    icmParams.parDictAdd(
        parName='targetType',
        parDescription="Target Type.",
        parDataType=None,
        parDefault=None,
        parChoices=None,
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--targetType',
        )

    icmParams.parDictAdd(
        parName='targetId',
        parDescription="Target ID.",
        parDataType=None,
        parDefault=None,
        parChoices=None,
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--targetId',
        )


    icmParams.parDictAdd(
        parName='targetFqdn',
        parDescription="Host name or IP Address",
        parDataType=None,
        parDefault=None,
        parChoices=None,
    #parCmndApplicability=['all'],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseLongOpt='--targetFqdn',
        )

    icmParams.parDictAdd(
        parName='accessMethod',
        parDescription="Connect using the indicated accessMethod.",
        parDataType=None,
        parDefault=None,
        parChoices=None,
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseLongOpt='--accessMethod',
        )

    icmParams.parDictAdd(
        parName='userName',
        parDescription="Connect using the indicated userName.",
        parDataType=None,
        parDefault=None,
        parChoices=None,
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt='-u',
        argparseLongOpt='--userName',
        )

    icmParams.parDictAdd(
        parName='password',
        parDescription="Use the indicated password to authenticate the connection.",
        parDataType=None,
        parDefault=None,
        parChoices=None,
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt='-p',
        argparseLongOpt='--password',
        )
      
    icm.argsparseBasedOnIcmParams(parser, icmParams)

    return


@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def targetParamSelectCommonExamples(loadTargetArgs="",
                                  loadParamsArgs="",
                                  ):
    """  """
    icm.cmndExampleMenuChapter('*Common: Select TargetList and Target Parameters*')

    icm.cmndExampleExternalCmndItem("""./empnaProc.sh""",
                                    comment=""" # Used For Selecting Current Target List""")
    icm.cmndExampleExternalCmndItem("""./empnaProc.sh -i effectiveLisLs""")
                                  

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def targetParamListCommonExamples(loadTargetArgs="",
                                  loadParamsArgs="",
                                  ):
    """  """
    icm.cmndExampleMenuChapter('*Common: TargetList And ParameterList and TICMO (Output) Information*')       

    icm.cmndExampleMenuSection('targetsAccessListShow -- Based on targetsAccessListGet')   

    thisCmndAction= " -i empna.targetsAccessListShow"
    icm.cmndExampleMenuItem(format (loadTargetArgs + thisCmndAction),
                            verbosity='none')                            

    thisCmndAction= " -i empna.targetsAccessListGet"
    icm.cmndExampleMenuItem(format (loadTargetArgs + thisCmndAction),
                            verbosity='none')                            

    icm.cmndExampleMenuSection('targetParametersListShow -- Based on targetParametersListGet')   

    thisCmndAction= " -i empna.targetParamsListShow"
    icm.cmndExampleMenuItem(format (loadTargetArgs + loadParamsArgs + thisCmndAction),
                            comment= "# Targets List + T_Params List",
                            verbosity='none')  
    thisCmndAction= " -i empna.targetParamsListGet"
    icm.cmndExampleMenuItem(format (loadTargetArgs + loadParamsArgs + thisCmndAction),
                            verbosity='none')                            

    icm.cmndExampleMenuSection("""TICMO: Target Path Base -- Give A Target's DN, Produce its Path Base""")

    thisCmndAction=" -i empna.targetBaseGet"
    targetSpecOptions=" --collective int --district libreCenter --targetType bxp --targetId localhost"
    icm.cmndExampleMenuItem(format (loadTargetArgs + targetSpecOptions  +  thisCmndAction),
                            verbosity='none')



"""
*      ======[[elisp:(org-cycle)][Fold]]====== ticmo Common Outputs
"""

"""
**      ====[[elisp:(org-cycle)][Fold]]==== ticmoBaseCreate
"""

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def ticmoBaseCreate(ticmoBase=None):
    """  """
    if ticmoBase == None:
        return icm.EH_problem_usageError()    

    parFullPath=ticmoBase
    try: os.makedirs( parFullPath, 0775 )
    except OSError: pass


"""
*      ======[[elisp:(org-cycle)][Fold]]====== ticmoBxpOutputs
"""

"""
**      ====[[elisp:(org-cycle)][Fold]]==== ticmoBxpOutputsBaseGet
"""

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def ticmoBxpOutputsBaseGetCmnd(interactive=False,
                           targetType="bxp",
                           collective=None,
                           district=None,
                           targetId=None):
    """  """
    try: icm.callableEntryEnhancer(type='cmnd')
    except StopIteration:  return
                           
    if targetType != "bxp":
        return icm.EH_problem_usageError("Unsupported Target Type: " + targetType)

    G = icm.IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()
    #icmParamDict = G.icmParamDictGet()

    if interactive == True:
        if not len(icmRunArgs.cmndArgs) == 0:
            try:  icm.EH_runTime('Bad Number Of cmndArgs')
            except RuntimeError:  return

        if icmRunArgs.collective:
            collective = icmRunArgs.collective

        if icmRunArgs.district:
            district = icmRunArgs.district
                            
        if icmRunArgs.targetType:
            targetType = icmRunArgs.targetType

        if icmRunArgs.targetId:
            targetId = icmRunArgs.targetId

    # /de/bx/ticmo/int/libreCenter/targets/bxp/bue/
    return(format("/de/bx/ticmo/%s/%s/targets/%s/%s" % 
                 (collective, district, targetType, targetId)))


"""
**      ====[[elisp:(org-cycle)][Fold]]==== ticmoBxpOutputsBaseGet
"""

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def ticmoBxpOutputsBaseGet(targetType="bxp",
                           targetElem=None,
                           collective=None,
                           district=None,
                           targetId=None):
    """  """
    if targetType != "bxp":
        return icm.EH_problem_usageError("Unsupported Target Type: " + targetType)

    if targetElem:
        # NOTYET, Get collectivem district, ... from targetElem
        if targetId == None:
            targetId = targetElem.targetFqdn()

    # /de/bx/ticmo/int/libreCenter/targets/bxp/bue/
    return(format("/de/bx/ticmo/%s/%s/targets/%s/%s" % 
                 (collective, district, targetType, targetId)))

"""
*      ################      _General Bxp Target And Parameter List CMND Facilities_
"""

"""
*      ======[[elisp:(org-cycle)][Fold]]====== targetsAccessListShow (CMND)
"""

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def targetsAccessListShow(interactive=False,
                          targetFqdn=None,
                          accessMethod=None,
                          userName=None,
                          password=None):
    """ Calls targetsAccessListGet and prints the results. """
    try: icm.callableEntryEnhancer(type='cmnd')
    except StopIteration:  return

    #G = icm.icm.IcmGlobalContext()
    #icmRunArgs = G.icmRunArgsGet()

    targetsAccessList = targetsAccessListGet(interactive=False,
                                             targetFqdn=targetFqdn,
                                             accessMethod=accessMethod,
                                             userName=userName,
                                             password=password)                                               
    
    print "Targets Access List:"
    print targetsAccessList

    return


"""
*      ======[[elisp:(org-cycle)][Fold]]====== targetsAccessListGet  (CMND)
"""

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def targetsAccessListGet(interactive=False,
                         targetFqdn=None,
                         accessMethod=None,
                         userName=None,
                         password=None):
    """ Returns a list of path to targetSpecifiers.
        If interactive args have been specified, an ephemera targetPathSpecifier
        is added to list of path to be returned.
        Loaded TARGET_list is appended to returnedList.
    """

    try: icm.callableEntryEnhancer(type='cmnd')
    except StopIteration:  return

    G = icm.IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()
    #icmParamDict = G.icmParamDictGet()

    #thisFunc = icm.FUNC_currentGet()
    #cmndThis= thisFunc.__name__
    #cmndMandatoryParams=[]
    #cmndOptionalParams=[]
    
    cmndPathTargets=[]

    if interactive == True:
        if not len(icmRunArgs.cmndArgs) == 0:
            try:  icm.EH_runTime('Bad Number Of cmndArgs')
            except RuntimeError:  return

        if icmRunArgs.targetFqdn:
            targetFqdn = icmRunArgs.targetFqdn

        if icmRunArgs.accessMethod:
            accessMethod = icmRunArgs.accessMethod
                            
        if icmRunArgs.userName:
            userName = icmRunArgs.userName

        if icmRunArgs.password:
            password = icmRunArgs.password

    if targetFqdn != None:
        ephemeraTargetBase = format("/tmp/ephemera-target/" + targetFqdn)
        try: os.makedirs(ephemeraTargetBase, 0777)
        except OSError: pass
        linuxTarget = TARGET_Proxy_Linux(basePath=ephemeraTargetBase)

        linuxTarget.accessParamsSet(
            accessMethod=accessMethod,
            targetFqdn=targetFqdn,
            userName=userName,
            password=password,
            )

        cmndPathTargets.append(ephemeraTargetBase)

    # Check For cmndArgs and stdin and  Add Them To cmndTargets
    for thisCmndArg in icmRunArgs.cmndArgs:
        icm.TM_here(thisCmndArg)
        cmndPathTargets.append(thisCmndArg)

    # NOTYET: Check For TargetParams and Add Them To cmndTargets

    tl = TARGET_List()
    targetList = tl.targetListGet()

    #icm.icm.TM_here(targetList)

    for thisTarget in targetList:
        targetType = thisTarget.targetType()
        if targetType != 'bxp':
            icm.EH_problem_usageError(targetType)
            continue
        dnType = thisTarget.dnType()
        #dnQualifier = thisTarget.dnQualifier()
        dnBase = thisTarget.base()        

        if dnType == 'path':
            cmndPathTargets.append(dnBase)            
        else:
            icm.EH_problem_usageError(dnType)            

    # for thisPathTarget in cmndPathTargets:
    #     print thisPathTarget

    return cmndPathTargets

        

"""
*      ======[[elisp:(org-cycle)][Fold]]====== T_Param_List Get  (CMND)
"""

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def targetParamsListGet(interactive=False):
    """ Returns a list of path to targetSpecifiers.
        If interactive args have been specified, an ephemera targetPathSpecifier
        is added to list of path to be returned.
        Loaded TARGET_list is appended to returnedList.
    """

    try: icm.callableEntryEnhancer(type='cmnd')
    except StopIteration:  return

    G = icm.IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()
    
    if interactive == True:
        if not len(icmRunArgs.cmndArgs) == 0:
            try:  icm.EH_runTime('Bad Number Of cmndArgs')
            except RuntimeError:  return

    tpl = Target_Param_List()
    paramList = tpl.parameterListGet()

    return paramList


"""
*      ======[[elisp:(org-cycle)][Fold]]====== T_Param_List Show (CMND)
"""

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def targetParamsListShow(interactive=False):
    """ Calls targetsAccessListGet and prints the results. """
    try: icm.callableEntryEnhancer(type='cmnd')
    except StopIteration:  return

    targetsAccessListShow(interactive=interactive)

    paramList = targetParamsListGet(interactive=interactive)

    print("Target Parameters List:")
    for thisParam in paramList:
        parameterType = thisParam.parameterType()
        if parameterType != 'bxp':
            continue
        #dnType = thisTarget.dnType()
        #paramName = thisParam.dnQualifier()
        paramBase = thisParam.base()
        print(paramBase)


"""
*      ======[[elisp:(org-cycle)][Fold]]====== targetBaseGet (CMND)
"""

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def targetBaseGet(interactive=False,    # Both Non-Interactive and Interactive
                  targetElem=None,
                  collective="int",
                  district="libreCenter",
                  targetType="bxp",
                  targetId=None):
    """  """
    try: icm.callableEntryEnhancer(type='cmnd')
    except StopIteration:  return

    G = icm.IcmGlobalContext()
    icmRunArgs = G.icmRunArgsGet()
    #icmParamDict = G.icmParamDictGet()

    if interactive == True:
        if not len(icmRunArgs.cmndArgs) == 0:
            try:  icm.EH_runTime('Bad Number Of cmndArgs')
            except RuntimeError:  return

        if icmRunArgs.collective: collective = icmRunArgs.collective
        if icmRunArgs.district: district = icmRunArgs.district
        if icmRunArgs.targetType: targetType = icmRunArgs.targetType
        if icmRunArgs.targetId: targetId = icmRunArgs.targetId

    targetBase = ticmoBxpOutputsBaseGet(targetType=targetType,
                                             targetElem=targetElem,
                                             collective=collective,
                                             district=district,
                                             targetId=targetId)
    print(targetBase)
    return(targetBase)



    

####+BEGIN: bx:icm:python:section :title "End Of Editable Text"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
