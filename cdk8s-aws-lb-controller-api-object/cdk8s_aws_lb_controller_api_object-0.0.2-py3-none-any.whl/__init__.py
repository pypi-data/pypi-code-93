'''
# cdk8s-aws-lb-controller-api-object

![Release](https://github.com/opencdk8s/cdk8s-aws-lb-controller-api-object/workflows/Release/badge.svg?branch=development)
[![npm version](https://badge.fury.io/js/%40opencdk8s%2Fcdk8s-aws-lb-controller-api-object.svg)](https://badge.fury.io/js/%40opencdk8s%2Fcdk8s-aws-lb-controller-api-object)
[![PyPI version](https://badge.fury.io/py/cdk8s-aws-lb-controller-api-object.svg)](https://badge.fury.io/py/cdk8s-aws-lb-controller-api-object)
![npm](https://img.shields.io/npm/dt/@opencdk8s/cdk8s-aws-lb-controller-api-object?label=npm&color=green)

API Object for AWS Load Balancer Controller, powered by the [cdk8s project](https://cdk8s.io) and [aws-load-balancer-controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller)  🚀

## Overview

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from constructs import Construct
from cdk8s import App, Chart, ChartProps
from opencdk8s.cdk8s_aws_lb_controller_api_object import AWSLoadBalancerControllerObject

class MyChart(Chart):
    def __init__(self, scope, id, *, namespace=None, labels=None):
        super().__init__(scope, id, namespace=namespace, labels=labels)
        AWSLoadBalancerControllerObject(self, "example",
            metadata={
                "annotations": {
                    "kubernetes.io/ingress.class": "alb"
                }
            },
            spec={
                "rules": [{
                    "host": "example.com",
                    "http": {
                        "paths": [{
                            "path": "/*",
                            "backend": {
                                "service_name": "helloworld-svc",
                                "service_port": 80
                            }
                        }]
                    }
                }]
            }
        )

app = App()
MyChart(app, "example1")
app.synth()
```

Example `cdk8s synth` manifest as follows.

<details>
<summary>manifest.k8s.yaml</summary>

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: alb
  name: example-c89c1904
spec:
  rules:
    - host: example.com
      http:
        paths:
          - backend:
              serviceName: helloworld-svc
              servicePort: 80
            path: /*


```

</details>

## Installation

### TypeScript

Use `yarn` or `npm` to install.

```sh
$ npm install @opencdk8s/cdk8s-aws-lb-controller-api-objects
```

```sh
$ yarn add @opencdk8s/cdk8s-aws-lb-controller-api-objects
```

### Python

```sh
$ pip install cdk8s-aws-lb-controller-api-objects
```

## Contribution

1. Fork ([link](https://github.com/opencdk8s/cdk8s-aws-lb-controller-api-objects/fork))
2. Bootstrap the repo:

   ```bash
   yarn install # installs dependencies
   yarn projen
   ```
3. Development scripts:
   |Command|Description
   |-|-
   |`yarn compile`|Compiles typescript => javascript
   |`yarn watch`|Watch & compile
   |`yarn test`|Run unit test & linter through jest
   |`yarn test -u`|Update jest snapshots
   |`yarn run package`|Creates a `dist` with packages for all languages.
   |`yarn build`|Compile + test + package
   |`yarn bump`|Bump version (with changelog) based on [conventional commits]
   |`yarn release`|Bump + push to `master`
4. Create a feature branch
5. Commit your changes
6. Rebase your local changes against the master branch
7. Create a new Pull Request (use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) for the title please)

## Licence

[Apache License, Version 2.0](./LICENSE)

## Author

[Hunter-Thompson](https://github.com/Hunter-Thompson)
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

import cdk8s
import constructs


class AWSLoadBalancerControllerObject(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.AWSLoadBalancerControllerObject",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        metadata: typing.Optional["ObjectMeta"] = None,
        spec: typing.Optional["IngressSpec"] = None,
    ) -> None:
        '''(experimental) Defines an "extentions" API object for AWS Load Balancer Controller - https://github.com/kubernetes-sigs/aws-load-balancer-controller.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param metadata: (experimental) Standard object's metadata.
        :param spec: (experimental) Spec defines the behavior of the ingress.

        :stability: experimental
        '''
        props = AWSLoadBalancerControllerProps(metadata=metadata, spec=spec)

        jsii.create(AWSLoadBalancerControllerObject, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        metadata: typing.Optional["ObjectMeta"] = None,
        spec: typing.Optional["IngressSpec"] = None,
    ) -> typing.Any:
        '''(experimental) Renders a Kubernetes manifest for an ingress object. https://github.com/kubernetes-sigs/aws-load-balancer-controller.

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param metadata: (experimental) Standard object's metadata.
        :param spec: (experimental) Spec defines the behavior of the ingress.

        :stability: experimental
        '''
        props = AWSLoadBalancerControllerProps(metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''
        :stability: experimental
        '''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.AWSLoadBalancerControllerProps",
    jsii_struct_bases=[],
    name_mapping={"metadata": "metadata", "spec": "spec"},
)
class AWSLoadBalancerControllerProps:
    def __init__(
        self,
        *,
        metadata: typing.Optional["ObjectMeta"] = None,
        spec: typing.Optional["IngressSpec"] = None,
    ) -> None:
        '''
        :param metadata: (experimental) Standard object's metadata.
        :param spec: (experimental) Spec defines the behavior of the ingress.

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = ObjectMeta(**metadata)
        if isinstance(spec, dict):
            spec = IngressSpec(**spec)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def metadata(self) -> typing.Optional["ObjectMeta"]:
        '''(experimental) Standard object's metadata.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional["ObjectMeta"], result)

    @builtins.property
    def spec(self) -> typing.Optional["IngressSpec"]:
        '''(experimental) Spec defines the behavior of the ingress.

        :stability: experimental
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Optional["IngressSpec"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AWSLoadBalancerControllerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.HttpIngressPath",
    jsii_struct_bases=[],
    name_mapping={"backend": "backend", "path": "path"},
)
class HttpIngressPath:
    def __init__(
        self,
        *,
        backend: "IngressBackend",
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) HTTPIngressPath associates a path regex with a backend.

        Incoming urls matching the path are forwarded to the backend.

        :param backend: (experimental) Backend defines the referenced service endpoint to which the traffic will be forwarded to.
        :param path: (experimental) Path is an extended POSIX regex as defined by IEEE Std 1003.1, (i.e this follows the egrep/unix syntax, not the perl syntax) matched against the path of an incoming request. Currently it can contain characters disallowed from the conventional "path" part of a URL as defined by RFC 3986. Paths must begin with a '/'. If unspecified, the path defaults to a catch all sending traffic to the backend.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.HTTPIngressPath
        '''
        if isinstance(backend, dict):
            backend = IngressBackend(**backend)
        self._values: typing.Dict[str, typing.Any] = {
            "backend": backend,
        }
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def backend(self) -> "IngressBackend":
        '''(experimental) Backend defines the referenced service endpoint to which the traffic will be forwarded to.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.HTTPIngressPath#backend
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast("IngressBackend", result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path is an extended POSIX regex as defined by IEEE Std 1003.1, (i.e this follows the egrep/unix syntax, not the perl syntax) matched against the path of an incoming request. Currently it can contain characters disallowed from the conventional "path" part of a URL as defined by RFC 3986. Paths must begin with a '/'. If unspecified, the path defaults to a catch all sending traffic to the backend.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.HTTPIngressPath#path
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpIngressPath(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.HttpIngressRuleValue",
    jsii_struct_bases=[],
    name_mapping={"paths": "paths"},
)
class HttpIngressRuleValue:
    def __init__(self, *, paths: typing.Sequence[HttpIngressPath]) -> None:
        '''(experimental) HTTPIngressRuleValue is a list of http selectors pointing to backends.

        In the example: http:///? -> backend where where parts of the url correspond to RFC 3986, this resource will be used to match against everything after the last '/' and before the first '?' or '#'.

        :param paths: (experimental) A collection of paths that map requests to backends.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.HTTPIngressRuleValue
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "paths": paths,
        }

    @builtins.property
    def paths(self) -> typing.List[HttpIngressPath]:
        '''(experimental) A collection of paths that map requests to backends.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.HTTPIngressRuleValue#paths
        '''
        result = self._values.get("paths")
        assert result is not None, "Required property 'paths' is missing"
        return typing.cast(typing.List[HttpIngressPath], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpIngressRuleValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.IngressBackend",
    jsii_struct_bases=[],
    name_mapping={"service_name": "serviceName", "service_port": "servicePort"},
)
class IngressBackend:
    def __init__(
        self,
        *,
        service_name: builtins.str,
        service_port: "IntOrString",
    ) -> None:
        '''(experimental) IngressBackend describes all endpoints for a given service and port.

        :param service_name: (experimental) Specifies the name of the referenced service.
        :param service_port: (experimental) Specifies the port of the referenced service.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressBackend
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "service_name": service_name,
            "service_port": service_port,
        }

    @builtins.property
    def service_name(self) -> builtins.str:
        '''(experimental) Specifies the name of the referenced service.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressBackend#serviceName
        '''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_port(self) -> "IntOrString":
        '''(experimental) Specifies the port of the referenced service.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressBackend#servicePort
        '''
        result = self._values.get("service_port")
        assert result is not None, "Required property 'service_port' is missing"
        return typing.cast("IntOrString", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressBackend(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.IngressRule",
    jsii_struct_bases=[],
    name_mapping={"host": "host", "http": "http"},
)
class IngressRule:
    def __init__(
        self,
        *,
        host: typing.Optional[builtins.str] = None,
        http: typing.Optional[HttpIngressRuleValue] = None,
    ) -> None:
        '''(experimental) IngressRule represents the rules mapping the paths under a specified host to the related backend services.

        Incoming requests are first evaluated for a host match, then routed to the backend associated with the matching IngressRuleValue.

        :param host: (experimental) Host is the fully qualified domain name of a network host, as defined by RFC 3986. Note the following deviations from the "host" part of the URI as defined in the RFC: 1. IPs are not allowed. Currently an IngressRuleValue can only apply to the IP in the Spec of the parent Ingress. 2. The ``:`` delimiter is not respected because ports are not allowed. Currently the port of an Ingress is implicitly :80 for http and :443 for https. Both these may change in the future. Incoming requests are matched against the host before the IngressRuleValue. If the host is unspecified, the Ingress routes all traffic based on the specified IngressRuleValue.
        :param http: 

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressRule
        '''
        if isinstance(http, dict):
            http = HttpIngressRuleValue(**http)
        self._values: typing.Dict[str, typing.Any] = {}
        if host is not None:
            self._values["host"] = host
        if http is not None:
            self._values["http"] = http

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''(experimental) Host is the fully qualified domain name of a network host, as defined by RFC 3986.

        Note the following deviations from the "host" part of the URI as defined in the RFC: 1. IPs are not allowed. Currently an IngressRuleValue can only apply to the
        IP in the Spec of the parent Ingress.
        2. The ``:`` delimiter is not respected because ports are not allowed.
        Currently the port of an Ingress is implicitly :80 for http and
        :443 for https.
        Both these may change in the future. Incoming requests are matched against the host before the IngressRuleValue. If the host is unspecified, the Ingress routes all traffic based on the specified IngressRuleValue.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressRule#host
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http(self) -> typing.Optional[HttpIngressRuleValue]:
        '''
        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressRule#http
        '''
        result = self._values.get("http")
        return typing.cast(typing.Optional[HttpIngressRuleValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.IngressSpec",
    jsii_struct_bases=[],
    name_mapping={"backend": "backend", "rules": "rules", "tls": "tls"},
)
class IngressSpec:
    def __init__(
        self,
        *,
        backend: typing.Optional[IngressBackend] = None,
        rules: typing.Optional[typing.Sequence[IngressRule]] = None,
        tls: typing.Optional[typing.Sequence["IngressTls"]] = None,
    ) -> None:
        '''(experimental) IngressSpec describes the Ingress the user wishes to exist.

        :param backend: (experimental) A default backend capable of servicing requests that don't match any rule. At least one of 'backend' or 'rules' must be specified. This field is optional to allow the loadbalancer controller or defaulting logic to specify a global default.
        :param rules: (experimental) A list of host rules used to configure the Ingress. If unspecified, or no rule matches, all traffic is sent to the default backend.
        :param tls: (experimental) TLS configuration. Currently the Ingress only supports a single TLS port, 443. If multiple members of this list specify different hosts, they will be multiplexed on the same port according to the hostname specified through the SNI TLS extension, if the ingress controller fulfilling the ingress supports SNI.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressSpec
        '''
        if isinstance(backend, dict):
            backend = IngressBackend(**backend)
        self._values: typing.Dict[str, typing.Any] = {}
        if backend is not None:
            self._values["backend"] = backend
        if rules is not None:
            self._values["rules"] = rules
        if tls is not None:
            self._values["tls"] = tls

    @builtins.property
    def backend(self) -> typing.Optional[IngressBackend]:
        '''(experimental) A default backend capable of servicing requests that don't match any rule.

        At least one of 'backend' or 'rules' must be specified. This field is optional to allow the loadbalancer controller or defaulting logic to specify a global default.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressSpec#backend
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[IngressBackend], result)

    @builtins.property
    def rules(self) -> typing.Optional[typing.List[IngressRule]]:
        '''(experimental) A list of host rules used to configure the Ingress.

        If unspecified, or no rule matches, all traffic is sent to the default backend.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressSpec#rules
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List[IngressRule]], result)

    @builtins.property
    def tls(self) -> typing.Optional[typing.List["IngressTls"]]:
        '''(experimental) TLS configuration.

        Currently the Ingress only supports a single TLS port, 443. If multiple members of this list specify different hosts, they will be multiplexed on the same port according to the hostname specified through the SNI TLS extension, if the ingress controller fulfilling the ingress supports SNI.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressSpec#tls
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[typing.List["IngressTls"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.IngressTls",
    jsii_struct_bases=[],
    name_mapping={"hosts": "hosts", "secret_name": "secretName"},
)
class IngressTls:
    def __init__(
        self,
        *,
        hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
        secret_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) IngressTLS describes the transport layer security associated with an Ingress.

        :param hosts: (experimental) Hosts are a list of hosts included in the TLS certificate. The values in this list must match the name/s used in the tlsSecret. Defaults to the wildcard host setting for the loadbalancer controller fulfilling this Ingress, if left unspecified. Default: the wildcard host setting for the loadbalancer controller fulfilling this Ingress, if left unspecified.
        :param secret_name: (experimental) SecretName is the name of the secret used to terminate SSL traffic on 443. Field is left optional to allow SSL routing based on SNI hostname alone. If the SNI host in a listener conflicts with the "Host" header field used by an IngressRule, the SNI host is used for termination and value of the Host header is used for routing.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressTLS
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if hosts is not None:
            self._values["hosts"] = hosts
        if secret_name is not None:
            self._values["secret_name"] = secret_name

    @builtins.property
    def hosts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Hosts are a list of hosts included in the TLS certificate.

        The values in this list must match the name/s used in the tlsSecret. Defaults to the wildcard host setting for the loadbalancer controller fulfilling this Ingress, if left unspecified.

        :default: the wildcard host setting for the loadbalancer controller fulfilling this Ingress, if left unspecified.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressTLS#hosts
        '''
        result = self._values.get("hosts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) SecretName is the name of the secret used to terminate SSL traffic on 443.

        Field is left optional to allow SSL routing based on SNI hostname alone. If the SNI host in a listener conflicts with the "Host" header field used by an IngressRule, the SNI host is used for termination and value of the Host header is used for routing.

        :stability: experimental
        :schema: io.k8s.api.networking.v1beta1.IngressTLS#secretName
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressTls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.Initializer",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class Initializer:
    def __init__(self, *, name: builtins.str) -> None:
        '''(experimental) Initializer is information about an initializer that has not yet completed.

        :param name: (experimental) name of the process that is responsible for initializing this object.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Initializer
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) name of the process that is responsible for initializing this object.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Initializer#name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Initializer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.Initializers",
    jsii_struct_bases=[],
    name_mapping={"pending": "pending", "result": "result"},
)
class Initializers:
    def __init__(
        self,
        *,
        pending: typing.Sequence[Initializer],
        result: typing.Optional["KubeStatusProps"] = None,
    ) -> None:
        '''(experimental) Initializers tracks the progress of initialization.

        :param pending: (experimental) Pending is a list of initializers that must execute in order before this object is visible. When the last pending initializer is removed, and no failing result is set, the initializers struct will be set to nil and the object is considered as initialized and visible to all clients.
        :param result: (experimental) If result is set with the Failure field, the object will be persisted to storage and then deleted, ensuring that other clients can observe the deletion.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Initializers
        '''
        if isinstance(result, dict):
            result = KubeStatusProps(**result)
        self._values: typing.Dict[str, typing.Any] = {
            "pending": pending,
        }
        if result is not None:
            self._values["result"] = result

    @builtins.property
    def pending(self) -> typing.List[Initializer]:
        '''(experimental) Pending is a list of initializers that must execute in order before this object is visible.

        When the last pending initializer is removed, and no failing result is set, the initializers struct will be set to nil and the object is considered as initialized and visible to all clients.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Initializers#pending
        '''
        result = self._values.get("pending")
        assert result is not None, "Required property 'pending' is missing"
        return typing.cast(typing.List[Initializer], result)

    @builtins.property
    def result(self) -> typing.Optional["KubeStatusProps"]:
        '''(experimental) If result is set with the Failure field, the object will be persisted to storage and then deleted, ensuring that other clients can observe the deletion.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Initializers#result
        '''
        result = self._values.get("result")
        return typing.cast(typing.Optional["KubeStatusProps"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Initializers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IntOrString(
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.IntOrString",
):
    '''
    :stability: experimental
    :schema: io.k8s.apimachinery.pkg.util.intstr.IntOrString
    '''

    @jsii.member(jsii_name="fromNumber") # type: ignore[misc]
    @builtins.classmethod
    def from_number(cls, value: jsii.Number) -> "IntOrString":
        '''
        :param value: -

        :stability: experimental
        '''
        return typing.cast("IntOrString", jsii.sinvoke(cls, "fromNumber", [value]))

    @jsii.member(jsii_name="fromString") # type: ignore[misc]
    @builtins.classmethod
    def from_string(cls, value: builtins.str) -> "IntOrString":
        '''
        :param value: -

        :stability: experimental
        '''
        return typing.cast("IntOrString", jsii.sinvoke(cls, "fromString", [value]))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.KubeStatusProps",
    jsii_struct_bases=[],
    name_mapping={
        "code": "code",
        "details": "details",
        "message": "message",
        "metadata": "metadata",
        "reason": "reason",
    },
)
class KubeStatusProps:
    def __init__(
        self,
        *,
        code: typing.Optional[jsii.Number] = None,
        details: typing.Optional["StatusDetails"] = None,
        message: typing.Optional[builtins.str] = None,
        metadata: typing.Optional["ListMeta"] = None,
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Status is a return value for calls that don't return other objects.

        :param code: (experimental) Suggested HTTP return code for this status, 0 if not set.
        :param details: (experimental) Extended data associated with the reason. Each reason may define its own extended details. This field is optional and the data returned is not guaranteed to conform to any schema except that defined by the reason type.
        :param message: (experimental) A human-readable description of the status of this operation.
        :param metadata: (experimental) Standard list metadata. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds
        :param reason: (experimental) A machine-readable description of why this operation is in the "Failure" status. If this value is empty there is no information available. A Reason clarifies an HTTP status code but does not override it.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Status
        '''
        if isinstance(details, dict):
            details = StatusDetails(**details)
        if isinstance(metadata, dict):
            metadata = ListMeta(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if code is not None:
            self._values["code"] = code
        if details is not None:
            self._values["details"] = details
        if message is not None:
            self._values["message"] = message
        if metadata is not None:
            self._values["metadata"] = metadata
        if reason is not None:
            self._values["reason"] = reason

    @builtins.property
    def code(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Suggested HTTP return code for this status, 0 if not set.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Status#code
        '''
        result = self._values.get("code")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def details(self) -> typing.Optional["StatusDetails"]:
        '''(experimental) Extended data associated with the reason.

        Each reason may define its own extended details. This field is optional and the data returned is not guaranteed to conform to any schema except that defined by the reason type.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Status#details
        '''
        result = self._values.get("details")
        return typing.cast(typing.Optional["StatusDetails"], result)

    @builtins.property
    def message(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human-readable description of the status of this operation.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Status#message
        '''
        result = self._values.get("message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional["ListMeta"]:
        '''(experimental) Standard list metadata.

        More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Status#metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional["ListMeta"], result)

    @builtins.property
    def reason(self) -> typing.Optional[builtins.str]:
        '''(experimental) A machine-readable description of why this operation is in the "Failure" status.

        If this value is empty there is no information available. A Reason clarifies an HTTP status code but does not override it.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.Status#reason
        '''
        result = self._values.get("reason")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubeStatusProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.ListMeta",
    jsii_struct_bases=[],
    name_mapping={
        "continue_": "continue",
        "remaining_item_count": "remainingItemCount",
        "resource_version": "resourceVersion",
        "self_link": "selfLink",
    },
)
class ListMeta:
    def __init__(
        self,
        *,
        continue_: typing.Optional[builtins.str] = None,
        remaining_item_count: typing.Optional[jsii.Number] = None,
        resource_version: typing.Optional[builtins.str] = None,
        self_link: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) ListMeta describes metadata that synthetic resources must have, including lists and various status objects.

        A resource may have only one of {ObjectMeta, ListMeta}.

        :param continue_: (experimental) continue may be set if the user set a limit on the number of items returned, and indicates that the server has more data available. The value is opaque and may be used to issue another request to the endpoint that served this list to retrieve the next set of available objects. Continuing a consistent list may not be possible if the server configuration has changed or more than a few minutes have passed. The resourceVersion field returned when using this continue value will be identical to the value in the first response, unless you have received this token from an error message.
        :param remaining_item_count: (experimental) remainingItemCount is the number of subsequent items in the list which are not included in this list response. If the list request contained label or field selectors, then the number of remaining items is unknown and the field will be left unset and omitted during serialization. If the list is complete (either because it is not chunking or because this is the last chunk), then there are no more remaining items and this field will be left unset and omitted during serialization. Servers older than v1.15 do not set this field. The intended use of the remainingItemCount is *estimating* the size of a collection. Clients should not rely on the remainingItemCount to be set or to be exact. This field is alpha and can be changed or removed without notice.
        :param resource_version: (experimental) String that identifies the server's internal version of this object that can be used by clients to determine when objects have changed. Value must be treated as opaque by clients and passed unmodified back to the server. Populated by the system. Read-only. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#concurrency-control-and-consistency
        :param self_link: (experimental) selfLink is a URL representing this object. Populated by the system. Read-only.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ListMeta
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if continue_ is not None:
            self._values["continue_"] = continue_
        if remaining_item_count is not None:
            self._values["remaining_item_count"] = remaining_item_count
        if resource_version is not None:
            self._values["resource_version"] = resource_version
        if self_link is not None:
            self._values["self_link"] = self_link

    @builtins.property
    def continue_(self) -> typing.Optional[builtins.str]:
        '''(experimental) continue may be set if the user set a limit on the number of items returned, and indicates that the server has more data available.

        The value is opaque and may be used to issue another request to the endpoint that served this list to retrieve the next set of available objects. Continuing a consistent list may not be possible if the server configuration has changed or more than a few minutes have passed. The resourceVersion field returned when using this continue value will be identical to the value in the first response, unless you have received this token from an error message.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ListMeta#continue
        '''
        result = self._values.get("continue_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remaining_item_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) remainingItemCount is the number of subsequent items in the list which are not included in this list response.

        If the list request contained label or field selectors, then the number of remaining items is unknown and the field will be left unset and omitted during serialization. If the list is complete (either because it is not chunking or because this is the last chunk), then there are no more remaining items and this field will be left unset and omitted during serialization. Servers older than v1.15 do not set this field. The intended use of the remainingItemCount is *estimating* the size of a collection. Clients should not rely on the remainingItemCount to be set or to be exact.

        This field is alpha and can be changed or removed without notice.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ListMeta#remainingItemCount
        '''
        result = self._values.get("remaining_item_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def resource_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) String that identifies the server's internal version of this object that can be used by clients to determine when objects have changed.

        Value must be treated as opaque by clients and passed unmodified back to the server. Populated by the system. Read-only. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#concurrency-control-and-consistency

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ListMeta#resourceVersion
        '''
        result = self._values.get("resource_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def self_link(self) -> typing.Optional[builtins.str]:
        '''(experimental) selfLink is a URL representing this object.

        Populated by the system. Read-only.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ListMeta#selfLink
        '''
        result = self._values.get("self_link")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ListMeta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.ManagedFieldsEntry",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "fields": "fields",
        "manager": "manager",
        "operation": "operation",
        "time": "time",
    },
)
class ManagedFieldsEntry:
    def __init__(
        self,
        *,
        api_version: typing.Optional[builtins.str] = None,
        fields: typing.Any = None,
        manager: typing.Optional[builtins.str] = None,
        operation: typing.Optional[builtins.str] = None,
        time: typing.Optional[datetime.datetime] = None,
    ) -> None:
        '''(experimental) ManagedFieldsEntry is a workflow-id, a FieldSet and the group version of the resource that the fieldset applies to.

        :param api_version: (experimental) APIVersion defines the version of this resource that this field set applies to. The format is "group/version" just like the top-level APIVersion field. It is necessary to track the version of a field set because it cannot be automatically converted.
        :param fields: (experimental) Fields identifies a set of fields.
        :param manager: (experimental) Manager is an identifier of the workflow managing these fields.
        :param operation: (experimental) Operation is the type of operation which lead to this ManagedFieldsEntry being created. The only valid values for this field are 'Apply' and 'Update'.
        :param time: (experimental) Time is timestamp of when these fields were set. It should always be empty if Operation is 'Apply'

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ManagedFieldsEntry
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if api_version is not None:
            self._values["api_version"] = api_version
        if fields is not None:
            self._values["fields"] = fields
        if manager is not None:
            self._values["manager"] = manager
        if operation is not None:
            self._values["operation"] = operation
        if time is not None:
            self._values["time"] = time

    @builtins.property
    def api_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) APIVersion defines the version of this resource that this field set applies to.

        The format is "group/version" just like the top-level APIVersion field. It is necessary to track the version of a field set because it cannot be automatically converted.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ManagedFieldsEntry#apiVersion
        '''
        result = self._values.get("api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fields(self) -> typing.Any:
        '''(experimental) Fields identifies a set of fields.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ManagedFieldsEntry#fields
        '''
        result = self._values.get("fields")
        return typing.cast(typing.Any, result)

    @builtins.property
    def manager(self) -> typing.Optional[builtins.str]:
        '''(experimental) Manager is an identifier of the workflow managing these fields.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ManagedFieldsEntry#manager
        '''
        result = self._values.get("manager")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operation(self) -> typing.Optional[builtins.str]:
        '''(experimental) Operation is the type of operation which lead to this ManagedFieldsEntry being created.

        The only valid values for this field are 'Apply' and 'Update'.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ManagedFieldsEntry#operation
        '''
        result = self._values.get("operation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time(self) -> typing.Optional[datetime.datetime]:
        '''(experimental) Time is timestamp of when these fields were set.

        It should always be empty if Operation is 'Apply'

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ManagedFieldsEntry#time
        '''
        result = self._values.get("time")
        return typing.cast(typing.Optional[datetime.datetime], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedFieldsEntry(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.ObjectMeta",
    jsii_struct_bases=[],
    name_mapping={
        "annotations": "annotations",
        "cluster_name": "clusterName",
        "creation_timestamp": "creationTimestamp",
        "deletion_grace_period_seconds": "deletionGracePeriodSeconds",
        "deletion_timestamp": "deletionTimestamp",
        "finalizers": "finalizers",
        "generate_name": "generateName",
        "generation": "generation",
        "initializers": "initializers",
        "labels": "labels",
        "managed_fields": "managedFields",
        "name": "name",
        "namespace": "namespace",
        "owner_references": "ownerReferences",
        "resource_version": "resourceVersion",
        "self_link": "selfLink",
        "uid": "uid",
    },
)
class ObjectMeta:
    def __init__(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        creation_timestamp: typing.Optional[datetime.datetime] = None,
        deletion_grace_period_seconds: typing.Optional[jsii.Number] = None,
        deletion_timestamp: typing.Optional[datetime.datetime] = None,
        finalizers: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_name: typing.Optional[builtins.str] = None,
        generation: typing.Optional[jsii.Number] = None,
        initializers: typing.Optional[Initializers] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        managed_fields: typing.Optional[typing.Sequence[ManagedFieldsEntry]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        owner_references: typing.Optional[typing.Sequence["OwnerReference"]] = None,
        resource_version: typing.Optional[builtins.str] = None,
        self_link: typing.Optional[builtins.str] = None,
        uid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) ObjectMeta is metadata that all persisted resources must have, which includes all objects users must create.

        :param annotations: (experimental) Annotations is an unstructured key value map stored with a resource that may be set by external tools to store and retrieve arbitrary metadata. They are not queryable and should be preserved when modifying objects. More info: http://kubernetes.io/docs/user-guide/annotations
        :param cluster_name: (experimental) The name of the cluster which the object belongs to. This is used to distinguish resources with same name and namespace in different clusters. This field is not set anywhere right now and apiserver is going to ignore it if set in create or update request.
        :param creation_timestamp: (experimental) CreationTimestamp is a timestamp representing the server time when this object was created. It is not guaranteed to be set in happens-before order across separate operations. Clients may not set this value. It is represented in RFC3339 form and is in UTC. Populated by the system. Read-only. Null for lists. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#metadata
        :param deletion_grace_period_seconds: (experimental) Number of seconds allowed for this object to gracefully terminate before it will be removed from the system. Only set when deletionTimestamp is also set. May only be shortened. Read-only.
        :param deletion_timestamp: (experimental) DeletionTimestamp is RFC 3339 date and time at which this resource will be deleted. This field is set by the server when a graceful deletion is requested by the user, and is not directly settable by a client. The resource is expected to be deleted (no longer visible from resource lists, and not reachable by name) after the time in this field, once the finalizers list is empty. As long as the finalizers list contains items, deletion is blocked. Once the deletionTimestamp is set, this value may not be unset or be set further into the future, although it may be shortened or the resource may be deleted prior to this time. For example, a user may request that a pod is deleted in 30 seconds. The Kubelet will react by sending a graceful termination signal to the containers in the pod. After that 30 seconds, the Kubelet will send a hard termination signal (SIGKILL) to the container and after cleanup, remove the pod from the API. In the presence of network partitions, this object may still exist after this timestamp, until an administrator or automated process can determine the resource is fully terminated. If not set, graceful deletion of the object has not been requested. Populated by the system when a graceful deletion is requested. Read-only. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#metadata
        :param finalizers: (experimental) Must be empty before the object is deleted from the registry. Each entry is an identifier for the responsible component that will remove the entry from the list. If the deletionTimestamp of the object is non-nil, entries in this list can only be removed.
        :param generate_name: (experimental) GenerateName is an optional prefix, used by the server, to generate a unique name ONLY IF the Name field has not been provided. If this field is used, the name returned to the client will be different than the name passed. This value will also be combined with a unique suffix. The provided value has the same validation rules as the Name field, and may be truncated by the length of the suffix required to make the value unique on the server. If this field is specified and the generated name exists, the server will NOT return a 409 - instead, it will either return 201 Created or 500 with Reason ServerTimeout indicating a unique name could not be found in the time allotted, and the client should retry (optionally after the time indicated in the Retry-After header). Applied only if Name is not specified. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#idempotency
        :param generation: (experimental) A sequence number representing a specific generation of the desired state. Populated by the system. Read-only.
        :param initializers: (experimental) An initializer is a controller which enforces some system invariant at object creation time. This field is a list of initializers that have not yet acted on this object. If nil or empty, this object has been completely initialized. Otherwise, the object is considered uninitialized and is hidden (in list/watch and get calls) from clients that haven't explicitly asked to observe uninitialized objects. When an object is created, the system will populate this list with the current set of initializers. Only privileged users may set or modify this list. Once it is empty, it may not be modified further by any user. DEPRECATED - initializers are an alpha field and will be removed in v1.15.
        :param labels: (experimental) Map of string keys and values that can be used to organize and categorize (scope and select) objects. May match selectors of replication controllers and services. More info: http://kubernetes.io/docs/user-guide/labels
        :param managed_fields: (experimental) ManagedFields maps workflow-id and version to the set of fields that are managed by that workflow. This is mostly for internal housekeeping, and users typically shouldn't need to set or understand this field. A workflow can be the user's name, a controller's name, or the name of a specific apply path like "ci-cd". The set of fields is always in the version that the workflow used when modifying the object. This field is alpha and can be changed or removed without notice.
        :param name: (experimental) Name must be unique within a namespace. Is required when creating resources, although some resources may allow a client to request the generation of an appropriate name automatically. Name is primarily intended for creation idempotence and configuration definition. Cannot be updated. More info: http://kubernetes.io/docs/user-guide/identifiers#names
        :param namespace: (experimental) Namespace defines the space within each name must be unique. An empty namespace is equivalent to the "default" namespace, but "default" is the canonical representation. Not all objects are required to be scoped to a namespace - the value of this field for those objects will be empty. Must be a DNS_LABEL. Cannot be updated. More info: http://kubernetes.io/docs/user-guide/namespaces
        :param owner_references: (experimental) List of objects depended by this object. If ALL objects in the list have been deleted, this object will be garbage collected. If this object is managed by a controller, then an entry in this list will point to this controller, with the controller field set to true. There cannot be more than one managing controller.
        :param resource_version: (experimental) An opaque value that represents the internal version of this object that can be used by clients to determine when objects have changed. May be used for optimistic concurrency, change detection, and the watch operation on a resource or set of resources. Clients must treat these values as opaque and passed unmodified back to the server. They may only be valid for a particular resource or set of resources. Populated by the system. Read-only. Value must be treated as opaque by clients and . More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#concurrency-control-and-consistency
        :param self_link: (experimental) SelfLink is a URL representing this object. Populated by the system. Read-only.
        :param uid: (experimental) UID is the unique in time and space value for this object. It is typically generated by the server on successful creation of a resource and is not allowed to change on PUT operations. Populated by the system. Read-only. More info: http://kubernetes.io/docs/user-guide/identifiers#uids

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta
        '''
        if isinstance(initializers, dict):
            initializers = Initializers(**initializers)
        self._values: typing.Dict[str, typing.Any] = {}
        if annotations is not None:
            self._values["annotations"] = annotations
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if creation_timestamp is not None:
            self._values["creation_timestamp"] = creation_timestamp
        if deletion_grace_period_seconds is not None:
            self._values["deletion_grace_period_seconds"] = deletion_grace_period_seconds
        if deletion_timestamp is not None:
            self._values["deletion_timestamp"] = deletion_timestamp
        if finalizers is not None:
            self._values["finalizers"] = finalizers
        if generate_name is not None:
            self._values["generate_name"] = generate_name
        if generation is not None:
            self._values["generation"] = generation
        if initializers is not None:
            self._values["initializers"] = initializers
        if labels is not None:
            self._values["labels"] = labels
        if managed_fields is not None:
            self._values["managed_fields"] = managed_fields
        if name is not None:
            self._values["name"] = name
        if namespace is not None:
            self._values["namespace"] = namespace
        if owner_references is not None:
            self._values["owner_references"] = owner_references
        if resource_version is not None:
            self._values["resource_version"] = resource_version
        if self_link is not None:
            self._values["self_link"] = self_link
        if uid is not None:
            self._values["uid"] = uid

    @builtins.property
    def annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Annotations is an unstructured key value map stored with a resource that may be set by external tools to store and retrieve arbitrary metadata.

        They are not queryable and should be preserved when modifying objects. More info: http://kubernetes.io/docs/user-guide/annotations

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#annotations
        '''
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the cluster which the object belongs to.

        This is used to distinguish resources with same name and namespace in different clusters. This field is not set anywhere right now and apiserver is going to ignore it if set in create or update request.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#clusterName
        '''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_timestamp(self) -> typing.Optional[datetime.datetime]:
        '''(experimental) CreationTimestamp is a timestamp representing the server time when this object was created.

        It is not guaranteed to be set in happens-before order across separate operations. Clients may not set this value. It is represented in RFC3339 form and is in UTC.

        Populated by the system. Read-only. Null for lists. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#metadata

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#creationTimestamp
        '''
        result = self._values.get("creation_timestamp")
        return typing.cast(typing.Optional[datetime.datetime], result)

    @builtins.property
    def deletion_grace_period_seconds(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of seconds allowed for this object to gracefully terminate before it will be removed from the system.

        Only set when deletionTimestamp is also set. May only be shortened. Read-only.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#deletionGracePeriodSeconds
        '''
        result = self._values.get("deletion_grace_period_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deletion_timestamp(self) -> typing.Optional[datetime.datetime]:
        '''(experimental) DeletionTimestamp is RFC 3339 date and time at which this resource will be deleted.

        This field is set by the server when a graceful deletion is requested by the user, and is not directly settable by a client. The resource is expected to be deleted (no longer visible from resource lists, and not reachable by name) after the time in this field, once the finalizers list is empty. As long as the finalizers list contains items, deletion is blocked. Once the deletionTimestamp is set, this value may not be unset or be set further into the future, although it may be shortened or the resource may be deleted prior to this time. For example, a user may request that a pod is deleted in 30 seconds. The Kubelet will react by sending a graceful termination signal to the containers in the pod. After that 30 seconds, the Kubelet will send a hard termination signal (SIGKILL) to the container and after cleanup, remove the pod from the API. In the presence of network partitions, this object may still exist after this timestamp, until an administrator or automated process can determine the resource is fully terminated. If not set, graceful deletion of the object has not been requested.

        Populated by the system when a graceful deletion is requested. Read-only. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#metadata

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#deletionTimestamp
        '''
        result = self._values.get("deletion_timestamp")
        return typing.cast(typing.Optional[datetime.datetime], result)

    @builtins.property
    def finalizers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Must be empty before the object is deleted from the registry.

        Each entry is an identifier for the responsible component that will remove the entry from the list. If the deletionTimestamp of the object is non-nil, entries in this list can only be removed.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#finalizers
        '''
        result = self._values.get("finalizers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def generate_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) GenerateName is an optional prefix, used by the server, to generate a unique name ONLY IF the Name field has not been provided.

        If this field is used, the name returned to the client will be different than the name passed. This value will also be combined with a unique suffix. The provided value has the same validation rules as the Name field, and may be truncated by the length of the suffix required to make the value unique on the server.

        If this field is specified and the generated name exists, the server will NOT return a 409 - instead, it will either return 201 Created or 500 with Reason ServerTimeout indicating a unique name could not be found in the time allotted, and the client should retry (optionally after the time indicated in the Retry-After header).

        Applied only if Name is not specified. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#idempotency

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#generateName
        '''
        result = self._values.get("generate_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def generation(self) -> typing.Optional[jsii.Number]:
        '''(experimental) A sequence number representing a specific generation of the desired state.

        Populated by the system. Read-only.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#generation
        '''
        result = self._values.get("generation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def initializers(self) -> typing.Optional[Initializers]:
        '''(experimental) An initializer is a controller which enforces some system invariant at object creation time.

        This field is a list of initializers that have not yet acted on this object. If nil or empty, this object has been completely initialized. Otherwise, the object is considered uninitialized and is hidden (in list/watch and get calls) from clients that haven't explicitly asked to observe uninitialized objects.

        When an object is created, the system will populate this list with the current set of initializers. Only privileged users may set or modify this list. Once it is empty, it may not be modified further by any user.

        DEPRECATED - initializers are an alpha field and will be removed in v1.15.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#initializers
        '''
        result = self._values.get("initializers")
        return typing.cast(typing.Optional[Initializers], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Map of string keys and values that can be used to organize and categorize (scope and select) objects.

        May match selectors of replication controllers and services. More info: http://kubernetes.io/docs/user-guide/labels

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#labels
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def managed_fields(self) -> typing.Optional[typing.List[ManagedFieldsEntry]]:
        '''(experimental) ManagedFields maps workflow-id and version to the set of fields that are managed by that workflow.

        This is mostly for internal housekeeping, and users typically shouldn't need to set or understand this field. A workflow can be the user's name, a controller's name, or the name of a specific apply path like "ci-cd". The set of fields is always in the version that the workflow used when modifying the object.

        This field is alpha and can be changed or removed without notice.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#managedFields
        '''
        result = self._values.get("managed_fields")
        return typing.cast(typing.Optional[typing.List[ManagedFieldsEntry]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name must be unique within a namespace.

        Is required when creating resources, although some resources may allow a client to request the generation of an appropriate name automatically. Name is primarily intended for creation idempotence and configuration definition. Cannot be updated. More info: http://kubernetes.io/docs/user-guide/identifiers#names

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) Namespace defines the space within each name must be unique.

        An empty namespace is equivalent to the "default" namespace, but "default" is the canonical representation. Not all objects are required to be scoped to a namespace - the value of this field for those objects will be empty.

        Must be a DNS_LABEL. Cannot be updated. More info: http://kubernetes.io/docs/user-guide/namespaces

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#namespace
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner_references(self) -> typing.Optional[typing.List["OwnerReference"]]:
        '''(experimental) List of objects depended by this object.

        If ALL objects in the list have been deleted, this object will be garbage collected. If this object is managed by a controller, then an entry in this list will point to this controller, with the controller field set to true. There cannot be more than one managing controller.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#ownerReferences
        '''
        result = self._values.get("owner_references")
        return typing.cast(typing.Optional[typing.List["OwnerReference"]], result)

    @builtins.property
    def resource_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) An opaque value that represents the internal version of this object that can be used by clients to determine when objects have changed.

        May be used for optimistic concurrency, change detection, and the watch operation on a resource or set of resources. Clients must treat these values as opaque and passed unmodified back to the server. They may only be valid for a particular resource or set of resources.

        Populated by the system. Read-only. Value must be treated as opaque by clients and . More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#concurrency-control-and-consistency

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#resourceVersion
        '''
        result = self._values.get("resource_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def self_link(self) -> typing.Optional[builtins.str]:
        '''(experimental) SelfLink is a URL representing this object.

        Populated by the system. Read-only.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#selfLink
        '''
        result = self._values.get("self_link")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uid(self) -> typing.Optional[builtins.str]:
        '''(experimental) UID is the unique in time and space value for this object.

        It is typically generated by the server on successful creation of a resource and is not allowed to change on PUT operations.

        Populated by the system. Read-only. More info: http://kubernetes.io/docs/user-guide/identifiers#uids

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta#uid
        '''
        result = self._values.get("uid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ObjectMeta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.OwnerReference",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "kind": "kind",
        "name": "name",
        "uid": "uid",
        "block_owner_deletion": "blockOwnerDeletion",
        "controller": "controller",
    },
)
class OwnerReference:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        kind: builtins.str,
        name: builtins.str,
        uid: builtins.str,
        block_owner_deletion: typing.Optional[builtins.bool] = None,
        controller: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) OwnerReference contains enough information to let you identify an owning object.

        An owning object must be in the same namespace as the dependent, or be cluster-scoped, so there is no namespace field.

        :param api_version: (experimental) API version of the referent.
        :param kind: (experimental) Kind of the referent. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds
        :param name: (experimental) Name of the referent. More info: http://kubernetes.io/docs/user-guide/identifiers#names
        :param uid: (experimental) UID of the referent. More info: http://kubernetes.io/docs/user-guide/identifiers#uids
        :param block_owner_deletion: (experimental) If true, AND if the owner has the "foregroundDeletion" finalizer, then the owner cannot be deleted from the key-value store until this reference is removed. Defaults to false. To set this field, a user needs "delete" permission of the owner, otherwise 422 (Unprocessable Entity) will be returned. Default: false. To set this field, a user needs "delete" permission of the owner, otherwise 422 (Unprocessable Entity) will be returned.
        :param controller: (experimental) If true, this reference points to the managing controller.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.OwnerReference
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_version": api_version,
            "kind": kind,
            "name": name,
            "uid": uid,
        }
        if block_owner_deletion is not None:
            self._values["block_owner_deletion"] = block_owner_deletion
        if controller is not None:
            self._values["controller"] = controller

    @builtins.property
    def api_version(self) -> builtins.str:
        '''(experimental) API version of the referent.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.OwnerReference#apiVersion
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kind(self) -> builtins.str:
        '''(experimental) Kind of the referent.

        More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.OwnerReference#kind
        '''
        result = self._values.get("kind")
        assert result is not None, "Required property 'kind' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Name of the referent.

        More info: http://kubernetes.io/docs/user-guide/identifiers#names

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.OwnerReference#name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uid(self) -> builtins.str:
        '''(experimental) UID of the referent.

        More info: http://kubernetes.io/docs/user-guide/identifiers#uids

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.OwnerReference#uid
        '''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def block_owner_deletion(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If true, AND if the owner has the "foregroundDeletion" finalizer, then the owner cannot be deleted from the key-value store until this reference is removed.

        Defaults to false. To set this field, a user needs "delete" permission of the owner, otherwise 422 (Unprocessable Entity) will be returned.

        :default: false. To set this field, a user needs "delete" permission of the owner, otherwise 422 (Unprocessable Entity) will be returned.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.OwnerReference#blockOwnerDeletion
        '''
        result = self._values.get("block_owner_deletion")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def controller(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If true, this reference points to the managing controller.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.OwnerReference#controller
        '''
        result = self._values.get("controller")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OwnerReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.StatusCause",
    jsii_struct_bases=[],
    name_mapping={"field": "field", "message": "message", "reason": "reason"},
)
class StatusCause:
    def __init__(
        self,
        *,
        field: typing.Optional[builtins.str] = None,
        message: typing.Optional[builtins.str] = None,
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) StatusCause provides more information about an api.Status failure, including cases when multiple errors are encountered.

        :param field: (experimental) The field of the resource that has caused this error, as named by its JSON serialization. May include dot and postfix notation for nested attributes. Arrays are zero-indexed. Fields may appear more than once in an array of causes due to fields having multiple errors. Optional. Examples: "name" - the field "name" on the current resource "items[0].name" - the field "name" on the first array entry in "items"
        :param message: (experimental) A human-readable description of the cause of the error. This field may be presented as-is to a reader.
        :param reason: (experimental) A machine-readable description of the cause of the error. If this value is empty there is no information available.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusCause
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if field is not None:
            self._values["field"] = field
        if message is not None:
            self._values["message"] = message
        if reason is not None:
            self._values["reason"] = reason

    @builtins.property
    def field(self) -> typing.Optional[builtins.str]:
        '''(experimental) The field of the resource that has caused this error, as named by its JSON serialization.

        May include dot and postfix notation for nested attributes. Arrays are zero-indexed.  Fields may appear more than once in an array of causes due to fields having multiple errors. Optional.

        Examples:
        "name" - the field "name" on the current resource
        "items[0].name" - the field "name" on the first array entry in "items"

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusCause#field
        '''
        result = self._values.get("field")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human-readable description of the cause of the error.

        This field may be presented as-is to a reader.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusCause#message
        '''
        result = self._values.get("message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reason(self) -> typing.Optional[builtins.str]:
        '''(experimental) A machine-readable description of the cause of the error.

        If this value is empty there is no information available.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusCause#reason
        '''
        result = self._values.get("reason")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatusCause(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-aws-lb-controller-api-object.StatusDetails",
    jsii_struct_bases=[],
    name_mapping={
        "causes": "causes",
        "group": "group",
        "kind": "kind",
        "name": "name",
        "retry_after_seconds": "retryAfterSeconds",
        "uid": "uid",
    },
)
class StatusDetails:
    def __init__(
        self,
        *,
        causes: typing.Optional[typing.Sequence[StatusCause]] = None,
        group: typing.Optional[builtins.str] = None,
        kind: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        retry_after_seconds: typing.Optional[jsii.Number] = None,
        uid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) StatusDetails is a set of additional properties that MAY be set by the server to provide additional information about a response.

        The Reason field of a Status object defines what attributes will be set. Clients must ignore fields that do not match the defined type of each attribute, and should assume that any attribute may be empty, invalid, or under defined.

        :param causes: (experimental) The Causes array includes more details associated with the StatusReason failure. Not all StatusReasons may provide detailed causes.
        :param group: (experimental) The group attribute of the resource associated with the status StatusReason.
        :param kind: (experimental) The kind attribute of the resource associated with the status StatusReason. On some operations may differ from the requested resource Kind. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds
        :param name: (experimental) The name attribute of the resource associated with the status StatusReason (when there is a single name which can be described).
        :param retry_after_seconds: (experimental) If specified, the time in seconds before the operation should be retried. Some errors may indicate the client must take an alternate action - for those errors this field may indicate how long to wait before taking the alternate action.
        :param uid: (experimental) UID of the resource. (when there is a single resource which can be described). More info: http://kubernetes.io/docs/user-guide/identifiers#uids

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusDetails
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if causes is not None:
            self._values["causes"] = causes
        if group is not None:
            self._values["group"] = group
        if kind is not None:
            self._values["kind"] = kind
        if name is not None:
            self._values["name"] = name
        if retry_after_seconds is not None:
            self._values["retry_after_seconds"] = retry_after_seconds
        if uid is not None:
            self._values["uid"] = uid

    @builtins.property
    def causes(self) -> typing.Optional[typing.List[StatusCause]]:
        '''(experimental) The Causes array includes more details associated with the StatusReason failure.

        Not all StatusReasons may provide detailed causes.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusDetails#causes
        '''
        result = self._values.get("causes")
        return typing.cast(typing.Optional[typing.List[StatusCause]], result)

    @builtins.property
    def group(self) -> typing.Optional[builtins.str]:
        '''(experimental) The group attribute of the resource associated with the status StatusReason.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusDetails#group
        '''
        result = self._values.get("group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kind(self) -> typing.Optional[builtins.str]:
        '''(experimental) The kind attribute of the resource associated with the status StatusReason.

        On some operations may differ from the requested resource Kind. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusDetails#kind
        '''
        result = self._values.get("kind")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name attribute of the resource associated with the status StatusReason (when there is a single name which can be described).

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusDetails#name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retry_after_seconds(self) -> typing.Optional[jsii.Number]:
        '''(experimental) If specified, the time in seconds before the operation should be retried.

        Some errors may indicate the client must take an alternate action - for those errors this field may indicate how long to wait before taking the alternate action.

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusDetails#retryAfterSeconds
        '''
        result = self._values.get("retry_after_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uid(self) -> typing.Optional[builtins.str]:
        '''(experimental) UID of the resource.

        (when there is a single resource which can be described). More info: http://kubernetes.io/docs/user-guide/identifiers#uids

        :stability: experimental
        :schema: io.k8s.apimachinery.pkg.apis.meta.v1.StatusDetails#uid
        '''
        result = self._values.get("uid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatusDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AWSLoadBalancerControllerObject",
    "AWSLoadBalancerControllerProps",
    "HttpIngressPath",
    "HttpIngressRuleValue",
    "IngressBackend",
    "IngressRule",
    "IngressSpec",
    "IngressTls",
    "Initializer",
    "Initializers",
    "IntOrString",
    "KubeStatusProps",
    "ListMeta",
    "ManagedFieldsEntry",
    "ObjectMeta",
    "OwnerReference",
    "StatusCause",
    "StatusDetails",
]

publication.publish()
