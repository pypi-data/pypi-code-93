# -*- coding: utf-8 -*-
"""\
* TODO *[Summary]* ::  A /library/ with ICM Cmnds to support ByStar facilities
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/de/bx/nne/dev-py/pypi/pkgs/unisos/x822Msg/dev/unisos/x822Msg/new-msgOut.py :: [[elisp:(org-cycle)][| ]]
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
__libName__ = "new-msgOut"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201712255611"
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

import copy

import email
import smtplib


# NOTYET, should become a dblock with its own subItem
from unisos import ucf
from unisos import icm

G = icm.IcmGlobalContext()
G.icmLibsAppend = __file__
G.icmCmndsLibsAppend = __file__
# NOTYET DBLOCK Ends -- Rest of bisos libs follow;

from unisos.x822Msg import msgLib

####+BEGIN: bx:dblock:python:section :title "Library Description (Overview)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Library Description (Overview)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:python:icm:cmnd:classHead :modPrefix "new" :cmndName "bxpBaseDir_LibOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /bxpBaseDir_LibOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class msgOut_LibOverview(icm.Cmnd):
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
** :Documentation: Authorative [[file:/lcnt/lgpc/bystar/permanent/facilities/marmee]]
** :Web:  http://www.by-star.net/PLPC/180051
** :Overview: (Functional Specification)
    msgOut is a library (set of facilities) that provide for 
    composition and submission of email messages based on the
    *Mail Gui To Mail Submit Client Software Pipeline*
    model.
    During mail-composition, a number of mail-headers are 
    added to the email header. 
    When the email is to be sent, all the necessary information 
    for the mail submission client is within the email headers.
    Standard capabilities of X822 Mail Submit Pipeline (X822-MSP) are:
      - Envelope-Addr specification
      - Deleivery-Status-Notifications Request  (bounce addresses and delivery reports)
      - Disposition-Notifications  (read-receipts)
      - Flexible Parameterized Message Submission (host, ssl, user, passwd)
** :SendingModel:
    Sending is the act of delivering the message to another 
    process for the purpose of transfer.
    Sending can be one of:
*** Injection -- using the command line and pipes
*** Submission -- using a protocol (smtp, etc.)
** :CompositionModel: (Mail User Agent)
   The msg itself is used as a container to gether and carry 
   all parameters and all requests for the message submission.
   The following local header fields are recognized:
*** BX-Non-Delivery-Notification
**** BX-Non-Delivery-Notification-Req-PerRecipient:
**** BX-Non-Delivery-Notification-Req-For:
**** BX-Non-Delivery-Notification-Req-To:
**** X-B-Non-Delivery-Notification-Actions:
*** BX-Delivery-Notification
**** BX-Delivery-Notification-Req-PerRecipient:
**** BX-Delivery-Notification-Req-For:
**** BX-Delivery-Notification-Req-To:
*** BX-Disposition-Notification
**** BX-Disposition-Notification-Req-PerRecipient:
**** BX-Disposition-Notification-Req-For:
**** BX-Disposition-Notification-Req-To:
*** X-B-Envelope-Addr:
*** X-B-CrossRef:
*** BX-Sending
**** BX-Sending-Method:          # inject, submit
**** BX-Sending-Run-Control:   # dryrun, debug
*** BX-MTA-Injection -- Obsoleted
**** BX-MTA-Injection-Plugins:   # for composite injection profile
**** BX-MTA-Injection-Method:    # inject, submit
**** BX-MTA-Injection-Control:   # dryrun, debug
*** BX-MTA-Rem
**** BX-MTA-Rem-Protocol:        # smtp
**** BX-MTA-Rem-Host:
**** BX-MTA-Rem-PortNu:
**** BX-MTA-Rem-User:
**** BX-MTA-Rem-Passwd:
**** BX-MTA-Rem-LinkConfidentiality:  ssl/tls
**** BX-MTA-Rem-CertFile:
**** BX-MTA-Rem-KeyFile:
**** BX-MTA-Submission-Pre-Plugins:    # executed before send
**** BX-MTA-Submission-Post-Plugins:   # executed after send for error reporting
** :SubmissionModel: (Mail Transfer Agent)
*** BX-MTA-Submission-Pre-Plugins are executued in order specified.
*** All the BX- headers are recognized and converted to params
*** Where appropriate BX- headers are converted to standard headers.
*** Some BX- headers are stripped
*** Complete SMTP Submit Protocol based on the email.smtp python library is executed.
*** BX-MTA-Submission-Post-Plugins are executued in order specified.
** :Contacts:
	[[elisp:(bystar:bbdb:search-here "Mohsen Banan")][Mohsen BANAN]]

**      [End-Of-Description]
"""
        
        moduleUsage="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]

