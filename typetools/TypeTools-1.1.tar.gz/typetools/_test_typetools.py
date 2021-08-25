import typetools

import unittest


class Stock:
    market = typetools.MaxSizedIterable(size=5)
    shares = typetools.Integer()
    price = typetools.MaxSizedInteger(size=100)
    people_buying = typetools.MinSizedInteger(size=0)

    def __init__(self, market, shares, price, people_buying):
        self.market = market
        self.shares = shares
        self.price = price
        self.people_buying = people_buying


class TestTypetools(unittest.TestCase):
    def setUp(self):
        self.stock = Stock("ABC", 13, 56, 14)

    def _change_market_to(self, market):
        self.stock.market = market

    def _change_shares_to(self, shares):
        self.stock.shares = shares

    def _change_price_to(self, price):
        self.stock.price = price

    def _change_people_buying_to(self, people_buying):
        self.stock.people_buying = people_buying

    def test_MaxSizedIterable(self):
        self.assertRaises(ValueError,
                          lambda: self._change_market_to("AAAAAAAAAA"))

    def test_Integer(self):
        self.assertRaises(TypeError,
                          lambda: self._change_shares_to("blah"))

    def test_MaxSizedInteger(self):
        self.assertRaises(ValueError,
                          lambda: self._change_price_to(128))
        self.assertRaises(TypeError,
                          lambda: self._change_price_to(["blah"]))

    def test_MinSizedInteger(self):
        self.assertRaises(ValueError,
                          lambda: self._change_people_buying_to(-1000))
        self.assertRaises(TypeError,
                          lambda: self._change_people_buying_to([1, 2, 3]))


if __name__ == "__main__":
    unittest.main()
