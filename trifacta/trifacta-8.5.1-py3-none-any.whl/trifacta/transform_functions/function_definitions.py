import random
from datetime import datetime, timedelta
from functools import lru_cache
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd
import regex
from dateutil.relativedelta import relativedelta
from pytz import timezone
from dateutil.relativedelta import relativedelta
from metaphone import doublemetaphone
from pytz import timezone

from trifacta.transform_functions.quote_matcher import QuoteMatcher
from trifacta.util.datetime_formatting_util import DateTimeFormattingUtil

""" 
This file contains definition for custom transform functions.
"""


# -------------------- TYPE-CAST FUNCTIONS ----------------------


def to_boolean(val):
    str_cast_map = {
        'false': False,
        'f': False,
        '0': False,
        'off': False,
        'no': False,
        'n': False,
        'true': True,
        't': True,
        '1': True,
        'on': True,
        'yes': True,
        'y': True
    }
    if pd.isnull(val):
        return np.nan
    elif isinstance(val, bool):
        return bool(val)
    elif isinstance(val, int):
        return str_cast_map.get(str(val).strip().lower(), np.nan)
    elif isinstance(val, str):
        return str_cast_map.get(val.strip().lower(), np.nan)
    return np.nan


def to_double(val):
    if pd.isnull(val):
        return np.nan
    elif isinstance(val, float):
        return float(val)
    elif isinstance(val, np.double):
        return float(val)
    elif isinstance(val, int):
        return float(val)
    elif isinstance(val, np.int64):
        return float(val)
    elif isinstance(val, bool):
        return float(1.0) if val else float(0.0)
    elif isinstance(val, str):
        try:
            d = float(val)
            if d == float('inf') or d == float('nan'):
                return np.nan
            elif abs(d) < np.finfo('d').min:
                return 0.0
            return d
        except Exception as e:
            return np.nan
    return np.nan


def to_integer(val):
    if pd.isnull(val):
        return np.nan
    elif isinstance(val, int) or isinstance(val, np.int_):
        return np.int64(val)
    elif isinstance(val, float) or isinstance(val, np.float_):
        float_val = np.float64(val)
        if float_val == round(float_val):
            return np.int64(float_val)
    elif isinstance(val, bool):
        return np.int64(1) if val else np.int64(0)
    elif isinstance(val, str):
        try:
            # Type casting string directly to int64 doesn't work as expected for big numbers.
            # It causes issues with pandas IntegerArray while type casting values to Int64.
            float_val = np.float64(val)
            if float_val == round(float_val):
                return np.int64(float_val)
        except Exception as e:
            return np.nan
    return np.nan


# -------------------- TYPE-VALIDATION FUNCTIONS ----------------------

def is_empty(x):
    if x == '' or pd.isna(x):
        return True
    return False


def is_boolean(x):
    x = to_boolean(x)
    if pd.isna(x):
        return False
    elif isinstance(x, bool):
        return True
    return False


def is_string(x):
    if type(x) is str:
        return True
    return False


def is_integer(x):
    x = to_integer(x)
    if pd.isna(x):
        return False
    elif isinstance(x, np.int_):
        return True
    return False


def is_double(x):
    x = to_double(x)
    if pd.isna(x):
        return False
    elif isinstance(x, float):
        return True
    return False


# -------------------- STRING FUNCTIONS ----------------------

