from datetime import timedelta

import factory
import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

from ob_dj_otp.core.otp.utils import validate_verification_code
from tests.core.otp.factories import OneTruePairingFactory


@pytest.mark.django_db
def test_validate_verification_code():
    assert not validate_verification_code(
        phone_number=factory.Faker("phone_number").generate({}),
        verification_code=factory.Faker("random_digit").generate({}),
    )
    with pytest.raises(ObjectDoesNotExist):
        validate_verification_code(
            phone_number=factory.Faker("phone_number").generate({}),
            verification_code=factory.Faker("random_digit").generate({}),
            raise_exception=True,
        )
    instance = OneTruePairingFactory(register=True)
    assert validate_verification_code(
        phone_number=instance.phone_number, verification_code=instance.verification_code
    )
    assert validate_verification_code(
        phone_number=instance.phone_number,
        verification_code=instance.verification_code,
        raise_exception=True,
    )
    # Test expired token
    instance.created_at = now() - timedelta(minutes=10)
    instance.save()
    assert not validate_verification_code(
        phone_number=instance.phone_number, verification_code=instance.verification_code
    )
