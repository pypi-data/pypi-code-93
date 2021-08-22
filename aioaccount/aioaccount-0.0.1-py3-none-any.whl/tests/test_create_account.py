from .base import TestBase
from .. import (
    PasswordPolicyError,
    AccountDetailsError,
    EmailError,
    NameLengthInvalidError,
    NameInvalidCharactersError,
    _MAX_NAME_LEN,
    UserModel,
    User,
    DetailsExistError
)


class TestCreateAccount(TestBase):
    use_sql = False
    use_smtp = False

    valid_password = "#!K2&33?e%@Pv3_Q"

    async def test_password_policy_invalid(self) -> None:
        with self.assertRaises(PasswordPolicyError):
            await self.handler.create_account(
                password="1234hh$",
                name="ward"
            )

    async def test_no_email_or_name(self) -> None:
        with self.assertRaises(AccountDetailsError):
            await self.handler.create_account(
                self.valid_password
            )

    async def test_invalid_email(self) -> None:
        with self.assertRaises(EmailError):
            await self.handler.create_account(
                password=self.valid_password,
                email="something@.com"
            )

    async def test_invalid_names(self) -> None:
        with self.assertRaises(NameLengthInvalidError):
            await self.handler.create_account(
                password=self.valid_password,
                name="wa"
            )

        with self.assertRaises(NameLengthInvalidError):
            await self.handler.create_account(
                password=self.valid_password,
                name="x" * (_MAX_NAME_LEN + 1)
            )

        with self.assertRaises(NameInvalidCharactersError):
            await self.handler.create_account(
                password=self.valid_password,
                name="war$"
            )

    async def test_valid_account_only_email(self) -> None:
        model, user = await self.handler.create_account(
            password=self.valid_password,
            email="example@example.com"
        )

        self.assertIsInstance(model, UserModel)
        self.assertIsInstance(user, User)

    async def test_valid_account_only_name(self) -> None:
        model, user = await self.handler.create_account(
            password=self.valid_password,
            name="ward"
        )

        self.assertIsInstance(model, UserModel)
        self.assertIsInstance(user, User)

    async def test_valid_account_both(self) -> None:
        model, user = await self.handler.create_account(
            password=self.valid_password,
            name="notward",
            email="wardpearce@pm.me"
        )

        self.assertIsInstance(model, UserModel)
        self.assertIsInstance(user, User)

    async def test_account_name_taken(self) -> None:
        model, _ = await self.handler.create_account(
            password=self.valid_password,
            name="oopwe"
        )

        with self.assertRaises(DetailsExistError):
            await self.handler.create_account(
                password=self.valid_password,
                name=model.name
            )

    async def test_account_email_taken(self) -> None:
        model, _ = await self.handler.create_account(
            password=self.valid_password,
            email="oopwe@example.com"
        )

        with self.assertRaises(DetailsExistError):
            await self.handler.create_account(
                password=self.valid_password,
                email=model.email
            )


class TestCreateAccountSqlSmtp(TestCreateAccount):
    use_sql = True
    use_smtp = True
