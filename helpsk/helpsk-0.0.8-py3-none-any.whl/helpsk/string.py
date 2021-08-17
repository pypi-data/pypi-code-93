"""
Contains a collection of helper functions to manipulate strings.
"""
from enum import unique, Enum, auto
from typing import List, Union


def collapse(*args: Union[str, List[str]], separate: str = '', surround: str = '') -> str:
    """Takes a list of strings and concatenates them, separating each string with the value of `separate` and
    surrounding each string with the value of `surround`.

    Keyword arguments:
    *args -- list of strings to concatenate
    separate -- string used to separate each string (default '')
    surround -- string used to surround each string (default '')
    """
    if len(args) == 1 and isinstance(args[0], list):
        args = args[0]

    return separate.join([surround + x + surround for x in args])


@unique
class RoundTo(Enum):
    """
    Valid values for rounding numbers; used in e.g. `format_number()`
    """
    NONE = auto()
    THOUSANDS = 'K'
    MILLIONS = 'M'
    BILLIONS = 'B'
    TRILLIONS = 'T'
    AUTO = auto()


def format_number(value: float,
                  granularity: RoundTo = RoundTo.AUTO,
                  places: int = 2) -> str:
    """
    Formats numbers in a way that humans would typically want to see at a glance (e.g. on a graph.)

    For example, `123560000` is transformed to `123.56M'

    Parameters
    ----------
    value : the number (float) to format

    granularity : the granularity (e.g. thousands, millions, billions). (default is
        RoundTo.AUTO)

        `RoundTo.NONE` will not change the granularity, but will still add commas if necessary.

        `RoundTo.AUTO` will reduce the granularity (or not) depending on the number passed in.

    places: the number of digits to the right of the decimal to display. (default is `2`)

        For example:
            `format_number(123567000, granularity=RoundTo.MILLIONS, num_digits=2)` -> '123.57M'
            `format_number(123567000, granularity=RoundTo.MILLIONS, num_digits=3)` -> '123.567M'

    Returns
    -------
    the formatted number as a string
    """
    granularity_lookup = {RoundTo.THOUSANDS: 1000,
                          RoundTo.MILLIONS:  1000000,
                          RoundTo.BILLIONS:  1000000000,
                          RoundTo.TRILLIONS: 1000000000000}

    if granularity == RoundTo.NONE:
        granularity = ''
    elif granularity == RoundTo.AUTO:

        if abs(value) >= granularity_lookup[RoundTo.TRILLIONS]:
            value = value / granularity_lookup[RoundTo.TRILLIONS]
            granularity = RoundTo.TRILLIONS.value

        elif abs(value) >= granularity_lookup[RoundTo.BILLIONS]:
            value = value / granularity_lookup[RoundTo.BILLIONS]
            granularity = RoundTo.BILLIONS.value

        elif abs(value) >= granularity_lookup[RoundTo.MILLIONS]:
            value = value / granularity_lookup[RoundTo.MILLIONS]
            granularity = RoundTo.MILLIONS.value

        elif abs(value) >= granularity_lookup[RoundTo.THOUSANDS]:
            value = value / granularity_lookup[RoundTo.THOUSANDS]
            granularity = RoundTo.THOUSANDS.value

        elif abs(value) >= 1:
            granularity = ''
        else:
            # else we have a number that is less than one, so we will override places
            granularity = ''

            places = 1
            while abs(value) < pow(10, places * -1):
                places += 1

            places += 2
    else:
        value = value / granularity_lookup[granularity]
        granularity = granularity.value

    assert isinstance(granularity, str)

    # return '{{:,.{0}f}}'.format(places).format(value) + granularity
    return f'{value:,.{places}f}' + granularity
