'''
# cdk-comprehend-s3olap

This construct creates the foundation for developers to explore the combination of Amazon S3 Object Lambda and Amazon Comprehend for PII scenarios and it is designed with flexibility, i.e, the developers could tweak arguments via CDK to see how AWS services work and behave.

[![License](https://img.shields.io/badge/License-Apache%202.0-green)](https://opensource.org/licenses/Apache-2.0)
[![Current cdk version](https://img.shields.io/github/package-json/dependency-version/HsiehShuJeng/cdk-comprehend-s3olap/@aws-cdk/core)](https://github.com/aws/aws-cdk)
[![Build](https://github.com/HsiehShuJeng/cdk-comprehend-s3olap/actions/workflows/build.yml/badge.svg)](https://github.com/HsiehShuJeng/cdk-comprehend-s3olap/actions/workflows/build.yml) [![Release](https://github.com/HsiehShuJeng/cdk-comprehend-s3olap/actions/workflows/release.yml/badge.svg)](https://github.com/HsiehShuJeng/cdk-comprehend-s3olap/actions/workflows/release.yml)
[![Python](https://img.shields.io/pypi/pyversions/cdk-comprehend-s3olap)](https://pypi.org) [![pip](https://img.shields.io/badge/pip%20install-cdk--comprehend--s3olap-blue)](https://pypi.org/project/cdk-comprehend-s3olap/)
[![npm version](https://img.shields.io/npm/v/cdk-comprehend-s3olap)](https://www.npmjs.com/package/cdk-comprehend-s3olap) [![pypi version](https://img.shields.io/pypi/v/cdk-comprehend-s3olap)](https://pypi.org/project/cdk-comprehend-s3olap/) [![Maven](https://img.shields.io/maven-central/v/io.github.hsiehshujeng/cdk-comprehend-s3olap)](https://search.maven.org/search?q=a:cdk-comprehend-s3olap) [![nuget](https://img.shields.io/nuget/v/Comprehend.S3olap)](https://www.nuget.org/packages/Comprehend.S3olap/)

# Table of Contents

* [Serverless Architecture](#serverless-architecture)

  * [Access Control](#access-control)
  * [Redaction](#rerfaction)
* [Introduction](#introduction)
* [Example](#example)

  * [Typescript](#typescript)
  * [Python](#python)
  * [Java](#java)
  * [C#](#c)
* [Some Notes](#some-notes)

# Serverless Architecture

## Access Control

**Data Flow**
![image](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2021/05/07/1-2891.jpg)
*Ram R. and Austin Q., 2021*
**Arhictecture**
![image](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2021/05/07/2-2891.jpg)
*Ram R. and Austin Q., 2021*

## Redaction

![image](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2021/05/07/3-2891.jpg)
*Ram R. and Austin Q., 2021*
![image](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2021/05/07/4-2891.jpg)
*Ram R. and Austin Q., 2021*

# Introduction

The architecture was introduced by **Ram Ramani** and **Austin Quam** and was posted on the AWS Blog as [*Protect PII using Amazon S3 Object Lambda to process and modify data during retrieval*](https://aws.amazon.com/tw/blogs/machine-learning/protect-pii-using-amazon-s3-object-lambda-to-process-and-modify-data-during-retrieval/).
I converted the architecture into a CDK constrcut for 4 programming languages. With this construct, you could manage the properties of IAM roles, the Lambda functions with Amazon Comprehend, and few for the constrcut.
Before deploying the construct via the CDK, you could either places the text files, i.e., those for the access control case and redaction case, under a directory with a specific name as the following or just deploying directly yet you need to upload the text files onto the S3 buckets manually yourself. It's all your choie.

```bash
# For the access control case.
$ cd ${ROOT_DIRECTORY_CDK_APPLICATION}
$ mkdir -p files/access_control
$ curl -o survey-results.txt https://raw.githubusercontent.com/aws-samples/amazon-comprehend-examples/master/s3_object_lambda_pii_protection_blog/access-control/survey-results.txt
$ curl -o innocuous.txt https://raw.githubusercontent.com/aws-samples/amazon-comprehend-examples/master/s3_object_lambda_pii_protection_blog/access-control/innocuous.txt
# For the redaction case.
$ cd ${ROOT_DIRECTORY_CDK_APPLICATION}
$ mkdir -p files/redaction
$ curl -o transcript.txt https://raw.githubusercontent.com/aws-samples/amazon-comprehend-examples/master/s3_object_lambda_pii_protection_blog/redaction/transcript.txt
```

# Example

## Typescript

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-comprehend-s3olap/tree/main/src/demo/typescript).

```bash
$ cdk --init language typescript
$ yarn add cdk-comprehend-s3olap
```

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
from cdk_comprehend_s3olap import ComprehendS3olab

class TypescriptStack(cdk.Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)
        s3olab = ComprehendS3olab(self, "PiiDemo",
            admin_redaction_lambda_config={
                "mask_character": " ",
                "unsupported_file_handling": "PASS"
            },
            billing_redaction_lambda_config={
                "mask_mode": "REPLACE_WITH_PII_ENTITY_TYPE",
                "pii_entity_types": "AGE,DRIVER_ID,IP_ADDRESS,MAC_ADDRESS,PASSPORT_NUMBER,PASSWORD,SSN"
            },
            cusrt_support_redaction_lambda_config={
                "mask_mode": "REPLACE_WITH_PII_ENTITY_TYPE",
                "pii_entity_types": " BANK_ACCOUNT_NUMBER,BANK_ROUTING,CREDIT_DEBIT_CVV,CREDIT_DEBIT_EXPIRY,CREDIT_DEBIT_NUMBER,SSN"
            }
        )

        cdk.CfnOutput(self, "OPiiAccessControlLambdaArn", value=s3olab.pii_access_conrtol_lambda_arn)
        cdk.CfnOutput(self, "OAdminLambdaArn", value=s3olab.admin_lambda_arn)
        cdk.CfnOutput(self, "OBillingLambdaArn", value=s3olab.billing_lambda_arn)
        cdk.CfnOutput(self, "OCustomerSupportLambdaArn", value=s3olab.customer_support_lambda_arn)
        cdk.CfnOutput(self, "OS3ObjectLambdaGeneralArn", value=s3olab.s3object_lambda_access_control_arn)
        cdk.CfnOutput(self, "OS3ObjectLambdaAdminArn", value=s3olab.s3object_lambda_admin_arn)
        cdk.CfnOutput(self, "OS3ObjectLambdaBillingArn", value=s3olab.s3object_lambda_billing_arn)
        cdk.CfnOutput(self, "OS3ObjectLambdaCustomerSupportArn", value=s3olab.customer_support_lambda_arn)

app = cdk.App()
TypescriptStack(app, "TypescriptStack",
    stack_name="Comprehend-S3olap"
)
```

## Python

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-databrew-cicd/tree/main/src/demo/python).

```bash
# upgrading related Python packages
$ python -m ensurepip --upgrade
$ python -m pip install --upgrade pip
$ python -m pip install --upgrade virtualenv
# initialize a CDK Python project
$ cdk init --language python
# make packages installed locally instead of globally
$ source .venv/bin/activate
$ # add "cdk-comprehend-s3olap==0.0.4" into `setup.py`
$ python -m pip install --upgrade -r requirements.txt
```

The demonstration sample code of Python can be viewed via the Python tab of this package on the [Constrcut Hub](https://constructs.dev/).

## Java

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-comprehend-s3olap/tree/main/src/demo/java).

```bash
$ cdk init --language java
$ mvn package # If you include the construct, you need to tweak the test case for Java in order to package with success via Maven.
```xml
.
.
<properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <cdk.version>1.112.0</cdk.version>
    <constrcut.verion>0.0.4</constrcut.verion>
    <junit.version>5.7.1</junit.version>
</properties>
.
.
<dependencies>
    <!-- AWS Cloud Development Kit -->
    <dependency>
        <groupId>software.amazon.awscdk</groupId>
        <artifactId>core</artifactId>
        <version>${cdk.version}</version>
    </dependency>
    <dependency>
        <groupId>io.github.hsiehshujeng</groupId>
        <artifactId>cdk-comprehend-s3olap</artifactId>
        <version>${constrcut.verion}</version>
    </dependency>
    .
    .
    .
</dependencies>
```

```java
package com.myorg;

import software.amazon.awscdk.core.CfnOutput;
import software.amazon.awscdk.core.CfnOutputProps;
import software.amazon.awscdk.core.Construct;
import software.amazon.awscdk.core.Stack;
import software.amazon.awscdk.core.StackProps;
import io.github.hsiehshujeng.cdk.comprehend.s3olap.RedactionLambdaProps;
import io.github.hsiehshujeng.cdk.comprehend.s3olap.ComprehendS3olab;
import io.github.hsiehshujeng.cdk.comprehend.s3olap.ComprehendS3olabProps;

public class JavaStack extends Stack {
    public JavaStack(final Construct scope, final String id) {
        this(scope, id, null);
    }

    public JavaStack(final Construct scope, final String id, final StackProps props) {
        super(scope, id, props);

        ComprehendS3olab s3olab = new ComprehendS3olab(this, "PiiDemo", ComprehendS3olabProps.builder()
            .adminRedactionLambdaConfig(
                RedactionLambdaProps.builder()
                    .maskCharacter(" ")
                    .unsupportedFileHandling("PASS").build())
            .billingRedactionLambdaConfig(
                RedactionLambdaProps.builder()
                    .maskMode("REPLACE_WITH_PII_ENTITY_TYPE")
                    .piiEntityTypes("AGE,DRIVER_ID,IP_ADDRESS,MAC_ADDRESS,PASSPORT_NUMBER,PASSWORD,SSN")
                    .build())
            .cusrtSupportRedactionLambdaConfig(
                RedactionLambdaProps.builder()
                .maskMode("REPLACE_WITH_PII_ENTITY_TYPE")
                .piiEntityTypes("BANK_ACCOUNT_NUMBER,BANK_ROUTING,CREDIT_DEBIT_CVV,CREDIT_DEBIT_EXPIRY,CREDIT_DEBIT_NUMBER,SSN")
                .build())
            .exampleFileDir("/opt/learning/cdk-comprehend-s3olap/src/demo/java")
            .build()
            );

          new CfnOutput(this, "OPiiAccessControlLambdaArn", CfnOutputProps.builder().value(s3olab.getPiiAccessConrtolLambdaArn()).build());
          new CfnOutput(this, "OAdminLambdaArn", CfnOutputProps.builder().value(s3olab.getAdminLambdaArn()).build());
          new CfnOutput(this, "OBillingLambdaArn", CfnOutputProps.builder().value(s3olab.getBillingLambdaArn()).build());
          new CfnOutput(this, "OCustomerSupportLambdaArn", CfnOutputProps.builder().value(s3olab.getCustomerSupportLambdaArn()).build());
          new CfnOutput(this, "OS3ObjectLambdaGeneralArn", CfnOutputProps.builder().value(s3olab.getS3objectLambdaAccessControlArn()).build());
          new CfnOutput(this, "OS3ObjectLambdaAdminArn", CfnOutputProps.builder().value(s3olab.getS3objectLambdaAdminArn()).build());
          new CfnOutput(this, "OS3ObjectLambdaBillingArn", CfnOutputProps.builder().value(s3olab.getS3objectLambdaBillingArn()).build());
          new CfnOutput(this, "OS3ObjectLambdaCustomerSupportArn", CfnOutputProps.builder().value(s3olab.getCustomerSupportLambdaArn()).build());
    }
}
```

## C#

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-comprehend-s3olap/tree/main/src/demo/csharp).

```bash
$ cdk init --language csharp
$ dotnet add src/Csharp package Comprehend.S3olap --version 0.0.8
```

```cs
using Amazon.CDK;
using ScottHsieh.Cdk;

namespace Csharp
{
    public class CsharpStack : Stack
    {
        internal CsharpStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            var S3olab = new ComprehendS3olab(this, "PiiDemo", new ComprehendS3olabProps
            {
                AdminRedactionLambdaConfig = new RedactionLambdaProps
                {
                    MaskCharacter = " ",
                    UnsupportedFileHandling = "PASS"
                },
                BillingRedactionLambdaConfig = new RedactionLambdaProps
                {
                    MaskMode = "REPLACE_WITH_PII_ENTITY_TYPE",
                    PiiEntityTypes = "AGE,DRIVER_ID,IP_ADDRESS,MAC_ADDRESS,PASSPORT_NUMBER,PASSWORD,SSN"
                },
                CusrtSupportRedactionLambdaConfig = new RedactionLambdaProps
                {
                    MaskMode = "REPLACE_WITH_PII_ENTITY_TYPE",
                    PiiEntityTypes = "BANK_ACCOUNT_NUMBER,BANK_ROUTING,CREDIT_DEBIT_CVV,CREDIT_DEBIT_EXPIRY,CREDIT_DEBIT_NUMBER,SSN"
                },
                ExampleFileDir = "/opt/learning/cdk-comprehend-s3olap/src/demo/csharp"
            });

            new CfnOutput(this, "OPiiAccessControlLambdaArn", new CfnOutputProps { Value = S3olab.PiiAccessConrtolLambdaArn });
            new CfnOutput(this, "OAdminLambdaArn", new CfnOutputProps { Value = S3olab.AdminLambdaArn });
            new CfnOutput(this, "OBillingLambdaArn", new CfnOutputProps { Value = S3olab.BillingLambdaArn });
            new CfnOutput(this, "OCustomerSupportLambdaArn", new CfnOutputProps { Value = S3olab.CustomerSupportLambdaArn });
            new CfnOutput(this, "OS3ObjectLambdaGeneralArn", new CfnOutputProps { Value = S3olab.S3objectLambdaAccessControlArn });
            new CfnOutput(this, "OS3ObjectLambdaAdminArn", new CfnOutputProps { Value = S3olab.S3objectLambdaAdminArn });
            new CfnOutput(this, "OS3ObjectLambdaBillingArn", new CfnOutputProps { Value = S3olab.S3objectLambdaBillingArn });
            new CfnOutput(this, "OS3ObjectLambdaCustomerSupportArn", new CfnOutputProps { Value = S3olab.CustomerSupportLambdaArn });
        }
    }
}
```

# Some Notes

1. You should see similar items as the following diagram displays after deploying the constrcut.
   ![image](https://raw.githubusercontent.com/HsiehShuJeng/cdk-comprehend-s3olap/main/images/s3olap_console.png)
2. After creating the foundation with success, you could switch roles that the consrtcut creates for you and see how **Amazon S3 Object Lambda** works. For what switching roles is, please refer to [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-console.html) for the detail.
   ![image](https://raw.githubusercontent.com/HsiehShuJeng/cdk-comprehend-s3olap/main/images/switch_roles.png)
3. You explore **Amazon S3 Object Lambda** through the Object Lambda access points on the AWS Console and open or download the text files via one of the IAM roles.
4. Lambda code that incorporates with **Amazon Comprehend** could be see [here](https://github.com/aws-samples/amazon-comprehend-examples/tree/master/s3_object_lambda_pii_protection_blog).
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


class AccessConrtolLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-comprehend-s3olap.AccessConrtolLambda",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        confidence_threshold: typing.Optional[builtins.str] = None,
        contains_pii_entities_thread_count: typing.Optional[builtins.str] = None,
        default_language_code: typing.Optional[builtins.str] = None,
        document_max_size: typing.Optional[builtins.str] = None,
        document_max_size_contains_pii_entities: typing.Optional[builtins.str] = None,
        is_partial_object_supported: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        max_chars_overlap: typing.Optional[builtins.str] = None,
        pii_entity_types: typing.Optional[builtins.str] = None,
        publish_cloud_watch_metrics: typing.Optional[builtins.str] = None,
        semantic_version: typing.Optional[builtins.str] = None,
        subsegment_overlapping_tokens: typing.Optional[builtins.str] = None,
        unsupported_file_handling: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param confidence_threshold: The minimum prediction confidence score above which PII classification and detection would be considered as final answer. Valid range (0.5 to 1.0). Default: '0.5'
        :param contains_pii_entities_thread_count: Number of threads to use for calling Comprehend's ContainsPiiEntities API. This controls the number of simultaneous calls that will be made from this Lambda. Default: '20'
        :param default_language_code: Default language of the text to be processed. This code will be used for interacting with Comprehend. Default: 'en'
        :param document_max_size: Default maximum document size (in bytes) that this function can process otherwise will throw exception for too large document size. Default: '102400'
        :param document_max_size_contains_pii_entities: Maximum document size (in bytes) to be used for making calls to Comprehend's ContainsPiiEntities API. Default: '50000'
        :param is_partial_object_supported: Whether to support partial objects or not. Accessing partial object through http headers such byte-range can corrupt the object and/or affect PII detection accuracy. Default: 'false'
        :param log_level: Log level for Lambda function logging, e.g., ERROR, INFO, DEBUG, etc. Default: 'INFO'
        :param max_chars_overlap: Maximum characters to overlap among segments of a document in case chunking is needed because of maximum document size limit. Default: '200'
        :param pii_entity_types: List of comma separated PII entity types to be considered for access control. Refer Comprehend's documentation page for list of supported PII entity types. Default: 'ALL'
        :param publish_cloud_watch_metrics: True if publish metrics to Cloudwatch, false otherwise. See README.md for details on CloudWatch metrics. Default: 'true'
        :param semantic_version: The version of the serverless application. Default: '1.0.2'
        :param subsegment_overlapping_tokens: Number of tokens/words to overlap among segments of a document in case chunking is needed because of maximum document size limit. Default: '20'
        :param unsupported_file_handling: Handling logic for Unsupported files. Valid values are PASS and FAIL. Default: 'FAIL'
        '''
        props = AccessConrtolLambdaProps(
            confidence_threshold=confidence_threshold,
            contains_pii_entities_thread_count=contains_pii_entities_thread_count,
            default_language_code=default_language_code,
            document_max_size=document_max_size,
            document_max_size_contains_pii_entities=document_max_size_contains_pii_entities,
            is_partial_object_supported=is_partial_object_supported,
            log_level=log_level,
            max_chars_overlap=max_chars_overlap,
            pii_entity_types=pii_entity_types,
            publish_cloud_watch_metrics=publish_cloud_watch_metrics,
            semantic_version=semantic_version,
            subsegment_overlapping_tokens=subsegment_overlapping_tokens,
            unsupported_file_handling=unsupported_file_handling,
        )

        jsii.create(AccessConrtolLambda, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackName")
    def stack_name(self) -> builtins.str:
        '''The name of the underlying resoure in the serverless application.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "stackName"))


@jsii.data_type(
    jsii_type="cdk-comprehend-s3olap.AccessConrtolLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "confidence_threshold": "confidenceThreshold",
        "contains_pii_entities_thread_count": "containsPiiEntitiesThreadCount",
        "default_language_code": "defaultLanguageCode",
        "document_max_size": "documentMaxSize",
        "document_max_size_contains_pii_entities": "documentMaxSizeContainsPiiEntities",
        "is_partial_object_supported": "isPartialObjectSupported",
        "log_level": "logLevel",
        "max_chars_overlap": "maxCharsOverlap",
        "pii_entity_types": "piiEntityTypes",
        "publish_cloud_watch_metrics": "publishCloudWatchMetrics",
        "semantic_version": "semanticVersion",
        "subsegment_overlapping_tokens": "subsegmentOverlappingTokens",
        "unsupported_file_handling": "unsupportedFileHandling",
    },
)
class AccessConrtolLambdaProps:
    def __init__(
        self,
        *,
        confidence_threshold: typing.Optional[builtins.str] = None,
        contains_pii_entities_thread_count: typing.Optional[builtins.str] = None,
        default_language_code: typing.Optional[builtins.str] = None,
        document_max_size: typing.Optional[builtins.str] = None,
        document_max_size_contains_pii_entities: typing.Optional[builtins.str] = None,
        is_partial_object_supported: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        max_chars_overlap: typing.Optional[builtins.str] = None,
        pii_entity_types: typing.Optional[builtins.str] = None,
        publish_cloud_watch_metrics: typing.Optional[builtins.str] = None,
        semantic_version: typing.Optional[builtins.str] = None,
        subsegment_overlapping_tokens: typing.Optional[builtins.str] = None,
        unsupported_file_handling: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param confidence_threshold: The minimum prediction confidence score above which PII classification and detection would be considered as final answer. Valid range (0.5 to 1.0). Default: '0.5'
        :param contains_pii_entities_thread_count: Number of threads to use for calling Comprehend's ContainsPiiEntities API. This controls the number of simultaneous calls that will be made from this Lambda. Default: '20'
        :param default_language_code: Default language of the text to be processed. This code will be used for interacting with Comprehend. Default: 'en'
        :param document_max_size: Default maximum document size (in bytes) that this function can process otherwise will throw exception for too large document size. Default: '102400'
        :param document_max_size_contains_pii_entities: Maximum document size (in bytes) to be used for making calls to Comprehend's ContainsPiiEntities API. Default: '50000'
        :param is_partial_object_supported: Whether to support partial objects or not. Accessing partial object through http headers such byte-range can corrupt the object and/or affect PII detection accuracy. Default: 'false'
        :param log_level: Log level for Lambda function logging, e.g., ERROR, INFO, DEBUG, etc. Default: 'INFO'
        :param max_chars_overlap: Maximum characters to overlap among segments of a document in case chunking is needed because of maximum document size limit. Default: '200'
        :param pii_entity_types: List of comma separated PII entity types to be considered for access control. Refer Comprehend's documentation page for list of supported PII entity types. Default: 'ALL'
        :param publish_cloud_watch_metrics: True if publish metrics to Cloudwatch, false otherwise. See README.md for details on CloudWatch metrics. Default: 'true'
        :param semantic_version: The version of the serverless application. Default: '1.0.2'
        :param subsegment_overlapping_tokens: Number of tokens/words to overlap among segments of a document in case chunking is needed because of maximum document size limit. Default: '20'
        :param unsupported_file_handling: Handling logic for Unsupported files. Valid values are PASS and FAIL. Default: 'FAIL'
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if confidence_threshold is not None:
            self._values["confidence_threshold"] = confidence_threshold
        if contains_pii_entities_thread_count is not None:
            self._values["contains_pii_entities_thread_count"] = contains_pii_entities_thread_count
        if default_language_code is not None:
            self._values["default_language_code"] = default_language_code
        if document_max_size is not None:
            self._values["document_max_size"] = document_max_size
        if document_max_size_contains_pii_entities is not None:
            self._values["document_max_size_contains_pii_entities"] = document_max_size_contains_pii_entities
        if is_partial_object_supported is not None:
            self._values["is_partial_object_supported"] = is_partial_object_supported
        if log_level is not None:
            self._values["log_level"] = log_level
        if max_chars_overlap is not None:
            self._values["max_chars_overlap"] = max_chars_overlap
        if pii_entity_types is not None:
            self._values["pii_entity_types"] = pii_entity_types
        if publish_cloud_watch_metrics is not None:
            self._values["publish_cloud_watch_metrics"] = publish_cloud_watch_metrics
        if semantic_version is not None:
            self._values["semantic_version"] = semantic_version
        if subsegment_overlapping_tokens is not None:
            self._values["subsegment_overlapping_tokens"] = subsegment_overlapping_tokens
        if unsupported_file_handling is not None:
            self._values["unsupported_file_handling"] = unsupported_file_handling

    @builtins.property
    def confidence_threshold(self) -> typing.Optional[builtins.str]:
        '''The minimum prediction confidence score above which PII classification and detection would be considered as final answer.

        Valid range (0.5 to 1.0).

        :default: '0.5'
        '''
        result = self._values.get("confidence_threshold")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contains_pii_entities_thread_count(self) -> typing.Optional[builtins.str]:
        '''Number of threads to use for calling Comprehend's ContainsPiiEntities API.

        This controls the number of simultaneous calls that will be made from this Lambda.

        :default: '20'
        '''
        result = self._values.get("contains_pii_entities_thread_count")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_language_code(self) -> typing.Optional[builtins.str]:
        '''Default language of the text to be processed.

        This code will be used for interacting with Comprehend.

        :default: 'en'
        '''
        result = self._values.get("default_language_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_max_size(self) -> typing.Optional[builtins.str]:
        '''Default maximum document size (in bytes) that this function can process otherwise will throw exception for too large document size.

        :default: '102400'
        '''
        result = self._values.get("document_max_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_max_size_contains_pii_entities(self) -> typing.Optional[builtins.str]:
        '''Maximum document size (in bytes) to be used for making calls to Comprehend's ContainsPiiEntities API.

        :default: '50000'
        '''
        result = self._values.get("document_max_size_contains_pii_entities")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_partial_object_supported(self) -> typing.Optional[builtins.str]:
        '''Whether to support partial objects or not.

        Accessing partial object through http headers such byte-range can corrupt the object and/or affect PII detection accuracy.

        :default: 'false'
        '''
        result = self._values.get("is_partial_object_supported")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        '''Log level for Lambda function logging, e.g., ERROR, INFO, DEBUG, etc.

        :default: 'INFO'
        '''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_chars_overlap(self) -> typing.Optional[builtins.str]:
        '''Maximum characters to overlap among segments of a document in case chunking is needed because of maximum document size limit.

        :default: '200'
        '''
        result = self._values.get("max_chars_overlap")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pii_entity_types(self) -> typing.Optional[builtins.str]:
        '''List of comma separated PII entity types to be considered for access control.

        Refer Comprehend's documentation page for list of supported PII entity types.

        :default: 'ALL'
        '''
        result = self._values.get("pii_entity_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_cloud_watch_metrics(self) -> typing.Optional[builtins.str]:
        '''True if publish metrics to Cloudwatch, false otherwise.

        See README.md for details on CloudWatch metrics.

        :default: 'true'
        '''
        result = self._values.get("publish_cloud_watch_metrics")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def semantic_version(self) -> typing.Optional[builtins.str]:
        '''The version of the serverless application.

        :default: '1.0.2'
        '''
        result = self._values.get("semantic_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subsegment_overlapping_tokens(self) -> typing.Optional[builtins.str]:
        '''Number of tokens/words to overlap among segments of a document in case chunking is needed because of maximum document size limit.

        :default: '20'
        '''
        result = self._values.get("subsegment_overlapping_tokens")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unsupported_file_handling(self) -> typing.Optional[builtins.str]:
        '''Handling logic for Unsupported files.

        Valid values are PASS and FAIL.

        :default: 'FAIL'
        '''
        result = self._values.get("unsupported_file_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessConrtolLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AdminRole(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-comprehend-s3olap.AdminRole",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        iam_role_name: typing.Optional[builtins.str] = None,
        object_lambda_access_point_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param iam_role_name: The name of the IAM role. Default: 'RedactionAdminRole'
        :param object_lambda_access_point_name: The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration. Default: 'admin-s3olap-call-transcripts-known-pii'
        :param policy_name: The name of the IAM policy for the IAM role. Default: 'admin-role-s3olap-policy'
        '''
        props = AdminRoleProps(
            iam_role_name=iam_role_name,
            object_lambda_access_point_name=object_lambda_access_point_name,
            policy_name=policy_name,
        )

        jsii.create(AdminRole, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The ARN of the IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        '''The unique string identifying the role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        '''The name of the IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleName"))


@jsii.data_type(
    jsii_type="cdk-comprehend-s3olap.AdminRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "iam_role_name": "iamRoleName",
        "object_lambda_access_point_name": "objectLambdaAccessPointName",
        "policy_name": "policyName",
    },
)
class AdminRoleProps:
    def __init__(
        self,
        *,
        iam_role_name: typing.Optional[builtins.str] = None,
        object_lambda_access_point_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param iam_role_name: The name of the IAM role. Default: 'RedactionAdminRole'
        :param object_lambda_access_point_name: The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration. Default: 'admin-s3olap-call-transcripts-known-pii'
        :param policy_name: The name of the IAM policy for the IAM role. Default: 'admin-role-s3olap-policy'
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if iam_role_name is not None:
            self._values["iam_role_name"] = iam_role_name
        if object_lambda_access_point_name is not None:
            self._values["object_lambda_access_point_name"] = object_lambda_access_point_name
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def iam_role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role.

        :default: 'RedactionAdminRole'
        '''
        result = self._values.get("iam_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lambda_access_point_name(self) -> typing.Optional[builtins.str]:
        '''The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration.

        :default: 'admin-s3olap-call-transcripts-known-pii'
        '''
        result = self._values.get("object_lambda_access_point_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM policy for the IAM role.

        :default: 'admin-role-s3olap-policy'
        '''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AdminRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BillingRole(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-comprehend-s3olap.BillingRole",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        iam_role_name: typing.Optional[builtins.str] = None,
        object_lambda_access_point_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param iam_role_name: The name of the IAM role. Default: 'RedactionAdminRole'
        :param object_lambda_access_point_name: The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration. Default: 'admin-s3olap-call-transcripts-known-pii'
        :param policy_name: The name of the IAM policy for the IAM role. Default: 'admin-role-s3olap-policy'
        '''
        props = AdminRoleProps(
            iam_role_name=iam_role_name,
            object_lambda_access_point_name=object_lambda_access_point_name,
            policy_name=policy_name,
        )

        jsii.create(BillingRole, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The ARN of the IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        '''The unique string identifying the role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        '''The name of the IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleName"))


@jsii.data_type(
    jsii_type="cdk-comprehend-s3olap.BillingRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "iam_role_name": "iamRoleName",
        "object_lambda_access_point_name": "objectLambdaAccessPointName",
        "policy_name": "policyName",
    },
)
class BillingRoleProps:
    def __init__(
        self,
        *,
        iam_role_name: typing.Optional[builtins.str] = None,
        object_lambda_access_point_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param iam_role_name: The name of the IAM role. Default: 'RedactionBillingRole'
        :param object_lambda_access_point_name: The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration. Default: 'billing-s3olap-call-transcripts-known-pii'
        :param policy_name: The name of the IAM policy for the IAM role. Default: 'billing-role-s3olap-policy'
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if iam_role_name is not None:
            self._values["iam_role_name"] = iam_role_name
        if object_lambda_access_point_name is not None:
            self._values["object_lambda_access_point_name"] = object_lambda_access_point_name
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def iam_role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role.

        :default: 'RedactionBillingRole'
        '''
        result = self._values.get("iam_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lambda_access_point_name(self) -> typing.Optional[builtins.str]:
        '''The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration.

        :default: 'billing-s3olap-call-transcripts-known-pii'
        '''
        result = self._values.get("object_lambda_access_point_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM policy for the IAM role.

        :default: 'billing-role-s3olap-policy'
        '''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BillingRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComprehendS3olab(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-comprehend-s3olap.ComprehendS3olab",
):
    '''Creates the foundation necessary to deploy the S3 Object Lambda Acceess Control Use Case.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        access_control_lambda_config: typing.Optional[AccessConrtolLambdaProps] = None,
        admin_redaction_lambda_config: typing.Optional["RedactionLambdaProps"] = None,
        admin_role_config: typing.Optional[AdminRoleProps] = None,
        billing_redaction_lambda_config: typing.Optional["RedactionLambdaProps"] = None,
        billing_role_config: typing.Optional[BillingRoleProps] = None,
        cusrt_support_redaction_lambda_config: typing.Optional["RedactionLambdaProps"] = None,
        cust_support_role_config: typing.Optional["CustSupportRoleProps"] = None,
        example_file_dir: typing.Optional[builtins.str] = None,
        general_role_config: typing.Optional["GeneralRoleProps"] = None,
        generate_random_characters: typing.Optional[builtins.bool] = None,
        s3_access_point_names: typing.Optional["S3AccessPointNames"] = None,
        survey_bucket_prefix: typing.Optional[builtins.str] = None,
        transcripts_bucket_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param access_control_lambda_config: The parameters needed for the ``ComprehendPiiAccessControlS3ObjectLambda`` function.
        :param admin_redaction_lambda_config: The parameters of the ``ComprehendPiiRedactionS3ObjectLambda`` function for the ``AdminRole``.
        :param admin_role_config: The manageable properties for the administrator IAM role in the redaction case.
        :param billing_redaction_lambda_config: The parameters of the ``ComprehendPiiRedactionS3ObjectLambda`` function for the ``BillingRole``.
        :param billing_role_config: The manageable properties for the billing IAM role in the redaction case.
        :param cusrt_support_redaction_lambda_config: The parameters of the ``ComprehendPiiRedactionS3ObjectLambda`` function for the ``CustSupportRole``.
        :param cust_support_role_config: The manageable properties for the customer support IAM role in the redaction case.
        :param example_file_dir: The directory path where ``files/access_control/*.txt`` and ``files/redaction/*.txt`` will be put. DO NOT INCLUDE ``/`` in the end. Default: __dirname
        :param general_role_config: The manageable properties for the IAM role used to access the ``survey-results.txt`` data.
        :param generate_random_characters: For distinguish test and normal deployment. Default: true
        :param s3_access_point_names: The names of the S3 access points for the access control case and redaction case.
        :param survey_bucket_prefix: The prefix attached to the name of the S3 bucket where you are going to explore the S3 Object Lambda pertaining to the access control case. Default: 6 random words
        :param transcripts_bucket_prefix: The prefix attached to the name of the S3 bucket where you are going to explore the S3 Object Lambda pertaining to the redaction case. Default: 6 random words
        '''
        props = ComprehendS3olabProps(
            access_control_lambda_config=access_control_lambda_config,
            admin_redaction_lambda_config=admin_redaction_lambda_config,
            admin_role_config=admin_role_config,
            billing_redaction_lambda_config=billing_redaction_lambda_config,
            billing_role_config=billing_role_config,
            cusrt_support_redaction_lambda_config=cusrt_support_redaction_lambda_config,
            cust_support_role_config=cust_support_role_config,
            example_file_dir=example_file_dir,
            general_role_config=general_role_config,
            generate_random_characters=generate_random_characters,
            s3_access_point_names=s3_access_point_names,
            survey_bucket_prefix=survey_bucket_prefix,
            transcripts_bucket_prefix=transcripts_bucket_prefix,
        )

        jsii.create(ComprehendS3olab, self, [scope, id, props])

    @jsii.member(jsii_name="generateS3Prefix")
    def generate_s3_prefix(self, length: jsii.Number) -> builtins.str:
        '''
        :param length: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "generateS3Prefix", [length]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminLambdaArn")
    def admin_lambda_arn(self) -> builtins.str:
        '''The ARN of the Lambda function combined with Amazon Comprehend for thie administrator role in the redaction case.'''
        return typing.cast(builtins.str, jsii.get(self, "adminLambdaArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="billingLambdaArn")
    def billing_lambda_arn(self) -> builtins.str:
        '''The ARN of the Lambda function combined with Amazon Comprehend for thie billing role in the redaction case.'''
        return typing.cast(builtins.str, jsii.get(self, "billingLambdaArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerSupportLambdaArn")
    def customer_support_lambda_arn(self) -> builtins.str:
        '''The ARN of the Lambda function combined with Amazon Comprehend for thie customer support role in the redaction case.'''
        return typing.cast(builtins.str, jsii.get(self, "customerSupportLambdaArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="piiAccessConrtolLambdaArn")
    def pii_access_conrtol_lambda_arn(self) -> builtins.str:
        '''The ARN of the Lambda function combined with Amazon Comprehend for the general case.'''
        return typing.cast(builtins.str, jsii.get(self, "piiAccessConrtolLambdaArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3objectLambdaAccessControlArn")
    def s3object_lambda_access_control_arn(self) -> builtins.str:
        '''The ARN of the S3 Object Lambda for access control.'''
        return typing.cast(builtins.str, jsii.get(self, "s3objectLambdaAccessControlArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3objectLambdaAdminArn")
    def s3object_lambda_admin_arn(self) -> builtins.str:
        '''The ARN of the S3 Object Lambda for the admin role in the redaction case.'''
        return typing.cast(builtins.str, jsii.get(self, "s3objectLambdaAdminArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3objectLambdaBillingArn")
    def s3object_lambda_billing_arn(self) -> builtins.str:
        '''The ARN of the S3 Object Lambda for the billing role in the redaction case.'''
        return typing.cast(builtins.str, jsii.get(self, "s3objectLambdaBillingArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3objectLambdaCustomerSupportArn")
    def s3object_lambda_customer_support_arn(self) -> builtins.str:
        '''The ARN of the S3 Object Lambda for the customer support role in the redaction case.'''
        return typing.cast(builtins.str, jsii.get(self, "s3objectLambdaCustomerSupportArn"))


@jsii.data_type(
    jsii_type="cdk-comprehend-s3olap.ComprehendS3olabProps",
    jsii_struct_bases=[],
    name_mapping={
        "access_control_lambda_config": "accessControlLambdaConfig",
        "admin_redaction_lambda_config": "adminRedactionLambdaConfig",
        "admin_role_config": "adminRoleConfig",
        "billing_redaction_lambda_config": "billingRedactionLambdaConfig",
        "billing_role_config": "billingRoleConfig",
        "cusrt_support_redaction_lambda_config": "cusrtSupportRedactionLambdaConfig",
        "cust_support_role_config": "custSupportRoleConfig",
        "example_file_dir": "exampleFileDir",
        "general_role_config": "generalRoleConfig",
        "generate_random_characters": "generateRandomCharacters",
        "s3_access_point_names": "s3AccessPointNames",
        "survey_bucket_prefix": "surveyBucketPrefix",
        "transcripts_bucket_prefix": "transcriptsBucketPrefix",
    },
)
class ComprehendS3olabProps:
    def __init__(
        self,
        *,
        access_control_lambda_config: typing.Optional[AccessConrtolLambdaProps] = None,
        admin_redaction_lambda_config: typing.Optional["RedactionLambdaProps"] = None,
        admin_role_config: typing.Optional[AdminRoleProps] = None,
        billing_redaction_lambda_config: typing.Optional["RedactionLambdaProps"] = None,
        billing_role_config: typing.Optional[BillingRoleProps] = None,
        cusrt_support_redaction_lambda_config: typing.Optional["RedactionLambdaProps"] = None,
        cust_support_role_config: typing.Optional["CustSupportRoleProps"] = None,
        example_file_dir: typing.Optional[builtins.str] = None,
        general_role_config: typing.Optional["GeneralRoleProps"] = None,
        generate_random_characters: typing.Optional[builtins.bool] = None,
        s3_access_point_names: typing.Optional["S3AccessPointNames"] = None,
        survey_bucket_prefix: typing.Optional[builtins.str] = None,
        transcripts_bucket_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_control_lambda_config: The parameters needed for the ``ComprehendPiiAccessControlS3ObjectLambda`` function.
        :param admin_redaction_lambda_config: The parameters of the ``ComprehendPiiRedactionS3ObjectLambda`` function for the ``AdminRole``.
        :param admin_role_config: The manageable properties for the administrator IAM role in the redaction case.
        :param billing_redaction_lambda_config: The parameters of the ``ComprehendPiiRedactionS3ObjectLambda`` function for the ``BillingRole``.
        :param billing_role_config: The manageable properties for the billing IAM role in the redaction case.
        :param cusrt_support_redaction_lambda_config: The parameters of the ``ComprehendPiiRedactionS3ObjectLambda`` function for the ``CustSupportRole``.
        :param cust_support_role_config: The manageable properties for the customer support IAM role in the redaction case.
        :param example_file_dir: The directory path where ``files/access_control/*.txt`` and ``files/redaction/*.txt`` will be put. DO NOT INCLUDE ``/`` in the end. Default: __dirname
        :param general_role_config: The manageable properties for the IAM role used to access the ``survey-results.txt`` data.
        :param generate_random_characters: For distinguish test and normal deployment. Default: true
        :param s3_access_point_names: The names of the S3 access points for the access control case and redaction case.
        :param survey_bucket_prefix: The prefix attached to the name of the S3 bucket where you are going to explore the S3 Object Lambda pertaining to the access control case. Default: 6 random words
        :param transcripts_bucket_prefix: The prefix attached to the name of the S3 bucket where you are going to explore the S3 Object Lambda pertaining to the redaction case. Default: 6 random words
        '''
        if isinstance(access_control_lambda_config, dict):
            access_control_lambda_config = AccessConrtolLambdaProps(**access_control_lambda_config)
        if isinstance(admin_redaction_lambda_config, dict):
            admin_redaction_lambda_config = RedactionLambdaProps(**admin_redaction_lambda_config)
        if isinstance(admin_role_config, dict):
            admin_role_config = AdminRoleProps(**admin_role_config)
        if isinstance(billing_redaction_lambda_config, dict):
            billing_redaction_lambda_config = RedactionLambdaProps(**billing_redaction_lambda_config)
        if isinstance(billing_role_config, dict):
            billing_role_config = BillingRoleProps(**billing_role_config)
        if isinstance(cusrt_support_redaction_lambda_config, dict):
            cusrt_support_redaction_lambda_config = RedactionLambdaProps(**cusrt_support_redaction_lambda_config)
        if isinstance(cust_support_role_config, dict):
            cust_support_role_config = CustSupportRoleProps(**cust_support_role_config)
        if isinstance(general_role_config, dict):
            general_role_config = GeneralRoleProps(**general_role_config)
        if isinstance(s3_access_point_names, dict):
            s3_access_point_names = S3AccessPointNames(**s3_access_point_names)
        self._values: typing.Dict[str, typing.Any] = {}
        if access_control_lambda_config is not None:
            self._values["access_control_lambda_config"] = access_control_lambda_config
        if admin_redaction_lambda_config is not None:
            self._values["admin_redaction_lambda_config"] = admin_redaction_lambda_config
        if admin_role_config is not None:
            self._values["admin_role_config"] = admin_role_config
        if billing_redaction_lambda_config is not None:
            self._values["billing_redaction_lambda_config"] = billing_redaction_lambda_config
        if billing_role_config is not None:
            self._values["billing_role_config"] = billing_role_config
        if cusrt_support_redaction_lambda_config is not None:
            self._values["cusrt_support_redaction_lambda_config"] = cusrt_support_redaction_lambda_config
        if cust_support_role_config is not None:
            self._values["cust_support_role_config"] = cust_support_role_config
        if example_file_dir is not None:
            self._values["example_file_dir"] = example_file_dir
        if general_role_config is not None:
            self._values["general_role_config"] = general_role_config
        if generate_random_characters is not None:
            self._values["generate_random_characters"] = generate_random_characters
        if s3_access_point_names is not None:
            self._values["s3_access_point_names"] = s3_access_point_names
        if survey_bucket_prefix is not None:
            self._values["survey_bucket_prefix"] = survey_bucket_prefix
        if transcripts_bucket_prefix is not None:
            self._values["transcripts_bucket_prefix"] = transcripts_bucket_prefix

    @builtins.property
    def access_control_lambda_config(self) -> typing.Optional[AccessConrtolLambdaProps]:
        '''The parameters needed for the ``ComprehendPiiAccessControlS3ObjectLambda`` function.'''
        result = self._values.get("access_control_lambda_config")
        return typing.cast(typing.Optional[AccessConrtolLambdaProps], result)

    @builtins.property
    def admin_redaction_lambda_config(self) -> typing.Optional["RedactionLambdaProps"]:
        '''The parameters of the ``ComprehendPiiRedactionS3ObjectLambda`` function for the ``AdminRole``.'''
        result = self._values.get("admin_redaction_lambda_config")
        return typing.cast(typing.Optional["RedactionLambdaProps"], result)

    @builtins.property
    def admin_role_config(self) -> typing.Optional[AdminRoleProps]:
        '''The manageable properties for the administrator IAM role in the redaction case.'''
        result = self._values.get("admin_role_config")
        return typing.cast(typing.Optional[AdminRoleProps], result)

    @builtins.property
    def billing_redaction_lambda_config(
        self,
    ) -> typing.Optional["RedactionLambdaProps"]:
        '''The parameters of the ``ComprehendPiiRedactionS3ObjectLambda`` function for the ``BillingRole``.'''
        result = self._values.get("billing_redaction_lambda_config")
        return typing.cast(typing.Optional["RedactionLambdaProps"], result)

    @builtins.property
    def billing_role_config(self) -> typing.Optional[BillingRoleProps]:
        '''The manageable properties for the billing IAM role in the redaction case.'''
        result = self._values.get("billing_role_config")
        return typing.cast(typing.Optional[BillingRoleProps], result)

    @builtins.property
    def cusrt_support_redaction_lambda_config(
        self,
    ) -> typing.Optional["RedactionLambdaProps"]:
        '''The parameters of the ``ComprehendPiiRedactionS3ObjectLambda`` function for the ``CustSupportRole``.'''
        result = self._values.get("cusrt_support_redaction_lambda_config")
        return typing.cast(typing.Optional["RedactionLambdaProps"], result)

    @builtins.property
    def cust_support_role_config(self) -> typing.Optional["CustSupportRoleProps"]:
        '''The manageable properties for the customer support IAM role in the redaction case.'''
        result = self._values.get("cust_support_role_config")
        return typing.cast(typing.Optional["CustSupportRoleProps"], result)

    @builtins.property
    def example_file_dir(self) -> typing.Optional[builtins.str]:
        '''The directory path where ``files/access_control/*.txt`` and ``files/redaction/*.txt`` will be put.

        DO NOT INCLUDE ``/`` in the end.

        :default: __dirname
        '''
        result = self._values.get("example_file_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def general_role_config(self) -> typing.Optional["GeneralRoleProps"]:
        '''The manageable properties for the IAM role used to access the ``survey-results.txt`` data.'''
        result = self._values.get("general_role_config")
        return typing.cast(typing.Optional["GeneralRoleProps"], result)

    @builtins.property
    def generate_random_characters(self) -> typing.Optional[builtins.bool]:
        '''For distinguish test and normal deployment.

        :default: true
        '''
        result = self._values.get("generate_random_characters")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def s3_access_point_names(self) -> typing.Optional["S3AccessPointNames"]:
        '''The names of the S3 access points for the access control case and redaction case.'''
        result = self._values.get("s3_access_point_names")
        return typing.cast(typing.Optional["S3AccessPointNames"], result)

    @builtins.property
    def survey_bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix attached to the name of the S3 bucket where you are going to explore the S3 Object Lambda pertaining to the access control case.

        :default: 6 random words
        '''
        result = self._values.get("survey_bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transcripts_bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix attached to the name of the S3 bucket where you are going to explore the S3 Object Lambda pertaining to the redaction case.

        :default: 6 random words
        '''
        result = self._values.get("transcripts_bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComprehendS3olabProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustSupportRole(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-comprehend-s3olap.CustSupportRole",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        iam_role_name: typing.Optional[builtins.str] = None,
        object_lambda_access_point_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param iam_role_name: The name of the IAM role. Default: 'RedactionAdminRole'
        :param object_lambda_access_point_name: The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration. Default: 'admin-s3olap-call-transcripts-known-pii'
        :param policy_name: The name of the IAM policy for the IAM role. Default: 'admin-role-s3olap-policy'
        '''
        props = AdminRoleProps(
            iam_role_name=iam_role_name,
            object_lambda_access_point_name=object_lambda_access_point_name,
            policy_name=policy_name,
        )

        jsii.create(CustSupportRole, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The ARN of the IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        '''The unique string identifying the role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        '''The name of the IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleName"))


@jsii.data_type(
    jsii_type="cdk-comprehend-s3olap.CustSupportRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "iam_role_name": "iamRoleName",
        "object_lambda_access_point_name": "objectLambdaAccessPointName",
        "policy_name": "policyName",
    },
)
class CustSupportRoleProps:
    def __init__(
        self,
        *,
        iam_role_name: typing.Optional[builtins.str] = None,
        object_lambda_access_point_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param iam_role_name: The name of the IAM role. Default: 'RedactionCustSupportRole'
        :param object_lambda_access_point_name: The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration. Default: 'custsupport-s3olap-call-transcripts-known-pii'
        :param policy_name: The name of the IAM policy for the IAM role. Default: 'customersupport-role-s3olap-policy'
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if iam_role_name is not None:
            self._values["iam_role_name"] = iam_role_name
        if object_lambda_access_point_name is not None:
            self._values["object_lambda_access_point_name"] = object_lambda_access_point_name
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def iam_role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role.

        :default: 'RedactionCustSupportRole'
        '''
        result = self._values.get("iam_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lambda_access_point_name(self) -> typing.Optional[builtins.str]:
        '''The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration.

        :default: 'custsupport-s3olap-call-transcripts-known-pii'
        '''
        result = self._values.get("object_lambda_access_point_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM policy for the IAM role.

        :default: 'customersupport-role-s3olap-policy'
        '''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustSupportRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GeneralRole(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-comprehend-s3olap.GeneralRole",
):
    '''The role that you are going to assume (switch role).

    Explores how the S3 Object Lambda works.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        iam_role_name: typing.Optional[builtins.str] = None,
        object_lambda_access_point_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param iam_role_name: The name of the IAM role. Default: 'GeneralRole'
        :param object_lambda_access_point_name: The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration. Default: 'accessctl-s3olap-survey-results-unknown-pii'
        :param policy_name: The name of the IAM policy for the IAM role. Default: 'general-role-s3olap-policy'
        '''
        props = GeneralRoleProps(
            iam_role_name=iam_role_name,
            object_lambda_access_point_name=object_lambda_access_point_name,
            policy_name=policy_name,
        )

        jsii.create(GeneralRole, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The ARN of the IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        '''The unique string identifying the role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        '''The name of the IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleName"))


@jsii.data_type(
    jsii_type="cdk-comprehend-s3olap.GeneralRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "iam_role_name": "iamRoleName",
        "object_lambda_access_point_name": "objectLambdaAccessPointName",
        "policy_name": "policyName",
    },
)
class GeneralRoleProps:
    def __init__(
        self,
        *,
        iam_role_name: typing.Optional[builtins.str] = None,
        object_lambda_access_point_name: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param iam_role_name: The name of the IAM role. Default: 'GeneralRole'
        :param object_lambda_access_point_name: The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration. Default: 'accessctl-s3olap-survey-results-unknown-pii'
        :param policy_name: The name of the IAM policy for the IAM role. Default: 'general-role-s3olap-policy'
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if iam_role_name is not None:
            self._values["iam_role_name"] = iam_role_name
        if object_lambda_access_point_name is not None:
            self._values["object_lambda_access_point_name"] = object_lambda_access_point_name
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def iam_role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role.

        :default: 'GeneralRole'
        '''
        result = self._values.get("iam_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lambda_access_point_name(self) -> typing.Optional[builtins.str]:
        '''The name of the object Lambda access point, which will be the same as the S3 acceess point for the S3 bucket in the demostration.

        :default: 'accessctl-s3olap-survey-results-unknown-pii'
        '''
        result = self._values.get("object_lambda_access_point_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM policy for the IAM role.

        :default: 'general-role-s3olap-policy'
        '''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GeneralRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-comprehend-s3olap.IamRoleName")
class IamRoleName(enum.Enum):
    GENERAL = "GENERAL"
    ADMIN = "ADMIN"
    BILLING = "BILLING"
    CUST_SUPPORT = "CUST_SUPPORT"


class LambdaArnCaptorCustomResource(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-comprehend-s3olap.LambdaArnCaptorCustomResource",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        partial_lambda_name: builtins.str,
        role_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param partial_lambda_name: The partial fixed name of the gemeral Lambda function created from the serverless application.
        :param role_name: the name of the corresponding IAM role.
        '''
        props = LambdaArnCaptorResourceProps(
            partial_lambda_name=partial_lambda_name, role_name=role_name
        )

        jsii.create(LambdaArnCaptorCustomResource, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArn")
    def lambda_arn(self) -> builtins.str:
        '''The ARN of the general Lambda function created from the serverless application.

        :see: https://github.com/aws/aws-cdk/issues/8760
        '''
        return typing.cast(builtins.str, jsii.get(self, "lambdaArn"))


@jsii.data_type(
    jsii_type="cdk-comprehend-s3olap.LambdaArnCaptorResourceProps",
    jsii_struct_bases=[],
    name_mapping={"partial_lambda_name": "partialLambdaName", "role_name": "roleName"},
)
class LambdaArnCaptorResourceProps:
    def __init__(
        self,
        *,
        partial_lambda_name: builtins.str,
        role_name: builtins.str,
    ) -> None:
        '''
        :param partial_lambda_name: The partial fixed name of the gemeral Lambda function created from the serverless application.
        :param role_name: the name of the corresponding IAM role.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "partial_lambda_name": partial_lambda_name,
            "role_name": role_name,
        }

    @builtins.property
    def partial_lambda_name(self) -> builtins.str:
        '''The partial fixed name of the gemeral Lambda function created from the serverless application.'''
        result = self._values.get("partial_lambda_name")
        assert result is not None, "Required property 'partial_lambda_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_name(self) -> builtins.str:
        '''the name of the corresponding IAM role.'''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaArnCaptorResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedactionLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-comprehend-s3olap.RedactionLambda",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        confidence_threshold: typing.Optional[builtins.str] = None,
        contains_pii_entities_thread_count: typing.Optional[builtins.str] = None,
        default_language_code: typing.Optional[builtins.str] = None,
        detect_pii_entities_thread_count: typing.Optional[builtins.str] = None,
        document_max_size: typing.Optional[builtins.str] = None,
        document_max_size_contains_pii_entities: typing.Optional[builtins.str] = None,
        document_max_size_detect_pii_entities: typing.Optional[builtins.str] = None,
        is_partial_object_supported: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        mask_character: typing.Optional[builtins.str] = None,
        mask_mode: typing.Optional[builtins.str] = None,
        max_chars_overlap: typing.Optional[builtins.str] = None,
        pii_entity_types: typing.Optional[builtins.str] = None,
        publish_cloud_watch_metrics: typing.Optional[builtins.str] = None,
        semantic_version: typing.Optional[builtins.str] = None,
        subsegment_overlapping_tokens: typing.Optional[builtins.str] = None,
        unsupported_file_handling: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param confidence_threshold: The minimum prediction confidence score above which PII classification and detection would be considered as final answer. Valid range (0.5 to 1.0). Default: '0.5'
        :param contains_pii_entities_thread_count: Number of threads to use for calling Comprehend's ContainsPiiEntities API. This controls the number of simultaneous calls that will be made from this Lambda. Default: '20'
        :param default_language_code: Default language of the text to be processed. This code will be used for interacting with Comprehend. Default: 'en'
        :param detect_pii_entities_thread_count: Number of threads to use for calling Comprehend's DetectPiiEntities API. This controls the number of simultaneous calls that will be made from this Lambda. Default: '8'
        :param document_max_size: Default maximum document size (in bytes) that this function can process otherwise will throw exception for too large document size. Default: '102400'
        :param document_max_size_contains_pii_entities: Maximum document size (in bytes) to be used for making calls to Comprehend's ContainsPiiEntities API. Default: '50000'
        :param document_max_size_detect_pii_entities: Maximum document size (in bytes) to be used for making calls to Comprehend's DetectPiiEntities API. Default: '5000'
        :param is_partial_object_supported: Whether to support partial objects or not. Accessing partial object through http headers such byte-range can corrupt the object and/or affect PII detection accuracy. Default: 'false'
        :param log_level: Log level for Lambda function logging, e.g., ERROR, INFO, DEBUG, etc. Default: 'INFO'
        :param mask_character: A character that replaces each character in the redacted PII entity. Default: '*'
        :param mask_mode: Specifies whether the PII entity is redacted with the mask character or the entity type. Valid values - REPLACE_WITH_PII_ENTITY_TYPE and MASK.
        :param max_chars_overlap: Maximum characters to overlap among segments of a document in case chunking is needed because of maximum document size limit. Default: '200'
        :param pii_entity_types: List of comma separated PII entity types to be considered for redaction. Refer Comprehend's documentation page for list of supported PII entity types. Default: 'ALL'
        :param publish_cloud_watch_metrics: True if publish metrics to Cloudwatch, false otherwise. See README.md for details on CloudWatch metrics. Default: 'true'
        :param semantic_version: The version of the serverless application. Default: '1.0.2'
        :param subsegment_overlapping_tokens: Number of tokens/words to overlap among segments of a document in case chunking is needed because of maximum document size limit. Default: '20'
        :param unsupported_file_handling: Handling logic for Unsupported files. Valid values are PASS and FAIL. Default: 'FAIL'
        '''
        props = RedactionLambdaProps(
            confidence_threshold=confidence_threshold,
            contains_pii_entities_thread_count=contains_pii_entities_thread_count,
            default_language_code=default_language_code,
            detect_pii_entities_thread_count=detect_pii_entities_thread_count,
            document_max_size=document_max_size,
            document_max_size_contains_pii_entities=document_max_size_contains_pii_entities,
            document_max_size_detect_pii_entities=document_max_size_detect_pii_entities,
            is_partial_object_supported=is_partial_object_supported,
            log_level=log_level,
            mask_character=mask_character,
            mask_mode=mask_mode,
            max_chars_overlap=max_chars_overlap,
            pii_entity_types=pii_entity_types,
            publish_cloud_watch_metrics=publish_cloud_watch_metrics,
            semantic_version=semantic_version,
            subsegment_overlapping_tokens=subsegment_overlapping_tokens,
            unsupported_file_handling=unsupported_file_handling,
        )

        jsii.create(RedactionLambda, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackName")
    def stack_name(self) -> builtins.str:
        '''The name of the underlying resoure in the serverless application.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "stackName"))


@jsii.data_type(
    jsii_type="cdk-comprehend-s3olap.RedactionLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "confidence_threshold": "confidenceThreshold",
        "contains_pii_entities_thread_count": "containsPiiEntitiesThreadCount",
        "default_language_code": "defaultLanguageCode",
        "detect_pii_entities_thread_count": "detectPiiEntitiesThreadCount",
        "document_max_size": "documentMaxSize",
        "document_max_size_contains_pii_entities": "documentMaxSizeContainsPiiEntities",
        "document_max_size_detect_pii_entities": "documentMaxSizeDetectPiiEntities",
        "is_partial_object_supported": "isPartialObjectSupported",
        "log_level": "logLevel",
        "mask_character": "maskCharacter",
        "mask_mode": "maskMode",
        "max_chars_overlap": "maxCharsOverlap",
        "pii_entity_types": "piiEntityTypes",
        "publish_cloud_watch_metrics": "publishCloudWatchMetrics",
        "semantic_version": "semanticVersion",
        "subsegment_overlapping_tokens": "subsegmentOverlappingTokens",
        "unsupported_file_handling": "unsupportedFileHandling",
    },
)
class RedactionLambdaProps:
    def __init__(
        self,
        *,
        confidence_threshold: typing.Optional[builtins.str] = None,
        contains_pii_entities_thread_count: typing.Optional[builtins.str] = None,
        default_language_code: typing.Optional[builtins.str] = None,
        detect_pii_entities_thread_count: typing.Optional[builtins.str] = None,
        document_max_size: typing.Optional[builtins.str] = None,
        document_max_size_contains_pii_entities: typing.Optional[builtins.str] = None,
        document_max_size_detect_pii_entities: typing.Optional[builtins.str] = None,
        is_partial_object_supported: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        mask_character: typing.Optional[builtins.str] = None,
        mask_mode: typing.Optional[builtins.str] = None,
        max_chars_overlap: typing.Optional[builtins.str] = None,
        pii_entity_types: typing.Optional[builtins.str] = None,
        publish_cloud_watch_metrics: typing.Optional[builtins.str] = None,
        semantic_version: typing.Optional[builtins.str] = None,
        subsegment_overlapping_tokens: typing.Optional[builtins.str] = None,
        unsupported_file_handling: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param confidence_threshold: The minimum prediction confidence score above which PII classification and detection would be considered as final answer. Valid range (0.5 to 1.0). Default: '0.5'
        :param contains_pii_entities_thread_count: Number of threads to use for calling Comprehend's ContainsPiiEntities API. This controls the number of simultaneous calls that will be made from this Lambda. Default: '20'
        :param default_language_code: Default language of the text to be processed. This code will be used for interacting with Comprehend. Default: 'en'
        :param detect_pii_entities_thread_count: Number of threads to use for calling Comprehend's DetectPiiEntities API. This controls the number of simultaneous calls that will be made from this Lambda. Default: '8'
        :param document_max_size: Default maximum document size (in bytes) that this function can process otherwise will throw exception for too large document size. Default: '102400'
        :param document_max_size_contains_pii_entities: Maximum document size (in bytes) to be used for making calls to Comprehend's ContainsPiiEntities API. Default: '50000'
        :param document_max_size_detect_pii_entities: Maximum document size (in bytes) to be used for making calls to Comprehend's DetectPiiEntities API. Default: '5000'
        :param is_partial_object_supported: Whether to support partial objects or not. Accessing partial object through http headers such byte-range can corrupt the object and/or affect PII detection accuracy. Default: 'false'
        :param log_level: Log level for Lambda function logging, e.g., ERROR, INFO, DEBUG, etc. Default: 'INFO'
        :param mask_character: A character that replaces each character in the redacted PII entity. Default: '*'
        :param mask_mode: Specifies whether the PII entity is redacted with the mask character or the entity type. Valid values - REPLACE_WITH_PII_ENTITY_TYPE and MASK.
        :param max_chars_overlap: Maximum characters to overlap among segments of a document in case chunking is needed because of maximum document size limit. Default: '200'
        :param pii_entity_types: List of comma separated PII entity types to be considered for redaction. Refer Comprehend's documentation page for list of supported PII entity types. Default: 'ALL'
        :param publish_cloud_watch_metrics: True if publish metrics to Cloudwatch, false otherwise. See README.md for details on CloudWatch metrics. Default: 'true'
        :param semantic_version: The version of the serverless application. Default: '1.0.2'
        :param subsegment_overlapping_tokens: Number of tokens/words to overlap among segments of a document in case chunking is needed because of maximum document size limit. Default: '20'
        :param unsupported_file_handling: Handling logic for Unsupported files. Valid values are PASS and FAIL. Default: 'FAIL'
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if confidence_threshold is not None:
            self._values["confidence_threshold"] = confidence_threshold
        if contains_pii_entities_thread_count is not None:
            self._values["contains_pii_entities_thread_count"] = contains_pii_entities_thread_count
        if default_language_code is not None:
            self._values["default_language_code"] = default_language_code
        if detect_pii_entities_thread_count is not None:
            self._values["detect_pii_entities_thread_count"] = detect_pii_entities_thread_count
        if document_max_size is not None:
            self._values["document_max_size"] = document_max_size
        if document_max_size_contains_pii_entities is not None:
            self._values["document_max_size_contains_pii_entities"] = document_max_size_contains_pii_entities
        if document_max_size_detect_pii_entities is not None:
            self._values["document_max_size_detect_pii_entities"] = document_max_size_detect_pii_entities
        if is_partial_object_supported is not None:
            self._values["is_partial_object_supported"] = is_partial_object_supported
        if log_level is not None:
            self._values["log_level"] = log_level
        if mask_character is not None:
            self._values["mask_character"] = mask_character
        if mask_mode is not None:
            self._values["mask_mode"] = mask_mode
        if max_chars_overlap is not None:
            self._values["max_chars_overlap"] = max_chars_overlap
        if pii_entity_types is not None:
            self._values["pii_entity_types"] = pii_entity_types
        if publish_cloud_watch_metrics is not None:
            self._values["publish_cloud_watch_metrics"] = publish_cloud_watch_metrics
        if semantic_version is not None:
            self._values["semantic_version"] = semantic_version
        if subsegment_overlapping_tokens is not None:
            self._values["subsegment_overlapping_tokens"] = subsegment_overlapping_tokens
        if unsupported_file_handling is not None:
            self._values["unsupported_file_handling"] = unsupported_file_handling

    @builtins.property
    def confidence_threshold(self) -> typing.Optional[builtins.str]:
        '''The minimum prediction confidence score above which PII classification and detection would be considered as final answer.

        Valid range (0.5 to 1.0).

        :default: '0.5'
        '''
        result = self._values.get("confidence_threshold")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contains_pii_entities_thread_count(self) -> typing.Optional[builtins.str]:
        '''Number of threads to use for calling Comprehend's ContainsPiiEntities API.

        This controls the number of simultaneous calls that will be made from this Lambda.

        :default: '20'
        '''
        result = self._values.get("contains_pii_entities_thread_count")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_language_code(self) -> typing.Optional[builtins.str]:
        '''Default language of the text to be processed.

        This code will be used for interacting with Comprehend.

        :default: 'en'
        '''
        result = self._values.get("default_language_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def detect_pii_entities_thread_count(self) -> typing.Optional[builtins.str]:
        '''Number of threads to use for calling Comprehend's DetectPiiEntities API.

        This controls the number of simultaneous calls that will be made from this Lambda.

        :default: '8'
        '''
        result = self._values.get("detect_pii_entities_thread_count")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_max_size(self) -> typing.Optional[builtins.str]:
        '''Default maximum document size (in bytes) that this function can process otherwise will throw exception for too large document size.

        :default: '102400'
        '''
        result = self._values.get("document_max_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_max_size_contains_pii_entities(self) -> typing.Optional[builtins.str]:
        '''Maximum document size (in bytes) to be used for making calls to Comprehend's ContainsPiiEntities API.

        :default: '50000'
        '''
        result = self._values.get("document_max_size_contains_pii_entities")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_max_size_detect_pii_entities(self) -> typing.Optional[builtins.str]:
        '''Maximum document size (in bytes) to be used for making calls to Comprehend's DetectPiiEntities API.

        :default: '5000'
        '''
        result = self._values.get("document_max_size_detect_pii_entities")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_partial_object_supported(self) -> typing.Optional[builtins.str]:
        '''Whether to support partial objects or not.

        Accessing partial object through http headers such byte-range can corrupt the object and/or affect PII detection accuracy.

        :default: 'false'
        '''
        result = self._values.get("is_partial_object_supported")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        '''Log level for Lambda function logging, e.g., ERROR, INFO, DEBUG, etc.

        :default: 'INFO'
        '''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask_character(self) -> typing.Optional[builtins.str]:
        '''A character that replaces each character in the redacted PII entity.

        :default: '*'
        '''
        result = self._values.get("mask_character")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask_mode(self) -> typing.Optional[builtins.str]:
        '''Specifies whether the PII entity is redacted with the mask character or the entity type.

        Valid values - REPLACE_WITH_PII_ENTITY_TYPE and MASK.

        :fefault: 'MASK'
        '''
        result = self._values.get("mask_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_chars_overlap(self) -> typing.Optional[builtins.str]:
        '''Maximum characters to overlap among segments of a document in case chunking is needed because of maximum document size limit.

        :default: '200'
        '''
        result = self._values.get("max_chars_overlap")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pii_entity_types(self) -> typing.Optional[builtins.str]:
        '''List of comma separated PII entity types to be considered for redaction.

        Refer Comprehend's documentation page for list of supported PII entity types.

        :default: 'ALL'
        '''
        result = self._values.get("pii_entity_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_cloud_watch_metrics(self) -> typing.Optional[builtins.str]:
        '''True if publish metrics to Cloudwatch, false otherwise.

        See README.md for details on CloudWatch metrics.

        :default: 'true'
        '''
        result = self._values.get("publish_cloud_watch_metrics")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def semantic_version(self) -> typing.Optional[builtins.str]:
        '''The version of the serverless application.

        :default: '1.0.2'
        '''
        result = self._values.get("semantic_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subsegment_overlapping_tokens(self) -> typing.Optional[builtins.str]:
        '''Number of tokens/words to overlap among segments of a document in case chunking is needed because of maximum document size limit.

        :default: '20'
        '''
        result = self._values.get("subsegment_overlapping_tokens")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unsupported_file_handling(self) -> typing.Optional[builtins.str]:
        '''Handling logic for Unsupported files.

        Valid values are PASS and FAIL.

        :default: 'FAIL'
        '''
        result = self._values.get("unsupported_file_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedactionLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-comprehend-s3olap.S3AccessPointNames",
    jsii_struct_bases=[],
    name_mapping={
        "admin": "admin",
        "billing": "billing",
        "customer_support": "customerSupport",
        "general": "general",
    },
)
class S3AccessPointNames:
    def __init__(
        self,
        *,
        admin: builtins.str,
        billing: builtins.str,
        customer_support: builtins.str,
        general: builtins.str,
    ) -> None:
        '''
        :param admin: The name of the S3 aceess point for the admin role in the redaction case. Default: 'admin-s3-access-point-call-transcripts-known-pii'
        :param billing: The name of the S3 aceess point for the billing role in the redaction case. Default: 'bill-s3-access-point-call-transcripts-known-pii'
        :param customer_support: The name of the S3 aceess point for the customer support role in the redaction case. Default: 'cs-s3-access-point-call-transcripts-known-pii'
        :param general: The name of the S3 aceess point for the general role in the access control case. Default: 'accessctl-s3-ap-survey-results-unknown-pii'
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "admin": admin,
            "billing": billing,
            "customer_support": customer_support,
            "general": general,
        }

    @builtins.property
    def admin(self) -> builtins.str:
        '''The name of the S3 aceess point for the admin role in the redaction case.

        :default: 'admin-s3-access-point-call-transcripts-known-pii'
        '''
        result = self._values.get("admin")
        assert result is not None, "Required property 'admin' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def billing(self) -> builtins.str:
        '''The name of the S3 aceess point for the billing role in the redaction case.

        :default: 'bill-s3-access-point-call-transcripts-known-pii'
        '''
        result = self._values.get("billing")
        assert result is not None, "Required property 'billing' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def customer_support(self) -> builtins.str:
        '''The name of the S3 aceess point for the customer support role in the redaction case.

        :default: 'cs-s3-access-point-call-transcripts-known-pii'
        '''
        result = self._values.get("customer_support")
        assert result is not None, "Required property 'customer_support' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def general(self) -> builtins.str:
        '''The name of the S3 aceess point for the general role in the access control case.

        :default: 'accessctl-s3-ap-survey-results-unknown-pii'
        '''
        result = self._values.get("general")
        assert result is not None, "Required property 'general' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3AccessPointNames(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccessConrtolLambda",
    "AccessConrtolLambdaProps",
    "AdminRole",
    "AdminRoleProps",
    "BillingRole",
    "BillingRoleProps",
    "ComprehendS3olab",
    "ComprehendS3olabProps",
    "CustSupportRole",
    "CustSupportRoleProps",
    "GeneralRole",
    "GeneralRoleProps",
    "IamRoleName",
    "LambdaArnCaptorCustomResource",
    "LambdaArnCaptorResourceProps",
    "RedactionLambda",
    "RedactionLambdaProps",
    "S3AccessPointNames",
]

publication.publish()
