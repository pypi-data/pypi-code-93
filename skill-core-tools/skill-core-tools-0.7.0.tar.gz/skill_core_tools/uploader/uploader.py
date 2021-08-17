from abc import ABC, abstractmethod
from pathlib import Path


class Uploader(ABC):
    @abstractmethod
    def upload(self, folder_name: str, file: str, data: str) -> Path:
        """
        Uploads a file into the specified dir and returns its path.
        :return: the path to the uploaded file
        """
        pass
