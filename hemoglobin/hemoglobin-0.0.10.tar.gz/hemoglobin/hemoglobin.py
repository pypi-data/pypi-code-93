from collections import namedtuple
from getpass import getpass
import os

from .grammarbot import HemoglobinGrammarBot as GrammarBotClient
from .files import HemoglobinFile

BaseConfig = namedtuple("Config", ["apikey", "paths", "language"])


class Config(BaseConfig):
    GRAMMARBOT_CLIENT_APIKEY_ENV_NAME = "GRAMMARBOT_CLIENT_APIKEY"
    GRAMMARBOT_LANGUAGE_ENV_NAME = "GRAMMARBOT_LANGUAGE"

    @classmethod
    def from_args(cls, args):
        apikey = args.apikey
        if not apikey:
            if cls.GRAMMARBOT_CLIENT_APIKEY_ENV_NAME in os.environ:
                apikey = os.environ[cls.GRAMMARBOT_CLIENT_APIKEY_ENV_NAME]
            else:
                apikey = getpass("Enter your API key: ")
                if not apikey:
                    print("GrammarBot API key is not defined.")
                    exit(1)
        language = args.language
        if not language:
            if cls.GRAMMARBOT_LANGUAGE_ENV_NAME in os.environ:
                language = os.environ[cls.GRAMMARBOT_LANGUAGE_ENV_NAME]
        return cls(apikey=apikey, paths=args.path, language=args.language)


class Hemoglobin(object):
    GRAMMARBOT_CLIENT = GrammarBotClient
    HEMOGLOBIN_FILE = HemoglobinFile

    ACCEPTABLE_FILE_EXTENSIONS = ["txt", "md"]

    @classmethod
    def from_config(cls, config):
        return cls(apikey=config.apikey, paths=config.paths, language=config.language)

    def __init__(self, apikey, paths, json=False, language="en_US"):
        self.apikey = apikey
        self.paths = paths
        self.language = language

        self._grammarbot = None
        self._files = []

    @property
    def grammarbot(self):
        if not self._grammarbot:
            self._grammarbot = self.GRAMMARBOT_CLIENT(
                api_key=self.apikey, language=self.language
            )
        return self._grammarbot

    @property
    def files(self):
        """A list of all the files to scan, based upon initial root path.
        Only lists files that have the right file extension.
        Wraps those files in to the TextStatFile object.
        """
        if not self._files:
            self._paths_walk()
        return self._files

    def _paths_walk(self):
        for path in self.paths:
            if os.path.isfile(path):
                self._claim_file(path)
            else:
                for root_path, _, file_names, _ in os.fwalk(path):
                    for file_name in file_names:
                        file_path = os.path.join(root_path, file_name)
                        self._claim_file(file_path)

    def _claim_file(self, file_path):
        """Takes file path, does some checks, and adds it to the files list if
        it meets the criteria.

        :param file_path: The path to the file to check
        :type file_path: str
        """
        if self._extension_ok(file_path):
            self._add_file(file_path)

    def _extension_ok(self, file_name):
        """Pass in a file path to see if the file is OK to be processed.

        :param file_path: Path of file to be checked
        :type file_path: str

        :return: True if this file is OK to process. False if not and should be
            rejected.
        :rtype: bool
        """
        # get the file extension, or the thing after the last dot
        # in the file name, to see if it's on the approved list
        extension = file_name.rsplit(".", maxsplit=1)[-1].lower()
        return extension in self.ACCEPTABLE_FILE_EXTENSIONS

    def _add_file(self, file_path):
        """Wraps file in processor object and adds to list of local variables

        :param file_path: Path of file to add
        :type file_path: str
        """
        self._files.append(self.HEMOGLOBIN_FILE.from_path(file_path, self))

    def to_dict(self):
        return dict(
            (grammarbot_file.f.name, grammarbot_file.to_dict())
            for grammarbot_file in self.files
        )
