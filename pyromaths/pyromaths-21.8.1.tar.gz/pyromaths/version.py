#! /usr/bin/env python3

"""Méta-information about pyromaths."""

# Ce fichier ne doit avoir *aucun* import à part ceux de la librairie standard.

import textwrap
import time

VERSION = '21.8.1'
AUTHOR = "Jérôme Ortais"
AUTHOR_EMAIL = "jerome.ortais@pyromaths.org"
COPYRIGHT_YEAR = time.strftime('%Y')
COPYRIGHT_HTML = textwrap.dedent("""\
        © 2006 – {} Jérôme Ortais
        <br/>
        <span style=" font-size:small;">Pyromaths est distribué sous licence GPL.</span>
        """).format(COPYRIGHT_YEAR)
WEBSITE = 'http://www.pyromaths.org/'
