import asyncio
import logging
import os
import tempfile
import textwrap
import uuid
from functools import partial
from multiprocessing import Process
from typing import Any, Callable, Dict, List, Optional, Text, Tuple, Union, Set


from sanic import Sanic, response
from sanic.exceptions import NotFound
from terminaltables import AsciiTable, SingleTable
import numpy as np
from aiohttp import ClientError
from colorclass import Color
import questionary
from questionary import Choice, Form, Question

from convo import telemetry
import convo.shared.utils.cli
import convo.shared.utils.io
import convo.cli.utils
import convo.shared.data
from convo.shared.nlu.constants import TXT, KEY_INTENT_NAME
from convo.shared.nlu.training_data.loading import MARKDOWN, CONVO, CONVO_YAML
from convo.shared.core.constants import (
    RESTART_USER_INTENT  ,
    LISTEN_ACTION_NAME  ,
    LOOPNAME  ,
    CURRENT_LOOP   ,
    LOOP_REJECTION,
    REQUESTED_SLOTS,
    LOOP_INTERRUPTION   ,
)
from convo.core import run, train, utils
from convo.core.constants import BY_DEFAULT_SERVER_FORMAT, BY_DEFAULT_SERVER_PORT
from convo.shared.core.domain import Domain
import convo.shared.core.events
from convo.shared.core.events import (
    ActionExecuted,
    ActReverted,
    BotUttered,
    Event,
    Restarted,
    UserUttered,
    UserChangeReverted,
)
import convo.core.interpreter
from convo.shared.constants import INTENT_MSG_PREFIX , CONVO_DEFAULT_SENDER_ID , CONVO_UTTER_PREFIX 
from convo.shared.core.trackers import releaseVerbosity, DialogueStateTracer
from convo.shared.core.training_data import visualization
from convo.shared.core.training_data.visualization import (
    visualizationTemplatePath,
    visualizeNeighborhood,
)
from convo.core.utils import AvailableEndpoints
from convo.shared.importers.convo import TrainingDataImporter
from convo.utils.common import updating_sanic_log_level
from convo.utils.endpoints import EndpointConfiguration

# noinspection PyProtectedMember
from convo.shared.nlu.training_data import loading
from convo.shared.nlu.training_data.message import Msg

# WARNING: This command line UI is using an external library
# communicating with the shell - these functions are hard to test
# automatically. If you change anything in here, please make sure to
# run the interactive learning and check if your part of the "ui"
# still works.
import convo.utils.io as io_utils

log = logging.getLogger(__name__)

MAXIMUM_VISUAL_HISTORY = 3

PATH_FLOW = {
    "stories": "data/stories.yml",
    "nlu": "data/nlu.yml",
    "backup": "data/nlu_interactive.yml",
    "domain": "domain.yml",
}

STORE_IN_E2E = False

# choose others intent, making sure this doesn't clash with an existing intent
ANOTHER_INTENT = uuid.uuid4().hex
OTHER_ACT = uuid.uuid4().hex
NEW_ACT = uuid.uuid4().hex

NEW_TEMPLATES_FILE = {}

MAXIMUM_NO_OF_TRAINING_STORY_FOR_VISUALIZATION = 200

BY_DEFAULT_STORY_GRAPH_FILE = "story_graph.dot"


class ResumeConversation(Exception):
    """Exception used to break out the flow and Restarted the conversation."""

    pass


class ForkTracer(Exception):
    """Exception used to break out the flow and fork at a previous step.

    The tracker will be reset to the selected point in the past and the
    conversation will continue from there."""

    pass


class RevertLastStep(Exception):
    """Exception used to break out the flow and undo the last step.

    The last step is either the most recent user message or the most
    recent action run by the bot."""

    pass


class Terminate(Exception):
    """Exception used to abort the interactive learning and exit."""

    pass


async def send_msg(
    endpoint: EndpointConfiguration,
    conversation_id: Text,
    message: Text,
    parse_data: Optional[Dict[Text, Any]] = None,
) -> Dict[Text, Any]:
    """Send a user message to a conversation."""

    pay_load = {
        "sender": UserUttered.type_name,
        "text": message,
        "parse_data": parse_data,
    }

    return await endpoint.request(
        json=pay_load,
        method="post",
        subpath=f"/conversations/{conversation_id}/messages",
    )


async def request_forecast(
    endpoint: EndpointConfiguration, conversation_id: Text
) -> Dict[Text, Any]:
    """Request the next action prediction from core."""

    return await endpoint.request(
        method="post", subpath=f"/conversations/{conversation_id}/predict"
    )


async def recover_domain(endpoint: EndpointConfiguration) -> Dict[Text, Any]:
    """Retrieve the domain from core."""

    return await endpoint.request(
        method="get", subpath="/domain", headers={"Accept": "application/json"}
    )


async def recover_status(endpoint: EndpointConfiguration) -> Dict[Text, Any]:
    """Retrieve the status from core."""

    return await endpoint.request(method="get", subpath="/status")


async def recover_tracker(
    endpoint: EndpointConfiguration,
    conversation_id: Text,
    verbosity: releaseVerbosity = releaseVerbosity.ALL,
) -> Dict[Text, Any]:
    """Retrieve a tracker from core."""

    path_flow = f"/conversations/{conversation_id}/tracker?include_events={verbosity.name}"
    return await endpoint.request(
        method="get", subpath=path_flow, headers={"Accept": "application/json"}
    )


async def send_act(
    endpoint: EndpointConfiguration,
    conversation_id: Text,
    action_name: Text,
    policy: Optional[Text] = None,
    confidence: Optional[float] = None,
    is_new_action: bool = False,
) -> Dict[Text, Any]:
    """Log an action to a conversation."""

    pay_load = ActionExecuted(action_name, policy, confidence).as_dictionary()

    sub_path_flow = f"/conversations/{conversation_id}/execute"

    try:
        return await endpoint.request(json=pay_load, method="post", subpath=sub_path_flow)
    except ClientError:
        if is_new_action:
            if action_name in NEW_TEMPLATES_FILE:
                warning_questions = questionary.confirm(
                    f"WARNING: You have created a new action: '{action_name}', "
                    f"with matching response: '{[*NEW_TEMPLATES_FILE[action_name]][0]}'. "
                    f"This action will not return its message in this session, "
                    f"but the new response will be saved to your domain file "
                    f"when you exit and save this session. "
                    f"You do not need to do anything further."
                )
                await _ask_ques(warning_questions, conversation_id, endpoint)
            else:
                warning_questions = questionary.confirm(
                    f"WARNING: You have created a new action: '{action_name}', "
                    f"which was not successfully executed. "
                    f"If this action does not return any events, "
                    f"you do not need to do anything. "
                    f"If this is a custom action which returns events, "
                    f"you are recommended to implement this action "
                    f"in your action server and try again."
                )
                await _ask_ques(warning_questions, conversation_id, endpoint)

            pay_load = ActionExecuted(action_name).as_dictionary()
            return await dispatch_event(endpoint, conversation_id, pay_load)
        else:
            log.error("failed to execute action!")
            raise


