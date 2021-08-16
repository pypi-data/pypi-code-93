#!/usr/bin/env python3
"""JailBase

Usage:
  jailbase sources [--log-level=<level>] [--cache=<dir>] [--json] [--limit=<int>] [--all] [--includes=<csv>] [--excludes=<csv>]
  jailbase recent <source_id> [--log-level=<level>] [--cache=<dir>] [--json] [--limit=<int>] [--all] [--includes=<csv>] [--excludes=<csv>]
  jailbase (-h | --help)
  jailbase --version

Options:
  -h --help            Show this screen.
  --version            Show version.
  --log-level=<level>  Logging level verbosity [default: info].
  --cache=<dir>        Cache request calls to directory [default: *NONE*].
  --json               Output a json
  --limit=<int>        The number of elments to display [default: 10]
  --all                Show all entries
  -i --includes=<csv>  Columns to include
  -i --excludes=<csv>  Columns to excludes

"""
import logging
import json
from typing import Callable
from itertools import islice

from tabulate import tabulate
from docopt import docopt

from jailbase.jailbase import JailBase, Source, Record


def setup_logger(level_name):
    level = logging.getLevelName(level_name.upper())
    logging.basicConfig(
        level=level, format="%(name)s - %(levelname)s - %(message)s",
    )


def print_to_console(data, data_class, **kwargs):
    if kwargs.get("--all", False):
        data = data
    else:
        data = islice(data, int(kwargs.get("--limit", 10)))

    includes = list(filter(lambda x: x, (kwargs["--includes"] or "").split(",")))
    excludes = list(filter(lambda x: x, (kwargs["--excludes"] or "").split(",")))

    if kwargs.get("--json", False):
        display = json.dumps([entry.to_dict() for entry in data], indent=2)
    else:
        display = tabulate(
            [data_class.fields(data_class, includes, excludes)]
            + [entry.row(includes, excludes) for entry in data],
            headers="firstrow",
        )

    print(display)


def sources(jailbase, **kwargs):
    jailbase_sources = jailbase.sources()
    print_to_console(jailbase_sources, Source, **kwargs)


def recent(jailbase, **kwargs):
    sources = jailbase.sources()
    source_id = kwargs.get("<source_id>")
    source_ids = [source.source_id for source in sources]
    if source_id not in source_ids:
        logging.fatal("Invalid source id: '%s'", source_id)
        logging.info("Pick from the following: [%s]", ", ".join(source_ids))

    recents = jailbase.recent(source_id)
    print_to_console(recents, Record, **kwargs)


def main():
    args = docopt(__doc__, version="Naval Fate 2.0")
    cache = args["--cache"] if args["--cache"] != "*NONE*" else False
    jailbase = JailBase(cache=cache)
    setup_logger(args["--log-level"])
    for func_name, func in filter(
        lambda kv: isinstance(kv[1], Callable), globals().items()
    ):
        if func_name in args and args[func_name]:
            func(jailbase, **args)
