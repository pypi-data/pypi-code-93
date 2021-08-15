import os
import yaml


def read_yml_file(path: os.PathLike):
    with open(path, "r") as f:
        return yaml.safe_load(f)
