#!/usr/bin/env python

"""Tests for `xarray_pickler` package."""

__author__ = """Elle Smith"""
__contact__ = "eleanor.smith@stfc.ac.uk"
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import os
import shutil
import tempfile

import xarray as xr

from xarray_pickler import CONFIG, open_dset
from xarray_pickler.xarray_pickler import _get_pickle_name, _get_pickle_path

from .conftest import MINI_ESGF_CACHE_DIR


def test_get_pickle_name():
    dpath = "/badc/cmip6/data/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/historical/r1i1p1f1/Amon/rlds/gr/v20180803"

    pickle_name = _get_pickle_name(dpath)

    assert (
        pickle_name
        == "/badc/cmip6/data/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/historical/r1i1p1f1/Amon.rlds.gr.v20180803.pickle"
    )


def test_remove_archive_in_path_dir_pickle_name():
    dpath = f"{MINI_ESGF_CACHE_DIR}/master/test_data/badc/cmip6/data/CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon/rlds/gr1/v20190610"

    pickle_name = _get_pickle_name(dpath)

    assert (
        pickle_name
        == "CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon.rlds.gr1.v20190610.pickle"
    )


def test_get_pickle_name_replace_chars():
    dpath = "/badc/cmip6/data/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/historical/r1i1p1f1/Amon/*/*/v201808??"

    pickle_name = _get_pickle_name(dpath)

    assert (
        pickle_name
        == "/badc/cmip6/data/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/historical/r1i1p1f1/Amon.all.all.v201808__.pickle"
    )


def test_get_pickle_path_write():
    pickle = (
        "CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon.rlds.gr1.v20190610.pickle"
    )

    pickle_path = _get_pickle_path(pickle, "w")

    assert pickle_path.endswith(
        "/otherdir/CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon.rlds.gr1.v20190610.pickle"
    )


def test_get_pickle_path_write_no_writeable_dir():
    writeable_dir = CONFIG["paths"]["writeable_pickle_dir"]
    CONFIG["paths"]["writeable_pickle_dir"] = ""

    pickle = (
        "CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon.rlds.gr1.v20190610.pickle"
    )

    pickle_path = _get_pickle_path(pickle, "w")

    assert pickle_path is None

    # reset CONFIG
    CONFIG["paths"]["writeable_pickle_dir"] = writeable_dir


def test_get_pickle_path_read_no_pickle_file():
    pickle = (
        "CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon.rlds.gr1.v20190610.pickle"
    )

    pickle_path = _get_pickle_path(pickle, "r")

    assert pickle_path is None


def test_get_pickle_path_read_file_in_primary_dir():

    pickle = (
        "CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon.rlds.gr1.v20190610.pickle"
    )

    #  put a pickle file in the primary dir for the test
    primary_dir = CONFIG["paths"]["pickle_dirs"][0]
    pickle_file = os.path.join(primary_dir, pickle)

    os.makedirs(os.path.dirname(pickle_file), exist_ok=True)
    f = open(pickle_file, "a")
    f.close()

    pickle_path = _get_pickle_path(pickle, "r")

    assert pickle_path.endswith(
        "/fakedir/CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon.rlds.gr1.v20190610.pickle"
    )

    # delete the test primary pickle dir
    shutil.rmtree(CONFIG["paths"]["pickle_dirs"][0])


def test_get_pickle_path_read_file_in_second_dir(load_test_data):
    dpath = f"{MINI_ESGF_CACHE_DIR}/master/test_data/badc/cmip6/data/CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon/rlds/gr1/v20190610"

    #  write pickle file in secondary dir
    open_dset(dpath)

    pickle = (
        "CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon.rlds.gr1.v20190610.pickle"
    )

    pickle_path = _get_pickle_path(pickle, "r")

    assert pickle_path.endswith(
        "/otherdir/CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon.rlds.gr1.v20190610.pickle"
    )

    # delete the test writeable pickle dir
    shutil.rmtree(CONFIG["paths"]["writeable_pickle_dir"])


def test_open_dset_default_kwargs(load_test_data):
    dpath = f"{MINI_ESGF_CACHE_DIR}/master/test_data/badc/cmip6/data/CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon/rlds/gr1/v20190610/"

    ds_original = xr.open_mfdataset(
        f"{dpath}/*nc", use_cftime=True, combine="by_coords"
    )

    # will write pickle file
    ds = open_dset(dpath)

    assert ds == ds_original

    #  try and open again now that it has been pickled
    ds_from_pickle = open_dset(dpath)

    assert ds_from_pickle == ds_original

    # delete the test writeable pickle dir
    shutil.rmtree(CONFIG["paths"]["writeable_pickle_dir"])


def test_open_dset_extra_kwargs(load_test_data):
    dpath = f"{MINI_ESGF_CACHE_DIR}/master/test_data/badc/cmip6/data/CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon/rlds/gr1/v20190610/"

    ds_original = xr.open_mfdataset(f"{dpath}/*nc")

    assert "lon_bnds" in ds_original.variables

    #  check extra kwargs are being picked up
    ds = open_dset(dpath, drop_variables=["lon_bnds"])

    assert "lon_bnds" not in ds.variables

    # delete the test writeable pickle dir
    shutil.rmtree(CONFIG["paths"]["writeable_pickle_dir"])


def test_open_dset_force_repickle(load_test_data):
    dpath = f"{MINI_ESGF_CACHE_DIR}/master/test_data/badc/cmip6/data/CMIP6/CMIP/INM/INM-CM5-0/historical/r1i1p1f1/Amon/rlds/gr1/v20190610/"

    ds_original = xr.open_mfdataset(
        f"{dpath}/*nc", use_cftime=True, combine="by_coords"
    )

    ds_pickle = open_dset(dpath)

    assert ds_pickle == ds_original

    ds_repickle = open_dset(dpath, force_repickle=True)

    assert ds_repickle == ds_original

    # delete the test writeable pickle dir
    shutil.rmtree(CONFIG["paths"]["writeable_pickle_dir"])


def test_curvilinear_dataset(load_test_data):
    dpath = f"{MINI_ESGF_CACHE_DIR}/master/test_data/badc/cmip6/data/CMIP6/CMIP/MPI-M/MPI-ESM1-2-LR/historical/r1i1p1f1/Omon/tos/gn/v20190710/"

    ds_original = xr.open_mfdataset(
        f"{dpath}/*nc", use_cftime=True, combine="by_coords"
    )

    ds = open_dset(dpath)

    assert ds == ds_original

    ds_pickle = open_dset(dpath)

    assert ds_pickle == ds_original

    # delete the test writeable pickle dir
    shutil.rmtree(CONFIG["paths"]["writeable_pickle_dir"])
