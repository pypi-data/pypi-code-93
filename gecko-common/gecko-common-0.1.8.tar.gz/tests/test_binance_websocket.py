import pytest
from binance.streams import BinanceSocketManager, AsyncClient, ReconnectingWebsocket
from binance.enums import FuturesType


@pytest.mark.asyncio
async def test_public_websocket(logger, proxy):
    client = AsyncClient()
    bm = BinanceSocketManager(client, proxy=proxy)

    ws: ReconnectingWebsocket = bm.index_price_socket("btcusd", True)
    await ws.__aenter__()
    # await ws.unsubscribe(["btcusdt@indexPrice@1s"])
    await ws.subscribe(["btcusd_210924@depth5", "btcusd_211231@depth5"])
    while True:
        res = await ws.recv()
        logger.info(res)

    async with bm.future_depth_socket("BTCUSD_210924", '5', FuturesType.COIN_M) as stream:
        while True:
            res = await stream.recv()
            logger.info(res)


@pytest.mark.asyncio
async def test_user_websocket(logger, proxy, binance_client: AsyncClient):
    bm = BinanceSocketManager(binance_client, proxy=proxy)
    socket = bm.user_socket()
    async with socket as stream:
        while True:
            res = await stream.recv()
            logger.info(res)


@pytest.mark.asyncio
async def test_coin_future_websocket(logger, proxy, binance_client: AsyncClient):
    bm = BinanceSocketManager(binance_client, proxy=proxy)
    socket = bm.coin_futures_socket()
    async with socket as stream:
        while True:
            res = await stream.recv()
            logger.info(res)
