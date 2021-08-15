import pyclesperanto_prototype as cle
import numpy as np


def test_laplace_box():
    test1 = cle.push(np.asarray([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]))

    reference = cle.push(np.asarray([
        [0, 0, 0, 0, 0],
        [0, -1, -1, -1, 0],
        [0, -1, 8, -1, 0],
        [0, -1, -1, -1, 0],
        [0, 0, 0, 0, 0]
    ]))

    result = cle.create(test1)
    cle.laplace_box(test1, result)

    a = cle.pull(result)
    b = cle.pull(reference)

    print(a)

    assert (np.array_equal(a, b))

