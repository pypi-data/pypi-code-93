'''
Projen External Project to setup an Awesome List

# p6-projen-project-awesome-list

* [p6-projen-project-awesome-list](#p6-projen-project-awesome-list)

  * [LICENSE](#license)
  * [CI/CD](#cicd)
  * [Distributions](#distributions)
  * [Summary](#summary)
  * [Code of Conduct](#code-of-conduct)
  * [Changes](#changes)
  * [Usage](#usage)
  * [Author](#author)

## LICENSE

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0) [![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/p6m7g8/p6-projen-p)

## CI/CD

![GitHub Build Workflow Status](https://img.shields.io/github/workflow/status/p6m7g8/p6-projen-project-awesome-list/Build) ![GitHub Release Workflow Statuss](https://github.com/p6m7g8/p6-projen-project-awesome-list/workflows/Release/badge.svg)
![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/p6m7g8/p6-projen-project-awesome-list) ![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=p6m7g8_p6-projen-project-awesome-list&metric=alert_status)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/p6m7g8/p6-projen-project-awesome-list) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/p6m7g8/p6-projen-project-awesome-list)

## Distributions

| Method | Version | Daily | Weekly | Monthly | Yearly | Total |
--------| --------| ------| -------| --------| -------|-------|
| NPM      | ![npm](https://img.shields.io/npm/v/p6-projen-project-awesome-list) |       | [![NPM Weekly Downloads](https://img.shields.io/npm/dw/p6-projen-project-awesome-list)](https://img.shields.io/npm/dw/p6-projen-project-awesome-list) | [![NPM Monthly Downloads](https://img.shields.io/npm/dm/p6-projen-project-awesome-list)](https://img.shields.io/npm/dm/p6-projen-project-awesome-list) | [![NPM Yearly Downloads](https://img.shields.io/npm/dy/p6-projen-project-awesome-list)](https://img.shields.io/npm/dy/p6-projen-project-awesome-list) | [![NPM Total Downloads](https://img.shields.io/npm/dt/p6-projen-project-awesome-list)](https://img.shields.io/npm/dt/p6-projen-project-awesome-list) |
| PYPI      | ![PyPI](https://img.shields.io/pypi/v/p6-projen-project-awesome-list) | ![PyPI - Downloads](https://img.shields.io/pypi/dd/p6-projen-project-awesome-list) | ![PyPI - Downloads](https://img.shields.io/pypi/dw/p6-projen-project-awesome-list) | ![PyPI - Downloads](https://img.shields.io/pypi/dm/p6-projen-project-awesome-list)         |       |        |
| Nuget      | ![Nuget](https://img.shields.io/nuget/v/P6m7g8.P6ProjenProjectAwesomeList) |       |        |         |       | ![NuGet Downloads](https://img.shields.io/nuget/dt/P6m7g8.P6ProjenProjectAwesomeList.svg) |
| Maven Central | ![Maven Central](https://img.shields.io/maven-central/v/com.github.p6m7g8/p6-projen-project-awesome-list) |       | ![Maven](https://jitpack.io/v/com.github.p6m7g8/p6-projen-project-awesome-list/week.svg) | ![Maven](https://jitpack.io/v/com.github.p6m7g8/p6-projen-project-awesome-list/month.svg)         |       |        |
| GoLang     |         |       |        |         |       |        |
| Kotlin     |         |       |        |         |       |        |

## Summary

Initializes a repo for use as an [awesome list](https://github.com/topics/awesome-list)

## Code of Conduct

* [Code of Conduct](https://github.com/p6m7g8/.github/blob/master/CODE_OF_CONDUCT.md)

## Changes

* [Change Log](CHANGELOG.md)

## Usage

```shell
projen new --from p6-projen-project-awesome-list
```

## Author

Philip M. Gollucci [pgollucci@p6m7g8.com](mailto:pgollucci@p6m7g8.com)
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

import projen
import projen.github
import projen.javascript
import projen.typescript


class AwesomeList(
    projen.JsiiProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="p6-projen-project-awesome-list.AwesomeList",
):
    '''Awesome List project.

    :pjid: awesome-list
    '''

    def __init__(
        self,
        *,
        contact_email: typing.Optional[builtins.str] = None,
        author: builtins.str,
        author_address: builtins.str,
        repository_url: builtins.str,
        compat: typing.Optional[builtins.bool] = None,
        compat_ignore: typing.Optional[builtins.str] = None,
        dotnet: typing.Optional[projen.JsiiDotNetTarget] = None,
        exclude_typescript: typing.Optional[typing.Sequence[builtins.str]] = None,
        publish_to_go: typing.Optional[projen.JsiiGoTarget] = None,
        publish_to_maven: typing.Optional[projen.JsiiJavaTarget] = None,
        publish_to_nuget: typing.Optional[projen.JsiiDotNetTarget] = None,
        publish_to_pypi: typing.Optional[projen.JsiiPythonTarget] = None,
        python: typing.Optional[projen.JsiiPythonTarget] = None,
        rootdir: typing.Optional[builtins.str] = None,
        compile_before_test: typing.Optional[builtins.bool] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[projen.EslintOptions] = None,
        libdir: typing.Optional[builtins.str] = None,
        package: typing.Optional[builtins.bool] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[projen.typescript.ProjenrcOptions] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[projen.TypescriptConfigOptions] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        default_release_branch: builtins.str,
        antitamper: typing.Optional[builtins.bool] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[projen.github.DependabotOptions] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        initial_version: typing.Optional[builtins.str] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[projen.JestOptions] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        mergify_auto_merge_label: typing.Optional[builtins.str] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projen_during_build: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projen_upgrade_auto_merge: typing.Optional[builtins.bool] = None,
        projen_upgrade_schedule: typing.Optional[typing.Sequence[builtins.str]] = None,
        projen_upgrade_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[builtins.str] = None,
        release_branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Any]] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        name: builtins.str,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[projen.NpmAccess] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_task_execution: typing.Optional[projen.NpmTaskExecution] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[projen.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[projen.PeerDependencyOptions] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        projen_command: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        mergify: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param contact_email: What e-mail address to list for the Code of Conduct Point of Contact. Default: - ``project.authorAddress``
        :param author: (experimental) The name of the library author. Default: $GIT_USER_NAME
        :param author_address: (experimental) Email or URL of the library author. Default: $GIT_USER_EMAIL
        :param repository_url: (experimental) Git repository URL. Default: $GIT_REMOTE
        :param compat: (experimental) Automatically run API compatibility test against the latest version published to npm after compilation. - You can manually run compatibility tests using ``yarn compat`` if this feature is disabled. - You can ignore compatibility failures by adding lines to a ".compatignore" file. Default: false
        :param compat_ignore: (experimental) Name of the ignore file for API compatibility tests. Default: ".compatignore"
        :param dotnet: 
        :param exclude_typescript: (experimental) Accepts a list of glob patterns. Files matching any of those patterns will be excluded from the TypeScript compiler input. By default, jsii will include all *.ts files (except .d.ts files) in the TypeScript compiler input. This can be problematic for example when the package's build or test procedure generates .ts files that cannot be compiled with jsii's compiler settings.
        :param publish_to_go: (experimental) Publish Go bindings to a git repository. Default: - no publishing
        :param publish_to_maven: (experimental) Publish to maven. Default: - no publishing
        :param publish_to_nuget: (experimental) Publish to NuGet. Default: - no publishing
        :param publish_to_pypi: (experimental) Publish to pypi. Default: - no publishing
        :param python: 
        :param rootdir: Default: "."
        :param compile_before_test: (experimental) Compile the code before running tests. Default: - if ``testdir`` is under ``src/**``, the default is ``true``, otherwise the default is `false.
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param package: (experimental) Defines a ``yarn package`` command that will produce a tarball and place it under ``dist/js``. Default: true
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig.
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param default_release_branch: (experimental) The name of the main release branch. NOTE: this field is temporarily required as we migrate the default value from "master" to "main". Shortly, it will be made optional with "main" as the default. Default: "main"
        :param antitamper: (experimental) Checks that after build there are no modified files on git. Default: true
        :param artifacts_directory: (experimental) A directory which will contain artifacts to be published to npm. Default: "dist"
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Include dependabot configuration. Default: true
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param initial_version: (experimental) The initial version of the repo. The first release will bump over this version, so it will be v0.1.1 or v0.2.0 (depending on whether the first bump is minor or patch). Default: "v0.1.0"
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param jsii_release_version: (experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm. Default: "latest"
        :param mergify_auto_merge_label: (experimental) Automatically merge PRs that build successfully and have this label. To disable, set this value to an empty string. Default: "auto-merge"
        :param mergify_options: (experimental) Options for mergify. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (experimental) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projen_during_build: (experimental) Execute ``projen`` as the first step of the ``build`` task to synthesize project files. This applies both to local builds and to CI builds. Disabling this feature is NOT RECOMMENDED and means that manual changes to synthesized project files will be persisted. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: true
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_upgrade_auto_merge: (experimental) Automatically merge projen upgrade PRs when build passes. Applies the ``mergifyAutoMergeLabel`` to the PR if enabled. Default: - "true" if mergify auto-merge is enabled (default)
        :param projen_upgrade_schedule: (experimental) Customize the projenUpgrade schedule in cron expression. Default: [ "0 6 * * *" ]
        :param projen_upgrade_secret: (experimental) Periodically submits a pull request for projen upgrades (executes ``yarn projen:upgrade``). This setting is a GitHub secret name which contains a GitHub Access Token with ``repo`` and ``workflow`` permissions. This token is used to submit the upgrade pull request, which will likely include workflow updates. To create a personal access token see https://github.com/settings/tokens Default: - no automatic projen upgrade pull requests
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release_branches: (experimental) Branches which trigger a release. Default value is based on defaultReleaseBranch. Default: [ "main" ]
        :param release_every_commit: (experimental) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_schedule: (experimental) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (experimental) Define a GitHub workflow for releasing from "main" when new versions are bumped. Requires that ``version`` will be undefined. Default: - true if not a subproject
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param project_type: (experimental) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Author's Organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``peerDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/master/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_dist_tag: (experimental) Tags can be used to provide an alias instead of version numbers. For example, a project might choose to have multiple streams of development and use a different tag for each stream, e.g., stable, beta, dev, canary. By default, the ``latest`` tag is used by npm to identify the current version of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>`` specifier) installs the latest tag. Typically, projects only use the ``latest`` tag for stable release versions, and use other tags for unstable versions such as prereleases. The ``next`` tag is used by some projects to identify the upcoming version. Default: "latest"
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_task_execution: (experimental) Determines how tasks are executed when invoked as npm scripts (yarn/npm run xyz). Default: NpmTaskExecution.PROJEN
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scripts: (experimental) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Default: {}
        :param stability: (experimental) Package's Stability.
        :param mergify: (experimental) Whether mergify should be enabled on this repository or not. Default: true
        '''
        options = AwesomeListProjectOptions(
            contact_email=contact_email,
            author=author,
            author_address=author_address,
            repository_url=repository_url,
            compat=compat,
            compat_ignore=compat_ignore,
            dotnet=dotnet,
            exclude_typescript=exclude_typescript,
            publish_to_go=publish_to_go,
            publish_to_maven=publish_to_maven,
            publish_to_nuget=publish_to_nuget,
            publish_to_pypi=publish_to_pypi,
            python=python,
            rootdir=rootdir,
            compile_before_test=compile_before_test,
            disable_tsconfig=disable_tsconfig,
            docgen=docgen,
            docs_directory=docs_directory,
            entrypoint_types=entrypoint_types,
            eslint=eslint,
            eslint_options=eslint_options,
            libdir=libdir,
            package=package,
            projenrc_ts=projenrc_ts,
            projenrc_ts_options=projenrc_ts_options,
            sample_code=sample_code,
            srcdir=srcdir,
            testdir=testdir,
            tsconfig=tsconfig,
            typescript_version=typescript_version,
            default_release_branch=default_release_branch,
            antitamper=antitamper,
            artifacts_directory=artifacts_directory,
            build_workflow=build_workflow,
            code_cov=code_cov,
            code_cov_token_secret=code_cov_token_secret,
            copyright_owner=copyright_owner,
            copyright_period=copyright_period,
            dependabot=dependabot,
            dependabot_options=dependabot_options,
            gitignore=gitignore,
            initial_version=initial_version,
            jest=jest,
            jest_options=jest_options,
            jsii_release_version=jsii_release_version,
            mergify_auto_merge_label=mergify_auto_merge_label,
            mergify_options=mergify_options,
            mutable_build=mutable_build,
            npmignore=npmignore,
            npmignore_enabled=npmignore_enabled,
            projen_dev_dependency=projen_dev_dependency,
            projen_during_build=projen_during_build,
            projenrc_js=projenrc_js,
            projenrc_js_options=projenrc_js_options,
            projen_upgrade_auto_merge=projen_upgrade_auto_merge,
            projen_upgrade_schedule=projen_upgrade_schedule,
            projen_upgrade_secret=projen_upgrade_secret,
            projen_version=projen_version,
            pull_request_template=pull_request_template,
            pull_request_template_contents=pull_request_template_contents,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_schedule=release_schedule,
            release_to_npm=release_to_npm,
            release_workflow=release_workflow,
            release_workflow_setup_steps=release_workflow_setup_steps,
            workflow_bootstrap_steps=workflow_bootstrap_steps,
            workflow_container_image=workflow_container_image,
            workflow_node_version=workflow_node_version,
            name=name,
            clobber=clobber,
            dev_container=dev_container,
            gitpod=gitpod,
            logging=logging,
            outdir=outdir,
            parent=parent,
            project_type=project_type,
            readme=readme,
            allow_library_dependencies=allow_library_dependencies,
            author_email=author_email,
            author_name=author_name,
            author_organization=author_organization,
            author_url=author_url,
            auto_detect_bin=auto_detect_bin,
            bin=bin,
            bundled_deps=bundled_deps,
            deps=deps,
            description=description,
            dev_deps=dev_deps,
            entrypoint=entrypoint,
            homepage=homepage,
            keywords=keywords,
            license=license,
            licensed=licensed,
            max_node_version=max_node_version,
            min_node_version=min_node_version,
            npm_access=npm_access,
            npm_dist_tag=npm_dist_tag,
            npm_registry=npm_registry,
            npm_registry_url=npm_registry_url,
            npm_task_execution=npm_task_execution,
            npm_token_secret=npm_token_secret,
            package_manager=package_manager,
            package_name=package_name,
            peer_dependency_options=peer_dependency_options,
            peer_deps=peer_deps,
            projen_command=projen_command,
            repository=repository,
            repository_directory=repository_directory,
            scripts=scripts,
            stability=stability,
            mergify=mergify,
        )

        jsii.create(AwesomeList, self, [options])


