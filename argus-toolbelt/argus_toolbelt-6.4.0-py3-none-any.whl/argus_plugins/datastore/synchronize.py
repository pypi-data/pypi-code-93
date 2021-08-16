import csv
from urllib.parse import quote_plus

from argus_api.api.datastores.v1.store.store import (
    put_data_store_entries,
    delete_data_store_entries,
    get_entries_from_store,
)

from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_plugins import argus_cli_module
from argus_plugins.cases.utils import get_customer_id


def get_buffered_data(func):
    """

    :param func: The getter function for the data to be buffered
    :return: a generator with the data, the data is the ["data"] parameter of the response.
    """

    def ann(*args, **kwargs):

        buffer_size = 200

        offset = 0
        response = func(*args, limit=buffer_size, offset=offset, **kwargs)
        while offset < response["count"]:

            yield from response["data"]
            offset += buffer_size

            response = func(*args, limit=buffer_size, offset=offset, **kwargs)

    return ann


def set_data_with_buffer(func: callable, buffered_argument: str):
    """
    Decorator to send data in multiple batches.

    Large requests might be eaten by a proxy or the service itself.
    Because of this, we're setting the batch size to 4k. This is half of the
    max size of an URL according to the HTTP RFC, and should be well within a
    safe limit to assure that our request is delivered.

    :param func: the function to buffer
    :param buffered_argument: The kwarg that is going to be split into
                              multiple requests. The key that this is
                              referencing has to be an iterable.
    :return: The decorated function
    """

    def buffered_arguments(args, kwargs):
        buffer = kwargs.pop(buffered_argument)
        buffer_size = len(buffer)

        if any(len(quote_plus(str(item))) > 4000 for item in buffer):
            raise ValueError(
                "One of the arguments to {} is over the 4K "
                "characters. This exceeds the maximum limit and "
                "is not allowed."
            )

        offset = 0
        while offset < buffer_size:
            current_end = offset + 1
            while (
                sum(len(str(s)) for s in buffer[offset : current_end + 1]) < 4000
                and buffer_size >= current_end + 1 > offset
            ):
                current_end += 1

            kwargs[buffered_argument] = buffer[offset:current_end]
            offset = current_end

            yield args, kwargs

    def buffered_function(*args, **kwargs):
        response = None
        for args, kwargs in buffered_arguments(args, kwargs):
            response = func(*args, **kwargs)

        return response

    return buffered_function


def datastore_data(data: str) -> dict:
    """Turns a CSV string into key:value pairs"""
    try:
        with open(data, "r") as fp:
            data = fp.readlines()
    except IOError:
        data = data.split("\n")

    # Remove any comments
    data = filter(
        lambda line: not line.startswith("#") and len(line) and not line.isspace(), data
    )
    csv_reader = csv.reader(data)

    entries = {}
    for row in csv_reader:
        key = row[0].strip()
        value = row[1].strip() if len(row) > 1 else None

        if key in entries:
            log.warn(
                f'The key "{key}" exists multiple times in the data. Overriding with new value'
            )

        entries[key] = value

    return entries


@register_command(extending="datastores", module=argus_cli_module)
def delete(datastore: str, keys: list, customer: get_customer_id = None):
    """Deletes given entries from the datastore.

    :param datastore: The datastore to modify
    :param customer: The customer to affect
    :param keys: Keys to delete. A file can be provided with the @-prefix
                 (eg. @/tmp/datastore_delete.txt).
    """
    buffered_delete = set_data_with_buffer(
        delete_data_store_entries, buffered_argument="key"
    )
    buffered_delete(dataStore=datastore, customerID=customer, key=keys)

    print("Successfully deleted {amount} entries".format(amount=len(keys)))


@register_command(extending="datastores", module=argus_cli_module)
def update(
    datastore: str,
    data: datastore_data,
    customer: get_customer_id = None,
    default_value: str = "N/A",
):
    """Adds or update entries from the data"""
    entries = [
        {"key": key, "value": value or default_value} for key, value in data.items()
    ]
    buffered_put = set_data_with_buffer(
        put_data_store_entries, buffered_argument="entries"
    )
    response = buffered_put(dataStore=datastore, entries=entries, customerID=customer)

    print("Successfully updated {amount} entries".format(amount=response["size"]))


@register_command(extending="datastores", module=argus_cli_module)
def sync(
    datastore: str,
    data: datastore_data,
    customer: get_customer_id = None,
    default_value: str = "N/A",
):
    """Makes sure the datastore is a 1:1 match with the given data (for a given customer, if any)."""
    delete_entries = []  # Items to delete
    update_entries = {}  # Items to update/add
    existing_entries = {}  # Entries that already exist

    fetched_entries = get_buffered_data(get_entries_from_store)(datastore)

    for entry in fetched_entries:
        if customer and entry["customer"]["id"] != customer:
            continue

        key = entry["key"]
        value = entry["value"] or default_value

        existing_entries[key] = value
        if key not in data:
            delete_entries.append(key)

    for key, value in data.items():
        if value != existing_entries.get(key):
            update_entries[key] = value

    if update_entries:
        update(datastore, update_entries, customer)
    if delete_entries:
        delete(datastore, delete_entries, customer)
