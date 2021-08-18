

# * Standard Library Imports -->
import os
import sys
import logging
from logging import handlers
from functools import wraps
from textwrap import shorten
from datetime import datetime
from typing import Optional, Callable
DATEFORMAT_STD = "%Y-%m-%d %H:%M:%S"
DATEFORMAT_DEV = "%H:%M:%S"
DATEFORMAT_FILE = "%Y-%m-%d_%H-%M-%S"


def pathmaker(first_segment, *in_path_segments, rev=False):
    """
    Normalizes input path or path fragments, replaces '\\\\' with '/' and combines fragments.

    Parameters
    ----------
    first_segment : str
        first path segment, if it is 'cwd' gets replaced by 'os.getcwd()'
    rev : bool, optional
        If 'True' reverts path back to Windows default, by default None

    Returns
    -------
    str
        New path from segments and normalized.
    """

    _path = first_segment

    _path = os.path.join(_path, *in_path_segments)
    if rev is True or sys.platform not in ['win32', 'linux']:
        return os.path.normpath(_path)
    return os.path.normpath(_path).replace(os.path.sep, '/')


def imported(in_name):
    return f"succesfully imported module: {in_name}"


def import_notification(logger, in_name):
    if os.getenv('DISABLE_IMPORT_LOGCALLS') == '1':
        return None
    else:
        return logger.debug("succesfully imported module: %s", in_name)


def DEPRECATED(in_alternative=None):
    if in_alternative is None:
        _msg = "!!!!!!!!!DEPRECATED FUNCTION!!!!!!!!!, stop using it!"
    else:
        _msg = f"!!!!!!!!!DEPRECATED FUNCTION!!!!!!!!!, use [{in_alternative}] instead!"
    return _msg


def NEWRUN():
    return "# " + "*-$-" * 6 + "* --> NEW_RUN <-- " + "*-?-" * 6 + "* #"


def class_init_notification(logger, in_class, use=None):
    if os.getenv('DISABLE_INITIATION_LOG_CALLS') == "1":
        return
    if use == 'repr':
        _string = f"'{repr(in_class)}'"
    elif use == 'str':
        _string = f"'{str(in_class)}'"
    else:
        _string = f"'{in_class.__class__.__name__}'"
    return logger.debug("finished initiating %s class", _string)


def called(function_name):
    return f"{function_name} was called"


def completed(function_name):
    return f"{function_name} completed"


def aux_logger(in_name: str):
    in_name = in_name.split('.', maxsplit=1)
    in_name = in_name[-1]

    return logging.getLogger('main.' + in_name)


def alt_aux_logger(in_name):
    in_name = in_name.split('.')
    in_name = in_name[-1]
    return logging.getLogger('main.' + in_name)


def library_base_logger(library_name: str):
    return logging.getLogger(library_name).addHandler(logging.NullHandler())


def aux_library_logger(in_name: str):
    return logging.getLogger(in_name)

# def main_logger(in_file_name, in_level, in_back_up=2):

#     _out = logging.getLogger('main')
#     _out.setLevel(getattr(logging, in_level.upper()))
#     formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | (%(lineno)s) | %(name)s | %(funcName)-25s | --> %(message)s <--')
#     should_roll_over = os.path.isfile(in_file_name)
#     handler = handlers.RotatingFileHandler(in_file_name, mode='a', backupCount=in_back_up)
#     handler.namer = std_namer
#     if should_roll_over:
#         handler.doRollover()
#     handler.setFormatter(formatter)
#     _out.addHandler(handler)

#     return _out


