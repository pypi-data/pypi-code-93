import os
import json

from .utils import get_dir
from .download import run, get_files


def load_impacts():
    # download all impacts first if not done yet
    run()

    folder = get_dir()
    files = get_files()
    impacts = []
    for filename in files:
        with open(os.path.join(folder, filename), 'r') as file:
            impacts.append(json.load(file))
    return impacts
