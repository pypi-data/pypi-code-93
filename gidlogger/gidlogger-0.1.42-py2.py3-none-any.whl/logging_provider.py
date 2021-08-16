
# * Standard Library Imports -->
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps, partial, cached_property
from pathlib import Path
from contextlib import contextmanager, asynccontextmanager
from typing import Optional, Union, Any, Iterable, TYPE_CHECKING, ClassVar, Callable
from datetime import datetime, timezone, timedelta, tzinfo
from dataclasses import dataclass
from pprint import pprint, pformat
from pytz import all_timezones, country_timezones, country_names, timezone as pytz_timezone
from gidlogger.utility.timestuff import QuickTimezone
from gidlogger.formatter import PreMadeFormatterFactory
import json
from typing import IO, TextIO, BinaryIO
from collections import defaultdict
import shutil
from gidlogger.logger_functions import CustomFormatter
from gidlogger.utility.misc import FileSizeParser


class FileNameData:
    defaults: ClassVar[dict[str, Any]] = {'filename': 'logfile',
                                          'extension': 'log',
                                          'datetime_format': "%Y-%m-%d_%H-%M-%S", }

    def __init__(self,
                 extension: Optional[str] = None,
                 raw: Optional[str] = None,
                 datetime_in_name: Optional[Union[bool, str]] = True,
                 dt_timezone: Optional[Union[str, tzinfo, QuickTimezone]] = None,
                 bracket_datetime: Optional[bool] = True) -> None:
        self._orig_arguments = {'extension': extension, 'raw': raw, "datetime_in_name": datetime_in_name, 'timezone': timezone, 'bracket_datetime': bracket_datetime}
        self.datetime_format = datetime_in_name
        self.extension = extension
        self.dt_timezone = dt_timezone
        self.bracket_datetime = bracket_datetime
        self.raw = raw

        self._process_attrs()

    def _process_datetime_in_name(self):
        if self.datetime_format is None:
            self.datetime_format = ""

        elif isinstance(self.datetime_format, bool):
            self.datetime_format = self.defaults.get('datetime_format') if self.datetime_format is True else ""

        elif isinstance(self.datetime_format, str):
            self.datetime_format = self.datetime_format
        else:
            raise TypeError(f"arg 'datetime_in_name' can either be a datetime format string, a boolean value or None. Not {self.datetime_format!r}")

    def _process_raw(self):
        for possible_name in (self.raw, os.getenv('APP_NAME', None), self.defaults.get('filename')):
            if possible_name is not None:
                self.raw = possible_name
                break

    def _process_dt_timezone(self):

        if isinstance(self.dt_timezone, tzinfo):
            self.dt_timezone = self.dt_timezone
        elif isinstance(self.dt_timezone, str):
            if len(self.dt_timezone) == 2:
                tz_name = country_timezones.get(self.dt_timezone.upper())[0]
            elif '/' in self.dt_timezone:
                tz_name = self.dt_timezone
            else:
                mod_timezone = self.dt_timezone.casefold()
                for _name in all_timezones:
                    _name_parts = set(_name.casefold().split('/'))
                    if mod_timezone in _name_parts:
                        tz_name = _name
                        break
            if tz_name is None:
                self.dt_timezone = None
            else:
                self.dt_timezone = pytz_timezone(pytz_timezone)

    def _process_bracket_datetime(self):
        if self.bracket_datetime is True:
            self.bracket_datetime = ("[", "]")
        else:
            self.bracket_datetime = ("", "")

    def _process_extension(self):
        if self.extension is None:
            self.extension = self.defaults.get('extension')
        self.extension = self.extension.lstrip('.')

    def _process_attrs(self):
        self._process_datetime_in_name()
        self._process_raw()
        self._process_dt_timezone()
        self._process_bracket_datetime()
        self._process_extension()

    @ property
    def base_template(self) -> str:
        if not self.datetime_format:
            return "{me.raw}"

        return "{me.raw}_{me.bracket_datetime[0]}{me.datetime_string}{me.bracket_datetime[1]}"

    @ property
    def full_template(self) -> str:
        base = self.base_template
        return base + '.{me.extension}'

    @ property
    def datetime_string(self) -> str:
        dt = datetime.now(tz=self.dt_timezone)
        return dt.strftime(self.datetime_format)

    def get_full_name(self):

        return self.full_template.format(me=self)


