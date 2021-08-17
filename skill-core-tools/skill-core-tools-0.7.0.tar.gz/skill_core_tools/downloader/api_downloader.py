import logging
import os
import tempfile
from pathlib import Path
from typing import List

from gaia_sdk.api.GaiaCredentials import HMACCredentials
from gaia_sdk.gaia import Gaia, GaiaRef
from rx import operators as ops, pipe

from skill_core_tools.downloader.downloader import Downloader
from skill_core_tools.downloader.gaia_connection_data import GaiaConnectionData

logger = logging.getLogger("DataApiDownloader")


def build_file_uri(folder_name: str, file_name: str) -> str:
    tenant_id = os.environ.get("TENANT_ID")
    return f"gaia://{tenant_id}/{folder_name}/{file_name}"


def build_folder_uri(folder_name: str) -> str:
    tenant_id = os.environ.get("TENANT_ID")
    return f"gaia://{tenant_id}/{folder_name}"


class DataApiDownloader(Downloader):

    def __init__(self, gaia_ref: GaiaRef):
        self.gaia_ref = gaia_ref

    @staticmethod
    def create(connection: GaiaConnectionData) -> Downloader:
        gaia_ref = Gaia.connect(connection.url(), HMACCredentials(connection.username(),
                                                                  connection.password()))
        return DataApiDownloader(gaia_ref=gaia_ref)

    def download(self, folder_name: str, *file_names: str) -> List[Path]:
        if file_names:
            for file_name in file_names:
                file_uri = build_file_uri(folder_name, file_name)
                logger.info(f"Trying to download file {file_uri} from data API")
                try:
                    downloaded_file_in_bytes: bytes = pipe(ops.first())(
                        self.gaia_ref.data(file_uri).as_bytes()).run()
                except Exception as exc:
                    logger.error("File could not be downloaded from data API")
                    raise exc
                destination_folder = Path(tempfile.gettempdir()) / folder_name
                if not os.path.exists(destination_folder):
                    mode = 0o777
                    os.makedirs(destination_folder, mode)
                dest_file_path = destination_folder / file_name

                with open(dest_file_path, mode='wb') as file:
                    file.write(downloaded_file_in_bytes)
                logger.info(f"file was successfully downloaded under {dest_file_path}")
                return [dest_file_path]
        else:
            return DataApiDownloader.download_folder(self, folder_name)

    def download_folder(self, folder_name: str) -> List[Path]:
        file_list = []
        folder_uri = build_folder_uri(folder_name)
        result = pipe(ops.first())(self.gaia_ref.data(folder_uri).list()).run()

        for possible_file in result:
            if folder_name in possible_file.file_path:
                file_split = possible_file.file_path.split('/')
                file_list.append(DataApiDownloader.download(self, folder_name, file_split[len(file_split) - 1])[0])

        return file_list
