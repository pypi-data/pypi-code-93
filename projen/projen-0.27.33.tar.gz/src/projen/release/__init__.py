import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import Component as _Component_2b0ad27f, Project as _Project_57d89203
from ..github.workflows import Job as _Job_20ffcf45, JobStep as _JobStep_c3287c05
from ..tasks import Task as _Task_fb843092


@jsii.data_type(
    jsii_type="projen.release.BranchOptions",
    jsii_struct_bases=[],
    name_mapping={
        "major_version": "majorVersion",
        "prerelease": "prerelease",
        "workflow_name": "workflowName",
    },
)
class BranchOptions:
    def __init__(
        self,
        *,
        major_version: jsii.Number,
        prerelease: typing.Optional[builtins.str] = None,
        workflow_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for a release branch.

        :param major_version: (experimental) The major versions released from this branch.
        :param prerelease: (experimental) Bump the version as a pre-release tag. Default: - normal releases
        :param workflow_name: (experimental) The name of the release workflow. Default: "release-BRANCH"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "major_version": major_version,
        }
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if workflow_name is not None:
            self._values["workflow_name"] = workflow_name

    @builtins.property
    def major_version(self) -> jsii.Number:
        '''(experimental) The major versions released from this branch.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        assert result is not None, "Required property 'major_version' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump the version as a pre-release tag.

        :default: - normal releases

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the release workflow.

        :default: "release-BRANCH"

        :stability: experimental
        '''
        result = self._values.get("workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.GitHubReleasesPublishOptions",
    jsii_struct_bases=[],
    name_mapping={"changelog_file": "changelogFile", "version_file": "versionFile"},
)
class GitHubReleasesPublishOptions:
    def __init__(
        self,
        *,
        changelog_file: builtins.str,
        version_file: builtins.str,
    ) -> None:
        '''(experimental) Publishing options for GitHub releases.

        :param changelog_file: (experimental) The location of an .md file that includes the changelog for the release.
        :param version_file: (experimental) The location of a text file (relative to ``dist/``) that contains the version number.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "changelog_file": changelog_file,
            "version_file": version_file,
        }

    @builtins.property
    def changelog_file(self) -> builtins.str:
        '''(experimental) The location of an .md file that includes the changelog for the release.

        :stability: experimental

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            changelog.md
        '''
        result = self._values.get("changelog_file")
        assert result is not None, "Required property 'changelog_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version_file(self) -> builtins.str:
        '''(experimental) The location of a text file (relative to ``dist/``) that contains the version number.

        :stability: experimental

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            version.txt
        '''
        result = self._values.get("version_file")
        assert result is not None, "Required property 'version_file' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubReleasesPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.GoPublishOptions",
    jsii_struct_bases=[],
    name_mapping={
        "git_branch": "gitBranch",
        "git_commit_message": "gitCommitMessage",
        "github_repo": "githubRepo",
        "github_token_secret": "githubTokenSecret",
        "git_user_email": "gitUserEmail",
        "git_user_name": "gitUserName",
    },
)
class GoPublishOptions:
    def __init__(
        self,
        *,
        git_branch: typing.Optional[builtins.str] = None,
        git_commit_message: typing.Optional[builtins.str] = None,
        github_repo: typing.Optional[builtins.str] = None,
        github_token_secret: typing.Optional[builtins.str] = None,
        git_user_email: typing.Optional[builtins.str] = None,
        git_user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param git_branch: (deprecated) Branch to push to. Default: "main"
        :param git_commit_message: (deprecated) The commit message. Default: "chore(release): $VERSION"
        :param github_repo: (deprecated) GitHub repository to push to. Default: - derived from ``moduleName``
        :param github_token_secret: (deprecated) The name of the secret that includes a personal GitHub access token used to push to the GitHub repository. Default: "GO_GITHUB_TOKEN"
        :param git_user_email: (deprecated) The email to use in the release git commit. Default: "github-actions
        :param git_user_name: (deprecated) The user name to use for the release git commit. Default: "GitHub Actions"

        :deprecated:

        Use ``GoPublishOptions`` instead.
        export interface JsiiReleaseGo extends GoPublishOptions { }
        /**
        Options for Go releases.

        :stability: deprecated
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if git_branch is not None:
            self._values["git_branch"] = git_branch
        if git_commit_message is not None:
            self._values["git_commit_message"] = git_commit_message
        if github_repo is not None:
            self._values["github_repo"] = github_repo
        if github_token_secret is not None:
            self._values["github_token_secret"] = github_token_secret
        if git_user_email is not None:
            self._values["git_user_email"] = git_user_email
        if git_user_name is not None:
            self._values["git_user_name"] = git_user_name

    @builtins.property
    def git_branch(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Branch to push to.

        :default: "main"

        :stability: deprecated
        '''
        result = self._values.get("git_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_commit_message(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The commit message.

        :default: "chore(release): $VERSION"

        :stability: deprecated
        '''
        result = self._values.get("git_commit_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def github_repo(self) -> typing.Optional[builtins.str]:
        '''(deprecated) GitHub repository to push to.

        :default: - derived from ``moduleName``

        :stability: deprecated
        '''
        result = self._values.get("github_repo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def github_token_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of the secret that includes a personal GitHub access token used to push to the GitHub repository.

        :default: "GO_GITHUB_TOKEN"

        :stability: deprecated
        '''
        result = self._values.get("github_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_user_email(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The email to use in the release git commit.

        :default: "github-actions

        :stability: deprecated
        :github: .com"
        '''
        result = self._values.get("git_user_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_user_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The user name to use for the release git commit.

        :default: "GitHub Actions"

        :stability: deprecated
        '''
        result = self._values.get("git_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.MavenPublishOptions",
    jsii_struct_bases=[],
    name_mapping={
        "maven_endpoint": "mavenEndpoint",
        "maven_gpg_private_key_passphrase": "mavenGpgPrivateKeyPassphrase",
        "maven_gpg_private_key_secret": "mavenGpgPrivateKeySecret",
        "maven_password": "mavenPassword",
        "maven_repository_url": "mavenRepositoryUrl",
        "maven_server_id": "mavenServerId",
        "maven_staging_profile_id": "mavenStagingProfileId",
        "maven_username": "mavenUsername",
    },
)
class MavenPublishOptions:
    def __init__(
        self,
        *,
        maven_endpoint: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_passphrase: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_secret: typing.Optional[builtins.str] = None,
        maven_password: typing.Optional[builtins.str] = None,
        maven_repository_url: typing.Optional[builtins.str] = None,
        maven_server_id: typing.Optional[builtins.str] = None,
        maven_staging_profile_id: typing.Optional[builtins.str] = None,
        maven_username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for Maven releases.

        :param maven_endpoint: (experimental) URL of Nexus repository. if not set, defaults to https://oss.sonatype.org Default: "https://oss.sonatype.org"
        :param maven_gpg_private_key_passphrase: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages
        :param maven_gpg_private_key_secret: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages
        :param maven_password: (experimental) GitHub secret name which contains the Password for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages
        :param maven_repository_url: (experimental) Deployment repository when not deploying to Maven Central. Default: - not set
        :param maven_server_id: (experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub). Default: "ossrh" (Maven Central) or "github" when using GitHub Packages
        :param maven_staging_profile_id: (experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521). Default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages
        :param maven_username: (experimental) GitHub secret name which contains the Username for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if maven_endpoint is not None:
            self._values["maven_endpoint"] = maven_endpoint
        if maven_gpg_private_key_passphrase is not None:
            self._values["maven_gpg_private_key_passphrase"] = maven_gpg_private_key_passphrase
        if maven_gpg_private_key_secret is not None:
            self._values["maven_gpg_private_key_secret"] = maven_gpg_private_key_secret
        if maven_password is not None:
            self._values["maven_password"] = maven_password
        if maven_repository_url is not None:
            self._values["maven_repository_url"] = maven_repository_url
        if maven_server_id is not None:
            self._values["maven_server_id"] = maven_server_id
        if maven_staging_profile_id is not None:
            self._values["maven_staging_profile_id"] = maven_staging_profile_id
        if maven_username is not None:
            self._values["maven_username"] = maven_username

    @builtins.property
    def maven_endpoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) URL of Nexus repository.

        if not set, defaults to https://oss.sonatype.org

        :default: "https://oss.sonatype.org"

        :stability: experimental
        '''
        result = self._values.get("maven_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_gpg_private_key_passphrase(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the GPG private key or file that includes it.

        This is used to sign your Maven packages. See instructions.

        :default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages

        :see: https://github.com/aws/jsii-release#maven
        :stability: experimental
        '''
        result = self._values.get("maven_gpg_private_key_passphrase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_gpg_private_key_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the GPG private key or file that includes it.

        This is used to sign your Maven
        packages. See instructions.

        :default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages

        :see: https://github.com/aws/jsii-release#maven
        :stability: experimental
        '''
        result = self._values.get("maven_gpg_private_key_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_password(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Password for maven repository.

        For Maven Central, you will need to Create JIRA account and then request a
        new project (see links).

        :default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages

        :see: https://issues.sonatype.org/secure/CreateIssue.jspa?issuetype=21&pid=10134
        :stability: experimental
        '''
        result = self._values.get("maven_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_repository_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Deployment repository when not deploying to Maven Central.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("maven_repository_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_server_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub).

        :default: "ossrh" (Maven Central) or "github" when using GitHub Packages

        :stability: experimental
        '''
        result = self._values.get("maven_server_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_staging_profile_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521).

        :default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages

        :stability: experimental
        '''
        result = self._values.get("maven_staging_profile_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_username(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Username for maven repository.

        For Maven Central, you will need to Create JIRA account and then request a
        new project (see links).

        :default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages

        :see: https://issues.sonatype.org/secure/CreateIssue.jspa?issuetype=21&pid=10134
        :stability: experimental
        '''
        result = self._values.get("maven_username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MavenPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.NpmPublishOptions",
    jsii_struct_bases=[],
    name_mapping={
        "dist_tag": "distTag",
        "npm_token_secret": "npmTokenSecret",
        "registry": "registry",
    },
)
class NpmPublishOptions:
    def __init__(
        self,
        *,
        dist_tag: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for npm release.

        :param dist_tag: (experimental) Tags can be used to provide an alias instead of version numbers. For example, a project might choose to have multiple streams of development and use a different tag for each stream, e.g., stable, beta, dev, canary. By default, the ``latest`` tag is used by npm to identify the current version of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>`` specifier) installs the latest tag. Typically, projects only use the ``latest`` tag for stable release versions, and use other tags for unstable versions such as prereleases. The ``next`` tag is used by some projects to identify the upcoming version. Default: "latest"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.
        :param registry: (experimental) The domain name of the npm package registry. To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In this if ``npmTokenSecret`` is not specified, it will default to ``GITHUB_TOKEN`` which means that you will be able to publish to the repository's package store. In this case, make sure ``repositoryUrl`` is correctly defined. Default: "registry.npmjs.org"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if dist_tag is not None:
            self._values["dist_tag"] = dist_tag
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if registry is not None:
            self._values["registry"] = registry

    @builtins.property
    def dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) Tags can be used to provide an alias instead of version numbers.

        For example, a project might choose to have multiple streams of development
        and use a different tag for each stream, e.g., stable, beta, dev, canary.

        By default, the ``latest`` tag is used by npm to identify the current version
        of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>``
        specifier) installs the latest tag. Typically, projects only use the
        ``latest`` tag for stable release versions, and use other tags for unstable
        versions such as prereleases.

        The ``next`` tag is used by some projects to identify the upcoming version.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''(experimental) The domain name of the npm package registry.

        To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In
        this if ``npmTokenSecret`` is not specified, it will default to
        ``GITHUB_TOKEN`` which means that you will be able to publish to the
        repository's package store. In this case, make sure ``repositoryUrl`` is
        correctly defined.

        :default: "registry.npmjs.org"

        :stability: experimental

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            "npm.pkg.github.com"
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NpmPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.NugetPublishOptions",
    jsii_struct_bases=[],
    name_mapping={"nuget_api_key_secret": "nugetApiKeySecret"},
)
class NugetPublishOptions:
    def __init__(
        self,
        *,
        nuget_api_key_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for NuGet releases.

        :param nuget_api_key_secret: (experimental) GitHub secret which contains the API key for NuGet. Default: "NUGET_API_KEY"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if nuget_api_key_secret is not None:
            self._values["nuget_api_key_secret"] = nuget_api_key_secret

    @builtins.property
    def nuget_api_key_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the API key for NuGet.

        :default: "NUGET_API_KEY"

        :stability: experimental
        '''
        result = self._values.get("nuget_api_key_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NugetPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Publisher(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.release.Publisher",
):
    '''(experimental) Implements GitHub jobs for publishing modules to package managers.

    Under the hood, it uses https://github.com/aws/jsii-release

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        artifact_name: builtins.str,
        build_job_id: builtins.str,
        condition: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param artifact_name: (experimental) The name of the artifact to download (e.g. ``dist``). The artifact is expected to include a subdirectory for each release target: ``go`` (GitHub), ``dotnet`` (NuGet), ``java`` (Maven), ``js`` (npm), ``python`` (PyPI).
        :param build_job_id: (experimental) The job ID that produces the build artifacts. All publish jobs will take a dependency on this job.
        :param condition: (experimental) A GitHub workflow expression used as a condition for publishers. Default: - no condition
        :param jsii_release_version: (experimental) Version requirement for ``jsii-release``. Default: "latest"

        :stability: experimental
        '''
        options = PublisherOptions(
            artifact_name=artifact_name,
            build_job_id=build_job_id,
            condition=condition,
            jsii_release_version=jsii_release_version,
        )

        jsii.create(Publisher, self, [project, options])

    @jsii.member(jsii_name="publishToGitHubReleases")
    def publish_to_git_hub_releases(
        self,
        *,
        changelog_file: builtins.str,
        version_file: builtins.str,
    ) -> None:
        '''(experimental) Creates a GitHub Release.

        :param changelog_file: (experimental) The location of an .md file that includes the changelog for the release.
        :param version_file: (experimental) The location of a text file (relative to ``dist/``) that contains the version number.

        :stability: experimental
        '''
        options = GitHubReleasesPublishOptions(
            changelog_file=changelog_file, version_file=version_file
        )

        return typing.cast(None, jsii.invoke(self, "publishToGitHubReleases", [options]))

    @jsii.member(jsii_name="publishToGo")
    def publish_to_go(
        self,
        *,
        git_branch: typing.Optional[builtins.str] = None,
        git_commit_message: typing.Optional[builtins.str] = None,
        github_repo: typing.Optional[builtins.str] = None,
        github_token_secret: typing.Optional[builtins.str] = None,
        git_user_email: typing.Optional[builtins.str] = None,
        git_user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Adds a go publishing job.

        :param git_branch: (deprecated) Branch to push to. Default: "main"
        :param git_commit_message: (deprecated) The commit message. Default: "chore(release): $VERSION"
        :param github_repo: (deprecated) GitHub repository to push to. Default: - derived from ``moduleName``
        :param github_token_secret: (deprecated) The name of the secret that includes a personal GitHub access token used to push to the GitHub repository. Default: "GO_GITHUB_TOKEN"
        :param git_user_email: (deprecated) The email to use in the release git commit. Default: "github-actions
        :param git_user_name: (deprecated) The user name to use for the release git commit. Default: "GitHub Actions"

        :stability: experimental
        '''
        options = GoPublishOptions(
            git_branch=git_branch,
            git_commit_message=git_commit_message,
            github_repo=github_repo,
            github_token_secret=github_token_secret,
            git_user_email=git_user_email,
            git_user_name=git_user_name,
        )

        return typing.cast(None, jsii.invoke(self, "publishToGo", [options]))

    @jsii.member(jsii_name="publishToMaven")
    def publish_to_maven(
        self,
        *,
        maven_endpoint: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_passphrase: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_secret: typing.Optional[builtins.str] = None,
        maven_password: typing.Optional[builtins.str] = None,
        maven_repository_url: typing.Optional[builtins.str] = None,
        maven_server_id: typing.Optional[builtins.str] = None,
        maven_staging_profile_id: typing.Optional[builtins.str] = None,
        maven_username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Publishes artifacts from ``java/**`` to Maven.

        :param maven_endpoint: (experimental) URL of Nexus repository. if not set, defaults to https://oss.sonatype.org Default: "https://oss.sonatype.org"
        :param maven_gpg_private_key_passphrase: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages
        :param maven_gpg_private_key_secret: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages
        :param maven_password: (experimental) GitHub secret name which contains the Password for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages
        :param maven_repository_url: (experimental) Deployment repository when not deploying to Maven Central. Default: - not set
        :param maven_server_id: (experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub). Default: "ossrh" (Maven Central) or "github" when using GitHub Packages
        :param maven_staging_profile_id: (experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521). Default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages
        :param maven_username: (experimental) GitHub secret name which contains the Username for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages

        :stability: experimental
        '''
        options = MavenPublishOptions(
            maven_endpoint=maven_endpoint,
            maven_gpg_private_key_passphrase=maven_gpg_private_key_passphrase,
            maven_gpg_private_key_secret=maven_gpg_private_key_secret,
            maven_password=maven_password,
            maven_repository_url=maven_repository_url,
            maven_server_id=maven_server_id,
            maven_staging_profile_id=maven_staging_profile_id,
            maven_username=maven_username,
        )

        return typing.cast(None, jsii.invoke(self, "publishToMaven", [options]))

    @jsii.member(jsii_name="publishToNpm")
    def publish_to_npm(
        self,
        *,
        dist_tag: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Publishes artifacts from ``js/**`` to npm.

        :param dist_tag: (experimental) Tags can be used to provide an alias instead of version numbers. For example, a project might choose to have multiple streams of development and use a different tag for each stream, e.g., stable, beta, dev, canary. By default, the ``latest`` tag is used by npm to identify the current version of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>`` specifier) installs the latest tag. Typically, projects only use the ``latest`` tag for stable release versions, and use other tags for unstable versions such as prereleases. The ``next`` tag is used by some projects to identify the upcoming version. Default: "latest"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.
        :param registry: (experimental) The domain name of the npm package registry. To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In this if ``npmTokenSecret`` is not specified, it will default to ``GITHUB_TOKEN`` which means that you will be able to publish to the repository's package store. In this case, make sure ``repositoryUrl`` is correctly defined. Default: "registry.npmjs.org"

        :stability: experimental
        '''
        options = NpmPublishOptions(
            dist_tag=dist_tag, npm_token_secret=npm_token_secret, registry=registry
        )

        return typing.cast(None, jsii.invoke(self, "publishToNpm", [options]))

    @jsii.member(jsii_name="publishToNuget")
    def publish_to_nuget(
        self,
        *,
        nuget_api_key_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Publishes artifacts from ``dotnet/**`` to NuGet Gallery.

        :param nuget_api_key_secret: (experimental) GitHub secret which contains the API key for NuGet. Default: "NUGET_API_KEY"

        :stability: experimental
        '''
        options = NugetPublishOptions(nuget_api_key_secret=nuget_api_key_secret)

        return typing.cast(None, jsii.invoke(self, "publishToNuget", [options]))

    @jsii.member(jsii_name="publishToPyPi")
    def publish_to_py_pi(
        self,
        *,
        twine_password_secret: typing.Optional[builtins.str] = None,
        twine_registry_url: typing.Optional[builtins.str] = None,
        twine_username_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Publishes wheel artifacts from ``python`` to PyPI.

        :param twine_password_secret: (experimental) The GitHub secret which contains PyPI password. Default: "TWINE_PASSWORD"
        :param twine_registry_url: (experimental) The registry url to use when releasing packages. Default: - twine default
        :param twine_username_secret: (experimental) The GitHub secret which contains PyPI user name. Default: "TWINE_USERNAME"

        :stability: experimental
        '''
        options = PyPiPublishOptions(
            twine_password_secret=twine_password_secret,
            twine_registry_url=twine_registry_url,
            twine_username_secret=twine_username_secret,
        )

        return typing.cast(None, jsii.invoke(self, "publishToPyPi", [options]))

    @jsii.member(jsii_name="render")
    def render(self) -> typing.Mapping[builtins.str, _Job_20ffcf45]:
        '''(experimental) Renders a set of workflow jobs for all the publishers.

        :return: GitHub workflow jobs

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, _Job_20ffcf45], jsii.invoke(self, "render", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactName")
    def artifact_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "artifactName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildJobId")
    def build_job_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "buildJobId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jsiiReleaseVersion")
    def jsii_release_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jsiiReleaseVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="condition")
    def condition(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "condition"))


@jsii.data_type(
    jsii_type="projen.release.PublisherOptions",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_name": "artifactName",
        "build_job_id": "buildJobId",
        "condition": "condition",
        "jsii_release_version": "jsiiReleaseVersion",
    },
)
class PublisherOptions:
    def __init__(
        self,
        *,
        artifact_name: builtins.str,
        build_job_id: builtins.str,
        condition: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``Publisher``.

        :param artifact_name: (experimental) The name of the artifact to download (e.g. ``dist``). The artifact is expected to include a subdirectory for each release target: ``go`` (GitHub), ``dotnet`` (NuGet), ``java`` (Maven), ``js`` (npm), ``python`` (PyPI).
        :param build_job_id: (experimental) The job ID that produces the build artifacts. All publish jobs will take a dependency on this job.
        :param condition: (experimental) A GitHub workflow expression used as a condition for publishers. Default: - no condition
        :param jsii_release_version: (experimental) Version requirement for ``jsii-release``. Default: "latest"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "artifact_name": artifact_name,
            "build_job_id": build_job_id,
        }
        if condition is not None:
            self._values["condition"] = condition
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version

    @builtins.property
    def artifact_name(self) -> builtins.str:
        '''(experimental) The name of the artifact to download (e.g. ``dist``).

        The artifact is expected to include a subdirectory for each release target:
        ``go`` (GitHub), ``dotnet`` (NuGet), ``java`` (Maven), ``js`` (npm), ``python``
        (PyPI).

        :see: https://github.com/aws/jsii-release
        :stability: experimental
        '''
        result = self._values.get("artifact_name")
        assert result is not None, "Required property 'artifact_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_job_id(self) -> builtins.str:
        '''(experimental) The job ID that produces the build artifacts.

        All publish jobs will take a dependency on this job.

        :stability: experimental
        '''
        result = self._values.get("build_job_id")
        assert result is not None, "Required property 'build_job_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) A GitHub workflow expression used as a condition for publishers.

        :default: - no condition

        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement for ``jsii-release``.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PublisherOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.PyPiPublishOptions",
    jsii_struct_bases=[],
    name_mapping={
        "twine_password_secret": "twinePasswordSecret",
        "twine_registry_url": "twineRegistryUrl",
        "twine_username_secret": "twineUsernameSecret",
    },
)
class PyPiPublishOptions:
    def __init__(
        self,
        *,
        twine_password_secret: typing.Optional[builtins.str] = None,
        twine_registry_url: typing.Optional[builtins.str] = None,
        twine_username_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for PyPI release.

        :param twine_password_secret: (experimental) The GitHub secret which contains PyPI password. Default: "TWINE_PASSWORD"
        :param twine_registry_url: (experimental) The registry url to use when releasing packages. Default: - twine default
        :param twine_username_secret: (experimental) The GitHub secret which contains PyPI user name. Default: "TWINE_USERNAME"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if twine_password_secret is not None:
            self._values["twine_password_secret"] = twine_password_secret
        if twine_registry_url is not None:
            self._values["twine_registry_url"] = twine_registry_url
        if twine_username_secret is not None:
            self._values["twine_username_secret"] = twine_username_secret

    @builtins.property
    def twine_password_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The GitHub secret which contains PyPI password.

        :default: "TWINE_PASSWORD"

        :stability: experimental
        '''
        result = self._values.get("twine_password_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def twine_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The registry url to use when releasing packages.

        :default: - twine default

        :stability: experimental
        '''
        result = self._values.get("twine_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def twine_username_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The GitHub secret which contains PyPI user name.

        :default: "TWINE_USERNAME"

        :stability: experimental
        '''
        result = self._values.get("twine_username_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PyPiPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Release(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.release.Release",
):
    '''(experimental) Manages releases (currently through GitHub workflows).

    By default, no branches are released. To add branches, call ``addBranch()``.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        branch: builtins.str,
        task: _Task_fb843092,
        version_file: builtins.str,
        github_release: typing.Optional[builtins.bool] = None,
        antitamper: typing.Optional[builtins.bool] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param branch: (experimental) The default branch name to release from. Use ``majorVersion`` to restrict this branch to only publish releases with a specific major version. You can add additional branches using ``addBranch()``.
        :param task: (experimental) The task to execute in order to create the release artifacts. Artifacts are expected to reside under ``artifactsDirectory`` (defaults to ``dist/``) once build is complete.
        :param version_file: (experimental) A name of a .json file to set the ``version`` field in after a bump.
        :param github_release: (experimental) Create a GitHub release for each release. Default: true
        :param antitamper: (experimental) Checks that after build there are no modified files on git. Default: true
        :param artifacts_directory: (experimental) A directory which will contain artifacts to be published to npm. Default: "dist"
        :param jsii_release_version: (experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (experimental) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_schedule: (experimental) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image

        :stability: experimental
        '''
        options = ReleaseOptions(
            branch=branch,
            task=task,
            version_file=version_file,
            github_release=github_release,
            antitamper=antitamper,
            artifacts_directory=artifacts_directory,
            jsii_release_version=jsii_release_version,
            major_version=major_version,
            post_build_steps=post_build_steps,
            prerelease=prerelease,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_schedule=release_schedule,
            release_workflow_name=release_workflow_name,
            release_workflow_setup_steps=release_workflow_setup_steps,
            workflow_container_image=workflow_container_image,
        )

        jsii.create(Release, self, [project, options])

    @jsii.member(jsii_name="addBranch")
    def add_branch(
        self,
        branch: builtins.str,
        *,
        major_version: jsii.Number,
        prerelease: typing.Optional[builtins.str] = None,
        workflow_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Adds a release branch.

        It is a git branch from which releases are published. If a project has more than one release
        branch, we require that ``majorVersion`` is also specified for the primary branch in order to
        ensure branches always release the correct version.

        :param branch: The branch to monitor (e.g. ``main``, ``v2.x``).
        :param major_version: (experimental) The major versions released from this branch.
        :param prerelease: (experimental) Bump the version as a pre-release tag. Default: - normal releases
        :param workflow_name: (experimental) The name of the release workflow. Default: "release-BRANCH"

        :stability: experimental
        '''
        options = BranchOptions(
            major_version=major_version,
            prerelease=prerelease,
            workflow_name=workflow_name,
        )

        return typing.cast(None, jsii.invoke(self, "addBranch", [branch, options]))

    @jsii.member(jsii_name="addJobs")
    def add_jobs(self, jobs: typing.Mapping[builtins.str, _Job_20ffcf45]) -> None:
        '''(experimental) Adds jobs to all release workflows.

        :param jobs: The jobs to add (name => job).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addJobs", [jobs]))

    @jsii.member(jsii_name="preSynthesize")
    def pre_synthesize(self) -> None:
        '''(experimental) Called before synthesis.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "preSynthesize", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publisher")
    def publisher(self) -> Publisher:
        '''(experimental) Package publisher.

        :stability: experimental
        '''
        return typing.cast(Publisher, jsii.get(self, "publisher"))


@jsii.data_type(
    jsii_type="projen.release.ReleaseProjectOptions",
    jsii_struct_bases=[],
    name_mapping={
        "antitamper": "antitamper",
        "artifacts_directory": "artifactsDirectory",
        "jsii_release_version": "jsiiReleaseVersion",
        "major_version": "majorVersion",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_schedule": "releaseSchedule",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "workflow_container_image": "workflowContainerImage",
    },
)
class ReleaseProjectOptions:
    def __init__(
        self,
        *,
        antitamper: typing.Optional[builtins.bool] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Project options for release.

        :param antitamper: (experimental) Checks that after build there are no modified files on git. Default: true
        :param artifacts_directory: (experimental) A directory which will contain artifacts to be published to npm. Default: "dist"
        :param jsii_release_version: (experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (experimental) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_schedule: (experimental) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if antitamper is not None:
            self._values["antitamper"] = antitamper
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if major_version is not None:
            self._values["major_version"] = major_version
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image

    @builtins.property
    def antitamper(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Checks that after build there are no modified files on git.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("antitamper")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory which will contain artifacts to be published to npm.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def post_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(experimental) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :stability: experimental
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "Release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReleaseProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.JsiiReleaseMaven",
    jsii_struct_bases=[MavenPublishOptions],
    name_mapping={
        "maven_endpoint": "mavenEndpoint",
        "maven_gpg_private_key_passphrase": "mavenGpgPrivateKeyPassphrase",
        "maven_gpg_private_key_secret": "mavenGpgPrivateKeySecret",
        "maven_password": "mavenPassword",
        "maven_repository_url": "mavenRepositoryUrl",
        "maven_server_id": "mavenServerId",
        "maven_staging_profile_id": "mavenStagingProfileId",
        "maven_username": "mavenUsername",
    },
)
class JsiiReleaseMaven(MavenPublishOptions):
    def __init__(
        self,
        *,
        maven_endpoint: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_passphrase: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_secret: typing.Optional[builtins.str] = None,
        maven_password: typing.Optional[builtins.str] = None,
        maven_repository_url: typing.Optional[builtins.str] = None,
        maven_server_id: typing.Optional[builtins.str] = None,
        maven_staging_profile_id: typing.Optional[builtins.str] = None,
        maven_username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param maven_endpoint: (experimental) URL of Nexus repository. if not set, defaults to https://oss.sonatype.org Default: "https://oss.sonatype.org"
        :param maven_gpg_private_key_passphrase: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages
        :param maven_gpg_private_key_secret: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages
        :param maven_password: (experimental) GitHub secret name which contains the Password for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages
        :param maven_repository_url: (experimental) Deployment repository when not deploying to Maven Central. Default: - not set
        :param maven_server_id: (experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub). Default: "ossrh" (Maven Central) or "github" when using GitHub Packages
        :param maven_staging_profile_id: (experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521). Default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages
        :param maven_username: (experimental) GitHub secret name which contains the Username for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages

        :deprecated: Use ``MavenPublishOptions`` instead.

        :stability: deprecated
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if maven_endpoint is not None:
            self._values["maven_endpoint"] = maven_endpoint
        if maven_gpg_private_key_passphrase is not None:
            self._values["maven_gpg_private_key_passphrase"] = maven_gpg_private_key_passphrase
        if maven_gpg_private_key_secret is not None:
            self._values["maven_gpg_private_key_secret"] = maven_gpg_private_key_secret
        if maven_password is not None:
            self._values["maven_password"] = maven_password
        if maven_repository_url is not None:
            self._values["maven_repository_url"] = maven_repository_url
        if maven_server_id is not None:
            self._values["maven_server_id"] = maven_server_id
        if maven_staging_profile_id is not None:
            self._values["maven_staging_profile_id"] = maven_staging_profile_id
        if maven_username is not None:
            self._values["maven_username"] = maven_username

    @builtins.property
    def maven_endpoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) URL of Nexus repository.

        if not set, defaults to https://oss.sonatype.org

        :default: "https://oss.sonatype.org"

        :stability: experimental
        '''
        result = self._values.get("maven_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_gpg_private_key_passphrase(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the GPG private key or file that includes it.

        This is used to sign your Maven packages. See instructions.

        :default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages

        :see: https://github.com/aws/jsii-release#maven
        :stability: experimental
        '''
        result = self._values.get("maven_gpg_private_key_passphrase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_gpg_private_key_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the GPG private key or file that includes it.

        This is used to sign your Maven
        packages. See instructions.

        :default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages

        :see: https://github.com/aws/jsii-release#maven
        :stability: experimental
        '''
        result = self._values.get("maven_gpg_private_key_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_password(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Password for maven repository.

        For Maven Central, you will need to Create JIRA account and then request a
        new project (see links).

        :default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages

        :see: https://issues.sonatype.org/secure/CreateIssue.jspa?issuetype=21&pid=10134
        :stability: experimental
        '''
        result = self._values.get("maven_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_repository_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Deployment repository when not deploying to Maven Central.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("maven_repository_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_server_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub).

        :default: "ossrh" (Maven Central) or "github" when using GitHub Packages

        :stability: experimental
        '''
        result = self._values.get("maven_server_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_staging_profile_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521).

        :default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages

        :stability: experimental
        '''
        result = self._values.get("maven_staging_profile_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_username(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Username for maven repository.

        For Maven Central, you will need to Create JIRA account and then request a
        new project (see links).

        :default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages

        :see: https://issues.sonatype.org/secure/CreateIssue.jspa?issuetype=21&pid=10134
        :stability: experimental
        '''
        result = self._values.get("maven_username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsiiReleaseMaven(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.JsiiReleaseNpm",
    jsii_struct_bases=[NpmPublishOptions],
    name_mapping={
        "dist_tag": "distTag",
        "npm_token_secret": "npmTokenSecret",
        "registry": "registry",
    },
)
class JsiiReleaseNpm(NpmPublishOptions):
    def __init__(
        self,
        *,
        dist_tag: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dist_tag: (experimental) Tags can be used to provide an alias instead of version numbers. For example, a project might choose to have multiple streams of development and use a different tag for each stream, e.g., stable, beta, dev, canary. By default, the ``latest`` tag is used by npm to identify the current version of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>`` specifier) installs the latest tag. Typically, projects only use the ``latest`` tag for stable release versions, and use other tags for unstable versions such as prereleases. The ``next`` tag is used by some projects to identify the upcoming version. Default: "latest"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.
        :param registry: (experimental) The domain name of the npm package registry. To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In this if ``npmTokenSecret`` is not specified, it will default to ``GITHUB_TOKEN`` which means that you will be able to publish to the repository's package store. In this case, make sure ``repositoryUrl`` is correctly defined. Default: "registry.npmjs.org"

        :deprecated: Use ``NpmPublishOptions`` instead.

        :stability: deprecated
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if dist_tag is not None:
            self._values["dist_tag"] = dist_tag
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if registry is not None:
            self._values["registry"] = registry

    @builtins.property
    def dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) Tags can be used to provide an alias instead of version numbers.

        For example, a project might choose to have multiple streams of development
        and use a different tag for each stream, e.g., stable, beta, dev, canary.

        By default, the ``latest`` tag is used by npm to identify the current version
        of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>``
        specifier) installs the latest tag. Typically, projects only use the
        ``latest`` tag for stable release versions, and use other tags for unstable
        versions such as prereleases.

        The ``next`` tag is used by some projects to identify the upcoming version.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''(experimental) The domain name of the npm package registry.

        To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In
        this if ``npmTokenSecret`` is not specified, it will default to
        ``GITHUB_TOKEN`` which means that you will be able to publish to the
        repository's package store. In this case, make sure ``repositoryUrl`` is
        correctly defined.

        :default: "registry.npmjs.org"

        :stability: experimental

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            "npm.pkg.github.com"
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsiiReleaseNpm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.JsiiReleaseNuget",
    jsii_struct_bases=[NugetPublishOptions],
    name_mapping={"nuget_api_key_secret": "nugetApiKeySecret"},
)
class JsiiReleaseNuget(NugetPublishOptions):
    def __init__(
        self,
        *,
        nuget_api_key_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param nuget_api_key_secret: (experimental) GitHub secret which contains the API key for NuGet. Default: "NUGET_API_KEY"

        :deprecated: Use ``NugetPublishOptions`` instead.

        :stability: deprecated
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if nuget_api_key_secret is not None:
            self._values["nuget_api_key_secret"] = nuget_api_key_secret

    @builtins.property
    def nuget_api_key_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the API key for NuGet.

        :default: "NUGET_API_KEY"

        :stability: experimental
        '''
        result = self._values.get("nuget_api_key_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsiiReleaseNuget(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.JsiiReleasePyPi",
    jsii_struct_bases=[PyPiPublishOptions],
    name_mapping={
        "twine_password_secret": "twinePasswordSecret",
        "twine_registry_url": "twineRegistryUrl",
        "twine_username_secret": "twineUsernameSecret",
    },
)
class JsiiReleasePyPi(PyPiPublishOptions):
    def __init__(
        self,
        *,
        twine_password_secret: typing.Optional[builtins.str] = None,
        twine_registry_url: typing.Optional[builtins.str] = None,
        twine_username_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param twine_password_secret: (experimental) The GitHub secret which contains PyPI password. Default: "TWINE_PASSWORD"
        :param twine_registry_url: (experimental) The registry url to use when releasing packages. Default: - twine default
        :param twine_username_secret: (experimental) The GitHub secret which contains PyPI user name. Default: "TWINE_USERNAME"

        :deprecated: Use ``PyPiPublishOptions`` instead.

        :stability: deprecated
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if twine_password_secret is not None:
            self._values["twine_password_secret"] = twine_password_secret
        if twine_registry_url is not None:
            self._values["twine_registry_url"] = twine_registry_url
        if twine_username_secret is not None:
            self._values["twine_username_secret"] = twine_username_secret

    @builtins.property
    def twine_password_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The GitHub secret which contains PyPI password.

        :default: "TWINE_PASSWORD"

        :stability: experimental
        '''
        result = self._values.get("twine_password_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def twine_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The registry url to use when releasing packages.

        :default: - twine default

        :stability: experimental
        '''
        result = self._values.get("twine_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def twine_username_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The GitHub secret which contains PyPI user name.

        :default: "TWINE_USERNAME"

        :stability: experimental
        '''
        result = self._values.get("twine_username_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsiiReleasePyPi(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.ReleaseOptions",
    jsii_struct_bases=[ReleaseProjectOptions],
    name_mapping={
        "antitamper": "antitamper",
        "artifacts_directory": "artifactsDirectory",
        "jsii_release_version": "jsiiReleaseVersion",
        "major_version": "majorVersion",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_schedule": "releaseSchedule",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "workflow_container_image": "workflowContainerImage",
        "branch": "branch",
        "task": "task",
        "version_file": "versionFile",
        "github_release": "githubRelease",
    },
)
class ReleaseOptions(ReleaseProjectOptions):
    def __init__(
        self,
        *,
        antitamper: typing.Optional[builtins.bool] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        branch: builtins.str,
        task: _Task_fb843092,
        version_file: builtins.str,
        github_release: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for ``Release``.

        :param antitamper: (experimental) Checks that after build there are no modified files on git. Default: true
        :param artifacts_directory: (experimental) A directory which will contain artifacts to be published to npm. Default: "dist"
        :param jsii_release_version: (experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (experimental) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_schedule: (experimental) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param branch: (experimental) The default branch name to release from. Use ``majorVersion`` to restrict this branch to only publish releases with a specific major version. You can add additional branches using ``addBranch()``.
        :param task: (experimental) The task to execute in order to create the release artifacts. Artifacts are expected to reside under ``artifactsDirectory`` (defaults to ``dist/``) once build is complete.
        :param version_file: (experimental) A name of a .json file to set the ``version`` field in after a bump.
        :param github_release: (experimental) Create a GitHub release for each release. Default: true

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "branch": branch,
            "task": task,
            "version_file": version_file,
        }
        if antitamper is not None:
            self._values["antitamper"] = antitamper
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if major_version is not None:
            self._values["major_version"] = major_version
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if github_release is not None:
            self._values["github_release"] = github_release

    @builtins.property
    def antitamper(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Checks that after build there are no modified files on git.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("antitamper")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory which will contain artifacts to be published to npm.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def post_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(experimental) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :stability: experimental
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "Release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''(experimental) The default branch name to release from.

        Use ``majorVersion`` to restrict this branch to only publish releases with a
        specific major version.

        You can add additional branches using ``addBranch()``.

        :stability: experimental
        '''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task(self) -> _Task_fb843092:
        '''(experimental) The task to execute in order to create the release artifacts.

        Artifacts are
        expected to reside under ``artifactsDirectory`` (defaults to ``dist/``) once
        build is complete.

        :stability: experimental
        '''
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(_Task_fb843092, result)

    @builtins.property
    def version_file(self) -> builtins.str:
        '''(experimental) A name of a .json file to set the ``version`` field in after a bump.

        :stability: experimental

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            "package.json"
        '''
        result = self._values.get("version_file")
        assert result is not None, "Required property 'version_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def github_release(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a GitHub release for each release.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github_release")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReleaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BranchOptions",
    "GitHubReleasesPublishOptions",
    "GoPublishOptions",
    "JsiiReleaseMaven",
    "JsiiReleaseNpm",
    "JsiiReleaseNuget",
    "JsiiReleasePyPi",
    "MavenPublishOptions",
    "NpmPublishOptions",
    "NugetPublishOptions",
    "Publisher",
    "PublisherOptions",
    "PyPiPublishOptions",
    "Release",
    "ReleaseOptions",
    "ReleaseProjectOptions",
]

publication.publish()
