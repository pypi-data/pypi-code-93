'''
# Endpoints for AWS Global Accelerator

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This library contains integration classes to reference endpoints in AWS
Global Accelerator. Instances of these classes should be passed to the
`endpointGroup.addEndpoint()` method.

See the README of the `@aws-cdk/aws-globalaccelerator` library for more information on
AWS Global Accelerator, and examples of all the integration classes available in
this module.
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

from ..aws_ec2 import CfnEIP as _CfnEIP_41f4ee0e, IInstance as _IInstance_3a12995c
from ..aws_elasticloadbalancingv2 import (
    IApplicationLoadBalancer as _IApplicationLoadBalancer_2b335873,
    INetworkLoadBalancer as _INetworkLoadBalancer_ead0b7fa,
)
from ..aws_globalaccelerator import IEndpoint as _IEndpoint_9178919e


@jsii.implements(_IEndpoint_9178919e)
class ApplicationLoadBalancerEndpoint(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_globalaccelerator_endpoints.ApplicationLoadBalancerEndpoint",
):
    '''(experimental) Use an Application Load Balancer as a Global Accelerator Endpoint.

    :stability: experimental
    '''

    def __init__(
        self,
        load_balancer: _IApplicationLoadBalancer_2b335873,
        *,
        preserve_client_ip: typing.Optional[builtins.bool] = None,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param load_balancer: -
        :param preserve_client_ip: (experimental) Forward the client IP address in an ``X-Forwarded-For`` header. GlobalAccelerator will create Network Interfaces in your VPC in order to preserve the client IP address. Client IP address preservation is supported only in specific AWS Regions. See the GlobalAccelerator Developer Guide for a list. Default: true if available
        :param weight: (experimental) Endpoint weight across all endpoints in the group. Must be a value between 0 and 255. Default: 128

        :stability: experimental
        '''
        options = ApplicationLoadBalancerEndpointOptions(
            preserve_client_ip=preserve_client_ip, weight=weight
        )

        jsii.create(ApplicationLoadBalancerEndpoint, self, [load_balancer, options])

    @jsii.member(jsii_name="renderEndpointConfiguration")
    def render_endpoint_configuration(self) -> typing.Any:
        '''(experimental) Render the endpoint to an endpoint configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "renderEndpointConfiguration", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region where the endpoint is located.

        If the region cannot be determined, ``undefined`` is returned

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))


@jsii.data_type(
    jsii_type="monocdk.aws_globalaccelerator_endpoints.ApplicationLoadBalancerEndpointOptions",
    jsii_struct_bases=[],
    name_mapping={"preserve_client_ip": "preserveClientIp", "weight": "weight"},
)
class ApplicationLoadBalancerEndpointOptions:
    def __init__(
        self,
        *,
        preserve_client_ip: typing.Optional[builtins.bool] = None,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties for a ApplicationLoadBalancerEndpoint.

        :param preserve_client_ip: (experimental) Forward the client IP address in an ``X-Forwarded-For`` header. GlobalAccelerator will create Network Interfaces in your VPC in order to preserve the client IP address. Client IP address preservation is supported only in specific AWS Regions. See the GlobalAccelerator Developer Guide for a list. Default: true if available
        :param weight: (experimental) Endpoint weight across all endpoints in the group. Must be a value between 0 and 255. Default: 128

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if preserve_client_ip is not None:
            self._values["preserve_client_ip"] = preserve_client_ip
        if weight is not None:
            self._values["weight"] = weight

    @builtins.property
    def preserve_client_ip(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Forward the client IP address in an ``X-Forwarded-For`` header.

        GlobalAccelerator will create Network Interfaces in your VPC in order
        to preserve the client IP address.

        Client IP address preservation is supported only in specific AWS Regions.
        See the GlobalAccelerator Developer Guide for a list.

        :default: true if available

        :stability: experimental
        '''
        result = self._values.get("preserve_client_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def weight(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Endpoint weight across all endpoints in the group.

        Must be a value between 0 and 255.

        :default: 128

        :stability: experimental
        '''
        result = self._values.get("weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationLoadBalancerEndpointOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IEndpoint_9178919e)
class CfnEipEndpoint(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_globalaccelerator_endpoints.CfnEipEndpoint",
):
    '''(experimental) Use an EC2 Instance as a Global Accelerator Endpoint.

    :stability: experimental
    '''

    def __init__(
        self,
        eip: _CfnEIP_41f4ee0e,
        *,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param eip: -
        :param weight: (experimental) Endpoint weight across all endpoints in the group. Must be a value between 0 and 255. Default: 128

        :stability: experimental
        '''
        options = CfnEipEndpointProps(weight=weight)

        jsii.create(CfnEipEndpoint, self, [eip, options])

    @jsii.member(jsii_name="renderEndpointConfiguration")
    def render_endpoint_configuration(self) -> typing.Any:
        '''(experimental) Render the endpoint to an endpoint configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "renderEndpointConfiguration", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region where the endpoint is located.

        If the region cannot be determined, ``undefined`` is returned

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))


@jsii.data_type(
    jsii_type="monocdk.aws_globalaccelerator_endpoints.CfnEipEndpointProps",
    jsii_struct_bases=[],
    name_mapping={"weight": "weight"},
)
class CfnEipEndpointProps:
    def __init__(self, *, weight: typing.Optional[jsii.Number] = None) -> None:
        '''(experimental) Properties for a NetworkLoadBalancerEndpoint.

        :param weight: (experimental) Endpoint weight across all endpoints in the group. Must be a value between 0 and 255. Default: 128

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if weight is not None:
            self._values["weight"] = weight

    @builtins.property
    def weight(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Endpoint weight across all endpoints in the group.

        Must be a value between 0 and 255.

        :default: 128

        :stability: experimental
        '''
        result = self._values.get("weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnEipEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IEndpoint_9178919e)
class InstanceEndpoint(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_globalaccelerator_endpoints.InstanceEndpoint",
):
    '''(experimental) Use an EC2 Instance as a Global Accelerator Endpoint.

    :stability: experimental
    '''

    def __init__(
        self,
        instance: _IInstance_3a12995c,
        *,
        preserve_client_ip: typing.Optional[builtins.bool] = None,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param instance: -
        :param preserve_client_ip: (experimental) Forward the client IP address. GlobalAccelerator will create Network Interfaces in your VPC in order to preserve the client IP address. Client IP address preservation is supported only in specific AWS Regions. See the GlobalAccelerator Developer Guide for a list. Default: true if available
        :param weight: (experimental) Endpoint weight across all endpoints in the group. Must be a value between 0 and 255. Default: 128

        :stability: experimental
        '''
        options = InstanceEndpointProps(
            preserve_client_ip=preserve_client_ip, weight=weight
        )

        jsii.create(InstanceEndpoint, self, [instance, options])

    @jsii.member(jsii_name="renderEndpointConfiguration")
    def render_endpoint_configuration(self) -> typing.Any:
        '''(experimental) Render the endpoint to an endpoint configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "renderEndpointConfiguration", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region where the endpoint is located.

        If the region cannot be determined, ``undefined`` is returned

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))


@jsii.data_type(
    jsii_type="monocdk.aws_globalaccelerator_endpoints.InstanceEndpointProps",
    jsii_struct_bases=[],
    name_mapping={"preserve_client_ip": "preserveClientIp", "weight": "weight"},
)
class InstanceEndpointProps:
    def __init__(
        self,
        *,
        preserve_client_ip: typing.Optional[builtins.bool] = None,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties for a NetworkLoadBalancerEndpoint.

        :param preserve_client_ip: (experimental) Forward the client IP address. GlobalAccelerator will create Network Interfaces in your VPC in order to preserve the client IP address. Client IP address preservation is supported only in specific AWS Regions. See the GlobalAccelerator Developer Guide for a list. Default: true if available
        :param weight: (experimental) Endpoint weight across all endpoints in the group. Must be a value between 0 and 255. Default: 128

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if preserve_client_ip is not None:
            self._values["preserve_client_ip"] = preserve_client_ip
        if weight is not None:
            self._values["weight"] = weight

    @builtins.property
    def preserve_client_ip(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Forward the client IP address.

        GlobalAccelerator will create Network Interfaces in your VPC in order
        to preserve the client IP address.

        Client IP address preservation is supported only in specific AWS Regions.
        See the GlobalAccelerator Developer Guide for a list.

        :default: true if available

        :stability: experimental
        '''
        result = self._values.get("preserve_client_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def weight(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Endpoint weight across all endpoints in the group.

        Must be a value between 0 and 255.

        :default: 128

        :stability: experimental
        '''
        result = self._values.get("weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IEndpoint_9178919e)
class NetworkLoadBalancerEndpoint(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_globalaccelerator_endpoints.NetworkLoadBalancerEndpoint",
):
    '''(experimental) Use a Network Load Balancer as a Global Accelerator Endpoint.

    :stability: experimental
    '''

    def __init__(
        self,
        load_balancer: _INetworkLoadBalancer_ead0b7fa,
        *,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param load_balancer: -
        :param weight: (experimental) Endpoint weight across all endpoints in the group. Must be a value between 0 and 255. Default: 128

        :stability: experimental
        '''
        options = NetworkLoadBalancerEndpointProps(weight=weight)

        jsii.create(NetworkLoadBalancerEndpoint, self, [load_balancer, options])

    @jsii.member(jsii_name="renderEndpointConfiguration")
    def render_endpoint_configuration(self) -> typing.Any:
        '''(experimental) Render the endpoint to an endpoint configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "renderEndpointConfiguration", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region where the endpoint is located.

        If the region cannot be determined, ``undefined`` is returned

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))


@jsii.data_type(
    jsii_type="monocdk.aws_globalaccelerator_endpoints.NetworkLoadBalancerEndpointProps",
    jsii_struct_bases=[],
    name_mapping={"weight": "weight"},
)
class NetworkLoadBalancerEndpointProps:
    def __init__(self, *, weight: typing.Optional[jsii.Number] = None) -> None:
        '''(experimental) Properties for a NetworkLoadBalancerEndpoint.

        :param weight: (experimental) Endpoint weight across all endpoints in the group. Must be a value between 0 and 255. Default: 128

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if weight is not None:
            self._values["weight"] = weight

    @builtins.property
    def weight(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Endpoint weight across all endpoints in the group.

        Must be a value between 0 and 255.

        :default: 128

        :stability: experimental
        '''
        result = self._values.get("weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkLoadBalancerEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApplicationLoadBalancerEndpoint",
    "ApplicationLoadBalancerEndpointOptions",
    "CfnEipEndpoint",
    "CfnEipEndpointProps",
    "InstanceEndpoint",
    "InstanceEndpointProps",
    "NetworkLoadBalancerEndpoint",
    "NetworkLoadBalancerEndpointProps",
]

publication.publish()
