import six
from six import string_types
from swimbundle_utils.exceptions import SwimlaneIntegrationException, InvalidInput
from swimbundle_utils.validation import Validators, StopValidation
from swimbundle_utils.asset_debugger import AssetDebugger
from six import string_types as StringTypes
from validators import ValidationFailure
from operator import eq, gt, lt
import pendulum
from math import ceil, log
DateTime = type(pendulum.now())  # py2/py3 support
import re
import base64


if six.PY2:
    from types import MethodType, InstanceType, FunctionType
    FuncTypes = (FunctionType, InstanceType, MethodType)
else:
    import types
    from types import FunctionType
    InstanceType = getattr(types, "InstanceType", object)
    FuncTypes = FunctionType


def asset_parser(context_asset, host_name="host",
                 username="username", password="password", auth=None, **kwargs):
    """Take in a context asset and break it into params for an ``__init__`` call on BasicRestEndpoint
    
    Args:
        context_asset: Context asset object
        host_name: host key name to grab from asset, defaults to ``host``
        username: username key name to grab from asset, defaults to ``username``
        password: password key name to grab from asset, defaults to ``password``
        auth: optional auth argument to override username/password. Set to None to disable auth
        kwargs: optional keyword args to overwrite the parameters with
    
    Returns:
        Dictionary of key args to use with \*\*{} in the ``super().__init__()`` of a BasicRestEndpoint

    """
    host = context_asset.get(host_name)
    if host is not None:
        host = host.strip(" /")
        if 'port' in context_asset:
            host = "{}:{}".format(host, context_asset['port'])

    params = {
        "host": host,
        "verify": context_asset.get("verify_ssl", True),
        "proxy": context_asset.get("http_proxy"),
        "verbose_errors": context_asset.get("verbose_errors", False)
    }

    if auth == "basic":  # nondefault auth
        params["auth"] = (context_asset[username], context_asset[password])
    elif auth:  # No auth, but not none (else is inferred to be no auth)
        params["auth"] = auth

    params.update(kwargs)

    return params


def create_attachment(filename, raw_data):
    """Easy way to create a single attachment. To create multiple attachments under a single key, use SwimlaneAttachment()
    
    Args:
        filename: filname of the attachment
        raw_data: raw data of the file (pre-base64)
    
    Returns:
        JSON data suitable for a key output in Swimlane

    """
    swa = SwimlaneAttachments()
    swa.add_attachment(filename, raw_data)
    return swa.get_attachments()


class SwimlaneAttachments(object):
    """Swimlane Attachment Manager Class"""
    
    def __init__(self):
        self.attachments = []

    def add_attachment(self, filename, raw_data):
        """Add an attachment to 

        Args:
            filename: Name of the file
            raw_data: Raw, pre-base64 data to encode

        """
        if isinstance(raw_data, string_types) and not isinstance(raw_data, bytes):  # Needed for python3 support
            raw_data = raw_data.encode()

        file_data = base64.b64encode(raw_data)
        if isinstance(file_data, bytes):
            # In python3, b64encode returns a bytes object.  Platform cant handle this because it isn't JSON
            #  serializable, so we convert it to a string.
            file_data = file_data.decode("ascii")

        self.attachments.append({
            "filename": filename,
            "base64": file_data
        })
        
    def get_attachments(self):
        """Get attachments fit for a key output in Swimlane

        Examples:
            All files to key "output_files"::
            
                >>>swa = SwimlaneAttachments()
                >>>swa.add_attachment("myfile.txt", "asdf")
                >>>output["output_files"] = swa.get_attachments()

        Returns:
            Attachments for output in a key in Swimlane

        """
        return self.attachments


def check_input(in_val, exp_val, flags=None, mapping=None, options=None):
    """Shorthand function for creating an InputChecker()

    Args:
        in_val: Value to check
        exp_val: Expected value(s)
        flags: Optional flags to pass to InputChecker
        mapping: Optional mapping to pass to InputChecker
        options: Optional options to pass to InputChecker

    Raises:
        SwimlaneIntegrationException: if the parsed or checked value fails

    Returns:
        Parsed and Checked Value

    """
    return InputChecker(flags=flags, mapping=mapping, options=options).check(in_val, exp_val)


