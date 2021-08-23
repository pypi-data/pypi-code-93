from typing import List, Callable, Any, Union, Optional
import atexit
import os
import sys
import dis
import traceback
import inspect
from datetime import datetime
import simplejson  # Required in case of PyInstaller
import jsonpickle
import re
import threading
from pathlib import Path
from contextlib import contextmanager
from dblogging.config import LogTag, LogTags
from dblogging.generators import HtmlLogGenerator
from dblogging.sqlite.dal import LoggerSql


class _LogThread:
    def __init__(self, depth: int = -1, sql: LoggerSql = None, blacklist_function: callable = None,
                 mode: str = 'all', blacklist_log_tag: 'LogTag' = None):
        self.depth = depth
        self.sql = sql
        self._mode = mode
        self.persistence_enabled = mode in {'all', 'persistence'}
        self.console_enabled = mode in {'all', 'console'}
        self.check_mode = False
        self._blacklist_function = None
        self.blacklist_function = blacklist_function
        self.blacklist_log_tag = blacklist_log_tag

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: str):
        if value == 'current':
            return
        elif value not in (values := {'all', 'persistence', 'console'}):
            raise ValueError(f'Cannot set mode to "{value}" because it is invalid.\n'
                             f'Valid modes are {values}')
        self._mode = value
        self.persistence_enabled = value in {'all', 'persistence'}
        self.console_enabled = value in {'all', 'console'}

    @property
    def blacklist_function(self):
        return self._blacklist_function

    @blacklist_function.setter
    def blacklist_function(self, value):
        if value and callable(value):
            # noinspection PyUnresolvedReferences
            arg_len = len(value.__code__.co_varnames)
            if arg_len == 0:
                raise ValueError('blacklist_function requires at least one input parameter for the '
                                 'log_tag and another optional parameter for the log mode.')
            elif arg_len == 1:
                self._blacklist_function = lambda x, y=None: value(x)
                self.check_mode = False
            else:
                self.check_mode = True
        else:
            self.check_mode = False
        self._blacklist_function = value

    def blacklisted(self, log_tag: 'LogTag'):
        if not isinstance(self.blacklist_function, Callable):
            return False, False
        if self.check_mode:
            console_blacklisted = self.blacklist_function(log_tag, 'console') is True
            persistence_blacklisted = self.blacklist_function(log_tag, 'persistence') is True
            return console_blacklisted, persistence_blacklisted
        return [self.blacklist_function(log_tag)] * 2


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class _LoggerPickler(jsonpickle.pickler.Pickler):
    MASKED_REGEXES = []

    def _flatten_key_value_pair(self, k, v, data):
        if self.MASKED_REGEXES and isinstance(k, jsonpickle.pickler.string_types):
            pattern = "(" + ")|(".join(self.MASKED_REGEXES) + ")"
            if re.match(pattern=pattern, string=str(k), flags=re.IGNORECASE):
                v = "********"
        return super()._flatten_key_value_pair(k, v, data)


