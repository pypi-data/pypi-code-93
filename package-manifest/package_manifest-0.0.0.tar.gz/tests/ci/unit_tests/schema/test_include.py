#  Copyright (c) 2021-2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with package-manifest.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib

from package_manifest._schema import Include

from .support import mock_files


def test_clean():
    data = {
        "include": ["LICENSE"],
    }
    under_test = Include.parse_obj(data)

    assert len(under_test.include) == 1
    assert under_test.include[0] == "LICENSE"


class TestApply:
    def test_single_file(self):
        data = {
            "include": ["this"],
        }
        under_test = Include.parse_obj(data)

        with mock_files(["this", "other", "some/file"]) as root_dir:
            result = under_test.apply(root_dir, set())

        assert result == {pathlib.Path("this")}

    def test_recursive_wildcard(self):
        data = {
            "include": ["**/*"],
        }
        under_test = Include.parse_obj(data)

        with mock_files(["this", "other", "some/file"]) as root_dir:
            result = under_test.apply(root_dir, set())

        assert result == {
            pathlib.Path("this"),
            pathlib.Path("other"),
            pathlib.Path("some/file"),
        }

    def test_single_wildcard(self):
        data = {
            "include": ["*"],
        }
        under_test = Include.parse_obj(data)

        with mock_files(["this", "other", "some/file"]) as root_dir:
            result = under_test.apply(root_dir, set())

        assert result == {pathlib.Path("this"), pathlib.Path("other")}

    def test_global_recursive_wildcard(self):
        data = {
            "include": ["**/this"],
        }
        under_test = Include.parse_obj(data)

        with mock_files(
            ["this", "other", "some/this", "some/dir/this"]
        ) as root_dir:
            result = under_test.apply(root_dir, set())

        assert result == {
            pathlib.Path("this"),
            pathlib.Path("some/this"),
            pathlib.Path("some/dir/this"),
        }
