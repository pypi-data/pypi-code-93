from abc import abstractmethod
from pynecone import ModuleProvider, ProtoShell, ProtoCmd, Config


class JobProvider(ModuleProvider):

    @abstractmethod
    def run(self, job):
        pass


class Job(ProtoShell):

    def __init__(self):
        super().__init__('job', [],  'manage jobs')