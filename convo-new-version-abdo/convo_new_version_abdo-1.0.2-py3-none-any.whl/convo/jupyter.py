import pprint as pretty_print
import typing
from typing import Any, Dict, Optional, Text

from convo.core.interpreter import ConvoNLUInterpreter
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.shared.utils.cli import printing_error, printing_success
import convo.utils.common

if typing.TYPE_CHECKING:
    from convo.core.agent import CoreAgent


def print_p(obj: Any):
    pretty_print.pprint(obj, indentation=2)


def chat(
    model_path: Optional[Text] = None,
    endpoints: Optional[Text] = None,
    intermediate: Optional["CoreAgent"] = None,
    interpreter: Optional[NaturalLangInterpreter] = None,
) -> None:
    """Chat to the bot within a Jupyter notebook.

    Args:
        model_path: Path to a combined Convo model.
        endpoints: Path to a yaml with the action server is custom actions are defined.
        intermediate: Convo Core agent (used if no Convo model given).
        interpreter: Convo NLU interpreter (used with Convo Core agent if no
                     Convo model is given).
    """

    if model_path:
        from convo.run import create_new_agent

        intermediate = create_new_agent(model_path, endpoints)

    elif intermediate is not None and interpreter is not None:
        # HACK: this skips loading the interpreter and directly
        # sets it afterwards
        nlu_interpret = ConvoNLUInterpreter(
            "skip this and use given interpreter", lazy_init=True
        )
        nlu_interpret.interpreter = interpreter
        intermediate.interpreter = interpreter
    else:
        printing_error(
            "You either have to define a model path or an agent and an interpreter."
        )
        return

    print("Your bot is ready to talk! Type your messages here or send '/stop'.")
    while True:
        msg = input()
        if msg == "/stop":
            break

        outcomes = convo.utils.common.running_in_loop(intermediate.handle_text(msg))
        for response in outcomes:
            _display_bot_response(response)


def _display_bot_response_outcome(response: Dict):
    from IPython.display import Image, display  # pytype: disable=import-error

    for response_type, value in response.items():
        if response_type == "text":
            printing_success(value)

        if response_type == "image":
            image = Image(url=value)
            display(image)
