import logging
from pentaquark.constants import START_NODE_ALIAS, SEPARATOR
from pentaquark.patterns import N, P
from pentaquark.utils import split_kwargs_into_first_level_and_remaining, unflatten_dict

logger = logging.getLogger(__name__)


class PatternBuilder:
    """
    Helper class to build a pattern ()-[]-() (optionally with multiple hops)
    Manages parameters
    """
    def __init__(self,
                 model,
                 param_store,
                 start_node_alias=None,
                 create_aliases=True,
                 variables_in_external_scope=None,
                 append_to_global_scope=True,
                 ):
        """

        :param model:
        :param param_store:
        :param start_node_alias:
        :param create_aliases:
        :param variables_in_external_scope:
        :param append_to_global_scope:
        """
        self.model = model
        self._param_store = param_store
        self.start_node_alias = start_node_alias or START_NODE_ALIAS
        self.create_aliases = create_aliases
        self._global_scope = variables_in_external_scope if variables_in_external_scope is not None else []
        self._local_scope = self._global_scope if append_to_global_scope else []

    @staticmethod
    def _parse_kwargs_tree(**kwargs):
        return unflatten_dict(**kwargs)

    def build(self, data, include_alias=True, include_label=True):
        ks = self._parse_kwargs_tree(**data)
        if self.model.is_bound():
            first_level_ks, remaining_ks = split_kwargs_into_first_level_and_remaining(self.model, data=ks)
        else:
            first_level_ks = ks
            remaining_ks = {}
        logger.debug(f"PATTERN_BUILDER: BUILD: {ks=}, {first_level_ks=}, {remaining_ks=}")
        # if len(remaining_ks) > 1:
        #     # do not allow 'branching', ie (a)-[r1]-(b) and (a)-[r2]-(c)
        #     # only direct paths are supported for now (a)-[r1]-(b)-[r2]-(c)
        #     print(self.start_node_alias)
        #     raise PentaQuarkInvalidMatchOperationException(
        #         "Branching not supported in MATCH clause, maybe you can use a WHERE instead?"
        #     )
        params = self.model.kwargs_to_cypher(**first_level_ks)
        include_init_label = self.start_node_alias not in self._global_scope
        n = self.model.to_cypher_match(
            alias=self.start_node_alias,
            param_store=self._param_store,
            include_label=include_init_label,
            include_alias=True,
            data=params,
        )
        patterns = []
        if include_init_label or params:  # n contains important information
            patterns.append(n)
        self._local_scope.append(n.alias)
        for k, v in remaining_ks.items():
            n = N(
                alias=n.alias,
                param_store=self._param_store,
            )
            p = P(left_node=n, param_store=self._param_store)

            if self.create_aliases:
                var = START_NODE_ALIAS + SEPARATOR + k
                self._local_scope.append(var)
            else:
                var = None
            h = self.model.traverse_cypher(
                k,
                alias=var,
                variables=self._global_scope,
                param_store=self._param_store,
                include_alias=include_alias,
                include_label=include_label,
                data=v,
            )
            p = p & h
            patterns.append(p)

        return ", ".join(p.repr() for p in patterns)
