from __future__ import annotations

import logging
from abc import abstractmethod, ABC
from typing import List, Optional, Any, Dict, Sequence

from vectice.api import Client, Page
from vectice.api.json_object import JsonObject
from vectice.api.output import JobOutput, JobRunOutput, PagedResponse
from vectice.models import (
    Artifact,
    ArtifactType,
    RunnableJob,
    Job,
    JobRun,
    JobRunStatus,
    DatasetVersionArtifact,
    Artifacts,
    ModelVersionArtifact,
    CodeVersionArtifact,
    DataResource,
)


class AbstractAdapter(ABC):
    @property
    @abstractmethod
    def active_runs(self) -> Dict[int, ActiveRun]:
        pass

    @abstractmethod
    def create_run(self, name: str) -> RunnableJob:
        pass

    @abstractmethod
    def end_run(
        self, run: ActiveRun, outputs: Optional[List[Artifact]] = None, status: str = JobRunStatus.COMPLETED
    ) -> Optional[int]:
        pass

    @abstractmethod
    def start_run(self, run: RunnableJob, inputs: Optional[List[Artifact]] = None) -> ActiveRun:
        pass

    @abstractmethod
    def save_job_and_associated_runs(self, name: str) -> None:
        pass

    @abstractmethod
    def save_run(
        self,
        run: Any,
        inputs: Optional[List[Artifact]] = None,
        outputs: Optional[List[Artifact]] = None,
    ) -> Optional[int]:
        pass

    @abstractmethod
    def run_failed(self, run: Optional[ActiveRun] = None):
        pass


class ActiveRun:
    """Wrapper around dict response to enable using Python ``with`` syntax."""

    _outputs: Optional[List[Artifact]]
    _adapter: AbstractAdapter
    _job: JsonObject
    _run: JsonObject
    _inputs: JsonObject

    def __init__(self, job: JsonObject, run: JsonObject, inputs: JsonObject, adapter: AbstractAdapter):
        self._adapter = adapter
        self._job = job
        self._run = run
        self._inputs = inputs
        self._outputs = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self) -> ActiveRun:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        status = JobRunStatus.COMPLETED if exc_type is None else JobRunStatus.FAILED
        try:
            self._adapter.end_run(self, status=status)
        except Exception as e:
            self._adapter.run_failed(self)
            self._logger.warning(f"Run failed because {e}")
        finally:
            return exc_type is None

    @property
    def outputs(self) -> Optional[List[Artifact]]:
        return self._outputs

    @property
    def run(self) -> JsonObject:
        return self._run

    @property
    def job(self) -> JsonObject:
        return self._job

    def add_output(self, output: Artifact):
        if self._outputs is None:
            self._outputs = []
        self._outputs.append(output)

    def add_outputs(self, outputs: List[Artifact]):
        if len(outputs) > 0:
            if self._outputs is None:
                self._outputs = []
            self._outputs.extend(outputs)


