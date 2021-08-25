from django.conf import settings
from django.db import models


def collate(field_name, collation=None):
    """
    Enforces collation specified by the given paramater, or the
    setting `IEVV_DB_POSTGRES_COLLATION`. Wrapping `django.db.models.Func`-class
    and generates a function expression with collation.

    Note::
        Returns the field name if collation is not defined in settings,
        which results in the default Django order_by behaviour.

    Args:
        field_name (str): The field name.
        collation (str): The collation to use. 'E.g en_US.UTF-8'
    """

    # Get collation from settings.
    if not collation:
        collation = getattr(settings, 'IEVV_DB_POSTGRES_COLLATION', None)

    # If collation is not defined in settings, return the field name.
    # This will result in the default wayt to do order_by (...order_by('<field_name>'))
    if not collation:
        return field_name

    # Determine if descending order should be used.
    # Setting desc_order to True if thats the case.
    desc_order = False
    if field_name.startswith('-'):
        field_name = field_name.split('-')[1]
        desc_order = True

    collate_function = models.Func(
        field_name,
        function=collation,
        template='(%(expressions)s) COLLATE "%(function)s"'
    )

    if desc_order:
        return collate_function.desc()
    return collate_function.asc()
