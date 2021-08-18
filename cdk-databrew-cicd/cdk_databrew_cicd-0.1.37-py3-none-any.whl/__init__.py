'''
# cdk-databrew-cicd

This construct creates a **CodePipeline** pipeline where users can push a **DataBrew** recipe into the **CodeCommit** repository and the recipe will be pushed to a pre-production AWS account and a production AWS account by order automatically.

[![License](https://img.shields.io/badge/License-Apache%202.0-green)](https://opensource.org/licenses/Apache-2.0)
[![Build](https://github.com/HsiehShuJeng/cdk-databrew-cicd/actions/workflows/build.yml/badge.svg)](https://github.com/HsiehShuJeng/cdk-databrew-cicd/actions/workflows/build.yml) [![Release](https://github.com/HsiehShuJeng/cdk-databrew-cicd/workflows/Release/badge.svg)](https://github.com/HsiehShuJeng/cdk-databrew-cicd/actions/workflows/release.yml)
[![Python](https://img.shields.io/pypi/pyversions/cdk-databrew-cicd)](https://pypi.org/) [![pip](https://img.shields.io/badge/pip%20install-cdk--databrew--cicd-blue)](https://pypi.org/project/cdk-databrew-cicd/)
[![npm version](https://img.shields.io/npm/v/cdk-databrew-cicd)](https://www.npmjs.com/package/cdk-databrew-cicd) [![pypi evrsion](https://img.shields.io/pypi/v/cdk-databrew-cicd)](https://pypi.org/project/cdk-databrew-cicd/) [![Maven](https://img.shields.io/maven-central/v/io.github.hsiehshujeng/cdk-databrew-cicd)](https://search.maven.org/search?q=a:cdk-databrew-cicd) [![nuget](https://img.shields.io/nuget/v/Databrew.Cicd)](https://www.nuget.org/packages/Databrew.Cicd/)

# Table of Contents

* [Serverless Architecture](#serverless-architecture)
* [Introduction](#introduction)
* [Example](#example)

  * [Typescript](#typescript)
  * [Python](#python)
  * [Java](#java)
  * [C#](#c)
* [Some Efforts after Stack Creation](#some-efforts-after-stack-creation)
* [How Successful Commits Look Like](#how-successful-commits-look-like)

# Serverless Architecture

![image](https://d2908q01vomqb2.cloudfront.net/b6692ea5df920cad691c20319a6fffd7a4a766b8/2021/05/19/image001.jpg) *Romi B. and Gaurav W., 2021*

# Introduction

The architecture was introduced by **Romi Boimer** and **Gaurav Wadhawan** and was posted on the AWS Blog as [*Set up CI/CD pipelines for AWS Glue DataBrew using AWS Developer Tools*](https://aws.amazon.com/tw/blogs/big-data/set-up-ci-cd-pipelines-for-aws-glue-databrew-using-aws-developer-tools/).
I converted the architecture into a CDK construct for 4 programming languages. Before applying the AWS construct, make sure you've set up a proper IAM role for the pre-production and production AWS accounts. You could achieve it either by creating manually or creating through a custom construct in this library.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_databrew_cicd import IamRole

IamRole(self, "AccountIamRole",
    environment="preproduction", # or 'production'
    account_iD="ACCOUNT_ID"
)
```

# Example

## Typescript

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-databrew-cicd/tree/main/src/demo/typescript).

```bash
$ cdk --init language typescript
$ yarn add cdk-databrew-cicd
```

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
from cdk_databrew_cicd import DataBrewCodePipeline

class TypescriptStack(cdk.Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        preproduction_account_id = "PREPRODUCTION_ACCOUNT_ID"
        production_account_id = "PRODUCTION_ACCOUNT_ID"

        data_brew_pipeline = DataBrewCodePipeline(self, "DataBrewCicdPipeline",
            preproduction_iam_role_arn=f"arn:{cdk.Aws.PARTITION}:iam::{preproductionAccountId}:role/preproduction-Databrew-Cicd-Role",
            production_iam_role_arn=f"arn:{cdk.Aws.PARTITION}:iam::{productionAccountId}:role/production-Databrew-Cicd-Role"
        )

        cdk.CfnOutput(self, "OPreproductionLambdaArn", value=data_brew_pipeline.preproduction_function_arn)
        cdk.CfnOutput(self, "OProductionLambdaArn", value=data_brew_pipeline.production_function_arn)
        cdk.CfnOutput(self, "OCodeCommitRepoArn", value=data_brew_pipeline.code_commit_repo_arn)
        cdk.CfnOutput(self, "OCodePipelineArn", value=data_brew_pipeline.code_pipeline_arn)

app = cdk.App()
TypescriptStack(app, "TypescriptStack",
    stack_name="DataBrew-CICD"
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
$ cat <<EOL > requirements.txt
aws-cdk.core
cdk-databrew-cicd
EOL
$ python -m pip install -r requirements.txt
```

```python
from aws_cdk import core as cdk
from cdk_databrew_cicd import DataBrewCodePipeline

class PythonStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        preproduction_account_id = "PREPRODUCTION_ACCOUNT_ID"
        production_account_id = "PRODUCTION_ACCOUNT_ID"

        databrew_pipeline = DataBrewCodePipeline(self,
        "DataBrewCicdPipeline",
        preproduction_iam_role_arn=f"arn:{cdk.Aws.PARTITION}:iam::{preproduction_account_id}:role/preproduction-Databrew-Cicd-Role",
        production_iam_role_arn=f"arn:{cdk.Aws.PARTITION}:iam::{production_account_id}:role/preproduction-Databrew-Cicd-Role",
            # bucket_name="OPTIONAL",
            # repo_name="OPTIONAL",
            # repo_name="OPTIONAL",
            # branch_namne="OPTIONAL",
            # pipeline_name="OPTIONAL"
            )

        cdk.CfnOutput(self, 'OPreproductionLambdaArn', value=databrew_pipeline.preproduction_function_arn)
        cdk.CfnOutput(self, 'OProductionLambdaArn', value=databrew_pipeline.production_function_arn)
        cdk.CfnOutput(self, 'OCodeCommitRepoArn', value=databrew_pipeline.code_commit_repo_arn)
        cdk.CfnOutput(self, 'OCodePipelineArn', value=databrew_pipeline.code_pipeline_arn)
```

```bash
$ deactivate
```

## Java

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-databrew-cicd/tree/main/src/demo/java).

```bash
$ cdk init --language java
$ mvn package
```

```xml
.
.
<properties>
      <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
      <cdk.version>1.107.0</cdk.version>
      <constrcut.verion>0.1.4</constrcut.verion>
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
        <artifactId>cdk-databrew-cicd</artifactId>
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
import io.github.hsiehshujeng.cdk.databrew.cicd.DataBrewCodePipeline;
import io.github.hsiehshujeng.cdk.databrew.cicd.DataBrewCodePipelineProps;

public class JavaStack extends Stack {
    public JavaStack(final Construct scope, final String id) {
        this(scope, id, null);
    }

    public JavaStack(final Construct scope, final String id, final StackProps props) {
        super(scope, id, props);
        String preproductionAccountId = "PREPRODUCTION_ACCOUNT_ID";
        String productionAccountId = "PRODUCTION_ACCOUNT_ID";
        DataBrewCodePipeline databrewPipeline = new DataBrewCodePipeline(this, "DataBrewCicdPipeline",
                DataBrewCodePipelineProps.builder().preproductionIamRoleArn(preproductionAccountId)
                        .productionIamRoleArn(productionAccountId)
                        // .bucketName("OPTIONAL")
                        // .branchName("OPTIONAL")
                        // .pipelineName("OPTIONAL")
                        .build());

        new CfnOutput(this, "OPreproductionLambdaArn",
                CfnOutputProps.builder()
                    .value(databrewPipeline.getPreproductionFunctionArn())
                    .build());
        new CfnOutput(this, "OProductionLambdaArn",
                CfnOutputProps.builder()
                    .value(databrewPipeline.getProductionFunctionArn())
                    .build());
        new CfnOutput(this, "OCodeCommitRepoArn",
                CfnOutputProps.builder()
                    .value(databrewPipeline.getCodeCommitRepoArn())
                    .build());
        new CfnOutput(this, "OCodePipelineArn",
                CfnOutputProps.builder()
                    .value(databrewPipeline.getCodePipelineArn())
                    .build());
    }
}
```

## C#

You could also refer to [here](https://github.com/HsiehShuJeng/cdk-databrew-cicd/tree/main/src/demo/csharp).

```bash
$ cdk init --language csharp
$ dotnet add src/Csharp package Databrew.Cicd --version 0.1.4
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
            var preproductionAccountId = "PREPRODUCTION_ACCOUNT_ID";
            var productionAccountId = "PRODUCTION_ACCOUNT_ID";

            var dataBrewPipeline = new DataBrewCodePipeline(this, "DataBrewCicdPipeline", new DataBrewCodePipelineProps
            {
                PreproductionIamRoleArn = $"arn:{Aws.PARTITION}:iam::{preproductionAccountId}:role/preproduction-Databrew-Cicd-Role",
                ProductionIamRoleArn = $"arn:{Aws.PARTITION}:iam::{productionAccountId}:role/preproduction-Databrew-Cicd-Role",
                // BucketName = "OPTIONAL",
                // RepoName = "OPTIONAL",
                // BranchName = "OPTIONAL",
                // PipelineName = "OPTIONAL"
            });
            new CfnOutput(this, "OPreproductionLambdaArn", new CfnOutputProps
            {
                Value = dataBrewPipeline.PreproductionFunctionArn
            });
            new CfnOutput(this, "OProductionLambdaArn", new CfnOutputProps
            {
                Value = dataBrewPipeline.ProductionFunctionArn
            });
            new CfnOutput(this, "OCodeCommitRepoArn", new CfnOutputProps
            {
                Value = dataBrewPipeline.CodeCommitRepoArn
            });
            new CfnOutput(this, "OCodePipelineArn", new CfnOutputProps
            {
                Value = dataBrewPipeline.CodeCommitRepoArn
            });
        }
    }
}
```

# Some Efforts after Stack Creation

## CodeCommit

1. Create HTTPS Git credentials for AWS CodeCommit with an IAM user that you're going to use.
   ![image](https://raw.githubusercontent.com/HsiehShuJeng/cdk-databrew-cicd/main/images/codecommit_credentials.png)
2. Run through the steps noted on the README.md of the CodeCommit repository after finishing establishing the stack via CDK. The returned message with success should be looked like the following (assume you have installed [`git-remote-codecommit`](https://pypi.org/project/git-remote-codecommit/)):

   ```bash
   $ git clone codecommit://scott.codecommit@DataBrew-Recipes-Repo
   Cloning into 'DataBrew-Recipes-Repo'...
   remote: Counting objects: 6, done.
   Unpacking objects: 100% (6/6), 2.03 KiB | 138.00 KiB/s, done.
   ```
3. Add a DataBrew recipe into the local repositroy (directory) and commit the change. (either directly on the main branch or merging another branch into the main branch)

## Glue DataBrew

1. Download any recipe either generated out by following [*Getting started with AWS Glue DataBrew*](https://docs.aws.amazon.com/zh_tw/databrew/latest/dg/getting-started.html) or made by yourself as **JSON file**.
   ![image](https://raw.githubusercontent.com/HsiehShuJeng/cdk-databrew-cicd/main/images/databrew_recipes.png)
2. Move the recipe from the download directory to the local directory for the CodeCommit repository.

   ```bash
   $ mv ${DOWNLOAD_DIRECTORY}/chess-project-recipe.json ${CODECOMMIT_LOCAL_DIRECTORY}/
   ```
3. Commit the change to a branch with a name you prefer.

   ```bash
   $ cd ${{CODECOMMIT_LOCAL_DIRECTORY}}
   $ git checkout -b add-recipe main
   $ git add .
   $ git commit -m "first recipe"
   $ git push --set-upstream origin add-recipe
   ```
4. Merge the branch into the main branch. Just go to the **AWS CodeCommit** web console to do the merge as its process is purely the same as you've already done thousands of times on **Github** but only with different UIs.

# How Successful Commits Look Like

1. In the infrastructure account, the status of the CodePipeline DataBrew pipeline should be similar as the following:
   ![image](https://raw.githubusercontent.com/HsiehShuJeng/cdk-databrew-cicd/main/images/infra_codepipeline.png)
2. In the **pre-production** account with the same region as where the CICD pipeline is deployed at the infrastructue account, you'll see this.
   ![image](https://raw.githubusercontent.com/HsiehShuJeng/cdk-databrew-cicd/main/images/preproduction-recipe.png)
3. In the **production** account with the same region as where the CICD pipeline is deployed at the infrastructue account, you'll see this.
   ![image](https://raw.githubusercontent.com/HsiehShuJeng/cdk-databrew-cicd/main/images/production-recipe.png)
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

import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.core


class CodePipelineIamRole(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-databrew-cicd.CodePipelineIamRole",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        bucket_arn: builtins.str,
        preproduction_lambda_arn: builtins.str,
        production_lambda_arn: builtins.str,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param bucket_arn: The ARN of the S3 bucket where you store your artifacts.
        :param preproduction_lambda_arn: The ARN of the Lambda function for the pre-production account.
        :param production_lambda_arn: The ARN of the Lambda function for the production account.
        :param role_name: The role name for the CodePipeline CICD pipeline. Default: 'DataBrew-Recipe-Pipeline-Role'
        '''
        props = CodePipelineIamRoleProps(
            bucket_arn=bucket_arn,
            preproduction_lambda_arn=preproduction_lambda_arn,
            production_lambda_arn=production_lambda_arn,
            role_name=role_name,
        )

        jsii.create(CodePipelineIamRole, self, [scope, name, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.Role:
        '''The representative of the IAM role for the CodePipeline CICD pipeline.'''
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The ARN of the IAM role for the CodePipeline CICD pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))


