import datetime
import math

from craft_ai.errors import CraftAiError
from craft_ai.operators import OPERATORS
from craft_ai.types import TYPES, TYPE_ANY

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def _time_formatter(time):
    if isinstance(time, datetime.datetime):
        if time.second == 0:
            return time.strftime("%H:%M")
        return time.strftime("%H:%M:%S")
    else:
        hours = int(math.floor(time))
        dec_minutes = (time - hours) * 60
        minutes = int(math.floor(dec_minutes))
        seconds = int(math.floor((dec_minutes - minutes) * 60))

        if seconds > 0:
            return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
        return "{:02d}:{:02d}".format(hours, minutes)


PROPERTY_FORMATTER = {
    TYPE_ANY: lambda value: value,
    TYPES["continuous"]: lambda number: "{:.2f}".format(number).rstrip("0").rstrip("."),
    TYPES["time_of_day"]: _time_formatter,
    TYPES["day_of_week"]: lambda day: DAYS[day.weekday()]
    if isinstance(day, datetime.datetime)
    else DAYS[day],
    TYPES["day_of_month"]: lambda day: day.day
    if isinstance(day, datetime.datetime)
    else day,
    # Months are in [1; 12] thus -1 to be index month name in [0; 11]
    TYPES["month_of_year"]: lambda month: MONTHS[month.month - 1]
    if isinstance(month, datetime.datetime)
    else MONTHS[month - 1],
}


def format_property(property_type, value=None):
    formatter = (
        PROPERTY_FORMATTER[property_type]
        if property_type in PROPERTY_FORMATTER
        else PROPERTY_FORMATTER[TYPE_ANY]
    )

    def extended_formatter(value):
        if value is None:
            return "null"
        if value == {}:
            return "N/A"
        return formatter(value)

    if value is not None:
        return extended_formatter(value)

    return extended_formatter


def _is_formatter(property_name, operand, operand_formatter):
    if property_name:
        return "'{}' is {}".format(property_name, operand_formatter(operand))
    return "is {}".format(operand_formatter(operand))


def _in_formatter(property_name, operand, operand_formatter):
    if property_name:
        return "'{}' in [{}, {}[".format(
            property_name, operand_formatter(operand[0]), operand_formatter(operand[1])
        )
    return "[{}, {}[".format(
        operand_formatter(operand[0]), operand_formatter(operand[1])
    )


def _in_day_of_week_formatter(property_name, operand, operand_formatter):
    day_from = int(math.floor(operand[0]))
    day_to = int(math.floor(operand[1]))

    formatted_day_from = operand_formatter(day_from)

    if (day_to - day_from == 1) or (day_from == 6 and day_to == 0):
        # One day in the interval
        if property_name:
            return "'{}' is {}".format(property_name, formatted_day_from)
        return formatted_day_from

    formatted_day_to = operand_formatter((7 + day_to - 1) % 7)

    if property_name:
        return "'{}' from {} to {}".format(
            property_name, formatted_day_from, formatted_day_to
        )
    return "{} to {}".format(formatted_day_from, formatted_day_to)


def _in_month_of_year_formatter(property_name, operand, operand_formatter):
    month_from = int(math.floor(operand[0]))
    month_to = int(math.floor(operand[1]))

    formatted_month_from = operand_formatter(month_from)

    if (month_to - month_from == 1) or (month_from == 12 and month_to == 1):
        # One month in the interval
        if property_name:
            return "'{}' is {}".format(property_name, formatted_month_from)
        return formatted_month_from

    formatted_month_to = operand_formatter((12 + month_to - 1) % 12)

    if property_name:
        return "'{}' from {} to {}".format(
            property_name, formatted_month_from, formatted_month_to
        )

    return "{} to {}".format(formatted_month_from, formatted_month_to)


def _gte_formatter(property_name, operand, operand_formatter):
    if property_name:
        return "'{}' >= {}".format(property_name, operand_formatter(operand))
    return ">= {}".format(operand_formatter(operand))


def _lt_formatter(property_name, operand, operand_formatter):
    if property_name:
        return "'{}' < {}".format(property_name, operand_formatter(operand))
    return "< {}".format(operand_formatter(operand))


FORMATTER_FROM_DECISION_RULE = {
    OPERATORS["IS"]: {TYPE_ANY: _is_formatter},
    OPERATORS["IN_INTERVAL"]: {
        TYPE_ANY: _in_formatter,
        TYPES["day_of_week"]: _in_day_of_week_formatter,
        TYPES["day_of_month"]: _in_formatter,
        TYPES["month_of_year"]: _in_month_of_year_formatter,
    },
    OPERATORS["GTE"]: {TYPE_ANY: _gte_formatter},
    OPERATORS["LT"]: {TYPE_ANY: _lt_formatter},
}


def _format_decision_rule(rule):
    if rule["operator"] not in FORMATTER_FROM_DECISION_RULE:
        raise CraftAiError(
            "Unable to format the given decision rule: unknown operator '{}'.".format(
                rule["operator"]
            )
        )
    operator_formatters = FORMATTER_FROM_DECISION_RULE[rule["operator"]]

    operand_type = rule["type"] if "type" in rule else TYPE_ANY

    formatter = (
        operator_formatters[operand_type]
        if operand_type in operator_formatters
        else operator_formatters[TYPE_ANY]
    )
    operand_formatter = format_property(operand_type)

    if "property" in rule:
        return formatter(rule["property"], rule["operand"], operand_formatter)

    return formatter(None, rule["operand"], operand_formatter)


def format_decision_rules(rules):
    return " and ".join([_format_decision_rule(rule) for rule in rules])
