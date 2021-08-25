"""Flywheel utilities and common helpers."""
import abc
import datetime as dt
import functools
import importlib.metadata as importlib_metadata
import itertools
import operator
import os
import re
import threading
import time
import typing as t
from collections.abc import Callable
from pathlib import Path
from tempfile import SpooledTemporaryFile, TemporaryDirectory

__version__ = importlib_metadata.version(__name__)


# FORMATTERS


PLURALS = {
    "study": "studies",
    "series": "series",
    "analysis": "analyses",
}


def pluralize(singular: str, plural: str = "") -> str:
    """Return plural for given singular noun."""
    if plural:
        PLURALS[singular.lower()] = plural.lower()
    return PLURALS.get(singular, f"{singular}s")


def quantify(num: int, singular: str, plural: str = "") -> str:
    """Return "counted str" for given num and word: (3,'file') => '3 files'."""
    if num == 1:
        return f"1 {singular}"
    plural = pluralize(singular, plural)
    return f"{num} {plural}"


def hrsize(size: float) -> str:
    """Return human-readable file size for given number of bytes."""
    unit, decimals = "B", 0
    for unit in "BKMGTPEZY":
        decimals = 0 if unit == "B" or round(size) > 9 else 1
        if round(size) < 1000 or unit == "Y":
            break
        size /= 1024.0
    return f"{size:.{decimals}f}{unit}".replace(".0", "")


def hrtime(seconds: float) -> str:
    """Return human-readable time duration for given number of seconds."""
    remainder = seconds
    parts: t.List[str] = []
    units = {"y": 31536000, "w": 604800, "d": 86400, "h": 3600, "m": 60, "s": 1}
    for unit, seconds_in_unit in units.items():
        quotient, remainder = divmod(remainder, seconds_in_unit)
        if len(parts) > 1 or (parts and not quotient):
            break
        if unit == "s" and not parts:
            decimals = 0 if round(quotient) >= 10 or not round(remainder, 1) else 1
            parts.append(f"{quotient + remainder:.{decimals}f}{unit}")
        elif quotient >= 1:
            parts.append(f"{int(quotient)}{unit}")
    return " ".join(parts)


class Timer:  # pylint: disable=too-few-public-methods
    """Timer for creating size/speed reports on file processing/transfers."""

    # pylint: disable=redefined-builtin
    def __init__(self, files: int = 0, bytes: int = 0) -> None:
        """Init timer w/ current timestamp and the no. of files/bytes."""
        self.start = time.time()
        self.files = files
        self.bytes = bytes

    def report(self) -> str:
        """Return message with size and speed info based on the elapsed time."""
        elapsed = time.time() - self.start
        size, speed = [], []
        if self.files or not self.bytes:
            size.append(quantify(self.files, "file"))
            speed.append(f"{self.files / elapsed:.1f}/s")
        if self.bytes:
            size.append(hrsize(self.bytes))
            speed.append(hrsize(self.bytes / elapsed) + "/s")
        return f"{'|'.join(size)} in {hrtime(elapsed)} [{'|'.join(speed)}]"


def str_to_python_id(raw_string: str) -> str:
    """Convert any string to a valid python identifier in a reversible way."""

    def char_to_hex(match: t.Match) -> str:
        return f"__{ord(match.group(0)):02x}__"

    raw_string = re.sub(r"^[^a-z_]", char_to_hex, raw_string, flags=re.I)
    return re.sub(r"[^a-z_0-9]{1}", char_to_hex, raw_string, flags=re.I)


def python_id_to_str(python_id: str) -> str:
    """Convert a python identifier back to the original/normal string."""

    def hex_to_char(match: t.Match) -> str:
        return chr(int(match.group(1), 16))

    return re.sub(r"__([a-f0-9]{2})__", hex_to_char, python_id)


# PARSERS


