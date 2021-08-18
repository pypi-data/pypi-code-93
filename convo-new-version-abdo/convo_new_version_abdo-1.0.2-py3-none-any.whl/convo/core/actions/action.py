import copy
import json
import logging
from typing import List, Text, Optional, Dict, Any, Set, TYPE_CHECKING

import aiohttp

import convo.core

from convo.shared.core import events
from convo.core.constants import BY_DEFAULT_REQUEST_TIMEOUT

from convo.nlu.constants import (
    DFAULT_INTENT_RESPONSE_PICKER,
    PROP_NAME_RESPONSE_PICKER,
    PREDICTION_KEY_RESPONSE_PICKER,
    TEMPLATE_NAME_KEY_RESPONSE_PICKER,
)

from convo.shared.constants import (
    DOCUMENTS_BASE_URL,
    DEFAULT_NLU_FALLBACK_INTENTS_NAME,
    CONVO_UTTER_PREFIX ,
)
from convo.shared.core.constants import (
    USERS_INTENT_OUT_OF_SCOPE  ,
    LISTEN_ACTION_NAME  ,
    RESTART_ACTION_NAME  ,
    SESSION_START_ACTION_NAME  ,
    ACTION_DEFAULT_FALLBACK_NAME,
    DEACTIVATE_LOOP_ACTION_NAME  ,
    REVERT_FALLBACK_EVENTS_ACTION_NAME   ,
    DEFAULT_ASK_AFFIRMATION_ACTION_NAME   ,
    DEFAULT_ASK_REPHRASE_ACTION_NAME   ,
    BACK_ACTION_NAME   ,
    REQUESTED_SLOTS,
)
from convo.shared.exceptions import ConvoExceptions 
from convo.shared.nlu.constants import KEY_INTENT_NAME, KEY_INTENT_RANKING
from convo.shared.core.events import (
    UserChangeReverted,
    UserUttered,
    ActionExecuted,
    Event,
    BotUttered,
    SetofSlot,
    OperationalLoop,
    Restarted,
    SessionBegan,
)
from convo.utils.endpoints import EndpointConfiguration, ClientResponseError
from convo.shared.core.domain import Domain


if TYPE_CHECKING:
    from convo.shared.core.trackers import DialogueStateTracer
    from convo.core.nlg import NaturalLanguageGenerator
    from convo.core.channels.channel import OutputSocket

log = logging.getLogger(__name__)


def default_act(action_endpoint: Optional[EndpointConfiguration] = None) -> List["Action"]:
    """List default actions."""
    from convo.core.actions.two_stage_fallback import DoubleStageFallbackAction

    return [
        ActListen(),
        ActRestart(),
        ActSessionBegins(),
        ActDefaultFallBack(),
        ActDeactivateLoop(),
        ActRevertFallbackEvents(),
        ActDefaultAskConfirmation(),
        ActDefaultAskRephrase(),
        DoubleStageFallbackAction(action_endpoint),
        ActBack(),
    ]


def _act_for_index(
    index: int, domain: Domain, action_endpoint: Optional[EndpointConfiguration]
) -> "Action":
    """Get an action based on its index in the list of available actions.

    Args:
        index: The index of the action. This is usually used by `Policy`s as they
            predict the action index instead of the name.
        domain: The `Domain` of the current model. The domain contains the actions
            provided by the user + the default actions.
        action_endpoint: Can be used to run `custom_actions`
            (e.g. using the `convo-sdk`).

    Returns:
        The instantiated `Action` or `None` if no `Action` was found for the given
        index.
    """
    if domain.number_of_actions <= index or index < 0:
        raise IndexError(
            f"Cannot access action at index {index}. "
            f"Domain has {domain.number_of_actions} actions."
        )

    return act_for_name(domain.action_names[index], domain, action_endpoint)


def act_for_name(
    action_name: Text, domain: Domain, action_endpoint: Optional[EndpointConfiguration]
) -> "Action":
    """Create an `Action` object based on the name of the `Action`.

    Args:
        action_name: The name of the `Action`.
        domain: The `Domain` of the current model. The domain contains the actions
            provided by the user + the default actions.
        action_endpoint: Can be used to run `custom_actions`
            (e.g. using the `convo-sdk`).

    Returns:
        The instantiated `Action` or `None` if no `Action` was found for the given
        index.
    """

    if action_name not in domain.action_names:
        domain.not_found_exception_rasie_action(action_name)

    should_use_form_action = (
        action_name in domain.form_names and domain.form_of_slot_mapping(action_name)
    )

    return act_from_name(
        action_name,
        action_endpoint,
        domain.user_forms_and_actions,
        should_use_form_action,
        domain.retrieval_intents,
    )