@jsii.data_type(
    jsii_type="cdk-databrew-cicd.CodePipelineIamRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_arn": "bucketArn",
        "preproduction_lambda_arn": "preproductionLambdaArn",
        "production_lambda_arn": "productionLambdaArn",
        "role_name": "roleName",
    },
)
class CodePipelineIamRoleProps:
    def __init__(
        self,
        *,
        bucket_arn: builtins.str,
        preproduction_lambda_arn: builtins.str,
        production_lambda_arn: builtins.str,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: The ARN of the S3 bucket where you store your artifacts.
        :param preproduction_lambda_arn: The ARN of the Lambda function for the pre-production account.
        :param production_lambda_arn: The ARN of the Lambda function for the production account.
        :param role_name: The role name for the CodePipeline CICD pipeline. Default: 'DataBrew-Recipe-Pipeline-Role'
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_arn": bucket_arn,
            "preproduction_lambda_arn": preproduction_lambda_arn,
            "production_lambda_arn": production_lambda_arn,
        }
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def bucket_arn(self) -> builtins.str:
        '''The ARN of the S3 bucket where you store your artifacts.'''
        result = self._values.get("bucket_arn")
        assert result is not None, "Required property 'bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def preproduction_lambda_arn(self) -> builtins.str:
        '''The ARN of the Lambda function for the pre-production account.'''
        result = self._values.get("preproduction_lambda_arn")
        assert result is not None, "Required property 'preproduction_lambda_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def production_lambda_arn(self) -> builtins.str:
        '''The ARN of the Lambda function for the production account.'''
        result = self._values.get("production_lambda_arn")
        assert result is not None, "Required property 'production_lambda_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''The role name for the CodePipeline CICD pipeline.

        :default: 'DataBrew-Recipe-Pipeline-Role'
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodePipelineIamRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataBrewCodePipeline(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-databrew-cicd.DataBrewCodePipeline",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        preproduction_iam_role_arn: builtins.str,
        production_iam_role_arn: builtins.str,
        branch_name: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        first_stage_artifact_name: typing.Optional[builtins.str] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        repo_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param preproduction_iam_role_arn: The ARN of the IAM role in the pre-production account.
        :param production_iam_role_arn: The ARN of the IAM role in the production account.
        :param branch_name: The name of the branch that will trigger the DataBrew CICD pipeline. Default: 'main'
        :param bucket_name: The name of the S3 bucket for the CodePipeline DataBrew CICD pipeline. Default: 'databrew-cicd-codepipelineartifactstorebucket'
        :param first_stage_artifact_name: the (required) name of the Artifact at the first stage. Default: 'SourceOutput'
        :param pipeline_name: The name of the CodePipeline Databrew CICD pipeline. Default: 'DataBrew-Recipe-Application'
        :param repo_name: The name of the CodeCommit repositroy for the DataBrew CICD pipeline. Default: 'DataBrew-Recipes-Repo'
        '''
        props = DataBrewCodePipelineProps(
            preproduction_iam_role_arn=preproduction_iam_role_arn,
            production_iam_role_arn=production_iam_role_arn,
            branch_name=branch_name,
            bucket_name=bucket_name,
            first_stage_artifact_name=first_stage_artifact_name,
            pipeline_name=pipeline_name,
            repo_name=repo_name,
        )

        jsii.create(DataBrewCodePipeline, self, [scope, name, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchName")
    def branch_name(self) -> builtins.str:
        '''The name of the branch that will trigger the DataBrew CICD pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "branchName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketArn")
    def bucket_arn(self) -> builtins.str:
        '''The ARN of the S3 bucket for the CodePipeline DataBrew CICD pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "bucketArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codeCommitRepoArn")
    def code_commit_repo_arn(self) -> builtins.str:
        '''The ARN of the CodeCommit repository.'''
        return typing.cast(builtins.str, jsii.get(self, "codeCommitRepoArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codePipelineArn")
    def code_pipeline_arn(self) -> builtins.str:
        '''The ARN of the DataBrew CICD pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "codePipelineArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firstStageArtifactName")
    def first_stage_artifact_name(self) -> builtins.str:
        '''the (required) name of the Artifact at the first stage.'''
        return typing.cast(builtins.str, jsii.get(self, "firstStageArtifactName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preproductionFunctionArn")
    def preproduction_function_arn(self) -> builtins.str:
        '''The ARN of the Lambda function for the pre-production account.'''
        return typing.cast(builtins.str, jsii.get(self, "preproductionFunctionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productionFunctionArn")
    def production_function_arn(self) -> builtins.str:
        '''The ARN of the Lambda function for the production account.'''
        return typing.cast(builtins.str, jsii.get(self, "productionFunctionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repoName")
    def repo_name(self) -> builtins.str:
        '''The name of the CodeCommit repositroy for the DataBrew CICD pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "repoName"))


@jsii.data_type(
    jsii_type="cdk-databrew-cicd.DataBrewCodePipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "preproduction_iam_role_arn": "preproductionIamRoleArn",
        "production_iam_role_arn": "productionIamRoleArn",
        "branch_name": "branchName",
        "bucket_name": "bucketName",
        "first_stage_artifact_name": "firstStageArtifactName",
        "pipeline_name": "pipelineName",
        "repo_name": "repoName",
    },
)
class DataBrewCodePipelineProps:
    def __init__(
        self,
        *,
        preproduction_iam_role_arn: builtins.str,
        production_iam_role_arn: builtins.str,
        branch_name: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        first_stage_artifact_name: typing.Optional[builtins.str] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        repo_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param preproduction_iam_role_arn: The ARN of the IAM role in the pre-production account.
        :param production_iam_role_arn: The ARN of the IAM role in the production account.
        :param branch_name: The name of the branch that will trigger the DataBrew CICD pipeline. Default: 'main'
        :param bucket_name: The name of the S3 bucket for the CodePipeline DataBrew CICD pipeline. Default: 'databrew-cicd-codepipelineartifactstorebucket'
        :param first_stage_artifact_name: the (required) name of the Artifact at the first stage. Default: 'SourceOutput'
        :param pipeline_name: The name of the CodePipeline Databrew CICD pipeline. Default: 'DataBrew-Recipe-Application'
        :param repo_name: The name of the CodeCommit repositroy for the DataBrew CICD pipeline. Default: 'DataBrew-Recipes-Repo'
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "preproduction_iam_role_arn": preproduction_iam_role_arn,
            "production_iam_role_arn": production_iam_role_arn,
        }
        if branch_name is not None:
            self._values["branch_name"] = branch_name
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if first_stage_artifact_name is not None:
            self._values["first_stage_artifact_name"] = first_stage_artifact_name
        if pipeline_name is not None:
            self._values["pipeline_name"] = pipeline_name
        if repo_name is not None:
            self._values["repo_name"] = repo_name

    @builtins.property
    def preproduction_iam_role_arn(self) -> builtins.str:
        '''The ARN of the IAM role in the pre-production account.'''
        result = self._values.get("preproduction_iam_role_arn")
        assert result is not None, "Required property 'preproduction_iam_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def production_iam_role_arn(self) -> builtins.str:
        '''The ARN of the IAM role in the production account.'''
        result = self._values.get("production_iam_role_arn")
        assert result is not None, "Required property 'production_iam_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_name(self) -> typing.Optional[builtins.str]:
        '''The name of the branch that will trigger the DataBrew CICD pipeline.

        :default: 'main'
        '''
        result = self._values.get("branch_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''The name of the S3 bucket for the CodePipeline DataBrew CICD pipeline.

        :default: 'databrew-cicd-codepipelineartifactstorebucket'
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def first_stage_artifact_name(self) -> typing.Optional[builtins.str]:
        '''the (required) name of the Artifact at the first stage.

        :default: 'SourceOutput'
        '''
        result = self._values.get("first_stage_artifact_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        '''The name of the CodePipeline Databrew CICD pipeline.

        :default: 'DataBrew-Recipe-Application'
        '''
        result = self._values.get("pipeline_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repo_name(self) -> typing.Optional[builtins.str]:
        '''The name of the CodeCommit repositroy for the DataBrew CICD pipeline.

        :default: 'DataBrew-Recipes-Repo'
        '''
        result = self._values.get("repo_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataBrewCodePipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FirstCommitHandler(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-databrew-cicd.FirstCommitHandler",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        branch_name: builtins.str,
        code_commit_repo_arn: builtins.str,
        repo_name: builtins.str,
        function_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param branch_name: The branch name used in the CodeCommit repo.
        :param code_commit_repo_arn: The ARN of the CodeCommit repository.
        :param repo_name: The name of the CodeCommit repo.
        :param function_name: The name of the Lambda function which deals with first commit via AWS CodeCommit. Default: 'FirstCommitHandler'
        :param role_name: The name of the IAM role for the Lambda function which deals with first commit via AWS CodeCommit. Default: 'LambdaForInitialCommitRole'
        '''
        props = FirstCommitHandlerProps(
            branch_name=branch_name,
            code_commit_repo_arn=code_commit_repo_arn,
            repo_name=repo_name,
            function_name=function_name,
            role_name=role_name,
        )

        jsii.create(FirstCommitHandler, self, [scope, name, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        '''The representative of Lambda function which deals with first commit via AWS CodeCommit.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "function"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        '''The name of the Lambda function which deals with first commit via AWS CodeCommit.'''
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        '''The name of the IAM role for the Lambda function which deals with first commit via AWS CodeCommit.'''
        return typing.cast(builtins.str, jsii.get(self, "roleName"))


@jsii.data_type(
    jsii_type="cdk-databrew-cicd.FirstCommitHandlerProps",
    jsii_struct_bases=[],
    name_mapping={
        "branch_name": "branchName",
        "code_commit_repo_arn": "codeCommitRepoArn",
        "repo_name": "repoName",
        "function_name": "functionName",
        "role_name": "roleName",
    },
)
class FirstCommitHandlerProps:
    def __init__(
        self,
        *,
        branch_name: builtins.str,
        code_commit_repo_arn: builtins.str,
        repo_name: builtins.str,
        function_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param branch_name: The branch name used in the CodeCommit repo.
        :param code_commit_repo_arn: The ARN of the CodeCommit repository.
        :param repo_name: The name of the CodeCommit repo.
        :param function_name: The name of the Lambda function which deals with first commit via AWS CodeCommit. Default: 'FirstCommitHandler'
        :param role_name: The name of the IAM role for the Lambda function which deals with first commit via AWS CodeCommit. Default: 'LambdaForInitialCommitRole'
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "branch_name": branch_name,
            "code_commit_repo_arn": code_commit_repo_arn,
            "repo_name": repo_name,
        }
        if function_name is not None:
            self._values["function_name"] = function_name
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def branch_name(self) -> builtins.str:
        '''The branch name used in the CodeCommit repo.'''
        result = self._values.get("branch_name")
        assert result is not None, "Required property 'branch_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_commit_repo_arn(self) -> builtins.str:
        '''The ARN of the CodeCommit repository.'''
        result = self._values.get("code_commit_repo_arn")
        assert result is not None, "Required property 'code_commit_repo_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo_name(self) -> builtins.str:
        '''The name of the CodeCommit repo.'''
        result = self._values.get("repo_name")
        assert result is not None, "Required property 'repo_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''The name of the Lambda function which deals with first commit via AWS CodeCommit.

        :default: 'FirstCommitHandler'
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role for the Lambda function which deals with first commit via AWS CodeCommit.

        :default: 'LambdaForInitialCommitRole'
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirstCommitHandlerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamRole(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-databrew-cicd.IamRole",
):
    '''IAM Role.

    Defines an IAM role for pre-production and production AWS accounts.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        account_id: builtins.str,
        environment: builtins.str,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param account_id: The ID of your infrastructure account.
        :param environment: 'preproduction' or 'production'.
        :param role_name: The role name. Default: '{environment}-Databrew-Cicd-Role'
        '''
        props = IamRoleProps(
            account_id=account_id, environment=environment, role_name=role_name
        )

        jsii.create(IamRole, self, [scope, name, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The ARN of the IAM role for pre-production or production.'''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))


@jsii.data_type(
    jsii_type="cdk-databrew-cicd.IamRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountID",
        "environment": "environment",
        "role_name": "roleName",
    },
)
class IamRoleProps:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        environment: builtins.str,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_id: The ID of your infrastructure account.
        :param environment: 'preproduction' or 'production'.
        :param role_name: The role name. Default: '{environment}-Databrew-Cicd-Role'
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "environment": environment,
        }
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def account_id(self) -> builtins.str:
        '''The ID of your infrastructure account.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def environment(self) -> builtins.str:
        ''''preproduction' or 'production'.'''
        result = self._values.get("environment")
        assert result is not None, "Required property 'environment' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''The role name.

        :default: '{environment}-Databrew-Cicd-Role'
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InfraIamRole(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-databrew-cicd.InfraIamRole",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param role_name: The role name for the infrastructure account. Default: 'CrossAccountRepositoryContributorRole'
        '''
        props = InfraIamRoleProps(role_name=role_name)

        jsii.create(InfraIamRole, self, [scope, name, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The ARN of the IAM role for the infrastructure account.'''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))


@jsii.data_type(
    jsii_type="cdk-databrew-cicd.InfraIamRoleProps",
    jsii_struct_bases=[],
    name_mapping={"role_name": "roleName"},
)
class InfraIamRoleProps:
    def __init__(self, *, role_name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param role_name: The role name for the infrastructure account. Default: 'CrossAccountRepositoryContributorRole'
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''The role name for the infrastructure account.

        :default: 'CrossAccountRepositoryContributorRole'
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InfraIamRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PreProductionLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-databrew-cicd.PreProductionLambda",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        bucket_arn: builtins.str,
        preproduction_iam_role_arn: builtins.str,
        function_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param bucket_arn: The ARN of the S3 bucket for the DataBrew CICD pipeline.
        :param preproduction_iam_role_arn: The ARN of the IAM role in the pre-production account.
        :param function_name: The Lambda funciton name for the pre-production account. Default: 'PreProd-DataBrew-Recipe-Deployer'
        :param role_name: The name of the IAM role for the pre-produciton Lambda function. Default: 'PreProd-DataBrew-Recipe-Deployer-role'
        '''
        props = PreProductionLambdaProps(
            bucket_arn=bucket_arn,
            preproduction_iam_role_arn=preproduction_iam_role_arn,
            function_name=function_name,
            role_name=role_name,
        )

        jsii.create(PreProductionLambda, self, [scope, name, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        '''The representative of Lambda function for the pre-production account.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "function"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        '''The Lambda funciton name for the pre-production account.'''
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        '''The name of the IAM role for the pre-produciton Lambda function.'''
        return typing.cast(builtins.str, jsii.get(self, "roleName"))


@jsii.data_type(
    jsii_type="cdk-databrew-cicd.PreProductionLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_arn": "bucketArn",
        "preproduction_iam_role_arn": "preproductionIamRoleArn",
        "function_name": "functionName",
        "role_name": "roleName",
    },
)
class PreProductionLambdaProps:
    def __init__(
        self,
        *,
        bucket_arn: builtins.str,
        preproduction_iam_role_arn: builtins.str,
        function_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: The ARN of the S3 bucket for the DataBrew CICD pipeline.
        :param preproduction_iam_role_arn: The ARN of the IAM role in the pre-production account.
        :param function_name: The Lambda funciton name for the pre-production account. Default: 'PreProd-DataBrew-Recipe-Deployer'
        :param role_name: The name of the IAM role for the pre-produciton Lambda function. Default: 'PreProd-DataBrew-Recipe-Deployer-role'
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_arn": bucket_arn,
            "preproduction_iam_role_arn": preproduction_iam_role_arn,
        }
        if function_name is not None:
            self._values["function_name"] = function_name
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def bucket_arn(self) -> builtins.str:
        '''The ARN of the S3 bucket for the DataBrew CICD pipeline.'''
        result = self._values.get("bucket_arn")
        assert result is not None, "Required property 'bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def preproduction_iam_role_arn(self) -> builtins.str:
        '''The ARN of the IAM role in the pre-production account.'''
        result = self._values.get("preproduction_iam_role_arn")
        assert result is not None, "Required property 'preproduction_iam_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''The Lambda funciton name for the pre-production account.

        :default: 'PreProd-DataBrew-Recipe-Deployer'
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role for the pre-produciton Lambda function.

        :default: 'PreProd-DataBrew-Recipe-Deployer-role'
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreProductionLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ProductionLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-databrew-cicd.ProductionLambda",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        bucket_arn: builtins.str,
        production_iam_role_arn: builtins.str,
        function_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param bucket_arn: The ARN of the S3 bucket for the DataBrew CICD pipeline.
        :param production_iam_role_arn: The ARN of the IAM role in the production account.
        :param function_name: The Lambda funciton name for the production account. Default: 'Prod-DataBrew-Recipe-Deployer'
        :param role_name: The name of the IAM role for the produciton Lambda function. Default: 'Prod-DataBrew-Recipe-Deployer-role'
        '''
        props = ProductionLambdaProps(
            bucket_arn=bucket_arn,
            production_iam_role_arn=production_iam_role_arn,
            function_name=function_name,
            role_name=role_name,
        )

        jsii.create(ProductionLambda, self, [scope, name, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        '''The representative of Lambda function for the production account.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "function"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        '''The Lambda funciton name for the production account.'''
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        '''The name of the IAM role for the produciton Lambda function.'''
        return typing.cast(builtins.str, jsii.get(self, "roleName"))


@jsii.data_type(
    jsii_type="cdk-databrew-cicd.ProductionLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_arn": "bucketArn",
        "production_iam_role_arn": "productionIamRoleArn",
        "function_name": "functionName",
        "role_name": "roleName",
    },
)
class ProductionLambdaProps:
    def __init__(
        self,
        *,
        bucket_arn: builtins.str,
        production_iam_role_arn: builtins.str,
        function_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: The ARN of the S3 bucket for the DataBrew CICD pipeline.
        :param production_iam_role_arn: The ARN of the IAM role in the production account.
        :param function_name: The Lambda funciton name for the production account. Default: 'Prod-DataBrew-Recipe-Deployer'
        :param role_name: The name of the IAM role for the produciton Lambda function. Default: 'Prod-DataBrew-Recipe-Deployer-role'
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_arn": bucket_arn,
            "production_iam_role_arn": production_iam_role_arn,
        }
        if function_name is not None:
            self._values["function_name"] = function_name
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def bucket_arn(self) -> builtins.str:
        '''The ARN of the S3 bucket for the DataBrew CICD pipeline.'''
        result = self._values.get("bucket_arn")
        assert result is not None, "Required property 'bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def production_iam_role_arn(self) -> builtins.str:
        '''The ARN of the IAM role in the production account.'''
        result = self._values.get("production_iam_role_arn")
        assert result is not None, "Required property 'production_iam_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''The Lambda funciton name for the production account.

        :default: 'Prod-DataBrew-Recipe-Deployer'
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role for the produciton Lambda function.

        :default: 'Prod-DataBrew-Recipe-Deployer-role'
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProductionLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CodePipelineIamRole",
    "CodePipelineIamRoleProps",
    "DataBrewCodePipeline",
    "DataBrewCodePipelineProps",
    "FirstCommitHandler",
    "FirstCommitHandlerProps",
    "IamRole",
    "IamRoleProps",
    "InfraIamRole",
    "InfraIamRoleProps",
    "PreProductionLambda",
    "PreProductionLambdaProps",
    "ProductionLambda",
    "ProductionLambdaProps",
]

publication.publish()
