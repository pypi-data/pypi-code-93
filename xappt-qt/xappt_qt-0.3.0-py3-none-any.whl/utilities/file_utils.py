import re

FILE_NAME_VALID_CHARS__RE = re.compile(r"\W")

__all__ = [
    'safe_file_name',
]


def safe_file_name(s: str, *, strip_underscores: bool = True) -> str:
    cleansed_string = FILE_NAME_VALID_CHARS__RE.sub("_", s.lower())
    while cleansed_string.count("__"):
        cleansed_string = cleansed_string.replace("__", "_")
    if strip_underscores:
        cleansed_string = cleansed_string.strip("_")
    return cleansed_string
