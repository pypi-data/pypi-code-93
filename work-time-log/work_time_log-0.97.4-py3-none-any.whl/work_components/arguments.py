#!/usr/bin/env python3
""" Argument names and the `Arguments` class. """

import argparse
import datetime as dt
import textwrap
from typing import Dict, List, Optional, Union

from work_components import consts

NAME = "work"

# Commands
# fmt: off
START_NAME =    "start"
STOP_NAME =     "stop"
CANCEL_NAME =   "cancel"
RESUME_NAME =   "resume"
SWITCH_NAMES = ["switch", "pause"]
ADD_NAME =      "add"
STATUS_NAMES = ["status", "s"]
HOURS_NAMES =  ["hours", "h"]
LIST_NAMES =   ["list", "ls"]
DAY_NAME =      "day"
EXPORT_NAME =   "export"
EDIT_NAMES =   ["edit", "e"]
REMOVE_NAMES = ["remove", "rm"]
RECESS_NAME =   "recess"

CONFIG_NAME =   "config"
REHASH_NAME =   "rehash"
MAINTENANCE_NAMES = [CONFIG_NAME, REHASH_NAME]
# fmt: on


class Mode:
    """ Definition of a 'mode', such as `work start`. """

    def __init__(
        self,
        names: Union[str, List[str]],
        help: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.names = [names] if isinstance(names, str) else names
        self.help = help
        self.description = description or help
        self.parents: List[argparse.ArgumentParser] = []

    def add_as_parser(self, subparsers) -> argparse.ArgumentParser:
        """
        Add this mode to the subparsers action as a new mode parser and
        return the created parser object.
        """
        aliases = self.names[1:] if len(self.names) > 1 else []
        return subparsers.add_parser(
            self.names[0],
            aliases=aliases,
            help=self.help,
            description=self.description,
            parents=self.parents,
        )

    def create_fish_completion(self, all_modes: List[str]) -> str:
        for field in ["help", "description"]:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].replace('"', '\\"')

        # Right now, we intentionally ignore aliases.
        return (
            f"complete --command {NAME}"
            f" --arguments \"{' '.join(self.names)}\""
            f" --description \"{self.help or self.description or ''}\""
            f" --condition \"not __fish_seen_subcommand_from {' '.join(all_modes)}\""
        )


MODES: Dict[str, Mode] = {
    START_NAME: Mode(START_NAME, help="Start the protocol"),
    STOP_NAME: Mode(STOP_NAME, help="Stop the protocol"),
    ADD_NAME: Mode(ADD_NAME, help="Add a protocol entry"),
    SWITCH_NAMES[0]: Mode(
        SWITCH_NAMES,
        help="Short-hand for stop & start",
        description=(
            "A short-hand for stop and start. Flags are passed to stop, meaning they "
            "refer to the stopped run."
        ),
    ),
    CANCEL_NAME: Mode(CANCEL_NAME, help="Cancel the current run"),
    RESUME_NAME: Mode(RESUME_NAME, help='Resume the last run today (undo "work stop")'),
    STATUS_NAMES[0]: Mode(STATUS_NAMES, help="Print the current status"),
    HOURS_NAMES[0]: Mode(HOURS_NAMES, help="Calculate hours worked"),
    LIST_NAMES[0]: Mode(
        LIST_NAMES,
        help="List protocol records",
        description=(
            "List protocol records (by default the current day)."
            " For other ranges use the optional arguments."
        ),
    ),
    DAY_NAME: Mode(
        DAY_NAME,
        help="List the current day with all details.",
        description=(
            "List the current day with all details. Shorthand for "
            '"list --include-active --with-breaks --list-empty"'
        ),
    ),
    EXPORT_NAME: Mode(EXPORT_NAME, help="Export records as CSV."),
    EDIT_NAMES[0]: Mode(
        EDIT_NAMES,
        help="Edit protocol records",
        description="Edit protocol records (by default from the current day)",
    ),
    REMOVE_NAMES[0]: Mode(
        REMOVE_NAMES,
        help="Remove records from the protocol",
        description="Remove records from the protocol (by default from the current day)",
    ),
    RECESS_NAME: Mode(
        RECESS_NAME,
        help="Manage free days (vacation, holidays, ...)",
        description="Manage free days (vacation, holidays, ...). Default mode: --list",
    ),
    CONFIG_NAME: Mode(CONFIG_NAME, help="Check and interact with the configuration"),
    REHASH_NAME: Mode(
        REHASH_NAME, help="Recompute verification checksum after manual edits"
    ),
}


