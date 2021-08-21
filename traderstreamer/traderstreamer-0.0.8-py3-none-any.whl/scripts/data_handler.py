from tradernetwork import (
    PubSocket,
    PullSocket,
    ProxySocket,
)


class SecondDataHandler:

    def __init__(self):
        self.pub_socket = PubSocket(4005)

        sockets = {
            'pull_socket_1': PullSocket(4003),
            'pull_socket_2': PullSocket(4004)
        }

        proxy = ProxySocket(sockets)
        proxy.callback = self.callback
        proxy.start_proxy_server_loop()

    def callback(self, socket_name: str, data: dict):
        self.pub_socket.publish(data)


if __name__ == '__main__':
    dh = SecondDataHandler()