def is_retrieval_act(action_name: Text, retrieval_intents: List[Text]) -> bool:
    """Check if an action name is a retrieval action.

    The name for a retrieval action has an extra `utter_` prefix added to
    the corresponding retrieval intent name.

    Args:
        action_name: Name of the action.
        retrieval_intents: List of retrieval convo_intents defined in the NLU training data.

    Returns:
        `True` if the resolved intent name is present in the list of retrieval
        convo_intents, `False` otherwise.
    """

    return (
            ActRetrieveResponse.intent_name_from_act(action_name) in retrieval_intents
    )


def act_from_name(
    name: Text,
    action_endpoint: Optional[EndpointConfiguration],
    user_actions: List[Text],
    should_use_form_action: bool = False,
    retrieval_intents: Optional[List[Text]] = None,
) -> "Action":
    """Return an action instance for the name."""

    defaults = {a.name(): a for a in default_act(action_endpoint)}

    if name in defaults and name not in user_actions:
        return defaults[name]
    elif name.startswith(CONVO_UTTER_PREFIX ) and is_retrieval_act(
        name, retrieval_intents or []
    ):
        return ActRetrieveResponse(name)
    elif name.startswith(CONVO_UTTER_PREFIX ):
        return ActUtterTemplate(name)
    elif should_use_form_action:
        from convo.core.actions.forms import FormAction

        return FormAction(name, action_endpoint)
    else:
        return RemoteAct(name, action_endpoint)


def generate_bot_utterance(message: Dict[Text, Any]) -> BotUttered:
    """Create BotUttered event from message."""

    bot_msg = BotUttered(
        text=message.pop("text", None),
        data={
            "elements": message.pop("elements", None),
            "quick_replies": message.pop("quick_replies", None),
            "buttons": message.pop("buttons", None),
            # for legacy / compatibility reasons we need to set the image
            # to be the attachment if there is no others attachment (the
            # `.get` is intentional - no `pop` as we still need the image`
            # property to set it in the following line)
            "attachment": message.pop("attachment", None) or message.get("image", None),
            "image": message.pop("image", None),
            "custom": message.pop("custom", None),
        },
        metadata=message,
    )

    return bot_msg


class Action:
    """Next action to be taken in response to a dialogue state."""

    def name(self) -> Text:
        """Unique identifier of this simple action."""

        raise NotImplementedError

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        """
        Execute the side effects of this action.

        Args:
            nlg: which ``nlg`` to use for response generation
            output_channel: ``output_channel`` to which to send the resulting message.
            tracker (DialogueStateTracer): the state tracker for the current
                user. You can access slot values using
                ``tracker.get_slot(slot_name)`` and the most recent user
                message is ``tracker.latest_message.text``.
            domain (Domain): the bot's domain
            metadata: dictionary that can be sent to action server with custom
            data.
        Returns:
            List[Event]: A list of :class:`convo.core.events.Event` instances
        """

        raise NotImplementedError

    def __str__(self) -> Text:
        return "Action('{}')".format(self.name())


class ActUtterTemplate(Action):
    """An action which only effect is to utter a template when it is run.

    Both, name and utter template, need to be specified using
    the `name` method."""

    def __init__(self, name: Text, silent_fail: Optional[bool] = False):
        self.template_name = name
        self.silent_fail = silent_fail

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        """Simple run implementation uttering a (hopefully defined) template."""

        message = await nlg.create(self.template_name, tracker, output_channel.name())
        if message is None:
            if not self.silent_fail:
                log.error(
                    "Couldn't create message for response '{}'."
                    "".format(self.template_name)
                )
            return []
        message["template_name"] = self.template_name

        return [generate_bot_utterance(message)]

    def name(self) -> Text:
        return self.template_name

    def __str__(self) -> Text:
        return "ActionUtterTemplate('{}')".format(self.name())


