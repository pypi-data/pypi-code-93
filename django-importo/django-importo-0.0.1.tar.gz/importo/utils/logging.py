DIVIDER_LENGTH = 50


def within_dividers(value: str, style: str = "-") -> str:
    divider = style * DIVIDER_LENGTH
    return f"{divider}\n{value}\n{divider}"
