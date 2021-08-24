#!/usr/bin/env python3

from typing import List

def clean_list(lst:List[str]=None) -> List[str]:
    """
    Removes all duplicate and null entries from a String array.

    :param lst: Given string list
    :type lst: list[str], optional
    :return: List without duplicate or None entries
    :rtype: list[str]
    """
    # RETURN AN EMPTY LIST IF GIVEN LIST IS NONE
    if lst is None:
        return []
    # REMOVE NONE ENTRIES
    out = lst
    i = 0
    while i < len(out):
        if out[i] is None:
            del out[i]
            i = i - 1
        # INCREMENT COUNTER
        i = i + 1
    # REMOVE DUPLICATE ENTRIES
    i = 0
    while i < len(out):
        k = i + 1
        while k < len(out):
            if out[i] == out[k]:
                del out[k]
                k = k - 1
            # INCREMENT K COUNTER
            k = k + 1
        # INCREMENT I COUNTER
        i = i + 1
    return out
