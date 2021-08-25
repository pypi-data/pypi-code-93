import numpy as np
import pytest
import mdtf_test_data.generators as generators


def test_generate_random_array_normal():
    stats = [(5.0, 10.0), (50.0, 100.0)]
    generator = generators.__dict__["normal"]
    generator_kwargs = {"stats": stats}
    result = generators.generate_random_array(
        (20, 20), 5, generator=generator, generator_kwargs=generator_kwargs
    )
    assert result.shape == (5, 2, 20, 20)
    assert np.allclose(result.sum(), 104847.61)
    assert np.allclose(
        (result[:, 0, :, :].mean(), result[:, 0, :, :].std()), (5.2270184, 10.07385)
    )
    assert np.allclose(
        (result[:, 1, :, :].mean(), result[:, 1, :, :].std()), (47.196785, 98.86136)
    )


@pytest.mark.parametrize(
    "varname,expected",
    [
        ("tave", 540084.0),
        ("qsat_int", 131016.664),
        ("cwv", 115304.7),
        ("pr", 0.0012361809),
    ],
)
def test_generate_random_array_convective(varname, expected):
    generator = generators.__dict__["convective"]
    generator_kwargs = {"varname": varname}
    result = generators.generate_random_array(
        (20, 20), 5, generator=generator, generator_kwargs=generator_kwargs
    )
    print(varname, result.sum())
    assert result.shape == (5, 20, 20)
    assert np.allclose(result.sum(), expected)
