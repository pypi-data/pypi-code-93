import os
import pytest
import numpy as np
import xarray as xr
import pickle
import pkg_resources as pkgr
import warnings

from mdtf_test_data.synthetic import dataset_stats
from mdtf_test_data.synthetic import write_to_netcdf
from mdtf_test_data.synthetic import generate_synthetic_dataset

from mdtf_test_data.synthetic.time import generate_daily_time_axis
from mdtf_test_data.synthetic.time import generate_hourly_time_axis
from mdtf_test_data.synthetic.time import generate_monthly_time_axis
from mdtf_test_data.synthetic.time import xr_times_from_tuples

from mdtf_test_data.synthetic.vertical import gfdl_plev19_vertical_coord
from mdtf_test_data.synthetic.vertical import gfdl_vertical_coord
from mdtf_test_data.synthetic.vertical import ncar_hybrid_coord

__all__ = [
    "test_xr_times_from_tuples_ncar",
    "test_write_to_netcdf",
    "test_ncar_hybrid_coord",
    "test_gfdl_plev19_vertical_coord",
    "test_gfdl_vertical_coord",
    "test_generate_random_array",
    "test_generate_daily_time_axis",
    "test_generate_hourly_time_axis",
    "test_generate_monthly_time_axis",
    "test_generate_synthetic_dataset",
    "test_dataset_stats",
]


def pytest_namespace():
    return {
        "ds_gfdl": None,
        "ds_ncar": None,
        "ncar_hybrid": None,
        "gfdl_plev19": None,
        "gfdl_vert": None,
        "dummy_dset": None,
    }


@pytest.mark.parametrize("timefmt", ["gfdl", "ncar"])
def test_xr_times_from_tuples_ncar(timefmt):
    bounds = [(1, 1, 1), (2, 1, 1), (3, 1, 1)]
    times = [(1, 7, 15), (2, 7, 15)]
    result = xr_times_from_tuples(times, bounds, timefmt=timefmt)
    assert isinstance(result, xr.Dataset)
    assert "base_time_unit" in result.attrs.keys()
    if timefmt == "gfdl":
        assert sorted(list(result.variables)) == [
            "average_DT",
            "average_T1",
            "average_T2",
            "time",
            "time_bnds",
        ]
        assert sorted(list(result.dims)) == ["bnds", "time"]
        pytest.ds_gfdl = result
    elif timefmt == "ncar":
        assert sorted(list(result.variables)) == ["date", "time", "time_bnds"]
        assert sorted(list(result.dims)) == ["nbnds", "time"]
        pytest.ds_ncar = result
    else:
        assert False, f"Unknown format: {timefmt}"


def test_write_to_netcdf():
    outfile = ".pytest.dummy.out.nc"
    if os.path.exists(outfile):
        os.remove(outfile)
    write_to_netcdf(pytest.ds_gfdl, outfile)
    assert os.path.exists(outfile)
    if os.path.exists(outfile):
        os.remove(outfile)


def test_ncar_hybrid_coord():
    result = ncar_hybrid_coord()
    assert isinstance(result, xr.Dataset)
    assert np.allclose(float(result.lev.sum()), 18419.680589)
    assert np.allclose(float(result.hyam.sum()), 4.999968233351692)
    assert np.allclose(float(result.hybm.sum()), 13.419714)
    pytest.ncar_hybrid = result


def test_gfdl_plev19_vertical_coord():
    result = gfdl_plev19_vertical_coord()
    assert isinstance(result, xr.Dataset)
    assert np.allclose(float(result.plev19.sum()), 616100.0)
    pytest.gfdl_plev19 = result


def test_gfdl_vertical_coord():
    result = gfdl_vertical_coord()
    assert isinstance(result, xr.Dataset)
    assert np.allclose(float(result.pfull.sum()), 14932.053848)
    assert np.allclose(float(result.phalf.sum()), 15444.908725)
    pytest.gfdl_vert = result


