import numpy as np


def partition(collection):
    if len(collection) == 1:
        yield [collection]
        return

    first = collection[0]
    for smaller in partition(collection[1:]):
        # insert `first` in each of the subpartition's subsets
        for n, subset in enumerate(smaller):
            # print([first, subset])
            yield smaller[:n] + [[first] + subset] + smaller[n + 1:]
        # put `first` in its own subset
        yield [[first]] + smaller


def has_single_part(part):
    for i in part:
        if len(i) == 1:
            return True
    return False


def cal_exp(X):
    return np.sum(np.prod(X, axis=1)) / X.shape[0]


def cum(X):
    # print(X.shape)
    X = X - np.mean(X, axis=0)
    cum_stats = 0.0
    parts = partition(list(range(X.shape[1])))
    for part in parts:
        # if has_single_part(part):
        #     continue
        cum_stat = 1.0
        # print(part)
        for i in part:
            # print(np.ix_(range(X.shape[0]), i))
            cum_stat *= cal_exp(X[np.ix_(range(X.shape[0]), i)])
        # print(cum_stat)
        cum_stats += (-1) ** (len(part)) * cum_stat
    return cum_stats


if __name__ == '__main__':
    # X = (np.arange(9)+1).reshape((3,-1))
    # print(cal_exp(X))

    # something = list(range(1, 3))
    #
    # for n, p in enumerate(partition(something), 1):
    #     print(n, sorted(p))
    sample_size = 1000
    L = np.random.uniform(-1, 1, size=sample_size) ** 5
    L = (L - np.mean(L)) / np.std(L)
    X1 = 2 * L + np.random.uniform(-1, 1, size=sample_size) ** 5
    X2 = 3 * L + np.random.uniform(-1, 1, size=sample_size) ** 5
    X3 = 5 * L + np.random.uniform(-1, 1, size=sample_size) ** 5
    X4 = 7 * L + np.random.uniform(-1, 1, size=sample_size) ** 5
    X5 = 11 * L + np.random.uniform(-1, 1, size=sample_size) ** 5

    # L = np.random.laplace(0, 1, size=sample_size)
    # L = (L - np.mean(L)) / np.std(L)
    # X1 = 2 * L + np.random.laplace(0, 1, size=sample_size)
    # X2 = 3 * L + np.random.laplace(0, 1, size=sample_size)
    # X3 = 5 * L + np.random.laplace(0, 1, size=sample_size)
    # X4 = 7 * L + np.random.laplace(0, 1, size=sample_size)
    # X5 = 11 * L + np.random.laplace(0, 1, size=sample_size)

    # L = np.random.uniform(0, 1, size=sample_size)**5
    # L = (L - np.mean(L)) / np.std(L)
    # X1 = L + np.random.normal(0, 1, size=sample_size)
    # X2 = L + np.random.normal(0, 1, size=sample_size)
    # X3 = L + np.random.normal(0, 1, size=sample_size)
    # X4 = L + np.random.normal(0, 1, size=sample_size)
    # print(cum(np.array([L, L, L, L]).T))
    # X5 = L + np.random.normal(0, 1, size=sample_size)

    # X1 = (X1 - np.mean(X1)) / np.std(X1)
    # X2 = (X2 - np.mean(X2)) / np.std(X2)
    # X1 = X1 / np.std(X1)
    # X2 = X2 / np.std(X2)
    # X3 = X3 / np.std(X3)
    cov = np.cov(X1, X2)
    print(cov[1, 1] / cov[0, 1])
    print(cov[0, 1] / cov[1, 1])
    print()

    print(cum(np.array([X2, X2]).T) / cum(np.array([X1, X2]).T))
    print(cum(np.array([X1, X2]).T) / cum(np.array([X2, X2]).T))
    print()

    #
    # print(cum(np.array([X1, X1, X2]).T))
    # print(cum(np.array([X1, X2, X2]).T))

    print(cum(np.array([X2, X1, X2]).T) / cum(np.array([X1, X1, X2]).T))
    print(cum(np.array([X1, X1, X2]).T) / cum(np.array([X2, X1, X2]).T))
    print()

    print(cum(np.array([X2, X1, X2, X1, X2]).T) /
          cum(np.array([X1, X1, X2, X1, X2]).T))
    print(cum(np.array([X1, X1, X2, X1, X2]).T) /
          cum(np.array([X2, X1, X2, X1, X2]).T))
    print()

    # print(cum(np.array([X2, X1, X2, X3, X4]).T) / cum(np.array([X1, X1, X2, X3, X4]).T))
    # print(cum(np.array([X1, X1, X2, X3, X4]).T) / cum(np.array([X2, X1, X2, X3, X4]).T))
    #
    print(cum(np.array([X2, X1, X2, X3, X4, X5]).T) /
          cum(np.array([X1, X1, X2, X3, X4, X5]).T))
    print(cum(np.array([X1, X1, X2, X3, X4, X5]).T) /
          cum(np.array([X2, X1, X2, X3, X4, X5]).T))
