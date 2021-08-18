'''
# cdk-lambda-subminute

This construct creates a state machine that can invoke a Lambda function per time unit which can be less than one minute, such as invoking every 10 seconds. You only need to craft a Lambda function and then assign it as an argument into the construct. An example is included.
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](https://opensource.org/licenses/Apache-2.0)
[![Build](https://github.com/HsiehShuJeng/cdk-lambda-subminute/actions/workflows/build.yml/badge.svg)](https://github.com/HsiehShuJeng/cdk-lambda-subminute/actions/workflows/build.yml) [![Release](https://github.com/HsiehShuJeng/cdk-lambda-subminute/workflows/Release/badge.svg)](https://github.com/HsiehShuJeng/cdk-lambda-subminute/actions/workflows/release.yml)
[![Python](https://img.shields.io/pypi/pyversions/cdk-lambda-subminute)](https://pypi.org/) [![pip](https://img.shields.io/badge/pip%20install-cdk--lambda--subminute-blue)](https://pypi.org/project/cdk-lambda-subminute/)
[![npm version](https://img.shields.io/npm/v/cdk-lambda-subminute)](https://www.npmjs.com/package/cdk-lambda-subminute) [![pypi evrsion](https://img.shields.io/pypi/v/cdk-lambda-subminute)](https://pypi.org/project/cdk-lambda-subminute/) [![Maven](https://img.shields.io/maven-central/v/io.github.hsiehshujeng/cdk-lambda-subminute)](https://search.maven.org/search?q=a:cdk-lambda-subminute) [![nuget](https://img.shields.io/nuget/v/Lambda.Subminute)](https://www.nuget.org/packages/Lambda.Subminute/)

# Serverless Architecture

<p align="center"><img src="https://raw.githubusercontent.com/HsiehShuJeng/cdk-lambda-subminute/main/images/cdk_lambda_subminute.png"/></p>

# Introduction

This construct library is reffered to thie AWS Architecture blog post, [*A serverless solution for invoking AWS Lambda at a sub-minute frequency*](https://aws.amazon.com/tw/blogs/architecture/a-serverless-solution-for-invoking-aws-lambda-at-a-sub-minute-frequency/), written by **Emanuele Menga**. I made it as a constrcut library where you only need to care about a target Lambda function, how frequent and how long you want to execute.

# Example

## Typescript

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-lambda-subminute/tree/main/src/demo/typescript).

```bash
$ cdk --init language typescript
$ yarn add cdk-lambda-subminute
```

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
class TypescriptStack(cdk.Stack):
    def __init__(self, scope, id, props=None):
        super().__init__(scope, id, props)

        target_labmda = Function(self, "targetFunction",
            code=Code.from_inline("exports.handler = function(event, ctx, cb) { return cb(null, \"hi\"); })"), # It's just a simple function for demonstration purpose only.
            function_name="testTargetFunction",
            runtime=Runtime.NODEJS_12_X,
            handler="index.handler"
        )
        cron_job_example = "cron(50/1 15-17 ? * SUN-SAT *)"
        subminute_master = LambdaSubminute(self, "LambdaSubminute", target_function=target_labmda, cronjob_expression=cron_job_example)

        cdk.CfnOutput(self, "OStateMachineArn", value=subminute_master.state_machine_arn)
        cdk.CfnOutput(self, "OIteratorFunctionArn", value=subminute_master.iterator_function.function_arn)

app = cdk.App()
TypescriptStack(app, "TypescriptStack")
```

## Python

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-lambda-subminute/tree/main/src/demo/python).

```bash
# upgrading related Python packages
$ python -m ensurepip --upgrade
$ python -m pip install --upgrade pip
$ python -m pip install --upgrade virtualenv
# initialize a CDK Python project
$ cdk init --language python
# make packages installed locally instead of globally
$ source .venv/bin/activate
$ cat <<EOL > requirements.txt
aws-cdk.core
aws-cdk.aws-lambda
cdk-lambda-subminute
EOL
$ python -m pip install -r requirements.txt
```

```python
from aws_cdk import core as cdk
from aws_cdk.aws_lambda import Code, Function, Runtime
from cdk_lambda_subminute import LambdaSubminute

class PythonStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        target_lambda = Function(
            self, "targetFunction",
            code=Code.from_inline(
                "exports.handler = function(event, ctx, cb) { return cb(null, \"hi\"); })"),
            function_name="testTargetFunction",
            runtime=Runtime.NODEJS_12_X,
            handler="index.handler"
        )
        cron_job_example = "cron(10/1 4-5 ? * SUN-SAT *)"
        subminute_master = LambdaSubminute(
            self, "LambdaSubminute",
            target_function=target_lambda,
            cronjob_expression=cron_job_example,
            frequency=7,
            interval_time=8)

        cdk.CfnOutput(self, "OStateMachineArn",
                      value=subminute_master.state_machine_arn)
        cdk.CfnOutput(self, "OIteratorFunctionArn",
                      value=subminute_master.iterator_function.function_arn)
```

```bash
$ deactivate
```

## Java

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-lambda-subminute/tree/main/src/demo/java).

```bash
$ cdk init --language java
$ mvn package
```

```xml
.
.
<properties>
      <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
      <cdk.version>1.105.0</cdk.version>
      <constrcut.verion>0.1.6</constrcut.verion>
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
            <groupId>software.amazon.awscdk</groupId>
            <artifactId>lambda</artifactId>
            <version>${cdk.version}</version>
      </dependency>
      <dependency>
            <groupId>io.github.hsiehshujeng</groupId>
            <artifactId>cdk-lambda-subminute</artifactId>
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
import software.amazon.awscdk.services.lambda.Code;
import software.amazon.awscdk.services.lambda.Function;
import software.amazon.awscdk.services.lambda.FunctionProps;
import software.amazon.awscdk.services.lambda.Runtime;
import io.github.hsiehshujeng.cdk.lambda.subminute.LambdaSubminute;
import io.github.hsiehshujeng.cdk.lambda.subminute.LambdaSubminuteProps;

public class JavaStack extends Stack {
    public JavaStack(final Construct scope, final String id) {
        this(scope, id, null);
    }

    public JavaStack(final Construct scope, final String id, final StackProps props) {
        super(scope, id, props);

        Function targetLambda = new Function(this, "targetFunction",
          FunctionProps.builder()
              .code(Code.fromInline("exports.handler = function(event, ctx, cb) { return cb(null, \"hi\"); })"))
              .functionName("estTargetFunction")
              .runtime(Runtime.NODEJS_12_X)
              .handler("index.handler")
              .build());
        String cronJobExample = "cron(50/1 4-5 ? * SUN-SAT *)";
        LambdaSubminute subminuteMaster = new LambdaSubminute(this, "LambdaSubminute", LambdaSubminuteProps.builder()
              .targetFunction(targetLambda)
              .cronjobExpression(cronJobExample)
              .frequency(6)
              .intervalTime(9)
              .build());

        new CfnOutput(this, "OStateMachineArn",
                CfnOutputProps.builder()
                  .value(subminuteMaster.getStateMachineArn())
                  .build());
        new CfnOutput(this, "OIteratorFunctionArn",
                CfnOutputProps.builder()
                  .value(subminuteMaster.getIteratorFunction().getFunctionName())
                  .build());
    }
}

```

## C#

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-lambda-subminute/tree/main/src/demo/csharp).

```bash
$ cdk init --language csharp
$ dotnet add src/Csharp package Amazon.CDK.AWS.Lambda
$ dotnet add src/Csharp package Lambda.Subminute --version 0.1.6
```

```cs
using Amazon.CDK;
using Amazon.CDK.AWS.Lambda;
using ScottHsieh.Cdk;

namespace Csharp
{
    public class CsharpStack : Stack
    {
        internal CsharpStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            var targetLambda = new Function(this, "targetFunction", new FunctionProps
            {
                Code = Code.FromInline("exports.handler = function(event, ctx, cb) { return cb(null, \"hi\"); })"),
                FunctionName = "testTargetFunction",
                Runtime = Runtime.NODEJS_12_X,
                Handler = "index.handler"
            });
            string cronJobExample = "cron(50/1 6-7 ? * SUN-SAT *)";
            var subminuteMaster = new LambdaSubminute(this, "LambdaSubminute", new LambdaSubminuteProps
            {
                TargetFunction = targetLambda,
                CronjobExpression = cronJobExample,
                Frequency = 10,
                IntervalTime = 6,
            });

            new CfnOutput(this, "OStateMachineArn", new CfnOutputProps
            {
                Value = subminuteMaster.StateMachineArn
            });
            new CfnOutput(this, "OIteratorFunctionArn", new CfnOutputProps
            {
                Value = subminuteMaster.IteratorFunction.FunctionArn
            });
        }
    }
}
```

# Statemachine Diagram

![image](https://raw.githubusercontent.com/HsiehShuJeng/cdk-lambda-subminute/main/images/statemachine_diagram.png)

# Known issue

Originally, I utilized `PythonFuncion` in the module of [**@aws-cdk/aws-lambda-python**](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-lambda-python-readme.html) to build the iterator Lambda function. Every thing works fine, including test, on my local machine (MacBook Pro M1), until it comes to the CI in Github Actions, it awlays gave me the following message:

```bash
## cdk version: 1.105.0 (build 4813992)
Bundling did not produce any output. Check that content is written to /asset-output.

      64 |     }));
      65 |
    > 66 |     this.function = new PythonFunction(this, 'Iterator', {
         |                     ^
      67 |       functionName: 'lambda-subminute-iterator',
      68 |       description: 'A function for breaking the limit of 1 minute with the CloudWatch Rules.',
      69 |       logRetention: RetentionDays.THREE_MONTHS,

      at AssetStaging.bundle (node_modules/@aws-cdk/core/lib/asset-staging.ts:484:13)
      at AssetStaging.stageByBundling (node_modules/@aws-cdk/core/lib/asset-staging.ts:328:10)
      at stageThisAsset (node_modules/@aws-cdk/core/lib/asset-staging.ts:194:35)
      at Cache.obtain (node_modules/@aws-cdk/core/lib/private/cache.ts:24:13)
      at new AssetStaging (node_modules/@aws-cdk/core/lib/asset-staging.ts:219:44)
      at new Asset (node_modules/@aws-cdk/aws-s3-assets/lib/asset.ts:127:21)
      at AssetCode.bind (node_modules/@aws-cdk/aws-lambda/lib/code.ts:277:20)
      at new Function (node_modules/@aws-cdk/aws-lambda/lib/function.ts:583:29)
      at new PythonFunction (node_modules/@aws-cdk/aws-lambda-python/lib/function.ts:106:5)
      at new IteratorLambda (src/cdk-lambda-subminute.ts:66:21)
      at new LambdaSubminute (src/cdk-lambda-subminute.ts:25:22)
      at Object.<anonymous>.test (test/integ.test.ts:23:3)
```

I actually have tried many different methods according to the following threads but to no avail.  I'll attempt to test some thoughts or just post the issue onto the CDK Github repo.

* [Asset Bundling](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-s3-assets-readme.html#asset-bundling)
* [Change the bundler's /asset-output local volume mount location #8589](https://github.com/aws/aws-cdk/issues/8589)
* [(aws-lambda-python: PythonFunction): unable to use bundling in BitBucket #14156](https://github.com/aws/aws-cdk/issues/14516)
* [BundlingDockerImage.cp() needs to be explained more in the README #11914](https://github.com/aws/aws-cdk/issues/11914)
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

import aws_cdk.aws_lambda
import aws_cdk.aws_stepfunctions
import aws_cdk.core


class IteratorLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-lambda-subminute.IteratorLambda",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        target_function: aws_cdk.aws_lambda.IFunction,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param target_function: The Lambda function that is going to be executed per time unit less than one minute.
        '''
        props = IteratorLambdaProps(target_function=target_function)

        jsii.create(IteratorLambda, self, [scope, name, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        '''A Lambda function that plays the role of the iterator.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "function"))


@jsii.data_type(
    jsii_type="cdk-lambda-subminute.IteratorLambdaProps",
    jsii_struct_bases=[],
    name_mapping={"target_function": "targetFunction"},
)
class IteratorLambdaProps:
    def __init__(self, *, target_function: aws_cdk.aws_lambda.IFunction) -> None:
        '''
        :param target_function: The Lambda function that is going to be executed per time unit less than one minute.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_function": target_function,
        }

    @builtins.property
    def target_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''The Lambda function that is going to be executed per time unit less than one minute.'''
        result = self._values.get("target_function")
        assert result is not None, "Required property 'target_function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IteratorLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaSubminute(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-lambda-subminute.LambdaSubminute",
):
    def __init__(
        self,
        parent: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        target_function: aws_cdk.aws_lambda.IFunction,
        cronjob_expression: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[jsii.Number] = None,
        interval_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param parent: -
        :param name: -
        :param target_function: The Lambda function that is going to be executed per time unit less than one minute.
        :param cronjob_expression: A pattern you want this statemachine to be executed. Default: cron(50/1 15-17 ? * * *) UTC+0 being run every minute starting from 15:00 PM to 17:00 PM.
        :param frequency: How many times you intent to execute in a minute. Default: 6
        :param interval_time: Seconds for an interval, the product of ``frequency`` and ``intervalTime`` should be approximagely 1 minute. Default: 10
        '''
        props = LambdaSubminuteProps(
            target_function=target_function,
            cronjob_expression=cronjob_expression,
            frequency=frequency,
            interval_time=interval_time,
        )

        jsii.create(LambdaSubminute, self, [parent, name, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iteratorFunction")
    def iterator_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''The Lambda function that plays the role of the iterator.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "iteratorFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> builtins.str:
        '''The ARN of the state machine that executes the target Lambda function per time unit less than one minute.'''
        return typing.cast(builtins.str, jsii.get(self, "stateMachineArn"))


@jsii.data_type(
    jsii_type="cdk-lambda-subminute.LambdaSubminuteProps",
    jsii_struct_bases=[],
    name_mapping={
        "target_function": "targetFunction",
        "cronjob_expression": "cronjobExpression",
        "frequency": "frequency",
        "interval_time": "intervalTime",
    },
)
class LambdaSubminuteProps:
    def __init__(
        self,
        *,
        target_function: aws_cdk.aws_lambda.IFunction,
        cronjob_expression: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[jsii.Number] = None,
        interval_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param target_function: The Lambda function that is going to be executed per time unit less than one minute.
        :param cronjob_expression: A pattern you want this statemachine to be executed. Default: cron(50/1 15-17 ? * * *) UTC+0 being run every minute starting from 15:00 PM to 17:00 PM.
        :param frequency: How many times you intent to execute in a minute. Default: 6
        :param interval_time: Seconds for an interval, the product of ``frequency`` and ``intervalTime`` should be approximagely 1 minute. Default: 10
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_function": target_function,
        }
        if cronjob_expression is not None:
            self._values["cronjob_expression"] = cronjob_expression
        if frequency is not None:
            self._values["frequency"] = frequency
        if interval_time is not None:
            self._values["interval_time"] = interval_time

    @builtins.property
    def target_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''The Lambda function that is going to be executed per time unit less than one minute.'''
        result = self._values.get("target_function")
        assert result is not None, "Required property 'target_function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    @builtins.property
    def cronjob_expression(self) -> typing.Optional[builtins.str]:
        '''A pattern you want this statemachine to be executed.

        :default: cron(50/1 15-17 ? * * *) UTC+0 being run every minute starting from 15:00 PM to 17:00 PM.

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html
        '''
        result = self._values.get("cronjob_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[jsii.Number]:
        '''How many times you intent to execute in a minute.

        :default: 6
        '''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval_time(self) -> typing.Optional[jsii.Number]:
        '''Seconds for an interval, the product of ``frequency`` and ``intervalTime`` should be approximagely 1 minute.

        :default: 10
        '''
        result = self._values.get("interval_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaSubminuteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SubminuteStateMachine(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-lambda-subminute.SubminuteStateMachine",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        frequency: jsii.Number,
        interval_time: jsii.Number,
        iterator_function: aws_cdk.aws_lambda.IFunction,
        state_machine_name: builtins.str,
        target_function: aws_cdk.aws_lambda.IFunction,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param frequency: How many times you intent to execute in a minute. Default: 6
        :param interval_time: Seconds for an interval, the product of ``frequency`` and ``intervalTime`` should be approximagely 1 minute. Default: 10
        :param iterator_function: the iterator Lambda function for the target Lambda function.
        :param state_machine_name: the name of the state machine.
        :param target_function: the Lambda function that executes your intention.
        '''
        props = SubminuteStateMachineProps(
            frequency=frequency,
            interval_time=interval_time,
            iterator_function=iterator_function,
            state_machine_name=state_machine_name,
            target_function=target_function,
        )

        jsii.create(SubminuteStateMachine, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> aws_cdk.aws_stepfunctions.StateMachine:
        return typing.cast(aws_cdk.aws_stepfunctions.StateMachine, jsii.get(self, "stateMachine"))


@jsii.data_type(
    jsii_type="cdk-lambda-subminute.SubminuteStateMachineProps",
    jsii_struct_bases=[],
    name_mapping={
        "frequency": "frequency",
        "interval_time": "intervalTime",
        "iterator_function": "iteratorFunction",
        "state_machine_name": "stateMachineName",
        "target_function": "targetFunction",
    },
)
class SubminuteStateMachineProps:
    def __init__(
        self,
        *,
        frequency: jsii.Number,
        interval_time: jsii.Number,
        iterator_function: aws_cdk.aws_lambda.IFunction,
        state_machine_name: builtins.str,
        target_function: aws_cdk.aws_lambda.IFunction,
    ) -> None:
        '''
        :param frequency: How many times you intent to execute in a minute. Default: 6
        :param interval_time: Seconds for an interval, the product of ``frequency`` and ``intervalTime`` should be approximagely 1 minute. Default: 10
        :param iterator_function: the iterator Lambda function for the target Lambda function.
        :param state_machine_name: the name of the state machine.
        :param target_function: the Lambda function that executes your intention.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "frequency": frequency,
            "interval_time": interval_time,
            "iterator_function": iterator_function,
            "state_machine_name": state_machine_name,
            "target_function": target_function,
        }

    @builtins.property
    def frequency(self) -> jsii.Number:
        '''How many times you intent to execute in a minute.

        :default: 6
        '''
        result = self._values.get("frequency")
        assert result is not None, "Required property 'frequency' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def interval_time(self) -> jsii.Number:
        '''Seconds for an interval, the product of ``frequency`` and ``intervalTime`` should be approximagely 1 minute.

        :default: 10
        '''
        result = self._values.get("interval_time")
        assert result is not None, "Required property 'interval_time' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def iterator_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''the iterator Lambda function for the target Lambda function.'''
        result = self._values.get("iterator_function")
        assert result is not None, "Required property 'iterator_function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    @builtins.property
    def state_machine_name(self) -> builtins.str:
        '''the name of the state machine.'''
        result = self._values.get("state_machine_name")
        assert result is not None, "Required property 'state_machine_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''the Lambda function that executes your intention.'''
        result = self._values.get("target_function")
        assert result is not None, "Required property 'target_function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SubminuteStateMachineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IteratorLambda",
    "IteratorLambdaProps",
    "LambdaSubminute",
    "LambdaSubminuteProps",
    "SubminuteStateMachine",
    "SubminuteStateMachineProps",
]

publication.publish()
