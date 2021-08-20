import asyncio
import logging

import pytest
from common.okex.stream import ReconnectingWebSocket
from common.okex.constants import *


@pytest.mark.asyncio
async def test_public_websocket(logger, okex_pub_ws: ReconnectingWebSocket):
    async with okex_pub_ws as ws:
        await ws.sub({
            "channel": "tickers",
            "instId": "BTC-USDT"
        })
        while True:
            msg = await ws.recv()
            logger.info(msg)


@pytest.mark.asyncio
async def test_private_websocket(logger, okex_pri_ws: ReconnectingWebSocket):
    async with okex_pri_ws as ws:
        await ws.sub({
            "channel": "orders",
            "instType": "FUTURES",
            "instId": "BTC-USD-210730"
        })
        while True:
            msg = await ws.recv()
            logger.info(msg)


