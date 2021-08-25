#!/usr/bin/env python

import sys
from logging import Logger as PythonLogger

#  --- Copied from logging module ---
if hasattr(sys, '_getframe'):
    def currentframe():
        return sys._getframe(3)
else:  # pragma: no cover
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back


#  --- Copied from logging module ---


class KomoLogger(PythonLogger):
    def __init__(self, name: str):
        super().__init__(name)
