from typing import Any, Dict, Text


class NotEmulator:
    def __init__(self) -> None:
        self.name = None

    def normalise_request_dict(self, data: Dict[Text, Any]) -> Dict[Text, Any]:

        _data_set = {
            "text": data["text"][0] if type(data["text"]) == list else data["text"]
        }

        if data.get("model"):
            if type(data["model"]) == list:
                _data_set["model"] = data["model"][0]
            else:
                _data_set["model"] = data["model"]

        _data_set["time"] = data["time"] if "time" in data else None
        return _data_set

    def normalise_response_dict(self, data: Dict[Text, Any]) -> Dict[Text, Any]:
        """Transform data to target format."""

        return data
