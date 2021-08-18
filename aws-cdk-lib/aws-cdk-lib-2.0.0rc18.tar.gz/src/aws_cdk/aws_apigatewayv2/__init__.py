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
class CfnApi(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApi",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::Api``.

    :cloudformationResource: AWS::ApiGatewayV2::Api
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_key_selection_expression: typing.Optional[builtins.str] = None,
        base_path: typing.Optional[builtins.str] = None,
        body: typing.Any = None,
        body_s3_location: typing.Optional[typing.Union["CfnApi.BodyS3LocationProperty", _IResolvable_da3f097b]] = None,
        cors_configuration: typing.Optional[typing.Union["CfnApi.CorsProperty", _IResolvable_da3f097b]] = None,
        credentials_arn: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_execute_api_endpoint: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        disable_schema_validation: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        fail_on_warnings: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        name: typing.Optional[builtins.str] = None,
        protocol_type: typing.Optional[builtins.str] = None,
        route_key: typing.Optional[builtins.str] = None,
        route_selection_expression: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
        target: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::Api``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_key_selection_expression: ``AWS::ApiGatewayV2::Api.ApiKeySelectionExpression``.
        :param base_path: ``AWS::ApiGatewayV2::Api.BasePath``.
        :param body: ``AWS::ApiGatewayV2::Api.Body``.
        :param body_s3_location: ``AWS::ApiGatewayV2::Api.BodyS3Location``.
        :param cors_configuration: ``AWS::ApiGatewayV2::Api.CorsConfiguration``.
        :param credentials_arn: ``AWS::ApiGatewayV2::Api.CredentialsArn``.
        :param description: ``AWS::ApiGatewayV2::Api.Description``.
        :param disable_execute_api_endpoint: ``AWS::ApiGatewayV2::Api.DisableExecuteApiEndpoint``.
        :param disable_schema_validation: ``AWS::ApiGatewayV2::Api.DisableSchemaValidation``.
        :param fail_on_warnings: ``AWS::ApiGatewayV2::Api.FailOnWarnings``.
        :param name: ``AWS::ApiGatewayV2::Api.Name``.
        :param protocol_type: ``AWS::ApiGatewayV2::Api.ProtocolType``.
        :param route_key: ``AWS::ApiGatewayV2::Api.RouteKey``.
        :param route_selection_expression: ``AWS::ApiGatewayV2::Api.RouteSelectionExpression``.
        :param tags: ``AWS::ApiGatewayV2::Api.Tags``.
        :param target: ``AWS::ApiGatewayV2::Api.Target``.
        :param version: ``AWS::ApiGatewayV2::Api.Version``.
        '''
        props = CfnApiProps(
            api_key_selection_expression=api_key_selection_expression,
            base_path=base_path,
            body=body,
            body_s3_location=body_s3_location,
            cors_configuration=cors_configuration,
            credentials_arn=credentials_arn,
            description=description,
            disable_execute_api_endpoint=disable_execute_api_endpoint,
            disable_schema_validation=disable_schema_validation,
            fail_on_warnings=fail_on_warnings,
            name=name,
            protocol_type=protocol_type,
            route_key=route_key,
            route_selection_expression=route_selection_expression,
            tags=tags,
            target=target,
            version=version,
        )

        jsii.create(CfnApi, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrApiEndpoint")
    def attr_api_endpoint(self) -> builtins.str:
        '''
        :cloudformationAttribute: ApiEndpoint
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrApiEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::ApiGatewayV2::Api.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Api.Body``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-body
        '''
        return typing.cast(typing.Any, jsii.get(self, "body"))

    @body.setter
    def body(self, value: typing.Any) -> None:
        jsii.set(self, "body", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKeySelectionExpression")
    def api_key_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.ApiKeySelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-apikeyselectionexpression
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeySelectionExpression"))

    @api_key_selection_expression.setter
    def api_key_selection_expression(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "apiKeySelectionExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basePath")
    def base_path(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.BasePath``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-basepath
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "basePath"))

    @base_path.setter
    def base_path(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "basePath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodyS3Location")
    def body_s3_location(
        self,
    ) -> typing.Optional[typing.Union["CfnApi.BodyS3LocationProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.BodyS3Location``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-bodys3location
        '''
        return typing.cast(typing.Optional[typing.Union["CfnApi.BodyS3LocationProperty", _IResolvable_da3f097b]], jsii.get(self, "bodyS3Location"))

    @body_s3_location.setter
    def body_s3_location(
        self,
        value: typing.Optional[typing.Union["CfnApi.BodyS3LocationProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "bodyS3Location", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="corsConfiguration")
    def cors_configuration(
        self,
    ) -> typing.Optional[typing.Union["CfnApi.CorsProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.CorsConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-corsconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnApi.CorsProperty", _IResolvable_da3f097b]], jsii.get(self, "corsConfiguration"))

    @cors_configuration.setter
    def cors_configuration(
        self,
        value: typing.Optional[typing.Union["CfnApi.CorsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "corsConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialsArn")
    def credentials_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.CredentialsArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-credentialsarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "credentialsArn"))

    @credentials_arn.setter
    def credentials_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "credentialsArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableExecuteApiEndpoint")
    def disable_execute_api_endpoint(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.DisableExecuteApiEndpoint``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-disableexecuteapiendpoint
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "disableExecuteApiEndpoint"))

    @disable_execute_api_endpoint.setter
    def disable_execute_api_endpoint(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "disableExecuteApiEndpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableSchemaValidation")
    def disable_schema_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.DisableSchemaValidation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-disableschemavalidation
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "disableSchemaValidation"))

    @disable_schema_validation.setter
    def disable_schema_validation(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "disableSchemaValidation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failOnWarnings")
    def fail_on_warnings(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.FailOnWarnings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-failonwarnings
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "failOnWarnings"))

    @fail_on_warnings.setter
    def fail_on_warnings(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "failOnWarnings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocolType")
    def protocol_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.ProtocolType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-protocoltype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolType"))

    @protocol_type.setter
    def protocol_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "protocolType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeKey")
    def route_key(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.RouteKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-routekey
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeKey"))

    @route_key.setter
    def route_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "routeKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeSelectionExpression")
    def route_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.RouteSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-routeselectionexpression
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeSelectionExpression"))

    @route_selection_expression.setter
    def route_selection_expression(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "routeSelectionExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.Target``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-target
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "target"))

    @target.setter
    def target(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.Version``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-version
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "version"))

    @version.setter
    def version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "version", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApi.BodyS3LocationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "bucket": "bucket",
            "etag": "etag",
            "key": "key",
            "version": "version",
        },
    )
    class BodyS3LocationProperty:
        def __init__(
            self,
            *,
            bucket: typing.Optional[builtins.str] = None,
            etag: typing.Optional[builtins.str] = None,
            key: typing.Optional[builtins.str] = None,
            version: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param bucket: ``CfnApi.BodyS3LocationProperty.Bucket``.
            :param etag: ``CfnApi.BodyS3LocationProperty.Etag``.
            :param key: ``CfnApi.BodyS3LocationProperty.Key``.
            :param version: ``CfnApi.BodyS3LocationProperty.Version``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-bodys3location.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if bucket is not None:
                self._values["bucket"] = bucket
            if etag is not None:
                self._values["etag"] = etag
            if key is not None:
                self._values["key"] = key
            if version is not None:
                self._values["version"] = version

        @builtins.property
        def bucket(self) -> typing.Optional[builtins.str]:
            '''``CfnApi.BodyS3LocationProperty.Bucket``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-bodys3location.html#cfn-apigatewayv2-api-bodys3location-bucket
            '''
            result = self._values.get("bucket")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def etag(self) -> typing.Optional[builtins.str]:
            '''``CfnApi.BodyS3LocationProperty.Etag``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-bodys3location.html#cfn-apigatewayv2-api-bodys3location-etag
            '''
            result = self._values.get("etag")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def key(self) -> typing.Optional[builtins.str]:
            '''``CfnApi.BodyS3LocationProperty.Key``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-bodys3location.html#cfn-apigatewayv2-api-bodys3location-key
            '''
            result = self._values.get("key")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def version(self) -> typing.Optional[builtins.str]:
            '''``CfnApi.BodyS3LocationProperty.Version``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-bodys3location.html#cfn-apigatewayv2-api-bodys3location-version
            '''
            result = self._values.get("version")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BodyS3LocationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApi.CorsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "allow_credentials": "allowCredentials",
            "allow_headers": "allowHeaders",
            "allow_methods": "allowMethods",
            "allow_origins": "allowOrigins",
            "expose_headers": "exposeHeaders",
            "max_age": "maxAge",
        },
    )
    class CorsProperty:
        def __init__(
            self,
            *,
            allow_credentials: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            allow_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
            allow_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
            allow_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
            expose_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
            max_age: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param allow_credentials: ``CfnApi.CorsProperty.AllowCredentials``.
            :param allow_headers: ``CfnApi.CorsProperty.AllowHeaders``.
            :param allow_methods: ``CfnApi.CorsProperty.AllowMethods``.
            :param allow_origins: ``CfnApi.CorsProperty.AllowOrigins``.
            :param expose_headers: ``CfnApi.CorsProperty.ExposeHeaders``.
            :param max_age: ``CfnApi.CorsProperty.MaxAge``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-cors.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if allow_credentials is not None:
                self._values["allow_credentials"] = allow_credentials
            if allow_headers is not None:
                self._values["allow_headers"] = allow_headers
            if allow_methods is not None:
                self._values["allow_methods"] = allow_methods
            if allow_origins is not None:
                self._values["allow_origins"] = allow_origins
            if expose_headers is not None:
                self._values["expose_headers"] = expose_headers
            if max_age is not None:
                self._values["max_age"] = max_age

        @builtins.property
        def allow_credentials(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnApi.CorsProperty.AllowCredentials``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-cors.html#cfn-apigatewayv2-api-cors-allowcredentials
            '''
            result = self._values.get("allow_credentials")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def allow_headers(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnApi.CorsProperty.AllowHeaders``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-cors.html#cfn-apigatewayv2-api-cors-allowheaders
            '''
            result = self._values.get("allow_headers")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def allow_methods(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnApi.CorsProperty.AllowMethods``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-cors.html#cfn-apigatewayv2-api-cors-allowmethods
            '''
            result = self._values.get("allow_methods")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def allow_origins(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnApi.CorsProperty.AllowOrigins``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-cors.html#cfn-apigatewayv2-api-cors-alloworigins
            '''
            result = self._values.get("allow_origins")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def expose_headers(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnApi.CorsProperty.ExposeHeaders``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-cors.html#cfn-apigatewayv2-api-cors-exposeheaders
            '''
            result = self._values.get("expose_headers")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def max_age(self) -> typing.Optional[jsii.Number]:
            '''``CfnApi.CorsProperty.MaxAge``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-api-cors.html#cfn-apigatewayv2-api-cors-maxage
            '''
            result = self._values.get("max_age")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CorsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.implements(_IInspectable_c2943556)
class CfnApiGatewayManagedOverrides(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiGatewayManagedOverrides",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides``.

    :cloudformationResource: AWS::ApiGatewayV2::ApiGatewayManagedOverrides
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        integration: typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.IntegrationOverridesProperty", _IResolvable_da3f097b]] = None,
        route: typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.RouteOverridesProperty", _IResolvable_da3f097b]] = None,
        stage: typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.StageOverridesProperty", _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.ApiId``.
        :param integration: ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Integration``.
        :param route: ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Route``.
        :param stage: ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Stage``.
        '''
        props = CfnApiGatewayManagedOverridesProps(
            api_id=api_id, integration=integration, route=route, stage=stage
        )

        jsii.create(CfnApiGatewayManagedOverrides, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integration")
    def integration(
        self,
    ) -> typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.IntegrationOverridesProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Integration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-integration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.IntegrationOverridesProperty", _IResolvable_da3f097b]], jsii.get(self, "integration"))

    @integration.setter
    def integration(
        self,
        value: typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.IntegrationOverridesProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "integration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="route")
    def route(
        self,
    ) -> typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.RouteOverridesProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Route``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-route
        '''
        return typing.cast(typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.RouteOverridesProperty", _IResolvable_da3f097b]], jsii.get(self, "route"))

    @route.setter
    def route(
        self,
        value: typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.RouteOverridesProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "route", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stage")
    def stage(
        self,
    ) -> typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.StageOverridesProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Stage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-stage
        '''
        return typing.cast(typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.StageOverridesProperty", _IResolvable_da3f097b]], jsii.get(self, "stage"))

    @stage.setter
    def stage(
        self,
        value: typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.StageOverridesProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "stage", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiGatewayManagedOverrides.AccessLogSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={"destination_arn": "destinationArn", "format": "format"},
    )
    class AccessLogSettingsProperty:
        def __init__(
            self,
            *,
            destination_arn: typing.Optional[builtins.str] = None,
            format: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param destination_arn: ``CfnApiGatewayManagedOverrides.AccessLogSettingsProperty.DestinationArn``.
            :param format: ``CfnApiGatewayManagedOverrides.AccessLogSettingsProperty.Format``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-accesslogsettings.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if destination_arn is not None:
                self._values["destination_arn"] = destination_arn
            if format is not None:
                self._values["format"] = format

        @builtins.property
        def destination_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.AccessLogSettingsProperty.DestinationArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-accesslogsettings.html#cfn-apigatewayv2-apigatewaymanagedoverrides-accesslogsettings-destinationarn
            '''
            result = self._values.get("destination_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def format(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.AccessLogSettingsProperty.Format``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-accesslogsettings.html#cfn-apigatewayv2-apigatewaymanagedoverrides-accesslogsettings-format
            '''
            result = self._values.get("format")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AccessLogSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiGatewayManagedOverrides.IntegrationOverridesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "description": "description",
            "integration_method": "integrationMethod",
            "payload_format_version": "payloadFormatVersion",
            "timeout_in_millis": "timeoutInMillis",
        },
    )
    class IntegrationOverridesProperty:
        def __init__(
            self,
            *,
            description: typing.Optional[builtins.str] = None,
            integration_method: typing.Optional[builtins.str] = None,
            payload_format_version: typing.Optional[builtins.str] = None,
            timeout_in_millis: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param description: ``CfnApiGatewayManagedOverrides.IntegrationOverridesProperty.Description``.
            :param integration_method: ``CfnApiGatewayManagedOverrides.IntegrationOverridesProperty.IntegrationMethod``.
            :param payload_format_version: ``CfnApiGatewayManagedOverrides.IntegrationOverridesProperty.PayloadFormatVersion``.
            :param timeout_in_millis: ``CfnApiGatewayManagedOverrides.IntegrationOverridesProperty.TimeoutInMillis``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-integrationoverrides.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if description is not None:
                self._values["description"] = description
            if integration_method is not None:
                self._values["integration_method"] = integration_method
            if payload_format_version is not None:
                self._values["payload_format_version"] = payload_format_version
            if timeout_in_millis is not None:
                self._values["timeout_in_millis"] = timeout_in_millis

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.IntegrationOverridesProperty.Description``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-integrationoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-integrationoverrides-description
            '''
            result = self._values.get("description")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def integration_method(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.IntegrationOverridesProperty.IntegrationMethod``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-integrationoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-integrationoverrides-integrationmethod
            '''
            result = self._values.get("integration_method")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def payload_format_version(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.IntegrationOverridesProperty.PayloadFormatVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-integrationoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-integrationoverrides-payloadformatversion
            '''
            result = self._values.get("payload_format_version")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def timeout_in_millis(self) -> typing.Optional[jsii.Number]:
            '''``CfnApiGatewayManagedOverrides.IntegrationOverridesProperty.TimeoutInMillis``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-integrationoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-integrationoverrides-timeoutinmillis
            '''
            result = self._values.get("timeout_in_millis")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IntegrationOverridesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiGatewayManagedOverrides.RouteOverridesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "authorization_scopes": "authorizationScopes",
            "authorization_type": "authorizationType",
            "authorizer_id": "authorizerId",
            "operation_name": "operationName",
            "target": "target",
        },
    )
    class RouteOverridesProperty:
        def __init__(
            self,
            *,
            authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
            authorization_type: typing.Optional[builtins.str] = None,
            authorizer_id: typing.Optional[builtins.str] = None,
            operation_name: typing.Optional[builtins.str] = None,
            target: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param authorization_scopes: ``CfnApiGatewayManagedOverrides.RouteOverridesProperty.AuthorizationScopes``.
            :param authorization_type: ``CfnApiGatewayManagedOverrides.RouteOverridesProperty.AuthorizationType``.
            :param authorizer_id: ``CfnApiGatewayManagedOverrides.RouteOverridesProperty.AuthorizerId``.
            :param operation_name: ``CfnApiGatewayManagedOverrides.RouteOverridesProperty.OperationName``.
            :param target: ``CfnApiGatewayManagedOverrides.RouteOverridesProperty.Target``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routeoverrides.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if authorization_scopes is not None:
                self._values["authorization_scopes"] = authorization_scopes
            if authorization_type is not None:
                self._values["authorization_type"] = authorization_type
            if authorizer_id is not None:
                self._values["authorizer_id"] = authorizer_id
            if operation_name is not None:
                self._values["operation_name"] = operation_name
            if target is not None:
                self._values["target"] = target

        @builtins.property
        def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnApiGatewayManagedOverrides.RouteOverridesProperty.AuthorizationScopes``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routeoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routeoverrides-authorizationscopes
            '''
            result = self._values.get("authorization_scopes")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def authorization_type(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.RouteOverridesProperty.AuthorizationType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routeoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routeoverrides-authorizationtype
            '''
            result = self._values.get("authorization_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def authorizer_id(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.RouteOverridesProperty.AuthorizerId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routeoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routeoverrides-authorizerid
            '''
            result = self._values.get("authorizer_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def operation_name(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.RouteOverridesProperty.OperationName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routeoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routeoverrides-operationname
            '''
            result = self._values.get("operation_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def target(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.RouteOverridesProperty.Target``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routeoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routeoverrides-target
            '''
            result = self._values.get("target")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RouteOverridesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiGatewayManagedOverrides.RouteSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "data_trace_enabled": "dataTraceEnabled",
            "detailed_metrics_enabled": "detailedMetricsEnabled",
            "logging_level": "loggingLevel",
            "throttling_burst_limit": "throttlingBurstLimit",
            "throttling_rate_limit": "throttlingRateLimit",
        },
    )
    class RouteSettingsProperty:
        def __init__(
            self,
            *,
            data_trace_enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            detailed_metrics_enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            logging_level: typing.Optional[builtins.str] = None,
            throttling_burst_limit: typing.Optional[jsii.Number] = None,
            throttling_rate_limit: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param data_trace_enabled: ``CfnApiGatewayManagedOverrides.RouteSettingsProperty.DataTraceEnabled``.
            :param detailed_metrics_enabled: ``CfnApiGatewayManagedOverrides.RouteSettingsProperty.DetailedMetricsEnabled``.
            :param logging_level: ``CfnApiGatewayManagedOverrides.RouteSettingsProperty.LoggingLevel``.
            :param throttling_burst_limit: ``CfnApiGatewayManagedOverrides.RouteSettingsProperty.ThrottlingBurstLimit``.
            :param throttling_rate_limit: ``CfnApiGatewayManagedOverrides.RouteSettingsProperty.ThrottlingRateLimit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routesettings.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if data_trace_enabled is not None:
                self._values["data_trace_enabled"] = data_trace_enabled
            if detailed_metrics_enabled is not None:
                self._values["detailed_metrics_enabled"] = detailed_metrics_enabled
            if logging_level is not None:
                self._values["logging_level"] = logging_level
            if throttling_burst_limit is not None:
                self._values["throttling_burst_limit"] = throttling_burst_limit
            if throttling_rate_limit is not None:
                self._values["throttling_rate_limit"] = throttling_rate_limit

        @builtins.property
        def data_trace_enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnApiGatewayManagedOverrides.RouteSettingsProperty.DataTraceEnabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routesettings.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routesettings-datatraceenabled
            '''
            result = self._values.get("data_trace_enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def detailed_metrics_enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnApiGatewayManagedOverrides.RouteSettingsProperty.DetailedMetricsEnabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routesettings.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routesettings-detailedmetricsenabled
            '''
            result = self._values.get("detailed_metrics_enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def logging_level(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.RouteSettingsProperty.LoggingLevel``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routesettings.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routesettings-logginglevel
            '''
            result = self._values.get("logging_level")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def throttling_burst_limit(self) -> typing.Optional[jsii.Number]:
            '''``CfnApiGatewayManagedOverrides.RouteSettingsProperty.ThrottlingBurstLimit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routesettings.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routesettings-throttlingburstlimit
            '''
            result = self._values.get("throttling_burst_limit")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def throttling_rate_limit(self) -> typing.Optional[jsii.Number]:
            '''``CfnApiGatewayManagedOverrides.RouteSettingsProperty.ThrottlingRateLimit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-routesettings.html#cfn-apigatewayv2-apigatewaymanagedoverrides-routesettings-throttlingratelimit
            '''
            result = self._values.get("throttling_rate_limit")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RouteSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiGatewayManagedOverrides.StageOverridesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "access_log_settings": "accessLogSettings",
            "auto_deploy": "autoDeploy",
            "default_route_settings": "defaultRouteSettings",
            "description": "description",
            "route_settings": "routeSettings",
            "stage_variables": "stageVariables",
        },
    )
    class StageOverridesProperty:
        def __init__(
            self,
            *,
            access_log_settings: typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.AccessLogSettingsProperty", _IResolvable_da3f097b]] = None,
            auto_deploy: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            default_route_settings: typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.RouteSettingsProperty", _IResolvable_da3f097b]] = None,
            description: typing.Optional[builtins.str] = None,
            route_settings: typing.Any = None,
            stage_variables: typing.Any = None,
        ) -> None:
            '''
            :param access_log_settings: ``CfnApiGatewayManagedOverrides.StageOverridesProperty.AccessLogSettings``.
            :param auto_deploy: ``CfnApiGatewayManagedOverrides.StageOverridesProperty.AutoDeploy``.
            :param default_route_settings: ``CfnApiGatewayManagedOverrides.StageOverridesProperty.DefaultRouteSettings``.
            :param description: ``CfnApiGatewayManagedOverrides.StageOverridesProperty.Description``.
            :param route_settings: ``CfnApiGatewayManagedOverrides.StageOverridesProperty.RouteSettings``.
            :param stage_variables: ``CfnApiGatewayManagedOverrides.StageOverridesProperty.StageVariables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-stageoverrides.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if access_log_settings is not None:
                self._values["access_log_settings"] = access_log_settings
            if auto_deploy is not None:
                self._values["auto_deploy"] = auto_deploy
            if default_route_settings is not None:
                self._values["default_route_settings"] = default_route_settings
            if description is not None:
                self._values["description"] = description
            if route_settings is not None:
                self._values["route_settings"] = route_settings
            if stage_variables is not None:
                self._values["stage_variables"] = stage_variables

        @builtins.property
        def access_log_settings(
            self,
        ) -> typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.AccessLogSettingsProperty", _IResolvable_da3f097b]]:
            '''``CfnApiGatewayManagedOverrides.StageOverridesProperty.AccessLogSettings``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-stageoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-stageoverrides-accesslogsettings
            '''
            result = self._values.get("access_log_settings")
            return typing.cast(typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.AccessLogSettingsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def auto_deploy(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnApiGatewayManagedOverrides.StageOverridesProperty.AutoDeploy``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-stageoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-stageoverrides-autodeploy
            '''
            result = self._values.get("auto_deploy")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def default_route_settings(
            self,
        ) -> typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.RouteSettingsProperty", _IResolvable_da3f097b]]:
            '''``CfnApiGatewayManagedOverrides.StageOverridesProperty.DefaultRouteSettings``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-stageoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-stageoverrides-defaultroutesettings
            '''
            result = self._values.get("default_route_settings")
            return typing.cast(typing.Optional[typing.Union["CfnApiGatewayManagedOverrides.RouteSettingsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            '''``CfnApiGatewayManagedOverrides.StageOverridesProperty.Description``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-stageoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-stageoverrides-description
            '''
            result = self._values.get("description")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def route_settings(self) -> typing.Any:
            '''``CfnApiGatewayManagedOverrides.StageOverridesProperty.RouteSettings``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-stageoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-stageoverrides-routesettings
            '''
            result = self._values.get("route_settings")
            return typing.cast(typing.Any, result)

        @builtins.property
        def stage_variables(self) -> typing.Any:
            '''``CfnApiGatewayManagedOverrides.StageOverridesProperty.StageVariables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-apigatewaymanagedoverrides-stageoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-stageoverrides-stagevariables
            '''
            result = self._values.get("stage_variables")
            return typing.cast(typing.Any, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StageOverridesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiGatewayManagedOverridesProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "integration": "integration",
        "route": "route",
        "stage": "stage",
    },
)
class CfnApiGatewayManagedOverridesProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        integration: typing.Optional[typing.Union[CfnApiGatewayManagedOverrides.IntegrationOverridesProperty, _IResolvable_da3f097b]] = None,
        route: typing.Optional[typing.Union[CfnApiGatewayManagedOverrides.RouteOverridesProperty, _IResolvable_da3f097b]] = None,
        stage: typing.Optional[typing.Union[CfnApiGatewayManagedOverrides.StageOverridesProperty, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides``.

        :param api_id: ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.ApiId``.
        :param integration: ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Integration``.
        :param route: ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Route``.
        :param stage: ``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Stage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
        }
        if integration is not None:
            self._values["integration"] = integration
        if route is not None:
            self._values["route"] = route
        if stage is not None:
            self._values["stage"] = stage

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def integration(
        self,
    ) -> typing.Optional[typing.Union[CfnApiGatewayManagedOverrides.IntegrationOverridesProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Integration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-integration
        '''
        result = self._values.get("integration")
        return typing.cast(typing.Optional[typing.Union[CfnApiGatewayManagedOverrides.IntegrationOverridesProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def route(
        self,
    ) -> typing.Optional[typing.Union[CfnApiGatewayManagedOverrides.RouteOverridesProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Route``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-route
        '''
        result = self._values.get("route")
        return typing.cast(typing.Optional[typing.Union[CfnApiGatewayManagedOverrides.RouteOverridesProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def stage(
        self,
    ) -> typing.Optional[typing.Union[CfnApiGatewayManagedOverrides.StageOverridesProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::ApiGatewayManagedOverrides.Stage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apigatewaymanagedoverrides.html#cfn-apigatewayv2-apigatewaymanagedoverrides-stage
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[typing.Union[CfnApiGatewayManagedOverrides.StageOverridesProperty, _IResolvable_da3f097b]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnApiGatewayManagedOverridesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnApiMapping(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiMapping",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::ApiMapping``.

    :cloudformationResource: AWS::ApiGatewayV2::ApiMapping
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        domain_name: builtins.str,
        stage: builtins.str,
        api_mapping_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::ApiMapping``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::ApiMapping.ApiId``.
        :param domain_name: ``AWS::ApiGatewayV2::ApiMapping.DomainName``.
        :param stage: ``AWS::ApiGatewayV2::ApiMapping.Stage``.
        :param api_mapping_key: ``AWS::ApiGatewayV2::ApiMapping.ApiMappingKey``.
        '''
        props = CfnApiMappingProps(
            api_id=api_id,
            domain_name=domain_name,
            stage=stage,
            api_mapping_key=api_mapping_key,
        )

        jsii.create(CfnApiMapping, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::ApiMapping.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::ApiMapping.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-domainname
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stage")
    def stage(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::ApiMapping.Stage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-stage
        '''
        return typing.cast(builtins.str, jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: builtins.str) -> None:
        jsii.set(self, "stage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiMappingKey")
    def api_mapping_key(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::ApiMapping.ApiMappingKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-apimappingkey
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiMappingKey"))

    @api_mapping_key.setter
    def api_mapping_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "apiMappingKey", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiMappingProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "domain_name": "domainName",
        "stage": "stage",
        "api_mapping_key": "apiMappingKey",
    },
)
class CfnApiMappingProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        domain_name: builtins.str,
        stage: builtins.str,
        api_mapping_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::ApiMapping``.

        :param api_id: ``AWS::ApiGatewayV2::ApiMapping.ApiId``.
        :param domain_name: ``AWS::ApiGatewayV2::ApiMapping.DomainName``.
        :param stage: ``AWS::ApiGatewayV2::ApiMapping.Stage``.
        :param api_mapping_key: ``AWS::ApiGatewayV2::ApiMapping.ApiMappingKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "domain_name": domain_name,
            "stage": stage,
        }
        if api_mapping_key is not None:
            self._values["api_mapping_key"] = api_mapping_key

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::ApiMapping.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::ApiMapping.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-domainname
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stage(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::ApiMapping.Stage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-stage
        '''
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_mapping_key(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::ApiMapping.ApiMappingKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-apimappingkey
        '''
        result = self._values.get("api_mapping_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnApiMappingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_key_selection_expression": "apiKeySelectionExpression",
        "base_path": "basePath",
        "body": "body",
        "body_s3_location": "bodyS3Location",
        "cors_configuration": "corsConfiguration",
        "credentials_arn": "credentialsArn",
        "description": "description",
        "disable_execute_api_endpoint": "disableExecuteApiEndpoint",
        "disable_schema_validation": "disableSchemaValidation",
        "fail_on_warnings": "failOnWarnings",
        "name": "name",
        "protocol_type": "protocolType",
        "route_key": "routeKey",
        "route_selection_expression": "routeSelectionExpression",
        "tags": "tags",
        "target": "target",
        "version": "version",
    },
)
class CfnApiProps:
    def __init__(
        self,
        *,
        api_key_selection_expression: typing.Optional[builtins.str] = None,
        base_path: typing.Optional[builtins.str] = None,
        body: typing.Any = None,
        body_s3_location: typing.Optional[typing.Union[CfnApi.BodyS3LocationProperty, _IResolvable_da3f097b]] = None,
        cors_configuration: typing.Optional[typing.Union[CfnApi.CorsProperty, _IResolvable_da3f097b]] = None,
        credentials_arn: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_execute_api_endpoint: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        disable_schema_validation: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        fail_on_warnings: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        name: typing.Optional[builtins.str] = None,
        protocol_type: typing.Optional[builtins.str] = None,
        route_key: typing.Optional[builtins.str] = None,
        route_selection_expression: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
        target: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::Api``.

        :param api_key_selection_expression: ``AWS::ApiGatewayV2::Api.ApiKeySelectionExpression``.
        :param base_path: ``AWS::ApiGatewayV2::Api.BasePath``.
        :param body: ``AWS::ApiGatewayV2::Api.Body``.
        :param body_s3_location: ``AWS::ApiGatewayV2::Api.BodyS3Location``.
        :param cors_configuration: ``AWS::ApiGatewayV2::Api.CorsConfiguration``.
        :param credentials_arn: ``AWS::ApiGatewayV2::Api.CredentialsArn``.
        :param description: ``AWS::ApiGatewayV2::Api.Description``.
        :param disable_execute_api_endpoint: ``AWS::ApiGatewayV2::Api.DisableExecuteApiEndpoint``.
        :param disable_schema_validation: ``AWS::ApiGatewayV2::Api.DisableSchemaValidation``.
        :param fail_on_warnings: ``AWS::ApiGatewayV2::Api.FailOnWarnings``.
        :param name: ``AWS::ApiGatewayV2::Api.Name``.
        :param protocol_type: ``AWS::ApiGatewayV2::Api.ProtocolType``.
        :param route_key: ``AWS::ApiGatewayV2::Api.RouteKey``.
        :param route_selection_expression: ``AWS::ApiGatewayV2::Api.RouteSelectionExpression``.
        :param tags: ``AWS::ApiGatewayV2::Api.Tags``.
        :param target: ``AWS::ApiGatewayV2::Api.Target``.
        :param version: ``AWS::ApiGatewayV2::Api.Version``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if api_key_selection_expression is not None:
            self._values["api_key_selection_expression"] = api_key_selection_expression
        if base_path is not None:
            self._values["base_path"] = base_path
        if body is not None:
            self._values["body"] = body
        if body_s3_location is not None:
            self._values["body_s3_location"] = body_s3_location
        if cors_configuration is not None:
            self._values["cors_configuration"] = cors_configuration
        if credentials_arn is not None:
            self._values["credentials_arn"] = credentials_arn
        if description is not None:
            self._values["description"] = description
        if disable_execute_api_endpoint is not None:
            self._values["disable_execute_api_endpoint"] = disable_execute_api_endpoint
        if disable_schema_validation is not None:
            self._values["disable_schema_validation"] = disable_schema_validation
        if fail_on_warnings is not None:
            self._values["fail_on_warnings"] = fail_on_warnings
        if name is not None:
            self._values["name"] = name
        if protocol_type is not None:
            self._values["protocol_type"] = protocol_type
        if route_key is not None:
            self._values["route_key"] = route_key
        if route_selection_expression is not None:
            self._values["route_selection_expression"] = route_selection_expression
        if tags is not None:
            self._values["tags"] = tags
        if target is not None:
            self._values["target"] = target
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def api_key_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.ApiKeySelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-apikeyselectionexpression
        '''
        result = self._values.get("api_key_selection_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def base_path(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.BasePath``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-basepath
        '''
        result = self._values.get("base_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def body(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Api.Body``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-body
        '''
        result = self._values.get("body")
        return typing.cast(typing.Any, result)

    @builtins.property
    def body_s3_location(
        self,
    ) -> typing.Optional[typing.Union[CfnApi.BodyS3LocationProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.BodyS3Location``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-bodys3location
        '''
        result = self._values.get("body_s3_location")
        return typing.cast(typing.Optional[typing.Union[CfnApi.BodyS3LocationProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def cors_configuration(
        self,
    ) -> typing.Optional[typing.Union[CfnApi.CorsProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.CorsConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-corsconfiguration
        '''
        result = self._values.get("cors_configuration")
        return typing.cast(typing.Optional[typing.Union[CfnApi.CorsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def credentials_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.CredentialsArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-credentialsarn
        '''
        result = self._values.get("credentials_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_execute_api_endpoint(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.DisableExecuteApiEndpoint``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-disableexecuteapiendpoint
        '''
        result = self._values.get("disable_execute_api_endpoint")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def disable_schema_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.DisableSchemaValidation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-disableschemavalidation
        '''
        result = self._values.get("disable_schema_validation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def fail_on_warnings(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Api.FailOnWarnings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-failonwarnings
        '''
        result = self._values.get("fail_on_warnings")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.ProtocolType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-protocoltype
        '''
        result = self._values.get("protocol_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_key(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.RouteKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-routekey
        '''
        result = self._values.get("route_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.RouteSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-routeselectionexpression
        '''
        result = self._values.get("route_selection_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Api.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.Target``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-target
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Api.Version``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-version
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnAuthorizer(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnAuthorizer",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::Authorizer``.

    :cloudformationResource: AWS::ApiGatewayV2::Authorizer
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        authorizer_type: builtins.str,
        name: builtins.str,
        authorizer_credentials_arn: typing.Optional[builtins.str] = None,
        authorizer_payload_format_version: typing.Optional[builtins.str] = None,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        authorizer_uri: typing.Optional[builtins.str] = None,
        enable_simple_responses: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        identity_validation_expression: typing.Optional[builtins.str] = None,
        jwt_configuration: typing.Optional[typing.Union["CfnAuthorizer.JWTConfigurationProperty", _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::Authorizer``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::Authorizer.ApiId``.
        :param authorizer_type: ``AWS::ApiGatewayV2::Authorizer.AuthorizerType``.
        :param name: ``AWS::ApiGatewayV2::Authorizer.Name``.
        :param authorizer_credentials_arn: ``AWS::ApiGatewayV2::Authorizer.AuthorizerCredentialsArn``.
        :param authorizer_payload_format_version: ``AWS::ApiGatewayV2::Authorizer.AuthorizerPayloadFormatVersion``.
        :param authorizer_result_ttl_in_seconds: ``AWS::ApiGatewayV2::Authorizer.AuthorizerResultTtlInSeconds``.
        :param authorizer_uri: ``AWS::ApiGatewayV2::Authorizer.AuthorizerUri``.
        :param enable_simple_responses: ``AWS::ApiGatewayV2::Authorizer.EnableSimpleResponses``.
        :param identity_source: ``AWS::ApiGatewayV2::Authorizer.IdentitySource``.
        :param identity_validation_expression: ``AWS::ApiGatewayV2::Authorizer.IdentityValidationExpression``.
        :param jwt_configuration: ``AWS::ApiGatewayV2::Authorizer.JwtConfiguration``.
        '''
        props = CfnAuthorizerProps(
            api_id=api_id,
            authorizer_type=authorizer_type,
            name=name,
            authorizer_credentials_arn=authorizer_credentials_arn,
            authorizer_payload_format_version=authorizer_payload_format_version,
            authorizer_result_ttl_in_seconds=authorizer_result_ttl_in_seconds,
            authorizer_uri=authorizer_uri,
            enable_simple_responses=enable_simple_responses,
            identity_source=identity_source,
            identity_validation_expression=identity_validation_expression,
            jwt_configuration=jwt_configuration,
        )

        jsii.create(CfnAuthorizer, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Authorizer.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerType")
    def authorizer_type(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizertype
        '''
        return typing.cast(builtins.str, jsii.get(self, "authorizerType"))

    @authorizer_type.setter
    def authorizer_type(self, value: builtins.str) -> None:
        jsii.set(self, "authorizerType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Authorizer.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerCredentialsArn")
    def authorizer_credentials_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerCredentialsArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizercredentialsarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizerCredentialsArn"))

    @authorizer_credentials_arn.setter
    def authorizer_credentials_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "authorizerCredentialsArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerPayloadFormatVersion")
    def authorizer_payload_format_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerPayloadFormatVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizerpayloadformatversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizerPayloadFormatVersion"))

    @authorizer_payload_format_version.setter
    def authorizer_payload_format_version(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "authorizerPayloadFormatVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerResultTtlInSeconds")
    def authorizer_result_ttl_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerResultTtlInSeconds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizerresultttlinseconds
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "authorizerResultTtlInSeconds"))

    @authorizer_result_ttl_in_seconds.setter
    def authorizer_result_ttl_in_seconds(
        self,
        value: typing.Optional[jsii.Number],
    ) -> None:
        jsii.set(self, "authorizerResultTtlInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerUri")
    def authorizer_uri(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerUri``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizeruri
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizerUri"))

    @authorizer_uri.setter
    def authorizer_uri(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "authorizerUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableSimpleResponses")
    def enable_simple_responses(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Authorizer.EnableSimpleResponses``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-enablesimpleresponses
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enableSimpleResponses"))

    @enable_simple_responses.setter
    def enable_simple_responses(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enableSimpleResponses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identitySource")
    def identity_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::ApiGatewayV2::Authorizer.IdentitySource``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-identitysource
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "identitySource"))

    @identity_source.setter
    def identity_source(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "identitySource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityValidationExpression")
    def identity_validation_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Authorizer.IdentityValidationExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-identityvalidationexpression
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityValidationExpression"))

    @identity_validation_expression.setter
    def identity_validation_expression(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "identityValidationExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jwtConfiguration")
    def jwt_configuration(
        self,
    ) -> typing.Optional[typing.Union["CfnAuthorizer.JWTConfigurationProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Authorizer.JwtConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-jwtconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnAuthorizer.JWTConfigurationProperty", _IResolvable_da3f097b]], jsii.get(self, "jwtConfiguration"))

    @jwt_configuration.setter
    def jwt_configuration(
        self,
        value: typing.Optional[typing.Union["CfnAuthorizer.JWTConfigurationProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "jwtConfiguration", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnAuthorizer.JWTConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"audience": "audience", "issuer": "issuer"},
    )
    class JWTConfigurationProperty:
        def __init__(
            self,
            *,
            audience: typing.Optional[typing.Sequence[builtins.str]] = None,
            issuer: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param audience: ``CfnAuthorizer.JWTConfigurationProperty.Audience``.
            :param issuer: ``CfnAuthorizer.JWTConfigurationProperty.Issuer``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-authorizer-jwtconfiguration.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if audience is not None:
                self._values["audience"] = audience
            if issuer is not None:
                self._values["issuer"] = issuer

        @builtins.property
        def audience(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnAuthorizer.JWTConfigurationProperty.Audience``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-authorizer-jwtconfiguration.html#cfn-apigatewayv2-authorizer-jwtconfiguration-audience
            '''
            result = self._values.get("audience")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def issuer(self) -> typing.Optional[builtins.str]:
            '''``CfnAuthorizer.JWTConfigurationProperty.Issuer``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-authorizer-jwtconfiguration.html#cfn-apigatewayv2-authorizer-jwtconfiguration-issuer
            '''
            result = self._values.get("issuer")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "JWTConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "authorizer_type": "authorizerType",
        "name": "name",
        "authorizer_credentials_arn": "authorizerCredentialsArn",
        "authorizer_payload_format_version": "authorizerPayloadFormatVersion",
        "authorizer_result_ttl_in_seconds": "authorizerResultTtlInSeconds",
        "authorizer_uri": "authorizerUri",
        "enable_simple_responses": "enableSimpleResponses",
        "identity_source": "identitySource",
        "identity_validation_expression": "identityValidationExpression",
        "jwt_configuration": "jwtConfiguration",
    },
)
class CfnAuthorizerProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        authorizer_type: builtins.str,
        name: builtins.str,
        authorizer_credentials_arn: typing.Optional[builtins.str] = None,
        authorizer_payload_format_version: typing.Optional[builtins.str] = None,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        authorizer_uri: typing.Optional[builtins.str] = None,
        enable_simple_responses: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        identity_validation_expression: typing.Optional[builtins.str] = None,
        jwt_configuration: typing.Optional[typing.Union[CfnAuthorizer.JWTConfigurationProperty, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::Authorizer``.

        :param api_id: ``AWS::ApiGatewayV2::Authorizer.ApiId``.
        :param authorizer_type: ``AWS::ApiGatewayV2::Authorizer.AuthorizerType``.
        :param name: ``AWS::ApiGatewayV2::Authorizer.Name``.
        :param authorizer_credentials_arn: ``AWS::ApiGatewayV2::Authorizer.AuthorizerCredentialsArn``.
        :param authorizer_payload_format_version: ``AWS::ApiGatewayV2::Authorizer.AuthorizerPayloadFormatVersion``.
        :param authorizer_result_ttl_in_seconds: ``AWS::ApiGatewayV2::Authorizer.AuthorizerResultTtlInSeconds``.
        :param authorizer_uri: ``AWS::ApiGatewayV2::Authorizer.AuthorizerUri``.
        :param enable_simple_responses: ``AWS::ApiGatewayV2::Authorizer.EnableSimpleResponses``.
        :param identity_source: ``AWS::ApiGatewayV2::Authorizer.IdentitySource``.
        :param identity_validation_expression: ``AWS::ApiGatewayV2::Authorizer.IdentityValidationExpression``.
        :param jwt_configuration: ``AWS::ApiGatewayV2::Authorizer.JwtConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "authorizer_type": authorizer_type,
            "name": name,
        }
        if authorizer_credentials_arn is not None:
            self._values["authorizer_credentials_arn"] = authorizer_credentials_arn
        if authorizer_payload_format_version is not None:
            self._values["authorizer_payload_format_version"] = authorizer_payload_format_version
        if authorizer_result_ttl_in_seconds is not None:
            self._values["authorizer_result_ttl_in_seconds"] = authorizer_result_ttl_in_seconds
        if authorizer_uri is not None:
            self._values["authorizer_uri"] = authorizer_uri
        if enable_simple_responses is not None:
            self._values["enable_simple_responses"] = enable_simple_responses
        if identity_source is not None:
            self._values["identity_source"] = identity_source
        if identity_validation_expression is not None:
            self._values["identity_validation_expression"] = identity_validation_expression
        if jwt_configuration is not None:
            self._values["jwt_configuration"] = jwt_configuration

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Authorizer.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorizer_type(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizertype
        '''
        result = self._values.get("authorizer_type")
        assert result is not None, "Required property 'authorizer_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Authorizer.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorizer_credentials_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerCredentialsArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizercredentialsarn
        '''
        result = self._values.get("authorizer_credentials_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorizer_payload_format_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerPayloadFormatVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizerpayloadformatversion
        '''
        result = self._values.get("authorizer_payload_format_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorizer_result_ttl_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerResultTtlInSeconds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizerresultttlinseconds
        '''
        result = self._values.get("authorizer_result_ttl_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def authorizer_uri(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Authorizer.AuthorizerUri``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizeruri
        '''
        result = self._values.get("authorizer_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_simple_responses(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Authorizer.EnableSimpleResponses``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-enablesimpleresponses
        '''
        result = self._values.get("enable_simple_responses")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::ApiGatewayV2::Authorizer.IdentitySource``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-identitysource
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def identity_validation_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Authorizer.IdentityValidationExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-identityvalidationexpression
        '''
        result = self._values.get("identity_validation_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_configuration(
        self,
    ) -> typing.Optional[typing.Union[CfnAuthorizer.JWTConfigurationProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Authorizer.JwtConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-jwtconfiguration
        '''
        result = self._values.get("jwt_configuration")
        return typing.cast(typing.Optional[typing.Union[CfnAuthorizer.JWTConfigurationProperty, _IResolvable_da3f097b]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDeployment(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnDeployment",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::Deployment``.

    :cloudformationResource: AWS::ApiGatewayV2::Deployment
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::Deployment``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::Deployment.ApiId``.
        :param description: ``AWS::ApiGatewayV2::Deployment.Description``.
        :param stage_name: ``AWS::ApiGatewayV2::Deployment.StageName``.
        '''
        props = CfnDeploymentProps(
            api_id=api_id, description=description, stage_name=stage_name
        )

        jsii.create(CfnDeployment, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Deployment.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html#cfn-apigatewayv2-deployment-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Deployment.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html#cfn-apigatewayv2-deployment-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Deployment.StageName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html#cfn-apigatewayv2-deployment-stagename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageName"))

    @stage_name.setter
    def stage_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "stageName", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnDeploymentProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "description": "description",
        "stage_name": "stageName",
    },
)
class CfnDeploymentProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::Deployment``.

        :param api_id: ``AWS::ApiGatewayV2::Deployment.ApiId``.
        :param description: ``AWS::ApiGatewayV2::Deployment.Description``.
        :param stage_name: ``AWS::ApiGatewayV2::Deployment.StageName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
        }
        if description is not None:
            self._values["description"] = description
        if stage_name is not None:
            self._values["stage_name"] = stage_name

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Deployment.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html#cfn-apigatewayv2-deployment-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Deployment.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html#cfn-apigatewayv2-deployment-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Deployment.StageName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html#cfn-apigatewayv2-deployment-stagename
        '''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDeploymentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDomainName(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnDomainName",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::DomainName``.

    :cloudformationResource: AWS::ApiGatewayV2::DomainName
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        domain_name_configurations: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDomainName.DomainNameConfigurationProperty", _IResolvable_da3f097b]]]] = None,
        mutual_tls_authentication: typing.Optional[typing.Union["CfnDomainName.MutualTlsAuthenticationProperty", _IResolvable_da3f097b]] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::DomainName``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param domain_name: ``AWS::ApiGatewayV2::DomainName.DomainName``.
        :param domain_name_configurations: ``AWS::ApiGatewayV2::DomainName.DomainNameConfigurations``.
        :param mutual_tls_authentication: ``AWS::ApiGatewayV2::DomainName.MutualTlsAuthentication``.
        :param tags: ``AWS::ApiGatewayV2::DomainName.Tags``.
        '''
        props = CfnDomainNameProps(
            domain_name=domain_name,
            domain_name_configurations=domain_name_configurations,
            mutual_tls_authentication=mutual_tls_authentication,
            tags=tags,
        )

        jsii.create(CfnDomainName, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrRegionalDomainName")
    def attr_regional_domain_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: RegionalDomainName
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrRegionalDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrRegionalHostedZoneId")
    def attr_regional_hosted_zone_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: RegionalHostedZoneId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrRegionalHostedZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::ApiGatewayV2::DomainName.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::DomainName.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-domainname
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNameConfigurations")
    def domain_name_configurations(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDomainName.DomainNameConfigurationProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::ApiGatewayV2::DomainName.DomainNameConfigurations``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-domainnameconfigurations
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDomainName.DomainNameConfigurationProperty", _IResolvable_da3f097b]]]], jsii.get(self, "domainNameConfigurations"))

    @domain_name_configurations.setter
    def domain_name_configurations(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDomainName.DomainNameConfigurationProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "domainNameConfigurations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mutualTlsAuthentication")
    def mutual_tls_authentication(
        self,
    ) -> typing.Optional[typing.Union["CfnDomainName.MutualTlsAuthenticationProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::DomainName.MutualTlsAuthentication``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-mutualtlsauthentication
        '''
        return typing.cast(typing.Optional[typing.Union["CfnDomainName.MutualTlsAuthenticationProperty", _IResolvable_da3f097b]], jsii.get(self, "mutualTlsAuthentication"))

    @mutual_tls_authentication.setter
    def mutual_tls_authentication(
        self,
        value: typing.Optional[typing.Union["CfnDomainName.MutualTlsAuthenticationProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "mutualTlsAuthentication", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnDomainName.DomainNameConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "certificate_arn": "certificateArn",
            "certificate_name": "certificateName",
            "endpoint_type": "endpointType",
            "security_policy": "securityPolicy",
        },
    )
    class DomainNameConfigurationProperty:
        def __init__(
            self,
            *,
            certificate_arn: typing.Optional[builtins.str] = None,
            certificate_name: typing.Optional[builtins.str] = None,
            endpoint_type: typing.Optional[builtins.str] = None,
            security_policy: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param certificate_arn: ``CfnDomainName.DomainNameConfigurationProperty.CertificateArn``.
            :param certificate_name: ``CfnDomainName.DomainNameConfigurationProperty.CertificateName``.
            :param endpoint_type: ``CfnDomainName.DomainNameConfigurationProperty.EndpointType``.
            :param security_policy: ``CfnDomainName.DomainNameConfigurationProperty.SecurityPolicy``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-domainnameconfiguration.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if certificate_arn is not None:
                self._values["certificate_arn"] = certificate_arn
            if certificate_name is not None:
                self._values["certificate_name"] = certificate_name
            if endpoint_type is not None:
                self._values["endpoint_type"] = endpoint_type
            if security_policy is not None:
                self._values["security_policy"] = security_policy

        @builtins.property
        def certificate_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainName.DomainNameConfigurationProperty.CertificateArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-domainnameconfiguration.html#cfn-apigatewayv2-domainname-domainnameconfiguration-certificatearn
            '''
            result = self._values.get("certificate_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def certificate_name(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainName.DomainNameConfigurationProperty.CertificateName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-domainnameconfiguration.html#cfn-apigatewayv2-domainname-domainnameconfiguration-certificatename
            '''
            result = self._values.get("certificate_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def endpoint_type(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainName.DomainNameConfigurationProperty.EndpointType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-domainnameconfiguration.html#cfn-apigatewayv2-domainname-domainnameconfiguration-endpointtype
            '''
            result = self._values.get("endpoint_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def security_policy(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainName.DomainNameConfigurationProperty.SecurityPolicy``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-domainnameconfiguration.html#cfn-apigatewayv2-domainname-domainnameconfiguration-securitypolicy
            '''
            result = self._values.get("security_policy")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DomainNameConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnDomainName.MutualTlsAuthenticationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "truststore_uri": "truststoreUri",
            "truststore_version": "truststoreVersion",
        },
    )
    class MutualTlsAuthenticationProperty:
        def __init__(
            self,
            *,
            truststore_uri: typing.Optional[builtins.str] = None,
            truststore_version: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param truststore_uri: ``CfnDomainName.MutualTlsAuthenticationProperty.TruststoreUri``.
            :param truststore_version: ``CfnDomainName.MutualTlsAuthenticationProperty.TruststoreVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-mutualtlsauthentication.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if truststore_uri is not None:
                self._values["truststore_uri"] = truststore_uri
            if truststore_version is not None:
                self._values["truststore_version"] = truststore_version

        @builtins.property
        def truststore_uri(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainName.MutualTlsAuthenticationProperty.TruststoreUri``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-mutualtlsauthentication.html#cfn-apigatewayv2-domainname-mutualtlsauthentication-truststoreuri
            '''
            result = self._values.get("truststore_uri")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def truststore_version(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainName.MutualTlsAuthenticationProperty.TruststoreVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-mutualtlsauthentication.html#cfn-apigatewayv2-domainname-mutualtlsauthentication-truststoreversion
            '''
            result = self._values.get("truststore_version")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MutualTlsAuthenticationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnDomainNameProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "domain_name_configurations": "domainNameConfigurations",
        "mutual_tls_authentication": "mutualTlsAuthentication",
        "tags": "tags",
    },
)
class CfnDomainNameProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        domain_name_configurations: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnDomainName.DomainNameConfigurationProperty, _IResolvable_da3f097b]]]] = None,
        mutual_tls_authentication: typing.Optional[typing.Union[CfnDomainName.MutualTlsAuthenticationProperty, _IResolvable_da3f097b]] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::DomainName``.

        :param domain_name: ``AWS::ApiGatewayV2::DomainName.DomainName``.
        :param domain_name_configurations: ``AWS::ApiGatewayV2::DomainName.DomainNameConfigurations``.
        :param mutual_tls_authentication: ``AWS::ApiGatewayV2::DomainName.MutualTlsAuthentication``.
        :param tags: ``AWS::ApiGatewayV2::DomainName.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
        }
        if domain_name_configurations is not None:
            self._values["domain_name_configurations"] = domain_name_configurations
        if mutual_tls_authentication is not None:
            self._values["mutual_tls_authentication"] = mutual_tls_authentication
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::DomainName.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-domainname
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name_configurations(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnDomainName.DomainNameConfigurationProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::ApiGatewayV2::DomainName.DomainNameConfigurations``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-domainnameconfigurations
        '''
        result = self._values.get("domain_name_configurations")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnDomainName.DomainNameConfigurationProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def mutual_tls_authentication(
        self,
    ) -> typing.Optional[typing.Union[CfnDomainName.MutualTlsAuthenticationProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::DomainName.MutualTlsAuthentication``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-mutualtlsauthentication
        '''
        result = self._values.get("mutual_tls_authentication")
        return typing.cast(typing.Optional[typing.Union[CfnDomainName.MutualTlsAuthenticationProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::DomainName.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDomainNameProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnIntegration(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnIntegration",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::Integration``.

    :cloudformationResource: AWS::ApiGatewayV2::Integration
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        integration_type: builtins.str,
        connection_id: typing.Optional[builtins.str] = None,
        connection_type: typing.Optional[builtins.str] = None,
        content_handling_strategy: typing.Optional[builtins.str] = None,
        credentials_arn: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        integration_method: typing.Optional[builtins.str] = None,
        integration_subtype: typing.Optional[builtins.str] = None,
        integration_uri: typing.Optional[builtins.str] = None,
        passthrough_behavior: typing.Optional[builtins.str] = None,
        payload_format_version: typing.Optional[builtins.str] = None,
        request_parameters: typing.Any = None,
        request_templates: typing.Any = None,
        response_parameters: typing.Any = None,
        template_selection_expression: typing.Optional[builtins.str] = None,
        timeout_in_millis: typing.Optional[jsii.Number] = None,
        tls_config: typing.Optional[typing.Union["CfnIntegration.TlsConfigProperty", _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::Integration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::Integration.ApiId``.
        :param integration_type: ``AWS::ApiGatewayV2::Integration.IntegrationType``.
        :param connection_id: ``AWS::ApiGatewayV2::Integration.ConnectionId``.
        :param connection_type: ``AWS::ApiGatewayV2::Integration.ConnectionType``.
        :param content_handling_strategy: ``AWS::ApiGatewayV2::Integration.ContentHandlingStrategy``.
        :param credentials_arn: ``AWS::ApiGatewayV2::Integration.CredentialsArn``.
        :param description: ``AWS::ApiGatewayV2::Integration.Description``.
        :param integration_method: ``AWS::ApiGatewayV2::Integration.IntegrationMethod``.
        :param integration_subtype: ``AWS::ApiGatewayV2::Integration.IntegrationSubtype``.
        :param integration_uri: ``AWS::ApiGatewayV2::Integration.IntegrationUri``.
        :param passthrough_behavior: ``AWS::ApiGatewayV2::Integration.PassthroughBehavior``.
        :param payload_format_version: ``AWS::ApiGatewayV2::Integration.PayloadFormatVersion``.
        :param request_parameters: ``AWS::ApiGatewayV2::Integration.RequestParameters``.
        :param request_templates: ``AWS::ApiGatewayV2::Integration.RequestTemplates``.
        :param response_parameters: ``AWS::ApiGatewayV2::Integration.ResponseParameters``.
        :param template_selection_expression: ``AWS::ApiGatewayV2::Integration.TemplateSelectionExpression``.
        :param timeout_in_millis: ``AWS::ApiGatewayV2::Integration.TimeoutInMillis``.
        :param tls_config: ``AWS::ApiGatewayV2::Integration.TlsConfig``.
        '''
        props = CfnIntegrationProps(
            api_id=api_id,
            integration_type=integration_type,
            connection_id=connection_id,
            connection_type=connection_type,
            content_handling_strategy=content_handling_strategy,
            credentials_arn=credentials_arn,
            description=description,
            integration_method=integration_method,
            integration_subtype=integration_subtype,
            integration_uri=integration_uri,
            passthrough_behavior=passthrough_behavior,
            payload_format_version=payload_format_version,
            request_parameters=request_parameters,
            request_templates=request_templates,
            response_parameters=response_parameters,
            template_selection_expression=template_selection_expression,
            timeout_in_millis=timeout_in_millis,
            tls_config=tls_config,
        )

        jsii.create(CfnIntegration, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Integration.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationType")
    def integration_type(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Integration.IntegrationType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationtype
        '''
        return typing.cast(builtins.str, jsii.get(self, "integrationType"))

    @integration_type.setter
    def integration_type(self, value: builtins.str) -> None:
        jsii.set(self, "integrationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestParameters")
    def request_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Integration.RequestParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-requestparameters
        '''
        return typing.cast(typing.Any, jsii.get(self, "requestParameters"))

    @request_parameters.setter
    def request_parameters(self, value: typing.Any) -> None:
        jsii.set(self, "requestParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestTemplates")
    def request_templates(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Integration.RequestTemplates``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-requesttemplates
        '''
        return typing.cast(typing.Any, jsii.get(self, "requestTemplates"))

    @request_templates.setter
    def request_templates(self, value: typing.Any) -> None:
        jsii.set(self, "requestTemplates", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseParameters")
    def response_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Integration.ResponseParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-responseparameters
        '''
        return typing.cast(typing.Any, jsii.get(self, "responseParameters"))

    @response_parameters.setter
    def response_parameters(self, value: typing.Any) -> None:
        jsii.set(self, "responseParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionId")
    def connection_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.ConnectionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-connectionid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionId"))

    @connection_id.setter
    def connection_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "connectionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionType")
    def connection_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.ConnectionType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-connectiontype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionType"))

    @connection_type.setter
    def connection_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "connectionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentHandlingStrategy")
    def content_handling_strategy(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.ContentHandlingStrategy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-contenthandlingstrategy
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentHandlingStrategy"))

    @content_handling_strategy.setter
    def content_handling_strategy(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "contentHandlingStrategy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialsArn")
    def credentials_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.CredentialsArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-credentialsarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "credentialsArn"))

    @credentials_arn.setter
    def credentials_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "credentialsArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationMethod")
    def integration_method(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.IntegrationMethod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationmethod
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationMethod"))

    @integration_method.setter
    def integration_method(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "integrationMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationSubtype")
    def integration_subtype(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.IntegrationSubtype``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationsubtype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationSubtype"))

    @integration_subtype.setter
    def integration_subtype(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "integrationSubtype", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationUri")
    def integration_uri(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.IntegrationUri``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationuri
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationUri"))

    @integration_uri.setter
    def integration_uri(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "integrationUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passthroughBehavior")
    def passthrough_behavior(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.PassthroughBehavior``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-passthroughbehavior
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passthroughBehavior"))

    @passthrough_behavior.setter
    def passthrough_behavior(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "passthroughBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadFormatVersion")
    def payload_format_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.PayloadFormatVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-payloadformatversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "payloadFormatVersion"))

    @payload_format_version.setter
    def payload_format_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "payloadFormatVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateSelectionExpression")
    def template_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.TemplateSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-templateselectionexpression
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateSelectionExpression"))

    @template_selection_expression.setter
    def template_selection_expression(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "templateSelectionExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInMillis")
    def timeout_in_millis(self) -> typing.Optional[jsii.Number]:
        '''``AWS::ApiGatewayV2::Integration.TimeoutInMillis``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-timeoutinmillis
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInMillis"))

    @timeout_in_millis.setter
    def timeout_in_millis(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "timeoutInMillis", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsConfig")
    def tls_config(
        self,
    ) -> typing.Optional[typing.Union["CfnIntegration.TlsConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Integration.TlsConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-tlsconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnIntegration.TlsConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "tlsConfig"))

    @tls_config.setter
    def tls_config(
        self,
        value: typing.Optional[typing.Union["CfnIntegration.TlsConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "tlsConfig", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnIntegration.ResponseParameterListProperty",
        jsii_struct_bases=[],
        name_mapping={"response_parameters": "responseParameters"},
    )
    class ResponseParameterListProperty:
        def __init__(
            self,
            *,
            response_parameters: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnIntegration.ResponseParameterProperty", _IResolvable_da3f097b]]]] = None,
        ) -> None:
            '''
            :param response_parameters: ``CfnIntegration.ResponseParameterListProperty.ResponseParameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-responseparameterlist.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if response_parameters is not None:
                self._values["response_parameters"] = response_parameters

        @builtins.property
        def response_parameters(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnIntegration.ResponseParameterProperty", _IResolvable_da3f097b]]]]:
            '''``CfnIntegration.ResponseParameterListProperty.ResponseParameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-responseparameterlist.html#cfn-apigatewayv2-integration-responseparameterlist-responseparameters
            '''
            result = self._values.get("response_parameters")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnIntegration.ResponseParameterProperty", _IResolvable_da3f097b]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResponseParameterListProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnIntegration.ResponseParameterProperty",
        jsii_struct_bases=[],
        name_mapping={"destination": "destination", "source": "source"},
    )
    class ResponseParameterProperty:
        def __init__(self, *, destination: builtins.str, source: builtins.str) -> None:
            '''
            :param destination: ``CfnIntegration.ResponseParameterProperty.Destination``.
            :param source: ``CfnIntegration.ResponseParameterProperty.Source``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-responseparameter.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "destination": destination,
                "source": source,
            }

        @builtins.property
        def destination(self) -> builtins.str:
            '''``CfnIntegration.ResponseParameterProperty.Destination``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-responseparameter.html#cfn-apigatewayv2-integration-responseparameter-destination
            '''
            result = self._values.get("destination")
            assert result is not None, "Required property 'destination' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def source(self) -> builtins.str:
            '''``CfnIntegration.ResponseParameterProperty.Source``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-responseparameter.html#cfn-apigatewayv2-integration-responseparameter-source
            '''
            result = self._values.get("source")
            assert result is not None, "Required property 'source' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResponseParameterProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnIntegration.TlsConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"server_name_to_verify": "serverNameToVerify"},
    )
    class TlsConfigProperty:
        def __init__(
            self,
            *,
            server_name_to_verify: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param server_name_to_verify: ``CfnIntegration.TlsConfigProperty.ServerNameToVerify``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if server_name_to_verify is not None:
                self._values["server_name_to_verify"] = server_name_to_verify

        @builtins.property
        def server_name_to_verify(self) -> typing.Optional[builtins.str]:
            '''``CfnIntegration.TlsConfigProperty.ServerNameToVerify``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html#cfn-apigatewayv2-integration-tlsconfig-servernametoverify
            '''
            result = self._values.get("server_name_to_verify")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TlsConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "integration_type": "integrationType",
        "connection_id": "connectionId",
        "connection_type": "connectionType",
        "content_handling_strategy": "contentHandlingStrategy",
        "credentials_arn": "credentialsArn",
        "description": "description",
        "integration_method": "integrationMethod",
        "integration_subtype": "integrationSubtype",
        "integration_uri": "integrationUri",
        "passthrough_behavior": "passthroughBehavior",
        "payload_format_version": "payloadFormatVersion",
        "request_parameters": "requestParameters",
        "request_templates": "requestTemplates",
        "response_parameters": "responseParameters",
        "template_selection_expression": "templateSelectionExpression",
        "timeout_in_millis": "timeoutInMillis",
        "tls_config": "tlsConfig",
    },
)
class CfnIntegrationProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        integration_type: builtins.str,
        connection_id: typing.Optional[builtins.str] = None,
        connection_type: typing.Optional[builtins.str] = None,
        content_handling_strategy: typing.Optional[builtins.str] = None,
        credentials_arn: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        integration_method: typing.Optional[builtins.str] = None,
        integration_subtype: typing.Optional[builtins.str] = None,
        integration_uri: typing.Optional[builtins.str] = None,
        passthrough_behavior: typing.Optional[builtins.str] = None,
        payload_format_version: typing.Optional[builtins.str] = None,
        request_parameters: typing.Any = None,
        request_templates: typing.Any = None,
        response_parameters: typing.Any = None,
        template_selection_expression: typing.Optional[builtins.str] = None,
        timeout_in_millis: typing.Optional[jsii.Number] = None,
        tls_config: typing.Optional[typing.Union[CfnIntegration.TlsConfigProperty, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::Integration``.

        :param api_id: ``AWS::ApiGatewayV2::Integration.ApiId``.
        :param integration_type: ``AWS::ApiGatewayV2::Integration.IntegrationType``.
        :param connection_id: ``AWS::ApiGatewayV2::Integration.ConnectionId``.
        :param connection_type: ``AWS::ApiGatewayV2::Integration.ConnectionType``.
        :param content_handling_strategy: ``AWS::ApiGatewayV2::Integration.ContentHandlingStrategy``.
        :param credentials_arn: ``AWS::ApiGatewayV2::Integration.CredentialsArn``.
        :param description: ``AWS::ApiGatewayV2::Integration.Description``.
        :param integration_method: ``AWS::ApiGatewayV2::Integration.IntegrationMethod``.
        :param integration_subtype: ``AWS::ApiGatewayV2::Integration.IntegrationSubtype``.
        :param integration_uri: ``AWS::ApiGatewayV2::Integration.IntegrationUri``.
        :param passthrough_behavior: ``AWS::ApiGatewayV2::Integration.PassthroughBehavior``.
        :param payload_format_version: ``AWS::ApiGatewayV2::Integration.PayloadFormatVersion``.
        :param request_parameters: ``AWS::ApiGatewayV2::Integration.RequestParameters``.
        :param request_templates: ``AWS::ApiGatewayV2::Integration.RequestTemplates``.
        :param response_parameters: ``AWS::ApiGatewayV2::Integration.ResponseParameters``.
        :param template_selection_expression: ``AWS::ApiGatewayV2::Integration.TemplateSelectionExpression``.
        :param timeout_in_millis: ``AWS::ApiGatewayV2::Integration.TimeoutInMillis``.
        :param tls_config: ``AWS::ApiGatewayV2::Integration.TlsConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "integration_type": integration_type,
        }
        if connection_id is not None:
            self._values["connection_id"] = connection_id
        if connection_type is not None:
            self._values["connection_type"] = connection_type
        if content_handling_strategy is not None:
            self._values["content_handling_strategy"] = content_handling_strategy
        if credentials_arn is not None:
            self._values["credentials_arn"] = credentials_arn
        if description is not None:
            self._values["description"] = description
        if integration_method is not None:
            self._values["integration_method"] = integration_method
        if integration_subtype is not None:
            self._values["integration_subtype"] = integration_subtype
        if integration_uri is not None:
            self._values["integration_uri"] = integration_uri
        if passthrough_behavior is not None:
            self._values["passthrough_behavior"] = passthrough_behavior
        if payload_format_version is not None:
            self._values["payload_format_version"] = payload_format_version
        if request_parameters is not None:
            self._values["request_parameters"] = request_parameters
        if request_templates is not None:
            self._values["request_templates"] = request_templates
        if response_parameters is not None:
            self._values["response_parameters"] = response_parameters
        if template_selection_expression is not None:
            self._values["template_selection_expression"] = template_selection_expression
        if timeout_in_millis is not None:
            self._values["timeout_in_millis"] = timeout_in_millis
        if tls_config is not None:
            self._values["tls_config"] = tls_config

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Integration.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def integration_type(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Integration.IntegrationType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationtype
        '''
        result = self._values.get("integration_type")
        assert result is not None, "Required property 'integration_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connection_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.ConnectionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-connectionid
        '''
        result = self._values.get("connection_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.ConnectionType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-connectiontype
        '''
        result = self._values.get("connection_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_handling_strategy(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.ContentHandlingStrategy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-contenthandlingstrategy
        '''
        result = self._values.get("content_handling_strategy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.CredentialsArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-credentialsarn
        '''
        result = self._values.get("credentials_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_method(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.IntegrationMethod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationmethod
        '''
        result = self._values.get("integration_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_subtype(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.IntegrationSubtype``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationsubtype
        '''
        result = self._values.get("integration_subtype")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_uri(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.IntegrationUri``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationuri
        '''
        result = self._values.get("integration_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def passthrough_behavior(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.PassthroughBehavior``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-passthroughbehavior
        '''
        result = self._values.get("passthrough_behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def payload_format_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.PayloadFormatVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-payloadformatversion
        '''
        result = self._values.get("payload_format_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Integration.RequestParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-requestparameters
        '''
        result = self._values.get("request_parameters")
        return typing.cast(typing.Any, result)

    @builtins.property
    def request_templates(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Integration.RequestTemplates``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-requesttemplates
        '''
        result = self._values.get("request_templates")
        return typing.cast(typing.Any, result)

    @builtins.property
    def response_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Integration.ResponseParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-responseparameters
        '''
        result = self._values.get("response_parameters")
        return typing.cast(typing.Any, result)

    @builtins.property
    def template_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Integration.TemplateSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-templateselectionexpression
        '''
        result = self._values.get("template_selection_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout_in_millis(self) -> typing.Optional[jsii.Number]:
        '''``AWS::ApiGatewayV2::Integration.TimeoutInMillis``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-timeoutinmillis
        '''
        result = self._values.get("timeout_in_millis")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls_config(
        self,
    ) -> typing.Optional[typing.Union[CfnIntegration.TlsConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Integration.TlsConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-tlsconfig
        '''
        result = self._values.get("tls_config")
        return typing.cast(typing.Optional[typing.Union[CfnIntegration.TlsConfigProperty, _IResolvable_da3f097b]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnIntegrationResponse(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnIntegrationResponse",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::IntegrationResponse``.

    :cloudformationResource: AWS::ApiGatewayV2::IntegrationResponse
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        integration_id: builtins.str,
        integration_response_key: builtins.str,
        content_handling_strategy: typing.Optional[builtins.str] = None,
        response_parameters: typing.Any = None,
        response_templates: typing.Any = None,
        template_selection_expression: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::IntegrationResponse``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::IntegrationResponse.ApiId``.
        :param integration_id: ``AWS::ApiGatewayV2::IntegrationResponse.IntegrationId``.
        :param integration_response_key: ``AWS::ApiGatewayV2::IntegrationResponse.IntegrationResponseKey``.
        :param content_handling_strategy: ``AWS::ApiGatewayV2::IntegrationResponse.ContentHandlingStrategy``.
        :param response_parameters: ``AWS::ApiGatewayV2::IntegrationResponse.ResponseParameters``.
        :param response_templates: ``AWS::ApiGatewayV2::IntegrationResponse.ResponseTemplates``.
        :param template_selection_expression: ``AWS::ApiGatewayV2::IntegrationResponse.TemplateSelectionExpression``.
        '''
        props = CfnIntegrationResponseProps(
            api_id=api_id,
            integration_id=integration_id,
            integration_response_key=integration_response_key,
            content_handling_strategy=content_handling_strategy,
            response_parameters=response_parameters,
            response_templates=response_templates,
            template_selection_expression=template_selection_expression,
        )

        jsii.create(CfnIntegrationResponse, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::IntegrationResponse.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationId")
    def integration_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::IntegrationResponse.IntegrationId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-integrationid
        '''
        return typing.cast(builtins.str, jsii.get(self, "integrationId"))

    @integration_id.setter
    def integration_id(self, value: builtins.str) -> None:
        jsii.set(self, "integrationId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationResponseKey")
    def integration_response_key(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::IntegrationResponse.IntegrationResponseKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-integrationresponsekey
        '''
        return typing.cast(builtins.str, jsii.get(self, "integrationResponseKey"))

    @integration_response_key.setter
    def integration_response_key(self, value: builtins.str) -> None:
        jsii.set(self, "integrationResponseKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseParameters")
    def response_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::IntegrationResponse.ResponseParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-responseparameters
        '''
        return typing.cast(typing.Any, jsii.get(self, "responseParameters"))

    @response_parameters.setter
    def response_parameters(self, value: typing.Any) -> None:
        jsii.set(self, "responseParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseTemplates")
    def response_templates(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::IntegrationResponse.ResponseTemplates``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-responsetemplates
        '''
        return typing.cast(typing.Any, jsii.get(self, "responseTemplates"))

    @response_templates.setter
    def response_templates(self, value: typing.Any) -> None:
        jsii.set(self, "responseTemplates", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentHandlingStrategy")
    def content_handling_strategy(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::IntegrationResponse.ContentHandlingStrategy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-contenthandlingstrategy
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentHandlingStrategy"))

    @content_handling_strategy.setter
    def content_handling_strategy(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "contentHandlingStrategy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateSelectionExpression")
    def template_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::IntegrationResponse.TemplateSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-templateselectionexpression
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateSelectionExpression"))

    @template_selection_expression.setter
    def template_selection_expression(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "templateSelectionExpression", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnIntegrationResponseProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "integration_id": "integrationId",
        "integration_response_key": "integrationResponseKey",
        "content_handling_strategy": "contentHandlingStrategy",
        "response_parameters": "responseParameters",
        "response_templates": "responseTemplates",
        "template_selection_expression": "templateSelectionExpression",
    },
)
class CfnIntegrationResponseProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        integration_id: builtins.str,
        integration_response_key: builtins.str,
        content_handling_strategy: typing.Optional[builtins.str] = None,
        response_parameters: typing.Any = None,
        response_templates: typing.Any = None,
        template_selection_expression: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::IntegrationResponse``.

        :param api_id: ``AWS::ApiGatewayV2::IntegrationResponse.ApiId``.
        :param integration_id: ``AWS::ApiGatewayV2::IntegrationResponse.IntegrationId``.
        :param integration_response_key: ``AWS::ApiGatewayV2::IntegrationResponse.IntegrationResponseKey``.
        :param content_handling_strategy: ``AWS::ApiGatewayV2::IntegrationResponse.ContentHandlingStrategy``.
        :param response_parameters: ``AWS::ApiGatewayV2::IntegrationResponse.ResponseParameters``.
        :param response_templates: ``AWS::ApiGatewayV2::IntegrationResponse.ResponseTemplates``.
        :param template_selection_expression: ``AWS::ApiGatewayV2::IntegrationResponse.TemplateSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "integration_id": integration_id,
            "integration_response_key": integration_response_key,
        }
        if content_handling_strategy is not None:
            self._values["content_handling_strategy"] = content_handling_strategy
        if response_parameters is not None:
            self._values["response_parameters"] = response_parameters
        if response_templates is not None:
            self._values["response_templates"] = response_templates
        if template_selection_expression is not None:
            self._values["template_selection_expression"] = template_selection_expression

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::IntegrationResponse.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def integration_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::IntegrationResponse.IntegrationId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-integrationid
        '''
        result = self._values.get("integration_id")
        assert result is not None, "Required property 'integration_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def integration_response_key(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::IntegrationResponse.IntegrationResponseKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-integrationresponsekey
        '''
        result = self._values.get("integration_response_key")
        assert result is not None, "Required property 'integration_response_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_handling_strategy(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::IntegrationResponse.ContentHandlingStrategy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-contenthandlingstrategy
        '''
        result = self._values.get("content_handling_strategy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::IntegrationResponse.ResponseParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-responseparameters
        '''
        result = self._values.get("response_parameters")
        return typing.cast(typing.Any, result)

    @builtins.property
    def response_templates(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::IntegrationResponse.ResponseTemplates``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-responsetemplates
        '''
        result = self._values.get("response_templates")
        return typing.cast(typing.Any, result)

    @builtins.property
    def template_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::IntegrationResponse.TemplateSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-templateselectionexpression
        '''
        result = self._values.get("template_selection_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnIntegrationResponseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnModel(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnModel",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::Model``.

    :cloudformationResource: AWS::ApiGatewayV2::Model
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        name: builtins.str,
        schema: typing.Any,
        content_type: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::Model``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::Model.ApiId``.
        :param name: ``AWS::ApiGatewayV2::Model.Name``.
        :param schema: ``AWS::ApiGatewayV2::Model.Schema``.
        :param content_type: ``AWS::ApiGatewayV2::Model.ContentType``.
        :param description: ``AWS::ApiGatewayV2::Model.Description``.
        '''
        props = CfnModelProps(
            api_id=api_id,
            name=name,
            schema=schema,
            content_type=content_type,
            description=description,
        )

        jsii.create(CfnModel, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Model.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Model.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Model.Schema``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-schema
        '''
        return typing.cast(typing.Any, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: typing.Any) -> None:
        jsii.set(self, "schema", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Model.ContentType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-contenttype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "contentType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Model.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnModelProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "name": "name",
        "schema": "schema",
        "content_type": "contentType",
        "description": "description",
    },
)
class CfnModelProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        name: builtins.str,
        schema: typing.Any,
        content_type: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::Model``.

        :param api_id: ``AWS::ApiGatewayV2::Model.ApiId``.
        :param name: ``AWS::ApiGatewayV2::Model.Name``.
        :param schema: ``AWS::ApiGatewayV2::Model.Schema``.
        :param content_type: ``AWS::ApiGatewayV2::Model.ContentType``.
        :param description: ``AWS::ApiGatewayV2::Model.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "name": name,
            "schema": schema,
        }
        if content_type is not None:
            self._values["content_type"] = content_type
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Model.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Model.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schema(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Model.Schema``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-schema
        '''
        result = self._values.get("schema")
        assert result is not None, "Required property 'schema' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def content_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Model.ContentType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-contenttype
        '''
        result = self._values.get("content_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Model.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnModelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnRoute(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnRoute",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::Route``.

    :cloudformationResource: AWS::ApiGatewayV2::Route
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        route_key: builtins.str,
        api_key_required: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorization_type: typing.Optional[builtins.str] = None,
        authorizer_id: typing.Optional[builtins.str] = None,
        model_selection_expression: typing.Optional[builtins.str] = None,
        operation_name: typing.Optional[builtins.str] = None,
        request_models: typing.Any = None,
        request_parameters: typing.Any = None,
        route_response_selection_expression: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::Route``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::Route.ApiId``.
        :param route_key: ``AWS::ApiGatewayV2::Route.RouteKey``.
        :param api_key_required: ``AWS::ApiGatewayV2::Route.ApiKeyRequired``.
        :param authorization_scopes: ``AWS::ApiGatewayV2::Route.AuthorizationScopes``.
        :param authorization_type: ``AWS::ApiGatewayV2::Route.AuthorizationType``.
        :param authorizer_id: ``AWS::ApiGatewayV2::Route.AuthorizerId``.
        :param model_selection_expression: ``AWS::ApiGatewayV2::Route.ModelSelectionExpression``.
        :param operation_name: ``AWS::ApiGatewayV2::Route.OperationName``.
        :param request_models: ``AWS::ApiGatewayV2::Route.RequestModels``.
        :param request_parameters: ``AWS::ApiGatewayV2::Route.RequestParameters``.
        :param route_response_selection_expression: ``AWS::ApiGatewayV2::Route.RouteResponseSelectionExpression``.
        :param target: ``AWS::ApiGatewayV2::Route.Target``.
        '''
        props = CfnRouteProps(
            api_id=api_id,
            route_key=route_key,
            api_key_required=api_key_required,
            authorization_scopes=authorization_scopes,
            authorization_type=authorization_type,
            authorizer_id=authorizer_id,
            model_selection_expression=model_selection_expression,
            operation_name=operation_name,
            request_models=request_models,
            request_parameters=request_parameters,
            route_response_selection_expression=route_response_selection_expression,
            target=target,
        )

        jsii.create(CfnRoute, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Route.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestModels")
    def request_models(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Route.RequestModels``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-requestmodels
        '''
        return typing.cast(typing.Any, jsii.get(self, "requestModels"))

    @request_models.setter
    def request_models(self, value: typing.Any) -> None:
        jsii.set(self, "requestModels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestParameters")
    def request_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Route.RequestParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-requestparameters
        '''
        return typing.cast(typing.Any, jsii.get(self, "requestParameters"))

    @request_parameters.setter
    def request_parameters(self, value: typing.Any) -> None:
        jsii.set(self, "requestParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeKey")
    def route_key(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Route.RouteKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-routekey
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeKey"))

    @route_key.setter
    def route_key(self, value: builtins.str) -> None:
        jsii.set(self, "routeKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKeyRequired")
    def api_key_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Route.ApiKeyRequired``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-apikeyrequired
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "apiKeyRequired"))

    @api_key_required.setter
    def api_key_required(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "apiKeyRequired", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizationScopes")
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::ApiGatewayV2::Route.AuthorizationScopes``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizationscopes
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "authorizationScopes"))

    @authorization_scopes.setter
    def authorization_scopes(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "authorizationScopes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizationType")
    def authorization_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.AuthorizationType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizationtype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizationType"))

    @authorization_type.setter
    def authorization_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "authorizationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.AuthorizerId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizerid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizerId"))

    @authorizer_id.setter
    def authorizer_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "authorizerId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modelSelectionExpression")
    def model_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.ModelSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-modelselectionexpression
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelSelectionExpression"))

    @model_selection_expression.setter
    def model_selection_expression(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "modelSelectionExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operationName")
    def operation_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.OperationName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-operationname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operationName"))

    @operation_name.setter
    def operation_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "operationName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeResponseSelectionExpression")
    def route_response_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.RouteResponseSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-routeresponseselectionexpression
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeResponseSelectionExpression"))

    @route_response_selection_expression.setter
    def route_response_selection_expression(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "routeResponseSelectionExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.Target``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-target
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "target"))

    @target.setter
    def target(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "target", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnRoute.ParameterConstraintsProperty",
        jsii_struct_bases=[],
        name_mapping={"required": "required"},
    )
    class ParameterConstraintsProperty:
        def __init__(
            self,
            *,
            required: typing.Union[builtins.bool, _IResolvable_da3f097b],
        ) -> None:
            '''
            :param required: ``CfnRoute.ParameterConstraintsProperty.Required``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-route-parameterconstraints.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "required": required,
            }

        @builtins.property
        def required(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnRoute.ParameterConstraintsProperty.Required``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-route-parameterconstraints.html#cfn-apigatewayv2-route-parameterconstraints-required
            '''
            result = self._values.get("required")
            assert result is not None, "Required property 'required' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ParameterConstraintsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnRouteProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "route_key": "routeKey",
        "api_key_required": "apiKeyRequired",
        "authorization_scopes": "authorizationScopes",
        "authorization_type": "authorizationType",
        "authorizer_id": "authorizerId",
        "model_selection_expression": "modelSelectionExpression",
        "operation_name": "operationName",
        "request_models": "requestModels",
        "request_parameters": "requestParameters",
        "route_response_selection_expression": "routeResponseSelectionExpression",
        "target": "target",
    },
)
class CfnRouteProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        route_key: builtins.str,
        api_key_required: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorization_type: typing.Optional[builtins.str] = None,
        authorizer_id: typing.Optional[builtins.str] = None,
        model_selection_expression: typing.Optional[builtins.str] = None,
        operation_name: typing.Optional[builtins.str] = None,
        request_models: typing.Any = None,
        request_parameters: typing.Any = None,
        route_response_selection_expression: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::Route``.

        :param api_id: ``AWS::ApiGatewayV2::Route.ApiId``.
        :param route_key: ``AWS::ApiGatewayV2::Route.RouteKey``.
        :param api_key_required: ``AWS::ApiGatewayV2::Route.ApiKeyRequired``.
        :param authorization_scopes: ``AWS::ApiGatewayV2::Route.AuthorizationScopes``.
        :param authorization_type: ``AWS::ApiGatewayV2::Route.AuthorizationType``.
        :param authorizer_id: ``AWS::ApiGatewayV2::Route.AuthorizerId``.
        :param model_selection_expression: ``AWS::ApiGatewayV2::Route.ModelSelectionExpression``.
        :param operation_name: ``AWS::ApiGatewayV2::Route.OperationName``.
        :param request_models: ``AWS::ApiGatewayV2::Route.RequestModels``.
        :param request_parameters: ``AWS::ApiGatewayV2::Route.RequestParameters``.
        :param route_response_selection_expression: ``AWS::ApiGatewayV2::Route.RouteResponseSelectionExpression``.
        :param target: ``AWS::ApiGatewayV2::Route.Target``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "route_key": route_key,
        }
        if api_key_required is not None:
            self._values["api_key_required"] = api_key_required
        if authorization_scopes is not None:
            self._values["authorization_scopes"] = authorization_scopes
        if authorization_type is not None:
            self._values["authorization_type"] = authorization_type
        if authorizer_id is not None:
            self._values["authorizer_id"] = authorizer_id
        if model_selection_expression is not None:
            self._values["model_selection_expression"] = model_selection_expression
        if operation_name is not None:
            self._values["operation_name"] = operation_name
        if request_models is not None:
            self._values["request_models"] = request_models
        if request_parameters is not None:
            self._values["request_parameters"] = request_parameters
        if route_response_selection_expression is not None:
            self._values["route_response_selection_expression"] = route_response_selection_expression
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Route.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def route_key(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Route.RouteKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-routekey
        '''
        result = self._values.get("route_key")
        assert result is not None, "Required property 'route_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_key_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Route.ApiKeyRequired``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-apikeyrequired
        '''
        result = self._values.get("api_key_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::ApiGatewayV2::Route.AuthorizationScopes``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizationscopes
        '''
        result = self._values.get("authorization_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def authorization_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.AuthorizationType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizationtype
        '''
        result = self._values.get("authorization_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorizer_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.AuthorizerId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizerid
        '''
        result = self._values.get("authorizer_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def model_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.ModelSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-modelselectionexpression
        '''
        result = self._values.get("model_selection_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operation_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.OperationName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-operationname
        '''
        result = self._values.get("operation_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_models(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Route.RequestModels``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-requestmodels
        '''
        result = self._values.get("request_models")
        return typing.cast(typing.Any, result)

    @builtins.property
    def request_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Route.RequestParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-requestparameters
        '''
        result = self._values.get("request_parameters")
        return typing.cast(typing.Any, result)

    @builtins.property
    def route_response_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.RouteResponseSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-routeresponseselectionexpression
        '''
        result = self._values.get("route_response_selection_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Route.Target``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-target
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnRouteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnRouteResponse(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnRouteResponse",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::RouteResponse``.

    :cloudformationResource: AWS::ApiGatewayV2::RouteResponse
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        route_id: builtins.str,
        route_response_key: builtins.str,
        model_selection_expression: typing.Optional[builtins.str] = None,
        response_models: typing.Any = None,
        response_parameters: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::RouteResponse``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::RouteResponse.ApiId``.
        :param route_id: ``AWS::ApiGatewayV2::RouteResponse.RouteId``.
        :param route_response_key: ``AWS::ApiGatewayV2::RouteResponse.RouteResponseKey``.
        :param model_selection_expression: ``AWS::ApiGatewayV2::RouteResponse.ModelSelectionExpression``.
        :param response_models: ``AWS::ApiGatewayV2::RouteResponse.ResponseModels``.
        :param response_parameters: ``AWS::ApiGatewayV2::RouteResponse.ResponseParameters``.
        '''
        props = CfnRouteResponseProps(
            api_id=api_id,
            route_id=route_id,
            route_response_key=route_response_key,
            model_selection_expression=model_selection_expression,
            response_models=response_models,
            response_parameters=response_parameters,
        )

        jsii.create(CfnRouteResponse, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::RouteResponse.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseModels")
    def response_models(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::RouteResponse.ResponseModels``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-responsemodels
        '''
        return typing.cast(typing.Any, jsii.get(self, "responseModels"))

    @response_models.setter
    def response_models(self, value: typing.Any) -> None:
        jsii.set(self, "responseModels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseParameters")
    def response_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::RouteResponse.ResponseParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-responseparameters
        '''
        return typing.cast(typing.Any, jsii.get(self, "responseParameters"))

    @response_parameters.setter
    def response_parameters(self, value: typing.Any) -> None:
        jsii.set(self, "responseParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeId")
    def route_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::RouteResponse.RouteId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-routeid
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeId"))

    @route_id.setter
    def route_id(self, value: builtins.str) -> None:
        jsii.set(self, "routeId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeResponseKey")
    def route_response_key(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::RouteResponse.RouteResponseKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-routeresponsekey
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeResponseKey"))

    @route_response_key.setter
    def route_response_key(self, value: builtins.str) -> None:
        jsii.set(self, "routeResponseKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modelSelectionExpression")
    def model_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::RouteResponse.ModelSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-modelselectionexpression
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelSelectionExpression"))

    @model_selection_expression.setter
    def model_selection_expression(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "modelSelectionExpression", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnRouteResponse.ParameterConstraintsProperty",
        jsii_struct_bases=[],
        name_mapping={"required": "required"},
    )
    class ParameterConstraintsProperty:
        def __init__(
            self,
            *,
            required: typing.Union[builtins.bool, _IResolvable_da3f097b],
        ) -> None:
            '''
            :param required: ``CfnRouteResponse.ParameterConstraintsProperty.Required``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-routeresponse-parameterconstraints.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "required": required,
            }

        @builtins.property
        def required(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnRouteResponse.ParameterConstraintsProperty.Required``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-routeresponse-parameterconstraints.html#cfn-apigatewayv2-routeresponse-parameterconstraints-required
            '''
            result = self._values.get("required")
            assert result is not None, "Required property 'required' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ParameterConstraintsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnRouteResponseProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "route_id": "routeId",
        "route_response_key": "routeResponseKey",
        "model_selection_expression": "modelSelectionExpression",
        "response_models": "responseModels",
        "response_parameters": "responseParameters",
    },
)
class CfnRouteResponseProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        route_id: builtins.str,
        route_response_key: builtins.str,
        model_selection_expression: typing.Optional[builtins.str] = None,
        response_models: typing.Any = None,
        response_parameters: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::RouteResponse``.

        :param api_id: ``AWS::ApiGatewayV2::RouteResponse.ApiId``.
        :param route_id: ``AWS::ApiGatewayV2::RouteResponse.RouteId``.
        :param route_response_key: ``AWS::ApiGatewayV2::RouteResponse.RouteResponseKey``.
        :param model_selection_expression: ``AWS::ApiGatewayV2::RouteResponse.ModelSelectionExpression``.
        :param response_models: ``AWS::ApiGatewayV2::RouteResponse.ResponseModels``.
        :param response_parameters: ``AWS::ApiGatewayV2::RouteResponse.ResponseParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "route_id": route_id,
            "route_response_key": route_response_key,
        }
        if model_selection_expression is not None:
            self._values["model_selection_expression"] = model_selection_expression
        if response_models is not None:
            self._values["response_models"] = response_models
        if response_parameters is not None:
            self._values["response_parameters"] = response_parameters

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::RouteResponse.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def route_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::RouteResponse.RouteId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-routeid
        '''
        result = self._values.get("route_id")
        assert result is not None, "Required property 'route_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def route_response_key(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::RouteResponse.RouteResponseKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-routeresponsekey
        '''
        result = self._values.get("route_response_key")
        assert result is not None, "Required property 'route_response_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model_selection_expression(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::RouteResponse.ModelSelectionExpression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-modelselectionexpression
        '''
        result = self._values.get("model_selection_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_models(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::RouteResponse.ResponseModels``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-responsemodels
        '''
        result = self._values.get("response_models")
        return typing.cast(typing.Any, result)

    @builtins.property
    def response_parameters(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::RouteResponse.ResponseParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-responseparameters
        '''
        result = self._values.get("response_parameters")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnRouteResponseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnStage(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnStage",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::Stage``.

    :cloudformationResource: AWS::ApiGatewayV2::Stage
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        stage_name: builtins.str,
        access_log_settings: typing.Optional[typing.Union["CfnStage.AccessLogSettingsProperty", _IResolvable_da3f097b]] = None,
        access_policy_id: typing.Optional[builtins.str] = None,
        auto_deploy: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        client_certificate_id: typing.Optional[builtins.str] = None,
        default_route_settings: typing.Optional[typing.Union["CfnStage.RouteSettingsProperty", _IResolvable_da3f097b]] = None,
        deployment_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        route_settings: typing.Any = None,
        stage_variables: typing.Any = None,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::Stage``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param api_id: ``AWS::ApiGatewayV2::Stage.ApiId``.
        :param stage_name: ``AWS::ApiGatewayV2::Stage.StageName``.
        :param access_log_settings: ``AWS::ApiGatewayV2::Stage.AccessLogSettings``.
        :param access_policy_id: ``AWS::ApiGatewayV2::Stage.AccessPolicyId``.
        :param auto_deploy: ``AWS::ApiGatewayV2::Stage.AutoDeploy``.
        :param client_certificate_id: ``AWS::ApiGatewayV2::Stage.ClientCertificateId``.
        :param default_route_settings: ``AWS::ApiGatewayV2::Stage.DefaultRouteSettings``.
        :param deployment_id: ``AWS::ApiGatewayV2::Stage.DeploymentId``.
        :param description: ``AWS::ApiGatewayV2::Stage.Description``.
        :param route_settings: ``AWS::ApiGatewayV2::Stage.RouteSettings``.
        :param stage_variables: ``AWS::ApiGatewayV2::Stage.StageVariables``.
        :param tags: ``AWS::ApiGatewayV2::Stage.Tags``.
        '''
        props = CfnStageProps(
            api_id=api_id,
            stage_name=stage_name,
            access_log_settings=access_log_settings,
            access_policy_id=access_policy_id,
            auto_deploy=auto_deploy,
            client_certificate_id=client_certificate_id,
            default_route_settings=default_route_settings,
            deployment_id=deployment_id,
            description=description,
            route_settings=route_settings,
            stage_variables=stage_variables,
            tags=tags,
        )

        jsii.create(CfnStage, self, [scope, id, props])

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
        '''``AWS::ApiGatewayV2::Stage.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Stage.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-apiid
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeSettings")
    def route_settings(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Stage.RouteSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-routesettings
        '''
        return typing.cast(typing.Any, jsii.get(self, "routeSettings"))

    @route_settings.setter
    def route_settings(self, value: typing.Any) -> None:
        jsii.set(self, "routeSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Stage.StageName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-stagename
        '''
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @stage_name.setter
    def stage_name(self, value: builtins.str) -> None:
        jsii.set(self, "stageName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageVariables")
    def stage_variables(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Stage.StageVariables``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-stagevariables
        '''
        return typing.cast(typing.Any, jsii.get(self, "stageVariables"))

    @stage_variables.setter
    def stage_variables(self, value: typing.Any) -> None:
        jsii.set(self, "stageVariables", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessLogSettings")
    def access_log_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnStage.AccessLogSettingsProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Stage.AccessLogSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-accesslogsettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnStage.AccessLogSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "accessLogSettings"))

    @access_log_settings.setter
    def access_log_settings(
        self,
        value: typing.Optional[typing.Union["CfnStage.AccessLogSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "accessLogSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPolicyId")
    def access_policy_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Stage.AccessPolicyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-accesspolicyid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessPolicyId"))

    @access_policy_id.setter
    def access_policy_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "accessPolicyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoDeploy")
    def auto_deploy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Stage.AutoDeploy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-autodeploy
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "autoDeploy"))

    @auto_deploy.setter
    def auto_deploy(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "autoDeploy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientCertificateId")
    def client_certificate_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Stage.ClientCertificateId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-clientcertificateid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientCertificateId"))

    @client_certificate_id.setter
    def client_certificate_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "clientCertificateId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRouteSettings")
    def default_route_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnStage.RouteSettingsProperty", _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Stage.DefaultRouteSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-defaultroutesettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnStage.RouteSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "defaultRouteSettings"))

    @default_route_settings.setter
    def default_route_settings(
        self,
        value: typing.Optional[typing.Union["CfnStage.RouteSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "defaultRouteSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentId")
    def deployment_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Stage.DeploymentId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-deploymentid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentId"))

    @deployment_id.setter
    def deployment_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "deploymentId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Stage.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnStage.AccessLogSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={"destination_arn": "destinationArn", "format": "format"},
    )
    class AccessLogSettingsProperty:
        def __init__(
            self,
            *,
            destination_arn: typing.Optional[builtins.str] = None,
            format: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param destination_arn: ``CfnStage.AccessLogSettingsProperty.DestinationArn``.
            :param format: ``CfnStage.AccessLogSettingsProperty.Format``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-accesslogsettings.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if destination_arn is not None:
                self._values["destination_arn"] = destination_arn
            if format is not None:
                self._values["format"] = format

        @builtins.property
        def destination_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnStage.AccessLogSettingsProperty.DestinationArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-accesslogsettings.html#cfn-apigatewayv2-stage-accesslogsettings-destinationarn
            '''
            result = self._values.get("destination_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def format(self) -> typing.Optional[builtins.str]:
            '''``CfnStage.AccessLogSettingsProperty.Format``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-accesslogsettings.html#cfn-apigatewayv2-stage-accesslogsettings-format
            '''
            result = self._values.get("format")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AccessLogSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnStage.RouteSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "data_trace_enabled": "dataTraceEnabled",
            "detailed_metrics_enabled": "detailedMetricsEnabled",
            "logging_level": "loggingLevel",
            "throttling_burst_limit": "throttlingBurstLimit",
            "throttling_rate_limit": "throttlingRateLimit",
        },
    )
    class RouteSettingsProperty:
        def __init__(
            self,
            *,
            data_trace_enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            detailed_metrics_enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            logging_level: typing.Optional[builtins.str] = None,
            throttling_burst_limit: typing.Optional[jsii.Number] = None,
            throttling_rate_limit: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param data_trace_enabled: ``CfnStage.RouteSettingsProperty.DataTraceEnabled``.
            :param detailed_metrics_enabled: ``CfnStage.RouteSettingsProperty.DetailedMetricsEnabled``.
            :param logging_level: ``CfnStage.RouteSettingsProperty.LoggingLevel``.
            :param throttling_burst_limit: ``CfnStage.RouteSettingsProperty.ThrottlingBurstLimit``.
            :param throttling_rate_limit: ``CfnStage.RouteSettingsProperty.ThrottlingRateLimit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if data_trace_enabled is not None:
                self._values["data_trace_enabled"] = data_trace_enabled
            if detailed_metrics_enabled is not None:
                self._values["detailed_metrics_enabled"] = detailed_metrics_enabled
            if logging_level is not None:
                self._values["logging_level"] = logging_level
            if throttling_burst_limit is not None:
                self._values["throttling_burst_limit"] = throttling_burst_limit
            if throttling_rate_limit is not None:
                self._values["throttling_rate_limit"] = throttling_rate_limit

        @builtins.property
        def data_trace_enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnStage.RouteSettingsProperty.DataTraceEnabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-datatraceenabled
            '''
            result = self._values.get("data_trace_enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def detailed_metrics_enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnStage.RouteSettingsProperty.DetailedMetricsEnabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-detailedmetricsenabled
            '''
            result = self._values.get("detailed_metrics_enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def logging_level(self) -> typing.Optional[builtins.str]:
            '''``CfnStage.RouteSettingsProperty.LoggingLevel``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-logginglevel
            '''
            result = self._values.get("logging_level")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def throttling_burst_limit(self) -> typing.Optional[jsii.Number]:
            '''``CfnStage.RouteSettingsProperty.ThrottlingBurstLimit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-throttlingburstlimit
            '''
            result = self._values.get("throttling_burst_limit")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def throttling_rate_limit(self) -> typing.Optional[jsii.Number]:
            '''``CfnStage.RouteSettingsProperty.ThrottlingRateLimit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-throttlingratelimit
            '''
            result = self._values.get("throttling_rate_limit")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RouteSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnStageProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_id": "apiId",
        "stage_name": "stageName",
        "access_log_settings": "accessLogSettings",
        "access_policy_id": "accessPolicyId",
        "auto_deploy": "autoDeploy",
        "client_certificate_id": "clientCertificateId",
        "default_route_settings": "defaultRouteSettings",
        "deployment_id": "deploymentId",
        "description": "description",
        "route_settings": "routeSettings",
        "stage_variables": "stageVariables",
        "tags": "tags",
    },
)
class CfnStageProps:
    def __init__(
        self,
        *,
        api_id: builtins.str,
        stage_name: builtins.str,
        access_log_settings: typing.Optional[typing.Union[CfnStage.AccessLogSettingsProperty, _IResolvable_da3f097b]] = None,
        access_policy_id: typing.Optional[builtins.str] = None,
        auto_deploy: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        client_certificate_id: typing.Optional[builtins.str] = None,
        default_route_settings: typing.Optional[typing.Union[CfnStage.RouteSettingsProperty, _IResolvable_da3f097b]] = None,
        deployment_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        route_settings: typing.Any = None,
        stage_variables: typing.Any = None,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::Stage``.

        :param api_id: ``AWS::ApiGatewayV2::Stage.ApiId``.
        :param stage_name: ``AWS::ApiGatewayV2::Stage.StageName``.
        :param access_log_settings: ``AWS::ApiGatewayV2::Stage.AccessLogSettings``.
        :param access_policy_id: ``AWS::ApiGatewayV2::Stage.AccessPolicyId``.
        :param auto_deploy: ``AWS::ApiGatewayV2::Stage.AutoDeploy``.
        :param client_certificate_id: ``AWS::ApiGatewayV2::Stage.ClientCertificateId``.
        :param default_route_settings: ``AWS::ApiGatewayV2::Stage.DefaultRouteSettings``.
        :param deployment_id: ``AWS::ApiGatewayV2::Stage.DeploymentId``.
        :param description: ``AWS::ApiGatewayV2::Stage.Description``.
        :param route_settings: ``AWS::ApiGatewayV2::Stage.RouteSettings``.
        :param stage_variables: ``AWS::ApiGatewayV2::Stage.StageVariables``.
        :param tags: ``AWS::ApiGatewayV2::Stage.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "stage_name": stage_name,
        }
        if access_log_settings is not None:
            self._values["access_log_settings"] = access_log_settings
        if access_policy_id is not None:
            self._values["access_policy_id"] = access_policy_id
        if auto_deploy is not None:
            self._values["auto_deploy"] = auto_deploy
        if client_certificate_id is not None:
            self._values["client_certificate_id"] = client_certificate_id
        if default_route_settings is not None:
            self._values["default_route_settings"] = default_route_settings
        if deployment_id is not None:
            self._values["deployment_id"] = deployment_id
        if description is not None:
            self._values["description"] = description
        if route_settings is not None:
            self._values["route_settings"] = route_settings
        if stage_variables is not None:
            self._values["stage_variables"] = stage_variables
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def api_id(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Stage.ApiId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-apiid
        '''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::Stage.StageName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-stagename
        '''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_log_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnStage.AccessLogSettingsProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Stage.AccessLogSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-accesslogsettings
        '''
        result = self._values.get("access_log_settings")
        return typing.cast(typing.Optional[typing.Union[CfnStage.AccessLogSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def access_policy_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Stage.AccessPolicyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-accesspolicyid
        '''
        result = self._values.get("access_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_deploy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Stage.AutoDeploy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-autodeploy
        '''
        result = self._values.get("auto_deploy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def client_certificate_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Stage.ClientCertificateId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-clientcertificateid
        '''
        result = self._values.get("client_certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_route_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnStage.RouteSettingsProperty, _IResolvable_da3f097b]]:
        '''``AWS::ApiGatewayV2::Stage.DefaultRouteSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-defaultroutesettings
        '''
        result = self._values.get("default_route_settings")
        return typing.cast(typing.Optional[typing.Union[CfnStage.RouteSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def deployment_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Stage.DeploymentId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-deploymentid
        '''
        result = self._values.get("deployment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::ApiGatewayV2::Stage.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_settings(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Stage.RouteSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-routesettings
        '''
        result = self._values.get("route_settings")
        return typing.cast(typing.Any, result)

    @builtins.property
    def stage_variables(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Stage.StageVariables``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-stagevariables
        '''
        result = self._values.get("stage_variables")
        return typing.cast(typing.Any, result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::Stage.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnVpcLink(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnVpcLink",
):
    '''A CloudFormation ``AWS::ApiGatewayV2::VpcLink``.

    :cloudformationResource: AWS::ApiGatewayV2::VpcLink
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::ApiGatewayV2::VpcLink``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param name: ``AWS::ApiGatewayV2::VpcLink.Name``.
        :param subnet_ids: ``AWS::ApiGatewayV2::VpcLink.SubnetIds``.
        :param security_group_ids: ``AWS::ApiGatewayV2::VpcLink.SecurityGroupIds``.
        :param tags: ``AWS::ApiGatewayV2::VpcLink.Tags``.
        '''
        props = CfnVpcLinkProps(
            name=name,
            subnet_ids=subnet_ids,
            security_group_ids=security_group_ids,
            tags=tags,
        )

        jsii.create(CfnVpcLink, self, [scope, id, props])

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
        '''``AWS::ApiGatewayV2::VpcLink.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html#cfn-apigatewayv2-vpclink-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::VpcLink.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html#cfn-apigatewayv2-vpclink-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::ApiGatewayV2::VpcLink.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html#cfn-apigatewayv2-vpclink-subnetids
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::ApiGatewayV2::VpcLink.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html#cfn-apigatewayv2-vpclink-securitygroupids
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "securityGroupIds", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_apigatewayv2.CfnVpcLinkProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "subnet_ids": "subnetIds",
        "security_group_ids": "securityGroupIds",
        "tags": "tags",
    },
)
class CfnVpcLinkProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::ApiGatewayV2::VpcLink``.

        :param name: ``AWS::ApiGatewayV2::VpcLink.Name``.
        :param subnet_ids: ``AWS::ApiGatewayV2::VpcLink.SubnetIds``.
        :param security_group_ids: ``AWS::ApiGatewayV2::VpcLink.SecurityGroupIds``.
        :param tags: ``AWS::ApiGatewayV2::VpcLink.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "subnet_ids": subnet_ids,
        }
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::ApiGatewayV2::VpcLink.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html#cfn-apigatewayv2-vpclink-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::ApiGatewayV2::VpcLink.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html#cfn-apigatewayv2-vpclink-subnetids
        '''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::ApiGatewayV2::VpcLink.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html#cfn-apigatewayv2-vpclink-securitygroupids
        '''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::ApiGatewayV2::VpcLink.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-vpclink.html#cfn-apigatewayv2-vpclink-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnVpcLinkProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnApi",
    "CfnApiGatewayManagedOverrides",
    "CfnApiGatewayManagedOverridesProps",
    "CfnApiMapping",
    "CfnApiMappingProps",
    "CfnApiProps",
    "CfnAuthorizer",
    "CfnAuthorizerProps",
    "CfnDeployment",
    "CfnDeploymentProps",
    "CfnDomainName",
    "CfnDomainNameProps",
    "CfnIntegration",
    "CfnIntegrationProps",
    "CfnIntegrationResponse",
    "CfnIntegrationResponseProps",
    "CfnModel",
    "CfnModelProps",
    "CfnRoute",
    "CfnRouteProps",
    "CfnRouteResponse",
    "CfnRouteResponseProps",
    "CfnStage",
    "CfnStageProps",
    "CfnVpcLink",
    "CfnVpcLinkProps",
]

publication.publish()
