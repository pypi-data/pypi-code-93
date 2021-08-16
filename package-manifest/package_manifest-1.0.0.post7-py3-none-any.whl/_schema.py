#  Copyright (c) 2021-2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with
#  package-manifest. If not, see <https://opensource.org/licenses/MIT>.
#
import abc
import pathlib
import typing

import aiofiles  # type: ignore
import pydantic
import ruamel.yaml  # type: ignore

from ._path import PathSet

X = typing.TypeVar("X", bound="GlobList")


GlobList = typing.List[str]


W = typing.TypeVar("W", bound="ManifestAction")


class ManifestAction(metaclass=abc.ABCMeta):
    """Define the interface to a manifest action."""

    @abc.abstractmethod
    def apply(
        self: W, root_directory: pathlib.Path, current: PathSet
    ) -> PathSet:
        """Apply a manifest action."""
        pass


V = typing.TypeVar("V", bound="Include")


class Include(pydantic.BaseModel, ManifestAction):
    """Manifest include action."""

    include: GlobList

    def apply(
        self: V, root_directory: pathlib.Path, current: PathSet
    ) -> PathSet:
        """
        Extract included files from the specified directory.

        Files included by the patterns in this action are added to the
        current set.

        Args:
            root_directory: Directory from which to recursively inspect.
            current: Set of currently included files.

        Returns:
            Set of files expanded by manifest patterns specified in this
            include action.
        """
        result: PathSet = current.copy()

        for this_pattern in self.include:
            matched_files = set(root_directory.glob(this_pattern))
            result = result.union(
                {
                    x.relative_to(root_directory)
                    for x in matched_files
                    if x.is_file()
                }
            )

        return result


U = typing.TypeVar("U", bound="Exclude")


class Exclude(pydantic.BaseModel, ManifestAction):
    """Manifest exclude action."""

    exclude: GlobList

    def apply(
        self: U, root_directory: pathlib.Path, current: PathSet
    ) -> PathSet:
        """
        Extract excluded files from the specified directory.

        Files matching the patterns in this action are removed from the
        current set.

        Args:
            root_directory: Directory from which to recursively inspect.
            current: Set of currently included files.

        Returns:
            Set of files reduced by manifest patterns specified in this
            exclude action.
        """
        result: PathSet = current.copy()

        for this_pattern in self.exclude:
            matched_files = set(root_directory.glob(this_pattern))
            result = result - {
                x.relative_to(root_directory)
                for x in matched_files
                if x.is_file()
            }

        return result


T = typing.TypeVar("T", bound="Manifest")


class Manifest(pydantic.BaseModel):
    """Top level data model of a file manifest."""

    manifest: typing.List[
        typing.Union[
            Include,
            Exclude,
        ]
    ]

    def apply(
        self: T,
        root_directory: pathlib.Path,
    ) -> PathSet:
        """
        Apply include and exclude actions specified in the manifest.

        Args:
            root_directory: Directory from which to recursively inspect.

        Returns:
            Set of files resulting from include and exclude actions
            specified in the manifest.
        """
        result: PathSet = set()
        for this_action in self.manifest:
            result = this_action.apply(root_directory, result)

        return result

    @classmethod
    def from_file(cls: typing.Type[T], manifest_path: pathlib.Path) -> T:
        """Load manifest data synchronously from a file."""
        yaml = ruamel.yaml.YAML(typ="safe")
        with manifest_path.open(mode="r") as f:
            yaml_data = yaml.load(f.read())

        this_object = cls.parse_obj(yaml_data)

        return this_object

    @classmethod
    async def from_aiofile(
        cls: typing.Type[T], manifest_path: pathlib.Path
    ) -> T:
        """Load manifest data asynchronously from a file."""
        yaml = ruamel.yaml.YAML(typ="safe")
        async with aiofiles.open(manifest_path, mode="r") as f:
            content = await f.read()

        yaml_data = yaml.load(content)
        this_object = cls.parse_obj(yaml_data)

        return this_object
