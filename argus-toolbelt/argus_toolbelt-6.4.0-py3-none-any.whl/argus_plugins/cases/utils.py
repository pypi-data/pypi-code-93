"""This is a helper module for all things case related"""

from typing import Union

from argus_api.api.customers.v1.customer import get_customer

#: Valid Argus case statuses
STATUSES = [
    "pendingCustomer",
    "pendingSoc",
    "pendingVendor",
    "workingSoc",
    "workingCustomer",
    "pendingClose",
    "closed",
]
#: Valid Argus case types
CASE_TYPES = ["securityIncident", "operationalIncident", "informational", "change"]
#: Valid Argus case priorities
PRIORITIES = ["low", "medium", "high", "critical"]
KEYWORD_FIELDS = ["subject", "description", "comments", "id", "all"]


def customer_from_shortname(name: str) -> dict:
    customer = get_customer(idOrShortname=name.lower())["data"]
    return customer


def get_customer_id(name: str) -> int:
    """Gets a customer's ID from their name

    :param name: The name of the customer
    """
    return customer_from_shortname(name)["id"]


def format_tags_list(tags: Union[list, dict]):
    """Converts a set of tags to the format expected by the API.

    Allows for a more lax format: where the API expects a list looking likeL

    ``[{"key": key, "value": value}, {"key": key, "value": value}]``

    This will allow:

    - ``[{key: value}, {"key": key, "value": value}]``
    - {key: value, key: value}

    :param tags: a list of tags in the "lax" format
    :return: a list of tags in the "strict" (API) format
    :raises ValueError: if the input is invalid
    """
    if isinstance(tags, dict):
        length = len(tags)
        if (length == 2 and all(k in ("key", "value") for k in tags)) or length == 1:
            # we have either one short-form tag, or one long-form tag
            return [format_tag(tags)]
        # otherwise we have a set of short-form tags as a JSON object
        return [format_tag({k: v}) for k, v in tags.items()]

    elif isinstance(tags, list):
        return [format_tag(tag) for tag in tags]

    raise ValueError("Expecting a list or dictionary")


def format_tag(tag: dict):
    """Ensures that a case tag is properly fornmatted.

    The API expects tags in the following format:

    {"key": key, "value": value}

    This utility allows using the short {"key": value} form by converting it to the
    format expected by the API. If the tag already has that format, it is not changed.

    Will raise a ValueError if the tag is in an unexpected format.

    :param tag: The tag in either the {"key": value} or the {"key": key, "value": value} form
    :return: The tag in the {"key": key, "value": value} form
    :raises ValueError: if the input is invalid
    """
    if len(tag) == 1:
        key = next(iter(tag))
        value = tag[key]
        return {"key": key, "value": value}
    elif len(tag) == 2 and "key" in tag and "value" in tag:
        return tag
    else:
        raise ValueError(
            "Invalid tag format, expected"
            ' either {key: value} or {"key": key, "value": value}'
        )
