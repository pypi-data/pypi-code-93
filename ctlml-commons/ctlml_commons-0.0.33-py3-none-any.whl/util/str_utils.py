import locale
from uuid import UUID


def camel_to_snake(camel: str) -> str:
    """Convert camel case to snake case.

    Args:
        camel: camel case string

    Returns: snake case string
    """
    return "".join(["_" + i.lower() if i.isupper() else i for i in camel]).lstrip("_")


def num_to_monetary_str(value: float) -> str:
    """Convert a value to a monetary string.

    Args:
        value: numerical value

    Returns: monetary string
    """
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    return locale.currency(value, grouping=True)


def num_to_percentage_str(value: float) -> str:
    """Convert a value to a percentage string.

    Args:
        value: numerical value

    Returns: percentage string
    """
    return "{:.2f}%".format(value * 100)


def uuid_to_str(uuid_value: UUID) -> str:
    """Converts a UUID to a string.

    Args:
        uuid_value: UUID

    Returns: string representation of the UUID
    """
    return str(uuid_value)


def str_to_uuid(value: str) -> UUID:
    """Converts a string to a UUID.

    Args:
        value: string value

    Returns: UUID of the string
    """
    return UUID(value, version=4)
