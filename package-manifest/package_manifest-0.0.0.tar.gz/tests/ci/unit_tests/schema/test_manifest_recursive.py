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
    def test_global(self, create_include_manifest):
        manifest_spec = '["**/t*"]'
        defined_files = [
            "one",
            "subdir/two",
            "sub/subdir/three",
            "subdir/four",
            "twice",
        ]
        expected_files = {
            pathlib.Path(x)
            for x in ["subdir/two", "twice", "sub/subdir/three"]
        }

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert result == expected_files

    def test_subdir(self, create_include_manifest):
        manifest_spec = '["subdir/**/t*"]'
        defined_files = [
            "one",
            "subdir/two",
            "subdir/sub/three",
            "subdir/four",
            "twice",
        ]
        expected_files = {
            pathlib.Path(x) for x in ["subdir/two", "subdir/sub/three"]
        }

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert result == expected_files

    def test_not_matched(self, create_include_manifest):
        manifest_spec = '["**/file"]'
        defined_files = [
            "file",
            "subdir/two",
            "subdir/filed/three",
            "subdir/file",
            "twice",
        ]
        expected_files = {pathlib.Path(x) for x in ["file", "subdir/file"]}

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert result == expected_files


class TestExclude:
    def test_global(self, create_exclude_manifest):
        manifest_spec = '["**/t*"]'
        defined_files = [
            "one",
            "subdir/two",
            "sub/subdir/three",
            "subdir/four",
            "twice",
        ]
        expected_files = {pathlib.Path(x) for x in ["one", "subdir/four"]}

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert result == expected_files

    def test_subdir(self, create_exclude_manifest):
        manifest_spec = '["**/subdir/**/t*"]'
        defined_files = [
            "one",
            "subdir/two",
            "subdir/sub/three",
            "subdir/four",
            "twice",
        ]
        expected_files = {
            pathlib.Path(x) for x in ["one", "subdir/four", "twice"]
        }

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert result == expected_files

    def test_not_matched(self, create_exclude_manifest):
        manifest_spec = '["**/file"]'
        defined_files = [
            "file",
            "subdir/two",
            "subdir/filed/three",
            "subdir/file",
            "twice",
        ]
        expected_files = {
            pathlib.Path(x)
            for x in ["twice", "subdir/two", "subdir/filed/three"]
        }

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert result == expected_files