class Adapter(AbstractAdapter):
    def __init__(self, project_token: str, auto_connect=True):
        self._client = Client(project_token, auto_connect)
        self._active_runs: Dict[int, ActiveRun] = {}
        self._last_created_run: Optional[RunnableJob] = None
        self._last_started_run: Optional[ActiveRun] = None
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def active_runs(self) -> Dict[int, ActiveRun]:
        return self._active_runs

    def get_current_runnable_job(self, run: Optional[RunnableJob] = None) -> RunnableJob:
        if run is not None:
            result: RunnableJob = run
        else:
            if self._last_created_run is None:
                raise RuntimeError("A job context must have been created.")
            else:
                result = self._last_created_run
        return result

    def start_run(self, run: Optional[RunnableJob] = None, inputs: Optional[List[Artifact]] = None) -> ActiveRun:
        """
        Start the run created before by calling :func:`~Vectice.create_run` function

        :param run: The runnable job to start
        :param inputs: A list of artifacts used as inputs by this run.
        :return: A reference to a run in progress
        """

        run = self.get_current_runnable_job(run)
        code_artifact_is_present = False
        if inputs is not None:
            for an_input in inputs:
                if an_input is not None:
                    an_input.jobArtifactType = "INPUT"
                    code_artifact_is_present = code_artifact_is_present or an_input.artifactType == ArtifactType.CODE
        if not code_artifact_is_present:
            if inputs is None:
                inputs = []
            artifact = CodeVersionArtifact.create(".")
            if artifact is not None:
                inputs.append(artifact)

        response = self._client.start_run(run, inputs)
        active_run = ActiveRun(response["job"], response["jobRun"], response["jobArtifacts"], self)
        self._active_runs[active_run.run["id"]] = active_run
        self._last_started_run = active_run
        return active_run

    def _get_current_active_run(self, run: Optional[ActiveRun] = None) -> ActiveRun:
        if run is not None:
            result: ActiveRun = run
        else:
            if self._last_started_run is None:
                raise RuntimeError("A job context must have been created.")
            else:
                result = self._last_started_run
        return result

    def end_run(
        self,
        run: Optional[ActiveRun] = None,
        outputs: Optional[List[Artifact]] = None,
        status: str = JobRunStatus.COMPLETED,
    ) -> Optional[int]:
        """
        End the current (last) active run started by :func:`~Vectice.start_run`.
        To end a specific run, use :func:`~Vectice.stop_run` instead.

        :return: Identifier of the run in Vectice if successfully saved
        """
        run = self._get_current_active_run(run)
        if outputs is not None:
            run.add_outputs(outputs)
        if run.outputs is not None:
            for an_output in run.outputs:
                if an_output is not None:
                    an_output.jobArtifactType = "OUTPUT"
        run.run["status"] = status
        self._client.stop_run(run.run, run.outputs)
        if "id" in run.run:
            run_id: Optional[int] = int(run.run["id"])
        else:
            run_id = None
        del self._active_runs[run.run["id"]]
        return run_id

    def __save_run(
        self,
        run: Optional[RunnableJob] = None,
        inputs: Optional[List[Artifact]] = None,
        outputs: Optional[List[Artifact]] = None,
    ) -> Optional[int]:
        if run is None:
            run = self._last_created_run
        active_run = self.start_run(run, inputs)
        return self.end_run(active_run, outputs)

    def save_job_and_associated_runs(self, name: str) -> None:
        raise RuntimeError("No implementation for this library")

    def save_run(
        self,
        run: Any,
        inputs: Optional[List[Artifact]] = None,
        outputs: Optional[List[Artifact]] = None,
    ) -> Optional[int]:
        """
        Save run with its associated inputs and outputs

        :param run: The run we want to save
        :param inputs: A list of inputs (artifacts) you are using in this run
        :param outputs: A list of outputs (artifacts) you are using in this run
        :return: Identifier of the run in Vectice if successfully saved
        """
        if isinstance(run, RunnableJob):
            return self.__save_run(run, inputs, outputs)
        else:
            raise RuntimeError("Incompatible object provided.")

    def create_run(self, job_name: str, job_type: Optional[str] = None) -> RunnableJob:
        """
        Create an instance of a future run of a job.
        The run is not started.
        You need to start it by calling start_run

        :param job_type: The type of the job. see :class:`~vectice.models.JobType` for the list of accepted type.
        :param job_name: The name of the job that should run.
        :return: An instance of a non started run.
        """
        if job_name is None:
            raise RuntimeError("Job name must be set")
        self._last_created_run = RunnableJob(Job(job_name, job_type), JobRun())
        return self._last_created_run

    def run_failed(self, run: Optional[ActiveRun] = None):
        """
        Indicates that the run failed
        """
        self.__update_run_status(run, JobRunStatus.FAILED)

    def run_aborted(self, run: Optional[ActiveRun] = None):
        """
        Indicates that the run was aborted by the user
        """
        self.__update_run_status(run, JobRunStatus.ABORTED)

    def __update_run_status(self, active_run: Optional[ActiveRun], status: str):
        try:
            active_run = self._get_current_active_run(active_run)
            active_run.run["status"] = status
            self._client.update_run(active_run.job["id"], active_run.run["id"], active_run.run)
        except RuntimeError:
            logging.error("run failed to start.")

    def list_jobs(
        self, search: Optional[str] = None, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[JobOutput]:
        """
        List all jobs

        :param search: A text to filter jobs base on their name
        :param page_index: The index of the page we want
        :param page_size: The size of the page we want
        :return: A list of filtered jobs
        """
        return self._client.list_jobs(search, page_index, page_size)

    def list_runs(self, job_id: int, page_index=Page.index, page_size=Page.size) -> Sequence[JobRunOutput]:
        """
        List all run of a specific job

        :param job_id: The Vectice job identifier
        :param page_index: The index of the page we want
        :param page_size: The size of the page we want
        :return: A list of runs
        """
        return self._client.list_runs(job_id, page_index, page_size)

    def create_dataset_with_connection_id(
        self, connection_id: int, dataset_name: str, files: Optional[List[str]], folders: Optional[List[str]] = None
    ) -> int:
        """
        create a new dataset linked to the connection with associated items in it
        :param connection_id: the connection identifier
        :param dataset_name: the dataset name
        :param files: the list of files to be set in the dataset
        :param folders: the list of folders to be set in the dataset
        :return: identifier of the created dataset
        """
        data_resources = DataResource.create_resources(files, folders)
        dataset = self._client.create_dataset(
            {"name": dataset_name, "connectionId": connection_id, "dataResources": data_resources}
        )
        return int(dataset["id"])

    def create_dataset_with_connection_name(
        self, connection_name: str, dataset_name: str, files: Optional[List[str]], folders: Optional[List[str]] = None
    ) -> int:
        """
        create a new dataset linked to the connection with associated items in it
        :param connection_name: the connection name
        :param dataset_name: the dataset name
        :param files: the list of files to be set in the dataset
        :param folders: the list of folders to be set in the dataset
        :return: identifier of the created dataset
        """
        data_resources = DataResource.create_resources(files, folders)
        dataset = self._client.create_dataset(
            {"name": dataset_name, "connectionName": connection_name, "dataResources": data_resources}
        )
        return int(dataset["id"])

    @classmethod
    def create_dataset_version(cls, description: Optional[str] = None) -> DatasetVersionArtifact:
        """
        Create an artifact that contains a version of a dataset

        :param description: A description of the dataset version
        :return: A dataset version artifact
        """
        return Artifacts.create_dataset_version(description)

    @classmethod
    def create_model_version(cls, description: Optional[str] = None) -> ModelVersionArtifact:
        """
        Create an artifact that contains a version of a model

        :param description: A description of the model version
        :return: A model version artifact
        """
        return Artifacts.create_model_version(description)

    @classmethod
    def create_code_version(cls, path: str = ".") -> Optional[CodeVersionArtifact]:
        """
        Create an artifact that contains a version of a code

        :param path: The path to the source code
        :return: A code version artifact
        """
        return Artifacts.create_code_version(path)

    @classmethod
    def create_code_version_with_github_uri(
        cls, uri: str, script_relative_path: Optional[str] = None, login_or_token=None, password=None, jwt=None
    ) -> Optional[CodeVersionArtifact]:
        """
        Create a code artifact based on the GitHub information relative to the given URI and relative path.

        Note: The URI given can include the branch you are working on. otherwise, the default repository branch will be used.

        sample :
            https://github.com/my-organization/my-repository (no branch given so using default branch)
            https://github.com/my-organization/my-repository/tree/my-current-branch (branch given is my-current-branch)

        To access private repositories, you need to authenticate with your credentials.
        see https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/about-authentication-to-github

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param login_or_token: A real login or a personal access token
        :param password: The password
        :param jwt: The OAuth2 access token
        :return: A CodeVersion or None if the GitHub repository was not found or is not accessible
        """
        return Artifacts.create_code_version_with_github_uri(uri, script_relative_path, login_or_token, password, jwt)
