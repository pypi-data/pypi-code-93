from typing import TypeVar, List

from pydantic import HttpUrl

from monox import MonoXClient, HttpxClient, MonoXMethod, GetCurrency, Currency

T = TypeVar("T")


class MonoX:
    def __init__(self,
                 token: str = "",
                 endpoint: HttpUrl = "https://api.monobank.ua"):
        self.client: MonoXClient = HttpxClient(
            base_url=endpoint,
            headers={
                "X-Token": token
            }
        )

    async def __call__(self, method: MonoXMethod) -> T:
        response = await self.client.make_request(method.build_request())
        return method.build_model(response)

    async def currency(self) -> List[Currency]:
        return await self(GetCurrency())

    async def close(self):
        await self.client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
