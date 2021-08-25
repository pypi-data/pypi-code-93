#!/usr/bin/env python
""" Module for generating synthetic datasets """

___all__ = [
    "dataset_stats",
    "generate_synthetic_dataset",
    "generate_random_array",
    "write_to_netcdf",
]

import cftime
import xarray as xr
import numpy as np
from mdtf_test_data.util.rectilinear import construct_rect_grid
import mdtf_test_data.generators as generators

from mdtf_test_data.synthetic.time import generate_monthly_time_axis
from mdtf_test_data.synthetic.time import generate_daily_time_axis
from mdtf_test_data.synthetic.time import generate_hourly_time_axis

from mdtf_test_data.synthetic.vertical import gfdl_plev19_vertical_coord
from mdtf_test_data.synthetic.vertical import gfdl_vertical_coord
from mdtf_test_data.synthetic.vertical import ncar_hybrid_coord


def dataset_stats(filename, var=None, limit=None):
    """Prints statistics and attributes for a NetCDF file

    Parameters
    ----------
    filename : str, path-like
        Path to NetCDF file to analyze
    var : str, optional
        Variable to analyze (None prints a list of variables), by default None
    """
    dset = xr.open_dataset(filename, use_cftime=True)
    dset = dset.isel(time=slice(0, limit)) if limit is not None else dset
    if var is None:
        raise ValueError(f"Please specify a variable from {list(dset.variables)}")
    else:
        means = dset[var].mean(axis=(0, -2, -1)).values
        stds = dset[var].std(axis=(0, -2, -1)).values

        means = [means] if means.shape == () else list(means)
        stds = [stds] if stds.shape == () else list(stds)

        means = [float(x) for x in means]
        stds = [float(x) for x in stds]

        print(dset[var].attrs)
        print(list(zip(means, stds)))

    dset.close()

    return list(zip(means, stds))


