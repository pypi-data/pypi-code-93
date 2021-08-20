# coding: utf8
# contract_gen 2020-05-19 11:24:17.150908

__all__ = ["BidAskMid"]

from ..instrument._definition import ObjectDefinition


class BidAskMid(ObjectDefinition):
    def __init__(self, bid=None, ask=None, mid=None):
        super().__init__()
        self.bid = bid
        self.ask = ask
        self.mid = mid

    @property
    def ask(self):
        """
        :return: float
        """
        return self._get_parameter("ask")

    @ask.setter
    def ask(self, value):
        self._set_parameter("ask", value)

    @property
    def bid(self):
        """
        :return: float
        """
        return self._get_parameter("bid")

    @bid.setter
    def bid(self, value):
        self._set_parameter("bid", value)

    @property
    def mid(self):
        """
        :return: float
        """
        return self._get_parameter("mid")

    @mid.setter
    def mid(self, value):
        self._set_parameter("mid", value)
