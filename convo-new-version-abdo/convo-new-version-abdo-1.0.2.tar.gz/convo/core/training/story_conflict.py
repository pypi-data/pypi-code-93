from collections import defaultdict
import logging
from typing import Dict, Generator, List, NamedTuple, Optional, Text, Tuple

from convo.core.featurizers.tracker_featurizers import MaxHistoryTrackerFeaturizer
from convo.shared.core.constants import LISTEN_ACTION_NAME  
from convo.shared.core.domain import Domain, PREVIOUS_PREFIX , fetch_state
from convo.shared.core.events import ActionExecuted, Event
from convo.shared.core.generator import TrackerInCachedStates
from convo.shared.nlu.constants import INTENTION

log = logging.getLogger(__name__)


class StoryConflict:
    """Represents a conflict between two or more stories.

    Here, a conflict means that different actions are supposed to follow from
    the same dialogue state, which most policies cannot learn.
    """

    def __init__(self, sliced_states: List[fetch_state]) -> None:
        """
        Creates a `StoryConflict` from a given state.

        Args:
            sliced_states: The (sliced) dialogue state at which the conflict occurs.
        """

        self._sliced_states = sliced_states
        # A list of actions that all follow from the same state.
        self._conflicting_actions = defaultdict(
            list
        )  # {"action": ["story_1", ...], ...}

    def __hash__(self) -> int:
        return hash(str(list(self._sliced_states)))

    def add_dispute_act(self, action: Text, story_name: Text) -> None:
        """Adds another action that follows from the same state.

        Args:
            action: Name of the action.
            story_name: Name of the story where this action is chosen.
        """
        self._conflicting_actions[action] += [story_name]

    @property
    def disputed_acts(self) -> List[Text]:
        """List of conflicting actions.

        Returns:
            List of conflicting actions.

        """
        return list(self._conflicting_actions.keys())

    @property
    def disputed_has_prior_events(self) -> bool:
        """Checks if prior events exist.

        Returns:
            `True` if anything has happened before this conflict, otherwise `False`.
        """
        return _fetch_previous_event(self._sliced_states[-1])[0] is not None

    def __str__(self) -> Text:
        # Describe where the conflict occurs in the stories
        last_event_type, last_event_name = _fetch_previous_event(self._sliced_states[-1])
        if last_event_type:
            differences_msg = (
                f"Story structure conflict after {last_event_type} "
                f"'{last_event_name}':\n"
            )
        else:
            differences_msg = "Story structure conflict at the beginning of stories:\n"

        # List which stories are in conflict with one another
        for action, stories in self._conflicting_actions.items():
            differences_msg += (
                f"  {self._summarize_disputed_acts(action, stories)}"
            )

        return differences_msg

    @staticmethod
    def _summarize_disputed_acts(action: Text, stories: List[Text]) -> Text:
        """Gives a summarized textual description of where one action occurs.

        Args:
            action: The name of the action.
            stories: The stories in which the action occurs.

        Returns:
            A textural summary.
        """
        if len(stories) > 3:
            # Four or more stories are present
            differences_description = (
                f"'{stories[0]}', '{stories[1]}', and {len(stories) - 2} others trackers"
            )
        elif len(stories) == 3:
            differences_description = f"'{stories[0]}', '{stories[1]}', and '{stories[2]}'"
        elif len(stories) == 2:
            differences_description = f"'{stories[0]}' and '{stories[1]}'"
        elif len(stories) == 1:
            differences_description = f"'{stories[0]}'"
        else:
            raise ValueError(
                "An internal error occurred while trying to summarise a conflict "
                "without stories. Please file a bug report at "
                "https://github.com/ConvoHQ/convo."
            )

        return f"{action} predicted in {differences_description}\n"


class TracerEventStateTuple(NamedTuple):
    """Holds a tracker, an event, and sliced states associated with those."""

    tracker: TrackerInCachedStates
    event: Event
    sliced_states: List[fetch_state]

    @property
    def divide_segment_states_hash(self) -> int:
        return hash(str(list(self.sliced_states)))


def _get_length_of_longest_story(
    trackers: List[TrackerInCachedStates], domain: Domain
) -> int:
    """Returns the longest story in the given trackers.

    Args:
        trackers: Trackers to get stories from.
        domain: The domain.

    Returns:
        The maximal length of any story
    """
    return max([len(tracker.freeze_state(domain)) for tracker in trackers])


def find_story_difference(
    trackers: List[TrackerInCachedStates],
    domain: Domain,
    max_history: Optional[int] = None,
) -> List[StoryConflict]:
    """Generates `StoryConflict` objects, describing conflicts in the given trackers.

    Args:
        trackers: Trackers in which to search for conflicts.
        domain: The domain.
        max_history: The maximum history length to be taken into account.

    Returns:
        StoryConflict objects.
    """
    if not max_history:
        max_history = _get_length_of_longest_story(trackers, domain)

    log.info(f"Considering the preceding {max_history} turns for conflict analysis.")

    # We do this in two steps, to reduce memory consumption:

    # Create a 'state -> list of actions' dict, where the state is
    # represented by its hash
    conflicting_state_action_mapping = _find_different_states(
        trackers, domain, max_history
    )

    # Iterate once more over all states and note the (unhashed) state,
    # for which a conflict occurs
    conflicts = _build_different_from_states(
        trackers, domain, max_history, conflicting_state_action_mapping
    )

    return conflicts


