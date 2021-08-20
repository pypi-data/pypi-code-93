from common.huobi.wallet import Wallet
from common.log import create_logger
from .config import Huobi

wallet = Wallet(Huobi.API_KEY, Huobi.API_SECRET)
logger = create_logger("pytest")


def test_spot_balance():
    for item in wallet.get_spot_balance().values():
        item.print_object()


################
# 币本位
################
def test_coin_margined_swap_balance_valuation():
    resp = wallet.get_coin_margined_swap_balance_valuation("USD")
    logger.info(resp)


def test_coin_margined_swap_account_info():
    print(wallet.get_coin_margined_swap_account_info())


def test_coin_margined_swap_position_info():
    print(wallet.get_coin_margined_swap_position())


################
# 交割合约
################
def test_get_contract_account_info():
    print(wallet.get_contract_account_info())


def test_get_contract_position_info():
    print(wallet.get_contract_position_info())
