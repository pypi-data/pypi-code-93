# -*- coding: utf-8 -*-

"""Console script for mystran_validation.

MYSTRAN Binary is found with the following scheme:

    * from `--mystran-bin` passed option
    * from "MYSTRAN_BIN" environment variable
    * from /usr/bin/mystran
"""
import configparser
import glob
import logging
import os
import shlex
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path
import pkg_resources

import click
import pytest

from mystran_validation import get_conf, get_profile, init_config


def find(
    path,
    extensions,
    name="*",
    break_on_first=True,
    return_first=True,
):
    """return a list of pathlib.Path canditates matching {name}{ext}"""
    if isinstance(path, str):
        path = Path(path)
    path = path  # .resolve()
    files = []
    for ext in extensions:
        pattern = str(path / f"{name}{ext}")
        _files = glob.glob(pattern)
        if _files:
            if break_on_first:
                files = _files
                break
            files += _files
    if not files:
        files = [None]
    else:
        files = [Path(f) for f in files]
    if return_first:
        return files[0]
    return files


def get_junit_files(rootdir):
    junit_file = rootdir / "mystran-testing.xml"
    junit_html_target = junit_file.parent / (junit_file.stem + ".html")
    return junit_file, junit_html_target


def setup(rootdir):
    # -------------------------------------------------------------------------
    # ensure conftest.py and __init__ is there
    _init = rootdir / "__init__.py"
    if not _init.exists():
        _init.touch()
    _conftest = rootdir / "conftest.py"
    if not _conftest.exists():
        with open(_conftest, "w") as fh:
            fh.write("from mystran_validation.conftest_ref import *\n")
    # delete junit stuff
    junit_file, junit_html_target = get_junit_files(rootdir)
    try:
        os.remove(junit_file)
    except FileNotFoundError:
        pass
    try:
        os.remove(junit_html_target)
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(rootdir / "dumps")
    except FileNotFoundError:
        pass


def teardown(rootdir):
    """clean rootdir"""
    to_delete = ["bandit.*", "conftest.py", "__init__.py", "__pycache__"]
    to_delete = [rootdir / p for p in to_delete]
    for pattern in to_delete:
        files = glob.glob(str(pattern))
        for file in files:
            try:
                shutil.rmtree(file)
            except NotADirectoryError:
                os.remove(file)


def _init_rootdir(rootdir):
    path = rootdir / "example"
    click.echo(click.style(f"creating missing test-cases repository...", bold=True))
    click.echo(click.style(f"created repository {path}", fg="green"))
    path.mkdir(parents=True, exist_ok=True)
    # copy example files
    _files = ["bulk_model.nas", "bulk_model_2.dat", "test_bar.ini", "test_case_03.op2"]
    for f in _files:
        src = Path(pkg_resources.resource_filename("mystran_validation.data", f))
        shutil.copy(src, path / f)
    return path


def _ensure_paths(profile_name, rootdir, mystran_bin):
    # -------------------------------------------------------------------------
    # get configuration
    try:
        config_fpath, config = get_conf()
    except FileNotFoundError:  # if not existing, create with defaults
        click.echo(click.style("Creating missing configuration file...", bold=True))
        config_fpath = init_config(
            profile_name=profile_name, rootdir=rootdir, mystran_bin=mystran_bin
        )
        click.echo(
            click.style(f"created configuration file {config_fpath}", fg="green")
        )
        click.echo("consider to modify this file as per your preferences")
        click.echo("\n")
        config_fpath, config = get_conf()
    # -------------------------------------------------------------------------
    # get profile
    try:
        profile = get_profile(config, profile_name)
    except KeyError:
        click.echo(
            click.style(
                f"profile [{profile_name}] not found in {config_fpath}",
                fg="red",
            )
        )
        default = get_profile(config, "DEFAULT")
        config[profile_name] = {
            "mystran-bin": mystran_bin if mystran_bin else default["mystran-bin"],
            "rootdir": rootdir if rootdir else default["rootdir"],
        }
        with open(config_fpath, "w") as fh:
            config.write(fh)
        click.echo(
            click.style(
                f"creating profile [{profile_name}] with following options:", fg="green"
            )
        )
        profile = get_profile(config, profile_name)
        for k, v in profile.items():
            click.echo(f"  * {k}: {v}")
        click.echo("\n")
    # rootdir may not exist at this point
    rootdir = Path(config[profile_name]["rootdir"])
    if not rootdir.exists():
        _init_rootdir(rootdir)


