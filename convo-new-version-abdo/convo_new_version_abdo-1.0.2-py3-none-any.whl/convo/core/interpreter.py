import aiohttp

import logging

import os
from typing import Text, Dict, Any, Union, Optional

from convo.core import constants
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.nlu.constants import KEY_INTENT_NAME
import convo.shared.utils.io
import convo.shared.utils.common
import convo.shared.nlu.interpreter
from convo.shared.nlu.training_data.message import Msg
from convo.utils.endpoints import EndpointConfiguration

log = logging.getLogger(__name__)


def generate_interpreter(
    obj: Union[
        convo.shared.nlu.interpreter.NaturalLangInterpreter,
        EndpointConfiguration,
        Text,
        None,
    ]
) -> "convo.shared.nlu.interpreter.NaturalLangInterpreter":
    """Factory to create a natural language interpreter."""

    if isinstance(obj, convo.shared.nlu.interpreter.NaturalLangInterpreter):
        return obj
    elif isinstance(obj, str) and os.path.exists(obj):
        return NLUInterpreter(model_directory=obj)
    elif isinstance(obj, str):
        # user passed in a string, but file does not exist
        log.warning(
            f"No local NLU model '{obj}' found. Using RegexInterpreter instead."
        )
        return convo.shared.nlu.interpreter.RegexInterpreter()
    else:
        return _generate_from_endpoint_configuration(obj)


class NLUHttpInterpreter(convo.shared.nlu.interpreter.NaturalLangInterpreter):
    def __init__(self, endpoint_config: Optional[EndpointConfiguration] = None) -> None:
        if endpoint_config:
            self.endpoint_config = endpoint_config
        else:
            self.endpoint_config = EndpointConfiguration(constants.BY_DEFAULT_SERVER_URL)

    async def parse(
        self,
        text: Text,
        message_id: Optional[Text] = None,
        tracker: Optional[DialogueStateTracer] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[Text, Any]:
        """Parse a text message.

        Return a default value if the parsing of the text failed."""

        by_default_return = {
            "intent": {KEY_INTENT_NAME: "", "confidence": 0.0},
            "entities": [],
            "text": "",
        }
        output = await self._http_parse(text, message_id)

        return output if output is not None else by_default_return

    async def _http_parse(
        self, text: Text, message_id: Optional[Text] = None
    ) -> Optional[Dict[Text, Any]]:
        """Send a text message to a running convo NLU http server.
        Return `None` on failure."""

        if not self.endpoint_config:
            log.error(
                f"Failed to parse text '{text}' using convo NLU over http. "
                f"No convo NLU server specified!"
            )
            return None

        parameters = {
            "token": self.endpoint_config.token,
            "text": text,
            "message_id": message_id,
        }

        if self.endpoint_config.url.endswith("/"):
            url_name = self.endpoint_config.url + "model/parse"
        else:
            url_name = self.endpoint_config.url + "/model/parse"

        # noinspection PyBroadException
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url_name, json=parameters) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        response_txt = await resp.text()
                        log.error(
                            f"Failed to parse text '{text}' using convo NLU over "
                            f"http. Error: {response_txt}"
                        )
                        return None
        except Exception:  # skipcq: PYL-W0703
            # need to catch all possible exceptions when doing http requests
            # (timeouts, value errors, parser errors, ...)
            log.exception(f"Failed to parse text '{text}' using convo NLU over http.")
            return None


class NLUInterpreter(convo.shared.nlu.interpreter.NaturalLangInterpreter):
    def __init__(
        self,
        model_directory: Text,
        config_file: Optional[Text] = None,
        lazy_init: bool = False,
    ):
        self.model_directory = model_directory
        self.lazy_init = lazy_init
        self.config_file = config_file

        if not lazy_init:
            self._interpreter_loading()
        else:
            self.interpreter = None

    async def parse(
        self,
        text: Text,
        message_id: Optional[Text] = None,
        tracker: Optional[DialogueStateTracer] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[Text, Any]:
        """Parse a text message.

        Return a default value if the parsing of the text failed."""

        if self.lazy_init and self.interpreter is None:
            self._interpreter_loading()

        output = self.interpreter.parse_func(text)

        return output

    def featurize_msg(self, message: Msg) -> Optional[Msg]:
        """Featurize message using a trained NLU pipeline.
        Args:
            message: storing text to process
        Returns:
            message containing tokens and features which are the output of the NLU pipeline
        """
        if self.lazy_init and self.interpreter is None:
            self._interpreter_loading()
        result = self.interpreter.featurize_msg(message)
        return result

    def _interpreter_loading(self) -> None:
        from convo.nlu.model import Interpreter

        self.interpreter = Interpreter.load(self.model_directory)


def _generate_from_endpoint_configuration(
    endpoint_config: Optional[EndpointConfiguration],
) -> convo.shared.nlu.interpreter.NaturalLangInterpreter:
    """Instantiate a natural language interpreter based on its configuration."""

    if endpoint_config is None:
        return convo.shared.nlu.interpreter.RegexInterpreter()
    elif endpoint_config.type is None or endpoint_config.type.lower() == "http":
        return NLUHttpInterpreter(endpoint_config=endpoint_config)
    else:
        return _load_from_module_name_in_endpoint_configuration(endpoint_config)


def _load_from_module_name_in_endpoint_configuration(
    endpoint_config: EndpointConfiguration,
) -> convo.shared.nlu.interpreter.NaturalLangInterpreter:
    """Instantiate an event channel based on its class name."""

    try:
        nlu_class_interpreter = convo.shared.utils.common.class_name_from_module_path(
            endpoint_config.type
        )
        return nlu_class_interpreter(endpoint_config=endpoint_config)
    except (AttributeError, ImportError) as e:
        raise Exception(
            f"Could not find a class based on the module path "
            f"'{endpoint_config.type}'. Failed to create a "
            f"`NaturalLangInterpreter` instance. Error: {e}"
        )
