#!/usr/bin/env python
""" Collection of tools to coarsen model data """

__all__ = ["construct_rect_grid", "regrid_lat_lon_dataset"]

import warnings

import numpy as np
import xarray as xr

try:
    import xesmf as xe
except:
    warnings.warn("Unable to load `xesmf`. Regridding functionality will not work.")


def construct_rect_grid(dlon, dlat, add_attrs=False, attr_fmt="ncar", bounds=False):
    """Generate a rectilinear grid based on values of dx and dy

    Parameters
    ----------
    dlon : float
        Grid spacing in the x-dimension (longitude)
    dlat : float
        Grid spacing in the y-dimension (latitude)
    add_attrs : bool, optional
        Include lat and lon variable attributes, by default False

    Returns
    -------
    xarray.Dataset
        Empty shell dataset with lat and lon dimensions
    """

    if 180.0 % dlat != 0:
        dlat = 180.0 / np.floor(180.0 / dlat)
        warnings.warn(
            f"180 degrees does not divide evenly by dlat. Adjusting dlat to {dlat}"
        )

    if 360.0 % dlon != 0:
        dlon = 360.0 / np.floor(360.0 / dlon)
        warnings.warn(
            f"360 degrees does not divide evenly by dlon. Adjusting dlon to {dlon}"
        )

    lat = np.arange(-90.0 + (dlat / 2.0), 90.0, dlat)
    lon = np.arange(0.0 + (dlon / 2.0), 360.0, dlon)

    dset = xr.Dataset({"lat": (["lat"], lat), "lon": (["lon"], lon)})

    if bounds:
        lat_bnds = np.arange(-90.0, 90.0 + (dlat / 2.0), dlat)
        lon_bnds = np.arange(0.0, 360.0 + (dlon / 2.0), dlon)

        lat_bnds = np.array(list(zip(lat_bnds[0:-1], lat_bnds[1::])))
        lon_bnds = np.array(list(zip(lon_bnds[0:-1], lon_bnds[1::])))

        bnds = np.array([0.0, 1.0])

        dset["lat_bnds"] = xr.DataArray(lat_bnds, coords=(dset.lat, ("bnds", bnds)))
        dset["lon_bnds"] = xr.DataArray(lon_bnds, coords=(dset.lon, ("bnds", bnds)))

        dset = dset.drop("bnds")

    if attr_fmt == "ncar":
        dset["lat"].attrs = (
            {"long_name": "latitude", "units": "degrees_north"} if add_attrs else {}
        )
        dset["lon"].attrs = (
            {"long_name": "longitude", "units": "degrees_east"} if add_attrs else {}
        )

    elif attr_fmt == "gfdl":
        dset["lat"].attrs = (
            {"long_name": "latitude", "units": "degrees_N", "cartesian_axis": "Y"}
            if add_attrs
            else {}
        )
        dset["lon"].attrs = (
            {"long_name": "longitude", "units": "degrees_E", "cartesian_axis": "X"}
            if add_attrs
            else {}
        )

        if bounds:
            dset["lat"].attrs["bounds"] = "lat_bnds"
            dset["lon"].attrs["bounds"] = "lon_bnds"

            dset["lat_bnds"].attrs = (
                {"long_name": "latitude bounds", "cartesian_axis": "Y"}
                if add_attrs
                else {}
            )
            dset["lon_bnds"].attrs = (
                {"long_name": "longitude bounds", "cartesian_axis": "X"}
                if add_attrs
                else {}
            )

    elif attr_fmt == "cmip":
        dset["lat"].attrs = (
            {
                "long_name": "latitude",
                "units": "degrees_north",
                "axis": "Y",
                "standard_name": "latitude",
                "cell_methods": "time: point",
            }
            if add_attrs
            else {}
        )
        dset["lon"].attrs = (
            {
                "long_name": "longitude",
                "units": "degrees_east",
                "axis": "X",
                "standard_name": "longitude",
                "cell_methods": "time: point",
            }
            if add_attrs
            else {}
        )

        if bounds:
            dset["bnds"] = xr.DataArray(bnds, dims={"bnds": bnds})
            dset["bnds"].attrs["long_name"] = "vertex number"

            dset["lat"].attrs["bounds"] = "lat_bnds"
            dset["lon"].attrs["bounds"] = "lon_bnds"

            dset["lat_bnds"].attrs = (
                {"long_name": "latitude bounds", "axis": "Y", "units": "degrees_north"}
                if add_attrs
                else {}
            )
            dset["lon_bnds"].attrs = (
                {"long_name": "longitude bounds", "axis": "X", "units": "degrees_east"}
                if add_attrs
                else {}
            )

    else:
        raise ValueError("Unknown model attribute format")

    return dset


def regrid_lat_lon_dataset(dset, dlon=10.0, dlat=10.0, method="bilinear"):
    """Regrids xarray dataset to a standard lat-lon grid

    Parameters
    ----------
    dset : xarray.Dataset
        Input dataset.  Must have horizonatal dimensions of "lat" and "lon"
    dlon : float, optional
        Grid spacing in the x-dimension (longitude)
    dlat : float, optional
        Grid spacing in the y-dimension (latitude)
    method : str, optional
        xESMF regridding option, by default "bilinear"

    Returns
    -------
    xarray.Dataset
        Regridded data set
    """

    # Define output grid.
    dset_out = construct_rect_grid(dlon=dlon, dlat=dlat)

    # Create xESMF regridder object
    regridder = xe.Regridder(dset, dset_out, method)

    # Loop over variables
    for var in list(dset.variables):
        _dim = list(dset[var].dims)
        if "lat" in _dim and "lon" in _dim:
            _regridded = regridder(dset[var])
            dset_out[var] = _regridded.astype(dset[var].dtype)
            dset_out[var].attrs = dset[var].attrs
        elif var not in ["lat", "lon"]:
            dset_out[var] = dset[var]

    # Copy coordinate metadata
    dset_out["lat"].attrs = dset["lat"].attrs
    dset_out["lon"].attrs = dset["lon"].attrs

    # Copy dataset metadata
    dset_out.attrs = dset.attrs
    dset_out.attrs["coarsen_method"] = f"xESMF {method}"

    return dset_out
