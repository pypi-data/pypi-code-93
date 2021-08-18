import json
import logging
import re

import jsonpickle
import time
import typing
import uuid
from dateutil import parser
from datetime import datetime
from typing import List, Dict, Text, Any, Type, Optional

import convo.shared.utils.common
from typing import Union

from convo.shared.core.constants import (
    LOOPNAME  ,
    EXT_MSG_PREFIX,
    SENDER_ID_CONNECTOR_STR_ACTION_NAME,
    EXTERNAL_CHECK,
    LOOP_INTERRUPTION   ,
)
from convo.shared.nlu.constants import (
    ATTRIBUTE_TYPE_ENTITY,
    INTENTION,
    TXT,
    ENTITIES_NAME,
    ATTRIBUTE_VALUE_ENTITY,
    ACT_TEXT,
    ACT_NAME,
    KEY_INTENT_NAME,
)

if typing.TYPE_CHECKING:
    from convo.shared.core.trackers import DialogueStateTracer

log = logging.getLogger(__name__)


def deserialized_events(serialized_events: List[Dict[Text, Any]]) -> List["Event"]:
    """Convert a list of dictionaries to a list of corresponding events.

    Example format:
        [{"event": "slot", "value": 5, "name": "my_slot"}]
    """

    deserialized = []

    for e in serialized_events:
        if "event" in e:
            event = Event.from_params(e)
            if event:
                deserialized.append(event)
            else:
                log.warning(
                    f"Unable to parse event '{event}' while deserialising. The event"
                    " will be ignored."
                )

    return deserialized


def deserialize_entities(entities: Union[Text, List[Any]]) -> List[Dict[Text, Any]]:
    if isinstance(entities, str):
        entities = json.loads(entities)

    return [e for e in entities if isinstance(e, dict)]


def md_format_msg(
    text: Text, intent: Optional[Text], entities: Union[Text, List[Any]]
) -> Text:
    """Uses NLU parser information to generate a message with inline entity annotations.

    Arguments:
        text: text of the message
        intent: intent of the message
        entities: entities of the message

    Return:
        Msg with entities annotated inline, e.g.
        `I am from [Berlin]{"entity": "city"}`.
    """
    from convo.shared.nlu.training_data.formats.readerwriter import TrainingDataAuthor
    from convo.shared.nlu.training_data import entities_parser

    message_from_md = entities_parser.parsing_training_example(text, intent)
    deserialized_entities = deserialize_entities(entities)
    return TrainingDataAuthor.generate_msg(
        {"text": message_from_md.get(TXT), "entities": deserialized_entities}
    )


def primary_key(d: Dict[Text, Any], default_key: Any) -> Any:
    if len(d) > 1:
        for k in d.keys():
            if k != default_key:
                # we return the first key that is not the default key
                return k
    elif len(d) == 1:
        return list(d.keys())[0]
    else:
        return None


# noinspection PyProtectedMember
class Event:
    """Events describe everything that occurs in
    a conversation and tell the :class:`convo.shared.core.trackers.DialogueStateTracer`
    how to update its state."""

    type_name = "event"

    def __init__(
        self,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        self.timestamp = timestamp or time.time()
        self._metadata = metadata or {}

    @property
    def metadata(self) -> Dict[Text, Any]:
        # Needed for compatibility with Convo versions <1.4.0. Previous versions
        # of Convo serialized trackers using the pickle module. For the moment,
        # Convo still supports loading these serialized trackers with pickle,
        # but will use JSON in any subsequent save operations. Versions of
        # trackers serialized with pickle won't include the `_metadata`
        # attribute in their events, so it is necessary to define this getter
        # in case the attribute does not exist. For more information see
        # CHANGELOG.rst.
        return getattr(self, "_metadata", {})

    def __ne__(self, others: Any) -> bool:
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == others)

    def as_story_string(self) -> Optional[Text]:
        raise NotImplementedError

    @staticmethod
    def from_story_str(
        event_name: Text,
        parameters: Dict[Text, Any],
        default: Optional[Type["Event"]] = None,
    ) -> Optional[List["Event"]]:
        event_var = Event.resolved_by_type(event_name, default)

        if not event_var:
            return None

        return event_var._from_story_str(parameters)

    @staticmethod
    def from_params(
        parameters: Dict[Text, Any], default: Optional[Type["Event"]] = None
    ) -> Optional["Event"]:

        fetch_event_name = parameters.get("event")
        if fetch_event_name is None:
            return None

        event_class: Optional[Type[Event]] = Event.resolved_by_type(fetch_event_name, default)
        if not event_class:
            return None

        return event_class._from_params(parameters)

    @classmethod
    def _from_story_str(cls, parameters: Dict[Text, Any]) -> Optional[List["Event"]]:
        """Called to convert a parsed story line into an event."""
        return [cls(parameters.get("timestamp"), parameters.get("metadata"))]

    def as_dictionary(self) -> Dict[Text, Any]:
        e = {"event": self.type_name, "timestamp": self.timestamp}

        if self.metadata:
            e["metadata"] = self.metadata

        return e

    @classmethod
    def _from_params(cls, parameters: Dict[Text, Any]) -> Optional["Event"]:
        """Called to convert a dictionary of parameters to a single event.

        By default uses the same implementation as the story line
        conversation ``_from_story_string``. But the subclass might
        decide to handle parameters differently if the parsed parameters
        don't origin from a story file."""

        results = cls._from_story_str(parameters)
        if len(results) > 1:
            log.warning(
                f"Event from parameters called with parameters "
                f"for multiple events. This is not supported, "
                f"only the first event will be returned. "
                f"Parameters: {parameters}"
            )
        return results[0] if results else None

    @staticmethod
    def resolved_by_type(
        type_name: Text, default: Optional[Type["Event"]] = None
    ) -> Optional[Type["Event"]]:
        """Returns a convo_slotsclass by its type name."""

        for cls in convo.shared.utils.common.all_sub_classes(Event):
            if cls.type_name == type_name:
                return cls
        if type_name == "topic":
            return None  # backwards compatibility to support old TopicSet evts
        elif default is not None:
            return default
        else:
            raise ValueError(f"Unknown event name '{type_name}'.")

    def apply(self, tracker: "DialogueStateTracer") -> None:
        pass


