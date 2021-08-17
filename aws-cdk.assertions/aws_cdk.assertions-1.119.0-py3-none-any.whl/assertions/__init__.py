'''
# Assertions

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

Functions for writing test asserting against CDK applications, with focus on CloudFormation templates.

The `Template` class includes a set of methods for writing assertions against CloudFormation templates. Use one of the `Template.fromXxx()` static methods to create an instance of this class.

To create `Template` from CDK stack, start off with:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import Stack
from aws_cdk.assertions import Template

stack = Stack(...)
assert = Template.from_stack(stack)
```

Alternatively, assertions can be run on an existing CloudFormation template -

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
template = fs.read_file_sync("/path/to/template/file")
assert = Template.from_string(template)
```

## Full Template Match

The simplest assertion would be to assert that the template matches a given
template.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
assert.template_matches(
    Resources={
        "Type": "Foo::Bar",
        "Properties": {
            "Baz": "Qux"
        }
    }
)
```

The `Template` class also supports [snapshot
testing](https://jestjs.io/docs/snapshot-testing) using jest.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
# using jest
expect(Template.from_stack(stack)).to_match_snapshot()
```

For non-javascript languages, the `toJSON()` can be called to get an in-memory object
of the template.

## Counting Resources

This module allows asserting the number of resources of a specific type found
in a template.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
assert.resource_count_is("Foo::Bar", 2)
```

## Resource Matching & Retrieval

Beyond resource counting, the module also allows asserting that a resource with
specific properties are present.

The following code asserts that the `Properties` section of a resource of type
`Foo::Bar` contains the specified properties -

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
assert.has_resource_properties("Foo::Bar",
    Foo="Bar",
    Baz=5,
    Qux=["Waldo", "Fred"]
)
```

Alternatively, if you would like to assert the entire resource definition, you
can use the `hasResource()` API.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
assert.has_resource("Foo::Bar",
    Properties={"Foo": "Bar"},
    DependsOn=["Waldo", "Fred"]
)
```

Beyond assertions, the module provides APIs to retrieve matching resources.
The `findResources()` API is complementary to the `hasResource()` API, except,
instead of asserting its presence, it returns the set of matching resources.

By default, the `hasResource()` and `hasResourceProperties()` APIs perform deep
partial object matching. This behavior can be configured using matchers.
See subsequent section on [special matchers](#special-matchers).

## Special Matchers

The expectation provided to the `hasResourceXXX()` methods, besides carrying
literal values, as seen in the above examples, can also have special matchers
encoded.
They are available as part of the `Match` class.

### Object Matchers

The `Match.objectLike()` API can be used to assert that the target is a superset
object of the provided pattern.
This API will perform a deep partial match on the target.
Deep partial matching is where objects are matched partially recursively. At each
level, the list of keys in the target is a subset of the provided pattern.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
# Given a template -
# {
#   "Resources": {
#     "MyBar": {
#       "Type": "Foo::Bar",
#       "Properties": {
#         "Fred": {
#           "Wobble": "Flob",
#           "Bob": "Cat"
#         }
#       }
#     }
#   }
# }

# The following will NOT throw an assertion error
assert.has_resource_properties("Foo::Bar",
    Fred=Match.object_like(
        Wobble="Flob"
    )
)

# The following will throw an assertion error
assert.has_resource_properties("Foo::Bar",
    Fred=Match.object_like(
        Brew="Coffee"
    )
)
```

The `Match.objectEquals()` API can be used to assert a target as a deep exact
match.

In addition, the `Match.absentProperty()` can be used to specify that a specific
property should not exist on the target. This can be used within `Match.objectLike()`
or outside of any matchers.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
# Given a template -
# {
#   "Resources": {
#     "MyBar": {
#       "Type": "Foo::Bar",
#       "Properties": {
#         "Fred": {
#           "Wobble": "Flob",
#         }
#       }
#     }
#   }
# }

# The following will NOT throw an assertion error
assert.has_resource_properties("Foo::Bar",
    Fred=Match.object_like(
        Bob=Match.absent_property()
    )
)

# The following will throw an assertion error
assert.has_resource_properties("Foo::Bar",
    Fred=Match.object_like(
        Wobble=Match.absent_property()
    )
)
```

### Array Matchers

The `Match.arrayWith()` API can be used to assert that the target is equal to or a subset
of the provided pattern array.
This API will perform subset match on the target.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
# Given a template -
# {
#   "Resources": {
#     "MyBar": {
#       "Type": "Foo::Bar",
#       "Properties": {
#         "Fred": ["Flob", "Cat"]
#       }
#     }
#   }
# }

# The following will NOT throw an assertion error
assert.has_resource_properties("Foo::Bar",
    Fred=Match.array_with(["Flob"])
)

# The following will throw an assertion error
assert.has_resource_properties("Foo::Bar", Match.object_like(
    Fred=Match.array_with(["Wobble"])
));
```

*Note:* The list of items in the pattern array should be in order as they appear in the
target array. Out of order will be recorded as a match failure.

Alternatively, the `Match.arrayEquals()` API can be used to assert that the target is
exactly equal to the pattern array.

## Strongly typed languages

Some of the APIs documented above, such as `templateMatches()` and
`hasResourceProperties()` accept fluently an arbitrary JSON (like) structure
its parameter.
This fluency is available only in dynamically typed languages like javascript
and Python.

For strongly typed languages, like Java, you can achieve similar fluency using
any popular JSON deserializer. The following Java example uses `Gson` -

```java
// In Java, using text blocks and Gson
import com.google.gson.Gson;

String json = """
  {
    "Foo": "Bar",
    "Baz": 5,
    "Qux": [ "Waldo", "Fred" ],
  } """;

Map expected = new Gson().fromJson(json, Map.class);
assert.hasResourceProperties("Foo::Bar", expected);
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


class Match(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/assertions.Match"):
    '''(experimental) Partial and special matching during template assertions.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(Match, self, [])

    @jsii.member(jsii_name="absentProperty") # type: ignore[misc]
    @builtins.classmethod
    def absent_property(cls) -> builtins.str:
        '''(experimental) Use this matcher in the place of a field's value, if the field must not be present.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sinvoke(cls, "absentProperty", []))

    @jsii.member(jsii_name="arrayEquals") # type: ignore[misc]
    @builtins.classmethod
    def array_equals(cls, pattern: typing.Sequence[typing.Any]) -> "Matcher":
        '''(experimental) Matches the specified pattern with the array found in the same relative path of the target.

        The set of elements (or matchers) must match exactly and in order.

        :param pattern: the pattern to match.

        :stability: experimental
        '''
        return typing.cast("Matcher", jsii.sinvoke(cls, "arrayEquals", [pattern]))

    @jsii.member(jsii_name="arrayWith") # type: ignore[misc]
    @builtins.classmethod
    def array_with(cls, pattern: typing.Sequence[typing.Any]) -> "Matcher":
        '''(experimental) Matches the specified pattern with the array found in the same relative path of the target.

        The set of elements (or matchers) must be in the same order as would be found.

        :param pattern: the pattern to match.

        :stability: experimental
        '''
        return typing.cast("Matcher", jsii.sinvoke(cls, "arrayWith", [pattern]))

    @jsii.member(jsii_name="exact") # type: ignore[misc]
    @builtins.classmethod
    def exact(cls, pattern: typing.Any) -> "Matcher":
        '''(experimental) Deep exact matching of the specified pattern to the target.

        :param pattern: the pattern to match.

        :stability: experimental
        '''
        return typing.cast("Matcher", jsii.sinvoke(cls, "exact", [pattern]))

    @jsii.member(jsii_name="objectEquals") # type: ignore[misc]
    @builtins.classmethod
    def object_equals(
        cls,
        pattern: typing.Mapping[builtins.str, typing.Any],
    ) -> "Matcher":
        '''(experimental) Matches the specified pattern to an object found in the same relative path of the target.

        The keys and their values (or matchers) must match exactly with the target.

        :param pattern: the pattern to match.

        :stability: experimental
        '''
        return typing.cast("Matcher", jsii.sinvoke(cls, "objectEquals", [pattern]))

    @jsii.member(jsii_name="objectLike") # type: ignore[misc]
    @builtins.classmethod
    def object_like(
        cls,
        pattern: typing.Mapping[builtins.str, typing.Any],
    ) -> "Matcher":
        '''(experimental) Matches the specified pattern to an object found in the same relative path of the target.

        The keys and their values (or matchers) must be present in the target but the target can be a superset.

        :param pattern: the pattern to match.

        :stability: experimental
        '''
        return typing.cast("Matcher", jsii.sinvoke(cls, "objectLike", [pattern]))


class _MatchProxy(Match):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Match).__jsii_proxy_class__ = lambda : _MatchProxy


class MatchResult(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/assertions.MatchResult"):
    '''(experimental) The result of ``Match.test()``.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(MatchResult, self, [])

    @jsii.member(jsii_name="compose")
    def compose(self, id: builtins.str, inner: "MatchResult") -> "MatchResult":
        '''(experimental) Compose the results of a previous match as a subtree.

        :param id: the id of the parent tree.
        :param inner: -

        :stability: experimental
        '''
        return typing.cast("MatchResult", jsii.invoke(self, "compose", [id, inner]))

    @jsii.member(jsii_name="hasFailed")
    def has_failed(self) -> builtins.bool:
        '''(experimental) Does the result contain any failures.

        If not, the result is a success

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "hasFailed", []))

    @jsii.member(jsii_name="push")
    def push(
        self,
        matcher: "Matcher",
        path: typing.Sequence[builtins.str],
        message: builtins.str,
    ) -> "MatchResult":
        '''(experimental) Push a new failure into this result at a specific path.

        If the failure occurred at root of the match tree, set the path to an empty list.
        If it occurs in the 5th index of an array nested within the 'foo' key of an object,
        set the path as ``['/foo', '[5]']``.

        :param matcher: -
        :param path: the path at which the failure occurred.
        :param message: the failure.

        :stability: experimental
        '''
        return typing.cast("MatchResult", jsii.invoke(self, "push", [matcher, path, message]))

    @jsii.member(jsii_name="toHumanStrings")
    def to_human_strings(self) -> typing.List[builtins.str]:
        '''(experimental) Get the list of failures as human readable strings.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "toHumanStrings", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failCount")
    def fail_count(self) -> jsii.Number:
        '''(experimental) The number of failures.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "failCount"))


class Matcher(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/assertions.Matcher",
):
    '''(experimental) Represents a matcher that can perform special data matching capabilities between a given pattern and a target.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(Matcher, self, [])

    @jsii.member(jsii_name="isMatcher") # type: ignore[misc]
    @builtins.classmethod
    def is_matcher(cls, x: typing.Any) -> builtins.bool:
        '''(experimental) Check whether the provided object is a subtype of the ``IMatcher``.

        :param x: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isMatcher", [x]))

    @jsii.member(jsii_name="test") # type: ignore[misc]
    @abc.abstractmethod
    def test(self, actual: typing.Any) -> MatchResult:
        '''(experimental) Test whether a target matches the provided pattern.

        :param actual: the target to match.

        :return: the list of match failures. An empty array denotes a successful match.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    @abc.abstractmethod
    def name(self) -> builtins.str:
        '''(experimental) A name for the matcher.

        This is collected as part of the result and may be presented to the user.

        :stability: experimental
        '''
        ...


