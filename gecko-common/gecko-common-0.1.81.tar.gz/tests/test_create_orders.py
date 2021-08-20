import timeit
import os
import asyncio

import aiohttp.helpers

from binance.client import Client, AsyncClient

loop = 3

API_KEY = os.environ.get("binance_quant_api_key")
API_SECRET = os.environ.get("binance_quant_api_secret")

symbol = "BUSDUSDT"


async def async_create_order():
    client = await AsyncClient.create(API_KEY, API_SECRET)

    async def task():
        resp = await client.order_limit_buy(symbol=symbol, price="0.95", quantity=11)
        await client.cancel_order(symbol=symbol, orderId=resp['orderId'])

    start = timeit.default_timer()
    await asyncio.gather(*[task() for _ in range(loop)])
    end = timeit.default_timer()
    await client.close_connection()
    print(f"异步版本: {end - start}")


def create_order():
    client = Client(API_KEY, API_SECRET)
    start = timeit.default_timer()

    for _ in range(loop):
        resp = client.order_limit_buy(symbol=symbol, price="0.95", quantity=11)
        client.cancel_order(symbol=symbol, orderId=resp['orderId'])
    end = timeit.default_timer()
    print(f"同步版本: {end-start}")


if __name__ == '__main__':
    # create_order()
    asyncio.run(async_create_order())
