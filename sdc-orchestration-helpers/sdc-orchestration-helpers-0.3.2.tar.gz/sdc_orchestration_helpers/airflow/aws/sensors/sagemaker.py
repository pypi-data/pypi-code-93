"""
    Sagemaker Sensors

    Used to monitor tasks executed on sagemaker.
    In practice any tasks that have a execution time which could be length or uncertain.
"""
import logging
import boto3
from sagemaker.session import Session
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(None)

class MonitorTrainingJob(BaseSensorOperator):
    template_fields = ('training_job_name', 'poke_interval', 'timeout', 'soft_fail', 'mode', 'xcom_tasks')

    @apply_defaults
    def __init__(self, training_job_name=None, poke_interval=60, timeout=60 * 60 * 24 * 7, soft_fail=False, mode='poke', xcom_tasks=None, *args, **kwargs):
        super(MonitorTrainingJob, self).__init__(
            poke_interval=poke_interval,
            timeout=timeout,
            soft_fail=soft_fail,
            mode=mode,
            *args,
            **kwargs
        )
        self.training_job_name = training_job_name
        self.xcom_tasks = xcom_tasks
    
    def poke(self, context):
        """Monitors Sagemaker Transform job"""
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        SAGEMAKER_CLIENT = BOTO_SESSION.client('sagemaker')
        try:
            if self.training_job_name is None:
                # assume model_name is passed
                self.training_job_name = context['task_instance'].xcom_pull(
                    task_ids=self.xcom_tasks['training_job_name']['task_id'],
                    key=self.xcom_tasks['training_job_name']['key']
                )
                logger.info("successfully retrieved training_job_name = {}".format(self.training_job_name))
                assert self.training_job_name is not None, (
                    "No {xcom_key} found in upstream={task_ids} task. "
                    "Either hardcode in config or pass from previous job".format(
                        xcom_key=self.xcom_tasks['training_job_name']['key'],
                        task_ids=self.xcom_tasks['training_job_name']['task_id']
                    )
                )
            response = SAGEMAKER_CLIENT.describe_training_job(
                TrainingJobName=self.training_job_name
            )
            # push response up
            context['task_instance'].xcom_push(
                key='training_job_name',
                value=self.training_job_name
            )

            job_state = response['TrainingJobStatus']
            reason = response.get('FailureReason', None)
            logger.info("Job status = {}".format(job_state))
            if job_state == 'Completed':
                # failure
                return True
            elif job_state in ['InProgress']:
                # retry state
                return False
            else:
                # failure, up for retry
                raise Exception(
                    "training job status == {JOB_STATE} with reason = {REASON}".format(
                        JOB_STATE=job_state, REASON=reason
                    )
                )
        except Exception as err:
            raise

class MonitorTransformJob(BaseSensorOperator):
    template_fields = ('transform_job_name', 'poke_interval', 'timeout', 'soft_fail', 'mode', 'xcom_tasks')

    @apply_defaults
    def __init__(self, transform_job_name=None, poke_interval=60, timeout=60 * 60 * 24 * 7, soft_fail=False, mode='poke', xcom_tasks=None, *args, **kwargs):
        super(MonitorTransformJob, self).__init__(
            poke_interval=poke_interval,
            timeout=timeout,
            soft_fail=soft_fail,
            mode=mode,
            *args,
            **kwargs
        )
        self.transform_job_name = transform_job_name
        self.xcom_tasks = xcom_tasks

    def poke(self, context):
        """Monitors Sagemaker Transform job"""
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        SAGEMAKER_CLIENT = BOTO_SESSION.client('sagemaker')
        try:
            if self.transform_job_name is None:
                # assume model_name is passed
                self.transform_job_name = context['task_instance'].xcom_pull(
                    task_ids=self.xcom_tasks['transform_job_name']['task_id'],
                    key=self.xcom_tasks['transform_job_name']['key']
                )
                logger.info("successfully retrieved transform_job_name = {}".format(self.transform_job_name))
                assert self.transform_job_name is not None, (
                    "No {xcom_key} found in upstream={task_ids} task. "
                    "Either hardcode in config or pass from previous job".format(
                        xcom_key=self.xcom_tasks['transform_job_name']['key'],
                        task_ids=self.xcom_tasks['transform_job_name']['task_id']
                    )
                )
            response = SAGEMAKER_CLIENT.describe_transform_job(
                TransformJobName=self.transform_job_name
            )
            # push response up
            context['task_instance'].xcom_push(
                key='transform_job_name',
                value=self.transform_job_name
            )

            job_state = response['TransformJobStatus']
            reason = response.get('FailureReason', None)
            logger.info("Job status = {}".format(job_state))
            if job_state == 'Completed':
                return True
            elif job_state in ['InProgress']:
                return False
            else:
                # retry on failure
                raise Exception(
                    "transform job status == {JOB_STATE} with reason = {REASON}".format(
                        JOB_STATE=job_state, REASON=reason
                    )
                )
        except Exception as err:
            raise
