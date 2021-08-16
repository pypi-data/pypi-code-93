import enum
import logging

from pentaquark.constants import START_NODE_ALIAS, SEPARATOR
from pentaquark.exceptions import PentaQuarkConfigurationError
from pentaquark.lookups import LOOKUP_REGISTRY
from .pattern_builder import PatternBuilder

logger = logging.getLogger(__name__)


class LogicalOperators(enum.Enum):
    AND = "AND"
    OR = "OR"
    EXISTS = "EXISTS"


class Predicate:
    def __init__(self):
        self._queries = None
        self._param_store = None
        self._variables = None
        self._model = None

    def __bool__(self):
        return bool(self._queries)

    def __and__(self, other):
        if not self:
            return C(other.queries)
        if not other:
            return C(self.queries)
        return C({
            LogicalOperators.AND: [self._queries, other.queries]
        })

    def __or__(self, other):
        if not self:
            return C(other.queries)
        if not other:
            return C(self.queries)
        return C({
            LogicalOperators.OR: [self._queries, other.queries]
        })

    def __eq__(self, other):
        return sorted(set(self.queries)) == sorted(set(other.queries))

    def __str__(self):
        return f"{self.__class__.__name__}: {self.queries}"

    @property
    def queries(self):
        return self._queries

    def _parse_final(self, key, value):
        raise NotImplementedError()
        # return predicate.to_cypher(key, value)

    def _parse(self, queries):
        if len(queries) > 1:
            raise Exception("This is a bug")
        k, v = next(iter(queries.items()))
        if k in (LogicalOperators.AND, LogicalOperators.OR):
            q = []
            for sub_v in v:
                q.append(self._parse(sub_v))
            return "(" + f" {k} ".join(q) + ")"
        elif k == LogicalOperators.EXISTS:
            return Exists(v).compile(param_store=self._param_store, model=self._model, variables=self._variables)
        else:
            return C(v).compile(param_store=self._param_store, variables=self._variables)

    def compile(self, model, param_store, variables=None):
        self._model = model
        self._param_store = param_store
        self._variables = variables or []
        return self._parse(self._queries)


class C(Predicate):
    """Lookup Predicate"""
    def __init__(self, *args, **kwargs):
        super().__init__()
        if args:
            if len(args) > 1:
                raise PentaQuarkConfigurationError("C conditions take only one argument")
            self._queries = args[0]
        elif kwargs:
            if len(kwargs) == 1:
                self._queries = kwargs
            else:
                self._queries = {
                    LogicalOperators.AND: [{k: v} for k, v in kwargs.items()]
                }
        else:
            self._queries = {}

    def _to_cypher(self, left, op, right, param_name):
        pn = self._param_store.add(param_name, right)
        return f"{left} {op} ${pn}"

    def _to_cypher_lookup(self, left, right, lookup):
        return lookup().to_cypher(left, right, self._param_store)

    def _parse_final(self, key, value):
        # FIXME: we can't filter on variables in the scope without accessing a property
        if not key.startswith(START_NODE_ALIAS):  # TODO: ideally, this check should be done before
            key = START_NODE_ALIAS + SEPARATOR + key
        if "__" not in key:  # FIXME: should not happen, to be checked
            logger.warning(f"QB: WHERE: separator missing from key {key}")
            return self._to_cypher(key, "=", value, key)
        variable, field_or_lookup = key.rsplit("__", 1)
        if field_or_lookup in LOOKUP_REGISTRY:
            lookup = LOOKUP_REGISTRY[field_or_lookup]
            variable, field = variable.rsplit("__", 1)
            if variable not in self._variables and variable != START_NODE_ALIAS:
                raise AttributeError(
                    f"'{variable}' is not in the query scope, can not filter on it ({self._variables})")
            # FIXME: need to check that prop is a valid property for the 'variable' model
            return self._to_cypher_lookup(variable + "." + field, value, lookup)
        else:
            if variable not in self._variables and variable != START_NODE_ALIAS:
                raise AttributeError(
                    f"'{variable}' is not in the query scope, can not filter on it ({self._variables})")
            return self._to_cypher(variable + "." + field_or_lookup, "=", value, key)

    def _parse_final_exists(self, data):
        logger.debug("WQB._parse_final_exists, variables=%s", self._variables)
        pb = PatternBuilder(
            self._model,
            self._param_store,
            start_node_alias=START_NODE_ALIAS,
            create_aliases=False,
            variables_in_external_scope=self._variables,
            append_to_global_scope=False
        )
        pattern = pb.build(data)
        return f"EXISTS({pattern})"

    def _parse(self, queries):
        if len(queries) > 1:
            raise Exception("This is a bug")
        k, v = next(iter(queries.items()))
        if k in (LogicalOperators.AND, LogicalOperators.OR):
            q = []
            for sub_v in v:
                q.append(self._parse(sub_v))
            return "(" + f" {k.value} ".join(q) + ")"
        if k == LogicalOperators.EXISTS:
            if len(v) > 1:
                logger.warning("WHERE, EXIST more than one predicate? %s", v)
            return self._parse_final_exists(v)
        else:
            return self._parse_final(k, v)

    def compile(self, model, param_store, variables=None):
        self._model = model
        self._param_store = param_store
        self._variables = variables or []
        logger.debug("WHERE _queries %s", self._queries)
        return self._parse(self._queries)


class Exists(Predicate):
    """
    "EXISTS" Cypher predicate function, with pattern argument
    TODO: support for pattern without attributes, ie we need to be able to build the pattern from a string:
        eg: "movies__director" or "attribute_instance__attribute"
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        q = None
        if args and kwargs:
            raise PentaQuarkConfigurationError("Exists predicate only understand either args or kwargs")
        if args:
            if len(args) > 1:
                raise PentaQuarkConfigurationError("Exists predicate only understand one single argument. "
                                                   "Use several Exists if several conditions are required.")
            q = args[0]
        elif kwargs:
            q = kwargs
        self._queries = {LogicalOperators.EXISTS: q}

    def _get_pattern(self, param_store, variables):
        pb = PatternBuilder(
            model=self._model, param_store=param_store, variables_in_external_scope=variables,
            append_to_global_scope=False
        )
        return pb.build(include_alias=False, include_label=True, **self._queries[LogicalOperators.EXISTS])

    def _parse_final(self, key, value):
        pattern = self._get_pattern(self._param_store, self._variables)
        return f"EXISTS({pattern})"
