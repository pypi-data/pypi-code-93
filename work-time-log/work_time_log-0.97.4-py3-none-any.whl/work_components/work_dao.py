#!/usr/bin/env python3

""" The DAO for the work module. """

import datetime as dt
import pathlib
import re
from typing import List, Optional, Tuple
import zlib

from work_components.consts import (
    DATETIME_FORMAT,
    INFO_FILE_NAME,
    INFO_FILE_CONTENT,
    INFO_FILE_PATTERN,
    PROTOCOL_DIRECTORY_NAME,
    PROTOCOL_VERSION,
    RUN_FILE_NAME,
)
from work_components.container import (
    Protocol,
    ProtocolRange,
    ProtocolDay,
    ProtocolMeta,
    Record,
)


class WorkDao(object):

    # work_directory        self.work_directory
    # |- info.winf          self.info_file
    # |- running.wtime      self.run_file
    # |- records/           self.records_directory
    #    |- 2019/ ...       –
    #    |- ...             –
    # |- vacations/         –
    #    |- 2021.wvac       –
    #    |- ...             –
    #
    # (see work_components/consts.py)
    def __init__(self, work_directory: str):
        self.work_directory: pathlib.Path = pathlib.Path(work_directory)
        self.info_file: pathlib.Path = self.work_directory.joinpath(INFO_FILE_NAME)
        self.run_file: pathlib.Path = self.work_directory.joinpath(RUN_FILE_NAME)
        self.records_directory: pathlib.Path = self.work_directory.joinpath(
            PROTOCOL_DIRECTORY_NAME
        )

        # We assume existence of the root directory in many operations.
        self._ensure_work_dir_exists()

    ### Interface ###

    def start_run(self, start_time: dt.datetime, force: bool = False) -> None:
        """ Start a run at the given time. Raises on invalid operation. """

        if not force and self.run_file.exists():
            raise IOError(
                f'File "{self.run_file.resolve()}" exists already! Could not create.'
            )

        with self.run_file.open(mode="w") as time_file:
            time_file.write(start_time.strftime(DATETIME_FORMAT))

    def stop_run(self, end_time: dt.datetime, category: str, message: str) -> None:
        """ Stop a run at the given time. Raises on invalid operation. """

        start_time = self.get_start_time()
        if start_time is None:
            raise RuntimeError("Tried to stop, but no run is active!")

        self.add_protocol_entry(start_time, end_time, category, message)
        self.run_file.unlink()

    def add_protocol_entry(
        self,
        start_time: dt.datetime,
        end_time: dt.datetime,
        category: str,
        message: str,
        force: bool = False,
    ) -> None:
        """
        Add the given elements to the end of the protocol file.
        Checks validity of the info file and updates it after write.
        """

        if not start_time < end_time:
            raise ValueError("End time is not after start time!")

        if start_time.date() != end_time.date():
            raise ValueError("Start and end lie on different dates!")

        if not force and self.has_entry(start_time=start_time, end_time=end_time):
            raise RuntimeError("Given time(s) overlap with existing protocol entry")

        # Both start and end lie on the same day, so we can just use one date
        their_date: dt.date = start_time.date()

        protocol_day: ProtocolDay = self._load_protocol_date(their_date)

        protocol_day.add(
            Record(
                start=start_time,
                end=end_time,
                category=category,
                message=message,
            ),
            force=force,
        )

        # Update the edit time and checksum
        self.update_info_file()

    def cancel_run(self) -> None:
        """ Cancel any currently active run. """
        self.run_file.unlink()

    def run_active(self) -> bool:
        """ Convenience function to check if a run is active. """
        return self.get_start_time() != None

    def get_start_time(self) -> Optional[dt.datetime]:
        """
        Try to retrieve the start time from the run file.

        Returns: None if no run is active.
        """

        if not self.run_file.exists():
            return None

        content = None
        with self.run_file.open(mode="r") as run_file:
            content = run_file.read()

        try:
            return dt.datetime.strptime(content, DATETIME_FORMAT)
        except ValueError:
            raise IOError(
                f"Invalid run file! Please delete or fix. (Path: {self.run_file.resolve()})"
            )

    def has_entry(self, start_time: dt.datetime, end_time: dt.datetime = None) -> bool:
        """ Check whether an existing entry overlaps the given time. """

        # Minimum run length: 15 minutes
        end_time = end_time or start_time + dt.timedelta(minutes=15)

        start_date: dt.date = start_time.date()
        end_date: dt.date = end_time.date()

        if start_date > end_date:
            raise ValueError("Start date lies after end date!")

        current_date: dt.date = start_date
        protocol_days: List[ProtocolDay] = []
        # Add all days covered by start and end time.
        while current_date <= end_date:
            protocol_days.append(self._load_protocol_date(current_date))
            current_date += dt.timedelta(days=1)

        # There may not be any entry on any day overlapping any part of the given slot
        for protocol_day in protocol_days:
            for record in protocol_day.entries:
                # "Touching" of entries (so start_time == existing_end or end_time == existing_start) is allowed
                if start_time < record.end and end_time > record.start:
                    return True

        return False

    def get_entries(
        self,
        date: Optional[dt.date] = None,
        range: Optional[Tuple[dt.date, dt.date]] = None,
    ) -> List[Record]:
        """
        Load stored entries (excluding a possible active run).
        Entries are sorted and overlap-free.

        You may optionally define either one of the optional parameters (but not both):

        : date :  Load a date.

        : range : Load a range.
        """

        entries_container: Optional[ProtocolMeta] = None

        # Nothing specified: Load all
        if date is None and range is None:
            entries_container = self._load_protocol()
        # Date specified
        elif date is not None:
            entries_container = self._load_protocol_date(date=date)
        # Range specified
        elif range is not None:
            entries_container = self._load_protocol_range(*range)
        # Both specified: Invalid arguments
        else:
            raise ValueError("May either specifiy a date or a range, not both.")

        return list(entries_container.entries)

    def get_container(self, date: dt.date) -> ProtocolMeta:
        """ Load a ProtocolMeta interface to the entries. """
        return self._load_protocol_date(date)

    def protocol_empty(self) -> bool:
        """ Fast check if the protocol is empty. """
        if not self.records_directory.exists():
            return True
        protocol: Protocol = self._load_protocol()
        return protocol.empty

    def ensure_protocol_integrity(self) -> None:
        """
        Check all preconditions for valid file operations.
        - Ensure a valid directory exists, otherwise create it.
        - Check if a protocol exists and the corresponding info file matches it.
        Raises if invalid directory structure or files are found.
        """

        protocol: Protocol = self._load_protocol()
        protocols_exist: bool = not protocol.empty
        protocol_info_exists: bool = self.info_file.exists()

        # If no protocols and no info file exist, they can be created safely.
        if not protocols_exist and not protocol_info_exists:
            return

        # If just one exists, something has gone wrong.
        if protocols_exist ^ protocol_info_exists:
            raise IOError(
                "A required file is missing! (Either the protocol or the protocol info file does not exist.)"
            )

        ifile_protocol_version: int
        ifile_protocol_checksum: int
        ifile_protocol_version, _, ifile_protocol_checksum = self._parse_info_file()

        # Version as expected?
        if ifile_protocol_version != PROTOCOL_VERSION:
            raise IOError(
                "Unexpected protocol version {}, expected {}".format(
                    ifile_protocol_version, PROTOCOL_VERSION
                )
            )
        # Checksum matches?
        protocol_checksum: int = self._get_protocol_checksum()
        if ifile_protocol_checksum != protocol_checksum:
            raise IOError(
                "The info file contains a checksum that does not correspond to the actual protocol file."
            )

    def _parse_info_file(self) -> Tuple[int, dt.datetime, int]:
        """ Parse and return info file fields. """

        with self.info_file.open(mode="r") as info_file:
            info_file_content: str = info_file.read()
            info_file_split: List[str] = info_file_content.split("/")
            info_file_match = re.fullmatch(INFO_FILE_PATTERN, info_file_content)

        # <MIGRATE-info-file> functionality. To be removed in v0.95!
        if re.fullmatch(
            r"work-time-protocol/protocol-v(\d{1,2})/last-edit:(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})/hash:([^\n]+)\n",
            info_file_content,
        ):
            raise IOError(
                "Old info file version detected. "
                "Please run `work rehash` once to update, then try again."
            )

        if not len(info_file_split) == 4 or not info_file_match:
            raise IOError(f"Invalid info file at {self.info_file.resolve()}")

        parsed_version: int = int(info_file_match.group(1))
        parsed_edit_date: dt.datetime = dt.datetime.strptime(
            info_file_match.group(2), DATETIME_FORMAT
        )
        parsed_checksum: int = int(info_file_match.group(3))

        return parsed_version, parsed_edit_date, parsed_checksum

    def update_info_file(self) -> None:
        """ Update the info file with the current time and a new protocol checksum. """

        content = INFO_FILE_CONTENT.format(
            PROTOCOL_VERSION,
            dt.datetime.now().strftime(DATETIME_FORMAT),
            self._get_protocol_checksum(),
        )

        if not re.fullmatch(INFO_FILE_PATTERN, content):
            raise RuntimeError("Info file generation produced erroneous output...")

        with self.info_file.open(mode="w") as info_file:
            info_file.write(content)

    ### File I/O ###

    def _get_protocol_checksum(self) -> int:
        """ Return an Adler-32 checksum representing the protocol. """

        content: List[str] = []
        protocol: Protocol = self._load_protocol()
        record: Record
        # Entries are always given back in alphabetical order by year, month, and day
        for record in protocol.entries:
            content.append(repr(record))

        checkbytes: bytes = ";".join(content).encode("utf-8")
        checksum: int = zlib.adler32(checkbytes)
        return checksum

    ### Protocol access (high level) ###

    def _load_protocol(self) -> Protocol:
        """ Load Protocol (lazily). """
        return Protocol(directory=self.records_directory)

    def _load_protocol_date(self, date: dt.date) -> ProtocolDay:
        """ Load protocol for the given date (lazily). """
        return ProtocolDay(
            date=date,
            root_directory=self.records_directory,
        )

    def _load_protocol_range(self, r_start: dt.date, r_end: dt.date) -> ProtocolMeta:
        """ Load protocol for the given range (lazily). """
        return ProtocolRange(
            first=r_start,
            last=r_end,
            root_directory=self.records_directory,
        )

    ### File system I/O (low level) ###

    def _ensure_work_dir_exists(self) -> None:
        """ Ensure the work and protocol directories exist and create it if it doesn't. """

        directory: pathlib.Path
        for directory in [self.work_directory, self.records_directory]:
            if not directory.exists():
                print(f"Initialized the directory {directory.resolve()}")
            elif not directory.is_dir():
                raise IOError(
                    f"Directory path {directory.resolve()} is taken by a file; please delete it."
                )

        # Nested creation (creates all parent directories, too)
        self.records_directory.mkdir(parents=True, exist_ok=True)
