import abc

from whizbang.core.workflow_task import IWorkflowTask, WorkflowTask
from whizbang.domain.manager.az.az_storage_manager import IAzStorageManager
from whizbang.domain.models.storage.datalake_state import DatalakeState


class IDatalakeTask(IWorkflowTask):

    @abc.abstractmethod
    def run(self, request: DatalakeState):
        """"""


class UpdateDatalakeAclTask(WorkflowTask, IDatalakeTask):
    def __init__(self, manager: IAzStorageManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "update_acl"

    def run(self, request: DatalakeState):
        self.manager.update_datalake_container_acl(datalake_container=request.storage_container)


class CreateDatalakeFoldersTask(WorkflowTask, IDatalakeTask):
    def __init__(self, manager: IAzStorageManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "create_datalake_folders"

    def run(self, request: DatalakeState):
        self.manager.create_file_system(file_system=request.storage_container)
        self.manager.create_datalake_directories(directories=request.datalake_json['folder-names'],
                                                 storage_container=request.storage_container)


class RemoveDatalakeAclTask(WorkflowTask, IDatalakeTask):
    def __init__(self, manager: IAzStorageManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "remove_acl"

    def run(self, request: DatalakeState):
        self.manager.remove_datalake_container_acl(datalake_container=request.storage_container)