**      How-Tos:
**      :Order: Of Invokations At Message Composition and Message Submission
*** import msgOut
*** envelopeAddrSet()
*** crossRefInfo()
*** nonDeliveryNotificationRequetsForTo()
*** deliveryNotificationRequetsForTo()
*** dispositionNotificationRequetsForTo()
*** injectionParams()
*** injectBasedOnHeadersInfo()
**      :Examples:
*** See msgOutExample.py

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
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Topic Section*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:dblock:python:subSection :title "Topic SubSection"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Topic SubSection*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Common Facilities*
"""



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  enumFromStrWhenValid    [[elisp:(org-cycle)][| ]]
"""
def enumFromStrWhenValid(
        enumTypeStr,
        enumValueStr,
):
    """
** Given a string, return the Enum's value if valid. 

Applies to current module because of exec and can therefore not be in a library
and is therefor a dblock.

Usage: 
    InjectionProgram = ucf.Enum(qmail='qmail', sendmail='sendmail',)
    if enumFromStrWhenValid('InjectionProgram', inputStr) == None: badInput()

Note: enumTypeStr.enumValueStr  gets execed. So a '-', "+" in enumValueStr is problematic.

*** TODO NOTYET, should become a dblock
"""
    enumRes = None
    try:
        #print "{0}.{1}".format(enumTypeStr, enumValueStr)
        exec("enumRes = {0}.{1}".format(enumTypeStr, enumValueStr))            
    except AttributeError:
        icm.LOG_here(enumValueStr)
        return None
    else:
        #print  enumRes
        return enumRes

    
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Envelope Address Specification*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  envelopeAddrSet    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def envelopeAddrSet(
        msg,
        mailBoxAddr,
):
    """
** Set the msg's envelope address to mailBoxAddr, but only if it had not been previously set.
This will be used for delivery-reports and non-delivery-reports.
"""
    if not 'X-B-Envelope-Addr' in msg:
        if mailBoxAddr:
            msg['X-B-Envelope-Addr'] = mailBoxAddr        
            
    return


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Delivery Status Notification And Disposition Report Requests*
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  dispositionNotificationRequetsForTo    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def dispositionNotificationRequetsForTo(
        msg,
        recipientsList=None,        
        notifyTo=None,
):
    """
** Request Receipt-Nofications for each of recipientsList. Notifications are to be sent to notifyTo address.
"""
    if recipientsList:
        msg['BX-Disposition-Notification-Req-For'] = ", ".join(recipientsList)

    if notifyTo:
        msg['BX-Disposition-Notification-Req-To'] = notifyTo

    return

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  dispositionNotificationRequetsPerRecipient    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def dispositionNotificationRequetsPerRecipient(
        msg,
        perRecipientsList=None,
):
    """
** Place Holder.
"""
    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  deliveryNotificationRequetsForTo    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryNotificationRequetsForTo(
        msg,
        recipientsList=None,
        notifyTo=None,
):
    """
** Request Delivery-Reports for each of recipientsList. Notifications are to be sent to notifyTo address.
"""
    if recipientsList:
        msg['BX-Delivery-Notification-Req-For'] = ", ".join(recipientsList)

    if notifyTo:
        msg['BX-Delivery-Notification-Req-To'] = notifyTo

    return

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  deliveryNotificationRequetsPerRecipient    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryNotificationRequetsPerRecipient(
        msg,
        perRecipientsList=None,
):
    """
** Place Holder.
"""
    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  nonDeliveryNotificationRequetsForTo    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def nonDeliveryNotificationRequetsForTo(
        msg,
        recipientsList=None,        
        notifyTo=None,
):
    """
** Request Non-Delivery-Reports for each of recipientsList. Notifications are to be sent to notifyTo address.
"""
    if recipientsList:
        msg['BX-Non-Delivery-Notification-Req-For'] = ", ".join(recipientsList)

    if notifyTo:
        msg['BX-Non-Delivery-Notification-Req-To'] = notifyTo

    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  nonDeliveryNotificationRequetsPerRecipient    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def nonDeliveryNotificationRequetsPerRecipient(
        msg,
        perRecipientsList=None,
):
    """
** Place Holder.
"""
    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  nonDeliveryNotificationActions    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def nonDeliveryNotificationActions(
        msg,
        coRecipientsList=None,
):
    """
** Based on action and address, process the Non-Delivery-Notification and notify each of coRecipientsList.
"""
    if coRecipientsList:
        msg['X-B-Non-Delivery-Notification-Actions'] = ", ".join(coRecipientsList)

    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  crossRefInfo    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def crossRefInfo(
        msg,
        crossRefInfo,
):
    """
** Set the crossRefInfo. E.g., X-B-CrossRef: peepid.
"""
    if crossRefInfo:
        msg['X-B-CrossRef'] = crossRefInfo

    return

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  dispositionNotificationHeaders    [[elisp:(org-cycle)][| ]]
"""    
def dispositionNotificationHeaders(
        msg,
        notifyTo,
):
    """
