import logging

import boto3
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(None)


class MonitorGlueJob(BaseSensorOperator):
    """
    Retrieves the metadata for a given job run and checks the run status.
    """
    template_fields = ('poke_interval', 'timeout', 'soft_fail', 'mode', 'xcom_tasks')

    @apply_defaults
    def __init__(self, poke_interval=60, timeout=60 * 60 * 24 * 7, soft_fail=False, mode='poke',
                 xcom_tasks=None, *args, **kwargs):
        super(MonitorGlueJob, self).__init__(
            poke_interval=poke_interval,
            timeout=timeout,
            soft_fail=soft_fail,
            mode=mode,
            *args,
            **kwargs
        )
        self.xcom_tasks = xcom_tasks

    def poke(self, context):
        """Monitors Glue Job Run Status"""

        CLIENT = boto3.client('glue')

        task_ids = self.xcom_tasks['job_name']['task_id']

        job_name = context['task_instance'].xcom_pull(
            task_ids=task_ids,
            key=self.xcom_tasks['job_name']['key']
        )

        job_run_id = context['task_instance'].xcom_pull(
            task_ids=task_ids,
            key=self.xcom_tasks['job_run_id']['key']
        )

        try:
            response = CLIENT.get_job_run(
                JobName=job_name,
                RunId=job_run_id,
            )

            state = response['JobRun']['JobRunState']
            if state == 'SUCCEEDED':
                # success
                return True
            elif state in ['STARTING', 'RUNNING', 'STOPPING']:
                # retry state
                return False
            else:
                # failure, up for retry
                raise Exception(
                    "training job status == {JOB_STATE} with reason = {REASON}".format(
                        JOB_STATE=state, REASON=response['JobRun']['ErrorMessage']
                    )
                )

        except Exception as err:
            raise


class MonitorGlueCrawler(BaseSensorOperator):
    """
    Retrieves the metadata for a given crawler run and checks the run status.
    """
    template_fields = ('poke_interval', 'timeout', 'soft_fail', 'mode', 'xcom_tasks')

    @apply_defaults
    def __init__(self, poke_interval=60, timeout=60 * 60 * 24 * 7, soft_fail=False, mode='poke',
                 xcom_tasks=None, *args, **kwargs):
        super(MonitorGlueCrawler, self).__init__(
            poke_interval=poke_interval,
            timeout=timeout,
            soft_fail=soft_fail,
            mode=mode,
            *args,
            **kwargs
        )
        self.xcom_tasks = xcom_tasks

    def poke(self, context):
        """Monitors Glue Crawler Run Status"""

        CLIENT = boto3.client('glue')

        task_ids = self.xcom_tasks['crawler_name']['task_id']

        crawler_name = context['task_instance'].xcom_pull(
            task_ids=task_ids,
            key=self.xcom_tasks['crawler_name']['key']
        )

        try:
            response = CLIENT.get_crawler(
                Name=crawler_name
            )

            state = response['Crawler']['State']
            if state == 'READY':
                # success
                return True
            elif state in ['RUNNING', 'STOPPING']:
                # retry state
                return False
            else:
                # failure, up for retry
                raise Exception(
                    "training job status == {JOB_STATE} with reason = {REASON}".format(
                        JOB_STATE=state, REASON=state
                    )
                )

        except Exception as err:
            raise
