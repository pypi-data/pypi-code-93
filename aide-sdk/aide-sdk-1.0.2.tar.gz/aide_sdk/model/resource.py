import dataclasses
from typing import Optional


@dataclasses.dataclass(eq=True)
class Resource:
    format: str
    content_type: str
    file_path: str
    namespace: Optional[str] = dataclasses.field(default=None, init=False)
