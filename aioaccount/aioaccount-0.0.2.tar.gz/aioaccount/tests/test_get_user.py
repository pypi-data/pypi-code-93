from .base import TestBase
from .. import UserModel, UserIdError


class TestGetUser(TestBase):
    use_sql = True

    valid_password = "#!K2&33?e%@Pv3_Q"

    async def test_invalid_id(self) -> None:
        with self.assertRaises(UserIdError):
            await self.handler.user("123").get()

    async def test_valid_get(self) -> None:
        _, user = await self.handler.create_account(
            password=self.valid_password,
            name="hhg"
        )

        self.assertIsInstance(
            await user.get(),
            UserModel
        )


class TestGetUserMongo(TestGetUser):
    use_sql = False
