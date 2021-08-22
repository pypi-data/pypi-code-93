from .base import TestBase
from .. import InvalidLogin, PasswordPolicyError


class TestUpdatePassword(TestBase):
    use_sql = False
    use_smtp = False

    old_password = "#!K2&33?e%@Pv3_Q"
    new_password = "ZRvTP72g-VwX3@\\H"

    async def test_invalid_user(self) -> None:
        with self.assertRaises(InvalidLogin):
            await (self.handler.user("123")).update_password(
                current_password=self.old_password,
                new_password=self.new_password
            )

    async def test_valid_user_invalid_old_pass(self) -> None:
        _, user = await self.handler.create_account(
            password=self.old_password,
            name="deezemail"
        )

        with self.assertRaises(InvalidLogin):
            await user.update_password(
                current_password="1234",
                new_password=self.new_password
            )

    async def test_valid_user_invalid_new_pass(self) -> None:
        _, user = await self.handler.create_account(
            password=self.old_password,
            name="eeezz"
        )

        with self.assertRaises(PasswordPolicyError):
            await user.update_password(
                current_password=self.old_password,
                new_password="123"
            )

    async def test_valid_user(self) -> None:
        model, user = await self.handler.create_account(
            password=self.old_password,
            name="ppez"
        )

        await user.update_password(
            current_password=self.old_password,
            new_password=self.new_password
        )

        await self.handler.login(
            password=self.new_password,
            name=model.name
        )


class TestUpdatePasswordSqlSmtp(TestUpdatePassword):
    use_sql = True
    use_smtp = True