def create_test_conn(base_cls, execute_func=None, custom_test_funcs=[]):
    """Create a test connection base class

    Examples:
        Create a basic integration for MyIntegration::
            >>>SwMain = create_test_conn(MyIntegration)
        Create a basic integration for MyIntegration with auth function name "auth"
            >>>SwMain = create_test_conn(MyIntegration, "auth")
        Create a basic integration for MyIntegration with custom test functions
            >>>SwMain = create_test_conn(MyIntegration, custom_test_funcs=[custom_func_1, custom_func_2])
            see quickstart for appropriate test function signatures

    Args:
        base_cls: a Classtype of the ABCIntegration
        execute_func: the name of the function to call during execute, such as 'login'

    Returns:
        TestConnection class

    """

    class SwMain(object):
        def __init__(self, context):
            self.context = context

        def execute(self):
            try:
                c = base_cls(self.context)
                if execute_func:
                    getattr(c, execute_func)()
                return {"successful": True}
            except Exception as e:
                message = e
                try:
                    message = AssetDebugger(asset=self.context.asset, test_conn_exception=e, custom_tests=custom_test_funcs).results
                except Exception as ex:
                    pass
                return {"successful": False, "errorMessage": str(message)}
    return SwMain


class InputChecker(object):
    STOP_VALIDATION = StopValidation

    def __init__(self, flags=None, mapping=None, options=None):
        """Check the validity of a given set of inputs
        Apply Order:
        1. flags
        2. mappings
        3. options

        Args:
            options: Special options to apply to given inputs, such as {"type": "int"}
            mapping: Change the inputs to another set, such as {True: "enable", False: "disable"}
            flags: Function to apply to input before any checking, like ["lower"]

        """

        self.options = options or {}  # {"type": "int"} etc
        self.mapping = mapping or {}  # {False: "disable"} etc
        self.flags = set(flags) if flags else set()  # ["lower"]
        self.validators = Validators()

        # TODO link inputs? if a and b -> good else bad
        # TODO Wait until .validate() is called to check all inputs (possibility for linked inputs?)

        self.flag_funcs = {
            "lower": lambda x: x.lower(),
            "caps": lambda x: x.upper(),
            "optional": lambda x: InputChecker.STOP_VALIDATION if x is None else x
            # Stop validation on optional if it's None
        }

        self.option_funcs = {
            "type": self.validators.get_type_validators()
        }

    def parse(self, val, flags=None, mapping=None, options=None):
        """Apply Order:
        1. flags
        2. mappings
        3. options

        All applied parameters will be merged with parameters set in __init__, taking priority
        
        Args:
            val: Value to parse
            options: Special options to apply to given inputs, such as ``{"type": "int"}``
            mapping: Change the inputs to another set, such as ``{True: "enable", False: "disable"}``
            flags: Function to apply to input before any checking, like ``["lower"]``

        Returns:
            Parsed value before checking

        """
        if not flags:
            flags = self.flags
        else:
            flags = self.flags.union(flags)

        if not options:
            options = self.options
        else:
            options.update(self.options)

        if not mapping:
            mapping = self.mapping
        else:
            mapping.update(self.mapping)

        # flags, mappings, options
        # Flags
        for flag in flags:
            if flag in self.flag_funcs:
                val = self.flag_funcs[flag](val)
            else:
                raise ValueError("Invalid flag '{}'".format(flag))

        # mappings
        if val in mapping:
            val = mapping[val]

        # options
        for option_k, option_v in six.iteritems(options):
            if option_k in self.option_funcs:
                if option_v in self.option_funcs[option_k]:
                    val = self.option_funcs[option_k][option_v](val)
                else:
                    raise ValueError("Invalid option value '{}'".format(option_v))
            else:
                raise ValueError("Invalid option '{}'".format(option_k))

        return val

    def check(self, val, expected=None, flags=None, mapping=None, options=None):
        """Check a value with given expected output, flags, mapping, and options
        
        Args:
            val: Value to check
            expected: Expected value(s) (can be a list or None if just type checking)
            flags: list of flags to apply
            mapping: dict to map values to 
            options: options to change how val is parsed

        Returns:
            Parsed and checked value

        """
        try:
            val = self.parse(val, flags=flags, mapping=mapping, options=options)
        except ValidationFailure as e:
            raise SwimlaneIntegrationException("Invalid value '{val}' Exception: {e}".format(val=val, e=str(e)))

        if val == InputChecker.STOP_VALIDATION:  # Parsed value says to stop validation, return None
            return None

        if expected is not None:  # If expected is None, the validation has been done in the .parse()
            if val not in expected:
                raise SwimlaneIntegrationException("Unexpected value '{}', must be one of '{}'".format(val, expected))

        return val