async def dispatch_event(
    endpoint: EndpointConfiguration,
    conversation_id: Text,
    evt: Union[List[Dict[Text, Any]], Dict[Text, Any]],
) -> Dict[Text, Any]:
    """Log an event to a conversation."""

    subpath = f"/conversations/{conversation_id}/tracker/events"

    return await endpoint.request(json=evt, method="post", subpath=subpath)


def format_bot_result(message: BotUttered) -> Text:
    """Format a bot response to be displayed in the history table."""

    # First, add text to output
    result = message.text or ""

    # Then, append all additional items
    data_set = message.data or {}
    if not data_set:
        return result

    if data_set.get("image"):
        result += "\nImage: " + data_set.get("image")

    if data_set.get("attachment"):
        result += "\nAttachment: " + data_set.get("attachment")

    if data_set.get("buttons"):
        result += "\nButtons:"
        choices = convo.cli.utils.button_choices_from_msg_data_set(
            data_set, allow_free_text_input=True
        )
        for choice in choices:
            result += "\n" + choice

    if data_set.get("elements"):
        result += "\nElements:"
        for idx, element in enumerate(data_set.get("elements")):
            element_str = convo.cli.utils.element_to_str(element, idx)
            result += "\n" + element_str

    if data_set.get("quick_replies"):
        result += "\nQuick replies:"
        for idx, element in enumerate(data_set.get("quick_replies")):
            element_str = convo.cli.utils.element_to_str(element, idx)
            result += "\n" + element_str
    return result


def latest_user_msg(events: List[Dict[Text, Any]]) -> Optional[Dict[Text, Any]]:
    """Return most recent user message."""

    for i, e in enumerate(reversed(events)):
        if e.get("event") == UserUttered.type_name:
            return e
    return None


def all_events_before_latest_user_messages(
    events: List[Dict[Text, Any]]
) -> List[Dict[Text, Any]]:
    """Return all events that happened before the most recent user message."""

    for i, e in enumerate(reversed(events)):
        if e.get("event") == UserUttered.type_name:
            return events[: -(i + 1)]
    return events


async def _ask_ques(
    questions: Union[Form, Question],
    conversation_id: Text,
    endpoint: EndpointConfiguration,
    is_abort: Callable[[Dict[Text, Any]], bool] = lambda x: False,
) -> Any:
    """Ask the user a question, if Ctrl-C is pressed provide user with menu."""

    shall_retry = True
    ans = {}

    while shall_retry:
        ans = questions.ask()
        if ans is None or is_abort(ans):
            shall_retry = await _query_if_quit(conversation_id, endpoint)
        else:
            shall_retry = False
    return ans


def _selection_choices_from_intent_forecast(
    predictions: List[Dict[Text, Any]]
) -> List[Dict[Text, Any]]:
    """Given a list of ML predictions create a UI choice list."""

    cached_intents = sorted(
        predictions, key=lambda k: (-k["confidence"], k[KEY_INTENT_NAME])
    )

    alternatives = []
    for p in cached_intents:
        name_with_belief = (
            f'{p.get("confidence"):03.2f} {p.get(KEY_INTENT_NAME):40}'
        )
        alternative = {
            KEY_INTENT_NAME: name_with_belief,
            "value": p.get(KEY_INTENT_NAME),
        }
        alternatives.append(alternative)

    return alternatives


async def _request_free_txt_intent(
    conversation_id: Text, endpoint: EndpointConfiguration
) -> Text:
    ques = questionary.text(
        message="Please type the intent name:",
        validate=io_utils.not_empty_validation("Please enter an intent name"),
    )
    return await _ask_ques(ques, conversation_id, endpoint)


async def _request_free_txt_act(
    conversation_id: Text, endpoint: EndpointConfiguration
) -> Text:
    ques = questionary.text(
        message="Please type the action name:",
        validate=io_utils.not_empty_validation("Please enter an action name"),
    )
    return await _ask_ques(ques, conversation_id, endpoint)


async def _request_free_text_utterance(
    conversation_id: Text, endpoint: EndpointConfiguration, action: Text
) -> Text:

    ques = questionary.text(
        message=(f"Please type the message for your new bot response '{action}':"),
        validate=io_utils.not_empty_validation("Please enter a response"),
    )
    return await _ask_ques(ques, conversation_id, endpoint)


async def _request_selection_from_objective(
    convo_intents: List[Dict[Text, Text]], conversation_id: Text, endpoint: EndpointConfiguration
) -> Text:
    question = questionary.select("What intent is it?", choices=convo_intents)
    return await _ask_ques(question, conversation_id, endpoint)


async def _request_split_point_from_list(
    forks: List[Dict[Text, Text]], conversation_id: Text, endpoint: EndpointConfiguration
) -> Text:
    question = questionary.select(
        "Before which user message do you want to fork?", choices=forks
    )
    return await _ask_ques(question, conversation_id, endpoint)


async def _request_split_from_user(
    conversation_id, endpoint
) -> Optional[List[Dict[Text, Any]]]:
    """Take in a conversation and ask at which point to fork the conversation.

    Returns the list of events that should be kept. Forking means, the
    conversation will be reset and continued from this previous point."""

    get_tracker = await recover_tracker(
        endpoint, conversation_id, releaseVerbosity.AFTER_RESTART
    )

    alternatives = []
    for i, e in enumerate(get_tracker.get("events", [])):
        if e.get("event") == UserUttered.type_name:
            alternatives.append({"name": e.get("text"), "value": i})

    fork_idx = await _request_split_point_from_list(
        list(reversed(alternatives)), conversation_id, endpoint
    )

    if fork_idx is not None:
        return get_tracker.get("events", [])[: int(fork_idx)]
    else:
        return None


async def _request_objective_from_user(
    latest_message, convo_intents, conversation_id, endpoint
) -> Dict[Text, Any]:
    """Take in latest message and ask which intent it should have been.

    Returns the intent dict that has been selected by the user."""

    forecast = latest_message.get("parse_data", {}).get("intent_ranking", [])

    forecast_intents = {p[KEY_INTENT_NAME] for p in forecast}

    for i in convo_intents:
        if i not in forecast_intents:
            forecast.append({KEY_INTENT_NAME: i, "confidence": 0.0})

    # convert convo_intents to ui list and add <others> as a free text alternative
    alternatives = [
        {KEY_INTENT_NAME: "<create_new_intent>", "value": ANOTHER_INTENT}
    ] + _selection_choices_from_intent_forecast(forecast)

    intent_names = await _request_selection_from_objective(
        alternatives, conversation_id, endpoint
    )

    if intent_names == ANOTHER_INTENT:
        intent_names = await _request_free_txt_intent(conversation_id, endpoint)
        selected_intent = {KEY_INTENT_NAME: intent_names, "confidence": 1.0}
    else:
        # returns the selected intent with the original probability value
        selected_intent = next(
            (x for x in forecast if x[KEY_INTENT_NAME] == intent_names),
            {KEY_INTENT_NAME: None},
        )

    return selected_intent


