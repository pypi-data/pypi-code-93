from .base import TestBase
from typing import cast
from .. import UnableToConfirmEmail, User


class TestEmailConfirm(TestBase):
    use_sql = True
    use_smtp = True

    valid_password = "#!K2&33?e%@Pv3_Q"

    async def test_invalid_code(self) -> None:
        model, _ = await self.handler.create_account(
            password=self.valid_password,
            email="jamisbae@pm.me"
        )

        with self.assertRaises(UnableToConfirmEmail):
            await self.handler.confirm_email(
                email=cast(str, model.email),
                given_code="competelymadeup"
            )

    async def test_invalid_email(self) -> None:
        with self.assertRaises(UnableToConfirmEmail):
            await self.handler.confirm_email(
                email="googleisnsasimp@gmail.com",
                given_code="competelymadeup"
            )

    async def test_valid_confirm(self) -> None:
        model, _ = await self.handler.create_account(
            password=self.valid_password,
            email="lokiismorebae@gmail.com"
        )

        result = await self.handler._db_wrapper.get(
            "user", {"user_id": model.user_id}
        )
        if not result:
            raise Exception("this shouldn't happen")

        user = await self.handler.confirm_email(
            email=cast(str, model.email),
            given_code=result["email_vaildate"]
        )

        self.assertIsInstance(user, User)

        model = await user.get()
        self.assertTrue(model.email_confirmed)


class TestEmailConfirmMongo(TestEmailConfirm):
    use_sql = False
    use_smtp = True
