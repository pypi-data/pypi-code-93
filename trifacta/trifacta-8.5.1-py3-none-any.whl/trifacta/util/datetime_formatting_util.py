import re
from datetime import datetime
from functools import lru_cache

from trifacta.constants import DATETIME_FORMAT_TOKEN_DICTIONARY, DATETIME_PARSE_TOKEN_DICTIONARY

'''
| ICU token | ICU string output    | strftime token | strftime string output        |
| --------- | -------------------- | -------------- | ----------------------------- |
|           |                      | %%             | %                             |
| MMMM      | January              | %B             | January                       |
| MMM       | Jan                  | %b             | Jan                           |
| MM        | 01                   | %m             | 01                            |
| M         | 1                    | %-m            |                               |

| dd        | 09                   | %d             | 09                            |
| D         | 352                  | %j             | 352                           |
| d         | 9                    | %-d            | 9                             |

| EEEE      | Wednesday (Week)     | %A             | Wednesday (Week)              |
| EEE       | Wed (Week)           | %a             | Wed (Week)                    |

| YYYY      | 2016 (year)          | %Y/%G          | 2016 (year)                   |
| YY        | 16 (year)            | %y             | 16 (year)                     |

| SSS       | 003920 (millisecond) | %f             | 003920 (millisecond)          |
| SS        | 003920 (millisecond) | %f             | 003920 (millisecond)          |
| S         | 003920 (millisecond) | %f             | 003920 (millisecond)          |

| ss        | 03 (second)          | %S             | 03 (second)                   |
| s         | 3 (second)           | %-S            | 3 (second)                    |

| mm        | 09 (minutes)         | %M             | 09                            |
| m         | 9 (minutes)          | %-M            | 9                             |

| HH        | 0-23 (hours)         | %H             | 0-23 (hours)                  |
| H         | 0-11 (hours)         | %I             | 0-11 (hours)                  |

| a         | am/pm                | %p             | AM/PM                         |

| XXX       | ISO 8601 (+ 5.30)    | %z             | +0530                         |
| XX        | ISO 8601 (+ 5.30)    | %z             | +0530                         |
| X         | ISO 8601 (+ 5.30)    | %z             | +0530                         |

| ww        | 09 (week #)          | %W             | 09 (week # with Monday first)  |
| w         | 09 (week #)          |                |                               |
|           |                      | %V             | 09 (week # with Sunday first)  |


|           |                      | %s             | 1614858605 (unix timestamp)   |
|           |                      | %Z             | IST                           |

|           |                      | %x             | 03/04/21 (local date)         |
|           |                      | %X             | 17:20:05 (local time)         |
|           |                      | %v             | 4-Mar-2021                    |
|           |                      | %u/%w          | 0-6 (weekday)                 |
|           |                      | %V             | 09 (01-52 week no)            |
|           |                      | %c             | Thu Mar  4 17:20:05 2021      |
| --------- | -------------------- | -------------- | ----------------------------- |
'''


class DateTimeFormattingUtil(object):
    """
    Utility class for translation datetime formatting string.
    This utility acts in place of ICU library,
    processing ICU format string
    ex- 'yyyy-MM-dd HH:mm:ss' ---> '%Y-%m-%d %H:%M:%S'
    """
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if DateTimeFormattingUtil.__instance is None:
            DateTimeFormattingUtil()
        return DateTimeFormattingUtil.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if DateTimeFormattingUtil.__instance is not None:
            raise Exception("DateTimeFormattingUtil is a singleton!")
        else:
            DateTimeFormattingUtil.__instance = self

    @lru_cache(maxsize=None)
    def translate(self, icu_fstring, mode='format'):
        """
        @param icu_fstring: basestring containing datetime format following ICU based specification
        This is not a exhaustive mapping of ICU tokens, this also does not translate any string
        ICU lib can, as trifacta UI inhibits user to enter a specific set of token and delimiters
        thus format string CDF can be translated easily
        @param mode: string flag used to disable zero padding in case of format string translation
        """
        passive_re = re.compile(r'(\'\S+\')')
        f_str_token_list = passive_re.split(icu_fstring)
        translated_f_str = ''
        for token in f_str_token_list:
            if passive_re.fullmatch(token):
                translated_f_str = ''.join((translated_f_str, token[1:-1]))
            else:
                translated_f_str = ''.join((translated_f_str, self._translate_parse_string(
                    token) if mode == 'parse' else self._translate_format_string(token)))
        return translated_f_str

    @lru_cache(maxsize=None)
    def _translate_format_string(self, icu_fstring):
        str_fstring = icu_fstring
        for key in DATETIME_FORMAT_TOKEN_DICTIONARY:
            str_fstring = str_fstring.replace(key, DATETIME_FORMAT_TOKEN_DICTIONARY[key])
        return str_fstring

    @lru_cache(maxsize=None)
    def _translate_parse_string(self, icu_fstring):
        str_fstring = icu_fstring
        for key in DATETIME_PARSE_TOKEN_DICTIONARY:
            str_fstring = str_fstring.replace(key, DATETIME_PARSE_TOKEN_DICTIONARY[key])
        return str_fstring

    def strptime(self, str, f_str):
        """
        @param str: basestring to parse to datetime,based on given ICU format string
        @return datetime object
        """
        try:
            return datetime.strptime(str, self.translate(f_str, mode='parse'))
        except (ValueError, TypeError):
            raise Exception

    def strftime(self, dt_obj, f_str):
        """
        @param dt_obj: datetime object
        @param f_str: basestring ICU format string
        """
        try:
            f_str = self.translate(f_str, mode='format')
            micro_second = int(dt_obj.microsecond / 1000)
            f_str = f_str.replace('%f', "{0:03}".format(micro_second))
            return dt_obj.strftime(f_str)
        except (ValueError, TypeError):
            raise Exception
