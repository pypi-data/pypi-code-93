import logging
import os
import time
from types import LambdaType
from typing import Any, Dict, List, Optional, Text, Tuple, Union

import numpy as np

import convo.shared.utils.io
import convo.core.actions.action
from convo.core import jobs
from convo.core.channels.channel import (
    CollectOutputChannel,
    OutputSocket,
    UserMsg,
)
from convo.shared.core.constants import (
    RESTART_USER_INTENT  ,
    LISTEN_ACTION_NAME  ,
    SESSION_START_ACTION_NAME  ,
    REQUESTED_SLOTS,
    CONVO_SLOTS,
)
from convo.shared.core.domain import Domain
from convo.shared.core.events import (
    ActionExecuted,
    ActExecutionRejected,
    BotUttered,
    Event,
    ReminderCancelled,
    ReminderOrganized,
  SetofSlot,
    UserUttered,
)
from convo.shared.nlu.interpreter import NaturalLangInterpreter, RegexInterpreter
from convo.shared.constants import (
    INTENT_MSG_PREFIX ,
    DOMAIN_DOCUMENTS_URL,
    CONVO_DEFAULT_SENDER_ID ,
    POLICIES_DOCUMENTS_URL ,
    CONVO_UTTER_PREFIX ,
)
from convo.core.nlg import NaturalLanguageGenerator
from convo.core.policies.ensemble import EnsemblePolicy
from convo.core.tracker_store import TrackerStorage
from convo.shared.core.trackers import DialogueStateTracer, releaseVerbosity
from convo.shared.nlu.constants import KEY_INTENT_NAME
from convo.utils.endpoints import EndpointConfiguration

log = logging.getLogger(__name__)

MAXIMUM_NO_OF_FORECAST = int(os.environ.get("MAX_NUMBER_OF_PREDICTIONS", "10"))