async def _print_record(conversation_id: Text, endpoint: EndpointConfiguration) -> None:
    """Print information about the conversation for the user."""

    tracker_store = await recover_tracker(
        endpoint, conversation_id, releaseVerbosity.AFTER_RESTART
    )
    act = tracker_store.get("events", [])

    table = _chat_record_table(act)
    slot_str = _slot_record(tracker_store)

    print("------")
    print("Chat History\n")
    print(table)

    if slot_str:
        print("\n")
        print(f"Current slots: \n\t{', '.join(slot_str)}\n")

    print("------")


def _chat_record_table(events: List[Dict[Text, Any]]) -> Text:
    """Create a table containing bot and user messages.

    Also includes additional information, like any events and
    prediction probabilities."""

    def wrap_up(txt: Text, max_width: int) -> Text:
        return "\n".join(textwrap.wrap(txt, max_width, replace_whitespace=False))

    def coloured(txt: Text, color: Text) -> Text:
        return "{" + color + "}" + txt + "{/" + color + "}"

    def format_user_message(user_event: UserUttered, max_width: int) -> Text:
        intent = user_event.intent or {}
        name_of_intent = intent.get(KEY_INTENT_NAME, "")
        _confidence = intent.get("confidence", 1.0)
        _md = _as_md_msg(user_event.parse_data)

        _line_no = [
            coloured(wrap_up(_md, max_width), "hired"),
            f"intent: {name_of_intent} {_confidence:03.2f}",
        ]
        return "\n".join(_line_no)

    def bot_breadth(_table: AsciiTable) -> int:
        return _table.column_max_width(1)

    def user_breadth(_table: AsciiTable) -> int:
        return _table.column_max_width(3)

    def addtional_bot_cell(data, cell):
        data.append([len(data), Color(cell), "", ""])

    def additional_user_cell(data, cell):
        data.append([len(data), "", "", Color(cell)])

    # prints the historical interactions between the bot and the user,
    # to help with correctly identifying the action
    table_data_set = [
        [
            "#  ",
            Color(coloured("Bot      ", "autoblue")),
            "  ",
            Color(coloured("You       ", "hired")),
        ]
    ]

    table_name = SingleTable(table_data_set, "Chat History")

    bot_column_name = []

    tracer = DialogueStateTracer.from_dict("any", events)
    request_events = tracer.request_events()

    for idx, event in enumerate(request_events):
        if isinstance(event, ActionExecuted):
            bot_column_name.append(coloured(event.action_name, "autocyan"))
            if event.confidence is not None:
                bot_column_name[-1] += coloured(f" {event.confidence:03.2f}", "autowhite")

        elif isinstance(event, UserUttered):
            if bot_column_name:
                txt = "\n".join(bot_column_name)
                addtional_bot_cell(table_data_set, txt)
                bot_column_name = []

            messages = format_user_message(event, user_breadth(table_name))
            additional_user_cell(table_data_set, messages)

        elif isinstance(event, BotUttered):
            wrap_up_ = wrap_up(format_bot_result(event), bot_breadth(table_name))
            bot_column_name.append(coloured(wrap_up_, "autoblue"))

        else:
            if event.as_story_string():
                bot_column_name.append(wrap_up(event.as_story_string(), bot_breadth(table_name)))

    if bot_column_name:
        txt = "\n".join(bot_column_name)
        addtional_bot_cell(table_data_set, txt)

    table_name.inner_heading_row_border = False
    table_name.inner_row_border = True
    table_name.inner_column_border = False
    table_name.outer_border = False
    table_name.justify_columns = {0: "left", 1: "left", 2: "center", 3: "right"}

    return table_name.table


def _slot_record(tracker_dump: Dict[Text, Any]) -> List[Text]:
    """Create an array of slot representations to be displayed."""

    slot_str = []
    for k, s in tracker_dump.get("slots", {}).items():
        colored_value = convo.shared.utils.io.wrapping_with_color(
            str(s), color=convo.shared.utils.io.bcolours.WARN
        )
        slot_str.append(f"{k}: {colored_value}")
    return slot_str


def _retry_on_err(
    func: Callable, export_path: Text, *args: Any, **kwargs: Any
) -> None:
    while True:
        try:
            return func(export_path, *args, **kwargs)
        except OSError as e:
            ans = questionary.confirm(
                f"Failed to export '{export_path}': {e}. Please make sure 'convo' "
                f"has read and write access to this file. Would you like to retry?"
            ).ask()
            if not ans:
                raise e


async def _write_data_set_to_file(conversation_id: Text, endpoint: EndpointConfiguration):
    """Write stories and nlu data to file."""

    story_path_flow, nlu_path_flow, domain_path_flow = _request_export_information()

    tracer = await recover_tracker(endpoint, conversation_id)
    events_name = tracer.get("events", [])

    serialised_domain_name = await recover_domain(endpoint)
    domain_name = Domain.from_dict(serialised_domain_name)

    _retry_on_err(_write_story_to_file, story_path_flow, events_name, domain_name)
    _retry_on_err(_write_nlu_to_file_name, nlu_path_flow, events_name)
    _retry_on_err(_write_domain_to_file_name, domain_path_flow, events_name, domain_name)

    log.info("Successfully wrote stories and NLU data")


async def _query_if_quit(conversation_id: Text, endpoint: EndpointConfiguration) -> bool:
    """Display the exit menu.

    Return `True` if the previous question should be retried."""

    ans = questionary.select(
        message="Do you want to stop?",
        choices=[
            Choice("Continue", "continue"),
            Choice("Undo Last", "undo"),
            Choice("Fork", "fork"),
            Choice("Start Fresh", "restart"),
            Choice("Export & Quit", "quit"),
        ],
    ).ask()

    if not ans or ans == "quit":
        # this is also the default answer if the user presses Ctrl-C
        await _write_data_set_to_file(conversation_id, endpoint)
        raise Terminate()
    elif ans == "continue":
        # in this case we will just return, and the original
        # question will get asked again
        return True
    elif ans == "undo":
        raise RevertLastStep()
    elif ans == "fork":
        raise ForkTracer()
    elif ans == "restart":
        raise ResumeConversation()


