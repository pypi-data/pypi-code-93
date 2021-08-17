'''
# @affinidi/common-check-widget-backend-lib [![NPM](https://img.shields.io/npm/v/jsii-code-samples)](https://www.npmjs.com/package/@affinidi/common-check-widget-backend-lib) [![PyPI](https://img.shields.io/pypi/v/aws-jsiisamples.jsii-code-samples)](https://pypi.org/project/common-check-widget-backend-lib) [![Maven](https://img.shields.io/maven-central/v/software.aws.jsiisamples.jsii/jsii-code-samples)](https://search.maven.org/artifact/common.check.widget.backend.lib/backend-ib) [![NuGet](https://img.shields.io/nuget/v/AWSSamples.Jsii)](https://www.nuget.org/packages/CCW.Jsii%22)

> An common-check-widget-backend-lib package authored in TypeScript that gets published as GitHub packages for Node.js, Python etc

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

## Coming soon
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *


class CommonCheckWidget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@affinidi/common-check-widget-backend-lib.CommonCheckWidget",
):
    def __init__(self) -> None:
        jsii.create(CommonCheckWidget, self, [])

    @jsii.member(jsii_name="ccw")
    def ccw(self, encryption_file: typing.Any, callback: typing.Any) -> None:
        '''
        :param encryption_file: -
        :param callback: -
        '''
        return typing.cast(None, jsii.invoke(self, "ccw", [encryption_file, callback]))

    @jsii.member(jsii_name="ccwasync")
    def ccwasync(self, encryption_file: typing.Any) -> typing.Any:
        '''
        :param encryption_file: -
        '''
        return typing.cast(typing.Any, jsii.ainvoke(self, "ccwasync", [encryption_file]))

    @jsii.member(jsii_name="ccwbypath")
    def ccwbypath(self, path: typing.Any, callback: typing.Any) -> None:
        '''
        :param path: -
        :param callback: -
        '''
        return typing.cast(None, jsii.invoke(self, "ccwbypath", [path, callback]))

    @jsii.member(jsii_name="ccwbypathasync")
    def ccwbypathasync(self, path: typing.Any) -> typing.Any:
        '''
        :param path: -
        '''
        return typing.cast(typing.Any, jsii.ainvoke(self, "ccwbypathasync", [path]))

    @jsii.member(jsii_name="ccwerror")
    def ccwerror(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.invoke(self, "ccwerror", []))


__all__ = [
    "CommonCheckWidget",
]

publication.publish()
