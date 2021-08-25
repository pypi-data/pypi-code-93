import numpy as np


def normal(xyshape, ntimes, stats=None):
    stats = (1.0, 1.0) if stats is None else stats
    stats = [stats] if not isinstance(stats, list) else stats
    data = []
    for time in range(ntimes):
        np.random.seed(time)
        data.append(np.array([np.random.normal(x[0], x[1], xyshape) for x in stats]))
    return data
