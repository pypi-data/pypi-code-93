import warnings
import networkx as nx

from lcase.graphs._graphutils import _2str, _edge_data2str_beautify


class CausalGraph(nx.Graph):

    def add_edge(self, u, v, u_tag="o", v_tag="o", **attr):
        attr.update({
            _2str(u): u_tag,
            _2str(v): v_tag
        })
        super(CausalGraph, self).add_edge(u_of_edge=u, v_of_edge=v, **attr)

    def __str__(self):
        graph_name_string = f"Graph Name: {super(CausalGraph, self).__str__()}"

        graph_nodes_string = f"Graph Nodes:\n {self.nodes()}"

        graph_edges_string = f"Graph Edges:\n" + "\n".join(
            [f"{i}. {_edge_data2str_beautify(edge)}"
             for i, edge in enumerate(self.edges.data())])

        return f"{graph_name_string}" \
               f"\n\n" \
               f"{graph_nodes_string}" \
               f"\n\n" \
               f"{graph_edges_string}"

    def modify_endpoint_mark(self, u, v, w, mark):
        assert u == w or v == w
        if not self.has_edge(u, v):
            warnings.warn(f"There is no edge between point {u} and point {v}.", UserWarning)
            return None
        tags = self.get_edge_data(u, v)
        tags[_2str(w)] = mark

    def has_fully_directed_edge(self, u, v):
        if not self.has_edge(u, v):
            return False
        tags = self.get_edge_data(u, v)
        if tags[_2str(u)] == '-' and tags[_2str(v)] == '>':
            return True
        else:
            return False

    def has_o_mark(self, u, v, w):
        assert u == w or v == w
        if not self.has_edge(u, v):
            return False
        tags = self.get_edge_data(u, v)
        if tags[_2str(w)] == 'o':
            return True
        else:
            return False


if __name__ == '__main__':
    g = CausalGraph()
    g.add_edge(2, 3, '>')
    g.add_edge(3, 4)
    print(g)
    g.modify_endpoint_mark(2, 3, 2, '-')
    print(g)

