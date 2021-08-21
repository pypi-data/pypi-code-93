from myvault.statics.formatted_enum import FormattedEnum


class ExitCode(FormattedEnum):
    INVALID_KEY = "INVALID_KEY_ERROR"
    INVALID_VALUE = "INVALID_VALUE_ERROR"
    SECRET_NOT_FOUND = "SECRET_NOT_FOUND_WARNING"
    INVALID_CONFIG = "INVALID_CONFIG_ERROR"
