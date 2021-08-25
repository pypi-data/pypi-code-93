#!/usr/bin/env python3

"""\
MySQL statements
"""

import math
import re
import sys
from typing import Union

import nltk
from nltk.corpus import stopwords
from dateutil.parser import parse

from .query import db_connect

################################################################
try:
    stopwords.words("english")
except (LookupError, OSError) as e:
    nltk.download("stopwords")

kargs_manager = {
    "Single-cell gene expression": "Choose 10X Kit",
    "InDrop": "Choose InDrop Version",
    "Single-cell immune profiling": "Choose Kit",
    "Single-cell ATAC-seq": "10X_scATAC",
}
################################################################


def sqlargs(kargs: dict, val: Union[str, int] = "NULL") -> dict:
    """\
    A cleaner for `nan` data types of empty values in dictionary.

    :param kargs:
        Dirty dictionary
    :param val:
        Replacement value

    :return:
        Clean dictionary
    """
    for k, v in kargs.items():
        if isinstance(v, dict):
            sqlargs(v)
        else:
            if isinstance(v, float) and math.isnan(v):
                kargs[k] = val
    return kargs


def get_sampleIndex(x: str) -> Union[int, str]:
    """\
    If sample_index id record not found, records new `sample_index` value in the
    database, and returns its `id`.

    :param x:
        Sample index to be searched for in the data base.

    :return:
        id value from the data base
    """
    if x != "NULL":
        db_connect.cur.execute(
            "SELECT id FROM sample_index WHERE Sample_Index=%s", (x,)
        )
        res = [i[0] for i in db_connect.cur.fetchall()]
        if res:
            sampleIndex_id = res[0]
        else:
            # attempt to add a new index to the database
            db_connect.cur.execute(
                "INSERT INTO sample_index (Sample_Index) Values (%s)", (x,)
            )
            db_connect.cur.execute("SELECT LAST_INSERT_ID()")
            sampleIndex_id = [i[0] for i in db_connect.cur.fetchall()][0]
            db_connect.db.commit()
        return sampleIndex_id
    else:
        return "NULL"


def get_hashtagBarcodes_id(seq: str, bar: str = None) -> Union[int, str]:
    """\
    Search and return ids of hashtag barcodes from the database.

    :param seq:
        barcode sequence
    :param bar:
        associated barcode with the barcode sequence

    :return:
        ids of hashtag barcodes

    """
    barcode = re.search(r"\d{4}$", bar)
    barcode = barcode.group()
    cat = re.search(r"^[a-zA-Z]?", bar)
    cat = cat.group()
    q = (
        f"SELECT id FROM hashtag_barcodes WHERE barcode_sequence='{seq}' "
        f"AND barcode='{barcode}' AND category like '%{cat}'"
    )
    db_connect.cur.execute(q)
    res = [i[0] for i in db_connect.cur.fetchall()]
    if res:
        return res[0]
    else:
        return "NULL"


class Query:
    """\
    Methods to read in key arguments and prepare the MySQL query command
    arguments to be passed for MySQL query execution

    Returns:
    --------
    `str` MySQL statement
    """

    def __init__(
        self,
        isinsert: Union[bool, str] = "",
        table: str = None,
        where: dict = None,
        **kwargs,
    ):
        """\
        Build MySQL statements to insert or update records in the data base.

        :param isinsert:
            if `True` build an `INSERT` statement, else build an `UPDATE` statement
        :param table:
            name of target table from the data base
        :param where:
            kwargs for `WHERE` clause used with `UPDATE`
        :param kargs: `kwargs`
            additional arguments passed for columns and corresponding values
        """
        self.table = table
        self.where = where
        self.kwargs = kwargs
        self.appropriate_case = isinsert

    def __repr__(self):
        return self.appropriate_case

    @classmethod
    def __insert_into(cls, table: str = None, **kwargs) -> str:
        """\
        Build insert statement.

        :param table:
            target table name from the data base

        :return
            MySQL insert statement
        """
        cols = ",".join(["%s"] * len(kwargs)) % tuple(kwargs.keys())
        values = ",".join(["%({})s".format(i) for i in kwargs.keys()])
        que = f"INSERT INTO {table} ({cols}) VALUES ({values})"
        return que

    @classmethod
    def __update_table(cls, table: str = None, where: dict = None, **kwargs) -> str:
        """\
        Build update statement.

        :param table:
            target table name from the data base
        :param where:
            kargs for a MySQL WHERE clause of key=value

        :return
            MySQL update statement
        """
        cols = ",".join(["{}=%({})s".format(k, k) for k in kwargs.keys()])
        key, val = [[k, v] for k, v in where.items()][0]
        que = f"UPDATE {table} SET {cols} WHERE {key}='{val}'"
        return que

    @property
    def appropriate_case(self) -> str:
        return self.__appropriatecase

    @appropriate_case.setter
    def appropriate_case(self, isinsert):
        if isinstance(isinsert, bool):
            if isinsert:
                self.__appropriatecase = self.__insert_into(self.table, **self.kwargs)
            else:
                self.__appropriatecase = self.__update_table(
                    self.table, self.where, **self.kwargs
                )
        else:
            self.__appropriatecase = isinsert


