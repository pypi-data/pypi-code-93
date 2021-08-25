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
""" AppOptics APM instrumentation for logging module.
"""
import inspect
import logging

from decorator import decorator

import appoptics_apm

ao_logger = logging.getLogger(__name__)

_INJECTION_STRING = 'ao.traceId={}'


def convert_xtr_to_trace_id(xtr):
    """Returns the traceId (for log injection) of the provided X-Trace"""
    trace_id = '0000000000000000000000000000000000000000-0'
    if len(xtr) == 60 and xtr[0:2] == '2B':
        task_id = xtr[2:42]
        sampled = xtr[-1]
        trace_id = task_id + '-' + sampled
    return trace_id


def wrap_getMessage(func, trace_id):
    def get_message(*f_args, **f_kwargs):
        res = func(*f_args, **f_kwargs)
        try:
            calling_class = type(inspect.currentframe().f_back.f_locals['self'])
            if calling_class is logging.Formatter:
                res = '{} {}'.format(_INJECTION_STRING.format(trace_id), res)
        except Exception:
            pass

        return res

    return get_message


class LogInjectionFilter:
    """ Filter object to insert traceId into logs. This filter may only be added to a logger object if the traceId
        injection into logs feature is not disabled."""
    def __init__(self, log_trace_id):
        self.log_trace_id = log_trace_id

    def filter(self, record):
        """Injects 'ao': {'traceId': <traceId>'} into the provided LogRecord."""
        if record.msg != '':
            if self.log_trace_id == 'always':
                record.ao = {'traceId': convert_xtr_to_trace_id(appoptics_apm.util.last_id())}
                record.getMessage = wrap_getMessage(record.getMessage, record.ao['traceId'])
            else:
                ctx = appoptics_apm.util.Context.get_default()
                if ctx is not None and ctx.is_valid():
                    if self.log_trace_id != 'sampled' or ctx.is_sampled():
                        record.ao = {'traceId': convert_xtr_to_trace_id(str(ctx))}
                        record.getMessage = wrap_getMessage(record.getMessage, record.ao['traceId'])
        return True


class LogInjector:
    def __init__(self):
        self.log_trace_id = 'never'
        self.wrapped = False
        self.injection_filter = LogInjectionFilter(self.log_trace_id)

    def set_wrapped(self):
        if not self.wrapped:
            self.wrapped = True
            if self.is_injecting():
                # injection filters need to be added manually the first time after wrapping
                self.update_filters()

    def is_injecting(self):
        return self.wrapped and (self.log_trace_id != 'never')

    def set_injection_mode(self, log_trace_id):
        """ Updates log injection mode """
        if self.log_trace_id != log_trace_id:
            self.log_trace_id = log_trace_id
            if self.wrapped:
                self.update_filters()

    def update_filters(self):
        logging._acquireLock()
        try:
            self.injection_filter.log_trace_id = self.log_trace_id
            loggers = [logging.root] + list(logging.Logger.manager.loggerDict.values())
            f_name = 'removeFilter' if self.log_trace_id == 'never' else 'addFilter'
            for logger in loggers:
                if isinstance(logger, logging.PlaceHolder):
                    # placeholders are not actual logger instances and can not have attached any filters
                    continue
                fn = getattr(logger, f_name, None)
                if callable(fn):
                    fn(self.injection_filter)
                    ao_logger.debug('update_filters: logger {}, {}(LogInjectionFilter).'.format(logger, f_name))
                else:
                    ao_logger.warning('update_filters: could not call {} on logger {}.'.format(f_name, logger))
        except Exception as e:
            ao_logger.error("AppOptics APM error: %s" % str(e))
        finally:
            logging._releaseLock()

    def get_log_trace_id(self):
        return convert_xtr_to_trace_id(appoptics_apm.util.last_id())


log_injector = LogInjector()


def wrap_logger_init(func, self, *f_args, **f_kwargs):
    func(self, *f_args, **f_kwargs)
    try:
        if log_injector.is_injecting():
            self.addFilter(log_injector.injection_filter)
            ao_logger.debug('wrap_logger_init adding LogInjectionFilter to logger {}.'.format(self))
    except Exception as e:
        ao_logger.error(
            "AppOptics APM error: wrap_logger_init could not add LogInjectionFilter and received following error: {}".
            format(e))


def wrap_logging_module():
    if appoptics_apm.util.ready() and not log_injector.wrapped:
        try:
            logger = logging.Logger
            fn = getattr(logger, '__init__', None)
            if hasattr(fn, '__func__'):  # Is this a bound method of an object
                fn = fn.__func__  # then wrap the unbound method
            setattr(logger, '__init__', decorator(wrap_logger_init, fn))
            ao_logger.debug('wrap_logging_module wraps {} of {} object'.format(fn.__name__, logger.__name__))
            log_injector.set_injection_mode(appoptics_apm.config['log_trace_id'])
            log_injector.set_wrapped()
        except Exception as e:
            ao_logger.error("AppOptics APM error: %s" % str(e))


def get_log_trace_id():
    """Returns a string of the trace id to inject trace context into logging messages."""
    return log_injector.get_log_trace_id()