class EachRunRotatingFileHandler(RotatingFileHandler):
    _namer: Callable = None
    _rotator: Callable = None

    def __init__(self,
                 folder: Union[str, os.PathLike],
                 backup_folder: Optional[Union[str, os.PathLike]] = None,
                 raw_filename: Optional[str] = None,
                 extension: Optional[str] = None,
                 maxBytes: Optional[Union[str, int]] = "10 mb",
                 backupCount: Optional[int] = 10,
                 datetime_in_name: Optional[Union[bool, str]] = True,
                 bracket_datetime: Optional[bool] = True,
                 dt_timezone: Optional[Union[str, tzinfo, QuickTimezone]] = None,
                 old_logs_suffix: Optional[str] = None) -> None:

        self.filename_data = FileNameData(raw=raw_filename, extension=extension, datetime_in_name=datetime_in_name, bracket_datetime=bracket_datetime, dt_timezone=dt_timezone)
        self.folder = Path(folder)
        self.backup_folder = self.folder.joinpath('old_logs') if backup_folder is None else Path(backup_folder)
        self.old_logs_suffix = "" if old_logs_suffix is None else f"_{old_logs_suffix.strip('_')}"

        super().__init__(self._make_full_path(), maxBytes=FileSizeParser.parse(maxBytes), backupCount=backupCount, encoding='utf-8', delay=False, errors='ignore')
        self._setup()

    def _setup(self):
        self.namer = self.default_namer
        self.rotator = self.default_rotator
        self.setFormatter(PreMadeFormatterFactory.get('file', max_func_name_length=28, max_module_name_length=18))
        self._move_old_logs()
        self._limit_old_logs()
        return self.baseFilename

    @staticmethod
    def _ensure_folder_exist(folder: Path) -> None:
        if folder.exists() is False:
            folder.mkdir(exist_ok=True, parents=True)

    def _move_old_logs(self):
        for file in self.folder.iterdir():
            self._ensure_folder_exist(self.backup_folder)
            if file.is_file() and file.suffix == f".{self.filename_data.extension}" and file.name != Path(self.baseFilename).name:
                tgt = self.namer(file)

                shutil.move(file, tgt)

    def _limit_old_logs(self):
        old_logs = sorted([file for file in self.backup_folder.iterdir() if file.is_file() and file.suffix == f".{self.filename_data.extension}"], key=lambda x: x.stat().st_mtime)
        if len(old_logs) > 0:
            while len(old_logs) > self.backupCount:
                oldest = old_logs.pop(0)
                os.remove(oldest)

    def _make_full_path(self):
        self._ensure_folder_exist(self.folder)
        _out = self.folder.joinpath(self.filename_data.get_full_name())

        return _out

    def default_namer(self, default_name: Optional[Union[str, os.PathLike, Path]]):
        new_name = f"{default_name.stem}{self.old_logs_suffix}"
        base_name_part = default_name.stem
        new_file_name = self.backup_folder.joinpath(default_name.name).with_stem(new_name)
        number = 0
        while new_file_name.exists():
            number += 1
            new_stem = f"{base_name_part}_{number}{self.old_logs_suffix}"
            new_file_name = new_file_name.with_stem(new_stem)

        return new_file_name

    def default_rotator(self, source: Union[str, os.PathLike, Path], dest: Union[str, os.PathLike, Path]):
        print(f"{source=} || {dest=}")
        if self.backupCount <= 0:
            os.remove(source)
        else:
            shutil.move(source, dest)
            self._move_old_logs()
            self._limit_old_logs()

    def doRollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            backup_file_name = self.rotation_filename(self.baseFilename)
            self.rotate(self.baseFilename, backup_file_name)

        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record: logging.LogRecord) -> int:
        return super().shouldRollover(record)


if __name__ == "__main__":
    pass
