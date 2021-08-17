from abc import ABC, abstractmethod
from pathlib import Path


class Downloader(ABC):
    @abstractmethod
    def download(self, folder_name: str, *file_name: str) -> Path:
        """
        Downloads a file into the specified download_dir and returns its path.
        :return: the path to the downloaded file
        """
        pass
