'''
[![awscdk-jsii-template](https://img.shields.io/badge/built%20with-awscdk--jsii--template-blue)](https://github.com/pahud/awscdk-jsii-template)
[![NPM version](https://badge.fury.io/js/cdk-soca.svg)](https://badge.fury.io/js/cdk-soca)
[![PyPI version](https://badge.fury.io/py/cdk-soca.svg)](https://badge.fury.io/py/cdk-soca)
![Release](https://github.com/pahud/cdk-soca/workflows/Release/badge.svg)

# Welcome to `cdk-soca`

`cdk-soca` is an AWS CDK construct library that allows you to create the [Scale-Out Computing on AWS](https://aws.amazon.com/tw/solutions/implementations/scale-out-computing-on-aws/) with AWS CDK in `TypeScript` or `Python`.

# Sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import cdk_soca as soca

# create the CDK application
app = App()

# create the stack in the CDK app
stack = Stack(app, "soca-testing-stack")

# create the workload in the CDK stack
soca.Workload(stack, "Workload")
```

That's all!
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


class Analytics(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-soca.Analytics",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster_id: builtins.str,
        scheduler_security_group: aws_cdk.aws_ec2.ISecurityGroup,
        secheduler_public_ip: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        client_ip_cidr: typing.Optional[builtins.str] = None,
        domain_name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_id: 
        :param scheduler_security_group: 
        :param secheduler_public_ip: 
        :param vpc: 
        :param client_ip_cidr: 
        :param domain_name: 
        :param removal_policy: (experimental) removal policy for the ES. Default: RemovalPolicy.DESTROY

        :stability: experimental
        '''
        props = AnalyticsProps(
            cluster_id=cluster_id,
            scheduler_security_group=scheduler_security_group,
            secheduler_public_ip=secheduler_public_ip,
            vpc=vpc,
            client_ip_cidr=client_ip_cidr,
            domain_name=domain_name,
            removal_policy=removal_policy,
        )

        jsii.create(Analytics, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-soca.AnalyticsProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_id": "clusterId",
        "scheduler_security_group": "schedulerSecurityGroup",
        "secheduler_public_ip": "sechedulerPublicIp",
        "vpc": "vpc",
        "client_ip_cidr": "clientIpCidr",
        "domain_name": "domainName",
        "removal_policy": "removalPolicy",
    },
)
class AnalyticsProps:
    def __init__(
        self,
        *,
        cluster_id: builtins.str,
        scheduler_security_group: aws_cdk.aws_ec2.ISecurityGroup,
        secheduler_public_ip: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        client_ip_cidr: typing.Optional[builtins.str] = None,
        domain_name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
    ) -> None:
        '''
        :param cluster_id: 
        :param scheduler_security_group: 
        :param secheduler_public_ip: 
        :param vpc: 
        :param client_ip_cidr: 
        :param domain_name: 
        :param removal_policy: (experimental) removal policy for the ES. Default: RemovalPolicy.DESTROY

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_id": cluster_id,
            "scheduler_security_group": scheduler_security_group,
            "secheduler_public_ip": secheduler_public_ip,
            "vpc": vpc,
        }
        if client_ip_cidr is not None:
            self._values["client_ip_cidr"] = client_ip_cidr
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def cluster_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scheduler_security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''
        :stability: experimental
        '''
        result = self._values.get("scheduler_security_group")
        assert result is not None, "Required property 'scheduler_security_group' is missing"
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, result)

    @builtins.property
    def secheduler_public_ip(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("secheduler_public_ip")
        assert result is not None, "Required property 'secheduler_public_ip' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def client_ip_cidr(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_ip_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''(experimental) removal policy for the ES.

        :default: RemovalPolicy.DESTROY

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AnalyticsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-soca.BaseOS")
class BaseOS(enum.Enum):
    '''
    :stability: experimental
    '''

    CENTOS_7 = "CENTOS_7"
    '''
    :stability: experimental
    '''
    RHEL_7 = "RHEL_7"
    '''
    :stability: experimental
    '''
    AMZN2 = "AMZN2"
    '''
    :stability: experimental
    '''


class EfsStorage(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-soca.EfsStorage",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster_id: builtins.str,
        compute_node_security_group: aws_cdk.aws_ec2.ISecurityGroup,
        scheduler_security_group: aws_cdk.aws_ec2.ISecurityGroup,
        vpc: aws_cdk.aws_ec2.IVpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_id: 
        :param compute_node_security_group: 
        :param scheduler_security_group: 
        :param vpc: 

        :stability: experimental
        '''
        props = EfsStorageProps(
            cluster_id=cluster_id,
            compute_node_security_group=compute_node_security_group,
            scheduler_security_group=scheduler_security_group,
            vpc=vpc,
        )

        jsii.create(EfsStorage, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="efsAppsDns")
    def efs_apps_dns(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "efsAppsDns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="efsDataDns")
    def efs_data_dns(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "efsDataDns"))


@jsii.data_type(
    jsii_type="cdk-soca.EfsStorageProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_id": "clusterId",
        "compute_node_security_group": "computeNodeSecurityGroup",
        "scheduler_security_group": "schedulerSecurityGroup",
        "vpc": "vpc",
    },
)
class EfsStorageProps:
    def __init__(
        self,
        *,
        cluster_id: builtins.str,
        compute_node_security_group: aws_cdk.aws_ec2.ISecurityGroup,
        scheduler_security_group: aws_cdk.aws_ec2.ISecurityGroup,
        vpc: aws_cdk.aws_ec2.IVpc,
    ) -> None:
        '''
        :param cluster_id: 
        :param compute_node_security_group: 
        :param scheduler_security_group: 
        :param vpc: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_id": cluster_id,
            "compute_node_security_group": compute_node_security_group,
            "scheduler_security_group": scheduler_security_group,
            "vpc": vpc,
        }

    @builtins.property
    def cluster_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compute_node_security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''
        :stability: experimental
        '''
        result = self._values.get("compute_node_security_group")
        assert result is not None, "Required property 'compute_node_security_group' is missing"
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, result)

    @builtins.property
    def scheduler_security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''
        :stability: experimental
        '''
        result = self._values.get("scheduler_security_group")
        assert result is not None, "Required property 'scheduler_security_group' is missing"
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsStorageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamRoles(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-soca.IamRoles",
):
    '''(experimental) Create all required IAM roles.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        network: "Network",
        s3_install_bucket_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param network: 
        :param s3_install_bucket_name: 

        :stability: experimental
        '''
        props = IamRolesProps(
            network=network, s3_install_bucket_name=s3_install_bucket_name
        )

        jsii.create(IamRoles, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeNodeIamRole")
    def compute_node_iam_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "computeNodeIamRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeNodeInstanceProfileName")
    def compute_node_instance_profile_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "computeNodeInstanceProfileName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulerIamInstanceProfileName")
    def scheduler_iam_instance_profile_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "schedulerIamInstanceProfileName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulerIAMRole")
    def scheduler_iam_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "schedulerIAMRole"))


