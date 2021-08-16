#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with package-manifest.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib

from .support import do_exclude_test, do_include_test


class TestInclude:
    def test_subdir(self, create_include_manifest):
        manifest_spec = '["**/t*"]'
        defined_files = [
            "one",
            "two",
            "three",
            "four",
            "subdir/one",
            "subdir/two",
        ]
        expected_files = {
            pathlib.Path(x) for x in ["two", "three", "subdir/two"]
        }

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert result == expected_files

    def test_subdir_path(self, create_include_manifest):
        manifest_spec = '["**/subdir/t*"]'
        defined_files = [
            "one",
            "two",
            "three",
            "four",
            "subdir/one",
            "subdir/two",
            "another/subdir/twice",
        ]
        expected_files = {
            pathlib.Path(x) for x in ["subdir/two", "another/subdir/twice"]
        }

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert result == expected_files


class TestExclude:
    def test_subdir(self, create_exclude_manifest):
        manifest_spec = '["**/t*"]'
        defined_files = [
            "one",
            "two",
            "three",
            "four",
            "subdir/one",
            "subdir/two",
        ]
        expected_files = {
            pathlib.Path(x) for x in ["one", "four", "subdir/one"]
        }

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert result == expected_files

    def test_subdir_path(self, create_exclude_manifest):
        manifest_spec = '["**/subdir/t*"]'
        defined_files = [
            "one",
            "two",
            "three",
            "four",
            "subdir/one",
            "subdir/two",
            "another/subdir/twice",
        ]
        expected_files = {
            pathlib.Path(x)
            for x in ["one", "two", "three", "four", "subdir/one"]
        }

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert result == expected_files
