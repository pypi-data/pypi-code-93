import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from lcase.causality import triad
from lcase.datasets.simulation import SyntheticData


def test_triad(adj_matrix, latent_size):
    data_gen = SyntheticData(sem_type='uniform', power=5.0)
    W = SyntheticData.to_weight_matrix(adj_matrix)
    data = data_gen.simulate_data(W, 1000)[:, latent_size:]
    g = triad(data, 0.05)
    # print(g)
    pos = nx.nx_pydot.graphviz_layout(g, prog="dot")
    nx.draw_networkx(g, pos, with_labels=True)
    plt.show()


def main():
    # adj_matrix = np.array([
    #     [0, 1, 1, 1, 0, 0],
    #     [0, 0, 0, 0, 1, 1],
    #     [0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0]
    # ])
    adj_matrix = np.array([
        [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])
    test_triad(adj_matrix=adj_matrix,latent_size=5)


if __name__ == '__main__':
    main()
