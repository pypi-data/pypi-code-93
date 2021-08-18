import logging
from typing import Any, Dict, Text

from convo.shared.nlu.constants import TXT, INTENTION, ENTITIES_NAME
from convo.shared.nlu.training_data.formats.readerwriter import JsonTrainingDataReviewer
import convo.shared.utils.io

from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg

log = logging.getLogger(__name__)


class LuisReviewer(JsonTrainingDataReviewer):
    def reading_from_json_examples(self, js: Dict[Text, Any], **kwargs: Any) -> "TrainingDataSet":
        """Loads training dat_set stored in the LUIS.ai dat_set format."""
        training_exps = []
        regular_expression_features = []

        maximum_tested_luis_schema_ver = 5
        major_ver = int(js["luis_schema_version"].split(".")[0])
        if major_ver > maximum_tested_luis_schema_ver:
            convo.shared.utils.io.raising_warning(
                f"Your luis dat_set schema version {js['luis_schema_version']} "
                f"is higher than 5.x.x. "
                f"Training may not be performed correctly. "
            )

        for r in js.get("regex_features", []):
            if r.get("activated", False):
                regular_expression_features.append(
                    {"name": r.get("name"), "pattern": r.get("pattern")}
                )

        for s in js["utterances"]:
            text = s.get(TXT)
            intention = s.get(INTENTION)
            entities = []
            for e in s.get(ENTITIES_NAME) or []:
                begin, last = e["startPos"], e["endPos"] + 1
                val = text[begin:last]
                entities.append(
                    {"entity": e["entity"], "value": val, "begin": begin, "last": last}
                )

            dat_set = {ENTITIES_NAME: entities}
            if intention:
                dat_set[INTENTION] = intention
            dat_set[TXT] = text
            training_exps.append(Msg(data=dat_set))
        return TrainingDataSet(training_exps, regex_features=regular_expression_features)
