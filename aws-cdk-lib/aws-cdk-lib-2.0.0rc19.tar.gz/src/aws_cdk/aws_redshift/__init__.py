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
    CfnResource as _CfnResource_9df397a6,
    CfnTag as _CfnTag_f6864754,
    IInspectable as _IInspectable_c2943556,
    IResolvable as _IResolvable_da3f097b,
    TagManager as _TagManager_0a598cb3,
    TreeInspector as _TreeInspector_488e0dd5,
)


@jsii.implements(_IInspectable_c2943556)
class CfnCluster(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_redshift.CfnCluster",
):
    '''A CloudFormation ``AWS::Redshift::Cluster``.

    :cloudformationResource: AWS::Redshift::Cluster
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_type: builtins.str,
        db_name: builtins.str,
        master_username: builtins.str,
        master_user_password: builtins.str,
        node_type: builtins.str,
        allow_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        aqua_configuration_status: typing.Optional[builtins.str] = None,
        automated_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        availability_zone_relocation: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        availability_zone_relocation_status: typing.Optional[builtins.str] = None,
        classic: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        cluster_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        cluster_subnet_group_name: typing.Optional[builtins.str] = None,
        cluster_version: typing.Optional[builtins.str] = None,
        defer_maintenance: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        defer_maintenance_duration: typing.Optional[jsii.Number] = None,
        defer_maintenance_end_time: typing.Optional[builtins.str] = None,
        defer_maintenance_identifier: typing.Optional[builtins.str] = None,
        defer_maintenance_start_time: typing.Optional[builtins.str] = None,
        destination_region: typing.Optional[builtins.str] = None,
        elastic_ip: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        endpoint: typing.Optional[typing.Union["CfnCluster.EndpointProperty", _IResolvable_da3f097b]] = None,
        enhanced_vpc_routing: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        hsm_client_certificate_identifier: typing.Optional[builtins.str] = None,
        hsm_configuration_identifier: typing.Optional[builtins.str] = None,
        iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        logging_properties: typing.Optional[typing.Union["CfnCluster.LoggingPropertiesProperty", _IResolvable_da3f097b]] = None,
        maintenance_track_name: typing.Optional[builtins.str] = None,
        manual_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        number_of_nodes: typing.Optional[jsii.Number] = None,
        owner_account: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        resource_action: typing.Optional[builtins.str] = None,
        revision_target: typing.Optional[builtins.str] = None,
        rotate_encryption_key: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        snapshot_cluster_identifier: typing.Optional[builtins.str] = None,
        snapshot_copy_grant_name: typing.Optional[builtins.str] = None,
        snapshot_copy_manual: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        snapshot_copy_retention_period: typing.Optional[jsii.Number] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Create a new ``AWS::Redshift::Cluster``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param cluster_type: ``AWS::Redshift::Cluster.ClusterType``.
        :param db_name: ``AWS::Redshift::Cluster.DBName``.
        :param master_username: ``AWS::Redshift::Cluster.MasterUsername``.
        :param master_user_password: ``AWS::Redshift::Cluster.MasterUserPassword``.
        :param node_type: ``AWS::Redshift::Cluster.NodeType``.
        :param allow_version_upgrade: ``AWS::Redshift::Cluster.AllowVersionUpgrade``.
        :param aqua_configuration_status: ``AWS::Redshift::Cluster.AquaConfigurationStatus``.
        :param automated_snapshot_retention_period: ``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.
        :param availability_zone: ``AWS::Redshift::Cluster.AvailabilityZone``.
        :param availability_zone_relocation: ``AWS::Redshift::Cluster.AvailabilityZoneRelocation``.
        :param availability_zone_relocation_status: ``AWS::Redshift::Cluster.AvailabilityZoneRelocationStatus``.
        :param classic: ``AWS::Redshift::Cluster.Classic``.
        :param cluster_identifier: ``AWS::Redshift::Cluster.ClusterIdentifier``.
        :param cluster_parameter_group_name: ``AWS::Redshift::Cluster.ClusterParameterGroupName``.
        :param cluster_security_groups: ``AWS::Redshift::Cluster.ClusterSecurityGroups``.
        :param cluster_subnet_group_name: ``AWS::Redshift::Cluster.ClusterSubnetGroupName``.
        :param cluster_version: ``AWS::Redshift::Cluster.ClusterVersion``.
        :param defer_maintenance: ``AWS::Redshift::Cluster.DeferMaintenance``.
        :param defer_maintenance_duration: ``AWS::Redshift::Cluster.DeferMaintenanceDuration``.
        :param defer_maintenance_end_time: ``AWS::Redshift::Cluster.DeferMaintenanceEndTime``.
        :param defer_maintenance_identifier: ``AWS::Redshift::Cluster.DeferMaintenanceIdentifier``.
        :param defer_maintenance_start_time: ``AWS::Redshift::Cluster.DeferMaintenanceStartTime``.
        :param destination_region: ``AWS::Redshift::Cluster.DestinationRegion``.
        :param elastic_ip: ``AWS::Redshift::Cluster.ElasticIp``.
        :param encrypted: ``AWS::Redshift::Cluster.Encrypted``.
        :param endpoint: ``AWS::Redshift::Cluster.Endpoint``.
        :param enhanced_vpc_routing: ``AWS::Redshift::Cluster.EnhancedVpcRouting``.
        :param hsm_client_certificate_identifier: ``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.
        :param hsm_configuration_identifier: ``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.
        :param iam_roles: ``AWS::Redshift::Cluster.IamRoles``.
        :param kms_key_id: ``AWS::Redshift::Cluster.KmsKeyId``.
        :param logging_properties: ``AWS::Redshift::Cluster.LoggingProperties``.
        :param maintenance_track_name: ``AWS::Redshift::Cluster.MaintenanceTrackName``.
        :param manual_snapshot_retention_period: ``AWS::Redshift::Cluster.ManualSnapshotRetentionPeriod``.
        :param number_of_nodes: ``AWS::Redshift::Cluster.NumberOfNodes``.
        :param owner_account: ``AWS::Redshift::Cluster.OwnerAccount``.
        :param port: ``AWS::Redshift::Cluster.Port``.
        :param preferred_maintenance_window: ``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.
        :param publicly_accessible: ``AWS::Redshift::Cluster.PubliclyAccessible``.
        :param resource_action: ``AWS::Redshift::Cluster.ResourceAction``.
        :param revision_target: ``AWS::Redshift::Cluster.RevisionTarget``.
        :param rotate_encryption_key: ``AWS::Redshift::Cluster.RotateEncryptionKey``.
        :param snapshot_cluster_identifier: ``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.
        :param snapshot_copy_grant_name: ``AWS::Redshift::Cluster.SnapshotCopyGrantName``.
        :param snapshot_copy_manual: ``AWS::Redshift::Cluster.SnapshotCopyManual``.
        :param snapshot_copy_retention_period: ``AWS::Redshift::Cluster.SnapshotCopyRetentionPeriod``.
        :param snapshot_identifier: ``AWS::Redshift::Cluster.SnapshotIdentifier``.
        :param tags: ``AWS::Redshift::Cluster.Tags``.
        :param vpc_security_group_ids: ``AWS::Redshift::Cluster.VpcSecurityGroupIds``.
        '''
        props = CfnClusterProps(
            cluster_type=cluster_type,
            db_name=db_name,
            master_username=master_username,
            master_user_password=master_user_password,
            node_type=node_type,
            allow_version_upgrade=allow_version_upgrade,
            aqua_configuration_status=aqua_configuration_status,
            automated_snapshot_retention_period=automated_snapshot_retention_period,
            availability_zone=availability_zone,
            availability_zone_relocation=availability_zone_relocation,
            availability_zone_relocation_status=availability_zone_relocation_status,
            classic=classic,
            cluster_identifier=cluster_identifier,
            cluster_parameter_group_name=cluster_parameter_group_name,
            cluster_security_groups=cluster_security_groups,
            cluster_subnet_group_name=cluster_subnet_group_name,
            cluster_version=cluster_version,
            defer_maintenance=defer_maintenance,
            defer_maintenance_duration=defer_maintenance_duration,
            defer_maintenance_end_time=defer_maintenance_end_time,
            defer_maintenance_identifier=defer_maintenance_identifier,
            defer_maintenance_start_time=defer_maintenance_start_time,
            destination_region=destination_region,
            elastic_ip=elastic_ip,
            encrypted=encrypted,
            endpoint=endpoint,
            enhanced_vpc_routing=enhanced_vpc_routing,
            hsm_client_certificate_identifier=hsm_client_certificate_identifier,
            hsm_configuration_identifier=hsm_configuration_identifier,
            iam_roles=iam_roles,
            kms_key_id=kms_key_id,
            logging_properties=logging_properties,
            maintenance_track_name=maintenance_track_name,
            manual_snapshot_retention_period=manual_snapshot_retention_period,
            number_of_nodes=number_of_nodes,
            owner_account=owner_account,
            port=port,
            preferred_maintenance_window=preferred_maintenance_window,
            publicly_accessible=publicly_accessible,
            resource_action=resource_action,
            revision_target=revision_target,
            rotate_encryption_key=rotate_encryption_key,
            snapshot_cluster_identifier=snapshot_cluster_identifier,
            snapshot_copy_grant_name=snapshot_copy_grant_name,
            snapshot_copy_manual=snapshot_copy_manual,
            snapshot_copy_retention_period=snapshot_copy_retention_period,
            snapshot_identifier=snapshot_identifier,
            tags=tags,
            vpc_security_group_ids=vpc_security_group_ids,
        )

        jsii.create(CfnCluster, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
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
    @jsii.member(jsii_name="attrEndpointAddress")
    def attr_endpoint_address(self) -> builtins.str:
        '''
        :cloudformationAttribute: Endpoint.Address
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrEndpointPort")
    def attr_endpoint_port(self) -> builtins.str:
        '''
        :cloudformationAttribute: Endpoint.Port
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrEndpointPort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Redshift::Cluster.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterType")
    def cluster_type(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.ClusterType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustertype
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterType"))

    @cluster_type.setter
    def cluster_type(self, value: builtins.str) -> None:
        jsii.set(self, "clusterType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbName")
    def db_name(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.DBName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-dbname
        '''
        return typing.cast(builtins.str, jsii.get(self, "dbName"))

    @db_name.setter
    def db_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.MasterUsername``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masterusername
        '''
        return typing.cast(builtins.str, jsii.get(self, "masterUsername"))

    @master_username.setter
    def master_username(self, value: builtins.str) -> None:
        jsii.set(self, "masterUsername", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUserPassword")
    def master_user_password(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.MasterUserPassword``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masteruserpassword
        '''
        return typing.cast(builtins.str, jsii.get(self, "masterUserPassword"))

    @master_user_password.setter
    def master_user_password(self, value: builtins.str) -> None:
        jsii.set(self, "masterUserPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.NodeType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
        '''
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @node_type.setter
    def node_type(self, value: builtins.str) -> None:
        jsii.set(self, "nodeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowVersionUpgrade")
    def allow_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.AllowVersionUpgrade``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-allowversionupgrade
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "allowVersionUpgrade"))

    @allow_version_upgrade.setter
    def allow_version_upgrade(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "allowVersionUpgrade", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aquaConfigurationStatus")
    def aqua_configuration_status(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.AquaConfigurationStatus``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-aquaconfigurationstatus
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aquaConfigurationStatus"))

    @aqua_configuration_status.setter
    def aqua_configuration_status(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "aquaConfigurationStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automatedSnapshotRetentionPeriod")
    def automated_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-automatedsnapshotretentionperiod
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "automatedSnapshotRetentionPeriod"))

    @automated_snapshot_retention_period.setter
    def automated_snapshot_retention_period(
        self,
        value: typing.Optional[jsii.Number],
    ) -> None:
        jsii.set(self, "automatedSnapshotRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.AvailabilityZone``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzone
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "availabilityZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneRelocation")
    def availability_zone_relocation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.AvailabilityZoneRelocation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzonerelocation
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "availabilityZoneRelocation"))

    @availability_zone_relocation.setter
    def availability_zone_relocation(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "availabilityZoneRelocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneRelocationStatus")
    def availability_zone_relocation_status(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.AvailabilityZoneRelocationStatus``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzonerelocationstatus
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneRelocationStatus"))

    @availability_zone_relocation_status.setter
    def availability_zone_relocation_status(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "availabilityZoneRelocationStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="classic")
    def classic(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.Classic``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-classic
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "classic"))

    @classic.setter
    def classic(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "classic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ClusterIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusteridentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "clusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterParameterGroupName")
    def cluster_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ClusterParameterGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterparametergroupname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterParameterGroupName"))

    @cluster_parameter_group_name.setter
    def cluster_parameter_group_name(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "clusterParameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterSecurityGroups")
    def cluster_security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Redshift::Cluster.ClusterSecurityGroups``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersecuritygroups
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "clusterSecurityGroups"))

    @cluster_security_groups.setter
    def cluster_security_groups(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "clusterSecurityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterSubnetGroupName")
    def cluster_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ClusterSubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersubnetgroupname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterSubnetGroupName"))

    @cluster_subnet_group_name.setter
    def cluster_subnet_group_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "clusterSubnetGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterVersion")
    def cluster_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ClusterVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterVersion"))

    @cluster_version.setter
    def cluster_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "clusterVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deferMaintenance")
    def defer_maintenance(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.DeferMaintenance``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenance
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "deferMaintenance"))

    @defer_maintenance.setter
    def defer_maintenance(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "deferMaintenance", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deferMaintenanceDuration")
    def defer_maintenance_duration(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.DeferMaintenanceDuration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenanceduration
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deferMaintenanceDuration"))

    @defer_maintenance_duration.setter
    def defer_maintenance_duration(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "deferMaintenanceDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deferMaintenanceEndTime")
    def defer_maintenance_end_time(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.DeferMaintenanceEndTime``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenanceendtime
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deferMaintenanceEndTime"))

    @defer_maintenance_end_time.setter
    def defer_maintenance_end_time(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "deferMaintenanceEndTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deferMaintenanceIdentifier")
    def defer_maintenance_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.DeferMaintenanceIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenanceidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deferMaintenanceIdentifier"))

    @defer_maintenance_identifier.setter
    def defer_maintenance_identifier(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "deferMaintenanceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deferMaintenanceStartTime")
    def defer_maintenance_start_time(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.DeferMaintenanceStartTime``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenancestarttime
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deferMaintenanceStartTime"))

    @defer_maintenance_start_time.setter
    def defer_maintenance_start_time(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "deferMaintenanceStartTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationRegion")
    def destination_region(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.DestinationRegion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-destinationregion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationRegion"))

    @destination_region.setter
    def destination_region(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "destinationRegion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticIp")
    def elastic_ip(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ElasticIp``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-elasticip
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticIp"))

    @elastic_ip.setter
    def elastic_ip(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "elasticIp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.Encrypted``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-encrypted
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "encrypted"))

    @encrypted.setter
    def encrypted(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "encrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(
        self,
    ) -> typing.Optional[typing.Union["CfnCluster.EndpointProperty", _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.Endpoint``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-endpoint
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCluster.EndpointProperty", _IResolvable_da3f097b]], jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(
        self,
        value: typing.Optional[typing.Union["CfnCluster.EndpointProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "endpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedVpcRouting")
    def enhanced_vpc_routing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.EnhancedVpcRouting``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-enhancedvpcrouting
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enhancedVpcRouting"))

    @enhanced_vpc_routing.setter
    def enhanced_vpc_routing(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enhancedVpcRouting", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hsmClientCertificateIdentifier")
    def hsm_client_certificate_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-hsmclientcertificateidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hsmClientCertificateIdentifier"))

    @hsm_client_certificate_identifier.setter
    def hsm_client_certificate_identifier(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "hsmClientCertificateIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hsmConfigurationIdentifier")
    def hsm_configuration_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-hsmconfigurationidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hsmConfigurationIdentifier"))

    @hsm_configuration_identifier.setter
    def hsm_configuration_identifier(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "hsmConfigurationIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoles")
    def iam_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Redshift::Cluster.IamRoles``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-iamroles
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "iamRoles"))

    @iam_roles.setter
    def iam_roles(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        jsii.set(self, "iamRoles", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-kmskeyid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingProperties")
    def logging_properties(
        self,
    ) -> typing.Optional[typing.Union["CfnCluster.LoggingPropertiesProperty", _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.LoggingProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-loggingproperties
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCluster.LoggingPropertiesProperty", _IResolvable_da3f097b]], jsii.get(self, "loggingProperties"))

    @logging_properties.setter
    def logging_properties(
        self,
        value: typing.Optional[typing.Union["CfnCluster.LoggingPropertiesProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "loggingProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceTrackName")
    def maintenance_track_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.MaintenanceTrackName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-maintenancetrackname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceTrackName"))

    @maintenance_track_name.setter
    def maintenance_track_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "maintenanceTrackName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manualSnapshotRetentionPeriod")
    def manual_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.ManualSnapshotRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-manualsnapshotretentionperiod
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "manualSnapshotRetentionPeriod"))

    @manual_snapshot_retention_period.setter
    def manual_snapshot_retention_period(
        self,
        value: typing.Optional[jsii.Number],
    ) -> None:
        jsii.set(self, "manualSnapshotRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfNodes")
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.NumberOfNodes``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-numberofnodes
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfNodes"))

    @number_of_nodes.setter
    def number_of_nodes(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "numberOfNodes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerAccount")
    def owner_account(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.OwnerAccount``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-owneraccount
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerAccount"))

    @owner_account.setter
    def owner_account(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "ownerAccount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.Port``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-port
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "port"))

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-preferredmaintenancewindow
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredMaintenanceWindow"))

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "preferredMaintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.PubliclyAccessible``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-publiclyaccessible
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "publiclyAccessible"))

    @publicly_accessible.setter
    def publicly_accessible(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "publiclyAccessible", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAction")
    def resource_action(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ResourceAction``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-resourceaction
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceAction"))

    @resource_action.setter
    def resource_action(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "resourceAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revisionTarget")
    def revision_target(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.RevisionTarget``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-revisiontarget
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "revisionTarget"))

    @revision_target.setter
    def revision_target(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "revisionTarget", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotateEncryptionKey")
    def rotate_encryption_key(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.RotateEncryptionKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-rotateencryptionkey
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "rotateEncryptionKey"))

    @rotate_encryption_key.setter
    def rotate_encryption_key(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "rotateEncryptionKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotClusterIdentifier")
    def snapshot_cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotclusteridentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotClusterIdentifier"))

    @snapshot_cluster_identifier.setter
    def snapshot_cluster_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "snapshotClusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotCopyGrantName")
    def snapshot_copy_grant_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.SnapshotCopyGrantName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotcopygrantname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotCopyGrantName"))

    @snapshot_copy_grant_name.setter
    def snapshot_copy_grant_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "snapshotCopyGrantName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotCopyManual")
    def snapshot_copy_manual(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.SnapshotCopyManual``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotcopymanual
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "snapshotCopyManual"))

    @snapshot_copy_manual.setter
    def snapshot_copy_manual(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "snapshotCopyManual", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotCopyRetentionPeriod")
    def snapshot_copy_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.SnapshotCopyRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotcopyretentionperiod
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "snapshotCopyRetentionPeriod"))

    @snapshot_copy_retention_period.setter
    def snapshot_copy_retention_period(
        self,
        value: typing.Optional[jsii.Number],
    ) -> None:
        jsii.set(self, "snapshotCopyRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.SnapshotIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdentifier"))

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "snapshotIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Redshift::Cluster.VpcSecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-vpcsecuritygroupids
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIds"))

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "vpcSecurityGroupIds", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_redshift.CfnCluster.EndpointProperty",
        jsii_struct_bases=[],
        name_mapping={"address": "address", "port": "port"},
    )
    class EndpointProperty:
        def __init__(
            self,
            *,
            address: typing.Optional[builtins.str] = None,
            port: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param address: ``CfnCluster.EndpointProperty.Address``.
            :param port: ``CfnCluster.EndpointProperty.Port``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-endpoint.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if address is not None:
                self._values["address"] = address
            if port is not None:
                self._values["port"] = port

        @builtins.property
        def address(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.EndpointProperty.Address``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-endpoint.html#cfn-redshift-cluster-endpoint-address
            '''
            result = self._values.get("address")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def port(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.EndpointProperty.Port``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-endpoint.html#cfn-redshift-cluster-endpoint-port
            '''
            result = self._values.get("port")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EndpointProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_redshift.CfnCluster.LoggingPropertiesProperty",
        jsii_struct_bases=[],
        name_mapping={"bucket_name": "bucketName", "s3_key_prefix": "s3KeyPrefix"},
    )
    class LoggingPropertiesProperty:
        def __init__(
            self,
            *,
            bucket_name: builtins.str,
            s3_key_prefix: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param bucket_name: ``CfnCluster.LoggingPropertiesProperty.BucketName``.
            :param s3_key_prefix: ``CfnCluster.LoggingPropertiesProperty.S3KeyPrefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-loggingproperties.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "bucket_name": bucket_name,
            }
            if s3_key_prefix is not None:
                self._values["s3_key_prefix"] = s3_key_prefix

        @builtins.property
        def bucket_name(self) -> builtins.str:
            '''``CfnCluster.LoggingPropertiesProperty.BucketName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-loggingproperties.html#cfn-redshift-cluster-loggingproperties-bucketname
            '''
            result = self._values.get("bucket_name")
            assert result is not None, "Required property 'bucket_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def s3_key_prefix(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.LoggingPropertiesProperty.S3KeyPrefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-loggingproperties.html#cfn-redshift-cluster-loggingproperties-s3keyprefix
            '''
            result = self._values.get("s3_key_prefix")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LoggingPropertiesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.implements(_IInspectable_c2943556)
class CfnClusterParameterGroup(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_redshift.CfnClusterParameterGroup",
):
    '''A CloudFormation ``AWS::Redshift::ClusterParameterGroup``.

    :cloudformationResource: AWS::Redshift::ClusterParameterGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: builtins.str,
        parameter_group_family: builtins.str,
        parameters: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnClusterParameterGroup.ParameterProperty", _IResolvable_da3f097b]]]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::Redshift::ClusterParameterGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param description: ``AWS::Redshift::ClusterParameterGroup.Description``.
        :param parameter_group_family: ``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.
        :param parameters: ``AWS::Redshift::ClusterParameterGroup.Parameters``.
        :param tags: ``AWS::Redshift::ClusterParameterGroup.Tags``.
        '''
        props = CfnClusterParameterGroupProps(
            description=description,
            parameter_group_family=parameter_group_family,
            parameters=parameters,
            tags=tags,
        )

        jsii.create(CfnClusterParameterGroup, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
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
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Redshift::ClusterParameterGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''``AWS::Redshift::ClusterParameterGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-description
        '''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupFamily")
    def parameter_group_family(self) -> builtins.str:
        '''``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parametergroupfamily
        '''
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupFamily"))

    @parameter_group_family.setter
    def parameter_group_family(self, value: builtins.str) -> None:
        jsii.set(self, "parameterGroupFamily", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnClusterParameterGroup.ParameterProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::Redshift::ClusterParameterGroup.Parameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parameters
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnClusterParameterGroup.ParameterProperty", _IResolvable_da3f097b]]]], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnClusterParameterGroup.ParameterProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "parameters", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_redshift.CfnClusterParameterGroup.ParameterProperty",
        jsii_struct_bases=[],
        name_mapping={
            "parameter_name": "parameterName",
            "parameter_value": "parameterValue",
        },
    )
    class ParameterProperty:
        def __init__(
            self,
            *,
            parameter_name: builtins.str,
            parameter_value: builtins.str,
        ) -> None:
            '''
            :param parameter_name: ``CfnClusterParameterGroup.ParameterProperty.ParameterName``.
            :param parameter_value: ``CfnClusterParameterGroup.ParameterProperty.ParameterValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-property-redshift-clusterparametergroup-parameter.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
            }

        @builtins.property
        def parameter_name(self) -> builtins.str:
            '''``CfnClusterParameterGroup.ParameterProperty.ParameterName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-property-redshift-clusterparametergroup-parameter.html#cfn-redshift-clusterparametergroup-parameter-parametername
            '''
            result = self._values.get("parameter_name")
            assert result is not None, "Required property 'parameter_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def parameter_value(self) -> builtins.str:
            '''``CfnClusterParameterGroup.ParameterProperty.ParameterValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-property-redshift-clusterparametergroup-parameter.html#cfn-redshift-clusterparametergroup-parameter-parametervalue
            '''
            result = self._values.get("parameter_value")
            assert result is not None, "Required property 'parameter_value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ParameterProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_redshift.CfnClusterParameterGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "parameter_group_family": "parameterGroupFamily",
        "parameters": "parameters",
        "tags": "tags",
    },
)
class CfnClusterParameterGroupProps:
    def __init__(
        self,
        *,
        description: builtins.str,
        parameter_group_family: builtins.str,
        parameters: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnClusterParameterGroup.ParameterProperty, _IResolvable_da3f097b]]]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Redshift::ClusterParameterGroup``.

        :param description: ``AWS::Redshift::ClusterParameterGroup.Description``.
        :param parameter_group_family: ``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.
        :param parameters: ``AWS::Redshift::ClusterParameterGroup.Parameters``.
        :param tags: ``AWS::Redshift::ClusterParameterGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "parameter_group_family": parameter_group_family,
        }
        if parameters is not None:
            self._values["parameters"] = parameters
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> builtins.str:
        '''``AWS::Redshift::ClusterParameterGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_group_family(self) -> builtins.str:
        '''``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parametergroupfamily
        '''
        result = self._values.get("parameter_group_family")
        assert result is not None, "Required property 'parameter_group_family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnClusterParameterGroup.ParameterProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::Redshift::ClusterParameterGroup.Parameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parameters
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnClusterParameterGroup.ParameterProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Redshift::ClusterParameterGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnClusterParameterGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_redshift.CfnClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_type": "clusterType",
        "db_name": "dbName",
        "master_username": "masterUsername",
        "master_user_password": "masterUserPassword",
        "node_type": "nodeType",
        "allow_version_upgrade": "allowVersionUpgrade",
        "aqua_configuration_status": "aquaConfigurationStatus",
        "automated_snapshot_retention_period": "automatedSnapshotRetentionPeriod",
        "availability_zone": "availabilityZone",
        "availability_zone_relocation": "availabilityZoneRelocation",
        "availability_zone_relocation_status": "availabilityZoneRelocationStatus",
        "classic": "classic",
        "cluster_identifier": "clusterIdentifier",
        "cluster_parameter_group_name": "clusterParameterGroupName",
        "cluster_security_groups": "clusterSecurityGroups",
        "cluster_subnet_group_name": "clusterSubnetGroupName",
        "cluster_version": "clusterVersion",
        "defer_maintenance": "deferMaintenance",
        "defer_maintenance_duration": "deferMaintenanceDuration",
        "defer_maintenance_end_time": "deferMaintenanceEndTime",
        "defer_maintenance_identifier": "deferMaintenanceIdentifier",
        "defer_maintenance_start_time": "deferMaintenanceStartTime",
        "destination_region": "destinationRegion",
        "elastic_ip": "elasticIp",
        "encrypted": "encrypted",
        "endpoint": "endpoint",
        "enhanced_vpc_routing": "enhancedVpcRouting",
        "hsm_client_certificate_identifier": "hsmClientCertificateIdentifier",
        "hsm_configuration_identifier": "hsmConfigurationIdentifier",
        "iam_roles": "iamRoles",
        "kms_key_id": "kmsKeyId",
        "logging_properties": "loggingProperties",
        "maintenance_track_name": "maintenanceTrackName",
        "manual_snapshot_retention_period": "manualSnapshotRetentionPeriod",
        "number_of_nodes": "numberOfNodes",
        "owner_account": "ownerAccount",
        "port": "port",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "publicly_accessible": "publiclyAccessible",
        "resource_action": "resourceAction",
        "revision_target": "revisionTarget",
        "rotate_encryption_key": "rotateEncryptionKey",
        "snapshot_cluster_identifier": "snapshotClusterIdentifier",
        "snapshot_copy_grant_name": "snapshotCopyGrantName",
        "snapshot_copy_manual": "snapshotCopyManual",
        "snapshot_copy_retention_period": "snapshotCopyRetentionPeriod",
        "snapshot_identifier": "snapshotIdentifier",
        "tags": "tags",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class CfnClusterProps:
    def __init__(
        self,
        *,
        cluster_type: builtins.str,
        db_name: builtins.str,
        master_username: builtins.str,
        master_user_password: builtins.str,
        node_type: builtins.str,
        allow_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        aqua_configuration_status: typing.Optional[builtins.str] = None,
        automated_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        availability_zone_relocation: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        availability_zone_relocation_status: typing.Optional[builtins.str] = None,
        classic: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        cluster_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        cluster_subnet_group_name: typing.Optional[builtins.str] = None,
        cluster_version: typing.Optional[builtins.str] = None,
        defer_maintenance: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        defer_maintenance_duration: typing.Optional[jsii.Number] = None,
        defer_maintenance_end_time: typing.Optional[builtins.str] = None,
        defer_maintenance_identifier: typing.Optional[builtins.str] = None,
        defer_maintenance_start_time: typing.Optional[builtins.str] = None,
        destination_region: typing.Optional[builtins.str] = None,
        elastic_ip: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        endpoint: typing.Optional[typing.Union[CfnCluster.EndpointProperty, _IResolvable_da3f097b]] = None,
        enhanced_vpc_routing: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        hsm_client_certificate_identifier: typing.Optional[builtins.str] = None,
        hsm_configuration_identifier: typing.Optional[builtins.str] = None,
        iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        logging_properties: typing.Optional[typing.Union[CfnCluster.LoggingPropertiesProperty, _IResolvable_da3f097b]] = None,
        maintenance_track_name: typing.Optional[builtins.str] = None,
        manual_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        number_of_nodes: typing.Optional[jsii.Number] = None,
        owner_account: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        resource_action: typing.Optional[builtins.str] = None,
        revision_target: typing.Optional[builtins.str] = None,
        rotate_encryption_key: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        snapshot_cluster_identifier: typing.Optional[builtins.str] = None,
        snapshot_copy_grant_name: typing.Optional[builtins.str] = None,
        snapshot_copy_manual: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        snapshot_copy_retention_period: typing.Optional[jsii.Number] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Redshift::Cluster``.

        :param cluster_type: ``AWS::Redshift::Cluster.ClusterType``.
        :param db_name: ``AWS::Redshift::Cluster.DBName``.
        :param master_username: ``AWS::Redshift::Cluster.MasterUsername``.
        :param master_user_password: ``AWS::Redshift::Cluster.MasterUserPassword``.
        :param node_type: ``AWS::Redshift::Cluster.NodeType``.
        :param allow_version_upgrade: ``AWS::Redshift::Cluster.AllowVersionUpgrade``.
        :param aqua_configuration_status: ``AWS::Redshift::Cluster.AquaConfigurationStatus``.
        :param automated_snapshot_retention_period: ``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.
        :param availability_zone: ``AWS::Redshift::Cluster.AvailabilityZone``.
        :param availability_zone_relocation: ``AWS::Redshift::Cluster.AvailabilityZoneRelocation``.
        :param availability_zone_relocation_status: ``AWS::Redshift::Cluster.AvailabilityZoneRelocationStatus``.
        :param classic: ``AWS::Redshift::Cluster.Classic``.
        :param cluster_identifier: ``AWS::Redshift::Cluster.ClusterIdentifier``.
        :param cluster_parameter_group_name: ``AWS::Redshift::Cluster.ClusterParameterGroupName``.
        :param cluster_security_groups: ``AWS::Redshift::Cluster.ClusterSecurityGroups``.
        :param cluster_subnet_group_name: ``AWS::Redshift::Cluster.ClusterSubnetGroupName``.
        :param cluster_version: ``AWS::Redshift::Cluster.ClusterVersion``.
        :param defer_maintenance: ``AWS::Redshift::Cluster.DeferMaintenance``.
        :param defer_maintenance_duration: ``AWS::Redshift::Cluster.DeferMaintenanceDuration``.
        :param defer_maintenance_end_time: ``AWS::Redshift::Cluster.DeferMaintenanceEndTime``.
        :param defer_maintenance_identifier: ``AWS::Redshift::Cluster.DeferMaintenanceIdentifier``.
        :param defer_maintenance_start_time: ``AWS::Redshift::Cluster.DeferMaintenanceStartTime``.
        :param destination_region: ``AWS::Redshift::Cluster.DestinationRegion``.
        :param elastic_ip: ``AWS::Redshift::Cluster.ElasticIp``.
        :param encrypted: ``AWS::Redshift::Cluster.Encrypted``.
        :param endpoint: ``AWS::Redshift::Cluster.Endpoint``.
        :param enhanced_vpc_routing: ``AWS::Redshift::Cluster.EnhancedVpcRouting``.
        :param hsm_client_certificate_identifier: ``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.
        :param hsm_configuration_identifier: ``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.
        :param iam_roles: ``AWS::Redshift::Cluster.IamRoles``.
        :param kms_key_id: ``AWS::Redshift::Cluster.KmsKeyId``.
        :param logging_properties: ``AWS::Redshift::Cluster.LoggingProperties``.
        :param maintenance_track_name: ``AWS::Redshift::Cluster.MaintenanceTrackName``.
        :param manual_snapshot_retention_period: ``AWS::Redshift::Cluster.ManualSnapshotRetentionPeriod``.
        :param number_of_nodes: ``AWS::Redshift::Cluster.NumberOfNodes``.
        :param owner_account: ``AWS::Redshift::Cluster.OwnerAccount``.
        :param port: ``AWS::Redshift::Cluster.Port``.
        :param preferred_maintenance_window: ``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.
        :param publicly_accessible: ``AWS::Redshift::Cluster.PubliclyAccessible``.
        :param resource_action: ``AWS::Redshift::Cluster.ResourceAction``.
        :param revision_target: ``AWS::Redshift::Cluster.RevisionTarget``.
        :param rotate_encryption_key: ``AWS::Redshift::Cluster.RotateEncryptionKey``.
        :param snapshot_cluster_identifier: ``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.
        :param snapshot_copy_grant_name: ``AWS::Redshift::Cluster.SnapshotCopyGrantName``.
        :param snapshot_copy_manual: ``AWS::Redshift::Cluster.SnapshotCopyManual``.
        :param snapshot_copy_retention_period: ``AWS::Redshift::Cluster.SnapshotCopyRetentionPeriod``.
        :param snapshot_identifier: ``AWS::Redshift::Cluster.SnapshotIdentifier``.
        :param tags: ``AWS::Redshift::Cluster.Tags``.
        :param vpc_security_group_ids: ``AWS::Redshift::Cluster.VpcSecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_type": cluster_type,
            "db_name": db_name,
            "master_username": master_username,
            "master_user_password": master_user_password,
            "node_type": node_type,
        }
        if allow_version_upgrade is not None:
            self._values["allow_version_upgrade"] = allow_version_upgrade
        if aqua_configuration_status is not None:
            self._values["aqua_configuration_status"] = aqua_configuration_status
        if automated_snapshot_retention_period is not None:
            self._values["automated_snapshot_retention_period"] = automated_snapshot_retention_period
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if availability_zone_relocation is not None:
            self._values["availability_zone_relocation"] = availability_zone_relocation
        if availability_zone_relocation_status is not None:
            self._values["availability_zone_relocation_status"] = availability_zone_relocation_status
        if classic is not None:
            self._values["classic"] = classic
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if cluster_parameter_group_name is not None:
            self._values["cluster_parameter_group_name"] = cluster_parameter_group_name
        if cluster_security_groups is not None:
            self._values["cluster_security_groups"] = cluster_security_groups
        if cluster_subnet_group_name is not None:
            self._values["cluster_subnet_group_name"] = cluster_subnet_group_name
        if cluster_version is not None:
            self._values["cluster_version"] = cluster_version
        if defer_maintenance is not None:
            self._values["defer_maintenance"] = defer_maintenance
        if defer_maintenance_duration is not None:
            self._values["defer_maintenance_duration"] = defer_maintenance_duration
        if defer_maintenance_end_time is not None:
            self._values["defer_maintenance_end_time"] = defer_maintenance_end_time
        if defer_maintenance_identifier is not None:
            self._values["defer_maintenance_identifier"] = defer_maintenance_identifier
        if defer_maintenance_start_time is not None:
            self._values["defer_maintenance_start_time"] = defer_maintenance_start_time
        if destination_region is not None:
            self._values["destination_region"] = destination_region
        if elastic_ip is not None:
            self._values["elastic_ip"] = elastic_ip
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if enhanced_vpc_routing is not None:
            self._values["enhanced_vpc_routing"] = enhanced_vpc_routing
        if hsm_client_certificate_identifier is not None:
            self._values["hsm_client_certificate_identifier"] = hsm_client_certificate_identifier
        if hsm_configuration_identifier is not None:
            self._values["hsm_configuration_identifier"] = hsm_configuration_identifier
        if iam_roles is not None:
            self._values["iam_roles"] = iam_roles
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if logging_properties is not None:
            self._values["logging_properties"] = logging_properties
        if maintenance_track_name is not None:
            self._values["maintenance_track_name"] = maintenance_track_name
        if manual_snapshot_retention_period is not None:
            self._values["manual_snapshot_retention_period"] = manual_snapshot_retention_period
        if number_of_nodes is not None:
            self._values["number_of_nodes"] = number_of_nodes
        if owner_account is not None:
            self._values["owner_account"] = owner_account
        if port is not None:
            self._values["port"] = port
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if publicly_accessible is not None:
            self._values["publicly_accessible"] = publicly_accessible
        if resource_action is not None:
            self._values["resource_action"] = resource_action
        if revision_target is not None:
            self._values["revision_target"] = revision_target
        if rotate_encryption_key is not None:
            self._values["rotate_encryption_key"] = rotate_encryption_key
        if snapshot_cluster_identifier is not None:
            self._values["snapshot_cluster_identifier"] = snapshot_cluster_identifier
        if snapshot_copy_grant_name is not None:
            self._values["snapshot_copy_grant_name"] = snapshot_copy_grant_name
        if snapshot_copy_manual is not None:
            self._values["snapshot_copy_manual"] = snapshot_copy_manual
        if snapshot_copy_retention_period is not None:
            self._values["snapshot_copy_retention_period"] = snapshot_copy_retention_period
        if snapshot_identifier is not None:
            self._values["snapshot_identifier"] = snapshot_identifier
        if tags is not None:
            self._values["tags"] = tags
        if vpc_security_group_ids is not None:
            self._values["vpc_security_group_ids"] = vpc_security_group_ids

    @builtins.property
    def cluster_type(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.ClusterType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustertype
        '''
        result = self._values.get("cluster_type")
        assert result is not None, "Required property 'cluster_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_name(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.DBName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-dbname
        '''
        result = self._values.get("db_name")
        assert result is not None, "Required property 'db_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def master_username(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.MasterUsername``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masterusername
        '''
        result = self._values.get("master_username")
        assert result is not None, "Required property 'master_username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def master_user_password(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.MasterUserPassword``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masteruserpassword
        '''
        result = self._values.get("master_user_password")
        assert result is not None, "Required property 'master_user_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def node_type(self) -> builtins.str:
        '''``AWS::Redshift::Cluster.NodeType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
        '''
        result = self._values.get("node_type")
        assert result is not None, "Required property 'node_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.AllowVersionUpgrade``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-allowversionupgrade
        '''
        result = self._values.get("allow_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def aqua_configuration_status(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.AquaConfigurationStatus``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-aquaconfigurationstatus
        '''
        result = self._values.get("aqua_configuration_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def automated_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-automatedsnapshotretentionperiod
        '''
        result = self._values.get("automated_snapshot_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.AvailabilityZone``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzone
        '''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def availability_zone_relocation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.AvailabilityZoneRelocation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzonerelocation
        '''
        result = self._values.get("availability_zone_relocation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def availability_zone_relocation_status(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.AvailabilityZoneRelocationStatus``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzonerelocationstatus
        '''
        result = self._values.get("availability_zone_relocation_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def classic(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.Classic``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-classic
        '''
        result = self._values.get("classic")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ClusterIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusteridentifier
        '''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ClusterParameterGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterparametergroupname
        '''
        result = self._values.get("cluster_parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Redshift::Cluster.ClusterSecurityGroups``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersecuritygroups
        '''
        result = self._values.get("cluster_security_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cluster_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ClusterSubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersubnetgroupname
        '''
        result = self._values.get("cluster_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ClusterVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterversion
        '''
        result = self._values.get("cluster_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def defer_maintenance(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.DeferMaintenance``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenance
        '''
        result = self._values.get("defer_maintenance")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def defer_maintenance_duration(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.DeferMaintenanceDuration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenanceduration
        '''
        result = self._values.get("defer_maintenance_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def defer_maintenance_end_time(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.DeferMaintenanceEndTime``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenanceendtime
        '''
        result = self._values.get("defer_maintenance_end_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def defer_maintenance_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.DeferMaintenanceIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenanceidentifier
        '''
        result = self._values.get("defer_maintenance_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def defer_maintenance_start_time(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.DeferMaintenanceStartTime``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-defermaintenancestarttime
        '''
        result = self._values.get("defer_maintenance_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_region(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.DestinationRegion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-destinationregion
        '''
        result = self._values.get("destination_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elastic_ip(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ElasticIp``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-elasticip
        '''
        result = self._values.get("elastic_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.Encrypted``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-encrypted
        '''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def endpoint(
        self,
    ) -> typing.Optional[typing.Union[CfnCluster.EndpointProperty, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.Endpoint``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-endpoint
        '''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[typing.Union[CfnCluster.EndpointProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def enhanced_vpc_routing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.EnhancedVpcRouting``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-enhancedvpcrouting
        '''
        result = self._values.get("enhanced_vpc_routing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def hsm_client_certificate_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-hsmclientcertificateidentifier
        '''
        result = self._values.get("hsm_client_certificate_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hsm_configuration_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-hsmconfigurationidentifier
        '''
        result = self._values.get("hsm_configuration_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Redshift::Cluster.IamRoles``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-iamroles
        '''
        result = self._values.get("iam_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-kmskeyid
        '''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_properties(
        self,
    ) -> typing.Optional[typing.Union[CfnCluster.LoggingPropertiesProperty, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.LoggingProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-loggingproperties
        '''
        result = self._values.get("logging_properties")
        return typing.cast(typing.Optional[typing.Union[CfnCluster.LoggingPropertiesProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def maintenance_track_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.MaintenanceTrackName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-maintenancetrackname
        '''
        result = self._values.get("maintenance_track_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def manual_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.ManualSnapshotRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-manualsnapshotretentionperiod
        '''
        result = self._values.get("manual_snapshot_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.NumberOfNodes``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-numberofnodes
        '''
        result = self._values.get("number_of_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def owner_account(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.OwnerAccount``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-owneraccount
        '''
        result = self._values.get("owner_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.Port``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-port
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-preferredmaintenancewindow
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publicly_accessible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.PubliclyAccessible``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-publiclyaccessible
        '''
        result = self._values.get("publicly_accessible")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def resource_action(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.ResourceAction``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-resourceaction
        '''
        result = self._values.get("resource_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def revision_target(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.RevisionTarget``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-revisiontarget
        '''
        result = self._values.get("revision_target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotate_encryption_key(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.RotateEncryptionKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-rotateencryptionkey
        '''
        result = self._values.get("rotate_encryption_key")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def snapshot_cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotclusteridentifier
        '''
        result = self._values.get("snapshot_cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_copy_grant_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.SnapshotCopyGrantName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotcopygrantname
        '''
        result = self._values.get("snapshot_copy_grant_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_copy_manual(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Redshift::Cluster.SnapshotCopyManual``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotcopymanual
        '''
        result = self._values.get("snapshot_copy_manual")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def snapshot_copy_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Redshift::Cluster.SnapshotCopyRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotcopyretentionperiod
        '''
        result = self._values.get("snapshot_copy_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::Cluster.SnapshotIdentifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotidentifier
        '''
        result = self._values.get("snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Redshift::Cluster.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Redshift::Cluster.VpcSecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-vpcsecuritygroupids
        '''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnClusterSecurityGroup(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_redshift.CfnClusterSecurityGroup",
):
    '''A CloudFormation ``AWS::Redshift::ClusterSecurityGroup``.

    :cloudformationResource: AWS::Redshift::ClusterSecurityGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::Redshift::ClusterSecurityGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param description: ``AWS::Redshift::ClusterSecurityGroup.Description``.
        :param tags: ``AWS::Redshift::ClusterSecurityGroup.Tags``.
        '''
        props = CfnClusterSecurityGroupProps(description=description, tags=tags)

        jsii.create(CfnClusterSecurityGroup, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
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
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Redshift::ClusterSecurityGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''``AWS::Redshift::ClusterSecurityGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-description
        '''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)


@jsii.implements(_IInspectable_c2943556)
class CfnClusterSecurityGroupIngress(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_redshift.CfnClusterSecurityGroupIngress",
):
    '''A CloudFormation ``AWS::Redshift::ClusterSecurityGroupIngress``.

    :cloudformationResource: AWS::Redshift::ClusterSecurityGroupIngress
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_security_group_name: builtins.str,
        cidrip: typing.Optional[builtins.str] = None,
        ec2_security_group_name: typing.Optional[builtins.str] = None,
        ec2_security_group_owner_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Redshift::ClusterSecurityGroupIngress``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param cluster_security_group_name: ``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.
        :param cidrip: ``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.
        :param ec2_security_group_name: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.
        :param ec2_security_group_owner_id: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.
        '''
        props = CfnClusterSecurityGroupIngressProps(
            cluster_security_group_name=cluster_security_group_name,
            cidrip=cidrip,
            ec2_security_group_name=ec2_security_group_name,
            ec2_security_group_owner_id=ec2_security_group_owner_id,
        )

        jsii.create(CfnClusterSecurityGroupIngress, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
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
    @jsii.member(jsii_name="clusterSecurityGroupName")
    def cluster_security_group_name(self) -> builtins.str:
        '''``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-clustersecuritygroupname
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterSecurityGroupName"))

    @cluster_security_group_name.setter
    def cluster_security_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterSecurityGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cidrip")
    def cidrip(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-cidrip
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cidrip"))

    @cidrip.setter
    def cidrip(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "cidrip", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2SecurityGroupName")
    def ec2_security_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ec2SecurityGroupName"))

    @ec2_security_group_name.setter
    def ec2_security_group_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "ec2SecurityGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2SecurityGroupOwnerId")
    def ec2_security_group_owner_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupownerid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ec2SecurityGroupOwnerId"))

    @ec2_security_group_owner_id.setter
    def ec2_security_group_owner_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "ec2SecurityGroupOwnerId", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_redshift.CfnClusterSecurityGroupIngressProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_security_group_name": "clusterSecurityGroupName",
        "cidrip": "cidrip",
        "ec2_security_group_name": "ec2SecurityGroupName",
        "ec2_security_group_owner_id": "ec2SecurityGroupOwnerId",
    },
)
class CfnClusterSecurityGroupIngressProps:
    def __init__(
        self,
        *,
        cluster_security_group_name: builtins.str,
        cidrip: typing.Optional[builtins.str] = None,
        ec2_security_group_name: typing.Optional[builtins.str] = None,
        ec2_security_group_owner_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Redshift::ClusterSecurityGroupIngress``.

        :param cluster_security_group_name: ``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.
        :param cidrip: ``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.
        :param ec2_security_group_name: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.
        :param ec2_security_group_owner_id: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_security_group_name": cluster_security_group_name,
        }
        if cidrip is not None:
            self._values["cidrip"] = cidrip
        if ec2_security_group_name is not None:
            self._values["ec2_security_group_name"] = ec2_security_group_name
        if ec2_security_group_owner_id is not None:
            self._values["ec2_security_group_owner_id"] = ec2_security_group_owner_id

    @builtins.property
    def cluster_security_group_name(self) -> builtins.str:
        '''``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-clustersecuritygroupname
        '''
        result = self._values.get("cluster_security_group_name")
        assert result is not None, "Required property 'cluster_security_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cidrip(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-cidrip
        '''
        result = self._values.get("cidrip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_security_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupname
        '''
        result = self._values.get("ec2_security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_security_group_owner_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupownerid
        '''
        result = self._values.get("ec2_security_group_owner_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnClusterSecurityGroupIngressProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_redshift.CfnClusterSecurityGroupProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "tags": "tags"},
)
class CfnClusterSecurityGroupProps:
    def __init__(
        self,
        *,
        description: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Redshift::ClusterSecurityGroup``.

        :param description: ``AWS::Redshift::ClusterSecurityGroup.Description``.
        :param tags: ``AWS::Redshift::ClusterSecurityGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
        }
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> builtins.str:
        '''``AWS::Redshift::ClusterSecurityGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Redshift::ClusterSecurityGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnClusterSecurityGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnClusterSubnetGroup(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_redshift.CfnClusterSubnetGroup",
):
    '''A CloudFormation ``AWS::Redshift::ClusterSubnetGroup``.

    :cloudformationResource: AWS::Redshift::ClusterSubnetGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::Redshift::ClusterSubnetGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param description: ``AWS::Redshift::ClusterSubnetGroup.Description``.
        :param subnet_ids: ``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.
        :param tags: ``AWS::Redshift::ClusterSubnetGroup.Tags``.
        '''
        props = CfnClusterSubnetGroupProps(
            description=description, subnet_ids=subnet_ids, tags=tags
        )

        jsii.create(CfnClusterSubnetGroup, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
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
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Redshift::ClusterSubnetGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''``AWS::Redshift::ClusterSubnetGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-description
        '''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-subnetids
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_redshift.CfnClusterSubnetGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "subnet_ids": "subnetIds",
        "tags": "tags",
    },
)
class CfnClusterSubnetGroupProps:
    def __init__(
        self,
        *,
        description: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Redshift::ClusterSubnetGroup``.

        :param description: ``AWS::Redshift::ClusterSubnetGroup.Description``.
        :param subnet_ids: ``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.
        :param tags: ``AWS::Redshift::ClusterSubnetGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "subnet_ids": subnet_ids,
        }
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> builtins.str:
        '''``AWS::Redshift::ClusterSubnetGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-subnetids
        '''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Redshift::ClusterSubnetGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnClusterSubnetGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnCluster",
    "CfnClusterParameterGroup",
    "CfnClusterParameterGroupProps",
    "CfnClusterProps",
    "CfnClusterSecurityGroup",
    "CfnClusterSecurityGroupIngress",
    "CfnClusterSecurityGroupIngressProps",
    "CfnClusterSecurityGroupProps",
    "CfnClusterSubnetGroup",
    "CfnClusterSubnetGroupProps",
]

publication.publish()
