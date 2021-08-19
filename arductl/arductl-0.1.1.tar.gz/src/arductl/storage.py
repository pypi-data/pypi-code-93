from __future__ import annotations

import json
from hashlib import md5
from pathlib import Path
from typing import Any, Dict, IO

from cattr import unstructure, structure

from .models import Mission


def _checksum(obj: object) -> str:
    return md5(str(obj).encode("utf-8")).hexdigest()


def _mission_file_path(mission_name: str) -> Path:
    return Path(mission_name).with_suffix(".json")


def _decode_mission(json: Dict[str, Any]) -> Dict[str, Any]:
    for key in json:
        if isinstance(json[key], dict):
            json[key] = _decode_mission(json[key])
        elif isinstance(json[key], list):
            json[key] = tuple(json[key])

    return json


class StorageError(Exception):
    pass


class ValidationError(Exception):
    pass


def write_mission(mission_file: IO[str], mission: Mission) -> None:
    mission_dict = unstructure(mission)
    checksum = _checksum(mission_dict)
    mission_dict_with_checksum = {"mission": mission_dict, "checksum": checksum}
    json.dump(mission_dict_with_checksum, mission_file)


def store_mission(mission: Mission, mission_name: str) -> None:
    """Store a mission in a file.

    Generates a checksum of the mission to ensure mission is not modified when reloaded. If the provided filename does
    not end in a json extension, one will be added.

    Args:
        mission: Mission to store
        file_name: Name of the file to store the mission to
    """
    file_path = _mission_file_path(mission_name)

    with file_path.open("w") as mission_file:
        write_mission(mission_file, mission)


def read_mission(mission_file: IO[str]) -> Mission:
    data = json.load(mission_file)
    required_keys = ["mission", "checksum"]
    has_required_keys = all(key in data for key in required_keys)

    if not has_required_keys:
        missing = [key for key in required_keys if key not in data]
        raise StorageError(f"Malformed mission file. Missing required key(s): {missing}")

    is_valid = _checksum(data["mission"]) == data["checksum"]

    if not is_valid:
        raise ValidationError("Mission data does not match checksum")

    return structure(data["mission"], Mission)


def load_mission(mission_name: str) -> Mission:
    """Load a mission from a file

    If the provided file name does not include a json extension, it will be added. An exception will be raised if the
    json object in the file does not include the proper keys, or the mission data does not match the checksum.

    Args:
        file_name: The name of the file to load mission from

    Returns:
        mission: The validated mission
    """

    file_path = _mission_file_path(mission_name)

    if not file_path.exists():
        return Mission()
    elif not file_path.is_file():
        raise StorageError(f"{file_path.name} is not a file")

    with file_path.open("r") as mission_file:
        return read_mission(mission_file)