async def _request_act_from_user(
    predictions: List[Dict[Text, Any]], conversation_id: Text, endpoint: EndpointConfiguration
) -> Tuple[Text, bool]:
    """Ask the user to correct an action prediction."""

    await _print_record(conversation_id, endpoint)

    alternatives = [
        {
            "name": f'{a.get("score"):03.2f} {a.get("action"):40}',
            "value": a.get("action"),
        }
        for a in predictions
    ]

    tracer = await recover_tracker(endpoint, conversation_id)
    events_name = tracer.get("events", [])

    session_act_all = [a["name"] for a in _collect_act(events_name)]
    session_act_unique = list(set(session_act_all))
    old_act = [action["value"] for action in alternatives]
    new_act = [
        {"name": action, "value": OTHER_ACT + action}
        for action in session_act_unique
        if action not in old_act
    ]
    alternatives = (
            [{"name": "<create new action>", "value": NEW_ACT}] + new_act + alternatives
    )
    ques = questionary.select("What is the next action of the bot?", alternatives)

    action_name = await _ask_ques(ques, conversation_id, endpoint)
    is_new_act = action_name == NEW_ACT

    if is_new_act:
        # create new action
        action_name = await _request_free_txt_act(conversation_id, endpoint)
        if action_name.startswith(CONVO_UTTER_PREFIX ):
            utter_message = await _request_free_text_utterance(
                conversation_id, endpoint, action_name
            )
            NEW_TEMPLATES_FILE[action_name] = {utter_message: ""}

    elif action_name[:32] == OTHER_ACT:
        # action was newly created in the session, but not this turn
        is_new_act = True
        action_name = action_name[32:]

    print(f"Thanks! The bot will now run {action_name}.\n")
    return action_name, is_new_act


def _request_export_information() -> Tuple[Text, Text, Text]:
    import convo.shared.data

    """Request file path and export stories & nlu data to that path"""

    # export training data and quit
    quest = questionary.form(
        export_stories=questionary.text(
            message="Export stories to (if file exists, this "
            "will append the stories)",
            default=PATH_FLOW["stories"],
            validate=io_utils.file_type_validation(
                convo.shared.data.MARK_DOWN_FILE_EXTENSIONS
                + convo.shared.data.CONVO_YAML_FILE_EXTENSIONS,
                "Please provide a valid export path for the stories, "
                "e.g. 'stories.yml'.",
            ),
        ),
        export_nlu=questionary.text(
            message="Export NLU data to (if file exists, this will "
            "merge learned data with previous training examples)",
            default=PATH_FLOW["nlu"],
            validate=io_utils.file_type_validation(
                list(convo.shared.data.TRAINING_DATA_FILE_EXTENSIONS),
                "Please provide a valid export path for the NLU data, "
                "e.g. 'nlu.yml'.",
            ),
        ),
        export_domain=questionary.text(
            message="Export domain file to (if file exists, this "
            "will be overwritten)",
            default=PATH_FLOW["domain"],
            validate=io_utils.file_type_validation(
                convo.shared.data.CONVO_YAML_FILE_EXTENSIONS,
                "Please provide a valid export path for the domain file, "
                "e.g. 'domain.yml'.",
            ),
        ),
    )

    ans = quest.ask()
    if not ans:
        raise Terminate()

    return ans["export_stories"], ans["export_nlu"], ans["export_domain"]


def _split_conversation_at_resume(
    events: List[Dict[Text, Any]]
) -> List[List[Dict[Text, Any]]]:
    """Split a conversation at Restarted events.

    Returns an array of event lists, without the Restarted events."""

    sub_chats = []
    present = []
    for e in events:
        if e.get("event") == "restart":
            if present:
                sub_chats.append(present)
            present = []
        else:
            present.append(e)

    if present:
        sub_chats.append(present)

    return sub_chats


def _collect_msg(events: List[Dict[Text, Any]]) -> List[Msg]:
    """Collect the message text and parsed data from the UserMsg events
    into a list"""

    import convo.shared.nlu.training_data.util as convo_nlu_training_data_utils

    msg_ = []

    for event in events:
        if event.get("event") == UserUttered.type_name:
            data = event.get("parse_data", {})
            convo_nlu_training_data_utils.remove_untrainable_entities(data)
            msg = Msg.building(
                data["text"], data["intent"][KEY_INTENT_NAME], data["entities"]
            )
            msg_.append(msg)
        elif event.get("event") == UserChangeReverted.type_name and msg_:
            msg_.pop()  # user corrected the nlu, remove incorrect example

    return msg_


def _collect_act(events: List[Dict[Text, Any]]) -> List[Dict[Text, Any]]:
    """Collect all the `ActionExecuted` events into a list."""

    return [evt for evt in events if evt.get("event") == ActionExecuted.type_name]


def _write_story_to_file(
    export_story_path: Text, events: List[Dict[Text, Any]], domain: Domain
) -> None:
    """Write the conversation of the conversation_id to the file convo_paths."""
    from convo.shared.core.training_data.story_reader.yaml_story_reader import (
        YAMLStoryReviewer,
    )
    from convo.shared.core.training_data.story_writer.yaml_story_writer import (
        YAMLStoryAuthor,
    )
    from convo.shared.core.training_data.story_writer.markdown_story_writer import (
        MarkdownStoryAuthor,
    )

    sub_chats = _split_conversation_at_resume(events)

    io_utils.creating_path(export_story_path)

    if convo.shared.data.is_yaml_file (export_story_path):
        writer = YAMLStoryAuthor()
    else:
        writer = MarkdownStoryAuthor()

    should_add_story = False
    if os.path.exists(export_story_path):
        add_write = "a"  # append if already exists
        should_add_story = True
    else:
        add_write = "w"  # make a new file if not

    with open(
        export_story_path, add_write, encoding=convo.shared.utils.io.ENCODING_DEFAULT
    ) as f:
        j = 1
        for conversation in sub_chats:
            analysed_events = convo.shared.core.events.deserialized_events(conversation)
            tracer = DialogueStateTracer.from_events_tracker(
                f"interactive_story_{j}", evts=analysed_events, slots=domain.slots
            )

            if any(
                isinstance(event, UserUttered) for event in tracer.request_events()
            ):
                j += 1
                f.write(
                    "\n"
                    + tracer.export_stories(
                        writer=writer,
                        should_append_stories=should_add_story,
                        e2e=STORE_IN_E2E,
                    )
                )


def _filter_msg(msgs: List[Msg]) -> List[Msg]:
    """Filter messages removing those that start with INTENT_MSG_PREFIX """

    filtered_msg = []
    for msg in msgs:
        if not msg.get(TXT).startswith(INTENT_MSG_PREFIX ):
            filtered_msg.append(msg)
    return filtered_msg


