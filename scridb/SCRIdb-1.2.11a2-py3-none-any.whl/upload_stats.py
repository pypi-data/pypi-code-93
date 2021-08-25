#!/usr/bin/env python3

"""\
Tools to upload stats on sequencing to our database.
"""
import json
import os
import re
import sys
import urllib.parse
from typing import Optional, Pattern, Union

import boto3
import pandas as pd
import yaml
from dateutil.parser import parse
from tabulate import tabulate

from .query import db_connect


def get_objects(
    bucket: str = None, key: str = None, pattern: Pattern[str] = None
) -> list:
    """\
    Filter keys of a bucket with objects matching a pattern.

    :param bucket:
        Bucket name
    :param key:
        Searchable object key
    :param pattern:
        Compiled regular expression object

    :return:
        list of filtered objects in bucket
    """

    s3r = boto3.resource("s3")
    bucket_s3 = s3r.Bucket(bucket)
    k = []
    for obj in bucket_s3.objects.filter(Prefix=key):
        hit = pattern.search(obj.key)
        if hit:
            k.append(obj.key)

    return k


def read_stats(bucket: str, keys: list) -> dict:
    """\
    A method to collect sequencing parameters from output `csv` or `json` files from
    samples on `S3`, provided a `bucket` and a `key`.

    :param bucket:
        bucket name
    :param keys:
        Keys to read stats from

    :return:
        A set of read contents from objects

    """
    s3 = boto3.client("s3")
    contents = {}
    for k in keys:
        try:
            data = s3.get_object(Bucket=bucket, Key=k)
            if os.path.splitext(k)[1] == ".json":
                cont = data["Body"].read()
                cont = json.loads(cont)
            elif os.path.splitext(k)[1] == ".csv":
                import csv

                reader = csv.DictReader(data["Body"].read().decode().split("\n"))
                cont = list(reader)[0]
                cont = dict(cont)
            if "count/outs/summary.json" in k:
                contents["count"] = cont
            elif "reanalyze/outs/summary.json" in k:
                contents["reanalyze"] = cont
            elif "Hashtag_results" in k:
                contents["end_date"] = parse(cont["end"]).strftime("%Y-%m-%d")
            else:
                contents = cont.copy()
        except Exception as e:
            print("`read_stats` Error Message: {}".format(k))
            print(str(e))
            contents = None

    return contents


def get_stats(s3paths: list, sample_ids: list, mode: str = "seqc") -> list:
    """\
    Process stats data and return a formatted structure compatible with the
    processing pipeline, that will be uploaded to the database.

    :param s3paths:
        Path/s to `yaml` or `json` file/s, *or* a single string to parent directory of
        project with samples listed in `sample_names`. For **HASHTAGS**: set this
        parameter to `labels.json` and `hash_tags` to `True`.
    :param sample_ids:
        Sample ids from database for samples in project parent directory.
    :param mode:
        One of `seqc`, `cellranger`, or `hashtags`, to read and return the proper
        format of stats

    :return:
        Stats for each input sample
    """

    def df_hs(x, d):
        X = x.copy()
        X.update(d)
        return X

    def df_cr(x, d):
        X = {"JSON": json.dumps(x)}
        X.update(d)
        return X

    def df_sq(x, d):
        X = x.copy()
        X.update(d)
        X["molecules_per_cell"] = json.dumps(
            {
                "25p": x["molcs_per_cell_25p"],
                "50p": x["med_molcs_per_cell"],
                "75p": x["molcs_per_cell_75p"],
            }
        )
        return X

    keys_mode = {
        "hashtags": {"pattern": re.compile("metadata.json$"), "data_keys": df_hs},
        "cellranger": {
            "pattern": re.compile("/outs/summary.json$|/outs/metrics_summary.csv$"),
            "data_keys": df_cr,
        },
        "seqc": {"pattern": re.compile("mini_summary.json$"), "data_keys": df_sq},
    }

    contents = []
    for s3path, sample_id in zip(s3paths, sample_ids):
        data_ = {"sampleData_id": sample_id, "platform": mode, "results_folder": s3path}
        _, netloc, path, _, _ = urllib.parse.urlsplit(s3path)
        keys_ = get_objects(netloc, path.strip("/"), keys_mode[mode]["pattern"])
        if keys_:
            df = read_stats(netloc, keys_)
            if df:
                data = keys_mode[mode]["data_keys"](df, data_)
                contents.append(data)
            else:
                print(
                    "`get_stats` WARNING: No data found on sample {}.".format(sample_id)
                )
        else:
            print(
                "WARNING: no keys found matching the pattern `{}`".format(
                    keys_mode[mode]["pattern"]
                )
            )

    return contents


