from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Dict, List
from cryptoshred.backends import KeyBackend
from cryptoshred.entities import CryptoContainer


def from_list_in_file(path: Path, key_backend: KeyBackend) -> Dict[str, List[str]]:
    with open(path, "rb") as f:
        content = json.load(f)

    mapping = defaultdict(list)

    for elem in content:
        cc: CryptoContainer[Any] = CryptoContainer(**elem, key_backend=key_backend)  # type: ignore
        mapping[str(cc.id)].append(cc.plain())

    return mapping