class ActRetrieveResponse(ActUtterTemplate):
    """An action which queries the Response Selector for the appropriate response."""

    def __init__(self, name: Text, silent_fail: Optional[bool] = False):
        super().__init__(name, silent_fail)
        self.action_name = name
        self.silent_fail = silent_fail

    @staticmethod
    def intent_name_from_act(action_name: Text) -> Text:
        """Resolve the name of the intent from the action name."""
        return action_name.split(CONVO_UTTER_PREFIX )[1]

    @staticmethod
    def act_name_from_intent(name_of_intent: Text) -> Text:
        """Resolve the action name from the name of the intent."""
        return f"{CONVO_UTTER_PREFIX }{name_of_intent}"

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        """Query the appropriate response and create a bot utterance with that."""

        response_selector_properties = tracker.latest_message.parse_data[
            PROP_NAME_RESPONSE_PICKER
        ]

        if (
            self.intent_name_from_act(self.action_name)
            in response_selector_properties
        ):
            query_key = self.intent_name_from_act(self.action_name)
        elif DFAULT_INTENT_RESPONSE_PICKER in response_selector_properties:
            query_key = DFAULT_INTENT_RESPONSE_PICKER
        else:
            if not self.silent_fail:
                log.error(
                    "Couldn't create message for response action '{}'."
                    "".format(self.action_name)
                )
            return []

        log.debug(f"Picking response from selector of type {query_key}")
        select = response_selector_properties[query_key]

        # Override template name of ActionUtterTemplate
        # with the complete template name retrieved from
        # the output of response selector.
        self.template_name = select[PREDICTION_KEY_RESPONSE_PICKER][
            TEMPLATE_NAME_KEY_RESPONSE_PICKER
        ]

        return await super().run(output_channel, nlg, tracker, domain)

    def name(self) -> Text:
        return self.action_name

    def __str__(self) -> Text:
        return "ActionRetrieveResponse('{}')".format(self.name())


class ActBack(ActUtterTemplate):
    """Revert the tracker state by two user utterances."""

    def name(self) -> Text:
        return BACK_ACTION_NAME   

    def __init__(self) -> None:
        super().__init__("utter_back", silent_fail=True)

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        # only utter the response if it is available
        evts = await super().run(output_channel, nlg, tracker, domain)

        return evts + [UserChangeReverted(), UserChangeReverted()]


class ActListen(Action):
    """The first action in any turn - bot waits for a user message.

    The bot should stop taking further actions and wait for the user to say
    something."""

    def name(self) -> Text:
        return LISTEN_ACTION_NAME  

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        return []


class ActRestart(ActUtterTemplate):
    """Resets the tracker to its initial state.

    Utters the Restarted response if available."""

    def name(self) -> Text:
        return RESTART_ACTION_NAME  

    def __init__(self) -> None:
        super().__init__("utter_restart", silent_fail=True)

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        # only utter the response if it is available
        evts = await super().run(output_channel, nlg, tracker, domain)

        return evts + [Restarted()]


class ActSessionBegins(Action):
    """Applies a conversation session start.

    Takes all `SetofSlot` events from the previous session and applies them to the new
    session.
    """

    # Optional arbitrary metadata that can be passed to the SessionBegan event.
    metadata: Optional[Dict[Text, Any]] = None

    def name(self) -> Text:
        return SESSION_START_ACTION_NAME  

    @staticmethod
    def _slot_put_events_from_tracker(
        tracker: "DialogueStateTracer",
    ) -> List["SetofSlot"]:
        """Fetch SetofSlot events from tracker and carry over key, value and metadata."""

        return [
          SetofSlot(key=event.key, value=event.value, metadata=event.metadata)
            for event in tracker.request_events()
            if isinstance(event, SetofSlot)
        ]

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        _events = [SessionBegan(metadata=self.metadata)]

        if domain.session_configuration.carry_over_slots:
            _events.extend(self._slot_put_events_from_tracker(tracker))

        _events.append(ActionExecuted(LISTEN_ACTION_NAME  ))

        return _events


class ActDefaultFallBack(ActUtterTemplate):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return ACTION_DEFAULT_FALLBACK_NAME

    def __init__(self) -> None:
        super().__init__("utter_default", silent_fail=True)

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        # only utter the response if it is available
        events = await super().run(output_channel, nlg, tracker, domain)

        return events + [UserChangeReverted()]


class ActDeactivateLoop(Action):
    """Deactivates an active loop."""

    def name(self) -> Text:
        return DEACTIVATE_LOOP_ACTION_NAME  

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        return [OperationalLoop(None), SetofSlot(REQUESTED_SLOTS, None)]


