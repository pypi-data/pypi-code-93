import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import (
    Component as _Component_2b0ad27f,
    NodeProject as _NodeProject_1f001c1d,
    Project as _Project_57d89203,
)


class NpmConfig(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.javascript.NpmConfig",
):
    '''(experimental) File representing the local NPM config in .npmrc.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _NodeProject_1f001c1d,
        *,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param registry: (experimental) URL of the registry mirror to use. You can change this or add scoped registries using the addRegistry method Default: - use npmjs default registry

        :stability: experimental
        '''
        options = NpmConfigOptions(registry=registry)

        jsii.create(NpmConfig, self, [project, options])

    @jsii.member(jsii_name="addConfig")
    def add_config(self, name: builtins.str, value: builtins.str) -> None:
        '''(experimental) configure a generic property.

        :param name: the name of the property.
        :param value: the value of the property.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addConfig", [name, value]))

    @jsii.member(jsii_name="addRegistry")
    def add_registry(
        self,
        url: builtins.str,
        scope: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) configure a scoped registry.

        :param url: the URL of the registry to use.
        :param scope: the scope the registry is used for; leave empty for the default registry

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addRegistry", [url, scope]))


@jsii.data_type(
    jsii_type="projen.javascript.NpmConfigOptions",
    jsii_struct_bases=[],
    name_mapping={"registry": "registry"},
)
class NpmConfigOptions:
    def __init__(self, *, registry: typing.Optional[builtins.str] = None) -> None:
        '''(experimental) Options to configure the local NPM config.

        :param registry: (experimental) URL of the registry mirror to use. You can change this or add scoped registries using the addRegistry method Default: - use npmjs default registry

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if registry is not None:
            self._values["registry"] = registry

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''(experimental) URL of the registry mirror to use.

        You can change this or add scoped registries using the addRegistry method

        :default: - use npmjs default registry

        :stability: experimental
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NpmConfigOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Projenrc(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.javascript.Projenrc",
):
    '''(experimental) Sets up a javascript project to use TypeScript for projenrc.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        filename: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.js"

        :stability: experimental
        '''
        options = ProjenrcOptions(filename=filename)

        jsii.create(Projenrc, self, [project, options])


@jsii.data_type(
    jsii_type="projen.javascript.ProjenrcOptions",
    jsii_struct_bases=[],
    name_mapping={"filename": "filename"},
)
class ProjenrcOptions:
    def __init__(self, *, filename: typing.Optional[builtins.str] = None) -> None:
        '''
        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.js"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if filename is not None:
            self._values["filename"] = filename

    @builtins.property
    def filename(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the projenrc file.

        :default: ".projenrc.js"

        :stability: experimental
        '''
        result = self._values.get("filename")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjenrcOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "NpmConfig",
    "NpmConfigOptions",
    "Projenrc",
    "ProjenrcOptions",
]

publication.publish()
