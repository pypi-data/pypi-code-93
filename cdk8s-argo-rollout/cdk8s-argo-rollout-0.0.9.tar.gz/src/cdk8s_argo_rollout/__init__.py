'''
# cdk8s-argo-rollout

![Release](https://github.com/opencdk8s/cdk8s-argo-rollout/workflows/Release/badge.svg?branch=master)
[![npm version](https://badge.fury.io/js/%40opencdk8s%2Fcdk8s-argo-rollout.svg)](https://badge.fury.io/js/%40opencdk8s%2Fcdk8s-argo-rollout)
[![PyPI version](https://badge.fury.io/py/cdk8s-argo-rollout.svg)](https://badge.fury.io/py/cdk8s-argo-rollout)
![npm](https://img.shields.io/npm/dt/@opencdk8s/cdk8s-argo-rollout?label=npm&color=green)

## Installation

### TypeScript

Use `yarn` or `npm` to install.

```sh
$ npm install @opencdk8s/cdk8s-argo-rollout
```

```sh
$ yarn add @opencdk8s/cdk8s-argo-rollout
```

### Python

```sh
$ pip install cdk8s-argo-rollout
```

## Contribution

1. Fork ([link](https://github.com/opencdk8s/cdk8s-argo-rollout/fork))
2. Bootstrap the repo:

   ```bash
   yarn install # installs dependencies
   npx projen

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

[Sumit Agarwal](https://github.com/agarwal-sumit)
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
from .k8s import (
    LabelSelector as _LabelSelector_e7ec8693,
    ObjectFieldSelector as _ObjectFieldSelector_05a3d12c,
    ObjectMeta as _ObjectMeta_5c2c93e5,
    PodAntiAffinity as _PodAntiAffinity_afb5a5bc,
    PodTemplateSpec as _PodTemplateSpec_331e2248,
)


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-argo-rollout.AnalysisArgs",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value", "value_from": "valueFrom"},
)
class AnalysisArgs:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: typing.Optional[builtins.str] = None,
        value_from: typing.Optional["ValueFrom"] = None,
    ) -> None:
        '''
        :param name: 
        :param value: 
        :param value_from: 

        :stability: experimental
        '''
        if isinstance(value_from, dict):
            value_from = ValueFrom(**value_from)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if value is not None:
            self._values["value"] = value
        if value_from is not None:
            self._values["value_from"] = value_from

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value_from(self) -> typing.Optional["ValueFrom"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("value_from")
        return typing.cast(typing.Optional["ValueFrom"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AnalysisArgs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-argo-rollout.AnalysisSpec",
    jsii_struct_bases=[],
    name_mapping={"args": "args", "templates": "templates"},
)
class AnalysisSpec:
    def __init__(
        self,
        *,
        args: typing.Sequence[AnalysisArgs],
        templates: typing.Sequence["AnalysisTemplate"],
    ) -> None:
        '''
        :param args: 
        :param templates: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "args": args,
            "templates": templates,
        }

    @builtins.property
    def args(self) -> typing.List[AnalysisArgs]:
        '''
        :stability: experimental
        '''
        result = self._values.get("args")
        assert result is not None, "Required property 'args' is missing"
        return typing.cast(typing.List[AnalysisArgs], result)

    @builtins.property
    def templates(self) -> typing.List["AnalysisTemplate"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("templates")
        assert result is not None, "Required property 'templates' is missing"
        return typing.cast(typing.List["AnalysisTemplate"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AnalysisSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-argo-rollout.AnalysisTemplate",
    jsii_struct_bases=[],
    name_mapping={"template_name": "templateName"},
)
class AnalysisTemplate:
    def __init__(self, *, template_name: builtins.str) -> None:
        '''
        :param template_name: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "template_name": template_name,
        }

    @builtins.property
    def template_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("template_name")
        assert result is not None, "Required property 'template_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AnalysisTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ArgoRollout(
    cdk8s.ApiObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-argo-rollout.ArgoRollout",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        metadata: typing.Optional[_ObjectMeta_5c2c93e5] = None,
        spec: typing.Optional["ArgoSpecs"] = None,
    ) -> None:
        '''(experimental) Defines an "extentions" API object for AWS Load Balancer Controller - https://github.com/kubernetes-sigs/aws-load-balancer-controller.

        :param scope: the scope in which to define this object.
        :param id: a scope-local name for the object.
        :param metadata: (experimental) Standard object's metadata.
        :param spec: (experimental) Spec defines the behavior of the ingress.

        :stability: experimental
        '''
        props = ArgoRolloutProps(metadata=metadata, spec=spec)

        jsii.create(ArgoRollout, self, [scope, id, props])

    @jsii.member(jsii_name="manifest") # type: ignore[misc]
    @builtins.classmethod
    def manifest(
        cls,
        *,
        metadata: typing.Optional[_ObjectMeta_5c2c93e5] = None,
        spec: typing.Optional["ArgoSpecs"] = None,
    ) -> typing.Any:
        '''(experimental) Renders a Kubernetes manifest for an ingress object. https://github.com/kubernetes-sigs/aws-load-balancer-controller.

        This can be used to inline resource manifests inside other objects (e.g. as templates).

        :param metadata: (experimental) Standard object's metadata.
        :param spec: (experimental) Spec defines the behavior of the ingress.

        :stability: experimental
        '''
        props = ArgoRolloutProps(metadata=metadata, spec=spec)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "manifest", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GVK")
    def GVK(cls) -> cdk8s.GroupVersionKind:
        '''
        :stability: experimental
        '''
        return typing.cast(cdk8s.GroupVersionKind, jsii.sget(cls, "GVK"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-argo-rollout.ArgoRolloutProps",
    jsii_struct_bases=[],
    name_mapping={"metadata": "metadata", "spec": "spec"},
)
class ArgoRolloutProps:
    def __init__(
        self,
        *,
        metadata: typing.Optional[_ObjectMeta_5c2c93e5] = None,
        spec: typing.Optional["ArgoSpecs"] = None,
    ) -> None:
        '''
        :param metadata: (experimental) Standard object's metadata.
        :param spec: (experimental) Spec defines the behavior of the ingress.

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = _ObjectMeta_5c2c93e5(**metadata)
        if isinstance(spec, dict):
            spec = ArgoSpecs(**spec)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def metadata(self) -> typing.Optional[_ObjectMeta_5c2c93e5]:
        '''(experimental) Standard object's metadata.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[_ObjectMeta_5c2c93e5], result)

    @builtins.property
    def spec(self) -> typing.Optional["ArgoSpecs"]:
        '''(experimental) Spec defines the behavior of the ingress.

        :stability: experimental
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Optional["ArgoSpecs"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ArgoRolloutProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-argo-rollout.ArgoSpecs",
    jsii_struct_bases=[],
    name_mapping={
        "selector": "selector",
        "strategy": "strategy",
        "template": "template",
        "min_ready_seconds": "minReadySeconds",
        "paused": "paused",
        "progress_deadline_seconds": "progressDeadlineSeconds",
        "replicas": "replicas",
        "revision_history_limit": "revisionHistoryLimit",
    },
)
class ArgoSpecs:
    def __init__(
        self,
        *,
        selector: _LabelSelector_e7ec8693,
        strategy: "StrategySpecs",
        template: _PodTemplateSpec_331e2248,
        min_ready_seconds: typing.Optional[jsii.Number] = None,
        paused: typing.Optional[builtins.bool] = None,
        progress_deadline_seconds: typing.Optional[jsii.Number] = None,
        replicas: typing.Optional[jsii.Number] = None,
        revision_history_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param selector: 
        :param strategy: 
        :param template: 
        :param min_ready_seconds: 
        :param paused: 
        :param progress_deadline_seconds: 
        :param replicas: 
        :param revision_history_limit: 

        :stability: experimental
        '''
        if isinstance(selector, dict):
            selector = _LabelSelector_e7ec8693(**selector)
        if isinstance(strategy, dict):
            strategy = StrategySpecs(**strategy)
        if isinstance(template, dict):
            template = _PodTemplateSpec_331e2248(**template)
        self._values: typing.Dict[str, typing.Any] = {
            "selector": selector,
            "strategy": strategy,
            "template": template,
        }
        if min_ready_seconds is not None:
            self._values["min_ready_seconds"] = min_ready_seconds
        if paused is not None:
            self._values["paused"] = paused
        if progress_deadline_seconds is not None:
            self._values["progress_deadline_seconds"] = progress_deadline_seconds
        if replicas is not None:
            self._values["replicas"] = replicas
        if revision_history_limit is not None:
            self._values["revision_history_limit"] = revision_history_limit

    @builtins.property
    def selector(self) -> _LabelSelector_e7ec8693:
        '''
        :stability: experimental
        '''
        result = self._values.get("selector")
        assert result is not None, "Required property 'selector' is missing"
        return typing.cast(_LabelSelector_e7ec8693, result)

    @builtins.property
    def strategy(self) -> "StrategySpecs":
        '''
        :stability: experimental
        '''
        result = self._values.get("strategy")
        assert result is not None, "Required property 'strategy' is missing"
        return typing.cast("StrategySpecs", result)

    @builtins.property
    def template(self) -> _PodTemplateSpec_331e2248:
        '''
        :stability: experimental
        '''
        result = self._values.get("template")
        assert result is not None, "Required property 'template' is missing"
        return typing.cast(_PodTemplateSpec_331e2248, result)

    @builtins.property
    def min_ready_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("min_ready_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def paused(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("paused")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def progress_deadline_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("progress_deadline_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def revision_history_limit(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("revision_history_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ArgoSpecs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-argo-rollout.BlueGreenStrategySpecs",
    jsii_struct_bases=[],
    name_mapping={
        "active_service": "activeService",
        "anti_affinity": "antiAffinity",
        "auto_promotion_enabled": "autoPromotionEnabled",
        "auto_promotion_seconds": "autoPromotionSeconds",
        "post_promotion_analysis": "postPromotionAnalysis",
        "pre_promotion_analysis": "prePromotionAnalysis",
        "preview_replica_count": "previewReplicaCount",
        "preview_service": "previewService",
        "scale_down_delay_revision_limit": "scaleDownDelayRevisionLimit",
        "scale_down_delay_seconds": "scaleDownDelaySeconds",
    },
)
class BlueGreenStrategySpecs:
    def __init__(
        self,
        *,
        active_service: builtins.str,
        anti_affinity: typing.Optional[_PodAntiAffinity_afb5a5bc] = None,
        auto_promotion_enabled: typing.Optional[builtins.bool] = None,
        auto_promotion_seconds: typing.Optional[jsii.Number] = None,
        post_promotion_analysis: typing.Optional[AnalysisSpec] = None,
        pre_promotion_analysis: typing.Optional[AnalysisSpec] = None,
        preview_replica_count: typing.Optional[jsii.Number] = None,
        preview_service: typing.Optional[builtins.str] = None,
        scale_down_delay_revision_limit: typing.Optional[jsii.Number] = None,
        scale_down_delay_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param active_service: 
        :param anti_affinity: 
        :param auto_promotion_enabled: 
        :param auto_promotion_seconds: 
        :param post_promotion_analysis: 
        :param pre_promotion_analysis: 
        :param preview_replica_count: 
        :param preview_service: 
        :param scale_down_delay_revision_limit: 
        :param scale_down_delay_seconds: 

        :stability: experimental
        '''
        if isinstance(anti_affinity, dict):
            anti_affinity = _PodAntiAffinity_afb5a5bc(**anti_affinity)
        if isinstance(post_promotion_analysis, dict):
            post_promotion_analysis = AnalysisSpec(**post_promotion_analysis)
        if isinstance(pre_promotion_analysis, dict):
            pre_promotion_analysis = AnalysisSpec(**pre_promotion_analysis)
        self._values: typing.Dict[str, typing.Any] = {
            "active_service": active_service,
        }
        if anti_affinity is not None:
            self._values["anti_affinity"] = anti_affinity
        if auto_promotion_enabled is not None:
            self._values["auto_promotion_enabled"] = auto_promotion_enabled
        if auto_promotion_seconds is not None:
            self._values["auto_promotion_seconds"] = auto_promotion_seconds
        if post_promotion_analysis is not None:
            self._values["post_promotion_analysis"] = post_promotion_analysis
        if pre_promotion_analysis is not None:
            self._values["pre_promotion_analysis"] = pre_promotion_analysis
        if preview_replica_count is not None:
            self._values["preview_replica_count"] = preview_replica_count
        if preview_service is not None:
            self._values["preview_service"] = preview_service
        if scale_down_delay_revision_limit is not None:
            self._values["scale_down_delay_revision_limit"] = scale_down_delay_revision_limit
        if scale_down_delay_seconds is not None:
            self._values["scale_down_delay_seconds"] = scale_down_delay_seconds

    @builtins.property
    def active_service(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("active_service")
        assert result is not None, "Required property 'active_service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def anti_affinity(self) -> typing.Optional[_PodAntiAffinity_afb5a5bc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("anti_affinity")
        return typing.cast(typing.Optional[_PodAntiAffinity_afb5a5bc], result)

    @builtins.property
    def auto_promotion_enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("auto_promotion_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_promotion_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("auto_promotion_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def post_promotion_analysis(self) -> typing.Optional[AnalysisSpec]:
        '''
        :stability: experimental
        '''
        result = self._values.get("post_promotion_analysis")
        return typing.cast(typing.Optional[AnalysisSpec], result)

    @builtins.property
    def pre_promotion_analysis(self) -> typing.Optional[AnalysisSpec]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pre_promotion_analysis")
        return typing.cast(typing.Optional[AnalysisSpec], result)

    @builtins.property
    def preview_replica_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("preview_replica_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preview_service(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("preview_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scale_down_delay_revision_limit(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("scale_down_delay_revision_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scale_down_delay_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("scale_down_delay_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BlueGreenStrategySpecs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-argo-rollout.StrategySpecs",
    jsii_struct_bases=[],
    name_mapping={"blue_green": "blueGreen"},
)
class StrategySpecs:
    def __init__(self, *, blue_green: BlueGreenStrategySpecs) -> None:
        '''
        :param blue_green: 

        :stability: experimental
        '''
        if isinstance(blue_green, dict):
            blue_green = BlueGreenStrategySpecs(**blue_green)
        self._values: typing.Dict[str, typing.Any] = {
            "blue_green": blue_green,
        }

    @builtins.property
    def blue_green(self) -> BlueGreenStrategySpecs:
        '''
        :stability: experimental
        '''
        result = self._values.get("blue_green")
        assert result is not None, "Required property 'blue_green' is missing"
        return typing.cast(BlueGreenStrategySpecs, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StrategySpecs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-argo-rollout.ValueFrom",
    jsii_struct_bases=[],
    name_mapping={
        "field_ref": "fieldRef",
        "pod_template_hash_value": "podTemplateHashValue",
    },
)
class ValueFrom:
    def __init__(
        self,
        *,
        field_ref: typing.Optional[_ObjectFieldSelector_05a3d12c] = None,
        pod_template_hash_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param field_ref: 
        :param pod_template_hash_value: 

        :stability: experimental
        '''
        if isinstance(field_ref, dict):
            field_ref = _ObjectFieldSelector_05a3d12c(**field_ref)
        self._values: typing.Dict[str, typing.Any] = {}
        if field_ref is not None:
            self._values["field_ref"] = field_ref
        if pod_template_hash_value is not None:
            self._values["pod_template_hash_value"] = pod_template_hash_value

    @builtins.property
    def field_ref(self) -> typing.Optional[_ObjectFieldSelector_05a3d12c]:
        '''
        :stability: experimental
        '''
        result = self._values.get("field_ref")
        return typing.cast(typing.Optional[_ObjectFieldSelector_05a3d12c], result)

    @builtins.property
    def pod_template_hash_value(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pod_template_hash_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ValueFrom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AnalysisArgs",
    "AnalysisSpec",
    "AnalysisTemplate",
    "ArgoRollout",
    "ArgoRolloutProps",
    "ArgoSpecs",
    "BlueGreenStrategySpecs",
    "StrategySpecs",
    "ValueFrom",
]

publication.publish()
