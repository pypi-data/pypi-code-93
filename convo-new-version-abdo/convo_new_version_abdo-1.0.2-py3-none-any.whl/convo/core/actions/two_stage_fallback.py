import copy
import time
from typing import List, Text, Optional

from convo.core.actions import action
from convo.core.actions.loops import LoopAct
from convo.core.channels import OutputSocket
from convo.shared.core.domain import Domain
from convo.shared.core.events import (
    Event,
    UserChangeReverted,
    ActionExecuted,
    UserUttered,
    OperationalLoop,
)
from convo.core.nlg import NaturalLanguageGenerator
from convo.shared.core.trackers import DialogueStateTracer, releaseVerbosity
from convo.shared.constants import DEFAULT_NLU_FALLBACK_INTENTS_NAME
from convo.shared.core.constants import (
    USERS_INTENT_OUT_OF_SCOPE  ,
    LISTEN_ACTION_NAME  ,
    ACTION_DEFAULT_FALLBACK_NAME,
    DEFAULT_ASK_AFFIRMATION_ACTION_NAME   ,
    DEFAULT_ASK_REPHRASE_ACTION_NAME   ,
    TWO_STAGE_FALLBACK_ACTION_NAME   ,
)
from convo.utils.endpoints import EndpointConfiguration


class DoubleStageFallbackAction(LoopAct):
    def __init__(self, action_endpoint: Optional[EndpointConfiguration] = None) -> None:
        self._action_endpoint = action_endpoint

    def name(self) -> Text:
        return TWO_STAGE_FALLBACK_ACTION_NAME   

    async def do(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
        events_so_far: List[Event],
    ) -> List[Event]:
        if _user_shall_confirm(tracker, events_so_far):
            return await self._ask_confirmation(output_channel, nlg, tracker, domain)

        return await self._ask_for_rephrase(output_channel, nlg, tracker, domain)

    async def _ask_confirmation(
        self,
        output_channel: OutputSocket,
        nlg: NaturalLanguageGenerator,
        tracker: DialogueStateTracer,
        domain: Domain,
    ) -> List[Event]:
        confirm_action = action.act_from_name(
            DEFAULT_ASK_AFFIRMATION_ACTION_NAME,
            self._action_endpoint,
            domain.user_actions,
        )

        return await confirm_action.execute(output_channel, nlg, tracker, domain)

    async def _ask_for_rephrase(
        self,
        output_channel: OutputSocket,
        nlg: NaturalLanguageGenerator,
        tracker: DialogueStateTracer,
        domain: Domain,
    ) -> List[Event]:
        recaste = action.act_from_name(
            DEFAULT_ASK_REPHRASE_ACTION_NAME, self._action_endpoint, domain.user_actions
        )

        return await recaste.execute(output_channel, nlg, tracker, domain)

    async def is_completed(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
        events_so_far: List[Event],
    ) -> bool:
        _user_clarification = _rearmost_intent_name(tracker) not in [
            DEFAULT_NLU_FALLBACK_INTENTS_NAME,
            USERS_INTENT_OUT_OF_SCOPE,
        ]
        return (
                _user_clarification
                or _two_fallbacks_in_single_row(tracker)
                or _second_confirmation_failed(tracker)
        )

    async def deactivate(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
        events_so_far: List[Event],
    ) -> List[Event]:
        if _two_fallbacks_in_single_row(tracker) or _second_confirmation_failed(tracker):
            return await self._give_up(output_channel, nlg, tracker, domain)

        return await self._return_fallback_event(
            output_channel, nlg, tracker, domain, events_so_far
        ) + _msg_clarification(tracker)

    async def _return_fallback_event(
        self,
        output_channel: OutputSocket,
        nlg: NaturalLanguageGenerator,
        tracker: DialogueStateTracer,
        domain: Domain,
        events_so_far: List[Event],
    ) -> List[Event]:
        return_events = [UserChangeReverted(), UserChangeReverted()]

        temporary_tracker = DialogueStateTracer.from_events_tracker(
            tracker.sender_id, tracker.request_events() + events_so_far + return_events
        )

        while temporary_tracker.latest_message and not await self.is_completed(
            output_channel, nlg, temporary_tracker, domain, []
        ):
            temporary_tracker.update(return_events[-1])
            return_events.append(UserChangeReverted())

        return return_events

    async def _give_up(
        self,
        output_channel: OutputSocket,
        nlg: NaturalLanguageGenerator,
        tracker: DialogueStateTracer,
        domain: Domain,
    ) -> List[Event]:
        fallback = action.act_from_name(
            ACTION_DEFAULT_FALLBACK_NAME, self._action_endpoint, domain.user_actions
        )

        return await fallback.execute(output_channel, nlg, tracker, domain)


def _rearmost_intent_name(tracker: DialogueStateTracer) -> Optional[Text]:
    last_msg = tracker.latest_message
    if not last_msg:
        return None

    return last_msg.intent.get("name")


def _two_fallbacks_in_single_row(tracker: DialogueStateTracer) -> bool:
    return __n_intent_names(tracker, 2) == [
        DEFAULT_NLU_FALLBACK_INTENTS_NAME,
        DEFAULT_NLU_FALLBACK_INTENTS_NAME,
    ]


def __n_intent_names(
    tracker: DialogueStateTracer, number_of_last_intent_names: int
) -> List[Text]:
    intent_name = []
    for i in range(number_of_last_intent_names):
        message = tracker.get_last_event_for(
            UserUttered, skip=i, event_verbosity=releaseVerbosity.AFTER_RESTART
        )
        if isinstance(message, UserUttered):
            intent_name.append(message.intent.get("name"))

    return intent_name


def _user_shall_confirm(
    tracker: DialogueStateTracer, events_so_far: List[Event]
) -> bool:
    fallback_has_just_begin = any(
        isinstance(event, OperationalLoop) for event in events_so_far
    )
    if fallback_has_just_begin:
        return True

    return _rearmost_intent_name(tracker) == DEFAULT_NLU_FALLBACK_INTENTS_NAME


def _second_confirmation_failed(tracker: DialogueStateTracer) -> bool:
    return __n_intent_names(tracker, 3) == [
        USERS_INTENT_OUT_OF_SCOPE,
        DEFAULT_NLU_FALLBACK_INTENTS_NAME,
        USERS_INTENT_OUT_OF_SCOPE,
    ]


def _msg_clarification(tracker: DialogueStateTracer) -> List[Event]:
    explanation = copy.deepcopy(tracker.latest_message)
    explanation.parse_data["intent"]["confidence"] = 1.0
    explanation.timestamp = time.time()
    return [ActionExecuted(LISTEN_ACTION_NAME), explanation]
