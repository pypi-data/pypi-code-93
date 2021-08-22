from __future__ import annotations

import logging
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

log = logging.getLogger("compliance_assistant")
_start_time = time.time()


def log_dataframe(worksheet_sheet: pd.DataFrame) -> None:
    path = time.strftime("%Y-%m-%d %H-%M-%S") + " - compliance-assistant"
    log.info(f"Data saved to {path}")
    worksheet_sheet.to_feather(path)


class _DeltaFormatter(logging.Formatter):
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, validate: bool = True):
        super().__init__(fmt=fmt, datefmt=datefmt, style="{", validate=validate)

    def format(self, record: logging.LogRecord) -> str:
        record.delta = round(record.created - _start_time, 5)
        return super().format(record)


def _setup_log_file() -> logging.Logger:
    import sys  # pylint: disable=import-outside-toplevel

    log.setLevel(logging.DEBUG)

    formatter = _DeltaFormatter(fmt="{asctime}.{msecs:03.0f} [{delta:.3f}] ({levelname}): {message}", datefmt="%Y-%m-%d %H:%M:%S")
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)

    log.addHandler(console)

    log.info("==================================================================")
    log.info("Please send this file to the developer peter.moretti@scouts.org.uk")
    log.info("==================================================================")

    log.info(f"OS: {sys.platform}")
    log.info(f"US: Compliance Assistant - {__file__}")  # workbook path
    log.info(f"Version: 6070.15")

    return log


_setup_log_file()