class Logger(metaclass=_Singleton):
    def __init__(self):
        """
        Creates a singleton instance of the logger. This object is a singleton object because different
        instances of the logger can create issues if persisting to the same file. Rather than having
        multiple instances of the logger, a single instance can be used while using log tags.

        --> Log Tags

        Log tags are a conceptual representation of how the program can be divided in terms of logging. Common
        tags are severity tags: info, debug, warning, error, and critical. However, custom tags can be created
        to represent the logging in more and different ways. Rather than severity tags, tags could alternatively
        represent the level of code that is performing the log, such as the Data Access Layer vs. a public API
        layer. Log tags provide a way to tag log messages so they can be more easily filtered when viewing the
        output.

        To create custom log tags, either import the LogTagTemplate or the LogTags and inherit it in the new
        custom log tag class. A ``default`` and ``critical`` log tags are required because the logger uses
        defaults for standard and error logging. The LogTagTemplate does not define any of the required tags,
        but raises an error when they are not implemented whereas the LogTags does. Here is an example:

            from logger.config import LogTagTemplate, LogTags, LogTag

            # Inheriting from LogTagTemplate requires default and critical tags to be defined.
            class CustomLogTags1(LogTagTemplate):
                default = LogTag(
                    name='Standard',
                    value=0,
                    html_color='cyan'
                )

                test = LogTag(
                    name='Test',
                    value=10,
                    html_color='green'
                )

                critical = LogTag(
                    name='Critical',
                    value=90,
                    html_color='red'
                )

            # Inheriting from LogTags doesn't require default and critical tags to be defined.
            class CustomLogTags2(LogTags):
                test = LogTag(
                    name='Test',
                    value=10,
                    html_color='green'
                )

        To use the custom log tags, set the ``log_tags`` to the class that defines them. Using the
        example above, ``logger.log_tags = CustomLogTags1``. Then ``logger.log(msg, CustomLogTags1.test)``
        would be legal.

        --> Basic Logging

        There are three basic logging methods: ``log()``, ``log_method()``, and ``log_exception()``.

        ``log()`` simply commits a log message on the fly. The function name is retrieved dynamically.
        ``log_method()`` should at most rarely be used. It creates a log entry with a given function name.
        ``log_exception()`` is used to locate the exception in the call stack to log.

        --> Logging Control

        Logging output can be controlled by setting rules once the ``start()`` method is called. These
        rules are set using the ``set_rule()`` method. These rules control a few factors when logging:
            a) The mode. There are four modes: current, console, persistence, and all. The console mode
               only logs to stdout. The persistence mode only logs to the DB log file. All does both. The
               current mode does not switch the mode when setting the rule.
            b) The rule. Basic rules are setting a minimum tag value or blacklisting a set of tag names.
               A custom rule can be supplied as well. This controls what will and won't get logged to
               reduce noise in the logs.
            c) Why. This is a message suggesting why the rule was changed. This will always be logged.

        --> Contextual Logging

        Use ``generate()`` as a context manager (i.e. ``with logger.generate('html'):``). Nothing is yielded
        to the context block. After the context is executed, the logger automatically searches the call stack
        if an error is raised and logs it. If persistence is enabled, the format generator's ``generate()``
        method is called to create the log file from the DB file. HTML is the only generator provided, although
        a custom generator can be created.

        --> Log Wrappers

        There are two log wrappers: wrap_class() and wrap_func(). They log the inputs and outputs of functions.
        They provided depth to the log output, meaning a hierarchy of logs can be created. Without these methods
        all logs would be flat and one dimensional. See their docstrings for more details.
        """
        self._disabled = True
        self._date_format = '%Y/%m/%d %H:%M:%S'
        self._timestamp = lambda: datetime.now().strftime(self._date_format)
        self._persistent_logging = False
        self._log_path = None  # type: Optional[Path]
        self._log_tags = LogTags
        self._sql = None
        self._main_thread = threading.current_thread()
        self._threads = {self._main_thread.ident: _LogThread(depth=0)}
        self._jsonpickle = jsonpickle
        self._jsonpickle.pickler.Pickler = _LoggerPickler
        self._jsonpickle.set_encoder_options(simplejson.__name__, sort_keys=True, indent=4)
        self.logger_lock = threading.Lock()
        self.use_cache_shared_file_memory = False

    @property
    def log_path(self) -> Path:
        return self._log_path

    @log_path.setter
    def log_path(self, path: Union[Path, str]):
        if self._log_path and os.path.exists(self._log_path):
            raise ValueError(f'Cannot set log path to "{path}" because it is already set to '
                             f'"{self._log_path}", which exists.')
        if not isinstance(path, Path):
            if not self.use_cache_shared_file_memory and not path.endswith('.db'):
                path += '.db'
            path = Path(path)
        if hasattr(sys, '_MEIPASS'):
            if str(path).startswith(sys._MEIPASS):
                path = Path(str(path).replace(sys._MEIPASS, os.path.dirname(sys.argv[0])))
        path.parent.mkdir(parents=True, exist_ok=True)
        self._log_path = path.absolute()
        self._persistent_logging = True

    @property
    def log_tags(self):
        return self._log_tags

    @log_tags.setter
    def log_tags(self, value):
        if not hasattr(value, 'default'):
            raise AttributeError(f'The custom logger must have a <default> LogTag attribute defined.')
        elif not hasattr(value, 'critical'):
            raise AttributeError(f'The custom logger must have a <critical> LogTag attribute defined.')
        self._log_tags = value

    @staticmethod
    def add_cleanup(func, *args, **kwargs):
        atexit.register(func, *args, **kwargs)

    @property
    def date_format(self):
        return self._date_format

    @date_format.setter
    def date_format(self, format: str):
        self._date_format = format

    @contextmanager
    def disabled(self, log_tag: LogTag = None, why: str = ''):
        """
        WARNING! This disables all logging in a context. This trumps all rules and modes as no logs
        will be processed or printed to the console. Use carefully. Useful in contexts of large
        concurrency and redundant logging. Upon exit of the context the logger will reset to the
        original state. Upon exit the logger will raise an error if an exceptions were raised in the
        context and the original state of the logger was enabled. In other words, if the logger was
        never started with ``start()``, then it will not log the exceptions.

        Examples:
            logger = Logger(...)

            with logger.disabled(log_tag=log_tags.default, why='Suppressing redundant logs...'):
                for i in range(5000):
                    logger.log('I will not be logged at all. Period.')
            logger.log('I am logged!')

        Args:
            log_tag: The log tag that logs why. Defaults to the default tag.
            why: A description of why logging is being disabled.
        """
        log_tag = log_tag or self._log_tags.default
        num_prev_callers = 2
        orig_state = self._disabled
        try:
            self.log(msg=f'Disabling logging. {why}', log_tag=log_tag, num_prev_callers=num_prev_callers)
            self._disabled = True
            yield
        except:
            self._disabled = orig_state
            self.log(msg=f'Re-enabling logging. {why}', log_tag=log_tag, num_prev_callers=num_prev_callers)
            raise
        self._disabled = orig_state
        self.log(msg=f'Re-enabling logging. {why}', log_tag=log_tag, num_prev_callers=num_prev_callers)

    @contextmanager
    def generate(self, format_generator: Union[str, Callable], **kwargs):
        """
        Generates logs and optionally generates an output file from the DB log file according
        to the ``format_generator`` parameter. The ``format_generator`` is either a string
        that identifies a built-in format generator or a custom generator that is callable.

        The only built-in generator is 'html' at this time.

        A custom generator can be used. It must be able to be initialized without parameters
        and have a ``generate()`` function with at least a ``log_file`` parameter. Optional
        parameters can be passed to the generator as ``kwargs``. For example:

            # Using the built-in HTML generator.
            with logger.generate('html'):
                # Do stuff here.

            # Using a custom generator.
            class SomeCustomGenerator:
                def __init__(self):  # No arguments required!
                    # Initialize stuff here.

                # This method is required!
                def generate(log_file: str, **kwargs): # log_file required!
                    # Generate output here.

            with logger.generate(SomeCustomGenerator, custom_kw='Some Custom Variable Value'):
                # Do stuff here.

        Args:
            format_generator: Either a string for a built-in generator or a callable custom one.
            **kwargs: Extra arguments to pass to the generator.
        """
        if self._disabled:
            self.start()
        if self._persistent_logging:
            if isinstance(format_generator, str):
                generators = {
                    'html': HtmlLogGenerator
                }
                generator = generators[format_generator]()
            else:
                generator = format_generator()
            if not self._log_path:
                raise ValueError('Cannot generate persisting logs without a log path.\n'
                                 'Please instantiate the logger with a log path.')
            try:
                yield
            except:
                self.log_exception()
                raise
            finally:
                db_file = self._log_path if not self.use_cache_shared_file_memory else 'file::memory:?cache=shared'
                generator.generate(log_file=str(self._log_path), db_file=db_file, **kwargs)
        else:
            try:
                yield
            except:
                self.log_exception()

    def log(self, msg: Any, log_tag: LogTag = None, num_prev_callers: int = 0):
        """
        Logs a message if logging is enabled and it satisfies the rule set. The default rule allows
        all logging. The rule may specify console logging only, persistent logging only, or both.

        ``num_prev_callers`` allows the caller to specify which caller in the call stack should be
        referenced in the log entry. By default the caller of this method is captured and logged.
        This is handy to use when the caller of this method doesn't live in a method whose context
        is helpful to debugging. For example, if A calls B and B calls ``log(..., prev_num_callers=1)``
        then the message is logged with a reference to the file path, line number, and function name
        from caller A in relation to the call stack.

        Args:
            msg: Log message.
            log_tag: The log tag that logs the message. Defaults to the default tag.
            num_prev_callers: Number of callers in the current call stack previous to the caller of
                              this method.
        """
        if self._disabled:
            return
        log_tag = log_tag or self._log_tags.default
        thread = threading.current_thread()
        if lt := self._threads.get(thread.ident):
            no_console, no_persistence = lt.blacklisted(log_tag)
            if no_console and no_persistence:
                return
        else:
            no_console, no_persistence = [False] * 2
        func, file_path, line_num = self._get_log_info(num_prev_callers=num_prev_callers)
        self._commit_log(msg=msg, log_tag=log_tag, file_path=file_path, line_num=line_num, func=func,
                         no_console=no_console, no_persistence=no_persistence)

    def log_exception(self):
        """
        Logs the function name, file path, line number, and exception message if logging is enabled. The
        log tag used is ``critical``. The log rule is disregarded.
        """
        if self._disabled:
            return
        with self.logger_lock:
            tb = sys.exc_info()[2]

        while True:
            if tb.tb_next is None:
                break
            tb = tb.tb_next
        frame = tb.tb_frame
        outer_frames = inspect.getouterframes(frame)[0]
        if outer_frames.function == '<module>':
            func = inspect.getmodulename(outer_frames.filename)
        else:
            if (class_name := outer_frames[0].f_locals.get('self')) is not None:
                func = f'{class_name.__class__.__qualname__}.{outer_frames.function}'
            else:
                func = outer_frames.function
        msg = traceback.format_exc()
        self._commit_log(msg=msg, log_tag=self._log_tags.critical, file_path=outer_frames[1], line_num=outer_frames[2],
                         func=func)

    def log_method(self, func: callable, msg: Any, log_tag: LogTag = None, returning: bool = False):
        """
        Similar to ``log()`` with one particular difference. ``log()`` dynamically retrieves the
        information of the referenced caller using ``num_prev_callers`` whereas ``log_method()``
        directly uses ``func`` for the name of the function and ``returning`` to decide if the
        line number referenced is the first or last line of the function. This method should rarely
        be used. To log a method use ``wrap_func()`` instead as it handles log depth.

        Args:
            func: A callable function.
            msg: Log message.
            log_tag: The log tag that logs the message. Defaults to the default tag.
            returning: If ``True``, reference the last line of the method, otherwise the first.
        """
        if self._disabled:
            return
        log_tag = log_tag or self._log_tags.default
        thread = threading.current_thread()
        if lt := self._threads.get(thread.ident):
            no_console, no_persistence = lt.blacklisted(log_tag)
            if no_console and no_persistence:
                return
        else:
            no_console, no_persistence = [False] * 2

        self._commit_log(
            msg=msg,
            log_tag=log_tag,
            file_path=func.__code__.co_filename,
            line_num=list(dis.findlinestarts(func.__code__))[-1][-1] if returning else func.__code__.co_firstlineno,
            func=func.__qualname__,
            no_console=no_console,
            no_persistence=no_persistence
        )

    @contextmanager
    def rule(self, log_tag: LogTag = None, min_tag_value: Union[LogTag, int] = None,
             blacklist_tag_names: List[str] = None, blacklist_function: Callable = None,
             why: str = ''):
        """
        A context manager for `meth:dblogging.logger.set_rule`.

            with logger.rule_context(...):
                # Code here.
        """
        self._set_rule(log_tag=log_tag, min_tag_value=min_tag_value, blacklist_tag_names=blacklist_tag_names,
                       blacklist_function=blacklist_function, why=why, num_prev_callers=2)
        yield
        self._set_rule(log_tag=log_tag, reset=True, num_prev_callers=2)

    def set_mode(self, mode: str, log_tag: LogTag = None, why: str = ''):
        """
        The log mode can be used to change where the logs are recorded. This is useful for simply
        reducing noise in the log output.
        There are four modes: current, console, persistence, and all.
            * current: Do not change the mode. Default.
            * console: Change the mode to log to the console only.
            * persistence: Change the mode to log to the SQLite DB file only.
            * all: Change the mode to use both console and persistent logging.

        Args:
            mode: One of 'current', 'console', 'persistence', or 'all'. Default is 'current'. Case sensitive.
            log_tag: The log tag that logs why. Defaults to the default tag.
            why: A description of why the mode is being set.
        """
        if self._disabled:
            return

        thread = threading.current_thread()
        log_tag = log_tag or self._log_tags.default
        msg = f'Setting log mode to "{mode}". '
        if thread.ident == self._main_thread.ident:
            for t in self._threads.values():
                t.mode = mode
        elif lt := self._threads.get(thread.ident):
            lt.mode = mode
        else:
            self._threads[thread.ident] = _LogThread(
                depth=self._threads[self._main_thread.ident].depth,
                blacklist_function=self._threads[self._main_thread.ident].blacklist_function,
                mode=mode
            )

        func, file_path, line_num = self._get_log_info(num_prev_callers=0)
        self._commit_log(msg=f'{msg}\n{why}', log_tag=log_tag, file_path=file_path, line_num=line_num, func=func,
                         force=True)

    def set_rule(self, log_tag: LogTag = None, min_tag_value: Union[LogTag, int] = None,
                 blacklist_tag_names: List[str] = None, blacklist_function: Callable = None,
                 reset: bool = False, why: str = ''):
        """
        Sets a rule that dictates what will and will not get logged, as well as how they are logged.

        The ``min_tag_value`` specifies the minimum tag value that a log tag must have in order to
        log a message.

        The ``blacklist_tag_names`` specifies a list of tag names that prevent messages from being
        logged. In other words, a log tag whose name is blacklisted will not log the message.

        The ``blacklist_function`` defines a custom function that blacklist log tags from logging
        their messages. There is no whitelist option. The function must return a boolean where
        ``False`` allows a message to be logged.

        The ``reset`` flag resets the log rules to their initial state when the logger was
        initialized.

        If none of ``min_tag_value``, ``blacklist_tag_names``, ``blacklist_function``, or ``reset`` are
        specified, then no rules are set to restrict any logging. In other words, all logging in the
        specified mode is enabled.

        The rule that is set cannot change unless calling `set_rule()` with a log tag value greater than
        or equal to the log tag used to set the rule in the first place. So:

            logger.set_rule(log_tag=LogTags.with_value_10, min_tag_value=20)  # Honored.
            logger.log(log_tag=LogTags.with_value_1, ...)  # Not logged.
            logger.log(log_tag=LogTags.with_value_10, ...)  # Not logged.
            logger.log(log_tag=LogTags.with_value_20, ...)  # Logged.
            logger.set_rule(log_tag=LogTags.with_value_5, reset=True)  # Not honored.
            logger.set_rule(log_tag=LogTags.with_value_15, min_tag_value=20)  # Honored.

        Args:
            log_tag: The log tag that logs why. Defaults to the default tag.
            blacklist_function: Optional. This is evaluate first. If not ``None``, this rule is used.
            min_tag_value: Optional. This is evaluated second. If not ``None``, this rule is used.
            blacklist_tag_names: Optional. This is evaluated third. If not ``None``, this rule is used. Must
                                 be a list of tag names.
            reset: Optional. This is evaluated last. If not ``None``, the rule in the specified mode is reset
                   to the initial state.
            why: A description of why the rule is being set.
        """
        return self._set_rule(
            log_tag=log_tag, min_tag_value=min_tag_value, blacklist_tag_names=blacklist_tag_names,
            blacklist_function=blacklist_function, reset=reset, why=why, num_prev_callers=1
        )

    def start(self):
        """
        Starts the logging. By default all logging is disabled. Once this method is called, logging
        is initialized according to the log path, log tags, and date format set. By default, nothing
        is set. These variables can be changed throughout the execution of the program, although it
        is not recommended as the output can produce unexpected results.

        If nothing is set and this method is called, only stdout is enabled. No logs will persist.

        The ``log_path`` can change throughout the execution of the program given that the file does
        not already exist (but the parent folder must exist). Once set, call ``start()`` again to
        reinitialize the DB file.

        The ``log_tags`` can change, although this is dangerous and should not happen. Once this
        method is called, the DB is initialized with all of the log tag data. If the log tags
        change during execution of the program and contains tags that did not exist previously,
        then they will not be included in the output logs.

        The ``date_format`` can change any time as this only affects stdout.
        """
        self._disabled = False
        if self.log_path:
            if self.use_cache_shared_file_memory:
                self._sql = LoggerSql(db_file_name='file::memory:?cache=shared')
            else:
                self._sql = LoggerSql(db_file_name=str(self._log_path))
            self._threads = {
                self._main_thread.ident: _LogThread(
                    depth=0,
                )
            }

            self._sql.create_database()
            for ll in self._log_tags.get_all():
                self._sql.log_tags.insert(
                    name=ll.name, value=ll.value, color=ll.html_color
                )

    def wrap_class(self, log_tag: LogTag = None, func_regex_exclude: str = '', mask_input_regexes: List = None,
                   mask_output: bool = False, mask_output_regexes: List = None):
        """
        Applies ``wrap_func()`` to each callable member of a class that does not start with "__" and does not
        match the ``func_regex_exclude``. If a callable member starting with "--" should be wrapped, then it
        must be explicitly wrapped with the ``wrap_func()`` method. The ``mask_input_regexes`` and ``mask_output``
        parameters are passed to the ``wrap_func()`` method.

        Args:
            log_tag: The log tag to apply to each method wrapped.
            func_regex_exclude: A regular expression matching method names that should not be wrapped.
            mask_input_regexes: Passed to ``wrap_func()``.
            mask_output: Passed to ``wrap_func()``.
            mask_output_regexes: A list of regular expressions of keys whose values ought to be masked in the
                                 output. This only applies to return values with key/value pair associations.
                                 Use ``mask_output`` if the output is not a dictionary-like object (such as a string).
        """
        log_tag = log_tag or self._log_tags.default
        if isinstance(mask_output_regexes, list):
            with self.logger_lock:
                _LoggerPickler.MASKED_REGEXES = list(set(_LoggerPickler.MASKED_REGEXES + mask_output_regexes))

        def _wrap(cls):
            for attr, fn in inspect.getmembers(cls, inspect.isroutine):
                if callable(getattr(cls, attr)) and not fn.__name__.startswith('__'):
                    if func_regex_exclude:
                        matches = re.findall(pattern=func_regex_exclude, string=fn.__name__, flags=re.IGNORECASE)
                        if fn.__name__ in matches:
                            continue

                    if type(cls.__dict__.get(fn.__name__)) in {staticmethod, classmethod}:
                        setattr(cls, attr, self.wrap_func(
                            log_tag=log_tag,
                            is_static_or_classmethod=True,
                            mask_input_regexes=mask_input_regexes,
                            mask_output=mask_output
                        )(getattr(cls, attr)))
                    else:
                        setattr(cls, attr, self.wrap_func(
                            log_tag=log_tag,
                            mask_input_regexes=mask_input_regexes,
                            mask_output=mask_output
                        )(getattr(cls, attr)))
            return cls
        return _wrap

    def wrap_func(self, log_tag: LogTag = None, mask_input_regexes: List = None, mask_output: bool = False,
                  is_static_or_classmethod: bool = False, mask_output_regexes: List = None):
        """
        Wrapper for a function or method. This wrapper performs a few important steps:
            1. Increases the depth of the call, which controls its relation to all previous and
               subsequent logs in the log hierarchy.
            2. Logs the function's name, inputs, and outputs.
            3. Catches any exceptions raised by the function and logs them.
            4. Decreases the depth of the call to return to the original depth of the call hierarchy.

        The depth is the defining marker for the position of a function in the logged hierarchy. Without it,
        all logs would be flat an hard to parse through.

        Example:

            @logger.wrap_func(
                log_tag=Tags.SomeTag,
                mask_input_regexes=['cls', 'password'],
                is_static_or_classmethod=True,
                mask_output_regexes=['.*api.*token.*']
            )
            @classmethod
            def do_something(cls, username, password):
                # Do some stuff
                return {'API Token': 'xyz'}

        * The above example will use the ``Tags.SomeTag`` tag to log the calling and the returning message.
        * The ``cls`` and ``password`` parameters will be masked. The message will show this:

          Called do_something
          Arguments:
          {
              "cls": "********",
              "username": "Admin",
              "password": "********"
          }

        * The output is not masked entirely, but the output will be partially masked like this:

          do_something returned.
          Return Values:
          {
              "API Token": "********"
          }

        * If ``is_static_or_classmethod`` was not set to ``True``, then this wrapper would have failed.

        Args:
            log_tag: The log tag to apply to the input and output log messages.
            mask_input_regexes: A list of regular expressions matching input variable names.
            mask_output: When ``True`` the entire  output is masked like this: "********".
            is_static_or_classmethod: Set this to ``True`` when wrapping a staticmethod or classmethod.
            mask_output_regexes: A list of regular expressions of keys whose values ought to be masked in the
                                 output. This only applies to return values with key/value pair associations.
                                 Use ``mask_output`` if the output is not a dictionary-like object (such as a string).
        """
        log_tag = log_tag or self._log_tags.default
        if isinstance(mask_output_regexes, list):
            with self.logger_lock:
                _LoggerPickler.MASKED_REGEXES = list(set(_LoggerPickler.MASKED_REGEXES + mask_output_regexes))

        def __wrap(func):
            def __wrapper(*args, **kwargs):
                if self._disabled:
                    return func(*args, **kwargs)

                thread = threading.current_thread()
                # If the current thread hasn't been accounted for, account for it by creating a
                # _LogThread using the main thread's configuration.
                if not self._threads.get(thread.ident):
                    mt = self._threads.get(self._main_thread.ident, _LogThread())
                    self._threads[thread.ident] = _LogThread(
                        depth=mt.depth,
                        blacklist_function=mt.blacklist_function,
                        mode=mt.mode,
                        blacklist_log_tag=mt.blacklist_log_tag
                    )

                # Before the function is called.
                try:
                    if is_static_or_classmethod:
                        # staticmethod and classmethod objects inject another argument at index 0.
                        args = args[1:]
                    params = dict(inspect.signature(func).bind(*args, **kwargs).arguments)  # type: dict
                except TypeError as e:
                    self.log(
                        msg='\n'.join(e.args),
                        log_tag=self._log_tags.critical,
                        num_prev_callers=2
                    )
                    raise TypeError(e)

                before_string = 'Called ' + func.__qualname__
                if params:
                    if mask_input_regexes:
                        in_regexes = "(" + ")|(".join(mask_input_regexes) + ")"
                        for key in params.keys():
                            if re.match(pattern=in_regexes, string=key, flags=re.IGNORECASE):
                                params[key] = '********'
                    before_string += '\nArguments:\n' + self._jsonpickle.dumps(params, max_depth=3, unpicklable=False)
                self.log_method(func=func, msg=before_string, log_tag=log_tag, returning=False)
                self._threads[thread.ident].depth += 1
                try:
                    result = func(*args, **kwargs)

                    # After the function returns.
                    after_string = f'{func.__qualname__} returned.'
                    if result is not None:
                        if mask_output:
                            after_string += ' Output is masked.'
                        else:
                            ret_vals = self._jsonpickle.dumps(result, max_depth=3, unpicklable=False)
                            after_string += f'\nReturn Values: {ret_vals}'
                    self.log_method(func=func, msg=after_string, log_tag=log_tag, returning=True)

                    return result
                except:
                    self.log_exception()
                    raise
                finally:
                    self._threads[thread.ident].depth -= 1

            return __wrapper
        return __wrap

    def _commit_log(self, msg: Any, log_tag: LogTag, file_path: str, line_num: int, func: str = None,
                    force: bool = False, no_console: bool = False, no_persistence: bool = False):
        """
        Commits the log transaction to the console and the SQLite DB.

        Args:
            msg: Log message.
            log_tag: The log tag that logs the message. Defaults to the default tag.
            file_path: Absolute path to the file in relation to the log message.
            line_num: Line number in the ``file_path``.
            func: Optional. The qualified name of the function in relation to the ``line_num``.
            force: Optional. If ``True``, then the log thread settings are ignored and the message is logged to
                   the console and, if ``persistent logging==True``, then the message is persisted.
            no_console: Optional. If ``True``, console output will be suppressed unless ```force`` is ``True``.
            no_persistence: Optional. If ``True``, persistence will be suppressed unless ```force`` is ``True``.
        """
        thread = threading.current_thread()
        # If the current thread hasn't been accounted for, account for it by creating a
        # _LogThread using the main thread's configuration.
        if (mt := self._threads.get(thread.ident)) is None:
            mt = self._threads.get(self._main_thread.ident, _LogThread())
            self._threads[thread.ident] = _LogThread(
                depth=mt.depth,
                blacklist_function=mt.blacklist_function,
                mode=mt.mode,
                blacklist_log_tag=mt.blacklist_log_tag
            )

        if (mt.console_enabled and not no_console) or force:
            print(f'[{log_tag.name}] {self._timestamp()}: {msg}')

        if self._persistent_logging and ((mt.persistence_enabled and not no_persistence) or force):
            with self.logger_lock:
                self._sql.log_entries.insert(
                    file_path=file_path,
                    function_name=func,
                    line_num=line_num,
                    msg=str(msg),
                    tag_name=log_tag.name,
                    depth=self._threads[thread.ident].depth,
                    thread_id=thread.ident,
                    thread_name=thread.name,
                    is_main_thread=(thread.ident == self._main_thread.ident)
                )

    def _get_log_info(self, num_prev_callers: int):
        with self.logger_lock:
            frame = inspect.currentframe()
        # Add two because this should only be called once internally.
        outer_frames = inspect.getouterframes(frame)[num_prev_callers + 2]
        if outer_frames.function == '<module>':
            func = inspect.getmodulename(outer_frames.filename)
        else:
            if (class_name := outer_frames[0].f_locals.get('self')) is not None:
                func = f'{class_name.__class__.__qualname__}.{outer_frames.function}'
            else:
                func = outer_frames.function
        return func, outer_frames[1], outer_frames[2]

    def _set_rule(self, log_tag: LogTag = None, min_tag_value: Union[LogTag, int] = None,
                  blacklist_tag_names: List[str] = None, blacklist_function: Callable = None,
                  reset: bool = False, why: str = '', num_prev_callers: int = 0):
        if self._disabled:
            return

        log_tag = log_tag or self._log_tags.default
        thread = threading.current_thread()
        if lt := self._threads.get(thread.ident):
            if lt.blacklist_log_tag and log_tag.value < lt.blacklist_log_tag.value:
                return

        blacklist_log_tag = log_tag
        if blacklist_function:
            msg = f'A function has been defined to decide what is logged.'
        elif min_tag_value:
            if isinstance(min_tag_value, LogTag):
                min_tag_value = min_tag_value.value
            blacklist_function = lambda x: x.value < min_tag_value
            msg = f'Only tag values greater than or equal to {min_tag_value} will be logged.'
        elif blacklist_tag_names:
            blacklist_function = lambda x: x.name in blacklist_tag_names
            msg = f'These tag names are will not be logged: {blacklist_tag_names}'
        elif reset:
            blacklist_function = lambda x: False
            blacklist_log_tag = None
            msg = f'Resetting rule. There are no restrictions to logging in this rule.'
        else:
            blacklist_function = lambda x: False
            blacklist_log_tag = None
            msg = f'No rule defined. There are no restrictions to logging in this rule.'

        func, file_path, line_num = self._get_log_info(num_prev_callers=num_prev_callers)
        self._commit_log(msg=f'{msg}\n{why}', log_tag=log_tag, file_path=file_path, line_num=line_num, func=func)

        if thread.ident == self._main_thread.ident:
            for thread in self._threads.values():
                thread.blacklist_function = blacklist_function
                thread.blacklist_log_tag = blacklist_log_tag
        elif lt := self._threads.get(thread.ident):
            lt.blacklist_function = blacklist_function
            lt.blacklist_log_tag = blacklist_log_tag
        else:
            self._threads[thread.ident] = _LogThread(
                depth=self._threads[self._main_thread.ident].depth,
                blacklist_function=blacklist_function,
                mode=self._threads[self._main_thread.ident].mode,
                blacklist_log_tag=blacklist_log_tag
            )
