# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Functions to set up and tear down a testing environment
"""

import os
import shutil
import sys
from locale import LC_ALL, setlocale
from logging import error
from tempfile import gettempdir
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import git

from portmod.cache import cache
from portmod.config import _create_config_placeholder, get_config
from portmod.globals import env
from portmod.prefix import add_prefix, get_prefixes
from portmod.repo.profiles import profile_parents
from portmod.repos import Repo
from portmod.sync import sync
from portmodlib.fs import onerror
from portmodlib.log import init_logger

TEST_REPO_DIR = os.path.join(os.path.dirname(__file__), "testrepo")
TEST_REPO = Repo("test", TEST_REPO_DIR, priority=-1000)
_TMP_FUNC = None
TESTDIR: Optional[str] = None
OLD: Optional[Dict[str, Any]] = None
OLD_CWD: Optional[str] = None
OLD_REPOS: List[Repo]


def set_test_repo():
    """Replaces the repo list with one that just contains the test repo"""
    global OLD_REPOS

    with open(env.REPOS_FILE, "w") as file:
        print("[test]", file=file)
        print(f"location = {TEST_REPO.location}", file=file)
        print("auto_sync = False", file=file)

    OLD_REPOS = env.REPOS
    env.REPOS = [TEST_REPO]
    env.prefix().REPOS = [TEST_REPO]


def setup_env(profile):
    """
    Sets up an entire testing environment
    All file writes will occur within a temporary directory as a result
    """
    global OLD, OLD_CWD, TESTDIR
    # Use C locale. This will fail to read files containing unicode,
    # unless the files are supposed to and we explicitly open them as utf-8
    setlocale(LC_ALL, None)
    init_logger(SimpleNamespace(verbose=False, quiet=False))

    cwd = os.getcwd()
    get_config.cache_clear()  # type: ignore
    OLD = env.__dict__
    OLD_CWD = cwd
    TESTDIR = os.path.join(gettempdir(), "portmod.test")
    env.CONFIG_DIR = os.path.join(TESTDIR, "config")
    env.CACHE_DIR = os.path.join(TESTDIR, "cache")
    env.DATA_DIR = os.path.join(TESTDIR, "local")
    env.__init__()  # type: ignore
    if "test" not in get_prefixes():
        add_prefix("test", "test")
        get_prefixes.cache_clear()
    env.set_prefix("test")

    env.INTERACTIVE = False
    env.TESTING = True
    env.DEBUG = True
    os.makedirs(env.prefix().CONFIG_DIR, exist_ok=True)
    gitrepo = git.Repo.init(env.prefix().INSTALLED_DB)
    gitrepo.config_writer().set_value("commit", "gpgsign", False).release()
    gitrepo.config_writer().set_value("user", "email", "pytest@example.com").release()
    gitrepo.config_writer().set_value("user", "name", "pytest").release()
    os.makedirs(TESTDIR, exist_ok=True)
    os.makedirs(os.path.join(TESTDIR, "local"), exist_ok=True)
    set_test_repo()
    sync(env.REPOS)
    set_test_repo()
    select_profile(profile)
    get_config.cache_clear()  # type: ignore
    _create_config_placeholder()
    with open(env.prefix().CONFIG, "a") as file:
        print('REPOS = "test"', file=file)

    os.environ["INSTALL_DEST"] = str(get_config()["INSTALL_DEST"])
    return {
        "testdir": TESTDIR,
        "config": f"{TESTDIR}/config.cfg",
        "config_ini": f"{TESTDIR}/config.ini",
    }


def rmtree(path: str):
    """Custom rmtree wrapper to deal with windows problems"""
    if sys.platform == "win32":
        from time import sleep

        iters = 0
        while os.path.exists(path) and iters < 10:
            iters += 1
            try:
                shutil.rmtree(path, onerror=onerror, ignore_errors=True)
            except PermissionError as e:
                error(e)
                sleep(0.01)
    else:
        shutil.rmtree(path, onerror=onerror)


def tear_down_env():
    """
    Reverts env to original state
    """
    assert OLD_CWD and TESTDIR and OLD
    os.chdir(OLD_CWD)
    env.__dict__ = OLD
    get_config.cache_clear()  # type: ignore
    cache.clear()
    if os.path.exists(TESTDIR):
        rmtree(TESTDIR)


def unset_profile():
    """Removes the profile link"""
    linkpath = os.path.join(env.prefix().CONFIG_DIR, "profile")
    if os.path.exists(linkpath):
        os.unlink(linkpath)
    profile_parents.cache_clear()  # type: ignore


def select_profile(profile):
    """Selects the given test repo profile"""
    linkpath = os.path.join(env.prefix().CONFIG_DIR, "profile")
    unset_profile()
    os.symlink(os.path.join(TEST_REPO_DIR, "profiles", profile), linkpath)
    profile_parents.cache_clear()  # type: ignore
