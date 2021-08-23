from django.dispatch import Signal

notification_received = Signal(providing_args=['name', 'data'])
