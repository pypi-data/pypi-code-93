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
class CfnCanary(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary",
):
    '''A CloudFormation ``AWS::Synthetics::Canary``.

    :cloudformationResource: AWS::Synthetics::Canary
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        artifact_s3_location: builtins.str,
        code: typing.Union["CfnCanary.CodeProperty", _IResolvable_da3f097b],
        execution_role_arn: builtins.str,
        name: builtins.str,
        runtime_version: builtins.str,
        schedule: typing.Union["CfnCanary.ScheduleProperty", _IResolvable_da3f097b],
        start_canary_after_creation: typing.Union[builtins.bool, _IResolvable_da3f097b],
        failure_retention_period: typing.Optional[jsii.Number] = None,
        run_config: typing.Optional[typing.Union["CfnCanary.RunConfigProperty", _IResolvable_da3f097b]] = None,
        success_retention_period: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        visual_reference: typing.Optional[typing.Union["CfnCanary.VisualReferenceProperty", _IResolvable_da3f097b]] = None,
        vpc_config: typing.Optional[typing.Union["CfnCanary.VPCConfigProperty", _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Create a new ``AWS::Synthetics::Canary``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param artifact_s3_location: ``AWS::Synthetics::Canary.ArtifactS3Location``.
        :param code: ``AWS::Synthetics::Canary.Code``.
        :param execution_role_arn: ``AWS::Synthetics::Canary.ExecutionRoleArn``.
        :param name: ``AWS::Synthetics::Canary.Name``.
        :param runtime_version: ``AWS::Synthetics::Canary.RuntimeVersion``.
        :param schedule: ``AWS::Synthetics::Canary.Schedule``.
        :param start_canary_after_creation: ``AWS::Synthetics::Canary.StartCanaryAfterCreation``.
        :param failure_retention_period: ``AWS::Synthetics::Canary.FailureRetentionPeriod``.
        :param run_config: ``AWS::Synthetics::Canary.RunConfig``.
        :param success_retention_period: ``AWS::Synthetics::Canary.SuccessRetentionPeriod``.
        :param tags: ``AWS::Synthetics::Canary.Tags``.
        :param visual_reference: ``AWS::Synthetics::Canary.VisualReference``.
        :param vpc_config: ``AWS::Synthetics::Canary.VPCConfig``.
        '''
        props = CfnCanaryProps(
            artifact_s3_location=artifact_s3_location,
            code=code,
            execution_role_arn=execution_role_arn,
            name=name,
            runtime_version=runtime_version,
            schedule=schedule,
            start_canary_after_creation=start_canary_after_creation,
            failure_retention_period=failure_retention_period,
            run_config=run_config,
            success_retention_period=success_retention_period,
            tags=tags,
            visual_reference=visual_reference,
            vpc_config=vpc_config,
        )

        jsii.create(CfnCanary, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

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
        '''``AWS::Synthetics::Canary.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactS3Location")
    def artifact_s3_location(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.ArtifactS3Location``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-artifacts3location
        '''
        return typing.cast(builtins.str, jsii.get(self, "artifactS3Location"))

    @artifact_s3_location.setter
    def artifact_s3_location(self, value: builtins.str) -> None:
        jsii.set(self, "artifactS3Location", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="code")
    def code(self) -> typing.Union["CfnCanary.CodeProperty", _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.Code``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-code
        '''
        return typing.cast(typing.Union["CfnCanary.CodeProperty", _IResolvable_da3f097b], jsii.get(self, "code"))

    @code.setter
    def code(
        self,
        value: typing.Union["CfnCanary.CodeProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "code", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.ExecutionRoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-executionrolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "executionRoleArn"))

    @execution_role_arn.setter
    def execution_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "executionRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtimeVersion")
    def runtime_version(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.RuntimeVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-runtimeversion
        '''
        return typing.cast(builtins.str, jsii.get(self, "runtimeVersion"))

    @runtime_version.setter
    def runtime_version(self, value: builtins.str) -> None:
        jsii.set(self, "runtimeVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(
        self,
    ) -> typing.Union["CfnCanary.ScheduleProperty", _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.Schedule``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-schedule
        '''
        return typing.cast(typing.Union["CfnCanary.ScheduleProperty", _IResolvable_da3f097b], jsii.get(self, "schedule"))

    @schedule.setter
    def schedule(
        self,
        value: typing.Union["CfnCanary.ScheduleProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "schedule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startCanaryAfterCreation")
    def start_canary_after_creation(
        self,
    ) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.StartCanaryAfterCreation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-startcanaryaftercreation
        '''
        return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], jsii.get(self, "startCanaryAfterCreation"))

    @start_canary_after_creation.setter
    def start_canary_after_creation(
        self,
        value: typing.Union[builtins.bool, _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "startCanaryAfterCreation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureRetentionPeriod")
    def failure_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Synthetics::Canary.FailureRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-failureretentionperiod
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "failureRetentionPeriod"))

    @failure_retention_period.setter
    def failure_retention_period(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "failureRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runConfig")
    def run_config(
        self,
    ) -> typing.Optional[typing.Union["CfnCanary.RunConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.RunConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-runconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCanary.RunConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "runConfig"))

    @run_config.setter
    def run_config(
        self,
        value: typing.Optional[typing.Union["CfnCanary.RunConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "runConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successRetentionPeriod")
    def success_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Synthetics::Canary.SuccessRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-successretentionperiod
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "successRetentionPeriod"))

    @success_retention_period.setter
    def success_retention_period(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "successRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visualReference")
    def visual_reference(
        self,
    ) -> typing.Optional[typing.Union["CfnCanary.VisualReferenceProperty", _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.VisualReference``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-visualreference
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCanary.VisualReferenceProperty", _IResolvable_da3f097b]], jsii.get(self, "visualReference"))

    @visual_reference.setter
    def visual_reference(
        self,
        value: typing.Optional[typing.Union["CfnCanary.VisualReferenceProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "visualReference", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(
        self,
    ) -> typing.Optional[typing.Union["CfnCanary.VPCConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.VPCConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-vpcconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCanary.VPCConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "vpcConfig"))

    @vpc_config.setter
    def vpc_config(
        self,
        value: typing.Optional[typing.Union["CfnCanary.VPCConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "vpcConfig", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.BaseScreenshotProperty",
        jsii_struct_bases=[],
        name_mapping={
            "screenshot_name": "screenshotName",
            "ignore_coordinates": "ignoreCoordinates",
        },
    )
    class BaseScreenshotProperty:
        def __init__(
            self,
            *,
            screenshot_name: builtins.str,
            ignore_coordinates: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''
            :param screenshot_name: ``CfnCanary.BaseScreenshotProperty.ScreenshotName``.
            :param ignore_coordinates: ``CfnCanary.BaseScreenshotProperty.IgnoreCoordinates``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-basescreenshot.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "screenshot_name": screenshot_name,
            }
            if ignore_coordinates is not None:
                self._values["ignore_coordinates"] = ignore_coordinates

        @builtins.property
        def screenshot_name(self) -> builtins.str:
            '''``CfnCanary.BaseScreenshotProperty.ScreenshotName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-basescreenshot.html#cfn-synthetics-canary-basescreenshot-screenshotname
            '''
            result = self._values.get("screenshot_name")
            assert result is not None, "Required property 'screenshot_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def ignore_coordinates(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnCanary.BaseScreenshotProperty.IgnoreCoordinates``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-basescreenshot.html#cfn-synthetics-canary-basescreenshot-ignorecoordinates
            '''
            result = self._values.get("ignore_coordinates")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BaseScreenshotProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.CodeProperty",
        jsii_struct_bases=[],
        name_mapping={
            "handler": "handler",
            "s3_bucket": "s3Bucket",
            "s3_key": "s3Key",
            "s3_object_version": "s3ObjectVersion",
            "script": "script",
        },
    )
    class CodeProperty:
        def __init__(
            self,
            *,
            handler: builtins.str,
            s3_bucket: typing.Optional[builtins.str] = None,
            s3_key: typing.Optional[builtins.str] = None,
            s3_object_version: typing.Optional[builtins.str] = None,
            script: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param handler: ``CfnCanary.CodeProperty.Handler``.
            :param s3_bucket: ``CfnCanary.CodeProperty.S3Bucket``.
            :param s3_key: ``CfnCanary.CodeProperty.S3Key``.
            :param s3_object_version: ``CfnCanary.CodeProperty.S3ObjectVersion``.
            :param script: ``CfnCanary.CodeProperty.Script``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "handler": handler,
            }
            if s3_bucket is not None:
                self._values["s3_bucket"] = s3_bucket
            if s3_key is not None:
                self._values["s3_key"] = s3_key
            if s3_object_version is not None:
                self._values["s3_object_version"] = s3_object_version
            if script is not None:
                self._values["script"] = script

        @builtins.property
        def handler(self) -> builtins.str:
            '''``CfnCanary.CodeProperty.Handler``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-handler
            '''
            result = self._values.get("handler")
            assert result is not None, "Required property 'handler' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def s3_bucket(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.CodeProperty.S3Bucket``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-s3bucket
            '''
            result = self._values.get("s3_bucket")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def s3_key(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.CodeProperty.S3Key``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-s3key
            '''
            result = self._values.get("s3_key")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def s3_object_version(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.CodeProperty.S3ObjectVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-s3objectversion
            '''
            result = self._values.get("s3_object_version")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def script(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.CodeProperty.Script``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-script
            '''
            result = self._values.get("script")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CodeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.RunConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "active_tracing": "activeTracing",
            "environment_variables": "environmentVariables",
            "memory_in_mb": "memoryInMb",
            "timeout_in_seconds": "timeoutInSeconds",
        },
    )
    class RunConfigProperty:
        def __init__(
            self,
            *,
            active_tracing: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            environment_variables: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]] = None,
            memory_in_mb: typing.Optional[jsii.Number] = None,
            timeout_in_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param active_tracing: ``CfnCanary.RunConfigProperty.ActiveTracing``.
            :param environment_variables: ``CfnCanary.RunConfigProperty.EnvironmentVariables``.
            :param memory_in_mb: ``CfnCanary.RunConfigProperty.MemoryInMB``.
            :param timeout_in_seconds: ``CfnCanary.RunConfigProperty.TimeoutInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if active_tracing is not None:
                self._values["active_tracing"] = active_tracing
            if environment_variables is not None:
                self._values["environment_variables"] = environment_variables
            if memory_in_mb is not None:
                self._values["memory_in_mb"] = memory_in_mb
            if timeout_in_seconds is not None:
                self._values["timeout_in_seconds"] = timeout_in_seconds

        @builtins.property
        def active_tracing(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnCanary.RunConfigProperty.ActiveTracing``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html#cfn-synthetics-canary-runconfig-activetracing
            '''
            result = self._values.get("active_tracing")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def environment_variables(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]]:
            '''``CfnCanary.RunConfigProperty.EnvironmentVariables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html#cfn-synthetics-canary-runconfig-environmentvariables
            '''
            result = self._values.get("environment_variables")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]], result)

        @builtins.property
        def memory_in_mb(self) -> typing.Optional[jsii.Number]:
            '''``CfnCanary.RunConfigProperty.MemoryInMB``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html#cfn-synthetics-canary-runconfig-memoryinmb
            '''
            result = self._values.get("memory_in_mb")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''``CfnCanary.RunConfigProperty.TimeoutInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html#cfn-synthetics-canary-runconfig-timeoutinseconds
            '''
            result = self._values.get("timeout_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RunConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.ScheduleProperty",
        jsii_struct_bases=[],
        name_mapping={
            "expression": "expression",
            "duration_in_seconds": "durationInSeconds",
        },
    )
    class ScheduleProperty:
        def __init__(
            self,
            *,
            expression: builtins.str,
            duration_in_seconds: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param expression: ``CfnCanary.ScheduleProperty.Expression``.
            :param duration_in_seconds: ``CfnCanary.ScheduleProperty.DurationInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-schedule.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "expression": expression,
            }
            if duration_in_seconds is not None:
                self._values["duration_in_seconds"] = duration_in_seconds

        @builtins.property
        def expression(self) -> builtins.str:
            '''``CfnCanary.ScheduleProperty.Expression``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-schedule.html#cfn-synthetics-canary-schedule-expression
            '''
            result = self._values.get("expression")
            assert result is not None, "Required property 'expression' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def duration_in_seconds(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.ScheduleProperty.DurationInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-schedule.html#cfn-synthetics-canary-schedule-durationinseconds
            '''
            result = self._values.get("duration_in_seconds")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ScheduleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.VPCConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "security_group_ids": "securityGroupIds",
            "subnet_ids": "subnetIds",
            "vpc_id": "vpcId",
        },
    )
    class VPCConfigProperty:
        def __init__(
            self,
            *,
            security_group_ids: typing.Sequence[builtins.str],
            subnet_ids: typing.Sequence[builtins.str],
            vpc_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param security_group_ids: ``CfnCanary.VPCConfigProperty.SecurityGroupIds``.
            :param subnet_ids: ``CfnCanary.VPCConfigProperty.SubnetIds``.
            :param vpc_id: ``CfnCanary.VPCConfigProperty.VpcId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-vpcconfig.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "security_group_ids": security_group_ids,
                "subnet_ids": subnet_ids,
            }
            if vpc_id is not None:
                self._values["vpc_id"] = vpc_id

        @builtins.property
        def security_group_ids(self) -> typing.List[builtins.str]:
            '''``CfnCanary.VPCConfigProperty.SecurityGroupIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-vpcconfig.html#cfn-synthetics-canary-vpcconfig-securitygroupids
            '''
            result = self._values.get("security_group_ids")
            assert result is not None, "Required property 'security_group_ids' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def subnet_ids(self) -> typing.List[builtins.str]:
            '''``CfnCanary.VPCConfigProperty.SubnetIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-vpcconfig.html#cfn-synthetics-canary-vpcconfig-subnetids
            '''
            result = self._values.get("subnet_ids")
            assert result is not None, "Required property 'subnet_ids' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def vpc_id(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.VPCConfigProperty.VpcId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-vpcconfig.html#cfn-synthetics-canary-vpcconfig-vpcid
            '''
            result = self._values.get("vpc_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VPCConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.VisualReferenceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "base_canary_run_id": "baseCanaryRunId",
            "base_screenshots": "baseScreenshots",
        },
    )
    class VisualReferenceProperty:
        def __init__(
            self,
            *,
            base_canary_run_id: builtins.str,
            base_screenshots: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnCanary.BaseScreenshotProperty", _IResolvable_da3f097b]]]] = None,
        ) -> None:
            '''
            :param base_canary_run_id: ``CfnCanary.VisualReferenceProperty.BaseCanaryRunId``.
            :param base_screenshots: ``CfnCanary.VisualReferenceProperty.BaseScreenshots``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-visualreference.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "base_canary_run_id": base_canary_run_id,
            }
            if base_screenshots is not None:
                self._values["base_screenshots"] = base_screenshots

        @builtins.property
        def base_canary_run_id(self) -> builtins.str:
            '''``CfnCanary.VisualReferenceProperty.BaseCanaryRunId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-visualreference.html#cfn-synthetics-canary-visualreference-basecanaryrunid
            '''
            result = self._values.get("base_canary_run_id")
            assert result is not None, "Required property 'base_canary_run_id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def base_screenshots(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCanary.BaseScreenshotProperty", _IResolvable_da3f097b]]]]:
            '''``CfnCanary.VisualReferenceProperty.BaseScreenshots``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-visualreference.html#cfn-synthetics-canary-visualreference-basescreenshots
            '''
            result = self._values.get("base_screenshots")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCanary.BaseScreenshotProperty", _IResolvable_da3f097b]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VisualReferenceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_synthetics.CfnCanaryProps",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_s3_location": "artifactS3Location",
        "code": "code",
        "execution_role_arn": "executionRoleArn",
        "name": "name",
        "runtime_version": "runtimeVersion",
        "schedule": "schedule",
        "start_canary_after_creation": "startCanaryAfterCreation",
        "failure_retention_period": "failureRetentionPeriod",
        "run_config": "runConfig",
        "success_retention_period": "successRetentionPeriod",
        "tags": "tags",
        "visual_reference": "visualReference",
        "vpc_config": "vpcConfig",
    },
)
class CfnCanaryProps:
    def __init__(
        self,
        *,
        artifact_s3_location: builtins.str,
        code: typing.Union[CfnCanary.CodeProperty, _IResolvable_da3f097b],
        execution_role_arn: builtins.str,
        name: builtins.str,
        runtime_version: builtins.str,
        schedule: typing.Union[CfnCanary.ScheduleProperty, _IResolvable_da3f097b],
        start_canary_after_creation: typing.Union[builtins.bool, _IResolvable_da3f097b],
        failure_retention_period: typing.Optional[jsii.Number] = None,
        run_config: typing.Optional[typing.Union[CfnCanary.RunConfigProperty, _IResolvable_da3f097b]] = None,
        success_retention_period: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        visual_reference: typing.Optional[typing.Union[CfnCanary.VisualReferenceProperty, _IResolvable_da3f097b]] = None,
        vpc_config: typing.Optional[typing.Union[CfnCanary.VPCConfigProperty, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Synthetics::Canary``.

        :param artifact_s3_location: ``AWS::Synthetics::Canary.ArtifactS3Location``.
        :param code: ``AWS::Synthetics::Canary.Code``.
        :param execution_role_arn: ``AWS::Synthetics::Canary.ExecutionRoleArn``.
        :param name: ``AWS::Synthetics::Canary.Name``.
        :param runtime_version: ``AWS::Synthetics::Canary.RuntimeVersion``.
        :param schedule: ``AWS::Synthetics::Canary.Schedule``.
        :param start_canary_after_creation: ``AWS::Synthetics::Canary.StartCanaryAfterCreation``.
        :param failure_retention_period: ``AWS::Synthetics::Canary.FailureRetentionPeriod``.
        :param run_config: ``AWS::Synthetics::Canary.RunConfig``.
        :param success_retention_period: ``AWS::Synthetics::Canary.SuccessRetentionPeriod``.
        :param tags: ``AWS::Synthetics::Canary.Tags``.
        :param visual_reference: ``AWS::Synthetics::Canary.VisualReference``.
        :param vpc_config: ``AWS::Synthetics::Canary.VPCConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "artifact_s3_location": artifact_s3_location,
            "code": code,
            "execution_role_arn": execution_role_arn,
            "name": name,
            "runtime_version": runtime_version,
            "schedule": schedule,
            "start_canary_after_creation": start_canary_after_creation,
        }
        if failure_retention_period is not None:
            self._values["failure_retention_period"] = failure_retention_period
        if run_config is not None:
            self._values["run_config"] = run_config
        if success_retention_period is not None:
            self._values["success_retention_period"] = success_retention_period
        if tags is not None:
            self._values["tags"] = tags
        if visual_reference is not None:
            self._values["visual_reference"] = visual_reference
        if vpc_config is not None:
            self._values["vpc_config"] = vpc_config

    @builtins.property
    def artifact_s3_location(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.ArtifactS3Location``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-artifacts3location
        '''
        result = self._values.get("artifact_s3_location")
        assert result is not None, "Required property 'artifact_s3_location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code(self) -> typing.Union[CfnCanary.CodeProperty, _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.Code``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-code
        '''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(typing.Union[CfnCanary.CodeProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def execution_role_arn(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.ExecutionRoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-executionrolearn
        '''
        result = self._values.get("execution_role_arn")
        assert result is not None, "Required property 'execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runtime_version(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.RuntimeVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-runtimeversion
        '''
        result = self._values.get("runtime_version")
        assert result is not None, "Required property 'runtime_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schedule(
        self,
    ) -> typing.Union[CfnCanary.ScheduleProperty, _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.Schedule``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-schedule
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(typing.Union[CfnCanary.ScheduleProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def start_canary_after_creation(
        self,
    ) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.StartCanaryAfterCreation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-startcanaryaftercreation
        '''
        result = self._values.get("start_canary_after_creation")
        assert result is not None, "Required property 'start_canary_after_creation' is missing"
        return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

    @builtins.property
    def failure_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Synthetics::Canary.FailureRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-failureretentionperiod
        '''
        result = self._values.get("failure_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def run_config(
        self,
    ) -> typing.Optional[typing.Union[CfnCanary.RunConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.RunConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-runconfig
        '''
        result = self._values.get("run_config")
        return typing.cast(typing.Optional[typing.Union[CfnCanary.RunConfigProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def success_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Synthetics::Canary.SuccessRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-successretentionperiod
        '''
        result = self._values.get("success_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Synthetics::Canary.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def visual_reference(
        self,
    ) -> typing.Optional[typing.Union[CfnCanary.VisualReferenceProperty, _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.VisualReference``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-visualreference
        '''
        result = self._values.get("visual_reference")
        return typing.cast(typing.Optional[typing.Union[CfnCanary.VisualReferenceProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def vpc_config(
        self,
    ) -> typing.Optional[typing.Union[CfnCanary.VPCConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.VPCConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-vpcconfig
        '''
        result = self._values.get("vpc_config")
        return typing.cast(typing.Optional[typing.Union[CfnCanary.VPCConfigProperty, _IResolvable_da3f097b]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCanaryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnCanary",
    "CfnCanaryProps",
]

publication.publish()
