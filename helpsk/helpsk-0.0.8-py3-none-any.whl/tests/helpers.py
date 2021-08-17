from helpsk.utility import is_debugging
from os import getcwd


def get_test_path():
    path = getcwd()
    if not is_debugging():
        path = path + '/tests'

    return path
