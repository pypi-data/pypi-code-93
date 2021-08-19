from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, Tuple, Type, TypeVar, Union

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt as jwt_lib
from passlib.context import CryptContext
from tortoise.models import Model

from .exceptions import HTTPUnAuthorizedError

password_context: CryptContext = CryptContext(schemes=["bcrypt"])
UserModel = TypeVar("UserModel", bound=Model)


def jwt(
    token_url: str,
    secret: str,
    model: Type[UserModel],
    field: str = "email",
    expire_after_seconds: int = 3600 * 24 * 30,
    algorithm: str = "HS256",
) -> Tuple[
    Callable[..., Union[Coroutine[Any, Any, UserModel], UserModel]],
    Callable[[str], str],
]:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)

    async def get_current_user(
        token: str = Depends(oauth2_scheme),
    ) -> UserModel:
        payload = jwt_lib.decode(token, secret, algorithms=[algorithm])
        username: str = payload.get("sub", "")
        if not username:
            raise HTTPUnAuthorizedError
        user = await model.filter(**{field: username}).first()
        if user is None:
            raise HTTPUnAuthorizedError
        exp = float(payload.get("exp", 0))
        assert exp > datetime.now().timestamp()
        return user

    def authorize(username: str) -> str:
        exp = datetime.now() + timedelta(seconds=expire_after_seconds)
        token = jwt_lib.encode(
            {"sub": username, "exp": int(exp.timestamp())},
            secret,
            algorithm=algorithm,
        )
        return token

    return get_current_user, authorize
