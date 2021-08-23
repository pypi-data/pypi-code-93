# Copyright (c) 2015 - Red Hat Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

"""package layout management"""


from pyrpkg.errors import LayoutError

from .base import MetaLayout
from .layouts import (DistGitLayout, IncompleteLayout,  # noqa: F401
                      RetiredLayout, SRPMLayout)


def build(path, hint=None):
    """
    Tries to create a layout instance based on MetaLayout._layouts
    and will return an instance in the first successfull attempt to
    create a new object from the MetaLayout._layouts list.

    Returns None if no layouts can be created.
    """
    for layout in MetaLayout._layouts:
        try:
            return layout.from_path(path, hint)
        except LayoutError:
            continue
    return None