def _write_nlu_to_file_name(export_nlu_path: Text, events: List[Dict[Text, Any]]) -> None:
    """Write the nlu data of the conversation_id to the file convo_paths."""
    from convo.shared.nlu.training_data.training_data import TrainingDataSet

    messages = _collect_msg(events)
    messages = _filter_msg(messages)

    # noinspection PyBroadException
    try:
        previous_eg = loading.load_data_set(export_nlu_path)
    except Exception as e:
        log.debug(
            f"An exception occurred while trying to load the NLU data. {str(e)}"
        )
        # No previous file exists, use empty training data as replacement.
        previous_eg = TrainingDataSet()

    nlu_data_set = previous_eg.merge(TrainingDataSet(messages))

    # need to guess the format of the file before opening it to avoid a read
    # in a write
    nlu_format_style = _fetch_nlu_target_format(export_nlu_path)
    if nlu_format_style == CONVO_YAML:
        stringified_training_data_set = nlu_data_set.nlu_yaml()
    elif nlu_format_style == MARKDOWN:
        stringified_training_data_set = nlu_data_set.nlu_markdown()
    else:
        stringified_training_data_set = nlu_data_set.nlu_json()

    convo.shared.utils.io.writing_text_file(stringified_training_data_set, export_nlu_path)


def _fetch_nlu_target_format(export_path: Text) -> Text:
    predict_format = loading.guessing_format(export_path)

    if predict_format not in {MARKDOWN, CONVO, CONVO_YAML}:
        if convo.shared.data.is_json_file (export_path):
            predict_format = CONVO
        elif convo.shared.data.is_mark_down_file (export_path):
            predict_format = MARKDOWN
        elif convo.shared.data.is_yaml_file (export_path):
            predict_format = CONVO_YAML

    return predict_format


def _entities_from_msg(messages: List[Msg]) -> List[Text]:
    """Return all entities that occur in at least one of the messages."""
    return list({e["entity"] for m in messages for e in m.data.get("entities", [])})


def _intents_from_msg(messages: List[Msg]) -> Set[Text]:
    """Return all convo_intents that occur in at least one of the messages."""

    # set of distinct convo_intents
    different_intents = {m.data["intent"] for m in messages if "intent" in m.data}

    return different_intents


def _write_domain_to_file_name(
    domain_path: Text, events: List[Dict[Text, Any]], old_domain: Domain
) -> None:
    """Write an updated domain file to the file path."""

    io_utils.creating_path(domain_path)

    msg = _collect_msg(events)
    act = _collect_act(events)
    get_templates = NEW_TEMPLATES_FILE  # type: Dict[Text, List[Dict[Text, Any]]]

    # TODO for now there is no way to distinguish between action and form
    collected_act = list(
        {
            e["name"]
            for e in act
            if e["name"] not in convo.shared.core.constants.DEFAULT_ACTION_NAME   
            and e["name"] not in old_domain.form_names
        }
    )

    new_domain_name = Domain(
        convo_intents=_intents_from_msg(msg),
        entities=_entities_from_msg(msg),
        slots=[],
        templates=get_templates,
        action_names=collected_act,
        forms=[],
    )

    old_domain.merge(new_domain_name).persist_trash(domain_path)


async def _forecast_till_next_listen(
    endpoint: EndpointConfiguration,
    conversation_id: Text,
    conversation_ids: List[Text],
    plot_file: Optional[Text],
) -> None:
    """Predict and validate actions until we need to wait for a user message."""

    pay_attention = False
    while not pay_attention:
        output = await request_forecast(endpoint, conversation_id)
        forecast = output.get("scores")
        chances = [prediction["score"] for prediction in forecast]
        forecast_output = int(np.argmax(chances))
        action_name = forecast[forecast_output].get("action")
        policies = output.get("policy")
        conf = output.get("confidence")

        await _print_record(conversation_id, endpoint)
        await _deploye_trackers(
            conversation_ids,
            plot_file,
            endpoint,
            unconfirmed=[ActionExecuted(action_name)],
        )

        pay_attention = await _validate_act(
            action_name, policies, conf, forecast, endpoint, conversation_id
        )

        await _deploye_trackers(conversation_ids, plot_file, endpoint)

    tracker_dump = await recover_tracker(
        endpoint, conversation_id, releaseVerbosity.AFTER_RESTART
    )
    events_name = tracker_dump.get("events", [])

    if len(events_name) >= 2:
        end_event = events_name[-2]  # last event before action_listen

        # if bot message includes buttons the user will get a list choice to reply
        # the list choice is displayed in place of action listen
        if end_event.get("event") == BotUttered.type_name and end_event["data"].get(
            "buttons", None
        ):
            user_select_option = _fetch_button_choice(end_event)
            if user_select_option != convo.cli.utils.FREE_TEXT_INSERT_PROMPT:
                await send_msg(endpoint, conversation_id, user_select_option)


def _fetch_button_choice(last_event: Dict[Text, Any]) -> Text:
    data_set = last_event["data"]
    msg = last_event.get("text", "")

    alternatives = convo.cli.utils.button_choices_from_msg_data_set(
        data_set, allow_free_text_input=True
    )
    quest = questionary.select(msg, alternatives)
    return convo.cli.utils.payload_from_button_ques(quest)


async def _right_wrong_nlu(
    corrected_nlu: Dict[Text, Any],
    events: List[Dict[Text, Any]],
    endpoint: EndpointConfiguration,
    conversation_id: Text,
) -> None:
    """A wrong NLU prediction got corrected, update core's tracker."""

    undo_latest_user_utterance = UserChangeReverted().as_dictionary()
    # `UserChangeReverted` also removes the `ACTION_LISTEN` event before, hence we
    # have to replay it.
    listen_for_next_msg = ActionExecuted(LISTEN_ACTION_NAME  ).as_dictionary()
    corrected_msg = latest_user_msg(events)

    if corrected_msg is None:
        raise Exception("Failed to correct NLU data. User message not found.")

    corrected_msg["parse_data"] = corrected_nlu
    await dispatch_event(
        endpoint,
        conversation_id,
        [undo_latest_user_utterance, listen_for_next_msg, corrected_msg],
    )


async def _right_wrong_act(
    corrected_action: Text,
    endpoint: EndpointConfiguration,
    conversation_id: Text,
    is_new_action: bool = False,
) -> None:
    """A wrong action prediction got corrected, update core's tracker."""

    await send_act(
        endpoint, conversation_id, corrected_action, is_new_action=is_new_action
    )


def _is_form_rejected(action_name: Text, tracker: Dict[Text, Any]) -> bool:
    """Check if the form got rejected with the most recent action name."""
    return (
        tracker.get(CURRENT_LOOP   , {}).get(LOOPNAME  )
        and action_name != tracker[CURRENT_LOOP   ][LOOPNAME  ]
        and action_name != LISTEN_ACTION_NAME  
    )


def _is_form_restored(action_name: Text, tracker: Dict[Text, Any]) -> bool:
    """Check whether the form is called again after it was rejected."""
    return (
        tracker.get(CURRENT_LOOP   , {}).get(LOOP_REJECTION)
        and tracker.get("latest_action_name") == LISTEN_ACTION_NAME  
        and action_name == tracker.get(CURRENT_LOOP   , {}).get(LOOPNAME  )
    )


