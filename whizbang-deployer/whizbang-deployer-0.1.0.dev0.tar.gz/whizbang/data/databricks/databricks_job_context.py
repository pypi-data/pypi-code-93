import abc
from databricks_cli.sdk import ApiClient
from databricks_cli.jobs.api import JobsApi

from whizbang.data.databricks.databricks_context_base import DatabricksContextBase, IDatabricksContextBase


class IDatabricksJobContext(IDatabricksContextBase):
    """"""

    @abc.abstractmethod
    def create_job(self, job_dict):
        """"""

    @abc.abstractmethod
    def get_jobs(self):
        """"""

    @abc.abstractmethod
    def update_job(self, job_dict):
        """"""

    @abc.abstractmethod
    def run_job(self, job_id, jar_params=None, notebook_params=None, python_params=None, spark_submit_params=None):
        """"""


class DatabricksJobContext(DatabricksContextBase, IDatabricksJobContext):
    def __init__(self, api_client: ApiClient, api: JobsApi):
        DatabricksContextBase.__init__(self, api_client=api_client, api=api)

    def create_job(self, job_dict):
        def _create_job(api: JobsApi, job_dict):
            return api.create_job(json=job_dict)

        return self._execute(func=_create_job, job_dict=job_dict)

    def get_jobs(self):
        def _get(api: JobsApi):
            return api.list_jobs()

        return self._execute(func=_get)

    def update_job(self, job_dict):
        def _update_job(api: JobsApi, job_dict):
            return api.reset_job(json=job_dict)

        return self._execute(func=_update_job, job_dict=job_dict)

    def run_job(self, job_id, jar_params=None, notebook_params=None, python_params=None, spark_submit_params=None):
        def _run_job(api: JobsApi,
                     job_id=job_id,
                     jar_params=jar_params,
                     notebook_params=notebook_params,
                     python_params=python_params,
                     spark_submit_params=spark_submit_params):
            return api.run_now(job_id=job_id,
                               jar_params=jar_params,
                               notebook_params=notebook_params,
                               python_params=python_params,
                               spark_submit_params=spark_submit_params)

        return self._execute(func=_run_job,
                             job_id=job_id,
                             jar_params=jar_params,
                             notebook_params=notebook_params,
                             python_params=python_params,
                             spark_submit_params=spark_submit_params)