class RemoteAct(Action):
    def __init__(self, name: Text, action_endpoint: Optional[EndpointConfiguration]) -> None:

        self._name = name
        self.action_endpoint = action_endpoint

    def _act_call_format(
        self, tracker: "DialogueStateTracer", domain: "Domain"
    ) -> Dict[Text, Any]:
        """Create the request json send to the action server."""
        from convo.shared.core.trackers import releaseVerbosity

        tracker_state = tracker.current_active_state(releaseVerbosity.ALL)

        return {
            "next_action": self._name,
            "sender_id": tracker.sender_id,
            "tracker": tracker_state,
            "domain": domain.as_dictionary(),
            "version": convo.__version__,
        }

    @staticmethod
    def act_response_format_specification() -> Dict[Text, Any]:
        """Expected response schema for an Action endpoint.

        Used for validation of the response returned from the
        Action endpoint."""
        return {
            "type": "object",
            "properties": {
                "events": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"event": {"type": "string"}},
                    },
                },
                "responses": {"type": "array", "items": {"type": "object"}},
            },
        }

    def _validate_act_output(self, result: Dict[Text, Any]) -> bool:
        from jsonschema import validate
        from jsonschema import ValidationError

        try:
            validate(result, self.act_response_format_specification())
            return True
        except ValidationError as e:
            e.msg += (
                f". Failed to validate Action server response from API, "
                f"make sure your response from the Action endpoint is valid. "
                f"For more information about the format visit "
                f"{DOCUMENTS_BASE_URL}/custom-actions"
            )
            raise e

    @staticmethod
    async def _utter_response(
        responses: List[Dict[Text, Any]],
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
    ) -> List[BotUttered]:
        """Use the responses generated by the action endpoint and utter them."""

        bot_msg = []
        for response_result in responses:
            temp = response_result.pop("template", None)
            if temp:
                draft = await nlg.create(
                    temp, tracker, output_channel.name(), **response_result
                )
                if not draft:
                    continue
                draft["template_name"] = temp
            else:
                draft = {}

            button = response_result.pop("buttons", []) or []
            if button:
                draft.setdefault("buttons", [])
                draft["buttons"].extend(button)

            # Avoid overwriting `draft` values with empty values
            response_result = {k: v for k, v in response_result.items() if v}
            draft.update(response_result)
            bot_msg.append(generate_bot_utterance(draft))

        return bot_msg

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        json_body = self._act_call_format(tracker, domain)
        if not self.action_endpoint:
            log.error(
                f"The model predicted the custom action '{self.name()}', "
                f"but you didn't configure an endpoint to "
                f"run this custom action. Please take a look at "
                f"the docs and set an endpoint configuration via the "
                f"--endpoints flag. "
                f"{DOCUMENTS_BASE_URL}/custom-actions"
            )
            raise Exception("Failed to execute custom action.")

        try:
            log.debug(
                "Calling action endpoint to run action '{}'.".format(self.name())
            )
            response = await self.action_endpoint.request(
                json=json_body, method="post", timeout=BY_DEFAULT_REQUEST_TIMEOUT
            )

            self._validate_act_output(response)

            events_json = response.get("events", [])
            responses = response.get("responses", [])
            bot_messages = await self._utter_response(
                responses, output_channel, nlg, tracker
            )

            evts = events.deserialized_events(events_json)
            return bot_messages + evts

        except ClientResponseError as e:
            if e.status == 400:
                response_data = json.loads(e.text)
                exception = ActExecutionRejection(
                    response_data["action_name"], response_data.get("error")
                )
                log.error(exception.message)
                raise exception
            else:
                raise Exception("Failed to execute custom action.") from e

        except aiohttp.ClientConnectionError as e:
            log.error(
                "Failed to run custom action '{}'. Couldn't connect "
                "to the server at '{}'. Is the server running? "
                "Error: {}".format(self.name(), self.action_endpoint.url, e)
            )
            raise Exception("Failed to execute custom action.")

        except aiohttp.ClientError as e:
            # not all errors have a status attribute, but
            # helpful to log if they got it

            # noinspection PyUnresolvedReferences
            stat = getattr(e, "status", None)
            log.error(
                "Failed to run custom action '{}'. Action server "
                "responded with a non 200 status code of {}. "
                "Make sure your action server properly runs actions "
                "and returns a 200 once the action is executed. "
                "Error: {}".format(self.name(), stat, e)
            )
            raise Exception("Failed to execute custom action.")

    def name(self) -> Text:
        return self._name


