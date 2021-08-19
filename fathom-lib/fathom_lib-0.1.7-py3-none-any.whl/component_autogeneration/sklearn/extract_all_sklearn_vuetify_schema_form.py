import os
import json
from collections import OrderedDict

import dataclasses

from fathom_lib.component_autogeneration.rest_html import convert_string_fragment
from fathom_lib.component_autogeneration.sklearn.generate_ui_components import (
    JS_SCHEMA_FOLDER,
    extract_class_info,
    filter_class,
    filter_estimator,
)
from fathom_lib.component_autogeneration.submodules import get_classes


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif callable(o):
            return o.__name__
        else:
            return super().default(o)


json_schema_form_types_mapping = {
    "string": {"type": "string"},
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "bool": {"type": "boolean"},
    "intrange": {"type": "string"},
}


def build_json_schema_form(estimator):
    schema = {"type": "object", "properties": OrderedDict()}
    for param_name, param_details in estimator["params"].items():
        schema_field = OrderedDict()

        if len(param_details.types) > 0:
            param_type = param_details.types[0]
        else:
            param_type = "string"

        # set some constants for type
        style = json_schema_form_types_mapping[param_type]
        for k, v in style.items():
            schema_field[k] = v

        # if there are choices
        if len(param_details.choices) > 0:
            schema_field["oneOf"] = [
                {"const": c, "title": c} for c in param_details.choices
            ]

        # set title and description
        schema_field["title"] = param_name
        schema_field["description"] = param_name

        schema["properties"][param_name] = schema_field
    return schema


if __name__ == "__main__":

    sklearn_objects = get_classes("sklearn", prefix="Sklearn")
    sklearn_objects.update(
        get_classes("sklearn.feature_extraction", prefix="Sklearnsklearn_")
    )
    sklearn_objects.update(
        get_classes("sklearn.feature_extraction.text", prefix="skleran_Sklearn")
    )
    sklearn_objects.update(get_classes("fathom.transformers", prefix="Fathom"))
    sklearn_objects.update(
        get_classes(
            "fathom.models.xgboost_aft",
            prefix="",
            human_submodule_func=lambda x: "xgboost",
        )
    )
    sklearn_objects.update(
        get_classes(
            "fathom.models.autokeras_models",
            prefix="",
            human_submodule_func=lambda x: "autokeras",
        )
    )
    # TODO: don't add LabelEncoder
    sklearn_objects.update(
        get_classes(
            "xgboost.sklearn", prefix="", human_submodule_func=lambda x: "xgboost"
        )
    )
    sklearn_objects.update(
        get_classes(
            "lightgbm.sklearn", prefix="", human_submodule_func=lambda x: "lightgbm"
        )
    )
    sklearn_objects.update(
        get_classes(
            "catboost.core", prefix="", human_submodule_func=lambda x: "catboost"
        )
    )
    sklearn_objects.update(
        get_classes(
            "pyod", prefix="Pyod", human_submodule_func=lambda x: "anomaly detection"
        )
    )

    workflows = get_classes("fathom.runnable.expanding_window", prefix="Fathom")
    workflows.update(get_classes("fathom.runnable.single_split", prefix="Fathom"))
    print("WORKFLOWS")
    print(workflows)

    for objects, filename in [
        (sklearn_objects, "sklearn_based_schemas.json"),
        (workflows, "runnable_schemas.json"),
    ]:
        estimators = []
        for k, v in objects.items():
            if filter_class(v):
                estimators.append(extract_class_info(v))
            else:
                print("discarded class", k, v)

        estimators = [est for est in estimators if filter_estimator(est)]

        estimators = sorted(estimators, key=lambda x: x["module"])

        schemas = []
        for estimator in estimators:
            print(estimator)
            name = estimator["js_name"]
            estimator["params"] = {p.name: p for p in estimator["params"]}
            estimator["json_schema_form"] = build_json_schema_form(estimator)
            schemas.append(estimator)

        with open(
            os.path.join(JS_SCHEMA_FOLDER, filename),
            "wt",
        ) as out:
            out.write(json.dumps(schemas, cls=EnhancedJSONEncoder, indent=4))
