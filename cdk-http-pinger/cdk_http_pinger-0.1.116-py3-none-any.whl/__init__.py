'''
[![NPM version](https://badge.fury.io/js/cdk-http-pinger.svg)](https://badge.fury.io/js/cdk-http-pinger)
[![PyPI version](https://badge.fury.io/py/cdk-http-pinger.svg)](https://badge.fury.io/py/cdk-http-pinger)
![Release](https://github.com/pahud/cdk-http-pinger/workflows/Release/badge.svg?branch=main)

# `cdk-http-pinger`

HTTP Pinger for AWS CDK

# Sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_http_pinger import Pinger

app = App()

stack = Stack(app, "my-stack")

pinger = Pinger(stack, "Pinger", url="https://aws.amazon.com")

CfnOutput(stack, "HttpStatus", value=pinger.http_status)
CfnOutput(stack, "HtmlTitle", value=pinger.html_title)
CfnOutput(stack, "URL", value=pinger.url)
CfnOutput(stack, "Body", value=pinger.body)
```
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

import aws_cdk.core


class Pinger(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-http-pinger.Pinger",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        url: builtins.str,
        entry: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param url: 
        :param entry: optional entry file.
        :param parameter: 
        '''
        props = PingerProps(url=url, entry=entry, parameter=parameter)

        jsii.create(Pinger, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlTitle")
    def html_title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlTitle"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpStatus")
    def http_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> aws_cdk.core.CustomResource:
        return typing.cast(aws_cdk.core.CustomResource, jsii.get(self, "resource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))


@jsii.data_type(
    jsii_type="cdk-http-pinger.PingerProps",
    jsii_struct_bases=[],
    name_mapping={"url": "url", "entry": "entry", "parameter": "parameter"},
)
class PingerProps:
    def __init__(
        self,
        *,
        url: builtins.str,
        entry: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param url: 
        :param entry: optional entry file.
        :param parameter: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }
        if entry is not None:
            self._values["entry"] = entry
        if parameter is not None:
            self._values["parameter"] = parameter

    @builtins.property
    def url(self) -> builtins.str:
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def entry(self) -> typing.Optional[builtins.str]:
        '''optional entry file.'''
        result = self._values.get("entry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PingerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Pinger",
    "PingerProps",
]

publication.publish()
