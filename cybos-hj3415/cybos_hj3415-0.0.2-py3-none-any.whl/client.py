from socket import *
import pickle
import data

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class Command:
    BUFSIZ = 1024
    PORT = 21567

    def __init__(self, host='127.0.0.1'):
        self.host = host
        self.addr = (self.host, self.PORT)
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)

    def account(self) -> data.AccountData:
        self.udp_sock.sendto('account'.encode(), self.addr)
        raw_data, addr = self.udp_sock.recvfrom(self.BUFSIZ)
        acc_data = pickle.loads(raw_data)
        logger.info(acc_data)
        return acc_data


