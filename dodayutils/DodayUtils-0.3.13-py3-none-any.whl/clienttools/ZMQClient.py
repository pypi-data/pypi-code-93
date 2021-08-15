# ZMQ Client that pushes request and
# subscribe requests
import os
import json
import time
from gadgethiServerUtils.GadgethiZMQ import GadgethiZMQ

class ZMQClient(GadgethiZMQ):
    """
    This is the ZMQClient for pushing request
    under push pull topology and subscribing
    requests under pub-sub topology. 

    - Input:
        * address: e.g. "tcp://*:5557", "tcp://211.72.230.173:5558"
        * mode: currently support PUSH, SUB
        * broadcast_message_header (optional): needed for subscribe
    """
    def __init__(self, **configs):
        super().__init__(**configs)

    def setup(self, **configs):
        mode = configs.get("mode", "undefined")
        # Setup topology based on modes
        if mode == "PUSH":
            self.sender = self.context.socket(zmq.PUSH)
            self.sender.bind(configs["address"])
        elif mode == "SUB":
            self.socket = self.context.socket(zmq.SUB)
            self.socket.connect(configs["address"])#"tcp://211.72.230.173:5558"
            self.socket.setsockopt_string(zmq.SUBSCRIBE, configs.get("broadcast_message_header", ""))
        else:
            raise Exception("ZMQ Client mode: %s not supported" % mode)