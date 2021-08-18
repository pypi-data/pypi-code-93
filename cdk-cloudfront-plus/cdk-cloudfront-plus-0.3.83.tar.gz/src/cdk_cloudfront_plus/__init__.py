'''
[![NPM version](https://badge.fury.io/js/cdk-cloudfront-plus.svg)](https://badge.fury.io/js/cdk-cloudfront-plus)
[![PyPI version](https://badge.fury.io/py/cdk-cloudfront-plus.svg)](https://badge.fury.io/py/cdk-cloudfront-plus)
![Release](https://github.com/pahud/cdk-cloudfront-plus/workflows/Release/badge.svg?branch=main)

# cdk-cloudfront-plus

CDK constructs library that allows you to build [AWS CloudFront Extensions](https://github.com/awslabs/aws-cloudfront-extensions) in **JavaScript**, **TypeScript** or **Python**.

# Sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import cdk_cloudfront_plus as cfplus

app = cdk.App()

stack = cdk.Stack(app, "demo-stack")

# prepare the `modify resonse header` extension
modify_resp_header = extensions.ModifyResponseHeader(stack, "ModifyResp")

# prepare the `anti-hotlinking` extension
anti_hotlinking = extensions.AntiHotlinking(stack, "AntiHotlink",
    referer=["example.com", "exa?ple.*"
    ]
)

# create the cloudfront distribution with extension(s)
Distribution(stack, "dist",
    default_behavior={
        "origin": origins.HttpOrigin("aws.amazon.com"),
        "edge_lambdas": [modify_resp_header, anti_hotlinking
        ]
    }
)
```

# Available Extensions in AWS CDK

| Extension Name | Category   | Solution ID   | Function/Folder Name   | Status | Contributor |
| -------------- | ---------- | ------------- | --------------------------------------- | ---| --- |
| [Access Origin by geolocation](https://github.com/pahud/cdk-cloudfront-plus/issues/41) | Origin Selection    | SO8118 | cf-access-origin-by-geolocation        | Completed | @pahud PR#52 |
| [Redirect by geolocation](https://github.com/pahud/cdk-cloudfront-plus/issues/11) | Origin Selection    | SO8135 | cf-redirect-by-geolocation        | Completed | @minche-tsai PR#50 |
| [Convert Query String](https://github.com/pahud/cdk-cloudfront-plus/issues/23) |  Override Request   | SO8113 | cf-convert-query-string        | Completed | @HsiehShuJeng PR#53 |
| [OAuth2 Authentication](https://github.com/pahud/cdk-cloudfront-plus/issues/17) |  Authentication   | SO8131 | cf-authentication-by-oauth2        | Completed | @dwchiang PR#59 |
| [Cognito Redirect](https://github.com/pahud/cdk-cloudfront-plus/issues/16) |  Authentication   | SO8132 | cf-authentication-by-cognito-redirect        | WIP(BabooPan) | - |
| [Global Data Ingestion](https://github.com/pahud/cdk-cloudfront-plus/issues/14) |  Logging   | SO8133 | cf-global-data-ingestion        | Completed | @titanjer PR#62 |
| [HTTP 302 from Origin](https://github.com/pahud/cdk-cloudfront-plus/issues/12) |  URL Redirect   | SO8103 | cf-http302-from-origin     | Completed | @RicoToothless PR#71 |
| [Default Directory Index for Amazon S3 Origin](https://github.com/pahud/cdk-cloudfront-plus/issues/9) |  URL Redirect   | SO8134 | cf-default-dir-index     | Completed | @guan840912 PR#21 |
| [Modify Response Header](https://github.com/awslabs/aws-cloudfront-extensions/tree/main/edge/nodejs/modify-response-header) |  Header Rewrite   | SO8105 | cf-modify-response-header     | Completed | @pahud PR#45 |
| [Custom Error Page](https://github.com/pahud/cdk-cloudfront-plus/pull/46)|  Header Rewrite   | SO8136 | cf-custom-error-page  | Completed | @BabooPan PR#46 |
| [Anti Hotlinking](https://github.com/awslabs/aws-cloudfront-extensions/tree/main/edge/nodejs/anti-hotlinking) |  Security   | SO8126 | cf-anti-hotlinking     | Completed | @pahud PR#2 |
| [Add Security Headers](https://github.com/awslabs/aws-cloudfront-extensions/tree/main/edge/nodejs/add-security-headers) |  Security   | SO8102 | cf-add-security-headers     | Completed | @pahud PR#7 |
| [Failover to alternative origin](https://github.com/awslabs/aws-cloudfront-extensions/tree/main/edge/nodejs/multiple-origin-IP-retry) |  Origin Selection   | SO8120 | cf-multiple-origin-ip-retry    | Completed | @guan840912 PR#58 |
| [Normalize Query String](https://github.com/pahud/cdk-cloudfront-plus/pull/64) |  Override Request   | SO8112 | cf-normalize-query-string    | Completed | @benkajaja  PR#64 |
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

import aws_cdk.aws_certificatemanager
import aws_cdk.aws_cloudfront
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.core


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.AccessOriginByGeolocationProps",
    jsii_struct_bases=[],
    name_mapping={"country_table": "countryTable"},
)
class AccessOriginByGeolocationProps:
    def __init__(
        self,
        *,
        country_table: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''
        :param country_table: The pre-defined country code table. Exampe: { 'US': 'amazon.com' }
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "country_table": country_table,
        }

    @builtins.property
    def country_table(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''The pre-defined country code table.

        Exampe: { 'US': 'amazon.com' }
        '''
        result = self._values.get("country_table")
        assert result is not None, "Required property 'country_table' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessOriginByGeolocationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.AntiHotlinkingProps",
    jsii_struct_bases=[],
    name_mapping={"referer": "referer"},
)
class AntiHotlinkingProps:
    def __init__(self, *, referer: typing.Sequence[builtins.str]) -> None:
        '''Construct properties for AntiHotlinking.

        :param referer: Referer allow list with wildcard(* and ?) support i.e. ``example.com`` or ``exa?ple.*``.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "referer": referer,
        }

    @builtins.property
    def referer(self) -> typing.List[builtins.str]:
        '''Referer allow list with wildcard(* and ?) support i.e. ``example.com`` or ``exa?ple.*``.'''
        result = self._values.get("referer")
        assert result is not None, "Required property 'referer' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AntiHotlinkingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.ConvertQueryStringProps",
    jsii_struct_bases=[],
    name_mapping={"args": "args"},
)
class ConvertQueryStringProps:
    def __init__(self, *, args: typing.Sequence[builtins.str]) -> None:
        '''keys options.

        :param args: The request arguments that will be converted to additional request headers. For example ['key1', 'key2'] will be converted to the header ``x-key1`` and ``x-key2``. Any other request arguments will not be converted.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "args": args,
        }

    @builtins.property
    def args(self) -> typing.List[builtins.str]:
        '''The request arguments that will be converted to additional request headers.

        For example ['key1', 'key2'] will be converted to the header ``x-key1`` and ``x-key2``.
        Any other request arguments will not be converted.
        '''
        result = self._values.get("args")
        assert result is not None, "Required property 'args' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConvertQueryStringProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.CustomProps",
    jsii_struct_bases=[],
    name_mapping={
        "code": "code",
        "event_type": "eventType",
        "func": "func",
        "handler": "handler",
        "include_body": "includeBody",
        "runtime": "runtime",
        "solution_id": "solutionId",
        "template_description": "templateDescription",
        "timeout": "timeout",
    },
)
class CustomProps:
    def __init__(
        self,
        *,
        code: typing.Optional[aws_cdk.aws_lambda.AssetCode] = None,
        event_type: typing.Optional[aws_cdk.aws_cloudfront.LambdaEdgeEventType] = None,
        func: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        handler: typing.Optional[builtins.str] = None,
        include_body: typing.Optional[builtins.bool] = None,
        runtime: typing.Optional[aws_cdk.aws_lambda.Runtime] = None,
        solution_id: typing.Optional[builtins.str] = None,
        template_description: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param code: The source code of your Lambda function. You can point to a file in an Amazon Simple Storage Service (Amazon S3) bucket or specify your source code as inline text. Default: Code.fromAsset(path.join(__dirname, '../lambda/function'))
        :param event_type: The type of event in response to which should the function be invoked. Default: LambdaEdgeEventType.ORIGIN_RESPONSE
        :param func: Specify your Lambda function. You can specify your Lamba function It's implement by lambda.Function, ex: NodejsFunction / PythonFunction or CustomFunction
        :param handler: The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-features.html#gettingstarted-features-programmingmodel. Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image. NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler. Default: index.lambda_handler
        :param include_body: Allows a Lambda function to have read access to the body content. Only valid for "request" event types (ORIGIN_REQUEST or VIEWER_REQUEST). Default: false
        :param runtime: The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide. Use ``Runtime.FROM_IMAGE`` when when defining a function from a Docker image. Default: Runtime.PYTHON_3_8
        :param solution_id: The solution identifier. Default: - no identifier
        :param template_description: The template description. Default: ''
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(5)
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if code is not None:
            self._values["code"] = code
        if event_type is not None:
            self._values["event_type"] = event_type
        if func is not None:
            self._values["func"] = func
        if handler is not None:
            self._values["handler"] = handler
        if include_body is not None:
            self._values["include_body"] = include_body
        if runtime is not None:
            self._values["runtime"] = runtime
        if solution_id is not None:
            self._values["solution_id"] = solution_id
        if template_description is not None:
            self._values["template_description"] = template_description
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def code(self) -> typing.Optional[aws_cdk.aws_lambda.AssetCode]:
        '''The source code of your Lambda function.

        You can point to a file in an
        Amazon Simple Storage Service (Amazon S3) bucket or specify your source
        code as inline text.

        :default: Code.fromAsset(path.join(__dirname, '../lambda/function'))
        '''
        result = self._values.get("code")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.AssetCode], result)

    @builtins.property
    def event_type(self) -> typing.Optional[aws_cdk.aws_cloudfront.LambdaEdgeEventType]:
        '''The type of event in response to which should the function be invoked.

        :default: LambdaEdgeEventType.ORIGIN_RESPONSE
        '''
        result = self._values.get("event_type")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.LambdaEdgeEventType], result)

    @builtins.property
    def func(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Specify your Lambda function.

        You can specify your Lamba function
        It's implement by lambda.Function, ex: NodejsFunction / PythonFunction or CustomFunction
        '''
        result = self._values.get("func")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def handler(self) -> typing.Optional[builtins.str]:
        '''The name of the method within your code that Lambda calls to execute your function.

        The format includes the file name. It can also include
        namespaces and other qualifiers, depending on the runtime.
        For more information, see https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-features.html#gettingstarted-features-programmingmodel.

        Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image.

        NOTE: If you specify your source code as inline text by specifying the
        ZipFile property within the Code property, specify index.function_name as
        the handler.

        :default: index.lambda_handler
        '''
        result = self._values.get("handler")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_body(self) -> typing.Optional[builtins.bool]:
        '''Allows a Lambda function to have read access to the body content.

        Only valid for "request" event types (ORIGIN_REQUEST or VIEWER_REQUEST).

        :default: false
        '''
        result = self._values.get("include_body")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def runtime(self) -> typing.Optional[aws_cdk.aws_lambda.Runtime]:
        '''The runtime environment for the Lambda function that you are uploading.

        For valid values, see the Runtime property in the AWS Lambda Developer
        Guide.

        Use ``Runtime.FROM_IMAGE`` when when defining a function from a Docker image.

        :default: Runtime.PYTHON_3_8
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Runtime], result)

    @builtins.property
    def solution_id(self) -> typing.Optional[builtins.str]:
        '''The solution identifier.

        :default: - no identifier
        '''
        result = self._values.get("solution_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template_description(self) -> typing.Optional[builtins.str]:
        '''The template description.

        :default: ''
        '''
        result = self._values.get("template_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value
        based on the function's expected execution time.

        :default: Duration.seconds(5)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Distribution(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.Distribution",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        default_behavior: aws_cdk.aws_cloudfront.BehaviorOptions,
        additional_behaviors: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions]] = None,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        comment: typing.Optional[builtins.str] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        error_responses: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.ErrorResponse]] = None,
        geo_restriction: typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction] = None,
        http_version: typing.Optional[aws_cdk.aws_cloudfront.HttpVersion] = None,
        log_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        log_file_prefix: typing.Optional[builtins.str] = None,
        log_includes_cookies: typing.Optional[builtins.bool] = None,
        minimum_protocol_version: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        price_class: typing.Optional[aws_cdk.aws_cloudfront.PriceClass] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param default_behavior: The default behavior for the distribution.
        :param additional_behaviors: Additional behaviors for the distribution, mapped by the pathPattern that specifies which requests to apply the behavior to. Default: - no additional behaviors are added.
        :param certificate: A certificate to associate with the distribution. The certificate must be located in N. Virginia (us-east-1). Default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        :param comment: Any comments you want to include about the distribution. Default: - no comment
        :param default_root_object: The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/). Default: - no default root object
        :param domain_names: Alternative domain names for this distribution. If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name, you can add an alternate domain name to your distribution. If you attach a certificate to the distribution, you must add (at least one of) the domain names of the certificate to this list. Default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        :param enabled: Enable or disable the distribution. Default: true
        :param enable_ipv6: Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address. If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses. This allows viewers to submit a second request, for an IPv4 address for your distribution. Default: true
        :param enable_logging: Enable access logging for the distribution. Default: - false, unless ``logBucket`` is specified.
        :param error_responses: How CloudFront should handle requests that are not successful (e.g., PageNotFound). Default: - No custom error responses.
        :param geo_restriction: Controls the countries in which your content is distributed. Default: - No geographic restrictions
        :param http_version: Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront. For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI). Default: HttpVersion.HTTP2
        :param log_bucket: The Amazon S3 bucket to store the access logs in. Default: - A bucket is created if ``enableLogging`` is true
        :param log_file_prefix: An optional string that you want CloudFront to prefix to the access log filenames for this distribution. Default: - no prefix
        :param log_includes_cookies: Specifies whether you want CloudFront to include cookies in access logs. Default: false
        :param minimum_protocol_version: The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: SecurityPolicyProtocol.TLS_V1_2_2019
        :param price_class: The price class that corresponds with the maximum price that you want to pay for CloudFront service. If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations. If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location that has the lowest latency among the edge locations in your price class. Default: PriceClass.PRICE_CLASS_ALL
        :param web_acl_id: Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution. To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``. Default: - No AWS Web Application Firewall web access control list (web ACL).
        '''
        props = DistributionProps(
            default_behavior=default_behavior,
            additional_behaviors=additional_behaviors,
            certificate=certificate,
            comment=comment,
            default_root_object=default_root_object,
            domain_names=domain_names,
            enabled=enabled,
            enable_ipv6=enable_ipv6,
            enable_logging=enable_logging,
            error_responses=error_responses,
            geo_restriction=geo_restriction,
            http_version=http_version,
            log_bucket=log_bucket,
            log_file_prefix=log_file_prefix,
            log_includes_cookies=log_includes_cookies,
            minimum_protocol_version=minimum_protocol_version,
            price_class=price_class,
            web_acl_id=web_acl_id,
        )

        jsii.create(Distribution, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensions")
    def extensions(self) -> typing.List["IExtensions"]:
        return typing.cast(typing.List["IExtensions"], jsii.get(self, "extensions"))


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.DistributionProps",
    jsii_struct_bases=[aws_cdk.aws_cloudfront.DistributionProps],
    name_mapping={
        "default_behavior": "defaultBehavior",
        "additional_behaviors": "additionalBehaviors",
        "certificate": "certificate",
        "comment": "comment",
        "default_root_object": "defaultRootObject",
        "domain_names": "domainNames",
        "enabled": "enabled",
        "enable_ipv6": "enableIpv6",
        "enable_logging": "enableLogging",
        "error_responses": "errorResponses",
        "geo_restriction": "geoRestriction",
        "http_version": "httpVersion",
        "log_bucket": "logBucket",
        "log_file_prefix": "logFilePrefix",
        "log_includes_cookies": "logIncludesCookies",
        "minimum_protocol_version": "minimumProtocolVersion",
        "price_class": "priceClass",
        "web_acl_id": "webAclId",
    },
)
class DistributionProps(aws_cdk.aws_cloudfront.DistributionProps):
    def __init__(
        self,
        *,
        default_behavior: aws_cdk.aws_cloudfront.BehaviorOptions,
        additional_behaviors: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions]] = None,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        comment: typing.Optional[builtins.str] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        error_responses: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.ErrorResponse]] = None,
        geo_restriction: typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction] = None,
        http_version: typing.Optional[aws_cdk.aws_cloudfront.HttpVersion] = None,
        log_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        log_file_prefix: typing.Optional[builtins.str] = None,
        log_includes_cookies: typing.Optional[builtins.bool] = None,
        minimum_protocol_version: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        price_class: typing.Optional[aws_cdk.aws_cloudfront.PriceClass] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_behavior: The default behavior for the distribution.
        :param additional_behaviors: Additional behaviors for the distribution, mapped by the pathPattern that specifies which requests to apply the behavior to. Default: - no additional behaviors are added.
        :param certificate: A certificate to associate with the distribution. The certificate must be located in N. Virginia (us-east-1). Default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        :param comment: Any comments you want to include about the distribution. Default: - no comment
        :param default_root_object: The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/). Default: - no default root object
        :param domain_names: Alternative domain names for this distribution. If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name, you can add an alternate domain name to your distribution. If you attach a certificate to the distribution, you must add (at least one of) the domain names of the certificate to this list. Default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        :param enabled: Enable or disable the distribution. Default: true
        :param enable_ipv6: Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address. If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses. This allows viewers to submit a second request, for an IPv4 address for your distribution. Default: true
        :param enable_logging: Enable access logging for the distribution. Default: - false, unless ``logBucket`` is specified.
        :param error_responses: How CloudFront should handle requests that are not successful (e.g., PageNotFound). Default: - No custom error responses.
        :param geo_restriction: Controls the countries in which your content is distributed. Default: - No geographic restrictions
        :param http_version: Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront. For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI). Default: HttpVersion.HTTP2
        :param log_bucket: The Amazon S3 bucket to store the access logs in. Default: - A bucket is created if ``enableLogging`` is true
        :param log_file_prefix: An optional string that you want CloudFront to prefix to the access log filenames for this distribution. Default: - no prefix
        :param log_includes_cookies: Specifies whether you want CloudFront to include cookies in access logs. Default: false
        :param minimum_protocol_version: The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: SecurityPolicyProtocol.TLS_V1_2_2019
        :param price_class: The price class that corresponds with the maximum price that you want to pay for CloudFront service. If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations. If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location that has the lowest latency among the edge locations in your price class. Default: PriceClass.PRICE_CLASS_ALL
        :param web_acl_id: Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution. To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``. Default: - No AWS Web Application Firewall web access control list (web ACL).
        '''
        if isinstance(default_behavior, dict):
            default_behavior = aws_cdk.aws_cloudfront.BehaviorOptions(**default_behavior)
        self._values: typing.Dict[str, typing.Any] = {
            "default_behavior": default_behavior,
        }
        if additional_behaviors is not None:
            self._values["additional_behaviors"] = additional_behaviors
        if certificate is not None:
            self._values["certificate"] = certificate
        if comment is not None:
            self._values["comment"] = comment
        if default_root_object is not None:
            self._values["default_root_object"] = default_root_object
        if domain_names is not None:
            self._values["domain_names"] = domain_names
        if enabled is not None:
            self._values["enabled"] = enabled
        if enable_ipv6 is not None:
            self._values["enable_ipv6"] = enable_ipv6
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if error_responses is not None:
            self._values["error_responses"] = error_responses
        if geo_restriction is not None:
            self._values["geo_restriction"] = geo_restriction
        if http_version is not None:
            self._values["http_version"] = http_version
        if log_bucket is not None:
            self._values["log_bucket"] = log_bucket
        if log_file_prefix is not None:
            self._values["log_file_prefix"] = log_file_prefix
        if log_includes_cookies is not None:
            self._values["log_includes_cookies"] = log_includes_cookies
        if minimum_protocol_version is not None:
            self._values["minimum_protocol_version"] = minimum_protocol_version
        if price_class is not None:
            self._values["price_class"] = price_class
        if web_acl_id is not None:
            self._values["web_acl_id"] = web_acl_id

    @builtins.property
    def default_behavior(self) -> aws_cdk.aws_cloudfront.BehaviorOptions:
        '''The default behavior for the distribution.'''
        result = self._values.get("default_behavior")
        assert result is not None, "Required property 'default_behavior' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.BehaviorOptions, result)

    @builtins.property
    def additional_behaviors(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions]]:
        '''Additional behaviors for the distribution, mapped by the pathPattern that specifies which requests to apply the behavior to.

        :default: - no additional behaviors are added.
        '''
        result = self._values.get("additional_behaviors")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions]], result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''A certificate to associate with the distribution.

        The certificate must be located in N. Virginia (us-east-1).

        :default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Any comments you want to include about the distribution.

        :default: - no comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_root_object(self) -> typing.Optional[builtins.str]:
        '''The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/).

        :default: - no default root object
        '''
        result = self._values.get("default_root_object")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Alternative domain names for this distribution.

        If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name,
        you can add an alternate domain name to your distribution. If you attach a certificate to the distribution,
        you must add (at least one of) the domain names of the certificate to this list.

        :default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        '''
        result = self._values.get("domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable or disable the distribution.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_ipv6(self) -> typing.Optional[builtins.bool]:
        '''Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address.

        If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses.
        This allows viewers to submit a second request, for an IPv4 address for your distribution.

        :default: true
        '''
        result = self._values.get("enable_ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''Enable access logging for the distribution.

        :default: - false, unless ``logBucket`` is specified.
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def error_responses(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudfront.ErrorResponse]]:
        '''How CloudFront should handle requests that are not successful (e.g., PageNotFound).

        :default: - No custom error responses.
        '''
        result = self._values.get("error_responses")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudfront.ErrorResponse]], result)

    @builtins.property
    def geo_restriction(self) -> typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction]:
        '''Controls the countries in which your content is distributed.

        :default: - No geographic restrictions
        '''
        result = self._values.get("geo_restriction")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction], result)

    @builtins.property
    def http_version(self) -> typing.Optional[aws_cdk.aws_cloudfront.HttpVersion]:
        '''Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront.

        For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI).

        :default: HttpVersion.HTTP2
        '''
        result = self._values.get("http_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.HttpVersion], result)

    @builtins.property
    def log_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''The Amazon S3 bucket to store the access logs in.

        :default: - A bucket is created if ``enableLogging`` is true
        '''
        result = self._values.get("log_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def log_file_prefix(self) -> typing.Optional[builtins.str]:
        '''An optional string that you want CloudFront to prefix to the access log filenames for this distribution.

        :default: - no prefix
        '''
        result = self._values.get("log_file_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_includes_cookies(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether you want CloudFront to include cookies in access logs.

        :default: false
        '''
        result = self._values.get("log_includes_cookies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def minimum_protocol_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol]:
        '''The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections.

        CloudFront serves your objects only to browsers or devices that support at
        least the SSL version that you specify.

        :default: SecurityPolicyProtocol.TLS_V1_2_2019
        '''
        result = self._values.get("minimum_protocol_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol], result)

    @builtins.property
    def price_class(self) -> typing.Optional[aws_cdk.aws_cloudfront.PriceClass]:
        '''The price class that corresponds with the maximum price that you want to pay for CloudFront service.

        If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations.
        If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location
        that has the lowest latency among the edge locations in your price class.

        :default: PriceClass.PRICE_CLASS_ALL
        '''
        result = self._values.get("price_class")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.PriceClass], result)

    @builtins.property
    def web_acl_id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution.

        To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example
        ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``.
        To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``.

        :default: - No AWS Web Application Firewall web access control list (web ACL).

        :see: https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CreateDistribution.html#API_CreateDistribution_RequestParameters.
        '''
        result = self._values.get("web_acl_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DistributionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.GlobalDataIngestionProps",
    jsii_struct_bases=[],
    name_mapping={"firehose_stream_name": "firehoseStreamName"},
)
class GlobalDataIngestionProps:
    def __init__(self, *, firehose_stream_name: builtins.str) -> None:
        '''
        :param firehose_stream_name: Kinesis Firehose DeliveryStreamName.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "firehose_stream_name": firehose_stream_name,
        }

    @builtins.property
    def firehose_stream_name(self) -> builtins.str:
        '''Kinesis Firehose DeliveryStreamName.'''
        result = self._values.get("firehose_stream_name")
        assert result is not None, "Required property 'firehose_stream_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlobalDataIngestionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cdk-cloudfront-plus.IExtensions")
class IExtensions(typing_extensions.Protocol):
    '''The Extension interface.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        '''The Lambda edge event type for this extension.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''Lambda function ARN for this extension.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.Version:
        '''Lambda function version for the function.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeBody")
    def include_body(self) -> typing.Optional[builtins.bool]:
        '''Allows a Lambda function to have read access to the body content.

        :default: false
        '''
        ...


class _IExtensionsProxy:
    '''The Extension interface.'''

    __jsii_type__: typing.ClassVar[str] = "cdk-cloudfront-plus.IExtensions"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        '''The Lambda edge event type for this extension.'''
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''Lambda function ARN for this extension.'''
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.Version:
        '''Lambda function version for the function.'''
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "functionVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeBody")
    def include_body(self) -> typing.Optional[builtins.bool]:
        '''Allows a Lambda function to have read access to the body content.

        :default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "includeBody"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExtensions).__jsii_proxy_class__ = lambda : _IExtensionsProxy


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.MultipleOriginIpRetryProps",
    jsii_struct_bases=[],
    name_mapping={"origin_ip": "originIp", "origin_protocol": "originProtocol"},
)
class MultipleOriginIpRetryProps:
    def __init__(
        self,
        *,
        origin_ip: typing.Sequence[builtins.str],
        origin_protocol: builtins.str,
    ) -> None:
        '''Construct properties for MultipleOriginIpRetry.

        :param origin_ip: Origin IP list for retry, use semicolon to separate multiple IP addresses.
        :param origin_protocol: Origin IP list for retry, use semicolon to separate multiple IP addresses.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "origin_ip": origin_ip,
            "origin_protocol": origin_protocol,
        }

    @builtins.property
    def origin_ip(self) -> typing.List[builtins.str]:
        '''Origin IP list for retry, use semicolon to separate multiple IP addresses.'''
        result = self._values.get("origin_ip")
        assert result is not None, "Required property 'origin_ip' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def origin_protocol(self) -> builtins.str:
        '''Origin IP list for retry, use semicolon to separate multiple IP addresses.

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            httpsorhttp
        '''
        result = self._values.get("origin_protocol")
        assert result is not None, "Required property 'origin_protocol' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MultipleOriginIpRetryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.OAuth2AuthorizationCodeGrantProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorize_params": "authorizeParams",
        "authorize_redirecturi_should_match": "authorizeRedirecturiShouldMatch",
        "authorize_url": "authorizeUrl",
        "callback_path": "callbackPath",
        "client_domain": "clientDomain",
        "client_id": "clientId",
        "client_public_key": "clientPublicKey",
        "client_secret": "clientSecret",
        "debug_enable": "debugEnable",
        "jwt_argorithm": "jwtArgorithm",
        "jwt_token_path": "jwtTokenPath",
    },
)
class OAuth2AuthorizationCodeGrantProps:
    def __init__(
        self,
        *,
        authorize_params: builtins.str,
        authorize_redirecturi_should_match: builtins.bool,
        authorize_url: builtins.str,
        callback_path: builtins.str,
        client_domain: builtins.str,
        client_id: builtins.str,
        client_public_key: builtins.str,
        client_secret: builtins.str,
        debug_enable: builtins.bool,
        jwt_argorithm: builtins.str,
        jwt_token_path: builtins.str,
    ) -> None:
        '''
        :param authorize_params: 
        :param authorize_redirecturi_should_match: 
        :param authorize_url: 
        :param callback_path: 
        :param client_domain: 
        :param client_id: 
        :param client_public_key: 
        :param client_secret: 
        :param debug_enable: 
        :param jwt_argorithm: 
        :param jwt_token_path: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authorize_params": authorize_params,
            "authorize_redirecturi_should_match": authorize_redirecturi_should_match,
            "authorize_url": authorize_url,
            "callback_path": callback_path,
            "client_domain": client_domain,
            "client_id": client_id,
            "client_public_key": client_public_key,
            "client_secret": client_secret,
            "debug_enable": debug_enable,
            "jwt_argorithm": jwt_argorithm,
            "jwt_token_path": jwt_token_path,
        }

    @builtins.property
    def authorize_params(self) -> builtins.str:
        result = self._values.get("authorize_params")
        assert result is not None, "Required property 'authorize_params' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorize_redirecturi_should_match(self) -> builtins.bool:
        result = self._values.get("authorize_redirecturi_should_match")
        assert result is not None, "Required property 'authorize_redirecturi_should_match' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def authorize_url(self) -> builtins.str:
        result = self._values.get("authorize_url")
        assert result is not None, "Required property 'authorize_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def callback_path(self) -> builtins.str:
        result = self._values.get("callback_path")
        assert result is not None, "Required property 'callback_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_domain(self) -> builtins.str:
        result = self._values.get("client_domain")
        assert result is not None, "Required property 'client_domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_id(self) -> builtins.str:
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_public_key(self) -> builtins.str:
        result = self._values.get("client_public_key")
        assert result is not None, "Required property 'client_public_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_secret(self) -> builtins.str:
        result = self._values.get("client_secret")
        assert result is not None, "Required property 'client_secret' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def debug_enable(self) -> builtins.bool:
        result = self._values.get("debug_enable")
        assert result is not None, "Required property 'debug_enable' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def jwt_argorithm(self) -> builtins.str:
        result = self._values.get("jwt_argorithm")
        assert result is not None, "Required property 'jwt_argorithm' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def jwt_token_path(self) -> builtins.str:
        result = self._values.get("jwt_token_path")
        assert result is not None, "Required property 'jwt_token_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OAuth2AuthorizationCodeGrantProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.RedirectByGeolocationProps",
    jsii_struct_bases=[],
    name_mapping={"country_table": "countryTable"},
)
class RedirectByGeolocationProps:
    def __init__(
        self,
        *,
        country_table: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''
        :param country_table: The pre-defined country code table. Exampe: { 'US': 'amazon.com' }
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "country_table": country_table,
        }

    @builtins.property
    def country_table(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''The pre-defined country code table.

        Exampe: { 'US': 'amazon.com' }
        '''
        result = self._values.get("country_table")
        assert result is not None, "Required property 'country_table' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedirectByGeolocationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServerlessApp(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.ServerlessApp",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        application_id: builtins.str,
        semantic_version: builtins.str,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application_id: 
        :param semantic_version: 
        :param parameters: The parameters for the ServerlessApp.
        '''
        props = ServerlessAppProps(
            application_id=application_id,
            semantic_version=semantic_version,
            parameters=parameters,
        )

        jsii.create(ServerlessApp, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> aws_cdk.core.CfnResource:
        return typing.cast(aws_cdk.core.CfnResource, jsii.get(self, "resource"))


@jsii.data_type(
    jsii_type="cdk-cloudfront-plus.ServerlessAppProps",
    jsii_struct_bases=[],
    name_mapping={
        "application_id": "applicationId",
        "semantic_version": "semanticVersion",
        "parameters": "parameters",
    },
)
class ServerlessAppProps:
    def __init__(
        self,
        *,
        application_id: builtins.str,
        semantic_version: builtins.str,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Construct properties for ServerlessApp.

        :param application_id: 
        :param semantic_version: 
        :param parameters: The parameters for the ServerlessApp.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "application_id": application_id,
            "semantic_version": semantic_version,
        }
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def application_id(self) -> builtins.str:
        result = self._values.get("application_id")
        assert result is not None, "Required property 'application_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def semantic_version(self) -> builtins.str:
        result = self._values.get("semantic_version")
        assert result is not None, "Required property 'semantic_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The parameters for the ServerlessApp.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerlessAppProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IExtensions)
class AntiHotlinking(
    ServerlessApp,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.AntiHotlinking",
):
    '''The Anti-Hotlinking extension.

    :see: https://console.aws.amazon.com/lambda/home#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:418289889111:applications/anti-hotlinking
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        referer: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param referer: Referer allow list with wildcard(* and ?) support i.e. ``example.com`` or ``exa?ple.*``.
        '''
        props = AntiHotlinkingProps(referer=referer)

        jsii.create(AntiHotlinking, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        '''The Lambda edge event type for this extension.'''
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''Lambda function ARN for this extension.'''
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.Version:
        '''Lambda function version for the function.'''
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "functionVersion"))


@jsii.implements(IExtensions)
class Custom(
    aws_cdk.core.NestedStack,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.Custom",
):
    '''Custom extension sample.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        code: typing.Optional[aws_cdk.aws_lambda.AssetCode] = None,
        event_type: typing.Optional[aws_cdk.aws_cloudfront.LambdaEdgeEventType] = None,
        func: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        handler: typing.Optional[builtins.str] = None,
        include_body: typing.Optional[builtins.bool] = None,
        runtime: typing.Optional[aws_cdk.aws_lambda.Runtime] = None,
        solution_id: typing.Optional[builtins.str] = None,
        template_description: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code: The source code of your Lambda function. You can point to a file in an Amazon Simple Storage Service (Amazon S3) bucket or specify your source code as inline text. Default: Code.fromAsset(path.join(__dirname, '../lambda/function'))
        :param event_type: The type of event in response to which should the function be invoked. Default: LambdaEdgeEventType.ORIGIN_RESPONSE
        :param func: Specify your Lambda function. You can specify your Lamba function It's implement by lambda.Function, ex: NodejsFunction / PythonFunction or CustomFunction
        :param handler: The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-features.html#gettingstarted-features-programmingmodel. Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image. NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler. Default: index.lambda_handler
        :param include_body: Allows a Lambda function to have read access to the body content. Only valid for "request" event types (ORIGIN_REQUEST or VIEWER_REQUEST). Default: false
        :param runtime: The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide. Use ``Runtime.FROM_IMAGE`` when when defining a function from a Docker image. Default: Runtime.PYTHON_3_8
        :param solution_id: The solution identifier. Default: - no identifier
        :param template_description: The template description. Default: ''
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(5)
        '''
        props = CustomProps(
            code=code,
            event_type=event_type,
            func=func,
            handler=handler,
            include_body=include_body,
            runtime=runtime,
            solution_id=solution_id,
            template_description=template_description,
            timeout=timeout,
        )

        jsii.create(Custom, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        '''The Lambda edge event type for this extension.'''
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''Lambda function ARN for this extension.'''
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.Version:
        '''Lambda function version for the function.'''
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "functionVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> CustomProps:
        return typing.cast(CustomProps, jsii.get(self, "props"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeBody")
    def include_body(self) -> typing.Optional[builtins.bool]:
        '''Allows a Lambda function to have read access to the body content.'''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "includeBody"))


class CustomErrorPage(
    Custom,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.CustomErrorPage",
):
    '''Display customized error pages, or mask 4XX error pages, based on where the error originated.

    use case - see https://aws.amazon.com/blogs/networking-and-content-delivery/customize-403-error-pages-from-amazon-cloudfront-origin-with-lambdaedge/
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(CustomErrorPage, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Version:
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "lambdaFunction"))


class DefaultDirIndex(
    Custom,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.DefaultDirIndex",
):
    '''Default Directory Indexes in Amazon S3-backed Amazon CloudFront Origins.

    use case - see https://aws.amazon.com/tw/blogs/compute/implementing-default-directory-indexes-in-amazon-s3-backed-amazon-cloudfront-origins-using-lambdaedge/
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(DefaultDirIndex, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Version:
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "lambdaFunction"))


class GlobalDataIngestion(
    Custom,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.GlobalDataIngestion",
):
    '''Ingest data to Kinesis Firehose by nearest cloudfront edge.

    :see: https://aws.amazon.com/blogs/networking-and-content-delivery/global-data-ingestion-with-amazon-cloudfront-and-lambdaedge/
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        firehose_stream_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param firehose_stream_name: Kinesis Firehose DeliveryStreamName.
        '''
        props = GlobalDataIngestionProps(firehose_stream_name=firehose_stream_name)

        jsii.create(GlobalDataIngestion, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Version:
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "lambdaFunction"))


class HTTP302FromOrigin(
    Custom,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.HTTP302FromOrigin",
):
    '''The HTTP[302] from origin extension.

    :see: https://console.aws.amazon.com/lambda/home#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:418289889111:applications/http302-from-origin
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(HTTP302FromOrigin, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Version:
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "lambdaFunction"))


@jsii.implements(IExtensions)
class ModifyResponseHeader(
    ServerlessApp,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.ModifyResponseHeader",
):
    '''The modify response header extension.

    :see: https://console.aws.amazon.com/lambda/home#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:418289889111:applications/modify-response-header
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(ModifyResponseHeader, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        '''The Lambda edge event type for this extension.'''
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''Lambda function ARN for this extension.'''
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.Version:
        '''Lambda function version for the function.'''
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "functionVersion"))


@jsii.implements(IExtensions)
class MultipleOriginIpRetry(
    ServerlessApp,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.MultipleOriginIpRetry",
):
    '''Multiple Origin IP Retry extension.

    :see: https://github.com/awslabs/aws-cloudfront-extensions/tree/main/edge/nodejs/multiple-origin-IP-retry
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        origin_ip: typing.Sequence[builtins.str],
        origin_protocol: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param origin_ip: Origin IP list for retry, use semicolon to separate multiple IP addresses.
        :param origin_protocol: Origin IP list for retry, use semicolon to separate multiple IP addresses.
        '''
        props = MultipleOriginIpRetryProps(
            origin_ip=origin_ip, origin_protocol=origin_protocol
        )

        jsii.create(MultipleOriginIpRetry, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        '''The Lambda edge event type for this extension.'''
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''Lambda function ARN for this extension.'''
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.Version:
        '''Lambda function version for the function.'''
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "functionVersion"))


