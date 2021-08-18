import json
import logging
import os
import sys
from typing import Any, Dict, List, NoReturn, Optional, TYPE_CHECKING, Text

from convo.shared.constants import DEFAULT_MODEL_PATH 
import convo.shared.utils.cli
import convo.shared.utils.io

if TYPE_CHECKING:
    from questionary import Question

logger = logging.getLogger(__name__)

FREE_TEXT_INSERT_PROMPT = "Type out your own message..."


def fetch_validated_path(
    present: Optional[Text],
    parameter: Text,
    default: Optional[Text] = None,
    none_is_valid: bool = False,
) -> Optional[Text]:
    """Check whether a file path or its default value is valid and returns it.

    Args:
        present: The parsed value.
        parameter: The name of the parameter.
        default: The default value of the parameter.
        none_is_valid: `True` if `None` is valid value for the path,
                        else `False``

    Returns:
        The current value if it was valid, else the default value of the
        argument if it is valid, else `None`.
    """
    if present is None or present is not None and not os.path.exists(present):
        if default is not None and os.path.exists(default):
            reason_string = f"'{present}' not found."
            if present is None:
                reason_string = f"Parameter '{parameter}' not set."
            else:
                convo.shared.utils.io.raising_warning(
                    f"The path '{present}' does not seem to exist. Using the "
                    f"default value '{default}' instead."
                )

            logger.debug(f"{reason_string} Using default location '{default}' instead.")
            present = default
        elif none_is_valid:
            present = None
        else:
            cause_not_found_cansel(present, parameter, default)

    return present


def lost_configuration_keys(path: Text, mandatory_keys: List[Text]) -> List[Text]:
    import convo.utils.io

    if not os.path.exists(path):
        return mandatory_keys

    configuration_data = convo.shared.utils.io.read_configuration_file(path)

    return [k for k in mandatory_keys if k not in configuration_data or configuration_data[k] is None]


def cause_not_found_cansel(
    current: Optional[Text], parameter: Text, default: Optional[Text]
) -> None:
    """Exits with an error because the given path was not valid.

    Args:
        current: The path given by the user.
        parameter: The name of the parameter.
        default: The default value of the parameter.

    """

    by_default_clause = ""
    if default:
        by_default_clause = f"use the default location ('{default}') or "
    convo.shared.utils.cli.printing_error(
        "The path '{}' does not exist. Please make sure to {}specify it"
        " with '--{}'.".format(current, by_default_clause, parameter)
    )
    sys.exit(1)


def parse_last_positional_args_as_model_path_flow() -> None:
    """Fixes the parsing of a potential positional model path argument."""

    if (
        len(sys.argv) >= 2
        # support relevant commands ...
        and sys.argv[1] in ["run", "shell", "interactive"]
        # but avoid interpreting subparser commands as model convo_paths
        and sys.argv[1:] != ["run", "actions"]
        and not sys.argv[-2].startswith("-")
        and os.path.exists(sys.argv[-1])
    ):
        sys.argv.append(sys.argv[-1])
        sys.argv[-2] = "--model"


def generate_output_path(
    output_path: Text = DEFAULT_MODEL_PATH ,
    prefix: Text = "",
    fixed_name: Optional[Text] = None,
) -> Text:
    """Creates an output path which includes the current timestamp.

    Args:
        output_path: The path where the model should be stored.
        fixed_name: Name of the model.
        prefix: A prefix which should be included in the output path.

    Returns:
        The generated output path, e.g. "20191201-103002.tar.gz".
    """
    import time

    if output_path.endswith("tar.gz"):
        return output_path
    else:
        if fixed_name:
            name = fixed_name
        else:
            time_format = "%Y%m%d-%H%M%S"
            name = time.strftime(time_format)
            name = f"{prefix}{name}"
        filename = f"{name}.tar.gz"
        return os.path.join(output_path, filename)


def button_to_str(button: Dict[Text, Any], idx: int = 0) -> Text:
    """Create a string representation of a button."""

    heading = button.pop("title", "")

    if "payload" in button:
        payload = " ({})".format(button.pop("payload"))
    else:
        payload = ""

    # if there are any additional attributes, we append them to the output
    if button:
        details = " - {}".format(json.dumps(button, sort_keys=True))
    else:
        details = ""

    button_str = "{idx}: {title}{payload}{details}".format(
        idx=idx + 1, title=heading, payload=payload, details=details
    )

    return button_str


def element_to_str(element: Dict[Text, Any], idx: int = 0) -> Text:
    """Create a string representation of an element."""
    title = element.pop("title", "")

    element_str = "{idx}: {title} - {element}".format(
        idx=idx + 1, title=title, element=json.dumps(element, sort_keys=True)
    )

    return element_str


def button_choices_from_msg_data_set(
    message: Dict[Text, Any], allow_free_text_input: bool = True
) -> List[Text]:
    """Return list of choices to present to the user.

    If allow_free_text_input is True, an additional option is added
    at the end along with the template buttons that allows the user
    to type in free text.
    """
    option_choices = [
        button_to_str(button, idx)
        for idx, button in enumerate(message.get("buttons"))
    ]
    if allow_free_text_input:
        option_choices.append(FREE_TEXT_INSERT_PROMPT)
    return option_choices


def payload_from_button_ques(button_question: "Question") -> Text:
    """Prompt user with a button question and returns the nlu payload."""
    response = button_question.ask()
    if response != FREE_TEXT_INSERT_PROMPT:
        # Extract intent slash command if it's a button
        response = response[response.find("(") + 1 : response.find(")")]
    return response


def signal_handler(sig, frame) -> NoReturn:
    print("Goodbye 👋")
    sys.exit(0)
