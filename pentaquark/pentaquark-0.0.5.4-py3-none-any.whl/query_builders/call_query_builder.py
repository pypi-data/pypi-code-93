"""Where the MATCH Cypher query is built.
"""
import logging
from pentaquark.constants import START_NODE_ALIAS
from . import MatchQueryBuilder


logger = logging.getLogger(__name__)


class CallQueryBuilder(MatchQueryBuilder):
    """CALL query builder"""

    def __init__(self, model, procedure, yield_names, yield_node_name="node"):
        super().__init__(model)
        self._call = ""
        self.procedure = procedure
        self.yield_names = yield_names
        self.yield_node_name = yield_node_name

    def call(self, *args):
        # db.index.fulltext.queryNodes
        ags = ','.join([f"'{a}'" for a in args])
        self._call = f"CALL {self.procedure}({ags}) YIELD {self.yield_names} " \
                     f"WITH {self.yield_names}, {self.yield_node_name} as {START_NODE_ALIAS} "
        self._variables.extend(self.yield_names.split(","))
        self._variables.append(START_NODE_ALIAS)
        return self

    def _build_match_query(self):
        return self._call
