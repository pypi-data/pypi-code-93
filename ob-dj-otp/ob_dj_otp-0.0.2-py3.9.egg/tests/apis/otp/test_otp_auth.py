from datetime import timedelta
from functools import partial

import mock
import pytest
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status

from ob_dj_otp.core.otp.models import OneTruePairing


@pytest.mark.django_db
@mock.patch("celery.current_app.send_task")
def test_opt_auth_create(mck_task, client, user):
    """Test requesting OTP Code for Authentication
    POST /{version}/otp/
    """
    # Request OTP Verification code for existing user
    client_post = partial(
        client.post,
        reverse("otp:otp-list"),
        data={"phone_number": user.phone_number.__str__()},
    )
    response = client_post()
    assert response.status_code == status.HTTP_201_CREATED, response.content
    # Test only `phone_number` and `status` returned in the response
    assert ["phone_number", "status", "usage"] == list(response.json().keys())
    assert response.json()["usage"] == OneTruePairing.Usages.auth
    instance = OneTruePairing.objects.get(phone_number=user.phone_number)
    assert instance.user == user
    assert instance.usage == instance.Usages.auth
    assert instance.status == instance.Statuses.init
    assert instance.verification_code
    # Request a code while one is active
    response = client_post()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "We sent a verification code please wait for 2 minutes; "
        "before requesting a new code." in response.json().__str__()
    )
    # Request OTP access and refresh token for verification code
    response = client_post(
        data={
            "phone_number": user.phone_number.__str__(),
            "verification_code": instance.verification_code,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED, response.content
    # Test only `access_token` and `refresh_token` returned in the response
    assert ["refresh", "access"] == list(response.json().keys())
    # Validate Creating another OneTimePairing when one already exists
    response = client_post(
        data={
            "phone_number": user.phone_number.__str__(),
            "verification_code": instance.verification_code,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    # Test throttling by phone number
    instance.status = OneTruePairing.Statuses.init
    instance.created_at = now() - timedelta(minutes=1)
    instance.save()
    response = client_post()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    assert (
        "We sent a verification code please wait for 2 minutes"
        in response.content.__str__()
    )
