import os
import tempfile

import pytest
from koalak import D, F, mkframework
from koalak.bases import normalize_home_structure

# TODO: unskip test and continue implementations


@pytest.mark.skip
def test_init_home_dict_files():
    with tempfile.TemporaryDirectory() as dirname:
        # fmt: off
        home = {
            "a": "",
            "b": "",
            "c": ""
        }
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(homepath=home_path, home_structure=home)
        framework.init()

        assert os.path.isdir(home_path)
        for path in ["a", "b", "c"]:
            path = os.path.join(home_path, path)
            assert os.path.isfile(path)
            with open(path) as f:
                assert f.read() == ""


@pytest.mark.skip
def test_init_home_dict_dirs():
    with tempfile.TemporaryDirectory() as dirname:
        # fmt: off
        home = {
            "a": {},
            "b": {},
            "c": {}
        }
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(homepath=home_path, home_structure=home)
        framework.init()

        assert os.path.isdir(home_path)
        for path in ["a", "b", "c"]:
            path = os.path.join(home_path, path)
            assert os.path.isdir(path)


@pytest.mark.skip
def test_init_home_dict_files_and_dirs():
    # str is a directory
    with tempfile.TemporaryDirectory() as dirname:
        # fmt: off
        home = {
            "a": "",
            "b": "",
            "c": {},
            "d": {},
            "e": {},
            "f": {}

        }
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(homepath=home_path, home_structure=home)
        framework.init()

        assert os.path.isdir(home_path)

        for path in ["a", "b"]:
            path = os.path.join(home_path, path)
            assert os.path.isfile(path)
            with open(path) as f:
                assert f.read() == ""

        for path in ["c", "d", "e", "f"]:
            path = os.path.join(home_path, path)
            assert os.path.isdir(path)


@pytest.mark.skip
def test_init_home_recurse():
    with tempfile.TemporaryDirectory() as dirname:
        # fmt: off
        home = {
            "a": "",
            "b": "",
            "c": {},
            "d": {
                "e": {},
                "f": ""
            },
            "g": {
                "h": {
                    "i": {
                        "j": {
                            "k": ""
                        }
                    }
                }
            }
        }
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(homepath=home_path, home_structure=home)
        framework.init()

        assert os.path.isdir(home_path)

        assert os.path.isfile(os.path.join(home_path, "a"))
        assert os.path.isfile(os.path.join(home_path, "b"))
        assert os.path.isdir(os.path.join(home_path, "c"))
        assert os.path.isdir(os.path.join(home_path, "d"))
        assert os.path.isdir(os.path.join(home_path, "d", "e"))
        assert os.path.isfile(os.path.join(home_path, "d", "f"))
        assert os.path.isdir(os.path.join(home_path, "g"))
        assert os.path.isdir(os.path.join(home_path, "g", "h"))
        assert os.path.isdir(os.path.join(home_path, "g", "h", "i"))
        assert os.path.isdir(os.path.join(home_path, "g", "h", "i", "j"))
        assert os.path.isfile(os.path.join(home_path, "g", "h", "i", "j", "k"))


@pytest.mark.skip
def test_init_home_dict_real_example():
    with tempfile.TemporaryDirectory() as dirname:
        # fmt: off
        home = {
            ".bashrc": "",
            "bin": {},
            "github": {
                "jwtattack": {},
                "gobuster": {},
                "nmap": {}
            },
            "tools": {
                "seclist": {}
            }

        }
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(homepath=home_path, home_structure=home)
        framework.init()

        assert os.path.isdir(home_path)

        assert os.path.isfile(os.path.join(home_path, ".bashrc"))
        assert os.path.isdir(os.path.join(home_path, "github"))
        assert os.path.isdir(os.path.join(home_path, "github", "jwtattack"))
        assert os.path.isdir(os.path.join(home_path, "github", "gobuster"))
        assert os.path.isdir(os.path.join(home_path, "github", "nmap"))
        assert os.path.isdir(os.path.join(home_path, "tools"))
        assert os.path.isdir(os.path.join(home_path, "tools", "seclist"))


def test_init_home_F_D_real_example():
    with tempfile.TemporaryDirectory() as dirname:
        # fmt: off
        home = [
            F(".bashrc"),
            D("bin"),
            D(
                "github",
                [D("jwtattack"), D("gobuster"), D("nmap")]
            ),
            D("tools", [D("seclist")])
        ]
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(homepath=home_path, home_structure=home)
        framework.init()

        assert os.path.isdir(home_path)

        assert os.path.isfile(os.path.join(home_path, ".bashrc"))
        assert os.path.isdir(os.path.join(home_path, "github"))
        assert os.path.isdir(os.path.join(home_path, "github", "jwtattack"))
        assert os.path.isdir(os.path.join(home_path, "github", "gobuster"))
        assert os.path.isdir(os.path.join(home_path, "github", "nmap"))
        assert os.path.isdir(os.path.join(home_path, "tools"))
        assert os.path.isdir(os.path.join(home_path, "tools", "seclist"))


