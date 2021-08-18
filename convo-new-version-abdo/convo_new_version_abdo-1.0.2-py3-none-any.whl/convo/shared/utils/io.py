from collections import OrderedDict
import errno
import glob
from hashlib import md5
from io import StringIO
import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Text, Type, Union
import warnings

from ruamel import yaml as yaml
from ruamel.yaml import RoundTripRepresenter, YAMLError
from ruamel.yaml.constructor import DuplicateKeyError

from convo.shared.constants import (
    CONVO_DEFAULT_LOG_LEVEL,
    ENVIRONMENT_LOG_LEVEL ,
    NEXT_MAJOR_DEPRECATION_VERSION,
)
from convo.shared.exceptions import YamlSyntaxExceptions 

ENCODING_DEFAULT = "utf-8"
YAML_VER = (1, 2)


class bcolours:
    HEADER_NAME = "\033[95m"
    OK_BLUE = "\033[94m"
    OK_GREEN = "\033[92m"
    WARN = "\033[93m"
    FAILED = "\033[91m"
    ENDC = "\033[0m"
    BOLD_STYLE = "\033[1m"
    UNDER_LINE = "\033[4m"


def wrapping_with_color(*args: Any, color: Text) -> Text:
    return color + " ".join(str(s) for s in args) + bcolours.ENDC


def raising_warning(
    message: Text,
    category: Optional[Type[Warning]] = None,
    docs: Optional[Text] = None,
    **kwargs: Any,
) -> None:
    """Emit a `warnings.warn` with sensible defaults and a colored warning msg."""

    original_formatter = warnings.formatwarning

    def show_source_line() -> bool:
        if "stacklevel" not in kwargs:
            if category == UserWarning or category is None:
                return False
            if category == FutureWarning:
                return False
        return True

    def format_warning(
        message: Text,
        category: Optional[Type[Warning]],
        filename: Text,
        lineno: Optional[int],
        sentence: Optional[Text] = None,
    ):
        """Function to format a warning the standard way."""

        if not show_source_line():
            if docs:
                sentence = f"More info at {docs}"
            else:
                sentence = ""

        formatted_msg = original_formatter(
            message, category, filename, lineno, sentence
        )
        return wrapping_with_color(formatted_msg, color=bcolours.WARN)

    if "stacklevel" not in kwargs:
        # try to set useful defaults for the most common warning categories
        if category == DeprecationWarning:
            kwargs["stacklevel"] = 3
        elif category in (UserWarning, FutureWarning):
            kwargs["stacklevel"] = 2

    warnings.formatwarning = format_warning
    warnings.warn(message, category=category, **kwargs)
    warnings.formatwarning = original_formatter


def writing_text_file(
    content: Text,
    file_path: Union[Text, Path],
    encoding: Text = ENCODING_DEFAULT,
    append: bool = False,
) -> None:
    """Writes text to a file.

    Args:
        content: The content to write.
        file_path: The path to which the content should be written.
        encoding: The encoding which should be used.
        append: Whether to append to the file or to truncate the file.

    """
    method = "a" if append else "w"
    with open(file_path, method, encoding=encoding) as file:
        file.write(content)


def read_file(filename: Union[Text, Path], encoding: Text = ENCODING_DEFAULT) -> Any:
    """Read text from a file."""

    try:
        with open(filename, encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"File '{filename}' does not exist.")


def reading_json_file(filename: Union[Text, Path]) -> Any:
    """Read json from a file."""
    matter = read_file(filename)
    try:
        return json.loads(matter)
    except ValueError as e:
        raise ValueError(
            "Failed to read json from '{}'. Error: "
            "{}".format(os.path.abspath(filename), e)
        )


def list_dir(path: Text) -> List[Text]:
    """Returns all files and folders excluding hidden files.

    If the path points to a file, returns the file. This is a recursive
    implementation returning files in any depth of the path."""

    if not isinstance(path, str):
        raise ValueError(
            "`resource_name` must be a string type. "
            "Got `{}` instead".format(type(path))
        )

    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        res = []
        for base, dirs, filename in os.walk(path, followlinks=True):
            # sort files for same order across runs
            filename = sorted(filename, key=file_name_without_prefix)
            # add not hidden files
            acceptable_files = filter(lambda x: not x.startswith("."), filename)
            res.extend(os.path.join(base, f) for f in acceptable_files)
            # add not hidden directories
            good_dirs = filter(lambda x: not x.startswith("."), dirs)
            res.extend(os.path.join(base, f) for f in good_dirs)
        return res
    else:
        raise ValueError(
            "Could not locate the resource '{}'.".format(os.path.abspath(path))
        )


