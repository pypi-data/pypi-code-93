import abc

from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.manager.databricks.databricks_cluster_manager import IDatabricksClusterManager
from whizbang.domain.manager.databricks.databricks_manager_base import DatabricksManagerBase, IDatabricksManager
from whizbang.domain.models.databricks.databricks_cluster import DatabricksCluster
from whizbang.domain.models.databricks.databricks_job import DatabricksJob
from whizbang.domain.models.databricks.databricks_job_instance import DatabricksJobInstance
from whizbang.domain.repository.databricks.databricks_job_repository import IDatabricksJobRepository


class IDatabricksJobManager(IDatabricksManager):
    @abc.abstractmethod
    def run_job(self, client_args: DatabricksClientArgs, job_instance: DatabricksJobInstance):
        """"""


class DatabricksJobManager(DatabricksManagerBase, IDatabricksJobManager):
    def __init__(self, repository: IDatabricksJobRepository, cluster_manager: IDatabricksClusterManager):
        self.cluster_manager = cluster_manager
        DatabricksManagerBase.__init__(self, repository)
        self.repository: IDatabricksJobRepository = self.repository

    def save(self, client_args: DatabricksClientArgs, new_job: DatabricksJob):
        existing_jobs: 'list[DatabricksJob]' = self.repository.get(client_args=client_args)
        existing_clusters: 'list[DatabricksCluster]' = self.cluster_manager.get(client_args=client_args)
        for existing_cluster in existing_clusters:
            if 'existing_cluster_name' in new_job.job_dict and \
                    new_job.job_dict['existing_cluster_name'] == existing_cluster.cluster_name:
                new_job.job_dict.update({'existing_cluster_id': existing_cluster.cluster_dict['cluster_id']})
        for existing_job in existing_jobs:
            if new_job.job_dict['name'] == existing_job.job_dict['settings']['name']:
                new_job.job_dict.update({'job_id': existing_job.job_dict['job_id']})
                return self.repository.update(client_args=client_args, t_object=new_job)
        return self.repository.create(client_args=client_args, t_object=new_job)

    def run_job(self, client_args: DatabricksClientArgs, job_instance: DatabricksJobInstance):
        existing_jobs: 'list[DatabricksJob]' = self.repository.get(client_args=client_args)
        for existing_job in existing_jobs:
            if job_instance.job_name == existing_job.job_dict['settings']['name']:
                job_instance.job_id = existing_job.job_dict['job_id']
                result = self.repository.run_job(client_args=client_args, job_instance=job_instance)
                return result
        return None
