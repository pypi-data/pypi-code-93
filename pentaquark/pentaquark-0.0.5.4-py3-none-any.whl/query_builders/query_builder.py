"""Query Builder commons
"""
import logging

from neo4j.graph import Node as Neo4jNode, Relationship as Neo4jRelationship

from pentaquark.constants import START_NODE_ALIAS
from pentaquark.db import connection
from pentaquark.exceptions import PentaQuarkObjectDoesNotExistError, PentaQuarkCardinalityError
from pentaquark.mixins import IteratorMixin
# from pentaquark.registry import node_registry
from .param_store import ParameterStore
from .result_query_builder import ResultQueryBuilder

logger = logging.getLogger(__name__)


class QueryBuilder(IteratorMixin):
    """Cypher query builder"""

    def __init__(self, model, query="", variables=None, parameter_store=None):
        """Query builder
        :param model: Node class
        """
        super().__init__()
        self.model = model

        self._param_store = parameter_store or ParameterStore()
        """Dict of query parameters"""
        self._alias = START_NODE_ALIAS

        self._match = []
        """Match clauses"""
        self._where = []
        """Where clauses"""
        self._return = []
        """Entities to return"""
        self._query = query or ""
        """Cypher query string"""
        self._query_built = False
        """Set to True when the query has been built for this QueryBuilder instance"""
        self._variables = list(variables) if variables else []
        """Intended to save already matched entities, to reuse them further away
        in the query, without having to rewrite the full pattern."""

    def with_(self, *args):
        return self

    def returns(self, *args, data=None):
        if len(args) > 0 and data is not None:
            raise TypeError("You must provide either data or list of return values")
        self._return.extend(args)
        return self

    def _build_query(self, include_returns=True):
        pass

    def get_query(self, include_returns=True):
        if not self._query_built:
            self._build_query(include_returns=include_returns)
            self._query_built = True
        # logger.debug("QUERY_BUILDER: query: %s", self._query)
        return self._query

    def _returns_to_cypher(self, _returns, start_node_alias: str = START_NODE_ALIAS) -> str:
        """
        Returns Cypher

        :param str start_node_alias:
        :return: Cypher string
        """
        rqb = ResultQueryBuilder(self.model, _returns, start_node_alias)
        return rqb.parse()

    def raw(self):
        self._fetch(raw=True)
        return self

    def get_params(self):
        return self._param_store.params

    def _fetch(self, raw=False):
        query = self.get_query()
        params = self.get_params()
        results = connection.cypher(query, params)
        if raw:
            self._data = results
        else:
            self._data = self._hydrate(results)
        self._executed = True

    def _hydrate(self, results: list) -> list:
        logger.debug("_hydrate %s", results)
        hydrated = []
        for r in results:
            for k, v in r.items():
                if isinstance(v, Neo4jNode):
                    label = list(v.labels)[0]
                    # klass = node_registry[label]
                    klass = self.model
                    if klass is None:  # can this really happen?
                        raise ValueError(f"{label} is not mapped to an object")
                    hydrated.append(
                        klass.hydrate(**dict(v.items()))
                    )
                elif isinstance(v, Neo4jRelationship):
                    pass
                elif isinstance(v, dict):
                    # infer node class from key
                    if k == START_NODE_ALIAS:
                        klass = self.model
                        hydrated.append(
                            klass.hydrate(**v)
                        )
        return hydrated

    # ACCESSORS
    def one(self, check_unique=False):
        it = iter(self)
        try:
            res = next(it)
        except StopIteration:
            raise PentaQuarkObjectDoesNotExistError("Does not exist")
        if check_unique:
            try:
                next(it)
            except StopIteration:
                pass
            else:
                raise PentaQuarkCardinalityError("More than one result")
        return res

    def all(self, limit=None):
        data = list(self)
        if limit:
            return data[:limit]
        return data

    def exists(self):
        try:
            return next(iter(self))
        except StopIteration:
            return None


class RawQueryBuilder(QueryBuilder):
    def __init__(self, model, query, parameters=None):
        super().__init__(model)
        self._query = query
        self.parameters = parameters

    def get_params(self):
        return self.parameters
