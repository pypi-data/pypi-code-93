from enum import Enum


class EnvStatus(Enum):
    Running = 1
    Down = 2
    Launching = 3
    Sleep = 4
    Unknown = 5
    Creating = 6
    Cloning = 7
    NotExists = 8
    Exporting = 9
    Migrating = 10
    Broken = 11
    Updating = 12
    Stopping = 13
    GoingToSleep = 14
    Restoring = 15
