import re
from dateutil.parser import parse as date_parser

def find_date(s):
    _STRICT_DATE_REGEX_PREFIX = r'(?<=\W)'
    DATE_REGEX = r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?'
    STRICT_DATE_REGEX = _STRICT_DATE_REGEX_PREFIX + DATE_REGEX
    date_match = re.search(STRICT_DATE_REGEX, s)
    rtn = None
    if date_match:
        date_str = date_match.group(0)
        try:
            rtn = date_parser(date_str)
        except (ValueError, OverflowError, AttributeError, TypeError):
            # near all parse failures are due to URL dates without a day
            # specifier, e.g. /2014/04/
            rtn = None
    return rtn