import pytest

from tests.core.otp.factories import OneTruePairingFactory


@pytest.mark.django_db
def test_one_true_pairing_factory():
    instance = OneTruePairingFactory()
    assert instance.id
    assert instance.verification_code
    assert instance.created_at
    assert instance.updated_at
