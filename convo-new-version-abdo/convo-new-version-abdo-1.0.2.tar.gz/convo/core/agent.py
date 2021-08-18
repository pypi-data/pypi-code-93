from asyncio import CancelledError
import logging
import os
import shutil
import tempfile
from typing import Any, Callable, Dict, List, Optional, Text, Tuple, Union
import uuid

import aiohttp
from aiohttp import ClientError

import convo
from convo.core import jobs, training
from convo.core.channels.channel import OutputSocket, UserMsg
from convo.core.constants import BY_DEFAULT_REQUEST_TIMEOUT
from convo.shared.core.domain import Domain
from convo.core.exceptions import AgentNotPrepared
import convo.core.interpreter
from convo.shared.constants import (
    CONVO_DEFAULT_SENDER_ID ,
    CONVO_DEFAULT_DOMAIN_PATH,
    DEFAULT_CORE_SUB_DIRECTORY_NAME,
)
from convo.shared.nlu.interpreter import NaturalLangInterpreter, RegexInterpreter
from convo.core.lock_store import InMemoryLockStorage, LockStore
from convo.core.nlg import NaturalLanguageGenerator
from convo.core.policies.ensemble import EnsemblePolicy, SimplePolicyEnsemble
from convo.core.policies.memoization import MemoizationPolicy
from convo.core.policies.policy import Policy
from convo.core.processor import MsgProcessor
from convo.core.tracker_store import (
    FailSafeTrackerStorage,
    InMemoryTrackerStorage,
    TrackerStorage,
)
from convo.shared.core.trackers import DialogueStateTracer
import convo.core.utils
from convo.exceptions import ModelNotPresent
from convo.shared.importers.importer import TrainingDataImporter
from convo.model import (
    fetch_latest_model,
    fetch_model,
    fetch_model_subdirectories,
    unpacking_model,
)
from convo.nlu.utils import is_url
import convo.shared.utils.io
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.utils.endpoints import EndpointConfiguration
import convo.utils.io

log = logging.getLogger(__name__)


async def loaded_from_server(agent: "CoreAgent", model_server: EndpointConfiguration) -> "CoreAgent":
    """Load a persisted model from a server."""

    # We are going to pull the model once first, and then schedule a recurring
    # job. the benefit of this approach is that we can be sure that there
    # is a model after this function completes -> allows to do proper
    # "is alive" check on a startup server's `/status` endpoint. If the server
    # is started, we can be sure that it also already loaded (or tried to)
    # a model.
    await _upgrade_model_from_server(model_server, agent)

    wait_time_between_two_pulls = model_server.kwargs.get("wait_time_between_pulls", 100)

    if wait_time_between_two_pulls:
        # continuously pull the model every `wait_time_between_pulls` seconds
        await scheduling_model_pull(model_server, int(wait_time_between_two_pulls), agent)

    return agent


def _interpreter_loaded(
    agent: "CoreAgent", nlu_path: Optional[Text]
) -> NaturalLangInterpreter:
    """Load the NLU interpreter at `nlu_path`.

    Args:
        agent: Instance of `CoreAgent` to inspect for an interpreter if `nlu_path` is
            `None`.
        nlu_path: NLU model path.

    Returns:
        The NLU interpreter.
    """
    if nlu_path:
        return convo.core.interpreter.generate_interpreter(nlu_path)

    return agent.interpreter or RegexInterpreter()


def _load_domain_and_policy_package(
    core_path: Optional[Text],
) -> Tuple[Optional[Domain], Optional[EnsemblePolicy]]:
    """Load the domain and policy ensemble from the model at `core_path`.

    Args:
        core_path: Core model path.

    Returns:
        An instance of `Domain` and `EnsemblePolicy` if `core_path` is not `None`.
    """
    policy_group = None
    domain_name = None

    if core_path:
        policy_group = EnsemblePolicy.load(core_path)
        domain_path_flow = os.path.join(os.path.abspath(core_path), CONVO_DEFAULT_DOMAIN_PATH)
        domain_name = Domain.load(domain_path_flow)

    return domain_name, policy_group