def parse_hrsize(value: str) -> float:
    """Return number of bytes for given human-readable file size."""
    pattern = r"(?P<num>\d+(\.\d*)?)\s*(?P<unit>([KMGTPEZY]i?)?B?)"
    match = re.match(pattern, value, flags=re.I)
    if match is None:
        raise ValueError(f"Cannot parse human-readable size: {value}")
    num = float(match.groupdict()["num"])
    unit = match.groupdict()["unit"].upper().rstrip("BI") or "B"
    units = {u: 1024 ** i for i, u in enumerate("BKMGTPEZY")}
    return num * units[unit]


def parse_hrtime(value: str) -> float:
    """Return number of seconds for given human-readable time duration."""
    parts = value.split()
    units = {"y": 31536000, "w": 604800, "d": 86400, "h": 3600, "m": 60, "s": 1}
    seconds = 0.0
    regex = re.compile(r"(?P<num>\d+(\.\d*)?)(?P<unit>[ywdhms])", flags=re.I)
    for part in parts:
        match = regex.match(part)
        if match is None:
            raise ValueError(f"Cannot parse human-readable time: {part}")
        num, unit = float(match.group("num")), match.group("unit").lower()
        seconds += num * units[unit]
    return seconds


URL_RE = re.compile(
    r"^"
    r"(?P<scheme>[^+:]+)(\+(?P<driver>[^:]+))?://"
    r"((?P<username>[^:]+):(?P<password>[^@]+)@)?"
    r"(?P<host>[^:/?#]*)"
    r"(:(?P<port>\d+))?"
    r"((?P<path>/[^?#]+))?"
    r"(\?(?P<query>[^#]+))?"
    r"(#(?P<fragment>.*))?"
    r"$"
)


def parse_url(url: str, pattern: t.Pattern = URL_RE) -> t.Dict[str, str]:
    """Return dictionary of fields parsed from a URL."""
    match = pattern.match(url)
    if not match:
        raise ValueError(f"Invalid URL: {url}")
    parsed = {k: v for k, v in match.groupdict().items() if v is not None}
    params = parsed.pop("query", "")
    if params:
        # store query params directly on the result
        for param in params.split("&"):
            if "=" not in param:
                param = f"{param}="
            key, value = param.split("=", maxsplit=1)
            if "," in value:
                value = value.split(",")
            parsed[key] = value
    return attrify(parsed)


# DICTS


class AttrDict(dict):
    """Dictionary with attribute access to valid-python-id keys."""

    def __getattr__(self, name: str):
        """Return dictionary keys as attributes."""
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def attrify(data):
    """Return data with dicts cast to attrdict for dot notation access."""
    if isinstance(data, dict):
        return AttrDict((key, attrify(value)) for key, value in data.items())
    if isinstance(data, list):
        return [attrify(elem) for elem in data]
    return data


def flatten_dotdict(deep: dict, prefix: str = "") -> dict:
    """Flatten dictionary using dot-notation: {a: b: c} => {a.b: c}."""
    flat = {}
    for key, value in deep.items():
        key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten_dotdict(value, prefix=key))
        else:
            flat[key] = value
    return flat


def inflate_dotdict(flat: dict) -> dict:
    """Inflate flat dot-notation dictionary: {a.b: c} => {a: b: c}."""
    deep = node = {}  # type: ignore
    for key, value in flat.items():
        parts = key.split(".")
        path, key = parts[:-1], parts[-1]
        for part in path:
            node = node.setdefault(part, {})
        node[key] = value
        node = deep
    return deep


# FILES

SPOOLED_TMP_MAX_SIZE = 1 << 20  # 1MB

AnyPath = t.Union[str, Path]
AnyFile_ = t.Union[AnyPath, t.IO]


