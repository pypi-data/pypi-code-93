"""
A basic Phantom App connector implementation.

Customise the Connector class using `ActionHandler` methods, or define your
own implementation.
"""
import asyncio
from enum import Enum
from uuid import uuid4

from phantom_dev.action_handler import (
    ActionHandler, Artifact, Container, SmartConnector, contains)


@contains('text')
class Text(str):
    """A string-based type that contains ['text']"""


@contains('fake count')
class Count(int):
    """A numeric-based type that contains ['fake count']"""


@contains('fake units')
class Amount(float):
    """A numeric-based type that contains ['fake units']"""


@contains('fake choice')
class Choice(Enum):
    """"""
    EENY = 'eeny'
    MEENY = 'meeny'
    MINEY = 'miney'
    MO = 'mo'


class Connector(SmartConnector, main=True):
    """
    Use a subclass of SmartConnector as a simple way to implement a Phantom App
    connector.

    Decorate member functions with `@ActionHandler` to register them as action
    handler methods.
    Handler methods should accept whichever parameters the action requires to
    run as keyword arguments.
    The connector's `context` member can be used to access the hidden context
    parameter passed to `phantom.act` during action execution.

    Parameter annotations can be used to infer the parameter type if they are
    subclasses of Python primitives (`int`, `float`, `str`, or `bool`).
    Handler docstrings can similarly be used to infer the description of each
    action.
    Sphinx-style docstring parameter descriptions can also be used to infer
    the description of each parameter if not specified in the metadata.
    Parameter annotation default values are reflected in the metadata, and are
    also used to infer whether a parameter is mandatory.

    To add `contains` information, decorate a class with the `contains`
    decorator with the `contains` values as positional arguments.
    Use this class for parameter annotations (it should inherit from a Python
    primitive type).

    `contains` information can also be added to output by using the
    `ActionHandler.data_contains` decorator instead of `ActionHandler`.
    Similarly, `<handler>.summary_contains` can be used instead of
    `<handler>.summary`.
    These decorators take a mapping of relative datapaths to parameter types;
    use `contains`-mapped classes in the same manner as described above for
    action parameters.
    For action result data, the datapath keys should be relative to
    `'action_result.data.*'`;
    for summary data, the datapath keys should be relative to
    `'action_result.summary'`

    Handler methods should return iterables of result data dictionaries.
    They can return iterables as functions, or be implemented as data
    dictionary generators.
    See the `test_connectivity` and `dummy_action` methods below for
    examples of each approach.

    Once an action handler method has been defined and decorated with
    `@ActionHandler`, the handler method has a member called `summary` that
    can be used to register another method as the action summary method.
    The action summary method should take an iterable of the results from the
    handler method and return an action result summary dict.
    See the `summarise` method for an example using the `dummy_action` handler
    method to register it as the summary method for `dummy_action`.

    A persistent state dictionary can be accessed by the `state` property.
    This can be used to replace calls to the various state path/file/dictionary
    methods on the base connector, and any access of the state data will cause
    the data to be written to the state file at the end of action handling.
    See `dummy_action` for an example of accessing and writing to persistent
    state.

    As a result of setting `main=True`, this class inherits from
    `phantom.base_connector.BaseConnector`, as well as implementing the testing
    interface when this module is run as the main script.

    See the official Phantom documentation for information about
    `phantom.base_connector.BaseConnector` and its members.
    """

    @ActionHandler(action_type='test')
    def test_connectivity(self):
        """
        Reports simple messages to Phantom using standard Python logging.
        """
        self.logger.info(
            'Hello! By default, log messages of level INFO and above will be'
            ' displayed using save_progress regardless of Phantom debug'
            ' logging configuration.'
        )
        self.logger.info(
            'An connector-specific logfile will also be created at %s',
            self.app_log_directory.joinpath('connector.log'),
        )
        self.logger.info(
            'All log messages of level ERROR and above will be logged to '
            '`%s/spawn.log`.',
            self.phantom_log_directory
        )
        self.logger.info(
            'If debug logging is enabled, all log messages of level DEBUG and '
            'above (including these INFO calls) will also be logged.'
        )
        self.logger.debug(
            'This DEBUG message will not be displayed using save_progress, but'
            ' if system debug logging is enabled, this message will be'
            ' logged to `%s/spawn.log`',
            self.phantom_log_directory,
        )
        self.logger.error(
            'This ERROR message will be logged regardless of Phantom logging'
            ' configuration, and also displayed using save_progress.'
        )
        return []

    @ActionHandler(action_type='ingest', read_only=True)
    def on_poll(
            self,
            start_time: int,
            end_time: int,
            container_count: int,
            artifact_count: int,
            container_id: str = None,
    ):
        """
        Callback action for the on_poll ingest functionality.

        :param container_id: Container IDs to limit the ingestion to.
        :param start_time:
            Start of time range, in epoch time (milliseconds)

            If not specified, the default is past 10 days
        :param end_time:
            End of time range, in epoch time (milliseconds)

            If not specified, the default is now"
        :param container_count:
            Maximum number of container records to query for.
        :param artifact_count: Maximum number of artifact records to query for.
        """
        if self.is_poll_now():
            self.logger.info(
                'Currently running as a result of hitting the `POLL NOW`'
                ' button under asset settings'
            )

        self.logger.info(
            (
                'None of start time %s, end time %s, or container_id %s will'
                ' be used to generate these fake containers.'
            ),
            start_time,
            end_time,
            container_id,
        )

        self.logger.info(
            'Generating %s fake containers with %s fake artifacts each',
            container_count,
            artifact_count,
        )

        containers = []
        for container_index in range(container_count):
            container = Container.from_fields(
                name=f'dummy_container {container_index}')

            for artifact_index in range(artifact_count):
                artifact = Artifact.from_fields(
                    name=f'dummy artifact {artifact_index}',
                    source_data_identifier=str(uuid4()),
                    cef={'dummy_key': 'dummy_value'},
                )
                container.add_artifact(artifact)

            containers.append(container)

        return self.save_all_containers(containers)

    @ActionHandler(
        action_type='generic',
        data_contains={
            'name': Text, 'value': Text, 'type': Text, 'context': Text},
        lock='parameters.required_str',
        lock_timeout=10,
    )
    def dummy_action(
            self,
            required_number: Count,
            required_str: Text,
            required_bool: bool,
            required_choice: Choice,
            optional_number: Amount = 42.69,
            optional_str: Text = 'spam',
            optional_bool: bool = False,
            optional_choice: Choice = None,
    ):
        """
        Takes a variety of parameters and reports them back to Phantom.

        The parameter type annotations are used to infer the `data_type` for
        each parameter in the generated metadata unless new values are manually
        specified.

        Because the data path to the `required_str` parameter is specified as
        the value for `lock` in the `ActionHandler` parameters, the action will
        be scheduled synchronously only with regard to other actions which
        specify the same value for `lock`.

        :param required_number: A mandatory number
        :param required_str: A mandatory string
        :param required_bool: A mandatory bool
        :param required_choice: A mandatory choice
        :param optional_number: An optional number
        :param optional_str: An optional string
        :param optional_bool: An optional bool
        :param optional_choice: An optional choice
        """
        self.logger.info('State: %r', self.state)
        names = [
            'required_number',
            'required_str',
            'required_bool',
            'required_choice',
            'optional_number',
            'optional_str',
            'optional_bool',
            'optional_choice',
        ]
        local_vars = locals()
        for x in names:
            value = local_vars[x]
            data = {
                'name': x,
                'value': value,
                'type': type(value).__name__,
                'context': str(self.context),
            }
            yield data
            self.state['last_data'] = data

    @dummy_action.summary_contains(
        {
            'message': Text,
            'results.name': Text,
            'results.value': Text,
            'results.type': Text,
            'results.context': Text,
        },
    )
    def summarise(self, results):
        """
        Create a summary object from the result of dummy_action.

        :param iterable results: The output of a call to dummy_action
        :return: A dictionary summarising the result of dummy_action
        :rtype: dict
        """
        return {'message': 'Dummy action ran', 'results': results}

    @ActionHandler(action_type='generic', lock=None)
    async def dummy_async(self, concurrency: int, sleep: int):
        """
        Run concurrent sleep coroutines for the specified time.

        Because `lock` is set to `None` in the `ActionHandler` parameters, this
        action will be scheduled asynchronously with regard to all other
        actions.
        Asynchronous action scheduling is separate from asynchronous coroutine
        execution, which this action also demonstrates.

        :param concurrency: The number of concurrent sleep actions
        :param sleep: The number of seconds for which to sleep
        """
        self.logger.debug('Gathering sleeps')

        async def report_delay():
            loop = asyncio.get_event_loop()
            start = loop.time()
            await asyncio.sleep(sleep)
            return loop.time() - start

        results = await asyncio.gather(
            *(report_delay() for _ in range(concurrency)))

        for data in results:
            yield {'slept': data}

    @dummy_async.summary
    def summarise_async(self, results):
        return {
            'max_sleep_time': max(d['slept'] for d in results),
            'count': len(results),
        }


@Connector.dummy_action.custom_view(title='Dummy Title', width=10, height=5)
def display_dummy_results(provides, all_app_runs, context):
    """
    This function is registered as the custom view function for dummy_action.

    By default, the html template used to render the view will be located at
    `views/<function_name>.html`, in this case
    `views/display_dummy_results.html`.

    The logic in the template will have access to the namespace passed into
    this function as the `context` parameter.
    By adding data to the `results` key, this function allows the template
    to use a variable named `results` containing whatever data is added.
    """
    results = context.setdefault('results', [])
    for summary, action_results in all_app_runs:
        result_data = {
            'summary': summary,
            'action_results': [a.get_dict() for a in action_results]
        }
        results.append(result_data)
