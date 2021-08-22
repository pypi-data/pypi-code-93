'''
# CDK ECR Asset Scanner

The CDK ECR Asset Scanner is a custom L3 `ScannedDockerImageAsset` construct that builds and uploads your container image assets to ECR. After pushing, it will return the vulnerability report status in a Stack Output. In that way, it gives crucial and important security related information directly back to the engineer working with the stack. It aims to improve security insight while working with AWS CDK.

As stated before, `ScannedDockerImageAsset` is a custom L3 construct in the AWS Construct Library that combines the following L2 Constructs:

* DockerImageAsset
* A Custom Resource backed by a Lambda function
* Stack outputs

Because it just combines existing Constructs, this means the `ScannedDockerImageAsset` is a very stable L3 construct, not deemed experimental.

![Terminal](./docs/assets/terminal_output.png)

## USAGE

Run `npm i cdk-ecr-asset-scanner`.

Just add the `ScannedDockerImageAsset` to your imports, and use it exactly like you would a normal `DockerImageAsset`. It will do all the heavy lifting under the hood by itself. Make sure cdk peer dependencies are correct as usual, but npm will point those out (> 1.118.0 cdk versions)

Example (ts):

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_ecr_asset_scanner import ScannedDockerImageAsset
import path as path

env = {
    "region": process.env.CDK_DEFAULT_REGION,
    "account": process.env.CDK_DEFAULT_ACCOUNT
}

app = cdk.App()

class TestStack(cdk.Stack):
    def __init__(self, scope, id, props=None):
        super().__init__(scope, id, props)

        # Image without scan
        # const image3 = new DockerImageAsset(this, "zzz", {
        #   directory: path.join(__dirname, "../src/"),
        # });

        # Image with scan
        image = ScannedDockerImageAsset(self, "zzz",
            directory=path.join(__dirname, "../src/")
        )
        image3 = ecs.ContainerImage.from_docker_image_asset(image)

        task_definition = ecs.FargateTaskDefinition(self, "test-task-definition",
            memory_limit_mi_b=2048,
            cpu=1024
        )
        task_definition.add_container("container_example_three",
            image=image3,
            environment={
                "TEST_VAR": "THREE"
            },
            logging=ecs.AwsLogDriver(
                stream_prefix="three"
            )
        )
TestStack(app, "hh-stack", env=env)
```

## Availability

* Typescript / JS
* Python
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

import aws_cdk.assets
import aws_cdk.aws_ecr_assets
import aws_cdk.aws_lambda
import aws_cdk.core


class ScannedDockerImageAsset(
    aws_cdk.aws_ecr_assets.DockerImageAsset,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-ecr-asset-scanner.ScannedDockerImageAsset",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        directory: builtins.str,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        file: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        extra_hash: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow: typing.Optional[aws_cdk.assets.FollowMode] = None,
        ignore_mode: typing.Optional[aws_cdk.core.IgnoreMode] = None,
        follow_symlinks: typing.Optional[aws_cdk.core.SymlinkFollowMode] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param directory: The directory where the Dockerfile is stored. Any directory inside with a name that matches the CDK output folder (cdk.out by default) will be excluded from the asset
        :param build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Default: - no build args are passed
        :param file: Path to the Dockerfile (relative to the directory). Default: 'Dockerfile'
        :param repository_name: (deprecated) ECR repository name. Specify this property if you need to statically address the image, e.g. from a Kubernetes Pod. Note, this is only the repository name, without the registry and the tag parts. Default: - the default ECR repository for CDK assets
        :param target: Docker target to build to. Default: - no target
        :param extra_hash: (deprecated) Extra information to encode into the fingerprint (e.g. build instructions and other inputs). Default: - hash is only based on source content
        :param exclude: (deprecated) Glob patterns to exclude from the copy. Default: nothing is excluded
        :param follow: (deprecated) A strategy for how to handle symlinks. Default: Never
        :param ignore_mode: (deprecated) The ignore behavior to use for exclude patterns. Default: - GLOB for file assets, DOCKER or GLOB for docker assets depending on whether the '
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        '''
        props = aws_cdk.aws_ecr_assets.DockerImageAssetProps(
            directory=directory,
            build_args=build_args,
            file=file,
            repository_name=repository_name,
            target=target,
            extra_hash=extra_hash,
            exclude=exclude,
            follow=follow,
            ignore_mode=ignore_mode,
            follow_symlinks=follow_symlinks,
        )

        jsii.create(ScannedDockerImageAsset, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scanCRHandler")
    def scan_cr_handler(self) -> aws_cdk.core.CustomResource:
        return typing.cast(aws_cdk.core.CustomResource, jsii.get(self, "scanCRHandler"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scanFunction")
    def scan_function(self) -> aws_cdk.aws_lambda.SingletonFunction:
        return typing.cast(aws_cdk.aws_lambda.SingletonFunction, jsii.get(self, "scanFunction"))


__all__ = [
    "ScannedDockerImageAsset",
]

publication.publish()
