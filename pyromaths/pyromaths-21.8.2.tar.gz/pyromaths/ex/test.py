#!/usr/bin/env python3

# Copyright (C) 2015 -- Louis Paternault (spalax@gresille.org)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""Test of exercises.

This module gather tests from all exercises. Running:

    python3 -m unittest discover

does just as expected.
"""
import codecs
import difflib
import gettext
import glob
import logging
import os
import random
import shutil
import tempfile
import unittest

# Quick and dirty definition of `_` as the identity function
gettext.install('pyromaths')

import pyromaths
from pyromaths.outils import System
from pyromaths.cli import PyromathsException
from pyromaths import directories

# Logging configuration
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger()

def load_tests(*__args, **__kwargs):
    """Return an `unittest.TestSuite` containing tests from all exercises."""
    tests = TestPerformer()
    return tests.as_unittest_suite([
        (exo, tests.get_tested_seeds(exo))
        for exo in tests.iter_names()
        ])

class ExerciseNotFound(PyromathsException):
    """Name of exercise cannot be found in known exercises."""

    def __init__(self, exercise):
        super().__init__()
        self.exercise = exercise

    def __str__(self):
        return "Exercise '{}' not found.".format(self.exercise)

def test_path(name, seed, choice):
    """Return the path of file containing expected test result."""
    return os.path.join(directories.EXODIR, 'tests', "%s.%s.%s" % (name, seed, choice))

class UnittestExercise(unittest.TestCase):
    """Test an exercise, with a particular seed."""

    maxDiff = None

    def __init__(self, exercise=None):
        super().__init__()
        self.exercise = exercise

    def shortDescription(self):
        if self.exercise is None:
            return super().shortDescription()
        else:
            return "{}-{}".format(self.exercise.name(), self.exercise.seed)

    def runTest(self):
        """Perform test"""
        self.assertEqual(
            self.exercise.tex_statement(),
            self.exercise.read_test('statement'),
            )

        self.assertEqual(
            self.exercise.tex_answer(),
            self.exercise.read_test('answer'),
            )

class TestPerformer:
    """Perform tests over every exercises"""

    def __init__(self):
        self.exercises = pyromaths.ex.ExerciseBag()

    def iter_names(self):
        """Iterate over exercise names."""
        return list(self.exercises.keys())

    def get(self, exercise, seed):
        """Return the `TestExercise` object corresponding to the arguments."""
        if exercise not in self.exercises:
            raise KeyError(exercise)
        return self.exercises[exercise](seed)

    def get_tested_seeds(self, exercise):
        """Return seeds that are tested for this exercise"""
        if exercise not in self.exercises:
            raise ExerciseNotFound(exercise)
        statement_seeds = [
            os.path.basename(path).split(".")[1]
            for path in glob.glob(test_path(
                self.exercises[exercise].name(),
                '*',
                'statement'
                ))
            ]
        for seed in statement_seeds:
            if os.path.exists(test_path(
                    self.exercises[exercise].name(),
                    seed,
                    'answer',
                )):
                yield int(seed)

    def iter_missing(self):
        """Iterate over exercises that are not tested."""
        for exercise in self.exercises:
            if not list(self.get_tested_seeds(exercise)):
                yield exercise

    def as_unittest_suite(self, exercises):
        """Return the tests, as a `unittest.TestSuite`."""
        suite = unittest.TestSuite()
        for exercise, seeds in exercises:
            for seed in seeds:
                suite.addTest(UnittestExercise(exercise=self.get(exercise, seed)))
        return suite
