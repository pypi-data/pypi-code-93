from datetime import timedelta

import jwt
import pytest
from django.utils import timezone

from .models import JwtAppModel, JwtTokenModel


@pytest.mark.django_db
def test_gen_jwt_token():
    JwtAppModel.objects.filter(app_name="t1").delete()
    app = JwtAppModel.objects.create(app_name="t1", jwt_iss="demo", app_key="hello")

    token = JwtTokenModel.objects.create(
        jwt_app=app,
        jwt_sub="user",
        jwt_aud="test",
        jwt_exp=timezone.now() + timedelta(days=10),
    )

    data = jwt.decode(
        token.jwt_token, app.app_key, algorithms=app.app_type, audience=["test"]
    )

    assert data["sub"] == "user"
    assert data["aud"] == "test"
    assert data["iss"] == "demo"
