import json
import logging
import typing
from difflib import SequenceMatcher
from typing import List, Text, Tuple

import convo.cli.utils
import convo.shared.utils.cli
import convo.shared.utils.io
import convo.utils.io
from convo.cli import utils as cli_utils
from convo.shared.constants import CONVO_DEFAULT_SENDER_ID 
from convo.shared.core.constants import LISTEN_ACTION_NAME
from convo.core.channels import console
from convo.core.channels.channel import CollectOutputChannel, UserMsg
from convo.shared.core.domain import Domain
from convo.shared.core.events import ActionExecuted, UserUttered
from convo.shared.core.trackers import DialogueStateTracer

if typing.TYPE_CHECKING:
    from convo.core.agent import CoreAgent

log = logging.getLogger()  # get the root logger


def _check_forecast_range_with_story(
    last_prediction: List[Text], actions_between_utterances: List[Text]
) -> None:
    """Emit a warning if predictions do not align with expected actions."""

    q, b = range_list(last_prediction, actions_between_utterances)
    if q != b:
        convo.shared.utils.io.raising_warning(
            f"The model predicted different actions than the "
            f"model used to create the story! Expected: "
            f"{q} but got {b}."
        )


def range_list(
    predictions: List[Text], golds: List[Text]
) -> Tuple[List[Text], List[Text]]:
    """Align two lists trying to keep same elements at the same index.

    If lists contain different items at some indices, the algorithm will
    try to find the best alignment and pad with `None`
    values where necessary."""

    padded_forecast = []
    golds_padded = []
    t = SequenceMatcher(None, predictions, golds)

    for tag, i1, i2, j1, j2 in t.get_opcodes():
        padded_forecast.extend(predictions[i1:i2])
        padded_forecast.extend(["None"] * ((j2 - j1) - (i2 - i1)))

        golds_padded.extend(golds[j1:j2])
        golds_padded.extend(["None"] * ((i2 - i1) - (j2 - j1)))

    return padded_forecast, golds_padded


def act_since_last_utterance(tracker: DialogueStateTracer) -> List[Text]:
    """Extract all events after the most recent utterance from the user."""

    actions = []
    for e in reversed(tracker.events):
        if isinstance(e, UserUttered):
            break
        elif isinstance(e, ActionExecuted):
            actions.append(e.action_name)
    actions.reverse()
    return actions


async def events_replay(tracer: DialogueStateTracer, agent: "CoreAgent") -> None:
    """Take a tracker and replay the logged user utterances against an agent.

    During replaying of the user utterances, the executed actions and events
    created by the agent are compared to the logged ones of the tracker that
    is getting replayed. If they differ, a warning is logged.

    At the end, the tracker stored in the agent's tracker store for the
    same sender id will have quite the same state as the one
    that got replayed."""

    act_in_utterances = []
    last_chances = [LISTEN_ACTION_NAME  ]

    for i, event in enumerate(tracer.events_after_last_restart()):
        if isinstance(event, UserUttered):
            _check_forecast_range_with_story(
                last_chances, act_in_utterances
            )

            act_in_utterances = []
            convo.shared.utils.cli.printing_success(event.text)
            output = CollectOutputChannel()
            await agent.handle_txt(
                event.text, sender_id=tracer.sender_id, output_channel=output
            )
            for m in output.messages:
                btn = m.pop("buttons", None)  # for non-terminal stdin
                console.print_bot_result(m)

                if btn is not None:
                    colour = convo.shared.utils.io.bcolours.OK_BLUE
                    convo.shared.utils.cli.printing_color("Buttons:", color=colour)
                    for idx, button in enumerate(btn):
                        convo.shared.utils.cli.printing_color(
                            cli_utils.button_to_str(button, idx), color=colour
                        )

            tracer = agent.tracker_store.recover(tracer.sender_id)
            last_chances = act_since_last_utterance(tracer)

        elif isinstance(event, ActionExecuted):
            act_in_utterances.append(event.action_name)

    _check_forecast_range_with_story(last_chances, act_in_utterances)


def load_tracker_from_dict(tracker_dump: Text, domain: Domain) -> DialogueStateTracer:
    """Read the json dump from the file and instantiate a tracker it."""

    tracker_dict = json.loads(convo.shared.utils.io.read_file(tracker_dump))
    sender_id = tracker_dict.get("sender_id", CONVO_DEFAULT_SENDER_ID)
    return DialogueStateTracer.from_dict(
        sender_id, tracker_dict.get("events", []), domain.slots
    )