class BinFile:
    """File class for accessing local paths and file-like objects similarly."""

    def __init__(self, file: AnyFile_, mode: str = "rb", metapath: str = "") -> None:
        """Open a file for reading or writing.

        Args:
            file (str|Path|file): The local path to open or a file-like object.
            mode (str, optional): The file opening mode, rb|wb. Default: rb.
            metapath (str, optional): Override metapath attribute if given.
        """
        if mode not in {"rb", "wb"}:
            raise ValueError(f"Invalid file mode: {mode} (expected rb|wb)")
        self.file: t.IO = None  # type: ignore
        self.file_open = False
        self.localpath = None
        self.mode = mode
        mode_func = "readable" if mode == "rb" else "writable"
        if isinstance(file, (str, Path)):
            self.file_open = True
            self.localpath = str(Path(file).resolve())
            file = Path(self.localpath).open(mode=mode)
        if not hasattr(file, mode_func) or not getattr(file, mode_func)():
            raise ValueError(f"File {file!r} is not {mode_func}")
        self.file = file
        self.metapath = metapath or self.localpath

    def __getattr__(self, name: str):
        """Return attrs proxied from the file."""
        return getattr(self.file, name)

    def __iter__(self):
        """Iterate over lines."""
        return self.file.__iter__()

    def __next__(self):
        """Get next line."""
        return self.file.__next__()

    def __enter__(self) -> "BinFile":
        """Enter 'with' context - seek to start if it's a BinaryIO or a TempFile."""
        if self.file.seekable():
            self.file.seek(0)
        return self

    def __exit__(self, exc_cls, exc_val, exc_trace) -> None:
        """Exit 'with' context - close file if it was opened by BinFile."""
        if self.file_open:
            self.file.close()

    def __repr__(self) -> str:
        """Return string representation of the BinFile."""
        file_str = self.metapath or f"{type(self.file).__name__}/{hex(id(self.file))}"
        return f"{type(self).__name__}('{file_str}', mode='{self.mode}')"


AnyFile = t.Union[AnyFile_, BinFile]


def open_any(file: AnyFile, mode: str = "rb") -> BinFile:
    """Return BinFile object as-is or AnyFile loaded as BinFile."""
    if isinstance(file, BinFile):
        if mode != file.mode:
            raise ValueError(f"open_any {mode!r} on a {file.mode!r} BinFile")
        return file
    return BinFile(file, mode=mode)


def fileglob(
    dirpath: AnyPath,
    pattern: str = "*",
    recurse: bool = False,
) -> t.List[Path]:
    """Return the list of files under a given directory.

    Args:
        dirpath (str|Path): The directory path to glob in.
        pattern (str, optional): The glob pattern to match files on. Default: "*".
        recurse (bool, optional): Toggle for enabling recursion. Default: False.

    Returns:
        list[Path]: The file paths that matched the glob within the directory.
    """
    if isinstance(dirpath, str):
        dirpath = Path(dirpath)
    glob_fn = getattr(dirpath, "rglob" if recurse else "glob")
    return list(sorted(f for f in glob_fn(pattern) if f.is_file()))


class TempFile(SpooledTemporaryFile):
    """Spooled tempfile with read/write/seekable() methods and default max size."""

    _file: t.IO

    def __init__(self, **kwargs) -> None:
        """Initialize TempFile with default max size."""
        kwargs.setdefault("max_size", SPOOLED_TMP_MAX_SIZE)
        super().__init__(**kwargs)

    def readable(self) -> bool:
        """Return that the file is readable."""
        return self._file.readable()

    def writable(self) -> bool:
        """Return that the file is writable."""
        return self._file.writable()

    def seekable(self) -> bool:
        """Return that the file is seekable."""
        return self._file.seekable()


class TempDir(TemporaryDirectory):
    """Temporary directory with chdir support."""

    def __init__(self, chdir: bool = False, **kwargs) -> None:
        """Initialize TempDir."""
        super().__init__(**kwargs)
        self.chdir = chdir
        self.cwd = os.getcwd()

    def __enter__(self) -> Path:
        """Return tempdir (and optionally chdir) when entering the context."""
        if self.chdir:
            os.chdir(self.name)
        return Path(self.name)

    def __exit__(self, exc, value, tb) -> None:
        """Restore the CWD if needed when exiting the context."""
        if self.chdir:
            os.chdir(self.cwd)
        self.cleanup()