def sampledata_sql(kwargs: dict) -> None:
    """\
    A method to insert new records of samples to the database.

    :param kwargs:
        A set of keys and values to be inserted to the database

    :return:
        MySQL statements
    """
    statements = []

    # for sample data get project data id
    query = "SELECT id FROM project_data WHERE request_id=%s"
    db_connect.cur.execute(query, (kwargs["proj_request_id"],))
    projectData_id = [i[0] for i in db_connect.cur.fetchall()]
    if not projectData_id:
        sys.exit("ERROR: missing project id associated with the sample/s !!")
    kwargs["projectData_id"] = projectData_id[0]

    for sample in kwargs["samples"]:
        # before initiating any MySQL statement check for missing important labels
        regex = re.compile(r"[\\&$@=;:+,?}{^%`\]\[<>~#|/]")
        try:
            # Validate sample name
            assert regex.findall(sample) == [], "Validation failed for sample Name!"
        except AssertionError as e:
            print(str(e))
            print("Sample name has unsafe characters:", regex.findall(sample))
            sys.exit("Fix the sample name '{}' and try again.".format(sample))
        try:
            db_connect.cur.execute("SELECT Species from species")
            sp = [i[0].lower() for i in db_connect.cur.fetchall()]
            assert (
                "Species" in kwargs["samples"][sample]
            ), "Key 'Species' not found in sample {}".format(kwargs["samples"][sample])
            assert kwargs["samples"][sample][
                "Species"
            ], "Missing species for sample {}!!".format(kwargs["samples"][sample])
            assert (
                kwargs["samples"][sample]["Species"].lower() in sp
            ), "Species does not match registry in DB: {}".format(
                kwargs["samples"][sample]["Species"]
            )
            assert "Sample type" in kwargs, "'Sample type' not found in {}".format(
                kwargs
            )
        except AssertionError as e:
            sys.exit("AssertionError: {}".format(str(e)))

    # get other ids
    for sample in kwargs["samples"]:
        _labels = [
            ("species_id", "species", "Species", kwargs["samples"][sample]["Species"]),
            ("sampleType_id", "sample_type", "sample_Type", kwargs["Sample type"]),
        ]
        query = "SELECT CONCAT('{} ',`id`) FROM {} WHERE {}='{}'"
        db_connect.cur.execute(query.format(*_labels[0]))
        res = [i[0] for i in db_connect.cur.fetchall()]
        for i in res:
            k, v = i.split()
            kwargs["samples"][sample][k] = v
        db_connect.cur.execute(query.format(*_labels[1]))
        res = [i[0] for i in db_connect.cur.fetchall()]
        if not res:
            db_connect.cur.execute(
                "INSERT INTO `sample_type` (`sample_Type`) VALUES "
                "('{}')".format(kwargs["Sample type"])
            )
            db_connect.cur.execute("SELECT LAST_INSERT_ID()")
            sampleType_id = [i[0] for i in db_connect.cur.fetchall()][0]
            kwargs["samples"][sample]["sampleType_id"] = sampleType_id
        else:
            for i in res:
                k, v = i.split()
                kwargs["samples"][sample][k] = v

        kargs = {
            "Sample": sample,
            "projectData_id": kwargs["projectData_id"],
            "request_id": kwargs["request_id"],
            "sampleType_id": kwargs["samples"][sample]["sampleType_id"],
        }
        notes = []
        _notes = ["Notes", "Notes or comments", "Staff notes or comments", "Problems"]
        for note in range(len(_notes)):
            if _notes[note] in kwargs and kwargs[_notes[note]] != "NULL":
                notes.append(": ".join([_notes[note], kwargs[_notes[note]]]))
            elif (
                _notes[note] in kwargs["samples"][sample]
                and kwargs["samples"][sample][_notes[note]] != "NULL"
            ):
                notes.append(
                    ": ".join([_notes[note], kwargs["samples"][sample][_notes[note]]])
                )
        if notes:
            kargs["notes"] = " |*** ".join(notes)

        query = (
            "SELECT `id` FROM sample_data WHERE projectData_id=%(projectData_id)s "
            "AND Sample=%(Sample)s AND request_id=%(request_id)s COLLATE utf8mb4_bin"
        )
        db_connect.cur.execute(query, kargs)
        res = db_connect.cur.fetchall()
        if res:
            sys.exit(
                f"message: Sample already exists in database:\n'{db_connect.cur.statement}'"
            )

        stmt = Query(isinsert=True, table="sample_data", **kargs)
        db_connect.cur.execute(stmt.appropriate_case, kargs)
        print(db_connect.cur.statement)
        db_connect.cur.execute("SELECT LAST_INSERT_ID()")
        last_id = [i[0] for i in db_connect.cur.fetchall()]
        kwargs["samples"][sample]["sampleData_id"] = last_id[0]

        # make insert statement for important_dates
        kargs = {
            "sampleData_id": kwargs["samples"][sample]["sampleData_id"],
            "submission_date": kwargs["date_created"],
        }
        stmt = Query(isinsert=True, table="important_dates", **kargs)
        statements.append([stmt.appropriate_case, kargs])

        # make insert statement for sample origin
        _columns = [
            "species_id",
            "organ",
            "subRegion",
            "cellType",
            "tumor_status",
            "biopsy_site",
            "FACS_Markers",
        ]
        _labels = [
            "species_id",
            "Organ/fluid",
            "Sub-region",
            "Cell Type",
            "Tumor Status",
            "Biopsy Site",
            "FACS Markers",
        ]
        kargs = {"sampleData_id": kwargs["samples"][sample]["sampleData_id"]}
        for label, column in zip(_labels, _columns):
            try:
                if kwargs["samples"][sample][label] != "NULL":
                    kargs[column] = kwargs["samples"][sample][label]
            except KeyError:
                pass
        stmt = Query(isinsert=True, table="sample_origin", **kargs)
        statements.append([stmt.appropriate_case, kargs])

        # make insert statement for hashtag barcodes
        if "hashtag_parameters" in kwargs["samples"][sample]:
            kwargs["samples"][sample]["hashtag_parameters"]["hashtagBarcodes_id"] = {}
            for k in kwargs["samples"][sample]["hashtag_parameters"]["hashtags"]:
                seq = kwargs["samples"][sample]["hashtag_parameters"]["hashtags"][k]
                bar = kwargs["samples"][sample]["hashtag_parameters"]["barcodes"][k]
                hashtagBarcodes_id = get_hashtagBarcodes_id(seq, bar)
                kwargs["samples"][sample]["hashtag_parameters"][
                    "hashtagBarcodes_id"
                ].update({k: hashtagBarcodes_id})
            # new cell hashing table
            _columns = ["hashtagBarcodes_id", "demultiplex_label", "notes"]
            _labels = ["hashtagBarcodes_id", "hlabels", "hashtag_notes"]
            for k in kwargs["samples"][sample]["hashtag_parameters"][
                "hashtagBarcodes_id"
            ].keys():
                kargs = {"sampleData_id": kwargs["samples"][sample]["sampleData_id"]}
                for label, column in zip(_labels, _columns):
                    try:
                        if (
                            kwargs["samples"][sample]["hashtag_parameters"][label][k]
                            != "NULL"
                        ):
                            kargs[column] = kwargs["samples"][sample][
                                "hashtag_parameters"
                            ][label][k]
                    except KeyError:
                        pass
                stmt = Query(isinsert=True, table="hashtags", **kargs)
                statements.append([stmt.appropriate_case, kargs])

    # execute all statements
    try:
        for op, kargs in statements:
            db_connect.cur.execute(op, kargs)
            print(db_connect.cur.statement)
        db_connect.db.commit()
    except Exception as e:
        print("ERROR: " + str(e))
        print()
        db_connect.db.rollback()

    return None


