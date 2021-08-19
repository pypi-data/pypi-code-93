from __future__ import absolute_import

import select

from simpy.io.base import (BaseIOEnvironment, Pipe, BaseTCPSocket,
                           BaseSSLSocket)
from time import time, sleep


class Environment(BaseIOEnvironment):
    def __init__(self, fds=None):
        BaseIOEnvironment.__init__(self, fds)

        # TODO Use an ordered set?
        self._rd, self._wd, self._xd = [], [], []

    def unregister_port(self, fileno):
        BaseIOEnvironment.unregister_port(self, fileno)
        if fileno in self._rd:
            self._rd.remove(fileno)
        if fileno in self._wd:
            self._wd.remove(fileno)
        if fileno in self._xd:
            self._xd.remove(fileno)

    def port_want_read(self, fileno):
        self._rd.append(fileno)

    def port_want_write(self, fileno):
        self._wd.append(fileno)

    def _iowait(self, timeout):
        # Windows quirk: select() does not take empty lists.
        if not (self._rd or self._wd or self._xd):
            if timeout is None:
                # Warning: This point represents a user error. No request to
                # read or write from a socket has been given and no timeout has
                # been given. The program will sleep forever.
                # It has been decided to not raise a warning or exception in
                # this case, because it is not feasible to detect this case in
                # the other backends. Let's see if we hit enough real world
                # cases to convince us otherwise.
                while True:
                    sleep(1)

            to = time() + timeout
            while True:
                duration = to - time()
                if duration <= 0:
                    break
                sleep(duration)
            return

        rd, wd, xd = select.select(self._rd, self._wd, self._xd, timeout)

        for fd in rd:
            self.fds[fd]._ready_read()
            self._rd.remove(fd)

        for fd in wd:
            self.fds[fd]._ready_write()
            self._wd.remove(fd)

        # TODO xd?


class Pipe(Pipe):
    pass


class TCPSocket(BaseTCPSocket):
    pass


class SSLSocket(BaseSSLSocket):
    pass