# CACHING


class Cached:
    """Descriptor for caching attributes and injecting dependencies."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        init: t.Callable,
        args: t.Optional[t.List["Cached"]] = None,
        clear: t.Optional[t.Callable] = None,
        fork_safe: bool = False,
        thread_safe: bool = True,
    ) -> None:
        """Initialize the cached attribute descriptor.

        Args:
            init (callable): The function to init the attribute with on access.
            args (list[Cached]): List of cached attributes to load and pass to
                the init function as arguments for dependency injection.
            clear (callable): Optional callback to tear down the attribute with.
            fork_safe: (bool): Set to True to enable sharing between processes.
            thread_safe: (bool): Set to False disable sharing between threads.
        """
        self.init = init
        self.args = args or []
        self.clear = clear
        if fork_safe and not thread_safe:
            raise ValueError(  # pragma: no cover
                "Thread IDs are only unique within a single process. Using "
                "fork_safe=True and thread_safe=False is not allowed."
            )
        self.fork_safe = fork_safe
        self.thread_safe = thread_safe
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        """Store the descriptor attribute name as defined on the owner class."""
        self.name = name

    def __get__(self, instance, owner: t.Optional[type] = None):
        """Return the initialized attribute (cached)."""
        # accessed as a class attribute - return the descriptor
        if instance is None:
            return self
        # accessed as an instance attribute - return the attribute
        cache = self.get_cache_dict(instance)
        key = self.get_cache_key()
        # initialize the attribute if it's not cached yet
        if key not in cache:
            # dependency injection - pass other cached attrs as args
            args = [arg.__get__(instance, owner) for arg in self.args]
            cache[key] = self.init(*args)
        return cache[key]

    def __set__(self, instance, value) -> None:
        """Set arbitrary attribute value."""
        cache = self.get_cache_dict(instance)
        key = self.get_cache_key()
        cache[key] = value

    def __delete__(self, instance) -> None:
        """Delete the cached attribute."""
        cache = self.get_cache_dict(instance)
        key = self.get_cache_key()
        # tear down the attribute if it's cached
        if key in cache:
            if self.clear:
                self.clear(cache[key])
            # remove from the cache dict and call an explicit del on the attr
            del cache[key]
            del key

    @staticmethod
    def get_cache_dict(instance) -> dict:
        """Return the cache dict of the given instance."""
        return instance.__dict__.setdefault("_cached", {})

    def get_cache_key(self) -> str:
        """Return the cache key based on multiprocess/thread safety."""
        key = f"/{self.name}"
        if not self.fork_safe:
            key = f"{key}/pid:{os.getpid()}"
        if not self.thread_safe:
            key = f"{key}/tid:{threading.get_ident()}"
        return key


# TEMPLATING


class Tokenizer:
    """Simple tokenizer to help parsing patterns."""

    def __init__(self, string: str):
        """Tokenize the given string."""
        self.string = string
        self.index = 0
        self.char: t.Optional[str] = None

    def __iter__(self) -> "Tokenizer":
        """Return tokenizer itself as an iterator."""
        return self

    def __next__(self) -> str:
        """Get the next char or 2 chars if it's escaped."""
        index = self.index
        try:
            char = self.string[index]
        except IndexError as exc:
            raise StopIteration from exc

        if char == "\\":
            index += 1
            try:
                char += self.string[index]
            except IndexError as exc:
                raise ValueError("Pattern ending with backslash") from exc

        self.index = index + 1
        self.char = char
        return char

    def get_until(self, terminals: t.Optional[str] = None) -> str:
        """Get until terminal character or until the end if no terminals specified."""
        result = ""
        for char in self:
            if terminals and char in terminals:
                break
            result += char
        else:
            if terminals:
                raise ValueError(f"missing {terminals}, unterminated pattern")
        return result


# ASSERTING