def projectdata_sql(kwargs: dict) -> str:
    """\
    A method to insert new records to the database on projects.

    :param kwargs:
        A set of keys and values to be inserted to the database

    :return:
        MySQL statement
    """
    # A set of common expressions to abbreviate
    # Order is important
    abbrv = {
        "Characterization": "Character",
        "Comparison": "Comp",
        "Conditions": "Cond",
        "Number": "Num",
        "Development": "Dev",
        "Differentiation": "Diff",
        "Education": "Edu",
        "Enrichment": "Enrich",
        "Evolution": "Evol",
        "Experimental": "Exp",
        "Experiments": "Exp",
        "Expression": "Expr",
        "Memory": "Mem",
        "Metastasis": "Met",
        "Environmental": "Env",
        "Normal": "Norm",
        "Optimization": "Optim",
        "Population": "Pop",
        "Primary": "Pri",
        "project": "Prj",
        "Regeneration": "Regen",
        "Sequencing": "Seq",
        "SingleCell": "sc",
        "Rna": "RNA",
        "RNASeq": "RNAseq",
        "Crc": "CRC",
        "Tcr": "TCR",
        "Csf": "CSF",
        "Cite": "CITE",
        "CITESeq": "CITEseq",
    }
    # first check if lab exists in the database:
    query = "SELECT `id` FROM lab WHERE PI_name=%(PI_name)s COLLATE utf8mb4_bin"
    db_connect.cur.execute(query, kwargs)
    lab_id = [i[0] for i in db_connect.cur.fetchall()]
    if lab_id:
        lab_id = lab_id[0]
    else:
        # insert new lab details to database
        # first get institute id
        query = "SELECT `id` FROM institute WHERE Institute=%s COLLATE utf8mb4_bin"
        db_connect.cur.execute(query, (kwargs["institute"],))
        res = [i[0] for i in db_connect.cur.fetchall()]
        institute_id = res[0] if res else "NULL"
        department = kwargs["Department"] if "Department" in kwargs else "NULL"
        # instantiate query for INSERT statement for new lab entry
        PI_name = kwargs["PI_name"] if kwargs["PI_name"] else kwargs["PI name"]
        PI_email = kwargs["PI_email"] if kwargs["PI_email"] else kwargs["PI e-mail"]
        kargs = {
            "labName": kwargs["labName"],
            "PI_name": PI_name,
            "PI_email": PI_email,
            "Phone": kwargs["Phone"],
            "Department": department,
            "institution_id": institute_id,
        }
        sql = Query(isinsert=True, table="lab", **kargs)
        db_connect.cur.execute(sql.appropriate_case, kargs)
        db_connect.cur.execute("SELECT LAST_INSERT_ID()")
        lab_id = [i[0] for i in db_connect.cur.fetchall()][0]
        db_connect.db.commit()

    kwargs["lab_id"] = lab_id

    # first check if project exists
    # create trigger in database such that projectShortName is nut null and required
    # before insert
    query = (
        "SELECT `id` FROM project_data WHERE request_id=%s"
        " UNION "
        "SELECT `id` FROM project_data WHERE projectName=%s COLLATE utf8mb4_bin"
    )
    db_connect.cur.execute(
        query, (kwargs["request_id"], kwargs["Provide a short project name"])
    )
    res = db_connect.cur.fetchall()
    if res:
        sys.exit(f"message: project already exists in database:\n'{query}'")

    # Validate project name
    regex = re.compile(r"[\\&$@=;:.+,?}{^%`\]\[<>~#|/]")
    try:
        assert (
            regex.findall(kwargs["Provide a short project name"]) == []
        ), "Validation failed for project Name!"
    except AssertionError as e:
        print(str(e))
        if regex.findall(kwargs["Provide a short project name"]):
            print(
                "Project name has undesired characters:",
                regex.findall(kwargs["Provide a short project name"]),
            )
        sys.exit("Fix the project name and try again.")
    else:
        # generate a project short name
        stop_words = set(stopwords.words("english"))
        tokenizer = nltk.RegexpTokenizer(r"\w+")
        # keep only words
        tokens = tokenizer.tokenize(kwargs["Provide a short project name"].lower())
        # remove stop words
        projShortName = [w for w in tokens if w not in stop_words]
        # reformat and keep only alphanumeric characters
        projShortName = [
            "".join(e for e in string.title() if e.isalnum())
            for string in projShortName
        ]
        projShortName = "".join(projShortName)
        # iterate through common words to abbreviate
        for k, v in abbrv.items():
            projShortName = re.sub(k, v, projShortName)
        confirm = input(
            "Confirm project short name (yes, no): `{}`".format(projShortName)
        )
        if confirm.lower() not in 'yes':
            projShortName = input("Enter project short name: ")

        kwargs["projShortName"] = projShortName

    # insert new project to database
    _columns = [
        "projectName",
        "projectShortName",
        "request_id",
        "project_label",
        "date_created",
        "lab_id",
        "contact_name",
        "contact_email",
    ]
    _labels = [
        "Provide a short project name",
        "projShortName",
        "request_id",
        "Project label",
        "date_created",
        "lab_id",
        "Project contact name",
        "Project contact e-mail",
    ]
    kargs = {}
    for label, column in zip(_labels, _columns):
        try:
            if kwargs[label] != "NULL":
                kargs[column] = kwargs[label]
        except KeyError:
            pass
    Description = []
    if kwargs["Brief summary of project goals"] != "NULL":
        Description.append(kwargs["Brief summary of project goals"])
    if kwargs["Experimental design"] != "NULL":
        Description.append(
            ": ".join(["Experimental design", kwargs["Experimental design"]])
        )
    if Description:
        kargs["Description"] = " |*** ".join(Description)
    notes = []
    for note in ["Other notes or comments:", "Staff notes"]:
        if kwargs[note] != "NULL":
            notes.append(": ".join([note, kwargs[note]]))
    if notes:
        kargs["notes"] = " |*** ".join(notes)

    sql = Query(isinsert=True, table="project_data", **kargs)
    try:
        db_connect.cur.execute(sql.appropriate_case, kargs)
        print(db_connect.cur.statement)
        db_connect.cur.execute("SELECT LAST_INSERT_ID()")
        last_id = [i[0] for i in db_connect.cur.fetchall()]
        kargs = {
            "projectData_id": last_id[0],
            "sample_count": kwargs["Anticipated number of samples"],
        }
        sql = Query(isinsert=True, table="expected_samples", **kargs)
        db_connect.cur.execute(sql.appropriate_case, kargs)
        print(db_connect.cur.statement)

        db_connect.db.commit()
    except Exception as e:
        print("ERROR: " + str(e))
        db_connect.db.rollback()

    return sql.appropriate_case


