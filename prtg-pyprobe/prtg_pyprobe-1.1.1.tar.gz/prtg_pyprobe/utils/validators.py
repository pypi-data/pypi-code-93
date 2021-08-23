import functools
from typing import Any

from cerberus import Validator

unit_kind_allowed = [
    "BytesBandwidth",
    "BytesMemory",
    "BytesDisk",
    "BytesFile",
    "TimeResponse",
    "TimeSeconds",
    "TimeHours",
    "Temperature",
    "Percent",
    "Count",
    "CPU",
    "Custom",
]
field_type_allowed = ["edit", "integer", "password", "radio"]
log_level_allowed = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

validation_schemes = {
    "SensorDefinitionGroupField": {
        "name": {"type": "string", "required": True, "empty": False},
        "type": {
            "type": "string",
            "required": True,
            "allowed": field_type_allowed,
            "empty": False,
        },
        "caption": {"type": "string", "required": True, "empty": False},
        "required": {"type": "string", "allowed": ["yes", "1", "true"]},
        "help": {"type": "string"},
        "default": {"type": ["string", "integer"]},
        "minimum": {"type": "integer"},
        "maximum": {"type": "integer"},
        "options": {
            "type": "dict",
            "keysrules": {"type": "string"},
            "valuesrules": {"type": "string"},
        },
    },
    "SensorDefinitionGroup": {
        "name": {
            "type": "string",
            "required": True,
            "empty": False,
            "regex": "^[a-z0-9_-]{5,40}",
        },
        "caption": {"type": "string", "required": True, "empty": False},
        "fields": {"type": "list", "required": False, "empty": True},
    },
    "SensorDefinition": {
        "name": {"type": "string", "required": True, "empty": False},
        "kind": {"type": "string", "required": True, "empty": False},
        "description": {"type": "string", "required": True, "empty": False},
        "help": {"type": "string", "required": True, "empty": False},
        "tag": {"type": "string", "required": True, "empty": False},
        "default": {"type": "string", "allowed": ["yes", "1", "true"]},
        "groups": {"type": "list", "required": True, "empty": True},
    },
    "SensorData": {
        "sensorid": {"type": "string", "required": True, "empty": False},
        "message": {"type": "string"},
        "channel": {"type": "list"},
        "error": {"type": "string", "dependencies": ["message", "code"]},
        "code": {"type": "integer"},
    },
    "SensorProbeData": {
        "sensorid": {"type": "string", "required": True, "empty": False},
        "message": {"type": "string"},
        "channel": {"type": "list"},
        "error": {"type": "string", "dependencies": ["message", "code"]},
        "code": {"type": "integer"},
    },
    "SensorDataChannel": {
        "name": {"type": "string", "required": True, "empty": False},
        "mode": {
            "type": "string",
            "required": True,
            "allowed": ["integer", "float", "counter"],
            "empty": False,
        },
        "value": {"type": ["integer", "float"]},
        "unit": {"type": "string", "allowed": unit_kind_allowed},
        "kind": {"type": "string", "allowed": unit_kind_allowed},
        "customunit": {"type": "string"},
    },
    "ProbeConfig": {
        "log_file_location": {"type": "string", "empty": True},
        "log_level": {"type": "string", "allowed": log_level_allowed, "empty": False},
        "disable_ssl_verification": {"type": "boolean", "empty": False},
        "probe_access_key": {"type": "string", "empty": False},
        "probe_access_key_hashed": {"type": "string", "empty": False},
        "probe_base_interval": {"type": "string", "empty": False},
        "probe_task_chunk_size": {"type": "string", "empty": False},
        "probe_gid": {
            "type": "string",
            "empty": False,
            "regex": "([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}){1}",
        },
        "probe_name": {"type": "string", "empty": False},
        "probe_protocol_version": {"type": "string", "empty": False, "allowed": ["1"]},
        "prtg_server_ip_dns": {"type": "string", "empty": False},
        "prtg_server_port": {"type": "string", "empty": False},
    },
}


class ValidationFailedError(Exception):
    """Raised when validation against scheme failed."""

    def __init__(self, validator):
        """Constructor of ValidationFailedError.

        Args:
            validator (cerberus.validator): Cerberus validator.

        """
        self._validator = validator
        self._message = self._validator.errors
        super().__init__(self._message)


class ValidationNotPossibleError(Exception):
    """Raised when validation is not possible."""

    def __init__(self):
        super().__init__("Cannot validate, no validation schema defined.")


def validate(func: Any):
    """Decorator to validate dictionaries.

    Args:
        func (Any): Decorated function.

    Returns:
        Any: Wrapped function.

    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        try:
            schema = validation_schemes[type(args[0]).__name__]
        except KeyError:
            raise ValidationNotPossibleError
        return validation(value, schema)

    return wrapper


def validation(val: dict, scheme: dict) -> dict:
    """Validation of a dict against a cerberus scheme.

    Args:
        val (dict): Input dictionary.
        scheme (dict): Cerberus validation scheme.

    Returns:
        dict: Input dictionary if validation succeeded.

    Raises:
        ValidationFailedError: Raised if the validation fails.
    """
    v = Validator(scheme)
    if v.validate(val):
        return val
    else:
        raise ValidationFailedError(v)
