#!/usr/bin/env python3

"""\
Submit new projects and samples
"""
import os
import sys

from . import sql
from .htmlparser import cleanhtml
from .query import db_connect


def data_sql(project: bool = False,):
    """\

    :param project
        Switch to project parser

    :return:
        `SCRIdb.sql` object
    """
    if project:
        return sql.projectdata_sql
    else:
        return sql.sampledata_sql


def data_submission_main(fn: str, mode: list, proj: bool = False,) -> None:
    """\
    A method that reads HTML data and submits new records into the database.

    :param fn:
        Input path to HTML, or HTML string
    :param mode:
        Action mode to submit new data and/or submit library preparation parameters.
        Choices are: submitnew, or stats, or both.
    :param proj:
        Project submission

    :return:
        `None`

    Example
    -------

    >>> from SCRIdb.submission import *
    >>> fn = "<p>Some<b>bad<i>HTML"
    >>> data_submission_main(fn=fn, mode=['submitnew'])

    """
    if os.path.isfile(fn):
        if os.path.splitext(fn)[1] != ".html":
            sys.exit("ERROR: Input file not `HTML` format!")
        with open(fn, "r") as f:
            html = f.read()
    elif isinstance(fn, str) and fn != "-":
        html = fn
    else:
        sys.exit("ERROR: Missing input! Try again...")

    cleanhtml(html)

    # Determine if `project intake form`
    if "Begin a new project" in html:
        proj = True
        print("Switching to `Project Intake Form` mode!")

    labels = {
        "Expected delivery date": "Expected delivery date",
        "Project Intake service ID": "proj_request_id",
        "Platform": "Platform",
        "Sequencing nuclei (Nuc-seq)?": "nucseq",
        "Sample type": "Sample type",
        "Target cell number": "Target cell number",
        "Notes or comments": "Notes or comments",
        "Staff notes or comments": "Staff notes or comments",
        "Provide a short project name": "Provide a short project name",
        "Department": "Department",
        "Project contact name": "Project contact name",
        "Project contact e-mail": "Project contact e-mail",
        "Brief summary of project goals": "Brief summary of project goals",
        "Experimental design": "Experimental design",
        "Anticipated number of samples": "Anticipated number of samples",
        "Other notes or comments:": "Other notes or comments:",
        "Staff notes": "Staff notes",
    }
    cleanhtml.get_general_attrs(**labels)
    cleanhtml.get_tables()
    cleanhtml.kargs = sql.sqlargs(cleanhtml.kargs)

    if "submitnew" in mode:
        print("Submitting new data to the database ...")
        func_sql = data_sql(proj)
        func_sql(cleanhtml.kargs)

    if not proj and "stats" in mode:
        print("Updating data on `stats_data` table ...")
        sql.statsdata_sql(cleanhtml.kargs)

    db_connect.db.disconnect()

    return None
