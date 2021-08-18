import time
import json
import logging
import os
import requests
from typing import Any, List, Optional, Text, Dict

import convo.utils.endpoints as endpoints_utils
from convo.shared.constants import COMPONENTS_DOCUMENTS_URL
from convo.shared.nlu.constants import ENTITIES_NAME, TXT
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.extractors.extractor import ExtractorEntity
from convo.nlu.model import Metadataset
from convo.shared.nlu.training_data.message import Msg
import convo.shared.utils.io

log = logging.getLogger(__name__)


def additional_value(match: Dict[Text, Any]) -> Dict[Text, Any]:
    if match["value"].get("type") == "interval":
        worth = {
            "to": match["value"].get("to", {}).get("value"),
            "from": match["value"].get("from", {}).get("value"),
        }
    else:
        worth = match["value"].get("value")

    return worth


def convert_duckling_format_to_convo(
    matches: List[Dict[Text, Any]]
) -> List[Dict[Text, Any]]:
    taken_out = []

    for match in matches:
        worth = additional_value(match)
        entity = {
            "start": match["start"],
            "end": match["end"],
            "text": match.get("body", match.get("text", None)),
            "value": worth,
            "confidence": 1.0,
            "additional_info": match["value"],
            "entity": match["dim"],
        }

        taken_out.append(entity)

    return taken_out


class DucklingEntityExtractor(ExtractorEntity):
    """Searches for structured entites, e.g. dates, using a duckling server."""

    defaults = {
        # by default all dimensions recognized by duckling are returned
        # dimensions can be configured to contain an array of strings
        # with the names of the dimensions to filter for
        "dimensions": None,
        # http url of the running duckling server
        "url": None,
        # locale - if not set, we will use the language of the model
        "locale": None,
        # timezone like Europe/Berlin
        # if not set the default timezone of Duckling is going to be used
        "timezone": None,
        # Timeout for receiving response from http url of the running duckling server
        # if not set the default timeout of duckling http url is set to 3 seconds.
        "timeout": 3,
    }

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        language: Optional[Text] = None,
    ) -> None:

        super().__init__(component_config)
        self.language = language

    @classmethod
    def create(
        cls, component_config: Dict[Text, Any], config: ConvoNLUModelConfiguration
    ) -> "DucklingEntityExtractor":

        return cls(component_config, config.lang)

    def _local(self) -> Optional[Text]:
        if not self.component_config.get("locale"):
            # this is king of a quick fix to generate a proper locale
            # works most of the time
            fetch_language = self.language or ""
            local_fixes = "{}_{}".format(fetch_language, fetch_language.upper())
            self.component_config["locale"] = local_fixes
        return self.component_config.get("locale")

    def _uniform_resource_locator(self) -> Optional[Text]:
        """Return url of the duckling service. Environment var will override."""
        if os.environ.get("CONVO_DUCKLING_HTTP_URL"):
            return os.environ["CONVO_DUCKLING_HTTP_URL"]

        return self.component_config.get("url")

    def _payload_data(self, text: Text, reference_time: int) -> Dict[Text, Any]:
        measurement = self.component_config["dimensions"]
        return {
            "text": text,
            "locale": self._local(),
            "tz": self.component_config.get("timezone"),
            "dims": json.dumps(measurement),
            "reftime": reference_time,
        }

    def _parse_duckling(self, text: Text, reference_time: int) -> List[Dict[Text, Any]]:
        """Sends the request to the duckling server and parses the result.

        Args:
            text: Text for duckling server to parse.
            reference_time: Reference time in milliseconds.

        Returns:
            JSON response from duckling server with parse data.
        """
        analyze_url = endpoints_utils.concatenate_url(self._uniform_resource_locator(), "/parse")
        try:
            pay_load = self._payload_data(text, reference_time)
            headers_name = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
            duckling_entity_extractor_response = requests.post(
                analyze_url,
                data=pay_load,
                headers=headers_name,
                timeout=self.component_config.get("timeout"),
            )
            if duckling_entity_extractor_response.status_code == 200:
                return duckling_entity_extractor_response.json()
            else:
                log.error(
                    f"Failed to get a proper response from remote "
                    f"duckling at '{analyze_url}. Status Code: {duckling_entity_extractor_response.status_code}. Response: {duckling_entity_extractor_response.text}"
                )
                return []
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
        ) as e:
            log.error(
                "Failed to connect to duckling http server. Make sure "
                "the duckling server is running/healthy/not stale and the proper host "
                "and port are set in the configuration. More "
                "information on how to run the server can be found on "
                "github: "
                "https://github.com/facebook/duckling#quickstart "
                "Error: {}".format(e)
            )
            return []

    @staticmethod
    def _reference_time_from_msg(message: Msg) -> int:
        if message.time is not None:
            try:
                return int(message.time) * 1000
            except ValueError as e:
                logging.warning(
                    "Could not parse timestamp {}. Instead "
                    "current UTC time will be passed to "
                    "duckling. Error: {}".format(message.time, e)
                )
        # fallbacks to current time, multiplied by 1000 because duckling
        # requires the reftime in miliseconds
        return int(time.time()) * 1000

    def process(self, message: Msg, **kwargs: Any) -> None:

        if self._uniform_resource_locator() is not None:
            time_reference = self._reference_time_from_msg(message)
            equivalentes = self._parse_duckling(message.get(TXT), time_reference)
            all_taken_out = convert_duckling_format_to_convo(equivalentes)
            measurements = self.component_config["dimensions"]
            taken_out = DucklingEntityExtractor.filter_irrelevant_entities(
                all_taken_out, measurements
            )
        else:
            taken_out = []
            convo.shared.utils.io.raising_warning(
                "Duckling HTTP component in pipeline, but no "
                "`url` configuration in the config "
                "file nor is `CONVO_DUCKLING_HTTP_URL` "
                "set as an environment variable. No entities will be extracted!",
                docs=COMPONENTS_DOCUMENTS_URL + "#DucklingEntityExtractor",
            )

        taken_out = self.add_extractor_name(taken_out)
        message.put(ENTITIES_NAME, message.get(ENTITIES_NAME, []) + taken_out, add_to_output=True)

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Text = None,
        model_metadata: Optional[Metadataset] = None,
        cached_component: Optional["DucklingEntityExtractor"] = None,
        **kwargs: Any,
    ) -> "DucklingEntityExtractor":

        get_language = model_metadata.get("language") if model_metadata else None
        return cls(meta, get_language)
