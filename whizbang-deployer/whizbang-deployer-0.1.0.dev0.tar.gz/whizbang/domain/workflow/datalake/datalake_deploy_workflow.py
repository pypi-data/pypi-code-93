from whizbang.core.workflow import Workflow, IWorkflow
from whizbang.core.workflow_task import IWorkflowTask
from whizbang.domain.workflow.datalake.datalake_task import UpdateDatalakeAclTask, CreateDatalakeFoldersTask,\
    RemoveDatalakeAclTask


class IDatalakeDeployWorkflow(IWorkflow):
    """"""


class DatalakeDeployWorkflow(Workflow, IDatalakeDeployWorkflow):
    def __init__(self, update_datalake_acl_task: UpdateDatalakeAclTask,
                 create_datalake_folders_task: CreateDatalakeFoldersTask,
                 remove_datalake_acl_task: RemoveDatalakeAclTask):
        self.update_datalake_acl_task = update_datalake_acl_task
        self.create_datalake_folders_task = create_datalake_folders_task
        self.remove_datalake_acl_task = remove_datalake_acl_task

    def _get_workflow_tasks(self) -> 'list[IWorkflowTask]':
        workflow: list[IWorkflowTask] = [self.update_datalake_acl_task,
                                         self.create_datalake_folders_task,
                                         self.remove_datalake_acl_task]
        return workflow
