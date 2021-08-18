import logging
from smtplib import SMTPException, SMTPServerDisconnected

from huey.contrib.djhuey import task

from .utils import _deserialize_email_message, _serialize_email_message
from .settings import RETRIES, DELAY


logger = logging.getLogger('huey.consumer')


@task()
def _async_send_messages(serializable_email_messages, retries=RETRIES):
    count = 0

    for email in serializable_email_messages:
        message = _deserialize_email_message(email)
        try:
            sent = message.send()
            if sent is not None:
                count += 1
                logger.info('Email sent to %s', message.to)
        except (SMTPException, SMTPServerDisconnected) as exc:
            if retries > 0:
                _async_send_messages.schedule(kwargs={
                    'serializable_email_messages': [_serialize_email_message(message)],
                    'retries': retries - 1,
                }, delay=DELAY)
            else:
                logger.info('Unable to send email to %s. Response: %s', message.to, exc)
