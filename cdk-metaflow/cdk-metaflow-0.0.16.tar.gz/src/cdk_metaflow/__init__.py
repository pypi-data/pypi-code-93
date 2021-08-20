'''
# CDK Metaflow

The `cdk-metaflow` package contains cdk constructs for deploying metaflow infrastructure on aws.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import cdk_metaflow as metaflow
```

## Metaflow

The main construct creates all the required infrastructure for getting up and running with Metaflow on AWS. This is achieved by creating an instance of `Metaflow`:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
metaflow = Metaflow(self, "metaflow")
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

import aws_cdk.aws_apigateway
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_dynamodb
import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_kinesis
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.aws_rds
import aws_cdk.aws_s3
import aws_cdk.aws_secretsmanager
import aws_cdk.core


class BatchExecutionRole(
    aws_cdk.aws_iam.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.BatchExecutionRole",
):
    '''
    :stability: experimental
    :summary: Batch Execution Role
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the BatchExecutionRole class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(BatchExecutionRole, self, [scope, id])


class BatchS3TaskRole(
    aws_cdk.aws_iam.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.BatchS3TaskRole",
):
    '''
    :stability: experimental
    :summary: Batch S3 Task Role
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the BatchS3TaskRole class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(BatchS3TaskRole, self, [scope, id])


@jsii.data_type(
    jsii_type="cdk-metaflow.DashboardProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "dashboard_name": "dashboardName",
        "ecs_service": "ecsService",
        "period": "period",
    },
)
class DashboardProps:
    def __init__(
        self,
        *,
        bucket_name: builtins.str,
        dashboard_name: builtins.str,
        ecs_service: aws_cdk.aws_ecs.FargateService,
        period: jsii.Number,
    ) -> None:
        '''
        :param bucket_name: 
        :param dashboard_name: 
        :param ecs_service: 
        :param period: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
            "dashboard_name": dashboard_name,
            "ecs_service": ecs_service,
            "period": period,
        }

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dashboard_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("dashboard_name")
        assert result is not None, "Required property 'dashboard_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ecs_service(self) -> aws_cdk.aws_ecs.FargateService:
        '''
        :stability: experimental
        '''
        result = self._values.get("ecs_service")
        assert result is not None, "Required property 'ecs_service' is missing"
        return typing.cast(aws_cdk.aws_ecs.FargateService, result)

    @builtins.property
    def period(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DashboardProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EcsExecutionRole(
    aws_cdk.aws_iam.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.EcsExecutionRole",
):
    '''
    :stability: experimental
    :summary: ECS Execution Role
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the EcsExecutionRole class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(EcsExecutionRole, self, [scope, id])


class EcsRole(
    aws_cdk.aws_iam.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.EcsRole",
):
    '''
    :stability: experimental
    :summary: Ecs  Role
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the EcsRole class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(EcsRole, self, [scope, id])


class EcsTaskRole(
    aws_cdk.aws_iam.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.EcsTaskRole",
):
    '''
    :stability: experimental
    :summary: ECS Task Role
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the EcsTaskRole class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(EcsTaskRole, self, [scope, id])


class EventBridgeRole(
    aws_cdk.aws_iam.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.EventBridgeRole",
):
    '''
    :stability: experimental
    :summary: EventBridge Role
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the EventBridgeRole class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(EventBridgeRole, self, [scope, id])


@jsii.interface(jsii_type="cdk-metaflow.IMetaflowDatabase")
class IMetaflowDatabase(typing_extensions.Protocol):
    '''
    :stability: experimental
    :summary: Metaflow Database Interface
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''(experimental) Database credentials in standard RDS json format.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> aws_cdk.aws_rds.IDatabaseInstance:
        '''(experimental) A database instance;

        can be extended to be a union type of Aurora Serverless or RDS Cluster.

        :stability: experimental
        '''
        ...


class _IMetaflowDatabaseProxy:
    '''
    :stability: experimental
    :summary: Metaflow Database Interface
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk-metaflow.IMetaflowDatabase"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''(experimental) Database credentials in standard RDS json format.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.get(self, "credentials"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> aws_cdk.aws_rds.IDatabaseInstance:
        '''(experimental) A database instance;

        can be extended to be a union type of Aurora Serverless or RDS Cluster.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_rds.IDatabaseInstance, jsii.get(self, "database"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMetaflowDatabase).__jsii_proxy_class__ = lambda : _IMetaflowDatabaseProxy


class LambdaECSExecuteRole(
    aws_cdk.aws_iam.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.LambdaECSExecuteRole",
):
    '''
    :stability: experimental
    :summary: Lambda ECS Execute Role
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the LambdaECSExecuteRole class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(LambdaECSExecuteRole, self, [scope, id])


class Metaflow(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.Metaflow",
):
    '''
    :stability: experimental
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        jsii.create(Metaflow, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="api")
    def api(self) -> aws_cdk.aws_apigateway.IRestApi:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigateway.IRestApi, jsii.get(self, "api"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="batchExecutionRole")
    def batch_execution_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "batchExecutionRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="batchS3TaskRole")
    def batch_s3_task_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "batchS3TaskRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> aws_cdk.aws_ecs.ICluster:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ecs.ICluster, jsii.get(self, "cluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> IMetaflowDatabase:
        '''
        :stability: experimental
        '''
        return typing.cast(IMetaflowDatabase, jsii.get(self, "database"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbMigrateLambda")
    def db_migrate_lambda(self) -> aws_cdk.aws_lambda.IFunction:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "dbMigrateLambda"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsExecutionRole")
    def ecs_execution_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "ecsExecutionRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsRole")
    def ecs_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "ecsRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsTaskRole")
    def ecs_task_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "ecsTaskRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventBridgeRole")
    def event_bridge_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "eventBridgeRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventBus")
    def event_bus(self) -> aws_cdk.aws_events.IEventBus:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_events.IEventBus, jsii.get(self, "eventBus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaECSExecuteRole")
    def lambda_ecs_execute_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "lambdaECSExecuteRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stepFunctionsRole")
    def step_functions_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "stepFunctionsRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_dynamodb.ITable, jsii.get(self, "table"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


class MetaflowApi(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.MetaflowApi",
):
    '''
    :stability: experimental
    :summary: Metaflow Api
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        nlb: aws_cdk.aws_elasticloadbalancingv2.INetworkLoadBalancer,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param nlb: 

        :stability: experimental
        '''
        props = MetaflowApiProps(nlb=nlb)

        jsii.create(MetaflowApi, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="api")
    def api(self) -> aws_cdk.aws_apigateway.IRestApi:
        '''(experimental) Constructs a new instance of the MetaflowApi class.

        :stability: experimental
        :access: public
        '''
        return typing.cast(aws_cdk.aws_apigateway.IRestApi, jsii.get(self, "api"))


@jsii.data_type(
    jsii_type="cdk-metaflow.MetaflowApiProps",
    jsii_struct_bases=[],
    name_mapping={"nlb": "nlb"},
)
class MetaflowApiProps:
    def __init__(
        self,
        *,
        nlb: aws_cdk.aws_elasticloadbalancingv2.INetworkLoadBalancer,
    ) -> None:
        '''
        :param nlb: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "nlb": nlb,
        }

    @builtins.property
    def nlb(self) -> aws_cdk.aws_elasticloadbalancingv2.INetworkLoadBalancer:
        '''
        :stability: experimental
        '''
        result = self._values.get("nlb")
        assert result is not None, "Required property 'nlb' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.INetworkLoadBalancer, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetaflowBucket(
    aws_cdk.aws_s3.Bucket,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.MetaflowBucket",
):
    '''
    :stability: experimental
    :summary:

    Metaflow S3 Bucket
    S3 bucket for metaflow artifacts. Creates a standard bucket for holding
    metaflow artifacts and with iam DENY policy for REST-HEADER auth.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        access_control: typing.Optional[aws_cdk.aws_s3.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[aws_cdk.aws_s3.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[aws_cdk.aws_s3.CorsRule]] = None,
        encryption: typing.Optional[aws_cdk.aws_s3.BucketEncryption] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        inventories: typing.Optional[typing.Sequence[aws_cdk.aws_s3.Inventory]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[aws_cdk.aws_s3.LifecycleRule]] = None,
        metrics: typing.Optional[typing.Sequence[aws_cdk.aws_s3.BucketMetrics]] = None,
        object_ownership: typing.Optional[aws_cdk.aws_s3.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        server_access_logs_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[aws_cdk.aws_s3.RedirectTarget] = None,
        website_routing_rules: typing.Optional[typing.Sequence[aws_cdk.aws_s3.RoutingRule]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Specifies whether Amazon S3 should use an S3 Bucket Key with server-side encryption using KMS (SSE-KMS) for new objects in the bucket. Only relevant, when Encryption is set to {@link BucketEncryption.KMS} Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``Kms`` if ``encryptionKey`` is specified, or ``Unencrypted`` otherwise.
        :param encryption_key: External KMS key to use for bucket encryption. The 'encryption' property must be either not specified or set to "Kms". An error will be emitted if encryption is set to "Unencrypted" or "Managed". Default: - If encryption is set to "Kms" and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration, uploading account will own the object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.

        :stability: experimental
        '''
        props = aws_cdk.aws_s3.BucketProps(
            access_control=access_control,
            auto_delete_objects=auto_delete_objects,
            block_public_access=block_public_access,
            bucket_key_enabled=bucket_key_enabled,
            bucket_name=bucket_name,
            cors=cors,
            encryption=encryption,
            encryption_key=encryption_key,
            enforce_ssl=enforce_ssl,
            inventories=inventories,
            lifecycle_rules=lifecycle_rules,
            metrics=metrics,
            object_ownership=object_ownership,
            public_read_access=public_read_access,
            removal_policy=removal_policy,
            server_access_logs_bucket=server_access_logs_bucket,
            server_access_logs_prefix=server_access_logs_prefix,
            versioned=versioned,
            website_error_document=website_error_document,
            website_index_document=website_index_document,
            website_redirect=website_redirect,
            website_routing_rules=website_routing_rules,
        )

        jsii.create(MetaflowBucket, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> aws_cdk.aws_s3.CfnBucket:
        '''(experimental) Constructs a new instance of the MetaflowBucket class.

        :stability: experimental
        :access: public
        '''
        return typing.cast(aws_cdk.aws_s3.CfnBucket, jsii.get(self, "resource"))


class MetaflowDashboard(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.MetaflowDashboard",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        bucket_name: builtins.str,
        dashboard_name: builtins.str,
        ecs_service: aws_cdk.aws_ecs.FargateService,
        period: jsii.Number,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: 
        :param dashboard_name: 
        :param ecs_service: 
        :param period: 

        :stability: experimental
        '''
        props = DashboardProps(
            bucket_name=bucket_name,
            dashboard_name=dashboard_name,
            ecs_service=ecs_service,
            period=period,
        )

        jsii.create(MetaflowDashboard, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dashboard")
    def dashboard(self) -> aws_cdk.aws_cloudwatch.Dashboard:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Dashboard, jsii.get(self, "dashboard"))


@jsii.implements(IMetaflowDatabase)
class MetaflowDatabaseInstance(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.MetaflowDatabaseInstance",
):
    '''(experimental) Provides a very basic RDS database instance.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        db_security_groups: typing.Sequence[aws_cdk.aws_ec2.SecurityGroup],
        db_subnets: aws_cdk.aws_ec2.SubnetSelection,
        vpc: aws_cdk.aws_ec2.IVpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param db_security_groups: 
        :param db_subnets: 
        :param vpc: 

        :stability: experimental
        '''
        props = MetaflowDatabaseInstanceProps(
            db_security_groups=db_security_groups, db_subnets=db_subnets, vpc=vpc
        )

        jsii.create(MetaflowDatabaseInstance, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''(experimental) Database credentials in standard RDS json format.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.get(self, "credentials"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> aws_cdk.aws_rds.IDatabaseInstance:
        '''(experimental) A database instance;

        can be extended to be a union type of Aurora Serverless or RDS Cluster.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_rds.IDatabaseInstance, jsii.get(self, "database"))


@jsii.data_type(
    jsii_type="cdk-metaflow.MetaflowDatabaseInstanceProps",
    jsii_struct_bases=[],
    name_mapping={
        "db_security_groups": "dbSecurityGroups",
        "db_subnets": "dbSubnets",
        "vpc": "vpc",
    },
)
class MetaflowDatabaseInstanceProps:
    def __init__(
        self,
        *,
        db_security_groups: typing.Sequence[aws_cdk.aws_ec2.SecurityGroup],
        db_subnets: aws_cdk.aws_ec2.SubnetSelection,
        vpc: aws_cdk.aws_ec2.IVpc,
    ) -> None:
        '''
        :param db_security_groups: 
        :param db_subnets: 
        :param vpc: 

        :stability: experimental
        '''
        if isinstance(db_subnets, dict):
            db_subnets = aws_cdk.aws_ec2.SubnetSelection(**db_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "db_security_groups": db_security_groups,
            "db_subnets": db_subnets,
            "vpc": vpc,
        }

    @builtins.property
    def db_security_groups(self) -> typing.List[aws_cdk.aws_ec2.SecurityGroup]:
        '''
        :stability: experimental
        '''
        result = self._values.get("db_security_groups")
        assert result is not None, "Required property 'db_security_groups' is missing"
        return typing.cast(typing.List[aws_cdk.aws_ec2.SecurityGroup], result)

    @builtins.property
    def db_subnets(self) -> aws_cdk.aws_ec2.SubnetSelection:
        '''
        :stability: experimental
        '''
        result = self._values.get("db_subnets")
        assert result is not None, "Required property 'db_subnets' is missing"
        return typing.cast(aws_cdk.aws_ec2.SubnetSelection, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowDatabaseInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-metaflow.MetaflowExportProps",
    jsii_struct_bases=[],
    name_mapping={
        "batch_execution_role_arn": "batchExecutionRoleArn",
        "batch_s3_task_role_arn": "batchS3TaskRoleArn",
        "bucket_name": "bucketName",
        "ecs_execution_role_arn": "ecsExecutionRoleArn",
        "ecs_role_arn": "ecsRoleArn",
        "ecs_task_role_arn": "ecsTaskRoleArn",
        "event_bridge_role_arn": "eventBridgeRoleArn",
        "lambda_ecs_execute_role_arn": "lambdaECSExecuteRoleArn",
        "migrate_lambda_name": "migrateLambdaName",
        "nlb_dns_name": "nlbDnsName",
        "step_functions_role_arn": "stepFunctionsRoleArn",
        "table_name": "tableName",
    },
)
class MetaflowExportProps:
    def __init__(
        self,
        *,
        batch_execution_role_arn: builtins.str,
        batch_s3_task_role_arn: builtins.str,
        bucket_name: builtins.str,
        ecs_execution_role_arn: builtins.str,
        ecs_role_arn: builtins.str,
        ecs_task_role_arn: builtins.str,
        event_bridge_role_arn: builtins.str,
        lambda_ecs_execute_role_arn: builtins.str,
        migrate_lambda_name: builtins.str,
        nlb_dns_name: builtins.str,
        step_functions_role_arn: builtins.str,
        table_name: builtins.str,
    ) -> None:
        '''
        :param batch_execution_role_arn: 
        :param batch_s3_task_role_arn: 
        :param bucket_name: 
        :param ecs_execution_role_arn: 
        :param ecs_role_arn: 
        :param ecs_task_role_arn: 
        :param event_bridge_role_arn: 
        :param lambda_ecs_execute_role_arn: 
        :param migrate_lambda_name: 
        :param nlb_dns_name: 
        :param step_functions_role_arn: 
        :param table_name: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "batch_execution_role_arn": batch_execution_role_arn,
            "batch_s3_task_role_arn": batch_s3_task_role_arn,
            "bucket_name": bucket_name,
            "ecs_execution_role_arn": ecs_execution_role_arn,
            "ecs_role_arn": ecs_role_arn,
            "ecs_task_role_arn": ecs_task_role_arn,
            "event_bridge_role_arn": event_bridge_role_arn,
            "lambda_ecs_execute_role_arn": lambda_ecs_execute_role_arn,
            "migrate_lambda_name": migrate_lambda_name,
            "nlb_dns_name": nlb_dns_name,
            "step_functions_role_arn": step_functions_role_arn,
            "table_name": table_name,
        }

    @builtins.property
    def batch_execution_role_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("batch_execution_role_arn")
        assert result is not None, "Required property 'batch_execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def batch_s3_task_role_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("batch_s3_task_role_arn")
        assert result is not None, "Required property 'batch_s3_task_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ecs_execution_role_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("ecs_execution_role_arn")
        assert result is not None, "Required property 'ecs_execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ecs_role_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("ecs_role_arn")
        assert result is not None, "Required property 'ecs_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ecs_task_role_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("ecs_task_role_arn")
        assert result is not None, "Required property 'ecs_task_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def event_bridge_role_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("event_bridge_role_arn")
        assert result is not None, "Required property 'event_bridge_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_ecs_execute_role_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("lambda_ecs_execute_role_arn")
        assert result is not None, "Required property 'lambda_ecs_execute_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def migrate_lambda_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("migrate_lambda_name")
        assert result is not None, "Required property 'migrate_lambda_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nlb_dns_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("nlb_dns_name")
        assert result is not None, "Required property 'nlb_dns_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def step_functions_role_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("step_functions_role_arn")
        assert result is not None, "Required property 'step_functions_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowExportProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetaflowExports(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.MetaflowExports",
):
    '''
    :stability: experimental
    :summary: Metaflow Nlb
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        batch_execution_role_arn: builtins.str,
        batch_s3_task_role_arn: builtins.str,
        bucket_name: builtins.str,
        ecs_execution_role_arn: builtins.str,
        ecs_role_arn: builtins.str,
        ecs_task_role_arn: builtins.str,
        event_bridge_role_arn: builtins.str,
        lambda_ecs_execute_role_arn: builtins.str,
        migrate_lambda_name: builtins.str,
        nlb_dns_name: builtins.str,
        step_functions_role_arn: builtins.str,
        table_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param batch_execution_role_arn: 
        :param batch_s3_task_role_arn: 
        :param bucket_name: 
        :param ecs_execution_role_arn: 
        :param ecs_role_arn: 
        :param ecs_task_role_arn: 
        :param event_bridge_role_arn: 
        :param lambda_ecs_execute_role_arn: 
        :param migrate_lambda_name: 
        :param nlb_dns_name: 
        :param step_functions_role_arn: 
        :param table_name: 

        :stability: experimental
        '''
        props = MetaflowExportProps(
            batch_execution_role_arn=batch_execution_role_arn,
            batch_s3_task_role_arn=batch_s3_task_role_arn,
            bucket_name=bucket_name,
            ecs_execution_role_arn=ecs_execution_role_arn,
            ecs_role_arn=ecs_role_arn,
            ecs_task_role_arn=ecs_task_role_arn,
            event_bridge_role_arn=event_bridge_role_arn,
            lambda_ecs_execute_role_arn=lambda_ecs_execute_role_arn,
            migrate_lambda_name=migrate_lambda_name,
            nlb_dns_name=nlb_dns_name,
            step_functions_role_arn=step_functions_role_arn,
            table_name=table_name,
        )

        jsii.create(MetaflowExports, self, [scope, id, props])


class MetaflowFargateService(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.MetaflowFargateService",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_ecs.ICluster,
        database: aws_cdk.aws_rds.IDatabaseInstance,
        execution_role: aws_cdk.aws_iam.IRole,
        log_group: aws_cdk.aws_logs.ILogGroup,
        secret: aws_cdk.aws_secretsmanager.ISecret,
        security_group: aws_cdk.aws_ec2.SecurityGroup,
        task_role: aws_cdk.aws_iam.IRole,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param database: 
        :param execution_role: 
        :param log_group: 
        :param secret: 
        :param security_group: 
        :param task_role: 

        :stability: experimental
        '''
        props = MetaflowFargateServiceProps(
            cluster=cluster,
            database=database,
            execution_role=execution_role,
            log_group=log_group,
            secret=secret,
            security_group=security_group,
            task_role=task_role,
        )

        jsii.create(MetaflowFargateService, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fargateService")
    def fargate_service(self) -> aws_cdk.aws_ecs.FargateService:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ecs.FargateService, jsii.get(self, "fargateService"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fargateTaskDefinition")
    def fargate_task_definition(self) -> aws_cdk.aws_ecs.FargateTaskDefinition:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ecs.FargateTaskDefinition, jsii.get(self, "fargateTaskDefinition"))


@jsii.data_type(
    jsii_type="cdk-metaflow.MetaflowFargateServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "database": "database",
        "execution_role": "executionRole",
        "log_group": "logGroup",
        "secret": "secret",
        "security_group": "securityGroup",
        "task_role": "taskRole",
    },
)
class MetaflowFargateServiceProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_ecs.ICluster,
        database: aws_cdk.aws_rds.IDatabaseInstance,
        execution_role: aws_cdk.aws_iam.IRole,
        log_group: aws_cdk.aws_logs.ILogGroup,
        secret: aws_cdk.aws_secretsmanager.ISecret,
        security_group: aws_cdk.aws_ec2.SecurityGroup,
        task_role: aws_cdk.aws_iam.IRole,
    ) -> None:
        '''
        :param cluster: 
        :param database: 
        :param execution_role: 
        :param log_group: 
        :param secret: 
        :param security_group: 
        :param task_role: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "database": database,
            "execution_role": execution_role,
            "log_group": log_group,
            "secret": secret,
            "security_group": security_group,
            "task_role": task_role,
        }

    @builtins.property
    def cluster(self) -> aws_cdk.aws_ecs.ICluster:
        '''
        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_ecs.ICluster, result)

    @builtins.property
    def database(self) -> aws_cdk.aws_rds.IDatabaseInstance:
        '''
        :stability: experimental
        '''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(aws_cdk.aws_rds.IDatabaseInstance, result)

    @builtins.property
    def execution_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        result = self._values.get("execution_role")
        assert result is not None, "Required property 'execution_role' is missing"
        return typing.cast(aws_cdk.aws_iam.IRole, result)

    @builtins.property
    def log_group(self) -> aws_cdk.aws_logs.ILogGroup:
        '''
        :stability: experimental
        '''
        result = self._values.get("log_group")
        assert result is not None, "Required property 'log_group' is missing"
        return typing.cast(aws_cdk.aws_logs.ILogGroup, result)

    @builtins.property
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''
        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, result)

    @builtins.property
    def security_group(self) -> aws_cdk.aws_ec2.SecurityGroup:
        '''
        :stability: experimental
        '''
        result = self._values.get("security_group")
        assert result is not None, "Required property 'security_group' is missing"
        return typing.cast(aws_cdk.aws_ec2.SecurityGroup, result)

    @builtins.property
    def task_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        result = self._values.get("task_role")
        assert result is not None, "Required property 'task_role' is missing"
        return typing.cast(aws_cdk.aws_iam.IRole, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowFargateServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetaflowNlb(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.MetaflowNlb",
):
    '''
    :stability: experimental
    :summary: Metaflow Nlb
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: 

        :stability: experimental
        '''
        props = MetaflowNlbProps(vpc=vpc)

        jsii.create(MetaflowNlb, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbMigrateTargetGroup")
    def db_migrate_target_group(
        self,
    ) -> aws_cdk.aws_elasticloadbalancingv2.NetworkTargetGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.NetworkTargetGroup, jsii.get(self, "dbMigrateTargetGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nlb")
    def nlb(self) -> aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer:
        '''(experimental) Constructs a new instance of the MetaflowNlb class.

        :stability: experimental
        :access: public
        '''
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer, jsii.get(self, "nlb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nlbTargetGroup")
    def nlb_target_group(self) -> aws_cdk.aws_elasticloadbalancingv2.NetworkTargetGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.NetworkTargetGroup, jsii.get(self, "nlbTargetGroup"))


@jsii.data_type(
    jsii_type="cdk-metaflow.MetaflowNlbProps",
    jsii_struct_bases=[],
    name_mapping={"vpc": "vpc"},
)
class MetaflowNlbProps:
    def __init__(self, *, vpc: aws_cdk.aws_ec2.IVpc) -> None:
        '''
        :param vpc: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowNlbProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetaflowTable(
    aws_cdk.aws_dynamodb.Table,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.MetaflowTable",
):
    '''
    :stability: experimental
    :summary:

    Metaflow DynamoDB Table
    This may be going away entirely because I'm not sure that
    ddb is necessary to manage state with dynamo with the recent support
    for strong read-after-write consistency.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        kinesis_stream: typing.Optional[aws_cdk.aws_kinesis.IStream] = None,
        table_name: typing.Optional[builtins.str] = None,
        billing_mode: typing.Optional[aws_cdk.aws_dynamodb.BillingMode] = None,
        contributor_insights_enabled: typing.Optional[builtins.bool] = None,
        encryption: typing.Optional[aws_cdk.aws_dynamodb.TableEncryption] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        point_in_time_recovery: typing.Optional[builtins.bool] = None,
        read_capacity: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        replication_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        replication_timeout: typing.Optional[aws_cdk.core.Duration] = None,
        server_side_encryption: typing.Optional[builtins.bool] = None,
        stream: typing.Optional[aws_cdk.aws_dynamodb.StreamViewType] = None,
        time_to_live_attribute: typing.Optional[builtins.str] = None,
        write_capacity: typing.Optional[jsii.Number] = None,
        partition_key: aws_cdk.aws_dynamodb.Attribute,
        sort_key: typing.Optional[aws_cdk.aws_dynamodb.Attribute] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param kinesis_stream: Kinesis Data Stream to capture item-level changes for the table. Default: - no Kinesis Data Stream
        :param table_name: Enforces a particular physical table name. Default: 
        :param billing_mode: Specify how you are charged for read and write throughput and how you manage capacity. Default: PROVISIONED if ``replicationRegions`` is not specified, PAY_PER_REQUEST otherwise
        :param contributor_insights_enabled: Whether CloudWatch contributor insights is enabled. Default: false
        :param encryption: Whether server-side encryption with an AWS managed customer master key is enabled. This property cannot be set if ``serverSideEncryption`` is set. Default: - server-side encryption is enabled with an AWS owned customer master key
        :param encryption_key: External KMS key to use for table encryption. This property can only be set if ``encryption`` is set to ``TableEncryption.CUSTOMER_MANAGED``. Default: - If ``encryption`` is set to ``TableEncryption.CUSTOMER_MANAGED`` and this property is undefined, a new KMS key will be created and associated with this table.
        :param point_in_time_recovery: Whether point-in-time recovery is enabled. Default: - point-in-time recovery is disabled
        :param read_capacity: The read capacity for the table. Careful if you add Global Secondary Indexes, as those will share the table's provisioned throughput. Can only be provided if billingMode is Provisioned. Default: 5
        :param removal_policy: The removal policy to apply to the DynamoDB Table. Default: RemovalPolicy.RETAIN
        :param replication_regions: Regions where replica tables will be created. Default: - no replica tables are created
        :param replication_timeout: The timeout for a table replication operation in a single region. Default: Duration.minutes(30)
        :param server_side_encryption: (deprecated) Whether server-side encryption with an AWS managed customer master key is enabled. This property cannot be set if ``encryption`` and/or ``encryptionKey`` is set. Default: - server-side encryption is enabled with an AWS owned customer master key
        :param stream: When an item in the table is modified, StreamViewType determines what information is written to the stream for this table. Default: - streams are disabled unless ``replicationRegions`` is specified
        :param time_to_live_attribute: The name of TTL attribute. Default: - TTL is disabled
        :param write_capacity: The write capacity for the table. Careful if you add Global Secondary Indexes, as those will share the table's provisioned throughput. Can only be provided if billingMode is Provisioned. Default: 5
        :param partition_key: Partition key attribute definition.
        :param sort_key: Sort key attribute definition. Default: no sort key

        :stability: experimental
        '''
        props = aws_cdk.aws_dynamodb.TableProps(
            kinesis_stream=kinesis_stream,
            table_name=table_name,
            billing_mode=billing_mode,
            contributor_insights_enabled=contributor_insights_enabled,
            encryption=encryption,
            encryption_key=encryption_key,
            point_in_time_recovery=point_in_time_recovery,
            read_capacity=read_capacity,
            removal_policy=removal_policy,
            replication_regions=replication_regions,
            replication_timeout=replication_timeout,
            server_side_encryption=server_side_encryption,
            stream=stream,
            time_to_live_attribute=time_to_live_attribute,
            write_capacity=write_capacity,
            partition_key=partition_key,
            sort_key=sort_key,
        )

        jsii.create(MetaflowTable, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> aws_cdk.aws_dynamodb.CfnTable:
        '''(experimental) Constructs a new instance of the MetaflowTable class.

        :stability: experimental
        :access: public
        '''
        return typing.cast(aws_cdk.aws_dynamodb.CfnTable, jsii.get(self, "resource"))


class MetaflowVpc(
    aws_cdk.aws_ec2.Vpc,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.MetaflowVpc",
):
    '''
    :stability: experimental
    :summary: Metaflow VPC
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cidr: typing.Optional[builtins.str] = None,
        default_instance_tenancy: typing.Optional[aws_cdk.aws_ec2.DefaultInstanceTenancy] = None,
        enable_dns_hostnames: typing.Optional[builtins.bool] = None,
        enable_dns_support: typing.Optional[builtins.bool] = None,
        flow_logs: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ec2.FlowLogOptions]] = None,
        gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ec2.GatewayVpcEndpointOptions]] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateway_provider: typing.Optional[aws_cdk.aws_ec2.NatProvider] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        nat_gateway_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        subnet_configuration: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.SubnetConfiguration]] = None,
        vpn_connections: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ec2.VpnConnectionOptions]] = None,
        vpn_gateway: typing.Optional[builtins.bool] = None,
        vpn_gateway_asn: typing.Optional[jsii.Number] = None,
        vpn_route_propagation: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.SubnetSelection]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cidr: The CIDR range to use for the VPC, e.g. '10.0.0.0/16'. Should be a minimum of /28 and maximum size of /16. The range will be split across all subnets per Availability Zone. Default: Vpc.DEFAULT_CIDR_RANGE
        :param default_instance_tenancy: The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy. Default: DefaultInstanceTenancy.Default (shared) tenancy
        :param enable_dns_hostnames: Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true. Default: true
        :param enable_dns_support: Indicates whether the DNS resolution is supported for the VPC. If this attribute is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames to IP addresses is not enabled. If this attribute is true, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC IPv4 network range plus two will succeed. Default: true
        :param flow_logs: Flow logs to add to this VPC. Default: - No flow logs.
        :param gateway_endpoints: Gateway endpoints to add to this VPC. Default: - None.
        :param max_azs: Define the maximum number of AZs to use in this region. If the region has more AZs than you want to use (for example, because of EIP limits), pick a lower number here. The AZs will be sorted and picked from the start of the list. If you pick a higher number than the number of AZs in the region, all AZs in the region will be selected. To use "all AZs" available to your account, use a high number (such as 99). Be aware that environment-agnostic stacks will be created with access to only 2 AZs, so to use more than 2 AZs, be sure to specify the account and region on your stack. Default: 3
        :param nat_gateway_provider: What type of NAT provider to use. Select between NAT gateways or NAT instances. NAT gateways may not be available in all AWS regions. Default: NatProvider.gateway()
        :param nat_gateways: The number of NAT Gateways/Instances to create. The type of NAT gateway or instance will be determined by the ``natGatewayProvider`` parameter. You can set this number lower than the number of Availability Zones in your VPC in order to save on NAT cost. Be aware you may be charged for cross-AZ data traffic instead. Default: - One NAT gateway/instance per Availability Zone
        :param nat_gateway_subnets: Configures the subnets which will have NAT Gateways/Instances. You can pick a specific group of subnets by specifying the group name; the picked subnets must be public subnets. Only necessary if you have more than one public subnet group. Default: - All public subnets.
        :param subnet_configuration: Configure the subnets to build for each AZ. Each entry in this list configures a Subnet Group; each group will contain a subnet for each Availability Zone. For example, if you want 1 public subnet, 1 private subnet, and 1 isolated subnet in each AZ provide the following:: new ec2.Vpc(this, 'VPC', { subnetConfiguration: [ { cidrMask: 24, name: 'ingress', subnetType: ec2.SubnetType.PUBLIC, }, { cidrMask: 24, name: 'application', subnetType: ec2.SubnetType.PRIVATE, }, { cidrMask: 28, name: 'rds', subnetType: ec2.SubnetType.ISOLATED, } ] }); Default: - The VPC CIDR will be evenly divided between 1 public and 1 private subnet per AZ.
        :param vpn_connections: VPN connections to this VPC. Default: - No connections.
        :param vpn_gateway: Indicates whether a VPN gateway should be created and attached to this VPC. Default: - true when vpnGatewayAsn or vpnConnections is specified
        :param vpn_gateway_asn: The private Autonomous System Number (ASN) for the VPN gateway. Default: - Amazon default ASN.
        :param vpn_route_propagation: Where to propagate VPN routes. Default: - On the route tables associated with private subnets. If no private subnets exists, isolated subnets are used. If no isolated subnets exists, public subnets are used.

        :stability: experimental
        '''
        props = aws_cdk.aws_ec2.VpcProps(
            cidr=cidr,
            default_instance_tenancy=default_instance_tenancy,
            enable_dns_hostnames=enable_dns_hostnames,
            enable_dns_support=enable_dns_support,
            flow_logs=flow_logs,
            gateway_endpoints=gateway_endpoints,
            max_azs=max_azs,
            nat_gateway_provider=nat_gateway_provider,
            nat_gateways=nat_gateways,
            nat_gateway_subnets=nat_gateway_subnets,
            subnet_configuration=subnet_configuration,
            vpn_connections=vpn_connections,
            vpn_gateway=vpn_gateway,
            vpn_gateway_asn=vpn_gateway_asn,
            vpn_route_propagation=vpn_route_propagation,
        )

        jsii.create(MetaflowVpc, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) Constructs a new instance of the MetaflowVpc class.

        :stability: experimental
        :access: public
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


class StepFunctionsRole(
    aws_cdk.aws_iam.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-metaflow.StepFunctionsRole",
):
    '''
    :stability: experimental
    :summary: StepFunctions  Role
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the StepFunctionsRole class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(StepFunctionsRole, self, [scope, id])


__all__ = [
    "BatchExecutionRole",
    "BatchS3TaskRole",
    "DashboardProps",
    "EcsExecutionRole",
    "EcsRole",
    "EcsTaskRole",
    "EventBridgeRole",
    "IMetaflowDatabase",
    "LambdaECSExecuteRole",
    "Metaflow",
    "MetaflowApi",
    "MetaflowApiProps",
    "MetaflowBucket",
    "MetaflowDashboard",
    "MetaflowDatabaseInstance",
    "MetaflowDatabaseInstanceProps",
    "MetaflowExportProps",
    "MetaflowExports",
    "MetaflowFargateService",
    "MetaflowFargateServiceProps",
    "MetaflowNlb",
    "MetaflowNlbProps",
    "MetaflowTable",
    "MetaflowVpc",
    "StepFunctionsRole",
]

publication.publish()