@click.group()
@click.option(
    "-p", "--profile", default="DEFAULT", type=str, help="configuration title"
)
@click.option("-r", "--rootdir")
@click.option("-m", "--mystran-bin")
@click.option("-l", "--loglevel", default="info", type=str)
@click.pass_context
def main(ctx, profile, rootdir, mystran_bin, loglevel):
    profile_name = profile  # profile will be used for dict
    # -------------------------------------------------------------------------
    # handling logging verbosity
    getattr(logging, loglevel.upper())
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(level=numeric_level)
    ctx.ensure_object(dict)
    ctx.obj["rootdir"] = rootdir
    ctx.obj["mystran_bin"] = mystran_bin
    ctx.obj["profile"] = profile


@main.command()
@click.pass_context
def init(ctx):
    # config_fpath, config = get_conf()
    # profile = get_profile(config, profile_name)
    _ensure_paths(
        profile_name=ctx.obj["profile"],
        rootdir=ctx.obj["rootdir"],
        mystran_bin=ctx.obj["mystran_bin"],
    )


@main.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.option("--report/--no-report", default=True)
@click.option("--open-report/--not-open-report", default=True)
@click.option("--dump", type=click.IntRange(0, 3))
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, report, open_report, dump, pytest_args):
    try:
        config_fpath, config = get_conf()
    except FileNotFoundError:
        click.echo(click.style("Configuration file not found!", "red"))
        click.echo(click.style("consider running `mystran-val init` first"))
        sys.exit(1)
    profile = get_profile(config, ctx.obj["profile"])
    # -------------------------------------------------------------------------
    # override with CLI arguments
    mystran_bin = Path(
        ctx.obj["mystran_bin"] if ctx.obj["mystran_bin"] else profile["mystran-bin"]
    )
    rootdir = Path(ctx.obj["rootdir"] if ctx.obj["rootdir"] else profile["rootdir"])
    # -------------------------------------------------------------------------
    # check that mystran binary exists
    if not mystran_bin.exists():
        click.echo(click.style(f"Mystran Binary `{mystran_bin}` not found!", "red"))
        sys.exit(1)
    if not rootdir.exists():
        click.echo(click.style(f"Rootdir `{rootdir}` not found!", "red"))
        sys.exit(1)
    # -------------------------------------------------------------------------
    os.environ["MYSTRAN_BIN"] = str(mystran_bin)
    if dump is None:
        dump = profile["dump"]
        logging.info(f"dumping got from profile {dump=}")
    os.environ["MYSTRAN_VALIDATION_DUMP_XLSX"] = str(dump)
    # -------------------------------------------------------------------------
    # setting up rootdir
    setup(rootdir)
    # =========================================================================
    # summary
    # =========================================================================
    click.echo(click.style(f"test-cases params:", fg="green"))
    click.echo(click.style(f"  * mystran_bin={mystran_bin}", fg="green"))
    click.echo(click.style(f"  * rootdir={rootdir}", fg="green"))
    click.echo(click.style(f"  * {dump=}", fg="green"))
    click.echo("\n")
    args = list(pytest_args)
    if report:
        junit_file, junit_html_target = get_junit_files(rootdir)
        args += [f"--junitxml={junit_file}"]
    args.append(str(rootdir))
    pytest.main(args)
    if report:
        python_bin = shutil.which("python")
        subprocess.run(
            shlex.split(
                f"{python_bin} -m junit2htmlreport {junit_file} {junit_html_target}"
            )
        )
    teardown(rootdir)
    if report and open_report:
        webbrowser.open(str(junit_html_target.resolve()))
    return 0


@main.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def collect(ctx, pytest_args):
    try:
        config_fpath, config = get_conf()
    except FileNotFoundError:
        click.echo(click.style("Configuration file not found!", "red"))
        click.echo(click.style("consider running `mystran-val init` first"))
        sys.exit(1)
    profile = get_profile(config, ctx.obj["profile"])
    rootdir = Path(ctx.obj["rootdir"] if ctx.obj["rootdir"] else profile["rootdir"])
    setup(rootdir)
    args = list(pytest_args) + ["--collect-only"]
    args.append(str(rootdir))
    pytest.main(args)
    teardown(rootdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
