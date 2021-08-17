'''
# Amazon DocumentDB Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

## Starting a Clustered Database

To set up a clustered DocumentDB database, define a `DatabaseCluster`. You must
always launch a database in a VPC. Use the `vpcSubnets` attribute to control whether
your instances will be launched privately or publicly:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
cluster = DatabaseCluster(self, "Database",
    master_user={
        "username": "myuser"
    },
    instance_type=ec2.InstanceType.of(ec2.InstanceClass.R5, ec2.InstanceSize.LARGE),
    vpc_subnets={
        "subnet_type": ec2.SubnetType.PUBLIC
    },
    vpc=vpc
)
```

By default, the master password will be generated and stored in AWS Secrets Manager with auto-generated description.

Your cluster will be empty by default.

## Connecting

To control who can access the cluster, use the `.connections` attribute. DocumentDB databases have a default port, so
you don't need to specify the port:

```python
# Example automatically generated. See https://github.com/aws/jsii/issues/826
cluster.connections.allow_default_port_from_any_ipv4("Open to the world")
```

The endpoints to access your database cluster will be available as the `.clusterEndpoint` and `.clusterReadEndpoint`
attributes:

```python
# Example automatically generated. See https://github.com/aws/jsii/issues/826
write_address = cluster.cluster_endpoint.socket_address
```

If you have existing security groups you would like to add to the cluster, use the `addSecurityGroups` method. Security
groups added in this way will not be managed by the `Connections` object of the cluster.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
security_group = ec2.SecurityGroup(stack, "SecurityGroup",
    vpc=vpc
)
cluster.add_security_groups(security_group)
```

## Rotating credentials

When the master password is generated and stored in AWS Secrets Manager, it can be rotated automatically:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
cluster.add_rotation_single_user()
```

[example of setting up master password rotation for a cluster](test/integ.cluster-rotation.lit.ts)

The multi user rotation scheme is also available:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
cluster.add_rotation_multi_user("MyUser",
    secret=my_imported_secret
)
```

It's also possible to create user credentials together with the cluster and add rotation:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
my_user_secret = docdb.DatabaseSecret(self, "MyUserSecret",
    username="myuser",
    master_secret=cluster.secret
)
my_user_secret_attached = my_user_secret.attach(cluster)# Adds DB connections information in the secret

cluster.add_rotation_multi_user("MyUser", # Add rotation using the multi user scheme
    secret=my_user_secret_attached)
```

**Note**: This user must be created manually in the database using the master credentials.
The rotation will start as soon as this user exists.

See also [@aws-cdk/aws-secretsmanager](https://github.com/aws/aws-cdk/blob/master/packages/%40aws-cdk/aws-secretsmanager/README.md) for credentials rotation of existing clusters.
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
    Duration as _Duration_070aa057,
    IInspectable as _IInspectable_82c04a63,
    IResolvable as _IResolvable_a771d0ef,
    IResource as _IResource_8c1dbbbd,
    RemovalPolicy as _RemovalPolicy_c97e7a20,
    Resource as _Resource_abff4495,
    SecretValue as _SecretValue_c18506ef,
    TagManager as _TagManager_0b7ab120,
    TreeInspector as _TreeInspector_1cd1894e,
)
from ..aws_ec2 import (
    Connections as _Connections_57ccbda9,
    IConnectable as _IConnectable_c1c0e72c,
    ISecurityGroup as _ISecurityGroup_cdbba9d3,
    IVpc as _IVpc_6d1f76c4,
    InstanceType as _InstanceType_072ad323,
    SubnetSelection as _SubnetSelection_1284e62c,
)
from ..aws_kms import IKey as _IKey_36930160
from ..aws_secretsmanager import (
    ISecret as _ISecret_22fb8757,
    ISecretAttachmentTarget as _ISecretAttachmentTarget_b6932462,
    Secret as _Secret_cb33d4cc,
    SecretAttachmentTargetProps as _SecretAttachmentTargetProps_ab8522eb,
    SecretRotation as _SecretRotation_e64158ad,
)


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.BackupProps",
    jsii_struct_bases=[],
    name_mapping={"retention": "retention", "preferred_window": "preferredWindow"},
)
class BackupProps:
    def __init__(
        self,
        *,
        retention: _Duration_070aa057,
        preferred_window: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Backup configuration for DocumentDB databases.

        :param retention: (experimental) How many days to retain the backup.
        :param preferred_window: (experimental) A daily time range in 24-hours UTC format in which backups preferably execute. Must be at least 30 minutes long. Example: '01:00-02:00' Default: - a 30-minute window selected at random from an 8-hour block of time for each AWS Region. To see the time blocks available, see https://docs.aws.amazon.com/documentdb/latest/developerguide/backup-restore.db-cluster-snapshots.html#backup-restore.backup-window

        :default:

        - The retention period for automated backups is 1 day.
        The preferred backup window will be a 30-minute window selected at random
        from an 8-hour block of time for each AWS Region.

        :see: https://docs.aws.amazon.com/documentdb/latest/developerguide/backup-restore.db-cluster-snapshots.html#backup-restore.backup-window
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "retention": retention,
        }
        if preferred_window is not None:
            self._values["preferred_window"] = preferred_window

    @builtins.property
    def retention(self) -> _Duration_070aa057:
        '''(experimental) How many days to retain the backup.

        :stability: experimental
        '''
        result = self._values.get("retention")
        assert result is not None, "Required property 'retention' is missing"
        return typing.cast(_Duration_070aa057, result)

    @builtins.property
    def preferred_window(self) -> typing.Optional[builtins.str]:
        '''(experimental) A daily time range in 24-hours UTC format in which backups preferably execute.

        Must be at least 30 minutes long.

        Example: '01:00-02:00'

        :default:

        - a 30-minute window selected at random from an 8-hour block of
        time for each AWS Region. To see the time blocks available, see
        https://docs.aws.amazon.com/documentdb/latest/developerguide/backup-restore.db-cluster-snapshots.html#backup-restore.backup-window

        :stability: experimental
        '''
        result = self._values.get("preferred_window")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnDBCluster(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_docdb.CfnDBCluster",
):
    '''A CloudFormation ``AWS::DocDB::DBCluster``.

    :cloudformationResource: AWS::DocDB::DBCluster
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        master_username: builtins.str,
        master_user_password: builtins.str,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        backup_retention_period: typing.Optional[jsii.Number] = None,
        db_cluster_identifier: typing.Optional[builtins.str] = None,
        db_cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        enable_cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        engine_version: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Create a new ``AWS::DocDB::DBCluster``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param master_username: ``AWS::DocDB::DBCluster.MasterUsername``.
        :param master_user_password: ``AWS::DocDB::DBCluster.MasterUserPassword``.
        :param availability_zones: ``AWS::DocDB::DBCluster.AvailabilityZones``.
        :param backup_retention_period: ``AWS::DocDB::DBCluster.BackupRetentionPeriod``.
        :param db_cluster_identifier: ``AWS::DocDB::DBCluster.DBClusterIdentifier``.
        :param db_cluster_parameter_group_name: ``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.
        :param db_subnet_group_name: ``AWS::DocDB::DBCluster.DBSubnetGroupName``.
        :param deletion_protection: ``AWS::DocDB::DBCluster.DeletionProtection``.
        :param enable_cloudwatch_logs_exports: ``AWS::DocDB::DBCluster.EnableCloudwatchLogsExports``.
        :param engine_version: ``AWS::DocDB::DBCluster.EngineVersion``.
        :param kms_key_id: ``AWS::DocDB::DBCluster.KmsKeyId``.
        :param port: ``AWS::DocDB::DBCluster.Port``.
        :param preferred_backup_window: ``AWS::DocDB::DBCluster.PreferredBackupWindow``.
        :param preferred_maintenance_window: ``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.
        :param snapshot_identifier: ``AWS::DocDB::DBCluster.SnapshotIdentifier``.
        :param storage_encrypted: ``AWS::DocDB::DBCluster.StorageEncrypted``.
        :param tags: ``AWS::DocDB::DBCluster.Tags``.
        :param vpc_security_group_ids: ``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.
        '''
        props = CfnDBClusterProps(
            master_username=master_username,
            master_user_password=master_user_password,
            availability_zones=availability_zones,
            backup_retention_period=backup_retention_period,
            db_cluster_identifier=db_cluster_identifier,
            db_cluster_parameter_group_name=db_cluster_parameter_group_name,
            db_subnet_group_name=db_subnet_group_name,
            deletion_protection=deletion_protection,
            enable_cloudwatch_logs_exports=enable_cloudwatch_logs_exports,
            engine_version=engine_version,
            kms_key_id=kms_key_id,
            port=port,
            preferred_backup_window=preferred_backup_window,
            preferred_maintenance_window=preferred_maintenance_window,
            snapshot_identifier=snapshot_identifier,
            storage_encrypted=storage_encrypted,
            tags=tags,
            vpc_security_group_ids=vpc_security_group_ids,
        )

        jsii.create(CfnDBCluster, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrClusterResourceId")
    def attr_cluster_resource_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: ClusterResourceId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrClusterResourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> builtins.str:
        '''
        :cloudformationAttribute: Endpoint
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrPort")
    def attr_port(self) -> builtins.str:
        '''
        :cloudformationAttribute: Port
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrPort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrReadEndpoint")
    def attr_read_endpoint(self) -> builtins.str:
        '''
        :cloudformationAttribute: ReadEndpoint
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrReadEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''``AWS::DocDB::DBCluster.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> builtins.str:
        '''``AWS::DocDB::DBCluster.MasterUsername``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masterusername
        '''
        return typing.cast(builtins.str, jsii.get(self, "masterUsername"))

    @master_username.setter
    def master_username(self, value: builtins.str) -> None:
        jsii.set(self, "masterUsername", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUserPassword")
    def master_user_password(self) -> builtins.str:
        '''``AWS::DocDB::DBCluster.MasterUserPassword``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masteruserpassword
        '''
        return typing.cast(builtins.str, jsii.get(self, "masterUserPassword"))

    @master_user_password.setter
    def master_user_password(self, value: builtins.str) -> None:
        jsii.set(self, "masterUserPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::DocDB::DBCluster.AvailabilityZones``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-availabilityzones
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "availabilityZones"))

    @availability_zones.setter
    def availability_zones(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "availabilityZones", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::DocDB::DBCluster.BackupRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-backupretentionperiod
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupRetentionPeriod"))

    @backup_retention_period.setter
    def backup_retention_period(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "backupRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.DBClusterIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusteridentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbClusterIdentifier"))

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "dbClusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterParameterGroupName")
    def db_cluster_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusterparametergroupname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbClusterParameterGroupName"))

    @db_cluster_parameter_group_name.setter
    def db_cluster_parameter_group_name(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "dbClusterParameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.DBSubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbsubnetgroupname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbSubnetGroupName"))

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "dbSubnetGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deletionProtection")
    def deletion_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::DocDB::DBCluster.DeletionProtection``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-deletionprotection
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], jsii.get(self, "deletionProtection"))

    @deletion_protection.setter
    def deletion_protection(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "deletionProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableCloudwatchLogsExports")
    def enable_cloudwatch_logs_exports(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::DocDB::DBCluster.EnableCloudwatchLogsExports``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-enablecloudwatchlogsexports
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "enableCloudwatchLogsExports"))

    @enable_cloudwatch_logs_exports.setter
    def enable_cloudwatch_logs_exports(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "enableCloudwatchLogsExports", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.EngineVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-engineversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersion"))

    @engine_version.setter
    def engine_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "engineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-kmskeyid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        '''``AWS::DocDB::DBCluster.Port``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-port
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "port"))

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.PreferredBackupWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredbackupwindow
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredBackupWindow"))

    @preferred_backup_window.setter
    def preferred_backup_window(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "preferredBackupWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredmaintenancewindow
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredMaintenanceWindow"))

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "preferredMaintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.SnapshotIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-snapshotidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdentifier"))

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "snapshotIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::DocDB::DBCluster.StorageEncrypted``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-storageencrypted
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], jsii.get(self, "storageEncrypted"))

    @storage_encrypted.setter
    def storage_encrypted(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "storageEncrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-vpcsecuritygroupids
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIds"))

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "vpcSecurityGroupIds", value)


