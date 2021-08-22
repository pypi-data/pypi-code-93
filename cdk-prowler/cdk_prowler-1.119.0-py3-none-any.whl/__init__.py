'''
[![NPM version](https://badge.fury.io/js/cdk-prowler.svg)](https://badge.fury.io/js/cdk-prowler)
[![PyPI version](https://badge.fury.io/py/cdk-prowler.svg)](https://badge.fury.io/py/cdk-prowler)
[![.NET version](https://img.shields.io/nuget/v/com.github.mmuller88.awsCdkBuildBadge.svg?style=flat-square)](https://www.nuget.org/packages/com.github.mmuller88.cdkProwler/)
![Release](https://github.com/mmuller88/cdk-prowler/workflows/Release/badge.svg)

# cdk-prowler

An AWS CDK custom construct for deploying Prowler to you AWS Account. The following description about Prowler is taken from https://github.com/toniblyx/prowler:

Prowler is a security tool to perform AWS security best practices assessments, audits, incident response, continuous monitoring, hardening and forensics readiness. It contains all CIS controls listed here https://d0.awsstatic.com/whitepapers/compliance/AWS_CIS_Foundations_Benchmark.pdf and more than 100 additional checks that help on GDPR, HIPAA…

It generates security html results which are stored in an s3 bucket:

![html results](https://raw.githubusercontent.com/mmuller88/cdk-prowler/main/misc/html-out.png)

And in your Codebuild Report group:

![Report group](https://raw.githubusercontent.com/mmuller88/cdk-prowler/main/misc/report-group-out.png)

# AWS AMI

If you just want to make the Prowler security checks in your account try my [Prowler AWS Marketplace AMI](https://aws.amazon.com/marketplace/pp/prodview-jlwcdlc3weta6). With just $1 Prowler will do over 180 security checks across a huge amount of AWS services in all your regions. Don't forget the terminate the Ec2 instance when the Prowler stack got created for not paying more than that $1 :).

With buying the AMI you support my on my passion for creating open source products like this cdk-prowler construct. Furthermore you enable me to work on future features like mentioned in the **Planned Features** section. Thank you so much :) !

# Example

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_prowler import ProwlerAudit
app = App()

stack = Stack(app, "ProwlerAudit-stack")

ProwlerAudit(stack, "ProwlerAudit")
```

# cdk-prowler Properties

cdk-prowler supports some properties to tweak your stack. Like for running a Cloudwatch schedule to regualary run the Prowler scan with a defined cron expression.

You can see the supported properties in [Api.md](https://github.com/mmuller88/cdk-prowler/blob/main/API.md)

# Planned Features

* Supporting AWS SecurityHub https://github.com/toniblyx/prowler#security-hub-integration
* Triggering an event with SNS when prowler finishes the run
* AMI EC2 executable

# Architecture

![cfn](misc/cfn.jpg)

# Misc

```sh
yes | yarn destroy && yarn deploy --require-approval never
```

Rerun Prowler on deploy

```sh
yarn deploy --require-approval never -c reRunProwler=true
```

# Thanks To

* My friend and fellaw ex colleague Tony de la Fuente (https://github.com/toniblyx https://twitter.com/ToniBlyx) for developing such a cool security tool as [Prowler](https://github.com/toniblyx/prowler)
* As always to the amazing CDK / Projen Community. Join us on [Slack](https://cdk-dev.slack.com)!
* [Projen](https://github.com/projen/projen) project and the community around it
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

import aws_cdk.aws_logs
import aws_cdk.aws_s3
import aws_cdk.core


class ProwlerAudit(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-prowler.ProwlerAudit",
):
    '''Creates a CodeBuild project to audit an AWS account with Prowler and stores the html report in a S3 bucket.

    This will run onece at the beginning and on a schedule afterwards. Partial contribution from https://github.com/stevecjones
    '''

    def __init__(
        self,
        parent: aws_cdk.core.Stack,
        id: builtins.str,
        *,
        enable_scheduler: typing.Optional[builtins.bool] = None,
        logs_retention_in_days: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        prowler_options: typing.Optional[builtins.str] = None,
        prowler_scheduler: typing.Optional[builtins.str] = None,
        prowler_version: typing.Optional[builtins.str] = None,
        report_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        report_bucket_prefix: typing.Optional[builtins.str] = None,
        service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: -
        :param enable_scheduler: enables the scheduler for running prowler periodically. Together with prowlerScheduler. Default: false
        :param logs_retention_in_days: Specifies the number of days you want to retain CodeBuild run log events in the specified log group. Junit reports are kept for 30 days, HTML reports in S3 are not deleted Default: : 3
        :param prowler_options: Options to pass to Prowler command, make sure at least -M junit-xml is used for CodeBuild reports. Use -r for the region to send API queries, -f to filter only one region, -M output formats, -c for comma separated checks, for all checks do not use -c or -g, for more options see -h. For a complete assessment use "-M text,junit-xml,html,csv,json", for SecurityHub integration use "-r region -f region -M text,junit-xml,html,csv,json,json-asff -S -q" Default: '-M text,junit-xml,html,csv,json'
        :param prowler_scheduler: The time when Prowler will run in cron format. Default is daily at 22:00h or 10PM 'cron(0 22 * * ? *)', for every 5 hours also works 'rate(5 hours)'. More info here https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html. Default: 'cron(0 22 * * ? *)'
        :param prowler_version: Specifies the concrete Prowler version. Default: 2.5.0
        :param report_bucket: An optional S3 bucket to store the Prowler reports.
        :param report_bucket_prefix: An optional prefix for the report bucket objects.
        :param service_name: Specifies the service name used within component naming. Default: : prowler
        '''
        props = ProwlerAuditProps(
            enable_scheduler=enable_scheduler,
            logs_retention_in_days=logs_retention_in_days,
            prowler_options=prowler_options,
            prowler_scheduler=prowler_scheduler,
            prowler_version=prowler_version,
            report_bucket=report_bucket,
            report_bucket_prefix=report_bucket_prefix,
            service_name=service_name,
        )

        jsii.create(ProwlerAudit, self, [parent, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableScheduler")
    def enable_scheduler(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enableScheduler"))

    @enable_scheduler.setter
    def enable_scheduler(self, value: builtins.bool) -> None:
        jsii.set(self, "enableScheduler", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logsRetentionInDays")
    def logs_retention_in_days(self) -> aws_cdk.aws_logs.RetentionDays:
        return typing.cast(aws_cdk.aws_logs.RetentionDays, jsii.get(self, "logsRetentionInDays"))

    @logs_retention_in_days.setter
    def logs_retention_in_days(self, value: aws_cdk.aws_logs.RetentionDays) -> None:
        jsii.set(self, "logsRetentionInDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prowlerOptions")
    def prowler_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prowlerOptions"))

    @prowler_options.setter
    def prowler_options(self, value: builtins.str) -> None:
        jsii.set(self, "prowlerOptions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prowlerScheduler")
    def prowler_scheduler(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prowlerScheduler"))

    @prowler_scheduler.setter
    def prowler_scheduler(self, value: builtins.str) -> None:
        jsii.set(self, "prowlerScheduler", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prowlerVersion")
    def prowler_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prowlerVersion"))

    @prowler_version.setter
    def prowler_version(self, value: builtins.str) -> None:
        jsii.set(self, "prowlerVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        jsii.set(self, "serviceName", value)


@jsii.data_type(
    jsii_type="cdk-prowler.ProwlerAuditProps",
    jsii_struct_bases=[],
    name_mapping={
        "enable_scheduler": "enableScheduler",
        "logs_retention_in_days": "logsRetentionInDays",
        "prowler_options": "prowlerOptions",
        "prowler_scheduler": "prowlerScheduler",
        "prowler_version": "prowlerVersion",
        "report_bucket": "reportBucket",
        "report_bucket_prefix": "reportBucketPrefix",
        "service_name": "serviceName",
    },
)
class ProwlerAuditProps:
    def __init__(
        self,
        *,
        enable_scheduler: typing.Optional[builtins.bool] = None,
        logs_retention_in_days: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        prowler_options: typing.Optional[builtins.str] = None,
        prowler_scheduler: typing.Optional[builtins.str] = None,
        prowler_version: typing.Optional[builtins.str] = None,
        report_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        report_bucket_prefix: typing.Optional[builtins.str] = None,
        service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enable_scheduler: enables the scheduler for running prowler periodically. Together with prowlerScheduler. Default: false
        :param logs_retention_in_days: Specifies the number of days you want to retain CodeBuild run log events in the specified log group. Junit reports are kept for 30 days, HTML reports in S3 are not deleted Default: : 3
        :param prowler_options: Options to pass to Prowler command, make sure at least -M junit-xml is used for CodeBuild reports. Use -r for the region to send API queries, -f to filter only one region, -M output formats, -c for comma separated checks, for all checks do not use -c or -g, for more options see -h. For a complete assessment use "-M text,junit-xml,html,csv,json", for SecurityHub integration use "-r region -f region -M text,junit-xml,html,csv,json,json-asff -S -q" Default: '-M text,junit-xml,html,csv,json'
        :param prowler_scheduler: The time when Prowler will run in cron format. Default is daily at 22:00h or 10PM 'cron(0 22 * * ? *)', for every 5 hours also works 'rate(5 hours)'. More info here https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html. Default: 'cron(0 22 * * ? *)'
        :param prowler_version: Specifies the concrete Prowler version. Default: 2.5.0
        :param report_bucket: An optional S3 bucket to store the Prowler reports.
        :param report_bucket_prefix: An optional prefix for the report bucket objects.
        :param service_name: Specifies the service name used within component naming. Default: : prowler
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if enable_scheduler is not None:
            self._values["enable_scheduler"] = enable_scheduler
        if logs_retention_in_days is not None:
            self._values["logs_retention_in_days"] = logs_retention_in_days
        if prowler_options is not None:
            self._values["prowler_options"] = prowler_options
        if prowler_scheduler is not None:
            self._values["prowler_scheduler"] = prowler_scheduler
        if prowler_version is not None:
            self._values["prowler_version"] = prowler_version
        if report_bucket is not None:
            self._values["report_bucket"] = report_bucket
        if report_bucket_prefix is not None:
            self._values["report_bucket_prefix"] = report_bucket_prefix
        if service_name is not None:
            self._values["service_name"] = service_name

    @builtins.property
    def enable_scheduler(self) -> typing.Optional[builtins.bool]:
        '''enables the scheduler for running prowler periodically.

        Together with prowlerScheduler.

        :default: false
        '''
        result = self._values.get("enable_scheduler")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logs_retention_in_days(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''Specifies the number of days you want to retain CodeBuild run log events in the specified log group.

        Junit reports are kept for 30 days, HTML reports in S3 are not deleted

        :default: : 3
        '''
        result = self._values.get("logs_retention_in_days")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def prowler_options(self) -> typing.Optional[builtins.str]:
        '''Options to pass to Prowler command, make sure at least -M junit-xml is used for CodeBuild reports.

        Use -r for the region to send API queries, -f to filter only one region, -M output formats, -c for comma separated checks, for all checks do not use -c or -g, for more options see -h. For a complete assessment use  "-M text,junit-xml,html,csv,json", for SecurityHub integration use "-r region -f region -M text,junit-xml,html,csv,json,json-asff -S -q"

        :default: '-M text,junit-xml,html,csv,json'
        '''
        result = self._values.get("prowler_options")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prowler_scheduler(self) -> typing.Optional[builtins.str]:
        '''The time when Prowler will run in cron format.

        Default is daily at 22:00h or 10PM 'cron(0 22 * * ? *)', for every 5 hours also works 'rate(5 hours)'. More info here https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html.

        :default: 'cron(0 22 * * ? *)'
        '''
        result = self._values.get("prowler_scheduler")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prowler_version(self) -> typing.Optional[builtins.str]:
        '''Specifies the concrete Prowler version.

        :default: 2.5.0
        '''
        result = self._values.get("prowler_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def report_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''An optional S3 bucket to store the Prowler reports.'''
        result = self._values.get("report_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def report_bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''An optional prefix for the report bucket objects.'''
        result = self._values.get("report_bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        '''Specifies the service name used within component naming.

        :default: : prowler
        '''
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProwlerAuditProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProwlerAudit",
    "ProwlerAuditProps",
]

publication.publish()
