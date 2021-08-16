import logging
from pentaquark.constants import SEPARATOR, START_NODE_ALIAS, RELATIONSHIP_OBJECT_KEY
from pentaquark.properties import CypherProperty
from pentaquark.utils import unflatten_list

logger = logging.getLogger(__name__)


class ResultQueryBuilder:

    def __init__(self, model, results_var=None, current=START_NODE_ALIAS, start_alias=START_NODE_ALIAS, variables=None):
        self._model = model
        self._results_var = results_var or []
        self._variables = variables
        """_variables is intended to save variables already in scope
        to prevent traversing the graph again. Not fully used for now.
        (only used in where clause, to make sure the variable exists in scope)"""
        self._start_alias = start_alias
        self._current_level = current

    def add_prefix(self, a: str) -> str:
        if not a.startswith(self._start_alias):
            prefix = self._start_alias + SEPARATOR
            return prefix + a
        return a

    def parse(self) -> str:
        if self._start_alias == START_NODE_ALIAS \
                and START_NODE_ALIAS not in self._results_var \
                and not any(START_NODE_ALIAS in item for item in self._results_var) \
                and not any(item in self._model._properties for item in self._results_var):
            self._results_var.append(START_NODE_ALIAS)
        _return = [
            self.add_prefix(a) for a in self._results_var
        ]
        values = unflatten_list(*_return)[0]
        parsed_result = self._parse_result(values)
        return parsed_result

    def _parse_result(self, _return) -> str:
        start = _return
        result = self._start_alias
        if isinstance(start, str):
            if start == self._start_alias:
                return result
            raise Exception("Unmanaged case: %s", self._results_var)
        # if isinstance(start, list):  # FIXME: when does this happen?
        #     return f"{self._start_alias} {{ {self._parse_result_list(start, prev=self._start_alias)} }}"
        return f"{self._start_alias} {{ " \
               f"{self._parse_result_list(start[self._current_level], prev=self._start_alias)} }}"

    def _parse_result_list(self, lst: list, prev="") -> str:
        r = []
        for item in lst:
            if isinstance(item, dict):
                rd = self._parse_result_dict(prev=prev, **item)
                if rd:
                    r += [rd]
                continue
            if item in self._model._graphql_properties:
                continue
            if item == '':
                r += [".*"]
                continue
            if prop := self._model._properties.get(item):
                if isinstance(prop, CypherProperty):
                    r += [f"{item}: {prop.to_cypher(start_node_alias=prev)}"]
                else:
                    r += [f".{item}"]
                continue
            if rel := self._model._relationships.get(item):
                alias = prev + SEPARATOR + item
                rel_pattern = rel.to_cypher_match(alias=alias).repr()
                r += [
                    f"{item}: [({self._start_alias}){rel_pattern} | {self._start_alias}{SEPARATOR}{item} {{ .* }}]"
                ]
                continue
            if item == RELATIONSHIP_OBJECT_KEY:
                rel_alias = f"{prev}{SEPARATOR}{item}"
                r += [
                    f"{RELATIONSHIP_OBJECT_KEY}: [{rel_alias} {{ .* }}]"
                ]
                continue
            raise ValueError(f"{item} not recognised")
        return ",".join(r)

    def _parse_result_dict(self, prev="", **kwargs) -> str:
        r = ""
        for k, v in kwargs.items():
            if k in self._model._graphql_properties:
                continue
            r += f"{k}: [ "
            if k in self._model._relationships:
                rel = self._model._relationships[k]
                alias = prev + SEPARATOR + k
                rel_pattern = rel.to_cypher_match(alias=alias).repr()
                r += f"({self._start_alias}){rel_pattern} | "
                target_node_class = rel.get_target_node_class()
                r += ResultQueryBuilder(start_alias=alias, current=k, model=target_node_class)._parse_result({k: v})
                return r + "]"
            if isinstance(v, str):
                r += f"{v}"
            if isinstance(v, list):
                r += f"{{ {self._parse_result_list(v, prev=prev)} }}"
            r += "]"
        return r
