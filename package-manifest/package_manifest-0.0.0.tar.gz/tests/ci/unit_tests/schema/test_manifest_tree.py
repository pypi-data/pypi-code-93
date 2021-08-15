#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with package-manifest.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib

from .support import do_exclude_test, do_include_test


class TestGraft:
    def test_from_root(self, create_include_manifest):
        manifest_spec = '["one/**/*"]'
        defined_files = ["file1", "one/file2", "one/subdir/file4", "two/file3"]
        expected_files = {
            pathlib.Path(x) for x in ["one/file2", "one/subdir/file4"]
        }

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert result == expected_files


class TestPrune:
    def test_from_root(self, create_exclude_manifest):
        manifest_spec = '["one/**/*"]'
        defined_files = ["file1", "one/file2", "one/subdir/file4", "two/file3"]
        expected_files = {pathlib.Path(x) for x in ["file1", "two/file3"]}

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert result == expected_files
