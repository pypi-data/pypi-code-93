import datetime
import logging
import logging.handlers
import os
import re
import socket

from stackifyapm.conf import constants
from stackifyapm.utils import compat

__all__ = ("setup_logging", "Config", "setup_stackifyapm_logging")


class ConfigError(ValueError):
    def __init__(self, msg, field_name):
        self.field_name = field_name
        super(ValueError, self).__init__(msg)


class _ConfigValue(object):
    def __init__(self, dict_key, env_key=None, type=compat.text_type, validators=None, default=None, required=False):
        self.type = type
        self.dict_key = dict_key
        self.validators = validators
        self.default = default
        self.required = required

        self.env_key = env_key or "STACKIFY_" + dict_key

    def __get__(self, instance, owner):
        return instance._values.get(self.dict_key, self.default) if instance else self.default

    def __set__(self, instance, value):
        value = self._validate(instance, value)
        instance._values[self.dict_key] = value or self.type(value)

    def _validate(self, instance, value):
        if value is None and self.required:
            raise ConfigError(
                "Configuration error: value for {} is required.".format(self.dict_key), self.dict_key
            )
        if self.validators and value is not None:
            for validator in self.validators:
                value = validator(value, self.dict_key)
        instance._errors.pop(self.dict_key, None)
        return value


class _BoolConfigValue(_ConfigValue):
    def __init__(self, dict_key, true_string="true", false_string="false", **kwargs):
        self.true_string = true_string
        self.false_string = false_string
        super(_BoolConfigValue, self).__init__(dict_key, **kwargs)

    def __set__(self, instance, value):
        if isinstance(value, compat.string_types):
            if value.lower() == self.true_string:
                value = True
            elif value.lower() == self.false_string:
                value = False
        instance._values[self.dict_key] = bool(value)


class RegexValidator(object):
    def __init__(self, regex, verbose_pattern=None):
        self.regex = regex
        self.verbose_pattern = verbose_pattern or regex

    def __call__(self, value, field_name):
        value = compat.text_type(value)
        match = re.match(self.regex, value)
        if match:
            return value
        raise ConfigError("{} does not match pattern {}".format(value, self.verbose_pattern), field_name)


class _ConfigBase(object):
    _NO_VALUE = object()

    def __init__(self, config_dict=None, env_dict=None, inline_dict=None):
        self._values = {}
        self._errors = {}
        if config_dict is None:
            config_dict = {}
        if env_dict is None:
            env_dict = os.environ
        if inline_dict is None:
            inline_dict = {}
        for field, config_value in self.__class__.__dict__.items():
            if not isinstance(config_value, _ConfigValue):
                continue

            new_value = self._NO_VALUE
            if config_value.env_key and config_value.env_key in env_dict:
                new_value = env_dict[config_value.env_key]
            elif config_value.dict_key in config_dict:
                new_value = config_dict[config_value.dict_key]
            elif field in inline_dict or field.upper() in inline_dict:
                new_value = inline_dict.get(field)
                if new_value is None:
                    new_value = inline_dict.get(field.upper())
                if new_value is None:
                    new_value = config_value.default

            if new_value is not self._NO_VALUE:
                try:
                    setattr(self, field, str(new_value))
                except ConfigError as e:
                    self._errors[e.field_name] = str(e)

    @property
    def errors(self):
        return self._errors


class Config(_ConfigBase):
    service_name = _ConfigValue("SERVICE_NAME", validators=[RegexValidator("^[a-zA-Z0-9 _-]+$")], required=True)
    hostname = _ConfigValue("HOSTNAME", default=socket.gethostname())
    capture_body = _ConfigValue("CAPTURE_BODY", default="off")
    async_mode = _BoolConfigValue("ASYNC_MODE", default=True)
    instrument_django_middleware = _BoolConfigValue("INSTRUMENT_DJANGO_MIDDLEWARE", default=True)
    service_version = _ConfigValue("SERVICE_VERSION")
    framework_name = _ConfigValue("FRAMEWORK_NAME", default="")
    framework_version = _ConfigValue("FRAMEWORK_VERSION", default="")
    instrument = _BoolConfigValue("DISABLE_INSTRUMENTATION", default=True)
    base_dir = _ConfigValue("BASE_DIR", default=None)
    application_name = _ConfigValue("APPLICATION_NAME", default=constants.DEFAULT_APPLICATION_NAME)
    environment = _ConfigValue("ENVIRONMENT", env_key="STACKIFY_ENVIRONMENT_NAME", default=constants.DEFAULT_ENVIRONMENT)
    config_file = _ConfigValue("CONFIG_FILE", default=constants.DEFAULT_CONFIG_FILE)
    multiprocessing = _BoolConfigValue("MULTIPROCESSING", default=constants.DEFAULT_MULTIPROCESSING)
    rum_enabled = _BoolConfigValue("RUMV2_ENABLED", env_key="RETRACE_RUMV2_ENABLED", default=constants.DEFAULT_RUM_ENABLED)
    socket_url = _ConfigValue("SOCKET_URL", env_key="STACKIFY_TRANSPORT_SOCKET_PATH", default=constants.DEFAULT_TRANSPORT_SOCKET_FILE)
    transport = _ConfigValue("TRANSPORT", default=constants.DEFAULT_TRANSPORT)
    http_endpoint = _ConfigValue(
        "HTTP_ENDPOINT",
        env_key="STACKIFY_TRANSPORT_HTTP_ENDPOINT",
        validators=[RegexValidator("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")],
        default=constants.DEFAULT_HTTP_ENDPOINT,
    )
    log_path = _ConfigValue("LOG_PATH", env_key="STACKIFY_TRANSPORT_LOG_PATH", default=constants.LOG_PATH)
    debug = _BoolConfigValue("DEBUG", default=constants.DEFAULT_DEBUG)
    queue = _BoolConfigValue("QUEUE", default=constants.DEFAULT_QUEUE)
    lambda_handler = _ConfigValue("LAMBDA_HANDLER", default="")
    prefix_enabled = _BoolConfigValue("PREFIX_ENABLED", default=constants.DEFAULT_PREFIX_ENABLED)
    instrument_all = _BoolConfigValue("INSTRUMENT_ALL", default=constants.DEFAULT_INSTRUMENT_ALL)
    instrument_all_exclude = _ConfigValue("INSTRUMENT_ALL_EXCLUDE", default="")
    rum_script_url = _ConfigValue(
        "RUM_SCRIPT_URL",
        env_key="RETRACE_RUM_SCRIPT_URL",
        validators=[RegexValidator("^((((https?|ftps?|gopher|telnet|nntp)://)|(mailto:|news:))(%[0-9A-Fa-f]{2}|[-\(\)_.!~*';/?:@&=+$,A-Za-z0-9])+)([).!';/?:,][\[:blank:|:blank:\]])?$")],
        default=constants.DEFAULT_RUM_SCRIPT_URL
    )
    rum_key = _ConfigValue(
        "RUM_KEY",
        env_key="RETRACE_RUM_KEY",
        validators=[RegexValidator("^[A-Za-z0-9_-]+$")],
        default=constants.DEFAULT_RUM_KEY
    )


