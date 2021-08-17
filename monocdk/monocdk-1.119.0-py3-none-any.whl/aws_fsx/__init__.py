'''
# Amazon FSx Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

[Amazon FSx](https://docs.aws.amazon.com/fsx/?id=docs_gateway) provides fully managed third-party file systems with the
native compatibility and feature sets for workloads such as Microsoft Windows–based storage, high-performance computing,
machine learning, and electronic design automation.

Amazon FSx supports two file system types: [Lustre](https://docs.aws.amazon.com/fsx/latest/LustreGuide/index.html) and
[Windows](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/index.html) File Server.

## FSx for Lustre

Amazon FSx for Lustre makes it easy and cost-effective to launch and run the popular, high-performance Lustre file
system. You use Lustre for workloads where speed matters, such as machine learning, high performance computing (HPC),
video processing, and financial modeling.

The open-source Lustre file system is designed for applications that require fast storage—where you want your storage
to keep up with your compute. Lustre was built to solve the problem of quickly and cheaply processing the world's
ever-growing datasets. It's a widely used file system designed for the fastest computers in the world. It provides
submillisecond latencies, up to hundreds of GBps of throughput, and up to millions of IOPS. For more information on
Lustre, see the [Lustre website](http://lustre.org/).

As a fully managed service, Amazon FSx makes it easier for you to use Lustre for workloads where storage speed matters.
Amazon FSx for Lustre eliminates the traditional complexity of setting up and managing Lustre file systems, enabling
you to spin up and run a battle-tested high-performance file system in minutes. It also provides multiple deployment
options so you can optimize cost for your needs.

Amazon FSx for Lustre is POSIX-compliant, so you can use your current Linux-based applications without having to make
any changes. Amazon FSx for Lustre provides a native file system interface and works as any file system does with your
Linux operating system. It also provides read-after-write consistency and supports file locking.

### Installation

Import to your project:

```python
# Example automatically generated. See https://github.com/aws/jsii/issues/826
from aws_cdk import aws_fsx as fsx
```

### Basic Usage

Setup required properties and create:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
stack = Stack(app, "Stack")
vpc = Vpc(stack, "VPC")

file_system = LustreFileSystem(stack, "FsxLustreFileSystem",
    lustre_configuration={"deployment_type": LustreDeploymentType.SCRATCH_2},
    storage_capacity_gi_b=1200,
    vpc=vpc,
    vpc_subnet=vpc.privateSubnets[0]
)
```

### Connecting

To control who can access the file system, use the `.connections` attribute. FSx has a fixed default port, so you don't
need to specify the port. This example allows an EC2 instance to connect to a file system:

```python
# Example automatically generated. See https://github.com/aws/jsii/issues/826
file_system.connections.allow_default_port_from(instance)
```

### Mounting

The LustreFileSystem Construct exposes both the DNS name of the file system as well as its mount name, which can be
used to mount the file system on an EC2 instance. The following example shows how to bring up a file system and EC2
instance, and then use User Data to mount the file system on the instance at start-up:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
app = App()
stack = Stack(app, "AwsCdkFsxLustre")
vpc = Vpc(stack, "VPC")

lustre_configuration = {
    "deployment_type": LustreDeploymentType.SCRATCH_2
}
fs = LustreFileSystem(stack, "FsxLustreFileSystem",
    lustre_configuration=lustre_configuration,
    storage_capacity_gi_b=1200,
    vpc=vpc,
    vpc_subnet=vpc.privateSubnets[0]
)

inst = Instance(stack, "inst",
    instance_type=InstanceType.of(InstanceClass.T2, InstanceSize.LARGE),
    machine_image=AmazonLinuxImage(
        generation=AmazonLinuxGeneration.AMAZON_LINUX_2
    ),
    vpc=vpc,
    vpc_subnets={
        "subnet_type": SubnetType.PUBLIC
    }
)
fs.connections.allow_default_port_from(inst)

# Need to give the instance access to read information about FSx to determine the file system's mount name.
inst.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonFSxReadOnlyAccess"))

mount_path = "/mnt/fsx"
dns_name = fs.dns_name
mount_name = fs.mount_name

inst.user_data.add_commands("set -eux", "yum update -y", "amazon-linux-extras install -y lustre2.10", f"mkdir -p {mountPath}", f"chmod 777 {mountPath}", f"chown ec2-user:ec2-user {mountPath}", f"echo \"{dnsName}@tcp:/{mountName} {mountPath} lustre defaults,noatime,flock,_netdev 0 0\" >> /etc/fstab", "mount -a")
```

### Importing

An FSx for Lustre file system can be imported with `fromLustreFileSystemAttributes(stack, id, attributes)`. The
following example lays out how you could import the SecurityGroup a file system belongs to, use that to import the file
system, and then also import the VPC the file system is in and add an EC2 instance to it, giving it access to the file
system.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
app = App()
stack = Stack(app, "AwsCdkFsxLustreImport")

sg = SecurityGroup.from_security_group_id(stack, "FsxSecurityGroup", "{SECURITY-GROUP-ID}")
fs = LustreFileSystem.from_lustre_file_system_attributes(stack, "FsxLustreFileSystem",
    dns_name="{FILE-SYSTEM-DNS-NAME}",
    file_system_id="{FILE-SYSTEM-ID}",
    security_group=sg
)

vpc = Vpc.from_vpc_attributes(stack, "Vpc",
    availability_zones=["us-west-2a", "us-west-2b"],
    public_subnet_ids=["{US-WEST-2A-SUBNET-ID}", "{US-WEST-2B-SUBNET-ID}"],
    vpc_id="{VPC-ID}"
)
inst = Instance(stack, "inst",
    instance_type=InstanceType.of(InstanceClass.T2, InstanceSize.LARGE),
    machine_image=AmazonLinuxImage(
        generation=AmazonLinuxGeneration.AMAZON_LINUX_2
    ),
    vpc=vpc,
    vpc_subnets={
        "subnet_type": SubnetType.PUBLIC
    }
)
fs.connections.allow_default_port_from(inst)
```

## FSx for Windows File Server

The L2 construct for the FSx for Windows File Server has not yet been implemented. To instantiate an FSx for Windows
file system, the L1 constructs can be used as defined by CloudFormation.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from .. import (
    CfnResource as _CfnResource_e0a482dc,
    CfnTag as _CfnTag_95fbdc29,
    Construct as _Construct_e78e779f,
    IInspectable as _IInspectable_82c04a63,
    IResolvable as _IResolvable_a771d0ef,
    RemovalPolicy as _RemovalPolicy_c97e7a20,
    Resource as _Resource_abff4495,
    ResourceProps as _ResourceProps_9b554c0f,
    TagManager as _TagManager_0b7ab120,
    TreeInspector as _TreeInspector_1cd1894e,
)
from ..aws_ec2 import (
    Connections as _Connections_57ccbda9,
    IConnectable as _IConnectable_c1c0e72c,
    ISecurityGroup as _ISecurityGroup_cdbba9d3,
    ISubnet as _ISubnet_0a12f914,
    IVpc as _IVpc_6d1f76c4,
)
from ..aws_kms import IKey as _IKey_36930160


@jsii.implements(_IInspectable_82c04a63)
class CfnFileSystem(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_fsx.CfnFileSystem",
):
    '''A CloudFormation ``AWS::FSx::FileSystem``.

    :cloudformationResource: AWS::FSx::FileSystem
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        file_system_type: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        backup_id: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        lustre_configuration: typing.Optional[typing.Union["CfnFileSystem.LustreConfigurationProperty", _IResolvable_a771d0ef]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
        windows_configuration: typing.Optional[typing.Union["CfnFileSystem.WindowsConfigurationProperty", _IResolvable_a771d0ef]] = None,
    ) -> None:
        '''Create a new ``AWS::FSx::FileSystem``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param file_system_type: ``AWS::FSx::FileSystem.FileSystemType``.
        :param subnet_ids: ``AWS::FSx::FileSystem.SubnetIds``.
        :param backup_id: ``AWS::FSx::FileSystem.BackupId``.
        :param kms_key_id: ``AWS::FSx::FileSystem.KmsKeyId``.
        :param lustre_configuration: ``AWS::FSx::FileSystem.LustreConfiguration``.
        :param security_group_ids: ``AWS::FSx::FileSystem.SecurityGroupIds``.
        :param storage_capacity: ``AWS::FSx::FileSystem.StorageCapacity``.
        :param storage_type: ``AWS::FSx::FileSystem.StorageType``.
        :param tags: ``AWS::FSx::FileSystem.Tags``.
        :param windows_configuration: ``AWS::FSx::FileSystem.WindowsConfiguration``.
        '''
        props = CfnFileSystemProps(
            file_system_type=file_system_type,
            subnet_ids=subnet_ids,
            backup_id=backup_id,
            kms_key_id=kms_key_id,
            lustre_configuration=lustre_configuration,
            security_group_ids=security_group_ids,
            storage_capacity=storage_capacity,
            storage_type=storage_type,
            tags=tags,
            windows_configuration=windows_configuration,
        )

        jsii.create(CfnFileSystem, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_1cd1894e) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrDnsName")
    def attr_dns_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: DNSName
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLustreMountName")
    def attr_lustre_mount_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: LustreMountName
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrLustreMountName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''``AWS::FSx::FileSystem.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemType")
    def file_system_type(self) -> builtins.str:
        '''``AWS::FSx::FileSystem.FileSystemType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-filesystemtype
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemType"))

    @file_system_type.setter
    def file_system_type(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::FSx::FileSystem.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-subnetids
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupId")
    def backup_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::FSx::FileSystem.BackupId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-backupid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupId"))

    @backup_id.setter
    def backup_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "backupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::FSx::FileSystem.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-kmskeyid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lustreConfiguration")
    def lustre_configuration(
        self,
    ) -> typing.Optional[typing.Union["CfnFileSystem.LustreConfigurationProperty", _IResolvable_a771d0ef]]:
        '''``AWS::FSx::FileSystem.LustreConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-lustreconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnFileSystem.LustreConfigurationProperty", _IResolvable_a771d0ef]], jsii.get(self, "lustreConfiguration"))

    @lustre_configuration.setter
    def lustre_configuration(
        self,
        value: typing.Optional[typing.Union["CfnFileSystem.LustreConfigurationProperty", _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "lustreConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::FSx::FileSystem.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-securitygroupids
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacity")
    def storage_capacity(self) -> typing.Optional[jsii.Number]:
        '''``AWS::FSx::FileSystem.StorageCapacity``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagecapacity
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageCapacity"))

    @storage_capacity.setter
    def storage_capacity(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "storageCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::FSx::FileSystem.StorageType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagetype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageType"))

    @storage_type.setter
    def storage_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "storageType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="windowsConfiguration")
    def windows_configuration(
        self,
    ) -> typing.Optional[typing.Union["CfnFileSystem.WindowsConfigurationProperty", _IResolvable_a771d0ef]]:
        '''``AWS::FSx::FileSystem.WindowsConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-windowsconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnFileSystem.WindowsConfigurationProperty", _IResolvable_a771d0ef]], jsii.get(self, "windowsConfiguration"))

    @windows_configuration.setter
    def windows_configuration(
        self,
        value: typing.Optional[typing.Union["CfnFileSystem.WindowsConfigurationProperty", _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "windowsConfiguration", value)

    @jsii.data_type(
        jsii_type="monocdk.aws_fsx.CfnFileSystem.AuditLogConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "file_access_audit_log_level": "fileAccessAuditLogLevel",
            "file_share_access_audit_log_level": "fileShareAccessAuditLogLevel",
            "audit_log_destination": "auditLogDestination",
        },
    )
    class AuditLogConfigurationProperty:
        def __init__(
            self,
            *,
            file_access_audit_log_level: builtins.str,
            file_share_access_audit_log_level: builtins.str,
            audit_log_destination: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param file_access_audit_log_level: ``CfnFileSystem.AuditLogConfigurationProperty.FileAccessAuditLogLevel``.
            :param file_share_access_audit_log_level: ``CfnFileSystem.AuditLogConfigurationProperty.FileShareAccessAuditLogLevel``.
            :param audit_log_destination: ``CfnFileSystem.AuditLogConfigurationProperty.AuditLogDestination``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-auditlogconfiguration.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "file_access_audit_log_level": file_access_audit_log_level,
                "file_share_access_audit_log_level": file_share_access_audit_log_level,
            }
            if audit_log_destination is not None:
                self._values["audit_log_destination"] = audit_log_destination

        @builtins.property
        def file_access_audit_log_level(self) -> builtins.str:
            '''``CfnFileSystem.AuditLogConfigurationProperty.FileAccessAuditLogLevel``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-auditlogconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-auditlogconfiguration-fileaccessauditloglevel
            '''
            result = self._values.get("file_access_audit_log_level")
            assert result is not None, "Required property 'file_access_audit_log_level' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def file_share_access_audit_log_level(self) -> builtins.str:
            '''``CfnFileSystem.AuditLogConfigurationProperty.FileShareAccessAuditLogLevel``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-auditlogconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-auditlogconfiguration-fileshareaccessauditloglevel
            '''
            result = self._values.get("file_share_access_audit_log_level")
            assert result is not None, "Required property 'file_share_access_audit_log_level' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def audit_log_destination(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.AuditLogConfigurationProperty.AuditLogDestination``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-auditlogconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-auditlogconfiguration-auditlogdestination
            '''
            result = self._values.get("audit_log_destination")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AuditLogConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="monocdk.aws_fsx.CfnFileSystem.LustreConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "auto_import_policy": "autoImportPolicy",
            "automatic_backup_retention_days": "automaticBackupRetentionDays",
            "copy_tags_to_backups": "copyTagsToBackups",
            "daily_automatic_backup_start_time": "dailyAutomaticBackupStartTime",
            "data_compression_type": "dataCompressionType",
            "deployment_type": "deploymentType",
            "drive_cache_type": "driveCacheType",
            "export_path": "exportPath",
            "imported_file_chunk_size": "importedFileChunkSize",
            "import_path": "importPath",
            "per_unit_storage_throughput": "perUnitStorageThroughput",
            "weekly_maintenance_start_time": "weeklyMaintenanceStartTime",
        },
    )
    class LustreConfigurationProperty:
        def __init__(
            self,
            *,
            auto_import_policy: typing.Optional[builtins.str] = None,
            automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
            copy_tags_to_backups: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
            daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
            data_compression_type: typing.Optional[builtins.str] = None,
            deployment_type: typing.Optional[builtins.str] = None,
            drive_cache_type: typing.Optional[builtins.str] = None,
            export_path: typing.Optional[builtins.str] = None,
            imported_file_chunk_size: typing.Optional[jsii.Number] = None,
            import_path: typing.Optional[builtins.str] = None,
            per_unit_storage_throughput: typing.Optional[jsii.Number] = None,
            weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param auto_import_policy: ``CfnFileSystem.LustreConfigurationProperty.AutoImportPolicy``.
            :param automatic_backup_retention_days: ``CfnFileSystem.LustreConfigurationProperty.AutomaticBackupRetentionDays``.
            :param copy_tags_to_backups: ``CfnFileSystem.LustreConfigurationProperty.CopyTagsToBackups``.
            :param daily_automatic_backup_start_time: ``CfnFileSystem.LustreConfigurationProperty.DailyAutomaticBackupStartTime``.
            :param data_compression_type: ``CfnFileSystem.LustreConfigurationProperty.DataCompressionType``.
            :param deployment_type: ``CfnFileSystem.LustreConfigurationProperty.DeploymentType``.
            :param drive_cache_type: ``CfnFileSystem.LustreConfigurationProperty.DriveCacheType``.
            :param export_path: ``CfnFileSystem.LustreConfigurationProperty.ExportPath``.
            :param imported_file_chunk_size: ``CfnFileSystem.LustreConfigurationProperty.ImportedFileChunkSize``.
            :param import_path: ``CfnFileSystem.LustreConfigurationProperty.ImportPath``.
            :param per_unit_storage_throughput: ``CfnFileSystem.LustreConfigurationProperty.PerUnitStorageThroughput``.
            :param weekly_maintenance_start_time: ``CfnFileSystem.LustreConfigurationProperty.WeeklyMaintenanceStartTime``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if auto_import_policy is not None:
                self._values["auto_import_policy"] = auto_import_policy
            if automatic_backup_retention_days is not None:
                self._values["automatic_backup_retention_days"] = automatic_backup_retention_days
            if copy_tags_to_backups is not None:
                self._values["copy_tags_to_backups"] = copy_tags_to_backups
            if daily_automatic_backup_start_time is not None:
                self._values["daily_automatic_backup_start_time"] = daily_automatic_backup_start_time
            if data_compression_type is not None:
                self._values["data_compression_type"] = data_compression_type
            if deployment_type is not None:
                self._values["deployment_type"] = deployment_type
            if drive_cache_type is not None:
                self._values["drive_cache_type"] = drive_cache_type
            if export_path is not None:
                self._values["export_path"] = export_path
            if imported_file_chunk_size is not None:
                self._values["imported_file_chunk_size"] = imported_file_chunk_size
            if import_path is not None:
                self._values["import_path"] = import_path
            if per_unit_storage_throughput is not None:
                self._values["per_unit_storage_throughput"] = per_unit_storage_throughput
            if weekly_maintenance_start_time is not None:
                self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

        @builtins.property
        def auto_import_policy(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.LustreConfigurationProperty.AutoImportPolicy``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-autoimportpolicy
            '''
            result = self._values.get("auto_import_policy")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def automatic_backup_retention_days(self) -> typing.Optional[jsii.Number]:
            '''``CfnFileSystem.LustreConfigurationProperty.AutomaticBackupRetentionDays``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-automaticbackupretentiondays
            '''
            result = self._values.get("automatic_backup_retention_days")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def copy_tags_to_backups(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
            '''``CfnFileSystem.LustreConfigurationProperty.CopyTagsToBackups``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-copytagstobackups
            '''
            result = self._values.get("copy_tags_to_backups")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

        @builtins.property
        def daily_automatic_backup_start_time(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.LustreConfigurationProperty.DailyAutomaticBackupStartTime``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-dailyautomaticbackupstarttime
            '''
            result = self._values.get("daily_automatic_backup_start_time")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def data_compression_type(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.LustreConfigurationProperty.DataCompressionType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-datacompressiontype
            '''
            result = self._values.get("data_compression_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def deployment_type(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.LustreConfigurationProperty.DeploymentType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-deploymenttype
            '''
            result = self._values.get("deployment_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def drive_cache_type(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.LustreConfigurationProperty.DriveCacheType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-drivecachetype
            '''
            result = self._values.get("drive_cache_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def export_path(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.LustreConfigurationProperty.ExportPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-exportpath
            '''
            result = self._values.get("export_path")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def imported_file_chunk_size(self) -> typing.Optional[jsii.Number]:
            '''``CfnFileSystem.LustreConfigurationProperty.ImportedFileChunkSize``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-importedfilechunksize
            '''
            result = self._values.get("imported_file_chunk_size")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def import_path(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.LustreConfigurationProperty.ImportPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-importpath
            '''
            result = self._values.get("import_path")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def per_unit_storage_throughput(self) -> typing.Optional[jsii.Number]:
            '''``CfnFileSystem.LustreConfigurationProperty.PerUnitStorageThroughput``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-perunitstoragethroughput
            '''
            result = self._values.get("per_unit_storage_throughput")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def weekly_maintenance_start_time(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.LustreConfigurationProperty.WeeklyMaintenanceStartTime``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-weeklymaintenancestarttime
            '''
            result = self._values.get("weekly_maintenance_start_time")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LustreConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="monocdk.aws_fsx.CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "dns_ips": "dnsIps",
            "domain_name": "domainName",
            "file_system_administrators_group": "fileSystemAdministratorsGroup",
            "organizational_unit_distinguished_name": "organizationalUnitDistinguishedName",
            "password": "password",
            "user_name": "userName",
        },
    )
    class SelfManagedActiveDirectoryConfigurationProperty:
        def __init__(
            self,
            *,
            dns_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
            domain_name: typing.Optional[builtins.str] = None,
            file_system_administrators_group: typing.Optional[builtins.str] = None,
            organizational_unit_distinguished_name: typing.Optional[builtins.str] = None,
            password: typing.Optional[builtins.str] = None,
            user_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param dns_ips: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.DnsIps``.
            :param domain_name: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.DomainName``.
            :param file_system_administrators_group: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.FileSystemAdministratorsGroup``.
            :param organizational_unit_distinguished_name: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.OrganizationalUnitDistinguishedName``.
            :param password: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.Password``.
            :param user_name: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.UserName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if dns_ips is not None:
                self._values["dns_ips"] = dns_ips
            if domain_name is not None:
                self._values["domain_name"] = domain_name
            if file_system_administrators_group is not None:
                self._values["file_system_administrators_group"] = file_system_administrators_group
            if organizational_unit_distinguished_name is not None:
                self._values["organizational_unit_distinguished_name"] = organizational_unit_distinguished_name
            if password is not None:
                self._values["password"] = password
            if user_name is not None:
                self._values["user_name"] = user_name

        @builtins.property
        def dns_ips(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.DnsIps``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-dnsips
            '''
            result = self._values.get("dns_ips")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def domain_name(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.DomainName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-domainname
            '''
            result = self._values.get("domain_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def file_system_administrators_group(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.FileSystemAdministratorsGroup``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-filesystemadministratorsgroup
            '''
            result = self._values.get("file_system_administrators_group")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def organizational_unit_distinguished_name(
            self,
        ) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.OrganizationalUnitDistinguishedName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-organizationalunitdistinguishedname
            '''
            result = self._values.get("organizational_unit_distinguished_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def password(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.Password``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-password
            '''
            result = self._values.get("password")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def user_name(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.UserName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-username
            '''
            result = self._values.get("user_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SelfManagedActiveDirectoryConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="monocdk.aws_fsx.CfnFileSystem.WindowsConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "throughput_capacity": "throughputCapacity",
            "active_directory_id": "activeDirectoryId",
            "aliases": "aliases",
            "audit_log_configuration": "auditLogConfiguration",
            "automatic_backup_retention_days": "automaticBackupRetentionDays",
            "copy_tags_to_backups": "copyTagsToBackups",
            "daily_automatic_backup_start_time": "dailyAutomaticBackupStartTime",
            "deployment_type": "deploymentType",
            "preferred_subnet_id": "preferredSubnetId",
            "self_managed_active_directory_configuration": "selfManagedActiveDirectoryConfiguration",
            "weekly_maintenance_start_time": "weeklyMaintenanceStartTime",
        },
    )
    class WindowsConfigurationProperty:
        def __init__(
            self,
            *,
            throughput_capacity: jsii.Number,
            active_directory_id: typing.Optional[builtins.str] = None,
            aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
            audit_log_configuration: typing.Optional[typing.Union["CfnFileSystem.AuditLogConfigurationProperty", _IResolvable_a771d0ef]] = None,
            automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
            copy_tags_to_backups: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
            daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
            deployment_type: typing.Optional[builtins.str] = None,
            preferred_subnet_id: typing.Optional[builtins.str] = None,
            self_managed_active_directory_configuration: typing.Optional[typing.Union["CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty", _IResolvable_a771d0ef]] = None,
            weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param throughput_capacity: ``CfnFileSystem.WindowsConfigurationProperty.ThroughputCapacity``.
            :param active_directory_id: ``CfnFileSystem.WindowsConfigurationProperty.ActiveDirectoryId``.
            :param aliases: ``CfnFileSystem.WindowsConfigurationProperty.Aliases``.
            :param audit_log_configuration: ``CfnFileSystem.WindowsConfigurationProperty.AuditLogConfiguration``.
            :param automatic_backup_retention_days: ``CfnFileSystem.WindowsConfigurationProperty.AutomaticBackupRetentionDays``.
            :param copy_tags_to_backups: ``CfnFileSystem.WindowsConfigurationProperty.CopyTagsToBackups``.
            :param daily_automatic_backup_start_time: ``CfnFileSystem.WindowsConfigurationProperty.DailyAutomaticBackupStartTime``.
            :param deployment_type: ``CfnFileSystem.WindowsConfigurationProperty.DeploymentType``.
            :param preferred_subnet_id: ``CfnFileSystem.WindowsConfigurationProperty.PreferredSubnetId``.
            :param self_managed_active_directory_configuration: ``CfnFileSystem.WindowsConfigurationProperty.SelfManagedActiveDirectoryConfiguration``.
            :param weekly_maintenance_start_time: ``CfnFileSystem.WindowsConfigurationProperty.WeeklyMaintenanceStartTime``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "throughput_capacity": throughput_capacity,
            }
            if active_directory_id is not None:
                self._values["active_directory_id"] = active_directory_id
            if aliases is not None:
                self._values["aliases"] = aliases
            if audit_log_configuration is not None:
                self._values["audit_log_configuration"] = audit_log_configuration
            if automatic_backup_retention_days is not None:
                self._values["automatic_backup_retention_days"] = automatic_backup_retention_days
            if copy_tags_to_backups is not None:
                self._values["copy_tags_to_backups"] = copy_tags_to_backups
            if daily_automatic_backup_start_time is not None:
                self._values["daily_automatic_backup_start_time"] = daily_automatic_backup_start_time
            if deployment_type is not None:
                self._values["deployment_type"] = deployment_type
            if preferred_subnet_id is not None:
                self._values["preferred_subnet_id"] = preferred_subnet_id
            if self_managed_active_directory_configuration is not None:
                self._values["self_managed_active_directory_configuration"] = self_managed_active_directory_configuration
            if weekly_maintenance_start_time is not None:
                self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

        @builtins.property
        def throughput_capacity(self) -> jsii.Number:
            '''``CfnFileSystem.WindowsConfigurationProperty.ThroughputCapacity``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-throughputcapacity
            '''
            result = self._values.get("throughput_capacity")
            assert result is not None, "Required property 'throughput_capacity' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def active_directory_id(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.WindowsConfigurationProperty.ActiveDirectoryId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-activedirectoryid
            '''
            result = self._values.get("active_directory_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def aliases(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnFileSystem.WindowsConfigurationProperty.Aliases``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-aliases
            '''
            result = self._values.get("aliases")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def audit_log_configuration(
            self,
        ) -> typing.Optional[typing.Union["CfnFileSystem.AuditLogConfigurationProperty", _IResolvable_a771d0ef]]:
            '''``CfnFileSystem.WindowsConfigurationProperty.AuditLogConfiguration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-auditlogconfiguration
            '''
            result = self._values.get("audit_log_configuration")
            return typing.cast(typing.Optional[typing.Union["CfnFileSystem.AuditLogConfigurationProperty", _IResolvable_a771d0ef]], result)

        @builtins.property
        def automatic_backup_retention_days(self) -> typing.Optional[jsii.Number]:
            '''``CfnFileSystem.WindowsConfigurationProperty.AutomaticBackupRetentionDays``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-automaticbackupretentiondays
            '''
            result = self._values.get("automatic_backup_retention_days")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def copy_tags_to_backups(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
            '''``CfnFileSystem.WindowsConfigurationProperty.CopyTagsToBackups``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-copytagstobackups
            '''
            result = self._values.get("copy_tags_to_backups")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

        @builtins.property
        def daily_automatic_backup_start_time(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.WindowsConfigurationProperty.DailyAutomaticBackupStartTime``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-dailyautomaticbackupstarttime
            '''
            result = self._values.get("daily_automatic_backup_start_time")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def deployment_type(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.WindowsConfigurationProperty.DeploymentType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-deploymenttype
            '''
            result = self._values.get("deployment_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def preferred_subnet_id(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.WindowsConfigurationProperty.PreferredSubnetId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-preferredsubnetid
            '''
            result = self._values.get("preferred_subnet_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def self_managed_active_directory_configuration(
            self,
        ) -> typing.Optional[typing.Union["CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty", _IResolvable_a771d0ef]]:
            '''``CfnFileSystem.WindowsConfigurationProperty.SelfManagedActiveDirectoryConfiguration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration
            '''
            result = self._values.get("self_managed_active_directory_configuration")
            return typing.cast(typing.Optional[typing.Union["CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty", _IResolvable_a771d0ef]], result)

        @builtins.property
        def weekly_maintenance_start_time(self) -> typing.Optional[builtins.str]:
            '''``CfnFileSystem.WindowsConfigurationProperty.WeeklyMaintenanceStartTime``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-weeklymaintenancestarttime
            '''
            result = self._values.get("weekly_maintenance_start_time")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "WindowsConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="monocdk.aws_fsx.CfnFileSystemProps",
    jsii_struct_bases=[],
    name_mapping={
        "file_system_type": "fileSystemType",
        "subnet_ids": "subnetIds",
        "backup_id": "backupId",
        "kms_key_id": "kmsKeyId",
        "lustre_configuration": "lustreConfiguration",
        "security_group_ids": "securityGroupIds",
        "storage_capacity": "storageCapacity",
        "storage_type": "storageType",
        "tags": "tags",
        "windows_configuration": "windowsConfiguration",
    },
)
class CfnFileSystemProps:
    def __init__(
        self,
        *,
        file_system_type: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        backup_id: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        lustre_configuration: typing.Optional[typing.Union[CfnFileSystem.LustreConfigurationProperty, _IResolvable_a771d0ef]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
        windows_configuration: typing.Optional[typing.Union[CfnFileSystem.WindowsConfigurationProperty, _IResolvable_a771d0ef]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::FSx::FileSystem``.

        :param file_system_type: ``AWS::FSx::FileSystem.FileSystemType``.
        :param subnet_ids: ``AWS::FSx::FileSystem.SubnetIds``.
        :param backup_id: ``AWS::FSx::FileSystem.BackupId``.
        :param kms_key_id: ``AWS::FSx::FileSystem.KmsKeyId``.
        :param lustre_configuration: ``AWS::FSx::FileSystem.LustreConfiguration``.
        :param security_group_ids: ``AWS::FSx::FileSystem.SecurityGroupIds``.
        :param storage_capacity: ``AWS::FSx::FileSystem.StorageCapacity``.
        :param storage_type: ``AWS::FSx::FileSystem.StorageType``.
        :param tags: ``AWS::FSx::FileSystem.Tags``.
        :param windows_configuration: ``AWS::FSx::FileSystem.WindowsConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "file_system_type": file_system_type,
            "subnet_ids": subnet_ids,
        }
        if backup_id is not None:
            self._values["backup_id"] = backup_id
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if lustre_configuration is not None:
            self._values["lustre_configuration"] = lustre_configuration
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if storage_capacity is not None:
            self._values["storage_capacity"] = storage_capacity
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if tags is not None:
            self._values["tags"] = tags
        if windows_configuration is not None:
            self._values["windows_configuration"] = windows_configuration

    @builtins.property
    def file_system_type(self) -> builtins.str:
        '''``AWS::FSx::FileSystem.FileSystemType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-filesystemtype
        '''
        result = self._values.get("file_system_type")
        assert result is not None, "Required property 'file_system_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::FSx::FileSystem.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-subnetids
        '''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def backup_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::FSx::FileSystem.BackupId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-backupid
        '''
        result = self._values.get("backup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::FSx::FileSystem.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-kmskeyid
        '''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lustre_configuration(
        self,
    ) -> typing.Optional[typing.Union[CfnFileSystem.LustreConfigurationProperty, _IResolvable_a771d0ef]]:
        '''``AWS::FSx::FileSystem.LustreConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-lustreconfiguration
        '''
        result = self._values.get("lustre_configuration")
        return typing.cast(typing.Optional[typing.Union[CfnFileSystem.LustreConfigurationProperty, _IResolvable_a771d0ef]], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::FSx::FileSystem.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-securitygroupids
        '''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def storage_capacity(self) -> typing.Optional[jsii.Number]:
        '''``AWS::FSx::FileSystem.StorageCapacity``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagecapacity
        '''
        result = self._values.get("storage_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::FSx::FileSystem.StorageType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagetype
        '''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''``AWS::FSx::FileSystem.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    @builtins.property
    def windows_configuration(
        self,
    ) -> typing.Optional[typing.Union[CfnFileSystem.WindowsConfigurationProperty, _IResolvable_a771d0ef]]:
        '''``AWS::FSx::FileSystem.WindowsConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-windowsconfiguration
        '''
        result = self._values.get("windows_configuration")
        return typing.cast(typing.Optional[typing.Union[CfnFileSystem.WindowsConfigurationProperty, _IResolvable_a771d0ef]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFileSystemProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_fsx.FileSystemAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "dns_name": "dnsName",
        "file_system_id": "fileSystemId",
        "security_group": "securityGroup",
    },
)
class FileSystemAttributes:
    def __init__(
        self,
        *,
        dns_name: builtins.str,
        file_system_id: builtins.str,
        security_group: _ISecurityGroup_cdbba9d3,
    ) -> None:
        '''(experimental) Properties that describe an existing FSx file system.

        :param dns_name: (experimental) The DNS name assigned to this file system.
        :param file_system_id: (experimental) The ID of the file system, assigned by Amazon FSx.
        :param security_group: (experimental) The security group of the file system.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dns_name": dns_name,
            "file_system_id": file_system_id,
            "security_group": security_group,
        }

    @builtins.property
    def dns_name(self) -> builtins.str:
        '''(experimental) The DNS name assigned to this file system.

        :stability: experimental
        '''
        result = self._values.get("dns_name")
        assert result is not None, "Required property 'dns_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_system_id(self) -> builtins.str:
        '''(experimental) The ID of the file system, assigned by Amazon FSx.

        :stability: experimental
        '''
        result = self._values.get("file_system_id")
        assert result is not None, "Required property 'file_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(self) -> _ISecurityGroup_cdbba9d3:
        '''(experimental) The security group of the file system.

        :stability: experimental
        '''
        result = self._values.get("security_group")
        assert result is not None, "Required property 'security_group' is missing"
        return typing.cast(_ISecurityGroup_cdbba9d3, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileSystemAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_fsx.FileSystemProps",
    jsii_struct_bases=[],
    name_mapping={
        "storage_capacity_gib": "storageCapacityGiB",
        "vpc": "vpc",
        "backup_id": "backupId",
        "kms_key": "kmsKey",
        "removal_policy": "removalPolicy",
        "security_group": "securityGroup",
    },
)
class FileSystemProps:
    def __init__(
        self,
        *,
        storage_capacity_gib: jsii.Number,
        vpc: _IVpc_6d1f76c4,
        backup_id: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_IKey_36930160] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
        security_group: typing.Optional[_ISecurityGroup_cdbba9d3] = None,
    ) -> None:
        '''(experimental) Properties for the FSx file system.

        :param storage_capacity_gib: (experimental) The storage capacity of the file system being created. For Windows file systems, valid values are 32 GiB to 65,536 GiB. For SCRATCH_1 deployment types, valid values are 1,200, 2,400, 3,600, then continuing in increments of 3,600 GiB. For SCRATCH_2 and PERSISTENT_1 types, valid values are 1,200, 2,400, then continuing in increments of 2,400 GiB.
        :param vpc: (experimental) The VPC to launch the file system in.
        :param backup_id: (experimental) The ID of the backup. Specifies the backup to use if you're creating a file system from an existing backup. Default: - no backup will be used.
        :param kms_key: (experimental) The KMS key used for encryption to protect your data at rest. Default: - the aws/fsx default KMS key for the AWS account being deployed into.
        :param removal_policy: (experimental) Policy to apply when the file system is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_group: (experimental) Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "storage_capacity_gib": storage_capacity_gib,
            "vpc": vpc,
        }
        if backup_id is not None:
            self._values["backup_id"] = backup_id
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_group is not None:
            self._values["security_group"] = security_group

    @builtins.property
    def storage_capacity_gib(self) -> jsii.Number:
        '''(experimental) The storage capacity of the file system being created.

        For Windows file systems, valid values are 32 GiB to 65,536 GiB.
        For SCRATCH_1 deployment types, valid values are 1,200, 2,400, 3,600, then continuing in increments of 3,600 GiB.
        For SCRATCH_2 and PERSISTENT_1 types, valid values are 1,200, 2,400, then continuing in increments of 2,400 GiB.

        :stability: experimental
        '''
        result = self._values.get("storage_capacity_gib")
        assert result is not None, "Required property 'storage_capacity_gib' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def vpc(self) -> _IVpc_6d1f76c4:
        '''(experimental) The VPC to launch the file system in.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_IVpc_6d1f76c4, result)

    @builtins.property
    def backup_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ID of the backup.

        Specifies the backup to use if you're creating a file system from an existing backup.

        :default: - no backup will be used.

        :stability: experimental
        '''
        result = self._values.get("backup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The KMS key used for encryption to protect your data at rest.

        :default: - the aws/fsx default KMS key for the AWS account being deployed into.

        :stability: experimental
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_RemovalPolicy_c97e7a20]:
        '''(experimental) Policy to apply when the file system is removed from the stack.

        :default: RemovalPolicy.RETAIN

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_RemovalPolicy_c97e7a20], result)

    @builtins.property
    def security_group(self) -> typing.Optional[_ISecurityGroup_cdbba9d3]:
        '''(experimental) Security Group to assign to this file system.

        :default: - creates new security group which allows all outbound traffic.

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_ISecurityGroup_cdbba9d3], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileSystemProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="monocdk.aws_fsx.IFileSystem")
class IFileSystem(_IConnectable_c1c0e72c, typing_extensions.Protocol):
    '''(experimental) Interface to implement FSx File Systems.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''(experimental) The ID of the file system, assigned by Amazon FSx.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IFileSystemProxy(
    jsii.proxy_for(_IConnectable_c1c0e72c) # type: ignore[misc]
):
    '''(experimental) Interface to implement FSx File Systems.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_fsx.IFileSystem"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''(experimental) The ID of the file system, assigned by Amazon FSx.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFileSystem).__jsii_proxy_class__ = lambda : _IFileSystemProxy


@jsii.data_type(
    jsii_type="monocdk.aws_fsx.LustreConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_type": "deploymentType",
        "export_path": "exportPath",
        "imported_file_chunk_size_mib": "importedFileChunkSizeMiB",
        "import_path": "importPath",
        "per_unit_storage_throughput": "perUnitStorageThroughput",
        "weekly_maintenance_start_time": "weeklyMaintenanceStartTime",
    },
)
class LustreConfiguration:
    def __init__(
        self,
        *,
        deployment_type: "LustreDeploymentType",
        export_path: typing.Optional[builtins.str] = None,
        imported_file_chunk_size_mib: typing.Optional[jsii.Number] = None,
        import_path: typing.Optional[builtins.str] = None,
        per_unit_storage_throughput: typing.Optional[jsii.Number] = None,
        weekly_maintenance_start_time: typing.Optional["LustreMaintenanceTime"] = None,
    ) -> None:
        '''(experimental) The configuration for the Amazon FSx for Lustre file system.

        :param deployment_type: (experimental) The type of backing file system deployment used by FSx.
        :param export_path: (experimental) The path in Amazon S3 where the root of your Amazon FSx file system is exported. The path must use the same Amazon S3 bucket as specified in ImportPath. If you only specify a bucket name, such as s3://import-bucket, you get a 1:1 mapping of file system objects to S3 bucket objects. This mapping means that the input data in S3 is overwritten on export. If you provide a custom prefix in the export path, such as s3://import-bucket/[custom-optional-prefix], Amazon FSx exports the contents of your file system to that export prefix in the Amazon S3 bucket. Default: s3://import-bucket/FSxLustre[creation-timestamp]
        :param imported_file_chunk_size_mib: (experimental) For files imported from a data repository, this value determines the stripe count and maximum amount of data per file (in MiB) stored on a single physical disk. Allowed values are between 1 and 512,000. Default: 1024
        :param import_path: (experimental) The path to the Amazon S3 bucket (including the optional prefix) that you're using as the data repository for your Amazon FSx for Lustre file system. Must be of the format "s3://{bucketName}/optional-prefix" and cannot exceed 900 characters. Default: - no bucket is imported
        :param per_unit_storage_throughput: (experimental) Required for the PERSISTENT_1 deployment type, describes the amount of read and write throughput for each 1 tebibyte of storage, in MB/s/TiB. Valid values are 50, 100, 200. Default: - no default, conditionally required for PERSISTENT_1 deployment type
        :param weekly_maintenance_start_time: (experimental) The preferred day and time to perform weekly maintenance. The first digit is the day of the week, starting at 1 for Monday, then the following are hours and minutes in the UTC time zone, 24 hour clock. For example: '2:20:30' is Tuesdays at 20:30. Default: - no preference

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "deployment_type": deployment_type,
        }
        if export_path is not None:
            self._values["export_path"] = export_path
        if imported_file_chunk_size_mib is not None:
            self._values["imported_file_chunk_size_mib"] = imported_file_chunk_size_mib
        if import_path is not None:
            self._values["import_path"] = import_path
        if per_unit_storage_throughput is not None:
            self._values["per_unit_storage_throughput"] = per_unit_storage_throughput
        if weekly_maintenance_start_time is not None:
            self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

    @builtins.property
    def deployment_type(self) -> "LustreDeploymentType":
        '''(experimental) The type of backing file system deployment used by FSx.

        :stability: experimental
        '''
        result = self._values.get("deployment_type")
        assert result is not None, "Required property 'deployment_type' is missing"
        return typing.cast("LustreDeploymentType", result)

    @builtins.property
    def export_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) The path in Amazon S3 where the root of your Amazon FSx file system is exported.

        The path must use the same
        Amazon S3 bucket as specified in ImportPath. If you only specify a bucket name, such as s3://import-bucket, you
        get a 1:1 mapping of file system objects to S3 bucket objects. This mapping means that the input data in S3 is
        overwritten on export. If you provide a custom prefix in the export path, such as
        s3://import-bucket/[custom-optional-prefix], Amazon FSx exports the contents of your file system to that export
        prefix in the Amazon S3 bucket.

        :default: s3://import-bucket/FSxLustre[creation-timestamp]

        :stability: experimental
        '''
        result = self._values.get("export_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def imported_file_chunk_size_mib(self) -> typing.Optional[jsii.Number]:
        '''(experimental) For files imported from a data repository, this value determines the stripe count and maximum amount of data per file (in MiB) stored on a single physical disk.

        Allowed values are between 1 and 512,000.

        :default: 1024

        :stability: experimental
        '''
        result = self._values.get("imported_file_chunk_size_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def import_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) The path to the Amazon S3 bucket (including the optional prefix) that you're using as the data repository for your Amazon FSx for Lustre file system.

        Must be of the format "s3://{bucketName}/optional-prefix" and cannot
        exceed 900 characters.

        :default: - no bucket is imported

        :stability: experimental
        '''
        result = self._values.get("import_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def per_unit_storage_throughput(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Required for the PERSISTENT_1 deployment type, describes the amount of read and write throughput for each 1 tebibyte of storage, in MB/s/TiB.

        Valid values are 50, 100, 200.

        :default: - no default, conditionally required for PERSISTENT_1 deployment type

        :stability: experimental
        '''
        result = self._values.get("per_unit_storage_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def weekly_maintenance_start_time(self) -> typing.Optional["LustreMaintenanceTime"]:
        '''(experimental) The preferred day and time to perform weekly maintenance.

        The first digit is the day of the week, starting at 1
        for Monday, then the following are hours and minutes in the UTC time zone, 24 hour clock. For example: '2:20:30'
        is Tuesdays at 20:30.

        :default: - no preference

        :stability: experimental
        '''
        result = self._values.get("weekly_maintenance_start_time")
        return typing.cast(typing.Optional["LustreMaintenanceTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LustreConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_fsx.LustreDeploymentType")
class LustreDeploymentType(enum.Enum):
    '''(experimental) The different kinds of file system deployments used by Lustre.

    :stability: experimental
    '''

    SCRATCH_1 = "SCRATCH_1"
    '''(experimental) Original type for shorter term data processing.

    Data is not replicated and does not persist on server fail.

    :stability: experimental
    '''
    SCRATCH_2 = "SCRATCH_2"
    '''(experimental) Newer type for shorter term data processing.

    Data is not replicated and does not persist on server fail.
    Provides better support for spiky workloads.

    :stability: experimental
    '''
    PERSISTENT_1 = "PERSISTENT_1"
    '''(experimental) Long term storage.

    Data is replicated and file servers are replaced if they fail.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="monocdk.aws_fsx.LustreFileSystemProps",
    jsii_struct_bases=[FileSystemProps],
    name_mapping={
        "storage_capacity_gib": "storageCapacityGiB",
        "vpc": "vpc",
        "backup_id": "backupId",
        "kms_key": "kmsKey",
        "removal_policy": "removalPolicy",
        "security_group": "securityGroup",
        "lustre_configuration": "lustreConfiguration",
        "vpc_subnet": "vpcSubnet",
    },
)
class LustreFileSystemProps(FileSystemProps):
    def __init__(
        self,
        *,
        storage_capacity_gib: jsii.Number,
        vpc: _IVpc_6d1f76c4,
        backup_id: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_IKey_36930160] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
        security_group: typing.Optional[_ISecurityGroup_cdbba9d3] = None,
        lustre_configuration: LustreConfiguration,
        vpc_subnet: _ISubnet_0a12f914,
    ) -> None:
        '''(experimental) Properties specific to the Lustre version of the FSx file system.

        :param storage_capacity_gib: (experimental) The storage capacity of the file system being created. For Windows file systems, valid values are 32 GiB to 65,536 GiB. For SCRATCH_1 deployment types, valid values are 1,200, 2,400, 3,600, then continuing in increments of 3,600 GiB. For SCRATCH_2 and PERSISTENT_1 types, valid values are 1,200, 2,400, then continuing in increments of 2,400 GiB.
        :param vpc: (experimental) The VPC to launch the file system in.
        :param backup_id: (experimental) The ID of the backup. Specifies the backup to use if you're creating a file system from an existing backup. Default: - no backup will be used.
        :param kms_key: (experimental) The KMS key used for encryption to protect your data at rest. Default: - the aws/fsx default KMS key for the AWS account being deployed into.
        :param removal_policy: (experimental) Policy to apply when the file system is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_group: (experimental) Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic.
        :param lustre_configuration: (experimental) Additional configuration for FSx specific to Lustre.
        :param vpc_subnet: (experimental) The subnet that the file system will be accessible from.

        :stability: experimental
        '''
        if isinstance(lustre_configuration, dict):
            lustre_configuration = LustreConfiguration(**lustre_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "storage_capacity_gib": storage_capacity_gib,
            "vpc": vpc,
            "lustre_configuration": lustre_configuration,
            "vpc_subnet": vpc_subnet,
        }
        if backup_id is not None:
            self._values["backup_id"] = backup_id
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_group is not None:
            self._values["security_group"] = security_group

    @builtins.property
    def storage_capacity_gib(self) -> jsii.Number:
        '''(experimental) The storage capacity of the file system being created.

        For Windows file systems, valid values are 32 GiB to 65,536 GiB.
        For SCRATCH_1 deployment types, valid values are 1,200, 2,400, 3,600, then continuing in increments of 3,600 GiB.
        For SCRATCH_2 and PERSISTENT_1 types, valid values are 1,200, 2,400, then continuing in increments of 2,400 GiB.

        :stability: experimental
        '''
        result = self._values.get("storage_capacity_gib")
        assert result is not None, "Required property 'storage_capacity_gib' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def vpc(self) -> _IVpc_6d1f76c4:
        '''(experimental) The VPC to launch the file system in.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_IVpc_6d1f76c4, result)

    @builtins.property
    def backup_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ID of the backup.

        Specifies the backup to use if you're creating a file system from an existing backup.

        :default: - no backup will be used.

        :stability: experimental
        '''
        result = self._values.get("backup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The KMS key used for encryption to protect your data at rest.

        :default: - the aws/fsx default KMS key for the AWS account being deployed into.

        :stability: experimental
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_RemovalPolicy_c97e7a20]:
        '''(experimental) Policy to apply when the file system is removed from the stack.

        :default: RemovalPolicy.RETAIN

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_RemovalPolicy_c97e7a20], result)

    @builtins.property
    def security_group(self) -> typing.Optional[_ISecurityGroup_cdbba9d3]:
        '''(experimental) Security Group to assign to this file system.

        :default: - creates new security group which allows all outbound traffic.

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_ISecurityGroup_cdbba9d3], result)

    @builtins.property
    def lustre_configuration(self) -> LustreConfiguration:
        '''(experimental) Additional configuration for FSx specific to Lustre.

        :stability: experimental
        '''
        result = self._values.get("lustre_configuration")
        assert result is not None, "Required property 'lustre_configuration' is missing"
        return typing.cast(LustreConfiguration, result)

    @builtins.property
    def vpc_subnet(self) -> _ISubnet_0a12f914:
        '''(experimental) The subnet that the file system will be accessible from.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnet")
        assert result is not None, "Required property 'vpc_subnet' is missing"
        return typing.cast(_ISubnet_0a12f914, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LustreFileSystemProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LustreMaintenanceTime(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_fsx.LustreMaintenanceTime",
):
    '''(experimental) Class for scheduling a weekly manitenance time.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        day: "Weekday",
        hour: jsii.Number,
        minute: jsii.Number,
    ) -> None:
        '''
        :param day: (experimental) The day of the week for maintenance to be performed.
        :param hour: (experimental) The hour of the day (from 0-24) for maintenance to be performed.
        :param minute: (experimental) The minute of the hour (from 0-59) for maintenance to be performed.

        :stability: experimental
        '''
        props = LustreMaintenanceTimeProps(day=day, hour=hour, minute=minute)

        jsii.create(LustreMaintenanceTime, self, [props])

    @jsii.member(jsii_name="toTimestamp")
    def to_timestamp(self) -> builtins.str:
        '''(experimental) Converts a day, hour, and minute into a timestamp as used by FSx for Lustre's weeklyMaintenanceStartTime field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toTimestamp", []))


@jsii.data_type(
    jsii_type="monocdk.aws_fsx.LustreMaintenanceTimeProps",
    jsii_struct_bases=[],
    name_mapping={"day": "day", "hour": "hour", "minute": "minute"},
)
class LustreMaintenanceTimeProps:
    def __init__(
        self,
        *,
        day: "Weekday",
        hour: jsii.Number,
        minute: jsii.Number,
    ) -> None:
        '''(experimental) Properties required for setting up a weekly maintenance time.

        :param day: (experimental) The day of the week for maintenance to be performed.
        :param hour: (experimental) The hour of the day (from 0-24) for maintenance to be performed.
        :param minute: (experimental) The minute of the hour (from 0-59) for maintenance to be performed.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "day": day,
            "hour": hour,
            "minute": minute,
        }

    @builtins.property
    def day(self) -> "Weekday":
        '''(experimental) The day of the week for maintenance to be performed.

        :stability: experimental
        '''
        result = self._values.get("day")
        assert result is not None, "Required property 'day' is missing"
        return typing.cast("Weekday", result)

    @builtins.property
    def hour(self) -> jsii.Number:
        '''(experimental) The hour of the day (from 0-24) for maintenance to be performed.

        :stability: experimental
        '''
        result = self._values.get("hour")
        assert result is not None, "Required property 'hour' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def minute(self) -> jsii.Number:
        '''(experimental) The minute of the hour (from 0-59) for maintenance to be performed.

        :stability: experimental
        '''
        result = self._values.get("minute")
        assert result is not None, "Required property 'minute' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LustreMaintenanceTimeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_fsx.Weekday")
class Weekday(enum.Enum):
    '''(experimental) Enum for representing all the days of the week.

    :stability: experimental
    '''

    MONDAY = "MONDAY"
    '''(experimental) Monday.

    :stability: experimental
    '''
    TUESDAY = "TUESDAY"
    '''(experimental) Tuesday.

    :stability: experimental
    '''
    WEDNESDAY = "WEDNESDAY"
    '''(experimental) Wednesday.

    :stability: experimental
    '''
    THURSDAY = "THURSDAY"
    '''(experimental) Thursday.

    :stability: experimental
    '''
    FRIDAY = "FRIDAY"
    '''(experimental) Friday.

    :stability: experimental
    '''
    SATURDAY = "SATURDAY"
    '''(experimental) Saturday.

    :stability: experimental
    '''
    SUNDAY = "SUNDAY"
    '''(experimental) Sunday.

    :stability: experimental
    '''


@jsii.implements(IFileSystem)
class FileSystemBase(
    _Resource_abff4495,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="monocdk.aws_fsx.FileSystemBase",
):
    '''(experimental) A new or imported FSx file system.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: (experimental) The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: (experimental) ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: (experimental) The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: (experimental) The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to

        :stability: experimental
        '''
        props = _ResourceProps_9b554c0f(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(FileSystemBase, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    @abc.abstractmethod
    def connections(self) -> _Connections_57ccbda9:
        '''(experimental) The security groups/rules used to allow network connections to the file system.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    @abc.abstractmethod
    def dns_name(self) -> builtins.str:
        '''(experimental) The DNS name assigned to this file system.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    @abc.abstractmethod
    def file_system_id(self) -> builtins.str:
        '''(experimental) The ID of the file system, assigned by Amazon FSx.

        :stability: experimental
        :attribute: true
        '''
        ...


class _FileSystemBaseProxy(
    FileSystemBase, jsii.proxy_for(_Resource_abff4495) # type: ignore[misc]
):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> _Connections_57ccbda9:
        '''(experimental) The security groups/rules used to allow network connections to the file system.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(_Connections_57ccbda9, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        '''(experimental) The DNS name assigned to this file system.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''(experimental) The ID of the file system, assigned by Amazon FSx.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, FileSystemBase).__jsii_proxy_class__ = lambda : _FileSystemBaseProxy


class LustreFileSystem(
    FileSystemBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_fsx.LustreFileSystem",
):
    '''(experimental) The FSx for Lustre File System implementation of IFileSystem.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
    :stability: experimental
    :resource: AWS::FSx::FileSystem
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        lustre_configuration: LustreConfiguration,
        vpc_subnet: _ISubnet_0a12f914,
        storage_capacity_gib: jsii.Number,
        vpc: _IVpc_6d1f76c4,
        backup_id: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_IKey_36930160] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
        security_group: typing.Optional[_ISecurityGroup_cdbba9d3] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param lustre_configuration: (experimental) Additional configuration for FSx specific to Lustre.
        :param vpc_subnet: (experimental) The subnet that the file system will be accessible from.
        :param storage_capacity_gib: (experimental) The storage capacity of the file system being created. For Windows file systems, valid values are 32 GiB to 65,536 GiB. For SCRATCH_1 deployment types, valid values are 1,200, 2,400, 3,600, then continuing in increments of 3,600 GiB. For SCRATCH_2 and PERSISTENT_1 types, valid values are 1,200, 2,400, then continuing in increments of 2,400 GiB.
        :param vpc: (experimental) The VPC to launch the file system in.
        :param backup_id: (experimental) The ID of the backup. Specifies the backup to use if you're creating a file system from an existing backup. Default: - no backup will be used.
        :param kms_key: (experimental) The KMS key used for encryption to protect your data at rest. Default: - the aws/fsx default KMS key for the AWS account being deployed into.
        :param removal_policy: (experimental) Policy to apply when the file system is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_group: (experimental) Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic.

        :stability: experimental
        '''
        props = LustreFileSystemProps(
            lustre_configuration=lustre_configuration,
            vpc_subnet=vpc_subnet,
            storage_capacity_gib=storage_capacity_gib,
            vpc=vpc,
            backup_id=backup_id,
            kms_key=kms_key,
            removal_policy=removal_policy,
            security_group=security_group,
        )

        jsii.create(LustreFileSystem, self, [scope, id, props])

    @jsii.member(jsii_name="fromLustreFileSystemAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_lustre_file_system_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        dns_name: builtins.str,
        file_system_id: builtins.str,
        security_group: _ISecurityGroup_cdbba9d3,
    ) -> IFileSystem:
        '''(experimental) Import an existing FSx for Lustre file system from the given properties.

        :param scope: -
        :param id: -
        :param dns_name: (experimental) The DNS name assigned to this file system.
        :param file_system_id: (experimental) The ID of the file system, assigned by Amazon FSx.
        :param security_group: (experimental) The security group of the file system.

        :stability: experimental
        '''
        attrs = FileSystemAttributes(
            dns_name=dns_name,
            file_system_id=file_system_id,
            security_group=security_group,
        )

        return typing.cast(IFileSystem, jsii.sinvoke(cls, "fromLustreFileSystemAttributes", [scope, id, attrs]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> _Connections_57ccbda9:
        '''(experimental) The security groups/rules used to allow network connections to the file system.

        :stability: experimental
        '''
        return typing.cast(_Connections_57ccbda9, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        '''(experimental) The DNS name assigned to this file system.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''(experimental) The ID that AWS assigns to the file system.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountName")
    def mount_name(self) -> builtins.str:
        '''(experimental) The mount name of the file system, generated by FSx.

        :stability: experimental
        :attribute: LustreMountName
        '''
        return typing.cast(builtins.str, jsii.get(self, "mountName"))


__all__ = [
    "CfnFileSystem",
    "CfnFileSystemProps",
    "FileSystemAttributes",
    "FileSystemBase",
    "FileSystemProps",
    "IFileSystem",
    "LustreConfiguration",
    "LustreDeploymentType",
    "LustreFileSystem",
    "LustreFileSystemProps",
    "LustreMaintenanceTime",
    "LustreMaintenanceTimeProps",
    "Weekday",
]

publication.publish()
