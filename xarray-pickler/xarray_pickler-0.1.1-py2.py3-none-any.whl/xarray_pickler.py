__author__ = """Elle Smith"""
__contact__ = "eleanor.smith@stfc.ac.uk"
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import os
import pickle

import xarray as xr

from xarray_pickler import CONFIG, logging

logger = logging.getLogger(__file__)


def _get_pickle_name(dpath):
    """
    Define a "grouped" path that splits facets across directories and then groups the final set into a file path, based on dir_grouping_level value in CONFIG.

    If remove_archive_dir_in_path is set as True in CONFIG, the base archive directory will be removed from the file path to shorten it.
    NOTE: the following characters are replaced as followed:
          - "*": "all"
          - "?": "_"
    """
    gl = CONFIG["paths"]["dir_grouping_level"]
    archive_dir = CONFIG["paths"]["archive_dir"]
    remove_archive_dir_in_path = CONFIG["paths"]["remove_archive_dir_in_path"]

    if remove_archive_dir_in_path:
        if dpath.startswith(archive_dir):
            if not archive_dir.endswith("/"):
                archive_dir = archive_dir + "/"
            dpath = dpath.replace(archive_dir, "")

    parts = dpath.split("/")
    parts.append("pickle")

    grouped_path = "/".join(parts[: -(gl + 1)]) + "/" + ".".join(parts[-(gl + 1) :])

    # Replace illegal characters
    replacers = {"*": "all", "?": "_"}

    for key, value in replacers.items():
        grouped_path = grouped_path.replace(key, value)

    return grouped_path


def _get_pickle_path(pck, mode="r"):
    """
    Gets the read or write file path for the pickle file.

    :param pck (str): The base pickle path, to append to the read or write directory.
    :param mode: This should be "r" for read or "w" for write. Default is "r". This determines the directory to insert before the pickle path.
                "r" will try all the pickle directories specfified in CONFIG, in order to see if the pcikle file exists. If there isn't a file at any of the paths, returns None.
                "w" will join the writeable pickle directory from CONFIG and the base pickle path if a writeable pickle directory has been supplied. Otherwise None is returned.

    :return: The read or write pickle path.
    """

    pickle_dirs = CONFIG["paths"]["pickle_dirs"]
    writeable_pickle_dir = CONFIG["paths"]["writeable_pickle_dir"]

    if mode == "r":
        for pdir in pickle_dirs:

            pickle_path = os.path.join(pdir, pck.lstrip("/"))
            if os.path.isfile(pickle_path):
                # found a pickle file so can return the path
                return pickle_path

    if mode == "w" and writeable_pickle_dir:
        pickle_path = os.path.join(writeable_pickle_dir, pck.lstrip("/"))

        os.makedirs(os.path.dirname(pickle_path), exist_ok=True)

        return pickle_path

    return


def open_dset(dpath, force_repickle=False, **kwargs):
    """
    Open xarray.Dataset object. If previously pickled, it will be opened from the pickle file stored in the cache.
    Otherwise, it will be pickled and stored in the cache, if a cache is specified, after it is opened using xarray.open_mfdataset() with any extra keyword arguments specified.
    If there is no writeable pickle directory specified in the config, and the pickle does not already exist, the dataset will just be opened using xarray and returned.

    :param dpath (str): Directory path to netCDF files to generate dataset from e.g. "/badc/cmip6/data/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/historical/r1i1p1f1/Amon/rlds/gr/v20180803"
    :param force_repickle: If True, the xarray.Dataset object will be repickled, if a writeable pickle directory is specified in the config. Default is False.
    :param **kwargs: Other keyword arguments that can be used in xarray.open_mfdataset(). Used only the first time a dataset is pickled or if force_repickle=True.

    :return: xarray.Dataset object
    """
    open_kwargs = CONFIG["open_mfdataset_kwargs"].copy()
    open_kwargs.update(kwargs)

    if dpath.endswith("/"):
        dpath = dpath[:-1]

    fpattn = f"{dpath}/*.nc"
    logger.info(f"Reading: {fpattn}")

    pck = _get_pickle_name(dpath)
    read_pickle_path = _get_pickle_path(pck, mode="r")

    if read_pickle_path and not force_repickle:
        try:
            with open(read_pickle_path, "rb") as reader:
                ds = pickle.load(reader)
                logger.info(f"Dataset read from cached pickle: {read_pickle_path}")
                return ds
        except Exception:
            # Assume failure so try to re-read and re-pickle the file
            pass

    ds = xr.open_mfdataset(fpattn, **open_kwargs)
    ds.close()

    write_pickle_path = _get_pickle_path(pck, mode="w")

    if write_pickle_path:
        logger.info(f"Pickling dataset to: {write_pickle_path}")
        with open(write_pickle_path, "wb") as writer:
            pickle.dump(ds, writer, protocol=-1)

    return ds
