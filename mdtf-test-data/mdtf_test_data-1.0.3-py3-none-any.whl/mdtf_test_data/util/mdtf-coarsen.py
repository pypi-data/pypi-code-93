#!/usr/bin/env python

""" CLI script for coarsening datasets for MDTF """

import argparse
import os
import warnings

import xarray as xr

from .rectilinear import regrid_lat_lon_dataset

# Newer versions of xESMF are throwing an error:
#     site-packages/xesmf/frontend.py:450: FutureWarning: ``output_sizes``
#     should be given in the ``dask_gufunc_kwargs`` parameter. It will be
#     removed as direct parameter in a future version.

warnings.simplefilter(action="ignore", category=FutureWarning)


def parse():
    """Parses the command line options

    Returns
    -------
    argparse
        argparse command line variables
    """
    parser = argparse.ArgumentParser(description="Coarsen a NetCDF file.")
    parser.add_argument(
        "-r",
        dest="regrid_method",
        type=str,
        default="bilinear",
        help="xESMF regridding method",
    )
    parser.add_argument(
        "-o", "--outfile", default=None, type=str, help="Filename of output NetCDF file"
    )
    parser.add_argument(
        "--dx", default=10.0, type=float, help="Longitude grid spacing in degrees"
    )
    parser.add_argument(
        "--dy", default=10.0, type=float, help="Latitude grid spacing in degrees"
    )
    parser.add_argument(
        "-O", dest="overwrite", action="store_true", help="Overwrite existing file"
    )
    parser.add_argument("infile", type=str, help="Path to input NetCDF file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse()
    _infile = os.path.abspath(args.infile)
    print(_infile)
    dset = xr.open_dataset(_infile,use_cftime=True)
    dset_out = regrid_lat_lon_dataset(
        dset, dlon=args.dx, dlat=args.dy, method=args.regrid_method
    )
    _outfile = args.outfile if args.outfile is not None else "out.nc"

    encoding = {}
    for var in list(dset_out.variables):
        if "float" in str(dset_out[var].dtype):
            dset_out[var].encoding["_FillValue"] = 1.0e20
        elif "int" in str(dset_out[var].dtype):
            dset_out[var].encoding["_FillValue"] = -999
        else:
            dset_out[var].encoding["_FillValue"] = None

    dset_out.to_netcdf(_outfile, encoding=encoding)

    if args.overwrite is True:
        print(f"Overwrite existing file {_infile}")
        os.replace(_outfile, _infile)
