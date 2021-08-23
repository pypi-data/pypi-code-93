from __future__ import absolute_import

import select

from math import ceil
from simpy.io.base import (BaseIOEnvironment, BaseTCPSocket, BaseSSLSocket)


class Environment(BaseIOEnvironment):
    def __init__(self, fds=None, type='epoll'):
        BaseIOEnvironment.__init__(self, fds)

        if type == 'epoll':
            self._read_flag = select.EPOLLIN
            self._write_flag = select.EPOLLOUT
            self._poll = select.epoll()
            self._iowait = self._epoll_iowait
        elif type == 'poll':
            self._read_flag = select.POLLIN
            self._write_flag = select.POLLOUT
            self._poll = select.poll()
            self._iowait = self._poll_iowait
        else:
            raise RuntimeError('Invalid poll type "%s"' % type)

        self._io_state = {}

    def register_port(self, fileno, port):
        BaseIOEnvironment.register_port(self, fileno, port)
        self._io_state[fileno] = 0
        self._poll.register(fileno, 0)

    def unregister_port(self, fileno):
        BaseIOEnvironment.unregister_port(self, fileno)
        del self._io_state[fileno]
        self._poll.unregister(fileno)

    def port_want_read(self, fileno):
        state = self._io_state[fileno] | self._read_flag
        self._io_state[state] = state
        self._poll.modify(fileno, state)

    def port_want_write(self, fileno):
        state = self._io_state[fileno] | self._write_flag
        self._io_state[state] = state
        self._poll.modify(fileno, state)

    def _epoll_iowait(self, timeout):
        # TODO Expect timeout to be an int of milliseconds? 
        if timeout is not None:
            timeout = ceil(timeout * 1000) / 1000
        else:
            timeout = -1

        for fd, eventmask in self._poll.poll(timeout):
            sock = self.fds[fd]
            sock._flags = 0
            self._poll.modify(fd, 0)

            if eventmask & self._read_flag:
                sock._ready_read()

            if eventmask & self._write_flag:
                sock._ready_write()

    def _poll_iowait(self, timeout):
        # TODO Expect timeout to be an int of milliseconds? 
        if timeout is not None:
            timeout = ceil(timeout * 1000)

        for fd, eventmask in self._poll.poll(timeout):
            sock = self.fds[fd]
            sock._flags = 0
            self._poll.modify(fd, 0)

            if eventmask & self._read_flag:
                sock._ready_read()

            if eventmask & self._write_flag:
                sock._ready_write()


class TCPSocket(BaseTCPSocket):
    pass


class SSLSocket(BaseSSLSocket):
    pass
