from typing import Any, Dict, Text

from convo.nlu.emulators.no_emulator import NotEmulator
from typing import List, Optional


class EmulatorLUIS(NotEmulator):
    def __init__(self) -> None:

        super().__init__()
        self.name = "luis"

    def _highest_intent(self, data) -> Optional[Dict[Text, Any]]:
        if data.get("intent"):
            return {
                "intent": data["intent"]["name"],
                "score": data["intent"]["confidence"],
            }
        else:
            return None

    def _rank(self, data) -> List[Dict[Text, Any]]:
        if data.get("intent_ranking"):
            return [
                {"intent": el["name"], "score": el["confidence"]}
                for el in data["intent_ranking"]
            ]
        else:
            highest = self._highest_intent(data)
            return [highest] if highest else []

    def normalise_response_dict(self, data: Dict[Text, Any]) -> Dict[Text, Any]:
        """Transform data to luis.ai format."""

        highest_intent = self._highest_intent(data)
        rank = self._rank(data)
        return {
            "query": data["text"],
            "topScoringIntent": highest_intent,
            "intents": rank,
            "entities": [
                {
                    "entity": e["value"],
                    "type": e["entity"],
                    "startIndex": e.get("start"),
                    "endIndex": (e["end"] - 1) if "end" in e else None,
                    "score": e.get("confidence"),
                }
                for e in data["entities"]
            ]
            if "entities" in data
            else [],
        }
