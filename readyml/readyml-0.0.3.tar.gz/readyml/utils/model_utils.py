import tensorflow_hub as hub
import importlib
import json
import os

os.environ['TFHUB_DOWNLOAD_PROGRESS'] = "1"

def load(model_name):
    model_link = model_utils_names.get(model_name)
    return hub.load(model_link)

def load_module(model_name):
    """
    TF1 Only
    """
    model_link = model_utils_names.get(model_name)
    return hub.Module(model_link)


def _load_models():
    f = importlib.resources.open_binary('readyml.utils', 'models.json')
    return json.load(f)

model_utils_names = _load_models()
