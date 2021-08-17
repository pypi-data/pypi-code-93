import tempfile
import contextlib
import shutil
import os
import logging
from pathlib import Path


JAVAC_RULE = 'javac_params.bzl'
JAVAC_PARAMS = os.path.join(Path(__file__).parent.absolute(), JAVAC_RULE)


@contextlib.contextmanager
def setup():
    d = tempfile.mkdtemp(suffix="unused_deps")
    try:
        Path(d, 'WORKSPACE').touch()
        Path(d, 'BUILD').touch()
        shutil.copyfile(JAVAC_PARAMS, Path(d, JAVAC_RULE).absolute())
        logging.info(f"prepared {d}")
        yield d
    finally:
        shutil.rmtree(d)