def stats(
    s3paths,
    sample_ids: list = None,
    sample_names: list = None,
    results_folder: Union[str, list] = None,
    cellranger: bool = False,
    hash_tags: bool = False,
) -> tuple:
    """\
    The core method which collects stats from successfully processed `scRNAseq`
    samples.

    :param s3paths:
        Path/s to `yaml` or `json` file/s, *or* a single string to parent directory of
        project with samples listed in `sample_names`. For **HASHTAGS**: set this
        parameter to `labels.json` and `hash_tags` to `True`.
    :param sample_ids:
        Sample ids from database for samples in project parent directory.
    :param sample_names:
        Sample names in project parent directory.
    :param results_folder:
        Path to parent directory where outputs from processing pipeline are stored.
    :param hash_tags:
        Hash tags stats format.
    :param cellranger:
        Cell Ranger stats format.

    :return:
        `tuple` of stats and list of sample IDs
    """
    s3paths = [s3paths] if isinstance(s3paths, str) else s3paths
    contents = []

    for i in range(len(s3paths)):
        # read `yml` jobs
        if (
            os.path.splitext(s3paths[i])[1].lower() in [".yml", ".yaml"]
            and os.path.exists(os.path.expanduser(s3paths[i]))
            and os.path.isfile(os.path.expanduser(s3paths[i]))
        ):
            jobs = yaml.full_load(open(os.path.expanduser(s3paths[i])))
            # determine if jobs.yml is a scata source config
            if "uriS3Output" in jobs["jobs"][0]:
                sample_ids = [job["sampleName"].split("_")[0] for job in jobs["jobs"]]
                s3paths_ = [job["uriS3Output"] for job in jobs["jobs"]]
                data = get_stats(s3paths_, sample_ids, mode="cellranger")
                if data:
                    contents.extend(data)

            else:
                s3path = [job["upload-prefix"] for job in jobs["jobs"]]
                sample_ids = [
                    job["output-prefix"].split("_")[0] for job in jobs["jobs"]
                ]
                data = get_stats(s3path, sample_ids)
                if data:
                    contents.extend(data)
        # read json hashtag label file
        elif (
            "labels.json" in s3paths[i]
            and os.path.exists(os.path.expanduser(s3paths[i]))
            and os.path.isfile(os.path.expanduser(s3paths[i]))
        ):
            j_labels = json.load(open(os.path.expanduser(s3paths[i])))
            sample_ids = [j_labels["sample"].split("_")[0]]
            s3paths_ = [j_labels["destination"]]
            data = get_stats(s3paths_, sample_ids, mode="hashtags")
            if data:
                contents.extend(data)
        else:
            if sample_ids is None:
                sys.exit("necessary sample ids not provided")
            if sample_names is None:
                sys.exit("necessary sample names not provided")

            if not isinstance(sample_ids, list):
                sample_ids = [sample_ids]
            if not isinstance(sample_names, list):
                sample_names = [sample_names]

            if cellranger:
                s3paths_ = [
                    os.path.join(s3paths[0], sn, "CR-results", "")
                    for sn in sample_names
                ]
                data = get_stats(s3paths_, sample_ids, mode="cellranger")
            elif hash_tags:
                s3paths_ = [
                    os.path.join(s3paths[0], sn, "Hashtag_results", "")
                    for sn in sample_names
                ]
                data = get_stats(s3paths_, sample_ids, mode="hashtags")
            else:
                # assuming `path` is `seqc-results` full path
                # append `output-prefix` to path appending `_mini_summary.json`
                if isinstance(results_folder, str):
                    s3paths_ = [
                        os.path.join(s3paths[0], sn, results_folder, "")
                        for sn in sample_names
                    ]
                elif results_folder is None:
                    s3paths_ = [os.path.join(s3paths[0], sn, "") for sn in sample_names]
                else:
                    s3paths_ = [
                        os.path.join(s3paths[0], sn, rf, "")
                        for sn, rf in zip(sample_names, results_folder)
                    ]
                data = get_stats(s3paths_, sample_ids)

            if data:
                contents = data
            break

    return contents, sample_ids


