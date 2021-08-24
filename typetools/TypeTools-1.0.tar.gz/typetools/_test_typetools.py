import typetools

import unittest


class Stock:
    market = typetools.MaxSized(size=5)
    shares = typetools.Integer()

    def __init__(self, market, shares):
        self.market = market
        self.shares = shares


class TestTypetools(unittest.TestCase):
    def setUp(self):
        self.stock = Stock("ABC", 13)

    def _change_market_to(self, market):
        self.stock.market = market

    def _change_shares_to(self, shares):
        self.stock.shares = shares

    def test_MaxSized(self):
        self.assertRaises(ValueError,
                          lambda: self._change_market_to("AAAAAAAAAA"))

    def test_Integer(self):
        self.assertRaises(TypeError,
                          lambda: self._change_shares_to("blah"))


if __name__ == "__main__":
    unittest.main()
