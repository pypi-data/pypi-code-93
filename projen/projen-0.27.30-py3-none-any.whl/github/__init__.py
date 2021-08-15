import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import (
    Component as _Component_2b0ad27f,
    Project as _Project_57d89203,
    TextFile as _TextFile_4a74808c,
    YamlFile as _YamlFile_909731b0,
)
from ..tasks import Task as _Task_fb843092
from .workflows import (
    CheckRunOptions as _CheckRunOptions_66af1ceb,
    CheckSuiteOptions as _CheckSuiteOptions_6a122376,
    ContainerOptions as _ContainerOptions_f50907af,
    CreateOptions as _CreateOptions_6247308d,
    CronScheduleOptions as _CronScheduleOptions_7724cd93,
    DeleteOptions as _DeleteOptions_c46578d4,
    DeploymentOptions as _DeploymentOptions_0bea6580,
    DeploymentStatusOptions as _DeploymentStatusOptions_f9cbd32b,
    ForkOptions as _ForkOptions_0437229d,
    GollumOptions as _GollumOptions_1acffea2,
    IssueCommentOptions as _IssueCommentOptions_b551b1e5,
    IssuesOptions as _IssuesOptions_dd89885c,
    Job as _Job_20ffcf45,
    JobPermissions as _JobPermissions_3b5b53dc,
    JobStep as _JobStep_c3287c05,
    JobStepOutput as _JobStepOutput_acebe827,
    LabelOptions as _LabelOptions_ca474a61,
    MilestoneOptions as _MilestoneOptions_6f9d8b6f,
    PageBuildOptions as _PageBuildOptions_c30eafce,
    ProjectCardOptions as _ProjectCardOptions_c89fc28d,
    ProjectColumnOptions as _ProjectColumnOptions_25a462f6,
    ProjectOptions as _ProjectOptions_50d963ea,
    PublicOptions as _PublicOptions_2c3a3b94,
    PullRequestOptions as _PullRequestOptions_b051b0c9,
    PullRequestReviewCommentOptions as _PullRequestReviewCommentOptions_85235a68,
    PullRequestReviewOptions as _PullRequestReviewOptions_27fd8e95,
    PullRequestTargetOptions as _PullRequestTargetOptions_81011bb1,
    PushOptions as _PushOptions_63e1c4f2,
    RegistryPackageOptions as _RegistryPackageOptions_781d5ac7,
    ReleaseOptions as _ReleaseOptions_d152186d,
    RepositoryDispatchOptions as _RepositoryDispatchOptions_d75e9903,
    StatusOptions as _StatusOptions_aa35df44,
    Triggers as _Triggers_e9ae7617,
    WatchOptions as _WatchOptions_d33f5d00,
    WorkflowDispatchOptions as _WorkflowDispatchOptions_7110ffdc,
    WorkflowRunOptions as _WorkflowRunOptions_5a4262c5,
)


