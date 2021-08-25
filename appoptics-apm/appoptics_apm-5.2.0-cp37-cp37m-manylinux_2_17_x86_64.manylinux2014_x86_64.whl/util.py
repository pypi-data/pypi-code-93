#    Copyright 2021 SolarWinds, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" AppOptics APM instrumentation API for Python.
When imported, the appoptics_apm_init() function will be executed to do some initialization tasks.
"""
import configparser
import inspect
import logging
import os
import re
import sys
import threading
import time
import traceback
import types
from collections import defaultdict, namedtuple
from functools import reduce

from decorator import decorator

import appoptics_apm
import appoptics_apm.ao_logging
import appoptics_apm.transaction_filter
from appoptics_apm.version import __version__

# "invalid name ... For type constant"
# pylint interprets all module-level variables as being 'constants'.
# pylint: disable=C0103

# Agent process start time, which is supposed to be a constant. -- don't modify it.
AGENT_START_TIME = time.time() * 1e6


class OboeTracingMode:
    """Provides an interface to translate the string representation of tracing_mode to the C-extension equivalent."""
    OBOE_SETTINGS_UNSET = -1
    OBOE_TRACE_DISABLED = 0
    OBOE_TRACE_ENABLED = 1

    @classmethod
    def get_oboe_trace_mode(cls, tracing_mode):
        if tracing_mode == 'enabled':
            return cls.OBOE_TRACE_ENABLED
        if tracing_mode == 'disabled':
            return cls.OBOE_TRACE_DISABLED
        return cls.OBOE_SETTINGS_UNSET


# Sample rate configuration sources
OBOE_SAMPLE_RATE_SOURCE_CONTINUED = -1
OBOE_SAMPLE_RATE_SOURCE_FILE = 1
OBOE_SAMPLE_RATE_SOURCE_DEFAULT = 2
OBOE_SAMPLE_RATE_SOURCE_OBOE = 3
OBOE_SAMPLE_RATE_SOURCE_LAST_OBOE = 4
OBOE_SAMPLE_RATE_SOURCE_DEFAULT_MISCONFIGURED = 5
OBOE_SAMPLE_RATE_SOURCE_OBOE_DEFAULT = 6
OBOE_SAMPLE_RATE_SOURCE_CUSTOM = 7

# Masks for bitwise ops
ZERO_MASK = 0b0000000000000000000000000000
SAMPLE_RATE_MASK = 0b0000111111111111111111111111
SAMPLE_SOURCE_MASK = 0b1111000000000000000000000000
ZERO_SAMPLE_RATE_MASK = 0b1111000000000000000000000000
ZERO_SAMPLE_SOURCE_MASK = 0b0000111111111111111111111111


def is_lambda():
    "Checks if agent is running in an AWS Lambda environment." ""
    if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') and os.environ.get("LAMBDA_TASK_ROOT"):
        return True
    return False


util_logger = logging.getLogger(__name__)
reporter_instance = None
_agent_enabled = True
try:
    if os.environ.get('APPOPTICS_AGENT_ENABLED', 'true').lower() == 'false':
        _agent_enabled = False
        util_logger.info(
            "AppOptics agent is disabled and will not report any traces because the environment variable "
            "APPOPTICS_AGENT_ENABLED is set to 'false'! If this is not intended either unset the variable or set it to "
            "a value other than false. Note that the value of APPOPTICS_AGENT_ENABLED is case-insensitive.")
        raise ImportError

    from appoptics_apm.swig.oboe import (
        Context as SwigContext,
        Event as SwigEvent,
        Reporter,
        Metadata,
        Span as SwigSpan,
        CustomMetrics,
        MetricTags,
        Config as SwigConfig,
    )
    if not os.environ.get('APPOPTICS_SERVICE_KEY', None) and not is_lambda():
        util_logger.error("Missing service key. Tracing disabled.")
        _agent_enabled = False
        raise ImportError
except ImportError as e:
    try:
        from appoptics_apm.appoptics_apm_noop import (
            Context as SwigContext,
            Event as SwigEvent,
            Reporter,
            Metadata,
            Span as SwigSpan,
            CustomMetrics,
            MetricTags,
            Config as SwigConfig,
        )

        if _agent_enabled:
            # only log the following messages if agent wasn't explicitly disabled via APPOPTICS_AGENT_ENABLED or due to
            # missing service key
            if sys.platform.startswith('linux'):
                util_logger.warning(
                    """Missing extension library.
                               Tracing is disabled and will go into no-op mode.
                               Contact support@appoptics.com if this is unexpected.
                               Error: %s
                               See: https://docs.appoptics.com/kb/apm_tracing/python/""" % e)
            else:
                util_logger.warning(
                    """Platform %s not yet supported.
                               See: https://docs.appoptics.com/kb/apm_tracing/supported_platforms/
                               Tracing is disabled and will go into no-op mode.
                               Contact support@appoptics.com if this is unexpected.""" % sys.platform)
    except ImportError as err:
        util_logger.error(
            """Unexpected error: %s.
                     Please reinstall or contact support@appoptics.com.""" % err)
    finally:
        # regardless of how we got into this (outer) exception block, the agent will not be able to trace (and thus be
        # disabled)
        _agent_enabled = False


def custom_metrics_summary(name, value, count=1, host_tag=False, service_name=None, tags=None, tags_count=0):
    """
    Creates a new or adds to an existing Summary Metric.

    :param name:str the name of the metrics, a part of the "metric key"
    :param value:float a value to be recorded associated with this "metric key"
    :param count:int (optional) count of metrics being reported, must be a positive integer, default is 1
    :param host_tag:boolean (optional) whether host information should be included, default is False
    :param service_name:str (optional) not yet supported, default is None
    :param tags: (optional) appoptics_apm.MetricTags which holds key/value pairs that describe
           the metric and a part of the "metric key", see example below
    :param tags_count: (optional) if tags is given, this must be set to the count of items in tags
    :return: integer between 0 and 5 corresponding to 0: OBOE_CUSTOM_METRICS_OK
                                                      1: OBOE_CUSTOM_METRICS_INVALID_COUNT
                                                      2: OBOE_CUSTOM_METRICS_INVALID_REPORTER
                                                      3: OBOE_CUSTOM_METRICS_TAG_LIMIT_EXCEEDED
                                                      4: OBOE_CUSTOM_METRICS_STOPPING
                                                      5: OBOE_CUSTOM_METRICS_QUEUE_LIMIT_EXCEEDED

    :example::
        # create a MetricTags object for two tags
        tags_count = 2
        tags = appoptics_apm.MetricTags(tags_count)
        # add tags into MetricTags by specifying the index and tag key and value
        tags.add(0, "Peter", "42")
        tags.add(1, "Paul", "45")
        # submit the metric
        appoptics_apm.custom_metrics_summary("my-summary-metric", 13.04, 1, False, None, tags, tags_count)
    """
    # convert None string to empty value, otherwise will cause oboe segfault
    if tags is None:
        tags = MetricTags(0)
        tags_count = 0
    return CustomMetrics.summary(name, value, count, host_tag, None, tags, tags_count)


def custom_metrics_increment(name, count, host_tag=False, service_name=None, tags=None, tags_count=0):
    """
    Creates a new or adds to an existing Increment Metric.

    :param name:str the name of the metrics, a part of the "metric key"
    :param count:int increment value, must be a positive integer, typically 1
    :param host_tag:boolean (optional) whether host information should be included, default is False
    :param service_name:str (optional) not yet supported, default is None
    :param tags: (optional) appoptics_apm.MetricTags which holds key/value pairs that describe
           the metric and a part of the "metric key", see example below
    :param tags_count: (optional) if tags is given, this must be set to the count of items in tags
    :return: integer between 0 and 5 corresponding to 0: OBOE_CUSTOM_METRICS_OK
                                                      1: OBOE_CUSTOM_METRICS_INVALID_COUNT
                                                      2: OBOE_CUSTOM_METRICS_INVALID_REPORTER
                                                      3: OBOE_CUSTOM_METRICS_TAG_LIMIT_EXCEEDED
                                                      4: OBOE_CUSTOM_METRICS_STOPPING
                                                      5: OBOE_CUSTOM_METRICS_QUEUE_LIMIT_EXCEEDED

    :example::
        # create a MetricTags object for two tags
        tags_count = 2
        tags = appoptics_apm.MetricTags(tags_count)
        # add tags into MetricTags by specifying the index and tag key and value
        tags.add(0, "Peter", "42")
        tags.add(1, "Paul", "45")
        # submit the metric
        appoptics_apm.custom_metrics_increment("my-counter-metric", 1, False, None, tags, tags_count)
    """
    if tags is None:
        tags = MetricTags(0)
        tags_count = 0
    return CustomMetrics.increment(name, count, host_tag, None, tags, tags_count)


_ready = False


def ready():
    """This function is called by functions outside of this module.
    They should not check the value of _ready directly."""
    global _ready
    return _ready


