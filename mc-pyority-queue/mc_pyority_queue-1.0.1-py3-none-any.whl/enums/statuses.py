from enum import Enum


class Statuses(Enum):
    PENDING = 'Pending'
    IN_PROGRESS = 'In-Progress'
    COMPLETED = 'Completed'
    FAILED = 'Failed'
