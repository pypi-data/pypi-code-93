import re
from .logger import Logger
from .config import Configs
from .providers import StoreProvider, Providers
from .stages import Stages
from .constants import *
from .exceptions import *


REGEX_PATTERN = r"^[a-zA-Z][.a-zA-Z0-9_-]*[a-zA-ZA-Z0-9]$"

class SecretProvider(StoreProvider):
    def list(self, project, application, stage, uninherited=False, decrypt=False, filter=None):
        raise NotImplementedError()
    def add(self, project, application, stage, key, value):
        raise NotImplementedError()
    def get(self, project, application, stage, key, decrypt=False, revision=None):
        raise NotImplementedError()
    def history(self, project, application, stage, key, decrypt=False):
        raise NotImplementedError()
    def delete(self, project, application, stage, key):
        raise NotImplementedError()

class SecretManager():

    def validate_key(self, key):
        Logger.info(f"Validating secret key '{key}'...")
        if not key:
            raise DSOException(MESSAGES['KeyNull'])
        if key == 'dso' or key.startswith('dso.'):
            raise DSOException(MESSAGES['DSOReserverdKey'].format(key))
        if not re.match(REGEX_PATTERN, key):
            raise DSOException(MESSAGES['InvalidKeyPattern'].format(key, REGEX_PATTERN))
        if '..' in key:
            raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '..'))

    def list(self, stage, uninherited=False, decrypt=False, filter=None):
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.SecretProvider()
        Logger.info(f"Start listing SSM secrets: project={project}, application={application}, stage={Stages.shorten(stage)}")
        return provider.list(project, application, stage, uninherited, decrypt, filter)

    def add(self, stage, key, value):
        self.validate_key(key)
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.SecretProvider()
        Logger.info(f"Start adding secret '{key}': project={project}, application={application}, stage={Stages.shorten(stage)}")
        return provider.add(project, application, stage, key, value)

    def get(self, stage, key, decrypt=False, revision=None):
        # self.validate_key(key)
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.SecretProvider()
        Logger.info(f"Start getting the value of secret '{key}': project={project}, application={application}, stage={Stages.shorten(stage)}")
        return provider.get(project, application, stage, key, decrypt, revision)

    def history(self, stage, key, decrypt=False):
        # self.validate_key(key)
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.SecretProvider()
        Logger.info(f"Start getting the history of secret '{key}': project={project}, application={application}, stage={Stages.shorten(stage)}")
        return provider.history(project, application, stage, key, decrypt)

    def delete(self, stage, key):
        # self.validate_key(key)
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.SecretProvider()
        Logger.info(f"Start deleting secret '{key}': project={project}, application={application}, stage={Stages.shorten(stage)}")
        return provider.delete(project, application, stage, key)

Secrets = SecretManager()
