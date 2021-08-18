import logging
import os
from typing import Text, Dict, List, Optional, Any

from packaging import version
from packaging.version import LegacyVersion
from pykwalify.errors import SchemaError

from ruamel.yaml.constructor import DuplicateKeyError

import convo.shared
from convo.shared.exceptions import YamlExceptions , YamlSyntaxExceptions 
import convo.shared.utils.io
from convo.shared.constants import (
    TRAINING_DATA_DOCUMENTS_URL,
    PACKAGING_NAME,
    TRAINING_DATA_LATEST_FORMAT_VERSION ,
    EXTENSIONS_SCHEMA_FILE,
    RESPONSE_SCHEMA_FILE,
)

log = logging.getLogger(__name__)

KEY_TRAINING_DATA_FORMAT_VER = "version"


class YamlValidationExceptionRaise(YamlExceptions , ValueError):
    """Raised if a yaml file does not correspond to the expected schema."""

    def __init__(
        self,
        message: Text,
        validation_errors: Optional[List[SchemaError.SchemaErrorEntry]] = None,
        filename: Optional[Text] = None,
        content: Any = None,
    ) -> None:
        """Create The Error.

        Args:
            message: error message
            validation_errors: validation errors
            filename: name of the file which was validated
            content: yaml content loaded from the file (used for line information)
        """
        super(YamlValidationExceptionRaise, self).__init__(filename)

        self.message = message
        self.validation_errors = validation_errors
        self.content = content

    def __str__(self) -> Text:
        message = ""
        if self.filename:
            message += f"Failed to validate '{self.filename}'. "
        else:
            message += "Failed to validate YAML. "
        message += self.message
        if self.validation_errors:
            distinct_errors = {}
            for error in self.validation_errors:
                line_no = self.line_no_for_path(self.content, error.path)

                if line_no and self.filename:
                    error_representation = f"  in {self.filename}:{line_no}:\n"
                elif line_no:
                    error_representation = f"  in Line {line_no}:\n"
                else:
                    error_representation = ""

                error_representation += f"      {error}"
                distinct_errors[str(error)] = error_representation
            error_message = "\n".join(distinct_errors.values())
            message += f":\n{error_message}"
        return message

    def line_no_for_path(self, current: Any, path: Text) -> Optional[int]:
        """Get line number for a yaml path in the current content.

        Implemented using recursion: algorithm goes down the path navigating to the
        leaf in the YAML tree. Unfortunately, not all nodes returned from the
        ruamel yaml parser have line numbers attached (arrays have them, dicts have
        them), e.g. strings don't have attached line numbers.
        If we arrive at a node that has no line number attached, we'll return the
        line number of the parent - that is as close as it gets.

        Args:
            current: current content
            path: path to traverse within the content

        Returns:
            the line number of the path in the content.
        """
        if not current:
            return None

        line = current.lc.line + 1 if hasattr(current, "lc") else None

        if not path:
            return line

        if "/" in path:
            line_head, line_tail = path.split("/", 1)
        else:
            line_head, line_tail = path, ""

        if line_head:
            if isinstance(current, dict) and line_head in current:
                return self.line_no_for_path(current[line_head], line_tail) or line
            elif isinstance(current, list) and line_head.isdigit():
                return self.line_no_for_path(current[int(line_head)], line_tail) or line
            else:
                return line
        return self.line_no_for_path(current, line_tail) or line


