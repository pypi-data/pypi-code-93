from sorcery import dict_of


def replace_empty_values(data: dict, defaults: dict) -> None:
    for k, v in defaults.items():
        if not data.get(k):
            data[k] = v


md = dict_of
