from typing import Mapping, Optional, TYPE_CHECKING
from bcrypt import checkpw, hashpw, gensalt
from email_validator import validate_email, EmailNotValidError
from secrets import token_urlsafe
from datetime import datetime

from ._models import UserModel
from ._errors import (
    UserIdError,
    InvalidLogin,
    EmailError,
    PasswordResetInvalid,
    DetailsExistError
)


if TYPE_CHECKING:
    from . import AccountHandler


class User:
    def __init__(self, upper: "AccountHandler", user_id: str) -> None:
        self._upper = upper
        self.user_id = user_id

    @property
    def __and(self) -> dict:
        return {"user_id": self.user_id}

    async def __raw_user(self) -> Optional[Mapping]:
        return await self._upper._db_wrapper.get(
            "user", self.__and
        )

    async def update_password(self, current_password: str,
                              new_password: str) -> None:
        """Used to update the password if they already know
           there current password.

        Parameters
        ----------
        current_password : str
        new_password : str

        Raises
        ------
        InvalidLogin
        PasswordPolicyError
        """

        user = await self.__raw_user()
        if not user:
            raise InvalidLogin()

        if not checkpw(current_password.encode(), user["password"]):
            raise InvalidLogin()

        self._upper._validate_details(password=new_password)

        await self._upper._db_wrapper.update(
            "user", self.__and, {
                "password": hashpw(new_password.encode(), gensalt())
            }
        )

    async def update_name(self, name: str) -> None:
        """Updates users name

        Parameters
        ----------
        name : str

        Raises
        ------
        DetailsExistError
        NameLengthInvalidError
        NameInvalidCharactersError
        """

        self._upper._validate_details(name=name)

        if await self._upper._db_wrapper.exists(
                "user", {"name": name}):
            raise DetailsExistError()

        await self._upper._db_wrapper.update(
            "user", self.__and, {"name": name}
        )

    async def update_email(self, new_email: str) -> None:
        """Used to update a user's email.

        Parameters
        ----------
        new_email : str

        Raises
        ------
        EmailError
        DetailsExistError
        """

        try:
            valid = validate_email(new_email)
        except EmailNotValidError as error:
            raise EmailError(str(error))

        if await self._upper._db_wrapper.exists(
                "user", {"email": valid.email}):
            raise DetailsExistError()

        values = {
            "email": valid.email,
        }

        if self._upper._smtp:
            values = {
                **values,
                **self._upper._email_regenerate()
            }

            await self._upper._jobs.spawn(
                self._upper._smtp._send(
                    values["email"],
                    values["email_vaildate"],
                    "confirm"
                )
            )

        await self._upper._db_wrapper.update(
            "user", self.__and, values
        )

    async def reset_password(self) -> str:
        """Used to reset a password

        Returns
        -------
        str
            The password reset code, if SMTP
            is being used you shouldn't need to touch this.
        """

        user = await self.get()

        values = {
            "password_reset_code": token_urlsafe(32),
            "password_reset_generated": datetime.now()
        }

        await self._upper._db_wrapper.update(
            "user", self.__and, values
        )

        if self._upper._smtp and user.email:
            await self._upper._jobs.spawn(
                self._upper._smtp._send(
                    user.email,
                    values["password_reset_code"],
                    "reset"
                )
            )

        return values["password_reset_code"]

    async def password_confirm(self, new_password: str,
                               given_code: str) -> None:
        """Used to reset password from password reset code.

        Parameters
        ----------
        new_password : str
        given_code : str

        Raises
        ------
        PasswordResetInvalid
        PasswordPolicyError
        """

        result = await self.__raw_user()
        if (not result or "password_reset_code" not in result or
                not result["password_reset_code"]):
            raise PasswordResetInvalid()

        if (datetime.now() - self._upper._password_reset_expires >
                result["password_reset_generated"]):
            raise PasswordResetInvalid()

        # Midigates timing attacks.
        valid = checkpw(
            given_code.encode(), hashpw(
                result["password_reset_code"].encode(),
                gensalt()
            )
        )

        if not valid:
            raise PasswordResetInvalid()

        self._upper._validate_details(password=new_password)

        await self._upper._db_wrapper.update(
            "user", self.__and, {
                "password": hashpw(new_password.encode(), gensalt()),
                "password_reset_code": None,
                "password_reset_generated": None
            }
        )

    async def get(self) -> UserModel:
        """Used to get details on user.

        Returns
        -------
        UserModel

        Raises
        ------
        UserIdError
        """

        result = await self.__raw_user()
        if not result:
            raise UserIdError()

        return UserModel(**result)

    async def delete(self) -> None:
        """Used to delete account, this can't be undone.
        """

        await self._upper._db_wrapper.delete("user", self.__and)
