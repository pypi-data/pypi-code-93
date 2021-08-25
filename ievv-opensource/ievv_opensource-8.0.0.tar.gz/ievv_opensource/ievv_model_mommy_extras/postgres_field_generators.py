from datetime import timedelta

from model_bakery.timezone import now
from psycopg2.extras import DateTimeTZRange, DateRange


def generate_datetime_range():
    return DateTimeTZRange(
        lower=now() - timedelta(hours=1),
        upper=now() + timedelta(hours=1)
    )


def generate_date_range():
    return DateRange(
        lower=now().date(),
        upper=(now() + timedelta(days=1)).date()
    )


def add_to_model_bakery():
    from model_bakery import baker
    baker.generators.add(
        'django.contrib.postgres.fields.ranges.DateTimeRangeField',
        generate_datetime_range)
    baker.generators.add(
        'django.contrib.postgres.fields.ranges.DateRangeField',
        generate_date_range)