def listing_files(path: Text) -> List[Text]:
    """Returns all files excluding hidden files.

    If the path points to a file, returns the file."""

    return [fn for fn in list_dir(path) if os.path.isfile(fn)]


def file_name_without_prefix(file: Text) -> Text:
    """Splits of a filenames prefix until after the first ``_``."""
    return "_".join(file.split("_")[1:])


def list_sub_dirs(path: Text) -> List[Text]:
    """Returns all folders excluding hidden files.

    If the path points to a file, returns an empty list."""

    return [fn for fn in glob.glob(os.path.join(path, "*")) if os.path.isdir(fn)]


def fetch_text_hashcode(text: Text, encoding: Text = ENCODING_DEFAULT) -> Text:
    """Calculate the md5 hash for a text."""
    return md5(text.encode(encoding)).hexdigest()


def json_to_str(obj: Any, **kwargs: Any) -> Text:
    indent = kwargs.pop("indent", 2)
    ascii_ensured = kwargs.pop("ascii_ensured", False)
    return json.dumps(obj, indent=indent, ensure_ascii=ascii_ensured, **kwargs)


def fixing_yaml_loader() -> None:
    """Ensure that any string read by yaml is represented as unicode."""

    def constructing_yaml_string(self, node):
        # Override the default string handling function
        # to always return unicode objects
        return self.construct_scalar(node)

    yaml.Loader.add_constructor("tag:yaml.org,2002:str", constructing_yaml_string)
    yaml.SafeLoader.add_constructor("tag:yaml.org,2002:str", constructing_yaml_string)


def replace_env_variables() -> None:
    """Enable yaml loader to process the environment variables in the yaml."""
    # eg. ${USER_NAME}, ${PASSWORD}
    env_variable_pattern = re.compile(r"^(.*)\$\{(.*)\}(.*)$")
    yaml.add_implicit_resolver("!env_var", env_variable_pattern)

    def env_variable_constructor(loader, node):
        """Process environment variables found in the YAML."""
        val = loader.construct_scalar(node)
        expanded_variables = os.path.expandvars(val)
        if "$" in expanded_variables:
            expanded_not = [w for w in expanded_variables.split() if "$" in w]
            raise ValueError(
                "Error when trying to expand the environment variables"
                " in '{}'. Please make sure to also set these environment"
                " variables: '{}'.".format(val, expanded_not)
            )
        return expanded_variables

    yaml.SafeConstructor.add_constructor("!env_var", env_variable_constructor)


def reading_yaml(matter: Text, reader_type: Union[Text, List[Text]] = "safe") -> Any:
    """Parses yaml from a text.

    Args:
        matter: A text containing yaml content.
        reader_type: Reader type to use. By default "safe" will be used

    Raises:
        ruamel.yaml.parser.ParserError: If there was an error when parsing the YAML.
    """
    fixing_yaml_loader()

    replace_env_variables()

    parser_yaml = yaml.YAML(typ=reader_type)
    parser_yaml.version = YAML_VER
    parser_yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = False

    if ascii_check(matter):
        # Required to make sure emojis are correctly parsed
        matter = (
            matter.encode("utf-8")
            .decode("raw_unicode_escape")
            .encode("utf-16", "surrogatepass")
            .decode("utf-16")
        )

    return parser_yaml.load(matter) or {}


def ascii_check(text: Text) -> bool:
    return all(ord(character) < 128 for character in text)


def reading_yaml_file(filename: Union[Text, Path]) -> Union[List[Any], Dict[Text, Any]]:
    """Parses a yaml file.

    Raises an exception if the content of the file can not be parsed as YAML.

    Args:
        filename: The path to the file which should be read.

    Returns:
        Parsed content of the file.
    """
    try:
        return reading_yaml(read_file(filename, ENCODING_DEFAULT))
    except (YAMLError, DuplicateKeyError) as e:
        raise YamlSyntaxExceptions (filename, e)


def writing_yaml(
    data_set: Any,
    target: Union[Text, Path, StringIO],
    should_preserve_key_order: bool = False,
) -> None:
    """Writes a yaml to the file or to the stream

    Args:
        data_set: The data to write.
        target: The path to the file which should be written or a stream object
        should_preserve_key_order: Whether to force preserve key order in `data`.
    """
    enabled_ordered_dictionary_yaml_dumping()

    if should_preserve_key_order:
        data_set = convert_to_ordered_dictionary(data_set)

    data_dumper = yaml.YAML()
    # no wrap lines
    data_dumper.width = YAML_MAX_WIDTH

    # use `null` to represent `None`
    data_dumper.representer.add_representer(
        type(None),
        lambda self, _: self.represent_scalar("tag:yaml.org,2002:null", "null"),
    )

    if isinstance(target, StringIO):
        data_dumper.dump(data_set, target)
        return

    with Path(target).open("w", encoding=ENCODING_DEFAULT) as outfile:
        data_dumper.dump(data_set, outfile)


