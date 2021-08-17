import asyncio
import time

import aiohttp


class StressTester:
    def __init__(self, url: str = 'http://127.0.0.1/', port: str = '88', num_connections: int = 100, duration: int = 60):
        """Initializes a stresstesters with a host_url and num_connections for the test

        Args:
            url (str, optional): host URL. Defaults to 'http://url:port/'. url=127.0.0.1.
            port (str, optional): host port. Defaults to 'http://url:port/'. port=88.
            num_connections (int, optional): number of concurrent connections. Defaults to 100.
            duration (int, optional): duration of tests
        """
        self.url = f'http://{url}:{port}/'
        self.num_connections = num_connections
        self.duration = duration

    def run_test(self, endpoint: str, params: dict, request_type: str = 'GET'):
        """run a test for executing an enpoint with parameters and a certain request type

        Args:
            endpoint (str): endpoint
            params (dict): a parmeter dictionary
            request_type (str, optional): GET/POST request type. Defaults to 'GET'.
        """
        self.endpoint_url = self.url + endpoint
        self.params = params
        self.request_type = request_type

        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.main())

    async def main(self):
        """Set async connections """
        results = await asyncio.gather(
            *[self.run_benchmark() for _ in range(self.num_connections)]
        )
        print("Queries per second:", sum(results))

    async def fetch_page(self, session: aiohttp.ClientSession) -> dict:
        """[summary]

        Args:
            session ([ClientSession]): [description]

        Returns:
            dict: N.A.
        """
        if self.request_type == 'GET':
            async with session.get(self.endpoint_url, params=self.params) as response:
                assert response.status == 200
                return await response.read()
        else:
            async with session.post(self.endpoint_url, json=self.params) as response:
                assert response.status == 200
                return await response.read()

    async def run_benchmark(self) -> float:
        """run the async page fetching

        Returns:
            float:  queries per second.
        """
        start = time.time()
        count = 0
        async with aiohttp.ClientSession(loop=self.loop) as session:
            # Run test for one minute.
            while time.time() - start < self.duration:
                count += 1
                await self.fetch_page(session)
            return count / (time.time() - start)  # Compute queries per second.
