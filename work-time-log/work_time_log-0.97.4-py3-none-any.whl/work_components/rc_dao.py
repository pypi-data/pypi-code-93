#!/usr/bin/env python3

""" The DAO for the runtime configuration file. """

import io
import json
import os
from typing import IO, Dict, List, Optional
from work_components import consts

from work_components.consts import RC_FILE_PATH

# When a new key is to be added:
# - Add key string as class variable
# - Add object to __init__()
# - Add to _dump(), _load()
# - Implement check in _ensure_dict_correctness()
# - Add example data to _example_rc()
# - (optional) Add verification to verify_configuration()
# In work.py:
# - Add actual functionality related to the configuration
# - (optional) Add see target to see()


TIME_FORMAT = "%H:%M"


class RCError(IOError):
    def __init__(self, msg):
        super().__init__("RC file erroneous! {}".format(msg))


class RC(object):

    expected_hours_k = "expected_hours"

    def __init__(self):
        self.expected_hours: Optional[Dict[str, float]] = None

    ### I/O ###

    def _dump(self, rc_file: IO) -> None:
        """ Write this RC to file. """

        # Convert data to JSON-formattable dict
        data: Dict = {
            RC.expected_hours_k: self.expected_hours,
        }
        RC._ensure_dict_correctness(data)

        json.dump(data, rc_file, indent="\t")

    def _load(self, rc_file: IO) -> None:
        """ Load an RC from file. """

        data = json.load(rc_file)
        RC._ensure_dict_correctness(data)

        self.expected_hours = data[RC.expected_hours_k]

    ### Static methods ###

    @staticmethod
    def create_rc_file() -> None:
        """ Create a RC file with default values. """

        if os.path.lexists(RC_FILE_PATH):
            raise FileExistsError()

        # Create RC with default values
        rc: RC = RC._default_rc()
        with open(RC_FILE_PATH, "w") as rc_file:
            rc._dump(rc_file)

        print("RC file created at {}".format(RC_FILE_PATH))

    @staticmethod
    def example_rc_file() -> str:
        """ Create the contents of an example RC file, setting all keys. """
        rc: RC = RC._default_rc()
        with io.StringIO() as output:
            rc._dump(output)
            return output.getvalue()

    @staticmethod
    def _default_rc():
        # type: () -> RC
        """ Create an example RC object with mandatory values set. """
        rc = RC()
        rc.expected_hours = {
            d: v for d, v in zip(consts.WEEKDAYS, [8.0] * 5 + [0.0] * 2)
        }
        return rc

    @staticmethod
    def load_rc():  # -> RC
        """ Load a RC. If any RC file exists, retrieve it. If not, creates a basic file. """

        if not os.path.lexists(RC_FILE_PATH):
            RC.create_rc_file()
            print(f"  Please check the file and update according to your needs.\n")

        rc = RC()
        with open(RC_FILE_PATH, "r") as rc_file:
            rc._load(rc_file)
        return rc

    @staticmethod
    def path() -> str:
        """ Return the RC file path. """
        return RC_FILE_PATH

    @staticmethod
    def _ensure_dict_correctness(data: Dict) -> None:
        """ Ensure that the dict is fit for JSON (de)serialization. Raises if not. """

        expected_keys: List[str] = [RC.expected_hours_k]
        for k in expected_keys:
            if k not in data:
                raise RCError(f'Missing expected key "{k}"')

        for k in data:
            if k not in expected_keys:
                raise RCError(f'Unexpected key "{k}"')

        pop_key = lambda l, k: l.pop(l.index(k))

        # Verify expected_hours
        e_h = data[pop_key(expected_keys, RC.expected_hours_k)]
        ## Expected hours may be None or { "Monday": 8.0, Tuesday: 0.0, ... }
        if e_h is not None:
            if unexpected_days := set(e_h.keys()) - set(consts.WEEKDAYS):
                raise RCError(
                    f"Unexpected key(s) for {RC.expected_hours_k}: "
                    + ", ".join(unexpected_days)
                    + f"; expects one of: {', '.join(consts.WEEKDAYS)}"
                )

            if missing_days := set(consts.WEEKDAYS) - set(e_h.keys()):
                raise RCError(
                    f"Missing expected key(s) for {RC.expected_hours_k}: "
                    + ", ".join(missing_days)
                )

            min_hours, max_hours = consts.ALLOWED_WORK_HOURS
            if invalid_hours := [
                expected_hour_value
                for expected_hour_value in e_h.values()
                if expected_hour_value < min_hours or expected_hour_value > max_hours
            ]:
                raise RCError(
                    f"Invalid value(s) for {RC.expected_hours_k}: "
                    + ", ".join([str(i_h) for i_h in invalid_hours])
                    + "; expects values in (0, 24)."
                )

        if len(expected_keys) > 0:
            raise RuntimeError("Missed a key!")
