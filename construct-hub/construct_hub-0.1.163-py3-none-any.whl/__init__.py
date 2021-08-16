'''
# Construct Hub

This project maintains a [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) construct library
that can be used to deploy instances of the Construct Hub in any AWS Account.

## Development

The `test/devapp` directory includes an AWS CDK app designed for deploying the
construct hub into a development account. This app is also used as a golden
snapshot, so every time the construct changes, you'll see its snapshot updated.

To bootstrap your developer account, use the following command:

```shell
CDK_NEW_BOOTSTRAP=1 npx cdk bootstrap aws://ACCOUNT/REGION
```

Use the following tasks to work with the dev app. It will always work with the
currently configured CLI account/region:

* `yarn dev:synth` - synthesize into `test/devapp/cdk.out`
* `yarn dev:deploy` - deploy to the current environment
* `yarn dev:diff` - diff against the current environment

## Testing

To run all tests, run `yarn test`.

Unit tests are implemented using [jest](https://jestjs.io/).

Integration tests are implemented as small CDK applications under files called
`.integ.ts`. For each integration test, you can use the following tasks:

* `integ:xxx:deploy` - deploys the integration test to your personal development
  account and stores the output under a `.cdkout` directory which is committed
  to the repository.
* `integ:xxx:assert` - runs during `yarn test` and compares the synthesized
  output of the test to the one in `.cdkout`.
* `integ:xxx:snapshot` - synthesizes the app and updates the snapshot without
  actually deploying the stack (generally not recommended)
* `integ:xxx:destroy` - can be used to delete the integration test app (called
  by `deploy` as well)

To deploy integration test apps, you'll need to configure your environment with
AWS credentials as well as set `AWS_REGION` to refer to the region you wish to
use.

Integration tests use "triggers" which are lambda functions that are executed
during deployment and are used to make assertions about the deployed resources.
Triggers are automatically generated for all files named `trigger.xxx.lambda.ts`
(for example, `trigger.prune-test.lambda.ts`) and can just be added to the
integration test stack with the relevant dependencies. See the deny-list
integration test as an example.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more
information.

## License

This project is licensed under the Apache-2.0 License.
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
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_iam
import aws_cdk.aws_route53
import aws_cdk.aws_sqs
import aws_cdk.core
import constructs


@jsii.data_type(
    jsii_type="construct-hub.AlarmActions",
    jsii_struct_bases=[],
    name_mapping={
        "high_severity": "highSeverity",
        "high_severity_action": "highSeverityAction",
        "normal_severity": "normalSeverity",
        "normal_severity_action": "normalSeverityAction",
    },
)
class AlarmActions:
    def __init__(
        self,
        *,
        high_severity: typing.Optional[builtins.str] = None,
        high_severity_action: typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction] = None,
        normal_severity: typing.Optional[builtins.str] = None,
        normal_severity_action: typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction] = None,
    ) -> None:
        '''(experimental) CloudWatch alarm actions to perform.

        :param high_severity: (experimental) The ARN of the CloudWatch alarm action to take for alarms of high-severity alarms. This must be an ARN that can be used with CloudWatch alarms.
        :param high_severity_action: (experimental) The CloudWatch alarm action to take for alarms of high-severity alarms. This must be an ARN that can be used with CloudWatch alarms.
        :param normal_severity: (experimental) The ARN of the CloudWatch alarm action to take for alarms of normal severity. This must be an ARN that can be used with CloudWatch alarms. Default: - no actions are taken in response to alarms of normal severity
        :param normal_severity_action: (experimental) The CloudWatch alarm action to take for alarms of normal severity. This must be an ARN that can be used with CloudWatch alarms. Default: - no actions are taken in response to alarms of normal severity

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if high_severity is not None:
            self._values["high_severity"] = high_severity
        if high_severity_action is not None:
            self._values["high_severity_action"] = high_severity_action
        if normal_severity is not None:
            self._values["normal_severity"] = normal_severity
        if normal_severity_action is not None:
            self._values["normal_severity_action"] = normal_severity_action

    @builtins.property
    def high_severity(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the CloudWatch alarm action to take for alarms of high-severity alarms.

        This must be an ARN that can be used with CloudWatch alarms.

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html#alarms-and-actions
        :stability: experimental
        '''
        result = self._values.get("high_severity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def high_severity_action(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction]:
        '''(experimental) The CloudWatch alarm action to take for alarms of high-severity alarms.

        This must be an ARN that can be used with CloudWatch alarms.

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html#alarms-and-actions
        :stability: experimental
        '''
        result = self._values.get("high_severity_action")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction], result)

    @builtins.property
    def normal_severity(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the CloudWatch alarm action to take for alarms of normal severity.

        This must be an ARN that can be used with CloudWatch alarms.

        :default: - no actions are taken in response to alarms of normal severity

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html#alarms-and-actions
        :stability: experimental
        '''
        result = self._values.get("normal_severity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def normal_severity_action(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction]:
        '''(experimental) The CloudWatch alarm action to take for alarms of normal severity.

        This must be an ARN that can be used with CloudWatch alarms.

        :default: - no actions are taken in response to alarms of normal severity

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html#alarms-and-actions
        :stability: experimental
        '''
        result = self._values.get("normal_severity_action")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlarmActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_iam.IGrantable)
class ConstructHub(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="construct-hub.ConstructHub",
):
    '''(experimental) Construct Hub.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alarm_actions: typing.Optional[AlarmActions] = None,
        backend_dashboard_name: typing.Optional[builtins.str] = None,
        deny_list: typing.Optional[typing.Sequence["DenyListRule"]] = None,
        domain: typing.Optional["Domain"] = None,
        isolate_lambdas: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alarm_actions: (experimental) Actions to perform when alarms are set.
        :param backend_dashboard_name: (experimental) The name of the CloudWatch dashboard that represents the health of backend systems.
        :param deny_list: (experimental) A list of packages to block from the construct hub. Default: []
        :param domain: (experimental) Connect the hub to a domain (requires a hosted zone and a certificate).
        :param isolate_lambdas: (experimental) Whether sensitive Lambda functions (which operate on un-trusted complex data, such as the transliterator, which operates with externally-sourced npm package tarballs) should run in network-isolated environments. This implies the creation of additonal resources, including: - A VPC with only isolated subnets. - VPC Endpoints (CodeArtifact, CodeArtifact API, S3) - A CodeArtifact Repository with an external connection to npmjs.com Default: true

        :stability: experimental
        '''
        props = ConstructHubProps(
            alarm_actions=alarm_actions,
            backend_dashboard_name=backend_dashboard_name,
            deny_list=deny_list,
            domain=domain,
            isolate_lambdas=isolate_lambdas,
        )

        jsii.create(ConstructHub, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingestionQueue")
    def ingestion_queue(self) -> aws_cdk.aws_sqs.IQueue:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_sqs.IQueue, jsii.get(self, "ingestionQueue"))


@jsii.data_type(
    jsii_type="construct-hub.ConstructHubProps",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_actions": "alarmActions",
        "backend_dashboard_name": "backendDashboardName",
        "deny_list": "denyList",
        "domain": "domain",
        "isolate_lambdas": "isolateLambdas",
    },
)
class ConstructHubProps:
    def __init__(
        self,
        *,
        alarm_actions: typing.Optional[AlarmActions] = None,
        backend_dashboard_name: typing.Optional[builtins.str] = None,
        deny_list: typing.Optional[typing.Sequence["DenyListRule"]] = None,
        domain: typing.Optional["Domain"] = None,
        isolate_lambdas: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Props for ``ConstructHub``.

        :param alarm_actions: (experimental) Actions to perform when alarms are set.
        :param backend_dashboard_name: (experimental) The name of the CloudWatch dashboard that represents the health of backend systems.
        :param deny_list: (experimental) A list of packages to block from the construct hub. Default: []
        :param domain: (experimental) Connect the hub to a domain (requires a hosted zone and a certificate).
        :param isolate_lambdas: (experimental) Whether sensitive Lambda functions (which operate on un-trusted complex data, such as the transliterator, which operates with externally-sourced npm package tarballs) should run in network-isolated environments. This implies the creation of additonal resources, including: - A VPC with only isolated subnets. - VPC Endpoints (CodeArtifact, CodeArtifact API, S3) - A CodeArtifact Repository with an external connection to npmjs.com Default: true

        :stability: experimental
        '''
        if isinstance(alarm_actions, dict):
            alarm_actions = AlarmActions(**alarm_actions)
        if isinstance(domain, dict):
            domain = Domain(**domain)
        self._values: typing.Dict[str, typing.Any] = {}
        if alarm_actions is not None:
            self._values["alarm_actions"] = alarm_actions
        if backend_dashboard_name is not None:
            self._values["backend_dashboard_name"] = backend_dashboard_name
        if deny_list is not None:
            self._values["deny_list"] = deny_list
        if domain is not None:
            self._values["domain"] = domain
        if isolate_lambdas is not None:
            self._values["isolate_lambdas"] = isolate_lambdas

    @builtins.property
    def alarm_actions(self) -> typing.Optional[AlarmActions]:
        '''(experimental) Actions to perform when alarms are set.

        :stability: experimental
        '''
        result = self._values.get("alarm_actions")
        return typing.cast(typing.Optional[AlarmActions], result)

    @builtins.property
    def backend_dashboard_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the CloudWatch dashboard that represents the health of backend systems.

        :stability: experimental
        '''
        result = self._values.get("backend_dashboard_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deny_list(self) -> typing.Optional[typing.List["DenyListRule"]]:
        '''(experimental) A list of packages to block from the construct hub.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("deny_list")
        return typing.cast(typing.Optional[typing.List["DenyListRule"]], result)

    @builtins.property
    def domain(self) -> typing.Optional["Domain"]:
        '''(experimental) Connect the hub to a domain (requires a hosted zone and a certificate).

        :stability: experimental
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional["Domain"], result)

    @builtins.property
    def isolate_lambdas(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether sensitive Lambda functions (which operate on un-trusted complex data, such as the transliterator, which operates with externally-sourced npm package tarballs) should run in network-isolated environments.

        This
        implies the creation of additonal resources, including:

        - A VPC with only isolated subnets.
        - VPC Endpoints (CodeArtifact, CodeArtifact API, S3)
        - A CodeArtifact Repository with an external connection to npmjs.com

        :default: true

        :stability: experimental
        '''
        result = self._values.get("isolate_lambdas")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConstructHubProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.DenyListMap",
    jsii_struct_bases=[],
    name_mapping={},
)
class DenyListMap:
    def __init__(self) -> None:
        '''(experimental) The contents of the deny list file in S3.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DenyListMap(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.DenyListRule",
    jsii_struct_bases=[],
    name_mapping={"package": "package", "reason": "reason", "version": "version"},
)
class DenyListRule:
    def __init__(
        self,
        *,
        package: builtins.str,
        reason: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) An entry in the list of packages blocked from display in the construct hub.

        :param package: (experimental) The name of the package to block (npm).
        :param reason: (experimental) The reason why this package/version is denied. This information will be emitted to the construct hub logs.
        :param version: (experimental) The package version to block (must be a valid version such as "1.0.3"). Default: - all versions of this package are blocked.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "package": package,
            "reason": reason,
        }
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def package(self) -> builtins.str:
        '''(experimental) The name of the package to block (npm).

        :stability: experimental
        '''
        result = self._values.get("package")
        assert result is not None, "Required property 'package' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def reason(self) -> builtins.str:
        '''(experimental) The reason why this package/version is denied.

        This information will be
        emitted to the construct hub logs.

        :stability: experimental
        '''
        result = self._values.get("reason")
        assert result is not None, "Required property 'reason' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The package version to block (must be a valid version such as "1.0.3").

        :default: - all versions of this package are blocked.

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DenyListRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.Domain",
    jsii_struct_bases=[],
    name_mapping={
        "cert": "cert",
        "zone": "zone",
        "monitor_certificate_expiration": "monitorCertificateExpiration",
    },
)
class Domain:
    def __init__(
        self,
        *,
        cert: aws_cdk.aws_certificatemanager.ICertificate,
        zone: aws_cdk.aws_route53.IHostedZone,
        monitor_certificate_expiration: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Domain configuration for the website.

        :param cert: (experimental) The certificate to use for serving the Construct Hub over a custom domain. Default: - a DNS-Validated certificate will be provisioned using the provided ``hostedZone``.
        :param zone: (experimental) The root domain name where this instance of Construct Hub will be served.
        :param monitor_certificate_expiration: (experimental) Whether the certificate should be monitored for expiration, meaning high severity alarms will be raised if it is due to expire in less than 45 days. Default: true

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cert": cert,
            "zone": zone,
        }
        if monitor_certificate_expiration is not None:
            self._values["monitor_certificate_expiration"] = monitor_certificate_expiration

    @builtins.property
    def cert(self) -> aws_cdk.aws_certificatemanager.ICertificate:
        '''(experimental) The certificate to use for serving the Construct Hub over a custom domain.

        :default:

        - a DNS-Validated certificate will be provisioned using the
        provided ``hostedZone``.

        :stability: experimental
        '''
        result = self._values.get("cert")
        assert result is not None, "Required property 'cert' is missing"
        return typing.cast(aws_cdk.aws_certificatemanager.ICertificate, result)

    @builtins.property
    def zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''(experimental) The root domain name where this instance of Construct Hub will be served.

        :stability: experimental
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def monitor_certificate_expiration(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the certificate should be monitored for expiration, meaning high severity alarms will be raised if it is due to expire in less than 45 days.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("monitor_certificate_expiration")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Domain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AlarmActions",
    "ConstructHub",
    "ConstructHubProps",
    "DenyListMap",
    "DenyListRule",
    "Domain",
]

publication.publish()
