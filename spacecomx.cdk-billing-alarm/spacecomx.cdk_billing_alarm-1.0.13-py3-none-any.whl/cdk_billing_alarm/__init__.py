'''
[![npm version](https://badge.fury.io/js/%40spacecomx%2Fcdk-billing-alarm.svg)](https://badge.fury.io/js/%40spacecomx%2Fcdk-billing-alarm)
[![PyPI version](https://badge.fury.io/py/spacecomx.cdk-billing-alarm.svg)](https://badge.fury.io/py/spacecomx.cdk-billing-alarm)

# @spacecomx/cdk-billing-alarm

CDK construct to monitor estimated billing charges with alerts and notifications. It sets up an estimated monthly billing alarm associated with an email address endpoint. It then subscribes an email endpoint to an SNS Topic or an existing SNS Topic Arn.

The construct can be used to implement multiple customizable billing alarms for master/payer accounts e.g (AWS Organization). For customizable multi-account billing alarm requirements, see [@spacecomx/cdk-organization-billing-alarm](https://github.com/spacecomx/cdk-organization-billing-alarm)

## Features

Some features built-in:

* consolidated charge estimates of all AWS services in your AWS account.
* associate the billing alarm with an existing SNS topic Arn in your AWS account.
* consolidated charges for a specific AWS service used by your AWS account e.g. Amazon DynamoDB.
* consolidated charges for all linked accounts within the master/payer account e.g. AWS Organization.
* consolidated charges for linked account within a master/payer account.
* consolidated charges for linked account and AWS service within the master/payer account.

## Prerequisites

> :warning: Before you can create a billing alarm, you must enable billing alerts in your account, or the master/payer account if you are using consolidated billing. For more information, see [Enabling Billing Alerts](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html#turning_on_billing_metrics).

## Installation

TypeScript/JavaScript:

```bash
npm i @spacecomx/cdk-billing-alarm
```

or:

```bash
yarn add @spacecomx/cdk-billing-alarm
```

Python:

```bash
pip install spacecomx.cdk-billing-alarm
```

## Example: Create a billing alarm in your AWS account

This type of billing alarm configuration will provide estimated charges for every AWS Service that you use, in addition to the estimated overall total of your AWS charges within your AWS account. For more advanced examples and custom implementations, see [**documentation**](https://github.com/spacecomx/cdk-billing-alarm/blob/main/docs/DOCUMENTATION.md).

> :small_orange_diamond: The `emailAddress` is an endpoint that subscribes to a SNS topic. The `thresholdAmount` is the amount in USD, that will trigger the alarm when AWS charges exceed the threshold.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import Stack, StackProps
from spacecomx.cdk_billing_alarm import BillingAlarm, BillingAlarmProps

class BillingAlarmStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        options = {
            "topic_configuration": {
                "email_address": ["john@example.org"]
            },
            "alarm_configuration": {
                "alarm_description": "Consolidated Billing Alarm - All AWS Services",
                "threshold_amount": 150
            }
        }

        BillingAlarm(self, "BillingAlarm", options)
```

## Documentation

For more advanced examples and custom implementations, see [documentation](https://github.com/spacecomx/cdk-billing-alarm/blob/main/docs/DOCUMENTATION.md)

## API Documentation

For more detail, see [API documentation](https://github.com/spacecomx/cdk-billing-alarm/blob/main/API.md)

## Contributions

Contributions of all kinds are welcome! Check out our [contributor's guide](https://github.com/spacecomx/cdk-billing-alarm/blob/main/CONTRIBUTING.md) and our [code of conduct](https://github.com/spacecomx/cdk-billing-alarm/blob/main/CODE_OF_CONDUCT.md)

## Credits

* [Wayne Gibson](https://github.com/waynegibson)

## Alternatives

* [@spacecomx/cdk-organization-billing-alarm](https://github.com/spacecomx/cdk-organization-billing-alarm#readme) - used for multi-account AWS Organization billing alarm requirements.
* [aws-cdk-billing-alarm](https://github.com/alvyn279/aws-cdk-billing-alarm)

## License

@spacecomx/cdk-billing-alarm is distributed under the [MIT](https://github.com/spacecomx/cdk-billing-alarm/blob/main/LICENSE) license.
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

import aws_cdk.aws_sns
import aws_cdk.core


@jsii.enum(jsii_type="@spacecomx/cdk-billing-alarm.AWSService")
class AWSService(enum.Enum):
    '''List of AWS Services to used to link a service to a billing alarm.'''

    AMAZON_API_GATEWAY = "AMAZON_API_GATEWAY"
    AMAZON_CLOUD_FRONT = "AMAZON_CLOUD_FRONT"
    AMAZON_CLOUD_WATCH = "AMAZON_CLOUD_WATCH"
    AMAZON_DYNAMO_DB = "AMAZON_DYNAMO_DB"
    AMAZON_RDS = "AMAZON_RDS"
    AMAZON_ROUTE_53 = "AMAZON_ROUTE_53"
    AMAZON_S3 = "AMAZON_S3"
    AMAZON_SES = "AMAZON_SES"
    AMAZON_SNS = "AMAZON_SNS"
    AMAZON_WORK_MAIL = "AMAZON_WORK_MAIL"
    AWS_AMPLIFY = "AWS_AMPLIFY"
    AWS_DATA_TRANSFER = "AWS_DATA_TRANSFER"
    AWS_LAMDA = "AWS_LAMDA"
    AWS_KMS = "AWS_KMS"
    AWS_MARKETPLACE = "AWS_MARKETPLACE"
    AWS_SECRETS_MANAGER = "AWS_SECRETS_MANAGER"
    AWS_QUEUE_SERVICE = "AWS_QUEUE_SERVICE"


@jsii.data_type(
    jsii_type="@spacecomx/cdk-billing-alarm.AlarmOptions",
    jsii_struct_bases=[],
    name_mapping={
        "threshold_amount": "thresholdAmount",
        "alarm_description": "alarmDescription",
        "alarm_name": "alarmName",
        "number_of_hours": "numberOfHours",
    },
)
class AlarmOptions:
    def __init__(
        self,
        *,
        threshold_amount: jsii.Number,
        alarm_description: typing.Optional[builtins.str] = None,
        alarm_name: typing.Optional[builtins.str] = None,
        number_of_hours: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param threshold_amount: Enter the monthly threshold amount in USD that must be exceeded to trigger the alarm e.g. (thresholdAmount: 150).
        :param alarm_description: Description for the alarm. A developer-defined string that can be used to identify this alarm. Default: - Not configured
        :param alarm_name: Name of the alarm. If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the alarm name (recommended). Default: Generated name
        :param number_of_hours: Evaluates the metric every few hours as ``EstimatedCharges`` metrics are updated every 6 hours. Default: Duration.hours(6)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "threshold_amount": threshold_amount,
        }
        if alarm_description is not None:
            self._values["alarm_description"] = alarm_description
        if alarm_name is not None:
            self._values["alarm_name"] = alarm_name
        if number_of_hours is not None:
            self._values["number_of_hours"] = number_of_hours

    @builtins.property
    def threshold_amount(self) -> jsii.Number:
        '''Enter the monthly threshold amount in USD that must be exceeded to trigger the alarm e.g. (thresholdAmount: 150).'''
        result = self._values.get("threshold_amount")
        assert result is not None, "Required property 'threshold_amount' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def alarm_description(self) -> typing.Optional[builtins.str]:
        '''Description for the alarm.

        A developer-defined string that can be used to identify this alarm.

        :default: - Not configured
        '''
        result = self._values.get("alarm_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alarm_name(self) -> typing.Optional[builtins.str]:
        '''Name of the alarm.

        If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the alarm name (recommended).

        :default: Generated name
        '''
        result = self._values.get("alarm_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def number_of_hours(self) -> typing.Optional[jsii.Number]:
        '''Evaluates the metric every few hours as ``EstimatedCharges`` metrics are updated every 6 hours.

        :default: Duration.hours(6)
        '''
        result = self._values.get("number_of_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlarmOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BillingAlarm(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@spacecomx/cdk-billing-alarm.BillingAlarm",
):
    '''A construct to create an estimated monthly billing alarm associated with an SNS topic, and estimate billing alert notifications via email.

    Example::

        # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
        org"],"alarmConfiguration: {
        thresholdAmount: 20,
        }
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        alarm_configuration: AlarmOptions,
        topic_configuration: "BillingTopicProps",
        metric_dimensions: typing.Optional["MetricDimensionOptions"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alarm_configuration: Alarm configuration options to configure the billing alarm e.g. (name, description etc.).
        :param topic_configuration: Topic configuration options to configure the SNS topic and email address's that will be used to subscribe to the topic.
        :param metric_dimensions: Metric dimension options to configure advanced alarm metrics e.g. (link the alarm to a specific account, region or AWS service).
        '''
        props = BillingAlarmProps(
            alarm_configuration=alarm_configuration,
            topic_configuration=topic_configuration,
            metric_dimensions=metric_dimensions,
        )

        jsii.create(BillingAlarm, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> aws_cdk.core.CfnOutput:
        return typing.cast(aws_cdk.core.CfnOutput, jsii.get(self, "topicArn"))


@jsii.data_type(
    jsii_type="@spacecomx/cdk-billing-alarm.BillingAlarmProps",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_configuration": "alarmConfiguration",
        "topic_configuration": "topicConfiguration",
        "metric_dimensions": "metricDimensions",
    },
)
class BillingAlarmProps:
    def __init__(
        self,
        *,
        alarm_configuration: AlarmOptions,
        topic_configuration: "BillingTopicProps",
        metric_dimensions: typing.Optional["MetricDimensionOptions"] = None,
    ) -> None:
        '''
        :param alarm_configuration: Alarm configuration options to configure the billing alarm e.g. (name, description etc.).
        :param topic_configuration: Topic configuration options to configure the SNS topic and email address's that will be used to subscribe to the topic.
        :param metric_dimensions: Metric dimension options to configure advanced alarm metrics e.g. (link the alarm to a specific account, region or AWS service).
        '''
        if isinstance(alarm_configuration, dict):
            alarm_configuration = AlarmOptions(**alarm_configuration)
        if isinstance(topic_configuration, dict):
            topic_configuration = BillingTopicProps(**topic_configuration)
        if isinstance(metric_dimensions, dict):
            metric_dimensions = MetricDimensionOptions(**metric_dimensions)
        self._values: typing.Dict[str, typing.Any] = {
            "alarm_configuration": alarm_configuration,
            "topic_configuration": topic_configuration,
        }
        if metric_dimensions is not None:
            self._values["metric_dimensions"] = metric_dimensions

    @builtins.property
    def alarm_configuration(self) -> AlarmOptions:
        '''Alarm configuration options to configure the billing alarm e.g. (name, description etc.).'''
        result = self._values.get("alarm_configuration")
        assert result is not None, "Required property 'alarm_configuration' is missing"
        return typing.cast(AlarmOptions, result)

    @builtins.property
    def topic_configuration(self) -> "BillingTopicProps":
        '''Topic configuration options to configure the SNS topic and email address's that will be used to subscribe to the topic.'''
        result = self._values.get("topic_configuration")
        assert result is not None, "Required property 'topic_configuration' is missing"
        return typing.cast("BillingTopicProps", result)

    @builtins.property
    def metric_dimensions(self) -> typing.Optional["MetricDimensionOptions"]:
        '''Metric dimension options to configure advanced alarm metrics e.g. (link the alarm to a specific account, region or AWS service).'''
        result = self._values.get("metric_dimensions")
        return typing.cast(typing.Optional["MetricDimensionOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BillingAlarmProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BillingTopic(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@spacecomx/cdk-billing-alarm.BillingTopic",
):
    '''A construct to create a new SNS topic or use an existing SNS topic Arn.

    It then subscribes the configured email address to the SNS topic or the existing SNS topic Arn.

    Example::

        # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
        org"]"
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        display_name: typing.Optional[builtins.str] = None,
        existing_topic_arn: typing.Optional[builtins.str] = None,
        topic_name: typing.Optional[builtins.str] = None,
        email_address: typing.Sequence[builtins.str],
        json: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param display_name: The display name of the topic. A developer-defined string that can be used to identify this SNS topic. Default: - Not configured
        :param existing_topic_arn: Use an existing SNS topic ARN e.g. ('arn:aws:sns:us-east-2:444455556666:MyTopic'). Default: - Not configured
        :param topic_name: The name of the topic. If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the topic name (recommended). Default: Generated name
        :param email_address: The email address that will be used to subcribe to the SNS topic for billing alert notifications e.g. ['hello@example.org'] or [''hello@example.org', 'admin@example.org'].
        :param json: Indicates if the full notification JSON should be sent to the email address or just the message text. Default: false (Message text)
        '''
        props = BillingTopicProps(
            display_name=display_name,
            existing_topic_arn=existing_topic_arn,
            topic_name=topic_name,
            email_address=email_address,
            json=json,
        )

        jsii.create(BillingTopic, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> aws_cdk.aws_sns.ITopic:
        return typing.cast(aws_cdk.aws_sns.ITopic, jsii.get(self, "topic"))


@jsii.data_type(
    jsii_type="@spacecomx/cdk-billing-alarm.MetricDimensionOptions",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "region": "region", "service": "service"},
)
class MetricDimensionOptions:
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: Account which this metric comes from. Default: - Not configured.
        :param region: Region which this metric comes from. Default: - Not configured.
        :param service: The AWS Service to associate the alarm with e.g (AWSService.AMAZON_API_GATEWAY). Default: - Not configured.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if region is not None:
            self._values["region"] = region
        if service is not None:
            self._values["service"] = service

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''Account which this metric comes from.

        :default: - Not configured.
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region which this metric comes from.

        :default: - Not configured.
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''The AWS Service to associate the alarm with e.g (AWSService.AMAZON_API_GATEWAY).

        :default: - Not configured.
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetricDimensionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@spacecomx/cdk-billing-alarm.SubscribeOptions",
    jsii_struct_bases=[],
    name_mapping={"email_address": "emailAddress", "json": "json"},
)
class SubscribeOptions:
    def __init__(
        self,
        *,
        email_address: typing.Sequence[builtins.str],
        json: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param email_address: The email address that will be used to subcribe to the SNS topic for billing alert notifications e.g. ['hello@example.org'] or [''hello@example.org', 'admin@example.org'].
        :param json: Indicates if the full notification JSON should be sent to the email address or just the message text. Default: false (Message text)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "email_address": email_address,
        }
        if json is not None:
            self._values["json"] = json

    @builtins.property
    def email_address(self) -> typing.List[builtins.str]:
        '''The email address that will be used to subcribe to the SNS topic for billing alert notifications e.g. ['hello@example.org'] or [''hello@example.org', 'admin@example.org'].'''
        result = self._values.get("email_address")
        assert result is not None, "Required property 'email_address' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.bool]:
        '''Indicates if the full notification JSON should be sent to the email address or just the message text.

        :default: false (Message text)
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SubscribeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@spacecomx/cdk-billing-alarm.TopicOptions",
    jsii_struct_bases=[],
    name_mapping={
        "display_name": "displayName",
        "existing_topic_arn": "existingTopicArn",
        "topic_name": "topicName",
    },
)
class TopicOptions:
    def __init__(
        self,
        *,
        display_name: typing.Optional[builtins.str] = None,
        existing_topic_arn: typing.Optional[builtins.str] = None,
        topic_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param display_name: The display name of the topic. A developer-defined string that can be used to identify this SNS topic. Default: - Not configured
        :param existing_topic_arn: Use an existing SNS topic ARN e.g. ('arn:aws:sns:us-east-2:444455556666:MyTopic'). Default: - Not configured
        :param topic_name: The name of the topic. If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the topic name (recommended). Default: Generated name
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if display_name is not None:
            self._values["display_name"] = display_name
        if existing_topic_arn is not None:
            self._values["existing_topic_arn"] = existing_topic_arn
        if topic_name is not None:
            self._values["topic_name"] = topic_name

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''The display name of the topic.

        A developer-defined string that can be used to identify this SNS topic.

        :default: - Not configured
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existing_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Use an existing SNS topic ARN e.g. ('arn:aws:sns:us-east-2:444455556666:MyTopic').

        :default: - Not configured
        '''
        result = self._values.get("existing_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def topic_name(self) -> typing.Optional[builtins.str]:
        '''The name of the topic.

        If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the topic name (recommended).

        :default: Generated name
        '''
        result = self._values.get("topic_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TopicOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@spacecomx/cdk-billing-alarm.BillingTopicProps",
    jsii_struct_bases=[TopicOptions, SubscribeOptions],
    name_mapping={
        "display_name": "displayName",
        "existing_topic_arn": "existingTopicArn",
        "topic_name": "topicName",
        "email_address": "emailAddress",
        "json": "json",
    },
)
class BillingTopicProps(TopicOptions, SubscribeOptions):
    def __init__(
        self,
        *,
        display_name: typing.Optional[builtins.str] = None,
        existing_topic_arn: typing.Optional[builtins.str] = None,
        topic_name: typing.Optional[builtins.str] = None,
        email_address: typing.Sequence[builtins.str],
        json: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param display_name: The display name of the topic. A developer-defined string that can be used to identify this SNS topic. Default: - Not configured
        :param existing_topic_arn: Use an existing SNS topic ARN e.g. ('arn:aws:sns:us-east-2:444455556666:MyTopic'). Default: - Not configured
        :param topic_name: The name of the topic. If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the topic name (recommended). Default: Generated name
        :param email_address: The email address that will be used to subcribe to the SNS topic for billing alert notifications e.g. ['hello@example.org'] or [''hello@example.org', 'admin@example.org'].
        :param json: Indicates if the full notification JSON should be sent to the email address or just the message text. Default: false (Message text)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "email_address": email_address,
        }
        if display_name is not None:
            self._values["display_name"] = display_name
        if existing_topic_arn is not None:
            self._values["existing_topic_arn"] = existing_topic_arn
        if topic_name is not None:
            self._values["topic_name"] = topic_name
        if json is not None:
            self._values["json"] = json

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''The display name of the topic.

        A developer-defined string that can be used to identify this SNS topic.

        :default: - Not configured
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existing_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Use an existing SNS topic ARN e.g. ('arn:aws:sns:us-east-2:444455556666:MyTopic').

        :default: - Not configured
        '''
        result = self._values.get("existing_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def topic_name(self) -> typing.Optional[builtins.str]:
        '''The name of the topic.

        If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the topic name (recommended).

        :default: Generated name
        '''
        result = self._values.get("topic_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_address(self) -> typing.List[builtins.str]:
        '''The email address that will be used to subcribe to the SNS topic for billing alert notifications e.g. ['hello@example.org'] or [''hello@example.org', 'admin@example.org'].'''
        result = self._values.get("email_address")
        assert result is not None, "Required property 'email_address' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.bool]:
        '''Indicates if the full notification JSON should be sent to the email address or just the message text.

        :default: false (Message text)
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BillingTopicProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AWSService",
    "AlarmOptions",
    "BillingAlarm",
    "BillingAlarmProps",
    "BillingTopic",
    "BillingTopicProps",
    "MetricDimensionOptions",
    "SubscribeOptions",
    "TopicOptions",
]

publication.publish()
