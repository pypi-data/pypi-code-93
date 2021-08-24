'''
# @affinidi/common-check-widget-backend-lib [![NPM](https://img.shields.io/npm/v/jsii-code-samples)](https://www.npmjs.com/package/@affinidi/common-check-widget-backend-lib) [![PyPI](https://img.shields.io/pypi/v/aws-jsiisamples.jsii-code-samples)](https://pypi.org/project/common-check-widget-backend-lib) [![Maven](https://img.shields.io/maven-central/v/software.aws.jsiisamples.jsii/jsii-code-samples)](https://search.maven.org/artifact/common.check.widget.backend.lib/backend-ib) [![NuGet](https://img.shields.io/nuget/v/AWSSamples.Jsii)](https://www.nuget.org/packages/CCW.Jsii%22)

> An common-check-widget-backend-lib package authored in TypeScript that gets published as GitHub packages for Node.js, Python etc

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

## Documentations

https://common-check-widget-backend-lib.affinity-project.org/
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

from .common_check_verify import CommonCheckVerify as _CommonCheckVerify_98e4d318


class CommonCheckWidget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@affinidi/common-check-widget-backend-lib.CommonCheckWidget",
):
    def __init__(self, request_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param request_id: -
        '''
        jsii.create(CommonCheckWidget, self, [request_id])

    @jsii.member(jsii_name="getErrorMessage")
    def get_error_message(self, error_obj: typing.Any) -> typing.Any:
        '''
        :param error_obj: -
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "getErrorMessage", [error_obj]))

    @jsii.member(jsii_name="verifyAsync")
    def verify_async(self, encryption_file: typing.Any) -> typing.Any:
        '''
        :param encryption_file: -
        '''
        return typing.cast(typing.Any, jsii.ainvoke(self, "verifyAsync", [encryption_file]))

    @jsii.member(jsii_name="verifyByPathAsync")
    def verify_by_path_async(self, encryption_file_path: builtins.str) -> typing.Any:
        '''
        :param encryption_file_path: -
        '''
        return typing.cast(typing.Any, jsii.ainvoke(self, "verifyByPathAsync", [encryption_file_path]))

    @jsii.member(jsii_name="verifyByPathWithCallback")
    def verify_by_path_with_callback(
        self,
        encryption_file_path: builtins.str,
        callback: typing.Any,
    ) -> None:
        '''
        :param encryption_file_path: -
        :param callback: -
        '''
        return typing.cast(None, jsii.invoke(self, "verifyByPathWithCallback", [encryption_file_path, callback]))

    @jsii.member(jsii_name="verifyWithCallback")
    def verify_with_callback(
        self,
        encryption_file: typing.Any,
        callback: typing.Any,
    ) -> None:
        '''
        :param encryption_file: -
        :param callback: -
        '''
        return typing.cast(None, jsii.invoke(self, "verifyWithCallback", [encryption_file, callback]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commonCheckVerify")
    def common_check_verify(self) -> _CommonCheckVerify_98e4d318:
        return typing.cast(_CommonCheckVerify_98e4d318, jsii.get(self, "commonCheckVerify"))

    @common_check_verify.setter
    def common_check_verify(self, value: _CommonCheckVerify_98e4d318) -> None:
        jsii.set(self, "commonCheckVerify", value)


__all__ = [
    "CommonCheckWidget",
]

publication.publish()
