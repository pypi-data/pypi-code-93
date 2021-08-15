#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with package-manifest.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pytest


@pytest.fixture()
def create_include_manifest():
    def _apply(content: str) -> str:
        return """---
        manifest:
          - include: {0}
        """.format(
            content
        )

    return _apply


@pytest.fixture()
def create_exclude_manifest():
    def _apply(content: str) -> str:
        return """---
        manifest:
          - include: ["**/*"]
          - exclude: [manifest.yml]
          - exclude: {0}
        """.format(
            content
        )

    return _apply
