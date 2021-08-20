import pytest
from common.okex.client import AsyncClient
from common.okex.constants import *


@pytest.mark.asyncio
async def test_account_balance(okex_client: AsyncClient, logger):
    resp = await okex_client.account_balance("BTC")
    logger.info(resp)


@pytest.mark.asyncio
async def test_account_position(okex_client: AsyncClient, logger):
    resp = await okex_client.positions(instId="BTC-USD-SWAP")
    logger.info(resp)


@pytest.mark.asyncio
async def test_create_order(okex_client: AsyncClient, logger):
    resp = await okex_client.create_order(
        "BTC-USDT",
        TradeMode.CASH,
        Side.BUY,
        OrderType.MARKET,
        sz=str(100)
    )
    logger.info(resp)
