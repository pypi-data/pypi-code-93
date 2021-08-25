'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-chatops

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-chatops)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-chatops/)

> Constructs for chattool integration: #slack / msteams

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-chatops
```

Python:

```bash
pip install cloudcomponents.cdk-chatops
```

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

## MSTeams

[Add incoming webhook](https://docs.microsoft.com/de-de/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook):

1. Navigate to the channel where you want to add the webhook and select (•••) More Options from the top navigation bar.
2. Choose Connectors from the drop-down menu and search for Incoming Webhook.
3. Select the Configure button, provide a name, and, optionally, upload an image avatar for your webhook.
4. The dialog window will present a unique URL that will map to the channel. Make sure that you copy and save the URL—you will need to provide it to the outside service.
5. Select the Done button. The webhook will be available in the team channel.

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-chatops/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-chatops/LICENSE)
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

import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_lambda_event_sources
import aws_cdk.aws_sns
import aws_cdk.core


@jsii.enum(jsii_type="@cloudcomponents/cdk-chatops.AccountLabelMode")
class AccountLabelMode(enum.Enum):
    ID = "ID"
    ALIAS = "ALIAS"
    ID_AND_ALIAS = "ID_AND_ALIAS"


@jsii.interface(jsii_type="@cloudcomponents/cdk-chatops.ISlackChannelConfiguration")
class ISlackChannelConfiguration(typing_extensions.Protocol):
    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_ISlackChannelConfigurationProxy"]:
        return _ISlackChannelConfigurationProxy

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationArn")
    def configuration_arn(self) -> builtins.str:
        ...


class _ISlackChannelConfigurationProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-chatops.ISlackChannelConfiguration"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationArn")
    def configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationArn"))


@jsii.enum(jsii_type="@cloudcomponents/cdk-chatops.LoggingLevel")
class LoggingLevel(enum.Enum):
    ERROR = "ERROR"
    INFO = "INFO"
    NONE = "NONE"


class MSTeamsIncomingWebhookConfiguration(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-chatops.MSTeamsIncomingWebhookConfiguration",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        url: builtins.str,
        account_label_mode: typing.Optional[AccountLabelMode] = None,
        notification_topics: typing.Optional[typing.Sequence[aws_cdk.aws_sns.ITopic]] = None,
        theme_color: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param url: The url of the incoming webhook for a channel.
        :param account_label_mode: Default: ACCOUNT_LABEL_MODE.ID_AND_ALIAS
        :param notification_topics: The SNS topics that deliver notifications to MS Teams.
        :param theme_color: Specifies a custom brand color for the card. The color will be displayed in a non-obtrusive manner. Default: ``#CEDB56``
        '''
        props = MSTeamsIncomingWebhookConfigurationProps(
            url=url,
            account_label_mode=account_label_mode,
            notification_topics=notification_topics,
            theme_color=theme_color,
        )

        jsii.create(MSTeamsIncomingWebhookConfiguration, self, [scope, id, props])

    @jsii.member(jsii_name="addEventSource")
    def add_event_source(
        self,
        sns_event_source: aws_cdk.aws_lambda_event_sources.SnsEventSource,
    ) -> None:
        '''
        :param sns_event_source: -
        '''
        return typing.cast(None, jsii.invoke(self, "addEventSource", [sns_event_source]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="incomingWebhook")
    def incoming_webhook(self) -> aws_cdk.aws_lambda.IFunction:
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "incomingWebhook"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-chatops.MSTeamsIncomingWebhookConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "url": "url",
        "account_label_mode": "accountLabelMode",
        "notification_topics": "notificationTopics",
        "theme_color": "themeColor",
    },
)
class MSTeamsIncomingWebhookConfigurationProps:
    def __init__(
        self,
        *,
        url: builtins.str,
        account_label_mode: typing.Optional[AccountLabelMode] = None,
        notification_topics: typing.Optional[typing.Sequence[aws_cdk.aws_sns.ITopic]] = None,
        theme_color: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param url: The url of the incoming webhook for a channel.
        :param account_label_mode: Default: ACCOUNT_LABEL_MODE.ID_AND_ALIAS
        :param notification_topics: The SNS topics that deliver notifications to MS Teams.
        :param theme_color: Specifies a custom brand color for the card. The color will be displayed in a non-obtrusive manner. Default: ``#CEDB56``
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }
        if account_label_mode is not None:
            self._values["account_label_mode"] = account_label_mode
        if notification_topics is not None:
            self._values["notification_topics"] = notification_topics
        if theme_color is not None:
            self._values["theme_color"] = theme_color

    @builtins.property
    def url(self) -> builtins.str:
        '''The url of the incoming webhook for a channel.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_label_mode(self) -> typing.Optional[AccountLabelMode]:
        '''
        :default: ACCOUNT_LABEL_MODE.ID_AND_ALIAS
        '''
        result = self._values.get("account_label_mode")
        return typing.cast(typing.Optional[AccountLabelMode], result)

    @builtins.property
    def notification_topics(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_sns.ITopic]]:
        '''The SNS topics that deliver notifications to MS Teams.'''
        result = self._values.get("notification_topics")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_sns.ITopic]], result)

    @builtins.property
    def theme_color(self) -> typing.Optional[builtins.str]:
        '''Specifies a custom brand color for the card.

        The color will be displayed in a non-obtrusive manner.

        :default: ``#CEDB56``
        '''
        result = self._values.get("theme_color")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MSTeamsIncomingWebhookConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackChannelConfiguration(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-chatops.SlackChannelConfiguration",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        configuration_name: builtins.str,
        slack_channel_id: builtins.str,
        slack_workspace_id: builtins.str,
        logging_level: typing.Optional[LoggingLevel] = None,
        notification_topics: typing.Optional[typing.Sequence[aws_cdk.aws_sns.ITopic]] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param configuration_name: The name of the configuration.
        :param slack_channel_id: The ID of the Slack channel. To get the ID, open Slack, right click on the channel name in the left pane, then choose Copy Link. The channel ID is the 9-character string at the end of the URL. For example, ABCBBLZZZ.
        :param slack_workspace_id: The ID of the Slack workspace authorized with AWS Chatbot. To get the workspace ID, you must perform the initial authorization flow with Slack in the AWS Chatbot console. Then you can copy and paste the workspace ID from the console. For more details, see steps 1-4 in Setting Up AWS Chatbot with Slack in the AWS Chatbot User Guide.
        :param logging_level: Specifies the logging level for this configuration. This property affects the log entries pushed to Amazon CloudWatch Logs. Logging levels include ERROR, INFO, or NONE. Default: NONE
        :param notification_topics: The SNS topics that deliver notifications to AWS Chatbot.
        :param role: The iam role that defines the permissions for AWS Chatbot. This is a user-defined role that AWS Chatbot will assume. This is not the service-linked role. For more information, see IAM Policies for AWS Chatbot.
        '''
        props = SlackChannelConfigurationProps(
            configuration_name=configuration_name,
            slack_channel_id=slack_channel_id,
            slack_workspace_id=slack_workspace_id,
            logging_level=logging_level,
            notification_topics=notification_topics,
            role=role,
        )

        jsii.create(SlackChannelConfiguration, self, [scope, id, props])

    @jsii.member(jsii_name="addLambdaInvokeCommandPermissions")
    def add_lambda_invoke_command_permissions(
        self,
        lambda_: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
    ) -> None:
        '''Allows Lambda-invoke commands in supported clients.

        :param lambda_: -
        '''
        return typing.cast(None, jsii.invoke(self, "addLambdaInvokeCommandPermissions", [lambda_]))

    @jsii.member(jsii_name="addNotificationPermissions")
    def add_notification_permissions(self) -> None:
        '''Allows AWS Chatbot to retreive metric graphs from Amazon Cloudwatch.'''
        return typing.cast(None, jsii.invoke(self, "addNotificationPermissions", []))

    @jsii.member(jsii_name="addReadOnlyCommandPermissions")
    def add_read_only_command_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "addReadOnlyCommandPermissions", []))

    @jsii.member(jsii_name="addSupportCommandPermissions")
    def add_support_command_permissions(self) -> None:
        '''Allows calling AWS Support APIs in supportzed clients.'''
        return typing.cast(None, jsii.invoke(self, "addSupportCommandPermissions", []))

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        '''Adds a statement to the IAM role assumed by the instance.

        :param statement: -
        '''
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationArn")
    def configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-chatops.SlackChannelConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "configuration_name": "configurationName",
        "slack_channel_id": "slackChannelId",
        "slack_workspace_id": "slackWorkspaceId",
        "logging_level": "loggingLevel",
        "notification_topics": "notificationTopics",
        "role": "role",
    },
)
class SlackChannelConfigurationProps:
    def __init__(
        self,
        *,
        configuration_name: builtins.str,
        slack_channel_id: builtins.str,
        slack_workspace_id: builtins.str,
        logging_level: typing.Optional[LoggingLevel] = None,
        notification_topics: typing.Optional[typing.Sequence[aws_cdk.aws_sns.ITopic]] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param configuration_name: The name of the configuration.
        :param slack_channel_id: The ID of the Slack channel. To get the ID, open Slack, right click on the channel name in the left pane, then choose Copy Link. The channel ID is the 9-character string at the end of the URL. For example, ABCBBLZZZ.
        :param slack_workspace_id: The ID of the Slack workspace authorized with AWS Chatbot. To get the workspace ID, you must perform the initial authorization flow with Slack in the AWS Chatbot console. Then you can copy and paste the workspace ID from the console. For more details, see steps 1-4 in Setting Up AWS Chatbot with Slack in the AWS Chatbot User Guide.
        :param logging_level: Specifies the logging level for this configuration. This property affects the log entries pushed to Amazon CloudWatch Logs. Logging levels include ERROR, INFO, or NONE. Default: NONE
        :param notification_topics: The SNS topics that deliver notifications to AWS Chatbot.
        :param role: The iam role that defines the permissions for AWS Chatbot. This is a user-defined role that AWS Chatbot will assume. This is not the service-linked role. For more information, see IAM Policies for AWS Chatbot.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "configuration_name": configuration_name,
            "slack_channel_id": slack_channel_id,
            "slack_workspace_id": slack_workspace_id,
        }
        if logging_level is not None:
            self._values["logging_level"] = logging_level
        if notification_topics is not None:
            self._values["notification_topics"] = notification_topics
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def configuration_name(self) -> builtins.str:
        '''The name of the configuration.'''
        result = self._values.get("configuration_name")
        assert result is not None, "Required property 'configuration_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def slack_channel_id(self) -> builtins.str:
        '''The ID of the Slack channel.

        To get the ID, open Slack, right click on the channel name
        in the left pane, then choose Copy Link. The channel ID is
        the 9-character string at the end of the URL.
        For example, ABCBBLZZZ.
        '''
        result = self._values.get("slack_channel_id")
        assert result is not None, "Required property 'slack_channel_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def slack_workspace_id(self) -> builtins.str:
        '''The ID of the Slack workspace authorized with AWS Chatbot.

        To get the workspace ID, you must perform the initial authorization
        flow with Slack in the AWS Chatbot console. Then you can copy and
        paste the workspace ID from the console. For more details, see steps
        1-4 in Setting Up AWS Chatbot with Slack in the AWS Chatbot User Guide.
        '''
        result = self._values.get("slack_workspace_id")
        assert result is not None, "Required property 'slack_workspace_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging_level(self) -> typing.Optional[LoggingLevel]:
        '''Specifies the logging level for this configuration. This property affects the log entries pushed to Amazon CloudWatch Logs.

        Logging levels include ERROR, INFO, or NONE.

        :default: NONE
        '''
        result = self._values.get("logging_level")
        return typing.cast(typing.Optional[LoggingLevel], result)

    @builtins.property
    def notification_topics(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_sns.ITopic]]:
        '''The SNS topics that deliver notifications to AWS Chatbot.'''
        result = self._values.get("notification_topics")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_sns.ITopic]], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The iam role that defines the permissions for AWS Chatbot.

        This is a user-defined role that AWS Chatbot will assume. This is
        not the service-linked role. For more information, see IAM Policies
        for AWS Chatbot.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackChannelConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccountLabelMode",
    "ISlackChannelConfiguration",
    "LoggingLevel",
    "MSTeamsIncomingWebhookConfiguration",
    "MSTeamsIncomingWebhookConfigurationProps",
    "SlackChannelConfiguration",
    "SlackChannelConfigurationProps",
]

publication.publish()
