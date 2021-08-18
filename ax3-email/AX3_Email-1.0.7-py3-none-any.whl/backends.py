from django.core.mail.backends.base import BaseEmailBackend

from .utils import _serialize_email_message
from .tasks import _async_send_messages


class AX3EmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        # Turn emails into something serializable
        if not email_messages:
            return None

        emails = [_serialize_email_message(email) for email in email_messages]

        return _async_send_messages(emails)
