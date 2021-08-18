import copy
import time
from aredis import StrictRedis, StrictRedisCluster, ClusterConnectionPool, ConnectionPool, client
import asyncio


async def example_client():
    pool = ConnectionPool(host='127.0.0.1', port=6379, password='admin', db=0)
    client = StrictRedis(connection_pool=pool)
    await client.set('5555', 1)
    await client.delete('5555')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example_client())
