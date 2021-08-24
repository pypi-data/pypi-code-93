import os
import sys
import platform
import signal
import contextlib
from subprocess import Popen, PIPE
from .logger import Logger
from .settings import *
from .file_utils import *
from .settings import *


def get_pager():
    if platform.system() == 'Windows':
        return WindowsPager()
    else:
        return PosixPager()


@contextlib.contextmanager
def ignore_ctrl_c():
    original = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, original)


class PagerBase(object):

    def __init__(self, output_stream=sys.stdout):
        self.output_stream = output_stream

    PAGER = None

    def _get_pager_cmdline(self):
        pager = PAGER or self.PAGER
        return pager.split(' ')

    def page(self, contents):
        if USE_PAGER:
            converted_content = self._convert_doc_content(contents)
            self._send_output_to_pager(converted_content)
        else:
            print(contents, flush=True)

    def _check_pager_cmdline(self):
        self.cmdline = self._get_pager_cmdline()
        if not exists_on_path(self.cmdline[0]):
            # Logger.debug(f"Pager '{cmdline[0]}' not found in PATH.")
            # self.output_stream.write(output.decode('utf-8') + "\n")
            # self.output_stream.flush()
            raise DSOException(f"Pager '{self.cmdline[0]}' not found in PATH.")

    def _send_output_to_pager(self, output):
        self._check_pager_cmdline()
        p = self._popen(self.cmdline, stdin=PIPE)
        p.communicate(input=output)

    def _popen(self, *args, **kwargs):
        return Popen(*args, **kwargs)

    def _convert_doc_content(self, contents: str):
        return contents.encode(encoding='utf-8')


class PosixPager(PagerBase):

    PAGER = 'less -R'

    def _send_output_to_pager(self, output):
        self._check_pager_cmdline()
        with ignore_ctrl_c():
            p = self._popen(self.cmdline, stdin=PIPE)
            p.communicate(input=output)

class WindowsPager(PagerBase):

    PAGER = 'more'

    def _popen(self, *args, **kwargs):
        kwargs['shell'] = True
        return Popen(*args, **kwargs)


Pager = get_pager()
