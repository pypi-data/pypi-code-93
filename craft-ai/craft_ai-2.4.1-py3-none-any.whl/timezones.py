import re

_TIMEZONE_REGEX = re.compile(r"^([+-](2[0-3]|[01][0-9])(:?[0-5][0-9])?|Z)$")

TIMEZONES = {
    "UTC": "+00:00",
    "GMT": "+00:00",
    "BST": "+01:00",
    "IST": "+01:00",
    "WET": "+00:00",
    "WEST": "+01:00",
    "CET": "+01:00",
    "CEST": "+02:00",
    "EET": "+02:00",
    "EEST": "+03:00",
    "MSK": "+03:00",
    "MSD": "+04:00",
    "AST": "-04:00",
    "ADT": "-03:00",
    "EST": "-05:00",
    "EDT": "-04:00",
    "CST": "-06:00",
    "CDT": "-05:00",
    "MST": "-07:00",
    "MDT": "-06:00",
    "PST": "-08:00",
    "PDT": "-07:00",
    "HST": "-10:00",
    "AKST": "-09:00",
    "AKDT": "-08:00",
    "AEST": "+10:00",
    "AEDT": "+11:00",
    "ACST": "+09:30",
    "ACDT": "+10:30",
    "AWST": "+08:00",
}


def is_timezone(value):
    # Valid time zone range is -12:00 (-720 min) and +14:00 (+840 min)
    # cf. https://en.wikipedia.org/wiki/List_of_UTC_time_offsets
    if isinstance(value, int) and value <= 840 and value >= -720:
        return True
    if not isinstance(value, str):
        return False
    if value in TIMEZONES:
        return True
    result_reg_exp = _TIMEZONE_REGEX.match(value) is not None
    return result_reg_exp


def get_timezone_key(configuration):
    for key in configuration:
        if configuration[key]["type"] == "timezone":
            return key
    return None


def timezone_offset_in_sec(timezone):
    if isinstance(timezone, int):
        # If the offset belongs to [-15, 15] it is considered to represent hours.
        # This reproduces Moment's utcOffset behaviour.
        if timezone > -16 and timezone < 16:
            return timezone * 60 * 60
        return timezone * 60
    if timezone in TIMEZONES:
        timezone = TIMEZONES[timezone]
    if len(timezone) > 3:
        timezone = timezone.replace(":", "")
        offset = (int(timezone[-4:-2]) * 60 + int(timezone[-2:])) * 60
    else:
        offset = (int(timezone[-2:]) * 60) * 60

    if timezone[0] == "-":
        offset = -offset

    return offset


def timezone_offset_in_standard_format(timezone):
    if isinstance(timezone, int):
        sign = "+" if timezone >= 0 else "-"
        absolute_offset = abs(timezone)
        if absolute_offset < 16:
            return "%s%02d:00" % (sign, absolute_offset)
        return "%s%02d:%02d" % (
            sign,
            int(absolute_offset / 60),
            int(absolute_offset % 60),
        )
    return timezone
