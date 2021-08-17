#!/usr/bin/env python3

""" Shared constants """

import os
from typing import List, Tuple

PROTOCOL_VERSION = 3

# Directories
PREFIX = os.path.expanduser("~/.local/share")
DIRECTORY = os.path.join(PREFIX, "work")
DIRECTORY_DEBUG = os.path.join(PREFIX, "debug", "work")

# Paths – work directory
PROTOCOL_DIRECTORY_NAME = "records"
PROTOCOL_FILE_EXTENSION = "wprot"
INFO_FILE_NAME = "info.winf"
RUN_FILE_NAME = "running.wtime"
RECESS_DIRECTORY_NAME = "recess"
RECESS_FILE_EXTENSION = "wvac"

# Configuration – user folder
RC_FILE_PATH = os.path.expanduser("~/.workrc")

# Formats
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

# Patterns
INFO_FILE_CONTENT = "work-time-protocol/protocol-v{}/last-edit:{}/checksum:{}\n"
INFO_FILE_PATTERN = INFO_FILE_CONTENT.format(
    r"(\d{1,2})", r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})", r"(\d+)"
)
TIME_PATTERN = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}"
YEAR_DIR_PATTERN = r"\d{4}"
MONTH_DIR_PATTERN = r"(0[1-9]|1[0-2])"
DAY_PATTERN = r"([0-2][0-9]|3[0-1])"
DAY_FILE_PATTERN = DAY_PATTERN + r"\." + PROTOCOL_FILE_EXTENSION

# Values
WEEKDAYS: List[str] = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
ALLOWED_WORK_HOURS: Tuple[float, float] = (0.0, 24.0)