@jsii.implements(_IInspectable_82c04a63)
class CfnDBClusterParameterGroup(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_docdb.CfnDBClusterParameterGroup",
):
    '''A CloudFormation ``AWS::DocDB::DBClusterParameterGroup``.

    :cloudformationResource: AWS::DocDB::DBClusterParameterGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        description: builtins.str,
        family: builtins.str,
        parameters: typing.Any,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Create a new ``AWS::DocDB::DBClusterParameterGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param description: ``AWS::DocDB::DBClusterParameterGroup.Description``.
        :param family: ``AWS::DocDB::DBClusterParameterGroup.Family``.
        :param parameters: ``AWS::DocDB::DBClusterParameterGroup.Parameters``.
        :param name: ``AWS::DocDB::DBClusterParameterGroup.Name``.
        :param tags: ``AWS::DocDB::DBClusterParameterGroup.Tags``.
        '''
        props = CfnDBClusterParameterGroupProps(
            description=description,
            family=family,
            parameters=parameters,
            name=name,
            tags=tags,
        )

        jsii.create(CfnDBClusterParameterGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''``AWS::DocDB::DBClusterParameterGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''``AWS::DocDB::DBClusterParameterGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-description
        '''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        '''``AWS::DocDB::DBClusterParameterGroup.Family``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-family
        '''
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        jsii.set(self, "family", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        '''``AWS::DocDB::DBClusterParameterGroup.Parameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-parameters
        '''
        return typing.cast(typing.Any, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Any) -> None:
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBClusterParameterGroup.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.CfnDBClusterParameterGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "family": "family",
        "parameters": "parameters",
        "name": "name",
        "tags": "tags",
    },
)
class CfnDBClusterParameterGroupProps:
    def __init__(
        self,
        *,
        description: builtins.str,
        family: builtins.str,
        parameters: typing.Any,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::DocDB::DBClusterParameterGroup``.

        :param description: ``AWS::DocDB::DBClusterParameterGroup.Description``.
        :param family: ``AWS::DocDB::DBClusterParameterGroup.Family``.
        :param parameters: ``AWS::DocDB::DBClusterParameterGroup.Parameters``.
        :param name: ``AWS::DocDB::DBClusterParameterGroup.Name``.
        :param tags: ``AWS::DocDB::DBClusterParameterGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "family": family,
            "parameters": parameters,
        }
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> builtins.str:
        '''``AWS::DocDB::DBClusterParameterGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def family(self) -> builtins.str:
        '''``AWS::DocDB::DBClusterParameterGroup.Family``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-family
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(self) -> typing.Any:
        '''``AWS::DocDB::DBClusterParameterGroup.Parameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-parameters
        '''
        result = self._values.get("parameters")
        assert result is not None, "Required property 'parameters' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBClusterParameterGroup.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''``AWS::DocDB::DBClusterParameterGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDBClusterParameterGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.CfnDBClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "master_username": "masterUsername",
        "master_user_password": "masterUserPassword",
        "availability_zones": "availabilityZones",
        "backup_retention_period": "backupRetentionPeriod",
        "db_cluster_identifier": "dbClusterIdentifier",
        "db_cluster_parameter_group_name": "dbClusterParameterGroupName",
        "db_subnet_group_name": "dbSubnetGroupName",
        "deletion_protection": "deletionProtection",
        "enable_cloudwatch_logs_exports": "enableCloudwatchLogsExports",
        "engine_version": "engineVersion",
        "kms_key_id": "kmsKeyId",
        "port": "port",
        "preferred_backup_window": "preferredBackupWindow",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "snapshot_identifier": "snapshotIdentifier",
        "storage_encrypted": "storageEncrypted",
        "tags": "tags",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class CfnDBClusterProps:
    def __init__(
        self,
        *,
        master_username: builtins.str,
        master_user_password: builtins.str,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        backup_retention_period: typing.Optional[jsii.Number] = None,
        db_cluster_identifier: typing.Optional[builtins.str] = None,
        db_cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        enable_cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        engine_version: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::DocDB::DBCluster``.

        :param master_username: ``AWS::DocDB::DBCluster.MasterUsername``.
        :param master_user_password: ``AWS::DocDB::DBCluster.MasterUserPassword``.
        :param availability_zones: ``AWS::DocDB::DBCluster.AvailabilityZones``.
        :param backup_retention_period: ``AWS::DocDB::DBCluster.BackupRetentionPeriod``.
        :param db_cluster_identifier: ``AWS::DocDB::DBCluster.DBClusterIdentifier``.
        :param db_cluster_parameter_group_name: ``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.
        :param db_subnet_group_name: ``AWS::DocDB::DBCluster.DBSubnetGroupName``.
        :param deletion_protection: ``AWS::DocDB::DBCluster.DeletionProtection``.
        :param enable_cloudwatch_logs_exports: ``AWS::DocDB::DBCluster.EnableCloudwatchLogsExports``.
        :param engine_version: ``AWS::DocDB::DBCluster.EngineVersion``.
        :param kms_key_id: ``AWS::DocDB::DBCluster.KmsKeyId``.
        :param port: ``AWS::DocDB::DBCluster.Port``.
        :param preferred_backup_window: ``AWS::DocDB::DBCluster.PreferredBackupWindow``.
        :param preferred_maintenance_window: ``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.
        :param snapshot_identifier: ``AWS::DocDB::DBCluster.SnapshotIdentifier``.
        :param storage_encrypted: ``AWS::DocDB::DBCluster.StorageEncrypted``.
        :param tags: ``AWS::DocDB::DBCluster.Tags``.
        :param vpc_security_group_ids: ``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "master_username": master_username,
            "master_user_password": master_user_password,
        }
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if backup_retention_period is not None:
            self._values["backup_retention_period"] = backup_retention_period
        if db_cluster_identifier is not None:
            self._values["db_cluster_identifier"] = db_cluster_identifier
        if db_cluster_parameter_group_name is not None:
            self._values["db_cluster_parameter_group_name"] = db_cluster_parameter_group_name
        if db_subnet_group_name is not None:
            self._values["db_subnet_group_name"] = db_subnet_group_name
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if enable_cloudwatch_logs_exports is not None:
            self._values["enable_cloudwatch_logs_exports"] = enable_cloudwatch_logs_exports
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if port is not None:
            self._values["port"] = port
        if preferred_backup_window is not None:
            self._values["preferred_backup_window"] = preferred_backup_window
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if snapshot_identifier is not None:
            self._values["snapshot_identifier"] = snapshot_identifier
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if tags is not None:
            self._values["tags"] = tags
        if vpc_security_group_ids is not None:
            self._values["vpc_security_group_ids"] = vpc_security_group_ids

    @builtins.property
    def master_username(self) -> builtins.str:
        '''``AWS::DocDB::DBCluster.MasterUsername``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masterusername
        '''
        result = self._values.get("master_username")
        assert result is not None, "Required property 'master_username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def master_user_password(self) -> builtins.str:
        '''``AWS::DocDB::DBCluster.MasterUserPassword``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masteruserpassword
        '''
        result = self._values.get("master_user_password")
        assert result is not None, "Required property 'master_user_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::DocDB::DBCluster.AvailabilityZones``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-availabilityzones
        '''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::DocDB::DBCluster.BackupRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-backupretentionperiod
        '''
        result = self._values.get("backup_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.DBClusterIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusteridentifier
        '''
        result = self._values.get("db_cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_cluster_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusterparametergroupname
        '''
        result = self._values.get("db_cluster_parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.DBSubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbsubnetgroupname
        '''
        result = self._values.get("db_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deletion_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::DocDB::DBCluster.DeletionProtection``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-deletionprotection
        '''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

    @builtins.property
    def enable_cloudwatch_logs_exports(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::DocDB::DBCluster.EnableCloudwatchLogsExports``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-enablecloudwatchlogsexports
        '''
        result = self._values.get("enable_cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.EngineVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-engineversion
        '''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-kmskeyid
        '''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''``AWS::DocDB::DBCluster.Port``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-port
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_backup_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.PreferredBackupWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredbackupwindow
        '''
        result = self._values.get("preferred_backup_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredmaintenancewindow
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBCluster.SnapshotIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-snapshotidentifier
        '''
        result = self._values.get("snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::DocDB::DBCluster.StorageEncrypted``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-storageencrypted
        '''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''``AWS::DocDB::DBCluster.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-vpcsecuritygroupids
        '''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDBClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnDBInstance(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_docdb.CfnDBInstance",
):
    '''A CloudFormation ``AWS::DocDB::DBInstance``.

    :cloudformationResource: AWS::DocDB::DBInstance
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        db_cluster_identifier: builtins.str,
        db_instance_class: builtins.str,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        db_instance_identifier: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Create a new ``AWS::DocDB::DBInstance``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param db_cluster_identifier: ``AWS::DocDB::DBInstance.DBClusterIdentifier``.
        :param db_instance_class: ``AWS::DocDB::DBInstance.DBInstanceClass``.
        :param auto_minor_version_upgrade: ``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.
        :param availability_zone: ``AWS::DocDB::DBInstance.AvailabilityZone``.
        :param db_instance_identifier: ``AWS::DocDB::DBInstance.DBInstanceIdentifier``.
        :param preferred_maintenance_window: ``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.
        :param tags: ``AWS::DocDB::DBInstance.Tags``.
        '''
        props = CfnDBInstanceProps(
            db_cluster_identifier=db_cluster_identifier,
            db_instance_class=db_instance_class,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            availability_zone=availability_zone,
            db_instance_identifier=db_instance_identifier,
            preferred_maintenance_window=preferred_maintenance_window,
            tags=tags,
        )

        jsii.create(CfnDBInstance, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> builtins.str:
        '''
        :cloudformationAttribute: Endpoint
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrPort")
    def attr_port(self) -> builtins.str:
        '''
        :cloudformationAttribute: Port
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrPort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''``AWS::DocDB::DBInstance.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> builtins.str:
        '''``AWS::DocDB::DBInstance.DBClusterIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbclusteridentifier
        '''
        return typing.cast(builtins.str, jsii.get(self, "dbClusterIdentifier"))

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbClusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceClass")
    def db_instance_class(self) -> builtins.str:
        '''``AWS::DocDB::DBInstance.DBInstanceClass``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceclass
        '''
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceClass"))

    @db_instance_class.setter
    def db_instance_class(self, value: builtins.str) -> None:
        jsii.set(self, "dbInstanceClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-autominorversionupgrade
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], jsii.get(self, "autoMinorVersionUpgrade"))

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "autoMinorVersionUpgrade", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBInstance.AvailabilityZone``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-availabilityzone
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "availabilityZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBInstance.DBInstanceIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbInstanceIdentifier"))

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "dbInstanceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-preferredmaintenancewindow
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredMaintenanceWindow"))

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "preferredMaintenanceWindow", value)


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.CfnDBInstanceProps",
    jsii_struct_bases=[],
    name_mapping={
        "db_cluster_identifier": "dbClusterIdentifier",
        "db_instance_class": "dbInstanceClass",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "availability_zone": "availabilityZone",
        "db_instance_identifier": "dbInstanceIdentifier",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "tags": "tags",
    },
)
class CfnDBInstanceProps:
    def __init__(
        self,
        *,
        db_cluster_identifier: builtins.str,
        db_instance_class: builtins.str,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        db_instance_identifier: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::DocDB::DBInstance``.

        :param db_cluster_identifier: ``AWS::DocDB::DBInstance.DBClusterIdentifier``.
        :param db_instance_class: ``AWS::DocDB::DBInstance.DBInstanceClass``.
        :param auto_minor_version_upgrade: ``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.
        :param availability_zone: ``AWS::DocDB::DBInstance.AvailabilityZone``.
        :param db_instance_identifier: ``AWS::DocDB::DBInstance.DBInstanceIdentifier``.
        :param preferred_maintenance_window: ``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.
        :param tags: ``AWS::DocDB::DBInstance.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "db_cluster_identifier": db_cluster_identifier,
            "db_instance_class": db_instance_class,
        }
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if db_instance_identifier is not None:
            self._values["db_instance_identifier"] = db_instance_identifier
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def db_cluster_identifier(self) -> builtins.str:
        '''``AWS::DocDB::DBInstance.DBClusterIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbclusteridentifier
        '''
        result = self._values.get("db_cluster_identifier")
        assert result is not None, "Required property 'db_cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_instance_class(self) -> builtins.str:
        '''``AWS::DocDB::DBInstance.DBInstanceClass``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceclass
        '''
        result = self._values.get("db_instance_class")
        assert result is not None, "Required property 'db_instance_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-autominorversionupgrade
        '''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBInstance.AvailabilityZone``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-availabilityzone
        '''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_instance_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBInstance.DBInstanceIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceidentifier
        '''
        result = self._values.get("db_instance_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-preferredmaintenancewindow
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''``AWS::DocDB::DBInstance.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDBInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnDBSubnetGroup(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_docdb.CfnDBSubnetGroup",
):
    '''A CloudFormation ``AWS::DocDB::DBSubnetGroup``.

    :cloudformationResource: AWS::DocDB::DBSubnetGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        db_subnet_group_description: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Create a new ``AWS::DocDB::DBSubnetGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param db_subnet_group_description: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.
        :param subnet_ids: ``AWS::DocDB::DBSubnetGroup.SubnetIds``.
        :param db_subnet_group_name: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.
        :param tags: ``AWS::DocDB::DBSubnetGroup.Tags``.
        '''
        props = CfnDBSubnetGroupProps(
            db_subnet_group_description=db_subnet_group_description,
            subnet_ids=subnet_ids,
            db_subnet_group_name=db_subnet_group_name,
            tags=tags,
        )

        jsii.create(CfnDBSubnetGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''``AWS::DocDB::DBSubnetGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupDescription")
    def db_subnet_group_description(self) -> builtins.str:
        '''``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupdescription
        '''
        return typing.cast(builtins.str, jsii.get(self, "dbSubnetGroupDescription"))

    @db_subnet_group_description.setter
    def db_subnet_group_description(self, value: builtins.str) -> None:
        jsii.set(self, "dbSubnetGroupDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::DocDB::DBSubnetGroup.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-subnetids
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbSubnetGroupName"))

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "dbSubnetGroupName", value)


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.CfnDBSubnetGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "db_subnet_group_description": "dbSubnetGroupDescription",
        "subnet_ids": "subnetIds",
        "db_subnet_group_name": "dbSubnetGroupName",
        "tags": "tags",
    },
)
class CfnDBSubnetGroupProps:
    def __init__(
        self,
        *,
        db_subnet_group_description: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::DocDB::DBSubnetGroup``.

        :param db_subnet_group_description: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.
        :param subnet_ids: ``AWS::DocDB::DBSubnetGroup.SubnetIds``.
        :param db_subnet_group_name: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.
        :param tags: ``AWS::DocDB::DBSubnetGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "db_subnet_group_description": db_subnet_group_description,
            "subnet_ids": subnet_ids,
        }
        if db_subnet_group_name is not None:
            self._values["db_subnet_group_name"] = db_subnet_group_name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def db_subnet_group_description(self) -> builtins.str:
        '''``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupdescription
        '''
        result = self._values.get("db_subnet_group_description")
        assert result is not None, "Required property 'db_subnet_group_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::DocDB::DBSubnetGroup.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-subnetids
        '''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def db_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupname
        '''
        result = self._values.get("db_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''``AWS::DocDB::DBSubnetGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDBSubnetGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.ClusterParameterGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "family": "family",
        "parameters": "parameters",
        "db_cluster_parameter_group_name": "dbClusterParameterGroupName",
        "description": "description",
    },
)
class ClusterParameterGroupProps:
    def __init__(
        self,
        *,
        family: builtins.str,
        parameters: typing.Mapping[builtins.str, builtins.str],
        db_cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a cluster parameter group.

        :param family: (experimental) Database family of this parameter group.
        :param parameters: (experimental) The parameters in this parameter group.
        :param db_cluster_parameter_group_name: (experimental) The name of the cluster parameter group. Default: A CDK generated name for the cluster parameter group
        :param description: (experimental) Description for this parameter group. Default: a CDK generated description

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "family": family,
            "parameters": parameters,
        }
        if db_cluster_parameter_group_name is not None:
            self._values["db_cluster_parameter_group_name"] = db_cluster_parameter_group_name
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def family(self) -> builtins.str:
        '''(experimental) Database family of this parameter group.

        :stability: experimental
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) The parameters in this parameter group.

        :stability: experimental
        '''
        result = self._values.get("parameters")
        assert result is not None, "Required property 'parameters' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def db_cluster_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the cluster parameter group.

        :default: A CDK generated name for the cluster parameter group

        :stability: experimental
        '''
        result = self._values.get("db_cluster_parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description for this parameter group.

        :default: a CDK generated description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterParameterGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.DatabaseClusterAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_endpoint_address": "clusterEndpointAddress",
        "cluster_identifier": "clusterIdentifier",
        "instance_endpoint_addresses": "instanceEndpointAddresses",
        "instance_identifiers": "instanceIdentifiers",
        "port": "port",
        "reader_endpoint_address": "readerEndpointAddress",
        "security_group": "securityGroup",
    },
)
class DatabaseClusterAttributes:
    def __init__(
        self,
        *,
        cluster_endpoint_address: builtins.str,
        cluster_identifier: builtins.str,
        instance_endpoint_addresses: typing.Sequence[builtins.str],
        instance_identifiers: typing.Sequence[builtins.str],
        port: jsii.Number,
        reader_endpoint_address: builtins.str,
        security_group: _ISecurityGroup_cdbba9d3,
    ) -> None:
        '''(experimental) Properties that describe an existing cluster instance.

        :param cluster_endpoint_address: (experimental) Cluster endpoint address.
        :param cluster_identifier: (experimental) Identifier for the cluster.
        :param instance_endpoint_addresses: (experimental) Endpoint addresses of individual instances.
        :param instance_identifiers: (experimental) Identifier for the instances.
        :param port: (experimental) The database port.
        :param reader_endpoint_address: (experimental) Reader endpoint address.
        :param security_group: (experimental) The security group of the database cluster.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_endpoint_address": cluster_endpoint_address,
            "cluster_identifier": cluster_identifier,
            "instance_endpoint_addresses": instance_endpoint_addresses,
            "instance_identifiers": instance_identifiers,
            "port": port,
            "reader_endpoint_address": reader_endpoint_address,
            "security_group": security_group,
        }

    @builtins.property
    def cluster_endpoint_address(self) -> builtins.str:
        '''(experimental) Cluster endpoint address.

        :stability: experimental
        '''
        result = self._values.get("cluster_endpoint_address")
        assert result is not None, "Required property 'cluster_endpoint_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_identifier(self) -> builtins.str:
        '''(experimental) Identifier for the cluster.

        :stability: experimental
        '''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_endpoint_addresses(self) -> typing.List[builtins.str]:
        '''(experimental) Endpoint addresses of individual instances.

        :stability: experimental
        '''
        result = self._values.get("instance_endpoint_addresses")
        assert result is not None, "Required property 'instance_endpoint_addresses' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def instance_identifiers(self) -> typing.List[builtins.str]:
        '''(experimental) Identifier for the instances.

        :stability: experimental
        '''
        result = self._values.get("instance_identifiers")
        assert result is not None, "Required property 'instance_identifiers' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''(experimental) The database port.

        :stability: experimental
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def reader_endpoint_address(self) -> builtins.str:
        '''(experimental) Reader endpoint address.

        :stability: experimental
        '''
        result = self._values.get("reader_endpoint_address")
        assert result is not None, "Required property 'reader_endpoint_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(self) -> _ISecurityGroup_cdbba9d3:
        '''(experimental) The security group of the database cluster.

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
        return "DatabaseClusterAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.DatabaseClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "master_user": "masterUser",
        "vpc": "vpc",
        "backup": "backup",
        "db_cluster_name": "dbClusterName",
        "engine_version": "engineVersion",
        "instance_identifier_base": "instanceIdentifierBase",
        "instances": "instances",
        "kms_key": "kmsKey",
        "parameter_group": "parameterGroup",
        "port": "port",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "removal_policy": "removalPolicy",
        "security_group": "securityGroup",
        "storage_encrypted": "storageEncrypted",
        "vpc_subnets": "vpcSubnets",
    },
)
class DatabaseClusterProps:
    def __init__(
        self,
        *,
        instance_type: _InstanceType_072ad323,
        master_user: "Login",
        vpc: _IVpc_6d1f76c4,
        backup: typing.Optional[BackupProps] = None,
        db_cluster_name: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        instance_identifier_base: typing.Optional[builtins.str] = None,
        instances: typing.Optional[jsii.Number] = None,
        kms_key: typing.Optional[_IKey_36930160] = None,
        parameter_group: typing.Optional["IClusterParameterGroup"] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
        security_group: typing.Optional[_ISecurityGroup_cdbba9d3] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> None:
        '''(experimental) Properties for a new database cluster.

        :param instance_type: (experimental) What type of instance to start for the replicas.
        :param master_user: (experimental) Username and password for the administrative user.
        :param vpc: (experimental) What subnets to run the DocumentDB instances in. Must be at least 2 subnets in two different AZs.
        :param backup: (experimental) Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param db_cluster_name: (experimental) An optional identifier for the cluster. Default: - A name is automatically generated.
        :param engine_version: (experimental) What version of the database to start. Default: - The default engine version.
        :param instance_identifier_base: (experimental) Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - ``dbClusterName`` is used with the word "Instance" appended. If ``dbClusterName`` is not provided, the identifier is automatically generated.
        :param instances: (experimental) Number of DocDB compute instances. Default: 1
        :param kms_key: (experimental) The KMS key for storage encryption. Default: - default master key.
        :param parameter_group: (experimental) The DB parameter group to associate with the instance. Default: no parameter group
        :param port: (experimental) The port the DocumentDB cluster will listen on. Default: DatabaseCluster.DEFAULT_PORT
        :param preferred_maintenance_window: (experimental) A weekly time range in which maintenance should preferably execute. Must be at least 30 minutes long. Example: 'tue:04:17-tue:04:47' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param removal_policy: (experimental) The removal policy to apply when the cluster and its instances are removed or replaced during a stack update, or when the stack is deleted. This removal policy also applies to the implicit security group created for the cluster if one is not supplied as a parameter. Default: - Retain cluster.
        :param security_group: (experimental) Security group. Default: a new security group is created.
        :param storage_encrypted: (experimental) Whether to enable storage encryption. Default: true
        :param vpc_subnets: (experimental) Where to place the instances within the VPC. Default: private subnets

        :stability: experimental
        '''
        if isinstance(master_user, dict):
            master_user = Login(**master_user)
        if isinstance(backup, dict):
            backup = BackupProps(**backup)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _SubnetSelection_1284e62c(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "instance_type": instance_type,
            "master_user": master_user,
            "vpc": vpc,
        }
        if backup is not None:
            self._values["backup"] = backup
        if db_cluster_name is not None:
            self._values["db_cluster_name"] = db_cluster_name
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if instance_identifier_base is not None:
            self._values["instance_identifier_base"] = instance_identifier_base
        if instances is not None:
            self._values["instances"] = instances
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if parameter_group is not None:
            self._values["parameter_group"] = parameter_group
        if port is not None:
            self._values["port"] = port
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_group is not None:
            self._values["security_group"] = security_group
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def instance_type(self) -> _InstanceType_072ad323:
        '''(experimental) What type of instance to start for the replicas.

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_InstanceType_072ad323, result)

    @builtins.property
    def master_user(self) -> "Login":
        '''(experimental) Username and password for the administrative user.

        :stability: experimental
        '''
        result = self._values.get("master_user")
        assert result is not None, "Required property 'master_user' is missing"
        return typing.cast("Login", result)

    @builtins.property
    def vpc(self) -> _IVpc_6d1f76c4:
        '''(experimental) What subnets to run the DocumentDB instances in.

        Must be at least 2 subnets in two different AZs.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_IVpc_6d1f76c4, result)

    @builtins.property
    def backup(self) -> typing.Optional[BackupProps]:
        '''(experimental) Backup settings.

        :default:

        - Backup retention period for automated backups is 1 day.
        Backup preferred window is set to a 30-minute window selected at random from an
        8-hour block of time for each AWS Region, occurring on a random day of the week.

        :see: https://docs.aws.amazon.com/documentdb/latest/developerguide/backup-restore.db-cluster-snapshots.html#backup-restore.backup-window
        :stability: experimental
        '''
        result = self._values.get("backup")
        return typing.cast(typing.Optional[BackupProps], result)

    @builtins.property
    def db_cluster_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional identifier for the cluster.

        :default: - A name is automatically generated.

        :stability: experimental
        '''
        result = self._values.get("db_cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) What version of the database to start.

        :default: - The default engine version.

        :stability: experimental
        '''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_identifier_base(self) -> typing.Optional[builtins.str]:
        '''(experimental) Base identifier for instances.

        Every replica is named by appending the replica number to this string, 1-based.

        :default:

        - ``dbClusterName`` is used with the word "Instance" appended. If ``dbClusterName`` is not provided, the
        identifier is automatically generated.

        :stability: experimental
        '''
        result = self._values.get("instance_identifier_base")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instances(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of DocDB compute instances.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("instances")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The KMS key for storage encryption.

        :default: - default master key.

        :stability: experimental
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def parameter_group(self) -> typing.Optional["IClusterParameterGroup"]:
        '''(experimental) The DB parameter group to associate with the instance.

        :default: no parameter group

        :stability: experimental
        '''
        result = self._values.get("parameter_group")
        return typing.cast(typing.Optional["IClusterParameterGroup"], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port the DocumentDB cluster will listen on.

        :default: DatabaseCluster.DEFAULT_PORT

        :stability: experimental
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''(experimental) A weekly time range in which maintenance should preferably execute.

        Must be at least 30 minutes long.

        Example: 'tue:04:17-tue:04:47'

        :default:

        - 30-minute window selected at random from an 8-hour block of time for
        each AWS Region, occurring on a random day of the week.

        :see: https://docs.aws.amazon.com/documentdb/latest/developerguide/db-instance-maintain.html#maintenance-window
        :stability: experimental
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_RemovalPolicy_c97e7a20]:
        '''(experimental) The removal policy to apply when the cluster and its instances are removed or replaced during a stack update, or when the stack is deleted.

        This
        removal policy also applies to the implicit security group created for the
        cluster if one is not supplied as a parameter.

        :default: - Retain cluster.

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_RemovalPolicy_c97e7a20], result)

    @builtins.property
    def security_group(self) -> typing.Optional[_ISecurityGroup_cdbba9d3]:
        '''(experimental) Security group.

        :default: a new security group is created.

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_ISecurityGroup_cdbba9d3], result)

    @builtins.property
    def storage_encrypted(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable storage encryption.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_SubnetSelection_1284e62c]:
        '''(experimental) Where to place the instances within the VPC.

        :default: private subnets

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_SubnetSelection_1284e62c], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.DatabaseInstanceAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "instance_endpoint_address": "instanceEndpointAddress",
        "instance_identifier": "instanceIdentifier",
        "port": "port",
    },
)
class DatabaseInstanceAttributes:
    def __init__(
        self,
        *,
        instance_endpoint_address: builtins.str,
        instance_identifier: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''(experimental) Properties that describe an existing instance.

        :param instance_endpoint_address: (experimental) The endpoint address.
        :param instance_identifier: (experimental) The instance identifier.
        :param port: (experimental) The database port.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_endpoint_address": instance_endpoint_address,
            "instance_identifier": instance_identifier,
            "port": port,
        }

    @builtins.property
    def instance_endpoint_address(self) -> builtins.str:
        '''(experimental) The endpoint address.

        :stability: experimental
        '''
        result = self._values.get("instance_endpoint_address")
        assert result is not None, "Required property 'instance_endpoint_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_identifier(self) -> builtins.str:
        '''(experimental) The instance identifier.

        :stability: experimental
        '''
        result = self._values.get("instance_identifier")
        assert result is not None, "Required property 'instance_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''(experimental) The database port.

        :stability: experimental
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseInstanceAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.DatabaseInstanceProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "instance_type": "instanceType",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "availability_zone": "availabilityZone",
        "db_instance_name": "dbInstanceName",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "removal_policy": "removalPolicy",
    },
)
class DatabaseInstanceProps:
    def __init__(
        self,
        *,
        cluster: "IDatabaseCluster",
        instance_type: _InstanceType_072ad323,
        auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        db_instance_name: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
    ) -> None:
        '''(experimental) Construction properties for a DatabaseInstanceNew.

        :param cluster: (experimental) The DocumentDB database cluster the instance should launch into.
        :param instance_type: (experimental) The name of the compute and memory capacity classes.
        :param auto_minor_version_upgrade: (experimental) Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. Default: true
        :param availability_zone: (experimental) The name of the Availability Zone where the DB instance will be located. Default: - no preference
        :param db_instance_name: (experimental) A name for the DB instance. If you specify a name, AWS CloudFormation converts it to lowercase. Default: - a CloudFormation generated name
        :param preferred_maintenance_window: (experimental) The weekly time range (in UTC) during which system maintenance can occur. Format: ``ddd:hh24:mi-ddd:hh24:mi`` Constraint: Minimum 30-minute window Default: - a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/documentdb/latest/developerguide/db-instance-maintain.html#maintenance-window
        :param removal_policy: (experimental) The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. Default: RemovalPolicy.Retain

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "instance_type": instance_type,
        }
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if db_instance_name is not None:
            self._values["db_instance_name"] = db_instance_name
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def cluster(self) -> "IDatabaseCluster":
        '''(experimental) The DocumentDB database cluster the instance should launch into.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast("IDatabaseCluster", result)

    @builtins.property
    def instance_type(self) -> _InstanceType_072ad323:
        '''(experimental) The name of the compute and memory capacity classes.

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_InstanceType_072ad323, result)

    @builtins.property
    def auto_minor_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Availability Zone where the DB instance will be located.

        :default: - no preference

        :stability: experimental
        '''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_instance_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the DB instance.

        If you specify a name, AWS CloudFormation
        converts it to lowercase.

        :default: - a CloudFormation generated name

        :stability: experimental
        '''
        result = self._values.get("db_instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''(experimental) The weekly time range (in UTC) during which system maintenance can occur.

        Format: ``ddd:hh24:mi-ddd:hh24:mi``
        Constraint: Minimum 30-minute window

        :default:

        - a 30-minute window selected at random from an 8-hour block of
        time for each AWS Region, occurring on a random day of the week. To see
        the time blocks available, see https://docs.aws.amazon.com/documentdb/latest/developerguide/db-instance-maintain.html#maintenance-window

        :stability: experimental
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_RemovalPolicy_c97e7a20]:
        '''(experimental) The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update.

        :default: RemovalPolicy.Retain

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_RemovalPolicy_c97e7a20], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecret(
    _Secret_cb33d4cc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_docdb.DatabaseSecret",
):
    '''(experimental) A database secret.

    :stability: experimental
    :resource: AWS::SecretsManager::Secret
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        username: builtins.str,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        master_secret: typing.Optional[_ISecret_22fb8757] = None,
        secret_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param username: (experimental) The username.
        :param encryption_key: (experimental) The KMS key to use to encrypt the secret. Default: default master key
        :param master_secret: (experimental) The master secret which will be used to rotate this secret. Default: - no master secret information will be included
        :param secret_name: (experimental) The physical name of the secret. Default: Secretsmanager will generate a physical name for the secret

        :stability: experimental
        '''
        props = DatabaseSecretProps(
            username=username,
            encryption_key=encryption_key,
            master_secret=master_secret,
            secret_name=secret_name,
        )

        jsii.create(DatabaseSecret, self, [scope, id, props])


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.DatabaseSecretProps",
    jsii_struct_bases=[],
    name_mapping={
        "username": "username",
        "encryption_key": "encryptionKey",
        "master_secret": "masterSecret",
        "secret_name": "secretName",
    },
)
class DatabaseSecretProps:
    def __init__(
        self,
        *,
        username: builtins.str,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        master_secret: typing.Optional[_ISecret_22fb8757] = None,
        secret_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Construction properties for a DatabaseSecret.

        :param username: (experimental) The username.
        :param encryption_key: (experimental) The KMS key to use to encrypt the secret. Default: default master key
        :param master_secret: (experimental) The master secret which will be used to rotate this secret. Default: - no master secret information will be included
        :param secret_name: (experimental) The physical name of the secret. Default: Secretsmanager will generate a physical name for the secret

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "username": username,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if master_secret is not None:
            self._values["master_secret"] = master_secret
        if secret_name is not None:
            self._values["secret_name"] = secret_name

    @builtins.property
    def username(self) -> builtins.str:
        '''(experimental) The username.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The KMS key to use to encrypt the secret.

        :default: default master key

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def master_secret(self) -> typing.Optional[_ISecret_22fb8757]:
        '''(experimental) The master secret which will be used to rotate this secret.

        :default: - no master secret information will be included

        :stability: experimental
        '''
        result = self._values.get("master_secret")
        return typing.cast(typing.Optional[_ISecret_22fb8757], result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The physical name of the secret.

        :default: Secretsmanager will generate a physical name for the secret

        :stability: experimental
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Endpoint(metaclass=jsii.JSIIMeta, jsii_type="monocdk.aws_docdb.Endpoint"):
    '''(experimental) Connection endpoint of a database cluster or instance.

    Consists of a combination of hostname and port.

    :stability: experimental
    '''

    def __init__(self, address: builtins.str, port: jsii.Number) -> None:
        '''(experimental) Constructs an Endpoint instance.

        :param address: - The hostname or address of the endpoint.
        :param port: - The port number of the endpoint.

        :stability: experimental
        '''
        jsii.create(Endpoint, self, [address, port])

    @jsii.member(jsii_name="portAsString")
    def port_as_string(self) -> builtins.str:
        '''(experimental) Returns the port number as a string representation that can be used for embedding within other strings.

        This is intended to deal with CDK's token system. Numeric CDK tokens are not expanded when their string
        representation is embedded in a string. This function returns the port either as an unresolved string token or
        as a resolved string representation of the port value.

        :return: An (un)resolved string representation of the endpoint's port number

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "portAsString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        '''(experimental) The hostname of the endpoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        '''(experimental) The port number of the endpoint.

        This can potentially be a CDK token. If you need to embed the port in a string (e.g. instance user data script),
        use {@link Endpoint.portAsString}.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="socketAddress")
    def socket_address(self) -> builtins.str:
        '''(experimental) The combination of ``HOSTNAME:PORT`` for this endpoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "socketAddress"))


