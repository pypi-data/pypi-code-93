#!/usr/bin/python3
import json
import socket
from threading import Thread
from time import sleep

from common.logging_config import logger


class WebSocketClient:
    def conn_ws(self, host="127.0.0.1", port=5678):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        return self.sock

    def send_msg(self, msg, encoding="utf-8"):
        if isinstance(msg, dict) or isinstance(msg, list):
            msg = json.dumps(msg)
        logger.debug("send msg ", self.host, self.port, msg)
        if not isinstance(msg, bytes):
            msg = msg.encode(encoding)
        self.sock.send(msg)

    def recv_msg(self, encoding="utf-8"):
        while True:
            msg = self.sock.recv(1024)
            msg = msg.decode(encoding)
            logger.debug("recv msg", self.host, self.port, msg)


if __name__ == "__main__":
    client = WebSocketClient()
    client.conn_ws()
    Thread(target=client.recv_msg).start()
    while True:
        client.send_msg("示范法")
        sleep(2)
