"""Helpers for interacting with a Slack workspace."""

from enum import Enum
from typing import List, Optional, Sequence, Union

from sym.sdk.errors import SymIntegrationErrorEnum
from sym.sdk.user import User


class SlackError(SymIntegrationErrorEnum):
    """Raised when there is an error connecting to Slack's API."""

    UNKNOWN = (
        "An unexpected error occurred while trying to connect to Slack.",
        "Sym Support has been notified of this issue and should be reaching out shortly.",
    )
    TIMEOUT = ("Sym timed out while trying to connect to Slack.", "Try again in a few seconds.")


class SlackLookupType(Enum):
    USER = "user"
    USER_ID = "slack_user_id"
    CHANNEL = "channel_id"
    GROUP = "group"
    EMAIL = "email"


class SlackChannel:
    def __init__(
        self,
        lookup_type: str,
        lookup_keys: List[str],
        allow_self: Optional[bool] = False,
    ):
        pass


def user(identifier: Union[str, User]) -> SlackChannel:
    """A reference to a Slack user.

    Users can be specified with a Slack user ID, email,
    or Sym :class:`~sym.sdk.user.User` instance.
    """


def channel(name: str, allow_self: Optional[bool] = False) -> SlackChannel:
    """A reference to a Slack channel."""


def group(users: Sequence[Union[str, User]]) -> SlackChannel:
    """
    A reference to a Slack group.

    Args:
        users (Sequence[Union[str, User]]): A list of either Sym :class:`~sym.sdk.user.User` objects or emails.
    """
