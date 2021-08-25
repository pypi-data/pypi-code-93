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
class CfnFlowTemplate(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iotthingsgraph.CfnFlowTemplate",
):
    '''A CloudFormation ``AWS::IoTThingsGraph::FlowTemplate``.

    :cloudformationResource: AWS::IoTThingsGraph::FlowTemplate
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        definition: typing.Union["CfnFlowTemplate.DefinitionDocumentProperty", _IResolvable_da3f097b],
        compatible_namespace_version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Create a new ``AWS::IoTThingsGraph::FlowTemplate``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param definition: ``AWS::IoTThingsGraph::FlowTemplate.Definition``.
        :param compatible_namespace_version: ``AWS::IoTThingsGraph::FlowTemplate.CompatibleNamespaceVersion``.
        '''
        props = CfnFlowTemplateProps(
            definition=definition,
            compatible_namespace_version=compatible_namespace_version,
        )

        jsii.create(CfnFlowTemplate, self, [scope, id, props])

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
    @jsii.member(jsii_name="definition")
    def definition(
        self,
    ) -> typing.Union["CfnFlowTemplate.DefinitionDocumentProperty", _IResolvable_da3f097b]:
        '''``AWS::IoTThingsGraph::FlowTemplate.Definition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html#cfn-iotthingsgraph-flowtemplate-definition
        '''
        return typing.cast(typing.Union["CfnFlowTemplate.DefinitionDocumentProperty", _IResolvable_da3f097b], jsii.get(self, "definition"))

    @definition.setter
    def definition(
        self,
        value: typing.Union["CfnFlowTemplate.DefinitionDocumentProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "definition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleNamespaceVersion")
    def compatible_namespace_version(self) -> typing.Optional[jsii.Number]:
        '''``AWS::IoTThingsGraph::FlowTemplate.CompatibleNamespaceVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html#cfn-iotthingsgraph-flowtemplate-compatiblenamespaceversion
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "compatibleNamespaceVersion"))

    @compatible_namespace_version.setter
    def compatible_namespace_version(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "compatibleNamespaceVersion", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotthingsgraph.CfnFlowTemplate.DefinitionDocumentProperty",
        jsii_struct_bases=[],
        name_mapping={"language": "language", "text": "text"},
    )
    class DefinitionDocumentProperty:
        def __init__(self, *, language: builtins.str, text: builtins.str) -> None:
            '''
            :param language: ``CfnFlowTemplate.DefinitionDocumentProperty.Language``.
            :param text: ``CfnFlowTemplate.DefinitionDocumentProperty.Text``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotthingsgraph-flowtemplate-definitiondocument.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "language": language,
                "text": text,
            }

        @builtins.property
        def language(self) -> builtins.str:
            '''``CfnFlowTemplate.DefinitionDocumentProperty.Language``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotthingsgraph-flowtemplate-definitiondocument.html#cfn-iotthingsgraph-flowtemplate-definitiondocument-language
            '''
            result = self._values.get("language")
            assert result is not None, "Required property 'language' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def text(self) -> builtins.str:
            '''``CfnFlowTemplate.DefinitionDocumentProperty.Text``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotthingsgraph-flowtemplate-definitiondocument.html#cfn-iotthingsgraph-flowtemplate-definitiondocument-text
            '''
            result = self._values.get("text")
            assert result is not None, "Required property 'text' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DefinitionDocumentProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iotthingsgraph.CfnFlowTemplateProps",
    jsii_struct_bases=[],
    name_mapping={
        "definition": "definition",
        "compatible_namespace_version": "compatibleNamespaceVersion",
    },
)
class CfnFlowTemplateProps:
    def __init__(
        self,
        *,
        definition: typing.Union[CfnFlowTemplate.DefinitionDocumentProperty, _IResolvable_da3f097b],
        compatible_namespace_version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoTThingsGraph::FlowTemplate``.

        :param definition: ``AWS::IoTThingsGraph::FlowTemplate.Definition``.
        :param compatible_namespace_version: ``AWS::IoTThingsGraph::FlowTemplate.CompatibleNamespaceVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
        }
        if compatible_namespace_version is not None:
            self._values["compatible_namespace_version"] = compatible_namespace_version

    @builtins.property
    def definition(
        self,
    ) -> typing.Union[CfnFlowTemplate.DefinitionDocumentProperty, _IResolvable_da3f097b]:
        '''``AWS::IoTThingsGraph::FlowTemplate.Definition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html#cfn-iotthingsgraph-flowtemplate-definition
        '''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.Union[CfnFlowTemplate.DefinitionDocumentProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def compatible_namespace_version(self) -> typing.Optional[jsii.Number]:
        '''``AWS::IoTThingsGraph::FlowTemplate.CompatibleNamespaceVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html#cfn-iotthingsgraph-flowtemplate-compatiblenamespaceversion
        '''
        result = self._values.get("compatible_namespace_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFlowTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnFlowTemplate",
    "CfnFlowTemplateProps",
]

publication.publish()