def generate_synthetic_dataset(
    dlon,
    dlat,
    startyear,
    nyears,
    varname,
    timeres="mon",
    attrs=None,
    fmt="ncar",
    coords=None,
    generator="normal",
    generator_kwargs=None,
    stats=None,
):
    """Generates xarray dataset of syntheic data in NCAR format

    Parameters
    ----------
    dlon : float, optional
        Grid spacing in the x-dimension (longitude)
    dlat : float, optional
        Grid spacing in the y-dimension (latitude)
    startyear : int
        Start year for requested time axis
    nyears : int
        Number of years in requested time axis
    varname : str
        Variable name in output dataset
    attrs : dict, optional
        Variable attributes, by default None
    attrs : dict, optional
        Variable attributes, by default None
    attrs : dict, optional
        Variable attributes, by default None
    stats : tuple or list of tuples
        Array statistics in the format of [(mean,stddev)]

    Returns
    -------
    xarray.Dataset
        Dataset of synthetic data
    """

    attrs = {} if attrs is None else attrs

    do_bounds = True if fmt == "cmip" else False

    dset = construct_rect_grid(
        dlon, dlat, add_attrs=True, attr_fmt=fmt, bounds=do_bounds
    )
    lat = dset.lat
    lon = dset.lon
    xyshape = (len(dset["lat"]), len(dset["lon"]))

    if timeres == "mon":
        ds_time = generate_monthly_time_axis(startyear, nyears, timefmt=fmt)
    elif timeres == "day":
        ds_time = generate_daily_time_axis(startyear, nyears, timefmt=fmt)
    elif timeres == "3hr":
        ds_time = generate_hourly_time_axis(startyear, nyears, 3, timefmt=fmt)
    elif timeres == "1hr":
        ds_time = generate_hourly_time_axis(startyear, nyears, 1, timefmt=fmt)
    else:
        print(timeres)
        raise ValueError("Unknown time resolution requested")

    dset = ds_time.merge(dset)
    time = dset["time"]

    generator_kwargs = {} if generator_kwargs is None else generator_kwargs

    if stats is not None:
        stats = [stats] if not isinstance(stats, list) else stats
        if len(stats) > 1:
            if fmt == "ncar":
                dset = dset.merge(ncar_hybrid_coord())
                lev = dset.lev
            elif fmt == "gfdl":
                if len(stats) == 19:
                    dset = dset.merge(gfdl_plev19_vertical_coord())
                    lev = dset.plev19
                else:
                    dset = dset.merge(gfdl_vertical_coord())
                    lev = dset.pfull
        generator_kwargs["stats"] = stats

    assert generator in list(
        generators.__dict__.keys()
    ), f"Unknown generator method: {generator}"
    generator = generators.__dict__[generator]

    data = generators.generate_random_array(
        xyshape, len(time), generator=generator, generator_kwargs=generator_kwargs
    )
    data = data.squeeze()

    if len(data.shape) == 4:
        assert data.shape[1] == len(lev), "Length of stats must match number of levels"
        dset[varname] = xr.DataArray(data, coords=(time, lev, lat, lon), attrs=attrs)
    else:
        dset[varname] = xr.DataArray(data, coords=(time, lat, lon), attrs=attrs)

    if coords is not None:
        dset[coords["name"]] = xr.DataArray(coords["value"], attrs=coords["atts"])
        dset[varname].attrs = {**dset[varname].attrs, "coordinates": coords["name"]}

    dset.attrs["convention"] = fmt

    if fmt == "cmip":
        dset["bnds"].attrs = {"long_name": "vertex number"}
        cmip_global_atts = [
            "external_variables",
            "history",
            "table_id",
            "activity_id",
            "branch_method",
            "branch_time_in_child",
            "branch_time_in_parent",
            "comment",
            "contact",
            "Conventions",
            "creation_date",
            "data_specs_version",
            "experiment",
            "experiment_id",
            "forcing_index",
            "frequency",
            "further_info_url",
            "grid",
            "grid_label",
            "initialization_index",
            "institution",
            "institution_id",
            "license",
            "mip_era" "nominal_resolution",
            "parent_activity_id",
            "parent_experiment_id",
            "parent_mip_era",
            "parent_source_id",
            "parent_time_units",
            "parent_variant_label",
            "physics_index",
            "product",
            "realization_index",
            "realm",
            "source",
            "source_id",
            "source_type",
            "sub_experiment",
            "sub_experiment_id",
            "title",
            "tracking_id",
            "variable_id",
            "variant_info",
            "references" "variant_label",
        ]

        cmip_global_atts = {x: "" for x in cmip_global_atts}
        dset.attrs = {**dset.attrs, **cmip_global_atts}

    return dset


def write_to_netcdf(dset_out, outfile, time_dtype="float"):
    """Writes xarray dataset to NetCDF with proper encodings

    Parameters
    ----------
    dset_out : xarray.Dataset
        xarray dataset to write to NetCDF
    outfile : str, path-like
        Path to output file
    """

    base_time_unit = (
        dset_out.attrs["base_time_unit"]
        if "base_time_unit" in list(dset_out.attrs.keys())
        else "days since 0001-01-01"
    )

    encoding = {}
    for var in list(dset_out.variables):
        if var in ["time", "time_bnds", "average_T1", "average_T2"]:
            dset_out[var].encoding["units"] = base_time_unit
            if time_dtype == "float":
                dset_out[var].encoding["dtype"] = "float64"
                dset_out[var].encoding["_FillValue"] = 1.0e20
            elif time_dtype == "int":
                dset_out[var].encoding["dtype"] = "i4"
        elif var == "date":
            dset_out[var].encoding["dtype"] = "i4"
        elif "float" in str(dset_out[var].dtype):
            dset_out[var].encoding["_FillValue"] = 1.0e20
        elif "int" in str(dset_out[var].dtype):
            dset_out[var].encoding["_FillValue"] = -999
        else:
            dset_out[var].encoding["_FillValue"] = None

    # encoding = {"lat_bnds": {"units": "degrees_north"}}
    dset_out.to_netcdf(outfile, encoding=encoding)
