import asyncio
import logging
import os
import pickle
import tarfile
import tempfile
import warnings
import zipfile
from asyncio import AbstractEventLoop
from io import BytesIO as IOReader
from pathlib import Path
from typing import Text, Any, Union, List, Type, Callable, TYPE_CHECKING

import convo.shared.constants
import convo.shared.utils.io

if TYPE_CHECKING:
    from prompt_toolkit.validation import Validate


def config_color_logging(log_level: Text) -> None:
    import coloredlogs

    log_level = log_level or os.environ.get(
        convo.shared.constants.ENVIRONMENT_LOG_LEVEL, convo.shared.constants.CONVO_DEFAULT_LOG_LEVEL
    )

    field_styling = coloredlogs.DEFAULT_FIELD_STYLES.copy()
    field_styling["asctime"] = {}
    level_styling = coloredlogs.DEFAULT_LEVEL_STYLES.copy()
    level_styling["debug"] = {}
    coloredlogs.install(
        level=log_level,
        use_chroot=False,
        fmt="%(asctime)s %(levelname)-8s %(name)s  - %(message)s",
        level_styles=level_styling,
        field_styles=field_styling,
    )


def enable_asynchronous_loop_debugging(
    event_loop: AbstractEventLoop, slow_callback_duration: float = 0.1
) -> AbstractEventLoop:
    logging.info(
        "Enabling coroutine debugging. Loop id {}.".format(id(asyncio.get_event_loop()))
    )

    # Enable debugging
    event_loop.set_debug(True)

    # Make the threshold for "slow" tasks very very small for
    # illustration. The default is 0.1 (= 100 milliseconds).
    event_loop.slow_callback_duration = slow_callback_duration

    # Report all mistakes managing asynchronous resources.
    warnings.simplefilter("always", ResourceWarning)
    return event_loop


def pick_data(filename: Union[Text, Path], obj: Any) -> None:
    """Saves object to file.

    Args:
        filename: the filename to save the object to
        obj: the object to store
    """
    with open(filename, "wb") as f:
        pickle.dump(obj, f)


def pick_load(filename: Union[Text, Path]) -> Any:
    """Loads an object from a file.

    Args:
        filename: the filename to load the object from

    Returns: the loaded object
    """
    with open(filename, "rb") as f:
        return pickle.load(f)


def un_archive(byte_array: bytes, dir: Text) -> Text:
    """Tries to unpack a byte array interpreting it as an archive.

    Tries to use target first to unpack, if that fails, zip will be used."""

    try:
        target = tarfile.open(fileobj=IOReader(byte_array))
        target.extractall(dir)
        target.close()
        return dir
    except tarfile.TarError:
        zip_reference = zipfile.ZipFile(IOReader(byte_array))
        zip_reference.extractall(dir)
        zip_reference.close()
        return dir


def create_temp_file(data: Any, suffix: Text = "", mode: Text = "w+") -> Text:
    """Creates a tempfile.NamedTemporaryFile object for data.

    mode defines NamedTemporaryFile's  mode parameter in py3."""

    encode = None if "b" in mode else convo.shared.utils.io.ENCODING_DEFAULT
    x = tempfile.NamedTemporaryFile(
        mode=mode, suffix=suffix, delete=False, encoding=encode
    )
    x.write(data)

    x.close()
    return x.name


def create_temp_dir() -> Text:
    """Creates a tempfile.TemporaryDirectory."""
    x = tempfile.TemporaryDirectory()
    return x.name


def creating_path(file_path: Text) -> None:
    """Makes sure all directories in the 'file_path' exists."""

    parent_directory = os.path.dirname(os.path.abspath(file_path))
    if not os.path.exists(parent_directory):
        os.makedirs(parent_directory)


def file_type_validation(
    valid_file_types: List[Text], error_message: Text
) -> Type["Validate"]:
    """Creates a `Validate` class which can be used with `questionary` to validate
    file convo_paths.
    """

    def validity_check(path: Text) -> bool:
        return path is not None and any(
            [path.endswith(file_type) for file_type in valid_file_types]
        )

    return creating_validity(validity_check, error_message)


def not_empty_validation(error_message: Text) -> Type["Validate"]:
    """Creates a `Validate` class which can be used with `questionary` to validate
    that the user entered something others than whitespace.
    """

    def validity_check(input: Text) -> bool:
        return input is not None and input.strip() != ""

    return creating_validity(validity_check, error_message)


def creating_validity(
    function: Callable[[Text], bool], error_message: Text
) -> Type["Validate"]:
    """Helper method to create `Validate` classes from callable functions. Should be
    removed when questionary supports `Validate` objects."""

    from prompt_toolkit.validation import Validator, ValidationError
    from prompt_toolkit.document import Document

    class ValidatorFunction(Validator):
        @staticmethod
        def validate(document: Document) -> None:
            validity_check = function(document.text)
            if not validity_check:
                raise ValidationError(message=error_message)

    return ValidatorFunction


def compressed_folder(folder: Text) -> Text:
    """Create an archive from a folder."""
    import shutil

    zip_path = tempfile.NamedTemporaryFile(delete=False)
    zip_path.close()

    # WARN: not thread-safe!
    return shutil.make_archive(zip_path.name, "zip", folder)


def json_un_pickle(filename: Union[Text, Path]) -> Any:
    """Unpickle an object from file using json.

    Args:
        filename: the file to load the object from

    Returns: the object
    """
    import jsonpickle.ext.numpy as jsonpickle_numpy
    import jsonpickle

    jsonpickle_numpy.register_handlers()

    file_matter = convo.shared.utils.io.read_file(filename)
    return jsonpickle.loads(file_matter)


def dictionary_pickle(filename: Union[Text, Path], obj: Any) -> None:
    """Pickle an object to a file using json.

    Args:
        filename: the file to store the object to
        obj: the object to store
    """
    import jsonpickle.ext.numpy as jsonpickle_numpy
    import jsonpickle

    jsonpickle_numpy.register_handlers()

    convo.shared.utils.io.writing_text_file(jsonpickle.dumps(obj), filename)
