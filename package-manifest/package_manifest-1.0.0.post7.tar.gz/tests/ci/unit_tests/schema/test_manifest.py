#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with package-manifest.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import contextlib
import pathlib
import typing

import pytest

from package_manifest import Manifest

from .support import mock_files


def test_clean():
    data = {
        "manifest": [
            {"include": ["one", "two"]},
            {"exclude": ["three", "four", "five"]},
        ],
    }
    under_test = Manifest.parse_obj(data)

    assert len(under_test.manifest) == 2
    assert len(under_test.manifest[0].include) == 2
    assert len(under_test.manifest[1].exclude) == 3


@contextlib.contextmanager
def simple_manifest(
    defined_files: typing.List[str],
) -> typing.Generator[pathlib.Path, None, None]:
    with mock_files(defined_files) as root_dir:
        manifest_file = root_dir / "manifest.yml"
        with manifest_file.open(mode="w") as f:
            f.write(
                """---
manifest:
  - include: ["*"]
  - exclude: 
    - other
"""
            )

        yield root_dir, manifest_file


class TestFile:
    def test_synchronous(self):
        defined_files = ["this", "other", "some/file"]
        with simple_manifest(defined_files) as (root_dir, manifest_file):
            under_test = Manifest.from_file(manifest_file)

        assert len(under_test.manifest) == 2
        assert len(under_test.manifest[0].include) == 1
        assert len(under_test.manifest[1].exclude) == 1

    @pytest.mark.asyncio
    async def test_asynchronous(self):
        defined_files = ["this", "other", "some/file"]
        with simple_manifest(defined_files) as (root_dir, manifest_file):
            under_test = await Manifest.from_aiofile(manifest_file)

        assert len(under_test.manifest) == 2
        assert len(under_test.manifest[0].include) == 1
        assert len(under_test.manifest[1].exclude) == 1
