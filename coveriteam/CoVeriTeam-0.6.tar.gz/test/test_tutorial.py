# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import os
import coveriteam.util as util
from nose.tools import nottest
import pathlib
import sys

script = pathlib.Path(__file__).resolve()
project_dir = script.parent
lib_dir = project_dir.parent / "lib"
for wheel in lib_dir.glob("*.whl"):
    sys.path.insert(0, str(wheel))
sys.path.insert(0, str(project_dir))

from coveriteam.coveriteam import CoVeriTeam


def setup_module():
    os.chdir("examples")
    util.set_cache_directories()


def teardown_module():
    os.chdir("..")


def test_tutorial_verifier():
    inputs = ["verifier.cvt"]
    inputs += ["--input", "verifier_path=../actors/cpa-seq.yml"]
    inputs += ["--input", "program_path=c/Problem02_label16.c"]
    inputs += ["--input", "specification_path=properties/unreach-call.prp"]
    inputs += ["--data-model", "ILP32"]
    CoVeriTeam().start(inputs)


def test_tutorial_validating_verifier():
    inputs = ["validating-verifier.cvt"]
    inputs += ["--input", "program_path=c/Problem02_label16.c"]
    inputs += ["--input", "specification_path=properties/unreach-call.prp"]
    inputs += [
        "--input",
        "validator_path=../actors/cpa-validate-violation-witnesses.yml",
    ]
    inputs += ["--input", "verifier_path=../actors/uautomizer.yml"]
    inputs += ["--data-model", "ILP32"]
    CoVeriTeam().start(inputs)


def test_execution_based_validation():
    inputs = ["execution-based-validation.cvt"]
    inputs += ["--input", "prog_path=c/Problem01_label15.c"]
    inputs += ["--input", "spec_path=properties/unreach-call.prp"]
    inputs += [
        "--input",
        "witness_path=witnesses/Problem01_label15_reach_safety.graphml",
    ]
    inputs += ["--data-model", "ILP32"]
    CoVeriTeam().start(inputs)


@nottest
def test_execution_based_validation_witness_instrument():
    inputs = ["exe-validator-witness-instrument.cvt"]
    inputs += ["--input", "prog_path=c/gcnr2008.i"]
    inputs += ["--input", "spec_path=properties/unreach-call.prp"]
    inputs += ["--input", "witness_path=witnesses/gcnr2008_violation_witness.graphml"]
    inputs += ["--data-model", "ILP32"]
    CoVeriTeam().start(inputs)


def test_cmc_reducer():
    inputs = ["cmc-reducer.cvt"]
    inputs += ["--input", "prog_path=c/slicingReducer-example.c"]
    inputs += ["--input", "spec_path=properties/unreach-call.prp"]
    inputs += ["--input", "cond_path=c/slicingCondition.txt"]
    inputs += ["--data-model", "ILP32"]
    CoVeriTeam().start(inputs)


def test_condtest():
    inputs = ["condtest.cvt"]
    inputs += ["--gen-code"]
    inputs += ["--input", "prog_path=c/test.c"]
    inputs += ["--input", "spec_path=properties/coverage-branches.prp"]
    inputs += ["--input", "tester_yml=../actors/klee.yml"]
    inputs += ["--data-model", "ILP32"]
    CoVeriTeam().start(inputs)


def test_verifier_based_tester():
    inputs = ["verifier-based-tester.cvt"]
    inputs += ["--input", "prog_path=c/CostasArray-10.c"]
    inputs += ["--input", "spec_path=properties/unreach-call.prp"]
    inputs += ["--data-model", "ILP32"]
    CoVeriTeam().start(inputs)


def test_repeat_condtest():
    inputs = ["repeat-condtest.cvt"]
    inputs += ["--input", "prog_path=c/Problem01_label15.c"]
    inputs += ["--input", "spec_path=properties/coverage-branches.prp"]
    inputs += ["--data-model", "ILP32"]
    CoVeriTeam().start(inputs)


def test_metaval():
    inputs = ["metaval.cvt"]
    inputs += ["--input", "prog_path=c/ConversionToSignedInt.i"]
    inputs += ["--input", "spec_path=properties/no-overflow.prp"]
    inputs += [
        "--input",
        "witness_path=witnesses/ConversionToSignedInt_nooverflow_witness.graphml",
    ]
    inputs += ["--data-model", "ILP32"]
    CoVeriTeam().start(inputs)
