'''
[![NPM version](https://badge.fury.io/js/cdk-certbot-dns-route53.svg)](https://badge.fury.io/js/cdk-certbot-dns-route53)
[![PyPI version](https://badge.fury.io/py/cdk-certbot-dns-route53.svg)](https://badge.fury.io/py/cdk-certbot-dns-route53)
[![Release](https://github.com/neilkuan/cdk-certbot-dns-route53/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/neilkuan/cdk-certbot-dns-route53/actions/workflows/release.yml)

# cdk-certbot-dns-route53

**cdk-certbot-dns-route53** is a CDK construct library that allows you to create [Certbot](https://github.com/certbot/certbot) Lambda Function on AWS with CDK, and setting schedule cron job to renew certificate to store on S3 Bucket.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.aws_route53 as r53
import aws_cdk.aws_s3 as s3
import aws_cdk.core as cdk
from cdk_certbot_dns_route53 import CertbotDnsRoute53Job

dev_env = {
    "account": process.env.CDK_DEFAULT_ACCOUNT,
    "region": process.env.CDK_DEFAULT_REGION
}

app = cdk.App()

stack = cdk.Stack(app, "lambda-certbot-dev", env=dev_env)

CertbotDnsRoute53Job(stack, "Demo",
    certbot_options={
        "domain_name": "*.example.com",
        "email": "user@example.com"
    },
    zone=r53.HostedZone.from_hosted_zone_attributes(stack, "myZone",
        zone_name="example.com",
        hosted_zone_id="mockId"
    ),
    destination_bucket=s3.Bucket.from_bucket_name(stack, "myBucket", "mybucket")
)
```

### Example: Invoke Lambda Function log.

![](./images/lambda-logs.png)

### Example: Renew certificate to store on S3 Bucket

![](./images/s3-bucket.png)
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

import aws_cdk.aws_events
import aws_cdk.aws_route53
import aws_cdk.aws_s3
import aws_cdk.core


class CertbotDnsRoute53Job(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-certbot-dns-route53.CertbotDnsRoute53Job",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        certbot_options: "CertbotOptions",
        destination_bucket: aws_cdk.aws_s3.IBucket,
        zone: aws_cdk.aws_route53.IHostedZone,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certbot_options: certbot cmd options.
        :param destination_bucket: The S3 bucket to store certificate.
        :param zone: The HostZone on route53 to dns-01 challenge.
        :param schedule: run the Job with defined schedule. Default: - no shedule
        '''
        props = CertbotDnsRoute53JobProps(
            certbot_options=certbot_options,
            destination_bucket=destination_bucket,
            zone=zone,
            schedule=schedule,
        )

        jsii.create(CertbotDnsRoute53Job, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-certbot-dns-route53.CertbotDnsRoute53JobProps",
    jsii_struct_bases=[],
    name_mapping={
        "certbot_options": "certbotOptions",
        "destination_bucket": "destinationBucket",
        "zone": "zone",
        "schedule": "schedule",
    },
)
class CertbotDnsRoute53JobProps:
    def __init__(
        self,
        *,
        certbot_options: "CertbotOptions",
        destination_bucket: aws_cdk.aws_s3.IBucket,
        zone: aws_cdk.aws_route53.IHostedZone,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
    ) -> None:
        '''
        :param certbot_options: certbot cmd options.
        :param destination_bucket: The S3 bucket to store certificate.
        :param zone: The HostZone on route53 to dns-01 challenge.
        :param schedule: run the Job with defined schedule. Default: - no shedule
        '''
        if isinstance(certbot_options, dict):
            certbot_options = CertbotOptions(**certbot_options)
        self._values: typing.Dict[str, typing.Any] = {
            "certbot_options": certbot_options,
            "destination_bucket": destination_bucket,
            "zone": zone,
        }
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def certbot_options(self) -> "CertbotOptions":
        '''certbot cmd options.'''
        result = self._values.get("certbot_options")
        assert result is not None, "Required property 'certbot_options' is missing"
        return typing.cast("CertbotOptions", result)

    @builtins.property
    def destination_bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''The S3 bucket to store certificate.'''
        result = self._values.get("destination_bucket")
        assert result is not None, "Required property 'destination_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''The HostZone on route53 to dns-01 challenge.'''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        '''run the Job with defined schedule.

        :default: - no shedule
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[aws_cdk.aws_events.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertbotDnsRoute53JobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-certbot-dns-route53.CertbotOptions",
    jsii_struct_bases=[],
    name_mapping={"domain_name": "domainName", "email": "email"},
)
class CertbotOptions:
    def __init__(self, *, domain_name: builtins.str, email: builtins.str) -> None:
        '''
        :param domain_name: the domain must host on route53 like example.com.
        :param email: Email address for important account notifications.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
            "email": email,
        }

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''the domain must host on route53 like example.com.

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            -"*.example.com"or `a.example.com`.
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email(self) -> builtins.str:
        '''Email address for important account notifications.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertbotOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CertbotDnsRoute53Job",
    "CertbotDnsRoute53JobProps",
    "CertbotOptions",
]

publication.publish()
