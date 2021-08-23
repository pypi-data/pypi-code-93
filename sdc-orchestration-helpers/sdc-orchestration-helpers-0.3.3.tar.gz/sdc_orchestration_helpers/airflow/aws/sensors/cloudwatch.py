# pylint: disable=super-with-arguments
# pylint: disable=redefined-builtin
# pylint: disable=invalid-name

import logging

import boto3
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(None)


class MonitorQuery(BaseSensorOperator):
    """
    Monitors the results from the specified query.
    Only the fields requested in the query are returned,
    along with a @ptr field, which is the identifier for the log record.
    """
    template_fields = ('poke_interval', 'timeout', 'soft_fail', 'mode', 'xcom_tasks')

    @apply_defaults
    def __init__(self, poke_interval=60, timeout=60 * 60 * 24 * 7, soft_fail=False, mode='poke',
                 xcom_tasks=None, *args, **kwargs):
        super(MonitorQuery, self).__init__(
            poke_interval=poke_interval,
            timeout=timeout,
            soft_fail=soft_fail,
            mode=mode,
            *args,
            **kwargs
        )
        self.xcom_tasks = xcom_tasks

    def poke(self, context):
        """Monitors CloudWatch Query Process"""

        BOTO_SESSION = boto3.Session()
        CLIENT = BOTO_SESSION.client('logs')

        task_ids = self.xcom_tasks['query_id']['task_id']
        query_id = context['task_instance'].xcom_pull(
            task_ids=task_ids,
            key=self.xcom_tasks['query_id']['key']
        )

        try:
            query_state = CLIENT.get_query_results(
                queryId=query_id
            )['status']

            if query_state == 'Complete':
                # success
                return True
            elif query_state in ['Running', 'Scheduled']:
                # retry state
                return False
            else:
                # failure, up for retry
                raise Exception(
                    "training job status == {JOB_STATE} with reason = {REASON}".format(
                        JOB_STATE=query_state, REASON=query_state
                    )
                )

        except Exception as err:
            raise
