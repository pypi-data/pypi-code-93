'''
# Terraform CDK pagerduty Provider ~> 1.10

This repo builds and publishes the Terraform pagerduty Provider bindings for [cdktf](https://cdk.tf).

Current build targets are:

* npm
* Pypi
* Nuget
* Maven

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform pagerduty Provider version 1:1. In fact, it always tracks `latest` of `~> 1.10` with every release. If there scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform pagerduty Provider](https://github.com/terraform-providers/terraform-provider-pagerduty)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform pagerduty Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

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


class Addon(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.Addon",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/addon.html pagerduty_addon}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        src: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/addon.html pagerduty_addon} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/addon.html#name Addon#name}.
        :param src: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/addon.html#src Addon#src}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AddonConfig(
            name=name,
            src=src,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Addon, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="srcInput")
    def src_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "srcInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="src")
    def src(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "src"))

    @src.setter
    def src(self, value: builtins.str) -> None:
        jsii.set(self, "src", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.AddonConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "src": "src",
    },
)
class AddonConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        src: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/addon.html#name Addon#name}.
        :param src: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/addon.html#src Addon#src}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "src": src,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/addon.html#name Addon#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def src(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/addon.html#src Addon#src}.'''
        result = self._values.get("src")
        assert result is not None, "Required property 'src' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddonConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BusinessService(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.BusinessService",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html pagerduty_business_service}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        point_of_contact: typing.Optional[builtins.str] = None,
        team: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html pagerduty_business_service} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#name BusinessService#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#description BusinessService#description}.
        :param point_of_contact: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#point_of_contact BusinessService#point_of_contact}.
        :param team: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#team BusinessService#team}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#type BusinessService#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BusinessServiceConfig(
            name=name,
            description=description,
            point_of_contact=point_of_contact,
            team=team,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(BusinessService, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetPointOfContact")
    def reset_point_of_contact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPointOfContact", []))

    @jsii.member(jsii_name="resetTeam")
    def reset_team(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeam", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selfAttribute")
    def self_attribute(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "selfAttribute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="summary")
    def summary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "summary"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pointOfContactInput")
    def point_of_contact_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pointOfContactInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamInput")
    def team_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

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
    @jsii.member(jsii_name="pointOfContact")
    def point_of_contact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pointOfContact"))

    @point_of_contact.setter
    def point_of_contact(self, value: builtins.str) -> None:
        jsii.set(self, "pointOfContact", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @team.setter
    def team(self, value: builtins.str) -> None:
        jsii.set(self, "team", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.BusinessServiceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "description": "description",
        "point_of_contact": "pointOfContact",
        "team": "team",
        "type": "type",
    },
)
class BusinessServiceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        point_of_contact: typing.Optional[builtins.str] = None,
        team: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#name BusinessService#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#description BusinessService#description}.
        :param point_of_contact: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#point_of_contact BusinessService#point_of_contact}.
        :param team: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#team BusinessService#team}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#type BusinessService#type}.
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
        if description is not None:
            self._values["description"] = description
        if point_of_contact is not None:
            self._values["point_of_contact"] = point_of_contact
        if team is not None:
            self._values["team"] = team
        if type is not None:
            self._values["type"] = type

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#name BusinessService#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#description BusinessService#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def point_of_contact(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#point_of_contact BusinessService#point_of_contact}.'''
        result = self._values.get("point_of_contact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def team(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#team BusinessService#team}.'''
        result = self._values.get("team")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/business_service.html#type BusinessService#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BusinessServiceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyBusinessService(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyBusinessService",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/business_service.html pagerduty_business_service}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/business_service.html pagerduty_business_service} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/business_service.html#name DataPagerdutyBusinessService#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyBusinessServiceConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyBusinessService, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyBusinessServiceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataPagerdutyBusinessServiceConfig(cdktf.TerraformMetaArguments):
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
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/business_service.html#name DataPagerdutyBusinessService#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/business_service.html#name DataPagerdutyBusinessService#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyBusinessServiceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyEscalationPolicy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyEscalationPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/escalation_policy.html pagerduty_escalation_policy}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/escalation_policy.html pagerduty_escalation_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/escalation_policy.html#name DataPagerdutyEscalationPolicy#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyEscalationPolicyConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyEscalationPolicy, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyEscalationPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataPagerdutyEscalationPolicyConfig(cdktf.TerraformMetaArguments):
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
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/escalation_policy.html#name DataPagerdutyEscalationPolicy#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/escalation_policy.html#name DataPagerdutyEscalationPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyEscalationPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyExtensionSchema(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyExtensionSchema",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/extension_schema.html pagerduty_extension_schema}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/extension_schema.html pagerduty_extension_schema} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/extension_schema.html#name DataPagerdutyExtensionSchema#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyExtensionSchemaConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyExtensionSchema, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyExtensionSchemaConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataPagerdutyExtensionSchemaConfig(cdktf.TerraformMetaArguments):
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
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/extension_schema.html#name DataPagerdutyExtensionSchema#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/extension_schema.html#name DataPagerdutyExtensionSchema#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyExtensionSchemaConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyPriority(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyPriority",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/priority.html pagerduty_priority}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/priority.html pagerduty_priority} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the priority to find in the PagerDuty API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/priority.html#name DataPagerdutyPriority#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyPriorityConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyPriority, self, [scope, id, config])

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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyPriorityConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataPagerdutyPriorityConfig(cdktf.TerraformMetaArguments):
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
        :param name: The name of the priority to find in the PagerDuty API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/priority.html#name DataPagerdutyPriority#name}
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
        '''The name of the priority to find in the PagerDuty API.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/priority.html#name DataPagerdutyPriority#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyPriorityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyRuleset(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyRuleset",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/ruleset.html pagerduty_ruleset}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/ruleset.html pagerduty_ruleset} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/ruleset.html#name DataPagerdutyRuleset#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyRulesetConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyRuleset, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingKeys")
    def routing_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "routingKeys"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyRulesetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataPagerdutyRulesetConfig(cdktf.TerraformMetaArguments):
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
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/ruleset.html#name DataPagerdutyRuleset#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/ruleset.html#name DataPagerdutyRuleset#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyRulesetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutySchedule(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutySchedule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/schedule.html pagerduty_schedule}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/schedule.html pagerduty_schedule} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/schedule.html#name DataPagerdutySchedule#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyScheduleConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutySchedule, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyScheduleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataPagerdutyScheduleConfig(cdktf.TerraformMetaArguments):
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
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/schedule.html#name DataPagerdutySchedule#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/schedule.html#name DataPagerdutySchedule#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyScheduleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyService(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyService",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/service.html pagerduty_service}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/service.html pagerduty_service} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/service.html#name DataPagerdutyService#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyServiceConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyService, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyServiceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataPagerdutyServiceConfig(cdktf.TerraformMetaArguments):
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
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/service.html#name DataPagerdutyService#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/service.html#name DataPagerdutyService#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyServiceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyTeam(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyTeam",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/team.html pagerduty_team}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        parent: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/team.html pagerduty_team} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the team to find in the PagerDuty API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/team.html#name DataPagerdutyTeam#name}
        :param parent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/team.html#parent DataPagerdutyTeam#parent}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyTeamConfig(
            name=name,
            parent=parent,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyTeam, self, [scope, id, config])

    @jsii.member(jsii_name="resetParent")
    def reset_parent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParent", []))

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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentInput")
    def parent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parent")
    def parent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parent"))

    @parent.setter
    def parent(self, value: builtins.str) -> None:
        jsii.set(self, "parent", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyTeamConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "parent": "parent",
    },
)
class DataPagerdutyTeamConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        parent: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the team to find in the PagerDuty API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/team.html#name DataPagerdutyTeam#name}
        :param parent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/team.html#parent DataPagerdutyTeam#parent}.
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
        if parent is not None:
            self._values["parent"] = parent

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
        '''The name of the team to find in the PagerDuty API.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/team.html#name DataPagerdutyTeam#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/team.html#parent DataPagerdutyTeam#parent}.'''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyTeamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyUser(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/user.html pagerduty_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        email: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/user.html pagerduty_user} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user.html#email DataPagerdutyUser#email}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyUserConfig(
            email=email,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyUser, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        jsii.set(self, "email", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "email": "email",
    },
)
class DataPagerdutyUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        email: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user.html#email DataPagerdutyUser#email}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
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
    def email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user.html#email DataPagerdutyUser#email}.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyUserContactMethod(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyUserContactMethod",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html pagerduty_user_contact_method}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        label: builtins.str,
        type: builtins.str,
        user_id: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html pagerduty_user_contact_method} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param label: The name of the contact method to find in the PagerDuty API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html#label DataPagerdutyUserContactMethod#label}
        :param type: The type of the contact method. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html#type DataPagerdutyUserContactMethod#type}
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html#user_id DataPagerdutyUserContactMethod#user_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyUserContactMethodConfig(
            label=label,
            type=type,
            user_id=user_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyUserContactMethod, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "labelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        jsii.set(self, "label", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        jsii.set(self, "userId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyUserContactMethodConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "label": "label",
        "type": "type",
        "user_id": "userId",
    },
)
class DataPagerdutyUserContactMethodConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        label: builtins.str,
        type: builtins.str,
        user_id: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param label: The name of the contact method to find in the PagerDuty API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html#label DataPagerdutyUserContactMethod#label}
        :param type: The type of the contact method. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html#type DataPagerdutyUserContactMethod#type}
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html#user_id DataPagerdutyUserContactMethod#user_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "type": type,
            "user_id": user_id,
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
    def label(self) -> builtins.str:
        '''The name of the contact method to find in the PagerDuty API.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html#label DataPagerdutyUserContactMethod#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the contact method.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html#type DataPagerdutyUserContactMethod#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/user_contact_method.html#user_id DataPagerdutyUserContactMethod#user_id}.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyUserContactMethodConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPagerdutyVendor(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyVendor",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/d/vendor.html pagerduty_vendor}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        name_regex: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/d/vendor.html pagerduty_vendor} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/vendor.html#name DataPagerdutyVendor#name}.
        :param name_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/vendor.html#name_regex DataPagerdutyVendor#name_regex}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataPagerdutyVendorConfig(
            name=name,
            name_regex=name_regex,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataPagerdutyVendor, self, [scope, id, config])

    @jsii.member(jsii_name="resetNameRegex")
    def reset_name_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNameRegex", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegexInput")
    def name_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameRegexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegex")
    def name_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameRegex"))

    @name_regex.setter
    def name_regex(self, value: builtins.str) -> None:
        jsii.set(self, "nameRegex", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.DataPagerdutyVendorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "name_regex": "nameRegex",
    },
)
class DataPagerdutyVendorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        name_regex: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/vendor.html#name DataPagerdutyVendor#name}.
        :param name_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/vendor.html#name_regex DataPagerdutyVendor#name_regex}.
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
        if name_regex is not None:
            self._values["name_regex"] = name_regex

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/vendor.html#name DataPagerdutyVendor#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name_regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/d/vendor.html#name_regex DataPagerdutyVendor#name_regex}.'''
        result = self._values.get("name_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPagerdutyVendorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EscalationPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.EscalationPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html pagerduty_escalation_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        rule: typing.Sequence["EscalationPolicyRule"],
        description: typing.Optional[builtins.str] = None,
        num_loops: typing.Optional[jsii.Number] = None,
        teams: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html pagerduty_escalation_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#name EscalationPolicy#name}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#rule EscalationPolicy#rule}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#description EscalationPolicy#description}.
        :param num_loops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#num_loops EscalationPolicy#num_loops}.
        :param teams: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#teams EscalationPolicy#teams}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EscalationPolicyConfig(
            name=name,
            rule=rule,
            description=description,
            num_loops=num_loops,
            teams=teams,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(EscalationPolicy, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetNumLoops")
    def reset_num_loops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumLoops", []))

    @jsii.member(jsii_name="resetTeams")
    def reset_teams(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeams", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleInput")
    def rule_input(self) -> typing.List["EscalationPolicyRule"]:
        return typing.cast(typing.List["EscalationPolicyRule"], jsii.get(self, "ruleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numLoopsInput")
    def num_loops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numLoopsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamsInput")
    def teams_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "teamsInput"))

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
    @jsii.member(jsii_name="numLoops")
    def num_loops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numLoops"))

    @num_loops.setter
    def num_loops(self, value: jsii.Number) -> None:
        jsii.set(self, "numLoops", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rule")
    def rule(self) -> typing.List["EscalationPolicyRule"]:
        return typing.cast(typing.List["EscalationPolicyRule"], jsii.get(self, "rule"))

    @rule.setter
    def rule(self, value: typing.List["EscalationPolicyRule"]) -> None:
        jsii.set(self, "rule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teams")
    def teams(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "teams"))

    @teams.setter
    def teams(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "teams", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.EscalationPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "rule": "rule",
        "description": "description",
        "num_loops": "numLoops",
        "teams": "teams",
    },
)
class EscalationPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        rule: typing.Sequence["EscalationPolicyRule"],
        description: typing.Optional[builtins.str] = None,
        num_loops: typing.Optional[jsii.Number] = None,
        teams: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#name EscalationPolicy#name}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#rule EscalationPolicy#rule}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#description EscalationPolicy#description}.
        :param num_loops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#num_loops EscalationPolicy#num_loops}.
        :param teams: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#teams EscalationPolicy#teams}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "rule": rule,
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
        if num_loops is not None:
            self._values["num_loops"] = num_loops
        if teams is not None:
            self._values["teams"] = teams

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#name EscalationPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule(self) -> typing.List["EscalationPolicyRule"]:
        '''rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#rule EscalationPolicy#rule}
        '''
        result = self._values.get("rule")
        assert result is not None, "Required property 'rule' is missing"
        return typing.cast(typing.List["EscalationPolicyRule"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#description EscalationPolicy#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_loops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#num_loops EscalationPolicy#num_loops}.'''
        result = self._values.get("num_loops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def teams(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#teams EscalationPolicy#teams}.'''
        result = self._values.get("teams")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EscalationPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.EscalationPolicyRule",
    jsii_struct_bases=[],
    name_mapping={
        "escalation_delay_in_minutes": "escalationDelayInMinutes",
        "target": "target",
    },
)
class EscalationPolicyRule:
    def __init__(
        self,
        *,
        escalation_delay_in_minutes: jsii.Number,
        target: typing.Sequence["EscalationPolicyRuleTarget"],
    ) -> None:
        '''
        :param escalation_delay_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#escalation_delay_in_minutes EscalationPolicy#escalation_delay_in_minutes}.
        :param target: target block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#target EscalationPolicy#target}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "escalation_delay_in_minutes": escalation_delay_in_minutes,
            "target": target,
        }

    @builtins.property
    def escalation_delay_in_minutes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#escalation_delay_in_minutes EscalationPolicy#escalation_delay_in_minutes}.'''
        result = self._values.get("escalation_delay_in_minutes")
        assert result is not None, "Required property 'escalation_delay_in_minutes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def target(self) -> typing.List["EscalationPolicyRuleTarget"]:
        '''target block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#target EscalationPolicy#target}
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(typing.List["EscalationPolicyRuleTarget"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EscalationPolicyRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.EscalationPolicyRuleTarget",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "type": "type"},
)
class EscalationPolicyRuleTarget:
    def __init__(
        self,
        *,
        id: builtins.str,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#id EscalationPolicy#id}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#type EscalationPolicy#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#id EscalationPolicy#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/escalation_policy.html#type EscalationPolicy#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EscalationPolicyRuleTarget(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EventRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.EventRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html pagerduty_event_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        action_json: builtins.str,
        condition_json: builtins.str,
        advanced_condition_json: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html pagerduty_event_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param action_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html#action_json EventRule#action_json}.
        :param condition_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html#condition_json EventRule#condition_json}.
        :param advanced_condition_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html#advanced_condition_json EventRule#advanced_condition_json}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EventRuleConfig(
            action_json=action_json,
            condition_json=condition_json,
            advanced_condition_json=advanced_condition_json,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(EventRule, self, [scope, id, config])

    @jsii.member(jsii_name="resetAdvancedConditionJson")
    def reset_advanced_condition_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdvancedConditionJson", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionJsonInput")
    def action_json_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="catchAll")
    def catch_all(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "catchAll"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditionJsonInput")
    def condition_json_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "conditionJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedConditionJsonInput")
    def advanced_condition_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "advancedConditionJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionJson")
    def action_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionJson"))

    @action_json.setter
    def action_json(self, value: builtins.str) -> None:
        jsii.set(self, "actionJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedConditionJson")
    def advanced_condition_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "advancedConditionJson"))

    @advanced_condition_json.setter
    def advanced_condition_json(self, value: builtins.str) -> None:
        jsii.set(self, "advancedConditionJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditionJson")
    def condition_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "conditionJson"))

    @condition_json.setter
    def condition_json(self, value: builtins.str) -> None:
        jsii.set(self, "conditionJson", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.EventRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "action_json": "actionJson",
        "condition_json": "conditionJson",
        "advanced_condition_json": "advancedConditionJson",
    },
)
class EventRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        action_json: builtins.str,
        condition_json: builtins.str,
        advanced_condition_json: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param action_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html#action_json EventRule#action_json}.
        :param condition_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html#condition_json EventRule#condition_json}.
        :param advanced_condition_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html#advanced_condition_json EventRule#advanced_condition_json}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "action_json": action_json,
            "condition_json": condition_json,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if advanced_condition_json is not None:
            self._values["advanced_condition_json"] = advanced_condition_json

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
    def action_json(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html#action_json EventRule#action_json}.'''
        result = self._values.get("action_json")
        assert result is not None, "Required property 'action_json' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def condition_json(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html#condition_json EventRule#condition_json}.'''
        result = self._values.get("condition_json")
        assert result is not None, "Required property 'condition_json' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def advanced_condition_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/event_rule.html#advanced_condition_json EventRule#advanced_condition_json}.'''
        result = self._values.get("advanced_condition_json")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Extension(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.Extension",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html pagerduty_extension}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        extension_objects: typing.Sequence[builtins.str],
        extension_schema: builtins.str,
        config: typing.Optional[builtins.str] = None,
        endpoint_url: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html pagerduty_extension} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param extension_objects: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#extension_objects Extension#extension_objects}.
        :param extension_schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#extension_schema Extension#extension_schema}.
        :param config: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#config Extension#config}.
        :param endpoint_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#endpoint_url Extension#endpoint_url}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#name Extension#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#type Extension#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config_ = ExtensionConfig(
            extension_objects=extension_objects,
            extension_schema=extension_schema,
            config=config,
            endpoint_url=endpoint_url,
            name=name,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Extension, self, [scope, id, config_])

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="resetEndpointUrl")
    def reset_endpoint_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointUrl", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensionObjectsInput")
    def extension_objects_input(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "extensionObjectsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensionSchemaInput")
    def extension_schema_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "extensionSchemaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configInput")
    def config_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointUrlInput")
    def endpoint_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="config")
    def config(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "config"))

    @config.setter
    def config(self, value: builtins.str) -> None:
        jsii.set(self, "config", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointUrl")
    def endpoint_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointUrl"))

    @endpoint_url.setter
    def endpoint_url(self, value: builtins.str) -> None:
        jsii.set(self, "endpointUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensionObjects")
    def extension_objects(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "extensionObjects"))

    @extension_objects.setter
    def extension_objects(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "extensionObjects", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensionSchema")
    def extension_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "extensionSchema"))

    @extension_schema.setter
    def extension_schema(self, value: builtins.str) -> None:
        jsii.set(self, "extensionSchema", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ExtensionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "extension_objects": "extensionObjects",
        "extension_schema": "extensionSchema",
        "config": "config",
        "endpoint_url": "endpointUrl",
        "name": "name",
        "type": "type",
    },
)
class ExtensionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        extension_objects: typing.Sequence[builtins.str],
        extension_schema: builtins.str,
        config: typing.Optional[builtins.str] = None,
        endpoint_url: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param extension_objects: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#extension_objects Extension#extension_objects}.
        :param extension_schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#extension_schema Extension#extension_schema}.
        :param config: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#config Extension#config}.
        :param endpoint_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#endpoint_url Extension#endpoint_url}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#name Extension#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#type Extension#type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "extension_objects": extension_objects,
            "extension_schema": extension_schema,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if config is not None:
            self._values["config"] = config
        if endpoint_url is not None:
            self._values["endpoint_url"] = endpoint_url
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

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
    def extension_objects(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#extension_objects Extension#extension_objects}.'''
        result = self._values.get("extension_objects")
        assert result is not None, "Required property 'extension_objects' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def extension_schema(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#extension_schema Extension#extension_schema}.'''
        result = self._values.get("extension_schema")
        assert result is not None, "Required property 'extension_schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#config Extension#config}.'''
        result = self._values.get("config")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#endpoint_url Extension#endpoint_url}.'''
        result = self._values.get("endpoint_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#name Extension#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension.html#type Extension#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExtensionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExtensionServicenow(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.ExtensionServicenow",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html pagerduty_extension_servicenow}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        extension_objects: typing.Sequence[builtins.str],
        extension_schema: builtins.str,
        referer: builtins.str,
        snow_password: builtins.str,
        snow_user: builtins.str,
        sync_options: builtins.str,
        target: builtins.str,
        task_type: builtins.str,
        endpoint_url: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html pagerduty_extension_servicenow} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param extension_objects: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#extension_objects ExtensionServicenow#extension_objects}.
        :param extension_schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#extension_schema ExtensionServicenow#extension_schema}.
        :param referer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#referer ExtensionServicenow#referer}.
        :param snow_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#snow_password ExtensionServicenow#snow_password}.
        :param snow_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#snow_user ExtensionServicenow#snow_user}.
        :param sync_options: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#sync_options ExtensionServicenow#sync_options}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#target ExtensionServicenow#target}.
        :param task_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#task_type ExtensionServicenow#task_type}.
        :param endpoint_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#endpoint_url ExtensionServicenow#endpoint_url}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#name ExtensionServicenow#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#type ExtensionServicenow#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ExtensionServicenowConfig(
            extension_objects=extension_objects,
            extension_schema=extension_schema,
            referer=referer,
            snow_password=snow_password,
            snow_user=snow_user,
            sync_options=sync_options,
            target=target,
            task_type=task_type,
            endpoint_url=endpoint_url,
            name=name,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ExtensionServicenow, self, [scope, id, config])

    @jsii.member(jsii_name="resetEndpointUrl")
    def reset_endpoint_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointUrl", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensionObjectsInput")
    def extension_objects_input(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "extensionObjectsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensionSchemaInput")
    def extension_schema_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "extensionSchemaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refererInput")
    def referer_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "refererInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snowPasswordInput")
    def snow_password_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snowPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snowUserInput")
    def snow_user_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snowUserInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="syncOptionsInput")
    def sync_options_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "syncOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskTypeInput")
    def task_type_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointUrlInput")
    def endpoint_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointUrl")
    def endpoint_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointUrl"))

    @endpoint_url.setter
    def endpoint_url(self, value: builtins.str) -> None:
        jsii.set(self, "endpointUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensionObjects")
    def extension_objects(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "extensionObjects"))

    @extension_objects.setter
    def extension_objects(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "extensionObjects", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensionSchema")
    def extension_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "extensionSchema"))

    @extension_schema.setter
    def extension_schema(self, value: builtins.str) -> None:
        jsii.set(self, "extensionSchema", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="referer")
    def referer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "referer"))

    @referer.setter
    def referer(self, value: builtins.str) -> None:
        jsii.set(self, "referer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snowPassword")
    def snow_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snowPassword"))

    @snow_password.setter
    def snow_password(self, value: builtins.str) -> None:
        jsii.set(self, "snowPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snowUser")
    def snow_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snowUser"))

    @snow_user.setter
    def snow_user(self, value: builtins.str) -> None:
        jsii.set(self, "snowUser", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="syncOptions")
    def sync_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "syncOptions"))

    @sync_options.setter
    def sync_options(self, value: builtins.str) -> None:
        jsii.set(self, "syncOptions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskType")
    def task_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskType"))

    @task_type.setter
    def task_type(self, value: builtins.str) -> None:
        jsii.set(self, "taskType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ExtensionServicenowConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "extension_objects": "extensionObjects",
        "extension_schema": "extensionSchema",
        "referer": "referer",
        "snow_password": "snowPassword",
        "snow_user": "snowUser",
        "sync_options": "syncOptions",
        "target": "target",
        "task_type": "taskType",
        "endpoint_url": "endpointUrl",
        "name": "name",
        "type": "type",
    },
)
class ExtensionServicenowConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        extension_objects: typing.Sequence[builtins.str],
        extension_schema: builtins.str,
        referer: builtins.str,
        snow_password: builtins.str,
        snow_user: builtins.str,
        sync_options: builtins.str,
        target: builtins.str,
        task_type: builtins.str,
        endpoint_url: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param extension_objects: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#extension_objects ExtensionServicenow#extension_objects}.
        :param extension_schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#extension_schema ExtensionServicenow#extension_schema}.
        :param referer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#referer ExtensionServicenow#referer}.
        :param snow_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#snow_password ExtensionServicenow#snow_password}.
        :param snow_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#snow_user ExtensionServicenow#snow_user}.
        :param sync_options: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#sync_options ExtensionServicenow#sync_options}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#target ExtensionServicenow#target}.
        :param task_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#task_type ExtensionServicenow#task_type}.
        :param endpoint_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#endpoint_url ExtensionServicenow#endpoint_url}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#name ExtensionServicenow#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#type ExtensionServicenow#type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "extension_objects": extension_objects,
            "extension_schema": extension_schema,
            "referer": referer,
            "snow_password": snow_password,
            "snow_user": snow_user,
            "sync_options": sync_options,
            "target": target,
            "task_type": task_type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if endpoint_url is not None:
            self._values["endpoint_url"] = endpoint_url
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

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
    def extension_objects(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#extension_objects ExtensionServicenow#extension_objects}.'''
        result = self._values.get("extension_objects")
        assert result is not None, "Required property 'extension_objects' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def extension_schema(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#extension_schema ExtensionServicenow#extension_schema}.'''
        result = self._values.get("extension_schema")
        assert result is not None, "Required property 'extension_schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def referer(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#referer ExtensionServicenow#referer}.'''
        result = self._values.get("referer")
        assert result is not None, "Required property 'referer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def snow_password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#snow_password ExtensionServicenow#snow_password}.'''
        result = self._values.get("snow_password")
        assert result is not None, "Required property 'snow_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def snow_user(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#snow_user ExtensionServicenow#snow_user}.'''
        result = self._values.get("snow_user")
        assert result is not None, "Required property 'snow_user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sync_options(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#sync_options ExtensionServicenow#sync_options}.'''
        result = self._values.get("sync_options")
        assert result is not None, "Required property 'sync_options' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#target ExtensionServicenow#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#task_type ExtensionServicenow#task_type}.'''
        result = self._values.get("task_type")
        assert result is not None, "Required property 'task_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#endpoint_url ExtensionServicenow#endpoint_url}.'''
        result = self._values.get("endpoint_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#name ExtensionServicenow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/extension_servicenow.html#type ExtensionServicenow#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExtensionServicenowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MaintenanceWindow(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.MaintenanceWindow",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html pagerduty_maintenance_window}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        end_time: builtins.str,
        services: typing.Sequence[builtins.str],
        start_time: builtins.str,
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html pagerduty_maintenance_window} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param end_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#end_time MaintenanceWindow#end_time}.
        :param services: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#services MaintenanceWindow#services}.
        :param start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#start_time MaintenanceWindow#start_time}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#description MaintenanceWindow#description}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MaintenanceWindowConfig(
            end_time=end_time,
            services=services,
            start_time=start_time,
            description=description,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(MaintenanceWindow, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endTimeInput")
    def end_time_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="servicesInput")
    def services_input(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "servicesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startTimeInput")
    def start_time_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endTime")
    def end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endTime"))

    @end_time.setter
    def end_time(self, value: builtins.str) -> None:
        jsii.set(self, "endTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="services")
    def services(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "services"))

    @services.setter
    def services(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "services", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startTime")
    def start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startTime"))

    @start_time.setter
    def start_time(self, value: builtins.str) -> None:
        jsii.set(self, "startTime", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.MaintenanceWindowConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "end_time": "endTime",
        "services": "services",
        "start_time": "startTime",
        "description": "description",
    },
)
class MaintenanceWindowConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        end_time: builtins.str,
        services: typing.Sequence[builtins.str],
        start_time: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param end_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#end_time MaintenanceWindow#end_time}.
        :param services: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#services MaintenanceWindow#services}.
        :param start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#start_time MaintenanceWindow#start_time}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#description MaintenanceWindow#description}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "end_time": end_time,
            "services": services,
            "start_time": start_time,
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
    def end_time(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#end_time MaintenanceWindow#end_time}.'''
        result = self._values.get("end_time")
        assert result is not None, "Required property 'end_time' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def services(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#services MaintenanceWindow#services}.'''
        result = self._values.get("services")
        assert result is not None, "Required property 'services' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def start_time(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#start_time MaintenanceWindow#start_time}.'''
        result = self._values.get("start_time")
        assert result is not None, "Required property 'start_time' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/maintenance_window.html#description MaintenanceWindow#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MaintenanceWindowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagerdutyProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.PagerdutyProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty pagerduty}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        token: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        skip_credentials_validation: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty pagerduty} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty#token PagerdutyProvider#token}.
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty#alias PagerdutyProvider#alias}
        :param skip_credentials_validation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty#skip_credentials_validation PagerdutyProvider#skip_credentials_validation}.
        '''
        config = PagerdutyProviderConfig(
            token=token,
            alias=alias,
            skip_credentials_validation=skip_credentials_validation,
        )

        jsii.create(PagerdutyProvider, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetSkipCredentialsValidation")
    def reset_skip_credentials_validation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipCredentialsValidation", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipCredentialsValidationInput")
    def skip_credentials_validation_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "skipCredentialsValidationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @token.setter
    def token(self, value: builtins.str) -> None:
        jsii.set(self, "token", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipCredentialsValidation")
    def skip_credentials_validation(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "skipCredentialsValidation"))

    @skip_credentials_validation.setter
    def skip_credentials_validation(
        self,
        value: typing.Optional[builtins.bool],
    ) -> None:
        jsii.set(self, "skipCredentialsValidation", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.PagerdutyProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "token": "token",
        "alias": "alias",
        "skip_credentials_validation": "skipCredentialsValidation",
    },
)
class PagerdutyProviderConfig:
    def __init__(
        self,
        *,
        token: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        skip_credentials_validation: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty#token PagerdutyProvider#token}.
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty#alias PagerdutyProvider#alias}
        :param skip_credentials_validation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty#skip_credentials_validation PagerdutyProvider#skip_credentials_validation}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "token": token,
        }
        if alias is not None:
            self._values["alias"] = alias
        if skip_credentials_validation is not None:
            self._values["skip_credentials_validation"] = skip_credentials_validation

    @builtins.property
    def token(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty#token PagerdutyProvider#token}.'''
        result = self._values.get("token")
        assert result is not None, "Required property 'token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty#alias PagerdutyProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_credentials_validation(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty#skip_credentials_validation PagerdutyProvider#skip_credentials_validation}.'''
        result = self._values.get("skip_credentials_validation")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagerdutyProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ResponsePlay(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.ResponsePlay",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html pagerduty_response_play}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        from_: builtins.str,
        name: builtins.str,
        conference_number: typing.Optional[builtins.str] = None,
        conference_url: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        responder: typing.Optional[typing.Sequence["ResponsePlayResponder"]] = None,
        responders_message: typing.Optional[builtins.str] = None,
        runnability: typing.Optional[builtins.str] = None,
        subscriber: typing.Optional[typing.Sequence["ResponsePlaySubscriber"]] = None,
        subscribers_message: typing.Optional[builtins.str] = None,
        team: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html pagerduty_response_play} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#from ResponsePlay#from}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#name ResponsePlay#name}.
        :param conference_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#conference_number ResponsePlay#conference_number}.
        :param conference_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#conference_url ResponsePlay#conference_url}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#description ResponsePlay#description}.
        :param responder: responder block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#responder ResponsePlay#responder}
        :param responders_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#responders_message ResponsePlay#responders_message}.
        :param runnability: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#runnability ResponsePlay#runnability}.
        :param subscriber: subscriber block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#subscriber ResponsePlay#subscriber}
        :param subscribers_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#subscribers_message ResponsePlay#subscribers_message}.
        :param team: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#team ResponsePlay#team}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#type ResponsePlay#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ResponsePlayConfig(
            from_=from_,
            name=name,
            conference_number=conference_number,
            conference_url=conference_url,
            description=description,
            responder=responder,
            responders_message=responders_message,
            runnability=runnability,
            subscriber=subscriber,
            subscribers_message=subscribers_message,
            team=team,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ResponsePlay, self, [scope, id, config])

    @jsii.member(jsii_name="resetConferenceNumber")
    def reset_conference_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConferenceNumber", []))

    @jsii.member(jsii_name="resetConferenceUrl")
    def reset_conference_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConferenceUrl", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetResponder")
    def reset_responder(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponder", []))

    @jsii.member(jsii_name="resetRespondersMessage")
    def reset_responders_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespondersMessage", []))

    @jsii.member(jsii_name="resetRunnability")
    def reset_runnability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunnability", []))

    @jsii.member(jsii_name="resetSubscriber")
    def reset_subscriber(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriber", []))

    @jsii.member(jsii_name="resetSubscribersMessage")
    def reset_subscribers_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscribersMessage", []))

    @jsii.member(jsii_name="resetTeam")
    def reset_team(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeam", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fromInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conferenceNumberInput")
    def conference_number_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "conferenceNumberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conferenceUrlInput")
    def conference_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "conferenceUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responderInput")
    def responder_input(self) -> typing.Optional[typing.List["ResponsePlayResponder"]]:
        return typing.cast(typing.Optional[typing.List["ResponsePlayResponder"]], jsii.get(self, "responderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="respondersMessageInput")
    def responders_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "respondersMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runnabilityInput")
    def runnability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runnabilityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriberInput")
    def subscriber_input(
        self,
    ) -> typing.Optional[typing.List["ResponsePlaySubscriber"]]:
        return typing.cast(typing.Optional[typing.List["ResponsePlaySubscriber"]], jsii.get(self, "subscriberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscribersMessageInput")
    def subscribers_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscribersMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamInput")
    def team_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conferenceNumber")
    def conference_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "conferenceNumber"))

    @conference_number.setter
    def conference_number(self, value: builtins.str) -> None:
        jsii.set(self, "conferenceNumber", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conferenceUrl")
    def conference_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "conferenceUrl"))

    @conference_url.setter
    def conference_url(self, value: builtins.str) -> None:
        jsii.set(self, "conferenceUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        jsii.set(self, "from", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responder")
    def responder(self) -> typing.List["ResponsePlayResponder"]:
        return typing.cast(typing.List["ResponsePlayResponder"], jsii.get(self, "responder"))

    @responder.setter
    def responder(self, value: typing.List["ResponsePlayResponder"]) -> None:
        jsii.set(self, "responder", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="respondersMessage")
    def responders_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "respondersMessage"))

    @responders_message.setter
    def responders_message(self, value: builtins.str) -> None:
        jsii.set(self, "respondersMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runnability")
    def runnability(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runnability"))

    @runnability.setter
    def runnability(self, value: builtins.str) -> None:
        jsii.set(self, "runnability", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriber")
    def subscriber(self) -> typing.List["ResponsePlaySubscriber"]:
        return typing.cast(typing.List["ResponsePlaySubscriber"], jsii.get(self, "subscriber"))

    @subscriber.setter
    def subscriber(self, value: typing.List["ResponsePlaySubscriber"]) -> None:
        jsii.set(self, "subscriber", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscribersMessage")
    def subscribers_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscribersMessage"))

    @subscribers_message.setter
    def subscribers_message(self, value: builtins.str) -> None:
        jsii.set(self, "subscribersMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @team.setter
    def team(self, value: builtins.str) -> None:
        jsii.set(self, "team", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ResponsePlayConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "from_": "from",
        "name": "name",
        "conference_number": "conferenceNumber",
        "conference_url": "conferenceUrl",
        "description": "description",
        "responder": "responder",
        "responders_message": "respondersMessage",
        "runnability": "runnability",
        "subscriber": "subscriber",
        "subscribers_message": "subscribersMessage",
        "team": "team",
        "type": "type",
    },
)
class ResponsePlayConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        from_: builtins.str,
        name: builtins.str,
        conference_number: typing.Optional[builtins.str] = None,
        conference_url: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        responder: typing.Optional[typing.Sequence["ResponsePlayResponder"]] = None,
        responders_message: typing.Optional[builtins.str] = None,
        runnability: typing.Optional[builtins.str] = None,
        subscriber: typing.Optional[typing.Sequence["ResponsePlaySubscriber"]] = None,
        subscribers_message: typing.Optional[builtins.str] = None,
        team: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#from ResponsePlay#from}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#name ResponsePlay#name}.
        :param conference_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#conference_number ResponsePlay#conference_number}.
        :param conference_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#conference_url ResponsePlay#conference_url}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#description ResponsePlay#description}.
        :param responder: responder block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#responder ResponsePlay#responder}
        :param responders_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#responders_message ResponsePlay#responders_message}.
        :param runnability: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#runnability ResponsePlay#runnability}.
        :param subscriber: subscriber block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#subscriber ResponsePlay#subscriber}
        :param subscribers_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#subscribers_message ResponsePlay#subscribers_message}.
        :param team: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#team ResponsePlay#team}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#type ResponsePlay#type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "from_": from_,
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
        if conference_number is not None:
            self._values["conference_number"] = conference_number
        if conference_url is not None:
            self._values["conference_url"] = conference_url
        if description is not None:
            self._values["description"] = description
        if responder is not None:
            self._values["responder"] = responder
        if responders_message is not None:
            self._values["responders_message"] = responders_message
        if runnability is not None:
            self._values["runnability"] = runnability
        if subscriber is not None:
            self._values["subscriber"] = subscriber
        if subscribers_message is not None:
            self._values["subscribers_message"] = subscribers_message
        if team is not None:
            self._values["team"] = team
        if type is not None:
            self._values["type"] = type

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
    def from_(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#from ResponsePlay#from}.'''
        result = self._values.get("from_")
        assert result is not None, "Required property 'from_' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#name ResponsePlay#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def conference_number(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#conference_number ResponsePlay#conference_number}.'''
        result = self._values.get("conference_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def conference_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#conference_url ResponsePlay#conference_url}.'''
        result = self._values.get("conference_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#description ResponsePlay#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def responder(self) -> typing.Optional[typing.List["ResponsePlayResponder"]]:
        '''responder block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#responder ResponsePlay#responder}
        '''
        result = self._values.get("responder")
        return typing.cast(typing.Optional[typing.List["ResponsePlayResponder"]], result)

    @builtins.property
    def responders_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#responders_message ResponsePlay#responders_message}.'''
        result = self._values.get("responders_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runnability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#runnability ResponsePlay#runnability}.'''
        result = self._values.get("runnability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscriber(self) -> typing.Optional[typing.List["ResponsePlaySubscriber"]]:
        '''subscriber block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#subscriber ResponsePlay#subscriber}
        '''
        result = self._values.get("subscriber")
        return typing.cast(typing.Optional[typing.List["ResponsePlaySubscriber"]], result)

    @builtins.property
    def subscribers_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#subscribers_message ResponsePlay#subscribers_message}.'''
        result = self._values.get("subscribers_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def team(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#team ResponsePlay#team}.'''
        result = self._values.get("team")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#type ResponsePlay#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResponsePlayConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ResponsePlayResponder",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "id": "id",
        "name": "name",
        "type": "type",
    },
)
class ResponsePlayResponder:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#description ResponsePlay#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#id ResponsePlay#id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#name ResponsePlay#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#type ResponsePlay#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#description ResponsePlay#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#id ResponsePlay#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#name ResponsePlay#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#type ResponsePlay#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResponsePlayResponder(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ResponsePlaySubscriber",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "type": "type"},
)
class ResponsePlaySubscriber:
    def __init__(
        self,
        *,
        id: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#id ResponsePlay#id}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#type ResponsePlay#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#id ResponsePlay#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/response_play.html#type ResponsePlay#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResponsePlaySubscriber(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Ruleset(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.Ruleset",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html pagerduty_ruleset}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        team: typing.Optional[typing.Sequence["RulesetTeam"]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html pagerduty_ruleset} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html#name Ruleset#name}.
        :param team: team block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html#team Ruleset#team}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RulesetConfig(
            name=name,
            team=team,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Ruleset, self, [scope, id, config])

    @jsii.member(jsii_name="resetTeam")
    def reset_team(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeam", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingKeys")
    def routing_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "routingKeys"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamInput")
    def team_input(self) -> typing.Optional[typing.List["RulesetTeam"]]:
        return typing.cast(typing.Optional[typing.List["RulesetTeam"]], jsii.get(self, "teamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="team")
    def team(self) -> typing.List["RulesetTeam"]:
        return typing.cast(typing.List["RulesetTeam"], jsii.get(self, "team"))

    @team.setter
    def team(self, value: typing.List["RulesetTeam"]) -> None:
        jsii.set(self, "team", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "team": "team",
    },
)
class RulesetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        team: typing.Optional[typing.Sequence["RulesetTeam"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html#name Ruleset#name}.
        :param team: team block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html#team Ruleset#team}
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
        if team is not None:
            self._values["team"] = team

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html#name Ruleset#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def team(self) -> typing.Optional[typing.List["RulesetTeam"]]:
        '''team block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html#team Ruleset#team}
        '''
        result = self._values.get("team")
        return typing.cast(typing.Optional[typing.List["RulesetTeam"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RulesetRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.RulesetRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html pagerduty_ruleset_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ruleset: builtins.str,
        actions: typing.Optional[typing.Sequence["RulesetRuleActions"]] = None,
        conditions: typing.Optional[typing.Sequence["RulesetRuleConditions"]] = None,
        disabled: typing.Optional[builtins.bool] = None,
        position: typing.Optional[jsii.Number] = None,
        time_frame: typing.Optional[typing.Sequence["RulesetRuleTimeFrame"]] = None,
        variable: typing.Optional[typing.Sequence["RulesetRuleVariable"]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html pagerduty_ruleset_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ruleset: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#ruleset RulesetRule#ruleset}.
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#actions RulesetRule#actions}
        :param conditions: conditions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#conditions RulesetRule#conditions}
        :param disabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#disabled RulesetRule#disabled}.
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#position RulesetRule#position}.
        :param time_frame: time_frame block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#time_frame RulesetRule#time_frame}
        :param variable: variable block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#variable RulesetRule#variable}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RulesetRuleConfig(
            ruleset=ruleset,
            actions=actions,
            conditions=conditions,
            disabled=disabled,
            position=position,
            time_frame=time_frame,
            variable=variable,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RulesetRule, self, [scope, id, config])

    @jsii.member(jsii_name="resetActions")
    def reset_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActions", []))

    @jsii.member(jsii_name="resetConditions")
    def reset_conditions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConditions", []))

    @jsii.member(jsii_name="resetDisabled")
    def reset_disabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisabled", []))

    @jsii.member(jsii_name="resetPosition")
    def reset_position(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosition", []))

    @jsii.member(jsii_name="resetTimeFrame")
    def reset_time_frame(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeFrame", []))

    @jsii.member(jsii_name="resetVariable")
    def reset_variable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVariable", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesetInput")
    def ruleset_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rulesetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionsInput")
    def actions_input(self) -> typing.Optional[typing.List["RulesetRuleActions"]]:
        return typing.cast(typing.Optional[typing.List["RulesetRuleActions"]], jsii.get(self, "actionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditionsInput")
    def conditions_input(self) -> typing.Optional[typing.List["RulesetRuleConditions"]]:
        return typing.cast(typing.Optional[typing.List["RulesetRuleConditions"]], jsii.get(self, "conditionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disabledInput")
    def disabled_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "disabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="positionInput")
    def position_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "positionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFrameInput")
    def time_frame_input(self) -> typing.Optional[typing.List["RulesetRuleTimeFrame"]]:
        return typing.cast(typing.Optional[typing.List["RulesetRuleTimeFrame"]], jsii.get(self, "timeFrameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variableInput")
    def variable_input(self) -> typing.Optional[typing.List["RulesetRuleVariable"]]:
        return typing.cast(typing.Optional[typing.List["RulesetRuleVariable"]], jsii.get(self, "variableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List["RulesetRuleActions"]:
        return typing.cast(typing.List["RulesetRuleActions"], jsii.get(self, "actions"))

    @actions.setter
    def actions(self, value: typing.List["RulesetRuleActions"]) -> None:
        jsii.set(self, "actions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditions")
    def conditions(self) -> typing.List["RulesetRuleConditions"]:
        return typing.cast(typing.List["RulesetRuleConditions"], jsii.get(self, "conditions"))

    @conditions.setter
    def conditions(self, value: typing.List["RulesetRuleConditions"]) -> None:
        jsii.set(self, "conditions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disabled")
    def disabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "disabled"))

    @disabled.setter
    def disabled(self, value: builtins.bool) -> None:
        jsii.set(self, "disabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        jsii.set(self, "position", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleset")
    def ruleset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleset"))

    @ruleset.setter
    def ruleset(self, value: builtins.str) -> None:
        jsii.set(self, "ruleset", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFrame")
    def time_frame(self) -> typing.List["RulesetRuleTimeFrame"]:
        return typing.cast(typing.List["RulesetRuleTimeFrame"], jsii.get(self, "timeFrame"))

    @time_frame.setter
    def time_frame(self, value: typing.List["RulesetRuleTimeFrame"]) -> None:
        jsii.set(self, "timeFrame", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variable")
    def variable(self) -> typing.List["RulesetRuleVariable"]:
        return typing.cast(typing.List["RulesetRuleVariable"], jsii.get(self, "variable"))

    @variable.setter
    def variable(self, value: typing.List["RulesetRuleVariable"]) -> None:
        jsii.set(self, "variable", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleActions",
    jsii_struct_bases=[],
    name_mapping={
        "annotate": "annotate",
        "event_action": "eventAction",
        "extractions": "extractions",
        "priority": "priority",
        "route": "route",
        "severity": "severity",
        "suppress": "suppress",
        "suspend": "suspend",
    },
)
class RulesetRuleActions:
    def __init__(
        self,
        *,
        annotate: typing.Optional[typing.Sequence["RulesetRuleActionsAnnotate"]] = None,
        event_action: typing.Optional[typing.Sequence["RulesetRuleActionsEventAction"]] = None,
        extractions: typing.Optional[typing.Sequence["RulesetRuleActionsExtractions"]] = None,
        priority: typing.Optional[typing.Sequence["RulesetRuleActionsPriority"]] = None,
        route: typing.Optional[typing.Sequence["RulesetRuleActionsRoute"]] = None,
        severity: typing.Optional[typing.Sequence["RulesetRuleActionsSeverity"]] = None,
        suppress: typing.Optional[typing.Sequence["RulesetRuleActionsSuppress"]] = None,
        suspend: typing.Optional[typing.Sequence["RulesetRuleActionsSuspend"]] = None,
    ) -> None:
        '''
        :param annotate: annotate block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#annotate RulesetRule#annotate}
        :param event_action: event_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#event_action RulesetRule#event_action}
        :param extractions: extractions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#extractions RulesetRule#extractions}
        :param priority: priority block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#priority RulesetRule#priority}
        :param route: route block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#route RulesetRule#route}
        :param severity: severity block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#severity RulesetRule#severity}
        :param suppress: suppress block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#suppress RulesetRule#suppress}
        :param suspend: suspend block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#suspend RulesetRule#suspend}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if annotate is not None:
            self._values["annotate"] = annotate
        if event_action is not None:
            self._values["event_action"] = event_action
        if extractions is not None:
            self._values["extractions"] = extractions
        if priority is not None:
            self._values["priority"] = priority
        if route is not None:
            self._values["route"] = route
        if severity is not None:
            self._values["severity"] = severity
        if suppress is not None:
            self._values["suppress"] = suppress
        if suspend is not None:
            self._values["suspend"] = suspend

    @builtins.property
    def annotate(self) -> typing.Optional[typing.List["RulesetRuleActionsAnnotate"]]:
        '''annotate block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#annotate RulesetRule#annotate}
        '''
        result = self._values.get("annotate")
        return typing.cast(typing.Optional[typing.List["RulesetRuleActionsAnnotate"]], result)

    @builtins.property
    def event_action(
        self,
    ) -> typing.Optional[typing.List["RulesetRuleActionsEventAction"]]:
        '''event_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#event_action RulesetRule#event_action}
        '''
        result = self._values.get("event_action")
        return typing.cast(typing.Optional[typing.List["RulesetRuleActionsEventAction"]], result)

    @builtins.property
    def extractions(
        self,
    ) -> typing.Optional[typing.List["RulesetRuleActionsExtractions"]]:
        '''extractions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#extractions RulesetRule#extractions}
        '''
        result = self._values.get("extractions")
        return typing.cast(typing.Optional[typing.List["RulesetRuleActionsExtractions"]], result)

    @builtins.property
    def priority(self) -> typing.Optional[typing.List["RulesetRuleActionsPriority"]]:
        '''priority block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#priority RulesetRule#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[typing.List["RulesetRuleActionsPriority"]], result)

    @builtins.property
    def route(self) -> typing.Optional[typing.List["RulesetRuleActionsRoute"]]:
        '''route block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#route RulesetRule#route}
        '''
        result = self._values.get("route")
        return typing.cast(typing.Optional[typing.List["RulesetRuleActionsRoute"]], result)

    @builtins.property
    def severity(self) -> typing.Optional[typing.List["RulesetRuleActionsSeverity"]]:
        '''severity block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#severity RulesetRule#severity}
        '''
        result = self._values.get("severity")
        return typing.cast(typing.Optional[typing.List["RulesetRuleActionsSeverity"]], result)

    @builtins.property
    def suppress(self) -> typing.Optional[typing.List["RulesetRuleActionsSuppress"]]:
        '''suppress block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#suppress RulesetRule#suppress}
        '''
        result = self._values.get("suppress")
        return typing.cast(typing.Optional[typing.List["RulesetRuleActionsSuppress"]], result)

    @builtins.property
    def suspend(self) -> typing.Optional[typing.List["RulesetRuleActionsSuspend"]]:
        '''suspend block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#suspend RulesetRule#suspend}
        '''
        result = self._values.get("suspend")
        return typing.cast(typing.Optional[typing.List["RulesetRuleActionsSuspend"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleActionsAnnotate",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class RulesetRuleActionsAnnotate:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleActionsAnnotate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleActionsEventAction",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class RulesetRuleActionsEventAction:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleActionsEventAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleActionsExtractions",
    jsii_struct_bases=[],
    name_mapping={
        "regex": "regex",
        "source": "source",
        "target": "target",
        "template": "template",
    },
)
class RulesetRuleActionsExtractions:
    def __init__(
        self,
        *,
        regex: typing.Optional[builtins.str] = None,
        source: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#regex RulesetRule#regex}.
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#source RulesetRule#source}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#target RulesetRule#target}.
        :param template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#template RulesetRule#template}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if regex is not None:
            self._values["regex"] = regex
        if source is not None:
            self._values["source"] = source
        if target is not None:
            self._values["target"] = target
        if template is not None:
            self._values["template"] = template

    @builtins.property
    def regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#regex RulesetRule#regex}.'''
        result = self._values.get("regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#source RulesetRule#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#target RulesetRule#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#template RulesetRule#template}.'''
        result = self._values.get("template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleActionsExtractions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleActionsPriority",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class RulesetRuleActionsPriority:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleActionsPriority(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleActionsRoute",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class RulesetRuleActionsRoute:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleActionsRoute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleActionsSeverity",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class RulesetRuleActionsSeverity:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleActionsSeverity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleActionsSuppress",
    jsii_struct_bases=[],
    name_mapping={
        "threshold_time_amount": "thresholdTimeAmount",
        "threshold_time_unit": "thresholdTimeUnit",
        "threshold_value": "thresholdValue",
        "value": "value",
    },
)
class RulesetRuleActionsSuppress:
    def __init__(
        self,
        *,
        threshold_time_amount: typing.Optional[jsii.Number] = None,
        threshold_time_unit: typing.Optional[builtins.str] = None,
        threshold_value: typing.Optional[jsii.Number] = None,
        value: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param threshold_time_amount: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#threshold_time_amount RulesetRule#threshold_time_amount}.
        :param threshold_time_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#threshold_time_unit RulesetRule#threshold_time_unit}.
        :param threshold_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#threshold_value RulesetRule#threshold_value}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if threshold_time_amount is not None:
            self._values["threshold_time_amount"] = threshold_time_amount
        if threshold_time_unit is not None:
            self._values["threshold_time_unit"] = threshold_time_unit
        if threshold_value is not None:
            self._values["threshold_value"] = threshold_value
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def threshold_time_amount(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#threshold_time_amount RulesetRule#threshold_time_amount}.'''
        result = self._values.get("threshold_time_amount")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def threshold_time_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#threshold_time_unit RulesetRule#threshold_time_unit}.'''
        result = self._values.get("threshold_time_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold_value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#threshold_value RulesetRule#threshold_value}.'''
        result = self._values.get("threshold_value")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleActionsSuppress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleActionsSuspend",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class RulesetRuleActionsSuspend:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleActionsSuspend(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleConditions",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "subconditions": "subconditions"},
)
class RulesetRuleConditions:
    def __init__(
        self,
        *,
        operator: typing.Optional[builtins.str] = None,
        subconditions: typing.Optional[typing.Sequence["RulesetRuleConditionsSubconditions"]] = None,
    ) -> None:
        '''
        :param operator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#operator RulesetRule#operator}.
        :param subconditions: subconditions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#subconditions RulesetRule#subconditions}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if operator is not None:
            self._values["operator"] = operator
        if subconditions is not None:
            self._values["subconditions"] = subconditions

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#operator RulesetRule#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subconditions(
        self,
    ) -> typing.Optional[typing.List["RulesetRuleConditionsSubconditions"]]:
        '''subconditions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#subconditions RulesetRule#subconditions}
        '''
        result = self._values.get("subconditions")
        return typing.cast(typing.Optional[typing.List["RulesetRuleConditionsSubconditions"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleConditions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleConditionsSubconditions",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "parameter": "parameter"},
)
class RulesetRuleConditionsSubconditions:
    def __init__(
        self,
        *,
        operator: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["RulesetRuleConditionsSubconditionsParameter"]] = None,
    ) -> None:
        '''
        :param operator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#operator RulesetRule#operator}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#parameter RulesetRule#parameter}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if operator is not None:
            self._values["operator"] = operator
        if parameter is not None:
            self._values["parameter"] = parameter

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#operator RulesetRule#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.List["RulesetRuleConditionsSubconditionsParameter"]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#parameter RulesetRule#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.List["RulesetRuleConditionsSubconditionsParameter"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleConditionsSubconditions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleConditionsSubconditionsParameter",
    jsii_struct_bases=[],
    name_mapping={"path": "path", "value": "value"},
)
class RulesetRuleConditionsSubconditionsParameter:
    def __init__(
        self,
        *,
        path: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#path RulesetRule#path}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if path is not None:
            self._values["path"] = path
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#path RulesetRule#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleConditionsSubconditionsParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "ruleset": "ruleset",
        "actions": "actions",
        "conditions": "conditions",
        "disabled": "disabled",
        "position": "position",
        "time_frame": "timeFrame",
        "variable": "variable",
    },
)
class RulesetRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        ruleset: builtins.str,
        actions: typing.Optional[typing.Sequence[RulesetRuleActions]] = None,
        conditions: typing.Optional[typing.Sequence[RulesetRuleConditions]] = None,
        disabled: typing.Optional[builtins.bool] = None,
        position: typing.Optional[jsii.Number] = None,
        time_frame: typing.Optional[typing.Sequence["RulesetRuleTimeFrame"]] = None,
        variable: typing.Optional[typing.Sequence["RulesetRuleVariable"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param ruleset: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#ruleset RulesetRule#ruleset}.
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#actions RulesetRule#actions}
        :param conditions: conditions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#conditions RulesetRule#conditions}
        :param disabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#disabled RulesetRule#disabled}.
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#position RulesetRule#position}.
        :param time_frame: time_frame block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#time_frame RulesetRule#time_frame}
        :param variable: variable block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#variable RulesetRule#variable}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "ruleset": ruleset,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if actions is not None:
            self._values["actions"] = actions
        if conditions is not None:
            self._values["conditions"] = conditions
        if disabled is not None:
            self._values["disabled"] = disabled
        if position is not None:
            self._values["position"] = position
        if time_frame is not None:
            self._values["time_frame"] = time_frame
        if variable is not None:
            self._values["variable"] = variable

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
    def ruleset(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#ruleset RulesetRule#ruleset}.'''
        result = self._values.get("ruleset")
        assert result is not None, "Required property 'ruleset' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[RulesetRuleActions]]:
        '''actions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#actions RulesetRule#actions}
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[RulesetRuleActions]], result)

    @builtins.property
    def conditions(self) -> typing.Optional[typing.List[RulesetRuleConditions]]:
        '''conditions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#conditions RulesetRule#conditions}
        '''
        result = self._values.get("conditions")
        return typing.cast(typing.Optional[typing.List[RulesetRuleConditions]], result)

    @builtins.property
    def disabled(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#disabled RulesetRule#disabled}.'''
        result = self._values.get("disabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#position RulesetRule#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def time_frame(self) -> typing.Optional[typing.List["RulesetRuleTimeFrame"]]:
        '''time_frame block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#time_frame RulesetRule#time_frame}
        '''
        result = self._values.get("time_frame")
        return typing.cast(typing.Optional[typing.List["RulesetRuleTimeFrame"]], result)

    @builtins.property
    def variable(self) -> typing.Optional[typing.List["RulesetRuleVariable"]]:
        '''variable block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#variable RulesetRule#variable}
        '''
        result = self._values.get("variable")
        return typing.cast(typing.Optional[typing.List["RulesetRuleVariable"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleTimeFrame",
    jsii_struct_bases=[],
    name_mapping={
        "active_between": "activeBetween",
        "scheduled_weekly": "scheduledWeekly",
    },
)
class RulesetRuleTimeFrame:
    def __init__(
        self,
        *,
        active_between: typing.Optional[typing.Sequence["RulesetRuleTimeFrameActiveBetween"]] = None,
        scheduled_weekly: typing.Optional[typing.Sequence["RulesetRuleTimeFrameScheduledWeekly"]] = None,
    ) -> None:
        '''
        :param active_between: active_between block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#active_between RulesetRule#active_between}
        :param scheduled_weekly: scheduled_weekly block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#scheduled_weekly RulesetRule#scheduled_weekly}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if active_between is not None:
            self._values["active_between"] = active_between
        if scheduled_weekly is not None:
            self._values["scheduled_weekly"] = scheduled_weekly

    @builtins.property
    def active_between(
        self,
    ) -> typing.Optional[typing.List["RulesetRuleTimeFrameActiveBetween"]]:
        '''active_between block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#active_between RulesetRule#active_between}
        '''
        result = self._values.get("active_between")
        return typing.cast(typing.Optional[typing.List["RulesetRuleTimeFrameActiveBetween"]], result)

    @builtins.property
    def scheduled_weekly(
        self,
    ) -> typing.Optional[typing.List["RulesetRuleTimeFrameScheduledWeekly"]]:
        '''scheduled_weekly block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#scheduled_weekly RulesetRule#scheduled_weekly}
        '''
        result = self._values.get("scheduled_weekly")
        return typing.cast(typing.Optional[typing.List["RulesetRuleTimeFrameScheduledWeekly"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleTimeFrame(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleTimeFrameActiveBetween",
    jsii_struct_bases=[],
    name_mapping={"end_time": "endTime", "start_time": "startTime"},
)
class RulesetRuleTimeFrameActiveBetween:
    def __init__(
        self,
        *,
        end_time: typing.Optional[jsii.Number] = None,
        start_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param end_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#end_time RulesetRule#end_time}.
        :param start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#start_time RulesetRule#start_time}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if end_time is not None:
            self._values["end_time"] = end_time
        if start_time is not None:
            self._values["start_time"] = start_time

    @builtins.property
    def end_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#end_time RulesetRule#end_time}.'''
        result = self._values.get("end_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#start_time RulesetRule#start_time}.'''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleTimeFrameActiveBetween(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleTimeFrameScheduledWeekly",
    jsii_struct_bases=[],
    name_mapping={
        "duration": "duration",
        "start_time": "startTime",
        "timezone": "timezone",
        "weekdays": "weekdays",
    },
)
class RulesetRuleTimeFrameScheduledWeekly:
    def __init__(
        self,
        *,
        duration: typing.Optional[jsii.Number] = None,
        start_time: typing.Optional[jsii.Number] = None,
        timezone: typing.Optional[builtins.str] = None,
        weekdays: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#duration RulesetRule#duration}.
        :param start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#start_time RulesetRule#start_time}.
        :param timezone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#timezone RulesetRule#timezone}.
        :param weekdays: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#weekdays RulesetRule#weekdays}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if duration is not None:
            self._values["duration"] = duration
        if start_time is not None:
            self._values["start_time"] = start_time
        if timezone is not None:
            self._values["timezone"] = timezone
        if weekdays is not None:
            self._values["weekdays"] = weekdays

    @builtins.property
    def duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#duration RulesetRule#duration}.'''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#start_time RulesetRule#start_time}.'''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#timezone RulesetRule#timezone}.'''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def weekdays(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#weekdays RulesetRule#weekdays}.'''
        result = self._values.get("weekdays")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleTimeFrameScheduledWeekly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleVariable",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "parameters": "parameters", "type": "type"},
)
class RulesetRuleVariable:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["RulesetRuleVariableParameters"]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#name RulesetRule#name}.
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#parameters RulesetRule#parameters}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#type RulesetRule#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if parameters is not None:
            self._values["parameters"] = parameters
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#name RulesetRule#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.List["RulesetRuleVariableParameters"]]:
        '''parameters block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#parameters RulesetRule#parameters}
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.List["RulesetRuleVariableParameters"]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#type RulesetRule#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleVariable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetRuleVariableParameters",
    jsii_struct_bases=[],
    name_mapping={"path": "path", "value": "value"},
)
class RulesetRuleVariableParameters:
    def __init__(
        self,
        *,
        path: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#path RulesetRule#path}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if path is not None:
            self._values["path"] = path
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#path RulesetRule#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset_rule.html#value RulesetRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetRuleVariableParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.RulesetTeam",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class RulesetTeam:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html#id Ruleset#id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/ruleset.html#id Ruleset#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RulesetTeam(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Schedule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.Schedule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html pagerduty_schedule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        layer: typing.Sequence["ScheduleLayer"],
        time_zone: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        overflow: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html pagerduty_schedule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param layer: layer block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#layer Schedule#layer}
        :param time_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#time_zone Schedule#time_zone}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#description Schedule#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#name Schedule#name}.
        :param overflow: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#overflow Schedule#overflow}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ScheduleConfig(
            layer=layer,
            time_zone=time_zone,
            description=description,
            name=name,
            overflow=overflow,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Schedule, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOverflow")
    def reset_overflow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverflow", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerInput")
    def layer_input(self) -> typing.List["ScheduleLayer"]:
        return typing.cast(typing.List["ScheduleLayer"], jsii.get(self, "layerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeZoneInput")
    def time_zone_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overflowInput")
    def overflow_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "overflowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layer")
    def layer(self) -> typing.List["ScheduleLayer"]:
        return typing.cast(typing.List["ScheduleLayer"], jsii.get(self, "layer"))

    @layer.setter
    def layer(self, value: typing.List["ScheduleLayer"]) -> None:
        jsii.set(self, "layer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overflow")
    def overflow(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "overflow"))

    @overflow.setter
    def overflow(self, value: builtins.bool) -> None:
        jsii.set(self, "overflow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZone"))

    @time_zone.setter
    def time_zone(self, value: builtins.str) -> None:
        jsii.set(self, "timeZone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ScheduleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "layer": "layer",
        "time_zone": "timeZone",
        "description": "description",
        "name": "name",
        "overflow": "overflow",
    },
)
class ScheduleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        layer: typing.Sequence["ScheduleLayer"],
        time_zone: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        overflow: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param layer: layer block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#layer Schedule#layer}
        :param time_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#time_zone Schedule#time_zone}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#description Schedule#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#name Schedule#name}.
        :param overflow: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#overflow Schedule#overflow}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "layer": layer,
            "time_zone": time_zone,
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
        if name is not None:
            self._values["name"] = name
        if overflow is not None:
            self._values["overflow"] = overflow

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
    def layer(self) -> typing.List["ScheduleLayer"]:
        '''layer block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#layer Schedule#layer}
        '''
        result = self._values.get("layer")
        assert result is not None, "Required property 'layer' is missing"
        return typing.cast(typing.List["ScheduleLayer"], result)

    @builtins.property
    def time_zone(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#time_zone Schedule#time_zone}.'''
        result = self._values.get("time_zone")
        assert result is not None, "Required property 'time_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#description Schedule#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#name Schedule#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def overflow(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#overflow Schedule#overflow}.'''
        result = self._values.get("overflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScheduleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ScheduleLayer",
    jsii_struct_bases=[],
    name_mapping={
        "rotation_turn_length_seconds": "rotationTurnLengthSeconds",
        "rotation_virtual_start": "rotationVirtualStart",
        "start": "start",
        "users": "users",
        "end": "end",
        "name": "name",
        "restriction": "restriction",
    },
)
class ScheduleLayer:
    def __init__(
        self,
        *,
        rotation_turn_length_seconds: jsii.Number,
        rotation_virtual_start: builtins.str,
        start: builtins.str,
        users: typing.Sequence[builtins.str],
        end: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        restriction: typing.Optional[typing.Sequence["ScheduleLayerRestriction"]] = None,
    ) -> None:
        '''
        :param rotation_turn_length_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#rotation_turn_length_seconds Schedule#rotation_turn_length_seconds}.
        :param rotation_virtual_start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#rotation_virtual_start Schedule#rotation_virtual_start}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#start Schedule#start}.
        :param users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#users Schedule#users}.
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#end Schedule#end}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#name Schedule#name}.
        :param restriction: restriction block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#restriction Schedule#restriction}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "rotation_turn_length_seconds": rotation_turn_length_seconds,
            "rotation_virtual_start": rotation_virtual_start,
            "start": start,
            "users": users,
        }
        if end is not None:
            self._values["end"] = end
        if name is not None:
            self._values["name"] = name
        if restriction is not None:
            self._values["restriction"] = restriction

    @builtins.property
    def rotation_turn_length_seconds(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#rotation_turn_length_seconds Schedule#rotation_turn_length_seconds}.'''
        result = self._values.get("rotation_turn_length_seconds")
        assert result is not None, "Required property 'rotation_turn_length_seconds' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def rotation_virtual_start(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#rotation_virtual_start Schedule#rotation_virtual_start}.'''
        result = self._values.get("rotation_virtual_start")
        assert result is not None, "Required property 'rotation_virtual_start' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def start(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#start Schedule#start}.'''
        result = self._values.get("start")
        assert result is not None, "Required property 'start' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def users(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#users Schedule#users}.'''
        result = self._values.get("users")
        assert result is not None, "Required property 'users' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#end Schedule#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#name Schedule#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restriction(self) -> typing.Optional[typing.List["ScheduleLayerRestriction"]]:
        '''restriction block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#restriction Schedule#restriction}
        '''
        result = self._values.get("restriction")
        return typing.cast(typing.Optional[typing.List["ScheduleLayerRestriction"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScheduleLayer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ScheduleLayerRestriction",
    jsii_struct_bases=[],
    name_mapping={
        "duration_seconds": "durationSeconds",
        "start_time_of_day": "startTimeOfDay",
        "type": "type",
        "start_day_of_week": "startDayOfWeek",
    },
)
class ScheduleLayerRestriction:
    def __init__(
        self,
        *,
        duration_seconds: jsii.Number,
        start_time_of_day: builtins.str,
        type: builtins.str,
        start_day_of_week: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param duration_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#duration_seconds Schedule#duration_seconds}.
        :param start_time_of_day: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#start_time_of_day Schedule#start_time_of_day}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#type Schedule#type}.
        :param start_day_of_week: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#start_day_of_week Schedule#start_day_of_week}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "duration_seconds": duration_seconds,
            "start_time_of_day": start_time_of_day,
            "type": type,
        }
        if start_day_of_week is not None:
            self._values["start_day_of_week"] = start_day_of_week

    @builtins.property
    def duration_seconds(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#duration_seconds Schedule#duration_seconds}.'''
        result = self._values.get("duration_seconds")
        assert result is not None, "Required property 'duration_seconds' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def start_time_of_day(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#start_time_of_day Schedule#start_time_of_day}.'''
        result = self._values.get("start_time_of_day")
        assert result is not None, "Required property 'start_time_of_day' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#type Schedule#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def start_day_of_week(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/schedule.html#start_day_of_week Schedule#start_day_of_week}.'''
        result = self._values.get("start_day_of_week")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScheduleLayerRestriction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Service(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.Service",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html pagerduty_service}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        escalation_policy: builtins.str,
        name: builtins.str,
        acknowledgement_timeout: typing.Optional[builtins.str] = None,
        alert_creation: typing.Optional[builtins.str] = None,
        alert_grouping: typing.Optional[builtins.str] = None,
        alert_grouping_parameters: typing.Optional[typing.Sequence["ServiceAlertGroupingParameters"]] = None,
        alert_grouping_timeout: typing.Optional[jsii.Number] = None,
        auto_resolve_timeout: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        incident_urgency_rule: typing.Optional[typing.Sequence["ServiceIncidentUrgencyRule"]] = None,
        scheduled_actions: typing.Optional[typing.Sequence["ServiceScheduledActions"]] = None,
        support_hours: typing.Optional[typing.Sequence["ServiceSupportHours"]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html pagerduty_service} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param escalation_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#escalation_policy Service#escalation_policy}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#name Service#name}.
        :param acknowledgement_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#acknowledgement_timeout Service#acknowledgement_timeout}.
        :param alert_creation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_creation Service#alert_creation}.
        :param alert_grouping: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_grouping Service#alert_grouping}.
        :param alert_grouping_parameters: alert_grouping_parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_grouping_parameters Service#alert_grouping_parameters}
        :param alert_grouping_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_grouping_timeout Service#alert_grouping_timeout}.
        :param auto_resolve_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#auto_resolve_timeout Service#auto_resolve_timeout}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#description Service#description}.
        :param incident_urgency_rule: incident_urgency_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#incident_urgency_rule Service#incident_urgency_rule}
        :param scheduled_actions: scheduled_actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#scheduled_actions Service#scheduled_actions}
        :param support_hours: support_hours block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#support_hours Service#support_hours}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceConfig(
            escalation_policy=escalation_policy,
            name=name,
            acknowledgement_timeout=acknowledgement_timeout,
            alert_creation=alert_creation,
            alert_grouping=alert_grouping,
            alert_grouping_parameters=alert_grouping_parameters,
            alert_grouping_timeout=alert_grouping_timeout,
            auto_resolve_timeout=auto_resolve_timeout,
            description=description,
            incident_urgency_rule=incident_urgency_rule,
            scheduled_actions=scheduled_actions,
            support_hours=support_hours,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Service, self, [scope, id, config])

    @jsii.member(jsii_name="resetAcknowledgementTimeout")
    def reset_acknowledgement_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAcknowledgementTimeout", []))

    @jsii.member(jsii_name="resetAlertCreation")
    def reset_alert_creation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertCreation", []))

    @jsii.member(jsii_name="resetAlertGrouping")
    def reset_alert_grouping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertGrouping", []))

    @jsii.member(jsii_name="resetAlertGroupingParameters")
    def reset_alert_grouping_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertGroupingParameters", []))

    @jsii.member(jsii_name="resetAlertGroupingTimeout")
    def reset_alert_grouping_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertGroupingTimeout", []))

    @jsii.member(jsii_name="resetAutoResolveTimeout")
    def reset_auto_resolve_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoResolveTimeout", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetIncidentUrgencyRule")
    def reset_incident_urgency_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncidentUrgencyRule", []))

    @jsii.member(jsii_name="resetScheduledActions")
    def reset_scheduled_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheduledActions", []))

    @jsii.member(jsii_name="resetSupportHours")
    def reset_support_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportHours", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="escalationPolicyInput")
    def escalation_policy_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "escalationPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastIncidentTimestamp")
    def last_incident_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastIncidentTimestamp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acknowledgementTimeoutInput")
    def acknowledgement_timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "acknowledgementTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alertCreationInput")
    def alert_creation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alertCreationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alertGroupingInput")
    def alert_grouping_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alertGroupingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alertGroupingParametersInput")
    def alert_grouping_parameters_input(
        self,
    ) -> typing.Optional[typing.List["ServiceAlertGroupingParameters"]]:
        return typing.cast(typing.Optional[typing.List["ServiceAlertGroupingParameters"]], jsii.get(self, "alertGroupingParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alertGroupingTimeoutInput")
    def alert_grouping_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "alertGroupingTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoResolveTimeoutInput")
    def auto_resolve_timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoResolveTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="incidentUrgencyRuleInput")
    def incident_urgency_rule_input(
        self,
    ) -> typing.Optional[typing.List["ServiceIncidentUrgencyRule"]]:
        return typing.cast(typing.Optional[typing.List["ServiceIncidentUrgencyRule"]], jsii.get(self, "incidentUrgencyRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduledActionsInput")
    def scheduled_actions_input(
        self,
    ) -> typing.Optional[typing.List["ServiceScheduledActions"]]:
        return typing.cast(typing.Optional[typing.List["ServiceScheduledActions"]], jsii.get(self, "scheduledActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportHoursInput")
    def support_hours_input(
        self,
    ) -> typing.Optional[typing.List["ServiceSupportHours"]]:
        return typing.cast(typing.Optional[typing.List["ServiceSupportHours"]], jsii.get(self, "supportHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acknowledgementTimeout")
    def acknowledgement_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acknowledgementTimeout"))

    @acknowledgement_timeout.setter
    def acknowledgement_timeout(self, value: builtins.str) -> None:
        jsii.set(self, "acknowledgementTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alertCreation")
    def alert_creation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alertCreation"))

    @alert_creation.setter
    def alert_creation(self, value: builtins.str) -> None:
        jsii.set(self, "alertCreation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alertGrouping")
    def alert_grouping(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alertGrouping"))

    @alert_grouping.setter
    def alert_grouping(self, value: builtins.str) -> None:
        jsii.set(self, "alertGrouping", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alertGroupingParameters")
    def alert_grouping_parameters(
        self,
    ) -> typing.List["ServiceAlertGroupingParameters"]:
        return typing.cast(typing.List["ServiceAlertGroupingParameters"], jsii.get(self, "alertGroupingParameters"))

    @alert_grouping_parameters.setter
    def alert_grouping_parameters(
        self,
        value: typing.List["ServiceAlertGroupingParameters"],
    ) -> None:
        jsii.set(self, "alertGroupingParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alertGroupingTimeout")
    def alert_grouping_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "alertGroupingTimeout"))

    @alert_grouping_timeout.setter
    def alert_grouping_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "alertGroupingTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoResolveTimeout")
    def auto_resolve_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoResolveTimeout"))

    @auto_resolve_timeout.setter
    def auto_resolve_timeout(self, value: builtins.str) -> None:
        jsii.set(self, "autoResolveTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="escalationPolicy")
    def escalation_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "escalationPolicy"))

    @escalation_policy.setter
    def escalation_policy(self, value: builtins.str) -> None:
        jsii.set(self, "escalationPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="incidentUrgencyRule")
    def incident_urgency_rule(self) -> typing.List["ServiceIncidentUrgencyRule"]:
        return typing.cast(typing.List["ServiceIncidentUrgencyRule"], jsii.get(self, "incidentUrgencyRule"))

    @incident_urgency_rule.setter
    def incident_urgency_rule(
        self,
        value: typing.List["ServiceIncidentUrgencyRule"],
    ) -> None:
        jsii.set(self, "incidentUrgencyRule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduledActions")
    def scheduled_actions(self) -> typing.List["ServiceScheduledActions"]:
        return typing.cast(typing.List["ServiceScheduledActions"], jsii.get(self, "scheduledActions"))

    @scheduled_actions.setter
    def scheduled_actions(self, value: typing.List["ServiceScheduledActions"]) -> None:
        jsii.set(self, "scheduledActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportHours")
    def support_hours(self) -> typing.List["ServiceSupportHours"]:
        return typing.cast(typing.List["ServiceSupportHours"], jsii.get(self, "supportHours"))

    @support_hours.setter
    def support_hours(self, value: typing.List["ServiceSupportHours"]) -> None:
        jsii.set(self, "supportHours", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceAlertGroupingParameters",
    jsii_struct_bases=[],
    name_mapping={"config": "config", "type": "type"},
)
class ServiceAlertGroupingParameters:
    def __init__(
        self,
        *,
        config: typing.Optional[typing.Sequence["ServiceAlertGroupingParametersConfig"]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#config Service#config}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if config is not None:
            self._values["config"] = config
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def config(
        self,
    ) -> typing.Optional[typing.List["ServiceAlertGroupingParametersConfig"]]:
        '''config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#config Service#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional[typing.List["ServiceAlertGroupingParametersConfig"]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceAlertGroupingParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceAlertGroupingParametersConfig",
    jsii_struct_bases=[],
    name_mapping={"aggregate": "aggregate", "fields": "fields", "timeout": "timeout"},
)
class ServiceAlertGroupingParametersConfig:
    def __init__(
        self,
        *,
        aggregate: typing.Optional[builtins.str] = None,
        fields: typing.Optional[typing.Sequence[builtins.str]] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param aggregate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#aggregate Service#aggregate}.
        :param fields: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#fields Service#fields}.
        :param timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#timeout Service#timeout}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if aggregate is not None:
            self._values["aggregate"] = aggregate
        if fields is not None:
            self._values["fields"] = fields
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def aggregate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#aggregate Service#aggregate}.'''
        result = self._values.get("aggregate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fields(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#fields Service#fields}.'''
        result = self._values.get("fields")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#timeout Service#timeout}.'''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceAlertGroupingParametersConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "escalation_policy": "escalationPolicy",
        "name": "name",
        "acknowledgement_timeout": "acknowledgementTimeout",
        "alert_creation": "alertCreation",
        "alert_grouping": "alertGrouping",
        "alert_grouping_parameters": "alertGroupingParameters",
        "alert_grouping_timeout": "alertGroupingTimeout",
        "auto_resolve_timeout": "autoResolveTimeout",
        "description": "description",
        "incident_urgency_rule": "incidentUrgencyRule",
        "scheduled_actions": "scheduledActions",
        "support_hours": "supportHours",
    },
)
class ServiceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        escalation_policy: builtins.str,
        name: builtins.str,
        acknowledgement_timeout: typing.Optional[builtins.str] = None,
        alert_creation: typing.Optional[builtins.str] = None,
        alert_grouping: typing.Optional[builtins.str] = None,
        alert_grouping_parameters: typing.Optional[typing.Sequence[ServiceAlertGroupingParameters]] = None,
        alert_grouping_timeout: typing.Optional[jsii.Number] = None,
        auto_resolve_timeout: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        incident_urgency_rule: typing.Optional[typing.Sequence["ServiceIncidentUrgencyRule"]] = None,
        scheduled_actions: typing.Optional[typing.Sequence["ServiceScheduledActions"]] = None,
        support_hours: typing.Optional[typing.Sequence["ServiceSupportHours"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param escalation_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#escalation_policy Service#escalation_policy}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#name Service#name}.
        :param acknowledgement_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#acknowledgement_timeout Service#acknowledgement_timeout}.
        :param alert_creation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_creation Service#alert_creation}.
        :param alert_grouping: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_grouping Service#alert_grouping}.
        :param alert_grouping_parameters: alert_grouping_parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_grouping_parameters Service#alert_grouping_parameters}
        :param alert_grouping_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_grouping_timeout Service#alert_grouping_timeout}.
        :param auto_resolve_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#auto_resolve_timeout Service#auto_resolve_timeout}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#description Service#description}.
        :param incident_urgency_rule: incident_urgency_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#incident_urgency_rule Service#incident_urgency_rule}
        :param scheduled_actions: scheduled_actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#scheduled_actions Service#scheduled_actions}
        :param support_hours: support_hours block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#support_hours Service#support_hours}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "escalation_policy": escalation_policy,
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
        if acknowledgement_timeout is not None:
            self._values["acknowledgement_timeout"] = acknowledgement_timeout
        if alert_creation is not None:
            self._values["alert_creation"] = alert_creation
        if alert_grouping is not None:
            self._values["alert_grouping"] = alert_grouping
        if alert_grouping_parameters is not None:
            self._values["alert_grouping_parameters"] = alert_grouping_parameters
        if alert_grouping_timeout is not None:
            self._values["alert_grouping_timeout"] = alert_grouping_timeout
        if auto_resolve_timeout is not None:
            self._values["auto_resolve_timeout"] = auto_resolve_timeout
        if description is not None:
            self._values["description"] = description
        if incident_urgency_rule is not None:
            self._values["incident_urgency_rule"] = incident_urgency_rule
        if scheduled_actions is not None:
            self._values["scheduled_actions"] = scheduled_actions
        if support_hours is not None:
            self._values["support_hours"] = support_hours

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
    def escalation_policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#escalation_policy Service#escalation_policy}.'''
        result = self._values.get("escalation_policy")
        assert result is not None, "Required property 'escalation_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#name Service#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def acknowledgement_timeout(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#acknowledgement_timeout Service#acknowledgement_timeout}.'''
        result = self._values.get("acknowledgement_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alert_creation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_creation Service#alert_creation}.'''
        result = self._values.get("alert_creation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alert_grouping(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_grouping Service#alert_grouping}.'''
        result = self._values.get("alert_grouping")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alert_grouping_parameters(
        self,
    ) -> typing.Optional[typing.List[ServiceAlertGroupingParameters]]:
        '''alert_grouping_parameters block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_grouping_parameters Service#alert_grouping_parameters}
        '''
        result = self._values.get("alert_grouping_parameters")
        return typing.cast(typing.Optional[typing.List[ServiceAlertGroupingParameters]], result)

    @builtins.property
    def alert_grouping_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#alert_grouping_timeout Service#alert_grouping_timeout}.'''
        result = self._values.get("alert_grouping_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def auto_resolve_timeout(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#auto_resolve_timeout Service#auto_resolve_timeout}.'''
        result = self._values.get("auto_resolve_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#description Service#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def incident_urgency_rule(
        self,
    ) -> typing.Optional[typing.List["ServiceIncidentUrgencyRule"]]:
        '''incident_urgency_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#incident_urgency_rule Service#incident_urgency_rule}
        '''
        result = self._values.get("incident_urgency_rule")
        return typing.cast(typing.Optional[typing.List["ServiceIncidentUrgencyRule"]], result)

    @builtins.property
    def scheduled_actions(
        self,
    ) -> typing.Optional[typing.List["ServiceScheduledActions"]]:
        '''scheduled_actions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#scheduled_actions Service#scheduled_actions}
        '''
        result = self._values.get("scheduled_actions")
        return typing.cast(typing.Optional[typing.List["ServiceScheduledActions"]], result)

    @builtins.property
    def support_hours(self) -> typing.Optional[typing.List["ServiceSupportHours"]]:
        '''support_hours block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#support_hours Service#support_hours}
        '''
        result = self._values.get("support_hours")
        return typing.cast(typing.Optional[typing.List["ServiceSupportHours"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceDependency(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.ServiceDependency",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html pagerduty_service_dependency}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        dependency: typing.Sequence["ServiceDependencyDependency"],
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html pagerduty_service_dependency} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param dependency: dependency block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#dependency ServiceDependency#dependency}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceDependencyConfig(
            dependency=dependency,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ServiceDependency, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dependencyInput")
    def dependency_input(self) -> typing.List["ServiceDependencyDependency"]:
        return typing.cast(typing.List["ServiceDependencyDependency"], jsii.get(self, "dependencyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dependency")
    def dependency(self) -> typing.List["ServiceDependencyDependency"]:
        return typing.cast(typing.List["ServiceDependencyDependency"], jsii.get(self, "dependency"))

    @dependency.setter
    def dependency(self, value: typing.List["ServiceDependencyDependency"]) -> None:
        jsii.set(self, "dependency", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceDependencyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "dependency": "dependency",
    },
)
class ServiceDependencyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        dependency: typing.Sequence["ServiceDependencyDependency"],
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param dependency: dependency block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#dependency ServiceDependency#dependency}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "dependency": dependency,
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
    def dependency(self) -> typing.List["ServiceDependencyDependency"]:
        '''dependency block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#dependency ServiceDependency#dependency}
        '''
        result = self._values.get("dependency")
        assert result is not None, "Required property 'dependency' is missing"
        return typing.cast(typing.List["ServiceDependencyDependency"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDependencyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceDependencyDependency",
    jsii_struct_bases=[],
    name_mapping={
        "dependent_service": "dependentService",
        "supporting_service": "supportingService",
        "type": "type",
    },
)
class ServiceDependencyDependency:
    def __init__(
        self,
        *,
        dependent_service: typing.Sequence["ServiceDependencyDependencyDependentService"],
        supporting_service: typing.Sequence["ServiceDependencyDependencySupportingService"],
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dependent_service: dependent_service block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#dependent_service ServiceDependency#dependent_service}
        :param supporting_service: supporting_service block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#supporting_service ServiceDependency#supporting_service}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#type ServiceDependency#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dependent_service": dependent_service,
            "supporting_service": supporting_service,
        }
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def dependent_service(
        self,
    ) -> typing.List["ServiceDependencyDependencyDependentService"]:
        '''dependent_service block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#dependent_service ServiceDependency#dependent_service}
        '''
        result = self._values.get("dependent_service")
        assert result is not None, "Required property 'dependent_service' is missing"
        return typing.cast(typing.List["ServiceDependencyDependencyDependentService"], result)

    @builtins.property
    def supporting_service(
        self,
    ) -> typing.List["ServiceDependencyDependencySupportingService"]:
        '''supporting_service block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#supporting_service ServiceDependency#supporting_service}
        '''
        result = self._values.get("supporting_service")
        assert result is not None, "Required property 'supporting_service' is missing"
        return typing.cast(typing.List["ServiceDependencyDependencySupportingService"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#type ServiceDependency#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDependencyDependency(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceDependencyDependencyDependentService",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "type": "type"},
)
class ServiceDependencyDependencyDependentService:
    def __init__(self, *, id: builtins.str, type: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#id ServiceDependency#id}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#type ServiceDependency#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "type": type,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#id ServiceDependency#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#type ServiceDependency#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDependencyDependencyDependentService(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceDependencyDependencySupportingService",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "type": "type"},
)
class ServiceDependencyDependencySupportingService:
    def __init__(self, *, id: builtins.str, type: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#id ServiceDependency#id}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#type ServiceDependency#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "type": type,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#id ServiceDependency#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_dependency.html#type ServiceDependency#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDependencyDependencySupportingService(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceEventRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html pagerduty_service_event_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        service: builtins.str,
        actions: typing.Optional[typing.Sequence["ServiceEventRuleActions"]] = None,
        conditions: typing.Optional[typing.Sequence["ServiceEventRuleConditions"]] = None,
        disabled: typing.Optional[builtins.bool] = None,
        position: typing.Optional[jsii.Number] = None,
        time_frame: typing.Optional[typing.Sequence["ServiceEventRuleTimeFrame"]] = None,
        variable: typing.Optional[typing.Sequence["ServiceEventRuleVariable"]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html pagerduty_service_event_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param service: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#service ServiceEventRule#service}.
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#actions ServiceEventRule#actions}
        :param conditions: conditions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#conditions ServiceEventRule#conditions}
        :param disabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#disabled ServiceEventRule#disabled}.
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#position ServiceEventRule#position}.
        :param time_frame: time_frame block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#time_frame ServiceEventRule#time_frame}
        :param variable: variable block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#variable ServiceEventRule#variable}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceEventRuleConfig(
            service=service,
            actions=actions,
            conditions=conditions,
            disabled=disabled,
            position=position,
            time_frame=time_frame,
            variable=variable,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ServiceEventRule, self, [scope, id, config])

    @jsii.member(jsii_name="resetActions")
    def reset_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActions", []))

    @jsii.member(jsii_name="resetConditions")
    def reset_conditions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConditions", []))

    @jsii.member(jsii_name="resetDisabled")
    def reset_disabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisabled", []))

    @jsii.member(jsii_name="resetPosition")
    def reset_position(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosition", []))

    @jsii.member(jsii_name="resetTimeFrame")
    def reset_time_frame(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeFrame", []))

    @jsii.member(jsii_name="resetVariable")
    def reset_variable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVariable", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionsInput")
    def actions_input(self) -> typing.Optional[typing.List["ServiceEventRuleActions"]]:
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleActions"]], jsii.get(self, "actionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditionsInput")
    def conditions_input(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleConditions"]]:
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleConditions"]], jsii.get(self, "conditionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disabledInput")
    def disabled_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "disabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="positionInput")
    def position_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "positionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFrameInput")
    def time_frame_input(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleTimeFrame"]]:
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleTimeFrame"]], jsii.get(self, "timeFrameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variableInput")
    def variable_input(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleVariable"]]:
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleVariable"]], jsii.get(self, "variableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List["ServiceEventRuleActions"]:
        return typing.cast(typing.List["ServiceEventRuleActions"], jsii.get(self, "actions"))

    @actions.setter
    def actions(self, value: typing.List["ServiceEventRuleActions"]) -> None:
        jsii.set(self, "actions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditions")
    def conditions(self) -> typing.List["ServiceEventRuleConditions"]:
        return typing.cast(typing.List["ServiceEventRuleConditions"], jsii.get(self, "conditions"))

    @conditions.setter
    def conditions(self, value: typing.List["ServiceEventRuleConditions"]) -> None:
        jsii.set(self, "conditions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disabled")
    def disabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "disabled"))

    @disabled.setter
    def disabled(self, value: builtins.bool) -> None:
        jsii.set(self, "disabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        jsii.set(self, "position", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        jsii.set(self, "service", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeFrame")
    def time_frame(self) -> typing.List["ServiceEventRuleTimeFrame"]:
        return typing.cast(typing.List["ServiceEventRuleTimeFrame"], jsii.get(self, "timeFrame"))

    @time_frame.setter
    def time_frame(self, value: typing.List["ServiceEventRuleTimeFrame"]) -> None:
        jsii.set(self, "timeFrame", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variable")
    def variable(self) -> typing.List["ServiceEventRuleVariable"]:
        return typing.cast(typing.List["ServiceEventRuleVariable"], jsii.get(self, "variable"))

    @variable.setter
    def variable(self, value: typing.List["ServiceEventRuleVariable"]) -> None:
        jsii.set(self, "variable", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleActions",
    jsii_struct_bases=[],
    name_mapping={
        "annotate": "annotate",
        "event_action": "eventAction",
        "extractions": "extractions",
        "priority": "priority",
        "severity": "severity",
        "suppress": "suppress",
        "suspend": "suspend",
    },
)
class ServiceEventRuleActions:
    def __init__(
        self,
        *,
        annotate: typing.Optional[typing.Sequence["ServiceEventRuleActionsAnnotate"]] = None,
        event_action: typing.Optional[typing.Sequence["ServiceEventRuleActionsEventAction"]] = None,
        extractions: typing.Optional[typing.Sequence["ServiceEventRuleActionsExtractions"]] = None,
        priority: typing.Optional[typing.Sequence["ServiceEventRuleActionsPriority"]] = None,
        severity: typing.Optional[typing.Sequence["ServiceEventRuleActionsSeverity"]] = None,
        suppress: typing.Optional[typing.Sequence["ServiceEventRuleActionsSuppress"]] = None,
        suspend: typing.Optional[typing.Sequence["ServiceEventRuleActionsSuspend"]] = None,
    ) -> None:
        '''
        :param annotate: annotate block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#annotate ServiceEventRule#annotate}
        :param event_action: event_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#event_action ServiceEventRule#event_action}
        :param extractions: extractions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#extractions ServiceEventRule#extractions}
        :param priority: priority block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#priority ServiceEventRule#priority}
        :param severity: severity block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#severity ServiceEventRule#severity}
        :param suppress: suppress block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#suppress ServiceEventRule#suppress}
        :param suspend: suspend block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#suspend ServiceEventRule#suspend}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if annotate is not None:
            self._values["annotate"] = annotate
        if event_action is not None:
            self._values["event_action"] = event_action
        if extractions is not None:
            self._values["extractions"] = extractions
        if priority is not None:
            self._values["priority"] = priority
        if severity is not None:
            self._values["severity"] = severity
        if suppress is not None:
            self._values["suppress"] = suppress
        if suspend is not None:
            self._values["suspend"] = suspend

    @builtins.property
    def annotate(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleActionsAnnotate"]]:
        '''annotate block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#annotate ServiceEventRule#annotate}
        '''
        result = self._values.get("annotate")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleActionsAnnotate"]], result)

    @builtins.property
    def event_action(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleActionsEventAction"]]:
        '''event_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#event_action ServiceEventRule#event_action}
        '''
        result = self._values.get("event_action")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleActionsEventAction"]], result)

    @builtins.property
    def extractions(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleActionsExtractions"]]:
        '''extractions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#extractions ServiceEventRule#extractions}
        '''
        result = self._values.get("extractions")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleActionsExtractions"]], result)

    @builtins.property
    def priority(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleActionsPriority"]]:
        '''priority block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#priority ServiceEventRule#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleActionsPriority"]], result)

    @builtins.property
    def severity(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleActionsSeverity"]]:
        '''severity block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#severity ServiceEventRule#severity}
        '''
        result = self._values.get("severity")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleActionsSeverity"]], result)

    @builtins.property
    def suppress(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleActionsSuppress"]]:
        '''suppress block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#suppress ServiceEventRule#suppress}
        '''
        result = self._values.get("suppress")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleActionsSuppress"]], result)

    @builtins.property
    def suspend(self) -> typing.Optional[typing.List["ServiceEventRuleActionsSuspend"]]:
        '''suspend block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#suspend ServiceEventRule#suspend}
        '''
        result = self._values.get("suspend")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleActionsSuspend"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleActionsAnnotate",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class ServiceEventRuleActionsAnnotate:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleActionsAnnotate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleActionsEventAction",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class ServiceEventRuleActionsEventAction:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleActionsEventAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleActionsExtractions",
    jsii_struct_bases=[],
    name_mapping={
        "regex": "regex",
        "source": "source",
        "target": "target",
        "template": "template",
    },
)
class ServiceEventRuleActionsExtractions:
    def __init__(
        self,
        *,
        regex: typing.Optional[builtins.str] = None,
        source: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#regex ServiceEventRule#regex}.
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#source ServiceEventRule#source}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#target ServiceEventRule#target}.
        :param template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#template ServiceEventRule#template}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if regex is not None:
            self._values["regex"] = regex
        if source is not None:
            self._values["source"] = source
        if target is not None:
            self._values["target"] = target
        if template is not None:
            self._values["template"] = template

    @builtins.property
    def regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#regex ServiceEventRule#regex}.'''
        result = self._values.get("regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#source ServiceEventRule#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#target ServiceEventRule#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#template ServiceEventRule#template}.'''
        result = self._values.get("template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleActionsExtractions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleActionsPriority",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class ServiceEventRuleActionsPriority:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleActionsPriority(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleActionsSeverity",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class ServiceEventRuleActionsSeverity:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleActionsSeverity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleActionsSuppress",
    jsii_struct_bases=[],
    name_mapping={
        "threshold_time_amount": "thresholdTimeAmount",
        "threshold_time_unit": "thresholdTimeUnit",
        "threshold_value": "thresholdValue",
        "value": "value",
    },
)
class ServiceEventRuleActionsSuppress:
    def __init__(
        self,
        *,
        threshold_time_amount: typing.Optional[jsii.Number] = None,
        threshold_time_unit: typing.Optional[builtins.str] = None,
        threshold_value: typing.Optional[jsii.Number] = None,
        value: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param threshold_time_amount: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#threshold_time_amount ServiceEventRule#threshold_time_amount}.
        :param threshold_time_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#threshold_time_unit ServiceEventRule#threshold_time_unit}.
        :param threshold_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#threshold_value ServiceEventRule#threshold_value}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if threshold_time_amount is not None:
            self._values["threshold_time_amount"] = threshold_time_amount
        if threshold_time_unit is not None:
            self._values["threshold_time_unit"] = threshold_time_unit
        if threshold_value is not None:
            self._values["threshold_value"] = threshold_value
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def threshold_time_amount(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#threshold_time_amount ServiceEventRule#threshold_time_amount}.'''
        result = self._values.get("threshold_time_amount")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def threshold_time_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#threshold_time_unit ServiceEventRule#threshold_time_unit}.'''
        result = self._values.get("threshold_time_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold_value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#threshold_value ServiceEventRule#threshold_value}.'''
        result = self._values.get("threshold_value")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleActionsSuppress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleActionsSuspend",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class ServiceEventRuleActionsSuspend:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleActionsSuspend(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleConditions",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "subconditions": "subconditions"},
)
class ServiceEventRuleConditions:
    def __init__(
        self,
        *,
        operator: typing.Optional[builtins.str] = None,
        subconditions: typing.Optional[typing.Sequence["ServiceEventRuleConditionsSubconditions"]] = None,
    ) -> None:
        '''
        :param operator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#operator ServiceEventRule#operator}.
        :param subconditions: subconditions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#subconditions ServiceEventRule#subconditions}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if operator is not None:
            self._values["operator"] = operator
        if subconditions is not None:
            self._values["subconditions"] = subconditions

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#operator ServiceEventRule#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subconditions(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleConditionsSubconditions"]]:
        '''subconditions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#subconditions ServiceEventRule#subconditions}
        '''
        result = self._values.get("subconditions")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleConditionsSubconditions"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleConditions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleConditionsSubconditions",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "parameter": "parameter"},
)
class ServiceEventRuleConditionsSubconditions:
    def __init__(
        self,
        *,
        operator: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["ServiceEventRuleConditionsSubconditionsParameter"]] = None,
    ) -> None:
        '''
        :param operator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#operator ServiceEventRule#operator}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#parameter ServiceEventRule#parameter}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if operator is not None:
            self._values["operator"] = operator
        if parameter is not None:
            self._values["parameter"] = parameter

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#operator ServiceEventRule#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleConditionsSubconditionsParameter"]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#parameter ServiceEventRule#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleConditionsSubconditionsParameter"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleConditionsSubconditions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleConditionsSubconditionsParameter",
    jsii_struct_bases=[],
    name_mapping={"path": "path", "value": "value"},
)
class ServiceEventRuleConditionsSubconditionsParameter:
    def __init__(
        self,
        *,
        path: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#path ServiceEventRule#path}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if path is not None:
            self._values["path"] = path
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#path ServiceEventRule#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleConditionsSubconditionsParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "service": "service",
        "actions": "actions",
        "conditions": "conditions",
        "disabled": "disabled",
        "position": "position",
        "time_frame": "timeFrame",
        "variable": "variable",
    },
)
class ServiceEventRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        service: builtins.str,
        actions: typing.Optional[typing.Sequence[ServiceEventRuleActions]] = None,
        conditions: typing.Optional[typing.Sequence[ServiceEventRuleConditions]] = None,
        disabled: typing.Optional[builtins.bool] = None,
        position: typing.Optional[jsii.Number] = None,
        time_frame: typing.Optional[typing.Sequence["ServiceEventRuleTimeFrame"]] = None,
        variable: typing.Optional[typing.Sequence["ServiceEventRuleVariable"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param service: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#service ServiceEventRule#service}.
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#actions ServiceEventRule#actions}
        :param conditions: conditions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#conditions ServiceEventRule#conditions}
        :param disabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#disabled ServiceEventRule#disabled}.
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#position ServiceEventRule#position}.
        :param time_frame: time_frame block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#time_frame ServiceEventRule#time_frame}
        :param variable: variable block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#variable ServiceEventRule#variable}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "service": service,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if actions is not None:
            self._values["actions"] = actions
        if conditions is not None:
            self._values["conditions"] = conditions
        if disabled is not None:
            self._values["disabled"] = disabled
        if position is not None:
            self._values["position"] = position
        if time_frame is not None:
            self._values["time_frame"] = time_frame
        if variable is not None:
            self._values["variable"] = variable

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
    def service(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#service ServiceEventRule#service}.'''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[ServiceEventRuleActions]]:
        '''actions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#actions ServiceEventRule#actions}
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[ServiceEventRuleActions]], result)

    @builtins.property
    def conditions(self) -> typing.Optional[typing.List[ServiceEventRuleConditions]]:
        '''conditions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#conditions ServiceEventRule#conditions}
        '''
        result = self._values.get("conditions")
        return typing.cast(typing.Optional[typing.List[ServiceEventRuleConditions]], result)

    @builtins.property
    def disabled(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#disabled ServiceEventRule#disabled}.'''
        result = self._values.get("disabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#position ServiceEventRule#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def time_frame(self) -> typing.Optional[typing.List["ServiceEventRuleTimeFrame"]]:
        '''time_frame block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#time_frame ServiceEventRule#time_frame}
        '''
        result = self._values.get("time_frame")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleTimeFrame"]], result)

    @builtins.property
    def variable(self) -> typing.Optional[typing.List["ServiceEventRuleVariable"]]:
        '''variable block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#variable ServiceEventRule#variable}
        '''
        result = self._values.get("variable")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleVariable"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleTimeFrame",
    jsii_struct_bases=[],
    name_mapping={
        "active_between": "activeBetween",
        "scheduled_weekly": "scheduledWeekly",
    },
)
class ServiceEventRuleTimeFrame:
    def __init__(
        self,
        *,
        active_between: typing.Optional[typing.Sequence["ServiceEventRuleTimeFrameActiveBetween"]] = None,
        scheduled_weekly: typing.Optional[typing.Sequence["ServiceEventRuleTimeFrameScheduledWeekly"]] = None,
    ) -> None:
        '''
        :param active_between: active_between block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#active_between ServiceEventRule#active_between}
        :param scheduled_weekly: scheduled_weekly block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#scheduled_weekly ServiceEventRule#scheduled_weekly}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if active_between is not None:
            self._values["active_between"] = active_between
        if scheduled_weekly is not None:
            self._values["scheduled_weekly"] = scheduled_weekly

    @builtins.property
    def active_between(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleTimeFrameActiveBetween"]]:
        '''active_between block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#active_between ServiceEventRule#active_between}
        '''
        result = self._values.get("active_between")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleTimeFrameActiveBetween"]], result)

    @builtins.property
    def scheduled_weekly(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleTimeFrameScheduledWeekly"]]:
        '''scheduled_weekly block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#scheduled_weekly ServiceEventRule#scheduled_weekly}
        '''
        result = self._values.get("scheduled_weekly")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleTimeFrameScheduledWeekly"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleTimeFrame(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleTimeFrameActiveBetween",
    jsii_struct_bases=[],
    name_mapping={"end_time": "endTime", "start_time": "startTime"},
)
class ServiceEventRuleTimeFrameActiveBetween:
    def __init__(
        self,
        *,
        end_time: typing.Optional[jsii.Number] = None,
        start_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param end_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#end_time ServiceEventRule#end_time}.
        :param start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#start_time ServiceEventRule#start_time}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if end_time is not None:
            self._values["end_time"] = end_time
        if start_time is not None:
            self._values["start_time"] = start_time

    @builtins.property
    def end_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#end_time ServiceEventRule#end_time}.'''
        result = self._values.get("end_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#start_time ServiceEventRule#start_time}.'''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleTimeFrameActiveBetween(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleTimeFrameScheduledWeekly",
    jsii_struct_bases=[],
    name_mapping={
        "duration": "duration",
        "start_time": "startTime",
        "timezone": "timezone",
        "weekdays": "weekdays",
    },
)
class ServiceEventRuleTimeFrameScheduledWeekly:
    def __init__(
        self,
        *,
        duration: typing.Optional[jsii.Number] = None,
        start_time: typing.Optional[jsii.Number] = None,
        timezone: typing.Optional[builtins.str] = None,
        weekdays: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#duration ServiceEventRule#duration}.
        :param start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#start_time ServiceEventRule#start_time}.
        :param timezone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#timezone ServiceEventRule#timezone}.
        :param weekdays: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#weekdays ServiceEventRule#weekdays}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if duration is not None:
            self._values["duration"] = duration
        if start_time is not None:
            self._values["start_time"] = start_time
        if timezone is not None:
            self._values["timezone"] = timezone
        if weekdays is not None:
            self._values["weekdays"] = weekdays

    @builtins.property
    def duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#duration ServiceEventRule#duration}.'''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#start_time ServiceEventRule#start_time}.'''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#timezone ServiceEventRule#timezone}.'''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def weekdays(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#weekdays ServiceEventRule#weekdays}.'''
        result = self._values.get("weekdays")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleTimeFrameScheduledWeekly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleVariable",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "parameters": "parameters", "type": "type"},
)
class ServiceEventRuleVariable:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["ServiceEventRuleVariableParameters"]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#name ServiceEventRule#name}.
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#parameters ServiceEventRule#parameters}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#type ServiceEventRule#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if parameters is not None:
            self._values["parameters"] = parameters
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#name ServiceEventRule#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.List["ServiceEventRuleVariableParameters"]]:
        '''parameters block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#parameters ServiceEventRule#parameters}
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.List["ServiceEventRuleVariableParameters"]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#type ServiceEventRule#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleVariable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceEventRuleVariableParameters",
    jsii_struct_bases=[],
    name_mapping={"path": "path", "value": "value"},
)
class ServiceEventRuleVariableParameters:
    def __init__(
        self,
        *,
        path: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#path ServiceEventRule#path}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if path is not None:
            self._values["path"] = path
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#path ServiceEventRule#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_event_rule.html#value ServiceEventRule#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEventRuleVariableParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceIncidentUrgencyRule",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "during_support_hours": "duringSupportHours",
        "outside_support_hours": "outsideSupportHours",
        "urgency": "urgency",
    },
)
class ServiceIncidentUrgencyRule:
    def __init__(
        self,
        *,
        type: builtins.str,
        during_support_hours: typing.Optional[typing.Sequence["ServiceIncidentUrgencyRuleDuringSupportHours"]] = None,
        outside_support_hours: typing.Optional[typing.Sequence["ServiceIncidentUrgencyRuleOutsideSupportHours"]] = None,
        urgency: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.
        :param during_support_hours: during_support_hours block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#during_support_hours Service#during_support_hours}
        :param outside_support_hours: outside_support_hours block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#outside_support_hours Service#outside_support_hours}
        :param urgency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#urgency Service#urgency}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if during_support_hours is not None:
            self._values["during_support_hours"] = during_support_hours
        if outside_support_hours is not None:
            self._values["outside_support_hours"] = outside_support_hours
        if urgency is not None:
            self._values["urgency"] = urgency

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def during_support_hours(
        self,
    ) -> typing.Optional[typing.List["ServiceIncidentUrgencyRuleDuringSupportHours"]]:
        '''during_support_hours block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#during_support_hours Service#during_support_hours}
        '''
        result = self._values.get("during_support_hours")
        return typing.cast(typing.Optional[typing.List["ServiceIncidentUrgencyRuleDuringSupportHours"]], result)

    @builtins.property
    def outside_support_hours(
        self,
    ) -> typing.Optional[typing.List["ServiceIncidentUrgencyRuleOutsideSupportHours"]]:
        '''outside_support_hours block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#outside_support_hours Service#outside_support_hours}
        '''
        result = self._values.get("outside_support_hours")
        return typing.cast(typing.Optional[typing.List["ServiceIncidentUrgencyRuleOutsideSupportHours"]], result)

    @builtins.property
    def urgency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#urgency Service#urgency}.'''
        result = self._values.get("urgency")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceIncidentUrgencyRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceIncidentUrgencyRuleDuringSupportHours",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "urgency": "urgency"},
)
class ServiceIncidentUrgencyRuleDuringSupportHours:
    def __init__(
        self,
        *,
        type: typing.Optional[builtins.str] = None,
        urgency: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.
        :param urgency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#urgency Service#urgency}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if type is not None:
            self._values["type"] = type
        if urgency is not None:
            self._values["urgency"] = urgency

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def urgency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#urgency Service#urgency}.'''
        result = self._values.get("urgency")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceIncidentUrgencyRuleDuringSupportHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceIncidentUrgencyRuleOutsideSupportHours",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "urgency": "urgency"},
)
class ServiceIncidentUrgencyRuleOutsideSupportHours:
    def __init__(
        self,
        *,
        type: typing.Optional[builtins.str] = None,
        urgency: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.
        :param urgency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#urgency Service#urgency}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if type is not None:
            self._values["type"] = type
        if urgency is not None:
            self._values["urgency"] = urgency

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def urgency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#urgency Service#urgency}.'''
        result = self._values.get("urgency")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceIncidentUrgencyRuleOutsideSupportHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceIntegration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.ServiceIntegration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html pagerduty_service_integration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        service: builtins.str,
        integration_email: typing.Optional[builtins.str] = None,
        integration_key: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        vendor: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html pagerduty_service_integration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param service: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#service ServiceIntegration#service}.
        :param integration_email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#integration_email ServiceIntegration#integration_email}.
        :param integration_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#integration_key ServiceIntegration#integration_key}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#name ServiceIntegration#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#type ServiceIntegration#type}.
        :param vendor: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#vendor ServiceIntegration#vendor}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceIntegrationConfig(
            service=service,
            integration_email=integration_email,
            integration_key=integration_key,
            name=name,
            type=type,
            vendor=vendor,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(ServiceIntegration, self, [scope, id, config])

    @jsii.member(jsii_name="resetIntegrationEmail")
    def reset_integration_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationEmail", []))

    @jsii.member(jsii_name="resetIntegrationKey")
    def reset_integration_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationKey", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetVendor")
    def reset_vendor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVendor", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationEmailInput")
    def integration_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationEmailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationKeyInput")
    def integration_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vendorInput")
    def vendor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vendorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationEmail")
    def integration_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationEmail"))

    @integration_email.setter
    def integration_email(self, value: builtins.str) -> None:
        jsii.set(self, "integrationEmail", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationKey")
    def integration_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationKey"))

    @integration_key.setter
    def integration_key(self, value: builtins.str) -> None:
        jsii.set(self, "integrationKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        jsii.set(self, "service", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vendor")
    def vendor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vendor"))

    @vendor.setter
    def vendor(self, value: builtins.str) -> None:
        jsii.set(self, "vendor", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceIntegrationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "service": "service",
        "integration_email": "integrationEmail",
        "integration_key": "integrationKey",
        "name": "name",
        "type": "type",
        "vendor": "vendor",
    },
)
class ServiceIntegrationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        service: builtins.str,
        integration_email: typing.Optional[builtins.str] = None,
        integration_key: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        vendor: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param service: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#service ServiceIntegration#service}.
        :param integration_email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#integration_email ServiceIntegration#integration_email}.
        :param integration_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#integration_key ServiceIntegration#integration_key}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#name ServiceIntegration#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#type ServiceIntegration#type}.
        :param vendor: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#vendor ServiceIntegration#vendor}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "service": service,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if integration_email is not None:
            self._values["integration_email"] = integration_email
        if integration_key is not None:
            self._values["integration_key"] = integration_key
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type
        if vendor is not None:
            self._values["vendor"] = vendor

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
    def service(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#service ServiceIntegration#service}.'''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def integration_email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#integration_email ServiceIntegration#integration_email}.'''
        result = self._values.get("integration_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#integration_key ServiceIntegration#integration_key}.'''
        result = self._values.get("integration_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#name ServiceIntegration#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#type ServiceIntegration#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vendor(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service_integration.html#vendor ServiceIntegration#vendor}.'''
        result = self._values.get("vendor")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceIntegrationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceScheduledActions",
    jsii_struct_bases=[],
    name_mapping={"at": "at", "to_urgency": "toUrgency", "type": "type"},
)
class ServiceScheduledActions:
    def __init__(
        self,
        *,
        at: typing.Optional[typing.Sequence["ServiceScheduledActionsAt"]] = None,
        to_urgency: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param at: at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#at Service#at}
        :param to_urgency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#to_urgency Service#to_urgency}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if at is not None:
            self._values["at"] = at
        if to_urgency is not None:
            self._values["to_urgency"] = to_urgency
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def at(self) -> typing.Optional[typing.List["ServiceScheduledActionsAt"]]:
        '''at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#at Service#at}
        '''
        result = self._values.get("at")
        return typing.cast(typing.Optional[typing.List["ServiceScheduledActionsAt"]], result)

    @builtins.property
    def to_urgency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#to_urgency Service#to_urgency}.'''
        result = self._values.get("to_urgency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceScheduledActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceScheduledActionsAt",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type"},
)
class ServiceScheduledActionsAt:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#name Service#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#name Service#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceScheduledActionsAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.ServiceSupportHours",
    jsii_struct_bases=[],
    name_mapping={
        "days_of_week": "daysOfWeek",
        "end_time": "endTime",
        "start_time": "startTime",
        "time_zone": "timeZone",
        "type": "type",
    },
)
class ServiceSupportHours:
    def __init__(
        self,
        *,
        days_of_week: typing.Optional[typing.Sequence[jsii.Number]] = None,
        end_time: typing.Optional[builtins.str] = None,
        start_time: typing.Optional[builtins.str] = None,
        time_zone: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param days_of_week: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#days_of_week Service#days_of_week}.
        :param end_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#end_time Service#end_time}.
        :param start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#start_time Service#start_time}.
        :param time_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#time_zone Service#time_zone}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if days_of_week is not None:
            self._values["days_of_week"] = days_of_week
        if end_time is not None:
            self._values["end_time"] = end_time
        if start_time is not None:
            self._values["start_time"] = start_time
        if time_zone is not None:
            self._values["time_zone"] = time_zone
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def days_of_week(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#days_of_week Service#days_of_week}.'''
        result = self._values.get("days_of_week")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def end_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#end_time Service#end_time}.'''
        result = self._values.get("end_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#start_time Service#start_time}.'''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#time_zone Service#time_zone}.'''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/service.html#type Service#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceSupportHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Team(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.Team",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html pagerduty_team}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        parent: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html pagerduty_team} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html#name Team#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html#description Team#description}.
        :param parent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html#parent Team#parent}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TeamConfig(
            name=name,
            description=description,
            parent=parent,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Team, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetParent")
    def reset_parent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParent", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentInput")
    def parent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentInput"))

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
    @jsii.member(jsii_name="parent")
    def parent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parent"))

    @parent.setter
    def parent(self, value: builtins.str) -> None:
        jsii.set(self, "parent", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.TeamConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "description": "description",
        "parent": "parent",
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
        description: typing.Optional[builtins.str] = None,
        parent: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html#name Team#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html#description Team#description}.
        :param parent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html#parent Team#parent}.
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
        if description is not None:
            self._values["description"] = description
        if parent is not None:
            self._values["parent"] = parent

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html#name Team#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html#description Team#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team.html#parent Team#parent}.'''
        result = self._values.get("parent")
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
    jsii_type="@cdktf/provider-pagerduty.TeamMembership",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html pagerduty_team_membership}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        team_id: builtins.str,
        user_id: builtins.str,
        role: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html pagerduty_team_membership} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param team_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html#team_id TeamMembership#team_id}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html#user_id TeamMembership#user_id}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html#role TeamMembership#role}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TeamMembershipConfig(
            team_id=team_id,
            user_id=user_id,
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamIdInput")
    def team_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userIdInput"))

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
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        jsii.set(self, "userId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.TeamMembershipConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "team_id": "teamId",
        "user_id": "userId",
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
        user_id: builtins.str,
        role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param team_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html#team_id TeamMembership#team_id}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html#user_id TeamMembership#user_id}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html#role TeamMembership#role}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "team_id": team_id,
            "user_id": user_id,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html#team_id TeamMembership#team_id}.'''
        result = self._values.get("team_id")
        assert result is not None, "Required property 'team_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html#user_id TeamMembership#user_id}.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/team_membership.html#role TeamMembership#role}.'''
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


class User(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.User",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html pagerduty_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        email: builtins.str,
        name: builtins.str,
        color: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        job_title: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
        teams: typing.Optional[typing.Sequence[builtins.str]] = None,
        time_zone: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html pagerduty_user} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#email User#email}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#name User#name}.
        :param color: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#color User#color}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#description User#description}.
        :param job_title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#job_title User#job_title}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#role User#role}.
        :param teams: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#teams User#teams}.
        :param time_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#time_zone User#time_zone}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = UserConfig(
            email=email,
            name=name,
            color=color,
            description=description,
            job_title=job_title,
            role=role,
            teams=teams,
            time_zone=time_zone,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(User, self, [scope, id, config])

    @jsii.member(jsii_name="resetColor")
    def reset_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetColor", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetJobTitle")
    def reset_job_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJobTitle", []))

    @jsii.member(jsii_name="resetRole")
    def reset_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRole", []))

    @jsii.member(jsii_name="resetTeams")
    def reset_teams(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeams", []))

    @jsii.member(jsii_name="resetTimeZone")
    def reset_time_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeZone", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="avatarUrl")
    def avatar_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "avatarUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlUrl")
    def html_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invitationSent")
    def invitation_sent(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "invitationSent"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="colorInput")
    def color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "colorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobTitleInput")
    def job_title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jobTitleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teamsInput")
    def teams_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "teamsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeZoneInput")
    def time_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeZoneInput"))

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
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        jsii.set(self, "email", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobTitle")
    def job_title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobTitle"))

    @job_title.setter
    def job_title(self, value: builtins.str) -> None:
        jsii.set(self, "jobTitle", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teams")
    def teams(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "teams"))

    @teams.setter
    def teams(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "teams", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZone"))

    @time_zone.setter
    def time_zone(self, value: builtins.str) -> None:
        jsii.set(self, "timeZone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.UserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "email": "email",
        "name": "name",
        "color": "color",
        "description": "description",
        "job_title": "jobTitle",
        "role": "role",
        "teams": "teams",
        "time_zone": "timeZone",
    },
)
class UserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        email: builtins.str,
        name: builtins.str,
        color: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        job_title: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
        teams: typing.Optional[typing.Sequence[builtins.str]] = None,
        time_zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#email User#email}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#name User#name}.
        :param color: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#color User#color}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#description User#description}.
        :param job_title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#job_title User#job_title}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#role User#role}.
        :param teams: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#teams User#teams}.
        :param time_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#time_zone User#time_zone}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
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
        if color is not None:
            self._values["color"] = color
        if description is not None:
            self._values["description"] = description
        if job_title is not None:
            self._values["job_title"] = job_title
        if role is not None:
            self._values["role"] = role
        if teams is not None:
            self._values["teams"] = teams
        if time_zone is not None:
            self._values["time_zone"] = time_zone

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
    def email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#email User#email}.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#name User#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#color User#color}.'''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#description User#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_title(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#job_title User#job_title}.'''
        result = self._values.get("job_title")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#role User#role}.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def teams(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#teams User#teams}.'''
        result = self._values.get("teams")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user.html#time_zone User#time_zone}.'''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UserContactMethod(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.UserContactMethod",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html pagerduty_user_contact_method}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        address: builtins.str,
        label: builtins.str,
        type: builtins.str,
        user_id: builtins.str,
        country_code: typing.Optional[jsii.Number] = None,
        send_short_email: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html pagerduty_user_contact_method} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#address UserContactMethod#address}.
        :param label: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#label UserContactMethod#label}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#type UserContactMethod#type}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#user_id UserContactMethod#user_id}.
        :param country_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#country_code UserContactMethod#country_code}.
        :param send_short_email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#send_short_email UserContactMethod#send_short_email}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = UserContactMethodConfig(
            address=address,
            label=label,
            type=type,
            user_id=user_id,
            country_code=country_code,
            send_short_email=send_short_email,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(UserContactMethod, self, [scope, id, config])

    @jsii.member(jsii_name="resetCountryCode")
    def reset_country_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountryCode", []))

    @jsii.member(jsii_name="resetSendShortEmail")
    def reset_send_short_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSendShortEmail", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "addressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blacklisted")
    def blacklisted(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "blacklisted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "labelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="countryCodeInput")
    def country_code_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countryCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sendShortEmailInput")
    def send_short_email_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sendShortEmailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        jsii.set(self, "address", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="countryCode")
    def country_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "countryCode"))

    @country_code.setter
    def country_code(self, value: jsii.Number) -> None:
        jsii.set(self, "countryCode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        jsii.set(self, "label", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sendShortEmail")
    def send_short_email(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "sendShortEmail"))

    @send_short_email.setter
    def send_short_email(self, value: builtins.bool) -> None:
        jsii.set(self, "sendShortEmail", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        jsii.set(self, "userId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.UserContactMethodConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "address": "address",
        "label": "label",
        "type": "type",
        "user_id": "userId",
        "country_code": "countryCode",
        "send_short_email": "sendShortEmail",
    },
)
class UserContactMethodConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        address: builtins.str,
        label: builtins.str,
        type: builtins.str,
        user_id: builtins.str,
        country_code: typing.Optional[jsii.Number] = None,
        send_short_email: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#address UserContactMethod#address}.
        :param label: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#label UserContactMethod#label}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#type UserContactMethod#type}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#user_id UserContactMethod#user_id}.
        :param country_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#country_code UserContactMethod#country_code}.
        :param send_short_email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#send_short_email UserContactMethod#send_short_email}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "address": address,
            "label": label,
            "type": type,
            "user_id": user_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if country_code is not None:
            self._values["country_code"] = country_code
        if send_short_email is not None:
            self._values["send_short_email"] = send_short_email

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
    def address(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#address UserContactMethod#address}.'''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def label(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#label UserContactMethod#label}.'''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#type UserContactMethod#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#user_id UserContactMethod#user_id}.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def country_code(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#country_code UserContactMethod#country_code}.'''
        result = self._values.get("country_code")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def send_short_email(self) -> typing.Optional[builtins.bool]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_contact_method.html#send_short_email UserContactMethod#send_short_email}.'''
        result = self._values.get("send_short_email")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserContactMethodConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UserNotificationRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-pagerduty.UserNotificationRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html pagerduty_user_notification_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        contact_method: typing.Mapping[builtins.str, builtins.str],
        start_delay_in_minutes: jsii.Number,
        urgency: builtins.str,
        user_id: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html pagerduty_user_notification_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param contact_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#contact_method UserNotificationRule#contact_method}.
        :param start_delay_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#start_delay_in_minutes UserNotificationRule#start_delay_in_minutes}.
        :param urgency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#urgency UserNotificationRule#urgency}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#user_id UserNotificationRule#user_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = UserNotificationRuleConfig(
            contact_method=contact_method,
            start_delay_in_minutes=start_delay_in_minutes,
            urgency=urgency,
            user_id=user_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(UserNotificationRule, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactMethodInput")
    def contact_method_input(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "contactMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startDelayInMinutesInput")
    def start_delay_in_minutes_input(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startDelayInMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urgencyInput")
    def urgency_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "urgencyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactMethod")
    def contact_method(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "contactMethod"))

    @contact_method.setter
    def contact_method(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "contactMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startDelayInMinutes")
    def start_delay_in_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startDelayInMinutes"))

    @start_delay_in_minutes.setter
    def start_delay_in_minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "startDelayInMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urgency")
    def urgency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "urgency"))

    @urgency.setter
    def urgency(self, value: builtins.str) -> None:
        jsii.set(self, "urgency", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        jsii.set(self, "userId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-pagerduty.UserNotificationRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "contact_method": "contactMethod",
        "start_delay_in_minutes": "startDelayInMinutes",
        "urgency": "urgency",
        "user_id": "userId",
    },
)
class UserNotificationRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        contact_method: typing.Mapping[builtins.str, builtins.str],
        start_delay_in_minutes: jsii.Number,
        urgency: builtins.str,
        user_id: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param contact_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#contact_method UserNotificationRule#contact_method}.
        :param start_delay_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#start_delay_in_minutes UserNotificationRule#start_delay_in_minutes}.
        :param urgency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#urgency UserNotificationRule#urgency}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#user_id UserNotificationRule#user_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "contact_method": contact_method,
            "start_delay_in_minutes": start_delay_in_minutes,
            "urgency": urgency,
            "user_id": user_id,
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
    def contact_method(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#contact_method UserNotificationRule#contact_method}.'''
        result = self._values.get("contact_method")
        assert result is not None, "Required property 'contact_method' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def start_delay_in_minutes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#start_delay_in_minutes UserNotificationRule#start_delay_in_minutes}.'''
        result = self._values.get("start_delay_in_minutes")
        assert result is not None, "Required property 'start_delay_in_minutes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def urgency(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#urgency UserNotificationRule#urgency}.'''
        result = self._values.get("urgency")
        assert result is not None, "Required property 'urgency' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/pagerduty/r/user_notification_rule.html#user_id UserNotificationRule#user_id}.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserNotificationRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Addon",
    "AddonConfig",
    "BusinessService",
    "BusinessServiceConfig",
    "DataPagerdutyBusinessService",
    "DataPagerdutyBusinessServiceConfig",
    "DataPagerdutyEscalationPolicy",
    "DataPagerdutyEscalationPolicyConfig",
    "DataPagerdutyExtensionSchema",
    "DataPagerdutyExtensionSchemaConfig",
    "DataPagerdutyPriority",
    "DataPagerdutyPriorityConfig",
    "DataPagerdutyRuleset",
    "DataPagerdutyRulesetConfig",
    "DataPagerdutySchedule",
    "DataPagerdutyScheduleConfig",
    "DataPagerdutyService",
    "DataPagerdutyServiceConfig",
    "DataPagerdutyTeam",
    "DataPagerdutyTeamConfig",
    "DataPagerdutyUser",
    "DataPagerdutyUserConfig",
    "DataPagerdutyUserContactMethod",
    "DataPagerdutyUserContactMethodConfig",
    "DataPagerdutyVendor",
    "DataPagerdutyVendorConfig",
    "EscalationPolicy",
    "EscalationPolicyConfig",
    "EscalationPolicyRule",
    "EscalationPolicyRuleTarget",
    "EventRule",
    "EventRuleConfig",
    "Extension",
    "ExtensionConfig",
    "ExtensionServicenow",
    "ExtensionServicenowConfig",
    "MaintenanceWindow",
    "MaintenanceWindowConfig",
    "PagerdutyProvider",
    "PagerdutyProviderConfig",
    "ResponsePlay",
    "ResponsePlayConfig",
    "ResponsePlayResponder",
    "ResponsePlaySubscriber",
    "Ruleset",
    "RulesetConfig",
    "RulesetRule",
    "RulesetRuleActions",
    "RulesetRuleActionsAnnotate",
    "RulesetRuleActionsEventAction",
    "RulesetRuleActionsExtractions",
    "RulesetRuleActionsPriority",
    "RulesetRuleActionsRoute",
    "RulesetRuleActionsSeverity",
    "RulesetRuleActionsSuppress",
    "RulesetRuleActionsSuspend",
    "RulesetRuleConditions",
    "RulesetRuleConditionsSubconditions",
    "RulesetRuleConditionsSubconditionsParameter",
    "RulesetRuleConfig",
    "RulesetRuleTimeFrame",
    "RulesetRuleTimeFrameActiveBetween",
    "RulesetRuleTimeFrameScheduledWeekly",
    "RulesetRuleVariable",
    "RulesetRuleVariableParameters",
    "RulesetTeam",
    "Schedule",
    "ScheduleConfig",
    "ScheduleLayer",
    "ScheduleLayerRestriction",
    "Service",
    "ServiceAlertGroupingParameters",
    "ServiceAlertGroupingParametersConfig",
    "ServiceConfig",
    "ServiceDependency",
    "ServiceDependencyConfig",
    "ServiceDependencyDependency",
    "ServiceDependencyDependencyDependentService",
    "ServiceDependencyDependencySupportingService",
    "ServiceEventRule",
    "ServiceEventRuleActions",
    "ServiceEventRuleActionsAnnotate",
    "ServiceEventRuleActionsEventAction",
    "ServiceEventRuleActionsExtractions",
    "ServiceEventRuleActionsPriority",
    "ServiceEventRuleActionsSeverity",
    "ServiceEventRuleActionsSuppress",
    "ServiceEventRuleActionsSuspend",
    "ServiceEventRuleConditions",
    "ServiceEventRuleConditionsSubconditions",
    "ServiceEventRuleConditionsSubconditionsParameter",
    "ServiceEventRuleConfig",
    "ServiceEventRuleTimeFrame",
    "ServiceEventRuleTimeFrameActiveBetween",
    "ServiceEventRuleTimeFrameScheduledWeekly",
    "ServiceEventRuleVariable",
    "ServiceEventRuleVariableParameters",
    "ServiceIncidentUrgencyRule",
    "ServiceIncidentUrgencyRuleDuringSupportHours",
    "ServiceIncidentUrgencyRuleOutsideSupportHours",
    "ServiceIntegration",
    "ServiceIntegrationConfig",
    "ServiceScheduledActions",
    "ServiceScheduledActionsAt",
    "ServiceSupportHours",
    "Team",
    "TeamConfig",
    "TeamMembership",
    "TeamMembershipConfig",
    "User",
    "UserConfig",
    "UserContactMethod",
    "UserContactMethodConfig",
    "UserNotificationRule",
    "UserNotificationRuleConfig",
]

publication.publish()