@jsii.interface(jsii_type="monocdk.aws_docdb.IClusterParameterGroup")
class IClusterParameterGroup(_IResource_8c1dbbbd, typing_extensions.Protocol):
    '''(experimental) A parameter group.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        '''(experimental) The name of this parameter group.

        :stability: experimental
        '''
        ...


class _IClusterParameterGroupProxy(
    jsii.proxy_for(_IResource_8c1dbbbd) # type: ignore[misc]
):
    '''(experimental) A parameter group.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_docdb.IClusterParameterGroup"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        '''(experimental) The name of this parameter group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IClusterParameterGroup).__jsii_proxy_class__ = lambda : _IClusterParameterGroupProxy


@jsii.interface(jsii_type="monocdk.aws_docdb.IDatabaseCluster")
class IDatabaseCluster(
    _IResource_8c1dbbbd,
    _IConnectable_c1c0e72c,
    _ISecretAttachmentTarget_b6932462,
    typing_extensions.Protocol,
):
    '''(experimental) Create a clustered database with a given number of instances.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> Endpoint:
        '''(experimental) The endpoint to use for read/write operations.

        :stability: experimental
        :attribute: Endpoint,Port
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        '''(experimental) Identifier of the cluster.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterReadEndpoint")
    def cluster_read_endpoint(self) -> Endpoint:
        '''(experimental) Endpoint to use for load-balanced read-only operations.

        :stability: experimental
        :attribute: ReadEndpoint
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceEndpoints")
    def instance_endpoints(self) -> typing.List[Endpoint]:
        '''(experimental) Endpoints which address each individual replica.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdentifiers")
    def instance_identifiers(self) -> typing.List[builtins.str]:
        '''(experimental) Identifiers of the replicas.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> builtins.str:
        '''(experimental) The security group for this database cluster.

        :stability: experimental
        '''
        ...


