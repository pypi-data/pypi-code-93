from enum import Enum


class DownloadState(Enum):
    CANCELED = 0
    CREATED = 1
    FAILED = 2
    RUNNING = 3
    OK = 4

