import os, uuid
import datetime
from boto3 import session
from botocore import credentials
from awsee.awseestate import AwsSeeState
from arnparse import arnparse
from os.path import expanduser
from awsee.logmanager import LogManager
from awsee.preferences import Preferences
from awsee.functions import Functions
from awsee.awsservices import AwsServices
from awsee.messages import Messages
from awsee.tableargs import TableArgs
from awsee.prettytable import PrettyTable
from awsee.style import Style
from awsee.emoticons import Emoticons
from awsee.utils import Utils
from tinydb import Query, where
from shutil import which
from awsee.repository import Repository, CredentialsRepository, ConfigRepository, RoleRepository, MfaRepository
from awsee.general import *
from awsee.sessioninfo import SessionInfo, CallerIdentity
from awsee.aws_credentials_parser import add_awsee_to_credentials

class SessionManager:

    SCRIPTS_PREFIX_NAME_FILE = "set-awssession-"

    def __init__(self):
        self.credentialsRepository = CredentialsRepository()
        self.roleRepository        = RoleRepository()
        self.mfaRepository         = MfaRepository()
        self.preferences           = Preferences()

    # Assume a Role
    #def assumeRole(self, role, profile=None, mfaToken=None):
    def assumeRole(self, sessionInfo: SessionInfo):
        aws = AwsServices()
        
        stsToken, callerIdentity = aws.assumeRole(sessionInfo.roleArn, sessionInfo.profile, sessionInfo.mfaToken)
        if not stsToken:
            return None, None
        sessionInfo.stsToken       = stsToken["Credentials"]
        sessionInfo.callerIdentity = callerIdentity
        sessionInfo.profile        = sessionInfo.roleProfile
        
        return self.createAWSSessionOnTerminalUser(sessionInfo)
    
    # Open Session using MFA (default or other profile)
    def startAWSSession(self, sessionInfo: SessionInfo):
        aws = AwsServices()

        _stsToken                                   = {}
        _stsToken["Credentials"]                    = {}
        _stsToken["Credentials"]["AccessKeyId"]     = sessionInfo.credentials['accessKey']
        _stsToken["Credentials"]["SecretAccessKey"] = sessionInfo.credentials['secretKey']
        _stsToken["Credentials"]["SessionToken"]    = ""
        _stsToken["Credentials"]["Expiration"]      = ""

        callerIdentity = aws.getCallerIdentity(_stsToken)

        sessionInfo.stsToken       = _stsToken["Credentials"]
        sessionInfo.callerIdentity = callerIdentity

        return self.createAWSSessionOnTerminalUser(sessionInfo)

    # Open Session (other profile - no need MFA)
    #def startAWSSessionWithMFA(self, profile, mfa, mfaToken, role=None):
    def startAWSSessionWithMFA(self, sessionInfo: SessionInfo):
        aws = AwsServices()
        
        stsTokenSession, callerIdentitySession = aws.getSessionToken(mfaSerial=sessionInfo.mfaDevice, mfaToken=sessionInfo.mfaToken, profile=sessionInfo.profile)
        if not stsTokenSession:
            return None, None

        if sessionInfo.hasRole:
           # If a Role was also passed, 
           # Initiate a session the the Profile given, and using it, immediately, create a Session with the Role passed
           stsTokenSessionRole, callerIdentitySessionRole = aws.startSessionWithTokenAndAssumeRole(stsTokenSession, sessionInfo.roleArn)
           sessionInfo.stsToken                           = stsTokenSessionRole["Credentials"]
           sessionInfo.callerIdentity                     = callerIdentitySessionRole
        else:
           sessionInfo.stsToken       = stsTokenSession["Credentials"]
           sessionInfo.callerIdentity = callerIdentitySession
        
        return self.createAWSSessionOnTerminalUser(sessionInfo)

    def createAWSSessionOnTerminalUser(self, sessionInfo: SessionInfo):
        output                     = None
        fileNamerole               = "" if not sessionInfo.hasRole else "_" + sessionInfo.roleName.replace(" ","_").lower()
        fileNameProfile            = "" if not sessionInfo.profile else sessionInfo.profile.replace(" ","_")
        roleTitle                  = "" if not sessionInfo.hasRole else f"Role: {sessionInfo.roleName.replace('_','')}" 
        windowTitle                = f"AWSEE Profile: {fileNameProfile}  {roleTitle}"
        sessionInfo.scriptFileWin  = f"{self.SCRIPTS_PREFIX_NAME_FILE}{fileNameProfile}{fileNamerole}.bat"
        sessionInfo.scriptFileBash = f"{self.SCRIPTS_PREFIX_NAME_FILE}{fileNameProfile}{fileNamerole}.sh"
        

        # Check if Config was loaded, otherwise load it if exists
        if not sessionInfo.hasConfig:
           sessionInfo.config = ConfigRepository().findByProfile(sessionInfo.profile)

        if Utils.isWindows():
            terminalCommand            = self.preferences.windows.terminalCommand
            sessionInfo.setBashEnv     = False
            
            # Check if there's a Terminal Commmand Set
            if AwsSeeState.NEW_TERMINAL:
                if not terminalCommand or terminalCommand.lstrip().rstrip() == "":
                    outputWin, environmentsWin = self.createEnvironment(sessionInfo)
                    output = outputWin

                    # Check CMDER is installed (then use it)
                    if which("cmder") and os.environ['CMDER_ROOT'] != "":
                        os.system(f"start %CMDER_ROOT%\\vendor\\conemu-maximus5\\ConEmu.exe /icon \"%CMDER_ROOT%\\cmder.exe\" /title \"{windowTitle}\" /loadcfgfile \"%CMDER_ROOT%\\config\\ConEmu.xml\" /cmd cmd /k " + environmentsWin)
                    else:
                        # Last option (windows default cmd)
                        if which("cmd"):
                            os.system("start cmd.exe /c cmd /k" + environmentsWin)
                        else:
                            msg = f"""\n{Style.GREEN}    Please set a {Style.IBLUE}terminal-command{Style.GREEN} at your {Style.IBLUE}~/.awsee/awsee.ini{Style.GREEN}, WINDOWS section in order \n    to open a Terminal ready to use with your AWS Session Token configured.
                            \n    Example: \n    {Style.IBLUE}[WINDOWS]\n    terminal-command = {Style.IGREEN}d:\Program Files\Git\git-bash.exe{Style.RESET}
                            """
                            Messages.showError("No Terminal Found (CMDER or CMD)",msg)
                            return None, None
                else:
                    if "git-bash.exe" in terminalCommand or "sh.exe" in terminalCommand:
                        sessionInfo.setBashEnv             = True
                        sessionInfo.setRunGitBashOnWindows = True  #To ask to set the path harcoded to the external scripts ~/.awsee/... otherwise it wont't find C:\User\...  when open the Shell Window
                        outputBash, environmentsBash       = self.createEnvironment(sessionInfo)
                        output = outputBash

                        os_command = ""
                        if "git-bash.exe" in terminalCommand:
                            os_command = f"start {terminalCommand} --needs-console --no-hide --command=usr\\bin\\bash.exe --login -i -c \"sh -c 'source {environmentsBash}; exec sh'\""
                        elif "sh.exe" in terminalCommand:
                            os_command = f"start {terminalCommand} --login -i -l -c \"sh -c 'source {environmentsBash}; exec sh'\""
                        else:
                            msg = f"""\n{Style.GREEN}    Please check the {Style.IBLUE}terminal-command{Style.GREEN} set at your {Style.IBLUE}~/.awsee/awsee.ini{Style.GREEN}, WINDOWS section in order \n    to open a Terminal ready to use with your AWS Session Token configured.
                            \n    Example: \n    {Style.IBLUE}[WINDOWS]\n    terminal-command = {Style.IGREEN}d:\Program Files\Git\sh.exe{Style.RESET}"""
                            Messages.showError(f"Terminal Command set \"{terminalCommand}\" not supported (Use git-bash.exe, sh.exe or let it blank, for system default",msg)
                            return None, None
                        os.system(os_command)
                    elif "wt" in terminalCommand:
                        outputWin, environmentsWin = self.createEnvironment(sessionInfo)
                        output = outputWin
                        os.system("wt -d c:\ cmd /k " + environmentsWin)

            else:
                # Windows (Where Am I? CMD/CDMER or GitBash (analysing the present of environment variable SHELL, if it there, so it is GitBash))
                if Utils.isRunningOnGitBash():
                    sessionInfo.setBashEnv       = True
                    outputBash, environmentsBash = self.createEnvironment(sessionInfo)
                    output = outputBash
                else:
                    sessionInfo.setBashEnv     = False
                    outputWin, environmentsWin = self.createEnvironment(sessionInfo)
                    output = outputWin

        else:
            # LINUX
            terminalCommand                = self.preferences.linux.terminalCommand
            sessionInfo.setBashEnv         = True
            outputLinux, environmentsLinux = self.createEnvironment(sessionInfo)
            output                         = outputLinux

            if AwsSeeState.NEW_TERMINAL:
                Messages.showWarning("New Terminal option not implemented here, yet!")
                sys.exit()
            #    if "cmd" in terminalCommand:
            #        # Using WSL (User inside Windows)
            #        sessionInfo.setBashEnv = False
            #        _, environmentsWin = self.createEnvironment(sessionInfo)
            #        printPy(environmentsWin)
            #        os.system("cmd.exe /c start cmd /k " + environmentsWin)
               
                

        return output, sessionInfo

    def cleanForEnvironmentVariables(self, isWindows) -> str:
        output = ""
        if isWindows:
           output += "set AWS_ACCESS_KEY_ID=\n"
           output += "set AWS_SECRET_ACCESS_KEY=\n"
           output += "set AWS_SESSION_TOKEN=\n"
           output += "set AWS_EXPIRATION=\n"
           output += "set AWS_SEE=CLOSED\n"
           output += "set AWS_WITH_TOKEN=\n"
           output += "set AWS_ROLE=\n"
           output += "set AWS_USER_ARN=\n"
           output += "set AWS_USER_ID=\n"
        else:
           output += "unset AWS_ACCESS_KEY_ID\n"
           output += "unset AWS_SECRET_ACCESS_KEY\n"
           output += "unset AWS_SESSION_TOKEN\n"
           output += "unset AWS_EXPIRATION\n"
           output += "unset AWS_ROLE\n"
           output += "unset AWS_WITH_TOKEN\n"
           output += "export AWS_SEE=CLOSED\n"
           output += "unset AWS_USER_ARN\n"
           output += "unset AWS_USER_ID\n"
        return output

    # Script to Help clean environment variables, etc. 
    def createCleanEnvironmentScript(self, scriptFile):
        if ".bat" in scriptFile:
            enviromentVariables = self.cleanForEnvironmentVariables(False).replace("\n","")
            cleanFileName = "clean.bat"
            content = f"""@ECHO OFF
{enviromentVariables}
DEL {self.SCRIPTS_PREFIX_NAME_FILE}*
            """
        else:
            enviromentVariables = self.cleanForEnvironmentVariables(True).replace("\n","")
            cleanFileName = "clean.sh"
            content = f"""{enviromentVariables}
rm {self.SCRIPTS_PREFIX_NAME_FILE}*
            """
        completePathFileName =  os.path.join(TEMP_CACHE_FOLDER,cleanFileName)
        with open(f"{completePathFileName}",'w') as fout:
            fout.write(content)

    # Create Contents, Script File for Environments Variables and Clipboard (Win and Bash)
    def createEnvironment(self, sessionInfo: SessionInfo):
        output           = self.createOutputStartSession(sessionInfo)
        self.addEnvironmentVariablesConfigurationToClipboard(sessionInfo)
        environments     = ""
        if AwsSeeState.NEW_TERMINAL:
            initFileContent  = self.createContentScriptFileStartSession(sessionInfo)

            with open(f"{os.path.join(TEMP_CACHE_FOLDER, sessionInfo.scriptFile)}",'w') as fout:
                fout.write(initFileContent)

            if sessionInfo.runGitBashOnWindows:
                #To ask to set the path of the external scripts to ~/.awsee/... (even though launched from CMDER) otherwise it wont't find C:\User\...  when open the Shell Window
                completePathFile = "~/.awsee/tmp/" + sessionInfo.scriptFile
                environments = completePathFile
            else:
                # Get the default format where it is running Shell or Windows
                completePathFile = os.path.join(TEMP_CACHE_FOLDER, sessionInfo.scriptFile)
                environments = f"\"{completePathFile}\""

            self.createCleanEnvironmentScript(completePathFile)
        return output, environments

    def calculateExpiresTime(self, expiration):
        result = Utils.time_to_expire(expiration)
        return f"{result['HH:MM:SS']}"

        # if expiration and expiration != "":
        #     diff      = (expiration - datetime.datetime.now().astimezone())
        #     if diff.seconds > 60:
        #         min  = int(diff.seconds / 60)
        #         secs = int(((diff.seconds / 60) - min) * 60)
        #         return "00:{:02d}:{:02d} minutes".format(min, secs)
        #     else:   
        #         return "00:00:{:02d} seconds".format(diff.seconds)
        # return ""

    #
    # This is the information to the user about his/her AWS Session opened, just informative
    #
    def createOutputStartSession(self, sessionInfo: SessionInfo):
        commandEnvSet = "set"
        executeScript = f"{sessionInfo.scriptFileWin}"
        if sessionInfo.isBashEnv:
            commandEnvSet = "export"
            executeScript = f"{sessionInfo.scriptFileBash}"

        diffLabel = self.calculateExpiresTime(sessionInfo.expiration)

        credential = self.credentialsRepository.findByProfile(sessionInfo.profile)
        awsProfile = f"{Style.GREEN}Profile................: {Style.IBLUE}{sessionInfo.profile}" if sessionInfo.hasProfile else ""
        awsRole    = f"{Style.GREEN}Role...................: {Style.IBLUE}{sessionInfo.roleName}" if sessionInfo.hasRole else ""
        awsAccount = f"{Style.GREEN}Account................: {Style.IBLUE}{credential['account']}"

        output  = "\n"
        output += f" {Style.IMAGENTA}#aswee\n"
        output += f" {Style.GREEN}======================="
        output += f"\n {Style.IMAGENTA}  >>> AWS SESSION <<<\n"
        output += f" {Style.GREEN}======================="
        if diffLabel:
           output += f"\n {Style.GREEN}Session will expires...: {Style.IBLUE}{diffLabel}"
        output += f"\n{Style.GREEN} {awsAccount}"
        output += f"\n{Style.GREEN} {awsProfile}"
        output += f"\n{Style.GREEN} {awsRole}"

        if AwsSeeState().NEW_TERMINAL:
            output += f"\n\n {Style.IBLUE}--> {Style.IMAGENTA}Session opened in another terminal..."

        output += f"{Style.RESET}"
        return output

    # This is the same AWS Session credentials information for the user in case he/she wants to open using the Clipboard
    def addEnvironmentVariablesConfigurationToClipboard(self, sessionInfo: SessionInfo):
        command = "set" if not sessionInfo.isBashEnv else "export"
        awsToken = f"{Style.GREEN}{command} AWS_SESSION_TOKEN{Style.WHITE}={Style.IBLUE}{sessionInfo.sessionToken}\r" if sessionInfo.hasSessionToken else ""
        # Add to Clipboard (SETs environmentsWin)
        forClipboard  = f"{command} AWS_ACCESS_KEY_ID={sessionInfo.accessKey}\r\n"
        forClipboard += f"{command} AWS_SECRET_ACCESS_KEY={sessionInfo.secretKey}\r\n"
        forClipboard += f"{awsToken}\r\n"
        forClipboard += f"{command} AWS_SEE=gG99USedshwRIVSe\r\n"
        if sessionInfo.isBashEnv:
           forClipboard += f"{command} AWS_EXPIRATION=\"{sessionInfo.expiration}\"\r\n"
        else:
           forClipboard += f"{command} AWS_EXPIRATION={sessionInfo.expiration}\r\n" 
        Utils.addToClipboard(forClipboard)

    # This is the content of a Script File (Bath or Bash) to opened a AWS Session with the credentials provided 
    def createContentScriptFileStartSession(self, sessionInfo: SessionInfo):
        initFileContent = self.createBashScriptFile(sessionInfo) if sessionInfo.isBashEnv else \
                          self.createCMDscriptFile(sessionInfo)
        return initFileContent

    def createCMDscriptFile(self, sessionInfo: SessionInfo):
        awsToken = f"set AWS_SESSION_TOKEN={sessionInfo.sessionToken}" if sessionInfo.hasSessionToken else ""
        roleEcho = f"ECHO.Role.........: {sessionInfo.roleName}" if sessionInfo.hasRole else ""
        roleSet  = f"{sessionInfo.roleName}" if sessionInfo.hasRole else " " 

        expirationLabel = self.calculateExpiresTime(sessionInfo.expiration)

        aliasLines  = ""
        for a in self.getAliasFileContent():
            aliasLines += a

        return f"""
        @ECHO OFF
        ECHO.#awsee
        ECHO.=============================
        ECHO.  AWSCLI Session Configured
        ECHO.=============================
        set AWS_ACCESS_KEY_ID={sessionInfo.accessKey}
        set AWS_SECRET_ACCESS_KEY={sessionInfo.secretKey}
        {awsToken}
        set AWS_EXPIRATION={sessionInfo.expiration:{"" if sessionInfo.hasExpiration else ""}}

        for /F "delims=" %%i in ('aws sts get-caller-identity') do (
            SET "string=%%i"
            echo %%i | findstr /C:"Account">nul && (
                SET ACCOUNT=%%i
            )
            echo %%i | findstr /C:"Arn">nul && (
                SET USERARN=%%i
            )
        )
        set ACCOUNT=%ACCOUNT:Account=%
        set ACCOUNT=%ACCOUNT::=%
        set ACCOUNT=%ACCOUNT:"=%
        set ACCOUNT=%ACCOUNT:,=%
        set ACCOUNT=%ACCOUNT: =%

        set USERARN=%USERARN: =%
        set USERARN=%USERARN:~7%
        set USERARN=%USERARN:"=%
        REM set USERARN=%USERARN:Arn=%
        REM set USERARN=%USERARN:,=%

        {aliasLines}
        
        set AWS_ACCOUNT=%ACCOUNT%
        set AWS_USER=%USERARN%
        set AWS_ROLE={roleSet}
        set AWS_SEE=gG99USedshwRIVSe

        ECHO.Expires at...: {expirationLabel}
        ECHO.Account......: %ACCOUNT%
        ECHO.User.........: %USERARN%
        {roleEcho} 
        ECHO.
        """

    def createBashScriptFile(self, sessionInfo: SessionInfo):
        awsToken = f"export AWS_SESSION_TOKEN={sessionInfo.sessionToken}" if sessionInfo.hasSessionToken else ""
        roleEcho = f"echo Role.........: {sessionInfo.roleName}" if sessionInfo.hasRole else " "
        roleSet  = f"{sessionInfo.roleName}" if sessionInfo.hasRole else " " 

        expirationLabel = self.calculateExpiresTime(sessionInfo.expiration)

        aliasLines = ""
        for a in self.getAliasFileContent():
            aliasLines += a
        
        return f"""
        #!/bin/sh
        echo 
        echo =============================
        echo   AWSCLI Session Configured
        echo =============================
        export AWS_ACCESS_KEY_ID={sessionInfo.accessKey}
        export AWS_SECRET_ACCESS_KEY={sessionInfo.secretKey}
        {awsToken}
        export AWS_EXPIRATION="{sessionInfo.expiration:{"" if sessionInfo.hasExpiration else ""}}"

        vlr="$(aws sts get-caller-identity)"
        account=$(echo "$vlr" | grep '"Account"' | sed s/\\"//g | sed s/,//g | sed s/"Account:"//g)
        arn=$(echo "$vlr" | grep '"Arn"' | sed s/\\"//g | sed s/,//g | sed s/"Arn:"//g )

        export AWS_ACCOUNT=$account
        export AWS_USER=$arn
        export AWS_ROLE={roleSet}
        export AWS_SEE=gG99USedshwRIVSe

        {aliasLines}

        echo Expires at...: "{expirationLabel}"
        echo Account......: $account
        echo User.........: $arn
        {roleEcho}
        echo
        """
    
    def createAliasFile(self):
        aliasPath = os.path.join(expanduser("~"),".awsee","alias")
        if not os.path.exists(aliasPath):
            os.makedirs(aliasPath)
        
        aliasFile = os.path.join(aliasPath,"alias_awsee.txt")
        if not os.path.exists(aliasFile):
            if Utils.isWindows():
                with open(aliasFile,'w') as fout:
                    fout.write("DOSKEY info=awsee -i\n")
                    fout.write("DOSKEY s3=aws s3 ls\n")
                    fout.write("DOSKEY ssmec2=aws ssm start-session --target \"i-\"\n")
                    fout.write("DOSKEY ec2=aws ec2 describe-instances --query Reservations[*].Instances[*].InstanceId --output table\n")
                    fout.write("DOSKEY calleridentity=aws sts get-caller-identity --output table\n")
            else:
                with open(aliasFile,'w') as fout:
                    fout.write("alias s3='aws s3 ls'\n")
                    fout.write("alias info='awsee -i'\n")
                    fout.write("alias info='aws ssm start-session --target \"i-\"'\n")
                    fout.write("alias ec2='aws ec2 describe-instances --query Reservations[*].Instances[*].InstanceId --output table'\n")
                    fout.write("alias calleridentity='aws sts get-caller-identity --output table'\n")
    
    def getAliasFileContent(self):
        aliasPath = os.path.join(expanduser("~"),".awsee","alias")
        aliasFile = os.path.join(aliasPath,"alias_awsee.txt")
        with open(aliasFile,'r') as fout:
            lines = list(fout)
        return lines

    def cleanAwsSession(self, showMessage=True):
        isWindows = True if Utils.isWindows() else False
        printOut(self.cleanForEnvironmentVariables(isWindows))
        if showMessage:
           Messages.showMessage("Session cleaned!")

    def setCreateSessionAtLocalOS(self, sessionInfo: SessionInfo, myPidFile: str=None):
        # If the user wants to save the temporary credentials also in the ~/.aws/credentials file under the [awsee] profile's name
        if self.preferences.append_awsee_to_crendentials:
            add_awsee_to_credentials(sessionInfo)

        uuidStr = str(uuid.uuid4()).replace("-","")

        os.environ["AWS_SEE"] = uuidStr
        sessionInfo.uuid = uuidStr

        command = "SET" 
        if sessionInfo.isBashEnv:
           command = "export"

        self.cleanAwsSession(False)

        # Let's clean before set another one (avoid conflicts)
        printOut(f"{command} AWS_ACCESS_KEY_ID={sessionInfo.accessKey}")
        printOut(f"{command} AWS_SECRET_ACCESS_KEY={sessionInfo.secretKey}")
        printOut(f"{command} AWS_SESSION_TOKEN={sessionInfo.sessionToken}")
        if sessionInfo.isBashEnv:
            printOut(f"{command} AWS_EXPIRATION='{sessionInfo.expiration}'")
        else:
            printOut(f"{command} AWS_EXPIRATION={sessionInfo.expiration}")
        printOut(f"{command} AWS_USER_ARN={sessionInfo.callerIdentity.arn}")
        printOut(f"{command} AWS_USER_ID={sessionInfo.callerIdentity.userId}")
        printOut(f"{command} AWS_SEE={uuidStr}")
        printOut(f"{command} AWS_PID={myPidFile if myPidFile else ''}")

        #TODO: Set if config has default region
        if sessionInfo.hasConfig:
            region = sessionInfo.config['configurations']['region']
            printOut(f"{command} AWS_REGION={region}")

        aliasLines = ""
        for a in self.getAliasFileContent():
            aliasLines += a + "\n"
        printOut(f"{aliasLines}")

        if sessionInfo.hasMfaToken:
            printOut(f"{command}  AWS_WITH_TOKEN=yes")
        if sessionInfo.hasProfile:
            printOut(f"{command}  AWS_PROFILE={sessionInfo.profile}")
        if sessionInfo.hasRole:
            printOut(f"{command}  AWS_ROLE={sessionInfo.roleName}")

    def showEnvironment(self):
        prettyTable = PrettyTable(["#","Variable","Value"])
        idx = 0
        for env in os.environ:
            if env.startswith("AWS_"):
                idx += 1
                value = os.environ[env]
                if "SESSION_TOKEN" in env:
                    value = Style.IMAGENTA + "*".ljust(10,"*") + Style.GREEN + value[250:] 
                prettyTable.addRow([idx,env,value])
        if idx < 1:
            prettyTable.addRow(["","",""])
        tableArgs = TableArgs()
        prettyTable.sortByColumn(int(tableArgs.sortCol) - 1)
        prettyTable.ascendingOrder(not tableArgs.desc)
        output = "\n" + Style.RESET + prettyTable.printMe("environmentVariablesAWsSession",False,tableArgs)
        Messages.showMessage("AWS Session Environment Variables", output)
