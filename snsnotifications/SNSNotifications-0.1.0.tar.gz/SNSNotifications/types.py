from typing import Union, List, Set, Callable

__all__ = ['NotificationChannel', 'Notification']


class Notification:
    via: Union[List, Set, Callable[[], List[str]]] = []


class NotificationChannel:

    def send(self, notification: Notification):
        raise NotImplementedError()

    def channel_identify(self) -> str:
        raise NotImplementedError()

    def can_send(self, notification: Notification) -> bool:
        convert_fn_name = "to_{}".format(self.channel_identify())
        if not hasattr(notification, convert_fn_name):
            return False
        convert_fn = getattr(notification, convert_fn_name)
        return callable(convert_fn)
