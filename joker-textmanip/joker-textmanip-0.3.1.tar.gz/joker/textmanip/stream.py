#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import os
import sys
import time

from joker.stream import Stream
from joker.stream.shell import ShellStream

_ = [
    Stream,
    ShellStream,
]


def _iter_lines(path, *args, **kwargs):
    with open(path, *args, **kwargs) as fin:
        for line in fin:
            yield line


def _iter_stdin_lines():
    for line in sys.stdin:
        yield line


def iter_lines(path, *args, **kwargs):
    if not path or path in ['-', 'stdin', '/dev/stdin']:
        return _iter_stdin_lines()
    else:
        return _iter_lines(path, *args, **kwargs)


def nonblank_lines_of(path, *args, **kwargs):
    # deprecated
    for line in iter_lines(path, *args, **kwargs):
        line = line.strip()
        if not line:
            continue
        yield line


def _write_lines(lines, path, mode='w', *args, **kwargs):
    with open(path, mode, *args, **kwargs) as fout:
        fout.writelines(lines)


def _write_stdout_lines(lines, target=sys.stdout):
    for line in lines:
        target.write(line)
    target.flush()


def write_lines(lines, path, mode='w', *args, **kwargs):
    if not path or path in ['-', 'stdout', '/dev/stdout']:
        _write_stdout_lines(lines)
    elif path in ['stderr', '/dev/stderr']:
        _write_stdout_lines(lines, sys.stderr)
    else:
        _write_lines(lines, path, mode, *args, **kwargs)


class AtomicTailer(object):
    """
    Read log file on-line
    inspired by https://github.com/six8/pytailer

    a minimized version with this issue fixed:
        https://github.com/six8/pytailer/issues/9
    """

    def __init__(self, file, interval=1., linesep=None, timeout=60):
        self.file = file
        self.start_pos = self.file.tell()
        self.interval = interval
        self.linesep = linesep or os.linesep
        self.timeout = timeout

    @classmethod
    def open(cls, path, *args, **kwargs):
        return cls(open(path), *args, **kwargs)

    def __iter__(self):
        return self.follow()

    def follow(self):
        """\
        follow a growing file
        tldr: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/157035
        """
        tm = time.time()
        while True:
            pos = self.file.tell()
            line = self.file.readline()
            if line.endswith(self.linesep):
                tm = time.time()
                yield line
            else:
                if time.time() - tm > self.timeout:
                    if line:
                        yield line
                    break
                self.file.seek(pos)
                time.sleep(self.interval)

    def follow_lines(self, limit=1000):
        tm = time.time()
        lines = []
        while True:
            if len(lines) >= limit:
                yield lines
                lines = []
            pos = self.file.tell()
            line = self.file.readline()
            if line.endswith(self.linesep):
                tm = time.time()
                lines.append(line)
            else:
                if time.time() - tm > self.timeout:
                    if line:
                        lines.append(line)
                    if lines:
                        yield lines
                    break
                self.file.seek(pos)
                time.sleep(self.interval)
