import importlib
import inspect
import json
import logging
import os
import sys

from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.handlers.exceptions import get_exception_context
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import execution_context
from stackifyapm.utils.compat import iteritems
from stackifyapm.utils.helper import is_async_span


logger = logging.getLogger("stackifyapm.instrument")


def _get_only_python_files(all_files, client=None):
    excludes = client and client.config and client.config.instrument_all_exclude.split(',') or []
    # filter only python files and remove common file name for servers
    return [
        file for file in all_files
        if '.py' in file[-3:] and
        'wsgi' not in file and
        'test' not in file and
        'setup.py' not in file and
        'manage.py' not in file and
        file.split(os.sep)[-1].split('.')[0] not in excludes
    ]


def _get_list_of_files(project_dir):
    # get all list of files in the directory and subdirectory
    # and exclude stackify and virtual environment directories
    list_of_files = [
        file for file in os.listdir(project_dir)
        if 'stackifyapm' not in file and
        'stackify' not in file and
        'venv' not in file and
        'env' not in file
    ]
    all_files = []

    for entry in list_of_files:
        full_path = os.path.join(project_dir, entry)
        if os.path.isdir(full_path):
            all_files = all_files + _get_list_of_files(full_path)
        else:
            all_files.append(full_path)

    return all_files


def _get_all_functions_to_instrument(client):
    # return list of modules and functions to instruments
    instrument_list = []
    base_dir = client.config.base_dir
    module_files = _get_only_python_files(_get_list_of_files(base_dir), client=client)

    for module_file in module_files:
        path = module_file.replace(base_dir, "").lstrip(os.sep).split(os.sep)
        module_name = path[-1].split('.')[0]
        module_path = module_name.startswith('__') and '.'.join(path[:-1]) or '.'.join(path[:-1] + [module_name])
        try:
            if not sys.modules.get(module_path):
                importlib.import_module(module_path)

            for class_name, handler_class in inspect.getmembers(sys.modules.get(module_path), inspect.isclass):
                # we should not include dependency classes
                if not str(handler_class.__module__) == str(module_path):
                    continue

                funcs = inspect.getmembers(handler_class, inspect.isfunction) + inspect.getmembers(handler_class, inspect.ismethod)
                for method in funcs:
                    instrument_list.append((module_path, ".".join([class_name, method[0]])))

        except Exception as e:
            logger.warning('Unable to parse module name: {}, path: {}. Error: {}'.format(module_name, module_path, e))

    return instrument_list


def _clean_up_duplicates(instrument_list):
    return list(set(instrument_list))


class CustomInstrumentation(AbstractInstrumentedModule):
    """
    Custom instrumentation support
    to be able to let user do custom instrumentation without code changes,
    we provide this custom instrumenation module to instrument
    specific class method provider by the user in their config file
    """
    name = "custom_instrumentation"
    instrumentations = []
    instrument_list = []

    def get_instrument_list(self):
        instrument_list = []
        config_file = self.client and self.client.get_application_info().get('config_file')

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file) as json_file:
                    data = json.load(json_file)
                    self.instrumentations = data.get('instrumentation', [])

                    for instrumentation in self.instrumentations:
                        class_name = instrumentation.get('class')
                        method_name = instrumentation.get('method')
                        method = class_name and "{}.{}".format(class_name, method_name) or method_name
                        instrument_list.append((instrumentation.get('module'), method))

            except Exception:
                logger.warning('Unable to read stackify json file.')

        if self.client and self.client.config.instrument_all:
            instrument_list += _get_all_functions_to_instrument(self.client)

        self.instrument_list = _clean_up_duplicates(instrument_list)
        return self.instrument_list

    def _call(self, custom_type, wrapped, args, kwargs):
        self.client.begin_transaction('custom', client=self.client)
        try:
            call = wrapped(*args, **kwargs)
        except Exception:
            exc_info = sys.exc_info()
            self.client.capture_exception(
                exception=get_exception_context(exc_info[1], exc_info[2])
            )
            self.client.end_transaction(name=custom_type)
            raise

        self.client.end_transaction(name=custom_type)
        return call

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        class_name, method_name = method.split('.')
        instrumentations = [i for i in self.instrumentations if i.get('class') == class_name and i.get('method') == method_name]
        custom_type = 'custom.{}.{}'.format(class_name, method_name)

        if instrumentations:
            instrumentation = instrumentations[0]

            if instrumentation.get('transaction') and self.client and not execution_context.get_transaction():
                return self._call(custom_type, wrapped, args, kwargs)
            else:
                context = {
                    "CATEGORY": "Python",
                }
                for k, v in iteritems(instrumentation.get('extra', {})):
                    context[k.upper()] = v

                if instrumentation.get('trackedFunction'):
                    context['TRACKED_FUNC'] = instrumentation.get('trackedFunctionName', '{ClassName}.{MethodName}').format(
                        ClassName=class_name,
                        MethodName=method_name,
                    )

                with CaptureSpan(custom_type, context, leaf=False, is_async=is_async_span()):
                    return wrapped(*args, **kwargs)

        elif self.client and self.client.config.instrument_all:
            if self.client and not execution_context.get_transaction():
                return self._call(custom_type, wrapped, args, kwargs)
            else:
                context = {
                    "CATEGORY": "Python",
                    "TRACKED_FUNC": '{ClassName}.{MethodName}'.format(
                        ClassName=class_name,
                        MethodName=method_name,
                    ),
                }

                with CaptureSpan(custom_type, context, leaf=False, is_async=is_async_span()):
                    return wrapped(*args, **kwargs)

        return wrapped(*args, **kwargs)
