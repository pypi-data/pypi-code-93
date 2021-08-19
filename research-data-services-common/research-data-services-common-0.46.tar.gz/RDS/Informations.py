from enum import Enum

class LoginMode(Enum):
    credentials = 0
    oauth = 1

class FileTransferMode(Enum):
    active = 0
    passive = 1

class FileTransferArchive(Enum):
    none = 0
    zip = 1