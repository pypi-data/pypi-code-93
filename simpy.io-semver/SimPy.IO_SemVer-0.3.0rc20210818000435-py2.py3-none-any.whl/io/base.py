import errno
import os
import socket
import ssl
import types
from heapq import heappush, heappop
from socket import error as SocketError

import sys
from itertools import count
from simpy.core import (Environment, BoundClass, Event, Process, Timeout,
                        AllOf, AnyOf, NORMAL)
from simpy.io.network import socket_error
from simpy.io.platform import blocking_io_errors, invalid_argument
from time import time


class BaseIOEnvironment(Environment):
    def __init__(self, fds=None):
        if fds is None:
            fds = {}

        self._queue = []
        """A list with all currently scheduled events."""
        self._eid = count()
        self._active_proc = None

        self.fds = fds

        BoundClass.bind_early(self)

    # FIXME Move this into the Environment?
    @property
    def active_process(self):
        """Property that returns the currently active process."""
        return self._active_proc

    process = BoundClass(Process)
    timeout = BoundClass(Timeout)
    event = BoundClass(Event)
    all_of = BoundClass(AllOf)
    any_of = BoundClass(AnyOf)
    suspend = event
    start = process

    def exit(self, value=None):
        """Convenience function provided for Python versions prior to 3.3. Stop
        the current process, optionally providing a ``value``.

        .. note::

            From Python 3.3, you can use ``return value`` instead."""
        raise StopIteration(value)

    @property
    def now(self):
        return time()

    def schedule(self, event, priority=NORMAL, delay=0):
        heappush(self._queue, (time() + delay, priority, next(self._eid),
            event))

    def _iowait(self, timeout):
        raise NotImplementedError(self)

    def register_port(self, fileno, port):
        if fileno is None:
            raise ValueError('fileno is None')
        self.fds[fileno] = port

    def unregister_port(self, fileno):
        if fileno is None:
            raise ValueError('fileno is None')
        del self.fds[fileno]

    def port_want_read(self, fileno):
        raise NotImplementedError(self)

    def port_want_write(self, fileno):
        raise NotImplementedError(self)

    def step(self):
        """Executes the next event. TODO Improve."""
        while True:
            timeout = self._queue[0][0] - time() if self._queue else None
            if timeout is not None and timeout < 0:
                break
            self._iowait(timeout)

        event = heappop(self._queue)[3]

        for callback in event.callbacks:
            callback(event)

        # Mark event as processed.
        event.callbacks = None

        if not event._ok:
            if not hasattr(event, 'defused'):
                # The event has not been defused by a callback.
                raise event._value

    def close(self):
        for fileno, socket in list(self.fds.items()):
            try:
                socket.close()
            except OSError as e:
                if e.errno != errno.EBADF:
                    raise


class Read(Event):
    def __init__(self, sock, amount):
        if sock._reader:
            raise RuntimeError('Already reading')
        sock._reader = self

        Event.__init__(self, sock.env)
        self.sock = sock
        self.amount = amount
        sock._try_read()


class Write(Event):
    def __init__(self, sock, data):
        if sock._writer:
            raise RuntimeError('Already writing')
        sock._writer = self

        Event.__init__(self, sock.env)
        self.sock = sock
        self.data = data
        sock._try_write()


def _ebadf(*args):
    raise socket_error(errno.EBADF)


class Port(object):
    """Interface for generic data input and output."""

    def __init__(self, env, fileno):
        self.env = env
        self.fileno = fileno

        self._writer = None
        self._reader = None

        self._ready_read = None
        self._ready_write = None

        self.env.register_port(self.fileno, self)

    def _do_read(self):
        """Read data and trigger the :attr:`_reader` with the data.
        :attr:`_reader` must also be set to ``None``."""
        raise NotImplementedError(self)

    def _do_write(self):
        """Write data from the :attr:`_writer` and trigger it with the amount
        of data written. :attr:`_writer` must also be set to ``None``."""
        raise NotImplementedError(self)

    def close(self):
        # Remove events.
        if self._reader is not None:
            self._reader.fail(socket_error(errno.EBADF))
            self._reader = None
        if self._writer is not None:
            self._writer.fail(socket_error(errno.EBADF))
            self._writer = None
        if self.fileno is not None:
            self.env.unregister_port(self.fileno)
            self.fileno = None


class Accept(Event):
    def __init__(self, sock):
        if sock._reader:
            raise RuntimeError('Already accepting')
        sock._reader = self

        Event.__init__(self, sock.env)
        self.sock = sock
        sock._do_accept()


class Connect(Event):
    def __init__(self, sock, address):
        if sock._reader:
            raise RuntimeError('Already connecting')
        sock._reader = self

        Event.__init__(self, sock.env)
        self.sock = sock
        self.address = address
        sock._do_connect()