YAML_MAX_WIDTH = 4096


def convert_to_ordered_dictionary(obj: Any) -> Any:
    """Convert object to an `OrderedDict`.

    Args:
        obj: Object to convert.

    Returns:
        An `OrderedDict` with all nested dictionaries converted if `obj` is a
        dictionary, otherwise the object itself.
    """
    if isinstance(obj, OrderedDict):
        return obj
    # use recursion on lists
    if isinstance(obj, list):
        return [convert_to_ordered_dictionary(element) for element in obj]

    if isinstance(obj, dict):
        output = OrderedDict()
        # use recursion on dictionaries
        for k, v in obj.items():
            output[k] = convert_to_ordered_dictionary(v)

        return output

    # return all others objects
    return obj


def enabled_ordered_dictionary_yaml_dumping() -> None:
    """Ensure that `OrderedDict`s are dumped so that the order of keys is respected."""
    yaml.add_representer(
        OrderedDict,
        RoundTripRepresenter.represent_dict,
        representer=RoundTripRepresenter,
    )


def logging_disabled_check() -> bool:
    """Returns `True` if log level is set to WARNING or ERROR, `False` otherwise."""
    logging_level = os.environ.get(ENVIRONMENT_LOG_LEVEL , CONVO_DEFAULT_LOG_LEVEL)

    return logging_level in ("ERROR", "WARNING")


def create_dir_from_file(file_path: Union[Text, Path]) -> None:
    """Creates any missing parent directories of this file path."""

    create_dir(os.path.dirname(file_path))


def dump_object_as_json_to_file(filename: Union[Text, Path], obj: Any) -> None:
    """Dump an object as a json string to a file."""

    writing_text_file(json.dumps(obj, indent=2), filename)


def dump_object_as_yaml_to_str(
    obj: Any, should_preserve_key_order: bool = False
) -> Text:
    """Writes data (python dict) to a yaml string.

    Args:
        obj: The object to dump. Has to be serializable.
        should_preserve_key_order: Whether to force preserve key order in `data`.

    Returns:
        The object converted to a YAML string.
    """
    buffer_str = StringIO()

    writing_yaml(obj, buffer_str, should_preserve_key_order=should_preserve_key_order)

    return buffer_str.getvalue()


def create_dir(directory_path: Text) -> None:
    """Creates a dir and its super convo_paths.

    Succeeds even if the path already exists."""

    try:
        os.makedirs(directory_path)
    except OSError as e:
        # be happy if someone already created the path
        if e.errno != errno.EEXIST:
            raise


def rasing_deprecate_warning(
    msg: Text,
    warn_until_version: Text = NEXT_MAJOR_DEPRECATION_VERSION,
    docs: Optional[Text] = None,
    **kwargs: Any,
) -> None:
    """
    Thin wrapper around `raise_warning()` to raise a deprecation warning. It requires
    a version until which we'll warn, and after which the support for the feature will
    be removed.
    """
    if warn_until_version not in msg:
        msg = f"{msg} (will be removed in {warn_until_version})"

    # need the correct stacklevel now
    kwargs.setdefault("stacklevel", 3)
    # we're raising a `FutureWarning` instead of a `DeprecationWarning` because
    # we want these warnings to be visible in the terminal of our users
    # https://docs.python.org/3/library/warnings.html#warning-categories
    raising_warning(msg, FutureWarning, docs, **kwargs)


def read_configuration_file(filename: Union[Path, Text]) -> Dict[Text, Any]:
    """Parses a yaml configuration file. Content needs to be a dictionary

    Args:
        filename: The path to the file which should be read.
    """
    matter = reading_yaml_file(filename)

    if matter is None:
        return {}
    elif isinstance(matter, dict):
        return matter
    else:
        raise YamlSyntaxExceptions (
            filename,
            ValueError(
                f"Tried to load configuration file '{filename}'. "
                f"Expected a key value mapping but found a {type(matter).__name__}"
            ),
        )


def is_sub_dir(path_flow: Text, potential_parent_dir: Text) -> bool:
    if path_flow is None or potential_parent_dir is None:
        return False

    path_flow = os.path.abspath(path_flow)
    potential_parent_dir = os.path.abspath(potential_parent_dir)

    return potential_parent_dir in path_flow
