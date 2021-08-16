"""Where the MATCH Cypher query is built.
"""
import logging
from pentaquark.constants import START_NODE_ALIAS, SEPARATOR
from .pattern_builder import PatternBuilder
from .predicates import C, CompositeC
from .query_builder import QueryBuilder
from ..exceptions import PentaQuarkInvalidQueryException

logger = logging.getLogger(__name__)


class MatchQueryBuilder(QueryBuilder):
    """MATCH query builder"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._order_by = []
        self._limit = None
        self._skip = None
        self._where = None

    def match(self, **kwargs):
        # self._variables = [START_NODE_ALIAS]
        pb = PatternBuilder(self.model, param_store=self._param_store, variables_in_external_scope=self._variables)
        match = pb.build(kwargs)
        self._match.append(match)
        # self._variables.extend(pb._variables)
        return self

    def optional_match(self, **kwargs):
        return self

    def where(self, *args, **kwargs):
        for a in args:
            if not isinstance(a, (C, CompositeC)):
                raise TypeError(f"where args must be instances of 'C' (condition), found {a.__class__.__name__}")
            if self._where:
                self._where &= a
            else:
                self._where = a
        for a, value in kwargs.items():
            c = C(**{a: value})
            if self._where:
                self._where &= c
            else:
                self._where = c
        return self

    def order_by(self, *args):
        for a in args:
            a = START_NODE_ALIAS + SEPARATOR + a
            variable, prop = a.rsplit(SEPARATOR, 1)
            if variable not in self._variables:
                raise ValueError(f"Can not order by non existing variable ({variable})")
            # TODO: check that property exists, otherwise raise a Warning (not an Exception, to ease migrations)
            self._order_by.append(a)
        return self

    def skip(self, skip):
        self._skip = skip
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def _build_match_query(self):
        if self._match:
            return "MATCH " + ", ".join(self._match)
        return ""

    def _build_where_query(self):
        if self._where:
            q = self._where.compile(model=self.model, param_store=self._param_store, variables=self._variables)
            return "WHERE " + q
        return ""

    def _build_return_query(self):
        return "RETURN " + self._returns_to_cypher(self._return)

    def _build_order_by_query(self):
        q = []
        for a in self._order_by:
            variable, prop = a.rsplit(SEPARATOR, 1)
            sort = ""
            if prop.startswith("-"):
                sort = "DESC"
                prop = prop[1:]
            q.append(f"{variable}.{prop} {sort}")
        return ",".join(q)

    def _build_post_return_query(self):
        q = ""
        if self._order_by:
            q += "ORDER BY " + self._build_order_by_query() + "\n"
        if self._skip:
            q += f"SKIP {self._skip}\n"
        if self._limit:
            q += f"LIMIT {self._limit}"
        return q

    def _build_query(self, include_returns=True):
        self._query += self._build_match_query() + "\n" \
                       + self._build_where_query() + "\n"
        if include_returns:
            self._query += self._build_return_query() + "\n"
        self._query += self._build_post_return_query()

    def with_(self, *variables):
        if self._return:
            raise PentaQuarkInvalidQueryException("Can not use WITH statement after RETURN")
        if self._order_by:
            raise PentaQuarkInvalidQueryException("Can not use WITH after ORDER BY")
        self._query += (
                self.get_query(include_returns=False)
                + "\n"
                + "WITH " + ", ".join(variables)
                + "\n"
        )
        return MatchQueryBuilder(
            self.model,
            query=self._query,
            variables=variables,
            parameter_store=self._param_store
        )
