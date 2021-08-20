def remove_key(value: dict, removed_key='self') -> dict:
    if removed_key in value:
        value.pop(removed_key)
    return value