@functools.singledispatch
def assert_like(  # pylint: disable=unused-argument
    expected, got, allow_extra=True, loc=""
) -> None:
    """Check whether an object is like the expected.

    Supported values:
    * dict: see 'assert_like_dict'
    * list: see 'assert_like_list'
    * regex pattern: see 'assert_like_pattern'
    * callable: see 'assert_like_function'
    * everything else: simply compared using '=='
    """
    assert expected == got, f"{loc}: {got!r} != {expected!r}"


@assert_like.register
def assert_like_dict(expected: dict, got, allow_extra=True, loc="") -> None:
    """Check whether a dictionary is like the expected.

    'allow_extra': enable extra keys in the dictionary or not
    """
    expected_keys = set(expected)
    got_keys = set(got)
    missing_keys = expected_keys - got_keys
    assert not missing_keys, f"{loc}: {missing_keys=}"
    if not allow_extra:
        extra_keys = got_keys - expected_keys
        assert not extra_keys, f"{loc}: {extra_keys=}"
    for key, value in sorted(expected.items()):
        assert_like(value, got[key], allow_extra=allow_extra, loc=f"{loc}.{key}")


@assert_like.register
def assert_like_list(expected: list, got, loc="", **kwargs) -> None:
    """Check whether a list is like the expected.

    Ellipsis can be used for partial matching ([..., 2] == [1, 2]).
    """
    assert isinstance(got, list), f"{loc} {got.__class__.__name__} != list"
    got_iter = iter(got)
    ellipsis = False
    for index, value in enumerate(expected):
        loc_ = f"{loc}[{index}]"
        if value is Ellipsis:
            ellipsis = True
            continue
        for got_ in got_iter:
            try:
                assert_like(value, got_, loc=loc_, **kwargs)
            except AssertionError:
                if not ellipsis:
                    raise
            else:
                ellipsis = False
                break
        else:
            raise AssertionError(f"{loc_}: unexpected end of list")
    if not ellipsis and (extra_items := list(got_iter)):
        raise AssertionError(f"{loc}: unexpected items: {extra_items=}")


@assert_like.register
def assert_like_pattern(expected: re.Pattern, got, loc="", **_) -> None:
    """Check whether a string matches the given pattern."""
    assert expected.search(got), f"{loc}: {got} !~ {expected.pattern}"


@assert_like.register
def assert_like_function(expected: Callable, got, loc="", **_) -> None:
    """Check whether an object is the expected using the callback function."""
    try:
        assert expected(got)
    except Exception as exc:
        ctx = None if isinstance(exc, AssertionError) else exc
        raise AssertionError(f"{loc}: {got} validation failed ({exc})") from ctx


# FILTERING


Filters = t.Optional[t.List[str]]


class BaseFilter(abc.ABC):
    """Base filter class defining the filter interface."""

    @abc.abstractmethod
    def match(self, value) -> bool:
        """Return True if the filter matches value."""


class Filter(BaseFilter):
    """Filter supporting multiple include- and exclude filters."""

    def __init__(
        self,
        factory: t.Dict[str, t.Type["ExpressionFilter"]],
        *,
        include: Filters = None,
        exclude: Filters = None,
        aliases: t.Optional[t.Dict[str, str]] = None,
    ) -> None:
        """Initialize include- and exclude filters from expressions.

        Custom filter {key: class} mapping may be provided with factory.
        """
        parse = functools.partial(parse_expression, factory=factory, aliases=aliases)
        self.include = [parse(expr) for expr in (include or [])]
        self.exclude = [parse(expr) for expr in (exclude or [])]

    # pylint: disable=arguments-differ
    def match(self, value, keys: t.List[str] = None) -> bool:
        """Return whether value matches all includes but none of the excludes.

        If keys is not None, apply only filters of the given keys.
        """
        include = self.include
        exclude = self.exclude
        if keys:
            include = []
            exclude = [filt for filt in exclude if set(filt.keys).issubset(keys)]
        include_match = (i.match(value) for i in include)
        exclude_match = (e.match(value) for e in exclude)
        return (not include or any(include_match)) and not any(exclude_match)

    def __repr__(self) -> str:
        """Return string representation of the filter."""
        cls_name = self.__class__.__name__
        include = ",".join(f"'{filt}'" for filt in self.include)
        exclude = ",".join(f"'{filt}'" for filt in self.exclude)
        return f"{cls_name}(include=[{include}], exclude=[{exclude}])"


