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
    IInspectable as _IInspectable_c2943556,
    IResolvable as _IResolvable_da3f097b,
    TreeInspector as _TreeInspector_488e0dd5,
)


@jsii.implements(_IInspectable_c2943556)
class CfnGitHubRepository(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_codestar.CfnGitHubRepository",
):
    '''A CloudFormation ``AWS::CodeStar::GitHubRepository``.

    :cloudformationResource: AWS::CodeStar::GitHubRepository
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        repository_name: builtins.str,
        repository_owner: builtins.str,
        code: typing.Optional[typing.Union["CfnGitHubRepository.CodeProperty", _IResolvable_da3f097b]] = None,
        connection_arn: typing.Optional[builtins.str] = None,
        enable_issues: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        is_private: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        repository_access_token: typing.Optional[builtins.str] = None,
        repository_description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::CodeStar::GitHubRepository``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param repository_name: ``AWS::CodeStar::GitHubRepository.RepositoryName``.
        :param repository_owner: ``AWS::CodeStar::GitHubRepository.RepositoryOwner``.
        :param code: ``AWS::CodeStar::GitHubRepository.Code``.
        :param connection_arn: ``AWS::CodeStar::GitHubRepository.ConnectionArn``.
        :param enable_issues: ``AWS::CodeStar::GitHubRepository.EnableIssues``.
        :param is_private: ``AWS::CodeStar::GitHubRepository.IsPrivate``.
        :param repository_access_token: ``AWS::CodeStar::GitHubRepository.RepositoryAccessToken``.
        :param repository_description: ``AWS::CodeStar::GitHubRepository.RepositoryDescription``.
        '''
        props = CfnGitHubRepositoryProps(
            repository_name=repository_name,
            repository_owner=repository_owner,
            code=code,
            connection_arn=connection_arn,
            enable_issues=enable_issues,
            is_private=is_private,
            repository_access_token=repository_access_token,
            repository_description=repository_description,
        )

        jsii.create(CfnGitHubRepository, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''``AWS::CodeStar::GitHubRepository.RepositoryName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-repositoryname
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @repository_name.setter
    def repository_name(self, value: builtins.str) -> None:
        jsii.set(self, "repositoryName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryOwner")
    def repository_owner(self) -> builtins.str:
        '''``AWS::CodeStar::GitHubRepository.RepositoryOwner``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-repositoryowner
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryOwner"))

    @repository_owner.setter
    def repository_owner(self, value: builtins.str) -> None:
        jsii.set(self, "repositoryOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="code")
    def code(
        self,
    ) -> typing.Optional[typing.Union["CfnGitHubRepository.CodeProperty", _IResolvable_da3f097b]]:
        '''``AWS::CodeStar::GitHubRepository.Code``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-code
        '''
        return typing.cast(typing.Optional[typing.Union["CfnGitHubRepository.CodeProperty", _IResolvable_da3f097b]], jsii.get(self, "code"))

    @code.setter
    def code(
        self,
        value: typing.Optional[typing.Union["CfnGitHubRepository.CodeProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "code", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionArn")
    def connection_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStar::GitHubRepository.ConnectionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-connectionarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionArn"))

    @connection_arn.setter
    def connection_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "connectionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableIssues")
    def enable_issues(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::CodeStar::GitHubRepository.EnableIssues``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-enableissues
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enableIssues"))

    @enable_issues.setter
    def enable_issues(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enableIssues", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isPrivate")
    def is_private(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::CodeStar::GitHubRepository.IsPrivate``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-isprivate
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "isPrivate"))

    @is_private.setter
    def is_private(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "isPrivate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryAccessToken")
    def repository_access_token(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStar::GitHubRepository.RepositoryAccessToken``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-repositoryaccesstoken
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryAccessToken"))

    @repository_access_token.setter
    def repository_access_token(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "repositoryAccessToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryDescription")
    def repository_description(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStar::GitHubRepository.RepositoryDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-repositorydescription
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryDescription"))

    @repository_description.setter
    def repository_description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "repositoryDescription", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codestar.CfnGitHubRepository.CodeProperty",
        jsii_struct_bases=[],
        name_mapping={"s3": "s3"},
    )
    class CodeProperty:
        def __init__(
            self,
            *,
            s3: typing.Union["CfnGitHubRepository.S3Property", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param s3: ``CfnGitHubRepository.CodeProperty.S3``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codestar-githubrepository-code.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "s3": s3,
            }

        @builtins.property
        def s3(
            self,
        ) -> typing.Union["CfnGitHubRepository.S3Property", _IResolvable_da3f097b]:
            '''``CfnGitHubRepository.CodeProperty.S3``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codestar-githubrepository-code.html#cfn-codestar-githubrepository-code-s3
            '''
            result = self._values.get("s3")
            assert result is not None, "Required property 's3' is missing"
            return typing.cast(typing.Union["CfnGitHubRepository.S3Property", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CodeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codestar.CfnGitHubRepository.S3Property",
        jsii_struct_bases=[],
        name_mapping={
            "bucket": "bucket",
            "key": "key",
            "object_version": "objectVersion",
        },
    )
    class S3Property:
        def __init__(
            self,
            *,
            bucket: builtins.str,
            key: builtins.str,
            object_version: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param bucket: ``CfnGitHubRepository.S3Property.Bucket``.
            :param key: ``CfnGitHubRepository.S3Property.Key``.
            :param object_version: ``CfnGitHubRepository.S3Property.ObjectVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codestar-githubrepository-s3.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "bucket": bucket,
                "key": key,
            }
            if object_version is not None:
                self._values["object_version"] = object_version

        @builtins.property
        def bucket(self) -> builtins.str:
            '''``CfnGitHubRepository.S3Property.Bucket``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codestar-githubrepository-s3.html#cfn-codestar-githubrepository-s3-bucket
            '''
            result = self._values.get("bucket")
            assert result is not None, "Required property 'bucket' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def key(self) -> builtins.str:
            '''``CfnGitHubRepository.S3Property.Key``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codestar-githubrepository-s3.html#cfn-codestar-githubrepository-s3-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def object_version(self) -> typing.Optional[builtins.str]:
            '''``CfnGitHubRepository.S3Property.ObjectVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codestar-githubrepository-s3.html#cfn-codestar-githubrepository-s3-objectversion
            '''
            result = self._values.get("object_version")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3Property(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codestar.CfnGitHubRepositoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "repository_name": "repositoryName",
        "repository_owner": "repositoryOwner",
        "code": "code",
        "connection_arn": "connectionArn",
        "enable_issues": "enableIssues",
        "is_private": "isPrivate",
        "repository_access_token": "repositoryAccessToken",
        "repository_description": "repositoryDescription",
    },
)
class CfnGitHubRepositoryProps:
    def __init__(
        self,
        *,
        repository_name: builtins.str,
        repository_owner: builtins.str,
        code: typing.Optional[typing.Union[CfnGitHubRepository.CodeProperty, _IResolvable_da3f097b]] = None,
        connection_arn: typing.Optional[builtins.str] = None,
        enable_issues: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        is_private: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        repository_access_token: typing.Optional[builtins.str] = None,
        repository_description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::CodeStar::GitHubRepository``.

        :param repository_name: ``AWS::CodeStar::GitHubRepository.RepositoryName``.
        :param repository_owner: ``AWS::CodeStar::GitHubRepository.RepositoryOwner``.
        :param code: ``AWS::CodeStar::GitHubRepository.Code``.
        :param connection_arn: ``AWS::CodeStar::GitHubRepository.ConnectionArn``.
        :param enable_issues: ``AWS::CodeStar::GitHubRepository.EnableIssues``.
        :param is_private: ``AWS::CodeStar::GitHubRepository.IsPrivate``.
        :param repository_access_token: ``AWS::CodeStar::GitHubRepository.RepositoryAccessToken``.
        :param repository_description: ``AWS::CodeStar::GitHubRepository.RepositoryDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "repository_name": repository_name,
            "repository_owner": repository_owner,
        }
        if code is not None:
            self._values["code"] = code
        if connection_arn is not None:
            self._values["connection_arn"] = connection_arn
        if enable_issues is not None:
            self._values["enable_issues"] = enable_issues
        if is_private is not None:
            self._values["is_private"] = is_private
        if repository_access_token is not None:
            self._values["repository_access_token"] = repository_access_token
        if repository_description is not None:
            self._values["repository_description"] = repository_description

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''``AWS::CodeStar::GitHubRepository.RepositoryName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-repositoryname
        '''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_owner(self) -> builtins.str:
        '''``AWS::CodeStar::GitHubRepository.RepositoryOwner``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-repositoryowner
        '''
        result = self._values.get("repository_owner")
        assert result is not None, "Required property 'repository_owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code(
        self,
    ) -> typing.Optional[typing.Union[CfnGitHubRepository.CodeProperty, _IResolvable_da3f097b]]:
        '''``AWS::CodeStar::GitHubRepository.Code``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-code
        '''
        result = self._values.get("code")
        return typing.cast(typing.Optional[typing.Union[CfnGitHubRepository.CodeProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def connection_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStar::GitHubRepository.ConnectionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-connectionarn
        '''
        result = self._values.get("connection_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_issues(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::CodeStar::GitHubRepository.EnableIssues``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-enableissues
        '''
        result = self._values.get("enable_issues")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def is_private(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::CodeStar::GitHubRepository.IsPrivate``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-isprivate
        '''
        result = self._values.get("is_private")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def repository_access_token(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStar::GitHubRepository.RepositoryAccessToken``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-repositoryaccesstoken
        '''
        result = self._values.get("repository_access_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_description(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeStar::GitHubRepository.RepositoryDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codestar-githubrepository.html#cfn-codestar-githubrepository-repositorydescription
        '''
        result = self._values.get("repository_description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnGitHubRepositoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnGitHubRepository",
    "CfnGitHubRepositoryProps",
]

publication.publish()
