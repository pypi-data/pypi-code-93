# coding=utf-8
#
# Author: Ualter Otoni Pereira
# ualter.junior@gmail.com
#
import os
import logging
import sys
import re, uuid
import atexit 
from os.path import expanduser
import signal, subprocess

from shutil import which
from tinydb import Query, where
from arnparse import arnparse
from awsee.messages import Messages
from awsee.style import Style
from awsee.emoticons import Emoticons
from awsee.utils import Utils
from awsee.tableargs import TableArgs
from awsee.prettytable import PrettyTable
from awsee.awsservices import AwsServices
from awsee.logmanager import LogManager
from awsee.preferences import Preferences
from awsee.functions import Functions
from awsee.rolemanager import RoleManager
from awsee.mfamanager import MFAManager
from awsee.repository import Repository, CredentialsRepository, ConfigRepository, RoleRepository, MfaRepository
from awsee.sessionmanager import SessionManager
from awsee.general import *

class ProfileManager:

    def __init__(self):
        self.credentialsRepository = CredentialsRepository()
        self.configRepository      = ConfigRepository()
        self.roleRepository        = RoleRepository()
        self.mfaRepository         = MfaRepository()
        self.preferences           = Preferences()

    def listProfiles(self, more=True):
        # defaultProfileAccessKey = ""
        # defaultCredential       = self.credentialsRepository.searchByQuery(where('default') == True)
        # if defaultCredential and len(defaultCredential) > 0:
        #    defaultProfileAccessKey = defaultCredential[0]["accessKey"]

        activeProfile = os.environ['AWS_PROFILE'] if 'AWS_PROFILE' in os.environ else None
        tableArgs = TableArgs()
        # Hightlight the current Profile
        if activeProfile:
           tableArgs.setArguments("| " + activeProfile + " ")
        header = ["#","Profile","Access Key", "Secret Key", "Region", "Account", "MFA Serial"]
        if more:
            header.append("Role Name")
            header.append("Role Arn")
        prettyTable = PrettyTable(header)

        idx = 0
        for credential in self.credentialsRepository.all():
            idx += 1

            profileName   = credential['profile']
            account       = str(credential["account"])
            accessKey     = credential['accessKey']
            secretKey     = "*".ljust(5,"*") + credential['secretKey'][:5]
            region        = ""
            configProfile = self.searchConfigForProfile(profileName)
            if configProfile and "region" in configProfile:
               region = configProfile["region"]


            mfaDevices = self.mfaRepository.searchByQuery(where('profile') == profileName)
            addSeparator  = False
            if more:
                listRoles = self.roleRepository.searchByQuery(Query().profile == profileName)
                if len(listRoles) > 0:
                    addSeparator = True
                    if len(mfaDevices) > len(listRoles):
                        for idxMfa, mfaDevice in enumerate(mfaDevices):
                            mfa      = f"{mfaDevice['mfa-device']}"
                            roleName = ""
                            roleArn  = ""
                            if (idxMfa+1) <= len(listRoles):
                                roleName = listRoles[idxMfa]['role-name']
                                roleArn  = listRoles[idxMfa]['role-arn']
                            columns = [ idx, profileName, accessKey, secretKey, region, account, mfa, roleArn, roleName]
                            prettyTable.addRow(columns)
                    else:    
                        for idxRole, role in enumerate(listRoles):
                            mfa      = ""
                            roleName = role['role-name']
                            roleArn  = role['role-arn']
                            if (idxRole+1) <= len(mfaDevices):
                               mfa  = f"{mfaDevices[idxRole]['mfa-device']}" 
                            columns = [ idx, profileName, accessKey, secretKey, region, account, mfa, roleArn, roleName]
                            prettyTable.addRow(columns)
                else:
                    if len(mfaDevices) > 0:
                        addSeparator = True if len(mfaDevices) > 1 else False
                        for idxMfa, mfaDevice in enumerate(mfaDevices):
                            mfa  = f"{mfaDevice['mfa-device']}"
                            columns = [ idx, profileName, accessKey, secretKey, region, account, mfa, "", ""]
                            prettyTable.addRow(columns)
                    else:
                        columns = [ idx, profileName, accessKey, secretKey, region, account, "", "", ""]
                        prettyTable.addRow(columns)
                if addSeparator:
                    prettyTable.addSeparatorGroup()    
            else:
                if len(mfaDevices) > 0:
                    addSeparator = True if len(mfaDevices) > 1 else False
                    for idxMfa, mfaDevice in enumerate(mfaDevices):
                        mfa  = f"{mfaDevice['mfa-device']}"
                        columns = [ idx, profileName, accessKey, secretKey, region, account, mfa]
                        prettyTable.addRow(columns)
                else:
                    addSeparator = False
                    columns = [ idx, profileName, accessKey, secretKey, region, account, ""]
                    prettyTable.addRow(columns)
                if addSeparator:
                    prettyTable.addSeparatorGroup()

        prettyTable.sortByColumn(int(tableArgs.sortCol) - 1)
        prettyTable.ascendingOrder(not tableArgs.desc)
        output = "\n" + Style.RESET + prettyTable.printMe("listProfiles",False,tableArgs)
        Messages.showMessage("PROFILES", output)
    
    def searchConfigForProfile(self, profileName):
        profileConfigurations = self.configRepository.findByProfile(profileName)
        return profileConfigurations["configurations"] if profileConfigurations else None
        