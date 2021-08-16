import logging
import datetime
import json
from bson import json_util


class DatetimeEncoder(json.JSONEncoder):
    """Custom class to help overcome datetime objects not being JSON serializable"""

    def default(self, obj):
        try:
            return super(DatetimeEncoder, obj).default(obj)
        except TypeError:
            return str(obj)


def update_big_ints(obj, int_bit_lim=32):
    """
    MongoDB cannot handle integers bigger than 8 bytes (or 64 bits). This function recursively searches through a nested
      dictionary and converts integers larger than 32 bits to str. Also works for nested dictionaries that contain lists
      of further (nested) dictionaries.
    :param obj: A dictionary object.
    :type obj: dict
    :param int_bit_lim: Maximum number of bits to allow integers to be.
    :type int_bit_lim: int
    :return: Same dictionary with integers > ``int_bit_lim`` bits are converted to str.
    :rtype: dict
    """
    if hasattr(obj, 'items'):
        for k, v in obj.items():
            if isinstance(v, dict):
                obj[k] = update_big_ints(v)
            elif isinstance(v, int):
                if v.bit_length() > int_bit_lim:
                    obj[k] = str(v)
            elif isinstance(v, list):
                [update_big_ints(element) for element in v]
    return obj


def safe_encode_document(document):
    """Various Python object types throw errors when inserting into MongoDB"""
    json_str = json.dumps(document, cls=DatetimeEncoder)
    new_document = json.loads(json_str, object_hook=json_util.object_hook)
    return new_document


def format_dates(result):
    """Format strings as dates - so we can query datetime fields during the analysis"""
    date_format = '%Y-%m-%d %H:%M:%S %Z'
    try:
        result['search_metadata']['created_at'] = datetime.datetime.strptime(
            result['search_metadata']['created_at'],
            date_format
        )
    except KeyError:
        logging.warning('search_metadata.created_at does not exist')

    try:
        result['search_metadata']['processed_at'] = datetime.datetime.strptime(
            result['search_metadata']['processed_at'],
            date_format
        )
    except KeyError as ke:
        logging.warning('search_metadata.processed_at does not exist')

    return result


def str_to_datetime(datetime_str, date_format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(datetime_str, date_format)


def valid_date_range(d1, d2, date_format='%Y-%m-%d %H:%M:%S'):
    """
    Formats and validates a datetime range in string format. If the start date is unspecified i.e. ``None`` then it will
      be set to the end date minus 24 hours. If the end date isn't specified then it defaults to the current date. This
      behaviour is intended to be read as "all documents from this date". If both are unspecified, then the default is
      the last 24 hours.
    :param d1: Start/from date.
    :type d1: str
    :param d2: To/end date.
    :type d2: str
    :param date_format: Strptime format to use for parsing the input strings.
    :type date_format: str
    :return: Start and to date in datetime format.
    :rtype: datetime.datetime
    """

    # Coerce datetime strings to datetime objects
    d1 = str_to_datetime(d1, date_format) if d1 is not None else d1
    d2 = str_to_datetime(d2, date_format) if d2 is not None else d2

    if d1 is None and d2 is None:
        # Set to last 24 hours
        d2 = datetime.datetime.now()
        d1 = d2 - datetime.timedelta(days=1)
    elif d1 is None and d2 is not None:
        # Set d1 to d2 minus 1 day
        d1 = d2 - datetime.timedelta(days=1)
    elif d1 is not None and d2 is None:
        # Set d2 to today
        d2 = datetime.datetime.now()
    else:
        # Validate date range
        assert d1 <= d2, 'start date cannot be after the end date'

    return d1, d2


def main():
    pass


if __name__ == '__main_':
    main()