def _load_and_put_upgraded_model(
    agent: "CoreAgent", model_directory: Text, fingerprint: Text
) -> None:
    """Load the persisted model into memory and set the model on the agent.

    Args:
        agent: Instance of `CoreAgent` to update with the new model.
        model_directory: Convo model directory.
        fingerprint: Fingerprint of the supplied model at `model_directory`.
    """
    log.debug(f"Found new model with fingerprint {fingerprint}. Loading...")

    core_path_flow, nlu_path_flow = fetch_model_subdirectories(model_directory)

    agent_interpreter = _interpreter_loaded(agent, nlu_path_flow)
    domain, policy_group = _load_domain_and_policy_package(core_path_flow)

    agent.upgrade_model(
        domain, policy_group, fingerprint, agent_interpreter, model_directory
    )

    log.debug("Finished updating agent to new model.")


async def _upgrade_model_from_server(
    model_server: EndpointConfiguration, agent: "CoreAgent"
) -> None:
    """Load a zipped Convo Core model from a URL and update the passed agent."""

    if not is_url(model_server.url):
        raise aiohttp.InvalidURL(model_server.url)

    model_dir = tempfile.mkdtemp()
    remove_directory = True

    try:
        new_finger_print = await _pull_model_and_finger_print(
            model_server, agent.fingerprint, model_dir
        )

        if new_finger_print:
            _load_and_put_upgraded_model(agent, model_dir, new_finger_print)
            remove_directory = False
        else:
            log.debug(f"No new model found at URL {model_server.url}")
    except Exception:  # skipcq: PYL-W0703
        # TODO: Make this exception more specific, possibly print different log
        # for each one.
        log.exception(
            "Failed to update model. The previous model will stay loaded instead."
        )
    finally:
        if remove_directory:
            shutil.rmtree(model_dir)


async def _pull_model_and_finger_print(
    model_server: EndpointConfiguration, fingerprint: Optional[Text], model_directory: Text
) -> Optional[Text]:
    """Queries the model server.

    Args:
        model_server: Model server endpoint information.
        fingerprint: Current model fingerprint.
        model_directory: Directory where to download model to.

    Returns:
        Value of the response's <ETag> header which contains the model
        hash. Returns `None` if no new model is found.
    """
    headers_name = {"If-None-Match": fingerprint}

    log.debug(f"Requesting model from server {model_server.url}...")

    async with model_server.endpoint_session() as session:
        try:
            parameters = model_server.combine_params()
            async with session.request(
                "GET",
                model_server.url,
                timeout=BY_DEFAULT_REQUEST_TIMEOUT,
                headers=headers_name,
                params=parameters,
            ) as resp:

                if resp.status in [204, 304]:
                    log.debug(
                        "Model server returned {} status code, "
                        "indicating that no new model is available. "
                        "Current fingerprint: {}"
                        "".format(resp.status, fingerprint)
                    )
                    return None
                elif resp.status == 404:
                    log.debug(
                        "Model server could not find a model at the requested "
                        "endpoint '{}'. It's possible that no model has been "
                        "trained, or that the requested tag hasn't been "
                        "assigned.".format(model_server.url)
                    )
                    return None
                elif resp.status != 200:
                    log.debug(
                        "Tried to fetch model from server, but server response "
                        "status code is {}. We'll retry later..."
                        "".format(resp.status)
                    )
                    return None

                convo.utils.io.un_archive(await resp.reading(), model_directory)
                log.debug(
                    "Unzipped model to '{}'".format(os.path.abspath(model_directory))
                )

                # return the new fingerprint
                return resp.headers.get("ETag")

        except aiohttp.ClientError as e:
            log.debug(
                "Tried to fetch model from server, but "
                "couldn't reach server. We'll retry later... "
                "Error: {}.".format(e)
            )
            return None


