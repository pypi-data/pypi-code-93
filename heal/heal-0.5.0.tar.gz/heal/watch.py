import json
import subprocess
from operator import itemgetter
from pathlib import Path
from typing import List, Any, Tuple

import yaml

from heal.util import ENCODING


def read_config(directory: Path) -> List[Any]:
    """
    Extracts every JSON or YAML configuration element from the files in the given directory.

    :param directory: Path to the configuration directory
    :return: aggregated list of configuration elements
    """

    print("reading configuration")
    config = []

    for path in directory.iterdir():
        try:
            text = path.read_text(encoding=ENCODING)
        except (OSError, ValueError) as error:
            print(f"'{path.relative_to(directory)}' ignored: {error}")
            continue

        data = yaml.load(text, Loader=yaml.BaseLoader)
        if not isinstance(data, list):
            print(f"'{path.relative_to(directory)}' ignored: not a proper yaml or json list")
        else:
            config.extend(data)

    return config


def filter_modes_and_checks(config: List[Any]) -> Tuple[List[dict], List[dict]]:
    """
    Validates and splits the given configuration elements into modes and checks.

    :param config: list of configuration elements
    :return: two sorted lists, one of modes and one of checks
    """

    print("filtering modes and checks")
    modes, checks = [], []

    for item in config:
        if not isinstance(item, dict):
            print("ignored, not a dictionary:", json.dumps(item))
            continue

        if not all(isinstance(value, str) for value in item.values()):
            print("ignored, values cannot be lists or dictionaries:", json.dumps(item))
            continue

        keys = item.keys()
        if keys == {"mode", "if"}:  # "mode" and "if" are mandatory for modes
            modes.append(item)
        elif keys == {"check", "fix", "rank"} or keys == {"check", "fix", "rank", "when"}:  # "check", "fix" and "rank" are mandatory for checks, "when" is optional
            try:
                item["rank"] = int(item["rank"])  # converts the rank to an integer so that checks can be sorted
                checks.append(item)
            except ValueError:
                print("ignored, rank must be an integer:", json.dumps(item))
        else:
            print('ignored, keys must match {"mode", "if"} or {"check", "fix", "rank"} or {"check", "fix", "rank", "when"}:', json.dumps(item))

    return sorted(modes, key=itemgetter("mode")), sorted(checks, key=itemgetter("rank"))  # modes are sorted by name, checks by rank


def filter_active_modes(modes: List[dict]) -> List[str]:
    """
    Executes the given modes' condition and returns the names of those that succeeds.

    :param modes: list of available modes
    :return: the names of the modes whose condition executed successfully
    """

    return [mode.get("mode") for mode in modes if subprocess.run(mode.get("if"), shell=True).returncode == 0]


def filter_active_checks(active_modes: List[str], checks: List[dict]) -> List[dict]:
    """
    :param active_modes: list of active modes
    :param checks: list of available checks
    :return: the list of active checks, i.e. checks without mode or with an active one
    """

    print("filtering active checks")
    active_checks = []

    for check in checks:
        if not check.get("when") or check.get("when") in active_modes:
            print("active:", json.dumps(check))
            active_checks.append(check)

    return active_checks


class Watcher:
    """
    Will watch over the given configuration directory and monitor possible changes:

    * directory timestamp
    * checks
    * active modes
    * active checks

    :param configuration_directory: obviously
    """

    def __init__(self, configuration_directory: Path):
        self.configuration_directory = configuration_directory
        self.mtime = 0
        self.modes = []
        self.checks = []
        self.active_modes = []
        self.active_checks = []

    def configuration_directory_has_changed(self) -> bool:
        """
        :return: whether or not the configuration directory has changed since last call
        """

        # monitoring the directory modification timestamp doesn't cover every possible file change but it's very cheap
        new_mtime = self.configuration_directory.stat().st_mtime
        if new_mtime == self.mtime:
            return False
        print("configuration directory has changed")
        self.mtime = new_mtime
        return True

    def checks_have_changed(self) -> bool:
        """
        :return: whether or not the checks have changed since last call
        """

        # caution: here modes are refreshed as a prerequisite for monitoring the active modes
        self.modes, new_checks = filter_modes_and_checks(read_config(self.configuration_directory))
        if new_checks == self.checks:
            return False
        print("checks have changed")
        self.checks = new_checks
        return True

    def active_modes_have_changed(self) -> bool:
        """
        :return: whether or not the active modes have changed since last call
        """

        new_active_modes = filter_active_modes(self.modes)
        if new_active_modes == self.active_modes:
            return False
        print("active modes have changed:", new_active_modes)
        self.active_modes = new_active_modes
        return True

    def refresh_active_checks_if_necessary(self) -> None:
        """
        Refreshes the active checks only if the configuration directory, the checks or the active modes have changed.
        It may not be the most performant, but the logs are much clearer.
        """

        # the order is important: active_modes_have_changed() needs the modes refreshed by checks_have_changed()
        # also: every function needs to be called, hence the use of "|" instead of "or" which would be lazily evaluated
        if (self.configuration_directory_has_changed() and self.checks_have_changed()) | self.active_modes_have_changed():
            self.active_checks = filter_active_checks(self.active_modes, self.checks)
