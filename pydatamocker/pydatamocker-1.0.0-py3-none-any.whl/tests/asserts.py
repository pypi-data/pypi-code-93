def _is_blank(str_: str):
    return str_ is None or len(str_) == 0


def assert_equals(expected, actual, message=None):
    full_msg = f"Expected: {expected}, Actual: {actual}."
    if not _is_blank(message):
        full_msg = f"{message}: {full_msg}"
    assert expected == actual, full_msg


def assert_subset(sub, super, message=None):
    full_msg = f"Subset: {sub}, Superset: {super}."
    if not _is_blank(message):
        full_msg = f"{message}: {full_msg}"
    assert set(sub).issubset(set(super))
