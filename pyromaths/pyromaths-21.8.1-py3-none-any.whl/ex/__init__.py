#!/usr/bin/env python3

import codecs
import collections
import difflib
import importlib
import inspect
import logging
import operator
import os
import pkgutil
import random
import shutil
import subprocess
import sys
import tempfile
import types

from ..outils import jinja2tex
from .test import test_path
from ..outils.System import Fiche
from .. import directories

class TexExercise:
    """Exercise with TeX support."""

    def __init__(self, seed=None):
        if seed is None:
            self.seed = random.randint(0, sys.maxsize)
        else:
            self.seed = seed
        random.seed(self.seed)

    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def description(cls):
        return cls.__doc__.splitlines()[0]

    @classmethod
    def thumb(cls):
        return os.path.join(directories.EXODIR, 'img', "%s.png" % cls.name())

    def tex_statement(self):
        """Return problem statement in TeX format."""
        raise NotImplementedError()

    def tex_answer(self):
        """Return full answer in TeX format."""
        raise NotImplementedError()

    ################################################################################
    # Tests

    def show(self, *, dir=None):
        """Generate exercise, and display its result."""
        subprocess.run(["gio", "open", self.generate(dir=dir)])

    def generate(self, *, enonce=True, corrige=True, dir=None):
        """Generate a single exercise.

        Return the pdf name.
        """
        parametres = {
            'enonce': enonce,
            'corrige': corrige,
            'exercices': [self],
            }
        output = os.path.join(
            tempfile.mkdtemp(dir=dir),
            "{}-{}.pdf".format(self.name(), self.seed),
            )
        with Fiche(parametres) as fiche:
            fiche.write_pdf()
            shutil.copy(fiche.pdfname, output)
        return output

    def test_path(self, name):
        """Return the path of the file containing expected results."""
        return test_path(
            self.name(),
            self.seed,
            name,
            )

    def write_test(self):
        """Write expected test results."""
        with codecs.open(self.test_path("statement"), "w", "utf8") as statement:
            statement.write(self.tex_statement())
        with codecs.open(self.test_path("answer"), "w", "utf8") as answer:
            answer.write(self.tex_answer())

    def read_test(self, choice):
        """Read expected test result."""
        with codecs.open(self.test_path(choice), "r", "utf8") as result:
            return result.read()

    def changed(self):
        """Return `True` iff exercise has changed."""
        if self.tex_statement() != self.read_test('statement'):
            return True
        if self.tex_answer() != self.read_test('answer'):
            return True
        return False

    def print_diff(self):
        """Print the diff between old and new test."""
        if self.tex_statement() != self.read_test('statement'):
            print("Statement:")
            for line in difflib.unified_diff(
                    self.read_test('statement').splitlines(),
                    self.tex_statement().splitlines(),
                    fromfile='Old statement',
                    tofile='New statement',
                    ):
                print(line)
        if self.tex_answer() != self.read_test('answer'):
            print("Answer:")
            for line in difflib.unified_diff(
                    self.read_test('answer').splitlines(),
                    self.tex_answer().splitlines(),
                    fromfile='Old answer',
                    tofile='New answer',
                    ):
                print(line)

