# Python
from pathlib import Path

# jsonpickle
import jsonpickle


def load_jpickle(file: Path) -> object:
    with open(file, 'r') as f:
        return jsonpickle.decode(
            f.read()
        )


def dump_jpickle(file: Path, data: object):
    with open(file, 'w') as f:
        f.write(
            jsonpickle.encode(data, indent='\t')
        )
