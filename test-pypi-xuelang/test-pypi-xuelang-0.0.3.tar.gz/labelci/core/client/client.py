from typing import Optional
import os
import requests
from requests.api import request
from requests.models import Response

from labelci.common.utils import check_response_status, save_file
from labelci.core.client.config import DEFAULT_REQUEST_TIMEOUT
from labelci.core.client.config import (
    GET_TOKEN,
    GET_PROJECT,
    GET_PROJECT_LIST,
    GET_PROJECT_TASKS,
    GET_LABEL_CONFIG_TEMPLATE,
    PROJECT_EXPORT,
    GET_EXPORT_FORMATS

)
from labelci.common.exception.labelci_sdk_exception import (
    InvalidTokenException,
    ProjectNotFound
)


class DataHubClient:

    def __init__(self, url, token) -> None:
        self.url = url
        self.token = token

    def request(
            self,
            method: str,
            relative_url: str,
            params: Optional[dict] = None,
            data: Optional[dict] = None,
            files: Optional[dict] = None,
            json: Optional[dict] = None,
            # headers: Optional[dict] = None,
            timeout: Optional[int] = DEFAULT_REQUEST_TIMEOUT,
    ):
        params = params or {}
        data = data or {}
        files = files or {}
        json = json or {}
        url = self.url + relative_url
        headers = {"Authorization": "Token " +
                                    self.token} if self.token else {}

        response = requests.request(
            method,
            url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            files=files,
            timeout=timeout,
        )
        check_response_status(response)
        return response

    # def get_all_annotations(self):
    #     headers = {
    #         "Authorization": "Token " + self.token
    #     }
    #     response = requests.get(url=self.url, headers=headers)
    #     check_response_status(response=response)

    #     print(response)

    # Projcet API
    def get_project_list(self):
        """Get a list of the projects that you've created.
        """
        relative_url = GET_PROJECT_LIST
        response = self.request("GET", relative_url).json()

        return response

    def create_project(self):
        pass

    def get_label_config_templates(self):
        """Get label-config templates list
        """
        relative_url = GET_LABEL_CONFIG_TEMPLATE
        response = self.request("GET", relative_url).json()

        return response

    def get_project_tasks(self, project_id):
        """Retrieve a paginated list of tasks for a specific project.
        """
        relative_url = GET_PROJECT_TASKS.format(project_id)
        response = self.request("GET", relative_url).json()

        return response

    # EXPORT API
    def export_project(self, project_id, export_type="JSON", download_all_tasks=False):
        """Export annotated tasks as a file in a specific format.
        """

        relative_url = PROJECT_EXPORT.format(project_id)
        export_type = export_type.upper()
        # response = self.request("GET", relative_url, params={"exportType": export_type})._content
        response = self.request("GET", relative_url,
                                params={"exportType": export_type,
                                        "download_all_tasks": download_all_tasks}).content

        return response

    def get_export_format(self, id):
        """Retrieve the available export formats for the current project.
        """
        relative_url = GET_EXPORT_FORMATS
        response = self.request("GET", relative_url).json()

        return response

    def download_file(self, path):
        relative_url = path
        response = self.request("GET", relative_url).content

        return response

    def check_token(self):
        """Check whether the token exists
        """
        relative_url = GET_TOKEN
        response = self.request("GET", relative_url).json()
        if not response.get("token"):
            raise InvalidTokenException

    def check_project_id(self, project_id):
        """Check whether the token exists
        """
        relative_url = GET_PROJECT.format(project_id)
        response = self.request("GET", relative_url).json()
        if response.get("status_code") == 404:
            raise ProjectNotFound
