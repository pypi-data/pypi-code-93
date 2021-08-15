#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with package-manifest.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import contextlib
import pathlib
import tempfile
import typing

from package_manifest._schema import Manifest


@contextlib.contextmanager
def mock_files(
    file_names: typing.List[str],
) -> typing.Generator[pathlib.Path, None, None]:
    with tempfile.TemporaryDirectory() as dir:
        this_path = pathlib.Path(dir)
        for this_file in file_names:
            file_path = this_path / this_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open(mode="w") as f:
                f.write("")

        yield this_path


@contextlib.contextmanager
def defined_manifest(
    defined_files: typing.List[str], manifest_content: str
) -> typing.Generator[pathlib.Path, None, None]:
    with mock_files(defined_files) as root_dir:
        manifest_file = root_dir / "manifest.yml"
        with manifest_file.open(mode="w") as f:
            f.write(manifest_content)

        yield root_dir, manifest_file


def do_include_test(manifest_spec, defined_files, create_include_manifest):
    with defined_manifest(
        defined_files, create_include_manifest(manifest_spec)
    ) as (
        root_dir,
        manifest_file,
    ):
        under_test = Manifest.from_file(manifest_file)

        assert len(under_test.manifest) == 1

        result = under_test.apply(root_dir)

        return result, under_test


def do_exclude_test(manifest_spec, defined_files, create_exclude_manifest):
    with defined_manifest(
        defined_files, create_exclude_manifest(manifest_spec)
    ) as (
        root_dir,
        manifest_file,
    ):
        under_test = Manifest.from_file(manifest_file)

        assert len(under_test.manifest) == 3

        result = under_test.apply(root_dir)

        return result, under_test
