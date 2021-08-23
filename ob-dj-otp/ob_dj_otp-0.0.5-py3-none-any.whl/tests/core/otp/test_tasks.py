import mock
import pytest
from twilio.base.version import Version

from ob_dj_otp.core.otp.tasks import send_sms_via_provider
from tests.core.otp.factories import OneTruePairingFactory


@pytest.mark.django_db(transaction=True)
@mock.patch.object(Version, "create")
def test_celery_send_sms_via_twilio(mck_twilio_create, celery_worker):
    instance = OneTruePairingFactory()
    task = send_sms_via_provider.apply_async(args=[instance.id]).get(timeout=3)
    assert task == "Success"
    mck_twilio_create.assert_called_once_with(
        method="POST",
        uri="/Services/None/Verifications",
        data={"To": "", "Channel": "sms", "CustomCode": "11111"},
    )
