
from awsee import general


class SessionInfo(object):

    def __init__(self):
        self._credentials         = None
        self._role                = None
        self._mfa                 = None
        self._callerIdentity      = None
        self._isBashEnv           = False
        self._scriptFileWin       = None
        self._scriptFileBash      = None
        self._stsToken            = None
        self._mfaToken            = None
        self._uuid                = None
        self._config              = None
        self._runOnGitBashWindows = False

    @property
    def isBashEnv(self):
        return self._isBashEnv
    @isBashEnv.setter
    def setBashEnv(self, value):
        self._isBashEnv = value

    @property
    def runGitBashOnWindows(self):
        return self._runOnGitBashWindows
    @runGitBashOnWindows.setter
    def setRunGitBashOnWindows(self, value):
        self._runOnGitBashWindows = value

    @property
    def scriptFile(self):
        if self._isBashEnv:
            return self._scriptFileBash
        return self._scriptFileWin
    
    @property
    def scriptFileWin(self):
        return self._scriptFileWin
    @scriptFileWin.setter
    def scriptFileWin(self, value):
        self._scriptFileWin = value

    @property
    def scriptFileBash(self):
        return self._scriptFileBash
    @scriptFileBash.setter
    def scriptFileBash(self, value):
        self._scriptFileBash = value
    
    @property
    def accessKey(self, returnOpt=None):
        return self.stsToken["AccessKeyId"] \
               if self.stsToken else returnOpt
    
    @property
    def secretKey(self, returnOpt=None):
        return self.stsToken["SecretAccessKey"] \
               if self.stsToken else returnOpt
    
    @property
    def hasSessionToken(self):
        return True if self._stsToken and "SessionToken" in self._stsToken else True
    @property
    def sessionToken(self, returnOpt=None):
        return self.stsToken["SessionToken"] \
               if self.stsToken else returnOpt

    @property
    def hasExpiration(self):
        return True if self._stsToken and "Expiration" in self._stsToken else False
    @property
    def expiration(self, returnOpt=None):
        return self.stsToken["Expiration"] \
               if self.stsToken else returnOpt
    
    @property
    def profile(self):
        return self._credentials["profile"]
    @profile.setter
    def profile(self, value):
        self._credentials = {}
        self._credentials["profile"] = value
    @property
    def hasProfile(self):
        return True if self._credentials and "profile" in self._credentials else False
    
    @property
    def role(self):
        return self._role
    @role.setter
    def role(self, value):
        self._role = value
    @property
    def hasRole(self):
        return True if self._role else False
    @property
    def roleName(self, returnOpt=None):
        return self._role['role-name'] \
               if self._role and 'role-name' in self._role else \
               returnOpt
    @property
    def roleArn(self, returnOpt=None):
        return self._role['role-arn'] \
               if self._role and 'role-arn' in self._role else \
               returnOpt
    @property
    def roleProfile(self, returnOpt=None):
        return self._role['profile'] \
               if self._role and 'profile' in self._role else \
               returnOpt
    
    @property
    def stsToken(self):
        return self._stsToken
    @stsToken.setter
    def stsToken(self, value):
        self._stsToken = value
    @property
    def hasStsToken(self):
        return True if self._stsToken else False
    
    @property
    def mfaToken(self):
        return self._mfaToken
    @mfaToken.setter
    def mfaToken(self, value):
        self._mfaToken = value
    @property
    def hasMfaToken(self):
        return True if self._mfaToken else False
    
    @property
    def config(self):
        return self._config
    @config.setter
    def config(self, value):
        self._config = value
    @property
    def hasConfig(self):
        return True if self._config else False
    
    @property
    def mfa(self):
        return self._mfa
    @mfa.setter
    def mfa(self, value):
        self._mfa = value
    @property
    def mfaDevice(self, returnOpt=None):
        return self._mfa['mfa-device'] \
               if self._mfa and 'mfa-device' in self._mfa else \
               returnOpt
    
    @property
    def uuid(self):
        return self._uuid
    @uuid.setter
    def uuid(self, value):
        self._uuid = value
    
    @property
    def credentials(self):
        return self._credentials
    @credentials.setter
    def credentials(self, value):
        self._credentials = value
    
    @property
    def callerIdentity(self):
        return self._callerIdentity
    @callerIdentity.setter
    def callerIdentity(self, value):
        self._callerIdentity = CallerIdentity(value)

    
class CallerIdentity:
    def __init__(self, callerIdentity):
        self._userId  = callerIdentity['UserId']
        self._account = callerIdentity['Account']
        self._arn     = callerIdentity['Arn']
    
    @property
    def userId(self):
        return self._userId
    @property
    def account(self):
        return self._account
    @property
    def arn(self):
        return self._arn
    