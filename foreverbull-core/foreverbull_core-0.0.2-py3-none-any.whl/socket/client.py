from foreverbull_core.models.socket import SocketConfig, Request
from foreverbull_core.socket.nanomsg import NanomsgSocket


class SocketClient:
    def __init__(self, host) -> None:
        self.config = SocketConfig(socket_type="replier", host=host)
        self._socket = NanomsgSocket(self.config)

    def url(self):
        return f"tcp://{self.config.host}:{self.config.port}"

    def send(self, message):
        self._socket.send(message.dump())

    def recv(self):
        data = self._socket.recv()
        return Request.load(data)

    def close(self):
        self._socket.close()