class Link(Port):
    """Interface for reliable and ordered data exchange (e.g. TCP)."""

    def __init__(self, env, fileno):
        Port.__init__(self, env, fileno)

        self._try_read = self._do_read
        self._try_write = self._do_write
        self._try_connect = self._do_connect
        self._try_accept = self._do_accept

        self.read = types.MethodType(Read, self)
        self.write = types.MethodType(Write, self)
        self.connect = types.MethodType(Connect, self)
        self.accept = types.MethodType(Accept, self)

    def _do_connect(self):
        raise NotImplementedError(self)

    def _do_accept(self):
        raise NotImplementedError(self)

    def bind(self, address):
        raise NotImplementedError(self)

    def listen(self, backlog=5):
        raise NotImplementedError(self)

    def accept(self):
        raise NotImplementedError(self)

    @property
    def address(self):
        raise NotImplementedError(self)

    @property
    def peer_address(self):
        raise NotImplementedError(self)

    @classmethod
    def server(cls, env, address, backlog=5):
        socket = cls(env)
        socket.bind(address)
        socket.listen(backlog)
        return socket

    @classmethod
    def connection(cls, env, address):
        socket = cls(env)
        return socket.connect(address)


class Bus(Port):
    def read(self, amount):
        raise NotImplementedError(self)

    def write(self, address, data):
        raise NotImplementedError(self)


# FIXME fcntl is not available on windows.
import fcntl