** Disposition-Notification-To is from RFC-8098 -- Return-Receipt-To is non standard but used.
"""
    msg['Disposition-Notification-To'] = notifyTo
    msg['Return-Receipt-To'] = notifyTo


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  deliveryNotificationHeaders    [[elisp:(org-cycle)][| ]]
"""    
def deliveryNotificationHeaders(
        msg,
        recipientsList,        
):
    """ 
** Notice-Requested-Upon-Delivery-To (NRUDT) as specified in: https://tools.ietf.org/html/draft-bernstein-nrudt-02
NRUDT is supported by the qreceipt program in the qmail package.

This header line can be shared and does not need to have
its own uniq msg.
"""
    if recipientsList:
        if 'Notice-Requested-Upon-Delivery-To' in msg:
            icm.LOG_here("Notice-Requested-Upon-Delivery-To -- existed. It has not been updated.")
        else:
            msg['Notice-Requested-Upon-Delivery-To'] = ", ".join(recipientsList)
    return



"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Mail Sending Method Selection -- Injection or Submit*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Enum        ::  SendingMethod -- Enum Values: inject, submit, etc [[elisp:(org-cycle)][| ]]
"""    
SendingMethod = ucf.Enum(
    inject='inject',
    submit='submit',
)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Enum        ::  SendingRunControl -- Enum Values: fullRun, dryRun, etc [[elisp:(org-cycle)][| ]]
"""    
SendingRunControl = ucf.Enum(
    fullRun='fullRun',
    dryRun='dryRun',
    runDebug='runDebug',
)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  sendingMethodSet -- Header Tagging as (inject, submit, etc)   [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def sendingMethodSet(
        msg,
        sendingMethodStr,
):
    """
** Set BX-Sending-Method in X822-MSP.
"""
    opRes = icm.OpOutcome()
    if enumFromStrWhenValid('SendingMethod', sendingMethodStr) == None:
        return icm.eh_problem_usageError(opRes, sendingMethodStr)
    if not 'BX-Sending-Method' in msg:
        msg['BX-Sending-Method'] = sendingMethodStr
    
    return opRes


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  sendingRunControlSet -- Header Tagging as (dryRun, fullRun)   [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def sendingRunControlSet(
        msg,
        sendingRunControl,
):
    """
** Set the msg's envelope address to mailBoxAddr. This will be used for delivery-reports and non-delivery-reports.
"""
    opRes = icm.OpOutcome()
    if enumFromStrWhenValid('SendingRunControl', sendingRunControl) == None:
        return (
            icm.eh_problem_usageError(opRes, sendingRunControl)
        )
    msg['BX-Sending-Run-Control'] = sendingRunControl
    return opRes

    
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Msg Injection (Request Parameters)*
"""



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Enum        ::  InjectionProgram -- Enum values of qmail, sendmail  [[elisp:(org-cycle)][| ]]
"""    
InjectionProgram = ucf.Enum(
    qmail='qmail',
    sendmail='sendmail',
)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  injectionProgramSet  -- Injection Program Header Tagging  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def injectionProgramSet(
        msg,
        injectionProgram,
):
    """
** Set the msg's envelope address to mailBoxAddr. This will be used for delivery-reports and non-delivery-reports.
"""
    opOutcome = icm.OpOutcome()
    if enumFromStrWhenValid('InjectionProgram', injectionProgram) == None:
        return (
            icm.EH_problem_usageError(injectionProgram)
        )
    msg['BX-Injection-Program'] = injectionProgram
    return opOutcome

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  injectionParams -- Header Tag All Injection Params   [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def injectionParams(
        msg,
        sendingRunControl=SendingRunControl.fullRun,
        injectionProgram=InjectionProgram.qmail      
):
    """
** Set necessary  injectionParams, to be used by sendBasedOnHeadersInfo.
"""

    if sendingMethodSet(msg, SendingMethod.inject).isProblematic():
        return icm.eh_badLastOutcome()

    if sendingRunControlSet(msg, sendingRunControl).isProblematic():
        return icm.eh_badLastOutcome()
    
    if injectionProgramSet(msg, injectionProgram).isProblematic():
        return icm.eh_badLastOutcome()
    
    return icm.opSuccess()


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Msg Submission (Request Parameters)*
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Enum        ::  MtaRemProtocol -- Enum values of: smtp, smtp_ssl, smtp_tls  [[elisp:(org-cycle)][| ]]
"""    
MtaRemProtocol = ucf.Enum(
    smtp='smtp',
    smtp_ssl='smtp_ssl',
    smtp_tls='smtp_tls',    
)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  mtaRemProtocolSet -- Header Tagging mtaRemProtocol  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def mtaRemProtocolSet(
        msg,
        mtaRemProtocolStr,
):
    """
** Set the msg's envelope address to mailBoxAddr. This will be used for delivery-reports and non-delivery-reports.
"""
    opRes = icm.OpOutcome()
    if enumFromStrWhenValid('MtaRemProtocol', mtaRemProtocolStr) == None:
        return (
            icm.eh_problem_usageError(opRes, mtaRemProtocolStr)
        )
    msg['BX-MTA-Rem-Protocol'] = mtaRemProtocolStr    
    return opRes


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  submitParams    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def submitParams(
        msg,
        sendingRunControl=SendingRunControl.fullRun,
        mtaRemProtocol=None,          # smtp
        mtaRemHost=None,              # Remote Host To Submit to (could be localhost)
        mtaRemPort=None,
        mtaRemUser=None,        
        mtaRemPasswd=None,
        mtaRemCerts=None,
        
):
    """
** Set necessary  injectionParams, to be used by sendBasedOnHeadersInfo. Header Tag All Submit Params.
"""

    if sendingMethodSet(msg, SendingMethod.submit).isProblematic():
        return icm.eh_badLastOutcome()

    if sendingRunControlSet(msg, sendingRunControl).isProblematic():
        return icm.eh_badLastOutcome()

    if mtaRemProtocolSet(msg, mtaRemProtocol).isProblematic():
        return icm.eh_badLastOutcome()

    if not 'BX-MTA-Rem-Host' in msg:    
        if mtaRemHost:
            msg['BX-MTA-Rem-Host'] = mtaRemHost

    if not 'BX-MTA-Rem-PortNu' in msg:            
        if mtaRemPort:
            msg['BX-MTA-Rem-PortNu'] = mtaRemPort

    if not 'BX-MTA-Rem-User' in msg:                        
        if mtaRemUser:
            msg['BX-MTA-Rem-User'] = mtaRemUser

    if not 'BX-MTA-Rem-Passwd' in msg:                                    
        if mtaRemPasswd:
            msg['BX-MTA-Rem-Passwd'] = mtaRemPasswd
         
    if mtaRemCerts:
        msg['BX-MTA-Rem-Certificates'] = mtaRemCerts
        
    return



"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Send Based On Headers*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  sendBasedOnHeadersInfo    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def sendBasedOnHeadersInfo(
        msg,
):
    """
** Submit or Inject msg using information contained in the header.

** Overview

Dispatch to recipients based on tailored Msg and tailored submission info.
Processes headers and creates two classes,
    - MsgForRecipient
    - OptionsForRecipient
Given a msg and recipients from MsgForRecipient
    - find common options for common recipients
    - Submit based on msg and options
    """

    bx822Set_setMandatoryFields(msg,)    

    if 'BX-Sending-Method' in msg:
        sendingMethod = msg['BX-Sending-Method']
    else:
        return icm.EH_problem_info("BX-Sending-Method")

    if sendingMethod == SendingMethod.inject:
        opOutcome = injectBasedOnHeadersInfo(msg,)            

    elif sendingMethod == SendingMethod.submit:
        opOutcome = submitBasedOnHeadersInfo(msg,) 

    else:
        return (icm.EH_problem_info("Bad Usage"))

    return opOutcome


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  mailHeadersPipelineClean    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def mailHeadersPipelineClean(
        msg,
):
    """
** Given a msg, at the end of mailHeadersPipeline cleanup (strip BX-)the headers.

    We want to make sure that msg's header does not contains any extra
    headers that are publicly visible and that are not needed.

    The X-B- header lines are public and should not be stripped.
"""

    toBeStrippedHeaders = [
        'BX-Non-Delivery-Notification-Req-To',
        'BX-Disposition-Notification-Req-For',
        'BX-Disposition-Notification-Req-To',
        'BX-Delivery-Notification-Req-For',
        'BX-Delivery-Notification-Req-To',        
        'BX-MTA-Injection-Method',
        'BX-MTA-Injection-Control',
    ]

    for each in toBeStrippedHeaders:
        if each in msg:  
            del msg[each]


    
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Inject Based On Headers*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  injectBasedOnHeadersInfo    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def injectBasedOnHeadersInfo(
        msg,
):
    """
** Dispatch based on BX-Injection-Program -- sendmail or qmail().
"""

    if 'BX-Injection-Program' in msg:
        injectionProgram = msg['BX-Injection-Program']
    else:
        injectionProgram = InjectionProgram.qmail
        #return icm.EH_problem_info("BX-Injection-Program")

    if injectionProgram == InjectionProgram.qmail:
        opOutcome = injectMsgWithQmail(msg,)            

    elif injectionProgram == InjectionProgram.qmail:
        opOutcome = injectMsgWithSendmail(msg,) 

    else:
        return (
            icm.EH_problem_info("Bad Usage")   
        )

    return opOutcome



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  injectMsgWithQmail    [[elisp:(org-cycle)][| ]]
"""    
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def injectMsgWithQmail(
        msg,
):
    """
** qmail inject -- NOTYET.
"""

    #icm.LOG_here("qmail Inject \n{msgStr}".format(msgStr=msg.as_string()))

    cmndLineOptions=""
    if icm.icmRunArgs_isRunModeDryRun():
        cmndLineOptions=" -n"

    commandLine=format("qmail-inject" + cmndLineOptions)

    outcome = icm.subProc_bash(
        commandLine,
        stdin=msg.as_string(),        
    ).log()
    if outcome.isProblematic(): return(icm.EH_badOutcome(outcome))

    #if outcome.stdout: icm.ANN_note("Stdout: " +  outcome.stdout)
    #if outcome.stderr: icm.ANN_note("Stderr: " +  outcome.stderr)
        
    return outcome.set(
        opError=icm.OpError.Success,
        opResults=None,
    )


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  injectMsgWithSendmail    [[elisp:(org-cycle)][| ]]
"""    
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def injectMsgWithSendmail(
        msg,
):
    """
** sendmail inject. NOTYET
    """


    
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Submit Based On Headers*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  submitBasedOnHeadersInfo    [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def submitBasedOnHeadersInfo(
        msg,
):
    """
** Submit or Inject msg using information contained in the header.

** Overview

Dispatch to recipients based on tailored Msg and tailored submission info.
Processes headers and creates two classes,
    - MsgForRecipient
    - OptionsForRecipient
Given a msg and recipients from MsgForRecipient
    - find common options for common recipients
    - Submit based on msg and options
    """

    if 'X-B-Envelope-Addr' in msg:
        envelopeAddr = msg['X-B-Envelope-Addr']
    else:
        envelopeAddr = msg['From']

    allRecipients = msgLib.msgAllRecipients(
        msg,
    )
    allRecipientsSet = set()
    for thisRecipient in allRecipients:
        allRecipientsSet.add(thisRecipient[1])

    msgForRecipient = MsgForRecipient()

    notificationAddrsSet = set()
    
    if 'BX-Disposition-Notification-Req-For' in msg:
        addrs =  email.utils.getaddresses(
            msg.get_all('BX-Disposition-Notification-Req-For', [])
        )
        for each in addrs:
            if each[1] in allRecipientsSet:
                notificationAddrsSet.add(each[1])
            else:
                icm.EH_problem_info("{each} is not a msg's recipient".format(each=each[1]))
        
        if 'BX-Disposition-Notification-Req-To' in msg:
            addrs =  msg.get_all('BX-Disposition-Notification-Req-To', [])
            notifyTo =  addrs[0]
            #del msg['BX-Disposition-Notification-Req-To']
        else:
            notifyTo = envelopeAddr

        for eachRecipientAddr in notificationAddrsSet:
            msgWithNotifyTo = getMsgWithDispositionNotifyTo(
                msgForRecipient,
                notifyTo,
            )
            if msgWithNotifyTo:
                msgForRecipient.addMsgForRcipient(
                    msgWithNotifyTo,                    
                    eachRecipientAddr,
                )
            else:
                # It must be a deepcopy -- not just copy
                msgCopy = copy.deepcopy(msg)
                dispositionNotificationHeaders(
                    msgCopy,
                    notifyTo,
                )
                msgForRecipient.addMsgForRcipient(
                    msgCopy,                    
                    eachRecipientAddr,
                )

    #
    # All other recipients are associated with the common msg.
    #                
    defaultMsgRecipients = allRecipientsSet - notificationAddrsSet
    for eachRecipientAddr in defaultMsgRecipients:
        msgForRecipient.addMsgForRcipient(
            msg,            
            eachRecipientAddr,
        )
        
    recipientsWithDeliveryNotificationReqSet = set()

    if 'BX-Delivery-Notification-Req-For' in msg:
        addrs =  email.utils.getaddresses(
            msg.get_all('BX-Delivery-Notification-Req-For', [])
        )
        for each in addrs:
            if each[1] in allRecipientsSet:
                recipientsWithDeliveryNotificationReqSet.add(each[1])
            else:
                icm.EH_problem_info("{each} is not a msg's recipient".format(each=each[1]))

        for eachRecipient in recipientsWithDeliveryNotificationReqSet:
            msgOfRecipient = msgForRecipient.getMessageForRecipient(
                eachRecipient,
            )
            if msgOfRecipient:
                #
                # This header line can be shared and does not need to have
                # its own uniq msg.
                #
                deliveryNotificationHeaders(
                    msgOfRecipient,
                    recipientsWithDeliveryNotificationReqSet,
                )

            else:
                icm.EH_problem_info("OOPS")
    #
    # With each copy of the message, we determine which
    # recipients are using that copy. We then determine
    # of those recipients which want delivery-reports and which
    # don't. We then do one submission with delivery-reqs and one without.
    #
    for eachMsg in msgForRecipient.getAllMsgs():
        msgRecipientsList = msgForRecipient.getAllRecipientsForMsg(eachMsg)
        
        msgRecipientsWithDeliveryNotification = set.intersection(
            set(msgRecipientsList),
            recipientsWithDeliveryNotificationReqSet,
        )
        
        if msgRecipientsWithDeliveryNotification:
            submitMsgToRecipients(
                eachMsg,
                msgRecipientsWithDeliveryNotification,
                deliveryNotificationRequest=True,
            )

        msgRecipientsWithoutDeliveryNotification = set(msgRecipientsList) - msgRecipientsWithDeliveryNotification
        
        if msgRecipientsWithoutDeliveryNotification:
            submitMsgToRecipients(
                eachMsg,
                msgRecipientsWithoutDeliveryNotification,
                deliveryNotificationRequest=False,
            )
            
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || FUNC        ::  strLogMessage    [[elisp:(org-cycle)][| ]]
"""    
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def strLogMessage(
        headerStr,
        msg,
):
    """
** Return a string to be used with log_here()
"""
    return (
        "{headerStr}\n{msgStr}".format(
            headerStr=headerStr,
            msgStr=msg.as_string(),
        )
    )


@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def runningWithDebugOn(
        msg,
):
    """
** Return True if runMode==dryRun or runMode=runDebug
"""
    if 'BX-Sending-Run-Control' in msg:
        sendingRunControl = msg['BX-Sending-Run-Control']
    else:
        # We are not going to check G.usageParams.runMode
        # because this library is not tied to ICMs
        return False
    
    if enumFromStrWhenValid('SendingRunControl', sendingRunControl) == None:
        # Unknown is considered DryRun -- to be safe
        return True
    else:
        sendingRunControl = enumFromStrWhenValid('SendingRunControl', sendingRunControl)

    if sendingRunControl == SendingRunControl.dryRun:
        return True
    elif sendingRunControl == SendingRunControl.runDebug:
        return True
    elif sendingRunControl == SendingRunControl.fullRun:
        return False
    else:
        icm.EH_critical_oops("Impossible")
        return True

@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def runningWithDryrun(
        msg,
):
    """
** Return True if runMode==dryRun 
"""
    if 'BX-Sending-Run-Control' in msg:
        sendingRunControl = msg['BX-Sending-Run-Control']
    else:
        # We are not going to check G.usageParams.runMode
        # because this library is not tied to ICMs
        return False
 
        
    if enumFromStrWhenValid('SendingRunControl', sendingRunControl) == None:
        # Unknown is considered DryRun -- to be safe
        return True
    else:
        sendingRunControl = enumFromStrWhenValid('SendingRunControl', sendingRunControl)

    if sendingRunControl == SendingRunControl.dryRun:
        return True
    elif sendingRunControl == SendingRunControl.runDebug:
        return False
    elif sendingRunControl == SendingRunControl.fullRun:
        return False
    else:
        icm.EH_critical_oops("Impossible")
        return True

        
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  submitMsgToRecipients    [[elisp:(org-cycle)][| ]]
"""        
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def submitMsgToRecipients(
        msg,
        recipients,
        deliveryNotificationRequest=False,
):
    """
** Given a msg with needed BX-MTA-Rem headers submit msg to recipients and perhaps request delivery notifications.

Overview
"""
    icm.LOG_here(strLogMessage(
        "Msg Before Any Header Cleanups", msg,))
    
    opRes = icm.OpOutcome()
    
    # if 'BX-MTA-Injection-Control' in msg:
    #     injectionControl = msg['BX-MTA-Injection-Control']
    #     if not isValidInjectionControl(injectionControl): 
    #         icm.EH_problem_info(injectionControl)
    #         return
    # else:
    #     icm.EH_problem_info("BX-MTA-Injection-Control")
    
    if 'X-B-Envelope-Addr' in msg:
        envelopeAddr = msg['X-B-Envelope-Addr']
        #del msg['X-B-Envelope-Addr']
    else:
        envelopeAddr = msg['From']
                
    if 'BX-MTA-Rem-Protocol' in msg:
        mtaRemProtocol = msg['BX-MTA-Rem-Protocol']
        #del msg['BX-MTA-Rem-Protocol']
        if enumFromStrWhenValid('MtaRemProtocol', mtaRemProtocol) == None:
            return (
                icm.eh_problem_usageError(opRes, mtaRemProtocol)
            )
        else:
            mtaRemProtocol =  enumFromStrWhenValid('MtaRemProtocol', mtaRemProtocol)
    else:
        return icm.EH_problem_info("BX-MTA-Rem-Protocol")

    mtaRemHost = "localhost"
    if 'BX-MTA-Rem-Host' in msg:  
        mtaRemHost = msg['BX-MTA-Rem-Host']
        del msg['BX-MTA-Rem-Host']
        
    mtaRemPort = None
    if 'BX-MTA-Rem-PortNu' in msg:  
        mtaRemPort = msg['BX-MTA-Rem-PortNu']
        del msg['BX-MTA-Rem-PortNu']
        
    mtaRemUser = None
    if 'BX-MTA-Rem-User' in msg:  
        mtaRemUser = msg['BX-MTA-Rem-User']
        del msg['BX-MTA-Rem-User']

    mtaRemPasswd = None
    if 'BX-MTA-Rem-Passwd' in msg:  
        mtaRemPasswd = msg['BX-MTA-Rem-Passwd']
        del msg['BX-MTA-Rem-Passwd']

    #mtaRemLinkConfidentiality = None
    #if 'BX-MTA-Rem-LinkConfidentiality' in msg:  
    #    mtaRemLinkConfidentiality = msg['BX-MTA-Rem-LinkConfidentiality']
    #    del msg['BX-MTA-Rem-LinkConfidentiality']

    mtaRemCertFile = None
    if 'BX-MTA-Rem-CertFile' in msg:  
        mtaRemCertFile = msg['BX-MTA-Rem-CertFile']
        del msg['BX-MTA-Rem-CertFile']

    mtaRemKeyFile = None
    if 'BX-MTA-Rem-KeyFile' in msg:  
        mtaRemKeyFile = msg['BX-MTA-Rem-KeyFile']
        del msg['BX-MTA-Rem-KeyFile']

    # 
    mailHeadersPipelineClean(msg)     
    
    if runningWithDebugOn(msg):
        icm.LOG_here("================")
        icm.LOG_here("envelopeAddr= {envelopeAddr}".format(envelopeAddr=envelopeAddr))
        icm.LOG_here("recipients= {recipients}".format(recipients=recipients))
        icm.LOG_here("deliveryNotificationRequest= {deliveryNotificationRequest}".format(deliveryNotificationRequest=deliveryNotificationRequest))                
        icm.LOG_here("---------------")

        icm.LOG_here(strLogMessage(
            "Final Msg As Being Submitted/Injected/Dryruned", msg,))

        if runningWithDryrun(msg):
            icm.ANN_here("DryRun of submitMsgToRecipients -- -v 20 for details")
            icm.LOG_here("DryRun of submitMsgToRecipients")
            return

    icm.LOG_here("")

    def smtpExceptionInfo(e):
        print 'got', e.__class__
        outString = format(e)
        print outString
        #errcode = getattr(e, 'smtp_code', -1)
        #errmsg = getattr(e, 'smtp_error', 'ignore')
        return

    try:
        
        if mtaRemProtocol == MtaRemProtocol.smtp:
            if not mtaRemPort:
                mtaRemPort = 25
            icm.LOG_here("Protocol=smtp -- remHost={remHost} -- portNu={portNu}".format(
                remHost=mtaRemHost, portNu=mtaRemPort,))
            
            smtpConn = smtplib.SMTP(
                mtaRemHost,
                port=mtaRemPort,
            )
        elif mtaRemProtocol == MtaRemProtocol.smtp_ssl:
            if not mtaRemPort:
                mtaRemPort = 465
            icm.LOG_here("Protocol=smtp_ssl -- remHost={remHost} -- portNu={portNu}".format(
                remHost=mtaRemHost, portNu=mtaRemPort,))
            
            smtpConn = smtplib.SMTP_SSL(
                mtaRemHost,
                port=mtaRemPort,
            )
        elif mtaRemProtocol == MtaRemProtocol.smtp_tls:
            if not mtaRemPort:
                mtaRemPort = 587
            icm.LOG_here("Protocol=smtp_tls -- remHost={remHost} -- portNu={portNu}".format(
                remHost=mtaRemHost, portNu=mtaRemPort,))
            icm.LOG_here("Not Fully Implemented/Tested. Will use certFile={} keyFile={}".format(
                mtaRemCertFile,  mtaRemKeyFile,))
            
            smtpConn = smtplib.SMTP_SSL(
                mtaRemHost,
                port=mtaRemPort,
            )

            #smtpConn.starttls()            
        else:
            icm.EH_critical_oops("Coding Error")
            return
        
    except smtplib.SMTPConnectError, e:
        smtpExceptionInfo(e)
        return None
    
    icm.LOG_here("")

    #
    # 
    #
    if runningWithDebugOn(msg):
        smtpConn.set_debuglevel(True)


    if mtaRemUser and mtaRemPasswd:
        try:
            smtpConn.login(
                mtaRemUser,
                mtaRemPasswd,
            )
        except smtplib.SMTPHeloError, e:   # The server didn't reply properly to the helo greeting.
            smtpExceptionInfo(e)
            return None

        except smtplib.SMTPAuthenticationError, e: # The server didn't accept the username/password combination.
            smtpExceptionInfo(e)
            return None

        except smtplib.SMTPNotSupportedError, e:  # The AUTH command is not supported by the server.
            smtpExceptionInfo(e)
            return None

        except smtplib. SMTPException, e:  # No suitable authentication method was found.
            smtpExceptionInfo(e)
            return None

    else:
        icm.EH_problem_usageError(
            "Missing --User={user} Passwd={passwd}".format(
                user=mtaRemUser, passwd=mtaRemPasswd,))
            
    icm.LOG_here("")
    
    #
    # If needed, we logged in. Ready to sendmail()
    #
        
    try:
        if deliveryNotificationRequest == True:
            failedRecipients = smtpConn.sendmail(
                envelopeAddr,
                recipients,
                msg.as_string(),
                mail_options=[],
                rcpt_options=[
                    "NOTIFY=FAILURE,SUCCESS,DELAY",
                ]
            )
        else:
            failedRecipients = smtpConn.sendmail(
                envelopeAddr,
                recipients,
                msg.as_string(),
            )

    except smtplib.SMTPHeloError, e:   # The server didn't reply properly to the helo greeting.
        smtpExceptionInfo(e)
        return None

    except smtplib.SMTPRecipientsRefused, e: # The server rejected ALL recipients (no mail was sent).
        smtpExceptionInfo(e)
        errcode = getattr(e, 'smtp_code', -1)
        errmsg = getattr(e, 'smtp_error', 'ignore')
        refused = []
        for r in recipients:
            refused[r] = (errcode, errmsg)
        return refused

    except smtplib.SMTPSenderRefused, e:  # The server didn't accept the from_addr.
        smtpExceptionInfo(e)
        return None

    except smtplib.SMTPNotSupportedError, e:  # The mail_options parameter includes 'SMTPUTF8' but the SMTPUTF8 extension is not supported by the server.
        smtpExceptionInfo(e)
        return None

    except smtplib.SMTPDataError, e:  # The server replied with an unexpected error code (other than a refusal of a recipient).
        smtpExceptionInfo(e)
        return None

    else:
        return failedRecipients

    finally:
        try:
            smtpConn.quit()
        except smtplib.SMTPServerDisconnected, e:   # Connection unexpectedly closed
            smtpExceptionInfo(e)
            return None


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Per Recipient Replicated Msg Customization And Management*
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || CLASS       ::  MsgForRecipient    [[elisp:(org-cycle)][| ]]
"""
class MsgForRecipient():
     """ 
** Singleton Class: maintain cross-refs for Msgs customized for Recipients. 

     Every recipient is associated with a Msg.
     msgRecipientsDict[msg] maps to a set of recipients.
     """

     msgRecipientsDict = dict()         #  msg, recipientAddrList

     def __init__(self):
         pass

     def addMsgForRcipient(self,
                           msg,                           
                           recipient,
     ):
         if msg in self.__class__.msgRecipientsDict:
             if recipient in self.__class__.msgRecipientsDict[msg]:
                 pass
             else:
                 self.__class__.msgRecipientsDict[msg].add(recipient)
         else:
             self.__class__.msgRecipientsDict[msg]=set([recipient])


     def getAllRecipientsForMsg(self,
                                msg,
     ):
         if msg in self.__class__.msgRecipientsDict:         
             return self.__class__.msgRecipientsDict[msg]
         else:
             icm.EH_problem_info()
             return None

     def getAllMsgs(self,
     ):
         return self.__class__.msgRecipientsDict.keys()

     def getMessageForRecipient(self,
                                recipient,
     ):
         #icm.LOG_here(self.__class__.msgRecipientsDict)
         for eachMsg in self.__class__.msgRecipientsDict:
             recipientsList = self.__class__.msgRecipientsDict[eachMsg]
             if recipient in recipientsList:
                 return eachMsg
         return None

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func        ::  getMsgWithDispositionNotifyTo    [[elisp:(org-cycle)][| ]]
"""     
def getMsgWithDispositionNotifyTo(
        msgForRecipient,
        notifyTo,
):
    """
** Return msg or None. Find msg for msgForRecipient whose Disposition-Notification-To is notifyTo.
"""
    for msg in msgForRecipient.getAllMsgs():
        if 'Disposition-Notification-To' in msg:
            dispositionNotifyTo = msg['Disposition-Notification-To']
            if dispositionNotifyTo == notifyTo:
                return msg
    return None

        
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Mandatory Bx822 Fields Set*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  mandatoryBx822FieldsSet    [[elisp:(org-cycle)][| ]]
"""
def bx822Set_setMandatoryFields(
        msg,
):
    """
** Mail Sending Agent's Final Setups: Date, Message-ID, User-Agent, if needed
"""
    if not 'Date' in msg:
        msg['Date'] = email.utils.formatdate(localtime = 1)        

    if not 'Message-ID' in msg:
        msg['Message-ID'] = email.utils.make_msgid()

    return None


    

####+BEGIN: bx:icm:python:section :title "End Of Editable Text"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
