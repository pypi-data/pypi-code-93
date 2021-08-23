from pollination.honeybee_radiance.matrix import MatrixMultiplication
from queenbee.plugin.function import Function


def test_matrix_multiplication():
    function = MatrixMultiplication().queenbee
    assert function.name == 'matrix-multiplication'
    assert isinstance(function, Function)