def upload_stats_main(
    s3paths: Union[str, list],
    results_folder: Optional[list],
    sample_names: list = None,
    sample_ids: list = None,
    cellranger: bool = False,
    hash_tags: bool = False,
    results_output: str = None,
) -> None:
    """\
    Collects sequencing parameters from successfully processed *scRNAseq* samples,
    and uploads the data to the database.

    :param s3paths:
        Path/s to `yaml` or `json` file/s, *or* a single string to parent directory of
        project with samples listed in `sample_names`. For **HASHTAGS**: set this
        parameter to `labels.json` and `hash_tags` to `True`.
    :param results_folder:
        Path to parent directory where outputs from processing pipeline are stored.
    :param sample_ids:
        Sample ids from database for samples in project parent directory.
    :param sample_names:
        Sample names in project parent directory.
    :param hash_tags:
        Hash tags stats format.
    :param cellranger:
        Cell Ranger stats format.
    :param results_output:
        Path to output file to save resulting data frame with necessary information
        used as input for :class:`~SCRIdb.transfer` sub-command.

    :return:
        `None`
    """
    global statement_, res
    statement = {
        "seqc": (
            "UPDATE stats_data SET "
            "n_reads=%(n_reads)s, "
            "recovered_cells=%(n_cells)s, "
            "avg_reads_per_cell=%(avg_reads_per_cell)s, "
            "avg_molcs_per_cell=%(med_molcs_per_cell)s, "
            "uniqe_mapped_pct=%(uniqmapped_pct)s, "
            "multi_mapped_pct=%(multimapped_pct)s, "
            "genomic_read_pct=%(genomic_read_pct)s, "
            "avg_reads_per_molc=%(avg_reads_per_molc)s, "
            "mt_rna_fraction=%(mt_rna_fraction)s, "
            "molecules_per_cell=%(molecules_per_cell)s, "
            "analysis_storage=%(results_folder)s "
            "WHERE sampleData_id=%(sampleData_id)s"
        ),
        "cellranger": (
            "UPDATE stats_data SET "
            "CR_summary=%(JSON)s, "
            "analysis_storage=%(results_folder)s "
            "WHERE sampleData_id=%(sampleData_id)s"
        ),
        "hashtags": (
            "UPDATE hashtag_lib SET "
            "analysis_storage=%(results_folder)s, "
            "analysis_date=%(end_date)s, "
            "status=4 "
            "WHERE sampleData_id=%(sampleData_id)s"
        ),
        "stmt1": (
            "SELECT a.id, a.Sample, a.request_id, "
            "a.projectData_id, b.projectShortName AS project, "
            "a.processed, c.PI_email, "
            "a.AWS_storage, NULL AS destination, "
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
        "stmt2": (
            "SELECT a.id, d.Sample, a.request_id, "
            "a.projectData_id, b.projectShortName AS project, "
            "a.processed, c.PI_email, "
            "d.AWS_storage, NULL AS destination, "
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
    }

    if results_folder and len(results_folder) == 1:
        results_folder = results_folder[0]

    recovered_sampleids = []
    missed_samplesids = []
    res_df = []

    mini_summaries, sample_ids = stats(
        s3paths=s3paths,
        sample_names=sample_names,
        sample_ids=sample_ids,
        results_folder=results_folder,
        cellranger=cellranger,
        hash_tags=hash_tags,
    )

    for data in mini_summaries:
        recovered_sampleids.append(data["sampleData_id"])
        if data["platform"] == "hashtags":
            try:
                db_connect.cur.execute(
                    "SELECT * from hashtag_lib WHERE sampleData_id=%s",
                    (data["sampleData_id"],),
                )
                res = [i[0] for i in db_connect.cur.fetchall()]
                if not res:
                    missed_samplesids.append(data["sampleData_id"])
                    raise ValueError
                db_connect.cur.execute(statement[data["platform"]], data)
                print(db_connect.cur.statement)
                db_connect.db.commit()
                stmt = statement["stmt2"].format(data["sampleData_id"])
                res_df.append(stmt)
            except Exception as e:
                print("something went wrong: {}".format(data))
                print(str(e))
                db_connect.db.rollback()
        else:
            try:
                db_connect.cur.execute(
                    "SELECT * from stats_data WHERE sampleData_id=%s",
                    (data["sampleData_id"],),
                )
                res = [i[0] for i in db_connect.cur.fetchall()]
                if not res:
                    missed_samplesids.append(data["sampleData_id"])
                    raise ValueError
                # when a key is missing ....
                for k in [
                    "n_reads",
                    "n_cells",
                    "avg_reads_per_cell",
                    "med_molcs_per_cell",
                    "uniqmapped_pct",
                    "multimapped_pct",
                    "genomic_read_pct",
                    "avg_reads_per_molc",
                    "mt_rna_fraction",
                    "molecules_per_cell",
                    "results_folder",
                    "sampleData_id",
                ]:
                    if k not in data:
                        data[k] = None
                db_connect.cur.execute(statement[data["platform"]], data)
                print(db_connect.cur.statement)
                db_connect.cur.execute(
                    "UPDATE important_dates SET upload_stats=CURDATE() "
                    "WHERE sampleData_id=%s",
                    (data["sampleData_id"],),
                )
                print(db_connect.cur.statement)
                db_connect.db.commit()
                stmt = statement["stmt1"].format(data["sampleData_id"])
                res_df.append(stmt)
            except Exception as e:
                print("something went wrong: {}".format(data["sampleData_id"]))
                print(str(e))
                db_connect.db.rollback()

    # write csv output upon completion for further processing
    # will be used to transfer files to their final location
    if recovered_sampleids:
        res_df = " UNION ".join(res_df)
        db_connect.cur.execute(res_df)
        print(db_connect.cur.statement)
        res = [i for i in db_connect.cur.fetchall()]
        data_frame = pd.DataFrame(res, columns=db_connect.cur.column_names)
        if results_output:
            data_frame.to_csv(results_output)
        else:
            print(
                tabulate(
                    data_frame, headers="keys", tablefmt="fancy_grid", showindex=False
                )
            )

    if missed_samplesids:
        print(
            "No stats were collected on the provided set of samples: {}".format(
                missed_samplesids
            )
        )

    db_connect.db.disconnect()

    return None
