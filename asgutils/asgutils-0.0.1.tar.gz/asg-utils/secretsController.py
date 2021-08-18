import yaml
import json
from typing import Optional


def loadSecrets(file_path: str, key: Optional[str] = None) -> dict:
    """
    Load a file into a dictionary

    :param file_path: Path to the file
    :type file_path: str
    :param key: key of the dictionary (defaults to None)
    :type key: str
    :return: File data
    :rtype: dict
    """
    if file_path.endswith('.yml'):
        file_dict = _load_yaml_file(file_path=file_path)
    elif file_path.endswith('.json'):
        file_dict = _load_json_file(file_path=file_path)
    else:
        raise ValueError('File format not supported')

    return file_dict[key] if key else file_dict


def _load_yaml_file(file_path: str) -> dict:
    """
    Load a yaml file into a dictionary

    :param file_path: Path to the file
    :return: yaml file data
    :rtype: dict
    """
    with open(file_path, 'r') as stream:
        return yaml.safe_load(stream)


def _load_json_file(file_path: str) -> dict:
    """
    Load a json file into a dictionary

    :param file_path: Path to the file
    :return: json file data
    :rtype: dict
    """
    with open(file_path, 'r') as f:
        return json.load(f)