'''
# Terraform CDK github Provider ~> 4.0

This repo builds and publishes the Terraform github Provider bindings for [cdktf](https://cdk.tf).

Current build targets are:

* npm
* Pypi
* Nuget
* Maven

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform github Provider version 1:1. In fact, it always tracks `latest` of `~> 4.0` with every release. If there scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform github Provider](https://github.com/terraform-providers/terraform-provider-github)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform github Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

## projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

## cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/terraform-cdk-providers/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

## provider version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).
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

import cdktf
import constructs


class ActionsEnvironmentSecret(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.ActionsEnvironmentSecret",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html github_actions_environment_secret}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        environment: builtins.str,
        repository: builtins.str,
        secret_name: builtins.str,
        encrypted_value: typing.Optional[builtins.str] = None,
        plaintext_value: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html github_actions_environment_secret} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param environment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#environment ActionsEnvironmentSecret#environment}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#repository ActionsEnvironmentSecret#repository}.
        :param secret_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#secret_name ActionsEnvironmentSecret#secret_name}.
        :param encrypted_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#encrypted_value ActionsEnvironmentSecret#encrypted_value}.
        :param plaintext_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#plaintext_value ActionsEnvironmentSecret#plaintext_value}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ActionsEnvironmentSecretConfig(
            environment=environment,
            repository=repository,
            secret_name=secret_name,
            encrypted_value=encrypted_value,
            plaintext_value=plaintext_value,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ActionsEnvironmentSecret, self, [scope, id, config])

    @jsii.member(jsii_name="resetEncryptedValue")
    def reset_encrypted_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptedValue", []))

    @jsii.member(jsii_name="resetPlaintextValue")
    def reset_plaintext_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlaintextValue", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environmentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretNameInput")
    def secret_name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedValueInput")
    def encrypted_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptedValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plaintextValueInput")
    def plaintext_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "plaintextValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedValue")
    def encrypted_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptedValue"))

    @encrypted_value.setter
    def encrypted_value(self, value: builtins.str) -> None:
        jsii.set(self, "encryptedValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: builtins.str) -> None:
        jsii.set(self, "environment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plaintextValue")
    def plaintext_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plaintextValue"))

    @plaintext_value.setter
    def plaintext_value(self, value: builtins.str) -> None:
        jsii.set(self, "plaintextValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretName"))

    @secret_name.setter
    def secret_name(self, value: builtins.str) -> None:
        jsii.set(self, "secretName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.ActionsEnvironmentSecretConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "environment": "environment",
        "repository": "repository",
        "secret_name": "secretName",
        "encrypted_value": "encryptedValue",
        "plaintext_value": "plaintextValue",
    },
)
class ActionsEnvironmentSecretConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        environment: builtins.str,
        repository: builtins.str,
        secret_name: builtins.str,
        encrypted_value: typing.Optional[builtins.str] = None,
        plaintext_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param environment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#environment ActionsEnvironmentSecret#environment}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#repository ActionsEnvironmentSecret#repository}.
        :param secret_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#secret_name ActionsEnvironmentSecret#secret_name}.
        :param encrypted_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#encrypted_value ActionsEnvironmentSecret#encrypted_value}.
        :param plaintext_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#plaintext_value ActionsEnvironmentSecret#plaintext_value}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "environment": environment,
            "repository": repository,
            "secret_name": secret_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if encrypted_value is not None:
            self._values["encrypted_value"] = encrypted_value
        if plaintext_value is not None:
            self._values["plaintext_value"] = plaintext_value

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def environment(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#environment ActionsEnvironmentSecret#environment}.'''
        result = self._values.get("environment")
        assert result is not None, "Required property 'environment' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#repository ActionsEnvironmentSecret#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#secret_name ActionsEnvironmentSecret#secret_name}.'''
        result = self._values.get("secret_name")
        assert result is not None, "Required property 'secret_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encrypted_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#encrypted_value ActionsEnvironmentSecret#encrypted_value}.'''
        result = self._values.get("encrypted_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plaintext_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_environment_secret.html#plaintext_value ActionsEnvironmentSecret#plaintext_value}.'''
        result = self._values.get("plaintext_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionsEnvironmentSecretConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ActionsOrganizationSecret(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.ActionsOrganizationSecret",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html github_actions_organization_secret}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        secret_name: builtins.str,
        visibility: builtins.str,
        encrypted_value: typing.Optional[builtins.str] = None,
        plaintext_value: typing.Optional[builtins.str] = None,
        selected_repository_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html github_actions_organization_secret} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param secret_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#secret_name ActionsOrganizationSecret#secret_name}.
        :param visibility: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#visibility ActionsOrganizationSecret#visibility}.
        :param encrypted_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#encrypted_value ActionsOrganizationSecret#encrypted_value}.
        :param plaintext_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#plaintext_value ActionsOrganizationSecret#plaintext_value}.
        :param selected_repository_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#selected_repository_ids ActionsOrganizationSecret#selected_repository_ids}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ActionsOrganizationSecretConfig(
            secret_name=secret_name,
            visibility=visibility,
            encrypted_value=encrypted_value,
            plaintext_value=plaintext_value,
            selected_repository_ids=selected_repository_ids,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ActionsOrganizationSecret, self, [scope, id, config])

    @jsii.member(jsii_name="resetEncryptedValue")
    def reset_encrypted_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptedValue", []))

    @jsii.member(jsii_name="resetPlaintextValue")
    def reset_plaintext_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlaintextValue", []))

    @jsii.member(jsii_name="resetSelectedRepositoryIds")
    def reset_selected_repository_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelectedRepositoryIds", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretNameInput")
    def secret_name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibilityInput")
    def visibility_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibilityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedValueInput")
    def encrypted_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptedValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plaintextValueInput")
    def plaintext_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "plaintextValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectedRepositoryIdsInput")
    def selected_repository_ids_input(
        self,
    ) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "selectedRepositoryIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedValue")
    def encrypted_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptedValue"))

    @encrypted_value.setter
    def encrypted_value(self, value: builtins.str) -> None:
        jsii.set(self, "encryptedValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plaintextValue")
    def plaintext_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plaintextValue"))

    @plaintext_value.setter
    def plaintext_value(self, value: builtins.str) -> None:
        jsii.set(self, "plaintextValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretName"))

    @secret_name.setter
    def secret_name(self, value: builtins.str) -> None:
        jsii.set(self, "secretName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectedRepositoryIds")
    def selected_repository_ids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "selectedRepositoryIds"))

    @selected_repository_ids.setter
    def selected_repository_ids(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "selectedRepositoryIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @visibility.setter
    def visibility(self, value: builtins.str) -> None:
        jsii.set(self, "visibility", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.ActionsOrganizationSecretConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "secret_name": "secretName",
        "visibility": "visibility",
        "encrypted_value": "encryptedValue",
        "plaintext_value": "plaintextValue",
        "selected_repository_ids": "selectedRepositoryIds",
    },
)
class ActionsOrganizationSecretConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        secret_name: builtins.str,
        visibility: builtins.str,
        encrypted_value: typing.Optional[builtins.str] = None,
        plaintext_value: typing.Optional[builtins.str] = None,
        selected_repository_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param secret_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#secret_name ActionsOrganizationSecret#secret_name}.
        :param visibility: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#visibility ActionsOrganizationSecret#visibility}.
        :param encrypted_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#encrypted_value ActionsOrganizationSecret#encrypted_value}.
        :param plaintext_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#plaintext_value ActionsOrganizationSecret#plaintext_value}.
        :param selected_repository_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#selected_repository_ids ActionsOrganizationSecret#selected_repository_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "secret_name": secret_name,
            "visibility": visibility,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if encrypted_value is not None:
            self._values["encrypted_value"] = encrypted_value
        if plaintext_value is not None:
            self._values["plaintext_value"] = plaintext_value
        if selected_repository_ids is not None:
            self._values["selected_repository_ids"] = selected_repository_ids

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def secret_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#secret_name ActionsOrganizationSecret#secret_name}.'''
        result = self._values.get("secret_name")
        assert result is not None, "Required property 'secret_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def visibility(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#visibility ActionsOrganizationSecret#visibility}.'''
        result = self._values.get("visibility")
        assert result is not None, "Required property 'visibility' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encrypted_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#encrypted_value ActionsOrganizationSecret#encrypted_value}.'''
        result = self._values.get("encrypted_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plaintext_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#plaintext_value ActionsOrganizationSecret#plaintext_value}.'''
        result = self._values.get("plaintext_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def selected_repository_ids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_organization_secret.html#selected_repository_ids ActionsOrganizationSecret#selected_repository_ids}.'''
        result = self._values.get("selected_repository_ids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionsOrganizationSecretConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ActionsSecret(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.ActionsSecret",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html github_actions_secret}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        repository: builtins.str,
        secret_name: builtins.str,
        encrypted_value: typing.Optional[builtins.str] = None,
        plaintext_value: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html github_actions_secret} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#repository ActionsSecret#repository}.
        :param secret_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#secret_name ActionsSecret#secret_name}.
        :param encrypted_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#encrypted_value ActionsSecret#encrypted_value}.
        :param plaintext_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#plaintext_value ActionsSecret#plaintext_value}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ActionsSecretConfig(
            repository=repository,
            secret_name=secret_name,
            encrypted_value=encrypted_value,
            plaintext_value=plaintext_value,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ActionsSecret, self, [scope, id, config])

    @jsii.member(jsii_name="resetEncryptedValue")
    def reset_encrypted_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptedValue", []))

    @jsii.member(jsii_name="resetPlaintextValue")
    def reset_plaintext_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlaintextValue", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretNameInput")
    def secret_name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedValueInput")
    def encrypted_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptedValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plaintextValueInput")
    def plaintext_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "plaintextValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedValue")
    def encrypted_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptedValue"))

    @encrypted_value.setter
    def encrypted_value(self, value: builtins.str) -> None:
        jsii.set(self, "encryptedValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plaintextValue")
    def plaintext_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plaintextValue"))

    @plaintext_value.setter
    def plaintext_value(self, value: builtins.str) -> None:
        jsii.set(self, "plaintextValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretName"))

    @secret_name.setter
    def secret_name(self, value: builtins.str) -> None:
        jsii.set(self, "secretName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.ActionsSecretConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "repository": "repository",
        "secret_name": "secretName",
        "encrypted_value": "encryptedValue",
        "plaintext_value": "plaintextValue",
    },
)
class ActionsSecretConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        repository: builtins.str,
        secret_name: builtins.str,
        encrypted_value: typing.Optional[builtins.str] = None,
        plaintext_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#repository ActionsSecret#repository}.
        :param secret_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#secret_name ActionsSecret#secret_name}.
        :param encrypted_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#encrypted_value ActionsSecret#encrypted_value}.
        :param plaintext_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#plaintext_value ActionsSecret#plaintext_value}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "repository": repository,
            "secret_name": secret_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if encrypted_value is not None:
            self._values["encrypted_value"] = encrypted_value
        if plaintext_value is not None:
            self._values["plaintext_value"] = plaintext_value

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#repository ActionsSecret#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#secret_name ActionsSecret#secret_name}.'''
        result = self._values.get("secret_name")
        assert result is not None, "Required property 'secret_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encrypted_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#encrypted_value ActionsSecret#encrypted_value}.'''
        result = self._values.get("encrypted_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plaintext_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/actions_secret.html#plaintext_value ActionsSecret#plaintext_value}.'''
        result = self._values.get("plaintext_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionsSecretConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppInstallationRepository(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.AppInstallationRepository",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/app_installation_repository.html github_app_installation_repository}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        installation_id: builtins.str,
        repository: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/app_installation_repository.html github_app_installation_repository} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param installation_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/app_installation_repository.html#installation_id AppInstallationRepository#installation_id}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/app_installation_repository.html#repository AppInstallationRepository#repository}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AppInstallationRepositoryConfig(
            installation_id=installation_id,
            repository=repository,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(AppInstallationRepository, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installationIdInput")
    def installation_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "installationIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repoId")
    def repo_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "repoId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installationId")
    def installation_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "installationId"))

    @installation_id.setter
    def installation_id(self, value: builtins.str) -> None:
        jsii.set(self, "installationId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.AppInstallationRepositoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "installation_id": "installationId",
        "repository": "repository",
    },
)
class AppInstallationRepositoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        installation_id: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param installation_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/app_installation_repository.html#installation_id AppInstallationRepository#installation_id}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/app_installation_repository.html#repository AppInstallationRepository#repository}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "installation_id": installation_id,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def installation_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/app_installation_repository.html#installation_id AppInstallationRepository#installation_id}.'''
        result = self._values.get("installation_id")
        assert result is not None, "Required property 'installation_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/app_installation_repository.html#repository AppInstallationRepository#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppInstallationRepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Branch(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.Branch",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/branch.html github_branch}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        branch: builtins.str,
        repository: builtins.str,
        source_branch: typing.Optional[builtins.str] = None,
        source_sha: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/branch.html github_branch} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#branch Branch#branch}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#repository Branch#repository}.
        :param source_branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#source_branch Branch#source_branch}.
        :param source_sha: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#source_sha Branch#source_sha}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BranchConfig(
            branch=branch,
            repository=repository,
            source_branch=source_branch,
            source_sha=source_sha,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Branch, self, [scope, id, config])

    @jsii.member(jsii_name="resetSourceBranch")
    def reset_source_branch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceBranch", []))

    @jsii.member(jsii_name="resetSourceSha")
    def reset_source_sha(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceSha", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchInput")
    def branch_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ref")
    def ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ref"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sha")
    def sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceBranchInput")
    def source_branch_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceBranchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceShaInput")
    def source_sha_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceShaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branch")
    def branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branch"))

    @branch.setter
    def branch(self, value: builtins.str) -> None:
        jsii.set(self, "branch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceBranch")
    def source_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceBranch"))

    @source_branch.setter
    def source_branch(self, value: builtins.str) -> None:
        jsii.set(self, "sourceBranch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceSha")
    def source_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceSha"))

    @source_sha.setter
    def source_sha(self, value: builtins.str) -> None:
        jsii.set(self, "sourceSha", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.BranchConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "branch": "branch",
        "repository": "repository",
        "source_branch": "sourceBranch",
        "source_sha": "sourceSha",
    },
)
class BranchConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        branch: builtins.str,
        repository: builtins.str,
        source_branch: typing.Optional[builtins.str] = None,
        source_sha: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#branch Branch#branch}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#repository Branch#repository}.
        :param source_branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#source_branch Branch#source_branch}.
        :param source_sha: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#source_sha Branch#source_sha}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "branch": branch,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if source_branch is not None:
            self._values["source_branch"] = source_branch
        if source_sha is not None:
            self._values["source_sha"] = source_sha

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#branch Branch#branch}.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#repository Branch#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_branch(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#source_branch Branch#source_branch}.'''
        result = self._values.get("source_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_sha(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch.html#source_sha Branch#source_sha}.'''
        result = self._values.get("source_sha")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BranchDefault(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.BranchDefault",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/branch_default.html github_branch_default}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        branch: builtins.str,
        repository: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/branch_default.html github_branch_default} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_default.html#branch BranchDefault#branch}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_default.html#repository BranchDefault#repository}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BranchDefaultConfig(
            branch=branch,
            repository=repository,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(BranchDefault, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchInput")
    def branch_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branch")
    def branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branch"))

    @branch.setter
    def branch(self, value: builtins.str) -> None:
        jsii.set(self, "branch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.BranchDefaultConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "branch": "branch",
        "repository": "repository",
    },
)
class BranchDefaultConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        branch: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_default.html#branch BranchDefault#branch}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_default.html#repository BranchDefault#repository}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "branch": branch,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_default.html#branch BranchDefault#branch}.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_default.html#repository BranchDefault#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchDefaultConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BranchProtection(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.BranchProtection",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html github_branch_protection}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        pattern: builtins.str,
        repository_id: builtins.str,
        allows_deletions: typing.Optional[builtins.bool] = None,
        allows_force_pushes: typing.Optional[builtins.bool] = None,
        enforce_admins: typing.Optional[builtins.bool] = None,
        push_restrictions: typing.Optional[typing.Sequence[builtins.str]] = None,
        required_pull_request_reviews: typing.Optional[typing.Sequence["BranchProtectionRequiredPullRequestReviews"]] = None,
        required_status_checks: typing.Optional[typing.Sequence["BranchProtectionRequiredStatusChecks"]] = None,
        require_signed_commits: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html github_branch_protection} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#pattern BranchProtection#pattern}.
        :param repository_id: Node ID or name of repository. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#repository_id BranchProtection#repository_id}
        :param allows_deletions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#allows_deletions BranchProtection#allows_deletions}.
        :param allows_force_pushes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#allows_force_pushes BranchProtection#allows_force_pushes}.
        :param enforce_admins: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#enforce_admins BranchProtection#enforce_admins}.
        :param push_restrictions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#push_restrictions BranchProtection#push_restrictions}.
        :param required_pull_request_reviews: required_pull_request_reviews block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#required_pull_request_reviews BranchProtection#required_pull_request_reviews}
        :param required_status_checks: required_status_checks block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#required_status_checks BranchProtection#required_status_checks}
        :param require_signed_commits: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#require_signed_commits BranchProtection#require_signed_commits}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BranchProtectionConfig(
            pattern=pattern,
            repository_id=repository_id,
            allows_deletions=allows_deletions,
            allows_force_pushes=allows_force_pushes,
            enforce_admins=enforce_admins,
            push_restrictions=push_restrictions,
            required_pull_request_reviews=required_pull_request_reviews,
            required_status_checks=required_status_checks,
            require_signed_commits=require_signed_commits,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(BranchProtection, self, [scope, id, config])

    @jsii.member(jsii_name="resetAllowsDeletions")
    def reset_allows_deletions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowsDeletions", []))

    @jsii.member(jsii_name="resetAllowsForcePushes")
    def reset_allows_force_pushes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowsForcePushes", []))

    @jsii.member(jsii_name="resetEnforceAdmins")
    def reset_enforce_admins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceAdmins", []))

    @jsii.member(jsii_name="resetPushRestrictions")
    def reset_push_restrictions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPushRestrictions", []))

    @jsii.member(jsii_name="resetRequiredPullRequestReviews")
    def reset_required_pull_request_reviews(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredPullRequestReviews", []))

    @jsii.member(jsii_name="resetRequiredStatusChecks")
    def reset_required_status_checks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredStatusChecks", []))

    @jsii.member(jsii_name="resetRequireSignedCommits")
    def reset_require_signed_commits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireSignedCommits", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="patternInput")
    def pattern_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "patternInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryIdInput")
    def repository_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowsDeletionsInput")
    def allows_deletions_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "allowsDeletionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowsForcePushesInput")
    def allows_force_pushes_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "allowsForcePushesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enforceAdminsInput")
    def enforce_admins_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enforceAdminsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pushRestrictionsInput")
    def push_restrictions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pushRestrictionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredPullRequestReviewsInput")
    def required_pull_request_reviews_input(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionRequiredPullRequestReviews"]]:
        return typing.cast(typing.Optional[typing.List["BranchProtectionRequiredPullRequestReviews"]], jsii.get(self, "requiredPullRequestReviewsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredStatusChecksInput")
    def required_status_checks_input(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionRequiredStatusChecks"]]:
        return typing.cast(typing.Optional[typing.List["BranchProtectionRequiredStatusChecks"]], jsii.get(self, "requiredStatusChecksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSignedCommitsInput")
    def require_signed_commits_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "requireSignedCommitsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowsDeletions")
    def allows_deletions(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "allowsDeletions"))

    @allows_deletions.setter
    def allows_deletions(self, value: builtins.bool) -> None:
        jsii.set(self, "allowsDeletions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowsForcePushes")
    def allows_force_pushes(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "allowsForcePushes"))

    @allows_force_pushes.setter
    def allows_force_pushes(self, value: builtins.bool) -> None:
        jsii.set(self, "allowsForcePushes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enforceAdmins")
    def enforce_admins(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enforceAdmins"))

    @enforce_admins.setter
    def enforce_admins(self, value: builtins.bool) -> None:
        jsii.set(self, "enforceAdmins", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pattern")
    def pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pattern"))

    @pattern.setter
    def pattern(self, value: builtins.str) -> None:
        jsii.set(self, "pattern", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pushRestrictions")
    def push_restrictions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pushRestrictions"))

    @push_restrictions.setter
    def push_restrictions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "pushRestrictions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryId")
    def repository_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryId"))

    @repository_id.setter
    def repository_id(self, value: builtins.str) -> None:
        jsii.set(self, "repositoryId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredPullRequestReviews")
    def required_pull_request_reviews(
        self,
    ) -> typing.List["BranchProtectionRequiredPullRequestReviews"]:
        return typing.cast(typing.List["BranchProtectionRequiredPullRequestReviews"], jsii.get(self, "requiredPullRequestReviews"))

    @required_pull_request_reviews.setter
    def required_pull_request_reviews(
        self,
        value: typing.List["BranchProtectionRequiredPullRequestReviews"],
    ) -> None:
        jsii.set(self, "requiredPullRequestReviews", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredStatusChecks")
    def required_status_checks(
        self,
    ) -> typing.List["BranchProtectionRequiredStatusChecks"]:
        return typing.cast(typing.List["BranchProtectionRequiredStatusChecks"], jsii.get(self, "requiredStatusChecks"))

    @required_status_checks.setter
    def required_status_checks(
        self,
        value: typing.List["BranchProtectionRequiredStatusChecks"],
    ) -> None:
        jsii.set(self, "requiredStatusChecks", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSignedCommits")
    def require_signed_commits(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "requireSignedCommits"))

    @require_signed_commits.setter
    def require_signed_commits(self, value: builtins.bool) -> None:
        jsii.set(self, "requireSignedCommits", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.BranchProtectionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "pattern": "pattern",
        "repository_id": "repositoryId",
        "allows_deletions": "allowsDeletions",
        "allows_force_pushes": "allowsForcePushes",
        "enforce_admins": "enforceAdmins",
        "push_restrictions": "pushRestrictions",
        "required_pull_request_reviews": "requiredPullRequestReviews",
        "required_status_checks": "requiredStatusChecks",
        "require_signed_commits": "requireSignedCommits",
    },
)
class BranchProtectionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        pattern: builtins.str,
        repository_id: builtins.str,
        allows_deletions: typing.Optional[builtins.bool] = None,
        allows_force_pushes: typing.Optional[builtins.bool] = None,
        enforce_admins: typing.Optional[builtins.bool] = None,
        push_restrictions: typing.Optional[typing.Sequence[builtins.str]] = None,
        required_pull_request_reviews: typing.Optional[typing.Sequence["BranchProtectionRequiredPullRequestReviews"]] = None,
        required_status_checks: typing.Optional[typing.Sequence["BranchProtectionRequiredStatusChecks"]] = None,
        require_signed_commits: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#pattern BranchProtection#pattern}.
        :param repository_id: Node ID or name of repository. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#repository_id BranchProtection#repository_id}
        :param allows_deletions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#allows_deletions BranchProtection#allows_deletions}.
        :param allows_force_pushes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#allows_force_pushes BranchProtection#allows_force_pushes}.
        :param enforce_admins: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#enforce_admins BranchProtection#enforce_admins}.
        :param push_restrictions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#push_restrictions BranchProtection#push_restrictions}.
        :param required_pull_request_reviews: required_pull_request_reviews block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#required_pull_request_reviews BranchProtection#required_pull_request_reviews}
        :param required_status_checks: required_status_checks block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#required_status_checks BranchProtection#required_status_checks}
        :param require_signed_commits: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#require_signed_commits BranchProtection#require_signed_commits}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "pattern": pattern,
            "repository_id": repository_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allows_deletions is not None:
            self._values["allows_deletions"] = allows_deletions
        if allows_force_pushes is not None:
            self._values["allows_force_pushes"] = allows_force_pushes
        if enforce_admins is not None:
            self._values["enforce_admins"] = enforce_admins
        if push_restrictions is not None:
            self._values["push_restrictions"] = push_restrictions
        if required_pull_request_reviews is not None:
            self._values["required_pull_request_reviews"] = required_pull_request_reviews
        if required_status_checks is not None:
            self._values["required_status_checks"] = required_status_checks
        if require_signed_commits is not None:
            self._values["require_signed_commits"] = require_signed_commits

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def pattern(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#pattern BranchProtection#pattern}.'''
        result = self._values.get("pattern")
        assert result is not None, "Required property 'pattern' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_id(self) -> builtins.str:
        '''Node ID or name of repository.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#repository_id BranchProtection#repository_id}
        '''
        result = self._values.get("repository_id")
        assert result is not None, "Required property 'repository_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allows_deletions(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#allows_deletions BranchProtection#allows_deletions}.'''
        result = self._values.get("allows_deletions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allows_force_pushes(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#allows_force_pushes BranchProtection#allows_force_pushes}.'''
        result = self._values.get("allows_force_pushes")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enforce_admins(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#enforce_admins BranchProtection#enforce_admins}.'''
        result = self._values.get("enforce_admins")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def push_restrictions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#push_restrictions BranchProtection#push_restrictions}.'''
        result = self._values.get("push_restrictions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def required_pull_request_reviews(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionRequiredPullRequestReviews"]]:
        '''required_pull_request_reviews block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#required_pull_request_reviews BranchProtection#required_pull_request_reviews}
        '''
        result = self._values.get("required_pull_request_reviews")
        return typing.cast(typing.Optional[typing.List["BranchProtectionRequiredPullRequestReviews"]], result)

    @builtins.property
    def required_status_checks(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionRequiredStatusChecks"]]:
        '''required_status_checks block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#required_status_checks BranchProtection#required_status_checks}
        '''
        result = self._values.get("required_status_checks")
        return typing.cast(typing.Optional[typing.List["BranchProtectionRequiredStatusChecks"]], result)

    @builtins.property
    def require_signed_commits(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#require_signed_commits BranchProtection#require_signed_commits}.'''
        result = self._values.get("require_signed_commits")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchProtectionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.BranchProtectionRequiredPullRequestReviews",
    jsii_struct_bases=[],
    name_mapping={
        "dismissal_restrictions": "dismissalRestrictions",
        "dismiss_stale_reviews": "dismissStaleReviews",
        "require_code_owner_reviews": "requireCodeOwnerReviews",
        "required_approving_review_count": "requiredApprovingReviewCount",
        "restrict_dismissals": "restrictDismissals",
    },
)
class BranchProtectionRequiredPullRequestReviews:
    def __init__(
        self,
        *,
        dismissal_restrictions: typing.Optional[typing.Sequence[builtins.str]] = None,
        dismiss_stale_reviews: typing.Optional[builtins.bool] = None,
        require_code_owner_reviews: typing.Optional[builtins.bool] = None,
        required_approving_review_count: typing.Optional[jsii.Number] = None,
        restrict_dismissals: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param dismissal_restrictions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#dismissal_restrictions BranchProtection#dismissal_restrictions}.
        :param dismiss_stale_reviews: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#dismiss_stale_reviews BranchProtection#dismiss_stale_reviews}.
        :param require_code_owner_reviews: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#require_code_owner_reviews BranchProtection#require_code_owner_reviews}.
        :param required_approving_review_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#required_approving_review_count BranchProtection#required_approving_review_count}.
        :param restrict_dismissals: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#restrict_dismissals BranchProtection#restrict_dismissals}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if dismissal_restrictions is not None:
            self._values["dismissal_restrictions"] = dismissal_restrictions
        if dismiss_stale_reviews is not None:
            self._values["dismiss_stale_reviews"] = dismiss_stale_reviews
        if require_code_owner_reviews is not None:
            self._values["require_code_owner_reviews"] = require_code_owner_reviews
        if required_approving_review_count is not None:
            self._values["required_approving_review_count"] = required_approving_review_count
        if restrict_dismissals is not None:
            self._values["restrict_dismissals"] = restrict_dismissals

    @builtins.property
    def dismissal_restrictions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#dismissal_restrictions BranchProtection#dismissal_restrictions}.'''
        result = self._values.get("dismissal_restrictions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dismiss_stale_reviews(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#dismiss_stale_reviews BranchProtection#dismiss_stale_reviews}.'''
        result = self._values.get("dismiss_stale_reviews")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_code_owner_reviews(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#require_code_owner_reviews BranchProtection#require_code_owner_reviews}.'''
        result = self._values.get("require_code_owner_reviews")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def required_approving_review_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#required_approving_review_count BranchProtection#required_approving_review_count}.'''
        result = self._values.get("required_approving_review_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def restrict_dismissals(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#restrict_dismissals BranchProtection#restrict_dismissals}.'''
        result = self._values.get("restrict_dismissals")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchProtectionRequiredPullRequestReviews(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.BranchProtectionRequiredStatusChecks",
    jsii_struct_bases=[],
    name_mapping={"contexts": "contexts", "strict": "strict"},
)
class BranchProtectionRequiredStatusChecks:
    def __init__(
        self,
        *,
        contexts: typing.Optional[typing.Sequence[builtins.str]] = None,
        strict: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param contexts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#contexts BranchProtection#contexts}.
        :param strict: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#strict BranchProtection#strict}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if contexts is not None:
            self._values["contexts"] = contexts
        if strict is not None:
            self._values["strict"] = strict

    @builtins.property
    def contexts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#contexts BranchProtection#contexts}.'''
        result = self._values.get("contexts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def strict(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection.html#strict BranchProtection#strict}.'''
        result = self._values.get("strict")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchProtectionRequiredStatusChecks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BranchProtectionV3(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.BranchProtectionV3",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html github_branch_protection_v3}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        branch: builtins.str,
        repository: builtins.str,
        enforce_admins: typing.Optional[builtins.bool] = None,
        required_pull_request_reviews: typing.Optional[typing.Sequence["BranchProtectionV3RequiredPullRequestReviews"]] = None,
        required_status_checks: typing.Optional[typing.Sequence["BranchProtectionV3RequiredStatusChecks"]] = None,
        require_signed_commits: typing.Optional[builtins.bool] = None,
        restrictions: typing.Optional[typing.Sequence["BranchProtectionV3Restrictions"]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html github_branch_protection_v3} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#branch BranchProtectionV3#branch}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#repository BranchProtectionV3#repository}.
        :param enforce_admins: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#enforce_admins BranchProtectionV3#enforce_admins}.
        :param required_pull_request_reviews: required_pull_request_reviews block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#required_pull_request_reviews BranchProtectionV3#required_pull_request_reviews}
        :param required_status_checks: required_status_checks block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#required_status_checks BranchProtectionV3#required_status_checks}
        :param require_signed_commits: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#require_signed_commits BranchProtectionV3#require_signed_commits}.
        :param restrictions: restrictions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#restrictions BranchProtectionV3#restrictions}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BranchProtectionV3Config(
            branch=branch,
            repository=repository,
            enforce_admins=enforce_admins,
            required_pull_request_reviews=required_pull_request_reviews,
            required_status_checks=required_status_checks,
            require_signed_commits=require_signed_commits,
            restrictions=restrictions,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(BranchProtectionV3, self, [scope, id, config])

    @jsii.member(jsii_name="resetEnforceAdmins")
    def reset_enforce_admins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceAdmins", []))

    @jsii.member(jsii_name="resetRequiredPullRequestReviews")
    def reset_required_pull_request_reviews(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredPullRequestReviews", []))

    @jsii.member(jsii_name="resetRequiredStatusChecks")
    def reset_required_status_checks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredStatusChecks", []))

    @jsii.member(jsii_name="resetRequireSignedCommits")
    def reset_require_signed_commits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireSignedCommits", []))

    @jsii.member(jsii_name="resetRestrictions")
    def reset_restrictions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictions", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchInput")
    def branch_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enforceAdminsInput")
    def enforce_admins_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enforceAdminsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredPullRequestReviewsInput")
    def required_pull_request_reviews_input(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionV3RequiredPullRequestReviews"]]:
        return typing.cast(typing.Optional[typing.List["BranchProtectionV3RequiredPullRequestReviews"]], jsii.get(self, "requiredPullRequestReviewsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredStatusChecksInput")
    def required_status_checks_input(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionV3RequiredStatusChecks"]]:
        return typing.cast(typing.Optional[typing.List["BranchProtectionV3RequiredStatusChecks"]], jsii.get(self, "requiredStatusChecksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSignedCommitsInput")
    def require_signed_commits_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "requireSignedCommitsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictionsInput")
    def restrictions_input(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionV3Restrictions"]]:
        return typing.cast(typing.Optional[typing.List["BranchProtectionV3Restrictions"]], jsii.get(self, "restrictionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branch")
    def branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branch"))

    @branch.setter
    def branch(self, value: builtins.str) -> None:
        jsii.set(self, "branch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enforceAdmins")
    def enforce_admins(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enforceAdmins"))

    @enforce_admins.setter
    def enforce_admins(self, value: builtins.bool) -> None:
        jsii.set(self, "enforceAdmins", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredPullRequestReviews")
    def required_pull_request_reviews(
        self,
    ) -> typing.List["BranchProtectionV3RequiredPullRequestReviews"]:
        return typing.cast(typing.List["BranchProtectionV3RequiredPullRequestReviews"], jsii.get(self, "requiredPullRequestReviews"))

    @required_pull_request_reviews.setter
    def required_pull_request_reviews(
        self,
        value: typing.List["BranchProtectionV3RequiredPullRequestReviews"],
    ) -> None:
        jsii.set(self, "requiredPullRequestReviews", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredStatusChecks")
    def required_status_checks(
        self,
    ) -> typing.List["BranchProtectionV3RequiredStatusChecks"]:
        return typing.cast(typing.List["BranchProtectionV3RequiredStatusChecks"], jsii.get(self, "requiredStatusChecks"))

    @required_status_checks.setter
    def required_status_checks(
        self,
        value: typing.List["BranchProtectionV3RequiredStatusChecks"],
    ) -> None:
        jsii.set(self, "requiredStatusChecks", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSignedCommits")
    def require_signed_commits(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "requireSignedCommits"))

    @require_signed_commits.setter
    def require_signed_commits(self, value: builtins.bool) -> None:
        jsii.set(self, "requireSignedCommits", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictions")
    def restrictions(self) -> typing.List["BranchProtectionV3Restrictions"]:
        return typing.cast(typing.List["BranchProtectionV3Restrictions"], jsii.get(self, "restrictions"))

    @restrictions.setter
    def restrictions(
        self,
        value: typing.List["BranchProtectionV3Restrictions"],
    ) -> None:
        jsii.set(self, "restrictions", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.BranchProtectionV3Config",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "branch": "branch",
        "repository": "repository",
        "enforce_admins": "enforceAdmins",
        "required_pull_request_reviews": "requiredPullRequestReviews",
        "required_status_checks": "requiredStatusChecks",
        "require_signed_commits": "requireSignedCommits",
        "restrictions": "restrictions",
    },
)
class BranchProtectionV3Config(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        branch: builtins.str,
        repository: builtins.str,
        enforce_admins: typing.Optional[builtins.bool] = None,
        required_pull_request_reviews: typing.Optional[typing.Sequence["BranchProtectionV3RequiredPullRequestReviews"]] = None,
        required_status_checks: typing.Optional[typing.Sequence["BranchProtectionV3RequiredStatusChecks"]] = None,
        require_signed_commits: typing.Optional[builtins.bool] = None,
        restrictions: typing.Optional[typing.Sequence["BranchProtectionV3Restrictions"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#branch BranchProtectionV3#branch}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#repository BranchProtectionV3#repository}.
        :param enforce_admins: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#enforce_admins BranchProtectionV3#enforce_admins}.
        :param required_pull_request_reviews: required_pull_request_reviews block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#required_pull_request_reviews BranchProtectionV3#required_pull_request_reviews}
        :param required_status_checks: required_status_checks block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#required_status_checks BranchProtectionV3#required_status_checks}
        :param require_signed_commits: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#require_signed_commits BranchProtectionV3#require_signed_commits}.
        :param restrictions: restrictions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#restrictions BranchProtectionV3#restrictions}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "branch": branch,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if enforce_admins is not None:
            self._values["enforce_admins"] = enforce_admins
        if required_pull_request_reviews is not None:
            self._values["required_pull_request_reviews"] = required_pull_request_reviews
        if required_status_checks is not None:
            self._values["required_status_checks"] = required_status_checks
        if require_signed_commits is not None:
            self._values["require_signed_commits"] = require_signed_commits
        if restrictions is not None:
            self._values["restrictions"] = restrictions

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#branch BranchProtectionV3#branch}.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#repository BranchProtectionV3#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enforce_admins(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#enforce_admins BranchProtectionV3#enforce_admins}.'''
        result = self._values.get("enforce_admins")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def required_pull_request_reviews(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionV3RequiredPullRequestReviews"]]:
        '''required_pull_request_reviews block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#required_pull_request_reviews BranchProtectionV3#required_pull_request_reviews}
        '''
        result = self._values.get("required_pull_request_reviews")
        return typing.cast(typing.Optional[typing.List["BranchProtectionV3RequiredPullRequestReviews"]], result)

    @builtins.property
    def required_status_checks(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionV3RequiredStatusChecks"]]:
        '''required_status_checks block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#required_status_checks BranchProtectionV3#required_status_checks}
        '''
        result = self._values.get("required_status_checks")
        return typing.cast(typing.Optional[typing.List["BranchProtectionV3RequiredStatusChecks"]], result)

    @builtins.property
    def require_signed_commits(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#require_signed_commits BranchProtectionV3#require_signed_commits}.'''
        result = self._values.get("require_signed_commits")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def restrictions(
        self,
    ) -> typing.Optional[typing.List["BranchProtectionV3Restrictions"]]:
        '''restrictions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#restrictions BranchProtectionV3#restrictions}
        '''
        result = self._values.get("restrictions")
        return typing.cast(typing.Optional[typing.List["BranchProtectionV3Restrictions"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchProtectionV3Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.BranchProtectionV3RequiredPullRequestReviews",
    jsii_struct_bases=[],
    name_mapping={
        "dismissal_teams": "dismissalTeams",
        "dismissal_users": "dismissalUsers",
        "dismiss_stale_reviews": "dismissStaleReviews",
        "include_admins": "includeAdmins",
        "require_code_owner_reviews": "requireCodeOwnerReviews",
        "required_approving_review_count": "requiredApprovingReviewCount",
    },
)
class BranchProtectionV3RequiredPullRequestReviews:
    def __init__(
        self,
        *,
        dismissal_teams: typing.Optional[typing.Sequence[builtins.str]] = None,
        dismissal_users: typing.Optional[typing.Sequence[builtins.str]] = None,
        dismiss_stale_reviews: typing.Optional[builtins.bool] = None,
        include_admins: typing.Optional[builtins.bool] = None,
        require_code_owner_reviews: typing.Optional[builtins.bool] = None,
        required_approving_review_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param dismissal_teams: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#dismissal_teams BranchProtectionV3#dismissal_teams}.
        :param dismissal_users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#dismissal_users BranchProtectionV3#dismissal_users}.
        :param dismiss_stale_reviews: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#dismiss_stale_reviews BranchProtectionV3#dismiss_stale_reviews}.
        :param include_admins: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#include_admins BranchProtectionV3#include_admins}.
        :param require_code_owner_reviews: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#require_code_owner_reviews BranchProtectionV3#require_code_owner_reviews}.
        :param required_approving_review_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#required_approving_review_count BranchProtectionV3#required_approving_review_count}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if dismissal_teams is not None:
            self._values["dismissal_teams"] = dismissal_teams
        if dismissal_users is not None:
            self._values["dismissal_users"] = dismissal_users
        if dismiss_stale_reviews is not None:
            self._values["dismiss_stale_reviews"] = dismiss_stale_reviews
        if include_admins is not None:
            self._values["include_admins"] = include_admins
        if require_code_owner_reviews is not None:
            self._values["require_code_owner_reviews"] = require_code_owner_reviews
        if required_approving_review_count is not None:
            self._values["required_approving_review_count"] = required_approving_review_count

    @builtins.property
    def dismissal_teams(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#dismissal_teams BranchProtectionV3#dismissal_teams}.'''
        result = self._values.get("dismissal_teams")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dismissal_users(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#dismissal_users BranchProtectionV3#dismissal_users}.'''
        result = self._values.get("dismissal_users")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dismiss_stale_reviews(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#dismiss_stale_reviews BranchProtectionV3#dismiss_stale_reviews}.'''
        result = self._values.get("dismiss_stale_reviews")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def include_admins(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#include_admins BranchProtectionV3#include_admins}.'''
        result = self._values.get("include_admins")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_code_owner_reviews(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#require_code_owner_reviews BranchProtectionV3#require_code_owner_reviews}.'''
        result = self._values.get("require_code_owner_reviews")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def required_approving_review_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#required_approving_review_count BranchProtectionV3#required_approving_review_count}.'''
        result = self._values.get("required_approving_review_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchProtectionV3RequiredPullRequestReviews(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.BranchProtectionV3RequiredStatusChecks",
    jsii_struct_bases=[],
    name_mapping={
        "contexts": "contexts",
        "include_admins": "includeAdmins",
        "strict": "strict",
    },
)
class BranchProtectionV3RequiredStatusChecks:
    def __init__(
        self,
        *,
        contexts: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_admins: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param contexts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#contexts BranchProtectionV3#contexts}.
        :param include_admins: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#include_admins BranchProtectionV3#include_admins}.
        :param strict: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#strict BranchProtectionV3#strict}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if contexts is not None:
            self._values["contexts"] = contexts
        if include_admins is not None:
            self._values["include_admins"] = include_admins
        if strict is not None:
            self._values["strict"] = strict

    @builtins.property
    def contexts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#contexts BranchProtectionV3#contexts}.'''
        result = self._values.get("contexts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_admins(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#include_admins BranchProtectionV3#include_admins}.'''
        result = self._values.get("include_admins")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def strict(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#strict BranchProtectionV3#strict}.'''
        result = self._values.get("strict")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchProtectionV3RequiredStatusChecks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.BranchProtectionV3Restrictions",
    jsii_struct_bases=[],
    name_mapping={"apps": "apps", "teams": "teams", "users": "users"},
)
class BranchProtectionV3Restrictions:
    def __init__(
        self,
        *,
        apps: typing.Optional[typing.Sequence[builtins.str]] = None,
        teams: typing.Optional[typing.Sequence[builtins.str]] = None,
        users: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param apps: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#apps BranchProtectionV3#apps}.
        :param teams: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#teams BranchProtectionV3#teams}.
        :param users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#users BranchProtectionV3#users}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if apps is not None:
            self._values["apps"] = apps
        if teams is not None:
            self._values["teams"] = teams
        if users is not None:
            self._values["users"] = users

    @builtins.property
    def apps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#apps BranchProtectionV3#apps}.'''
        result = self._values.get("apps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def teams(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#teams BranchProtectionV3#teams}.'''
        result = self._values.get("teams")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def users(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/branch_protection_v3.html#users BranchProtectionV3#users}.'''
        result = self._values.get("users")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchProtectionV3Restrictions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubActionsPublicKey(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubActionsPublicKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/actions_public_key.html github_actions_public_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        repository: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/actions_public_key.html github_actions_public_key} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/actions_public_key.html#repository DataGithubActionsPublicKey#repository}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubActionsPublicKeyConfig(
            repository=repository,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubActionsPublicKey, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubActionsPublicKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "repository": "repository",
    },
)
class DataGithubActionsPublicKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        repository: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/actions_public_key.html#repository DataGithubActionsPublicKey#repository}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/actions_public_key.html#repository DataGithubActionsPublicKey#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubActionsPublicKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubBranch(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubBranch",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/branch.html github_branch}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        branch: builtins.str,
        repository: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/branch.html github_branch} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/branch.html#branch DataGithubBranch#branch}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/branch.html#repository DataGithubBranch#repository}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubBranchConfig(
            branch=branch,
            repository=repository,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubBranch, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchInput")
    def branch_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ref")
    def ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ref"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sha")
    def sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branch")
    def branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branch"))

    @branch.setter
    def branch(self, value: builtins.str) -> None:
        jsii.set(self, "branch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubBranchConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "branch": "branch",
        "repository": "repository",
    },
)
class DataGithubBranchConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        branch: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/branch.html#branch DataGithubBranch#branch}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/branch.html#repository DataGithubBranch#repository}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "branch": branch,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/branch.html#branch DataGithubBranch#branch}.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/branch.html#repository DataGithubBranch#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubBranchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubCollaborators(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubCollaborators",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/collaborators.html github_collaborators}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        owner: builtins.str,
        repository: builtins.str,
        affiliation: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/collaborators.html github_collaborators} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/collaborators.html#owner DataGithubCollaborators#owner}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/collaborators.html#repository DataGithubCollaborators#repository}.
        :param affiliation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/collaborators.html#affiliation DataGithubCollaborators#affiliation}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubCollaboratorsConfig(
            owner=owner,
            repository=repository,
            affiliation=affiliation,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubCollaborators, self, [scope, id, config])

    @jsii.member(jsii_name="collaborator")
    def collaborator(
        self,
        index: builtins.str,
    ) -> "DataGithubCollaboratorsCollaborator":
        '''
        :param index: -
        '''
        return typing.cast("DataGithubCollaboratorsCollaborator", jsii.invoke(self, "collaborator", [index]))

    @jsii.member(jsii_name="resetAffiliation")
    def reset_affiliation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAffiliation", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="affiliationInput")
    def affiliation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "affiliationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="affiliation")
    def affiliation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "affiliation"))

    @affiliation.setter
    def affiliation(self, value: builtins.str) -> None:
        jsii.set(self, "affiliation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


class DataGithubCollaboratorsCollaborator(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubCollaboratorsCollaborator",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(DataGithubCollaboratorsCollaborator, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventsUrl")
    def events_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventsUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="followersUrl")
    def followers_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "followersUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="followingUrl")
    def following_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "followingUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gistsUrl")
    def gists_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gistsUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="login")
    def login(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "login"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationsUrl")
    def organizations_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationsUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="receivedEventsUrl")
    def received_events_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "receivedEventsUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reposUrl")
    def repos_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reposUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="siteAdmin")
    def site_admin(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "siteAdmin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="starredUrl")
    def starred_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "starredUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriptionsUrl")
    def subscriptions_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionsUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubCollaboratorsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "owner": "owner",
        "repository": "repository",
        "affiliation": "affiliation",
    },
)
class DataGithubCollaboratorsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        owner: builtins.str,
        repository: builtins.str,
        affiliation: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/collaborators.html#owner DataGithubCollaborators#owner}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/collaborators.html#repository DataGithubCollaborators#repository}.
        :param affiliation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/collaborators.html#affiliation DataGithubCollaborators#affiliation}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "owner": owner,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if affiliation is not None:
            self._values["affiliation"] = affiliation

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/collaborators.html#owner DataGithubCollaborators#owner}.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/collaborators.html#repository DataGithubCollaborators#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def affiliation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/collaborators.html#affiliation DataGithubCollaborators#affiliation}.'''
        result = self._values.get("affiliation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubCollaboratorsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubIpRanges(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubIpRanges",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/ip_ranges.html github_ip_ranges}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/ip_ranges.html github_ip_ranges} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubIpRangesConfig(
            count=count, depends_on=depends_on, lifecycle=lifecycle, provider=provider
        )

        jsii.create(DataGithubIpRanges, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "actions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dependabot")
    def dependabot(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dependabot"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="git")
    def git(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "git"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hooks")
    def hooks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "hooks"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="importer")
    def importer(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "importer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pages")
    def pages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pages"))


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubIpRangesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
    },
)
class DataGithubIpRangesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubIpRangesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubMembership(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubMembership",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/membership.html github_membership}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        username: builtins.str,
        organization: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/membership.html github_membership} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/membership.html#username DataGithubMembership#username}.
        :param organization: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/membership.html#organization DataGithubMembership#organization}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubMembershipConfig(
            username=username,
            organization=organization,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubMembership, self, [scope, id, config])

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationInput")
    def organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organization")
    def organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: builtins.str) -> None:
        jsii.set(self, "organization", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubMembershipConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "username": "username",
        "organization": "organization",
    },
)
class DataGithubMembershipConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        username: builtins.str,
        organization: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/membership.html#username DataGithubMembership#username}.
        :param organization: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/membership.html#organization DataGithubMembership#organization}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "username": username,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if organization is not None:
            self._values["organization"] = organization

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/membership.html#username DataGithubMembership#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/membership.html#organization DataGithubMembership#organization}.'''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubMembershipConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubOrganization(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubOrganization",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/organization.html github_organization}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/organization.html github_organization} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/organization.html#name DataGithubOrganization#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubOrganizationConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubOrganization, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="login")
    def login(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "login"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="members")
    def members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "members"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositories")
    def repositories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "repositories"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubOrganizationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataGithubOrganizationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/organization.html#name DataGithubOrganization#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/organization.html#name DataGithubOrganization#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubOrganizationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubOrganizationTeamSyncGroups(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubOrganizationTeamSyncGroups",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/organization_team_sync_groups.html github_organization_team_sync_groups}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/organization_team_sync_groups.html github_organization_team_sync_groups} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubOrganizationTeamSyncGroupsConfig(
            count=count, depends_on=depends_on, lifecycle=lifecycle, provider=provider
        )

        jsii.create(DataGithubOrganizationTeamSyncGroups, self, [scope, id, config])

    @jsii.member(jsii_name="groups")
    def groups(
        self,
        index: builtins.str,
    ) -> "DataGithubOrganizationTeamSyncGroupsGroups":
        '''
        :param index: -
        '''
        return typing.cast("DataGithubOrganizationTeamSyncGroupsGroups", jsii.invoke(self, "groups", [index]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubOrganizationTeamSyncGroupsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
    },
)
class DataGithubOrganizationTeamSyncGroupsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubOrganizationTeamSyncGroupsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubOrganizationTeamSyncGroupsGroups(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubOrganizationTeamSyncGroupsGroups",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(DataGithubOrganizationTeamSyncGroupsGroups, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupDescription")
    def group_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupDescription"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupName"))


class DataGithubOrganizationTeams(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubOrganizationTeams",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/organization_teams.html github_organization_teams}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        root_teams_only: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/organization_teams.html github_organization_teams} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param root_teams_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/organization_teams.html#root_teams_only DataGithubOrganizationTeams#root_teams_only}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubOrganizationTeamsConfig(
            root_teams_only=root_teams_only,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubOrganizationTeams, self, [scope, id, config])

    @jsii.member(jsii_name="resetRootTeamsOnly")
    def reset_root_teams_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootTeamsOnly", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="teams")
    def teams(self, index: builtins.str) -> "DataGithubOrganizationTeamsTeams":
        '''
        :param index: -
        '''
        return typing.cast("DataGithubOrganizationTeamsTeams", jsii.invoke(self, "teams", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootTeamsOnlyInput")
    def root_teams_only_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "rootTeamsOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootTeamsOnly")
    def root_teams_only(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "rootTeamsOnly"))

    @root_teams_only.setter
    def root_teams_only(self, value: builtins.bool) -> None:
        jsii.set(self, "rootTeamsOnly", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubOrganizationTeamsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "root_teams_only": "rootTeamsOnly",
    },
)
class DataGithubOrganizationTeamsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        root_teams_only: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param root_teams_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/organization_teams.html#root_teams_only DataGithubOrganizationTeams#root_teams_only}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if root_teams_only is not None:
            self._values["root_teams_only"] = root_teams_only

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def root_teams_only(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/organization_teams.html#root_teams_only DataGithubOrganizationTeams#root_teams_only}.'''
        result = self._values.get("root_teams_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubOrganizationTeamsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubOrganizationTeamsTeams(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubOrganizationTeamsTeams",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(DataGithubOrganizationTeamsTeams, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="members")
    def members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "members"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privacy")
    def privacy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privacy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositories")
    def repositories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "repositories"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slug")
    def slug(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "slug"))


class DataGithubRelease(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubRelease",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/release.html github_release}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        owner: builtins.str,
        repository: builtins.str,
        retrieve_by: builtins.str,
        release_id: typing.Optional[jsii.Number] = None,
        release_tag: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/release.html github_release} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#owner DataGithubRelease#owner}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#repository DataGithubRelease#repository}.
        :param retrieve_by: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#retrieve_by DataGithubRelease#retrieve_by}.
        :param release_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#release_id DataGithubRelease#release_id}.
        :param release_tag: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#release_tag DataGithubRelease#release_tag}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubReleaseConfig(
            owner=owner,
            repository=repository,
            retrieve_by=retrieve_by,
            release_id=release_id,
            release_tag=release_tag,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubRelease, self, [scope, id, config])

    @jsii.member(jsii_name="resetReleaseId")
    def reset_release_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReleaseId", []))

    @jsii.member(jsii_name="resetReleaseTag")
    def reset_release_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReleaseTag", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="assertsUrl")
    def asserts_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "assertsUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="draft")
    def draft(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "draft"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prerelease")
    def prerelease(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "prerelease"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishedAt")
    def published_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publishedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retrieveByInput")
    def retrieve_by_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retrieveByInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tarballUrl")
    def tarball_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tarballUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetCommitish")
    def target_commitish(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetCommitish"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uploadUrl")
    def upload_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uploadUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zipballUrl")
    def zipball_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zipballUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="releaseIdInput")
    def release_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "releaseIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="releaseTagInput")
    def release_tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "releaseTagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="releaseId")
    def release_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "releaseId"))

    @release_id.setter
    def release_id(self, value: jsii.Number) -> None:
        jsii.set(self, "releaseId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="releaseTag")
    def release_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "releaseTag"))

    @release_tag.setter
    def release_tag(self, value: builtins.str) -> None:
        jsii.set(self, "releaseTag", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retrieveBy")
    def retrieve_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retrieveBy"))

    @retrieve_by.setter
    def retrieve_by(self, value: builtins.str) -> None:
        jsii.set(self, "retrieveBy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubReleaseConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "owner": "owner",
        "repository": "repository",
        "retrieve_by": "retrieveBy",
        "release_id": "releaseId",
        "release_tag": "releaseTag",
    },
)
class DataGithubReleaseConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        owner: builtins.str,
        repository: builtins.str,
        retrieve_by: builtins.str,
        release_id: typing.Optional[jsii.Number] = None,
        release_tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#owner DataGithubRelease#owner}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#repository DataGithubRelease#repository}.
        :param retrieve_by: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#retrieve_by DataGithubRelease#retrieve_by}.
        :param release_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#release_id DataGithubRelease#release_id}.
        :param release_tag: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#release_tag DataGithubRelease#release_tag}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "owner": owner,
            "repository": repository,
            "retrieve_by": retrieve_by,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if release_id is not None:
            self._values["release_id"] = release_id
        if release_tag is not None:
            self._values["release_tag"] = release_tag

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#owner DataGithubRelease#owner}.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#repository DataGithubRelease#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retrieve_by(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#retrieve_by DataGithubRelease#retrieve_by}.'''
        result = self._values.get("retrieve_by")
        assert result is not None, "Required property 'retrieve_by' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def release_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#release_id DataGithubRelease#release_id}.'''
        result = self._values.get("release_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def release_tag(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/release.html#release_tag DataGithubRelease#release_tag}.'''
        result = self._values.get("release_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubReleaseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubRepositories(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubRepositories",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/repositories.html github_repositories}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        query: builtins.str,
        sort: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/repositories.html github_repositories} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repositories.html#query DataGithubRepositories#query}.
        :param sort: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repositories.html#sort DataGithubRepositories#sort}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubRepositoriesConfig(
            query=query,
            sort=sort,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubRepositories, self, [scope, id, config])

    @jsii.member(jsii_name="resetSort")
    def reset_sort(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSort", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fullNames")
    def full_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "fullNames"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="names")
    def names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "names"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryInput")
    def query_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sortInput")
    def sort_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="query")
    def query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "query"))

    @query.setter
    def query(self, value: builtins.str) -> None:
        jsii.set(self, "query", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sort")
    def sort(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sort"))

    @sort.setter
    def sort(self, value: builtins.str) -> None:
        jsii.set(self, "sort", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubRepositoriesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "query": "query",
        "sort": "sort",
    },
)
class DataGithubRepositoriesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        query: builtins.str,
        sort: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repositories.html#query DataGithubRepositories#query}.
        :param sort: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repositories.html#sort DataGithubRepositories#sort}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if sort is not None:
            self._values["sort"] = sort

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repositories.html#query DataGithubRepositories#query}.'''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sort(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repositories.html#sort DataGithubRepositories#sort}.'''
        result = self._values.get("sort")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubRepositoriesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubRepository(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubRepository",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/repository.html github_repository}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        full_name: typing.Optional[builtins.str] = None,
        homepage_url: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/repository.html github_repository} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#description DataGithubRepository#description}.
        :param full_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#full_name DataGithubRepository#full_name}.
        :param homepage_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#homepage_url DataGithubRepository#homepage_url}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#name DataGithubRepository#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubRepositoryConfig(
            description=description,
            full_name=full_name,
            homepage_url=homepage_url,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubRepository, self, [scope, id, config])

    @jsii.member(jsii_name="pages")
    def pages(self, index: builtins.str) -> "DataGithubRepositoryPages":
        '''
        :param index: -
        '''
        return typing.cast("DataGithubRepositoryPages", jsii.invoke(self, "pages", [index]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFullName")
    def reset_full_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFullName", []))

    @jsii.member(jsii_name="resetHomepageUrl")
    def reset_homepage_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomepageUrl", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMergeCommit")
    def allow_merge_commit(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "allowMergeCommit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowRebaseMerge")
    def allow_rebase_merge(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "allowRebaseMerge"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowSquashMerge")
    def allow_squash_merge(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "allowSquashMerge"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="archived")
    def archived(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "archived"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultBranch")
    def default_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultBranch"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gitCloneUrl")
    def git_clone_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitCloneUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasDownloads")
    def has_downloads(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasDownloads"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasIssues")
    def has_issues(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasIssues"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasProjects")
    def has_projects(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasProjects"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasWiki")
    def has_wiki(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasWiki"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpCloneUrl")
    def http_clone_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpCloneUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="private")
    def private(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "private"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repoId")
    def repo_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "repoId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshCloneUrl")
    def ssh_clone_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshCloneUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svnUrl")
    def svn_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "svnUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topics")
    def topics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "topics"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fullNameInput")
    def full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fullNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homepageUrlInput")
    def homepage_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homepageUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fullName")
    def full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullName"))

    @full_name.setter
    def full_name(self, value: builtins.str) -> None:
        jsii.set(self, "fullName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homepageUrl")
    def homepage_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homepageUrl"))

    @homepage_url.setter
    def homepage_url(self, value: builtins.str) -> None:
        jsii.set(self, "homepageUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubRepositoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "description": "description",
        "full_name": "fullName",
        "homepage_url": "homepageUrl",
        "name": "name",
    },
)
class DataGithubRepositoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        description: typing.Optional[builtins.str] = None,
        full_name: typing.Optional[builtins.str] = None,
        homepage_url: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#description DataGithubRepository#description}.
        :param full_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#full_name DataGithubRepository#full_name}.
        :param homepage_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#homepage_url DataGithubRepository#homepage_url}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#name DataGithubRepository#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if full_name is not None:
            self._values["full_name"] = full_name
        if homepage_url is not None:
            self._values["homepage_url"] = homepage_url
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#description DataGithubRepository#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def full_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#full_name DataGithubRepository#full_name}.'''
        result = self._values.get("full_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#homepage_url DataGithubRepository#homepage_url}.'''
        result = self._values.get("homepage_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository.html#name DataGithubRepository#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubRepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubRepositoryMilestone(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubRepositoryMilestone",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html github_repository_milestone}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        number: jsii.Number,
        owner: builtins.str,
        repository: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html github_repository_milestone} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html#number DataGithubRepositoryMilestone#number}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html#owner DataGithubRepositoryMilestone#owner}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html#repository DataGithubRepositoryMilestone#repository}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubRepositoryMilestoneConfig(
            number=number,
            owner=owner,
            repository=repository,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubRepositoryMilestone, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dueDate")
    def due_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dueDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberInput")
    def number_input(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="number")
    def number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "number"))

    @number.setter
    def number(self, value: jsii.Number) -> None:
        jsii.set(self, "number", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubRepositoryMilestoneConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "number": "number",
        "owner": "owner",
        "repository": "repository",
    },
)
class DataGithubRepositoryMilestoneConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        number: jsii.Number,
        owner: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html#number DataGithubRepositoryMilestone#number}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html#owner DataGithubRepositoryMilestone#owner}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html#repository DataGithubRepositoryMilestone#repository}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "number": number,
            "owner": owner,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def number(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html#number DataGithubRepositoryMilestone#number}.'''
        result = self._values.get("number")
        assert result is not None, "Required property 'number' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html#owner DataGithubRepositoryMilestone#owner}.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_milestone.html#repository DataGithubRepositoryMilestone#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubRepositoryMilestoneConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubRepositoryPages(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubRepositoryPages",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(DataGithubRepositoryPages, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cname")
    def cname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cname"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="custom404")
    def custom404(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "custom404"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))


class DataGithubRepositoryPagesSource(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubRepositoryPagesSource",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(DataGithubRepositoryPagesSource, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branch")
    def branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branch"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))


class DataGithubRepositoryPullRequest(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubRepositoryPullRequest",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html github_repository_pull_request}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        base_repository: builtins.str,
        number: jsii.Number,
        owner: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html github_repository_pull_request} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param base_repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html#base_repository DataGithubRepositoryPullRequest#base_repository}.
        :param number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html#number DataGithubRepositoryPullRequest#number}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html#owner DataGithubRepositoryPullRequest#owner}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubRepositoryPullRequestConfig(
            base_repository=base_repository,
            number=number,
            owner=owner,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubRepositoryPullRequest, self, [scope, id, config])

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRef")
    def base_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRef"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRepositoryInput")
    def base_repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRepositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseSha")
    def base_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="draft")
    def draft(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "draft"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headOwner")
    def head_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headOwner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headRef")
    def head_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headRef"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headRepository")
    def head_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headRepository"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headSha")
    def head_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "labels"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintainerCanModify")
    def maintainer_can_modify(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "maintainerCanModify"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberInput")
    def number_input(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openedAt")
    def opened_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "openedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openedBy")
    def opened_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRepository")
    def base_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRepository"))

    @base_repository.setter
    def base_repository(self, value: builtins.str) -> None:
        jsii.set(self, "baseRepository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="number")
    def number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "number"))

    @number.setter
    def number(self, value: jsii.Number) -> None:
        jsii.set(self, "number", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubRepositoryPullRequestConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "base_repository": "baseRepository",
        "number": "number",
        "owner": "owner",
    },
)
class DataGithubRepositoryPullRequestConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        base_repository: builtins.str,
        number: jsii.Number,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param base_repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html#base_repository DataGithubRepositoryPullRequest#base_repository}.
        :param number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html#number DataGithubRepositoryPullRequest#number}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html#owner DataGithubRepositoryPullRequest#owner}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "base_repository": base_repository,
            "number": number,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if owner is not None:
            self._values["owner"] = owner

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def base_repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html#base_repository DataGithubRepositoryPullRequest#base_repository}.'''
        result = self._values.get("base_repository")
        assert result is not None, "Required property 'base_repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html#number DataGithubRepositoryPullRequest#number}.'''
        result = self._values.get("number")
        assert result is not None, "Required property 'number' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_request.html#owner DataGithubRepositoryPullRequest#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubRepositoryPullRequestConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubRepositoryPullRequests(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubRepositoryPullRequests",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html github_repository_pull_requests}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        base_repository: builtins.str,
        base_ref: typing.Optional[builtins.str] = None,
        head_ref: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        sort_by: typing.Optional[builtins.str] = None,
        sort_direction: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html github_repository_pull_requests} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param base_repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#base_repository DataGithubRepositoryPullRequests#base_repository}.
        :param base_ref: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#base_ref DataGithubRepositoryPullRequests#base_ref}.
        :param head_ref: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#head_ref DataGithubRepositoryPullRequests#head_ref}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#owner DataGithubRepositoryPullRequests#owner}.
        :param sort_by: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#sort_by DataGithubRepositoryPullRequests#sort_by}.
        :param sort_direction: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#sort_direction DataGithubRepositoryPullRequests#sort_direction}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#state DataGithubRepositoryPullRequests#state}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubRepositoryPullRequestsConfig(
            base_repository=base_repository,
            base_ref=base_ref,
            head_ref=head_ref,
            owner=owner,
            sort_by=sort_by,
            sort_direction=sort_direction,
            state=state,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubRepositoryPullRequests, self, [scope, id, config])

    @jsii.member(jsii_name="resetBaseRef")
    def reset_base_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseRef", []))

    @jsii.member(jsii_name="resetHeadRef")
    def reset_head_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeadRef", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="resetSortBy")
    def reset_sort_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSortBy", []))

    @jsii.member(jsii_name="resetSortDirection")
    def reset_sort_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSortDirection", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="results")
    def results(self, index: builtins.str) -> "DataGithubRepositoryPullRequestsResults":
        '''
        :param index: -
        '''
        return typing.cast("DataGithubRepositoryPullRequestsResults", jsii.invoke(self, "results", [index]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRepositoryInput")
    def base_repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRepositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRefInput")
    def base_ref_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseRefInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headRefInput")
    def head_ref_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headRefInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sortByInput")
    def sort_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sortByInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sortDirectionInput")
    def sort_direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sortDirectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRef")
    def base_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRef"))

    @base_ref.setter
    def base_ref(self, value: builtins.str) -> None:
        jsii.set(self, "baseRef", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRepository")
    def base_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRepository"))

    @base_repository.setter
    def base_repository(self, value: builtins.str) -> None:
        jsii.set(self, "baseRepository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headRef")
    def head_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headRef"))

    @head_ref.setter
    def head_ref(self, value: builtins.str) -> None:
        jsii.set(self, "headRef", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sortBy")
    def sort_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sortBy"))

    @sort_by.setter
    def sort_by(self, value: builtins.str) -> None:
        jsii.set(self, "sortBy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sortDirection")
    def sort_direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sortDirection"))

    @sort_direction.setter
    def sort_direction(self, value: builtins.str) -> None:
        jsii.set(self, "sortDirection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        jsii.set(self, "state", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubRepositoryPullRequestsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "base_repository": "baseRepository",
        "base_ref": "baseRef",
        "head_ref": "headRef",
        "owner": "owner",
        "sort_by": "sortBy",
        "sort_direction": "sortDirection",
        "state": "state",
    },
)
class DataGithubRepositoryPullRequestsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        base_repository: builtins.str,
        base_ref: typing.Optional[builtins.str] = None,
        head_ref: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        sort_by: typing.Optional[builtins.str] = None,
        sort_direction: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param base_repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#base_repository DataGithubRepositoryPullRequests#base_repository}.
        :param base_ref: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#base_ref DataGithubRepositoryPullRequests#base_ref}.
        :param head_ref: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#head_ref DataGithubRepositoryPullRequests#head_ref}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#owner DataGithubRepositoryPullRequests#owner}.
        :param sort_by: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#sort_by DataGithubRepositoryPullRequests#sort_by}.
        :param sort_direction: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#sort_direction DataGithubRepositoryPullRequests#sort_direction}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#state DataGithubRepositoryPullRequests#state}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "base_repository": base_repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if base_ref is not None:
            self._values["base_ref"] = base_ref
        if head_ref is not None:
            self._values["head_ref"] = head_ref
        if owner is not None:
            self._values["owner"] = owner
        if sort_by is not None:
            self._values["sort_by"] = sort_by
        if sort_direction is not None:
            self._values["sort_direction"] = sort_direction
        if state is not None:
            self._values["state"] = state

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def base_repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#base_repository DataGithubRepositoryPullRequests#base_repository}.'''
        result = self._values.get("base_repository")
        assert result is not None, "Required property 'base_repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def base_ref(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#base_ref DataGithubRepositoryPullRequests#base_ref}.'''
        result = self._values.get("base_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def head_ref(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#head_ref DataGithubRepositoryPullRequests#head_ref}.'''
        result = self._values.get("head_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#owner DataGithubRepositoryPullRequests#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sort_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#sort_by DataGithubRepositoryPullRequests#sort_by}.'''
        result = self._values.get("sort_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sort_direction(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#sort_direction DataGithubRepositoryPullRequests#sort_direction}.'''
        result = self._values.get("sort_direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/repository_pull_requests.html#state DataGithubRepositoryPullRequests#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubRepositoryPullRequestsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubRepositoryPullRequestsResults(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubRepositoryPullRequestsResults",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(DataGithubRepositoryPullRequestsResults, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRef")
    def base_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRef"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseSha")
    def base_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="draft")
    def draft(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "draft"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headOwner")
    def head_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headOwner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headRef")
    def head_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headRef"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headRepository")
    def head_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headRepository"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headSha")
    def head_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "labels"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintainerCanModify")
    def maintainer_can_modify(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "maintainerCanModify"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="number")
    def number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "number"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openedAt")
    def opened_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "openedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openedBy")
    def opened_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))


class DataGithubTeam(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubTeam",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/team.html github_team}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        slug: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/team.html github_team} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param slug: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/team.html#slug DataGithubTeam#slug}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubTeamConfig(
            slug=slug,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubTeam, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="members")
    def members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "members"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privacy")
    def privacy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privacy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositories")
    def repositories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "repositories"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slugInput")
    def slug_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "slugInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slug")
    def slug(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "slug"))

    @slug.setter
    def slug(self, value: builtins.str) -> None:
        jsii.set(self, "slug", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubTeamConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "slug": "slug",
    },
)
class DataGithubTeamConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        slug: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param slug: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/team.html#slug DataGithubTeam#slug}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "slug": slug,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def slug(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/team.html#slug DataGithubTeam#slug}.'''
        result = self._values.get("slug")
        assert result is not None, "Required property 'slug' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubTeamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGithubUser(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.DataGithubUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/d/user.html github_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        username: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/d/user.html github_user} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/user.html#username DataGithubUser#username}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataGithubUserConfig(
            username=username,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataGithubUser, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="avatarUrl")
    def avatar_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "avatarUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bio")
    def bio(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bio"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blog")
    def blog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "blog"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="company")
    def company(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "company"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="followers")
    def followers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "followers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="following")
    def following(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "following"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gpgKeys")
    def gpg_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gpgKeys"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gravatarId")
    def gravatar_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gravatarId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="login")
    def login(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "login"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicGists")
    def public_gists(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "publicGists"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicRepos")
    def public_repos(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "publicRepos"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="siteAdmin")
    def site_admin(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "siteAdmin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshKeys")
    def ssh_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sshKeys"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.DataGithubUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "username": "username",
    },
)
class DataGithubUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        username: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/user.html#username DataGithubUser#username}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "username": username,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/d/user.html#username DataGithubUser#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGithubUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GithubProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.GithubProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github github}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        app_auth: typing.Optional[typing.Sequence["GithubProviderAppAuth"]] = None,
        base_url: typing.Optional[builtins.str] = None,
        insecure: typing.Optional[builtins.bool] = None,
        organization: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github github} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#alias GithubProvider#alias}
        :param app_auth: app_auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#app_auth GithubProvider#app_auth}
        :param base_url: The GitHub Base API URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#base_url GithubProvider#base_url}
        :param insecure: Enable ``insecure`` mode for testing purposes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#insecure GithubProvider#insecure}
        :param organization: The GitHub organization name to manage. Use this field instead of ``owner`` when managing organization accounts. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#organization GithubProvider#organization}
        :param owner: The GitHub owner name to manage. Use this field instead of ``organization`` when managing individual accounts. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#owner GithubProvider#owner}
        :param token: The OAuth token used to connect to GitHub. Anonymous mode is enabled if both ``token`` and ``app_auth`` are not set. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#token GithubProvider#token}
        '''
        config = GithubProviderConfig(
            alias=alias,
            app_auth=app_auth,
            base_url=base_url,
            insecure=insecure,
            organization=organization,
            owner=owner,
            token=token,
        )

        jsii.create(GithubProvider, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetAppAuth")
    def reset_app_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppAuth", []))

    @jsii.member(jsii_name="resetBaseUrl")
    def reset_base_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseUrl", []))

    @jsii.member(jsii_name="resetInsecure")
    def reset_insecure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecure", []))

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appAuthInput")
    def app_auth_input(self) -> typing.Optional[typing.List["GithubProviderAppAuth"]]:
        return typing.cast(typing.Optional[typing.List["GithubProviderAppAuth"]], jsii.get(self, "appAuthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseUrlInput")
    def base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureInput")
    def insecure_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "insecureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationInput")
    def organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appAuth")
    def app_auth(self) -> typing.Optional[typing.List["GithubProviderAppAuth"]]:
        return typing.cast(typing.Optional[typing.List["GithubProviderAppAuth"]], jsii.get(self, "appAuth"))

    @app_auth.setter
    def app_auth(
        self,
        value: typing.Optional[typing.List["GithubProviderAppAuth"]],
    ) -> None:
        jsii.set(self, "appAuth", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrl"))

    @base_url.setter
    def base_url(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "baseUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecure")
    def insecure(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "insecure"))

    @insecure.setter
    def insecure(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "insecure", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organization")
    def organization(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "organization", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="token")
    def token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "token"))

    @token.setter
    def token(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "token", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.GithubProviderAppAuth",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "installation_id": "installationId",
        "pem_file": "pemFile",
    },
)
class GithubProviderAppAuth:
    def __init__(
        self,
        *,
        id: builtins.str,
        installation_id: builtins.str,
        pem_file: builtins.str,
    ) -> None:
        '''
        :param id: The GitHub App ID. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#id GithubProvider#id}
        :param installation_id: The GitHub App installation instance ID. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#installation_id GithubProvider#installation_id}
        :param pem_file: The GitHub App PEM file contents. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#pem_file GithubProvider#pem_file}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "installation_id": installation_id,
            "pem_file": pem_file,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The GitHub App ID.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#id GithubProvider#id}
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def installation_id(self) -> builtins.str:
        '''The GitHub App installation instance ID.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#installation_id GithubProvider#installation_id}
        '''
        result = self._values.get("installation_id")
        assert result is not None, "Required property 'installation_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pem_file(self) -> builtins.str:
        '''The GitHub App PEM file contents.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#pem_file GithubProvider#pem_file}
        '''
        result = self._values.get("pem_file")
        assert result is not None, "Required property 'pem_file' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubProviderAppAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.GithubProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alias": "alias",
        "app_auth": "appAuth",
        "base_url": "baseUrl",
        "insecure": "insecure",
        "organization": "organization",
        "owner": "owner",
        "token": "token",
    },
)
class GithubProviderConfig:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        app_auth: typing.Optional[typing.Sequence[GithubProviderAppAuth]] = None,
        base_url: typing.Optional[builtins.str] = None,
        insecure: typing.Optional[builtins.bool] = None,
        organization: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#alias GithubProvider#alias}
        :param app_auth: app_auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#app_auth GithubProvider#app_auth}
        :param base_url: The GitHub Base API URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#base_url GithubProvider#base_url}
        :param insecure: Enable ``insecure`` mode for testing purposes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#insecure GithubProvider#insecure}
        :param organization: The GitHub organization name to manage. Use this field instead of ``owner`` when managing organization accounts. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#organization GithubProvider#organization}
        :param owner: The GitHub owner name to manage. Use this field instead of ``organization`` when managing individual accounts. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#owner GithubProvider#owner}
        :param token: The OAuth token used to connect to GitHub. Anonymous mode is enabled if both ``token`` and ``app_auth`` are not set. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#token GithubProvider#token}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if app_auth is not None:
            self._values["app_auth"] = app_auth
        if base_url is not None:
            self._values["base_url"] = base_url
        if insecure is not None:
            self._values["insecure"] = insecure
        if organization is not None:
            self._values["organization"] = organization
        if owner is not None:
            self._values["owner"] = owner
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#alias GithubProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_auth(self) -> typing.Optional[typing.List[GithubProviderAppAuth]]:
        '''app_auth block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#app_auth GithubProvider#app_auth}
        '''
        result = self._values.get("app_auth")
        return typing.cast(typing.Optional[typing.List[GithubProviderAppAuth]], result)

    @builtins.property
    def base_url(self) -> typing.Optional[builtins.str]:
        '''The GitHub Base API URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#base_url GithubProvider#base_url}
        '''
        result = self._values.get("base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure(self) -> typing.Optional[builtins.bool]:
        '''Enable ``insecure`` mode for testing purposes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#insecure GithubProvider#insecure}
        '''
        result = self._values.get("insecure")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''The GitHub organization name to manage. Use this field instead of ``owner`` when managing organization accounts.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#organization GithubProvider#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''The GitHub owner name to manage. Use this field instead of ``organization`` when managing individual accounts.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#owner GithubProvider#owner}
        '''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''The OAuth token used to connect to GitHub.

        Anonymous mode is enabled if both ``token`` and ``app_auth`` are not set.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github#token GithubProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IssueLabel(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.IssueLabel",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/issue_label.html github_issue_label}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        color: builtins.str,
        name: builtins.str,
        repository: builtins.str,
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/issue_label.html github_issue_label} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param color: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#color IssueLabel#color}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#name IssueLabel#name}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#repository IssueLabel#repository}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#description IssueLabel#description}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IssueLabelConfig(
            color=color,
            name=name,
            repository=repository,
            description=description,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(IssueLabel, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="colorInput")
    def color_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "colorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="color")
    def color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "color"))

    @color.setter
    def color(self, value: builtins.str) -> None:
        jsii.set(self, "color", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.IssueLabelConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "color": "color",
        "name": "name",
        "repository": "repository",
        "description": "description",
    },
)
class IssueLabelConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        color: builtins.str,
        name: builtins.str,
        repository: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param color: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#color IssueLabel#color}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#name IssueLabel#name}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#repository IssueLabel#repository}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#description IssueLabel#description}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "color": color,
            "name": name,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def color(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#color IssueLabel#color}.'''
        result = self._values.get("color")
        assert result is not None, "Required property 'color' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#name IssueLabel#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#repository IssueLabel#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/issue_label.html#description IssueLabel#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IssueLabelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Membership(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.Membership",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/membership.html github_membership}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        username: builtins.str,
        role: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/membership.html github_membership} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/membership.html#username Membership#username}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/membership.html#role Membership#role}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MembershipConfig(
            username=username,
            role=role,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Membership, self, [scope, id, config])

    @jsii.member(jsii_name="resetRole")
    def reset_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRole", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.MembershipConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "username": "username",
        "role": "role",
    },
)
class MembershipConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        username: builtins.str,
        role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/membership.html#username Membership#username}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/membership.html#role Membership#role}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "username": username,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/membership.html#username Membership#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/membership.html#role Membership#role}.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MembershipConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OrganizationBlock(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.OrganizationBlock",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/organization_block.html github_organization_block}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        username: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/organization_block.html github_organization_block} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_block.html#username OrganizationBlock#username}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OrganizationBlockConfig(
            username=username,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(OrganizationBlock, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.OrganizationBlockConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "username": "username",
    },
)
class OrganizationBlockConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        username: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_block.html#username OrganizationBlock#username}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "username": username,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_block.html#username OrganizationBlock#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationBlockConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OrganizationProject(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.OrganizationProject",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/organization_project.html github_organization_project}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        body: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/organization_project.html github_organization_project} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_project.html#name OrganizationProject#name}.
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_project.html#body OrganizationProject#body}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OrganizationProjectConfig(
            name=name,
            body=body,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(OrganizationProject, self, [scope, id, config])

    @jsii.member(jsii_name="resetBody")
    def reset_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBody", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodyInput")
    def body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @body.setter
    def body(self, value: builtins.str) -> None:
        jsii.set(self, "body", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.OrganizationProjectConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "body": "body",
    },
)
class OrganizationProjectConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        body: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_project.html#name OrganizationProject#name}.
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_project.html#body OrganizationProject#body}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if body is not None:
            self._values["body"] = body

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_project.html#name OrganizationProject#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_project.html#body OrganizationProject#body}.'''
        result = self._values.get("body")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationProjectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OrganizationWebhook(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.OrganizationWebhook",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html github_organization_webhook}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[builtins.str],
        active: typing.Optional[builtins.bool] = None,
        configuration: typing.Optional[typing.Sequence["OrganizationWebhookConfiguration"]] = None,
        name: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html github_organization_webhook} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#events OrganizationWebhook#events}.
        :param active: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#active OrganizationWebhook#active}.
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#configuration OrganizationWebhook#configuration}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#name OrganizationWebhook#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OrganizationWebhookConfig(
            events=events,
            active=active,
            configuration=configuration,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(OrganizationWebhook, self, [scope, id, config])

    @jsii.member(jsii_name="resetActive")
    def reset_active(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActive", []))

    @jsii.member(jsii_name="resetConfiguration")
    def reset_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfiguration", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventsInput")
    def events_input(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activeInput")
    def active_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "activeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInput")
    def configuration_input(
        self,
    ) -> typing.Optional[typing.List["OrganizationWebhookConfiguration"]]:
        return typing.cast(typing.Optional[typing.List["OrganizationWebhookConfiguration"]], jsii.get(self, "configurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="active")
    def active(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "active"))

    @active.setter
    def active(self, value: builtins.bool) -> None:
        jsii.set(self, "active", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> typing.List["OrganizationWebhookConfiguration"]:
        return typing.cast(typing.List["OrganizationWebhookConfiguration"], jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(
        self,
        value: typing.List["OrganizationWebhookConfiguration"],
    ) -> None:
        jsii.set(self, "configuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="events")
    def events(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "events"))

    @events.setter
    def events(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "events", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.OrganizationWebhookConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "events": "events",
        "active": "active",
        "configuration": "configuration",
        "name": "name",
    },
)
class OrganizationWebhookConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        events: typing.Sequence[builtins.str],
        active: typing.Optional[builtins.bool] = None,
        configuration: typing.Optional[typing.Sequence["OrganizationWebhookConfiguration"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#events OrganizationWebhook#events}.
        :param active: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#active OrganizationWebhook#active}.
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#configuration OrganizationWebhook#configuration}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#name OrganizationWebhook#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "events": events,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if active is not None:
            self._values["active"] = active
        if configuration is not None:
            self._values["configuration"] = configuration
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def events(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#events OrganizationWebhook#events}.'''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def active(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#active OrganizationWebhook#active}.'''
        result = self._values.get("active")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def configuration(
        self,
    ) -> typing.Optional[typing.List["OrganizationWebhookConfiguration"]]:
        '''configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#configuration OrganizationWebhook#configuration}
        '''
        result = self._values.get("configuration")
        return typing.cast(typing.Optional[typing.List["OrganizationWebhookConfiguration"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#name OrganizationWebhook#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationWebhookConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.OrganizationWebhookConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "url": "url",
        "content_type": "contentType",
        "insecure_ssl": "insecureSsl",
        "secret": "secret",
    },
)
class OrganizationWebhookConfiguration:
    def __init__(
        self,
        *,
        url: builtins.str,
        content_type: typing.Optional[builtins.str] = None,
        insecure_ssl: typing.Optional[builtins.bool] = None,
        secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#url OrganizationWebhook#url}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#content_type OrganizationWebhook#content_type}.
        :param insecure_ssl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#insecure_ssl OrganizationWebhook#insecure_ssl}.
        :param secret: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#secret OrganizationWebhook#secret}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }
        if content_type is not None:
            self._values["content_type"] = content_type
        if insecure_ssl is not None:
            self._values["insecure_ssl"] = insecure_ssl
        if secret is not None:
            self._values["secret"] = secret

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#url OrganizationWebhook#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#content_type OrganizationWebhook#content_type}.'''
        result = self._values.get("content_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure_ssl(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#insecure_ssl OrganizationWebhook#insecure_ssl}.'''
        result = self._values.get("insecure_ssl")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/organization_webhook.html#secret OrganizationWebhook#secret}.'''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationWebhookConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ProjectCard(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.ProjectCard",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/project_card.html github_project_card}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        column_id: builtins.str,
        note: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/project_card.html github_project_card} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param column_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_card.html#column_id ProjectCard#column_id}.
        :param note: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_card.html#note ProjectCard#note}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ProjectCardConfig(
            column_id=column_id,
            note=note,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ProjectCard, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cardId")
    def card_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cardId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="columnIdInput")
    def column_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "columnIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noteInput")
    def note_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "noteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="columnId")
    def column_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "columnId"))

    @column_id.setter
    def column_id(self, value: builtins.str) -> None:
        jsii.set(self, "columnId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="note")
    def note(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "note"))

    @note.setter
    def note(self, value: builtins.str) -> None:
        jsii.set(self, "note", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.ProjectCardConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "column_id": "columnId",
        "note": "note",
    },
)
class ProjectCardConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        column_id: builtins.str,
        note: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param column_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_card.html#column_id ProjectCard#column_id}.
        :param note: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_card.html#note ProjectCard#note}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "column_id": column_id,
            "note": note,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def column_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_card.html#column_id ProjectCard#column_id}.'''
        result = self._values.get("column_id")
        assert result is not None, "Required property 'column_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def note(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_card.html#note ProjectCard#note}.'''
        result = self._values.get("note")
        assert result is not None, "Required property 'note' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectCardConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ProjectColumn(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.ProjectColumn",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/project_column.html github_project_column}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        project_id: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/project_column.html github_project_column} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_column.html#name ProjectColumn#name}.
        :param project_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_column.html#project_id ProjectColumn#project_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ProjectColumnConfig(
            name=name,
            project_id=project_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ProjectColumn, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="columnId")
    def column_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "columnId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        jsii.set(self, "projectId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.ProjectColumnConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "project_id": "projectId",
    },
)
class ProjectColumnConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        project_id: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_column.html#name ProjectColumn#name}.
        :param project_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_column.html#project_id ProjectColumn#project_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "project_id": project_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_column.html#name ProjectColumn#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/project_column.html#project_id ProjectColumn#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectColumnConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Repository(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.Repository",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/repository.html github_repository}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        allow_merge_commit: typing.Optional[builtins.bool] = None,
        allow_rebase_merge: typing.Optional[builtins.bool] = None,
        allow_squash_merge: typing.Optional[builtins.bool] = None,
        archived: typing.Optional[builtins.bool] = None,
        archive_on_destroy: typing.Optional[builtins.bool] = None,
        auto_init: typing.Optional[builtins.bool] = None,
        default_branch: typing.Optional[builtins.str] = None,
        delete_branch_on_merge: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        gitignore_template: typing.Optional[builtins.str] = None,
        has_downloads: typing.Optional[builtins.bool] = None,
        has_issues: typing.Optional[builtins.bool] = None,
        has_projects: typing.Optional[builtins.bool] = None,
        has_wiki: typing.Optional[builtins.bool] = None,
        homepage_url: typing.Optional[builtins.str] = None,
        is_template: typing.Optional[builtins.bool] = None,
        license_template: typing.Optional[builtins.str] = None,
        pages: typing.Optional[typing.Sequence["RepositoryPages"]] = None,
        private: typing.Optional[builtins.bool] = None,
        template: typing.Optional[typing.Sequence["RepositoryTemplate"]] = None,
        topics: typing.Optional[typing.Sequence[builtins.str]] = None,
        visibility: typing.Optional[builtins.str] = None,
        vulnerability_alerts: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/repository.html github_repository} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#name Repository#name}.
        :param allow_merge_commit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#allow_merge_commit Repository#allow_merge_commit}.
        :param allow_rebase_merge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#allow_rebase_merge Repository#allow_rebase_merge}.
        :param allow_squash_merge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#allow_squash_merge Repository#allow_squash_merge}.
        :param archived: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#archived Repository#archived}.
        :param archive_on_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#archive_on_destroy Repository#archive_on_destroy}.
        :param auto_init: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#auto_init Repository#auto_init}.
        :param default_branch: Can only be set after initial repository creation, and only if the target branch exists. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#default_branch Repository#default_branch}
        :param delete_branch_on_merge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#delete_branch_on_merge Repository#delete_branch_on_merge}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#description Repository#description}.
        :param gitignore_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#gitignore_template Repository#gitignore_template}.
        :param has_downloads: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_downloads Repository#has_downloads}.
        :param has_issues: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_issues Repository#has_issues}.
        :param has_projects: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_projects Repository#has_projects}.
        :param has_wiki: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_wiki Repository#has_wiki}.
        :param homepage_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#homepage_url Repository#homepage_url}.
        :param is_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#is_template Repository#is_template}.
        :param license_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#license_template Repository#license_template}.
        :param pages: pages block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#pages Repository#pages}
        :param private: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#private Repository#private}.
        :param template: template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#template Repository#template}
        :param topics: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#topics Repository#topics}.
        :param visibility: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#visibility Repository#visibility}.
        :param vulnerability_alerts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#vulnerability_alerts Repository#vulnerability_alerts}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RepositoryConfig(
            name=name,
            allow_merge_commit=allow_merge_commit,
            allow_rebase_merge=allow_rebase_merge,
            allow_squash_merge=allow_squash_merge,
            archived=archived,
            archive_on_destroy=archive_on_destroy,
            auto_init=auto_init,
            default_branch=default_branch,
            delete_branch_on_merge=delete_branch_on_merge,
            description=description,
            gitignore_template=gitignore_template,
            has_downloads=has_downloads,
            has_issues=has_issues,
            has_projects=has_projects,
            has_wiki=has_wiki,
            homepage_url=homepage_url,
            is_template=is_template,
            license_template=license_template,
            pages=pages,
            private=private,
            template=template,
            topics=topics,
            visibility=visibility,
            vulnerability_alerts=vulnerability_alerts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Repository, self, [scope, id, config])

    @jsii.member(jsii_name="resetAllowMergeCommit")
    def reset_allow_merge_commit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowMergeCommit", []))

    @jsii.member(jsii_name="resetAllowRebaseMerge")
    def reset_allow_rebase_merge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowRebaseMerge", []))

    @jsii.member(jsii_name="resetAllowSquashMerge")
    def reset_allow_squash_merge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowSquashMerge", []))

    @jsii.member(jsii_name="resetArchived")
    def reset_archived(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArchived", []))

    @jsii.member(jsii_name="resetArchiveOnDestroy")
    def reset_archive_on_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArchiveOnDestroy", []))

    @jsii.member(jsii_name="resetAutoInit")
    def reset_auto_init(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoInit", []))

    @jsii.member(jsii_name="resetDefaultBranch")
    def reset_default_branch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultBranch", []))

    @jsii.member(jsii_name="resetDeleteBranchOnMerge")
    def reset_delete_branch_on_merge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteBranchOnMerge", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetGitignoreTemplate")
    def reset_gitignore_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGitignoreTemplate", []))

    @jsii.member(jsii_name="resetHasDownloads")
    def reset_has_downloads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHasDownloads", []))

    @jsii.member(jsii_name="resetHasIssues")
    def reset_has_issues(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHasIssues", []))

    @jsii.member(jsii_name="resetHasProjects")
    def reset_has_projects(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHasProjects", []))

    @jsii.member(jsii_name="resetHasWiki")
    def reset_has_wiki(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHasWiki", []))

    @jsii.member(jsii_name="resetHomepageUrl")
    def reset_homepage_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomepageUrl", []))

    @jsii.member(jsii_name="resetIsTemplate")
    def reset_is_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsTemplate", []))

    @jsii.member(jsii_name="resetLicenseTemplate")
    def reset_license_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLicenseTemplate", []))

    @jsii.member(jsii_name="resetPages")
    def reset_pages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPages", []))

    @jsii.member(jsii_name="resetPrivate")
    def reset_private(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivate", []))

    @jsii.member(jsii_name="resetTemplate")
    def reset_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplate", []))

    @jsii.member(jsii_name="resetTopics")
    def reset_topics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopics", []))

    @jsii.member(jsii_name="resetVisibility")
    def reset_visibility(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVisibility", []))

    @jsii.member(jsii_name="resetVulnerabilityAlerts")
    def reset_vulnerability_alerts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVulnerabilityAlerts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fullName")
    def full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gitCloneUrl")
    def git_clone_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitCloneUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpCloneUrl")
    def http_clone_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpCloneUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repoId")
    def repo_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "repoId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshCloneUrl")
    def ssh_clone_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshCloneUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svnUrl")
    def svn_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "svnUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMergeCommitInput")
    def allow_merge_commit_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "allowMergeCommitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowRebaseMergeInput")
    def allow_rebase_merge_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "allowRebaseMergeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowSquashMergeInput")
    def allow_squash_merge_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "allowSquashMergeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="archivedInput")
    def archived_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "archivedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="archiveOnDestroyInput")
    def archive_on_destroy_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "archiveOnDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoInitInput")
    def auto_init_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "autoInitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultBranchInput")
    def default_branch_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultBranchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteBranchOnMergeInput")
    def delete_branch_on_merge_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "deleteBranchOnMergeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gitignoreTemplateInput")
    def gitignore_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitignoreTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasDownloadsInput")
    def has_downloads_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "hasDownloadsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasIssuesInput")
    def has_issues_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "hasIssuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasProjectsInput")
    def has_projects_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "hasProjectsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasWikiInput")
    def has_wiki_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "hasWikiInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homepageUrlInput")
    def homepage_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homepageUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isTemplateInput")
    def is_template_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "isTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseTemplateInput")
    def license_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "licenseTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pagesInput")
    def pages_input(self) -> typing.Optional[typing.List["RepositoryPages"]]:
        return typing.cast(typing.Optional[typing.List["RepositoryPages"]], jsii.get(self, "pagesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateInput")
    def private_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "privateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateInput")
    def template_input(self) -> typing.Optional[typing.List["RepositoryTemplate"]]:
        return typing.cast(typing.Optional[typing.List["RepositoryTemplate"]], jsii.get(self, "templateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicsInput")
    def topics_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "topicsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibilityInput")
    def visibility_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "visibilityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vulnerabilityAlertsInput")
    def vulnerability_alerts_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "vulnerabilityAlertsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMergeCommit")
    def allow_merge_commit(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "allowMergeCommit"))

    @allow_merge_commit.setter
    def allow_merge_commit(self, value: builtins.bool) -> None:
        jsii.set(self, "allowMergeCommit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowRebaseMerge")
    def allow_rebase_merge(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "allowRebaseMerge"))

    @allow_rebase_merge.setter
    def allow_rebase_merge(self, value: builtins.bool) -> None:
        jsii.set(self, "allowRebaseMerge", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowSquashMerge")
    def allow_squash_merge(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "allowSquashMerge"))

    @allow_squash_merge.setter
    def allow_squash_merge(self, value: builtins.bool) -> None:
        jsii.set(self, "allowSquashMerge", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="archived")
    def archived(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "archived"))

    @archived.setter
    def archived(self, value: builtins.bool) -> None:
        jsii.set(self, "archived", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="archiveOnDestroy")
    def archive_on_destroy(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "archiveOnDestroy"))

    @archive_on_destroy.setter
    def archive_on_destroy(self, value: builtins.bool) -> None:
        jsii.set(self, "archiveOnDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoInit")
    def auto_init(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "autoInit"))

    @auto_init.setter
    def auto_init(self, value: builtins.bool) -> None:
        jsii.set(self, "autoInit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultBranch")
    def default_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultBranch"))

    @default_branch.setter
    def default_branch(self, value: builtins.str) -> None:
        jsii.set(self, "defaultBranch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteBranchOnMerge")
    def delete_branch_on_merge(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "deleteBranchOnMerge"))

    @delete_branch_on_merge.setter
    def delete_branch_on_merge(self, value: builtins.bool) -> None:
        jsii.set(self, "deleteBranchOnMerge", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gitignoreTemplate")
    def gitignore_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitignoreTemplate"))

    @gitignore_template.setter
    def gitignore_template(self, value: builtins.str) -> None:
        jsii.set(self, "gitignoreTemplate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasDownloads")
    def has_downloads(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasDownloads"))

    @has_downloads.setter
    def has_downloads(self, value: builtins.bool) -> None:
        jsii.set(self, "hasDownloads", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasIssues")
    def has_issues(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasIssues"))

    @has_issues.setter
    def has_issues(self, value: builtins.bool) -> None:
        jsii.set(self, "hasIssues", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasProjects")
    def has_projects(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasProjects"))

    @has_projects.setter
    def has_projects(self, value: builtins.bool) -> None:
        jsii.set(self, "hasProjects", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasWiki")
    def has_wiki(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "hasWiki"))

    @has_wiki.setter
    def has_wiki(self, value: builtins.bool) -> None:
        jsii.set(self, "hasWiki", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homepageUrl")
    def homepage_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homepageUrl"))

    @homepage_url.setter
    def homepage_url(self, value: builtins.str) -> None:
        jsii.set(self, "homepageUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isTemplate")
    def is_template(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "isTemplate"))

    @is_template.setter
    def is_template(self, value: builtins.bool) -> None:
        jsii.set(self, "isTemplate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseTemplate")
    def license_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseTemplate"))

    @license_template.setter
    def license_template(self, value: builtins.str) -> None:
        jsii.set(self, "licenseTemplate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pages")
    def pages(self) -> typing.List["RepositoryPages"]:
        return typing.cast(typing.List["RepositoryPages"], jsii.get(self, "pages"))

    @pages.setter
    def pages(self, value: typing.List["RepositoryPages"]) -> None:
        jsii.set(self, "pages", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="private")
    def private(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "private"))

    @private.setter
    def private(self, value: builtins.bool) -> None:
        jsii.set(self, "private", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="template")
    def template(self) -> typing.List["RepositoryTemplate"]:
        return typing.cast(typing.List["RepositoryTemplate"], jsii.get(self, "template"))

    @template.setter
    def template(self, value: typing.List["RepositoryTemplate"]) -> None:
        jsii.set(self, "template", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topics")
    def topics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "topics"))

    @topics.setter
    def topics(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "topics", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @visibility.setter
    def visibility(self, value: builtins.str) -> None:
        jsii.set(self, "visibility", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vulnerabilityAlerts")
    def vulnerability_alerts(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "vulnerabilityAlerts"))

    @vulnerability_alerts.setter
    def vulnerability_alerts(self, value: builtins.bool) -> None:
        jsii.set(self, "vulnerabilityAlerts", value)


class RepositoryCollaborator(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.RepositoryCollaborator",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html github_repository_collaborator}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        repository: builtins.str,
        username: builtins.str,
        permission: typing.Optional[builtins.str] = None,
        permission_diff_suppression: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html github_repository_collaborator} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#repository RepositoryCollaborator#repository}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#username RepositoryCollaborator#username}.
        :param permission: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#permission RepositoryCollaborator#permission}.
        :param permission_diff_suppression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#permission_diff_suppression RepositoryCollaborator#permission_diff_suppression}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RepositoryCollaboratorConfig(
            repository=repository,
            username=username,
            permission=permission,
            permission_diff_suppression=permission_diff_suppression,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RepositoryCollaborator, self, [scope, id, config])

    @jsii.member(jsii_name="resetPermission")
    def reset_permission(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermission", []))

    @jsii.member(jsii_name="resetPermissionDiffSuppression")
    def reset_permission_diff_suppression(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermissionDiffSuppression", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invitationId")
    def invitation_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invitationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionDiffSuppressionInput")
    def permission_diff_suppression_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "permissionDiffSuppressionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        jsii.set(self, "permission", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionDiffSuppression")
    def permission_diff_suppression(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "permissionDiffSuppression"))

    @permission_diff_suppression.setter
    def permission_diff_suppression(self, value: builtins.bool) -> None:
        jsii.set(self, "permissionDiffSuppression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryCollaboratorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "repository": "repository",
        "username": "username",
        "permission": "permission",
        "permission_diff_suppression": "permissionDiffSuppression",
    },
)
class RepositoryCollaboratorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        repository: builtins.str,
        username: builtins.str,
        permission: typing.Optional[builtins.str] = None,
        permission_diff_suppression: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#repository RepositoryCollaborator#repository}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#username RepositoryCollaborator#username}.
        :param permission: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#permission RepositoryCollaborator#permission}.
        :param permission_diff_suppression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#permission_diff_suppression RepositoryCollaborator#permission_diff_suppression}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "repository": repository,
            "username": username,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if permission is not None:
            self._values["permission"] = permission
        if permission_diff_suppression is not None:
            self._values["permission_diff_suppression"] = permission_diff_suppression

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#repository RepositoryCollaborator#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#username RepositoryCollaborator#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#permission RepositoryCollaborator#permission}.'''
        result = self._values.get("permission")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permission_diff_suppression(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_collaborator.html#permission_diff_suppression RepositoryCollaborator#permission_diff_suppression}.'''
        result = self._values.get("permission_diff_suppression")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryCollaboratorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "allow_merge_commit": "allowMergeCommit",
        "allow_rebase_merge": "allowRebaseMerge",
        "allow_squash_merge": "allowSquashMerge",
        "archived": "archived",
        "archive_on_destroy": "archiveOnDestroy",
        "auto_init": "autoInit",
        "default_branch": "defaultBranch",
        "delete_branch_on_merge": "deleteBranchOnMerge",
        "description": "description",
        "gitignore_template": "gitignoreTemplate",
        "has_downloads": "hasDownloads",
        "has_issues": "hasIssues",
        "has_projects": "hasProjects",
        "has_wiki": "hasWiki",
        "homepage_url": "homepageUrl",
        "is_template": "isTemplate",
        "license_template": "licenseTemplate",
        "pages": "pages",
        "private": "private",
        "template": "template",
        "topics": "topics",
        "visibility": "visibility",
        "vulnerability_alerts": "vulnerabilityAlerts",
    },
)
class RepositoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        allow_merge_commit: typing.Optional[builtins.bool] = None,
        allow_rebase_merge: typing.Optional[builtins.bool] = None,
        allow_squash_merge: typing.Optional[builtins.bool] = None,
        archived: typing.Optional[builtins.bool] = None,
        archive_on_destroy: typing.Optional[builtins.bool] = None,
        auto_init: typing.Optional[builtins.bool] = None,
        default_branch: typing.Optional[builtins.str] = None,
        delete_branch_on_merge: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        gitignore_template: typing.Optional[builtins.str] = None,
        has_downloads: typing.Optional[builtins.bool] = None,
        has_issues: typing.Optional[builtins.bool] = None,
        has_projects: typing.Optional[builtins.bool] = None,
        has_wiki: typing.Optional[builtins.bool] = None,
        homepage_url: typing.Optional[builtins.str] = None,
        is_template: typing.Optional[builtins.bool] = None,
        license_template: typing.Optional[builtins.str] = None,
        pages: typing.Optional[typing.Sequence["RepositoryPages"]] = None,
        private: typing.Optional[builtins.bool] = None,
        template: typing.Optional[typing.Sequence["RepositoryTemplate"]] = None,
        topics: typing.Optional[typing.Sequence[builtins.str]] = None,
        visibility: typing.Optional[builtins.str] = None,
        vulnerability_alerts: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#name Repository#name}.
        :param allow_merge_commit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#allow_merge_commit Repository#allow_merge_commit}.
        :param allow_rebase_merge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#allow_rebase_merge Repository#allow_rebase_merge}.
        :param allow_squash_merge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#allow_squash_merge Repository#allow_squash_merge}.
        :param archived: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#archived Repository#archived}.
        :param archive_on_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#archive_on_destroy Repository#archive_on_destroy}.
        :param auto_init: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#auto_init Repository#auto_init}.
        :param default_branch: Can only be set after initial repository creation, and only if the target branch exists. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#default_branch Repository#default_branch}
        :param delete_branch_on_merge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#delete_branch_on_merge Repository#delete_branch_on_merge}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#description Repository#description}.
        :param gitignore_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#gitignore_template Repository#gitignore_template}.
        :param has_downloads: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_downloads Repository#has_downloads}.
        :param has_issues: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_issues Repository#has_issues}.
        :param has_projects: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_projects Repository#has_projects}.
        :param has_wiki: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_wiki Repository#has_wiki}.
        :param homepage_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#homepage_url Repository#homepage_url}.
        :param is_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#is_template Repository#is_template}.
        :param license_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#license_template Repository#license_template}.
        :param pages: pages block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#pages Repository#pages}
        :param private: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#private Repository#private}.
        :param template: template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#template Repository#template}
        :param topics: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#topics Repository#topics}.
        :param visibility: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#visibility Repository#visibility}.
        :param vulnerability_alerts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#vulnerability_alerts Repository#vulnerability_alerts}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allow_merge_commit is not None:
            self._values["allow_merge_commit"] = allow_merge_commit
        if allow_rebase_merge is not None:
            self._values["allow_rebase_merge"] = allow_rebase_merge
        if allow_squash_merge is not None:
            self._values["allow_squash_merge"] = allow_squash_merge
        if archived is not None:
            self._values["archived"] = archived
        if archive_on_destroy is not None:
            self._values["archive_on_destroy"] = archive_on_destroy
        if auto_init is not None:
            self._values["auto_init"] = auto_init
        if default_branch is not None:
            self._values["default_branch"] = default_branch
        if delete_branch_on_merge is not None:
            self._values["delete_branch_on_merge"] = delete_branch_on_merge
        if description is not None:
            self._values["description"] = description
        if gitignore_template is not None:
            self._values["gitignore_template"] = gitignore_template
        if has_downloads is not None:
            self._values["has_downloads"] = has_downloads
        if has_issues is not None:
            self._values["has_issues"] = has_issues
        if has_projects is not None:
            self._values["has_projects"] = has_projects
        if has_wiki is not None:
            self._values["has_wiki"] = has_wiki
        if homepage_url is not None:
            self._values["homepage_url"] = homepage_url
        if is_template is not None:
            self._values["is_template"] = is_template
        if license_template is not None:
            self._values["license_template"] = license_template
        if pages is not None:
            self._values["pages"] = pages
        if private is not None:
            self._values["private"] = private
        if template is not None:
            self._values["template"] = template
        if topics is not None:
            self._values["topics"] = topics
        if visibility is not None:
            self._values["visibility"] = visibility
        if vulnerability_alerts is not None:
            self._values["vulnerability_alerts"] = vulnerability_alerts

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#name Repository#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_merge_commit(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#allow_merge_commit Repository#allow_merge_commit}.'''
        result = self._values.get("allow_merge_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_rebase_merge(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#allow_rebase_merge Repository#allow_rebase_merge}.'''
        result = self._values.get("allow_rebase_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_squash_merge(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#allow_squash_merge Repository#allow_squash_merge}.'''
        result = self._values.get("allow_squash_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def archived(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#archived Repository#archived}.'''
        result = self._values.get("archived")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def archive_on_destroy(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#archive_on_destroy Repository#archive_on_destroy}.'''
        result = self._values.get("archive_on_destroy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_init(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#auto_init Repository#auto_init}.'''
        result = self._values.get("auto_init")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def default_branch(self) -> typing.Optional[builtins.str]:
        '''Can only be set after initial repository creation, and only if the target branch exists.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#default_branch Repository#default_branch}
        '''
        result = self._values.get("default_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_branch_on_merge(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#delete_branch_on_merge Repository#delete_branch_on_merge}.'''
        result = self._values.get("delete_branch_on_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#description Repository#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitignore_template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#gitignore_template Repository#gitignore_template}.'''
        result = self._values.get("gitignore_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def has_downloads(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_downloads Repository#has_downloads}.'''
        result = self._values.get("has_downloads")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def has_issues(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_issues Repository#has_issues}.'''
        result = self._values.get("has_issues")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def has_projects(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_projects Repository#has_projects}.'''
        result = self._values.get("has_projects")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def has_wiki(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#has_wiki Repository#has_wiki}.'''
        result = self._values.get("has_wiki")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def homepage_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#homepage_url Repository#homepage_url}.'''
        result = self._values.get("homepage_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_template(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#is_template Repository#is_template}.'''
        result = self._values.get("is_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def license_template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#license_template Repository#license_template}.'''
        result = self._values.get("license_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pages(self) -> typing.Optional[typing.List["RepositoryPages"]]:
        '''pages block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#pages Repository#pages}
        '''
        result = self._values.get("pages")
        return typing.cast(typing.Optional[typing.List["RepositoryPages"]], result)

    @builtins.property
    def private(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#private Repository#private}.'''
        result = self._values.get("private")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def template(self) -> typing.Optional[typing.List["RepositoryTemplate"]]:
        '''template block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#template Repository#template}
        '''
        result = self._values.get("template")
        return typing.cast(typing.Optional[typing.List["RepositoryTemplate"]], result)

    @builtins.property
    def topics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#topics Repository#topics}.'''
        result = self._values.get("topics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def visibility(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#visibility Repository#visibility}.'''
        result = self._values.get("visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vulnerability_alerts(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#vulnerability_alerts Repository#vulnerability_alerts}.'''
        result = self._values.get("vulnerability_alerts")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RepositoryDeployKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.RepositoryDeployKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html github_repository_deploy_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        key: builtins.str,
        repository: builtins.str,
        title: builtins.str,
        read_only: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html github_repository_deploy_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#key RepositoryDeployKey#key}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#repository RepositoryDeployKey#repository}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#title RepositoryDeployKey#title}.
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#read_only RepositoryDeployKey#read_only}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RepositoryDeployKeyConfig(
            key=key,
            repository=repository,
            title=title,
            read_only=read_only,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RepositoryDeployKey, self, [scope, id, config])

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "readOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(self, value: builtins.bool) -> None:
        jsii.set(self, "readOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryDeployKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "key": "key",
        "repository": "repository",
        "title": "title",
        "read_only": "readOnly",
    },
)
class RepositoryDeployKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        key: builtins.str,
        repository: builtins.str,
        title: builtins.str,
        read_only: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#key RepositoryDeployKey#key}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#repository RepositoryDeployKey#repository}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#title RepositoryDeployKey#title}.
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#read_only RepositoryDeployKey#read_only}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "repository": repository,
            "title": title,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if read_only is not None:
            self._values["read_only"] = read_only

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#key RepositoryDeployKey#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#repository RepositoryDeployKey#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#title RepositoryDeployKey#title}.'''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_deploy_key.html#read_only RepositoryDeployKey#read_only}.'''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryDeployKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RepositoryEnvironment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.RepositoryEnvironment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html github_repository_environment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        environment: builtins.str,
        repository: builtins.str,
        deployment_branch_policy: typing.Optional[typing.Sequence["RepositoryEnvironmentDeploymentBranchPolicy"]] = None,
        reviewers: typing.Optional[typing.Sequence["RepositoryEnvironmentReviewers"]] = None,
        wait_timer: typing.Optional[jsii.Number] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html github_repository_environment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param environment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#environment RepositoryEnvironment#environment}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#repository RepositoryEnvironment#repository}.
        :param deployment_branch_policy: deployment_branch_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#deployment_branch_policy RepositoryEnvironment#deployment_branch_policy}
        :param reviewers: reviewers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#reviewers RepositoryEnvironment#reviewers}
        :param wait_timer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#wait_timer RepositoryEnvironment#wait_timer}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RepositoryEnvironmentConfig(
            environment=environment,
            repository=repository,
            deployment_branch_policy=deployment_branch_policy,
            reviewers=reviewers,
            wait_timer=wait_timer,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RepositoryEnvironment, self, [scope, id, config])

    @jsii.member(jsii_name="resetDeploymentBranchPolicy")
    def reset_deployment_branch_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentBranchPolicy", []))

    @jsii.member(jsii_name="resetReviewers")
    def reset_reviewers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReviewers", []))

    @jsii.member(jsii_name="resetWaitTimer")
    def reset_wait_timer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitTimer", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environmentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentBranchPolicyInput")
    def deployment_branch_policy_input(
        self,
    ) -> typing.Optional[typing.List["RepositoryEnvironmentDeploymentBranchPolicy"]]:
        return typing.cast(typing.Optional[typing.List["RepositoryEnvironmentDeploymentBranchPolicy"]], jsii.get(self, "deploymentBranchPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reviewersInput")
    def reviewers_input(
        self,
    ) -> typing.Optional[typing.List["RepositoryEnvironmentReviewers"]]:
        return typing.cast(typing.Optional[typing.List["RepositoryEnvironmentReviewers"]], jsii.get(self, "reviewersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitTimerInput")
    def wait_timer_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "waitTimerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentBranchPolicy")
    def deployment_branch_policy(
        self,
    ) -> typing.List["RepositoryEnvironmentDeploymentBranchPolicy"]:
        return typing.cast(typing.List["RepositoryEnvironmentDeploymentBranchPolicy"], jsii.get(self, "deploymentBranchPolicy"))

    @deployment_branch_policy.setter
    def deployment_branch_policy(
        self,
        value: typing.List["RepositoryEnvironmentDeploymentBranchPolicy"],
    ) -> None:
        jsii.set(self, "deploymentBranchPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: builtins.str) -> None:
        jsii.set(self, "environment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reviewers")
    def reviewers(self) -> typing.List["RepositoryEnvironmentReviewers"]:
        return typing.cast(typing.List["RepositoryEnvironmentReviewers"], jsii.get(self, "reviewers"))

    @reviewers.setter
    def reviewers(self, value: typing.List["RepositoryEnvironmentReviewers"]) -> None:
        jsii.set(self, "reviewers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitTimer")
    def wait_timer(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "waitTimer"))

    @wait_timer.setter
    def wait_timer(self, value: jsii.Number) -> None:
        jsii.set(self, "waitTimer", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryEnvironmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "environment": "environment",
        "repository": "repository",
        "deployment_branch_policy": "deploymentBranchPolicy",
        "reviewers": "reviewers",
        "wait_timer": "waitTimer",
    },
)
class RepositoryEnvironmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        environment: builtins.str,
        repository: builtins.str,
        deployment_branch_policy: typing.Optional[typing.Sequence["RepositoryEnvironmentDeploymentBranchPolicy"]] = None,
        reviewers: typing.Optional[typing.Sequence["RepositoryEnvironmentReviewers"]] = None,
        wait_timer: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param environment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#environment RepositoryEnvironment#environment}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#repository RepositoryEnvironment#repository}.
        :param deployment_branch_policy: deployment_branch_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#deployment_branch_policy RepositoryEnvironment#deployment_branch_policy}
        :param reviewers: reviewers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#reviewers RepositoryEnvironment#reviewers}
        :param wait_timer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#wait_timer RepositoryEnvironment#wait_timer}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "environment": environment,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if deployment_branch_policy is not None:
            self._values["deployment_branch_policy"] = deployment_branch_policy
        if reviewers is not None:
            self._values["reviewers"] = reviewers
        if wait_timer is not None:
            self._values["wait_timer"] = wait_timer

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def environment(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#environment RepositoryEnvironment#environment}.'''
        result = self._values.get("environment")
        assert result is not None, "Required property 'environment' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#repository RepositoryEnvironment#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deployment_branch_policy(
        self,
    ) -> typing.Optional[typing.List["RepositoryEnvironmentDeploymentBranchPolicy"]]:
        '''deployment_branch_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#deployment_branch_policy RepositoryEnvironment#deployment_branch_policy}
        '''
        result = self._values.get("deployment_branch_policy")
        return typing.cast(typing.Optional[typing.List["RepositoryEnvironmentDeploymentBranchPolicy"]], result)

    @builtins.property
    def reviewers(
        self,
    ) -> typing.Optional[typing.List["RepositoryEnvironmentReviewers"]]:
        '''reviewers block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#reviewers RepositoryEnvironment#reviewers}
        '''
        result = self._values.get("reviewers")
        return typing.cast(typing.Optional[typing.List["RepositoryEnvironmentReviewers"]], result)

    @builtins.property
    def wait_timer(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#wait_timer RepositoryEnvironment#wait_timer}.'''
        result = self._values.get("wait_timer")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryEnvironmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryEnvironmentDeploymentBranchPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "custom_branch_policies": "customBranchPolicies",
        "protected_branches": "protectedBranches",
    },
)
class RepositoryEnvironmentDeploymentBranchPolicy:
    def __init__(
        self,
        *,
        custom_branch_policies: builtins.bool,
        protected_branches: builtins.bool,
    ) -> None:
        '''
        :param custom_branch_policies: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#custom_branch_policies RepositoryEnvironment#custom_branch_policies}.
        :param protected_branches: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#protected_branches RepositoryEnvironment#protected_branches}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "custom_branch_policies": custom_branch_policies,
            "protected_branches": protected_branches,
        }

    @builtins.property
    def custom_branch_policies(self) -> builtins.bool:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#custom_branch_policies RepositoryEnvironment#custom_branch_policies}.'''
        result = self._values.get("custom_branch_policies")
        assert result is not None, "Required property 'custom_branch_policies' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def protected_branches(self) -> builtins.bool:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#protected_branches RepositoryEnvironment#protected_branches}.'''
        result = self._values.get("protected_branches")
        assert result is not None, "Required property 'protected_branches' is missing"
        return typing.cast(builtins.bool, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryEnvironmentDeploymentBranchPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryEnvironmentReviewers",
    jsii_struct_bases=[],
    name_mapping={"teams": "teams", "users": "users"},
)
class RepositoryEnvironmentReviewers:
    def __init__(
        self,
        *,
        teams: typing.Optional[typing.Sequence[jsii.Number]] = None,
        users: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param teams: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#teams RepositoryEnvironment#teams}.
        :param users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#users RepositoryEnvironment#users}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if teams is not None:
            self._values["teams"] = teams
        if users is not None:
            self._values["users"] = users

    @builtins.property
    def teams(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#teams RepositoryEnvironment#teams}.'''
        result = self._values.get("teams")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def users(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_environment.html#users RepositoryEnvironment#users}.'''
        result = self._values.get("users")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryEnvironmentReviewers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RepositoryFile(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.RepositoryFile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/repository_file.html github_repository_file}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        content: builtins.str,
        file: builtins.str,
        repository: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        commit_author: typing.Optional[builtins.str] = None,
        commit_email: typing.Optional[builtins.str] = None,
        commit_message: typing.Optional[builtins.str] = None,
        overwrite_on_create: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/repository_file.html github_repository_file} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param content: The file's content. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#content RepositoryFile#content}
        :param file: The file path to manage. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#file RepositoryFile#file}
        :param repository: The repository name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#repository RepositoryFile#repository}
        :param branch: The branch name, defaults to "main". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#branch RepositoryFile#branch}
        :param commit_author: The commit author name, defaults to the authenticated user's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#commit_author RepositoryFile#commit_author}
        :param commit_email: The commit author email address, defaults to the authenticated user's email address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#commit_email RepositoryFile#commit_email}
        :param commit_message: The commit message when creating or updating the file. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#commit_message RepositoryFile#commit_message}
        :param overwrite_on_create: Enable overwriting existing files, defaults to "false". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#overwrite_on_create RepositoryFile#overwrite_on_create}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RepositoryFileConfig(
            content=content,
            file=file,
            repository=repository,
            branch=branch,
            commit_author=commit_author,
            commit_email=commit_email,
            commit_message=commit_message,
            overwrite_on_create=overwrite_on_create,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RepositoryFile, self, [scope, id, config])

    @jsii.member(jsii_name="resetBranch")
    def reset_branch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBranch", []))

    @jsii.member(jsii_name="resetCommitAuthor")
    def reset_commit_author(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommitAuthor", []))

    @jsii.member(jsii_name="resetCommitEmail")
    def reset_commit_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommitEmail", []))

    @jsii.member(jsii_name="resetCommitMessage")
    def reset_commit_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommitMessage", []))

    @jsii.member(jsii_name="resetOverwriteOnCreate")
    def reset_overwrite_on_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverwriteOnCreate", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commitSha")
    def commit_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commitSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentInput")
    def content_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileInput")
    def file_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sha")
    def sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchInput")
    def branch_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "branchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commitAuthorInput")
    def commit_author_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commitAuthorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commitEmailInput")
    def commit_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commitEmailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commitMessageInput")
    def commit_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commitMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overwriteOnCreateInput")
    def overwrite_on_create_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "overwriteOnCreateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branch")
    def branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branch"))

    @branch.setter
    def branch(self, value: builtins.str) -> None:
        jsii.set(self, "branch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commitAuthor")
    def commit_author(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commitAuthor"))

    @commit_author.setter
    def commit_author(self, value: builtins.str) -> None:
        jsii.set(self, "commitAuthor", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commitEmail")
    def commit_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commitEmail"))

    @commit_email.setter
    def commit_email(self, value: builtins.str) -> None:
        jsii.set(self, "commitEmail", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commitMessage")
    def commit_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commitMessage"))

    @commit_message.setter
    def commit_message(self, value: builtins.str) -> None:
        jsii.set(self, "commitMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @content.setter
    def content(self, value: builtins.str) -> None:
        jsii.set(self, "content", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="file")
    def file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "file"))

    @file.setter
    def file(self, value: builtins.str) -> None:
        jsii.set(self, "file", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overwriteOnCreate")
    def overwrite_on_create(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "overwriteOnCreate"))

    @overwrite_on_create.setter
    def overwrite_on_create(self, value: builtins.bool) -> None:
        jsii.set(self, "overwriteOnCreate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryFileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "content": "content",
        "file": "file",
        "repository": "repository",
        "branch": "branch",
        "commit_author": "commitAuthor",
        "commit_email": "commitEmail",
        "commit_message": "commitMessage",
        "overwrite_on_create": "overwriteOnCreate",
    },
)
class RepositoryFileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        content: builtins.str,
        file: builtins.str,
        repository: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        commit_author: typing.Optional[builtins.str] = None,
        commit_email: typing.Optional[builtins.str] = None,
        commit_message: typing.Optional[builtins.str] = None,
        overwrite_on_create: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param content: The file's content. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#content RepositoryFile#content}
        :param file: The file path to manage. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#file RepositoryFile#file}
        :param repository: The repository name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#repository RepositoryFile#repository}
        :param branch: The branch name, defaults to "main". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#branch RepositoryFile#branch}
        :param commit_author: The commit author name, defaults to the authenticated user's name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#commit_author RepositoryFile#commit_author}
        :param commit_email: The commit author email address, defaults to the authenticated user's email address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#commit_email RepositoryFile#commit_email}
        :param commit_message: The commit message when creating or updating the file. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#commit_message RepositoryFile#commit_message}
        :param overwrite_on_create: Enable overwriting existing files, defaults to "false". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#overwrite_on_create RepositoryFile#overwrite_on_create}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "file": file,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if branch is not None:
            self._values["branch"] = branch
        if commit_author is not None:
            self._values["commit_author"] = commit_author
        if commit_email is not None:
            self._values["commit_email"] = commit_email
        if commit_message is not None:
            self._values["commit_message"] = commit_message
        if overwrite_on_create is not None:
            self._values["overwrite_on_create"] = overwrite_on_create

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def content(self) -> builtins.str:
        '''The file's content.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#content RepositoryFile#content}
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file(self) -> builtins.str:
        '''The file path to manage.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#file RepositoryFile#file}
        '''
        result = self._values.get("file")
        assert result is not None, "Required property 'file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''The repository name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#repository RepositoryFile#repository}
        '''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''The branch name, defaults to "main".

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#branch RepositoryFile#branch}
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit_author(self) -> typing.Optional[builtins.str]:
        '''The commit author name, defaults to the authenticated user's name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#commit_author RepositoryFile#commit_author}
        '''
        result = self._values.get("commit_author")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit_email(self) -> typing.Optional[builtins.str]:
        '''The commit author email address, defaults to the authenticated user's email address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#commit_email RepositoryFile#commit_email}
        '''
        result = self._values.get("commit_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit_message(self) -> typing.Optional[builtins.str]:
        '''The commit message when creating or updating the file.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#commit_message RepositoryFile#commit_message}
        '''
        result = self._values.get("commit_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def overwrite_on_create(self) -> typing.Optional[builtins.bool]:
        '''Enable overwriting existing files, defaults to "false".

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_file.html#overwrite_on_create RepositoryFile#overwrite_on_create}
        '''
        result = self._values.get("overwrite_on_create")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryFileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RepositoryMilestone(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.RepositoryMilestone",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html github_repository_milestone}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        owner: builtins.str,
        repository: builtins.str,
        title: builtins.str,
        description: typing.Optional[builtins.str] = None,
        due_date: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html github_repository_milestone} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#owner RepositoryMilestone#owner}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#repository RepositoryMilestone#repository}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#title RepositoryMilestone#title}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#description RepositoryMilestone#description}.
        :param due_date: in yyyy-mm-dd format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#due_date RepositoryMilestone#due_date}
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#state RepositoryMilestone#state}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RepositoryMilestoneConfig(
            owner=owner,
            repository=repository,
            title=title,
            description=description,
            due_date=due_date,
            state=state,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RepositoryMilestone, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDueDate")
    def reset_due_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDueDate", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="number")
    def number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "number"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dueDateInput")
    def due_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dueDateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dueDate")
    def due_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dueDate"))

    @due_date.setter
    def due_date(self, value: builtins.str) -> None:
        jsii.set(self, "dueDate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        jsii.set(self, "state", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryMilestoneConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "owner": "owner",
        "repository": "repository",
        "title": "title",
        "description": "description",
        "due_date": "dueDate",
        "state": "state",
    },
)
class RepositoryMilestoneConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        owner: builtins.str,
        repository: builtins.str,
        title: builtins.str,
        description: typing.Optional[builtins.str] = None,
        due_date: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#owner RepositoryMilestone#owner}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#repository RepositoryMilestone#repository}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#title RepositoryMilestone#title}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#description RepositoryMilestone#description}.
        :param due_date: in yyyy-mm-dd format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#due_date RepositoryMilestone#due_date}
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#state RepositoryMilestone#state}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "owner": owner,
            "repository": repository,
            "title": title,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if due_date is not None:
            self._values["due_date"] = due_date
        if state is not None:
            self._values["state"] = state

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#owner RepositoryMilestone#owner}.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#repository RepositoryMilestone#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#title RepositoryMilestone#title}.'''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#description RepositoryMilestone#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def due_date(self) -> typing.Optional[builtins.str]:
        '''in yyyy-mm-dd format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#due_date RepositoryMilestone#due_date}
        '''
        result = self._values.get("due_date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_milestone.html#state RepositoryMilestone#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryMilestoneConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryPages",
    jsii_struct_bases=[],
    name_mapping={"source": "source", "cname": "cname"},
)
class RepositoryPages:
    def __init__(
        self,
        *,
        source: typing.Sequence["RepositoryPagesSource"],
        cname: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#source Repository#source}
        :param cname: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#cname Repository#cname}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "source": source,
        }
        if cname is not None:
            self._values["cname"] = cname

    @builtins.property
    def source(self) -> typing.List["RepositoryPagesSource"]:
        '''source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#source Repository#source}
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(typing.List["RepositoryPagesSource"], result)

    @builtins.property
    def cname(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#cname Repository#cname}.'''
        result = self._values.get("cname")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryPages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryPagesSource",
    jsii_struct_bases=[],
    name_mapping={"branch": "branch", "path": "path"},
)
class RepositoryPagesSource:
    def __init__(
        self,
        *,
        branch: builtins.str,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#branch Repository#branch}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#path Repository#path}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "branch": branch,
        }
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def branch(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#branch Repository#branch}.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#path Repository#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryPagesSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RepositoryProject(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.RepositoryProject",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/repository_project.html github_repository_project}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        repository: builtins.str,
        body: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/repository_project.html github_repository_project} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_project.html#name RepositoryProject#name}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_project.html#repository RepositoryProject#repository}.
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_project.html#body RepositoryProject#body}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RepositoryProjectConfig(
            name=name,
            repository=repository,
            body=body,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RepositoryProject, self, [scope, id, config])

    @jsii.member(jsii_name="resetBody")
    def reset_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBody", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodyInput")
    def body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @body.setter
    def body(self, value: builtins.str) -> None:
        jsii.set(self, "body", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryProjectConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "repository": "repository",
        "body": "body",
    },
)
class RepositoryProjectConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        repository: builtins.str,
        body: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_project.html#name RepositoryProject#name}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_project.html#repository RepositoryProject#repository}.
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_project.html#body RepositoryProject#body}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if body is not None:
            self._values["body"] = body

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_project.html#name RepositoryProject#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_project.html#repository RepositoryProject#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_project.html#body RepositoryProject#body}.'''
        result = self._values.get("body")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryProjectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RepositoryPullRequest(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.RepositoryPullRequest",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html github_repository_pull_request}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        base_ref: builtins.str,
        base_repository: builtins.str,
        head_ref: builtins.str,
        title: builtins.str,
        body: typing.Optional[builtins.str] = None,
        maintainer_can_modify: typing.Optional[builtins.bool] = None,
        owner: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html github_repository_pull_request} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param base_ref: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#base_ref RepositoryPullRequest#base_ref}.
        :param base_repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#base_repository RepositoryPullRequest#base_repository}.
        :param head_ref: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#head_ref RepositoryPullRequest#head_ref}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#title RepositoryPullRequest#title}.
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#body RepositoryPullRequest#body}.
        :param maintainer_can_modify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#maintainer_can_modify RepositoryPullRequest#maintainer_can_modify}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#owner RepositoryPullRequest#owner}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RepositoryPullRequestConfig(
            base_ref=base_ref,
            base_repository=base_repository,
            head_ref=head_ref,
            title=title,
            body=body,
            maintainer_can_modify=maintainer_can_modify,
            owner=owner,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RepositoryPullRequest, self, [scope, id, config])

    @jsii.member(jsii_name="resetBody")
    def reset_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBody", []))

    @jsii.member(jsii_name="resetMaintainerCanModify")
    def reset_maintainer_can_modify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintainerCanModify", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRefInput")
    def base_ref_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRefInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRepositoryInput")
    def base_repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRepositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseSha")
    def base_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="draft")
    def draft(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "draft"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headRefInput")
    def head_ref_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headRefInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headSha")
    def head_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "labels"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="number")
    def number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "number"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openedAt")
    def opened_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "openedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openedBy")
    def opened_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodyInput")
    def body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintainerCanModifyInput")
    def maintainer_can_modify_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "maintainerCanModifyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRef")
    def base_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRef"))

    @base_ref.setter
    def base_ref(self, value: builtins.str) -> None:
        jsii.set(self, "baseRef", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRepository")
    def base_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRepository"))

    @base_repository.setter
    def base_repository(self, value: builtins.str) -> None:
        jsii.set(self, "baseRepository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @body.setter
    def body(self, value: builtins.str) -> None:
        jsii.set(self, "body", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headRef")
    def head_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headRef"))

    @head_ref.setter
    def head_ref(self, value: builtins.str) -> None:
        jsii.set(self, "headRef", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintainerCanModify")
    def maintainer_can_modify(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "maintainerCanModify"))

    @maintainer_can_modify.setter
    def maintainer_can_modify(self, value: builtins.bool) -> None:
        jsii.set(self, "maintainerCanModify", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryPullRequestConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "base_ref": "baseRef",
        "base_repository": "baseRepository",
        "head_ref": "headRef",
        "title": "title",
        "body": "body",
        "maintainer_can_modify": "maintainerCanModify",
        "owner": "owner",
    },
)
class RepositoryPullRequestConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        base_ref: builtins.str,
        base_repository: builtins.str,
        head_ref: builtins.str,
        title: builtins.str,
        body: typing.Optional[builtins.str] = None,
        maintainer_can_modify: typing.Optional[builtins.bool] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param base_ref: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#base_ref RepositoryPullRequest#base_ref}.
        :param base_repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#base_repository RepositoryPullRequest#base_repository}.
        :param head_ref: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#head_ref RepositoryPullRequest#head_ref}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#title RepositoryPullRequest#title}.
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#body RepositoryPullRequest#body}.
        :param maintainer_can_modify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#maintainer_can_modify RepositoryPullRequest#maintainer_can_modify}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#owner RepositoryPullRequest#owner}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "base_ref": base_ref,
            "base_repository": base_repository,
            "head_ref": head_ref,
            "title": title,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if body is not None:
            self._values["body"] = body
        if maintainer_can_modify is not None:
            self._values["maintainer_can_modify"] = maintainer_can_modify
        if owner is not None:
            self._values["owner"] = owner

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def base_ref(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#base_ref RepositoryPullRequest#base_ref}.'''
        result = self._values.get("base_ref")
        assert result is not None, "Required property 'base_ref' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def base_repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#base_repository RepositoryPullRequest#base_repository}.'''
        result = self._values.get("base_repository")
        assert result is not None, "Required property 'base_repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def head_ref(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#head_ref RepositoryPullRequest#head_ref}.'''
        result = self._values.get("head_ref")
        assert result is not None, "Required property 'head_ref' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#title RepositoryPullRequest#title}.'''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#body RepositoryPullRequest#body}.'''
        result = self._values.get("body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintainer_can_modify(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#maintainer_can_modify RepositoryPullRequest#maintainer_can_modify}.'''
        result = self._values.get("maintainer_can_modify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_pull_request.html#owner RepositoryPullRequest#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryPullRequestConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryTemplate",
    jsii_struct_bases=[],
    name_mapping={"owner": "owner", "repository": "repository"},
)
class RepositoryTemplate:
    def __init__(self, *, owner: builtins.str, repository: builtins.str) -> None:
        '''
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#owner Repository#owner}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#repository Repository#repository}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "owner": owner,
            "repository": repository,
        }

    @builtins.property
    def owner(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#owner Repository#owner}.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository.html#repository Repository#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RepositoryWebhook(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.RepositoryWebhook",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html github_repository_webhook}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[builtins.str],
        repository: builtins.str,
        active: typing.Optional[builtins.bool] = None,
        configuration: typing.Optional[typing.Sequence["RepositoryWebhookConfiguration"]] = None,
        name: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html github_repository_webhook} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#events RepositoryWebhook#events}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#repository RepositoryWebhook#repository}.
        :param active: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#active RepositoryWebhook#active}.
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#configuration RepositoryWebhook#configuration}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#name RepositoryWebhook#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RepositoryWebhookConfig(
            events=events,
            repository=repository,
            active=active,
            configuration=configuration,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RepositoryWebhook, self, [scope, id, config])

    @jsii.member(jsii_name="resetActive")
    def reset_active(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActive", []))

    @jsii.member(jsii_name="resetConfiguration")
    def reset_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfiguration", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventsInput")
    def events_input(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activeInput")
    def active_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "activeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInput")
    def configuration_input(
        self,
    ) -> typing.Optional[typing.List["RepositoryWebhookConfiguration"]]:
        return typing.cast(typing.Optional[typing.List["RepositoryWebhookConfiguration"]], jsii.get(self, "configurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="active")
    def active(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "active"))

    @active.setter
    def active(self, value: builtins.bool) -> None:
        jsii.set(self, "active", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> typing.List["RepositoryWebhookConfiguration"]:
        return typing.cast(typing.List["RepositoryWebhookConfiguration"], jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(
        self,
        value: typing.List["RepositoryWebhookConfiguration"],
    ) -> None:
        jsii.set(self, "configuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="events")
    def events(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "events"))

    @events.setter
    def events(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "events", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryWebhookConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "events": "events",
        "repository": "repository",
        "active": "active",
        "configuration": "configuration",
        "name": "name",
    },
)
class RepositoryWebhookConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        events: typing.Sequence[builtins.str],
        repository: builtins.str,
        active: typing.Optional[builtins.bool] = None,
        configuration: typing.Optional[typing.Sequence["RepositoryWebhookConfiguration"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#events RepositoryWebhook#events}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#repository RepositoryWebhook#repository}.
        :param active: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#active RepositoryWebhook#active}.
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#configuration RepositoryWebhook#configuration}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#name RepositoryWebhook#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "events": events,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if active is not None:
            self._values["active"] = active
        if configuration is not None:
            self._values["configuration"] = configuration
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def events(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#events RepositoryWebhook#events}.'''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#repository RepositoryWebhook#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def active(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#active RepositoryWebhook#active}.'''
        result = self._values.get("active")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def configuration(
        self,
    ) -> typing.Optional[typing.List["RepositoryWebhookConfiguration"]]:
        '''configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#configuration RepositoryWebhook#configuration}
        '''
        result = self._values.get("configuration")
        return typing.cast(typing.Optional[typing.List["RepositoryWebhookConfiguration"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#name RepositoryWebhook#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryWebhookConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.RepositoryWebhookConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "url": "url",
        "content_type": "contentType",
        "insecure_ssl": "insecureSsl",
        "secret": "secret",
    },
)
class RepositoryWebhookConfiguration:
    def __init__(
        self,
        *,
        url: builtins.str,
        content_type: typing.Optional[builtins.str] = None,
        insecure_ssl: typing.Optional[builtins.bool] = None,
        secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#url RepositoryWebhook#url}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#content_type RepositoryWebhook#content_type}.
        :param insecure_ssl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#insecure_ssl RepositoryWebhook#insecure_ssl}.
        :param secret: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#secret RepositoryWebhook#secret}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }
        if content_type is not None:
            self._values["content_type"] = content_type
        if insecure_ssl is not None:
            self._values["insecure_ssl"] = insecure_ssl
        if secret is not None:
            self._values["secret"] = secret

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#url RepositoryWebhook#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#content_type RepositoryWebhook#content_type}.'''
        result = self._values.get("content_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure_ssl(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#insecure_ssl RepositoryWebhook#insecure_ssl}.'''
        result = self._values.get("insecure_ssl")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/repository_webhook.html#secret RepositoryWebhook#secret}.'''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryWebhookConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Team(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.Team",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/team.html github_team}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        create_default_maintainer: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        ldap_dn: typing.Optional[builtins.str] = None,
        parent_team_id: typing.Optional[jsii.Number] = None,
        privacy: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/team.html github_team} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#name Team#name}.
        :param create_default_maintainer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#create_default_maintainer Team#create_default_maintainer}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#description Team#description}.
        :param ldap_dn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#ldap_dn Team#ldap_dn}.
        :param parent_team_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#parent_team_id Team#parent_team_id}.
        :param privacy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#privacy Team#privacy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TeamConfig(
            name=name,
            create_default_maintainer=create_default_maintainer,
            description=description,
            ldap_dn=ldap_dn,
            parent_team_id=parent_team_id,
            privacy=privacy,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Team, self, [scope, id, config])

    @jsii.member(jsii_name="resetCreateDefaultMaintainer")
    def reset_create_default_maintainer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateDefaultMaintainer", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetLdapDn")
    def reset_ldap_dn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLdapDn", []))

    @jsii.member(jsii_name="resetParentTeamId")
    def reset_parent_team_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentTeamId", []))

    @jsii.member(jsii_name="resetPrivacy")
    def reset_privacy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivacy", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="membersCount")
    def members_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "membersCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slug")
    def slug(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "slug"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createDefaultMaintainerInput")
    def create_default_maintainer_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "createDefaultMaintainerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ldapDnInput")
    def ldap_dn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ldapDnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentTeamIdInput")
    def parent_team_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "parentTeamIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privacyInput")
    def privacy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privacyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createDefaultMaintainer")
    def create_default_maintainer(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "createDefaultMaintainer"))

    @create_default_maintainer.setter
    def create_default_maintainer(self, value: builtins.bool) -> None:
        jsii.set(self, "createDefaultMaintainer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ldapDn")
    def ldap_dn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ldapDn"))

    @ldap_dn.setter
    def ldap_dn(self, value: builtins.str) -> None:
        jsii.set(self, "ldapDn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentTeamId")
    def parent_team_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "parentTeamId"))

    @parent_team_id.setter
    def parent_team_id(self, value: jsii.Number) -> None:
        jsii.set(self, "parentTeamId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privacy")
    def privacy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privacy"))

    @privacy.setter
    def privacy(self, value: builtins.str) -> None:
        jsii.set(self, "privacy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.TeamConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "create_default_maintainer": "createDefaultMaintainer",
        "description": "description",
        "ldap_dn": "ldapDn",
        "parent_team_id": "parentTeamId",
        "privacy": "privacy",
    },
)
class TeamConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        create_default_maintainer: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        ldap_dn: typing.Optional[builtins.str] = None,
        parent_team_id: typing.Optional[jsii.Number] = None,
        privacy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#name Team#name}.
        :param create_default_maintainer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#create_default_maintainer Team#create_default_maintainer}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#description Team#description}.
        :param ldap_dn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#ldap_dn Team#ldap_dn}.
        :param parent_team_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#parent_team_id Team#parent_team_id}.
        :param privacy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#privacy Team#privacy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if create_default_maintainer is not None:
            self._values["create_default_maintainer"] = create_default_maintainer
        if description is not None:
            self._values["description"] = description
        if ldap_dn is not None:
            self._values["ldap_dn"] = ldap_dn
        if parent_team_id is not None:
            self._values["parent_team_id"] = parent_team_id
        if privacy is not None:
            self._values["privacy"] = privacy

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#name Team#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def create_default_maintainer(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#create_default_maintainer Team#create_default_maintainer}.'''
        result = self._values.get("create_default_maintainer")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#description Team#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ldap_dn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#ldap_dn Team#ldap_dn}.'''
        result = self._values.get("ldap_dn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_team_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#parent_team_id Team#parent_team_id}.'''
        result = self._values.get("parent_team_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def privacy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team.html#privacy Team#privacy}.'''
        result = self._values.get("privacy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TeamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TeamMembership(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.TeamMembership",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/team_membership.html github_team_membership}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        team_id: builtins.str,
        username: builtins.str,
        role: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/team_membership.html github_team_membership} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param team_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_membership.html#team_id TeamMembership#team_id}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_membership.html#username TeamMembership#username}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_membership.html#role TeamMembership#role}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TeamMembershipConfig(
            team_id=team_id,
            username=username,
            role=role,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(TeamMembership, self, [scope, id, config])

    @jsii.member(jsii_name="resetRole")
    def reset_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRole", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamIdInput")
    def team_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamId"))

    @team_id.setter
    def team_id(self, value: builtins.str) -> None:
        jsii.set(self, "teamId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.TeamMembershipConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "team_id": "teamId",
        "username": "username",
        "role": "role",
    },
)
class TeamMembershipConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        team_id: builtins.str,
        username: builtins.str,
        role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param team_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_membership.html#team_id TeamMembership#team_id}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_membership.html#username TeamMembership#username}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_membership.html#role TeamMembership#role}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "team_id": team_id,
            "username": username,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def team_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_membership.html#team_id TeamMembership#team_id}.'''
        result = self._values.get("team_id")
        assert result is not None, "Required property 'team_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_membership.html#username TeamMembership#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_membership.html#role TeamMembership#role}.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TeamMembershipConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TeamRepository(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.TeamRepository",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/team_repository.html github_team_repository}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        repository: builtins.str,
        team_id: builtins.str,
        permission: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/team_repository.html github_team_repository} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_repository.html#repository TeamRepository#repository}.
        :param team_id: ID or slug of team. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_repository.html#team_id TeamRepository#team_id}
        :param permission: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_repository.html#permission TeamRepository#permission}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TeamRepositoryConfig(
            repository=repository,
            team_id=team_id,
            permission=permission,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(TeamRepository, self, [scope, id, config])

    @jsii.member(jsii_name="resetPermission")
    def reset_permission(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermission", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamIdInput")
    def team_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        jsii.set(self, "permission", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamId"))

    @team_id.setter
    def team_id(self, value: builtins.str) -> None:
        jsii.set(self, "teamId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.TeamRepositoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "repository": "repository",
        "team_id": "teamId",
        "permission": "permission",
    },
)
class TeamRepositoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        repository: builtins.str,
        team_id: builtins.str,
        permission: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_repository.html#repository TeamRepository#repository}.
        :param team_id: ID or slug of team. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_repository.html#team_id TeamRepository#team_id}
        :param permission: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_repository.html#permission TeamRepository#permission}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "repository": repository,
            "team_id": team_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if permission is not None:
            self._values["permission"] = permission

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_repository.html#repository TeamRepository#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def team_id(self) -> builtins.str:
        '''ID or slug of team.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_repository.html#team_id TeamRepository#team_id}
        '''
        result = self._values.get("team_id")
        assert result is not None, "Required property 'team_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_repository.html#permission TeamRepository#permission}.'''
        result = self._values.get("permission")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TeamRepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TeamSyncGroupMapping(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.TeamSyncGroupMapping",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html github_team_sync_group_mapping}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        team_slug: builtins.str,
        group: typing.Optional[typing.Sequence["TeamSyncGroupMappingGroup"]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html github_team_sync_group_mapping} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param team_slug: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#team_slug TeamSyncGroupMapping#team_slug}.
        :param group: group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#group TeamSyncGroupMapping#group}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TeamSyncGroupMappingConfig(
            team_slug=team_slug,
            group=group,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(TeamSyncGroupMapping, self, [scope, id, config])

    @jsii.member(jsii_name="resetGroup")
    def reset_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroup", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamSlugInput")
    def team_slug_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamSlugInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupInput")
    def group_input(self) -> typing.Optional[typing.List["TeamSyncGroupMappingGroup"]]:
        return typing.cast(typing.Optional[typing.List["TeamSyncGroupMappingGroup"]], jsii.get(self, "groupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="group")
    def group(self) -> typing.List["TeamSyncGroupMappingGroup"]:
        return typing.cast(typing.List["TeamSyncGroupMappingGroup"], jsii.get(self, "group"))

    @group.setter
    def group(self, value: typing.List["TeamSyncGroupMappingGroup"]) -> None:
        jsii.set(self, "group", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamSlug")
    def team_slug(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamSlug"))

    @team_slug.setter
    def team_slug(self, value: builtins.str) -> None:
        jsii.set(self, "teamSlug", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.TeamSyncGroupMappingConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "team_slug": "teamSlug",
        "group": "group",
    },
)
class TeamSyncGroupMappingConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        team_slug: builtins.str,
        group: typing.Optional[typing.Sequence["TeamSyncGroupMappingGroup"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param team_slug: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#team_slug TeamSyncGroupMapping#team_slug}.
        :param group: group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#group TeamSyncGroupMapping#group}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "team_slug": team_slug,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if group is not None:
            self._values["group"] = group

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def team_slug(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#team_slug TeamSyncGroupMapping#team_slug}.'''
        result = self._values.get("team_slug")
        assert result is not None, "Required property 'team_slug' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group(self) -> typing.Optional[typing.List["TeamSyncGroupMappingGroup"]]:
        '''group block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#group TeamSyncGroupMapping#group}
        '''
        result = self._values.get("group")
        return typing.cast(typing.Optional[typing.List["TeamSyncGroupMappingGroup"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TeamSyncGroupMappingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-github.TeamSyncGroupMappingGroup",
    jsii_struct_bases=[],
    name_mapping={
        "group_description": "groupDescription",
        "group_id": "groupId",
        "group_name": "groupName",
    },
)
class TeamSyncGroupMappingGroup:
    def __init__(
        self,
        *,
        group_description: builtins.str,
        group_id: builtins.str,
        group_name: builtins.str,
    ) -> None:
        '''
        :param group_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#group_description TeamSyncGroupMapping#group_description}.
        :param group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#group_id TeamSyncGroupMapping#group_id}.
        :param group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#group_name TeamSyncGroupMapping#group_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "group_description": group_description,
            "group_id": group_id,
            "group_name": group_name,
        }

    @builtins.property
    def group_description(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#group_description TeamSyncGroupMapping#group_description}.'''
        result = self._values.get("group_description")
        assert result is not None, "Required property 'group_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#group_id TeamSyncGroupMapping#group_id}.'''
        result = self._values.get("group_id")
        assert result is not None, "Required property 'group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/team_sync_group_mapping.html#group_name TeamSyncGroupMapping#group_name}.'''
        result = self._values.get("group_name")
        assert result is not None, "Required property 'group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TeamSyncGroupMappingGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UserGpgKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.UserGpgKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/user_gpg_key.html github_user_gpg_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        armored_public_key: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/user_gpg_key.html github_user_gpg_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param armored_public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_gpg_key.html#armored_public_key UserGpgKey#armored_public_key}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = UserGpgKeyConfig(
            armored_public_key=armored_public_key,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(UserGpgKey, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="armoredPublicKeyInput")
    def armored_public_key_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "armoredPublicKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="armoredPublicKey")
    def armored_public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "armoredPublicKey"))

    @armored_public_key.setter
    def armored_public_key(self, value: builtins.str) -> None:
        jsii.set(self, "armoredPublicKey", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.UserGpgKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "armored_public_key": "armoredPublicKey",
    },
)
class UserGpgKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        armored_public_key: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param armored_public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_gpg_key.html#armored_public_key UserGpgKey#armored_public_key}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "armored_public_key": armored_public_key,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def armored_public_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_gpg_key.html#armored_public_key UserGpgKey#armored_public_key}.'''
        result = self._values.get("armored_public_key")
        assert result is not None, "Required property 'armored_public_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserGpgKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UserInvitationAccepter(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.UserInvitationAccepter",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/user_invitation_accepter.html github_user_invitation_accepter}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        invitation_id: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/user_invitation_accepter.html github_user_invitation_accepter} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param invitation_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_invitation_accepter.html#invitation_id UserInvitationAccepter#invitation_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = UserInvitationAccepterConfig(
            invitation_id=invitation_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(UserInvitationAccepter, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invitationIdInput")
    def invitation_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invitationIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invitationId")
    def invitation_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invitationId"))

    @invitation_id.setter
    def invitation_id(self, value: builtins.str) -> None:
        jsii.set(self, "invitationId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.UserInvitationAccepterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "invitation_id": "invitationId",
    },
)
class UserInvitationAccepterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        invitation_id: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param invitation_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_invitation_accepter.html#invitation_id UserInvitationAccepter#invitation_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "invitation_id": invitation_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def invitation_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_invitation_accepter.html#invitation_id UserInvitationAccepter#invitation_id}.'''
        result = self._values.get("invitation_id")
        assert result is not None, "Required property 'invitation_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserInvitationAccepterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UserSshKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-github.UserSshKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/github/r/user_ssh_key.html github_user_ssh_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        key: builtins.str,
        title: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/github/r/user_ssh_key.html github_user_ssh_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_ssh_key.html#key UserSshKey#key}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_ssh_key.html#title UserSshKey#title}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = UserSshKeyConfig(
            key=key,
            title=title,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(UserSshKey, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-github.UserSshKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "key": "key",
        "title": "title",
    },
)
class UserSshKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        key: builtins.str,
        title: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_ssh_key.html#key UserSshKey#key}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_ssh_key.html#title UserSshKey#title}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "title": title,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_ssh_key.html#key UserSshKey#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/github/r/user_ssh_key.html#title UserSshKey#title}.'''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserSshKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ActionsEnvironmentSecret",
    "ActionsEnvironmentSecretConfig",
    "ActionsOrganizationSecret",
    "ActionsOrganizationSecretConfig",
    "ActionsSecret",
    "ActionsSecretConfig",
    "AppInstallationRepository",
    "AppInstallationRepositoryConfig",
    "Branch",
    "BranchConfig",
    "BranchDefault",
    "BranchDefaultConfig",
    "BranchProtection",
    "BranchProtectionConfig",
    "BranchProtectionRequiredPullRequestReviews",
    "BranchProtectionRequiredStatusChecks",
    "BranchProtectionV3",
    "BranchProtectionV3Config",
    "BranchProtectionV3RequiredPullRequestReviews",
    "BranchProtectionV3RequiredStatusChecks",
    "BranchProtectionV3Restrictions",
    "DataGithubActionsPublicKey",
    "DataGithubActionsPublicKeyConfig",
    "DataGithubBranch",
    "DataGithubBranchConfig",
    "DataGithubCollaborators",
    "DataGithubCollaboratorsCollaborator",
    "DataGithubCollaboratorsConfig",
    "DataGithubIpRanges",
    "DataGithubIpRangesConfig",
    "DataGithubMembership",
    "DataGithubMembershipConfig",
    "DataGithubOrganization",
    "DataGithubOrganizationConfig",
    "DataGithubOrganizationTeamSyncGroups",
    "DataGithubOrganizationTeamSyncGroupsConfig",
    "DataGithubOrganizationTeamSyncGroupsGroups",
    "DataGithubOrganizationTeams",
    "DataGithubOrganizationTeamsConfig",
    "DataGithubOrganizationTeamsTeams",
    "DataGithubRelease",
    "DataGithubReleaseConfig",
    "DataGithubRepositories",
    "DataGithubRepositoriesConfig",
    "DataGithubRepository",
    "DataGithubRepositoryConfig",
    "DataGithubRepositoryMilestone",
    "DataGithubRepositoryMilestoneConfig",
    "DataGithubRepositoryPages",
    "DataGithubRepositoryPagesSource",
    "DataGithubRepositoryPullRequest",
    "DataGithubRepositoryPullRequestConfig",
    "DataGithubRepositoryPullRequests",
    "DataGithubRepositoryPullRequestsConfig",
    "DataGithubRepositoryPullRequestsResults",
    "DataGithubTeam",
    "DataGithubTeamConfig",
    "DataGithubUser",
    "DataGithubUserConfig",
    "GithubProvider",
    "GithubProviderAppAuth",
    "GithubProviderConfig",
    "IssueLabel",
    "IssueLabelConfig",
    "Membership",
    "MembershipConfig",
    "OrganizationBlock",
    "OrganizationBlockConfig",
    "OrganizationProject",
    "OrganizationProjectConfig",
    "OrganizationWebhook",
    "OrganizationWebhookConfig",
    "OrganizationWebhookConfiguration",
    "ProjectCard",
    "ProjectCardConfig",
    "ProjectColumn",
    "ProjectColumnConfig",
    "Repository",
    "RepositoryCollaborator",
    "RepositoryCollaboratorConfig",
    "RepositoryConfig",
    "RepositoryDeployKey",
    "RepositoryDeployKeyConfig",
    "RepositoryEnvironment",
    "RepositoryEnvironmentConfig",
    "RepositoryEnvironmentDeploymentBranchPolicy",
    "RepositoryEnvironmentReviewers",
    "RepositoryFile",
    "RepositoryFileConfig",
    "RepositoryMilestone",
    "RepositoryMilestoneConfig",
    "RepositoryPages",
    "RepositoryPagesSource",
    "RepositoryProject",
    "RepositoryProjectConfig",
    "RepositoryPullRequest",
    "RepositoryPullRequestConfig",
    "RepositoryTemplate",
    "RepositoryWebhook",
    "RepositoryWebhookConfig",
    "RepositoryWebhookConfiguration",
    "Team",
    "TeamConfig",
    "TeamMembership",
    "TeamMembershipConfig",
    "TeamRepository",
    "TeamRepositoryConfig",
    "TeamSyncGroupMapping",
    "TeamSyncGroupMappingConfig",
    "TeamSyncGroupMappingGroup",
    "UserGpgKey",
    "UserGpgKeyConfig",
    "UserInvitationAccepter",
    "UserInvitationAccepterConfig",
    "UserSshKey",
    "UserSshKeyConfig",
]

publication.publish()
