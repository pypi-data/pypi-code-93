#!/usr/bin/env python3

from tabulate import tabulate

from .query import run
from .tools import *


def worker_main(
    f_in: Union[str, list],
    source_path: str = None,
    target_path: str = None,
    runseqc: bool = True,
    hashtag: bool = True,
    vdj: bool = True,
    atac: bool = True,
    cr: bool = True,
    fp: bool = True,
    no_rsync: bool = False,
    save: bool = False,
    **args
) -> None:
    """\
    A method to process raw sequencing data returned from **IGO**. Newly sequenced
    samples are copied from IGO shared drive to a defined `S3URI`. Then, the proper
    pipeline is called to process the copied raw data.

    :param f_in:
        Input file name, a single sample name, or a list of sample names, sequenced and
        ready to be processed.
    :param source_path:
        Source path to parent directory of sequenced samples, usually an IGO shared
        drive.
    :param target_path:
        Target path to parent directory of sequenced samples, usually, a `S3URI`.
    :param runseqc:
        Call `seqc` pipeline. Default: `True`.
    :param hashtag:
        Call `hashtag` pipeline. Default: `True`.
    :param vdj:
        Call `VDJ` pipeline. Default: `True`.
    :param atac:
        Call `atac-seq` pipeline. Default: `True`.
    :param cr:
        Call `Cell Ranger` pipeline. Default: `True`.
    :param fp:
        Call 'Five Prime GEX' pipeline. Default: 'True'.
    :param no_rsync:
        Skip copying files to `S3`.
    :param save:
        Write `sample_data` to `.csv` output configured in `--results_output`.
    :param args:
        Additional args passed to other methods.

    :return:
        `None`.

    Example
    =======

    >>> from SCRIdb.worker import *
    >>> args = json.load(open(os.path.expanduser("~/.config.json")))
    >>> args["jobs"] = "jobs.yml"
    >>> args["seqcargs"] = {"min-poly-t": 0}
    >>> db_connect.conn(args)
    >>> worker_main(
        f_in=[
                "Sample_CCR7_DC_1_IGO_10587_12",
                "Sample_CCR7_DC_2_IGO_10587_13",
                "Sample_CCR7_DC_3_IGO_10587_14",
                "Sample_CCR7_DC_4_IGO_10587_15"
        ],
        source_path="/Volumes/peerd/FASTQ/Project_10587/MICHELLE_0194",
        target_path="s3://dp-lab-data/sc-seq/Project_10587",
        runseqc = False,
        no_rsync = True,
        **args
    )
    """

    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s: %(asctime)s: %(message)s")

    fh = logging.FileHandler("processing.log")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    print("Processing new fastq files ...")

    # read in delivery report
    if os.path.isfile(f_in):
        sd = pd.read_csv(f_in, index_col=0)
    elif f_in == "-":
        print(
            "Fill in the Sample ID/s and Sample name/s below, comma or tab "
            "separated:"
        )
        sample_ids = input("\n\nSample ID/s: ")
        if not sample_ids:
            print("Try again:")
            sample_ids = input("\n\nSample ID/s: ")
            if not sample_ids:
                print("Missing Sample ID/s!!")
                sys.exit(1)

        sample_names = input("\n\nSample name/s: ")
        if not sample_names:
            print("Try again:")
            sample_names = input("\n\nSample name/s: ")
            if not sample_names:
                print("Missing Sample name/s!!")
                sys.exit(1)

        sample_ids = re.sub(",", " ", sample_ids.strip()).split()
        sample_names = re.sub(",", " ", sample_names.strip()).split()

        # Collect data from the database
        stmt = (
            "SELECT `id`, `Sample`, `source_path`, `AWS_storage` "
            "FROM `sample_data` WHERE `id`=%s AND `Sample`=%s "
            "UNION "
            "SELECT `sampleData_id`, `Sample`, `source_path`, `AWS_storage` "
            "FROM `hashtag_lib` WHERE `sampleData_id`=%s AND `Sample`=%s "
            "UNION "
            "SELECT `sampleData_id`, `Sample`, `source_path`, `AWS_storage` "
            "FROM `TCR_lib` WHERE `sampleData_id`=%s AND `Sample`=%s"
        )
        results = []
        for items in zip(sample_ids, sample_names):
            db_connect.cur.execute(stmt, items * 3)
            res = db_connect.cur.fetchall()
            if res:
                try:
                    assert res[0][2], "AssertionError: Missing S3URI!"
                    assert res[0][3], "AssertionError: Missing S3URI!"
                except AssertionError as e:
                    print(str(e), "\n\t", db_connect.cur.statement)
                    sys.exit(1)

                results.extend(res)
        sd = pd.DataFrame(columns=["proj_folder", "s3_loc", "fastq"])
        for row in results:
            sd = sd.append(
                [
                    {
                        "proj_folder": os.path.dirname(row[2].strip("/")),
                        "s3_loc": os.path.dirname(row[3].strip("/")),
                        "fastq": row[1],
                    }
                ]
            )

        print(tabulate(sd, headers="keys", tablefmt="fancy_grid", showindex=False))

    else:
        if isinstance(f_in, list):
            f_in = " ".join(f_in)
        else:
            f_in = re.sub(",", " ", f_in)

        if any([source_path is None, target_path is None]):
            print("WARNING: Missing at least one of source_path and target_path!")
            return
        sd = pd.DataFrame(
            {"proj_folder": [source_path], "s3_loc": [target_path], "fastq": [f_in]}
        )

    sample_data = sample_data_frame(sd)

    if not no_rsync:
        failed_samples = copy_files_to_processing_folder(sample_data, **args)
        if failed_samples:
            logging.warning(
                "Samples {} will be excluded from processing due to failed upload or "
                "other issues related to copy_files_to_processing_folder!".format(
                    failed_samples
                )
            )
            criterion = sample_data["id"].map(
                lambda x: int(x) not in [int(i) for i in failed_samples]
            )
            sample_data = sample_data[criterion]

    # write the processing jobs to yaml
    # need to determine `run_name` to build proper yaml files
    # don't include failed-to-transfer samples
    filter_index, exclude_index = filter_samples(sample_data)
    if exclude_index:
        logging.warning(
            "Samples {} will be excluded from processing due to missing "
            "meta data!".format(sample_data.id[exclude_index].tolist())
        )
    sample_data_ = sample_data.iloc[filter_index].copy()

    if sample_data_.empty:
        print("\nSample data frame is empty! Nothing to process!...\n")
        print("{:-^50}\n".format(" END "))

        return

    # frequent query statements being used
    q_newraw = (
        "INSERT INTO `raw_data` "
        "(`sampleData_id`, `platform`, `IGO_id`, `source`, `s3uri`) "
        "VALUES (%s,%s,%s,%s,%s)"
    )
    q_raw = (
        "SELECT * FROM `raw_data` WHERE `sampleData_id`=%s "
        "AND `platform`=%s AND `IGO_id`=%s"
    )
    q_records = (
        "INSERT INTO `run_records` (`rawData_id`,`tools_id`,`workflow_id`, `state`) "
        "VALUES (%s,%s,%s,1)"
    )
    q_tool = "SELECT `id` FROM `tools` WHERE `tool`=%s"

    # record raw data in the database
    for row in sample_data_.itertuples():
        # query the table to prevent duplicate entries
        db_connect.cur.execute(q_raw, (row.id, row.platform, row.igo_id,))
        res = [i for i in db_connect.cur.fetchall()]
        if not res:
            db_connect.cur.execute(
                q_newraw, (row.id, row.platform, row.igo_id, row.source, row.s3uri,),
            )
            print("Update `raw_data`:\n\t", db_connect.cur.statement)
            db_connect.db.commit()
        # update hashtag/citeseq status
        if row.platform in (2, 3):
            statement = (
                "UPDATE `hashtag_lib` SET `status`=2 WHERE "
                "`sampleData_id`={}".format(row.id)
            )
            db_connect.cur.execute(statement)
            print(db_connect.cur.statement)

    idx_seqc = sample_data_["run_name"].map(
        lambda x: x
        not in ["ATAC", "H3", "H2", "H4", "CiteSeq", "VDJ", "five_prime", "CR"]
    )
    idx_atac = sample_data_["run_name"].map(lambda x: x == "ATAC")
    idx_feature_barcoding = sample_data_["run_name"].map(
        lambda x: x in ["H3", "H2", "H4", "CiteSeq"]
    )
    idx_cellranger = sample_data_["run_name"].map(lambda x: x in ["CR"])
    idx_five_prime = sample_data_["run_name"].map(
        lambda x: x in ["five_prime"]
    )
    idx_vdj = sample_data_["run_name"].map(lambda x: x == "VDJ")

    if idx_seqc.any():
        config_jobs_yml = os.path.join(args["dockerizedSEQC"], "config", args["jobs"])
        db_connect.cur.execute(
            q_tool, (os.path.basename(args["dockerizedSEQC"].rstrip("/")),)
        )
        try:
            tools_id = [i[0] for i in db_connect.cur.fetchall()][0]
        except IndexError:
            tools_id = input(
                "Please provide the tool `id` as it appears in the database: "
            )
        jobs_yml_config(
            sample_data_[idx_seqc],
            email=args["email"],
            ami=args["ami"],
            instance_type=args["instance_type"],
            config_jobs_yml=config_jobs_yml,
            seqcargs=args["seqcargs"],
        )

        if runseqc:
            out = run(execp="seqc_submit_mjobs.py", path=args["dockerizedSEQC"], **args)

            try:
                assert out["returncode"] == 0, RuntimeError("SEQC run failed!".upper())
                logging.info("SEQC run initiated successfully!")
            except (AssertionError, RuntimeError) as e:
                print("{:*^50}\n".format(" START ERROR "))
                logging.error(out["stdout"])
                logging.warning(str(e))
                print()
                print("{:*^50}\n".format(" END ERROR "))
            else:
                for row in sample_data_.loc[
                    idx_seqc, ["id", "platform", "igo_id", "source", "s3uri"]
                ].itertuples():

                    db_connect.cur.execute(q_raw, (row.id, row.platform, row.igo_id,))
                    rawData_id = [i[0] for i in db_connect.cur.fetchall()]

                    if rawData_id:
                        db_connect.cur.execute(
                            q_records, (rawData_id[0], tools_id, args["ami"]),
                        )
                        print("Update `run_records`:\n\t", db_connect.cur.statement)

            db_connect.db.commit()

    if idx_atac.any():
        if not args["tool_path"]:
            atac_path = input("Please provide the root path to `scata`:")
            atac_path = os.path.expanduser(atac_path)
        else:
            atac_path = args["tool_path"]
        db_connect.cur.execute(q_tool, (os.path.basename(atac_path.rstrip("/")),))
        try:
            tools_id = [i[0] for i in db_connect.cur.fetchall()][0]
        except IndexError:
            tools_id = input(
                "Please provide the tool `id` as it appears in the database: "
            )
        config_jobs_yml = os.path.join(atac_path, "config", args["jobs"])
        jobs_yml_config(
            sample_data_[idx_atac],
            email=args["email"],
            config_jobs_yml=config_jobs_yml,
        )

        if atac:
            out = run(execp="scata_submit_mjobs.py", path=atac_path, **args)

            try:
                assert out["returncode"] == 0, RuntimeError(
                    "scATAC-seq run failed!".upper()
                )
                logging.info("scATAC-seq run initiated successfully!")
            except (AssertionError, RuntimeError) as e:
                print("{:*^50}\n".format(" START ERROR "))
                logging.error(out["stdout"])
                logging.warning(str(e))
                print()
                print("{:*^50}\n".format(" END ERROR "))
            else:
                for row in sample_data_.loc[
                    idx_atac, ["id", "platform", "igo_id", "source", "s3uri"]
                ].itertuples():

                    db_connect.cur.execute(q_raw, (row.id, row.platform, row.igo_id,))
                    rawData_id = [i[0] for i in db_connect.cur.fetchall()]

                    if rawData_id:
                        # TODO: workflow_id set for "ND" needs to be changed to a known
                        #  id, e.g. ami-12345 or cromwel-${uuid}
                        db_connect.cur.execute(
                            q_records, (rawData_id[0], tools_id, "ND"),
                        )
                        print("Update `run_records`:\n\t", db_connect.cur.statement)

            db_connect.db.commit()

    if idx_feature_barcoding.any():
        if not args["tool_path"]:
            feature_barcoding_path = input("Please provide the root path to `sharp`:")
            feature_barcoding_path = os.path.expanduser(feature_barcoding_path.strip())
        else:
            feature_barcoding_path = args["tool_path"]
        db_connect.cur.execute(
            q_tool, (os.path.basename(feature_barcoding_path.rstrip("/")),)
        )
        try:
            tools_id = [i[0] for i in db_connect.cur.fetchall()][0]
        except IndexError:
            tools_id = input(
                "Please provide the tool `id` as it appears in the " "database: "
            )

        hsample_data = sample_data_[idx_feature_barcoding]
        inputs_labels, exclude_s = json_jobs(
            hsample_data, config_path=feature_barcoding_path
        )

        print("Excluding:", exclude_s)
        filter_excluded = sample_data_["id"].map(lambda x: str(x) not in exclude_s)
        sample_data_ = sample_data_[filter_excluded]
        # TODO: change to feature_barcoding
        if hashtag:
            # generate a secret key for cromwell server if not found in path
            secret_cromwell = get_cromwell_credentials(db_connect.config)
            print("Establishing connection to Cromwell Server, please wait ...!")
            for inputs, labels in inputs_labels:
                kargs = {
                    "inputs": inputs,
                    "labels": labels,
                    "secret": secret_cromwell,
                    "output": "Sharp.options.aws.json",
                }
                try:
                    # TODO: pick the platform from sample_data and execute the proper ./submit.sh
                    #   if paltform == "CITE":
                    #        executable = "./submit_citseq.sh"
                    out = run(
                        execp="./submit-hashtag.sh",
                        path=feature_barcoding_path,
                        cromwell_param=kargs,
                        **args
                    )

                    if out["returncode"] == 0:
                        print(inputs, labels, "successfully deployed to Cromwell!")
                    else:
                        msg = "\n" + "\n".join(
                            [
                                inputs,
                                labels,
                                "returned exit code {}".format(out["returncode"]),
                            ]
                        )

                        raise RuntimeError(msg)

                    label_id = os.path.basename(labels).split("_")[0]
                    label_id = int(label_id)
                    platform = (
                        3
                        if hsample_data.run_name[hsample_data.id == label_id].values[0]
                        == "CiteSeq"
                        else 2
                    )
                    igo_id = sample_data_.loc[
                        (sample_data_.id == label_id)
                        & (sample_data_.platform == platform),
                        "igo_id",
                    ].values[0]

                    db_connect.cur.execute(q_raw, (label_id, platform, igo_id,))
                    rawData_id = [i[0] for i in db_connect.cur.fetchall()]
                    db_connect.cur.execute(
                        q_records,
                        (
                            rawData_id[0],
                            tools_id,
                            "cromwell-" + str(json.loads(out["stdout"])["id"]),
                        ),
                    )
                    print("Update `run_records`:\n\t", db_connect.cur.statement)

                    db_connect.cur.execute(
                        "UPDATE hashtag_lib SET `status`=3 "
                        "WHERE sampleData_id={}".format(label_id)
                    )
                    print("Update `hashtag_lib`:\n\t", db_connect.cur.statement)

                except (TimeoutError, RuntimeError) as e:
                    db_connect.db.rollback()
                    print("{:*^50}\n".format(" START ERROR "))
                    logging.error(str(e))
                    print()
                    print("{:*^50}\n".format(" END ERROR "))

                db_connect.db.commit()

    if idx_vdj.any():
        if not args["tool_path"]:
            vdj_path = input("Please provide the root path to `CellRangerVdj`:")
            vdj_path = os.path.expanduser(vdj_path)
        else:
            vdj_path = args["tool_path"]
        db_connect.cur.execute(q_tool, (os.path.basename(vdj_path.rstrip("/")),))
        try:
            tools_id = [i[0] for i in db_connect.cur.fetchall()][0]
        except IndexError:
            tools_id = input(
                "Please provide the tool `id` as it appears in the database: "
            )
        vdjsample_data = sample_data_[idx_vdj]
        inputs_labels, exclude_s = json_jobs(vdjsample_data, config_path=vdj_path)

        print("Excluding:", exclude_s)
        filter_excluded = sample_data_["id"].map(lambda x: str(x) not in exclude_s)
        sample_data_ = sample_data_[filter_excluded]

        if vdj:
            # generate a secret key for cromwell server if not found in path
            secret_cromwell = get_cromwell_credentials(db_connect.config)
            print("Establishing connection to Cromwell Server, please wait ...!")
            for inputs, labels in inputs_labels:
                kargs = {
                    "inputs": inputs,
                    "labels": labels,
                    "secret": secret_cromwell,
                    "output": "CellRangerVdj.options.aws.json",
                }
                try:
                    out = run(
                        execp="./submit.sh", path=vdj_path, cromwell_param=kargs, **args
                    )
                    if out["returncode"] == 0:
                        print(inputs, labels, "successfully deployed to Cromwell!")
                    else:
                        msg = "\n" + "\n".join(
                            [
                                inputs,
                                labels,
                                "returned exit code {}".format(out["returncode"]),
                            ]
                        )

                        raise RuntimeError(msg)

                    print(inputs, labels, "successfully deployed to Cromwell!")
                    label_id = os.path.basename(labels).split("_")[0]
                    label_id = int(label_id)
                    platform = 4
                    igo_id = sample_data_.loc[
                        (sample_data_.id == label_id)
                        & (sample_data_.platform == platform),
                        "igo_id",
                    ].values[0]

                    db_connect.cur.execute(q_raw, (label_id, platform, igo_id,))
                    rawData_id = [i[0] for i in db_connect.cur.fetchall()]
                    db_connect.cur.execute(
                        q_records,
                        (
                            rawData_id[0],
                            tools_id,
                            "cromwell-" + str(json.loads(out["stdout"])["id"]),
                        ),
                    )
                    print("Update `run_records`:\n\t", db_connect.cur.statement)

                    db_connect.cur.execute(
                        "UPDATE TCR_lib SET `status`=3 "
                        "WHERE sampleData_id={}".format(label_id)
                    )
                    print("Update `TCR_lib`:\n\t", db_connect.cur.statement)

                except (TimeoutError, RuntimeError) as e:
                    db_connect.db.rollback()
                    print("{:*^50}\n".format(" START ERROR "))
                    logging.error(str(e))
                    print()
                    print("{:*^50}\n".format(" END ERROR "))

                db_connect.db.commit()

    if idx_five_prime.any():
        if not args["tool_path"]:
            five_prime_path = input("Please provide the root path to `CellRangerGex`:")
            five_prime_path = os.path.expanduser(five_prime_path)
        else:
            five_prime_path = args["tool_path"]
        db_connect.cur.execute(q_tool, (os.path.basename(five_prime_path.rstrip("/")),))
        try:
            tools_id = [i[0] for i in db_connect.cur.fetchall()][0]
        except IndexError:
            tools_id = input(
                "Please provide the tool `id` as it appears in the database: "
            )
        five_prime_sample_data = sample_data_[idx_five_prime]
        inputs_labels, exclude_s = json_jobs(five_prime_sample_data, config_path=five_prime_path)

        print("Excluding:", exclude_s)
        filter_excluded = sample_data_["id"].map(lambda x: str(x) not in exclude_s)
        sample_data_ = sample_data_[filter_excluded]

        if fp:
            # generate a secret key for cromwell server if not found in path
            secret_cromwell = get_cromwell_credentials(db_connect.config)
            print("Establishing connection to Cromwell Server, please wait ...!")
            for inputs, labels in inputs_labels:
                kargs = {
                    "inputs": inputs,
                    "labels": labels,
                    "secret": secret_cromwell,
                    "output": "CellRangerGex.options.aws.json",
                }
                try:
                    out = run(
                        execp="./submit.sh", path=five_prime_path, cromwell_param=kargs, **args
                    )
                    if out["returncode"] == 0:
                        print(inputs, labels, "successfully deployed to Cromwell!")
                    else:
                        msg = "\n" + "\n".join(
                            [
                                inputs,
                                labels,
                                "returned exit code {}".format(out["returncode"]),
                            ]
                        )

                        raise RuntimeError(msg)

                    print(inputs, labels, "successfully deployed to Cromwell!")
                    label_id = os.path.basename(labels).split("_")[0]
                    label_id = int(label_id)
                    platform = 5
                    igo_id = sample_data_.loc[
                        (sample_data_.id == label_id)
                        & (sample_data_.platform == platform),
                        "igo_id",
                    ].values[0]

                    db_connect.cur.execute(q_raw, (label_id, platform, igo_id,))
                    rawData_id = [i[0] for i in db_connect.cur.fetchall()]
                    db_connect.cur.execute(
                        q_records,
                        (
                            rawData_id[0],
                            tools_id,
                            "cromwell-" + str(json.loads(out["stdout"])["id"]),
                        ),
                    )
                    print("Update `run_records`:\n\t", db_connect.cur.statement)

                except (TimeoutError, RuntimeError) as e:
                    db_connect.db.rollback()
                    print("{:*^50}\n".format(" START ERROR "))
                    logging.error(str(e))
                    print()
                    print("{:*^50}\n".format(" END ERROR "))

                db_connect.db.commit()

    if idx_cellranger.any():
        if not args["tool_path"]:
            cellranger_path = input("Please provide the root path to `sera`:")
            cellranger_path = os.path.expanduser(cellranger_path)
        else:
            cellranger_path = args["tool_path"]
        db_connect.cur.execute(q_tool, (os.path.basename(cellranger_path.rstrip("/")),))
        try:
            tools_id = [i[0] for i in db_connect.cur.fetchall()][0]
        except IndexError:
            tools_id = input(
                "Please provide the tool `id` as it appears in the database: "
            )
        config_jobs_yml = os.path.join(cellranger_path, "config", args["jobs"])
        jobs_yml_config(
            sample_data_[idx_cellranger],
            email=args["email"],
            config_jobs_yml=config_jobs_yml,
        )

        if cr:
            out = run(execp="sera_submit_mjobs.py", path=cellranger_path, **args)

            try:
                assert out["returncode"] == 0, RuntimeError(
                    "Cell Ranger run failed!".upper()
                )
                logging.info("Cell Ranger run initiated successfully!")
            except (AssertionError, RuntimeError) as e:
                print("{:*^50}\n".format(" START ERROR "))
                logging.error(out["stdout"])
                logging.warning(str(e))
                print()
                print("{:*^50}\n".format(" END ERROR "))
            else:
                for row in sample_data_.loc[
                    idx_cellranger, ["id", "platform", "igo_id", "source", "s3uri"]
                ].itertuples():

                    db_connect.cur.execute(q_raw, (row.id, row.platform, row.igo_id,))
                    rawData_id = [i[0] for i in db_connect.cur.fetchall()]

                    if rawData_id:
                        # TODO: workflow_id set for "ND" needs to be changed to a known
                        #  id, e.g. ami-12345 or cromwell-${uuid}
                        db_connect.cur.execute(
                            q_records, (rawData_id[0], tools_id, "ND"),
                        )
                        print("Update `run_records`:\n\t", db_connect.cur.statement)

            db_connect.db.commit()

    if save:
        print("Writing output to `{}`.".format(args["results_output"]))
        sample_data_.to_csv(args["results_output"])
    else:
        print(
            tabulate(
                sample_data_, headers="keys", tablefmt="fancy_grid", showindex=False
            )
        )

    db_connect.db.disconnect()

    return None
