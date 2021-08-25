from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QueueMessage:
    queue_name: str
    message_id: str
    receipt_handle: str
    body: Any
