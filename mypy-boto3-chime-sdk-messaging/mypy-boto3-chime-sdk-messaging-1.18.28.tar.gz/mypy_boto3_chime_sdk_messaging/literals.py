"""
Type annotations for chime-sdk-messaging service literal definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_chime_sdk_messaging/literals.html)

Usage::

    ```python
    from mypy_boto3_chime_sdk_messaging.literals import ChannelMembershipTypeType

    data: ChannelMembershipTypeType = "DEFAULT"
    ```
"""
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "ChannelMembershipTypeType",
    "ChannelMessagePersistenceTypeType",
    "ChannelMessageTypeType",
    "ChannelModeType",
    "ChannelPrivacyType",
    "ErrorCodeType",
    "SortOrderType",
)


ChannelMembershipTypeType = Literal["DEFAULT", "HIDDEN"]
ChannelMessagePersistenceTypeType = Literal["NON_PERSISTENT", "PERSISTENT"]
ChannelMessageTypeType = Literal["CONTROL", "STANDARD"]
ChannelModeType = Literal["RESTRICTED", "UNRESTRICTED"]
ChannelPrivacyType = Literal["PRIVATE", "PUBLIC"]
ErrorCodeType = Literal[
    "AccessDenied",
    "BadRequest",
    "Conflict",
    "Forbidden",
    "NotFound",
    "PhoneNumberAssociationsExist",
    "PreconditionFailed",
    "ResourceLimitExceeded",
    "ServiceFailure",
    "ServiceUnavailable",
    "Throttled",
    "Throttling",
    "Unauthorized",
    "Unprocessable",
    "VoiceConnectorGroupAssociationsExist",
]
SortOrderType = Literal["ASCENDING", "DESCENDING"]