class LegacyExercise(TexExercise):
    """Base class for legacy format exercise proxies.

    This class is deprecated. Do not use it to write new exercises.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stat, self.ans = self.__class__.function()

    def tex_statement(self):
        return "\n".join(self.stat)

    def tex_answer(self):
        return "\n".join(self.ans)

def __import(name=__name__, parent=None):
    ''' Import 'name' from 'parent' package. '''
    if not isinstance(name, str):
        name = name.__name__
    # parent is None: assume 'name' is a package name
    # hack tout moche pour l'import des exercices dans la version Windows de Pyromaths :
    # Les modules sixiemes, quatriemes doivent être appelés avec le chemin complet,
    # alors que les exercices cinquiemes.aires ne doivent être appelés qu'ainsi.
    if "." not in name and hasattr(sys, "frozen"): name = "pyromaths.ex." + name
    if parent is None: parent = name
    elif not isinstance(parent, str):
        # assume 'parent' is a package instance
        parent = parent.__name__
    return importlib.import_module(name)
    # return __import__(name, fromlist=parent)

def _iter_pkg_exercises(pkg):
    ''' List exercises in 'pkg' modules. '''
    # level defaults to description, then unknown
    if 'level' not in dir(pkg): pkg.level = "Inconnu"
    for _, name, ispkg in pkgutil.iter_modules(pkg.__path__, pkg.__name__ + '.'):
        # skip packages
        if ispkg: continue;
        # import module
        mod = __import(name, pkg)
        # search exercises in module
        for name in dir(mod):
            cls = getattr(mod, name)
            if name.startswith("_"):
                continue
            if not isinstance(cls, type):
                continue
            if not issubclass(cls, TexExercise):
                continue
            if cls.__module__ == "pyromaths.ex":
                continue
            yield cls

def _subpackages(pkg):
    ''' List 'pkg' sub-packages. '''
    for _, name, ispkg in pkgutil.iter_modules(pkg.__path__, pkg.__name__ + '.'):
        # skip modules
        if not ispkg: continue;
        yield __import(name, pkg)

def _iter_exercises(pkg=None):
    """Iterator over existing exercises"""
    if pkg is None:
        pkg = __import()
    yield from _iter_pkg_exercises(pkg)

    # load sub-packages
    for sub in _subpackages(pkg):
        yield from _iter_exercises(sub)

NIVEAUX = [
    "Sixième",
    "Cinquième",
    "Quatrième",
    "Troisième",
    "Seconde",
    "1re Spé math",
    "Term STMG",
    "Term Spé math",
    # "exemple",
    ]

class ExerciseBag(collections.UserDict):
    """Classe regroupant tous les exercices.

    Cette classe est la sous-classe d'un dictionnaire :
    - clef: le nom (:type:`str`) des exercices ;
    - valeur: l'exercice (:type:`TexExercise`).

    Des méthodes permettent d'accéder à ces exercices avec d'autres présentations.
    """

    def __init__(self, *, exercises=None):
        super().__init__()
        if exercises is None:
            iterable = _iter_exercises()
        else:
            iterable = exercises
        for exo in iterable:
            if exo.name() in self:
                logging.error(
                    "Deux exercices portent le même nom '%s': %s et %s.",
                    exo.name(),
                    exo,
                    self[exo.name()],
                    )
            self[exo.name()] = exo

    def dict_levels(self):
        """Renvoit les exercices, comme un dictionnaire classé par niveau.

        - clefs: les niveaux ;
        - valeurs: l'ensemble des exercices de ce niveau.

        Remarque : Des exercices qui appartiennent à plusieurs niveaux peuvent
        apparaître plurieurs fois.
        """
        levels = collections.defaultdict(set)
        for exo in self.values():
            for lvl in exo.tags:
                levels[lvl].add(exo)
        return levels

    def sorted_levels(self):
        """Renvoit les exercices, sous la forme d'une liste triée par niveau.

        Chaque élément de la liste est lui-même une liste ``[niveau, exercices]``, où :
        - ``niveau`` : est le niveau (chaîne de caractères) ,
        - ``exercices`` : est la liste triée des exercices de ce niveau.

        Le tri par niveau est un tri logique pour un humain (sixième, puis cinquième, etc.).
        """
        levels = self.dict_levels()
        return [
            [niveau, sorted(levels[niveau], key=operator.methodcaller("name"))]
            for niveau in NIVEAUX
            ]

    def filter_tags(self, *clauses):
        if not clauses:
            return self
        exercises = set()
        for conjunction in clauses:
            for exo in self.values():
                if conjunction.issubset(set(exo.tags)):
                    exercises.add(exo)
        return self.__class__(exercises = exercises)

    def filter_desc(self, *descriptions):
        if not descriptions:
            return self
        exercises = set()
        for desc in descriptions:
            for exo in self.values():
                if desc.search(exo.description()):
                    exercises.add(exo)
        return self.__class__(exercises = exercises)

################################################################################
# Exercices créés à partir de templates Jinja2

def templatedir():
    return os.path.join(directories.EXODIR, "templates")

class Jinja2Exercise(TexExercise):
    """Exercice utilisant un template jinja2."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = {}

    @property
    def environment(self):
        """Création de l'environnement Jinja2, duquel sera chargé le template."""
        return jinja2tex.LatexEnvironment(
            loader=jinja2tex.FileSystemLoader(templatedir())
        )

    @property
    def statement_name(self):
        """Nom du fichier de l'énoncé (sans le répertoire)."""
        return os.path.join("{}-statement.tex".format(self.__class__.__name__))

    @property
    def answer_name(self):
        """Nom du fichier du corrigé (sans le répertoire)."""
        return os.path.join("{}-answer.tex".format(self.__class__.__name__))

    def tex_statement(self):
        """Génération de l'énoncé"""
        return self.environment.get_template(self.statement_name).render(self.context)

    def tex_answer(self):
        """Génération du corrigé"""
        return self.environment.get_template(self.answer_name).render(self.context)

