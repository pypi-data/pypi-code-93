from django.core.mail.backends.base import BaseEmailBackend

from sparkpost.django.message import SparkPostMessage

from .tasks import async_send_message


class AsyncSparkPostEmailBackend(BaseEmailBackend):
    """
    Async SparkPost wrapper for Django BaseEmailBackend.
    """

    def send_messages(self, email_messages):
        """
        Send emails, returns integer representing number of successful emails.

        email_messages - A Python list of Django EmailMessage objects.
        """
        success = 0
        for message in email_messages:
            try:
                # Don't get confused with the use of send() here.
                # send() creates a new async task using Dramatiq.
                # This is the equivalent of Celery's delay()
                async_send_message.send(
                    # SparkPostMessage (dict) is JSON serializable
                    SparkPostMessage(message),
                    self.fail_silently,
                )
                # Number of recipients to send to.
                # message.to is always a list in Django's EmailMessage
                # Assume success:
                # If we don't assume success it might break some people's
                # code where they depend on checking for success using this.
                # However, this method will never return an accurate success
                # number and therefore assuming success is safer.
                success += len(message.to)
            except Exception:
                if not self.fail_silently:
                    raise
        return success
