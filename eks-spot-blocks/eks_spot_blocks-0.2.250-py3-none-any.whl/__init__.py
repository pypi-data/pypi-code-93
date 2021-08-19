'''
[![awscdk-jsii-template](https://img.shields.io/badge/built%20with-awscdk--jsii--template-blue)](https://github.com/pahud/awscdk-jsii-template)
[![NPM version](https://badge.fury.io/js/eks-spot-blocks.svg)](https://badge.fury.io/js/eks-spot-blocks)
[![PyPI version](https://badge.fury.io/py/eks-spot-blocks.svg)](https://badge.fury.io/py/eks-spot-blocks)
![Release](https://github.com/pahud/eks-spot-blocks/workflows/Release/badge.svg)

# cdk-eks-spotblocks

`cdk-eks-spotblocks` is a JSII construct library for AWS CDK to provison Amazon EKS cluster with `EC2 Spot Blocks` for defined workloads with the advantages of ensured availability and considerable price reduction for your kubernetes workload.

![](images/pahud_eks-spot2.svg)

## Features

* [x] support the upstream AWS CDK `aws-eks` construct libraries by extending its capabilities
* [x] `addSpotFleet()` to create your spot fleet for your cluster
* [x] define your `blockDuration`, `validFrom` and `validUntil` for fine-graned control
* [x] support any AWS commercial regions which has Amazon EKS and EC2 Spot Block support, including AWS China regions

## Sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import eks_spot_blocks as eksspot
import aws_cdk.core as cdk
import aws_cdk.aws_ec2 as ec2

cluster_stack = eksspot.EksSpotCluster(stack, "Cluster",
    cluster_version=eks.KubernetesVersion.V1_16
)

cluster_stack.add_spot_fleet("FirstFleet",
    block_duration=eksspot.BlockDuration.SIX_HOURS,
    target_capacity=1,
    default_instance_type=ec2.InstanceType("p3.2xlarge"),
    valid_until=cluster_stack.add_hours(Date(), 6).to_iSOString(),
    terminate_instances_with_expiration=True
)

cluster_stack.add_spot_fleet("SecondFleet",
    block_duration=eksspot.BlockDuration.ONE_HOUR,
    target_capacity=2,
    default_instance_type=ec2.InstanceType("c5.large"),
    valid_until=cluster_stack.add_hours(Date(), 1).to_iSOString(),
    terminate_instances_with_expiration=True
)
```

check [eks-spot-blocks-demo](https://github.com/pahud/eks-spot-blocks-demo) for a full AWS CDK demo with this construct library.

## Custom AMI support

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
cluster_stack = EksSpotCluster(stack, "Cluster",
    cluster_version=eks.KubernetesVersion.V1_16,
    custom_ami_id="ami-xxxxxx"
)
```

## FAQ

### Does `eks-spot-blocks` support existing eks clusters created by `eksctl`, `terraform` or any other tools?

No. This construct library does not support existing Amazon EKS clusters. You have to create the cluster as well as the spot fleet altogether in this construct library.

### Can I write the CDK in other languages like `Python` and `Java`?

Not at this moment. But we plan to publish this construct with `JSII` so we can install this library via `npm`, `pypi`, `maven` or `nuget`.

### How much time can I block the spotfleet?

You can block the fleet with hourly increments up to 6 hours.

### What happens after the `blockDuration`?

Spot Blocks ensure the availability of your spot instances during the `blockDuration` and avoid termination during the price disruption. After the `blockDuration`, by default, your spot instances will still be in `running` state but it doesn't ensure the availability, which means it might be terminated anytime after the `blockDuration`.

### Can I terminate the fleet immediately after the `blockDuration` to save the money?

Yes. Basically you can configure `validFrom`, `validUntil` and `terminateInstancesWithExpiration` to achieve this.

However, consider the following scenario

```
<deploy start at 1:00>|--------(one hour)-----------------------|<2:00>
                           |<fleet created at 1:05>--------(one-hour block)-------|<2:05>
```

Your fleet will be terminated at `2:00` rather at `2:05`.

### Are `tains` and `labels` supported?

Yes.

(samples TBD)

### Does it support AWS China regions?

Yes. Including **Beijing**(`cn-north-1`) and **Ningxia**(`cn-northwest-1`).

### How much can I save from the EC2 Spot Block compared to the on-demand?

According to this [document](https://aws.amazon.com/ec2/spot/pricing/?nc1=h_ls)

`Spot Instances are also available to run for a predefined duration – in hourly increments up to six hours in length – at a discount of up to 30-50% compared to On-Demand pricing.`

### Will this library become part of the upstream `aws-eks` construct library?

Probably. As it's still in the preliminary stage, we are still collecting feedbacks from the community to make `eks-spot-blocks` ready for production workloads. Eventually we will commit this feature to the upstream `aws-eks` construct library in AWS CDK through pull requests.
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
import aws_cdk.aws_eks
import aws_cdk.aws_iam
import aws_cdk.core


@jsii.data_type(
    jsii_type="eks-spot-blocks.BaseSpotFleetProps",
    jsii_struct_bases=[aws_cdk.core.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "block_duration": "blockDuration",
        "bootstrap_enabled": "bootstrapEnabled",
        "custom_ami_id": "customAmiId",
        "default_instance_type": "defaultInstanceType",
        "instance_interruption_behavior": "instanceInterruptionBehavior",
        "instance_role": "instanceRole",
        "map_role": "mapRole",
        "target_capacity": "targetCapacity",
        "terminate_instances_with_expiration": "terminateInstancesWithExpiration",
        "valid_from": "validFrom",
        "valid_until": "validUntil",
    },
)
class BaseSpotFleetProps(aws_cdk.core.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        block_duration: typing.Optional["BlockDuration"] = None,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        instance_interruption_behavior: typing.Optional["InstanceInterruptionBehavior"] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        map_role: typing.Optional[builtins.bool] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        terminate_instances_with_expiration: typing.Optional[builtins.bool] = None,
        valid_from: typing.Optional[builtins.str] = None,
        valid_until: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param block_duration: 
        :param bootstrap_enabled: 
        :param custom_ami_id: 
        :param default_instance_type: 
        :param instance_interruption_behavior: 
        :param instance_role: 
        :param map_role: 
        :param target_capacity: 
        :param terminate_instances_with_expiration: 
        :param valid_from: 
        :param valid_until: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region
        if block_duration is not None:
            self._values["block_duration"] = block_duration
        if bootstrap_enabled is not None:
            self._values["bootstrap_enabled"] = bootstrap_enabled
        if custom_ami_id is not None:
            self._values["custom_ami_id"] = custom_ami_id
        if default_instance_type is not None:
            self._values["default_instance_type"] = default_instance_type
        if instance_interruption_behavior is not None:
            self._values["instance_interruption_behavior"] = instance_interruption_behavior
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if map_role is not None:
            self._values["map_role"] = map_role
        if target_capacity is not None:
            self._values["target_capacity"] = target_capacity
        if terminate_instances_with_expiration is not None:
            self._values["terminate_instances_with_expiration"] = terminate_instances_with_expiration
        if valid_from is not None:
            self._values["valid_from"] = valid_from
        if valid_until is not None:
            self._values["valid_until"] = valid_until

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The AWS account ID this resource belongs to.

        :default: - the resource is in the same account as the stack it belongs to
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_from_arn(self) -> typing.Optional[builtins.str]:
        '''ARN to deduce region and account from.

        The ARN is parsed and the account and region are taken from the ARN.
        This should be used for imported resources.

        Cannot be supplied together with either ``account`` or ``region``.

        :default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        '''
        result = self._values.get("environment_from_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def physical_name(self) -> typing.Optional[builtins.str]:
        '''The value passed in by users to the physical name prop of the resource.

        - ``undefined`` implies that a physical name will be allocated by
          CloudFormation during deployment.
        - a concrete value implies a specific physical name
        - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated
          by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation.

        :default: - The physical name will be allocated by CloudFormation at deployment time
        '''
        result = self._values.get("physical_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region this resource belongs to.

        :default: - the resource is in the same region as the stack it belongs to
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_duration(self) -> typing.Optional["BlockDuration"]:
        result = self._values.get("block_duration")
        return typing.cast(typing.Optional["BlockDuration"], result)

    @builtins.property
    def bootstrap_enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("bootstrap_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_ami_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("custom_ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        result = self._values.get("default_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def instance_interruption_behavior(
        self,
    ) -> typing.Optional["InstanceInterruptionBehavior"]:
        result = self._values.get("instance_interruption_behavior")
        return typing.cast(typing.Optional["InstanceInterruptionBehavior"], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], result)

    @builtins.property
    def map_role(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("map_role")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def target_capacity(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("target_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def terminate_instances_with_expiration(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("terminate_instances_with_expiration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def valid_from(self) -> typing.Optional[builtins.str]:
        result = self._values.get("valid_from")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def valid_until(self) -> typing.Optional[builtins.str]:
        result = self._values.get("valid_until")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseSpotFleetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="eks-spot-blocks.BlockDuration")
class BlockDuration(enum.Enum):
    ONE_HOUR = "ONE_HOUR"
    TWO_HOURS = "TWO_HOURS"
    THREE_HOURS = "THREE_HOURS"
    FOUR_HOURS = "FOUR_HOURS"
    FIVE_HOURS = "FIVE_HOURS"
    SIX_HOURS = "SIX_HOURS"


class EksSpotCluster(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="eks-spot-blocks.EksSpotCluster",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster_version: aws_cdk.aws_eks.KubernetesVersion,
        cluster_attributes: typing.Optional[aws_cdk.aws_eks.ClusterAttributes] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional["InstanceInterruptionBehavior"] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        kubectl_enabled: typing.Optional[builtins.bool] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[aws_cdk.core.Environment] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[aws_cdk.core.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_version: 
        :param cluster_attributes: 
        :param custom_ami_id: Specify a custom AMI ID for your spot fleet. By default the Amazon EKS-optimized AMI will be selected. Default: - none
        :param instance_interruption_behavior: 
        :param instance_role: 
        :param kubectl_enabled: 
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        props = EksSpotClusterProps(
            cluster_version=cluster_version,
            cluster_attributes=cluster_attributes,
            custom_ami_id=custom_ami_id,
            instance_interruption_behavior=instance_interruption_behavior,
            instance_role=instance_role,
            kubectl_enabled=kubectl_enabled,
            analytics_reporting=analytics_reporting,
            description=description,
            env=env,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(EksSpotCluster, self, [scope, id, props])

    @jsii.member(jsii_name="addDays")
    def add_days(self, date: datetime.datetime, days: jsii.Number) -> datetime.datetime:
        '''
        :param date: -
        :param days: -
        '''
        return typing.cast(datetime.datetime, jsii.invoke(self, "addDays", [date, days]))

    @jsii.member(jsii_name="addHours")
    def add_hours(
        self,
        date: datetime.datetime,
        hours: jsii.Number,
    ) -> datetime.datetime:
        '''
        :param date: -
        :param hours: -
        '''
        return typing.cast(datetime.datetime, jsii.invoke(self, "addHours", [date, hours]))

    @jsii.member(jsii_name="addMinutes")
    def add_minutes(
        self,
        date: datetime.datetime,
        minutes: jsii.Number,
    ) -> datetime.datetime:
        '''
        :param date: -
        :param minutes: -
        '''
        return typing.cast(datetime.datetime, jsii.invoke(self, "addMinutes", [date, minutes]))

    @jsii.member(jsii_name="addSpotFleet")
    def add_spot_fleet(
        self,
        id: builtins.str,
        *,
        block_duration: typing.Optional[BlockDuration] = None,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        instance_interruption_behavior: typing.Optional["InstanceInterruptionBehavior"] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        map_role: typing.Optional[builtins.bool] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        terminate_instances_with_expiration: typing.Optional[builtins.bool] = None,
        valid_from: typing.Optional[builtins.str] = None,
        valid_until: typing.Optional[builtins.str] = None,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: -
        :param block_duration: 
        :param bootstrap_enabled: 
        :param custom_ami_id: 
        :param default_instance_type: 
        :param instance_interruption_behavior: 
        :param instance_role: 
        :param map_role: 
        :param target_capacity: 
        :param terminate_instances_with_expiration: 
        :param valid_from: 
        :param valid_until: 
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        props = BaseSpotFleetProps(
            block_duration=block_duration,
            bootstrap_enabled=bootstrap_enabled,
            custom_ami_id=custom_ami_id,
            default_instance_type=default_instance_type,
            instance_interruption_behavior=instance_interruption_behavior,
            instance_role=instance_role,
            map_role=map_role,
            target_capacity=target_capacity,
            terminate_instances_with_expiration=terminate_instances_with_expiration,
            valid_from=valid_from,
            valid_until=valid_until,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        return typing.cast(None, jsii.invoke(self, "addSpotFleet", [id, props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        return typing.cast(aws_cdk.aws_eks.Cluster, jsii.get(self, "cluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterVersion")
    def cluster_version(self) -> aws_cdk.aws_eks.KubernetesVersion:
        return typing.cast(aws_cdk.aws_eks.KubernetesVersion, jsii.get(self, "clusterVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="eks-spot-blocks.EksSpotClusterProps",
    jsii_struct_bases=[aws_cdk.core.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "description": "description",
        "env": "env",
        "stack_name": "stackName",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "cluster_version": "clusterVersion",
        "cluster_attributes": "clusterAttributes",
        "custom_ami_id": "customAmiId",
        "instance_interruption_behavior": "instanceInterruptionBehavior",
        "instance_role": "instanceRole",
        "kubectl_enabled": "kubectlEnabled",
    },
)
class EksSpotClusterProps(aws_cdk.core.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[aws_cdk.core.Environment] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[aws_cdk.core.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        cluster_version: aws_cdk.aws_eks.KubernetesVersion,
        cluster_attributes: typing.Optional[aws_cdk.aws_eks.ClusterAttributes] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional["InstanceInterruptionBehavior"] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        kubectl_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param cluster_version: 
        :param cluster_attributes: 
        :param custom_ami_id: Specify a custom AMI ID for your spot fleet. By default the Amazon EKS-optimized AMI will be selected. Default: - none
        :param instance_interruption_behavior: 
        :param instance_role: 
        :param kubectl_enabled: 
        '''
        if isinstance(env, dict):
            env = aws_cdk.core.Environment(**env)
        if isinstance(cluster_attributes, dict):
            cluster_attributes = aws_cdk.aws_eks.ClusterAttributes(**cluster_attributes)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_version": cluster_version,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if cluster_attributes is not None:
            self._values["cluster_attributes"] = cluster_attributes
        if custom_ami_id is not None:
            self._values["custom_ami_id"] = custom_ami_id
        if instance_interruption_behavior is not None:
            self._values["instance_interruption_behavior"] = instance_interruption_behavior
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if kubectl_enabled is not None:
            self._values["kubectl_enabled"] = kubectl_enabled

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[aws_cdk.core.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            # Use a concrete account and region to deploy this stack to:
            # `.account` and `.region` will simply return these values.
            Stack(app, "Stack1",
                env={
                    "account": "123456789012",
                    "region": "us-east-1"
                }
            )
            
            # Use the CLI's current credentials to determine the target environment:
            # `.account` and `.region` will reflect the account+region the CLI
            # is configured to use (based on the user CLI credentials)
            Stack(app, "Stack2",
                env={
                    "account": process.env.CDK_DEFAULT_ACCOUNT,
                    "region": process.env.CDK_DEFAULT_REGION
                }
            )
            
            # Define multiple stacks stage associated with an environment
            my_stage = Stage(app, "MyStage",
                env={
                    "account": "123456789012",
                    "region": "us-east-1"
                }
            )
            
            # both of these stacks will use the stage's account/region:
            # `.account` and `.region` will resolve to the concrete values as above
            MyStack(my_stage, "Stack1")
            YourStack(my_stage, "Stack2")
            
            # Define an environment-agnostic stack:
            # `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            # which will only resolve to actual values by CloudFormation during deployment.
            MyStack(app, "Stack1")
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[aws_cdk.core.Environment], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[aws_cdk.core.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        :default:

        - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag
        is set, ``LegacyStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[aws_cdk.core.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cluster_version(self) -> aws_cdk.aws_eks.KubernetesVersion:
        result = self._values.get("cluster_version")
        assert result is not None, "Required property 'cluster_version' is missing"
        return typing.cast(aws_cdk.aws_eks.KubernetesVersion, result)

    @builtins.property
    def cluster_attributes(self) -> typing.Optional[aws_cdk.aws_eks.ClusterAttributes]:
        result = self._values.get("cluster_attributes")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.ClusterAttributes], result)

    @builtins.property
    def custom_ami_id(self) -> typing.Optional[builtins.str]:
        '''Specify a custom AMI ID for your spot fleet.

        By default the Amazon EKS-optimized
        AMI will be selected.

        :default: - none
        '''
        result = self._values.get("custom_ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_interruption_behavior(
        self,
    ) -> typing.Optional["InstanceInterruptionBehavior"]:
        result = self._values.get("instance_interruption_behavior")
        return typing.cast(typing.Optional["InstanceInterruptionBehavior"], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def kubectl_enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("kubectl_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EksSpotClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="eks-spot-blocks.ILaunchtemplate")
class ILaunchtemplate(typing_extensions.Protocol):
    @jsii.member(jsii_name="bind")
    def bind(self, spotfleet: "SpotFleet") -> "SpotFleetLaunchTemplateConfig":
        '''
        :param spotfleet: -
        '''
        ...


class _ILaunchtemplateProxy:
    __jsii_type__: typing.ClassVar[str] = "eks-spot-blocks.ILaunchtemplate"

    @jsii.member(jsii_name="bind")
    def bind(self, spotfleet: "SpotFleet") -> "SpotFleetLaunchTemplateConfig":
        '''
        :param spotfleet: -
        '''
        return typing.cast("SpotFleetLaunchTemplateConfig", jsii.invoke(self, "bind", [spotfleet]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILaunchtemplate).__jsii_proxy_class__ = lambda : _ILaunchtemplateProxy


@jsii.enum(jsii_type="eks-spot-blocks.InstanceInterruptionBehavior")
class InstanceInterruptionBehavior(enum.Enum):
    HIBERNATE = "HIBERNATE"
    STOP = "STOP"
    TERMINATE = "TERMINATE"


@jsii.implements(ILaunchtemplate)
class LaunchTemplate(
    metaclass=jsii.JSIIMeta,
    jsii_type="eks-spot-blocks.LaunchTemplate",
):
    def __init__(self) -> None:
        jsii.create(LaunchTemplate, self, [])

    @jsii.member(jsii_name="bind")
    def bind(self, spotfleet: "SpotFleet") -> "SpotFleetLaunchTemplateConfig":
        '''
        :param spotfleet: -
        '''
        return typing.cast("SpotFleetLaunchTemplateConfig", jsii.invoke(self, "bind", [spotfleet]))


class SpotFleet(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="eks-spot-blocks.SpotFleet",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: EksSpotCluster,
        launch_template: typing.Optional[ILaunchtemplate] = None,
        block_duration: typing.Optional[BlockDuration] = None,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        map_role: typing.Optional[builtins.bool] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        terminate_instances_with_expiration: typing.Optional[builtins.bool] = None,
        valid_from: typing.Optional[builtins.str] = None,
        valid_until: typing.Optional[builtins.str] = None,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param launch_template: 
        :param block_duration: 
        :param bootstrap_enabled: 
        :param custom_ami_id: 
        :param default_instance_type: 
        :param instance_interruption_behavior: 
        :param instance_role: 
        :param map_role: 
        :param target_capacity: 
        :param terminate_instances_with_expiration: 
        :param valid_from: 
        :param valid_until: 
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        props = SpotFleetProps(
            cluster=cluster,
            launch_template=launch_template,
            block_duration=block_duration,
            bootstrap_enabled=bootstrap_enabled,
            custom_ami_id=custom_ami_id,
            default_instance_type=default_instance_type,
            instance_interruption_behavior=instance_interruption_behavior,
            instance_role=instance_role,
            map_role=map_role,
            target_capacity=target_capacity,
            terminate_instances_with_expiration=terminate_instances_with_expiration,
            valid_from=valid_from,
            valid_until=valid_until,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(SpotFleet, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterStack")
    def cluster_stack(self) -> EksSpotCluster:
        return typing.cast(EksSpotCluster, jsii.get(self, "clusterStack"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultInstanceType")
    def default_instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        return typing.cast(aws_cdk.aws_ec2.InstanceType, jsii.get(self, "defaultInstanceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> aws_cdk.aws_iam.IRole:
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "instanceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplate")
    def launch_template(self) -> ILaunchtemplate:
        return typing.cast(ILaunchtemplate, jsii.get(self, "launchTemplate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotFleetId")
    def spot_fleet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotFleetId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetCapacity")
    def target_capacity(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetCapacity"))


@jsii.data_type(
    jsii_type="eks-spot-blocks.SpotFleetLaunchTemplateConfig",
    jsii_struct_bases=[],
    name_mapping={"launch_template": "launchTemplate", "spotfleet": "spotfleet"},
)
class SpotFleetLaunchTemplateConfig:
    def __init__(
        self,
        *,
        launch_template: ILaunchtemplate,
        spotfleet: SpotFleet,
    ) -> None:
        '''
        :param launch_template: 
        :param spotfleet: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "launch_template": launch_template,
            "spotfleet": spotfleet,
        }

    @builtins.property
    def launch_template(self) -> ILaunchtemplate:
        result = self._values.get("launch_template")
        assert result is not None, "Required property 'launch_template' is missing"
        return typing.cast(ILaunchtemplate, result)

    @builtins.property
    def spotfleet(self) -> SpotFleet:
        result = self._values.get("spotfleet")
        assert result is not None, "Required property 'spotfleet' is missing"
        return typing.cast(SpotFleet, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpotFleetLaunchTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="eks-spot-blocks.SpotFleetProps",
    jsii_struct_bases=[BaseSpotFleetProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "block_duration": "blockDuration",
        "bootstrap_enabled": "bootstrapEnabled",
        "custom_ami_id": "customAmiId",
        "default_instance_type": "defaultInstanceType",
        "instance_interruption_behavior": "instanceInterruptionBehavior",
        "instance_role": "instanceRole",
        "map_role": "mapRole",
        "target_capacity": "targetCapacity",
        "terminate_instances_with_expiration": "terminateInstancesWithExpiration",
        "valid_from": "validFrom",
        "valid_until": "validUntil",
        "cluster": "cluster",
        "launch_template": "launchTemplate",
    },
)
class SpotFleetProps(BaseSpotFleetProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        block_duration: typing.Optional[BlockDuration] = None,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        map_role: typing.Optional[builtins.bool] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        terminate_instances_with_expiration: typing.Optional[builtins.bool] = None,
        valid_from: typing.Optional[builtins.str] = None,
        valid_until: typing.Optional[builtins.str] = None,
        cluster: EksSpotCluster,
        launch_template: typing.Optional[ILaunchtemplate] = None,
    ) -> None:
        '''
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param block_duration: 
        :param bootstrap_enabled: 
        :param custom_ami_id: 
        :param default_instance_type: 
        :param instance_interruption_behavior: 
        :param instance_role: 
        :param map_role: 
        :param target_capacity: 
        :param terminate_instances_with_expiration: 
        :param valid_from: 
        :param valid_until: 
        :param cluster: 
        :param launch_template: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
        }
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region
        if block_duration is not None:
            self._values["block_duration"] = block_duration
        if bootstrap_enabled is not None:
            self._values["bootstrap_enabled"] = bootstrap_enabled
        if custom_ami_id is not None:
            self._values["custom_ami_id"] = custom_ami_id
        if default_instance_type is not None:
            self._values["default_instance_type"] = default_instance_type
        if instance_interruption_behavior is not None:
            self._values["instance_interruption_behavior"] = instance_interruption_behavior
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if map_role is not None:
            self._values["map_role"] = map_role
        if target_capacity is not None:
            self._values["target_capacity"] = target_capacity
        if terminate_instances_with_expiration is not None:
            self._values["terminate_instances_with_expiration"] = terminate_instances_with_expiration
        if valid_from is not None:
            self._values["valid_from"] = valid_from
        if valid_until is not None:
            self._values["valid_until"] = valid_until
        if launch_template is not None:
            self._values["launch_template"] = launch_template

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The AWS account ID this resource belongs to.

        :default: - the resource is in the same account as the stack it belongs to
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_from_arn(self) -> typing.Optional[builtins.str]:
        '''ARN to deduce region and account from.

        The ARN is parsed and the account and region are taken from the ARN.
        This should be used for imported resources.

        Cannot be supplied together with either ``account`` or ``region``.

        :default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        '''
        result = self._values.get("environment_from_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def physical_name(self) -> typing.Optional[builtins.str]:
        '''The value passed in by users to the physical name prop of the resource.

        - ``undefined`` implies that a physical name will be allocated by
          CloudFormation during deployment.
        - a concrete value implies a specific physical name
        - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated
          by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation.

        :default: - The physical name will be allocated by CloudFormation at deployment time
        '''
        result = self._values.get("physical_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region this resource belongs to.

        :default: - the resource is in the same region as the stack it belongs to
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_duration(self) -> typing.Optional[BlockDuration]:
        result = self._values.get("block_duration")
        return typing.cast(typing.Optional[BlockDuration], result)

    @builtins.property
    def bootstrap_enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("bootstrap_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_ami_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("custom_ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        result = self._values.get("default_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def instance_interruption_behavior(
        self,
    ) -> typing.Optional[InstanceInterruptionBehavior]:
        result = self._values.get("instance_interruption_behavior")
        return typing.cast(typing.Optional[InstanceInterruptionBehavior], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], result)

    @builtins.property
    def map_role(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("map_role")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def target_capacity(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("target_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def terminate_instances_with_expiration(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("terminate_instances_with_expiration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def valid_from(self) -> typing.Optional[builtins.str]:
        result = self._values.get("valid_from")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def valid_until(self) -> typing.Optional[builtins.str]:
        result = self._values.get("valid_until")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster(self) -> EksSpotCluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(EksSpotCluster, result)

    @builtins.property
    def launch_template(self) -> typing.Optional[ILaunchtemplate]:
        result = self._values.get("launch_template")
        return typing.cast(typing.Optional[ILaunchtemplate], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpotFleetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BaseSpotFleetProps",
    "BlockDuration",
    "EksSpotCluster",
    "EksSpotClusterProps",
    "ILaunchtemplate",
    "InstanceInterruptionBehavior",
    "LaunchTemplate",
    "SpotFleet",
    "SpotFleetLaunchTemplateConfig",
    "SpotFleetProps",
]

publication.publish()