class ExpressionFilter(BaseFilter):
    """Expression filter tied to a key, operator and value."""

    def __init__(self, key: str, op: str, value: str) -> None:
        """Initialize an expression filter."""
        if not re.match(fr"^{self.operator_re}$", op):
            raise ValueError(f"Invalid op: {op} (expected {self.operator_re})")
        self.key = key
        self.op = op
        self.value = value

    def __repr__(self) -> str:
        """Return the filter's string representation."""
        cls_name = self.__class__.__name__
        cls_args = self.key, self.op, self.value
        return f"{cls_name}{cls_args!r}"

    def __str__(self) -> str:
        """Return human-readable stringification (the original expression)."""
        return f"{self.key}{self.op}{self.value}"

    @property
    def operator_re(self) -> str:
        """Return regex of allowed operators."""
        return "|".join(OPERATORS)

    def getval(self, value):
        """Return attribute of the value."""
        try:
            return operator.attrgetter(self.key)(value)
        except AttributeError:
            return None


class StringFilter(ExpressionFilter):
    """String filter."""

    operator_re = r"=|!=|=~|!~"
    string: t.Union[str, t.Pattern]

    def __init__(self, key: str, op: str, value: str) -> None:
        """Initialize string filter from a literal or regex pattern."""
        super().__init__(key, op, value)
        if op in ("=", "!="):
            self.string = value
            return
        try:
            self.string = re.compile(value)
        except re.error as exc:
            raise ValueError(f"Invalid pattern: {value} - {exc}") from exc

    def match(self, value: t.Union[str, t.Any]) -> bool:
        """Match str with the filter's regex pattern."""
        string = value if isinstance(value, str) else self.getval(value)
        if string is None:
            return False
        return OPERATORS[self.op](string, self.string)


class SizeFilter(ExpressionFilter):
    """Size filter."""

    operator_re = r"<=|>=|!=|<>|<|>|="

    def __init__(self, key: str, op: str, value: str) -> None:
        """Initialize size filter from a human-readable size."""
        super().__init__(key, op, value)
        self.size = parse_hrsize(value)

    def match(self, value: t.Union[int, t.Any]) -> bool:
        """Compare size to the filter value."""
        size = value if isinstance(value, int) else self.getval(value)
        if size is None:
            return False
        return OPERATORS[self.op](size, self.size)


class TimeFilter(ExpressionFilter):
    """Time filter."""

    operator_re = r"<=|>=|!=|<>|<|>|="
    timestamp_re = (
        r"(?P<year>\d\d\d\d)([-_/]?"
        r"(?P<month>\d\d)([-_/]?"
        r"(?P<day>\d\d)([-_/T ]?"
        r"(?P<hour>\d\d)([-_:]?"
        r"(?P<minute>\d\d)([-_:]?"
        r"(?P<second>\d\d)?)?)?)?)?)?"
    )

    def __init__(self, key: str, op: str, value: str) -> None:
        """Initialize time filter from an iso-format timestamp."""
        super().__init__(key, op, value)
        match = re.match(self.timestamp_re, value)
        if not match:
            raise ValueError(f"Invalid time: {value} (expected YYYY-MM-DD HH:MM:SS)")
        self.time = "".join(part or "" for part in match.groupdict().values())

    def match(self, value: t.Union[int, str, dt.datetime, t.Any]) -> bool:
        """Compare timestamp to the filter value."""
        if not isinstance(value, (str, int, dt.datetime)):
            value = self.getval(value)
        if value is None:
            return False
        if isinstance(value, str):
            time_obj = dt.datetime.fromisoformat(value)
        elif isinstance(value, int):
            time_obj = dt.datetime.fromtimestamp(value)
        elif isinstance(value, dt.datetime):
            time_obj = value
        else:
            raise ValueError(f"Expected int, str or datetime (got {type(value)})")
        time_str = time_obj.strftime("%Y%m%d%H%M%S")
        return OPERATORS[self.op](time_str[: len(self.time)], self.time)


