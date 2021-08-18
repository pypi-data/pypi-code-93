"""
Input and output handling
"""
import contextlib
import gzip
import io
import logging
import os
import os.path
import tempfile

import click
import pandas as pd
from botocore.exceptions import ClientError
from scmdata.run import ScmRun, run_append

LOGGER = logging.getLogger(__name__)


def ensure_dir_exists(fp):
    """
    Ensure directory exists

    Parameters
    ----------
    fp : str
        Filepath of which to ensure the directory exists
    """
    dir_to_check = os.path.dirname(fp)
    if not os.path.isdir(dir_to_check):
        LOGGER.info("Creating {}".format(dir_to_check))
        os.makedirs(dir_to_check)


def read_results_submission(results):
    """
    Read results submission

    Parameters
    ----------
    results : str or list of str
        Files to read in. All files to be read should be formatted as csv or
        xlsx files following the formatting defined in the template
        spreadsheet.

    Returns
    -------
    :obj:`scmdata.ScmRun`
        Results read in from the submission(s)
    """
    if isinstance(results, str):
        results = [results]

    db = []
    for rf in results:
        LOGGER.info("Reading %s", rf)

        if rf.endswith(".nc"):
            LOGGER.info("Assuming netCDF format")
            loaded = ScmRun.from_nc(rf)
        else:
            if rf.endswith(".xlsx") or rf.endswith(".xls"):
                LOGGER.info("Assuming excel format")
                loaded = pd.read_excel(rf, sheet_name="your_data", engine="openpyxl")
            else:
                LOGGER.info("Assuming csv format")
                loaded = pd.read_csv(rf)

            LOGGER.debug("Converting all columns to lowercase")
            loaded.columns = loaded.columns.astype(str).str.lower()
            loaded = ScmRun(loaded)

        db.append(ScmRun(loaded))

    LOGGER.info("Joining results together")
    db = run_append(db)

    return db


def read_submission_model_reported(fp):
    """
    Read the model reported component of a submission

    Parameters
    ----------
    fp : str
        Filepath to read

    Returns
    -------
    :obj:`pd.DataFrame`
    """
    out = pd.read_csv(fp)

    return out


def read_submission_model_metadata(fp):
    """
    Read the model metadata component of a submission

    Parameters
    ----------
    fp : str
        Filepath to read

    Returns
    -------
    :obj:`pd.DataFrame`
    """
    out = pd.read_csv(fp)

    if out.columns[0] == "Unnamed: 0":
        # assume data was saved directly from excel sheet
        # drop first column
        out = out.iloc[:, 1:]
        column_map = {
            "ClimateModel": "climate_model",
            "Climate Model Name": "climate_model_name",
            "Climate Model Version": "climate_model_version",
            "Climate Model Configuration Label": "climate_model_configuration_label",
            "Model Configuration Description": "climate_model_configuration_description",
            "Project": "project",
            "Name of Person": "name_of_person",
            "Literature Reference": "literature_reference",
        }
        out.columns = out.columns.map(column_map)

    return out


@contextlib.contextmanager
def temporary_file_to_upload(df, max_size=1024, compress=False):
    """
    Create a gzipped temporary serialized version of a file to upload

    Attempts to keep the file in memory until it exceeds `max_size`. The file is then stored on-disk
    and cleaned up at the end of the context.

    The temporary location can be overriden using the `TMPDIR` environment variable as per
    https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir

    Parameters
    ----------
    df : :obj:`scmdata.ScmRun` or :obj:`pd.DataFrame`
        Run to store

    max_size: int or float
        Max size in MB before file is temporarily streamed to disk. Defaults to 1GB

    Returns
    -------
    :obj:`tempfile.SpooledTemporaryFile`
        Open file object ready to be streamed
    """
    if isinstance(df, ScmRun):
        df = df.timeseries().reset_index()

    if compress:
        buffer = tempfile.SpooledTemporaryFile(max_size=max_size * 1024 * 1024)
        with gzip.GzipFile(mode="w", fileobj=buffer) as gz_file:
            df.to_csv(io.TextIOWrapper(gz_file, "utf8"), index=False)
    else:
        buffer = io.BytesIO(df.to_csv(index=False).encode("utf8"))

    buffer.seek(0)

    try:
        yield buffer
    finally:
        buffer.close()


def _upload_file(client, bucket, key, run, compress=True):
    # Small files are kept in memory while bigger files are written to disk and automatically cleaned up
    LOGGER.info("Preparing {} for upload".format(key))
    with temporary_file_to_upload(run, max_size=1024, compress=compress) as fh:
        try:
            if compress:
                key += ".gz"
            LOGGER.info("Uploading {}".format(key))
            client.upload_fileobj(fh, Bucket=bucket, Key=key)
        except ClientError:  # pragma: no cover
            LOGGER.exception("Failed to upload file")
            raise click.ClickException("Failed to upload file")
