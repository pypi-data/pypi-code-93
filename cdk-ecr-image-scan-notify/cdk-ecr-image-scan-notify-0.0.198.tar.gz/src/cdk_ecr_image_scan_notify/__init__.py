'''
[![NPM version](https://badge.fury.io/js/cdk-ecr-image-scan-notify.svg)](https://badge.fury.io/js/cdk-ecr-image-scan-notify)
[![PyPI version](https://badge.fury.io/py/cdk-ecr-image-scan-notify.svg)](https://badge.fury.io/py/cdk-ecr-image-scan-notify)
![Release](https://github.com/hayao-k/cdk-ecr-image-scan-notify/workflows/Release/badge.svg)

# cdk-ecr-image-scan-notify

cdk-ecr-image-scan-notify is an AWS CDK construct library that notify the slack channel of Amazon ECR image scan results.

![](https://github.com/hayao-k/ecr-image-scan-findings-to-slack/raw/master/docs/images/slack-notification.png)

Click on an image name to go to the scan results page.

![](https://github.com/hayao-k/ecr-image-scan-findings-to-slack/raw/master/docs/images/scan-result.png)

## Getting Started

### TypeScript

Installation

```
$ yarn add cdk-ecr-image-scan-notify
```

Usage

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
from cdk_ecr_image_scan_notify import EcrImageScanNotify

mock_app = cdk.App()
stack = cdk.Stack(mock_app, "<your-stack-name>")

EcrImageScanNotify(stack, "ecr-image-scan-notify",
    webhook_url="<your-incoming-webhook-url>",
    channel="<your-slack-channel-name>"
)
```

Deploy!

```
$ cdk deploy
```

### Python

Installation

```
$ pip install cdk-ecr-image-scan-notify
```

Usage

```py
import aws_cdk.core as cdk
from cdk_ecr_image_scan_notify import EcrImageScanNotify

app = cdk.App()
stack = cdk.Stack(app, "<your-stack-name>", env={'region': 'ap-northeast-1'})

EcrImageScanNotify(stack, "EcrImageScanNotify",
    webhook_url = '<your-incoming-webhook-url>',
    channel =  '<your-slack-channel-name>',
)
```

Deploy!

```
$ cdk deploy
```

## Overview

Amazon EventBridge (CloudWatch Events) detects the image scan execution and starts the Lambda function.
The Lambda function uses the DescribeImages API to get a summary of the scan results, formatting them and notifying Slack.

![](https://github.com/hayao-k/ecr-image-scan-findings-to-slack/raw/master/docs/images/architecture.png)
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


class EcrImageScanNotify(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-ecr-image-scan-notify.EcrImageScanNotify",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        channel: builtins.str,
        webhook_url: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param channel: 
        :param webhook_url: 

        :stability: experimental
        '''
        props = EcrImageScanNotifyProps(channel=channel, webhook_url=webhook_url)

        jsii.create(EcrImageScanNotify, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-ecr-image-scan-notify.EcrImageScanNotifyProps",
    jsii_struct_bases=[],
    name_mapping={"channel": "channel", "webhook_url": "webhookUrl"},
)
class EcrImageScanNotifyProps:
    def __init__(self, *, channel: builtins.str, webhook_url: builtins.str) -> None:
        '''
        :param channel: 
        :param webhook_url: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "channel": channel,
            "webhook_url": webhook_url,
        }

    @builtins.property
    def channel(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("channel")
        assert result is not None, "Required property 'channel' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def webhook_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("webhook_url")
        assert result is not None, "Required property 'webhook_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcrImageScanNotifyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EcrImageScanNotify",
    "EcrImageScanNotifyProps",
]

publication.publish()
