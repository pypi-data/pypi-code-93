from __future__ import annotations
from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from ckan.lib.search.query import solr_literal

from ..interfaces import ICompositeSearch
from ..utils import SearchParam

CONFIG_LITERAL_QUOTES = "ckanext.composite_search.literal.quotes"
DEFAULT_LITERAL_QUOTES = "double"


def single_quote_solr_literal(t: str) -> str:
    escaped = t.replace("'", r"\'")
    return f"'{escaped}'"


def both_quote_solr_literal(t: str) -> str:
    single = single_quote_solr_literal(t)
    double = solr_literal(t)
    return f"{single} OR {double}"

_literals = {
    "single": single_quote_solr_literal,
    "double": solr_literal,
    "both": both_quote_solr_literal,

}


class DefaultSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(ICompositeSearch)

    # ICompositeSearch

    def before_composite_search(
        self, search_params: dict[str, Any], params: list[SearchParam]
    ) -> tuple[dict[str, Any], list[SearchParam]]:
        query = ''

        literal = _literals.get(tk.config.get(CONFIG_LITERAL_QUOTES, DEFAULT_LITERAL_QUOTES), _literals[DEFAULT_LITERAL_QUOTES])

        for param in reversed(params):
            value = ' '.join([literal(word) for word in param.value.split()])
            if not value:
                continue
            sign = '-' if tk.asbool(param.negation) else '+'
            fragment = f"{param.type}:* AND {sign}{param.type}:({value})"
            if query:
                query = f'{fragment} {param.junction} ({query})'
            else:
                query = fragment
        q = search_params.get('q', '')
        q += ' ' + query
        search_params['q'] = q.strip()
        return search_params, params
