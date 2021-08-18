import logging
from typing import Callable, List, Optional, TypeVar

RESPONSE = TypeVar("RESPONSE")
ITEM = TypeVar("ITEM")

log = logging.getLogger(__name__)


def cursor_multi_request(
    get_cursor: Callable[[RESPONSE], Optional[str]],
    get_items: Callable[[RESPONSE], List[ITEM]],
    limit: Optional[int],
    request: Callable[[Optional[str]], RESPONSE],
) -> List[ITEM]:
    output: List[ITEM] = []
    cursor: Optional[str] = None
    while True:
        response = request(cursor)
        items = get_items(response)
        output += items
        log.debug(f"[{len(output)}/{limit}] Multi request")
        if limit is not None and len(output) >= limit:
            return output[:limit]
        cursor = get_cursor(response)
        if cursor is None:
            return output
