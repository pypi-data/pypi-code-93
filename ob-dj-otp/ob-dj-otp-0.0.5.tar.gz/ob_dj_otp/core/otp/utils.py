import typing
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

from ob_dj_otp.core.otp.models import OneTruePairing


def validate_verification_code(
    phone_number: typing.Text,
    verification_code: typing.Text,
    usage: typing.Text = None,
    raise_exception: bool = False,
):
    usage = usage or OneTruePairing.Usages.register
    try:
        otp_expiry = now() - timedelta(minutes=getattr(settings, "OTP_EXPIRY", 5))
        OneTruePairing.objects.get(
            phone_number=phone_number,
            verification_code=verification_code,
            status=OneTruePairing.Statuses.init,
            usage=usage,
            created_at__gte=otp_expiry,
        )
        return True
    except ObjectDoesNotExist:
        if raise_exception:
            raise
        return False