def validating_yaml_schema(yaml_file_content: Text, schema_path: Text) -> None:
    """
    Validate yaml content.

    Args:
        yaml_file_content: the content of the yaml file to be validated
        schema_path: the schema of the yaml file
    """
    from pykwalify.core import Core
    from pykwalify.errors import SchemaError
    from ruamel.yaml import YAMLError
    import pkg_resources
    import logging

    log_data = logging.getLogger("pykwalify")
    log_data.setLevel(logging.CRITICAL)

    try:
        # we need "rt" since
        # it will add meta information to the parsed output. this meta information
        # will include e.g. at which line an object was parsed. this is very
        # helpful when we validate files later on and want to point the user to the
        # right line
        source_data_set = convo.shared.utils.io.reading_yaml(
            yaml_file_content, reader_type=["safe", "rt"]
        )
    except (YAMLError, DuplicateKeyError) as e:
        raise YamlSyntaxExceptions (underlying_yaml_exception=e)

    file_for_schema = pkg_resources.resource_filename(PACKAGING_NAME, schema_path)
    schema_utility_file = pkg_resources.resource_filename(
        PACKAGING_NAME, RESPONSE_SCHEMA_FILE
    )
    db_schema_extensions = pkg_resources.resource_filename(
        PACKAGING_NAME, EXTENSIONS_SCHEMA_FILE
    )

    d = Core(
        source_data=source_data_set,
        schema_files=[file_for_schema, schema_utility_file],
        extensions=[db_schema_extensions],
    )

    try:
        d.validate(raise_exception=True)
    except SchemaError:
        raise YamlValidationExceptionRaise(
            "Please make sure the file is correct and all "
            "mandatory parameters are specified. Here are the errors "
            "found during validation",
            d.errors,
            content=source_data_set,
        )


def validating_training_data(json_data: Dict[Text, Any], schema: Dict[Text, Any]) -> None:
    """Validate convo training data format to ensure proper training.

    Args:
        json_data: the data to validate
        schema: the schema

    Raises:
        ValidationError if validation fails.
    """
    from jsonschema import validate
    from jsonschema import ValidationError

    try:
        validate(json_data, schema)
    except ValidationError as e:
        e.msg += (
            f". Failed to validate data, make sure your data "
            f"is valid. For more information about the format visit "
            f"{TRAINING_DATA_DOCUMENTS_URL}."
        )
        raise e


def validating_training_data_format_version(
    yaml_file_content: Dict[Text, Any], file_name: Optional[Text]
) -> bool:
    """Validates version on the training data content using `version` field
       and warns users if the file is not compatible with the current version of
       Convo Open Source.

    Args:
        yaml_file_content: Raw content of training data file as a dictionary.
        file_name: Name of the validated file.

    Returns:
        `True` if the file can be processed by current version of Convo Open Source,
        `False` otherwise.
    """

    if file_name:
        file_name = os.path.abspath(file_name)

    if not isinstance(yaml_file_content, dict):
        raise YamlValidationExceptionRaise(
            "YAML content in is not a mapping, can not validate training "
            "data schema version.",
            filename=file_name,
        )

    version_val = yaml_file_content.get(KEY_TRAINING_DATA_FORMAT_VER)

    if not version_val:
        # not raising here since it's not critical
        log.info(
            f"The '{KEY_TRAINING_DATA_FORMAT_VER}' key is missing in "
            f"the training data file {file_name}. "
            f"Convo Open Source will read the file as a "
            f"version '{TRAINING_DATA_LATEST_FORMAT_VERSION }' file. "
            f"See {TRAINING_DATA_DOCUMENTS_URL}."
        )
        return True

    try:
        parsed_ver = version.parse(version_val)
        if isinstance(parsed_ver, LegacyVersion):
            raise TypeError

        if version.parse(TRAINING_DATA_LATEST_FORMAT_VERSION ) >= parsed_ver:
            return True

    except TypeError:
        convo.shared.utils.io.raising_warning(
            f"Training data file {filename} must specify "
            f"'{KEY_TRAINING_DATA_FORMAT_VER}' as string, for example:\n"
            f"{KEY_TRAINING_DATA_FORMAT_VER}: '{TRAINING_DATA_LATEST_FORMAT_VERSION }'\n"
            f"Convo Open Source will read the file as a "
            f"version '{TRAINING_DATA_LATEST_FORMAT_VERSION }' file.",
            docs=TRAINING_DATA_DOCUMENTS_URL,
        )
        return True

    convo.shared.utils.io.raising_warning(
        f"Training data file {file_name} has a greater "
        f"format version than your Convo Open Source installation: "
        f"{version_value} > {TRAINING_DATA_LATEST_FORMAT_VERSION }. "
        f"Please consider updating to the latest version of Convo Open Source."
        f"This file will be skipped.",
        docs=TRAINING_DATA_DOCUMENTS_URL,
    )
    return False
