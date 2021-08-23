import re


def dict_depth(collection):
    if isinstance(collection, dict) and collection:
        return 1 + max(dict_depth(collection[a]) for a in collection)
    if isinstance(collection, list) and collection:
        return 1 + max(dict_depth(a) for a in collection)
    return 0


OPERATIONS_COUNT_RE = re.compile(r"\d+(?=\ operation\(s\))")


def extract_operations_count_from_message(message):
    count_matches = OPERATIONS_COUNT_RE.search(message)
    if not count_matches:
        return 0
    return int(count_matches.group())
