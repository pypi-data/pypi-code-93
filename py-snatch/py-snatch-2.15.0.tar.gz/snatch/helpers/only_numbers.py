def only_numbers(text: str) -> str:
    """Return Only numbers from String."""
    return "".join([char for char in text if char.isdigit()])