class AppOpticsApmException(Exception):
    """ AppOptics APM Exception Class """


class AppOpticsApmConfig:
    """ AppOptics APM Configuration Class
    The precedence: in-code keyword arguments > Environment Variables > config file > default values.
    Note that oboe doesn't read configurations by itself. The Python agent needs to
    read environment variables and/or config files and pass them into oboe. This is
    done only once during the initialization and the properties cannot be refreshed."""
    supported_instrumentations = (
        'django_orm',
        'httplib',
        'memcache',
        'pymongo',
        'redis',
        'sqlalchemy',
    )
    deprecated = {
        # key: deprecated key, value: the warning message showing the replacement key.
        'reporter_host': 'collector (in `host:port` format)',
        'reporter_port': 'collector (in `host:port` format)',
        'collector_mode': 'reporter',
        'log_level': 'debug_level'
    }
    delimiter = '.'

    def __init__(self, **kwargs):
        self._config = dict()
        # Update the config with default values
        self._config = {
            #'sample_rate' and 'tracing_mode' do not have any default values (i.e. they are unset by default)
            'sample_rate': None,
            'tracing_mode': None,
            'collector': '',  # the collector address in host:port format.
            'reporter': '',  # the reporter mode, either 'udp' or 'ssl'.
            'debug_level': appoptics_apm.ao_logging.AoLoggingLevel.default_level(),
            'warn_deprecated': True,
            'service_key': '',
            'hostname_alias': '',
            'trustedpath': '',
            'events_flush_interval': -1,
            'max_request_size_bytes': -1,
            'ec2_metadata_timeout': 1000,
            'max_flush_wait_time': -1,
            'max_transactions': -1,
            'logname': '',
            'trace_metrics': -1,
            'token_bucket_capacity': -1,
            'token_bucket_rate': -1,
            'bufsize': -1,
            'histogram_precision': -1,
            'reporter_file_single': 0,
            'enable_sanitize_sql': True,
            'inst_enabled': defaultdict(lambda: True),
            'log_trace_id': 'never',
            'proxy': '',
            'transaction': defaultdict(lambda: True),
            'inst': defaultdict(lambda: True),
            'is_grpc_clean_hack_enabled': False,
        }
        self._config['transaction']['prepend_domain_name'] = False
        for inst in self.supported_instrumentations:
            self._config['inst_enabled'][inst] = True
            self._config['inst'][inst] = defaultdict(lambda: True)
            self._config['inst'][inst]['collect_backtraces'] = True
        for inst in ('memcache', 'redis'):
            self._config['inst'][inst]['collect_backtraces'] = False

        cnf_file = os.environ.get('APPOPTICS_APM_CONFIG_PYTHON', os.environ.get('APPOPTICS_PYCONF', None))
        if cnf_file:
            self.update_with_cnf_file(cnf_file)

        self.update_with_env_var()
        self.update_with_kwargs(kwargs)

        util_logger.debug('Instrumentation config : {config}'.format(config=self._config))

    def update_with_kwargs(self, kwargs):
        """Update the configuration settings with (in-code) keyword arguments"""
        for key in kwargs:
            self._set_config_value(key, str(kwargs[key]))

    def update_with_env_var(self):
        """Update the settings with environment variables."""
        val = os.environ.get('APPOPTICS_APM_PREPEND_DOMAIN_NAME', None)
        if val is not None:
            self._set_config_value('transaction.prepend_domain_name', val)
        available_envvs = set(self._config.keys())
        # bucket rate and capacity should be configurable through environment variable only under AWS Lambda
        if not is_lambda():
            available_envvs.remove('token_bucket_capacity')
            available_envvs.remove('token_bucket_rate')

        for key in available_envvs:
            if key in ('inst_enabled', 'transaction', 'inst'):
                # we do not allow complex config options to be set via environment variables
                continue
            env = 'APPOPTICS_' + key.upper()
            val = os.environ.get(env)
            if val is not None:
                self._set_config_value(key, val)

    def _set_config_value(self, keys, val):
        """Sets the value of the config option indexed by 'keys' to 'val', where 'keys' is a nested key (separated by
        self.delimiter, i.e., the position of the element to be changed in the nested dictionary)"""
        def _convert_to_bool(val):
            """Converts given value to boolean value"""
            val = val.lower() if isinstance(val, str) else val
            return val == 'true' if isinstance(val, str) and val in ('true', 'false') else bool(int(val))

        # _config is a nested dict, thus find most deeply nested sub dict according to the provided keys
        # by defaulting to None in d.get(), we do not allow the creation of any new (key, value) pair, even
        # when we are handling a defaultdict (i.e., with this we do not allow e.g. the creation of new instrumentations
        # through the config)
        keys = keys.split(self.delimiter)
        sub_dict = reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) else None, keys[:-1], self._config)
        key = keys[-1]
        try:
            if key in self.deprecated:
                # there are no concatenated keys in deprecated, thus we only need to check key here
                if self._config['warn_deprecated']:
                    util_logger.warning(
                        'Ignore deprecated key: {}, use {} instead.'.format(key, self.deprecated.get(key)))
                return
            if keys == ['sample_rate']:
                sample_rate = float(val)
                if not 0 <= sample_rate <= 1:
                    raise ValueError
                self._config[key] = sample_rate
                SwigContext.setDefaultSampleRate(int(sample_rate * 1e6))
            elif keys == ['ec2_metadata_timeout']:
                timeout = int(val)
                if timeout not in range(0, 3001):
                    raise ValueError
                self._config[key] = timeout
            elif keys == ['token_bucket_capacity']:
                bucket_cap = float(val)
                if not 0 <= bucket_cap <= 8.0:
                    raise ValueError
                self._config[key] = bucket_cap
            elif keys == ['token_bucket_rate']:
                bucket_rate = float(val)
                if not 0 <= bucket_rate <= 4.0:
                    raise ValueError
                self._config[key] = bucket_rate
            elif keys == ['proxy']:
                if not isinstance(val, str) or not val.startswith('http://'):
                    raise ValueError
                self._config[key] = val
            elif keys == ['tracing_mode']:
                if not isinstance(val, str):
                    raise ValueError
                val = val.lower()
                if val in ['always', 'never']:
                    val = 'enabled' if val == 'always' else 'disabled'
                    if self._config['warn_deprecated']:
                        util_logger.warning(
                            'appoptics_apm.config "tracing_mode" configurations "always" and "never" are deprecated.'
                            'Please use "enabled" and "disabled" instead.')
                if val not in ['enabled', 'disabled']:
                    raise ValueError
                self._config[key] = val
                SwigContext.setTracingMode(OboeTracingMode.get_oboe_trace_mode(val))
            elif keys == ['reporter']:
                if not isinstance(val, str) or val.lower() not in ('udp', 'ssl', 'null', 'file', 'lambda'):
                    raise ValueError
                self._config[key] = val.lower()
            elif keys == ['debug_level']:
                val = int(val)
                if not appoptics_apm.ao_logging.AoLoggingLevel.is_valid_level(val):
                    raise ValueError
                self._config[key] = val
                # update loggig level of agent util_logger
                appoptics_apm.ao_logging.set_ao_log_level(val)
            elif keys == ['log_trace_id']:
                if not isinstance(val, str) or val.lower() not in [
                        'never',
                        'sampled',
                        'traced',
                        'always',
                ]:
                    raise ValueError
                self._config[key] = val.lower()
            elif keys == ['is_grpc_clean_hack_enabled']:
                self._config[key] = _convert_to_bool(val)
            elif (keys[0] == 'inst' and keys[1] in self.supported_instrumentations and keys[2] == 'collect_backtraces'):
                self._config[keys[0]][keys[1]][keys[2]] = _convert_to_bool(val)
            elif isinstance(sub_dict, dict) and keys[-1] in sub_dict:
                if isinstance(sub_dict[keys[-1]], bool):
                    val = _convert_to_bool(val)
                else:
                    val = type(sub_dict[keys[-1]])(val)
                sub_dict[keys[-1]] = val
            else:
                util_logger.warning("Ignore invalid configuration key: {}".format('.'.join(keys)))
        except (ValueError, TypeError):
            util_logger.warning(
                'Ignore config option with invalid (non-convertible or out-of-range) type: ' +
                '.'.join(keys if keys[0] not in ['inst', 'transaction'] else keys[1:]))

    def update_with_cnf_file(self, cnf_path):
        """Update the settings with the config file, if any."""

        cnf = configparser.ConfigParser()
        try:
            if not cnf.read(cnf_path):
                util_logger.warning('Failed to open the config file: {}.'.format(cnf_path))
                return
        except configparser.Error as e:
            util_logger.warning('Failed to read or parse config file: {e}'.format(e=e))

        # make sure we are reading the main section first, such that the debug_level can be evaluated before any other
        # configuration option
        sections = cnf.sections()
        if 'main' in sections:
            sections.remove('main')
            sections.insert(0, 'main')

        for section in sections:
            if section in ('main', 'transaction', 'inst'):
                configs = cnf[section]
                if 'debug_level' in configs:
                    # logging level must be set before any other configuration option as other options might emit log
                    # messages
                    debug_level_envv = os.getenv('APPOPTICS_DEBUG_LEVEL', None)
                    if not appoptics_apm.ao_logging.AoLoggingLevel.is_valid_level(debug_level_envv):
                        # environment variables have precedence over config file, and thus log level should only be set
                        # if envv does not exist or is invalid, in order to prevent overriding log level set in
                        # _get_logger
                        self._set_config_value('debug_level', configs['debug_level'])
                    configs.pop('debug_level')
                for key, val in configs.items():
                    self._set_config_value(section + '.' + key if section != 'main' else key, val)
                continue
            # check for custom transaction filter configuration settings
            subsections = section.split(':')
            if len(subsections) == 3 and subsections[0] == 'transaction' and subsections[1] == 'filter':
                # convert custom transaction filter rule into configuration dictionary
                config_dict = cnf[section]
                if not appoptics_apm.transaction_filter.add_transaction_filter_rule(config_dict):
                    util_logger.warning("Ignoring custom transaction setting [{}]".format(section))

            else:
                util_logger.warning('Invalid section: {s} found in {f}'.format(s=section, f=cnf_path))

        if appoptics_apm.transaction_filter.url_filter:
            util_logger.debug(
                "Configured custom transaction filter {}".format(appoptics_apm.transaction_filter.url_filter))

    def __setitem__(self, key, value):
        """Refresh the configurations in liboboe global struct while user changes settings.
        """
        if key == 'tracing_mode':
            self._set_config_value(key, value)

        elif key == 'sample_rate':
            self._set_config_value(key, value)

        elif key == 'log_trace_id':
            self._set_config_value(key, value)
            from appoptics_apm.inst_logging import log_injector
            log_injector.set_injection_mode(self._config[key])

        elif key in ('enable_sanitize_sql', 'warn_deprecated'):
            self._set_config_value(key, value)
        else:
            util_logger.warning('Unsupported AppOptics APM config key: {key}'.format(key=key))

    def __getitem__(self, key):
        return self._config[key]

    def __delitem__(self, key):
        del self._config[key]

    def get(self, key, default=None):
        """ Get the value of key. Nested keys separated by a dot are also accepted."""
        key = key.split(self.delimiter)
        value = reduce(lambda d, k: d.get(k, None) if isinstance(d, dict) else None, key, self._config)
        return value if value is not None else default


