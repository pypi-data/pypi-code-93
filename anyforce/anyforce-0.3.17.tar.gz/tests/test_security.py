import time

import pytest
from faker import Faker
from fastapi import HTTPException
from jose import ExpiredSignatureError

from anyforce.api import exceptions, security

from .model import User


@pytest.mark.asyncio
async def test_jwt(database: bool, faker: Faker):
    assert database
    email = faker.email()
    password = faker.pystr()
    await User.create(
        email=email,
        hashed_password=security.password_context.hash(password),
    )
    get_current_user, authorize = security.jwt(
        "", faker.name(), User, expire_after_seconds=1
    )

    try:
        await get_current_user(authorize(""))
        assert False
    except HTTPException as e:
        assert e is exceptions.HTTPUnAuthorizedError

    try:
        await get_current_user(authorize(faker.email()))
        assert False
    except HTTPException as e:
        assert e is exceptions.HTTPUnAuthorizedError

    token = authorize(email)
    authed_user = await get_current_user(token)
    assert authed_user.email == email

    time.sleep(2)
    try:
        await get_current_user(token)
        assert False
    except ExpiredSignatureError:
        pass
