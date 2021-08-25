'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-contentful-webhook

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-contentful-webhook)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-contentful-webhook/)

> Create, update and delete contentful webhooks with your app deployment

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-contentful-webhook
```

Python:

```bash
pip install cloudcomponents.cdk-contentful-webhook
```

## How to use

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.aws_apigateway import RestApi
from aws_cdk.core import Construct, Stack, StackProps
from cloudcomponents.cdk_contentful_webhook import ContentfulWebhook
from cloudcomponents.cdk_secret_key import SecretKey

class ContentfulWebhookStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        api = RestApi(self, "Endpoint")
        api.root.add_method("POST")

        access_token = SecretKey.from_plain_text(process.env.ACCESS_TOKEN)

        space_id = process.env.SPACE_ID

        topics = ["Entry.create"]

        ContentfulWebhook(self, "ContentfulWebhook",
            access_token=access_token,
            space_id=space_id,
            name="ExampleWebhook",
            url=api.url,
            topics=topics,
            log_level="debug"
        )
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-contentful-webhook/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-contentful-webhook/LICENSE)
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
import cloudcomponents.cdk_secret_key


class ContentfulWebhook(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-contentful-webhook.ContentfulWebhook",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        access_token: typing.Union[builtins.str, cloudcomponents.cdk_secret_key.SecretKey],
        name: builtins.str,
        space_id: builtins.str,
        topics: typing.Sequence[builtins.str],
        url: builtins.str,
        log_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param access_token: -
        :param name: -
        :param space_id: -
        :param topics: -
        :param url: -
        :param log_level: -
        '''
        props = ContentfulWebhookProps(
            access_token=access_token,
            name=name,
            space_id=space_id,
            topics=topics,
            url=url,
            log_level=log_level,
        )

        jsii.create(ContentfulWebhook, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-contentful-webhook.ContentfulWebhookProps",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "name": "name",
        "space_id": "spaceId",
        "topics": "topics",
        "url": "url",
        "log_level": "logLevel",
    },
)
class ContentfulWebhookProps:
    def __init__(
        self,
        *,
        access_token: typing.Union[builtins.str, cloudcomponents.cdk_secret_key.SecretKey],
        name: builtins.str,
        space_id: builtins.str,
        topics: typing.Sequence[builtins.str],
        url: builtins.str,
        log_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_token: -
        :param name: -
        :param space_id: -
        :param topics: -
        :param url: -
        :param log_level: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "access_token": access_token,
            "name": name,
            "space_id": space_id,
            "topics": topics,
            "url": url,
        }
        if log_level is not None:
            self._values["log_level"] = log_level

    @builtins.property
    def access_token(
        self,
    ) -> typing.Union[builtins.str, cloudcomponents.cdk_secret_key.SecretKey]:
        result = self._values.get("access_token")
        assert result is not None, "Required property 'access_token' is missing"
        return typing.cast(typing.Union[builtins.str, cloudcomponents.cdk_secret_key.SecretKey], result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def space_id(self) -> builtins.str:
        result = self._values.get("space_id")
        assert result is not None, "Required property 'space_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def topics(self) -> typing.List[builtins.str]:
        result = self._values.get("topics")
        assert result is not None, "Required property 'topics' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def url(self) -> builtins.str:
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContentfulWebhookProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ContentfulWebhook",
    "ContentfulWebhookProps",
]

publication.publish()
