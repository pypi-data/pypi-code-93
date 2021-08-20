from logging import Logger

import pytest
from common.log import create_logger
from common.huobi.client import AsyncClient
from common.huobi.service import HuobiService
from common.okex.client import AsyncClient as OkexAsyncClient
from common.okex.stream import ReconnectingWebSocket
from binance.client import AsyncClient as BinanceAsyncClient
from .config import Huobi, Okex, Binance


@pytest.fixture(scope="function")
async def hb_client() -> AsyncClient:
    client = AsyncClient.create(Huobi.API_KEY, Huobi.API_SECRET)
    yield client
    await client.close_connection()


@pytest.fixture(scope="session")
def logger() -> Logger:
    return create_logger("pytest")


@pytest.fixture(scope="function")
async def huobi_service(hb_client) -> HuobiService:
    return HuobiService(hb_client)


@pytest.fixture()
async def okex_client() -> OkexAsyncClient:
    client = OkexAsyncClient.create(Okex.API_KEY, Okex.API_SECRET, Okex.API_PASSPHRASE, True)
    yield client
    await client.close_connection()


@pytest.fixture(scope="session")
def proxy() -> str:
    return "http://127.0.0.1:51838"


@pytest.fixture()
async def okex_pub_ws(proxy):
    return ReconnectingWebSocket(
        proxy=proxy,
        api_key=Okex.API_KEY,
        api_secret=Okex.API_SECRET,
        api_passphrase=Okex.API_PASSPHRASE,
        simulated=True
    )


@pytest.fixture()
async def okex_pri_ws(proxy):
    return ReconnectingWebSocket(
        public=False,
        proxy=proxy,
        api_key=Okex.API_KEY,
        api_secret=Okex.API_SECRET,
        api_passphrase=Okex.API_PASSPHRASE,
        simulated=True
    )


@pytest.fixture()
async def binance_client() -> BinanceAsyncClient:
    client = BinanceAsyncClient.create(Binance.API_KEY, Binance.API_SECRET)
    yield client
    await client.close_connection()