class Pipe(Port):
    def __init__(self, env, fileno):
        Port.__init__(self, env, fileno)

        # Make the file descriptor non-blocking.
        flags = fcntl.fcntl(fileno, fcntl.F_GETFL)
        fcntl.fcntl(fileno, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        self._try_read = self._do_read
        self._try_write = self._do_write
        self._ready_read = self._do_read
        self._ready_write = self._do_write

        self.read = types.MethodType(Read, self)
        self.write = types.MethodType(Write, self)

    @classmethod
    def pair(cls, env):
        r, w = os.pipe()
        return cls(env, r), cls(env, w)

    def _do_read(self):
        try:
            self._reader._value = os.read(self.fileno, self._reader.amount)
            if not self._reader._value:
                self._reader._ok = False
                self._reader._value = socket_error(errno.EPIPE)
            else:
                self._reader._ok = True
            self.env.schedule(self._reader)
        except OSError as e:
            if e.errno == errno.EAGAIN:
                self.env.port_want_read(self.fileno)
                return

            self._reader.fail(e)
        self._reader = None

    def _do_write(self):
        try:
            self._writer._value = os.write(self.fileno, self._writer.data)
            self._writer._ok = True
            self.env.schedule(self._writer)
        except OSError as e:
            if e.errno == errno.EAGAIN:
                self.env.port_want_write(self.fileno)
                return

            self._writer.fail(e)
        self._writer = None

    def close(self):
        os.close(self.fileno)
        Port.close(self)


class BaseTCPSocket(Link):
    def __init__(self, env, sock=None):
        if sock is None:
            sock = socket.socket()
        self.sock = sock

        self.sock.setblocking(False)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        Link.__init__(self, env, self.sock.fileno())

    @property
    def address(self):
        try:
            return self.sock.getsockname()
        except SocketError as e:
            # Windows quirk: Return invalid address if the socket is not yet
            # connected as is done by linux.
            if sys.platform == 'win32':
                if e.errno == invalid_argument:
                    return ('0.0.0.0', 0)

            raise e

    @property
    def peer_address(self):
        return self.sock.getpeername()

    def _do_connect(self):
        if self.fileno is None:
            raise socket_error(errno.EBADF)

        try:
            self.sock.setblocking(1)
            self.sock.connect(self._reader.address)
        except SocketError as e:
            if e.errno in blocking_io_errors:
                # Windows quirk: Ignore blocking IO errors on connect.
                pass
            elif e.errno == errno.EISCONN:
                # Windows quirk: Ignore connects on already connected sockets
                # as linux does.
                pass
            else:
                raise e
        finally:
            self.sock.setblocking(0)

        # Set IO state.
        self._try_read = self._do_read
        self._try_write = self._do_write
        self._ready_read = self._do_read
        self._ready_write = self._do_write

        self._reader.succeed(self)
        self._reader = None

    def _do_serve(self):
        # Set IO state.
        self._try_read = self._do_read
        self._try_write = self._do_write
        self._ready_read = self._do_read
        self._ready_write = self._do_write

        self._reader.succeed(self)
        self._reader = None

    def _do_read(self):
        try:
            self._reader._value = self.sock.recv(self._reader.amount)
            if not self._reader._value:
                self._reader._ok = False
                self._reader._value = socket_error(errno.ECONNRESET)
            else:
                self._reader._ok = True
            self.env.schedule(self._reader)
        except SocketError as e:
            if e.errno in blocking_io_errors:
                self.env.port_want_read(self.fileno)
                return

            self._reader.fail(e)
        self._reader = None

    def _do_write(self):
        try:
            self._writer._value = self.sock.send(self._writer.data)
            self._writer._ok = True
            self.env.schedule(self._writer)
        except SocketError as e:
            if e.errno in blocking_io_errors:
                self.env.port_want_write(self.fileno)
                return

            self._writer.fail(e)
        self._writer = None

    def _do_accept(self):
        try:
            link = type(self)(self.env, self.sock.accept()[0])
            # Pass ownership of the accept event to the link.
            link._reader = self._reader
            link._do_serve()
        except SocketError as e:
            if e.errno in blocking_io_errors:
                self.env.port_want_read(self.fileno)
                return

            self._reader.fail(e)
        self._reader = None

    def bind(self, address):
        self.sock.bind(address)
        self._try_read = self._do_accept
        self._ready_read = self._do_accept

    def listen(self, backlog=5):
        self.sock.listen(backlog)

    def close(self):
        self.sock.close()
        Link.close(self)


class BaseSSLSocket(BaseTCPSocket):
    # TODO Raise errors on _do_read/_do_write/_do_accept if the handshake is
    # not completed yet.

    def __init__(self, env, sock=None, **kwargs):
        if sock is None:
            # Non-blocking sockets are not allowed to block for the handshake.
            kwargs['do_handshake_on_connect'] = None
            sock = ssl.wrap_socket(socket.socket(), **kwargs)

        BaseTCPSocket.__init__(self, env, sock)

        self._ssl_event = None

    def _do_connect(self):
        if self.fileno is None:
            raise socket_error(errno.EBADF)

        try:
            self.sock.setblocking(1)
            self.sock.connect(self._reader.address)
        except SocketError as e:
            if e.errno in blocking_io_errors:
                # Windows quirk: Ignore blocking IO errors on connect.
                pass
            elif e.errno == errno.EISCONN:
                # Windows quirk: Ignore connects on already connected sockets as
                # linux does.
                pass
            else:
                raise e
        finally:
            self.sock.setblocking(0)

        self._ready_read = self._do_handshake
        self._ready_write = self._do_handshake
        self._do_handshake()

    def _do_serve(self):
        self._ready_read = self._do_handshake
        self._ready_write = self._do_handshake
        self._do_handshake()

    def _do_read(self):
        try:
            buf = bytearray(self._reader.amount)
            self._reader._value = buf[:self.sock.recv_into(buf)]
            if not self._reader._value:
                self._reader._ok = False
                self._reader._value = socket_error(errno.ECONNRESET)
            else:
                self._reader._ok = True
            self.env.schedule(self._reader)
        except ssl.SSLError as e:
            if e.errno == ssl.SSL_ERROR_WANT_READ:
                self.env.port_want_read(self.fileno)
                return

            self._reader.fail(e)
        except SocketError as e:
            if e.errno in blocking_io_errors:
                self.env.port_want_read(self.fileno)
                return

            self._reader.fail(e)
        self._reader = None

    def _do_write(self):
        try:
            self._writer._value = self.sock.send(self._writer.data)
            self._writer._ok = True
            self.env.schedule(self._writer)
        except ssl.SSLError as e:
            if e.errno == ssl.SSL_ERROR_WANT_WRITE:
                self.env.port_want_write(self.fileno)
                return

            self._writer.fail(e)
        except SocketError as e:
            if e.errno in blocking_io_errors:
                self.env.port_want_write(self.fileno)
                return

            self._writer.fail(e)
        self._writer = None

    def _do_accept(self):
        try:
            link = type(self)(self.env, self.sock.accept()[0])
            # Pass ownership of the accept event to the link.
            link._reader = self._reader
            link._do_serve()
        except SocketError as e:
            if e.errno in blocking_io_errors:
                self.env.port_want_read(self.fileno)
                return

            self._reader.fail(e)
        self._reader = None

    def _do_handshake(self):
        """Performs the SSL handshake."""
        if self.sock._sslobj is None:
            # FIXME This wrapping is ugly as it is using SSL internal stuff. It
            # is really necessary?

            self.sock._sslobj = self.sock.context._wrap_socket(self.sock,
                    False, self.sock.server_hostname)

        try:
            # Call do_handshake directly on the _sslobj. SSLSocket.do_handshake
            # checks if the connection is established before really calling
            # _sslobj.do_handshake. This hides ECONNREFUSED errors.
            self.sock._sslobj.do_handshake()
        except ssl.SSLError as err:
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                self.env.port_want_read(self.fileno)
                return
            elif err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                self.env.port_want_write(self.fileno)
                return
            else:
                raise

        self.sock.do_handshake()

        # Handshake has completed. Start IO.
        self._ready_read = self._do_read
        self._ready_write = self._do_write
        self._try_read = self._do_read
        self._try_write = self._do_write

        self._reader.succeed(self)
        self._reader = None