@pytest.mark.skip
def test_init_home_list_files():
    with tempfile.TemporaryDirectory() as dirname:
        # fmt: off
        home = ["a", "b", "c"]
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(homepath=home_path, home_structure=home)
        framework.init()

        assert os.path.isdir(home_path)
        for path in ["a", "b", "c"]:
            path = os.path.join(home_path, path)
            assert os.path.isfile(path)
            with open(path) as f:
                assert f.read() == ""


def test_init_home_F_content():
    with tempfile.TemporaryDirectory() as dirname:
        # fmt: off
        home = [F("a"), F("b", content="Hello")]
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(homepath=home_path, home_structure=home)
        framework.init()

        assert os.path.isdir(home_path)
        assert os.path.isfile(os.path.join(home_path, "a"))
        assert open(os.path.join(home_path, "a")).read() == ""
        assert os.path.isfile(os.path.join(home_path, "b"))
        assert open(os.path.join(home_path, "b")).read() == "Hello"


@pytest.mark.skip
def test_init_home_F_substitute():
    """Test variables substitutions"""
    with tempfile.TemporaryDirectory() as dirname:
        # fmt: off
        home = [F("a"), F("b", content="my age is $age", substitute=True)]
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(
            homepath=home_path, home_structure=home, variables={"age": 30}
        )
        framework.init()

        assert os.path.isdir(home_path)
        assert os.path.isfile(os.path.join(home_path, "a"))
        assert open(os.path.join(home_path, "a")).read() == ""
        assert os.path.isfile(os.path.join(home_path, "b"))
        assert open(os.path.join(home_path, "b")).read() == "my age is 30"


def test_init_home_F_src():
    with tempfile.TemporaryDirectory() as dirname, tempfile.NamedTemporaryFile(
        "w"
    ) as tmpfile:
        # write on file
        tmpfile.file.write("World!")
        tmpfile.file.flush()
        # fmt: off
        home = [F("a"), F("b", content="Hello"), F("c", src=tmpfile.name)]
        # fmt: on
        home_path = os.path.join(dirname, "home")
        framework = mkframework(homepath=home_path, home_structure=home)
        framework.init()

        assert os.path.isdir(home_path)
        assert os.path.isfile(os.path.join(home_path, "a"))
        assert open(os.path.join(home_path, "a")).read() == ""
        assert os.path.isfile(os.path.join(home_path, "b"))
        assert open(os.path.join(home_path, "b")).read() == "Hello"
        assert os.path.isfile(os.path.join(home_path, "c"))
        assert open(os.path.join(home_path, "c")).read() == "World!"


# ========================== #
# test _normalize_home_nodes #
# ========================== #


def test__normalize_home_nodes_list_of_str():
    nodes = ["a", "b", "c"]
    expected = [F("a"), F("b"), F("c")]
    result = normalize_home_structure(nodes)
    assert expected == result


def test__normalize_home_nodes_list_of_str_and_F_D():
    nodes = ["a", "b", "c", F("d"), D("e")]
    expected = [F("a"), F("b"), F("c"), F("d"), D("e")]
    result = normalize_home_structure(nodes)
    assert expected == result


def test__normalize_home_nodes_list_of_str_with_dirs():
    nodes = ["a", "b", "c/"]
    expected = [F("a"), F("b"), D("c")]
    result = normalize_home_structure(nodes)
    assert expected == result


@pytest.mark.skip
def test__normalize_home_nodes_dict():
    # fmt: off
    nodes = {
        "a": {},
        "b": {},
        "c": "",
    }
    # fmt: on
    expected = [D("a"), D("b"), F("c")]
    result = normalize_home_structure(nodes)
    assert expected == result


"""
x = ["a", "b", "c"] +  [F("a"), F("b"), F("C")]
home = {
            ".bashrc": "",
            "bin": {},
            "github": {
                "jwtattack": {},
                "gobuster": {},
                "nmap": {}
            },
            "tools": {
                "seclist": {}
            }

        }
home = [
    F(".bashrc"),
    D("bin"),
    D("github", D("jwtattack"))
]
"""
