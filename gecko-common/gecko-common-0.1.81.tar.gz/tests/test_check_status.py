from common.binance.check import *
from .config import Binance


client = Client(Binance.API_KEY, Binance.API_SECRET)


def test_check_system_status():
    assert check_system_status(client) is True


def test_check_account_status():
    assert check_account_status(client) is True


def test_check_api_trading_status():
    assert check_api_trading_status(client) is True


def test_check_wallet_can_trade():
    assert check_can_trade(client) is True



