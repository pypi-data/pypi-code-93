'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-pull-request-check

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-pull-request-check)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-pull-request-check/)
[![Mentioned in Awesome CDK](https://awesome.re/mentioned-badge.svg)](https://github.com/kolomied/awesome-cdk)

> Cdk component that automatically check pull requests

## Install

TypeScript/JavaScript:

```bash
npm install --save @cloudcomponents/cdk-pull-request-check
```

Python:

```bash
pip install cloudcomponents.cdk-pull-request-check
```

## How to use

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import Construct, Stack, StackProps
from aws_cdk.aws_codecommit import Repository
from aws_cdk.aws_codebuild import BuildSpec
from cloudcomponents.cdk_pull_request_check import PullRequestCheck

class CodePipelineStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        repository = Repository(self, "Repository",
            repository_name="MyRepositoryName"
        )

        # CodePipeline etc.

        PullRequestCheck(self, "PullRequestCheck",
            repository=repository,
            build_spec=BuildSpec.from_source_filename("prcheck.yml")
        )
```

## Approval Template Rules

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import Construct, Stack, StackProps
from aws_cdk.aws_codecommit import Repository
from aws_cdk.aws_codebuild import BuildSpec
from cloudcomponents.cdk_pull_request_check import PullRequestCheck
from cloudcomponents.cdk_pull_request_approval_rule import ApprovalRuleTemplate, ApprovalRuleTemplateRepositoryAssociation

class CodePipelinePullRequestCheckStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        repository = Repository(self, "Repository",
            repository_name="repository"
        )

        { approvalRuleTemplateName } = ApprovalRuleTemplate(self, "ApprovalRuleTemplate",
            approval_rule_template_name="Require 1 approver",
            template=Template(
                approvers=Approvers(
                    number_of_approvals_needed=1
                )
            )
        )

        ApprovalRuleTemplateRepositoryAssociation(self, "ApprovalRuleTemplateRepositoryAssociation",
            approval_rule_template_name=approval_rule_template_name,
            repository=repository
        )

        # Approves the pull request
        PullRequestCheck(self, "PullRequestCheck",
            repository=repository,
            build_spec=BuildSpec.from_source_filename("prcheck.yml")
        )
```

## Custom notifications

The component comments the pull request and sets the approval state by default. Custom notifications can be set up this way

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import Construct, Stack, StackProps
from aws_cdk.aws_codecommit import Repository
from aws_cdk.aws_codebuild import BuildSpec
from aws_cdk.aws_events_targets import SnsTopic
from aws_cdk.aws_sns import Topic
from aws_cdk.aws_sns_subscriptions import EmailSubscription
from cloudcomponents.cdk_pull_request_check import PullRequestCheck

class CodePipelineStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        repository = Repository(self, "Repository",
            repository_name="MyRepositoryName",
            description="Some description."
        )

        # Your CodePipeline...

        pr_check = PullRequestCheck(self, "PullRequestCheck",
            repository=repository,
            build_spec=BuildSpec.from_source_filename("buildspecs/prcheck.yml")
        )

        pr_topic = Topic(self, "PullRequestTopic")

        pr_topic.add_subscription(
            EmailSubscription(process.env.DEVSECOPS_TEAM_EMAIL))

        pr_check.on_check_started("started",
            target=SnsTopic(pr_topic)
        )

        pr_check.on_check_succeeded("succeeded",
            target=SnsTopic(pr_topic)
        )

        pr_check.on_check_failed("failed",
            target=SnsTopic(pr_topic)
        )
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-pull-request-check/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-pull-request-check/LICENSE)
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
import aws_cdk.aws_ec2
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.core


class PullRequestCheck(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-pull-request-check.PullRequestCheck",
):
    '''Represents a reference to a PullRequestCheck.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        build_spec: aws_cdk.aws_codebuild.BuildSpec,
        repository: aws_cdk.aws_codecommit.IRepository,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        build_image: typing.Optional[aws_cdk.aws_codebuild.IBuildImage] = None,
        compute_type: typing.Optional[aws_cdk.aws_codebuild.ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_codebuild.BuildEnvironmentVariable]] = None,
        post_comment: typing.Optional[builtins.bool] = None,
        privileged: typing.Optional[builtins.bool] = None,
        project_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        update_approval_state: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param build_spec: Filename or contents of buildspec in JSON format.
        :param repository: The CodeCommit repository.
        :param allow_all_outbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
        :param build_image: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_2_0
        :param compute_type: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
        :param environment_variables: The environment variables that your builds can use.
        :param post_comment: Specifies whether comments should be written in the request. Default: true
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false
        :param project_name: The human-visible name of this PullRequest-Project. - @default taken from {@link #repository:#repositoryName}-pull-request
        :param role: The IAM service Role of the Project.
        :param security_groups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: Security group will be automatically created
        :param subnet_selection: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Default: All private subnets
        :param update_approval_state: Indicates whether the approval state [APPROVE, REVOKE] should be updated. Default: true
        :param vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: No VPC is specified
        '''
        props = PullRequestCheckProps(
            build_spec=build_spec,
            repository=repository,
            allow_all_outbound=allow_all_outbound,
            build_image=build_image,
            compute_type=compute_type,
            environment_variables=environment_variables,
            post_comment=post_comment,
            privileged=privileged,
            project_name=project_name,
            role=role,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            update_approval_state=update_approval_state,
            vpc=vpc,
        )

        jsii.create(PullRequestCheck, self, [scope, id, props])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        '''Add a permission only if there's a policy attached.

        :param statement: The permissions statement to add.
        '''
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="onCheckFailed")
    def on_check_failed(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        '''Defines an event rule which triggers when a check fails.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(aws_cdk.aws_events.Rule, jsii.invoke(self, "onCheckFailed", [id, options]))

    @jsii.member(jsii_name="onCheckStarted")
    def on_check_started(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        '''Defines an event rule which triggers when a check starts.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(aws_cdk.aws_events.Rule, jsii.invoke(self, "onCheckStarted", [id, options]))

    @jsii.member(jsii_name="onCheckSucceeded")
    def on_check_succeeded(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        '''Defines an event rule which triggers when a check complets successfully.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(aws_cdk.aws_events.Rule, jsii.invoke(self, "onCheckSucceeded", [id, options]))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-pull-request-check.PullRequestCheckProps",
    jsii_struct_bases=[],
    name_mapping={
        "build_spec": "buildSpec",
        "repository": "repository",
        "allow_all_outbound": "allowAllOutbound",
        "build_image": "buildImage",
        "compute_type": "computeType",
        "environment_variables": "environmentVariables",
        "post_comment": "postComment",
        "privileged": "privileged",
        "project_name": "projectName",
        "role": "role",
        "security_groups": "securityGroups",
        "subnet_selection": "subnetSelection",
        "update_approval_state": "updateApprovalState",
        "vpc": "vpc",
    },
)
class PullRequestCheckProps:
    def __init__(
        self,
        *,
        build_spec: aws_cdk.aws_codebuild.BuildSpec,
        repository: aws_cdk.aws_codecommit.IRepository,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        build_image: typing.Optional[aws_cdk.aws_codebuild.IBuildImage] = None,
        compute_type: typing.Optional[aws_cdk.aws_codebuild.ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_codebuild.BuildEnvironmentVariable]] = None,
        post_comment: typing.Optional[builtins.bool] = None,
        privileged: typing.Optional[builtins.bool] = None,
        project_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        update_approval_state: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param build_spec: Filename or contents of buildspec in JSON format.
        :param repository: The CodeCommit repository.
        :param allow_all_outbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
        :param build_image: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_2_0
        :param compute_type: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
        :param environment_variables: The environment variables that your builds can use.
        :param post_comment: Specifies whether comments should be written in the request. Default: true
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false
        :param project_name: The human-visible name of this PullRequest-Project. - @default taken from {@link #repository:#repositoryName}-pull-request
        :param role: The IAM service Role of the Project.
        :param security_groups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: Security group will be automatically created
        :param subnet_selection: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Default: All private subnets
        :param update_approval_state: Indicates whether the approval state [APPROVE, REVOKE] should be updated. Default: true
        :param vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: No VPC is specified
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = aws_cdk.aws_ec2.SubnetSelection(**subnet_selection)
        self._values: typing.Dict[str, typing.Any] = {
            "build_spec": build_spec,
            "repository": repository,
        }
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if build_image is not None:
            self._values["build_image"] = build_image
        if compute_type is not None:
            self._values["compute_type"] = compute_type
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if post_comment is not None:
            self._values["post_comment"] = post_comment
        if privileged is not None:
            self._values["privileged"] = privileged
        if project_name is not None:
            self._values["project_name"] = project_name
        if role is not None:
            self._values["role"] = role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if update_approval_state is not None:
            self._values["update_approval_state"] = update_approval_state
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def build_spec(self) -> aws_cdk.aws_codebuild.BuildSpec:
        '''Filename or contents of buildspec in JSON format.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-example
        '''
        result = self._values.get("build_spec")
        assert result is not None, "Required property 'build_spec' is missing"
        return typing.cast(aws_cdk.aws_codebuild.BuildSpec, result)

    @builtins.property
    def repository(self) -> aws_cdk.aws_codecommit.IRepository:
        '''The CodeCommit repository.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(aws_cdk.aws_codecommit.IRepository, result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the CodeBuild to send all network traffic.

        If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets.
        Only used if 'vpc' is supplied.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_image(self) -> typing.Optional[aws_cdk.aws_codebuild.IBuildImage]:
        '''Build environment to use for the build.

        :default: BuildEnvironment.LinuxBuildImage.STANDARD_2_0
        '''
        result = self._values.get("build_image")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.IBuildImage], result)

    @builtins.property
    def compute_type(self) -> typing.Optional[aws_cdk.aws_codebuild.ComputeType]:
        '''The type of compute to use for this build.

        See the {@link ComputeType} enum for the possible values.

        :default: taken from {@link #buildImage#defaultComputeType}
        '''
        result = self._values.get("compute_type")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.ComputeType], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_codebuild.BuildEnvironmentVariable]]:
        '''The environment variables that your builds can use.'''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_codebuild.BuildEnvironmentVariable]], result)

    @builtins.property
    def post_comment(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether comments should be written in the request.

        :default: true
        '''
        result = self._values.get("post_comment")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def privileged(self) -> typing.Optional[builtins.bool]:
        '''Indicates how the project builds Docker images.

        Specify true to enable
        running the Docker daemon inside a Docker container. This value must be
        set to true only if this build project will be used to build Docker
        images, and the specified build environment image is not one provided by
        AWS CodeBuild with Docker support. Otherwise, all associated builds that
        attempt to interact with the Docker daemon will fail.

        :default: false
        '''
        result = self._values.get("privileged")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def project_name(self) -> typing.Optional[builtins.str]:
        '''The human-visible name of this PullRequest-Project.

        - @default taken from {@link #repository:#repositoryName}-pull-request
        '''
        result = self._values.get("project_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The IAM service Role of the Project.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        '''What security group to associate with the codebuild project's network interfaces.

        If no security group is identified, one will be created automatically.
        Only used if 'vpc' is supplied.

        :default: Security group will be automatically created
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def subnet_selection(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.

        Only used if 'vpc' is supplied.

        :default: All private subnets
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def update_approval_state(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the approval state [APPROVE, REVOKE] should be updated.

        :default: true
        '''
        result = self._values.get("update_approval_state")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC network to place codebuild network interfaces.

        Specify this if the codebuild project needs to access resources in a VPC.

        :default: No VPC is specified
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PullRequestCheckProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PullRequestCheck",
    "PullRequestCheckProps",
]

publication.publish()
