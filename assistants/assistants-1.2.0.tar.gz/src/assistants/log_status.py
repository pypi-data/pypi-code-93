from __future__ import annotations

import logging
import logging.config
import sys
import time

_start_time = time.time()


class _DeltaFormatter(logging.Formatter):
    def __init__(self, fmt: str | None = None, date_fmt: str | None = None):
        super().__init__(fmt=fmt, datefmt=date_fmt, style="{", validate=True)

    def format(self, record: logging.LogRecord) -> str:
        record.delta = round(record.created - _start_time, 5)
        return super().format(record)


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "delta": {
                "()": _DeltaFormatter,
                "fmt": "{asctime}.{msecs:03.0f} [{delta:.3f}] ({levelname}): {message}",
                "date_fmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "delta",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "compliance_assistant": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False
            },
            "compass_interface": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
        }
    }
)

log = logging.getLogger("compliance_assistant")
log.info("==================================================================")
log.info("Please send this file to the developer peter.moretti@scouts.org.uk")
log.info("==================================================================")

log.info(f"OS: {sys.platform}")
log.info(f"US: Compliance Assistant - {__file__}")  # workbook path
log.info(f"Version: 6070.15")
