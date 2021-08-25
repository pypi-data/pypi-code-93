#!/usr/bin/env python3

"""\
The final step in processing single cell sequencing data.
The following tools are used to transfer raw data and SEQC outputs to their final
destination, and grant access to collaborators to their data.
"""
import os
import random
import re
import string
import urllib.parse
from typing import Tuple

import boto3
import pandas as pd
import regex
from botocore.exceptions import ClientError
from tabulate import tabulate

from .tools import db_connect, execute_cmd, di
from .upload_stats import get_objects


def make_credentials(
    user: str = None,
    name: str = None,
    email: str = None,
    groupname: str = "collaborators",
) -> None:
    """\
    A method to create an AWS user with credentials.

    :param user:
        username for AWS.
    :param name:
        Name of user for tagging.
    :param email:
        Email address of user for tagging.
    :param groupname:
        GroupName policy.

    :return:
        `None`
    """
    link = "https://583643567512.signin.aws.amazon.com/console"
    password = "".join(
        random.choice(string.ascii_letters + string.digits) for i in range(8)
    )
    iam_ = boto3.client("iam")
    try:
        iam_.create_user(
            UserName=user,
            Tags=[{"Key": "Name", "Value": name}, {"Key": "email", "Value": email}],
        )
    except ClientError:

        user = regex.findall("[\p{L}\p{Z}\p{N}_.:/=+\-@]*", user)
        user = "".join(user)
        name = regex.findall("[\p{L}\p{Z}\p{N}_.:/=+\-@]*", name)
        name = "".join(name)

        iam_.create_user(
            UserName=user,
            Tags=[{"Key": "Name", "Value": name}, {"Key": "email", "Value": email}],
        )
    iam_.add_user_to_group(GroupName=groupname, UserName=user)
    key_response = iam_.create_access_key(UserName=user)
    iam_.create_login_profile(
        Password=password, PasswordResetRequired=False, UserName=user
    )
    key_responses = pd.DataFrame(
        [
            [
                user,
                password,
                name,
                email,
                key_response["AccessKey"]["AccessKeyId"],
                key_response["AccessKey"]["SecretAccessKey"],
                link,
            ]
        ],
        columns=[
            "UserName",
            "password",
            "name",
            "email",
            "AccessKeyId",
            "SecretAccessKey",
            "link",
        ],
    )
    key_responses.to_csv(
        os.path.expanduser("~/{}.aws.credentials.csv".format(user)), index=0
    )
    return None


def get_glob(
    sample_name: str = None, AWS_storage: str = None, new_dest: str = None,
) -> Tuple[list, str]:
    """\
    Compile a list of `awscli` commands to move the desired data from a sample to a
    desired destination on `s3uri`.

    :param sample_name:
        Sample name
    :param AWS_storage:
        `s3uri` source path of the sample
    :param new_dest:
        `s3uri` target path of the sample

    :return:
        Collected `mv` commands, and target path
    """
    collect_cmds = []
    _, bucket, key, _, _ = urllib.parse.urlsplit(AWS_storage)
    glob = get_objects(bucket, key.strip("/"), re.compile("glob.list"))
    if glob:
        # selective move of objects
        s3 = boto3.client("s3")
        data = s3.get_object(Bucket=bucket, Key=glob[0])
        cont = data["Body"].read()
        cont = cont.decode().strip().split("\n")
        obj = []
        [
            obj.extend(i)
            for i in [get_objects(bucket, key.strip("/"), re.compile(o)) for o in cont]
        ]
        obj = [re.search(f"(?<=/{sample_name}/).*", i).group() for i in obj]

        collect_cmds.extend(
            [
                "aws s3 mv {} {}".format(
                    os.path.join(AWS_storage, o), os.path.join(new_dest, o)
                )
                for o in obj
            ]
        )
        collect_cmds.append(
            "aws s3 mv --recursive {} {}".format(
                os.path.join(AWS_storage, "FASTQ"), os.path.join(new_dest, "FASTQ")
            )
        )
    else:
        collect_cmds.append(
            "aws s3 mv --recursive {} {}".format(AWS_storage.strip("/"), new_dest)
        )

    return collect_cmds, new_dest