def parse_datetime(param_name, param_value):
    """
    :param val: A string representing a datetime.
    This can be any standard datetime format supported by pendulum or a relative datetime.
    Relative datetime format:
        For the current time:
            now
        Any other time:
            (+/-)(integer) (milliseconds|seconds|minutes|days|weeks|months|years)
    examples:
        now
        -1 months
        +3 days
        -123 seconds

    :return: a pendulum object for the datetime
    """
    try:
        datetime = QueryStringParser.is_datetime(param_value)
    except SwimlaneIntegrationException as e:
        raise InvalidInput(e.message,
                           input_name=param_name,
                           input_value=param_value)
    if datetime is None:
        raise InvalidInput("Unknown datetime format",
                           input_name=param_name,
                           input_value=param_value)
    return datetime


class InvalidComparisonTimevalError(Exception):
    pass


class ComparisonTimeval(object):
    OP_EQ = ""
    OP_GTE = "gte"
    OP_LTE = "lte"
    OP_LT = "lt"
    OP_GT = "gt"

    OP_ORDER = [OP_EQ, OP_LT, OP_LTE, OP_GT, OP_GTE]  # Higher index == higher priority

    ALL_OPS = [
        OP_GTE,
        OP_LTE,
        OP_LT,
        OP_GT,
        OP_EQ  # Always put this last in list, or regex won't work
    ]
    OP_MAP = {  # OP_NAME -> OP func (a, b) -> bool
        OP_EQ: eq,
        OP_GTE: lambda a, b: gt(a, b) or eq(a, b),
        # v1 == v2 --lte-> v2 <= v1
        OP_LTE: lambda a, b: lt(a, b) or eq(a, b),
        OP_LT: lambda a, b: lt(a, b),
        OP_GT: lambda a, b: gt(a, b),
    }
    RELATIVE_OP = {
        "-": "subtract",
        "+": "add"
    }

    def __init__(self, time_val, operator):
        if operator not in self.ALL_OPS:
            raise ValueError("Invalid time.<op>now() operator '{}' Valid operators '{}' use time.now(), time.gtenow(), etc...".format(operator, self.ALL_OPS))
        self.time_val = time_val
        self.op = operator

    def __getattr__(self, item):

        return getattr(self.time_val, item)

    def __eq__(self, other):
        dt = parse_datetime("time param", other)
        func = self.OP_MAP[self.op]
        v1 = self.time_val
        v2 = dt
        if isinstance(dt, ComparisonTimeval):
            v2 = dt.time_val

        val = func(v2, v1)

        if isinstance(other, ComparisonTimeval):
            op1 = self.OP_ORDER.index(self.op)
            op2 = self.OP_ORDER.index(other.op)
            opval1 = self.op
            opval2 = other.op

            # v1 = self.time_val
            # v2 = dt.time_val

            val = val or other == self.time_val

        return val

    def __str__(self):
        return str(self.time_val)

    @staticmethod
    def create_timeval(val):
        """
        :param val: A string representing a relative time or comparison timeval
        Relative datetime format:
            For the current time:
                now
            Any other time:
                (+/-)(integer) (milliseconds|seconds|minutes|days|weeks|months|years)
        examples:
            now
            -1 months
            +3 days
            -123 seconds

        comparison timeval format:
            ("lte"|"gte"|"lt"|"gt"|"") now (relative time format)
        examples:
            lte now -2 days

        :return: a pendulum object for the datetime
        """
        if isinstance(val, StringTypes):
            val = val.replace(" ", "")
            pat = re.compile(r'^(?:(' + "|".join(ComparisonTimeval.ALL_OPS) + r')now)?(?:(\+|-)([0-9]+)(.+))?$')
            match = pat.match(val)
            match = match.groups() if match is not None else None
            if val == 'now':
                return ComparisonTimeval(pendulum.now(), "")
            elif match and any(match):
                op, fn, timespan_val, timespan_name = match
                op = "" if op is None else op
                dt = pendulum.now()
                if fn:
                    fn_name = ComparisonTimeval.RELATIVE_OP[fn]
                    try:
                        dt = getattr(dt, fn_name)(**{timespan_name: int(timespan_val)})
                    except TypeError as e:
                        raise InvalidComparisonTimevalError(
                            "Invalid time unit '{}'.  must be one of: milliseconds, "
                            "seconds, minutes, days, weeks, months, years".format(timespan_name)
                        )
                return ComparisonTimeval(dt, op)
            else:
                raise InvalidComparisonTimevalError("Invalid value '{}', didn't match timeval regex!".format(val))

        elif isinstance(val, ComparisonTimeval):
            return val
        else:
            raise InvalidComparisonTimevalError("Invalid type for value passed to create_timeval, type: '{}'".format(type(val)))

    @staticmethod
    def to_iso8601_period(compare_val, other_time=None):
        """
        Will return the Absolute value time difference between other_time and the Comparision value.
        i.e. if it's 1/1 and the val is 1/2, the result will be 'P1D'
        and vice versa, if it's 1/2, and the val is 1/1, result will be P1D

        Convert the ComparisonTimeval to ISO 8601 Period format:

        P(x)Y(x)M(x)DT(x)H(x)M(x)S

        Where:

        P is the duration period and is always placed at the beginning of the duration.
        Y is the year
        M is the month
        D is the day
        T is the time designator that preceeds the time components
        H is the hour
        M is the minute
        S is the second
        For example:

        P2Y5M3DT12H30M5S

        Represents a duration of two years, five months, three days, twelve hours, thirty minutes, and five seconds.

        And:
        P30D
        Is a period of 30 days

        Args:
            other_time: Other time to compare against, instead of now()

        Returns:
            String value for this ComparisonTimeval
        """
        if other_time is None:
            other_time = pendulum.now()
        diff = other_time.diff(compare_val.time_val)
        times = ["years", "months", "days", "TIME", "hours", "minutes", "seconds"]

        iso_str = "P"

        for time in times:
            if time == "TIME":
                iso_str += "T"
                continue
            # Use internal timedelta for correct vals
            val = getattr(diff._delta, time)
            if val == 0:
                continue
            else:
                iso_str += "{}{}".format(int(val), time[0].upper())

        if iso_str.endswith("T"):
            iso_str = iso_str[:-1]

        if iso_str == "P":
            iso_str = "P0D"

        return iso_str