def test_generate_daily_time_axis():
    result = generate_daily_time_axis(1850, 2)
    assert isinstance(result, xr.Dataset)
    assert len(result.time) == 730
    assert int(result.time[1] - result.time[0]) == 86400000000000


@pytest.mark.parametrize(
    "dhour,length,dt", [(3, 2920, 10800000000000), (4, 2190, 14400000000000)]
)
def test_generate_hourly_time_axis(dhour, length, dt):
    result = generate_hourly_time_axis(1971, 1, dhour)
    assert isinstance(result, xr.Dataset)
    assert len(result.time) == length
    assert int(result.time[1] - result.time[0]) == dt


def test_generate_monthly_time_axis():
    result = generate_monthly_time_axis(1931, 5)
    assert isinstance(result, xr.Dataset)
    assert len(result.time) == 60
    assert int(result.time[1] - result.time[0]) == 2419200000000000


def test_generate_synthetic_dataset_1():
    # not sure this is fully portable below
    stats = [(10.0, 1.0) for x in range(0, 19)]
    result = generate_synthetic_dataset(
        180,
        90,
        1860,
        2,
        "dummy",
        attrs={"test_attribute": "some_value"},
        fmt="gfdl",
        generator="normal",
        stats=stats,
    )

    pytest.dummy_dset = result
    xr_version = tuple([int(x) for x in xr.__version__.split(".")])
    if xr_version < (0, 17, 0):
        warnings.warn(
            "The version of Xarray is outdated. Consider "
            + "upgrading to version >= 0.17.0"
        )
        pytest.skip()

    ref_file = pkgr.resource_filename("mdtf_test_data", "tests/ref_synth_dset.nc")

    if os.path.exists(ref_file):
        reference = xr.open_dataset(ref_file)
        assert result.equals(reference)
    else:
        warnings.warn("Unable to compare against reference dataset")
        # below are lines to write out the reference file
        # result.time.encoding["units"] = "days since 0001-01-01 00:00:00"
        # result.to_netcdf("ref_synth_dset.nc")


def test_generate_synthetic_dataset_2():
    stats = [(10.0, 1.0) for x in range(0, 19)]
    result = generate_synthetic_dataset(
        180,
        90,
        1860,
        1,
        "dummy_var_2",
        timeres="1hr",
        attrs={"test_attribute": "some_value"},
        fmt="gfdl",
        generator="convective",
        generator_kwargs={"varname": "pr"},
    )
    assert isinstance(result, xr.Dataset)
    assert len(result.time) == 8760


def test_dataset_stats():
    outfile = ".pytest.dummy.out.nc"

    if os.path.exists(outfile):
        os.remove(outfile)
    write_to_netcdf(pytest.dummy_dset, outfile)
    assert os.path.exists(outfile)

    result = dataset_stats(outfile, var="dummy")
    result = np.array(result)
    reference = np.array(
        [
            (10.017495155334473, 1.0194365978240967),
            (9.847151756286621, 1.0603336095809937),
            (10.118196487426758, 0.9625908732414246),
            (9.954728126525879, 0.8641798496246338),
            (10.177528381347656, 0.9840584993362427),
            (10.048087120056152, 1.0727150440216064),
            (9.969891548156738, 0.9925058484077454),
            (10.043947219848633, 1.1448439359664917),
            (9.788042068481445, 0.9455227851867676),
            (9.98440170288086, 0.9929303526878357),
            (9.975597381591797, 0.9340150356292725),
            (10.185722351074219, 0.9520735144615173),
            (9.898139953613281, 1.0450271368026733),
            (10.102021217346191, 0.9363077282905579),
            (10.039666175842285, 0.9595484733581543),
            (9.8911714553833, 1.005807876586914),
            (9.9674711227417, 1.0527175664901733),
            (10.098736763000488, 1.1312658786773682),
            (10.204208374023438, 0.9746913313865662),
        ]
    )
    if os.path.exists(outfile):
        os.remove(outfile)
    assert np.allclose(result, reference)