def df_compiler(d: list, m: str = "all", dist: str = "") -> list:
    """\
    Collect essential information for transferring samples to the destination folder
    on AWS.

    :param d:
        Sample ids
    :param m:
        Mode of operation, one of `all`, or `hashtags`, or `TCR`
    :param dist:
        Target folder destination for transfer, which is the parent directory where
        projects and samples are stored, for a particular sample.

    :return:
        Statement results
    """
    statement = {
        "all": (
            "SELECT a.id, a.Sample, a.request_id, "
            "a.projectData_id, b.projectShortName AS project, "
            "a.processed, c.PI_email, "
            "a.AWS_storage, '{}' AS destination, "
            "'sample_data stats_data' AS `table`, "
            "s.Run_Name, "
            "a.processed "
            "FROM sample_data AS a "
            "JOIN project_data AS b "
            "ON a.projectData_id=b.id "
            "JOIN lab AS c "
            "ON b.lab_id=c.id "
            "JOIN genome_index AS g "
            "ON g.id=a.genomeIndex_id "
            "JOIN sc_tech AS s "
            "ON s.id=g.scTech_id "
            "WHERE a.id='{}'"
        ),
        "hashtags": (
            "SELECT a.id, d.Sample, a.request_id, "
            "a.projectData_id, b.projectShortName AS project, "
            "a.processed, c.PI_email, "
            "d.AWS_storage, '{}' AS destination, "
            "'hashtag_lib' AS `table`, "
            "s.Run_Name, "
            "d.`status` "
            "FROM sample_data AS a "
            "JOIN project_data AS b "
            "ON a.projectData_id=b.id "
            "JOIN lab AS c "
            "ON b.lab_id=c.id "
            "JOIN hashtag_lib AS d "
            "ON d.sampleData_id=a.id "
            "JOIN genome_index AS g "
            "ON g.id=d.genomeIndex_id "
            "JOIN sc_tech AS s "
            "ON s.id=g.scTech_id "
            "WHERE a.id='{}'"
        ),
        "tcr": (
            "SELECT a.id, d.Sample, a.request_id, "
            "a.projectData_id, b.projectShortName AS project, "
            "a.processed, c.PI_email, "
            "d.AWS_storage, '{}' AS destination, "
            "'TCR_lib' AS `table`, "
            "s.Run_Name "
            "FROM sample_data AS a "
            "JOIN project_data AS b "
            "ON a.projectData_id=b.id "
            "JOIN lab AS c "
            "ON b.lab_id=c.id "
            "JOIN TCR_lib AS d "
            "ON d.sampleData_id=a.id "
            "JOIN genome_index AS g "
            "ON g.id=d.genomeIndex_id "
            "JOIN sc_tech AS s "
            "ON s.id=g.scTech_id "
            "WHERE a.id='{}'"
        ),
    }
    statements = []
    for i in d:
        statements.append(statement[m.lower()].format(dist, i))

    return statements