class OboeReporterCodes:
    """Return values of Oboe Reporter"""
    OBOE_INIT_ALREADY_INIT = -1
    OBOE_INIT_OK = 0
    OBOE_INIT_WRONG_VERSION = 1
    OBOE_INIT_INVALID_PROTOCOL = 2
    OBOE_INIT_NULL_REPORTER = 3
    OBOE_INIT_DESC_ALLOC = 4
    OBOE_INIT_FILE_OPEN_LOG = 5
    OBOE_INIT_UDP_NO_SUPPORT = 6
    OBOE_INIT_UDP_OPEN = 7
    OBOE_INIT_SSL_CONFIG_AUTH = 8
    OBOE_INIT_SSL_LOAD_CERT = 9
    OBOE_INIT_SSL_REPORTER_CREATE = 10
    OBOE_INIT_SSL_MISSING_KEY = 11

    @classmethod
    def get_text_code(cls, num):
        """Returns the textual representation of the numerical status code."""
        for k, v in cls.__dict__.items():
            if v == num:
                return k
        return None


def appoptics_apm_init():
    """Initialize the instrumentation context:
    1. Load the environment variables.
    2. Create a reporter, either ssl or udp
    3. Get sample configurations from collectors: sample_rate and sample_source"""
    global _ready

    # APPOPTICS_COLLECTOR is fetched by underlying library
    reporter = _reporter()
    if reporter.init_status in (OboeReporterCodes.OBOE_INIT_OK, OboeReporterCodes.OBOE_INIT_ALREADY_INIT):
        # If the agent was explicitly disabled, no tracing should ever happen
        _ready = _agent_enabled
    else:
        util_logger.error(
            "Failed to initialize the reporter, error code=%s (%s)" %
            (reporter.init_status, OboeReporterCodes.get_text_code(reporter.init_status)))


###############################################################################
# Low-level Public API
###############################################################################


def _str_backtrace(backtrace=None):
    """ Return a string representation of an existing or new backtrace """
    if backtrace:
        return "".join(traceback.format_tb(backtrace))
    return "".join(traceback.format_stack()[:-1])


def _collect_backtraces(module_name):
    """ Return the collect backtraces config value for module """
    return appoptics_apm.config['inst'][module_name]['collect_backtraces']


