"""
Work in Progress
"""
import warnings

from pentaquark.exceptions import PentaQuarkWarning
from pentaquark.properties import Property


class CypherProperty(Property):
    def __init__(self, /, required=False, allow_null=True, default=None, exposed=True, cypher="", return_type=""):
        warnings.warn("CypherProperty is currently experimental", PentaQuarkWarning)
        if not cypher:
            raise TypeError("CypherProperty must have a `cypher` parameter")
        if not return_type:
            raise TypeError("CypherProperty must have a `return_type` parameter")
        super().__init__(required=required, allow_null=allow_null, default=default, exposed=exposed)
        self._set_return_type(return_type)
        self._set_cypher(cypher)

    def _set_cypher(self, cypher):
        self.cypher = cypher

    def _set_return_type(self, return_type):
        self.return_type = return_type

    def get_graphql_type(self):
        return self.graphql_type

    def to_cypher(self, start_node_alias):
        cypher = """[x IN apoc.cypher.runFirstColumn(
                        "WITH $this as this MATCH (this)-[:ACTED_IN]->(m:Movie) RETURN count(m)",
                        {this: %s})
                    ]""" % start_node_alias
        return cypher
        # self.cypher.replace("this", start_node_alias)