def data_transfer(
    sample_ids: list = None,
    results_output: str = None,
    target: str = None,
    mode: str = "all",
) -> None:
    """\
    Move the processed samples to the destination folder on AWS, given the provided
    parameters, including the destination parent `s3uri`.

    :param sample_ids:
        Sample ids from database for samples in project parent directory.
    :param results_output:
        Path to `csv` file with necessary information for transfer, generated by
        `upload_stats`. If passed as `-`, the method will attempt to recover the
        necessary information, internally.
    :param target:
        `s3uri` target parent directory move the outputs to. In general, the expected
        `s3uri` is the root path for `s3uri/<project_name>/<sample_name>/` where
        `<project_name>/<sample_name>/` are omitted.
    :param mode:
        Choose between `all` or `hashtags`, or `TCR`

    :return:
        `None`
    """

    analysis_results_key = {
        "ten_x_v2": "seqc-results",
        "ten_x_v3": "seqc-results",
        "in_drop_v2": "seqc-results",
        "in_drop_v4": "seqc-results",
        "in_drop_v5": "seqc-results",
        "ATAC": "CR-results",
        "CR": "CR-results",
        "five_prime": "CR-results",
        "H2": "Hashtag_results",
        "H3": "Hashtag_results",
        "H4": "Hashtag_results",
        # TODO: "CiteSeq": "CiteSeq_results"
        "CiteSeq": "Hashtag_results",
        "VDJ": "CR-vdj-results",
    }
    # read in results_output.csv file with important information
    try:
        converter = {"Sample": lambda x: str(x)}
        df = pd.read_csv(results_output, index_col=0, converters=converter)
        # set the target destination directory
        if all(df.destination.isna()):
            # Default to PI user name
            if target is None:
                df["destination"] = df.PI_email.str.split("@", expand=True)[0]
                df["destination"] = (
                    "s3://dp-lab-data/collaborators/"
                    + df["destination"].astype(str)
                    + "/"
                )
            else:
                # otherwise use provided `target`
                df["destination"] = target

        elif any(df.destination.isna()):
            print("Fill in the missing `destination` in the table, and try again..")
            import sys

            sys.exit()

    except FileNotFoundError as e:
        try:
            assert results_output == "-", str(e)
            assert (
                target
            ), "AssertionError: the following arguments are required: -t/--target"
            res_df = df_compiler(sample_ids, mode, target)
            res_df = " UNION ".join(res_df)
            db_connect.cur.execute(res_df)
            res = [i for i in db_connect.cur.fetchall()]
            df = pd.DataFrame(res, columns=db_connect.cur.column_names)
        except AssertionError as e:
            import sys

            sys.exit(str(e))

    print(
        "\n\n{:-^100s}\n\n".format(
            "Please review the information below before you proceed"
        )
    )
    print(
        tabulate(
            df.loc[
                :,
                [
                    "id",
                    "Sample",
                    "projectData_id",
                    "project",
                    "PI_email",
                    "AWS_storage",
                    "destination",
                ],
            ],
            headers="keys",
            tablefmt="fancy_grid",
            showindex=False,
        )
    )

    confirm = input("\n\nPlease confirm that all the information is correct (y/n): ")
    if confirm.lower() not in ["y", "yes"]:
        import sys

        sys.exit("\n\nCorrect the information and try again!")
    else:
        print("\n\nThank you! Please wait ...")

    # AWS and IAM
    iam = boto3.client("iam")
    for i, p_id in zip(df.destination, df.projectData_id):
        user = os.path.basename(i.strip("/"))
        _, _, root_bucket, _, _ = urllib.parse.urlsplit(i)
        root_bucket = os.path.dirname(root_bucket.strip("/"))
        # create new credentials only for collaborators
        if root_bucket == "collaborators":
            try:
                resp = iam.get_user(UserName=user)
                print("User {} exists".format(resp["User"]["UserName"]))
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchEntity":
                    # fetch PI name and email for tagging
                    db_connect.cur.execute(
                        f"SELECT PI_name, PI_email FROM lab WHERE id in (SELECT "
                        f"lab_id FROM project_data WHERE id={p_id!r})"
                    )
                    try:
                        name, email = db_connect.cur.fetchall()[0]
                    except IndexError:
                        name, email = ("", "")

                    make_credentials(
                        user=user, name=name, email=email, groupname="collaborators",
                    )
                    newresp = iam.get_user(UserName=user)
                    print("Message: New user was setup with proper credentials")
                    print(newresp)
                else:
                    raise

    outs = []
    for row in df.itertuples():
        new_dest = os.path.join(
            row.destination, re.sub("[\s|/]", "_", row.project), row.Sample
        )
        outs.append(
            get_glob(
                sample_name=row.Sample, AWS_storage=row.AWS_storage, new_dest=new_dest,
            )
        )
    cmds = [i[0] for i in outs]
    dest = [i[1] for i in outs]
    df["command"] = cmds
    df["dest"] = dest

    for i in df.itertuples():
        statement_1 = (
            "UPDATE `raw_data` SET `s3uri`='{}' WHERE "
            "sampleData_id={} AND `platform` = {}".format(
                os.path.join(i.dest, ""), i.id, di[i.Run_Name]
            )
        )
        statement_2 = (
            "UPDATE `run_records` SET `analysis_storage` = '{}' "
            "WHERE `state` = 2 AND `rawData_id` IN "
            "(SELECT MAX(`id`) FROM `raw_data` "
            "WHERE `sampleData_id` = {} AND `platform` = {} "
            "GROUP BY `sampleData_id`)".format(
                os.path.join(i.dest, analysis_results_key[i.Run_Name], ""),
                i.id,
                di[i.Run_Name],
            )
        )
        try:
            # update location in database
            assert i.Run_Name not in ["H2", "H3", "H4", "VDJ", "CiteSeq"]
            statement1 = "UPDATE {} SET AWS_storage='{}' WHERE id={}".format(
                i.table.split()[0], os.path.join(i.dest, ""), i.id
            )
            if i.processed.lower() == "yes":
                statement2 = (
                    "UPDATE {} SET analysis_storage='{}' WHERE "
                    "sampleData_id={}".format(
                        i.table.split()[1],
                        os.path.join(i.dest, analysis_results_key[i.Run_Name], ""),
                        i.id,
                    )
                )
            else:
                statement1 = (
                    "UPDATE {} SET AWS_storage='{}', processed=2, status=2 "
                    "WHERE id={}".format(
                        i.table.split()[0], os.path.join(i.dest, ""), i.id
                    )
                )
                statement2 = ""
        except AssertionError:
            if i.table == "TCR_lib":
                statement1 = (
                    "UPDATE {} SET AWS_storage='{}', analysis_storage='{}' WHERE "
                    "sampleData_id={}".format(
                        i.table,
                        os.path.join(i.dest, ""),
                        os.path.join(i.dest, analysis_results_key[i.Run_Name], ""),
                        i.id,
                    )
                )
            else:
                if i.status == "analyzed":
                    statement1 = (
                        "UPDATE {} SET AWS_storage='{}', "
                        "analysis_storage='{}', status=5 "
                        "WHERE sampleData_id={}".format(
                            i.table,
                            os.path.join(i.dest, ""),
                            os.path.join(i.dest, analysis_results_key[i.Run_Name], ""),
                            i.id,
                        )
                    )
                else:
                    statement1 = (
                        "UPDATE {} SET AWS_storage='{}', status=5 WHERE "
                        "sampleData_id={}".format(
                            i.table, os.path.join(i.dest, ""), i.id,
                        )
                    )
            statement2 = ""
        statements = "; ".join([statement_1, statement_2, statement1, statement2])
        for com in i.command:
            print("Executing command: {}".format(com))
            out, err = execute_cmd(com)
            if err:
                print("ERROR: Executing command {}\n\t".format(com), err.decode())
                statements = ""
        try:
            for result in db_connect.cur.execute(statements, multi=True):
                print(
                    "Number of rows affected by statement '{}': {}".format(
                        result.statement, result.rowcount
                    )
                )
            db_connect.db.commit()
        except TypeError:
            db_connect.db.rollback()
            print(
                "ERROR executing statement:\n\t{}\n\t{}".format(statement1, statement2)
            )
    db_connect.db.disconnect()

    return None
