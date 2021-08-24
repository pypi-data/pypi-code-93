"""Set of utility methods."""
from datetime import datetime, timedelta, timezone
import importlib.resources as pkg_resources
import json
import os
from os import listdir
from pathlib import Path
import re
from shlex import split
from types import ModuleType
from typing import List
from urllib import parse
from urllib.error import URLError
import urllib.request

import click
from dateutil.parser import parse as date_string_parse
from google.cloud import storage
from packaging import version
import pytz
from tzlocal import get_localzone
import ulid

from grid.cli import autocomplete
from grid.metadata import __package_name__, __version__


class GCPStorage:  # pragma: no cover
    """
    Google Cloud Platform Storage wrapper for uploading
    objects to GCP.
    """
    def __init__(self):
        self.storage_client = storage.Client()

    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))

    def delete_blob(self, bucket_name, blob_name):
        """Deletes a blob from the bucket."""
        # bucket_name = "your-bucket-name"
        # blob_name = "your-object-name"
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()

        print("Blob {} deleted.".format(blob_name))

    def delete_blobs(self, bucket_name, prefix=''):
        """ Deletes all blobs with a specific prefix from a bucket."""
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        for blob in blobs:
            if blob.name.startswith(prefix):
                blob.delete()

    def list_blobs(self, bucket_name, prefix='', delimiter=None):
        """Lists all the blobs in the bucket."""
        blobs = self.storage_client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)

        names = []
        for blob in blobs:
            names.append(blob.name)
        return names

    def download_blob(self, bucket_name, source_blob_name, destination_file_name, source_blob_prefix=''):
        """Downloads a blob from the bucket."""
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        for blob in blobs:
            if blob.name.startswith(source_blob_prefix):
                print("downloading")
                blob.download_to_filename(destination_file_name)


def get_abs_time_difference(date_1: datetime, date_2: datetime) -> timedelta:
    """
    Gets the absolute value of the timedelta of the difference
    between date_1 and date_2. If a datetime is timezone naive,
    then UTC timezone will be assumed
    """

    # check if need to localize:
    if not date_1.tzinfo:
        # skipcq: PYL-E1120
        date_1 = pytz.UTC.localize(dt=date_1)
    if not date_2.tzinfo:
        # skipcq: PYL-E1120
        date_2 = pytz.UTC.localize(dt=date_2)
    diff = abs(date_2 - date_1)
    return diff


def convert_utc_string_to_local_datetime(date: str) -> datetime:
    """
    Converts a string timestamp in utc to the datetime equivalent in the
    local timezone.
    """
    return date_string_parse(date).replace(tzinfo=get_localzone())


def string_format_date(date: datetime):
    """
    Get's a human readable string formatted version
    of a datetime object.
    """
    return date.strftime("%Y-%m-%d %H:%M:%S%z")


def string_format_timedelta(delta: timedelta) -> str:
    """
    Gets the iso8601 string format of a datetime.
    """
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    delta_str = f"{days}d-{hours:02d}:{minutes:02d}:{seconds:02d}"
    return delta_str


def upload_wheel(gcp_storage, version, bucket_name, blob_path):  # pragma: no cover
    """
    Uploads wheel to it's designated GCP bucket.
    """
    whl_exists = False
    for file in listdir('dist'):
        if '.whl' in file:
            wheel = file
            whl_exists = True

    if whl_exists:
        lastest_path = Path(blob_path) / "latest" / wheel
        version_path = Path(blob_path) / version / wheel

        # delete existing object in "latest" directory
        gcp_storage.delete_blobs(bucket_name=bucket_name, prefix=f'{blob_path}/latest/')

        gcp_storage.upload_blob(
            bucket_name=bucket_name, source_file_name=f'dist/{wheel}', destination_blob_name=lastest_path
        )
        gcp_storage.upload_blob(
            bucket_name=bucket_name, source_file_name=f'dist/{wheel}', destination_blob_name=version_path
        )
    else:
        raise ValueError("You did not build a wheel for this project.")


def check_environment_variables(variables: list) -> bool:
    """
    Check that environment variables have been
    set, raising an error if they have not.

    Parameters
    ----------
    variables: list
        List of environment variables to check.
    Returns
    -------
    bool
        Returns True if all environment variables
        have been set correctly.
    """
    for variable in variables:
        if not os.getenv(variable):
            raise ValueError(f'Environment variable `{variable}` has not been set.')

    return True


def introspect_module(module: ModuleType):
    """
    Introspects a module looking for namespace references
    in __all__

    Parameters
    ----------
    module: ModuleType
        A Python module. This module must contain the `__all__`
        attribute.

    Yields
    ------
    objects
        Python objects
    """
    for m in module.__all__:
        yield module.__dict__[m]


