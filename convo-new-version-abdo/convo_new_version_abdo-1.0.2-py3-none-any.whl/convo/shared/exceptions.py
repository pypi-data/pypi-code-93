from typing import Optional, Text


class ConvoExceptions(Exception):
    """Base exception class for all errors raised by Convo Open Source."""


class CoreException (ConvoExceptions):
    """Basic exception for errors raised by Convo Core."""


class XTermsError (ConvoExceptions ):
    """Error in case the user didn't accept the Convo X terms."""


class YamlExceptions (ConvoExceptions ):
    """Raised if there is an error reading yaml."""

    def __init__(self, filename: Optional[Text] = None) -> None:
        """Create exception.

        Args:
            filename: optional file the error occurred in"""
        self.filename = filename


class YamlSyntaxExceptions (YamlExceptions ):
    """Raised when a YAML file can not be parsed properly due to a syntax error."""

    def __init__(
        self,
        filename: Optional[Text] = None,
        underlying_yaml_exception: Optional[Exception] = None,
    ) -> None:
        super(YamlSyntaxExceptions , self).__init__(filename)

        self.underlying_yaml_exception = underlying_yaml_exception

    def __str__(self) -> Text:
        if self.filename:
            exception_message  = f"Failed to read '{self.filename}'."
        else:
            exception_message  = "Failed to read YAML."

        if self.underlying_yaml_exception:
            self.underlying_yaml_exception.warn = None
            self.underlying_yaml_exception.note = None
            exception_message  += f" {self.underlying_yaml_exception}"

        if self.filename:
            exception_message  = exception_message .replace(
                'in "<unicode string>"', f'in "{self.filename}"'
            )

        exception_message  += (
            "\n\nYou can use https://yamlchecker.com/ to validate the "
            "YAML syntax of your file."
        )
        return exception_message 
