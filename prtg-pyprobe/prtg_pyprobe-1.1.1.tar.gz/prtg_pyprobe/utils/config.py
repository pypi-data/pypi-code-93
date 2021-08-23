import json
import logging
import os
import traceback
import uuid
from pathlib import Path

import regex
import yaml
from prompt_toolkit.validation import Validator, ValidationError

from prtg_pyprobe.utils.validators import (
    validation,
    validation_schemes,
    ValidationFailedError,
)


class IPDNSValidator(Validator):
    def validate(self, document):
        """Check if input is a IP address or DNS name.

        Args:
            document: ``prompt`` toolkit document.

        Raises:
            ValidationError: If the document does not match validation rule.

        """
        ip_dns_ok = regex.match(
            r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|"
            r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)+([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$",
            document.text,
        )
        if not ip_dns_ok or document.text == "":
            raise ValidationError(
                message="Please Enter a valid IP/DNS name.",
                cursor_position=len(document.text),
            )


class DirectoryWriteableValidator(Validator):
    def validate(self, document):
        """Check if input directory is writeable.

        Args:
            document: ``prompt`` toolkit document.

        Raises:
            ValidationError: If the document does not match validation rule.

        """
        if document.text:
            try:
                os.chdir(Path(document.text).parent)
                f = open(document.text, "w+")
                f.write("This is your logfile")
                f.close()
            except PermissionError:
                raise ValidationError(
                    message="Please specify a path that is writeable for the user running the probe",
                    cursor_position=len(document.text),
                )
            except IsADirectoryError:
                raise ValidationError(
                    message='Please specify a directory and filename that is writeable i.e.  "~/somefolder/probe.log"',
                    cursor_position=len(document.text),
                )
        else:
            print("Empty string specified, no logfile will be saved and logs will be printed to stdout!")


class PortRangeValidator(Validator):
    def validate(self, document):
        """Check if integer is between 1 and 65535.

        Args:
            document: ``prompt`` toolkit document.

        Raises:
            ValidationError: If the document does not match validation rule.

        """
        port_ok = True
        try:
            port_number = int(document.text)
            if not 0 < port_number < 65536:
                port_ok = False
        except ValueError:
            port_ok = False
        if not port_ok or document.text == "":
            raise ValidationError(
                message="Please enter a valid port in the range 1 - 65535.",
                cursor_position=len(document.text),
            )


class GUIDValidator(Validator):
    def validate(self, document):
        """Check if string is valid GUID.

        Args:
            document: ``prompt`` toolkit document.

        Raises:
            ValidationError: If the document does not match validation rule.

        """
        guid_ok = regex.match(
            r"([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}){1}",
            document.text,
        )
        if not guid_ok or document.text == "":
            raise ValidationError(
                message="Probe GID has to be in GUID Format",
                cursor_position=(len(document.text)),
            )


class BaseIntervalValidator(Validator):
    def validate(self, document):
        """Check if input interval is between 60 and 300 seconds.

        Args:
            document: ``prompt`` toolkit document.

        Raises:
            ValidationError: If the document does not match validation rule,

        """
        interval_ok = True
        try:
            interval = int(document.text)
            if not 59 < interval < 301:
                interval_ok = False
        except ValueError:
            interval_ok = False
        if not interval_ok or document.text == "":
            raise ValidationError(
                message="Interval has to be between 60 and 300.",
                cursor_position=(len(document.text)),
            )


class BaseChunkSizeValidator(Validator):
    def validate(self, document):
        chunk_size_ok = True
        try:
            chunk_size = int(document.text)
            if not 5 < chunk_size < 50:
                chunk_size_ok = False
        except ValueError:
            chunk_size_ok = False
        if not chunk_size_ok or document.text == "":
            raise ValidationError(
                message="Chunk Size has to be between 5 and 50.",
                cursor_position=(len(document.text)),
            )


class NotEmptyValidator(Validator):
    def validate(self, document):
        """Check if input is empty.

        Args:
            document: ``prompt`` toolkit document.

        Raises:
            ValidationError: If the document does not match validation rule.

        """
        if document.text == "":
            raise ValidationError(message="Input cannot be empty.", cursor_position=len(document.text))


class ProbeConfig(object):
    """An object representing the probe config providing read and write functions."""

    def __init__(self, path: str):
        """Constructor of ProbeConfig.

        Args:
            path (str): The path to the config file.

        """
        self.config_path = path

    def write(self, config_data: dict):
        """Write the given config data to the path provided to the constructor.

        Args:
            config_data (dict): Config data as dict.

        """
        with open(self.config_path, "w") as f:
            yaml.dump(config_data, f)

    def read(self) -> dict:
        """Read the config from file or ENV.

        Returns:
            dict: Config as dict.

        Raises:
            ValidationFailedError: Is raised when config can not be validated.
            KeyError: Is raised when there is no config in the ENV.

        """
        try:
            with open(self.config_path, "r") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
            return config
        except FileNotFoundError:
            try:
                # todo: think about different variables instead of one which holds json
                logging.info("No config file found, attempting to read from ENV!")
                env_probe_conf = os.environ["PROBE_CONFIG"]
                try:
                    config = validation(
                        val=json.loads(env_probe_conf),
                        scheme=validation_schemes["ProbeConfig"],
                    )
                    return config
                except ValidationFailedError:
                    logging.error(traceback.format_exc())
                    logging.error("Loading of config from ENV failed. Wrong Format!")
                    raise
            except KeyError:
                logging.error("There is no config in ENV!")
                raise


configuration_questions = [
    {
        "type": "input",
        "name": "log_file_location",
        "message": "Where do you want the log file to be saved? (empty means logs will be sent to stdout)",
        "default": "/var/log/pyprobe/pyprobe.log",
        "validate": DirectoryWriteableValidator,
    },
    {
        "type": "input",
        "name": "prtg_server_ip_dns",
        "message": "IP or DNS of your PRTG Server:",
        "validate": IPDNSValidator,
    },
    {
        "type": "input",
        "name": "prtg_server_port",
        "message": "The port your PRTG server, listens for mini probe connections (only HTTPS connection allowed):",
        "default": "443",
        "validate": PortRangeValidator,
    },
    {
        "type": "input",
        "name": "probe_gid",
        "message": "Probe Gid (GUID/UUID):",
        "default": str(uuid.uuid4()).upper(),
        "validate": GUIDValidator,
    },
    {
        "type": "input",
        "name": "probe_access_key",
        "message": "The access key as defined on the PRTG Server:",
        "validate": NotEmptyValidator,
    },
    {
        "type": "input",
        "name": "probe_name",
        "message": "The name of the probe:",
        "default": "Python Mini Probe",
        "validate": NotEmptyValidator,
    },
    {
        "type": "input",
        "name": "probe_base_interval",
        "message": "The base interval for sensor in seconds (only values between 60 and 300 supported):",
        "default": "60",
        "validate": BaseIntervalValidator,
    },
    {
        "type": "input",
        "name": "probe_task_chunk_size",
        "message": "The task chunk size, default 20, powerful machines may be able to handle more "
        "(only values between 5 and 50 supported):",
        "default": "20",
        "validate": BaseChunkSizeValidator,
    },
    {
        "type": "list",
        "name": "log_level",
        "message": "What level of logging do you want?",
        "choices": ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
    },
    {
        "type": "confirm",
        "message": "Do you want to turn off Certificate Validation for connections to the PRTG Core? "
        "(recommended when using a self signed certificate)",
        "name": "disable_ssl_verification",
        "default": True,
    },
]
