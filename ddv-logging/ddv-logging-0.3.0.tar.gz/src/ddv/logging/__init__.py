__version__ = "0.1.0"

"""
    Convenience methods for logging
"""
import sys
import logging
import traceback

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the
# foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    "WARNING": YELLOW,
    "INFO": CYAN,
    "DEBUG": MAGENTA,
    "CRITICAL": YELLOW,
    "ERROR": RED,
}


class ColouredFormatter(logging.Formatter):
    def __init__(self, fmt):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            levelname_color = (
                COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            )
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


class IndentFormatter(logging.Formatter):
    def __init__(self, fmt, use_colour=False):
        logging.Formatter.__init__(self, fmt)
        self.baseline = len(traceback.extract_stack()) + 7
        self.coloured_formatter = (
            ColouredFormatter(fmt) if use_colour else logging.Formatter(fmt)
        )

    def format(self, rec):
        depth = len(traceback.extract_stack()) - self.baseline
        rec.indent = ". " * depth
        out = self.coloured_formatter.format(rec)
        out = logging.Formatter.format(self, rec)
        del rec.indent
        return out


class VerbosityFilter(logging.Filter):
    def __init__(self, verbosity_level=0, verbosity_filters={0: []}):
        logging.Filter.__init__(self)

        self.filter_out_list = []

        for filter_level in verbosity_filters:
            if verbosity_level < filter_level:
                self.filter_out_list += verbosity_filters[filter_level]

    def filter(self, record):
        for filter_out_name in self.filter_out_list:
            if record.name.startswith(filter_out_name):
                return False
        return True


def log_to_stdout(
    logging_level=logging.DEBUG,
    enable_colours=False,
    enable_indentation=False,
    verbosity_level=0,
    verbosity_filters={0: []},
    message_format=None,
):

    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)

    root.setLevel(logging_level)
    handler.setLevel(logging_level)

    if message_format is not None:
        log_format = message_format
    elif logging_level == logging.DEBUG:
        log_format = "%(levelname)s %(name)s.%(funcName)s: %(message)s"
    else:
        log_format = "%(levelname)s %(name)s: %(message)s"

    if enable_indentation:
        log_format = "%(indent)s" + log_format
        formatter = IndentFormatter(log_format, use_colour=enable_colours)
    elif enable_colours:
        formatter = ColouredFormatter(log_format)
    else:
        formatter = logging.Formatter(log_format)

    handler.setFormatter(formatter)
    handler.addFilter(VerbosityFilter(verbosity_level, verbosity_filters))
    root.addHandler(handler)