async def _confirm_form_authentication(
    action_name, tracker, endpoint, conversation_id
) -> None:
    """Ask a user whether an input for a form should be validated.

    Previous to this call, the active form was chosen after it was rejected."""

    requested_slot = tracker.get("slots", {}).get(REQUESTED_SLOTS)

    verify_ques = questionary.confirm(
        f"Should '{action_name}' validate user input to fill "
        f"the slot '{requested_slot}'?"
    )
    verify_input = await _ask_ques(
        verify_ques, conversation_id, endpoint
    )

    if not verify_input:
        # notify form action to skip validation
        await dispatch_event(
            endpoint,
            conversation_id,
            {
                "event": convo.shared.core.events.LoopHindered.type_name,
                LOOP_INTERRUPTION   : True,
            },
        )

    elif tracker.get(CURRENT_LOOP   , {}).get(LOOP_INTERRUPTION   ):
        # handle contradiction with learned behaviour
        warning_ques = questionary.confirm(
            "ERROR: FormPolicy predicted no form validation "
            "based on previous training stories. "
            "Make sure to remove contradictory stories "
            "from training data. "
            "Otherwise predicting no form validation "
            "will not work as expected."
        )

        await _ask_ques(warning_ques, conversation_id, endpoint)
        # notify form action to validate an input
        await dispatch_event(
            endpoint,
            conversation_id,
            {
                "event": convo.shared.core.events.LoopHindered.type_name,
                LOOP_INTERRUPTION   : False,
            },
        )


async def _validate_act(
    action_name: Text,
    policy: Text,
    confidence: float,
    predictions: List[Dict[Text, Any]],
    endpoint: EndpointConfiguration,
    conversation_id: Text,
) -> bool:
    """Query the user to validate if an action prediction is correct.

    Returns `True` if the prediction is correct, `False` otherwise."""

    ques = questionary.confirm(f"The bot wants to run '{action_name}', correct?")

    is_right = await _ask_ques(ques, conversation_id, endpoint)

    if not is_right:
        action_name, is_new_act = await _request_act_from_user(
            predictions, conversation_id, endpoint
        )
    else:
        is_new_act = False

    tracer = await recover_tracker(
        endpoint, conversation_id, releaseVerbosity.AFTER_RESTART
    )

    if _is_form_rejected(action_name, tracer):
        # notify the tracker that form was rejected
        await dispatch_event(
            endpoint,
            conversation_id,
            {
                "event": "action_execution_rejected",
                LOOPNAME  : tracer[CURRENT_LOOP   ][LOOPNAME  ],
            },
        )

    elif _is_form_restored(action_name, tracer):
        await _confirm_form_authentication(action_name, tracer, endpoint, conversation_id)

    if not is_right:
        await _right_wrong_act(
            action_name, endpoint, conversation_id, is_new_action=is_new_act
        )
    else:
        await send_act(endpoint, conversation_id, action_name, policy, confidence)

    return action_name == LISTEN_ACTION_NAME


def _as_md_msg(parse_data: Dict[Text, Any]) -> Text:
    """Display the parse data of a message in markdown format."""
    from convo.shared.nlu.training_data.formats.readerwriter import TrainingDataAuthor

    if parse_data.get("text", "").startswith(INTENT_MSG_PREFIX ):
        return parse_data["text"]

    if not parse_data.get("entities"):
        parse_data["entities"] = []

    return TrainingDataAuthor.generate_msg(parse_data)


def _authenticate_user_regex(latest_message: Dict[Text, Any], convo_intents: List[Text]) -> bool:
    """Validate if a users message input is correct.

    This assumes the user entered an intent directly, e.g. using
    `/greet`. Return `True` if the intent is a known one."""

    parse_data_set = latest_message.get("parse_data", {})
    intention = parse_data_set.get("intent", {}).get(KEY_INTENT_NAME)

    if intention in convo_intents:
        return True
    else:
        return False


async def _authenticate_user_text(
    latest_message: Dict[Text, Any], endpoint: EndpointConfiguration, conversation_id: Text
) -> bool:
    """Validate a user message input as free text.

    This assumes the user message is a text message (so NOT `/greet`)."""

    parse_data_set = latest_message.get("parse_data", {})
    txt = _as_md_msg(parse_data_set)
    intention = parse_data_set.get("intent", {}).get(KEY_INTENT_NAME)
    fetch_entities = parse_data_set.get("entities", [])
    if fetch_entities:
        msg = (
            f"Is the intent '{intention}' correct for '{txt}' and are "
            f"all entities labeled correctly?"
        )
    else:
        msg = (
            f"Your NLU model classified '{txt}' with intent '{intention}'"
            f" and there are no entities, is this correct?"
        )

    if intention is None:
        print(f"The NLU classification for '{txt}' returned '{intention}'")
        return False
    else:
        ques = questionary.confirm(msg)

        return await _ask_ques(ques, conversation_id, endpoint)


async def _authenticate_nlu(
    convo_intents: List[Text], endpoint: EndpointConfiguration, conversation_id: Text
) -> None:
    """Validate if a user message, either text or intent is correct.

    If the prediction of the latest user message is incorrect,
    the tracker will be corrected with the correct intent / entities."""

    tracer = await recover_tracker(
        endpoint, conversation_id, releaseVerbosity.AFTER_RESTART
    )

    latest_msg = latest_user_msg(tracer.get("events", [])) or {}

    if latest_msg.get("text", "").startswith(  # pytype: disable=attribute-error
        INTENT_MSG_PREFIX 
    ):
        authentic = _authenticate_user_regex(latest_msg, convo_intents)
    else:
        authentic = await _authenticate_user_text(latest_msg, endpoint, conversation_id)

    if not authentic:
        rectifyed_intent = await _request_objective_from_user(
            latest_msg, convo_intents, conversation_id, endpoint
        )
        # corrected convo_intents have confidence 1.0
        rectifyed_intent["confidence"] = 1.0

        events_name = tracer.get("events", [])

        fetch_entities = await _right_entities(latest_msg, endpoint, conversation_id)
        rectified_nlu = {
            "intent": rectifyed_intent,
            "entities": fetch_entities,
            "text": latest_msg.get("text"),
        }

        await _right_wrong_nlu(rectified_nlu, events_name, endpoint, conversation_id)


async def _right_entities(
    latest_message: Dict[Text, Any], endpoint: EndpointConfiguration, conversation_id: Text
) -> List[Dict[Text, Any]]:
    """Validate the entities of a user message.

    Returns the corrected entities"""
    from convo.shared.nlu.training_data import entities_parser

    parse_original_data = latest_message.get("parse_data", {})
    entity_string = _as_md_msg(parse_original_data)
    ques = questionary.text(
        "Please mark the entities using [value](type) notation", default=entity_string
    )

    comments = await _ask_ques(ques, conversation_id, endpoint)
    parse_comments = entities_parser.parsing_training_example(comments)

    rectified_entities = _merge_commented_and_original_entities(
        parse_comments, parse_original_data
    )

    return rectified_entities