class Context:
    """ A wrapper around the swig Metadata """

    # class scope dict to manage active_instance, transaction_name, and start_time
    # initialize it here (early) in case it is referenced before starting a trace
    transaction_dict = threading.local()

    def __init__(self, md):
        if isinstance(md, str):
            self._md = Metadata.fromString(md)
        else:
            self._md = md
        self.layer = None

    @property
    def md(self):
        return self._md

    # For interacting with SRv1

    @classmethod
    def set_tracing_mode(cls, mode):
        """ Updates liboboe with the configured tracing_mode """
        SwigContext.setTracingMode(mode)

    @classmethod
    def set_default_sample_rate(cls, rate):
        """ Updates liboboe with the configured sample_rate """
        SwigContext.setDefaultSampleRate(rate)

    # For interacting with the thread-local Context

    @classmethod
    def get_default(cls):
        """Returns the Context currently stored as the thread-local default."""
        return cls(SwigContext)

    def set_as_default(self):
        """Sets this object as the thread-local default Context.
        For now the liboboe does not check the validity of the context, it stores a context even
        the option byte is set to not tracing."""
        # We use is_valid() here as we should allow a context with flags=not tracing to be stored
        # in the context thread local storage.
        if self.is_valid():
            SwigContext.set(self._md)

    @classmethod
    def clear_default(cls):
        """Removes the current thread-local Context."""
        SwigContext.clear()

    # For starting/stopping traces
    @classmethod
    def start_trace(cls, layer, xtr=None, url_getter=None):
        """Returns a Context and a start event.
        Takes sampling into account -- may return an (invalid Context, event) pair.
        """
        Context.transaction_dict = threading.local()
        do_sample = sample_request(xtr, url_getter)
        # events are only generated if the request is actually sampled
        raw_evt = None
        # Oboe will set sample_source to OBOE_SAMPLE_RATE_SOURCE_CONTINUED if this is a continued trace
        if getattr(cls.transaction_dict, 'sample_source') == OBOE_SAMPLE_RATE_SOURCE_CONTINUED:
            # continue incoming X-Trace
            md = Metadata.fromString(xtr[:-1] + ('1' if do_sample else '0'))
            if do_sample:
                # since this is a continued trace, we need to add an edge to the start event
                raw_evt = md.createEvent()
        else:
            # there either was no incoming X-Trace, or Oboe decided we can not continue it, thus create a new X-Trace
            md = Metadata.makeRandom(do_sample)
            if do_sample:
                raw_evt = SwigEvent.startTrace(md)

        if raw_evt:
            event = Event(raw_evt, 'entry', layer)
            event.add_info('Language', 'Python')  # in case we have an unclear layer name
            # the below KVs should not be added if this is a continued trace
            if getattr(cls.transaction_dict, 'sample_source') != OBOE_SAMPLE_RATE_SOURCE_CONTINUED:
                event.add_info('SampleRate', getattr(Context.transaction_dict, 'sample_rate'))
                event.add_info('SampleSource', getattr(Context.transaction_dict, 'sample_source'))
                event.add_info('BucketRate', str(getattr(Context.transaction_dict, 'bucket_rate')))
                event.add_info('BucketCapacity', str(getattr(Context.transaction_dict, 'bucket_cap')))
        else:
            event = NullEvent()
        ctx = cls(md)
        ctx.layer = layer
        ctx.set_as_default()
        setattr(Context.transaction_dict, 'start_time', time.time() * 1e6)
        setattr(Context.transaction_dict, 'layer', layer)
        return ctx, event

    def set_transaction_name(self, trans_name=""):
        """ Set transaction name to this trace instance. Note that the transaction name can also be set via the
        APPOPTICS_TRANSACTION_NAME environment variable which has precedence over this function call.

        Keyword and  arguments:
               trans_name -- transaction name to tag this trace instance
        """

        ret_val = False
        if not trans_name:
            util_logger.debug('Invalid transaction name:{n}'.format(n=trans_name))
        elif self.is_valid():
            transaction_name_envv = os.environ.get('APPOPTICS_TRANSACTION_NAME', None)
            if transaction_name_envv:
                util_logger.debug("Transaction name ignored as APPOPTICS_TRANSACTION_NAME environment variable is set.")
            else:
                trans_name = str(trans_name)
                setattr(Context.transaction_dict, 'transaction_name', trans_name)
                ret_val = True
        else:
            util_logger.debug("Transaction name ignored as current execution flow is not monitored by agent")
        return ret_val

    def get_transaction_name(self):
        """ Get transaction name of this trace instance"""
        transaction_name_envv = os.environ.get('APPOPTICS_TRANSACTION_NAME', None)
        if transaction_name_envv:
            return transaction_name_envv
        else:
            return getattr(Context.transaction_dict, 'transaction_name', None)

    def end_trace(self, event, has_error=False):  # Reports the last event in a trace
        """Ends this trace, rendering this Context invalid.
           submit inbound metrics and get final transaction name
           update event info with transaction name

           Keyword arguments:
           self -- this context instance
           event -- last trace event
           has_error -- indicates if an error occurred in this span (only honoured in non-http spans)
        """
        http_span = getattr(Context.transaction_dict, 'http', None)
        do_metrics = getattr(Context.transaction_dict, 'do_metrics', None)
        trans_name = self.get_transaction_name()
        url_tran = getattr(Context.transaction_dict, 'url_tran', None)
        # non-http requests are not subject to transaction filtering and should always report metrics
        if not http_span or do_metrics:
            end_time = time.time() * 1e6
            domain = getattr(Context.transaction_dict, 'domain', None)
            if not appoptics_apm.config['transaction']['prepend_domain_name']:
                domain = None
            if domain is not None and len(domain.split(":")) > 1:
                port = domain.split(":")[1]
                if port in ('80', '443'):
                    domain = domain.split(":")[0]

            start_time = getattr(Context.transaction_dict, 'start_time', None)
            if start_time is None:
                start_time = end_time
                util_logger.debug('trace start_time not recorded')
            else:
                start_time = int(start_time)
            span_time = int(end_time - start_time)

            try:
                if http_span:
                    request_method = getattr(Context.transaction_dict, 'request_method', None)
                    status_code = getattr(Context.transaction_dict, 'status_code', None)
                    if request_method is None or status_code is None:
                        util_logger.debug(
                            'http_span request info error request_method: {r}, status_code: {s}'.format(
                                r=request_method, s=status_code))
                    if trans_name is None and url_tran is None:
                        util_logger.debug(
                            'http_span error: transaction_name is None, \
                                    use set_transaction_name("transaction_name") to set')
                    if status_code is None:
                        status_code = 0
                    has_error = bool(status_code > 499) and bool(status_code < 600)
                    trans_name = SwigSpan.createHttpSpan(
                        trans_name, url_tran, domain, span_time, status_code, request_method, has_error)
                else:
                    trans_name = SwigSpan.createSpan(trans_name, domain, span_time, has_error)
                util_logger.debug(
                    'create span: http: {http}, transaction_name: {xn}, duration: {duration}us.'.format(
                        http=http_span, xn=trans_name, duration=span_time))
            except Exception as e:
                util_logger.error('appoptics_apm::end_trace create SPAN fail: {0}'.format(e))

        # If request is not sampled, we do not need to add the following KVs since the event will not be reported.
        if self.is_sampled() and isinstance(event, Event):
            event.add_info('TransactionName', trans_name)
            if http_span:
                event.add_info('Spec', 'ws')
                event.add_info('HTTPMethod', getattr(Context.transaction_dict, 'request_method', None))
                event.add_info('HTTP-Host', getattr(Context.transaction_dict, 'domain', None))
                forwarded_host = getattr(Context.transaction_dict, 'forwarded_host', None)
                if forwarded_host:
                    event.add_info('Forwarded-Host', forwarded_host)
                event.add_info('URL', url_tran)
                event.add_info('Status', getattr(Context.transaction_dict, 'status_code', 0))
            self.report(event)
        _reporter().flush()
        self._md = None
        Context.clear_default()

    def create_event(self, label, layer):
        """Returns an Event associated with this Context."""
        if self.is_sampled() or label == 'exit':
            return Event(self._md.createEvent(), label, layer)
        return NullEvent()

    def report(self, event):
        """Report this Event.
        -------------------------------------------------------------------------------
        | Please note that we don't need to update the current op_id to the context   |
        | as the liboboe helps to do that in functions: oboe_send_event() -->         |
        | oboe_ids_set_op_id(). There is a risk for now that if the reporter fails to |
        | send the event out, the chain will be broken.                               |
        -------------------------------------------------------------------------------
        """
        if self.is_sampled() and event.is_valid():
            _reporter().sendReport(event.evt)
            util_logger.debug('report event: {e}'.format(e=event))

    def report_status(self, event):
        """Report with postStatus() Thrift API. It's mainly for the __Init message
        A code refactoring may be needed here for the boilerplate code"""
        if self.is_sampled() and event.is_valid():
            _reporter().sendStatus(event.evt)

    def is_valid(self):
        """Returns whether this Context is valid.

        Call this before doing expensive introspection. If this returns False,
        then the context is not valid for moving forward to next step.
        """
        return self._md and self._md.isValid()

    def is_sampled(self):
        """Returns whether this Context is sampled.

        Call this before doing expensive introspection. If this returns False,
        then any event created by this Context will not actually return
        information to AppOptics APM.
        """
        return self.is_valid() and self.md.isSampled()

    def copy(self):
        """Make a clone of this Context."""
        return self.__class__(self._md.toString())

    def __str__(self):
        if self._md:
            return self._md.toString()
        return ''


class Event:
    """An Event is a key/value bag that will be reported to the Tracelyzer."""
    def __init__(self, raw_evt, label, layer):
        self._evt = raw_evt
        self._evt.addInfo('Label', label)
        self._evt.addInfo('Layer', layer)
        # for __repr__ only, as the KVs are hard to be decoded once encoded with oboe
        self.label = label
        self.layer = layer

    @property
    def evt(self):
        return self._evt

    def add_edge(self, ctx):
        """Connect an additional Context to this Event.

        All Events are created with an edge pointing to the previous Event. This
        creates an additional edge. This pattern is useful for entry/exit pairs
        in a layer.
        """
        if ctx.md == SwigContext:
            self._evt.addEdge(ctx.md.get())
        else:
            self._evt.addEdge(ctx.md)

    def add_edge_str(self, xtr):
        """Adds an edge to this Event, based on a str(Context).

        Useful for continuing a trace, e.g., from an X-Trace header in a service
        call.
        """
        self._evt.addEdgeStr(xtr)

    def add_info(self, key, value):
        """Add a key/value pair to this event."""
        self._evt.addInfo(key, value)

    def add_backtrace(self, backtrace=None):
        """Add a backtrace to this event.

        If backtrace is None, grab the backtrace from the current stack trace.
        """
        self.add_info('Backtrace', _str_backtrace(backtrace))

    @staticmethod
    def is_valid():
        """Returns whether this event will be reported to the Tracelyzer."""
        return True

    def id(self):
        """Returns a string version of this Event.

        Useful for attaching to output service calls (e.g., an X-Trace request
        header).
        """
        return self._evt.metadataString()

    def __repr__(self):
        """
        The representation of the key values of the event.
        :return: a string represents the Event object.
        """
        rp = u"Event(id={id}, layer={layer}, label={label})".format(
            id=self.id(),
            layer=self.layer,
            label=self.label,
        )

        return str(rp)


class NullEvent:
    """Subclass of event that will not be reported to the Tracelyzer.

    All methods here are no-ops. Checking for this class can be done
    (indirectly) by calling is_valid() on an object.
    """
    def __init__(self):
        pass

    def add_edge(self, event):
        pass

    def add_edge_str(self, op_id):
        pass

    def add_info(self, key, value):
        pass

    def add_backtrace(self, backtrace=None):
        pass

    @staticmethod
    def is_valid():
        return False

    @staticmethod
    def id():
        return ''


###############################################################################
# High-level Public API
###############################################################################

try:
    from io import StringIO

    import cProfile
    import pstats

    found_cprofile = True
except ImportError:
    found_cprofile = False


def _get_profile_info(p):
    """Returns a sorted set of stats from a cProfile instance."""
    sio = StringIO()
    s = pstats.Stats(p, stream=sio)
    s.sort_stats('time')
    s.print_stats(15)
    stats = sio.getvalue()
    sio.close()
    return stats


def _update_event(evt, keys=None, store_backtrace=True, backtrace=None, edge_str=None):
    """Add the backtrace and edge to the event
    """
    keys = keys or {}

    if isinstance(keys, dict):
        for k, v in keys.items():
            evt.add_info(k, v)
    else:
        util_logger.debug('_update_event type of {keys} is : {t}' 'not dict type'.format(keys=keys, t=type(keys)))

    if store_backtrace:
        evt.add_backtrace(backtrace)

    if edge_str:
        evt.add_edge_str(edge_str)
    return evt


