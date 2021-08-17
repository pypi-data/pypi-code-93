'''
# AWS APIGatewayv2 Authorizers

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

* [Introduction](#introduction)
* [HTTP APIs](#http-apis)

  * [Default Authorization](#default-authorization)
  * [Route Authorization](#route-authorization)
* [JWT Authorizers](#jwt-authorizers)

  * [User Pool Authorizer](#user-pool-authorizer)
* [Lambda Authorizers](#lambda-authorizers)

## Introduction

API Gateway supports multiple mechanisms for controlling and managing access to your HTTP API. They are mainly
classified into Lambda Authorizers, JWT authorizers and standard AWS IAM roles and policies. More information is
available at [Controlling and managing access to an HTTP
API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control.html).

## HTTP APIs

Access control for Http Apis is managed by restricting which routes can be invoked via.

Authorizers, and scopes can either be applied to the api, or specifically for each route.

### Default Authorization

When using default authorization, all routes of the api will inherit the configuration.

In the example below, all routes will require the `manage:books` scope present in order to invoke the integration.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
authorizer = HttpJwtAuthorizer(...
)

api = HttpApi(stack, "HttpApi",
    default_authorizer=authorizer,
    default_authorization_scopes=["manage:books"]
)
```

### Route Authorization

Authorization can also configured for each Route. When a route authorization is configured, it takes precedence over default authorization.

The example below showcases default authorization, along with route authorization. It also shows how to remove authorization entirely for a route.

* `GET /books` and `GET /books/{id}` use the default authorizer settings on the api
* `POST /books` will require the [write:books] scope
* `POST /login` removes the default authorizer (unauthenticated route)

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
authorizer = HttpJwtAuthorizer(...
)

api = HttpApi(stack, "HttpApi",
    default_authorizer=authorizer,
    default_authorization_scopes=["read:books"]
)

api.add_routes(
    (SpreadAssignment ...
      path
      path), /books=,
    method="get"
)

api.add_routes(
    (SpreadAssignment ...
      path
      path), /books/{id}=,
    method="get"
)

api.add_routes(
    (SpreadAssignment ...
      path
      path), /books=,
    method="post",
    authorization_scopes=["write:books"]
)

api.add_routes(
    (SpreadAssignment ...
      path
      path), /login=,
    method="post",
    authorizer=NoneAuthorizer()
)
```

## JWT Authorizers

JWT authorizers allow the use of JSON Web Tokens (JWTs) as part of [OpenID Connect](https://openid.net/specs/openid-connect-core-1_0.html) and [OAuth 2.0](https://oauth.net/2/) frameworks to allow and restrict clients from accessing HTTP APIs.

When configured, API Gateway validates the JWT submitted by the client, and allows or denies access based on its content.

The location of the token is defined by the `identitySource` which defaults to the http `Authorization` header. However it also
[supports a number of other options](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html#http-api-lambda-authorizer.identity-sources).
It then decodes the JWT and validates the signature and claims, against the options defined in the authorizer and route (scopes).
For more information check the [JWT Authorizer documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html).

Clients that fail authorization are presented with either 2 responses:

* `401 - Unauthorized` - When the JWT validation fails
* `403 - Forbidden` - When the JWT validation is successful but the required scopes are not met

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
authorizer = HttpJwtAuthorizer(
    jwt_audience=["3131231"],
    jwt_issuer="https://test.us.auth0.com"
)

api = HttpApi(stack, "HttpApi")

api.add_routes(
    integration=HttpProxyIntegration(
        url="https://get-books-proxy.myproxy.internal"
    ),
    path="/books",
    authorizer=authorizer
)
```

### User Pool Authorizer

User Pool Authorizer is a type of JWT Authorizer that uses a Cognito user pool and app client to control who can access your Api. After a successful authorization from the app client, the generated access token will be used as the JWT.

Clients accessing an API that uses a user pool authorizer must first sign in to a user pool and obtain an identity or access token.
They must then use this token in the specified `identitySource` for the API call. More information is available at [using Amazon Cognito user
pools as authorizer](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html).

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
user_pool = UserPool(stack, "UserPool")
user_pool_client = user_pool.add_client("UserPoolClient")

authorizer = HttpUserPoolAuthorizer(
    user_pool=user_pool,
    user_pool_client=user_pool_client
)

api = HttpApi(stack, "HttpApi")

api.add_routes(
    integration=HttpProxyIntegration(
        url="https://get-books-proxy.myproxy.internal"
    ),
    path="/books",
    authorizer=authorizer
)
```

## Lambda Authorizers

Lambda authorizers use a Lambda function to control access to your HTTP API. When a client calls your API, API Gateway invokes your Lambda function and uses the response to determine whether the client can access your API.

Lambda authorizers depending on their response, fall into either two types - Simple or IAM. You can learn about differences [here](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html#http-api-lambda-authorizer.payload-format-response).

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
# This function handles your auth logic
auth_handler = Function(self, "auth-function")

authorizer = HttpLambdaAuthorizer(
    response_types=[HttpLambdaResponseType.SIMPLE], # Define if returns simple and/or iam response
    handler=auth_handler
)

api = HttpApi(stack, "HttpApi")

api.add_routes(
    integration=HttpProxyIntegration(
        url="https://get-books-proxy.myproxy.internal"
    ),
    path="/books",
    authorizer=authorizer
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

import constructs
from .. import Duration as _Duration_070aa057
from ..aws_apigatewayv2 import (
    HttpRouteAuthorizerBindOptions as _HttpRouteAuthorizerBindOptions_290d6475,
    HttpRouteAuthorizerConfig as _HttpRouteAuthorizerConfig_cd6b9e02,
    IHttpRoute as _IHttpRoute_bfbdc841,
    IHttpRouteAuthorizer as _IHttpRouteAuthorizer_717e7ba3,
)
from ..aws_cognito import (
    IUserPool as _IUserPool_5e500460, IUserPoolClient as _IUserPoolClient_4cdf19bd
)
from ..aws_lambda import IFunction as _IFunction_6e14f09e


@jsii.implements(_IHttpRouteAuthorizer_717e7ba3)
class HttpJwtAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_apigatewayv2_authorizers.HttpJwtAuthorizer",
):
    '''(experimental) Authorize Http Api routes on whether the requester is registered as part of an AWS Cognito user pool.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        jwt_audience: typing.Sequence[builtins.str],
        jwt_issuer: builtins.str,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param jwt_audience: (experimental) A list of the intended recipients of the JWT. A valid JWT must provide an aud that matches at least one entry in this list.
        :param jwt_issuer: (experimental) The base domain of the identity provider that issues JWT.
        :param authorizer_name: (experimental) The name of the authorizer. Default: 'JwtAuthorizer'
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']

        :stability: experimental
        '''
        props = HttpJwtAuthorizerProps(
            jwt_audience=jwt_audience,
            jwt_issuer=jwt_issuer,
            authorizer_name=authorizer_name,
            identity_source=identity_source,
        )

        jsii.create(HttpJwtAuthorizer, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _IHttpRoute_bfbdc841,
        scope: constructs.Construct,
    ) -> _HttpRouteAuthorizerConfig_cd6b9e02:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        options = _HttpRouteAuthorizerBindOptions_290d6475(route=route, scope=scope)

        return typing.cast(_HttpRouteAuthorizerConfig_cd6b9e02, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_authorizers.HttpJwtAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "jwt_audience": "jwtAudience",
        "jwt_issuer": "jwtIssuer",
        "authorizer_name": "authorizerName",
        "identity_source": "identitySource",
    },
)
class HttpJwtAuthorizerProps:
    def __init__(
        self,
        *,
        jwt_audience: typing.Sequence[builtins.str],
        jwt_issuer: builtins.str,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties to initialize HttpJwtAuthorizer.

        :param jwt_audience: (experimental) A list of the intended recipients of the JWT. A valid JWT must provide an aud that matches at least one entry in this list.
        :param jwt_issuer: (experimental) The base domain of the identity provider that issues JWT.
        :param authorizer_name: (experimental) The name of the authorizer. Default: 'JwtAuthorizer'
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "jwt_audience": jwt_audience,
            "jwt_issuer": jwt_issuer,
        }
        if authorizer_name is not None:
            self._values["authorizer_name"] = authorizer_name
        if identity_source is not None:
            self._values["identity_source"] = identity_source

    @builtins.property
    def jwt_audience(self) -> typing.List[builtins.str]:
        '''(experimental) A list of the intended recipients of the JWT.

        A valid JWT must provide an aud that matches at least one entry in this list.

        :stability: experimental
        '''
        result = self._values.get("jwt_audience")
        assert result is not None, "Required property 'jwt_audience' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def jwt_issuer(self) -> builtins.str:
        '''(experimental) The base domain of the identity provider that issues JWT.

        :stability: experimental
        '''
        result = self._values.get("jwt_issuer")
        assert result is not None, "Required property 'jwt_issuer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the authorizer.

        :default: 'JwtAuthorizer'

        :stability: experimental
        '''
        result = self._values.get("authorizer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The identity source for which authorization is requested.

        :default: ['$request.header.Authorization']

        :stability: experimental
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpJwtAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IHttpRouteAuthorizer_717e7ba3)
class HttpLambdaAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_apigatewayv2_authorizers.HttpLambdaAuthorizer",
):
    '''(experimental) Authorize Http Api routes via a lambda function.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        authorizer_name: builtins.str,
        handler: _IFunction_6e14f09e,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_types: typing.Optional[typing.Sequence["HttpLambdaResponseType"]] = None,
        results_cache_ttl: typing.Optional[_Duration_070aa057] = None,
    ) -> None:
        '''
        :param authorizer_name: (experimental) The name of the authorizer.
        :param handler: (experimental) The lambda function used for authorization.
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']
        :param response_types: (experimental) The types of responses the lambda can return. If HttpLambdaResponseType.SIMPLE is included then response format 2.0 will be used. Default: [HttpLambdaResponseType.IAM]
        :param results_cache_ttl: (experimental) How long APIGateway should cache the results. Max 1 hour. Disable caching by setting this to ``Duration.seconds(0)``. Default: Duration.minutes(5)

        :stability: experimental
        '''
        props = HttpLambdaAuthorizerProps(
            authorizer_name=authorizer_name,
            handler=handler,
            identity_source=identity_source,
            response_types=response_types,
            results_cache_ttl=results_cache_ttl,
        )

        jsii.create(HttpLambdaAuthorizer, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _IHttpRoute_bfbdc841,
        scope: constructs.Construct,
    ) -> _HttpRouteAuthorizerConfig_cd6b9e02:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        options = _HttpRouteAuthorizerBindOptions_290d6475(route=route, scope=scope)

        return typing.cast(_HttpRouteAuthorizerConfig_cd6b9e02, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_authorizers.HttpLambdaAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_name": "authorizerName",
        "handler": "handler",
        "identity_source": "identitySource",
        "response_types": "responseTypes",
        "results_cache_ttl": "resultsCacheTtl",
    },
)
class HttpLambdaAuthorizerProps:
    def __init__(
        self,
        *,
        authorizer_name: builtins.str,
        handler: _IFunction_6e14f09e,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_types: typing.Optional[typing.Sequence["HttpLambdaResponseType"]] = None,
        results_cache_ttl: typing.Optional[_Duration_070aa057] = None,
    ) -> None:
        '''(experimental) Properties to initialize HttpTokenAuthorizer.

        :param authorizer_name: (experimental) The name of the authorizer.
        :param handler: (experimental) The lambda function used for authorization.
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']
        :param response_types: (experimental) The types of responses the lambda can return. If HttpLambdaResponseType.SIMPLE is included then response format 2.0 will be used. Default: [HttpLambdaResponseType.IAM]
        :param results_cache_ttl: (experimental) How long APIGateway should cache the results. Max 1 hour. Disable caching by setting this to ``Duration.seconds(0)``. Default: Duration.minutes(5)

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authorizer_name": authorizer_name,
            "handler": handler,
        }
        if identity_source is not None:
            self._values["identity_source"] = identity_source
        if response_types is not None:
            self._values["response_types"] = response_types
        if results_cache_ttl is not None:
            self._values["results_cache_ttl"] = results_cache_ttl

    @builtins.property
    def authorizer_name(self) -> builtins.str:
        '''(experimental) The name of the authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorizer_name")
        assert result is not None, "Required property 'authorizer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def handler(self) -> _IFunction_6e14f09e:
        '''(experimental) The lambda function used for authorization.

        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(_IFunction_6e14f09e, result)

    @builtins.property
    def identity_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The identity source for which authorization is requested.

        :default: ['$request.header.Authorization']

        :stability: experimental
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def response_types(self) -> typing.Optional[typing.List["HttpLambdaResponseType"]]:
        '''(experimental) The types of responses the lambda can return.

        If HttpLambdaResponseType.SIMPLE is included then
        response format 2.0 will be used.

        :default: [HttpLambdaResponseType.IAM]

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html#http-api-lambda-authorizer.payload-format-response
        :stability: experimental
        '''
        result = self._values.get("response_types")
        return typing.cast(typing.Optional[typing.List["HttpLambdaResponseType"]], result)

    @builtins.property
    def results_cache_ttl(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) How long APIGateway should cache the results.

        Max 1 hour.
        Disable caching by setting this to ``Duration.seconds(0)``.

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("results_cache_ttl")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpLambdaAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_apigatewayv2_authorizers.HttpLambdaResponseType")
class HttpLambdaResponseType(enum.Enum):
    '''(experimental) Specifies the type responses the lambda returns.

    :stability: experimental
    '''

    SIMPLE = "SIMPLE"
    '''(experimental) Returns simple boolean response.

    :stability: experimental
    '''
    IAM = "IAM"
    '''(experimental) Returns an IAM Policy.

    :stability: experimental
    '''


