from typing import Any


def orjson_serialize_default_handler(obj: Any) -> str:
    """Default callback for orjson dumps.

    Supports pandas Timestamp type.

    Args:
        obj: Object to serialize

    Returns:
        Serialized object
    """
    # This supports serializing pandas the Timestamp type
    if hasattr(obj, "isoformat"):
        return obj.isoformat()

    # As recommended by orjson, we raise TypeError to indicate this
    # function can't serialize the object
    raise TypeError()
