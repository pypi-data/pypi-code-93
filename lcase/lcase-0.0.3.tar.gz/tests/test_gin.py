import numpy as np

from lcase.causality import gin
from lcase.datasets.simulation import SyntheticData

def test_gin(adj_matrix, latent_size):
    data_gen = SyntheticData(sem_type='uniform', power=5.0)
    W = SyntheticData.to_weight_matrix(adj_matrix)
    data = data_gen.simulate_data(W, 1000)[:, latent_size:]
    k = gin(data)
    print(k)


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
        [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])
    test_gin(adj_matrix=adj_matrix,latent_size=3)


if __name__ == '__main__':
    main()