class CustomFormatter(logging.Formatter):
    """ Custom Formatter does these 2 things:
    1. Overrides 'funcName' with the value of 'func_name_override', if it exists.
    2. Overrides 'filename' with the value of 'file_name_override', if it exists.
    3. Shortens 'funcName' and 'filename' so to not cause issues with the formatting.
    """

    def __init__(self, fmt: Optional[str] = None, max_name_size: int = 25, datefmt: Optional[str] = None, style='%', validate: bool = True, error_formatter: Callable = None, no_newline_on_error: bool = False) -> None:
        self.max_name_size = max_name_size
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        self.error_formatter = error_formatter
        self.no_newline_on_error = no_newline_on_error

    def format(self, record):
        record.name = record.name.removeprefix('main.')

        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'file_name_override'):
            record.filename = record.file_name_override
        if len(record.levelname) >= 11:
            record.levelname = record.levelname[:11 - 3] + '...'
        if len(record.threadName) >= 12:
            record.threadName = record.threadName[-(12 - 3):] + '...'
        if len(record.name) >= self.max_name_size:
            record.name = '...' + record.name[-(self.max_name_size - 3):]
        if len(record.funcName) >= 30:
            record.funcName = record.funcName[:30 - 3] + '...'

        s = super().format(record)
        if record.exc_text:
            if self.no_newline_on_error is True:
                s = s.replace('\n', '')
        return s

    def formatException(self, ei) -> str:
        output = super().formatException(ei)
        if self.error_formatter is None:
            return output
        return self.error_formatter(output)


class ExcludeProfilingStreamHandler(logging.StreamHandler):

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelname.casefold() != 'profile':
            return super().emit(record)


def marked_exception_formatter(in_text: str) -> str:
    text = f"<TRACEBACK>\n\n{in_text}\n\n</TRACEBACK>"
    return text


def _each_run_file_rotate_handler(in_file_name, in_back_up, formatter_kwargs: dict = None):
    _date_format = DATEFORMAT_DEV if os.getenv('IS_DEV') == "1" else DATEFORMAT_STD
    formatter = CustomFormatter(fmt='{asctime}.{msecs:03.0f} |{levelname:^11}|{threadName:^12}|{lineno:^5}| {name:<50} |{funcName:^30}||--> {message}', datefmt=_date_format, style='{', **formatter_kwargs)
    handler = handlers.RotatingFileHandler(in_file_name, mode='a', backupCount=in_back_up, maxBytes=10 * (1024 * 1024))
    handler.namer = std_namer
    handler.setFormatter(formatter)
    return handler


def _stdout_handler(formatter_kwargs: dict = None):
    _date_format = DATEFORMAT_DEV
    formatter = CustomFormatter(fmt='{asctime} |{levelname:^11}| {name:<50} |{funcName:^30}||--> {message}', datefmt=_date_format, style='{', **formatter_kwargs)
    # formatter = logging.Formatter(fmt='[{asctime}][{levelname:^7}][{name:<30}][{funcName:^25}] --> {message}', datefmt=_date_format, style='{')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    return handler


def _minimal_stdout_handler(formatter_kwargs: dict = None):
    _date_format = DATEFORMAT_DEV
    formatter = CustomFormatter(fmt='{asctime} |{levelname:^11}||--> {message}', datefmt=_date_format, style='{', **formatter_kwargs)
    # formatter = logging.Formatter(fmt='[{asctime}][{levelname:^7}][{name:<30}][{funcName:^25}] --> {message}', datefmt=_date_format, style='{')
    handler = ExcludeProfilingStreamHandler()
    handler.setFormatter(formatter)
    return handler


