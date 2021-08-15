from foreverbull_core.http import HTTPClient
from foreverbull_core.socket.client import SocketClient


class Broker:
    def __init__(self, host, service_id, instance_id, local_host):
        self._host = host
        self._service_id = service_id
        self._instance_id = instance_id
        self._local_host = local_host
        self.http = HTTPClient(host)
        self.socket = SocketClient(self._local_host)

    def mark_as_online(self):
        self.http.service.update_instance(
            self._service_id, self._instance_id, self._local_host, self.socket.config.port, True
        )

    def mark_as_offline(self):
        self.http.service.update_instance(
            self._service_id, self._instance_id, self._local_host, self.socket.config.port, False
        )
