'''
[![NPM version](https://badge.fury.io/js/cdk-kaniko.svg)](https://badge.fury.io/js/cdk-kaniko)
[![PyPI version](https://badge.fury.io/py/cdk-kaniko.svg)](https://badge.fury.io/py/cdk-kaniko)
[![Release](https://github.com/pahud/cdk-kaniko/actions/workflows/release.yml/badge.svg)](https://github.com/pahud/cdk-kaniko/actions/workflows/release.yml)

# `cdk-kaniko`

Build images with `kanilo` in **AWS Fargate**

# About

`cdk-kaniko` is a CDK construct library that allows you to build images with [**kaniko**](https://github.com/GoogleContainerTools/kaniko) in **AWS Fargate**. Inspired from the blog post - [Building container images on Amazon ECS on AWS Fargate](https://aws.amazon.com/tw/blogs/containers/building-container-images-on-amazon-ecs-on-aws-fargate/) by *Re Alvarez-Parmar* and *Olly Pomeroy*, this library aims to abstract away all the infrastructure provisioning and configuration with minimal IAM policies required and allow you to focus on the high level CDK constructs. Under the covers, `cdk-kaniko` leverages the [cdk-fargate-run-task](https://github.com/pahud/cdk-fargate-run-task) so you can build the image just once or schedule the building periodically.

# Sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
app = cdk.App()

stack = cdk.Stack(app, "my-stack-dev")

kaniko = Kaniko(stack, "KanikoDemo",
    context="git://github.com/pahud/vscode.git",
    context_sub_path="./.devcontainer"
)

# build it once
kaniko.build_image("once")

# schedule the build every day 0:00AM
kaniko.build_image("everyday", Schedule.cron(
    minute="0",
    hour="0"
))
```

# fargate spot support

Use `fargateSpot` to enable the `FARGATE_SPOT` capacity provider to provision the fargate tasks.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
Kaniko(stack, "KanikoDemo",
    context=context,
    context_sub_path=context_sub_path,
    fargate_spot=True
)
```

# Note

Please note the image building could take some minutes depending on the complexity of the provided `Dockerfile`. On deployment completed, you can check and tail the **AWS Fargate** task logs from the **AWS CloudWatch Logs** to view all the build output.
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
import aws_cdk.aws_ecr
import aws_cdk.aws_ecs
import aws_cdk.aws_events
import aws_cdk.core


class Kaniko(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-kaniko.Kaniko",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        context: builtins.str,
        context_sub_path: typing.Optional[builtins.str] = None,
        destination_repository: typing.Optional[aws_cdk.aws_ecr.IRepository] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        fargate_spot: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param context: Kaniko build context.
        :param context_sub_path: The context sub path.
        :param destination_repository: The target ECR repository. Default: - create a new ECR private repository
        :param dockerfile: The Dockerfile for the image building. Default: Dockerfile
        :param fargate_spot: Use FARGATE_SPOT capacity provider.
        '''
        props = KanikoProps(
            context=context,
            context_sub_path=context_sub_path,
            destination_repository=destination_repository,
            dockerfile=dockerfile,
            fargate_spot=fargate_spot,
        )

        jsii.create(Kaniko, self, [scope, id, props])

    @jsii.member(jsii_name="buildImage")
    def build_image(
        self,
        id: builtins.str,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
    ) -> None:
        '''Build the image with kaniko.

        :param id: -
        :param schedule: The schedule to repeatedly build the image.
        '''
        return typing.cast(None, jsii.invoke(self, "buildImage", [id, schedule]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> aws_cdk.aws_ecs.ICluster:
        return typing.cast(aws_cdk.aws_ecs.ICluster, jsii.get(self, "cluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationRepository")
    def destination_repository(self) -> aws_cdk.aws_ecr.IRepository:
        return typing.cast(aws_cdk.aws_ecr.IRepository, jsii.get(self, "destinationRepository"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="task")
    def task(self) -> aws_cdk.aws_ecs.FargateTaskDefinition:
        return typing.cast(aws_cdk.aws_ecs.FargateTaskDefinition, jsii.get(self, "task"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-kaniko.KanikoProps",
    jsii_struct_bases=[],
    name_mapping={
        "context": "context",
        "context_sub_path": "contextSubPath",
        "destination_repository": "destinationRepository",
        "dockerfile": "dockerfile",
        "fargate_spot": "fargateSpot",
    },
)
class KanikoProps:
    def __init__(
        self,
        *,
        context: builtins.str,
        context_sub_path: typing.Optional[builtins.str] = None,
        destination_repository: typing.Optional[aws_cdk.aws_ecr.IRepository] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        fargate_spot: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param context: Kaniko build context.
        :param context_sub_path: The context sub path.
        :param destination_repository: The target ECR repository. Default: - create a new ECR private repository
        :param dockerfile: The Dockerfile for the image building. Default: Dockerfile
        :param fargate_spot: Use FARGATE_SPOT capacity provider.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "context": context,
        }
        if context_sub_path is not None:
            self._values["context_sub_path"] = context_sub_path
        if destination_repository is not None:
            self._values["destination_repository"] = destination_repository
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if fargate_spot is not None:
            self._values["fargate_spot"] = fargate_spot

    @builtins.property
    def context(self) -> builtins.str:
        '''Kaniko build context.

        :see: https://github.com/GoogleContainerTools/kaniko#kaniko-build-contexts
        '''
        result = self._values.get("context")
        assert result is not None, "Required property 'context' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def context_sub_path(self) -> typing.Optional[builtins.str]:
        '''The context sub path.

        :defautl: - current directory
        '''
        result = self._values.get("context_sub_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_repository(self) -> typing.Optional[aws_cdk.aws_ecr.IRepository]:
        '''The target ECR repository.

        :default: - create a new ECR private repository
        '''
        result = self._values.get("destination_repository")
        return typing.cast(typing.Optional[aws_cdk.aws_ecr.IRepository], result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''The Dockerfile for the image building.

        :default: Dockerfile
        '''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fargate_spot(self) -> typing.Optional[builtins.bool]:
        '''Use FARGATE_SPOT capacity provider.'''
        result = self._values.get("fargate_spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KanikoProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Kaniko",
    "KanikoProps",
]

publication.publish()
