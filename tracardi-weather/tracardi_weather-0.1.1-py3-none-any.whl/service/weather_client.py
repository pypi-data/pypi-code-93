import python_weather
from python_weather.response import Weather
from tracardi.service.singleton import Singleton


class AsyncWeatherClient(metaclass=Singleton):

    METRIC = "C"
    IMPERIAL = "F"

    def __init__(self, type=None):
        print('i')
        if type is None:
            type = self.METRIC
        self.client = python_weather.Client(format=type)

    async def fetch(self, city) -> Weather:
        return await self.client.find(city)

    async def close(self):
        await self.client.close()

    async def __aenter__(self):
        print('en')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print('ex')
        await self.client.close()