@jsii.data_type(
    jsii_type="p6-projen-project-awesome-list.AwesomeListProjectOptions",
    jsii_struct_bases=[projen.JsiiProjectOptions],
    name_mapping={
        "mergify": "mergify",
        "name": "name",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "gitpod": "gitpod",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "project_type": "projectType",
        "readme": "readme",
        "allow_library_dependencies": "allowLibraryDependencies",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "author_organization": "authorOrganization",
        "author_url": "authorUrl",
        "auto_detect_bin": "autoDetectBin",
        "bin": "bin",
        "bundled_deps": "bundledDeps",
        "deps": "deps",
        "description": "description",
        "dev_deps": "devDeps",
        "entrypoint": "entrypoint",
        "homepage": "homepage",
        "keywords": "keywords",
        "license": "license",
        "licensed": "licensed",
        "max_node_version": "maxNodeVersion",
        "min_node_version": "minNodeVersion",
        "npm_access": "npmAccess",
        "npm_dist_tag": "npmDistTag",
        "npm_registry": "npmRegistry",
        "npm_registry_url": "npmRegistryUrl",
        "npm_task_execution": "npmTaskExecution",
        "npm_token_secret": "npmTokenSecret",
        "package_manager": "packageManager",
        "package_name": "packageName",
        "peer_dependency_options": "peerDependencyOptions",
        "peer_deps": "peerDeps",
        "projen_command": "projenCommand",
        "repository": "repository",
        "repository_directory": "repositoryDirectory",
        "scripts": "scripts",
        "stability": "stability",
        "default_release_branch": "defaultReleaseBranch",
        "antitamper": "antitamper",
        "artifacts_directory": "artifactsDirectory",
        "build_workflow": "buildWorkflow",
        "code_cov": "codeCov",
        "code_cov_token_secret": "codeCovTokenSecret",
        "copyright_owner": "copyrightOwner",
        "copyright_period": "copyrightPeriod",
        "dependabot": "dependabot",
        "dependabot_options": "dependabotOptions",
        "gitignore": "gitignore",
        "initial_version": "initialVersion",
        "jest": "jest",
        "jest_options": "jestOptions",
        "jsii_release_version": "jsiiReleaseVersion",
        "mergify_auto_merge_label": "mergifyAutoMergeLabel",
        "mergify_options": "mergifyOptions",
        "mutable_build": "mutableBuild",
        "npmignore": "npmignore",
        "npmignore_enabled": "npmignoreEnabled",
        "projen_dev_dependency": "projenDevDependency",
        "projen_during_build": "projenDuringBuild",
        "projenrc_js": "projenrcJs",
        "projenrc_js_options": "projenrcJsOptions",
        "projen_upgrade_auto_merge": "projenUpgradeAutoMerge",
        "projen_upgrade_schedule": "projenUpgradeSchedule",
        "projen_upgrade_secret": "projenUpgradeSecret",
        "projen_version": "projenVersion",
        "pull_request_template": "pullRequestTemplate",
        "pull_request_template_contents": "pullRequestTemplateContents",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_schedule": "releaseSchedule",
        "release_to_npm": "releaseToNpm",
        "release_workflow": "releaseWorkflow",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "workflow_bootstrap_steps": "workflowBootstrapSteps",
        "workflow_container_image": "workflowContainerImage",
        "workflow_node_version": "workflowNodeVersion",
        "compile_before_test": "compileBeforeTest",
        "disable_tsconfig": "disableTsconfig",
        "docgen": "docgen",
        "docs_directory": "docsDirectory",
        "entrypoint_types": "entrypointTypes",
        "eslint": "eslint",
        "eslint_options": "eslintOptions",
        "libdir": "libdir",
        "package": "package",
        "projenrc_ts": "projenrcTs",
        "projenrc_ts_options": "projenrcTsOptions",
        "sample_code": "sampleCode",
        "srcdir": "srcdir",
        "testdir": "testdir",
        "tsconfig": "tsconfig",
        "typescript_version": "typescriptVersion",
        "author": "author",
        "author_address": "authorAddress",
        "repository_url": "repositoryUrl",
        "compat": "compat",
        "compat_ignore": "compatIgnore",
        "dotnet": "dotnet",
        "exclude_typescript": "excludeTypescript",
        "publish_to_go": "publishToGo",
        "publish_to_maven": "publishToMaven",
        "publish_to_nuget": "publishToNuget",
        "publish_to_pypi": "publishToPypi",
        "python": "python",
        "rootdir": "rootdir",
        "contact_email": "contactEmail",
    },
)
class AwesomeListProjectOptions(projen.JsiiProjectOptions):
    def __init__(
        self,
        *,
        mergify: typing.Optional[builtins.bool] = None,
        name: builtins.str,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[projen.NpmAccess] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_task_execution: typing.Optional[projen.NpmTaskExecution] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[projen.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[projen.PeerDependencyOptions] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        projen_command: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        default_release_branch: builtins.str,
        antitamper: typing.Optional[builtins.bool] = None,
        artifacts_directory: typing.Optional[builtins.str] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[projen.github.DependabotOptions] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        initial_version: typing.Optional[builtins.str] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[projen.JestOptions] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        mergify_auto_merge_label: typing.Optional[builtins.str] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projen_during_build: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projen_upgrade_auto_merge: typing.Optional[builtins.bool] = None,
        projen_upgrade_schedule: typing.Optional[typing.Sequence[builtins.str]] = None,
        projen_upgrade_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[builtins.str] = None,
        release_branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[typing.Any]] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        compile_before_test: typing.Optional[builtins.bool] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[projen.EslintOptions] = None,
        libdir: typing.Optional[builtins.str] = None,
        package: typing.Optional[builtins.bool] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[projen.typescript.ProjenrcOptions] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[projen.TypescriptConfigOptions] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        author: builtins.str,
        author_address: builtins.str,
        repository_url: builtins.str,
        compat: typing.Optional[builtins.bool] = None,
        compat_ignore: typing.Optional[builtins.str] = None,
        dotnet: typing.Optional[projen.JsiiDotNetTarget] = None,
        exclude_typescript: typing.Optional[typing.Sequence[builtins.str]] = None,
        publish_to_go: typing.Optional[projen.JsiiGoTarget] = None,
        publish_to_maven: typing.Optional[projen.JsiiJavaTarget] = None,
        publish_to_nuget: typing.Optional[projen.JsiiDotNetTarget] = None,
        publish_to_pypi: typing.Optional[projen.JsiiPythonTarget] = None,
        python: typing.Optional[projen.JsiiPythonTarget] = None,
        rootdir: typing.Optional[builtins.str] = None,
        contact_email: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configurable knobs for Awesome Lists.

        :param mergify: (experimental) Whether mergify should be enabled on this repository or not. Default: true
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param project_type: (experimental) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Author's Organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``peerDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/master/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_dist_tag: (experimental) Tags can be used to provide an alias instead of version numbers. For example, a project might choose to have multiple streams of development and use a different tag for each stream, e.g., stable, beta, dev, canary. By default, the ``latest`` tag is used by npm to identify the current version of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>`` specifier) installs the latest tag. Typically, projects only use the ``latest`` tag for stable release versions, and use other tags for unstable versions such as prereleases. The ``next`` tag is used by some projects to identify the upcoming version. Default: "latest"
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_task_execution: (experimental) Determines how tasks are executed when invoked as npm scripts (yarn/npm run xyz). Default: NpmTaskExecution.PROJEN
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scripts: (experimental) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Default: {}
        :param stability: (experimental) Package's Stability.
        :param default_release_branch: (experimental) The name of the main release branch. NOTE: this field is temporarily required as we migrate the default value from "master" to "main". Shortly, it will be made optional with "main" as the default. Default: "main"
        :param antitamper: (experimental) Checks that after build there are no modified files on git. Default: true
        :param artifacts_directory: (experimental) A directory which will contain artifacts to be published to npm. Default: "dist"
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Include dependabot configuration. Default: true
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param initial_version: (experimental) The initial version of the repo. The first release will bump over this version, so it will be v0.1.1 or v0.2.0 (depending on whether the first bump is minor or patch). Default: "v0.1.0"
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param jsii_release_version: (experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm. Default: "latest"
        :param mergify_auto_merge_label: (experimental) Automatically merge PRs that build successfully and have this label. To disable, set this value to an empty string. Default: "auto-merge"
        :param mergify_options: (experimental) Options for mergify. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (experimental) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projen_during_build: (experimental) Execute ``projen`` as the first step of the ``build`` task to synthesize project files. This applies both to local builds and to CI builds. Disabling this feature is NOT RECOMMENDED and means that manual changes to synthesized project files will be persisted. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: true
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_upgrade_auto_merge: (experimental) Automatically merge projen upgrade PRs when build passes. Applies the ``mergifyAutoMergeLabel`` to the PR if enabled. Default: - "true" if mergify auto-merge is enabled (default)
        :param projen_upgrade_schedule: (experimental) Customize the projenUpgrade schedule in cron expression. Default: [ "0 6 * * *" ]
        :param projen_upgrade_secret: (experimental) Periodically submits a pull request for projen upgrades (executes ``yarn projen:upgrade``). This setting is a GitHub secret name which contains a GitHub Access Token with ``repo`` and ``workflow`` permissions. This token is used to submit the upgrade pull request, which will likely include workflow updates. To create a personal access token see https://github.com/settings/tokens Default: - no automatic projen upgrade pull requests
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release_branches: (experimental) Branches which trigger a release. Default value is based on defaultReleaseBranch. Default: [ "main" ]
        :param release_every_commit: (experimental) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_schedule: (experimental) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (experimental) Define a GitHub workflow for releasing from "main" when new versions are bumped. Requires that ``version`` will be undefined. Default: - true if not a subproject
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param compile_before_test: (experimental) Compile the code before running tests. Default: - if ``testdir`` is under ``src/**``, the default is ``true``, otherwise the default is `false.
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param package: (experimental) Defines a ``yarn package`` command that will produce a tarball and place it under ``dist/js``. Default: true
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig.
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param author: (experimental) The name of the library author. Default: $GIT_USER_NAME
        :param author_address: (experimental) Email or URL of the library author. Default: $GIT_USER_EMAIL
        :param repository_url: (experimental) Git repository URL. Default: $GIT_REMOTE
        :param compat: (experimental) Automatically run API compatibility test against the latest version published to npm after compilation. - You can manually run compatibility tests using ``yarn compat`` if this feature is disabled. - You can ignore compatibility failures by adding lines to a ".compatignore" file. Default: false
        :param compat_ignore: (experimental) Name of the ignore file for API compatibility tests. Default: ".compatignore"
        :param dotnet: 
        :param exclude_typescript: (experimental) Accepts a list of glob patterns. Files matching any of those patterns will be excluded from the TypeScript compiler input. By default, jsii will include all *.ts files (except .d.ts files) in the TypeScript compiler input. This can be problematic for example when the package's build or test procedure generates .ts files that cannot be compiled with jsii's compiler settings.
        :param publish_to_go: (experimental) Publish Go bindings to a git repository. Default: - no publishing
        :param publish_to_maven: (experimental) Publish to maven. Default: - no publishing
        :param publish_to_nuget: (experimental) Publish to NuGet. Default: - no publishing
        :param publish_to_pypi: (experimental) Publish to pypi. Default: - no publishing
        :param python: 
        :param rootdir: Default: "."
        :param contact_email: What e-mail address to list for the Code of Conduct Point of Contact. Default: - ``project.authorAddress``
        '''
        if isinstance(logging, dict):
            logging = projen.LoggerOptions(**logging)
        if isinstance(readme, dict):
            readme = projen.SampleReadmeProps(**readme)
        if isinstance(peer_dependency_options, dict):
            peer_dependency_options = projen.PeerDependencyOptions(**peer_dependency_options)
        if isinstance(dependabot_options, dict):
            dependabot_options = projen.github.DependabotOptions(**dependabot_options)
        if isinstance(jest_options, dict):
            jest_options = projen.JestOptions(**jest_options)
        if isinstance(mergify_options, dict):
            mergify_options = projen.github.MergifyOptions(**mergify_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = projen.javascript.ProjenrcOptions(**projenrc_js_options)
        if isinstance(eslint_options, dict):
            eslint_options = projen.EslintOptions(**eslint_options)
        if isinstance(projenrc_ts_options, dict):
            projenrc_ts_options = projen.typescript.ProjenrcOptions(**projenrc_ts_options)
        if isinstance(tsconfig, dict):
            tsconfig = projen.TypescriptConfigOptions(**tsconfig)
        if isinstance(dotnet, dict):
            dotnet = projen.JsiiDotNetTarget(**dotnet)
        if isinstance(publish_to_go, dict):
            publish_to_go = projen.JsiiGoTarget(**publish_to_go)
        if isinstance(publish_to_maven, dict):
            publish_to_maven = projen.JsiiJavaTarget(**publish_to_maven)
        if isinstance(publish_to_nuget, dict):
            publish_to_nuget = projen.JsiiDotNetTarget(**publish_to_nuget)
        if isinstance(publish_to_pypi, dict):
            publish_to_pypi = projen.JsiiPythonTarget(**publish_to_pypi)
        if isinstance(python, dict):
            python = projen.JsiiPythonTarget(**python)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "default_release_branch": default_release_branch,
            "author": author,
            "author_address": author_address,
            "repository_url": repository_url,
        }
        if mergify is not None:
            self._values["mergify"] = mergify
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if project_type is not None:
            self._values["project_type"] = project_type
        if readme is not None:
            self._values["readme"] = readme
        if allow_library_dependencies is not None:
            self._values["allow_library_dependencies"] = allow_library_dependencies
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if author_organization is not None:
            self._values["author_organization"] = author_organization
        if author_url is not None:
            self._values["author_url"] = author_url
        if auto_detect_bin is not None:
            self._values["auto_detect_bin"] = auto_detect_bin
        if bin is not None:
            self._values["bin"] = bin
        if bundled_deps is not None:
            self._values["bundled_deps"] = bundled_deps
        if deps is not None:
            self._values["deps"] = deps
        if description is not None:
            self._values["description"] = description
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if homepage is not None:
            self._values["homepage"] = homepage
        if keywords is not None:
            self._values["keywords"] = keywords
        if license is not None:
            self._values["license"] = license
        if licensed is not None:
            self._values["licensed"] = licensed
        if max_node_version is not None:
            self._values["max_node_version"] = max_node_version
        if min_node_version is not None:
            self._values["min_node_version"] = min_node_version
        if npm_access is not None:
            self._values["npm_access"] = npm_access
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if npm_registry is not None:
            self._values["npm_registry"] = npm_registry
        if npm_registry_url is not None:
            self._values["npm_registry_url"] = npm_registry_url
        if npm_task_execution is not None:
            self._values["npm_task_execution"] = npm_task_execution
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if package_name is not None:
            self._values["package_name"] = package_name
        if peer_dependency_options is not None:
            self._values["peer_dependency_options"] = peer_dependency_options
        if peer_deps is not None:
            self._values["peer_deps"] = peer_deps
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if repository is not None:
            self._values["repository"] = repository
        if repository_directory is not None:
            self._values["repository_directory"] = repository_directory
        if scripts is not None:
            self._values["scripts"] = scripts
        if stability is not None:
            self._values["stability"] = stability
        if antitamper is not None:
            self._values["antitamper"] = antitamper
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if build_workflow is not None:
            self._values["build_workflow"] = build_workflow
        if code_cov is not None:
            self._values["code_cov"] = code_cov
        if code_cov_token_secret is not None:
            self._values["code_cov_token_secret"] = code_cov_token_secret
        if copyright_owner is not None:
            self._values["copyright_owner"] = copyright_owner
        if copyright_period is not None:
            self._values["copyright_period"] = copyright_period
        if dependabot is not None:
            self._values["dependabot"] = dependabot
        if dependabot_options is not None:
            self._values["dependabot_options"] = dependabot_options
        if gitignore is not None:
            self._values["gitignore"] = gitignore
        if initial_version is not None:
            self._values["initial_version"] = initial_version
        if jest is not None:
            self._values["jest"] = jest
        if jest_options is not None:
            self._values["jest_options"] = jest_options
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if mergify_auto_merge_label is not None:
            self._values["mergify_auto_merge_label"] = mergify_auto_merge_label
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if mutable_build is not None:
            self._values["mutable_build"] = mutable_build
        if npmignore is not None:
            self._values["npmignore"] = npmignore
        if npmignore_enabled is not None:
            self._values["npmignore_enabled"] = npmignore_enabled
        if projen_dev_dependency is not None:
            self._values["projen_dev_dependency"] = projen_dev_dependency
        if projen_during_build is not None:
            self._values["projen_during_build"] = projen_during_build
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projen_upgrade_auto_merge is not None:
            self._values["projen_upgrade_auto_merge"] = projen_upgrade_auto_merge
        if projen_upgrade_schedule is not None:
            self._values["projen_upgrade_schedule"] = projen_upgrade_schedule
        if projen_upgrade_secret is not None:
            self._values["projen_upgrade_secret"] = projen_upgrade_secret
        if projen_version is not None:
            self._values["projen_version"] = projen_version
        if pull_request_template is not None:
            self._values["pull_request_template"] = pull_request_template
        if pull_request_template_contents is not None:
            self._values["pull_request_template_contents"] = pull_request_template_contents
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_to_npm is not None:
            self._values["release_to_npm"] = release_to_npm
        if release_workflow is not None:
            self._values["release_workflow"] = release_workflow
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if workflow_bootstrap_steps is not None:
            self._values["workflow_bootstrap_steps"] = workflow_bootstrap_steps
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_node_version is not None:
            self._values["workflow_node_version"] = workflow_node_version
        if compile_before_test is not None:
            self._values["compile_before_test"] = compile_before_test
        if disable_tsconfig is not None:
            self._values["disable_tsconfig"] = disable_tsconfig
        if docgen is not None:
            self._values["docgen"] = docgen
        if docs_directory is not None:
            self._values["docs_directory"] = docs_directory
        if entrypoint_types is not None:
            self._values["entrypoint_types"] = entrypoint_types
        if eslint is not None:
            self._values["eslint"] = eslint
        if eslint_options is not None:
            self._values["eslint_options"] = eslint_options
        if libdir is not None:
            self._values["libdir"] = libdir
        if package is not None:
            self._values["package"] = package
        if projenrc_ts is not None:
            self._values["projenrc_ts"] = projenrc_ts
        if projenrc_ts_options is not None:
            self._values["projenrc_ts_options"] = projenrc_ts_options
        if sample_code is not None:
            self._values["sample_code"] = sample_code
        if srcdir is not None:
            self._values["srcdir"] = srcdir
        if testdir is not None:
            self._values["testdir"] = testdir
        if tsconfig is not None:
            self._values["tsconfig"] = tsconfig
        if typescript_version is not None:
            self._values["typescript_version"] = typescript_version
        if compat is not None:
            self._values["compat"] = compat
        if compat_ignore is not None:
            self._values["compat_ignore"] = compat_ignore
        if dotnet is not None:
            self._values["dotnet"] = dotnet
        if exclude_typescript is not None:
            self._values["exclude_typescript"] = exclude_typescript
        if publish_to_go is not None:
            self._values["publish_to_go"] = publish_to_go
        if publish_to_maven is not None:
            self._values["publish_to_maven"] = publish_to_maven
        if publish_to_nuget is not None:
            self._values["publish_to_nuget"] = publish_to_nuget
        if publish_to_pypi is not None:
            self._values["publish_to_pypi"] = publish_to_pypi
        if python is not None:
            self._values["python"] = python
        if rootdir is not None:
            self._values["rootdir"] = rootdir
        if contact_email is not None:
            self._values["contact_email"] = contact_email

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether mergify should be enabled on this repository or not.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logging(self) -> typing.Optional[projen.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[projen.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[projen.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[projen.Project], result)

    @builtins.property
    def project_type(self) -> typing.Optional[projen.ProjectType]:
        '''(experimental) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[projen.ProjectType], result)

    @builtins.property
    def readme(self) -> typing.Optional[projen.SampleReadmeProps]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[projen.SampleReadmeProps], result)

    @builtins.property
    def allow_library_dependencies(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``.

        This is normally only allowed for libraries. For apps, there's no meaning
        for specifying these.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow_library_dependencies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's e-mail.

        :stability: experimental
        '''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's name.

        :stability: experimental
        '''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_organization(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Author's Organization.

        :stability: experimental
        '''
        result = self._values.get("author_organization")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's URL / Website.

        :stability: experimental
        '''
        result = self._values.get("author_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_detect_bin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_detect_bin")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bin(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Binary programs vended with your module.

        You can use this option to add/customize how binaries are represented in
        your ``package.json``, but unless ``autoDetectBin`` is ``false``, every
        executable file under ``bin`` will automatically be added to this section.

        :stability: experimental
        '''
        result = self._values.get("bin")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def bundled_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dependencies to bundle into this module.

        These modules will be
        added both to the ``dependencies`` section and ``peerDependencies`` section of
        your ``package.json``.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :stability: experimental
        '''
        result = self._values.get("bundled_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Runtime dependencies of this module.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            ["express", "lodash", "foo@^2"]
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description is just a string that helps people understand the purpose of the package.

        It can be used when searching for packages in a package manager as well.
        See https://classic.yarnpkg.com/en/docs/package-json/#toc-description

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Build dependencies for this module.

        These dependencies will only be
        available in your build environment but will not be fetched when this
        module is consumed.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            ["typescript", "@types/express"]
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) Module entrypoint (``main`` in ``package.json``).

        Set to an empty string to not include ``main`` in your package.json

        :default: "lib/index.js"

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Homepage / Website.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Keywords to include in ``package.json``.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License's SPDX identifier.

        See https://github.com/projen/projen/tree/master/license-text for a list of supported licenses.
        Use the ``licensed`` option if you want to no license to be specified.

        :default: "Apache-2.0"

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def licensed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates if a license should be added.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("licensed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum node.js version to require via ``engines`` (inclusive).

        :default: - no max

        :stability: experimental
        '''
        result = self._values.get("max_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive).

        :default: - no "engines" specified

        :stability: experimental
        '''
        result = self._values.get("min_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_access(self) -> typing.Optional[projen.NpmAccess]:
        '''(experimental) Access level of the npm package.

        :default:

        - for scoped packages (e.g. ``foo@bar``), the default is
        ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is
        ``NpmAccess.PUBLIC``.

        :stability: experimental
        '''
        result = self._values.get("npm_access")
        return typing.cast(typing.Optional[projen.NpmAccess], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
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
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_registry(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The host name of the npm registry to publish to.

        Cannot be set together with ``npmRegistryUrl``.

        :deprecated: use ``npmRegistryUrl`` instead

        :stability: deprecated
        '''
        result = self._values.get("npm_registry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The base URL of the npm package registry.

        Must be a URL (e.g. start with "https://" or "http://")

        :default: "https://registry.npmjs.org"

        :stability: experimental
        '''
        result = self._values.get("npm_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_task_execution(self) -> typing.Optional[projen.NpmTaskExecution]:
        '''(experimental) Determines how tasks are executed when invoked as npm scripts (yarn/npm run xyz).

        :default: NpmTaskExecution.PROJEN

        :stability: experimental
        '''
        result = self._values.get("npm_task_execution")
        return typing.cast(typing.Optional[projen.NpmTaskExecution], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: "NPM_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package_manager(self) -> typing.Optional[projen.NodePackageManager]:
        '''(experimental) The Node Package Manager used to execute scripts.

        :default: NodePackageManager.YARN

        :stability: experimental
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[projen.NodePackageManager], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The "name" in package.json.

        :default: - defaults to project name

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer_dependency_options(self) -> typing.Optional[projen.PeerDependencyOptions]:
        '''(experimental) Options for ``peerDeps``.

        :stability: experimental
        '''
        result = self._values.get("peer_dependency_options")
        return typing.cast(typing.Optional[projen.PeerDependencyOptions], result)

    @builtins.property
    def peer_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Peer dependencies for this module.

        Dependencies listed here are required to
        be installed (and satisfied) by the *consumer* of this library. Using peer
        dependencies allows you to ensure that only a single module of a certain
        library exists in the ``node_modules`` tree of your consumers.

        Note that prior to npm@7, peer dependencies are *not* automatically
        installed, which means that adding peer dependencies to a library will be a
        breaking change for your customers.

        Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is
        enabled by default), projen will automatically add a dev dependency with a
        pinned version for each peer dependency. This will ensure that you build &
        test your module against the lowest peer version required.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("peer_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository is the location where the actual code for your package lives.

        See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.

        :stability: experimental
        '''
        result = self._values.get("repository_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) npm scripts to include.

        If a script has the same name as a standard script,
        the standard script will be overwritten.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def stability(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Stability.

        :stability: experimental
        '''
        result = self._values.get("stability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_release_branch(self) -> builtins.str:
        '''(experimental) The name of the main release branch.

        NOTE: this field is temporarily required as we migrate the default value
        from "master" to "main". Shortly, it will be made optional with "main" as
        the default.

        :default: "main"

        :stability: experimental
        '''
        result = self._values.get("default_release_branch")
        assert result is not None, "Required property 'default_release_branch' is missing"
        return typing.cast(builtins.str, result)

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
    def build_workflow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow for building PRs.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("build_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_cov(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("code_cov")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_cov_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories.

        :default: - if this option is not specified, only public repositories are supported

        :stability: experimental
        '''
        result = self._values.get("code_cov_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_owner(self) -> typing.Optional[builtins.str]:
        '''(experimental) License copyright owner.

        :default: - defaults to the value of authorName or "" if ``authorName`` is undefined.

        :stability: experimental
        '''
        result = self._values.get("copyright_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_period(self) -> typing.Optional[builtins.str]:
        '''(experimental) The copyright years to put in the LICENSE file.

        :default: - current year

        :stability: experimental
        '''
        result = self._values.get("copyright_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependabot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include dependabot configuration.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("dependabot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dependabot_options(self) -> typing.Optional[projen.github.DependabotOptions]:
        '''(experimental) Options for dependabot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("dependabot_options")
        return typing.cast(typing.Optional[projen.github.DependabotOptions], result)

    @builtins.property
    def gitignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional entries to .gitignore.

        :stability: experimental
        '''
        result = self._values.get("gitignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def initial_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The initial version of the repo.

        The first release will bump over this
        version, so it will be v0.1.1 or v0.2.0 (depending on whether the first
        bump is minor or patch).

        :default: "v0.1.0"

        :stability: experimental
        '''
        result = self._values.get("initial_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup jest unit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("jest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jest_options(self) -> typing.Optional[projen.JestOptions]:
        '''(experimental) Jest options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("jest_options")
        return typing.cast(typing.Optional[projen.JestOptions], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mergify_auto_merge_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically merge PRs that build successfully and have this label.

        To disable, set this value to an empty string.

        :default: "auto-merge"

        :stability: experimental
        '''
        result = self._values.get("mergify_auto_merge_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional[projen.github.MergifyOptions]:
        '''(experimental) Options for mergify.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[projen.github.MergifyOptions], result)

    @builtins.property
    def mutable_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically update files modified during builds to pull-request branches.

        This means
        that any files synthesized by projen or e.g. test snapshots will always be up-to-date
        before a PR is merged.

        Implies that PR builds do not have anti-tamper checks.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mutable_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npmignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional entries to .npmignore.

        :stability: experimental
        '''
        result = self._values.get("npmignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def npmignore_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("npmignore_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projen_dev_dependency(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates of "projen" should be installed as a devDependency.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projen_dev_dependency")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projen_during_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Execute ``projen`` as the first step of the ``build`` task to synthesize project files.

        This applies both to local builds and to CI builds.

        Disabling this feature is NOT RECOMMENDED and means that manual changes to
        synthesized project files will be persisted.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projen_during_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js_options(self) -> typing.Optional[projen.javascript.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.js.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[projen.javascript.ProjenrcOptions], result)

    @builtins.property
    def projen_upgrade_auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically merge projen upgrade PRs when build passes.

        Applies the ``mergifyAutoMergeLabel`` to the PR if enabled.

        :default: - "true" if mergify auto-merge is enabled (default)

        :stability: experimental
        '''
        result = self._values.get("projen_upgrade_auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projen_upgrade_schedule(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Customize the projenUpgrade schedule in cron expression.

        :default: [ "0 6 * * *" ]

        :stability: experimental
        '''
        result = self._values.get("projen_upgrade_schedule")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def projen_upgrade_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) Periodically submits a pull request for projen upgrades (executes ``yarn projen:upgrade``).

        This setting is a GitHub secret name which contains a GitHub Access Token
        with ``repo`` and ``workflow`` permissions.

        This token is used to submit the upgrade pull request, which will likely
        include workflow updates.

        To create a personal access token see https://github.com/settings/tokens

        :default: - no automatic projen upgrade pull requests

        :stability: experimental
        '''
        result = self._values.get("projen_upgrade_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of projen to install.

        :default: - Defaults to the latest version.

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_template(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a GitHub pull request template.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template_contents(self) -> typing.Optional[builtins.str]:
        '''(experimental) The contents of the pull request template.

        :default: - default content

        :stability: experimental
        '''
        result = self._values.get("pull_request_template_contents")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_branches(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Branches which trigger a release.

        Default value is based on defaultReleaseBranch.

        :default: [ "main" ]

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

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
    def release_to_npm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release to npm when new versions are introduced.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_to_npm")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_workflow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow for releasing from "main" when new versions are bumped.

        Requires that ``version`` will be undefined.

        :default: - true if not a subproject

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("release_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_workflow_setup_steps(self) -> typing.Optional[typing.List[typing.Any]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[typing.Any]], result)

    @builtins.property
    def workflow_bootstrap_steps(self) -> typing.Optional[typing.List[typing.Any]]:
        '''(experimental) Workflow steps to use in order to bootstrap this repo.

        :default: "yarn install --frozen-lockfile && yarn projen"

        :stability: experimental
        '''
        result = self._values.get("workflow_bootstrap_steps")
        return typing.cast(typing.Optional[typing.List[typing.Any]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The node version to use in GitHub workflows.

        :default: - same as ``minNodeVersion``

        :stability: experimental
        '''
        result = self._values.get("workflow_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compile_before_test(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Compile the code before running tests.

        :default: - if ``testdir`` is under ``src/**``, the default is ``true``, otherwise the default is `false.

        :stability: experimental
        '''
        result = self._values.get("compile_before_test")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_tsconfig(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docgen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Docgen by Typedoc.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("docgen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docs_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docs directory.

        :default: "docs"

        :stability: experimental
        '''
        result = self._values.get("docs_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_types(self) -> typing.Optional[builtins.str]:
        '''(experimental) The .d.ts file that includes the type declarations for this module.

        :default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)

        :stability: experimental
        '''
        result = self._values.get("entrypoint_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eslint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup eslint.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("eslint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eslint_options(self) -> typing.Optional[projen.EslintOptions]:
        '''(experimental) Eslint options.

        :default: - opinionated default options

        :stability: experimental
        '''
        result = self._values.get("eslint_options")
        return typing.cast(typing.Optional[projen.EslintOptions], result)

    @builtins.property
    def libdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript  artifacts output directory.

        :default: "lib"

        :stability: experimental
        '''
        result = self._values.get("libdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines a ``yarn package`` command that will produce a tarball and place it under ``dist/js``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("package")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use TypeScript for your projenrc file (``.projenrc.ts``).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts_options(self) -> typing.Optional[projen.typescript.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.ts.

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts_options")
        return typing.cast(typing.Optional[projen.typescript.ProjenrcOptions], result)

    @builtins.property
    def sample_code(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample_code")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def srcdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript sources directory.

        :default: "src"

        :stability: experimental
        '''
        result = self._values.get("srcdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``.

        If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``),
        then tests are going to be compiled into ``lib/`` and executed as javascript.
        If the test directory is outside of ``src``, then we configure jest to
        compile the code in-memory.

        :default: "test"

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tsconfig(self) -> typing.Optional[projen.TypescriptConfigOptions]:
        '''(experimental) Custom TSConfig.

        :stability: experimental
        '''
        result = self._values.get("tsconfig")
        return typing.cast(typing.Optional[projen.TypescriptConfigOptions], result)

    @builtins.property
    def typescript_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) TypeScript version to use.

        NOTE: Typescript is not semantically versioned and should remain on the
        same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``).

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("typescript_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author(self) -> builtins.str:
        '''(experimental) The name of the library author.

        :default: $GIT_USER_NAME

        :stability: experimental
        '''
        result = self._values.get("author")
        assert result is not None, "Required property 'author' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def author_address(self) -> builtins.str:
        '''(experimental) Email or URL of the library author.

        :default: $GIT_USER_EMAIL

        :stability: experimental
        '''
        result = self._values.get("author_address")
        assert result is not None, "Required property 'author_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_url(self) -> builtins.str:
        '''(experimental) Git repository URL.

        :default: $GIT_REMOTE

        :stability: experimental
        '''
        result = self._values.get("repository_url")
        assert result is not None, "Required property 'repository_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compat(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically run API compatibility test against the latest version published to npm after compilation.

        - You can manually run compatibility tests using ``yarn compat`` if this feature is disabled.
        - You can ignore compatibility failures by adding lines to a ".compatignore" file.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("compat")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def compat_ignore(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the ignore file for API compatibility tests.

        :default: ".compatignore"

        :stability: experimental
        '''
        result = self._values.get("compat_ignore")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dotnet(self) -> typing.Optional[projen.JsiiDotNetTarget]:
        '''
        :deprecated: use ``publishToNuget``

        :stability: deprecated
        '''
        result = self._values.get("dotnet")
        return typing.cast(typing.Optional[projen.JsiiDotNetTarget], result)

    @builtins.property
    def exclude_typescript(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Accepts a list of glob patterns.

        Files matching any of those patterns will be excluded from the TypeScript compiler input.

        By default, jsii will include all *.ts files (except .d.ts files) in the TypeScript compiler input.
        This can be problematic for example when the package's build or test procedure generates .ts files
        that cannot be compiled with jsii's compiler settings.

        :stability: experimental
        '''
        result = self._values.get("exclude_typescript")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def publish_to_go(self) -> typing.Optional[projen.JsiiGoTarget]:
        '''(experimental) Publish Go bindings to a git repository.

        :default: - no publishing

        :stability: experimental
        '''
        result = self._values.get("publish_to_go")
        return typing.cast(typing.Optional[projen.JsiiGoTarget], result)

    @builtins.property
    def publish_to_maven(self) -> typing.Optional[projen.JsiiJavaTarget]:
        '''(experimental) Publish to maven.

        :default: - no publishing

        :stability: experimental
        '''
        result = self._values.get("publish_to_maven")
        return typing.cast(typing.Optional[projen.JsiiJavaTarget], result)

    @builtins.property
    def publish_to_nuget(self) -> typing.Optional[projen.JsiiDotNetTarget]:
        '''(experimental) Publish to NuGet.

        :default: - no publishing

        :stability: experimental
        '''
        result = self._values.get("publish_to_nuget")
        return typing.cast(typing.Optional[projen.JsiiDotNetTarget], result)

    @builtins.property
    def publish_to_pypi(self) -> typing.Optional[projen.JsiiPythonTarget]:
        '''(experimental) Publish to pypi.

        :default: - no publishing

        :stability: experimental
        '''
        result = self._values.get("publish_to_pypi")
        return typing.cast(typing.Optional[projen.JsiiPythonTarget], result)

    @builtins.property
    def python(self) -> typing.Optional[projen.JsiiPythonTarget]:
        '''
        :deprecated: use ``publishToPyPi``

        :stability: deprecated
        '''
        result = self._values.get("python")
        return typing.cast(typing.Optional[projen.JsiiPythonTarget], result)

    @builtins.property
    def rootdir(self) -> typing.Optional[builtins.str]:
        '''
        :default: "."

        :stability: experimental
        '''
        result = self._values.get("rootdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contact_email(self) -> typing.Optional[builtins.str]:
        '''What e-mail address to list for the Code of Conduct Point of Contact.

        :default: - ``project.authorAddress``
        '''
        result = self._values.get("contact_email")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwesomeListProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AwesomeList",
    "AwesomeListProjectOptions",
]

publication.publish()