def main_logger(in_file_name, in_level='DEBUG', in_back_up=2, other_logger_names=None, log_to='both', stdout_formatter: str = None, formatter_kwargs: dict = None):
    default_formatter_kwargs = {"error_formatter": marked_exception_formatter, "no_newline_on_error": False}
    formatter_kwargs = default_formatter_kwargs if formatter_kwargs is None else default_formatter_kwargs | formatter_kwargs
    stdout_fomatter_map = {'minimal': _minimal_stdout_handler,
                           'normal': _stdout_handler}
    stdout_formatter = 'minimal' if stdout_formatter is None else stdout_formatter.casefold()
    stdout_handler_function = stdout_fomatter_map.get(stdout_formatter, _minimal_stdout_handler)
    log_to = log_to.casefold()
    should_roll_over = os.path.isfile(in_file_name)
    run_rotating_file_handler = _each_run_file_rotate_handler(in_file_name=in_file_name, in_back_up=in_back_up, formatter_kwargs=formatter_kwargs)
    stdout_handler = stdout_handler_function(formatter_kwargs=formatter_kwargs)
    _out = logging.getLogger('main')
    all_loggers = [_out] + list(map(logging.getLogger, other_logger_names)) if other_logger_names is not None else [_out]
    for logger in all_loggers:
        logger.setLevel(in_level.upper())
        if log_to in ['both', 'file']:
            logger.addHandler(run_rotating_file_handler)
        if log_to in ['both', 'stdout']:
            logger.addHandler(stdout_handler)
    if log_to in ['both', 'file']:

        if should_roll_over:
            run_rotating_file_handler.doRollover()
    return _out


def main_logger_stdout(in_level):

    _out = logging.getLogger('main')
    _out.setLevel(in_level.upper())

    _out.addHandler(_stdout_handler())

    return _out


def _is_appdata_object(in_object):
    try:
        _name = in_object.__class__.__name__
        return _name == 'AppDataStorager'
    except AttributeError:
        return False


def std_namer(name):
    dir_path = os.path.dirname(name)
    new_dir_path = pathmaker(dir_path, 'old_logs')
    file_name = os.path.basename(name)
    file_number = 1
    new_file_name = file_name.split('.log')[0] + f"_{str(file_number)}.log"
    new_path = pathmaker(new_dir_path, new_file_name)
    while os.path.exists(new_path):
        file_number += 1
        new_file_name = file_name.split('.log')[0] + f"_{str(file_number)}.log"
        new_path = pathmaker(new_dir_path, new_file_name)
    return new_path


def timestamp_log_folderer(in_log_file_name, in_main_log_folder=None):
    if in_main_log_folder is None:
        _cwd = pathmaker(os.getcwd(), 'logs')
    elif isinstance(in_main_log_folder, str):
        if os.path.basename(in_main_log_folder) == 'logs':
            _cwd = pathmaker(in_main_log_folder)
        else:
            _cwd = pathmaker(in_main_log_folder, 'logs')

    elif _is_appdata_object(in_main_log_folder) is True:
        _cwd = pathmaker(in_main_log_folder.log_folder)

    else:
        raise TypeError(f"type {type(in_main_log_folder)} not supported")
    _path_to_old_folder = pathmaker(_cwd, 'old_logs')
    if os.path.exists(_path_to_old_folder) is False:
        os.makedirs(_path_to_old_folder)
    return pathmaker(_cwd, in_log_file_name + '_' + datetime.utcnow().strftime(DATEFORMAT_FILE) + ".log")


def log_folderer(in_log_file_name, in_main_log_folder=None):
    if in_main_log_folder is None:
        _cwd = pathmaker(os.getcwd(), 'logs')
    elif isinstance(in_main_log_folder, str):
        if os.path.basename(in_main_log_folder) == 'logs':
            _cwd = pathmaker(in_main_log_folder)
        else:
            _cwd = pathmaker(in_main_log_folder, 'logs')

    elif _is_appdata_object(in_main_log_folder) is True:
        _cwd = pathmaker(in_main_log_folder.log_folder)

    else:
        raise TypeError(f"type {type(in_main_log_folder)} not supported")
    _path_to_old_folder = pathmaker(_cwd, 'old_logs')
    if os.path.exists(_path_to_old_folder) is False:
        os.makedirs(_path_to_old_folder)
    return pathmaker(_cwd, in_log_file_name + ".log")


def log_args(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        _log = logging.getLogger('main')
        _log.debug('started executing %s: --> %s <--, with arguments: %s, %s %s', type(function).__name__, function.__name__, ', '.join(map(str, args)), ', '.join([f"{str(key)}={str(value)}" for key, value in kwargs.items()]), '-' * 50)
        return function(*args, **kwargs)
    return wrapper


if __name__ == "__main__":
    pass
