#!/usr/bin/env python3

# Pyromaths
# Un programme en Python qui permet de créer des fiches d'exercices types de
# mathématiques niveau collège ainsi que leur corrigé en LaTeX.
# Copyright (C) 2006 -- Jérôme Ortais (jerome.ortais@pyromaths.org)
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
#

import codecs
import contextlib
import functools
import logging
import os
import subprocess
import shutil
import sys
import tempfile
import textwrap

from pyromaths.outils import jinja2tex
from pyromaths import directories

#==============================================================
#        Gestion des extensions de fichiers
#==============================================================
def supprime_extension(filename, ext):
    """Supprime l'éventuelle extension ext du nom de fichier filename.

    - ext est une chaîne de caractères quelconque.

    >>> supprime_extension("plop.tex", ".tex")
    'plop'
    >>> supprime_extension("plop.tex", ".pdf")
    'plop.tex'
    """
    if filename.endswith(ext):
        return filename[:-len(ext)]
    return filename

################################################################################

class Fiche:
    basename = "exercise"

    def __init__(self, context, *, template="pyromaths.tex", dirty=False):
        self.context = context
        self.template = template
        self.dirty = dirty

    def __enter__(self):
        self.workingdir = tempfile.mkdtemp(prefix="pyromaths-")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.dirty:
            logging.info("Temporary directory '%s' not removed (as requested).", self.workingdir)
        else:
            shutil.rmtree(self.workingdir)

    def tempfile(self, ext=None):
        if ext is None:
            return os.path.join(self.workingdir, self.basename)
        return os.path.join(self.workingdir, "{}.{}".format(self.basename, ext))

    @property
    def texname(self):
        return self.tempfile("tex")

    @property
    def pdfname(self):
        return self.tempfile("pdf")

    @property
    def latexmkrcname(self):
        return os.path.join(self.workingdir, "latexmkrc")

    @functools.lru_cache(10)
    def write_tex(self):
        environment = jinja2tex.LatexEnvironment(
            loader=jinja2tex.FileSystemLoader([
                os.path.join(directories.CONFIGDIR, 'templates'),
                os.path.join(directories.DATADIR, 'templates'),
                ])
        )
        with codecs.open(self.texname, mode='w', encoding='utf-8') as exofile:
            exofile.write(environment.get_template(self.template).render(self.context))

    def write_pdf(self):
        self.write_tex()
        self.write_latexmkrc()
        if os.name == 'nt':
            subprocess.run(
                ["latexmk", "-norc", "-r", "latexmkrc", self.basename],
                cwd=self.workingdir,
                env={"PATH": os.environ['PATH'], "WINDIR": os.environ['WINDIR'], 'USERPROFILE': os.environ['USERPROFILE']},
                )
            subprocess.run(
                ["latexmk", "-norc", "-r", "latexmkrc", "-c"],
                cwd=self.workingdir,
                env={"PATH": os.environ['PATH'], "WINDIR": os.environ['WINDIR'], 'USERPROFILE': os.environ['USERPROFILE']},
                )
        else:
            subprocess.run(
                ["latexmk", "-norc", "-r", "latexmkrc", self.basename],
                cwd=self.workingdir,
                )
            subprocess.run(
                ["latexmk", "-norc", "-r", "latexmkrc", "-c"],
                cwd=self.workingdir,
                )

    @functools.lru_cache(1)
    def write_latexmkrc(self):
        with open(self.latexmkrcname, 'w') as latexmkrc:
            latexmkrc.write(textwrap.dedent("""\
            $pdf_mode = 2;
            $ps2pdf = "ps2pdf %O %S %D";
            $latex = "latex --shell-escape -interaction=nonstopmode  %O %S";
            $auto_rc_use=0;
            $silent = 1;
            sub asy {return system("asy '$_[0]'");}
            add_cus_dep("asy","eps",0,"asy");
            add_cus_dep("asy","pdf",0,"asy");
            add_cus_dep("asy","tex",0,"asy");
            $cleanup_mode = 2;
            $clean_ext .= " %R-?.tex %R-??.tex %R-figure*.dpth %R-figure*.dvi %R-figure*.eps %R-figure*.log %R-figure*.md5 %R-figure*.pre %R-figure*.ps %R-figure*.asy %R-*.asy %R-*_0.eps %R-*.pre";
            """))
            #latexmkrc.write('push @generated_exts, \'pre\', \'dvi\', \'ps\', \'auxlock\', \'fdb_latexmk\', \'fls\', \'out\', \'aux\';\n')
            #latexmkrc.write('@generated_exts = qw(4ct 4tc acn acr alg aux auxlock bbl dvi eps fls glg glo gls idv idx ind ist lg lof lot nav net out pre ps ptc run.xml snm thm tmp toc vrb xdv xref);')


    def show_pdf(self, filename=None):
        if filename is None:
            filename = self.pdfname
        if os.name == "nt":  # Cas de Windows.
            os.startfile(filename)
        elif sys.platform == "darwin":  # Cas de Mac OS X.
            subprocess.run(['open', filename])
        else:
            subprocess.run(['gio', 'open', filename])