# noinspection PyProtectedMember
class UserUttered(Event):
    """The user has said something to the bot.

    As a side effect a new ``Turn`` will be created in the ``Tracker``."""

    type_name = "user"

    def __init__(
        self,
        text: Optional[Text] = None,
        intent: Optional[Dict] = None,
        entities: Optional[List[Dict]] = None,
        parse_data: Optional[Dict[Text, Any]] = None,
        timestamp: Optional[float] = None,
        input_channel: Optional[Text] = None,
        message_id: Optional[Text] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        self.text = text
        self.intent = intent if intent else {}
        self.entities = entities if entities else []
        self.input_channel = input_channel
        self.message_id = message_id

        super().__init__(timestamp, metadata)

        self.parse_data = {
            "intent": self.intent,
            "entities": self.entities,
            "text": text,
            "message_id": self.message_id,
            "metadata": self.metadata,
        }

        if parse_data:
            self.parse_data.update(**parse_data)

    @staticmethod
    def from_parse_data(
        text: Text,
        parse_data: Dict[Text, Any],
        timestamp: Optional[float] = None,
        input_channel: Optional[Text] = None,
        message_id: Optional[Text] = None,
        metadata: Optional[Dict] = None,
    ):
        return UserUttered(
            text,
            parse_data.get("intent"),
            parse_data.get("entities", []),
            parse_data,
            timestamp,
            input_channel,
            message_id,
            metadata,
        )

    def __hash__(self) -> int:
        return hash((self.text, self.name_of_intent, jsonpickle.encode(self.entities)))

    @property
    def name_of_intent(self) -> Optional[Text]:
        return self.intent.get(KEY_INTENT_NAME)

    def __eq__(self, others: Any) -> bool:
        if not isinstance(others, UserUttered):
            return False
        else:
            return (
                self.text,
                self.name_of_intent,
                [jsonpickle.encode(ent) for ent in self.entities],
            ) == (
                others.text,
                others.name_of_intent,
                [jsonpickle.encode(ent) for ent in others.entities],
            )

    def __str__(self) -> Text:
        return (
            f"UserUttered(text: {self.text}, intent: {self.intent}, "
            f"entities: {self.entities})"
        )

    @staticmethod
    def empty() -> "UserUttered":
        return UserUttered(None)

    def is_empty_check(self) -> bool:
        return not self.text and not self.name_of_intent and not self.entities

    def as_dictionary(self) -> Dict[Text, Any]:
        _dictionary = super().as_dictionary()
        _dictionary.update(
            {
                "text": self.text,
                "parse_data": self.parse_data,
                "input_channel": getattr(self, "input_channel", None),
                "message_id": getattr(self, "message_id", None),
                "metadata": self.metadata,
            }
        )
        return _dictionary

    def as_substate(self) -> Dict[Text, Union[None, Text, List[Optional[Text]]]]:
        """Turns a UserUttered event into a substate containing information about entities,
        intent and text of the UserUttered
        Returns:
            a dictionary with intent name, text and entities
        """
        entities = [entity.get(ATTRIBUTE_TYPE_ENTITY) for entity in self.entities]
        out = {}
        # During training we expect either name_of_intent or text to be set.
        # During prediction both will be set.
        if self.name_of_intent:
            out[INTENTION] = self.name_of_intent
        if self.text:
            out[TXT] = self.text
        if entities:
            out[ENTITIES_NAME] = entities

        return out

    @classmethod
    def _from_story_str(cls, parameters: Dict[Text, Any]) -> Optional[List[Event]]:
        try:
            return [
                cls.from_parse_data(
                    parameters.get("text"),
                    parameters.get("parse_data"),
                    parameters.get("timestamp"),
                    parameters.get("input_channel"),
                    parameters.get("message_id"),
                    parameters.get("metadata"),
                )
            ]
        except KeyError as e:
            raise ValueError(f"Failed to parse bot uttered event. {e}")

    def as_story_string(self, e2e: bool = False) -> Text:
        # TODO figure out how to print if TED chose to use text,
        #  during prediction there will be always intent
        if self.intent:
            if self.entities:
                ent_str = json.dumps(
                    {
                        entity[ATTRIBUTE_TYPE_ENTITY]: entity[ATTRIBUTE_VALUE_ENTITY]
                        for entity in self.entities
                    },
                    ensure_ascii=False,
                )
            else:
                ent_str = ""

            parse_str = "{intent}{entities}".format(
                intent=self.intent.get(KEY_INTENT_NAME, ""), entities=ent_str
            )
            if e2e:
                msg = md_format_msg(
                    self.text, self.intent.get(KEY_INTENT_NAME), self.entities
                )
                return "{}: {}".format(self.intent.get(KEY_INTENT_NAME), msg)
            else:
                return parse_str
        else:
            return self.text

    def apply(self, tracker: "DialogueStateTracer") -> None:
        tracker.latest_message = self
        tracker.clear_follow_up_action()

    @staticmethod
    def create_external_event(
        name_of_intent: Text,
        entity_list: Optional[List[Dict[Text, Any]]] = None,
        input_channel: Optional[Text] = None,
    ) -> "UserUttered":
        return UserUttered(
            text=f"{EXT_MSG_PREFIX}{name_of_intent}",
            intent={KEY_INTENT_NAME: name_of_intent},
            metadata={EXTERNAL_CHECK: True},
            entities=entity_list or [],
            input_channel=input_channel,
        )


# noinspection PyProtectedMember
class BotUttered(Event):
    """The bot has said something to the user.

    This class is not used in the story training as it is contained in the

    ``ActionExecuted`` class. An entry is made in the ``Tracker``."""

    type_name = "bot"

    def __init__(self, text=None, data=None, metadata=None, timestamp=None) -> None:
        self.text = text
        self.data = data or {}
        super().__init__(timestamp, metadata)

    def members(self):
        data_with_no_nones = {k: v for k, v in self.data.items() if v is not None}
        meta_with_no_nones = {k: v for k, v in self.metadata.items() if v is not None}
        return (
            self.text,
            jsonpickle.encode(data_with_no_nones),
            jsonpickle.encode(meta_with_no_nones),
        )

    def __hash__(self) -> int:
        return hash(self.members())

    def __eq__(self, others) -> bool:
        if not isinstance(others, BotUttered):
            return False
        else:
            return self.members() == others.members()

    def __str__(self) -> Text:
        return "BotUttered(text: {}, data: {}, metadata: {})".format(
            self.text, json.dumps(self.data), json.dumps(self.metadata)
        )

    def __repr__(self) -> Text:
        return "BotUttered('{}', {}, {}, {})".format(
            self.text, json.dumps(self.data), json.dumps(self.metadata), self.timestamp
        )

    def apply(self, tracker: "DialogueStateTracer") -> None:

        tracker.latest_bot_utterance = self

    def as_story_string(self) -> None:
        return None

    def msg(self) -> Dict[Text, Any]:
        """Return the complete message as a dictionary."""

        m = self.data.copy()
        m["text"] = self.text
        m["timestamp"] = self.timestamp
        m.update(self.metadata)

        if m.get("image") == m.get("attachment"):
            # we need this as there is an oddity we introduced a while ago where
            # we automatically set the attachment to the image. to not break
            # any persisted events we kept that, but we need to make sure that
            # the message contains the image only once
            m["attachment"] = None

        return m

    @staticmethod
    def empty() -> "BotUttered":
        return BotUttered()

    def as_dictionary(self) -> Dict[Text, Any]:
        e = super().as_dictionary()
        e.update({"text": self.text, "data": self.data, "metadata": self.metadata})
        return e

    @classmethod
    def _from_params(cls, parameters) -> "BotUttered":
        try:
            return BotUttered(
                parameters.get("text"),
                parameters.get("data"),
                parameters.get("metadata"),
                parameters.get("timestamp"),
            )
        except KeyError as e:
            raise ValueError(f"Failed to parse bot uttered event. {e}")


# noinspection PyProtectedMember
class SetofSlot(Event):
    """The user has specified their preference for the value of a ``slot``.

    Every slot has a name and a value. This event can be used to set a
    value for a slot on a conversation.

    As a side effect the ``Tracker``'s convo_slotswill be updated so
    that ``tracker.slots[key]=value``."""

    type_name = "slot"

    def __init__(
        self,
        key: Text,
        value: Optional[Any] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        self.key = key
        self.value = value
        super().__init__(timestamp, metadata)

    def __str__(self) -> Text:
        return f"SetofSlot(key: {self.key}, value: {self.value})"

    def __hash__(self) -> int:
        return hash((self.key, jsonpickle.encode(self.value)))

    def __eq__(self, others) -> bool:
        if not isinstance(others, SetofSlot):
            return False
        else:
            return (self.key, self.value) == (others.key, others.value)

    def as_story_string(self) -> Text:
        props = json.dumps({self.key: self.value}, ensure_ascii=False)
        return f"{self.type_name}{props}"

    @classmethod
    def _from_story_str(cls, parameters: Dict[Text, Any]) -> Optional[List[Event]]:

        slot= []
        for slot_key, slot_val in parameters.items():
            slot.append(SetofSlot(slot_key, slot_val))

        if slot:
            return slot
        else:
            return None

    def as_dictionary(self) -> Dict[Text, Any]:
        d = super().as_dictionary()
        d.update({"name": self.key, "value": self.value})
        return d

    @classmethod
    def _from_params(cls, parameters) -> "SetofSlot":
        try:
            return SetofSlot(
                parameters.get("name"),
                parameters.get("value"),
                parameters.get("timestamp"),
                parameters.get("metadata"),
            )
        except KeyError as e:
            raise ValueError(f"Failed to parse set slot event. {e}")

    def apply(self, tracker: "DialogueStateTracer") -> None:
        tracker.set_slot(self.key, self.value)


# noinspection PyProtectedMember
class Restarted(Event):
    """Conversation should start over & history wiped.

    Instead of deleting all events, this event can be used to reset the
    trackers state (e.g. ignoring any past user messages & resetting all
    the slots)."""

    type_name = "restart"

    def __hash__(self) -> int:
        return hash(32143124312)

    def __eq__(self, others) -> bool:
        return isinstance(others, Restarted)

    def __str__(self) -> Text:
        return "Restarted()"

    def as_story_string(self) -> Text:
        return self.type_name

    def apply(self, tracker: "DialogueStateTracer") -> None:
        from convo.shared.core.constants import LISTEN_ACTION_NAME  

        tracker._reset()
        tracker.trigger_follow_up_action(LISTEN_ACTION_NAME)


# noinspection PyProtectedMember
class UserChangeReverted(Event):
    """Bot reverts everything until before the most recent user message.

    The bot will revert all events after the latest `UserUttered`, this
    also means that the last event on the tracker is usually `action_listen`
    and the bot is waiting for a new user message."""

    type_name = "rewind"

    def __hash__(self) -> int:
        return hash(32143124315)

    def __eq__(self, others) -> bool:
        return isinstance(others, UserChangeReverted)

    def __str__(self) -> Text:
        return "UserChangeReverted()"

    def as_story_string(self) -> Text:
        return self.type_name

    def apply(self, tracker: "DialogueStateTracer") -> None:
        tracker._reset()
        tracker.events_replay()


# noinspection PyProtectedMember
class AllSlotsReset(Event):
    """All Slots are reset to their initial values.

    If you want to keep the dialogue history and only want to reset the
    slots, you can use this event to set all the convo_slotsto their initial
    values."""

    type_name = "reset_slots"

    def __hash__(self) -> int:
        return hash(32143124316)

    def __eq__(self, others) -> bool:
        return isinstance(others, AllSlotsReset)

    def __str__(self) -> Text:
        return "AllSlotsReset()"

    def as_story_string(self) -> Text:
        return self.type_name

    def apply(self, tracker) -> None:
        tracker.reset_slots()


# noinspection PyProtectedMember
class ReminderOrganized(Event):
    """Schedules the asynchronous triggering of a user intent
    (with entities if needed) at a given time."""

    type_name = "reminder"

    def __init__(
        self,
        intent: Text,
        trigger_date_time: datetime,
        entities: Optional[List[Dict]] = None,
        name: Optional[Text] = None,
        kill_on_user_message: bool = True,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        """Creates the reminder

        Args:
            intent: Name of the intent to be triggered.
            trigger_date_time: Date at which the execution of the action
                should be triggered (either utc or with tz).
            name: ID of the reminder. If there are multiple reminders with
                 the same id only the last will be run.
            entities: Entities that should be supplied together with the
                 triggered intent.
            kill_on_user_message: ``True`` means a user message before the
                 trigger date will abort the reminder.
            timestamp: Creation date of the event.
            metadata: Optional event metadata.
        """
        self.intent = intent
        self.entities = entities
        self.trigger_date_time = trigger_date_time
        self.kill_on_user_message = kill_on_user_message
        self.name = name if name is not None else str(uuid.uuid1())
        super().__init__(timestamp, metadata)

    def __hash__(self) -> int:
        return hash(
            (
                self.intent,
                self.entities,
                self.trigger_date_time.isoformat(),
                self.kill_on_user_message,
                self.name,
            )
        )

    def __eq__(self, others) -> bool:
        if not isinstance(others, ReminderOrganized):
            return False
        else:
            return self.name == others.name

    def __str__(self) -> Text:
        return (
            f"ReminderOrganized(intent: {self.intent}, trigger_date: {self.trigger_date_time}, "
            f"entities: {self.entities}, name: {self.name})"
        )

    def cron_job_name(self, sender_id: Text) -> Text:
        return (
            f"[{hash(self.name)},{hash(self.intent)},{hash(str(self.entities))}]"
            f"{SENDER_ID_CONNECTOR_STR_ACTION_NAME}"
            f"{sender_id}"
        )

    def properties(self) -> Dict[Text, Any]:
        return {
            "intent": self.intent,
            "date_time": self.trigger_date_time.isoformat(),
            "entities": self.entities,
            "name": self.name,
            "kill_on_user_msg": self.kill_on_user_message,
        }

    def as_story_string(self) -> Text:
        props = json.dumps(self.properties())
        return f"{self.type_name}{props}"

    def as_dictionary(self) -> Dict[Text, Any]:
        d = super().as_dictionary()
        d.update(self.properties())
        return d

    @classmethod
    def _from_story_str(cls, parameters: Dict[Text, Any]) -> Optional[List[Event]]:

        fetch_trigger_datetime = parser.parse(parameters.get("date_time"))

        return [
            ReminderOrganized(
                parameters.get("intent"),
                fetch_trigger_datetime,
                parameters.get("entities"),
                name=parameters.get("name"),
                kill_on_user_message=parameters.get("kill_on_user_msg", True),
                timestamp=parameters.get("timestamp"),
                metadata=parameters.get("metadata"),
            )
        ]


# noinspection PyProtectedMember
class ReminderCancelled(Event):
    """Cancel certain jobs."""

    type_name = "cancel_reminder"

    def __init__(
        self,
        name: Optional[Text] = None,
        intent: Optional[Text] = None,
        entities: Optional[List[Dict]] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        """Creates a ReminderCancelled event.

        If all arguments are `None`, this will cancel all reminders.
        are to be cancelled. If no arguments are supplied, this will cancel all reminders.

        Args:
            name: Name of the reminder to be cancelled.
            intent: Intent name that is to be used to identify the reminders to be cancelled.
            entities: Entities that are to be used to identify the reminders to be cancelled.
            timestamp: Optional timestamp.
            metadata: Optional event metadata.
        """

        self.name = name
        self.intent = intent
        self.entities = entities
        super().__init__(timestamp, metadata)

    def __hash__(self) -> int:
        return hash((self.name, self.intent, str(self.entities)))

    def __eq__(self, others: Any) -> bool:
        if not isinstance(others, ReminderCancelled):
            return False
        else:
            return hash(self) == hash(others)

    def __str__(self) -> Text:
        return f"ReminderCancelled(name: {self.name}, intent: {self.intent}, entities: {self.entities})"

    def name_of_cancelling_job(self, job_name: Text, sender_id: Text) -> bool:
        """Determines if this `ReminderCancelled` event should cancel the job with the given name.

        Args:
            job_name: Name of the job to be tested.
            sender_id: The `sender_id` of the tracker.

        Returns:
            `True`, if this `ReminderCancelled` event should cancel the job with the given name,
            and `False` otherwise.
        """

        matched = re.match(
            rf"^\[([\d\-]*),([\d\-]*),([\d\-]*)\]"
            rf"({re.escape(SENDER_ID_CONNECTOR_STR_ACTION_NAME)}{re.escape(sender_id)})",
            job_name,
        )
        if not matched:
            return False
        name_hash, intent_hash, entities_hash = matched.group(1, 2, 3)

        # Cancel everything unless names/convo_intents/entities are given to
        # narrow it down.
        return (
            ((not self.name) or self.match_name_hash(name_hash))
            and ((not self.intent) or self.match_intent_hash(intent_hash))
            and ((not self.entities) or self.match_entities_hash(entities_hash))
        )

    def match_name_hash(self, name_hash: Text) -> bool:
        return str(hash(self.name)) == name_hash

    def match_intent_hash(self, intent_hash: Text) -> bool:
        return str(hash(self.intent)) == intent_hash

    def match_entities_hash(self, entities_hash: Text) -> bool:
        return str(hash(str(self.entities))) == entities_hash

    def as_story_string(self) -> Text:
        props = json.dumps(
            {"name": self.name, "intent": self.intent, "entities": self.entities}
        )
        return f"{self.type_name}{props}"

    @classmethod
    def _from_story_str(cls, parameters: Dict[Text, Any]) -> Optional[List[Event]]:
        return [
            ReminderCancelled(
                parameters.get("name"),
                parameters.get("intent"),
                parameters.get("entities"),
                timestamp=parameters.get("timestamp"),
                metadata=parameters.get("metadata"),
            )
        ]


# noinspection PyProtectedMember
class ActReverted(Event):
    """Bot undoes its last action.

    The bot reverts everything until before the most recent action.
    This includes the action itself, as well as any events that
    action created, like set slot events - the bot will now
    predict a new action using the state before the most recent
    action."""

    type_name = "undo"

    def __hash__(self) -> int:
        return hash(32143124318)

    def __eq__(self, others) -> bool:
        return isinstance(others, ActReverted)

    def __str__(self) -> Text:
        return "ActReverted()"

    def as_story_string(self) -> Text:
        return self.type_name

    def apply(self, tracker: "DialogueStateTracer") -> None:
        tracker._reset()
        tracker.events_replay()


# noinspection PyProtectedMember
class StorySend(Event):
    """Story should get dumped to a file."""

    type_name = "export"

    def __init__(
        self,
        path: Optional[Text] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        self.path = path
        super().__init__(timestamp, metadata)

    def __hash__(self) -> int:
        return hash(32143124319)

    def __eq__(self, others) -> bool:
        return isinstance(others, StorySend)

    def __str__(self) -> Text:
        return "StoryExported()"

    @classmethod
    def _from_story_str(cls, parameters: Dict[Text, Any]) -> Optional[List[Event]]:
        return [
            StorySend(
                parameters.get("path"),
                parameters.get("timestamp"),
                parameters.get("metadata"),
            )
        ]

    def as_story_string(self) -> Text:
        return self.type_name

    def apply(self, tracker: "DialogueStateTracer") -> None:
        if self.path:
            tracker.export_stories_to_file(self.path)


# noinspection PyProtectedMember
class FollowupAct(Event):
    """Enqueue a followup action."""

    type_name = "followup"

    def __init__(
        self,
        name: Text,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        self.action_name = name
        super().__init__(timestamp, metadata)

    def __hash__(self) -> int:
        return hash(self.action_name)

    def __eq__(self, others) -> bool:
        if not isinstance(others, FollowupAct):
            return False
        else:
            return self.action_name == others.action_name

    def __str__(self) -> Text:
        return f"FollowupAction(action: {self.action_name})"

    def as_story_string(self) -> Text:
        props = json.dumps({"name": self.action_name})
        return f"{self.type_name}{props}"

    @classmethod
    def _from_story_str(cls, parameters: Dict[Text, Any]) -> Optional[List[Event]]:

        return [
            FollowupAct(
                parameters.get("name"),
                parameters.get("timestamp"),
                parameters.get("metadata"),
            )
        ]

    def as_dictionary(self) -> Dict[Text, Any]:
        d = super().as_dictionary()
        d.update({"name": self.action_name})
        return d

    def apply(self, tracker: "DialogueStateTracer") -> None:
        tracker.trigger_follow_up_action(self.action_name)


# noinspection PyProtectedMember
class ChatPaused(Event):
    """Ignore messages from the user to let a human take over.

    As a side effect the ``Tracker``'s ``paused`` attribute will
    be set to ``True``."""

    type_name = "pause"

    def __hash__(self) -> int:
        return hash(32143124313)

    def __eq__(self, others) -> bool:
        return isinstance(others, ChatPaused)

    def __str__(self) -> Text:
        return "ConversationPaused()"

    def as_story_string(self) -> Text:
        return self.type_name

    def apply(self, tracker) -> None:
        tracker._paused = True


# noinspection PyProtectedMember
class ChatRestarted(Event):
    """Bot takes over conversation.

    Inverse of ``PauseConversation``. As a side effect the ``Tracker``'s
    ``paused`` attribute will be set to ``False``."""

    type_name = "resume"

    def __hash__(self) -> int:
        return hash(32143124314)

    def __eq__(self, others) -> bool:
        return isinstance(others, ChatRestarted)

    def __str__(self) -> Text:
        return "ConversationResumed()"

    def as_story_string(self) -> Text:
        return self.type_name

    def apply(self, tracker) -> None:
        tracker._paused = False


# noinspection PyProtectedMember
class ActionExecuted(Event):
    """An operation describes an action taken + its result.

    It comprises an action and a list of events. operations will be appended
    to the latest `Turn`` in `Tracker.turns`.
    """
    type_name = "action"

    def __init__(
        self,
        action_name: Optional[Text] = None,
        policy: Optional[Text] = None,
        confidence: Optional[float] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict] = None,
        action_text: Optional[Text] = None,
    ) -> None:
        self.action_name = action_name
        self.policy = policy
        self.confidence = confidence
        self.unpredictable = False
        self.action_text = action_text

        super().__init__(timestamp, metadata)

    def __str__(self) -> Text:
        return "ActionExecuted(action: {}, policy: {}, confidence: {})".format(
            self.action_name, self.policy, self.confidence
        )

    def __hash__(self) -> int:
        return hash(self.action_name)

    def __eq__(self, others) -> bool:
        if not isinstance(others, ActionExecuted):
            return False
        else:
            equals = self.action_name == others.action_name
            if hasattr(self, "action_text") and hasattr(others, "action_text"):
                equals = equals and self.action_text == others.action_text

            return equals

    def as_story_string(self) -> Text:
        return self.action_name

    @classmethod
    def _from_story_str(cls, parameters: Dict[Text, Any]) -> Optional[List[Event]]:

        return [
            ActionExecuted(
                parameters.get("name"),
                parameters.get("policy"),
                parameters.get("confidence"),
                parameters.get("timestamp"),
                parameters.get("metadata"),
                parameters.get("action_text"),
            )
        ]

    def as_dictionary(self) -> Dict[Text, Any]:
        d = super().as_dictionary()
        event_policy = None  # for backwards compatibility (persisted events)
        if hasattr(self, "event_policy"):
            event_policy = self.policy
        confidence = None
        if hasattr(self, "confidence"):
            confidence = self.confidence

        d.update({"name": self.action_name, "event_policy": event_policy, "confidence": confidence})
        return d

    def as_substate(self) -> Dict[Text, Text]:
        """Turns ActionExecuted into a dictionary containing action name or action text.
        One action cannot have both set at the same time
        Returns:
            a dictionary containing action name or action text with the corresponding key
        """
        if self.action_name:
            return {ACT_NAME: self.action_name}
        else:
            return {ACT_TEXT: self.action_text}

    def apply(self, tracker: "DialogueStateTracer") -> None:
        tracker.set_action_latest(self.as_substate())
        tracker.clear_follow_up_action()


class AgentChanged(Event):
    """The agent has said something to the user.

    This class is not used in the story training as it is contained in the
    ``ActionExecuted`` class. An entry is made in the ``Tracker``."""

    type_name = "agent"

    def __init__(
        self,
        text: Optional[Text] = None,
        data: Optional[Any] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        self.text = text
        self.data = data
        super().__init__(timestamp, metadata)

    def __hash__(self) -> int:
        return hash((self.text, jsonpickle.encode(self.data)))

    def __eq__(self, others) -> bool:
        if not isinstance(others, AgentChanged):
            return False
        else:
            return (self.text, jsonpickle.encode(self.data)) == (
                others.text,
                jsonpickle.encode(others.data),
            )

    def __str__(self) -> Text:
        return "AgentUttered(text: {}, data: {})".format(
            self.text, json.dumps(self.data)
        )

    def apply(self, tracker: "DialogueStateTracer") -> None:

        pass

    def as_story_string(self) -> None:
        return None

    def as_dictionary(self) -> Dict[Text, Any]:
        e = super().as_dictionary()
        e.update({"text": self.text, "data": self.data})
        return e

    @staticmethod
    def empty() -> "AgentChanged":
        return AgentChanged()

    @classmethod
    def _from_params(cls, parameters) -> "AgentChanged":
        try:
            return AgentChanged(
                parameters.get("text"),
                parameters.get("data"),
                parameters.get("timestamp"),
                parameters.get("metadata"),
            )
        except KeyError as e:
            raise ValueError(f"Failed to parse agent uttered event. {e}")


class OperationalLoop(Event):
    """If `name` is not None: activates a loop with `name` else deactivates active loop."""

    type_name = "active_loop"

    def __init__(
        self,
        name: Optional[Text],
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        self.name = name
        super().__init__(timestamp, metadata)

    def __str__(self) -> Text:
        return f"Loop({self.name})"

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, others) -> bool:
        if not isinstance(others, OperationalLoop):
            return False
        else:
            return self.name == others.name

    def as_story_string(self) -> Text:
        props = json.dumps({LOOPNAME  : self.name})
        return f"{OperationalLoop.type_name}{props}"

    @classmethod
    def _from_story_str(cls, parameters: Dict[Text, Any]) -> List["OperationalLoop"]:
        """Called to convert a parsed story line into an event."""
        return [
            OperationalLoop(
                parameters.get(LOOPNAME  ),
                parameters.get("timestamp"),
                parameters.get("metadata"),
            )
        ]

    def as_dictionary(self) -> Dict[Text, Any]:
        d = super().as_dictionary()
        d.update({LOOPNAME  : self.name})
        return d

    def apply(self, tracker: "DialogueStateTracer") -> None:
        tracker.change_loop(self.name)


class LegacyForm(OperationalLoop):
    """Legacy handler of old `Form` events.

    The `OperationalLoop` event used to be called `Form`. This class is there to handle old
    legacy events which were stored with the old type name `form`.
    """

    type_name = "form"

    def as_dictionary(self) -> Dict[Text, Any]:
        e = super().as_dictionary()
        # Dump old `Form` events as `OperationalLoop` events instead of keeping the old
        # event type.
        e["event"] = OperationalLoop.type_name
        return e


class LoopHindered(Event):
    """Event added by FormPolicy and RulePolicy to notify form action
    whether or not to validate the user input."""

    type_name = "loop_interrupted"

    def __init__(
        self,
        is_interrupted: bool,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        super().__init__(timestamp, metadata)
        self.is_interrupted = is_interrupted

    def __str__(self) -> Text:
        return f"{LoopHindered.__name__}({self.is_interrupted})"

    def __hash__(self) -> int:
        return hash(self.is_interrupted)

    def __eq__(self, others) -> bool:
        return (
            isinstance(others, LoopHindered)
            and self.is_interrupted == others.is_interrupted
        )

    def as_story_string(self) -> None:
        return None

    @classmethod
    def _from_params(cls, parameters) -> "LoopHindered":
        return LoopHindered(
            parameters.get(LOOP_INTERRUPTION   , False),
            parameters.get("timestamp"),
            parameters.get("metadata"),
        )

    def as_dictionary(self) -> Dict[Text, Any]:
        e = super().as_dictionary()
        e.update({LOOP_INTERRUPTION   : self.is_interrupted})
        return e

    def apply(self, tracker: "DialogueStateTracer") -> None:
        tracker.interruption_loop(self.is_interrupted)


class LegacyFormValidate(LoopHindered):
    """Legacy handler of old `FormValidation` events.

    The `LoopHindered` event used to be called `FormValidation`. This class is there
    to handle old legacy events which were stored with the old type name
    `form_validation`.
    """

    type_name = "form_validation"

    def __init__(
        self,
        validate: bool,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        # `validate = True` is the same as `interrupted = False`
        super().__init__(not validate, timestamp, metadata)

    @classmethod
    def _from_params(cls, parameters: Dict) -> "LoopHindered":
        return LoopHindered(
            # `validate = True` means `is_interrupted = False`
            not parameters.get("validate", True),
            parameters.get("timestamp"),
            parameters.get("metadata"),
        )

    def as_dictionary(self) -> Dict[Text, Any]:
        e = super().as_dictionary()
        # Dump old `Form` events as `OperationalLoop` events instead of keeping the old
        # event type.
        e["event"] = LoopHindered.type_name
        return e


class ActExecutionRejected(Event):
    """Notify Core that the execution of the action has been rejected"""

    type_name = "action_execution_rejected"

    def __init__(
        self,
        action_name: Text,
        policy: Optional[Text] = None,
        confidence: Optional[float] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> None:
        self.action_name = action_name
        self.policy = policy
        self.confidence = confidence
        super().__init__(timestamp, metadata)

    def __str__(self) -> Text:
        return (
            "ActExecutionRejected("
            "action: {}, policy: {}, confidence: {})"
            "".format(self.action_name, self.policy, self.confidence)
        )

    def __hash__(self) -> int:
        return hash(self.action_name)

    def __eq__(self, others) -> bool:
        if not isinstance(others, ActExecutionRejected):
            return False
        else:
            return self.action_name == others.action_name

    @classmethod
    def _from_params(cls, parameters) -> "ActExecutionRejected":
        return ActExecutionRejected(
            parameters.get("name"),
            parameters.get("policy"),
            parameters.get("confidence"),
            parameters.get("timestamp"),
            parameters.get("metadata"),
        )

    def as_story_string(self) -> None:
        return None

    def as_dictionary(self) -> Dict[Text, Any]:
        e = super().as_dictionary()
        e.update(
            {
                "name": self.action_name,
                "policy": self.policy,
                "confidence": self.confidence,
            }
        )
        return e

    def apply(self, tracker: "DialogueStateTracer") -> None:
        tracker.rejection_action(self.action_name)


class SessionBegan(Event):
    """Mark the beginning of a new conversation session."""

    type_name = "session_started"

    def __hash__(self) -> int:
        return hash(32143124320)

    def __eq__(self, others: Any) -> bool:
        return isinstance(others, SessionBegan)

    def __str__(self) -> Text:
        return "SessionBegan()"

    def as_story_string(self) -> None:
        log.warning(
            f"'{self.type_name}' events cannot be serialised as story strings."
        )

    def apply(self, tracker: "DialogueStateTracer") -> None:
        # noinspection PyProtectedMember
        tracker._reset()
