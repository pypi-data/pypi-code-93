from abc import ABC
from typing import Any


class SearchByCriteriaVo(ABC):
    def __get_search_criteria_fields(self):
        search_criteria: dict = {}
        for attribute in dir(self):
            if (
                not attribute.startswith("__")
                and not attribute.startswith("_")
                and not callable(getattr(self, attribute))
                and getattr(self, attribute) is not None
            ):
                search_criteria[attribute] = getattr(self, attribute)
        return search_criteria

    def as_dict(self) -> dict:
        return self.__get_search_criteria_fields()

    def __str__(self) -> str:
        return self.as_dict()
