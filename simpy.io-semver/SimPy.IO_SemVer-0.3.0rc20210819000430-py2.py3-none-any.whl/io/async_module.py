import asyncore

from simpy.io.base import (BaseIOEnvironment, BaseTCPSocket, BaseSSLSocket)
from time import sleep


class Dispatcher(asyncore.dispatcher):
    def __init__(self, port):
        self.port = port

        # asyncore.dispatcher.__init__ is not called to prevent socket
        # modifications.
        self._fileno = port.fileno

        self._want_read = False
        self._want_write = False

    def readable(self):
        return self._want_read

    def writable(self):
        return self._want_write

    def handle_read(self):
        self.port._ready_read()

    def handle_write(self):
        self.port._ready_write()


class Environment(BaseIOEnvironment):
    def __init__(self):
        BaseIOEnvironment.__init__(self)

        self._dispatchers = {}

    def register_port(self, fileno, port):
        BaseIOEnvironment.register_port(self, fileno, port)
        dispatcher = Dispatcher(port)
        self._dispatchers[fileno] = dispatcher

    def unregister_port(self, fileno):
        BaseIOEnvironment.unregister_port(self, fileno)
        del self._dispatchers[fileno]

    def port_want_read(self, fileno):
        self._dispatchers[fileno]._want_read = True

    def port_want_write(self, fileno):
        self._dispatchers[fileno]._want_write = True

    def _iowait(self, timeout):
        if self.fds:
            asyncore.loop(timeout, False, self._dispatchers, 1)
        else:
            sleep(timeout)


class TCPSocket(BaseTCPSocket):
    pass


class SSLSocket(BaseSSLSocket):
    pass
