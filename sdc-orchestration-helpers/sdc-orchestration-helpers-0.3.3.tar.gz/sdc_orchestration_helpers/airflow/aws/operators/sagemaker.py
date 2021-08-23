"""Custom Sagemaker Operators"""
import logging
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

import boto3
from sagemaker.session import Session
from sagemaker.estimator import Estimator, Transformer

logger = logging.getLogger(None)


class CreateTrainingJob(BaseOperator):
    """Execute Create Sagemaker training job using boto3 api"""
    template_fields = ('config', 'xcom_tasks')

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(CreateTrainingJob, self).__init__(*args, **kwargs)
        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """
            Execute a sagemaker training job run
        """
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        SM_SESSION = Session(default_bucket=self.config.pop('bucket', None), boto_session=BOTO_SESSION)

        print("Running else where")
        IAM_CLIENT = BOTO_SESSION.client('iam')
        ROLE = IAM_CLIENT.get_role(RoleName=self.config.pop('sagemaker_role_name', {}))['Role']['Arn']

        input_data = self.config.pop('inputs', None)
        wait_for_completion = self.config.pop('wait', False)

        try:
            print("creating estimator")
            estimator = Estimator(
                role=ROLE,
                sagemaker_session=SM_SESSION,
                **self.config
            )

            print("starting training")
            estimator.fit(
                inputs = input_data,
                wait=wait_for_completion
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
            logger.error(exception)
            raise

class CreateModel(BaseOperator):
    """Execute Create Sagemaker model using boto3 api"""
    template_fields = ('config', 'xcom_tasks', )

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(CreateModel, self).__init__(*args, **kwargs)
        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """
            Execute create model
        """
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

            try:
                _ = SM_CLIENT.create_model(
                    ModelName=model_name,
                    ExecutionRoleArn=training_job_config['RoleArn'],
                    PrimaryContainer=primary_container,
                    Tags=self.config.get('tags', [])
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
        except Exception as exception:
            logger.error(exception)

class CreateTransformJob(BaseOperator):
    """Execute Create Sagemaker transform job using boto3 api"""
    template_fields = ('config', 'xcom_tasks', )

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(CreateTransformJob, self).__init__(*args, **kwargs)
        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """
            execute sagemaker transform job
        """
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        SM_SESSION = Session(default_bucket=self.config.pop('bucket', None), boto_session=BOTO_SESSION)

        model_name = self.config.pop('model_name', None)
        data = self.config.pop('data', None)
        data_type = self.config.pop('data_type','S3Prefix')
        split_type = self.config.pop('split_type','Line')
        compression_type = self.config.pop('compression_type', None)
        content_type = self.config.pop('content_type', 'text/csv')
        input_filter = self.config.pop('input_filter',None)
        join_source = self.config.pop('join_source',None)
        output_filter = self.config.pop('output_filter', None)
        wait_for_completion = self.config.pop('wait', True)
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
                assemble_with=split_type,
                accept=content_type,
                sagemaker_session=SM_SESSION,
                **self.config
            )
            transformer.transform(
                data=data,
                data_type=data_type,
                split_type=split_type,
                compression_type=compression_type,
                content_type=content_type,
                input_filter=input_filter,
                join_source=join_source,
                output_filter=output_filter,
                wait=wait_for_completion
            )

            context['task_instance'].xcom_push(
                key='transform_job_name',
                value=transformer.latest_transform_job.name
            )
        except Exception as exception:
            logger.error(exception)
            raise
