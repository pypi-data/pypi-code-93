import re
from typing import Any
from pylint.checkers import BaseChecker

from .. import settings


class BaseChecker(BaseChecker):
    name: str = settings.CHECKER_NAME

    def _validate_match_name(
        self,
        node: Any,
        key: str,
        name: str,
    ) -> None:
        value: dict = self.validators[key]
        if not re.match(value['re'], name):
            self.add_message(value['msg_id'], node=node)
