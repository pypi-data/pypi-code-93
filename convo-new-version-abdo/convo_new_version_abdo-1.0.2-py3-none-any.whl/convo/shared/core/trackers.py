import copy
import logging
import os
from collections import deque
from enum import Enum
from typing import (
    Dict,
    Text,
    Any,
    Optional,
    Iterator,
    Generator,
    Type,
    List,
    Deque,
    Iterable,
    Union,
    FrozenSet,
    Tuple,
)

import typing

import convo.shared.utils.io
from convo.shared.constants import CONVO_DEFAULT_SENDER_ID 
from convo.shared.nlu.constants import (
    ATTRIBUTE_VALUE_ENTITY,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
    ACT_TEXT,
    ACT_NAME,
)
from convo.shared.core import events  # pytype: disable=pyi-error
from convo.shared.core.constants import (
    LISTEN_ACTION_NAME  ,
    LOOPNAME  ,
    NOT_SET   ,
    PRECEDING_ACTION   ,
    CURRENT_LOOP   ,
    LOOP_REJECTION,
    TRIGGER_MSG,
    LOOP_INTERRUPTION   ,
)
from convo.shared.core.conversation import Dialogue  # pytype: disable=pyi-error
from convo.shared.core.events import (  # pytype: disable=pyi-error
    UserUttered,
    ActionExecuted,
    Event,
  SetofSlot,
    Restarted,
    ActReverted,
    UserChangeReverted,
    BotUttered,
    OperationalLoop,
    SessionBegan,
    ActExecutionRejected,
)
from convo.shared.core.domain import Domain, fetch_state  # pytype: disable=pyi-error
from convo.shared.core.slots import Slot

if typing.TYPE_CHECKING:
    from convo.shared.core.training_data.structures import Story
    from convo.shared.core.training_data.story_writer.story_writer import StoryWriter


log = logging.getLogger(__name__)

# same as fetch_state but with Dict[...] substituted with FrozenSet[Tuple[...]]
Frozen_State = FrozenSet[Tuple[Text, FrozenSet[Tuple[Text, Tuple[Union[float, Text]]]]]]


class releaseVerbosity(Enum):
    """Filter on which events to include in tracker data_dumps."""

    # no events will be included
    NONE = 1

    # all events, that contribute to the trackers state are included
    # these are all you need to reconstruct the tracker state
    APPLIED = 2

    # include even more events, in this case everything that comes
    # after the most recent Restarted event. this will also include
    # utterances that got reverted and actions that got undone.
    AFTER_RESTART = 3

    # include every logged event
    ALL = 4


class AnySlotDictionary(dict):
    """A slot dictionary that pretends every slot exists, by creating convo_slotson demand.

    This only uses the generic slot type! This means certain functionality wont work,
    e.g. properly featurizing the slot."""

    def __missing__(self, key) -> Slot:
        value = self[key] = Slot(key)
        return value

    def __contains__(self, key) -> bool:
        return True


