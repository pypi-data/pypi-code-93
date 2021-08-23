def repr_parent(value: object) -> str:
    return "None" if value is None else f"{type(value).__name__}()"
