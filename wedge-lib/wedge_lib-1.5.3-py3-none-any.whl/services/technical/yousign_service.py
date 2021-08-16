import base64
import json

from django.conf import settings

from w.services.abstract_service import AbstractService
from w.services.technical.filesystem_service import FilesystemService
from w.services.technical.json_service import JsonService
from w.services.technical.models.yousign import YouSignRequest
from w.services.technical.request_service import RequestService


class YouSignService(AbstractService):
    _api_url = None
    _request_session = None
    _headers = None

    @classmethod
    def init(cls, api_url=None, api_key=None) -> None:
        """ Initialize service with API url and key """
        if api_url is None:
            api_url = settings.YOUSIGN_API_URL
        if api_key is None:
            api_key = settings.YOUSIGN_API_KEY

        cls._api_url = api_url
        cls._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    @classmethod
    def clear(cls):
        """ Clear service """
        super().clear()
        cls._api_url = None
        cls._request_session = None

    @classmethod
    def _is_initialized(cls) -> bool:
        """ Check service is initialized """
        return cls._api_url and cls._headers

    @classmethod
    def _raise_api_failed(cls, response, msg):
        """
        raise RuntimeError for yousign api failure
        """
        if JsonService.is_valid(response.orig_content):
            error = json.loads(response.orig_content)
            error = error["detail"]
        else:
            error = "no detail"

        raise RuntimeError(
            f"{msg} ({response.status_code} - {response.content}) : {error}"
        )

    @classmethod
    def _upload_file(cls, filename):
        """
        Upload file to YouSign (first step)

        Args:
            filename(str): file to upload

        Returns:
            file_id: file id
        """
        payload = {"name": FilesystemService.get_basename(filename), "content": None}
        with open(filename, "rb") as f:
            payload["content"] = base64.b64encode(f.read())
        payload["content"] = payload["content"].decode("utf-8")
        payload = JsonService.dump(payload)
        response = RequestService.post(
            "/files", data=payload, session=cls._request_session
        )
        if response.success:
            return response.content["id"]

        cls._raise_api_failed(response, f"Failed to upload '{filename}'")

    @classmethod
    def _create_procedure(cls, file_id, data: YouSignRequest) -> str:
        """
        Create procedure

        Args:
            file_id(str): uploaded file id for procedure
            data(YouSignRequest): needed data to create procedure

        Returns:
            str: member id
        """
        payload = data.get_procedure_payload(file_id)
        payload = JsonService.dump(payload)
        response = RequestService.post(
            "/procedures", data=payload, session=cls._request_session
        )
        if response.success:
            return response.content["members"][0]["id"]
        cls._raise_api_failed(response, "Failed to create procedure")

    @classmethod
    def create(cls, data: YouSignRequest):
        """
        create signature procedure

        Args:
            data(YouSignRequest): data needed to start procedure

        Returns:
            str: member id needed for iFrame
        """
        cls._check_is_initialized()
        FilesystemService.check_file_exists(data.filename)
        cls._request_session = RequestService.init_session(
            cls._api_url, headers=cls._headers
        )

        # basic mode
        # Step 1 - Upload the file
        file_id = cls._upload_file(data.filename)

        # Step 2 - Create the procedure
        return cls._create_procedure(file_id, data)

    @classmethod
    def get_file(cls, file_url: str):
        """
        get contract file by id

        Args:
            file_url(str): file url from webhook

        Returns:
            str: file object in base64
        """
        cls._check_is_initialized()
        cls._request_session = RequestService.init_session(
            cls._api_url, headers=cls._headers
        )

        response = RequestService.get(
            f"{file_url}/download", session=cls._request_session
        )
        if response.success:
            return response.content
        cls._raise_api_failed(response, "Failed to get contract file")
