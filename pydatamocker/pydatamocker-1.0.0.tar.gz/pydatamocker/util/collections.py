def dedup_list(list_: list):
    return list(dict.fromkeys(list_))


def list_diff(minuend: list, subtrahend: list):
    subtr_set = set(subtrahend)
    return [ el for el in minuend if el not in subtr_set ]
