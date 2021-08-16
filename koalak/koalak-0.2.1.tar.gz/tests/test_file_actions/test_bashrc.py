import os
import tempfile

import pytest
from koalak import F, get_unique_framework_name, mkframework
from koalak.frameworks.home_structure import BashrcFileAction


def test_bashrc_empty_bashrc():
    with tempfile.TemporaryDirectory() as dirname, tempfile.NamedTemporaryFile(
        "w"
    ) as tmpfile:
        # fmt: off
        home = [F("script.sh", content="whoami", actions=BashrcFileAction(tmpfile.name))]
        # fmt: on
        home_path = os.path.join(dirname, "home")
        name = get_unique_framework_name()
        framework = mkframework(name, homepath=home_path, home_structure=home)
        framework.init()

        script_path = os.path.join(home_path, "script.sh")
        expected = BashrcFileAction._add_to_bashrc_template.format(
            path=script_path, basename="script.sh", framework_name=name
        )

        with open(tmpfile.name) as f:
            data = f.read()
            assert data == expected
        assert open(script_path).read() == "whoami"


def test_bashrc_not_empty_bashrc():
    """Test action bashtc with an empty bashrc"""
    with tempfile.TemporaryDirectory() as dirname, tempfile.NamedTemporaryFile(
        "w"
    ) as tmpfile:
        bashrc = "alias ls='ls --color=auto'"
        tmpfile.file.write(bashrc)
        tmpfile.file.flush()

        # fmt: off
        home = [F("script.sh", content="whoami", actions=BashrcFileAction(tmpfile.name))]
        # fmt: on
        home_path = os.path.join(dirname, "home")
        name = get_unique_framework_name()
        framework = mkframework(name, homepath=home_path, home_structure=home)
        framework.init()

        script_path = os.path.join(home_path, "script.sh")
        expected = bashrc
        expected += BashrcFileAction._add_to_bashrc_template.format(
            path=script_path, basename="script.sh", framework_name=name
        )

        with open(tmpfile.name) as f:
            data = f.read()
            assert data == expected
        assert open(script_path).read() == "whoami"


@pytest.mark.skip
def test_bashrc_uninstall():
    with tempfile.TemporaryDirectory() as dirname, tempfile.NamedTemporaryFile(
        "w"
    ) as tmpfile:
        # init bashrc file
        bashrc = "alias ls='ls --color=auto'"
        tmpfile.file.write(bashrc)
        tmpfile.file.flush()

        # fmt: off
        home = [F("script.sh", content="whoami", actions=BashrcFileAction(tmpfile.name))]
        # fmt: on
        home_path = os.path.join(dirname, "home")
        name = get_unique_framework_name()
        framework = mkframework(name, homepath=home_path, home_structure=home)
        framework.init()

        script_path = os.path.join(home_path, "script.sh")
        expected = bashrc
        expected += BashrcFileAction._add_to_bashrc_template.format(
            path=script_path, basename="script.sh", framework_name=name
        )

        # check that bashrc added the needed lines
        with open(tmpfile.name) as f:
            data = f.read()
            assert data == expected
        # check the content of our script
        assert open(script_path).read() == "whoami"

        # check that when uninstalling the framework the bashrc return to it's original
        framework.uninstall()
        with open(tmpfile.name) as f:
            data = f.read()
            assert data == bashrc