@jsii.implements(IExtensions)
class NormalizeQueryString(
    ServerlessApp,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.NormalizeQueryString",
):
    '''Normalize Query String extension.

    :see: https://github.com/awslabs/aws-cloudfront-extensions/tree/main/edge/nodejs/normalize-query-string
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(NormalizeQueryString, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        '''The Lambda edge event type for this extension.'''
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''Lambda function ARN for this extension.'''
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.Version:
        '''Lambda function version for the function.'''
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "functionVersion"))


class OAuth2AuthorizationCodeGrant(
    Custom,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.OAuth2AuthorizationCodeGrant",
):
    '''OAuth2 Authentication - Authorization Code Grant.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        authorize_params: builtins.str,
        authorize_redirecturi_should_match: builtins.bool,
        authorize_url: builtins.str,
        callback_path: builtins.str,
        client_domain: builtins.str,
        client_id: builtins.str,
        client_public_key: builtins.str,
        client_secret: builtins.str,
        debug_enable: builtins.bool,
        jwt_argorithm: builtins.str,
        jwt_token_path: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param authorize_params: 
        :param authorize_redirecturi_should_match: 
        :param authorize_url: 
        :param callback_path: 
        :param client_domain: 
        :param client_id: 
        :param client_public_key: 
        :param client_secret: 
        :param debug_enable: 
        :param jwt_argorithm: 
        :param jwt_token_path: 
        '''
        props = OAuth2AuthorizationCodeGrantProps(
            authorize_params=authorize_params,
            authorize_redirecturi_should_match=authorize_redirecturi_should_match,
            authorize_url=authorize_url,
            callback_path=callback_path,
            client_domain=client_domain,
            client_id=client_id,
            client_public_key=client_public_key,
            client_secret=client_secret,
            debug_enable=debug_enable,
            jwt_argorithm=jwt_argorithm,
            jwt_token_path=jwt_token_path,
        )

        jsii.create(OAuth2AuthorizationCodeGrant, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Version:
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "lambdaFunction"))


