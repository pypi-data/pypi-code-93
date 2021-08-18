from enum import Enum
from typing import List

import mimeparse
import requests

from grammarbot import GrammarBotClient, GrammarBotApiResponse, GrammarBotMatch


class Language(Enum):
    EN_US = "en-US"
    EN_GB = "en-GB"


class GrammarBotException(Exception):
    pass


class HemoglobinGrammarBotMatch(GrammarBotMatch):
    @property
    def sentence(self) -> str:
        """
        Gives the rule category.
        """
        return self._match_json["sentence"]


class HemoglobinGrammarBotApiResponse(GrammarBotApiResponse):
    MATCH = HemoglobinGrammarBotMatch

    @property
    def matches(self) -> List[GrammarBotMatch]:
        """
        Different matches detected by the GrammarBot API.
        """
        return [self.MATCH(mjson) for mjson in self._json["matches"]]

    def to_dict(self):
        return self.matches


class HemoglobinGrammarBot(GrammarBotClient):
    API_RESPONSE = HemoglobinGrammarBotApiResponse
    MAX_CHARS = 7000

    def __init__(
        self,
        base_uri: str = "http://api.grammarbot.io/",
        api_key: str = "python-default",
        language: Language = Language.EN_US,
    ):
        super(HemoglobinGrammarBot, self).__init__(base_uri=base_uri, api_key=api_key)
        self.language = language
        self.api_calls_made = 0

    def _create_params(self, text):
        return {"language": self.language.value, "text": text, "api_key": self._api_key}

    def get_response(self, text: str):
        params = self._create_params(text)
        self.api_calls_made += 1
        return requests.get(self._endpoint, params=params)

    def check_response(self, response):
        main_mime_type, sub_mime_type, _ = mimeparse.parse_mime_type(
            response.headers["Content-Type"]
        )
        if not (main_mime_type == "application" and sub_mime_type == "json"):
            raise GrammarBotException(response.text)

    def check_under_max_chars(self, text):
        response = self.get_response(text)
        self.check_response(response)
        return self.API_RESPONSE(response.json())

    def check_over_max_chars(self, text):
        paras = text.splitlines()
        buffer = ""

        results = {"matches": []}

        for para in paras:
            if para:
                if len(para) > self.MAX_CHARS:
                    raise GrammarBotException(
                        "A paragraph is longer than {max_chars} maximum number of characters for GrammarBot. Processing cannot continue.".format(
                            max_chars=self.MAX_CHARS
                        )
                    )
                if (len(buffer) + len(para)) > self.MAX_CHARS:
                    response = self.get_response(buffer)
                    self.check_response(response)
                    results["matches"] += response.json()["matches"]
                    buffer = para
                else:
                    buffer += para

        response = self.get_response(buffer)
        self.check_response(response)
        results["matches"] += response.json()["matches"]

        return self.API_RESPONSE(results)

    def check(self, text: str):
        """
        Check a given piece of text for grammatical errors.
        :param text:
            Text to be checked using the API.
        """
        if len(text) < self.MAX_CHARS:
            return self.check_under_max_chars(text)
        else:
            return self.check_over_max_chars(text)
