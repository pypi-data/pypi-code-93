import sympy as sy
import numpy as np

class Matrix(np.matrix):
    @staticmethod
    def random(shape, min, max):
        def random_matrix_generator():
            rng = np.random.default_rng()
            mat_val = rng.integers( low = min, high = max,
                                    size = shape)
            return sy.Matrix(mat_val.tolist())
        return random_matrix_generator

    @staticmethod
    def full_rank(shape, min, max):
        def random_full_rank_generator():
            rng = np.random.default_rng()
            mat_val = rng.integers( low = min, high = max,
                                    size = shape)
            while(np.linalg.matrix_rank(mat_val) != shape[0]):
                mat_val = rng.integers( low = min, high = max,
                                        size = shape)
            return sy.Matrix(mat_val.tolist())
        return random_full_rank_generator

    """some caveats for the function below: https://stackoverflow.com/questions/10132585/generate-random-matrix-of-certain-rank-over-a-fixed-set-of-elements"""

    @staticmethod
    def with_rank(shape, rank, min, max):
        def random_with_rank_generator():
            r = rank
            assert shape[0] >= r and shape[1] >= r
            trans = False
            m,n = shape
            if m > n: # more columns than rows I think is better
                m, n = n, m
                trans = True
            vals = [i for i in range(min, max + 1)]
            get_vec = lambda: np.array([np.random.choice(vals) for i in range(n)])

            vecs = []
            n_rejects = 0

            # fill in r linearly independent rows
            while len(vecs) < r:
                v = get_vec()
                if np.linalg.matrix_rank(np.vstack(vecs + [v])) > len(vecs):
                    vecs.append(v)
                else:
                    n_rejects += 1
            print("have {} independent ({} rejects)".format(r, n_rejects))

            # fill in the rest of the dependent rows
            while len(vecs) < m:
                v = get_vec()
                if np.linalg.matrix_rank(np.vstack(vecs + [v])) > len(vecs):
                    n_rejects += 1
                    if n_rejects % 1000 == 0:
                        print(n_rejects)
                else:
                    vecs.append(v)
            print("done ({} total rejects)".format(n_rejects))

            m = np.vstack(vecs)
            m = m.T if trans else m
            return sy.Matrix(m.tolist())
        return random_with_rank_generator

    @staticmethod
    def diagonal(shape, min, max):
        def random_diagonal_generator():

            vals = np.arange(min, max + 1, 1)
            vec=np.random.choice(vals,shape[0])
            mat_val = np.diag(vec)
            return sy.Matrix(mat_val.tolist())

        return random_diagonal_generator

    @staticmethod
    def upper_triangular(shape, min, max):
        def random_upper_triangular_generator():

            rng = np.random.default_rng()
            mat_val = rng.integers( low = min, high = max,
                                    size = shape)
            mat_val = np.triu(mat_val)
            return sy.Matrix(mat_val.tolist())

        return random_upper_triangular_generator
    @staticmethod
    def lower_triangular(shape, min, max):
        def random_lower_triangular_generator():

            rng = np.random.default_rng()
            mat_val = rng.integers( low = min, high = max,
                                    size = shape)
            mat_val = np.tril(mat_val)
            return sy.Matrix(mat_val.tolist())

        return random_lower_triangular_generator

    @staticmethod
    def symmetric(shape, min, max):
        def random_symmetric_generator():

            rng = np.random.default_rng()
            mat_val = rng.integers( low = min, high = max,
                                    size = shape)
            mat_val = np.tril(mat_val) + np.tril(mat_val, -1).T
            return sy.Matrix(mat_val.tolist())

        return random_symmetric_generator

    def to_sympy(self):
        return sy.Matrix(self)