def _merge_commented_and_original_entities(
    parse_annotated: Msg, parse_original: Dict[Text, Any]
) -> List[Dict[Text, Any]]:
    # overwrite entities which have already been
    # annotated in the original annotation to preserve
    # additional entity parser information
    fetch_entities = parse_annotated.get("entities", [])[:]
    for i, entity in enumerate(fetch_entities):
        for original_entity in parse_original.get("entities", []):
            if _is_same_entity_comments(entity, original_entity):
                fetch_entities[i] = original_entity
                break
    return fetch_entities


def _is_same_entity_comments(entity: Dict[Text, Any], others: Dict[Text, Any]) -> bool:
    return (
        entity["value"] == others["value"]
        and entity["entity"] == others["entity"]
        and entity.get("group") == others.get("group")
        and entity.get("role") == others.get("group")
    )


async def _enter_user_msg(conversation_id: Text, endpoint: EndpointConfiguration) -> None:
    """Request a new message from the user."""

    ques = questionary.text("Your input ->")

    msg = await _ask_ques(ques, conversation_id, endpoint, lambda a: not a)

    if msg == (INTENT_MSG_PREFIX  + RESTART_USER_INTENT):
        raise ResumeConversation()

    await send_msg(endpoint, conversation_id, msg)


async def is_listening_for_msg(
    conversation_id: Text, endpoint: EndpointConfiguration
) -> bool:
    """Check if the conversation is in need for a user message."""

    tracer = await recover_tracker(endpoint, conversation_id, releaseVerbosity.APPLIED)

    for i, e in enumerate(reversed(tracer.get("events", []))):
        if e.get("event") == UserUttered.type_name:
            return False
        elif e.get("event") == ActionExecuted.type_name:
            return e.get("name") == LISTEN_ACTION_NAME  
    return False


async def _revert_latest(conversation_id: Text, endpoint: EndpointConfiguration) -> None:
    """Undo either the latest bot action or user message, whatever is last."""

    tracker = await recover_tracker(endpoint, conversation_id, releaseVerbosity.ALL)

    # Get latest `UserUtterance` or `ActionExecuted` event.
    end_event_type = None
    for i, e in enumerate(reversed(tracker.get("events", []))):
        end_event_type = e.get("event")
        if end_event_type in {ActionExecuted.type_name, UserUttered.type_name}:
            break
        elif end_event_type == Restarted.type_name:
            break

    if end_event_type == ActionExecuted.type_name:
        revert_act = ActReverted().as_dictionary()
        await dispatch_event(endpoint, conversation_id, revert_act)
    elif end_event_type == UserUttered.type_name:
        revert_user_msg = UserChangeReverted().as_dictionary()
        listen_for_next_msg = ActionExecuted(LISTEN_ACTION_NAME  ).as_dictionary()

        await dispatch_event(
            endpoint, conversation_id, [revert_user_msg, listen_for_next_msg]
        )


async def _get_events(
    conversation_ids: List[Union[Text, List[Event]]], endpoint: EndpointConfiguration
) -> List[List[Event]]:
    """Retrieve all event trackers from the endpoint for all conversation ids."""

    event_chain = []
    for conversation_id in conversation_ids:
        if isinstance(conversation_id, str):
            tracer = await recover_tracker(endpoint, conversation_id)
            events_name = tracer.get("events", [])

            for conversation in _split_conversation_at_resume(events_name):
                analyse_events = convo.shared.core.events.deserialized_events(conversation)
                event_chain.append(analyse_events)
        else:
            event_chain.append(conversation_id)
    return event_chain


async def _deploye_trackers(
    conversation_ids: List[Union[Text, List[Event]]],
    output_file: Optional[Text],
    endpoint: EndpointConfiguration,
    unconfirmed: Optional[List[Event]] = None,
) -> None:
    """Create a plot of the trackers of the passed conversation ids.

    This assumes that the last conversation id is the conversation we are currently
    working on. If there are events that are not part of this active tracker
    yet, they can be passed as part of `unconfirmed`. They will be appended
    to the currently active conversation."""

    if not output_file or not conversation_ids:
        # if there is no output file provided, we are going to skip plotting
        # same happens if there are no conversation ids
        return

    event_order = await _get_events(conversation_ids, endpoint)

    if unconfirmed:
        event_order[-1].extend(unconfirmed)

    graph = await visualizeNeighborhood(
        event_order[-1], event_order, output_file=None, max_history=2
    )

    from networkx.drawing.nx_pydot import write_dot

    write_dot(graph, output_file)


def _help_print(skip_visualization: bool) -> None:
    """Print some initial help message for the user."""

    if not skip_visualization:
        visualise_url = BY_DEFAULT_SERVER_FORMAT.format(
            "http", BY_DEFAULT_SERVER_PORT + 1
        )
        visualis_help = (
            f"Visualisation at {visualise_url}/visualization.html ."
        )
    else:
        visualis_help = ""

    convo.shared.utils.cli.printing_success(
        f"Bot loaded. {visualis_help}\n"
        f"Type a message and press enter "
        f"(press 'Ctr-c' to exit)."
    )


async def record_msg(
    endpoint: EndpointConfiguration,
    file_importer: TrainingDataImporter,
    conversation_id: Text = CONVO_DEFAULT_SENDER_ID ,
    max_message_limit: Optional[int] = None,
    skip_visualization: bool = False,
) -> None:
    """Read messages from the command line and print bot responses."""

    try:
        try:
            domain_name = await recover_domain(endpoint)
        except ClientError:
            log.exception(
                f"Failed to connect to Convo Core server at '{endpoint.url}'. "
                f"Is the server running?"
            )
            return

        intention = [next(iter(i)) for i in (domain_name.get("intents") or [])]

        num_msg = 0

        if not skip_visualization:
            events_containing_current_user_id = await _fetch_tracker_events_to_plot(
                domain_name, file_importer, conversation_id
            )

            plot_file_name = BY_DEFAULT_STORY_GRAPH_FILE
            await _deploye_trackers(events_containing_current_user_id, plot_file_name, endpoint)
        else:
            # `None` means that future `_plot_trackers` calls will also skip the
            # visualization.
            plot_file_name = None
            events_containing_current_user_id = []

        _help_print(skip_visualization)

        while not utils.is_limit_achived(num_msg, max_message_limit):
            try:
                if await is_listening_for_msg(conversation_id, endpoint):
                    await _enter_user_msg(conversation_id, endpoint)
                    await _authenticate_nlu(intention, endpoint, conversation_id)

                await _forecast_till_next_listen(
                    endpoint,
                    conversation_id,
                    events_containing_current_user_id,
                    plot_file_name,
                )

                num_msg += 1
            except ResumeConversation:
                await dispatch_event(endpoint, conversation_id, Restarted().as_dictionary())

                await dispatch_event(
                    endpoint,
                    conversation_id,
                    ActionExecuted(LISTEN_ACTION_NAME  ).as_dictionary(),
                )

                log.info("Restarted conversation, starting a new one.")
            except RevertLastStep:
                await _revert_latest(conversation_id, endpoint)
                await _print_record(conversation_id, endpoint)
            except ForkTracer:
                await _print_record(conversation_id, endpoint)

                events_fork = await _request_split_from_user(conversation_id, endpoint)

                await dispatch_event(endpoint, conversation_id, Restarted().as_dictionary())

                if events_fork:
                    for evt in events_fork:
                        await dispatch_event(endpoint, conversation_id, evt)
                log.info("Restarted conversation at fork.")

                await _print_record(conversation_id, endpoint)
                await _deploye_trackers(
                    events_containing_current_user_id, plot_file_name, endpoint
                )

    except Terminate:
        return
    except Exception:
        log.exception("An exception occurred while recording messages.")
        raise


