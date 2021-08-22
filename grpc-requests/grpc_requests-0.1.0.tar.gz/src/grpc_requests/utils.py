from pathlib import Path


def load_data(_path):
    with open(Path(_path).expanduser(), 'rb') as f:
        data = f.read()
    return data
