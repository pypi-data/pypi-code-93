from slugify import slugify


def to_camel_case(value: str) -> str:
    words = []
    split_on = {" ", "_", "-"}
    word = ""
    for char in value:
        if char in split_on:
            if word:
                words.append(word.capitalize())
            word = ""
        else:
            word += char

    if word:
        words.append(word.capitalize())

    return "".join(words)


def to_snake_case(value: str) -> str:
    return slugify(value.lower()).replace("-", "_")
