# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests the setup systems
"""

import sys
from contextlib import redirect_stdout
from io import StringIO

import pytest

from portmod._cli.main import main
from portmod.globals import env
from portmod.prefix import get_prefixes
from portmod.repos import get_local_repos

from .env import setup_env, tear_down_env


@pytest.fixture(autouse=True)
def setup():
    """
    Sets up test repo for querying
    """
    yield setup_env("test")
    tear_down_env()


def test_init_prefix():
    """Tests prefix creation"""
    sys.argv = ["portmod", "init", "test2", "test", "--no-confirm"]
    main()

    assert get_prefixes()["test2"] == "test"
    sys.argv = ["portmod", "test2", "destroy", "--no-confirm"]
    main()
    assert "test2" not in get_prefixes()


def test_add_repo():
    """Tests adding repositories automatically"""
    stringio = StringIO()
    with redirect_stdout(stringio):
        sys.argv = ["portmod", "test", "select", "repo", "list"]
        main()
    assert "blank" in stringio.getvalue()

    sys.argv = ["portmod", "test", "select", "repo", "add", "blank"]
    main()

    assert any(repo.name == "blank" for repo in env.REPOS)
    assert "blank" in get_local_repos()
