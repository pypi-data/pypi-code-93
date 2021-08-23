
"""
https://docs.python-guide.org/writing/structure/
https://realpython.com/python-application-layouts/
https://python-packaging.readthedocs.io/en/latest/minimal.html
https://dev.to/codemouse92/dead-simple-python-project-structure-and-imports-38c6
https://stackoverflow.com/questions/193161/what-is-the-best-project-structure-for-a-python-application
https://stackoverflow.com/questions/3931741/why-does-make-think-the-target-is-up-to-date
https://gist.github.com/tasdikrahman/2bdb3fb31136a3768fac
https://github.com/ferdinandvanwyk/python_project_example
https://blog.j-labs.pl/2019/02/Pytest-why-its-more-popular-than-unittest
https://docs.pytest.org/en/reorganize-docs/new-docs/user/directory_structure.html
"""

# https://docs.python-guide.org/writing/structure/


# ***************************************************************************************

import pathlib as _pl
import sys     as _sys

# Insert project root as first directory to search in Python session PATH
_sys.path.insert(0, (_pl.Path(__file__).parent / "..").__str__())

# ***************************************************************************************

import lex2
import unittest

def DIR_OF(file: str) -> _pl.Path:
    return _pl.Path(file).parent