async def _execute_model_pulling_worker(
    model_server: EndpointConfiguration, agent: "CoreAgent"
) -> None:
    # noinspection PyBroadException
    try:
        await _upgrade_model_from_server(model_server, agent)
    except CancelledError:
        log.warning("Stopping model pulling (cancelled).")
    except ClientError:
        log.exception(
            "An exception was raised while fetching a model. Continuing anyways..."
        )


async def scheduling_model_pull(
    model_server: EndpointConfiguration, wait_time_between_pulls: int, agent: "CoreAgent"
):
    (await jobs.schedule_jobs()).add_job(
        _execute_model_pulling_worker,
        "interval",
        seconds=wait_time_between_pulls,
        args=[model_server, agent],
        id="pull-model-from-server",
        replace_existing=True,
    )


async def agent_load(
    model_path: Optional[Text] = None,
    model_server: Optional[EndpointConfiguration] = None,
    remote_storage: Optional[Text] = None,
    interpreter: Optional[NaturalLangInterpreter] = None,
    generator: Union[EndpointConfiguration, NaturalLanguageGenerator] = None,
    tracker_store: Optional[TrackerStorage] = None,
    lock_store: Optional[LockStore] = None,
    action_endpoint: Optional[EndpointConfiguration] = None,
):
    try:
        if model_server is not None:
            return await loaded_from_server(
                CoreAgent(
                    interpreter=interpreter,
                    generator=generator,
                    tracker_store=tracker_store,
                    lock_store=lock_store,
                    action_endpoint=action_endpoint,
                    model_server=model_server,
                    remote_storage=remote_storage,
                ),
                model_server,
            )

        elif remote_storage is not None:
            return CoreAgent.load_from_remote_cache(
                remote_storage,
                model_path,
                interpreter=interpreter,
                generator=generator,
                tracker_store=tracker_store,
                lock_store=lock_store,
                action_endpoint=action_endpoint,
                model_server=model_server,
            )

        elif model_path is not None and os.path.exists(model_path):
            return CoreAgent.load_localized_model(
                model_path,
                interpreter=interpreter,
                generator=generator,
                tracker_store=tracker_store,
                lock_store=lock_store,
                action_endpoint=action_endpoint,
                model_server=model_server,
                remote_storage=remote_storage,
            )

        else:
            convo.shared.utils.io.raising_warning(
                "No valid configuration given to load agent."
            )
            return None

    except Exception as e:
        log.error(f"Could not load model due to {e}.")
        raise


