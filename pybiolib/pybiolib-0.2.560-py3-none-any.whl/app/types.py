from biolib.typing_utils import TypedDict, Optional

from biolib.biolib_api_client.common_types import SemanticVersion


class ParsedAppUri(TypedDict):
    name: str
    account_handle: str
    version: Optional[SemanticVersion]
