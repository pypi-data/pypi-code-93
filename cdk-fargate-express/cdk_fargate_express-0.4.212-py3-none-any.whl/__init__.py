'''
[![awscdk-jsii-template](https://img.shields.io/badge/built%20with-awscdk--jsii--template-blue)](https://github.com/pahud/awscdk-jsii-template)
[![NPM version](https://badge.fury.io/js/cdk-fargate-express.svg)](https://badge.fury.io/js/cdk-fargate-express)
[![PyPI version](https://badge.fury.io/py/cdk-fargate-express.svg)](https://badge.fury.io/py/cdk-fargate-express)
![Release](https://github.com/pahud/cdk-fargate-express/workflows/Release/badge.svg)

# cdk-fargate-express

Deploy your serverless Express app in AWS with AWS CDK

## Usage

On deployment, AWS CDK executs `docker build` with your Express code assets at `express.d`

For example:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_fargate_express import ExpressService

ExpressService(stack, "testing", vpc=vpc)
```

You may specify different folder by specifying `expressAssets` property:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
ExpressService(stack, "testing",
    vpc=vpc,
    express_assets=path.join(__dirname, "../another_express.d")
)
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

import aws_cdk.aws_ec2
import aws_cdk.aws_ecs_patterns
import aws_cdk.core


class ExpressService(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-fargate-express.ExpressService",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        express_assets: builtins.str,
        service_options: typing.Optional[aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateServiceProps] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param express_assets: local path to the docker assets directory.
        :param service_options: options to customize the servide.
        :param vpc: The VPC.
        '''
        props = ExpressServiceProps(
            express_assets=express_assets, service_options=service_options, vpc=vpc
        )

        jsii.create(ExpressService, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expressAssets")
    def express_assets(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expressAssets"))


@jsii.data_type(
    jsii_type="cdk-fargate-express.ExpressServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "express_assets": "expressAssets",
        "service_options": "serviceOptions",
        "vpc": "vpc",
    },
)
class ExpressServiceProps:
    def __init__(
        self,
        *,
        express_assets: builtins.str,
        service_options: typing.Optional[aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateServiceProps] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param express_assets: local path to the docker assets directory.
        :param service_options: options to customize the servide.
        :param vpc: The VPC.
        '''
        if isinstance(service_options, dict):
            service_options = aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateServiceProps(**service_options)
        self._values: typing.Dict[str, typing.Any] = {
            "express_assets": express_assets,
        }
        if service_options is not None:
            self._values["service_options"] = service_options
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def express_assets(self) -> builtins.str:
        '''local path to the docker assets directory.'''
        result = self._values.get("express_assets")
        assert result is not None, "Required property 'express_assets' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_options(
        self,
    ) -> typing.Optional[aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateServiceProps]:
        '''options to customize the servide.

        :defult: - None
        '''
        result = self._values.get("service_options")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateServiceProps], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''The VPC.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExpressServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ExpressService",
    "ExpressServiceProps",
]

publication.publish()
