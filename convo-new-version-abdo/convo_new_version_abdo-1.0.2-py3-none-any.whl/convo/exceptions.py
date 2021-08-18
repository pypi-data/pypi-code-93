from typing import Text

from convo.shared.exceptions import ConvoExceptions 


class ModelNotPresent(ConvoExceptions ):
    """Raised when a model is not found in the path provided by the user."""


class NoEventsToMigrateErr(ConvoExceptions ):
    """Raised when no events to be migrated are found."""


class NoConvers_InTrackerStoreError(ConvoExceptions):
    """Raised when a tracker store does not contain any conversations."""


class NoEventsOccurInTimeRangeError(ConvoExceptions):
    """Raised when a tracker store does not contain events within a given time range."""


class DependencyExceptionMissing(ConvoExceptions ):
    """Raised if a python package dependency is needed, but not installed."""


class PublishingErr(ConvoExceptions ):
    """Raised when publishing of an event fails.

    Attributes:
        timestamp -- Unix timestamp of the event during which publishing fails.
    """

    def __init__(self, timestamp: float) -> None:
        self.timestamp = timestamp
        super(PublishingErr, self).__init__()

    def __str__(self) -> Text:
        return str(self.timestamp)
