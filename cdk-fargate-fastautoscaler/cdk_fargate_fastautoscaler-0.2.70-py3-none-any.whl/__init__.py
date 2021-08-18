'''
[![awscdk-jsii-template](https://img.shields.io/badge/built%20with-awscdk--jsii--template-blue)](https://github.com/pahud/awscdk-jsii-template)
[![NPM version](https://badge.fury.io/js/cdk-fargate-fastautoscaler.svg)](https://badge.fury.io/js/cdk-fargate-fastautoscaler)
[![PyPI version](https://badge.fury.io/py/cdk-fargate-fastautoscaler.svg)](https://badge.fury.io/py/cdk-fargate-fastautoscaler)
![Build](https://github.com/aws-samples/aws-fargate-fast-autoscaler/workflows/Build/badge.svg)

## aws-fargate-fast-autoscaler

**AWS Fargate Fast Autosaler** - A Serverless Implementation that Triggers your AWS Fargate autoscaling in seconds with `cdk-fargate-fastautoscaler`.

## cdk-fargate-fastautoscaler

`cdk-fargate-fastautoscaler` is a [aws/jsii](https://github.com/aws/jsii) construct library for AWS CDK.

By building your AWS CDK stacks with `cdk-fargate-fastautoscaler`, you can create your customized Fargate workload with the fast autoscaling capabilities.

![](images/fargate-fast-autoscaler.png)

# How it works

Behind the scene, our workload in PHP, NodeJS, Java or Python is running with a nginx reverse proxy within a single AWS Fargate Task exposing a `/nginx_status` endpoint for realtime connections info generation. All traffic coming through ALB to Fargate tasks will establish active connecitons with the nginx reverse proxy before it can hit our backend server.

We are running an AWS Step Function state machine to periodically invoke the AWS Lambda function and collect active connection numbers from each Fargate Task **every 3 seconds** and determine our scaling policy in the state machine followed by immediate `ecs service update` to increase the desired number of Fargate tasks.

# AWS CDK Sample

The following CDK sample creates a PHP service in AWS Fargate with the nginx as the reverse proxy.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
import aws_cdk.aws_ec2 as ec2
from aws_cdk.aws_ecs import AwsLogDriver, ContainerImage
from cdk_fargate_fastautoscaler import FargateFastAutoscaler
import path as path

app = cdk.App()

env = {
    "region": process.env.CDK_DEFAULT_REGION,
    "account": process.env.CDK_DEFAULT_ACCOUNT
}

stack = cdk.Stack(app, "FargateFastAutoscalerDemo", env=env)

vpc = ec2.Vpc.from_lookup(stack, "Vpc", is_default=True)

FargateFastAutoscaler(stack, "FargateFastAutoscaler",
    vpc=vpc,
    # create the backend PHP service
    backend_container={
        "image": ContainerImage.from_asset(path.join(__dirname, "../../sample/backend/php"))
    },
    # PHP service running on container port 2015
    backend_container_port_mapping=[{"container_port": 2015}]
)
```

On deployment complete, you'll see the URL in the Outputs:

**fargate-fast-autoscaling.URL** = http://farga-exter-1GW64WGQYNE4O-1567742142.us-west-2.elb.amazonaws.com

Open this URL and you will see the Caddy web server welcome page with phpinfo.

![](images/php-welcome.png)

And if you append `/nginx_status` in the URL and reload the page, you'll see this page:

![](images/nginx-status.png)

### Start your state machine

Go to Step Function console and click **start execution** on the state machines. Leave the execution name and input column as is and click **start execution** again. Your state machine will be running. Behind the scene the step function will invoke a Lambda function to collect **Active Connections** number from nginx reverse proxy on each fargate task and determine a new desired number of fargate tasks to scale. Typically it would just take **less than 10 seconds** before it starts to scale.

![](images/stepfunc.png)

# SNS Service Integration

The **SNSScaleOut** task in the state machine leverages direct Amazon SNS service integration to publish a notification to your SNS topic. You will receive SNS notification when it starts **ServiceScaleOut** task.

Specify the `snsTopic` property to define your custom SNS topic. If not defined, the construct will create a default SNS topic.

# Disable Scale In

By default, `disableScaleIn` is set to true to prevent your workload from scale-in. If you prefer to enable scale in, set `disableScaleIn` to `false`.

## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.
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
import aws_cdk.aws_ecs
import aws_cdk.aws_sns
import aws_cdk.core


class FargateFastAutoscaler(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-fargate-fastautoscaler.FargateFastAutoscaler",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        backend_container: aws_cdk.aws_ecs.ContainerDefinitionOptions,
        backend_container_port_mapping: typing.Sequence[aws_cdk.aws_ecs.PortMapping],
        vpc: aws_cdk.aws_ec2.IVpc,
        aws_cli_layer_arn: typing.Optional[builtins.str] = None,
        aws_cli_layer_version: typing.Optional[builtins.str] = None,
        disable_scale_in: typing.Optional[builtins.bool] = None,
        initial_task_number: typing.Optional[jsii.Number] = None,
        sns_topic: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param backend_container: backend container.
        :param backend_container_port_mapping: container port for the backend container.
        :param vpc: The VPC for the stack.
        :param aws_cli_layer_arn: AWS CLI Lambda layer ARN in Serverless App Repository. Default: - 'arn:aws:serverlessrepo:us-east-1:903779448426:applications/lambda-layer-awscli'
        :param aws_cli_layer_version: The version of the Serverless App for AWS CLI Lambda layer. Default: - AWSCLI_LAYER_VERSION
        :param disable_scale_in: disable scale in. Default: - true
        :param initial_task_number: initial number of tasks for the service. Default: - 2
        :param sns_topic: SNS Topic to publish the notification. Default: - do not publish to SNS
        '''
        props = FargateFastAutoscalerProps(
            backend_container=backend_container,
            backend_container_port_mapping=backend_container_port_mapping,
            vpc=vpc,
            aws_cli_layer_arn=aws_cli_layer_arn,
            aws_cli_layer_version=aws_cli_layer_version,
            disable_scale_in=disable_scale_in,
            initial_task_number=initial_task_number,
            sns_topic=sns_topic,
        )

        jsii.create(FargateFastAutoscaler, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fargateService")
    def fargate_service(self) -> aws_cdk.aws_ecs.FargateService:
        return typing.cast(aws_cdk.aws_ecs.FargateService, jsii.get(self, "fargateService"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fargateTaskDef")
    def fargate_task_def(self) -> aws_cdk.aws_ecs.FargateTaskDefinition:
        return typing.cast(aws_cdk.aws_ecs.FargateTaskDefinition, jsii.get(self, "fargateTaskDef"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fargateWatcherFuncArn")
    def fargate_watcher_func_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fargateWatcherFuncArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerVersionArn")
    def layer_version_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "layerVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-fargate-fastautoscaler.FargateFastAutoscalerProps",
    jsii_struct_bases=[],
    name_mapping={
        "backend_container": "backendContainer",
        "backend_container_port_mapping": "backendContainerPortMapping",
        "vpc": "vpc",
        "aws_cli_layer_arn": "awsCliLayerArn",
        "aws_cli_layer_version": "awsCliLayerVersion",
        "disable_scale_in": "disableScaleIn",
        "initial_task_number": "initialTaskNumber",
        "sns_topic": "snsTopic",
    },
)
class FargateFastAutoscalerProps:
    def __init__(
        self,
        *,
        backend_container: aws_cdk.aws_ecs.ContainerDefinitionOptions,
        backend_container_port_mapping: typing.Sequence[aws_cdk.aws_ecs.PortMapping],
        vpc: aws_cdk.aws_ec2.IVpc,
        aws_cli_layer_arn: typing.Optional[builtins.str] = None,
        aws_cli_layer_version: typing.Optional[builtins.str] = None,
        disable_scale_in: typing.Optional[builtins.bool] = None,
        initial_task_number: typing.Optional[jsii.Number] = None,
        sns_topic: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
    ) -> None:
        '''
        :param backend_container: backend container.
        :param backend_container_port_mapping: container port for the backend container.
        :param vpc: The VPC for the stack.
        :param aws_cli_layer_arn: AWS CLI Lambda layer ARN in Serverless App Repository. Default: - 'arn:aws:serverlessrepo:us-east-1:903779448426:applications/lambda-layer-awscli'
        :param aws_cli_layer_version: The version of the Serverless App for AWS CLI Lambda layer. Default: - AWSCLI_LAYER_VERSION
        :param disable_scale_in: disable scale in. Default: - true
        :param initial_task_number: initial number of tasks for the service. Default: - 2
        :param sns_topic: SNS Topic to publish the notification. Default: - do not publish to SNS
        '''
        if isinstance(backend_container, dict):
            backend_container = aws_cdk.aws_ecs.ContainerDefinitionOptions(**backend_container)
        self._values: typing.Dict[str, typing.Any] = {
            "backend_container": backend_container,
            "backend_container_port_mapping": backend_container_port_mapping,
            "vpc": vpc,
        }
        if aws_cli_layer_arn is not None:
            self._values["aws_cli_layer_arn"] = aws_cli_layer_arn
        if aws_cli_layer_version is not None:
            self._values["aws_cli_layer_version"] = aws_cli_layer_version
        if disable_scale_in is not None:
            self._values["disable_scale_in"] = disable_scale_in
        if initial_task_number is not None:
            self._values["initial_task_number"] = initial_task_number
        if sns_topic is not None:
            self._values["sns_topic"] = sns_topic

    @builtins.property
    def backend_container(self) -> aws_cdk.aws_ecs.ContainerDefinitionOptions:
        '''backend container.'''
        result = self._values.get("backend_container")
        assert result is not None, "Required property 'backend_container' is missing"
        return typing.cast(aws_cdk.aws_ecs.ContainerDefinitionOptions, result)

    @builtins.property
    def backend_container_port_mapping(
        self,
    ) -> typing.List[aws_cdk.aws_ecs.PortMapping]:
        '''container port for the backend container.'''
        result = self._values.get("backend_container_port_mapping")
        assert result is not None, "Required property 'backend_container_port_mapping' is missing"
        return typing.cast(typing.List[aws_cdk.aws_ecs.PortMapping], result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC for the stack.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def aws_cli_layer_arn(self) -> typing.Optional[builtins.str]:
        '''AWS CLI Lambda layer ARN in Serverless App Repository.

        :default: - 'arn:aws:serverlessrepo:us-east-1:903779448426:applications/lambda-layer-awscli'
        '''
        result = self._values.get("aws_cli_layer_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_cli_layer_version(self) -> typing.Optional[builtins.str]:
        '''The version of the Serverless App for AWS CLI Lambda layer.

        :default: - AWSCLI_LAYER_VERSION
        '''
        result = self._values.get("aws_cli_layer_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_scale_in(self) -> typing.Optional[builtins.bool]:
        '''disable scale in.

        :default: - true
        '''
        result = self._values.get("disable_scale_in")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def initial_task_number(self) -> typing.Optional[jsii.Number]:
        '''initial number of tasks for the service.

        :default: - 2
        '''
        result = self._values.get("initial_task_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sns_topic(self) -> typing.Optional[aws_cdk.aws_sns.ITopic]:
        '''SNS Topic to publish the notification.

        :default: - do not publish to SNS
        '''
        result = self._values.get("sns_topic")
        return typing.cast(typing.Optional[aws_cdk.aws_sns.ITopic], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateFastAutoscalerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "FargateFastAutoscaler",
    "FargateFastAutoscalerProps",
]

publication.publish()
