def get_first_value_from_comma_separated_string(comma_separated_string: str) -> str:
    if comma_separated_string:
        return comma_separated_string.split(sep=",")[0]

    return None
