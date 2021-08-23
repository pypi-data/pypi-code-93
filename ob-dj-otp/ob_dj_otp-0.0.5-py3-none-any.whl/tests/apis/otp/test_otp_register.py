from datetime import timedelta
from functools import partial

import pytest
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status

from ob_dj_otp.core.otp.models import OneTruePairing


@pytest.mark.django_db
def test_opt_auth_register(client):
    """Test requesting OTP Code for Registration
    POST /{version}/otp/
    """
    # Request OTP Verification code for non-existing user
    phone_number = "+96599005094"
    client_post = partial(
        client.post, reverse("otp:otp-list"), data={"phone_number": phone_number}
    )
    response = client_post()
    assert response.status_code == status.HTTP_201_CREATED, response.content
    # Test only `phone_number` and `status` returned in the response
    assert ["phone_number", "status", "usage"] == list(response.json().keys())
    assert response.json()["usage"] == OneTruePairing.Usages.register
    instance = OneTruePairing.objects.get(phone_number=phone_number)
    assert not instance.user
    assert instance.usage == instance.Usages.register
    assert instance.status == instance.Statuses.init
    assert instance.verification_code
    # Test throttling by phone number
    instance.created_at = now() - timedelta(minutes=1)
    instance.save()
    response = client_post()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    assert (
        "We sent a verification code please wait for 2 minutes"
        in response.content.__str__()
    )
