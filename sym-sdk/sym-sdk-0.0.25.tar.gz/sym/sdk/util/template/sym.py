"""Introspection tools and helpers for the Sym API."""

from typing import Dict, List, Optional

from sym.sdk.errors import SymIntegrationErrorEnum
from sym.sdk.user import User


class SymAPIError(SymIntegrationErrorEnum):
    """Raised when there is an error in Sym's internals."""

    HANDLER_NOT_INITIALIZED = ("The Sym API Integration has not been initialized.",)
    USER_NOT_FOUND = ("The User '{user_id}' cannot be found.",)
    ENVIRONMENT_NAME_NOT_FOUND = ("The Environment '{environment_name}' cannot be found.",)
    FLOW_NOT_REGISTERED = (
        "The Flow '{flow_name}' cannot be found in the '{environment_name}' Environment.",
    )
    UNKNOWN_ERROR = ("An unknown error has occurred.",)


def get_flows(
    *,
    user: User,
    environment: Optional[str] = None,
    name: Optional[str] = None,
) -> Dict[str, dict]:
    """Fetches the set of :class:`~sym.sdk.user.Flow`s visible to a given :class:`~sym.sdk.user.User`.

    Args:
        user: The :class:`~sym.sdk.user.User` who is making the request.
        environment: Filters the returned :class:`~sym.sdk.user.Flow`s by a given environment. Supply "*" to return all environments.
        name: Filters by :class:`~sym.sdk.user.Flow` name.
    Returns:
        Dict[str, dict]: The matching `~sym.sdk.user.Flow`s, keyed by slug.
    """
    pass


def handles_to_users(
    *, integration_type: str, integration_srn: Optional[str], handles: List[str]
) -> Dict[str, User]:
    """Fetches the set of :class:`~sym.sdk.user.User`s for a given Integration and set of external handles.

    Args:
        integration_type: Type of the Integration.
        integration_srn: :class:`~sym.sdk.resource.SRN` of the Integration (in case there are multiple of the same type).
        handles: A list of external IDs representing the :class:`~sym.sdk.user.User`s in this Integration.
    Returns:
        Dict[str, User]: A :class:`~sym.sdk.user.User` for each valid handle, keyed by handle.
    """
    pass


def debug(message: str, *, user: Optional[User] = None):
    """Send a debug message.
    This method takes a message and sends it to a :class:`~sym.sdk.user.User`
    via an appropriate channel (e.g. Slack).
    It can be helpful to debug the output of various Integrations.
    Args:
        user: The :class:`~sym.sdk.user.User` to send the message to. Defaults to the Implementer of this Flow.
    """
    pass
