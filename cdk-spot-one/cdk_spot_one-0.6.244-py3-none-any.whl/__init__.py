'''
[![awscdk-jsii-template](https://img.shields.io/badge/built%20with-awscdk--jsii--template-blue)](https://github.com/pahud/awscdk-jsii-template)
[![NPM version](https://badge.fury.io/js/cdk-spot-one.svg)](https://badge.fury.io/js/cdk-spot-one)
[![PyPI version](https://badge.fury.io/py/cdk-spot-one.svg)](https://badge.fury.io/py/cdk-spot-one)
![Release](https://github.com/pahud/cdk-spot-one/workflows/Release/badge.svg)

# cdk-spot-one

One spot instance with EIP and defined duration. No interruption.

# Why

Sometimes we need an Amazon EC2 instance with static fixed IP for testing or development purpose for a duration of
time(probably hours). We need to make sure during this time, no interruption will occur and we don't want to pay
for on-demand rate. `cdk-spot-one` helps you reserve one single spot instance with pre-allocated or new
Elastic IP addresses(EIP) with defined `blockDuration`, during which time the spot instance will be secured with no spot interruption.

Behind the scene, `cdk-spot-one` provisions a spot fleet with capacity of single instance for you and it associates the EIP with this instance. The spot fleet is reserved as spot block with `blockDuration` from one hour up to six hours to ensure the high availability for your spot instance.

Multiple spot instances are possible by simply specifying the `targetCapacity` construct property, but we only associate the EIP with the first spot instance at this moment.

Enjoy your highly durable one spot instance with AWS CDK!

# Constructs

This library provides two major constructs:

## SpotInstance

* Create a spot instance **without** any fleet
* Does **NOT** support [Spot Block](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-requests.html#fixed-duration-spot-instances)
* Support `stop` or `hibernate` instance

Scenario: To leverage the `stop` or `hibernate` capabilities of the spot instance to persist the data in the ebs volume.

## SpotFleet

* Create a spot instance with a [Spot Fleet](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-fleet.html)
* Support [Spot Block](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-requests.html#fixed-duration-spot-instances)
* Does **NOT** support `stop` or `hibernate` instance

Scenario: To ensure the availability with no disruption with defined period up to 6 hours.

# Sample

## SpotInstance

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_spot_one import SpotInstance

# Default use Amazon Linux 2
SpotInstance(stack, "SpotInstance")

# Custom Id use Ubuntu 20.04 Arm64 Server.
SpotInstance(stack, "SpotInstanceUbuntu",
    vpc=vpc,
    custom_ami_id="ami-076d8ebdd0e1ec091", # ubuntu ami id.
    default_instance_type=InstanceType("t4g.medium"),
    key_name=key_name,
    block_device_mappings=[{"device_name": "/dev/sda1", "ebs": {"volume_size": 20}}],
    additional_user_data=["curl -fsSL https://get.docker.com -o get-docker.sh", "sudo sh get-docker.sh"]
)
```

## SpotFleet

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_spot_one import SpotFleet

# create the first fleet for one hour and associate with our existing EIP
fleet = SpotFleet(stack, "SpotFleet")

# configure the expiration after 1 hour
fleet.expire_after(Duration.hours(1))

# create the 2nd fleet with single Gravition 2 instance for 6 hours and associate with new EIP
fleet2 = SpotFleet(stack, "SpotFleet2",
    block_duration=BlockDuration.SIX_HOURS,
    eip_allocation_id="eipalloc-0d1bc6d85895a5410",
    default_instance_type=InstanceType("c6g.large"),
    vpc=fleet.vpc
)
# configure the expiration after 6 hours
fleet2.expire_after(Duration.hours(6))

# print the instanceId from each spot fleet
CfnOutput(stack, "SpotFleetInstanceId", value=fleet.instance_id)
CfnOutput(stack, "SpotFleet2InstanceId", value=fleet2.instance_id)
```

# Create spot instances without duration block

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
fleet = SpotFleet(stack, "SpotFleet",
    block_duration=BlockDuration.NONE
)
```

NOTE: This kind of spot instance will be interrupted by AWS. However the fleet is using type [maintain](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-fleet.html#spot-fleet-allocation-strategy), the fleet can be refulfilled.

# ARM64 and Graviton 2 support

`cdk-spot-one` selects the latest Amazon Linux 2 AMI for your `ARM64` instances. Simply select the instance types with the `defaultInstanceType` property and the `SpotFleet` will auto configure correct AMI for the instance.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
defaultInstanceType: new InstanceType('c6g.large')
```

# ECS Cluster support

See https://github.com/pahud/cdk-spot-one/issues/270#issuecomment-877152685

# SSH connect

By default the `cdk-spot-one` does not bind any SSH public key for you on the instance. You are encouraged to use `ec2-instance-connect` to send your public key from local followed by one-time SSH connect.

For example:

```sh
pubkey="$HOME/.ssh/aws_2020_id_rsa.pub"
echo "sending public key to ${instanceId}"
aws ec2-instance-connect send-ssh-public-key --instance-id ${instanceId} --instance-os-user ec2-user \
--ssh-public-key file://${pubkey} --availability-zone ${az}
```

## npx ec2-connect INSTANCE_ID

To connect to the instance, run `npx ec2-connect` as below:

```sh
$ npx ec2-connect i-01f827ab9de7b93a9
```

or

```sh
$ npx ec2-connect i-01f827ab9de7b93a9 ~/.ssh/other_public_key_path
```

If you are using different SSH public key(default is ~/.ssh/id_rsa.pub)
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
import aws_cdk.aws_iam
import aws_cdk.core
import constructs


@jsii.enum(jsii_type="cdk-spot-one.BlockDuration")
class BlockDuration(enum.Enum):
    ONE_HOUR = "ONE_HOUR"
    TWO_HOURS = "TWO_HOURS"
    THREE_HOURS = "THREE_HOURS"
    FOUR_HOURS = "FOUR_HOURS"
    FIVE_HOURS = "FIVE_HOURS"
    SIX_HOURS = "SIX_HOURS"
    NONE = "NONE"


@jsii.interface(jsii_type="cdk-spot-one.ILaunchtemplate")
class ILaunchtemplate(typing_extensions.Protocol):
    @jsii.member(jsii_name="bind")
    def bind(self, spotfleet: "SpotFleet") -> "SpotFleetLaunchTemplateConfig":
        '''
        :param spotfleet: -
        '''
        ...


class _ILaunchtemplateProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-spot-one.ILaunchtemplate"

    @jsii.member(jsii_name="bind")
    def bind(self, spotfleet: "SpotFleet") -> "SpotFleetLaunchTemplateConfig":
        '''
        :param spotfleet: -
        '''
        return typing.cast("SpotFleetLaunchTemplateConfig", jsii.invoke(self, "bind", [spotfleet]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILaunchtemplate).__jsii_proxy_class__ = lambda : _ILaunchtemplateProxy


@jsii.enum(jsii_type="cdk-spot-one.InstanceInterruptionBehavior")
class InstanceInterruptionBehavior(enum.Enum):
    HIBERNATE = "HIBERNATE"
    STOP = "STOP"
    TERMINATE = "TERMINATE"


@jsii.implements(ILaunchtemplate)
class LaunchTemplate(metaclass=jsii.JSIIMeta, jsii_type="cdk-spot-one.LaunchTemplate"):
    def __init__(self) -> None:
        jsii.create(LaunchTemplate, self, [])

    @jsii.member(jsii_name="bind")
    def bind(self, spotfleet: "SpotFleet") -> "SpotFleetLaunchTemplateConfig":
        '''
        :param spotfleet: -
        '''
        return typing.cast("SpotFleetLaunchTemplateConfig", jsii.invoke(self, "bind", [spotfleet]))


@jsii.data_type(
    jsii_type="cdk-spot-one.LaunchTemplateProps",
    jsii_struct_bases=[],
    name_mapping={
        "block_device_mappings": "blockDeviceMappings",
        "default_instance_type": "defaultInstanceType",
        "iam_instance_profile": "iamInstanceProfile",
        "image_id": "imageId",
        "instance_market_options": "instanceMarketOptions",
        "key_name": "keyName",
        "security_group": "securityGroup",
        "user_data": "userData",
    },
)
class LaunchTemplateProps:
    def __init__(
        self,
        *,
        block_device_mappings: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        iam_instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        image_id: typing.Optional[builtins.str] = None,
        instance_market_options: typing.Optional[aws_cdk.aws_ec2.CfnLaunchTemplate.InstanceMarketOptionsProperty] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
    ) -> None:
        '''
        :param block_device_mappings: blockDeviceMappings for config instance. Default: - from ami config.
        :param default_instance_type: 
        :param iam_instance_profile: 
        :param image_id: 
        :param instance_market_options: 
        :param key_name: 
        :param security_group: 
        :param user_data: 
        '''
        if isinstance(instance_market_options, dict):
            instance_market_options = aws_cdk.aws_ec2.CfnLaunchTemplate.InstanceMarketOptionsProperty(**instance_market_options)
        self._values: typing.Dict[str, typing.Any] = {}
        if block_device_mappings is not None:
            self._values["block_device_mappings"] = block_device_mappings
        if default_instance_type is not None:
            self._values["default_instance_type"] = default_instance_type
        if iam_instance_profile is not None:
            self._values["iam_instance_profile"] = iam_instance_profile
        if image_id is not None:
            self._values["image_id"] = image_id
        if instance_market_options is not None:
            self._values["instance_market_options"] = instance_market_options
        if key_name is not None:
            self._values["key_name"] = key_name
        if security_group is not None:
            self._values["security_group"] = security_group
        if user_data is not None:
            self._values["user_data"] = user_data

    @builtins.property
    def block_device_mappings(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]]:
        '''blockDeviceMappings for config instance.

        :default: - from ami config.
        '''
        result = self._values.get("block_device_mappings")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]], result)

    @builtins.property
    def default_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        result = self._values.get("default_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def iam_instance_profile(
        self,
    ) -> typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile]:
        result = self._values.get("iam_instance_profile")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile], result)

    @builtins.property
    def image_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("image_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_market_options(
        self,
    ) -> typing.Optional[aws_cdk.aws_ec2.CfnLaunchTemplate.InstanceMarketOptionsProperty]:
        result = self._values.get("instance_market_options")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.CfnLaunchTemplate.InstanceMarketOptionsProperty], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def user_data(self) -> typing.Optional[aws_cdk.aws_ec2.UserData]:
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.UserData], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LaunchTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LaunchTemplateResource(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-spot-one.LaunchTemplateResource",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        block_device_mappings: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        iam_instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        image_id: typing.Optional[builtins.str] = None,
        instance_market_options: typing.Optional[aws_cdk.aws_ec2.CfnLaunchTemplate.InstanceMarketOptionsProperty] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param block_device_mappings: blockDeviceMappings for config instance. Default: - from ami config.
        :param default_instance_type: 
        :param iam_instance_profile: 
        :param image_id: 
        :param instance_market_options: 
        :param key_name: 
        :param security_group: 
        :param user_data: 
        '''
        props = LaunchTemplateProps(
            block_device_mappings=block_device_mappings,
            default_instance_type=default_instance_type,
            iam_instance_profile=iam_instance_profile,
            image_id=image_id,
            instance_market_options=instance_market_options,
            key_name=key_name,
            security_group=security_group,
            user_data=user_data,
        )

        jsii.create(LaunchTemplateResource, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultInstanceType")
    def default_instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        return typing.cast(aws_cdk.aws_ec2.InstanceType, jsii.get(self, "defaultInstanceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> aws_cdk.aws_ec2.CfnLaunchTemplate:
        return typing.cast(aws_cdk.aws_ec2.CfnLaunchTemplate, jsii.get(self, "resource"))


@jsii.enum(jsii_type="cdk-spot-one.NodeType")
class NodeType(enum.Enum):
    '''Whether the worker nodes should support GPU or just standard instances.'''

    STANDARD = "STANDARD"
    '''Standard instances.'''
    GPU = "GPU"
    '''GPU instances.'''
    INFERENTIA = "INFERENTIA"
    '''Inferentia instances.'''
    ARM = "ARM"
    '''ARM instances.'''


@jsii.data_type(
    jsii_type="cdk-spot-one.SpotFleetLaunchTemplateConfig",
    jsii_struct_bases=[],
    name_mapping={"launch_template": "launchTemplate", "spotfleet": "spotfleet"},
)
class SpotFleetLaunchTemplateConfig:
    def __init__(
        self,
        *,
        launch_template: ILaunchtemplate,
        spotfleet: "SpotFleet",
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
    def spotfleet(self) -> "SpotFleet":
        result = self._values.get("spotfleet")
        assert result is not None, "Required property 'spotfleet' is missing"
        return typing.cast("SpotFleet", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpotFleetLaunchTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SpotOne(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-spot-one.SpotOne",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        additional_user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        assign_eip: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        eip_allocation_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param additional_user_data: Additional commands for user data. Default: - no additional user data
        :param assign_eip: Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined. Default: true
        :param custom_ami_id: custom AMI ID. Default: - The latest Amaozn Linux 2 AMI ID
        :param default_instance_type: default EC2 instance type. Default: - t3.large
        :param ebs_volume_size: default EBS volume size for the spot instance. Default: 60;
        :param eip_allocation_id: Allocation ID for your existing Elastic IP Address.
        :param instance_interruption_behavior: The behavior when a Spot Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE
        :param instance_profile: instance profile for the resource. Default: - create a new one
        :param instance_role: IAM role for the spot instance.
        :param key_name: SSH key name. Default: - no ssh key will be assigned
        :param security_group: Security group for the spot fleet. Default: - allows TCP 22 SSH ingress rule
        :param target_capacity: number of the target capacity. Default: - 1
        :param vpc: VPC for the spot fleet. Default: - new VPC will be created
        :param vpc_subnet: VPC subnet for the spot fleet. Default: - public subnet
        '''
        props = SpotOneProps(
            additional_user_data=additional_user_data,
            assign_eip=assign_eip,
            custom_ami_id=custom_ami_id,
            default_instance_type=default_instance_type,
            ebs_volume_size=ebs_volume_size,
            eip_allocation_id=eip_allocation_id,
            instance_interruption_behavior=instance_interruption_behavior,
            instance_profile=instance_profile,
            instance_role=instance_role,
            key_name=key_name,
            security_group=security_group,
            target_capacity=target_capacity,
            vpc=vpc,
            vpc_subnet=vpc_subnet,
        )

        jsii.create(SpotOne, self, [scope, id, props])

    @jsii.member(jsii_name="associateEip")
    def _associate_eip(
        self,
        *,
        additional_user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        assign_eip: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        eip_allocation_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param additional_user_data: Additional commands for user data. Default: - no additional user data
        :param assign_eip: Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined. Default: true
        :param custom_ami_id: custom AMI ID. Default: - The latest Amaozn Linux 2 AMI ID
        :param default_instance_type: default EC2 instance type. Default: - t3.large
        :param ebs_volume_size: default EBS volume size for the spot instance. Default: 60;
        :param eip_allocation_id: Allocation ID for your existing Elastic IP Address.
        :param instance_interruption_behavior: The behavior when a Spot Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE
        :param instance_profile: instance profile for the resource. Default: - create a new one
        :param instance_role: IAM role for the spot instance.
        :param key_name: SSH key name. Default: - no ssh key will be assigned
        :param security_group: Security group for the spot fleet. Default: - allows TCP 22 SSH ingress rule
        :param target_capacity: number of the target capacity. Default: - 1
        :param vpc: VPC for the spot fleet. Default: - new VPC will be created
        :param vpc_subnet: VPC subnet for the spot fleet. Default: - public subnet
        '''
        props = SpotOneProps(
            additional_user_data=additional_user_data,
            assign_eip=assign_eip,
            custom_ami_id=custom_ami_id,
            default_instance_type=default_instance_type,
            ebs_volume_size=ebs_volume_size,
            eip_allocation_id=eip_allocation_id,
            instance_interruption_behavior=instance_interruption_behavior,
            instance_profile=instance_profile,
            instance_role=instance_role,
            key_name=key_name,
            security_group=security_group,
            target_capacity=target_capacity,
            vpc=vpc,
            vpc_subnet=vpc_subnet,
        )

        return typing.cast(None, jsii.invoke(self, "associateEip", [props]))

    @jsii.member(jsii_name="createInstanceProfile")
    def _create_instance_profile(
        self,
        role: aws_cdk.aws_iam.IRole,
    ) -> aws_cdk.aws_iam.CfnInstanceProfile:
        '''
        :param role: -
        '''
        return typing.cast(aws_cdk.aws_iam.CfnInstanceProfile, jsii.invoke(self, "createInstanceProfile", [role]))

    @jsii.member(jsii_name="createInstanceRole")
    def _create_instance_role(self) -> aws_cdk.aws_iam.IRole:
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.invoke(self, "createInstanceRole", []))

    @jsii.member(jsii_name="createSecurityGroup")
    def _create_security_group(self) -> aws_cdk.aws_ec2.SecurityGroup:
        return typing.cast(aws_cdk.aws_ec2.SecurityGroup, jsii.invoke(self, "createSecurityGroup", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultInstanceType")
    def default_instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        return typing.cast(aws_cdk.aws_ec2.InstanceType, jsii.get(self, "defaultInstanceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSecurityGroup")
    def default_security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''The default security group of the instance, which only allows TCP 22 SSH ingress rule.'''
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, jsii.get(self, "defaultSecurityGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userData")
    def user_data(self) -> aws_cdk.aws_ec2.UserData:
        return typing.cast(aws_cdk.aws_ec2.UserData, jsii.get(self, "userData"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfile")
    def _instance_profile(self) -> typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile]:
        return typing.cast(typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile], jsii.get(self, "instanceProfile"))

    @_instance_profile.setter
    def _instance_profile(
        self,
        value: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile],
    ) -> None:
        jsii.set(self, "instanceProfile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRole")
    def _instance_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], jsii.get(self, "instanceRole"))

    @_instance_role.setter
    def _instance_role(self, value: typing.Optional[aws_cdk.aws_iam.IRole]) -> None:
        jsii.set(self, "instanceRole", value)


class _SpotOneProxy(SpotOne):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, SpotOne).__jsii_proxy_class__ = lambda : _SpotOneProxy


@jsii.data_type(
    jsii_type="cdk-spot-one.SpotOneProps",
    jsii_struct_bases=[],
    name_mapping={
        "additional_user_data": "additionalUserData",
        "assign_eip": "assignEip",
        "custom_ami_id": "customAmiId",
        "default_instance_type": "defaultInstanceType",
        "ebs_volume_size": "ebsVolumeSize",
        "eip_allocation_id": "eipAllocationId",
        "instance_interruption_behavior": "instanceInterruptionBehavior",
        "instance_profile": "instanceProfile",
        "instance_role": "instanceRole",
        "key_name": "keyName",
        "security_group": "securityGroup",
        "target_capacity": "targetCapacity",
        "vpc": "vpc",
        "vpc_subnet": "vpcSubnet",
    },
)
class SpotOneProps:
    def __init__(
        self,
        *,
        additional_user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        assign_eip: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        eip_allocation_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param additional_user_data: Additional commands for user data. Default: - no additional user data
        :param assign_eip: Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined. Default: true
        :param custom_ami_id: custom AMI ID. Default: - The latest Amaozn Linux 2 AMI ID
        :param default_instance_type: default EC2 instance type. Default: - t3.large
        :param ebs_volume_size: default EBS volume size for the spot instance. Default: 60;
        :param eip_allocation_id: Allocation ID for your existing Elastic IP Address.
        :param instance_interruption_behavior: The behavior when a Spot Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE
        :param instance_profile: instance profile for the resource. Default: - create a new one
        :param instance_role: IAM role for the spot instance.
        :param key_name: SSH key name. Default: - no ssh key will be assigned
        :param security_group: Security group for the spot fleet. Default: - allows TCP 22 SSH ingress rule
        :param target_capacity: number of the target capacity. Default: - 1
        :param vpc: VPC for the spot fleet. Default: - new VPC will be created
        :param vpc_subnet: VPC subnet for the spot fleet. Default: - public subnet
        '''
        if isinstance(vpc_subnet, dict):
            vpc_subnet = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnet)
        self._values: typing.Dict[str, typing.Any] = {}
        if additional_user_data is not None:
            self._values["additional_user_data"] = additional_user_data
        if assign_eip is not None:
            self._values["assign_eip"] = assign_eip
        if custom_ami_id is not None:
            self._values["custom_ami_id"] = custom_ami_id
        if default_instance_type is not None:
            self._values["default_instance_type"] = default_instance_type
        if ebs_volume_size is not None:
            self._values["ebs_volume_size"] = ebs_volume_size
        if eip_allocation_id is not None:
            self._values["eip_allocation_id"] = eip_allocation_id
        if instance_interruption_behavior is not None:
            self._values["instance_interruption_behavior"] = instance_interruption_behavior
        if instance_profile is not None:
            self._values["instance_profile"] = instance_profile
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if key_name is not None:
            self._values["key_name"] = key_name
        if security_group is not None:
            self._values["security_group"] = security_group
        if target_capacity is not None:
            self._values["target_capacity"] = target_capacity
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnet is not None:
            self._values["vpc_subnet"] = vpc_subnet

    @builtins.property
    def additional_user_data(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional commands for user data.

        :default: - no additional user data
        '''
        result = self._values.get("additional_user_data")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def assign_eip(self) -> typing.Optional[builtins.bool]:
        '''Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined.

        :default: true
        '''
        result = self._values.get("assign_eip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_ami_id(self) -> typing.Optional[builtins.str]:
        '''custom AMI ID.

        :default: - The latest Amaozn Linux 2 AMI ID
        '''
        result = self._values.get("custom_ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''default EC2 instance type.

        :default: - t3.large
        '''
        result = self._values.get("default_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def ebs_volume_size(self) -> typing.Optional[jsii.Number]:
        '''default EBS volume size for the spot instance.

        :default: 60;
        '''
        result = self._values.get("ebs_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def eip_allocation_id(self) -> typing.Optional[builtins.str]:
        '''Allocation ID for your existing Elastic IP Address.

        :defalt: new EIP and its association will be created for the first instance in this spot fleet
        '''
        result = self._values.get("eip_allocation_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_interruption_behavior(
        self,
    ) -> typing.Optional[InstanceInterruptionBehavior]:
        '''The behavior when a Spot Instance is interrupted.

        :default: - InstanceInterruptionBehavior.TERMINATE
        '''
        result = self._values.get("instance_interruption_behavior")
        return typing.cast(typing.Optional[InstanceInterruptionBehavior], result)

    @builtins.property
    def instance_profile(self) -> typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile]:
        '''instance profile for the resource.

        :default: - create a new one
        '''
        result = self._values.get("instance_profile")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''IAM role for the spot instance.'''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''SSH key name.

        :default: - no ssh key will be assigned
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.SecurityGroup]:
        '''Security group for the spot fleet.

        :default: - allows TCP 22 SSH ingress rule
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SecurityGroup], result)

    @builtins.property
    def target_capacity(self) -> typing.Optional[jsii.Number]:
        '''number of the target capacity.

        :default: - 1
        '''
        result = self._values.get("target_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC for the spot fleet.

        :default: - new VPC will be created
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnet(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnet for the spot fleet.

        :default: - public subnet
        '''
        result = self._values.get("vpc_subnet")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpotOneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VpcProvider(
    aws_cdk.core.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-spot-one.VpcProvider",
):
    def __init__(
        self,
        scope: typing.Optional[constructs.Construct] = None,
        id: typing.Optional[builtins.str] = None,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[aws_cdk.core.Environment] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[aws_cdk.core.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Creates a new stack.

        :param scope: Parent of this stack, usually an ``App`` or a ``Stage``, but could be any construct.
        :param id: The construct ID of this stack. If ``stackName`` is not explicitly defined, this id (and any parent IDs) will be used to determine the physical ID of the stack.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        props = aws_cdk.core.StackProps(
            analytics_reporting=analytics_reporting,
            description=description,
            env=env,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(VpcProvider, self, [scope, id, props])

    @jsii.member(jsii_name="getOrCreate") # type: ignore[misc]
    @builtins.classmethod
    def get_or_create(cls, scope: aws_cdk.core.Construct) -> aws_cdk.aws_ec2.IVpc:
        '''
        :param scope: -
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.sinvoke(cls, "getOrCreate", [scope]))


@jsii.data_type(
    jsii_type="cdk-spot-one.BaseSpotFleetProps",
    jsii_struct_bases=[SpotOneProps],
    name_mapping={
        "additional_user_data": "additionalUserData",
        "assign_eip": "assignEip",
        "custom_ami_id": "customAmiId",
        "default_instance_type": "defaultInstanceType",
        "ebs_volume_size": "ebsVolumeSize",
        "eip_allocation_id": "eipAllocationId",
        "instance_interruption_behavior": "instanceInterruptionBehavior",
        "instance_profile": "instanceProfile",
        "instance_role": "instanceRole",
        "key_name": "keyName",
        "security_group": "securityGroup",
        "target_capacity": "targetCapacity",
        "vpc": "vpc",
        "vpc_subnet": "vpcSubnet",
        "block_device_mappings": "blockDeviceMappings",
        "block_duration": "blockDuration",
        "terminate_instances_with_expiration": "terminateInstancesWithExpiration",
        "valid_from": "validFrom",
        "valid_until": "validUntil",
    },
)
class BaseSpotFleetProps(SpotOneProps):
    def __init__(
        self,
        *,
        additional_user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        assign_eip: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        eip_allocation_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        block_device_mappings: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]] = None,
        block_duration: typing.Optional[BlockDuration] = None,
        terminate_instances_with_expiration: typing.Optional[builtins.bool] = None,
        valid_from: typing.Optional[builtins.str] = None,
        valid_until: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param additional_user_data: Additional commands for user data. Default: - no additional user data
        :param assign_eip: Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined. Default: true
        :param custom_ami_id: custom AMI ID. Default: - The latest Amaozn Linux 2 AMI ID
        :param default_instance_type: default EC2 instance type. Default: - t3.large
        :param ebs_volume_size: default EBS volume size for the spot instance. Default: 60;
        :param eip_allocation_id: Allocation ID for your existing Elastic IP Address.
        :param instance_interruption_behavior: The behavior when a Spot Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE
        :param instance_profile: instance profile for the resource. Default: - create a new one
        :param instance_role: IAM role for the spot instance.
        :param key_name: SSH key name. Default: - no ssh key will be assigned
        :param security_group: Security group for the spot fleet. Default: - allows TCP 22 SSH ingress rule
        :param target_capacity: number of the target capacity. Default: - 1
        :param vpc: VPC for the spot fleet. Default: - new VPC will be created
        :param vpc_subnet: VPC subnet for the spot fleet. Default: - public subnet
        :param block_device_mappings: blockDeviceMappings for config instance. Default: - from ami config.
        :param block_duration: reservce the spot instance as spot block with defined duration. Default: - BlockDuration.ONE_HOUR
        :param terminate_instances_with_expiration: terminate the instance when the allocation is expired. Default: - true
        :param valid_from: the time when the spot fleet allocation starts. Default: - no expiration
        :param valid_until: the time when the spot fleet allocation expires. Default: - no expiration
        '''
        if isinstance(vpc_subnet, dict):
            vpc_subnet = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnet)
        self._values: typing.Dict[str, typing.Any] = {}
        if additional_user_data is not None:
            self._values["additional_user_data"] = additional_user_data
        if assign_eip is not None:
            self._values["assign_eip"] = assign_eip
        if custom_ami_id is not None:
            self._values["custom_ami_id"] = custom_ami_id
        if default_instance_type is not None:
            self._values["default_instance_type"] = default_instance_type
        if ebs_volume_size is not None:
            self._values["ebs_volume_size"] = ebs_volume_size
        if eip_allocation_id is not None:
            self._values["eip_allocation_id"] = eip_allocation_id
        if instance_interruption_behavior is not None:
            self._values["instance_interruption_behavior"] = instance_interruption_behavior
        if instance_profile is not None:
            self._values["instance_profile"] = instance_profile
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if key_name is not None:
            self._values["key_name"] = key_name
        if security_group is not None:
            self._values["security_group"] = security_group
        if target_capacity is not None:
            self._values["target_capacity"] = target_capacity
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnet is not None:
            self._values["vpc_subnet"] = vpc_subnet
        if block_device_mappings is not None:
            self._values["block_device_mappings"] = block_device_mappings
        if block_duration is not None:
            self._values["block_duration"] = block_duration
        if terminate_instances_with_expiration is not None:
            self._values["terminate_instances_with_expiration"] = terminate_instances_with_expiration
        if valid_from is not None:
            self._values["valid_from"] = valid_from
        if valid_until is not None:
            self._values["valid_until"] = valid_until

    @builtins.property
    def additional_user_data(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional commands for user data.

        :default: - no additional user data
        '''
        result = self._values.get("additional_user_data")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def assign_eip(self) -> typing.Optional[builtins.bool]:
        '''Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined.

        :default: true
        '''
        result = self._values.get("assign_eip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_ami_id(self) -> typing.Optional[builtins.str]:
        '''custom AMI ID.

        :default: - The latest Amaozn Linux 2 AMI ID
        '''
        result = self._values.get("custom_ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''default EC2 instance type.

        :default: - t3.large
        '''
        result = self._values.get("default_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def ebs_volume_size(self) -> typing.Optional[jsii.Number]:
        '''default EBS volume size for the spot instance.

        :default: 60;
        '''
        result = self._values.get("ebs_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def eip_allocation_id(self) -> typing.Optional[builtins.str]:
        '''Allocation ID for your existing Elastic IP Address.

        :defalt: new EIP and its association will be created for the first instance in this spot fleet
        '''
        result = self._values.get("eip_allocation_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_interruption_behavior(
        self,
    ) -> typing.Optional[InstanceInterruptionBehavior]:
        '''The behavior when a Spot Instance is interrupted.

        :default: - InstanceInterruptionBehavior.TERMINATE
        '''
        result = self._values.get("instance_interruption_behavior")
        return typing.cast(typing.Optional[InstanceInterruptionBehavior], result)

    @builtins.property
    def instance_profile(self) -> typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile]:
        '''instance profile for the resource.

        :default: - create a new one
        '''
        result = self._values.get("instance_profile")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''IAM role for the spot instance.'''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''SSH key name.

        :default: - no ssh key will be assigned
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.SecurityGroup]:
        '''Security group for the spot fleet.

        :default: - allows TCP 22 SSH ingress rule
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SecurityGroup], result)

    @builtins.property
    def target_capacity(self) -> typing.Optional[jsii.Number]:
        '''number of the target capacity.

        :default: - 1
        '''
        result = self._values.get("target_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC for the spot fleet.

        :default: - new VPC will be created
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnet(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnet for the spot fleet.

        :default: - public subnet
        '''
        result = self._values.get("vpc_subnet")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def block_device_mappings(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]]:
        '''blockDeviceMappings for config instance.

        :default: - from ami config.
        '''
        result = self._values.get("block_device_mappings")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]], result)

    @builtins.property
    def block_duration(self) -> typing.Optional[BlockDuration]:
        '''reservce the spot instance as spot block with defined duration.

        :default: - BlockDuration.ONE_HOUR
        '''
        result = self._values.get("block_duration")
        return typing.cast(typing.Optional[BlockDuration], result)

    @builtins.property
    def terminate_instances_with_expiration(self) -> typing.Optional[builtins.bool]:
        '''terminate the instance when the allocation is expired.

        :default: - true
        '''
        result = self._values.get("terminate_instances_with_expiration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def valid_from(self) -> typing.Optional[builtins.str]:
        '''the time when the spot fleet allocation starts.

        :default: - no expiration
        '''
        result = self._values.get("valid_from")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def valid_until(self) -> typing.Optional[builtins.str]:
        '''the time when the spot fleet allocation expires.

        :default: - no expiration
        '''
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


class SpotFleet(SpotOne, metaclass=jsii.JSIIMeta, jsii_type="cdk-spot-one.SpotFleet"):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        instance_only: typing.Optional[builtins.bool] = None,
        launch_template: typing.Optional[ILaunchtemplate] = None,
        block_device_mappings: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]] = None,
        block_duration: typing.Optional[BlockDuration] = None,
        terminate_instances_with_expiration: typing.Optional[builtins.bool] = None,
        valid_from: typing.Optional[builtins.str] = None,
        valid_until: typing.Optional[builtins.str] = None,
        additional_user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        assign_eip: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        eip_allocation_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_only: Whether to create spot instance only instead of a fleet. Default: false;
        :param launch_template: Launch template for the spot fleet.
        :param block_device_mappings: blockDeviceMappings for config instance. Default: - from ami config.
        :param block_duration: reservce the spot instance as spot block with defined duration. Default: - BlockDuration.ONE_HOUR
        :param terminate_instances_with_expiration: terminate the instance when the allocation is expired. Default: - true
        :param valid_from: the time when the spot fleet allocation starts. Default: - no expiration
        :param valid_until: the time when the spot fleet allocation expires. Default: - no expiration
        :param additional_user_data: Additional commands for user data. Default: - no additional user data
        :param assign_eip: Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined. Default: true
        :param custom_ami_id: custom AMI ID. Default: - The latest Amaozn Linux 2 AMI ID
        :param default_instance_type: default EC2 instance type. Default: - t3.large
        :param ebs_volume_size: default EBS volume size for the spot instance. Default: 60;
        :param eip_allocation_id: Allocation ID for your existing Elastic IP Address.
        :param instance_interruption_behavior: The behavior when a Spot Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE
        :param instance_profile: instance profile for the resource. Default: - create a new one
        :param instance_role: IAM role for the spot instance.
        :param key_name: SSH key name. Default: - no ssh key will be assigned
        :param security_group: Security group for the spot fleet. Default: - allows TCP 22 SSH ingress rule
        :param target_capacity: number of the target capacity. Default: - 1
        :param vpc: VPC for the spot fleet. Default: - new VPC will be created
        :param vpc_subnet: VPC subnet for the spot fleet. Default: - public subnet
        '''
        props = SpotFleetProps(
            instance_only=instance_only,
            launch_template=launch_template,
            block_device_mappings=block_device_mappings,
            block_duration=block_duration,
            terminate_instances_with_expiration=terminate_instances_with_expiration,
            valid_from=valid_from,
            valid_until=valid_until,
            additional_user_data=additional_user_data,
            assign_eip=assign_eip,
            custom_ami_id=custom_ami_id,
            default_instance_type=default_instance_type,
            ebs_volume_size=ebs_volume_size,
            eip_allocation_id=eip_allocation_id,
            instance_interruption_behavior=instance_interruption_behavior,
            instance_profile=instance_profile,
            instance_role=instance_role,
            key_name=key_name,
            security_group=security_group,
            target_capacity=target_capacity,
            vpc=vpc,
            vpc_subnet=vpc_subnet,
        )

        jsii.create(SpotFleet, self, [scope, id, props])

    @jsii.member(jsii_name="expireAfter")
    def expire_after(self, duration: aws_cdk.core.Duration) -> None:
        '''
        :param duration: -
        '''
        return typing.cast(None, jsii.invoke(self, "expireAfter", [duration]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplate")
    def launch_template(self) -> ILaunchtemplate:
        return typing.cast(ILaunchtemplate, jsii.get(self, "launchTemplate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotFleetId")
    def spot_fleet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotFleetId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> typing.Optional[builtins.str]:
        '''the first instance id in this fleet.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceInterruptionBehavior")
    def instance_interruption_behavior(
        self,
    ) -> typing.Optional[InstanceInterruptionBehavior]:
        '''The behavior when a Spot Instance is interrupted.

        :default: terminate
        '''
        return typing.cast(typing.Optional[InstanceInterruptionBehavior], jsii.get(self, "instanceInterruptionBehavior"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[builtins.str]:
        '''instance type of the first instance in this fleet.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotFleetRequestId")
    def spot_fleet_request_id(self) -> typing.Optional[builtins.str]:
        '''SpotFleetRequestId for this spot fleet.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotFleetRequestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetCapacity")
    def target_capacity(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetCapacity"))


@jsii.data_type(
    jsii_type="cdk-spot-one.SpotFleetProps",
    jsii_struct_bases=[BaseSpotFleetProps],
    name_mapping={
        "additional_user_data": "additionalUserData",
        "assign_eip": "assignEip",
        "custom_ami_id": "customAmiId",
        "default_instance_type": "defaultInstanceType",
        "ebs_volume_size": "ebsVolumeSize",
        "eip_allocation_id": "eipAllocationId",
        "instance_interruption_behavior": "instanceInterruptionBehavior",
        "instance_profile": "instanceProfile",
        "instance_role": "instanceRole",
        "key_name": "keyName",
        "security_group": "securityGroup",
        "target_capacity": "targetCapacity",
        "vpc": "vpc",
        "vpc_subnet": "vpcSubnet",
        "block_device_mappings": "blockDeviceMappings",
        "block_duration": "blockDuration",
        "terminate_instances_with_expiration": "terminateInstancesWithExpiration",
        "valid_from": "validFrom",
        "valid_until": "validUntil",
        "instance_only": "instanceOnly",
        "launch_template": "launchTemplate",
    },
)
class SpotFleetProps(BaseSpotFleetProps):
    def __init__(
        self,
        *,
        additional_user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        assign_eip: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        eip_allocation_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        block_device_mappings: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]] = None,
        block_duration: typing.Optional[BlockDuration] = None,
        terminate_instances_with_expiration: typing.Optional[builtins.bool] = None,
        valid_from: typing.Optional[builtins.str] = None,
        valid_until: typing.Optional[builtins.str] = None,
        instance_only: typing.Optional[builtins.bool] = None,
        launch_template: typing.Optional[ILaunchtemplate] = None,
    ) -> None:
        '''
        :param additional_user_data: Additional commands for user data. Default: - no additional user data
        :param assign_eip: Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined. Default: true
        :param custom_ami_id: custom AMI ID. Default: - The latest Amaozn Linux 2 AMI ID
        :param default_instance_type: default EC2 instance type. Default: - t3.large
        :param ebs_volume_size: default EBS volume size for the spot instance. Default: 60;
        :param eip_allocation_id: Allocation ID for your existing Elastic IP Address.
        :param instance_interruption_behavior: The behavior when a Spot Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE
        :param instance_profile: instance profile for the resource. Default: - create a new one
        :param instance_role: IAM role for the spot instance.
        :param key_name: SSH key name. Default: - no ssh key will be assigned
        :param security_group: Security group for the spot fleet. Default: - allows TCP 22 SSH ingress rule
        :param target_capacity: number of the target capacity. Default: - 1
        :param vpc: VPC for the spot fleet. Default: - new VPC will be created
        :param vpc_subnet: VPC subnet for the spot fleet. Default: - public subnet
        :param block_device_mappings: blockDeviceMappings for config instance. Default: - from ami config.
        :param block_duration: reservce the spot instance as spot block with defined duration. Default: - BlockDuration.ONE_HOUR
        :param terminate_instances_with_expiration: terminate the instance when the allocation is expired. Default: - true
        :param valid_from: the time when the spot fleet allocation starts. Default: - no expiration
        :param valid_until: the time when the spot fleet allocation expires. Default: - no expiration
        :param instance_only: Whether to create spot instance only instead of a fleet. Default: false;
        :param launch_template: Launch template for the spot fleet.
        '''
        if isinstance(vpc_subnet, dict):
            vpc_subnet = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnet)
        self._values: typing.Dict[str, typing.Any] = {}
        if additional_user_data is not None:
            self._values["additional_user_data"] = additional_user_data
        if assign_eip is not None:
            self._values["assign_eip"] = assign_eip
        if custom_ami_id is not None:
            self._values["custom_ami_id"] = custom_ami_id
        if default_instance_type is not None:
            self._values["default_instance_type"] = default_instance_type
        if ebs_volume_size is not None:
            self._values["ebs_volume_size"] = ebs_volume_size
        if eip_allocation_id is not None:
            self._values["eip_allocation_id"] = eip_allocation_id
        if instance_interruption_behavior is not None:
            self._values["instance_interruption_behavior"] = instance_interruption_behavior
        if instance_profile is not None:
            self._values["instance_profile"] = instance_profile
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if key_name is not None:
            self._values["key_name"] = key_name
        if security_group is not None:
            self._values["security_group"] = security_group
        if target_capacity is not None:
            self._values["target_capacity"] = target_capacity
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnet is not None:
            self._values["vpc_subnet"] = vpc_subnet
        if block_device_mappings is not None:
            self._values["block_device_mappings"] = block_device_mappings
        if block_duration is not None:
            self._values["block_duration"] = block_duration
        if terminate_instances_with_expiration is not None:
            self._values["terminate_instances_with_expiration"] = terminate_instances_with_expiration
        if valid_from is not None:
            self._values["valid_from"] = valid_from
        if valid_until is not None:
            self._values["valid_until"] = valid_until
        if instance_only is not None:
            self._values["instance_only"] = instance_only
        if launch_template is not None:
            self._values["launch_template"] = launch_template

    @builtins.property
    def additional_user_data(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional commands for user data.

        :default: - no additional user data
        '''
        result = self._values.get("additional_user_data")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def assign_eip(self) -> typing.Optional[builtins.bool]:
        '''Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined.

        :default: true
        '''
        result = self._values.get("assign_eip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_ami_id(self) -> typing.Optional[builtins.str]:
        '''custom AMI ID.

        :default: - The latest Amaozn Linux 2 AMI ID
        '''
        result = self._values.get("custom_ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''default EC2 instance type.

        :default: - t3.large
        '''
        result = self._values.get("default_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def ebs_volume_size(self) -> typing.Optional[jsii.Number]:
        '''default EBS volume size for the spot instance.

        :default: 60;
        '''
        result = self._values.get("ebs_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def eip_allocation_id(self) -> typing.Optional[builtins.str]:
        '''Allocation ID for your existing Elastic IP Address.

        :defalt: new EIP and its association will be created for the first instance in this spot fleet
        '''
        result = self._values.get("eip_allocation_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_interruption_behavior(
        self,
    ) -> typing.Optional[InstanceInterruptionBehavior]:
        '''The behavior when a Spot Instance is interrupted.

        :default: - InstanceInterruptionBehavior.TERMINATE
        '''
        result = self._values.get("instance_interruption_behavior")
        return typing.cast(typing.Optional[InstanceInterruptionBehavior], result)

    @builtins.property
    def instance_profile(self) -> typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile]:
        '''instance profile for the resource.

        :default: - create a new one
        '''
        result = self._values.get("instance_profile")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''IAM role for the spot instance.'''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''SSH key name.

        :default: - no ssh key will be assigned
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.SecurityGroup]:
        '''Security group for the spot fleet.

        :default: - allows TCP 22 SSH ingress rule
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SecurityGroup], result)

    @builtins.property
    def target_capacity(self) -> typing.Optional[jsii.Number]:
        '''number of the target capacity.

        :default: - 1
        '''
        result = self._values.get("target_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC for the spot fleet.

        :default: - new VPC will be created
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnet(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnet for the spot fleet.

        :default: - public subnet
        '''
        result = self._values.get("vpc_subnet")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def block_device_mappings(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]]:
        '''blockDeviceMappings for config instance.

        :default: - from ami config.
        '''
        result = self._values.get("block_device_mappings")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]], result)

    @builtins.property
    def block_duration(self) -> typing.Optional[BlockDuration]:
        '''reservce the spot instance as spot block with defined duration.

        :default: - BlockDuration.ONE_HOUR
        '''
        result = self._values.get("block_duration")
        return typing.cast(typing.Optional[BlockDuration], result)

    @builtins.property
    def terminate_instances_with_expiration(self) -> typing.Optional[builtins.bool]:
        '''terminate the instance when the allocation is expired.

        :default: - true
        '''
        result = self._values.get("terminate_instances_with_expiration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def valid_from(self) -> typing.Optional[builtins.str]:
        '''the time when the spot fleet allocation starts.

        :default: - no expiration
        '''
        result = self._values.get("valid_from")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def valid_until(self) -> typing.Optional[builtins.str]:
        '''the time when the spot fleet allocation expires.

        :default: - no expiration
        '''
        result = self._values.get("valid_until")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_only(self) -> typing.Optional[builtins.bool]:
        '''Whether to create spot instance only instead of a fleet.

        :default: false;
        '''
        result = self._values.get("instance_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def launch_template(self) -> typing.Optional[ILaunchtemplate]:
        '''Launch template for the spot fleet.'''
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


class SpotInstance(
    SpotOne,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-spot-one.SpotInstance",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        block_device_mappings: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]] = None,
        additional_user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        assign_eip: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        eip_allocation_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param block_device_mappings: blockDeviceMappings for config instance. Default: - from ami config.
        :param additional_user_data: Additional commands for user data. Default: - no additional user data
        :param assign_eip: Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined. Default: true
        :param custom_ami_id: custom AMI ID. Default: - The latest Amaozn Linux 2 AMI ID
        :param default_instance_type: default EC2 instance type. Default: - t3.large
        :param ebs_volume_size: default EBS volume size for the spot instance. Default: 60;
        :param eip_allocation_id: Allocation ID for your existing Elastic IP Address.
        :param instance_interruption_behavior: The behavior when a Spot Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE
        :param instance_profile: instance profile for the resource. Default: - create a new one
        :param instance_role: IAM role for the spot instance.
        :param key_name: SSH key name. Default: - no ssh key will be assigned
        :param security_group: Security group for the spot fleet. Default: - allows TCP 22 SSH ingress rule
        :param target_capacity: number of the target capacity. Default: - 1
        :param vpc: VPC for the spot fleet. Default: - new VPC will be created
        :param vpc_subnet: VPC subnet for the spot fleet. Default: - public subnet
        '''
        props = SpotInstanceProps(
            block_device_mappings=block_device_mappings,
            additional_user_data=additional_user_data,
            assign_eip=assign_eip,
            custom_ami_id=custom_ami_id,
            default_instance_type=default_instance_type,
            ebs_volume_size=ebs_volume_size,
            eip_allocation_id=eip_allocation_id,
            instance_interruption_behavior=instance_interruption_behavior,
            instance_profile=instance_profile,
            instance_role=instance_role,
            key_name=key_name,
            security_group=security_group,
            target_capacity=target_capacity,
            vpc=vpc,
            vpc_subnet=vpc_subnet,
        )

        jsii.create(SpotInstance, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceType"))


@jsii.data_type(
    jsii_type="cdk-spot-one.SpotInstanceProps",
    jsii_struct_bases=[SpotOneProps],
    name_mapping={
        "additional_user_data": "additionalUserData",
        "assign_eip": "assignEip",
        "custom_ami_id": "customAmiId",
        "default_instance_type": "defaultInstanceType",
        "ebs_volume_size": "ebsVolumeSize",
        "eip_allocation_id": "eipAllocationId",
        "instance_interruption_behavior": "instanceInterruptionBehavior",
        "instance_profile": "instanceProfile",
        "instance_role": "instanceRole",
        "key_name": "keyName",
        "security_group": "securityGroup",
        "target_capacity": "targetCapacity",
        "vpc": "vpc",
        "vpc_subnet": "vpcSubnet",
        "block_device_mappings": "blockDeviceMappings",
    },
)
class SpotInstanceProps(SpotOneProps):
    def __init__(
        self,
        *,
        additional_user_data: typing.Optional[typing.Sequence[builtins.str]] = None,
        assign_eip: typing.Optional[builtins.bool] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        default_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        eip_allocation_id: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional[InstanceInterruptionBehavior] = None,
        instance_profile: typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        target_capacity: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        block_device_mappings: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]] = None,
    ) -> None:
        '''
        :param additional_user_data: Additional commands for user data. Default: - no additional user data
        :param assign_eip: Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined. Default: true
        :param custom_ami_id: custom AMI ID. Default: - The latest Amaozn Linux 2 AMI ID
        :param default_instance_type: default EC2 instance type. Default: - t3.large
        :param ebs_volume_size: default EBS volume size for the spot instance. Default: 60;
        :param eip_allocation_id: Allocation ID for your existing Elastic IP Address.
        :param instance_interruption_behavior: The behavior when a Spot Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE
        :param instance_profile: instance profile for the resource. Default: - create a new one
        :param instance_role: IAM role for the spot instance.
        :param key_name: SSH key name. Default: - no ssh key will be assigned
        :param security_group: Security group for the spot fleet. Default: - allows TCP 22 SSH ingress rule
        :param target_capacity: number of the target capacity. Default: - 1
        :param vpc: VPC for the spot fleet. Default: - new VPC will be created
        :param vpc_subnet: VPC subnet for the spot fleet. Default: - public subnet
        :param block_device_mappings: blockDeviceMappings for config instance. Default: - from ami config.
        '''
        if isinstance(vpc_subnet, dict):
            vpc_subnet = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnet)
        self._values: typing.Dict[str, typing.Any] = {}
        if additional_user_data is not None:
            self._values["additional_user_data"] = additional_user_data
        if assign_eip is not None:
            self._values["assign_eip"] = assign_eip
        if custom_ami_id is not None:
            self._values["custom_ami_id"] = custom_ami_id
        if default_instance_type is not None:
            self._values["default_instance_type"] = default_instance_type
        if ebs_volume_size is not None:
            self._values["ebs_volume_size"] = ebs_volume_size
        if eip_allocation_id is not None:
            self._values["eip_allocation_id"] = eip_allocation_id
        if instance_interruption_behavior is not None:
            self._values["instance_interruption_behavior"] = instance_interruption_behavior
        if instance_profile is not None:
            self._values["instance_profile"] = instance_profile
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if key_name is not None:
            self._values["key_name"] = key_name
        if security_group is not None:
            self._values["security_group"] = security_group
        if target_capacity is not None:
            self._values["target_capacity"] = target_capacity
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnet is not None:
            self._values["vpc_subnet"] = vpc_subnet
        if block_device_mappings is not None:
            self._values["block_device_mappings"] = block_device_mappings

    @builtins.property
    def additional_user_data(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional commands for user data.

        :default: - no additional user data
        '''
        result = self._values.get("additional_user_data")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def assign_eip(self) -> typing.Optional[builtins.bool]:
        '''Auto assign a new EIP on this instance if ``eipAllocationId`` is not defined.

        :default: true
        '''
        result = self._values.get("assign_eip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_ami_id(self) -> typing.Optional[builtins.str]:
        '''custom AMI ID.

        :default: - The latest Amaozn Linux 2 AMI ID
        '''
        result = self._values.get("custom_ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''default EC2 instance type.

        :default: - t3.large
        '''
        result = self._values.get("default_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def ebs_volume_size(self) -> typing.Optional[jsii.Number]:
        '''default EBS volume size for the spot instance.

        :default: 60;
        '''
        result = self._values.get("ebs_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def eip_allocation_id(self) -> typing.Optional[builtins.str]:
        '''Allocation ID for your existing Elastic IP Address.

        :defalt: new EIP and its association will be created for the first instance in this spot fleet
        '''
        result = self._values.get("eip_allocation_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_interruption_behavior(
        self,
    ) -> typing.Optional[InstanceInterruptionBehavior]:
        '''The behavior when a Spot Instance is interrupted.

        :default: - InstanceInterruptionBehavior.TERMINATE
        '''
        result = self._values.get("instance_interruption_behavior")
        return typing.cast(typing.Optional[InstanceInterruptionBehavior], result)

    @builtins.property
    def instance_profile(self) -> typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile]:
        '''instance profile for the resource.

        :default: - create a new one
        '''
        result = self._values.get("instance_profile")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''IAM role for the spot instance.'''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''SSH key name.

        :default: - no ssh key will be assigned
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.SecurityGroup]:
        '''Security group for the spot fleet.

        :default: - allows TCP 22 SSH ingress rule
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SecurityGroup], result)

    @builtins.property
    def target_capacity(self) -> typing.Optional[jsii.Number]:
        '''number of the target capacity.

        :default: - 1
        '''
        result = self._values.get("target_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC for the spot fleet.

        :default: - new VPC will be created
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnet(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnet for the spot fleet.

        :default: - public subnet
        '''
        result = self._values.get("vpc_subnet")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def block_device_mappings(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]]:
        '''blockDeviceMappings for config instance.

        :default: - from ami config.
        '''
        result = self._values.get("block_device_mappings")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpotInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BaseSpotFleetProps",
    "BlockDuration",
    "ILaunchtemplate",
    "InstanceInterruptionBehavior",
    "LaunchTemplate",
    "LaunchTemplateProps",
    "LaunchTemplateResource",
    "NodeType",
    "SpotFleet",
    "SpotFleetLaunchTemplateConfig",
    "SpotFleetProps",
    "SpotInstance",
    "SpotInstanceProps",
    "SpotOne",
    "SpotOneProps",
    "VpcProvider",
]

publication.publish()
