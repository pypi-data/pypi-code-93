import logging
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

import os
import time
import boto3
from sagemaker.session import Session
from sagemaker.estimator import Estimator, Transformer
from sagemaker import get_execution_role

logger = logging.getLogger(None)


class CreateTrainingJob(BaseOperator):
    template_fields = ('config', 'xcom_tasks')

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(CreateTrainingJob, self).__init__(*args, **kwargs)
        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """
            May need to change input to be AthenaFeatureQuery

            https://sagemaker.readthedocs.io/en/stable/api/prep_data/\
                feature_store.html#sagemaker.feature_store.inputs.DataCatalogConfig
        """
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        SM_CLIENT = BOTO_SESSION.client('sagemaker')
        SM_SESSION = Session(default_bucket=self.config['bucket'], boto_session=BOTO_SESSION)
        # get execution role
        if self.config.get('role', None) in ['None', None, '']:
            print("Running on sagemaker friendly context")
            ROLE = get_execution_role(sagemaker_session=SM_SESSION)
        else:
            print("Running else where")
            IAM_CLIENT = BOTO_SESSION.client('iam')
            ROLE = IAM_CLIENT.get_role(RoleName=self.config['sagemaker_role_name'])['Role']['Arn']

        input_data = self.config.get('inputs', None)

        try:
            print("creating estimator")
            estimator = Estimator(
                image_uri=self.config['image_uri'],
                role=ROLE,
                train_instance_type=self.config.get('train_instance_type', 'ml.t3.medium'),
                train_instance_count=self.config.get('train_instance_count', 1),
                train_max_run=self.config.get('train_max_run', None),
                output_path=self.config['output_path'],
                base_job_name=self.config['base_job_name'],
                sagemaker_session=SM_SESSION,
                hyperparameters=self.config.get('hyperparameters', None),
                tags=self.config.get('tags', None),
                enable_sagemaker_metrics=self.config.get('enable_sagemaker_metrics',False),
                metric_definitions=self.config.get('metric_definitions',{})
            )

            print("fitting data")
            # add test data to s3 s3://bucket/bernard/data
            estimator.fit(
                inputs = input_data,
                wait=self.config.get('wait', False)
            )

            context['task_instance'].xcom_push(
                key='training_job_name',
                value=estimator.latest_training_job.name
            )
            context['task_instance'].xcom_push(
                key='model_name',
                value=estimator.latest_training_job.name
            )
        except Exception as exception:
            raise exception

class CreateModel(BaseOperator):
    template_fields = ('config', 'xcom_tasks', )

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(CreateModel, self).__init__(*args, **kwargs)
        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """
            Create model through usual boto3 handling

            model_name = training_job_name + '-mod'

            info = sm.describe_training_job(TrainingJobName=training_job_name)
            model_data = info['ModelArtifacts']['S3ModelArtifacts']
            print(model_data)

            primary_container = {
                'Image': container,
                'ModelDataUrl': model_data
            }

            create_model_response = sm.create_model(
                ModelName = model_name,
                ExecutionRoleArn = role,
                PrimaryContainer = primary_container)

            print(create_model_response['ModelArn'])
        """
        import os
        import boto3
        from botocore.exceptions import ClientError as botocore_clienterror
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        SM_CLIENT = BOTO_SESSION.client('sagemaker')

        # context = context_dict + op_kwargs_dict
        training_job_name = self.config.get('training_job_name', None) # pass from training job
        container_image = self.config.get('container_image', None)

        try:
            if training_job_name is None:
                training_job_name = context['task_instance'].xcom_pull(
                    task_ids=self.xcom_tasks['training_job_name']['task_id'],
                    key=self.xcom_tasks['training_job_name']['key']
                )
                print("training_job_name = {}".format(training_job_name))
                assert training_job_name is not None, "No training job name found. Either hardcode in config or pass from previous job"

            # get model_name
            model_name = self.config.get('model_name', training_job_name)

            # retrieve training job config
            training_job_config = SM_CLIENT.describe_training_job(
                TrainingJobName=training_job_name
            )

            if container_image is None:
                container_image=training_job_config['AlgorithmSpecification']['TrainingImage']

            primary_container = {
                'Image': container_image,
                'Mode': self.config.get('primary_container', {}).get('mode','SingleModel'),
                'ModelDataUrl': training_job_config['ModelArtifacts']['S3ModelArtifacts'],
                'Environment': self.config.get('primary_container', {}).get('environment', {})
            }

            model_tags = self.config.get('tags', [])
            model_tags.append({
                'Key': 'status',
                'Value': 'active'
            })
            try:
                _ = SM_CLIENT.create_model(
                    ModelName=model_name,
                    ExecutionRoleArn=training_job_config['RoleArn'],
                    PrimaryContainer=primary_container,
                    Tags=model_tags
                )

            except botocore_clienterror as exception:
                if exception.response['Error']['Code'] == 'ValidationException':
                    # handle no
                    if 'Cannot create already existing model' in exception.response['Error']['Message']:
                        print((
                            "This Model already exists, "
                            "with name = {}. Using the already created model."
                            .format(model_name)
                        ))
                    else:
                        raise botocore_clienterror(
                            error_response=exception.operation_name,
                            operation_name=exception.response
                        )

            context['task_instance'].xcom_push(
                key='model_name',
                value=model_name
            )
        except Exception as err:
            raise

