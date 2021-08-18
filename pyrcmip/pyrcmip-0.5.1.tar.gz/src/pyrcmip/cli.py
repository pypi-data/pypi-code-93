"""
Console script for rcmip.
"""
import logging
import sys
from os.path import basename, join

import boto3
import click
import jwt
import semver
from botocore.exceptions import ClientError

from pyrcmip.io import (
    _upload_file,
    read_results_submission,
    read_submission_model_metadata,
    read_submission_model_reported,
)
from pyrcmip.validate import validate_submission_bundle

LOGGER = logging.getLogger(__name__)
DEFAULT_LOG_FORMAT = "{process} {asctime} {levelname}:{name}:{message}"


class ColorFormatter(logging.Formatter):
    """
    Colour formatter for log messages

    A handy little tool for making our log messages look slightly prettier
    """

    colors = {
        "DEBUG": dict(fg="blue"),
        "INFO": dict(fg="green"),
        "WARNING": dict(fg="yellow"),
        "Error": dict(fg="red"),
        "ERROR": dict(fg="red"),
        "EXCEPTION": dict(fg="red"),
        "CRITICAL": dict(fg="red"),
    }

    def format(self, record):
        """
        Format a record so it has pretty colours

        Parameters
        ----------
        record : :obj:`logging.LogRecord`
            Record to format

        Returns
        -------
        str
            Formatted message string
        """
        formatted_message = super(ColorFormatter, self).format(record)

        level = record.levelname

        if level in self.colors:
            level_colour = click.style("{}".format(level), **self.colors[level])
            formatted_message = formatted_message.replace(level, level_colour)

        return formatted_message


class ClickHandler(logging.Handler):
    """
    Handler which emits using click when going to stdout
    """

    _use_stderr = True

    def emit(self, record):
        """
        Emit a record

        Parameters
        ----------
        record : :obj:`logging.LogRecord`
            Record to emit
        """
        try:
            msg = self.format(record)
            click.echo(msg, err=self._use_stderr)

        except Exception:  # pragma: no cover
            self.handleError(record)


_default_handler = ClickHandler()
_default_handler.formatter = ColorFormatter(DEFAULT_LOG_FORMAT, style="{")


@click.group(name="rcmip")
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION", "CRITICAL"]),
)
def cli(log_level):
    """
    Command-line interface for pyrcmip
    """
    root = logging.getLogger()
    root.handlers.append(_default_handler)
    root.setLevel(log_level)

    logging.captureWarnings(True)


def _read_bundle(timeseries, model_reported, metadata):
    try:
        scmrun = read_results_submission(timeseries)
    except Exception as e:
        LOGGER.exception("reading timeseries failed")
        raise click.ClickException(str(e))

    try:
        model_reported_df = read_submission_model_reported(model_reported)
    except Exception as e:
        LOGGER.exception("reading model_reported failed")
        raise click.ClickException(str(e))

    try:
        metadata_df = read_submission_model_metadata(metadata)
    except Exception as e:
        LOGGER.exception("reading metadata failed")
        raise click.ClickException(str(e))

    return scmrun, model_reported_df, metadata_df