@jsii.data_type(
    jsii_type="cdk-soca.IamRolesProps",
    jsii_struct_bases=[],
    name_mapping={
        "network": "network",
        "s3_install_bucket_name": "s3InstallBucketName",
    },
)
class IamRolesProps:
    def __init__(
        self,
        *,
        network: "Network",
        s3_install_bucket_name: builtins.str,
    ) -> None:
        '''
        :param network: 
        :param s3_install_bucket_name: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "network": network,
            "s3_install_bucket_name": s3_install_bucket_name,
        }

    @builtins.property
    def network(self) -> "Network":
        '''
        :stability: experimental
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast("Network", result)

    @builtins.property
    def s3_install_bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_install_bucket_name")
        assert result is not None, "Required property 's3_install_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamRolesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Network(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-soca.Network",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster_id: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_id: 
        :param vpc: 

        :stability: experimental
        '''
        props = NetworkProps(cluster_id=cluster_id, vpc=vpc)

        jsii.create(Network, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="natEip")
    def nat_eip(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "natEip"))


@jsii.data_type(
    jsii_type="cdk-soca.NetworkProps",
    jsii_struct_bases=[],
    name_mapping={"cluster_id": "clusterId", "vpc": "vpc"},
)
class NetworkProps:
    def __init__(
        self,
        *,
        cluster_id: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param cluster_id: 
        :param vpc: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Scheduler(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-soca.Scheduler",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        ldap_user_name: builtins.str,
        ldap_user_password: builtins.str,
        network: Network,
        s3_install_bucket: builtins.str,
        s3_install_folder: builtins.str,
        scheduler_security_group: aws_cdk.aws_ec2.ISecurityGroup,
        storage: EfsStorage,
        base_os: typing.Optional[BaseOS] = None,
        custom_ami: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ldap_user_name: 
        :param ldap_user_password: 
        :param network: 
        :param s3_install_bucket: 
        :param s3_install_folder: 
        :param scheduler_security_group: 
        :param storage: 
        :param base_os: 
        :param custom_ami: 
        :param instance_type: 

        :stability: experimental
        '''
        props = SchedulerProps(
            ldap_user_name=ldap_user_name,
            ldap_user_password=ldap_user_password,
            network=network,
            s3_install_bucket=s3_install_bucket,
            s3_install_folder=s3_install_folder,
            scheduler_security_group=scheduler_security_group,
            storage=storage,
            base_os=base_os,
            custom_ami=custom_ami,
            instance_type=instance_type,
        )

        jsii.create(Scheduler, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicIp")
    def public_ip(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "publicIp"))


