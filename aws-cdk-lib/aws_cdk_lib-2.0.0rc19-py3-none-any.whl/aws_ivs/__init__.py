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
class CfnChannel(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_ivs.CfnChannel",
):
    '''A CloudFormation ``AWS::IVS::Channel``.

    :cloudformationResource: AWS::IVS::Channel
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        authorized: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        latency_mode: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        recording_configuration_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::IVS::Channel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param authorized: ``AWS::IVS::Channel.Authorized``.
        :param latency_mode: ``AWS::IVS::Channel.LatencyMode``.
        :param name: ``AWS::IVS::Channel.Name``.
        :param recording_configuration_arn: ``AWS::IVS::Channel.RecordingConfigurationArn``.
        :param tags: ``AWS::IVS::Channel.Tags``.
        :param type: ``AWS::IVS::Channel.Type``.
        '''
        props = CfnChannelProps(
            authorized=authorized,
            latency_mode=latency_mode,
            name=name,
            recording_configuration_arn=recording_configuration_arn,
            tags=tags,
            type=type,
        )

        jsii.create(CfnChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrIngestEndpoint")
    def attr_ingest_endpoint(self) -> builtins.str:
        '''
        :cloudformationAttribute: IngestEndpoint
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrIngestEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrPlaybackUrl")
    def attr_playback_url(self) -> builtins.str:
        '''
        :cloudformationAttribute: PlaybackUrl
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrPlaybackUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IVS::Channel.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorized")
    def authorized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::IVS::Channel.Authorized``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-authorized
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "authorized"))

    @authorized.setter
    def authorized(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "authorized", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latencyMode")
    def latency_mode(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::Channel.LatencyMode``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-latencymode
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "latencyMode"))

    @latency_mode.setter
    def latency_mode(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "latencyMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::Channel.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recordingConfigurationArn")
    def recording_configuration_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::Channel.RecordingConfigurationArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-recordingconfigurationarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recordingConfigurationArn"))

    @recording_configuration_arn.setter
    def recording_configuration_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "recordingConfigurationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::Channel.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-type
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "type"))

    @type.setter
    def type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_ivs.CfnChannelProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorized": "authorized",
        "latency_mode": "latencyMode",
        "name": "name",
        "recording_configuration_arn": "recordingConfigurationArn",
        "tags": "tags",
        "type": "type",
    },
)
class CfnChannelProps:
    def __init__(
        self,
        *,
        authorized: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        latency_mode: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        recording_configuration_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IVS::Channel``.

        :param authorized: ``AWS::IVS::Channel.Authorized``.
        :param latency_mode: ``AWS::IVS::Channel.LatencyMode``.
        :param name: ``AWS::IVS::Channel.Name``.
        :param recording_configuration_arn: ``AWS::IVS::Channel.RecordingConfigurationArn``.
        :param tags: ``AWS::IVS::Channel.Tags``.
        :param type: ``AWS::IVS::Channel.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authorized is not None:
            self._values["authorized"] = authorized
        if latency_mode is not None:
            self._values["latency_mode"] = latency_mode
        if name is not None:
            self._values["name"] = name
        if recording_configuration_arn is not None:
            self._values["recording_configuration_arn"] = recording_configuration_arn
        if tags is not None:
            self._values["tags"] = tags
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def authorized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::IVS::Channel.Authorized``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-authorized
        '''
        result = self._values.get("authorized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def latency_mode(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::Channel.LatencyMode``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-latencymode
        '''
        result = self._values.get("latency_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::Channel.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recording_configuration_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::Channel.RecordingConfigurationArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-recordingconfigurationarn
        '''
        result = self._values.get("recording_configuration_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IVS::Channel.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::Channel.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnChannelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnPlaybackKeyPair(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_ivs.CfnPlaybackKeyPair",
):
    '''A CloudFormation ``AWS::IVS::PlaybackKeyPair``.

    :cloudformationResource: AWS::IVS::PlaybackKeyPair
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        public_key_material: builtins.str,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::IVS::PlaybackKeyPair``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param public_key_material: ``AWS::IVS::PlaybackKeyPair.PublicKeyMaterial``.
        :param name: ``AWS::IVS::PlaybackKeyPair.Name``.
        :param tags: ``AWS::IVS::PlaybackKeyPair.Tags``.
        '''
        props = CfnPlaybackKeyPairProps(
            public_key_material=public_key_material, name=name, tags=tags
        )

        jsii.create(CfnPlaybackKeyPair, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrFingerprint")
    def attr_fingerprint(self) -> builtins.str:
        '''
        :cloudformationAttribute: Fingerprint
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrFingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IVS::PlaybackKeyPair.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyMaterial")
    def public_key_material(self) -> builtins.str:
        '''``AWS::IVS::PlaybackKeyPair.PublicKeyMaterial``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-publickeymaterial
        '''
        return typing.cast(builtins.str, jsii.get(self, "publicKeyMaterial"))

    @public_key_material.setter
    def public_key_material(self, value: builtins.str) -> None:
        jsii.set(self, "publicKeyMaterial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::PlaybackKeyPair.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_ivs.CfnPlaybackKeyPairProps",
    jsii_struct_bases=[],
    name_mapping={
        "public_key_material": "publicKeyMaterial",
        "name": "name",
        "tags": "tags",
    },
)
class CfnPlaybackKeyPairProps:
    def __init__(
        self,
        *,
        public_key_material: builtins.str,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IVS::PlaybackKeyPair``.

        :param public_key_material: ``AWS::IVS::PlaybackKeyPair.PublicKeyMaterial``.
        :param name: ``AWS::IVS::PlaybackKeyPair.Name``.
        :param tags: ``AWS::IVS::PlaybackKeyPair.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "public_key_material": public_key_material,
        }
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def public_key_material(self) -> builtins.str:
        '''``AWS::IVS::PlaybackKeyPair.PublicKeyMaterial``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-publickeymaterial
        '''
        result = self._values.get("public_key_material")
        assert result is not None, "Required property 'public_key_material' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::PlaybackKeyPair.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IVS::PlaybackKeyPair.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPlaybackKeyPairProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnRecordingConfiguration(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_ivs.CfnRecordingConfiguration",
):
    '''A CloudFormation ``AWS::IVS::RecordingConfiguration``.

    :cloudformationResource: AWS::IVS::RecordingConfiguration
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        destination_configuration: typing.Union["CfnRecordingConfiguration.DestinationConfigurationProperty", _IResolvable_da3f097b],
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::IVS::RecordingConfiguration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param destination_configuration: ``AWS::IVS::RecordingConfiguration.DestinationConfiguration``.
        :param name: ``AWS::IVS::RecordingConfiguration.Name``.
        :param tags: ``AWS::IVS::RecordingConfiguration.Tags``.
        '''
        props = CfnRecordingConfigurationProps(
            destination_configuration=destination_configuration, name=name, tags=tags
        )

        jsii.create(CfnRecordingConfiguration, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrState")
    def attr_state(self) -> builtins.str:
        '''
        :cloudformationAttribute: State
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrState"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IVS::RecordingConfiguration.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationConfiguration")
    def destination_configuration(
        self,
    ) -> typing.Union["CfnRecordingConfiguration.DestinationConfigurationProperty", _IResolvable_da3f097b]:
        '''``AWS::IVS::RecordingConfiguration.DestinationConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-destinationconfiguration
        '''
        return typing.cast(typing.Union["CfnRecordingConfiguration.DestinationConfigurationProperty", _IResolvable_da3f097b], jsii.get(self, "destinationConfiguration"))

    @destination_configuration.setter
    def destination_configuration(
        self,
        value: typing.Union["CfnRecordingConfiguration.DestinationConfigurationProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "destinationConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::RecordingConfiguration.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_ivs.CfnRecordingConfiguration.DestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"s3": "s3"},
    )
    class DestinationConfigurationProperty:
        def __init__(
            self,
            *,
            s3: typing.Union["CfnRecordingConfiguration.S3DestinationConfigurationProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param s3: ``CfnRecordingConfiguration.DestinationConfigurationProperty.S3``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-destinationconfiguration.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "s3": s3,
            }

        @builtins.property
        def s3(
            self,
        ) -> typing.Union["CfnRecordingConfiguration.S3DestinationConfigurationProperty", _IResolvable_da3f097b]:
            '''``CfnRecordingConfiguration.DestinationConfigurationProperty.S3``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-destinationconfiguration.html#cfn-ivs-recordingconfiguration-destinationconfiguration-s3
            '''
            result = self._values.get("s3")
            assert result is not None, "Required property 's3' is missing"
            return typing.cast(typing.Union["CfnRecordingConfiguration.S3DestinationConfigurationProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_ivs.CfnRecordingConfiguration.S3DestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"bucket_name": "bucketName"},
    )
    class S3DestinationConfigurationProperty:
        def __init__(self, *, bucket_name: builtins.str) -> None:
            '''
            :param bucket_name: ``CfnRecordingConfiguration.S3DestinationConfigurationProperty.BucketName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-s3destinationconfiguration.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "bucket_name": bucket_name,
            }

        @builtins.property
        def bucket_name(self) -> builtins.str:
            '''``CfnRecordingConfiguration.S3DestinationConfigurationProperty.BucketName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-s3destinationconfiguration.html#cfn-ivs-recordingconfiguration-s3destinationconfiguration-bucketname
            '''
            result = self._values.get("bucket_name")
            assert result is not None, "Required property 'bucket_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3DestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_ivs.CfnRecordingConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "destination_configuration": "destinationConfiguration",
        "name": "name",
        "tags": "tags",
    },
)
class CfnRecordingConfigurationProps:
    def __init__(
        self,
        *,
        destination_configuration: typing.Union[CfnRecordingConfiguration.DestinationConfigurationProperty, _IResolvable_da3f097b],
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IVS::RecordingConfiguration``.

        :param destination_configuration: ``AWS::IVS::RecordingConfiguration.DestinationConfiguration``.
        :param name: ``AWS::IVS::RecordingConfiguration.Name``.
        :param tags: ``AWS::IVS::RecordingConfiguration.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination_configuration": destination_configuration,
        }
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def destination_configuration(
        self,
    ) -> typing.Union[CfnRecordingConfiguration.DestinationConfigurationProperty, _IResolvable_da3f097b]:
        '''``AWS::IVS::RecordingConfiguration.DestinationConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-destinationconfiguration
        '''
        result = self._values.get("destination_configuration")
        assert result is not None, "Required property 'destination_configuration' is missing"
        return typing.cast(typing.Union[CfnRecordingConfiguration.DestinationConfigurationProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IVS::RecordingConfiguration.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IVS::RecordingConfiguration.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnRecordingConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnStreamKey(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_ivs.CfnStreamKey",
):
    '''A CloudFormation ``AWS::IVS::StreamKey``.

    :cloudformationResource: AWS::IVS::StreamKey
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        channel_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::IVS::StreamKey``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param channel_arn: ``AWS::IVS::StreamKey.ChannelArn``.
        :param tags: ``AWS::IVS::StreamKey.Tags``.
        '''
        props = CfnStreamKeyProps(channel_arn=channel_arn, tags=tags)

        jsii.create(CfnStreamKey, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrValue")
    def attr_value(self) -> builtins.str:
        '''
        :cloudformationAttribute: Value
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IVS::StreamKey.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html#cfn-ivs-streamkey-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelArn")
    def channel_arn(self) -> builtins.str:
        '''``AWS::IVS::StreamKey.ChannelArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html#cfn-ivs-streamkey-channelarn
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelArn"))

    @channel_arn.setter
    def channel_arn(self, value: builtins.str) -> None:
        jsii.set(self, "channelArn", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_ivs.CfnStreamKeyProps",
    jsii_struct_bases=[],
    name_mapping={"channel_arn": "channelArn", "tags": "tags"},
)
class CfnStreamKeyProps:
    def __init__(
        self,
        *,
        channel_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IVS::StreamKey``.

        :param channel_arn: ``AWS::IVS::StreamKey.ChannelArn``.
        :param tags: ``AWS::IVS::StreamKey.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "channel_arn": channel_arn,
        }
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def channel_arn(self) -> builtins.str:
        '''``AWS::IVS::StreamKey.ChannelArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html#cfn-ivs-streamkey-channelarn
        '''
        result = self._values.get("channel_arn")
        assert result is not None, "Required property 'channel_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IVS::StreamKey.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html#cfn-ivs-streamkey-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnStreamKeyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnChannel",
    "CfnChannelProps",
    "CfnPlaybackKeyPair",
    "CfnPlaybackKeyPairProps",
    "CfnRecordingConfiguration",
    "CfnRecordingConfigurationProps",
    "CfnStreamKey",
    "CfnStreamKeyProps",
]

publication.publish()
