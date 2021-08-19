import pathlib
from pathlib import Path


def write_file(path, content, compressed: bool = False):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w" if not compressed else "wb") as file:
        file.write(content)
