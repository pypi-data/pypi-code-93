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
    IInspectable as _IInspectable_c2943556,
    IResolvable as _IResolvable_da3f097b,
    TagManager as _TagManager_0a598cb3,
    TreeInspector as _TreeInspector_488e0dd5,
)


@jsii.implements(_IInspectable_c2943556)
class CfnCluster(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_msk.CfnCluster",
):
    '''A CloudFormation ``AWS::MSK::Cluster``.

    :cloudformationResource: AWS::MSK::Cluster
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        broker_node_group_info: typing.Union["CfnCluster.BrokerNodeGroupInfoProperty", _IResolvable_da3f097b],
        cluster_name: builtins.str,
        kafka_version: builtins.str,
        number_of_broker_nodes: jsii.Number,
        client_authentication: typing.Optional[typing.Union["CfnCluster.ClientAuthenticationProperty", _IResolvable_da3f097b]] = None,
        configuration_info: typing.Optional[typing.Union["CfnCluster.ConfigurationInfoProperty", _IResolvable_da3f097b]] = None,
        encryption_info: typing.Optional[typing.Union["CfnCluster.EncryptionInfoProperty", _IResolvable_da3f097b]] = None,
        enhanced_monitoring: typing.Optional[builtins.str] = None,
        logging_info: typing.Optional[typing.Union["CfnCluster.LoggingInfoProperty", _IResolvable_da3f097b]] = None,
        open_monitoring: typing.Optional[typing.Union["CfnCluster.OpenMonitoringProperty", _IResolvable_da3f097b]] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::MSK::Cluster``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param broker_node_group_info: ``AWS::MSK::Cluster.BrokerNodeGroupInfo``.
        :param cluster_name: ``AWS::MSK::Cluster.ClusterName``.
        :param kafka_version: ``AWS::MSK::Cluster.KafkaVersion``.
        :param number_of_broker_nodes: ``AWS::MSK::Cluster.NumberOfBrokerNodes``.
        :param client_authentication: ``AWS::MSK::Cluster.ClientAuthentication``.
        :param configuration_info: ``AWS::MSK::Cluster.ConfigurationInfo``.
        :param encryption_info: ``AWS::MSK::Cluster.EncryptionInfo``.
        :param enhanced_monitoring: ``AWS::MSK::Cluster.EnhancedMonitoring``.
        :param logging_info: ``AWS::MSK::Cluster.LoggingInfo``.
        :param open_monitoring: ``AWS::MSK::Cluster.OpenMonitoring``.
        :param tags: ``AWS::MSK::Cluster.Tags``.
        '''
        props = CfnClusterProps(
            broker_node_group_info=broker_node_group_info,
            cluster_name=cluster_name,
            kafka_version=kafka_version,
            number_of_broker_nodes=number_of_broker_nodes,
            client_authentication=client_authentication,
            configuration_info=configuration_info,
            encryption_info=encryption_info,
            enhanced_monitoring=enhanced_monitoring,
            logging_info=logging_info,
            open_monitoring=open_monitoring,
            tags=tags,
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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::MSK::Cluster.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerNodeGroupInfo")
    def broker_node_group_info(
        self,
    ) -> typing.Union["CfnCluster.BrokerNodeGroupInfoProperty", _IResolvable_da3f097b]:
        '''``AWS::MSK::Cluster.BrokerNodeGroupInfo``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-brokernodegroupinfo
        '''
        return typing.cast(typing.Union["CfnCluster.BrokerNodeGroupInfoProperty", _IResolvable_da3f097b], jsii.get(self, "brokerNodeGroupInfo"))

    @broker_node_group_info.setter
    def broker_node_group_info(
        self,
        value: typing.Union["CfnCluster.BrokerNodeGroupInfoProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "brokerNodeGroupInfo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''``AWS::MSK::Cluster.ClusterName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-clustername
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersion")
    def kafka_version(self) -> builtins.str:
        '''``AWS::MSK::Cluster.KafkaVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-kafkaversion
        '''
        return typing.cast(builtins.str, jsii.get(self, "kafkaVersion"))

    @kafka_version.setter
    def kafka_version(self, value: builtins.str) -> None:
        jsii.set(self, "kafkaVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfBrokerNodes")
    def number_of_broker_nodes(self) -> jsii.Number:
        '''``AWS::MSK::Cluster.NumberOfBrokerNodes``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-numberofbrokernodes
        '''
        return typing.cast(jsii.Number, jsii.get(self, "numberOfBrokerNodes"))

    @number_of_broker_nodes.setter
    def number_of_broker_nodes(self, value: jsii.Number) -> None:
        jsii.set(self, "numberOfBrokerNodes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientAuthentication")
    def client_authentication(
        self,
    ) -> typing.Optional[typing.Union["CfnCluster.ClientAuthenticationProperty", _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.ClientAuthentication``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-clientauthentication
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCluster.ClientAuthenticationProperty", _IResolvable_da3f097b]], jsii.get(self, "clientAuthentication"))

    @client_authentication.setter
    def client_authentication(
        self,
        value: typing.Optional[typing.Union["CfnCluster.ClientAuthenticationProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "clientAuthentication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInfo")
    def configuration_info(
        self,
    ) -> typing.Optional[typing.Union["CfnCluster.ConfigurationInfoProperty", _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.ConfigurationInfo``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-configurationinfo
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCluster.ConfigurationInfoProperty", _IResolvable_da3f097b]], jsii.get(self, "configurationInfo"))

    @configuration_info.setter
    def configuration_info(
        self,
        value: typing.Optional[typing.Union["CfnCluster.ConfigurationInfoProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "configurationInfo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInfo")
    def encryption_info(
        self,
    ) -> typing.Optional[typing.Union["CfnCluster.EncryptionInfoProperty", _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.EncryptionInfo``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-encryptioninfo
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCluster.EncryptionInfoProperty", _IResolvable_da3f097b]], jsii.get(self, "encryptionInfo"))

    @encryption_info.setter
    def encryption_info(
        self,
        value: typing.Optional[typing.Union["CfnCluster.EncryptionInfoProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "encryptionInfo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedMonitoring")
    def enhanced_monitoring(self) -> typing.Optional[builtins.str]:
        '''``AWS::MSK::Cluster.EnhancedMonitoring``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-enhancedmonitoring
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enhancedMonitoring"))

    @enhanced_monitoring.setter
    def enhanced_monitoring(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "enhancedMonitoring", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingInfo")
    def logging_info(
        self,
    ) -> typing.Optional[typing.Union["CfnCluster.LoggingInfoProperty", _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.LoggingInfo``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-logginginfo
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCluster.LoggingInfoProperty", _IResolvable_da3f097b]], jsii.get(self, "loggingInfo"))

    @logging_info.setter
    def logging_info(
        self,
        value: typing.Optional[typing.Union["CfnCluster.LoggingInfoProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "loggingInfo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openMonitoring")
    def open_monitoring(
        self,
    ) -> typing.Optional[typing.Union["CfnCluster.OpenMonitoringProperty", _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.OpenMonitoring``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-openmonitoring
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCluster.OpenMonitoringProperty", _IResolvable_da3f097b]], jsii.get(self, "openMonitoring"))

    @open_monitoring.setter
    def open_monitoring(
        self,
        value: typing.Optional[typing.Union["CfnCluster.OpenMonitoringProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "openMonitoring", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.BrokerLogsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "cloud_watch_logs": "cloudWatchLogs",
            "firehose": "firehose",
            "s3": "s3",
        },
    )
    class BrokerLogsProperty:
        def __init__(
            self,
            *,
            cloud_watch_logs: typing.Optional[typing.Union["CfnCluster.CloudWatchLogsProperty", _IResolvable_da3f097b]] = None,
            firehose: typing.Optional[typing.Union["CfnCluster.FirehoseProperty", _IResolvable_da3f097b]] = None,
            s3: typing.Optional[typing.Union["CfnCluster.S3Property", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param cloud_watch_logs: ``CfnCluster.BrokerLogsProperty.CloudWatchLogs``.
            :param firehose: ``CfnCluster.BrokerLogsProperty.Firehose``.
            :param s3: ``CfnCluster.BrokerLogsProperty.S3``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokerlogs.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if cloud_watch_logs is not None:
                self._values["cloud_watch_logs"] = cloud_watch_logs
            if firehose is not None:
                self._values["firehose"] = firehose
            if s3 is not None:
                self._values["s3"] = s3

        @builtins.property
        def cloud_watch_logs(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.CloudWatchLogsProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.BrokerLogsProperty.CloudWatchLogs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokerlogs.html#cfn-msk-cluster-brokerlogs-cloudwatchlogs
            '''
            result = self._values.get("cloud_watch_logs")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.CloudWatchLogsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def firehose(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.FirehoseProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.BrokerLogsProperty.Firehose``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokerlogs.html#cfn-msk-cluster-brokerlogs-firehose
            '''
            result = self._values.get("firehose")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.FirehoseProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def s3(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.S3Property", _IResolvable_da3f097b]]:
            '''``CfnCluster.BrokerLogsProperty.S3``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokerlogs.html#cfn-msk-cluster-brokerlogs-s3
            '''
            result = self._values.get("s3")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.S3Property", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BrokerLogsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.BrokerNodeGroupInfoProperty",
        jsii_struct_bases=[],
        name_mapping={
            "client_subnets": "clientSubnets",
            "instance_type": "instanceType",
            "broker_az_distribution": "brokerAzDistribution",
            "security_groups": "securityGroups",
            "storage_info": "storageInfo",
        },
    )
    class BrokerNodeGroupInfoProperty:
        def __init__(
            self,
            *,
            client_subnets: typing.Sequence[builtins.str],
            instance_type: builtins.str,
            broker_az_distribution: typing.Optional[builtins.str] = None,
            security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
            storage_info: typing.Optional[typing.Union["CfnCluster.StorageInfoProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param client_subnets: ``CfnCluster.BrokerNodeGroupInfoProperty.ClientSubnets``.
            :param instance_type: ``CfnCluster.BrokerNodeGroupInfoProperty.InstanceType``.
            :param broker_az_distribution: ``CfnCluster.BrokerNodeGroupInfoProperty.BrokerAZDistribution``.
            :param security_groups: ``CfnCluster.BrokerNodeGroupInfoProperty.SecurityGroups``.
            :param storage_info: ``CfnCluster.BrokerNodeGroupInfoProperty.StorageInfo``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "client_subnets": client_subnets,
                "instance_type": instance_type,
            }
            if broker_az_distribution is not None:
                self._values["broker_az_distribution"] = broker_az_distribution
            if security_groups is not None:
                self._values["security_groups"] = security_groups
            if storage_info is not None:
                self._values["storage_info"] = storage_info

        @builtins.property
        def client_subnets(self) -> typing.List[builtins.str]:
            '''``CfnCluster.BrokerNodeGroupInfoProperty.ClientSubnets``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-clientsubnets
            '''
            result = self._values.get("client_subnets")
            assert result is not None, "Required property 'client_subnets' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def instance_type(self) -> builtins.str:
            '''``CfnCluster.BrokerNodeGroupInfoProperty.InstanceType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-instancetype
            '''
            result = self._values.get("instance_type")
            assert result is not None, "Required property 'instance_type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def broker_az_distribution(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.BrokerNodeGroupInfoProperty.BrokerAZDistribution``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-brokerazdistribution
            '''
            result = self._values.get("broker_az_distribution")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnCluster.BrokerNodeGroupInfoProperty.SecurityGroups``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-securitygroups
            '''
            result = self._values.get("security_groups")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def storage_info(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.StorageInfoProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.BrokerNodeGroupInfoProperty.StorageInfo``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-storageinfo
            '''
            result = self._values.get("storage_info")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.StorageInfoProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BrokerNodeGroupInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.ClientAuthenticationProperty",
        jsii_struct_bases=[],
        name_mapping={"sasl": "sasl", "tls": "tls"},
    )
    class ClientAuthenticationProperty:
        def __init__(
            self,
            *,
            sasl: typing.Optional[typing.Union["CfnCluster.SaslProperty", _IResolvable_da3f097b]] = None,
            tls: typing.Optional[typing.Union["CfnCluster.TlsProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param sasl: ``CfnCluster.ClientAuthenticationProperty.Sasl``.
            :param tls: ``CfnCluster.ClientAuthenticationProperty.Tls``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-clientauthentication.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if sasl is not None:
                self._values["sasl"] = sasl
            if tls is not None:
                self._values["tls"] = tls

        @builtins.property
        def sasl(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.SaslProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.ClientAuthenticationProperty.Sasl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-clientauthentication.html#cfn-msk-cluster-clientauthentication-sasl
            '''
            result = self._values.get("sasl")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.SaslProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def tls(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.TlsProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.ClientAuthenticationProperty.Tls``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-clientauthentication.html#cfn-msk-cluster-clientauthentication-tls
            '''
            result = self._values.get("tls")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.TlsProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ClientAuthenticationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.CloudWatchLogsProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled", "log_group": "logGroup"},
    )
    class CloudWatchLogsProperty:
        def __init__(
            self,
            *,
            enabled: typing.Union[builtins.bool, _IResolvable_da3f097b],
            log_group: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param enabled: ``CfnCluster.CloudWatchLogsProperty.Enabled``.
            :param log_group: ``CfnCluster.CloudWatchLogsProperty.LogGroup``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-cloudwatchlogs.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "enabled": enabled,
            }
            if log_group is not None:
                self._values["log_group"] = log_group

        @builtins.property
        def enabled(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCluster.CloudWatchLogsProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-cloudwatchlogs.html#cfn-msk-cluster-cloudwatchlogs-enabled
            '''
            result = self._values.get("enabled")
            assert result is not None, "Required property 'enabled' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        @builtins.property
        def log_group(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.CloudWatchLogsProperty.LogGroup``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-cloudwatchlogs.html#cfn-msk-cluster-cloudwatchlogs-loggroup
            '''
            result = self._values.get("log_group")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CloudWatchLogsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.ConfigurationInfoProperty",
        jsii_struct_bases=[],
        name_mapping={"arn": "arn", "revision": "revision"},
    )
    class ConfigurationInfoProperty:
        def __init__(self, *, arn: builtins.str, revision: jsii.Number) -> None:
            '''
            :param arn: ``CfnCluster.ConfigurationInfoProperty.Arn``.
            :param revision: ``CfnCluster.ConfigurationInfoProperty.Revision``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-configurationinfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "arn": arn,
                "revision": revision,
            }

        @builtins.property
        def arn(self) -> builtins.str:
            '''``CfnCluster.ConfigurationInfoProperty.Arn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-configurationinfo.html#cfn-msk-cluster-configurationinfo-arn
            '''
            result = self._values.get("arn")
            assert result is not None, "Required property 'arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def revision(self) -> jsii.Number:
            '''``CfnCluster.ConfigurationInfoProperty.Revision``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-configurationinfo.html#cfn-msk-cluster-configurationinfo-revision
            '''
            result = self._values.get("revision")
            assert result is not None, "Required property 'revision' is missing"
            return typing.cast(jsii.Number, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConfigurationInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.EBSStorageInfoProperty",
        jsii_struct_bases=[],
        name_mapping={"volume_size": "volumeSize"},
    )
    class EBSStorageInfoProperty:
        def __init__(self, *, volume_size: typing.Optional[jsii.Number] = None) -> None:
            '''
            :param volume_size: ``CfnCluster.EBSStorageInfoProperty.VolumeSize``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-ebsstorageinfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if volume_size is not None:
                self._values["volume_size"] = volume_size

        @builtins.property
        def volume_size(self) -> typing.Optional[jsii.Number]:
            '''``CfnCluster.EBSStorageInfoProperty.VolumeSize``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-ebsstorageinfo.html#cfn-msk-cluster-ebsstorageinfo-volumesize
            '''
            result = self._values.get("volume_size")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EBSStorageInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.EncryptionAtRestProperty",
        jsii_struct_bases=[],
        name_mapping={"data_volume_kms_key_id": "dataVolumeKmsKeyId"},
    )
    class EncryptionAtRestProperty:
        def __init__(self, *, data_volume_kms_key_id: builtins.str) -> None:
            '''
            :param data_volume_kms_key_id: ``CfnCluster.EncryptionAtRestProperty.DataVolumeKMSKeyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionatrest.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "data_volume_kms_key_id": data_volume_kms_key_id,
            }

        @builtins.property
        def data_volume_kms_key_id(self) -> builtins.str:
            '''``CfnCluster.EncryptionAtRestProperty.DataVolumeKMSKeyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionatrest.html#cfn-msk-cluster-encryptionatrest-datavolumekmskeyid
            '''
            result = self._values.get("data_volume_kms_key_id")
            assert result is not None, "Required property 'data_volume_kms_key_id' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EncryptionAtRestProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.EncryptionInTransitProperty",
        jsii_struct_bases=[],
        name_mapping={"client_broker": "clientBroker", "in_cluster": "inCluster"},
    )
    class EncryptionInTransitProperty:
        def __init__(
            self,
            *,
            client_broker: typing.Optional[builtins.str] = None,
            in_cluster: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param client_broker: ``CfnCluster.EncryptionInTransitProperty.ClientBroker``.
            :param in_cluster: ``CfnCluster.EncryptionInTransitProperty.InCluster``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionintransit.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if client_broker is not None:
                self._values["client_broker"] = client_broker
            if in_cluster is not None:
                self._values["in_cluster"] = in_cluster

        @builtins.property
        def client_broker(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.EncryptionInTransitProperty.ClientBroker``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionintransit.html#cfn-msk-cluster-encryptionintransit-clientbroker
            '''
            result = self._values.get("client_broker")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def in_cluster(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnCluster.EncryptionInTransitProperty.InCluster``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionintransit.html#cfn-msk-cluster-encryptionintransit-incluster
            '''
            result = self._values.get("in_cluster")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EncryptionInTransitProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.EncryptionInfoProperty",
        jsii_struct_bases=[],
        name_mapping={
            "encryption_at_rest": "encryptionAtRest",
            "encryption_in_transit": "encryptionInTransit",
        },
    )
    class EncryptionInfoProperty:
        def __init__(
            self,
            *,
            encryption_at_rest: typing.Optional[typing.Union["CfnCluster.EncryptionAtRestProperty", _IResolvable_da3f097b]] = None,
            encryption_in_transit: typing.Optional[typing.Union["CfnCluster.EncryptionInTransitProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param encryption_at_rest: ``CfnCluster.EncryptionInfoProperty.EncryptionAtRest``.
            :param encryption_in_transit: ``CfnCluster.EncryptionInfoProperty.EncryptionInTransit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptioninfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if encryption_at_rest is not None:
                self._values["encryption_at_rest"] = encryption_at_rest
            if encryption_in_transit is not None:
                self._values["encryption_in_transit"] = encryption_in_transit

        @builtins.property
        def encryption_at_rest(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.EncryptionAtRestProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.EncryptionInfoProperty.EncryptionAtRest``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptioninfo.html#cfn-msk-cluster-encryptioninfo-encryptionatrest
            '''
            result = self._values.get("encryption_at_rest")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.EncryptionAtRestProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def encryption_in_transit(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.EncryptionInTransitProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.EncryptionInfoProperty.EncryptionInTransit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptioninfo.html#cfn-msk-cluster-encryptioninfo-encryptionintransit
            '''
            result = self._values.get("encryption_in_transit")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.EncryptionInTransitProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EncryptionInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.FirehoseProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled", "delivery_stream": "deliveryStream"},
    )
    class FirehoseProperty:
        def __init__(
            self,
            *,
            enabled: typing.Union[builtins.bool, _IResolvable_da3f097b],
            delivery_stream: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param enabled: ``CfnCluster.FirehoseProperty.Enabled``.
            :param delivery_stream: ``CfnCluster.FirehoseProperty.DeliveryStream``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-firehose.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "enabled": enabled,
            }
            if delivery_stream is not None:
                self._values["delivery_stream"] = delivery_stream

        @builtins.property
        def enabled(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCluster.FirehoseProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-firehose.html#cfn-msk-cluster-firehose-enabled
            '''
            result = self._values.get("enabled")
            assert result is not None, "Required property 'enabled' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        @builtins.property
        def delivery_stream(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.FirehoseProperty.DeliveryStream``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-firehose.html#cfn-msk-cluster-firehose-deliverystream
            '''
            result = self._values.get("delivery_stream")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FirehoseProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.IamProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled"},
    )
    class IamProperty:
        def __init__(
            self,
            *,
            enabled: typing.Union[builtins.bool, _IResolvable_da3f097b],
        ) -> None:
            '''
            :param enabled: ``CfnCluster.IamProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-iam.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "enabled": enabled,
            }

        @builtins.property
        def enabled(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCluster.IamProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-iam.html#cfn-msk-cluster-iam-enabled
            '''
            result = self._values.get("enabled")
            assert result is not None, "Required property 'enabled' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IamProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.JmxExporterProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled_in_broker": "enabledInBroker"},
    )
    class JmxExporterProperty:
        def __init__(
            self,
            *,
            enabled_in_broker: typing.Union[builtins.bool, _IResolvable_da3f097b],
        ) -> None:
            '''
            :param enabled_in_broker: ``CfnCluster.JmxExporterProperty.EnabledInBroker``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-jmxexporter.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "enabled_in_broker": enabled_in_broker,
            }

        @builtins.property
        def enabled_in_broker(
            self,
        ) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCluster.JmxExporterProperty.EnabledInBroker``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-jmxexporter.html#cfn-msk-cluster-jmxexporter-enabledinbroker
            '''
            result = self._values.get("enabled_in_broker")
            assert result is not None, "Required property 'enabled_in_broker' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "JmxExporterProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.LoggingInfoProperty",
        jsii_struct_bases=[],
        name_mapping={"broker_logs": "brokerLogs"},
    )
    class LoggingInfoProperty:
        def __init__(
            self,
            *,
            broker_logs: typing.Union["CfnCluster.BrokerLogsProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param broker_logs: ``CfnCluster.LoggingInfoProperty.BrokerLogs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-logginginfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "broker_logs": broker_logs,
            }

        @builtins.property
        def broker_logs(
            self,
        ) -> typing.Union["CfnCluster.BrokerLogsProperty", _IResolvable_da3f097b]:
            '''``CfnCluster.LoggingInfoProperty.BrokerLogs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-logginginfo.html#cfn-msk-cluster-logginginfo-brokerlogs
            '''
            result = self._values.get("broker_logs")
            assert result is not None, "Required property 'broker_logs' is missing"
            return typing.cast(typing.Union["CfnCluster.BrokerLogsProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LoggingInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.NodeExporterProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled_in_broker": "enabledInBroker"},
    )
    class NodeExporterProperty:
        def __init__(
            self,
            *,
            enabled_in_broker: typing.Union[builtins.bool, _IResolvable_da3f097b],
        ) -> None:
            '''
            :param enabled_in_broker: ``CfnCluster.NodeExporterProperty.EnabledInBroker``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-nodeexporter.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "enabled_in_broker": enabled_in_broker,
            }

        @builtins.property
        def enabled_in_broker(
            self,
        ) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCluster.NodeExporterProperty.EnabledInBroker``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-nodeexporter.html#cfn-msk-cluster-nodeexporter-enabledinbroker
            '''
            result = self._values.get("enabled_in_broker")
            assert result is not None, "Required property 'enabled_in_broker' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "NodeExporterProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.OpenMonitoringProperty",
        jsii_struct_bases=[],
        name_mapping={"prometheus": "prometheus"},
    )
    class OpenMonitoringProperty:
        def __init__(
            self,
            *,
            prometheus: typing.Union["CfnCluster.PrometheusProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param prometheus: ``CfnCluster.OpenMonitoringProperty.Prometheus``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-openmonitoring.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "prometheus": prometheus,
            }

        @builtins.property
        def prometheus(
            self,
        ) -> typing.Union["CfnCluster.PrometheusProperty", _IResolvable_da3f097b]:
            '''``CfnCluster.OpenMonitoringProperty.Prometheus``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-openmonitoring.html#cfn-msk-cluster-openmonitoring-prometheus
            '''
            result = self._values.get("prometheus")
            assert result is not None, "Required property 'prometheus' is missing"
            return typing.cast(typing.Union["CfnCluster.PrometheusProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OpenMonitoringProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.PrometheusProperty",
        jsii_struct_bases=[],
        name_mapping={"jmx_exporter": "jmxExporter", "node_exporter": "nodeExporter"},
    )
    class PrometheusProperty:
        def __init__(
            self,
            *,
            jmx_exporter: typing.Optional[typing.Union["CfnCluster.JmxExporterProperty", _IResolvable_da3f097b]] = None,
            node_exporter: typing.Optional[typing.Union["CfnCluster.NodeExporterProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param jmx_exporter: ``CfnCluster.PrometheusProperty.JmxExporter``.
            :param node_exporter: ``CfnCluster.PrometheusProperty.NodeExporter``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-prometheus.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if jmx_exporter is not None:
                self._values["jmx_exporter"] = jmx_exporter
            if node_exporter is not None:
                self._values["node_exporter"] = node_exporter

        @builtins.property
        def jmx_exporter(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.JmxExporterProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.PrometheusProperty.JmxExporter``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-prometheus.html#cfn-msk-cluster-prometheus-jmxexporter
            '''
            result = self._values.get("jmx_exporter")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.JmxExporterProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def node_exporter(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.NodeExporterProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.PrometheusProperty.NodeExporter``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-prometheus.html#cfn-msk-cluster-prometheus-nodeexporter
            '''
            result = self._values.get("node_exporter")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.NodeExporterProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PrometheusProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.S3Property",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled", "bucket": "bucket", "prefix": "prefix"},
    )
    class S3Property:
        def __init__(
            self,
            *,
            enabled: typing.Union[builtins.bool, _IResolvable_da3f097b],
            bucket: typing.Optional[builtins.str] = None,
            prefix: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param enabled: ``CfnCluster.S3Property.Enabled``.
            :param bucket: ``CfnCluster.S3Property.Bucket``.
            :param prefix: ``CfnCluster.S3Property.Prefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-s3.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "enabled": enabled,
            }
            if bucket is not None:
                self._values["bucket"] = bucket
            if prefix is not None:
                self._values["prefix"] = prefix

        @builtins.property
        def enabled(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCluster.S3Property.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-s3.html#cfn-msk-cluster-s3-enabled
            '''
            result = self._values.get("enabled")
            assert result is not None, "Required property 'enabled' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        @builtins.property
        def bucket(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.S3Property.Bucket``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-s3.html#cfn-msk-cluster-s3-bucket
            '''
            result = self._values.get("bucket")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def prefix(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.S3Property.Prefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-s3.html#cfn-msk-cluster-s3-prefix
            '''
            result = self._values.get("prefix")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3Property(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.SaslProperty",
        jsii_struct_bases=[],
        name_mapping={"iam": "iam", "scram": "scram"},
    )
    class SaslProperty:
        def __init__(
            self,
            *,
            iam: typing.Optional[typing.Union["CfnCluster.IamProperty", _IResolvable_da3f097b]] = None,
            scram: typing.Optional[typing.Union["CfnCluster.ScramProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param iam: ``CfnCluster.SaslProperty.Iam``.
            :param scram: ``CfnCluster.SaslProperty.Scram``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-sasl.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if iam is not None:
                self._values["iam"] = iam
            if scram is not None:
                self._values["scram"] = scram

        @builtins.property
        def iam(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.IamProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.SaslProperty.Iam``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-sasl.html#cfn-msk-cluster-sasl-iam
            '''
            result = self._values.get("iam")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.IamProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def scram(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.ScramProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.SaslProperty.Scram``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-sasl.html#cfn-msk-cluster-sasl-scram
            '''
            result = self._values.get("scram")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.ScramProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SaslProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.ScramProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled"},
    )
    class ScramProperty:
        def __init__(
            self,
            *,
            enabled: typing.Union[builtins.bool, _IResolvable_da3f097b],
        ) -> None:
            '''
            :param enabled: ``CfnCluster.ScramProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-scram.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "enabled": enabled,
            }

        @builtins.property
        def enabled(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCluster.ScramProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-scram.html#cfn-msk-cluster-scram-enabled
            '''
            result = self._values.get("enabled")
            assert result is not None, "Required property 'enabled' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ScramProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.StorageInfoProperty",
        jsii_struct_bases=[],
        name_mapping={"ebs_storage_info": "ebsStorageInfo"},
    )
    class StorageInfoProperty:
        def __init__(
            self,
            *,
            ebs_storage_info: typing.Optional[typing.Union["CfnCluster.EBSStorageInfoProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param ebs_storage_info: ``CfnCluster.StorageInfoProperty.EBSStorageInfo``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-storageinfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if ebs_storage_info is not None:
                self._values["ebs_storage_info"] = ebs_storage_info

        @builtins.property
        def ebs_storage_info(
            self,
        ) -> typing.Optional[typing.Union["CfnCluster.EBSStorageInfoProperty", _IResolvable_da3f097b]]:
            '''``CfnCluster.StorageInfoProperty.EBSStorageInfo``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-storageinfo.html#cfn-msk-cluster-storageinfo-ebsstorageinfo
            '''
            result = self._values.get("ebs_storage_info")
            return typing.cast(typing.Optional[typing.Union["CfnCluster.EBSStorageInfoProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StorageInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_msk.CfnCluster.TlsProperty",
        jsii_struct_bases=[],
        name_mapping={"certificate_authority_arn_list": "certificateAuthorityArnList"},
    )
    class TlsProperty:
        def __init__(
            self,
            *,
            certificate_authority_arn_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''
            :param certificate_authority_arn_list: ``CfnCluster.TlsProperty.CertificateAuthorityArnList``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-tls.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if certificate_authority_arn_list is not None:
                self._values["certificate_authority_arn_list"] = certificate_authority_arn_list

        @builtins.property
        def certificate_authority_arn_list(
            self,
        ) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnCluster.TlsProperty.CertificateAuthorityArnList``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-tls.html#cfn-msk-cluster-tls-certificateauthorityarnlist
            '''
            result = self._values.get("certificate_authority_arn_list")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TlsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_msk.CfnClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "broker_node_group_info": "brokerNodeGroupInfo",
        "cluster_name": "clusterName",
        "kafka_version": "kafkaVersion",
        "number_of_broker_nodes": "numberOfBrokerNodes",
        "client_authentication": "clientAuthentication",
        "configuration_info": "configurationInfo",
        "encryption_info": "encryptionInfo",
        "enhanced_monitoring": "enhancedMonitoring",
        "logging_info": "loggingInfo",
        "open_monitoring": "openMonitoring",
        "tags": "tags",
    },
)
class CfnClusterProps:
    def __init__(
        self,
        *,
        broker_node_group_info: typing.Union[CfnCluster.BrokerNodeGroupInfoProperty, _IResolvable_da3f097b],
        cluster_name: builtins.str,
        kafka_version: builtins.str,
        number_of_broker_nodes: jsii.Number,
        client_authentication: typing.Optional[typing.Union[CfnCluster.ClientAuthenticationProperty, _IResolvable_da3f097b]] = None,
        configuration_info: typing.Optional[typing.Union[CfnCluster.ConfigurationInfoProperty, _IResolvable_da3f097b]] = None,
        encryption_info: typing.Optional[typing.Union[CfnCluster.EncryptionInfoProperty, _IResolvable_da3f097b]] = None,
        enhanced_monitoring: typing.Optional[builtins.str] = None,
        logging_info: typing.Optional[typing.Union[CfnCluster.LoggingInfoProperty, _IResolvable_da3f097b]] = None,
        open_monitoring: typing.Optional[typing.Union[CfnCluster.OpenMonitoringProperty, _IResolvable_da3f097b]] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::MSK::Cluster``.

        :param broker_node_group_info: ``AWS::MSK::Cluster.BrokerNodeGroupInfo``.
        :param cluster_name: ``AWS::MSK::Cluster.ClusterName``.
        :param kafka_version: ``AWS::MSK::Cluster.KafkaVersion``.
        :param number_of_broker_nodes: ``AWS::MSK::Cluster.NumberOfBrokerNodes``.
        :param client_authentication: ``AWS::MSK::Cluster.ClientAuthentication``.
        :param configuration_info: ``AWS::MSK::Cluster.ConfigurationInfo``.
        :param encryption_info: ``AWS::MSK::Cluster.EncryptionInfo``.
        :param enhanced_monitoring: ``AWS::MSK::Cluster.EnhancedMonitoring``.
        :param logging_info: ``AWS::MSK::Cluster.LoggingInfo``.
        :param open_monitoring: ``AWS::MSK::Cluster.OpenMonitoring``.
        :param tags: ``AWS::MSK::Cluster.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "broker_node_group_info": broker_node_group_info,
            "cluster_name": cluster_name,
            "kafka_version": kafka_version,
            "number_of_broker_nodes": number_of_broker_nodes,
        }
        if client_authentication is not None:
            self._values["client_authentication"] = client_authentication
        if configuration_info is not None:
            self._values["configuration_info"] = configuration_info
        if encryption_info is not None:
            self._values["encryption_info"] = encryption_info
        if enhanced_monitoring is not None:
            self._values["enhanced_monitoring"] = enhanced_monitoring
        if logging_info is not None:
            self._values["logging_info"] = logging_info
        if open_monitoring is not None:
            self._values["open_monitoring"] = open_monitoring
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def broker_node_group_info(
        self,
    ) -> typing.Union[CfnCluster.BrokerNodeGroupInfoProperty, _IResolvable_da3f097b]:
        '''``AWS::MSK::Cluster.BrokerNodeGroupInfo``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-brokernodegroupinfo
        '''
        result = self._values.get("broker_node_group_info")
        assert result is not None, "Required property 'broker_node_group_info' is missing"
        return typing.cast(typing.Union[CfnCluster.BrokerNodeGroupInfoProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''``AWS::MSK::Cluster.ClusterName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-clustername
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kafka_version(self) -> builtins.str:
        '''``AWS::MSK::Cluster.KafkaVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-kafkaversion
        '''
        result = self._values.get("kafka_version")
        assert result is not None, "Required property 'kafka_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_broker_nodes(self) -> jsii.Number:
        '''``AWS::MSK::Cluster.NumberOfBrokerNodes``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-numberofbrokernodes
        '''
        result = self._values.get("number_of_broker_nodes")
        assert result is not None, "Required property 'number_of_broker_nodes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def client_authentication(
        self,
    ) -> typing.Optional[typing.Union[CfnCluster.ClientAuthenticationProperty, _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.ClientAuthentication``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-clientauthentication
        '''
        result = self._values.get("client_authentication")
        return typing.cast(typing.Optional[typing.Union[CfnCluster.ClientAuthenticationProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def configuration_info(
        self,
    ) -> typing.Optional[typing.Union[CfnCluster.ConfigurationInfoProperty, _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.ConfigurationInfo``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-configurationinfo
        '''
        result = self._values.get("configuration_info")
        return typing.cast(typing.Optional[typing.Union[CfnCluster.ConfigurationInfoProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def encryption_info(
        self,
    ) -> typing.Optional[typing.Union[CfnCluster.EncryptionInfoProperty, _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.EncryptionInfo``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-encryptioninfo
        '''
        result = self._values.get("encryption_info")
        return typing.cast(typing.Optional[typing.Union[CfnCluster.EncryptionInfoProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def enhanced_monitoring(self) -> typing.Optional[builtins.str]:
        '''``AWS::MSK::Cluster.EnhancedMonitoring``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-enhancedmonitoring
        '''
        result = self._values.get("enhanced_monitoring")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_info(
        self,
    ) -> typing.Optional[typing.Union[CfnCluster.LoggingInfoProperty, _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.LoggingInfo``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-logginginfo
        '''
        result = self._values.get("logging_info")
        return typing.cast(typing.Optional[typing.Union[CfnCluster.LoggingInfoProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def open_monitoring(
        self,
    ) -> typing.Optional[typing.Union[CfnCluster.OpenMonitoringProperty, _IResolvable_da3f097b]]:
        '''``AWS::MSK::Cluster.OpenMonitoring``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-openmonitoring
        '''
        result = self._values.get("open_monitoring")
        return typing.cast(typing.Optional[typing.Union[CfnCluster.OpenMonitoringProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::MSK::Cluster.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnCluster",
    "CfnClusterProps",
]

publication.publish()
