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
class CfnClassifier(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnClassifier",
):
    '''A CloudFormation ``AWS::Glue::Classifier``.

    :cloudformationResource: AWS::Glue::Classifier
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        csv_classifier: typing.Optional[typing.Union["CfnClassifier.CsvClassifierProperty", _IResolvable_da3f097b]] = None,
        grok_classifier: typing.Optional[typing.Union["CfnClassifier.GrokClassifierProperty", _IResolvable_da3f097b]] = None,
        json_classifier: typing.Optional[typing.Union["CfnClassifier.JsonClassifierProperty", _IResolvable_da3f097b]] = None,
        xml_classifier: typing.Optional[typing.Union["CfnClassifier.XMLClassifierProperty", _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Create a new ``AWS::Glue::Classifier``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param csv_classifier: ``AWS::Glue::Classifier.CsvClassifier``.
        :param grok_classifier: ``AWS::Glue::Classifier.GrokClassifier``.
        :param json_classifier: ``AWS::Glue::Classifier.JsonClassifier``.
        :param xml_classifier: ``AWS::Glue::Classifier.XMLClassifier``.
        '''
        props = CfnClassifierProps(
            csv_classifier=csv_classifier,
            grok_classifier=grok_classifier,
            json_classifier=json_classifier,
            xml_classifier=xml_classifier,
        )

        jsii.create(CfnClassifier, self, [scope, id, props])

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
    @jsii.member(jsii_name="csvClassifier")
    def csv_classifier(
        self,
    ) -> typing.Optional[typing.Union["CfnClassifier.CsvClassifierProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Classifier.CsvClassifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-csvclassifier
        '''
        return typing.cast(typing.Optional[typing.Union["CfnClassifier.CsvClassifierProperty", _IResolvable_da3f097b]], jsii.get(self, "csvClassifier"))

    @csv_classifier.setter
    def csv_classifier(
        self,
        value: typing.Optional[typing.Union["CfnClassifier.CsvClassifierProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "csvClassifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grokClassifier")
    def grok_classifier(
        self,
    ) -> typing.Optional[typing.Union["CfnClassifier.GrokClassifierProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Classifier.GrokClassifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-grokclassifier
        '''
        return typing.cast(typing.Optional[typing.Union["CfnClassifier.GrokClassifierProperty", _IResolvable_da3f097b]], jsii.get(self, "grokClassifier"))

    @grok_classifier.setter
    def grok_classifier(
        self,
        value: typing.Optional[typing.Union["CfnClassifier.GrokClassifierProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "grokClassifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jsonClassifier")
    def json_classifier(
        self,
    ) -> typing.Optional[typing.Union["CfnClassifier.JsonClassifierProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Classifier.JsonClassifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-jsonclassifier
        '''
        return typing.cast(typing.Optional[typing.Union["CfnClassifier.JsonClassifierProperty", _IResolvable_da3f097b]], jsii.get(self, "jsonClassifier"))

    @json_classifier.setter
    def json_classifier(
        self,
        value: typing.Optional[typing.Union["CfnClassifier.JsonClassifierProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "jsonClassifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="xmlClassifier")
    def xml_classifier(
        self,
    ) -> typing.Optional[typing.Union["CfnClassifier.XMLClassifierProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Classifier.XMLClassifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-xmlclassifier
        '''
        return typing.cast(typing.Optional[typing.Union["CfnClassifier.XMLClassifierProperty", _IResolvable_da3f097b]], jsii.get(self, "xmlClassifier"))

    @xml_classifier.setter
    def xml_classifier(
        self,
        value: typing.Optional[typing.Union["CfnClassifier.XMLClassifierProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "xmlClassifier", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnClassifier.CsvClassifierProperty",
        jsii_struct_bases=[],
        name_mapping={
            "allow_single_column": "allowSingleColumn",
            "contains_header": "containsHeader",
            "delimiter": "delimiter",
            "disable_value_trimming": "disableValueTrimming",
            "header": "header",
            "name": "name",
            "quote_symbol": "quoteSymbol",
        },
    )
    class CsvClassifierProperty:
        def __init__(
            self,
            *,
            allow_single_column: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            contains_header: typing.Optional[builtins.str] = None,
            delimiter: typing.Optional[builtins.str] = None,
            disable_value_trimming: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            header: typing.Optional[typing.Sequence[builtins.str]] = None,
            name: typing.Optional[builtins.str] = None,
            quote_symbol: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param allow_single_column: ``CfnClassifier.CsvClassifierProperty.AllowSingleColumn``.
            :param contains_header: ``CfnClassifier.CsvClassifierProperty.ContainsHeader``.
            :param delimiter: ``CfnClassifier.CsvClassifierProperty.Delimiter``.
            :param disable_value_trimming: ``CfnClassifier.CsvClassifierProperty.DisableValueTrimming``.
            :param header: ``CfnClassifier.CsvClassifierProperty.Header``.
            :param name: ``CfnClassifier.CsvClassifierProperty.Name``.
            :param quote_symbol: ``CfnClassifier.CsvClassifierProperty.QuoteSymbol``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if allow_single_column is not None:
                self._values["allow_single_column"] = allow_single_column
            if contains_header is not None:
                self._values["contains_header"] = contains_header
            if delimiter is not None:
                self._values["delimiter"] = delimiter
            if disable_value_trimming is not None:
                self._values["disable_value_trimming"] = disable_value_trimming
            if header is not None:
                self._values["header"] = header
            if name is not None:
                self._values["name"] = name
            if quote_symbol is not None:
                self._values["quote_symbol"] = quote_symbol

        @builtins.property
        def allow_single_column(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnClassifier.CsvClassifierProperty.AllowSingleColumn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-allowsinglecolumn
            '''
            result = self._values.get("allow_single_column")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def contains_header(self) -> typing.Optional[builtins.str]:
            '''``CfnClassifier.CsvClassifierProperty.ContainsHeader``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-containsheader
            '''
            result = self._values.get("contains_header")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def delimiter(self) -> typing.Optional[builtins.str]:
            '''``CfnClassifier.CsvClassifierProperty.Delimiter``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-delimiter
            '''
            result = self._values.get("delimiter")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def disable_value_trimming(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnClassifier.CsvClassifierProperty.DisableValueTrimming``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-disablevaluetrimming
            '''
            result = self._values.get("disable_value_trimming")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def header(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnClassifier.CsvClassifierProperty.Header``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-header
            '''
            result = self._values.get("header")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnClassifier.CsvClassifierProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def quote_symbol(self) -> typing.Optional[builtins.str]:
            '''``CfnClassifier.CsvClassifierProperty.QuoteSymbol``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-quotesymbol
            '''
            result = self._values.get("quote_symbol")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CsvClassifierProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnClassifier.GrokClassifierProperty",
        jsii_struct_bases=[],
        name_mapping={
            "classification": "classification",
            "grok_pattern": "grokPattern",
            "custom_patterns": "customPatterns",
            "name": "name",
        },
    )
    class GrokClassifierProperty:
        def __init__(
            self,
            *,
            classification: builtins.str,
            grok_pattern: builtins.str,
            custom_patterns: typing.Optional[builtins.str] = None,
            name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param classification: ``CfnClassifier.GrokClassifierProperty.Classification``.
            :param grok_pattern: ``CfnClassifier.GrokClassifierProperty.GrokPattern``.
            :param custom_patterns: ``CfnClassifier.GrokClassifierProperty.CustomPatterns``.
            :param name: ``CfnClassifier.GrokClassifierProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "classification": classification,
                "grok_pattern": grok_pattern,
            }
            if custom_patterns is not None:
                self._values["custom_patterns"] = custom_patterns
            if name is not None:
                self._values["name"] = name

        @builtins.property
        def classification(self) -> builtins.str:
            '''``CfnClassifier.GrokClassifierProperty.Classification``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-classification
            '''
            result = self._values.get("classification")
            assert result is not None, "Required property 'classification' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def grok_pattern(self) -> builtins.str:
            '''``CfnClassifier.GrokClassifierProperty.GrokPattern``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-grokpattern
            '''
            result = self._values.get("grok_pattern")
            assert result is not None, "Required property 'grok_pattern' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def custom_patterns(self) -> typing.Optional[builtins.str]:
            '''``CfnClassifier.GrokClassifierProperty.CustomPatterns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-custompatterns
            '''
            result = self._values.get("custom_patterns")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnClassifier.GrokClassifierProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "GrokClassifierProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnClassifier.JsonClassifierProperty",
        jsii_struct_bases=[],
        name_mapping={"json_path": "jsonPath", "name": "name"},
    )
    class JsonClassifierProperty:
        def __init__(
            self,
            *,
            json_path: builtins.str,
            name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param json_path: ``CfnClassifier.JsonClassifierProperty.JsonPath``.
            :param name: ``CfnClassifier.JsonClassifierProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-jsonclassifier.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "json_path": json_path,
            }
            if name is not None:
                self._values["name"] = name

        @builtins.property
        def json_path(self) -> builtins.str:
            '''``CfnClassifier.JsonClassifierProperty.JsonPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-jsonclassifier.html#cfn-glue-classifier-jsonclassifier-jsonpath
            '''
            result = self._values.get("json_path")
            assert result is not None, "Required property 'json_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnClassifier.JsonClassifierProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-jsonclassifier.html#cfn-glue-classifier-jsonclassifier-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "JsonClassifierProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnClassifier.XMLClassifierProperty",
        jsii_struct_bases=[],
        name_mapping={
            "classification": "classification",
            "row_tag": "rowTag",
            "name": "name",
        },
    )
    class XMLClassifierProperty:
        def __init__(
            self,
            *,
            classification: builtins.str,
            row_tag: builtins.str,
            name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param classification: ``CfnClassifier.XMLClassifierProperty.Classification``.
            :param row_tag: ``CfnClassifier.XMLClassifierProperty.RowTag``.
            :param name: ``CfnClassifier.XMLClassifierProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "classification": classification,
                "row_tag": row_tag,
            }
            if name is not None:
                self._values["name"] = name

        @builtins.property
        def classification(self) -> builtins.str:
            '''``CfnClassifier.XMLClassifierProperty.Classification``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html#cfn-glue-classifier-xmlclassifier-classification
            '''
            result = self._values.get("classification")
            assert result is not None, "Required property 'classification' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def row_tag(self) -> builtins.str:
            '''``CfnClassifier.XMLClassifierProperty.RowTag``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html#cfn-glue-classifier-xmlclassifier-rowtag
            '''
            result = self._values.get("row_tag")
            assert result is not None, "Required property 'row_tag' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnClassifier.XMLClassifierProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html#cfn-glue-classifier-xmlclassifier-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "XMLClassifierProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnClassifierProps",
    jsii_struct_bases=[],
    name_mapping={
        "csv_classifier": "csvClassifier",
        "grok_classifier": "grokClassifier",
        "json_classifier": "jsonClassifier",
        "xml_classifier": "xmlClassifier",
    },
)
class CfnClassifierProps:
    def __init__(
        self,
        *,
        csv_classifier: typing.Optional[typing.Union[CfnClassifier.CsvClassifierProperty, _IResolvable_da3f097b]] = None,
        grok_classifier: typing.Optional[typing.Union[CfnClassifier.GrokClassifierProperty, _IResolvable_da3f097b]] = None,
        json_classifier: typing.Optional[typing.Union[CfnClassifier.JsonClassifierProperty, _IResolvable_da3f097b]] = None,
        xml_classifier: typing.Optional[typing.Union[CfnClassifier.XMLClassifierProperty, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Classifier``.

        :param csv_classifier: ``AWS::Glue::Classifier.CsvClassifier``.
        :param grok_classifier: ``AWS::Glue::Classifier.GrokClassifier``.
        :param json_classifier: ``AWS::Glue::Classifier.JsonClassifier``.
        :param xml_classifier: ``AWS::Glue::Classifier.XMLClassifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if csv_classifier is not None:
            self._values["csv_classifier"] = csv_classifier
        if grok_classifier is not None:
            self._values["grok_classifier"] = grok_classifier
        if json_classifier is not None:
            self._values["json_classifier"] = json_classifier
        if xml_classifier is not None:
            self._values["xml_classifier"] = xml_classifier

    @builtins.property
    def csv_classifier(
        self,
    ) -> typing.Optional[typing.Union[CfnClassifier.CsvClassifierProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Classifier.CsvClassifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-csvclassifier
        '''
        result = self._values.get("csv_classifier")
        return typing.cast(typing.Optional[typing.Union[CfnClassifier.CsvClassifierProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def grok_classifier(
        self,
    ) -> typing.Optional[typing.Union[CfnClassifier.GrokClassifierProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Classifier.GrokClassifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-grokclassifier
        '''
        result = self._values.get("grok_classifier")
        return typing.cast(typing.Optional[typing.Union[CfnClassifier.GrokClassifierProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def json_classifier(
        self,
    ) -> typing.Optional[typing.Union[CfnClassifier.JsonClassifierProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Classifier.JsonClassifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-jsonclassifier
        '''
        result = self._values.get("json_classifier")
        return typing.cast(typing.Optional[typing.Union[CfnClassifier.JsonClassifierProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def xml_classifier(
        self,
    ) -> typing.Optional[typing.Union[CfnClassifier.XMLClassifierProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Classifier.XMLClassifier``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-xmlclassifier
        '''
        result = self._values.get("xml_classifier")
        return typing.cast(typing.Optional[typing.Union[CfnClassifier.XMLClassifierProperty, _IResolvable_da3f097b]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnClassifierProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnConnection(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnConnection",
):
    '''A CloudFormation ``AWS::Glue::Connection``.

    :cloudformationResource: AWS::Glue::Connection
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        catalog_id: builtins.str,
        connection_input: typing.Union["CfnConnection.ConnectionInputProperty", _IResolvable_da3f097b],
    ) -> None:
        '''Create a new ``AWS::Glue::Connection``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param catalog_id: ``AWS::Glue::Connection.CatalogId``.
        :param connection_input: ``AWS::Glue::Connection.ConnectionInput``.
        '''
        props = CfnConnectionProps(
            catalog_id=catalog_id, connection_input=connection_input
        )

        jsii.create(CfnConnection, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::Connection.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-catalogid
        '''
        return typing.cast(builtins.str, jsii.get(self, "catalogId"))

    @catalog_id.setter
    def catalog_id(self, value: builtins.str) -> None:
        jsii.set(self, "catalogId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionInput")
    def connection_input(
        self,
    ) -> typing.Union["CfnConnection.ConnectionInputProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::Connection.ConnectionInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-connectioninput
        '''
        return typing.cast(typing.Union["CfnConnection.ConnectionInputProperty", _IResolvable_da3f097b], jsii.get(self, "connectionInput"))

    @connection_input.setter
    def connection_input(
        self,
        value: typing.Union["CfnConnection.ConnectionInputProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "connectionInput", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnConnection.ConnectionInputProperty",
        jsii_struct_bases=[],
        name_mapping={
            "connection_type": "connectionType",
            "connection_properties": "connectionProperties",
            "description": "description",
            "match_criteria": "matchCriteria",
            "name": "name",
            "physical_connection_requirements": "physicalConnectionRequirements",
        },
    )
    class ConnectionInputProperty:
        def __init__(
            self,
            *,
            connection_type: builtins.str,
            connection_properties: typing.Any = None,
            description: typing.Optional[builtins.str] = None,
            match_criteria: typing.Optional[typing.Sequence[builtins.str]] = None,
            name: typing.Optional[builtins.str] = None,
            physical_connection_requirements: typing.Optional[typing.Union["CfnConnection.PhysicalConnectionRequirementsProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param connection_type: ``CfnConnection.ConnectionInputProperty.ConnectionType``.
            :param connection_properties: ``CfnConnection.ConnectionInputProperty.ConnectionProperties``.
            :param description: ``CfnConnection.ConnectionInputProperty.Description``.
            :param match_criteria: ``CfnConnection.ConnectionInputProperty.MatchCriteria``.
            :param name: ``CfnConnection.ConnectionInputProperty.Name``.
            :param physical_connection_requirements: ``CfnConnection.ConnectionInputProperty.PhysicalConnectionRequirements``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "connection_type": connection_type,
            }
            if connection_properties is not None:
                self._values["connection_properties"] = connection_properties
            if description is not None:
                self._values["description"] = description
            if match_criteria is not None:
                self._values["match_criteria"] = match_criteria
            if name is not None:
                self._values["name"] = name
            if physical_connection_requirements is not None:
                self._values["physical_connection_requirements"] = physical_connection_requirements

        @builtins.property
        def connection_type(self) -> builtins.str:
            '''``CfnConnection.ConnectionInputProperty.ConnectionType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-connectiontype
            '''
            result = self._values.get("connection_type")
            assert result is not None, "Required property 'connection_type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def connection_properties(self) -> typing.Any:
            '''``CfnConnection.ConnectionInputProperty.ConnectionProperties``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-connectionproperties
            '''
            result = self._values.get("connection_properties")
            return typing.cast(typing.Any, result)

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            '''``CfnConnection.ConnectionInputProperty.Description``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-description
            '''
            result = self._values.get("description")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def match_criteria(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnConnection.ConnectionInputProperty.MatchCriteria``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-matchcriteria
            '''
            result = self._values.get("match_criteria")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnConnection.ConnectionInputProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def physical_connection_requirements(
            self,
        ) -> typing.Optional[typing.Union["CfnConnection.PhysicalConnectionRequirementsProperty", _IResolvable_da3f097b]]:
            '''``CfnConnection.ConnectionInputProperty.PhysicalConnectionRequirements``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-physicalconnectionrequirements
            '''
            result = self._values.get("physical_connection_requirements")
            return typing.cast(typing.Optional[typing.Union["CfnConnection.PhysicalConnectionRequirementsProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConnectionInputProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnConnection.PhysicalConnectionRequirementsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "availability_zone": "availabilityZone",
            "security_group_id_list": "securityGroupIdList",
            "subnet_id": "subnetId",
        },
    )
    class PhysicalConnectionRequirementsProperty:
        def __init__(
            self,
            *,
            availability_zone: typing.Optional[builtins.str] = None,
            security_group_id_list: typing.Optional[typing.Sequence[builtins.str]] = None,
            subnet_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param availability_zone: ``CfnConnection.PhysicalConnectionRequirementsProperty.AvailabilityZone``.
            :param security_group_id_list: ``CfnConnection.PhysicalConnectionRequirementsProperty.SecurityGroupIdList``.
            :param subnet_id: ``CfnConnection.PhysicalConnectionRequirementsProperty.SubnetId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if availability_zone is not None:
                self._values["availability_zone"] = availability_zone
            if security_group_id_list is not None:
                self._values["security_group_id_list"] = security_group_id_list
            if subnet_id is not None:
                self._values["subnet_id"] = subnet_id

        @builtins.property
        def availability_zone(self) -> typing.Optional[builtins.str]:
            '''``CfnConnection.PhysicalConnectionRequirementsProperty.AvailabilityZone``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html#cfn-glue-connection-physicalconnectionrequirements-availabilityzone
            '''
            result = self._values.get("availability_zone")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def security_group_id_list(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnConnection.PhysicalConnectionRequirementsProperty.SecurityGroupIdList``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html#cfn-glue-connection-physicalconnectionrequirements-securitygroupidlist
            '''
            result = self._values.get("security_group_id_list")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def subnet_id(self) -> typing.Optional[builtins.str]:
            '''``CfnConnection.PhysicalConnectionRequirementsProperty.SubnetId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html#cfn-glue-connection-physicalconnectionrequirements-subnetid
            '''
            result = self._values.get("subnet_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PhysicalConnectionRequirementsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnConnectionProps",
    jsii_struct_bases=[],
    name_mapping={"catalog_id": "catalogId", "connection_input": "connectionInput"},
)
class CfnConnectionProps:
    def __init__(
        self,
        *,
        catalog_id: builtins.str,
        connection_input: typing.Union[CfnConnection.ConnectionInputProperty, _IResolvable_da3f097b],
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Connection``.

        :param catalog_id: ``AWS::Glue::Connection.CatalogId``.
        :param connection_input: ``AWS::Glue::Connection.ConnectionInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "catalog_id": catalog_id,
            "connection_input": connection_input,
        }

    @builtins.property
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::Connection.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-catalogid
        '''
        result = self._values.get("catalog_id")
        assert result is not None, "Required property 'catalog_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connection_input(
        self,
    ) -> typing.Union[CfnConnection.ConnectionInputProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::Connection.ConnectionInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-connectioninput
        '''
        result = self._values.get("connection_input")
        assert result is not None, "Required property 'connection_input' is missing"
        return typing.cast(typing.Union[CfnConnection.ConnectionInputProperty, _IResolvable_da3f097b], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnConnectionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnCrawler(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnCrawler",
):
    '''A CloudFormation ``AWS::Glue::Crawler``.

    :cloudformationResource: AWS::Glue::Crawler
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        role: builtins.str,
        targets: typing.Union["CfnCrawler.TargetsProperty", _IResolvable_da3f097b],
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        configuration: typing.Optional[builtins.str] = None,
        crawler_security_configuration: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        recrawl_policy: typing.Optional[typing.Union["CfnCrawler.RecrawlPolicyProperty", _IResolvable_da3f097b]] = None,
        schedule: typing.Optional[typing.Union["CfnCrawler.ScheduleProperty", _IResolvable_da3f097b]] = None,
        schema_change_policy: typing.Optional[typing.Union["CfnCrawler.SchemaChangePolicyProperty", _IResolvable_da3f097b]] = None,
        table_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Glue::Crawler``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param role: ``AWS::Glue::Crawler.Role``.
        :param targets: ``AWS::Glue::Crawler.Targets``.
        :param classifiers: ``AWS::Glue::Crawler.Classifiers``.
        :param configuration: ``AWS::Glue::Crawler.Configuration``.
        :param crawler_security_configuration: ``AWS::Glue::Crawler.CrawlerSecurityConfiguration``.
        :param database_name: ``AWS::Glue::Crawler.DatabaseName``.
        :param description: ``AWS::Glue::Crawler.Description``.
        :param name: ``AWS::Glue::Crawler.Name``.
        :param recrawl_policy: ``AWS::Glue::Crawler.RecrawlPolicy``.
        :param schedule: ``AWS::Glue::Crawler.Schedule``.
        :param schema_change_policy: ``AWS::Glue::Crawler.SchemaChangePolicy``.
        :param table_prefix: ``AWS::Glue::Crawler.TablePrefix``.
        :param tags: ``AWS::Glue::Crawler.Tags``.
        '''
        props = CfnCrawlerProps(
            role=role,
            targets=targets,
            classifiers=classifiers,
            configuration=configuration,
            crawler_security_configuration=crawler_security_configuration,
            database_name=database_name,
            description=description,
            name=name,
            recrawl_policy=recrawl_policy,
            schedule=schedule,
            schema_change_policy=schema_change_policy,
            table_prefix=table_prefix,
            tags=tags,
        )

        jsii.create(CfnCrawler, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Glue::Crawler.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        '''``AWS::Glue::Crawler.Role``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-role
        '''
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Union["CfnCrawler.TargetsProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::Crawler.Targets``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-targets
        '''
        return typing.cast(typing.Union["CfnCrawler.TargetsProperty", _IResolvable_da3f097b], jsii.get(self, "targets"))

    @targets.setter
    def targets(
        self,
        value: typing.Union["CfnCrawler.TargetsProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "targets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="classifiers")
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Glue::Crawler.Classifiers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-classifiers
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "classifiers"))

    @classifiers.setter
    def classifiers(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        jsii.set(self, "classifiers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.Configuration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-configuration
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "configuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="crawlerSecurityConfiguration")
    def crawler_security_configuration(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.CrawlerSecurityConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-crawlersecurityconfiguration
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "crawlerSecurityConfiguration"))

    @crawler_security_configuration.setter
    def crawler_security_configuration(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "crawlerSecurityConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.DatabaseName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-databasename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recrawlPolicy")
    def recrawl_policy(
        self,
    ) -> typing.Optional[typing.Union["CfnCrawler.RecrawlPolicyProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Crawler.RecrawlPolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-recrawlpolicy
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCrawler.RecrawlPolicyProperty", _IResolvable_da3f097b]], jsii.get(self, "recrawlPolicy"))

    @recrawl_policy.setter
    def recrawl_policy(
        self,
        value: typing.Optional[typing.Union["CfnCrawler.RecrawlPolicyProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "recrawlPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(
        self,
    ) -> typing.Optional[typing.Union["CfnCrawler.ScheduleProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Crawler.Schedule``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schedule
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCrawler.ScheduleProperty", _IResolvable_da3f097b]], jsii.get(self, "schedule"))

    @schedule.setter
    def schedule(
        self,
        value: typing.Optional[typing.Union["CfnCrawler.ScheduleProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "schedule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaChangePolicy")
    def schema_change_policy(
        self,
    ) -> typing.Optional[typing.Union["CfnCrawler.SchemaChangePolicyProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Crawler.SchemaChangePolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schemachangepolicy
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCrawler.SchemaChangePolicyProperty", _IResolvable_da3f097b]], jsii.get(self, "schemaChangePolicy"))

    @schema_change_policy.setter
    def schema_change_policy(
        self,
        value: typing.Optional[typing.Union["CfnCrawler.SchemaChangePolicyProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "schemaChangePolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tablePrefix")
    def table_prefix(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.TablePrefix``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tableprefix
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tablePrefix"))

    @table_prefix.setter
    def table_prefix(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "tablePrefix", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnCrawler.CatalogTargetProperty",
        jsii_struct_bases=[],
        name_mapping={"database_name": "databaseName", "tables": "tables"},
    )
    class CatalogTargetProperty:
        def __init__(
            self,
            *,
            database_name: typing.Optional[builtins.str] = None,
            tables: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''
            :param database_name: ``CfnCrawler.CatalogTargetProperty.DatabaseName``.
            :param tables: ``CfnCrawler.CatalogTargetProperty.Tables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-catalogtarget.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if database_name is not None:
                self._values["database_name"] = database_name
            if tables is not None:
                self._values["tables"] = tables

        @builtins.property
        def database_name(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.CatalogTargetProperty.DatabaseName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-catalogtarget.html#cfn-glue-crawler-catalogtarget-databasename
            '''
            result = self._values.get("database_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def tables(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnCrawler.CatalogTargetProperty.Tables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-catalogtarget.html#cfn-glue-crawler-catalogtarget-tables
            '''
            result = self._values.get("tables")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CatalogTargetProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnCrawler.DynamoDBTargetProperty",
        jsii_struct_bases=[],
        name_mapping={"path": "path"},
    )
    class DynamoDBTargetProperty:
        def __init__(self, *, path: typing.Optional[builtins.str] = None) -> None:
            '''
            :param path: ``CfnCrawler.DynamoDBTargetProperty.Path``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-dynamodbtarget.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if path is not None:
                self._values["path"] = path

        @builtins.property
        def path(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.DynamoDBTargetProperty.Path``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-dynamodbtarget.html#cfn-glue-crawler-dynamodbtarget-path
            '''
            result = self._values.get("path")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DynamoDBTargetProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnCrawler.JdbcTargetProperty",
        jsii_struct_bases=[],
        name_mapping={
            "connection_name": "connectionName",
            "exclusions": "exclusions",
            "path": "path",
        },
    )
    class JdbcTargetProperty:
        def __init__(
            self,
            *,
            connection_name: typing.Optional[builtins.str] = None,
            exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
            path: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param connection_name: ``CfnCrawler.JdbcTargetProperty.ConnectionName``.
            :param exclusions: ``CfnCrawler.JdbcTargetProperty.Exclusions``.
            :param path: ``CfnCrawler.JdbcTargetProperty.Path``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if connection_name is not None:
                self._values["connection_name"] = connection_name
            if exclusions is not None:
                self._values["exclusions"] = exclusions
            if path is not None:
                self._values["path"] = path

        @builtins.property
        def connection_name(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.JdbcTargetProperty.ConnectionName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html#cfn-glue-crawler-jdbctarget-connectionname
            '''
            result = self._values.get("connection_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnCrawler.JdbcTargetProperty.Exclusions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html#cfn-glue-crawler-jdbctarget-exclusions
            '''
            result = self._values.get("exclusions")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def path(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.JdbcTargetProperty.Path``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html#cfn-glue-crawler-jdbctarget-path
            '''
            result = self._values.get("path")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "JdbcTargetProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnCrawler.RecrawlPolicyProperty",
        jsii_struct_bases=[],
        name_mapping={"recrawl_behavior": "recrawlBehavior"},
    )
    class RecrawlPolicyProperty:
        def __init__(
            self,
            *,
            recrawl_behavior: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param recrawl_behavior: ``CfnCrawler.RecrawlPolicyProperty.RecrawlBehavior``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-recrawlpolicy.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if recrawl_behavior is not None:
                self._values["recrawl_behavior"] = recrawl_behavior

        @builtins.property
        def recrawl_behavior(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.RecrawlPolicyProperty.RecrawlBehavior``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-recrawlpolicy.html#cfn-glue-crawler-recrawlpolicy-recrawlbehavior
            '''
            result = self._values.get("recrawl_behavior")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RecrawlPolicyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnCrawler.S3TargetProperty",
        jsii_struct_bases=[],
        name_mapping={
            "connection_name": "connectionName",
            "exclusions": "exclusions",
            "path": "path",
        },
    )
    class S3TargetProperty:
        def __init__(
            self,
            *,
            connection_name: typing.Optional[builtins.str] = None,
            exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
            path: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param connection_name: ``CfnCrawler.S3TargetProperty.ConnectionName``.
            :param exclusions: ``CfnCrawler.S3TargetProperty.Exclusions``.
            :param path: ``CfnCrawler.S3TargetProperty.Path``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if connection_name is not None:
                self._values["connection_name"] = connection_name
            if exclusions is not None:
                self._values["exclusions"] = exclusions
            if path is not None:
                self._values["path"] = path

        @builtins.property
        def connection_name(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.S3TargetProperty.ConnectionName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html#cfn-glue-crawler-s3target-connectionname
            '''
            result = self._values.get("connection_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnCrawler.S3TargetProperty.Exclusions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html#cfn-glue-crawler-s3target-exclusions
            '''
            result = self._values.get("exclusions")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def path(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.S3TargetProperty.Path``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html#cfn-glue-crawler-s3target-path
            '''
            result = self._values.get("path")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3TargetProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnCrawler.ScheduleProperty",
        jsii_struct_bases=[],
        name_mapping={"schedule_expression": "scheduleExpression"},
    )
    class ScheduleProperty:
        def __init__(
            self,
            *,
            schedule_expression: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param schedule_expression: ``CfnCrawler.ScheduleProperty.ScheduleExpression``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schedule.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if schedule_expression is not None:
                self._values["schedule_expression"] = schedule_expression

        @builtins.property
        def schedule_expression(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.ScheduleProperty.ScheduleExpression``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schedule.html#cfn-glue-crawler-schedule-scheduleexpression
            '''
            result = self._values.get("schedule_expression")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ScheduleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnCrawler.SchemaChangePolicyProperty",
        jsii_struct_bases=[],
        name_mapping={
            "delete_behavior": "deleteBehavior",
            "update_behavior": "updateBehavior",
        },
    )
    class SchemaChangePolicyProperty:
        def __init__(
            self,
            *,
            delete_behavior: typing.Optional[builtins.str] = None,
            update_behavior: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param delete_behavior: ``CfnCrawler.SchemaChangePolicyProperty.DeleteBehavior``.
            :param update_behavior: ``CfnCrawler.SchemaChangePolicyProperty.UpdateBehavior``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schemachangepolicy.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if delete_behavior is not None:
                self._values["delete_behavior"] = delete_behavior
            if update_behavior is not None:
                self._values["update_behavior"] = update_behavior

        @builtins.property
        def delete_behavior(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.SchemaChangePolicyProperty.DeleteBehavior``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schemachangepolicy.html#cfn-glue-crawler-schemachangepolicy-deletebehavior
            '''
            result = self._values.get("delete_behavior")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def update_behavior(self) -> typing.Optional[builtins.str]:
            '''``CfnCrawler.SchemaChangePolicyProperty.UpdateBehavior``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schemachangepolicy.html#cfn-glue-crawler-schemachangepolicy-updatebehavior
            '''
            result = self._values.get("update_behavior")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SchemaChangePolicyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnCrawler.TargetsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "catalog_targets": "catalogTargets",
            "dynamo_db_targets": "dynamoDbTargets",
            "jdbc_targets": "jdbcTargets",
            "s3_targets": "s3Targets",
        },
    )
    class TargetsProperty:
        def __init__(
            self,
            *,
            catalog_targets: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnCrawler.CatalogTargetProperty", _IResolvable_da3f097b]]]] = None,
            dynamo_db_targets: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnCrawler.DynamoDBTargetProperty", _IResolvable_da3f097b]]]] = None,
            jdbc_targets: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnCrawler.JdbcTargetProperty", _IResolvable_da3f097b]]]] = None,
            s3_targets: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnCrawler.S3TargetProperty", _IResolvable_da3f097b]]]] = None,
        ) -> None:
            '''
            :param catalog_targets: ``CfnCrawler.TargetsProperty.CatalogTargets``.
            :param dynamo_db_targets: ``CfnCrawler.TargetsProperty.DynamoDBTargets``.
            :param jdbc_targets: ``CfnCrawler.TargetsProperty.JdbcTargets``.
            :param s3_targets: ``CfnCrawler.TargetsProperty.S3Targets``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if catalog_targets is not None:
                self._values["catalog_targets"] = catalog_targets
            if dynamo_db_targets is not None:
                self._values["dynamo_db_targets"] = dynamo_db_targets
            if jdbc_targets is not None:
                self._values["jdbc_targets"] = jdbc_targets
            if s3_targets is not None:
                self._values["s3_targets"] = s3_targets

        @builtins.property
        def catalog_targets(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCrawler.CatalogTargetProperty", _IResolvable_da3f097b]]]]:
            '''``CfnCrawler.TargetsProperty.CatalogTargets``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html#cfn-glue-crawler-targets-catalogtargets
            '''
            result = self._values.get("catalog_targets")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCrawler.CatalogTargetProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def dynamo_db_targets(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCrawler.DynamoDBTargetProperty", _IResolvable_da3f097b]]]]:
            '''``CfnCrawler.TargetsProperty.DynamoDBTargets``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html#cfn-glue-crawler-targets-dynamodbtargets
            '''
            result = self._values.get("dynamo_db_targets")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCrawler.DynamoDBTargetProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def jdbc_targets(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCrawler.JdbcTargetProperty", _IResolvable_da3f097b]]]]:
            '''``CfnCrawler.TargetsProperty.JdbcTargets``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html#cfn-glue-crawler-targets-jdbctargets
            '''
            result = self._values.get("jdbc_targets")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCrawler.JdbcTargetProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def s3_targets(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCrawler.S3TargetProperty", _IResolvable_da3f097b]]]]:
            '''``CfnCrawler.TargetsProperty.S3Targets``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html#cfn-glue-crawler-targets-s3targets
            '''
            result = self._values.get("s3_targets")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCrawler.S3TargetProperty", _IResolvable_da3f097b]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TargetsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnCrawlerProps",
    jsii_struct_bases=[],
    name_mapping={
        "role": "role",
        "targets": "targets",
        "classifiers": "classifiers",
        "configuration": "configuration",
        "crawler_security_configuration": "crawlerSecurityConfiguration",
        "database_name": "databaseName",
        "description": "description",
        "name": "name",
        "recrawl_policy": "recrawlPolicy",
        "schedule": "schedule",
        "schema_change_policy": "schemaChangePolicy",
        "table_prefix": "tablePrefix",
        "tags": "tags",
    },
)
class CfnCrawlerProps:
    def __init__(
        self,
        *,
        role: builtins.str,
        targets: typing.Union[CfnCrawler.TargetsProperty, _IResolvable_da3f097b],
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        configuration: typing.Optional[builtins.str] = None,
        crawler_security_configuration: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        recrawl_policy: typing.Optional[typing.Union[CfnCrawler.RecrawlPolicyProperty, _IResolvable_da3f097b]] = None,
        schedule: typing.Optional[typing.Union[CfnCrawler.ScheduleProperty, _IResolvable_da3f097b]] = None,
        schema_change_policy: typing.Optional[typing.Union[CfnCrawler.SchemaChangePolicyProperty, _IResolvable_da3f097b]] = None,
        table_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Crawler``.

        :param role: ``AWS::Glue::Crawler.Role``.
        :param targets: ``AWS::Glue::Crawler.Targets``.
        :param classifiers: ``AWS::Glue::Crawler.Classifiers``.
        :param configuration: ``AWS::Glue::Crawler.Configuration``.
        :param crawler_security_configuration: ``AWS::Glue::Crawler.CrawlerSecurityConfiguration``.
        :param database_name: ``AWS::Glue::Crawler.DatabaseName``.
        :param description: ``AWS::Glue::Crawler.Description``.
        :param name: ``AWS::Glue::Crawler.Name``.
        :param recrawl_policy: ``AWS::Glue::Crawler.RecrawlPolicy``.
        :param schedule: ``AWS::Glue::Crawler.Schedule``.
        :param schema_change_policy: ``AWS::Glue::Crawler.SchemaChangePolicy``.
        :param table_prefix: ``AWS::Glue::Crawler.TablePrefix``.
        :param tags: ``AWS::Glue::Crawler.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role": role,
            "targets": targets,
        }
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if configuration is not None:
            self._values["configuration"] = configuration
        if crawler_security_configuration is not None:
            self._values["crawler_security_configuration"] = crawler_security_configuration
        if database_name is not None:
            self._values["database_name"] = database_name
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if recrawl_policy is not None:
            self._values["recrawl_policy"] = recrawl_policy
        if schedule is not None:
            self._values["schedule"] = schedule
        if schema_change_policy is not None:
            self._values["schema_change_policy"] = schema_change_policy
        if table_prefix is not None:
            self._values["table_prefix"] = table_prefix
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def role(self) -> builtins.str:
        '''``AWS::Glue::Crawler.Role``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-role
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Union[CfnCrawler.TargetsProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::Crawler.Targets``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-targets
        '''
        result = self._values.get("targets")
        assert result is not None, "Required property 'targets' is missing"
        return typing.cast(typing.Union[CfnCrawler.TargetsProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Glue::Crawler.Classifiers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-classifiers
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def configuration(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.Configuration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-configuration
        '''
        result = self._values.get("configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def crawler_security_configuration(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.CrawlerSecurityConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-crawlersecurityconfiguration
        '''
        result = self._values.get("crawler_security_configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.DatabaseName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-databasename
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recrawl_policy(
        self,
    ) -> typing.Optional[typing.Union[CfnCrawler.RecrawlPolicyProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Crawler.RecrawlPolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-recrawlpolicy
        '''
        result = self._values.get("recrawl_policy")
        return typing.cast(typing.Optional[typing.Union[CfnCrawler.RecrawlPolicyProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def schedule(
        self,
    ) -> typing.Optional[typing.Union[CfnCrawler.ScheduleProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Crawler.Schedule``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schedule
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[typing.Union[CfnCrawler.ScheduleProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def schema_change_policy(
        self,
    ) -> typing.Optional[typing.Union[CfnCrawler.SchemaChangePolicyProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Crawler.SchemaChangePolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schemachangepolicy
        '''
        result = self._values.get("schema_change_policy")
        return typing.cast(typing.Optional[typing.Union[CfnCrawler.SchemaChangePolicyProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def table_prefix(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Crawler.TablePrefix``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tableprefix
        '''
        result = self._values.get("table_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Glue::Crawler.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCrawlerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDataCatalogEncryptionSettings(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnDataCatalogEncryptionSettings",
):
    '''A CloudFormation ``AWS::Glue::DataCatalogEncryptionSettings``.

    :cloudformationResource: AWS::Glue::DataCatalogEncryptionSettings
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        catalog_id: builtins.str,
        data_catalog_encryption_settings: typing.Union["CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty", _IResolvable_da3f097b],
    ) -> None:
        '''Create a new ``AWS::Glue::DataCatalogEncryptionSettings``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param catalog_id: ``AWS::Glue::DataCatalogEncryptionSettings.CatalogId``.
        :param data_catalog_encryption_settings: ``AWS::Glue::DataCatalogEncryptionSettings.DataCatalogEncryptionSettings``.
        '''
        props = CfnDataCatalogEncryptionSettingsProps(
            catalog_id=catalog_id,
            data_catalog_encryption_settings=data_catalog_encryption_settings,
        )

        jsii.create(CfnDataCatalogEncryptionSettings, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::DataCatalogEncryptionSettings.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-catalogid
        '''
        return typing.cast(builtins.str, jsii.get(self, "catalogId"))

    @catalog_id.setter
    def catalog_id(self, value: builtins.str) -> None:
        jsii.set(self, "catalogId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataCatalogEncryptionSettings")
    def data_catalog_encryption_settings(
        self,
    ) -> typing.Union["CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::DataCatalogEncryptionSettings.DataCatalogEncryptionSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings
        '''
        return typing.cast(typing.Union["CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty", _IResolvable_da3f097b], jsii.get(self, "dataCatalogEncryptionSettings"))

    @data_catalog_encryption_settings.setter
    def data_catalog_encryption_settings(
        self,
        value: typing.Union["CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "dataCatalogEncryptionSettings", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "kms_key_id": "kmsKeyId",
            "return_connection_password_encrypted": "returnConnectionPasswordEncrypted",
        },
    )
    class ConnectionPasswordEncryptionProperty:
        def __init__(
            self,
            *,
            kms_key_id: typing.Optional[builtins.str] = None,
            return_connection_password_encrypted: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param kms_key_id: ``CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty.KmsKeyId``.
            :param return_connection_password_encrypted: ``CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty.ReturnConnectionPasswordEncrypted``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-connectionpasswordencryption.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if kms_key_id is not None:
                self._values["kms_key_id"] = kms_key_id
            if return_connection_password_encrypted is not None:
                self._values["return_connection_password_encrypted"] = return_connection_password_encrypted

        @builtins.property
        def kms_key_id(self) -> typing.Optional[builtins.str]:
            '''``CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty.KmsKeyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-connectionpasswordencryption.html#cfn-glue-datacatalogencryptionsettings-connectionpasswordencryption-kmskeyid
            '''
            result = self._values.get("kms_key_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def return_connection_password_encrypted(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty.ReturnConnectionPasswordEncrypted``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-connectionpasswordencryption.html#cfn-glue-datacatalogencryptionsettings-connectionpasswordencryption-returnconnectionpasswordencrypted
            '''
            result = self._values.get("return_connection_password_encrypted")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConnectionPasswordEncryptionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "connection_password_encryption": "connectionPasswordEncryption",
            "encryption_at_rest": "encryptionAtRest",
        },
    )
    class DataCatalogEncryptionSettingsProperty:
        def __init__(
            self,
            *,
            connection_password_encryption: typing.Optional[typing.Union["CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty", _IResolvable_da3f097b]] = None,
            encryption_at_rest: typing.Optional[typing.Union["CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param connection_password_encryption: ``CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty.ConnectionPasswordEncryption``.
            :param encryption_at_rest: ``CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty.EncryptionAtRest``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-datacatalogencryptionsettings.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if connection_password_encryption is not None:
                self._values["connection_password_encryption"] = connection_password_encryption
            if encryption_at_rest is not None:
                self._values["encryption_at_rest"] = encryption_at_rest

        @builtins.property
        def connection_password_encryption(
            self,
        ) -> typing.Optional[typing.Union["CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty", _IResolvable_da3f097b]]:
            '''``CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty.ConnectionPasswordEncryption``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings-connectionpasswordencryption
            '''
            result = self._values.get("connection_password_encryption")
            return typing.cast(typing.Optional[typing.Union["CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def encryption_at_rest(
            self,
        ) -> typing.Optional[typing.Union["CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty", _IResolvable_da3f097b]]:
            '''``CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty.EncryptionAtRest``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings-encryptionatrest
            '''
            result = self._values.get("encryption_at_rest")
            return typing.cast(typing.Optional[typing.Union["CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DataCatalogEncryptionSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty",
        jsii_struct_bases=[],
        name_mapping={
            "catalog_encryption_mode": "catalogEncryptionMode",
            "sse_aws_kms_key_id": "sseAwsKmsKeyId",
        },
    )
    class EncryptionAtRestProperty:
        def __init__(
            self,
            *,
            catalog_encryption_mode: typing.Optional[builtins.str] = None,
            sse_aws_kms_key_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param catalog_encryption_mode: ``CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty.CatalogEncryptionMode``.
            :param sse_aws_kms_key_id: ``CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty.SseAwsKmsKeyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-encryptionatrest.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if catalog_encryption_mode is not None:
                self._values["catalog_encryption_mode"] = catalog_encryption_mode
            if sse_aws_kms_key_id is not None:
                self._values["sse_aws_kms_key_id"] = sse_aws_kms_key_id

        @builtins.property
        def catalog_encryption_mode(self) -> typing.Optional[builtins.str]:
            '''``CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty.CatalogEncryptionMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-encryptionatrest.html#cfn-glue-datacatalogencryptionsettings-encryptionatrest-catalogencryptionmode
            '''
            result = self._values.get("catalog_encryption_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def sse_aws_kms_key_id(self) -> typing.Optional[builtins.str]:
            '''``CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty.SseAwsKmsKeyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-encryptionatrest.html#cfn-glue-datacatalogencryptionsettings-encryptionatrest-sseawskmskeyid
            '''
            result = self._values.get("sse_aws_kms_key_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EncryptionAtRestProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnDataCatalogEncryptionSettingsProps",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_id": "catalogId",
        "data_catalog_encryption_settings": "dataCatalogEncryptionSettings",
    },
)
class CfnDataCatalogEncryptionSettingsProps:
    def __init__(
        self,
        *,
        catalog_id: builtins.str,
        data_catalog_encryption_settings: typing.Union[CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty, _IResolvable_da3f097b],
    ) -> None:
        '''Properties for defining a ``AWS::Glue::DataCatalogEncryptionSettings``.

        :param catalog_id: ``AWS::Glue::DataCatalogEncryptionSettings.CatalogId``.
        :param data_catalog_encryption_settings: ``AWS::Glue::DataCatalogEncryptionSettings.DataCatalogEncryptionSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "catalog_id": catalog_id,
            "data_catalog_encryption_settings": data_catalog_encryption_settings,
        }

    @builtins.property
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::DataCatalogEncryptionSettings.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-catalogid
        '''
        result = self._values.get("catalog_id")
        assert result is not None, "Required property 'catalog_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_catalog_encryption_settings(
        self,
    ) -> typing.Union[CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::DataCatalogEncryptionSettings.DataCatalogEncryptionSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings
        '''
        result = self._values.get("data_catalog_encryption_settings")
        assert result is not None, "Required property 'data_catalog_encryption_settings' is missing"
        return typing.cast(typing.Union[CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty, _IResolvable_da3f097b], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDataCatalogEncryptionSettingsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDatabase(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnDatabase",
):
    '''A CloudFormation ``AWS::Glue::Database``.

    :cloudformationResource: AWS::Glue::Database
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        catalog_id: builtins.str,
        database_input: typing.Union["CfnDatabase.DatabaseInputProperty", _IResolvable_da3f097b],
    ) -> None:
        '''Create a new ``AWS::Glue::Database``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param catalog_id: ``AWS::Glue::Database.CatalogId``.
        :param database_input: ``AWS::Glue::Database.DatabaseInput``.
        '''
        props = CfnDatabaseProps(catalog_id=catalog_id, database_input=database_input)

        jsii.create(CfnDatabase, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::Database.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-catalogid
        '''
        return typing.cast(builtins.str, jsii.get(self, "catalogId"))

    @catalog_id.setter
    def catalog_id(self, value: builtins.str) -> None:
        jsii.set(self, "catalogId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(
        self,
    ) -> typing.Union["CfnDatabase.DatabaseInputProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::Database.DatabaseInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-databaseinput
        '''
        return typing.cast(typing.Union["CfnDatabase.DatabaseInputProperty", _IResolvable_da3f097b], jsii.get(self, "databaseInput"))

    @database_input.setter
    def database_input(
        self,
        value: typing.Union["CfnDatabase.DatabaseInputProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "databaseInput", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnDatabase.DataLakePrincipalProperty",
        jsii_struct_bases=[],
        name_mapping={"data_lake_principal_identifier": "dataLakePrincipalIdentifier"},
    )
    class DataLakePrincipalProperty:
        def __init__(
            self,
            *,
            data_lake_principal_identifier: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param data_lake_principal_identifier: ``CfnDatabase.DataLakePrincipalProperty.DataLakePrincipalIdentifier``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-datalakeprincipal.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if data_lake_principal_identifier is not None:
                self._values["data_lake_principal_identifier"] = data_lake_principal_identifier

        @builtins.property
        def data_lake_principal_identifier(self) -> typing.Optional[builtins.str]:
            '''``CfnDatabase.DataLakePrincipalProperty.DataLakePrincipalIdentifier``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-datalakeprincipal.html#cfn-glue-database-datalakeprincipal-datalakeprincipalidentifier
            '''
            result = self._values.get("data_lake_principal_identifier")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DataLakePrincipalProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnDatabase.DatabaseIdentifierProperty",
        jsii_struct_bases=[],
        name_mapping={"catalog_id": "catalogId", "database_name": "databaseName"},
    )
    class DatabaseIdentifierProperty:
        def __init__(
            self,
            *,
            catalog_id: typing.Optional[builtins.str] = None,
            database_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param catalog_id: ``CfnDatabase.DatabaseIdentifierProperty.CatalogId``.
            :param database_name: ``CfnDatabase.DatabaseIdentifierProperty.DatabaseName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseidentifier.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if catalog_id is not None:
                self._values["catalog_id"] = catalog_id
            if database_name is not None:
                self._values["database_name"] = database_name

        @builtins.property
        def catalog_id(self) -> typing.Optional[builtins.str]:
            '''``CfnDatabase.DatabaseIdentifierProperty.CatalogId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseidentifier.html#cfn-glue-database-databaseidentifier-catalogid
            '''
            result = self._values.get("catalog_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def database_name(self) -> typing.Optional[builtins.str]:
            '''``CfnDatabase.DatabaseIdentifierProperty.DatabaseName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseidentifier.html#cfn-glue-database-databaseidentifier-databasename
            '''
            result = self._values.get("database_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DatabaseIdentifierProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnDatabase.DatabaseInputProperty",
        jsii_struct_bases=[],
        name_mapping={
            "create_table_default_permissions": "createTableDefaultPermissions",
            "description": "description",
            "location_uri": "locationUri",
            "name": "name",
            "parameters": "parameters",
            "target_database": "targetDatabase",
        },
    )
    class DatabaseInputProperty:
        def __init__(
            self,
            *,
            create_table_default_permissions: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDatabase.PrincipalPrivilegesProperty", _IResolvable_da3f097b]]]] = None,
            description: typing.Optional[builtins.str] = None,
            location_uri: typing.Optional[builtins.str] = None,
            name: typing.Optional[builtins.str] = None,
            parameters: typing.Any = None,
            target_database: typing.Optional[typing.Union["CfnDatabase.DatabaseIdentifierProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param create_table_default_permissions: ``CfnDatabase.DatabaseInputProperty.CreateTableDefaultPermissions``.
            :param description: ``CfnDatabase.DatabaseInputProperty.Description``.
            :param location_uri: ``CfnDatabase.DatabaseInputProperty.LocationUri``.
            :param name: ``CfnDatabase.DatabaseInputProperty.Name``.
            :param parameters: ``CfnDatabase.DatabaseInputProperty.Parameters``.
            :param target_database: ``CfnDatabase.DatabaseInputProperty.TargetDatabase``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if create_table_default_permissions is not None:
                self._values["create_table_default_permissions"] = create_table_default_permissions
            if description is not None:
                self._values["description"] = description
            if location_uri is not None:
                self._values["location_uri"] = location_uri
            if name is not None:
                self._values["name"] = name
            if parameters is not None:
                self._values["parameters"] = parameters
            if target_database is not None:
                self._values["target_database"] = target_database

        @builtins.property
        def create_table_default_permissions(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDatabase.PrincipalPrivilegesProperty", _IResolvable_da3f097b]]]]:
            '''``CfnDatabase.DatabaseInputProperty.CreateTableDefaultPermissions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-createtabledefaultpermissions
            '''
            result = self._values.get("create_table_default_permissions")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDatabase.PrincipalPrivilegesProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            '''``CfnDatabase.DatabaseInputProperty.Description``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-description
            '''
            result = self._values.get("description")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def location_uri(self) -> typing.Optional[builtins.str]:
            '''``CfnDatabase.DatabaseInputProperty.LocationUri``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-locationuri
            '''
            result = self._values.get("location_uri")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnDatabase.DatabaseInputProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def parameters(self) -> typing.Any:
            '''``CfnDatabase.DatabaseInputProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Any, result)

        @builtins.property
        def target_database(
            self,
        ) -> typing.Optional[typing.Union["CfnDatabase.DatabaseIdentifierProperty", _IResolvable_da3f097b]]:
            '''``CfnDatabase.DatabaseInputProperty.TargetDatabase``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-targetdatabase
            '''
            result = self._values.get("target_database")
            return typing.cast(typing.Optional[typing.Union["CfnDatabase.DatabaseIdentifierProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DatabaseInputProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnDatabase.PrincipalPrivilegesProperty",
        jsii_struct_bases=[],
        name_mapping={"permissions": "permissions", "principal": "principal"},
    )
    class PrincipalPrivilegesProperty:
        def __init__(
            self,
            *,
            permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
            principal: typing.Optional[typing.Union["CfnDatabase.DataLakePrincipalProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param permissions: ``CfnDatabase.PrincipalPrivilegesProperty.Permissions``.
            :param principal: ``CfnDatabase.PrincipalPrivilegesProperty.Principal``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-principalprivileges.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if permissions is not None:
                self._values["permissions"] = permissions
            if principal is not None:
                self._values["principal"] = principal

        @builtins.property
        def permissions(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnDatabase.PrincipalPrivilegesProperty.Permissions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-principalprivileges.html#cfn-glue-database-principalprivileges-permissions
            '''
            result = self._values.get("permissions")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def principal(
            self,
        ) -> typing.Optional[typing.Union["CfnDatabase.DataLakePrincipalProperty", _IResolvable_da3f097b]]:
            '''``CfnDatabase.PrincipalPrivilegesProperty.Principal``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-principalprivileges.html#cfn-glue-database-principalprivileges-principal
            '''
            result = self._values.get("principal")
            return typing.cast(typing.Optional[typing.Union["CfnDatabase.DataLakePrincipalProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PrincipalPrivilegesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnDatabaseProps",
    jsii_struct_bases=[],
    name_mapping={"catalog_id": "catalogId", "database_input": "databaseInput"},
)
class CfnDatabaseProps:
    def __init__(
        self,
        *,
        catalog_id: builtins.str,
        database_input: typing.Union[CfnDatabase.DatabaseInputProperty, _IResolvable_da3f097b],
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Database``.

        :param catalog_id: ``AWS::Glue::Database.CatalogId``.
        :param database_input: ``AWS::Glue::Database.DatabaseInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "catalog_id": catalog_id,
            "database_input": database_input,
        }

    @builtins.property
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::Database.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-catalogid
        '''
        result = self._values.get("catalog_id")
        assert result is not None, "Required property 'catalog_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_input(
        self,
    ) -> typing.Union[CfnDatabase.DatabaseInputProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::Database.DatabaseInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-databaseinput
        '''
        result = self._values.get("database_input")
        assert result is not None, "Required property 'database_input' is missing"
        return typing.cast(typing.Union[CfnDatabase.DatabaseInputProperty, _IResolvable_da3f097b], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDevEndpoint(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnDevEndpoint",
):
    '''A CloudFormation ``AWS::Glue::DevEndpoint``.

    :cloudformationResource: AWS::Glue::DevEndpoint
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        role_arn: builtins.str,
        arguments: typing.Any = None,
        endpoint_name: typing.Optional[builtins.str] = None,
        extra_jars_s3_path: typing.Optional[builtins.str] = None,
        extra_python_libs_s3_path: typing.Optional[builtins.str] = None,
        glue_version: typing.Optional[builtins.str] = None,
        number_of_nodes: typing.Optional[jsii.Number] = None,
        number_of_workers: typing.Optional[jsii.Number] = None,
        public_key: typing.Optional[builtins.str] = None,
        public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_configuration: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
        worker_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Glue::DevEndpoint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param role_arn: ``AWS::Glue::DevEndpoint.RoleArn``.
        :param arguments: ``AWS::Glue::DevEndpoint.Arguments``.
        :param endpoint_name: ``AWS::Glue::DevEndpoint.EndpointName``.
        :param extra_jars_s3_path: ``AWS::Glue::DevEndpoint.ExtraJarsS3Path``.
        :param extra_python_libs_s3_path: ``AWS::Glue::DevEndpoint.ExtraPythonLibsS3Path``.
        :param glue_version: ``AWS::Glue::DevEndpoint.GlueVersion``.
        :param number_of_nodes: ``AWS::Glue::DevEndpoint.NumberOfNodes``.
        :param number_of_workers: ``AWS::Glue::DevEndpoint.NumberOfWorkers``.
        :param public_key: ``AWS::Glue::DevEndpoint.PublicKey``.
        :param public_keys: ``AWS::Glue::DevEndpoint.PublicKeys``.
        :param security_configuration: ``AWS::Glue::DevEndpoint.SecurityConfiguration``.
        :param security_group_ids: ``AWS::Glue::DevEndpoint.SecurityGroupIds``.
        :param subnet_id: ``AWS::Glue::DevEndpoint.SubnetId``.
        :param tags: ``AWS::Glue::DevEndpoint.Tags``.
        :param worker_type: ``AWS::Glue::DevEndpoint.WorkerType``.
        '''
        props = CfnDevEndpointProps(
            role_arn=role_arn,
            arguments=arguments,
            endpoint_name=endpoint_name,
            extra_jars_s3_path=extra_jars_s3_path,
            extra_python_libs_s3_path=extra_python_libs_s3_path,
            glue_version=glue_version,
            number_of_nodes=number_of_nodes,
            number_of_workers=number_of_workers,
            public_key=public_key,
            public_keys=public_keys,
            security_configuration=security_configuration,
            security_group_ids=security_group_ids,
            subnet_id=subnet_id,
            tags=tags,
            worker_type=worker_type,
        )

        jsii.create(CfnDevEndpoint, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Glue::DevEndpoint.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arguments")
    def arguments(self) -> typing.Any:
        '''``AWS::Glue::DevEndpoint.Arguments``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-arguments
        '''
        return typing.cast(typing.Any, jsii.get(self, "arguments"))

    @arguments.setter
    def arguments(self, value: typing.Any) -> None:
        jsii.set(self, "arguments", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''``AWS::Glue::DevEndpoint.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-rolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.EndpointName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-endpointname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointName"))

    @endpoint_name.setter
    def endpoint_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "endpointName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extraJarsS3Path")
    def extra_jars_s3_path(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.ExtraJarsS3Path``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrajarss3path
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "extraJarsS3Path"))

    @extra_jars_s3_path.setter
    def extra_jars_s3_path(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "extraJarsS3Path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extraPythonLibsS3Path")
    def extra_python_libs_s3_path(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.ExtraPythonLibsS3Path``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrapythonlibss3path
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "extraPythonLibsS3Path"))

    @extra_python_libs_s3_path.setter
    def extra_python_libs_s3_path(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "extraPythonLibsS3Path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="glueVersion")
    def glue_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.GlueVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-glueversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "glueVersion"))

    @glue_version.setter
    def glue_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "glueVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfNodes")
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::DevEndpoint.NumberOfNodes``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-numberofnodes
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfNodes"))

    @number_of_nodes.setter
    def number_of_nodes(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "numberOfNodes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfWorkers")
    def number_of_workers(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::DevEndpoint.NumberOfWorkers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-numberofworkers
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfWorkers"))

    @number_of_workers.setter
    def number_of_workers(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "numberOfWorkers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.PublicKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-publickey
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKey"))

    @public_key.setter
    def public_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "publicKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeys")
    def public_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Glue::DevEndpoint.PublicKeys``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-publickeys
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "publicKeys"))

    @public_keys.setter
    def public_keys(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        jsii.set(self, "publicKeys", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityConfiguration")
    def security_configuration(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.SecurityConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securityconfiguration
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityConfiguration"))

    @security_configuration.setter
    def security_configuration(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "securityConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Glue::DevEndpoint.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securitygroupids
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.SubnetId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-subnetid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "subnetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerType")
    def worker_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.WorkerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-workertype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workerType"))

    @worker_type.setter
    def worker_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "workerType", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnDevEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "arguments": "arguments",
        "endpoint_name": "endpointName",
        "extra_jars_s3_path": "extraJarsS3Path",
        "extra_python_libs_s3_path": "extraPythonLibsS3Path",
        "glue_version": "glueVersion",
        "number_of_nodes": "numberOfNodes",
        "number_of_workers": "numberOfWorkers",
        "public_key": "publicKey",
        "public_keys": "publicKeys",
        "security_configuration": "securityConfiguration",
        "security_group_ids": "securityGroupIds",
        "subnet_id": "subnetId",
        "tags": "tags",
        "worker_type": "workerType",
    },
)
class CfnDevEndpointProps:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        arguments: typing.Any = None,
        endpoint_name: typing.Optional[builtins.str] = None,
        extra_jars_s3_path: typing.Optional[builtins.str] = None,
        extra_python_libs_s3_path: typing.Optional[builtins.str] = None,
        glue_version: typing.Optional[builtins.str] = None,
        number_of_nodes: typing.Optional[jsii.Number] = None,
        number_of_workers: typing.Optional[jsii.Number] = None,
        public_key: typing.Optional[builtins.str] = None,
        public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_configuration: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
        worker_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::DevEndpoint``.

        :param role_arn: ``AWS::Glue::DevEndpoint.RoleArn``.
        :param arguments: ``AWS::Glue::DevEndpoint.Arguments``.
        :param endpoint_name: ``AWS::Glue::DevEndpoint.EndpointName``.
        :param extra_jars_s3_path: ``AWS::Glue::DevEndpoint.ExtraJarsS3Path``.
        :param extra_python_libs_s3_path: ``AWS::Glue::DevEndpoint.ExtraPythonLibsS3Path``.
        :param glue_version: ``AWS::Glue::DevEndpoint.GlueVersion``.
        :param number_of_nodes: ``AWS::Glue::DevEndpoint.NumberOfNodes``.
        :param number_of_workers: ``AWS::Glue::DevEndpoint.NumberOfWorkers``.
        :param public_key: ``AWS::Glue::DevEndpoint.PublicKey``.
        :param public_keys: ``AWS::Glue::DevEndpoint.PublicKeys``.
        :param security_configuration: ``AWS::Glue::DevEndpoint.SecurityConfiguration``.
        :param security_group_ids: ``AWS::Glue::DevEndpoint.SecurityGroupIds``.
        :param subnet_id: ``AWS::Glue::DevEndpoint.SubnetId``.
        :param tags: ``AWS::Glue::DevEndpoint.Tags``.
        :param worker_type: ``AWS::Glue::DevEndpoint.WorkerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
        }
        if arguments is not None:
            self._values["arguments"] = arguments
        if endpoint_name is not None:
            self._values["endpoint_name"] = endpoint_name
        if extra_jars_s3_path is not None:
            self._values["extra_jars_s3_path"] = extra_jars_s3_path
        if extra_python_libs_s3_path is not None:
            self._values["extra_python_libs_s3_path"] = extra_python_libs_s3_path
        if glue_version is not None:
            self._values["glue_version"] = glue_version
        if number_of_nodes is not None:
            self._values["number_of_nodes"] = number_of_nodes
        if number_of_workers is not None:
            self._values["number_of_workers"] = number_of_workers
        if public_key is not None:
            self._values["public_key"] = public_key
        if public_keys is not None:
            self._values["public_keys"] = public_keys
        if security_configuration is not None:
            self._values["security_configuration"] = security_configuration
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if subnet_id is not None:
            self._values["subnet_id"] = subnet_id
        if tags is not None:
            self._values["tags"] = tags
        if worker_type is not None:
            self._values["worker_type"] = worker_type

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''``AWS::Glue::DevEndpoint.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-rolearn
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def arguments(self) -> typing.Any:
        '''``AWS::Glue::DevEndpoint.Arguments``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-arguments
        '''
        result = self._values.get("arguments")
        return typing.cast(typing.Any, result)

    @builtins.property
    def endpoint_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.EndpointName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-endpointname
        '''
        result = self._values.get("endpoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extra_jars_s3_path(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.ExtraJarsS3Path``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrajarss3path
        '''
        result = self._values.get("extra_jars_s3_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extra_python_libs_s3_path(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.ExtraPythonLibsS3Path``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrapythonlibss3path
        '''
        result = self._values.get("extra_python_libs_s3_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def glue_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.GlueVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-glueversion
        '''
        result = self._values.get("glue_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::DevEndpoint.NumberOfNodes``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-numberofnodes
        '''
        result = self._values.get("number_of_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number_of_workers(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::DevEndpoint.NumberOfWorkers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-numberofworkers
        '''
        result = self._values.get("number_of_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def public_key(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.PublicKey``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-publickey
        '''
        result = self._values.get("public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Glue::DevEndpoint.PublicKeys``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-publickeys
        '''
        result = self._values.get("public_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def security_configuration(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.SecurityConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securityconfiguration
        '''
        result = self._values.get("security_configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::Glue::DevEndpoint.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securitygroupids
        '''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subnet_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.SubnetId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-subnetid
        '''
        result = self._values.get("subnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Glue::DevEndpoint.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    @builtins.property
    def worker_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::DevEndpoint.WorkerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-workertype
        '''
        result = self._values.get("worker_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDevEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnJob(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnJob",
):
    '''A CloudFormation ``AWS::Glue::Job``.

    :cloudformationResource: AWS::Glue::Job
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        command: typing.Union["CfnJob.JobCommandProperty", _IResolvable_da3f097b],
        role: builtins.str,
        allocated_capacity: typing.Optional[jsii.Number] = None,
        connections: typing.Optional[typing.Union["CfnJob.ConnectionsListProperty", _IResolvable_da3f097b]] = None,
        default_arguments: typing.Any = None,
        description: typing.Optional[builtins.str] = None,
        execution_property: typing.Optional[typing.Union["CfnJob.ExecutionPropertyProperty", _IResolvable_da3f097b]] = None,
        glue_version: typing.Optional[builtins.str] = None,
        log_uri: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        notification_property: typing.Optional[typing.Union["CfnJob.NotificationPropertyProperty", _IResolvable_da3f097b]] = None,
        number_of_workers: typing.Optional[jsii.Number] = None,
        security_configuration: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
        timeout: typing.Optional[jsii.Number] = None,
        worker_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Glue::Job``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param command: ``AWS::Glue::Job.Command``.
        :param role: ``AWS::Glue::Job.Role``.
        :param allocated_capacity: ``AWS::Glue::Job.AllocatedCapacity``.
        :param connections: ``AWS::Glue::Job.Connections``.
        :param default_arguments: ``AWS::Glue::Job.DefaultArguments``.
        :param description: ``AWS::Glue::Job.Description``.
        :param execution_property: ``AWS::Glue::Job.ExecutionProperty``.
        :param glue_version: ``AWS::Glue::Job.GlueVersion``.
        :param log_uri: ``AWS::Glue::Job.LogUri``.
        :param max_capacity: ``AWS::Glue::Job.MaxCapacity``.
        :param max_retries: ``AWS::Glue::Job.MaxRetries``.
        :param name: ``AWS::Glue::Job.Name``.
        :param notification_property: ``AWS::Glue::Job.NotificationProperty``.
        :param number_of_workers: ``AWS::Glue::Job.NumberOfWorkers``.
        :param security_configuration: ``AWS::Glue::Job.SecurityConfiguration``.
        :param tags: ``AWS::Glue::Job.Tags``.
        :param timeout: ``AWS::Glue::Job.Timeout``.
        :param worker_type: ``AWS::Glue::Job.WorkerType``.
        '''
        props = CfnJobProps(
            command=command,
            role=role,
            allocated_capacity=allocated_capacity,
            connections=connections,
            default_arguments=default_arguments,
            description=description,
            execution_property=execution_property,
            glue_version=glue_version,
            log_uri=log_uri,
            max_capacity=max_capacity,
            max_retries=max_retries,
            name=name,
            notification_property=notification_property,
            number_of_workers=number_of_workers,
            security_configuration=security_configuration,
            tags=tags,
            timeout=timeout,
            worker_type=worker_type,
        )

        jsii.create(CfnJob, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Glue::Job.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="command")
    def command(
        self,
    ) -> typing.Union["CfnJob.JobCommandProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::Job.Command``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-command
        '''
        return typing.cast(typing.Union["CfnJob.JobCommandProperty", _IResolvable_da3f097b], jsii.get(self, "command"))

    @command.setter
    def command(
        self,
        value: typing.Union["CfnJob.JobCommandProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "command", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultArguments")
    def default_arguments(self) -> typing.Any:
        '''``AWS::Glue::Job.DefaultArguments``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-defaultarguments
        '''
        return typing.cast(typing.Any, jsii.get(self, "defaultArguments"))

    @default_arguments.setter
    def default_arguments(self, value: typing.Any) -> None:
        jsii.set(self, "defaultArguments", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        '''``AWS::Glue::Job.Role``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-role
        '''
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocatedCapacity")
    def allocated_capacity(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.AllocatedCapacity``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-allocatedcapacity
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allocatedCapacity"))

    @allocated_capacity.setter
    def allocated_capacity(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "allocatedCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(
        self,
    ) -> typing.Optional[typing.Union["CfnJob.ConnectionsListProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Job.Connections``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-connections
        '''
        return typing.cast(typing.Optional[typing.Union["CfnJob.ConnectionsListProperty", _IResolvable_da3f097b]], jsii.get(self, "connections"))

    @connections.setter
    def connections(
        self,
        value: typing.Optional[typing.Union["CfnJob.ConnectionsListProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "connections", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionProperty")
    def execution_property(
        self,
    ) -> typing.Optional[typing.Union["CfnJob.ExecutionPropertyProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Job.ExecutionProperty``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-executionproperty
        '''
        return typing.cast(typing.Optional[typing.Union["CfnJob.ExecutionPropertyProperty", _IResolvable_da3f097b]], jsii.get(self, "executionProperty"))

    @execution_property.setter
    def execution_property(
        self,
        value: typing.Optional[typing.Union["CfnJob.ExecutionPropertyProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "executionProperty", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="glueVersion")
    def glue_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.GlueVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-glueversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "glueVersion"))

    @glue_version.setter
    def glue_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "glueVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logUri")
    def log_uri(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.LogUri``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-loguri
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logUri"))

    @log_uri.setter
    def log_uri(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "logUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxCapacity")
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.MaxCapacity``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-maxcapacity
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCapacity"))

    @max_capacity.setter
    def max_capacity(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "maxCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetries")
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.MaxRetries``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-maxretries
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetries"))

    @max_retries.setter
    def max_retries(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "maxRetries", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationProperty")
    def notification_property(
        self,
    ) -> typing.Optional[typing.Union["CfnJob.NotificationPropertyProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Job.NotificationProperty``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-notificationproperty
        '''
        return typing.cast(typing.Optional[typing.Union["CfnJob.NotificationPropertyProperty", _IResolvable_da3f097b]], jsii.get(self, "notificationProperty"))

    @notification_property.setter
    def notification_property(
        self,
        value: typing.Optional[typing.Union["CfnJob.NotificationPropertyProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "notificationProperty", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfWorkers")
    def number_of_workers(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.NumberOfWorkers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-numberofworkers
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfWorkers"))

    @number_of_workers.setter
    def number_of_workers(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "numberOfWorkers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityConfiguration")
    def security_configuration(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.SecurityConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-securityconfiguration
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityConfiguration"))

    @security_configuration.setter
    def security_configuration(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "securityConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.Timeout``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-timeout
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "timeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerType")
    def worker_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.WorkerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-workertype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workerType"))

    @worker_type.setter
    def worker_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "workerType", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnJob.ConnectionsListProperty",
        jsii_struct_bases=[],
        name_mapping={"connections": "connections"},
    )
    class ConnectionsListProperty:
        def __init__(
            self,
            *,
            connections: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''
            :param connections: ``CfnJob.ConnectionsListProperty.Connections``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-connectionslist.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if connections is not None:
                self._values["connections"] = connections

        @builtins.property
        def connections(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnJob.ConnectionsListProperty.Connections``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-connectionslist.html#cfn-glue-job-connectionslist-connections
            '''
            result = self._values.get("connections")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConnectionsListProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnJob.ExecutionPropertyProperty",
        jsii_struct_bases=[],
        name_mapping={"max_concurrent_runs": "maxConcurrentRuns"},
    )
    class ExecutionPropertyProperty:
        def __init__(
            self,
            *,
            max_concurrent_runs: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param max_concurrent_runs: ``CfnJob.ExecutionPropertyProperty.MaxConcurrentRuns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-executionproperty.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if max_concurrent_runs is not None:
                self._values["max_concurrent_runs"] = max_concurrent_runs

        @builtins.property
        def max_concurrent_runs(self) -> typing.Optional[jsii.Number]:
            '''``CfnJob.ExecutionPropertyProperty.MaxConcurrentRuns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-executionproperty.html#cfn-glue-job-executionproperty-maxconcurrentruns
            '''
            result = self._values.get("max_concurrent_runs")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ExecutionPropertyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnJob.JobCommandProperty",
        jsii_struct_bases=[],
        name_mapping={
            "name": "name",
            "python_version": "pythonVersion",
            "script_location": "scriptLocation",
        },
    )
    class JobCommandProperty:
        def __init__(
            self,
            *,
            name: typing.Optional[builtins.str] = None,
            python_version: typing.Optional[builtins.str] = None,
            script_location: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param name: ``CfnJob.JobCommandProperty.Name``.
            :param python_version: ``CfnJob.JobCommandProperty.PythonVersion``.
            :param script_location: ``CfnJob.JobCommandProperty.ScriptLocation``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if name is not None:
                self._values["name"] = name
            if python_version is not None:
                self._values["python_version"] = python_version
            if script_location is not None:
                self._values["script_location"] = script_location

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnJob.JobCommandProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html#cfn-glue-job-jobcommand-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def python_version(self) -> typing.Optional[builtins.str]:
            '''``CfnJob.JobCommandProperty.PythonVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html#cfn-glue-job-jobcommand-pythonversion
            '''
            result = self._values.get("python_version")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def script_location(self) -> typing.Optional[builtins.str]:
            '''``CfnJob.JobCommandProperty.ScriptLocation``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html#cfn-glue-job-jobcommand-scriptlocation
            '''
            result = self._values.get("script_location")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "JobCommandProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnJob.NotificationPropertyProperty",
        jsii_struct_bases=[],
        name_mapping={"notify_delay_after": "notifyDelayAfter"},
    )
    class NotificationPropertyProperty:
        def __init__(
            self,
            *,
            notify_delay_after: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param notify_delay_after: ``CfnJob.NotificationPropertyProperty.NotifyDelayAfter``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-notificationproperty.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if notify_delay_after is not None:
                self._values["notify_delay_after"] = notify_delay_after

        @builtins.property
        def notify_delay_after(self) -> typing.Optional[jsii.Number]:
            '''``CfnJob.NotificationPropertyProperty.NotifyDelayAfter``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-notificationproperty.html#cfn-glue-job-notificationproperty-notifydelayafter
            '''
            result = self._values.get("notify_delay_after")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "NotificationPropertyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnJobProps",
    jsii_struct_bases=[],
    name_mapping={
        "command": "command",
        "role": "role",
        "allocated_capacity": "allocatedCapacity",
        "connections": "connections",
        "default_arguments": "defaultArguments",
        "description": "description",
        "execution_property": "executionProperty",
        "glue_version": "glueVersion",
        "log_uri": "logUri",
        "max_capacity": "maxCapacity",
        "max_retries": "maxRetries",
        "name": "name",
        "notification_property": "notificationProperty",
        "number_of_workers": "numberOfWorkers",
        "security_configuration": "securityConfiguration",
        "tags": "tags",
        "timeout": "timeout",
        "worker_type": "workerType",
    },
)
class CfnJobProps:
    def __init__(
        self,
        *,
        command: typing.Union[CfnJob.JobCommandProperty, _IResolvable_da3f097b],
        role: builtins.str,
        allocated_capacity: typing.Optional[jsii.Number] = None,
        connections: typing.Optional[typing.Union[CfnJob.ConnectionsListProperty, _IResolvable_da3f097b]] = None,
        default_arguments: typing.Any = None,
        description: typing.Optional[builtins.str] = None,
        execution_property: typing.Optional[typing.Union[CfnJob.ExecutionPropertyProperty, _IResolvable_da3f097b]] = None,
        glue_version: typing.Optional[builtins.str] = None,
        log_uri: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        notification_property: typing.Optional[typing.Union[CfnJob.NotificationPropertyProperty, _IResolvable_da3f097b]] = None,
        number_of_workers: typing.Optional[jsii.Number] = None,
        security_configuration: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
        timeout: typing.Optional[jsii.Number] = None,
        worker_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Job``.

        :param command: ``AWS::Glue::Job.Command``.
        :param role: ``AWS::Glue::Job.Role``.
        :param allocated_capacity: ``AWS::Glue::Job.AllocatedCapacity``.
        :param connections: ``AWS::Glue::Job.Connections``.
        :param default_arguments: ``AWS::Glue::Job.DefaultArguments``.
        :param description: ``AWS::Glue::Job.Description``.
        :param execution_property: ``AWS::Glue::Job.ExecutionProperty``.
        :param glue_version: ``AWS::Glue::Job.GlueVersion``.
        :param log_uri: ``AWS::Glue::Job.LogUri``.
        :param max_capacity: ``AWS::Glue::Job.MaxCapacity``.
        :param max_retries: ``AWS::Glue::Job.MaxRetries``.
        :param name: ``AWS::Glue::Job.Name``.
        :param notification_property: ``AWS::Glue::Job.NotificationProperty``.
        :param number_of_workers: ``AWS::Glue::Job.NumberOfWorkers``.
        :param security_configuration: ``AWS::Glue::Job.SecurityConfiguration``.
        :param tags: ``AWS::Glue::Job.Tags``.
        :param timeout: ``AWS::Glue::Job.Timeout``.
        :param worker_type: ``AWS::Glue::Job.WorkerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "command": command,
            "role": role,
        }
        if allocated_capacity is not None:
            self._values["allocated_capacity"] = allocated_capacity
        if connections is not None:
            self._values["connections"] = connections
        if default_arguments is not None:
            self._values["default_arguments"] = default_arguments
        if description is not None:
            self._values["description"] = description
        if execution_property is not None:
            self._values["execution_property"] = execution_property
        if glue_version is not None:
            self._values["glue_version"] = glue_version
        if log_uri is not None:
            self._values["log_uri"] = log_uri
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if name is not None:
            self._values["name"] = name
        if notification_property is not None:
            self._values["notification_property"] = notification_property
        if number_of_workers is not None:
            self._values["number_of_workers"] = number_of_workers
        if security_configuration is not None:
            self._values["security_configuration"] = security_configuration
        if tags is not None:
            self._values["tags"] = tags
        if timeout is not None:
            self._values["timeout"] = timeout
        if worker_type is not None:
            self._values["worker_type"] = worker_type

    @builtins.property
    def command(self) -> typing.Union[CfnJob.JobCommandProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::Job.Command``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-command
        '''
        result = self._values.get("command")
        assert result is not None, "Required property 'command' is missing"
        return typing.cast(typing.Union[CfnJob.JobCommandProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def role(self) -> builtins.str:
        '''``AWS::Glue::Job.Role``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-role
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocated_capacity(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.AllocatedCapacity``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-allocatedcapacity
        '''
        result = self._values.get("allocated_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connections(
        self,
    ) -> typing.Optional[typing.Union[CfnJob.ConnectionsListProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Job.Connections``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-connections
        '''
        result = self._values.get("connections")
        return typing.cast(typing.Optional[typing.Union[CfnJob.ConnectionsListProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def default_arguments(self) -> typing.Any:
        '''``AWS::Glue::Job.DefaultArguments``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-defaultarguments
        '''
        result = self._values.get("default_arguments")
        return typing.cast(typing.Any, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_property(
        self,
    ) -> typing.Optional[typing.Union[CfnJob.ExecutionPropertyProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Job.ExecutionProperty``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-executionproperty
        '''
        result = self._values.get("execution_property")
        return typing.cast(typing.Optional[typing.Union[CfnJob.ExecutionPropertyProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def glue_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.GlueVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-glueversion
        '''
        result = self._values.get("glue_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_uri(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.LogUri``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-loguri
        '''
        result = self._values.get("log_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.MaxCapacity``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-maxcapacity
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.MaxRetries``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-maxretries
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_property(
        self,
    ) -> typing.Optional[typing.Union[CfnJob.NotificationPropertyProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Job.NotificationProperty``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-notificationproperty
        '''
        result = self._values.get("notification_property")
        return typing.cast(typing.Optional[typing.Union[CfnJob.NotificationPropertyProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def number_of_workers(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.NumberOfWorkers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-numberofworkers
        '''
        result = self._values.get("number_of_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def security_configuration(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.SecurityConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-securityconfiguration
        '''
        result = self._values.get("security_configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Glue::Job.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::Job.Timeout``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-timeout
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def worker_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Job.WorkerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-workertype
        '''
        result = self._values.get("worker_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnJobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnMLTransform(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnMLTransform",
):
    '''A CloudFormation ``AWS::Glue::MLTransform``.

    :cloudformationResource: AWS::Glue::MLTransform
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        input_record_tables: typing.Union["CfnMLTransform.InputRecordTablesProperty", _IResolvable_da3f097b],
        role: builtins.str,
        transform_parameters: typing.Union["CfnMLTransform.TransformParametersProperty", _IResolvable_da3f097b],
        description: typing.Optional[builtins.str] = None,
        glue_version: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        number_of_workers: typing.Optional[jsii.Number] = None,
        tags: typing.Any = None,
        timeout: typing.Optional[jsii.Number] = None,
        transform_encryption: typing.Optional[typing.Union["CfnMLTransform.TransformEncryptionProperty", _IResolvable_da3f097b]] = None,
        worker_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Glue::MLTransform``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param input_record_tables: ``AWS::Glue::MLTransform.InputRecordTables``.
        :param role: ``AWS::Glue::MLTransform.Role``.
        :param transform_parameters: ``AWS::Glue::MLTransform.TransformParameters``.
        :param description: ``AWS::Glue::MLTransform.Description``.
        :param glue_version: ``AWS::Glue::MLTransform.GlueVersion``.
        :param max_capacity: ``AWS::Glue::MLTransform.MaxCapacity``.
        :param max_retries: ``AWS::Glue::MLTransform.MaxRetries``.
        :param name: ``AWS::Glue::MLTransform.Name``.
        :param number_of_workers: ``AWS::Glue::MLTransform.NumberOfWorkers``.
        :param tags: ``AWS::Glue::MLTransform.Tags``.
        :param timeout: ``AWS::Glue::MLTransform.Timeout``.
        :param transform_encryption: ``AWS::Glue::MLTransform.TransformEncryption``.
        :param worker_type: ``AWS::Glue::MLTransform.WorkerType``.
        '''
        props = CfnMLTransformProps(
            input_record_tables=input_record_tables,
            role=role,
            transform_parameters=transform_parameters,
            description=description,
            glue_version=glue_version,
            max_capacity=max_capacity,
            max_retries=max_retries,
            name=name,
            number_of_workers=number_of_workers,
            tags=tags,
            timeout=timeout,
            transform_encryption=transform_encryption,
            worker_type=worker_type,
        )

        jsii.create(CfnMLTransform, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Glue::MLTransform.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputRecordTables")
    def input_record_tables(
        self,
    ) -> typing.Union["CfnMLTransform.InputRecordTablesProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::MLTransform.InputRecordTables``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-inputrecordtables
        '''
        return typing.cast(typing.Union["CfnMLTransform.InputRecordTablesProperty", _IResolvable_da3f097b], jsii.get(self, "inputRecordTables"))

    @input_record_tables.setter
    def input_record_tables(
        self,
        value: typing.Union["CfnMLTransform.InputRecordTablesProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "inputRecordTables", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        '''``AWS::Glue::MLTransform.Role``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-role
        '''
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transformParameters")
    def transform_parameters(
        self,
    ) -> typing.Union["CfnMLTransform.TransformParametersProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::MLTransform.TransformParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-transformparameters
        '''
        return typing.cast(typing.Union["CfnMLTransform.TransformParametersProperty", _IResolvable_da3f097b], jsii.get(self, "transformParameters"))

    @transform_parameters.setter
    def transform_parameters(
        self,
        value: typing.Union["CfnMLTransform.TransformParametersProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "transformParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::MLTransform.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="glueVersion")
    def glue_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::MLTransform.GlueVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-glueversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "glueVersion"))

    @glue_version.setter
    def glue_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "glueVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxCapacity")
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::MLTransform.MaxCapacity``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-maxcapacity
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCapacity"))

    @max_capacity.setter
    def max_capacity(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "maxCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetries")
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::MLTransform.MaxRetries``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-maxretries
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetries"))

    @max_retries.setter
    def max_retries(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "maxRetries", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::MLTransform.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfWorkers")
    def number_of_workers(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::MLTransform.NumberOfWorkers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-numberofworkers
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfWorkers"))

    @number_of_workers.setter
    def number_of_workers(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "numberOfWorkers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::MLTransform.Timeout``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-timeout
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "timeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transformEncryption")
    def transform_encryption(
        self,
    ) -> typing.Optional[typing.Union["CfnMLTransform.TransformEncryptionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::MLTransform.TransformEncryption``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-transformencryption
        '''
        return typing.cast(typing.Optional[typing.Union["CfnMLTransform.TransformEncryptionProperty", _IResolvable_da3f097b]], jsii.get(self, "transformEncryption"))

    @transform_encryption.setter
    def transform_encryption(
        self,
        value: typing.Optional[typing.Union["CfnMLTransform.TransformEncryptionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "transformEncryption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerType")
    def worker_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::MLTransform.WorkerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-workertype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workerType"))

    @worker_type.setter
    def worker_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "workerType", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnMLTransform.FindMatchesParametersProperty",
        jsii_struct_bases=[],
        name_mapping={
            "primary_key_column_name": "primaryKeyColumnName",
            "accuracy_cost_tradeoff": "accuracyCostTradeoff",
            "enforce_provided_labels": "enforceProvidedLabels",
            "precision_recall_tradeoff": "precisionRecallTradeoff",
        },
    )
    class FindMatchesParametersProperty:
        def __init__(
            self,
            *,
            primary_key_column_name: builtins.str,
            accuracy_cost_tradeoff: typing.Optional[jsii.Number] = None,
            enforce_provided_labels: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            precision_recall_tradeoff: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param primary_key_column_name: ``CfnMLTransform.FindMatchesParametersProperty.PrimaryKeyColumnName``.
            :param accuracy_cost_tradeoff: ``CfnMLTransform.FindMatchesParametersProperty.AccuracyCostTradeoff``.
            :param enforce_provided_labels: ``CfnMLTransform.FindMatchesParametersProperty.EnforceProvidedLabels``.
            :param precision_recall_tradeoff: ``CfnMLTransform.FindMatchesParametersProperty.PrecisionRecallTradeoff``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformparameters-findmatchesparameters.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "primary_key_column_name": primary_key_column_name,
            }
            if accuracy_cost_tradeoff is not None:
                self._values["accuracy_cost_tradeoff"] = accuracy_cost_tradeoff
            if enforce_provided_labels is not None:
                self._values["enforce_provided_labels"] = enforce_provided_labels
            if precision_recall_tradeoff is not None:
                self._values["precision_recall_tradeoff"] = precision_recall_tradeoff

        @builtins.property
        def primary_key_column_name(self) -> builtins.str:
            '''``CfnMLTransform.FindMatchesParametersProperty.PrimaryKeyColumnName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformparameters-findmatchesparameters.html#cfn-glue-mltransform-transformparameters-findmatchesparameters-primarykeycolumnname
            '''
            result = self._values.get("primary_key_column_name")
            assert result is not None, "Required property 'primary_key_column_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def accuracy_cost_tradeoff(self) -> typing.Optional[jsii.Number]:
            '''``CfnMLTransform.FindMatchesParametersProperty.AccuracyCostTradeoff``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformparameters-findmatchesparameters.html#cfn-glue-mltransform-transformparameters-findmatchesparameters-accuracycosttradeoff
            '''
            result = self._values.get("accuracy_cost_tradeoff")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def enforce_provided_labels(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnMLTransform.FindMatchesParametersProperty.EnforceProvidedLabels``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformparameters-findmatchesparameters.html#cfn-glue-mltransform-transformparameters-findmatchesparameters-enforceprovidedlabels
            '''
            result = self._values.get("enforce_provided_labels")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def precision_recall_tradeoff(self) -> typing.Optional[jsii.Number]:
            '''``CfnMLTransform.FindMatchesParametersProperty.PrecisionRecallTradeoff``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformparameters-findmatchesparameters.html#cfn-glue-mltransform-transformparameters-findmatchesparameters-precisionrecalltradeoff
            '''
            result = self._values.get("precision_recall_tradeoff")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FindMatchesParametersProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnMLTransform.GlueTablesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "database_name": "databaseName",
            "table_name": "tableName",
            "catalog_id": "catalogId",
            "connection_name": "connectionName",
        },
    )
    class GlueTablesProperty:
        def __init__(
            self,
            *,
            database_name: builtins.str,
            table_name: builtins.str,
            catalog_id: typing.Optional[builtins.str] = None,
            connection_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param database_name: ``CfnMLTransform.GlueTablesProperty.DatabaseName``.
            :param table_name: ``CfnMLTransform.GlueTablesProperty.TableName``.
            :param catalog_id: ``CfnMLTransform.GlueTablesProperty.CatalogId``.
            :param connection_name: ``CfnMLTransform.GlueTablesProperty.ConnectionName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-inputrecordtables-gluetables.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "database_name": database_name,
                "table_name": table_name,
            }
            if catalog_id is not None:
                self._values["catalog_id"] = catalog_id
            if connection_name is not None:
                self._values["connection_name"] = connection_name

        @builtins.property
        def database_name(self) -> builtins.str:
            '''``CfnMLTransform.GlueTablesProperty.DatabaseName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-inputrecordtables-gluetables.html#cfn-glue-mltransform-inputrecordtables-gluetables-databasename
            '''
            result = self._values.get("database_name")
            assert result is not None, "Required property 'database_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def table_name(self) -> builtins.str:
            '''``CfnMLTransform.GlueTablesProperty.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-inputrecordtables-gluetables.html#cfn-glue-mltransform-inputrecordtables-gluetables-tablename
            '''
            result = self._values.get("table_name")
            assert result is not None, "Required property 'table_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def catalog_id(self) -> typing.Optional[builtins.str]:
            '''``CfnMLTransform.GlueTablesProperty.CatalogId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-inputrecordtables-gluetables.html#cfn-glue-mltransform-inputrecordtables-gluetables-catalogid
            '''
            result = self._values.get("catalog_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def connection_name(self) -> typing.Optional[builtins.str]:
            '''``CfnMLTransform.GlueTablesProperty.ConnectionName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-inputrecordtables-gluetables.html#cfn-glue-mltransform-inputrecordtables-gluetables-connectionname
            '''
            result = self._values.get("connection_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "GlueTablesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnMLTransform.InputRecordTablesProperty",
        jsii_struct_bases=[],
        name_mapping={"glue_tables": "glueTables"},
    )
    class InputRecordTablesProperty:
        def __init__(
            self,
            *,
            glue_tables: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnMLTransform.GlueTablesProperty", _IResolvable_da3f097b]]]] = None,
        ) -> None:
            '''
            :param glue_tables: ``CfnMLTransform.InputRecordTablesProperty.GlueTables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-inputrecordtables.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if glue_tables is not None:
                self._values["glue_tables"] = glue_tables

        @builtins.property
        def glue_tables(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnMLTransform.GlueTablesProperty", _IResolvable_da3f097b]]]]:
            '''``CfnMLTransform.InputRecordTablesProperty.GlueTables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-inputrecordtables.html#cfn-glue-mltransform-inputrecordtables-gluetables
            '''
            result = self._values.get("glue_tables")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnMLTransform.GlueTablesProperty", _IResolvable_da3f097b]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "InputRecordTablesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnMLTransform.MLUserDataEncryptionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "ml_user_data_encryption_mode": "mlUserDataEncryptionMode",
            "kms_key_id": "kmsKeyId",
        },
    )
    class MLUserDataEncryptionProperty:
        def __init__(
            self,
            *,
            ml_user_data_encryption_mode: builtins.str,
            kms_key_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param ml_user_data_encryption_mode: ``CfnMLTransform.MLUserDataEncryptionProperty.MLUserDataEncryptionMode``.
            :param kms_key_id: ``CfnMLTransform.MLUserDataEncryptionProperty.KmsKeyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformencryption-mluserdataencryption.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "ml_user_data_encryption_mode": ml_user_data_encryption_mode,
            }
            if kms_key_id is not None:
                self._values["kms_key_id"] = kms_key_id

        @builtins.property
        def ml_user_data_encryption_mode(self) -> builtins.str:
            '''``CfnMLTransform.MLUserDataEncryptionProperty.MLUserDataEncryptionMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformencryption-mluserdataencryption.html#cfn-glue-mltransform-transformencryption-mluserdataencryption-mluserdataencryptionmode
            '''
            result = self._values.get("ml_user_data_encryption_mode")
            assert result is not None, "Required property 'ml_user_data_encryption_mode' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def kms_key_id(self) -> typing.Optional[builtins.str]:
            '''``CfnMLTransform.MLUserDataEncryptionProperty.KmsKeyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformencryption-mluserdataencryption.html#cfn-glue-mltransform-transformencryption-mluserdataencryption-kmskeyid
            '''
            result = self._values.get("kms_key_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MLUserDataEncryptionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnMLTransform.TransformEncryptionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "ml_user_data_encryption": "mlUserDataEncryption",
            "task_run_security_configuration_name": "taskRunSecurityConfigurationName",
        },
    )
    class TransformEncryptionProperty:
        def __init__(
            self,
            *,
            ml_user_data_encryption: typing.Optional[typing.Union["CfnMLTransform.MLUserDataEncryptionProperty", _IResolvable_da3f097b]] = None,
            task_run_security_configuration_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param ml_user_data_encryption: ``CfnMLTransform.TransformEncryptionProperty.MLUserDataEncryption``.
            :param task_run_security_configuration_name: ``CfnMLTransform.TransformEncryptionProperty.TaskRunSecurityConfigurationName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformencryption.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if ml_user_data_encryption is not None:
                self._values["ml_user_data_encryption"] = ml_user_data_encryption
            if task_run_security_configuration_name is not None:
                self._values["task_run_security_configuration_name"] = task_run_security_configuration_name

        @builtins.property
        def ml_user_data_encryption(
            self,
        ) -> typing.Optional[typing.Union["CfnMLTransform.MLUserDataEncryptionProperty", _IResolvable_da3f097b]]:
            '''``CfnMLTransform.TransformEncryptionProperty.MLUserDataEncryption``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformencryption.html#cfn-glue-mltransform-transformencryption-mluserdataencryption
            '''
            result = self._values.get("ml_user_data_encryption")
            return typing.cast(typing.Optional[typing.Union["CfnMLTransform.MLUserDataEncryptionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def task_run_security_configuration_name(self) -> typing.Optional[builtins.str]:
            '''``CfnMLTransform.TransformEncryptionProperty.TaskRunSecurityConfigurationName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformencryption.html#cfn-glue-mltransform-transformencryption-taskrunsecurityconfigurationname
            '''
            result = self._values.get("task_run_security_configuration_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TransformEncryptionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnMLTransform.TransformParametersProperty",
        jsii_struct_bases=[],
        name_mapping={
            "transform_type": "transformType",
            "find_matches_parameters": "findMatchesParameters",
        },
    )
    class TransformParametersProperty:
        def __init__(
            self,
            *,
            transform_type: builtins.str,
            find_matches_parameters: typing.Optional[typing.Union["CfnMLTransform.FindMatchesParametersProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param transform_type: ``CfnMLTransform.TransformParametersProperty.TransformType``.
            :param find_matches_parameters: ``CfnMLTransform.TransformParametersProperty.FindMatchesParameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformparameters.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "transform_type": transform_type,
            }
            if find_matches_parameters is not None:
                self._values["find_matches_parameters"] = find_matches_parameters

        @builtins.property
        def transform_type(self) -> builtins.str:
            '''``CfnMLTransform.TransformParametersProperty.TransformType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformparameters.html#cfn-glue-mltransform-transformparameters-transformtype
            '''
            result = self._values.get("transform_type")
            assert result is not None, "Required property 'transform_type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def find_matches_parameters(
            self,
        ) -> typing.Optional[typing.Union["CfnMLTransform.FindMatchesParametersProperty", _IResolvable_da3f097b]]:
            '''``CfnMLTransform.TransformParametersProperty.FindMatchesParameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-mltransform-transformparameters.html#cfn-glue-mltransform-transformparameters-findmatchesparameters
            '''
            result = self._values.get("find_matches_parameters")
            return typing.cast(typing.Optional[typing.Union["CfnMLTransform.FindMatchesParametersProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TransformParametersProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnMLTransformProps",
    jsii_struct_bases=[],
    name_mapping={
        "input_record_tables": "inputRecordTables",
        "role": "role",
        "transform_parameters": "transformParameters",
        "description": "description",
        "glue_version": "glueVersion",
        "max_capacity": "maxCapacity",
        "max_retries": "maxRetries",
        "name": "name",
        "number_of_workers": "numberOfWorkers",
        "tags": "tags",
        "timeout": "timeout",
        "transform_encryption": "transformEncryption",
        "worker_type": "workerType",
    },
)
class CfnMLTransformProps:
    def __init__(
        self,
        *,
        input_record_tables: typing.Union[CfnMLTransform.InputRecordTablesProperty, _IResolvable_da3f097b],
        role: builtins.str,
        transform_parameters: typing.Union[CfnMLTransform.TransformParametersProperty, _IResolvable_da3f097b],
        description: typing.Optional[builtins.str] = None,
        glue_version: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        number_of_workers: typing.Optional[jsii.Number] = None,
        tags: typing.Any = None,
        timeout: typing.Optional[jsii.Number] = None,
        transform_encryption: typing.Optional[typing.Union[CfnMLTransform.TransformEncryptionProperty, _IResolvable_da3f097b]] = None,
        worker_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::MLTransform``.

        :param input_record_tables: ``AWS::Glue::MLTransform.InputRecordTables``.
        :param role: ``AWS::Glue::MLTransform.Role``.
        :param transform_parameters: ``AWS::Glue::MLTransform.TransformParameters``.
        :param description: ``AWS::Glue::MLTransform.Description``.
        :param glue_version: ``AWS::Glue::MLTransform.GlueVersion``.
        :param max_capacity: ``AWS::Glue::MLTransform.MaxCapacity``.
        :param max_retries: ``AWS::Glue::MLTransform.MaxRetries``.
        :param name: ``AWS::Glue::MLTransform.Name``.
        :param number_of_workers: ``AWS::Glue::MLTransform.NumberOfWorkers``.
        :param tags: ``AWS::Glue::MLTransform.Tags``.
        :param timeout: ``AWS::Glue::MLTransform.Timeout``.
        :param transform_encryption: ``AWS::Glue::MLTransform.TransformEncryption``.
        :param worker_type: ``AWS::Glue::MLTransform.WorkerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "input_record_tables": input_record_tables,
            "role": role,
            "transform_parameters": transform_parameters,
        }
        if description is not None:
            self._values["description"] = description
        if glue_version is not None:
            self._values["glue_version"] = glue_version
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if name is not None:
            self._values["name"] = name
        if number_of_workers is not None:
            self._values["number_of_workers"] = number_of_workers
        if tags is not None:
            self._values["tags"] = tags
        if timeout is not None:
            self._values["timeout"] = timeout
        if transform_encryption is not None:
            self._values["transform_encryption"] = transform_encryption
        if worker_type is not None:
            self._values["worker_type"] = worker_type

    @builtins.property
    def input_record_tables(
        self,
    ) -> typing.Union[CfnMLTransform.InputRecordTablesProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::MLTransform.InputRecordTables``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-inputrecordtables
        '''
        result = self._values.get("input_record_tables")
        assert result is not None, "Required property 'input_record_tables' is missing"
        return typing.cast(typing.Union[CfnMLTransform.InputRecordTablesProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def role(self) -> builtins.str:
        '''``AWS::Glue::MLTransform.Role``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-role
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def transform_parameters(
        self,
    ) -> typing.Union[CfnMLTransform.TransformParametersProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::MLTransform.TransformParameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-transformparameters
        '''
        result = self._values.get("transform_parameters")
        assert result is not None, "Required property 'transform_parameters' is missing"
        return typing.cast(typing.Union[CfnMLTransform.TransformParametersProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::MLTransform.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def glue_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::MLTransform.GlueVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-glueversion
        '''
        result = self._values.get("glue_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::MLTransform.MaxCapacity``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-maxcapacity
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::MLTransform.MaxRetries``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-maxretries
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::MLTransform.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def number_of_workers(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::MLTransform.NumberOfWorkers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-numberofworkers
        '''
        result = self._values.get("number_of_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Glue::MLTransform.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Glue::MLTransform.Timeout``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-timeout
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def transform_encryption(
        self,
    ) -> typing.Optional[typing.Union[CfnMLTransform.TransformEncryptionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::MLTransform.TransformEncryption``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-transformencryption
        '''
        result = self._values.get("transform_encryption")
        return typing.cast(typing.Optional[typing.Union[CfnMLTransform.TransformEncryptionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def worker_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::MLTransform.WorkerType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-mltransform.html#cfn-glue-mltransform-workertype
        '''
        result = self._values.get("worker_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnMLTransformProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnPartition(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnPartition",
):
    '''A CloudFormation ``AWS::Glue::Partition``.

    :cloudformationResource: AWS::Glue::Partition
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        catalog_id: builtins.str,
        database_name: builtins.str,
        partition_input: typing.Union["CfnPartition.PartitionInputProperty", _IResolvable_da3f097b],
        table_name: builtins.str,
    ) -> None:
        '''Create a new ``AWS::Glue::Partition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param catalog_id: ``AWS::Glue::Partition.CatalogId``.
        :param database_name: ``AWS::Glue::Partition.DatabaseName``.
        :param partition_input: ``AWS::Glue::Partition.PartitionInput``.
        :param table_name: ``AWS::Glue::Partition.TableName``.
        '''
        props = CfnPartitionProps(
            catalog_id=catalog_id,
            database_name=database_name,
            partition_input=partition_input,
            table_name=table_name,
        )

        jsii.create(CfnPartition, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::Partition.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-catalogid
        '''
        return typing.cast(builtins.str, jsii.get(self, "catalogId"))

    @catalog_id.setter
    def catalog_id(self, value: builtins.str) -> None:
        jsii.set(self, "catalogId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''``AWS::Glue::Partition.DatabaseName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-databasename
        '''
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionInput")
    def partition_input(
        self,
    ) -> typing.Union["CfnPartition.PartitionInputProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::Partition.PartitionInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-partitioninput
        '''
        return typing.cast(typing.Union["CfnPartition.PartitionInputProperty", _IResolvable_da3f097b], jsii.get(self, "partitionInput"))

    @partition_input.setter
    def partition_input(
        self,
        value: typing.Union["CfnPartition.PartitionInputProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "partitionInput", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        '''``AWS::Glue::Partition.TableName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-tablename
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnPartition.ColumnProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "comment": "comment", "type": "type"},
    )
    class ColumnProperty:
        def __init__(
            self,
            *,
            name: builtins.str,
            comment: typing.Optional[builtins.str] = None,
            type: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param name: ``CfnPartition.ColumnProperty.Name``.
            :param comment: ``CfnPartition.ColumnProperty.Comment``.
            :param type: ``CfnPartition.ColumnProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
            }
            if comment is not None:
                self._values["comment"] = comment
            if type is not None:
                self._values["type"] = type

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnPartition.ColumnProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html#cfn-glue-partition-column-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def comment(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.ColumnProperty.Comment``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html#cfn-glue-partition-column-comment
            '''
            result = self._values.get("comment")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def type(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.ColumnProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html#cfn-glue-partition-column-type
            '''
            result = self._values.get("type")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ColumnProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnPartition.OrderProperty",
        jsii_struct_bases=[],
        name_mapping={"column": "column", "sort_order": "sortOrder"},
    )
    class OrderProperty:
        def __init__(
            self,
            *,
            column: builtins.str,
            sort_order: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param column: ``CfnPartition.OrderProperty.Column``.
            :param sort_order: ``CfnPartition.OrderProperty.SortOrder``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-order.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "column": column,
            }
            if sort_order is not None:
                self._values["sort_order"] = sort_order

        @builtins.property
        def column(self) -> builtins.str:
            '''``CfnPartition.OrderProperty.Column``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-order.html#cfn-glue-partition-order-column
            '''
            result = self._values.get("column")
            assert result is not None, "Required property 'column' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def sort_order(self) -> typing.Optional[jsii.Number]:
            '''``CfnPartition.OrderProperty.SortOrder``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-order.html#cfn-glue-partition-order-sortorder
            '''
            result = self._values.get("sort_order")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OrderProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnPartition.PartitionInputProperty",
        jsii_struct_bases=[],
        name_mapping={
            "values": "values",
            "parameters": "parameters",
            "storage_descriptor": "storageDescriptor",
        },
    )
    class PartitionInputProperty:
        def __init__(
            self,
            *,
            values: typing.Sequence[builtins.str],
            parameters: typing.Any = None,
            storage_descriptor: typing.Optional[typing.Union["CfnPartition.StorageDescriptorProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param values: ``CfnPartition.PartitionInputProperty.Values``.
            :param parameters: ``CfnPartition.PartitionInputProperty.Parameters``.
            :param storage_descriptor: ``CfnPartition.PartitionInputProperty.StorageDescriptor``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "values": values,
            }
            if parameters is not None:
                self._values["parameters"] = parameters
            if storage_descriptor is not None:
                self._values["storage_descriptor"] = storage_descriptor

        @builtins.property
        def values(self) -> typing.List[builtins.str]:
            '''``CfnPartition.PartitionInputProperty.Values``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html#cfn-glue-partition-partitioninput-values
            '''
            result = self._values.get("values")
            assert result is not None, "Required property 'values' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def parameters(self) -> typing.Any:
            '''``CfnPartition.PartitionInputProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html#cfn-glue-partition-partitioninput-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Any, result)

        @builtins.property
        def storage_descriptor(
            self,
        ) -> typing.Optional[typing.Union["CfnPartition.StorageDescriptorProperty", _IResolvable_da3f097b]]:
            '''``CfnPartition.PartitionInputProperty.StorageDescriptor``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html#cfn-glue-partition-partitioninput-storagedescriptor
            '''
            result = self._values.get("storage_descriptor")
            return typing.cast(typing.Optional[typing.Union["CfnPartition.StorageDescriptorProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PartitionInputProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnPartition.SchemaIdProperty",
        jsii_struct_bases=[],
        name_mapping={
            "registry_name": "registryName",
            "schema_arn": "schemaArn",
            "schema_name": "schemaName",
        },
    )
    class SchemaIdProperty:
        def __init__(
            self,
            *,
            registry_name: typing.Optional[builtins.str] = None,
            schema_arn: typing.Optional[builtins.str] = None,
            schema_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param registry_name: ``CfnPartition.SchemaIdProperty.RegistryName``.
            :param schema_arn: ``CfnPartition.SchemaIdProperty.SchemaArn``.
            :param schema_name: ``CfnPartition.SchemaIdProperty.SchemaName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-schemaid.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if registry_name is not None:
                self._values["registry_name"] = registry_name
            if schema_arn is not None:
                self._values["schema_arn"] = schema_arn
            if schema_name is not None:
                self._values["schema_name"] = schema_name

        @builtins.property
        def registry_name(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.SchemaIdProperty.RegistryName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-schemaid.html#cfn-glue-partition-schemaid-registryname
            '''
            result = self._values.get("registry_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def schema_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.SchemaIdProperty.SchemaArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-schemaid.html#cfn-glue-partition-schemaid-schemaarn
            '''
            result = self._values.get("schema_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def schema_name(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.SchemaIdProperty.SchemaName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-schemaid.html#cfn-glue-partition-schemaid-schemaname
            '''
            result = self._values.get("schema_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SchemaIdProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnPartition.SchemaReferenceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "schema_id": "schemaId",
            "schema_version_id": "schemaVersionId",
            "schema_version_number": "schemaVersionNumber",
        },
    )
    class SchemaReferenceProperty:
        def __init__(
            self,
            *,
            schema_id: typing.Optional[typing.Union["CfnPartition.SchemaIdProperty", _IResolvable_da3f097b]] = None,
            schema_version_id: typing.Optional[builtins.str] = None,
            schema_version_number: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param schema_id: ``CfnPartition.SchemaReferenceProperty.SchemaId``.
            :param schema_version_id: ``CfnPartition.SchemaReferenceProperty.SchemaVersionId``.
            :param schema_version_number: ``CfnPartition.SchemaReferenceProperty.SchemaVersionNumber``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-schemareference.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if schema_id is not None:
                self._values["schema_id"] = schema_id
            if schema_version_id is not None:
                self._values["schema_version_id"] = schema_version_id
            if schema_version_number is not None:
                self._values["schema_version_number"] = schema_version_number

        @builtins.property
        def schema_id(
            self,
        ) -> typing.Optional[typing.Union["CfnPartition.SchemaIdProperty", _IResolvable_da3f097b]]:
            '''``CfnPartition.SchemaReferenceProperty.SchemaId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-schemareference.html#cfn-glue-partition-schemareference-schemaid
            '''
            result = self._values.get("schema_id")
            return typing.cast(typing.Optional[typing.Union["CfnPartition.SchemaIdProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def schema_version_id(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.SchemaReferenceProperty.SchemaVersionId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-schemareference.html#cfn-glue-partition-schemareference-schemaversionid
            '''
            result = self._values.get("schema_version_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def schema_version_number(self) -> typing.Optional[jsii.Number]:
            '''``CfnPartition.SchemaReferenceProperty.SchemaVersionNumber``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-schemareference.html#cfn-glue-partition-schemareference-schemaversionnumber
            '''
            result = self._values.get("schema_version_number")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SchemaReferenceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnPartition.SerdeInfoProperty",
        jsii_struct_bases=[],
        name_mapping={
            "name": "name",
            "parameters": "parameters",
            "serialization_library": "serializationLibrary",
        },
    )
    class SerdeInfoProperty:
        def __init__(
            self,
            *,
            name: typing.Optional[builtins.str] = None,
            parameters: typing.Any = None,
            serialization_library: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param name: ``CfnPartition.SerdeInfoProperty.Name``.
            :param parameters: ``CfnPartition.SerdeInfoProperty.Parameters``.
            :param serialization_library: ``CfnPartition.SerdeInfoProperty.SerializationLibrary``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if name is not None:
                self._values["name"] = name
            if parameters is not None:
                self._values["parameters"] = parameters
            if serialization_library is not None:
                self._values["serialization_library"] = serialization_library

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.SerdeInfoProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html#cfn-glue-partition-serdeinfo-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def parameters(self) -> typing.Any:
            '''``CfnPartition.SerdeInfoProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html#cfn-glue-partition-serdeinfo-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Any, result)

        @builtins.property
        def serialization_library(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.SerdeInfoProperty.SerializationLibrary``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html#cfn-glue-partition-serdeinfo-serializationlibrary
            '''
            result = self._values.get("serialization_library")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SerdeInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnPartition.SkewedInfoProperty",
        jsii_struct_bases=[],
        name_mapping={
            "skewed_column_names": "skewedColumnNames",
            "skewed_column_value_location_maps": "skewedColumnValueLocationMaps",
            "skewed_column_values": "skewedColumnValues",
        },
    )
    class SkewedInfoProperty:
        def __init__(
            self,
            *,
            skewed_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
            skewed_column_value_location_maps: typing.Any = None,
            skewed_column_values: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''
            :param skewed_column_names: ``CfnPartition.SkewedInfoProperty.SkewedColumnNames``.
            :param skewed_column_value_location_maps: ``CfnPartition.SkewedInfoProperty.SkewedColumnValueLocationMaps``.
            :param skewed_column_values: ``CfnPartition.SkewedInfoProperty.SkewedColumnValues``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if skewed_column_names is not None:
                self._values["skewed_column_names"] = skewed_column_names
            if skewed_column_value_location_maps is not None:
                self._values["skewed_column_value_location_maps"] = skewed_column_value_location_maps
            if skewed_column_values is not None:
                self._values["skewed_column_values"] = skewed_column_values

        @builtins.property
        def skewed_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnPartition.SkewedInfoProperty.SkewedColumnNames``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html#cfn-glue-partition-skewedinfo-skewedcolumnnames
            '''
            result = self._values.get("skewed_column_names")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def skewed_column_value_location_maps(self) -> typing.Any:
            '''``CfnPartition.SkewedInfoProperty.SkewedColumnValueLocationMaps``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html#cfn-glue-partition-skewedinfo-skewedcolumnvaluelocationmaps
            '''
            result = self._values.get("skewed_column_value_location_maps")
            return typing.cast(typing.Any, result)

        @builtins.property
        def skewed_column_values(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnPartition.SkewedInfoProperty.SkewedColumnValues``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html#cfn-glue-partition-skewedinfo-skewedcolumnvalues
            '''
            result = self._values.get("skewed_column_values")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SkewedInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnPartition.StorageDescriptorProperty",
        jsii_struct_bases=[],
        name_mapping={
            "bucket_columns": "bucketColumns",
            "columns": "columns",
            "compressed": "compressed",
            "input_format": "inputFormat",
            "location": "location",
            "number_of_buckets": "numberOfBuckets",
            "output_format": "outputFormat",
            "parameters": "parameters",
            "schema_reference": "schemaReference",
            "serde_info": "serdeInfo",
            "skewed_info": "skewedInfo",
            "sort_columns": "sortColumns",
            "stored_as_sub_directories": "storedAsSubDirectories",
        },
    )
    class StorageDescriptorProperty:
        def __init__(
            self,
            *,
            bucket_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
            columns: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnPartition.ColumnProperty", _IResolvable_da3f097b]]]] = None,
            compressed: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            input_format: typing.Optional[builtins.str] = None,
            location: typing.Optional[builtins.str] = None,
            number_of_buckets: typing.Optional[jsii.Number] = None,
            output_format: typing.Optional[builtins.str] = None,
            parameters: typing.Any = None,
            schema_reference: typing.Optional[typing.Union["CfnPartition.SchemaReferenceProperty", _IResolvable_da3f097b]] = None,
            serde_info: typing.Optional[typing.Union["CfnPartition.SerdeInfoProperty", _IResolvable_da3f097b]] = None,
            skewed_info: typing.Optional[typing.Union["CfnPartition.SkewedInfoProperty", _IResolvable_da3f097b]] = None,
            sort_columns: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnPartition.OrderProperty", _IResolvable_da3f097b]]]] = None,
            stored_as_sub_directories: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param bucket_columns: ``CfnPartition.StorageDescriptorProperty.BucketColumns``.
            :param columns: ``CfnPartition.StorageDescriptorProperty.Columns``.
            :param compressed: ``CfnPartition.StorageDescriptorProperty.Compressed``.
            :param input_format: ``CfnPartition.StorageDescriptorProperty.InputFormat``.
            :param location: ``CfnPartition.StorageDescriptorProperty.Location``.
            :param number_of_buckets: ``CfnPartition.StorageDescriptorProperty.NumberOfBuckets``.
            :param output_format: ``CfnPartition.StorageDescriptorProperty.OutputFormat``.
            :param parameters: ``CfnPartition.StorageDescriptorProperty.Parameters``.
            :param schema_reference: ``CfnPartition.StorageDescriptorProperty.SchemaReference``.
            :param serde_info: ``CfnPartition.StorageDescriptorProperty.SerdeInfo``.
            :param skewed_info: ``CfnPartition.StorageDescriptorProperty.SkewedInfo``.
            :param sort_columns: ``CfnPartition.StorageDescriptorProperty.SortColumns``.
            :param stored_as_sub_directories: ``CfnPartition.StorageDescriptorProperty.StoredAsSubDirectories``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if bucket_columns is not None:
                self._values["bucket_columns"] = bucket_columns
            if columns is not None:
                self._values["columns"] = columns
            if compressed is not None:
                self._values["compressed"] = compressed
            if input_format is not None:
                self._values["input_format"] = input_format
            if location is not None:
                self._values["location"] = location
            if number_of_buckets is not None:
                self._values["number_of_buckets"] = number_of_buckets
            if output_format is not None:
                self._values["output_format"] = output_format
            if parameters is not None:
                self._values["parameters"] = parameters
            if schema_reference is not None:
                self._values["schema_reference"] = schema_reference
            if serde_info is not None:
                self._values["serde_info"] = serde_info
            if skewed_info is not None:
                self._values["skewed_info"] = skewed_info
            if sort_columns is not None:
                self._values["sort_columns"] = sort_columns
            if stored_as_sub_directories is not None:
                self._values["stored_as_sub_directories"] = stored_as_sub_directories

        @builtins.property
        def bucket_columns(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnPartition.StorageDescriptorProperty.BucketColumns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-bucketcolumns
            '''
            result = self._values.get("bucket_columns")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def columns(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPartition.ColumnProperty", _IResolvable_da3f097b]]]]:
            '''``CfnPartition.StorageDescriptorProperty.Columns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-columns
            '''
            result = self._values.get("columns")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPartition.ColumnProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def compressed(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnPartition.StorageDescriptorProperty.Compressed``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-compressed
            '''
            result = self._values.get("compressed")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def input_format(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.StorageDescriptorProperty.InputFormat``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-inputformat
            '''
            result = self._values.get("input_format")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def location(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.StorageDescriptorProperty.Location``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-location
            '''
            result = self._values.get("location")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def number_of_buckets(self) -> typing.Optional[jsii.Number]:
            '''``CfnPartition.StorageDescriptorProperty.NumberOfBuckets``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-numberofbuckets
            '''
            result = self._values.get("number_of_buckets")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def output_format(self) -> typing.Optional[builtins.str]:
            '''``CfnPartition.StorageDescriptorProperty.OutputFormat``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-outputformat
            '''
            result = self._values.get("output_format")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def parameters(self) -> typing.Any:
            '''``CfnPartition.StorageDescriptorProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Any, result)

        @builtins.property
        def schema_reference(
            self,
        ) -> typing.Optional[typing.Union["CfnPartition.SchemaReferenceProperty", _IResolvable_da3f097b]]:
            '''``CfnPartition.StorageDescriptorProperty.SchemaReference``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-schemareference
            '''
            result = self._values.get("schema_reference")
            return typing.cast(typing.Optional[typing.Union["CfnPartition.SchemaReferenceProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def serde_info(
            self,
        ) -> typing.Optional[typing.Union["CfnPartition.SerdeInfoProperty", _IResolvable_da3f097b]]:
            '''``CfnPartition.StorageDescriptorProperty.SerdeInfo``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-serdeinfo
            '''
            result = self._values.get("serde_info")
            return typing.cast(typing.Optional[typing.Union["CfnPartition.SerdeInfoProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def skewed_info(
            self,
        ) -> typing.Optional[typing.Union["CfnPartition.SkewedInfoProperty", _IResolvable_da3f097b]]:
            '''``CfnPartition.StorageDescriptorProperty.SkewedInfo``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-skewedinfo
            '''
            result = self._values.get("skewed_info")
            return typing.cast(typing.Optional[typing.Union["CfnPartition.SkewedInfoProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sort_columns(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPartition.OrderProperty", _IResolvable_da3f097b]]]]:
            '''``CfnPartition.StorageDescriptorProperty.SortColumns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-sortcolumns
            '''
            result = self._values.get("sort_columns")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPartition.OrderProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def stored_as_sub_directories(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnPartition.StorageDescriptorProperty.StoredAsSubDirectories``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-storedassubdirectories
            '''
            result = self._values.get("stored_as_sub_directories")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StorageDescriptorProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnPartitionProps",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_id": "catalogId",
        "database_name": "databaseName",
        "partition_input": "partitionInput",
        "table_name": "tableName",
    },
)
class CfnPartitionProps:
    def __init__(
        self,
        *,
        catalog_id: builtins.str,
        database_name: builtins.str,
        partition_input: typing.Union[CfnPartition.PartitionInputProperty, _IResolvable_da3f097b],
        table_name: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Partition``.

        :param catalog_id: ``AWS::Glue::Partition.CatalogId``.
        :param database_name: ``AWS::Glue::Partition.DatabaseName``.
        :param partition_input: ``AWS::Glue::Partition.PartitionInput``.
        :param table_name: ``AWS::Glue::Partition.TableName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "catalog_id": catalog_id,
            "database_name": database_name,
            "partition_input": partition_input,
            "table_name": table_name,
        }

    @builtins.property
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::Partition.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-catalogid
        '''
        result = self._values.get("catalog_id")
        assert result is not None, "Required property 'catalog_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''``AWS::Glue::Partition.DatabaseName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-databasename
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def partition_input(
        self,
    ) -> typing.Union[CfnPartition.PartitionInputProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::Partition.PartitionInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-partitioninput
        '''
        result = self._values.get("partition_input")
        assert result is not None, "Required property 'partition_input' is missing"
        return typing.cast(typing.Union[CfnPartition.PartitionInputProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''``AWS::Glue::Partition.TableName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-tablename
        '''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPartitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnRegistry(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnRegistry",
):
    '''A CloudFormation ``AWS::Glue::Registry``.

    :cloudformationResource: AWS::Glue::Registry
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-registry.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::Glue::Registry``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param name: ``AWS::Glue::Registry.Name``.
        :param description: ``AWS::Glue::Registry.Description``.
        :param tags: ``AWS::Glue::Registry.Tags``.
        '''
        props = CfnRegistryProps(name=name, description=description, tags=tags)

        jsii.create(CfnRegistry, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Glue::Registry.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-registry.html#cfn-glue-registry-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Glue::Registry.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-registry.html#cfn-glue-registry-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Registry.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-registry.html#cfn-glue-registry-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnRegistryProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "description": "description", "tags": "tags"},
)
class CfnRegistryProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Registry``.

        :param name: ``AWS::Glue::Registry.Name``.
        :param description: ``AWS::Glue::Registry.Description``.
        :param tags: ``AWS::Glue::Registry.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-registry.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Glue::Registry.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-registry.html#cfn-glue-registry-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Registry.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-registry.html#cfn-glue-registry-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Glue::Registry.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-registry.html#cfn-glue-registry-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnRegistryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnSchema(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnSchema",
):
    '''A CloudFormation ``AWS::Glue::Schema``.

    :cloudformationResource: AWS::Glue::Schema
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        compatibility: builtins.str,
        data_format: builtins.str,
        name: builtins.str,
        schema_definition: builtins.str,
        checkpoint_version: typing.Optional[typing.Union["CfnSchema.SchemaVersionProperty", _IResolvable_da3f097b]] = None,
        description: typing.Optional[builtins.str] = None,
        registry: typing.Optional[typing.Union["CfnSchema.RegistryProperty", _IResolvable_da3f097b]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::Glue::Schema``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param compatibility: ``AWS::Glue::Schema.Compatibility``.
        :param data_format: ``AWS::Glue::Schema.DataFormat``.
        :param name: ``AWS::Glue::Schema.Name``.
        :param schema_definition: ``AWS::Glue::Schema.SchemaDefinition``.
        :param checkpoint_version: ``AWS::Glue::Schema.CheckpointVersion``.
        :param description: ``AWS::Glue::Schema.Description``.
        :param registry: ``AWS::Glue::Schema.Registry``.
        :param tags: ``AWS::Glue::Schema.Tags``.
        '''
        props = CfnSchemaProps(
            compatibility=compatibility,
            data_format=data_format,
            name=name,
            schema_definition=schema_definition,
            checkpoint_version=checkpoint_version,
            description=description,
            registry=registry,
            tags=tags,
        )

        jsii.create(CfnSchema, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrInitialSchemaVersionId")
    def attr_initial_schema_version_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: InitialSchemaVersionId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrInitialSchemaVersionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Glue::Schema.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibility")
    def compatibility(self) -> builtins.str:
        '''``AWS::Glue::Schema.Compatibility``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-compatibility
        '''
        return typing.cast(builtins.str, jsii.get(self, "compatibility"))

    @compatibility.setter
    def compatibility(self, value: builtins.str) -> None:
        jsii.set(self, "compatibility", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataFormat")
    def data_format(self) -> builtins.str:
        '''``AWS::Glue::Schema.DataFormat``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-dataformat
        '''
        return typing.cast(builtins.str, jsii.get(self, "dataFormat"))

    @data_format.setter
    def data_format(self, value: builtins.str) -> None:
        jsii.set(self, "dataFormat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Glue::Schema.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaDefinition")
    def schema_definition(self) -> builtins.str:
        '''``AWS::Glue::Schema.SchemaDefinition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-schemadefinition
        '''
        return typing.cast(builtins.str, jsii.get(self, "schemaDefinition"))

    @schema_definition.setter
    def schema_definition(self, value: builtins.str) -> None:
        jsii.set(self, "schemaDefinition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checkpointVersion")
    def checkpoint_version(
        self,
    ) -> typing.Optional[typing.Union["CfnSchema.SchemaVersionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Schema.CheckpointVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-checkpointversion
        '''
        return typing.cast(typing.Optional[typing.Union["CfnSchema.SchemaVersionProperty", _IResolvable_da3f097b]], jsii.get(self, "checkpointVersion"))

    @checkpoint_version.setter
    def checkpoint_version(
        self,
        value: typing.Optional[typing.Union["CfnSchema.SchemaVersionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "checkpointVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Schema.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registry")
    def registry(
        self,
    ) -> typing.Optional[typing.Union["CfnSchema.RegistryProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Schema.Registry``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-registry
        '''
        return typing.cast(typing.Optional[typing.Union["CfnSchema.RegistryProperty", _IResolvable_da3f097b]], jsii.get(self, "registry"))

    @registry.setter
    def registry(
        self,
        value: typing.Optional[typing.Union["CfnSchema.RegistryProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "registry", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnSchema.RegistryProperty",
        jsii_struct_bases=[],
        name_mapping={"arn": "arn", "name": "name"},
    )
    class RegistryProperty:
        def __init__(
            self,
            *,
            arn: typing.Optional[builtins.str] = None,
            name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param arn: ``CfnSchema.RegistryProperty.Arn``.
            :param name: ``CfnSchema.RegistryProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schema-registry.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if arn is not None:
                self._values["arn"] = arn
            if name is not None:
                self._values["name"] = name

        @builtins.property
        def arn(self) -> typing.Optional[builtins.str]:
            '''``CfnSchema.RegistryProperty.Arn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schema-registry.html#cfn-glue-schema-registry-arn
            '''
            result = self._values.get("arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnSchema.RegistryProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schema-registry.html#cfn-glue-schema-registry-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RegistryProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnSchema.SchemaVersionProperty",
        jsii_struct_bases=[],
        name_mapping={"is_latest": "isLatest", "version_number": "versionNumber"},
    )
    class SchemaVersionProperty:
        def __init__(
            self,
            *,
            is_latest: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            version_number: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param is_latest: ``CfnSchema.SchemaVersionProperty.IsLatest``.
            :param version_number: ``CfnSchema.SchemaVersionProperty.VersionNumber``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schema-schemaversion.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if is_latest is not None:
                self._values["is_latest"] = is_latest
            if version_number is not None:
                self._values["version_number"] = version_number

        @builtins.property
        def is_latest(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnSchema.SchemaVersionProperty.IsLatest``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schema-schemaversion.html#cfn-glue-schema-schemaversion-islatest
            '''
            result = self._values.get("is_latest")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def version_number(self) -> typing.Optional[jsii.Number]:
            '''``CfnSchema.SchemaVersionProperty.VersionNumber``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schema-schemaversion.html#cfn-glue-schema-schemaversion-versionnumber
            '''
            result = self._values.get("version_number")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SchemaVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnSchemaProps",
    jsii_struct_bases=[],
    name_mapping={
        "compatibility": "compatibility",
        "data_format": "dataFormat",
        "name": "name",
        "schema_definition": "schemaDefinition",
        "checkpoint_version": "checkpointVersion",
        "description": "description",
        "registry": "registry",
        "tags": "tags",
    },
)
class CfnSchemaProps:
    def __init__(
        self,
        *,
        compatibility: builtins.str,
        data_format: builtins.str,
        name: builtins.str,
        schema_definition: builtins.str,
        checkpoint_version: typing.Optional[typing.Union[CfnSchema.SchemaVersionProperty, _IResolvable_da3f097b]] = None,
        description: typing.Optional[builtins.str] = None,
        registry: typing.Optional[typing.Union[CfnSchema.RegistryProperty, _IResolvable_da3f097b]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Schema``.

        :param compatibility: ``AWS::Glue::Schema.Compatibility``.
        :param data_format: ``AWS::Glue::Schema.DataFormat``.
        :param name: ``AWS::Glue::Schema.Name``.
        :param schema_definition: ``AWS::Glue::Schema.SchemaDefinition``.
        :param checkpoint_version: ``AWS::Glue::Schema.CheckpointVersion``.
        :param description: ``AWS::Glue::Schema.Description``.
        :param registry: ``AWS::Glue::Schema.Registry``.
        :param tags: ``AWS::Glue::Schema.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "compatibility": compatibility,
            "data_format": data_format,
            "name": name,
            "schema_definition": schema_definition,
        }
        if checkpoint_version is not None:
            self._values["checkpoint_version"] = checkpoint_version
        if description is not None:
            self._values["description"] = description
        if registry is not None:
            self._values["registry"] = registry
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def compatibility(self) -> builtins.str:
        '''``AWS::Glue::Schema.Compatibility``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-compatibility
        '''
        result = self._values.get("compatibility")
        assert result is not None, "Required property 'compatibility' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_format(self) -> builtins.str:
        '''``AWS::Glue::Schema.DataFormat``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-dataformat
        '''
        result = self._values.get("data_format")
        assert result is not None, "Required property 'data_format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Glue::Schema.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schema_definition(self) -> builtins.str:
        '''``AWS::Glue::Schema.SchemaDefinition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-schemadefinition
        '''
        result = self._values.get("schema_definition")
        assert result is not None, "Required property 'schema_definition' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def checkpoint_version(
        self,
    ) -> typing.Optional[typing.Union[CfnSchema.SchemaVersionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Schema.CheckpointVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-checkpointversion
        '''
        result = self._values.get("checkpoint_version")
        return typing.cast(typing.Optional[typing.Union[CfnSchema.SchemaVersionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Schema.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry(
        self,
    ) -> typing.Optional[typing.Union[CfnSchema.RegistryProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Schema.Registry``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-registry
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[typing.Union[CfnSchema.RegistryProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Glue::Schema.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schema.html#cfn-glue-schema-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSchemaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnSchemaVersion(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnSchemaVersion",
):
    '''A CloudFormation ``AWS::Glue::SchemaVersion``.

    :cloudformationResource: AWS::Glue::SchemaVersion
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversion.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        schema: typing.Union["CfnSchemaVersion.SchemaProperty", _IResolvable_da3f097b],
        schema_definition: builtins.str,
    ) -> None:
        '''Create a new ``AWS::Glue::SchemaVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param schema: ``AWS::Glue::SchemaVersion.Schema``.
        :param schema_definition: ``AWS::Glue::SchemaVersion.SchemaDefinition``.
        '''
        props = CfnSchemaVersionProps(
            schema=schema, schema_definition=schema_definition
        )

        jsii.create(CfnSchemaVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrVersionId")
    def attr_version_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: VersionId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrVersionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(
        self,
    ) -> typing.Union["CfnSchemaVersion.SchemaProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::SchemaVersion.Schema``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversion.html#cfn-glue-schemaversion-schema
        '''
        return typing.cast(typing.Union["CfnSchemaVersion.SchemaProperty", _IResolvable_da3f097b], jsii.get(self, "schema"))

    @schema.setter
    def schema(
        self,
        value: typing.Union["CfnSchemaVersion.SchemaProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "schema", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaDefinition")
    def schema_definition(self) -> builtins.str:
        '''``AWS::Glue::SchemaVersion.SchemaDefinition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversion.html#cfn-glue-schemaversion-schemadefinition
        '''
        return typing.cast(builtins.str, jsii.get(self, "schemaDefinition"))

    @schema_definition.setter
    def schema_definition(self, value: builtins.str) -> None:
        jsii.set(self, "schemaDefinition", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnSchemaVersion.SchemaProperty",
        jsii_struct_bases=[],
        name_mapping={
            "registry_name": "registryName",
            "schema_arn": "schemaArn",
            "schema_name": "schemaName",
        },
    )
    class SchemaProperty:
        def __init__(
            self,
            *,
            registry_name: typing.Optional[builtins.str] = None,
            schema_arn: typing.Optional[builtins.str] = None,
            schema_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param registry_name: ``CfnSchemaVersion.SchemaProperty.RegistryName``.
            :param schema_arn: ``CfnSchemaVersion.SchemaProperty.SchemaArn``.
            :param schema_name: ``CfnSchemaVersion.SchemaProperty.SchemaName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schemaversion-schema.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if registry_name is not None:
                self._values["registry_name"] = registry_name
            if schema_arn is not None:
                self._values["schema_arn"] = schema_arn
            if schema_name is not None:
                self._values["schema_name"] = schema_name

        @builtins.property
        def registry_name(self) -> typing.Optional[builtins.str]:
            '''``CfnSchemaVersion.SchemaProperty.RegistryName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schemaversion-schema.html#cfn-glue-schemaversion-schema-registryname
            '''
            result = self._values.get("registry_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def schema_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnSchemaVersion.SchemaProperty.SchemaArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schemaversion-schema.html#cfn-glue-schemaversion-schema-schemaarn
            '''
            result = self._values.get("schema_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def schema_name(self) -> typing.Optional[builtins.str]:
            '''``CfnSchemaVersion.SchemaProperty.SchemaName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-schemaversion-schema.html#cfn-glue-schemaversion-schema-schemaname
            '''
            result = self._values.get("schema_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SchemaProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.implements(_IInspectable_c2943556)
class CfnSchemaVersionMetadata(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnSchemaVersionMetadata",
):
    '''A CloudFormation ``AWS::Glue::SchemaVersionMetadata``.

    :cloudformationResource: AWS::Glue::SchemaVersionMetadata
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversionmetadata.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        key: builtins.str,
        schema_version_id: builtins.str,
        value: builtins.str,
    ) -> None:
        '''Create a new ``AWS::Glue::SchemaVersionMetadata``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param key: ``AWS::Glue::SchemaVersionMetadata.Key``.
        :param schema_version_id: ``AWS::Glue::SchemaVersionMetadata.SchemaVersionId``.
        :param value: ``AWS::Glue::SchemaVersionMetadata.Value``.
        '''
        props = CfnSchemaVersionMetadataProps(
            key=key, schema_version_id=schema_version_id, value=value
        )

        jsii.create(CfnSchemaVersionMetadata, self, [scope, id, props])

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
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        '''``AWS::Glue::SchemaVersionMetadata.Key``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversionmetadata.html#cfn-glue-schemaversionmetadata-key
        '''
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaVersionId")
    def schema_version_id(self) -> builtins.str:
        '''``AWS::Glue::SchemaVersionMetadata.SchemaVersionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversionmetadata.html#cfn-glue-schemaversionmetadata-schemaversionid
        '''
        return typing.cast(builtins.str, jsii.get(self, "schemaVersionId"))

    @schema_version_id.setter
    def schema_version_id(self, value: builtins.str) -> None:
        jsii.set(self, "schemaVersionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        '''``AWS::Glue::SchemaVersionMetadata.Value``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversionmetadata.html#cfn-glue-schemaversionmetadata-value
        '''
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnSchemaVersionMetadataProps",
    jsii_struct_bases=[],
    name_mapping={
        "key": "key",
        "schema_version_id": "schemaVersionId",
        "value": "value",
    },
)
class CfnSchemaVersionMetadataProps:
    def __init__(
        self,
        *,
        key: builtins.str,
        schema_version_id: builtins.str,
        value: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::SchemaVersionMetadata``.

        :param key: ``AWS::Glue::SchemaVersionMetadata.Key``.
        :param schema_version_id: ``AWS::Glue::SchemaVersionMetadata.SchemaVersionId``.
        :param value: ``AWS::Glue::SchemaVersionMetadata.Value``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversionmetadata.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "schema_version_id": schema_version_id,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''``AWS::Glue::SchemaVersionMetadata.Key``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversionmetadata.html#cfn-glue-schemaversionmetadata-key
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schema_version_id(self) -> builtins.str:
        '''``AWS::Glue::SchemaVersionMetadata.SchemaVersionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversionmetadata.html#cfn-glue-schemaversionmetadata-schemaversionid
        '''
        result = self._values.get("schema_version_id")
        assert result is not None, "Required property 'schema_version_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''``AWS::Glue::SchemaVersionMetadata.Value``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversionmetadata.html#cfn-glue-schemaversionmetadata-value
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSchemaVersionMetadataProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnSchemaVersionProps",
    jsii_struct_bases=[],
    name_mapping={"schema": "schema", "schema_definition": "schemaDefinition"},
)
class CfnSchemaVersionProps:
    def __init__(
        self,
        *,
        schema: typing.Union[CfnSchemaVersion.SchemaProperty, _IResolvable_da3f097b],
        schema_definition: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::SchemaVersion``.

        :param schema: ``AWS::Glue::SchemaVersion.Schema``.
        :param schema_definition: ``AWS::Glue::SchemaVersion.SchemaDefinition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversion.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "schema": schema,
            "schema_definition": schema_definition,
        }

    @builtins.property
    def schema(
        self,
    ) -> typing.Union[CfnSchemaVersion.SchemaProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::SchemaVersion.Schema``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversion.html#cfn-glue-schemaversion-schema
        '''
        result = self._values.get("schema")
        assert result is not None, "Required property 'schema' is missing"
        return typing.cast(typing.Union[CfnSchemaVersion.SchemaProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def schema_definition(self) -> builtins.str:
        '''``AWS::Glue::SchemaVersion.SchemaDefinition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-schemaversion.html#cfn-glue-schemaversion-schemadefinition
        '''
        result = self._values.get("schema_definition")
        assert result is not None, "Required property 'schema_definition' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSchemaVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnSecurityConfiguration(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnSecurityConfiguration",
):
    '''A CloudFormation ``AWS::Glue::SecurityConfiguration``.

    :cloudformationResource: AWS::Glue::SecurityConfiguration
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        encryption_configuration: typing.Union["CfnSecurityConfiguration.EncryptionConfigurationProperty", _IResolvable_da3f097b],
        name: builtins.str,
    ) -> None:
        '''Create a new ``AWS::Glue::SecurityConfiguration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param encryption_configuration: ``AWS::Glue::SecurityConfiguration.EncryptionConfiguration``.
        :param name: ``AWS::Glue::SecurityConfiguration.Name``.
        '''
        props = CfnSecurityConfigurationProps(
            encryption_configuration=encryption_configuration, name=name
        )

        jsii.create(CfnSecurityConfiguration, self, [scope, id, props])

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
    @jsii.member(jsii_name="encryptionConfiguration")
    def encryption_configuration(
        self,
    ) -> typing.Union["CfnSecurityConfiguration.EncryptionConfigurationProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::SecurityConfiguration.EncryptionConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration
        '''
        return typing.cast(typing.Union["CfnSecurityConfiguration.EncryptionConfigurationProperty", _IResolvable_da3f097b], jsii.get(self, "encryptionConfiguration"))

    @encryption_configuration.setter
    def encryption_configuration(
        self,
        value: typing.Union["CfnSecurityConfiguration.EncryptionConfigurationProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "encryptionConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Glue::SecurityConfiguration.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnSecurityConfiguration.CloudWatchEncryptionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "cloud_watch_encryption_mode": "cloudWatchEncryptionMode",
            "kms_key_arn": "kmsKeyArn",
        },
    )
    class CloudWatchEncryptionProperty:
        def __init__(
            self,
            *,
            cloud_watch_encryption_mode: typing.Optional[builtins.str] = None,
            kms_key_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param cloud_watch_encryption_mode: ``CfnSecurityConfiguration.CloudWatchEncryptionProperty.CloudWatchEncryptionMode``.
            :param kms_key_arn: ``CfnSecurityConfiguration.CloudWatchEncryptionProperty.KmsKeyArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-cloudwatchencryption.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if cloud_watch_encryption_mode is not None:
                self._values["cloud_watch_encryption_mode"] = cloud_watch_encryption_mode
            if kms_key_arn is not None:
                self._values["kms_key_arn"] = kms_key_arn

        @builtins.property
        def cloud_watch_encryption_mode(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityConfiguration.CloudWatchEncryptionProperty.CloudWatchEncryptionMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-cloudwatchencryption.html#cfn-glue-securityconfiguration-cloudwatchencryption-cloudwatchencryptionmode
            '''
            result = self._values.get("cloud_watch_encryption_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def kms_key_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityConfiguration.CloudWatchEncryptionProperty.KmsKeyArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-cloudwatchencryption.html#cfn-glue-securityconfiguration-cloudwatchencryption-kmskeyarn
            '''
            result = self._values.get("kms_key_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CloudWatchEncryptionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnSecurityConfiguration.EncryptionConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "cloud_watch_encryption": "cloudWatchEncryption",
            "job_bookmarks_encryption": "jobBookmarksEncryption",
            "s3_encryptions": "s3Encryptions",
        },
    )
    class EncryptionConfigurationProperty:
        def __init__(
            self,
            *,
            cloud_watch_encryption: typing.Optional[typing.Union["CfnSecurityConfiguration.CloudWatchEncryptionProperty", _IResolvable_da3f097b]] = None,
            job_bookmarks_encryption: typing.Optional[typing.Union["CfnSecurityConfiguration.JobBookmarksEncryptionProperty", _IResolvable_da3f097b]] = None,
            s3_encryptions: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnSecurityConfiguration.S3EncryptionProperty", _IResolvable_da3f097b]]]] = None,
        ) -> None:
            '''
            :param cloud_watch_encryption: ``CfnSecurityConfiguration.EncryptionConfigurationProperty.CloudWatchEncryption``.
            :param job_bookmarks_encryption: ``CfnSecurityConfiguration.EncryptionConfigurationProperty.JobBookmarksEncryption``.
            :param s3_encryptions: ``CfnSecurityConfiguration.EncryptionConfigurationProperty.S3Encryptions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if cloud_watch_encryption is not None:
                self._values["cloud_watch_encryption"] = cloud_watch_encryption
            if job_bookmarks_encryption is not None:
                self._values["job_bookmarks_encryption"] = job_bookmarks_encryption
            if s3_encryptions is not None:
                self._values["s3_encryptions"] = s3_encryptions

        @builtins.property
        def cloud_watch_encryption(
            self,
        ) -> typing.Optional[typing.Union["CfnSecurityConfiguration.CloudWatchEncryptionProperty", _IResolvable_da3f097b]]:
            '''``CfnSecurityConfiguration.EncryptionConfigurationProperty.CloudWatchEncryption``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration-cloudwatchencryption
            '''
            result = self._values.get("cloud_watch_encryption")
            return typing.cast(typing.Optional[typing.Union["CfnSecurityConfiguration.CloudWatchEncryptionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def job_bookmarks_encryption(
            self,
        ) -> typing.Optional[typing.Union["CfnSecurityConfiguration.JobBookmarksEncryptionProperty", _IResolvable_da3f097b]]:
            '''``CfnSecurityConfiguration.EncryptionConfigurationProperty.JobBookmarksEncryption``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration-jobbookmarksencryption
            '''
            result = self._values.get("job_bookmarks_encryption")
            return typing.cast(typing.Optional[typing.Union["CfnSecurityConfiguration.JobBookmarksEncryptionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def s3_encryptions(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSecurityConfiguration.S3EncryptionProperty", _IResolvable_da3f097b]]]]:
            '''``CfnSecurityConfiguration.EncryptionConfigurationProperty.S3Encryptions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration-s3encryptions
            '''
            result = self._values.get("s3_encryptions")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSecurityConfiguration.S3EncryptionProperty", _IResolvable_da3f097b]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EncryptionConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnSecurityConfiguration.JobBookmarksEncryptionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "job_bookmarks_encryption_mode": "jobBookmarksEncryptionMode",
            "kms_key_arn": "kmsKeyArn",
        },
    )
    class JobBookmarksEncryptionProperty:
        def __init__(
            self,
            *,
            job_bookmarks_encryption_mode: typing.Optional[builtins.str] = None,
            kms_key_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param job_bookmarks_encryption_mode: ``CfnSecurityConfiguration.JobBookmarksEncryptionProperty.JobBookmarksEncryptionMode``.
            :param kms_key_arn: ``CfnSecurityConfiguration.JobBookmarksEncryptionProperty.KmsKeyArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-jobbookmarksencryption.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if job_bookmarks_encryption_mode is not None:
                self._values["job_bookmarks_encryption_mode"] = job_bookmarks_encryption_mode
            if kms_key_arn is not None:
                self._values["kms_key_arn"] = kms_key_arn

        @builtins.property
        def job_bookmarks_encryption_mode(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityConfiguration.JobBookmarksEncryptionProperty.JobBookmarksEncryptionMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-jobbookmarksencryption.html#cfn-glue-securityconfiguration-jobbookmarksencryption-jobbookmarksencryptionmode
            '''
            result = self._values.get("job_bookmarks_encryption_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def kms_key_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityConfiguration.JobBookmarksEncryptionProperty.KmsKeyArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-jobbookmarksencryption.html#cfn-glue-securityconfiguration-jobbookmarksencryption-kmskeyarn
            '''
            result = self._values.get("kms_key_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "JobBookmarksEncryptionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnSecurityConfiguration.S3EncryptionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "kms_key_arn": "kmsKeyArn",
            "s3_encryption_mode": "s3EncryptionMode",
        },
    )
    class S3EncryptionProperty:
        def __init__(
            self,
            *,
            kms_key_arn: typing.Optional[builtins.str] = None,
            s3_encryption_mode: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param kms_key_arn: ``CfnSecurityConfiguration.S3EncryptionProperty.KmsKeyArn``.
            :param s3_encryption_mode: ``CfnSecurityConfiguration.S3EncryptionProperty.S3EncryptionMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-s3encryption.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if kms_key_arn is not None:
                self._values["kms_key_arn"] = kms_key_arn
            if s3_encryption_mode is not None:
                self._values["s3_encryption_mode"] = s3_encryption_mode

        @builtins.property
        def kms_key_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityConfiguration.S3EncryptionProperty.KmsKeyArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-s3encryption.html#cfn-glue-securityconfiguration-s3encryption-kmskeyarn
            '''
            result = self._values.get("kms_key_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def s3_encryption_mode(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityConfiguration.S3EncryptionProperty.S3EncryptionMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-s3encryption.html#cfn-glue-securityconfiguration-s3encryption-s3encryptionmode
            '''
            result = self._values.get("s3_encryption_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3EncryptionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnSecurityConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "encryption_configuration": "encryptionConfiguration",
        "name": "name",
    },
)
class CfnSecurityConfigurationProps:
    def __init__(
        self,
        *,
        encryption_configuration: typing.Union[CfnSecurityConfiguration.EncryptionConfigurationProperty, _IResolvable_da3f097b],
        name: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::SecurityConfiguration``.

        :param encryption_configuration: ``AWS::Glue::SecurityConfiguration.EncryptionConfiguration``.
        :param name: ``AWS::Glue::SecurityConfiguration.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "encryption_configuration": encryption_configuration,
            "name": name,
        }

    @builtins.property
    def encryption_configuration(
        self,
    ) -> typing.Union[CfnSecurityConfiguration.EncryptionConfigurationProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::SecurityConfiguration.EncryptionConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration
        '''
        result = self._values.get("encryption_configuration")
        assert result is not None, "Required property 'encryption_configuration' is missing"
        return typing.cast(typing.Union[CfnSecurityConfiguration.EncryptionConfigurationProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Glue::SecurityConfiguration.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSecurityConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnTable(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnTable",
):
    '''A CloudFormation ``AWS::Glue::Table``.

    :cloudformationResource: AWS::Glue::Table
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        catalog_id: builtins.str,
        database_name: builtins.str,
        table_input: typing.Union["CfnTable.TableInputProperty", _IResolvable_da3f097b],
    ) -> None:
        '''Create a new ``AWS::Glue::Table``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param catalog_id: ``AWS::Glue::Table.CatalogId``.
        :param database_name: ``AWS::Glue::Table.DatabaseName``.
        :param table_input: ``AWS::Glue::Table.TableInput``.
        '''
        props = CfnTableProps(
            catalog_id=catalog_id, database_name=database_name, table_input=table_input
        )

        jsii.create(CfnTable, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::Table.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-catalogid
        '''
        return typing.cast(builtins.str, jsii.get(self, "catalogId"))

    @catalog_id.setter
    def catalog_id(self, value: builtins.str) -> None:
        jsii.set(self, "catalogId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''``AWS::Glue::Table.DatabaseName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-databasename
        '''
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableInput")
    def table_input(
        self,
    ) -> typing.Union["CfnTable.TableInputProperty", _IResolvable_da3f097b]:
        '''``AWS::Glue::Table.TableInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-tableinput
        '''
        return typing.cast(typing.Union["CfnTable.TableInputProperty", _IResolvable_da3f097b], jsii.get(self, "tableInput"))

    @table_input.setter
    def table_input(
        self,
        value: typing.Union["CfnTable.TableInputProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "tableInput", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTable.ColumnProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "comment": "comment", "type": "type"},
    )
    class ColumnProperty:
        def __init__(
            self,
            *,
            name: builtins.str,
            comment: typing.Optional[builtins.str] = None,
            type: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param name: ``CfnTable.ColumnProperty.Name``.
            :param comment: ``CfnTable.ColumnProperty.Comment``.
            :param type: ``CfnTable.ColumnProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
            }
            if comment is not None:
                self._values["comment"] = comment
            if type is not None:
                self._values["type"] = type

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnTable.ColumnProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html#cfn-glue-table-column-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def comment(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.ColumnProperty.Comment``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html#cfn-glue-table-column-comment
            '''
            result = self._values.get("comment")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def type(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.ColumnProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html#cfn-glue-table-column-type
            '''
            result = self._values.get("type")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ColumnProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTable.OrderProperty",
        jsii_struct_bases=[],
        name_mapping={"column": "column", "sort_order": "sortOrder"},
    )
    class OrderProperty:
        def __init__(self, *, column: builtins.str, sort_order: jsii.Number) -> None:
            '''
            :param column: ``CfnTable.OrderProperty.Column``.
            :param sort_order: ``CfnTable.OrderProperty.SortOrder``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-order.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "column": column,
                "sort_order": sort_order,
            }

        @builtins.property
        def column(self) -> builtins.str:
            '''``CfnTable.OrderProperty.Column``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-order.html#cfn-glue-table-order-column
            '''
            result = self._values.get("column")
            assert result is not None, "Required property 'column' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def sort_order(self) -> jsii.Number:
            '''``CfnTable.OrderProperty.SortOrder``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-order.html#cfn-glue-table-order-sortorder
            '''
            result = self._values.get("sort_order")
            assert result is not None, "Required property 'sort_order' is missing"
            return typing.cast(jsii.Number, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OrderProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTable.SchemaIdProperty",
        jsii_struct_bases=[],
        name_mapping={
            "registry_name": "registryName",
            "schema_arn": "schemaArn",
            "schema_name": "schemaName",
        },
    )
    class SchemaIdProperty:
        def __init__(
            self,
            *,
            registry_name: typing.Optional[builtins.str] = None,
            schema_arn: typing.Optional[builtins.str] = None,
            schema_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param registry_name: ``CfnTable.SchemaIdProperty.RegistryName``.
            :param schema_arn: ``CfnTable.SchemaIdProperty.SchemaArn``.
            :param schema_name: ``CfnTable.SchemaIdProperty.SchemaName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-schemaid.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if registry_name is not None:
                self._values["registry_name"] = registry_name
            if schema_arn is not None:
                self._values["schema_arn"] = schema_arn
            if schema_name is not None:
                self._values["schema_name"] = schema_name

        @builtins.property
        def registry_name(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.SchemaIdProperty.RegistryName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-schemaid.html#cfn-glue-table-schemaid-registryname
            '''
            result = self._values.get("registry_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def schema_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.SchemaIdProperty.SchemaArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-schemaid.html#cfn-glue-table-schemaid-schemaarn
            '''
            result = self._values.get("schema_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def schema_name(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.SchemaIdProperty.SchemaName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-schemaid.html#cfn-glue-table-schemaid-schemaname
            '''
            result = self._values.get("schema_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SchemaIdProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTable.SchemaReferenceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "schema_id": "schemaId",
            "schema_version_id": "schemaVersionId",
            "schema_version_number": "schemaVersionNumber",
        },
    )
    class SchemaReferenceProperty:
        def __init__(
            self,
            *,
            schema_id: typing.Optional[typing.Union["CfnTable.SchemaIdProperty", _IResolvable_da3f097b]] = None,
            schema_version_id: typing.Optional[builtins.str] = None,
            schema_version_number: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param schema_id: ``CfnTable.SchemaReferenceProperty.SchemaId``.
            :param schema_version_id: ``CfnTable.SchemaReferenceProperty.SchemaVersionId``.
            :param schema_version_number: ``CfnTable.SchemaReferenceProperty.SchemaVersionNumber``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-schemareference.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if schema_id is not None:
                self._values["schema_id"] = schema_id
            if schema_version_id is not None:
                self._values["schema_version_id"] = schema_version_id
            if schema_version_number is not None:
                self._values["schema_version_number"] = schema_version_number

        @builtins.property
        def schema_id(
            self,
        ) -> typing.Optional[typing.Union["CfnTable.SchemaIdProperty", _IResolvable_da3f097b]]:
            '''``CfnTable.SchemaReferenceProperty.SchemaId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-schemareference.html#cfn-glue-table-schemareference-schemaid
            '''
            result = self._values.get("schema_id")
            return typing.cast(typing.Optional[typing.Union["CfnTable.SchemaIdProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def schema_version_id(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.SchemaReferenceProperty.SchemaVersionId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-schemareference.html#cfn-glue-table-schemareference-schemaversionid
            '''
            result = self._values.get("schema_version_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def schema_version_number(self) -> typing.Optional[jsii.Number]:
            '''``CfnTable.SchemaReferenceProperty.SchemaVersionNumber``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-schemareference.html#cfn-glue-table-schemareference-schemaversionnumber
            '''
            result = self._values.get("schema_version_number")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SchemaReferenceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTable.SerdeInfoProperty",
        jsii_struct_bases=[],
        name_mapping={
            "name": "name",
            "parameters": "parameters",
            "serialization_library": "serializationLibrary",
        },
    )
    class SerdeInfoProperty:
        def __init__(
            self,
            *,
            name: typing.Optional[builtins.str] = None,
            parameters: typing.Any = None,
            serialization_library: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param name: ``CfnTable.SerdeInfoProperty.Name``.
            :param parameters: ``CfnTable.SerdeInfoProperty.Parameters``.
            :param serialization_library: ``CfnTable.SerdeInfoProperty.SerializationLibrary``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if name is not None:
                self._values["name"] = name
            if parameters is not None:
                self._values["parameters"] = parameters
            if serialization_library is not None:
                self._values["serialization_library"] = serialization_library

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.SerdeInfoProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html#cfn-glue-table-serdeinfo-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def parameters(self) -> typing.Any:
            '''``CfnTable.SerdeInfoProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html#cfn-glue-table-serdeinfo-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Any, result)

        @builtins.property
        def serialization_library(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.SerdeInfoProperty.SerializationLibrary``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html#cfn-glue-table-serdeinfo-serializationlibrary
            '''
            result = self._values.get("serialization_library")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SerdeInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTable.SkewedInfoProperty",
        jsii_struct_bases=[],
        name_mapping={
            "skewed_column_names": "skewedColumnNames",
            "skewed_column_value_location_maps": "skewedColumnValueLocationMaps",
            "skewed_column_values": "skewedColumnValues",
        },
    )
    class SkewedInfoProperty:
        def __init__(
            self,
            *,
            skewed_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
            skewed_column_value_location_maps: typing.Any = None,
            skewed_column_values: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''
            :param skewed_column_names: ``CfnTable.SkewedInfoProperty.SkewedColumnNames``.
            :param skewed_column_value_location_maps: ``CfnTable.SkewedInfoProperty.SkewedColumnValueLocationMaps``.
            :param skewed_column_values: ``CfnTable.SkewedInfoProperty.SkewedColumnValues``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if skewed_column_names is not None:
                self._values["skewed_column_names"] = skewed_column_names
            if skewed_column_value_location_maps is not None:
                self._values["skewed_column_value_location_maps"] = skewed_column_value_location_maps
            if skewed_column_values is not None:
                self._values["skewed_column_values"] = skewed_column_values

        @builtins.property
        def skewed_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnTable.SkewedInfoProperty.SkewedColumnNames``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html#cfn-glue-table-skewedinfo-skewedcolumnnames
            '''
            result = self._values.get("skewed_column_names")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def skewed_column_value_location_maps(self) -> typing.Any:
            '''``CfnTable.SkewedInfoProperty.SkewedColumnValueLocationMaps``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html#cfn-glue-table-skewedinfo-skewedcolumnvaluelocationmaps
            '''
            result = self._values.get("skewed_column_value_location_maps")
            return typing.cast(typing.Any, result)

        @builtins.property
        def skewed_column_values(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnTable.SkewedInfoProperty.SkewedColumnValues``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html#cfn-glue-table-skewedinfo-skewedcolumnvalues
            '''
            result = self._values.get("skewed_column_values")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SkewedInfoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTable.StorageDescriptorProperty",
        jsii_struct_bases=[],
        name_mapping={
            "bucket_columns": "bucketColumns",
            "columns": "columns",
            "compressed": "compressed",
            "input_format": "inputFormat",
            "location": "location",
            "number_of_buckets": "numberOfBuckets",
            "output_format": "outputFormat",
            "parameters": "parameters",
            "schema_reference": "schemaReference",
            "serde_info": "serdeInfo",
            "skewed_info": "skewedInfo",
            "sort_columns": "sortColumns",
            "stored_as_sub_directories": "storedAsSubDirectories",
        },
    )
    class StorageDescriptorProperty:
        def __init__(
            self,
            *,
            bucket_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
            columns: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTable.ColumnProperty", _IResolvable_da3f097b]]]] = None,
            compressed: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            input_format: typing.Optional[builtins.str] = None,
            location: typing.Optional[builtins.str] = None,
            number_of_buckets: typing.Optional[jsii.Number] = None,
            output_format: typing.Optional[builtins.str] = None,
            parameters: typing.Any = None,
            schema_reference: typing.Optional[typing.Union["CfnTable.SchemaReferenceProperty", _IResolvable_da3f097b]] = None,
            serde_info: typing.Optional[typing.Union["CfnTable.SerdeInfoProperty", _IResolvable_da3f097b]] = None,
            skewed_info: typing.Optional[typing.Union["CfnTable.SkewedInfoProperty", _IResolvable_da3f097b]] = None,
            sort_columns: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTable.OrderProperty", _IResolvable_da3f097b]]]] = None,
            stored_as_sub_directories: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param bucket_columns: ``CfnTable.StorageDescriptorProperty.BucketColumns``.
            :param columns: ``CfnTable.StorageDescriptorProperty.Columns``.
            :param compressed: ``CfnTable.StorageDescriptorProperty.Compressed``.
            :param input_format: ``CfnTable.StorageDescriptorProperty.InputFormat``.
            :param location: ``CfnTable.StorageDescriptorProperty.Location``.
            :param number_of_buckets: ``CfnTable.StorageDescriptorProperty.NumberOfBuckets``.
            :param output_format: ``CfnTable.StorageDescriptorProperty.OutputFormat``.
            :param parameters: ``CfnTable.StorageDescriptorProperty.Parameters``.
            :param schema_reference: ``CfnTable.StorageDescriptorProperty.SchemaReference``.
            :param serde_info: ``CfnTable.StorageDescriptorProperty.SerdeInfo``.
            :param skewed_info: ``CfnTable.StorageDescriptorProperty.SkewedInfo``.
            :param sort_columns: ``CfnTable.StorageDescriptorProperty.SortColumns``.
            :param stored_as_sub_directories: ``CfnTable.StorageDescriptorProperty.StoredAsSubDirectories``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if bucket_columns is not None:
                self._values["bucket_columns"] = bucket_columns
            if columns is not None:
                self._values["columns"] = columns
            if compressed is not None:
                self._values["compressed"] = compressed
            if input_format is not None:
                self._values["input_format"] = input_format
            if location is not None:
                self._values["location"] = location
            if number_of_buckets is not None:
                self._values["number_of_buckets"] = number_of_buckets
            if output_format is not None:
                self._values["output_format"] = output_format
            if parameters is not None:
                self._values["parameters"] = parameters
            if schema_reference is not None:
                self._values["schema_reference"] = schema_reference
            if serde_info is not None:
                self._values["serde_info"] = serde_info
            if skewed_info is not None:
                self._values["skewed_info"] = skewed_info
            if sort_columns is not None:
                self._values["sort_columns"] = sort_columns
            if stored_as_sub_directories is not None:
                self._values["stored_as_sub_directories"] = stored_as_sub_directories

        @builtins.property
        def bucket_columns(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnTable.StorageDescriptorProperty.BucketColumns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-bucketcolumns
            '''
            result = self._values.get("bucket_columns")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def columns(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTable.ColumnProperty", _IResolvable_da3f097b]]]]:
            '''``CfnTable.StorageDescriptorProperty.Columns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-columns
            '''
            result = self._values.get("columns")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTable.ColumnProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def compressed(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnTable.StorageDescriptorProperty.Compressed``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-compressed
            '''
            result = self._values.get("compressed")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def input_format(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.StorageDescriptorProperty.InputFormat``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-inputformat
            '''
            result = self._values.get("input_format")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def location(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.StorageDescriptorProperty.Location``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-location
            '''
            result = self._values.get("location")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def number_of_buckets(self) -> typing.Optional[jsii.Number]:
            '''``CfnTable.StorageDescriptorProperty.NumberOfBuckets``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-numberofbuckets
            '''
            result = self._values.get("number_of_buckets")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def output_format(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.StorageDescriptorProperty.OutputFormat``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-outputformat
            '''
            result = self._values.get("output_format")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def parameters(self) -> typing.Any:
            '''``CfnTable.StorageDescriptorProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Any, result)

        @builtins.property
        def schema_reference(
            self,
        ) -> typing.Optional[typing.Union["CfnTable.SchemaReferenceProperty", _IResolvable_da3f097b]]:
            '''``CfnTable.StorageDescriptorProperty.SchemaReference``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-schemareference
            '''
            result = self._values.get("schema_reference")
            return typing.cast(typing.Optional[typing.Union["CfnTable.SchemaReferenceProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def serde_info(
            self,
        ) -> typing.Optional[typing.Union["CfnTable.SerdeInfoProperty", _IResolvable_da3f097b]]:
            '''``CfnTable.StorageDescriptorProperty.SerdeInfo``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-serdeinfo
            '''
            result = self._values.get("serde_info")
            return typing.cast(typing.Optional[typing.Union["CfnTable.SerdeInfoProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def skewed_info(
            self,
        ) -> typing.Optional[typing.Union["CfnTable.SkewedInfoProperty", _IResolvable_da3f097b]]:
            '''``CfnTable.StorageDescriptorProperty.SkewedInfo``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-skewedinfo
            '''
            result = self._values.get("skewed_info")
            return typing.cast(typing.Optional[typing.Union["CfnTable.SkewedInfoProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sort_columns(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTable.OrderProperty", _IResolvable_da3f097b]]]]:
            '''``CfnTable.StorageDescriptorProperty.SortColumns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-sortcolumns
            '''
            result = self._values.get("sort_columns")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTable.OrderProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def stored_as_sub_directories(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnTable.StorageDescriptorProperty.StoredAsSubDirectories``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-storedassubdirectories
            '''
            result = self._values.get("stored_as_sub_directories")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StorageDescriptorProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTable.TableIdentifierProperty",
        jsii_struct_bases=[],
        name_mapping={
            "catalog_id": "catalogId",
            "database_name": "databaseName",
            "name": "name",
        },
    )
    class TableIdentifierProperty:
        def __init__(
            self,
            *,
            catalog_id: typing.Optional[builtins.str] = None,
            database_name: typing.Optional[builtins.str] = None,
            name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param catalog_id: ``CfnTable.TableIdentifierProperty.CatalogId``.
            :param database_name: ``CfnTable.TableIdentifierProperty.DatabaseName``.
            :param name: ``CfnTable.TableIdentifierProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableidentifier.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if catalog_id is not None:
                self._values["catalog_id"] = catalog_id
            if database_name is not None:
                self._values["database_name"] = database_name
            if name is not None:
                self._values["name"] = name

        @builtins.property
        def catalog_id(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.TableIdentifierProperty.CatalogId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableidentifier.html#cfn-glue-table-tableidentifier-catalogid
            '''
            result = self._values.get("catalog_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def database_name(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.TableIdentifierProperty.DatabaseName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableidentifier.html#cfn-glue-table-tableidentifier-databasename
            '''
            result = self._values.get("database_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.TableIdentifierProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableidentifier.html#cfn-glue-table-tableidentifier-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TableIdentifierProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTable.TableInputProperty",
        jsii_struct_bases=[],
        name_mapping={
            "description": "description",
            "name": "name",
            "owner": "owner",
            "parameters": "parameters",
            "partition_keys": "partitionKeys",
            "retention": "retention",
            "storage_descriptor": "storageDescriptor",
            "table_type": "tableType",
            "target_table": "targetTable",
            "view_expanded_text": "viewExpandedText",
            "view_original_text": "viewOriginalText",
        },
    )
    class TableInputProperty:
        def __init__(
            self,
            *,
            description: typing.Optional[builtins.str] = None,
            name: typing.Optional[builtins.str] = None,
            owner: typing.Optional[builtins.str] = None,
            parameters: typing.Any = None,
            partition_keys: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTable.ColumnProperty", _IResolvable_da3f097b]]]] = None,
            retention: typing.Optional[jsii.Number] = None,
            storage_descriptor: typing.Optional[typing.Union["CfnTable.StorageDescriptorProperty", _IResolvable_da3f097b]] = None,
            table_type: typing.Optional[builtins.str] = None,
            target_table: typing.Optional[typing.Union["CfnTable.TableIdentifierProperty", _IResolvable_da3f097b]] = None,
            view_expanded_text: typing.Optional[builtins.str] = None,
            view_original_text: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param description: ``CfnTable.TableInputProperty.Description``.
            :param name: ``CfnTable.TableInputProperty.Name``.
            :param owner: ``CfnTable.TableInputProperty.Owner``.
            :param parameters: ``CfnTable.TableInputProperty.Parameters``.
            :param partition_keys: ``CfnTable.TableInputProperty.PartitionKeys``.
            :param retention: ``CfnTable.TableInputProperty.Retention``.
            :param storage_descriptor: ``CfnTable.TableInputProperty.StorageDescriptor``.
            :param table_type: ``CfnTable.TableInputProperty.TableType``.
            :param target_table: ``CfnTable.TableInputProperty.TargetTable``.
            :param view_expanded_text: ``CfnTable.TableInputProperty.ViewExpandedText``.
            :param view_original_text: ``CfnTable.TableInputProperty.ViewOriginalText``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if description is not None:
                self._values["description"] = description
            if name is not None:
                self._values["name"] = name
            if owner is not None:
                self._values["owner"] = owner
            if parameters is not None:
                self._values["parameters"] = parameters
            if partition_keys is not None:
                self._values["partition_keys"] = partition_keys
            if retention is not None:
                self._values["retention"] = retention
            if storage_descriptor is not None:
                self._values["storage_descriptor"] = storage_descriptor
            if table_type is not None:
                self._values["table_type"] = table_type
            if target_table is not None:
                self._values["target_table"] = target_table
            if view_expanded_text is not None:
                self._values["view_expanded_text"] = view_expanded_text
            if view_original_text is not None:
                self._values["view_original_text"] = view_original_text

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.TableInputProperty.Description``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-description
            '''
            result = self._values.get("description")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.TableInputProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def owner(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.TableInputProperty.Owner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-owner
            '''
            result = self._values.get("owner")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def parameters(self) -> typing.Any:
            '''``CfnTable.TableInputProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Any, result)

        @builtins.property
        def partition_keys(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTable.ColumnProperty", _IResolvable_da3f097b]]]]:
            '''``CfnTable.TableInputProperty.PartitionKeys``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-partitionkeys
            '''
            result = self._values.get("partition_keys")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTable.ColumnProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def retention(self) -> typing.Optional[jsii.Number]:
            '''``CfnTable.TableInputProperty.Retention``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-retention
            '''
            result = self._values.get("retention")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def storage_descriptor(
            self,
        ) -> typing.Optional[typing.Union["CfnTable.StorageDescriptorProperty", _IResolvable_da3f097b]]:
            '''``CfnTable.TableInputProperty.StorageDescriptor``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-storagedescriptor
            '''
            result = self._values.get("storage_descriptor")
            return typing.cast(typing.Optional[typing.Union["CfnTable.StorageDescriptorProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def table_type(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.TableInputProperty.TableType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-tabletype
            '''
            result = self._values.get("table_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def target_table(
            self,
        ) -> typing.Optional[typing.Union["CfnTable.TableIdentifierProperty", _IResolvable_da3f097b]]:
            '''``CfnTable.TableInputProperty.TargetTable``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-targettable
            '''
            result = self._values.get("target_table")
            return typing.cast(typing.Optional[typing.Union["CfnTable.TableIdentifierProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def view_expanded_text(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.TableInputProperty.ViewExpandedText``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-viewexpandedtext
            '''
            result = self._values.get("view_expanded_text")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def view_original_text(self) -> typing.Optional[builtins.str]:
            '''``CfnTable.TableInputProperty.ViewOriginalText``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-vieworiginaltext
            '''
            result = self._values.get("view_original_text")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TableInputProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnTableProps",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_id": "catalogId",
        "database_name": "databaseName",
        "table_input": "tableInput",
    },
)
class CfnTableProps:
    def __init__(
        self,
        *,
        catalog_id: builtins.str,
        database_name: builtins.str,
        table_input: typing.Union[CfnTable.TableInputProperty, _IResolvable_da3f097b],
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Table``.

        :param catalog_id: ``AWS::Glue::Table.CatalogId``.
        :param database_name: ``AWS::Glue::Table.DatabaseName``.
        :param table_input: ``AWS::Glue::Table.TableInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "catalog_id": catalog_id,
            "database_name": database_name,
            "table_input": table_input,
        }

    @builtins.property
    def catalog_id(self) -> builtins.str:
        '''``AWS::Glue::Table.CatalogId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-catalogid
        '''
        result = self._values.get("catalog_id")
        assert result is not None, "Required property 'catalog_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''``AWS::Glue::Table.DatabaseName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-databasename
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_input(
        self,
    ) -> typing.Union[CfnTable.TableInputProperty, _IResolvable_da3f097b]:
        '''``AWS::Glue::Table.TableInput``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-tableinput
        '''
        result = self._values.get("table_input")
        assert result is not None, "Required property 'table_input' is missing"
        return typing.cast(typing.Union[CfnTable.TableInputProperty, _IResolvable_da3f097b], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnTableProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnTrigger(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnTrigger",
):
    '''A CloudFormation ``AWS::Glue::Trigger``.

    :cloudformationResource: AWS::Glue::Trigger
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        actions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTrigger.ActionProperty", _IResolvable_da3f097b]]],
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        predicate: typing.Optional[typing.Union["CfnTrigger.PredicateProperty", _IResolvable_da3f097b]] = None,
        schedule: typing.Optional[builtins.str] = None,
        start_on_creation: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        tags: typing.Any = None,
        workflow_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Glue::Trigger``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param actions: ``AWS::Glue::Trigger.Actions``.
        :param type: ``AWS::Glue::Trigger.Type``.
        :param description: ``AWS::Glue::Trigger.Description``.
        :param name: ``AWS::Glue::Trigger.Name``.
        :param predicate: ``AWS::Glue::Trigger.Predicate``.
        :param schedule: ``AWS::Glue::Trigger.Schedule``.
        :param start_on_creation: ``AWS::Glue::Trigger.StartOnCreation``.
        :param tags: ``AWS::Glue::Trigger.Tags``.
        :param workflow_name: ``AWS::Glue::Trigger.WorkflowName``.
        '''
        props = CfnTriggerProps(
            actions=actions,
            type=type,
            description=description,
            name=name,
            predicate=predicate,
            schedule=schedule,
            start_on_creation=start_on_creation,
            tags=tags,
            workflow_name=workflow_name,
        )

        jsii.create(CfnTrigger, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Glue::Trigger.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTrigger.ActionProperty", _IResolvable_da3f097b]]]:
        '''``AWS::Glue::Trigger.Actions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-actions
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTrigger.ActionProperty", _IResolvable_da3f097b]]], jsii.get(self, "actions"))

    @actions.setter
    def actions(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTrigger.ActionProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "actions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''``AWS::Glue::Trigger.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-type
        '''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Trigger.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Trigger.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="predicate")
    def predicate(
        self,
    ) -> typing.Optional[typing.Union["CfnTrigger.PredicateProperty", _IResolvable_da3f097b]]:
        '''``AWS::Glue::Trigger.Predicate``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-predicate
        '''
        return typing.cast(typing.Optional[typing.Union["CfnTrigger.PredicateProperty", _IResolvable_da3f097b]], jsii.get(self, "predicate"))

    @predicate.setter
    def predicate(
        self,
        value: typing.Optional[typing.Union["CfnTrigger.PredicateProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "predicate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Trigger.Schedule``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-schedule
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schedule"))

    @schedule.setter
    def schedule(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "schedule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startOnCreation")
    def start_on_creation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Trigger.StartOnCreation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-startoncreation
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "startOnCreation"))

    @start_on_creation.setter
    def start_on_creation(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "startOnCreation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowName")
    def workflow_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Trigger.WorkflowName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-workflowname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workflowName"))

    @workflow_name.setter
    def workflow_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "workflowName", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTrigger.ActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "arguments": "arguments",
            "crawler_name": "crawlerName",
            "job_name": "jobName",
            "notification_property": "notificationProperty",
            "security_configuration": "securityConfiguration",
            "timeout": "timeout",
        },
    )
    class ActionProperty:
        def __init__(
            self,
            *,
            arguments: typing.Any = None,
            crawler_name: typing.Optional[builtins.str] = None,
            job_name: typing.Optional[builtins.str] = None,
            notification_property: typing.Optional[typing.Union["CfnTrigger.NotificationPropertyProperty", _IResolvable_da3f097b]] = None,
            security_configuration: typing.Optional[builtins.str] = None,
            timeout: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param arguments: ``CfnTrigger.ActionProperty.Arguments``.
            :param crawler_name: ``CfnTrigger.ActionProperty.CrawlerName``.
            :param job_name: ``CfnTrigger.ActionProperty.JobName``.
            :param notification_property: ``CfnTrigger.ActionProperty.NotificationProperty``.
            :param security_configuration: ``CfnTrigger.ActionProperty.SecurityConfiguration``.
            :param timeout: ``CfnTrigger.ActionProperty.Timeout``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if arguments is not None:
                self._values["arguments"] = arguments
            if crawler_name is not None:
                self._values["crawler_name"] = crawler_name
            if job_name is not None:
                self._values["job_name"] = job_name
            if notification_property is not None:
                self._values["notification_property"] = notification_property
            if security_configuration is not None:
                self._values["security_configuration"] = security_configuration
            if timeout is not None:
                self._values["timeout"] = timeout

        @builtins.property
        def arguments(self) -> typing.Any:
            '''``CfnTrigger.ActionProperty.Arguments``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-arguments
            '''
            result = self._values.get("arguments")
            return typing.cast(typing.Any, result)

        @builtins.property
        def crawler_name(self) -> typing.Optional[builtins.str]:
            '''``CfnTrigger.ActionProperty.CrawlerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-crawlername
            '''
            result = self._values.get("crawler_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def job_name(self) -> typing.Optional[builtins.str]:
            '''``CfnTrigger.ActionProperty.JobName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-jobname
            '''
            result = self._values.get("job_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def notification_property(
            self,
        ) -> typing.Optional[typing.Union["CfnTrigger.NotificationPropertyProperty", _IResolvable_da3f097b]]:
            '''``CfnTrigger.ActionProperty.NotificationProperty``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-notificationproperty
            '''
            result = self._values.get("notification_property")
            return typing.cast(typing.Optional[typing.Union["CfnTrigger.NotificationPropertyProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def security_configuration(self) -> typing.Optional[builtins.str]:
            '''``CfnTrigger.ActionProperty.SecurityConfiguration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-securityconfiguration
            '''
            result = self._values.get("security_configuration")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def timeout(self) -> typing.Optional[jsii.Number]:
            '''``CfnTrigger.ActionProperty.Timeout``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-timeout
            '''
            result = self._values.get("timeout")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTrigger.ConditionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "crawler_name": "crawlerName",
            "crawl_state": "crawlState",
            "job_name": "jobName",
            "logical_operator": "logicalOperator",
            "state": "state",
        },
    )
    class ConditionProperty:
        def __init__(
            self,
            *,
            crawler_name: typing.Optional[builtins.str] = None,
            crawl_state: typing.Optional[builtins.str] = None,
            job_name: typing.Optional[builtins.str] = None,
            logical_operator: typing.Optional[builtins.str] = None,
            state: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param crawler_name: ``CfnTrigger.ConditionProperty.CrawlerName``.
            :param crawl_state: ``CfnTrigger.ConditionProperty.CrawlState``.
            :param job_name: ``CfnTrigger.ConditionProperty.JobName``.
            :param logical_operator: ``CfnTrigger.ConditionProperty.LogicalOperator``.
            :param state: ``CfnTrigger.ConditionProperty.State``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if crawler_name is not None:
                self._values["crawler_name"] = crawler_name
            if crawl_state is not None:
                self._values["crawl_state"] = crawl_state
            if job_name is not None:
                self._values["job_name"] = job_name
            if logical_operator is not None:
                self._values["logical_operator"] = logical_operator
            if state is not None:
                self._values["state"] = state

        @builtins.property
        def crawler_name(self) -> typing.Optional[builtins.str]:
            '''``CfnTrigger.ConditionProperty.CrawlerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-crawlername
            '''
            result = self._values.get("crawler_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def crawl_state(self) -> typing.Optional[builtins.str]:
            '''``CfnTrigger.ConditionProperty.CrawlState``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-crawlstate
            '''
            result = self._values.get("crawl_state")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def job_name(self) -> typing.Optional[builtins.str]:
            '''``CfnTrigger.ConditionProperty.JobName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-jobname
            '''
            result = self._values.get("job_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def logical_operator(self) -> typing.Optional[builtins.str]:
            '''``CfnTrigger.ConditionProperty.LogicalOperator``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-logicaloperator
            '''
            result = self._values.get("logical_operator")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def state(self) -> typing.Optional[builtins.str]:
            '''``CfnTrigger.ConditionProperty.State``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-state
            '''
            result = self._values.get("state")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConditionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTrigger.NotificationPropertyProperty",
        jsii_struct_bases=[],
        name_mapping={"notify_delay_after": "notifyDelayAfter"},
    )
    class NotificationPropertyProperty:
        def __init__(
            self,
            *,
            notify_delay_after: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param notify_delay_after: ``CfnTrigger.NotificationPropertyProperty.NotifyDelayAfter``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-notificationproperty.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if notify_delay_after is not None:
                self._values["notify_delay_after"] = notify_delay_after

        @builtins.property
        def notify_delay_after(self) -> typing.Optional[jsii.Number]:
            '''``CfnTrigger.NotificationPropertyProperty.NotifyDelayAfter``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-notificationproperty.html#cfn-glue-trigger-notificationproperty-notifydelayafter
            '''
            result = self._values.get("notify_delay_after")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "NotificationPropertyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_glue.CfnTrigger.PredicateProperty",
        jsii_struct_bases=[],
        name_mapping={"conditions": "conditions", "logical": "logical"},
    )
    class PredicateProperty:
        def __init__(
            self,
            *,
            conditions: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTrigger.ConditionProperty", _IResolvable_da3f097b]]]] = None,
            logical: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param conditions: ``CfnTrigger.PredicateProperty.Conditions``.
            :param logical: ``CfnTrigger.PredicateProperty.Logical``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-predicate.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if conditions is not None:
                self._values["conditions"] = conditions
            if logical is not None:
                self._values["logical"] = logical

        @builtins.property
        def conditions(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTrigger.ConditionProperty", _IResolvable_da3f097b]]]]:
            '''``CfnTrigger.PredicateProperty.Conditions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-predicate.html#cfn-glue-trigger-predicate-conditions
            '''
            result = self._values.get("conditions")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTrigger.ConditionProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def logical(self) -> typing.Optional[builtins.str]:
            '''``CfnTrigger.PredicateProperty.Logical``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-predicate.html#cfn-glue-trigger-predicate-logical
            '''
            result = self._values.get("logical")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PredicateProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnTriggerProps",
    jsii_struct_bases=[],
    name_mapping={
        "actions": "actions",
        "type": "type",
        "description": "description",
        "name": "name",
        "predicate": "predicate",
        "schedule": "schedule",
        "start_on_creation": "startOnCreation",
        "tags": "tags",
        "workflow_name": "workflowName",
    },
)
class CfnTriggerProps:
    def __init__(
        self,
        *,
        actions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnTrigger.ActionProperty, _IResolvable_da3f097b]]],
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        predicate: typing.Optional[typing.Union[CfnTrigger.PredicateProperty, _IResolvable_da3f097b]] = None,
        schedule: typing.Optional[builtins.str] = None,
        start_on_creation: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        tags: typing.Any = None,
        workflow_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Trigger``.

        :param actions: ``AWS::Glue::Trigger.Actions``.
        :param type: ``AWS::Glue::Trigger.Type``.
        :param description: ``AWS::Glue::Trigger.Description``.
        :param name: ``AWS::Glue::Trigger.Name``.
        :param predicate: ``AWS::Glue::Trigger.Predicate``.
        :param schedule: ``AWS::Glue::Trigger.Schedule``.
        :param start_on_creation: ``AWS::Glue::Trigger.StartOnCreation``.
        :param tags: ``AWS::Glue::Trigger.Tags``.
        :param workflow_name: ``AWS::Glue::Trigger.WorkflowName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "actions": actions,
            "type": type,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if predicate is not None:
            self._values["predicate"] = predicate
        if schedule is not None:
            self._values["schedule"] = schedule
        if start_on_creation is not None:
            self._values["start_on_creation"] = start_on_creation
        if tags is not None:
            self._values["tags"] = tags
        if workflow_name is not None:
            self._values["workflow_name"] = workflow_name

    @builtins.property
    def actions(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnTrigger.ActionProperty, _IResolvable_da3f097b]]]:
        '''``AWS::Glue::Trigger.Actions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-actions
        '''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnTrigger.ActionProperty, _IResolvable_da3f097b]]], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''``AWS::Glue::Trigger.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Trigger.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Trigger.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def predicate(
        self,
    ) -> typing.Optional[typing.Union[CfnTrigger.PredicateProperty, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Trigger.Predicate``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-predicate
        '''
        result = self._values.get("predicate")
        return typing.cast(typing.Optional[typing.Union[CfnTrigger.PredicateProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def schedule(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Trigger.Schedule``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-schedule
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_on_creation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::Glue::Trigger.StartOnCreation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-startoncreation
        '''
        result = self._values.get("start_on_creation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Glue::Trigger.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    @builtins.property
    def workflow_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Trigger.WorkflowName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-workflowname
        '''
        result = self._values.get("workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnTriggerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnWorkflow(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_glue.CfnWorkflow",
):
    '''A CloudFormation ``AWS::Glue::Workflow``.

    :cloudformationResource: AWS::Glue::Workflow
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        default_run_properties: typing.Any = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Glue::Workflow``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param default_run_properties: ``AWS::Glue::Workflow.DefaultRunProperties``.
        :param description: ``AWS::Glue::Workflow.Description``.
        :param name: ``AWS::Glue::Workflow.Name``.
        :param tags: ``AWS::Glue::Workflow.Tags``.
        '''
        props = CfnWorkflowProps(
            default_run_properties=default_run_properties,
            description=description,
            name=name,
            tags=tags,
        )

        jsii.create(CfnWorkflow, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Glue::Workflow.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html#cfn-glue-workflow-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRunProperties")
    def default_run_properties(self) -> typing.Any:
        '''``AWS::Glue::Workflow.DefaultRunProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html#cfn-glue-workflow-defaultrunproperties
        '''
        return typing.cast(typing.Any, jsii.get(self, "defaultRunProperties"))

    @default_run_properties.setter
    def default_run_properties(self, value: typing.Any) -> None:
        jsii.set(self, "defaultRunProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Workflow.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html#cfn-glue-workflow-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Workflow.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html#cfn-glue-workflow-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_glue.CfnWorkflowProps",
    jsii_struct_bases=[],
    name_mapping={
        "default_run_properties": "defaultRunProperties",
        "description": "description",
        "name": "name",
        "tags": "tags",
    },
)
class CfnWorkflowProps:
    def __init__(
        self,
        *,
        default_run_properties: typing.Any = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Glue::Workflow``.

        :param default_run_properties: ``AWS::Glue::Workflow.DefaultRunProperties``.
        :param description: ``AWS::Glue::Workflow.Description``.
        :param name: ``AWS::Glue::Workflow.Name``.
        :param tags: ``AWS::Glue::Workflow.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if default_run_properties is not None:
            self._values["default_run_properties"] = default_run_properties
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def default_run_properties(self) -> typing.Any:
        '''``AWS::Glue::Workflow.DefaultRunProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html#cfn-glue-workflow-defaultrunproperties
        '''
        result = self._values.get("default_run_properties")
        return typing.cast(typing.Any, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Workflow.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html#cfn-glue-workflow-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::Glue::Workflow.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html#cfn-glue-workflow-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Glue::Workflow.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-workflow.html#cfn-glue-workflow-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnWorkflowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnClassifier",
    "CfnClassifierProps",
    "CfnConnection",
    "CfnConnectionProps",
    "CfnCrawler",
    "CfnCrawlerProps",
    "CfnDataCatalogEncryptionSettings",
    "CfnDataCatalogEncryptionSettingsProps",
    "CfnDatabase",
    "CfnDatabaseProps",
    "CfnDevEndpoint",
    "CfnDevEndpointProps",
    "CfnJob",
    "CfnJobProps",
    "CfnMLTransform",
    "CfnMLTransformProps",
    "CfnPartition",
    "CfnPartitionProps",
    "CfnRegistry",
    "CfnRegistryProps",
    "CfnSchema",
    "CfnSchemaProps",
    "CfnSchemaVersion",
    "CfnSchemaVersionMetadata",
    "CfnSchemaVersionMetadataProps",
    "CfnSchemaVersionProps",
    "CfnSecurityConfiguration",
    "CfnSecurityConfigurationProps",
    "CfnTable",
    "CfnTableProps",
    "CfnTrigger",
    "CfnTriggerProps",
    "CfnWorkflow",
    "CfnWorkflowProps",
]

publication.publish()
