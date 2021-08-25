#!/usr/bin/env python3

"""\
Core functions to execute sub-commands called from command line.
"""
import os
import re
import shlex
import sys
from subprocess import run as runprocess
from typing import Dict, Optional

from .argsParser import parse_arguments
from .connector import Conn

db_connect = Conn()


def get_params(args: parse_arguments, **params):
    if params:
        for param, namespace in params.items():
            params[param] = args.__getattribute__(namespace)
        return params
    else:
        return args.__dict__


def run(
    execp: str = None, path: str = None, cromwell_param: Dict = False, **args
) -> Optional[Dict]:
    """\
    The method relies on an existing config file, and requires:
    1) a path to dockerized SEQC or other tools (scata, sera)
    2) an email address
    3) path to AWS EC key .pem

    :param execp:
        Executable pipeline. This is usually the python executable {seqc | atac |
        sera}_submit_mjobs.py
    :param path:
        Path to pipeline (seqc | atac | sera)
    :param cromwell_param:
        In case of hashtags switch to specialty command
    :param args:
        Additional arguments passed to executable pipeline

    :return:
        `str` or `None`
    """
    # change working directory to the pipeline package
    oldwd = os.getcwd()
    os.chdir(path)

    # execute the pipeline command
    if cromwell_param:
        cmd = " ".join(
            [
                execp,
                "-k {}".format(cromwell_param["secret"]),
                "-i {}".format(cromwell_param["inputs"]),
                "-l {}".format(cromwell_param["labels"]),
                "-o {}".format(cromwell_param["output"]),
            ]
        )

        var = runprocess(shlex.split(cmd), universal_newlines=True, capture_output=True)
        out = var.__dict__

    else:

        jobs = os.path.join(path, "config", args["jobs"])
        cmd = " ".join([sys.executable, execp, "--pem", args["pem"], "--config", jobs])

        var = runprocess(shlex.split(cmd), universal_newlines=True, capture_output=True)
        out = var.__dict__
        if "Cannot connect to the Docker daemon" in out["stdout"]:
            out["returncode"] = 1

    print("--")
    # change back to old working dir
    os.chdir(oldwd)

    return out


def data_submission(args):
    from SCRIdb.submission import data_submission_main

    data_submission_main(**get_params(args, fn="file", mode="mode",))


def process(args):
    from SCRIdb.worker import worker_main

    worker_main(f_in=args.file, **get_params(args,))


def uploadstats(args):
    from SCRIdb.upload_stats import upload_stats_main

    upload_stats_main(
        **get_params(
            args,
            s3paths="s3paths",
            results_folder="results_folder",
            sample_names="sample_names",
            sample_ids="sample_ids",
            cellranger="cellranger",
            hash_tags="hash_tags",
            results_output="results_output",
        )
    )


def data_transfer(args):
    from SCRIdb.transfer import data_transfer

    data_transfer(
        **get_params(
            args,
            sample_ids="sample_ids",
            results_output="results_output",
            target="target",
            mode="mode",
        )
    )


def main(argv):
    args = parse_arguments(argv)

    db_connect.conn(args.config)

    # call specialty function
    if args.func.__name__ == "run":  # calling a pipeline independently of `process`
        if not args.tool_path:
            args.tool_path = os.path.join(os.path.expanduser("~"), args.tool_set)
        execp_key = {
            "seqc": "seqc_submit_mjobs.py",
            "sera": "sera_submit_mjobs.py",
            "scata": "scata_submit_mjobs.py",
            "five_prime": "./submit.sh",
            "Hashtag": "./submit-hashtag.sh",
            "CITE-seq": "./submit-hashtag.sh",
            "CellRangerVdj": "./submit.sh",
        }
        execp = execp_key[args.tool_set]
        path = args.tool_path
        if args.tool_set in ["Hashtag", "CellRangerVdj", "CITE-seq", "five_prime"]:
            hashtag_param = {
                "secret": os.path.expanduser("~/.cromwell/credentials.json"),
                "labels": os.path.join("config", args.jobs),
                "inputs": os.path.join(
                    "config", re.sub("labels.json$", "inputs.json", args.jobs)
                ),
                "output": "{}.options.aws.json".format(args.tool_set),
            }
            out = args.func(execp, path, hashtag_param, **get_params(args,))
        else:
            out = args.func(execp, path, **get_params(args,))

        import json

        print(
            json.dumps({"args": out["args"], "returncode": out["returncode"]}, indent=4)
        )
        print("stdout:\n", out["stdout"])
        print("stderr:\n", out["stderr"])

    else:
        args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