class QueryStringParser(object):
    def __init__(self, string, delimiter=",", assigner="=", try_type=False):
        """
        Parse a given query string into parameters, such as 'key1=value1,key2=value2'
        Args:
            string: list of data coming in to parse
            delimiter: Entry separator character, defaults to ',' (entry1,entry2)
            assigner: Entry key-value separator, defaults to '=' (key=value)
            try_type: Try to type the incoming values to int, datetime, boolean, or string
                        if try_type is a function, it should have a definition like:
                        try_type({data_dict}) -> {new_data_dict}
                        Will overwrite the type guessed
        """
        self.delm = delimiter
        self.asgn = assigner
        self.try_type = try_type
        self._try_isfunc = bool(isinstance(self.try_type, FuncTypes))

        self._raw_string = string
        self.data = {}

    @staticmethod
    def is_int(val):
        try:
            return int(val)
        except ValueError:
            return None

    @staticmethod
    def is_datetime(val):
        """
        :param val: A string representing a datetime.
        This can be any standard datetime format supported by pendulum or a relative datetime.
        Relative datetime format:
            For the current time:
                now
            Any other time:
                (+/-)(integer) (milliseconds|seconds|minutes|days|weeks|months|years)
        examples:
            now
            -1 months
            +3 days
            -123 seconds

        :return: a pendulum object for the datetime
        """
        try:
            return ComparisonTimeval.create_timeval(val)
        except InvalidComparisonTimevalError:
            pass

        dt = try_parse_dt(val, is_number=False, return_pend_obj=True)
        if isinstance(dt, DateTime):
            return dt
        try:
            return pendulum.parse(dt, strict=False)
        except Exception:
            return None

    def _typecast(self):
        # Take in the string values and turn them into int bool or string
        new_data = {}
        
        for k, v in self.data.items():
            if isinstance(v, StringTypes):
                if v.lower() == "true":  # Bool case
                    new_data[k] = True
                elif v.lower() == "false":  # Bool case
                    new_data[k] = False
                elif self.is_int(v) is not None:  # Int case
                    new_data[k] = int(v)
                elif self.is_datetime(v) is not None:  # Datetime case
                    new_data[k] = self.is_datetime(v)
                else:
                    new_data[k] = v  # Can't figure out what it is, must leave as a string
            else:
                new_data[k] = v  # v is already a nonstring type
        
        return new_data

    def parse(self):
        try:
            pairs = self._raw_string.split(self.delm)
            
            for pair in pairs:
                k, v = pair.split(self.asgn)
                self.data[k] = v
            
            if not self.try_type:
                return self.data
            else:
                data = self._typecast()
                if self._try_isfunc:
                    data = self.try_type(data)
                return data
        except Exception as e:
            raise SwimlaneIntegrationException("Exception parsing QueryString, most likely malformed input! Error: {}".format(str(e)))


