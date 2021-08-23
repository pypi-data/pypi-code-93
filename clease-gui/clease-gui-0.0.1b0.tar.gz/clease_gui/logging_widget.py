import os
import ipywidgets as widgets
from IPython.display import display
import logging

__all__ = [
    'default_handler',
    'register_logger',
    'OutputWidgetHandler',
    'initialize_clease_gui_logging',
]


class OutputWidgetHandler(logging.Handler):
    """ Custom logging handler sending logs to an output widget.
    Class inspired by
    https://ipywidgets.readthedocs.io/en/stable/examples/Output%20Widget.html
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # layout = widgets.Layout(width='100%',
        # height='160px',
        # bor)
        layout = {
            'width': '100%',
            'height': '160px',
            'border': '1px solid black',
            'overflow': 'auto',
        }
        self.out = widgets.Output(layout=layout)

    def emit(self, record):
        """ Overload of logging.Handler method """
        formatted_record = self.format(record)
        new_output = {
            'name': 'stdout',
            'output_type': 'stream',
            'text': formatted_record + os.linesep
        }
        self.out.outputs = (new_output, ) + self.out.outputs

    def show_logs(self):
        """ Show the logs """
        display(self.out)

    def clear_logs(self):
        """ Clear the current logs """
        self.out.clear_output()


default_handler = OutputWidgetHandler()
default_handler.setFormatter(
    logging.Formatter('%(asctime)s  - [%(levelname)s] %(message)s'))
registered_loggers = []


def register_logger(logger, level=logging.INFO):
    """Register a logger to the default output widget handler.
    Anything emitted by this log will be shown in that widget"""
    global default_handler, registered_loggers
    registered_loggers.append(logger)
    logger.addHandler(default_handler)
    logger.setLevel(level)


def _register_warning_logger():
    """Inspired by
    https://stackoverflow.com/questions/38531786/capturewarnings-set-to-true-doesnt-capture-warnings
    Warning: this changes global variable in logging.
    """
    logging.captureWarnings(True)
    warnings_logger = logging.getLogger("py.warnings")
    register_logger(warnings_logger)


def _register_clease_logger(level=logging.INFO):
    clease_logger = logging.getLogger('clease')
    register_logger(clease_logger, level=level)


def set_all_levels(level) -> None:
    for logger in registered_loggers:
        logger.setLevel(level)


def initialize_clease_gui_logging():
    # _register_clease_logger()
    _register_warning_logger()
