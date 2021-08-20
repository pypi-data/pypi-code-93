import asyncio

from tracardi_weather.service.weather_client import AsyncWeatherClient


async def main():
    async with AsyncWeatherClient() as a:
        s = await a.fetch("Wrocław")
        print(s.current)


asyncio.run(main())
