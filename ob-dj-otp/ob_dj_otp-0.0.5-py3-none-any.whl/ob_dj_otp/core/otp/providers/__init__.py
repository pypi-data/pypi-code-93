import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from ob_dj_otp.core.otp.providers.twilio import TwilioProviderWrapper


class SMSProvider:
    def __init__(self):
        if getattr(settings, "OTP_PROVIDER", None) == "twilio":
            self.provider = TwilioProviderWrapper()

        # If not provider set; raise ImproperlyConfigured
        if not getattr(self, "provider", None):
            raise ImproperlyConfigured("OTP_PROVIDER is required")

    def send_message(
        self, phone_number: typing.Text, verification_code: typing.Text
    ) -> typing.NoReturn:
        self.provider.send_message(
            phone_number=phone_number, verification_code=verification_code
        )
