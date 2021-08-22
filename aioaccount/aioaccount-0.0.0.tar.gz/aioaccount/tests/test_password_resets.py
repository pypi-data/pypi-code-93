from .base import TestBase
from .. import PasswordResetInvalid


class TestPasswordResets(TestBase):
    use_sql = True
    use_smtp = True

    valid_password = "S]Q}67=uLetG{r,_8{"

    async def test_password_confirm_invalid_code(self) -> None:
        _, user = await self.handler.create_account(
            password=self.valid_password,
            name="oewup"
        )

        self.assertIsInstance(await user.reset_password(), str)

        with self.assertRaises(PasswordResetInvalid):
            await user.password_confirm(
                new_password=self.valid_password,
                given_code="ddd"
            )

    async def test_password_no_reset(self) -> None:
        _, user = await self.handler.create_account(
            password=self.valid_password,
            name="hhd"
        )

        with self.assertRaises(PasswordResetInvalid):
            await user.password_confirm(
                new_password=self.valid_password,
                given_code="ddd"
            )

    async def test_invalid_user(self) -> None:
        with self.assertRaises(PasswordResetInvalid):
            await self.handler.user("123").password_confirm(
                new_password=self.valid_password,
                given_code="ddd"
            )

    async def test_valid_code(self) -> None:
        _, user = await self.handler.create_account(
            password=self.valid_password,
            name="xxz"
        )

        code = await user.reset_password()

        await user.password_confirm(
            new_password=self.valid_password,
            given_code=code
        )


class TestPasswordResetsMongo(TestPasswordResets):
    use_sql = False
    use_smtp = False
