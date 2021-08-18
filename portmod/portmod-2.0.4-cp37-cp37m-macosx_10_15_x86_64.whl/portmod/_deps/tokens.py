# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import List, Union

from portmodlib.atom import Atom
from portmodlib.usestr import parse_usestr


def token_conflicts(token1: str, token2: str) -> bool:
    """
    Returns true if and only if two tokens, which use minus-format (e.g. -foo)
    to indicate a disabled token, conflict. E.g. foo and -foo
    """
    return (
        token1.lstrip("-") == token2.lstrip("-")
        and token1[0] == "-"
        and token2[0] != "-"
        or token1[0] != "-"
        and token2[0] == "-"
    )


def negate(token: str) -> str:
    """Returns the negation of the given token"""
    if token.startswith("-"):
        return token.lstrip("-")
    return "-" + token


def expand_use_conditionals(tokens: List[str]) -> List[Union[str, List]]:
    """Expands any conditional use dependencies in the token tree"""
    result = []
    for token in tokens:
        if isinstance(token, list):
            result.append(expand_use_conditionals(token))
        elif isinstance(token, Atom) and token.USE:
            for flag in token.USE:
                stripped = token.strip_use()
                sflag = flag.rstrip("?=").lstrip("!")
                if flag.endswith("?") and not flag.startswith("!"):
                    result += parse_usestr(
                        f"{sflag}? ( {stripped}[{sflag}] ) !{sflag}? ( {stripped} )",
                        Atom,
                    )
                elif flag.endswith("?") and flag.startswith("!"):
                    result += parse_usestr(
                        f"{sflag}? ( {stripped} ) !{sflag}? ( {stripped}[-{sflag}] )",
                        Atom,
                    )
                elif flag.endswith("=") and not flag.startswith("!"):
                    result += parse_usestr(
                        f"{sflag}? ( {stripped}[{sflag}] ) !{sflag}? ( {stripped}[-{sflag}] )",
                        Atom,
                    )
                elif flag.endswith("=") and flag.startswith("!"):
                    result += parse_usestr(
                        f"{sflag}? ( {stripped}[-{sflag}] ) !{sflag}? ( {stripped}[{sflag}] )",
                        Atom,
                    )
                else:
                    result.append(Atom(stripped + f"[{flag}]"))
        else:
            result.append(token)
    return result