class _IDatabaseClusterProxy(
    jsii.proxy_for(_IResource_8c1dbbbd), # type: ignore[misc]
    jsii.proxy_for(_IConnectable_c1c0e72c), # type: ignore[misc]
    jsii.proxy_for(_ISecretAttachmentTarget_b6932462), # type: ignore[misc]
):
    '''(experimental) Create a clustered database with a given number of instances.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_docdb.IDatabaseCluster"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> Endpoint:
        '''(experimental) The endpoint to use for read/write operations.

        :stability: experimental
        :attribute: Endpoint,Port
        '''
        return typing.cast(Endpoint, jsii.get(self, "clusterEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        '''(experimental) Identifier of the cluster.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterReadEndpoint")
    def cluster_read_endpoint(self) -> Endpoint:
        '''(experimental) Endpoint to use for load-balanced read-only operations.

        :stability: experimental
        :attribute: ReadEndpoint
        '''
        return typing.cast(Endpoint, jsii.get(self, "clusterReadEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceEndpoints")
    def instance_endpoints(self) -> typing.List[Endpoint]:
        '''(experimental) Endpoints which address each individual replica.

        :stability: experimental
        '''
        return typing.cast(typing.List[Endpoint], jsii.get(self, "instanceEndpoints"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdentifiers")
    def instance_identifiers(self) -> typing.List[builtins.str]:
        '''(experimental) Identifiers of the replicas.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceIdentifiers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> builtins.str:
        '''(experimental) The security group for this database cluster.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "securityGroupId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDatabaseCluster).__jsii_proxy_class__ = lambda : _IDatabaseClusterProxy


@jsii.interface(jsii_type="monocdk.aws_docdb.IDatabaseInstance")
class IDatabaseInstance(_IResource_8c1dbbbd, typing_extensions.Protocol):
    '''(experimental) A database instance.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> builtins.str:
        '''(experimental) The instance endpoint address.

        :stability: experimental
        :attribute: Endpoint
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> builtins.str:
        '''(experimental) The instance endpoint port.

        :stability: experimental
        :attribute: Port
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''(experimental) The instance arn.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceEndpoint")
    def instance_endpoint(self) -> Endpoint:
        '''(experimental) The instance endpoint.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdentifier")
    def instance_identifier(self) -> builtins.str:
        '''(experimental) The instance identifier.

        :stability: experimental
        '''
        ...


class _IDatabaseInstanceProxy(
    jsii.proxy_for(_IResource_8c1dbbbd) # type: ignore[misc]
):
    '''(experimental) A database instance.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_docdb.IDatabaseInstance"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> builtins.str:
        '''(experimental) The instance endpoint address.

        :stability: experimental
        :attribute: Endpoint
        '''
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> builtins.str:
        '''(experimental) The instance endpoint port.

        :stability: experimental
        :attribute: Port
        '''
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceEndpointPort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''(experimental) The instance arn.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceEndpoint")
    def instance_endpoint(self) -> Endpoint:
        '''(experimental) The instance endpoint.

        :stability: experimental
        '''
        return typing.cast(Endpoint, jsii.get(self, "instanceEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdentifier")
    def instance_identifier(self) -> builtins.str:
        '''(experimental) The instance identifier.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceIdentifier"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDatabaseInstance).__jsii_proxy_class__ = lambda : _IDatabaseInstanceProxy


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.Login",
    jsii_struct_bases=[],
    name_mapping={"username": "username", "kms_key": "kmsKey", "password": "password"},
)
class Login:
    def __init__(
        self,
        *,
        username: builtins.str,
        kms_key: typing.Optional[_IKey_36930160] = None,
        password: typing.Optional[_SecretValue_c18506ef] = None,
    ) -> None:
        '''(experimental) Login credentials for a database cluster.

        :param username: (experimental) Username.
        :param kms_key: (experimental) KMS encryption key to encrypt the generated secret. Default: default master key
        :param password: (experimental) Password. Do not put passwords in your CDK code directly. Default: a Secrets Manager generated password

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "username": username,
        }
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if password is not None:
            self._values["password"] = password

    @builtins.property
    def username(self) -> builtins.str:
        '''(experimental) Username.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) KMS encryption key to encrypt the generated secret.

        :default: default master key

        :stability: experimental
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def password(self) -> typing.Optional[_SecretValue_c18506ef]:
        '''(experimental) Password.

        Do not put passwords in your CDK code directly.

        :default: a Secrets Manager generated password

        :stability: experimental
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[_SecretValue_c18506ef], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Login(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_docdb.RotationMultiUserOptions",
    jsii_struct_bases=[],
    name_mapping={"secret": "secret", "automatically_after": "automaticallyAfter"},
)
class RotationMultiUserOptions:
    def __init__(
        self,
        *,
        secret: _ISecret_22fb8757,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
    ) -> None:
        '''(experimental) Options to add the multi user rotation.

        :param secret: (experimental) The secret to rotate. It must be a JSON string with the following format:: { "engine": <required: must be set to 'mongo'>, "host": <required: instance host name>, "username": <required: username>, "password": <required: password>, "dbname": <optional: database name>, "port": <optional: if not specified, default port 27017 will be used>, "masterarn": <required: the arn of the master secret which will be used to create users/change passwords> "ssl": <optional: if not specified, defaults to false. This must be true if being used for DocumentDB rotations where the cluster has TLS enabled> }
        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "secret": secret,
        }
        if automatically_after is not None:
            self._values["automatically_after"] = automatically_after

    @builtins.property
    def secret(self) -> _ISecret_22fb8757:
        '''(experimental) The secret to rotate.

        It must be a JSON string with the following format::

           {
              "engine": <required: must be set to 'mongo'>,
              "host": <required: instance host name>,
              "username": <required: username>,
              "password": <required: password>,
              "dbname": <optional: database name>,
              "port": <optional: if not specified, default port 27017 will be used>,
              "masterarn": <required: the arn of the master secret which will be used to create users/change passwords>
              "ssl": <optional: if not specified, defaults to false. This must be true if being used for DocumentDB rotations
                     where the cluster has TLS enabled>
           }

        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(_ISecret_22fb8757, result)

    @builtins.property
    def automatically_after(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation.

        :default: Duration.days(30)

        :stability: experimental
        '''
        result = self._values.get("automatically_after")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RotationMultiUserOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IClusterParameterGroup)
