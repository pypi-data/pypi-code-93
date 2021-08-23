# coding=utf-8
#
# Author: Ualter Otoni Pereira
# ualter.junior@gmail.com
#
import os
import logging
import sys
import re
import atexit 
from os.path import expanduser
import signal
import datetime, uuid
from datetime import timezone

from shutil import which
from boto3.session import Session
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
from awsee.profilemanager import ProfileManager
from awsee.awseestate import AwsSeeState
from awsee.sessioninfo import SessionInfo
from awsee.general import *

LOG = logging.getLogger("app." + __name__)
LOG.setLevel(logging.DEBUG)
FILE_LOG = os.path.join(expanduser("~"),".awsee","log")

signal.signal(signal.SIGINT, signal.SIG_DFL)

class AwsSeePy:

    def __init__(self):
        myhomeFolder = os.path.join(expanduser("~"),".awsee")
        if not os.path.exists(myhomeFolder):
           os.makedirs(myhomeFolder)

        if not os.path.exists(TEMP_CACHE_FOLDER):
            os.makedirs(TEMP_CACHE_FOLDER)

        self.mfaToken = None

        #LogManager().LOG.info("Starting...")
        self.credentialsRepository = CredentialsRepository()
        self.configRepository      = ConfigRepository()
        self.roleRepository        = RoleRepository()
        self.mfaRepository         = MfaRepository()
        self.preferences           = Preferences()
        self.executeFunction       = None
        self.myPidFile             = None

        self.checkDBs()

    def checkDBs(self):
        # Correct the missing 'id' field for MFAs
        for m in self.mfaRepository.all():
            if 'id' not in m:
               m['id'] = str(uuid.uuid4())
               self.mfaRepository.databaseConnection().update(m)

    def loadConfigProfiles(self):
        fileConfig  = expanduser("~") + "/.aws/config"

        if not os.path.exists(fileConfig):
            LogManager().LOG.warning("No file {} was found".format(fileConfig))
            return None
       
        configProfiles           = {}
        configProfiles["config"] = []
        currentProfileName = None 
        keys               = {}
        with open(fileConfig,'r') as fcfg:
            for line in fcfg.readlines():
                line = line.lstrip().rstrip()
                if line.lstrip().rstrip().startswith("["):
                   if currentProfileName:
                       configProfiles["config"].append({
                           "profile": currentProfileName,
                           "configurations": keys
                       })
                       keys = {}
                   # Read Current    
                   currentProfileName = Utils.cleanBreakLines(line).replace("[","").replace("]","")     
                else:
                   if Utils.cleanBreakLines(line).lstrip().rstrip() != "":
                      line = Utils.cleanBreakLines(re.sub('\s',"",line))
                      kv   = line.split("=")
                      keys[kv[0]] = kv[1]
            if currentProfileName:
               configProfiles["config"].append({
                   "profile": currentProfileName,
                   "configurations": keys
               })

        # Check if needs updates/inserts
        for c in configProfiles["config"]:
            dbRecordProfile = self.configRepository.findByProfile(c["profile"])
            # Insert the new one
            if not dbRecordProfile:
                self.configRepository.insert(c)
            else:
                # Update if needed
                update = False
                for config in c["configurations"]:
                    if config not in dbRecordProfile or \
                       c["configurations"][config] != dbRecordProfile["configurations"][config]:
                       update = True
                if update:
                   self.configRepository.update(c, c["profile"])

    def loadProfiles(self):
        fileCredentials = expanduser("~") + "/.aws/credentials"

        if not os.path.exists(fileCredentials):
            LogManager().LOG.warning("No file {} was found".format(fileCredentials))
            Messages.showWarning("Credentials Not Found!",f" The file {Style.IBLUE}/.aws/credentials{Style.GREEN} was not found, did you install and configure your {Style.IBLUE}awscli{Style.GREEN}?")
            sys.exit()

        currentProfileName                   = None
        accessKey                            = None
        secretKey                            = None
        credentialsProfiles                  = {}
        credentialsProfiles["credentials"]   = []
        with open(fileCredentials,'r') as fcred:
            for line in fcred.readlines():
                if line.lstrip().rstrip().startswith("["):
                   if currentProfileName:
                       defaultProfile = False
                       if currentProfileName == self.preferences.defaultProfile:
                           defaultProfile = True
                       # SAVE Previous
                       credentialsProfiles["credentials"].append({
                           "profile": currentProfileName,
                           "accessKey": accessKey,
                           "secretKey": secretKey,
                           "default": defaultProfile
                       })
                   # Read Current    
                   currentProfileName = Utils.cleanBreakLines(line).replace("[","").replace("]","") 
                else:
                   if Utils.cleanBreakLines(line).lstrip().rstrip() != "":
                      line = Utils.cleanBreakLines(re.sub('\s',"",line))
                      kv   = line.split("=")
                      if   "aws_access_key_id" in kv[0].lower():
                         accessKey = kv[1]
                      elif "aws_secret_access_key" in kv[0].lower():
                         secretKey = kv[1]
            if currentProfileName:
                defaultProfile = False
                if currentProfileName == self.preferences.defaultProfile:
                    defaultProfile = True
                # SAVE Previous
                credentialsProfiles["credentials"].append({
                    "profile": currentProfileName,
                    "accessKey": accessKey,
                    "secretKey": secretKey,
                    "default": defaultProfile
                })            

        # Check if needs updates/inserts
        awsServices = AwsServices()
        for c in credentialsProfiles["credentials"]:
            dbRecordProfile = self.credentialsRepository.findByProfile(c["profile"])
            # Insert the new one
            if not dbRecordProfile:
                account   = ""
                # Read Account and MFA Devices of the Profile at AWS
                try:
                    account = awsServices.getAccountOwner(c["profile"])["Account"]
                    for m in awsServices.getMFADevices(c["profile"])["MFADevices"]:
                        mfaRecord = self.mfaRepository.searchByQuery(Query().mfaDevice == m["SerialNumber"])
                        if not mfaRecord or len(mfaRecord) < 0:
                            self.mfaRepository.insert({
                                "profile": c["profile"],
                                "mfa-device": m["SerialNumber"],
                                "user-name": m["UserName"]
                            })
                except:
                    LogManager().LOG.warning(f"Not able to retrieve the MFA Devices for the {c['profile']}, probably some police might be blocking by the lack of MFA Token")
                c["account"] = account
                self.credentialsRepository.insert(c)
            else:
                # Check if needs to update the record (credentials change)
                if dbRecordProfile["accessKey"] != c["accessKey"]  or \
                   dbRecordProfile["secretKey"] != c["secretKey"]  or \
                   dbRecordProfile["default"]   != c["default"]:
                   # UPDATEIT
                   self.credentialsRepository.update(c, c["profile"])
                   
                # Try to Update its MFA Devices 
                # Removed to avoid remote connect all the time when the command --list is called
                #  TODO: Check to create a new function later, like --update-mfa-devices to explicitly update 
                #  the local credentials with MFA Devices remotely (if not blocked by polices)
                refreshMFA = False
                if refreshMFA:
                    try:
                        for m in awsServices.getMFADevices(c["profile"])["MFADevices"]:
                            mfaRecord = self.mfaRepository.searchByQuery(where('mfa-device') == m["SerialNumber"])
                            # Add a new MFA Device found at his/her Account (not in the MFA Device Repository yet)
                            if not mfaRecord or len(mfaRecord) < 0:
                                self.mfaRepository.insert({
                                    "profile": c["profile"],
                                    "mfa-device": m["SerialNumber"],
                                    "user-name": m["UserName"]
                                })
                    except:
                        pass

    def synchronize(self):
        printPy("")
        Messages.showStartExecution("Wait, synchronizing...")
        self.credentialsRepository.purge()
        self.configRepository.purge()
        self.loadProfiles()
        self.loadConfigProfiles()
        Messages.showStartExecution("Synchronization done!             ")
        printPy("")
    
    def listProfiles(self, more):
        profileManager = ProfileManager()
        profileManager.listProfiles(more)

    def addRole(self):
        roleManager = RoleManager()
        roleManager.addRole()

    def listRoles(self, filterByProfile):
        roleManager = RoleManager()
        roleManager.listRoles(filterByProfile)

    def removeRole(self, numberInList, roleName):
        roleManager = RoleManager()
        roleManager.removeRole(numberInList, roleName)
    
    def addMFADevice(self):
        mfaManager = MFAManager()
        mfaManager.addMfa()

    def listMFADevices(self, filterByProfile):
        mfaManager = MFAManager()
        mfaManager.listmfaDevices(filterByProfile)

    def removeMFADevice(self, numberInList):
        mfaManager = MFAManager()
        mfaManager.removeMFADevice(numberInList)

    def assumeRole(self, assumeRoleName, nameProfile=None, mfaToken=None):
        roleRecords = self.roleRepository.searchByQuery(where('role-name') == assumeRoleName)
        if not roleRecords or len(roleRecords) < 1:
           Messages.showWarning("Role not found!",f"     Role with the name {Style.IBLUE}{assumeRoleName}{Style.GREEN} was not found")
           sys.exit()

        role           = roleRecords[0]
        sessionManager = SessionManager()

        sessionInfo = SessionInfo()
        sessionInfo.role     = role
        sessionInfo.profile  = nameProfile
        sessionInfo.mfaToken = mfaToken

        output, sessionInfo = sessionManager.assumeRole(sessionInfo)
        if output:
           output = Utils.removeCharsColors(output) if self.preferences.noColor else output
           printPy(output)
        
        if sessionInfo and sessionInfo.hasStsToken:
           sessionManager.setCreateSessionAtLocalOS(sessionInfo, self.myPidFile) 

    def startAWSSessionWithMFAToken(self, nameProfile=None, mfaToken=None, assumeRole=None):
        if not nameProfile:
           # If not informed, use the Default Profile
           listCredentials = self.credentialsRepository.searchByQuery(where('default') == True)
           if not listCredentials or len(listCredentials) < 1:
               Messages.showWarning("Default profile not defined!")
               sys.exit()
           credentials = listCredentials[0]
        else:
            # Get the Profile using the name informed
            credentials = self.credentialsRepository.findByProfile(nameProfile)
            if not credentials:
               Messages.showWarning(f"Profile {Style.IBLUE}{nameProfile}{Style.GREEN} not defined!")
               sys.exit()

        mfa = self.mfaRepository.findByProfile(credentials['profile'])
        if not mfa:
           Messages.showWarning(f"MFA for the profile {credentials['profile']} not found!")
           sys.exit()

        role = None
        if assumeRole:
            roles = self.roleRepository.searchByQuery(where('role-name') == assumeRole)
            if not roles or len(roles) < 1:
               Messages.showWarning(f"Role {assumeRole} not found!")
               sys.exit()
            role = roles[0]

        sessionManager = SessionManager()

        sessionInfo = SessionInfo()
        sessionInfo.credentials = credentials
        sessionInfo.mfa         = mfa
        sessionInfo.role        = role
        sessionInfo.mfaToken    = mfaToken

        output, sessionInfo = sessionManager.startAWSSessionWithMFA(sessionInfo)
        if output:
           output = Utils.removeCharsColors(output) if self.preferences.noColor else output
           printPy(output)
        
        if sessionInfo and sessionInfo.hasStsToken:
           sessionManager.setCreateSessionAtLocalOS(sessionInfo, self.myPidFile)
    
    def startAWSSession(self, nameProfile, nameRole=None):
        credentials = self.credentialsRepository.findByProfile(nameProfile)
        if not credentials:
           Messages.showWarning(f"Profile {Style.IBLUE}{nameProfile}{Style.GREEN} not defined!")
           sys.exit()

        # Check if the asked profile has a MFA Device associate with it, if yes ask for a MFA Token
        mfaToken = None
        mfa      = self.mfaRepository.findByProfile(nameProfile)
        if mfa:
           label = f"\n{Style.IBLUE} ->> {Style.GREEN}The profile {Style.IBLUE}{nameProfile} {Style.GREEN}has an MFA Device associated\n\n \
    Please enter a MFA Token.......:{Style.IBLUE}"
           printPy(label, end=' ') 
           while True:
               mfaToken = input()
               if self.checkMFATokenValid(mfaToken) or not mfaToken:
                  break
               Messages.showWarning(f"Invalid Token! Try again or [{Style.IBLUE}BLANKS{Style.GREEN}] to exit...")
               printPy(f"     {Style.GREEN}Please enter a MFA Token.......:{Style.IBLUE}", end=' ')
        
        role = None
        if nameRole:
            roles = self.roleRepository.searchByQuery(where('role-name') == nameRole)
            if roles and len(roles) > 0:
                role = roles[0]

        sessionManager = SessionManager()
        if   not mfaToken and not nameRole:
           # No need for MFA Token and no Role So, add the default credentials direct in the Session
           sessionInfo = SessionInfo()
           sessionInfo.credentials = credentials
           output, sessionInfo = sessionManager.startAWSSession(sessionInfo)
        elif not mfaToken and nameRole:
           # No need for MFA, but has Role, let's assume the Role
           sessionInfo = SessionInfo()
           sessionInfo.credentials = credentials
           sessionInfo.role        = role
           #sessionInfo.profile     = credentials["profile"]
           output, sessionInfo = sessionManager.assumeRole(sessionInfo) 
        else:
           # With MFA Token Profile and Role (if it is there)
           sessionInfo = SessionInfo()
           sessionInfo.credentials = credentials
           sessionInfo.role        = role
           sessionInfo.mfaToken    = mfaToken
           sessionInfo.mfa         = mfa
           output, sessionInfo     = sessionManager.startAWSSessionWithMFA(sessionInfo) 

        if output:
           output = Utils.removeCharsColors(output) if self.preferences.noColor else output
           printPy(output)
        
        if sessionInfo and sessionInfo.stsToken:
           sessionManager.setCreateSessionAtLocalOS(sessionInfo, self.myPidFile) 
        
    def syntax(self, short=False):
        printPy("")
        functions = Functions()
        functions.showUsage(short)
        functions.showFunctions(short)
    
    def askForMFAToken(self):
        defaultProfile = self.credentialsRepository.searchByQuery(where("default") == True)
        if defaultProfile and len(defaultProfile) > 0:
            profile = defaultProfile[0]
            mfa     = self.mfaRepository.findByProfile(profile['profile'])
            if mfa:
                printPy(f"{Style.GREEN}")
                printPy(f"Profile.......: {Style.IBLUE}{profile['profile']}{Style.GREEN}")
                printPy(f"Account.......: {Style.IBLUE}{profile['account']}{Style.GREEN}")
                printPy(f"{Style.GREEN}MFA Token.....:{Style.IBLUE}", end=' ')
                while True:
                    response = input()
                    if response == "":
                        printPy("")
                        sys.exit()
                    if self.checkMFATokenValid(response):
                        break
                    Messages.showWarning(f"Invalid Token! Try again or [{Style.IBLUE}BLANKS{Style.GREEN}] to exit...")
                    printPy(f"{Style.GREEN}Profile.......: {Style.IBLUE}{profile['profile']}{Style.GREEN}")
                    printPy(f"Account.......: {Style.IBLUE}{profile['account']}{Style.GREEN}")
                    printPy(f"{Style.GREEN}MFA Token.....:{Style.IBLUE}", end=' ')
                self.startAWSSessionWithMFAToken(profile['profile'], response, None)
            else:
                self.startAWSSession(profile['profile'])
            printPy("")
            sys.exit()
        else:
            Messages.showError("Default profile not defined!")
            self.syntax()
        self.syntax()
        sys.exit()

    def bootStrap(self):
        SessionManager().createAliasFile()

    def start(self):
        #executeFunction = False
        args = sys.argv

        self.bootStrap()

        # Remove PID File if found
        for a in args:
            found = re.search("pid_[0-9]{1,}_pid",a) 
            if found:
                self.myPidFile = found.group()
                args.remove(a)

        if len(args) < 2:
           # In case no argument was informed, let's use the default profile
           # and if needed MFA Token lets request it
           self.askForMFAToken()

        # Check for -nt / --new-terminal
        if "-nt" in args or "--new-terminal" in args:
            AwsSeeState.NEW_TERMINAL = True
            # Remove this "-nt or --new-terminal" from args
            if "-nt" in args:
               args.remove("-nt")
            if "--new-terminal" in args:
               args.remove("--new-terminal")
            # in case there's nothing more, ask for the MFA Token
            if len(args) < 2:
                self.askForMFAToken()

        functions = Functions()
        if "-h" in args or "--help" in args:
            short = True if "-h" in args else False
            if len(args) > 2:
               f = functions.getFunctionByArgumentIdentifier(args[2])
               output = functions.showFunction(f)
               output = Utils.removeCharsColors(output) if self.preferences.noColor else output
               printPy(output)
            else:
               self.syntax(short)
            sys.exit()
        
        if "-u" in args or "--usage" in args:
            functions.showUsage(False)
            sys.exit()
        
        if "-v" in args or "--version" in args:
            printPy("")
            functions.showVersion()
            sys.exit()
        
        self.loadProfiles()
        self.loadConfigProfiles()

        args                 = args[1:]                          # Discard the first argument (our python function name)
        self.executeFunction = self.parseArgsFindFunction(args)  # Identify which function by the arguments/identifiers (-l --list, etc.)

        if  functions.INFO == self.executeFunction:
            self.showInfo()
        
        elif  functions.ENV == self.executeFunction:
            SessionManager().showEnvironment()
        
        elif functions.CLEAN == self.executeFunction:
            SessionManager().cleanAwsSession()
        
        elif  functions.LIST_PROFILES == self.executeFunction:
            more = True if "full" in args or "-lf" in args else False
            self.listProfiles(more)

        elif functions.SYNC == self.executeFunction:
            self.synchronize()

        elif functions.ADD_ROLE == self.executeFunction:
            self.addRole()

        elif functions.LIST_ROLES == self.executeFunction:
            filterByProfile = None
            if len(args) > 1:
               filterByProfile = args[1]
            self.listRoles(filterByProfile)

        elif functions.REMOVE_ROLE == self.executeFunction:
            numberInList = -1
            roleName     = None
            if len(args) > 1:
               if Utils.isNumber(args[1]):
                   numberInList = int(args[1])
               else:
                   roleName = args[1]
            else:
                Messages.showWarning("Missing parameter! At least one of them must be informed:")
                output = Functions().showFunction(Functions.REMOVE_ROLE)
                output = Utils.removeCharsColors(output) if self.preferences.noColor else output
                printPy(output)
                sys.exit()
            self.removeRole(numberInList, roleName)

        elif functions.ADD_MFA == self.executeFunction:
             self.addMFADevice()

        elif functions.LIST_MFAS == self.executeFunction:
             filterByProfile = None
             if len(args) > 1:
                filterByProfile = args[1]
             self.listMFADevices(filterByProfile)

        elif functions.REMOVE_MFA == self.executeFunction:
            numberInList = -1
            if len(args) > 1:
               if Utils.isNumber(args[1]):
                   numberInList = int(args[1])
            else:
                Messages.showWarning("Missing parameter for Remove MFA...")
                output = Functions().showFunction(Functions.REMOVE_MFA)
                output = Utils.removeCharsColors(output) if self.preferences.noColor else output
                printPy(output)
                sys.exit()
            self.removeMFADevice(numberInList)

        elif functions.ASSUME_ROLE == self.executeFunction:
            if len(args) > 1:
               role = args[1]
               self.assumeRole(role,None,None)
            else:
               Messages.showWarning("Missing [ROLE] parameter...")
               output = Functions().showFunction(Functions.ASSUME_ROLE)
               output = Utils.removeCharsColors(output) if self.preferences.noColor else output
               printPy(output)
               sys.exit()

        elif functions.START_SESSION == self.executeFunction:
            if len(args) > 1:
                profile = args[1]
                role    = args[3] if len(args) > 3 else None
                self.startAWSSession(nameProfile=profile, nameRole=role)
            else:
                Messages.showWarning("Missing [PROFILE] parameter...")
                output = Functions().showFunction(Functions.START_SESSION)
                output = Utils.removeCharsColors(output) if self.preferences.noColor else output
                printPy(output)
                sys.exit()

        elif functions.START_SESSION_MFA_TOKEN == self.executeFunction:
            # Parameters Already validated (if exists)
            mfaToken = args[0]
            profile  = args[2] if len(args) > 2 else None
            role     = args[4] if len(args) > 4 else None
            if not self.checkMFATokenValid(mfaToken):
                Messages.showWarning("Invalid Parameter!",f"    Is {Style.IBLUE}{mfaToken}{Style.GREEN} MFA Token?  Please, check it\n")
                sys.exit()
            self.startAWSSessionWithMFAToken(nameProfile=profile, mfaToken=mfaToken, assumeRole=role)
        else:
             self.exitWithMessageInvalidUsage()

    def parseArgsFunctionStartAWSSession(self, args):
        functions = Functions()

        # Check if a profile was passed: "-p [profile] or -p [profile] -r [role]"
        role = None
        if len(args) > 1:
           if len(args) == 4:
               self.exitWithMessageInvalidUsage()
           # Here, It should be -p [PROFILE]    
           elif len(args) == 3:
              if args[1] == "-p":
                 profile = args[2]
              elif args[1] != "-p":
                 self.exitWithMessageInvalidUsage()
           # Here, It should be -p [PROFILE] -r [ROLE]
           elif len(args) == 5:     
               if   args[1] == "-p":
                    profile = args[2]
               if   args[3] == "-p":
                    profile = args[4] 
               if args[1] == "-r":
                    role = args[2]  
               if args[3] == "-r":
                    role    = args[4]
               if (not profile or profile == "") or (not role or role == ""):
                   self.exitWithMessageInvalidUsage()
           else:
              Messages.showError(f"Missing parameter profile [-p profile], check syntax with {Style.GREEN}awsee -h{Style.RESET}")
              sys.exit()

        # Start AWS Session with Default Profile
        return functions.START_SESSION_MFA_TOKEN
    
    def parseArgsFindFunction(self, args):
        functions = Functions()

        # Check if the First Argument is a Valid MFA Token (Six-Digit)  Obs: The lack of Arguments was already tested before
        isMFAToken = self.checkMFATokenValid(args[0])
        if isMFAToken:
           self.parseArgsFunctionStartAWSSession(args)

        #
        # Looking for an auxiliar functions (Add Role, Add MFA, List Profiles, Remove Role, Sync, etc.)
        #
        for arg in args:
            func = functions.getFunctionByArgumentIdentifier(arg)
            if func:
                # Check if there's a MFA Token Informed, if it is, the funcion asked was not START_SESSION only, the argument -p must be the first one
                if func == functions.START_SESSION:
                   if args[0] == "-p":
                      return func
                   else:
                      continue
                # Check if there's a MFA Token Informed, if it is, the funcion asked was not ASSUME_ROLE, it is START_SESSION_MFA_TOKEN
                if func == functions.ASSUME_ROLE:
                   if args[0] == "-r":
                      return func
                   else:
                      continue 
                return func

        return self.parseArgsFunctionStartAWSSession(args)

        

    def showInfo(self):
        if 'AWS_SEE' in os.environ:
            if os.environ['AWS_SEE'] == "CLOSED":
                Messages.showWarning("The AWSee Session was closed already!")
                sys.exit()
        else:
            Messages.showWarning("No AWSee Session was started in this terminal!")
            sys.exit()
        
        account      = os.environ['AWS_ACCOUNT'] if 'AWS_ACCOUNT' in os.environ else None
        user         = os.environ['AWS_USER_ARN'] if 'AWS_USER_ARN' in os.environ else None
        userId       = os.environ['AWS_USER_ID'] if 'AWS_USER_ID' in os.environ else None
        accessKey    = os.environ['AWS_ACCESS_KEY_ID'] if 'AWS_ACCESS_KEY_ID' in os.environ else None
        secretKey    = os.environ['AWS_SECRET_ACCESS_KEY'] if 'AWS_SECRET_ACCESS_KEY' in os.environ else None
        expiration   = os.environ['AWS_EXPIRATION'] if 'AWS_EXPIRATION' in os.environ else None
        profile      = os.environ['AWS_PROFILE'] if 'AWS_PROFILE' in os.environ else ""
        role         = os.environ['AWS_ROLE'] if 'AWS_ROLE' in os.environ else ""
        tokenNeeded  = os.environ['AWS_WITH_TOKEN'] if 'AWS_WITH_TOKEN' in os.environ else ""

        if (not account or account == "") and (profile and profile.strip() != ""):
            credential = self.credentialsRepository.findByProfile(profile)
            account = credential["account"]

        if expiration and expiration != "":
            expDate         = datetime.datetime.strptime(expiration,"%Y-%m-%d %H:%M:%S%z")

            if (expDate < datetime.datetime.now(timezone.utc)):

                #diff  = (datetime.datetime.now(timezone.utc) - expDate).seconds / 60
                diff   = Utils.time_to_expire(expDate)["HH:MM:SS"]
                Messages.showWarning(f"Your AWS Session expired {Style.IBLUE}{diff} {Style.IGREEN}ago\n    At {Style.IMAGENTA}{expiration}")

                profiles = self.credentialsRepository.searchByQuery(where("profile") == profile)
                if profiles and len(profiles) > 0:
                    # label = f"   {Style.GREEN}Would like to re-connect to profile {Style.IBLUE}{profiles[0]['profile']}"
                    # if role and role != "":
                    #     label += f" {Style.GREEN}role {Style.IBLUE}{role}{Style.GREEN}? [y/n]{Style.IBLUE}" 
                    # else:
                    #     label += f"{Style.GREEN}? [y/n]{Style.IBLUE}"
                    # printPy(label, end=' ')
                    # response = input()
                    # if response.lower() == "y":
                    if tokenNeeded:
                        printPy(f"   {Style.GREEN}MFA Token.........:{Style.IBLUE}", end=' ')
                        while True:
                            response = input()
                            if response == "":
                                printPy("")
                                sys.exit()
                            if self.checkMFATokenValid(response):
                                break
                            Messages.showWarning(f"Invalid Token! Try again or hit [{Style.IBLUE}ENTER{Style.GREEN}] to exit...")
                            printPy(f"   {Style.GREEN}MFA Token.........:{Style.IBLUE}", end=' ')
                        self.startAWSSessionWithMFAToken(profile,response,role if role != "" else None)
                        sys.exit()
                    else:
                        self.startAWSSession(profile)
                        sys.exit()
                    printPy("")
                sys.exit()
            
            #diff            = Utils.time_to_expire(expDate)["total_minutes"]
            #expirationLabel = f"{Style.GREEN}Expiration........: {Style.IBLUE}{expiration} ({Style.YELLOW}{diff:02.0f} {Style.IBLUE}minutes remaining)"
            diff            = Utils.time_to_expire(expDate)["HH:MM:SS"]
            expirationLabel = f"{Style.GREEN}Expiration........: {Style.IBLUE}{expiration} ({Style.YELLOW}{diff} {Style.IBLUE} remaining)"
        else:
            expirationLabel = None

        output  = f"\n{Style.IMAGENTA}#awsee{Style.GREEN}\n"
        output += f"=============================\n"
        output += f"      {Style.IMAGENTA}My AWSee Session{Style.GREEN}\n"
        output += f"=============================\n"
        if account:
            output += f"{Style.GREEN}Account...........: {Style.IBLUE}{account}\n"
        if user:
            output += f"{Style.GREEN}User..............: {Style.IBLUE}{user}\n"
        if userId:
            output += f"{Style.GREEN}User Id...........: {Style.IBLUE}{userId}\n"
        if profile:
            output += f"{Style.GREEN}Profile...........: {Style.IBLUE}{profile}\n"
        if role:
            output += f"{Style.GREEN}Role..............: {Style.IBLUE}{role}\n"
        if accessKey:
            output += f"{Style.GREEN}Access Key........: {Style.IBLUE}{accessKey}\n"
        if secretKey:
            secretKey = secretKey[:10] + "*".ljust(10,"*")
            output += f"{Style.GREEN}Secret Key........: {Style.IBLUE}{secretKey}\n"
        if expirationLabel:
            output += f"\n{Emoticons.pointRight()} {Style.GREEN}{Style.IBLUE}Your AWS Session will expires in {Style.YELLOW}{diff} {Style.IBLUE}\n{Emoticons.pointRight()} At {Style.IMAGENTA}{expiration}{Style.RESET}\n"
        output = Utils.removeCharsColors(output) if self.preferences.noColor else output
        printPy( output )

    def exitWithMessageInvalidUsage(self):
        Messages.showError(f"Invalid usage!\n     Please, check syntax with {Style.GREEN}awsee -h{Style.RESET}")
        sys.exit() 

    def checkMFATokenValid(self, token):
        f = re.findall("[0-9]{6}$",token)
        if len(f) > 0:
            return True
        return False

@atexit.register 
def goodbye(): 
    pass

def main():
    """Start AwsSe"""
    try:
        awsee = AwsSeePy()
        awsee.start()
    except KeyboardInterrupt:
        pass    
    except UnicodeEncodeError as e:
        if Utils.isWindows():
           output = f"\n{Style.IRED} --> {Style.IMAGENTA}UnicodeEncode Error{Style.GREEN}\n     If you are using GitBash at Windows\n     disable the use of emoticons at ~/.awsse/awsee.ini, {Style.IBLUE}emoticons-enabled = false{Style.RESET}\n\n"
           output = Utils.removeCharsColors(output) if Preferences().noColor else output
           printPy(output)

if __name__ == '__main__':
    main()