class MsgProcessor:
    def __init__(
        self,
        interpreter: NaturalLangInterpreter,
        policy_ensemble: EnsemblePolicy,
        domain: Domain,
        tracker_store: TrackerStorage,
        generator: NaturalLanguageGenerator,
        action_endpoint: Optional[EndpointConfiguration] = None,
        max_number_of_predictions: int = MAXIMUM_NO_OF_FORECAST,
        message_preprocessor: Optional[LambdaType] = None,
        on_circuit_break: Optional[LambdaType] = None,
    ):
        self.interpreter = interpreter
        self.nlg = generator
        self.policy_ensemble = policy_ensemble
        self.domain = domain
        self.tracker_store = tracker_store
        self.max_number_of_predictions = max_number_of_predictions
        self.message_preprocessor = message_preprocessor
        self.on_circuit_break = on_circuit_break
        self.action_endpoint = action_endpoint

    async def handle_msg(
        self, msg: UserMsg
    ) -> Optional[List[Dict[Text, Any]]]:
        """Handle a single msg with this processor."""

        # preprocess msg if necessary
        processor_tracker = await self.log_msg(msg, should_save_tracker=False)
        if not processor_tracker:
            return None

        if not self.policy_ensemble or not self.domain:
            # save tracker state to continue conversation from this state
            self._store_tracker(processor_tracker)
            convo.shared.utils.io.raising_warning(
                "No policy ensemble or domain set. Skipping action prediction "
                "and execution.",
                docs=POLICIES_DOCUMENTS_URL ,
            )
            return None

        await self._forecast_and_run_next_act(msg.output_channel, processor_tracker)

        # save tracker state to continue conversation from this state
        self._store_tracker(processor_tracker)

        if isinstance(msg.output_channel, CollectOutputChannel):
            return msg.output_channel.messages
        else:
            return None

    async def forecast_next(self, sender_id: Text) -> Optional[Dict[Text, Any]]:

        # we have a Tracker instance for each user
        # which maintains conversation state
        tracker = await self.fetch_tracker_with_session_start(sender_id)
        if not tracker:
            log.warning(
                f"Failed to retrieve or create tracker for sender '{sender_id}'."
            )
            return None

        if not self.policy_ensemble or not self.domain:
            # save tracker state to continue conversation from this state
            convo.shared.utils.io.raising_warning(
                "No policy ensemble or domain set. Skipping action prediction."
                "You should set a policy before training a model.",
                docs=POLICIES_DOCUMENTS_URL ,
            )
            return None

        chances, processor_policy = self._fetch_next_act_chance(tracker)
        # save tracker state to continue conversation from this state
        self._store_tracker(tracker)
        result = [
            {"action": a, "score": p}
            for a, p in zip(self.domain.action_names, chances)
        ]
        return {
            "scores": result,
            "policy": processor_policy,
            "confidence": np.max(chances),
            "tracker": tracker.current_active_state(releaseVerbosity.AFTER_RESTART),
        }

    async def _upgrade_tracker_session(
        self,
        tracker: DialogueStateTracer,
        output_channel: OutputSocket,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Check the current session in `tracker` and update it if expired.

        An 'action_session_start' is run if the latest tracker session has expired,
        or if the tracker does not yet contain any events (only those after the last
        Restarted are considered).

        Args:
            metadata: Data sent from client associated with the incoming user msg.
            tracker: Tracker to inspect.
            output_channel: Output channel for potential utterances in a custom
                `ActionSessionStart`.
        """
        if not tracker.request_events() or self._is_session_expired(tracker):
            log.debug(
                f"Starting a new session for conversation ID '{tracker.sender_id}'."
            )

            await self._execute_act(
                action=self._fetch_act(SESSION_START_ACTION_NAME),
                tracker=tracker,
                output_channel=output_channel,
                nlg=self.nlg,
                metadata=metadata,
            )

    async def fetch_tracker_with_session_start(
        self,
        sender_id: Text,
        output_channel: Optional[OutputSocket] = None,
        metadata: Optional[Dict] = None,
    ) -> Optional[DialogueStateTracer]:
        """Get tracker for `sender_id` or create a new tracker for `sender_id`.

        If a new tracker is created, `action_session_start` is run.

        Args:
            metadata: Data sent from client associated with the incoming user msg.
            output_channel: Output channel associated with the incoming user msg.
            sender_id: Conversation ID for which to fetch the tracker.

        Returns:
              Tracker for `sender_id` if available, `None` otherwise.
        """

        tracer = self.fetch_tracker(sender_id)
        if not tracer:
            return None

        await self._upgrade_tracker_session(tracer, output_channel, metadata)

        return tracer

    def fetch_tracker(self, communication_id: Text) -> Optional[DialogueStateTracer]:
        """Get the tracker for a conversation.

        In contrast to `get_tracker_with_session_start` this does not add any
        `action_session_start` or `session_start` events at the beginning of a
        conversation.

        Args:
            communication_id: The ID of the conversation for which the history should be
                retrieved.

        Returns:
            Tracker for the conversation. Creates an empty tracker in case it's a new
            conversation.
        """
        communication_id = communication_id or CONVO_DEFAULT_SENDER_ID
        return self.tracker_store.fetch_or_generate_tracker(
            communication_id, append_action_listen=False
        )

    async def log_msg(
        self, msg: UserMsg, should_save_tracker: bool = True
    ) -> Optional[DialogueStateTracer]:
        """Log `msg` on tracker belonging to the msg's conversation_id.

        Optionally save the tracker if `should_save_tracker` is `True`. Tracker saving
        can be skipped if the tracker returned by this method is used for further
        processing and saved at a later stage.
        """

        # we have a Tracker instance for each user
        # which maintains conversation state
        tracer = await self.fetch_tracker_with_session_start(
            msg.sender_id, msg.output_channel, msg.metadata
        )

        if tracer:
            await self._handle_msg_with_tracker(msg, tracer)

            if should_save_tracker:
                # save tracker state to continue conversation from this state
                self._store_tracker(tracer)
        else:
            log.warning(
                f"Failed to retrieve or create tracker for conversation ID "
                f"'{msg.sender_id}'."
            )
        return tracer

    async def perform_action(
        self,
        sender_id: Text,
        action_name: Text,
        output_channel: OutputSocket,
        nlg: NaturalLanguageGenerator,
        policy: Text,
        confidence: float,
    ) -> Optional[DialogueStateTracer]:

        # we have a Tracker instance for each user
        # which maintains conversation state
        tracer = await self.fetch_tracker_with_session_start(sender_id, output_channel)
        if tracer:
            action = self._fetch_act(action_name)
            await self._execute_act(
                action, tracer, output_channel, nlg, policy, confidence
            )

            # save tracker state to continue conversation from this state
            self._store_tracker(tracer)
        else:
            log.warning(
                f"Failed to retrieve or create tracker for conversation ID "
                f"'{sender_id}'."
            )
        return tracer

    def forecast_next_act(
        self, tracker: DialogueStateTracer
    ) -> Tuple[convo.core.actions.action.Action, Optional[Text], float]:
        """Predicts the next action the bot should take after seeing x.

        This should be overwritten by more advanced policies to use
        ML to predict the action. Returns the index of the next action."""

        guidelines, policy = self._fetch_next_act_chance(tracker)

        maximum_confidence_index = int(np.argmax(guidelines))
        act = convo.core.actions.action._act_for_index(
            maximum_confidence_index, self.domain, self.action_endpoint
        )

        log.debug(
            f"Predicted next action '{act.name()}' with confidence "
            f"{guidelines[maximum_confidence_index]:.2f}."
        )

        return act, policy, guidelines[maximum_confidence_index]

    @staticmethod
    def _is_reminder(e: Event, name: Text) -> bool:
        return isinstance(e, ReminderOrganized) and e.name == name

    @staticmethod
    def _is_reminder_valid(
        tracker: DialogueStateTracer, reminder_event: ReminderOrganized
    ) -> bool:
        """Check if the conversation has been restarted after reminder."""

        for e in reversed(tracker.request_events()):
            if MsgProcessor._is_reminder(e, reminder_event.name):
                return True
        return False  # not found in applied events --> has been restarted

    @staticmethod
    def _had_msg_after_reminder(
        tracker: DialogueStateTracer, reminder_event: ReminderOrganized
    ) -> bool:
        """Check if the user sent a msg after the reminder."""

        for e in reversed(tracker.events):
            if MsgProcessor._check_reminder(e, reminder_event.name):
                return False
            elif isinstance(e, UserUttered) and e.text:
                return True
        return True  # tracker has probably been restarted

    async def control_reminder(
        self,
        reminder_event: ReminderOrganized,
        sender_id: Text,
        output_channel: OutputSocket,
    ) -> None:
        """Handle a reminder that is triggered asynchronously."""

        tracer = await self.fetch_tracker_with_session_start(sender_id, output_channel)

        if not tracer:
            log.warning(
                f"Failed to retrieve tracker for conversation ID '{sender_id}'."
            )
            return None

        if (
            reminder_event.kill_on_user_message
            and self._had_msg_after_reminder(tracer, reminder_event)
            or not self._is_reminder_valid(tracer, reminder_event)
        ):
            log.debug(
                f"Canceled reminder because it is outdated ({reminder_event})."
            )
        else:
            intent = reminder_event.intent
            entities = reminder_event.entities or {}
            await self.trigger_external_user_changed(
                intent, entities, tracer, output_channel
            )

    async def trigger_external_user_changed(
        self,
        name_of_intent: Text,
        entities: Optional[Union[List[Dict[Text, Any]], Dict[Text, Text]]],
        tracker: DialogueStateTracer,
        output_channel: OutputSocket,
    ) -> None:
        """Triggers an external msg.

        Triggers an external msg (like a user msg, but invisible;
        used, e.g., by a reminder or the trigger_intent endpoint).

        Args:
            name_of_intent: Name of the intent to be triggered.
            entities: Entities to be passed on.
            tracker: The tracker to which the event should be added.
            output_channel: The output channel.
        """
        if isinstance(entities, list):
            entity_list_name = entities
        elif isinstance(entities, dict):
            # Allow for a short-hand notation {"ent1": "val1", "ent2": "val2", ...}.
            # Useful if properties like 'start', 'end', or 'extractor' are not given,
            # e.g. for external events.
            entity_list_name = [
                {"entity": ent, "value": val} for ent, val in entities.items()
            ]
        elif not entities:
            entity_list_name = []
        else:
            convo.shared.utils.io.raising_warning(
                f"Invalid entity specification: {entities}. Assuming no entities."
            )
            entity_list_name = []

        # Set the new event's input channel to the latest input channel, so
        # that we don't lose this property.
        input_channel_received = tracker.get_input_channel_latest()

        tracker.update(
            UserUttered.create_external_event(name_of_intent, entity_list_name, input_channel_received)
        )
        await self._forecast_and_run_next_act(output_channel, tracker)
        # save tracker state to continue conversation from this state
        self._store_tracker(tracker)

    @staticmethod
    def _fetch_log_slot(tracker) -> None:
        # Log currently set slots
        slot_value = "\n".join(
            [f"\t{s.name}: {s.value}" for s in tracker.slots.values()]
        )
        if slot_value.strip():
            log.debug(f"Current slot values: \n{slot_value}")

    def _check_for_not_existing_features(self, parse_data: Dict[Text, Any]) -> None:
        """Warns the user if the NLU parse data contains unrecognized features.

        Checks convo_intents and entities picked up by the NLU interpreter
        against the domain and warns the user of those that don't match.
        Also considers a list of default convo_intents that are valid but don't
        need to be listed in the domain.

        Args:
            parse_data: NLUInterpreter parse data to check against the domain.
        """
        if not self.domain or self.domain.is_empty():
            return

        intention = parse_data["intent"][KEY_INTENT_NAME]
        if intention and intention not in self.domain.fetch_intents:
            convo.shared.utils.io.raising_warning(
                f"Interpreter parsed an intent '{intention}' "
                f"which is not defined in the domain. "
                f"Please make sure all intents are listed in the domain.",
                docs=DOMAIN_DOCUMENTS_URL,
            )

        processor_entities = parse_data["entities"] or []
        for element in processor_entities:
            entity = element["entity"]
            if entity and entity not in self.domain.entities:
                convo.shared.utils.io.raising_warning(
                    f"Interpreter parsed an entity '{entity}' "
                    f"which is not defined in the domain. "
                    f"Please make sure all entities are listed in the domain.",
                    docs=DOMAIN_DOCUMENTS_URL,
                )

    def _fetch_act(self, action_name) -> Optional[convo.core.actions.action.Action]:
        return convo.core.actions.action.act_for_name(
            action_name, self.domain, self.action_endpoint
        )

    async def parse_msg(
        self, msg: UserMsg, tracker: Optional[DialogueStateTracer] = None
    ) -> Dict[Text, Any]:
        """Interprete the passed msg using the NLU interpreter.

        Arguments:
            msg: Msg to handle
            tracker: Dialogue context of the msg

        Returns:
            Parsed data extracted from the msg.
        """
        # preprocess msg if necessary
        if self.message_preprocessor is not None:
            txt = self.message_preprocessor(msg.text)
        else:
            txt = msg.text

        # for testing - you can short-cut the NLU part with a msg
        # in the format /intent{"entity1": val1, "entity2": val2}
        # parse_data is a dict of intent & entities
        if txt.startswith(INTENT_MSG_PREFIX ):
            parse_data_set = await RegexInterpreter().parse(
                txt, msg.message_id, tracker
            )
        else:
            parse_data_set = await self.interpreter.parse(
                txt, msg.message_id, tracker, metadata=msg.metadata
            )

        log.debug(
            "Received user msg '{}' with intent '{}' "
            "and entities '{}'".format(
                msg.text, parse_data_set["intent"], parse_data_set["entities"]
            )
        )

        self._check_for_not_existing_features(parse_data_set)

        return parse_data_set

    async def _handle_msg_with_tracker(
        self, msg: UserMsg, tracker: DialogueStateTracer
    ) -> None:

        if msg.parse_data:
            parse_data = msg.parse_data
        else:
            parse_data = await self.parse_msg(msg, tracker)

        # don't ever directly mutate the tracker
        # - instead pass its events to log
        tracker.update(
            UserUttered(
                msg.text,
                parse_data["intent"],
                parse_data["entities"],
                parse_data,
                input_channel=msg.input_channel,
                message_id=msg.message_id,
                metadata=msg.metadata,
            ),
            self.domain,
        )

        if parse_data["entities"]:
            self._fetch_log_slot(tracker)

        log.debug(
            f"Logged UserUtterance - tracker now has {len(tracker.events)} events."
        )

    @staticmethod
    def _should_handle_msg(tracker: DialogueStateTracer):
        return (
            not tracker.pause_check()
            or tracker.latest_message.intent.get(KEY_INTENT_NAME) == RESTART_USER_INTENT  
        )

    def is_act_limit_reached(
        self, num_predicted_actions: int, should_predict_another_action: bool
    ) -> bool:
        """Check whether the maximum number of predictions has been met.

        Args:
            num_predicted_actions: Number of predicted actions.
            should_predict_another_action: Whether the last executed action allows
            for more actions to be predicted or not.

        Returns:
            `True` if the limit of actions to predict has been reached.
        """
        return (
            num_predicted_actions >= self.max_number_of_predictions
            and should_predict_another_action
        )

    async def _forecast_and_run_next_act(
        self, output_channel: OutputSocket, tracker: DialogueStateTracer
    ):
        # keep taking actions decided by the policy until it chooses to 'listen'
        shall_forecast_another_act = True
        num_forecast_act = 0

        # action loop. predicts actions until we hit action listen
        while (
            shall_forecast_another_act
            and self._should_handle_msg(tracker)
            and num_forecast_act < self.max_number_of_predictions
        ):
            # this actually just calls the policy's method by the same name
            act, guideline, confidence = self.forecast_next_act(tracker)

            shall_forecast_another_act = await self._execute_act(
                act, tracker, output_channel, self.nlg, guideline, confidence
            )
            num_forecast_act += 1

        if self.is_act_limit_reached(
            num_forecast_act, shall_forecast_another_act
        ):
            # circuit breaker was tripped
            log.warning(
                "Circuit breaker tripped. Stopped predicting "
                f"more actions for sender '{tracker.sender_id}'."
            )
            if self.on_circuit_break:
                # call a registered callback
                self.on_circuit_break(tracker, output_channel, self.nlg)

    @staticmethod
    def should_forecast_another_act(action_name: Text) -> bool:
        """Determine whether the processor should predict another action.

        Args:
            action_name: Name of the latest executed action.

        Returns:
            `False` if `action_name` is `LISTEN_ACTION_NAME  ` or
            `SESSION_START_ACTION_NAME  `, otherwise `True`.
        """

        return action_name not in (LISTEN_ACTION_NAME  , SESSION_START_ACTION_NAME  )

    async def run_side_effects(
        self,
        events: List[Event],
        tracker: DialogueStateTracer,
        output_channel: OutputSocket,
    ) -> None:
        """Send bot messages, schedule and cancel reminders that are logged
        in the events array."""

        await self._send_bot_messages(events, tracker, output_channel)
        await self._send_bot_msg(events, tracker, output_channel)
        await self._abort_reminders(events, tracker)

    @staticmethod
    async def _send_bot_messages(
        events: List[Event],
        tracker: DialogueStateTracer,
        output_channel: OutputSocket,
    ) -> None:
        """Send all the bot messages that are logged in the events array."""

        for e in events:
            if not isinstance(e, BotUttered):
                continue

            await output_channel.send_response(tracker.sender_id, e.msg())

    async def _send_bot_msg(
        self,
        events: List[Event],
        tracker: DialogueStateTracer,
        output_channel: OutputSocket,
    ) -> None:
        """Uses the scheduler to time a job to trigger the passed reminder.

        Reminders with the same `id` property will overwrite one another
        (i.e. only one of them will eventually run)."""

        for e in events:
            if not isinstance(e, ReminderOrganized):
                continue

            (await jobs.schedule_jobs()).add_job(
                self.control_reminder,
                "date",
                run_date=e.trigger_date_time,
                args=[e, tracker.sender_id, output_channel],
                id=e.name,
                replace_existing=True,
                name=e.cron_job_name(tracker.sender_id),
            )

    @staticmethod
    async def _abort_reminders(
        events: List[Event], tracker: DialogueStateTracer
    ) -> None:
        """Cancel reminders that match the `ReminderCancelled` event."""

        # All Reminders specified by ReminderCancelled events will be cancelled
        for event in events:
            if isinstance(event, ReminderCancelled):
                scheduler = await jobs.schedule_jobs()
                for scheduled_job in scheduler.get_jobs():
                    if event.name_of_cancelling_job(
                        scheduled_job.name, tracker.sender_id
                    ):
                        scheduler.remove_job(scheduled_job.id)

    async def _execute_act(
        self,
        action,
        tracker,
        output_channel,
        nlg,
        policy=None,
        confidence=None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> bool:
        # events and return values are used to update
        # the tracker state after an action has been taken
        try:
            # Here we set optional metadata to the ActionSessionStart, which will then
            # be passed to the SessionStart event. Otherwise the metadata will be lost.
            if action.name() == SESSION_START_ACTION_NAME  :
                action.metadata = metadata
            events = await action.run(output_channel, nlg, tracker, self.domain)
        except convo.core.actions.action.ActExecutionRejection:
            events = [ActExecutionRejected(action.name(), policy, confidence)]
            tracker.update(events[0])
            return self.should_forecast_another_act(action.name())
        except Exception:
            log.exception(
                f"Encountered an exception while running action '{action.name()}'."
                "Bot will continue, but the actions events are lost. "
                "Please check the logs of your action server for "
                "more information."
            )
            events = []

        self._log_act_on_tracker(tracker, action.name(), events, policy, confidence)
        if action.name() != LISTEN_ACTION_NAME and not action.name().startswith(
            CONVO_UTTER_PREFIX 
        ):
            self._fetch_log_slot(tracker)

        await self.run_side_effects(events, tracker, output_channel)

        return self.should_forecast_another_act(action.name())

    def _warning_about_new_slots(self, tracker, action_name, events) -> None:
        # these are the events from that action we have seen during training

        if (
            not self.policy_ensemble
            or action_name not in self.policy_ensemble.action_fingerprints
        ):
            return

        fp = self.policy_ensemble.action_fingerprints[action_name]
        slots_seen_in_train = fp.get(CONVO_SLOTS, set())
        for e in events:
            if isinstance(e, SetofSlot) and e.key not in slots_seen_in_train:
                t = tracker.slots.get(e.key)
                if t and t.features_check():
                    if e.key == REQUESTED_SLOTS and tracker.active_loop:
                        pass
                    else:
                        convo.shared.utils.io.raising_warning(
                            f"Action '{action_name}' set a slot type '{e.key}' which "
                            f"it never set during the training. This "
                            f"can throw off the prediction. Make sure to "
                            f"include training examples in your stories "
                            f"for the different types of convo_slotsthis "
                            f"action can return. Remember: you need to "
                            f"set the convo_slotsmanually in the stories by "
                            f"adding '- slot{{\"{e.key}\": {e.value}}}' "
                            f"after the action."
                        )

    def _log_act_on_tracker(
        self, tracker, action_name, events, policy, confidence
    ) -> None:
        # Ensures that the code still works even if a lazy programmer missed
        # to type `return []` at the end of an action or the run method
        # returns `None` for some others reason.
        if events is None:
            events = []

        log.debug(
            f"Action '{action_name}' ended with events '{[e for e in events]}'."
        )

        self._warning_about_new_slots(tracker, action_name, events)

        if action_name is not None:
            # log the action and its produced events
            tracker.update(ActionExecuted(action_name, policy, confidence))

        for e in events:
            # this makes sure the events are ordered by timestamp -
            # since the event objects are created somewhere else,
            # the timestamp would indicate a time before the time
            # of the action executed
            e.timestamp = time.time()
            tracker.update(e, self.domain)

    def _is_session_expired(self, tracker: DialogueStateTracer) -> bool:
        """Determine whether the latest session in `tracker` has expired.

        Args:
            tracker: Tracker to inspect.

        Returns:
            `True` if the session in `tracker` has expired, `False` otherwise.
        """

        if not self.domain.session_configuration.sessions_enabled():
            # tracker has never expired if sessions are disabled
            return False

        user_uttered_event: Optional[UserUttered] = tracker.get_last_event_for(
            UserUttered
        )

        if not user_uttered_event:
            # there is no user event so far so the session should not be considered
            # expired
            return False

        time_delta_in_sec = time.time() - user_uttered_event.timestamp
        had_over = (
            time_delta_in_sec / 60
            > self.domain.session_configuration.session_expiration_time
        )
        if had_over:
            log.debug(
                f"The latest session for conversation ID '{tracker.sender_id}' has "
                f"expired."
            )

        return had_over

    def _store_tracker(self, tracker: DialogueStateTracer) -> None:
        self.tracker_store.save(tracker)

    def _prob_array_for_act(self, action_name: Text) -> Tuple[List[float], None]:
        idx = self.domain.actions_index(action_name)
        if idx is not None:
            output = [0.0] * self.domain.number_of_actions
            output[idx] = 1.0
            return output, None
        else:
            return [], None

    def _fetch_next_act_chance(
        self, tracker: DialogueStateTracer
    ) -> Tuple[List[float], Optional[Text]]:
        """Collect predictions from ensemble and return action and predictions."""

        follow_up_act = tracker.followup_action
        if follow_up_act:
            tracker.clear_follow_up_action()
            result = self._prob_array_for_act(follow_up_act)
            if result:
                return result
            else:
                log.error(
                    f"Trying to run unknown follow-up action '{follow_up_act}'!"
                    "Instead of running that, we will ignore the action "
                    "and predict the next action."
                )

        return self.policy_ensemble.probability_using_finest_policy(
            tracker, self.domain, self.interpreter
        )
