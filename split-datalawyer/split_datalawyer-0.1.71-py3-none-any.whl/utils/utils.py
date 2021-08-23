def parenthesis_is_closed(phrase: str) -> bool:
    if phrase != "":
        if phrase.count("(") > phrase.count(")") or phrase.rfind(")") < phrase.rfind("("):
            return False
    return True


def contains_only_closing_parenthesis(phrase: str) -> bool:
    return phrase.count("(") == 0 and phrase.count(")") > 0


def is_closing_a_parenthesis(phrase: str) -> bool:
    return phrase.count(")") > phrase.count("(")
