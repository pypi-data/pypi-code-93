# coding=utf-8
from scipy.sparse import csr_matrix
import numpy as np

from tf_geometric.datasets import MultiLabelBlogCatalogDataset

edge_index, y = MultiLabelBlogCatalogDataset().load_data()
num_nodes = y.shape[0]
num_classes = y.shape[1]

row, col = edge_index

adj = csr_matrix((np.ones_like(row), (row, col)), shape=[num_nodes, num_nodes])

adj_t = csr_matrix((np.ones_like(row), (col, row)), shape=[num_nodes, num_nodes])
import tensorflow as tf
import tf_geometric as tfg
x = tf.sparse.eye(num_nodes)
gcn = tfg.layers.GCN(num_classes)

# logits = gcn([x, edge_index])
#
# loss = tf.nn.sigmoid_cross_entropy_with_logits(
#     logits=logits,
#     labels=y
# )

graph = tfg.Graph(x=x, edge_index=edge_index, y=y)
logits = gcn([graph.x, graph.edge_index])

loss = tf.nn.sigmoid_cross_entropy_with_logits(
    logits=logits,
    labels=y
)

print(loss)



# print(edge_index)
# print(y)