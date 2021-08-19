from dataclasses import dataclass
from typing import Optional, Dict, List


@dataclass
class MonolithResponse:
    data: Optional[Dict] = None
    errors: Optional[List[Dict]] = None