def _sanitize_sql(sql_statement=""):
    """ sanitize sql statement
    """
    # regex only works on str type, if it's bytes, decode it
    sql = sql_statement.decode() if isinstance(sql_statement, bytes) else str(sql_statement)

    # replace '...' "..." with ? and keep '', "" intact
    # replace single quotes
    sql = re.sub(r"(?!'')(?<!')'[^']+'", "?", sql)
    # replace double quotes
    sql = re.sub(r'(?!"")(?<!")"[^"]+"', '?', sql)

    # replace number literals to ?
    sql = re.sub(
        r'([^a-zA-Z_0-9\.]+)'  # excludes leading field names
        r'([1-9]\d*\.?\d*|0\.\d*|'  # decimal number
        r'0[xX][1-9a-fA-F][0-9a-fA-F]*\.?[0-9a-fA-F]*|0[xX]0\.[0-9a-fA-F]*|'  # hex number
        r'0[1-7][0-7]*\.?[0-7]*|00\.[0-7]*)',  # oct number
        r"\g<1>0",
        sql)
    # we leave it a byte string if the query was in form of a byte string before
    return sql.encode() if isinstance(sql_statement, bytes) else sql


def _log_event(evt, keys=None, store_backtrace=True, backtrace=None, edge_str=None):
    """Add the backtrace and edge, then send it out to the reporter.
    """

    if isinstance(keys, dict) and 'Query' in keys and appoptics_apm.config['enable_sanitize_sql']:
        keys['Query'] = _sanitize_sql(keys['Query'])

        if 'QueryArgs' in keys:
            del keys['QueryArgs']

    evt = _update_event(evt, keys, store_backtrace, backtrace, edge_str)
    ctx = Context.get_default()
    ctx.report(evt)


def log(label, layer, keys=None, store_backtrace=True, backtrace=None, edge_str=None):
    """Report a single tracing event.

    :label: 'entry', 'exit', 'info', or 'error'
    :layer: The layer name
    :keys: A optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    ctx = Context.get_default()
    if not ctx.is_sampled():
        return
    evt = ctx.create_event(label, layer)
    _log_event(evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace, edge_str=edge_str)


def start_trace(layer, xtr=None, keys=None, store_backtrace=True, backtrace=None):
    """Start a new trace, or continue one from an external layer.

    :layer: The layer name of the root of the trace.
    :xtr: The X-Trace ID to continue this trace with.
    :keys: An optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    keys = keys or {}

    ctx, evt = Context.start_trace(layer, xtr=xtr)

    if ctx.is_valid():  # Set it to the thread local storage even it's not sampled.
        ctx.set_as_default()

    if ctx.is_sampled():
        _log_event(evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace)

    return ctx


def start_http_trace(
        layer, xtr=None, keys=None, store_backtrace=True, backtrace=None, transaction_name=None, url_getter=None):
    """Start a new http trace, or continue one from an external layer.

    :layer: The layer name of the root of the trace.
    :xtr: The X-Trace ID to continue this trace with.
    :keys: An optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    :transaction_name: The name of the traced transaction. Default: None
    :url_getter: UrlGetter instance to provide the request URL
    """
    keys = keys or {}

    ctx, evt = Context.start_trace(layer, xtr=xtr, url_getter=url_getter)

    if ctx.is_valid():  # Set it to the thread local storage even it's not sampled.
        ctx.set_as_default()
        if transaction_name is not None:
            ctx.set_transaction_name(transaction_name)

    if ctx.is_sampled():
        _log_event(evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace)

    return ctx


def end_trace(layer, keys=None, http=False, has_error=False):
    """End a trace, reporting a final event.

    This will end a trace locally. If the X-Trace ID returned here is reported
    externally, other processes can continue this trace.

    :layer: The layer name of the final layer.
    :keys: An optional dictionary of key-value pairs to report.
    :http: A flag indicates http span for True or non for False
    :has_error: A flag indicating if an error occurred in this span
    """
    setattr(Context.transaction_dict, 'http', http)
    if not http:
        setattr(Context.transaction_dict, 'domain', None)
        setattr(Context.transaction_dict, 'request_method', None)

    ctx = Context.get_default()
    evt = ctx.create_event('exit', layer)
    if ctx.is_sampled():
        evt = _update_event(evt, keys=keys, store_backtrace=False)
    ctx.end_trace(evt, has_error=has_error)

    return evt.id()


def end_http_trace(layer, keys=None):
    """End a trace, reporting a final event.

    This will end a trace locally. If the X-Trace ID returned here is reported
    externally, other processes can continue this trace.

    :layer: The layer name of the final layer.
    :keys: An optional dictionary of key-value pairs to report.
    """
    # is this check necessary and can we move it to the end_trace() call?
    if not isinstance(layer, str):
        util_logger.debug('Layer {layer} should be a string, got {type}'.format(layer=layer, type=type(layer)))
        layer = str(layer)
    return end_trace(layer, keys, True)


def set_request_info(host=None, status_code=None, method=None, full_path=None):
    """set or update http span info for current request

      this setting only take effect if currently there is an active tracing
      instance

      Keywords and parameters:
          host -- request host name
          status_code -- response status code
          method -- request method
          full_path -- full uri
    """

    if status_code is not None:
        setattr(Context.transaction_dict, 'status_code', status_code)
    if method is not None:
        setattr(Context.transaction_dict, 'request_method', method)
    if host is not None:
        setattr(Context.transaction_dict, 'domain', host)
    if full_path is not None:
        setattr(Context.transaction_dict, 'url_tran', full_path)


def log_entry(layer, keys=None, store_backtrace=True, backtrace=None):
    """Report the first event of a new layer.

    :layer: The layer name.
    :keys: An optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    ctx = Context.get_default()
    if not ctx.is_sampled():
        return
    evt = ctx.create_event('entry', layer)
    _log_event(evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace)


def log_error(err_class, err_msg, store_backtrace=True, backtrace=None):
    """Report an error event.

    :err_class: The class of error to report, e.g., the name of the Exception.
    :err_msg: The specific error that occurred.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    ctx = Context.get_default()
    if not ctx.is_sampled():
        return

    layer = getattr(Context.transaction_dict, 'layer', None)
    evt = ctx.create_event('error', layer)
    util_logger.debug('log_error create event: {e}, for layer:{l}'.format(e=evt, l=layer))
    keys = {
        'Spec': 'error',
        'ErrorClass': err_class,
        'ErrorMsg': err_msg,
    }
    _log_event(evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace)


def log_exception(msg=None, store_backtrace=True):
    """Report the last thrown exception as an error

    :msg: An optional message, to override err_msg. Defaults to str(Exception).
    :store_backtrace: Whether to store the Exception backtrace.
    """
    typ, val, tb = sys.exc_info()
    try:
        if typ is None:
            util_logger.debug('log_exception should only be called from an exception context ' '(e.g., except: block)')
            return

        if msg is None:
            try:
                msg = str(val)
            except Exception:
                msg = repr(val)

        log_error(typ.__name__, msg, store_backtrace=store_backtrace, backtrace=tb if store_backtrace else None)
    finally:
        del tb  # delete reference to traceback object to allow garbage collection


