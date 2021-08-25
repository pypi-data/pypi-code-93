"""
Generic handler functionality for Phantom App connector implementations.

To implement a basic connector that supports a hypothetical `echo message`
action and provides a result summary:
```
class MyConnector(SmartConnector, main=True):
    @ActionHandler
    def echo_message(self, message, context=None):
        self.logger.info('message: %r', message)
        yield message

    @echo_message.summary
    def get_summary(self, results):
        message, = results
        return {'message': message}
```
"""
import asyncio
from inspect import isasyncgen
import json
import logging
from abc import ABCMeta
from contextlib import contextmanager
from functools import lru_cache, partial, update_wrapper, wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)
import warnings

import phantom.vault
from phantom.action_result import ActionResult
from phantom.app import APP_ERROR, APP_SUCCESS
from phantom.base_connector import BaseConnector

from .models import Artifact, Container, RemoteError, contains, contains_map


logger = logging.getLogger(__name__)


class ActionHandler:
    """
    A descriptor for a method designated as an action handler for a connector
    class.
    When used as a decorator, it provides a straightforward way to register
    the decorated method as an action handler.

    This class wraps the provided method with standard error handling, and
    manages the conversion of generic method results to Phantom ActionResults.

    :param function method: The method that implements the connector's action
        handler logic for the action of the same name
    """
    DEFAULT_LOCK = object()

    registered_handlers = {}

    def __init__(
            self,
            method=None,
            *,
            data_contains=None,
            action_type=None,
            read_only=False,
            lock=DEFAULT_LOCK,
            lock_timeout=None,
    ):
        self.unbound_method = None
        self.handler_method = None
        self.summary_method_name = None
        self.data_contains_map = data_contains
        self.summary_contains_map = None
        self.action_type = action_type
        self.read_only = read_only
        self.custom_view_metadata = None
        self.custom_view_function = None
        self.lock = lock
        self.lock_timeout = lock_timeout
        if method is not None:
            self.decorate_method(method=method)

    def __call__(self, method):
        return self.decorate_method(method=method)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        bound_method = partial(self.unbound_method, instance)
        update_wrapper(bound_method, self.unbound_method)
        return bound_method

    @property
    def action_identifier(self):
        return self.unbound_method.__name__

    def decorate_method(self, method):
        self.unbound_method = method
        self.handler_method = self.create_handler_method()
        handler_set = self.registered_handlers.setdefault(
            self.action_identifier, set())

        handler_set.add(self)
        return self

    def create_handler_method(self):
        """
        Wrap the action handler logic in standard Phantom ActionResult results
        and error-handling

        :return: A new unbound method that wraps the original in Phantom
            reporting and error handling
        :rtype: function
        """
        action_identifier = self.action_identifier

        @wraps(self.unbound_method)
        def handler_method(connector: SmartConnector, param: Mapping):
            connector.logger.info('Handling %r', action_identifier)
            context = param.pop('context', None)
            with connector._result_context(
                    param=param, context=context) as action_result:
                data_source = self.unbound_method(connector, **param)
                try:
                    data_iterable = iter(data_source)
                except TypeError:
                    connector.logger.debug('Data not iterable; assuming async')
                    self.consume_async_data(
                        connector, action_result, data_source)
                else:
                    for data in data_iterable:
                        connector.logger.debug(
                            'Adding %r result data', action_identifier)
                        action_result.add_data(data)

                if self.summary_method_name is None:
                    connector.logger.debug(
                        'No summary method for %r handler', action_identifier)
                else:
                    summary_method = getattr(
                        connector, self.summary_method_name)
                    results = action_result.get_data()
                    connector.logger.debug(
                        'Creating summary for %r', action_identifier)
                    summary = summary_method(results)
                    action_result.set_summary(summary)

                connector.logger.info(
                    'Finished handling %r', action_identifier)

            return action_result

        return handler_method

    def summary(self, unbound_method):
        """
        A decorator for a connector method that will produce a summary from
        the result of a call to a handler

        :param function unbound_method: The summary method
        :return: The summary method
        :rtype: function
        """
        self.summary_method_name = unbound_method.__name__
        return unbound_method

    def summary_contains(self, summary_contains_map):
        self.summary_contains_map = summary_contains_map
        return self.summary

    async def consume_async_generator(
            self, connector, action_result, generator):
        connector.logger.debug('Consuming from async generator %r', generator)
        data_queue = asyncio.Queue()
        async def enqueue_data():
            connector.logger.debug('Enqueuing data using %r', generator)
            async for data in generator:
                connector.logger.debug('Putting data %r', data)
                await data_queue.put(data)

        loop = asyncio.get_event_loop()
        task = loop.create_task(enqueue_data())
        connector.logger.debug('Created enqueue task %r', task)
        while (not task.done()) or (not data_queue.empty()):
            connector.logger.debug('Awaiting queue data')
            data = await data_queue.get()
            connector.logger.debug('Adding async result data')
            action_result.add_data(data)
            data_queue.task_done()

        task.result()

    async def consume_coroutine(self, connector, action_result, coroutine):
        connector.logger.debug('Consuming from coroutine %r', coroutine)
        result = await coroutine
        connector.logger.debug('Adding result data: %r', result)
        action_result.update_data(result)
        return result

    def consume_async_data(self, connector, action_result, data_source):
        if isasyncgen(data_source):
            coroutine = self.consume_async_generator(
                connector, action_result, data_source)
        else:
            coroutine = self.consume_coroutine(
                connector, action_result, data_source)

        connector.logger.debug('Creating event loop')
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(coroutine)
        finally:
            connector.logger.debug('Closing event loop')
            loop.close()

    def custom_view(
            self,
            title: str = None,
            width: int = 10,
            height: int = 5,
    ):
        """
        A parameterised decorator for registering a custom view function for
        this action handler.

        The `title`, `width`, and `height` parameters will be used to populate
        the `render` metadata for this action.
        """
        if title is None:
            method_name = self.unbound_method.__name__
            title = ' '.join(method_name.split('_')).title()

        self.custom_view_metadata = {
            'type': 'custom', 'title': title, 'width': width, 'height': height}

        def decorator(
                view_function: Callable[
                    [str, List[Tuple[dict, List[ActionResult]]], dict],
                    Optional[str],
                ],
        ):
            @wraps(view_function)
            def wrapper(provides, all_app_runs, context):
                logger.warning('Running view function %r', view_function)
                result = view_function(provides, all_app_runs, context)
                logger.warning('Got result %r', result)
                if result is None:
                    return_path = Path(
                        'views', f'{view_function.__name__}.html')
                else:
                    return_path = result
                logger.warning('Return path: %r', return_path)
                return str(return_path)

            self.custom_view_function = view_function
            return wrapper

        return decorator


    ### Deprecated ###

    @classmethod
    def data_contains(cls, data_contains_map):
        warnings.warn(
            f'Use {cls} constructor parameters instead of {cls}.data_contains')
        return cls(data_contains=data_contains_map)


