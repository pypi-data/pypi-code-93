import logging
import typing
from typing import Optional, Text

from convo.shared.utils.cli import printing_information, printing_success
from convo.shared.nlu.interpreter import RegexInterpreter
from convo.shared.constants import INTENT_MSG_PREFIX 
from convo.nlu.model import Interpreter
from convo.shared.utils.io import json_to_str
import convo.utils.common

if typing.TYPE_CHECKING:
    from convo.nlu.components import ElementBuilder

log = logging.getLogger(__name__)


def run_cmd(
    model_path: Text, component_builder: Optional["ElementBuilder"] = None
) -> None:
    interpreter = Interpreter.load(model_path, component_builder)
    regular_expression_interpreter = RegexInterpreter()

    printing_success("NLU model loaded. Type a message and press enter to parse it.")
    while True:
        printing_success("Next message:")
        try:
            msg = input().strip()
        except (EOFError, KeyboardInterrupt):
            printing_information("Wrapping up command line chat...")
            break

        if msg.startswith(INTENT_MSG_PREFIX):
            res = convo.utils.common.running_in_loop(regular_expression_interpreter.parse_func(msg))
        else:
            res = interpreter.parse_func(msg)

        print(json_to_str(res))
