from types import FunctionType

from collections import OrderedDict
import logging
import os
import yaml

from pyrasgo.schemas.enums import DataType
from pyrasgo.schemas.feature_set import FeatureSet, FeatureSetYML

RASGO_DICT: dict = {
"sourceTable": "mandatory DB.SCHEMA.TABLE where features are",
"features": [
                {
                    "columnName": "mandatory_field_name_in_table",
                    "displayName": "Optional Pretty Name",
                    "dataType": "mandatory sql type",
                    "description": "optional display text",
                    "tags": ["optional",
                                "list of strings",
                                "apply only to this feature"
                            ],
                    "attributes":  [
                                        {"key": "value"},
                                        {"optional": "apply only to this features"}
                                   ]
                }
            ],
"dimensions": [
                {
                    "columnName": "mandatory_field_name_in_table",
                    "displayName": "Optional Pretty Name",
                    "dataType": "mandatory sql type",
                    "granularity": "mandatory noun ..."
                }
            ],
"status": "Production | Sandbox",
"tags": [
            "optional",
            "list of strings",
            "apply to all features"
        ],
"attributes": [
                {"key": "value"},
                {"optional": "apply to all features"}
              ],
"script": "OptionalFile.py",
"sourceCode": "Optional valid SQL or python string",
"gitRepo": "Optional"
}

def load_feature_set_from_yaml(*, file_name: str, directory: str = None) -> FeatureSet:
    if directory is None:
        directory = os.getcwd()

    if os.path.splitext(f"{directory}/{file_name}")[1] in ['yaml', 'yml']:
        raise ValueError("Must provide valid yaml file")

    with open(f"{directory}/{file_name}") as _yaml:
        return FeatureSet.parse_obj(yaml.load(_yaml, Loader=yaml.SafeLoader)[0])

def load_feature_set_from_dict(*, feature_set_dict: dict) -> FeatureSet:
    return FeatureSet.parse_obj(feature_set_dict)

def save_feature_set_to_yaml(feature_set: FeatureSetYML, *,
                             file_name: str, directory: str = None, overwrite: bool = True) -> None:
    if directory is None:
        directory = os.getcwd()

    if directory[-1] == "/":
        directory = directory[:-1]

    if file_name.split(".")[-1] not in ['yaml', 'yml']:
        file_name += ".yaml"

    if os.path.exists(f"{directory}/{file_name}") and overwrite:
        logging.warning(f"Overwriting existing file {file_name} in directory: {directory}")

    safe_dumper = yaml.SafeDumper
    safe_dumper.add_representer(DataType, lambda self, data: self.represent_str(str(data.value)))
    safe_dumper.add_representer(OrderedDict, lambda self, data: self.represent_mapping('tag:yaml.org,2002:map',
                                                                                       data.items()))
    safe_dumper.ignore_aliases = lambda self, data: True

    with open(f"{directory}/{file_name}", "w") as _yaml:
        yaml.dump(data=OrderedDict(feature_set.dict(exclude_unset=True, by_alias=True)), Dumper=safe_dumper, stream=_yaml)

def save_feature_set_to_dict(feature_set: FeatureSet, overwrite: bool = True) -> dict:
    return feature_set.dict(exclude_unset=False, by_alias=True)

def _confirm_valid_dict(dict_in: dict, version: int = None) -> bool:
    if not dict_in.get("sourceTable"):
        print("Missing table")
        return False
    if not dict_in.get("features"):
        print("Missing features")
        return False
    for f in dict_in.get("features"):
        if not f.get("columnName") or not f.get("dataType"):
            print("Missing feature attributes")
            return False
    if not dict_in.get("dimensions"):
        print("Missing dimensions")
        return False
    for d in dict_in.get("dimensions"):
        if not d.get("columnName") or not d.get("dataType") or not d.get("granularity"):
            print("Missing dimension attributes")
            return False
    return True