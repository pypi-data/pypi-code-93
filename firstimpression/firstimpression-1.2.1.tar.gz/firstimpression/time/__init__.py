import datetime
import time
import locale
from firstimpression.xml import get_text_from_element
from firstimpression.constants import ENGLISH_INDEX, DUTCH_INDEX


def change_language(language_index):
    if language_index == ENGLISH_INDEX:
        language = 'en_US'
        try:
            locale.setlocale(locale.LC_TIME, language)
        except locale.Error:
            language = 'English_America'
            locale.setlocale(locale.LC_TIME, language)
    elif language_index == DUTCH_INDEX:
        language = 'nl_NL'
        try:
            locale.setlocale(locale.LC_TIME, language)
        except locale.Error:
            language = 'Dutch_Netherlands'
            locale.setlocale(locale.LC_TIME, language)

def get_datetime_object_from_element(element, name, format):
    """ Gets the datetime object of an element (xml) based on name and format

    :param element: the element from which the date needs to be grabbed
    :type element: xml.etree.ElementTree.Element

    :param name: name of the element in xml which contains date
    :type name: str

    :param format: the format of the datetime in the element
    :type format: str

    :returns: time and date in the right format
    :rtype: date
     """
    unparsed_pubdate = get_text_from_element(element, name)

    created_at = parse_string_to_time(element, format)
    return parse_timestamp_to_date(created_at)


def parse_string_to_time(element, format):
    """ Gets the timestamp of an string in specific format

    :param element: string with the time in it
    :type element: str

    :param format: string with the format devined
    :type format: str

    :returns: time as timestamp
    :rtype: float """
    return parse_date_to_time(parse_string_to_date(element, format))


def parse_date_to_time(date_object):
    return time.mktime(date_object.timetuple())


def parse_string_to_date(element, format):
    return datetime.datetime.strptime(element, format)


def parse_timestamp_to_date(timestamp):
    """ Change timestamp to date object

    :param timestamp: the time in POSIX timestamp
    :type timestamp: float

    :returns: the time as a date
    :rtype: date """
    return datetime.datetime.fromtimestamp(timestamp)


def parse_date_to_string(date_object, format):
    return datetime.datetime.strftime(date_object, format)


def parse_string_time_to_minutes(element):
    [hours, minutes, seconds] = element.split(':')

    minutes = int(minutes)

    if int(seconds) > 30:
        minutes += 1

    minutes += int(hours) * 60

    return minutes

def parse_string_to_string(element, format, new_format):
    if element != '':
        return parse_date_to_string(parse_string_to_date(element, format), new_format)
    else:
        return ''
