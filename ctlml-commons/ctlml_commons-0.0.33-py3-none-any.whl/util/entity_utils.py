from typing import Any, Dict, List, Tuple


def separate_fields(input_data: Dict[str, Any], known_fields: List[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    other_fields: List[str] = [name for name, value in input_data.items() if name not in known_fields]

    known_fields = [field for field in known_fields if field != "other"]
    return {k: v for k, v in input_data.items() if k in known_fields}, {
        k: v for k, v in input_data.items() if k in other_fields
    }
