# Dramatiq tasks

import dramatiq

from django.conf import settings
from django.contrib.auth import get_user_model

from sparkpost import SparkPost, US_API


User = get_user_model()




sp_api_key = None
sp_base_uri = None
client = None

if hasattr(settings, 'SPARKPOST_API_KEY') and hasattr(settings, 'SPARKPOST_BASE_URI'):
    if settings.SPARKPOST_API_KEY and settings.SPARKPOST_BASE_URI:
        sp_api_key = getattr(settings, 'SPARKPOST_API_KEY', None)
        sp_base_uri = getattr(settings, 'SPARKPOST_BASE_URI', US_API)
        client = SparkPost(sp_api_key, sp_base_uri)




@dramatiq.actor(max_retries=0)
def async_send_message(message, fail_silently=False):
    """
    A Dramatiq actor that sends an email asynchronously.

    message - A SparkPost message instance which is a subclass of dict.
    """
    success = 0
    logger = async_send_message.logger
    try:
        logger.info('Sending email via SparkPost async backend')
        params = getattr(settings, 'SPARKPOST_OPTIONS', {}).copy()
        params.update(message)
        response = client.transmissions.send(**params)
        success += response['total_accepted_recipients']
        logger.info('Email sent via SparkPost async backend')
    except Exception:
        if not fail_silently:
            msg = (
                'An error occured while trying to send an email via the '
                'SparkPost async backend'
            )
            logger.error(msg)
