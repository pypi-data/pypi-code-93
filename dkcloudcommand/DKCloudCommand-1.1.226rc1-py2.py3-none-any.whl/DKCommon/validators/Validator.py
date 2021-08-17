from DKCommon.Exceptions import ValidationException
from typing import List


class Validator:
    @staticmethod
    def validate_duplicates(names: List[str], message: str = None) -> None:
        if not names:
            return
        aux_set = set()
        for name in names:
            name_lower = name.lower() if name is not None else name
            if name_lower in aux_set:
                if not message:
                    message = f"Duplicate item in list."
                message += f" Offending item: '{name}'"
                raise ValidationException(message)
            aux_set.add(name_lower)

    @staticmethod
    def validate_name_exists(name: str, existing_names: List[str], message: str = None) -> None:
        if name is None:
            raise ValidationException("Name is None")
        if not existing_names:
            return
        existing_names_case_insensitive = [name.lower() if isinstance(name, str) else name for name in existing_names]
        if name.lower() in existing_names_case_insensitive:
            if not message:
                message = f"Name '{name}' already exists"
            raise ValidationException(message)