def log_exit(layer, keys=None, store_backtrace=True, backtrace=None, edge_str=None):
    """Report the last event of the current layer.

    :layer: The layer name.
    :keys: An optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    ctx = Context.get_default()
    if not ctx.is_sampled():
        return
    evt = ctx.create_event('exit', layer)
    util_logger.debug('log_exit create event: {e}'.format(e=evt))
    _log_event(evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace, edge_str=edge_str)


def set_transaction_name(trans_name=""):
    """ Sets a transaction name to the current active trace, the transaction name will
    be reported along with the corresponding trace and metrics.
    This overrides the transaction name provided by out-of-the-box instrumentation, but it will not override the value
    provided by APPOPTICS_TRANSACTION_NAME environment variable. This means, if the APPOPTICS_TRANSACTION_NAME is set
    and is a non-empty string, this function will have no effect and False will be returned.

    If multiple transaction names are set on the same trace, then the last one would be used.
    Take note that transaction name might be truncated with invalid characters replaced.

    Keyword arguments:
    trans_name -- customer defined transaction name
    return -- result of setting, True for success
    """

    ctx = Context.get_default()
    ret = ctx.set_transaction_name(trans_name)
    util_logger.debug('set_transaction_name:{n} returns  {r}'.format(n=trans_name, r=ret))
    return ret


def get_transaction_name():
    """ Returns the currently set custom transaction name, if any. """

    ctx = Context.get_default()
    return ctx.get_transaction_name()


def last_id():
    """Returns a string representation the last event reported."""
    return str(Context.get_default())


###############################################################################
# Python-specific functions
###############################################################################


def _function_signature(func):
    """Returns a string representation of the function signature of the given func."""
    name = func.__name__
    (args, varargs, keywords, defaults) = inspect.getargspec(func)  # pylint: disable-msg=W1505
    argstrings = []
    if defaults:
        first = len(args) - len(defaults)
        argstrings = args[:first]
        for i in range(first, len(args)):
            d = defaults[i - first]
            if isinstance(d, str):
                d = "'" + d + "'"
            else:
                d = str(d)
            argstrings.append(args[i] + '=' + d)
    else:
        argstrings = args
    if varargs:
        argstrings.append('*' + varargs)
    if keywords:
        argstrings.append('**' + keywords)
    return name + '(' + ', '.join(argstrings) + ')'


def trace(layer='Python', xtr_hdr=None, kvs=None):
    """ Decorator to begin a new trace on a block of code.  Takes into account
    appoptics_apm.config['tracing_mode'] as well as appoptics_apm.config['sample_rate'], so may
    not always start a trace.

    :layer: layer name to report as
    :xtr_hdr: optional, incoming x-trace header if available
    :kvs: optional, dictionary of additional key/value pairs to report
    """
    def _trace_wrapper(func, *f_args, **f_kwargs):
        start_trace(layer, keys=kvs, xtr=xtr_hdr)
        try:
            res = func(*f_args, **f_kwargs)
        except Exception:
            # log exception and re-raise
            log_exception()
            raise
        finally:
            end_trace(layer)

        return res  # return output of func(*f_args, **f_kwargs)

    _trace_wrapper._appoptics_apm_wrapped = True  # mark our wrapper for protection below

    # instrumentation helper decorator, called to add wrapper at "decorate" time
    def decorate_with_trace(f):
        if getattr(f, '_appoptics_apm_wrapped', False):  # has this function already been wrapped?
            return f  # then pass through
        return decorator(_trace_wrapper, f)  # otherwise wrap function f with wrapper

    return decorate_with_trace


class profile_block:
    """A context manager for AppOptics APM profiling a block of code with AppOptics APM lib.

    Reports an error event between entry and exit if an exception is thrown,
    then reraises.

    :profile_name: the profile name to use when reporting.  this should be
        unique to the profiled method.
    :store_backtrace: whether to capture a backtrace or not (False)
    :profile: profile this function with cProfile and report the result
    """
    def __init__(self, profile_name, profile=False, store_backtrace=False):
        self.profile_name = profile_name
        self.use_cprofile = profile
        self.backtrace = store_backtrace
        self.p = None  # possible cProfile.Profile() instance

    def __enter__(self):
        ctx = Context.get_default()
        if not ctx.is_sampled():
            return

        # build entry event
        entry_kvs = {
            'Language': 'python',
            'ProfileName': self.profile_name,
            # XXX We can definitely figure out a way to make these
            # both available and fast.  For now, this is ok.
            'File': '',
            'LineNumber': 0,
            'Module': '',
            'FunctionName': '',
            'Signature': ''
        }
        log('profile_entry', None, keys=entry_kvs, store_backtrace=self.backtrace)

        # begin profiling
        if self.use_cprofile and found_cprofile:
            self.p = cProfile.Profile()
            self.p.enable(subcalls=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        ctx = Context.get_default()
        if not ctx.is_sampled():
            return

        # end profiling
        stats = None
        if self.use_cprofile and found_cprofile and self.p:
            stats = _get_profile_info(self.p)

        # exception?
        if exc_type:
            log_exception()

        # build exit event
        exit_kvs = {}
        if self.use_cprofile and stats:
            exit_kvs['ProfileStats'] = stats
        exit_kvs['Language'] = 'python'
        exit_kvs['ProfileName'] = self.profile_name

        log('profile_exit', None, keys=exit_kvs, store_backtrace=self.backtrace)


def profile_function(
        profile_name,
        store_args=False,
        store_return=False,
        store_backtrace=False,
        profile=False,
        callback=None,
        entry_kvs=None):
    """Wrap a method for tracing and profiling with the AppOptics APM library.

    Reports an error event between entry and exit if an exception is thrown,
    then reraises.

    :profile_name: the profile name to use when reporting.  this should be
        unique to the profiled method.
    :store_return: report the return value of this function
    :store_args: report the arguments to this function
    :store_backtrace: whether to capture a backtrace or not (False)
    :profile: profile this function with cProfile and report the result
    :callback: if set, calls this function after the wrapped function returns,
        which examines the function, arguments, and return value, and may add
        more K/V pairs to the dictionary to be reported
    """
    def before(func, f_args, f_kwargs):
        # get filename, line number, etc, and cache in wrapped function to avoid overhead
        def cache(name, value_func):
            try:
                if not hasattr(func, name):
                    setattr(func, name, value_func())
            except Exception:
                setattr(func, name, None)

        cache('_appoptics_apm_file', lambda: inspect.getsourcefile(func))
        cache('_appoptics_apm_line_number', lambda: inspect.getsourcelines(func)[1])
        cache('_appoptics_apm_module', lambda: inspect.getmodule(func).__name__)
        cache('_appoptics_apm_signature', lambda: _function_signature(func))

        keys = {
            'Language': 'python',
            'ProfileName': profile_name,
            'File': getattr(func, '_appoptics_apm_file'),
            'LineNumber': getattr(func, '_appoptics_apm_line_number'),
            'Module': getattr(func, '_appoptics_apm_module'),
            'FunctionName': getattr(func, '__name__'),
            'Signature': getattr(func, '_appoptics_apm_signature')
        }
        return f_args, f_kwargs, keys

    def after(func, f_args, f_kwargs, res):

        kvs = {
            'Language': 'python',
            'ProfileName': profile_name,
        }

        if callback:
            user_kvs = callback(func, f_args, f_kwargs, res)
            if user_kvs:
                kvs.update(user_kvs)

        return kvs

    # Do function passed in here expect to be bound (have im_func/im_class)?

    return log_method(
        None,
        store_return=store_return,
        store_args=store_args,
        store_backtrace=store_backtrace,
        before_callback=before,
        callback=after,
        profile=profile,
        entry_kvs=entry_kvs)


def log_method(
        layer,
        store_return=False,
        store_args=False,
        store_backtrace=False,
        before_callback=None,
        callback=None,
        profile=False,
        entry_kvs=None,
        send_entry_event=True,
        send_exit_event=True,
        except_send_exit_event=False):
    """Wrap a method for tracing with the AppOptics APM library.

    As opposed to profile_function, this decorator gives the method its own layer

    Reports an error event between entry and exit if an exception is thrown,
    then reraises.

    :layer: the layer to use when reporting. If none, this layer will be a
        profile.
    :store_return: report the return value
    :store_args: report the arguments to this function
    :before_callback: if set, calls this function before the wrapped function is
        called. This function can change the args and kwargs, and can return K/V
        pairs to be reported in the entry event.
    :callback: if set, calls this function after the wrapped function returns,
        which examines the function, arguments, and return value, and may add
        more K/V pairs to the dictionary to be reported
    """
    if not entry_kvs:
        entry_kvs = {}

    # run-time event-reporting function, called at each invocation of func(f_args, f_kwargs)

    def _log_method_wrapper(func, *f_args, **f_kwargs):
        log_exit_event = send_exit_event
        ctx = Context.get_default()
        # ctx should never be None, checking here in case
        if ctx is None or not ctx.is_sampled() or not ready():
            if ctx is None:
                util_logger.error("util._log_method_wrapper failed to get default context")
            return func(*f_args, **f_kwargs)  # pass through to func right away
        if store_args:
            entry_kvs.update({'args': f_args, 'kwargs': f_kwargs})
        if before_callback:
            before_res = before_callback(func, f_args, f_kwargs)
            if before_res:
                f_args, f_kwargs, extra_entry_kvs = before_res
                entry_kvs.update(extra_entry_kvs)
        if store_backtrace:
            entry_kvs['Backtrace'] = _str_backtrace()
        # is func an instance method?
        if 'im_class' in dir(func):
            entry_kvs['Class'] = func.im_class.__name__

        if send_entry_event:
            # log entry event
            if layer is None:
                log('profile_entry', layer, keys=entry_kvs, store_backtrace=False)
            else:
                log('entry', layer, keys=entry_kvs, store_backtrace=False)

        res = None  # return value of wrapped function
        stats = None  # cProfile statistics, if enabled
        try:
            if profile and found_cprofile:  # use cProfile?
                p = cProfile.Profile()
                res = p.runcall(func, *f_args, **f_kwargs)  # call func via cProfile
                stats = _get_profile_info(p)
            else:  # don't use cProfile, call func directly
                res = func(*f_args, **f_kwargs)
        except Exception:
            # log exception and re-raise
            log_exit_event = log_exit_event or except_send_exit_event
            log_exception()
            raise
        finally:
            # prepare data for reporting exit event
            exit_kvs = {}
            edge_str = None

            # call the callback function, if set, and merge its return
            # values with the exit event's reporting data
            if callback and callable(callback):
                try:
                    cb_ret = callback(func, f_args, f_kwargs, res)
                    # callback can optionally return a 2-tuple, where the
                    # second parameter is an additional edge to add to
                    # the exit event
                    if isinstance(cb_ret, tuple) and len(cb_ret) == 2:
                        cb_ret, edge_str = cb_ret
                    if cb_ret:
                        exit_kvs.update(cb_ret)
                except Exception:
                    # should be no user exceptions here; it's a trace-related callback
                    type_, msg_, bt_ = sys.exc_info()
                    util_logger.debug(
                        "Non-fatal error in log_method callback: %s, %s, %s" % (str(type_), msg_, _str_backtrace(bt_)))
                    del bt_

            # (optionally) report return value
            if store_return:
                exit_kvs['ReturnValue'] = str(res)

            # (optionally) report profiler results
            if profile and stats:
                exit_kvs['ProfileStats'] = stats

            if log_exit_event:
                # log exit event
                if layer is None:
                    log('profile_exit', layer, keys=exit_kvs, store_backtrace=False, edge_str=edge_str)
                else:
                    log('exit', layer, keys=exit_kvs, store_backtrace=False, edge_str=edge_str)
        return res  # return output of func(*f_args, **f_kwargs)

    _log_method_wrapper._appoptics_apm_wrapped = True  # mark our wrapper for protection below

    # instrumentation helper decorator, called to add wrapper at "decorate" time
    def decorate_with_log_method(f):
        if getattr(f, '_appoptics_apm_wrapped', False):  # has this function already been wrapped?
            return f  # then pass through
        if hasattr(f, '__func__'):  # Is this a bound method of an object
            f = f.__func__  # then wrap the unbound method
        util_logger.debug('decorate_with_log_method wraps: {f}'.format(f=f.__name__))
        return decorator(_log_method_wrapper, f)  # otherwise wrap function f with wrapper

    # return decorator function with arguments to log_method() baked in
    return decorate_with_log_method


def _reporter():
    """A reporter has already been initialized by appoptics_apm_init() when appoptics_apm is imported.
    However, when a new child process is forked it needs its own reporter. Inside oboe_init_reporter()
    it will check if the current pid matches the stored one, if not it will create a new reporter."""

    global reporter_instance

    if not reporter_instance:
        reporter_instance = Reporter(
            hostname_alias=appoptics_apm.config.get('hostname_alias'),
            log_level=appoptics_apm.config.get('debug_level'),
            log_file_path=appoptics_apm.config.get('logname'),
            max_transactions=appoptics_apm.config.get('max_transactions'),
            max_flush_wait_time=appoptics_apm.config.get('max_flush_wait_time'),
            events_flush_interval=appoptics_apm.config.get('events_flush_interval'),
            max_request_size_bytes=appoptics_apm.config.get('max_request_size_bytes'),
            reporter=appoptics_apm.config.get('reporter'),
            host=appoptics_apm.config.get('collector'),
            service_key=appoptics_apm.config.get('service_key'),
            trusted_path=appoptics_apm.config.get('trustedpath'),
            buffer_size=appoptics_apm.config.get('bufsize'),
            trace_metrics=appoptics_apm.config.get('trace_metrics'),
            histogram_precision=appoptics_apm.config.get('histogram_precision'),
            token_bucket_capacity=appoptics_apm.config.get('token_bucket_capacity'),
            token_bucket_rate=appoptics_apm.config.get('token_bucket_rate'),
            file_single=appoptics_apm.config.get('reporter_file_single'),
            ec2_metadata_timeout=appoptics_apm.config.get('ec2_metadata_timeout'),
            grpc_proxy=appoptics_apm.config.get('proxy'),
            stdout_clear_nonblocking=0,
            is_grpc_clean_hack_enabled=appoptics_apm.config.get('is_grpc_clean_hack_enabled'),
        )

    return reporter_instance


def _Event_addInfo_safe(func):
    def wrapped(*args, **kw):
        try:
            if args[1] is None:
                # SWIG-generated Event.addInfo does not accept None types as keys, thus we need to manually convert
                # them to a "None" string
                args = (args[0], str(args[1]), args[2])
            return func(*args)
        except (TypeError, IndexError):
            # SWIG-generated Event.addInfo did either receive a wrong number of arguments, or objects of a type it can
            # not process
            if len(args) != 3:
                # wrong number of arguments was provided, we cannot do anything about this except logging this issue
                util_logger.error(
                    '_Event_addInfo_safe: event.add_info provided with wrong number of arguments: Expected an event '
                    ' object, a key and value parameter, but got following arguments instead: %s.' % (args, ))
                return False
            # the key part of a key-value pair must be a string, attempt to convert it into one if necessary
            if not isinstance(args[1], str):
                try:
                    args = (args[0], str(args[1]), args[2])
                except Exception:
                    util_logger.error(
                        '_Event_addInfo_safe: event.add_info wrong key type: Bad type for key. Key object must be '
                        'convertible to a string, but object of type %s does not have a string representation.' %
                        (type(args[1])))
                    return False
            # the value part of the key-value pair can only be of certain types, thus we try to convert objects of an
            # unsupported type into a string
            allowed_types = (int, float, bool, str)
            if isinstance(args[2], bytes):
                # bytes type needs to be decoded into a string otherwise, it would result in "b'string content'"
                try:
                    args = (args[0], args[1], args[2].decode(errors='backslashreplace'))
                except LookupError:
                    args = (args[0], args[1], args[2].decode(errors='ignore'))
            elif type(args[2]) not in allowed_types:
                # try to convert the object of unsupported type to a string and intercept possible errors
                try:
                    args = (args[0], args[1], str(args[2]))
                except Exception:
                    util_logger.error(
                        '_Event_addInfo_safe: event.add_info wrong value type: value object must be one of %s or have a'
                        ' string representation, but found object of type %s.' % (allowed_types, type(args[2])))
                    return False
            return func(*args)

    return wrapped


def sample_request(xtr, url_getter):
    """This functions calls the liboboe API to get the sampling decision. A side effect
    is to get the server-side sample_rate and sample_source.
    """
    args = [xtr, appoptics_apm.transaction_filter.url_filter.filter_url_and_get_tracing(url_getter)
            ] if appoptics_apm.transaction_filter.url_filter and url_getter else [xtr]

    SampleDecisions = namedtuple(
        'SampleDecisions',
        'do_metrics do_sample sample_rate sample_source bucket_rate bucket_cap typ auth status_msg auth_msg status')

    try:
        res = SampleDecisions(*SwigContext.getDecisions(*args))
    except TypeError:
        # xtr and url_getter can be provided by the customer, and thus might be objects the Oboe API can not handle
        if xtr is not None and not isinstance(xtr, str):
            # first argument provided to getDecisions must be the x-trace (or nothing)
            args[0] = None
            util_logger.debug("sample_request: ignoring invalid xtr object %s." % xtr)
        if len(args) == 2 and not isinstance(args[1], int):
            # second argument provided to getDecisions must be integer representation of custom tracing mode
            util_logger.debug("sample_request: ignoring invalid custom tracing_mode object %s." % args[1])
            _ = args.pop(1)
        res = SampleDecisions(*SwigContext.getDecisions(*args))

    util_logger.debug(
        "sample result: do_sample=%s, do_metrics=%s, sample_rate=%s, sample_source=%s, bucket_rate=%s, bucket_cap=%s, "
        "type=%s, auth=%s, status=%s, status_msg=%s, auth_msg=%s" % (
            res.do_sample,
            res.do_metrics,
            res.sample_rate,
            res.sample_source,
            res.bucket_rate,
            res.bucket_cap,
            res.typ,
            res.auth,
            res.status,
            res.status_msg,
            res.auth_msg))

    setattr(Context.transaction_dict, 'do_metrics', res.do_metrics)
    setattr(Context.transaction_dict, 'sample_rate', res.sample_rate)
    setattr(Context.transaction_dict, 'sample_source', res.sample_source)
    setattr(Context.transaction_dict, 'bucket_rate', res.bucket_rate)
    setattr(Context.transaction_dict, 'bucket_cap', res.bucket_cap)
    return bool(res.do_sample)


###############################################################################
# Backwards compatibility
###############################################################################

setattr(SwigEvent, 'addInfo', _Event_addInfo_safe(getattr(SwigEvent, 'addInfo')))


def _old_context_log(cls, layer, label, backtrace=False, **kwargs):
    if appoptics_apm.config['warn_deprecated']:
        util_logger.debug(
            'appoptics_apm.Context.log is deprecated. '
            'Please use appoptics_apm.log (and note signature change).')
    log(label, layer, store_backtrace=backtrace, keys=kwargs)


def _old_context_log_error(cls, exception=None, err_class=None, err_msg=None, backtrace=True):
    if appoptics_apm.config['warn_deprecated']:
        util_logger.debug(
            'appoptics_apm.Context.log_error is deprecated. '
            'Please use appoptics_apm.log_error (and note signature change).')
    if exception:
        err_class = exception.__class__.__name__
        err_msg = str(exception)
    store_backtrace = False
    tb = None
    if backtrace:
        _, _, tb = sys.exc_info()
        store_backtrace = True
    try:
        return log_error(err_class, err_msg, store_backtrace=store_backtrace, backtrace=tb)
    finally:
        del tb


def _old_context_log_exception(cls, msg=None, exc_info=None, backtrace=True):
    if appoptics_apm.config['warn_deprecated']:
        util_logger.debug(
            'appoptics_apm.Context.log_exception is deprecated. '
            'Please use appoptics_apm.log_exception (and note signature change).')
    typ, val, tb = exc_info or sys.exc_info()
    if msg is None:
        try:
            msg = str(val)
        except Exception:
            msg = repr(val)
    try:
        return log_error(typ.__name__, msg, store_backtrace=backtrace, backtrace=tb)
    finally:
        del tb


def _old_context_trace(cls, layer='Python', xtr_hdr=None, kvs=None):
    if appoptics_apm.config['warn_deprecated']:
        util_logger.debug(
            'appoptics_apm.Context.trace is deprecated. '
            'Please use appoptics_apm.trace (and note signature change).')
    return trace(layer, xtr_hdr=xtr_hdr, kvs=kvs)


def _old_context_profile_function(
        cls,
        profile_name,
        store_args=False,
        store_return=False,
        store_backtrace=False,
        profile=False,
        callback=None,
        **entry_kvs):
    if appoptics_apm.config['warn_deprecated']:
        util_logger.debug(
            'appoptics_apm.Context.trace is deprecated. '
            'Please use appoptics_apm.trace (and note signature change).')
    return profile_function(
        profile_name,
        store_args=False,
        store_return=False,
        store_backtrace=False,
        profile=False,
        callback=None,
        entry_kvs=entry_kvs)


def _old_context_log_method(
        cls, layer='Python', store_return=False, store_args=False, callback=None, profile=False, **entry_kvs):
    if appoptics_apm.config['warn_deprecated']:
        util_logger.debug(
            'appoptics_apm.Context.log_method is deprecated. '
            'Please use appoptics_apm.log_method (and note signature change).')
    return log_method(
        layer,
        store_return=store_return,
        store_args=store_args,
        callback=callback,
        profile=profile,
        entry_kvs=entry_kvs)


class _old_context_profile_block(profile_block):
    def __init__(self, *args, **kw):
        if appoptics_apm.config['warn_deprecated']:
            util_logger.debug(
                'appoptics_apm.Context.profile_block is deprecated. '
                'Please use appoptics_apm.profile_block (and note signature change).')
        super(_old_context_profile_block, self).__init__(*args, **kw)


def _old_context_to_string(cls):
    if appoptics_apm.config['warn_deprecated']:
        util_logger.debug(
            'appoptics_apm.Context.toString is deprecated. '
            'Please use str(appoptics_apm.Context.get_default())')
    return str(Context.get_default())


def _old_context_from_string(cls, md_string):
    if appoptics_apm.config['warn_deprecated']:
        util_logger.debug('appoptics_apm.Context.fromString is deprecated.')
    c = Context(md_string)
    c.set_as_default()


def _old_context_is_valid(cls):
    if appoptics_apm.config['warn_deprecated']:
        util_logger.debug(
            'appoptics_apm.Context.isValid is deprecated. '
            'Please use appoptics_apm.Context.get_default().is_valid()')
    return Context.get_default().is_valid()


setattr(Context, 'log', types.MethodType(_old_context_log, Context))
setattr(Context, 'log_error', types.MethodType(_old_context_log_error, Context))
setattr(Context, 'log_exception', types.MethodType(_old_context_log_exception, Context))
setattr(Context, 'log_method', types.MethodType(_old_context_log_method, Context))
setattr(Context, 'trace', types.MethodType(_old_context_trace, Context))
setattr(Context, 'profile_function', types.MethodType(_old_context_profile_function, Context))
setattr(Context, 'profile_block', _old_context_profile_block)
setattr(Context, 'toString', types.MethodType(_old_context_to_string, Context))
setattr(Context, 'fromString', types.MethodType(_old_context_from_string, Context))
setattr(Context, 'isValid', types.MethodType(_old_context_is_valid, Context))


def report_layer_init(layer='Python', keys=None):
    """ Send a status report with postStatus Thrift API showing the initialization and version of
    this layer's instrumentation.
    """
    if not ready():
        util_logger.debug('AppOptics APM is not ready, ignoring init message of layer {layer}.'.format(layer=layer))
        return

    ver_keys = dict()
    keys = keys or dict()

    ver_keys['__Init'] = 'True'
    try:
        ver_keys['Python.Version'] = "{major}.{minor}.{patch}".format(
            major=sys.version_info[0], minor=sys.version_info[1], patch=sys.version_info[2])
    except Exception as e:
        util_logger.warning("Could not retrieve Python version (%s)", e)
    ver_keys['Python.AppOptics.Version'] = __version__

    ver_keys['Python.AppOpticsExtension.Version'] = SwigConfig.getVersionString()

    # Just attempt to get the following info if we are in a regular file.
    # Else the path operations fail, for example when the agent is running
    # in an application zip archive.
    if os.path.isfile(__file__):
        ver_keys['Python.InstallDirectory'] = os.path.dirname(__file__)
        ver_keys['Python.InstallTimestamp'] = os.path.getmtime(__file__)  # in sec since epoch
    else:
        ver_keys['Python.InstallDirectory'] = "Unknown"
        ver_keys['Python.InstallTimestamp'] = 0
    ver_keys['Python.LastRestart'] = AGENT_START_TIME  # in usec

    # Don't add Hostname here as liboboe will do it for you.
    # ver_keys['Hostname'] = socket.gethostname()

    if layer.lower() == 'tornado':
        try:
            import tornado  # pylint: disable-msg=W0611
            ver_keys["Python.Tornado.Version"] = sys.modules['tornado'].version
        except ImportError as e:
            util_logger.warning('Failed to report init event for Tornado: {e}'.format(e=e))
            return

    if layer.lower() == 'django':
        try:
            import django
            ver_keys["Python.Django.Version"] = django.get_version()
        except ImportError as e:
            util_logger.warning('Failed to report init event for Django: {e}'.format(e=e))
            return

    ver_keys.update(keys)

    ctx = Context(Metadata.makeRandom(True))
    if not ctx.is_valid():
        return
    ctx.set_as_default()
    evt = ctx.create_event('single', layer)

    for k, v in ver_keys.items():
        evt.add_info(k, v)
    ctx.report_status(evt)


class oboe_ready_code:
    OBOE_SERVER_RESPONSE_UNKNOWN = (0, "Oboe server : unknown error")
    OBOE_SERVER_RESPONSE_OK = (1, "Oboe server : is ready")
    OBOE_SERVER_RESPONSE_TRY_LATER = (2, "Oboe server : not ready yet, try later")
    OBOE_SERVER_RESPONSE_LIMIT_EXCEEDED = (3, "Oboe server : limit exceeded")
    OBOE_SERVER_RESPONSE_INVALID_API_KEY = (4, "Oboe server : invalid API key")
    OBOE_SERVER_RESPONSE_CONNECT_ERROR = (5, "Oboe server : connection error")

    @classmethod
    def code_values(cls):
        code_pairs = [v for k, v in cls.__dict__.items() if not k.startswith("__")]
        return {p[0]: p[1] for p in code_pairs if isinstance(p, tuple)}


def appoptics_ready(wait_milliseconds=3000, integer_response=False):
    """
     Wait for AppOptics to be ready to send traces.

     This may be useful in short lived background processes when it is important to capture
     information during the whole time the process is running. Usually AppOptics doesn't block an
     application while it is starting up.

     :param wait_milliseconds:int default 3000, the maximum time to wait in milliseconds
     :param integer_response:int default false, return boolean value, otherwise return integer for
     detail information

     :return: return True for ready, False not ready, integer 1 for ready, others not ready

     :Example:

      if not appoptics_ready(10000):
         Logger.info("AppOptics not ready after 10 seconds, no metrics will be sent")
    """

    rc = SwigContext.isReady(wait_milliseconds)
    if not isinstance(rc, int) or not rc in oboe_ready_code.code_values():
        util_logger.warning("Unrecognized  return code:{rc}".format(rc=rc))
    elif rc != oboe_ready_code.OBOE_SERVER_RESPONSE_OK[0]:
        util_logger.warning(oboe_ready_code.code_values()[rc])

    return rc if integer_response else rc == oboe_ready_code.OBOE_SERVER_RESPONSE_OK[0]
