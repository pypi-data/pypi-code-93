import datetime
import logging
import sys
from logging.handlers import RotatingFileHandler
from timeit import default_timer as timer

import wrapt
# class TheLogger(object):
# 	def __init__(self,logger_name):
# 		pass
#
# def get_console_handler():
# 	console_handler=logging.StreamHandler(sys.stdout)
# 	console_handler.setFormatter(FORMATTER)
# 	return console_handler
#
# def get_file_handler():
# 	file_handler=TimedRotatingFileHandler(LOG_FILE,when='midnight',backupCount=3)
# 	file_handler.setFormatter(FORMATTER)
# 	return file_handler
#
# def get_logger(logger_name):
# 	logger=logging.getLogger(logger_name)
# 	logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
# 	logger.addHandler(get_console_handler())
# 	# logger.addHandler(get_file_handler())
# 	# with this pattern, it's rarely necessary to propagate the error up to parent
# 	logger.propagate=False
# 	return logger
from box import Box
from colorlog import ColoredFormatter
from python_log_indenter import IndentedLoggerAdapter

# FORMATTER=logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# LOG_FILE="lgblkb_tools.log"

colored_log_format = f"%(log_color)s%(asctime)s %(levelname)5.5s %(message)s"
# colored_log_format=f"%(asctime)s — %(name)s — %(levelname)s — %(message)s"
base_log_indent_settings = dict(indent_char='| ', spaces=1)
# date_fmt="%m-%d %H:%M:%S"
date_fmt = "%H:%M:%S"
default_log_format = colored_log_format.replace(r'%(log_color)s', '')

# region log_func_mapper:
log_func_mapper = Box()
log_func_mapper[logging.DEBUG] = lambda _logger: _logger.debug
log_func_mapper[logging.INFO] = lambda _logger: _logger.info
log_func_mapper[logging.WARNING] = lambda _logger: _logger.warning
log_func_mapper[logging.CRITICAL] = lambda _logger: _logger.critical
log_func_mapper[logging.ERROR] = lambda _logger: _logger.error
# endregion

log_sayer = lambda _logger, log_level: log_func_mapper[log_level](_logger)


def generate_handle():
    @wrapt.decorator
    def _handle_generator(wrapped, instance, args, kwargs):
        log_detailer = lambda *_args, level=logging.DEBUG, log_format='', **_kwargs: (level, log_format, _args, _kwargs)
        the_level, the_format, args, kwargs = log_detailer(*args, **kwargs)
        instance.create_handler(wrapped(*args, **kwargs), level=the_level, log_format=the_format)
        instance.info('Log handle %s created at %s', instance.logger.handlers[-1].__class__.__name__,
                      datetime.datetime.now())
        return instance
    
    return _handle_generator


# noinspection PyUnusedLocal
class TheLogger(IndentedLoggerAdapter):
    def __init__(self, logger_name, level=logging.DEBUG, extra=None, auto_add=True, propagate=False, _logger=None,
                 **kwargs):
        if _logger is None:
            _logger = logging.getLogger(logger_name)
        _logger.setLevel(level)
        super(TheLogger, self).__init__(_logger, extra=extra, auto_add=auto_add,
                                        **dict(base_log_indent_settings, **kwargs))
        _logger.propagate = propagate
    
    def create_handler(self, handler: logging.Handler, level=logging.DEBUG, log_format=''):
        if log_format:
            if type(handler) is logging.StreamHandler:
                log_formatter_class = ColoredFormatter
            else:
                log_formatter_class = logging.Formatter
            log_formatter = log_formatter_class(log_format, date_fmt)
        else:
            # if type(handler) is logging.StreamHandler:
            # 	log_formatter=ColoredFormatter(colored_log_format,date_fmt)
            # else:
            log_formatter = logging.Formatter(default_log_format, date_fmt)
        handler.setFormatter(log_formatter)
        handler.setLevel(level=level)
        self.logger.addHandler(handler)
        return self
    
    @generate_handle()
    def to_rotate(self, log_filepath, maxBytes=2.5e6, backupCount=14, **kwargs):
        return RotatingFileHandler(filename=log_filepath, maxBytes=int(maxBytes), backupCount=backupCount)
    
    def trace(self, level=logging.DEBUG, skimpy: bool = False, verbose=False):
        log_say = log_sayer(self, level)
        
        @wrapt.decorator
        def wrapper(wrapped, instance, args, kwargs):
            if skimpy:
                log_say('Performing "%s"...', wrapped.__name__)
            else:
                log_say('Running "%s":', wrapped.__name__)
            if verbose:
                logger.debug('args_count: %s', len(args)).a(3)
                for arg in args:
                    logger.debug('arg: %s', arg)
                logger.s(3)
                logger.debug('kwargs_count: %s', len(kwargs)).a(3)
                for k, v in kwargs.items():
                    logger.debug('%s: %s', k, v)
                logger.s(3)
            start = timer()
            self.add()
            out = wrapped(*args, **kwargs)
            if not skimpy: log_say('Done "%s". Duration: %.3f sec.', wrapped.__name__, timer() - start)
            self.sub()
            return out
        
        return wrapper
    
    @generate_handle()
    def to_file(self, log_filepath, **kwargs):
        return logging.FileHandler(log_filepath, **kwargs)
    
    @generate_handle()
    def to_stream(self, stream=None):
        return logging.StreamHandler(stream or sys.stdout)


logger: TheLogger = TheLogger('lgblkb_logger').to_stream()
logger.info('Log start datetime: %s', datetime.datetime.now())
