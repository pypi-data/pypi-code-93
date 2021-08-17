import logging
import os
from pathlib import Path
from typing import List

from gaia_sdk.api.GaiaCredentials import HMACCredentials
from gaia_sdk.gaia import Gaia, GaiaRef
from rx import operators as ops, pipe

from skill_core_tools.uploader.uploader import Uploader
from skill_core_tools.downloader.gaia_connection_data import GaiaConnectionData

logger = logging.getLogger("DataApiUploader")

def build_file_uri(folder_name: str, file_name: str) -> str:
    tenant_id = os.environ.get("TENANT_ID")
    return f"gaia://{tenant_id}/{folder_name}/{file_name}"

def build_folder_uri(folder_name: str) -> str:
    tenant_id = os.environ.get("TENANT_ID")
    return f"gaia://{tenant_id}/{folder_name}"

class DataApiUploader(Uploader):
    def __init__(self, gaia_ref: GaiaRef):
        self.gaia_ref = gaia_ref

    @staticmethod
    def create(connection: GaiaConnectionData) -> Uploader:
        gaia_ref = Gaia.connect(connection.url(), HMACCredentials(connection.username(), connection.password()))
        return DataApiUploader(gaia_ref=gaia_ref)

    def upload(self, folder_name: str, file_name: str, data: str) -> Path:
        file_uri = build_file_uri(folder_name, file_name)
        folder_uri = build_folder_uri(folder_name)
        logger.info(f"Trying to upload file {file_uri} to data API")

        try:
            upload_data_in_bytes = bytes(data, encoding="utf-8")
            response = self.gaia_ref.data(folder_uri).add(file_name, upload_data_in_bytes)
            path_to_uploaded_file = pipe(ops.first())(response).run().uri

            return path_to_uploaded_file
        except Exception as exc:
            logger.error("File could not be uploaded to data API")
            raise exc

