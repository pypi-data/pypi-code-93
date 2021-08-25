# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import filecmp
import shutil
import uuid
import coveriteam.util as util
from pathlib import Path
import os
from benchexec.result import get_result_classification

VERDICT_TRUE = "TRUE"
VERDICT_FALSE = "FALSE"
VERDICT_UNKNOWN = "UNKNOWN"
VERDICT_ERROR = "ERROR"
VERDICT_TIMEOUT = "TIMEOUT"


class Artifact:
    def __init__(self, path: str):
        if path:
            self.path = str(Path(path).resolve())
        else:
            self.path = ""

    def __str__(self):
        return os.path.relpath(self.path, os.getcwd()) if self.path else ""

    def __repr__(self):
        return "'%s'" % os.path.relpath(self.path, os.getcwd()) if self.path else ""


class Joinable:
    def join(self, artifact2):
        """
        Definition of this function is to be provided by the child class.
        """
        pass


class BehaviorDescription(Artifact):
    pass


class Justification(Artifact):
    pass


class Verdict(Artifact):
    def __init__(self, verdict: str):
        self.verdict = verdict
        self.path = ""

    def __str__(self):
        return self.verdict

    def __repr__(self):
        return "'%s'" % self.verdict

    def __eq__(self, other):
        # Compare only true or false. We can see later if we need to compare the actual string.
        return get_result_classification(self.verdict) == get_result_classification(
            other
        )


class Specification(Artifact):
    pass


class Program(BehaviorDescription):
    # TODO move it to artifact at some point
    def __init__(self, path):
        self.multipath = False
        if not path:
            self.path = ""
        elif not isinstance(path, str) and isinstance(path, list):
            self.path = [str(Path(p).resolve()) for p in path]
            self.multipath = True
        else:
            self.path = str(Path(path).resolve())

    def __str__(self):
        if self.multipath:
            return str(
                [os.path.relpath(p, os.getcwd()) if p else "" for p in self.path]
            )
        return super().__str__()

    def __repr__(self):
        if self.multipath:
            return str(
                [
                    "'%s'" % os.path.relpath(p, os.getcwd()) if p else ""
                    for p in self.path
                ]
            )
        return super().__repr__()


class CProgram(Program):
    pass


class JavaProgram(Program):
    pass


class BehaviorSpecification(Specification):
    pass


class TestSpecification(Specification):
    pass


class Witness(Justification):
    pass


class ReachabilityWitness(Witness):
    pass


class Condition(Justification):
    pass


class TestGoal(Condition, Joinable):
    def join(self, other):
        assert type(self) is type(
            other
        ), "Cannot join %r and %r. Types are not same." % (self, other)
        if not self.path:
            return TestGoal(other.path)
        elif other.path:
            # If files are same then no need to compare
            if filecmp.cmp(self.path, other.path, False):
                return self
            joined = Path(self.path).parent / str(uuid.uuid4())
            with joined.open("w") as f:
                with open(self.path) as f1:
                    f.write(f1.read())
                with open(other.path) as f1:
                    f.write(f1.read())
            return TestGoal(joined)
        # When other does not exist
        return self

    def __eq__(self, other):
        if isinstance(other, TestGoal):
            if self.path and other.path:
                return filecmp.cmp(self.path, other.path, False)
            elif not (self.path or other.path):
                return True
            else:
                return False
        else:
            return False


class TestSuite(Justification):
    def join(self, other):
        assert type(self) is type(
            other
        ), "Cannot join %r and %r. Types are not same." % (self, other)
        if not self.path:
            self.path = other.path
        elif other.path:
            shutil.copytree(other.path, str(Path(self.path) / str(uuid.uuid4())))
        return self


class AtomicActorDefinition(Artifact):
    def __init__(self, actordef):
        self.actordef = actordef
        # Assumption: There should be a file present with the same name in our actor configs.
        if util.ACTOR_CONFIG_PATH:
            actordef_path = Path(util.ACTOR_CONFIG_PATH) / actordef / ".yml"
        else:
            this_path = Path(__file__).resolve()
            actordef_path = (
                this_path.parent.parent.parent / "actors" / (actordef + ".yml")
            )

        if actordef_path.exists():
            self.path = str(actordef_path)
        else:
            raise Exception("Actor %r could not be found!!" % actordef)

    def __str__(self):
        return self.actordef
