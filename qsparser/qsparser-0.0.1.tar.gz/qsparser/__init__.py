from typing import Any
from urllib.parse import quote, unquote
from re import split


def stringify(obj: dict[str, Any]) -> str:
    tokens: list[str] = []
    for key, value in obj.items():
        tokens.extend(gen_tokens([key], value))
    return '&'.join(tokens)


def gen_tokens(items: list[str], value: Any) -> list[str]:
    if value is True:
        return [f'{gen_key(items)}=true']
    elif value is False:
        return [f'{gen_key(items)}=false']
    elif value is None:
        return [f'{gen_key(items)}=null']
    elif isinstance(value, list):
        result: list[str] = []
        for i, v in enumerate(value):
            result.extend(gen_tokens(items + [str(i)], v))
        return result
    elif isinstance(value, dict):
        result: list[str] = []
        for k, v in value.items():
            result.extend(gen_tokens(items + [str(k)], v))
        return result
    else:
        return [f'{gen_key(items)}={quote(str(value))}']


def gen_key(items: list[str]) -> str:
    return f'{items[0]}[{"][".join(items[1:])}]'.removesuffix('[]')


def parse(qs: str) -> dict[str, Any]:
    result = {}
    tokens = qs.split('&')
    for token in tokens:
        key, value = token.split('=')
        items = split('\]?\[', key.removesuffix(']'))
        assign_to_result(result, items, value)
    return result


def assign_to_result(result: dict[str, Any], items: list[str], value: str) -> dict[str, Any]:
    if len(items) == 1:
        result[items[0]] = unquote(value)
        return result
    if items[0] not in result:
        result[items[0]] = {}
    assign_to_result(result[items[0]], items[1:], value)
    return result