class DialogueStateTracer:
    """Maintains the state of a conversation.

    The field max_event_history will only give you these last events,
    it can be set in the tracker_store"""

    @classmethod
    def from_dict(
        cls,
        sender_id: Text,
        events_as_dict: List[Dict[Text, Any]],
        slots: Optional[List[Slot]] = None,
        max_event_history: Optional[int] = None,
    ) -> "DialogueStateTracer":
        """Create a tracker from dump.

        The dump should be an array of dumped evts. When restoring
        the tracker, these evts will be replayed to recreate the state."""

        evts = events.deserialized_events(events_as_dict)
        return cls.from_events_tracker(sender_id, evts, slots, max_event_history)

    @classmethod
    def from_events_tracker(
        cls,
        sender_id: Text,
        evts: List[Event],
        slots: Optional[List[Slot]] = None,
        max_event_history: Optional[int] = None,
        sender_source: Optional[Text] = None,
    ):
        tracer = cls(sender_id, slots, max_event_history, sender_source)
        for e in evts:
            tracer.update(e)
        return tracer

    def __init__(
        self,
        sender_id: Text,
        slots: Optional[Iterable[Slot]],
        max_event_history: Optional[int] = None,
        sender_source: Optional[Text] = None,
        is_rule_tracker: bool = False,
    ) -> None:
        """Initialize the tracker.

        A set of events can be stored externally, and we will run through all
        of them to get the current state. The tracker will represent all the
        information we captured while processing messages of the dialogue."""

        # maximum number of events to store
        self._max_event_history = max_event_history
        # list of previously seen events
        self.events = self.create_events([])
        # id of the source of the messages
        self.sender_id = sender_id
        # convo_slotsthat can be filled in this domain
        if slots is not None:
            self.slots= {slot.name: copy.copy(slot) for slot in slots}
        else:
            self.slots= AnySlotDictionary()
        # file source of the messages
        self.sender_source = sender_source
        # whether the tracker belongs to a rule-based data
        self.is_rule_tracker = is_rule_tracker

        ###
        # current state of the tracker - MUST be re-creatable by processing
        # all the events. This only defines the attributes, values are set in
        # `reset()`
        ###
        # if tracker is paused, no actions should be taken
        self._paused = False
        # A deterministically scheduled action to be executed next
        self.followup_action = LISTEN_ACTION_NAME  
        self.latest_action = None
        # Stores the most recent message sent by the user
        self.latest_message = None
        self.latest_bot_utterance = None
        self._reset()
        self.active_loop: Dict[Text, Union[Text, bool, Dict, None]] = {}

    ###
    # Public tracker interface
    ###
    def current_active_state(
        self, event_verbosity: releaseVerbosity = releaseVerbosity.NONE
    ) -> Dict[Text, Any]:
        """Return the current tracker state as an object."""

        tracker_events = self.events_for_verbosity(event_verbosity)
        if tracker_events:
            tracker_events = [e.as_dictionary() for e in tracker_events]
        event_name_latest = None
        if len(self.events) > 0:
            event_name_latest = self.events[-1].timestamp

        return {
            "sender_id": self.sender_id,
            "slots": self.values_of_current_slot(),
            "latest_message": self.latest_message.parse_data,
            "event_name_latest": event_name_latest,
            "followup_action": self.followup_action,
            "paused": self.pause_check(),
            "events": tracker_events,
            "latest_input_channel": self.get_input_channel_latest(),
            CURRENT_LOOP   : self.active_loop,
            "latest_action": self.latest_action,
            "latest_action_name": self.latestActionName,
        }

    def events_for_verbosity(
        self, event_verbosity: releaseVerbosity
    ) -> Optional[List[Event]]:
        if event_verbosity == releaseVerbosity.ALL:
            return list(self.events)
        if event_verbosity == releaseVerbosity.AFTER_RESTART:
            return self.events_after_last_restart()
        if event_verbosity == releaseVerbosity.APPLIED:
            return self.request_events()

        return None

    @staticmethod
    def current_state_freeze(state: fetch_state) -> Frozen_State:
        frozen_state = frozenset(
            {
                key: frozenset(values.items())
                if isinstance(values, Dict)
                else frozenset(values)
                for key, values in state.items()
            }.items()
        )
        return frozen_state

    def freeze_state(self, domain: Domain) -> List[fetch_state]:
        """Generate the past states of this tracker based on the history.

        Args:
            domain: a :class:`convo.shared.core.domain.Domain`

        Returns:
            a list of states
        """
        return domain.states_tracker_history(self)

    def change_loop(self, loop_name: Text) -> None:
        """Set the currently active loop.

        Args:
            loop_name: The name of loop which should be marked as active.
        """
        if loop_name is not None:
            self.active_loop = {
                LOOPNAME  : loop_name,
                LOOP_INTERRUPTION   : False,
                LOOP_REJECTION: False,
                TRIGGER_MSG: self.latest_message.parse_data,
            }
        else:
            self.active_loop = {}

    def change_form(self, form_name: Text) -> None:
        convo.shared.utils.io.raising_warning(
            "`change_form_to` is deprecated and will be removed "
            "in future versions. Please use `change_loop_to` "
            "instead.",
            category=DeprecationWarning,
        )
        self.change_loop(form_name)

    def interruption_loop(self, is_interrupted: bool) -> None:
        """Interrupt loop and mark that we entered an unhappy path in the conversation.
        Args:
            is_interrupted: `True` if the loop was run after an unhappy path.
        """
        self.active_loop[LOOP_INTERRUPTION] = is_interrupted

    def set_form_validity(self, validate: bool) -> None:
        convo.shared.utils.io.raising_warning(
            "`set_form_validation` is deprecated and will be removed "
            "in future versions. Please use `interrupt_loop` "
            "instead.",
            category=DeprecationWarning,
        )
        # `validate = True` means `is_interrupted = False`
        self.interruption_loop(not validate)

    def rejection_action(self, action_name: Text) -> None:
        """Notify active loop that it was rejected"""
        if action_name == self.activeLoopName:
            self.active_loop[LOOP_REJECTION] = True

    def set_action_latest(self, action: Dict[Text, Text]) -> None:
        """Set latest action name
        and reset form validation and rejection parameters
        """
        self.latest_action = action
        if self.activeLoopName:
            # reset form validation if some loop is active
            self.active_loop[LOOP_INTERRUPTION   ] = False

        if action.get(ACT_NAME) == self.activeLoopName:
            # reset loop rejection if it was predicted again
            self.active_loop[LOOP_REJECTION] = False

    def values_of_current_slot(self) -> Dict[Text, Any]:
        """Return the currently set values of the slots"""
        return {key: slot.value for key, slot in self.slots.items()}

    def get_slot(self, key: Text) -> Optional[Any]:
        """Retrieves the value of a slot."""

        if key in self.slots:
            return self.slots[key].value
        else:
            log.info(f"Tried to access non existent slot '{key}'")
            return None

    def get_entity_values_latest(
        self,
        entity_type: Text,
        entity_role: Optional[Text] = None,
        entity_group: Optional[Text] = None,
    ) -> Iterator[Text]:
        """Get entity values found for the passed entity type and optional role and
        group in latest message.

        If you are only interested in the first entity of a given type use
        `next(tracker.get_latest_entity_values("my_entity_name"), None)`.
        If no entity is found `None` is the default result.

        Args:
            entity_type: the entity type of interest
            entity_role: optional entity role of interest
            entity_group: optional entity group of interest

        Returns:
            Entity values.
        """

        return (
            x.get(ATTRIBUTE_VALUE_ENTITY)
            for x in self.latest_message.entities
            if x.get(ATTRIBUTE_TYPE_ENTITY) == entity_type
            and x.get(ATTRIBUTE_GROUP_ENTITY) == entity_group
            and x.get(ATTRIBUTE_ROLE_ENTITY) == entity_role
        )

    def get_input_channel_latest(self) -> Optional[Text]:
        """Get the name of the input_channel of the latest UserUttered event"""

        for e in reversed(self.events):
            if isinstance(e, UserUttered):
                return e.input_channel
        return None

    def pause_check(self) -> bool:
        """fetch_state whether the tracker is currently paused."""
        return self._paused

    def idx_after_last_restart(self) -> int:
        """Return the idx of the most recent Restarted in the list of events.

        If the conversation has not been restarted, ``0`` is returned."""

        for i, event in enumerate(reversed(self.events)):
            if isinstance(event, Restarted):
                return len(self.events) - i

        return 0

    def events_after_last_restart(self) -> List[Event]:
        """Return a list of events after the most recent Restarted."""
        return list(self.events)[self.idx_after_last_restart():]

    def initialize_copy(self) -> "DialogueStateTracer":
        """Creates a new state tracker with the same initial values."""

        return DialogueStateTracer(
            CONVO_DEFAULT_SENDER_ID ,
            self.slots.values(),
            self._max_event_history,
            is_rule_tracker=self.is_rule_tracker,
        )

    def generates_all_priority_trackers(
        self,
    ) -> Generator["DialogueStateTracer", None, None]:
        """Returns a generator of the previous trackers of this tracker.

        The resulting array is representing the trackers before each action."""

        tracer = self.initialize_copy()

        for event in self.request_events():

            if isinstance(event, ActionExecuted):
                yield tracer

            tracer.update(event)

        yield tracer

    def request_events(self) -> List[Event]:
        """Returns all actions that should be applied - w/o reverted events."""

        names_of_loop= [
            event.name
            for event in self.events
            if isinstance(event, OperationalLoop) and event.name
        ]

        request_events = []

        for event in self.events:
            if isinstance(event, (Restarted, SessionBegan)):
                request_events = []
            elif isinstance(event, ActReverted):
                self.undo_till_previous(ActionExecuted, request_events)
            elif isinstance(event, UserChangeReverted):
                # Seeing a user uttered event automatically implies there was
                # a listen event right before it, so we'll first rewind the
                # user utterance, then get the action right before it (also removes
                # the `action_listen` action right before it).
                self.undo_till_previous(UserUttered, request_events)
                self.undo_till_previous(ActionExecuted, request_events)
            elif (
                    isinstance(event, ActionExecuted)
                    and event.action_name in names_of_loop
                    and not self.first_loop_execution_or_unhappy_path(
                    event.action_name, request_events
                )
            ):
                self.undo_till_prev_loop_execution(
                    event.action_name, request_events
                )
            else:
                request_events.append(event)

        return request_events

    @staticmethod
    def undo_till_previous(EventType: Type[Event], done_events: List[Event]) -> None:
        """Removes events from `done_events` until the first occurrence `EventType`
        is found which is also removed."""
        # list gets modified - hence we need to copy events!
        for e in reversed(done_events[:]):
            del done_events[-1]
            if isinstance(e, EventType):
                break

    def first_loop_execution_or_unhappy_path(
        self, loop_action_name: Text, request_events: List[Event]
    ) -> bool:
        next_available_action: Optional[Text] = None

        for event in reversed(request_events):
            # Stop looking for a previous loop execution if there is a loop deactivate
            # event because it means that the current loop is running for the first
            # time and previous loop events belong to different loops.
            if isinstance(event, OperationalLoop) and event.name is None:
                return True

            if self.within_unhappy_path_check(loop_action_name, event, next_available_action):
                return True

            if isinstance(event, ActionExecuted):
                # We found a previous execution of the loop and we are not within an
                # unhappy path.
                if event.action_name == loop_action_name:
                    return False

                # Remember the action as we need that to check whether we might be
                # within an unhappy path.
                next_available_action = event.action_name

        return True

    @staticmethod
    def within_unhappy_path_check(
        loop_action_name: Text, event: Event, next_action_in_the_future: Optional[Text]
    ) -> bool:
        # When actual users are talking to the action has to return an
        # `ActExecutionRejected` in order to enter an unhappy path.
        loop_rejected_previously = (
                isinstance(event, ActExecutionRejected)
                and event.action_name == loop_action_name
        )
        # During the policy training there are no `ActExecutionRejected` events
        # which let us see whether we are within an unhappy path. Hence, we check if a
        # different action was executed instead of the loop after last user utterance.
        action_after_latest_user_utterance = (
            isinstance(event, UserUttered)
            and next_action_in_the_future is not None
            and next_action_in_the_future != loop_action_name
        )

        return loop_rejected_previously or action_after_latest_user_utterance

    @staticmethod
    def undo_till_prev_loop_execution(
        loop_action_name: Text, done_events: List[Event]
    ) -> None:
        off_set = 0
        for e in reversed(done_events[:]):
            if isinstance(e, ActionExecuted) and e.action_name == loop_action_name:
                break

            if isinstance(e, (ActionExecuted, UserUttered)):
                del done_events[-1 - off_set]
            else:
                # Remember events which aren't unfeaturized to get the index right
                off_set += 1

    def events_replay(self) -> None:
        """Update the tracker based on a list of events."""

        request_events = self.request_events()
        for event in request_events:
            event.apply(self)

    def recreate_from_dialogue(self, dialogue: Dialogue) -> None:
        """Use a serialised `Dialogue` to update the trackers state.

        This uses the state as is persisted in a ``TrackerStorage``. If the
        tracker is blank before calling this method, the final state will be
        identical to the tracker from which the dialogue was created."""

        if not isinstance(dialogue, Dialogue):
            raise ValueError(
                f"story {dialogue} is not of type Dialogue. "
                f"Have you deserialized it?"
            )

        self._reset()
        self.events.extend(dialogue.events)
        self.events_replay()

    def copy(self) -> "DialogueStateTracer":
        """Creates a duplicate of this tracker"""
        return self.travel_back_in_time(float("inf"))

    def travel_back_in_time(self, target_time: float) -> "DialogueStateTracer":
        """Creates a new tracker with a state at a specific timestamp.

        A new tracker will be created and all events previous to the
        passed time stamp will be replayed. Events that occur exactly
        at the target time will be included."""

        tracker = self.initialize_copy()

        for event in self.events:
            if event.timestamp <= target_time:
                tracker.update(event)
            else:
                break

        return tracker  # yields the final state

    def asDialogue(self) -> Dialogue:
        """Return a ``Dialogue`` object containing all of the turns.

        This can be serialised and later used to recover the state
        of this tracker exactly."""

        return Dialogue(self.sender_id, list(self.events))

    def update(self, event: Event, domain: Optional[Domain] = None) -> None:
        """Modify the state of the tracker according to an ``Event``. """
        if not isinstance(event, Event):  # pragma: no cover
            raise ValueError("event to log must be an instance of a subclass of Event.")

        self.events.append(event)
        event.apply(self)

        if domain and isinstance(event, UserUttered):
            # store all entities as slots
            for e in domain.entities_slots(event.parse_data["entities"]):
                self.update(e)

    def as_story(self, include_source: bool = False) -> "Story":
        """Dump the tracker as a story in the Convo Core story format.

        Returns the dumped tracker as a string."""
        from convo.shared.core.training_data.structures import Story

        story_name = (
            f"{self.sender_id} ({self.sender_source})"
            if include_source
            else self.sender_id
        )
        return Story.from_events_tracker(self.request_events(), story_name)

    def export_stories(
        self,
        writer: "StoryWriter",
        e2e: bool = False,
        include_source: bool = False,
        should_append_stories: bool = False,
    ) -> Text:
        """Dump the tracker as a story in the Convo Core story format.

        Returns:
            The dumped tracker as a string.
        """

        # TODO: we need to revisit all usages of this, the caller needs to specify
        #       the format. this likely points to areas where we are not properly
        #       handling markdown vs yaml
        story = self.as_story(include_source)

        return writer.data_dumps(
            story.story_steps, is_appendable=should_append_stories, is_test_story=e2e
        )

    def export_stories_to_file(self, export_path: Text = "debug_stories.yml") -> None:
        """Dump the tracker as a story to a file."""
        from convo.shared.core.training_data.story_writer.yaml_story_writer import (
            YAMLStoryAuthor,
        )

        append = not os.path.exists(export_path)

        convo.shared.utils.io.writing_text_file(
            self.export_stories(YAMLStoryAuthor()) + "\n", export_path, append=append
        )

    def get_last_event_for(
        self,
        EventType: Type[Event],
        action_names_to_exclude: List[Text] = None,
        skip: int = 0,
        event_verbosity: releaseVerbosity = releaseVerbosity.APPLIED,
    ) -> Optional[Event]:
        """Gets the last event of a given type which was actually applied.

        Args:
            EventType: The type of event you want to find.
            action_names_to_exclude: Events of type `ActionExecuted` which
                should be excluded from the results. Can be used to skip
                `action_listen` events.
            skip: Skips n possible results before return an event.
            event_verbosity: Which `releaseVerbosity` should be used to search for events.

        Returns:
            event which matched the query or `None` if no event matched.
        """

        to_exclude = action_names_to_exclude or []

        def filter_function(e: Event):
            has_instance = isinstance(e, EventType)
            excluded = isinstance(e, ActionExecuted) and e.action_name in to_exclude
            return has_instance and not excluded

        filtered = filter(
            filter_function, reversed(self.events_for_verbosity(event_verbosity) or [])
        )

        for i in range(skip):
            next(filtered, None)

        return next(filtered, None)

    def last_executed_action_has(self, name: Text, skip: int = 0) -> bool:
        """Returns whether last `ActionExecuted` event had a specific name.

        Args:
            name: Name of the event which should be matched.
            skip: Skips n possible results in between.

        Returns:
            `True` if last executed action had name `name`, otherwise `False`.
        """

        last: Optional[ActionExecuted] = self.get_last_event_for(
            ActionExecuted, action_names_to_exclude=[LISTEN_ACTION_NAME  ], skip=skip
        )
        return last is not None and last.action_name == name

    ###
    # Internal methods for the modification of the trackers state. Should
    # only be called by events, not directly. Rather update the tracker
    # with an event that in its ``apply_to`` method modifies the tracker.
    ###
    def _reset(self) -> None:
        """Reset tracker to initial state - doesn't delete events though!."""

        self.reset_slots()
        self._paused = False
        self.latest_action = {}
        self.latest_message = UserUttered.empty()
        self.latest_bot_utterance = BotUttered.empty()
        self.followup_action = LISTEN_ACTION_NAME  
        self.active_loop = {}

    def reset_slots(self) -> None:
        """Set all the convo_slotsto their initial value."""

        for slot in self.slots.values():
            slot.slot_reset()

    def set_slot(self, key: Text, value: Any) -> None:
        """Set the value of a slot if that slot exists."""

        if key in self.slots:
            self.slots[key].value = value
        else:
            log.error(
                f"Tried to set non existent slot '{key}'. Make sure you "
                f"added all your convo_slotsto your domain file."
            )

    def create_events(self, evts: List[Event]) -> Deque[Event]:

        if evts and not isinstance(evts[0], Event):  # pragma: no cover
            raise ValueError("events, if given, must be a list of events")
        return deque(evts, self._max_event_history)

    def __eq__(self, others) -> bool:
        if isinstance(self, type(others)):
            return others.events == self.events and self.sender_id == others.sender_id
        else:
            return False

    def __ne__(self, others) -> bool:
        return not self.__eq__(others)

    def trigger_follow_up_action(self, action: Text) -> None:
        """Triggers another action following the execution of the current."""

        self.followup_action = action

    def clear_follow_up_action(self) -> None:
        """Clears follow up action when it was executed."""

        self.followup_action = None

    def merge_slots(
        self, entities: Optional[List[Dict[Text, Any]]] = None
    ) -> List[SetofSlot]:
        """Take a list of entities and create tracker slot set events.

        If an entity type matches a convo_slotsname, the entities value is set
        as the convo_slotsvalue by creating a ``SetofSlot`` event.
        """

        entities = entities if entities else self.latest_message.entities
        newSlots= [
          SetofSlot(e["entity"], e["value"])
            for e in entities
            if e["entity"] in self.slots.keys()
        ]
        return newSlots

    # pytype: disable=bad-return-type
    @property
    def activeLoopName(self) -> Optional[Text]:
        """Get the name of the currently active loop.

        Returns: `None` if no active loop or the name of the currently active loop.
        """
        if not self.active_loop or self.active_loop.get(LOOPNAME  ) == NOT_SET   :
            return None

        return self.active_loop.get(LOOPNAME  )

    # pytype: enable=bad-return-type

    @property
    def latestActionName(self) -> Optional[Text]:
        """Get the name of the previously executed action or text of e2e action.

        Returns: name of the previously executed action or text of e2e action
        """
        return self.latest_action.get(ACT_NAME) or self.latest_action.get(
            ACT_TEXT
        )


def getActiveLoopName(state: fetch_state) -> Optional[Text]:
    """Get the name of current active loop.

    Args:
        state: The state from which the name of active loop should be extracted

    Return:
        the name of active loop or None
    """
    if (
        not state.get(CURRENT_LOOP   )
        or state[CURRENT_LOOP   ].get(LOOPNAME  ) == NOT_SET   
    ):
        return

    return state[CURRENT_LOOP   ].get(LOOPNAME  )


def isPrevActionListenInState(state: fetch_state) -> bool:
    """Check if action_listen is the previous executed action.

    Args:
        state: The state for which the check should be performed

    Return:
        boolean value indicating whether action_listen is previous action
    """
    prevActionName = state.get(PRECEDING_ACTION   , {}).get(ACT_NAME)
    return prevActionName == LISTEN_ACTION_NAME