class IncrementalFileHandler(logging.handlers.RotatingFileHandler):
    """
    IncrementalFileHandler specific for Stackify Linux Agent
    """

    def __init__(self, filename, mode='a', maxBytes=0, encoding=None, delay=False):
        logging.handlers.RotatingFileHandler.__init__(
            self,
            filename=filename,
            mode=mode,
            maxBytes=maxBytes,
            backupCount=0,
            encoding=encoding,
            delay=delay,
        )
        self.namer = None
        self.baseFilename = filename
        self.index = 0

    def doRollover(self):
        # close current stream
        if self.stream:
            self.stream.close()
            self.stream = None

        # increase the file index and generate new baseFilename
        self.index = self.index + 1
        self.baseFilename = self.rotation_filename("{}.{}".format(self.baseFilename, self.index))

        # set stream with the new file
        if not self.delay:
            self.stream = self._open()

    def rotation_filename(self, default_name):
        if not callable(self.namer):
            result = default_name
        else:
            result = self.namer(default_name)
        return result

    def emit(self, record):
        # recreate stream file if file was deleted
        if not os.path.exists(self.baseFilename):
            if not self.shouldRollover(record):
                if self.stream:
                    self.stream.close()
                self.stream = self._open()

        logging.handlers.RotatingFileHandler.emit(self, record)

    def _open(self):
        ret = super(IncrementalFileHandler, self)._open()

        # set log file to mod 777
        os.chmod(self.baseFilename, 0o777)

        self._delete_old_files()

        return ret

    def _delete_old_files(self):
        dir_name = os.path.dirname(self.baseFilename)
        try:
            log_files = sorted([
                os.path.join(dir_name, file)
                for file in os.listdir(dir_name)
                if file.endswith('.log')
            ], key=lambda f: os.stat(f).st_mtime)[::-1]

            if len(log_files) > constants.MAX_LOG_FILE_COUNT:
                for file in log_files[constants.MAX_LOG_FILE_COUNT:]:
                    os.path.exists(file) and os.remove(file)
        except Exception:
            pass


class StackifyFormatter(logging.Formatter):
    """
    StackifyFormatter specific for Stackify Windows Agent
    where it will force to show 6 digits for msecs
    """

    def formatTime(self, record, datefmt):
        return datetime.datetime.utcfromtimestamp(record.created).strftime(datefmt)


def setup_logging(client):
    """
    Configure debug loggings for Stackify APM
    """
    debug_path = constants.PREFIX_DEBUG_PATH if client.config.prefix_enabled else constants.LOG_PATH

    try:
        for logger_name in ["stackifyapm", "stackifyapm.traces", "stackifyapm.errors", "stackifyapm.instrument"]:
            _logger = logging.getLogger(logger_name)
            _logger.propagate = False
            _logger.setLevel(logging.DEBUG if client.config.debug else logging.INFO)
            _logger_name = "{}.{}".format(logger_name, "error" in logger_name and "err" or "out")

            if os.path.exists(debug_path):
                _handler = logging.FileHandler("{}{}".format(debug_path, _logger_name))
            else:
                _handler = logging.StreamHandler()

            _logger.addHandler(_handler)

    except Exception:
        pass


def setup_stackifyapm_logging(client):
    """
    Configure loggings to pipe to Stackify Linux Agent
    """
    log_path = constants.PREFIX_LOG_PATH if client.config.prefix_enabled else client.config.log_path

    logger = None
    host_name = client.get_system_info().get("hostname")
    process_id = client.get_process_info().get("pid")
    filename = "{}{}#{}-1.log".format(log_path, host_name, process_id)

    def namer(name):
        num = int(name.split("/")[-1].split(".")[-1] or 0) + 1
        return "{}{}#{}-{}.log".format(log_path, host_name, process_id, num)

    try:
        handler = IncrementalFileHandler(filename, maxBytes=50000000)
        handler.setFormatter(StackifyFormatter("%(asctime)s> %(message)s", '%Y-%m-%d, %H:%M:%S.%f'))
        handler.setLevel(logging.DEBUG)
        handler.namer = namer

        logger = logging.getLogger("stackify_apm")
        logger.propagate = False
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    except Exception:
        print("No such file or directory: {}.".format(log_path))

    return logger
