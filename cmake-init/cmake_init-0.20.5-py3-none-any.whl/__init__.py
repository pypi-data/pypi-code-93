import os
import zipfile

from .cmake_init import main

def pypi_main():
    zip = zipfile.ZipFile(
        os.path.join(os.path.dirname(__file__), "cmake-init.zip"),
        "r",
    )
    try:
        # open a dummy fd to keep the zip from being closed
        with zip.open("templates/common/.gitignore") as dummy_fp:
            main(zip)
    except KeyboardInterrupt:
        pass
