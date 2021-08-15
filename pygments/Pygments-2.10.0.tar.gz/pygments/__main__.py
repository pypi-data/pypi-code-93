"""
    pygments.__main__
    ~~~~~~~~~~~~~~~~~

    Main entry point for ``python -m pygments``.

    :copyright: Copyright 2006-2021 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import sys
import pygments.cmdline

try:
    sys.exit(pygments.cmdline.main(sys.argv))
except KeyboardInterrupt:
    sys.exit(1)
