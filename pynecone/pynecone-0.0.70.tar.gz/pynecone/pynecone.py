from .shell import Shell
from .gen import Gen
from .env import Env
from .broker import Broker
from .folder import Folder
from .job import Job
from .mount import Mount
from .task import Task
from .topic import Topic
from .repl import Repl
from .api import Api
from .rest import Rest
from .config import Config
from .test import Test


class Pynecone(Shell):

    def __init__(self):
        super().__init__('pynecone')

    def get_commands(self):
        return [Gen(),
                Env(),
                Api(),
                Broker(),
                Folder(),
                Job(),
                Mount(),
                Task(),
                Topic(),
                Test(),
                Repl(),
                Rest()] + Config.init().list_commands()

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'pynecone shell'