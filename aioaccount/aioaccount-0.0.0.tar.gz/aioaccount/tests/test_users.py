from .base import TestBase
from .. import UserModel, User


class TestUsers(TestBase):
    use_sql = True

    valid_password = "#!K2&33?e%@Pv3_Q"

    async def test_users_listing(self) -> None:
        await self.handler.create_account(
            password=self.valid_password,
            name="jjd"
        )

        async for model, user in self.handler.users():
            self.assertIsInstance(model, UserModel)
            self.assertIsInstance(user, User)


class TestUsersMongo(TestUsers):
    use_sql = False