class _MatcherProxy(Matcher):
    @jsii.member(jsii_name="test")
    def test(self, actual: typing.Any) -> MatchResult:
        '''(experimental) Test whether a target matches the provided pattern.

        :param actual: the target to match.

        :return: the list of match failures. An empty array denotes a successful match.

        :stability: experimental
        '''
        return typing.cast(MatchResult, jsii.invoke(self, "test", [actual]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) A name for the matcher.

        This is collected as part of the result and may be presented to the user.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Matcher).__jsii_proxy_class__ = lambda : _MatcherProxy


class Template(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/assertions.Template"):
    '''(experimental) Suite of assertions that can be run on a CDK stack.

    Typically used, as part of unit tests, to validate that the rendered
    CloudFormation template has expected resources and properties.

    :stability: experimental
    '''

    @jsii.member(jsii_name="fromJSON") # type: ignore[misc]
    @builtins.classmethod
    def from_json(
        cls,
        template: typing.Mapping[builtins.str, typing.Any],
    ) -> "Template":
        '''(experimental) Base your assertions from an existing CloudFormation template formatted as an in-memory JSON object.

        :param template: the CloudFormation template formatted as a nested set of records.

        :stability: experimental
        '''
        return typing.cast("Template", jsii.sinvoke(cls, "fromJSON", [template]))

    @jsii.member(jsii_name="fromStack") # type: ignore[misc]
    @builtins.classmethod
    def from_stack(cls, stack: aws_cdk.core.Stack) -> "Template":
        '''(experimental) Base your assertions on the CloudFormation template synthesized by a CDK ``Stack``.

        :param stack: the CDK Stack to run assertions on.

        :stability: experimental
        '''
        return typing.cast("Template", jsii.sinvoke(cls, "fromStack", [stack]))

    @jsii.member(jsii_name="fromString") # type: ignore[misc]
    @builtins.classmethod
    def from_string(cls, template: builtins.str) -> "Template":
        '''(experimental) Base your assertions from an existing CloudFormation template formatted as a JSON string.

        :param template: the CloudFormation template in.

        :stability: experimental
        '''
        return typing.cast("Template", jsii.sinvoke(cls, "fromString", [template]))

    @jsii.member(jsii_name="findResources")
    def find_resources(
        self,
        type: builtins.str,
        props: typing.Any = None,
    ) -> typing.List[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Get the set of matching resources of a given type and properties in the CloudFormation template.

        :param type: the type to match in the CloudFormation template.
        :param props: by default, matches all resources with the given type. When a literal is provided, performs a partial match via ``Match.objectLike()``. Use the ``Match`` APIs to configure a different behaviour.

        :stability: experimental
        '''
        return typing.cast(typing.List[typing.Mapping[builtins.str, typing.Any]], jsii.invoke(self, "findResources", [type, props]))

    @jsii.member(jsii_name="hasResource")
    def has_resource(self, type: builtins.str, props: typing.Any) -> None:
        '''(experimental) Assert that a resource of the given type and given definition exists in the CloudFormation template.

        By default, performs partial matching on the resource, via the ``Match.objectLike()``.
        To configure different behavour, use other matchers in the ``Match`` class.

        :param type: the resource type; ex: ``AWS::S3::Bucket``
        :param props: the entire defintion of the resource as should be expected in the template.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "hasResource", [type, props]))

    @jsii.member(jsii_name="hasResourceProperties")
    def has_resource_properties(self, type: builtins.str, props: typing.Any) -> None:
        '''(experimental) Assert that a resource of the given type and properties exists in the CloudFormation template.

        By default, performs partial matching on the ``Properties`` key of the resource, via the
        ``Match.objectLike()``. To configure different behavour, use other matchers in the ``Match`` class.

        :param type: the resource type; ex: ``AWS::S3::Bucket``
        :param props: the 'Properties' section of the resource as should be expected in the template.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "hasResourceProperties", [type, props]))

    @jsii.member(jsii_name="resourceCountIs")
    def resource_count_is(self, type: builtins.str, count: jsii.Number) -> None:
        '''(experimental) Assert that the given number of resources of the given type exist in the template.

        :param type: the resource type; ex: ``AWS::S3::Bucket``
        :param count: number of expected instances.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "resourceCountIs", [type, count]))

    @jsii.member(jsii_name="templateMatches")
    def template_matches(
        self,
        expected: typing.Mapping[builtins.str, typing.Any],
    ) -> None:
        '''(experimental) Assert that the CloudFormation template matches the given value.

        :param expected: the expected CloudFormation template as key-value pairs.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "templateMatches", [expected]))

    @jsii.member(jsii_name="toJSON")
    def to_json(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) The CloudFormation template deserialized into an object.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "toJSON", []))


__all__ = [
    "Match",
    "MatchResult",
    "Matcher",
    "Template",
]

publication.publish()
