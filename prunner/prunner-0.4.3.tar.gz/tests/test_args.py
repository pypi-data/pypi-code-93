from prunner.util import convert_args_to_dict
from prunner import main
import pytest


@pytest.fixture
def args():
    input = [
        "-c",
        "example",
        "-v",
        "pipeline",
        "--dryrun",
        "rest",
        "of",
        "args",
        "--FOO=bar",
        "more",
    ]
    return main.parse_arguments(input)


def test_set_config_directory(args):
    config_dir, pipeline, rest_of_args, dryrun, verbose = args
    assert config_dir.endswith("example")
    assert config_dir.startswith("/home")


def test_detects_flags_before_pipeline(args):
    config_dir, pipeline, rest_of_args, dryrun, verbose = args
    assert verbose == True


def test_ignores_flags_after_pipeline(args):
    config_dir, pipeline, rest_of_args, dryrun, verbose = args
    assert dryrun == False


def test_detects_pipeline(args):
    config_dir, pipeline, rest_of_args, dryrun, verbose = args
    assert pipeline == "pipeline"


def test_detect_rest_of_positionals():
    rest_of_args = ["--dryrun", "rest", "of", "args", "--FOO=bar", "more"]
    expected = {
        "_0": "rest of args more",
        "_1": "rest",
        "_2": "of",
        "_3": "args",
        "_4": "more",
    }
    actual = convert_args_to_dict(rest_of_args)
    assert expected.items() < actual.items()


def test_detect_rest_of_name_args():
    rest_of_args = ["--dryrun", "rest", "of", "args", "--FOO=bar", "more"]
    expected = {
        "dryrun": "",
        "FOO": "bar",
    }
    actual = convert_args_to_dict(rest_of_args)
    assert expected.items() < actual.items()
