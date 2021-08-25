#!/usr/bin/env python3

"""\
html parser for sample forms and project initiation forms
"""

import re
import sys

import pandas as pd
import regex
from bs4 import BeautifulSoup
from dateutil.parser import parse
from lxml.html.clean import Cleaner


class ParseHtml:
    """\
    HTML parser that returns clean parameters and data extracted from *iLabs*
    submitted forms.
    """

    def __init__(self, func):
        self.func = func
        self.kargs = {}
        self.soup = str
        self.idx = None
        self.index = "Sample Name"

    def __call__(self, *args):

        new_html = self.func(*args)
        self.soup = BeautifulSoup(new_html, "html.parser")

    def reset(self):
        self.__init__(self.func)

    def get_tags(
        self,
        tag_name: str = None,
        tag_text: str = None,
        label_text: str = None,
    ) -> None:
        try:
            tag = self.soup.find_all(tag_name, text=tag_text)[0]
            tag = tag.findNext()
            while tag.name != tag_name:
                if tag.name == "label":
                    if tag_text == "Project label":
                        self.kargs["Project label"] = tag.text.strip()
                    else:
                        if tag.text.strip() != label_text:
                            self.kargs[tag_text] = tag.text.strip()
                tag = tag.findNext()
        except (KeyError, IndexError, AttributeError):
            pass

        return None

    def get_general_attrs(self, **labels) -> None:

        self.soup.a.decompose()
        request_id = self.soup.h2.string.strip().split()[0]
        date_created = self.soup.find(text=regex.compile("Created")).strip()
        date_created = re.search(r"(?<=Created: ).*", date_created).group()
        date_created = parse(date_created).strftime("%Y-%m-%d")
        if self.soup.find("td", string="Lab Name:"):
            self.kargs["labName"] = self.soup.a.text
        if self.soup.find("td", string="Customer institute:"):
            self.kargs["institute"] = (
                self.soup.find(
                    "td",
                    string="Customer institute:",
                )
                .findNextSibling()
                .get_text()
            )
            labinfo = (
                self.soup.find("td", string="Lab PI(s):").findNextSibling().get_text()
            ).strip()
            self.kargs["PI_name"] = re.match(r"\A.+?(?=:)", labinfo).group()
            self.kargs["PI_email"] = re.search(
                r"[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+", labinfo
            ).group()
            phone = (
                re.search(r"(?<=Phone: ).*", labinfo).group()
                if re.search(r"(?<=Phone: ).*", labinfo)
                else ""
            )
            self.kargs["Phone"] = phone if phone else "NULL"
        self.kargs["request_id"] = request_id
        self.kargs["date_created"] = date_created

        # This bloc will capture sample type label and every other label with values.
        # labels without values will be set to NULL
        # New sample type specified will be set as well if found
        stype = ""
        for tag in self.soup.find_all("label"):
            if tag.text.strip() in labels:
                if tag.text.strip() == "Sample type":
                    stype = tag.findNext().text.strip()
                elif tag.text.strip() in labels and tag.findNext().text.strip() in list(
                    labels
                ) + [""]:
                    self.kargs[labels[tag.text.strip()]] = "NULL"
                else:
                    self.kargs[labels[tag.text.strip()]] = tag.findNext().text.strip()
        for tag in self.soup.find_all("label"):
            if tag.text.strip() == "Specify new sample type":
                if tag.findNext().text.strip() in ["Specify new sample type", ""]:
                    pass
                else:
                    stype = tag.findNext().text.strip()

        self.kargs["Sample type"] = stype

        # get rid of none checked radio buttons and checkboxes
        for i in self.soup.find_all("input", attrs={"checked": False}):
            try:
                i.parent.decompose()
            except AttributeError:
                pass

        try:
            tag = self.soup.find_all("font", text="Choose Kit")[0]
            tag = tag.findNext()
            while tag.name != "font":
                if tag.name == "label":
                    if tag.text.strip() != "Problems":
                        if "Choose Kit" in self.kargs:
                            self.kargs["Choose Kit"].append(tag.text.strip())
                        else:
                            self.kargs["Choose Kit"] = [tag.text.strip()]
                tag = tag.findNext()
            self.kargs["Choose Kit"] = " ".join(self.kargs["Choose Kit"])
        except (KeyError, IndexError):
            pass

        try:
            tag = self.soup.find_all("font", text="Problems")[0]
            tag = tag.findNext()
            while tag.name != "font":
                if tag.name == "label":
                    if tag.text.strip() != "Staff notes or comments":
                        if "Problems" in self.kargs:
                            self.kargs["Problems"].append(tag.text.strip())
                        else:
                            self.kargs["Problems"] = [tag.text.strip()]
                tag = tag.findNext()
            self.kargs["Problems"] = "; ".join(self.kargs["Problems"])
        except (KeyError, IndexError):
            pass

        self.get_tags(tag_name="font", tag_text="Choose 10X Kit", label_text="Problems")
        self.get_tags(
            tag_name="font", tag_text="Choose InDrop Version", label_text="Problems"
        )
        self.get_tags(
            tag_name="font",
            tag_text="Other notes or comments:",
            label_text="Staff notes",
        )
        self.get_tags(
            tag_name="font", tag_text="Staff notes", label_text="Project label"
        )
        self.get_tags(tag_name="font", tag_text="Project label")

        return None

    def get_library_prep_parameters(
        self,
        label: str = None,
        key: str = None,
    ) -> None:

        for tag in self.soup.find_all("label"):
            if tag.text.strip() == label:
                converter = {"Sample Name": lambda x: str(x)}
                parameters = pd.read_html(
                    repr(tag.find_next("table")), index_col=0, converters=converter
                )[0]
                parameters = parameters.dropna(how="all")
                # get rid of spaces in sample name
                parameters.loc[:, self.index] = parameters[self.index].replace(
                    to_replace=r" ", value="_", regex=True
                )
                parameters = parameters.set_index(self.index)
                if parameters.empty:
                    pass
                else:
                    try:
                        assert not bool(
                            parameters.index.difference(self.idx).values.any()
                        ), (
                            "sample names don't match in {} "
                            "table compared to samples table".format(label)
                        )
                    except (KeyError, AssertionError) as e:
                        print("ERROR: index = ", self.index)
                        print(
                            pd.DataFrame(
                                {
                                    label: pd.Series(parameters.index),
                                    "sample_names": pd.Series(self.idx),
                                }
                            )
                        )
                        print(str(e))
                        sys.exit("ERROR:\n" + str(e))

                    t = parameters.to_dict(orient="index")
                    for k, v in t.items():
                        if key is None:
                            self.kargs["samples"][k].update(v)
                        elif key in self.kargs["samples"][k]:
                            self.kargs["samples"][k][key].update(v)
                        else:
                            self.kargs["samples"][k][key] = v

        return None

    def get_tables(self) -> None:

        # collect samples
        for tag in self.soup.find_all("label"):
            if tag.text.strip() == "Upload samples from Excel?":
                converter = {"Sample Name": lambda x: str(x)}
                samples_table = pd.read_html(
                    repr(tag.find_next("table")), index_col=0, converters=converter
                )[0]
                samples_table = samples_table.dropna(how="all")
                # Important: get rid of spaces in sample name, since sample name is
                # used to construct prefix for seqc outputs
                samples_table.loc[:, self.index] = samples_table[self.index].replace(
                    to_replace=r" ", value="_", regex=True
                )
                samples_table = samples_table.set_index(self.index)
                # establish indexed sample names to test for discrepancies
                self.idx = samples_table.index
                try:
                    assert (
                        not self.idx.empty
                    ), "Missing sample data! Check the form for Sample data integrity."
                except AssertionError as e:
                    print(str(e))
                    sys.exit("ERROR:\n" + str(e))

                self.kargs["samples"] = samples_table.to_dict(orient="index")

        # collect library prep parameters
        self.get_library_prep_parameters(label="Sample parameters")

        # collect feature barcodes if any
        for tag in self.soup.find_all("label"):
            if "barcodes used" in tag.text.strip():
                converters = {i: str for i in range(5)}
                barcodes_table = pd.read_html(
                    str(tag.find_next("table")), index_col=0, converters=converters
                )[0]
                barcodes_table = barcodes_table.dropna(how="all")
                barcodes_table.columns = [
                    "hlabels",
                    "hashtags",
                    "barcodes",
                    "Sample_Name",
                    "hashtag_notes",
                ]
                try:
                    assert not barcodes_table.empty, (
                        "Missing barcode data! Check the form for barcode data "
                        "integrity."
                    )
                except AssertionError as e:
                    print(str(e))
                    sys.exit("ERROR:\n" + str(e))

                # attach barcodes to samples
                if barcodes_table.iloc[:, 3].dropna().empty:
                    barcodes_table = barcodes_table.iloc[:, [0, 1, 2, 4]]
                    for sample in self.kargs["samples"]:
                        self.kargs["samples"][sample][
                            "hashtag_parameters"
                        ] = barcodes_table.to_dict()
                else:
                    barcodes_table.iloc[:, 3] = barcodes_table.iloc[:, 3].replace(
                        to_replace=r" ", value="_", regex=True
                    )
                    for sample in self.kargs["samples"]:
                        t1 = barcodes_table[barcodes_table.iloc[:, 3] == sample].iloc[
                            :, [0, 1, 2, 4]
                        ]
                        if not t1.empty:
                            self.kargs["samples"][sample][
                                "hashtag_parameters"
                            ] = t1.to_dict()

        # collect hashtags prep parameters
        self.get_library_prep_parameters(
            label="Hashtag parameters",
            key="hashtag_parameters",
        )

        # collect TCR prep parameters
        self.get_library_prep_parameters(
            label="TCR parameters",
            key="TCR_parameters",
        )

        return None


@ParseHtml
def cleanhtml(html: str = "", kill_tags: list = ["span"]) -> str:
    """\
    HTML parser that returns clean parameters and data extracted from *iLabs*
    submitted forms.

    :type html: str
    :type kill_tags: list

    :param html:
        Input HTML
    :param kill_tags:
        HTML tags to be cleaned and removed

    :rtype: str
    :return:
        Cleaned html string

    Example
    -------

    >>> from SCRIdb.htmlparser import cleanhtml
    >>> cleanhtml("<p>Some<b>bad<i>HTML")
    """
    cleaner = Cleaner(
        style=True,
        links=True,
        add_nofollow=True,
        javascript=True,
        meta=True,
        page_structure=True,
        kill_tags=kill_tags,
        processing_instructions=True,
        embedded=True,
        frames=True,
        forms=False,
    )
    new_html = cleaner.clean_html(html)

    return new_html