class _ConnectorClass(ABCMeta):
    """
    A metaclass that will dynamically determine whether instance classes
    inherit from `phantom.base_connector.BaseConnector` based on the value of
    keyword argument `main` (default `True`).

    This behaviour allows us to trick IDEs into resolving mocked Phantom module
    interface definitions without actually subclassing from
    `phantom.base_connector.BaseConnector`, which will break the app unless
    the subclass is the intended connector implementation class.
    """
    def __new__(cls, name, bases, class_dict, *, main=True, **kwargs):
        if main:
            if BaseConnector in bases:
                new_bases = bases
            else:
                new_bases = *bases, BaseConnector
        else:
            new_bases = tuple(b for b in bases if b is not BaseConnector)

        result = super().__new__(cls, name, new_bases, class_dict, **kwargs)
        if main:
            result = _main_connector(result)

        return result


class SmartConnector(BaseConnector, metaclass=_ConnectorClass, main=False):
    """
    A base class for a Phantom App connector implementation that will use the
    truth value of the class keyword argument `main` to decide whether it
    inherits from `phantom.base_connector.BaseConnector`.
    The default is `main=True`, which will cause the subclass to inherit from
    `phantom.base_connector.BaseConnector`.

    This behaviour is implemented because Phantom blindly chooses the
    first subclass of `phantom.base_connector.BaseConnector` as the concrete
    implementation, whether this was the intended implementation or a helper
    class.
    This drastically intereferes with app development, as helper superclasses
    (such as `SmartConnector` itself) are unable to inherit from
    `phantom.base_connector.BaseConnector`, precluding interface stubbing or
    straightforward implementation inheritance.

    To define a class that is notionally intended to subclass from
    `phantom.base_connector.BaseConnector` but is not a concrete
    implementation, define a subclass of `SmartConnector` with the class
    argument `main=False`:
    ```python
    class Helper(SmartConnector, main=False):
        ...
    ```

    To define the intended connector implementation, set `main=True`:
    ```python
    class Connector(SmartConnector, main=True):
        ...
    ```
    """
    def __init__(self, *args, **kwargs):
        self.context = None
        self._state_context = None
        self.logger = logging.getLogger(self.__module__)
        # Setting the logging level to DEBUG will ensure all logging calls
        # are properly delegated to the appropriate
        # debug_print/error_print/save_progress calls.
        # The Phantom platform will still drop debug_print calls if the system
        # log level is not DEBUG.
        # In this case, the effective minimum log level is ERROR, but
        # save_progress calls will still be made for INFO.
        self.logger.setLevel(level=logging.DEBUG)
        log_handler = _ConnectorLogHandler(connector=self)
        self.logger.addHandler(log_handler)
        super().__init__(*args, **kwargs)

    def handle_action(self, param: dict) -> ActionResult:
        """
        Use `ActionHandler` decorated methods instead of overriding this.

        Implements abstract method
        `phantom.base_connector.BaseConnector.handle_action`.

        Delegates execution to the appropriate action handler logic.

        :param dict param: Parameter dictionary passed in by Phantom
        :return: The Phantom action result
        :rtype: phantom.action_result.ActionResult
        """
        action_identifier = self.get_action_identifier()
        action_handler = self._get_handler(action_identifier)
        unbound_method = action_handler.handler_method
        with self._persistent_state():
            result: ActionResult = unbound_method(self, param)

        self.logger.debug('Returning with result: %r', result.get_dict())
        return result

    @property
    def state(self) -> dict:
        """
        Access the persistent state dictionary.

        The first reference to this property will load the state from the
        filesystem.
        If no state file exists, an empty dictionary will be created.

        Once loaded, the final contents of the state dict will be automatically
        saved back to the filesystem at the end of each action handler
        execution, creating a new state file if necessary.
        """
        return self._state_context.data

    @property
    @lru_cache(maxsize=1)
    def config(self) -> dict:
        """
        Access the app config dictionary.

        The first reference to this property will load the config data using
        `self.get_config()`.
        Following references will use the cached result, incurring no
        performance penalty over using `get_config` directly.
        """
        return self.get_config()

    @property
    @lru_cache(maxsize=1)
    def phantom_home(self) -> Path:
        """
        Retrieve the path to the Phantom home directory.
        """
        state_dir = Path(self.get_state_dir())
        # Expecting <PHANTOM_HOME>/local_data/app_states/<APP_ID>/
        *home_components, _, _, _ = state_dir.parts
        return Path(*home_components).resolve().absolute()

    @property
    @lru_cache(maxsize=1)
    def phantom_log_directory(self) -> Path:
        """
        Retrieve the path to the Phantom logging directory.

        Automatically determines the correct location, which depends on
        whether Phantom was installed with root privileges and the Phantom home
        location.
        """
        components = ['var', 'log', 'phantom']
        privileged_logs = Path('/').joinpath(*components)
        if privileged_logs.exists():
            return privileged_logs

        unprivileged_logs = self.phantom_home.joinpath(*components)
        if unprivileged_logs.exists():
            return unprivileged_logs

        raise FileNotFoundError('Unable to find log directory')

    @property
    @lru_cache(maxsize=1)
    def app_log_directory(self) -> Path:
        """
        Retrieve the app connector logging directory.

        Logging to this directory is a feature that is specific to apps
        implemented with this module.
        """
        # The app doesn't have permission to write to the syslog apps directory
        # Use the app's state directory as a janky hack
        return self.get_state_path('logs')

    def get_state_path(self, path: Union[Path, str] = None) -> Path:
        """
        Retrieve the state file path.

        If called without a `path` argument, returns the path to the file that
        stores the app state dictionary.
        If a `path` argument is specified, returns the path given by resolving
        the value as a relative path to the app state directory.
        """
        state_dir = Path(self.get_state_dir())
        if path is None:
            file_path = Path(self.get_state_file_path())
        else:
            file_path = state_dir.joinpath(path)

        resolved_path = file_path.resolve()
        # Raise ValueError if not subpath of state_dir
        resolved_path.relative_to(state_dir)
        return resolved_path

    def get_vault_path(self, vault_id: str) -> Path:
        """
        Retrieve the vault path for the specified vault ID.

        This method will automatically choose the correct interface to the API,
        which introduced breaking changes to the Vault API in Phantom version
        4.10.
        """
        try:
            vault_info_function = phantom.vault.vault_info
        except AttributeError:
            self.logger.debug('Using Phantom 4.8 vault interface')
            path_string = phantom.vault.Vault.get_file_path(vault_id)
        else:
            self.logger.debug('Using Phantom 4.10 vault interface')
            success, message, info = vault_info_function(vault_id=vault_id)
            if not success:
                raise RuntimeError(message)

            # All file entries for a vault ID will have the same file path
            path_string = info[0]['path']

        return Path(path_string).resolve()

    def save_all_containers(
            self, containers: Iterable[MutableMapping]) -> List[dict]:
        """
        Create or update multiple containers at once on the Phantom platform.

        Like `save_containers`, this is the most performant API to use during
        ingestion as you can create all the artifacts and containers at once.

        Unlike `save_containers`, this method will raise a `RemoteError` if any
        of the containers fail to update successfully.
        If a `RemoteError` is raised, its `responses` member can be checked
        for the individual results for each container.
        """
        containers = list(containers)
        status, message, responses = self.save_containers(
            [dict(c) for c in containers])

        if status != APP_SUCCESS:
            raise RemoteError(message, responses=responses)

        self.logger.info(message)
        self.logger.info(
            'Saved new containers with responses %s', responses)

        errors = []
        for container, response in zip(containers, responses):
            if response['success'] != APP_SUCCESS:
                errors.append(response)
                continue

            new_id = response['id']
            try:
                existing_id = container['id']
            except KeyError:
                container['id'] = new_id
            else:
                if existing_id != new_id:
                    raise ValueError(
                        'Conflicting container ID in response for existing ID'
                        f' {existing_id}; responses: {responses}'
                    )

        if errors:
            raise RemoteError(message, responses=responses)

        return responses

    @classmethod
    def get_handlers(cls) -> Iterable[ActionHandler]:
        """
        Get all action handler instances for this object
        """
        for action_identifier in ActionHandler.registered_handlers:
            try:
                yield cls._get_handler(action_identifier)
            except AttributeError as error:
                logger.debug(error, exc_info=error)
                continue

    @classmethod
    def main(cls) -> Any:  # pragma: no cover
        """
        A copy of the logic provided by the app-creation wizard tweaked to
        support remote debugging with `debugpy`.
        """
        import argparse
        import requests

        try:
            from pudb import set_trace as breakpoint
        except ImportError:
            from pdb import set_trace as breakpoint

        try:
            import debugpy
        except ImportError:
            pass
        else:
            if debugpy.is_client_connected():
                breakpoint = debugpy.breakpoint

        breakpoint()

        argparser = argparse.ArgumentParser()

        argparser.add_argument('input_test_json', help='Input Test JSON file')
        argparser.add_argument(
            '-u', '--username', help='username', required=False)
        argparser.add_argument(
            '-p', '--password', help='password', required=False)

        args = argparser.parse_args()
        session_id = None

        username = args.username
        password = args.password

        if username is not None and password is None:

            # User specified a username but not a password, so ask
            import getpass
            password = getpass.getpass("Password: ")

        if username and password:
            try:
                phantom_base_url = cls._get_phantom_base_url()
                login_url = f'{phantom_base_url}/login'

                print("Accessing the Login page")
                r = requests.get(login_url, verify=False)
                csrftoken = r.cookies['csrftoken']

                data = dict()
                data['username'] = username
                data['password'] = password
                data['csrfmiddlewaretoken'] = csrftoken

                headers = dict()
                headers['Cookie'] = 'csrftoken=' + csrftoken
                headers['Referer'] = login_url

                print("Logging into Platform to get the session id")
                r2 = requests.post(
                    login_url, verify=False, data=data, headers=headers)
                session_id = r2.cookies['sessionid']
            except Exception as e:
                print(
                    f"Unable to get session id from the platform. Error: {e}")
                exit(1)

        with open(args.input_test_json) as f:
            in_json = f.read()
            in_json = json.loads(in_json)
            print(json.dumps(in_json, indent=4))

            connector = cls()
            connector.print_progress_message = True

            if session_id is not None:
                in_json['user_session_token'] = session_id
                connector._set_csrf_info(csrftoken, headers['Referer'])

            ret_val = connector._handle_action(json.dumps(in_json), None)
            print(json.dumps(json.loads(ret_val), indent=4))

        exit(0)

    ### Implementation helpers ###

    @contextmanager
    def _persistent_state(self):
        """
        Automatically save the state data if it was loaded while running under
        this context.
        """
        if self._state_context is not None:
            raise RuntimeError(f'{self!r} already has a state context')

        try:
            with _StateContext(path=self.get_state_path()) as state_context:
                self._state_context = state_context
                yield state_context
        finally:
            self._state_context = None

    @contextmanager
    def _result_context(self, param: Mapping, context: Union[dict, None]):
        """
        Set the connnector context data, create an ActionResult, and set its
        status depending on whether an exception is raised while running under
        this context.
        """
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)
        old_context = self.context
        self.context = context
        try:
            yield action_result
        except Exception as error:
            # Phantom appears to expect errors to be handled by the connector.
            # Report and log the error, but suppress it from propagating.
            self.logger.exception(error)
            action_result.set_status(APP_ERROR, '', error)
        else:
            action_result.set_status(APP_SUCCESS)
        finally:
            self.context = old_context

    @classmethod
    def _get_handler(cls, action_identifier: str) -> ActionHandler:
        """
        Get the action handler for the provided action identifier

        The connector class is expected to have an `ActionHandler` member that
        is named after the action identifier.

        :param str action_identifier: The identifer of a handled action
        :return: The action handler for the identified action
        :rtype: function
        """
        target = getattr(cls, action_identifier)
        handler_set = ActionHandler.registered_handlers[action_identifier]
        if target in handler_set:
            return target

        raise AttributeError(
            f'{cls!r} has no handler for action identifier'
            f' {action_identifier}'
        )

    ### Deprecated ###

    def open_vault_file(self, vault_id, mode='r'):
        """
        Deprecated; use `get_vault_path` instead.
        """
        self.logger.warning(
            '`open_vault_file` will be deprecated;'
            ' Use the `get_vault_path` and open the Path object directly'
        )
        file_path = self.get_vault_path(vault_id=vault_id)
        self.logger.debug(
            'Opening file path for vault ID %r: %r', vault_id, file_path)

        return file_path.open(mode)

    def open_state(self, path=None, *args, **kwargs):
        """
        Deprecated; use `get_state_path` instead.
        """
        self.logger.warning(
            '`open_state` will be deprecated;'
            ' Use the `get_state_path` and open the Path object directly'
        )
        return self.get_state_path(path=path).open(*args, **kwargs)

    def get_phantom_home(self) -> Path:
        """
        Deprecated; use `self.phantom_home` instead.

        Retrieve the path to the Phantom home directory.
        """
        self.logger.warning(
            '`get_phantom_home` will be deprecated;'
            ' Use the `self.phantom_home`'
        )
        return self.phantom_home

    def get_phantom_logs_path(self) -> Path:
        """
        Deprecated; use `self.phantom_log_directory` instead.

        Retrieve the path to the Phantom logging directory.

        Automatically determines the correct location, which depends on
        whether Phantom was installed with root privileges and the Phantom home
        location.
        """
        return self.phantom_log_directory

    def get_logs_path(self) -> Path:
        """
        Deprecated; use `self.app_log_directory` instead.

        Retrieve the app connector logging directory.

        Logging to this directory is a feature that is specific to apps
        implemented with this module.
        """
        return self.app_log_directory


