import json
import os
from collections import OrderedDict
from typing import Dict

from distpy.calc import pub_command_set

from fathom_lib.component_autogeneration.sklearn.extract_all_sklearn_vuetify_schema_form import (
    EnhancedJSONEncoder,
)
from fathom_lib.component_autogeneration.sklearn.generate_ui_components import (
    JS_SCHEMA_FOLDER,
)

json_schema_form_types_mapping = {
    "string": {"type": "string"},
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "bool": {"type": "boolean"},
    "intrange": {"type": "string"},
}


def build_json_schema_form(doc: Dict):
    schema = {"type": "object", "properties": OrderedDict()}
    for param_name, param_details in doc.items():
        schema_field = OrderedDict()
        # for now set to string - later check the type of the default value
        schema_field["type"] = "string"
        schema_field["title"] = param_name
        schema_field["default"] = param_details.get("default", "")
        schema_field["description"] = param_details["description"]
        if "default" in param_details:
            schema_field["is_optional"] = param_details["default"] is None
        else:
            schema_field["is_optional"] = False
        schema["properties"][param_name] = schema_field
    return schema


"""
                "name": "kernel",
                "types": [],
                "choices": [
                    "knn",
                    "rbf"
                ],
                "is_optional": false,
                "default": "rbf"
            },
"""


def convert_to_param(name, param):
    return {
        "name": name,
        "description": param.get("description", ""),
        "types": [],
        "is_optional": True,
        "default": param.get("default", ""),
    }


if __name__ == "__main__":

    list_of_commands = pub_command_set.KnownCommands({})

    estimators = []
    for command_name, command_obj in list_of_commands.items():
        if command_name in ["NONE", "data"]:
            continue
        print(command_name)
        raw_docs = command_obj.docs()
        print(raw_docs)
        docs = {}
        docs["doc"] = raw_docs.get("one_liner", "")
        docs["js_name"] = "DFO" + command_obj.__name__.replace("Command", "")
        docs["name"] = command_obj.__name__
        docs["module"] = "DFO"
        docs["module"] = "distpy.calc.pub_command_set"
        docs["human_module"] = "DFO"
        docs["js_component_prefix"] = "DFO"
        docs["params_list"] = (
            [p for p in raw_docs["args"].keys()] if "args" in raw_docs else []
        )
        docs["params"] = (
            {
                name: convert_to_param(name, details)
                for name, details in raw_docs["args"].items()
            }
            if "args" in raw_docs
            else {}
        )
        docs["json_schema_form"] = build_json_schema_form(
            raw_docs["args"] if "args" in raw_docs else {}
        )
        docs["input_list"] = [
            {
                "key": "input",
                "name": "input",
                "socket": "anySocket",
                "many_connections": False,
            }
        ]
        docs["output_list"] = [
            {
                "key": "output",
                "name": "output",
                "socket": "anySocket",
                "many_connections": False,
            }
        ]

        estimators.append(docs)

    with open(
        os.path.join(JS_SCHEMA_FOLDER, "dfo_schemas.json"),
        "wt",
    ) as out:
        out.write(json.dumps(estimators, cls=EnhancedJSONEncoder, indent=4))