class CoreAgent:
    """The CoreAgent class provides a convenient interface for the most important
    Convo functionality.

    This includes training, handling messages, loading a dialogue model,
    getting the next action, and handling a channel."""

    def __init__(
        self,
        domain: Union[Text, Domain, None] = None,
        policies: Union[EnsemblePolicy, List[Policy], None] = None,
        interpreter: Optional[NaturalLangInterpreter] = None,
        generator: Union[EndpointConfiguration, NaturalLanguageGenerator, None] = None,
        tracker_store: Optional[TrackerStorage] = None,
        lock_store: Optional[LockStore] = None,
        action_endpoint: Optional[EndpointConfiguration] = None,
        fingerprint: Optional[Text] = None,
        model_directory: Optional[Text] = None,
        model_server: Optional[EndpointConfiguration] = None,
        remote_storage: Optional[Text] = None,
        path_to_model_archive: Optional[Text] = None,
    ):
        # Initializing variables with the passed parameters.
        self.domain = self._generate_domain(domain)
        self.policy_ensemble = self._generate_ensemble(policies)

        if self.domain is not None:
            self.domain.add_new_requested_slot()
            self.domain.add_knowledge_base_slot()
            self.domain.add_category_wise_slot_default_value()

        EnsemblePolicy.inspect_domain_combination_compatibility(
            self.policy_ensemble, self.domain
        )

        self.interpreter = convo.core.interpreter.generate_interpreter(interpreter)

        self.nlg = NaturalLanguageGenerator.create(generator, self.domain)
        self.tracker_store = self.generate_tracker_store(tracker_store, self.domain)
        self.lock_store = self._generate_tracker_store(lock_store)
        self.action_endpoint = action_endpoint

        self._set_finger_print(fingerprint)
        self.model_directory = model_directory
        self.model_server = model_server
        self.remote_storage = remote_storage
        self.path_to_model_archive = path_to_model_archive

    def upgrade_model(
        self,
        domain: Optional[Domain],
        policy_ensemble: Optional[EnsemblePolicy],
        fingerprint: Optional[Text],
        interpreter: Optional[NaturalLangInterpreter] = None,
        model_directory: Optional[Text] = None,
    ) -> None:
        self.domain = self._generate_domain(domain)
        self.policy_ensemble = policy_ensemble

        if interpreter:
            self.interpreter = convo.core.interpreter.generate_interpreter(interpreter)

        self._set_finger_print(fingerprint)

        # update domain on all instances
        self.tracker_store.domain = domain
        if hasattr(self.nlg, "templates"):
            self.nlg.templates = domain.templates if domain else {}

        self.model_directory = model_directory

    @classmethod
    def load(
        cls,
        model_path: Text,
        interpreter: Optional[NaturalLangInterpreter] = None,
        generator: Union[EndpointConfiguration, NaturalLanguageGenerator] = None,
        tracker_store: Optional[TrackerStorage] = None,
        lock_store: Optional[LockStore] = None,
        action_endpoint: Optional[EndpointConfiguration] = None,
        model_server: Optional[EndpointConfiguration] = None,
        remote_storage: Optional[Text] = None,
        path_to_model_archive: Optional[Text] = None,
    ) -> "CoreAgent":
        """Load a persisted model from the passed path."""
        try:
            if not model_path:
                raise ModelNotPresent("No path specified.")
            if not os.path.exists(model_path):
                raise ModelNotPresent(f"No file or directory at '{model_path}'.")
            if os.path.isfile(model_path):
                model_path = fetch_model(model_path)
        except ModelNotPresent:
            raise ValueError(
                "You are trying to load a MODEL from '{}', which is not possible. \n"
                "The model path should be a 'tar.gz' file or a directory "
                "containing the various model files in the sub-directories 'core' "
                "and 'nlu'. \n\nIf you want to load training data instead of "
                "a model, use `agent.load_data(...)` instead.".format(model_path)
            )

        model_core, model_nlu = fetch_model_subdirectories(model_path)

        if not interpreter and model_nlu:
            interpreter = convo.core.interpreter.generate_interpreter(model_nlu)

        domain_name = None
        group = None

        if model_core:
            domain_name = Domain.load(os.path.join(model_core, CONVO_DEFAULT_DOMAIN_PATH))
            group = EnsemblePolicy.load(model_core) if model_core else None

            # ensures the domain hasn't changed between test and train
            domain_name.compare_with_specs(model_core)

        return cls(
            domain=domain_name,
            policies=group,
            interpreter=interpreter,
            generator=generator,
            tracker_store=tracker_store,
            lock_store=lock_store,
            action_endpoint=action_endpoint,
            model_directory=model_path,
            model_server=model_server,
            remote_storage=remote_storage,
            path_to_model_archive=path_to_model_archive,
        )

    def is_core_prepared(self) -> bool:
        """Check if all necessary components and policies are ready to use the agent."""
        return self.is_prepared() and self.policy_ensemble is not None

    def is_prepared(self) -> bool:
        """Check if all necessary components are instantiated to use agent.

        Policies might not be available, if this is an NLU only agent."""

        return self.tracker_store is not None and self.interpreter is not None

    async def parse_msg_using_nlu_interpreter(
        self, message_data: Text, tracker: DialogueStateTracer = None
    ) -> Dict[Text, Any]:
        """Handles message text and intent payload input messages.

        The return value of this function is parsed_data.

        Args:
            message_data (Text): Contain the received message in text or\
            intent payload format.
            tracker (DialogueStateTracer): Contains the tracker to be\
            used by the interpreter.

        Returns:
            The parsed message.

            Example:

                {\
                    "text": '/greet{"name":"Convo"}',\
                    "intent": {"name": "greet", "confidence": 1.0},\
                    "intent_ranking": [{"name": "greet", "confidence": 1.0}],\
                    "entities": [{"entity": "name", "start": 6,\
                                  "end": 21, "value": "Convo"}],\
                }

        """

        processor_name = self.create_processor()
        msg = UserMsg(message_data)
        return await processor_name.parse_msg(msg, tracker)

    async def handle_message(
        self,
        message: UserMsg,
        message_preprocessor: Optional[Callable[[Text], Text]] = None,
        **kwargs,
    ) -> Optional[List[Dict[Text, Any]]]:
        """Handle a single message."""

        if not isinstance(message, UserMsg):
            # DEPRECATION EXCEPTION - remove in 2.1
            raise Exception(
                "Passing a text to `agent.handle_message(...)` is "
                "not supported anymore. Rather use `agent.handle_text(...)`."
            )

        def noop(_: Any) -> None:
            log.info("Ignoring message as there is no agent to handle it.")

        if not self.is_prepared():
            return noop(message)

        processor_name = self.create_processor(message_preprocessor)

        async with self.lock_store.secure_lock(message.sender_id):
            return await processor_name.handle_msg(message)

    # noinspection PyUnusedLocal
    async def forecast_next(
        self, sender_id: Text, **kwargs: Any
    ) -> Optional[Dict[Text, Any]]:
        """Handle a single message."""

        processor = self.create_processor()
        return await processor.forecast_next(sender_id)

    # noinspection PyUnusedLocal
    async def log_msg(
        self,
        message: UserMsg,
        message_preprocessor: Optional[Callable[[Text], Text]] = None,
        **kwargs: Any,
    ) -> Optional[DialogueStateTracer]:
        """Append a message to a dialogue - does not predict actions."""

        processor_name = self.create_processor(message_preprocessor)
        return await processor_name.log_msg(message)

    async def perform_action(
        self,
        sender_id: Text,
        action: Text,
        output_channel: OutputSocket,
        policy: Text,
        confidence: float,
    ) -> Optional[DialogueStateTracer]:
        """Handle a single message."""

        processor_name = self.create_processor()
        return await processor_name.perform_action(
            sender_id, action, output_channel, self.nlg, policy, confidence
        )

    async def intention_trigger(
        self,
        name_of_intent: Text,
        entities: List[Dict[Text, Any]],
        output_channel: OutputSocket,
        tracker: DialogueStateTracer,
    ) -> None:
        """Trigger a user intent, e.g. triggered by an external event."""

        processor_name = self.create_processor()
        await processor_name.trigger_external_user_changed(
            name_of_intent, entities, tracker, output_channel
        )

    async def handle_txt(
        self,
        text_msg: Union[Text, Dict[Text, Any]],
        message_preprocessor: Optional[Callable[[Text], Text]] = None,
        output_channel: Optional[OutputSocket] = None,
        sender_id: Optional[Text] = CONVO_DEFAULT_SENDER_ID ,
    ) -> Optional[List[Dict[Text, Any]]]:
        """Handle a single message.

        If a message preprocessor is passed, the message will be passed to that
        function first and the return value is then used as the
        input for the dialogue engine.

        The return value of this function depends on the ``output_channel``. If
        the output channel is not set, set to ``None``, or set
        to ``CollectOutputChannel`` this function will return the messages
        the bot wants to respond.

        :Example:

            >>> from convo.core.agent import CoreAgent
            >>> from convo.core.interpreter import ConvoNLUInterpreter
            >>> agent = CoreAgent.load("examples/moodbot/models")
            >>> await agent.handle_txt("hello")
            [u'how can I help you?']

        """

        if isinstance(text_msg, str):
            text_msg = {"text": text_msg}

        message = UserMsg(text_msg.get("text"), output_channel, sender_id)

        return await self.handle_message(message, message_preprocessor)

    def memoization_toggle(self, activate: bool) -> None:
        """Toggles the memoization on and off.

        If a memoization policy is present in the ensemble, this will toggle
        the prediction of that policy. When set to ``False`` the Memoization
        policies present in the policy ensemble will not make any predictions.
        Hence, the prediction result from the ensemble always needs to come
        from a different policy (e.g. ``TEDPolicy``). Useful to test
        prediction
        capabilities of an ensemble when ignoring memorized turns from the
        training data."""

        if not self.policy_ensemble:
            return

        for p in self.policy_ensemble.policies:
            # explicitly ignore inheritance (e.g. augmented memoization policy)
            if type(p) is MemoizationPolicy:
                p.toggle(activate)

    def _maximum_history(self) -> int:
        """Find maximum max_history."""

        maximum_histories = [
            policy.featurizer.max_history
            for policy in self.policy_ensemble.policies
            if policy.featurizer
            and hasattr(policy.featurizer, "max_history")
            and policy.featurizer.max_history is not None
        ]

        return max(maximum_histories or [0])

    def _are_all_featurizers_using_a_maximum_history(self) -> bool:
        """Check if all featurizers are MaxHistoryTrackerFeaturizer."""

        def has_max_history_featurizer(policy: Policy) -> bool:
            return (
                policy.featurizer
                and hasattr(policy.featurizer, "max_history")
                and policy.featurizer.max_history is not None
            )

        for p in self.policy_ensemble.policies:
            if p.featurizer and not has_max_history_featurizer(p):
                return False
        return True

    async def load_data_set(
        self,
        training_resource: Union[Text, TrainingDataImporter],
        remove_identical: bool = True,
        unique_last_num_of_states: Optional[int] = None,
        augmentation_factor: int = 50,
        tracker_limit: Optional[int] = None,
        use_story_concatenation: bool = True,
        debug_plots: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> List[DialogueStateTracer]:
        """Load training data from a resource."""

        maximum_histories = self._maximum_history()

        if unique_last_num_of_states is None:
            # for speed up of data generation
            # automatically detect unique_last_num_of_states
            # if it was not set and
            # if all featurizers are MaxHistoryTrackerFeaturizer
            if self._are_all_featurizers_using_a_maximum_history():
                unique_last_num_of_states = maximum_histories
        elif unique_last_num_of_states < maximum_histories:
            # possibility of data loss
            convo.shared.utils.io.raising_warning(
                f"unique_last_num_of_states={unique_last_num_of_states} but "
                f"maximum max_history={maximum_histories}. "
                f"Possibility of data loss. "
                f"It is recommended to set "
                f"unique_last_num_of_states to "
                f"at least maximum max_history."
            )

        return await training.load_data(
            training_resource,
            self.domain,
            remove_identical,
            unique_last_num_of_states,
            augmentation_factor,
            tracker_limit,
            use_story_concatenation,
            debug_plots,
            exclusion_percentage=exclusion_percentage,
        )

    def train(
        self, training_trackers: List[DialogueStateTracer], **kwargs: Any
    ) -> None:
        """Train the policies / policy ensemble using dialogue data from file.

        Args:
            training_trackers: trackers to train on
            **kwargs: additional arguments passed to the underlying ML
                           trainer (e.g. keras parameters)
        """
        if not self.is_core_prepared():
            raise AgentNotPrepared("Can't train without a policy ensemble.")

        if isinstance(training_trackers, str):
            # the user most likely passed in a file name to load training
            # data from
            raise Exception(
                "Passing a file name to `agent.train(...)` is "
                "not supported anymore. Rather load the data with "
                "`data = agent.load_data(filename)` and pass it "
                "to `agent.train(data)`."
            )

        log.debug(f"CoreAgent trainer got kwargs: {kwargs}")

        self.policy_ensemble.train(
            training_trackers, self.domain, interpreter=self.interpreter, **kwargs
        )
        self._set_finger_print()

    def _set_finger_print(self, fingerprint: Optional[Text] = None) -> None:

        if fingerprint:
            self.fingerprint = fingerprint
        else:
            self.fingerprint = uuid.uuid4().hex

    @staticmethod
    def _clear_model_dir(model_path: Text) -> None:
        """Remove existing files from model directory.

        Only removes files if the directory seems to contain a previously
        persisted model. Otherwise does nothing to avoid deleting
        `/` by accident."""

        if not os.path.exists(model_path):
            return

        domain_specific_path = os.path.join(model_path, "metadata.json")
        # check if there were a model before
        if os.path.exists(domain_specific_path):
            log.info(
                "Model directory {} exists and contains old "
                "model files. All files will be overwritten."
                "".format(model_path)
            )
            shutil.rmtree(model_path)
        else:
            log.debug(
                "Model directory {} exists, but does not contain "
                "all old model files. Some files might be "
                "overwritten.".format(model_path)
            )

    def persist(self, model_path_flow: Text) -> None:
        """Persists this agent into a directory for later loading and usage."""

        if not self.is_core_prepared():
            raise AgentNotPrepared("Can't persist without a policy ensemble.")

        if not model_path_flow.endswith(DEFAULT_CORE_SUB_DIRECTORY_NAME):
            model_path_flow = os.path.join(model_path_flow, DEFAULT_CORE_SUB_DIRECTORY_NAME)

        self._clear_model_dir(model_path_flow)

        self.policy_ensemble.persist(model_path_flow)
        self.domain.persist(os.path.join(model_path_flow, CONVO_DEFAULT_DOMAIN_PATH))
        self.domain.persist_specs(model_path_flow)

        log.info("Persisted model to '{}'".format(os.path.abspath(model_path_flow)))

    async def fetch_visualization(
        self,
        resource_name: Text,
        output_file: Text,
        max_history: Optional[int] = None,
        nlu_training_data: Optional[TrainingDataSet] = None,
        should_merge_nodes: bool = True,
        fontsize: int = 12,
    ) -> None:
        from convo.shared.core.training_data.visualization import imaginary_stories
        from convo.shared.core.training_data import loading

        """Visualize the loaded training data from the resource."""

        # if the user doesn't provide a max history, we will use the
        # largest value from any policy
        max_history = max_history or self._maximum_history()

        story_sequence = await loading.load_data_from_resource(resource_name, self.domain)
        await imaginary_stories(
            story_sequence,
            self.domain,
            output_file,
            max_history,
            self.interpreter,
            nlu_training_data,
            should_merge_nodes,
            fontsize,
        )

    def create_processor(
        self, preprocessor: Optional[Callable[[Text], Text]] = None
    ) -> MsgProcessor:
        """Instantiates a processor based on the set state of the agent."""
        # Checks that the interpreter and tracker store are set and
        # creates a processor
        if not self.is_prepared():
            raise AgentNotPrepared(
                "CoreAgent needs to be prepared before usage. You need to set an "
                "interpreter and a tracker store."
            )

        return MsgProcessor(
            self.interpreter,
            self.policy_ensemble,
            self.domain,
            self.tracker_store,
            self.nlg,
            action_endpoint=self.action_endpoint,
            message_preprocessor=preprocessor,
        )

    @staticmethod
    def _generate_domain(domain: Union[Domain, Text, None]) -> Domain:

        if isinstance(domain, str):
            domain = Domain.load(domain)
            domain.missing_templates_check()
            return domain
        elif isinstance(domain, Domain):
            return domain
        elif domain is None:
            return Domain.empty()
        else:
            raise ValueError(
                "Invalid param `domain`. Expected a path to a domain "
                "specification or a domain instance. But got "
                "type '{}' with value '{}'".format(type(domain), domain)
            )

    @staticmethod
    def generate_tracker_store(
        store: Optional[TrackerStorage], domain: Domain
    ) -> TrackerStorage:
        if store is not None:
            store.domain = domain
            tracker_storage = store
        else:
            tracker_storage = InMemoryTrackerStorage(domain)

        return FailSafeTrackerStorage(tracker_storage)

    @staticmethod
    def _generate_tracker_store(store: Optional[LockStore]) -> LockStore:
        if store is not None:
            return store

        return InMemoryLockStorage()

    @staticmethod
    def _generate_ensemble(
        policies: Union[List[Policy], EnsemblePolicy, None]
    ) -> Optional[EnsemblePolicy]:
        if policies is None:
            return None
        if isinstance(policies, list):
            return SimplePolicyEnsemble(policies)
        elif isinstance(policies, EnsemblePolicy):
            return policies
        else:
            type_declared = type(policies).__name__
            raise ValueError(
                "Invalid param `policies`. Passed object is "
                "of type '{}', but should be policy, an array of "
                "policies, or a policy ensemble.".format(type_declared)
            )

    @staticmethod
    def load_localized_model(
        model_path: Text,
        interpreter: Optional[NaturalLangInterpreter] = None,
        generator: Union[EndpointConfiguration, NaturalLanguageGenerator] = None,
        tracker_store: Optional[TrackerStorage] = None,
        lock_store: Optional[LockStore] = None,
        action_endpoint: Optional[EndpointConfiguration] = None,
        model_server: Optional[EndpointConfiguration] = None,
        remote_storage: Optional[Text] = None,
    ) -> "CoreAgent":
        if os.path.isfile(model_path):
            archive_model = model_path
        else:
            archive_model = fetch_latest_model(model_path)

        if archive_model is None:
            convo.shared.utils.io.raising_warning(
                f"Could not load local model in '{model_path}'."
            )
            return CoreAgent()

        working_dir = tempfile.mkdtemp()
        model_unpacked = unpacking_model(archive_model, working_dir)

        return CoreAgent.load(
            model_unpacked,
            interpreter=interpreter,
            generator=generator,
            tracker_store=tracker_store,
            lock_store=lock_store,
            action_endpoint=action_endpoint,
            model_server=model_server,
            remote_storage=remote_storage,
            path_to_model_archive=archive_model,
        )

    @staticmethod
    def load_from_remote_cache(
        remote_storage: Text,
        model_name: Text,
        interpreter: Optional[NaturalLangInterpreter] = None,
        generator: Union[EndpointConfiguration, NaturalLanguageGenerator] = None,
        tracker_store: Optional[TrackerStorage] = None,
        lock_store: Optional[LockStore] = None,
        action_endpoint: Optional[EndpointConfiguration] = None,
        model_server: Optional[EndpointConfiguration] = None,
    ) -> Optional["CoreAgent"]:
        from convo.nlu.persistor import fetch_persistor

        carry_on = fetch_persistor(remote_storage)

        if carry_on is not None:
            target_path_flow = tempfile.mkdtemp()
            carry_on.recover(model_name, target_path_flow)

            return CoreAgent.load(
                target_path_flow,
                interpreter=interpreter,
                generator=generator,
                tracker_store=tracker_store,
                lock_store=lock_store,
                action_endpoint=action_endpoint,
                model_server=model_server,
                remote_storage=remote_storage,
            )

        return None
