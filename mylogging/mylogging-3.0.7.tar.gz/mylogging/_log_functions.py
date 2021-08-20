import traceback as trcbck
import textwrap
import sys
import warnings

from . import _misc
from . import colors
from .colors import colorize, colorize_traceback
from ._config import config


def debug(message, caption=""):
    """Log debug info. Only difference with info is filtering LEVEL in config.

    Args:
        message (str): Message to be logged.
        caption (str, optional): Headning of warning. Defaults to 'User message'.
    """

    if not _misc.filter_out((caption + message)[:150], "DEBUG"):
        _misc.log_warn(return_str(message, caption=caption, objectize=False, level="DEBUG"), level="DEBUG")


def info(message, caption=""):
    """Log info.

    Args:
        message (str): Message to be logged.
        caption (str, optional): Headning of warning. Defaults to 'User message'.
    """

    if not _misc.filter_out((caption + message)[:150], "INFO"):
        _misc.log_warn(return_str(message, caption=caption, objectize=False, level="INFO"), level="INFO")


def warn(message, caption=""):
    """Raise warning - just message, not traceback. Can be colorized. Display of warning is based on warning settings.
    You can configure how to cope with warnings with function set_warnings with debug parameter. Instead of traceback_warning
    this is not from catched error. It usually bring some information good to know.

    Args:
        message (str): Any string content of warning.
        caption (str, optional): Headning of warning. Defaults to 'User message'.
    """

    if not _misc.filter_out((caption + message)[:150], "WARNING"):
        _misc.log_warn(
            return_str(message, caption=caption, objectize=False, level="WARNING"), level="WARNING"
        )


def error(message, caption=""):
    """Same as warn, but can be filtered different way with level. This is only for loggin message.
    If you want to log error code, you can use function traceback.

    Args:
        message (str): Any string content of error.
        caption (str, optional): Headning of error. Defaults to 'User message'.
    """
    if not _misc.filter_out((caption + message)[:150], "ERROR"):
        _misc.log_warn(return_str(message, caption=caption, objectize=False, level="ERROR"), level="ERROR")


def critical(message, caption=""):
    """Same as warning, but usually describe error that stopped the application.

    Args:
        message (str): Any string content of error.
        caption (str, optional): Headning of error. Defaults to 'User message'.
    """
    if not _misc.filter_out((caption + message)[:150], "CRITICAL"):
        _misc.log_warn(
            return_str(message, caption=caption, objectize=False, level="CRITICAL"), level="CRITICAL"
        )


# Just for naming convention
def fatal(message, caption=""):
    """Call critical(message, caption=""), just for naming conventions.

    Args:
        message (str): Any string content of error.
        caption (str, optional): Headning of error. Defaults to 'User message'.
    """
    critical(message, caption)


def traceback(message="", caption="error_type", level="ERROR", stack_level=3, remove_frame_by_line_str=[]):
    """Raise warning with current traceback as content. It means, that error was catched, but still something crashed.

    Args:
        message (str): Any string content of traceback.
        caption (str, optional): Caption of warning. If 'error_type', than Error type (e.g. ZeroDivisionError) is used.
            Defaults to 'error_type'.
    """
    if remove_frame_by_line_str:
        separated_traceback = get_traceback_with_removed_frames_by_line_string(remove_frame_by_line_str)

    else:
        separated_traceback = trcbck.format_exc()

    compared_message = caption + message + separated_traceback

    if _misc.filter_out(compared_message, level):
        return

    if caption == "error_type":
        try:
            caption = sys.exc_info()[1].__class__.__name__
        except Exception:
            caption = "Error"

    if colors.USE_COLORS:
        separated_traceback = colorize_traceback(separated_traceback)

    separated_traceback = separated_traceback.rstrip()

    separated_traceback = return_str(
        message=message,
        caption=caption,
        objectize=False,
        uncolored_message=f"\n\n{separated_traceback}" if message else f"{separated_traceback}",
        level=level,
    )

    _misc.log_warn(separated_traceback, level=level, showwarning_details=False, stack_level=stack_level)


def return_str(
    message,
    caption="User message",
    around="config",
    objectize=True,
    indent=4,
    uncolored_message=None,
    level="WARNING",
):
    """Return enhanced colored message. Used for raising exceptions, assertions.

    Args:
        message (str): Any string content of warning.
        caption (ctr, optional): Headning of warning. Defaults to 'User message'.
        around ((bool, str), optional): If print to file - whether print ====== lines around.
            If 'auto', then if TO_FILE = True, then AROUND = False, if TO_FILE = False, AROUND = True.
            If 'config', use global config (defaults 'auto'). Defaults to 'config'.
        objectize (bool, optional): Turn into object (If call in raise - only way to print colors).
            If you need string to variable, call str(). Defaults to True.
        indent (int, optional): By how many spaces are logs indented (for better visibility). If 0,
            than no indentation. Defaults to 4.
        uncolored_message (str, optional): Appendix added to end that will not be colorized (or
            already is colorized). Used for example for tracebacks. Defaults to None.

    Returns:
        str: Enhanced message as a string, that is wrapped by and can be colorized.
    """

    # If only caption do not print None or False
    if not message:
        message = ""

    if around == "config":
        around = config._used_around

    updated_str = colorize(message, level=level)

    if uncolored_message:
        if not around:
            uncolored_message = uncolored_message + "\n"
        updated_str = updated_str + uncolored_message

    if around:
        top_line = f"========= {caption} =========" if caption else "============================="
        bottom_line = colorize(f"{'=' * len(top_line)}\n\n", level=level)
        top_line = colorize(top_line, level=level)
        updated_str = f"\n\n{top_line} \n\n{updated_str} \n\n{bottom_line}"
    else:
        if caption:
            updated_str = f"{colorize(caption, level=level)}: {updated_str}"

    if indent:
        updated_str = textwrap.indent(text=updated_str, prefix=" " * indent)

    if objectize:
        updated_str = _misc.objectize_str(updated_str)

    return updated_str


def outer_warnings_filter(messages=[], messages_and_categories=[]):
    """Also other libraries you use can raise warnings. This function can filter warnings from such a libraries.

    Note:
        !!! Globally overwrite warnings behaviour - even outside called module. If using in
        library that other users use, you should reset their original filter settings with
        reset_outer_warnings_filter() at the end of your code.

    Args:
        messages (list, optional): List of warnings (any part of inner string) that will be ignored even if debug is set.
            Example ["AR coefficients are not stationary.", "Mean of empty slice",]. Defaults to [].
        messages_and_categories (list, optional): List of tuples (string of module that raise it and warning type) that will be ignored even if debug is set.
            Example [('statsmodels.tsa.arima_model', FutureWarning)].  Defaults to [].
    """
    _misc.user_filters = warnings.filters.copy()

    for i in messages:
        warnings.filterwarnings("ignore", message=fr"[\s\S]*{i}*")

    for i in messages_and_categories:
        warnings.filterwarnings("ignore", module=i[0], category=i[1])


def reset_outer_warnings_filter():
    """If you are filtering warnings and log inside your library, it's good to keep user's filters."""

    warnings.filters.clear()
    warnings.filters.extend(_misc.user_filters)


def get_traceback_with_removed_frames_by_line_string(lines):
    exc = trcbck.TracebackException(*sys.exc_info())
    for i in exc.stack[:]:
        if i.line in lines:
            exc.stack.remove(i)

    return "".join(exc.format())