def _find_different_states(
    trackers: List[TrackerInCachedStates], domain: Domain, max_history: int
) -> Dict[int, Optional[List[Text]]]:
    """Identifies all states from which different actions follow.

    Args:
        trackers: Trackers that contain the states.
        domain: The domain object.
        max_history: Number of turns to take into account for the state descriptions.

    Returns:
        A dictionary mapping state-hashes to a list of actions that follow from each state.
    """
    # Create a 'state -> list of actions' dict, where the state is
    # represented by its hash
    state_act_mapping = defaultdict(list)
    for element in _divide_segment_states_iterator(trackers, domain, max_history):
        hashed_state = element.divide_segment_states_hash
        if element.event.as_story_string() not in state_act_mapping[hashed_state]:
            state_act_mapping[hashed_state] += [element.event.as_story_string()]

    # Keep only conflicting `state_action_mapping`s
    return {
        state_hash: actions
        for (state_hash, actions) in state_act_mapping.items()
        if len(actions) > 1
    }


def _build_different_from_states(
    trackers: List[TrackerInCachedStates],
    domain: Domain,
    max_history: int,
    conflicting_state_action_mapping: Dict[int, Optional[List[Text]]],
) -> List["StoryConflict"]:
    """Builds a list of `StoryConflict` objects for each given conflict.

    Args:
        trackers: Trackers that contain the states.
        domain: The domain object.
        max_history: Number of turns to take into account for the state descriptions.
        conflicting_state_action_mapping: A dictionary mapping state-hashes to a list of actions
                                          that follow from each state.

    Returns:
        A list of `StoryConflict` objects that describe inconsistencies in the story
        structure. These objects also contain the history that leads up to the conflict.
    """
    # Iterate once more over all states and note the (unhashed) state,
    # for which a conflict occurs
    differences = {}
    for element in _divide_segment_states_iterator(trackers, domain, max_history):
        one_way_transformation_state = element.divide_segment_states_hash

        if one_way_transformation_state in conflicting_state_action_mapping:
            if one_way_transformation_state not in differences:
                differences[one_way_transformation_state] = StoryConflict(element.sliced_states)

            differences[one_way_transformation_state].add_dispute_act(
                action=element.event.as_story_string(),
                story_name=element.tracker.sender_id,
            )

    # Return list of conflicts that arise from unpredictable actions
    # (actions that start the conversation)
    return [
        conflict
        for (one_way_transformation_state, conflict) in differences.items()
        if conflict.disputed_has_prior_events
    ]


def _divide_segment_states_iterator(
    trackers: List[TrackerInCachedStates], domain: Domain, max_history: int
) -> Generator[TracerEventStateTuple, None, None]:
    """Creates an iterator over sliced states.

    Iterate over all given trackers and all sliced states within each tracker,
    where the slicing is based on `max_history`.

    Args:
        trackers: List of trackers.
        domain: Domain (used for tracker.past_states).
        max_history: Assumed `max_history` value for slicing.

    Yields:
        A (tracker, event, sliced_states) triplet.
    """
    for tracker in trackers:
        story_conflict_states = tracker.freeze_state(domain)

        story_conflict_idx = 0
        for event in tracker.events:
            if isinstance(event, ActionExecuted):
                sliced_states = MaxHistoryTrackerFeaturizer.slice_state_history(
                    story_conflict_states[: story_conflict_idx + 1], max_history
                )
                yield TracerEventStateTuple(tracker, event, sliced_states)
                story_conflict_idx += 1


def _fetch_previous_event(
    state: Optional[fetch_state],
) -> Tuple[Optional[Text], Optional[Text]]:
    """Returns previous event type and name.

    Returns the type and name of the event (action or intent) previous to the
    given state.

    Args:
        state: Element of sliced states.

    Returns:
        Tuple of (type, name) strings of the prior event.
    """

    before_event_type = None
    before_event_name = None

    if not state:
        return before_event_type, before_event_name

    # A typical state is, for example,
    # `{'prev_action_listen': 1.0, 'intent_greet': 1.0, 'slot_cuisine_0': 1.0}`.
    # We need to look out for `prev_` and `intent_` prefixes in the labels.
    for turn_label in state:
        if (
            turn_label.startswith(PREVIOUS_PREFIX )
            and turn_label.replace(PREVIOUS_PREFIX , "") != LISTEN_ACTION_NAME  
        ):
            # The `prev_...` was an action that was NOT `action_listen`
            return "action", turn_label.replace(PREVIOUS_PREFIX , "")
        elif turn_label.startswith(INTENTION + "_"):
            # We found an intent, but it is only the previous event if
            # the `prev_...` was `prev_action_listen`, so we don't return.
            before_event_type = "intent"
            before_event_name = turn_label.replace(INTENTION + "_", "")

    return before_event_type, before_event_name
