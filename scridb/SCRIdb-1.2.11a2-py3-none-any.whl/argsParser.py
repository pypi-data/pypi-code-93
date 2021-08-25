#!/usr/bin/env python3

"""\
parser for command line arguments.
"""

import argparse
import json
import os
import sys

import SCRIdb.query


def parse_arguments(argsv: str = None) -> argparse.Namespace:
    """\

    :param argsv: command line arguments
    :return: args :class:`~argparse.Namespace`
    """
    parent_parser = argparse.ArgumentParser(fromfile_prefix_chars="@", add_help=False)

    class StoreDictKeyPair(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if not values:
                sys.exit("ERROR: Missing `--seqc-args` values!")
            my_dict = {}
            for kv in values.split(","):
                k, v = kv.split("=")
                my_dict[k] = v
            setattr(namespace, self.dest, my_dict)

    ggroup = parent_parser.add_argument_group("global options")
    pgroup = parent_parser.add_argument_group("process options")
    ogroup = parent_parser.add_argument_group("output options")
    ggroup.add_argument(
        "-c",
        "--config",
        dest="config",
        action="store",
        nargs="?",
        default=os.path.expanduser("~/.config.json"),
        help="path to database configuration file. Default: $HOME/.config.json",
    )

    ggroup.add_argument(
        "-f",
        "--file",
        dest="file",
        action="store",
        nargs="?",
        help="With `data_submission` sub-command: string, path to html form. With "
        "`process` sub-command: string, path to `.csv` file listing newly delivered "
        "sequencing data from the genome center. OR, list of comma separated sample "
        "names (no spaces)- override the `.csv` file. A special case for `process` "
        "sub-command: pass `-`, and follow the prompt on screen. For more details "
        "and examples follow the documentation at https://tinyurl.com/y5f9pzx8 ",
    )

    ggroup.add_argument(
        "-v",
        "--version",
        dest="ver",
        action="store_true",
        help="Print the package version and exit.",
    )

    ogroup.add_argument(
        "-o",
        "--results_output",
        dest="results_output",
        action="store",
        nargs="?",
        default="~/results_output.csv",
        help="Default: ~/results_output.csv. Path to results_output `csv` file. When "
        "used with `process` sub-command, a `sample_data` data frame is written. "
        "When used with `upload_stats` sub-command, a data frame with necessary "
        "information used as input for `data_transfer` sub-command, is written. "
        "Before invoking `data_transfer` sub-command, the user must complete the "
        "`destination` column in the resulting data frame. IN CASES WHERE "
        "`process` AND/OR `upload_stats` ARE SKIPPED USE `-` AS THE ARGUMENT. "
        "This is useful for cases where we need to share raw data with "
        "collaborators without processing.",
    )

    pgroup.add_argument(
        "-j",
        "--jobs",
        dest="jobs",
        action="store",
        nargs="?",
        default="jobs.yml",
        help="Default: `jobs.yml`. "
        "When used with `process` sub-command, a <jobs.yml> is passed as the OUTPUT "
        "file name instead of the default `jobs.yml`. When used with `run` the "
        "provided jobs filename will override the default `jobs.yml`.",
    )

    pgroup.add_argument(
        "-e",
        "--email",
        dest="email",
        action="store",
        nargs="?",
        help="Override email address to receive SEQC run summary in config.",
    )

    pgroup.add_argument(
        "-p",
        "--pem",
        dest="pem",
        action="store",
        nargs="?",
        help="Override path to AWS EC key pair file `.pem` in config.",
    )

    pgroup.add_argument(
        "-a",
        "--ami",
        dest="ami",
        action="store",
        nargs="?",
        help="Override Amazon Machine Image (AMI) in config.",
    )

    pgroup.add_argument(
        "-n",
        "--instance_type",
        dest="instance_type",
        action="store",
        nargs="?",
        help="Instance Type in config for SEQC.",
    )

    pgroup.add_argument(
        "-dS",
        "--dockerized-SEQC",
        dest="dockerizedSEQC",
        action="store",
        nargs="?",
        help="Override default path in config to root directory of the "
        "dockerized SEQC.",
    )

    pgroup.add_argument(
        "-tp",
        "--tool_path",
        dest="tool_path",
        action="store",
        nargs="?",
        help="Provide path to root directory of the scata or sera. "
        "This will override the default, assuming it is in $HOME.",
    )

    parser = argparse.ArgumentParser(fromfile_prefix_chars="@", parents=[parent_parser])
    subparsers = parser.add_subparsers(
        help="Required. Call one of the following sub-commands. "
        "While `process` sub-command calls `run`, `run` can be "
        "called independently, if a processing jobs.yml already exists."
    )

    data_submission_parser = subparsers.add_parser(
        "data_submission",
        help="sub-command to submit new projects and samples to the database "
        "and to collect parameters on library preparations.",
    )

    data_submission_parser.add_argument(
        "mode",
        choices=["submitnew", "stats"],
        nargs="*",
        help="Choose the mode of action: {submitnew, stats}; "
        "submitnew: submit new forms to the database; "
        "stats: insert new library parameters to stats table."
        "Can choose either one or both",
    )

    data_submission_parser.set_defaults(func=SCRIdb.query.data_submission)

    process_parser = subparsers.add_parser(
        "process",
        help="sub-command to process newly delivered fatsq files from fhe "
        "genome center core.",
    )

    process_parser.add_argument(
        "--runseqc",
        action="store_false",
        default=True,
        help="Skip `seqc` run on submitted jobs.",
    )

    process_parser.add_argument(
        "--hashtag",
        action="store_false",
        default=True,
        help="Skip `hashtag` run on submitted jobs.",
    )

    process_parser.add_argument(
        "--vdj",
        action="store_false",
        default=True,
        help="Skip `VDJ` (TCR) run on submitted jobs.",
    )

    process_parser.add_argument(
        "--atac",
        action="store_false",
        default=True,
        help="Skip `atac-seq` run on submitted jobs.",
    )

    process_parser.add_argument(
        "--CR",
        action="store_false",
        default=True,
        help="Skip `Cell Ranger` run on submitted jobs.",
    )

    process_parser.add_argument(
        "--fp",
        action="store_false",
        default=True,
        help="Skip `CellRanger 5' GEX` run on submitted jobs.",
    )

    process_parser.add_argument(
        "--no-rsync",
        dest="no_rsync",
        action="store_true",
        default=False,
        help="Skip copying files to AWS.",
    )

    process_parser.add_argument(
        "--source_path",
        dest="source_path",
        action="store",
        nargs="?",
        help="Source directory of samples listed with `--file`.",
    )

    process_parser.add_argument(
        "--target_path",
        dest="target_path",
        action="store",
        nargs="?",
        help="Copying target directory for samples listed with `--file`.",
    )

    process_parser.add_argument(
        "--seqc-args",
        dest="seqcargs",
        action=StoreDictKeyPair,
        nargs="?",
        metavar="KEY1=VAL1,KEY2=VAL2...",
        help="Additional arguments to pass to SEQC.",
    )

    process_parser.add_argument(
        "--md5sums",
        dest="md5sums",
        action="store",
        nargs="?",
        help="Path to MD5 hashes.",
    )

    process_parser.add_argument(
        "--save",
        dest="save",
        action="store_true",
        default=False,
        help="Write `sample_data` to .csv output configured in --results_output.",
    )

    process_parser.set_defaults(func=SCRIdb.query.process)

    uploadstats_parser = subparsers.add_parser(
        "upload_stats",
        help="sub-command to upload stats following successful SEQC/scata/sera run. "
        "This sub-command accepts one or more space separated positional arguments "
        "of full paths to jobs.yml files, or labels.json in the case of hashtags. "
        "Use -o to provide full path to output csv file with data results necessary "
        "for data_transfer sub-command.",
    )

    uploadstats_parser.add_argument(
        "s3paths",
        action="store",
        nargs="+",
        help="A single string or a list of paths to jobs.yml, "
        "OR a single string to parent directory of project with samples listed in "
        "`sample_names`. "
        "For HASHTAGS: a single string or a list of paths to labels.json, "
        "OR a single string to root directory of project with samples listed in "
        "`sample_names` "
        "CONDITIONAL on using the `--hash_tags` switch.",
    )

    uploadstats_parser.add_argument(
        "-s",
        dest="sample_names",
        action="store",
        nargs="*",
        default=None,
        help="A single string or a list of sample names. "
        "Used in the case of uploading stats NOT using a jobs files.",
    )

    uploadstats_parser.add_argument(
        "-i",
        dest="sample_ids",
        action="store",
        nargs="*",
        default=None,
        help="A single string or a list of sample ids. "
        "Used in the case of uploading stats NOT using a jobs files.",
    )

    uploadstats_parser.add_argument(
        "-r",
        dest="results_folder",
        action="store",
        nargs="*",
        default="seqc-results",
        help="SEQC summary results containing folder. Override the default "
        "`seqc-results` folder.",
    )

    uploadstats_parser.add_argument(
        "--cellranger",
        dest="cellranger",
        action="store_true",
        default=False,
        help="Cell Ranger or ATAC-seq stats. Used in the case of uploading stats NOT "
        "using the `jobs.yml` template as input.",
    )

    uploadstats_parser.add_argument(
        "--hash_tags",
        dest="hash_tags",
        action="store_true",
        default=False,
        help="Hash tags switch. Used in the case of uploading stats using the "
        "`lables.json` template as input.",
    )

    uploadstats_parser.set_defaults(func=SCRIdb.query.uploadstats)

    transfer_parser = subparsers.add_parser(
        "data_transfer",
        help="sub-command to transfer SEQC results to destination folder designated "
        "in resulting csv file from upload_stats. Use -o to provide the full "
        "path to the csv file.",
    )

    transfer_parser.add_argument(
        "-i",
        dest="sample_ids",
        action="store",
        nargs="*",
        default=None,
        help="A single string or a list of sample ids. "
        "Used in the case of uploading stats NOT using a jobs files.",
    )

    transfer_parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        action="store",
        choices=["all", "hashtags", "TCR"],
        default="all",
        help="Default: all, a switch mode for hashtags.",
    )

    transfer_parser.add_argument(
        "-t",
        "--target",
        dest="target",
        action="store",
        nargs="?",
        help="S3URI in the form of s3://bucket/key/, where data will be copied to. "
        "In general, the expected `s3URI` is the root path for "
        "`s3URI/<project_name>/<sample_name>/ where <project_name>/<sample_name>/ "
        "are omitted.",
    )

    transfer_parser.set_defaults(func=SCRIdb.query.data_transfer)

    run_parser = subparsers.add_parser(
        "run",
        help="sub-command to call SeqC or scata (ATAC-seq) or sera (Cell Ranger) "
        "independently, conditional on having a jobs.yml file in path defined by "
        "config.",
    )

    run_parser.add_argument(
        "tool_set",
        choices=["seqc", "scata", "sera", "Hashtag", "CellRangerVdj", "five_prime"],  # TODO: Add "CITE-seq"
        help="Choose between `seqc`, `scata`, `sera`, `Hashtag`, `CellRangerVdj`, or `five_prime`"
        " to run SeqC, ATAC, Cell Ranger, ATAC, HashTag, CellRanger V(D)J, or CellRanger 5' GEX"
        " using the defined jobs.yml/labels.json file in the {tool}/config. MUST"
        " PROVIDE PATH TO THE TOOL BEING USED TO PROCESS using `-tp`.",
    )

    run_parser.set_defaults(func=SCRIdb.query.run)

    args = parser.parse_args(argsv)

    if args.ver:
        from SCRIdb.version import __version__

        print(__version__)
        sys.exit()

    try:
        assert args.func
    except AttributeError:
        print()
        print("EROOR: missing positional argument!")
        print()
        sys.exit(parser.print_help())

    # pass config defaults to args while keeping overrides
    config = json.load(open(args.config))
    args.file = config["path_submit_data"] if not args.file else args.file
    args.dockerizedSEQC = (
        config["dockerizedSEQC"] if not args.dockerizedSEQC else args.dockerizedSEQC
    )
    args.email = config["email"] if not args.email else args.email
    args.pem = config["pem"] if not args.pem else args.pem
    args.ami = config["ami"] if not args.ami else args.ami
    args.instance_type = (
        config["instance_type"] if not args.instance_type else args.instance_type
    )

    return args
