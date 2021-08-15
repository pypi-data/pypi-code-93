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

MYSTRAN_BIN = os.getenv("MYSTRAN_BIN", "/usr/bin/mystran")


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
    return


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


@click.group()
@click.option("-r", "--rootdir", default="~/mystran_test_cases")
@click.option("-l", "--loglevel", default="info", type=str)
@click.pass_context
def setup_rootdir(ctx, rootdir, loglevel):
    # -------------------------------------------------------------------------
    # handling logging verbosity
    getattr(logging, loglevel.upper())
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(level=numeric_level)
    # -------------------------------------------------------------------------
    # setting up rootdir
    rootdir = Path(rootdir).expanduser().resolve()
    if not Path(rootdir).exists():
        logging.warning(f"Repository `{rootdir}` not found! Creating it now...")
        Path(rootdir).mkdir(parents=True, exist_ok=True)
    setup(rootdir)


@click.group()
@click.option("-r", "--rootdir", default="~/mystran_test_cases")
@click.option("-m", "--mystran-bin", default=MYSTRAN_BIN, type=str)
@click.option("-l", "--loglevel", default="info", type=str)
@click.pass_context
def main(ctx, rootdir, mystran_bin, loglevel):
    # -------------------------------------------------------------------------
    # handling logging verbosity
    getattr(logging, loglevel.upper())
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(level=numeric_level)
    # -------------------------------------------------------------------------
    # check that mystran binary exists
    if not Path(mystran_bin).exists():
        logging.error(f"Mystran Binary `{mystran_bin}` not found!")
        sys.exit(1)
    logging.info(f"using mystran binary `{mystran_bin}`")
    os.environ["_MYSTRAN_BIN"] = mystran_bin
    # -------------------------------------------------------------------------
    # setting up rootdir
    rootdir = Path(rootdir).expanduser().resolve()
    if not Path(rootdir).exists():
        logging.warning(f"Repository `{rootdir}` not found! Creating it now...")
        Path(rootdir).mkdir(parents=True, exist_ok=True)
    setup(rootdir)
    logging.info(f"running tests in {str(rootdir)}")
    ctx.ensure_object(dict)
    ctx.obj["rootdir"] = rootdir


@main.command()
@click.pass_context
def init(ctx):
    rootdir = ctx.obj["rootdir"]
    path = Path(rootdir) / "example"
    path.mkdir(parents=True, exist_ok=True)
    # copy example files
    _files = ["bulk_model.nas", "bulk_model_2.dat", "test_bar.ini", "test_case_03.op2"]
    for f in _files:
        src = Path(pkg_resources.resource_filename("mystran_validation.data", f))
        shutil.copy(src, path / f)


@main.command()
@click.argument("--path", type=click.Path(exists=False))
@click.option("-f", "--force", help="force creation of path", is_flag=True)
@click.option("-v", "--verbose", help="print ini content", is_flag=True)
@click.pass_context
def dump_config(ctx, path, force, verbose):
    """dump configuration file as example"""
    # search for bulk file
    rootdir = ctx.obj["rootdir"]
    path = Path(rootdir).expanduser() / path
    if not path.exists():
        if force is True:
            path.mkdir(parents=True)
            logging.warning(f"creating {path}")
        else:
            logging.error(f"path {path} does not exist. Create it passing --force flag")
    # path = Path(path)#.resolve()
    bulkfile = find(path, extensions=(".nas", ".bdf", ".dat"))
    if not bulkfile:
        logging.info(f"no bulk file found")
        bulkfile = "# path to bulk file"
    else:
        bulkfile = bulkfile.relative_to(path)
    # -------------------------------------------------------------------------
    # search for op2
    op2file = find(path, extensions=(".op2", ".OP2"))
    if not op2file:
        logging.info(f"no op2 file found")
        op2file = "# path to OP2 file"
    else:
        op2file = op2file.relative_to(path)
    # -------------------------------------------------------------------------
    # create test.ini
    config = configparser.ConfigParser()
    config["DEFAULT"] = {
        "title": path.stem,
        "bulk": bulkfile,
        "reference": op2file,
        "atol": 1e-5,
        "rtol": 1e-8,
    }
    config["Displacements"] = {
        "description": "checking all displacements",
        "vector": "displacements",
    }
    config["Reactions"] = {
        "description": "checking all reactions",
        "vector": "reactions",
    }
    target = path / f"test_{path.resolve().stem}.ini"
    with open(target, "w") as fh:
        config.write(fh)
    logging.info(f"\nwrote {target}")
    if verbose:
        print("\n")
        with open(target, "r") as fh:
            for line in fh.read().split("\n"):
                print(line)
    return 0


@main.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.option("--report/--no-report", default=True)
@click.option("--open-report/--not-open-report", default=True)
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, report, open_report, pytest_args):
    rootdir = ctx.obj["rootdir"]
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
    rootdir = ctx.obj["rootdir"]
    args = list(pytest_args) + ["--collect-only"]
    args.append(str(rootdir))
    pytest.main(["--collect-only", str(rootdir)])
    teardown(rootdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
