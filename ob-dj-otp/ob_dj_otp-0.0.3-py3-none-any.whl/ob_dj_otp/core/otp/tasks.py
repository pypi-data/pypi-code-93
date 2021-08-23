from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from ob_dj_otp.core.otp.models import OneTruePairing


@shared_task(
    name="otp.send_sms_via_provider",
    autoretry_for=(ObjectDoesNotExist,),
    default_retry_delay=5,
    bind=True,
)
def send_sms_via_provider(self, otp_id) -> None:
    """" Sends SMS async via Provider
    """
    otp = OneTruePairing.objects.get(id=otp_id)
    otp.send_sms()
    return "Success"
