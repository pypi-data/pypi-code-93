import re


def clean_path(path: str):
    return re.sub('[^a-zA-Z0-9-.]', '_', path)