def statsdata_sql(kwargs: dict) -> None:
    """\
    A method to records library preparation stats of samples.

    :param kwargs:
        A set of keys and values to be inserted to the database

    :return:
        `None`
    """
    statements = []
    _kargs = {}
    query = "SELECT id, Sample FROM sample_data WHERE request_id=%s"
    db_connect.cur.execute(query, (kwargs["request_id"],))
    res = [i for i in db_connect.cur.fetchall()]
    if not res:
        sys.exit(f"message: samples do not exist in database:\n'{query}'")
    [_kargs.update({s: k}) for k, s in res]

    for sample in kwargs["samples"]:
        sc_Tech = kargs_manager[kwargs["Platform"]]
        sc_Tech = kwargs[sc_Tech] if sc_Tech in kwargs else sc_Tech
        hto_Tech = None
        # in the case of Single-cell immune profiling
        if len(sc_Tech.split()) > 1:
            sc_mode = sc_Tech.split()
            sc_Tech = [i for i in sc_mode if i == "10X_5prime"]
            sc_Tech = sc_Tech[0] if sc_Tech else None
            hto_Tech = [i for i in sc_mode if "HashTag" in i]
            hto_Tech = hto_Tech[0] if hto_Tech else None
            tcr_Tech = [i for i in sc_mode if i == "VDJ"]
            tcr_Tech = tcr_Tech[0] if tcr_Tech else None
        if kwargs["nucseq"].lower() == "yes":
            sc_Tech = sc_Tech + "_snRNA-seq"
        # make sure all samples are able to pass the following statement
        try:
            stmt = (
                "UPDATE sample_data SET genomeIndex_id = ("
                "SELECT genome_index.id FROM genome_index "
                "WHERE genome_index.species_id = ("
                "SELECT id FROM species WHERE Species = %(SPECIES)s) "
                "AND genome_index.scTech_id = ("
                "SELECT id FROM sc_tech WHERE sc_Tech = %(SCTECH)s)) "
                "WHERE id = %(SAMPLEDATA_ID)s"
            )
            data_kargs = {
                "SPECIES": kwargs["samples"][sample]["Species"],
                "SCTECH": sc_Tech,
                "SAMPLEDATA_ID": _kargs[sample],
            }
            statements.append([stmt, data_kargs])
        except KeyError as e:
            print("*********** ERROR *************")
            print(
                "ERROR: UPDATE sample_data SET genomeIndex_id = ("
                "SELECT genome_index.id ....... FAILED!\n\t{} ".format(str(e))
            )

        # make update statement for `important_dates`
        # it is assumed that if there are stats then samples were delivered
        # therefore `delivery_date` and `encap_date` will be written to the database
        # it is also assumed that encapsulation happens the same day the samples are
        # delivered. In some cases, samples are frozen then encapsulation happens
        # later on
        kargs = {}
        _columns = ["delivery_date", "encap_date"]
        _labels = ["Expected delivery date", "Encapsulation Date"]
        for label, column in zip(_labels, _columns):
            try:
                if label == "Expected delivery date" and kwargs[label] != "NULL":
                    kargs[column] = parse(kwargs[label]).strftime("%Y-%m-%d")
                if (
                    label == "Encapsulation Date"
                    and kwargs["samples"][sample][label] != "NULL"
                ):
                    kargs[column] = parse(kwargs["samples"][sample][label]).strftime(
                        "%Y-%m-%d"
                    )
            except KeyError:
                pass
        stmt = Query(
            isinsert=False,
            table="important_dates",
            where={"sampleData_id": _kargs[sample]},
            **kargs,
        )
        statements.append([stmt.appropriate_case, kargs])

        # prepare insert statement for stats table
        kwargs["samples"][sample]["sampleIndex_id"] = get_sampleIndex(
            kwargs["samples"][sample]["Index"]
        )
        if kwargs["samples"][sample]["QC"].lower() == "passed":
            kwargs["samples"][sample]["QC"] = 1
            if kwargs["samples"][sample]["sampleIndex_id"] == "NULL":
                sys.exit("ERROR: Missing Sample Index with QC='Passed'!")
        elif kwargs["samples"][sample]["QC"].lower() == "failed":
            kwargs["samples"][sample]["QC"] = 2

        kargs = {
            "sampleData_id": _kargs[sample],
            "n_cells": kwargs["Target cell number"],
        }
        _columns = [
            "sampleIndex_id",
            "QC",
            "lib_vol",
            "lib_conct",
            "lib_mol",
            "lib_qbit",
            "flow_sorted",
            "viability_pct",
            "target_reads",
            "cDNA_yield",
            "notes",
        ]
        _labels = [
            "sampleIndex_id",
            "QC",
            "lib_vol",
            "lib_conct",
            "lib_mo",
            "lib_qbit",
            "Flow Sorted?",
            "Viability %",
            "target_reads",
            "cDNA Yield",
            "Parameters Notes",
        ]
        for label, column in zip(_labels, _columns):
            try:
                if kwargs["samples"][sample][label] != "NULL":
                    kargs[column] = kwargs["samples"][sample][label]
            except KeyError:
                pass
        if (
            all([i in kargs for i in ["sampleIndex_id", "QC"]])
            or str(kargs["QC"]) == "2"
        ):
            stmt = Query(isinsert=True, table="stats_data", **kargs)
            statements.append([stmt.appropriate_case, kargs])
        else:
            stmt_ = Query(isinsert=True, table="stats_data", **kargs)
            print(
                "WARNING: no new data was inserted into `stats_data` table!\n\t{"
                "}".format(stmt_)
            )
            print(kargs)
            print("Missing `QC` and `sampleIndex_id`")

        if "hashtag_parameters" in kwargs["samples"][sample]:
            kwargs["samples"][sample]["hashtag_parameters"][
                "Hash_sampleIndex_id"
            ] = get_sampleIndex(
                kwargs["samples"][sample]["hashtag_parameters"]["Hashtag Index"]
            )

            _columns = ["Sample", "sampleIndex_id", "hash_lib_conct", "notes"]
            _labels = [
                "Appended Name",
                "Hash_sampleIndex_id",
                "Hashtag lib_conct",
                "Hashtag Notes",
            ]
            kargs_ = {"sampleData_id": _kargs[sample]}
            for label, column in zip(_labels, _columns):
                try:
                    if kwargs["samples"][sample]["hashtag_parameters"][label] != "NULL":
                        kargs_[column] = kwargs["samples"][sample][
                            "hashtag_parameters"
                        ][label]
                except KeyError:
                    pass
            kargs_["Sample"] = sample + "_" + kargs_["Sample"]
            stmt = Query(isinsert=True, table="hashtag_lib", **kargs_)
            statements.append([stmt.appropriate_case, kargs_])
            # make sure all samples are able to pass the following statement
            try:
                # in cases other than 5-prime set hto_Tech = sc_Tech + '_HashTag'
                if hto_Tech is None:
                    if (
                        kwargs["samples"][sample]["hashtag_parameters"]["Appended Name"]
                        == "HTO"
                    ):
                        hto_Tech = sc_Tech + "_HashTag"
                    elif (
                        kwargs["samples"][sample]["hashtag_parameters"]["Appended Name"]
                        == "CITE"
                    ):
                        hto_Tech = sc_Tech + "_CiteSeq"
                    else:
                        hto_Tech = "multiome"
                stmt = (
                    "UPDATE hashtag_lib SET genomeIndex_id = ("
                    "SELECT genome_index.id FROM genome_index "
                    "WHERE genome_index.species_id = ("
                    "SELECT id FROM species WHERE Species = %(SPECIES)s) "
                    "AND genome_index.scTech_id = ("
                    "SELECT id FROM sc_tech WHERE sc_Tech = %(HTOTECH)s)) "
                    "WHERE sampleData_id = %(SAMPLEDATA_ID)s"
                )
                data_kargs = {
                    "SPECIES": kwargs["samples"][sample]["Species"],
                    "HTOTECH": hto_Tech,
                    "SAMPLEDATA_ID": _kargs[sample],
                }
                statements.append([stmt, data_kargs])
            except KeyError as e:
                print("*********** ERROR *************")
                print(
                    "ERROR: UPDATE hashtag_lib SET genomeIndex_id = ("
                    "SELECT genome_index.id ....... FAILED!\n\t{} ".format(str(e))
                )

        if "TCR_parameters" in kwargs["samples"][sample]:
            kwargs["samples"][sample]["TCR_parameters"][
                "TCR_sampleIndex_id"
            ] = get_sampleIndex(
                kwargs["samples"][sample]["TCR_parameters"]["TCR Index"]
            )
            _columns = ["Sample", "sampleIndex_id", "TCR_lib_conct", "notes"]
            _labels = [
                "Appended Name",
                "TCR_sampleIndex_id",
                "TCR lib_conct",
                "TCR Notes",
            ]
            kargs_ = {"sampleData_id": _kargs[sample]}
            for label, column in zip(_labels, _columns):
                try:
                    if kwargs["samples"][sample]["TCR_parameters"][label] != "NULL":
                        kargs_[column] = kwargs["samples"][sample]["TCR_parameters"][
                            label
                        ]
                except KeyError:
                    pass
            kargs_["Sample"] = sample + "_" + kargs_["Sample"]
            stmt = Query(isinsert=True, table="TCR_lib", **kargs_)
            statements.append([stmt.appropriate_case, kargs_])
            # make sure all samples are able to pass the following statement
            try:
                stmt = (
                    "UPDATE TCR_lib SET genomeIndex_id = ("
                    "SELECT genome_index.id FROM genome_index "
                    "WHERE genome_index.species_id = ("
                    "SELECT id FROM species WHERE Species = %(SPECIES)s) "
                    "AND genome_index.scTech_id = ("
                    "SELECT id FROM sc_tech WHERE sc_Tech = %(TCRTECH)s)) "
                    "WHERE sampleData_id = %(SAMPLEDATA_ID)s"
                )
                data_kargs = {
                    "SPECIES": kwargs["samples"][sample]["Species"],
                    "TCRTECH": tcr_Tech,
                    "SAMPLEDATA_ID": _kargs[sample],
                }
                statements.append([stmt, data_kargs])
            except KeyError as e:
                print("*********** ERROR *************")
                print(
                    "ERROR: UPDATE TCR_lib SET genomeIndex_id = (SELECT genome_"
                    "index.id ....... FAILED!\n\t{} ".format(str(e))
                )

    # execute all statements
    try:
        for op, kargs in statements:
            db_connect.cur.execute(op, kargs)
            print(db_connect.cur.statement)
        db_connect.db.commit()
    except Exception as e:
        print("ERROR: " + str(e))
        print()
        db_connect.db.rollback()

    return None
