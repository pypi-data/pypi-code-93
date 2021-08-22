from .base import TestBase
from .. import UserIdError


class TestDeleteAccount(TestBase):
    use_sql = True

    valid_password = "#!K2&33?e%@Pv3_Q"

    async def test_delete_account(self) -> None:
        _, user = await self.handler.create_account(
            password=self.valid_password,
            name="deleteme"
        )

        await user.delete()

        with self.assertRaises(UserIdError):
            await user.get()


class TestDeleteAccountMongo(TestDeleteAccount):
    use_sql = False