class CreateTransformJob(BaseOperator):
    template_fields = ('config', 'xcom_tasks', )

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(CreateTransformJob, self).__init__(*args, **kwargs)
        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """
            Creates a transform job

            https://sagemaker.readthedocs.io/en/stable/api/inference/transformer.html#sagemaker.transformer.Transformer
        """
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        SM_CLIENT = BOTO_SESSION.client('sagemaker')
        SM_SESSION = Session(default_bucket=self.config['bucket'], boto_session=BOTO_SESSION)
        # get execution role
        if self.config.get('role', None) in ['None', None, '']:
            print("Running on sagemaker friendly context")
            ROLE = get_execution_role(sagemaker_session=SM_SESSION)
        else:
            print("Running else where")
            IAM_CLIENT = BOTO_SESSION.client('iam')
            ROLE = IAM_CLIENT.get_role(RoleName=self.config['sagemaker_role_name'])['Role']['Arn']

        model_name = self.config.get('model_name', None)
        data = self.config.get('data', None)

        try:
            if model_name is None:
                # assume model_name is passed
                model_name = context['task_instance'].xcom_pull(
                    task_ids=self.xcom_tasks['model_name']['task_id'],
                    key=self.xcom_tasks['model_name']['key']
                )
                print("model_name = {}".format(model_name))
                logger.info("successfully retrieved model_name = {}".format(model_name))
                assert model_name is not None, "No model name found. Either hardcode in config or pass from previous job"
            
            if data is None:
                # assume model_name is passed
                data = context['task_instance'].xcom_pull(task_ids=self.xcom_tasks['data']['task_id'], key=self.xcom_tasks['data']['key'])
                print("data = {}".format(data))
                logger.info("successfully retrieved data path = {}".format(data))
                assert data is not None, "No s3 data path found. Either hardcode in config or pass from previous job"       

            transformer = Transformer(
                model_name=model_name,
                instance_count=self.config['instance_count'],
                instance_type=self.config['instance_type'],
                strategy=self.config.get('strategy', None),
                assemble_with=self.config.get('split_type', None),
                output_path=self.config['output_path'],
                output_kms_key=self.config.get('output_kms_key', None),
                accept=self.config.get('content_type', None),
                max_concurrent_transforms=self.config.get('max_concurrent_transforms', None),
                max_payload=self.config.get('max_payload', None),
                tags=self.config.get('tags', None),
                env=self.config.get('env', None),
                base_transform_job_name=self.config['base_transform_job_name'],
                sagemaker_session=SM_SESSION
            )
            transformer.transform(
                data=data,
                data_type=self.config.get('data_type','S3Prefix'),
                split_type=self.config.get('split_type','Line'),
                compression_type=self.config.get('compression_type', None),
                content_type=self.config.get('content_type','text/csv'),
                input_filter=self.config.get('input_filter',None),
                join_source=self.config.get('join_source',None),
                output_filter=self.config.get('output_filter', None),
                wait=self.config.get('wait', True)
            )

            context['task_instance'].xcom_push(
                key='transform_job_name',
                value=transformer.latest_transform_job.name
            )
        except Exception as err:
            raise

class CreateEndpointConfig(BaseOperator):
    template_fields = ('config', 'xcom_tasks', )

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(CreateEndpointConfig, self).__init__(*args, **kwargs)
        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """get model configuration"""
        import os
        import boto3
        from botocore.exceptions import ClientError as botocore_clienterror
        from utils.sagemaker import \
            build_resource_tags, name_from_base
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        SM_CLIENT = BOTO_SESSION.client('sagemaker')
        up_stream = op_args[0]
        model_name = context.get('model_name', None)
        try:
            if model_name is None:
                # assume model_name is passed
                model_name = context['task_instance'].xcom_pull(task_ids=self.xcom_task_id, key=self.xcom_task_id_key)
                print("model_name = {}".format(model_name))
                assert model_name is not None, "No model name found. Either hardcode in config or pass from previous job"
                response = client.create_endpoint_config(
                    EndpointConfigName=context.get('endpoint_configuration', {})['endpoint_config_name'],
                    ProductionVariants=context.get('endpoint_configuration', {})['production_variants'],
                    DataCaptureConfig=context.get('endpoint_configuration', {})['data_capture_config'],
                    Tags=context.get('endpoint_configuration', {})['tags']
                )
            return model_name
        except Exception as err:
            raise