registered_connectors = {}


### Implementation helpers ###


def _main_connector(connector_class: SmartConnector):
    """
    This decorator automatically executes the decorated class's `main` method
    if the class is defined in the `__main__` module

    :param type connector_class: A Phantom app connector implementation
    """
    module = connector_class.__module__
    logger.debug(
        'Registering connector_class %r from module %r',
        connector_class,
        module,
    )
    registered_connectors.setdefault(module, set()).add(connector_class)
    logger.debug(
        'Registered connector %r from file %r', connector_class, __file__)

    if module != '__main__':
        return connector_class

    connector_class.main()
    return connector_class


class _ConnectorLogHandler(logging.Handler):
    """
    Delegates logging calls to app interface functions, and provides filthy
    hacks to write to a logging file
    """
    FIELDS = [
        '{levelname}',
        '{name}',
        '{message}',
    ]

    FIELD_SEPARATOR = ' : '

    FORMAT_STRING = f' {FIELD_SEPARATOR.join(FIELDS)}'

    FORMATTER = logging.Formatter(FORMAT_STRING, style='{')

    FILE_FORMATTER = logging.Formatter(
        f'[%(asctime)s] {logging.BASIC_FORMAT}', style='%')

    def __init__(self, connector, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connector = connector
        self.setFormatter(self.FORMATTER)
        self._file_handler = None

    @property
    def file_handler(self):
        # This needs to be instantiated after after the connector;
        # Assuming any logging calls will occur after the state directory
        # is ready to use.
        if self._file_handler is not None:
            return self._file_handler

        logs_directory = self.connector.get_logs_path()
        logs_directory.mkdir(exist_ok=True)
        connector_log = logs_directory.joinpath('connector.log')
        self._file_handler = RotatingFileHandler(
            filename=connector_log, maxBytes=1024*1024, backupCount=5)
        self._file_handler.setFormatter(self.FILE_FORMATTER)
        return self._file_handler

    def emit(self, record: logging.LogRecord):
        message = self.format(record)
        if record.levelno >= logging.ERROR:
            self.connector.error_print(message)
        else:
            self.connector.debug_print(message)

        if record.levelno >= logging.INFO:
            self.connector.save_progress(record.message)

        self.file_handler.emit(record=record)


class _StateContext:
    """
    Manage the dynamic loading and storage of state from/to the filesystem
    """
    def __init__(self, path: Path):
        self.state_path = path
        self._data = None

    @property
    def data(self):
        if self._data is None:
            try:
                with self.state_path.open() as state_file:
                    self._data = json.load(state_file)

            except FileNotFoundError:
                self._data = {}

        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        if self._data is not None:
            with self.state_path.open(mode='w') as state_file:
                json.dump(self._data, state_file)


### Deprecated ###


class HandlerMixin(SmartConnector, main=False):
    """
	Deprecated; inherit from `SmartConnector` instead.
	"""


def smart_connector(connector_class):
    """
    Deprecated; inherit from SmartConnector instead.

    This decorator automatically subclasses the decorated class from
    each of `SmartConnector` and `phantom.base_connector.BaseConnector` if it
    is not already a subclass.
    It also calls the `_main_connector` decorator on the class to automatically
    execute the `main` method if the class is defined in the `__main__` module.

    Note: The `SmartConnector` superclass is specified by default to facilitate
    IDE functionality, but is not necessary when using this decorator.

    :param type connector_class: A Phantom app connector implementation
    """
    warnings.warn(
        'smart_connector is deprecated; inherit from SmartConnector instead')
    new_superclasses = []
    for superclass in [SmartConnector, BaseConnector]:
        if not issubclass(connector_class, superclass):
            new_superclasses.append(superclass)

    if not new_superclasses:
        return _main_connector(connector_class)

    @wraps(connector_class.__init__)
    def init(connector, *args, **kwargs):
        SmartConnector.__init__(connector, *args, **kwargs)
        connector_class.__init__(connector, *args, **kwargs)

    metaclass = type(SmartConnector)
    new_class = metaclass(
        connector_class.__name__,
        (connector_class, *new_superclasses),
        {'__init__': init, '__original_class': connector_class},
        main=True,
    )

    new_class.__doc__ = connector_class.__doc__
    new_class.__module__ = connector_class.__module__
    return _main_connector(new_class)


def main_connector(connector_class: SmartConnector):
    """
    Deprecated; inherit from `SmartConnector` with `main=True` instead.
    """
    warnings.warn(
        '`main_connector` is deprecated;'
        ' inherit from `SmartConnector` with `main=True` instead'
    )
    return _main_connector(connector_class)
