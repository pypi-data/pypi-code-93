import asyncio
import grpc
import injective.exchange_api as ea


async def main() -> None:
    async with grpc.aio.insecure_channel("localhost:9910") as channel:
        ea
