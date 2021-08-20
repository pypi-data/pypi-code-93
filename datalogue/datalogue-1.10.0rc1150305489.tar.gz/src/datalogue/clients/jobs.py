from typing import List, Optional, Union
from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.models.job import Job, JobStatus, JobType
from datalogue.dtl_utils import _parse_list
from datalogue.errors import DtlError
from datetime import datetime
from uuid import UUID


class JobsClient:
    """
    Client to interact with the Scheduled pipelines
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def list(
        self,
        statuses: List["JobStatus"] = [
            JobStatus.Scheduled,
            JobStatus.Defined,
            JobStatus.Running,
            JobStatus.Succeeded,
            JobStatus.Failed,
            JobStatus.Unknown,
            JobStatus.Cancelled,
        ],
        job_types: List["JobType"] = [JobType.Pipeline, JobType.Sampling],
        page: int = 1,
        item_per_page: int = 25,
        pipeline_ids: Optional[List[UUID]] = None,
        scheduled_from: Optional[datetime] = None,
        scheduled_until: Optional[datetime] = None,
        job_duration_min: Optional[int] = None,
        job_duration_max: Optional[int] = None,
        job_owners: Optional[List[UUID]] = None,
        connection_ids: Optional[List[UUID]] = None,
    ) -> Union[DtlError, List[Job]]:
        """
        List jobs

        :param page: page to be retrieved
        :param item_per_page: number of jobs to be put in a page
        :param pipeline_id: optional pipeline id used to retrieve related jobs.
        :return: Returns a List of all the available Jobs or an error message as a string
        """

        statuses_list = [s.value for s in statuses]
        job_type_list = [jt.value for jt in job_types]

        endpoint = f"/v2/jobs?page={page}&size={item_per_page}"

        params = {"job-statuses": statuses_list, "job-type-filter": job_type_list}

        if pipeline_ids:
            params["stream-ids"] = pipeline_ids
        if job_duration_max:
            params["duration-max"] = job_duration_max
        if job_duration_min:
            params["duration-min"] = job_duration_min
        if scheduled_from:
            params["scheduled-from"] = created_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        if scheduled_until:
            params["scheduled-until"] = created_until.strftime("%Y-%m-%dT%H:%M:%SZ")
        if job_owners:
            params["owner"] = job_owners
        if connection_ids:
            params["connection-ids"] = connection_ids

        res = self.http_client.make_authed_request(
            path=self.service_uri + endpoint, method=HttpMethod.GET, params=params
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(Job._from_payload)(res)

    def cancel(self, job_id: UUID) -> Union[DtlError, Job]:
        """"
        Cancel a Job given job_id.

        :param job_id:
        :return: Returns the Job object canceled or an error
        """

        res = self.http_client.make_authed_request(self.service_uri + f"/jobs/{str(job_id)}/cancel", HttpMethod.POST)

        if isinstance(res, DtlError):
            return res

        return Job._from_payload(res)

    def get(self, job_id: UUID) -> Union[DtlError, Job]:
        """"
        Get a Job given job_id.

        :param job_id:
        :return: Returns the Job object or an error
        """
        endpoint = f"/v2/jobs"

        statuses = JobStatus.values()
        job_types = JobType.values()

        params = {"job-statuses": statuses, "job-type-filter": job_types, "id": job_id, "page": 1, "size": 1}
        res = self.http_client.make_authed_request(
            path=self.service_uri + endpoint, method=HttpMethod.GET, params=params
        )
        if isinstance(res, DtlError):
            return res

        if not isinstance(res, list):
            return DtlError("Response from server should be a list")

        if len(res) < 1:
            return DtlError(f"No job results found with id {job_id}")

        return Job._from_payload(res[0])
