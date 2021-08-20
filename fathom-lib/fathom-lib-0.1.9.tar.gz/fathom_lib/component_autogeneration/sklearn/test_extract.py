import glob
import os
import pandas as pd
import json

from fathom_lib.component_autogeneration.sklearn.generate_ui_components import (
    JS_FOLDER,
    extract_class_info,
    filter_class,
    filter_estimator,
)
from fathom_lib.component_autogeneration.submodules import get_classes
from jinja2 import Template
from sklearn.cross_decomposition import PLSSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.impute._base import SimpleImputer
from sklearn.calibration import IsotonicRegression
import dataclasses


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif callable(o):
            return o.__name__
        else:
            return super().default(o)


if __name__ == "__main__":
    cls = IsotonicRegression
    cls_obj = {
        "name": cls.__name__,
        "cls": cls,
        "submodule": "sklearn.cross_decomposition",
    }

    for k, v in extract_class_info(cls_obj).items():
        if k == "doc":
            continue
        print(k, v)
        print()

    print(json.dumps(extract_class_info(cls_obj), cls=EnhancedJSONEncoder, indent=4))
