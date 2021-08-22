from .base import TestBase
from .. import AccountDetailsError, User, UserModel


class TestToUser(TestBase):
    use_sql = False
    use_smtp = False

    valid_password = "#!K2&33?e%@Pv3_Q"

    async def test_no_email_or_name(self) -> None:
        with self.assertRaises(AccountDetailsError):
            await self.handler.to_user()

    async def test_no_result(self) -> None:
        with self.assertRaises(AccountDetailsError):
            await self.handler.to_user(
                email="thisisn'treal"
            )

    async def test_valid_to_user_from_name(self) -> None:
        c_model, _ = await self.handler.create_account(
            password=self.valid_password,
            name="epicgamer1"
        )

        model, user = await self.handler.to_user(
            name=c_model.name
        )

        self.assertIsInstance(
            model,
            UserModel
        )

        self.assertIsInstance(
            user,
            User
        )

    async def test_valid_to_user_from_email(self) -> None:
        c_model, _ = await self.handler.create_account(
            password=self.valid_password,
            email="epicgamer@gmail.com"
        )

        model, user = await self.handler.to_user(
            email=c_model.email
        )

        self.assertIsInstance(
            model,
            UserModel
        )

        self.assertIsInstance(
            user,
            User
        )


class TestToUserSqlSmtp(TestToUser):
    use_sql = True
    use_smtp = True
