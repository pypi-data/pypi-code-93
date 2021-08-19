from typing import Any

import requests

from dataverk_publisher.connectors.resources.base import StorageBase


class DakanConnector(StorageBase):
    def __init__(self, host: str):
        super().__init__()
        self._host = host

    def write(
        self, file: Any, dp_id: str, resource_path: str, fmt: str = "csv", **kwargs
    ):
        try:
            res = requests.put(
                url=f"{self._host}/v1/datapackage/{dp_id}/attachments",
                files=[("files", (f"{resource_path}", file))],
            )
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.logger.error(
                f"Unable to write object {dp_id}/{resource_path} to api {self._host}: {str(err)}"
            )
            raise
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Connection error {self._host}: {str(err)}")
            raise
        else:
            self.logger.info(
                f"Successfully wrote {dp_id}/{resource_path} to api {self._host}"
            )
            return res.json()
