"""Module for colors. Contain functions for coloring messages by level (yellow, red, grey...)
or function that color python code."""

# Lazy imports
# import pygments
# from pygments.lexers.python import PythonTracebackLexer
# from pygments.formatters import TerminalFormatter

USE_COLORS = True

color_palette = {
    "reset": "\x1b[0m",  # "reset"
    # "INFO": "\x1b[38;21m",  # "grey"
    # "DEBUG": "\x1b[38;21m",  # "grey"
    "WARNING": "\x1b[33;21m",  # "yellow"
    "ERROR": "\x1b[31;21m",  # "red"
    "CRITICAL": "\x1b[31;1m",  # "bold_red"
}


def colorize(message, level="WARNING", use=None):
    """Add color to message based on level - usally warnings and errors, to know what is internal error on first sight.
    There is global config.COLOR value that can be configured, so it's not necessary to pass as argument.

    Args:
        message (str): Any string you want to color.
        level (str, optional): "INFO" and "DEBUG" not colored, "WARNING": yellow, "ERROR": red or "CRITICAL": more red
        use (bool): It's possible to turn on and off colors with one config variable to keep syntax simple

    Returns:
        str: Message in yellow color. Symbols added to string cannot be read in some terminals.
            If config COLOR is 0, it return original string.

    Example:
        >>> message = "Hello there"
        >>> colored_message = colorize(message)
        >>> colored_message
        '\\x1b[33;21m Hello there \\x1b[0m'
    """

    if use is None:
        use = USE_COLORS

    if not use or level in ["DEBUG", "INFO"]:
        return message
    else:
        return f"{color_palette[level]} {message} {color_palette['reset']}"


def colorize_traceback(code):
    """Colorize string with code with python syntax.

    Args:
        code (str): Any python code

    Returns:
        str: String with added symbols cause that string will be colorized.

    Example:
        >>> import traceback
        ...
        >>> try:
        ...     1/0
        ... except ZeroDivisionError:
        ...     colorize_traceback(traceback.format_exc())
        'Traceback (most recent call last):\\n  File \\x1b[36m"<doctest mylogging.colors.colorize_traceback[1]>"\\x1b[39;49;00m...'
    """
    import pygments
    from pygments.lexers.python import PythonTracebackLexer
    from pygments.formatters import TerminalFormatter

    return pygments.highlight(
        code,
        PythonTracebackLexer(),
        TerminalFormatter(style="friendly"),
    )
