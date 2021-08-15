#  Copyright (c) 2007-2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with
#  package-manifest. If not, see <https://opensource.org/licenses/MIT>.
#

"""A YAML based file package manifest framework for defining packages."""

from ._schema import Manifest  # noqa: F401

# required to satisfy flit packaging
from ._version import __version__  # noqa: F401
