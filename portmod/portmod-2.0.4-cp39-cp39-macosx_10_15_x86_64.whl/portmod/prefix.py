# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import configparser
import getpass
import os
import re
from functools import lru_cache
from logging import info, warning
from stat import S_IWRITE
from typing import Mapping

from portmodlib.l10n import l10n

from .globals import env
from .repo.metadata import get_archs
from .repos import get_local_repos


class InvalidPrefix(RuntimeError):
    def __init__(self, prefix):
        self.prefix = prefix

    def __str__(self):
        return l10n("invalid-prefix", prefix=self.prefix)


class PrefixExistsError(RuntimeError):
    def __init__(self, prefix):
        self.prefix = prefix

    def __str__(self):
        return l10n("prefix-exists", prefix=self.prefix)


@lru_cache()
def get_prefixes() -> Mapping[str, str]:
    """Returns a mapping of prefixes to their architectures"""
    prefixes = {}
    if os.path.exists(env.PREFIX_FILE):
        with open(env.PREFIX_FILE, "r") as file:
            for line in file.readlines():
                elems = re.sub("#.*", "", line).strip().split()
                if elems:
                    # Note: Additional information at the end of the line is ignored.
                    prefix = elems[0]
                    arch = elems[1]
                    prefixes[prefix] = arch

    return prefixes


def remove_prefix(prefix: str):
    """
    Removes a prefix the prefix file

    Does not modify the prefix's data
    """
    stat = os.stat(env.PREFIX_FILE)
    os.chmod(env.PREFIX_FILE, stat.st_mode | S_IWRITE, follow_symlinks=True)

    info(l10n("removing-prefix", prefix=prefix))
    with open(env.PREFIX_FILE) as file:
        lines = file.readlines()
        origlines = list(lines)
        for index, line in enumerate(lines):
            file_prefix, _ = line.split()
            if prefix == file_prefix:
                del lines[index]

    with open(env.PREFIX_FILE, "w") as file:
        if lines != origlines:
            file.writelines(lines)

    stat = os.stat(env.PREFIX_FILE)
    os.chmod(env.PREFIX_FILE, stat.st_mode - S_IWRITE, follow_symlinks=True)

    get_prefixes.cache_clear()


def add_prefix(prefix: str, arch: str):
    """Adds a new prefix"""

    invalid_prefixes = {"news", "sync", "mirror"}

    if prefix in invalid_prefixes:
        raise InvalidPrefix(prefix)

    if prefix in get_prefixes():
        raise PrefixExistsError(prefix)

    arch_options = set()
    for repo in get_local_repos().values():
        arch_options |= get_archs(repo.location)

    if arch not in arch_options:
        warning(l10n("unknown-arch", arch=arch))

    # Add new prefix to the prefix file
    if os.path.exists(env.PREFIX_FILE):
        stat = os.stat(env.PREFIX_FILE)
        os.chmod(env.PREFIX_FILE, stat.st_mode | S_IWRITE, follow_symlinks=True)

    os.makedirs(os.path.dirname(env.PREFIX_FILE), exist_ok=True)

    with open(env.PREFIX_FILE, "a") as file:
        print(prefix, arch, file=file)

    stat = os.stat(env.PREFIX_FILE)
    os.chmod(env.PREFIX_FILE, stat.st_mode - S_IWRITE, follow_symlinks=True)

    get_prefixes.cache_clear()

    env.set_prefix(prefix)

    # Ensure that INSTALLED_DB exists
    if not os.path.exists(env.prefix().INSTALLED_DB):
        import git

        # Initialize as git repo
        os.makedirs(env.prefix().INSTALLED_DB)
        gitrepo = git.Repo.init(env.prefix().INSTALLED_DB)
        # This repository is for local purposes only.
        # We don't want to worry about prompts for the user's gpg key password
        localconfig = gitrepo.config_writer()
        localconfig.set_value("commit", "gpgsign", False)
        USER = getpass.getuser()

        try:
            # May throw TypeError if GitPython<3.0.5
            globalconfig = git.config.GitConfigParser()
            globalconfig.get_value("user", "name")
            globalconfig.get_value("user", "email")
        except (TypeError, configparser.NoOptionError, configparser.NoSectionError):
            # Set the user name and email if they aren't in a global config
            localconfig.set_value("user", "name", f"{USER}")
            localconfig.set_value("user", "email", f"{USER}@example.com")

        localconfig.release()

    get_prefixes.cache_clear()
    info(l10n("initialized-prefix", prefix=prefix))
