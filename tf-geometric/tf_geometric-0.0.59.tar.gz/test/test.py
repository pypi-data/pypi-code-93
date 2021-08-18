import tf_geometric as tfg
import numpy as np
edge_index = [
    [0, 1, 2, 3, 0, 1, 2, 2, 1, 2, 3],
    [0, 1, 2, 3, 1, 2, 3, 3, 2, 1, 0]
]

edge_weight = [0.1, 0.2, 0.5, 0.2, 0.7, 0.8, 0.1, 0.2, 0.1, 0.5, 0.2]

graph0 = tfg.Graph(x=np.random.randn(10, 5), edge_index=edge_index, edge_weight=edge_weight)

edge_index = [
    [0, 1, 3, 3, 4, 4, 7],
    [0, 1, 2, 3, 6, 6, 0]
]

edge_weight = [0.5, 0.2, 0.1, 0.5, 0.2, 0.5, 0.1]
# edge_graph_index = [0, 1, 5, 3, 1, 3, 0]
graph1 = tfg.Graph(x=np.random.randn(8, 5), edge_index=edge_index, edge_weight=edge_weight)

batch_graph = tfg.BatchGraph.from_graphs([graph0, graph1])

print(batch_graph.edge_index)
print(batch_graph.edge_weight)
print(batch_graph.edge_graph_index)
batch_graph.convert_edge_to_directed()

print("=========")

print(batch_graph.edge_index)
print(batch_graph.edge_weight)
print(batch_graph.edge_graph_index)

# print(convert_edge_to_upper(edge_index, [edge_weight, edge_graph_index], merge_modes=["sum", "max"]))

# print(convert_edge_to_directed(edge_index, [edge_weight, edge_graph_index], ["sum", "max"]))

def test(a):
    """

    :param a:
    :return:
    """
    pass