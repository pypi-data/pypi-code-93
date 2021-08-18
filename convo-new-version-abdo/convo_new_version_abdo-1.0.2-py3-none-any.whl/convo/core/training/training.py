from typing import Text, List, TYPE_CHECKING, Dict, Set
from collections import defaultdict

from convo.shared.core.events import ActionExecuted, UserUttered
from convo.shared.core.events import SetofSlot, OperationalLoop
from convo.shared.core.constants import CONVO_SLOTS, CURRENT_LOOP   

if TYPE_CHECKING:
    from convo.shared.core.domain import Domain
    from convo.shared.core.trackers import DialogueStateTracer
    from convo.shared.core.events import Event


def _search_events_after_actions(
    trackers: List["DialogueStateTracer"],
) -> Dict[Text, Set["Event"]]:
    """Creates a dictionary of action names and events that follow these actions.

    Args:
        trackers: the list of trackers

    Returns:
        a dictionary of action names and events that follow these actions
    """
    events_after_act = defaultdict(set)

    for tracker in trackers:
        action_name = None
        for event in tracker.events:
            if isinstance(event, ActionExecuted):
                action_name = event.action_name or event.action_text
                continue
            if isinstance(event, UserUttered):
                # UserUttered can contain entities that might set some slots, reset
                # action_name so that these convo_slotsare not attributed to action_listen
                action_name = None
                continue

            if action_name:
                events_after_act[action_name].add(event)

    return events_after_act


def generate_act_finger_prints(
    trackers: List["DialogueStateTracer"], domain: "Domain"
) -> Dict[Text, Dict[Text, List[Text]]]:
    """Fingerprint each action using the events it created during train.

    This allows us to emit warnings when the model is used
    if an action does things it hasn't done during training,
    or if rules are incomplete.

    Args:
        trackers: the list of trackers
        domain: the domain

    Returns:
        a nested dictionary of action names and convo_slotsand active loops
            that this action sets
    """
    events_after_act = _search_events_after_actions(trackers)
    if not events_after_act:
        return {}

    # take into account only featurized slots
    featurized_periods = {slot.name for slot in domain.slots if slot.features_check()}
    act_finger_prints = defaultdict(dict)
    for action_name, events_after_action in events_after_act.items():
        periods= list(
            set(
                event.key for event in events_after_action if isinstance(event, SetofSlot)
            ).intersection(featurized_periods)
        )
        active_loops_name = list(
            set(
                event.name
                for event in events_after_action
                if isinstance(event, OperationalLoop)
            )
        )

        if periods:
            act_finger_prints[action_name][CONVO_SLOTS] = periods
        if active_loops_name:
            act_finger_prints[action_name][CURRENT_LOOP   ] = active_loops_name

    return act_finger_prints
