import ssl
from os import environ, pathsep
from os.path import abspath, dirname, join

if getattr(ssl, "HAS_SNI", False):
    data_path = join(abspath(dirname(__file__)), "data")
    environ["AWS_DATA_PATH"] = (
        environ["AWS_DATA_PATH"] + pathsep + data_path
        if environ.get("AWS_DATA_PATH")
        else data_path
    )
