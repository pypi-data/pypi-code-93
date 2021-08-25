import json

from whizbang.domain.models.json_serializable import JsonSerializable


def import_local_json(file_path: str):
    file = open(file_path)
    j_object = json.load(file)
    file.close()
    return j_object


def export_local_json(file_path: str, t_object: JsonSerializable) -> None:
    file = open(file_path, 'w+')
    file.write(t_object.to_json())
    file.close()