class AutoApprove(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.AutoApprove",
):
    '''(experimental) Auto approve pull requests that meet a criteria.

    :stability: experimental
    '''

    def __init__(
        self,
        github: "GitHub",
        *,
        secret: builtins.str,
        allowed_usernames: typing.Optional[typing.Sequence[builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param github: -
        :param secret: (experimental) A GitHub secret name which contains a GitHub Access Token with write permissions for the ``pull_request`` scope. This token is used to approve pull requests. Github forbids an identity to approve its own pull request. If your project produces automated pull requests using the Github default token - {@link https://docs.github.com/en/actions/reference/authentication-in-a-workflow ``GITHUB_TOKEN`` } - that you would like auto approved, such as when using the ``depsUpgrade`` property in ``NodeProjectOptions``, then you must use a different token here.
        :param allowed_usernames: (experimental) Only pull requests authored by these Github usernames will be auto-approved. Default: ['github-bot']
        :param label: (experimental) Only pull requests with this label will be auto-approved. Default: 'auto-approve'

        :stability: experimental
        '''
        options = AutoApproveOptions(
            secret=secret, allowed_usernames=allowed_usernames, label=label
        )

        jsii.create(AutoApprove, self, [github, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "label"))


@jsii.data_type(
    jsii_type="projen.github.AutoApproveOptions",
    jsii_struct_bases=[],
    name_mapping={
        "secret": "secret",
        "allowed_usernames": "allowedUsernames",
        "label": "label",
    },
)
class AutoApproveOptions:
    def __init__(
        self,
        *,
        secret: builtins.str,
        allowed_usernames: typing.Optional[typing.Sequence[builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for 'AutoApprove'.

        :param secret: (experimental) A GitHub secret name which contains a GitHub Access Token with write permissions for the ``pull_request`` scope. This token is used to approve pull requests. Github forbids an identity to approve its own pull request. If your project produces automated pull requests using the Github default token - {@link https://docs.github.com/en/actions/reference/authentication-in-a-workflow ``GITHUB_TOKEN`` } - that you would like auto approved, such as when using the ``depsUpgrade`` property in ``NodeProjectOptions``, then you must use a different token here.
        :param allowed_usernames: (experimental) Only pull requests authored by these Github usernames will be auto-approved. Default: ['github-bot']
        :param label: (experimental) Only pull requests with this label will be auto-approved. Default: 'auto-approve'

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "secret": secret,
        }
        if allowed_usernames is not None:
            self._values["allowed_usernames"] = allowed_usernames
        if label is not None:
            self._values["label"] = label

    @builtins.property
    def secret(self) -> builtins.str:
        '''(experimental) A GitHub secret name which contains a GitHub Access Token with write permissions for the ``pull_request`` scope.

        This token is used to approve pull requests.

        Github forbids an identity to approve its own pull request.
        If your project produces automated pull requests using the Github default token -
        {@link https://docs.github.com/en/actions/reference/authentication-in-a-workflow ``GITHUB_TOKEN`` }

        - that you would like auto approved, such as when using the ``depsUpgrade`` property in
          ``NodeProjectOptions``, then you must use a different token here.

        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_usernames(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Only pull requests authored by these Github usernames will be auto-approved.

        :default: ['github-bot']

        :stability: experimental
        '''
        result = self._values.get("allowed_usernames")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''(experimental) Only pull requests with this label will be auto-approved.

        :default: 'auto-approve'

        :stability: experimental
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoApproveOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoMerge(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.AutoMerge",
):
    '''(experimental) Sets up mergify to merging approved pull requests.

    If ``buildJob`` is specified, the specified GitHub workflow job ID is required
    to succeed in order for the PR to be merged.

    ``approvedReviews`` specified the number of code review approvals required for
    the PR to be merged.

    :stability: experimental
    '''

    def __init__(
        self,
        github: "GitHub",
        *,
        approved_reviews: typing.Optional[jsii.Number] = None,
        blocking_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        build_job: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param github: -
        :param approved_reviews: (experimental) Number of approved code reviews. Default: 1
        :param blocking_labels: (experimental) List of labels that will prevent auto-merging. Default: ['do-not-merge']
        :param build_job: (experimental) The GitHub job ID of the build workflow.

        :stability: experimental
        '''
        options = AutoMergeOptions(
            approved_reviews=approved_reviews,
            blocking_labels=blocking_labels,
            build_job=build_job,
        )

        jsii.create(AutoMerge, self, [github, options])


@jsii.data_type(
    jsii_type="projen.github.AutoMergeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "approved_reviews": "approvedReviews",
        "blocking_labels": "blockingLabels",
        "build_job": "buildJob",
    },
)
class AutoMergeOptions:
    def __init__(
        self,
        *,
        approved_reviews: typing.Optional[jsii.Number] = None,
        blocking_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        build_job: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param approved_reviews: (experimental) Number of approved code reviews. Default: 1
        :param blocking_labels: (experimental) List of labels that will prevent auto-merging. Default: ['do-not-merge']
        :param build_job: (experimental) The GitHub job ID of the build workflow.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if approved_reviews is not None:
            self._values["approved_reviews"] = approved_reviews
        if blocking_labels is not None:
            self._values["blocking_labels"] = blocking_labels
        if build_job is not None:
            self._values["build_job"] = build_job

    @builtins.property
    def approved_reviews(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of approved code reviews.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("approved_reviews")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def blocking_labels(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of labels that will prevent auto-merging.

        :default: ['do-not-merge']

        :stability: experimental
        '''
        result = self._values.get("blocking_labels")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def build_job(self) -> typing.Optional[builtins.str]:
        '''(experimental) The GitHub job ID of the build workflow.

        :stability: experimental
        '''
        result = self._values.get("build_job")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoMergeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Dependabot(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.Dependabot",
):
    '''(experimental) Defines dependabot configuration for node projects.

    Since module versions are managed in projen, the versioning strategy will be
    configured to "lockfile-only" which means that only updates that can be done
    on the lockfile itself will be proposed.

    :stability: experimental
    '''

    def __init__(
        self,
        github: "GitHub",
        *,
        ignore: typing.Optional[typing.Sequence["DependabotIgnore"]] = None,
        ignore_projen: typing.Optional[builtins.bool] = None,
        labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        registries: typing.Optional[typing.Mapping[builtins.str, "DependabotRegistry"]] = None,
        schedule_interval: typing.Optional["DependabotScheduleInterval"] = None,
        versioning_strategy: typing.Optional["VersioningStrategy"] = None,
    ) -> None:
        '''
        :param github: -
        :param ignore: (experimental) You can use the ``ignore`` option to customize which dependencies are updated. The ignore option supports the following options. Default: []
        :param ignore_projen: (experimental) Ignores updates to ``projen``. This is required since projen updates may cause changes in committed files and anti-tamper checks will fail. Projen upgrades are covered through the ``ProjenUpgrade`` class. Default: true
        :param labels: (experimental) List of labels to apply to the created PR's.
        :param registries: (experimental) Map of package registries to use. Default: - use public registries
        :param schedule_interval: (experimental) How often to check for new versions and raise pull requests. Default: ScheduleInterval.DAILY
        :param versioning_strategy: (experimental) The strategy to use when edits manifest and lock files. Default: VersioningStrategy.LOCKFILE_ONLY The default is to only update the lock file because package.json is controlled by projen and any outside updates will fail the build.

        :stability: experimental
        '''
        options = DependabotOptions(
            ignore=ignore,
            ignore_projen=ignore_projen,
            labels=labels,
            registries=registries,
            schedule_interval=schedule_interval,
            versioning_strategy=versioning_strategy,
        )

        jsii.create(Dependabot, self, [github, options])

    @jsii.member(jsii_name="addIgnore")
    def add_ignore(
        self,
        dependency_name: builtins.str,
        *versions: builtins.str,
    ) -> None:
        '''(experimental) Ignores a dependency from automatic updates.

        :param dependency_name: Use to ignore updates for dependencies with matching names, optionally using ``*`` to match zero or more characters.
        :param versions: Use to ignore specific versions or ranges of versions. If you want to define a range, use the standard pattern for the package manager (for example: ``^1.0.0`` for npm, or ``~> 2.0`` for Bundler).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addIgnore", [dependency_name, *versions]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="config")
    def config(self) -> typing.Any:
        '''(experimental) The raw dependabot configuration.

        :see: https://docs.github.com/en/github/administering-a-repository/configuration-options-for-dependency-updates
        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.get(self, "config"))


@jsii.data_type(
    jsii_type="projen.github.DependabotIgnore",
    jsii_struct_bases=[],
    name_mapping={"dependency_name": "dependencyName", "versions": "versions"},
)
class DependabotIgnore:
    def __init__(
        self,
        *,
        dependency_name: builtins.str,
        versions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) You can use the ``ignore`` option to customize which dependencies are updated.

        The ignore option supports the following options.

        :param dependency_name: (experimental) Use to ignore updates for dependencies with matching names, optionally using ``*`` to match zero or more characters. For Java dependencies, the format of the dependency-name attribute is: ``groupId:artifactId``, for example: ``org.kohsuke:github-api``.
        :param versions: (experimental) Use to ignore specific versions or ranges of versions. If you want to define a range, use the standard pattern for the package manager (for example: ``^1.0.0`` for npm, or ``~> 2.0`` for Bundler).

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dependency_name": dependency_name,
        }
        if versions is not None:
            self._values["versions"] = versions

    @builtins.property
    def dependency_name(self) -> builtins.str:
        '''(experimental) Use to ignore updates for dependencies with matching names, optionally using ``*`` to match zero or more characters.

        For Java dependencies, the format of the dependency-name attribute is:
        ``groupId:artifactId``, for example: ``org.kohsuke:github-api``.

        :stability: experimental
        '''
        result = self._values.get("dependency_name")
        assert result is not None, "Required property 'dependency_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Use to ignore specific versions or ranges of versions.

        If you want to
        define a range, use the standard pattern for the package manager (for
        example: ``^1.0.0`` for npm, or ``~> 2.0`` for Bundler).

        :stability: experimental
        '''
        result = self._values.get("versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DependabotIgnore(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.DependabotOptions",
    jsii_struct_bases=[],
    name_mapping={
        "ignore": "ignore",
        "ignore_projen": "ignoreProjen",
        "labels": "labels",
        "registries": "registries",
        "schedule_interval": "scheduleInterval",
        "versioning_strategy": "versioningStrategy",
    },
)
class DependabotOptions:
    def __init__(
        self,
        *,
        ignore: typing.Optional[typing.Sequence[DependabotIgnore]] = None,
        ignore_projen: typing.Optional[builtins.bool] = None,
        labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        registries: typing.Optional[typing.Mapping[builtins.str, "DependabotRegistry"]] = None,
        schedule_interval: typing.Optional["DependabotScheduleInterval"] = None,
        versioning_strategy: typing.Optional["VersioningStrategy"] = None,
    ) -> None:
        '''
        :param ignore: (experimental) You can use the ``ignore`` option to customize which dependencies are updated. The ignore option supports the following options. Default: []
        :param ignore_projen: (experimental) Ignores updates to ``projen``. This is required since projen updates may cause changes in committed files and anti-tamper checks will fail. Projen upgrades are covered through the ``ProjenUpgrade`` class. Default: true
        :param labels: (experimental) List of labels to apply to the created PR's.
        :param registries: (experimental) Map of package registries to use. Default: - use public registries
        :param schedule_interval: (experimental) How often to check for new versions and raise pull requests. Default: ScheduleInterval.DAILY
        :param versioning_strategy: (experimental) The strategy to use when edits manifest and lock files. Default: VersioningStrategy.LOCKFILE_ONLY The default is to only update the lock file because package.json is controlled by projen and any outside updates will fail the build.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if ignore is not None:
            self._values["ignore"] = ignore
        if ignore_projen is not None:
            self._values["ignore_projen"] = ignore_projen
        if labels is not None:
            self._values["labels"] = labels
        if registries is not None:
            self._values["registries"] = registries
        if schedule_interval is not None:
            self._values["schedule_interval"] = schedule_interval
        if versioning_strategy is not None:
            self._values["versioning_strategy"] = versioning_strategy

    @builtins.property
    def ignore(self) -> typing.Optional[typing.List[DependabotIgnore]]:
        '''(experimental) You can use the ``ignore`` option to customize which dependencies are updated.

        The ignore option supports the following options.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("ignore")
        return typing.cast(typing.Optional[typing.List[DependabotIgnore]], result)

    @builtins.property
    def ignore_projen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Ignores updates to ``projen``.

        This is required since projen updates may cause changes in committed files
        and anti-tamper checks will fail.

        Projen upgrades are covered through the ``ProjenUpgrade`` class.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("ignore_projen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of labels to apply to the created PR's.

        :stability: experimental
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def registries(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "DependabotRegistry"]]:
        '''(experimental) Map of package registries to use.

        :default: - use public registries

        :stability: experimental
        '''
        result = self._values.get("registries")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "DependabotRegistry"]], result)

    @builtins.property
    def schedule_interval(self) -> typing.Optional["DependabotScheduleInterval"]:
        '''(experimental) How often to check for new versions and raise pull requests.

        :default: ScheduleInterval.DAILY

        :stability: experimental
        '''
        result = self._values.get("schedule_interval")
        return typing.cast(typing.Optional["DependabotScheduleInterval"], result)

    @builtins.property
    def versioning_strategy(self) -> typing.Optional["VersioningStrategy"]:
        '''(experimental) The strategy to use when edits manifest and lock files.

        :default:

        VersioningStrategy.LOCKFILE_ONLY The default is to only update the
        lock file because package.json is controlled by projen and any outside
        updates will fail the build.

        :stability: experimental
        '''
        result = self._values.get("versioning_strategy")
        return typing.cast(typing.Optional["VersioningStrategy"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DependabotOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.DependabotRegistry",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "url": "url",
        "key": "key",
        "organization": "organization",
        "password": "password",
        "replaces_base": "replacesBase",
        "token": "token",
        "username": "username",
    },
)
class DependabotRegistry:
    def __init__(
        self,
        *,
        type: "DependabotRegistryType",
        url: builtins.str,
        key: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        replaces_base: typing.Optional[builtins.bool] = None,
        token: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Use to add private registry support for dependabot.

        :param type: (experimental) Registry type e.g. 'npm-registry' or 'docker-registry'.
        :param url: (experimental) Url for the registry e.g. 'https://npm.pkg.github.com' or 'registry.hub.docker.com'.
        :param key: (experimental) A reference to a Dependabot secret containing an access key for this registry. Default: undefined
        :param organization: (experimental) Used with the hex-organization registry type. Default: undefined
        :param password: (experimental) A reference to a Dependabot secret containing the password for the specified user. Default: undefined
        :param replaces_base: (experimental) For registries with type: python-index, if the boolean value is true, pip esolves dependencies by using the specified URL rather than the base URL of the Python Package Index (by default https://pypi.org/simple). Default: undefined
        :param token: (experimental) Secret token for dependabot access e.g. '${{ secrets.DEPENDABOT_PACKAGE_TOKEN }}'. Default: undefined
        :param username: (experimental) The username that Dependabot uses to access the registry. Default: - do not authenticate

        :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#configuration-options-for-private-registries
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
            "url": url,
        }
        if key is not None:
            self._values["key"] = key
        if organization is not None:
            self._values["organization"] = organization
        if password is not None:
            self._values["password"] = password
        if replaces_base is not None:
            self._values["replaces_base"] = replaces_base
        if token is not None:
            self._values["token"] = token
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def type(self) -> "DependabotRegistryType":
        '''(experimental) Registry type e.g. 'npm-registry' or 'docker-registry'.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("DependabotRegistryType", result)

    @builtins.property
    def url(self) -> builtins.str:
        '''(experimental) Url for the registry e.g. 'https://npm.pkg.github.com' or 'registry.hub.docker.com'.

        :stability: experimental
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''(experimental) A reference to a Dependabot secret containing an access key for this registry.

        :default: undefined

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''(experimental) Used with the hex-organization registry type.

        :default: undefined

        :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#hex-organization
        :stability: experimental
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''(experimental) A reference to a Dependabot secret containing the password for the specified user.

        :default: undefined

        :stability: experimental
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replaces_base(self) -> typing.Optional[builtins.bool]:
        '''(experimental) For registries with type: python-index, if the boolean value is true, pip esolves dependencies by using the specified URL rather than the base URL of the Python Package Index (by default https://pypi.org/simple).

        :default: undefined

        :stability: experimental
        '''
        result = self._values.get("replaces_base")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''(experimental) Secret token for dependabot access e.g. '${{ secrets.DEPENDABOT_PACKAGE_TOKEN }}'.

        :default: undefined

        :stability: experimental
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''(experimental) The username that Dependabot uses to access the registry.

        :default: - do not authenticate

        :stability: experimental
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DependabotRegistry(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.github.DependabotRegistryType")
class DependabotRegistryType(enum.Enum):
    '''(experimental) Each configuration type requires you to provide particular settings.

    Some types allow more than one way to connect

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#configuration-options-for-private-registries
    :stability: experimental
    '''

    COMPOSER_REGISTRY = "COMPOSER_REGISTRY"
    '''(experimental) The composer-repository type supports username and password.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#composer-repository
    :stability: experimental
    '''
    DOCKER_REGISTRY = "DOCKER_REGISTRY"
    '''(experimental) The docker-registry type supports username and password.

    The docker-registry type can also be used to pull from Amazon ECR using static AWS credentials

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#docker-registry
    :stability: experimental
    '''
    GIT = "GIT"
    '''(experimental) The git type supports username and password.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#git
    :stability: experimental
    '''
    HEX_ORGANIZATION = "HEX_ORGANIZATION"
    '''(experimental) The hex-organization type supports organization and key.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#hex-organization
    :stability: experimental
    '''
    MAVEN_REPOSITORY = "MAVEN_REPOSITORY"
    '''(experimental) The maven-repository type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#maven-repository
    :stability: experimental
    '''
    NPM_REGISTRY = "NPM_REGISTRY"
    '''(experimental) The npm-registry type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#npm-registry
    :stability: experimental
    '''
    NUGET_FEED = "NUGET_FEED"
    '''(experimental) The nuget-feed type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#nuget-feed
    :stability: experimental
    '''
    PYTHON_INDEX = "PYTHON_INDEX"
    '''(experimental) The python-index type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#python-index
    :stability: experimental
    '''
    RUBYGEMS_SERVER = "RUBYGEMS_SERVER"
    '''(experimental) The rubygems-server type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#rubygems-server
    :stability: experimental
    '''
    TERRAFORM_REGISTRY = "TERRAFORM_REGISTRY"
    '''(experimental) The terraform-registry type supports a token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#terraform-registry
    :stability: experimental
    '''


@jsii.enum(jsii_type="projen.github.DependabotScheduleInterval")
class DependabotScheduleInterval(enum.Enum):
    '''(experimental) How often to check for new versions and raise pull requests for version updates.

    :stability: experimental
    '''

    DAILY = "DAILY"
    '''(experimental) Runs on every weekday, Monday to Friday.

    :stability: experimental
    '''
    WEEKLY = "WEEKLY"
    '''(experimental) Runs once each week.

    By default, this is on Monday.

    :stability: experimental
    '''
    MONTHLY = "MONTHLY"
    '''(experimental) Runs once each month.

    This is on the first day of the month.

    :stability: experimental
    '''


class GitHub(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.GitHub",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        mergify: typing.Optional[builtins.bool] = None,
        workflows: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param mergify: (experimental) Whether mergify should be enabled on this repository or not. Default: true
        :param workflows: (experimental) Enables GitHub workflows. If this is set to ``false``, workflows will not be created. Default: true

        :stability: experimental
        '''
        options = GitHubOptions(mergify=mergify, workflows=workflows)

        jsii.create(GitHub, self, [project, options])

    @jsii.member(jsii_name="addDependabot")
    def add_dependabot(
        self,
        *,
        ignore: typing.Optional[typing.Sequence[DependabotIgnore]] = None,
        ignore_projen: typing.Optional[builtins.bool] = None,
        labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        registries: typing.Optional[typing.Mapping[builtins.str, DependabotRegistry]] = None,
        schedule_interval: typing.Optional[DependabotScheduleInterval] = None,
        versioning_strategy: typing.Optional["VersioningStrategy"] = None,
    ) -> Dependabot:
        '''
        :param ignore: (experimental) You can use the ``ignore`` option to customize which dependencies are updated. The ignore option supports the following options. Default: []
        :param ignore_projen: (experimental) Ignores updates to ``projen``. This is required since projen updates may cause changes in committed files and anti-tamper checks will fail. Projen upgrades are covered through the ``ProjenUpgrade`` class. Default: true
        :param labels: (experimental) List of labels to apply to the created PR's.
        :param registries: (experimental) Map of package registries to use. Default: - use public registries
        :param schedule_interval: (experimental) How often to check for new versions and raise pull requests. Default: ScheduleInterval.DAILY
        :param versioning_strategy: (experimental) The strategy to use when edits manifest and lock files. Default: VersioningStrategy.LOCKFILE_ONLY The default is to only update the lock file because package.json is controlled by projen and any outside updates will fail the build.

        :stability: experimental
        '''
        options = DependabotOptions(
            ignore=ignore,
            ignore_projen=ignore_projen,
            labels=labels,
            registries=registries,
            schedule_interval=schedule_interval,
            versioning_strategy=versioning_strategy,
        )

        return typing.cast(Dependabot, jsii.invoke(self, "addDependabot", [options]))

    @jsii.member(jsii_name="addPullRequestTemplate")
    def add_pull_request_template(
        self,
        *content: builtins.str,
    ) -> "PullRequestTemplate":
        '''
        :param content: -

        :stability: experimental
        '''
        return typing.cast("PullRequestTemplate", jsii.invoke(self, "addPullRequestTemplate", [*content]))

    @jsii.member(jsii_name="addWorkflow")
    def add_workflow(self, name: builtins.str) -> "GithubWorkflow":
        '''
        :param name: -

        :stability: experimental
        '''
        return typing.cast("GithubWorkflow", jsii.invoke(self, "addWorkflow", [name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflows")
    def workflows(self) -> builtins.bool:
        '''(experimental) Are workflows enabled?

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "workflows"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mergify")
    def mergify(self) -> typing.Optional["Mergify"]:
        '''(experimental) The ``Mergify`` configured on this repository.

        This is ``undefined`` if Mergify
        was not enabled when creating the repository.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["Mergify"], jsii.get(self, "mergify"))


@jsii.data_type(
    jsii_type="projen.github.GitHubOptions",
    jsii_struct_bases=[],
    name_mapping={"mergify": "mergify", "workflows": "workflows"},
)
class GitHubOptions:
    def __init__(
        self,
        *,
        mergify: typing.Optional[builtins.bool] = None,
        workflows: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param mergify: (experimental) Whether mergify should be enabled on this repository or not. Default: true
        :param workflows: (experimental) Enables GitHub workflows. If this is set to ``false``, workflows will not be created. Default: true

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if mergify is not None:
            self._values["mergify"] = mergify
        if workflows is not None:
            self._values["workflows"] = workflows

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether mergify should be enabled on this repository or not.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflows(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enables GitHub workflows.

        If this is set to ``false``, workflows will not be created.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("workflows")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GithubWorkflow(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.GithubWorkflow",
):
    '''(experimental) Workflow for GitHub.

    A workflow is a configurable automated process made up of one or more jobs.

    :see: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        name: builtins.str,
        *,
        force: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param github: -
        :param name: -
        :param force: (experimental) Force the creation of the workflow even if ``workflows`` is disabled in ``GitHub``. Default: false

        :stability: experimental
        '''
        options = GithubWorkflowOptions(force=force)

        jsii.create(GithubWorkflow, self, [github, name, options])

    @jsii.member(jsii_name="addJobs")
    def add_jobs(self, jobs: typing.Mapping[builtins.str, _Job_20ffcf45]) -> None:
        '''
        :param jobs: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addJobs", [jobs]))

    @jsii.member(jsii_name="on")
    def on(
        self,
        *,
        check_run: typing.Optional[_CheckRunOptions_66af1ceb] = None,
        check_suite: typing.Optional[_CheckSuiteOptions_6a122376] = None,
        create: typing.Optional[_CreateOptions_6247308d] = None,
        delete: typing.Optional[_DeleteOptions_c46578d4] = None,
        deployment: typing.Optional[_DeploymentOptions_0bea6580] = None,
        deployment_status: typing.Optional[_DeploymentStatusOptions_f9cbd32b] = None,
        fork: typing.Optional[_ForkOptions_0437229d] = None,
        gollum: typing.Optional[_GollumOptions_1acffea2] = None,
        issue_comment: typing.Optional[_IssueCommentOptions_b551b1e5] = None,
        issues: typing.Optional[_IssuesOptions_dd89885c] = None,
        label: typing.Optional[_LabelOptions_ca474a61] = None,
        milestone: typing.Optional[_MilestoneOptions_6f9d8b6f] = None,
        page_build: typing.Optional[_PageBuildOptions_c30eafce] = None,
        project: typing.Optional[_ProjectOptions_50d963ea] = None,
        project_card: typing.Optional[_ProjectCardOptions_c89fc28d] = None,
        project_column: typing.Optional[_ProjectColumnOptions_25a462f6] = None,
        public: typing.Optional[_PublicOptions_2c3a3b94] = None,
        pull_request: typing.Optional[_PullRequestOptions_b051b0c9] = None,
        pull_request_review: typing.Optional[_PullRequestReviewOptions_27fd8e95] = None,
        pull_request_review_comment: typing.Optional[_PullRequestReviewCommentOptions_85235a68] = None,
        pull_request_target: typing.Optional[_PullRequestTargetOptions_81011bb1] = None,
        push: typing.Optional[_PushOptions_63e1c4f2] = None,
        registry_package: typing.Optional[_RegistryPackageOptions_781d5ac7] = None,
        release: typing.Optional[_ReleaseOptions_d152186d] = None,
        repository_dispatch: typing.Optional[_RepositoryDispatchOptions_d75e9903] = None,
        schedule: typing.Optional[typing.Sequence[_CronScheduleOptions_7724cd93]] = None,
        status: typing.Optional[_StatusOptions_aa35df44] = None,
        watch: typing.Optional[_WatchOptions_d33f5d00] = None,
        workflow_dispatch: typing.Optional[_WorkflowDispatchOptions_7110ffdc] = None,
        workflow_run: typing.Optional[_WorkflowRunOptions_5a4262c5] = None,
    ) -> None:
        '''
        :param check_run: (experimental) Runs your workflow anytime the check_run event occurs.
        :param check_suite: (experimental) Runs your workflow anytime the check_suite event occurs.
        :param create: (experimental) Runs your workflow anytime someone creates a branch or tag, which triggers the create event.
        :param delete: (experimental) Runs your workflow anytime someone deletes a branch or tag, which triggers the delete event.
        :param deployment: (experimental) Runs your workflow anytime someone creates a deployment, which triggers the deployment event. Deployments created with a commit SHA may not have a Git ref.
        :param deployment_status: (experimental) Runs your workflow anytime a third party provides a deployment status, which triggers the deployment_status event. Deployments created with a commit SHA may not have a Git ref.
        :param fork: (experimental) Runs your workflow anytime when someone forks a repository, which triggers the fork event.
        :param gollum: (experimental) Runs your workflow when someone creates or updates a Wiki page, which triggers the gollum event.
        :param issue_comment: (experimental) Runs your workflow anytime the issue_comment event occurs.
        :param issues: (experimental) Runs your workflow anytime the issues event occurs.
        :param label: (experimental) Runs your workflow anytime the label event occurs.
        :param milestone: (experimental) Runs your workflow anytime the milestone event occurs.
        :param page_build: (experimental) Runs your workflow anytime someone pushes to a GitHub Pages-enabled branch, which triggers the page_build event.
        :param project: (experimental) Runs your workflow anytime the project event occurs.
        :param project_card: (experimental) Runs your workflow anytime the project_card event occurs.
        :param project_column: (experimental) Runs your workflow anytime the project_column event occurs.
        :param public: (experimental) Runs your workflow anytime someone makes a private repository public, which triggers the public event.
        :param pull_request: (experimental) Runs your workflow anytime the pull_request event occurs.
        :param pull_request_review: (experimental) Runs your workflow anytime the pull_request_review event occurs.
        :param pull_request_review_comment: (experimental) Runs your workflow anytime a comment on a pull request's unified diff is modified, which triggers the pull_request_review_comment event.
        :param pull_request_target: (experimental) This event runs in the context of the base of the pull request, rather than in the merge commit as the pull_request event does. This prevents executing unsafe workflow code from the head of the pull request that could alter your repository or steal any secrets you use in your workflow. This event allows you to do things like create workflows that label and comment on pull requests based on the contents of the event payload. WARNING: The ``pull_request_target`` event is granted read/write repository token and can access secrets, even when it is triggered from a fork. Although the workflow runs in the context of the base of the pull request, you should make sure that you do not check out, build, or run untrusted code from the pull request with this event. Additionally, any caches share the same scope as the base branch, and to help prevent cache poisoning, you should not save the cache if there is a possibility that the cache contents were altered.
        :param push: (experimental) Runs your workflow when someone pushes to a repository branch, which triggers the push event.
        :param registry_package: (experimental) Runs your workflow anytime a package is published or updated.
        :param release: (experimental) Runs your workflow anytime the release event occurs.
        :param repository_dispatch: (experimental) You can use the GitHub API to trigger a webhook event called repository_dispatch when you want to trigger a workflow for activity that happens outside of GitHub.
        :param schedule: (experimental) You can schedule a workflow to run at specific UTC times using POSIX cron syntax. Scheduled workflows run on the latest commit on the default or base branch. The shortest interval you can run scheduled workflows is once every 5 minutes.
        :param status: (experimental) Runs your workflow anytime the status of a Git commit changes, which triggers the status event.
        :param watch: (experimental) Runs your workflow anytime the watch event occurs.
        :param workflow_dispatch: (experimental) You can configure custom-defined input properties, default input values, and required inputs for the event directly in your workflow. When the workflow runs, you can access the input values in the github.event.inputs context.
        :param workflow_run: (experimental) This event occurs when a workflow run is requested or completed, and allows you to execute a workflow based on the finished result of another workflow. A workflow run is triggered regardless of the result of the previous workflow.

        :stability: experimental
        '''
        events = _Triggers_e9ae7617(
            check_run=check_run,
            check_suite=check_suite,
            create=create,
            delete=delete,
            deployment=deployment,
            deployment_status=deployment_status,
            fork=fork,
            gollum=gollum,
            issue_comment=issue_comment,
            issues=issues,
            label=label,
            milestone=milestone,
            page_build=page_build,
            project=project,
            project_card=project_card,
            project_column=project_column,
            public=public,
            pull_request=pull_request,
            pull_request_review=pull_request_review,
            pull_request_review_comment=pull_request_review_comment,
            pull_request_target=pull_request_target,
            push=push,
            registry_package=registry_package,
            release=release,
            repository_dispatch=repository_dispatch,
            schedule=schedule,
            status=status,
            watch=watch,
            workflow_dispatch=workflow_dispatch,
            workflow_run=workflow_run,
        )

        return typing.cast(None, jsii.invoke(self, "on", [events]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="file")
    def file(self) -> typing.Optional[_YamlFile_909731b0]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_YamlFile_909731b0], jsii.get(self, "file"))


@jsii.data_type(
    jsii_type="projen.github.GithubWorkflowOptions",
    jsii_struct_bases=[],
    name_mapping={"force": "force"},
)
class GithubWorkflowOptions:
    def __init__(self, *, force: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param force: (experimental) Force the creation of the workflow even if ``workflows`` is disabled in ``GitHub``. Default: false

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if force is not None:
            self._values["force"] = force

    @builtins.property
    def force(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Force the creation of the workflow even if ``workflows`` is disabled in ``GitHub``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("force")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubWorkflowOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Mergify(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.Mergify",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        *,
        rules: typing.Optional[typing.Sequence["MergifyRule"]] = None,
    ) -> None:
        '''
        :param github: -
        :param rules: 

        :stability: experimental
        '''
        options = MergifyOptions(rules=rules)

        jsii.create(Mergify, self, [github, options])

    @jsii.member(jsii_name="addRule")
    def add_rule(
        self,
        *,
        actions: typing.Mapping[builtins.str, typing.Any],
        conditions: typing.Sequence[typing.Union[builtins.str, "MergifyConditionalOperator"]],
        name: builtins.str,
    ) -> None:
        '''
        :param actions: (experimental) A dictionary made of Actions that will be executed on the matching pull requests.
        :param conditions: (experimental) A list of Conditions string that must match against the pull request for the rule to be applied.
        :param name: (experimental) The name of the rule. This is not used by the engine directly, but is used when reporting information about a rule.

        :stability: experimental
        '''
        rule = MergifyRule(actions=actions, conditions=conditions, name=name)

        return typing.cast(None, jsii.invoke(self, "addRule", [rule]))


@jsii.data_type(
    jsii_type="projen.github.MergifyConditionalOperator",
    jsii_struct_bases=[],
    name_mapping={"and_": "and", "or_": "or"},
)
class MergifyConditionalOperator:
    def __init__(
        self,
        *,
        and_: typing.Optional[typing.Sequence[typing.Union[builtins.str, "MergifyConditionalOperator"]]] = None,
        or_: typing.Optional[typing.Sequence[typing.Union[builtins.str, "MergifyConditionalOperator"]]] = None,
    ) -> None:
        '''(experimental) The Mergify conditional operators that can be used are: ``or`` and ``and``.

        Note: The number of nested conditions is limited to 3.

        :param and_: 
        :param or_: 

        :see: https://docs.mergify.io/conditions/#combining-conditions-with-operators
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if and_ is not None:
            self._values["and_"] = and_
        if or_ is not None:
            self._values["or_"] = or_

    @builtins.property
    def and_(
        self,
    ) -> typing.Optional[typing.List[typing.Union[builtins.str, "MergifyConditionalOperator"]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("and_")
        return typing.cast(typing.Optional[typing.List[typing.Union[builtins.str, "MergifyConditionalOperator"]]], result)

    @builtins.property
    def or_(
        self,
    ) -> typing.Optional[typing.List[typing.Union[builtins.str, "MergifyConditionalOperator"]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("or_")
        return typing.cast(typing.Optional[typing.List[typing.Union[builtins.str, "MergifyConditionalOperator"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MergifyConditionalOperator(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.MergifyOptions",
    jsii_struct_bases=[],
    name_mapping={"rules": "rules"},
)
class MergifyOptions:
    def __init__(
        self,
        *,
        rules: typing.Optional[typing.Sequence["MergifyRule"]] = None,
    ) -> None:
        '''
        :param rules: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if rules is not None:
            self._values["rules"] = rules

    @builtins.property
    def rules(self) -> typing.Optional[typing.List["MergifyRule"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List["MergifyRule"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MergifyOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.MergifyRule",
    jsii_struct_bases=[],
    name_mapping={"actions": "actions", "conditions": "conditions", "name": "name"},
)
class MergifyRule:
    def __init__(
        self,
        *,
        actions: typing.Mapping[builtins.str, typing.Any],
        conditions: typing.Sequence[typing.Union[builtins.str, MergifyConditionalOperator]],
        name: builtins.str,
    ) -> None:
        '''
        :param actions: (experimental) A dictionary made of Actions that will be executed on the matching pull requests.
        :param conditions: (experimental) A list of Conditions string that must match against the pull request for the rule to be applied.
        :param name: (experimental) The name of the rule. This is not used by the engine directly, but is used when reporting information about a rule.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "actions": actions,
            "conditions": conditions,
            "name": name,
        }

    @builtins.property
    def actions(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) A dictionary made of Actions that will be executed on the matching pull requests.

        :see: https://docs.mergify.io/actions/#actions
        :stability: experimental
        '''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def conditions(
        self,
    ) -> typing.List[typing.Union[builtins.str, MergifyConditionalOperator]]:
        '''(experimental) A list of Conditions string that must match against the pull request for the rule to be applied.

        :see: https://docs.mergify.io/conditions/#conditions
        :stability: experimental
        '''
        result = self._values.get("conditions")
        assert result is not None, "Required property 'conditions' is missing"
        return typing.cast(typing.List[typing.Union[builtins.str, MergifyConditionalOperator]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the rule.

        This is not used by the engine directly,
        but is used when reporting information about a rule.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MergifyRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PullRequestTemplate(
    _TextFile_4a74808c,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.PullRequestTemplate",
):
    '''(experimental) Template for GitHub pull requests.

    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        *,
        lines: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param github: -
        :param lines: (experimental) The contents of the template. You can use ``addLine()`` to add additional lines. Default: - a standard default template will be created.

        :stability: experimental
        '''
        options = PullRequestTemplateOptions(lines=lines)

        jsii.create(PullRequestTemplate, self, [github, options])


@jsii.data_type(
    jsii_type="projen.github.PullRequestTemplateOptions",
    jsii_struct_bases=[],
    name_mapping={"lines": "lines"},
)
class PullRequestTemplateOptions:
    def __init__(
        self,
        *,
        lines: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Options for ``PullRequestTemplate``.

        :param lines: (experimental) The contents of the template. You can use ``addLine()`` to add additional lines. Default: - a standard default template will be created.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if lines is not None:
            self._values["lines"] = lines

    @builtins.property
    def lines(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The contents of the template.

        You can use ``addLine()`` to add additional lines.

        :default: - a standard default template will be created.

        :stability: experimental
        '''
        result = self._values.get("lines")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PullRequestTemplateOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Stale(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.Stale",
):
    '''(experimental) Warns and then closes issues and PRs that have had no activity for a specified amount of time.

    The default configuration will:

    - Add a "Stale" label to pull requests after 14 days and closed after 2 days
    - Add a "Stale" label to issues after 60 days and closed after 7 days
    - If a comment is added, the label will be removed and timer is restarted.

    :see: https://github.com/actions/stale
    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        *,
        issues: typing.Optional["StaleBehavior"] = None,
        pull_request: typing.Optional["StaleBehavior"] = None,
    ) -> None:
        '''
        :param github: -
        :param issues: (experimental) How to handle stale issues. Default: - By default, stale issues with no activity will be marked as stale after 60 days and closed within 7 days.
        :param pull_request: (experimental) How to handle stale pull requests. Default: - By default, pull requests with no activity will be marked as stale after 14 days and closed within 2 days with relevant comments.

        :stability: experimental
        '''
        options = StaleOptions(issues=issues, pull_request=pull_request)

        jsii.create(Stale, self, [github, options])


@jsii.data_type(
    jsii_type="projen.github.StaleBehavior",
    jsii_struct_bases=[],
    name_mapping={
        "close_message": "closeMessage",
        "days_before_close": "daysBeforeClose",
        "days_before_stale": "daysBeforeStale",
        "enabled": "enabled",
        "stale_label": "staleLabel",
        "stale_message": "staleMessage",
    },
)
class StaleBehavior:
    def __init__(
        self,
        *,
        close_message: typing.Optional[builtins.str] = None,
        days_before_close: typing.Optional[jsii.Number] = None,
        days_before_stale: typing.Optional[jsii.Number] = None,
        enabled: typing.Optional[builtins.bool] = None,
        stale_label: typing.Optional[builtins.str] = None,
        stale_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Stale behavior.

        :param close_message: (experimental) The comment to add to the issue/PR when it's closed. Default: "Closing this pull request as it hasn't seen activity for a while. Please add a comment
        :param days_before_close: (experimental) Days until the issue/PR is closed after it is marked as "Stale". Set to -1 to disable. Default: -
        :param days_before_stale: (experimental) How many days until the issue or pull request is marked as "Stale". Set to -1 to disable. Default: -
        :param enabled: (experimental) Determines if this behavior is enabled. Same as setting ``daysBeforeStale`` and ``daysBeforeClose`` to ``-1``. Default: true
        :param stale_label: (experimental) The label to apply to the issue/PR when it becomes stale. Default: "Stale"
        :param stale_message: (experimental) The comment to add to the issue/PR when it becomes stale. Default: "This pull request is now marked as stale because hasn't seen activity for a while. Add a comment or it will be closed soon."

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if close_message is not None:
            self._values["close_message"] = close_message
        if days_before_close is not None:
            self._values["days_before_close"] = days_before_close
        if days_before_stale is not None:
            self._values["days_before_stale"] = days_before_stale
        if enabled is not None:
            self._values["enabled"] = enabled
        if stale_label is not None:
            self._values["stale_label"] = stale_label
        if stale_message is not None:
            self._values["stale_message"] = stale_message

    @builtins.property
    def close_message(self) -> typing.Optional[builtins.str]:
        '''(experimental) The comment to add to the issue/PR when it's closed.

        :default: "Closing this pull request as it hasn't seen activity for a while. Please add a comment

        :stability: experimental
        :mentioning: a maintainer when you are ready to continue."
        '''
        result = self._values.get("close_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def days_before_close(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Days until the issue/PR is closed after it is marked as "Stale".

        Set to -1 to disable.

        :default: -

        :stability: experimental
        '''
        result = self._values.get("days_before_close")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def days_before_stale(self) -> typing.Optional[jsii.Number]:
        '''(experimental) How many days until the issue or pull request is marked as "Stale".

        Set to -1 to disable.

        :default: -

        :stability: experimental
        '''
        result = self._values.get("days_before_stale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Determines if this behavior is enabled.

        Same as setting ``daysBeforeStale`` and ``daysBeforeClose`` to ``-1``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to the issue/PR when it becomes stale.

        :default: "Stale"

        :stability: experimental
        '''
        result = self._values.get("stale_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stale_message(self) -> typing.Optional[builtins.str]:
        '''(experimental) The comment to add to the issue/PR when it becomes stale.

        :default: "This pull request is now marked as stale because hasn't seen activity for a while. Add a comment or it will be closed soon."

        :stability: experimental
        '''
        result = self._values.get("stale_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaleBehavior(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.StaleOptions",
    jsii_struct_bases=[],
    name_mapping={"issues": "issues", "pull_request": "pullRequest"},
)
class StaleOptions:
    def __init__(
        self,
        *,
        issues: typing.Optional[StaleBehavior] = None,
        pull_request: typing.Optional[StaleBehavior] = None,
    ) -> None:
        '''(experimental) Options for ``Stale``.

        :param issues: (experimental) How to handle stale issues. Default: - By default, stale issues with no activity will be marked as stale after 60 days and closed within 7 days.
        :param pull_request: (experimental) How to handle stale pull requests. Default: - By default, pull requests with no activity will be marked as stale after 14 days and closed within 2 days with relevant comments.

        :stability: experimental
        '''
        if isinstance(issues, dict):
            issues = StaleBehavior(**issues)
        if isinstance(pull_request, dict):
            pull_request = StaleBehavior(**pull_request)
        self._values: typing.Dict[str, typing.Any] = {}
        if issues is not None:
            self._values["issues"] = issues
        if pull_request is not None:
            self._values["pull_request"] = pull_request

    @builtins.property
    def issues(self) -> typing.Optional[StaleBehavior]:
        '''(experimental) How to handle stale issues.

        :default:

        - By default, stale issues with no activity will be marked as
        stale after 60 days and closed within 7 days.

        :stability: experimental
        '''
        result = self._values.get("issues")
        return typing.cast(typing.Optional[StaleBehavior], result)

    @builtins.property
    def pull_request(self) -> typing.Optional[StaleBehavior]:
        '''(experimental) How to handle stale pull requests.

        :default:

        - By default, pull requests with no activity will be marked as
        stale after 14 days and closed within 2 days with relevant comments.

        :stability: experimental
        '''
        result = self._values.get("pull_request")
        return typing.cast(typing.Optional[StaleBehavior], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TaskWorkflow(
    GithubWorkflow,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.TaskWorkflow",
):
    '''(experimental) A GitHub workflow for common build tasks within a project.

    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        *,
        name: builtins.str,
        permissions: _JobPermissions_3b5b53dc,
        task: _Task_fb843092,
        artifacts_directory: typing.Optional[builtins.str] = None,
        checkout_with: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        condition: typing.Optional[builtins.str] = None,
        container: typing.Optional[_ContainerOptions_f50907af] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        job_id: typing.Optional[builtins.str] = None,
        outputs: typing.Optional[typing.Mapping[builtins.str, _JobStepOutput_acebe827]] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_checkout_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        triggers: typing.Optional[_Triggers_e9ae7617] = None,
    ) -> None:
        '''
        :param github: -
        :param name: (experimental) The workflow name.
        :param permissions: (experimental) Permissions for the build job.
        :param task: (experimental) The main task to be executed.
        :param artifacts_directory: (experimental) A directory name which contains artifacts to be uploaded (e.g. ``dist``). If this is set, the contents of this directory will be uploaded as an artifact at the end of the workflow run, even if other steps fail. Default: - not set
        :param checkout_with: (experimental) Override for the ``with`` property of the source code checkout step. Default: - not set
        :param condition: (experimental) Adds an 'if' condition to the workflow.
        :param container: Default: - default image
        :param env: (experimental) Workflow environment variables. Default: {}
        :param job_id: (experimental) The primary job id. Default: "build"
        :param outputs: (experimental) Mapping of job output names to values/expressions. Default: {}
        :param post_build_steps: (experimental) Actions to run after the main build step. Default: - not set
        :param pre_build_steps: (experimental) Steps to run before the main build step. Default: - not set
        :param pre_checkout_steps: (experimental) Initial steps to run before the source code checkout. Default: - not set
        :param triggers: (experimental) The triggers for the workflow. Default: - by default workflows can only be triggered by manually.

        :stability: experimental
        '''
        options = TaskWorkflowOptions(
            name=name,
            permissions=permissions,
            task=task,
            artifacts_directory=artifacts_directory,
            checkout_with=checkout_with,
            condition=condition,
            container=container,
            env=env,
            job_id=job_id,
            outputs=outputs,
            post_build_steps=post_build_steps,
            pre_build_steps=pre_build_steps,
            pre_checkout_steps=pre_checkout_steps,
            triggers=triggers,
        )

        jsii.create(TaskWorkflow, self, [github, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobId")
    def job_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobId"))


@jsii.data_type(
    jsii_type="projen.github.TaskWorkflowOptions",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "permissions": "permissions",
        "task": "task",
        "artifacts_directory": "artifactsDirectory",
        "checkout_with": "checkoutWith",
        "condition": "condition",
        "container": "container",
        "env": "env",
        "job_id": "jobId",
        "outputs": "outputs",
        "post_build_steps": "postBuildSteps",
        "pre_build_steps": "preBuildSteps",
        "pre_checkout_steps": "preCheckoutSteps",
        "triggers": "triggers",
    },
)
class TaskWorkflowOptions:
    def __init__(
        self,
        *,
        name: builtins.str,
        permissions: _JobPermissions_3b5b53dc,
        task: _Task_fb843092,
        artifacts_directory: typing.Optional[builtins.str] = None,
        checkout_with: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        condition: typing.Optional[builtins.str] = None,
        container: typing.Optional[_ContainerOptions_f50907af] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        job_id: typing.Optional[builtins.str] = None,
        outputs: typing.Optional[typing.Mapping[builtins.str, _JobStepOutput_acebe827]] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_checkout_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        triggers: typing.Optional[_Triggers_e9ae7617] = None,
    ) -> None:
        '''
        :param name: (experimental) The workflow name.
        :param permissions: (experimental) Permissions for the build job.
        :param task: (experimental) The main task to be executed.
        :param artifacts_directory: (experimental) A directory name which contains artifacts to be uploaded (e.g. ``dist``). If this is set, the contents of this directory will be uploaded as an artifact at the end of the workflow run, even if other steps fail. Default: - not set
        :param checkout_with: (experimental) Override for the ``with`` property of the source code checkout step. Default: - not set
        :param condition: (experimental) Adds an 'if' condition to the workflow.
        :param container: Default: - default image
        :param env: (experimental) Workflow environment variables. Default: {}
        :param job_id: (experimental) The primary job id. Default: "build"
        :param outputs: (experimental) Mapping of job output names to values/expressions. Default: {}
        :param post_build_steps: (experimental) Actions to run after the main build step. Default: - not set
        :param pre_build_steps: (experimental) Steps to run before the main build step. Default: - not set
        :param pre_checkout_steps: (experimental) Initial steps to run before the source code checkout. Default: - not set
        :param triggers: (experimental) The triggers for the workflow. Default: - by default workflows can only be triggered by manually.

        :stability: experimental
        '''
        if isinstance(permissions, dict):
            permissions = _JobPermissions_3b5b53dc(**permissions)
        if isinstance(container, dict):
            container = _ContainerOptions_f50907af(**container)
        if isinstance(triggers, dict):
            triggers = _Triggers_e9ae7617(**triggers)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "permissions": permissions,
            "task": task,
        }
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if checkout_with is not None:
            self._values["checkout_with"] = checkout_with
        if condition is not None:
            self._values["condition"] = condition
        if container is not None:
            self._values["container"] = container
        if env is not None:
            self._values["env"] = env
        if job_id is not None:
            self._values["job_id"] = job_id
        if outputs is not None:
            self._values["outputs"] = outputs
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if pre_build_steps is not None:
            self._values["pre_build_steps"] = pre_build_steps
        if pre_checkout_steps is not None:
            self._values["pre_checkout_steps"] = pre_checkout_steps
        if triggers is not None:
            self._values["triggers"] = triggers

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The workflow name.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permissions(self) -> _JobPermissions_3b5b53dc:
        '''(experimental) Permissions for the build job.

        :stability: experimental
        '''
        result = self._values.get("permissions")
        assert result is not None, "Required property 'permissions' is missing"
        return typing.cast(_JobPermissions_3b5b53dc, result)

    @builtins.property
    def task(self) -> _Task_fb843092:
        '''(experimental) The main task to be executed.

        :stability: experimental
        '''
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(_Task_fb843092, result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory name which contains artifacts to be uploaded (e.g. ``dist``). If this is set, the contents of this directory will be uploaded as an artifact at the end of the workflow run, even if other steps fail.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def checkout_with(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Override for the ``with`` property of the source code checkout step.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("checkout_with")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) Adds an 'if' condition to the workflow.

        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def container(self) -> typing.Optional[_ContainerOptions_f50907af]:
        '''
        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("container")
        return typing.cast(typing.Optional[_ContainerOptions_f50907af], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Workflow environment variables.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def job_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The primary job id.

        :default: "build"

        :stability: experimental
        '''
        result = self._values.get("job_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outputs(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _JobStepOutput_acebe827]]:
        '''(experimental) Mapping of job output names to values/expressions.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("outputs")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _JobStepOutput_acebe827]], result)

    @builtins.property
    def post_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Actions to run after the main build step.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def pre_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to run before the main build step.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("pre_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def pre_checkout_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Initial steps to run before the source code checkout.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("pre_checkout_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def triggers(self) -> typing.Optional[_Triggers_e9ae7617]:
        '''(experimental) The triggers for the workflow.

        :default: - by default workflows can only be triggered by manually.

        :stability: experimental
        '''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[_Triggers_e9ae7617], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskWorkflowOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.github.VersioningStrategy")
class VersioningStrategy(enum.Enum):
    '''(experimental) The strategy to use when edits manifest and lock files.

    :stability: experimental
    '''

    LOCKFILE_ONLY = "LOCKFILE_ONLY"
    '''(experimental) Only create pull requests to update lockfiles updates.

    Ignore any new
    versions that would require package manifest changes.

    :stability: experimental
    '''
    AUTO = "AUTO"
    '''(experimental) - For apps, the version requirements are increased.

    - For libraries, the range of versions is widened.

    :stability: experimental
    '''
    WIDEN = "WIDEN"
    '''(experimental) Relax the version requirement to include both the new and old version, when possible.

    :stability: experimental
    '''
    INCREASE = "INCREASE"
    '''(experimental) Always increase the version requirement to match the new version.

    :stability: experimental
    '''
    INCREASE_IF_NECESSARY = "INCREASE_IF_NECESSARY"
    '''(experimental) Increase the version requirement only when required by the new version.

    :stability: experimental
    '''


__all__ = [
    "AutoApprove",
    "AutoApproveOptions",
    "AutoMerge",
    "AutoMergeOptions",
    "Dependabot",
    "DependabotIgnore",
    "DependabotOptions",
    "DependabotRegistry",
    "DependabotRegistryType",
    "DependabotScheduleInterval",
    "GitHub",
    "GitHubOptions",
    "GithubWorkflow",
    "GithubWorkflowOptions",
    "Mergify",
    "MergifyConditionalOperator",
    "MergifyOptions",
    "MergifyRule",
    "PullRequestTemplate",
    "PullRequestTemplateOptions",
    "Stale",
    "StaleBehavior",
    "StaleOptions",
    "TaskWorkflow",
    "TaskWorkflowOptions",
    "VersioningStrategy",
]

publication.publish()
