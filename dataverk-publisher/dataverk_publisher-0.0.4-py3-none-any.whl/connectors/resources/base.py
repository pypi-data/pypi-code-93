from abc import abstractmethod, ABC

from dataverk_publisher.utils.logger import Logger


class StorageBase(ABC, Logger):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def write(self, file, dp_id: str, resource_path: str, fmt: str, **kwargs):
        raise NotImplementedError(
            f"Abstract method. Needs to be implemented in subclass"
        )
