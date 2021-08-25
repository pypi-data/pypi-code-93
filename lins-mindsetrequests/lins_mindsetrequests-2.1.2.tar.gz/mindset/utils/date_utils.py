from pytz import timezone
from datetime import datetime


def make_aware(date):
    return datetime(
        date.year,
        date.month,
        date.day,
        date.hour,
        date.minute,
        date.second,
        tzinfo=timezone('America/Sao_Paulo'),
    )
