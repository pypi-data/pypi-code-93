import logging
import os
import dbm
from pathlib import Path
import shelve

import click
from click_log.core import _normalize_logger
from xdg import XDG_CONFIG_HOME

logger = logging.getLogger("nts")

configfile_dir = XDG_CONFIG_HOME / "ntscli-client"
if "$HOME" in str(configfile_dir):
    user_home = Path("~").expanduser()
    configfile_dir = user_home / XDG_CONFIG_HOME.relative_to("$HOME") / "ntscli-client"
os.makedirs(configfile_dir.resolve(), exist_ok=True)

shelve_path = configfile_dir / "last"


class CachedLogLevel:
    LEVEL_KEY = "level"
    DEFAULT_LEVEL = "ERROR"

    @property
    def level(self) -> str:
        try:
            with shelve.open(str(shelve_path), flag="r") as open_shelve_file:
                return open_shelve_file[self.LEVEL_KEY]
        except dbm.error:
            return CachedLogLevel.DEFAULT_LEVEL

    @level.setter
    def level(self, value: str):
        with shelve.open(str(shelve_path)) as open_shelve_file:
            open_shelve_file[self.LEVEL_KEY] = value


def nts_verbosity_option(logger=None, *names, **kwargs):
    """A decorator that adds a `--verbosity, -v` option to the decorated
    command.

    Name can be configured through ``*names``. Keyword arguments are passed to
    the underlying ``click.option`` decorator.
    """

    if not names:
        names = ["--verbosity", "-v"]
    if isinstance(logger, str) and logger.startswith("-"):
        raise ValueError("Since click-log 0.2.0, the first argument must now " "be a logger.")

    kwargs.setdefault("default", "CURRENT")
    kwargs.setdefault("metavar", "LVL")
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("help", "Either CRITICAL, ERROR, WARNING, INFO or DEBUG")
    kwargs.setdefault("is_eager", True)

    logger = _normalize_logger(logger)

    def decorator(f):
        def _set_level(ctx, param, user_requested_value: str):
            if user_requested_value.lower() == "current":  # the new default
                user_requested_value = CachedLogLevel().level
            else:
                CachedLogLevel().level = user_requested_value

            x = getattr(logging, user_requested_value.upper(), None)
            if x is None:
                raise click.BadParameter("Must be CRITICAL, ERROR, WARNING, INFO or DEBUG, not {}")
            logger.setLevel(x)

        return click.option(*names, callback=_set_level, **kwargs)(f)

    return decorator
