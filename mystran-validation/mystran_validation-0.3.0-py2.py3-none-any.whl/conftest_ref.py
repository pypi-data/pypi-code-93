# content of conftest.py
import ast
import configparser
import numbers
import os
import shlex
import shutil
import subprocess
import traceback
from pathlib import Path

import pandas as pd
import pytest
from femap_neutral_parser import Parser as NeuParser

from mystran_validation import assert_frame_equal
from mystran_validation.parsers import subset
from mystran_validation.parsers.nastran_op2 import Parser as OP2Parser


def pytest_collect_file(parent, path):
    _path = Path(path)
    if _path.suffix == ".ini" and _path.name.startswith("test"):
        return IniTestFile.from_parent(parent, fspath=path)


class IniTestFile(pytest.File):
    bulkfile = None
    rootdir = None
    rootname = None
    mystran_run_status = {}
    reference = {}
    op2s = {}

    def collect(self):
        config = configparser.ConfigParser()
        config.read(self.fspath)
        # ---------------------------------------------------------------------
        # prepare paths
        self.rootdir = Path(self.fspath).parent
        self.rootname = Path(self.fspath).stem
        # ---------------------------------------------------------------------
        # clean working dir
        wdir = self.rootdir / (".out_" + self.rootname)
        try:
            wdir.mkdir()
        except FileExistsError:
            shutil.rmtree(wdir)
            wdir.mkdir()
        for name in config.sections():
            spec = dict(config[name].items())
            bulkfile = self.rootdir / spec["bulk"]
            if self.bulkfile:
                if bulkfile != self.bulkfile:
                    raise ValueError(f"{name}: One class, one bulk!")
            spec["workingdir"] = wdir
            spec["bulk"] = bulkfile
            ref = spec["reference"]
            # -----------------------------------------------------------------
            # if ref is obviously a file
            if Path(ref).suffix.lower() in (".op2", ".neu"):
                spec["reference"] = self.rootdir / spec["reference"]
            # -----------------------------------------------------------------
            # if ref a sing value
            else:
                ref = float(ref)
                spec["reference"] = ref
            spec["output"] = spec["workingdir"] / (bulkfile.stem + ".NEU")
            spec["rtol"] = float(spec.get("rtol", 1e-05))
            spec["atol"] = float(spec.get("atol", 1e-08))
            yield IniItem.from_parent(self, name=name, spec=spec)


class IniItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec
        # ---------------------------------------------------------------------
        # run Mystran only once
        if spec["bulk"] not in self.parent.mystran_run_status:
            # first test for this class, a few things to set up
            self.parent.mystran_run_status[spec["bulk"]] = self.run_mystran()
        # ---------------------------------------------------------------------
        # process OP2
        ref = self.spec["reference"]
        if not isinstance(ref, numbers.Number):
            if ref.suffix.lower() == ".op2" and str(ref) not in self.parent.op2s:
                self.parent.op2s[ref] = OP2Parser(str(self.spec["reference"]))
            self.op2 = self.parent.op2s[ref]  # shortcut for self
        else:
            self.op2 = None
        self.user_properties += [("ref", self.op2)]
        self.user_properties += [("description", self.spec["description"])]
        self.user_properties += [("atol", self.spec["atol"])]
        self.user_properties += [("rtol", self.spec["rtol"])]

    def run_mystran(self):
        # =====================================================================
        # run bulkfile
        # =====================================================================

        target = shutil.copy(self.spec["bulk"], self.spec["workingdir"])
        cmd = f"{os.getenv('_MYSTRAN_BIN')} {target}"
        status = subprocess.run(shlex.split(cmd))
        # ---------------------------------------------------------------------
        # get actual results
        neu = NeuParser(self.spec["output"], autotranslate=False)
        self.parent.actual = neu
        self.parent.actual.info(doprint=False)  # pre-digest data
        self.parent.actual_available_vectors = sorted(
            self.parent.actual.output_vectors.keys()
        )
        return status

    def expected(self, vector, filters=None, axis=None, raw=False):
        if not filters:
            filters = {}
        df_expected = None
        # ---------------------------------------------------------------------
        # reference is a numerical value
        if isinstance(self.spec["reference"], numbers.Number):
            if axis is None:
                raise ValueError("param `axis` must be specified for manual checking")
            _data = filters.copy()
            _data.update({axis: [self.spec["reference"]]})
            df_expected = pd.DataFrame(_data)
            df_expected.set_index(list(filters.keys()), inplace=True)
            df_expected = df_expected[axis].to_frame()
        # ---------------------------------------------------------------------
        # reference is a ref file
        elif self.spec["reference"].suffix.lower() == ".op2":
            op2 = self.parent.op2s[self.spec["reference"]]
            df_expected = op2.get_vector(vector=vector, raw=raw, **filters)
        else:
            raise ValueError("reference {self.spec['reference']} not understood")
        return df_expected

    def actual(self, vector, filters=None, axis=None, raw=False):
        if not filters:
            filters = {}
        # -----------------------------------------------------------------
        # get values from neutral file, and reshape it
        df_actual = pd.DataFrame(getattr(self.parent.actual, f"get_{vector}")(raw=raw))
        if not raw:
            if "NodeID" in df_actual and "ElementID" not in df_actual:
                df_actual.set_index(["SubcaseID", "NodeID"], inplace=True)
            elif "ElementID" in df_actual and "NodeID" not in df_actual:
                df_actual.set_index(["SubcaseID", "ElementID"], inplace=True)
            else:
                raise ValueError("cannot get values")
            df_actual.sort_index(inplace=True)
            df_actual = subset(df_actual, **filters)
            if axis:
                try:
                    df_actual = df_actual[axis].to_frame()
                except KeyError:
                    msg = f"{axis} is not a proper column. Use one of {df_actual.columns.tolist()}"
                    raise KeyError(msg)
        return df_actual

    def runtest(self):
        if self.spec.get("skip"):
            pytest.skip(self.spec["skip"])
        try:
            vector = self.spec["vector"]
            # ---------------------------------------------------------------------
            # get subset index
            filters = dict(
                SubcaseID=ast.literal_eval(self.spec.get("subcaseids", "None")),
                NodeID=ast.literal_eval(self.spec.get("nodeids", "None")),
                ElementID=ast.literal_eval(self.spec.get("elementids", "None")),
            )
            axis = self.spec.get("axis")
            filters = {k: [v] for k, v in filters.items() if v}
            # ---------------------------------------------------------------------
            # get dataframes to compare
            df_actual = self.actual(vector, filters, axis)
            df_expected = self.expected(vector, filters, axis)
            # -----------------------------------------------------------------
            # check tolerances
            rtol = self.spec["rtol"]
            atol = self.spec["atol"]
            failures, aerr, rerr = assert_frame_equal(
                df_actual, df_expected, rtol=rtol, atol=atol
            )
        except Exception as exc:
            tb = traceback.format_exc()
            raise GenericException(self, exc, tb)
        else:
            if len(failures) > 0:
                raise IniException(
                    self, df_actual, df_expected, failures, rtol, atol, aerr, rerr
                )

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""
        if isinstance(excinfo.value, IniException):
            (
                item,
                df_actual,
                df_expected,
                failures,
                rtol,
                atol,
                aerr,
                rerr,
            ) = excinfo.value.args
            df_actual = df_actual.loc[failures.index]
            df_expected = df_expected.loc[failures.index]
            # failing difference
            return "\n".join(
                [
                    f"usecase `{self.fspath}::[{self.name}]`\nexecution failed given precision requirements:\n  * {atol=}\n  * {rtol=}\n",
                    f"failing with:\n  * Absolute difference {aerr=}\n  * Relative difference {rerr=}\n",
                    f"Expected\n--------\n{df_expected}\n",
                    f"Actual\n------\n{df_actual}",
                ]
            )
        elif isinstance(excinfo.value, GenericException):
            item, exc, traceback = excinfo.value.args
            return "\n".join(
                [
                    f"usecase `{self.fspath}::[{self.name}]` raised the following exception\n",
                    f"{exc}\n",
                    f"file: {traceback}",  # get rid of "file " prefix
                ]
            )

    def reportinfo(self):
        return self.fspath, 0, f"usecase: {self.name}"


class IniException(Exception):
    pass


class GenericException(Exception):
    pass
