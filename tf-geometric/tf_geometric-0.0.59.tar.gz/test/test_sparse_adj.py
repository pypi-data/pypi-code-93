# edge_index = [
#     [0, 0, 0, 0, 1, 1, 4, 6],
#     [0, 2, 4, 6, 2, 3, 6, 8]
# ]
#
# adj = SparseAdj(edge_index)
# print("==========")
# print(adj.reduce_sum(axis=-1, keepdims=True))
# # h = np.random.randn(9, 20).astype(np.float32)
# #
# # print(adj @ h)
# # print(adj.softmax(axis=-1))