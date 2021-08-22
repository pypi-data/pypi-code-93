from .base import TestBase
from .. import EmailError, DetailsExistError
from typing import cast


class TestUpdateEmail(TestBase):
    use_sql = True
    use_smtp = True

    valid_password = "#!K2&33?e%@Pv3_Q"

    async def test_invalid_email(self) -> None:
        _, user = await self.handler.create_account(
            password=self.valid_password,
            name="lloop"
        )

        with self.assertRaises(EmailError):
            await user.update_email("kkd@@pm.me")

    async def test_details_not_exist(self) -> None:
        model, user = await self.handler.create_account(
            password=self.valid_password,
            email="iio@pm.me"
        )

        with self.assertRaises(DetailsExistError):
            await user.update_email(
                new_email=cast(str, model.email)
            )

    async def test_valid_update_email(self) -> None:
        _, user = await self.handler.create_account(
            password=self.valid_password,
            email="llw3@pm.me"
        )

        await user.update_email(new_email="h3h3@pm.me")

        result = await self.handler._db_wrapper.get(
            "user",
            {"user_id": user.user_id}
        )
        if not result:
            raise Exception("Shouldn't happen")

        self.assertFalse(result["email_confirmed"])
        self.assertIsInstance(result["email_vaildate"], str)


class TestUpdateEmailMongo(TestUpdateEmail):
    use_sql = False
    use_smtp = True