class RedirectByGeolocation(
    Custom,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.RedirectByGeolocation",
):
    '''Forward request to the nearest PoP as per geolocation.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        country_table: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param country_table: The pre-defined country code table. Exampe: { 'US': 'amazon.com' }
        '''
        props = RedirectByGeolocationProps(country_table=country_table)

        jsii.create(RedirectByGeolocation, self, [scope, id, props])


@jsii.implements(IExtensions)
class SecurtyHeaders(
    ServerlessApp,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.SecurtyHeaders",
):
    '''Security Headers extension.

    :see: https://aws.amazon.com/tw/blogs/networking-and-content-delivery/adding-http-security-headers-using-lambdaedge-and-amazon-cloudfront/
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(SecurtyHeaders, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        '''The Lambda edge event type for this extension.'''
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''Lambda function ARN for this extension.'''
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.Version:
        '''Lambda function version for the function.'''
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "functionVersion"))


class SimpleLambdaEdge(
    Custom,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.SimpleLambdaEdge",
):
    '''Simple content generation.

    :see: https://github.com/awslabs/aws-cloudfront-extensions/tree/main/edge/nodejs/simple-lambda-edge
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(SimpleLambdaEdge, self, [scope, id])


class AccessOriginByGeolocation(
    Custom,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.AccessOriginByGeolocation",
):
    '''(SO8118)Access Origin by Geolocation.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        country_table: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param country_table: The pre-defined country code table. Exampe: { 'US': 'amazon.com' }
        '''
        props = AccessOriginByGeolocationProps(country_table=country_table)

        jsii.create(AccessOriginByGeolocation, self, [scope, id, props])


class ConvertQueryString(
    Custom,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cloudfront-plus.ConvertQueryString",
):
    '''Convert a query string to key-value pairs and add them into header.

    :see: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-examples.html#lambda-examples-header-based-on-query-string
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        args: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param args: The request arguments that will be converted to additional request headers. For example ['key1', 'key2'] will be converted to the header ``x-key1`` and ``x-key2``. Any other request arguments will not be converted.
        '''
        props = ConvertQueryStringProps(args=args)

        jsii.create(ConvertQueryString, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Version:
        return typing.cast(aws_cdk.aws_lambda.Version, jsii.get(self, "lambdaFunction"))


__all__ = [
    "AccessOriginByGeolocation",
    "AccessOriginByGeolocationProps",
    "AntiHotlinking",
    "AntiHotlinkingProps",
    "ConvertQueryString",
    "ConvertQueryStringProps",
    "Custom",
    "CustomErrorPage",
    "CustomProps",
    "DefaultDirIndex",
    "Distribution",
    "DistributionProps",
    "GlobalDataIngestion",
    "GlobalDataIngestionProps",
    "HTTP302FromOrigin",
    "IExtensions",
    "ModifyResponseHeader",
    "MultipleOriginIpRetry",
    "MultipleOriginIpRetryProps",
    "NormalizeQueryString",
    "OAuth2AuthorizationCodeGrant",
    "OAuth2AuthorizationCodeGrantProps",
    "RedirectByGeolocation",
    "RedirectByGeolocationProps",
    "SecurtyHeaders",
    "ServerlessApp",
    "ServerlessAppProps",
    "SimpleLambdaEdge",
]

publication.publish()
