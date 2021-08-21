"""

파이썬 cybos 서버를 실행시킨 상태에서 서버와 통신하며 여러 명령어를 실행하는 클라이언트 모듈
"""

from socket import *
import pickle
from . import data

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

ACC = 'account'
CPRICE = 'current_price'
IORDER = 'inquire_order'
BUY = 'buy_order'
SELL = 'sell_order'
CANCEL = 'cancel_order'


class Command:
    BUFSIZ = 1024
    PORT = 21567

    def __init__(self, host='127.0.0.1'):
        """

        소켓 통신을 이용하여 cybos 서버에 명령어를 내리는 클래스

        Args:
            host (str): 서버의 호스트 주소 기본값 - 127.0.0.1
        """
        self.host = host
        self.addr = (self.host, self.PORT)
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)

    def account(self) -> data.AccountData:
        self.udp_sock.sendto(ACC.encode(), self.addr)
        raw_data, addr = self.udp_sock.recvfrom(self.BUFSIZ)
        acc_data = pickle.loads(raw_data)
        logger.info(acc_data)
        return acc_data

    def cprice(self, code) -> data.CurrentPriceData:
        self.udp_sock.sendto(f'{CPRICE}/{code}'.encode(), self.addr)
        raw_data, addr = self.udp_sock.recvfrom(self.BUFSIZ)
        cprice_data = pickle.loads(raw_data)
        logger.info(cprice_data)
        return cprice_data

    def inquire_order(self) -> list:
        self.udp_sock.sendto(IORDER.encode(), self.addr)
        raw_data, addr = self.udp_sock.recvfrom(self.BUFSIZ)
        order_list = pickle.loads(raw_data)
        logger.info(order_list)
        return order_list

    def buy_order(self, code: str, amount: int, price: int):
        self.udp_sock.sendto(f'{BUY}/{code}/{amount}/{price}'.encode(), self.addr)
        raw_data, addr = self.udp_sock.recvfrom(self.BUFSIZ)
        result = pickle.loads(raw_data)
        logger.info(result)

    def sell_order(self, code: str, amount: int, price: int):
        self.udp_sock.sendto(f'{SELL}/{code}/{amount}/{price}'.encode(), self.addr)
        raw_data, addr = self.udp_sock.recvfrom(self.BUFSIZ)
        result = pickle.loads(raw_data)
        logger.info(result)

    def cancel_one(self, ordernum: int):
        self.udp_sock.sendto(f'{CANCEL}/{ordernum}'.encode(), self.addr)
        raw_data, addr = self.udp_sock.recvfrom(self.BUFSIZ)
        result = pickle.loads(raw_data)
        logger.info(result)

    def cancel_all(self, code: str):
        self.udp_sock.sendto(f'{CANCEL}/{code}'.encode(), self.addr)
        raw_data, addr = self.udp_sock.recvfrom(self.BUFSIZ)
        result = pickle.loads(raw_data)
        logger.info(result)