class Replace:
    no_action = False

    def __init__(self, replace_on, replace_with, global_, ignore_case):
        self.replace_on_pattern = None
        try:
            if replace_on is not None:
                if ignore_case:
                    self.replace_on_pattern = regex.compile(replace_on, regex.IGNORECASE, regex.VERSION1)
                else:
                    self.replace_on_pattern = regex.compile(replace_on, regex.VERSION1)
        except Exception:
            self.replace_on_pattern = None
        self.global_ = global_
        self.replace_with = replace_with
        if self.replace_on_pattern is None or self.replace_on_pattern.pattern == '' or self.replace_with is None:
            self.no_action = True

    def exec(self, val):
        if pd.isnull(val):
            return val
        val = str(val)
        if self.no_action:
            return val

        replacement_count = 0 if self.global_ else 1

        replaced_val = self.replace_on_pattern.subf(self._translate(self.replace_with, val), val,
                                                    count=replacement_count)
        return replaced_val

    def _translate(self, replace_with, val):
        # https://stackoverflow.com/a/5466478
        # escaping curly braces in replaceWith string
        replace_with = regex.sub(r"{", '{{', replace_with)
        replace_with = regex.sub(r"}", '}}', replace_with)
        replace_with = regex.sub(r"\\\"", r'"', replace_with)
        r_expr = r'((\\*)\$(\d+)*)'
        replace_with = regex.sub(
            r_expr,
            (lambda x: self._replace_token(x.groups(), val)),
            replace_with)
        return regex.sub(r'\\\\', r'\\', replace_with)

    def _replace_token(self, groups, val):
        # following logic unescape all $ in replaceWith string
        if len(groups[1]) != 0:
            if len(groups[1]) % 2 == 1:
                return groups[0][len(groups[1]) // 2 + 1:]
            else:
                return groups[0][:len(groups[1]) // 2] + (f'{{{groups[2]}}}' if groups[2] is not None else '')
        # following logic check for absence of integer ahead of $
        if groups[2] is None:
            return groups[0]

        try:
            # as replaceWith string can have indexes out of group tuple,
            # so their translation is skipped
            if to_integer(groups[2]) == 0 or to_integer(groups[2]) <= self.replace_on_pattern.groups:
                return f'{{{groups[2]}}}'
        except IndexError:
            return groups[0]
        return groups[0]


class ReplacePosition:

    def __init__(self, start_index, end_index, replacement):
        self.start_index = max(start_index, 0)
        self.end_index = max(end_index, 0)
        self.replacement = replacement

    def exec(self, val):
        if pd.isnull(val):
            return val
        val = str(val)
        if len(val) <= self.start_index or self.start_index > self.end_index:
            return val

        substrings = [val[:self.start_index], self.replacement]
        if len(val) > self.end_index:
            substrings.append(val[self.end_index:])

        return ''.join(substrings)


class ReplaceColumn:

    def __init__(self, is_pattern_column, global_, ignore_case):
        self.is_pattern_column = is_pattern_column
        self.global_ = global_
        self.ignore_case = ignore_case

    def exec(self, val, pattern, replacement):
        if pd.isnull(val):
            return val
        val = str(val)
        if pattern is None or pattern == '':
            return val

        temp_pattern = regex.escape(pattern) if self.is_pattern_column else pattern
        try:
            if self.ignore_case:
                replace_on_pattern = regex.compile(temp_pattern, regex.IGNORECASE, regex.VERSION1)
            else:
                replace_on_pattern = regex.compile(temp_pattern, regex.VERSION1)

            # 0 means replace all
            replacement_count = 0 if self.global_ else 1
            replaced_val = replace_on_pattern.sub(replacement, val, count=replacement_count)
            return replaced_val

        except Exception:
            return None


class Matches:
    def __init__(self, pattern, ignore_case):
        self.pattern = None
        if pattern is not None and len(pattern) > 0:
            if ignore_case:
                self.pattern = regex.compile(pattern, regex.IGNORECASE, regex.VERSION1)
            else:
                self.pattern = regex.compile(pattern, regex.VERSION1)

    def exec(self, val):
        if self.pattern is None:
            return True
        if pd.isnull(val):
            return False

        val = str(val)
        match = self.pattern.search(val)
        return match is not None


class CountPattern:
    def __init__(self, pattern, ignore_case):
        self.pattern = None
        if pattern is not None:
            if ignore_case:
                self.pattern = regex.compile(pattern, regex.IGNORECASE, regex.VERSION1)
            else:
                self.pattern = regex.compile(pattern, regex.VERSION1)

    def exec(self, val):
        if self.pattern is None or pd.isnull(val):
            return 0

        start_pos = 0
        count = 0
        while start_pos < len(val):
            match = self.pattern.search(val, start_pos)
            if match is None:
                break

            count += 1
            start_pos = match.end()

        return count


class Find:
    def __init__(self, pattern, ignore_case):
        self.pattern = None
        if pattern is not None:
            if ignore_case:
                self.pattern = regex.compile(pattern, regex.IGNORECASE, regex.VERSION1)
            else:
                self.pattern = regex.compile(pattern, regex.VERSION1)

    def exec(self, val, start_position):
        if pd.isnull(val) or start_position is None or start_position < 0 or \
                start_position >= len(val) or self.pattern is None:
            return None

        val = str(val)
        match = self.pattern.search(val, start_position)
        if match is None:
            return None

        return match.start() + start_position


class RightFind:
    def __init__(self, pattern, ignore_case):
        self.pattern = None
        if pattern is not None:
            if ignore_case:
                self.pattern = regex.compile(pattern, regex.IGNORECASE, regex.VERSION1)
            else:
                self.pattern = regex.compile(pattern, regex.VERSION1)

    def exec(self, val, start_position):
        if pd.isnull(val) or start_position is None or start_position < 0 or \
                start_position >= len(val) or self.pattern is None:
            return None

        val = str(val)
        start_search_position = 0
        end_position = len(val) - start_position
        match_position = None
        while start_search_position < end_position:
            match = self.pattern.search(val, start_search_position, end_position)
            if match is None:
                break
            match_position = match.start()
            start_search_position = match_position + 1

        return match_position


class NthOccurrence:
    LEFT_DIRECTION = 'left'
    RIGHT_DIRECTION = 'right'

    def __init__(self, pattern, ignore_case):
        self.pattern = None
        if pattern is not None or len(pattern) == 0:
            if ignore_case:
                self.pattern = regex.compile(pattern, regex.IGNORECASE, regex.VERSION1)
            else:
                self.pattern = regex.compile(pattern, regex.VERSION1)

    def exec(self, val, match_number, direction):
        if pd.isnull(val) or len(val) == 0 or match_number is None or match_number < 0 or \
                direction is None or self.pattern is None:
            return None

        val = str(val)
        matches = [match.start() for match in self.pattern.finditer(val)]

        if match_number > len(matches):
            return None

        match_position = None
        if direction == self.LEFT_DIRECTION:
            match_position = match_number - 1
        elif direction == self.RIGHT_DIRECTION:
            match_position = len(matches) - match_number

        return matches[match_position] if match_position is not None else None


class ColumnFind:

    def __init__(self, ignore_case, start):
        self.ignore_case = False if ignore_case is None else ignore_case
        self.start = -1 if start is None else start

    def exec(self, val, pattern):
        """
        @param val: basestring
        @param pattern: basestring
        """
        if pd.isnull(val) or pd.isnull(pattern):
            return None
        val = str(val)
        pattern = str(pattern)
        if len(pattern) == 0 or self.start < 0 or self.start > len(val):
            return None
        try:
            if self.ignore_case:
                val, pattern = val.lower(), pattern.lower()
            return val.index(pattern, self.start)
        except ValueError:
            return None


class DoubleMetaphone:
    def __init__(self):
        pass

    def exec(self, val):
        """
        @param val: basestring
        Returns a two-element array of primary and secondary phonetic encodings for an input string
        """
        if pd.isnull(val):
            return None
        val = str(val)
        return list(doublemetaphone(val))


class DoubleMetaphoneEquals:
    def __init__(self):
        pass

    def exec(self, str1, str2, match_threshold):
        """
        @param str1: basestring
        @param str2: basestring
        @match_threshold: basestring
        Return true and false after comparing two strings by using Double Metaphone encoding algorithm
        """
        if pd.isnull(str1) or pd.isnull(str2):
            return False
        str1, str2 = str(str1), str(str2)
        if str1 == '' and str2 == '':
            return True
        if str1 == '' or str2 == '':
            return False
        dm1, dm2 = DoubleMetaphone().exec(str1), DoubleMetaphone().exec(str2)
        if match_threshold.upper() == 'STRONG':
            return dm1[0] == dm2[0]
        elif match_threshold.upper() == 'NORMAL':
            return dm1[0] == dm2[0] or dm1[0] == dm2[1] or dm1[1] == dm2[0]
        elif match_threshold.upper() == 'WEAK':
            return dm1[0] == dm2[0] or dm1[0] == dm2[1] or dm1[1] == dm2[0] or dm1[1] == dm2[1]
        else:
            return None

class Unicode:
    def __init__(self):
        pass

    @lru_cache(maxsize=None)
    def exec(self, val):
        if pd.isnull(val):
            return None
        val = str(val)[0]
        return ord(val)


# -------------------- MATH FUNCTIONS ----------------------

class Rand:
    def __init__(self, seed):
        random.seed(seed)

    @staticmethod
    def exec():
        return random.random()


# -------------------- TEXT FUNCTIONS ----------------------

class Text:
    """
    Generic TextTransform function, needs to extended by specific TextTransform UDF
    implementation class.
    """

    def __init__(self, on, limit, ignore_case, quote, target_group, num_outputs):
        self.on = on
        self.limit = limit
        self.num_outputs = num_outputs
        self.ignore_case = ignore_case
        self.quote = quote
        self.target_group = target_group
        self.pattern = None
        if ignore_case:
            self.pattern = regex.compile(self.on, regex.IGNORECASE, regex.VERSION1)
        else:
            self.pattern = regex.compile(self.on, regex.VERSION1)

    def get_pandas_series(self, value_list):
        return pd.Series(value_list)

    def exec(self, val):
        if pd.isnull(val) or val == '':
            empty_col = [''] * self.num_outputs
            return self.get_pandas_series(empty_col)

        if self.limit == 0:
            cols = [val] * self.num_outputs
            return cols

        quote_matcher = QuoteMatcher(val, self.quote) if (
                self.quote is not None and len(self.quote) > 0) else None
        start_pos, end_pos = 0, len(val)
        num_matches = 0
        result = []
        try:
            while start_pos < end_pos and num_matches < self.limit:
                m = self.pattern.search(val, start_pos)
                if m is None:
                    break
                start_target_group_index = m.start(self.target_group)
                end_target_group_index = m.end(self.target_group)

                if quote_matcher is not None and quote_matcher.in_quotes(m.start()):
                    continue

                self.push_regex_match(result, val, start_pos, start_target_group_index, end_target_group_index)
                start_pos = end_target_group_index
                num_matches += 1

        except Exception as e:
            print('Text transform operation failed, {}'.format(e))
            return self.handle_regex_exception(val)

        self.push_remaining_string(result, val, start_pos)
        self.backfill_columns(result)
        return self.get_pandas_series(result)

    def push_regex_match(self, output_columns, input_val, start_search_index,
                         start_target_group_ind, end_target_group_ind):
        # Provide definition in specific function implementation class.
        pass

    def push_remaining_string(self, output_columns, input_val, start_index):
        # Provide definition in specific function implementation class.
        pass

    def backfill_columns(self, output_columns):
        curr_size = len(output_columns)
        null_columns = [pd.NA] * (self.num_outputs - curr_size - 1)
        output_columns.extend(null_columns)

    def handle_regex_exception(self, input_val):
        result = []
        self.push_remaining_string(result, input_val, 0)
        self.backfill_columns(result)
        return result


class Split(Text):
    def __init__(self, on, limit, ignore_case, quote, target_group):
        super().__init__(on, limit, ignore_case, quote, target_group, limit + 1)

    def push_regex_match(self, output_columns, input_val, start_search_index,
                         start_target_group_index, end_target_group_index):
        output_columns.append(input_val[start_search_index: start_target_group_index])

    def push_remaining_string(self, output_columns, input_val, start_index):
        if start_index >= len(input_val):
            output_columns.append('')
        else:
            output_columns.append(input_val[start_index:])

    def backfill_columns(self, output_columns):
        # if input value is empty line, then first generated
        # column would be empty string
        if len(output_columns) == 0 and self.num_outputs > 0:
            output_columns.append('')
        super().backfill_columns(output_columns)


class Extract(Text):
    def __init__(self, on, limit, ignore_case, quote, target_group):
        super().__init__(on, limit, ignore_case, quote, target_group, limit)

    def push_regex_match(self, output_columns, input_val, start_search_index, start_target_group_index,
                         end_target_group_index):
        output_columns.append(input_val[start_target_group_index: end_target_group_index])

    def push_remaining_string(self, output_columns, input_column, start_index):
        # No need to do anything here as remaining string is not needed in an
        # Extract transform operation.
        pass


class SplitPositions:
    def __init__(self, positions):
        self.positions = [0] + positions

    def exec(self, val):
        if pd.isnull(val) or val == '':
            return pd.Series([''] * len(self.positions))

        output = []
        for i in range(0, len(self.positions) - 1):
            start_ind = min(self.positions[i], len(val))
            end_ind = min(self.positions[i + 1], len(val))
            output.append(val[start_ind: end_ind])

        start_ind = min(self.positions[-1], len(val))
        output.append(val[start_ind:])

        return pd.Series(output)


# -------------------- DATETIME FUNCTIONS ----------------------
class DateTimeFormat:
    """
    DateTimeFormat accepts datetime object and return string based on provided formatting string
    """

    def __init__(self, f_str):
        self.f_str = f_str

    def exec(self, val):
        """
        @param val: basestring
        """
        if pd.isnull(val):
            return None
        try:
            return DateTimeFormattingUtil.get_instance().strftime(val, self.f_str)
        except ValueError:
            return None


class ParseDate:
    """
    ParseDate accepts any number of ICU string format and parses it based on provided list of formatting strings
    """

    def __init__(self, *f_str):
        self.f_str_list = list(f_str)

    def exec(self, val):
        """
        @param val: basestring
        """
        if pd.isnull(val):
            return None
        val = str(val)
        for f_str in self.f_str_list:
            try:
                return DateTimeFormattingUtil.get_instance().strptime(val, f_str)
            except Exception:
                continue
        return None


class ToTime:
    """
    ToTime accepts any number of ICU string format and parses them based on provided format string
    """

    def __init__(self, f_str):
        self.f_str = f_str

    def exec(self, val):
        """
        @param val: basestring
        """
        if pd.isnull(val):
            return None
        val = str(val)
        try:
            return DateTimeFormattingUtil.get_instance().strptime(val, self.f_str)
        except ValueError:
            return None


class UnixTime:
    """
    UnixTime return accepts datetime object and return total second passed starting from zero epoch
    """

    def __init__(self):
        pass

    def exec(self, val):
        """
        @param val: basestring
        """
        if pd.isnull(val):
            return None
        try:
            epoch = datetime.utcfromtimestamp(0)
            return int((val - epoch).total_seconds())
        except ValueError:
            return None


class ConvertTimeZone:
    """
    ConvertTimeZone accepts any datetime object and translate timezone
    """

    def __init__(self, src_tz, tar_tz):
        self.src_tz = timezone(src_tz)
        self.tar_tz = timezone(tar_tz)

    def exec(self, val):
        """
        @param val: basestring
        """
        if pd.isnull(val):
            return None
        try:
            s_t = self.src_tz.localize(val)
            t_t = self.tar_tz.localize(val)
            return val + t_t.utcoffset() - s_t.utcoffset()
        except ValueError:
            return None


class UnixTimeFormat:
    """
    UnixTimeFormat accepts parses provides unix timestamp to datetime object
    """

    def __init__(self, f_str=None):
        self.f_str = f_str

    def exec(self, val):
        """
        @param val: basestring
        @return
        """
        if self.f_str is None or pd.isnull(val):
            return None
        if self.f_str == '':
            self.f_str = 'yyMMdd'
        if len(str(val)) > 10:
            val = val // 1000
        val = int(val)
        try:
            return DateTimeFormattingUtil.get_instance().strftime(datetime.utcfromtimestamp(val), self.f_str)
        except ValueError:
            return None


class DayOfWeek:
    """
    DayOfWeek accepts datetime object and return weekday number
    """

    def __init__(self):
        pass

    def exec(self, val):
        """
        @param val: datetime object
        @return: week number (1-Monday, 7-sunday according to joda datetime library)
        """
        if pd.isnull(val):
            return None
        # datetime weekday() returns 0-6 index weekday starting from monday, hence 1 is incremented
        return val.weekday() + 1


class WorkDayIntl:
    """
    WorkDayIntl returns delta-th working day based on provided weekend bitmask and holiday list
    """

    def __init__(self):
        pass

    def exec(self, val, offset, week_day_mask=None, holidays=None):
        """
        @param val: datetime object denoting starting date
        @param offset: integer that marks th working day from starting date
        @param week_day_mask: string of size 7 making 1 for weekend and 0 for working day -- [Mon,    Sun]
        @param holidays: list of date in string following yyyy-mm-dd and yyyy/mm/dd format
        """
        if week_day_mask is None and holidays is None:
            return None

        val = np.datetime64(val).astype('datetime64[D]')
        if week_day_mask == '1111111':
            return 0
        # replacing 1>>0 and 0>>1
        weekend_mask_complement = ''.join(['1' if day == '0' else '0' for day in week_day_mask])
        if offset >= 0:
            if holidays is None:
                offset_date = np.busday_offset(val, offset, weekmask=weekend_mask_complement, roll='backward')
            else:
                offset_date = np.busday_offset(val, offset, weekmask=weekend_mask_complement, holidays=holidays,
                                               roll='backward')
        else:
            if holidays is None:
                offset_date = np.busday_offset(val, offset, weekmask=weekend_mask_complement, roll='forward')
            else:
                offset_date = np.busday_offset(val, offset, weekmask=weekend_mask_complement, holidays=holidays,
                                               roll='forward')

        return datetime.utcfromtimestamp((offset_date - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))


class NetWorkDaysIntl:
    """
    NetWorkDaysIntl returns number of working day between given datetime object
    based on provided weekend bitmask and holiday list
    """

    def __init__(self):
        pass

    def exec(self, lhs, rhs, week_day_mask=None, holidays=None):
        """
        @param lhs : starting datetime object
        @param rhs: end datetime object
        @param week_day_mask: string of size 7 making 1 for weekend and 0 for working day -- [Mon,    Sun]
        @param holidays: list of date in string following yyyy-mm-dd and yyyy/mm/dd format
        """
        if week_day_mask is None and holidays is None:
            return None
        lhs = np.datetime64(lhs).astype('datetime64[D]')
        rhs = np.datetime64(rhs).astype('datetime64[D]')
        if week_day_mask == '1111111':
            return 0
        # replacing 1>>0 and 0>>1
        weekend_mask_complement = ''.join(['1' if day == '0' else '0' for day in week_day_mask])
        if holidays is None:
            return np.busday_count(lhs, rhs + np.timedelta64(1, 'D'), weekmask=weekend_mask_complement)
        return np.busday_count(lhs, rhs + np.timedelta64(1, 'D'), weekmask=weekend_mask_complement, holidays=holidays)


class EOMonth:

    def __init__(self):
        pass

    def exec(self, val, delta_month):
        if val is None or not isinstance(val, datetime):
            return None
        val_post_delta = DateAdd('month').exec(val, delta_month)
        last_day = (val_post_delta.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return SerialNumber().exec(last_day)


class DateAdd:

    def __init__(self, measure):
        self.measure = measure

    def exec(self, val, delta):
        if pd.isnull(val):
            return None
        if not isinstance(val, datetime):
            return val
        return val + self.get_measure_delta_datetime(delta)

    def get_measure_delta_datetime(self, delta):
        if self.measure == 'year':
            return relativedelta(years=delta)
        elif self.measure == 'month':
            return relativedelta(months=delta)
        elif self.measure == 'week':
            return relativedelta(days=(7 * delta))
        elif self.measure == 'day':
            return relativedelta(days=delta)
        elif self.measure == 'hour':
            return relativedelta(hours=delta)
        elif self.measure == 'minute':
            return relativedelta(minutes=delta)
        elif self.measure == 'second':
            return relativedelta(seconds=delta)
        elif self.measure == 'millisecond':
            return relativedelta(microseconds=(delta * 1000))
        return None


class DateDiff:

    def __init__(self, measure):
        self.measure = measure

    def exec(self, lhs, rhs):
        if pd.isnull(lhs) or pd.isnull(rhs):
            return None
        # diff_date = rhs - lhs
        return self._get_datetime_diff_measure(lhs, rhs)

    def _get_datetime_diff_measure(self, start_date, end_date):
        delta_date = end_date - start_date
        if self.measure == 'year':
            return delta_date.days // 365
        elif self.measure == 'month':
            return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        elif self.measure == 'week':
            return delta_date.days // 7
        elif self.measure == 'day':
            return delta_date.days
        elif self.measure == 'hour':
            return int(delta_date.total_seconds()) // 3600
        elif self.measure == 'minute':
            return int(delta_date.total_seconds()) // 60
        elif self.measure == 'second':
            return int(delta_date.total_seconds())
        elif self.measure == 'millisecond':
            return delta_date.microseconds // 1000
        return None


class SerialNumber:
    # number of days between Jan 1, 1900 till Jan 1, 1970 (including the last day)
    DAYS_BETWEEN_1900_TILL_1970 = 25568

    def __init__(self):
        pass

    def exec(self, val):
        """
        @param val: datetime input object
        """
        if not isinstance(val, datetime) or datetime is None:
            return None
        if val.year < 1900:
            return None
        try:
            ref_date = datetime(1899, 12, 30)
            delta = val - ref_date
            return int(float(delta.days) + (float(delta.seconds) / 86400))
        except ValueError:
            return None


# -------------------- AGGREGATE FUNCTIONS ----------------------

def any_agg(series):
    try:
        series = series.dropna().to_list()
        return series[0]
    except IndexError:
        return np.NaN


def size_agg(series):
    return series.__len__()


def var(ddof=0):
    def var_(series):
        return series.var(ddof=ddof)

    return var_


def stdev(ddof=0):
    def stdev_(series):
        return series.std(ddof=ddof)

    return stdev_


def mode(series):
    """
    https://docs.trifacta.com/display/SS/MODE+Function
    Following logic processes series ignoring nan values and return the minimum value in case of tie
    """
    return series.mode(dropna=True).min()


def approximate_quantile(q, interpolation='linear'):
    def approximate_quantile_(series):
        return series.quantile(q=q, interpolation=interpolation)

    return approximate_quantile_


def kth_largest(k, unique=False):
    def kth_largest_(series):
        if unique:
            return series.drop_duplicates().nlargest(k).iloc[-1]
        else:
            return series.nlargest(k).iloc[-1]

    return kth_largest_


def to_list(unique=False):
    def to_list_(series):
        if unique:
            return series.dropna().drop_duplicates().to_list()
        else:
            return series.dropna().to_list()

    return to_list_


def rank(dense=False):
    def rank_(df):
        if isinstance(df, pd.DataFrame):
            series = df.iloc[:, 0]
        else:
            series = df
        series = series.apply(lambda x: x if x != [np.NaN] else np.NaN)
        if dense:
            series = series.rank(method='dense', na_option='bottom').reset_index(drop=True)
        else:
            series = series.rank(method='min', na_option='bottom').reset_index(drop=True)
        if isinstance(df, pd.DataFrame):
            return series.to_frame()
        return series

    return rank_


def window_fill(indexer):
    def window_fill_(df):
        left, right = indexer._get_tf_extreme()
        if left < right:
            if left == -1:
                df = df.ffill()
            elif left > 0:
                df = df.ffill(limit=left)
            if right > 0:
                df = df.bfill(limit=right)
        else:
            if right > 0:
                df = df.bfill(limit=right)
            if left == -1:
                df = df.ffill()
            elif left > 0:
                df = df.ffill(limit=left)
        return df.reset_index(drop=True)

    return window_fill_


def window_session(timeout):
    def window_session_(df):
        # stripping out first column from received dataframe, as session work on a single column
        if isinstance(df, pd.DataFrame):
            series = df.iloc[:, 0]
        else:
            series = df
        if series.first_valid_index() is not None:
            last_val = series[series.first_valid_index()]
        else:
            return series.to_frame()
        null_mask = series.isna().to_numpy()
        last_session_id = 1
        session_list = np.ones_like(series)
        series = series.to_numpy()
        for x in range(len(series)):
            if null_mask[x]:
                session_list[x] = np.NaN
            else:
                last_session_id = last_session_id + (1 if abs(series[x] - last_val) > timeout else 0)
                session_list[x] = last_session_id
                last_val = series[x]
        series = pd.Series(session_list)
        if isinstance(df, pd.DataFrame):
            return series.to_frame()
        return series

    return window_session_


class FrameBoundEnum(Enum):
    UNBOUNDED_PRECEDING = 1
    VALUE_PRECEDING = 2
    CURRENT_ROW = 3
    VALUE_FOLLOWING = 4
    UNBOUNDED_FOLLOWING = 5


class WindowIndexer(pd.api.indexers.BaseIndexer):
    def get_window_bounds(self,
                          num_values: int = 0,
                          min_periods: Optional[int] = None,
                          center: Optional[bool] = None,
                          closed: Optional[str] = None):
        start_bounds = self._populate_bounds(num_values, self.start[0], self.start[1])
        end_bounds = self._populate_bounds(num_values, self.end[0], self.end[1], end=True)
        return start_bounds, end_bounds

    def _populate_bounds(self, num_values, frame_bound_type, value, end=False):
        bounds = np.empty(num_values, dtype=np.int64)
        if frame_bound_type == FrameBoundEnum.UNBOUNDED_PRECEDING:
            for i in range(num_values):
                bounds[i] = 0
        elif frame_bound_type == FrameBoundEnum.VALUE_PRECEDING:
            for i in range(num_values):
                bounds[i] = max(0, i - value + (1 if end else 0))
        elif frame_bound_type == FrameBoundEnum.CURRENT_ROW:
            for i in range(num_values):
                bounds[i] = i + (1 if end else 0)
        elif frame_bound_type == FrameBoundEnum.VALUE_FOLLOWING:
            for i in range(num_values):
                bounds[i] = min(num_values, i + value + (1 if end else 0))
        elif frame_bound_type == FrameBoundEnum.UNBOUNDED_FOLLOWING:
            for i in range(num_values):
                bounds[i] = num_values
        return bounds

    def _get_tf_extreme(self):
        """
        return trifacta documentation based extreme bound
        """
        left = right = 0
        if self.start[0] == FrameBoundEnum.UNBOUNDED_PRECEDING:
            left = -1
        elif self.start[0] == FrameBoundEnum.VALUE_PRECEDING:
            left = self.start[1]
        right = self.end[1]
        return left, right


class MultiSplit:
    END_OF_LINE_PATTERN = "()($)"

    def __init__(self, *regex_expressions):
        self.regex_expressions = list()
        try:
            for r_expr in list(regex_expressions):
                self.regex_expressions.append(regex.compile(r_expr))
            self.regex_expressions.append(regex.compile(self.END_OF_LINE_PATTERN))
        except regex.error as e:
            # case of invalid regex expression
            self.regex_expressions.append(None)
        self.num_col = self.regex_expressions.__len__()

    def exec(self, val):
        split_np_arr = np.empty(self.num_col + 1, dtype=np.object)
        split_np_arr[0] = val
        start_split_at = 0
        for i in range(self.num_col):
            r_expr = self.regex_expressions[i]
            if r_expr is None:
                # assigning original column in case of invalid regex expression
                split_np_arr[i + 1] = None
                continue
            match = r_expr.search(val, start_split_at)
            split_np_arr[i + 1] = val[start_split_at:match.start(2)]
            start_split_at = match.end(2)
        return pd.Series(split_np_arr)
