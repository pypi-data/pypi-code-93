import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from .. import (
    CfnResource as _CfnResource_9df397a6,
    CfnTag as _CfnTag_f6864754,
    IInspectable as _IInspectable_c2943556,
    IResolvable as _IResolvable_da3f097b,
    TagManager as _TagManager_0a598cb3,
    TreeInspector as _TreeInspector_488e0dd5,
)


@jsii.implements(_IInspectable_c2943556)
class CfnApp(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_amplify.CfnApp",
):
    '''A CloudFormation ``AWS::Amplify::App``.

    :cloudformationResource: AWS::Amplify::App
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        access_token: typing.Optional[builtins.str] = None,
        auto_branch_creation_config: typing.Optional[typing.Union["CfnApp.AutoBranchCreationConfigProperty", _IResolvable_da3f097b]] = None,
        basic_auth_config: typing.Optional[typing.Union["CfnApp.BasicAuthConfigProperty", _IResolvable_da3f097b]] = None,
        build_spec: typing.Optional[builtins.str] = None,
        custom_headers: typing.Optional[builtins.str] = None,
        custom_rules: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnApp.CustomRuleProperty", _IResolvable_da3f097b]]]] = None,
        description: typing.Optional[builtins.str] = None,
        enable_branch_auto_deletion: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        environment_variables: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnApp.EnvironmentVariableProperty", _IResolvable_da3f097b]]]] = None,
        iam_service_role: typing.Optional[builtins.str] = None,
        oauth_token: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::Amplify::App``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param name: ``AWS::Amplify::App.Name``.
        :param access_token: ``AWS::Amplify::App.AccessToken``.
        :param auto_branch_creation_config: ``AWS::Amplify::App.AutoBranchCreationConfig``.
        :param basic_auth_config: ``AWS::Amplify::App.BasicAuthConfig``.
        :param build_spec: ``AWS::Amplify::App.BuildSpec``.
        :param custom_headers: ``AWS::Amplify::App.CustomHeaders``.
        :param custom_rules: ``AWS::Amplify::App.CustomRules``.
        :param description: ``AWS::Amplify::App.Description``.
        :param enable_branch_auto_deletion: ``AWS::Amplify::App.EnableBranchAutoDeletion``.
        :param environment_variables: ``AWS::Amplify::App.EnvironmentVariables``.
        :param iam_service_role: ``AWS::Amplify::App.IAMServiceRole``.
        :param oauth_token: ``AWS::Amplify::App.OauthToken``.
        :param repository: ``AWS::Amplify::App.Repository``.
        :param tags: ``AWS::Amplify::App.Tags``.
        '''
        props = CfnAppProps(
            name=name,
            access_token=access_token,
            auto_branch_creation_config=auto_branch_creation_config,
            basic_auth_config=basic_auth_config,
            build_spec=build_spec,
            custom_headers=custom_headers,
            custom_rules=custom_rules,
            description=description,
            enable_branch_auto_deletion=enable_branch_auto_deletion,
            environment_variables=environment_variables,
            iam_service_role=iam_service_role,
            oauth_token=oauth_token,
            repository=repository,
            tags=tags,
        )

        jsii.create(CfnApp, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrAppId")
    def attr_app_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: AppId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrAppId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrAppName")
    def attr_app_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: AppName
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrAppName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrDefaultDomain")
    def attr_default_domain(self) -> builtins.str:
        '''
        :cloudformationAttribute: DefaultDomain
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrDefaultDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Amplify::App.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Amplify::App.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.AccessToken``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-accesstoken
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessToken"))

    @access_token.setter
    def access_token(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "accessToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoBranchCreationConfig")
    def auto_branch_creation_config(
        self,
    ) -> typing.Optional[typing.Union["CfnApp.AutoBranchCreationConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::Amplify::App.AutoBranchCreationConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-autobranchcreationconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnApp.AutoBranchCreationConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "autoBranchCreationConfig"))

    @auto_branch_creation_config.setter
    def auto_branch_creation_config(
        self,
        value: typing.Optional[typing.Union["CfnApp.AutoBranchCreationConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "autoBranchCreationConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basicAuthConfig")
    def basic_auth_config(
        self,
    ) -> typing.Optional[typing.Union["CfnApp.BasicAuthConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::Amplify::App.BasicAuthConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-basicauthconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnApp.BasicAuthConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "basicAuthConfig"))

    @basic_auth_config.setter
    def basic_auth_config(
        self,
        value: typing.Optional[typing.Union["CfnApp.BasicAuthConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "basicAuthConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildSpec")
    def build_spec(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.BuildSpec``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-buildspec
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buildSpec"))

    @build_spec.setter
    def build_spec(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "buildSpec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customHeaders")
    def custom_headers(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.CustomHeaders``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-customheaders
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customHeaders"))

    @custom_headers.setter
    def custom_headers(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "customHeaders", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customRules")
    def custom_rules(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnApp.CustomRuleProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::Amplify::App.CustomRules``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-customrules
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnApp.CustomRuleProperty", _IResolvable_da3f097b]]]], jsii.get(self, "customRules"))

    @custom_rules.setter
    def custom_rules(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnApp.CustomRuleProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "customRules", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBranchAutoDeletion")
    def enable_branch_auto_deletion(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::App.EnableBranchAutoDeletion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-enablebranchautodeletion
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enableBranchAutoDeletion"))

    @enable_branch_auto_deletion.setter
    def enable_branch_auto_deletion(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enableBranchAutoDeletion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentVariables")
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnApp.EnvironmentVariableProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::Amplify::App.EnvironmentVariables``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-environmentvariables
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnApp.EnvironmentVariableProperty", _IResolvable_da3f097b]]]], jsii.get(self, "environmentVariables"))

    @environment_variables.setter
    def environment_variables(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnApp.EnvironmentVariableProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "environmentVariables", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamServiceRole")
    def iam_service_role(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.IAMServiceRole``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-iamservicerole
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamServiceRole"))

    @iam_service_role.setter
    def iam_service_role(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "iamServiceRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oauthToken")
    def oauth_token(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.OauthToken``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-oauthtoken
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oauthToken"))

    @oauth_token.setter
    def oauth_token(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "oauthToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.Repository``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-repository
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "repository", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_amplify.CfnApp.AutoBranchCreationConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "auto_branch_creation_patterns": "autoBranchCreationPatterns",
            "basic_auth_config": "basicAuthConfig",
            "build_spec": "buildSpec",
            "enable_auto_branch_creation": "enableAutoBranchCreation",
            "enable_auto_build": "enableAutoBuild",
            "enable_performance_mode": "enablePerformanceMode",
            "enable_pull_request_preview": "enablePullRequestPreview",
            "environment_variables": "environmentVariables",
            "pull_request_environment_name": "pullRequestEnvironmentName",
            "stage": "stage",
        },
    )
    class AutoBranchCreationConfigProperty:
        def __init__(
            self,
            *,
            auto_branch_creation_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
            basic_auth_config: typing.Optional[typing.Union["CfnApp.BasicAuthConfigProperty", _IResolvable_da3f097b]] = None,
            build_spec: typing.Optional[builtins.str] = None,
            enable_auto_branch_creation: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            enable_auto_build: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            enable_performance_mode: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            enable_pull_request_preview: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            environment_variables: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnApp.EnvironmentVariableProperty", _IResolvable_da3f097b]]]] = None,
            pull_request_environment_name: typing.Optional[builtins.str] = None,
            stage: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param auto_branch_creation_patterns: ``CfnApp.AutoBranchCreationConfigProperty.AutoBranchCreationPatterns``.
            :param basic_auth_config: ``CfnApp.AutoBranchCreationConfigProperty.BasicAuthConfig``.
            :param build_spec: ``CfnApp.AutoBranchCreationConfigProperty.BuildSpec``.
            :param enable_auto_branch_creation: ``CfnApp.AutoBranchCreationConfigProperty.EnableAutoBranchCreation``.
            :param enable_auto_build: ``CfnApp.AutoBranchCreationConfigProperty.EnableAutoBuild``.
            :param enable_performance_mode: ``CfnApp.AutoBranchCreationConfigProperty.EnablePerformanceMode``.
            :param enable_pull_request_preview: ``CfnApp.AutoBranchCreationConfigProperty.EnablePullRequestPreview``.
            :param environment_variables: ``CfnApp.AutoBranchCreationConfigProperty.EnvironmentVariables``.
            :param pull_request_environment_name: ``CfnApp.AutoBranchCreationConfigProperty.PullRequestEnvironmentName``.
            :param stage: ``CfnApp.AutoBranchCreationConfigProperty.Stage``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if auto_branch_creation_patterns is not None:
                self._values["auto_branch_creation_patterns"] = auto_branch_creation_patterns
            if basic_auth_config is not None:
                self._values["basic_auth_config"] = basic_auth_config
            if build_spec is not None:
                self._values["build_spec"] = build_spec
            if enable_auto_branch_creation is not None:
                self._values["enable_auto_branch_creation"] = enable_auto_branch_creation
            if enable_auto_build is not None:
                self._values["enable_auto_build"] = enable_auto_build
            if enable_performance_mode is not None:
                self._values["enable_performance_mode"] = enable_performance_mode
            if enable_pull_request_preview is not None:
                self._values["enable_pull_request_preview"] = enable_pull_request_preview
            if environment_variables is not None:
                self._values["environment_variables"] = environment_variables
            if pull_request_environment_name is not None:
                self._values["pull_request_environment_name"] = pull_request_environment_name
            if stage is not None:
                self._values["stage"] = stage

        @builtins.property
        def auto_branch_creation_patterns(
            self,
        ) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnApp.AutoBranchCreationConfigProperty.AutoBranchCreationPatterns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-autobranchcreationpatterns
            '''
            result = self._values.get("auto_branch_creation_patterns")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def basic_auth_config(
            self,
        ) -> typing.Optional[typing.Union["CfnApp.BasicAuthConfigProperty", _IResolvable_da3f097b]]:
            '''``CfnApp.AutoBranchCreationConfigProperty.BasicAuthConfig``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-basicauthconfig
            '''
            result = self._values.get("basic_auth_config")
            return typing.cast(typing.Optional[typing.Union["CfnApp.BasicAuthConfigProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def build_spec(self) -> typing.Optional[builtins.str]:
            '''``CfnApp.AutoBranchCreationConfigProperty.BuildSpec``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-buildspec
            '''
            result = self._values.get("build_spec")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def enable_auto_branch_creation(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnApp.AutoBranchCreationConfigProperty.EnableAutoBranchCreation``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-enableautobranchcreation
            '''
            result = self._values.get("enable_auto_branch_creation")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def enable_auto_build(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnApp.AutoBranchCreationConfigProperty.EnableAutoBuild``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-enableautobuild
            '''
            result = self._values.get("enable_auto_build")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def enable_performance_mode(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnApp.AutoBranchCreationConfigProperty.EnablePerformanceMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-enableperformancemode
            '''
            result = self._values.get("enable_performance_mode")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def enable_pull_request_preview(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnApp.AutoBranchCreationConfigProperty.EnablePullRequestPreview``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-enablepullrequestpreview
            '''
            result = self._values.get("enable_pull_request_preview")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def environment_variables(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnApp.EnvironmentVariableProperty", _IResolvable_da3f097b]]]]:
            '''``CfnApp.AutoBranchCreationConfigProperty.EnvironmentVariables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-environmentvariables
            '''
            result = self._values.get("environment_variables")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnApp.EnvironmentVariableProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def pull_request_environment_name(self) -> typing.Optional[builtins.str]:
            '''``CfnApp.AutoBranchCreationConfigProperty.PullRequestEnvironmentName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-pullrequestenvironmentname
            '''
            result = self._values.get("pull_request_environment_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def stage(self) -> typing.Optional[builtins.str]:
            '''``CfnApp.AutoBranchCreationConfigProperty.Stage``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-autobranchcreationconfig.html#cfn-amplify-app-autobranchcreationconfig-stage
            '''
            result = self._values.get("stage")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AutoBranchCreationConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_amplify.CfnApp.BasicAuthConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "enable_basic_auth": "enableBasicAuth",
            "password": "password",
            "username": "username",
        },
    )
    class BasicAuthConfigProperty:
        def __init__(
            self,
            *,
            enable_basic_auth: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            password: typing.Optional[builtins.str] = None,
            username: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param enable_basic_auth: ``CfnApp.BasicAuthConfigProperty.EnableBasicAuth``.
            :param password: ``CfnApp.BasicAuthConfigProperty.Password``.
            :param username: ``CfnApp.BasicAuthConfigProperty.Username``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-basicauthconfig.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if enable_basic_auth is not None:
                self._values["enable_basic_auth"] = enable_basic_auth
            if password is not None:
                self._values["password"] = password
            if username is not None:
                self._values["username"] = username

        @builtins.property
        def enable_basic_auth(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnApp.BasicAuthConfigProperty.EnableBasicAuth``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-basicauthconfig.html#cfn-amplify-app-basicauthconfig-enablebasicauth
            '''
            result = self._values.get("enable_basic_auth")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def password(self) -> typing.Optional[builtins.str]:
            '''``CfnApp.BasicAuthConfigProperty.Password``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-basicauthconfig.html#cfn-amplify-app-basicauthconfig-password
            '''
            result = self._values.get("password")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def username(self) -> typing.Optional[builtins.str]:
            '''``CfnApp.BasicAuthConfigProperty.Username``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-basicauthconfig.html#cfn-amplify-app-basicauthconfig-username
            '''
            result = self._values.get("username")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BasicAuthConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_amplify.CfnApp.CustomRuleProperty",
        jsii_struct_bases=[],
        name_mapping={
            "source": "source",
            "target": "target",
            "condition": "condition",
            "status": "status",
        },
    )
    class CustomRuleProperty:
        def __init__(
            self,
            *,
            source: builtins.str,
            target: builtins.str,
            condition: typing.Optional[builtins.str] = None,
            status: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param source: ``CfnApp.CustomRuleProperty.Source``.
            :param target: ``CfnApp.CustomRuleProperty.Target``.
            :param condition: ``CfnApp.CustomRuleProperty.Condition``.
            :param status: ``CfnApp.CustomRuleProperty.Status``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "source": source,
                "target": target,
            }
            if condition is not None:
                self._values["condition"] = condition
            if status is not None:
                self._values["status"] = status

        @builtins.property
        def source(self) -> builtins.str:
            '''``CfnApp.CustomRuleProperty.Source``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html#cfn-amplify-app-customrule-source
            '''
            result = self._values.get("source")
            assert result is not None, "Required property 'source' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def target(self) -> builtins.str:
            '''``CfnApp.CustomRuleProperty.Target``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html#cfn-amplify-app-customrule-target
            '''
            result = self._values.get("target")
            assert result is not None, "Required property 'target' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def condition(self) -> typing.Optional[builtins.str]:
            '''``CfnApp.CustomRuleProperty.Condition``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html#cfn-amplify-app-customrule-condition
            '''
            result = self._values.get("condition")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def status(self) -> typing.Optional[builtins.str]:
            '''``CfnApp.CustomRuleProperty.Status``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html#cfn-amplify-app-customrule-status
            '''
            result = self._values.get("status")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CustomRuleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_amplify.CfnApp.EnvironmentVariableProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "value": "value"},
    )
    class EnvironmentVariableProperty:
        def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
            '''
            :param name: ``CfnApp.EnvironmentVariableProperty.Name``.
            :param value: ``CfnApp.EnvironmentVariableProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-environmentvariable.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
                "value": value,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnApp.EnvironmentVariableProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-environmentvariable.html#cfn-amplify-app-environmentvariable-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value(self) -> builtins.str:
            '''``CfnApp.EnvironmentVariableProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-environmentvariable.html#cfn-amplify-app-environmentvariable-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EnvironmentVariableProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_amplify.CfnAppProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "access_token": "accessToken",
        "auto_branch_creation_config": "autoBranchCreationConfig",
        "basic_auth_config": "basicAuthConfig",
        "build_spec": "buildSpec",
        "custom_headers": "customHeaders",
        "custom_rules": "customRules",
        "description": "description",
        "enable_branch_auto_deletion": "enableBranchAutoDeletion",
        "environment_variables": "environmentVariables",
        "iam_service_role": "iamServiceRole",
        "oauth_token": "oauthToken",
        "repository": "repository",
        "tags": "tags",
    },
)
class CfnAppProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        access_token: typing.Optional[builtins.str] = None,
        auto_branch_creation_config: typing.Optional[typing.Union[CfnApp.AutoBranchCreationConfigProperty, _IResolvable_da3f097b]] = None,
        basic_auth_config: typing.Optional[typing.Union[CfnApp.BasicAuthConfigProperty, _IResolvable_da3f097b]] = None,
        build_spec: typing.Optional[builtins.str] = None,
        custom_headers: typing.Optional[builtins.str] = None,
        custom_rules: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnApp.CustomRuleProperty, _IResolvable_da3f097b]]]] = None,
        description: typing.Optional[builtins.str] = None,
        enable_branch_auto_deletion: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        environment_variables: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnApp.EnvironmentVariableProperty, _IResolvable_da3f097b]]]] = None,
        iam_service_role: typing.Optional[builtins.str] = None,
        oauth_token: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Amplify::App``.

        :param name: ``AWS::Amplify::App.Name``.
        :param access_token: ``AWS::Amplify::App.AccessToken``.
        :param auto_branch_creation_config: ``AWS::Amplify::App.AutoBranchCreationConfig``.
        :param basic_auth_config: ``AWS::Amplify::App.BasicAuthConfig``.
        :param build_spec: ``AWS::Amplify::App.BuildSpec``.
        :param custom_headers: ``AWS::Amplify::App.CustomHeaders``.
        :param custom_rules: ``AWS::Amplify::App.CustomRules``.
        :param description: ``AWS::Amplify::App.Description``.
        :param enable_branch_auto_deletion: ``AWS::Amplify::App.EnableBranchAutoDeletion``.
        :param environment_variables: ``AWS::Amplify::App.EnvironmentVariables``.
        :param iam_service_role: ``AWS::Amplify::App.IAMServiceRole``.
        :param oauth_token: ``AWS::Amplify::App.OauthToken``.
        :param repository: ``AWS::Amplify::App.Repository``.
        :param tags: ``AWS::Amplify::App.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if access_token is not None:
            self._values["access_token"] = access_token
        if auto_branch_creation_config is not None:
            self._values["auto_branch_creation_config"] = auto_branch_creation_config
        if basic_auth_config is not None:
            self._values["basic_auth_config"] = basic_auth_config
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if custom_headers is not None:
            self._values["custom_headers"] = custom_headers
        if custom_rules is not None:
            self._values["custom_rules"] = custom_rules
        if description is not None:
            self._values["description"] = description
        if enable_branch_auto_deletion is not None:
            self._values["enable_branch_auto_deletion"] = enable_branch_auto_deletion
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if iam_service_role is not None:
            self._values["iam_service_role"] = iam_service_role
        if oauth_token is not None:
            self._values["oauth_token"] = oauth_token
        if repository is not None:
            self._values["repository"] = repository
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Amplify::App.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_token(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.AccessToken``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-accesstoken
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_branch_creation_config(
        self,
    ) -> typing.Optional[typing.Union[CfnApp.AutoBranchCreationConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::App.AutoBranchCreationConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-autobranchcreationconfig
        '''
        result = self._values.get("auto_branch_creation_config")
        return typing.cast(typing.Optional[typing.Union[CfnApp.AutoBranchCreationConfigProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def basic_auth_config(
        self,
    ) -> typing.Optional[typing.Union[CfnApp.BasicAuthConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::App.BasicAuthConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-basicauthconfig
        '''
        result = self._values.get("basic_auth_config")
        return typing.cast(typing.Optional[typing.Union[CfnApp.BasicAuthConfigProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.BuildSpec``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-buildspec
        '''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_headers(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.CustomHeaders``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-customheaders
        '''
        result = self._values.get("custom_headers")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_rules(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnApp.CustomRuleProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::Amplify::App.CustomRules``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-customrules
        '''
        result = self._values.get("custom_rules")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnApp.CustomRuleProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_branch_auto_deletion(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::App.EnableBranchAutoDeletion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-enablebranchautodeletion
        '''
        result = self._values.get("enable_branch_auto_deletion")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnApp.EnvironmentVariableProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::Amplify::App.EnvironmentVariables``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-environmentvariables
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnApp.EnvironmentVariableProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def iam_service_role(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.IAMServiceRole``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-iamservicerole
        '''
        result = self._values.get("iam_service_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oauth_token(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.OauthToken``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-oauthtoken
        '''
        result = self._values.get("oauth_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::App.Repository``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-repository
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Amplify::App.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAppProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnBranch(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_amplify.CfnBranch",
):
    '''A CloudFormation ``AWS::Amplify::Branch``.

    :cloudformationResource: AWS::Amplify::Branch
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_id: builtins.str,
        branch_name: builtins.str,
        basic_auth_config: typing.Optional[typing.Union["CfnBranch.BasicAuthConfigProperty", _IResolvable_da3f097b]] = None,
        build_spec: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enable_auto_build: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        enable_performance_mode: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        enable_pull_request_preview: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        environment_variables: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnBranch.EnvironmentVariableProperty", _IResolvable_da3f097b]]]] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        stage: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::Amplify::Branch``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param app_id: ``AWS::Amplify::Branch.AppId``.
        :param branch_name: ``AWS::Amplify::Branch.BranchName``.
        :param basic_auth_config: ``AWS::Amplify::Branch.BasicAuthConfig``.
        :param build_spec: ``AWS::Amplify::Branch.BuildSpec``.
        :param description: ``AWS::Amplify::Branch.Description``.
        :param enable_auto_build: ``AWS::Amplify::Branch.EnableAutoBuild``.
        :param enable_performance_mode: ``AWS::Amplify::Branch.EnablePerformanceMode``.
        :param enable_pull_request_preview: ``AWS::Amplify::Branch.EnablePullRequestPreview``.
        :param environment_variables: ``AWS::Amplify::Branch.EnvironmentVariables``.
        :param pull_request_environment_name: ``AWS::Amplify::Branch.PullRequestEnvironmentName``.
        :param stage: ``AWS::Amplify::Branch.Stage``.
        :param tags: ``AWS::Amplify::Branch.Tags``.
        '''
        props = CfnBranchProps(
            app_id=app_id,
            branch_name=branch_name,
            basic_auth_config=basic_auth_config,
            build_spec=build_spec,
            description=description,
            enable_auto_build=enable_auto_build,
            enable_performance_mode=enable_performance_mode,
            enable_pull_request_preview=enable_pull_request_preview,
            environment_variables=environment_variables,
            pull_request_environment_name=pull_request_environment_name,
            stage=stage,
            tags=tags,
        )

        jsii.create(CfnBranch, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrBranchName")
    def attr_branch_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: BranchName
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrBranchName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Amplify::Branch.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        '''``AWS::Amplify::Branch.AppId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-appid
        '''
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @app_id.setter
    def app_id(self, value: builtins.str) -> None:
        jsii.set(self, "appId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchName")
    def branch_name(self) -> builtins.str:
        '''``AWS::Amplify::Branch.BranchName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-branchname
        '''
        return typing.cast(builtins.str, jsii.get(self, "branchName"))

    @branch_name.setter
    def branch_name(self, value: builtins.str) -> None:
        jsii.set(self, "branchName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basicAuthConfig")
    def basic_auth_config(
        self,
    ) -> typing.Optional[typing.Union["CfnBranch.BasicAuthConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Branch.BasicAuthConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-basicauthconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnBranch.BasicAuthConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "basicAuthConfig"))

    @basic_auth_config.setter
    def basic_auth_config(
        self,
        value: typing.Optional[typing.Union["CfnBranch.BasicAuthConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "basicAuthConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildSpec")
    def build_spec(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Branch.BuildSpec``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-buildspec
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buildSpec"))

    @build_spec.setter
    def build_spec(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "buildSpec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Branch.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAutoBuild")
    def enable_auto_build(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Branch.EnableAutoBuild``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-enableautobuild
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enableAutoBuild"))

    @enable_auto_build.setter
    def enable_auto_build(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enableAutoBuild", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePerformanceMode")
    def enable_performance_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Branch.EnablePerformanceMode``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-enableperformancemode
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enablePerformanceMode"))

    @enable_performance_mode.setter
    def enable_performance_mode(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enablePerformanceMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePullRequestPreview")
    def enable_pull_request_preview(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Branch.EnablePullRequestPreview``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-enablepullrequestpreview
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enablePullRequestPreview"))

    @enable_pull_request_preview.setter
    def enable_pull_request_preview(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enablePullRequestPreview", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentVariables")
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnBranch.EnvironmentVariableProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::Amplify::Branch.EnvironmentVariables``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-environmentvariables
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnBranch.EnvironmentVariableProperty", _IResolvable_da3f097b]]]], jsii.get(self, "environmentVariables"))

    @environment_variables.setter
    def environment_variables(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnBranch.EnvironmentVariableProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "environmentVariables", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullRequestEnvironmentName")
    def pull_request_environment_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Branch.PullRequestEnvironmentName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-pullrequestenvironmentname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pullRequestEnvironmentName"))

    @pull_request_environment_name.setter
    def pull_request_environment_name(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "pullRequestEnvironmentName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stage")
    def stage(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Branch.Stage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-stage
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "stage", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_amplify.CfnBranch.BasicAuthConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "password": "password",
            "username": "username",
            "enable_basic_auth": "enableBasicAuth",
        },
    )
    class BasicAuthConfigProperty:
        def __init__(
            self,
            *,
            password: builtins.str,
            username: builtins.str,
            enable_basic_auth: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param password: ``CfnBranch.BasicAuthConfigProperty.Password``.
            :param username: ``CfnBranch.BasicAuthConfigProperty.Username``.
            :param enable_basic_auth: ``CfnBranch.BasicAuthConfigProperty.EnableBasicAuth``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-basicauthconfig.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "password": password,
                "username": username,
            }
            if enable_basic_auth is not None:
                self._values["enable_basic_auth"] = enable_basic_auth

        @builtins.property
        def password(self) -> builtins.str:
            '''``CfnBranch.BasicAuthConfigProperty.Password``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-basicauthconfig.html#cfn-amplify-branch-basicauthconfig-password
            '''
            result = self._values.get("password")
            assert result is not None, "Required property 'password' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def username(self) -> builtins.str:
            '''``CfnBranch.BasicAuthConfigProperty.Username``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-basicauthconfig.html#cfn-amplify-branch-basicauthconfig-username
            '''
            result = self._values.get("username")
            assert result is not None, "Required property 'username' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def enable_basic_auth(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnBranch.BasicAuthConfigProperty.EnableBasicAuth``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-basicauthconfig.html#cfn-amplify-branch-basicauthconfig-enablebasicauth
            '''
            result = self._values.get("enable_basic_auth")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BasicAuthConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_amplify.CfnBranch.EnvironmentVariableProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "value": "value"},
    )
    class EnvironmentVariableProperty:
        def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
            '''
            :param name: ``CfnBranch.EnvironmentVariableProperty.Name``.
            :param value: ``CfnBranch.EnvironmentVariableProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-environmentvariable.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
                "value": value,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnBranch.EnvironmentVariableProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-environmentvariable.html#cfn-amplify-branch-environmentvariable-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value(self) -> builtins.str:
            '''``CfnBranch.EnvironmentVariableProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-environmentvariable.html#cfn-amplify-branch-environmentvariable-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EnvironmentVariableProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_amplify.CfnBranchProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_id": "appId",
        "branch_name": "branchName",
        "basic_auth_config": "basicAuthConfig",
        "build_spec": "buildSpec",
        "description": "description",
        "enable_auto_build": "enableAutoBuild",
        "enable_performance_mode": "enablePerformanceMode",
        "enable_pull_request_preview": "enablePullRequestPreview",
        "environment_variables": "environmentVariables",
        "pull_request_environment_name": "pullRequestEnvironmentName",
        "stage": "stage",
        "tags": "tags",
    },
)
class CfnBranchProps:
    def __init__(
        self,
        *,
        app_id: builtins.str,
        branch_name: builtins.str,
        basic_auth_config: typing.Optional[typing.Union[CfnBranch.BasicAuthConfigProperty, _IResolvable_da3f097b]] = None,
        build_spec: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enable_auto_build: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        enable_performance_mode: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        enable_pull_request_preview: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        environment_variables: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnBranch.EnvironmentVariableProperty, _IResolvable_da3f097b]]]] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        stage: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Amplify::Branch``.

        :param app_id: ``AWS::Amplify::Branch.AppId``.
        :param branch_name: ``AWS::Amplify::Branch.BranchName``.
        :param basic_auth_config: ``AWS::Amplify::Branch.BasicAuthConfig``.
        :param build_spec: ``AWS::Amplify::Branch.BuildSpec``.
        :param description: ``AWS::Amplify::Branch.Description``.
        :param enable_auto_build: ``AWS::Amplify::Branch.EnableAutoBuild``.
        :param enable_performance_mode: ``AWS::Amplify::Branch.EnablePerformanceMode``.
        :param enable_pull_request_preview: ``AWS::Amplify::Branch.EnablePullRequestPreview``.
        :param environment_variables: ``AWS::Amplify::Branch.EnvironmentVariables``.
        :param pull_request_environment_name: ``AWS::Amplify::Branch.PullRequestEnvironmentName``.
        :param stage: ``AWS::Amplify::Branch.Stage``.
        :param tags: ``AWS::Amplify::Branch.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_id": app_id,
            "branch_name": branch_name,
        }
        if basic_auth_config is not None:
            self._values["basic_auth_config"] = basic_auth_config
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if description is not None:
            self._values["description"] = description
        if enable_auto_build is not None:
            self._values["enable_auto_build"] = enable_auto_build
        if enable_performance_mode is not None:
            self._values["enable_performance_mode"] = enable_performance_mode
        if enable_pull_request_preview is not None:
            self._values["enable_pull_request_preview"] = enable_pull_request_preview
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if pull_request_environment_name is not None:
            self._values["pull_request_environment_name"] = pull_request_environment_name
        if stage is not None:
            self._values["stage"] = stage
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def app_id(self) -> builtins.str:
        '''``AWS::Amplify::Branch.AppId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-appid
        '''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_name(self) -> builtins.str:
        '''``AWS::Amplify::Branch.BranchName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-branchname
        '''
        result = self._values.get("branch_name")
        assert result is not None, "Required property 'branch_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def basic_auth_config(
        self,
    ) -> typing.Optional[typing.Union[CfnBranch.BasicAuthConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Branch.BasicAuthConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-basicauthconfig
        '''
        result = self._values.get("basic_auth_config")
        return typing.cast(typing.Optional[typing.Union[CfnBranch.BasicAuthConfigProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Branch.BuildSpec``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-buildspec
        '''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Branch.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_auto_build(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Branch.EnableAutoBuild``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-enableautobuild
        '''
        result = self._values.get("enable_auto_build")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def enable_performance_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Branch.EnablePerformanceMode``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-enableperformancemode
        '''
        result = self._values.get("enable_performance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def enable_pull_request_preview(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Branch.EnablePullRequestPreview``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-enablepullrequestpreview
        '''
        result = self._values.get("enable_pull_request_preview")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnBranch.EnvironmentVariableProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::Amplify::Branch.EnvironmentVariables``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-environmentvariables
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnBranch.EnvironmentVariableProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def pull_request_environment_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Branch.PullRequestEnvironmentName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-pullrequestenvironmentname
        '''
        result = self._values.get("pull_request_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Branch.Stage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-stage
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Amplify::Branch.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBranchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDomain(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_amplify.CfnDomain",
):
    '''A CloudFormation ``AWS::Amplify::Domain``.

    :cloudformationResource: AWS::Amplify::Domain
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_id: builtins.str,
        domain_name: builtins.str,
        sub_domain_settings: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDomain.SubDomainSettingProperty", _IResolvable_da3f097b]]],
        auto_sub_domain_creation_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_sub_domain_iam_role: typing.Optional[builtins.str] = None,
        enable_auto_sub_domain: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Create a new ``AWS::Amplify::Domain``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param app_id: ``AWS::Amplify::Domain.AppId``.
        :param domain_name: ``AWS::Amplify::Domain.DomainName``.
        :param sub_domain_settings: ``AWS::Amplify::Domain.SubDomainSettings``.
        :param auto_sub_domain_creation_patterns: ``AWS::Amplify::Domain.AutoSubDomainCreationPatterns``.
        :param auto_sub_domain_iam_role: ``AWS::Amplify::Domain.AutoSubDomainIAMRole``.
        :param enable_auto_sub_domain: ``AWS::Amplify::Domain.EnableAutoSubDomain``.
        '''
        props = CfnDomainProps(
            app_id=app_id,
            domain_name=domain_name,
            sub_domain_settings=sub_domain_settings,
            auto_sub_domain_creation_patterns=auto_sub_domain_creation_patterns,
            auto_sub_domain_iam_role=auto_sub_domain_iam_role,
            enable_auto_sub_domain=enable_auto_sub_domain,
        )

        jsii.create(CfnDomain, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrAutoSubDomainCreationPatterns")
    def attr_auto_sub_domain_creation_patterns(self) -> typing.List[builtins.str]:
        '''
        :cloudformationAttribute: AutoSubDomainCreationPatterns
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "attrAutoSubDomainCreationPatterns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrAutoSubDomainIamRole")
    def attr_auto_sub_domain_iam_role(self) -> builtins.str:
        '''
        :cloudformationAttribute: AutoSubDomainIAMRole
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrAutoSubDomainIamRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCertificateRecord")
    def attr_certificate_record(self) -> builtins.str:
        '''
        :cloudformationAttribute: CertificateRecord
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCertificateRecord"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrDomainName")
    def attr_domain_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: DomainName
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrDomainStatus")
    def attr_domain_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: DomainStatus
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrDomainStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrEnableAutoSubDomain")
    def attr_enable_auto_sub_domain(self) -> _IResolvable_da3f097b:
        '''
        :cloudformationAttribute: EnableAutoSubDomain
        '''
        return typing.cast(_IResolvable_da3f097b, jsii.get(self, "attrEnableAutoSubDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatusReason")
    def attr_status_reason(self) -> builtins.str:
        '''
        :cloudformationAttribute: StatusReason
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatusReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        '''``AWS::Amplify::Domain.AppId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-appid
        '''
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @app_id.setter
    def app_id(self, value: builtins.str) -> None:
        jsii.set(self, "appId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''``AWS::Amplify::Domain.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-domainname
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subDomainSettings")
    def sub_domain_settings(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDomain.SubDomainSettingProperty", _IResolvable_da3f097b]]]:
        '''``AWS::Amplify::Domain.SubDomainSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-subdomainsettings
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDomain.SubDomainSettingProperty", _IResolvable_da3f097b]]], jsii.get(self, "subDomainSettings"))

    @sub_domain_settings.setter
    def sub_domain_settings(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDomain.SubDomainSettingProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "subDomainSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoSubDomainCreationPatterns")
    def auto_sub_domain_creation_patterns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Amplify::Domain.AutoSubDomainCreationPatterns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-autosubdomaincreationpatterns
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "autoSubDomainCreationPatterns"))

    @auto_sub_domain_creation_patterns.setter
    def auto_sub_domain_creation_patterns(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "autoSubDomainCreationPatterns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoSubDomainIamRole")
    def auto_sub_domain_iam_role(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Domain.AutoSubDomainIAMRole``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-autosubdomainiamrole
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoSubDomainIamRole"))

    @auto_sub_domain_iam_role.setter
    def auto_sub_domain_iam_role(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "autoSubDomainIamRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAutoSubDomain")
    def enable_auto_sub_domain(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Domain.EnableAutoSubDomain``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-enableautosubdomain
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enableAutoSubDomain"))

    @enable_auto_sub_domain.setter
    def enable_auto_sub_domain(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enableAutoSubDomain", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_amplify.CfnDomain.SubDomainSettingProperty",
        jsii_struct_bases=[],
        name_mapping={"branch_name": "branchName", "prefix": "prefix"},
    )
    class SubDomainSettingProperty:
        def __init__(self, *, branch_name: builtins.str, prefix: builtins.str) -> None:
            '''
            :param branch_name: ``CfnDomain.SubDomainSettingProperty.BranchName``.
            :param prefix: ``CfnDomain.SubDomainSettingProperty.Prefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-domain-subdomainsetting.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "branch_name": branch_name,
                "prefix": prefix,
            }

        @builtins.property
        def branch_name(self) -> builtins.str:
            '''``CfnDomain.SubDomainSettingProperty.BranchName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-domain-subdomainsetting.html#cfn-amplify-domain-subdomainsetting-branchname
            '''
            result = self._values.get("branch_name")
            assert result is not None, "Required property 'branch_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def prefix(self) -> builtins.str:
            '''``CfnDomain.SubDomainSettingProperty.Prefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-domain-subdomainsetting.html#cfn-amplify-domain-subdomainsetting-prefix
            '''
            result = self._values.get("prefix")
            assert result is not None, "Required property 'prefix' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SubDomainSettingProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_amplify.CfnDomainProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_id": "appId",
        "domain_name": "domainName",
        "sub_domain_settings": "subDomainSettings",
        "auto_sub_domain_creation_patterns": "autoSubDomainCreationPatterns",
        "auto_sub_domain_iam_role": "autoSubDomainIamRole",
        "enable_auto_sub_domain": "enableAutoSubDomain",
    },
)
class CfnDomainProps:
    def __init__(
        self,
        *,
        app_id: builtins.str,
        domain_name: builtins.str,
        sub_domain_settings: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnDomain.SubDomainSettingProperty, _IResolvable_da3f097b]]],
        auto_sub_domain_creation_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_sub_domain_iam_role: typing.Optional[builtins.str] = None,
        enable_auto_sub_domain: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Amplify::Domain``.

        :param app_id: ``AWS::Amplify::Domain.AppId``.
        :param domain_name: ``AWS::Amplify::Domain.DomainName``.
        :param sub_domain_settings: ``AWS::Amplify::Domain.SubDomainSettings``.
        :param auto_sub_domain_creation_patterns: ``AWS::Amplify::Domain.AutoSubDomainCreationPatterns``.
        :param auto_sub_domain_iam_role: ``AWS::Amplify::Domain.AutoSubDomainIAMRole``.
        :param enable_auto_sub_domain: ``AWS::Amplify::Domain.EnableAutoSubDomain``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_id": app_id,
            "domain_name": domain_name,
            "sub_domain_settings": sub_domain_settings,
        }
        if auto_sub_domain_creation_patterns is not None:
            self._values["auto_sub_domain_creation_patterns"] = auto_sub_domain_creation_patterns
        if auto_sub_domain_iam_role is not None:
            self._values["auto_sub_domain_iam_role"] = auto_sub_domain_iam_role
        if enable_auto_sub_domain is not None:
            self._values["enable_auto_sub_domain"] = enable_auto_sub_domain

    @builtins.property
    def app_id(self) -> builtins.str:
        '''``AWS::Amplify::Domain.AppId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-appid
        '''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''``AWS::Amplify::Domain.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-domainname
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sub_domain_settings(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnDomain.SubDomainSettingProperty, _IResolvable_da3f097b]]]:
        '''``AWS::Amplify::Domain.SubDomainSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-subdomainsettings
        '''
        result = self._values.get("sub_domain_settings")
        assert result is not None, "Required property 'sub_domain_settings' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnDomain.SubDomainSettingProperty, _IResolvable_da3f097b]]], result)

    @builtins.property
    def auto_sub_domain_creation_patterns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Amplify::Domain.AutoSubDomainCreationPatterns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-autosubdomaincreationpatterns
        '''
        result = self._values.get("auto_sub_domain_creation_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def auto_sub_domain_iam_role(self) -> typing.Optional[builtins.str]:
        '''``AWS::Amplify::Domain.AutoSubDomainIAMRole``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-autosubdomainiamrole
        '''
        result = self._values.get("auto_sub_domain_iam_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_auto_sub_domain(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Amplify::Domain.EnableAutoSubDomain``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-enableautosubdomain
        '''
        result = self._values.get("enable_auto_sub_domain")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnApp",
    "CfnAppProps",
    "CfnBranch",
    "CfnBranchProps",
    "CfnDomain",
    "CfnDomainProps",
]

publication.publish()
