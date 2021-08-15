from pynng import Pub0, Rep0, Req0, exceptions

from .exceptions import SocketClosed, SocketTimeout


class NanomsgSocket:
    SOCKETS = {"publisher": Pub0, "replier": Rep0, "requester": Req0}

    def __init__(self, configuration):
        self._socket = None
        self._configuration = configuration
        socket = self.SOCKETS[configuration.socket_type]
        if configuration.listen:
            self._socket = socket(listen=f"tcp://{configuration.host}:{configuration.port}")
        else:
            self._socket = socket(dial=f"tcp://{configuration.host}:{configuration.port}")
        self._socket.recv_timeout = configuration.recv_timeout
        self._socket.send_timeout = configuration.send_timeout
        if configuration.listen and configuration.port == 0:
            # Pretty hacky way to find the port that OS randomly assigns when it's orginally set as 0
            configuration.port = int(self._socket.listeners[0].url.split(":")[-1])

    def url(self):
        if self._configuration.listen:
            return self._socket.listeners[0].url
        return self._socket.dialers[0].url

    def send(self, data):
        try:
            return self._socket.send(data)
        except exceptions.Timeout as exc:
            raise SocketTimeout(exc)
        except exceptions.Closed as exc:
            raise SocketClosed(exc)

    def recv(self):
        try:
            return self._socket.recv()
        except exceptions.Timeout as exc:
            raise SocketTimeout(exc)
        except exceptions.Closed as exc:
            raise SocketClosed(exc)

    def close(self):
        return self._socket.close()
