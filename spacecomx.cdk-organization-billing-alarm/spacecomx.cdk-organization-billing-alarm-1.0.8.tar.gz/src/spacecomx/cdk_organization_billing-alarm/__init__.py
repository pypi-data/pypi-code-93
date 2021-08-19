'''
[![npm version](https://badge.fury.io/js/%40spacecomx%2Fcdk-organization-billing-alarm.svg)](https://badge.fury.io/js/%40spacecomx%2Fcdk-organization-billing-alarm)
[![PyPI version](https://badge.fury.io/py/spacecomx.cdk-organization-billing-alarm.svg)](https://badge.fury.io/py/spacecomx.cdk-organization-billing-alarm)

# @spacecomx/cdk-organization-billing-alarm

Multi-account CDK construct to monitor estimated billing charges with alerts and notifications for a AWS Organization. It gives you the capability to monitor specific AWS Service charges, by a linked AWS account in a master/payer account. It can create customizable billing alarms for multiple linked AWS accounts within AWS Organization. It can subscribe multiple email address endpoints to an SNS Topic created by the package or it can use an existing SNS Topic Arn within the master/payer account.

For single AWS account billing alarm requirements, see [@spacecomx/cdk-billing-alarm](https://github.com/spacecomx/cdk-billing-alarm#readme)

## Table of Contents

* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Usage](#usage)

  * [Example 1: Create billing alarm in a master/payer account](#example_1)
  * [Example 2: Link alarm to an existing SNS Topic Arn](#example_2)
  * [Example 3: Link alarm to specific AWS Account in master/payer account](#example_3)
  * [Example 4: Updating/Removing SNS Topic email address endpoint subscription](#example_4)
* [Post Deployment](#post-deployment)
* [API Documentation](#api-documentation)

## Prerequisites

> :warning: Before you can create a billing alarm, you must enable billing alerts in your master/payer account when using consolidated billing. For more information, see [Enabling Billing Alerts](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html#turning_on_billing_metrics).

## Installation

TypeScript/JavaScript:

```bash
npm i @spacecomx/cdk-organization-billing-alarm
```

or:

```bash
yarn add @spacecomx/cdk-organization-billing-alarm
```

Python:

```bash
pip install spacecomx.cdk-organization-billing-alarm
```

## Usage

<a name="example_1"></a>

### Example 1: Create billing alarm in a master/payer account.

This type of billing alarm configuration will provide estimated charges for every AWS Service that you use, in addition to the estimated overall total of your AWS charges within your AWS master/payer account e.g (AWS Organization).

* It creates a new SNS Topic in your AWS master/payer account.
* It then subscribes the email address endpoint to the topic.
* It then creates the Cloudwach estimate billing alarm.
* It then associates the SNS topic with the newly created billing alarm.

> :small_orange_diamond: The `emailAddress` is an endpoint that subscribes to a SNS topic. The `thresholdAmount` is the amount in USD, that will trigger the alarm when AWS charges exceed the threshold.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import Stack, StackProps
from spacecomx.cdk_organization_billing_alarm import MasterAccountAlarm, MasterAccountAlarmProps

class OrganizationBillingAlarmStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        config = {
            "alarm_configuration": {
                "topic_description": "Organization Billing Alarm Topic",
                "email_address": ["billing@example.org", "admin@example.org"],
                "alarm_description": "Consolidated Billing Alarm: All AWS Services",
                "threshold_amount": 140
            }
        }

        MasterAccountAlarm(self, "MasterAccountAlarm", config)
```

<a name="example_2"></a>

### Example 2: Link alarm to an existing SNS Topic Arn.

This type of billing alarm configuration simliar to [example 1](#example_1), with the exception that the billing alarm is now linked to an existing SNS Topic in the master/payer account.

* It uses an existing SNS Topic within the AWS master/payer account.
* It imports a secret by secret name that was created in master/payer account using AWS Secrets Manager e.g (prod/billing/topicArn).
* It then subscribes the email address endpoint to the retrieved SNS Topic's Arn.
* It then creates the Cloudwach estimate billing alarm.
* It then associates the SNS topic with the newly created billing alarm.

> :small_orange_diamond: The `secretName` option is required and used to retrieve the existing SNS Topic's Arn from AWS Secrets Manager. The secret name **must exist** in the same account and region as the master/payer AWS account.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import Stack, StackProps
from spacecomx.cdk_organization_billing_alarm import MasterAccountAlarm, MasterAccountAlarmProps

class OrganizationBillingAlarmStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        config = {
            "secret_name": "prod/billing/topicArn", # existing sns topic arn
            "alarm_configuration": {
                "email_address": ["john@example.org"],
                "alarm_description": "Consolidated Billing Alarm: All AWS Services",
                "threshold_amount": 140
            }
        }

        MasterAccountAlarm(self, "MasterAccountAlarm", config)
```

<a name="example_3"></a>

### Example 3: Link alarm to specific AWS Account in master/payer account.

This type of billing alarm configuration provides customizable options for linked AWS accounts within the master/payer account. The packages `accountConfiguration` required option allows for multiple AWS accounts to link to a single SNS Topic using the required `secretName` option.

* It uses an existing SNS Topic's Arn within the AWS master/payer account.
* It imports a secret by secret name that was created in master/payer account using AWS Secrets Manager e.g (prod/billing/topicArn).
* It then creates the Cloudwach estimate billing alarm associated to the linked AWS account.
* It then associates the SNS topic with the newly created billing alarm.

> :small_orange_diamond: The `secretName` option is required and used to retrieve the existing SNS Topic's Arn from AWS Secrets Manager. The secret name **must exist** in the same account and region as the master/payer AWS account.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import Stack, StackProps
from spacecomx.cdk_organization_billing_alarm import LinkedAccountAlarm, LinkedAccountAlarmProps

class OrganizationBillingAlarmStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        config = {
            "secret_name": "prod/billing/topicArn",
            "account_configuration": [{
                "account": "444455556666",
                "alarm_name": "Billing Alarm (Acc: 444455556666)", # named by aws-cdk (recommended)
                "alarm_description": "Billing Alarm: All AWS Services (Acc: 444455556666)",
                "threshold_amount": 50
            }
            ]
        }

        LinkedAccountAlarm(self, "LinkedAccountAlarm", config)
```

-OR-

You can manage **multiple linked AWS accounts** each with its own billing alarm configuration, with a single implementation of the `LinkedAccountAlarm` construct. The code example below uses a ***single SNS Topic*** to manage alerts and notifications for all linked accounts within the master/payer account. Each linked account can send alerts and notifications to either a single email address or multiple email addresses, subscribed to the SNS Topic within the master/payer account

> :small_orange_diamond: Should you need more that one SNS topic e.g. you want seperate out linked accounts by department or business unit, each having its own SNS Topic. One option would be to, firstly create an SNS Topic in the master/payer account for each department or business unit. Remember to create a new secret with that SNS Topic's Arn in AWS Secrets Manager. Then simply, new up `LinkedAccountAlarm` constructs that group those linked accounts by department or business unit, each with its own SNS Topic.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
config = {
    "secret_name": "prod/billing/other/topicArn", # single topic used by multiple accounts
    "account_configuration": [{
        "account": "444455556666",
        "alarm_description": "Billing Alarm: All AWS Services (Acc: 444455556666)",
        "threshold_amount": 50
    }, {
        "account": "123456789000",
        "alarm_description": "Billing Alarm: All AWS Services (Acc: 123456789000)",
        "threshold_amount": 120
    }
    ]
}
```

> :small_orange_diamond: You can also link the alarm to a specific AWS Service, per linked AWS account. Use the `awsService` option. See the code example below.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
config = {
    "secret_name": "prod/billing/topicArn",
    "account_configuration": [{
        "account": "444455556666",
        "alarm_description": "Billing Alarm: All AWS Services (Acc: 444455556666)",
        "threshold_amount": 50
    }, {
        "account": "123456789000",
        "alarm_description": "Billing Alarm: Amazon DynamoDB (Acc: 123456789000)",
        "threshold_amount": 120,
        "aws_service": "AmazonDynamoDB"
    }
    ]
}
```

> :small_orange_diamond: Should you need to remove a `awsService` subscribed to a specific linked account, simply remove the `awsService` option.

<a name="example_4"></a>

### Example 4: Updating/Removing SNS Topic email address endpoint subscription.

When would you use this option?

* When an existing SNS topic that already has an email address endpoint subscribed to it,
* or you dont require any additional email address endpoints to be added to the existing topic,
* or you want to add your own email address endpoints manually to the SNS topic (not recommended),
* or you want to remove an email address endpoints from the SNS topic created with the package,
* or you want to add or update email address endpoints for the SNS topic using the package.

> :small_orange_diamond: To manage adding and removing endpoints for the SNS topic, use the packages `emailAddress` option. You can simply set the `emailAddress: ['john@example.org']` option to `emailAddress: []`. Please note that email endpoint subscriptions created manually via AWS SNS Console **will not be removed** by the package.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
config = {
    "alarm_configuration": {
        "email_address": [], ...
    }
}
```

Adding and removing endpoints means ***you will need to again confirm the subscription*** of each email address you specified with `emailAddress` option or those added manually by you e.g AWS SNS console (not recommended). See [post deployment](#post-deployment) for details.

> :warning: Please be **cautious**. Without an endpoint been provided i.e. (email address been subscribed to the SNS topic), the billing alarm will still trigger when exceeding the alarm threshold. However you will **not recieve any email alarm notifications** via email.

## Post Deployment

Once the Billing Alarm Stack resources has been successfully created in your AWS account, you will need to confirm the subscription of each email address you specified with the `emailAddress` configuration option. Clicking on the **"Confirm Subscription"** link for that email, will automatically activate billing alarm notifications for that email address.

If you did not receive the email, you can process a **"Request Confirmation"** for the subscription from the Simple Notification Service (SNS) console within your AWS account.

> :warning: Without confirming the email subscription you will **not recieve any email alarm notifications** via email. The billing alarm will trigger when exceeding the alarm threshold, but **you will not be notified** via email.

## API Documentation

For more detail, see [API documentation](https://github.com/spacecomx/cdk-organization-billing-alarm/blob/main/API.md)

## Contributions

Contributions of all kinds are welcome! Check out our [contributor's guide](https://github.com/spacecomx/cdk-organization-billing-alarm/blob/main/CONTRIBUTING.md) and our [code of conduct](https://github.com/spacecomx/cdk-organization-billing-alarm/blob/main/CODE_OF_CONDUCT.md)

## Credits

* [Wayne Gibson](https://github.com/waynegibson)

## Alternatives

* [@spacecomx/cdk-billing-alarm](https://github.com/spacecomx/cdk-billing-alarm#readme) - used for single account billing alarm requirements and some.

## License

@spacecomx/cdk-organization-billing-alarm is distributed under the [MIT](https://github.com/spacecomx/cdk-organization-billing-alarm/blob/main/LICENSE) license.
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

import aws_cdk.core


@jsii.data_type(
    jsii_type="@spacecomx/cdk-organization-billing-alarm.AlarmConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_description": "alarmDescription",
        "email_address": "emailAddress",
        "threshold_amount": "thresholdAmount",
        "aws_service": "awsService",
        "topic_description": "topicDescription",
    },
)
class AlarmConfig:
    def __init__(
        self,
        *,
        alarm_description: builtins.str,
        email_address: typing.Sequence[builtins.str],
        threshold_amount: jsii.Number,
        aws_service: typing.Optional[builtins.str] = None,
        topic_description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alarm_description: Description for the alarm. A developer-defined string that can be used to identify this alarm.
        :param email_address: The email address that will be used to subcribe to the SNS topic for billing alert notifications e.g. ['hello@example.org'] or [''hello@example.org', 'admin@example.org']. Default: - Not configured
        :param threshold_amount: Enter the threshold amount in USD that must be exceeded to trigger the alarm e.g. (limit: 150).
        :param aws_service: The AWS Service to associate the alarm with e.g (AmazonDynamoDB). Default: - Not configured.
        :param topic_description: Description for the topic. A developer-defined string that can be used to identify this topic.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alarm_description": alarm_description,
            "email_address": email_address,
            "threshold_amount": threshold_amount,
        }
        if aws_service is not None:
            self._values["aws_service"] = aws_service
        if topic_description is not None:
            self._values["topic_description"] = topic_description

    @builtins.property
    def alarm_description(self) -> builtins.str:
        '''Description for the alarm.

        A developer-defined string that can be used to identify this alarm.
        '''
        result = self._values.get("alarm_description")
        assert result is not None, "Required property 'alarm_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email_address(self) -> typing.List[builtins.str]:
        '''The email address that will be used to subcribe to the SNS topic for billing alert notifications e.g. ['hello@example.org'] or [''hello@example.org', 'admin@example.org'].

        :default: - Not configured
        '''
        result = self._values.get("email_address")
        assert result is not None, "Required property 'email_address' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def threshold_amount(self) -> jsii.Number:
        '''Enter the threshold amount in USD that must be exceeded to trigger the alarm e.g. (limit: 150).'''
        result = self._values.get("threshold_amount")
        assert result is not None, "Required property 'threshold_amount' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def aws_service(self) -> typing.Optional[builtins.str]:
        '''The AWS Service to associate the alarm with e.g (AmazonDynamoDB).

        :default: - Not configured.
        '''
        result = self._values.get("aws_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def topic_description(self) -> typing.Optional[builtins.str]:
        '''Description for the topic.

        A developer-defined string that can be used to identify this topic.
        '''
        result = self._values.get("topic_description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlarmConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LinkedAccountAlarm(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@spacecomx/cdk-organization-billing-alarm.LinkedAccountAlarm",
):
    '''A construct to create a linked account billing alarm within a master/payer AWS account e.g (AWS Organization).

    Example::

        # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
        org"] },"
        account: '123456789000', alarmDescription"Billing Alarm for AWS DynamoDB charge estimates only (Account: 123456789000)" , threshold_amount120 , aws_service"AmazonDynamoDB"
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        account_configuration: typing.Sequence["LinkedAccountConfig"],
        secret_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account_configuration: Account configuration to configure linked account billing alarms with an exsiting SNS topic.
        :param secret_name: Imports a secret by secret name e.g 'prod/billing/topicArn'. A secret with this name must exist in the same account & region as the master/payer AWS account.
        '''
        props = LinkedAccountAlarmProps(
            account_configuration=account_configuration, secret_name=secret_name
        )

        jsii.create(LinkedAccountAlarm, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@spacecomx/cdk-organization-billing-alarm.LinkedAccountAlarmProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_configuration": "accountConfiguration",
        "secret_name": "secretName",
    },
)
class LinkedAccountAlarmProps:
    def __init__(
        self,
        *,
        account_configuration: typing.Sequence["LinkedAccountConfig"],
        secret_name: builtins.str,
    ) -> None:
        '''
        :param account_configuration: Account configuration to configure linked account billing alarms with an exsiting SNS topic.
        :param secret_name: Imports a secret by secret name e.g 'prod/billing/topicArn'. A secret with this name must exist in the same account & region as the master/payer AWS account.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_configuration": account_configuration,
            "secret_name": secret_name,
        }

    @builtins.property
    def account_configuration(self) -> typing.List["LinkedAccountConfig"]:
        '''Account configuration to configure linked account billing alarms with an exsiting SNS topic.'''
        result = self._values.get("account_configuration")
        assert result is not None, "Required property 'account_configuration' is missing"
        return typing.cast(typing.List["LinkedAccountConfig"], result)

    @builtins.property
    def secret_name(self) -> builtins.str:
        '''Imports a secret by secret name e.g 'prod/billing/topicArn'.

        A secret with this name must exist in the same account & region as the master/payer AWS account.
        '''
        result = self._values.get("secret_name")
        assert result is not None, "Required property 'secret_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LinkedAccountAlarmProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@spacecomx/cdk-organization-billing-alarm.LinkedAccountConfig",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "alarm_description": "alarmDescription",
        "threshold_amount": "thresholdAmount",
        "alarm_name": "alarmName",
        "aws_service": "awsService",
        "email_address": "emailAddress",
    },
)
class LinkedAccountConfig:
    def __init__(
        self,
        *,
        account: builtins.str,
        alarm_description: builtins.str,
        threshold_amount: jsii.Number,
        alarm_name: typing.Optional[builtins.str] = None,
        aws_service: typing.Optional[builtins.str] = None,
        email_address: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param account: Account id which this metric comes from.
        :param alarm_description: Description for the alarm. A developer-defined string that can be used to identify this alarm.
        :param threshold_amount: Enter the threshold amount in USD that must be exceeded to trigger the alarm e.g. (limit: 150).
        :param alarm_name: Name of the alarm. If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the alarm name (recommended). Default: Generated name
        :param aws_service: The AWS Service to associate the alarm with e.g (AmazonDynamoDB). Default: - Not configured.
        :param email_address: The email address that will be used to subcribe to the SNS topic for billing alert notifications e.g. ['hello@example.org'] or [''hello@example.org', 'admin@example.org']. Default: - Not configured
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "alarm_description": alarm_description,
            "threshold_amount": threshold_amount,
        }
        if alarm_name is not None:
            self._values["alarm_name"] = alarm_name
        if aws_service is not None:
            self._values["aws_service"] = aws_service
        if email_address is not None:
            self._values["email_address"] = email_address

    @builtins.property
    def account(self) -> builtins.str:
        '''Account id which this metric comes from.'''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alarm_description(self) -> builtins.str:
        '''Description for the alarm.

        A developer-defined string that can be used to identify this alarm.
        '''
        result = self._values.get("alarm_description")
        assert result is not None, "Required property 'alarm_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold_amount(self) -> jsii.Number:
        '''Enter the threshold amount in USD that must be exceeded to trigger the alarm e.g. (limit: 150).'''
        result = self._values.get("threshold_amount")
        assert result is not None, "Required property 'threshold_amount' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def alarm_name(self) -> typing.Optional[builtins.str]:
        '''Name of the alarm.

        If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the alarm name (recommended).

        :default: Generated name
        '''
        result = self._values.get("alarm_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_service(self) -> typing.Optional[builtins.str]:
        '''The AWS Service to associate the alarm with e.g (AmazonDynamoDB).

        :default: - Not configured.
        '''
        result = self._values.get("aws_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_address(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The email address that will be used to subcribe to the SNS topic for billing alert notifications e.g. ['hello@example.org'] or [''hello@example.org', 'admin@example.org'].

        :default: - Not configured
        '''
        result = self._values.get("email_address")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LinkedAccountConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MasterAccountAlarm(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@spacecomx/cdk-organization-billing-alarm.MasterAccountAlarm",
):
    '''A construct to create a master account billing alarm in master/payer AWS account e.g (AWS Organization).

    Example::

        # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
        org"],"alarmDescription: 'Consolidated billing alarm for all AWS Service charges',
        thresholdAmount140 ,
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        alarm_configuration: AlarmConfig,
        secret_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alarm_configuration: Alarm configuration options to configure the AWS master/payer account billing alarm, with SNS topic or an existing Topic Arn.
        :param secret_name: Imports a secret by secret name e.g 'prod/billing/topicArn'. A secret with this name must exist in the same account & region as the master/payer AWS account.
        '''
        props = MasterAccountAlarmProps(
            alarm_configuration=alarm_configuration, secret_name=secret_name
        )

        jsii.create(MasterAccountAlarm, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@spacecomx/cdk-organization-billing-alarm.MasterAccountAlarmProps",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_configuration": "alarmConfiguration",
        "secret_name": "secretName",
    },
)
class MasterAccountAlarmProps:
    def __init__(
        self,
        *,
        alarm_configuration: AlarmConfig,
        secret_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alarm_configuration: Alarm configuration options to configure the AWS master/payer account billing alarm, with SNS topic or an existing Topic Arn.
        :param secret_name: Imports a secret by secret name e.g 'prod/billing/topicArn'. A secret with this name must exist in the same account & region as the master/payer AWS account.
        '''
        if isinstance(alarm_configuration, dict):
            alarm_configuration = AlarmConfig(**alarm_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "alarm_configuration": alarm_configuration,
        }
        if secret_name is not None:
            self._values["secret_name"] = secret_name

    @builtins.property
    def alarm_configuration(self) -> AlarmConfig:
        '''Alarm configuration options to configure the AWS master/payer account billing alarm, with SNS topic or an existing Topic Arn.'''
        result = self._values.get("alarm_configuration")
        assert result is not None, "Required property 'alarm_configuration' is missing"
        return typing.cast(AlarmConfig, result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''Imports a secret by secret name e.g 'prod/billing/topicArn'.

        A secret with this name must exist in the same account & region as the master/payer AWS account.
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MasterAccountAlarmProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AlarmConfig",
    "LinkedAccountAlarm",
    "LinkedAccountAlarmProps",
    "LinkedAccountConfig",
    "MasterAccountAlarm",
    "MasterAccountAlarmProps",
]

publication.publish()
