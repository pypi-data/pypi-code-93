'''
# Amazon Route53 Resolver Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

> All classes with the `Cfn` prefix in this module ([CFN Resources](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) are always stable and safe to use.

---
<!--END STABILITY BANNER-->

```python
# Example automatically generated. See https://github.com/aws/jsii/issues/826
import aws_cdk.aws_route53resolver as route53resolver
```
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

import aws_cdk.core


@jsii.implements(aws_cdk.core.IInspectable)
class CfnFirewallDomainList(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver.CfnFirewallDomainList",
):
    '''A CloudFormation ``AWS::Route53Resolver::FirewallDomainList``.

    :cloudformationResource: AWS::Route53Resolver::FirewallDomainList
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        domain_file_url: typing.Optional[builtins.str] = None,
        domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Create a new ``AWS::Route53Resolver::FirewallDomainList``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param domain_file_url: ``AWS::Route53Resolver::FirewallDomainList.DomainFileUrl``.
        :param domains: ``AWS::Route53Resolver::FirewallDomainList.Domains``.
        :param name: ``AWS::Route53Resolver::FirewallDomainList.Name``.
        :param tags: ``AWS::Route53Resolver::FirewallDomainList.Tags``.
        '''
        props = CfnFirewallDomainListProps(
            domain_file_url=domain_file_url, domains=domains, name=name, tags=tags
        )

        jsii.create(CfnFirewallDomainList, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrCreationTime")
    def attr_creation_time(self) -> builtins.str:
        '''
        :cloudformationAttribute: CreationTime
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreatorRequestId")
    def attr_creator_request_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: CreatorRequestId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreatorRequestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrDomainCount")
    def attr_domain_count(self) -> jsii.Number:
        '''
        :cloudformationAttribute: DomainCount
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrDomainCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrManagedOwnerName")
    def attr_managed_owner_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: ManagedOwnerName
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrManagedOwnerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrModificationTime")
    def attr_modification_time(self) -> builtins.str:
        '''
        :cloudformationAttribute: ModificationTime
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrModificationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatus")
    def attr_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: Status
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatusMessage")
    def attr_status_message(self) -> builtins.str:
        '''
        :cloudformationAttribute: StatusMessage
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatusMessage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''``AWS::Route53Resolver::FirewallDomainList.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html#cfn-route53resolver-firewalldomainlist-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainFileUrl")
    def domain_file_url(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallDomainList.DomainFileUrl``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html#cfn-route53resolver-firewalldomainlist-domainfileurl
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainFileUrl"))

    @domain_file_url.setter
    def domain_file_url(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "domainFileUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domains")
    def domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Route53Resolver::FirewallDomainList.Domains``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html#cfn-route53resolver-firewalldomainlist-domains
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "domains"))

    @domains.setter
    def domains(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        jsii.set(self, "domains", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallDomainList.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html#cfn-route53resolver-firewalldomainlist-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver.CfnFirewallDomainListProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_file_url": "domainFileUrl",
        "domains": "domains",
        "name": "name",
        "tags": "tags",
    },
)
class CfnFirewallDomainListProps:
    def __init__(
        self,
        *,
        domain_file_url: typing.Optional[builtins.str] = None,
        domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Route53Resolver::FirewallDomainList``.

        :param domain_file_url: ``AWS::Route53Resolver::FirewallDomainList.DomainFileUrl``.
        :param domains: ``AWS::Route53Resolver::FirewallDomainList.Domains``.
        :param name: ``AWS::Route53Resolver::FirewallDomainList.Name``.
        :param tags: ``AWS::Route53Resolver::FirewallDomainList.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if domain_file_url is not None:
            self._values["domain_file_url"] = domain_file_url
        if domains is not None:
            self._values["domains"] = domains
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def domain_file_url(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallDomainList.DomainFileUrl``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html#cfn-route53resolver-firewalldomainlist-domainfileurl
        '''
        result = self._values.get("domain_file_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Route53Resolver::FirewallDomainList.Domains``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html#cfn-route53resolver-firewalldomainlist-domains
        '''
        result = self._values.get("domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallDomainList.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html#cfn-route53resolver-firewalldomainlist-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        '''``AWS::Route53Resolver::FirewallDomainList.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewalldomainlist.html#cfn-route53resolver-firewalldomainlist-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.core.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFirewallDomainListProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnFirewallRuleGroup(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver.CfnFirewallRuleGroup",
):
    '''A CloudFormation ``AWS::Route53Resolver::FirewallRuleGroup``.

    :cloudformationResource: AWS::Route53Resolver::FirewallRuleGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroup.html
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        firewall_rules: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union["CfnFirewallRuleGroup.FirewallRuleProperty", aws_cdk.core.IResolvable]]]] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Create a new ``AWS::Route53Resolver::FirewallRuleGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param firewall_rules: ``AWS::Route53Resolver::FirewallRuleGroup.FirewallRules``.
        :param name: ``AWS::Route53Resolver::FirewallRuleGroup.Name``.
        :param tags: ``AWS::Route53Resolver::FirewallRuleGroup.Tags``.
        '''
        props = CfnFirewallRuleGroupProps(
            firewall_rules=firewall_rules, name=name, tags=tags
        )

        jsii.create(CfnFirewallRuleGroup, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrCreationTime")
    def attr_creation_time(self) -> builtins.str:
        '''
        :cloudformationAttribute: CreationTime
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreatorRequestId")
    def attr_creator_request_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: CreatorRequestId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreatorRequestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrModificationTime")
    def attr_modification_time(self) -> builtins.str:
        '''
        :cloudformationAttribute: ModificationTime
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrModificationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrOwnerId")
    def attr_owner_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: OwnerId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrOwnerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrRuleCount")
    def attr_rule_count(self) -> jsii.Number:
        '''
        :cloudformationAttribute: RuleCount
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrRuleCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrShareStatus")
    def attr_share_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: ShareStatus
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrShareStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatus")
    def attr_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: Status
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatusMessage")
    def attr_status_message(self) -> builtins.str:
        '''
        :cloudformationAttribute: StatusMessage
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatusMessage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''``AWS::Route53Resolver::FirewallRuleGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroup.html#cfn-route53resolver-firewallrulegroup-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRules")
    def firewall_rules(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnFirewallRuleGroup.FirewallRuleProperty", aws_cdk.core.IResolvable]]]]:
        '''``AWS::Route53Resolver::FirewallRuleGroup.FirewallRules``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroup.html#cfn-route53resolver-firewallrulegroup-firewallrules
        '''
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnFirewallRuleGroup.FirewallRuleProperty", aws_cdk.core.IResolvable]]]], jsii.get(self, "firewallRules"))

    @firewall_rules.setter
    def firewall_rules(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnFirewallRuleGroup.FirewallRuleProperty", aws_cdk.core.IResolvable]]]],
    ) -> None:
        jsii.set(self, "firewallRules", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallRuleGroup.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroup.html#cfn-route53resolver-firewallrulegroup-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-route53resolver.CfnFirewallRuleGroup.FirewallRuleProperty",
        jsii_struct_bases=[],
        name_mapping={
            "action": "action",
            "firewall_domain_list_id": "firewallDomainListId",
            "priority": "priority",
            "block_override_dns_type": "blockOverrideDnsType",
            "block_override_domain": "blockOverrideDomain",
            "block_override_ttl": "blockOverrideTtl",
            "block_response": "blockResponse",
        },
    )
    class FirewallRuleProperty:
        def __init__(
            self,
            *,
            action: builtins.str,
            firewall_domain_list_id: builtins.str,
            priority: jsii.Number,
            block_override_dns_type: typing.Optional[builtins.str] = None,
            block_override_domain: typing.Optional[builtins.str] = None,
            block_override_ttl: typing.Optional[jsii.Number] = None,
            block_response: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param action: ``CfnFirewallRuleGroup.FirewallRuleProperty.Action``.
            :param firewall_domain_list_id: ``CfnFirewallRuleGroup.FirewallRuleProperty.FirewallDomainListId``.
            :param priority: ``CfnFirewallRuleGroup.FirewallRuleProperty.Priority``.
            :param block_override_dns_type: ``CfnFirewallRuleGroup.FirewallRuleProperty.BlockOverrideDnsType``.
            :param block_override_domain: ``CfnFirewallRuleGroup.FirewallRuleProperty.BlockOverrideDomain``.
            :param block_override_ttl: ``CfnFirewallRuleGroup.FirewallRuleProperty.BlockOverrideTtl``.
            :param block_response: ``CfnFirewallRuleGroup.FirewallRuleProperty.BlockResponse``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-firewallrulegroup-firewallrule.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "action": action,
                "firewall_domain_list_id": firewall_domain_list_id,
                "priority": priority,
            }
            if block_override_dns_type is not None:
                self._values["block_override_dns_type"] = block_override_dns_type
            if block_override_domain is not None:
                self._values["block_override_domain"] = block_override_domain
            if block_override_ttl is not None:
                self._values["block_override_ttl"] = block_override_ttl
            if block_response is not None:
                self._values["block_response"] = block_response

        @builtins.property
        def action(self) -> builtins.str:
            '''``CfnFirewallRuleGroup.FirewallRuleProperty.Action``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-firewallrulegroup-firewallrule.html#cfn-route53resolver-firewallrulegroup-firewallrule-action
            '''
            result = self._values.get("action")
            assert result is not None, "Required property 'action' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def firewall_domain_list_id(self) -> builtins.str:
            '''``CfnFirewallRuleGroup.FirewallRuleProperty.FirewallDomainListId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-firewallrulegroup-firewallrule.html#cfn-route53resolver-firewallrulegroup-firewallrule-firewalldomainlistid
            '''
            result = self._values.get("firewall_domain_list_id")
            assert result is not None, "Required property 'firewall_domain_list_id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def priority(self) -> jsii.Number:
            '''``CfnFirewallRuleGroup.FirewallRuleProperty.Priority``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-firewallrulegroup-firewallrule.html#cfn-route53resolver-firewallrulegroup-firewallrule-priority
            '''
            result = self._values.get("priority")
            assert result is not None, "Required property 'priority' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def block_override_dns_type(self) -> typing.Optional[builtins.str]:
            '''``CfnFirewallRuleGroup.FirewallRuleProperty.BlockOverrideDnsType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-firewallrulegroup-firewallrule.html#cfn-route53resolver-firewallrulegroup-firewallrule-blockoverridednstype
            '''
            result = self._values.get("block_override_dns_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def block_override_domain(self) -> typing.Optional[builtins.str]:
            '''``CfnFirewallRuleGroup.FirewallRuleProperty.BlockOverrideDomain``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-firewallrulegroup-firewallrule.html#cfn-route53resolver-firewallrulegroup-firewallrule-blockoverridedomain
            '''
            result = self._values.get("block_override_domain")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def block_override_ttl(self) -> typing.Optional[jsii.Number]:
            '''``CfnFirewallRuleGroup.FirewallRuleProperty.BlockOverrideTtl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-firewallrulegroup-firewallrule.html#cfn-route53resolver-firewallrulegroup-firewallrule-blockoverridettl
            '''
            result = self._values.get("block_override_ttl")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def block_response(self) -> typing.Optional[builtins.str]:
            '''``CfnFirewallRuleGroup.FirewallRuleProperty.BlockResponse``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-firewallrulegroup-firewallrule.html#cfn-route53resolver-firewallrulegroup-firewallrule-blockresponse
            '''
            result = self._values.get("block_response")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FirewallRuleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnFirewallRuleGroupAssociation(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver.CfnFirewallRuleGroupAssociation",
):
    '''A CloudFormation ``AWS::Route53Resolver::FirewallRuleGroupAssociation``.

    :cloudformationResource: AWS::Route53Resolver::FirewallRuleGroupAssociation
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        firewall_rule_group_id: builtins.str,
        priority: jsii.Number,
        vpc_id: builtins.str,
        mutation_protection: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Create a new ``AWS::Route53Resolver::FirewallRuleGroupAssociation``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param firewall_rule_group_id: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.FirewallRuleGroupId``.
        :param priority: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.Priority``.
        :param vpc_id: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.VpcId``.
        :param mutation_protection: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.MutationProtection``.
        :param name: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.Name``.
        :param tags: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.Tags``.
        '''
        props = CfnFirewallRuleGroupAssociationProps(
            firewall_rule_group_id=firewall_rule_group_id,
            priority=priority,
            vpc_id=vpc_id,
            mutation_protection=mutation_protection,
            name=name,
            tags=tags,
        )

        jsii.create(CfnFirewallRuleGroupAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrCreationTime")
    def attr_creation_time(self) -> builtins.str:
        '''
        :cloudformationAttribute: CreationTime
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreatorRequestId")
    def attr_creator_request_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: CreatorRequestId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreatorRequestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrManagedOwnerName")
    def attr_managed_owner_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: ManagedOwnerName
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrManagedOwnerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrModificationTime")
    def attr_modification_time(self) -> builtins.str:
        '''
        :cloudformationAttribute: ModificationTime
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrModificationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatus")
    def attr_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: Status
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatusMessage")
    def attr_status_message(self) -> builtins.str:
        '''
        :cloudformationAttribute: StatusMessage
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatusMessage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupId")
    def firewall_rule_group_id(self) -> builtins.str:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.FirewallRuleGroupId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-firewallrulegroupid
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupId"))

    @firewall_rule_group_id.setter
    def firewall_rule_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "firewallRuleGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.Priority``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-priority
        '''
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        jsii.set(self, "priority", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.VpcId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-vpcid
        '''
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mutationProtection")
    def mutation_protection(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.MutationProtection``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-mutationprotection
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mutationProtection"))

    @mutation_protection.setter
    def mutation_protection(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "mutationProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver.CfnFirewallRuleGroupAssociationProps",
    jsii_struct_bases=[],
    name_mapping={
        "firewall_rule_group_id": "firewallRuleGroupId",
        "priority": "priority",
        "vpc_id": "vpcId",
        "mutation_protection": "mutationProtection",
        "name": "name",
        "tags": "tags",
    },
)
class CfnFirewallRuleGroupAssociationProps:
    def __init__(
        self,
        *,
        firewall_rule_group_id: builtins.str,
        priority: jsii.Number,
        vpc_id: builtins.str,
        mutation_protection: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Route53Resolver::FirewallRuleGroupAssociation``.

        :param firewall_rule_group_id: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.FirewallRuleGroupId``.
        :param priority: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.Priority``.
        :param vpc_id: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.VpcId``.
        :param mutation_protection: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.MutationProtection``.
        :param name: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.Name``.
        :param tags: ``AWS::Route53Resolver::FirewallRuleGroupAssociation.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "firewall_rule_group_id": firewall_rule_group_id,
            "priority": priority,
            "vpc_id": vpc_id,
        }
        if mutation_protection is not None:
            self._values["mutation_protection"] = mutation_protection
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def firewall_rule_group_id(self) -> builtins.str:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.FirewallRuleGroupId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-firewallrulegroupid
        '''
        result = self._values.get("firewall_rule_group_id")
        assert result is not None, "Required property 'firewall_rule_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.Priority``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-priority
        '''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.VpcId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-vpcid
        '''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mutation_protection(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.MutationProtection``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-mutationprotection
        '''
        result = self._values.get("mutation_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        '''``AWS::Route53Resolver::FirewallRuleGroupAssociation.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroupassociation.html#cfn-route53resolver-firewallrulegroupassociation-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.core.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFirewallRuleGroupAssociationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver.CfnFirewallRuleGroupProps",
    jsii_struct_bases=[],
    name_mapping={"firewall_rules": "firewallRules", "name": "name", "tags": "tags"},
)
class CfnFirewallRuleGroupProps:
    def __init__(
        self,
        *,
        firewall_rules: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[CfnFirewallRuleGroup.FirewallRuleProperty, aws_cdk.core.IResolvable]]]] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Route53Resolver::FirewallRuleGroup``.

        :param firewall_rules: ``AWS::Route53Resolver::FirewallRuleGroup.FirewallRules``.
        :param name: ``AWS::Route53Resolver::FirewallRuleGroup.Name``.
        :param tags: ``AWS::Route53Resolver::FirewallRuleGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroup.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if firewall_rules is not None:
            self._values["firewall_rules"] = firewall_rules
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def firewall_rules(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[CfnFirewallRuleGroup.FirewallRuleProperty, aws_cdk.core.IResolvable]]]]:
        '''``AWS::Route53Resolver::FirewallRuleGroup.FirewallRules``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroup.html#cfn-route53resolver-firewallrulegroup-firewallrules
        '''
        result = self._values.get("firewall_rules")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[CfnFirewallRuleGroup.FirewallRuleProperty, aws_cdk.core.IResolvable]]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::FirewallRuleGroup.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroup.html#cfn-route53resolver-firewallrulegroup-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        '''``AWS::Route53Resolver::FirewallRuleGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-firewallrulegroup.html#cfn-route53resolver-firewallrulegroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.core.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFirewallRuleGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnResolverDNSSECConfig(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverDNSSECConfig",
):
    '''A CloudFormation ``AWS::Route53Resolver::ResolverDNSSECConfig``.

    :cloudformationResource: AWS::Route53Resolver::ResolverDNSSECConfig
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverdnssecconfig.html
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        resource_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Route53Resolver::ResolverDNSSECConfig``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param resource_id: ``AWS::Route53Resolver::ResolverDNSSECConfig.ResourceId``.
        '''
        props = CfnResolverDNSSECConfigProps(resource_id=resource_id)

        jsii.create(CfnResolverDNSSECConfig, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrOwnerId")
    def attr_owner_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: OwnerId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrOwnerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrValidationStatus")
    def attr_validation_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: ValidationStatus
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrValidationStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverDNSSECConfig.ResourceId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverdnssecconfig.html#cfn-route53resolver-resolverdnssecconfig-resourceid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceId"))

    @resource_id.setter
    def resource_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "resourceId", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverDNSSECConfigProps",
    jsii_struct_bases=[],
    name_mapping={"resource_id": "resourceId"},
)
class CfnResolverDNSSECConfigProps:
    def __init__(self, *, resource_id: typing.Optional[builtins.str] = None) -> None:
        '''Properties for defining a ``AWS::Route53Resolver::ResolverDNSSECConfig``.

        :param resource_id: ``AWS::Route53Resolver::ResolverDNSSECConfig.ResourceId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverdnssecconfig.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if resource_id is not None:
            self._values["resource_id"] = resource_id

    @builtins.property
    def resource_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverDNSSECConfig.ResourceId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverdnssecconfig.html#cfn-route53resolver-resolverdnssecconfig-resourceid
        '''
        result = self._values.get("resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResolverDNSSECConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnResolverEndpoint(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpoint",
):
    '''A CloudFormation ``AWS::Route53Resolver::ResolverEndpoint``.

    :cloudformationResource: AWS::Route53Resolver::ResolverEndpoint
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        direction: builtins.str,
        ip_addresses: typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnResolverEndpoint.IpAddressRequestProperty"]]],
        security_group_ids: typing.Sequence[builtins.str],
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Create a new ``AWS::Route53Resolver::ResolverEndpoint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param direction: ``AWS::Route53Resolver::ResolverEndpoint.Direction``.
        :param ip_addresses: ``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.
        :param security_group_ids: ``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.
        :param name: ``AWS::Route53Resolver::ResolverEndpoint.Name``.
        :param tags: ``AWS::Route53Resolver::ResolverEndpoint.Tags``.
        '''
        props = CfnResolverEndpointProps(
            direction=direction,
            ip_addresses=ip_addresses,
            security_group_ids=security_group_ids,
            name=name,
            tags=tags,
        )

        jsii.create(CfnResolverEndpoint, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrDirection")
    def attr_direction(self) -> builtins.str:
        '''
        :cloudformationAttribute: Direction
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrDirection"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrHostVpcId")
    def attr_host_vpc_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: HostVPCId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrHostVpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrIpAddressCount")
    def attr_ip_address_count(self) -> builtins.str:
        '''
        :cloudformationAttribute: IpAddressCount
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrIpAddressCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrResolverEndpointId")
    def attr_resolver_endpoint_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: ResolverEndpointId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrResolverEndpointId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''``AWS::Route53Resolver::ResolverEndpoint.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverEndpoint.Direction``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-direction
        '''
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        jsii.set(self, "direction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResolverEndpoint.IpAddressRequestProperty"]]]:
        '''``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-ipaddresses
        '''
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResolverEndpoint.IpAddressRequestProperty"]]], jsii.get(self, "ipAddresses"))

    @ip_addresses.setter
    def ip_addresses(
        self,
        value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResolverEndpoint.IpAddressRequestProperty"]]],
    ) -> None:
        jsii.set(self, "ipAddresses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        '''``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-securitygroupids
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverEndpoint.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpoint.IpAddressRequestProperty",
        jsii_struct_bases=[],
        name_mapping={"subnet_id": "subnetId", "ip": "ip"},
    )
    class IpAddressRequestProperty:
        def __init__(
            self,
            *,
            subnet_id: builtins.str,
            ip: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param subnet_id: ``CfnResolverEndpoint.IpAddressRequestProperty.SubnetId``.
            :param ip: ``CfnResolverEndpoint.IpAddressRequestProperty.Ip``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverendpoint-ipaddressrequest.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "subnet_id": subnet_id,
            }
            if ip is not None:
                self._values["ip"] = ip

        @builtins.property
        def subnet_id(self) -> builtins.str:
            '''``CfnResolverEndpoint.IpAddressRequestProperty.SubnetId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverendpoint-ipaddressrequest.html#cfn-route53resolver-resolverendpoint-ipaddressrequest-subnetid
            '''
            result = self._values.get("subnet_id")
            assert result is not None, "Required property 'subnet_id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def ip(self) -> typing.Optional[builtins.str]:
            '''``CfnResolverEndpoint.IpAddressRequestProperty.Ip``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverendpoint-ipaddressrequest.html#cfn-route53resolver-resolverendpoint-ipaddressrequest-ip
            '''
            result = self._values.get("ip")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IpAddressRequestProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "direction": "direction",
        "ip_addresses": "ipAddresses",
        "security_group_ids": "securityGroupIds",
        "name": "name",
        "tags": "tags",
    },
)
class CfnResolverEndpointProps:
    def __init__(
        self,
        *,
        direction: builtins.str,
        ip_addresses: typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, CfnResolverEndpoint.IpAddressRequestProperty]]],
        security_group_ids: typing.Sequence[builtins.str],
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Route53Resolver::ResolverEndpoint``.

        :param direction: ``AWS::Route53Resolver::ResolverEndpoint.Direction``.
        :param ip_addresses: ``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.
        :param security_group_ids: ``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.
        :param name: ``AWS::Route53Resolver::ResolverEndpoint.Name``.
        :param tags: ``AWS::Route53Resolver::ResolverEndpoint.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "direction": direction,
            "ip_addresses": ip_addresses,
            "security_group_ids": security_group_ids,
        }
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def direction(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverEndpoint.Direction``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-direction
        '''
        result = self._values.get("direction")
        assert result is not None, "Required property 'direction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip_addresses(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnResolverEndpoint.IpAddressRequestProperty]]]:
        '''``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-ipaddresses
        '''
        result = self._values.get("ip_addresses")
        assert result is not None, "Required property 'ip_addresses' is missing"
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnResolverEndpoint.IpAddressRequestProperty]]], result)

    @builtins.property
    def security_group_ids(self) -> typing.List[builtins.str]:
        '''``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-securitygroupids
        '''
        result = self._values.get("security_group_ids")
        assert result is not None, "Required property 'security_group_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverEndpoint.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        '''``AWS::Route53Resolver::ResolverEndpoint.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.core.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResolverEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnResolverQueryLoggingConfig(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverQueryLoggingConfig",
):
    '''A CloudFormation ``AWS::Route53Resolver::ResolverQueryLoggingConfig``.

    :cloudformationResource: AWS::Route53Resolver::ResolverQueryLoggingConfig
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfig.html
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        destination_arn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Route53Resolver::ResolverQueryLoggingConfig``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param destination_arn: ``AWS::Route53Resolver::ResolverQueryLoggingConfig.DestinationArn``.
        :param name: ``AWS::Route53Resolver::ResolverQueryLoggingConfig.Name``.
        '''
        props = CfnResolverQueryLoggingConfigProps(
            destination_arn=destination_arn, name=name
        )

        jsii.create(CfnResolverQueryLoggingConfig, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrAssociationCount")
    def attr_association_count(self) -> jsii.Number:
        '''
        :cloudformationAttribute: AssociationCount
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrAssociationCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreationTime")
    def attr_creation_time(self) -> builtins.str:
        '''
        :cloudformationAttribute: CreationTime
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreatorRequestId")
    def attr_creator_request_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: CreatorRequestId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreatorRequestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrOwnerId")
    def attr_owner_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: OwnerId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrOwnerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrShareStatus")
    def attr_share_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: ShareStatus
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrShareStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatus")
    def attr_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: Status
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationArn")
    def destination_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverQueryLoggingConfig.DestinationArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfig.html#cfn-route53resolver-resolverqueryloggingconfig-destinationarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationArn"))

    @destination_arn.setter
    def destination_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "destinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverQueryLoggingConfig.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfig.html#cfn-route53resolver-resolverqueryloggingconfig-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)


@jsii.implements(aws_cdk.core.IInspectable)
class CfnResolverQueryLoggingConfigAssociation(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverQueryLoggingConfigAssociation",
):
    '''A CloudFormation ``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation``.

    :cloudformationResource: AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfigassociation.html
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        resolver_query_log_config_id: typing.Optional[builtins.str] = None,
        resource_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param resolver_query_log_config_id: ``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation.ResolverQueryLogConfigId``.
        :param resource_id: ``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation.ResourceId``.
        '''
        props = CfnResolverQueryLoggingConfigAssociationProps(
            resolver_query_log_config_id=resolver_query_log_config_id,
            resource_id=resource_id,
        )

        jsii.create(CfnResolverQueryLoggingConfigAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrCreationTime")
    def attr_creation_time(self) -> builtins.str:
        '''
        :cloudformationAttribute: CreationTime
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrError")
    def attr_error(self) -> builtins.str:
        '''
        :cloudformationAttribute: Error
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrError"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrErrorMessage")
    def attr_error_message(self) -> builtins.str:
        '''
        :cloudformationAttribute: ErrorMessage
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrErrorMessage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatus")
    def attr_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: Status
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resolverQueryLogConfigId")
    def resolver_query_log_config_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation.ResolverQueryLogConfigId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfigassociation.html#cfn-route53resolver-resolverqueryloggingconfigassociation-resolverquerylogconfigid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resolverQueryLogConfigId"))

    @resolver_query_log_config_id.setter
    def resolver_query_log_config_id(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "resolverQueryLogConfigId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation.ResourceId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfigassociation.html#cfn-route53resolver-resolverqueryloggingconfigassociation-resourceid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceId"))

    @resource_id.setter
    def resource_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "resourceId", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverQueryLoggingConfigAssociationProps",
    jsii_struct_bases=[],
    name_mapping={
        "resolver_query_log_config_id": "resolverQueryLogConfigId",
        "resource_id": "resourceId",
    },
)
class CfnResolverQueryLoggingConfigAssociationProps:
    def __init__(
        self,
        *,
        resolver_query_log_config_id: typing.Optional[builtins.str] = None,
        resource_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation``.

        :param resolver_query_log_config_id: ``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation.ResolverQueryLogConfigId``.
        :param resource_id: ``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation.ResourceId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfigassociation.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if resolver_query_log_config_id is not None:
            self._values["resolver_query_log_config_id"] = resolver_query_log_config_id
        if resource_id is not None:
            self._values["resource_id"] = resource_id

    @builtins.property
    def resolver_query_log_config_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation.ResolverQueryLogConfigId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfigassociation.html#cfn-route53resolver-resolverqueryloggingconfigassociation-resolverquerylogconfigid
        '''
        result = self._values.get("resolver_query_log_config_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation.ResourceId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfigassociation.html#cfn-route53resolver-resolverqueryloggingconfigassociation-resourceid
        '''
        result = self._values.get("resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResolverQueryLoggingConfigAssociationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverQueryLoggingConfigProps",
    jsii_struct_bases=[],
    name_mapping={"destination_arn": "destinationArn", "name": "name"},
)
class CfnResolverQueryLoggingConfigProps:
    def __init__(
        self,
        *,
        destination_arn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Route53Resolver::ResolverQueryLoggingConfig``.

        :param destination_arn: ``AWS::Route53Resolver::ResolverQueryLoggingConfig.DestinationArn``.
        :param name: ``AWS::Route53Resolver::ResolverQueryLoggingConfig.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfig.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if destination_arn is not None:
            self._values["destination_arn"] = destination_arn
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def destination_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverQueryLoggingConfig.DestinationArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfig.html#cfn-route53resolver-resolverqueryloggingconfig-destinationarn
        '''
        result = self._values.get("destination_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverQueryLoggingConfig.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverqueryloggingconfig.html#cfn-route53resolver-resolverqueryloggingconfig-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResolverQueryLoggingConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnResolverRule(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRule",
):
    '''A CloudFormation ``AWS::Route53Resolver::ResolverRule``.

    :cloudformationResource: AWS::Route53Resolver::ResolverRule
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        rule_type: builtins.str,
        name: typing.Optional[builtins.str] = None,
        resolver_endpoint_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
        target_ips: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnResolverRule.TargetAddressProperty"]]]] = None,
    ) -> None:
        '''Create a new ``AWS::Route53Resolver::ResolverRule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param domain_name: ``AWS::Route53Resolver::ResolverRule.DomainName``.
        :param rule_type: ``AWS::Route53Resolver::ResolverRule.RuleType``.
        :param name: ``AWS::Route53Resolver::ResolverRule.Name``.
        :param resolver_endpoint_id: ``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.
        :param tags: ``AWS::Route53Resolver::ResolverRule.Tags``.
        :param target_ips: ``AWS::Route53Resolver::ResolverRule.TargetIps``.
        '''
        props = CfnResolverRuleProps(
            domain_name=domain_name,
            rule_type=rule_type,
            name=name,
            resolver_endpoint_id=resolver_endpoint_id,
            tags=tags,
            target_ips=target_ips,
        )

        jsii.create(CfnResolverRule, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrDomainName")
    def attr_domain_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: DomainName
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrResolverEndpointId")
    def attr_resolver_endpoint_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: ResolverEndpointId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrResolverEndpointId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrResolverRuleId")
    def attr_resolver_rule_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: ResolverRuleId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrResolverRuleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrTargetIps")
    def attr_target_ips(self) -> builtins.str:
        '''
        :cloudformationAttribute: TargetIps
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrTargetIps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''``AWS::Route53Resolver::ResolverRule.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverRule.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-domainname
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleType")
    def rule_type(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverRule.RuleType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-ruletype
        '''
        return typing.cast(builtins.str, jsii.get(self, "ruleType"))

    @rule_type.setter
    def rule_type(self, value: builtins.str) -> None:
        jsii.set(self, "ruleType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverRule.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resolverEndpointId")
    def resolver_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-resolverendpointid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resolverEndpointId"))

    @resolver_endpoint_id.setter
    def resolver_endpoint_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "resolverEndpointId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetIps")
    def target_ips(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResolverRule.TargetAddressProperty"]]]]:
        '''``AWS::Route53Resolver::ResolverRule.TargetIps``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-targetips
        '''
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResolverRule.TargetAddressProperty"]]]], jsii.get(self, "targetIps"))

    @target_ips.setter
    def target_ips(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResolverRule.TargetAddressProperty"]]]],
    ) -> None:
        jsii.set(self, "targetIps", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRule.TargetAddressProperty",
        jsii_struct_bases=[],
        name_mapping={"ip": "ip", "port": "port"},
    )
    class TargetAddressProperty:
        def __init__(
            self,
            *,
            ip: builtins.str,
            port: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param ip: ``CfnResolverRule.TargetAddressProperty.Ip``.
            :param port: ``CfnResolverRule.TargetAddressProperty.Port``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverrule-targetaddress.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "ip": ip,
            }
            if port is not None:
                self._values["port"] = port

        @builtins.property
        def ip(self) -> builtins.str:
            '''``CfnResolverRule.TargetAddressProperty.Ip``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverrule-targetaddress.html#cfn-route53resolver-resolverrule-targetaddress-ip
            '''
            result = self._values.get("ip")
            assert result is not None, "Required property 'ip' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def port(self) -> typing.Optional[builtins.str]:
            '''``CfnResolverRule.TargetAddressProperty.Port``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverrule-targetaddress.html#cfn-route53resolver-resolverrule-targetaddress-port
            '''
            result = self._values.get("port")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TargetAddressProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnResolverRuleAssociation(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRuleAssociation",
):
    '''A CloudFormation ``AWS::Route53Resolver::ResolverRuleAssociation``.

    :cloudformationResource: AWS::Route53Resolver::ResolverRuleAssociation
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        resolver_rule_id: builtins.str,
        vpc_id: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Route53Resolver::ResolverRuleAssociation``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param resolver_rule_id: ``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.
        :param vpc_id: ``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.
        :param name: ``AWS::Route53Resolver::ResolverRuleAssociation.Name``.
        '''
        props = CfnResolverRuleAssociationProps(
            resolver_rule_id=resolver_rule_id, vpc_id=vpc_id, name=name
        )

        jsii.create(CfnResolverRuleAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrResolverRuleAssociationId")
    def attr_resolver_rule_association_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: ResolverRuleAssociationId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrResolverRuleAssociationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrResolverRuleId")
    def attr_resolver_rule_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: ResolverRuleId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrResolverRuleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrVpcId")
    def attr_vpc_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: VPCId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrVpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resolverRuleId")
    def resolver_rule_id(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-resolverruleid
        '''
        return typing.cast(builtins.str, jsii.get(self, "resolverRuleId"))

    @resolver_rule_id.setter
    def resolver_rule_id(self, value: builtins.str) -> None:
        jsii.set(self, "resolverRuleId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-vpcid
        '''
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverRuleAssociation.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRuleAssociationProps",
    jsii_struct_bases=[],
    name_mapping={
        "resolver_rule_id": "resolverRuleId",
        "vpc_id": "vpcId",
        "name": "name",
    },
)
class CfnResolverRuleAssociationProps:
    def __init__(
        self,
        *,
        resolver_rule_id: builtins.str,
        vpc_id: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Route53Resolver::ResolverRuleAssociation``.

        :param resolver_rule_id: ``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.
        :param vpc_id: ``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.
        :param name: ``AWS::Route53Resolver::ResolverRuleAssociation.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "resolver_rule_id": resolver_rule_id,
            "vpc_id": vpc_id,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def resolver_rule_id(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-resolverruleid
        '''
        result = self._values.get("resolver_rule_id")
        assert result is not None, "Required property 'resolver_rule_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-vpcid
        '''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverRuleAssociation.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResolverRuleAssociationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "rule_type": "ruleType",
        "name": "name",
        "resolver_endpoint_id": "resolverEndpointId",
        "tags": "tags",
        "target_ips": "targetIps",
    },
)
class CfnResolverRuleProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        rule_type: builtins.str,
        name: typing.Optional[builtins.str] = None,
        resolver_endpoint_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
        target_ips: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, CfnResolverRule.TargetAddressProperty]]]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Route53Resolver::ResolverRule``.

        :param domain_name: ``AWS::Route53Resolver::ResolverRule.DomainName``.
        :param rule_type: ``AWS::Route53Resolver::ResolverRule.RuleType``.
        :param name: ``AWS::Route53Resolver::ResolverRule.Name``.
        :param resolver_endpoint_id: ``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.
        :param tags: ``AWS::Route53Resolver::ResolverRule.Tags``.
        :param target_ips: ``AWS::Route53Resolver::ResolverRule.TargetIps``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
            "rule_type": rule_type,
        }
        if name is not None:
            self._values["name"] = name
        if resolver_endpoint_id is not None:
            self._values["resolver_endpoint_id"] = resolver_endpoint_id
        if tags is not None:
            self._values["tags"] = tags
        if target_ips is not None:
            self._values["target_ips"] = target_ips

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverRule.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-domainname
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_type(self) -> builtins.str:
        '''``AWS::Route53Resolver::ResolverRule.RuleType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-ruletype
        '''
        result = self._values.get("rule_type")
        assert result is not None, "Required property 'rule_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverRule.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resolver_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-resolverendpointid
        '''
        result = self._values.get("resolver_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        '''``AWS::Route53Resolver::ResolverRule.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.core.CfnTag]], result)

    @builtins.property
    def target_ips(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnResolverRule.TargetAddressProperty]]]]:
        '''``AWS::Route53Resolver::ResolverRule.TargetIps``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-targetips
        '''
        result = self._values.get("target_ips")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnResolverRule.TargetAddressProperty]]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResolverRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnFirewallDomainList",
    "CfnFirewallDomainListProps",
    "CfnFirewallRuleGroup",
    "CfnFirewallRuleGroupAssociation",
    "CfnFirewallRuleGroupAssociationProps",
    "CfnFirewallRuleGroupProps",
    "CfnResolverDNSSECConfig",
    "CfnResolverDNSSECConfigProps",
    "CfnResolverEndpoint",
    "CfnResolverEndpointProps",
    "CfnResolverQueryLoggingConfig",
    "CfnResolverQueryLoggingConfigAssociation",
    "CfnResolverQueryLoggingConfigAssociationProps",
    "CfnResolverQueryLoggingConfigProps",
    "CfnResolverRule",
    "CfnResolverRuleAssociation",
    "CfnResolverRuleAssociationProps",
    "CfnResolverRuleProps",
]

publication.publish()
