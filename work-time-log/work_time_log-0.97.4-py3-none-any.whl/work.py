#!/usr/bin/env python3

""" The work time log app tracks working hours in an interaction model similar to git. """

import csv
from dataclasses import dataclass
import datetime as dt
import os
import sys
from typing import Callable, Dict, List, Optional, Tuple

from work_components import consts, dt_parse, util
from work_components.arguments import (
    ADD_NAME,
    MAINTENANCE_NAMES,
    START_NAME,
    STOP_NAME,
    SWITCH_NAMES,
    Arguments,
)
from work_components.consts import DIRECTORY, DIRECTORY_DEBUG
from work_components.container import ProtocolMeta, Record, sort_and_merge
from work_components.rc_dao import RC
from work_components.recess_dao import RecessDao
from work_components.util import Color, PrinTable
from work_components.work_dao import WorkDao

assert sys.version_info >= (3, 8)

VERSION: str = "0.97.4"

# Formats
TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%d.%m.%Y"
DATE_FORMAT_FULL = "%A, " + DATE_FORMAT


class Work(object):
    def __init__(self):
        self.base_dir: str
        self.dao: WorkDao
        self.recess_dao: RecessDao
        self.configuration: RC

    def _reinit(self, base_dir: str) -> None:
        """ Connect the DAO and load the RC """

        # Connect the DAOs
        self.dao = WorkDao(base_dir)
        self.recess_dao = RecessDao(base_dir)

        # Load and check configuration
        self.configuration = RC.load_rc()

    def main(self) -> None:
        """ Main program flow. """

        # Argument parsing
        parser = Arguments.create_argparser(version=VERSION, program=self)
        args = parser.parse_args()

        if args.help_verbose:
            Arguments.print_verbose_help(parser)
            sys.exit(0)

        # For lack of a required=True argument
        if args.mode is None:
            parser.print_help()
            sys.exit(2)

        if args.dry_run:
            print(">>> Dry run: Only output <<<")

        try:
            # Connect DAO with normal or debug dir and load RC file
            self.base_dir = DIRECTORY if not args.debug else DIRECTORY_DEBUG
            self._reinit(base_dir=self.base_dir)

            # Only verify the protocol and state for non-maintenance modes
            if args.mode not in MAINTENANCE_NAMES:
                self.dao.ensure_protocol_integrity()

                # Restore the state if erroneous, exit if done so.
                self.fix_state()

            args.func(args)
        # Invalid operations are considered part of the program flow and printed
        except InvalidOperationWarning as warn:
            print(warn)
            sys.exit(1)
        # Exceptions are handled depending on the mode
        except Exception as err:
            # Debug mode: Raise
            if args.debug:
                raise err

            # Normal mode: In case of an exception, print the message and exit.
            print(f"{Color.color('ERROR', Color.RED)}: {err}")
            sys.exit(1)

    def fix_state(self) -> None:
        """
        Fix a possibly invalid state. Exits if an invalid state is detected.
        Currently only checks for an active run on a different date than today.
        """

        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        if active_start is None or active_start.date() == dt.date.today():
            return

        # Forgot to stop a run: Run is active, but start date is not today
        print(
            f"Invalid state detected! A run started at {self._readable_dt(active_start)} is still active.\n"
        )

        # Read input, strip and lower
        user_says: str = (
            input(
                'To add to log, enter an end time (%H:%M). Cancel the run with "cancel", abort with "abort":\n'
            )
            .strip()
            .lower()
        )

        if user_says == "abort" or not user_says:
            print("Aborted")
            sys.exit(1)
        elif user_says == "cancel":
            self.dao.cancel_run()
        else:
            # If the string is not parseable, this will raise an exception
            parsed_time: dt.time = dt_parse.parse_time_str(user_says)
            end_time: dt.datetime = dt.datetime.combine(active_start, parsed_time)
            category: str = input("Category? (leave empty for none): ")
            message: str = input("Message?  (leave empty for none): ")
            self._stop(end_time=end_time, category=category, message=message)
            print(f"Stopped run at {self._readable_dt(end_time)}")

        print("\nState fixed. Please retry.")
        sys.exit(1)

    ### Argument parsing / Step two ###

    def get_single_time(self, args) -> dt.datetime:
        """ Resolve the single time argument (start, stop). """

        if args.mode not in [START_NAME, STOP_NAME]:
            raise ValueError("Expecting start or stop mode!")

        time_arg = args.time

        # start and stop do not allow a date other than today
        baseline_date: dt.date = dt.date.today()
        rounding_mode: dt_parse.RoundingMode = dt_parse.RoundingMode.DOWN
        if args.mode == STOP_NAME:
            rounding_mode = dt_parse.RoundingMode.UP

        # Only start should understand "again"
        if args.mode == START_NAME and time_arg == "again":
            entries_today: List[Record] = self.dao.get_entries(date=dt.date.today())
            if not entries_today:
                raise ValueError(
                    'The keyword "again" only works if at least one entry was recorded today.'
                )
            last_entry_ends: dt.datetime = entries_today[-1].end
            assert last_entry_ends.date() == dt.date.today()
            return last_entry_ends

        single_time: dt.datetime = dt_parse.resolve_time_argument(
            argument=time_arg, baseline_date=baseline_date, rounding_mode=rounding_mode
        )

        return single_time

    def get_time_from_and_to(
        self, args, baseline_date: dt.date
    ) -> Tuple[dt.datetime, dt.datetime]:
        """ Resolve the from and to time arguments. """

        if args.mode not in [ADD_NAME, *SWITCH_NAMES]:
            raise ValueError("Expecting add or switch mode!")

        # Add and pause work in reverse: when adding / pausing with "now now" at 12:50, we
        # expect it to resolve to "12:45 13:00", not to "12:50 12:50" or "13:00 12:45".
        from_rounding_mode = dt_parse.RoundingMode.DOWN
        to_rounding_mode = dt_parse.RoundingMode.UP

        time_from: dt.datetime = dt_parse.resolve_time_argument(
            argument=args.time_from,
            baseline_date=baseline_date,
            rounding_mode=from_rounding_mode,
        )
        time_to: dt.datetime = dt_parse.resolve_time_argument(
            argument=args.time_to,
            baseline_date=baseline_date,
            rounding_mode=to_rounding_mode,
        )

        return (time_from, time_to)

    def get_date(self, args) -> dt.date:
        """
        Evaluate the args to find the requested date.
        Modes:
        - Nothing given : Today
        - --date YY       : Parse specified date
        """

        # Date specified by --on
        if args.date:
            return dt_parse.resolve_date_argument(args.date)
        # No date given – use today
        else:
            return dt.date.today()

    def get_selected_days(self, args) -> List[dt.date]:
        """
        Evaluate the args to find the selected days (used in list and export).

        Modes:
        - Nothing given : Today
        - --date X      : Parse specified date (includes --yesterday)
        - --day V       : Parse specified day
        - --period X Y  : A period defined by two dates
        - --week        : Current week
        - --month       : Current month
        """

        if args.period:
            period_start, period_end = [
                dt_parse.resolve_date_argument(x) for x in args.period
            ]
            return util.get_period(period_start=period_start, period_end=period_end)
        elif args.month:
            return self._containing_month(day=dt.date.today())
        elif args.week:
            return self._containing_week(week_no=args.week)
        elif args.day:
            try:
                day_day = dt_parse.resolve_day_argument(argument=args.day)
            except ValueError:
                raise InvalidOperationWarning.cant(
                    "list day", 'given input "' + args.day + '" does not match any day'
                )
            return [day_day]
        # Default: --date / nothing – if nothing is set, this will return "today"
        else:
            try:
                date_day: dt.date = self.get_date(args)
            except ValueError:
                raise InvalidOperationWarning.cant(
                    "list date", 'given input "' + args.date + '" could not be parsed'
                )
            return [date_day]

    ### Modes ###

    # start #

    def start(self, args) -> None:
        """	Start the protocol based on the given arguments. """

        start_time: dt.datetime = self.get_single_time(args)
        self._start(start_time=start_time, force=args.force, dry_run=args.dry_run)
        print(f"Started work at {self._readable_dt(start_time)}")

    def ensure_valid_start_time(
        self,
        start_time: dt.datetime,
        action: str = "start work",
        time_desc: str = "starting time",
    ) -> None:
        """Check if a run could be started with the given start time.
        Raises `InvalidOperationWarning` if not."""

        if self.dao.has_entry(start_time=start_time):
            raise InvalidOperationWarning.cant(
                action, f"an existing record overlaps with the specified {time_desc}"
            )

        if start_time.date() != dt.date.today():
            raise InvalidOperationWarning.cant(action, f"{time_desc} needs to be today")

        # Allows starting only a few minutes early
        m: float = 10
        if start_time > (dt.datetime.now() + dt.timedelta(minutes=m)):
            raise InvalidOperationWarning.cant(
                action, f"{time_desc} may not be more than {m} minutes in the future"
            )

    def _start(
        self, start_time: dt.datetime, force: bool = False, dry_run: bool = False
    ) -> None:
        """
        Start the protocol with the given start time.

        force: If a run is active, overwrite it silently.
        """

        if not force and self.dao.run_active():
            raise InvalidOperationWarning.cant(
                "start work", "a run is still active (add --force to override)"
            )

        self.ensure_valid_start_time(start_time=start_time)

        if not dry_run:
            self.dao.start_run(start_time, force=force)

    # stop #

    def stop(self, args) -> None:
        """ Stop the protocol based on the given arguments. """
        end_time: dt.datetime = self.get_single_time(args)
        self._stop(
            end_time=end_time,
            category=args.category,
            message=args.message,
            dry_run=args.dry_run,
        )
        print(f"Stopped work at {self._readable_dt(end_time)}")

    def _stop(
        self, end_time: dt.datetime, category: str, message: str, dry_run: bool = False
    ) -> None:
        """ Stop the protocol with the given end time. """

        start_time: Optional[dt.datetime] = self.dao.get_start_time()

        if start_time is None:
            raise InvalidOperationWarning.cant(
                "stop work", "no run is currently active"
            )

        self._can_i_add_this(
            start_time=start_time, end_time=end_time, operation="stop work"
        )

        if end_time == start_time:
            self.dao.cancel_run()
            print("End time is identical to start time – run cancelled.")
            return

        # Preconditions met: Run can be stopped.
        if not dry_run:
            self.dao.stop_run(end_time=end_time, category=category, message=message)

    # add #

    def add(self, args) -> None:
        """ Add a protocol entry consisting of start time, end time and optional date flag. """

        start_time: dt.datetime
        end_time: dt.datetime
        baseline_date: dt.date = self.get_date(args)
        start_time, end_time = self.get_time_from_and_to(args, baseline_date)

        self._can_i_add_this(
            start_time=start_time,
            end_time=end_time,
            operation="add entry",
            force=args.force,
        )

        if end_time == start_time:
            print("End time is identical to start time – did nothing.")
            return

        if not args.dry_run:
            self.dao.add_protocol_entry(
                start_time=start_time,
                end_time=end_time,
                category=args.category,
                message=args.message,
                force=args.force,
            )

        # Expectation: Start and end lie on the same day
        print(
            "Added a record from {} to {} {}".format(
                start_time.strftime(TIME_FORMAT),
                end_time.strftime(TIME_FORMAT),
                self._readable_d(start_time.date()),
            )
        )

    def _can_i_add_this(
        self,
        start_time: dt.datetime,
        end_time: dt.datetime,
        operation: str,
        force: bool = False,
    ) -> None:
        """ Shared checks for valid start and end time of a run. Raises InvalidOperationWarning if not. """

        if end_time.date() != start_time.date():
            raise InvalidOperationWarning.cant(
                operation,
                "dates of start and end time differ\n"
                + "Start date:          {}\n".format(start_time.strftime("%d.%m.%Y"))
                + "Requested stop date: {}".format(end_time.strftime("%d.%m.%Y")),
            )

        if end_time < start_time:
            raise InvalidOperationWarning.cant(
                operation,
                f"requested end time is before the start time {self._readable_dt(start_time)}",
            )

        if not force and self.dao.has_entry(start_time=start_time, end_time=end_time):
            raise InvalidOperationWarning.cant(
                operation,
                "an existing record overlaps with the specified time (add --force to override)",
            )

    # switch #

    def switch(self, args) -> None:
        """
        Switch based on the given arguments. Convenience function for stop + start.

        Two functions:
        - switch A B -> stop at time A, start at B (e.g. after taking a break)
        - switch A -> stop at A and immediately start again (e.g. after switching tasks)
        """

        switch_time: dt.datetime = dt_parse.resolve_time_argument(
            args.time_s,
            dt.date.today(),
            rounding_mode=dt_parse.RoundingMode.DOWN,
        )

        # If not specified otherwise, restart immediately at switch time.
        restart_time: dt.datetime = switch_time
        if args.start:
            restart_time = dt_parse.resolve_time_argument(
                args.start, dt.date.today(), rounding_mode=dt_parse.RoundingMode.DOWN
            )

        self._switch(
            switch_time=switch_time,
            restart_time=restart_time,
            category=args.category,
            message=args.message,
            dry_run=args.dry_run,
        )

        if not args.start:
            print(f"Switched work at {self._readable_dt(switch_time)}")
        else:
            print(
                "Stopped work at {} and restarted at {}".format(
                    switch_time.strftime(TIME_FORMAT),
                    self._readable_dt(restart_time),
                )
            )

    def _switch(
        self,
        switch_time: dt.datetime,
        restart_time: dt.datetime,
        category: str,
        message: str,
        dry_run: bool,
    ):
        """
        Switch tasks at the given time points.

        `category` and `message` will be added to the stopped run.
        """

        active_run_start: Optional[dt.datetime] = self.dao.get_start_time()
        if active_run_start is None:
            raise InvalidOperationWarning.cant("switch", "no run is currently active")

        if switch_time > restart_time:
            raise InvalidOperationWarning.cant(
                "switch", "specified stop time needs to lie before the restart time"
            )

        if active_run_start > switch_time:
            raise InvalidOperationWarning.cant(
                "switch", "end / switch time lies before the active run's start time"
            )

        self.ensure_valid_start_time(
            start_time=restart_time, action="switch", time_desc="restart time"
        )

        # Stop at the beginning of the pause, restart at the end of the pause
        self._stop(
            end_time=switch_time,
            category=category,
            message=message,
            dry_run=dry_run,
        )
        self._start(start_time=restart_time, dry_run=dry_run)

    # cancel #

    def cancel(self, args) -> None:
        """ Cancels the current run. """

        if not self.dao.run_active():
            print("No active run")
            return

        if not args.dry_run:
            self.dao.cancel_run()
        print("Run cancelled")

    # resume #

    def resume(self, args) -> None:
        """ Resumes the last run. """

        if not args.force and self.dao.run_active():
            raise InvalidOperationWarning.cant(
                "resume run", "a run is currently active (add --force to override)"
            )

        protocol: ProtocolMeta = self.dao.get_container(dt.date.today())
        records_today: List[Record] = list(protocol.entries)

        if not records_today:
            raise InvalidOperationWarning.cant(
                "resume run", "no records stored for today"
            )

        last_today: Record = records_today[-1]
        if not args.dry_run:
            protocol.remove(record=last_today)
            self.dao.update_info_file()

        print(f"Record {last_today.strftime(TIME_FORMAT)} removed. Resuming...")
        self._start(start_time=last_today.start, force=args.force, dry_run=args.dry_run)

    # status #

    def status(self, args) -> None:
        """ Print the current status. """

        today: dt.date = dt.date.today()
        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        minutes_protocol, minutes_active_run = self._total_minutes_worked_today()

        output: str

        if active_start is None:
            output = "Inactive"
        elif active_start > dt.datetime.now():
            output = (
                Color.color("Scheduled", Color.BLUE)
                + f" to start work at {self._readable_dt(active_start)}"
            )
        else:
            output = Color.color("Active", Color.BLUE) + " since {} ({})".format(
                self._readable_dt(active_start), self._timedelta_str(minutes_active_run)
            )

        if args.oneline:
            print(output)
            return

        total_minutes_worked = minutes_protocol + minutes_active_run
        entries_today: List[Record] = self.dao.get_entries(date=today)
        output += (
            "\n> " + self._timedelta_str(total_minutes_worked) + " worked until now – "
        )
        if minutes_protocol > 0:
            num: int = len(entries_today)
            output += "{} {} on record".format(num, "entry" if num == 1 else "entries")
        else:
            output += "nothing on record"
        if entries_today:
            # We assume the entries are sorted by time in ascending order.
            output += (
                f"\n> Last entry ends at {entries_today[-1].end.strftime('%H:%M')}"
            )

        new_section = lambda s: f"\n\n{s}:"
        new_section_line = lambda: "\n\t"

        # How many hours are we expected to work?
        output += new_section("Workday status")

        # Delta until (including) yesterday – a negative delta represents overtime
        delta_yesterday: float = self._minute_balance_up_to(day=today)
        minutes_expected: float = self._minutes_per_day(day=today)

        minutes_to_work: float = minutes_expected + delta_yesterday

        minutes_left_today: float = minutes_to_work - total_minutes_worked
        minutes_left_delta_str: str = self._timedelta_str(abs(minutes_left_today))

        output += new_section_line()

        if minutes_left_today <= 0:
            done_msg = "Done"
            if minutes_left_today < 0:
                done_msg += " (" + minutes_left_delta_str + " over)"
            output += Color.color(done_msg, Color.GREEN)
        else:
            output += "{} left (until {})".format(
                minutes_left_delta_str,
                (dt.datetime.now() + dt.timedelta(minutes=minutes_left_today)).strftime(
                    TIME_FORMAT
                ),
            )

            output += new_section_line() + "Week balance: "
            if delta_yesterday == 0:
                output += Color.color("On time", Color.GREEN)
            else:
                # _timedelta_str() only allows positive arguments
                time_str: str = self._timedelta_str(abs(delta_yesterday))
                if delta_yesterday > 0:
                    output += Color.color(time_str + " undertime", Color.ORANGE)
                elif delta_yesterday < 0:
                    output += Color.color(time_str + " overtime", Color.GREEN)

        if minutes_expected != 8.0 * 60:
            output += new_section_line()
            output += (
                "Note: Reduced hour day (" + self._timedelta_str(minutes_expected) + ")"
            )

        print(output)

    # hours #

    def hours(self, args):
        """ Print the hours worked until a specified time or related things. """

        today: dt.date = dt.date.today()
        minutes_logged, minutes_active_run = self._total_minutes_worked_today()
        new_section = lambda: "\n> "

        output: str = "{} on record, {} active run".format(
            self._timedelta_str(minutes_logged),
            self._timedelta_str(minutes_active_run),
        )

        ## Optional modes

        start_time: Optional[dt.datetime] = self.dao.get_start_time()

        # prospective_start | If start_time is None, no run is active. Then we assume
        #                     we would start a run now.
        prospective_start: dt.datetime = start_time or dt_parse.resolve_time_argument(
            argument="now",
            baseline_date=dt.date.today(),
            rounding_mode=dt_parse.RoundingMode.DOWN,
        )

        # worked_towork_split | By default, we base on the prospective start time.
        #                       If a run was started in the past, worked_minutes
        #                       includes the minutes up to now, so we have to remove
        #                       those by basing on _dt_now_stripped().
        worked_towork_split: dt.datetime = prospective_start
        if start_time is not None and start_time < dt.datetime.now():
            worked_towork_split = self._dt_now_stripped()

        hours_data: Work.HoursData = Work.HoursData(
            start_time=start_time,
            minutes_logged=minutes_logged,
            minutes_active_run=minutes_active_run,
            prospective_start=prospective_start,
            worked_towork_split=worked_towork_split,
        )

        if args.h_until:
            target: dt.datetime = dt_parse.resolve_time_argument(
                argument=args.h_until,
                baseline_date=today,
                rounding_mode=dt_parse.RoundingMode.UP,
            )

            # Verify input correctness
            if target.date() < today or target < prospective_start:
                raise InvalidOperationWarning(
                    "The target time supplied to --until needs to be after the "
                    f"(prospective) start time {self._readable_dt(prospective_start)}."
                )

            output += new_section()
            output += self._get_hours_worked_until_msg(
                target_time=target, hours_data=hours_data
            )

        # Only continue if args.h_target is set and not 0
        if args.h_target:
            time: dt.time = dt_parse.parse_time_str(str(args.h_target))

            output += new_section()
            output += self._get_target_end_time_msg(
                target_hours=time.hour,
                target_minutes=time.minute,
                hours_data=hours_data,
            )

        # Calculate the remaining hours for a full workday (respecting the week balance)
        if args.h_workday:
            output += new_section()
            output += self._get_workday_end_time_msg(hours_data=hours_data)

        if args.h_balance:
            output += new_section()
            output += self._get_day_balance_msg(hours_data=hours_data)

        print(output)

    @dataclass
    class HoursData:
        """ Storage container for data used in hours sub-functions. """

        start_time: Optional[dt.datetime]
        minutes_logged: float
        minutes_active_run: float
        prospective_start: dt.datetime
        worked_towork_split: dt.datetime

        @property
        def total_minutes_worked(self) -> float:
            return self.minutes_logged + self.minutes_active_run

    def _get_hours_worked_until_msg(self, target_time, hours_data):
        # type: (dt.datetime, Work.HoursData) -> str
        """ Compute and stringify the worked hours at a given target time. """

        minutes_from_now: float = (
            target_time - hours_data.worked_towork_split
        ) / dt.timedelta(minutes=1)
        total_minutes: float = hours_data.total_minutes_worked + minutes_from_now

        target_strf: str = target_time.strftime(TIME_FORMAT)
        minutes_strf: str = self._timedelta_str(minutes=total_minutes)

        if hours_data.start_time is None:
            return (
                f"You will have worked {minutes_strf} at target time {target_strf} if "
                f"you start now ({hours_data.prospective_start.strftime('%H:%M')})"
            )

        return f"You will have worked {minutes_strf} at target time {target_strf}."

    def _get_target_end_time_msg(self, target_hours, target_minutes, hours_data):
        # type: (float, float, Work.HoursData) -> str
        """ Compute and stringify the status towards a given time target. """

        target_time: str = f"{target_hours}:{target_minutes:0>2}"
        target_minutes += target_hours * 60.0

        # Remove ".0" for full hours
        if int(target_hours) == target_hours:
            target_hours = int(target_hours)

        return self._get_end_time_msg(
            target_minutes=target_minutes,
            hours_data=hours_data,
            target_explainer=f"for a {target_time} hour day",
            completed_msg=f"Target of {target_time} hours {Color.color('achieved', Color.GREEN)}!",
        )

    def _get_workday_end_time_msg(self, hours_data):
        # type: (Work.HoursData) -> str
        """ Compute and stringify the end time for a full workday, respecting the current week balance. """

        minutes_today: float = self._minutes_per_day(day=dt.date.today())
        minute_balance_up_to_today: float = self._minute_balance_up_to(
            day=dt.date.today()
        )
        target_minutes: float = minutes_today + minute_balance_up_to_today

        completed_msg: str = f"Workday {Color.color('finished', Color.GREEN)}!"

        target_explainer: str
        timedelta_str: str = self._timedelta_str(abs(minute_balance_up_to_today))
        if minute_balance_up_to_today < 0:
            target_explainer = "to clear your overtime of " + timedelta_str
        elif minute_balance_up_to_today > 0:
            target_explainer = "to recover from your undertime of " + timedelta_str
        else:
            target_explainer = "for a full workday"

        return self._get_end_time_msg(
            target_minutes=target_minutes,
            hours_data=hours_data,
            target_explainer=target_explainer,
            completed_msg=completed_msg,
        )

    def _get_end_time_msg(
        self, target_minutes, hours_data, target_explainer, completed_msg
    ):
        # type: (float, Work.HoursData, str, str) -> str
        """
        Compute the end time for a day of the specified hours.
        Returns: None if target is achieved.
        """

        # If the expected hours were already reached before this run, we can immediately return.
        if hours_data.minutes_logged >= target_minutes:
            return completed_msg

        delta_minutes: float = target_minutes - hours_data.total_minutes_worked

        # If a run was started in the past, worked_minutes includes the minutes up to now,
        # so we have to calculate the end from _dt_now_stripped().
        prospective_end: dt.datetime = hours_data.worked_towork_split
        prospective_end += dt.timedelta(minutes=delta_minutes)

        # The end time might lie on the next day. We don't support multi-day runs, so we catch this here.
        if prospective_end.date() != dt.date.today():
            return "Given target hours can't be completed anymore today!"

        # End time has already been reached
        if prospective_end <= self._dt_now_stripped():
            return completed_msg

        # End time not yet reached

        message: str
        if not self.dao.run_active():
            message = f"Start now ({hours_data.prospective_start.strftime('%H:%M')}) and work "
        else:
            message = "Work "
        message += f"until {prospective_end.strftime(TIME_FORMAT)} "

        # Explainer, such as "for a 7 hour day"
        message += target_explainer.strip()
        message += "."

        return message

    def _get_day_balance_msg(self, hours_data):
        # type: (Work.HoursData) -> str
        """Compute and stringify the week balance including the current workday,
        taking into account all worked hours."""

        minutes_to_work: float = self._minutes_per_day(
            day=dt.date.today()
        ) + self._minute_balance_up_to(day=dt.date.today())
        remaining_minutes: float = minutes_to_work - hours_data.total_minutes_worked

        message = "Current balance: "
        timedelta_str: str = self._timedelta_str(abs(remaining_minutes))

        if remaining_minutes < 0:
            message += timedelta_str + " overtime"
        elif remaining_minutes > 0:
            message += timedelta_str + " remaining"
        else:
            message += "+/- 0"

        message += f" ({self._timedelta_str(minutes_to_work)} total)"

        return message

    # list #

    def list_entries(self, args) -> None:
        """ List protocol entries. """
        selected_days: List[dt.date] = self.get_selected_days(args)
        self._list(
            days=selected_days,
            list_empty=args.list_empty,
            include_active=args.include_active,
            print_breaks=args.with_breaks,
            only_time=args.only_time,
        )

    def _list(
        self,
        days: List[dt.date],
        list_empty: bool,
        include_active: bool,
        print_breaks: bool,
        only_time: bool,
    ) -> None:
        """ Print the given list of dates. For more than one date: Print a summary. """

        if not days:
            raise ValueError("At least one element is required")

        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        # This variable stores two properties: include_active and the date to include
        include_active_date: Optional[dt.date] = None
        if active_start is not None and include_active:
            if active_start.date() not in days:
                raise InvalidOperationWarning.cant(
                    "list the active run",
                    because="the selected period doesn't cover it",
                )
            include_active_date = active_start.date()

        output: List[str] = []
        total_includes_active_run: bool = False

        total_number_of_records: int = 0
        total_minutes_worked: float = 0.0
        for day in days:
            records: List[Record] = self.dao.get_entries(date=day)

            active_start_to_include: Optional[dt.datetime] = None
            # If it is None or not the current day, do not include the active run.
            if include_active_date == day:
                active_start_to_include = active_start

            if len(records) == 0 and not list_empty and active_start_to_include is None:
                continue

            output_lines = self._evaluate_day(
                day=day,
                records=records,
                print_breaks=print_breaks,
                only_time=only_time,
                active_start_to_include=active_start_to_include,
            )
            total_number_of_records += len(records)
            output.extend(output_lines)
            output.append("")
            total_minutes_worked += self._minutes_logged_on(day)

            # If we want to include the active run and it is today, add those minutes.
            if active_start_to_include is not None:
                total_minutes_worked += self._minutes_active_run()
                total_includes_active_run = True

        # Add info if no result (when omitting empty records)
        if not output:
            none_found_msg: str = "No records found"
            # Single day
            if len(days) == 1:
                none_found_msg += " on " + days[0].strftime(DATE_FORMAT_FULL)
            # Continuous period (each two consecutive list elements are directly adjacent days)
            elif all(
                [
                    days[i - 1] == days[i] - dt.timedelta(days=1)
                    for i in range(1, len(days))
                ]
            ):
                none_found_msg += " for the period from {} to {}".format(
                    days[0].strftime(DATE_FORMAT), days[-1].strftime(DATE_FORMAT)
                )
            else:
                none_found_msg += " for the selected days:\n{}".format(
                    ", ".join([d.strftime(DATE_FORMAT) for d in days])
                )

            output.append(none_found_msg)
        # Add summary if more than one element
        elif len(days) > 1:
            output.append(
                Color.bold(
                    "Total: {} records{}, {} worked".format(
                        total_number_of_records,
                        " (+ active run)" if total_includes_active_run else "",
                        self._timedelta_str(total_minutes_worked),
                    )
                )
            )
        else:
            output = output[:-1]

        for line in output:
            print(line)

    def _evaluate_day(
        self,
        day: dt.date,
        records: List[Record],
        print_breaks: bool,
        only_time: bool,
        active_start_to_include: Optional[dt.datetime] = None,
    ) -> List[str]:
        """
        Produce a list of output strings describing the records stored on the given day.
        Return the output list as well as the number of records.

        :param print_breaks: If true, intertwine the break times with the listed entries.
        :param only_time: If true, omit optional record fields from output.
        :param active_start_to_include: If given, the "active run" will be added to the output.
        """

        if (
            active_start_to_include is not None
            and active_start_to_include.date() != day
        ):
            raise ValueError("Invalid day for active_start_to_include passed.")

        # Add the year to the printout if it's not the current year
        date_fmt: str = "%d.%m." if day.year == dt.date.today().year else "%d.%m.%Y"

        # Merge entries for only_time
        record_count: int = len(records)
        if only_time:
            for i in range(len(records)):
                records[i] = Record(start=records[i].start, end=records[i].end)
            records = sort_and_merge(entries=records, output=False)

        result: List[str] = []
        result.append(
            "{: <3}, {}: {} records{}{}".format(
                day.strftime("%a"),
                day.strftime(date_fmt),
                record_count,
                f" (merged to {len(records)})"
                if only_time and len(records) != record_count
                else "",
                " (+ active run)" if active_start_to_include is not None else "",
            )
        )

        active_run_to_include: Optional[Record] = None
        if active_start_to_include is not None:
            # For a future run, we have to select an end time, so we just choose the start time (= 0m).
            active_run_to_include = Record(
                start=active_start_to_include,
                end=max(active_start_to_include, self._dt_now_stripped()),
            )
            records.append(active_run_to_include)

        total_minutes: float = 0.0
        total_break_minutes: float = 0.0
        prin_table: PrinTable = PrinTable()

        for i, record in enumerate(records):
            minutes: float = record.get_minutes()
            total_minutes += minutes
            row: List[str] = [
                f"{record.strftime(TIME_FORMAT)}",
                f" | {self._timedelta_str(minutes)}",
            ]

            # Add optional attributes
            if not only_time:
                category: str = f"  ({record.category})" if record.category else " "
                message: str = f' "{record.message}"' if record.message else " "
                row.extend([category, message])

            prin_table.add_row(row)

            # Add break info after all but the last entry
            if print_breaks:
                break_str, break_length = self._break_str(records, i)
                total_break_minutes += break_length
                if break_length > 0:
                    prin_table.add_row(["", Color.color(break_str, Color.GRAY)])

        # TODO Just add row to table, as color handling should be fixed now
        if active_start_to_include is not None:
            # Note: If we were to just add a row to the table, the first column would
            # be too wide (the color codes are not handled correctly by PrinTable).
            # If we fix the color code handling, we can change this.
            active_run_row: str = f"{active_start_to_include.strftime(TIME_FORMAT)} ~"
            prin_table.rows[-1][0] = "{}{}".format(
                Color.color(active_run_row, Color.BLUE),
                " " * (13 - len(active_run_row)),
            )

        for row in prin_table.printable():
            result.append("".join(row).rstrip())

        if len(records) > 0:
            result[0] = Color.bold(result[0])
            result.append(" " * 13 + f" = {self._timedelta_str(minutes=total_minutes)}")
            if print_breaks:
                result[-1] = result[-1] + Color.color(
                    f" (+ {self._timedelta_str(total_break_minutes)} of breaks)",
                    Color.GRAY,
                )

        return result

    def _break_str(self, records: List[Record], i: int) -> Tuple[str, float]:
        """ Create a break string for the given row. Skips last row. """
        if i == len(records) - 1:
            return "", 0

        break_to_next = Record(start=records[i].end, end=records[i + 1].start)
        break_length: float = break_to_next.get_minutes()

        if break_length == 0:
            return "", 0
        return f" ~ {self._timedelta_str(break_length)} break", break_length

    # day #

    def day(self, args) -> None:
        """ List the current day, including the active run. """
        self._list(
            [dt.date.today()],
            list_empty=True,
            include_active=True,
            print_breaks=True,
            only_time=False,
        )

    # export #

    def export(self, args) -> None:
        """ Export any day or range of days as CSV. """
        selected_days: List[dt.date] = self.get_selected_days(args)
        writer = csv.writer(sys.stdout, lineterminator=os.linesep)

        assert consts.PROTOCOL_VERSION == 3
        writer.writerow(["start", "end", "category", "message"])

        date: dt.date
        for date in selected_days:
            record: Record
            for record in self.dao.get_entries(date=date):
                writer.writerow(record.to_protocol_row())

    # edit + remove #

    def edit(self, args) -> None:
        """ Edit protocol entries. Currently supports changing the time. """

        selection = self._start_manipulation_mode(args, "edit")
        if not selection:
            return

        protocol: ProtocolMeta
        selected_records: List[Record]
        protocol, selected_records = selection

        edited: int = 0
        modification_buffer: List[Tuple[Record, Record]] = []

        for record in selected_records:
            print(f"\n > Selected record: {record.strf(TIME_FORMAT)}\n")

            new_start: dt.datetime = self._new_time_or_not(
                time_name="start", old_val=record.start
            )
            new_end: dt.datetime = self._new_time_or_not(
                time_name="end", old_val=record.end
            )
            new_category: str = self._new_text_field_or_not(
                field_name="category", old_val=record.category
            )
            new_message: str = self._new_text_field_or_not(
                field_name="message", old_val=record.message
            )
            new_record: Record = Record(
                start=new_start, end=new_end, category=new_category, message=new_message
            )

            if new_record == record:
                print("Unchanged")
                continue

            user_choice = input(
                "Change\n\t{}\nto\n\t{}\n? [Y/n]\n".format(
                    record.strf(TIME_FORMAT), new_record.strf(TIME_FORMAT)
                )
            )
            # By using in, we ensure that no input is also True. "" in "y" == True
            if user_choice.lower() in "y":
                modification_buffer.append((record, new_record))
                edited += 1
                print("Done")
            else:
                print("Skipped")

        # This still does not consider the case of a merge affecting an entry still to come
        for record, new_record in modification_buffer:
            protocol.replace(record=record, new_record=new_record)

        self._end_manipulation_mode(num_edited=edited, verb="edited")

    def _new_time_or_not(self, time_name: str, old_val: dt.datetime) -> dt.datetime:
        """ User interaction: Ask for a new time (or no change). """

        user_choice = input(f"New {time_name} time? ({old_val.strftime(TIME_FORMAT)}) ")
        if user_choice == "":
            return old_val

        try:
            return dt_parse.resolve_time_argument(
                argument=user_choice,
                baseline_date=old_val.date(),
                rounding_mode=dt_parse.RoundingMode.NONE,
            )
        except ValueError as e:
            print(f"{Color.color('Parse error', Color.RED)}: {str(e)}")
            return self._new_time_or_not(time_name, old_val)

    def _new_text_field_or_not(self, field_name: str, old_val: str) -> str:
        """ User interaction: Ask for a new text field, field removal, or no change. """

        user_choice: str = input(
            f'New {field_name} or remove ["-"]? ({old_val}) '
        ).strip()

        if user_choice == "":
            return old_val
        elif user_choice == "-":
            return ""

        return user_choice

    def remove(self, args) -> None:
        """ Remove protocol entries. """

        selection = self._start_manipulation_mode(args, "remove")
        if not selection:
            return

        protocol: ProtocolMeta
        selected_records: List[Record]
        protocol, selected_records = selection

        for record in selected_records:
            protocol.remove(record)

        self._end_manipulation_mode(num_edited=len(selected_records), verb="removed")

    def _start_manipulation_mode(
        self, args, verb: str
    ) -> Optional[Tuple[ProtocolMeta, List[Record]]]:
        """ Common functionality for both manipulation modes. """

        date: dt.date = self.get_date(args)
        protocol: ProtocolMeta = self.dao.get_container(date=date)
        records: List[Record] = list(protocol.entries)
        date_readable: str = self._readable_d(date)

        if not records:
            print("No entries on selected date: " + date_readable)
            return None

        print(verb.capitalize() + " mode – " + date_readable)

        all_indices: List[int] = list(range(len(records)))
        zipped_records: Dict[int, Record] = {
            i: r for (i, r) in zip(all_indices, records)
        }

        print()
        for i, record in zipped_records.items():
            print(f"[{i}] {record.strf(TIME_FORMAT)}")
        print()

        user_choice: str = ""
        while user_choice not in ["all"] + [str(i) for i in all_indices]:
            user_choice = input(
                f'Which element? Enter an index [{0}..{len(records) - 1}] or "all": '
            )

        selected_indices: List[int] = []
        if user_choice == "all":
            selected_indices = all_indices
        else:
            selected_indices = [int(user_choice)]

        return protocol, [zipped_records[i] for i in selected_indices]

    def _end_manipulation_mode(self, num_edited: int, verb: str) -> None:
        """ Print result message, update checksum. """

        print(
            verb.capitalize() + f" {num_edited} record{'s' if num_edited != 1 else ''}"
        )

        # Only update the checksum if we actually changed something (double-check)
        if num_edited > 0:
            self.dao.update_info_file()

    # recess #

    def recess(self, args) -> None:
        """ Manage recess days, a.k.a. vacation days or holidays (add, remove, list). """

        action: Optional[Callable] = None
        output: str = ""

        if args.add_vacation:
            if len(args.add_vacation) not in [1, 2]:
                raise ValueError("Expects either one or two arguments!")
            action, output = self._recess_add_vacation(args.add_vacation)
        elif args.add_holiday:
            holi_day: dt.date = dt_parse.resolve_date_argument(args.add_holiday)
            action = lambda: self.recess_dao.add_holiday(date=holi_day)
            output = f"Added holiday on {holi_day.strftime(DATE_FORMAT)}"
        elif args.add_reduced_day:
            assert len(args.add_reduced_day) == 2
            redu_day: dt.date = dt_parse.resolve_date_argument(args.add_reduced_day[0])
            try:
                hours: float = float(args.add_reduced_day[1])
            except ValueError:
                raise ValueError(
                    f"Invalid value {args.add_reduced_day[1]} for HOURS; expects float."
                )
            action = lambda: self.recess_dao.add_reduced_hour_day(
                date=redu_day, hours=hours
            )
            output = (
                f"Added reduced hour day on {redu_day.strftime(DATE_FORMAT)} "
                f"with {hours} hours"
            )
        elif args.remove:
            remove_dates: List[dt.date] = [
                dt_parse.resolve_date_argument(r) for r in args.remove
            ]
            action = lambda: self.recess_dao.remove(dates=remove_dates)
            output = (
                f"Removed {', '.join([r.strftime(DATE_FORMAT) for r in remove_dates])}"
            )

        if action is None:
            # Default: List (even if no mode was selected)
            list_year = args.list or dt.date.today().year
            self._list_recess_days(year=list_year)
            return

        if not args.dry_run:
            action()
        print(output)

    def _recess_add_vacation(self, vacation_period: List[str]) -> Tuple[Callable, str]:
        """ Add a vacation for the given period. May be either one or two arguments. """
        first: dt.date
        last: dt.date
        action: Callable

        length: int = len(vacation_period)
        if length == 1:
            vacation_period.append(vacation_period[0])
        first, last = [dt_parse.resolve_date_argument(d) for d in vacation_period]
        if first > last:
            raise InvalidOperationWarning.cant(
                "add vacation", because="begin date lies after end date"
            )
        action = lambda: self.recess_dao.add_vacation(first_day=first, last_day=last)
        if length == 1:
            assert first == last
            return action, f"Added vacation on {first.strftime(DATE_FORMAT)}"

        return action, (
            f"Added vacation from {first.strftime(DATE_FORMAT)} "
            f"to {last.strftime(DATE_FORMAT)}"
        )

    def _list_recess_days(self, year: int) -> None:
        """ List recess days of the given year. """
        if not self.recess_dao.has_days(year=year):
            print(f"No recess days stored for {year}.")
            return
        if holidays := self.recess_dao.get_holidays(year=year):
            print("Holidays:")
            for h in holidays:
                print(f"  {h.date.strftime(DATE_FORMAT)}")
        if reduced_hour_days := self.recess_dao.get_reduced_hour_days(year=year):
            print("Reduced hour days:")
            for r in reduced_hour_days:
                print(f"  {r.date.strftime(DATE_FORMAT)} ({r.hours} hours)")
        if vacations := self.recess_dao.get_vacations(year=year):
            print("Vacation:")
            for v in vacations:
                print(f"  {v.date.strftime(DATE_FORMAT)}")

    # rehash #

    def rehash(self, args) -> None:
        """ Recompute the info file checksum (after reconfirming). """

        user_says: str = input(
            "Do you really want to update the verification checksum?\n"
            + "This will validate all possibly erroneous manual edits!\n"
            + "[y/N] "
        )
        if user_says.lower() == "y":
            self.dao.update_info_file()
            print("Checksum updated")
        else:
            print("Cancelled")

    # config #

    def config(self, args) -> None:
        """
        Check and interact with the configuration (RC and hardcoded).
        Formerly `rc()` and `see()`.
        """

        if args.create:
            try:
                RC.create_rc_file()
                return
            except FileExistsError:
                raise InvalidOperationWarning.cant(
                    "create RC file", "file already exists"
                )
        elif args.expected:
            print(RC.example_rc_file())
            return
        elif args.see:
            self._see(s_target=args.see)
            return

        # Default: Print configuration path
        print(f"Runtime configuration file path: {RC.path()}")

    def _see(self, s_target) -> None:
        """ See configuration details. """

        if s_target == "dir":
            print(f"Records directory: {self.dao.records_directory}")
        elif s_target == "expected hours":
            if self.configuration.expected_hours is None:
                print("No expected hours configured.")
            else:
                for wd, eh in self.configuration.expected_hours.items():
                    print(f"{wd:<10}: {eh}")
        # When adding a new option, make sure to update the "choices" of the ArgumentParser!
        else:
            raise NotImplementedError(f"Target {s_target} unknown")

    ### Shared functionality ###

    def _readable_dt(self, date_and_time: dt.datetime) -> str:
        """ Convert the given datetime.datetime to a human readable string with the time and day. """

        result: str = date_and_time.strftime(TIME_FORMAT)
        result += " " + self._readable_d(date_and_time.date())

        return result

    def _readable_d(self, date: dt.date) -> str:
        """ Convert the given datetime.date to a human readable string with the day. """

        if date == dt.date.today():
            return "today"
        elif date == (dt.date.today() + dt.timedelta(days=1)):
            return "tomorrow"
        elif date == (dt.date.today() - dt.timedelta(days=1)):
            return "yesterday"
        else:
            return "on " + date.strftime(DATE_FORMAT_FULL)

    def _minutes_logged_on(self, requested_date: dt.date) -> float:
        """ Return the minutes logged on the requested date. """
        the_days_records: List[Record] = self.dao.get_entries(date=requested_date)
        return self._minutes_worked(the_days_records)

    def _minutes_worked(self, records: List[Record]) -> float:
        """ Return the summed up work times contained in the given records. """
        return sum([r.get_minutes() for r in records])

    def _minutes_active_run(self) -> float:
        """ Return the minutes the current run has been active. Raises if no run is active. """

        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        if active_start is None:
            raise RuntimeError("No active run – can't calculate minutes!")

        minutes_active_run: float = util.minutes_difference(
            start=active_start, end=self._dt_now_stripped()
        )
        # Fixes bug for future start in which case a negative number is returned.
        return max(minutes_active_run, 0)

    def _total_minutes_worked_today(self) -> Tuple[float, float]:
        """
        Return the total minutes worked until now.
        Includes all of today's protocol entries, as well as the current run (if active).
        """

        minutes_protocol = self._minutes_logged_on(requested_date=dt.date.today())
        minutes_active_run: float = 0.0

        if self.dao.run_active():
            minutes_active_run = self._minutes_active_run()

        return minutes_protocol, minutes_active_run

    def _total_pauses_today(self) -> float:
        """
        Return the pauses today, in minutes.
        Sums up all gaps between protocol entries, also taking into account the active run.
        """

        records: List[Record] = self.dao.get_entries(date=dt.date.today())

        # If a run is active, it is added as a theoretical entry
        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        if active_start is not None:
            records.append(
                Record(start=active_start, end=active_start + dt.timedelta(minutes=1))
            )

        return self._total_pauses(records=records)

    def _total_pauses(self, records: List[Record]) -> float:
        """ Return the sum of all gaps between protocol entries. """

        if len(records) <= 1:
            return 0.0

        pauses: float = 0.0
        last_end: dt.datetime = records[0].end
        for r in records[1:]:
            pauses += util.minutes_difference(start=last_end, end=r.start)
            last_end = r.end

        return pauses

    def _timedelta_str(self, minutes: float) -> str:
        """
        Return a string representing the minutes (e.g. 150.0) as HH:MM (e.g. 2 h 30 m).
         minutes : Positive-valued number of minutes to translate.
        """

        if minutes < 0:
            raise ValueError(
                "Timedelta can only be computed for positive minute values."
            )

        only_hours: int = int(minutes // 60)
        only_minutes: int = int(minutes % 60)
        # Handle the corner case of both rounding down to zero; happens for inputs 0, m < 1
        if only_hours + only_minutes == 0:
            return "0 m"

        hour_part: str = "" if only_hours == 0 else f"{only_hours} h"
        minute_part: str = "" if only_minutes == 0 else f"{only_minutes} m"

        return f"{hour_part} {minute_part}".strip()

    def _timedelta_str_signed(self, minutes: float) -> str:
        """ Return a timedelta string with sign. Allows negative values. """

        result = ""
        if minutes > 0:
            result = "+ "
        elif minutes < 0:
            result = "- "
        result += self._timedelta_str(abs(minutes))
        return result

    def _minutes_per_days(self, days: List[dt.date]) -> List[Tuple[dt.date, float]]:
        """ Return a list of the minutes to work on each day. """

        # This method is the single place where expected hours are calculated.
        # That means that we only need to consider vacations or holidays here.

        result: List[Tuple[dt.date, float]] = []
        normal_hours: List[float] = (
            list(self.configuration.expected_hours.values())
            if self.configuration.expected_hours
            else [8.0] * 5 + [0.0] * 2
        )
        assert len(normal_hours) == 7

        for day in days:
            # We don't need the list index of the day, but its relative "index" in its week.
            hours = normal_hours[day.weekday()]
            # If a day is added twice, this always returns the lowest hour value.
            if (reduced_hours := self.recess_dao.reduced_hours(day)) is not None:
                hours = reduced_hours
            result.append((day, hours * 60.0))

        return result

    def _minutes_per_day(self, day: dt.date) -> float:
        """ Return the minutes to work on the given day. """

        mins_per_days = self._minutes_per_days(days=[day])[0]
        _, minutes = mins_per_days
        return minutes

    def _minute_balance(self, week: List[dt.date]) -> float:
        """
        Return the minute balance for the given days.
        Negative delta = Overtime
         week : The list may be shorter than seven elements; then only the first len(week) days will be assumed.
        """

        if len(week) > 7:
            raise ValueError("A week has no more than seven days.")

        deltas: List[float] = []

        for day, minutes_expected in self._minutes_per_days(days=week):
            minutes_logged: float = self._minutes_logged_on(requested_date=day)
            deltas.append(minutes_expected - minutes_logged)

        return sum(deltas)

    def _minute_balance_up_to(self, day: dt.date) -> float:
        """
        Return the minute balance for all days in the given day's week, excluding itself.
        Correctly handles Monday and Sunday.
         see: `_minute_balance()`
        """

        week_no: int
        _, week_no, _ = day.isocalendar()
        week: List[dt.date] = self._containing_week(week_no=week_no)
        week_up_to: List[dt.date] = week[: week.index(day)]

        return self._minute_balance(week=week_up_to)

    ### Convenience functions ###

    def _dt_now_stripped(self) -> dt.datetime:
        """ Return the current time, with seconds and microseconds set to 0. """
        return dt.datetime.now().replace(second=0, microsecond=0)

    def _containing_week(self, week_no: int) -> List[dt.date]:
        """
        Return the week specified by the given week number.

        week: Either a valid week number, or -1 for the current week.
        """

        current_year, current_week, _ = dt.date.today().isocalendar()

        # If -1 is given as a week number, the current week is requested.
        if week_no == -1:
            week_no = current_week

        # The weekday is a 0-6 number for Mon-Sun
        monday: dt.date = dt.date.fromisocalendar(
            year=current_year, week=week_no, day=1
        )
        sunday: dt.date = monday + dt.timedelta(days=6)
        week: List[dt.date] = util.get_period(period_start=monday, period_end=sunday)

        return week

    def _containing_month(self, day: dt.date) -> List[dt.date]:
        """ Return the month that contains the given day. """

        first: dt.date = day.replace(day=1)
        # Get a day from the following month
        date_next_month: dt.date = first + dt.timedelta(days=32)
        # 7th - 7 = last of month before
        last = date_next_month - dt.timedelta(days=date_next_month.day)

        return util.get_period(period_start=first, period_end=last)


### Other classes ###


class InvalidOperationWarning(Warning):
    pass

    @staticmethod
    def cant(do: str, because: str):
        return InvalidOperationWarning(f"Can't {do} – {because}!")


### Main program trigger ###


def main():
    try:
        Work().main()
    except KeyboardInterrupt:
        print("Cancelled")
        sys.exit(130)


if __name__ == "__main__":
    main()
