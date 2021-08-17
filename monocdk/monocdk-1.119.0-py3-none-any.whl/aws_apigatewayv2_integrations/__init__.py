'''
# AWS APIGatewayv2 Integrations

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## Table of Contents

* [HTTP APIs](#http-apis)

  * [Lambda Integration](#lambda)
  * [HTTP Proxy Integration](#http-proxy)
  * [Private Integration](#private-integration)
* [WebSocket APIs](#websocket-apis)

  * [Lambda WebSocket Integration](#lambda-websocket-integration)

## HTTP APIs

Integrations connect a route to backend resources. HTTP APIs support Lambda proxy, AWS service, and HTTP proxy integrations. HTTP proxy integrations are also known as private integrations.

### Lambda

Lambda integrations enable integrating an HTTP API route with a Lambda function. When a client invokes the route, the
API Gateway service forwards the request to the Lambda function and returns the function's response to the client.

The API Gateway service will invoke the lambda function with an event payload of a specific format. The service expects
the function to respond in a specific format. The details on this format is available at [Working with AWS Lambda
proxy integrations](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html).

The following code configures a route `GET /books` with a Lambda proxy integration.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
books_fn = lambda_.Function(stack, "BooksDefaultFn", ...)
books_integration = LambdaProxyIntegration(
    handler=books_default_fn
)

http_api = HttpApi(stack, "HttpApi")

http_api.add_routes(
    path="/books",
    methods=[HttpMethod.GET],
    integration=books_integration
)
```

### HTTP Proxy

HTTP Proxy integrations enables connecting an HTTP API route to a publicly routable HTTP endpoint. When a client
invokes the route, the API Gateway service forwards the entire request and response between the API Gateway endpoint
and the integrating HTTP endpoint. More information can be found at [Working with HTTP proxy
integrations](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-http.html).

The following code configures a route `GET /books` with an HTTP proxy integration to an HTTP endpoint
`get-books-proxy.myproxy.internal`.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
books_integration = HttpProxyIntegration(
    url="https://get-books-proxy.myproxy.internal"
)

http_api = HttpApi(stack, "HttpApi")

http_api.add_routes(
    path="/books",
    methods=[HttpMethod.GET],
    integration=books_integration
)
```

### Private Integration

Private integrations enable integrating an HTTP API route with private resources in a VPC, such as Application Load Balancers or
Amazon ECS container-based applications.  Using private integrations, resources in a VPC can be exposed for access by
clients outside of the VPC.

The following integrations are supported for private resources in a VPC.

#### Application Load Balancer

The following code is a basic application load balancer private integration of HTTP API:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
vpc = ec2.Vpc(stack, "VPC")
lb = elbv2.ALB(stack, "lb", vpc=vpc)
listener = lb.add_listener("listener", port=80)
listener.add_targets("target",
    port=80
)

http_endpoint = HttpApi(stack, "HttpProxyPrivateApi",
    default_integration=HttpAlbIntegration(
        listener=listener
    )
)
```

When an imported load balancer is used, the `vpc` option must be specified for `HttpAlbIntegration`.

#### Network Load Balancer

The following code is a basic network load balancer private integration of HTTP API:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
vpc = ec2.Vpc(stack, "VPC")
lb = elbv2.NLB(stack, "lb", vpc=vpc)
listener = lb.add_listener("listener", port=80)
listener.add_targets("target",
    port=80
)

http_endpoint = HttpApi(stack, "HttpProxyPrivateApi",
    default_integration=HttpNlbIntegration(
        listener=listener
    )
)
```

When an imported load balancer is used, the `vpc` option must be specified for `HttpNlbIntegration`.

#### Cloud Map Service Discovery

The following code is a basic discovery service private integration of HTTP API:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
vpc = ec2.Vpc(stack, "VPC")
vpc_link = VpcLink(stack, "VpcLink", vpc=vpc)
namespace = servicediscovery.PrivateDnsNamespace(stack, "Namespace",
    name="boobar.com",
    vpc=vpc
)
service = namespace.create_service("Service")

http_endpoint = HttpApi(stack, "HttpProxyPrivateApi",
    default_integration=HttpServiceDiscoveryIntegration(
        vpc_link=vpc_link,
        service=service
    )
)
```

## WebSocket APIs

WebSocket integrations connect a route to backend resources. The following integrations are supported in the CDK.

### Lambda WebSocket Integration

Lambda integrations enable integrating a WebSocket API route with a Lambda function. When a client connects/disconnects
or sends message specific to a route, the API Gateway service forwards the request to the Lambda function

The API Gateway service will invoke the lambda function with an event payload of a specific format.

The following code configures a `sendmessage` route with a Lambda integration

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
web_socket_api = WebSocketApi(stack, "mywsapi")
WebSocketStage(stack, "mystage",
    web_socket_api=web_socket_api,
    stage_name="dev",
    auto_deploy=True
)

message_handler = lambda_.Function(stack, "MessageHandler", ...)
web_socket_api.add_route("sendmessage",
    integration=LambdaWebSocketIntegration(
        handler=connect_handler
    )
)
```
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

from .. import Construct as _Construct_e78e779f
from ..aws_apigatewayv2 import (
    HttpConnectionType as _HttpConnectionType_4cd688f4,
    HttpIntegrationType as _HttpIntegrationType_9cef8778,
    HttpMethod as _HttpMethod_53075460,
    HttpRouteIntegrationBindOptions as _HttpRouteIntegrationBindOptions_71d720e7,
    HttpRouteIntegrationConfig as _HttpRouteIntegrationConfig_ad0a4b4c,
    IHttpRoute as _IHttpRoute_bfbdc841,
    IHttpRouteIntegration as _IHttpRouteIntegration_152e999d,
    IVpcLink as _IVpcLink_f701d5cb,
    IWebSocketRoute as _IWebSocketRoute_bcd0851a,
    IWebSocketRouteIntegration as _IWebSocketRouteIntegration_d3bc2bf2,
    PayloadFormatVersion as _PayloadFormatVersion_63c22993,
    WebSocketRouteIntegrationBindOptions as _WebSocketRouteIntegrationBindOptions_5b8af65c,
    WebSocketRouteIntegrationConfig as _WebSocketRouteIntegrationConfig_9594a91c,
)
from ..aws_elasticloadbalancingv2 import (
    IApplicationListener as _IApplicationListener_90dffa22,
    INetworkListener as _INetworkListener_d2e2b5dc,
)
from ..aws_lambda import IFunction as _IFunction_6e14f09e
from ..aws_servicediscovery import IService as _IService_66c1fbd2


@jsii.implements(_IHttpRouteIntegration_152e999d)
class HttpAlbIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_apigatewayv2_integrations.HttpAlbIntegration",
):
    '''(experimental) The Application Load Balancer integration resource for HTTP API.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        listener: _IApplicationListener_90dffa22,
        method: typing.Optional[_HttpMethod_53075460] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_IVpcLink_f701d5cb] = None,
    ) -> None:
        '''
        :param listener: (experimental) The listener to the application load balancer used for the integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        props = HttpAlbIntegrationProps(
            listener=listener,
            method=method,
            secure_server_name=secure_server_name,
            vpc_link=vpc_link,
        )

        jsii.create(HttpAlbIntegration, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _IHttpRoute_bfbdc841,
        scope: _Construct_e78e779f,
    ) -> _HttpRouteIntegrationConfig_ad0a4b4c:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = _HttpRouteIntegrationBindOptions_71d720e7(route=route, scope=scope)

        return typing.cast(_HttpRouteIntegrationConfig_ad0a4b4c, jsii.invoke(self, "bind", [options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionType")
    def _connection_type(self) -> _HttpConnectionType_4cd688f4:
        '''
        :stability: experimental
        '''
        return typing.cast(_HttpConnectionType_4cd688f4, jsii.get(self, "connectionType"))

    @_connection_type.setter
    def _connection_type(self, value: _HttpConnectionType_4cd688f4) -> None:
        jsii.set(self, "connectionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def _http_method(self) -> _HttpMethod_53075460:
        '''
        :stability: experimental
        '''
        return typing.cast(_HttpMethod_53075460, jsii.get(self, "httpMethod"))

    @_http_method.setter
    def _http_method(self, value: _HttpMethod_53075460) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationType")
    def _integration_type(self) -> _HttpIntegrationType_9cef8778:
        '''
        :stability: experimental
        '''
        return typing.cast(_HttpIntegrationType_9cef8778, jsii.get(self, "integrationType"))

    @_integration_type.setter
    def _integration_type(self, value: _HttpIntegrationType_9cef8778) -> None:
        jsii.set(self, "integrationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadFormatVersion")
    def _payload_format_version(self) -> _PayloadFormatVersion_63c22993:
        '''
        :stability: experimental
        '''
        return typing.cast(_PayloadFormatVersion_63c22993, jsii.get(self, "payloadFormatVersion"))

    @_payload_format_version.setter
    def _payload_format_version(self, value: _PayloadFormatVersion_63c22993) -> None:
        jsii.set(self, "payloadFormatVersion", value)


@jsii.implements(_IHttpRouteIntegration_152e999d)
class HttpNlbIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_apigatewayv2_integrations.HttpNlbIntegration",
):
    '''(experimental) The Network Load Balancer integration resource for HTTP API.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        listener: _INetworkListener_d2e2b5dc,
        method: typing.Optional[_HttpMethod_53075460] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_IVpcLink_f701d5cb] = None,
    ) -> None:
        '''
        :param listener: (experimental) The listener to the network load balancer used for the integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        props = HttpNlbIntegrationProps(
            listener=listener,
            method=method,
            secure_server_name=secure_server_name,
            vpc_link=vpc_link,
        )

        jsii.create(HttpNlbIntegration, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _IHttpRoute_bfbdc841,
        scope: _Construct_e78e779f,
    ) -> _HttpRouteIntegrationConfig_ad0a4b4c:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = _HttpRouteIntegrationBindOptions_71d720e7(route=route, scope=scope)

        return typing.cast(_HttpRouteIntegrationConfig_ad0a4b4c, jsii.invoke(self, "bind", [options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionType")
    def _connection_type(self) -> _HttpConnectionType_4cd688f4:
        '''
        :stability: experimental
        '''
        return typing.cast(_HttpConnectionType_4cd688f4, jsii.get(self, "connectionType"))

    @_connection_type.setter
    def _connection_type(self, value: _HttpConnectionType_4cd688f4) -> None:
        jsii.set(self, "connectionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def _http_method(self) -> _HttpMethod_53075460:
        '''
        :stability: experimental
        '''
        return typing.cast(_HttpMethod_53075460, jsii.get(self, "httpMethod"))

    @_http_method.setter
    def _http_method(self, value: _HttpMethod_53075460) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationType")
    def _integration_type(self) -> _HttpIntegrationType_9cef8778:
        '''
        :stability: experimental
        '''
        return typing.cast(_HttpIntegrationType_9cef8778, jsii.get(self, "integrationType"))

    @_integration_type.setter
    def _integration_type(self, value: _HttpIntegrationType_9cef8778) -> None:
        jsii.set(self, "integrationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadFormatVersion")
    def _payload_format_version(self) -> _PayloadFormatVersion_63c22993:
        '''
        :stability: experimental
        '''
        return typing.cast(_PayloadFormatVersion_63c22993, jsii.get(self, "payloadFormatVersion"))

    @_payload_format_version.setter
    def _payload_format_version(self, value: _PayloadFormatVersion_63c22993) -> None:
        jsii.set(self, "payloadFormatVersion", value)


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_integrations.HttpPrivateIntegrationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "method": "method",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
    },
)
class HttpPrivateIntegrationOptions:
    def __init__(
        self,
        *,
        method: typing.Optional[_HttpMethod_53075460] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_IVpcLink_f701d5cb] = None,
    ) -> None:
        '''(experimental) Base options for private integration.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if method is not None:
            self._values["method"] = method
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(self) -> typing.Optional[_HttpMethod_53075460]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_HttpMethod_53075460], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the server name to verified by HTTPS when calling the backend integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_link(self) -> typing.Optional[_IVpcLink_f701d5cb]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[_IVpcLink_f701d5cb], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpPrivateIntegrationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IHttpRouteIntegration_152e999d)
class HttpProxyIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_apigatewayv2_integrations.HttpProxyIntegration",
):
    '''(experimental) The HTTP Proxy integration resource for HTTP API.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        url: builtins.str,
        method: typing.Optional[_HttpMethod_53075460] = None,
    ) -> None:
        '''
        :param url: (experimental) The full-qualified HTTP URL for the HTTP integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY

        :stability: experimental
        '''
        props = HttpProxyIntegrationProps(url=url, method=method)

        jsii.create(HttpProxyIntegration, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _IHttpRoute_bfbdc841,
        scope: _Construct_e78e779f,
    ) -> _HttpRouteIntegrationConfig_ad0a4b4c:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        _ = _HttpRouteIntegrationBindOptions_71d720e7(route=route, scope=scope)

        return typing.cast(_HttpRouteIntegrationConfig_ad0a4b4c, jsii.invoke(self, "bind", [_]))


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_integrations.HttpProxyIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={"url": "url", "method": "method"},
)
class HttpProxyIntegrationProps:
    def __init__(
        self,
        *,
        url: builtins.str,
        method: typing.Optional[_HttpMethod_53075460] = None,
    ) -> None:
        '''(experimental) Properties to initialize a new ``HttpProxyIntegration``.

        :param url: (experimental) The full-qualified HTTP URL for the HTTP integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }
        if method is not None:
            self._values["method"] = method

    @builtins.property
    def url(self) -> builtins.str:
        '''(experimental) The full-qualified HTTP URL for the HTTP integration.

        :stability: experimental
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def method(self) -> typing.Optional[_HttpMethod_53075460]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_HttpMethod_53075460], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpProxyIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IHttpRouteIntegration_152e999d)
class HttpServiceDiscoveryIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_apigatewayv2_integrations.HttpServiceDiscoveryIntegration",
):
    '''(experimental) The Service Discovery integration resource for HTTP API.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        service: _IService_66c1fbd2,
        method: typing.Optional[_HttpMethod_53075460] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_IVpcLink_f701d5cb] = None,
    ) -> None:
        '''
        :param service: (experimental) The discovery service used for the integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        props = HttpServiceDiscoveryIntegrationProps(
            service=service,
            method=method,
            secure_server_name=secure_server_name,
            vpc_link=vpc_link,
        )

        jsii.create(HttpServiceDiscoveryIntegration, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _IHttpRoute_bfbdc841,
        scope: _Construct_e78e779f,
    ) -> _HttpRouteIntegrationConfig_ad0a4b4c:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        _ = _HttpRouteIntegrationBindOptions_71d720e7(route=route, scope=scope)

        return typing.cast(_HttpRouteIntegrationConfig_ad0a4b4c, jsii.invoke(self, "bind", [_]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionType")
    def _connection_type(self) -> _HttpConnectionType_4cd688f4:
        '''
        :stability: experimental
        '''
        return typing.cast(_HttpConnectionType_4cd688f4, jsii.get(self, "connectionType"))

    @_connection_type.setter
    def _connection_type(self, value: _HttpConnectionType_4cd688f4) -> None:
        jsii.set(self, "connectionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def _http_method(self) -> _HttpMethod_53075460:
        '''
        :stability: experimental
        '''
        return typing.cast(_HttpMethod_53075460, jsii.get(self, "httpMethod"))

    @_http_method.setter
    def _http_method(self, value: _HttpMethod_53075460) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationType")
    def _integration_type(self) -> _HttpIntegrationType_9cef8778:
        '''
        :stability: experimental
        '''
        return typing.cast(_HttpIntegrationType_9cef8778, jsii.get(self, "integrationType"))

    @_integration_type.setter
    def _integration_type(self, value: _HttpIntegrationType_9cef8778) -> None:
        jsii.set(self, "integrationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadFormatVersion")
    def _payload_format_version(self) -> _PayloadFormatVersion_63c22993:
        '''
        :stability: experimental
        '''
        return typing.cast(_PayloadFormatVersion_63c22993, jsii.get(self, "payloadFormatVersion"))

    @_payload_format_version.setter
    def _payload_format_version(self, value: _PayloadFormatVersion_63c22993) -> None:
        jsii.set(self, "payloadFormatVersion", value)


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_integrations.HttpServiceDiscoveryIntegrationProps",
    jsii_struct_bases=[HttpPrivateIntegrationOptions],
    name_mapping={
        "method": "method",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
        "service": "service",
    },
)
class HttpServiceDiscoveryIntegrationProps(HttpPrivateIntegrationOptions):
    def __init__(
        self,
        *,
        method: typing.Optional[_HttpMethod_53075460] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_IVpcLink_f701d5cb] = None,
        service: _IService_66c1fbd2,
    ) -> None:
        '''(experimental) Properties to initialize ``HttpServiceDiscoveryIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created
        :param service: (experimental) The discovery service used for the integration.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "service": service,
        }
        if method is not None:
            self._values["method"] = method
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(self) -> typing.Optional[_HttpMethod_53075460]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_HttpMethod_53075460], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the server name to verified by HTTPS when calling the backend integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_link(self) -> typing.Optional[_IVpcLink_f701d5cb]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[_IVpcLink_f701d5cb], result)

    @builtins.property
    def service(self) -> _IService_66c1fbd2:
        '''(experimental) The discovery service used for the integration.

        :stability: experimental
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(_IService_66c1fbd2, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpServiceDiscoveryIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IHttpRouteIntegration_152e999d)
class LambdaProxyIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_apigatewayv2_integrations.LambdaProxyIntegration",
):
    '''(experimental) The Lambda Proxy integration resource for HTTP API.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        handler: _IFunction_6e14f09e,
        payload_format_version: typing.Optional[_PayloadFormatVersion_63c22993] = None,
    ) -> None:
        '''
        :param handler: (experimental) The handler for this integration.
        :param payload_format_version: (experimental) Version of the payload sent to the lambda handler. Default: PayloadFormatVersion.VERSION_2_0

        :stability: experimental
        '''
        props = LambdaProxyIntegrationProps(
            handler=handler, payload_format_version=payload_format_version
        )

        jsii.create(LambdaProxyIntegration, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _IHttpRoute_bfbdc841,
        scope: _Construct_e78e779f,
    ) -> _HttpRouteIntegrationConfig_ad0a4b4c:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = _HttpRouteIntegrationBindOptions_71d720e7(route=route, scope=scope)

        return typing.cast(_HttpRouteIntegrationConfig_ad0a4b4c, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_integrations.LambdaProxyIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={
        "handler": "handler",
        "payload_format_version": "payloadFormatVersion",
    },
)
class LambdaProxyIntegrationProps:
    def __init__(
        self,
        *,
        handler: _IFunction_6e14f09e,
        payload_format_version: typing.Optional[_PayloadFormatVersion_63c22993] = None,
    ) -> None:
        '''(experimental) Lambda Proxy integration properties.

        :param handler: (experimental) The handler for this integration.
        :param payload_format_version: (experimental) Version of the payload sent to the lambda handler. Default: PayloadFormatVersion.VERSION_2_0

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "handler": handler,
        }
        if payload_format_version is not None:
            self._values["payload_format_version"] = payload_format_version

    @builtins.property
    def handler(self) -> _IFunction_6e14f09e:
        '''(experimental) The handler for this integration.

        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(_IFunction_6e14f09e, result)

    @builtins.property
    def payload_format_version(self) -> typing.Optional[_PayloadFormatVersion_63c22993]:
        '''(experimental) Version of the payload sent to the lambda handler.

        :default: PayloadFormatVersion.VERSION_2_0

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
        :stability: experimental
        '''
        result = self._values.get("payload_format_version")
        return typing.cast(typing.Optional[_PayloadFormatVersion_63c22993], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaProxyIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IWebSocketRouteIntegration_d3bc2bf2)
class LambdaWebSocketIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_apigatewayv2_integrations.LambdaWebSocketIntegration",
):
    '''(experimental) Lambda WebSocket Integration.

    :stability: experimental
    '''

    def __init__(self, *, handler: _IFunction_6e14f09e) -> None:
        '''
        :param handler: (experimental) The handler for this integration.

        :stability: experimental
        '''
        props = LambdaWebSocketIntegrationProps(handler=handler)

        jsii.create(LambdaWebSocketIntegration, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _IWebSocketRoute_bcd0851a,
        scope: _Construct_e78e779f,
    ) -> _WebSocketRouteIntegrationConfig_9594a91c:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``WebSocketRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = _WebSocketRouteIntegrationBindOptions_5b8af65c(
            route=route, scope=scope
        )

        return typing.cast(_WebSocketRouteIntegrationConfig_9594a91c, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_integrations.LambdaWebSocketIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={"handler": "handler"},
)
class LambdaWebSocketIntegrationProps:
    def __init__(self, *, handler: _IFunction_6e14f09e) -> None:
        '''(experimental) Lambda WebSocket Integration props.

        :param handler: (experimental) The handler for this integration.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "handler": handler,
        }

    @builtins.property
    def handler(self) -> _IFunction_6e14f09e:
        '''(experimental) The handler for this integration.

        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(_IFunction_6e14f09e, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaWebSocketIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_integrations.HttpAlbIntegrationProps",
    jsii_struct_bases=[HttpPrivateIntegrationOptions],
    name_mapping={
        "method": "method",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
        "listener": "listener",
    },
)
class HttpAlbIntegrationProps(HttpPrivateIntegrationOptions):
    def __init__(
        self,
        *,
        method: typing.Optional[_HttpMethod_53075460] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_IVpcLink_f701d5cb] = None,
        listener: _IApplicationListener_90dffa22,
    ) -> None:
        '''(experimental) Properties to initialize ``HttpAlbIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created
        :param listener: (experimental) The listener to the application load balancer used for the integration.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "listener": listener,
        }
        if method is not None:
            self._values["method"] = method
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(self) -> typing.Optional[_HttpMethod_53075460]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_HttpMethod_53075460], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the server name to verified by HTTPS when calling the backend integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_link(self) -> typing.Optional[_IVpcLink_f701d5cb]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[_IVpcLink_f701d5cb], result)

    @builtins.property
    def listener(self) -> _IApplicationListener_90dffa22:
        '''(experimental) The listener to the application load balancer used for the integration.

        :stability: experimental
        '''
        result = self._values.get("listener")
        assert result is not None, "Required property 'listener' is missing"
        return typing.cast(_IApplicationListener_90dffa22, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpAlbIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_integrations.HttpNlbIntegrationProps",
    jsii_struct_bases=[HttpPrivateIntegrationOptions],
    name_mapping={
        "method": "method",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
        "listener": "listener",
    },
)
class HttpNlbIntegrationProps(HttpPrivateIntegrationOptions):
    def __init__(
        self,
        *,
        method: typing.Optional[_HttpMethod_53075460] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_IVpcLink_f701d5cb] = None,
        listener: _INetworkListener_d2e2b5dc,
    ) -> None:
        '''(experimental) Properties to initialize ``HttpNlbIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created
        :param listener: (experimental) The listener to the network load balancer used for the integration.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "listener": listener,
        }
        if method is not None:
            self._values["method"] = method
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(self) -> typing.Optional[_HttpMethod_53075460]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_HttpMethod_53075460], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the server name to verified by HTTPS when calling the backend integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_link(self) -> typing.Optional[_IVpcLink_f701d5cb]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[_IVpcLink_f701d5cb], result)

    @builtins.property
    def listener(self) -> _INetworkListener_d2e2b5dc:
        '''(experimental) The listener to the network load balancer used for the integration.

        :stability: experimental
        '''
        result = self._values.get("listener")
        assert result is not None, "Required property 'listener' is missing"
        return typing.cast(_INetworkListener_d2e2b5dc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpNlbIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HttpAlbIntegration",
    "HttpAlbIntegrationProps",
    "HttpNlbIntegration",
    "HttpNlbIntegrationProps",
    "HttpPrivateIntegrationOptions",
    "HttpProxyIntegration",
    "HttpProxyIntegrationProps",
    "HttpServiceDiscoveryIntegration",
    "HttpServiceDiscoveryIntegrationProps",
    "LambdaProxyIntegration",
    "LambdaProxyIntegrationProps",
    "LambdaWebSocketIntegration",
    "LambdaWebSocketIntegrationProps",
]

publication.publish()
