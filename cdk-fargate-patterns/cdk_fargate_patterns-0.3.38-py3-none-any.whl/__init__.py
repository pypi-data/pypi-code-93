'''
[![NPM version](https://badge.fury.io/js/cdk-fargate-patterns.svg)](https://badge.fury.io/js/cdk-fargate-patterns)
[![PyPI version](https://badge.fury.io/py/cdk-fargate-patterns.svg)](https://badge.fury.io/py/cdk-fargate-patterns)
[![Release](https://github.com/pahud/cdk-fargate-patterns/actions/workflows/release.yml/badge.svg)](https://github.com/pahud/cdk-fargate-patterns/actions/workflows/release.yml)

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

# cdk-fargate-patterns

CDK patterns for serverless container with AWS Fargate

# `DualAlbFargateService`

![](images/DualAlbFargateService.svg)

Inspired by *Vijay Menon* from the [AWS blog post](https://aws.amazon.com/blogs/containers/how-to-use-multiple-load-balancer-target-group-support-for-amazon-ecs-to-access-internal-and-external-service-endpoint-using-the-same-dns-name/) introduced in 2019, `DualAlbFargateService` allows you to create one or many fargate services with both internet-facing ALB and internal ALB associated with all services. With this pattern, fargate services will be allowed to intercommunicat via internal ALB while external inbound traffic will be spread across the same service tasks through internet-facing ALB.

The sample below will create 3 fargate services associated with both external and internal ALBs. The internal ALB will have an alias(`internal.svc.local`) auto-configured from Route 53 so services can interconnect through the private ALB endpoint.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
DualAlbFargateService(stack, "Service",
    spot=True, # FARGATE_SPOT only cluster
    tasks=[{
        "task": order_task,
        "desired_count": 2,
        "external": {"port": 443, "certificate": certificate},
        "internal": {"port": 80},
        # customize the service autoscaling policy
        "scaling_policy": {
            "max_capacity": 20,
            "request_per_target": 1000,
            "target_cpu_utilization": 50
        }
    }, {"task": customer_task, "desired_count": 2, "internal": {"port": 8080}}, {"task": product_task, "desired_count": 2, "internal": {"port": 9090}}, {
        "task": task,
        "desired_count": 1,
        "internal": {"port": 50051, "certificate": [cert]},
        "external": {"port": 50051, "certificate": [cert]},
        "protocol_version": elbv2.ApplicationProtocolVersion.GRPC,
        "health_check": {
            "healthy_grpc_codes": "12"
        }
    }
    ],
    route53_ops={
        "zone_name": "svc.local",
        "external_elb_record_name": "external",
        "internal_elb_record_name": "internal"
    }
)
```

# `DualNlbFargateService`

Similar to `DualAlbFargateService`, you are allowed to deploy multiple container services with AWS Fargate as well as external NLB and internal NLB.

To allowed ingress traffic, you will need to explicitly add ingress rules on the `connections`:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
nlb_service = DualNlbFargateService(stack, "NLBService",
    tasks=[...]
)

# we need this to allow ingress traffic from public internet only for the order service
nlbService.service[0].connections.allow_from_any_ipv4(ec2.Port.tcp(8080))
# allow from VPC
nlb_service.service.for_each(s => {
      s.connections.allowFrom(ec2.Peer.ipv4(nlbService.vpc.vpcCidrBlock), ec2.Port.tcp(8080));
    })
```

## ALB Listener Rules Support

To share the ALB listener with multiple services, use `forwardConditions` to specify custom rules.

The sample below defines three services sharing a single extneral listener on HTTPS(TCP 443) with different host names while
interconnecting internally with different listeners on the internal ALB.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
DualAlbFargateService(stack, "ALBService",
    spot=True, # FARGATE_SPOT only cluster
    enable_execute_command=True,
    tasks=[{
        "task": order_task,
        "desired_count": 2,
        "internal": {"port": 80},
        "external": {
            "port": 443,
            "certificate": [cert],
            "forward_conditions": [elbv2.ListenerCondition.host_headers(["order.example.com"])]
        }
    }, {
        "task": customer_task,
        "desired_count": 1,
        "external": {
            "port": 443,
            "certificate": [cert],
            "forward_conditions": [elbv2.ListenerCondition.host_headers(["customer.example.com"])]
        },
        "internal": {"port": 8080}
    }, {
        "task": product_task,
        "desired_count": 1,
        "external": {
            "port": 443,
            "certificate": [cert],
            "forward_conditions": [elbv2.ListenerCondition.host_headers(["product.example.com"])]
        },
        "internal": {"port": 9090}
    }
    ]
)
```

## Fargate Spot Support

By enabling the `spot` property, 100% fargate spot tasks will be provisioned to help you save up to 70%. Check more details about [Fargate Spot](https://aws.amazon.com/about-aws/whats-new/2019/12/aws-launches-fargate-spot-save-up-to-70-for-fault-tolerant-applications/?nc1=h_ls). This is a handy catch-all flag to force all tasks to be `FARGATE_SPOT` only.

To specify mixed strategy with partial `FARGATE` and partial `FARGATE_SPOT`, specify the `capacityProviderStrategy` for individual tasks like.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
DualAlbFargateService(stack, "Service",
    tasks=[{
        "task": customer_task,
        "internal": {"port": 8080},
        "desired_count": 2,
        "capacity_provider_strategy": [{
            "capacity_provider": "FARGATE",
            "base": 1,
            "weight": 1
        }, {
            "capacity_provider": "FARGATE_SPOT",
            "base": 0,
            "weight": 3
        }
        ]
    }
    ]
)
```

The custom capacity provider strategy will be applied if `capacityProviderStretegy` is specified, otherwise, 100% spot will be used when `spot: true`. The default policy is 100% Fargate on-demand.

### Fargate Spot Termination Handling

By default, if fargate spot capacity is available in the cluster, a fargate spot termination handler Lambda function will be created with proper IAM role policies to handle the termination event to ensure we deregister the fargate spot task from target groups gracefully. While it's a recommended feature, you may opt out with `spotTerminationHandler: false`.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
DualAlbFargateService(stack, "Service",
    spot=True, # FARGATE_SPOT only cluster
    spot_termination_handler=False, ...
)
```

## ECS Exec

Simply turn on the `enableExecuteCommand` property to enable the [ECS Exec](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html) support for all services.

## ECS deployment circuit breaker

ECS deployment circuit breaker automatically rolls back unhealthy service deployments without the need for manual intervention. By default this feature is enabled, you can opt out with `circuitBreaker: false`. Read the [docummentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html) or [blog post](https://aws.amazon.com/tw/blogs/containers/announcing-amazon-ecs-deployment-circuit-breaker/) for more details.

## Internal, External or Both

Specify the `internal` or `external` property to expose your service internally, externally or both.

The `certificate` property implies `HTTPS` protocol.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
DualAlbFargateService(stack, "Service",
    tasks=[{"task": task1, "internal": {"port": 8080}}, {"task": task2, "external": {"port": 8081}}, {
        "task": task3,
        "external": {"port": 443, "certificate": my_acm_cert},
        "internal": {"port": 8888}
    }
    ]
)
```

## VPC Subnets

By default, all tasks will be deployed in the private subnets. You will need the NAT gateway for the default route associated with the private subnets to ensure the task can successfully pull the container images.

However, you are allowed to specify `vpcSubnets` to customize the subnet selection.

To deploy all tasks in public subnets, one per AZ:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
DualAlbFargateService(stack, "Service",
    vpc_subnets={
        "subnet_type": ec2.SubnetType.PUBLIC,
        "one_per_az": True
    }, ...
)
```

This will implicitly enable the `auto assign public IP` for each fargate task so the task can successfully pull the container images from external registry. However, the ingress traffic will still be balanced via the external ALB.

To deploy all tasks in specific subnets:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
DualAlbFargateService(stack, "Service",
    vpc_subnets={
        "subnets": [
            ec2.Subnet.from_subnet_id(stack, "sub-1a", "subnet-0e9460dbcfc4cf6ee"),
            ec2.Subnet.from_subnet_id(stack, "sub-1b", "subnet-0562f666bdf5c29af"),
            ec2.Subnet.from_subnet_id(stack, "sub-1c", "subnet-00ab15c0022872f06")
        ]
    }, ...
)
```

### Import an existing Cluster

!!! Before using an existing `ECS Cluster`, please make sure you have the following:

* see : [Adding Fargate capacity providers to an existing cluster](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html#fargate-capacity-providers-existing-cluster)

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
vpc = ec2.Vpc.from_lookup(stack, "defVpc", is_default=True)
sg = ec2.SecurityGroup(stack, "demo-sg",
    vpc=vpc
)
exist_cluster = ecs.Cluster.from_cluster_attributes(stack, "existCluster",
    security_groups=[sg],
    cluster_name="existCluster",
    vpc=vpc
)

DualAlbFargateService(stack, "Service",
    enable_execute_command=True,
    cluster=exist_cluster,
    tasks=[{
        "task": nginx,
        "desired_count": 1,
        "external": {"port": 80},
        "capacity_provider_strategy": [{
            "capacity_provider": "FARGATE_SPOT",
            "weight": 1
        }]
    }
    ]
)
```

## Sample Application

This repository comes with a sample applicaiton with 3 services in Golang. On deployment, the `Order` service will be exposed externally on external ALB port `80` and all requests to the `Order` service will trigger sub-requests internally to another other two services(`product` and `customer`) through the internal ALB and eventually aggregate the response back to the client.

![](images/DualAlbFargateService.svg)

## Deploy

To deploy the sample application in you default VPC:

```sh
// install first
$ yarn install
// compile the ts to js
$ yarn build
$ npx cdk --app lib/integ.default.js -c use_default_vpc=1 diff
$ npx cdk --app lib/integ.default.js -c use_default_vpc=1 deploy
```

To deploy with HTTPS-only with existing ACM certificate in your default VPC:

```sh
$ npx cdk --app lib/integ.default.js deploy -c use_default_vpc=1 -c ACM_CERT_ARN=<YOUR_ACM_CERT_ARN>
```

On deployment complete, you will see the external ALB endpoint in the CDK output. `cURL` the external HTTP endpoint and you should be able to see the aggregated response.

```sh
$ curl http://demo-Servi-EH1OINYDWDU9-1397122594.ap-northeast-1.elb.amazonaws.com
or
$ curl https://<YOUR_CUSTOM_DOMAIN_NAME>

{"service":"order", "version":"1.0"}
{"service":"product","version":"1.0"}
{"service":"customer","version":"1.0"}
```

# `WordPress`

Use the `WordPress` construct to create a serverless **WordPress** service with AWS Fargate, Amazon EFS filesystem and Aurora serverless database. All credentials auto generated from the **AWS Secret Manager** and securely inject the credentials into the serverless container with the auto generated IAM task execution role.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
WordPress(stack, "WP",
    aurora_serverless=True,
    spot=True,
    enable_execute_command=True
)
```

# `Laravel`

The `Laravl` construct is provided as a high-level abstraction that allows you to create a modern Laravel environment running on `AWS Fargate` and `Amazon Aurora Serverless`. Here comes two variants as the reference:

**laravel-bitnami** - based on [bitnami/laravel](https://hub.docker.com/r/bitnami/laravel/) with `artisan` running as the built-in web server.

**laravel-nginx-php-fpm** - laravel with nginx and php-fpm maintained by [Ernest Chiang](https://github.com/dwchiang).

Simply point `code` to your local Laravel codebase and it takes care everything else for you.

## Samples

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
#
# laravel-bitnami
#
Laravel(stack, "LaravelBitnamiDemo",
    aurora_serverless=True,
    spot=True,
    enable_execute_command=True,
    code=path.join(__dirname, "../services/laravel-bitnami"),
    container_port=3000,
    loadbalancer={"port": 80}
)

#
# laravel-nginx-php-fpm
#
Laravel(stack, "LaravelNginxDemo",
    aurora_serverless=True,
    spot=True,
    enable_execute_command=True,
    code=path.join(__dirname, "../services/laravel-nginx-php-fpm"),
    loadbalancer={"port": 80}
)
```

See [integ.laravel.ts](src/integ.laravel.ts) for the full code sample.

# Local development and testing

The [docker-compose.yml](./services/docker-compose.yml) is provided with all sample services in the repository. To bring up all services locally, run:

```sh
$ cd services
$ docker compose up
```

Use `cURL` to test locally:

```
curl http://localhost
```

Response:

```
{"service":"order","version":"1.0"}
{"service":"product","version":"1.0"}
{"service":"customer","version":"1.0"}
```

# FAQ

Q: What is the difference between `cdk-fargate-patterns` and [aws-ecs-patterns](https://github.com/aws/aws-cdk/tree/master/packages/%40aws-cdk/aws-ecs-patterns)?

A: `aws-ecs-patterns` comes with a few patterns around Amazon ECS with AWS Fargate or AWS EC2 and focuses on some scenarios with single service and single ELB like `ApplicationLoadBalancedFargateService` and `NetworkLoadBalancedFargateService`. However, `cdk-fargate-patterns` is trying to explore use cases on modern application which usually comes with multiple container services grouped as a deployment with inter-service connectivity as well as ingress traffic from external internet by seperating the internal ELB from the external one.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section --><!-- prettier-ignore-start --><!-- markdownlint-disable --><table>
  <tr>
    <td align="center"><a href="https://blog.neilkuan.net"><img src="https://avatars.githubusercontent.com/u/46012524?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Neil Kuan</b></sub></a><br /><a href="#design-neilkuan" title="Design">🎨</a> <a href="https://github.com/pahud/cdk-fargate-patterns/commits?author=neilkuan" title="Code">💻</a> <a href="https://github.com/pahud/cdk-fargate-patterns/commits?author=neilkuan" title="Tests">⚠️</a> <a href="#example-neilkuan" title="Examples">💡</a></td>
    <td align="center"><a href="https://www.ernestchiang.com"><img src="https://avatars.githubusercontent.com/u/251263?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Ernest Chiang</b></sub></a><br /><a href="#ideas-dwchiang" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/pahud/cdk-fargate-patterns/commits?author=dwchiang" title="Tests">⚠️</a> <a href="https://github.com/pahud/cdk-fargate-patterns/commits?author=dwchiang" title="Code">💻</a> <a href="#example-dwchiang" title="Examples">💡</a></td>
    <td align="center"><a href="https://clarence.tw"><img src="https://avatars.githubusercontent.com/u/5698291?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Clarence</b></sub></a><br /><a href="#example-clarencetw" title="Examples">💡</a> <a href="https://github.com/pahud/cdk-fargate-patterns/commits?author=clarencetw" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/paper5487"><img src="https://avatars.githubusercontent.com/u/15643225?v=4?s=100" width="100px;" alt=""/><br /><sub><b>paper5487</b></sub></a><br /><a href="https://github.com/pahud/cdk-fargate-patterns/issues?q=author%3Apaper5487" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/plarsson"><img src="https://avatars.githubusercontent.com/u/903607?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Peter Larsson</b></sub></a><br /><a href="#ideas-plarsson" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/LeoChien-SC"><img src="https://avatars.githubusercontent.com/u/81736089?v=4?s=100" width="100px;" alt=""/><br /><sub><b>LeoChien-SC</b></sub></a><br /><a href="https://github.com/pahud/cdk-fargate-patterns/issues?q=author%3ALeoChien-SC" title="Bug reports">🐛</a></td>
  </tr>
</table><!-- markdownlint-restore --><!-- prettier-ignore-end --><!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
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
import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_efs
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_rds
import aws_cdk.aws_secretsmanager
import aws_cdk.core


class BaseFargateService(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-fargate-patterns.BaseFargateService",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        tasks: typing.Sequence["FargateTaskProps"],
        circuit_breaker: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.ICluster] = None,
        cluster_props: typing.Optional[aws_cdk.aws_ecs.ClusterProps] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional["Route53Options"] = None,
        spot: typing.Optional[builtins.bool] = None,
        spot_termination_handler: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param tasks: 
        :param circuit_breaker: Enable the ECS service circuit breaker. Default: true
        :param cluster: Use existing ECS Cluster. Default: - create a new ECS Cluster.
        :param cluster_props: The properties used to define an ECS cluster. Default: - Create vpc and enable Fargate Capacity Providers.
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param spot_termination_handler: Enable the fargate spot termination handler. Default: true
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        '''
        props = BaseFargateServiceProps(
            tasks=tasks,
            circuit_breaker=circuit_breaker,
            cluster=cluster,
            cluster_props=cluster_props,
            enable_execute_command=enable_execute_command,
            route53_ops=route53_ops,
            spot=spot,
            spot_termination_handler=spot_termination_handler,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(BaseFargateService, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> typing.List[aws_cdk.aws_ecs.FargateService]:
        '''The service(s) created from the task(s).'''
        return typing.cast(typing.List[aws_cdk.aws_ecs.FargateService], jsii.get(self, "service"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC.'''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableLoadBalancerAlias")
    def _enable_load_balancer_alias(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enableLoadBalancerAlias"))

    @_enable_load_balancer_alias.setter
    def _enable_load_balancer_alias(self, value: builtins.bool) -> None:
        jsii.set(self, "enableLoadBalancerAlias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasExternalLoadBalancer")
    def _has_external_load_balancer(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasExternalLoadBalancer"))

    @_has_external_load_balancer.setter
    def _has_external_load_balancer(self, value: builtins.bool) -> None:
        jsii.set(self, "hasExternalLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasInternalLoadBalancer")
    def _has_internal_load_balancer(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasInternalLoadBalancer"))

    @_has_internal_load_balancer.setter
    def _has_internal_load_balancer(self, value: builtins.bool) -> None:
        jsii.set(self, "hasInternalLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnets")
    def _vpc_subnets(self) -> aws_cdk.aws_ec2.SubnetSelection:
        return typing.cast(aws_cdk.aws_ec2.SubnetSelection, jsii.get(self, "vpcSubnets"))

    @_vpc_subnets.setter
    def _vpc_subnets(self, value: aws_cdk.aws_ec2.SubnetSelection) -> None:
        jsii.set(self, "vpcSubnets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneName")
    def _zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @_zone_name.setter
    def _zone_name(self, value: builtins.str) -> None:
        jsii.set(self, "zoneName", value)


class _BaseFargateServiceProxy(BaseFargateService):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseFargateService).__jsii_proxy_class__ = lambda : _BaseFargateServiceProxy


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.BaseFargateServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "tasks": "tasks",
        "circuit_breaker": "circuitBreaker",
        "cluster": "cluster",
        "cluster_props": "clusterProps",
        "enable_execute_command": "enableExecuteCommand",
        "route53_ops": "route53Ops",
        "spot": "spot",
        "spot_termination_handler": "spotTerminationHandler",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class BaseFargateServiceProps:
    def __init__(
        self,
        *,
        tasks: typing.Sequence["FargateTaskProps"],
        circuit_breaker: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.ICluster] = None,
        cluster_props: typing.Optional[aws_cdk.aws_ecs.ClusterProps] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional["Route53Options"] = None,
        spot: typing.Optional[builtins.bool] = None,
        spot_termination_handler: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param tasks: 
        :param circuit_breaker: Enable the ECS service circuit breaker. Default: true
        :param cluster: Use existing ECS Cluster. Default: - create a new ECS Cluster.
        :param cluster_props: The properties used to define an ECS cluster. Default: - Create vpc and enable Fargate Capacity Providers.
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param spot_termination_handler: Enable the fargate spot termination handler. Default: true
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        '''
        if isinstance(cluster_props, dict):
            cluster_props = aws_cdk.aws_ecs.ClusterProps(**cluster_props)
        if isinstance(route53_ops, dict):
            route53_ops = Route53Options(**route53_ops)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "tasks": tasks,
        }
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if cluster is not None:
            self._values["cluster"] = cluster
        if cluster_props is not None:
            self._values["cluster_props"] = cluster_props
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if route53_ops is not None:
            self._values["route53_ops"] = route53_ops
        if spot is not None:
            self._values["spot"] = spot
        if spot_termination_handler is not None:
            self._values["spot_termination_handler"] = spot_termination_handler
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def tasks(self) -> typing.List["FargateTaskProps"]:
        result = self._values.get("tasks")
        assert result is not None, "Required property 'tasks' is missing"
        return typing.cast(typing.List["FargateTaskProps"], result)

    @builtins.property
    def circuit_breaker(self) -> typing.Optional[builtins.bool]:
        '''Enable the ECS service circuit breaker.

        :default: true

        :see: - https://aws.amazon.com/tw/blogs/containers/announcing-amazon-ecs-deployment-circuit-breaker/
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cluster(self) -> typing.Optional[aws_cdk.aws_ecs.ICluster]:
        '''Use existing ECS Cluster.

        :default: - create a new ECS Cluster.
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ICluster], result)

    @builtins.property
    def cluster_props(self) -> typing.Optional[aws_cdk.aws_ecs.ClusterProps]:
        '''The properties used to define an ECS cluster.

        :default: - Create vpc and enable Fargate Capacity Providers.
        '''
        result = self._values.get("cluster_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ClusterProps], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable ECS Exec support.

        :default: false

        :see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def route53_ops(self) -> typing.Optional["Route53Options"]:
        result = self._values.get("route53_ops")
        return typing.cast(typing.Optional["Route53Options"], result)

    @builtins.property
    def spot(self) -> typing.Optional[builtins.bool]:
        '''create a FARGATE_SPOT only cluster.

        :default: false
        '''
        result = self._values.get("spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def spot_termination_handler(self) -> typing.Optional[builtins.bool]:
        '''Enable the fargate spot termination handler.

        :default: true

        :see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html#fargate-capacity-providers-termination
        '''
        result = self._values.get("spot_termination_handler")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''The subnets to associate with the service.

        :default:

        -

        {
        subnetType: ec2.SubnetType.PRIVATE,
        }
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseFargateServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Database(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-fargate-patterns.Database",
):
    '''Represents the database instance or database cluster.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        allow_from: typing.Optional[aws_cdk.aws_ec2.IConnectable] = None,
        aurora_serverless: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: The VPC for the database.
        :param allow_from: Allow database connection. Default: - the whole VPC CIDR
        :param aurora_serverless: enable aurora serverless. Default: false
        :param backup_retention: database backup retension. Default: - 7 days
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param database_subnets: VPC subnets for database.
        :param default_database_name: Default database name to create. Default: - do not create any default database
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param instance_type: The database instance type. Default: r5.large
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        '''
        props = DatabaseProps(
            vpc=vpc,
            allow_from=allow_from,
            aurora_serverless=aurora_serverless,
            backup_retention=backup_retention,
            cluster_engine=cluster_engine,
            database_subnets=database_subnets,
            default_database_name=default_database_name,
            instance_engine=instance_engine,
            instance_type=instance_type,
            single_db_instance=single_db_instance,
        )

        jsii.create(Database, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterEndpointHostname")
    def cluster_endpoint_hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterEndpointHostname"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.get(self, "secret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.DatabaseCofig",
    jsii_struct_bases=[],
    name_mapping={
        "connections": "connections",
        "endpoint": "endpoint",
        "identifier": "identifier",
        "secret": "secret",
    },
)
class DatabaseCofig:
    def __init__(
        self,
        *,
        connections: aws_cdk.aws_ec2.Connections,
        endpoint: builtins.str,
        identifier: builtins.str,
        secret: aws_cdk.aws_secretsmanager.ISecret,
    ) -> None:
        '''Database configuration.

        :param connections: The database connnections.
        :param endpoint: The endpoint address for the database.
        :param identifier: The databasae identifier.
        :param secret: The database secret.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "connections": connections,
            "endpoint": endpoint,
            "identifier": identifier,
            "secret": secret,
        }

    @builtins.property
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''The database connnections.'''
        result = self._values.get("connections")
        assert result is not None, "Required property 'connections' is missing"
        return typing.cast(aws_cdk.aws_ec2.Connections, result)

    @builtins.property
    def endpoint(self) -> builtins.str:
        '''The endpoint address for the database.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identifier(self) -> builtins.str:
        '''The databasae identifier.'''
        result = self._values.get("identifier")
        assert result is not None, "Required property 'identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''The database secret.'''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseCofig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.DatabaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "allow_from": "allowFrom",
        "aurora_serverless": "auroraServerless",
        "backup_retention": "backupRetention",
        "cluster_engine": "clusterEngine",
        "database_subnets": "databaseSubnets",
        "default_database_name": "defaultDatabaseName",
        "instance_engine": "instanceEngine",
        "instance_type": "instanceType",
        "single_db_instance": "singleDbInstance",
    },
)
class DatabaseProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        allow_from: typing.Optional[aws_cdk.aws_ec2.IConnectable] = None,
        aurora_serverless: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param vpc: The VPC for the database.
        :param allow_from: Allow database connection. Default: - the whole VPC CIDR
        :param aurora_serverless: enable aurora serverless. Default: false
        :param backup_retention: database backup retension. Default: - 7 days
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param database_subnets: VPC subnets for database.
        :param default_database_name: Default database name to create. Default: - do not create any default database
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param instance_type: The database instance type. Default: r5.large
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        '''
        if isinstance(database_subnets, dict):
            database_subnets = aws_cdk.aws_ec2.SubnetSelection(**database_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if allow_from is not None:
            self._values["allow_from"] = allow_from
        if aurora_serverless is not None:
            self._values["aurora_serverless"] = aurora_serverless
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if cluster_engine is not None:
            self._values["cluster_engine"] = cluster_engine
        if database_subnets is not None:
            self._values["database_subnets"] = database_subnets
        if default_database_name is not None:
            self._values["default_database_name"] = default_database_name
        if instance_engine is not None:
            self._values["instance_engine"] = instance_engine
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if single_db_instance is not None:
            self._values["single_db_instance"] = single_db_instance

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC for the database.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def allow_from(self) -> typing.Optional[aws_cdk.aws_ec2.IConnectable]:
        '''Allow database connection.

        :default: - the whole VPC CIDR
        '''
        result = self._values.get("allow_from")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IConnectable], result)

    @builtins.property
    def aurora_serverless(self) -> typing.Optional[builtins.bool]:
        '''enable aurora serverless.

        :default: false
        '''
        result = self._values.get("aurora_serverless")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''database backup retension.

        :default: - 7 days
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def cluster_engine(self) -> typing.Optional[aws_cdk.aws_rds.IClusterEngine]:
        '''The database cluster engine.

        :default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        '''
        result = self._values.get("cluster_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IClusterEngine], result)

    @builtins.property
    def database_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnets for database.'''
        result = self._values.get("database_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def default_database_name(self) -> typing.Optional[builtins.str]:
        '''Default database name to create.

        :default: - do not create any default database
        '''
        result = self._values.get("default_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_engine(self) -> typing.Optional[aws_cdk.aws_rds.IInstanceEngine]:
        '''The database instance engine.

        :default: - MySQL 8.0.21
        '''
        result = self._values.get("instance_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IInstanceEngine], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''The database instance type.

        :default: r5.large
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def single_db_instance(self) -> typing.Optional[builtins.bool]:
        '''Whether to use single RDS instance rather than RDS cluster.

        Not recommended for production.

        :default: false
        '''
        result = self._values.get("single_db_instance")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DualAlbFargateService(
    BaseFargateService,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-fargate-patterns.DualAlbFargateService",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        external_alb_idle_timeout: typing.Optional[aws_cdk.core.Duration] = None,
        internal_alb_idle_timeout: typing.Optional[aws_cdk.core.Duration] = None,
        tasks: typing.Sequence["FargateTaskProps"],
        circuit_breaker: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.ICluster] = None,
        cluster_props: typing.Optional[aws_cdk.aws_ecs.ClusterProps] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional["Route53Options"] = None,
        spot: typing.Optional[builtins.bool] = None,
        spot_termination_handler: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param external_alb_idle_timeout: The external load balancer idle timeout, in seconds. Default: - 60.
        :param internal_alb_idle_timeout: The internal load balancer idle timeout, in seconds. Default: - 60.
        :param tasks: 
        :param circuit_breaker: Enable the ECS service circuit breaker. Default: true
        :param cluster: Use existing ECS Cluster. Default: - create a new ECS Cluster.
        :param cluster_props: The properties used to define an ECS cluster. Default: - Create vpc and enable Fargate Capacity Providers.
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param spot_termination_handler: Enable the fargate spot termination handler. Default: true
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        '''
        props = DualAlbFargateServiceProps(
            external_alb_idle_timeout=external_alb_idle_timeout,
            internal_alb_idle_timeout=internal_alb_idle_timeout,
            tasks=tasks,
            circuit_breaker=circuit_breaker,
            cluster=cluster,
            cluster_props=cluster_props,
            enable_execute_command=enable_execute_command,
            route53_ops=route53_ops,
            spot=spot,
            spot_termination_handler=spot_termination_handler,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(DualAlbFargateService, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalAlb")
    def external_alb(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer]:
        '''The external ALB.'''
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer], jsii.get(self, "externalAlb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalAlb")
    def internal_alb(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer]:
        '''The internal ALB.'''
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer], jsii.get(self, "internalAlb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalAlbApplicationListeners")
    def _external_alb_application_listeners(
        self,
    ) -> typing.Mapping[builtins.str, aws_cdk.aws_elasticloadbalancingv2.ApplicationListener]:
        return typing.cast(typing.Mapping[builtins.str, aws_cdk.aws_elasticloadbalancingv2.ApplicationListener], jsii.get(self, "externalAlbApplicationListeners"))

    @_external_alb_application_listeners.setter
    def _external_alb_application_listeners(
        self,
        value: typing.Mapping[builtins.str, aws_cdk.aws_elasticloadbalancingv2.ApplicationListener],
    ) -> None:
        jsii.set(self, "externalAlbApplicationListeners", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalAlbApplicationListeners")
    def _internal_alb_application_listeners(
        self,
    ) -> typing.Mapping[builtins.str, aws_cdk.aws_elasticloadbalancingv2.ApplicationListener]:
        return typing.cast(typing.Mapping[builtins.str, aws_cdk.aws_elasticloadbalancingv2.ApplicationListener], jsii.get(self, "internalAlbApplicationListeners"))

    @_internal_alb_application_listeners.setter
    def _internal_alb_application_listeners(
        self,
        value: typing.Mapping[builtins.str, aws_cdk.aws_elasticloadbalancingv2.ApplicationListener],
    ) -> None:
        jsii.set(self, "internalAlbApplicationListeners", value)


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.DualAlbFargateServiceProps",
    jsii_struct_bases=[BaseFargateServiceProps],
    name_mapping={
        "tasks": "tasks",
        "circuit_breaker": "circuitBreaker",
        "cluster": "cluster",
        "cluster_props": "clusterProps",
        "enable_execute_command": "enableExecuteCommand",
        "route53_ops": "route53Ops",
        "spot": "spot",
        "spot_termination_handler": "spotTerminationHandler",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "external_alb_idle_timeout": "externalAlbIdleTimeout",
        "internal_alb_idle_timeout": "internalAlbIdleTimeout",
    },
)
class DualAlbFargateServiceProps(BaseFargateServiceProps):
    def __init__(
        self,
        *,
        tasks: typing.Sequence["FargateTaskProps"],
        circuit_breaker: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.ICluster] = None,
        cluster_props: typing.Optional[aws_cdk.aws_ecs.ClusterProps] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional["Route53Options"] = None,
        spot: typing.Optional[builtins.bool] = None,
        spot_termination_handler: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        external_alb_idle_timeout: typing.Optional[aws_cdk.core.Duration] = None,
        internal_alb_idle_timeout: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param tasks: 
        :param circuit_breaker: Enable the ECS service circuit breaker. Default: true
        :param cluster: Use existing ECS Cluster. Default: - create a new ECS Cluster.
        :param cluster_props: The properties used to define an ECS cluster. Default: - Create vpc and enable Fargate Capacity Providers.
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param spot_termination_handler: Enable the fargate spot termination handler. Default: true
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        :param external_alb_idle_timeout: The external load balancer idle timeout, in seconds. Default: - 60.
        :param internal_alb_idle_timeout: The internal load balancer idle timeout, in seconds. Default: - 60.
        '''
        if isinstance(cluster_props, dict):
            cluster_props = aws_cdk.aws_ecs.ClusterProps(**cluster_props)
        if isinstance(route53_ops, dict):
            route53_ops = Route53Options(**route53_ops)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "tasks": tasks,
        }
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if cluster is not None:
            self._values["cluster"] = cluster
        if cluster_props is not None:
            self._values["cluster_props"] = cluster_props
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if route53_ops is not None:
            self._values["route53_ops"] = route53_ops
        if spot is not None:
            self._values["spot"] = spot
        if spot_termination_handler is not None:
            self._values["spot_termination_handler"] = spot_termination_handler
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if external_alb_idle_timeout is not None:
            self._values["external_alb_idle_timeout"] = external_alb_idle_timeout
        if internal_alb_idle_timeout is not None:
            self._values["internal_alb_idle_timeout"] = internal_alb_idle_timeout

    @builtins.property
    def tasks(self) -> typing.List["FargateTaskProps"]:
        result = self._values.get("tasks")
        assert result is not None, "Required property 'tasks' is missing"
        return typing.cast(typing.List["FargateTaskProps"], result)

    @builtins.property
    def circuit_breaker(self) -> typing.Optional[builtins.bool]:
        '''Enable the ECS service circuit breaker.

        :default: true

        :see: - https://aws.amazon.com/tw/blogs/containers/announcing-amazon-ecs-deployment-circuit-breaker/
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cluster(self) -> typing.Optional[aws_cdk.aws_ecs.ICluster]:
        '''Use existing ECS Cluster.

        :default: - create a new ECS Cluster.
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ICluster], result)

    @builtins.property
    def cluster_props(self) -> typing.Optional[aws_cdk.aws_ecs.ClusterProps]:
        '''The properties used to define an ECS cluster.

        :default: - Create vpc and enable Fargate Capacity Providers.
        '''
        result = self._values.get("cluster_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ClusterProps], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable ECS Exec support.

        :default: false

        :see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def route53_ops(self) -> typing.Optional["Route53Options"]:
        result = self._values.get("route53_ops")
        return typing.cast(typing.Optional["Route53Options"], result)

    @builtins.property
    def spot(self) -> typing.Optional[builtins.bool]:
        '''create a FARGATE_SPOT only cluster.

        :default: false
        '''
        result = self._values.get("spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def spot_termination_handler(self) -> typing.Optional[builtins.bool]:
        '''Enable the fargate spot termination handler.

        :default: true

        :see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html#fargate-capacity-providers-termination
        '''
        result = self._values.get("spot_termination_handler")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''The subnets to associate with the service.

        :default:

        -

        {
        subnetType: ec2.SubnetType.PRIVATE,
        }
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def external_alb_idle_timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The external load balancer idle timeout, in seconds.

        :default:

        -
        60.
        '''
        result = self._values.get("external_alb_idle_timeout")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def internal_alb_idle_timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The internal load balancer idle timeout, in seconds.

        :default:

        -
        60.
        '''
        result = self._values.get("internal_alb_idle_timeout")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DualAlbFargateServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DualNlbFargateService(
    BaseFargateService,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-fargate-patterns.DualNlbFargateService",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        tasks: typing.Sequence["FargateTaskProps"],
        circuit_breaker: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.ICluster] = None,
        cluster_props: typing.Optional[aws_cdk.aws_ecs.ClusterProps] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional["Route53Options"] = None,
        spot: typing.Optional[builtins.bool] = None,
        spot_termination_handler: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param tasks: 
        :param circuit_breaker: Enable the ECS service circuit breaker. Default: true
        :param cluster: Use existing ECS Cluster. Default: - create a new ECS Cluster.
        :param cluster_props: The properties used to define an ECS cluster. Default: - Create vpc and enable Fargate Capacity Providers.
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param spot_termination_handler: Enable the fargate spot termination handler. Default: true
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        '''
        props = DualNlbFargateServiceProps(
            tasks=tasks,
            circuit_breaker=circuit_breaker,
            cluster=cluster,
            cluster_props=cluster_props,
            enable_execute_command=enable_execute_command,
            route53_ops=route53_ops,
            spot=spot,
            spot_termination_handler=spot_termination_handler,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(DualNlbFargateService, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalNlb")
    def external_nlb(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]:
        '''The external Nlb.'''
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer], jsii.get(self, "externalNlb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalNlb")
    def internal_nlb(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]:
        '''The internal Nlb.'''
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer], jsii.get(self, "internalNlb"))


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.DualNlbFargateServiceProps",
    jsii_struct_bases=[BaseFargateServiceProps],
    name_mapping={
        "tasks": "tasks",
        "circuit_breaker": "circuitBreaker",
        "cluster": "cluster",
        "cluster_props": "clusterProps",
        "enable_execute_command": "enableExecuteCommand",
        "route53_ops": "route53Ops",
        "spot": "spot",
        "spot_termination_handler": "spotTerminationHandler",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class DualNlbFargateServiceProps(BaseFargateServiceProps):
    def __init__(
        self,
        *,
        tasks: typing.Sequence["FargateTaskProps"],
        circuit_breaker: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.ICluster] = None,
        cluster_props: typing.Optional[aws_cdk.aws_ecs.ClusterProps] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        route53_ops: typing.Optional["Route53Options"] = None,
        spot: typing.Optional[builtins.bool] = None,
        spot_termination_handler: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param tasks: 
        :param circuit_breaker: Enable the ECS service circuit breaker. Default: true
        :param cluster: Use existing ECS Cluster. Default: - create a new ECS Cluster.
        :param cluster_props: The properties used to define an ECS cluster. Default: - Create vpc and enable Fargate Capacity Providers.
        :param enable_execute_command: Whether to enable ECS Exec support. Default: false
        :param route53_ops: 
        :param spot: create a FARGATE_SPOT only cluster. Default: false
        :param spot_termination_handler: Enable the fargate spot termination handler. Default: true
        :param vpc: 
        :param vpc_subnets: The subnets to associate with the service. Default: - { subnetType: ec2.SubnetType.PRIVATE, }
        '''
        if isinstance(cluster_props, dict):
            cluster_props = aws_cdk.aws_ecs.ClusterProps(**cluster_props)
        if isinstance(route53_ops, dict):
            route53_ops = Route53Options(**route53_ops)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "tasks": tasks,
        }
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if cluster is not None:
            self._values["cluster"] = cluster
        if cluster_props is not None:
            self._values["cluster_props"] = cluster_props
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if route53_ops is not None:
            self._values["route53_ops"] = route53_ops
        if spot is not None:
            self._values["spot"] = spot
        if spot_termination_handler is not None:
            self._values["spot_termination_handler"] = spot_termination_handler
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def tasks(self) -> typing.List["FargateTaskProps"]:
        result = self._values.get("tasks")
        assert result is not None, "Required property 'tasks' is missing"
        return typing.cast(typing.List["FargateTaskProps"], result)

    @builtins.property
    def circuit_breaker(self) -> typing.Optional[builtins.bool]:
        '''Enable the ECS service circuit breaker.

        :default: true

        :see: - https://aws.amazon.com/tw/blogs/containers/announcing-amazon-ecs-deployment-circuit-breaker/
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cluster(self) -> typing.Optional[aws_cdk.aws_ecs.ICluster]:
        '''Use existing ECS Cluster.

        :default: - create a new ECS Cluster.
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ICluster], result)

    @builtins.property
    def cluster_props(self) -> typing.Optional[aws_cdk.aws_ecs.ClusterProps]:
        '''The properties used to define an ECS cluster.

        :default: - Create vpc and enable Fargate Capacity Providers.
        '''
        result = self._values.get("cluster_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ClusterProps], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable ECS Exec support.

        :default: false

        :see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def route53_ops(self) -> typing.Optional["Route53Options"]:
        result = self._values.get("route53_ops")
        return typing.cast(typing.Optional["Route53Options"], result)

    @builtins.property
    def spot(self) -> typing.Optional[builtins.bool]:
        '''create a FARGATE_SPOT only cluster.

        :default: false
        '''
        result = self._values.get("spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def spot_termination_handler(self) -> typing.Optional[builtins.bool]:
        '''Enable the fargate spot termination handler.

        :default: true

        :see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html#fargate-capacity-providers-termination
        '''
        result = self._values.get("spot_termination_handler")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''The subnets to associate with the service.

        :default:

        -

        {
        subnetType: ec2.SubnetType.PRIVATE,
        }
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DualNlbFargateServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.FargateTaskProps",
    jsii_struct_bases=[],
    name_mapping={
        "task": "task",
        "capacity_provider_strategy": "capacityProviderStrategy",
        "desired_count": "desiredCount",
        "external": "external",
        "health_check": "healthCheck",
        "health_check_grace_period": "healthCheckGracePeriod",
        "internal": "internal",
        "max_healthy_percent": "maxHealthyPercent",
        "min_healthy_percent": "minHealthyPercent",
        "protocol": "protocol",
        "protocol_version": "protocolVersion",
        "scaling_policy": "scalingPolicy",
        "service_name": "serviceName",
    },
)
class FargateTaskProps:
    def __init__(
        self,
        *,
        task: aws_cdk.aws_ecs.FargateTaskDefinition,
        capacity_provider_strategy: typing.Optional[typing.Sequence[aws_cdk.aws_ecs.CapacityProviderStrategy]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        external: typing.Optional["LoadBalancerAccessibility"] = None,
        health_check: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.HealthCheck] = None,
        health_check_grace_period: typing.Optional[aws_cdk.core.Duration] = None,
        internal: typing.Optional["LoadBalancerAccessibility"] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.Protocol] = None,
        protocol_version: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocolVersion] = None,
        scaling_policy: typing.Optional["ServiceScalingPolicy"] = None,
        service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Task properties for the Fargate.

        :param task: 
        :param capacity_provider_strategy: Customized capacity provider strategy.
        :param desired_count: desired number of tasks for the service. Default: 1
        :param external: The external ELB listener. Default: - no external listener
        :param health_check: health check from elbv2 target group.
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: cdk.Duration.seconds(60),
        :param internal: The internal ELB listener. Default: - no internal listener
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: 50
        :param protocol: The target group protocol for NLB. For ALB, this option will be ignored and always set to HTTP. Default: - TCP
        :param protocol_version: The protocol version to use.
        :param scaling_policy: service autoscaling policy. Default: - { maxCapacity: 10, targetCpuUtilization: 50, requestsPerTarget: 1000 }
        :param service_name: The serviceName. Default: - auto-generated
        '''
        if isinstance(external, dict):
            external = LoadBalancerAccessibility(**external)
        if isinstance(health_check, dict):
            health_check = aws_cdk.aws_elasticloadbalancingv2.HealthCheck(**health_check)
        if isinstance(internal, dict):
            internal = LoadBalancerAccessibility(**internal)
        if isinstance(scaling_policy, dict):
            scaling_policy = ServiceScalingPolicy(**scaling_policy)
        self._values: typing.Dict[str, typing.Any] = {
            "task": task,
        }
        if capacity_provider_strategy is not None:
            self._values["capacity_provider_strategy"] = capacity_provider_strategy
        if desired_count is not None:
            self._values["desired_count"] = desired_count
        if external is not None:
            self._values["external"] = external
        if health_check is not None:
            self._values["health_check"] = health_check
        if health_check_grace_period is not None:
            self._values["health_check_grace_period"] = health_check_grace_period
        if internal is not None:
            self._values["internal"] = internal
        if max_healthy_percent is not None:
            self._values["max_healthy_percent"] = max_healthy_percent
        if min_healthy_percent is not None:
            self._values["min_healthy_percent"] = min_healthy_percent
        if protocol is not None:
            self._values["protocol"] = protocol
        if protocol_version is not None:
            self._values["protocol_version"] = protocol_version
        if scaling_policy is not None:
            self._values["scaling_policy"] = scaling_policy
        if service_name is not None:
            self._values["service_name"] = service_name

    @builtins.property
    def task(self) -> aws_cdk.aws_ecs.FargateTaskDefinition:
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(aws_cdk.aws_ecs.FargateTaskDefinition, result)

    @builtins.property
    def capacity_provider_strategy(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ecs.CapacityProviderStrategy]]:
        '''Customized capacity provider strategy.'''
        result = self._values.get("capacity_provider_strategy")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ecs.CapacityProviderStrategy]], result)

    @builtins.property
    def desired_count(self) -> typing.Optional[jsii.Number]:
        '''desired number of tasks for the service.

        :default: 1
        '''
        result = self._values.get("desired_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def external(self) -> typing.Optional["LoadBalancerAccessibility"]:
        '''The external ELB listener.

        :default: - no external listener
        '''
        result = self._values.get("external")
        return typing.cast(typing.Optional["LoadBalancerAccessibility"], result)

    @builtins.property
    def health_check(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.HealthCheck]:
        '''health check from elbv2 target group.'''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.HealthCheck], result)

    @builtins.property
    def health_check_grace_period(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started.

        :default: cdk.Duration.seconds(60),
        '''
        result = self._values.get("health_check_grace_period")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def internal(self) -> typing.Optional["LoadBalancerAccessibility"]:
        '''The internal ELB listener.

        :default: - no internal listener
        '''
        result = self._values.get("internal")
        return typing.cast(typing.Optional["LoadBalancerAccessibility"], result)

    @builtins.property
    def max_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment.

        :default: 200
        '''
        result = self._values.get("max_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment.

        :default: 50
        '''
        result = self._values.get("min_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def protocol(self) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.Protocol]:
        '''The target group protocol for NLB.

        For ALB, this option will be ignored and always set to HTTP.

        :default: - TCP
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.Protocol], result)

    @builtins.property
    def protocol_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocolVersion]:
        '''The protocol version to use.'''
        result = self._values.get("protocol_version")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationProtocolVersion], result)

    @builtins.property
    def scaling_policy(self) -> typing.Optional["ServiceScalingPolicy"]:
        '''service autoscaling policy.

        :default: - { maxCapacity: 10, targetCpuUtilization: 50, requestsPerTarget: 1000 }
        '''
        result = self._values.get("scaling_policy")
        return typing.cast(typing.Optional["ServiceScalingPolicy"], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        '''The serviceName.

        :default: - auto-generated
        '''
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Laravel(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-fargate-patterns.Laravel",
):
    '''Represents the Laravel service.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        code: builtins.str,
        loadbalancer: "LoadBalancerAccessibility",
        aurora_serverless: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        container_port: typing.Optional[jsii.Number] = None,
        database_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        efs_file_system: typing.Optional[aws_cdk.aws_efs.FileSystemProps] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        service_props: typing.Optional[FargateTaskProps] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
        spot: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code: The local path to the Laravel code base.
        :param loadbalancer: The loadbalancer accessibility for the service.
        :param aurora_serverless: Whether to use aurora serverless. When enabled, the ``databaseInstanceType`` and ``engine`` will be ignored. The ``rds.DatabaseClusterEngine.AURORA_MYSQL`` will be used as the default cluster engine instead. Default: false
        :param backup_retention: database backup retension. Default: - 7 days
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param container_port: The Laravel container port. Default: 80
        :param database_instance_type: Database instance type. Default: r5.large
        :param database_subnets: VPC subnets for database. Default: - VPC isolated subnets
        :param default_database_name: The default database name to create.
        :param efs_file_system: Options to create the EFS FileSystem.
        :param enable_execute_command: enable ECS Exec.
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param service_props: task options for the Laravel fargate service.
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        :param spot: enable fargate spot.
        :param vpc: 
        '''
        props = LaravelProps(
            code=code,
            loadbalancer=loadbalancer,
            aurora_serverless=aurora_serverless,
            backup_retention=backup_retention,
            cluster_engine=cluster_engine,
            container_port=container_port,
            database_instance_type=database_instance_type,
            database_subnets=database_subnets,
            default_database_name=default_database_name,
            efs_file_system=efs_file_system,
            enable_execute_command=enable_execute_command,
            instance_engine=instance_engine,
            service_props=service_props,
            single_db_instance=single_db_instance,
            spot=spot,
            vpc=vpc,
        )

        jsii.create(Laravel, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svc")
    def svc(self) -> DualAlbFargateService:
        return typing.cast(DualAlbFargateService, jsii.get(self, "svc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="db")
    def db(self) -> typing.Optional[Database]:
        return typing.cast(typing.Optional[Database], jsii.get(self, "db"))


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.LaravelProps",
    jsii_struct_bases=[],
    name_mapping={
        "code": "code",
        "loadbalancer": "loadbalancer",
        "aurora_serverless": "auroraServerless",
        "backup_retention": "backupRetention",
        "cluster_engine": "clusterEngine",
        "container_port": "containerPort",
        "database_instance_type": "databaseInstanceType",
        "database_subnets": "databaseSubnets",
        "default_database_name": "defaultDatabaseName",
        "efs_file_system": "efsFileSystem",
        "enable_execute_command": "enableExecuteCommand",
        "instance_engine": "instanceEngine",
        "service_props": "serviceProps",
        "single_db_instance": "singleDbInstance",
        "spot": "spot",
        "vpc": "vpc",
    },
)
class LaravelProps:
    def __init__(
        self,
        *,
        code: builtins.str,
        loadbalancer: "LoadBalancerAccessibility",
        aurora_serverless: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        container_port: typing.Optional[jsii.Number] = None,
        database_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        efs_file_system: typing.Optional[aws_cdk.aws_efs.FileSystemProps] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        service_props: typing.Optional[FargateTaskProps] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
        spot: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param code: The local path to the Laravel code base.
        :param loadbalancer: The loadbalancer accessibility for the service.
        :param aurora_serverless: Whether to use aurora serverless. When enabled, the ``databaseInstanceType`` and ``engine`` will be ignored. The ``rds.DatabaseClusterEngine.AURORA_MYSQL`` will be used as the default cluster engine instead. Default: false
        :param backup_retention: database backup retension. Default: - 7 days
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param container_port: The Laravel container port. Default: 80
        :param database_instance_type: Database instance type. Default: r5.large
        :param database_subnets: VPC subnets for database. Default: - VPC isolated subnets
        :param default_database_name: The default database name to create.
        :param efs_file_system: Options to create the EFS FileSystem.
        :param enable_execute_command: enable ECS Exec.
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param service_props: task options for the Laravel fargate service.
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        :param spot: enable fargate spot.
        :param vpc: 
        '''
        if isinstance(loadbalancer, dict):
            loadbalancer = LoadBalancerAccessibility(**loadbalancer)
        if isinstance(database_subnets, dict):
            database_subnets = aws_cdk.aws_ec2.SubnetSelection(**database_subnets)
        if isinstance(efs_file_system, dict):
            efs_file_system = aws_cdk.aws_efs.FileSystemProps(**efs_file_system)
        if isinstance(service_props, dict):
            service_props = FargateTaskProps(**service_props)
        self._values: typing.Dict[str, typing.Any] = {
            "code": code,
            "loadbalancer": loadbalancer,
        }
        if aurora_serverless is not None:
            self._values["aurora_serverless"] = aurora_serverless
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if cluster_engine is not None:
            self._values["cluster_engine"] = cluster_engine
        if container_port is not None:
            self._values["container_port"] = container_port
        if database_instance_type is not None:
            self._values["database_instance_type"] = database_instance_type
        if database_subnets is not None:
            self._values["database_subnets"] = database_subnets
        if default_database_name is not None:
            self._values["default_database_name"] = default_database_name
        if efs_file_system is not None:
            self._values["efs_file_system"] = efs_file_system
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if instance_engine is not None:
            self._values["instance_engine"] = instance_engine
        if service_props is not None:
            self._values["service_props"] = service_props
        if single_db_instance is not None:
            self._values["single_db_instance"] = single_db_instance
        if spot is not None:
            self._values["spot"] = spot
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def code(self) -> builtins.str:
        '''The local path to the Laravel code base.'''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def loadbalancer(self) -> "LoadBalancerAccessibility":
        '''The loadbalancer accessibility for the service.'''
        result = self._values.get("loadbalancer")
        assert result is not None, "Required property 'loadbalancer' is missing"
        return typing.cast("LoadBalancerAccessibility", result)

    @builtins.property
    def aurora_serverless(self) -> typing.Optional[builtins.bool]:
        '''Whether to use aurora serverless.

        When enabled, the ``databaseInstanceType`` and
        ``engine`` will be ignored. The ``rds.DatabaseClusterEngine.AURORA_MYSQL`` will be used as
        the default cluster engine instead.

        :default: false
        '''
        result = self._values.get("aurora_serverless")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''database backup retension.

        :default: - 7 days
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def cluster_engine(self) -> typing.Optional[aws_cdk.aws_rds.IClusterEngine]:
        '''The database cluster engine.

        :default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        '''
        result = self._values.get("cluster_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IClusterEngine], result)

    @builtins.property
    def container_port(self) -> typing.Optional[jsii.Number]:
        '''The Laravel container port.

        :default: 80
        '''
        result = self._values.get("container_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def database_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''Database instance type.

        :default: r5.large
        '''
        result = self._values.get("database_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def database_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnets for database.

        :default: - VPC isolated subnets
        '''
        result = self._values.get("database_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def default_database_name(self) -> typing.Optional[builtins.str]:
        '''The default database name to create.'''
        result = self._values.get("default_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def efs_file_system(self) -> typing.Optional[aws_cdk.aws_efs.FileSystemProps]:
        '''Options to create the EFS FileSystem.'''
        result = self._values.get("efs_file_system")
        return typing.cast(typing.Optional[aws_cdk.aws_efs.FileSystemProps], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''enable ECS Exec.'''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_engine(self) -> typing.Optional[aws_cdk.aws_rds.IInstanceEngine]:
        '''The database instance engine.

        :default: - MySQL 8.0.21
        '''
        result = self._values.get("instance_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IInstanceEngine], result)

    @builtins.property
    def service_props(self) -> typing.Optional[FargateTaskProps]:
        '''task options for the Laravel fargate service.'''
        result = self._values.get("service_props")
        return typing.cast(typing.Optional[FargateTaskProps], result)

    @builtins.property
    def single_db_instance(self) -> typing.Optional[builtins.bool]:
        '''Whether to use single RDS instance rather than RDS cluster.

        Not recommended for production.

        :default: false
        '''
        result = self._values.get("single_db_instance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def spot(self) -> typing.Optional[builtins.bool]:
        '''enable fargate spot.'''
        result = self._values.get("spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LaravelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.LoadBalancerAccessibility",
    jsii_struct_bases=[],
    name_mapping={
        "port": "port",
        "certificate": "certificate",
        "forward_conditions": "forwardConditions",
    },
)
class LoadBalancerAccessibility:
    def __init__(
        self,
        *,
        port: jsii.Number,
        certificate: typing.Optional[typing.Sequence[aws_cdk.aws_certificatemanager.ICertificate]] = None,
        forward_conditions: typing.Optional[typing.Sequence[aws_cdk.aws_elasticloadbalancingv2.ListenerCondition]] = None,
    ) -> None:
        '''The load balancer accessibility.

        :param port: The port of the listener.
        :param certificate: The ACM certificate for the HTTPS listener. Default: - no certificate(HTTP only)
        :param forward_conditions: Listener forward conditions. Default: - no forward conditions.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "port": port,
        }
        if certificate is not None:
            self._values["certificate"] = certificate
        if forward_conditions is not None:
            self._values["forward_conditions"] = forward_conditions

    @builtins.property
    def port(self) -> jsii.Number:
        '''The port of the listener.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_certificatemanager.ICertificate]]:
        '''The ACM certificate for the HTTPS listener.

        :default: - no certificate(HTTP only)
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_certificatemanager.ICertificate]], result)

    @builtins.property
    def forward_conditions(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_elasticloadbalancingv2.ListenerCondition]]:
        '''Listener forward conditions.

        :default: - no forward conditions.
        '''
        result = self._values.get("forward_conditions")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_elasticloadbalancingv2.ListenerCondition]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerAccessibility(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.Route53Options",
    jsii_struct_bases=[],
    name_mapping={
        "enable_load_balancer_alias": "enableLoadBalancerAlias",
        "external_elb_record_name": "externalElbRecordName",
        "internal_elb_record_name": "internalElbRecordName",
        "zone_name": "zoneName",
    },
)
class Route53Options:
    def __init__(
        self,
        *,
        enable_load_balancer_alias: typing.Optional[builtins.bool] = None,
        external_elb_record_name: typing.Optional[builtins.str] = None,
        internal_elb_record_name: typing.Optional[builtins.str] = None,
        zone_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enable_load_balancer_alias: Whether to configure the ALIAS for the LB. Default: true
        :param external_elb_record_name: the external ELB record name. Default: external
        :param internal_elb_record_name: the internal ELB record name. Default: internal
        :param zone_name: private zone name. Default: svc.local
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if enable_load_balancer_alias is not None:
            self._values["enable_load_balancer_alias"] = enable_load_balancer_alias
        if external_elb_record_name is not None:
            self._values["external_elb_record_name"] = external_elb_record_name
        if internal_elb_record_name is not None:
            self._values["internal_elb_record_name"] = internal_elb_record_name
        if zone_name is not None:
            self._values["zone_name"] = zone_name

    @builtins.property
    def enable_load_balancer_alias(self) -> typing.Optional[builtins.bool]:
        '''Whether to configure the ALIAS for the LB.

        :default: true
        '''
        result = self._values.get("enable_load_balancer_alias")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def external_elb_record_name(self) -> typing.Optional[builtins.str]:
        '''the external ELB record name.

        :default: external
        '''
        result = self._values.get("external_elb_record_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def internal_elb_record_name(self) -> typing.Optional[builtins.str]:
        '''the internal ELB record name.

        :default: internal
        '''
        result = self._values.get("internal_elb_record_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_name(self) -> typing.Optional[builtins.str]:
        '''private zone name.

        :default: svc.local
        '''
        result = self._values.get("zone_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Route53Options(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.ServiceScalingPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "max_capacity": "maxCapacity",
        "request_per_target": "requestPerTarget",
        "target_cpu_utilization": "targetCpuUtilization",
    },
)
class ServiceScalingPolicy:
    def __init__(
        self,
        *,
        max_capacity: typing.Optional[jsii.Number] = None,
        request_per_target: typing.Optional[jsii.Number] = None,
        target_cpu_utilization: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_capacity: max capacity for the service autoscaling. Default: 10
        :param request_per_target: request per target. Default: 1000
        :param target_cpu_utilization: target cpu utilization. Default: 50
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if request_per_target is not None:
            self._values["request_per_target"] = request_per_target
        if target_cpu_utilization is not None:
            self._values["target_cpu_utilization"] = target_cpu_utilization

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''max capacity for the service autoscaling.

        :default: 10
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def request_per_target(self) -> typing.Optional[jsii.Number]:
        '''request per target.

        :default: 1000
        '''
        result = self._values.get("request_per_target")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_cpu_utilization(self) -> typing.Optional[jsii.Number]:
        '''target cpu utilization.

        :default: 50
        '''
        result = self._values.get("target_cpu_utilization")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceScalingPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WordPress(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-fargate-patterns.WordPress",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        aurora_serverless: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        database_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        service_props: typing.Optional[FargateTaskProps] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
        spot: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param aurora_serverless: Whether to use aurora serverless. When enabled, the ``databaseInstanceType`` and ``engine`` will be ignored. The ``rds.DatabaseClusterEngine.AURORA_MYSQL`` will be used as the default cluster engine instead. Default: false
        :param backup_retention: database backup retension. Default: - 7 days
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param database_instance_type: Database instance type. Default: r5.large
        :param database_subnets: VPC subnets for database. Default: - VPC isolated subnets
        :param enable_execute_command: enable ECS Exec.
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param service_props: task options for the WordPress fargate service.
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        :param spot: enable fargate spot.
        :param vpc: 
        '''
        props = WordPressProps(
            aurora_serverless=aurora_serverless,
            backup_retention=backup_retention,
            cluster_engine=cluster_engine,
            database_instance_type=database_instance_type,
            database_subnets=database_subnets,
            enable_execute_command=enable_execute_command,
            instance_engine=instance_engine,
            service_props=service_props,
            single_db_instance=single_db_instance,
            spot=spot,
            vpc=vpc,
        )

        jsii.create(WordPress, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svc")
    def svc(self) -> DualAlbFargateService:
        return typing.cast(DualAlbFargateService, jsii.get(self, "svc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="db")
    def db(self) -> typing.Optional[Database]:
        return typing.cast(typing.Optional[Database], jsii.get(self, "db"))


@jsii.data_type(
    jsii_type="cdk-fargate-patterns.WordPressProps",
    jsii_struct_bases=[],
    name_mapping={
        "aurora_serverless": "auroraServerless",
        "backup_retention": "backupRetention",
        "cluster_engine": "clusterEngine",
        "database_instance_type": "databaseInstanceType",
        "database_subnets": "databaseSubnets",
        "enable_execute_command": "enableExecuteCommand",
        "instance_engine": "instanceEngine",
        "service_props": "serviceProps",
        "single_db_instance": "singleDbInstance",
        "spot": "spot",
        "vpc": "vpc",
    },
)
class WordPressProps:
    def __init__(
        self,
        *,
        aurora_serverless: typing.Optional[builtins.bool] = None,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_engine: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        database_instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        database_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        instance_engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        service_props: typing.Optional[FargateTaskProps] = None,
        single_db_instance: typing.Optional[builtins.bool] = None,
        spot: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param aurora_serverless: Whether to use aurora serverless. When enabled, the ``databaseInstanceType`` and ``engine`` will be ignored. The ``rds.DatabaseClusterEngine.AURORA_MYSQL`` will be used as the default cluster engine instead. Default: false
        :param backup_retention: database backup retension. Default: - 7 days
        :param cluster_engine: The database cluster engine. Default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        :param database_instance_type: Database instance type. Default: r5.large
        :param database_subnets: VPC subnets for database. Default: - VPC isolated subnets
        :param enable_execute_command: enable ECS Exec.
        :param instance_engine: The database instance engine. Default: - MySQL 8.0.21
        :param service_props: task options for the WordPress fargate service.
        :param single_db_instance: Whether to use single RDS instance rather than RDS cluster. Not recommended for production. Default: false
        :param spot: enable fargate spot.
        :param vpc: 
        '''
        if isinstance(database_subnets, dict):
            database_subnets = aws_cdk.aws_ec2.SubnetSelection(**database_subnets)
        if isinstance(service_props, dict):
            service_props = FargateTaskProps(**service_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if aurora_serverless is not None:
            self._values["aurora_serverless"] = aurora_serverless
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if cluster_engine is not None:
            self._values["cluster_engine"] = cluster_engine
        if database_instance_type is not None:
            self._values["database_instance_type"] = database_instance_type
        if database_subnets is not None:
            self._values["database_subnets"] = database_subnets
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if instance_engine is not None:
            self._values["instance_engine"] = instance_engine
        if service_props is not None:
            self._values["service_props"] = service_props
        if single_db_instance is not None:
            self._values["single_db_instance"] = single_db_instance
        if spot is not None:
            self._values["spot"] = spot
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def aurora_serverless(self) -> typing.Optional[builtins.bool]:
        '''Whether to use aurora serverless.

        When enabled, the ``databaseInstanceType`` and
        ``engine`` will be ignored. The ``rds.DatabaseClusterEngine.AURORA_MYSQL`` will be used as
        the default cluster engine instead.

        :default: false
        '''
        result = self._values.get("aurora_serverless")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''database backup retension.

        :default: - 7 days
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def cluster_engine(self) -> typing.Optional[aws_cdk.aws_rds.IClusterEngine]:
        '''The database cluster engine.

        :default: rds.AuroraMysqlEngineVersion.VER_2_09_1
        '''
        result = self._values.get("cluster_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IClusterEngine], result)

    @builtins.property
    def database_instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''Database instance type.

        :default: r5.large
        '''
        result = self._values.get("database_instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def database_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''VPC subnets for database.

        :default: - VPC isolated subnets
        '''
        result = self._values.get("database_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''enable ECS Exec.'''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_engine(self) -> typing.Optional[aws_cdk.aws_rds.IInstanceEngine]:
        '''The database instance engine.

        :default: - MySQL 8.0.21
        '''
        result = self._values.get("instance_engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IInstanceEngine], result)

    @builtins.property
    def service_props(self) -> typing.Optional[FargateTaskProps]:
        '''task options for the WordPress fargate service.'''
        result = self._values.get("service_props")
        return typing.cast(typing.Optional[FargateTaskProps], result)

    @builtins.property
    def single_db_instance(self) -> typing.Optional[builtins.bool]:
        '''Whether to use single RDS instance rather than RDS cluster.

        Not recommended for production.

        :default: false
        '''
        result = self._values.get("single_db_instance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def spot(self) -> typing.Optional[builtins.bool]:
        '''enable fargate spot.'''
        result = self._values.get("spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WordPressProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BaseFargateService",
    "BaseFargateServiceProps",
    "Database",
    "DatabaseCofig",
    "DatabaseProps",
    "DualAlbFargateService",
    "DualAlbFargateServiceProps",
    "DualNlbFargateService",
    "DualNlbFargateServiceProps",
    "FargateTaskProps",
    "Laravel",
    "LaravelProps",
    "LoadBalancerAccessibility",
    "Route53Options",
    "ServiceScalingPolicy",
    "WordPress",
    "WordPressProps",
]

publication.publish()