async def _fetch_tracker_events_to_plot(
    domain: Dict[Text, Any], file_importer: TrainingDataImporter, conversation_id: Text
) -> List[Union[Text, List[Event]]]:
    trackers_training = await _fetch_training_trackers(file_importer, domain)
    no_of_trackers = len(trackers_training)
    if no_of_trackers > MAXIMUM_NO_OF_TRAINING_STORY_FOR_VISUALIZATION:
        convo.shared.utils.cli.printing_warning(
            f"You have {no_of_trackers} different story convo_paths in "
            f"your training data. Visualizing them is very resource "
            f"consuming. Hence, the visualization will only show the stories "
            f"which you created during interactive learning, but not your "
            f"training stories."
        )
        trackers_training = []

    training_data_set_events = [t.events for t in trackers_training]
    events_containing_current_user_id = training_data_set_events + [conversation_id]

    return events_containing_current_user_id


async def _fetch_training_trackers(
    file_importer: TrainingDataImporter, domain: Dict[str, Any]
) -> List[DialogueStateTracer]:
    from convo.core import training

    return await training.load_data(
        file_importer,
        Domain.from_dict(domain),
        augmentation_factor=0,
        use_story_concatenation=False,
    )


def _serve_app(
    app: Sanic,
    file_importer: TrainingDataImporter,
    skip_visualization: bool,
    conversation_id: Text,
    port: int,
) -> Sanic:
    """Start a core server and attach the interactive learning IO."""

    last_point = EndpointConfiguration(url=BY_DEFAULT_SERVER_FORMAT.format("http", port))

    async def run_interactive_io(running_app: Sanic) -> None:
        """Small wrapper to shut down the server once cmd io is done."""

        await record_msg(
            endpoint=last_point,
            file_importer=file_importer,
            skip_visualization=skip_visualization,
            conversation_id=conversation_id,
        )

        log.info("Killing Sanic server now.")

        running_app.stop()  # kill the sanic server

    app.add_task(run_interactive_io)

    updating_sanic_log_level()

    app.run(host="0.0.0.0", port=port)

    return app


def begin_visualize(image_path: Text, port: int) -> None:
    """Add routes to serve the conversation visualization files."""

    application = Sanic(__name__)

    # noinspection PyUnusedLocal
    @application.exception(NotFound)
    async def disregard_404s(request, exception):
        return response.text("Not found", status=404)

    # noinspection PyUnusedLocal
    @application.route(visualizationTemplatePath, methods=["GET"])
    def imagine_html(request):
        return response.file(visualization.visualizationHtmlPath())

    # noinspection PyUnusedLocal
    @application.route("/visualization.dot", methods=["GET"])
    def imagine_png(request):
        try:
            headers = {"Cache-Control": "no-cache"}
            return response.file(os.path.abspath(image_path), headers=headers)
        except FileNotFoundError:
            return response.text("", 404)

    updating_sanic_log_level()

    application.run(host="0.0.0.0", port=port, access_log=False)


# noinspection PyUnusedLocal
async def train_agent_on_begin(
    args, endpoints, add_on_arguments, app, loop
) -> None:
    _interpreter = convo.core.interpreter.generate_interpreter(
        endpoints.nlu or args.get("nlu")
    )

    model_dir = args.get("out", tempfile.mkdtemp(suffix="_core_model"))

    agent = await train(
        args.get("domain"),
        args.get("stories"),
        model_dir,
        _interpreter,
        endpoints,
        args.get("config")[0],
        None,
        add_on_arguments,
    )
    app.agent = agent


async def wait_till_server_running_state(
    endpoint, max_retries=30, sleep_between_retries=1
) -> bool:
    """Try to reach the server, retry a couple of times and sleep in between."""

    while max_retries:
        try:
            s = await recover_status(endpoint)
            log.info(f"Reached core: {s}")
            if not s.get("is_ready"):
                # server did not finish loading the agent yet
                # in this case, we need to wait till the model trained
                # so we might be sleeping for a while...
                await asyncio.sleep(sleep_between_retries)
                continue
            else:
                # server is ready to go
                return True
        except ClientError:
            max_retries -= 1
            if max_retries:
                await asyncio.sleep(sleep_between_retries)

    return False


def execute_interactive_learning(
    file_importer: TrainingDataImporter,
    skip_visualization: bool = False,
    conversation_id: Text = uuid.uuid4().hex,
    server_arguments: Dict[Text, Any] = None,
) -> None:
    """Start the interactive learning with the model of the agent."""
    global STORE_IN_E2E
    server_arguments = server_arguments or {}

    if server_arguments.get("nlu_data"):
        PATH_FLOW["nlu"] = server_arguments["nlu_data"]

    if server_arguments.get("stories"):
        PATH_FLOW["stories"] = server_arguments["stories"]

    if server_arguments.get("domain"):
        PATH_FLOW["domain"] = server_arguments["domain"]

    port_name = server_arguments.get("port", BY_DEFAULT_SERVER_PORT)

    STORE_IN_E2E = server_arguments["e2e"]

    if not skip_visualization:
        visualise_port = port_name + 1
        q = Process(
            target=begin_visualize,
            args=(BY_DEFAULT_STORY_GRAPH_FILE, visualise_port),
        )
        q.daemon = True
        q.start()
    else:
        q = None

    application = run.configure_application(port=port_name, conversation_id="default", enable_api=True)
    last_point = AvailableEndpoints.read_last_points(server_arguments.get("endpoints"))

    # before_server_start handlers make sure the agent is loaded before the
    # interactive learning IO starts
    application.register_listener(
        partial(run.load_agent_on_boot, server_arguments.get("model"), last_point, None),
        "before_server_start",
    )

    telemetry.track_interactive_learning_start(skip_visualization, STORE_IN_E2E)

    _serve_app(application, file_importer, skip_visualization, conversation_id, port_name)

    if not skip_visualization and q is not None:
        q.terminate()  # pytype: disable=attribute-error
        q.join()  # pytype: disable=attribute-error
