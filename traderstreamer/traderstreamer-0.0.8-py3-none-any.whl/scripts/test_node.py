from scripts.services import *


class TestStreamerNode:

    streaming = False

    svc1 = bybit_mkt_svc

    def __init__(self):
        pass

    def start(self):
        self.streaming = True

        self.svc1.start()


if __name__ == '__main__':
    odd_node = TestStreamerNode()
    odd_node.start()