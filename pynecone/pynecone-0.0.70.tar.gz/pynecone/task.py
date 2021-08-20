from abc import abstractmethod
from pynecone import ModuleProvider, ProtoShell, ProtoCmd, Config


class TaskProvider(ModuleProvider):

    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class Task(ProtoShell):

    def __init__(self):
        super().__init__('task', [], 'manage tasks')