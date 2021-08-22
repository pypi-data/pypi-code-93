import importlib
import inspect
import pkgutil
import re
from typing import Any, Dict, List, Union

import tfl.api.presentation.entities


def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


TYPES = dict()
for finder, name, ispkg in iter_namespace(tfl.api.presentation.entities):
    module = importlib.import_module(name)
    for class_name, class_spec in inspect.getmembers(module, inspect.isclass):
        TYPES[f"tfl.api.presentation.entities.{class_name.lower()}"] = class_spec


def get_type(json: Dict[str, Any]) -> Any:
    if _type := json.get("$type"):
        first, _, _ = _type.partition(",")
        return TYPES[first.lower()]
    return None


BASE_TYPES = {"str", "float"}

LST_RE = re.compile(r"List\[(\w+)\]")


def from_json(json: Union[List, Dict]):
    if isinstance(json, list):
        return [from_json_obj(obj) for obj in json]
    return from_json_obj(json)


def from_json_obj(json: Dict[str, Any]):
    entity_type = get_type(json)
    argspec = inspect.getfullargspec(entity_type)

    # Fill out arguments
    class_kwargs = dict()
    for arg in argspec.args[1:]:
        annotation = str(argspec.annotations[arg])
        if annotation in BASE_TYPES:
            class_kwargs[arg] = json[arg]
        else:
            if match := LST_RE.match(annotation):  # it is a list of things
                base_type = match.groups()[0]
                if base_type in BASE_TYPES:
                    class_kwargs[arg] = json.get(arg, None)
                else:
                    collection = []
                    for inner_json in json.get(arg, list()):
                        collection.append(from_json_obj(inner_json))
                    class_kwargs[arg] = collection

    resource = entity_type(**class_kwargs)
    return resource
