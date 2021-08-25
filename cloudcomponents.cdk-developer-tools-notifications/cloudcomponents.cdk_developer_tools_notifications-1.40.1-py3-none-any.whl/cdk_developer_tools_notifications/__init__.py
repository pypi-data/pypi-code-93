'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-developer-tools-notifications

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-developer-tools-notifications)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-developer-tools-notifications/)
[![Mentioned in Awesome CDK](https://awesome.re/mentioned-badge.svg)](https://github.com/kolomied/awesome-cdk)

> #slack / msteams / email notifications for developer tools: CodeCommit, CodeBuild, CodeDeploy, CodePipeline

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-developer-tools-notifications
```

Python:

```bash
pip install cloudcomponents.cdk-developer-tools-notifications
```

## MSTeams

[Add incoming webhook](https://docs.microsoft.com/de-de/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook):

1. Navigate to the channel where you want to add the webhook and select (•••) More Options from the top navigation bar.
2. Choose Connectors from the drop-down menu and search for Incoming Webhook.
3. Select the Configure button, provide a name, and, optionally, upload an image avatar for your webhook.
4. The dialog window will present a unique URL that will map to the channel. Make sure that you copy and save the URL—you will need to provide it to the outside service.
5. Select the Done button. The webhook will be available in the team channel.

![codepipeline message](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/packages/cdk-developer-tools-notifications/assets/codepipeline-message.png)

## #Slack

[Notifications for AWS developer tools](https://docs.aws.amazon.com/chatbot/latest/adminguide/related-services.html#codeserviceevents)

## How to use

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import Construct, Stack, StackProps
from aws_cdk.aws_codecommit import Repository
from aws_cdk.aws_codepipeline import Pipeline, Artifact
from aws_cdk.aws_codepipeline_actions import CodeCommitSourceAction, ManualApprovalAction
from cloudcomponents.cdk_developer_tools_notifications import RepositoryNotificationRule, PipelineNotificationRule, RepositoryEvent, PipelineEvent, SlackChannel, MSTeamsIncomingWebhook
from cloudcomponents.cdk_chatops import SlackChannelConfiguration, MSTeamsIncomingWebhookConfiguration, AccountLabelMode

class NotificationsStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        repository = Repository(self, "Repository",
            repository_name="notifications-repository"
        )

        slack_channel = SlackChannelConfiguration(self, "SlackChannel",
            slack_workspace_id=process.env.SLACK_WORKSPACE_ID,
            configuration_name="notifications",
            slack_channel_id=process.env.SLACK_CHANNEL_ID
        )

        webhook = MSTeamsIncomingWebhookConfiguration(self, "MSTeamsWebhook",
            url=process.env.INCOMING_WEBHOOK_URL,
            account_label_mode=AccountLabelMode.ID_AND_ALIAS,
            theme_color="#FF0000"
        )

        RepositoryNotificationRule(self, "RepoNotifications",
            name="notifications-repository",
            repository=repository,
            events=[RepositoryEvent.COMMENTS_ON_COMMITS, RepositoryEvent.PULL_REQUEST_CREATED, RepositoryEvent.PULL_REQUEST_MERGED
            ],
            targets=[
                SlackChannel(slack_channel),
                MSTeamsIncomingWebhook(webhook)
            ]
        )

        source_artifact = Artifact()

        source_action = CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repository,
            output=source_artifact
        )

        approval_action = ManualApprovalAction(
            action_name="Approval"
        )

        pipeline = Pipeline(self, "Pipeline",
            pipeline_name="notifications-pipeline",
            stages=[StageProps(
                stage_name="Source",
                actions=[source_action]
            ), StageProps(
                stage_name="Approval",
                actions=[approval_action]
            )
            ]
        )

        PipelineNotificationRule(self, "PipelineNotificationRule",
            name="pipeline-notification",
            pipeline=pipeline,
            events=[PipelineEvent.PIPELINE_EXECUTION_STARTED, PipelineEvent.PIPELINE_EXECUTION_FAILED, PipelineEvent.PIPELINE_EXECUTION_SUCCEEDED, PipelineEvent.MANUAL_APPROVAL_NEEDED, PipelineEvent.MANUAL_APPROVAL_SUCCEEDED
            ],
            targets=[
                SlackChannel(slack_channel),
                MSTeamsIncomingWebhook(webhook)
            ]
        )
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-developer-tools-notifications/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-developer-tools-notifications/LICENSE)
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

import aws_cdk.aws_codebuild
import aws_cdk.aws_codecommit
import aws_cdk.aws_codedeploy
import aws_cdk.aws_codepipeline
import aws_cdk.aws_sns
import aws_cdk.core
import cloudcomponents.cdk_chatops


@jsii.enum(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.ApplicationEvent"
)
class ApplicationEvent(enum.Enum):
    DEPLOYMENT_FAILED = "DEPLOYMENT_FAILED"
    DEPLOYMENT_SUCCEEDED = "DEPLOYMENT_SUCCEEDED"
    DEPLOYMENT_STARTED = "DEPLOYMENT_STARTED"


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.CommonNotificationRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
    },
)
class CommonNotificationRuleProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional["DetailType"] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence["INotificationTarget"]] = None,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional["DetailType"]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional["DetailType"], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List["INotificationTarget"]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List["INotificationTarget"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cloudcomponents/cdk-developer-tools-notifications.DetailType")
class DetailType(enum.Enum):
    FULL = "FULL"
    BASIC = "BASIC"


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.INotificationRule"
)
class INotificationRule(typing_extensions.Protocol):
    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_INotificationRuleProxy"]:
        return _INotificationRuleProxy

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationRuleArn")
    def notification_rule_arn(self) -> builtins.str:
        ...


class _INotificationRuleProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-developer-tools-notifications.INotificationRule"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationRuleArn")
    def notification_rule_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationRuleArn"))


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.INotificationTarget"
)
class INotificationTarget(typing_extensions.Protocol):
    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_INotificationTargetProxy"]:
        return _INotificationTargetProxy

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: aws_cdk.core.Construct,
        rule: INotificationRule,
    ) -> "NotificationTargetProperty":
        '''
        :param scope: -
        :param rule: -
        '''
        ...


class _INotificationTargetProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-developer-tools-notifications.INotificationTarget"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: aws_cdk.core.Construct,
        rule: INotificationRule,
    ) -> "NotificationTargetProperty":
        '''
        :param scope: -
        :param rule: -
        '''
        return typing.cast("NotificationTargetProperty", jsii.invoke(self, "bind", [scope, rule]))


@jsii.implements(INotificationTarget)
class MSTeamsIncomingWebhook(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.MSTeamsIncomingWebhook",
):
    def __init__(
        self,
        webhook: cloudcomponents.cdk_chatops.MSTeamsIncomingWebhookConfiguration,
    ) -> None:
        '''
        :param webhook: -
        '''
        jsii.create(MSTeamsIncomingWebhook, self, [webhook])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: aws_cdk.core.Construct,
        _rule: INotificationRule,
    ) -> "NotificationTargetProperty":
        '''
        :param scope: -
        :param _rule: -
        '''
        return typing.cast("NotificationTargetProperty", jsii.invoke(self, "bind", [scope, _rule]))


@jsii.implements(INotificationRule)
class NotificationRule(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.NotificationRule",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[typing.Union["RepositoryEvent", "ProjectEvent", ApplicationEvent, "PipelineEvent"]],
        resource: builtins.str,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: A list of events associated with this notification rule.
        :param resource: The Amazon Resource Name (ARN) of the resource to associate with the notification rule. Supported resources include pipelines in AWS CodePipeline, repositories in AWS CodeCommit, and build projects in AWS CodeBuild.
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        props = NotificationRuleProps(
            events=events,
            resource=resource,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(NotificationRule, self, [scope, id, props])

    @jsii.member(jsii_name="addTarget")
    def add_target(self, target: INotificationTarget) -> None:
        '''
        :param target: -
        '''
        return typing.cast(None, jsii.invoke(self, "addTarget", [target]))

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[builtins.str]:
        '''Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationRuleArn")
    def notification_rule_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationRuleArn"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.NotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "events": "events",
        "resource": "resource",
    },
)
class NotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        events: typing.Sequence[typing.Union["RepositoryEvent", "ProjectEvent", ApplicationEvent, "PipelineEvent"]],
        resource: builtins.str,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param events: A list of events associated with this notification rule.
        :param resource: The Amazon Resource Name (ARN) of the resource to associate with the notification rule. Supported resources include pipelines in AWS CodePipeline, repositories in AWS CodeCommit, and build projects in AWS CodeBuild.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "events": events,
            "resource": resource,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def events(
        self,
    ) -> typing.List[typing.Union["RepositoryEvent", "ProjectEvent", ApplicationEvent, "PipelineEvent"]]:
        '''A list of events associated with this notification rule.'''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[typing.Union["RepositoryEvent", "ProjectEvent", ApplicationEvent, "PipelineEvent"]], result)

    @builtins.property
    def resource(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the resource to associate with the notification rule.

        Supported resources include pipelines in
        AWS CodePipeline, repositories in AWS CodeCommit, and build
        projects in AWS CodeBuild.
        '''
        result = self._values.get("resource")
        assert result is not None, "Required property 'resource' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.NotificationTargetProperty",
    jsii_struct_bases=[],
    name_mapping={"target_address": "targetAddress", "target_type": "targetType"},
)
class NotificationTargetProperty:
    def __init__(
        self,
        *,
        target_address: builtins.str,
        target_type: "TargetType",
    ) -> None:
        '''
        :param target_address: -
        :param target_type: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_address": target_address,
            "target_type": target_type,
        }

    @builtins.property
    def target_address(self) -> builtins.str:
        result = self._values.get("target_address")
        assert result is not None, "Required property 'target_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> "TargetType":
        result = self._values.get("target_type")
        assert result is not None, "Required property 'target_type' is missing"
        return typing.cast("TargetType", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationTargetProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.PipelineEvent"
)
class PipelineEvent(enum.Enum):
    ACTION_EXECUTION_SUCCEEDED = "ACTION_EXECUTION_SUCCEEDED"
    ACTION_EXECUTION_FAILED = "ACTION_EXECUTION_FAILED"
    ACTION_EXECUTION_CANCELED = "ACTION_EXECUTION_CANCELED"
    ACTION_EXECUTION_STARTED = "ACTION_EXECUTION_STARTED"
    STAGE_EXECUTION_STARTED = "STAGE_EXECUTION_STARTED"
    STAGE_EXECUTION_SUCCEEDED = "STAGE_EXECUTION_SUCCEEDED"
    STAGE_EXECUTION_RESUMED = "STAGE_EXECUTION_RESUMED"
    STAGE_EXECUTION_CANCELED = "STAGE_EXECUTION_CANCELED"
    STAGE_EXECUTION_FAILED = "STAGE_EXECUTION_FAILED"
    PIPELINE_EXECUTION_FAILED = "PIPELINE_EXECUTION_FAILED"
    PIPELINE_EXECUTION_CANCELED = "PIPELINE_EXECUTION_CANCELED"
    PIPELINE_EXECUTION_STARTED = "PIPELINE_EXECUTION_STARTED"
    PIPELINE_EXECUTION_RESUMED = "PIPELINE_EXECUTION_RESUMED"
    PIPELINE_EXECUTION_SUCCEEDED = "PIPELINE_EXECUTION_SUCCEEDED"
    PIPELINE_EXECUTION_SUPERSEDED = "PIPELINE_EXECUTION_SUPERSEDED"
    MANUAL_APPROVAL_FAILED = "MANUAL_APPROVAL_FAILED"
    MANUAL_APPROVAL_NEEDED = "MANUAL_APPROVAL_NEEDED"
    MANUAL_APPROVAL_SUCCEEDED = "MANUAL_APPROVAL_SUCCEEDED"


class PipelineNotificationRule(
    NotificationRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.PipelineNotificationRule",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[PipelineEvent],
        pipeline: aws_cdk.aws_codepipeline.IPipeline,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: -
        :param pipeline: -
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        props = PipelineNotificationRuleProps(
            events=events,
            pipeline=pipeline,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(PipelineNotificationRule, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.PipelineNotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "events": "events",
        "pipeline": "pipeline",
    },
)
class PipelineNotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        events: typing.Sequence[PipelineEvent],
        pipeline: aws_cdk.aws_codepipeline.IPipeline,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param events: -
        :param pipeline: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "events": events,
            "pipeline": pipeline,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def events(self) -> typing.List[PipelineEvent]:
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[PipelineEvent], result)

    @builtins.property
    def pipeline(self) -> aws_cdk.aws_codepipeline.IPipeline:
        result = self._values.get("pipeline")
        assert result is not None, "Required property 'pipeline' is missing"
        return typing.cast(aws_cdk.aws_codepipeline.IPipeline, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cloudcomponents/cdk-developer-tools-notifications.ProjectEvent")
class ProjectEvent(enum.Enum):
    BUILD_STATE_FAILED = "BUILD_STATE_FAILED"
    BUILD_STATE_SUCCEEDED = "BUILD_STATE_SUCCEEDED"
    BUILD_STATE_IN_PROGRESS = "BUILD_STATE_IN_PROGRESS"
    BUILD_STATE_STOPPED = "BUILD_STATE_STOPPED"
    BUILD_PHASE_FAILURE = "BUILD_PHASE_FAILURE"
    BUILD_PHASE_SUCCESS = "BUILD_PHASE_SUCCESS"


class ProjectNotificationRule(
    NotificationRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.ProjectNotificationRule",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[ProjectEvent],
        project: aws_cdk.aws_codebuild.IProject,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: -
        :param project: -
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        props = ProjectNotificationRuleProps(
            events=events,
            project=project,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(ProjectNotificationRule, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.ProjectNotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "events": "events",
        "project": "project",
    },
)
class ProjectNotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        events: typing.Sequence[ProjectEvent],
        project: aws_cdk.aws_codebuild.IProject,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param events: -
        :param project: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "events": events,
            "project": project,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def events(self) -> typing.List[ProjectEvent]:
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[ProjectEvent], result)

    @builtins.property
    def project(self) -> aws_cdk.aws_codebuild.IProject:
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(aws_cdk.aws_codebuild.IProject, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.RepositoryEvent"
)
class RepositoryEvent(enum.Enum):
    COMMENTS_ON_COMMITS = "COMMENTS_ON_COMMITS"
    COMMENTS_ON_PULL_REQUEST = "COMMENTS_ON_PULL_REQUEST"
    APPROVAL_STATUS_CHANGED = "APPROVAL_STATUS_CHANGED"
    APPROVAL_RULE_OVERRIDE = "APPROVAL_RULE_OVERRIDE"
    PULL_REQUEST_CREATED = "PULL_REQUEST_CREATED"
    PULL_REQUEST_SOURCE_UPDATED = "PULL_REQUEST_SOURCE_UPDATED"
    PULL_REQUEST_STATUS_CHANGED = "PULL_REQUEST_STATUS_CHANGED"
    PULL_REQUEST_MERGED = "PULL_REQUEST_MERGED"
    BRANCHES_AND_TAGS_CREATED = "BRANCHES_AND_TAGS_CREATED"
    BRANCHES_AND_TAGS_DELETED = "BRANCHES_AND_TAGS_DELETED"
    BRANCHES_AND_TAGS_UPDATED = "BRANCHES_AND_TAGS_UPDATED"


class RepositoryNotificationRule(
    NotificationRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.RepositoryNotificationRule",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[RepositoryEvent],
        repository: aws_cdk.aws_codecommit.IRepository,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: -
        :param repository: -
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        props = RepositoryNotificationRuleProps(
            events=events,
            repository=repository,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(RepositoryNotificationRule, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.RepositoryNotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "events": "events",
        "repository": "repository",
    },
)
class RepositoryNotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        events: typing.Sequence[RepositoryEvent],
        repository: aws_cdk.aws_codecommit.IRepository,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param events: -
        :param repository: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "events": events,
            "repository": repository,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def events(self) -> typing.List[RepositoryEvent]:
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[RepositoryEvent], result)

    @builtins.property
    def repository(self) -> aws_cdk.aws_codecommit.IRepository:
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(aws_cdk.aws_codecommit.IRepository, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(INotificationTarget)
class SlackChannel(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.SlackChannel",
):
    def __init__(
        self,
        channel: cloudcomponents.cdk_chatops.ISlackChannelConfiguration,
    ) -> None:
        '''
        :param channel: -
        '''
        jsii.create(SlackChannel, self, [channel])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: aws_cdk.core.Construct,
        _rule: INotificationRule,
    ) -> NotificationTargetProperty:
        '''
        :param _scope: -
        :param _rule: -
        '''
        return typing.cast(NotificationTargetProperty, jsii.invoke(self, "bind", [_scope, _rule]))


@jsii.implements(INotificationTarget)
class SnsTopic(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.SnsTopic",
):
    def __init__(self, topic: aws_cdk.aws_sns.ITopic) -> None:
        '''
        :param topic: -
        '''
        jsii.create(SnsTopic, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: aws_cdk.core.Construct,
        _rule: INotificationRule,
    ) -> NotificationTargetProperty:
        '''
        :param _scope: -
        :param _rule: -
        '''
        return typing.cast(NotificationTargetProperty, jsii.invoke(self, "bind", [_scope, _rule]))


@jsii.enum(jsii_type="@cloudcomponents/cdk-developer-tools-notifications.Status")
class Status(enum.Enum):
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"


@jsii.enum(jsii_type="@cloudcomponents/cdk-developer-tools-notifications.TargetType")
class TargetType(enum.Enum):
    SNS = "SNS"
    AWS_CHATBOT_SLACK = "AWS_CHATBOT_SLACK"


class ApplicationNotificationRule(
    NotificationRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.ApplicationNotificationRule",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        application: typing.Union[aws_cdk.aws_codedeploy.IServerApplication, aws_cdk.aws_codedeploy.ILambdaApplication, aws_cdk.aws_codedeploy.IEcsApplication],
        events: typing.Sequence[ApplicationEvent],
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional[Status] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application: -
        :param events: -
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        props = ApplicationNotificationRuleProps(
            application=application,
            events=events,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(ApplicationNotificationRule, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-developer-tools-notifications.ApplicationNotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "application": "application",
        "events": "events",
    },
)
class ApplicationNotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional[Status] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        application: typing.Union[aws_cdk.aws_codedeploy.IServerApplication, aws_cdk.aws_codedeploy.ILambdaApplication, aws_cdk.aws_codedeploy.IEcsApplication],
        events: typing.Sequence[ApplicationEvent],
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param application: -
        :param events: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "application": application,
            "events": events,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional[Status]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[Status], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def application(
        self,
    ) -> typing.Union[aws_cdk.aws_codedeploy.IServerApplication, aws_cdk.aws_codedeploy.ILambdaApplication, aws_cdk.aws_codedeploy.IEcsApplication]:
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast(typing.Union[aws_cdk.aws_codedeploy.IServerApplication, aws_cdk.aws_codedeploy.ILambdaApplication, aws_cdk.aws_codedeploy.IEcsApplication], result)

    @builtins.property
    def events(self) -> typing.List[ApplicationEvent]:
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[ApplicationEvent], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApplicationEvent",
    "ApplicationNotificationRule",
    "ApplicationNotificationRuleProps",
    "CommonNotificationRuleProps",
    "DetailType",
    "INotificationRule",
    "INotificationTarget",
    "MSTeamsIncomingWebhook",
    "NotificationRule",
    "NotificationRuleProps",
    "NotificationTargetProperty",
    "PipelineEvent",
    "PipelineNotificationRule",
    "PipelineNotificationRuleProps",
    "ProjectEvent",
    "ProjectNotificationRule",
    "ProjectNotificationRuleProps",
    "RepositoryEvent",
    "RepositoryNotificationRule",
    "RepositoryNotificationRuleProps",
    "SlackChannel",
    "SnsTopic",
    "Status",
    "TargetType",
]

publication.publish()
