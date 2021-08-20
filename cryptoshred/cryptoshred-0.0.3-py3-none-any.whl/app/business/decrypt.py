from pathlib import Path
from typing import Any
from cryptoshred.backends import KeyBackend
import json
from cryptoshred.convenience import find_and_decrypt_in_dict

from cryptoshred.entities import CryptoContainer


def from_list_in_file(path: Path, key_backend: KeyBackend) -> Any:
    # TODO maybe this is easier with pydantics from_file
    with open(path, "rb") as f:
        content = json.load(f)

    return [CryptoContainer(**elem, key_backend=key_backend).plain() for elem in content]  # type: ignore


def from_dict_in_file(path: Path, key_backend: KeyBackend) -> Any:
    with open(path, "rb") as f:
        content = json.load(f)

    return find_and_decrypt_in_dict(content, key_backend)


def from_json_string(input: str, key_backend: KeyBackend) -> str:
    dct = json.loads(input)
    return CryptoContainer(**dct, key_backend=key_backend).plain()  # type:ignore
