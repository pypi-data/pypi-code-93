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
    def test_simple(self, create_include_manifest):
        manifest_spec = '["t*"]'
        defined_files = ["one", "two", "three", "four"]
        expected_files = {pathlib.Path(x) for x in ["two", "three"]}

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert result == expected_files

    def test_two_wildcards(self, create_include_manifest):
        manifest_spec = "[tw*,th*]"
        defined_files = ["one", "two", "three", "four"]
        expected_files = {pathlib.Path(x) for x in ["two", "three"]}

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert len(under_test.manifest[0].include) == 2
        assert under_test.manifest[0].include[0] == "tw*"
        assert under_test.manifest[0].include[1] == "th*"

        assert result == expected_files

    def test_path_wildcards(self, create_include_manifest):
        manifest_spec = "[one/tw*]"
        expected_files = {pathlib.Path(x) for x in ["one/two", "one/twill"]}
        defined_files = [
            "this",
            "one/twill",
            "two",
            "three",
            "one/two",
            "four",
        ]

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert result == expected_files

    def test_subdir(self, create_include_manifest):
        manifest_spec = '["t*"]'
        defined_files = [
            "one",
            "two",
            "three",
            "four",
            "subdir/one",
            "subdir/two",
        ]
        expected_files = {pathlib.Path(x) for x in ["two", "three"]}

        result, under_test = do_include_test(
            manifest_spec, defined_files, create_include_manifest
        )

        assert result == expected_files


class TestExclude:
    def test_simple(self, create_exclude_manifest):
        manifest_spec = "[t*]"
        defined_files = ["one", "two", "three", "four"]
        expected_files = {pathlib.Path(x) for x in ["one", "four"]}

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert len(under_test.manifest[2].exclude) == 1
        assert result == expected_files

    def test_two_wildcards(self, create_exclude_manifest):
        manifest_spec = '["tw*", "th*"]'
        defined_files = ["one", "two", "three", "four"]
        expected_files = {pathlib.Path(x) for x in ["one", "four"]}

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert len(under_test.manifest[2].exclude) == 2
        assert result == expected_files

    def test_path1(self, create_exclude_manifest):
        manifest_spec = "[two]"
        defined_files = ["one", "two", "three/two", "four"]
        expected_files = {
            pathlib.Path(x) for x in ["one", "three/two", "four"]
        }

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert len(under_test.manifest[2].exclude) == 1
        assert result == expected_files

    def test_path2(self, create_exclude_manifest):
        manifest_spec = '["one/two*"]'
        defined_files = ["one/two-some", "one/twoother/three", "four"]
        expected_files = {
            pathlib.Path(x) for x in ["one/twoother/three", "four"]
        }

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert len(under_test.manifest[2].exclude) == 1
        assert result == expected_files

    def test_path3(self, create_exclude_manifest):
        manifest_spec = '["one/two*","one/two*/*"]'
        defined_files = [
            "one/two-some",
            "one/twoother/three",
            "one/twit/three",
            "four",
        ]
        expected_files = {pathlib.Path(x) for x in ["one/twit/three", "four"]}

        result, under_test = do_exclude_test(
            manifest_spec, defined_files, create_exclude_manifest
        )

        assert len(under_test.manifest[2].exclude) == 2
        assert result == expected_files