DEFAULT_TIMEVAL_IGNORES = [
        "\d+/\d+$"  # Don't match stuff like 5/67
]


def try_parse_dt(value, is_number=False, ignore_dt_formats=None, special_dt_formats=None, oldest_dt_allowed=None, return_pend_obj=False):
    """
            Try to parse a given value into a pendulum object, then return the iso string
            Works with strings and numbers that look like datestamps
            Ignores anything not parsed, returning it without parsing
            Ignores any datetime that is too old (could just be a really big numerical value) (anything past 2005)
            Uses self.special_dt_formats for other formats that could be specific to the data

            Args:
                value: Value to attempt to parse into a datetime
                is_number: Is the value a number and should be treated as a timestamp?
                ignore_dt_formats: List of formats to ignore in parsing, defaults to DEFAULT_TIMEVAL_IGNORES
                special_dt_formats: List of string formats to attempt parsing on for auto DT parsing. Will be ignored if
                    autoparse_dt_strs is False
                oldest_dt_allowed: String of the oldest datetime that is allowed to be parsed. Defaults to 2005
                return_pend_obj: Return a pendulum object if parsing is successful, otherwise a string will be returned
            """
    if isinstance(value, DateTime):
        if return_pend_obj:
            return pendulum.instance(value)
        else:
            return str(value)

    dt = None
    if not ignore_dt_formats:
        ignore_dt_formats = DEFAULT_TIMEVAL_IGNORES

    if not special_dt_formats:
        special_dt_formats = []

    if not oldest_dt_allowed:
        oldest_dt_allowed = pendulum.parse("2005")

    try:
        original_value = value
        value = float(original_value)
        is_number = True
        value = int(original_value)
    except ValueError:
        # Attempt to parse the value as a number, in case it's a string
        pass

    if ignore_dt_formats and not is_number:
        for fmt in ignore_dt_formats:
            if re.match(fmt, value):
                return value  # Ignore format, return value unprocessed

    try:
        if is_number:
            if ceil(log(value, 10)) == 13:
                value = value / 1000.0
            dt = pendulum.from_timestamp(value)
        else:
            dt = pendulum.parse(value, strict=False)
    except Exception:  # Broad exception clause to be picky about dates and parsing errors
        if is_number:  # Can't parse number with format, must be unparsable
            return value

        for fmt in special_dt_formats:  # Try special formats
            try:
                dt = pendulum.from_format(value, fmt)
            except Exception:
                continue

    if dt:
        diff = oldest_dt_allowed.diff(dt)
        signed_diff = diff.years * (1 if diff.invert else -1)
        if signed_diff <= 0:
            # Difference between datetime and oldest_dt is negative, which means it's oldest_dt+
            if return_pend_obj:
                return dt
            else:
                return dt.to_iso8601_string()
        else:
            # Difference is positive, earlier than oldest_dt, probably not a timestamp
            return value
    else:
        return value  # dt isn't a value


def get_session(base_class, asset_keys):
    """
    This decorator helps mimic the separation of asset and inputs we have in Swimlane plugins.
    We often want to pass all the inputs directly as API params, so this allows us to do
      that by removing any asset params before the action is called
    Basically all it does is remove the asset params after the base class has been instantiated so
      that the only params that are passed into your action functions are the inputs for that
      specific action.

    base_class: the base class of the plugin, should build the session and authenticate.  Anything
                  that uses asset params need to be in the base class as those params will not be
                  available in the action function
    asset_keys:  a list of each param that is part of the asset.  This is used to remove those keys from
                   the kwargs so that the action function kwargs only contains params defined in the action.
    """
    def inner(func):
        def session_setup(*args, **kwargs):
            conn = base_class(*args, **kwargs)
            for key in asset_keys:
                kwargs.pop(key, None)
            return func(conn, *args, **kwargs)
        return session_setup
    return inner

def test_connection(custom_tests=()):
    """
    decorator that replaces create_test_conn,  use for the function that is called as an asset test connection.
    """
    def inner(func):
        def session_setup(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                message = e
                try:
                    message = AssetDebugger(asset=kwargs, test_conn_exception=e, custom_tests=custom_tests).results
                except Exception as ex:
                    pass
                raise SwimlaneIntegrationException(str(message))
        return session_setup
    return inner
