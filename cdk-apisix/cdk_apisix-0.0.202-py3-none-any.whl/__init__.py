'''
[![NPM version](https://badge.fury.io/js/cdk-apisix.svg)](https://badge.fury.io/js/cdk-apisix)
[![PyPI version](https://badge.fury.io/py/cdk-apisix.svg)](https://badge.fury.io/py/cdk-apisix)
![Release](https://github.com/pahud/cdk-apisix/workflows/Release/badge.svg)

# cdk-apisix

CDK construct library to generate serverless [Apache APISIX](https://github.com/apache/apisix) workload on AWS Fargate

![](images/apisix-fargate-cdk.png)

# sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_apisix import Apisix

# create a standard apisix service
apisix = Apisix(stack, "apisix-demo")

# create a sample webservice with apisix in the same Amazon ECS cluster
apisix.create_web_service("flask",
    environment={
        "PLATFORM": "Apache APISIX on AWS Fargate"
    },
    image=ContainerImage.from_registry("public.ecr.aws/pahudnet/flask-docker-sample")
)
```

## deploy with required context variables

```sh
cdk deploy \
-c ADMIN_KEY_ADMIN=*********** \
-c ADMIN_KEY_VIEWER=*********** \
-c DASHBOARD_ADMIN_PASSWORD=*********** \
-c DASHBOARD_USER_PASSWORD=***********
```

## custom container image from local assets

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
Apisix(stack, "apisix-demo",
    apisix_container=ContainerImage.from_asset(path.join(__dirname, "../apisix_container")),
    dashboard_container=ContainerImage.from_asset(path.join(__dirname, "../apisix_dashboard"))
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

from ._jsii import *

import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_ecs_patterns
import aws_cdk.aws_efs
import aws_cdk.core


class Apisix(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-apisix.Apisix",
):
    '''The Apisix construct.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        apisix_container: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.ICluster] = None,
        dashboard_container: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        efs_filesystem: typing.Optional[aws_cdk.aws_efs.IFileSystem] = None,
        etcd_container: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param apisix_container: container for APISIX API service. Default: - public.ecr.aws/d7p2r8s3/apisix
        :param cluster: Amazon ECS cluster. Default: - create a new cluster
        :param dashboard_container: container for the dashboard. Default: - public.ecr.aws/d7p2r8s3/apisix-dashboard
        :param efs_filesystem: Amazon EFS filesystem for etcd data persistence. Default: - ceate a new filesystem
        :param etcd_container: container for the etcd. Default: - public.ecr.aws/eks-distro/etcd-io/etcd:v3.4.14-eks-1-18-1
        :param vpc: Vpc for the APISIX. Default: - create a new VPC or use existing one
        '''
        props = ApisixProps(
            apisix_container=apisix_container,
            cluster=cluster,
            dashboard_container=dashboard_container,
            efs_filesystem=efs_filesystem,
            etcd_container=etcd_container,
            vpc=vpc,
        )

        jsii.create(Apisix, self, [scope, id, props])

    @jsii.member(jsii_name="createWebService")
    def create_web_service(
        self,
        id: builtins.str,
        *,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        image: typing.Optional[aws_cdk.aws_ecs.RepositoryImage] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> aws_cdk.aws_ecs_patterns.NetworkLoadBalancedFargateService:
        '''Create a basic web service on AWS Fargate.

        :param id: -
        :param environment: 
        :param image: 
        :param port: 
        '''
        options = WebServiceOptions(environment=environment, image=image, port=port)

        return typing.cast(aws_cdk.aws_ecs_patterns.NetworkLoadBalancedFargateService, jsii.invoke(self, "createWebService", [id, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> aws_cdk.aws_ecs.ICluster:
        return typing.cast(aws_cdk.aws_ecs.ICluster, jsii.get(self, "cluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="envVar")
    def env_var(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "envVar"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-apisix.ApisixProps",
    jsii_struct_bases=[],
    name_mapping={
        "apisix_container": "apisixContainer",
        "cluster": "cluster",
        "dashboard_container": "dashboardContainer",
        "efs_filesystem": "efsFilesystem",
        "etcd_container": "etcdContainer",
        "vpc": "vpc",
    },
)
class ApisixProps:
    def __init__(
        self,
        *,
        apisix_container: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.ICluster] = None,
        dashboard_container: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        efs_filesystem: typing.Optional[aws_cdk.aws_efs.IFileSystem] = None,
        etcd_container: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''construct properties for Apisix.

        :param apisix_container: container for APISIX API service. Default: - public.ecr.aws/d7p2r8s3/apisix
        :param cluster: Amazon ECS cluster. Default: - create a new cluster
        :param dashboard_container: container for the dashboard. Default: - public.ecr.aws/d7p2r8s3/apisix-dashboard
        :param efs_filesystem: Amazon EFS filesystem for etcd data persistence. Default: - ceate a new filesystem
        :param etcd_container: container for the etcd. Default: - public.ecr.aws/eks-distro/etcd-io/etcd:v3.4.14-eks-1-18-1
        :param vpc: Vpc for the APISIX. Default: - create a new VPC or use existing one
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if apisix_container is not None:
            self._values["apisix_container"] = apisix_container
        if cluster is not None:
            self._values["cluster"] = cluster
        if dashboard_container is not None:
            self._values["dashboard_container"] = dashboard_container
        if efs_filesystem is not None:
            self._values["efs_filesystem"] = efs_filesystem
        if etcd_container is not None:
            self._values["etcd_container"] = etcd_container
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def apisix_container(self) -> typing.Optional[aws_cdk.aws_ecs.ContainerImage]:
        '''container for APISIX API service.

        :default: - public.ecr.aws/d7p2r8s3/apisix
        '''
        result = self._values.get("apisix_container")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ContainerImage], result)

    @builtins.property
    def cluster(self) -> typing.Optional[aws_cdk.aws_ecs.ICluster]:
        '''Amazon ECS cluster.

        :default: - create a new cluster
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ICluster], result)

    @builtins.property
    def dashboard_container(self) -> typing.Optional[aws_cdk.aws_ecs.ContainerImage]:
        '''container for the dashboard.

        :default: - public.ecr.aws/d7p2r8s3/apisix-dashboard
        '''
        result = self._values.get("dashboard_container")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ContainerImage], result)

    @builtins.property
    def efs_filesystem(self) -> typing.Optional[aws_cdk.aws_efs.IFileSystem]:
        '''Amazon EFS filesystem for etcd data persistence.

        :default: - ceate a new filesystem
        '''
        result = self._values.get("efs_filesystem")
        return typing.cast(typing.Optional[aws_cdk.aws_efs.IFileSystem], result)

    @builtins.property
    def etcd_container(self) -> typing.Optional[aws_cdk.aws_ecs.ContainerImage]:
        '''container for the etcd.

        :default: - public.ecr.aws/eks-distro/etcd-io/etcd:v3.4.14-eks-1-18-1
        '''
        result = self._values.get("etcd_container")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ContainerImage], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''Vpc for the APISIX.

        :default: - create a new VPC or use existing one
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApisixProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-apisix.WebServiceOptions",
    jsii_struct_bases=[],
    name_mapping={"environment": "environment", "image": "image", "port": "port"},
)
class WebServiceOptions:
    def __init__(
        self,
        *,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        image: typing.Optional[aws_cdk.aws_ecs.RepositoryImage] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''options for createWebService.

        :param environment: 
        :param image: 
        :param port: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if environment is not None:
            self._values["environment"] = environment
        if image is not None:
            self._values["image"] = image
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def image(self) -> typing.Optional[aws_cdk.aws_ecs.RepositoryImage]:
        result = self._values.get("image")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.RepositoryImage], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebServiceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Apisix",
    "ApisixProps",
    "WebServiceOptions",
]

publication.publish()
