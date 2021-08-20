import pytest
from common.huobi.client import AsyncClient
from common.models import Result


def asset_ok(resp: Result):
    return resp.status == 'ok'


@pytest.mark.asyncio
async def test_kline(hb_client: AsyncClient, logger):
    resp: Result = await hb_client.spot_kline("btcusdt", hb_client.KLINE_INTERVAL_1MINUTE)
    assert asset_ok(resp)


@pytest.mark.asyncio
async def test_account_balance(hb_client: AsyncClient, logger):
    resp: Result = await hb_client.spot_account_info()
    assert asset_ok(resp)
    for item in resp.data:
        balance_info = await hb_client.spot_account_balance(item['id'])
        logger.info(balance_info.data)


@pytest.mark.asyncio
async def test_asset_valuation(hb_client: AsyncClient, logger):
    resp = await hb_client.spot_asset_valuation(hb_client.SPOT, "USD")
    logger.info(resp.data)

