import logging
from typing import Any, Dict, Text

from convo.shared.nlu.constants import INTENTION, ENTITIES_NAME, TXT
from convo.shared.nlu.training_data.formats.readerwriter import JsonTrainingDataReviewer

from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg

log = logging.getLogger(__name__)


class WitReviewer(JsonTrainingDataReviewer):
    def reading_from_json(self, js: Dict[Text, Any], **kwargs: Any):
        """Loads training data_set stored in the WIT.ai data_set format."""
        training_exps = []

        for s in js["data_set"]:
            entities = s.get(ENTITIES_NAME)
            if entities is None:
                continue
            text = s.get(TXT)
            intentions = [e["value"] for e in entities if e["entity"] == INTENTION]
            intention = intentions[0].strip('"') if intentions else None

            entities = [
                e
                for e in entities
                if ("start" in e and "end" in e and e["entity"] != INTENTION)
            ]
            for e in entities:
                # for some reason wit adds additional quotes around entities
                e["value"] = e["value"].strip('"')

            data_set = {}
            if intention:
                data_set[INTENTION] = intention
            if entities is not None:
                data_set[ENTITIES_NAME] = entities
            data_set[TXT] = text
            training_exps.append(Msg(data=data_set))
        return TrainingDataSet(training_exps)
