import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import Component as _Component_2b0ad27f, Project as _Project_57d89203


class Dependencies(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.deps.Dependencies",
):
    '''(experimental) The ``Dependencies`` component is responsible to track the list of dependencies a project has, and then used by project types as the model for rendering project-specific dependency manifests such as the dependencies section ``package.json`` files.

    To add a dependency you can use a project-type specific API such as
    ``nodeProject.addDeps()`` or use the generic API of ``project.deps``:

    :stability: experimental
    '''

    def __init__(self, project: _Project_57d89203) -> None:
        '''(experimental) Adds a dependencies component to the project.

        :param project: The parent project.

        :stability: experimental
        '''
        jsii.create(Dependencies, self, [project])

    @jsii.member(jsii_name="parseDependency") # type: ignore[misc]
    @builtins.classmethod
    def parse_dependency(cls, spec: builtins.str) -> "DependencyCoordinates":
        '''(experimental) Returns the coordinates of a dependency spec.

        Given ``foo@^3.4.0`` returns ``{ name: "foo", version: "^3.4.0" }``.
        Given ``bar@npm:@bar/legacy`` returns ``{ name: "bar", version: "npm:@bar/legacy" }``.

        :param spec: -

        :stability: experimental
        '''
        return typing.cast("DependencyCoordinates", jsii.sinvoke(cls, "parseDependency", [spec]))

    @jsii.member(jsii_name="addDependency")
    def add_dependency(
        self,
        spec: builtins.str,
        type: "DependencyType",
        metadata: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> "Dependency":
        '''(experimental) Adds a dependency to this project.

        :param spec: The dependency spec in the format ``MODULE[@VERSION]`` where ``MODULE`` is the package-manager-specific module name and ``VERSION`` is an optional semantic version requirement (e.g. ``^3.4.0``).
        :param type: The type of the dependency.
        :param metadata: -

        :stability: experimental
        '''
        return typing.cast("Dependency", jsii.invoke(self, "addDependency", [spec, type, metadata]))

    @jsii.member(jsii_name="getDependency")
    def get_dependency(
        self,
        name: builtins.str,
        type: typing.Optional["DependencyType"] = None,
    ) -> "Dependency":
        '''(experimental) Returns a dependency by name.

        Fails if there is no dependency defined by that name or if ``type`` is not
        provided and there is more then one dependency type for this dependency.

        :param name: The name of the dependency.
        :param type: The dependency type. If this dependency is defined only for a single type, this argument can be omitted.

        :return: a copy (cannot be modified)

        :stability: experimental
        '''
        return typing.cast("Dependency", jsii.invoke(self, "getDependency", [name, type]))

    @jsii.member(jsii_name="removeDependency")
    def remove_dependency(
        self,
        name: builtins.str,
        type: typing.Optional["DependencyType"] = None,
    ) -> None:
        '''(experimental) Removes a dependency.

        :param name: The name of the module to remove (without the version).
        :param type: The dependency type. This is only required if there the dependency is defined for multiple types.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "removeDependency", [name, type]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MANIFEST_FILE")
    def MANIFEST_FILE(cls) -> builtins.str:
        '''(experimental) The project-relative path of the deps manifest file.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "MANIFEST_FILE"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="all")
    def all(self) -> typing.List["Dependency"]:
        '''(experimental) A copy of all dependencies recorded for this project.

        The list is sorted by type->name->version

        :stability: experimental
        '''
        return typing.cast(typing.List["Dependency"], jsii.get(self, "all"))


@jsii.data_type(
    jsii_type="projen.deps.DependencyCoordinates",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "version": "version"},
)
class DependencyCoordinates:
    def __init__(
        self,
        *,
        name: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Coordinates of the dependency (name and version).

        :param name: (experimental) The package manager name of the dependency (e.g. ``leftpad`` for npm). NOTE: For package managers that use complex coordinates (like Maven), we will codify it into a string somehow.
        :param version: (experimental) Semantic version version requirement. Default: - requirement is managed by the package manager (e.g. npm/yarn).

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The package manager name of the dependency (e.g. ``leftpad`` for npm).

        NOTE: For package managers that use complex coordinates (like Maven), we
        will codify it into a string somehow.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Semantic version version requirement.

        :default: - requirement is managed by the package manager (e.g. npm/yarn).

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DependencyCoordinates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.deps.DependencyType")
class DependencyType(enum.Enum):
    '''(experimental) Type of dependency.

    :stability: experimental
    '''

    RUNTIME = "RUNTIME"
    '''(experimental) The dependency is required for the program/library during runtime.

    :stability: experimental
    '''
    PEER = "PEER"
    '''(experimental) The dependency is required at runtime but expected to be installed by the consumer.

    :stability: experimental
    '''
    BUNDLED = "BUNDLED"
    '''(experimental) The dependency is bundled and shipped with the module, so consumers are not required to install it.

    :stability: experimental
    '''
    BUILD = "BUILD"
    '''(experimental) The dependency is required to run the ``build`` task.

    :stability: experimental
    '''
    TEST = "TEST"
    '''(experimental) The dependency is required to run the ``test`` task.

    :stability: experimental
    '''
    DEVENV = "DEVENV"
    '''(experimental) The dependency is required for development (e.g. IDE plugins).

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="projen.deps.DepsManifest",
    jsii_struct_bases=[],
    name_mapping={"dependencies": "dependencies"},
)
class DepsManifest:
    def __init__(self, *, dependencies: typing.Sequence["Dependency"]) -> None:
        '''
        :param dependencies: (experimental) All dependencies of this module.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dependencies": dependencies,
        }

    @builtins.property
    def dependencies(self) -> typing.List["Dependency"]:
        '''(experimental) All dependencies of this module.

        :stability: experimental
        '''
        result = self._values.get("dependencies")
        assert result is not None, "Required property 'dependencies' is missing"
        return typing.cast(typing.List["Dependency"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DepsManifest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.deps.Dependency",
    jsii_struct_bases=[DependencyCoordinates],
    name_mapping={
        "name": "name",
        "version": "version",
        "type": "type",
        "metadata": "metadata",
    },
)
class Dependency(DependencyCoordinates):
    def __init__(
        self,
        *,
        name: builtins.str,
        version: typing.Optional[builtins.str] = None,
        type: DependencyType,
        metadata: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''(experimental) Represents a project dependency.

        :param name: (experimental) The package manager name of the dependency (e.g. ``leftpad`` for npm). NOTE: For package managers that use complex coordinates (like Maven), we will codify it into a string somehow.
        :param version: (experimental) Semantic version version requirement. Default: - requirement is managed by the package manager (e.g. npm/yarn).
        :param type: (experimental) Which type of dependency this is (runtime, build-time, etc).
        :param metadata: (experimental) Additional JSON metadata associated with the dependency (package manager specific). Default: {}

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "type": type,
        }
        if version is not None:
            self._values["version"] = version
        if metadata is not None:
            self._values["metadata"] = metadata

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The package manager name of the dependency (e.g. ``leftpad`` for npm).

        NOTE: For package managers that use complex coordinates (like Maven), we
        will codify it into a string somehow.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Semantic version version requirement.

        :default: - requirement is managed by the package manager (e.g. npm/yarn).

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> DependencyType:
        '''(experimental) Which type of dependency this is (runtime, build-time, etc).

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(DependencyType, result)

    @builtins.property
    def metadata(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional JSON metadata associated with the dependency (package manager specific).

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Dependency(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Dependencies",
    "Dependency",
    "DependencyCoordinates",
    "DependencyType",
    "DepsManifest",
]

publication.publish()
