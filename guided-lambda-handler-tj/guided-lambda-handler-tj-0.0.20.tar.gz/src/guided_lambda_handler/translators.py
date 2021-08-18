import json
import jsondatetime

from datetime import datetime


def json_to_model(json_str, model_class):
    return model_class(**jsondatetime.loads(json_str))
