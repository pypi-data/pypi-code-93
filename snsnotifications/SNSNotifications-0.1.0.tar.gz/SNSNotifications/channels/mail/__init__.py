from SNSNotifications.types import NotificationChannel, Notification
from .mailable import Mailable
from .transport_manager import TransportManager

__all__ = ['Mailer', 'Mailable']


class Mailer(NotificationChannel):

    def __init__(self, driver: str, **kwargs):
        self.transport = getattr(TransportManager(), 'create_{}_driver'.format(driver))(**kwargs)

    def send(self, notification: Notification):
        if not self.can_send(notification):
            return
        mail = getattr(notification, "to_{}".format(self.channel_identify()))()
        self.transport.send(mail)

    def channel_identify(self) -> str:
        return "mail"
