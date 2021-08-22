from .base import TestBase
from .. import AccountDetailsError, InvalidLogin


class TestLogin(TestBase):
    use_sql = False
    use_smtp = False

    valid_password = "S]Q}67=uLetG{r,_8{"

    async def test_no_name_or_email(self) -> None:
        with self.assertRaises(AccountDetailsError):
            await self.handler.login(password="12341")

    async def test_invalid_email(self) -> None:
        with self.assertRaises(InvalidLogin):
            await self.handler.login(password="12341", email="doens'texist")

    async def test_invalid_name(self) -> None:
        with self.assertRaises(InvalidLogin):
            await self.handler.login(
                password="12341",
                name="notarealname1231234"
            )

    async def test_valid_password_invalid_name(self) -> None:
        await self.handler.create_account(
            password=self.valid_password,
            name="somethingrllyc00l"
        )

        with self.assertRaises(InvalidLogin):
            await self.handler.login(
                password=self.valid_password,
                name="somethingrllyc"
            )

    async def test_valid_password_invalid_email(self) -> None:
        await self.handler.create_account(
            password=self.valid_password,
            email="somethingrllyc00l@pm.me"
        )

        with self.assertRaises(InvalidLogin):
            await self.handler.login(
                password=self.valid_password,
                email="somethingrllyc@pm.me"
            )

    async def test_valid_email_not_confirmed_with_smtp(self) -> None:
        if self.use_smtp:
            model, _ = await self.handler.create_account(
                password=self.valid_password,
                email="newemail@gamil.com"
            )

            with self.assertRaises(InvalidLogin):
                await self.handler.login(
                    email=model.email,
                    password=self.valid_password
                )

    async def test_valid_email_not_confirmed_without_smtp(self) -> None:
        if not self.use_smtp:
            model, _ = await self.handler.create_account(
                password=self.valid_password,
                email="newemail59@gamil.com"
            )

            await self.handler.login(
                email=model.email,
                password=self.valid_password
            )

    async def test_valid_name_invalid_password(self) -> None:
        model, _ = await self.handler.create_account(
            password=self.valid_password,
            name="wogamer420"
        )

        with self.assertRaises(InvalidLogin):
            await self.handler.login(
                password="1234",
                name=model.name
            )

    async def test_valid_email_invalid_password(self) -> None:
        model, _ = await self.handler.create_account(
            password=self.valid_password,
            email="somecreate@example.com"
        )

        with self.assertRaises(InvalidLogin):
            await self.handler.login(
                password="1234",
                email=model.email
            )

    async def test_valid_with_name(self) -> None:
        model, _ = await self.handler.create_account(
            password=self.valid_password,
            name="wogamer"
        )

        await self.handler.login(
            password=self.valid_password,
            name=model.name
        )

    async def test_valid_email_with_smtp(self) -> None:
        if self.use_smtp:
            model, _ = await self.handler.create_account(
                password=self.valid_password,
                email="wpearce6@gmail.com"
            )

            await self.handler._db_wrapper.update(
                "user", {"user_id": model.user_id},
                {"email_confirmed": True}
            )

            await self.handler.login(
                email=model.email,
                password=self.valid_password
            )


class TestLoginSqlSmtp(TestLogin):
    use_sql = True
    use_smtp = True