def is_latest_version() -> bool:
    """
    Checks if a more recent version is available from PyPI.

    Returns
    -------
    bool
        True if a more recent version is available on PyPI or if an error is encountered in accessing the package
        metadata, False otherwise.
    """
    if __version__ == "vx.y.z":
        return True
    try:
        response = urllib.request.urlopen(f'https://pypi.org/pypi/{__package_name__}/json').read().decode()
        latest_version = max(version.parse(s) for s in json.loads(response)['releases'].keys())
        return version.parse(__version__) >= latest_version
    except URLError:
        # Return True if PyPI can't be accessed
        return True


def is_experiment(identifier: str) -> bool:
    """
    Checks if identifier is an Experiment. The check is done
    both against experiment names and experiments IDs (ULIDs).

    Parameters
    ----------
    identifier: str
        Experiment identifier to check.

    Returns
    -------
    output: bool
        True if is experiment, False otherwise.
    """
    regex = re.compile(r'exp[0-9]+$')
    result = regex.search(identifier)

    is_experiment_name = False
    if result:
        is_experiment_name = True

    try:
        ulid.from_str(identifier)
        is_experiment_id = True
    except ValueError:
        is_experiment_id = False

    return is_experiment_name or is_experiment_id


def get_param_values(command: str) -> List[str]:
    """
    Converts string parameters into a list of strings.
    This is useful for rendering such parameters into
    a table.

    Parameters
    ----------
    command: str
        String representing invocation command alongside
        parameters.

    Returns
    -------
    hparam_vals: List[str]
        List of hyper parameter values.
    """
    toks = split(command)[1:]
    hparam_vals = []
    for index, tok_val in enumerate(toks):
        if '--' not in tok_val:
            hparam_vals.append(tok_val)
        elif index == len(toks) - 1 or '--' in toks[index + 1]:
            hparam_vals.append("True")

    return hparam_vals


def get_experiment_duration_string(created_at: str, started_running_at: str, finished_at: str):
    """
    Calculates:
    - If experiment still queued: between experiment creation and now
    - If experiment running: between start of run and now
    - If experiment finished, between start of run and end
    """
    end = datetime.now(timezone.utc) if finished_at is None else date_string_parse(finished_at)

    start = date_string_parse(created_at) if started_running_at is None else date_string_parse(started_running_at)

    delta = get_abs_time_difference(end, start)
    return string_format_timedelta(delta)


def get_experiment_queued_duration_string(created_at: str, started_running_at: str):
    """
    Calculates:
    - If experiment still queued: between experiment creation and now
    - If experiment running: between created of run and start
    """
    end = datetime.now(timezone.utc) if started_running_at is None else date_string_parse(started_running_at)

    start = date_string_parse(created_at)

    # This is to handle a case where an experiment never starts (for example build fails)
    # and the started_running_at is not set. In this case we just make the start to equal end
    # so the end result becomes '0d-00:00:00'
    if start > end:
        start = end

    delta = get_abs_time_difference(end, start)
    return string_format_timedelta(delta)


def get_graphql_url(url: str) -> str:
    """
    Appends a graphql to the end of the url if not included

    Parameters
    ----------
    url: str
        URL potentially including graphql

    Returns
    -------
    A url appended with graphql if not already included
    """
    return url if parse.urlparse(url).path.endswith('/graphql') else parse.urljoin(url, "/graphql")


def check_is_python_script(ctx, _param, value):
    """Click callback that checks if a file is a Python script."""
    if value is not None:
        if not value.endswith('.py'):
            raise click.BadParameter('You must provide a Python script. ' 'No script detected.')

        ctx.params['entrypoint'] = value
        return value


def check_description_isnt_too_long(ctx, _param, value):
    """Click callback that checks if the description isn't too long."""
    if value is not None and len(value) > 200:
        raise click.BadParameter('Description should have at most ' f'200 characters, yours has {len(value)}.')
    return value


def install_autocomplete() -> None:
    """
    Installs autocomplete files from package resources, and activates in users shell config.
    """
    home = Path.home()
    # this should probably be a global but no one seems to be doing that
    # for .grid files
    complete = home / ".grid/autocomplete"

    bashrc = home / ".bashrc"
    zshrc = home / ".zshrc"
    bash_complete = complete / "complete.bash"
    zsh_complete = complete / "complete.zsh"

    complete.mkdir(parents=True, exist_ok=True)

    bash_complete.write_text(pkg_resources.read_text(autocomplete, "complete.bash"))
    zsh_complete.write_text(pkg_resources.read_text(autocomplete, "complete.zsh"))

    for rc, sh_complete in zip([bashrc, zshrc], [bash_complete, zsh_complete]):
        # Adds necessary activation to shell config if the file exists and doesn't already contain
        if rc.exists() and str(sh_complete) not in rc.read_text():
            with rc.open("a") as f:
                f.write("\n# Grid Autocomplete\n" f"if [ -f '{sh_complete}' ]; then . '{sh_complete}' ; fi\n")