class NumberFilter(ExpressionFilter):
    """Number filter."""

    operator_re = r"<=|>=|!=|<>|<|>|="

    def __init__(self, key: str, op: str, value: str) -> None:
        """Initialize number filter from str value."""
        super().__init__(key, op, value)
        self.num = float(value)

    def match(self, value: t.Union[int, float, t.Any]) -> bool:
        """Compare number to the filter value."""
        value = value if isinstance(value, (int, float)) else self.getval(value)
        if value is None:
            return False
        return OPERATORS[self.op](value, self.num)


class SetFilter(ExpressionFilter):
    """Set filter."""

    operator_re = r"=|!="

    def __init__(self, key: str, op: str, value: str) -> None:
        """Initialize set filter from str value."""
        super().__init__(key, op, value)
        self.item = value

    def match(self, value: t.Union[list, set, t.Any]) -> bool:
        """Return that the given item is in the given list/set."""
        value = value if isinstance(value, (list, set)) else self.getval(value)
        if value is None:
            return False
        return OPERATORS[self.op](self.item in value, True)


class AndFilter(BaseFilter):
    """Logically AND multiple filter expressions."""

    def __init__(self, filters: t.List[ExpressionFilter]) -> None:
        """Initialize AND filter."""
        self.filters = filters
        self.keys = [filt.key for filt in filters]

    def match(self, value: t.Union[int, t.Any]) -> bool:
        """Match value to all filter expressions."""
        return all(filt.match(value) for filt in self.filters)

    def __repr__(self) -> str:
        """Return the filter's string representation."""
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.filters!r})"

    def __str__(self) -> str:
        """Return human-readable stringification (the original expression)."""
        return " & ".join(str(filt) for filt in self.filters)


def parse_expression(
    expression: str,
    factory: t.Dict[str, t.Type[ExpressionFilter]],
    aliases: t.Optional[t.Dict[str, str]] = None,
) -> AndFilter:
    """Parse and return filter from expression string (factory)."""
    aliases = aliases or {}
    factory_keys = [k.pattern if isinstance(k, re.Pattern) else k for k in factory]
    keys = sorted(itertools.chain(factory_keys, aliases.keys()))
    filter_re = fr"({'|'.join(keys)})({'|'.join(OPERATORS)})([^&]*)&?"
    matches = list(re.finditer(filter_re, expression))
    if not matches:
        raise ValueError(f"Invalid filter: {expression} (expected {filter_re})")

    def get_matching_filter_cls(key: str) -> t.Type[ExpressionFilter]:
        for f_key, expr_cls in factory.items():
            if isinstance(f_key, re.Pattern) and f_key.match(key):
                return expr_cls
            if isinstance(f_key, str) and f_key == key:
                return expr_cls
        raise ValueError("Invalid filter key")  # pragma: no cover

    filters = []
    for match in matches:
        key, op, value = match.groups()
        key = aliases.get(key, key)
        filter_cls = get_matching_filter_cls(key)
        filters.append(filter_cls(key, op, value))
    return AndFilter(filters)


def eq_tilde(value: str, pattern: t.Pattern) -> bool:
    """Return True if the regex pattern matches the value."""
    return bool(pattern.search(value))


def ne_tilde(value: str, pattern: t.Pattern) -> bool:
    """Return True if the regex pattern does not match the value."""
    return not eq_tilde(value, pattern)


OPERATORS = {
    "=~": eq_tilde,
    "!~": ne_tilde,
    "<=": operator.le,
    ">=": operator.ge,
    "!=": operator.ne,
    "<>": operator.ne,
    "=": operator.eq,
    "<": operator.lt,
    ">": operator.gt,
}
