import json
import logging
import os
import typing
from typing import Optional, Text

import convo.shared.utils.io
from convo.shared.nlu.training_data.formats import MarkdownReviewer, NLGMarkdownReviewer
from convo.shared.nlu.training_data.formats.dialogflow import (
    AGENT_DIALOGFLOW,
    ENTITIES_DIALOGFLOW,
    ENTRIES_DIALOGFLOW_ENTITY,
    INTENT_DIALOGFLOW,
    EXAMPLES_DIALOGFLOW_INTENT,
    PACKAGE_DIALOGFLOW,
)
from convo.shared.nlu.training_data.training_data import TrainingDataSet

if typing.TYPE_CHECKING:
    from convo.shared.nlu.training_data.formats.readerwriter import TrainingDataReviewer

log = logging.getLogger(__name__)

# Different supported file formats and their identifier
WIT = "wit"
LUIS = "luis"
CONVO = "convo_nlu"
MARKDOWN = "md"
CONVO_YAML = "convo_yml"
UNK = "unk"
MARK_DOWN_NLG = "nlg.md"
DICTIONARY = "json"
DIALOG_FLOW_RELEVANT = {ENTITIES_DIALOGFLOW, INTENT_DIALOGFLOW}

json_data_format_heuristics = {
    WIT: lambda js, fn: "data" in js and isinstance(js.get("data"), list),
    LUIS: lambda js, fn: "luis_schema_version" in js,
    CONVO: lambda js, fn: "convo_nlu_data" in js,
    AGENT_DIALOGFLOW: lambda js, fn: "supportedLanguages" in js,
    PACKAGE_DIALOGFLOW: lambda js, fn: "version" in js and len(js) == 1,
    INTENT_DIALOGFLOW: lambda js, fn: "responses" in js,
    ENTITIES_DIALOGFLOW: lambda js, fn: "isEnum" in js,
    EXAMPLES_DIALOGFLOW_INTENT: lambda js, fn: "_usersays_" in fn,
    ENTRIES_DIALOGFLOW_ENTITY: lambda js, fn: "_entries_" in fn,
}


def load_data_set(resource_name: Text, language: Optional[Text] = "en") -> "TrainingDataSet":
    """Load training data from disk.

    Merges them if loaded from disk and multiple files are found."""
    if not os.path.exists(resource_name):
        raise ValueError(f"File '{resource_name}' does not exist.")

    if os.path.isfile(resource_name):
        file_name = [resource_name]
    else:
        file_name = convo.shared.utils.io.listing_files(resource_name)

    data = [loader(f, language) for f in file_name]
    data = [ds for ds in data if ds]
    if len(data) == 0:
        training_data_set = TrainingDataSet()
    elif len(data) == 1:
        training_data_set = data[0]
    else:
        training_data_set = data[0].merge(*data[1:])

    return training_data_set


def reader_factory(fformat: Text) -> Optional["TrainingDataReviewer"]:
    """Generates the appropriate reader class based on the file format."""
    from convo.shared.nlu.training_data.formats import (
        ConvoYAMLReviewer,
        MarkdownReviewer,
        WitReviewer,
        LuisReviewer,
        ConvoReviewer,
        DialogflowReviewer,
        NLGMarkdownReviewer,
    )

    reviewer = None
    if fformat == LUIS:
        reviewer = LuisReviewer()
    elif fformat == WIT:
        reviewer = WitReviewer()
    elif fformat in DIALOG_FLOW_RELEVANT:
        reviewer = DialogflowReviewer()
    elif fformat == CONVO:
        reviewer = ConvoReviewer()
    elif fformat == MARKDOWN:
        reviewer = MarkdownReviewer()
    elif fformat == MARK_DOWN_NLG:
        reviewer = NLGMarkdownReviewer()
    elif fformat == CONVO_YAML:
        reviewer = ConvoYAMLReviewer()
    return reviewer


def loader(filename: Text, language: Optional[Text] = "en") -> Optional["TrainingDataSet"]:
    """Loads a single training data file from disk."""

    format = guessing_format(filename)
    if format == UNK:
        raise ValueError(f"Unknown data format for file '{filename}'.")

    reviewer = reader_factory(format)

    if reviewer:
        return reviewer.reading(filename, language=language, fformat=format)
    else:
        return None


def guessing_format(filename: Text) -> Text:
    """Applies heuristics to guesses the data format of a file.

    Args:
        filename: file whose type should be guessed

    Returns:
        Guessed file format.
    """
    from convo.shared.nlu.training_data.formats import ConvoYAMLReviewer

    guesses = UNK

    if not os.path.isfile(filename):
        return guesses

    try:
        matter = convo.shared.utils.io.read_file(filename)
        js = json.loads(matter)
    except ValueError:
        if MarkdownReviewer.markdown_nlu_file_check(filename):
            guesses = MARKDOWN
        elif NLGMarkdownReviewer.markdown_nlg_file_check(filename):
            guesses = MARK_DOWN_NLG
        elif ConvoYAMLReviewer.yaml_nlu_file_check(filename):
            guesses = CONVO_YAML
    else:
        for file_format, format_heuristic in json_data_format_heuristics.items():
            if format_heuristic(js, filename):
                guesses = file_format
                break

    log.debug(f"Training data format of '{filename}' is '{guesses}'.")

    return guesses
