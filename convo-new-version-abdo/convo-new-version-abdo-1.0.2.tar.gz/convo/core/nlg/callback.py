import logging
from typing import Text, Any, Dict, Optional

from convo.core.constants import BY_DEFAULT_REQUEST_TIMEOUT
from convo.core.nlg.generator import NaturalLanguageGenerator
from convo.shared.core.trackers import DialogueStateTracer, releaseVerbosity
from convo.utils.endpoints import EndpointConfiguration

log = logging.getLogger(__name__)


def nlg_response_format_specification() -> Dict[Text, Any]:
    """Expected response schema for an NLG endpoint.

    Used for validation of the response returned from the NLG endpoint."""
    return {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "buttons": {"type": ["array", "null"], "items": {"type": "object"}},
            "elements": {"type": ["array", "null"], "items": {"type": "object"}},
            "attachment": {"type": ["object", "null"]},
            "image": {"type": ["string", "null"]},
            "custom": {"type": "object"},
        },
    }


def nlg_request_format_specification() -> Dict[Text, Any]:
    """Expected request schema for requests sent to an NLG endpoint."""

    return {
        "type": "object",
        "properties": {
            "template": {"type": "string"},
            "arguments": {"type": "object"},
            "tracker": {
                "type": "object",
                "properties": {
                    "sender_id": {"type": "string"},
                    "slots": {"type": "object"},
                    "latest_message": {"type": "object"},
                    "latest_event_time": {"type": "number"},
                    "paused": {"type": "boolean"},
                    "events": {"type": "array"},
                },
            },
            "channel": {"type": "object", "properties": {"name": {"type": "string"}}},
        },
    }


def request_format_of_nlg(
    template_name: Text,
    tracker: DialogueStateTracer,
    output_channel: Text,
    **kwargs: Any,
) -> Dict[Text, Any]:
    """Create the json body for the NLG json body for the request."""

    _tracker_state = tracker.current_active_state(releaseVerbosity.ALL)

    return {
        "template": template_name,
        "arguments": kwargs,
        "tracker": _tracker_state,
        "channel": {"name": output_channel},
    }


class CallbackNaturalLangGenerator(NaturalLanguageGenerator):
    """Generate bot utterances by using a remote endpoint for the generation.

    The generator will call the endpoint for each message it wants to
    generate. The endpoint needs to respond with a properly formatted
    json. The generator will use this message to create a response for
    the bot."""

    def __init__(self, endpoint_config: EndpointConfiguration) -> None:

        self.nlg_endpoint = endpoint_config

    async def create(
        self,
        template_name: Text,
        tracker: DialogueStateTracer,
        output_channel: Text,
        **kwargs: Any,
    ) -> Dict[Text, Any]:
        """Retrieve a named template from the domain using an endpoint."""

        matter = request_format_of_nlg(template_name, tracker, output_channel, **kwargs)

        log.debug(
            "Requesting NLG for {} from {}."
            "".format(template_name, self.nlg_endpoint.url)
        )

        respn = await self.nlg_endpoint.request(
            method="post", json=matter, timeout=BY_DEFAULT_REQUEST_TIMEOUT
        )

        if self.verify_response(respn):
            return respn
        else:
            raise Exception("NLG web endpoint returned an invalid respn.")

    @staticmethod
    def verify_response(content: Optional[Dict[Text, Any]]) -> bool:
        """Validate the NLG response. Raises exception on failure."""

        from jsonschema import validate
        from jsonschema import ValidationError

        try:
            if content is None or content == "":
                # means the endpoint did not want to respond with anything
                return True
            else:
                validate(content, nlg_response_format_specification())
                return True
        except ValidationError as e:
            e.msg += (
                ". Failed to validate NLG response from API, make sure your "
                "response from the NLG endpoint is valid. "
                "For more information about the format please consult the "
                "`nlg_response_format_spec` function from this same module: "
                "https://github.com/ConvoHQ/convo/blob/master/convo/core/nlg/callback.py"
            )
            raise e
