import logging
from itertools import groupby

from pentaquark.constants import SEPARATOR
from pentaquark.exceptions import PentaQuarkInvalidQueryException
from pentaquark.lookups import LOOKUPS

logger = logging.getLogger(__name__)


def _grouper(item: str) -> str:
    if SEPARATOR in item:
        return item.split(SEPARATOR)[0]
    return item


def _get_key_without_group_key(g: str) -> str:
    return SEPARATOR.join(g.split(SEPARATOR)[1:])


def unflatten_list(*args) -> list:
    """Recursive function to parse args and transform them to a list of lists

    :param args:
    :return:
    """

    def _get_item(lst: list) -> list:
        return [
            _get_key_without_group_key(g) for g in lst
        ]

    result = []
    for key, group in groupby(args, _grouper):
        group_list = list(group)
        if any(SEPARATOR in g for g in group_list):
            # recursion
            result.append({
                key: unflatten_list(* _get_item(group_list))
            })
        else:
            result.append(key)
    return result


def unflatten_dict(**kwargs) -> dict:
    """Recursive function to parse kwargs and transform them to a deep dict.

    :param kwargs:
    :return:
    """

    def _get_item(lst: list) -> dict:
        return {
            _get_key_without_group_key(g): kwargs.get(g)
            for g in lst
        }

    ks = dict(sorted(kwargs.items()))
    result = {}
    for key, group in groupby(ks, _grouper):
        group_list = list(group)
        if any(SEPARATOR in g for g in group_list):
            # recursion
            result[key] = unflatten_dict(**_get_item(group_list))
        else:
            if key in LOOKUPS:
                raise PentaQuarkInvalidQueryException("Lookup not implemented")
            result[key] = kwargs.get(group_list[0])
    return result


def split_kwargs_into_first_level_and_remaining(model, data):
    first_level_kwargs = {}
    remaining_kwargs = {}
    for k, v in data.items():
        if k in model._properties:
            first_level_kwargs[k] = v
        elif model._meta.allow_undeclared_properties and k not in model._relationships:
            first_level_kwargs[k] = v
        else:
            remaining_kwargs[k] = v
    return first_level_kwargs, remaining_kwargs
