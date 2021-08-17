class ConnParserError(Exception):
    """Base exception for this module"""


class CLIError(ConnParserError):
    """Generic exception"""


class ParseError(ConnParserError):
    """Generic exception"""


class FieldParseError(ConnParserError):
    """Generic exception"""


class LoadError(ConnParserError):
    """Generic exception"""


class NotValidConnectionError(ConnParserError):
    """Generic exception"""
