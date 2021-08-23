import re

from split_datalawyer.modules.modules_types import ModulesType

__PAGE_PRINT_PATTERNS__ = [
    "^Página [0-9]{1,} de [0-9]{1,}$",
    "^[0-9]{1,} (de|of) [0-9]{1,}$",
    "^Página([0-9]| [0-9])$",
    "^Fls.: [0-9]{1,}$",
    "^ID.* Pág\.([0-9]{1,}| [0-9]{1,})$",
    "^[0-9]{1,}\/[0-9]{1,}$"
]


class ForceDropDuplicatedModule():

    def get_type(self):
        return ModulesType.DUPLICATED_CONDITION

    def evaluate(self, document_sentences):
        has_page_print_indicator = False
        patterns = [re.compile(pattern) for pattern in __PAGE_PRINT_PATTERNS__]

        for sentence in document_sentences:
            has_page_print_indicator = any(pattern.match(sentence) for pattern in patterns)

            if has_page_print_indicator:
                break

        return has_page_print_indicator
