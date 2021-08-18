import logging
import warnings
from typing import Dict, Text, Any, List, Optional, Union
import datetime

log = logging.getLogger(__name__)

EventType = Dict[Text, Any]


# noinspection PyPep8Naming
def UserUttered(
    text: Optional[Text],
    parse_data: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
    input_channel: Optional[Text] = None,
) -> EventType:
    return {
        "event": "user",
        "timestamp": timestamp,
        "text": text,
        "parse_data": parse_data,
        "input_channel": input_channel,
    }


# noinspection PyPep8Naming
def bot_utterance(
    text: Optional[Text] = None,
    data: Optional[Dict[Text, Any]] = None,
    metadata: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return {
        "event": "bot",
        "timestamp": timestamp,
        "text": text,
        "data": data,
        "metadata": metadata,
    }


# noinspection PyPep8Naming
def SlotSet(
    key: Text, value: Any = None, timestamp: Optional[float] = None
) -> EventType:
    return {"event": "slot", "timestamp": timestamp, "name": key, "value": value}


# noinspection PyPep8Naming
def Restarted(timestamp: Optional[float] = None) -> EventType:
    return {"event": "restart", "timestamp": timestamp}


# noinspection PyPep8Naming
def session_started(timestamp: Optional[float] = None) -> EventType:
    return {"event": "session_started", "timestamp": timestamp}


# noinspection PyPep8Naming
def UserUtteranceReverted(timestamp: Optional[float] = None) -> EventType:
    return {"event": "rewind", "timestamp": timestamp}


# noinspection PyPep8Naming
def AllSlotsReset(timestamp: Optional[float] = None) -> EventType:
    return {"event": "reset_slots", "timestamp": timestamp}


def _is_probably_action_name(name: Optional[Text]) -> bool:
    return name is not None and (
        name.startswith("utter_") or name.startswith("action_")
    )


# noinspection PyPep8Naming
def reminder_scheduled(
    intent_name: Text,
    trigger_date_time: datetime.datetime,
    entities: Optional[Union[List[Dict[Text, Any]], Dict[Text, Text]]] = None,
    name: Optional[Text] = None,
    kill_on_user_message: bool = True,
    timestamp: Optional[float] = None,
) -> EventType:
    if _is_probably_action_name(intent_name):
        warnings.warn(
            f"reminder_scheduled intent starts with 'utter_' or 'action_'. "
            f"If '{intent_name}' is indeed an intent, then you can ignore this warning.",
            FutureWarning,
        )
    return {
        "event": "reminder",
        "timestamp": timestamp,
        "intent": intent_name,
        "entities": entities,
        "date_time": trigger_date_time.isoformat(),
        "name": name,
        "kill_on_user_msg": kill_on_user_message,
    }


# noinspection PyPep8Naming
def reminder_cancelled(
    name: Optional[Text] = None,
    intent_name: Optional[Text] = None,
    entities: Optional[Union[List[Dict[Text, Any]], Dict[Text, Text]]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    if _is_probably_action_name(intent_name):
        warnings.warn(
            f"reminder_cancelled intent starts with 'utter_' or 'action_'. "
            f"If '{intent_name}' is indeed an intent, then you can ignore this warning.",
            FutureWarning,
        )
    return {
        "event": "cancel_reminder",
        "timestamp": timestamp,
        "intent": intent_name,
        "entities": entities,
        "name": name,
    }


# noinspection PyPep8Naming
def act_reverted(timestamp: Optional[float] = None) -> EventType:
    return {"event": "undo", "timestamp": timestamp}


# noinspection PyPep8Naming
def story_exported(timestamp: Optional[float] = None) -> EventType:
    return {"event": "export", "timestamp": timestamp}


# noinspection PyPep8Naming
def FollowupAction(name: Text, timestamp: Optional[float] = None) -> EventType:
    return {"event": "followup", "timestamp": timestamp, "name": name}


# noinspection PyPep8Naming
def ConversationPaused(timestamp: Optional[float] = None) -> EventType:
    return {"event": "pause", "timestamp": timestamp}


# noinspection PyPep8Naming
def conv_resumed(timestamp: Optional[float] = None) -> EventType:
    return {"event": "resume", "timestamp": timestamp}


# noinspection PyPep8Naming
def ActionExecuted(
    action_name,
    policy=None,
    confidence: Optional[float] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return {
        "event": "action",
        "name": action_name,
        "policy": policy,
        "confidence": confidence,
        "timestamp": timestamp,
    }


# noinspection PyPep8Naming
def agent_uttered(
    text: Optional[Text] = None, data=None, timestamp: Optional[float] = None
) -> EventType:
    return {"event": "agent", "text": text, "data": data, "timestamp": timestamp}


# noinspection PyPep8Naming
def active_loop(name: Optional[Text], timestamp: Optional[float] = None) -> EventType:
    return {"event": "active_loop", "name": name, "timestamp": timestamp}


# noinspection PyPep8Naming
def Form(name: Optional[Text], timestamp: Optional[float] = None) -> EventType:
    warnings.warn(
        "The `Form` event is deprecated. Please use the `active_loop` event " "instead.",
        DeprecationWarning,
    )
    return active_loop(name, timestamp)


# noinspection PyPep8Naming
def loop_interrupt(
    is_interrupted: bool, timestamp: Optional[float] = None
) -> EventType:
    return {
        "event": "loop_interrupted",
        "is_interrupted": is_interrupted,
        "timestamp": timestamp,
    }


# noinspection PyPep8Naming
def form_validation(validate: bool, timestamp: Optional[float] = None) -> EventType:
    warnings.warn(
        f"The {form_validation.__name__}` event is deprecated. Please use the "
        f"`{loop_interrupt.__name__}` event instead.",
        DeprecationWarning,
    )
    # `validate = False` is the same as `is_interrupted = True`
    return loop_interrupt(not validate, timestamp)


# noinspection PyPep8Naming
def action_exec_stopped(
    action_name: Text,
    policy: Optional[Text] = None,
    confidence: Optional[float] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return {
        "event": "action_execution_rejected",
        "name": action_name,
        "policy": policy,
        "confidence": confidence,
        "timestamp": timestamp,
    }