@jsii.implements(_IHttpRouteAuthorizer_717e7ba3)
class HttpUserPoolAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_apigatewayv2_authorizers.HttpUserPoolAuthorizer",
):
    '''(experimental) Authorize Http Api routes on whether the requester is registered as part of an AWS Cognito user pool.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        user_pool: _IUserPool_5e500460,
        user_pool_client: _IUserPoolClient_4cdf19bd,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_pool_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param user_pool: (experimental) The associated user pool.
        :param user_pool_client: (experimental) The user pool client that should be used to authorize requests with the user pool.
        :param authorizer_name: (experimental) The name of the authorizer. Default: 'UserPoolAuthorizer'
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']
        :param user_pool_region: (experimental) The AWS region in which the user pool is present. Default: - same region as the Route the authorizer is attached to.

        :stability: experimental
        '''
        props = UserPoolAuthorizerProps(
            user_pool=user_pool,
            user_pool_client=user_pool_client,
            authorizer_name=authorizer_name,
            identity_source=identity_source,
            user_pool_region=user_pool_region,
        )

        jsii.create(HttpUserPoolAuthorizer, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _IHttpRoute_bfbdc841,
        scope: constructs.Construct,
    ) -> _HttpRouteAuthorizerConfig_cd6b9e02:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        options = _HttpRouteAuthorizerBindOptions_290d6475(route=route, scope=scope)

        return typing.cast(_HttpRouteAuthorizerConfig_cd6b9e02, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="monocdk.aws_apigatewayv2_authorizers.UserPoolAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "user_pool": "userPool",
        "user_pool_client": "userPoolClient",
        "authorizer_name": "authorizerName",
        "identity_source": "identitySource",
        "user_pool_region": "userPoolRegion",
    },
)
class UserPoolAuthorizerProps:
    def __init__(
        self,
        *,
        user_pool: _IUserPool_5e500460,
        user_pool_client: _IUserPoolClient_4cdf19bd,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_pool_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties to initialize UserPoolAuthorizer.

        :param user_pool: (experimental) The associated user pool.
        :param user_pool_client: (experimental) The user pool client that should be used to authorize requests with the user pool.
        :param authorizer_name: (experimental) The name of the authorizer. Default: 'UserPoolAuthorizer'
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']
        :param user_pool_region: (experimental) The AWS region in which the user pool is present. Default: - same region as the Route the authorizer is attached to.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool": user_pool,
            "user_pool_client": user_pool_client,
        }
        if authorizer_name is not None:
            self._values["authorizer_name"] = authorizer_name
        if identity_source is not None:
            self._values["identity_source"] = identity_source
        if user_pool_region is not None:
            self._values["user_pool_region"] = user_pool_region

    @builtins.property
    def user_pool(self) -> _IUserPool_5e500460:
        '''(experimental) The associated user pool.

        :stability: experimental
        '''
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(_IUserPool_5e500460, result)

    @builtins.property
    def user_pool_client(self) -> _IUserPoolClient_4cdf19bd:
        '''(experimental) The user pool client that should be used to authorize requests with the user pool.

        :stability: experimental
        '''
        result = self._values.get("user_pool_client")
        assert result is not None, "Required property 'user_pool_client' is missing"
        return typing.cast(_IUserPoolClient_4cdf19bd, result)

    @builtins.property
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the authorizer.

        :default: 'UserPoolAuthorizer'

        :stability: experimental
        '''
        result = self._values.get("authorizer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The identity source for which authorization is requested.

        :default: ['$request.header.Authorization']

        :stability: experimental
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_pool_region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS region in which the user pool is present.

        :default: - same region as the Route the authorizer is attached to.

        :stability: experimental
        '''
        result = self._values.get("user_pool_region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPoolAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HttpJwtAuthorizer",
    "HttpJwtAuthorizerProps",
    "HttpLambdaAuthorizer",
    "HttpLambdaAuthorizerProps",
    "HttpLambdaResponseType",
    "HttpUserPoolAuthorizer",
    "UserPoolAuthorizerProps",
]

publication.publish()
