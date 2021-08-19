from typing import Any, Dict

from dataverk_publisher.connectors.resources.base import StorageBase
from dataverk_publisher.utils.file_functions import write_file


class FileStorageConnector(StorageBase):
    def __init__(self):
        super().__init__()

    def write(
        self, file: Any, dp_id: str, resource_path: str, fmt: str = "csv", **kwargs
    ) -> Dict:
        write_file(
            path=f"{dp_id}/{resource_path}",
            content=file,
            compressed=fmt.endswith("gz"),
        )
        return {
            "id": dp_id,
            "status": f"Resource written to file: {dp_id}/{resource_path}",
        }
