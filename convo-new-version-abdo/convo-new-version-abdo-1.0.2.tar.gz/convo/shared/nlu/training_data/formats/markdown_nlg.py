import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Text, Union

from convo.shared.nlu.constants import TXT
from convo.shared.nlu.training_data.formats.readerwriter import (
    TrainingDataReviewer,
    TrainingDataAuthor,
)
from convo.shared.nlu.training_data.training_data import TrainingDataSet
import convo.shared.utils.io as io_utils

log = logging.getLogger(__name__)


# looks for pattern like:
# ##
# * intent/response_key
#   - response_text
NLG_MARK_DOWN_REGULAR_EXPRESSION = re.compile(r"##\s*.*\n\*[^:]*\/.*\n\s*\t*\-.*")


class NLGMarkdownReviewer(TrainingDataReviewer):
    """Reads markdown training data containing NLG stories and creates a TrainingDataSet object."""

    def __init__(self) -> None:
        self.responses = {}
        super(NLGMarkdownReviewer, self).__init__()

    def reading(self, s: Text, **kwargs: Any) -> "TrainingDataSet":
        """Read markdown string and create TrainingDataSet object"""
        self.__init__()
        sentence = s.splitlines()
        self.responses = self.processing_lines(sentence)
        return TrainingDataSet(responses=self.responses)

    @staticmethod
    def processing_lines(lines: List[Text]) -> Dict[Text, List[Dict[Text, Text]]]:

        resps = {}
        intent_of_story = None
        story_bot_changes = []  # Keeping it a list for future additions

        for idx, sentence in enumerate(lines):

            line_number = idx + 1
            try:
                sentence = sentence.strip()
                if sentence == "":
                    continue
                elif sentence.startswith("#"):
                    # reached a new story block
                    if intent_of_story:
                        resps[intent_of_story] = story_bot_changes
                        story_bot_changes = []
                        intent_of_story = None

                elif sentence.startswith("-"):
                    # reach an assistant's utterance

                    # utterance might have '-' itself, so joining them back if any
                    change = "-".join(sentence.split("- ")[1:])
                    # utterance might contain escaped newlines that we want to unescape
                    change = change.replace("\\n", "\n")
                    story_bot_changes.append({TXT: change})

                elif sentence.startswith("*"):
                    # reached a user intent
                    intent_of_story = "*".join(sentence.split("* ")[1:])

                else:
                    # reached an unknown type of line
                    log.warning(
                        f"Skipping line {line_number}. "
                        "No valid command found. "
                        f"Line Content: '{sentence}'"
                    )
            except Exception as e:
                message = f"Error in line {line_number}: {e}"
                log.error(message, exc_info=1)  # pytype: disable=wrong-arg-types
                raise ValueError(message)

        # add last story
        if intent_of_story:
            resps[intent_of_story] = story_bot_changes

        return resps

    @staticmethod
    def markdown_nlg_file_check(filename: Union[Text, Path]) -> bool:
        """Checks if given file contains NLG training data.

        Args:
            filename: Path to the training data file.

        Returns:
            `True` if file contains NLG training data, `False` otherwise.
        """
        matter = io_utils.read_file(filename)
        return re.search(NLG_MARK_DOWN_REGULAR_EXPRESSION, matter) is not None


class NLGMarkdownAuthor(TrainingDataAuthor):
    def data_dumps(self, training_data: "TrainingDataSet") -> Text:
        """Transforms the NlG part of TrainingDataSet object into a markdown string."""

        md = ""
        for intent, utterances in training_data.responses.items():
            md += "## \n"
            md += f"* {intent}\n"
            for utterance in utterances:
                md += f"- {utterance.get('text')}\n"
            md += "\n"
        return md
