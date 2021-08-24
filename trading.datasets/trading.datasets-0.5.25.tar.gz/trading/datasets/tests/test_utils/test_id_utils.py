"""Tests for trading.datasets.utils.id_utils."""
# pylint: disable=missing-class-docstring,missing-function-docstring

from trading.datasets.utils import id_utils


class TestIDUtils:

    def test_reproducable_ids(self):
        assert str(id_utils.generate_uuid('t')) == 'e358efa4-89f5-8062-f10d-d7316b65649e'
        assert str(id_utils.generate_uuid('t')) == 'e358efa4-89f5-8062-f10d-d7316b65649e'
        assert str(id_utils.generate_uuid('BTC/USDT-Binance')) == 'e05925d4-286c-161f-8ad6-8a36901adc20'