class Arguments:
    """ Allows creating parsers or completions. """

    @staticmethod
    def create_argparser(version, program) -> argparse.ArgumentParser:
        """ Create an `ArgumentParser` instance and return it. """

        parser = argparse.ArgumentParser(
            prog=NAME,
            epilog="To find out more, check the help page of individual modes.",
        )
        # fmt: off
        parser.add_argument("-H", "--help-verbose", action="store_true", help="A longer help output, similar to a man page.")
        parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {version}")
        parser.add_argument("-d", "--debug", action="store_true", help="Use a debug directory")
        parser.add_argument("-y", "--dry-run", action="store_true", help="Only print output")
        # fmt: on

        modes = parser.add_subparsers(title="modes", dest="mode")

        # Shared help texts
        date_help_text = 'Either a date (such as "12.", "1.1." or "5.09.19"), or any prefix of "today" or "yesterday".'
        # TODO Consider if / how the keyword "again" should be documented
        time_help_text = 'Either a time (such as "1:20" or "12:1") or "now" for the current time (rounded).'

        # Parent parser for optional entry fields

        category_message_parent = argparse.ArgumentParser(add_help=False)
        category_message_parent.add_argument(
            "-c",
            "--category",
            metavar="C",
            help="Categorize the entry. Anything is allowed, but this will be used for summarization.",
        )
        category_message_parent.add_argument(
            "-m", "--message", metavar="M", help="Free-text description of the entry."
        )

        MODES[STOP_NAME].parents.append(category_message_parent)
        MODES[ADD_NAME].parents.append(category_message_parent)
        MODES[SWITCH_NAMES[0]].parents.append(category_message_parent)

        # SINGLE TIME modes

        start_mode = MODES[START_NAME].add_as_parser(modes)
        start_mode.set_defaults(func=program.start)
        start_mode.add_argument(
            "--force",
            action="store_true",
            help="Start anew even if a run is already active.",
        )

        stop_mode = MODES[STOP_NAME].add_as_parser(modes)
        stop_mode.set_defaults(func=program.stop)

        # start / stop have a single time argument
        for single_time_mode in [start_mode, stop_mode]:
            single_time_mode.add_argument("time", metavar="TIME", help=time_help_text)

        # DOUBLE TIME modes

        add_mode = MODES[ADD_NAME].add_as_parser(modes)
        add_mode.set_defaults(func=program.add)
        add_mode.add_argument("-d", "--date", metavar="DATE", help=date_help_text)
        add_mode.add_argument(
            "time_from", metavar="TIME", help="Start time. " + time_help_text
        )
        add_mode.add_argument(
            "time_to", metavar="TIME", help="End time. " + time_help_text
        )
        add_mode.add_argument(
            "--force",
            action="store_true",
            help=(
                "Add even if an existing entry overlaps. "
                "This can result in three outcomes: The old entry will be... "
                "(1) subsumed (removed). "
                "(2) cut (shortened) to make space. "
                "(3) split in two parts, which are then cut (see 2)."
            ),
        )

        switch_mode = MODES[SWITCH_NAMES[0]].add_as_parser(modes)
        switch_mode.set_defaults(func=program.switch)
        switch_mode.add_argument(
            "time_s",
            metavar="TIME",
            help=("The time to switch runs at. TIME: " + time_help_text),
        )
        switch_mode.add_argument(
            "-s",
            "--start",
            metavar="TIME",
            help="Instead of restarting immediately, start the next run at TIME.",
        )

        # STATE dependent modes

        cancel_mode = MODES[CANCEL_NAME].add_as_parser(modes)
        cancel_mode.set_defaults(func=program.cancel)

        resume_mode = MODES[RESUME_NAME].add_as_parser(modes)
        resume_mode.set_defaults(func=program.resume)
        resume_mode.add_argument(
            "--force",
            action="store_true",
            help="Resume even if a run is active.",
        )

        status_mode = MODES[STATUS_NAMES[0]].add_as_parser(modes)
        status_mode.set_defaults(func=program.status)
        status_mode.add_argument(
            "-o", "--oneline", action="store_true", help="Print status in one line."
        )

        hours_mode = MODES[HOURS_NAMES[0]].add_as_parser(modes)
        hours_mode.set_defaults(func=program.hours)
        hours_mode.add_argument(
            "-d",
            "--workday",
            action="store_true",
            dest="h_workday",
            help="Also show the end time of a complete workday with respect to the week balance.",
        )
        hours_mode.add_argument(
            "-b",
            "--balance",
            action="store_true",
            dest="h_balance",
            help="Also show the current week balance, including all hours worked today.",
        )
        hours_mode.add_argument(
            "-u",
            "--until",
            metavar="T",
            dest="h_until",
            help="Also show the hours that will have been worked at the given time.",
        )
        hours_target = hours_mode.add_mutually_exclusive_group()
        target_arg_help_text_stub = "Also show the end time for "
        hours_target.add_argument(
            "-t",
            "--target",
            metavar="H:M",
            dest="h_target",
            type=str,
            help=target_arg_help_text_stub
            + "a workday of the specified length in hours:minutes.",
        )
        hours_target.add_argument(
            "-8",
            "--eight",
            action="store_const",
            dest="h_target",
            const="8",
            help=target_arg_help_text_stub
            + "an 8 hour day (equivalent to --target 8).",
        )

        # Parent parser for date ranges
        date_selection_parent = argparse.ArgumentParser(add_help=False)
        date_selection_modes = date_selection_parent.add_mutually_exclusive_group()
        date_selection_modes.add_argument(
            "-d", "--date", metavar="DATE", help=f"Any DATE – {date_help_text}"
        )
        date_selection_modes.add_argument(
            "-1",
            "--yesterday",
            action="store_const",
            dest="date",
            const="yesterday",
            help="Short-hand for --date yesterday.",
        )
        date_selection_modes.add_argument(
            "-D",
            "--day",
            metavar="DAY",
            help='A weekday (full or abbreviated), such as "Mon", "su" or "wednesday".',
        )
        date_selection_modes.add_argument(
            "-p",
            "--period",
            metavar="DATE",
            nargs=2,
            help="A specified period, defined by two DATEs.",
        )
        date_selection_modes.add_argument(
            "-w",
            "--week",
            type=int,
            nargs="?",
            const=-1,
            help="The specified week (default: current week). Expects a week number.",
        )
        date_selection_modes.add_argument(
            "-m", "--month", action="store_true", help="The current month."
        )

        MODES[LIST_NAMES[0]].parents.append(date_selection_parent)
        MODES[EXPORT_NAME].parents.append(date_selection_parent)

        # PROTOCOL interaction modes

        list_mode = MODES[LIST_NAMES[0]].add_as_parser(modes)
        list_mode.set_defaults(func=program.list_entries)
        list_mode.add_argument(
            "-e", "--list-empty", action="store_true", help="Include empty days."
        )
        list_mode.add_argument(
            "-i",
            "--include-active",
            action="store_true",
            help="Include the active run.",
        )
        list_mode.add_argument(
            "-b", "--with-breaks", action="store_true", help="Also show break lengths."
        )
        list_mode.add_argument(
            "-t",
            "--only-time",
            action="store_true",
            help="Only show record times and omit all optional record attributes.",
        )

        day_mode = MODES[DAY_NAME].add_as_parser(modes)
        day_mode.set_defaults(func=program.day)

        export_mode = MODES[EXPORT_NAME].add_as_parser(modes)
        export_mode.set_defaults(func=program.export)

        edit_mode = MODES[EDIT_NAMES[0]].add_as_parser(modes)
        edit_mode.set_defaults(func=program.edit)

        remove_mode = MODES[REMOVE_NAMES[0]].add_as_parser(modes)
        remove_mode.set_defaults(func=program.remove)

        for manipulation_mode in [edit_mode, remove_mode]:
            manipulation_mode.add_argument(
                "-d", "--date", metavar="DATE", help=date_help_text
            )

        # RECESS management

        recess_mode = MODES[RECESS_NAME].add_as_parser(modes)
        recess_mode.set_defaults(func=program.recess)
        recess_mode_modes = recess_mode.add_mutually_exclusive_group()
        recess_mode_modes.add_argument(
            "--add-vacation",
            nargs="+",
            metavar="DATE",
            help="Add a vacation. Either a single day or a begin and end. DATE: "
            + date_help_text,
        )
        recess_mode_modes.add_argument(
            "--add-holiday",
            metavar="DATE",
            help="Add a holiday. DATE: " + date_help_text,
        )
        recess_mode_modes.add_argument(
            "--add-reduced-day",
            nargs=2,
            metavar=("DATE", "HOURS"),
            help="Add a reduced hour day on DATE (see DATE) with HOURS being a value in ({}, {}).".format(
                *consts.ALLOWED_WORK_HOURS
            ),
        )
        recess_mode_modes.add_argument(
            "--remove", nargs="+", metavar="DATE", help="Remove free day(s)."
        )
        recess_mode_modes.add_argument(
            "--list",
            metavar="YEAR",
            type=int,
            nargs="?",
            const=dt.date.today().year,
            help="List recess days of YEAR (default: current year)",
        )

        # MAINTENANCE modes

        config_mode = MODES[CONFIG_NAME].add_as_parser(modes)
        config_mode.set_defaults(func=program.config)
        config_mode_modes = config_mode.add_mutually_exclusive_group()
        config_mode_modes.add_argument(
            "-p",
            "--path",
            action="store_true",
            help="Default mode: Print the path of the runtime configuration file.",
        )
        config_mode_modes.add_argument(
            "-c",
            "--create",
            action="store_true",
            help="Create a default runtime configuration with all currently active options.",
        )
        config_mode_modes.add_argument(
            "-e",
            "--expected",
            action="store_true",
            help="Print the contents of an expected runtime configuration file.",
        )
        config_mode_modes.add_argument(
            "-s",
            "--see",
            choices=["dir", "expected hours"],
            help="Check how work is configured (see --help for options).",
        )

        rehash_mode = MODES[REHASH_NAME].add_as_parser(modes)
        rehash_mode.set_defaults(func=program.rehash)

        return parser

    @staticmethod
    def print_verbose_help(parser: argparse.ArgumentParser) -> None:
        """ Print the parser's help with more detailed help below it. """

        parser.print_help()

        two_spaces: str = " " * 2
        fill = lambda s: textwrap.fill(
            s,
            width=80,
            initial_indent=two_spaces,
            subsequent_indent=two_spaces,
            replace_whitespace=False,
            drop_whitespace=False,
        )
        new_epilog = lambda t, c: "\n\n" + t + ":\n" + "\n".join(map(fill, c))

        # fmt: off
        print(
            new_epilog(
                t="rounding",
                c=[
                    "Times are rounded in your favor, to the next full 15 minutes, when"
                        " you enter 'now' instead of an exact time. For example:",
                    "- 'work start now' at 10:14 starts at 10:00",
                    "- 'work stop now' at  19:01 stops at  19:15",
                ],
            )
            + new_epilog(
                t="expected hours",
                c=[
                    "For some sub-functions (mainly status and hours), you will be nudged to work "
                        "no more, but also no less, than the expected hours. By default, work will "
                        "expect 8 hours for every workday (Mon–Fri). Two ways exist to define days "
                        "where less hours should be expected:",
                    '- holidays: In the RC file, you can define days as "reduced_hour_days"',
                    "- vacation: Use work vacation --add to add vacation days (expect 0 hours)",
                ],
            )
            + new_epilog(
                t="balance",
                c=[
                    "Based on the expected hours and the time worked, two balances are "
                        "calculated:",
                    "1) Week balance (shown in status): Total over-/undertime "
                        "accumulated over the current week (starting Monday), up to "
                        "the day before today.",
                    "2) Current balance (shown in hours --balance): This shows "
                        "the hours you need to work that day and how many are remaining.",
                ],
            )
        )
        # fmt: on
