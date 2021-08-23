from itertools import product
from typing import List, Mapping

from igenius_adapters_sdk.entities.numeric_binning import Bin, BinningRules
from igenius_adapters_sdk.entities.query import GroupByQuery, Query


def bin_interpolation(query: GroupByQuery, result: List[Mapping]) -> List[Mapping]:
    binset = {}
    for att in query.groups:
        if isinstance(att.function_uri.function_params, BinningRules):
            binset[att.alias] = att.function_uri.function_params.bins
        else:
            binset[att.alias] = list(dict.fromkeys([row[att.alias] for row in result]))
    default = {d.alias: d.default_bin_interpolation for d in query.aggregations}
    fullset = []
    for comb in product(*[[{bins: str(b) if isinstance(b, Bin) else b} for b in binset[bins]] for bins in binset]):
        partial = {k: v for d in comb for k, v in d.items()}
        match = []
        keep = {}
        for row in result:
            if any(match):
                break
            match.append(True)
            for k in row:
                if k not in partial:
                    keep[k] = row[k]
                    continue
                # the following two lines are related to a postgres issue with None management
                # see https://igenius.atlassian.net/browse/SQD-922?focusedCommentId=57332
                if isinstance(row[k], str):
                    row[k] = row[k].replace("NaN", "None")
                if partial[k] != row[k]:
                    match[-1] = False
                    break
        partial.update(keep if any(match) else default)
        fullset.append(partial)
    return fullset


def apply_alias_shortening(query: Query) -> Query:
    if hasattr(query, "groups") and query.groups:
        for att in query.groups:
            att.switch_to_shortened_alias()
    if hasattr(query, "aggregations") and query.aggregations:
        for att in query.aggregations:
            att.switch_to_shortened_alias()
    if hasattr(query, "order_by") and query.order_by:
        for att in query.order_by:
            att.switch_to_shortened_alias()
    return query


def restore_original_aliases(query: Query, result: List[Mapping]) -> List[Mapping]:
    alias_map = {}
    if hasattr(query, "groups") and query.groups:
        for att in query.groups:
            if att.has_been_shortened():
                alias_map[att.alias] = att.get_original_alias()
    if hasattr(query, "aggregations") and query.aggregations:
        for att in query.aggregations:
            if att.has_been_shortened():
                alias_map[att.alias] = att.get_original_alias()
    if len(alias_map):
        return [{alias_map[k] if k in alias_map else k: v for k, v in row.items()} for row in result]
    return result