class ClusterParameterGroup(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_docdb.ClusterParameterGroup",
):
    '''(experimental) A cluster parameter group.

    :stability: experimental
    :resource: AWS::DocDB::DBClusterParameterGroup
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        family: builtins.str,
        parameters: typing.Mapping[builtins.str, builtins.str],
        db_cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param family: (experimental) Database family of this parameter group.
        :param parameters: (experimental) The parameters in this parameter group.
        :param db_cluster_parameter_group_name: (experimental) The name of the cluster parameter group. Default: A CDK generated name for the cluster parameter group
        :param description: (experimental) Description for this parameter group. Default: a CDK generated description

        :stability: experimental
        '''
        props = ClusterParameterGroupProps(
            family=family,
            parameters=parameters,
            db_cluster_parameter_group_name=db_cluster_parameter_group_name,
            description=description,
        )

        jsii.create(ClusterParameterGroup, self, [scope, id, props])

    @jsii.member(jsii_name="fromParameterGroupName") # type: ignore[misc]
    @builtins.classmethod
    def from_parameter_group_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        parameter_group_name: builtins.str,
    ) -> IClusterParameterGroup:
        '''(experimental) Imports a parameter group.

        :param scope: -
        :param id: -
        :param parameter_group_name: -

        :stability: experimental
        '''
        return typing.cast(IClusterParameterGroup, jsii.sinvoke(cls, "fromParameterGroupName", [scope, id, parameter_group_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        '''(experimental) The name of the parameter group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupName"))


@jsii.implements(IDatabaseCluster)
class DatabaseCluster(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_docdb.DatabaseCluster",
):
    '''(experimental) Create a clustered database with a given number of instances.

    :stability: experimental
    :resource: AWS::DocDB::DBCluster
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        instance_type: _InstanceType_072ad323,
        master_user: Login,
        vpc: _IVpc_6d1f76c4,
        backup: typing.Optional[BackupProps] = None,
        db_cluster_name: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        instance_identifier_base: typing.Optional[builtins.str] = None,
        instances: typing.Optional[jsii.Number] = None,
        kms_key: typing.Optional[_IKey_36930160] = None,
        parameter_group: typing.Optional[IClusterParameterGroup] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
        security_group: typing.Optional[_ISecurityGroup_cdbba9d3] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_type: (experimental) What type of instance to start for the replicas.
        :param master_user: (experimental) Username and password for the administrative user.
        :param vpc: (experimental) What subnets to run the DocumentDB instances in. Must be at least 2 subnets in two different AZs.
        :param backup: (experimental) Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param db_cluster_name: (experimental) An optional identifier for the cluster. Default: - A name is automatically generated.
        :param engine_version: (experimental) What version of the database to start. Default: - The default engine version.
        :param instance_identifier_base: (experimental) Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - ``dbClusterName`` is used with the word "Instance" appended. If ``dbClusterName`` is not provided, the identifier is automatically generated.
        :param instances: (experimental) Number of DocDB compute instances. Default: 1
        :param kms_key: (experimental) The KMS key for storage encryption. Default: - default master key.
        :param parameter_group: (experimental) The DB parameter group to associate with the instance. Default: no parameter group
        :param port: (experimental) The port the DocumentDB cluster will listen on. Default: DatabaseCluster.DEFAULT_PORT
        :param preferred_maintenance_window: (experimental) A weekly time range in which maintenance should preferably execute. Must be at least 30 minutes long. Example: 'tue:04:17-tue:04:47' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param removal_policy: (experimental) The removal policy to apply when the cluster and its instances are removed or replaced during a stack update, or when the stack is deleted. This removal policy also applies to the implicit security group created for the cluster if one is not supplied as a parameter. Default: - Retain cluster.
        :param security_group: (experimental) Security group. Default: a new security group is created.
        :param storage_encrypted: (experimental) Whether to enable storage encryption. Default: true
        :param vpc_subnets: (experimental) Where to place the instances within the VPC. Default: private subnets

        :stability: experimental
        '''
        props = DatabaseClusterProps(
            instance_type=instance_type,
            master_user=master_user,
            vpc=vpc,
            backup=backup,
            db_cluster_name=db_cluster_name,
            engine_version=engine_version,
            instance_identifier_base=instance_identifier_base,
            instances=instances,
            kms_key=kms_key,
            parameter_group=parameter_group,
            port=port,
            preferred_maintenance_window=preferred_maintenance_window,
            removal_policy=removal_policy,
            security_group=security_group,
            storage_encrypted=storage_encrypted,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(DatabaseCluster, self, [scope, id, props])

    @jsii.member(jsii_name="fromDatabaseClusterAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_database_cluster_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_endpoint_address: builtins.str,
        cluster_identifier: builtins.str,
        instance_endpoint_addresses: typing.Sequence[builtins.str],
        instance_identifiers: typing.Sequence[builtins.str],
        port: jsii.Number,
        reader_endpoint_address: builtins.str,
        security_group: _ISecurityGroup_cdbba9d3,
    ) -> IDatabaseCluster:
        '''(experimental) Import an existing DatabaseCluster from properties.

        :param scope: -
        :param id: -
        :param cluster_endpoint_address: (experimental) Cluster endpoint address.
        :param cluster_identifier: (experimental) Identifier for the cluster.
        :param instance_endpoint_addresses: (experimental) Endpoint addresses of individual instances.
        :param instance_identifiers: (experimental) Identifier for the instances.
        :param port: (experimental) The database port.
        :param reader_endpoint_address: (experimental) Reader endpoint address.
        :param security_group: (experimental) The security group of the database cluster.

        :stability: experimental
        '''
        attrs = DatabaseClusterAttributes(
            cluster_endpoint_address=cluster_endpoint_address,
            cluster_identifier=cluster_identifier,
            instance_endpoint_addresses=instance_endpoint_addresses,
            instance_identifiers=instance_identifiers,
            port=port,
            reader_endpoint_address=reader_endpoint_address,
            security_group=security_group,
        )

        return typing.cast(IDatabaseCluster, jsii.sinvoke(cls, "fromDatabaseClusterAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addRotationMultiUser")
    def add_rotation_multi_user(
        self,
        id: builtins.str,
        *,
        secret: _ISecret_22fb8757,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
    ) -> _SecretRotation_e64158ad:
        '''(experimental) Adds the multi user rotation to this cluster.

        :param id: -
        :param secret: (experimental) The secret to rotate. It must be a JSON string with the following format:: { "engine": <required: must be set to 'mongo'>, "host": <required: instance host name>, "username": <required: username>, "password": <required: password>, "dbname": <optional: database name>, "port": <optional: if not specified, default port 27017 will be used>, "masterarn": <required: the arn of the master secret which will be used to create users/change passwords> "ssl": <optional: if not specified, defaults to false. This must be true if being used for DocumentDB rotations where the cluster has TLS enabled> }
        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        :stability: experimental
        '''
        options = RotationMultiUserOptions(
            secret=secret, automatically_after=automatically_after
        )

        return typing.cast(_SecretRotation_e64158ad, jsii.invoke(self, "addRotationMultiUser", [id, options]))

    @jsii.member(jsii_name="addRotationSingleUser")
    def add_rotation_single_user(
        self,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
    ) -> _SecretRotation_e64158ad:
        '''(experimental) Adds the single user rotation of the master password to this cluster.

        :param automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation.

        :stability: experimental
        '''
        return typing.cast(_SecretRotation_e64158ad, jsii.invoke(self, "addRotationSingleUser", [automatically_after]))

    @jsii.member(jsii_name="addSecurityGroups")
    def add_security_groups(self, *security_groups: _ISecurityGroup_cdbba9d3) -> None:
        '''(experimental) Adds security groups to this cluster.

        :param security_groups: The security groups to add.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addSecurityGroups", [*security_groups]))

    @jsii.member(jsii_name="asSecretAttachmentTarget")
    def as_secret_attachment_target(self) -> _SecretAttachmentTargetProps_ab8522eb:
        '''(experimental) Renders the secret attachment target specifications.

        :stability: experimental
        '''
        return typing.cast(_SecretAttachmentTargetProps_ab8522eb, jsii.invoke(self, "asSecretAttachmentTarget", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DEFAULT_NUM_INSTANCES")
    def DEFAULT_NUM_INSTANCES(cls) -> jsii.Number:
        '''(experimental) The default number of instances in the DocDB cluster if none are specified.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.sget(cls, "DEFAULT_NUM_INSTANCES"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DEFAULT_PORT")
    def DEFAULT_PORT(cls) -> jsii.Number:
        '''(experimental) The default port Document DB listens on.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.sget(cls, "DEFAULT_PORT"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> Endpoint:
        '''(experimental) The endpoint to use for read/write operations.

        :stability: experimental
        '''
        return typing.cast(Endpoint, jsii.get(self, "clusterEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        '''(experimental) Identifier of the cluster.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterReadEndpoint")
    def cluster_read_endpoint(self) -> Endpoint:
        '''(experimental) Endpoint to use for load-balanced read-only operations.

        :stability: experimental
        '''
        return typing.cast(Endpoint, jsii.get(self, "clusterReadEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterResourceIdentifier")
    def cluster_resource_identifier(self) -> builtins.str:
        '''(experimental) The resource id for the cluster;

        for example: cluster-ABCD1234EFGH5678IJKL90MNOP. The cluster ID uniquely
        identifies the cluster and is used in things like IAM authentication policies.

        :stability: experimental
        :attribute: ClusterResourceId
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterResourceIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> _Connections_57ccbda9:
        '''(experimental) The connections object to implement IConnectable.

        :stability: experimental
        '''
        return typing.cast(_Connections_57ccbda9, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceEndpoints")
    def instance_endpoints(self) -> typing.List[Endpoint]:
        '''(experimental) Endpoints which address each individual replica.

        :stability: experimental
        '''
        return typing.cast(typing.List[Endpoint], jsii.get(self, "instanceEndpoints"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdentifiers")
    def instance_identifiers(self) -> typing.List[builtins.str]:
        '''(experimental) Identifiers of the replicas.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceIdentifiers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> builtins.str:
        '''(experimental) Security group identifier of this database.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "securityGroupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> typing.Optional[_ISecret_22fb8757]:
        '''(experimental) The secret attached to this cluster.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_ISecret_22fb8757], jsii.get(self, "secret"))


@jsii.implements(IDatabaseInstance)
class DatabaseInstance(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_docdb.DatabaseInstance",
):
    '''(experimental) A database instance.

    :stability: experimental
    :resource: AWS::DocDB::DBInstance
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster: IDatabaseCluster,
        instance_type: _InstanceType_072ad323,
        auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        db_instance_name: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) The DocumentDB database cluster the instance should launch into.
        :param instance_type: (experimental) The name of the compute and memory capacity classes.
        :param auto_minor_version_upgrade: (experimental) Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. Default: true
        :param availability_zone: (experimental) The name of the Availability Zone where the DB instance will be located. Default: - no preference
        :param db_instance_name: (experimental) A name for the DB instance. If you specify a name, AWS CloudFormation converts it to lowercase. Default: - a CloudFormation generated name
        :param preferred_maintenance_window: (experimental) The weekly time range (in UTC) during which system maintenance can occur. Format: ``ddd:hh24:mi-ddd:hh24:mi`` Constraint: Minimum 30-minute window Default: - a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/documentdb/latest/developerguide/db-instance-maintain.html#maintenance-window
        :param removal_policy: (experimental) The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. Default: RemovalPolicy.Retain

        :stability: experimental
        '''
        props = DatabaseInstanceProps(
            cluster=cluster,
            instance_type=instance_type,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            availability_zone=availability_zone,
            db_instance_name=db_instance_name,
            preferred_maintenance_window=preferred_maintenance_window,
            removal_policy=removal_policy,
        )

        jsii.create(DatabaseInstance, self, [scope, id, props])

    @jsii.member(jsii_name="fromDatabaseInstanceAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_database_instance_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        instance_endpoint_address: builtins.str,
        instance_identifier: builtins.str,
        port: jsii.Number,
    ) -> IDatabaseInstance:
        '''(experimental) Import an existing database instance.

        :param scope: -
        :param id: -
        :param instance_endpoint_address: (experimental) The endpoint address.
        :param instance_identifier: (experimental) The instance identifier.
        :param port: (experimental) The database port.

        :stability: experimental
        '''
        attrs = DatabaseInstanceAttributes(
            instance_endpoint_address=instance_endpoint_address,
            instance_identifier=instance_identifier,
            port=port,
        )

        return typing.cast(IDatabaseInstance, jsii.sinvoke(cls, "fromDatabaseInstanceAttributes", [scope, id, attrs]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> IDatabaseCluster:
        '''(experimental) The instance's database cluster.

        :stability: experimental
        '''
        return typing.cast(IDatabaseCluster, jsii.get(self, "cluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> builtins.str:
        '''(experimental) The instance endpoint address.

        :stability: experimental
        :inheritdoc: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> builtins.str:
        '''(experimental) The instance endpoint port.

        :stability: experimental
        :inheritdoc: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceEndpointPort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''(experimental) The instance arn.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceEndpoint")
    def instance_endpoint(self) -> Endpoint:
        '''(experimental) The instance endpoint.

        :stability: experimental
        :inheritdoc: true
        '''
        return typing.cast(Endpoint, jsii.get(self, "instanceEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdentifier")
    def instance_identifier(self) -> builtins.str:
        '''(experimental) The instance identifier.

        :stability: experimental
        :inheritdoc: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceIdentifier"))


__all__ = [
    "BackupProps",
    "CfnDBCluster",
    "CfnDBClusterParameterGroup",
    "CfnDBClusterParameterGroupProps",
    "CfnDBClusterProps",
    "CfnDBInstance",
    "CfnDBInstanceProps",
    "CfnDBSubnetGroup",
    "CfnDBSubnetGroupProps",
    "ClusterParameterGroup",
    "ClusterParameterGroupProps",
    "DatabaseCluster",
    "DatabaseClusterAttributes",
    "DatabaseClusterProps",
    "DatabaseInstance",
    "DatabaseInstanceAttributes",
    "DatabaseInstanceProps",
    "DatabaseSecret",
    "DatabaseSecretProps",
    "Endpoint",
    "IClusterParameterGroup",
    "IDatabaseCluster",
    "IDatabaseInstance",
    "Login",
    "RotationMultiUserOptions",
]

publication.publish()