@jsii.data_type(
    jsii_type="cdk-soca.SchedulerProps",
    jsii_struct_bases=[],
    name_mapping={
        "ldap_user_name": "ldapUserName",
        "ldap_user_password": "ldapUserPassword",
        "network": "network",
        "s3_install_bucket": "s3InstallBucket",
        "s3_install_folder": "s3InstallFolder",
        "scheduler_security_group": "schedulerSecurityGroup",
        "storage": "storage",
        "base_os": "baseOs",
        "custom_ami": "customAmi",
        "instance_type": "instanceType",
    },
)
class SchedulerProps:
    def __init__(
        self,
        *,
        ldap_user_name: builtins.str,
        ldap_user_password: builtins.str,
        network: Network,
        s3_install_bucket: builtins.str,
        s3_install_folder: builtins.str,
        scheduler_security_group: aws_cdk.aws_ec2.ISecurityGroup,
        storage: EfsStorage,
        base_os: typing.Optional[BaseOS] = None,
        custom_ami: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
    ) -> None:
        '''
        :param ldap_user_name: 
        :param ldap_user_password: 
        :param network: 
        :param s3_install_bucket: 
        :param s3_install_folder: 
        :param scheduler_security_group: 
        :param storage: 
        :param base_os: 
        :param custom_ami: 
        :param instance_type: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "ldap_user_name": ldap_user_name,
            "ldap_user_password": ldap_user_password,
            "network": network,
            "s3_install_bucket": s3_install_bucket,
            "s3_install_folder": s3_install_folder,
            "scheduler_security_group": scheduler_security_group,
            "storage": storage,
        }
        if base_os is not None:
            self._values["base_os"] = base_os
        if custom_ami is not None:
            self._values["custom_ami"] = custom_ami
        if instance_type is not None:
            self._values["instance_type"] = instance_type

    @builtins.property
    def ldap_user_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("ldap_user_name")
        assert result is not None, "Required property 'ldap_user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ldap_user_password(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("ldap_user_password")
        assert result is not None, "Required property 'ldap_user_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network(self) -> Network:
        '''
        :stability: experimental
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(Network, result)

    @builtins.property
    def s3_install_bucket(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_install_bucket")
        assert result is not None, "Required property 's3_install_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_install_folder(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_install_folder")
        assert result is not None, "Required property 's3_install_folder' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scheduler_security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''
        :stability: experimental
        '''
        result = self._values.get("scheduler_security_group")
        assert result is not None, "Required property 'scheduler_security_group' is missing"
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, result)

    @builtins.property
    def storage(self) -> EfsStorage:
        '''
        :stability: experimental
        '''
        result = self._values.get("storage")
        assert result is not None, "Required property 'storage' is missing"
        return typing.cast(EfsStorage, result)

    @builtins.property
    def base_os(self) -> typing.Optional[BaseOS]:
        '''
        :stability: experimental
        '''
        result = self._values.get("base_os")
        return typing.cast(typing.Optional[BaseOS], result)

    @builtins.property
    def custom_ami(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("custom_ami")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SchedulerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Workload(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-soca.Workload",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        client_ip_cidr: typing.Optional[builtins.str] = None,
        custom_ami: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ldap_user_name: typing.Optional[builtins.str] = None,
        ldap_user_password: typing.Optional[builtins.str] = None,
        linux_distribution: typing.Optional[BaseOS] = None,
        s3_install_bucket: typing.Optional[builtins.str] = None,
        s3_install_folder: typing.Optional[builtins.str] = None,
        ssh_key_name: typing.Optional[builtins.str] = None,
        vpc_cidr: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param client_ip_cidr: (experimental) Default IP(s) allowed to directly SSH into the scheduler and access ElasticSearch. 0.0.0.0/0 means ALL INTERNET access. You probably want to change it with your own IP/subnet (x.x.x.x/32 for your own ip or x.x.x.x/24 for range. Replace x.x.x.x with your own PUBLIC IP. You can get your public IP using tools such as https://ifconfig.co/). Make sure to keep it restrictive! Default: - not to add any client IP Cidr address
        :param custom_ami: (experimental) Custom AMI if available. Default: - no custom AMI
        :param instance_type: (experimental) Instance type for your master host(scheduler). Default: - m5.xlarge
        :param ldap_user_name: (experimental) Username for your default LDAP user. Default: - 'ldapUserName'
        :param ldap_user_password: (experimental) Password for your default LDAP user. Default: - 'ldapUserPassword!123'
        :param linux_distribution: (experimental) Linux distribution. Default: - amazonlinux2
        :param s3_install_bucket: (experimental) S3 bucket with your SOCA installer. Name of your S3 Bucket where you uploaded your install files. Default: - solutions-reference
        :param s3_install_folder: (experimental) Name of the S3 folder where you uploaded SOCA. Default: - scale-out-computing-on-aws/v2.5.0
        :param ssh_key_name: (experimental) Default SSH pem keys used to SSH into the scheduler.
        :param vpc_cidr: (experimental) VPC Cidr for the new VPC. Default: - 10.0.0.0/16

        :stability: experimental
        '''
        props = WorkloadProps(
            client_ip_cidr=client_ip_cidr,
            custom_ami=custom_ami,
            instance_type=instance_type,
            ldap_user_name=ldap_user_name,
            ldap_user_password=ldap_user_password,
            linux_distribution=linux_distribution,
            s3_install_bucket=s3_install_bucket,
            s3_install_folder=s3_install_folder,
            ssh_key_name=ssh_key_name,
            vpc_cidr=vpc_cidr,
        )

        jsii.create(Workload, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-soca.WorkloadProps",
    jsii_struct_bases=[],
    name_mapping={
        "client_ip_cidr": "clientIpCidr",
        "custom_ami": "customAmi",
        "instance_type": "instanceType",
        "ldap_user_name": "ldapUserName",
        "ldap_user_password": "ldapUserPassword",
        "linux_distribution": "linuxDistribution",
        "s3_install_bucket": "s3InstallBucket",
        "s3_install_folder": "s3InstallFolder",
        "ssh_key_name": "sshKeyName",
        "vpc_cidr": "vpcCidr",
    },
)
class WorkloadProps:
    def __init__(
        self,
        *,
        client_ip_cidr: typing.Optional[builtins.str] = None,
        custom_ami: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        ldap_user_name: typing.Optional[builtins.str] = None,
        ldap_user_password: typing.Optional[builtins.str] = None,
        linux_distribution: typing.Optional[BaseOS] = None,
        s3_install_bucket: typing.Optional[builtins.str] = None,
        s3_install_folder: typing.Optional[builtins.str] = None,
        ssh_key_name: typing.Optional[builtins.str] = None,
        vpc_cidr: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_ip_cidr: (experimental) Default IP(s) allowed to directly SSH into the scheduler and access ElasticSearch. 0.0.0.0/0 means ALL INTERNET access. You probably want to change it with your own IP/subnet (x.x.x.x/32 for your own ip or x.x.x.x/24 for range. Replace x.x.x.x with your own PUBLIC IP. You can get your public IP using tools such as https://ifconfig.co/). Make sure to keep it restrictive! Default: - not to add any client IP Cidr address
        :param custom_ami: (experimental) Custom AMI if available. Default: - no custom AMI
        :param instance_type: (experimental) Instance type for your master host(scheduler). Default: - m5.xlarge
        :param ldap_user_name: (experimental) Username for your default LDAP user. Default: - 'ldapUserName'
        :param ldap_user_password: (experimental) Password for your default LDAP user. Default: - 'ldapUserPassword!123'
        :param linux_distribution: (experimental) Linux distribution. Default: - amazonlinux2
        :param s3_install_bucket: (experimental) S3 bucket with your SOCA installer. Name of your S3 Bucket where you uploaded your install files. Default: - solutions-reference
        :param s3_install_folder: (experimental) Name of the S3 folder where you uploaded SOCA. Default: - scale-out-computing-on-aws/v2.5.0
        :param ssh_key_name: (experimental) Default SSH pem keys used to SSH into the scheduler.
        :param vpc_cidr: (experimental) VPC Cidr for the new VPC. Default: - 10.0.0.0/16

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if client_ip_cidr is not None:
            self._values["client_ip_cidr"] = client_ip_cidr
        if custom_ami is not None:
            self._values["custom_ami"] = custom_ami
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if ldap_user_name is not None:
            self._values["ldap_user_name"] = ldap_user_name
        if ldap_user_password is not None:
            self._values["ldap_user_password"] = ldap_user_password
        if linux_distribution is not None:
            self._values["linux_distribution"] = linux_distribution
        if s3_install_bucket is not None:
            self._values["s3_install_bucket"] = s3_install_bucket
        if s3_install_folder is not None:
            self._values["s3_install_folder"] = s3_install_folder
        if ssh_key_name is not None:
            self._values["ssh_key_name"] = ssh_key_name
        if vpc_cidr is not None:
            self._values["vpc_cidr"] = vpc_cidr

    @builtins.property
    def client_ip_cidr(self) -> typing.Optional[builtins.str]:
        '''(experimental) Default IP(s) allowed to directly SSH into the scheduler and access ElasticSearch.

        0.0.0.0/0 means
        ALL INTERNET access. You probably want to change it with your own IP/subnet (x.x.x.x/32 for your own
        ip or x.x.x.x/24 for range. Replace x.x.x.x with your own PUBLIC IP. You can get your public IP using
        tools such as https://ifconfig.co/). Make sure to keep it restrictive!

        :default: - not to add any client IP Cidr address

        :stability: experimental
        '''
        result = self._values.get("client_ip_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_ami(self) -> typing.Optional[builtins.str]:
        '''(experimental) Custom AMI if available.

        :default: - no custom AMI

        :stability: experimental
        '''
        result = self._values.get("custom_ami")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''(experimental) Instance type for your master host(scheduler).

        :default: - m5.xlarge

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def ldap_user_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Username for your default LDAP user.

        :default: - 'ldapUserName'

        :stability: experimental
        '''
        result = self._values.get("ldap_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ldap_user_password(self) -> typing.Optional[builtins.str]:
        '''(experimental) Password for your default LDAP user.

        :default: - 'ldapUserPassword!123'

        :stability: experimental
        '''
        result = self._values.get("ldap_user_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def linux_distribution(self) -> typing.Optional[BaseOS]:
        '''(experimental) Linux distribution.

        :default: - amazonlinux2

        :stability: experimental
        '''
        result = self._values.get("linux_distribution")
        return typing.cast(typing.Optional[BaseOS], result)

    @builtins.property
    def s3_install_bucket(self) -> typing.Optional[builtins.str]:
        '''(experimental) S3 bucket with your SOCA installer.

        Name of your S3 Bucket where you uploaded your install files.

        :default: - solutions-reference

        :stability: experimental
        '''
        result = self._values.get("s3_install_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_install_folder(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the S3 folder where you uploaded SOCA.

        :default: - scale-out-computing-on-aws/v2.5.0

        :stability: experimental
        '''
        result = self._values.get("s3_install_folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_key_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Default SSH pem keys used to SSH into the scheduler.

        :stability: experimental
        '''
        result = self._values.get("ssh_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_cidr(self) -> typing.Optional[builtins.str]:
        '''(experimental) VPC Cidr for the new VPC.

        :default: - 10.0.0.0/16

        :stability: experimental
        '''
        result = self._values.get("vpc_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkloadProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Analytics",
    "AnalyticsProps",
    "BaseOS",
    "EfsStorage",
    "EfsStorageProps",
    "IamRoles",
    "IamRolesProps",
    "Network",
    "NetworkProps",
    "Scheduler",
    "SchedulerProps",
    "Workload",
    "WorkloadProps",
]

publication.publish()