timeseries = click.argument(
    "timeseries", nargs=-1, required=True, type=click.Path(exists=True, dir_okay=False)
)
model_reported = click.argument(
    "model_reported",
    nargs=1,
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
metadata = click.argument(
    "metadata", nargs=1, required=True, type=click.Path(exists=True, dir_okay=False)
)


@cli.command()
@timeseries
@model_reported
@metadata
def validate(timeseries, model_reported, metadata):
    """
    Validate submission input

    Three different types of input data are required for validation, namely:

    One or more ``TIMESERIES`` files in which the timeseries output is stored. These should be
    CSV or NetCDF files conforming to the format expected by ``scmdata``. Multiple
    timeseries inputs can be specified, but care must be taken to ensure that all of
    the individual timeseries have unique metadata.

    ``MODEL_REPORTED`` is the CSV file in which the model reported metrics are stored.

    ``METADATA`` is the CSV file in which the metadata output is stored.
    """
    for timeseries_fname in timeseries:
        scmrun, model_reported_df, metadata_df = _read_bundle(
            timeseries_fname, model_reported, metadata
        )

        try:
            validate_submission_bundle(scmrun, model_reported_df, metadata_df)
        except Exception as e:
            raise click.ClickException(str(e))


def validate_version(ctx, param, value):
    """
    Validate version string

    Parameters
    ----------
    ctx
        Not used

    param
        Not used

    value : str
        Version string to validate

    Returns
    -------
    str
        Validated version string

    Raises
    ------
    :obj:`click.BadParameter`
        Version string cannot be passed or does not follow semantic versioning
    """
    try:
        s = semver.VersionInfo.parse(value)

        if s.prerelease is None and s.build is None:
            return value
        else:
            raise click.BadParameter(
                "Version must only contain major, minor and patch values"
            )
    except ValueError:
        raise click.BadParameter("Cannot parse version string")


@cli.command()
@click.option(
    "--token",
    required=True,
    help="Authentication token. Contact zebedee.nicholls@climate-energy-college.org for a token",
)
@click.option("--bucket", default="rcmip-uploads-au")
@click.option("--model", required=True)
@click.option(
    "--version",
    required=True,
    callback=validate_version,
    help="Version of the data being uploaded. Must be a valid semver version string (https://semver.org/). "
    "For example 2.0.0",
)
@timeseries
@model_reported
@metadata
def upload(token, bucket, model, version, timeseries, model_reported, metadata):
    """
    Validate and upload data to RCMIP's S3 bucket.

    All the files for a given version have to be uploaded together.

    One or more ``TIMESERIES`` files in which the timeseries output is stored. These should be
    CSV or NetCDF files conforming to the format expected by ``scmdata``. Multiple
    timeseries inputs can be specified, but care must be taken to ensure that all of
    the individual timeseries have unique metadata. Each timeseries file will be validated and
    uploaded independently.

    ``MODEL_REPORTED`` is the CSV file in which the model reported metrics are stored.

    ``METADATA`` is the CSV file in which the metadata output is stored.
    """
    # Upload data to S3
    t = jwt.decode(token, options={"verify_signature": False})
    session = boto3.session.Session(
        aws_access_key_id=t["access_key_id"],
        aws_secret_access_key=t["secret_access_key"],
    )
    client = session.client("s3")

    root_key = "{}/{}/{}".format(t["org"], model, version)

    for file_idx, timeseries_fname in enumerate(timeseries):
        LOGGER.info("Reading and validating {}".format(timeseries_fname))
        try:
            scmrun, model_reported_df, metadata_df = _read_bundle(
                timeseries_fname, model_reported, metadata
            )
            (
                scmrun_rcmip_compatible,
                model_reported_rcmip_compatible,
                metadata_rcmip_compatiable,
            ) = validate_submission_bundle(scmrun, model_reported_df, metadata_df)
        except Exception:
            raise click.ClickException("Validation failed. Fix issues and rerun")

        # Check if this version is already uploaded (using the {key}-complete dummy file)
        try:
            LOGGER.debug("Checking if object with key {} exists".format(root_key))
            client.head_object(Bucket=bucket, Key=root_key + "-complete")

            raise click.ClickException(
                "Data for this version has already been uploaded. Increment the version and try again"
            )
        except ClientError:
            LOGGER.debug("Object with key {} does not exist".format(root_key))

        def _get_fname(data_type):
            if data_type == "data":
                fname = "rcmip-{}-{}-{}-{:03}.csv".format(
                    model, version, data_type, file_idx
                )
            else:
                fname = "rcmip-{}-{}-{}.csv".format(model, version, data_type)
            return join(root_key, fname)

        if file_idx == 0:
            _upload_file(
                client,
                bucket=bucket,
                key=_get_fname("model_reported"),
                run=model_reported_rcmip_compatible,
                compress=False,
            )
            _upload_file(
                client,
                bucket=bucket,
                key=_get_fname("metadata"),
                run=metadata_rcmip_compatiable,
                compress=False,
            )

        _upload_file(
            client,
            bucket=bucket,
            key=_get_fname("data"),
            run=scmrun_rcmip_compatible,
            compress=True,
        )

    # Finally mark the upload as complete by uploading a dummy file
    # Writing this dummy file will be used to start the processing of the upload
    client.put_object(Bucket=bucket, Key=root_key + "-complete")

    LOGGER.info("All files uploaded successfully")


@cli.command()
@click.option(
    "--token",
    required=True,
    help="Authentication token. Contact zebedee.nicholls@climate-energy-college.org for a token",
)
@click.option("--bucket", default="rcmip-uploads-au")
@click.option("--model", required=True)
@click.option(
    "--version",
    required=True,
    callback=validate_version,
    help="Version of the data that was uploaded. Must be a valid semver version string (https://semver.org/). "
    "For example 2.0.0",
)
@click.argument("outdir", required=True, type=click.Path(exists=True, dir_okay=True))
def download(token, bucket, model, version, outdir):
    """
    Download submitted files
    """
    t = jwt.decode(token, options={"verify_signature": False})
    session = boto3.session.Session(
        aws_access_key_id=t["access_key_id"],
        aws_secret_access_key=t["secret_access_key"],
    )
    client = session.client("s3")

    root_key = "{}/{}/{}/".format(t["org"], model, version)  # trailing / is important

    resp = client.list_objects(Bucket=bucket, Prefix=root_key)

    if "Contents" not in resp:
        raise click.ClickException(
            "No files for {}=={} have been uploaded".format(model, version)
        )

    for o in resp["Contents"]:
        key = o["Key"]
        LOGGER.info("Downloading {}".format(key))
        resp = client.get_object(Bucket=bucket, Key=key)

        with open(join(outdir, basename(key)), "wb") as fh:
            for chunk in resp["Body"]:
                fh.write(chunk)

    LOGGER.info("All files downloaded successfully")


def run_cli():
    """
    Run command-line interface

    TODO: fix this so environment variables can be used
    """
    sys.exit(cli(auto_envvar_prefix="RCMIP"))  # pragma: no cover


if __name__ == "__main__":
    run_cli()  # pragma: no cover
