import pydash


def str_to_list(data: str, lower=False, remove_comments=False, unique=False) -> list[str]:
    if lower:
        data = data.lower()
    arr = [line.strip() for line in data.split("\n") if line.strip()]
    if remove_comments:
        arr = [line.split("#")[0].strip() for line in arr]
        arr = [line for line in arr if line]
    if unique:
        arr = pydash.uniq(arr)

    return arr


def number_with_separator(value, prefix="", suffix="", separator="_", hide_zero=False, round_digits=2) -> str:
    if value is None or value == "":
        return ""
    if float(value) == 0:
        if hide_zero:
            return ""
        else:
            return f"{prefix}0{suffix}"
    if float(value) > 1000:
        value = "".join(
            reversed([x + (separator if i and not i % 3 else "") for i, x in enumerate(reversed(str(int(value))))]),
        )
    else:
        value = round(value, round_digits)

    return f"{prefix}{value}{suffix}"