class ActExecutionRejection(ConvoExceptions):
    """Raising this exception will allow others policies
    to predict a different action"""

    def __init__(self, action_name: Text, message: Optional[Text] = None) -> None:
        self.action_name = action_name
        self.message = message or "Custom action '{}' rejected to run".format(
            action_name
        )
        super(ActExecutionRejection, self).__init__()

    def __str__(self) -> Text:
        return self.message


class ActRevertFallbackEvents(Action):
    """Reverts events which were done during the `TwoStageFallbackPolicy`.

    This reverts user messages and bot utterances done during a fallback
    of the `TwoStageFallbackPolicy`. By doing so it is not necessary to
    write custom stories for the different convo_paths, but only of the happy
    path. This is deprecated and can be removed once the
    `TwoStageFallbackPolicy` is removed.
    """

    def name(self) -> Text:
        return REVERT_FALLBACK_EVENTS_ACTION_NAME   

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        from convo.core.policies.two_stage_fallback import has_user_rephrased

        # User rephrased
        if has_user_rephrased(tracker):
            return _return_success_rephrasing(tracker)
        # User affirmed
        elif has_user_confirmed(tracker):
            return _return_confirmation_events(tracker)
        else:
            return []


def has_user_confirmed(tracker: "DialogueStateTracer") -> bool:
    return tracker.last_executed_action_has(DEFAULT_ASK_AFFIRMATION_ACTION_NAME   )


def _return_confirmation_events(tracker: "DialogueStateTracer") -> List[Event]:
    return_events = _return_single_confirmation_events()

    end_user_event = tracker.get_last_event_for(UserUttered)
    end_user_event = copy.deepcopy(end_user_event)
    end_user_event.parse_data["intent"]["confidence"] = 1.0

    # User affirms the rephrased intent
    rephrased_intent = tracker.last_executed_action_has(
        name=DEFAULT_ASK_REPHRASE_ACTION_NAME   , skip=1
    )
    if rephrased_intent:
        return_events += _return_rephrasing_events()

    return return_events + [end_user_event]


def _return_single_confirmation_events() -> List[Event]:
    return [
        UserChangeReverted(),  # revert affirmation and request
        # revert original intent (has to be re-added later)
        UserChangeReverted(),
        # add action listen intent
        ActionExecuted(action_name=LISTEN_ACTION_NAME  ),
    ]


def _return_success_rephrasing(tracker) -> List[Event]:
    end_user_event = tracker.get_last_event_for(UserUttered)
    end_user_event = copy.deepcopy(end_user_event)
    return _return_rephrasing_events() + [end_user_event]


def _return_rephrasing_events() -> List[Event]:
    return [
        UserChangeReverted(),  # remove rephrasing
        # remove feedback and rephrase request
        UserChangeReverted(),
        # remove affirmation request and false intent
        UserChangeReverted(),
        # replace action with action listen
        ActionExecuted(action_name=LISTEN_ACTION_NAME  ),
    ]


class ActDefaultAskConfirmation(Action):
    """Default implementation which asks the user to affirm his intent.

    It is suggested to overwrite this default action with a custom action
    to have more meaningful prompts for the affirmations. E.g. have a
    description of the intent instead of its identifier name.
    """

    def name(self) -> Text:
        return DEFAULT_ASK_AFFIRMATION_ACTION_NAME   

    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        intent_to_confirm = tracker.latest_message.intent.get(KEY_INTENT_NAME)

        intent_rank = tracker.latest_message.intent.get(KEY_INTENT_RANKING, [])
        if (
            intent_to_confirm == DEFAULT_NLU_FALLBACK_INTENTS_NAME
            and len(intent_rank) > 1
        ):
            intent_to_confirm = intent_rank[1][KEY_INTENT_NAME]

        confirmation_msg = f"Did you mean '{intent_to_confirm}'?"

        msg = {
            "text": confirmation_msg,
            "buttons": [
                {"title": "Yes", "payload": f"/{intent_to_confirm}"},
                {"title": "No", "payload": f"/{USERS_INTENT_OUT_OF_SCOPE  }"},
            ],
            "template_name": self.name(),
        }

        return [generate_bot_utterance(msg)]


class ActDefaultAskRephrase(ActUtterTemplate):
    """Default implementation which asks the user to rephrase his intent."""

    def name(self) -> Text:
        return DEFAULT_ASK_REPHRASE_ACTION_NAME   

    def __init__(self) -> None:
        super().__init__("utter_ask_rephrase", silent_fail=True)
