#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with package-manifest.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib

from package_manifest._schema import Exclude

from .support import mock_files


def test_clean():
    data = {
        "exclude": ["LICENSE"],
    }
    under_test = Exclude.parse_obj(data)

    assert len(under_test.exclude) == 1
    assert under_test.exclude[0] == "LICENSE"


class TestApply:
    def test_single_file(self):
        data = {
            "exclude": ["some/file"],
        }
        under_test = Exclude.parse_obj(data)

        defined_files = ["this", "other", "some/file"]
        with mock_files(defined_files) as root_dir:
            result = under_test.apply(
                root_dir, {pathlib.Path(x) for x in defined_files}
            )

        assert result == {pathlib.Path("this"), pathlib.Path("other")}

    def test_recursive_wildcard(self):
        data = {
            # probably a silly thing to exclude?
            "exclude": ["**/*"],
        }
        under_test = Exclude.parse_obj(data)

        with mock_files(["this", "other", "some/file"]) as root_dir:
            result = under_test.apply(
                root_dir,
                {pathlib.Path(x) for x in ["this", "other", "some/file"]},
            )

        assert result == set()

    def test_single_wildcard1(self):
        data = {
            "exclude": ["*"],
        }
        under_test = Exclude.parse_obj(data)

        defined_files = ["this", "other", "some/file"]
        with mock_files(defined_files) as root_dir:
            result = under_test.apply(
                root_dir, {pathlib.Path(x) for x in defined_files}
            )

        assert result == {pathlib.Path("some/file")}

    def test_single_wildcard2(self):
        data = {
            "exclude": ["some/*"],
        }
        under_test = Exclude.parse_obj(data)

        defined_files = ["this", "other", "some/file"]
        with mock_files(defined_files) as root_dir:
            result = under_test.apply(
                root_dir, {pathlib.Path(x) for x in defined_files}
            )

        assert result == {pathlib.Path("this"), pathlib.Path("other")}

    def test_global_recursive_wildcard(self):
        data = {
            "exclude": ["**/this"],
        }
        under_test = Exclude.parse_obj(data)

        defined_files = ["this", "other", "some/this", "some/dir/this"]
        with mock_files(defined_files) as root_dir:
            result = under_test.apply(
                root_dir, {pathlib.Path(x) for x in defined_files}
            )

        assert len(result) == 1
        assert result == {pathlib.Path("other")}
