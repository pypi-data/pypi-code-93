from binance import AsyncClient
from binance.client import Client


async def async_check_system_status(client: AsyncClient) -> bool:
    rst = await client.get_system_status()
    return rst['status'] == 0


async def async_check_account_status(client: AsyncClient) -> bool:
    rst = await client.get_account_status()
    return rst['data'] == "Normal"


def check_system_status(client: Client) -> bool:
    rst = client.get_system_status()
    return rst['status'] == 0


def check_account_status(client: Client) -> bool:
    rst = client.get_account_status()
    return rst['data'] == "Normal"


def check_api_trading_status(client: Client) -> bool:
    rst = client.get_account_api_trading_status()
    return rst['data']['isLocked'] is False


def check_can_trade(client: Client) -> bool:
    rst = client.get_account()
    return rst['canTrade'] is True
